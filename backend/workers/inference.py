"""
Vigilant-AI — Modal Pipeline
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Layer 0  │ Chunker + Motion Scorer        │ Modal CPU  (parallel, one per 5-min chunk)
Layer 1  │ Quality Gate                   │ (inside Layer 0)
Layer 2  │ YOLO Detection + Tracking      │ Modal GPU — A10G  (one per 10s sub-clip)
Layer 3  │ CLIP ViT-L/14 Embeddings       │ Modal GPU — A10G  (same container)
Layer 4  │ Florence-2-Large Captioning    │ Modal GPU — A10G  (same container)
Layer 5  │ Event JSON Assembly            │ in-process (GPU container)
Layer 6  │ Alert Scoring (Stage A/B/C)    │ in-process (GPU container)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TWO LEVELS OF PARALLELISM:
  1. CPU layer  — chunk_and_score.map()        one CPU worker per 5-min segment
  2. GPU layer  — extract_from_window.map()    one A10G worker per 10-s sub-clip

Non-multiples handled: a 9m15s video (555s) becomes [(0,300), (300,555)].
Overlap: every active window is sliced into 10s clips with 2s overlap (8s stride).

IMPORTANT: NOTHING heavy runs locally.
  - Local machine only needs:   pip install modal
  - All pip installs happen inside the Modal image (container)
  - Model weights live in Modal Volume 'vigilant-model-weights' (download once)
  - All torch/transformers/cv2 imports live inside Modal function bodies

Run (first time — download models):
    modal run workers/inference.py::download_models

Run pipeline:
    modal run workers/inference.py                   # uses test.mp4
    modal run workers/inference.py --video-path x.mp4
"""

# ── Local imports: ONLY stdlib + modal ────────────────────────────────────────
import modal
import json
import time
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Any

# ─── Config (plain Python literals — no deps) ──────────────────────────────────
GPU_TYPE          = "A100"
CHUNK_DURATION    = 300.0          # 5-minute segments for parallel CPU processing
SUBCLIP_DURATION  = 10.0           # each active window sliced into N×10s sub-clips
SUBCLIP_OVERLAP   = 2.0            # 2s overlap between consecutive sub-clips
TRACKING_FPS      = 8              # fps for YOLO tracking (higher = finer ms detail)
MOTION_SAMPLE_FPS = 2              # fps for motion scoring
MOTION_THRESHOLD  = 0.05           # fraction of changed pixels → motion
ACTIVE_MIN_SECS   = 1.5            # minimum active window length
WINDOW_MERGE_GAP  = 5.0            # merge windows within this gap (seconds)
AFTER_HOURS_START = 22             # 10 PM
AFTER_HOURS_END   = 6              # 6 AM
ALERT_C_THRESHOLD = 0.70
YOLO_CONF         = 0.25           # lower = catch more subtle detections
YOLO_MODEL        = "yolo11l.pt"
CLIP_MODEL_ID     = "openai/clip-vit-large-patch14"
VLM_MODEL_ID      = "Qwen/Qwen2-VL-7B-Instruct"   # multi-frame video understanding
MODEL_CACHE_DIR   = "/models"      # path inside Modal Volume

VIDEO_URL = "shoplifting2.mp4"

# Expanded COCO classes to detect beyond just person/vehicle
EXPANDED_OBJECTS  = {"backpack", "handbag", "suitcase", "bottle", "chair",
                     "cell phone", "laptop", "knife", "scissors", "fire hydrant"}
VEHICLE_CLASSES   = {"car", "truck", "bus", "motorcycle", "bicycle", "forklift"}

RESULTS_DIR = Path("results")      # local output directory

# ─── Modal Volumes ─────────────────────────────────────────────────────────────
model_vol = modal.Volume.from_name("vigilant-model-weights", create_if_missing=True)
video_vol = modal.Volume.from_name("vigilant-videos",        create_if_missing=True)

# ─── Modal Image ───────────────────────────────────────────────────────────────
# Simple debian_slim — no CUDA compiler needed since we use the
# no-flash-attn Florence-2 variant. Single pip_install, fast image build.
vigilant_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install([
        "ffmpeg", "libgl1-mesa-glx", "libglib2.0-0", "libsm6", "libxext6",
    ])
    .pip_install([
        "ultralytics>=8.3.0",
        "transformers>=4.45.0",
        "torch>=2.2.0",
        "torchvision>=0.17.0",
        "Pillow>=10.0.0",
        "opencv-python-headless>=4.9.0",
        "numpy",
        "einops",
        "timm",
        "huggingface_hub",
        "sentencepiece",
        "qwen-vl-utils",
        "accelerate>=0.26.0",
    ])
    .add_local_python_source("workers")
)
app = modal.App("vigilant-ai", image=vigilant_image)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MODEL DOWNLOADER  (run once: modal run workers/inference.py::download_models)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.function(
    volumes={MODEL_CACHE_DIR: model_vol},
    timeout=3600,
    image=vigilant_image,
)
def download_models():
    """
    One-time setup: downloads all model weights into the Modal Volume.
    After this runs, containers read from the volume — no internet needed.
    """
    import os, shutil, glob
    os.environ["HF_HOME"]            = MODEL_CACHE_DIR
    os.environ["TRANSFORMERS_CACHE"] = MODEL_CACHE_DIR
    os.environ["YOLO_CONFIG_DIR"]    = "/tmp/Ultralytics"   # suppress writable warning

    from ultralytics import YOLO
    from transformers import (
        CLIPModel, CLIPProcessor,
        Qwen2VLForConditionalGeneration, AutoProcessor,
    )

    print("⬇️  YOLOv11-L...")
    YOLO(YOLO_MODEL)
    # YOLO writes to /tmp when home isn't writable — copy from there to volume
    for search_dir in ["/tmp/Ultralytics", f"{os.path.expanduser('~')}/.config/Ultralytics"]:
        for f in glob.glob(f"{search_dir}/{YOLO_MODEL}"):
            dest = f"{MODEL_CACHE_DIR}/{YOLO_MODEL}"
            shutil.copy(f, dest)
            print(f"  Copied {YOLO_MODEL} → {dest}")

    print("⬇️  CLIP ViT-L/14...")
    CLIPModel.from_pretrained(CLIP_MODEL_ID,     cache_dir=MODEL_CACHE_DIR)
    CLIPProcessor.from_pretrained(CLIP_MODEL_ID, cache_dir=MODEL_CACHE_DIR)

    print("⬇️  Qwen2-VL-7B-Instruct (multi-frame video understanding)...")
    Qwen2VLForConditionalGeneration.from_pretrained(
        VLM_MODEL_ID, torch_dtype="auto", cache_dir=MODEL_CACHE_DIR,
    )
    AutoProcessor.from_pretrained(
        VLM_MODEL_ID, cache_dir=MODEL_CACHE_DIR,
    )

    model_vol.commit()
    print("✅ All models saved to Modal Volume 'vigilant-model-weights'")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LAYER 0 + 1 — Per-chunk Motion Scorer + Quality Gate  (Modal CPU)
#
# Runs in PARALLEL: one instance per 5-min segment via .map()
# Non-multiple durations handled: last chunk = whatever remains.
# Each active window is sliced into 10s sub-clips with 2s overlap.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.function(
    cpu=2,
    memory=4096,
    volumes={"/data": video_vol},
    timeout=600,
    image=vigilant_image,
)
def chunk_and_score(args: Tuple) -> List[Dict]:
    """
    Layer 0 + 1 for ONE 5-min segment of the video.

    Input : (video_name, chunk_start_sec, chunk_end_sec, chunk_index)
    Output: list of sub-clip WindowData dicts (one per 10s active sub-clip)

    Steps:
      1. Read only [chunk_start, chunk_end] frames from the video
      2. Compute motion score every 1/MOTION_SAMPLE_FPS seconds
      3. Find active windows (motion > threshold)
      4. Slice each active window into 10s sub-clips with 2s overlap
      5. Quality gate each sub-clip (brightness + sharpness)
      6. Return surviving sub-clips as WindowData dicts
    """
    import cv2
    import numpy as np
    from workers.pipeline import (
        find_active_windows, window_motion_stats,
        make_subclips, is_after_hours,
    )

    video_name, chunk_start, chunk_end, chunk_index = args
    video_path = f"/data/{video_name}"

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    fps          = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    total_secs   = total_frames / fps

    # Clamp chunk boundaries to actual video duration
    chunk_end = min(chunk_end, total_secs)
    if chunk_start >= chunk_end:
        cap.release()
        return []

    chunk_dur = chunk_end - chunk_start
    print(f"  📦 Chunk {chunk_index}: {chunk_start:.0f}s–{chunk_end:.0f}s "
          f"({chunk_dur:.1f}s of {total_secs:.1f}s total)")

    # ── Seek to chunk start ───────────────────────────────────────────────────
    cap.set(cv2.CAP_PROP_POS_MSEC, chunk_start * 1000)
    sample_every  = max(1, int(fps / MOTION_SAMPLE_FPS))
    motion_scores: List = []
    prev_gray     = None
    frame_idx     = 0

    while cap.isOpened():
        pos_sec = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        if pos_sec > chunk_end + 0.5:
            break
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % sample_every == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (5, 5), 0)
            if prev_gray is not None:
                diff  = cv2.absdiff(prev_gray, gray)
                score = float(np.sum(diff > 25) / diff.size)
                # Store absolute timestamp (seconds from video start)
                motion_scores.append((pos_sec, score))
            prev_gray = gray
        frame_idx += 1

    cap.release()

    if not motion_scores:
        return []

    # ── Find active windows within this chunk ─────────────────────────────────
    raw_windows = find_active_windows(motion_scores)
    print(f"    🎯 Chunk {chunk_index}: {len(raw_windows)} active windows")

    # ── Determine recording hour for after-hours flag ─────────────────────────
    mtime          = os.path.getmtime(video_path)
    recording_hour = datetime.fromtimestamp(mtime).hour
    after_hours    = is_after_hours(recording_hour)

    # ── Slice each active window into 10s sub-clips with 2s overlap ───────────
    subclip_datas: List[Dict] = []
    subclip_global_idx = 0

    for win_start, win_end in raw_windows:
        subclips = make_subclips(win_start, win_end,
                                 duration=SUBCLIP_DURATION,
                                 overlap=SUBCLIP_OVERLAP)

        for sc_start, sc_end in subclips:
            peak_m, mean_m = window_motion_stats(motion_scores, sc_start, sc_end)

            # ── Layer 1: Quality gate on mid-frame ────────────────────────────
            cap2 = cv2.VideoCapture(video_path)
            cap2.set(cv2.CAP_PROP_POS_MSEC, ((sc_start + sc_end) / 2) * 1000)
            ret, frame = cap2.read()
            cap2.release()

            quality = 0.5  # default if frame unreadable
            if ret:
                gray       = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                brightness = float(np.mean(gray)) / 255.0
                blur       = float(cv2.Laplacian(gray, cv2.CV_64F).var())
                quality    = 0.5 * min(brightness / 0.15, 1.0) + 0.5 * min(blur / 150.0, 1.0)

            if quality < 0.08:
                print(f"    ⚠️  Sub-clip dropped (quality={quality:.2f})")
                continue

            subclip_datas.append({
                "chunk_index":    chunk_index,
                "window_index":   subclip_global_idx,
                "video_source":   video_name,
                "start_sec":      sc_start,
                "end_sec":        sc_end,
                "peak_motion":    round(peak_m, 4),
                "mean_motion":    round(mean_m, 4),
                "quality_score":  round(quality, 3),
                "is_after_hours": after_hours,
            })
            subclip_global_idx += 1

    print(f"    ✅ Chunk {chunk_index}: {len(subclip_datas)} sub-clips ready for GPU")
    return subclip_datas


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LAYERS 2–6 — FeatureExtractor  (Modal GPU — A10G)
# One container per 10s sub-clip, all running in parallel.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.cls(
    gpu=GPU_TYPE,
    cpu=4,
    memory=24576,
    volumes={
        MODEL_CACHE_DIR: model_vol,
        "/data":         video_vol,
    },
    timeout=600,
    image=vigilant_image,
    max_containers=50,   # Modal 1.0: was concurrency_limit
)
class FeatureExtractor:
    """
    GPU worker. Models load once per container (@modal.enter).
    extract_from_window is called for each 10s sub-clip via .map().

    Layer 2 — YOLOv11-L detection + ByteTrack tracking
    Layer 3 — CLIP ViT-L/14 embedding (avg of 3 keyframes)
    Layer 4 — Florence-2-Large captioning (mid-window keyframe)
    Layer 5 — Signal-based event labeling
    Layer 6 — Alert scoring: Stage A (rules) → B (score) → C (LLM verify)
    """

    @modal.enter()
    def load_models(self):
        """Runs once per container start. Reads from Modal Volume — no download."""
        import os
        import torch
        from ultralytics import YOLO
        from transformers import (
            CLIPModel, CLIPProcessor,
            AutoModelForCausalLM, AutoProcessor,
        )
        os.environ["HF_HOME"]            = MODEL_CACHE_DIR
        os.environ["TRANSFORMERS_CACHE"] = MODEL_CACHE_DIR
        os.environ["YOLO_CONFIG_DIR"]    = "/tmp/Ultralytics"

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.dtype  = torch.float16 if self.device == "cuda" else torch.float32
        print(f"🚀 Container | device={self.device} | gpu={GPU_TYPE}")

        self.yolo = YOLO(YOLO_MODEL)
        print("✅ YOLOv11-L")

        self.clip_model     = CLIPModel.from_pretrained(
            CLIP_MODEL_ID, cache_dir=MODEL_CACHE_DIR
        ).to(self.device)
        self.clip_processor = CLIPProcessor.from_pretrained(
            CLIP_MODEL_ID, cache_dir=MODEL_CACHE_DIR
        )
        self.clip_model.eval()
        print("✅ CLIP ViT-L/14")

        from transformers import Qwen2VLForConditionalGeneration
        self.vlm = Qwen2VLForConditionalGeneration.from_pretrained(
            VLM_MODEL_ID, torch_dtype=self.dtype,
            attn_implementation="sdpa",   # no flash_attn needed
            cache_dir=MODEL_CACHE_DIR,
        ).to(self.device)
        self.vlm_proc = AutoProcessor.from_pretrained(
            VLM_MODEL_ID, cache_dir=MODEL_CACHE_DIR,
        )
        self.vlm.eval()
        print(f"✅ Qwen2-VL-7B (SDPA) | 🟢 Container ready on {GPU_TYPE}")

    @modal.method()
    def extract_from_window(self, window: Dict) -> Dict:
        """Process one 10-second sub-clip through Layers 2–6."""
        import cv2
        import numpy as np
        import torch
        from PIL import Image
        from workers.pipeline import (
            max_pairwise_iou, label_from_signals,
            compute_alert_score, ALERT_C_THRESHOLD,
        )

        video_path = f"/data/{window['video_source']}"
        win_start  = window["start_sec"]
        win_end    = window["end_sec"]
        chunk_idx  = window["chunk_index"]
        win_idx    = window["window_index"]
        clip_id    = f"c{chunk_idx:02d}_w{win_idx:04d}"

        # ── Extract frames at TRACKING_FPS ───────────────────────────────────
        cap       = cv2.VideoCapture(video_path)
        video_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        step      = max(1, int(video_fps / TRACKING_FPS))

        frames: List = []
        cap.set(cv2.CAP_PROP_POS_MSEC, win_start * 1000)
        while cap.isOpened():
            ts = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
            if ts > win_end + 0.1:
                break
            ret, frame = cap.read()
            if not ret:
                break
            if int(cap.get(cv2.CAP_PROP_POS_FRAMES)) % step == 0:
                frames.append((ts, frame))
        cap.release()

        if not frames:
            return self._empty_event(window, clip_id, "no_frames")

        # ── Layer 2 — YOLO Detection + ByteTrack ─────────────────────────────
        bgr_only = [f for _, f in frames]
        try:
            results = self.yolo.track(
                source=bgr_only, conf=YOLO_CONF, iou=0.5,
                tracker="bytetrack.yaml", persist=True, verbose=False,
            )
        except Exception as e:
            print(f"  ⚠️  Tracking fallback ({e})")
            results = self.yolo(bgr_only, conf=YOLO_CONF, verbose=False)

        people_max  = 0
        vehicle_max = 0
        person_tracks: Dict = {}
        contact_score       = 0.0
        objects_seen: Dict[str, int] = {}   # expanded class counts
        first_detection_ms: float = -1
        last_detection_ms:  float = -1

        for (ts, _), res in zip(frames, results):
            if res.boxes is None or len(res.boxes) == 0:
                continue
            person_boxes_frame: List = []
            np_, nv_ = 0, 0

            for box in res.boxes:
                cid   = int(box.cls[0])
                cname = res.names[cid]
                xyxy  = box.xyxy[0].tolist()
                conf  = float(box.conf[0])

                if cname == "person":
                    np_ += 1
                    person_boxes_frame.append(xyxy)
                    if first_detection_ms < 0:
                        first_detection_ms = ts * 1000
                    last_detection_ms = ts * 1000
                    if box.id is not None:
                        tid = int(box.id[0])
                        person_tracks.setdefault(tid, []).append((ts, xyxy))
                elif cname in VEHICLE_CLASSES:
                    nv_ += 1
                    if first_detection_ms < 0:
                        first_detection_ms = ts * 1000
                    last_detection_ms = ts * 1000
                elif cname in EXPANDED_OBJECTS:
                    objects_seen[cname] = objects_seen.get(cname, 0) + 1

            people_max  = max(people_max,  np_)
            vehicle_max = max(vehicle_max, nv_)
            if len(person_boxes_frame) >= 2:
                contact_score = max(contact_score, max_pairwise_iou(person_boxes_frame))

        # Build track summaries (trajectories go to DB only, not JSON)
        track_summaries: List[Dict] = []
        track_trajectories: List[Dict] = []
        for tid, tdata in person_tracks.items():
            if len(tdata) >= 2:
                dwell = tdata[-1][0] - tdata[0][0]
                track_summaries.append({
                    "id":            f"p{tid}",
                    "dwell_seconds": round(dwell, 2),
                    "entry_ms":      round(tdata[0][0] * 1000, 1),
                    "exit_ms":       round(tdata[-1][0] * 1000, 1),
                })
                track_trajectories.append({
                    "id": f"p{tid}",
                    "points": [[round(t * 1000, 1), round(b[0], 1), round(b[1], 1)]
                               for t, b in tdata],
                })

        max_dwell = max((t["dwell_seconds"] for t in track_summaries), default=0.0)

        # ── Keyframes: start / mid / end ──────────────────────────────────────
        kf_indices = [0, len(frames) // 2, len(frames) - 1]
        kf_pil: List = []
        for ki in kf_indices:
            _, bgr = frames[min(ki, len(frames)-1)]
            kf_pil.append(Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)))

        # ── Layer 3 — CLIP Embedding (avg over keyframes) ─────────────────────
        with torch.no_grad():
            ci = self.clip_processor(images=kf_pil, return_tensors="pt", padding=True)
            ci = {k: v.to(self.device) for k, v in ci.items()}
            feats = self.clip_model.get_image_features(**ci)
            # transformers 5.x returns BaseModelOutputWithPooling; extract tensor
            if hasattr(feats, 'image_embeds'):
                feats = feats.image_embeds
            elif not isinstance(feats, torch.Tensor):
                feats = feats[0]  # first element is the tensor
            clip_vec = feats.mean(dim=0).cpu().float().tolist()

        # ── Layer 4 — Qwen2-VL multi-frame caption ─────────────────────────
        caption = self._vlm_caption(kf_pil, track_summaries, people_max, vehicle_max,
                                    round(contact_score, 3), round(window["peak_motion"], 3))

        #---
        # Simple theft context: presence of carry/valuable items
        carry_items = {"backpack", "handbag", "suitcase"}
        valuable_items = {"cell phone", "laptop"}

        has_carry = any(k in (objects_seen or {}) for k in carry_items)
        has_valuable = any(k in (objects_seen or {}) for k in valuable_items)

        # Optional: append hint words into caption to help the caption keyword extractor
        # (keeps doors open without changing pipeline function signatures)
        if has_carry:
            caption = caption + " (person has a bag/backpack)"
        if has_valuable:
            caption = caption + " (valuable item visible)"
        #---
        # ── Layer 5 — Signal-based event labeling ─────────────────────────────
        hypotheses, tags = label_from_signals(
            people_count      = people_max,
            vehicle_count     = vehicle_max,
            contact_score     = contact_score,
            peak_motion       = window["peak_motion"],
            dwell_seconds     = max_dwell,
            after_hours_flag  = window["is_after_hours"],
            caption           = caption,
        )
        # Top hypothesis → primary event label
        if hypotheses:
            event_label = hypotheses[0]["label"]
            event_conf  = hypotheses[0]["confidence"]
        else:
            event_label = "activity_detected"
            event_conf  = 0.5

        # ── Layer 6 — Alert Scoring (Stage A → B → C) ─────────────────────────
        evidence = {
            "motion":        round(window["peak_motion"], 3),
            "overlap":       round(contact_score, 3),
            "dwell_seconds": round(max_dwell, 1),
            "people_count":  float(people_max),
            "vehicle_count": float(vehicle_max),
        }
        alert_score, alert_stage = compute_alert_score(evidence, window["is_after_hours"])

        alert_reason = f"primary={event_label}"
        if alert_score >= ALERT_C_THRESHOLD:
            alert_reason = self._stage_c_verify(kf_pil, evidence, event_label)

        icon = "🚨" if alert_stage in ("B","C") else "✅"
        print(f"  {icon} {clip_id}: {event_label} | "
              f"score={alert_score:.2f} stage={alert_stage} people={people_max}")

        # ── Build clean output ────────────────────────────────────────────────
        # JSON-friendly output: no raw embeddings or trajectory arrays
        # Embeddings → VectorAI only. Trajectories → SQLite only.
        start_ms = round(win_start * 1000, 1)
        end_ms   = round(win_end * 1000, 1)

        return {
            "clip_id":        clip_id,
            "video_source":   window["video_source"],
            "chunk_index":    chunk_idx,
            "window_index":   win_idx,

            # Millisecond-precision timestamps
            "time": {
                "start_ms":           start_ms,
                "end_ms":             end_ms,
                "duration_ms":        round(end_ms - start_ms, 1),
                "first_detection_ms": round(first_detection_ms, 1) if first_detection_ms >= 0 else None,
                "last_detection_ms":  round(last_detection_ms, 1) if last_detection_ms >= 0 else None,
            },
            # Legacy float seconds (for backward compat)
            "start":          round(win_start, 3),
            "end":            round(win_end, 3),
            "duration":       round(win_end - win_start, 3),

            "quality_score":  round(window["quality_score"], 3),

            "detections": {
                "people_count":   people_max,
                "vehicle_count":  vehicle_max,
                "peak_motion":    round(window["peak_motion"], 4),
                "mean_motion":    round(window["mean_motion"], 4),
                "contact_score":  round(contact_score, 4),
                "objects":        objects_seen if objects_seen else None,
            },

            # Track summaries (no full trajectory data in JSON)
            "tracks":         track_summaries,
            "track_count":    len(track_summaries),

            "event":          {"label": event_label, "confidence": event_conf},
            "evidence":       evidence,
            "caption":        caption,
            "tags":           tags,

            "alert": {
                "score":  round(alert_score, 3),
                "stage":  alert_stage,
                "reason": alert_reason,
            },

            # These go to DB only, stripped from API responses
            "_clip_embedding":     clip_vec,
            "_track_trajectories": track_trajectories,

            "processed_at":   datetime.utcnow().isoformat() + "Z",
            "processing_gpu": GPU_TYPE,
        }

    # ── Private helpers ────────────────────────────────────────────────────────

    def _vlm_caption(self, keyframes: List, tracks: List[Dict],
                     people: int, vehicles: int,
                     contact: float, motion: float) -> str:
        """
        Multi-frame Qwen2-VL caption. Sends start/mid/end keyframes with
        detection context so the VLM understands temporal progression.
        """
        import torch
        from qwen_vl_utils import process_vision_info

        # Build signal context for the VLM
        track_desc = ""
        for t in tracks[:4]:
            track_desc += (f"  Person {t['id']}: present for {t['dwell_seconds']}s "
                          f"(entered at {t.get('entry_ms',0)/1000:.1f}s, "
                          f"exited at {t.get('exit_ms',0)/1000:.1f}s)\n")

        prompt = (
            f"These are 3 frames from a CCTV surveillance clip (start, middle, end of a {len(keyframes)}-frame sequence).\n"
            f"Detection signals: {people} people detected, {vehicles} vehicles, "
            f"physical contact score={contact}, motion intensity={motion}.\n"
            f"{track_desc}"
            f"Describe in detail: What is happening? Who is doing what to whom? "
            f"What changed between the start frame and the end frame? "
            f"Be specific about actions (hitting, falling, running, standing, etc). "
            f"Keep it under 100 words."
        )

        # Build multi-image message for Qwen2-VL
        content = []
        for i, kf in enumerate(keyframes[:3]):
            content.append({"type": "image", "image": kf})
        content.append({"type": "text", "text": prompt})

        messages = [{"role": "user", "content": content}]

        text = self.vlm_proc.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = self.vlm_proc(
            text=[text], images=image_inputs, videos=video_inputs,
            padding=True, return_tensors="pt",
        ).to(self.device)

        with torch.no_grad():
            ids = self.vlm.generate(
                **inputs,
                max_new_tokens=200,
                do_sample=False,
            )
        # Trim the input tokens from the output
        generated = ids[:, inputs.input_ids.shape[1]:]
        text_out = self.vlm_proc.batch_decode(generated, skip_special_tokens=True)[0].strip()
        return text_out or "Scene description unavailable."

    def _stage_c_verify(self, keyframes, evidence: Dict, event_label: str) -> str:
        """Multi-frame VLM analysis for high-risk events (Stage C)."""
        desc = self._vlm_caption(
            keyframes[:3], [], int(evidence.get('people_count', 0)),
            int(evidence.get('vehicle_count', 0)),
            evidence.get('overlap', 0), evidence.get('motion', 0),
        )
        return f"STAGE-C | {event_label} | {desc}"

    def _empty_event(self, window: Dict, clip_id: str, reason: str) -> Dict:
        s_ms = round(window["start_sec"] * 1000, 1)
        e_ms = round(window["end_sec"] * 1000, 1)
        return {
            "clip_id": clip_id, "video_source": window["video_source"],
            "chunk_index": window["chunk_index"], "window_index": window["window_index"],
            "time": {"start_ms": s_ms, "end_ms": e_ms, "duration_ms": round(e_ms - s_ms, 1),
                     "first_detection_ms": None, "last_detection_ms": None},
            "start": window["start_sec"], "end": window["end_sec"],
            "duration": round(window["end_sec"] - window["start_sec"], 3),
            "quality_score": window["quality_score"],
            "detections": {"people_count": 0, "vehicle_count": 0, "peak_motion": 0,
                           "mean_motion": 0, "contact_score": 0, "objects": None},
            "tracks": [], "track_count": 0,
            "event": {"label": "processing_error", "confidence": 0.0},
            "evidence": {"error": reason},
            "_clip_embedding": [], "_track_trajectories": [],
            "caption": reason, "tags": ["error"],
            "alert": {"score": 0.0, "stage": "none", "reason": reason},
            "processed_at": datetime.utcnow().isoformat() + "Z",
            "processing_gpu": GPU_TYPE,
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LOCAL ENTRYPOINT — Orchestrates the full pipeline
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.local_entrypoint()
def main(video_path: str = VIDEO_URL):
    """
    Runs on your local machine — orchestrates everything on Modal.

    Two-level parallelism:
      Level 1 (CPU): chunk_and_score.map()       → N parallel CPU workers
      Level 2 (GPU): extract_from_window.map()   → M parallel A10G workers

    Handles non-multiple-of-5-min durations automatically.
    """
    import sys

    video_file = Path(video_path)
    if not video_file.exists():
        print(f"❌  Video not found: {video_file.resolve()}")
        sys.exit(1)

    RESULTS_DIR.mkdir(exist_ok=True)
    video_name = video_file.name

    # ── Step 1: Upload video to Modal Volume ──────────────────────────────────
    print(f"\n📤 Uploading '{video_name}' → Modal Volume...")
    with video_vol.batch_upload(force=True) as batch:
        batch.put_file(str(video_file), video_name)
    print("✅ Upload done")

    # ── Step 2: Compute chunk boundaries (handles non-multiples) ─────────────
    # We need the video duration to build chunk list.
    # Quick local check using Path stat doesn't give us duration, so we query
    # the volume via a lightweight Modal call.
    print(f"\n📐 Computing chunk boundaries...")
    total_seconds: float = get_video_duration.remote(video_name)
    from workers.pipeline import make_video_chunks
    raw_chunks = make_video_chunks(total_seconds, CHUNK_DURATION)
    print(f"  Video duration : {total_seconds:.1f}s  ({total_seconds/60:.1f} min)")
    print(f"  Chunks created : {len(raw_chunks)}  "
          f"(last chunk: {raw_chunks[-1][0]:.0f}s–{raw_chunks[-1][1]:.0f}s)")

    # Build args tuples: (video_name, start, end, chunk_index)
    chunk_args = [
        (video_name, start, end, idx)
        for idx, (start, end) in enumerate(raw_chunks)
    ]

    # ── Step 3: Parallel CPU — motion scoring + sub-clip detection ────────────
    print(f"\n🔍 Layer 0+1 — Chunking + motion scoring "
          f"({len(chunk_args)} parallel CPU workers)...")
    t0 = time.time()
    chunked_results: List[List[Dict]] = list(
        chunk_and_score.map(chunk_args, order_outputs=True)
    )
    # Flatten: each CPU worker returns a list of sub-clips
    all_subclips: List[Dict] = [
        sc for chunk_scs in chunked_results for sc in chunk_scs
    ]
    cpu_time = time.time() - t0
    print(f"✅ {len(all_subclips)} active 10s sub-clips found in {cpu_time:.1f}s "
          f"(across {len(chunk_args)} parallel workers)")

    if not all_subclips:
        print("⚠️  No active sub-clips detected. Exiting.")
        return

    # ── Step 4: Parallel GPU — feature extraction ─────────────────────────────
    print(f"\n⚡ Layers 2–6 — {len(all_subclips)} sub-clips → "
          f"parallel A10G workers...")
    t_gpu = time.time()
    extractor = FeatureExtractor()
    events: List[Dict] = list(
        extractor.extract_from_window.map(all_subclips, order_outputs=False)
    )
    gpu_time   = time.time() - t_gpu
    total_time = time.time() - t0

    # ── Step 5: Summarise + save ──────────────────────────────────────────────
    alerts  = [e for e in events if e["alert"]["stage"] != "none"]
    stage_c = [e for e in alerts  if e["alert"]["stage"] == "C"]
    events.sort(key=lambda e: e["start"])
    alerts.sort(key=lambda e: e["alert"]["score"], reverse=True)

    print(f"\n{'─'*54}")
    print(f"  📊 SENTINEL-STREAM RESULTS")
    print(f"{'─'*54}")
    print(f"  Video                  : {video_name}")
    print(f"  Duration               : {total_seconds:.0f}s  ({total_seconds/60:.1f} min)")
    print(f"  5-min Chunks           : {len(chunk_args)}  (CPU parallel workers)")
    print(f"  10s Sub-clips processed: {len(events)}")
    print(f"  Alerts triggered       : {len(alerts)}")
    print(f"  Stage C (critical)     : {len(stage_c)}")
    print(f"  GPU                    : {GPU_TYPE}")
    print(f"  CPU phase time         : {cpu_time:.1f}s")
    print(f"  GPU phase time         : {gpu_time:.1f}s")
    print(f"  Total pipeline time    : {total_time:.1f}s")
    print(f"  GPU workers used       : {len(all_subclips)} parallel A10G containers")
    print(f"{'─'*54}\n")

    events_path = RESULTS_DIR / "events.json"
    with open(events_path, "w") as f:
        json.dump({
            "video": video_name, "duration_s": total_seconds,
            "chunks": len(chunk_args), "subclips": len(events),
            "total_alerts": len(alerts),
            "cpu_time_s": round(cpu_time, 2),
            "gpu_time_s": round(gpu_time, 2),
            "total_time_s": round(total_time, 2),
            "gpu": GPU_TYPE, "events": events,
        }, f, indent=2)

    # Alert summary (strip heavy fields)
    alert_summary = [{k: v for k, v in a.items()
                      if k not in ("_clip_embedding", "_track_trajectories")}
                     for a in alerts]
    alerts_path = RESULTS_DIR / "alerts.json"
    with open(alerts_path, "w") as f:
        json.dump({"video": video_name, "alerts": alert_summary}, f, indent=2)

    print(f"💾 {events_path}  ({len(events)} events)")
    print(f"🚨 {alerts_path}  ({len(alerts)} alerts)")

    if alerts:
        print(f"\n🚨 TOP ALERTS:")
        for a in alerts[:5]:
            label = a["event"]["label"]
            print(f"  [{a['alert']['stage']}] {a['clip_id']}  "
                  f"{a['start']:.1f}s–{a['end']:.1f}s  "
                  f"score={a['alert']['score']:.2f}  {label}")
            print(f"       {a['caption'][:100]}...")


# ── Helper: get video duration on Modal (reads from Volume) ───────────────────
@app.function(
    volumes={"/data": video_vol},
    image=vigilant_image,
    timeout=60,
)
def get_video_duration(video_name: str) -> float:
    """Returns total duration in seconds using cv2 — runs on Modal."""
    import cv2
    cap = cv2.VideoCapture(f"/data/{video_name}")
    fps    = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return frames / fps
