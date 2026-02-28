# config.py
import os
from dataclasses import dataclass
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()  # reads .env

@dataclass(frozen=True)
class AppConfig:
    ffmpeg_bin: str | None
    uploads_dir: str
    clips_dir: str
    chunk_minutes: int
    exact_cuts: bool

def load_config() -> AppConfig:
    ffmpeg_bin = os.getenv("FFMPEG_BIN")

    uploads_dir = os.getenv("UPLOADS_DIR", "./uploads")
    clips_dir = os.getenv("CLIPS_DIR", "./clips_out")
    chunk_minutes = int(os.getenv("CHUNK_MINUTES", "5"))

    exact_str = os.getenv("EXACT_CUTS", "false").lower().strip()
    exact_cuts = exact_str in ("1", "true", "yes", "y")

    return AppConfig(
        ffmpeg_bin=ffmpeg_bin,
        uploads_dir=str(Path(uploads_dir)),
        clips_dir=str(Path(clips_dir)),
        chunk_minutes=chunk_minutes,
        exact_cuts=exact_cuts,
    )