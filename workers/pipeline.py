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

DOMAIN_LABELS: Dict[str, List[str]] = {
    "human_safety": [
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
    ],
    "dog_safety": [
        "dog_playing",
        "dog_aggression",
        "dog_fight",
        "dog_injury_risk",
        "dog_in_distress",
        "dog_leash_incident",
        "dog_left_in_hot_area",
    ],
    "antitheft": [
        "theft_suspected",
        "shoplifting_suspected",
        "package_theft",
        "vehicle_break_in",
        "snatch_and_run",
        "tampering_detected",
        "suspicious_loitering",
    ],
}

LABELS = [label for group in DOMAIN_LABELS.values() for label in group] + ["activity_detected"]

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
    "dog_playing": "low",
    "dog_aggression": "medium",
    "dog_fight": "high",
    "dog_injury_risk": "high",
    "dog_in_distress": "high",
    "dog_leash_incident": "medium",
    "dog_left_in_hot_area": "critical",
    "theft_suspected": "high",
    "shoplifting_suspected": "high",
    "package_theft": "high",
    "vehicle_break_in": "critical",
    "snatch_and_run": "high",
    "tampering_detected": "medium",
    "suspicious_loitering": "medium",
    "activity_detected": "low",
}

CAPTION_KEYWORDS: Dict[str, str] = {
    # Human safety keywords
    "handshake": "handshake",
    "shake hands": "handshake",
    "hug": "hug",
    "embrace": "hug",
    "help": "helping_gesture",
    "assist": "helping_gesture",
    "supporting": "helping_gesture",
    "fight": "physical_altercation",
    "brawl": "physical_altercation",
    "punch": "aggressive_behavior",
    "kick": "aggressive_behavior",
    "attack": "aggressive_behavior",
    "weapon": "weapon_detected",
    "gun": "weapon_detected",
    "knife": "weapon_detected",
    "bat": "weapon_detected",
    "fall": "person_fallen",
    "fainted": "medical_emergency",
    "collapsed": "medical_emergency",
    "medical": "medical_emergency",
    "injured": "person_in_distress",
    "distress": "person_in_distress",
    "screaming": "person_in_distress",
    "intruder": "intruder_detected",
    "trespass": "intruder_detected",
    "unauthorized": "intruder_detected",
    # Dog safety keywords
    "dog": "dog_playing",
    "puppy": "dog_playing",
    "wagging": "dog_playing",
    "dog fight": "dog_fight",
    "dogs fighting": "dog_fight",
    "dog biting": "dog_aggression",
    "growling": "dog_aggression",
    "snarling": "dog_aggression",
    "dog limping": "dog_injury_risk",
    "dog injured": "dog_injury_risk",
    "dog trapped": "dog_in_distress",
    "dog crying": "dog_in_distress",
    "dog yelping": "dog_in_distress",
    "leash tangled": "dog_leash_incident",
    "leash choke": "dog_leash_incident",
    "dog in car": "dog_left_in_hot_area",
    "hot car": "dog_left_in_hot_area",
    # Anti-theft keywords
    "theft": "theft_suspected",
    "steal": "theft_suspected",
    "stealing": "theft_suspected",
    "shoplifting": "shoplifting_suspected",
    "concealing item": "shoplifting_suspected",
    "package theft": "package_theft",
    "porch pirate": "package_theft",
    "break in": "vehicle_break_in",
    "window smash": "vehicle_break_in",
    "snatch": "snatch_and_run",
    "grab and run": "snatch_and_run",
    "tampering": "tampering_detected",
    "lock picking": "tampering_detected",
    "loitering": "suspicious_loitering",
    "casing": "suspicious_loitering",
}

WEIGHTS = {
    "contact_score": 0.28,
    "motion": 0.18,
    "people": 0.12,
    "dog_count": 0.10,
    "vehicles": 0.08,
    "after_hours": 0.09,
    "threats": 0.15,
}

SAFE_LABELS = {"handshake", "hug", "helping_gesture", "dog_playing"}
HIGH_LABELS = {
    "physical_altercation",
    "person_fallen",
    "intruder_detected",
    "dog_fight",
    "dog_injury_risk",
    "dog_in_distress",
    "theft_suspected",
    "package_theft",
    "snatch_and_run",
    "shoplifting_suspected",
}
CRITICAL_LABELS = {"weapon_detected", "medical_emergency", "vehicle_break_in", "dog_left_in_hot_area"}


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


def infer_domain(signals: Dict[str, float], caption_tags: Iterable[str]) -> str:
    tags = set(caption_tags)
    if signals.get("dog_count", 0) > 0 or any(tag in DOMAIN_LABELS["dog_safety"] for tag in tags):
        return "dog_safety"
    if any(tag in DOMAIN_LABELS["antitheft"] for tag in tags):
        return "antitheft"
    return "human_safety"


def label_from_signals(signals: Dict[str, float], caption_tags: Iterable[str]) -> Tuple[str, float, Dict[str, float]]:
    tags = set(caption_tags)
    domain = infer_domain(signals, tags)
    score_map: Dict[str, float] = {"activity_detected": 0.2}

    # Human safety scoring
    score_map["physical_altercation"] = signals.get("contact_score", 0.0) * 0.8 + (0.2 if "physical_altercation" in tags else 0.0)
    score_map["aggressive_behavior"] = signals.get("contact_score", 0.0) * 0.5 + signals.get("peak_motion", 0.0) * 0.4 + (0.2 if "aggressive_behavior" in tags else 0.0)
    score_map["weapon_detected"] = 0.95 if "weapon_detected" in tags else 0.0
    score_map["medical_emergency"] = 0.92 if "medical_emergency" in tags else 0.0
    score_map["person_fallen"] = signals.get("peak_motion", 0.0) * 0.3 + (0.6 if "person_fallen" in tags else 0.0)
    score_map["person_in_distress"] = 0.55 if "person_in_distress" in tags else 0.1
    score_map["intruder_detected"] = 0.65 if "intruder_detected" in tags else 0.0
    score_map["after_hours_activity"] = 0.58 if signals.get("after_hours", 0) else 0.0
    score_map["handshake"] = 0.85 if "handshake" in tags else 0.0
    score_map["hug"] = 0.85 if "hug" in tags else 0.0
    score_map["helping_gesture"] = 0.75 if "helping_gesture" in tags else 0.0

    # Dog safety scoring
    score_map["dog_playing"] = 0.55 if "dog_playing" in tags else 0.0
    score_map["dog_aggression"] = signals.get("contact_score", 0.0) * 0.45 + (0.35 if "dog_aggression" in tags else 0.0)
    score_map["dog_fight"] = signals.get("contact_score", 0.0) * 0.65 + signals.get("peak_motion", 0.0) * 0.2 + (0.3 if "dog_fight" in tags else 0.0)
    score_map["dog_injury_risk"] = (0.65 if "dog_injury_risk" in tags else 0.0) + (0.2 if signals.get("peak_motion", 0.0) > 0.4 else 0.0)
    score_map["dog_in_distress"] = 0.72 if "dog_in_distress" in tags else 0.0
    score_map["dog_leash_incident"] = 0.6 if "dog_leash_incident" in tags else 0.0
    score_map["dog_left_in_hot_area"] = 0.95 if "dog_left_in_hot_area" in tags else 0.0

    # Anti-theft scoring
    score_map["theft_suspected"] = 0.7 if "theft_suspected" in tags else 0.0
    score_map["shoplifting_suspected"] = 0.8 if "shoplifting_suspected" in tags else 0.0
    score_map["package_theft"] = 0.82 if "package_theft" in tags else 0.0
    score_map["vehicle_break_in"] = 0.95 if "vehicle_break_in" in tags else 0.0
    score_map["snatch_and_run"] = 0.78 if "snatch_and_run" in tags else 0.0
    score_map["tampering_detected"] = 0.62 if "tampering_detected" in tags else 0.0
    score_map["suspicious_loitering"] = 0.58 if "suspicious_loitering" in tags else 0.0

    # Bias to detected domain
    for label in DOMAIN_LABELS.get(domain, []):
        score_map[label] *= 1.08

    label, confidence = max(score_map.items(), key=lambda item: item[1])
    return label, float(min(1.0, confidence)), score_map


def compute_alert_score(label: str, signals: Dict[str, float], caption_tags: Sequence[str]) -> Tuple[float, str, str]:
    threats = len(set(caption_tags) & (HIGH_LABELS | CRITICAL_LABELS | {"aggressive_behavior", "dog_aggression"}))
    raw = (
        WEIGHTS["contact_score"] * min(1.0, signals.get("contact_score", 0.0))
        + WEIGHTS["motion"] * min(1.0, signals.get("peak_motion", 0.0))
        + WEIGHTS["people"] * min(1.0, signals.get("people_count", 0) / 4.0)
        + WEIGHTS["dog_count"] * min(1.0, signals.get("dog_count", 0) / 3.0)
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
