"""
Sentinel-Stream — CLI Results Viewer
Prints all AI detections from results/events.json in a clean, tabulated format.
Handles both new (v2) and legacy (v1) JSON structures.
Usage: python view_results.py [path/to/events.json]
"""
import json
import sys
from pathlib import Path


def fmt_time(seconds: float) -> str:
    """Format seconds into M:SS.mmm"""
    m = int(seconds // 60)
    s = seconds % 60
    return f"{m}:{s:06.3f}"


def fmt_ms(ms: float) -> str:
    """Format milliseconds into M:SS.mmm"""
    if ms is None:
        return "N/A"
    return fmt_time(ms / 1000)


def print_header(data: dict) -> None:
    w = 70
    print("=" * w)
    print("  SENTINEL-STREAM  —  AI Video Analysis Report")
    print("=" * w)
    print(f"  Video       : {data['video']}")
    print(f"  Duration    : {data['duration_s']:.1f}s ({data['duration_s']/60:.1f} min)")
    print(f"  Chunks      : {data['chunks']} (CPU parallel workers)")
    print(f"  Sub-clips   : {data['subclips']} processed")
    print(f"  Alerts      : {data['total_alerts']}")
    print(f"  GPU         : {data['gpu']}")
    print(f"  CPU time    : {data['cpu_time_s']:.1f}s")
    print(f"  GPU time    : {data['gpu_time_s']:.1f}s")
    print(f"  Total       : {data['total_time_s']:.1f}s")
    print("-" * w)


def print_event(i: int, e: dict) -> None:
    start = e.get("start", 0)
    end = e.get("end", 0)

    # Handle new vs legacy structure
    alert = e.get("alert", {})
    if not alert:
        alert = {"score": e.get("alert_score", 0), "stage": e.get("alert_stage", "none")}

    ev = e.get("event", {})
    if not ev:
        evts = e.get("events", [{}])
        ev = evts[0] if evts else {}

    detections = e.get("detections", {})
    people = detections.get("people_count", e.get("people_count", 0))
    vehicles = detections.get("vehicle_count", e.get("vehicle_count", 0))

    time_info = e.get("time", {})
    evidence = e.get("evidence", {})
    stage = alert.get("stage", "none")
    score = alert.get("score", 0)

    icon = "!!" if stage in ("B", "C") else "! " if stage == "A" else "  "

    print(f"\n[{icon}] Event {i+1}: {e.get('clip_id', '?')}")
    print(f"    Time     : {fmt_time(start)} - {fmt_time(end)}  ({e.get('duration', 0):.1f}s)")

    if time_info:
        print(f"    Time(ms) : {fmt_ms(time_info.get('start_ms'))} - {fmt_ms(time_info.get('end_ms'))}")
        fd = time_info.get("first_detection_ms")
        ld = time_info.get("last_detection_ms")
        if fd is not None:
            print(f"    Detected : {fmt_ms(fd)} - {fmt_ms(ld)}")

    print(f"    Label    : {ev.get('label', '?')}  (conf={ev.get('confidence', 0)})")
    print(f"    People   : {people}  |  Vehicles: {vehicles}")

    objects = detections.get("objects")
    if objects:
        print(f"    Objects  : {objects}")

    print(f"    Quality  : {e.get('quality_score', 0)}")
    print(f"    Motion   : peak={detections.get('peak_motion', evidence.get('motion', 0)):.4f}  "
          f"contact={detections.get('contact_score', evidence.get('overlap', 0)):.4f}")
    print(f"    Alert    : stage={stage}  score={score}")
    print(f"    Tags     : {', '.join(e.get('tags', []))}")

    tracks = e.get("tracks", [])
    if tracks:
        print(f"    Tracks   : {e.get('track_count', len(tracks))} people")
        for t in tracks[:4]:
            entry = fmt_ms(t.get("entry_ms")) if "entry_ms" in t else "?"
            exit_ = fmt_ms(t.get("exit_ms")) if "exit_ms" in t else "?"
            print(f"      {t['id']}: dwell={t['dwell_seconds']}s  {entry} → {exit_}")
        if len(tracks) > 4:
            print(f"      ... and {len(tracks)-4} more")

    caption = e.get("caption", "")
    if caption:
        lines = [caption[j:j+60] for j in range(0, len(caption), 60)]
        print(f"    Caption  : {lines[0]}")
        for line in lines[1:]:
            print(f"               {line}")


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("results/events.json")
    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(1)

    with open(path) as f:
        data = json.load(f)

    print_header(data)

    events = data.get("events", [])

    # Detect structure version
    sample = events[0] if events else {}
    is_v2 = "alert" in sample and isinstance(sample.get("alert"), dict)

    if is_v2:
        alerts = [e for e in events if e.get("alert", {}).get("stage") != "none"]
    else:
        alerts = [e for e in events if e.get("alert_stage") != "none"]

    print(f"\n  ALL EVENTS ({len(events)}):")
    for i, e in enumerate(events):
        print_event(i, e)

    w = 70
    print(f"\n{'=' * w}")
    print(f"  ALERTS ({len(alerts)} triggered)")
    print("=" * w)
    if not alerts:
        print("  No alerts triggered.")
    else:
        for a in sorted(alerts, key=lambda x: (
            x.get("alert", {}).get("score", x.get("alert_score", 0))
        ), reverse=True):
            if is_v2:
                lbl = a["event"]["label"]
                stg = a["alert"]["stage"]
                scr = a["alert"]["score"]
            else:
                lbl = a["events"][0]["label"] if a.get("events") else "?"
                stg = a["alert_stage"]
                scr = a["alert_score"]
            print(f"  [{stg}] {a['clip_id']}  "
                  f"{fmt_time(a['start'])} - {fmt_time(a['end'])}  "
                  f"score={scr:.3f}  {lbl}")

    print(f"\n{'=' * w}")
    print(f"  Files: {path}  |  results/alerts.json")
    print("=" * w)


if __name__ == "__main__":
    main()
