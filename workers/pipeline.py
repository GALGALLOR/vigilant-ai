from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re
from typing import Dict, Iterable, List, Sequence, Tuple

CHUNK_SECONDS = 300
MOTION_SAMPLE_FPS = 2
MOTION_THRESHOLD = 0.05
ACTIVE_MIN_SECS = 1.5
WINDOW_MERGE_GAP = 5.0
SUBCLIP_DURATION = 10
SUBCLIP_OVERLAP = 2
SUBCLIP_STRIDE = SUBCLIP_DURATION - SUBCLIP_OVERLAP
QUALITY_THRESHOLD = 0.08
ALERT_B_THRESHOLD = 0.45
ALERT_C_THRESHOLD = 0.70
AFTER_HOURS_START = 22
AFTER_HOURS_END = 6

LABELS = [
    "handshake",
    "hug",
    "helping_gesture",
    "aggressive_behavior",
    "physical_altercation",
    "weapon_detected",
    "person_fallen",
    "medical_emergency",
    "person_in_distress",
    "intruder_detected",
    "after_hours_activity",
    "activity_detected",
]

SEVERITY_MAP = {
    "handshake": "low",
    "hug": "low",
    "helping_gesture": "low",
    "aggressive_behavior": "medium",
    "physical_altercation": "high",
    "weapon_detected": "critical",
    "person_fallen": "high",
    "medical_emergency": "critical",
    "person_in_distress": "medium",
    "intruder_detected": "high",
    "after_hours_activity": "medium",
    "activity_detected": "low",
}

CAPTION_KEYWORDS: Dict[str, str] = {
    "handshake": "handshake",
    "hug": "hug",
    "help": "helping_gesture",
    "assist": "helping_gesture",
    "fight": "physical_altercation",
    "punch": "aggressive_behavior",
    "kick": "aggressive_behavior",
    "weapon": "weapon_detected",
    "gun": "weapon_detected",
    "knife": "weapon_detected",
    "fall": "person_fallen",
    "collapsed": "medical_emergency",
    "medical": "medical_emergency",
    "distress": "person_in_distress",
    "intruder": "intruder_detected",
    "trespass": "intruder_detected",
}

WEIGHTS = {
    "contact_score": 0.30,
    "motion": 0.20,
    "people": 0.15,
    "vehicles": 0.05,
    "after_hours": 0.10,
    "threats": 0.20,
}

SAFE_LABELS = {"handshake", "hug", "helping_gesture"}
HIGH_LABELS = {"physical_altercation", "person_fallen", "intruder_detected"}
CRITICAL_LABELS = {"weapon_detected", "medical_emergency"}


@dataclass
class Thresholds:
    motion_threshold: float = MOTION_THRESHOLD
    active_min_secs: float = ACTIVE_MIN_SECS
    merge_gap: float = WINDOW_MERGE_GAP
    quality_threshold: float = QUALITY_THRESHOLD
    alert_b_threshold: float = ALERT_B_THRESHOLD
    alert_c_threshold: float = ALERT_C_THRESHOLD


thresholds = Thresholds()


def make_video_chunks(duration_seconds: float, chunk_seconds: int = CHUNK_SECONDS) -> List[Tuple[float, float]]:
    if duration_seconds <= 0:
        return []
    chunks: List[Tuple[float, float]] = []
    start = 0.0
    while start < duration_seconds:
        end = min(start + chunk_seconds, duration_seconds)
        chunks.append((start, end))
        start = end
    return chunks


def find_active_windows(
    motion_series: Sequence[Tuple[float, float]],
    motion_threshold: float = MOTION_THRESHOLD,
    min_window_secs: float = ACTIVE_MIN_SECS,
    merge_gap_secs: float = WINDOW_MERGE_GAP,
) -> List[Tuple[float, float]]:
    raw: List[Tuple[float, float]] = []
    start = None
    for t, motion in motion_series:
        if motion >= motion_threshold and start is None:
            start = t
        if motion < motion_threshold and start is not None:
            if t - start >= min_window_secs:
                raw.append((start, t))
            start = None
    if start is not None and motion_series and motion_series[-1][0] - start >= min_window_secs:
        raw.append((start, motion_series[-1][0]))

    if not raw:
        return []
    merged = [raw[0]]
    for s, e in raw[1:]:
        ms, me = merged[-1]
        if s - me <= merge_gap_secs:
            merged[-1] = (ms, max(me, e))
        else:
            merged.append((s, e))
    return merged


def make_subclips(window_start: float, window_end: float, duration: int = SUBCLIP_DURATION, overlap: int = SUBCLIP_OVERLAP) -> List[Tuple[float, float]]:
    if window_end <= window_start:
        return []
    stride = max(1, duration - overlap)
    clips: List[Tuple[float, float]] = []
    current = window_start
    while current < window_end:
        end = min(current + duration, window_end)
        clips.append((current, end))
        if end >= window_end:
            break
        current += stride
    return clips


def window_motion_stats(window: Tuple[float, float], motion_series: Sequence[Tuple[float, float]]) -> Dict[str, float]:
    s, e = window
    values = [m for t, m in motion_series if s <= t <= e]
    if not values:
        return {"peak_motion": 0.0, "mean_motion": 0.0}
    return {"peak_motion": max(values), "mean_motion": sum(values) / len(values)}


def extract_caption_threats(caption: str) -> List[str]:
    text = caption.lower()
    tags = {label for key, label in CAPTION_KEYWORDS.items() if re.search(rf"\b{re.escape(key)}\b", text)}
    return sorted(tags)


def is_after_hours(timestamp: datetime) -> bool:
    hour = timestamp.hour
    return hour >= AFTER_HOURS_START or hour < AFTER_HOURS_END


def label_from_signals(signals: Dict[str, float], caption_tags: Iterable[str]) -> Tuple[str, float, Dict[str, float]]:
    tags = set(caption_tags)
    score_map: Dict[str, float] = {"activity_detected": 0.2}
    score_map["physical_altercation"] = signals.get("contact_score", 0.0) * 0.8 + (0.2 if "physical_altercation" in tags else 0.0)
    score_map["aggressive_behavior"] = signals.get("contact_score", 0.0) * 0.5 + signals.get("peak_motion", 0.0) * 0.4 + (0.2 if "aggressive_behavior" in tags else 0.0)
    score_map["weapon_detected"] = 0.95 if "weapon_detected" in tags else 0.0
    score_map["medical_emergency"] = 0.92 if "medical_emergency" in tags else 0.0
    score_map["person_fallen"] = signals.get("peak_motion", 0.0) * 0.3 + (0.6 if "person_fallen" in tags else 0.0)
    score_map["person_in_distress"] = 0.5 if "person_in_distress" in tags else 0.1
    score_map["intruder_detected"] = 0.6 if "intruder_detected" in tags else 0.0
    score_map["after_hours_activity"] = 0.55 if signals.get("after_hours", 0) else 0.0
    score_map["handshake"] = 0.85 if "handshake" in tags else 0.0
    score_map["hug"] = 0.85 if "hug" in tags else 0.0
    score_map["helping_gesture"] = 0.75 if "helping_gesture" in tags else 0.0

    label, confidence = max(score_map.items(), key=lambda item: item[1])
    return label, float(min(1.0, confidence)), score_map


def compute_alert_score(label: str, signals: Dict[str, float], caption_tags: Sequence[str]) -> Tuple[float, str, str]:
    threats = len(set(caption_tags) & (HIGH_LABELS | CRITICAL_LABELS | {"aggressive_behavior"}))
    raw = (
        WEIGHTS["contact_score"] * min(1.0, signals.get("contact_score", 0.0))
        + WEIGHTS["motion"] * min(1.0, signals.get("peak_motion", 0.0))
        + WEIGHTS["people"] * min(1.0, signals.get("people_count", 0) / 4.0)
        + WEIGHTS["vehicles"] * min(1.0, signals.get("vehicle_count", 0) / 2.0)
        + WEIGHTS["after_hours"] * (1.0 if signals.get("after_hours", 0) else 0.0)
        + WEIGHTS["threats"] * min(1.0, threats / 2.0)
    )

    if label in SAFE_LABELS:
        raw = min(raw, ALERT_B_THRESHOLD - 0.01)
    if label in HIGH_LABELS:
        raw = max(raw, 0.52)
    if label in CRITICAL_LABELS:
        raw = max(raw, 0.76)

    if raw >= ALERT_C_THRESHOLD:
        return round(raw, 3), "C", "critical threshold reached"
    if raw >= ALERT_B_THRESHOLD:
        return round(raw, 3), "B", "weighted evidence threshold reached"
    stage_a = signals.get("contact_score", 0.0) >= 0.35 or signals.get("after_hours", 0) or threats > 0
    return round(raw, 3), ("A" if stage_a else "none"), ("rule trigger" if stage_a else "insufficient evidence")
