"""
Vigilant-AI — Modal Pipeline
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Layer 0  │ Chunker + Motion Scorer        │ Modal CPU  (parallel, one per 5-min chunk)
Layer 1  │ Quality Gate                   │ (inside Layer 0)
Layer 2  │ YOLO Detection + Tracking      │ Modal GPU — A100  (one per 10s sub-clip)
Layer 3  │ CLIP ViT-L/14 Embeddings       │ Modal GPU — A100  (same container)
Layer 4  │ Gemini 2.0 Flash Vision        │ API call  (from GPU container, no censorship)
Layer 5  │ Signal-based Event Labeling    │ in-process (GPU container)
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
GEMINI_MODEL_ID   = "gemini-2.0-flash"             # vision API — no censorship, fast
GEMINI_API_KEY    = os.environ.get("GEMINI_API_KEY", "AIzaSyABZMPfjVnsPu3aYpnuFqhORorteVao6wo")
MODEL_CACHE_DIR   = "/models"      # path inside Modal Volume

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
        "huggingface_hub",
        "accelerate>=0.26.0",
        "google-genai>=1.0.0",
    ])
    .add_local_python_source("workers")
)
app = modal.App("vigilant-ai", image=vigilant_image)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MODEL DOWNLOADER  (run once: modal run workers/inference.py::download_models)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.function(
    volumes={MODEL_CACHE_DIR: model_vol},
    timeout=1800,
    image=vigilant_image,
)
def download_models():
    """
    One-time setup: downloads YOLO + CLIP weights into the Modal Volume.
    Captioning is handled by Gemini API (no local VLM weights needed).
    After this runs, containers read from the volume — no internet needed.
    """
    import os, shutil, glob
    os.environ["HF_HOME"]            = MODEL_CACHE_DIR
    os.environ["TRANSFORMERS_CACHE"] = MODEL_CACHE_DIR
    os.environ["YOLO_CONFIG_DIR"]    = "/tmp/Ultralytics"

    from ultralytics import YOLO
    from transformers import CLIPModel, CLIPProcessor

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

    model_vol.commit()
    print("✅ YOLO + CLIP saved to Modal Volume 'vigilant-model-weights'")
    print("ℹ️  Captioning handled by Gemini 2.0 Flash API — no VLM weights needed")


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
    Layer 3 — CLIP ViT-L/14 embedding (avg of 5 keyframes, 768-dim, L2-normalized)
    Layer 4 — Gemini 2.0 Flash Vision captioning (5 keyframes → forensic JSON)
    Layer 5 — Signal-based multi-hypothesis event labeling (pipeline.py)
    Layer 6 — Alert scoring: Stage A (rules) → B (score) → C threshold
    """

    @modal.enter()
    def load_models(self):
        """Runs once per container start. Reads from Modal Volume — no download."""
        import os
        import torch
        from ultralytics import YOLO
        from transformers import CLIPModel, CLIPProcessor

        os.environ["HF_HOME"]            = MODEL_CACHE_DIR
        os.environ["TRANSFORMERS_CACHE"] = MODEL_CACHE_DIR
        os.environ["YOLO_CONFIG_DIR"]    = "/tmp/Ultralytics"

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
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
        print(f"✅ CLIP ViT-L/14 | 🟢 Container ready on {GPU_TYPE}")

    @modal.method()
    def extract_from_window(self, window: Dict) -> Dict:
        """Process one 10-second sub-clip through Layers 2–6."""
        import cv2
        import numpy as np
        import torch
        from PIL import Image

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
        contact_score = 0.0             # max pairwise IoU across all frames
        person_tracks: Dict = {}
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

            # Contact score: max bounding-box IoU between any two people this frame
            if len(person_boxes_frame) >= 2:
                from workers.pipeline import max_pairwise_iou
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

        # ── Keyframes: 5 evenly spaced frames ─────────────────────────────────
        kf_indices = [int(i * (len(frames) - 1) / 4) for i in range(5)]
        kf_pil: List = []
        for ki in kf_indices:
            _, bgr = frames[min(ki, len(frames)-1)]
            kf_pil.append(Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)))

        # ── Layer 3 — CLIP Embedding (avg over keyframes) ─────────────────────
        with torch.no_grad():
            ci = self.clip_processor(images=kf_pil, return_tensors="pt", padding=True)
            pixel_values = ci["pixel_values"].to(self.device)
            # Use vision_model + visual_projection directly.
            # get_image_features() has version-dependent return shapes in newer
            # transformers (can return [batch, seq_len, hidden] instead of [batch, 768]).
            # Accessing sub-modules directly gives guaranteed stable shapes:
            #   vision_model -> pooler_output: [N, 1024] (CLS token, ViT-L/14 hidden size)
            #   visual_projection: Linear(1024 → 768) -> [N, 768]
            vision_out = self.clip_model.vision_model(pixel_values=pixel_values)
            pooled  = vision_out.pooler_output                  # [N, 1024]
            feats   = self.clip_model.visual_projection(pooled) # [N, 768]
            feats   = feats / feats.norm(dim=-1, keepdim=True)  # L2 norm per frame
            clip_vec_t = feats.mean(dim=0)                      # [768]
            clip_vec_t = clip_vec_t / clip_vec_t.norm()         # L2 norm final
            clip_vec = clip_vec_t.cpu().float().tolist()        # flat list, always 768

        assert len(clip_vec) == 768 and isinstance(clip_vec[0], float), (
            f"CLIP image embed: expected 768 floats, got len={len(clip_vec)}"
        )

        # ── Layer 4 — Gemini 2.0 Flash Vision caption ──────────────────────
        vlm_data = self._vlm_caption(kf_pil)
        caption = vlm_data.get("description", "No description")

        # ── Layer 5 — Signal-based multi-hypothesis event labeling ──────────
        from workers.pipeline import (
            label_from_signals, compute_alert_score, extract_caption_threats,
        )

        hypotheses, tags = label_from_signals(
            people_count    = people_max,
            vehicle_count   = vehicle_max,
            contact_score   = contact_score,
            peak_motion     = window["peak_motion"],
            dwell_seconds   = max_dwell,
            after_hours_flag= window["is_after_hours"],
            caption         = caption,
        )

        # VLM boolean flags can force high-confidence hypotheses
        if vlm_data.get("is_fighting") and not any(h["label"] == "physical_altercation" for h in hypotheses):
            hypotheses.insert(0, {"label": "physical_altercation", "confidence": 0.85, "severity": "high"})
        if vlm_data.get("is_stealing") and not any(h["label"] == "suspicious_behavior" for h in hypotheses):
            hypotheses.insert(0, {"label": "suspicious_behavior", "confidence": 0.80, "severity": "medium"})

        # Primary event = top hypothesis
        if hypotheses:
            event_label = hypotheses[0]["label"]
            event_conf  = hypotheses[0]["confidence"]
        else:
            event_label = "activity_detected"
            event_conf  = 0.30

        # ── Layer 6 — Alert Scoring (Stage A / B / C) ───────────────────────
        caption_threats = extract_caption_threats(caption)
        evidence = {
            "motion":        round(window["peak_motion"], 3),
            "overlap":       round(contact_score, 4),
            "dwell_seconds": round(max_dwell, 1),
            "people_count":  float(people_max),
            "vehicle_count": float(vehicle_max),
            "vlm_flags": {
                "fighting": vlm_data.get("is_fighting", False),
                "stealing": vlm_data.get("is_stealing", False),
                "erratic":  vlm_data.get("is_erratic", False),
            },
        }

        alert_score, alert_stage = compute_alert_score(
            evidence         = evidence,
            after_hours_flag = window["is_after_hours"],
            events_list      = hypotheses,
            caption_threats  = caption_threats,
        )
        alert_reason = event_label

        icon = "🚨" if alert_stage in ("A", "B", "C") else "✅"
        print(f"  {icon} {clip_id}: {event_label} | people={people_max} | alert={alert_stage}({alert_score:.2f})")

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
                "objects":        objects_seen if objects_seen else None,
            },

            # Track summaries (no full trajectory data in JSON)
            "tracks":         track_summaries,
            "track_count":    len(track_summaries),

            "event":      {"label": event_label, "confidence": event_conf},
            "hypotheses": hypotheses,               # full ranked hypothesis list
            "evidence":   evidence,
            "caption":    caption,
            "tags":       tags,

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

    def _vlm_caption(self, keyframes: List) -> Dict:
        """
        Multi-frame caption using Gemini 2.0 Flash Vision API.

        Sends up to 5 JPEG keyframes + a forensic analysis prompt to Gemini.
        Returns parsed JSON dict with 'description' and boolean flags.
        Gemini has no safety filters for forensic/surveillance use-cases —
        it will accurately describe violence, theft, and other incidents.
        """
        import io, json
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=GEMINI_API_KEY)

        prompt_text = (
            f"You are a Forensic Video Analyst reviewing {len(keyframes)} sequential CCTV keyframes. "
            "These frames are from a security camera. Your job is objective, accurate description. "
            "Do NOT use euphemisms. If you see punching, say punching. "
            "If you see someone concealing merchandise, say that explicitly. "
            "Pay close attention to hands and body contact between people.\n\n"
            "Respond ONLY with raw JSON (no markdown, no code fences):\n"
            '{"description": "Precise chronological description of what is happening. '
            'Name physical actions explicitly.", '
            '"is_fighting": true_or_false, '
            '"is_stealing": true_or_false, '
            '"is_erratic": true_or_false}'
        )

        # Build parts: JPEG images first, then text prompt
        parts = []
        for kf in keyframes:
            buf = io.BytesIO()
            kf.save(buf, format="JPEG", quality=85)
            parts.append(types.Part.from_bytes(data=buf.getvalue(), mime_type="image/jpeg"))
        parts.append(types.Part.from_text(text=prompt_text))

        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL_ID,
                contents=parts,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=512,
                ),
            )
            raw = (response.text or "").strip()
        except Exception as e:
            print(f"  ⚠️ Gemini API error: {e}")
            return {"description": "API error", "is_fighting": False, "is_stealing": False, "is_erratic": False}

        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw.rsplit("```", 1)[0]
        if raw.lstrip().startswith("json"):
            raw = raw.lstrip()[4:]
        raw = raw.strip()

        try:
            result = json.loads(raw)
            # Ensure all expected keys exist
            return {
                "description": str(result.get("description", raw[:200])),
                "is_fighting": bool(result.get("is_fighting", False)),
                "is_stealing": bool(result.get("is_stealing", False)),
                "is_erratic":  bool(result.get("is_erratic", False)),
            }
        except Exception as e:
            print(f"  ⚠️ Gemini JSON parse failed: {e} | raw={raw[:120]}")
            return {
                "description": raw[:500] if raw else "Parse error",
                "is_fighting": False,
                "is_stealing": False,
                "is_erratic":  False,
            }



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
            "hypotheses": [],
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
def main(video_path: str = "test.mp4"):
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
