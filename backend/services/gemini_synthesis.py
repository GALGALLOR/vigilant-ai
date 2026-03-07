"""
Vigilant-AI — Gemini Synthesis Service
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The "brain" layer. Takes clip-level events from Modal and produces:
  1. Holistic video summary (what actually happened)
  2. Intent classification (shoplifting, assault, etc.)
  3. Key moments with timestamps
  4. RAG-powered conversational answers to user queries

Uses Gemini 2.5 Flash (free tier: 30 RPM, 1M tokens/day).
"""

from __future__ import annotations
import os, json, asyncio, threading
from typing import List, Dict, Any, Optional, AsyncIterator


# ─── JSON Cleaner ─────────────────────────────────────────────────────────────

def _clean_json_string(raw: str) -> str:
    """
    Walk JSON text char-by-char fixing two classes of Gemini output bugs:

    1. Literal control characters (\\n, \\r, \\t) inside JSON string values.
       e.g. Gemini writes a multi-line summary without escaping the newlines.

    2. Unescaped double-quotes embedded inside JSON string values.
       e.g. Gemini writes: "summary": "The video "galo.mp4" presents..."
       The inner "galo.mp4" is not escaped and breaks json.loads().

    Heuristic for (2): when inside a string and we see '"', look at the next
    non-whitespace character. If it's a JSON structural delimiter (:, ,, }, ])
    then it's the closing quote. Otherwise it's an embedded unescaped quote
    that we convert to \\".
    """
    chars = list(raw)
    n = len(chars)
    result: list[str] = []
    in_string = False
    escape_next = False
    i = 0

    while i < n:
        ch = chars[i]

        if escape_next:
            result.append(ch)
            escape_next = False
            i += 1
            continue

        if ch == '\\' and in_string:
            result.append(ch)
            escape_next = True
            i += 1
            continue

        if ch == '"':
            if not in_string:
                in_string = True
                result.append(ch)
            else:
                # Peek at the next non-whitespace character to decide
                # whether this " closes the string or is embedded inside it.
                j = i + 1
                while j < n and chars[j] in ' \t\r\n':
                    j += 1
                next_nws = chars[j] if j < n else ''

                if next_nws in (':', ',', '}', ']', ''):
                    # Closing quote — end the string
                    in_string = False
                    result.append(ch)
                else:
                    # Embedded unescaped quote — escape it
                    result.append('\\"')
            i += 1
            continue

        if in_string:
            if ch == '\n':
                result.append('\\n')
            elif ch == '\r':
                result.append('\\r')
            elif ch == '\t':
                result.append('\\t')
            elif ord(ch) < 0x20:
                result.append(f'\\u{ord(ch):04x}')
            else:
                result.append(ch)
        else:
            result.append(ch)

        i += 1

    return ''.join(result)


_API_ERROR_CAPTIONS = {"api error", "api error.", "[api error]", "api_error"}

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
MODEL_ID = "gemini-2.5-flash"

# ─── Gemini Client ────────────────────────────────────────────────────────────

def _get_client():
    """
    Build a Gemini client.
    Supports:
      - google-genai (preferred): from google import genai
      - google-generativeai (fallback): import google.generativeai as genai
    """
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is missing")

    try:
        from google import genai as sdk  # google-genai
        return ("google-genai", sdk.Client(api_key=GEMINI_API_KEY))
    except Exception:
        try:
            import google.generativeai as legacy  # google-generativeai
            legacy.configure(api_key=GEMINI_API_KEY)
            return ("google-generativeai", legacy.GenerativeModel(MODEL_ID))
        except Exception as e:
            raise ImportError(
                "Gemini SDK not available. Install `google-genai` "
                "(or legacy `google-generativeai`)."
            ) from e


def _call_gemini_once(prompt: str) -> str:
    mode, client = _get_client()
    if mode == "google-genai":
        response = client.models.generate_content(model=MODEL_ID, contents=prompt)
        return response.text or ""

    # Legacy SDK path (google-generativeai)
    response = client.generate_content(prompt)
    return getattr(response, "text", "") or ""


def _call_gemini(prompt: str, max_tokens: int = 2048) -> str:
    """Call Gemini with exponential backoff retry on rate limits and transient errors."""
    import time, random
    MAX_RETRIES = 3
    last_exc = None

    for attempt in range(MAX_RETRIES):
        try:
            return _call_gemini_once(prompt)
        except Exception as e:
            last_exc = e
            err = str(e)
            rate_limited = "429" in err or "RESOURCE_EXHAUSTED" in err or "quota" in err.lower()
            server_err   = any(x in err for x in ("500", "502", "503", "overloaded"))

            if attempt < MAX_RETRIES - 1 and (rate_limited or server_err):
                backoff = (2 ** attempt) * (10 if rate_limited else 3) + random.uniform(1, 3)
                print(f"Gemini synthesis {'rate-limited' if rate_limited else 'server error'} "
                      f"(attempt {attempt+1}/{MAX_RETRIES}) — retry in {backoff:.1f}s")
                time.sleep(backoff)
            else:
                print(f"Gemini synthesis error ({type(e).__name__}): {e}")
                return ""

    print(f"Gemini synthesis: all {MAX_RETRIES} attempts failed. Last: {last_exc}")
    return ""


# ─── Video Synthesis ──────────────────────────────────────────────────────────

def synthesize_video(events: List[Dict], video_name: str) -> Dict[str, Any]:
    """
    Takes ALL clip-level events from a video and produces a holistic understanding.

    Returns:
        {
            "summary": str,       # 2-3 paragraph description of what happened
            "intent": [str],      # activity classifications
            "key_moments": [...], # important timestamps with descriptions
            "risk_level": str,    # low/medium/high
            "tags": [str],        # searchable tags
        }
    """
    # Build a concise context from all events
    clips_context = []
    for e in events:
        start      = e.get("start", 0)
        end        = e.get("end", 0)
        caption    = e.get("caption", "")
        label      = e.get("event", {}).get("label", "") if isinstance(e.get("event"), dict) else ""
        conf       = e.get("event", {}).get("confidence", 0.0) if isinstance(e.get("event"), dict) else 0.0
        people     = e.get("detections", {}).get("people_count", 0) if isinstance(e.get("detections"), dict) else 0
        alert_stage = e.get("alert", {}).get("stage", "none") if isinstance(e.get("alert"), dict) else "none"
        alert_score = e.get("alert", {}).get("score", 0) if isinstance(e.get("alert"), dict) else 0

        # VLM boolean flags (from Gemini Vision / Qwen per-clip analysis)
        vlm = e.get("evidence", {}).get("vlm_flags", {}) if isinstance(e.get("evidence"), dict) else {}
        flag_parts = []
        if vlm.get("fighting"): flag_parts.append("IS_FIGHTING")
        if vlm.get("stealing"): flag_parts.append("IS_STEALING")
        if vlm.get("erratic"):  flag_parts.append("IS_ERRATIC")
        flags_str = " | " + " | ".join(flag_parts) if flag_parts else ""

        # All ranked hypotheses (top 3)
        hyps = e.get("hypotheses", [])[:3]
        hyp_str = ", ".join(f"{h['label']}({h['confidence']:.2f})" for h in hyps) if hyps else "none"

        # Replace failed captions with label-based fallback
        if caption.strip().lower() in _API_ERROR_CAPTIONS:
            caption = f"[visual details unavailable — infer from CV label={label}]"

        # Alert prefix makes severity immediately visible
        prefix = f"🚨 ALERT-{alert_stage}" if alert_stage != "none" else "  no-alert"

        clips_context.append(
            f"[{_fmt_time(start)}–{_fmt_time(end)}] {prefix} | "
            f"CV_LABEL={label.upper()} conf={conf:.2f} | people={people}{flags_str}\n"
            f"  All hypotheses: {hyp_str}\n"
            f"  Caption: {caption}"
        )

    clips_text = "\n\n".join(clips_context)

    prompt = f"""You are an expert video surveillance analyst writing an official security incident report for "{video_name}".

CRITICAL CONTEXT — HOW TO READ THIS DATA:
• CV_LABEL = output of computer vision (YOLO object detection + motion tracking). This is AUTHORITATIVE.
• Captions = natural language descriptions that may be incomplete. Fast actions (punches, grabs) often last
  only 1-2 frames and may not appear clearly in a caption even when the CV system detected them.
• RULE: TRUST CV_LABEL over captions. Captions add detail; they do not override CV detections.
• If CV_LABEL says "physical_altercation" → an altercation occurred. Do not contradict this.
• If CV_LABEL says "theft_detected" → a theft occurred. Do not contradict this.

CLIPS:
{clips_text}

Respond in this exact JSON format (no markdown, no code fences, just raw JSON):
{{
  "summary": "A detailed 2-3 paragraph incident report. Lead with what the CV system detected (the labels), then add context from captions. If labels indicate assault, the report must describe an assault — captions may have missed the fast action.",
  "intent": ["primary_activity", "secondary_activity"],
  "key_moments": [
    {{"time": "M:SS", "description": "What happened at this moment"}}
  ],
  "risk_level": "low|medium|high",
  "tags": ["searchable", "tags", "for", "this", "video"]
}}

CLASSIFICATION RULES for "intent":
Violence rule: If ANY clip has CV_LABEL containing "altercation", "assault", or "fighting" → include "assault/fighting". Violence happens in one clip and is real.
Theft rule: Only include "theft" or "shoplifting" if EITHER (a) ≥2 separate clips have a theft label, OR (b) a single clip has conf≥0.75 AND the caption explicitly mentions concealing, pocketing, or removing an item from a shelf/surface (not from the floor). One ambiguous "picked something up" clip is NOT theft.
Normal activity: Use ONLY if ALL clips have no alerts and no threat labels whatsoever.
Suspicious: Use if alerts exist but evidence is mixed or ambiguous.

RISK LEVEL RULES:
- "high" if any alert stage A, B, or C is present
- "medium" if any alerts are present
- "low" only if literally zero alerts fired across all clips"""

    raw = _call_gemini(prompt)
    if not raw:
        return _default_synthesis(events, video_name)

    try:
        # Clean up response (strip markdown fences if any)
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("```", 1)[0]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()
        # Escape any literal control characters inside JSON string values
        cleaned = _clean_json_string(cleaned)

        result = json.loads(cleaned)
        # Validate required fields
        return {
            "summary": result.get("summary", "Analysis unavailable"),
            "intent": result.get("intent", ["unknown"]),
            "key_moments": result.get("key_moments", []),
            "risk_level": result.get("risk_level", "medium"),
            "tags": result.get("tags", []),
        }
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Gemini JSON parse error: {e}\nRaw: {raw[:500]}")
        return _default_synthesis(events, video_name)


def _default_synthesis(events: List[Dict], video_name: str) -> Dict:
    """Fallback when Gemini fails."""
    labels = set()
    for e in events:
        lbl = e.get("event", {}).get("label", "") if isinstance(e.get("event"), dict) else ""
        if lbl:
            labels.add(lbl)
    return {
        "summary": f"Video '{video_name}' contains {len(events)} detected events.",
        "intent": list(labels) or ["activity_detected"],
        "key_moments": [],
        "risk_level": "medium",
        "tags": list(labels),
    }


# ─── RAG Chat Answer ─────────────────────────────────────────────────────────

def chat_answer(
    query: str,
    relevant_events: List[Dict],
    video_summary: Optional[str] = None,
    video_name: str = "",
) -> str:
    """
    RAG-powered conversational answer.
    Takes user query + retrieved events + video summary → natural language answer.
    """
    if not relevant_events and not video_summary:
        return "I couldn't find any relevant moments in this video for your query."

    # Build context from events
    events_context = []
    for i, e in enumerate(relevant_events[:8], 1):
        start = e.get("start", 0)
        end = e.get("end", 0)
        caption = e.get("caption", "")
        # Handle both nested and flat formats
        label = ""
        if isinstance(e.get("event"), dict):
            label = e["event"].get("label", "")
        elif e.get("event_label"):
            label = e["event_label"]

        events_context.append(f"  Clip {i} [{_fmt_time(start)}–{_fmt_time(end)}]: {label} — {caption}")

    events_text = "\n".join(events_context)

    summary_section = ""
    if video_summary:
        summary_section = f"\nVIDEO SUMMARY:\n{video_summary}\n"

    prompt = f"""You are a helpful video surveillance AI assistant. A user is asking about a video named "{video_name}".
{summary_section}
RELEVANT CLIPS FOUND:
{events_text}

USER QUESTION: "{query}"

Give a clear, concise, conversational answer based on the evidence above. Be specific about:
- What was observed and when (use timestamps)
- Who was involved (number of people)
- What activity or behavior was detected
- Any risk or concern level

If the clips don't directly answer the question, say so honestly but share what you DID find.
Keep your answer to 2-4 sentences unless the user asks for detail. Do NOT use markdown formatting."""

    answer = _call_gemini(prompt)
    if not answer:
        return f"Found {len(relevant_events)} relevant clip(s) but couldn't generate a summary. Check the clips below."
    return answer.strip()


# ─── Streaming Chat Answer ────────────────────────────────────────────────────

def _build_chat_prompt(query: str, relevant_events: List[Dict], video_summary: Optional[str], video_name: str) -> str:
    """Build the RAG chat prompt (shared by blocking and streaming versions)."""
    events_context = []
    for i, e in enumerate(relevant_events[:8], 1):
        start = e.get("start", 0)
        end = e.get("end", 0)
        caption = e.get("caption", "")
        label = ""
        if isinstance(e.get("event"), dict):
            label = e["event"].get("label", "")
        elif e.get("event_label"):
            label = e["event_label"]
        if caption.strip().lower() in _API_ERROR_CAPTIONS:
            caption = f"[visual details unavailable — infer from label={label}]"
        events_context.append(f"  Clip {i} [{_fmt_time(start)}–{_fmt_time(end)}]: {label} — {caption}")

    events_text = "\n".join(events_context)
    summary_section = f"\nVIDEO SUMMARY:\n{video_summary}\n" if video_summary else ""

    return f"""You are a helpful video surveillance AI assistant. A user is asking about a video named "{video_name}".
{summary_section}
RELEVANT CLIPS FOUND:
{events_text}

USER QUESTION: "{query}"

Give a clear, concise, conversational answer based on the evidence above. Be specific about:
- What was observed and when (use timestamps)
- Who was involved (number of people)
- What activity or behavior was detected
- Any risk or concern level

If the clips don't directly answer the question, say so honestly but share what you DID find.
Keep your answer to 2-4 sentences unless the user asks for detail. Do NOT use markdown formatting."""


async def chat_answer_stream(
    query: str,
    relevant_events: List[Dict],
    video_summary: Optional[str] = None,
    video_name: str = "",
) -> AsyncIterator[str]:
    """
    Streaming version of chat_answer. Yields text chunks as they arrive from Gemini.
    Uses a background thread + asyncio.Queue to bridge the sync Gemini SDK to async.
    """
    if not relevant_events and not video_summary:
        yield "I couldn't find any relevant moments in this video for your query."
        return

    prompt = _build_chat_prompt(query, relevant_events, video_summary, video_name)
    queue: asyncio.Queue = asyncio.Queue()
    loop = asyncio.get_event_loop()

    def _stream_text_chunks(prompt_text: str):
        mode, client = _get_client()
        if mode == "google-genai":
            for chunk in client.models.generate_content_stream(model=MODEL_ID, contents=prompt_text):
                text = chunk.text or ""
                if text:
                    yield text
            return

        # Legacy SDK path (google-generativeai)
        for chunk in client.generate_content(prompt_text, stream=True):
            text = getattr(chunk, "text", "") or ""
            if text:
                yield text

    def _run_stream():
        import time, random
        MAX_RETRIES = 3
        for attempt in range(MAX_RETRIES):
            try:
                for text in _stream_text_chunks(prompt):
                    loop.call_soon_threadsafe(queue.put_nowait, text)
                break  # stream completed successfully
            except Exception as e:
                err = str(e)
                rate_limited = "429" in err or "RESOURCE_EXHAUSTED" in err or "quota" in err.lower()
                server_err   = any(x in err for x in ("500", "502", "503", "overloaded"))
                if attempt < MAX_RETRIES - 1 and (rate_limited or server_err):
                    backoff = (2 ** attempt) * (8 if rate_limited else 2) + random.uniform(1, 2)
                    print(f"Gemini stream {'rate-limited' if rate_limited else 'server error'} "
                          f"(attempt {attempt+1}/{MAX_RETRIES}) — retry in {backoff:.1f}s")
                    time.sleep(backoff)
                else:
                    print(f"Gemini stream error ({type(e).__name__}): {e}")
                    break
        loop.call_soon_threadsafe(queue.put_nowait, None)  # sentinel always sent

    thread = threading.Thread(target=_run_stream, daemon=True)
    thread.start()

    while True:
        chunk = await queue.get()
        if chunk is None:
            break
        yield chunk


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _fmt_time(seconds: float) -> str:
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m}:{s:02d}"
