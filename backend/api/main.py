"""
Sentinel-Stream — FastAPI Backend
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REST API for the React frontend. Handles:
  - Video upload → Modal pipeline → Gemini synthesis → ingest
  - Per-video events, alerts, summaries
  - RAG-powered chat (Gemini answers + CLIP search)
  - Persistent chat history
  - Dashboard stats & insights

IMPORTANT: Before uploading, deploy the Modal app once:
    modal deploy workers/inference.py

Run locally:
    uvicorn api.main:app --reload --port 8000
"""

from __future__ import annotations
import os, json, time, math, traceback

# Load .env from backend/ directory before anything else reads os.environ
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
except ImportError:
    pass
from pathlib import Path
from fastapi import FastAPI, Query, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, AsyncIterator


# ─── App Setup ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Sentinel-Stream API",
    description="AI Video Surveillance Backend — Upload, Analyze, Search",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_UPLOAD_MB = 5120
UPLOAD_DIR = Path(__file__).parent.parent / "uploads"
RESULTS_DIR = Path(__file__).parent.parent / "results"

_jobs: Dict[str, Dict] = {}


# ─── Request Models ───────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    query: str
    video_id: Optional[str] = None
    top_k: int = 10


class MemoryQueryRequest(BaseModel):
    query: str
    video_id: Optional[str] = None


# ─── Startup ──────────────────────────────────────────────────────────────────

@app.on_event("startup")
def startup():
    from services.db import init_db
    init_db()
    UPLOAD_DIR.mkdir(exist_ok=True)
    RESULTS_DIR.mkdir(exist_ok=True)

    # Pre-warm CLIP text encoder in background — eliminates ~30s cold start on first chat
    import threading
    def _warm_clip():
        try:
            from services.clip_search import encode_text
            encode_text("security camera footage person walking")
            print("✅ CLIP text encoder pre-warmed")
        except Exception as e:
            print(f"⚠️  CLIP warmup failed: {e}")
    threading.Thread(target=_warm_clip, daemon=True).start()


# ─── Health ───────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "sentinel-stream"}


# ─── Upload Pipeline ─────────────────────────────────────────────────────────

def _cleanup(path: str):
    try:
        os.remove(path)
    except Exception:
        pass


def _process_video_background(video_id: str, video_name: str, file_path: str):
    """Background: upload → Modal → ingest (SQLite + VectorAI + Gemini) → cleanup."""
    try:
        import modal

        t_start = time.time()

        # Step 1: Upload to Modal Volume
        _jobs[video_id] = {"status": "uploading", "progress": 10, "error": None}
        video_vol = modal.Volume.from_name("vigilant-videos", create_if_missing=True)
        with video_vol.batch_upload(force=True) as batch:
            batch.put_file(file_path, video_name)
        print(f"[upload] '{video_name}' → Modal Volume")

        # Step 2: Call deployed Modal functions
        _jobs[video_id] = {"status": "processing", "progress": 25, "error": None}

        get_video_duration = modal.Function.from_name("vigilant-ai", "get_video_duration")
        chunk_and_score = modal.Function.from_name("vigilant-ai", "chunk_and_score")
        FeatureExtractorCls = modal.Cls.from_name("vigilant-ai", "FeatureExtractor")
        extractor = FeatureExtractorCls()

        total_seconds = get_video_duration.remote(video_name)
        print(f"[upload] Duration: {total_seconds:.1f}s")
        _jobs[video_id]["progress"] = 35

        num_chunks = max(1, math.ceil(total_seconds / 300.0))
        chunk_args = [
            (video_name, i * 300.0, min((i + 1) * 300.0, total_seconds), i)
            for i in range(num_chunks)
        ]

        _jobs[video_id]["progress"] = 40
        t_cpu_start = time.time()
        chunked_results = list(chunk_and_score.map(chunk_args, order_outputs=True))
        cpu_time_s = time.time() - t_cpu_start
        all_subclips = [sc for chunk_scs in chunked_results for sc in chunk_scs]
        print(f"[upload] {len(all_subclips)} sub-clips (CPU phase: {cpu_time_s:.1f}s)")

        _jobs[video_id]["progress"] = 60

        if not all_subclips:
            _cleanup(file_path)
            _jobs[video_id] = {"status": "done", "progress": 100, "error": None,
                               "message": "No active scenes detected"}
            return

        t_gpu_start = time.time()
        events = list(extractor.extract_from_window.map(all_subclips, order_outputs=False))
        gpu_time_s = time.time() - t_gpu_start
        events.sort(key=lambda e: e["start"])
        print(f"[upload] {len(events)} events (GPU phase: {gpu_time_s:.1f}s)")

        _jobs[video_id]["progress"] = 75

        # Step 3: Save results + ingest (SQLite + VectorAI + Gemini)
        alerts = [e for e in events if e["alert"]["stage"] != "none"]
        total_time_s = time.time() - t_start
        events_path = RESULTS_DIR / f"{video_id}_events.json"
        with open(events_path, "w") as f:
            json.dump({
                "video": video_name,
                "duration_s": total_seconds,
                "total_alerts": len(alerts),
                "gpu": "A100-80GB",
                "chunks": num_chunks,
                "subclips": len(all_subclips),
                "cpu_time_s": round(cpu_time_s, 1),
                "gpu_time_s": round(gpu_time_s, 1),
                "processing_time_s": round(total_time_s, 1),
                "events": events,
            }, f)

        _jobs[video_id] = {"status": "analyzing", "progress": 85, "error": None}

        from services.ingest import ingest_results
        ingest_results(str(events_path), delete_json=True)

        _cleanup(file_path)
        _jobs[video_id] = {"status": "done", "progress": 100, "error": None}
        print(f"[upload] Complete '{video_name}' in {total_time_s:.1f}s")

    except Exception as e:
        traceback.print_exc()
        _jobs[video_id] = {"status": "error", "progress": 0, "error": str(e)}
        _cleanup(file_path)


@app.post("/api/upload")
async def upload_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "No file provided")

    video_name = file.filename
    video_id = video_name.replace(".", "_").replace(" ", "_").lower()
    file_path = str(UPLOAD_DIR / video_name)

    # Stream to disk in chunks — supports files up to MAX_UPLOAD_MB without OOM
    chunk_size = 4 * 1024 * 1024  # 4 MB chunks
    total_bytes = 0
    with open(file_path, "wb") as f:
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            total_bytes += len(chunk)
            size_mb = total_bytes / (1024 * 1024)
            if size_mb > MAX_UPLOAD_MB:
                f.close()
                _cleanup(file_path)
                raise HTTPException(413, f"File too large (max {MAX_UPLOAD_MB}MB)")
            f.write(chunk)

    size_mb = total_bytes / (1024 * 1024)
    _jobs[video_id] = {"status": "queued", "progress": 0, "error": None}
    background_tasks.add_task(_process_video_background, video_id, video_name, file_path)
    return {"video_id": video_id, "video_name": video_name, "size_mb": round(size_mb, 1),
            "status": "queued", "message": "Processing started."}


@app.get("/api/upload/status/{video_id}")
def upload_status(video_id: str):
    job = _jobs.get(video_id)
    if not job:
        return {"video_id": video_id, "status": "unknown"}
    return {"video_id": video_id, **job}


# ─── Videos ───────────────────────────────────────────────────────────────────

@app.get("/api/videos")
def list_videos():
    from services.db import list_videos as db_list
    return {"videos": db_list()}


@app.get("/api/videos/{video_id}")
def video_info(video_id: str):
    from services.db import list_videos as db_list
    videos = db_list()
    for v in videos:
        if v["id"] == video_id:
            return v
    raise HTTPException(404, f"Video '{video_id}' not found")


# ─── Per-Video: Events, Alerts, Summary ───────────────────────────────────────

@app.get("/api/videos/{video_id}/events")
def video_events(video_id: str, limit: int = Query(100, le=500)):
    from services.db import get_events
    events = get_events(video_id=video_id, limit=limit)
    return {"video_id": video_id, "count": len(events), "events": events}


@app.get("/api/videos/{video_id}/alerts")
def video_alerts(video_id: str, top_k: int = Query(50, le=200)):
    from services.db import get_alerts
    alerts = get_alerts(video_id=video_id, top_k=top_k)
    return {"video_id": video_id, "count": len(alerts), "alerts": alerts}


@app.get("/api/videos/{video_id}/summary")
def video_summary(video_id: str):
    from services.db import get_video_summary
    summary = get_video_summary(video_id)
    if not summary:
        return {"video_id": video_id, "summary": None}
    return summary


@app.get("/api/videos/{video_id}/insights")
def video_insights(video_id: str):
    """Chart-ready data: event types, alert distribution, activity timeline."""
    from services.db import get_events, get_alerts
    events = get_events(video_id=video_id, limit=500)
    alerts = get_alerts(video_id=video_id, top_k=100)

    # Event type distribution
    type_counts: Dict[str, int] = {}
    timeline_points = []
    for e in events:
        label = ""
        if isinstance(e.get("event"), dict):
            label = e["event"].get("label", "unknown")
        elif e.get("event_type"):
            label = e["event_type"]
        else:
            label = "unknown"
        type_counts[label] = type_counts.get(label, 0) + 1

        timeline_points.append({
            "start": e.get("start", 0),
            "end": e.get("end", 0),
            "label": label,
            "alert_stage": e.get("alert", {}).get("stage", "none") if isinstance(e.get("alert"), dict) else "none",
            "people": e.get("detections", {}).get("people_count", 0) if isinstance(e.get("detections"), dict) else 0,
        })

    # Alert stage distribution
    stage_counts = {"none": 0, "A": 0, "B": 0, "C": 0}
    for a in alerts:
        stage = a.get("alert", {}).get("stage", "none") if isinstance(a.get("alert"), dict) else "none"
        stage_counts[stage] = stage_counts.get(stage, 0) + 1

    return {
        "video_id": video_id,
        "event_types": type_counts,
        "alert_stages": stage_counts,
        "timeline": timeline_points,
        "total_events": len(events),
        "total_alerts": len(alerts),
    }


# ─── Chat (RAG-powered with Gemini) ──────────────────────────────────────────

@app.post("/api/chat")
def chat_search(req: ChatRequest):
    """
    RAG chat: retrieve relevant events → Gemini synthesizes conversational answer.
    Also persists chat history per video.
    """
    from services.clip_search import hybrid_search
    from services.gemini_synthesis import chat_answer
    from services.db import get_video_summary, save_chat_message

    # Step 1: Retrieve relevant events
    relevant = hybrid_search(query=req.query, video_id=req.video_id, top_k=req.top_k)

    # Step 2: Get video summary for context
    summary_text = None
    video_name = ""
    if req.video_id:
        summary = get_video_summary(req.video_id)
        if summary:
            summary_text = summary.get("summary", "")
            video_name = req.video_id

    # Step 3: Gemini RAG answer
    answer = chat_answer(
        query=req.query,
        relevant_events=relevant,
        video_summary=summary_text,
        video_name=video_name,
    )

    # Step 4: Persist chat history
    if req.video_id:
        save_chat_message(req.video_id, "user", req.query)
        save_chat_message(req.video_id, "assistant", answer,
                          results_json=json.dumps([r.get("clip_id", "") for r in relevant[:5]]))

    return {
        "query": req.query,
        "answer": answer,
        "count": len(relevant),
        "results": relevant,
    }


# ─── Streaming Chat (SSE) ────────────────────────────────────────────────────

@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest):
    """
    Streaming RAG chat via Server-Sent Events.
    Returns text/event-stream with 'data: <chunk>\n\n' format.
    """
    from services.clip_search import hybrid_search
    from services.gemini_synthesis import chat_answer_stream
    from services.db import get_video_summary, save_chat_message

    relevant = hybrid_search(query=req.query, video_id=req.video_id, top_k=req.top_k)

    summary_text = None
    video_name = ""
    if req.video_id:
        summary = get_video_summary(req.video_id)
        if summary:
            summary_text = summary.get("summary", "")
            video_name = req.video_id

    # Save user message
    if req.video_id:
        save_chat_message(req.video_id, "user", req.query)

    async def event_stream() -> AsyncIterator[str]:
        # Phase 1: emit search results immediately (before Gemini starts)
        # Frontend can render matching clips while waiting for narrative
        results_payload = json.dumps([r.get("clip_id", "") for r in relevant[:5]])
        yield f"event: results\ndata: {json.dumps({'count': len(relevant), 'results': relevant[:8]})}\n\n"

        # Phase 2: stream Gemini narrative token by token
        full_answer: List[str] = []
        async for chunk in chat_answer_stream(
            query=req.query,
            relevant_events=relevant,
            video_summary=summary_text,
            video_name=video_name,
        ):
            full_answer.append(chunk)
            yield f"event: token\ndata: {json.dumps(chunk)}\n\n"

        if req.video_id:
            save_chat_message(req.video_id, "assistant", "".join(full_answer),
                              results_json=results_payload)
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ─── Chat History ─────────────────────────────────────────────────────────────

@app.get("/api/videos/{video_id}/chat")
def chat_history(video_id: str, limit: int = Query(50, le=200)):
    from services.db import get_chat_history
    messages = get_chat_history(video_id, limit=limit)
    return {"video_id": video_id, "messages": messages}


# ─── Events (global) ─────────────────────────────────────────────────────────

@app.get("/api/events")
def list_events(
    video_id: Optional[str] = None,
    limit: int = Query(100, le=500),
    offset: int = 0,
):
    from services.db import get_events
    events = get_events(video_id=video_id, limit=limit, offset=offset)
    return {"count": len(events), "events": events}


@app.get("/api/events/{clip_id}")
def get_event(clip_id: str):
    from services.db import get_event_by_id
    event = get_event_by_id(clip_id)
    if not event:
        raise HTTPException(404, f"Event '{clip_id}' not found")
    return {"event": event}


# ─── Alerts (global) ─────────────────────────────────────────────────────────

@app.get("/api/alerts")
def list_alerts(video_id: Optional[str] = None, top_k: int = Query(50, le=200)):
    from services.db import get_alerts
    alerts = get_alerts(video_id=video_id, top_k=top_k)
    return {"count": len(alerts), "alerts": alerts}


# ─── Timeline ────────────────────────────────────────────────────────────────

@app.get("/api/timeline")
def timeline(video_id: Optional[str] = None):
    from services.db import get_timeline
    markers = get_timeline(video_id=video_id)
    return {"count": len(markers), "markers": markers}


# ─── Stats ────────────────────────────────────────────────────────────────────

@app.get("/api/stats")
def stats():
    from services.db import get_stats
    return get_stats()


# ─── Incident Report ─────────────────────────────────────────────────────────

@app.get("/api/videos/{video_id}/report")
def video_report(
    video_id: str,
    as_text: bool = Query(False),
    as_pdf: bool = Query(False),
):
    """
    Generate a consolidated incident report for an entire video.
    Use ?as_pdf=true for a PDF download, ?as_text=true for plain-text.
    """
    from services.db import get_events, get_video_summary
    from services.incident_report import generate_incident_report, report_to_text, report_to_pdf

    events = get_events(video_id=video_id, limit=500)
    if not events:
        raise HTTPException(404, f"No events found for video '{video_id}'")

    synthesis = get_video_summary(video_id) or {}
    video_name = events[0].get("video_source", video_id) if events else video_id
    report = generate_incident_report(video_id, video_name, events, synthesis)

    if as_pdf:
        pdf_bytes = report_to_pdf(report)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=report_{video_id}.pdf",
                "Cache-Control": "no-store",
            },
        )

    if as_text:
        text = report_to_text(report)
        return Response(
            content=text,
            media_type="text/plain",
            headers={
                "Content-Disposition": f"attachment; filename=report_{video_id}.txt",
                "Cache-Control": "no-store",
            },
        )
    return report


# ─── Cross-Video Memory (Supermemory) ────────────────────────────────────────

@app.post("/api/memory/query")
def memory_query(req: MemoryQueryRequest):
    """Natural-language cross-video intelligence search via Supermemory."""
    from services.supermemory_client import query_intelligence
    return query_intelligence(query=req.query, video_id=req.video_id)


# ─── Benchmarks ───────────────────────────────────────────────────────────────

@app.get("/api/benchmarks/modal")
def modal_benchmark():
    """Modal GPU compute performance metrics aggregated from all processed videos."""
    from services.db import list_videos
    videos = list_videos()

    total_gpu_s    = sum(v.get("gpu_time_s", 0) or 0 for v in videos)
    total_cpu_s    = sum(v.get("cpu_time_s", 0) or 0 for v in videos)
    total_subclips = sum(v.get("subclips",   0) or 0 for v in videos)
    total_chunks   = sum(v.get("chunks",     0) or 0 for v in videos)
    total_proc_s   = sum(v.get("processing_time_s", 0) or 0 for v in videos)

    # Sequential baseline: ~8s per subclip on a single CPU core (no GPU, no parallelism)
    serial_estimate_s = total_subclips * 8.0
    speedup = round(serial_estimate_s / total_gpu_s, 1) if total_gpu_s > 0 else 0.0

    return {
        "gpu_type":                "A100",
        "max_containers":          50,
        "peak_parallelism":        50,
        "total_videos_processed":  len(videos),
        "total_subclips_processed": total_subclips,
        "total_chunks":            total_chunks,
        "total_gpu_time_s":        round(total_gpu_s, 1),
        "total_cpu_time_s":        round(total_cpu_s, 1),
        "total_processing_s":      round(total_proc_s, 1),
        "avg_gpu_time_s":          round(total_gpu_s / len(videos), 1) if videos else 0.0,
        "avg_cpu_time_s":          round(total_cpu_s / len(videos), 1) if videos else 0.0,
        "estimated_serial_s":      round(serial_estimate_s, 1),
        "speedup_x":               speedup,
        "videos": [
            {
                "name":         v["name"],
                "chunks":       v.get("chunks", 0),
                "subclips":     v.get("subclips", 0),
                "gpu_time_s":   v.get("gpu_time_s", 0),
                "cpu_time_s":   v.get("cpu_time_s", 0),
                "processing_s": v.get("processing_time_s", 0),
            }
            for v in videos
        ],
    }


@app.get("/api/benchmarks/vectorai")
def vectorai_benchmark():
    """VectorAI (Actian) search latency benchmark — runs a live test query."""
    import time as _time
    from services.clip_search import hybrid_search, encode_text
    from services.db import get_stats

    # Measure CLIP text-encode latency
    t0 = _time.time()
    encode_text("person walking aggressive behavior surveillance")
    encode_ms = round((_time.time() - t0) * 1000, 1)

    # Measure end-to-end hybrid search latency (CLIP + SQLite)
    t1 = _time.time()
    results = hybrid_search(query="person walking", video_id=None, top_k=5)
    search_ms = round((_time.time() - t1) * 1000, 1)

    # Total vector count ≈ total events (each event has a 768-dim CLIP vector)
    s = get_stats()

    return {
        "collection":                "vigilant_clips",
        "dimensions":                768,
        "distance_metric":           "COSINE",
        "model":                     "CLIP ViT-L/14",
        "clip_encode_latency_ms":    encode_ms,
        "hybrid_search_latency_ms":  search_ms,
        "total_vectors":             s.get("total_events", 0),
        "results_returned":          len(results),
    }
