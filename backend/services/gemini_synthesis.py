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

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyABZMPfjVnsPu3aYpnuFqhORorteVao6wo")
MODEL_ID = "gemini-2.5-flash"

# ─── Gemini Client ────────────────────────────────────────────────────────────

_client = None

def _get_client():
    global _client
    if _client is None:
        from google import genai
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def _call_gemini(prompt: str, max_tokens: int = 2048) -> str:
    """Call Gemini and return the text response."""
    try:
        client = _get_client()
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
        )
        return response.text or ""
    except Exception as e:
        print(f"Gemini API error: {e}")
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
        clip_id = e.get("clip_id", "?")
        start = e.get("start", 0)
        end = e.get("end", 0)
        caption = e.get("caption", "")
        label = e.get("event", {}).get("label", "") if isinstance(e.get("event"), dict) else ""
        people = e.get("detections", {}).get("people_count", 0) if isinstance(e.get("detections"), dict) else 0
        alert_stage = e.get("alert", {}).get("stage", "none") if isinstance(e.get("alert"), dict) else "none"
        alert_score = e.get("alert", {}).get("score", 0) if isinstance(e.get("alert"), dict) else 0

        clips_context.append(
            f"[{_fmt_time(start)}–{_fmt_time(end)}] "
            f"label={label} people={people} alert={alert_stage}({alert_score:.2f})\n"
            f"  Caption: {caption}"
        )

    clips_text = "\n\n".join(clips_context)

    prompt = f"""You are an expert video surveillance analyst. Analyze these chronological clips from a video named "{video_name}" and provide a comprehensive assessment.

CLIPS:
{clips_text}

Respond in this exact JSON format (no markdown, no code fences, just raw JSON):
{{
  "summary": "A detailed 2-3 paragraph narrative of what happened in this video, written like a security report. Be specific about actions, movements, and interactions between people. If the behavior suggests criminal activity (theft, assault, trespassing, etc.), clearly state that.",
  "intent": ["primary_activity", "secondary_activity"],
  "key_moments": [
    {{"time": "M:SS", "description": "What happened at this moment"}}
  ],
  "risk_level": "low|medium|high",
  "tags": ["searchable", "tags", "for", "this", "video"]
}}

CLASSIFICATION GUIDE for "intent":
- shoplifting: concealing merchandise, leaving without paying, distraction techniques
- theft: taking property that belongs to others
- assault/fighting: physical altercation, hitting, punching
- trespassing: unauthorized entry to restricted areas
- loitering: prolonged aimless presence
- vandalism: property damage
- normal_activity: regular behavior, shopping, browsing
- suspicious_behavior: unusual patterns that warrant attention

Be accurate and specific. Do not hallucinate events that weren't described in the clips."""

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

    def _run_stream():
        try:
            client = _get_client()
            for chunk in client.models.generate_content_stream(
                model=MODEL_ID,
                contents=prompt,
            ):
                text = chunk.text or ""
                if text:
                    loop.call_soon_threadsafe(queue.put_nowait, text)
        except Exception as e:
            print(f"Gemini stream error: {e}")
        finally:
            loop.call_soon_threadsafe(queue.put_nowait, None)  # sentinel

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
