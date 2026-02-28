#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set

RESULTS_DIR = Path("results")

SCENARIO_PRESETS: Dict[str, Set[str]] = {
    "shoplifting": {"shoplifting_suspected", "theft_suspected", "snatch_and_run", "tampering_detected"},
    "theft": {"theft_suspected", "package_theft", "vehicle_break_in", "shoplifting_suspected", "snatch_and_run"},
    "antitheft": {
        "theft_suspected",
        "shoplifting_suspected",
        "package_theft",
        "vehicle_break_in",
        "snatch_and_run",
        "tampering_detected",
        "suspicious_loitering",
    },
    "human": {
        "aggressive_behavior",
        "physical_altercation",
        "weapon_detected",
        "person_fallen",
        "medical_emergency",
        "person_in_distress",
        "intruder_detected",
    },
    "dog": {
        "dog_aggression",
        "dog_fight",
        "dog_injury_risk",
        "dog_in_distress",
        "dog_leash_incident",
        "dog_left_in_hot_area",
    },
    "all": set(),
}


def _load_events(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"Expected list payload in {path}")
    return data


def _has_matching_tag(tags: Iterable[str], labels: Set[str]) -> bool:
    return any(tag in labels for tag in tags)


def select_likely_scenes(
    events: List[Dict[str, Any]],
    scenario: str,
    min_score: float,
    stages: Set[str],
    limit: int,
) -> List[Dict[str, Any]]:
    labels = SCENARIO_PRESETS[scenario]
    selected: List[Dict[str, Any]] = []

    for event in events:
        event_label = (event.get("event") or {}).get("label", "")
        alert = event.get("alert") or {}
        score = float(alert.get("score", 0.0))
        stage = str(alert.get("stage", "none"))
        tags = event.get("tags") or []

        if score < min_score:
            continue
        if stages and stage not in stages:
            continue
        if labels and event_label not in labels and not _has_matching_tag(tags, labels):
            continue

        selected.append(
            {
                "clip_id": event.get("clip_id"),
                "start": event.get("start"),
                "end": event.get("end"),
                "label": event_label,
                "confidence": (event.get("event") or {}).get("confidence"),
                "alert_score": score,
                "alert_stage": stage,
                "tags": tags,
                "caption": event.get("caption", ""),
            }
        )

    selected.sort(key=lambda item: item["alert_score"], reverse=True)
    return selected[:limit]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Find likely risk scenes from results/events.json")
    parser.add_argument(
        "--scenario",
        choices=sorted(SCENARIO_PRESETS.keys()),
        default="shoplifting",
        help="Scenario preset to filter likely scenes.",
    )
    parser.add_argument("--events", default=str(RESULTS_DIR / "events.json"), help="Path to events.json")
    parser.add_argument("--min-score", type=float, default=0.45, help="Minimum alert score threshold")
    parser.add_argument(
        "--stages",
        default="A,B,C",
        help="Comma-separated allowed alert stages (e.g. B,C). Use empty string to disable stage filter.",
    )
    parser.add_argument("--limit", type=int, default=20, help="Maximum number of scenes to print")
    parser.add_argument("--json", action="store_true", help="Print JSON output instead of table")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    events = _load_events(Path(args.events))
    stages = {s.strip() for s in args.stages.split(",") if s.strip()}

    scenes = select_likely_scenes(
        events=events,
        scenario=args.scenario,
        min_score=args.min_score,
        stages=stages,
        limit=args.limit,
    )

    if args.json:
        print(json.dumps(scenes, indent=2))
        return

    print(f"Scenario: {args.scenario} | matches: {len(scenes)}")
    for row in scenes:
        print(
            f"{row['clip_id']} | {row['start']:.2f}-{row['end']:.2f}s | "
            f"{row['label']} ({float(row['confidence'] or 0.0):.2f}) | stage {row['alert_stage']} | score {row['alert_score']:.3f}"
        )


if __name__ == "__main__":
    main()
