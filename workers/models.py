from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List


@dataclass
class TimeWindow:
    start_ms: int
    end_ms: int
    duration_ms: int
    first_detection_ms: int
    last_detection_ms: int


@dataclass
class DetectionSummary:
    people_count: int
    vehicle_count: int
    peak_motion: float
    mean_motion: float
    contact_score: float
    objects: List[str] = field(default_factory=list)


@dataclass
class AlertSummary:
    score: float
    stage: str
    reason: str


@dataclass
class EventSummary:
    label: str
    confidence: float


@dataclass
class EventJSON:
    clip_id: str
    video_source: str
    chunk_index: int
    window_index: int
    time: TimeWindow
    start: float
    end: float
    duration: float
    quality_score: float
    detections: DetectionSummary
    tracks: List[Dict[str, Any]]
    track_count: int
    event: EventSummary
    evidence: Dict[str, Any]
    caption: str
    tags: List[str]
    alert: AlertSummary
    _clip_embedding: List[float] = field(default_factory=list)
    _track_trajectories: List[Dict[str, Any]] = field(default_factory=list)
    processed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    processing_gpu: str = "A100"

    def to_dict(self, strip_heavy: bool = False) -> Dict[str, Any]:
        payload = asdict(self)
        if strip_heavy:
            payload.pop("_clip_embedding", None)
            payload.pop("_track_trajectories", None)
        return payload
