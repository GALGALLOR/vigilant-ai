import math
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any, Optional


@dataclass
class MiniClipInfo:
    parent_clip_index: int
    mini_index: int
    start_sec: float
    end_sec: float
    duration_sec: float
    parent_file_path: str
    mini_file_path: Optional[str]  # None if not cutting files
    json_path: Optional[str]       # None if not writing json files


class MiniClipGenerator:
    """
    Splits a parent clip into overlapping mini-clips (e.g., 10s length, 2s stride).
    Example (length=10, stride=2):
      [0-10], [2-12], [4-14], ...
    """

    def __init__(
        self,
        ffmpeg_path: str,
        mini_length_sec: float = 10.0,
        stride_sec: float = 2.0,
        cut_files: bool = True,
        exact_cuts: bool = False,
        write_json_files: bool = True,
    ):
        self.ffmpeg = ffmpeg_path
        self.mini_length_sec = float(mini_length_sec)
        self.stride_sec = float(stride_sec)
        self.cut_files = bool(cut_files)
        self.exact_cuts = bool(exact_cuts)
        self.write_json_files = bool(write_json_files)

        if self.mini_length_sec <= 0:
            raise ValueError("mini_length_sec must be > 0")
        if self.stride_sec <= 0:
            raise ValueError("stride_sec must be > 0")

    def _cut_with_ffmpeg(self, input_path: Path, output_path: Path, start: float, end: float) -> None:
        duration = max(0.0, end - start)

        if self.exact_cuts:
            cmd = [
                self.ffmpeg, "-y",
                "-ss", f"{start:.3f}",
                "-i", str(input_path),
                "-t", f"{duration:.3f}",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
                "-c:a", "aac", "-b:a", "128k",
                str(output_path),
            ]
        else:
            cmd = [
                self.ffmpeg, "-y",
                "-ss", f"{start:.3f}",
                "-i", str(input_path),
                "-t", f"{duration:.3f}",
                "-c", "copy",
                str(output_path),
            ]

        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def generate(
        self,
        parent_clip_index: int,
        parent_clip_path: str,
        parent_duration_sec: float,
        output_dir: str,
    ) -> Dict[str, Any]:
        """
        Generates mini-clips for a given parent clip.

        Returns:
          {
            "parent_clip_index": int,
            "parent_clip_path": str,
            "parent_duration_sec": float,
            "mini_length_sec": float,
            "stride_sec": float,
            "miniclips": [ ...MiniClipInfo dicts... ]
          }
        """
        parent_path = Path(parent_clip_path).resolve()
        if not parent_path.exists():
            raise FileNotFoundError(f"Parent clip not found: {parent_path}")

        out_dir = Path(output_dir).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)

        miniclips: List[MiniClipInfo] = []

        # Generate windows until start exceeds duration
        mini_index = 0
        start = 0.0

        # stop condition: when start >= parent_duration_sec
        while start < parent_duration_sec:
            end = start + self.mini_length_sec
            if end > parent_duration_sec:
                # clamp end to parent duration
                end = parent_duration_sec

            # ensure duration positive
            dur = max(0.0, end - start)
            if dur <= 0:
                break

            mini_file_path = None
            json_path = None

            if self.cut_files:
                mini_name = f"parent_{parent_clip_index:04d}_mini_{mini_index:04d}_{int(start*1000):010d}_{int(end*1000):010d}.mp4"
                mini_out = out_dir / mini_name
                self._cut_with_ffmpeg(parent_path, mini_out, start, end)
                mini_file_path = str(mini_out)

            mini_info = MiniClipInfo(
                parent_clip_index=parent_clip_index,
                mini_index=mini_index,
                start_sec=float(start),
                end_sec=float(end),
                duration_sec=float(dur),
                parent_file_path=str(parent_path),
                mini_file_path=mini_file_path,
                json_path=None,
            )

            # Write JSON per mini-clip if requested
            if self.write_json_files:
                json_name = f"parent_{parent_clip_index:04d}_mini_{mini_index:04d}.json"
                json_out = out_dir / json_name
                json_out.write_text(
                    _pretty_json(asdict(mini_info)),
                    encoding="utf-8"
                )
                mini_info.json_path = str(json_out)

            miniclips.append(mini_info)

            mini_index += 1
            start += self.stride_sec

            # If we've reached the end exactly, we can stop
            if math.isclose(start, parent_duration_sec, rel_tol=0.0, abs_tol=1e-6):
                break

        return {
            "parent_clip_index": parent_clip_index,
            "parent_clip_path": str(parent_path),
            "parent_duration_sec": float(parent_duration_sec),
            "mini_length_sec": self.mini_length_sec,
            "stride_sec": self.stride_sec,
            "cut_files": self.cut_files,
            "exact_cuts": self.exact_cuts,
            "miniclips": [asdict(m) for m in miniclips],
        }


def _pretty_json(obj: Any) -> str:
    import json
    return json.dumps(obj, indent=2, ensure_ascii=False)

# Suppose you already created a 5-min parent clip:
parent_clip_path = "C:/.../clips_out/clip_0000_000000_000300.mp4"
parent_duration_sec = 300.0

mini = MiniClipGenerator(
    ffmpeg_path=FFMPEG,       # your resolved ffmpeg path
    mini_length_sec=10.0,
    stride_sec=2.0,
    cut_files=True,
    exact_cuts=False,
    write_json_files=True,
)

result = mini.generate(
    parent_clip_index=0,
    parent_clip_path=parent_clip_path,
    parent_duration_sec=parent_duration_sec,
    output_dir="C:/.../clips_out/miniclips/clip_0000",
)

print(result["miniclips"][0])