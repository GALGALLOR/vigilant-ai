import os
import json
import math
import shutil
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional
from config import load_config
from pathlib import Path

cfg = load_config()

@dataclass
class ClipInfo:
    clip_index: int
    start_sec: float
    end_sec: float
    duration_sec: float
    file_path: str

class VideoChunker:
    """
    Chunk uploaded videos into fixed segments using ffmpeg/ffprobe.

    Online: install ffmpeg in your container/image and PATH will work.
    Local Windows: either ensure ffmpeg is on PATH OR set FFMPEG_BIN env var.
    """







    def __init__(
        self,
        uploads_dir: str = "./uploads",
        clips_dir: str = "./clips_out",
        chunk_minutes: int = 5,
        exact_cuts: bool = False,
        ffmpeg_path: Optional[str] = None,
        ffprobe_path: Optional[str] = None,
    ):
        self.uploads_dir = Path(uploads_dir).resolve()
        self.clips_dir = Path(clips_dir).resolve()
        self.chunk_minutes = chunk_minutes
        self.exact_cuts = exact_cuts

        # 1) Prefer explicit paths (passed in)
        # 2) Else use env var FFMPEG_BIN
        # 3) Else fall back to PATH lookup (online best)
        ffmpeg_bin = os.getenv("FFMPEG_BIN")

        if ffmpeg_path and ffprobe_path:
            self.ffmpeg = ffmpeg_path
            self.ffprobe = ffprobe_path
        elif ffmpeg_bin:
            self.ffmpeg = str(Path(ffmpeg_bin) / "ffmpeg.exe" if os.name == "nt" else Path(ffmpeg_bin) / "ffmpeg")
            self.ffprobe = str(Path(ffmpeg_bin) / "ffprobe.exe" if os.name == "nt" else Path(ffmpeg_bin) / "ffprobe")
        else:
            self.ffmpeg = shutil.which("ffmpeg") or ""
            self.ffprobe = shutil.which("ffprobe") or ""

        if not self.ffmpeg or not Path(self.ffmpeg).exists() and os.name == "nt":
            # On Windows, shutil.which may fail if not in PATH; handle gracefully
            raise RuntimeError(
                "ffmpeg not found. Install FFmpeg or set env var FFMPEG_BIN to its bin folder."
            )
        if not self.ffprobe or not Path(self.ffprobe).exists() and os.name == "nt":
            raise RuntimeError(
                "ffprobe not found. Install FFmpeg or set env var FFMPEG_BIN to its bin folder."
            )

        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.clips_dir.mkdir(parents=True, exist_ok=True)

    def ffprobe_duration_sec(self, video_path: Path) -> float:
        cmd = [
            self.ffprobe,
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video_path),
        ]
        out = subprocess.check_output(cmd, text=True).strip()
        return float(out)

    def chunk_ranges(self, duration_sec: float, chunk_sec: int) -> List[tuple]:
        if duration_sec <= 0 or chunk_sec <= 0:
            return []
        num = math.ceil(duration_sec / chunk_sec)
        return [(i * chunk_sec, min(duration_sec, (i + 1) * chunk_sec)) for i in range(num)]

    def cut_clip(self, input_path: Path, output_path: Path, start_sec: float, end_sec: float) -> None:
        duration = max(0.0, end_sec - start_sec)

        if self.exact_cuts:
            cmd = [
                self.ffmpeg, "-y",
                "-ss", f"{start_sec:.3f}",
                "-i", str(input_path),
                "-t", f"{duration:.3f}",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
                "-c:a", "aac", "-b:a", "128k",
                str(output_path),
            ]
        else:
            cmd = [
                self.ffmpeg, "-y",
                "-ss", f"{start_sec:.3f}",
                "-i", str(input_path),
                "-t", f"{duration:.3f}",
                "-c", "copy",
                str(output_path),
            ]

        subprocess.run(cmd, check=True)

    def chunk_uploaded_video(self, filename: str) -> dict:
        """
        filename should exist inside uploads_dir (e.g., user uploaded to ./uploads/file.mp4)
        """
        input_path = (self.uploads_dir / filename).resolve()

        if not input_path.exists():
            raise FileNotFoundError(f"Uploaded video not found: {input_path}")

        duration_sec = self.ffprobe_duration_sec(input_path)
        chunk_sec = self.chunk_minutes * 60
        ranges = self.chunk_ranges(duration_sec, chunk_sec)

        out_subdir = self.clips_dir / input_path.stem
        out_subdir.mkdir(parents=True, exist_ok=True)

        clips: List[ClipInfo] = []
        for i, (start, end) in enumerate(ranges):
            clip_name = f"clip_{i:04d}_{int(start):06d}_{int(end):06d}.mp4"
            clip_path = out_subdir / clip_name

            self.cut_clip(input_path, clip_path, start, end)

            clips.append(
                ClipInfo(
                    clip_index=i,
                    start_sec=float(start),
                    end_sec=float(end),
                    duration_sec=float(end - start),
                    file_path=str(clip_path),
                )
            )

        return {
            "input_video": str(input_path),
            "duration_sec": duration_sec,
            "chunk_minutes": self.chunk_minutes,
            "chunk_sec": chunk_sec,
            "exact_cuts": self.exact_cuts,
            "clips_dir": str(out_subdir),
            "clips": [asdict(c) for c in clips],
        }


if __name__ == "__main__":
    chunker = VideoChunker(
        uploads_dir=cfg.uploads_dir,
        clips_dir=cfg.clips_dir,
        chunk_minutes=cfg.chunk_minutes,
        exact_cuts=cfg.exact_cuts,
    )

    # If you want to force ffmpeg paths from the bin:
    if cfg.ffmpeg_bin:
        chunker.ffmpeg = str(Path(cfg.ffmpeg_bin) / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg"))
        chunker.ffprobe = str(Path(cfg.ffmpeg_bin) / ("ffprobe.exe" if os.name == "nt" else "ffprobe"))


    # Put the uploaded mp4 into ./uploads first (or your API saves it there)
    result = chunker.chunk_uploaded_video("longvid.mp4")
    print(json.dumps(result, indent=2))

