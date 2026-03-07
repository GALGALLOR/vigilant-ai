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


def _strip_private(event: dict) -> dict:
    """Remove _prefixed keys (embeddings, trajectories) from event for JSON storage."""
    return {k: v for k, v in event.items() if not k.startswith("_")}


_THREAT_LABELS = {
    "physical_altercation", "assault_detected", "fighting_detected",
    "theft_detected",       "shoplifting_detected",
    "vandalism",            "weapon_detected",   "trespassing",
}
_LABEL_TO_INTENT = {
    "physical_altercation":  "assault/fighting",
    "assault_detected":      "assault/fighting",
    "fighting_detected":     "assault/fighting",
    "theft_detected":        "theft",
    "shoplifting_detected":  "shoplifting",
    "vandalism":             "vandalism",
    "weapon_detected":       "assault/fighting",
    "trespassing":           "trespassing",
}

def _validate_synthesis(synthesis: dict, events: list) -> dict:
    """
    Safety net: prevent Gemini synthesis from contradicting hard CV signals.

    Case 1 — Synthesis says normal_activity but CV labels say threat:
      If ≥30% of clips have a threat label, override intent + risk.

    Case 2 — Synthesis risk is 'low' but many alerts fired:
      If ≥50% of clips triggered alerts, bump risk to at least 'medium'.
    """
    if not events:
        return synthesis

    from collections import Counter

    threat_labels_found = [
        e.get("event", {}).get("label", "")
        for e in events
        if e.get("event", {}).get("label", "") in _THREAT_LABELS
    ]
    alert_count = sum(
        1 for e in events
        if e.get("alert", {}).get("stage", "none") != "none"
    )

    intent   = synthesis.get("intent", [])
    risk     = synthesis.get("risk_level", "low")
    n        = len(events)

    # Case 1: threat labels present but synthesis says normal
    threat_ratio = len(threat_labels_found) / n
    if threat_ratio >= 0.3 and (not intent or intent == ["normal_activity"] or "normal_activity" in intent):
        top_label   = Counter(threat_labels_found).most_common(1)[0][0]
        new_intent  = _LABEL_TO_INTENT.get(top_label, "suspicious_behavior")
        synthesis["intent"] = [new_intent, "suspicious_behavior"]
        synthesis["risk_level"] = "high" if threat_ratio >= 0.5 else "medium"
        print(f"  ⚠️  Synthesis override: intent corrected to '{new_intent}' "
              f"({len(threat_labels_found)}/{n} clips had threat CV labels)")

    # Case 2: many alerts but risk is low
    alert_ratio = alert_count / n
    if alert_ratio >= 0.5 and synthesis.get("risk_level", "low") == "low":
        synthesis["risk_level"] = "medium"
        print(f"  ⚠️  Synthesis override: risk bumped low→medium "
              f"({alert_count}/{n} clips had alerts)")

    return synthesis


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
    synthesis: dict = {}
    try:
        from services.gemini_synthesis import synthesize_video
        print("  Gemini: synthesizing video summary...")
        synthesis = synthesize_video(events, video_name)
        synthesis = _validate_synthesis(synthesis, events)   # safety net — CV labels override synthesis
        save_video_summary(video_id, synthesis)
        print(f"  Gemini: summary saved (intent={synthesis.get('intent', [])}, risk={synthesis.get('risk_level', '?')})")
    except Exception as e:
        print(f"  Gemini: synthesis failed ({e})")

    # ── 4. Supermemory — Cross-Video Intelligence ─────────────────────────────
    try:
        from services.supermemory_client import store_video_intelligence
        store_video_intelligence(
            video_id=video_id,
            video_name=video_name,
            synthesis=synthesis,
            alerts=alerts,
            duration_s=data.get("duration_s", 0),
        )
    except Exception as e:
        print(f"  Supermemory: skipped ({e})")

    # ── 5. Cleanup ────────────────────────────────────────────────────────────
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
