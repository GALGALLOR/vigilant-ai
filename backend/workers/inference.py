"""
Vigilant-AI — Modal Pipeline
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Layer 0  │ Chunker + Motion Scorer        │ Modal CPU  (parallel, one per 5-min chunk)
Layer 1  │ Quality Gate                   │ (inside Layer 0)
Layer 2  │ YOLO Detection + Tracking      │ Modal GPU — A100  (one per 10s sub-clip)
Layer 3  │ CLIP ViT-L/14 Embeddings       │ Modal GPU — A100  (same container)
Layer 4  │ Gemini 2.5 Pro Vision          │ API call  (best reasoning for subtle actions)
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
GEMINI_MODEL_ID   = "gemini-2.5-pro"               # vision API — best reasoning for subtle actions
GEMINI_API_KEY    = os.environ.get("GEMINI_API_KEY", "")
MODEL_CACHE_DIR   = "/models"      # path inside Modal Volume
QWEN_MODEL_ID     = "Qwen/Qwen2.5-VL-7B-Instruct"
QWEN_LOCAL_DIR    = f"{MODEL_CACHE_DIR}/qwen25-vl-7b"  # where weights land in the Volume

# Expanded COCO classes to detect beyond just person/vehicle
EXPANDED_OBJECTS  = {"backpack", "handbag", "suitcase", "bottle", "chair",
                     "cell phone", "laptop", "knife", "scissors", "fire hydrant"}
VEHICLE_CLASSES   = {"car", "truck", "bus", "motorcycle", "bicycle", "forklift"}

RESULTS_DIR = Path("results")      # local output directory


# ─── JSON Cleaner (local copy — services/ not available in Modal container) ───

def _clean_json_string(raw: str) -> str:
    """
    Fix two classes of Gemini output bugs before json.loads():
    1. Literal control chars (\\n, \\r, \\t) inside JSON string values.
    2. Unescaped double-quotes embedded inside JSON string values,
       e.g. "description": "The officer struck the "detainee" while..."
    Uses lookahead: if the char after " is a JSON structural delimiter
    (:, ,, }, ]) then it's a closing quote; otherwise escape it as \\".
    """
    chars = list(raw)
    n = len(chars)
    result: list = []
    in_string = False
    escape_next = False
    i = 0
    while i < n:
        ch = chars[i]
        if escape_next:
            result.append(ch); escape_next = False; i += 1; continue
        if ch == '\\' and in_string:
            result.append(ch); escape_next = True; i += 1; continue
        if ch == '"':
            if not in_string:
                in_string = True; result.append(ch)
            else:
                j = i + 1
                while j < n and chars[j] in ' \t\r\n':
                    j += 1
                next_nws = chars[j] if j < n else ''
                if next_nws in (':', ',', '}', ']', ''):
                    in_string = False; result.append(ch)
                else:
                    result.append('\\"')
            i += 1; continue
        if in_string:
            if ch == '\n':         result.append('\\n')
            elif ch == '\r':       result.append('\\r')
            elif ch == '\t':       result.append('\\t')
            elif ord(ch) < 0x20:  result.append(f'\\u{ord(ch):04x}')
            else:                  result.append(ch)
        else:
            result.append(ch)
        i += 1
    return ''.join(result)


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
        "transformers>=4.49.0",         # 4.49+ required for Qwen2.5-VL support
        "torch>=2.2.0",
        "torchvision>=0.17.0",
        "Pillow>=10.0.0",
        "opencv-python-headless>=4.9.0",
        "numpy",
        "huggingface_hub",
        "accelerate>=0.26.0",
        "qwen-vl-utils>=0.0.8",         # multi-image preprocessing for Qwen2.5-VL
        "google-genai>=1.5.0,<2.0.0",  # pin minor — >2.0 has breaking API changes
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
    One-time setup: downloads YOLO + CLIP + Qwen2.5-VL-7B weights into the Modal Volume.
    Run once with: modal run workers/inference.py::download_models
    After this, containers read from the volume — no internet needed per inference.

    Model sizes:
      YOLOv11-L       ~  140 MB
      CLIP ViT-L/14   ~  890 MB
      Qwen2.5-VL-7B   ~ 15.5 GB  (BF16)
    """
    import os, shutil, glob
    os.environ["HF_HOME"]            = MODEL_CACHE_DIR
    os.environ["TRANSFORMERS_CACHE"] = MODEL_CACHE_DIR
    os.environ["YOLO_CONFIG_DIR"]    = "/tmp/Ultralytics"

    from ultralytics import YOLO
    from transformers import CLIPModel, CLIPProcessor
    from huggingface_hub import snapshot_download

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

    print(f"⬇️  Qwen2.5-VL-7B-Instruct (~15.5 GB, BF16) — this takes a few minutes...")
    # Use snapshot_download: streams files to disk without loading into CPU RAM.
    # Saves to QWEN_LOCAL_DIR inside the persistent Modal Volume.
    snapshot_download(
        repo_id=QWEN_MODEL_ID,
        local_dir=QWEN_LOCAL_DIR,
        ignore_patterns=["*.msgpack", "*.h5", "original/"],  # skip non-PyTorch formats
    )
    print(f"  ✅ Qwen2.5-VL-7B saved → {QWEN_LOCAL_DIR}")

    model_vol.commit()
    print("✅ All models saved to Modal Volume 'vigilant-model-weights'")
    print("   YOLO + CLIP + Qwen2.5-VL-7B (3 neural networks per GPU container)")


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
        """
        Runs once per container start. Reads all models from Modal Volume.

        Three neural networks loaded onto A100 GPU:
          1. YOLOv11-L          — detection + ByteTrack multi-object tracking
          2. CLIP ViT-L/14      — 768-dim semantic embeddings for vector search
          3. Qwen2.5-VL-7B      — on-device visual reasoning, forensic captioning
        """
        import os
        import torch
        from ultralytics import YOLO
        from transformers import (
            CLIPModel, CLIPProcessor,
            Qwen2_5_VLForConditionalGeneration, AutoProcessor,
        )

        os.environ["HF_HOME"]            = MODEL_CACHE_DIR
        os.environ["TRANSFORMERS_CACHE"] = MODEL_CACHE_DIR
        os.environ["YOLO_CONFIG_DIR"]    = "/tmp/Ultralytics"

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🚀 Container | device={self.device} | gpu={GPU_TYPE}")

        # ── Model 1: YOLO ─────────────────────────────────────────────────────
        self.yolo = YOLO(YOLO_MODEL)
        print("✅ YOLOv11-L")

        # ── Model 2: CLIP ─────────────────────────────────────────────────────
        self.clip_model     = CLIPModel.from_pretrained(
            CLIP_MODEL_ID, cache_dir=MODEL_CACHE_DIR
        ).to(self.device)
        self.clip_processor = CLIPProcessor.from_pretrained(
            CLIP_MODEL_ID, cache_dir=MODEL_CACHE_DIR
        )
        self.clip_model.eval()
        print("✅ CLIP ViT-L/14")

        # ── Model 3: Qwen2.5-VL-7B ───────────────────────────────────────────
        # Prefer the local Modal Volume snapshot when available.
        # If missing, fall back to Hugging Face Hub repo id.
        qwen_source = QWEN_LOCAL_DIR if os.path.isdir(QWEN_LOCAL_DIR) else QWEN_MODEL_ID
        qwen_load_kwargs = {"local_files_only": True} if qwen_source == QWEN_LOCAL_DIR else {}
        print(f"🔎 Qwen source: {qwen_source}")

        # Loaded in BF16 — uses ~15.5 GB VRAM. Total with YOLO+CLIP: ~19 GB / 40 GB A100.
        # SDPA attention (PyTorch built-in) — no flash-attn compilation needed.
        self.qwen_model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            qwen_source,
            torch_dtype=torch.bfloat16,
            attn_implementation="sdpa",
            device_map="cuda",
            cache_dir=MODEL_CACHE_DIR,
            **qwen_load_kwargs,
        )
        # min/max_pixels caps the token budget per image frame.
        # 640*28*28 ≈ 501K pixels → ~640 tokens/image → 8 frames = ~5120 image tokens total.
        self.qwen_processor = AutoProcessor.from_pretrained(
            qwen_source,
            min_pixels=256 * 28 * 28,
            max_pixels=640 * 28 * 28,
            cache_dir=MODEL_CACHE_DIR,
            **qwen_load_kwargs,
        )
        self.qwen_model.eval()
        print(f"✅ Qwen2.5-VL-7B | 🟢 3 models loaded on {GPU_TYPE}")

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

        # ── Keyframes: up to 8 frames, biased toward the action zone ─────────
        # Theft/assault actions typically complete in the last 30-40% of a clip.
        # Uniform 5-frame sampling creates a 2.5s dead gap at 75-100% where
        # the critical grab/strike moment falls and is never seen by Gemini.
        # Fix: add 4 frames densely in the last 35% of the clip.
        n = len(frames)
        if n <= 8:
            kf_indices = list(range(n))
        else:
            kf_indices = sorted(set([
                0,               # 0%  — entry/context
                n // 4,          # 25% — early movement
                n // 2,          # 50% — mid approach
                int(n * 0.65),   # 65% — late approach
                int(n * 0.75),   # 75% — action start
                int(n * 0.85),   # 85% — action peak  (catches grab/strike)
                int(n * 0.93),   # 93% — action completing
                n - 1,           # 100% — final state (object gone?)
            ]))
        kf_pil: List = []
        for ki in kf_indices:
            _, bgr = frames[min(ki, n - 1)]
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
        if vlm_data.get("is_stealing") and not any(h["label"] == "theft_detected" for h in hypotheses):
            hypotheses.insert(0, {"label": "theft_detected", "confidence": 0.85, "severity": "high"})

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

            # Benchmark telemetry — real measured inference times per clip
            "_benchmark": {
                "qwen_inference_ms": vlm_data.get("_qwen_ms", 0),
                "models_on_gpu":     ["yolo11l", "clip-vit-l14", "qwen2.5-vl-7b"],
            },

            "processed_at":   datetime.utcnow().isoformat() + "Z",
            "processing_gpu": GPU_TYPE,
        }

    # ── Private helpers ────────────────────────────────────────────────────────

    def _vlm_caption(self, keyframes: List) -> Dict:
        """
        Dual-model forensic captioning pipeline (runs concurrently on each sub-clip):

          Thread A  →  Qwen2.5-VL-7B  on A100 GPU  (real on-device inference)
          Thread B  →  Gemini 2.5 Pro via API       (high-quality description)

        Both run at the same time — Gemini's network latency overlaps with Qwen's
        GPU compute, so total wall time ≈ max(Qwen_time, Gemini_time), not their sum.

        Merge strategy:
          • description  = Gemini (primary, highest quality) → Qwen if Gemini fails
          • bool flags   = OR-union of both models (max detection sensitivity)
            If either model sees a theft or fight, it's flagged.
        """
        import threading

        _FAIL = {"description": "API error", "is_fighting": False,
                 "is_stealing": False, "is_erratic": False}

        # ── Launch Gemini in background thread ────────────────────────────────
        gemini_result = [_FAIL]
        gemini_done   = threading.Event()

        def _run_gemini():
            try:
                gemini_result[0] = self._vlm_caption_gemini(keyframes)
            except Exception as e:
                print(f"  ⚠️  Gemini thread error: {e}")
            finally:
                gemini_done.set()

        threading.Thread(target=_run_gemini, daemon=True).start()

        # ── Qwen on GPU while Gemini is in-flight ─────────────────────────────
        # This is the real GPU inference — YOLO+CLIP+Qwen all running on A100.
        qwen = self._vlm_caption_qwen(keyframes)

        # ── Wait for Gemini (120s max before giving up) ───────────────────────
        gemini_done.wait(timeout=120)
        gemini = gemini_result[0]

        # ── Merge ─────────────────────────────────────────────────────────────
        gem_desc = gemini.get("description", "")
        description = (
            gem_desc
            if gem_desc and gem_desc.lower() not in ("api error", "api error.", "")
            else qwen.get("description", "API error")
        )

        return {
            "description": description,
            "is_fighting": gemini.get("is_fighting", False) or qwen.get("is_fighting", False),
            "is_stealing": gemini.get("is_stealing", False) or qwen.get("is_stealing", False),
            "is_erratic":  gemini.get("is_erratic",  False) or qwen.get("is_erratic",  False),
            "_qwen_ms":    qwen.get("_inference_ms", 0),
        }

    def _vlm_caption_qwen(self, keyframes: List) -> Dict:
        """
        Qwen2.5-VL-7B-Instruct — on-device A100 GPU inference.
        Sends up to 8 CCTV keyframes through the local 7B vision model.
        Returns structured JSON with boolean flags + brief description.
        This is the Modal GPU compute layer — real transformer inference, no API calls.
        """
        import json, time as _t
        import torch
        from qwen_vl_utils import process_vision_info

        _FAIL = {"description": "", "is_fighting": False,
                 "is_stealing": False, "is_erratic": False, "_inference_ms": 0}

        prompt_text = (
            f"You are a forensic CCTV analyst. You have {len(keyframes)} chronological "
            "keyframes from a 10-second security camera clip.\n\n"
            "OUTPUT ONLY a raw JSON object — no preamble, no markdown, no explanation.\n\n"
            "In the 'description' field write ONE paragraph stating:\n"
            "  (a) What objects are visible on surfaces/tables in the FIRST frame\n"
            "  (b) Exactly what the person's hands do in each frame\n"
            "  (c) Whether any object present in frame 1 is ABSENT in the last frame\n\n"
            "Use precise language: 'picks up black headphones from table' not 'interacts with items'.\n"
            "Set is_stealing=true ONLY IF an object is taken from a table, shelf, counter, or display surface.\n"
            "  Do NOT set is_stealing=true for: picking something up from the floor, person falling,\n"
            "  person helping another person, or any action not involving a retail/display surface.\n"
            "Set is_fighting=true if any person physically strikes, punches, kicks, or assaults another.\n"
            "Set is_erratic=true if movement is sudden, agitated, or unpredictable.\n\n"
            'Output exactly: {"description": "...", "is_stealing": false, '
            '"is_fighting": false, "is_erratic": false}'
        )

        messages = [{
            "role": "user",
            "content": [
                *[{"type": "image", "image": kf} for kf in keyframes],
                {"type": "text", "text": prompt_text},
            ],
        }]

        t0 = _t.time()
        try:
            text_input   = self.qwen_processor.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            image_inputs, video_inputs = process_vision_info(messages)
            inputs = self.qwen_processor(
                text=[text_input],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt",
            ).to(self.device)

            with torch.no_grad():
                output_ids = self.qwen_model.generate(
                    **inputs,
                    max_new_tokens=256,
                    do_sample=False,
                )

            # Decode only the newly generated tokens (not the input prompt)
            generated_ids = [
                out[len(inp):]
                for inp, out in zip(inputs.input_ids, output_ids)
            ]
            raw = self.qwen_processor.batch_decode(
                generated_ids, skip_special_tokens=True,
                clean_up_tokenization_spaces=False,
            )[0].strip()

            elapsed_ms = round((_t.time() - t0) * 1000)
            print(f"  🧠 Qwen2.5-VL: {elapsed_ms}ms | out={raw[:80]}")

            # Extract JSON (safety net if model outputs any preamble)
            bs = raw.find('{')
            be = raw.rfind('}')
            if bs >= 0 and be > bs:
                raw = raw[bs:be + 1]

            result = json.loads(_clean_json_string(raw))
            return {
                "description":   str(result.get("description", "")),
                "is_fighting":   bool(result.get("is_fighting", False)),
                "is_stealing":   bool(result.get("is_stealing", False)),
                "is_erratic":    bool(result.get("is_erratic",  False)),
                "_inference_ms": elapsed_ms,
            }

        except Exception as e:
            elapsed_ms = round((_t.time() - t0) * 1000)
            print(f"  ⚠️  Qwen inference error ({type(e).__name__}): {e}")
            return {**_FAIL, "_inference_ms": elapsed_ms}

    def _vlm_caption_gemini(self, keyframes: List) -> Dict:
        """
        Gemini 2.5 Pro Vision API — high-quality forensic caption.
        Called from _vlm_caption() in a background thread while Qwen runs on GPU.
        Returns parsed JSON dict with 'description' and boolean flags.
        """
        import io, json
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=GEMINI_API_KEY)

        prompt_text = (
            f"You are a Forensic Video Analyst. You have {len(keyframes)} CCTV keyframes in chronological order.\n\n"
            "OUTPUT ONLY a raw JSON object. No preamble, no steps text, no markdown, no explanation outside the JSON.\n\n"
            "In the 'description' field encode ALL of the following in one coherent paragraph:\n"
            "  (a) What objects are visible on tables/surfaces in the FIRST frame (e.g. 'black headphones on table')\n"
            "  (b) What the person's hands do in each frame — any reaching, touching, grabbing, pocketing, striking\n"
            "  (c) Whether any surface object from the first frame is ABSENT in the last frame and was taken\n\n"
            "Naming rules (non-negotiable):\n"
            "  - 'picks up headphones from table' NOT 'interacts with items'\n"
            "  - 'officer punches prone detainee' NOT 'officer applies force'\n"
            "  - If any object is missing in the last frame that was present in the first, state it was taken\n\n"
            "Set is_stealing=true ONLY IF an object is removed from a table, shelf, counter, or display surface.\n"
            "  Do NOT set is_stealing=true for: picking something up from the floor, person falling,\n"
            "  someone helping another person up, or any action not involving a retail/display surface.\n"
            "Set is_fighting=true if any person physically strikes, punches, kicks, or assaults another.\n\n"
            'Output exactly: {"description": "...", "is_fighting": true_or_false, "is_stealing": true_or_false, "is_erratic": true_or_false}'
        )

        # Build parts: JPEG images first, then text prompt
        parts = []
        for kf in keyframes:
            buf = io.BytesIO()
            kf.save(buf, format="JPEG", quality=85)
            parts.append(types.Part.from_bytes(data=buf.getvalue(), mime_type="image/jpeg"))
        parts.append(types.Part.from_text(text=prompt_text))

        # ── Retry loop: exponential backoff for rate limits + transient errors ──
        # Root cause of intermittent "API error": Modal fires ALL sub-clip containers
        # in parallel via .map(). Every container finishes YOLO+CLIP at the same
        # moment and hammers Gemini simultaneously. gemini-2.5-pro free tier = 5 RPM.
        # 11 sub-clips → 6 instantly fail with 429. Fix: jitter + retry.
        import time as _time, random as _random, traceback as _tb

        _FAIL = {"description": "API error", "is_fighting": False,
                 "is_stealing": False, "is_erratic": False}

        # Initial jitter: spread parallel container calls over 0-5s so they
        # don't all slam Gemini at the same millisecond.
        _time.sleep(_random.uniform(0, 5))

        MAX_RETRIES = 4
        raw = ""
        _last_exc = None

        for _attempt in range(MAX_RETRIES):
            try:
                print(f"  🔑 Gemini (attempt {_attempt+1}/{MAX_RETRIES}) "
                      f"key=...{GEMINI_API_KEY[-6:]} model={GEMINI_MODEL_ID}")
                response = client.models.generate_content(
                    model=GEMINI_MODEL_ID,
                    contents=parts,
                    config=types.GenerateContentConfig(
                        temperature=0.1,
                        max_output_tokens=8192,  # gemini-2.5-pro uses thinking tokens; 1024 truncates JSON
                    ),
                )
                raw = (response.text or "").strip()
                if not raw:
                    try:
                        finish = response.candidates[0].finish_reason if response.candidates else "unknown"
                        print(f"  ⚠️ Gemini empty response (finish_reason={finish}) — safety filter")
                    except Exception:
                        print(f"  ⚠️ Gemini empty response — safety filter")
                    return _FAIL
                break  # ← success
            except Exception as _e:
                _last_exc = _e
                _err = str(_e)
                _rate_limited = "429" in _err or "RESOURCE_EXHAUSTED" in _err or "quota" in _err.lower()
                _server_err   = any(x in _err for x in ("500", "502", "503", "overloaded"))
                _network_err  = any(x in _err.lower() for x in ("timeout", "timed out", "connection", "ssl", "errno", "socket", "reset"))

                if _attempt < MAX_RETRIES - 1 and (_rate_limited or _server_err or _network_err):
                    # Rate limit: wait longer (15s base × 2^attempt). Server error: 4s base.
                    _backoff = (2 ** _attempt) * (15 if _rate_limited else 4) + _random.uniform(1, 4)
                    print(f"  ⚠️ Gemini {'rate-limited' if _rate_limited else 'server error'} "
                          f"(attempt {_attempt+1}/{MAX_RETRIES}) — retry in {_backoff:.1f}s")
                    _time.sleep(_backoff)
                else:
                    # Non-retryable (403 bad key, 404 bad model) or all retries used
                    print(f"  ❌ Gemini failed ({type(_e).__name__}): {_e}")
                    print(_tb.format_exc())
                    return _FAIL
        else:
            # for-loop completed without break → all retries exhausted
            print(f"  ❌ Gemini: all {MAX_RETRIES} attempts failed. Last: {_last_exc}")
            return _FAIL

        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw.rsplit("```", 1)[0]
        if raw.lstrip().startswith("json"):
            raw = raw.lstrip()[4:]
        raw = raw.strip()

        # Safety net: if preamble text slipped through, extract the JSON object
        # e.g. Gemini outputs "Step 1: ...\n\n{...}" — grab from first { to last }
        brace_start = raw.find('{')
        brace_end   = raw.rfind('}')
        if brace_start > 0 and brace_end > brace_start:
            raw = raw[brace_start:brace_end + 1]

        try:
            cleaned = _clean_json_string(raw)
            result = json.loads(cleaned)
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
def main(video_path: str = "C:/Users/galga/Documents/GitHub/vigilant-ai_MVP/backend/uploads/galo.mp4"):
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
