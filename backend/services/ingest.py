"""
Sentinel-Stream — Ingest Pipeline Results into Databases
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
After video processing completes, ingests data into:
  1. SQLite — structured events + videos table
  2. VectorAI — CLIP embeddings for similarity search
  3. Gemini — holistic video synthesis (summary + intent)

Usage:
    python -m services.ingest results/events.json
"""

import json
import sys
import os
from pathlib import Path
import tempfile
import threading
from typing import Dict, List


def _strip_private(event: dict) -> dict:
    """Remove _prefixed keys (embeddings, trajectories) from event for JSON storage."""
    return {k: v for k, v in event.items() if not k.startswith("_")}


def ingest_results(events_json_path: str, delete_json: bool = False) -> None:
    from services.db import init_db, insert_video, insert_events, save_video_summary

    path = Path(events_json_path)
    if not path.exists():
        print(f"File not found: {path}")
        return

    with open(path) as f:
        data = json.load(f)

    events     = data.get("events", [])
    video_name = data.get("video", "unknown.mp4")
    video_id   = video_name.replace(".", "_").replace(" ", "_")

    if not events:
        print("No events in results file")
        return

    def _get_stage(e):
        a = e.get("alert", {})
        if isinstance(a, dict):
            return a.get("stage", "none")
        return e.get("alert_stage", "none")
    alerts = [e for e in events if _get_stage(e) != "none"]

    print(f"Ingesting {len(events)} events for '{video_name}'...")

    # ── 1. SQLite ──────────────────────────────────────────────────────────────
    init_db()
    insert_video(
        video_id          = video_id,
        name              = video_name,
        duration_s        = data.get("duration_s", 0),
        total_events      = len(events),
        total_alerts      = len(alerts),
        processing_time_s = data.get("processing_time_s", data.get("total_time_s", 0)),
        gpu               = data.get("gpu", "A100-80GB"),
        chunks            = data.get("chunks", 0),
        subclips          = data.get("subclips", 0),
        cpu_time_s        = data.get("cpu_time_s", 0.0),
        gpu_time_s        = data.get("gpu_time_s", 0.0),
    )
    n_inserted = insert_events(video_id, events)
    print(f"  SQLite: {n_inserted} events inserted")

    # ── 2. VectorAI ───────────────────────────────────────────────────────────
    try:
        from services.vectordb import ensure_collection, ingest_events
        ensure_collection()
        n_vectors = ingest_events(events)
        print(f"  VectorAI: {n_vectors} embeddings inserted")
    except Exception as e:
        print(f"  VectorAI: skipped ({e})")

    # ── 3. Gemini Synthesis ───────────────────────────────────────────────────
    try:
        from services.gemini_synthesis import synthesize_video
        print("  Gemini: synthesizing video summary...")
        synthesis = synthesize_video(events, video_name)
        save_video_summary(video_id, synthesis)
        print(f"  Gemini: summary saved (intent={synthesis.get('intent', [])}, risk={synthesis.get('risk_level', '?')})")
    except Exception as e:
        print(f"  Gemini: synthesis failed ({e})")

    # ── 4. Cleanup ────────────────────────────────────────────────────────────
    if delete_json:
        try:
            os.remove(path)
            print(f"  Cleanup: deleted {path.name}")
        except Exception:
            pass

    print(f"Ingest complete: {len(events)} events, {len(alerts)} alerts")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "results/events.json"
    ingest_results(path)


# ─── Streamed ingest helper ──────────────────────────────────────────────────
# Buffers short binary chunks (from WebSocket MediaRecorder) per client and
# writes a clip file once enough chunks are accumulated, then calls
# `workers.inference.analyze_clip` in a background thread.
_client_buffers: Dict[str, List[bytes]] = {}
CHUNKS_PER_CLIP = 1  # number of MediaRecorder blobs to assemble per clip


async def ingest_frame(client_id: str, chunk_bytes: bytes) -> None:
    """Called by the WebSocket handler. Buffers chunks and spawns a background
    thread to analyze an assembled clip once the threshold is reached.
    """
    buf = _client_buffers.setdefault(client_id, [])
    buf.append(chunk_bytes)
    if len(buf) < CHUNKS_PER_CLIP:
        return

    # assemble clip on disk
    uploads_dir = Path(__file__).parent.parent / "uploads"
    uploads_dir.mkdir(exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(suffix=".webm", dir=str(uploads_dir))
    os.close(fd)
    try:
        with open(tmp_path, "wb") as f:
            for b in buf:
                f.write(b)
    except Exception as e:
        print(f"[ingest] failed to write clip: {e}")
        try:
            os.remove(tmp_path)
        except Exception:
            pass
        _client_buffers[client_id] = []
        return

    # reset buffer
    _client_buffers[client_id] = []

    def _analyze(path: str):
        try:
            from workers import inference
            inference.analyze_clip(path)
        except Exception as e:
            print(f"[ingest] analysis failed: {e}")
        finally:
            try:
                os.remove(path)
            except Exception:
                pass

    threading.Thread(target=_analyze, args=(tmp_path,), daemon=True).start()
