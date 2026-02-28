# vigilant-ai

AI video analytics pipeline orchestrated locally and executed on Modal for Human Safety, Dog Safety, and Anti-Theft detection.

## What it does
- Uploads local MP4 to Modal Volume `vigilant-videos`
- Splits input into **5-minute chunks** (CPU workers)
- Detects motion windows and creates **10s subclips** with 2s overlap
- Runs GPU inference per subclip (YOLO + CLIP scaffold + Qwen2-VL model reference) with expanded keyword-driven inference for human/dog/antitheft scenes
- Produces:
  - `results/events.json` (full events, includes `_clip_embedding` + `_track_trajectories`)
  - `results/alerts.json` (heavy fields stripped)
- Optionally indexes events into Actian VectorDB for similarity retrieval

## Tech choices
- Modal GPU: **A100**
- YOLO weights path: `/models/yolo11l.pt`
- Caption model: `Qwen/Qwen2-VL-7B-Instruct`
- Model cache volume: `vigilant-model-weights`

## Repository layout
```
workers/
  inference.py
  pipeline.py
  models.py
api/
  server.py
tests/
  test_pipeline.py
scripts/
results/
```

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
modal setup
```

## Run pipeline
```bash
modal run workers/inference.py::run_pipeline --input-video /path/to/video.mp4
```

## Warm model cache (optional)
```bash
modal run workers/inference.py::download_models
```

## Run API
```bash
uvicorn api.server:app --reload --port 8000
```

Routes:
- `GET /health`
- `GET /runs/latest`
- `GET /runs/latest/events`
- `GET /runs/latest/alerts`
- `POST /run` (multipart MP4 upload)

## Tests
```bash
pytest -q
```

## Troubleshooting
- **Missing Modal auth:** rerun `modal setup`.
- **Model cache issues:** ensure `vigilant-model-weights` exists and mounts at `/models`.
- **No events output:** input may be static or rejected by quality gate (`quality_score < 0.08`).
- **Actian indexing skipped:** pipeline continues even if VectorDB package/endpoint is unavailable.
- **Modal image build failure for `actian-vector`:** not required for this pipeline image; Actian integration remains optional via backend-side `cortex` client setup.


## Domain labels
- Human safety: handshake, hug, helping_gesture, aggressive_behavior, physical_altercation, weapon_detected, person_fallen, medical_emergency, person_in_distress, intruder_detected, after_hours_activity
- Dog safety: dog_playing, dog_aggression, dog_fight, dog_injury_risk, dog_in_distress, dog_leash_incident, dog_left_in_hot_area
- Anti-theft: theft_suspected, shoplifting_suspected, package_theft, vehicle_break_in, snatch_and_run, tampering_detected, suspicious_loitering
