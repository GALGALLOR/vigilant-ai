"""
Vigilant-AI — Supermemory Cross-Video Intelligence
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Uses Supermemory Context Engineering API to build persistent intelligence
across ALL processed videos — not just within one recording.

What gets stored after each video:
  - Behavioral summary (what happened, who was involved)
  - Risk classification and key tags
  - Person/party descriptions derived from Gemini captions
  - Alert timeline

What you can query:
  - "Has someone in a police uniform been involved in violence before?"
  - "Any prior shoplifting incidents in this store?"
  - "Show all high-risk incidents from the last week"

API: https://api.supermemory.ai
Auth: Bearer sm_... token

API notes (confirmed from docs):
  - POST /v3/documents  → store a document
    body: { content, containerTag (singular string), metadata (primitives only) }
  - POST /v4/search     → semantic search
    body: { q (NOT 'query'), containerTag, searchMode, limit }
  - POST /v4/profile    → fetch all memories for a container (no query needed)
    body: { containerTag }
"""

from __future__ import annotations
import os, json
from typing import List, Dict, Any, Optional

# Load .env so the key is available when running outside uvicorn (e.g. tests, CLI)
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
except ImportError:
    pass

SUPERMEMORY_API_KEY = os.environ.get("SUPERMEMORY_API_KEY", "")
BASE_URL = "https://api.supermemory.ai"


def _headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {SUPERMEMORY_API_KEY}",
        "Content-Type": "application/json",
    }


def _is_configured() -> bool:
    return bool(SUPERMEMORY_API_KEY and SUPERMEMORY_API_KEY.startswith("sm_"))


# ─── Store video intelligence ─────────────────────────────────────────────────

def store_video_intelligence(
    video_id: str,
    video_name: str,
    synthesis: Dict,
    alerts: List[Dict],
    duration_s: float = 0,
) -> bool:
    """
    Store a video's behavioral intelligence in Supermemory after processing.
    Called once per video from the ingest pipeline.

    containerTag = "video:{video_id}" — scopes each record to its video,
    enabling both cross-video search (no tag filter) and per-video retrieval.
    """
    if not _is_configured():
        print("⚠️  Supermemory: no API key set (SUPERMEMORY_API_KEY). Skipping.")
        return False

    import httpx

    risk_level  = synthesis.get("risk_level", "unknown")
    intent      = synthesis.get("intent", [])
    tags        = synthesis.get("tags", [])
    summary     = synthesis.get("summary", "")
    key_moments = synthesis.get("key_moments", [])

    # Build rich document content for semantic search
    moments_text = "\n".join(
        f"  {m.get('time','?')}: {m.get('description','')}"
        for m in key_moments[:5]
    )

    alert_captions = "\n".join(
        f"  [{e.get('start',0):.0f}s] {e.get('caption','')}"
        for e in sorted(
            alerts,
            key=lambda x: -(x.get("alert", {}).get("score", 0) if isinstance(x.get("alert"), dict) else 0)
        )[:5]
    )

    content = f"""VIGILANT-AI VIDEO INTELLIGENCE RECORD

Video: {video_name}
Video ID: {video_id}
Duration: {duration_s:.0f}s
Risk Level: {risk_level.upper()}
Classifications: {', '.join(intent)}
Tags: {', '.join(tags)}
Total Alerts: {len(alerts)}

BEHAVIORAL SUMMARY:
{summary}

KEY MOMENTS:
{moments_text}

TOP ALERT CAPTIONS:
{alert_captions}
"""

    try:
        resp = httpx.post(
            f"{BASE_URL}/v3/documents",
            headers=_headers(),
            json={
                "content":      content,
                # containerTag must be a single string (not an array)
                "containerTag": f"video:{video_id}",
                # metadata values must be primitives (str / int / float / bool)
                "metadata": {
                    "video_id":    video_id,
                    "video_name":  video_name,
                    "risk_level":  risk_level,
                    "duration_s":  duration_s,
                    "alert_count": len(alerts),
                    # Store intent/tags as comma-separated strings (not lists)
                    "intent":      ", ".join(intent),
                    "tags":        ", ".join(tags),
                },
            },
            timeout=15,
        )
        resp.raise_for_status()
        print(f"✅ Supermemory: stored intelligence for '{video_name}' (risk={risk_level})")
        return True
    except Exception as e:
        print(f"⚠️  Supermemory store failed: {e}")
        return False


# ─── Query cross-video intelligence ──────────────────────────────────────────

def query_intelligence(
    query: str,
    video_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Natural-language search across ALL stored video intelligence.

    Args:
        query:    e.g. "assault by uniformed officers" or "shoplifting near entrance"
        video_id: if set, restrict search to a specific video's context

    Returns:
        {
          "answer":   str,           # synthesized answer from memory
          "memories": [...],         # raw memory chunks matched
          "query":    str,
        }
    """
    if not _is_configured():
        return {
            "query": query,
            "answer": "Supermemory is not configured. Set SUPERMEMORY_API_KEY in your environment.",
            "memories": [],
            "configured": False,
        }

    import httpx

    # /v4/search — semantic search endpoint
    # field is "q" (NOT "query"), searchMode "hybrid" gives best results
    body: Dict[str, Any] = {
        "q":          query,
        "searchMode": "hybrid",
        "limit":      10,
    }
    if video_id:
        body["containerTag"] = f"video:{video_id}"

    try:
        resp = httpx.post(
            f"{BASE_URL}/v4/search",
            headers=_headers(),
            json=body,
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()

        # Extract readable chunks — API returns "results" array
        memories = []
        for chunk in (data.get("results") or data.get("memories") or []):
            memories.append({
                "content":  chunk.get("content", chunk.get("text", "")),
                "score":    chunk.get("score", chunk.get("relevance", 0)),
                "metadata": chunk.get("metadata", {}),
            })

        # Use Gemini to synthesize a readable answer from the retrieved chunks
        answer = _synthesize_answer(query, memories)

        return {
            "query":    query,
            "answer":   answer,
            "memories": memories[:5],
            "configured": True,
        }
    except Exception as e:
        print(f"⚠️  Supermemory query failed: {e}")
        return {
            "query":    query,
            "answer":   f"Memory query failed: {str(e)}",
            "memories": [],
            "configured": True,
        }


def _synthesize_answer(query: str, memories: List[Dict]) -> str:
    """Use Gemini to synthesize a natural-language answer from retrieved memory chunks."""
    if not memories:
        return "No relevant incidents found in the cross-video intelligence database."

    from services.gemini_synthesis import _call_gemini

    context = "\n\n---\n\n".join(
        m.get("content", "")[:600] for m in memories[:4]
    )

    prompt = f"""You are a security intelligence analyst.
A user asked: "{query}"

RETRIEVED INTELLIGENCE FROM PAST VIDEOS:
{context}

Answer the question based solely on the intelligence above.
Be specific: mention video names, risk levels, timestamps if available.
Keep it to 3–5 sentences. Do NOT use markdown."""

    return _call_gemini(prompt, max_tokens=400) or "Unable to synthesize answer from retrieved memories."


# ─── Get memory for a specific video ─────────────────────────────────────────

def get_video_memory(video_id: str) -> Dict[str, Any]:
    """Retrieve what Supermemory knows about a specific video."""
    if not _is_configured():
        return {"video_id": video_id, "memories": [], "configured": False}

    import httpx
    try:
        # /v4/profile fetches accumulated profile for a container (no query needed)
        resp = httpx.post(
            f"{BASE_URL}/v4/profile",
            headers=_headers(),
            json={"containerTag": f"video:{video_id}"},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        memories = data.get("results") or data.get("memories") or []
        return {
            "video_id":   video_id,
            "memories":   memories[:3],
            "configured": True,
        }
    except Exception as e:
        return {"video_id": video_id, "memories": [], "configured": True, "error": str(e)}
