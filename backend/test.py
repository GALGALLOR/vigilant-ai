"""
Sentinel-Stream — High Alerts Only (SHORT)
Prints only higher alerts from results/events.json:
  - time range
  - score
  - caption (or label fallback)

Handles both new (v2) and legacy (v1) JSON structures.

Usage:
  python view_results.py
  python view_results.py path/to/events.json
"""
import json
import sys
from pathlib import Path

# 🔧 TUNE THESE:
MIN_SCORE = 0.10          # only show alerts with score >= this
TOP_N = 50                # show only top N (by score). set None to show all
MIN_GAP_SECONDS = 20.0    # suppress alerts too close in time (0 disables)


def fmt_time(seconds: float) -> str:
    m = int(seconds // 60)
    s = seconds % 60
    return f"{m}:{s:06.3f}"


def get_stage_score(e: dict) -> tuple[str, float]:
    alert = e.get("alert")
    if isinstance(alert, dict):
        stage = str(alert.get("stage", "none"))
        score = float(alert.get("score", 0.0) or 0.0)
        return stage, score
    stage = str(e.get("alert_stage", "none"))
    score = float(e.get("alert_score", 0.0) or 0.0)
    return stage, score


def get_label(e: dict) -> str:
    ev = e.get("event")
    if isinstance(ev, dict) and ev.get("label"):
        return str(ev.get("label"))
    evts = e.get("events")
    if isinstance(evts, list) and evts:
        return str((evts[0] or {}).get("label", "?"))
    return "?"


def get_description(e: dict) -> str:
    caption = (e.get("caption") or "").strip()
    return caption if caption else get_label(e)


def suppress_nearby(sorted_events: list[dict], min_gap: float) -> list[dict]:
    """Keep highest score events, suppress ones within min_gap seconds of already kept events."""
    if min_gap <= 0:
        return sorted_events

    kept = []
    kept_starts = []

    for e in sorted_events:
        start = float(e.get("start", 0.0) or 0.0)
        if any(abs(start - ks) < min_gap for ks in kept_starts):
            continue
        kept.append(e)
        kept_starts.append(start)

    return kept


def print_header(data: dict) -> None:
    w = 80
    video = data.get("video", "?")
    dur = float(data.get("duration_s", 0.0) or 0.0)
    total_alerts = data.get("total_alerts", "?")
    print("=" * w)
    print("  SENTINEL-STREAM — HIGH ALERTS ONLY")
    print("=" * w)
    print(f"  Video    : {video}")
    print(f"  Duration : {dur:.1f}s ({dur/60:.1f} min)")
    print(f"  Alerts   : {total_alerts}")
    print("-" * w)


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("results/events.json")
    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print_header(data)

    events = data.get("events", []) or []

    # Filter: only important alerts (B/C OR score >= MIN_SCORE)
    important = []
    for e in events:
        stage, score = get_stage_score(e)
        if stage in ("B", "C") or score >= MIN_SCORE:
            important.append(e)

    if not important:
        print("No high/important alerts found for your threshold.")
        return

    # Sort by score DESC (most important first)
    important.sort(key=lambda x: get_stage_score(x)[1], reverse=True)

    # Suppress near-duplicates in time
    important = suppress_nearby(important, MIN_GAP_SECONDS)

    # Limit to TOP_N
    if TOP_N is not None:
        important = important[:TOP_N]

    # Print only time + caption + score
    for e in important:
        stage, score = get_stage_score(e)
        start = float(e.get("start", 0.0) or 0.0)
        end = float(e.get("end", 0.0) or 0.0)
        desc = get_description(e)

        # keep output short
        if len(desc) > 140:
            desc = desc + "..."

        print(f"[{stage}] score={score:.3f}  {fmt_time(start)} - {fmt_time(end)}  {desc}")

    print("-" * 80)
    print(f"File: {path}")


if __name__ == "__main__":
    main()