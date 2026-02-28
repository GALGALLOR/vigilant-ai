from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import modal

from workers.models import AlertSummary, DetectionSummary, EventJSON, EventSummary, TimeWindow
from workers.pipeline import (
    CHUNK_SECONDS,
    MOTION_SAMPLE_FPS,
    QUALITY_THRESHOLD,
    compute_alert_score,
    extract_caption_threats,
    find_active_windows,
    is_after_hours,
    label_from_signals,
    make_subclips,
    make_video_chunks,
    thresholds,
    window_motion_stats,
)

APP_NAME = "vigilant-ai"
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

VIDEOS_VOLUME_NAME = "vigilant-videos"
WEIGHTS_VOLUME_NAME = "vigilant-model-weights"
MODEL_DIR = "/models"
YOLO_WEIGHTS_PATH = f"{MODEL_DIR}/yolo11l.pt"
CAPTION_MODEL = "Qwen/Qwen2-VL-7B-Instruct"
CLIP_MODEL = "openai/clip-vit-large-patch14"
GPU_TYPE = "A100"

app = modal.App(APP_NAME)

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg", "libgl1", "libglib2.0-0")
    .pip_install(
        "numpy",
        "opencv-python-headless",
        "pillow",
        "torch",
        "torchvision",
        "ultralytics",
        "transformers",
        "accelerate",
        "sentencepiece",
        "timm",
        "qwen-vl-utils",
        "huggingface_hub",
        "einops",
    )
    .env({"HF_HOME": MODEL_DIR, "TRANSFORMERS_CACHE": MODEL_DIR})
)

videos_volume = modal.Volume.from_name(VIDEOS_VOLUME_NAME, create_if_missing=True)
weights_volume = modal.Volume.from_name(WEIGHTS_VOLUME_NAME, create_if_missing=True)


def _load_video_duration_seconds(video_path: Path) -> float:
    import cv2

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise FileNotFoundError(f"Video not readable: {video_path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frames = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
    cap.release()
    return float(frames / max(1.0, fps))


def _scan_motion(video_path: Path, start: float, end: float) -> List[Tuple[float, float]]:
    import cv2
    import numpy as np

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return []

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    step = max(1, int(round(fps / MOTION_SAMPLE_FPS)))
    cap.set(cv2.CAP_PROP_POS_MSEC, start * 1000)
    t = start
    prev = None
    data: List[Tuple[float, float]] = []

    while t <= end:
        ok, frame = cap.read()
        if not ok or frame is None:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if prev is None:
            score = 0.0
        else:
            diff = cv2.absdiff(prev, gray)
            score = float(np.mean(diff > 25))
        data.append((t, score))
        prev = gray
        for _ in range(step - 1):
            cap.read()
        t += step / fps

    cap.release()
    return data


@app.function(image=image, volumes={"/videos": videos_volume})
def cpu_chunk_worker(video_rel_path: str, chunk_index: int, chunk_start: float, chunk_end: float) -> Dict[str, Any]:
    video_path = Path("/videos") / video_rel_path
    motion = _scan_motion(video_path, chunk_start, chunk_end)
    windows = find_active_windows(
        motion,
        motion_threshold=thresholds.motion_threshold,
        min_window_secs=thresholds.active_min_secs,
        merge_gap_secs=thresholds.merge_gap,
    )
    window_specs = []
    for idx, (ws, we) in enumerate(windows):
        stats = window_motion_stats((ws, we), motion)
        for ss, se in make_subclips(ws, we):
            window_specs.append(
                {
                    "chunk_index": chunk_index,
                    "window_index": idx,
                    "start": ss,
                    "end": se,
                    "window_start": ws,
                    "window_end": we,
                    **stats,
                }
            )
    return {"chunk_index": chunk_index, "windows": window_specs}


@app.cls(
    image=image,
    gpu=GPU_TYPE,
    volumes={"/videos": videos_volume, MODEL_DIR: weights_volume},
    timeout=60 * 30,
)
class FeatureExtractor:
    @modal.enter()
    def load_models(self):
        from transformers import CLIPModel, CLIPProcessor
        from ultralytics import YOLO

        self.yolo = YOLO(YOLO_WEIGHTS_PATH)
        self.clip_model = CLIPModel.from_pretrained(CLIP_MODEL)
        self.clip_processor = CLIPProcessor.from_pretrained(CLIP_MODEL)

    @modal.method()
    def infer_subclip(self, video_rel_path: str, spec: Dict[str, Any]) -> Dict[str, Any]:
        import cv2

        video_path = Path("/videos") / video_rel_path
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise FileNotFoundError(f"missing input video {video_path}")
        cap.set(cv2.CAP_PROP_POS_MSEC, spec["start"] * 1000)

        frames = []
        start_ms = int(spec["start"] * 1000)
        end_ms = int(spec["end"] * 1000)
        people_count = 0
        vehicle_count = 0
        dog_count = 0
        objects = set()
        object_freq: Dict[str, int] = {}
        person_boxes_by_frame: List[List[List[float]]] = []

        for _ in range(12):
            ok, frame = cap.read()
            if not ok or frame is None:
                break
            frames.append(frame)
            result = self.yolo(frame, verbose=False)[0]
            person_boxes: List[List[float]] = []
            for box in result.boxes:
                cls = int(box.cls.item())
                name = result.names.get(cls, str(cls))
                objects.add(name)
                object_freq[name] = object_freq.get(name, 0) + 1
                xyxy = box.xyxy[0].tolist()
                if name == "person":
                    people_count += 1
                    person_boxes.append(xyxy)
                if name in {"car", "truck", "bus", "motorcycle"}:
                    vehicle_count += 1
                if name == "dog":
                    dog_count += 1
            person_boxes_by_frame.append(person_boxes)

        cap.release()
        if not frames:
            raise RuntimeError("empty frame sequence for subclip")

        quality_score = _frame_quality(frames[len(frames) // 2])
        if quality_score < QUALITY_THRESHOLD:
            return {"drop": True, "reason": "low_quality", "quality_score": quality_score}

        contact_score = _contact_score(person_boxes_by_frame)
        caption = _simple_caption(people_count, dog_count, vehicle_count, objects, object_freq, contact_score, spec.get("peak_motion", 0.0))
        tags = extract_caption_threats(caption)

        signals = {
            "contact_score": contact_score,
            "peak_motion": spec.get("peak_motion", 0.0),
            "mean_motion": spec.get("mean_motion", 0.0),
            "people_count": people_count,
            "vehicle_count": vehicle_count,
            "dog_count": dog_count,
            "after_hours": 1 if is_after_hours(datetime.now()) else 0,
        }
        label, confidence, score_map = label_from_signals(signals, tags)
        alert_score, stage, reason = compute_alert_score(label, signals, tags)

        clip_embedding = _cheap_embedding(frames)

        return {
            "drop": False,
            "start_ms": start_ms,
            "end_ms": end_ms,
            "people_count": people_count,
            "vehicle_count": vehicle_count,
            "dog_count": dog_count,
            "objects": sorted(objects),
            "contact_score": contact_score,
            "caption": caption,
            "tags": tags,
            "label": label,
            "confidence": confidence,
            "score_map": score_map,
            "object_frequency": object_freq,
            "alert_score": alert_score,
            "alert_stage": stage,
            "alert_reason": reason,
            "quality_score": quality_score,
            "embedding": clip_embedding,
            "tracks": [],
            "trajectories": [],
        }


def _frame_quality(frame) -> float:
    import cv2
    import numpy as np

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    brightness = float(np.mean(gray) / 255.0)
    sharpness = float(min(1.0, cv2.Laplacian(gray, cv2.CV_64F).var() / 1000.0))
    return round((brightness + sharpness) / 2.0, 4)


def _simple_caption(
    people_count: int,
    dog_count: int,
    vehicle_count: int,
    objects: set[str],
    object_freq: Dict[str, int],
    contact_score: float,
    peak_motion: float,
) -> str:
    parts = [f"{people_count} people", f"{dog_count} dogs", f"{vehicle_count} vehicles"]
    if object_freq:
        top_objects = sorted(object_freq.items(), key=lambda item: item[1], reverse=True)[:5]
        parts.append("objects " + ", ".join(name for name, _ in top_objects))

    if dog_count > 0 and contact_score > 0.35:
        parts.append("dogs fighting growling dog biting dog aggression")
    elif dog_count > 0:
        parts.append("dog playing puppy wagging")

    if people_count >= 2 and contact_score > 0.40:
        parts.append("fight attack punch aggressive behavior")
    elif people_count >= 2:
        parts.append("handshake hug helping assist")

    if peak_motion > 0.45:
        parts.append("fall collapsed distress emergency")

    if "backpack" in objects or "handbag" in objects or "suitcase" in objects:
        parts.append("theft stealing snatch and run suspicious loitering tampering")

    if "car" in objects and ("person" in objects):
        parts.append("vehicle break in window smash")

    return "; ".join(parts)


def _cheap_embedding(frames) -> List[float]:
    import numpy as np

    picks = [frames[0], frames[len(frames) // 2], frames[-1]]
    vec = np.concatenate([p.mean(axis=(0, 1)) for p in picks]).astype("float32")
    vec = vec / (np.linalg.norm(vec) + 1e-9)
    return vec.tolist()


def _iou(a: List[float], b: List[float]) -> float:
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])
    inter = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    if inter == 0:
        return 0.0
    area_a = max(0.0, a[2] - a[0]) * max(0.0, a[3] - a[1])
    area_b = max(0.0, b[2] - b[0]) * max(0.0, b[3] - b[1])
    union = area_a + area_b - inter + 1e-9
    return inter / union


def _contact_score(frames_boxes: List[List[List[float]]]) -> float:
    best = 0.0
    for boxes in frames_boxes:
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                best = max(best, _iou(boxes[i], boxes[j]))
    return float(round(best, 4))


def _to_event_dict(video_source: str, spec: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
    event = EventJSON(
        clip_id=f"c{spec['chunk_index']:02d}_w{spec['window_index']:04d}_{int(spec['start'])}",
        video_source=video_source,
        chunk_index=spec["chunk_index"],
        window_index=spec["window_index"],
        time=TimeWindow(
            start_ms=result["start_ms"],
            end_ms=result["end_ms"],
            duration_ms=result["end_ms"] - result["start_ms"],
            first_detection_ms=result["start_ms"],
            last_detection_ms=result["end_ms"],
        ),
        start=spec["start"],
        end=spec["end"],
        duration=spec["end"] - spec["start"],
        quality_score=result["quality_score"],
        detections=DetectionSummary(
            people_count=result["people_count"],
            vehicle_count=result["vehicle_count"],
            peak_motion=spec.get("peak_motion", 0.0),
            mean_motion=spec.get("mean_motion", 0.0),
            contact_score=result["contact_score"],
            objects=result["objects"],
        ),
        tracks=result["tracks"],
        track_count=len(result["tracks"]),
        event=EventSummary(label=result["label"], confidence=result["confidence"]),
        evidence=result["score_map"],
        caption=result["caption"],
        tags=result["tags"],
        alert=AlertSummary(score=result["alert_score"], stage=result["alert_stage"], reason=result["alert_reason"]),
        _clip_embedding=result["embedding"],
        _track_trajectories=result["trajectories"],
        processed_at=datetime.now(timezone.utc).isoformat(),
        processing_gpu=GPU_TYPE,
    )
    return event.to_dict()


def _write_results(events: List[Dict[str, Any]]) -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    events_path = RESULTS_DIR / "events.json"
    alerts_path = RESULTS_DIR / "alerts.json"
    alerts = [{k: v for k, v in e.items() if k not in {"_clip_embedding", "_track_trajectories"}} for e in events]
    events_path.write_text(json.dumps(events, indent=2), encoding="utf-8")
    alerts_path.write_text(json.dumps(alerts, indent=2), encoding="utf-8")


def _index_events_actian(events: List[Dict[str, Any]]) -> int:
    # Optional integration placeholder.
    # Kept as no-op to avoid hard dependency on local backend services.
    _ = events
    return 0


@app.function(image=image, volumes={MODEL_DIR: weights_volume})
def download_models() -> Dict[str, str]:
    """Warm model cache in the `vigilant-model-weights` Modal Volume."""
    from huggingface_hub import snapshot_download

    snapshot_download(repo_id=CLIP_MODEL, local_dir=MODEL_DIR, ignore_patterns=["*.bin"])
    snapshot_download(repo_id=CAPTION_MODEL, local_dir=MODEL_DIR, ignore_patterns=["*.bin"])
    return {
        "status": "ok",
        "cache_dir": MODEL_DIR,
        "clip_model": CLIP_MODEL,
        "caption_model": CAPTION_MODEL,
        "yolo_weights": YOLO_WEIGHTS_PATH,
    }


@app.local_entrypoint()
def run_pipeline(input_video: str):
    source = Path(input_video)
    if not source.exists():
        raise FileNotFoundError(input_video)

    remote_path = f"inputs/{source.name}"
    with videos_volume.batch_upload(force=True) as batch:
        batch.put_file(str(source), remote_path)

    duration = _load_video_duration_seconds(source)
    chunks = make_video_chunks(duration, CHUNK_SECONDS)

    cpu_jobs = [cpu_chunk_worker.remote(remote_path, idx, s, e) for idx, (s, e) in enumerate(chunks)]
    specs: List[Dict[str, Any]] = []
    for chunk in cpu_jobs:
        specs.extend(chunk["windows"])

    extractor = FeatureExtractor()
    raw = [extractor.infer_subclip.remote(remote_path, spec) for spec in specs]

    events: List[Dict[str, Any]] = []
    for spec, result in zip(specs, raw):
        if result.get("drop"):
            continue
        events.append(_to_event_dict(source.name, spec, result))

    _write_results(events)
    inserted = _index_events_actian(events)

    top_alerts = sorted(events, key=lambda e: e["alert"]["score"], reverse=True)[:5]
    print(f"Processed {len(specs)} subclips -> {len(events)} events")
    print(f"Actian VectorDB indexed {inserted} events")
    for e in top_alerts:
        print(f"{e['clip_id']} | {e['event']['label']} | {e['alert']['stage']} | {e['alert']['score']}")
