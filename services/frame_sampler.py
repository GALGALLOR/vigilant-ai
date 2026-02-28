#Samples multiple frames to be used by Inference Models

import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any, Optional


@dataclass
class FrameInfo:
    frame_index: int
    timestamp_sec: float
    file_path: str


class FrameSampler:
    """
    Samples frames from a video using ffmpeg.

    - interval_sec: sample every N seconds (e.g., 2.0)
    - optional start/end to sample within a window
    """

    def __init__(
        self,
        ffmpeg_path: str,
        interval_sec: float = 2.0,
        image_ext: str = "jpg",
        jpeg_quality: int = 2,  # 2=high quality, 31=low quality (ffmpeg scale)
    ):
        self.ffmpeg = ffmpeg_path
        self.interval_sec = float(interval_sec)
        self.image_ext = image_ext.lower().strip(".")
        self.jpeg_quality = int(jpeg_quality)

        if self.interval_sec <= 0:
            raise ValueError("interval_sec must be > 0")

    def sample_frames(
        self,
        video_path: str,
        output_dir: str,
        start_sec: Optional[float] = None,
        end_sec: Optional[float] = None,
        prefix: str = "frame",
    ) -> Dict[str, Any]:
        """
        Extract frames at a fixed interval.

        Returns JSON:
          {
            "video_path": "...",
            "output_dir": "...",
            "interval_sec": 2.0,
            "start_sec": 0.0,
            "end_sec": 300.0,
            "frames": [{frame_index, timestamp_sec, file_path}, ...]
          }
        """
        vpath = Path(video_path).resolve()
        if not vpath.exists():
            raise FileNotFoundError(f"Video not found: {vpath}")

        out_dir = Path(output_dir).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)

        # Output pattern (ffmpeg will write frame_000001.jpg, etc.)
        pattern = str(out_dir / f"{prefix}_%06d.{self.image_ext}")

        cmd = [self.ffmpeg, "-y"]

        # Optional window cropping
        if start_sec is not None:
            cmd += ["-ss", f"{float(start_sec):.3f}"]

        cmd += ["-i", str(vpath)]

        if end_sec is not None and start_sec is not None:
            dur = max(0.0, float(end_sec) - float(start_sec))
            cmd += ["-t", f"{dur:.3f}"]
        elif end_sec is not None and start_sec is None:
            # If only end given, interpret as duration from start=0
            cmd += ["-t", f"{float(end_sec):.3f}"]

        # Sample frames every interval_sec:
        # fps = 1/interval_sec
        fps = 1.0 / self.interval_sec

        # Filters:
        # -vf fps=... extracts frames at fixed rate
        vf = f"fps={fps}"

        cmd += [
            "-vf", vf,
            "-vsync", "vfr",
        ]

        # Quality control for jpg
        if self.image_ext in ("jpg", "jpeg"):
            cmd += ["-q:v", str(self.jpeg_quality)]

        cmd += [pattern]

        # Run ffmpeg
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Collect generated frames and compute timestamps
        # Since we sample at fixed interval, timestamps are:
        # t = start_sec + frame_index * interval_sec
        frames: List[FrameInfo] = []
        files = sorted(out_dir.glob(f"{prefix}_*.{self.image_ext}"))

        # Determine base start (for returned timestamps)
        base = float(start_sec) if start_sec is not None else 0.0

        for idx, fp in enumerate(files):
            ts = base + idx * self.interval_sec
            frames.append(FrameInfo(frame_index=idx, timestamp_sec=ts, file_path=str(fp)))

        return {
            "video_path": str(vpath),
            "output_dir": str(out_dir),
            "interval_sec": self.interval_sec,
            "start_sec": float(start_sec) if start_sec is not None else 0.0,
            "end_sec": float(end_sec) if end_sec is not None else None,
            "frames": [asdict(f) for f in frames],
        }
    
if __name__ == "__main__":
    from pathlib import Path

    FFMPEG_BIN = r"C:\Users\galga\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin"
    FFMPEG = str(Path(FFMPEG_BIN) / "ffmpeg.exe")

    sampler = FrameSampler(ffmpeg_path=FFMPEG, interval_sec=2.0)

    result = sampler.sample_frames(
        video_path=r"C:\Users\galga\Documents\GitHub\vigilant-ai\clips_out\Abuse001\clip_0000_000000_000090.mp4",
        output_dir="C:/Users/galga/Documents/GitHub/vigilant-ai/frames/clip_0000",
        start_sec=0,
        end_sec=300,
        prefix="t",
    )

    import json
    print(json.dumps(result, indent=2))