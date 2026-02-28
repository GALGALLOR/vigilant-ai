"""
Vigilant-AI — Pipeline Helpers
Pure-Python utilities (no Modal, no GPU deps) for:
  - Active window detection from motion scores
  - IoU / contact scoring
  - Signal-based event labeling (multi-hypothesis)
  - Caption threat keyword extraction
  - Alert scoring (Stage A + B)
"""
from __future__ import annotations

from typing import List, Dict, Tuple, Any
import re

# ─── Constants ─────────────────────────────────────────────────────────────────
MOTION_THRESHOLD  = 0.05    # fraction of changed pixels to count as motion
ACTIVE_MIN_SECS   = 1.5     # minimum window length to keep
WINDOW_MERGE_GAP  = 5.0     # merge windows within this gap (seconds)
MOTION_SAMPLE_FPS = 2       # frames-per-second we sample for motion scoring

AFTER_HOURS_START = 22      # 10 PM
AFTER_HOURS_END   = 6       # 6 AM

ALERT_B_THRESHOLD = 0.45    # stage B: numeric score
ALERT_C_THRESHOLD = 0.70    # stage C: LLM verification

SUBCLIP_DURATION  = 10      # seconds per sub-clip sent to GPU
SUBCLIP_OVERLAP   = 2       # seconds of overlap between consecutive sub-clips
SUBCLIP_STRIDE    = SUBCLIP_DURATION - SUBCLIP_OVERLAP  # = 8 s

# Evidence weights for Stage-B scoring
EVIDENCE_WEIGHTS = {
    "motion":        0.20,
    "overlap":       0.35,   # contact/overlap score is the strongest signal
    "dwell_norm":    0.20,   # dwell_seconds / 60, capped at 1
    "people_norm":   0.15,   # people_count / 4, capped at 1
    "after_hours":   0.10,
}

# Keyword → tag mapping for caption parsing
CAPTION_KEYWORDS = {
    "run": "running", "sprint": "running",
    "fight": "fighting", "attack": "fighting", "hit": "fighting",
    "fall": "fallen", "fell": "fallen", "collapse": "fallen",
    "jump": "jumping",
    "enter": "entry", "exit": "exit", "leave": "exit",
    "crowd": "crowd", "group": "crowd",
    "loiter": "loitering", "wait": "loitering",
    "vehicle": "vehicle", "car": "vehicle", "truck": "vehicle",
}


# ─── Expanded Event Taxonomy (21+ types across 7+ categories) ─────────────────

# Canonical taxonomy: category -> list of event labels.
EVENT_TAXONOMY: Dict[str, List[str]] = {
    "violence": [
        "physical_altercation",
        "aggressive_behavior",
        "weapon_detected",
    ],
    "falls_medical": [
        "person_fallen",
        "medical_emergency",
    ],
    "intrusion": [
        "trespassing",
        "perimeter_breach",
        "tailgating",
    ],
    "suspicious": [
        "loitering",
        "erratic_movement",
        "surveillance_behavior",
        "abandoned_object",
    ],
    "crowd": [
        "crowd_gathering",
        "crowd_surge",
        "stampede_risk",
        "confrontation",
    ],
    "vehicle": [
        "vehicle_incident",
        "reckless_driving",
        "vehicle_intrusion",
    ],
    "running": [
        "person_running",
        "pursuit",
        "fleeing_scene",
    ],
    "environmental": [
        "fire_smoke_detected",
        "vandalism",
        "property_damage",
    ],
}

# Severity tiers: critical/high/medium/low
EVENT_SEVERITY: Dict[str, str] = {
    # Violence
    "weapon_detected": "critical",
    "physical_altercation": "high",
    "aggressive_behavior": "medium",

    # Falls/Medical
    "medical_emergency": "critical",
    "person_fallen": "high",

    # Intrusion
    "perimeter_breach": "high",
    "trespassing": "medium",
    "tailgating": "medium",

    # Suspicious
    "abandoned_object": "high",
    "surveillance_behavior": "medium",
    "erratic_movement": "medium",
    "loitering": "low",

    # Crowd
    "stampede_risk": "critical",
    "crowd_surge": "high",
    "confrontation": "high",
    "crowd_gathering": "medium",

    # Vehicle
    "vehicle_incident": "high",
    "reckless_driving": "high",
    "vehicle_intrusion": "high",

    # Running
    "pursuit": "high",
    "fleeing_scene": "high",
    "person_running": "medium",

    # Environmental
    "fire_smoke_detected": "critical",
    "property_damage": "high",
    "vandalism": "medium",

    # Legacy / generic
    "after_hours_activity": "medium",
    "activity_detected": "low",
    "processing_error": "low",
}

SEVERITY_MULTIPLIERS: Dict[str, float] = {
    "critical": 1.35,
    "high": 1.20,
    "medium": 1.08,
    "low": 1.00,
}

_SEVERITY_RANK: Dict[str, int] = {"low": 0, "medium": 1, "high": 2, "critical": 3}


# ─── Threat Keywords (caption → category, base_weight) ────────────────────────
# Categories: violence, weapon, fall, medical, running, pursuit, fire, vandalism,
#             intrusion, suspicious, crowd, vehicle, abandonment

THREAT_KEYWORDS: Dict[str, Tuple[str, float]] = {
    # violence
    "fight": ("violence", 0.85),
    "fighting": ("violence", 0.90),
    "brawl": ("violence", 0.90),
    "altercation": ("violence", 0.70),
    "assault": ("violence", 0.90),
    "attack": ("violence", 0.85),
    "attacking": ("violence", 0.90),
    "hit": ("violence", 0.60),
    "hitting": ("violence", 0.70),
    "punch": ("violence", 0.80),
    "punching": ("violence", 0.85),
    "kick": ("violence", 0.70),
    "kicking": ("violence", 0.75),
    "beat": ("violence", 0.80),
    "beating": ("violence", 0.85),
    "choke": ("violence", 0.90),
    "choking": ("violence", 0.95),
    "strangle": ("violence", 0.95),
    "strangling": ("violence", 1.00),
    "stab": ("violence", 0.95),
    "stabbing": ("violence", 1.00),
    "shoot": ("violence", 1.00),
    "shooting": ("violence", 1.00),
    "gunfire": ("violence", 1.00),
    "wrestle": ("violence", 0.60),
    "wrestling": ("violence", 0.65),
    "grapple": ("violence", 0.65),
    "grappling": ("violence", 0.70),
    "drag": ("violence", 0.70),
    "dragging": ("violence", 0.75),
    "threat": ("violence", 0.55),
    "threatening": ("violence", 0.65),
    "violent": ("violence", 0.60),
    "aggressive": ("violence", 0.55),
    "argue": ("violence", 0.35),
    "arguing": ("violence", 0.40),
    "argument": ("violence", 0.40),
    "confrontation": ("violence", 0.55),
    "harass": ("violence", 0.55),
    "harassing": ("violence", 0.60),
    "harassment": ("violence", 0.60),
    "bully": ("violence", 0.50),
    "bullying": ("violence", 0.55),
    "mugging": ("violence", 0.85),
    "robbery": ("violence", 0.95),
    "riot": ("violence", 0.80),

    # weapon
    "weapon": ("weapon", 0.90),
    "gun": ("weapon", 1.00),
    "handgun": ("weapon", 1.00),
    "pistol": ("weapon", 1.00),
    "rifle": ("weapon", 1.00),
    "shotgun": ("weapon", 1.00),
    "firearm": ("weapon", 1.00),
    "knife": ("weapon", 0.95),
    "blade": ("weapon", 0.85),
    "machete": ("weapon", 1.00),
    "sword": ("weapon", 0.90),
    "baseball bat": ("weapon", 0.80),
    "bat": ("weapon", 0.60),
    "club": ("weapon", 0.70),
    "crowbar": ("weapon", 0.80),
    "hammer": ("weapon", 0.75),
    "brick": ("weapon", 0.70),
    "bottle": ("weapon", 0.55),
    "pipe": ("weapon", 0.65),
    "taser": ("weapon", 0.85),
    "pepper spray": ("weapon", 0.70),
    "explosive": ("weapon", 1.00),
    "bomb": ("weapon", 1.00),
    "grenade": ("weapon", 1.00),
    "molotov": ("weapon", 1.00),
    "ammunition": ("weapon", 0.90),
    "magazine": ("weapon", 0.60),

    # fall
    "fall": ("fall", 0.75),
    "fell": ("fall", 0.75),
    "fallen": ("fall", 0.80),
    "collapse": ("fall", 0.85),
    "collapsed": ("fall", 0.85),
    "trip": ("fall", 0.60),
    "tripped": ("fall", 0.65),
    "slip": ("fall", 0.60),
    "slipped": ("fall", 0.65),
    "stumble": ("fall", 0.55),
    "stumbled": ("fall", 0.60),
    "faint": ("fall", 0.80),
    "fainted": ("fall", 0.85),
    "unconscious": ("fall", 0.90),
    "passed out": ("fall", 0.90),
    "lying on the ground": ("fall", 0.85),
    "on the ground": ("fall", 0.60),

    # medical
    "medical": ("medical", 0.60),
    "emergency": ("medical", 0.60),
    "ambulance": ("medical", 0.95),
    "paramedic": ("medical", 0.90),
    "cpr": ("medical", 1.00),
    "resuscitation": ("medical", 1.00),
    "heart attack": ("medical", 1.00),
    "stroke": ("medical", 0.95),
    "seizure": ("medical", 0.95),
    "overdose": ("medical", 1.00),
    "bleeding": ("medical", 0.90),
    "blood": ("medical", 0.75),
    "wound": ("medical", 0.70),
    "injury": ("medical", 0.65),
    "injured": ("medical", 0.70),
    "help": ("medical", 0.40),
    "call 911": ("medical", 0.95),
    "distress": ("medical", 0.60),

    # running
    "run": ("running", 0.55),
    "running": ("running", 0.60),
    "sprint": ("running", 0.70),
    "sprinting": ("running", 0.75),
    "dash": ("running", 0.65),
    "dashing": ("running", 0.70),
    "jog": ("running", 0.35),
    "jogging": ("running", 0.40),
    "bolting": ("running", 0.75),
    "rush": ("running", 0.45),
    "rushing": ("running", 0.50),

    # pursuit
    "chase": ("pursuit", 0.80),
    "chasing": ("pursuit", 0.85),
    "pursuit": ("pursuit", 0.90),
    "pursue": ("pursuit", 0.85),
    "pursuing": ("pursuit", 0.90),
    "follow": ("pursuit", 0.45),
    "following": ("pursuit", 0.50),
    "escape": ("pursuit", 0.70),
    "escaping": ("pursuit", 0.75),
    "flee": ("pursuit", 0.80),
    "fleeing": ("pursuit", 0.85),
    "fled": ("pursuit", 0.85),
    "caught": ("pursuit", 0.55),

    # fire
    "fire": ("fire", 0.90),
    "flame": ("fire", 0.90),
    "flames": ("fire", 0.95),
    "smoke": ("fire", 0.90),
    "smoky": ("fire", 0.80),
    "burn": ("fire", 0.70),
    "burning": ("fire", 0.85),
    "explosion": ("fire", 1.00),
    "sparks": ("fire", 0.65),
    "gas leak": ("fire", 0.95),
    "electrical fire": ("fire", 1.00),
    "blaze": ("fire", 0.95),

    # vandalism / property
    "vandalism": ("vandalism", 0.80),
    "graffiti": ("vandalism", 0.70),
    "spray paint": ("vandalism", 0.65),
    "tagging": ("vandalism", 0.65),
    "deface": ("vandalism", 0.70),
    "defacing": ("vandalism", 0.75),
    "smash": ("vandalism", 0.75),
    "smashing": ("vandalism", 0.80),
    "break": ("vandalism", 0.55),
    "breaking": ("vandalism", 0.65),
    "broken": ("vandalism", 0.55),
    "damage": ("vandalism", 0.60),
    "damaging": ("vandalism", 0.65),
    "destroy": ("vandalism", 0.75),
    "destroying": ("vandalism", 0.80),
    "property damage": ("vandalism", 0.80),
    "broken window": ("vandalism", 0.80),
    "breaking window": ("vandalism", 0.90),

    # intrusion
    "trespass": ("intrusion", 0.75),
    "trespassing": ("intrusion", 0.80),
    "intruder": ("intrusion", 0.85),
    "intrusion": ("intrusion", 0.85),
    "unauthorized": ("intrusion", 0.75),
    "restricted": ("intrusion", 0.70),
    "no entry": ("intrusion", 0.80),
    "private property": ("intrusion", 0.70),
    "break in": ("intrusion", 0.85),
    "break-in": ("intrusion", 0.85),
    "forced entry": ("intrusion", 0.95),
    "climb fence": ("intrusion", 0.90),
    "climbing": ("intrusion", 0.60),
    "jump fence": ("intrusion", 0.90),
    "breach": ("intrusion", 0.80),
    "perimeter": ("intrusion", 0.70),
    "gate": ("intrusion", 0.55),
    "tailgating": ("intrusion", 0.70),
    "sneak": ("intrusion", 0.65),
    "sneaking": ("intrusion", 0.70),

    # suspicious
    "loiter": ("suspicious", 0.55),
    "loitering": ("suspicious", 0.65),
    "lurking": ("suspicious", 0.70),
    "suspicious": ("suspicious", 0.60),
    "looking around": ("suspicious", 0.60),
    "scoping": ("suspicious", 0.65),
    "casing": ("suspicious", 0.70),
    "surveillance": ("suspicious", 0.75),
    "watching": ("suspicious", 0.55),
    "stalking": ("suspicious", 0.85),
    "hiding": ("suspicious", 0.65),
    "masked": ("suspicious", 0.70),
    "mask": ("suspicious", 0.55),
    "hooded": ("suspicious", 0.60),
    "hood": ("suspicious", 0.45),
    "gloves": ("suspicious", 0.45),

    # crowd
    "crowd": ("crowd", 0.55),
    "crowded": ("crowd", 0.60),
    "group": ("crowd", 0.45),
    "gathering": ("crowd", 0.50),
    "mob": ("crowd", 0.75),
    "stampede": ("crowd", 1.00),
    "panic": ("crowd", 0.80),
    "surge": ("crowd", 0.75),
    "pushing": ("crowd", 0.65),
    "trampling": ("crowd", 1.00),
    "riot": ("crowd", 0.80),

    # vehicle
    "vehicle": ("vehicle", 0.40),
    "car": ("vehicle", 0.40),
    "truck": ("vehicle", 0.45),
    "bus": ("vehicle", 0.45),
    "van": ("vehicle", 0.45),
    "motorcycle": ("vehicle", 0.45),
    "scooter": ("vehicle", 0.35),
    "bicycle": ("vehicle", 0.25),
    "crash": ("vehicle", 0.85),
    "collision": ("vehicle", 0.90),
    "accident": ("vehicle", 0.80),
    "hit and run": ("vehicle", 1.00),
    "speeding": ("vehicle", 0.80),
    "reckless": ("vehicle", 0.75),
    "drifting": ("vehicle", 0.70),
    "burnout": ("vehicle", 0.65),
    "wrong way": ("vehicle", 0.85),
    "ramming": ("vehicle", 1.00),

    # abandonment
    "abandoned": ("abandonment", 0.80),
    "unattended": ("abandonment", 0.80),
    "left behind": ("abandonment", 0.85),
    "suspicious package": ("abandonment", 1.00),
    "package": ("abandonment", 0.45),
    "package left": ("abandonment", 0.90),
    "bag": ("abandonment", 0.40),
    "bag left": ("abandonment", 0.90),
    "backpack": ("abandonment", 0.50),
    "backpack left": ("abandonment", 0.95),
    "suitcase": ("abandonment", 0.55),
    "briefcase": ("abandonment", 0.55),
    "object left": ("abandonment", 0.85),
    "unclaimed": ("abandonment", 0.80),
    "dumped": ("abandonment", 0.70),
    "discarded": ("abandonment", 0.60),
}


# Precompiled regex patterns for efficient matching.
# - For single words, use word boundaries.
# - For multi-word phrases, match on whitespace-normalized caption.
_THREAT_PATTERNS: List[Tuple[str, str, float, re.Pattern[str]]] = []
for _kw, (_cat, _w) in THREAT_KEYWORDS.items():
    if not _kw:
        continue
    if any(ch.isspace() for ch in _kw) or "-" in _kw:
        # Normalize hyphenated keywords to space in the caption preprocessor.
        pat = re.compile(r"(?<!\w)" + re.escape(_kw) + r"(?!\w)")
    else:
        pat = re.compile(r"\b" + re.escape(_kw) + r"\b")
    _THREAT_PATTERNS.append((_kw, _cat, float(_w), pat))


def extract_caption_threats(caption: str) -> List[Dict[str, Any]]:
    """
    Extract threat-related keywords from a free-form caption.

    Returns a list of:
      {"keyword": <matched keyword>, "category": <category>, "weight": <base_weight>}

    Notes:
      - Matching is case-insensitive.
      - Keyword weights are *base* weights; downstream scoring may scale them.
    """
    if not caption:
        return []

    # Lowercase + light normalization so multi-word phrases have a chance.
    # Keep spaces; remove most punctuation to reduce false negatives.
    cap = caption.lower()
    cap = cap.replace("_", " ").replace("-", " ")
    cap = re.sub(r"[^a-z0-9\s]", " ", cap)
    cap = re.sub(r"\s+", " ", cap).strip()

    found: Dict[str, Dict[str, Any]] = {}
    for kw, cat, w, pat in _THREAT_PATTERNS:
        if pat.search(cap) is not None:
            found[kw] = {"keyword": kw, "category": cat, "weight": float(w)}

    # Sort higher weight first for downstream convenience.
    return sorted(found.values(), key=lambda d: float(d.get("weight", 0.0)), reverse=True)


# ─── Video Chunking Helpers ───────────────────────────────────────────────────


def make_video_chunks(
    total_seconds: float,
    chunk_size: float = 300.0,
) -> List[Tuple[float, float]]:
    """
    Split a video of `total_seconds` into chunks of `chunk_size` seconds.
    The last chunk is whatever remains — handles non-multiples correctly.

    Example: 555s video, 300s chunks → [(0,300), (300,555)]
    """
    chunks: List[Tuple[float, float]] = []
    start = 0.0
    while start < total_seconds:
        end = min(start + chunk_size, total_seconds)
        chunks.append((round(start, 2), round(end, 2)))
        start = end
    return chunks



def make_subclips(
    win_start: float,
    win_end: float,
    duration: float = SUBCLIP_DURATION,
    overlap: float = SUBCLIP_OVERLAP,
) -> List[Tuple[float, float]]:
    """
    Slice an active window into fixed-length sub-clips with overlap.
    Stride = duration - overlap  (default: 10s clip, 2s overlap → 8s stride).

    The last sub-clip is extended to cover any remainder, up to `duration` long.
    This ensures no event is cut at a boundary.

    Example: window 45s–105s, duration=10, overlap=2
      → (45,55), (53,63), (61,71), (69,79), (77,87), (85,95), (93,103), (103,105)
    """
    stride   = duration - overlap
    subclips: List[Tuple[float, float]] = []
    start    = win_start

    while start < win_end:
        end = min(start + duration, win_end)
        subclips.append((round(start, 2), round(end, 2)))
        if end >= win_end:
            break
        start += stride

    return subclips




def find_active_windows(
    motion_scores: List[Tuple[float, float]],
) -> List[Tuple[float, float]]:
    """
    Given a list of (timestamp_sec, score) pairs, return merged active windows.
    Returns list of (start_sec, end_sec) tuples.
    """
    raw: List[Tuple[float, float]] = []
    in_window = False
    window_start = 0.0

    for ts, score in motion_scores:
        if not in_window and score > MOTION_THRESHOLD:
            in_window = True
            window_start = ts
        elif in_window and score <= MOTION_THRESHOLD:
            if ts - window_start >= ACTIVE_MIN_SECS:
                raw.append((window_start, ts))
            in_window = False

    if in_window and motion_scores:
        raw.append((window_start, motion_scores[-1][0]))

    # Merge nearby windows
    merged: List[Tuple[float, float]] = []
    for start, end in raw:
        if merged and start - merged[-1][1] < WINDOW_MERGE_GAP:
            merged[-1] = (merged[-1][0], end)
        else:
            merged.append((start, end))

    return merged



def window_motion_stats(
    motion_scores: List[Tuple[float, float]],
    win_start: float,
    win_end: float,
) -> Tuple[float, float]:
    """Return (peak_motion, mean_motion) for scores within a window."""
    vals = [s for ts, s in motion_scores if win_start <= ts <= win_end]
    if not vals:
        return 0.0, 0.0
    return float(max(vals)), float(sum(vals) / len(vals))



def is_after_hours(hour: int) -> bool:
    return hour >= AFTER_HOURS_START or hour < AFTER_HOURS_END



# ─── Geometry ─────────────────────────────────────────────────────────────────

def compute_iou(box1: List[float], box2: List[float]) -> float:
    """Intersection over Union for [x1, y1, x2, y2] boxes."""
    ix1 = max(box1[0], box2[0])
    iy1 = max(box1[1], box2[1])
    ix2 = min(box1[2], box2[2])
    iy2 = min(box1[3], box2[3])

    inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union = area1 + area2 - inter
    return inter / union if union > 0 else 0.0



def max_pairwise_iou(person_boxes: List[List[float]]) -> float:
    """Return max IoU among all pairs of person boxes in one frame."""
    best = 0.0
    for i in range(len(person_boxes)):
        for j in range(i + 1, len(person_boxes)):
            best = max(best, compute_iou(person_boxes[i], person_boxes[j]))
    return best



# ─── Signal-Based Event Labeling ──────────────────────────────────────────────

def _clamp01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return float(x)


def _severity_for_label(label: str) -> str:
    sev = EVENT_SEVERITY.get(label)
    if sev in _SEVERITY_RANK:
        return sev
    return "low"


def _highest_severity(events_list: List[Dict[str, Any]]) -> str:
    best = "low"
    best_rank = _SEVERITY_RANK[best]
    for ev in events_list or []:
        lab = str(ev.get("label", ""))
        sev = str(ev.get("severity") or _severity_for_label(lab))
        rank = _SEVERITY_RANK.get(sev, 0)
        if rank > best_rank:
            best, best_rank = sev, rank
    return best


def _add_hypothesis(
    acc: Dict[str, float],
    label: str,
    confidence: float,
) -> None:
    """Keep the max confidence per label."""
    c = _clamp01(float(confidence))
    if label not in acc or c > acc[label]:
        acc[label] = c


def label_from_signals(
    people_count: int,
    vehicle_count: int,
    contact_score: float,
    peak_motion: float,
    dwell_seconds: float,
    after_hours_flag: bool,
    caption: str,
) -> Tuple[List[Dict], List[str]]:
    """
    Rule-based multi-hypothesis classification from numeric signals + caption.

    Returns:
      (hypotheses_list, tags)

    Where hypotheses_list is sorted by confidence descending:
      [{"label": str, "confidence": float, "severity": str}, ...]

    Notes:
      - This function is intentionally conservative: it emits *all* matching
        hypotheses above a minimum confidence, rather than a single label.
      - Severity is attached per hypothesis using EVENT_SEVERITY.
    """
    # Normalize inputs
    people_count = int(people_count or 0)
    vehicle_count = int(vehicle_count or 0)
    contact_score = float(contact_score or 0.0)
    peak_motion = float(peak_motion or 0.0)
    dwell_seconds = float(dwell_seconds or 0.0)
    after_hours_flag = bool(after_hours_flag)

    caption_threats = extract_caption_threats(caption)
    threat_by_cat: Dict[str, float] = {}
    for t in caption_threats:
        cat = str(t.get("category", ""))
        w = float(t.get("weight", 0.0))
        threat_by_cat[cat] = threat_by_cat.get(cat, 0.0) + w

    motion_n = _clamp01(peak_motion / 0.6)          # motion is often < 0.6
    contact_n = _clamp01(contact_score / 0.25)      # iou contact rarely > 0.25
    dwell_n = _clamp01(dwell_seconds / 180.0)       # 3 minutes saturates
    people_n = _clamp01(people_count / 8.0)
    vehicle_n = _clamp01(vehicle_count / 3.0)

    acc: Dict[str, float] = {}
    tags: List[str] = []

    # Base tags from numeric signals
    if after_hours_flag:
        tags.append("after_hours")
    if vehicle_count >= 1:
        tags.append("vehicle")
    if people_count >= 4:
        tags.append("crowd")
    if contact_score > 0.10:
        tags.append("contact")
    if dwell_seconds >= 60:
        tags.append("dwell")

    # Tags from caption threats
    for cat in sorted(threat_by_cat.keys()):
        if cat:
            tags.append(cat)

    # ── Violence ─────────────────────────────────────────────────────────────
    weapon_strength = threat_by_cat.get("weapon", 0.0)
    violence_strength = threat_by_cat.get("violence", 0.0)

    if weapon_strength > 0.0:
        _add_hypothesis(
            acc,
            "weapon_detected",
            0.60 + min(weapon_strength, 2.0) * 0.18,
        )

    if people_count >= 2 and contact_score > 0.15:
        _add_hypothesis(
            acc,
            "physical_altercation",
            0.55 + 0.30 * contact_n + 0.10 * motion_n + 0.10 * min(violence_strength, 1.0),
        )

    if people_count >= 2 and (contact_score > 0.08 or violence_strength > 0.0) and peak_motion > 0.20:
        _add_hypothesis(
            acc,
            "aggressive_behavior",
            0.40 + 0.20 * contact_n + 0.20 * motion_n + 0.15 * min(violence_strength, 1.5),
        )

    # Crowd confrontation (also listed under crowd category)
    if people_count >= 3 and (contact_score > 0.12 or violence_strength > 0.0):
        _add_hypothesis(
            acc,
            "confrontation",
            0.45 + 0.25 * contact_n + 0.15 * people_n + 0.10 * min(violence_strength, 1.0),
        )

    # ── Falls / medical ───────────────────────────────────────────────────────
    fall_strength = threat_by_cat.get("fall", 0.0)
    medical_strength = threat_by_cat.get("medical", 0.0)

    if fall_strength > 0.0:
        _add_hypothesis(
            acc,
            "person_fallen",
            0.58 + min(fall_strength, 2.0) * 0.16 + 0.10 * motion_n,
        )

    if medical_strength > 0.0:
        _add_hypothesis(
            acc,
            "medical_emergency",
            0.62 + min(medical_strength, 2.0) * 0.18,
        )

    # ── Intrusion ────────────────────────────────────────────────────────────
    intrusion_strength = threat_by_cat.get("intrusion", 0.0)

    if after_hours_flag and people_count >= 1:
        _add_hypothesis(
            acc,
            "trespassing",
            0.50 + 0.15 * motion_n + 0.10 * people_n + 0.10 * min(intrusion_strength, 1.0),
        )

    # Perimeter breach: more specific than trespassing.
    if intrusion_strength > 0.8 or (after_hours_flag and peak_motion > 0.35 and people_count >= 1 and dwell_seconds < 25):
        _add_hypothesis(
            acc,
            "perimeter_breach",
            0.52 + 0.18 * motion_n + 0.15 * min(intrusion_strength, 1.5),
        )

    # Tailgating: multiple people, short dwell, and entry-like language.
    if people_count >= 2 and dwell_seconds < 25 and (intrusion_strength > 0.0 or after_hours_flag):
        _add_hypothesis(
            acc,
            "tailgating",
            0.42 + 0.10 * people_n + 0.10 * min(intrusion_strength, 1.0) + 0.05 * float(after_hours_flag),
        )

    # ── Suspicious behavior ───────────────────────────────────────────────────
    suspicious_strength = threat_by_cat.get("suspicious", 0.0)
    abandonment_strength = threat_by_cat.get("abandonment", 0.0)

    if dwell_seconds > 60.0:
        _add_hypothesis(
            acc,
            "loitering",
            0.40 + 0.30 * dwell_n + 0.05 * float(after_hours_flag) + 0.10 * min(suspicious_strength, 1.0),
        )

    # Erratic movement: high motion but low contact; often single subject.
    if peak_motion > 0.45 and contact_score < 0.05 and people_count >= 1:
        _add_hypothesis(
            acc,
            "erratic_movement",
            0.40 + 0.35 * motion_n + 0.10 * min(suspicious_strength, 1.0),
        )

    if suspicious_strength > 0.8 or (dwell_seconds > 20 and suspicious_strength > 0.0):
        _add_hypothesis(
            acc,
            "surveillance_behavior",
            0.42 + 0.18 * dwell_n + 0.18 * min(suspicious_strength, 1.5) + 0.05 * float(after_hours_flag),
        )

    if abandonment_strength > 0.0:
        _add_hypothesis(
            acc,
            "abandoned_object",
            0.55 + min(abandonment_strength, 2.0) * 0.18 + 0.05 * float(after_hours_flag),
        )

    # ── Crowd ────────────────────────────────────────────────────────────────
    crowd_strength = threat_by_cat.get("crowd", 0.0)

    if people_count >= 4:
        _add_hypothesis(
            acc,
            "crowd_gathering",
            0.42 + 0.25 * people_n + 0.10 * motion_n + 0.10 * min(crowd_strength, 1.0),
        )

    if people_count >= 6 and peak_motion > 0.40:
        _add_hypothesis(
            acc,
            "crowd_surge",
            0.52 + 0.20 * people_n + 0.20 * motion_n + 0.10 * min(crowd_strength, 1.0),
        )

    if people_count >= 8 and peak_motion > 0.55:
        _add_hypothesis(
            acc,
            "stampede_risk",
            0.62 + 0.20 * people_n + 0.20 * motion_n + 0.10 * min(crowd_strength, 1.0),
        )

    # ── Vehicle ──────────────────────────────────────────────────────────────
    vehicle_strength = threat_by_cat.get("vehicle", 0.0)

    if vehicle_count >= 1 and (vehicle_strength > 0.8 or peak_motion > 0.40):
        _add_hypothesis(
            acc,
            "vehicle_incident",
            0.48 + 0.22 * vehicle_n + 0.15 * motion_n + 0.10 * min(vehicle_strength, 1.5),
        )

    if vehicle_count >= 1 and (vehicle_strength > 1.2 or peak_motion > 0.55):
        _add_hypothesis(
            acc,
            "reckless_driving",
            0.52 + 0.22 * vehicle_n + 0.18 * motion_n + 0.08 * min(vehicle_strength, 1.5),
        )

    if vehicle_count >= 1 and after_hours_flag:
        _add_hypothesis(
            acc,
            "vehicle_intrusion",
            0.50 + 0.22 * vehicle_n + 0.05 * motion_n,
        )

    # ── Running / pursuit ────────────────────────────────────────────────────
    running_strength = threat_by_cat.get("running", 0.0)
    pursuit_strength = threat_by_cat.get("pursuit", 0.0)

    if running_strength > 0.0:
        _add_hypothesis(
            acc,
            "person_running",
            0.45 + min(running_strength, 2.0) * 0.15 + 0.15 * motion_n,
        )

    if pursuit_strength > 0.0:
        _add_hypothesis(
            acc,
            "pursuit",
            0.52 + min(pursuit_strength, 2.0) * 0.18 + 0.10 * min(people_n, 1.0),
        )

    if (pursuit_strength > 0.0 and running_strength > 0.0) or (running_strength > 1.2 and after_hours_flag):
        _add_hypothesis(
            acc,
            "fleeing_scene",
            0.55 + 0.10 * motion_n + 0.10 * min(pursuit_strength + running_strength, 2.0),
        )

    # ── Environmental ─────────────────────────────────────────────────────────
    fire_strength = threat_by_cat.get("fire", 0.0)
    vandal_strength = threat_by_cat.get("vandalism", 0.0)

    if fire_strength > 0.0:
        _add_hypothesis(
            acc,
            "fire_smoke_detected",
            0.65 + min(fire_strength, 2.0) * 0.18,
        )

    if vandal_strength > 0.0:
        _add_hypothesis(
            acc,
            "vandalism",
            0.48 + min(vandal_strength, 2.0) * 0.16,
        )
        if vandal_strength > 1.0:
            _add_hypothesis(
                acc,
                "property_damage",
                0.52 + min(vandal_strength, 2.0) * 0.16,
            )

    # ── Contextual / legacy labels ───────────────────────────────────────────
    if after_hours_flag and (people_count >= 1 or vehicle_count >= 1):
        _add_hypothesis(acc, "after_hours_activity", 0.50 + 0.10 * people_n + 0.10 * vehicle_n)

    # Always include a generic activity hypothesis.
    _add_hypothesis(acc, "activity_detected", 0.30 + 0.25 * motion_n + 0.10 * min(people_n + vehicle_n, 1.0))

    # Filter + assemble
    hypotheses: List[Dict[str, Any]] = []
    for label, conf in acc.items():
        # Keep low-confidence noise out, except activity_detected.
        if label != "activity_detected" and conf < 0.35:
            continue
        hypotheses.append(
            {
                "label": label,
                "confidence": round(_clamp01(conf), 3),
                "severity": _severity_for_label(label),
            }
        )

    hypotheses.sort(key=lambda d: float(d.get("confidence", 0.0)), reverse=True)

    # De-dupe tags, preserving insertion order
    seen = set()
    uniq_tags: List[str] = []
    for t in tags:
        if t and t not in seen:
            seen.add(t)
            uniq_tags.append(t)

    return hypotheses, uniq_tags



# ─── Alert Scoring ────────────────────────────────────────────────────────────

def compute_alert_score(
    evidence: Dict[str, float],
    after_hours_flag: bool,
    events_list: List[Dict] | None = None,
    caption_threats: List[Dict] | None = None,
) -> Tuple[float, str]:
    """
    Stage A + B alert scoring.

    Inputs:
      evidence: {
        "motion": float (0..1-ish),
        "overlap": float (0..1),
        "dwell_seconds": float,
        "people_count": float,
        "vehicle_count": float,
        ...
      }
      after_hours_flag: bool
      events_list: list of {"label": str, "confidence": float, "severity": str} dicts
      caption_threats: list from extract_caption_threats()

    Returns:
      (alert_score 0-1, alert_stage "none"|"A"|"B"|"C").

    Scoring changes (vs legacy):
      - Applies highest event severity multiplier (SEVERITY_MULTIPLIERS)
      - Applies caption threat boost: sum(weights) * 0.05, capped at 0.15
      - Stronger Stage-A rule gate
    """
    motion       = float(evidence.get("motion", 0.0) or 0.0)
    overlap      = float(evidence.get("overlap", 0.0) or 0.0)
    dwell        = float(evidence.get("dwell_seconds", 0.0) or 0.0)
    people       = float(evidence.get("people_count", 0.0) or 0.0)
    vehicles     = float(evidence.get("vehicle_count", 0.0) or 0.0)

    events_list = events_list or []
    caption_threats = caption_threats or []

    # ── Stage A — hard rules (expanded) ──────────────────────────────────────
    highest_sev = _highest_severity(events_list)
    any_high_sev = highest_sev in ("high", "critical")

    # Event-driven gate: if a high/critical hypothesis is reasonably confident.
    event_gate = False
    for ev in events_list:
        sev = str(ev.get("severity") or _severity_for_label(str(ev.get("label", ""))))
        conf = float(ev.get("confidence", 0.0) or 0.0)
        if sev in ("high", "critical") and conf >= 0.45:
            event_gate = True
            break

    threat_gate = False
    threat_weight_sum = 0.0
    for t in caption_threats:
        threat_weight_sum += float(t.get("weight", 0.0) or 0.0)
        if str(t.get("category", "")) in ("weapon", "fire", "medical", "violence") and float(t.get("weight", 0.0) or 0.0) >= 0.75:
            threat_gate = True

    stage_a = (
        # People/contact
        (people >= 2 and overlap >= 0.12)
        or (overlap >= 0.18)
        # Crowd
        or (people >= 5)
        # Loitering
        or (dwell >= 120)
        # After-hours presence
        or (after_hours_flag and (people >= 1 or vehicles >= 1))
        # Vehicle risk
        or (vehicles >= 1 and (motion >= 0.55 or after_hours_flag))
        # Caption-confirmed criticality
        or threat_gate
        # Model hypothesis criticality
        or event_gate
    )

    # ── Stage B — weighted numeric score ─────────────────────────────────────
    base_score = (
        EVIDENCE_WEIGHTS["motion"]      * motion
        + EVIDENCE_WEIGHTS["overlap"]   * overlap
        + EVIDENCE_WEIGHTS["dwell_norm"]  * min(dwell / 60.0, 1.0)
        + EVIDENCE_WEIGHTS["people_norm"] * min(people / 4.0, 1.0)
        + EVIDENCE_WEIGHTS["after_hours"] * float(after_hours_flag)
    )

    # Severity multiplier from highest-severity event
    sev_mult = float(SEVERITY_MULTIPLIERS.get(highest_sev, 1.0))

    # Caption threat boost
    caption_boost = min(float(threat_weight_sum) * 0.05, 0.15)

    score = base_score * sev_mult + caption_boost
    score = round(min(max(score, 0.0), 1.0), 3)

    if score >= ALERT_C_THRESHOLD:
        stage = "C"
    elif score >= ALERT_B_THRESHOLD:
        stage = "B"
    elif stage_a:
        stage = "A"
    else:
        stage = "none"

    return score, stage
