"""
Sentinel-Stream — Ingest Pipeline Results into Databases
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Called after `modal run workers/inference.py` completes.
Reads results/events.json and pushes data into:
  1. SQLite (vigilant.db) — structured events + videos table
  2. Actian VectorAI (localhost:50051) — CLIP embeddings for similarity search

Usage:
    python -m services.ingest results/events.json
"""

import json
import sys
from pathlib import Path


def _strip_private(event: dict) -> dict:
    """Remove _prefixed keys (embeddings, trajectories) from event for JSON storage."""
    return {k: v for k, v in event.items() if not k.startswith("_")}


def ingest_results(events_json_path: str) -> None:
    from services.db import init_db, insert_video, insert_events
    from services.vectordb import ensure_collection, ingest_events

    path = Path(events_json_path)
    if not path.exists():
        print(f"❌ File not found: {path}")
        sys.exit(1)

    with open(path) as f:
        data = json.load(f)

    events     = data.get("events", [])
    video_name = data.get("video", "unknown.mp4")
    video_id   = video_name.replace(".", "_").replace(" ", "_")

    if not events:
        print("⚠️  No events in results file")
        return

    def _get_stage(e):
        a = e.get("alert", {})
        if isinstance(a, dict):
            return a.get("stage", "none")
        return e.get("alert_stage", "none")
    alerts = [e for e in events if _get_stage(e) != "none"]

    print(f"\n📥 Ingesting {len(events)} events for '{video_name}'...")

    # ── 1. SQLite ──────────────────────────────────────────────────────────────
    print("  🗄  SQLite...")
    init_db()
    insert_video(
        video_id          = video_id,
        name              = video_name,
        duration_s        = data.get("duration_s", 0),
        total_events      = len(events),
        total_alerts      = len(alerts),
        processing_time_s = data.get("total_time_s", 0),
        gpu               = data.get("gpu", "A10G"),
    )
    n_inserted = insert_events(video_id, events)
    print(f"     ✅ {n_inserted} events inserted into SQLite")

    # ── 2. Actian VectorAI ─────────────────────────────────────────────────────
    print("  🔍  Actian VectorAI...")
    try:
        ensure_collection()
        n_vectors = ingest_events(events)
        print(f"     ✅ {n_vectors} embeddings inserted into VectorAI")
    except Exception as e:
        print(f"     ⚠️  VectorAI insert failed: {e}")
        print(f"        Make sure Docker is running: docker compose up -d")

    print(f"\n✅ Ingest complete — {len(events)} events, {len(alerts)} alerts")
    print(f"   SQLite: vigilant.db")
    print(f"   VectorAI collection: vigilant_events")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "results/events.json"
    ingest_results(path)
