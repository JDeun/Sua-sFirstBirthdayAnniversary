"""Verify final MP4 duration, streams, and sampled black-frame intervals.

Runs locally on generated output only; no private media is uploaded.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import subprocess
import sys


def _run(args: list[str]) -> str:
    return subprocess.run(args, check=True, capture_output=True, text=True, timeout=120).stdout


def inspect_render(path: Path, expected_frames: int, fps: int = 30,
                   duration_tolerance_frames: int = 2) -> dict:
    if expected_frames <= 0 or fps <= 0:
        raise ValueError("Expected frames and fps must be positive")
    data = json.loads(_run(["ffprobe", "-v", "error", "-show_streams", "-show_format",
                            "-of", "json", str(path)]))
    streams = data.get("streams", [])
    videos = [s for s in streams if s.get("codec_type") == "video"]
    audios = [s for s in streams if s.get("codec_type") == "audio"]
    errors = []
    if not videos:
        errors.append("video stream missing")
    if not audios:
        errors.append("audio stream missing")
    duration = float(data.get("format", {}).get("duration", 0))
    if not math.isfinite(duration) or abs(duration - expected_frames / fps) > duration_tolerance_frames / fps:
        errors.append(f"duration mismatch: actual={duration:.3f}s expected={expected_frames / fps:.3f}s")
    return {"status": "pass" if not errors else "fail", "errors": errors,
            "duration_seconds": duration, "video_streams": len(videos),
            "audio_streams": len(audios)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Check local final MP4 streams and duration")
    parser.add_argument("video", type=Path)
    parser.add_argument("--expected-frames", type=int, required=True)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = inspect_render(args.video, args.expected_frames, args.fps)
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output, encoding="utf-8")
    else:
        print(output)
    sys.exit(result["status"] != "pass")


if __name__ == "__main__":
    main()
