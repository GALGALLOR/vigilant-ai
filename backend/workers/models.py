"""
Vigilant-AI — Data Models
Dataclasses for the pipeline stages. Using plain dataclasses (not Pydantic)
so they work inside Modal containers without extra deps.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional


@dataclass
class WindowData:
    """
    One active window identified by the motion scorer.
    Passed from the CPU chunker to the GPU feature extractor.
    """
    chunk_index: int
    window_index: int
    video_source: str          # path relative to /data volume (e.g. "test.mp4")
    start_sec: float           # absolute seconds from video start
    end_sec: float
    peak_motion: float         # 0-1, fraction of changed pixels
    mean_motion: float         # 0-1
    quality_score: float       # 0-1, brightness + sharpness gate
    is_after_hours: bool       # True if window falls in 22:00-06:00

    @property
    def duration(self) -> float:
        return self.end_sec - self.start_sec

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TrackInfo:
    """Dwell + contact info for a single tracked person."""
    track_id: str
    dwell_seconds: float
    max_contact_score: float   # max IoU overlap with any other person track


@dataclass
class EventJSON:
    """
    Final structured output for one active window.
    Stored in DB + returned via API.
    """
    clip_id: str               # e.g. "c00_w003"
    video_source: str
    chunk_index: int
    window_index: int
    start: float
    end: float
    quality_score: float

    # Detection & tracking outputs
    people_count: int
    vehicle_count: int
    entities: List[Dict[str, Any]]    # [{"type":"person","count":2}, ...]
    tracks: List[Dict[str, Any]]      # [{"id":"p1","dwell_seconds":4.2}, ...]

    # Event semantics (from signal-based labeling)
    events: List[Dict[str, Any]]      # [{"label":"physical_contact","confidence":0.72}]
    evidence: Dict[str, float]        # {"motion":0.88,"overlap":0.81,"dwell_seconds":12.0,...}

    # Embedding for VectorDB
    clip_embedding: List[float]       # 768-dim CLIP ViT-L/14 vector

    # Human-readable outputs (Florence-2)
    caption: str
    tags: List[str]

    # Alert outputs
    alert_score: float                # 0-1 composite risk score
    alert_stage: str                  # "none" | "A" | "B" | "C"
    alert_reason: str

    # Metadata
    processed_at: str
    processing_gpu: str

    def to_dict(self) -> Dict:
        return asdict(self)
