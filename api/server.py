from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI, File, HTTPException, UploadFile

RESULTS_DIR = Path("results")
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Vigilant AI API")


def _read_json(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/runs/latest")
def latest_summary() -> Dict[str, Any]:
    events = _read_json(RESULTS_DIR / "events.json")
    alerts = _read_json(RESULTS_DIR / "alerts.json")
    return {
        "event_count": len(events),
        "alert_count": len(alerts),
        "top_alerts": alerts[:5],
    }


@app.get("/runs/latest/events")
def latest_events() -> List[Dict[str, Any]]:
    events = _read_json(RESULTS_DIR / "events.json")
    for event in events:
        event.pop("_clip_embedding", None)
        event.pop("_track_trajectories", None)
    return events


@app.get("/runs/latest/alerts")
def latest_alerts() -> List[Dict[str, Any]]:
    return _read_json(RESULTS_DIR / "alerts.json")


@app.post("/run")
async def run(file: UploadFile = File(...)) -> Dict[str, Any]:
    if not file.filename.lower().endswith(".mp4"):
        raise HTTPException(status_code=400, detail="only mp4 accepted")

    output_path = UPLOAD_DIR / file.filename
    output_path.write_bytes(await file.read())

    cmd = ["modal", "run", "workers/inference.py::run_pipeline", "--input-video", str(output_path)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise HTTPException(status_code=500, detail=proc.stderr[-500:])

    return {"status": "completed", "file": file.filename, "stdout": proc.stdout[-500:]}
