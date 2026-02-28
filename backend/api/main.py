"""
Sentinel-Stream — FastAPI Backend
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REST API for the React frontend. Serves events, alerts, search, timeline.

Run locally:
    uvicorn api.main:app --reload --port 8000
"""

from __future__ import annotations
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional


# ─── App Setup ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Sentinel-Stream API",
    description="AI Video Surveillance Backend — Events, Alerts, Search",
    version="1.0.0",
)

# CORS: allow React dev server + any localhost frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Request Models ───────────────────────────────────────────────────────────

class TextSearchRequest(BaseModel):
    query: str
    video_id: Optional[str] = None
    limit: int = 20

class SimilarSearchRequest(BaseModel):
    clip_id: str
    top_k: int = 10


# ─── Startup ──────────────────────────────────────────────────────────────────

@app.on_event("startup")
def startup():
    from services.db import init_db
    init_db()


# ─── Health ───────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "sentinel-stream"}


# ─── Videos ───────────────────────────────────────────────────────────────────

@app.get("/api/videos")
def list_videos():
    from services.db import list_videos as db_list
    return {"videos": db_list()}


# ─── Events ───────────────────────────────────────────────────────────────────

@app.get("/api/events")
def list_events(
    video_id: Optional[str] = None,
    alert_stage: Optional[str] = None,
    event_type: Optional[str] = None,
    min_score: Optional[float] = None,
    limit: int = Query(100, le=500),
    offset: int = 0,
):
    """List events with optional filters. Returns clean JSON (no embeddings)."""
    from services.db import get_events
    events = get_events(
        video_id=video_id,
        alert_stage=alert_stage,
        event_type=event_type,
        min_alert_score=min_score,
        limit=limit,
        offset=offset,
    )
    return {"count": len(events), "events": events}


@app.get("/api/events/{clip_id}")
def get_event(clip_id: str):
    """Get a single event by clip_id."""
    from services.db import get_event_by_id
    event = get_event_by_id(clip_id)
    if not event:
        raise HTTPException(status_code=404, detail=f"Event '{clip_id}' not found")
    return {"event": event}


# ─── Alerts ───────────────────────────────────────────────────────────────────

@app.get("/api/alerts")
def list_alerts(
    video_id: Optional[str] = None,
    top_k: int = Query(50, le=200),
):
    """Get top alerts sorted by score (highest first)."""
    from services.db import get_alerts
    alerts = get_alerts(video_id=video_id, top_k=top_k)
    return {"count": len(alerts), "alerts": alerts}


# ─── Timeline ─────────────────────────────────────────────────────────────────

@app.get("/api/timeline")
def timeline(video_id: Optional[str] = None):
    """Compact timeline markers for the frontend visualization."""
    from services.db import get_timeline
    markers = get_timeline(video_id=video_id)
    return {"count": len(markers), "markers": markers}


# ─── Search ───────────────────────────────────────────────────────────────────

@app.post("/api/search/text")
def search_text(req: TextSearchRequest):
    """Search events by caption/tag text match."""
    from services.db import search_events_text
    results = search_events_text(
        query=req.query,
        video_id=req.video_id,
        limit=req.limit,
    )
    return {"query": req.query, "count": len(results), "results": results}


@app.post("/api/search/similar")
def search_similar(req: SimilarSearchRequest):
    """
    Find events visually similar to a given clip_id.
    Uses CLIP embeddings stored in Actian VectorAI.
    """
    try:
        from services.vectordb import search_similar_to_event
        results = search_similar_to_event(
            clip_id=req.clip_id,
            top_k=req.top_k,
        )
        return {
            "query_clip_id": req.clip_id,
            "count": len(results),
            "results": results,
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"VectorAI search failed: {e}. Is Docker running?"
        )


# ─── Stats ────────────────────────────────────────────────────────────────────

@app.get("/api/stats")
def stats():
    """Pipeline statistics for the dashboard header."""
    from services.db import get_stats
    return get_stats()
