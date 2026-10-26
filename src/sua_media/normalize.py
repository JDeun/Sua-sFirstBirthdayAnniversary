"""Normalize private local media into deterministic SDR/CFR editing assets.

Never overwrites originals. Requires ffmpeg and ffprobe installed locally.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from .preflight import AUDIO_EXT, IMAGE_EXT, VIDEO_EXT, inspect


def normalize(source: Path, output_dir: Path) -> Path:
    source = source.expanduser().resolve()
    report = inspect(source)
    if report["status"] != "ok":
        raise ValueError(f"미디어 검사 실패: {source.name}: {report['warnings']}")
    kind = ("video" if source.suffix.lower() in VIDEO_EXT else
            "audio" if source.suffix.lower() in AUDIO_EXT else "image")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    ext = {"video": ".mp4", "audio": ".wav", "image": ".png"}[kind]
    destination = output_dir.resolve() / (digest + ext)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size > 0:
        return destination
    temporary = destination.with_name(destination.stem + ".partial" + destination.suffix)
    # Input options precede -i. Autorotation is enabled by FFmpeg by default.
    command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y", "-i", str(source)]
    if kind == "video":
        hdr = any("HDR" in warning for warning in report["warnings"])
        if hdr:
            video_filter = ("zscale=t=linear:npl=100,format=gbrpf32le,"
                            "tonemap=tonemap=hable:desat=0,"
                            "zscale=p=bt709:t=bt709:m=bt709:r=tv,format=yuv420p,fps=30")
        else:
            video_filter = "fps=30,format=yuv420p"
        command += ["-map", "0:v:0", "-map", "0:a:0?", "-vf", video_filter,
                    "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                    "-pix_fmt", "yuv420p", "-colorspace", "bt709",
                    "-color_primaries", "bt709", "-color_trc", "bt709",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                    "-movflags", "+faststart", str(temporary)]
    elif kind == "audio":
        command += ["-map", "0:a:0", "-vn", "-c:a", "pcm_s16le", "-ar", "48000",
                    "-ac", "2", str(temporary)]
    else:
        command += ["-frames:v", "1", "-update", "1", str(temporary)]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True, timeout=900)
        if not temporary.is_file() or temporary.stat().st_size == 0:
            raise ValueError(f"변환 결과가 비어 있습니다: {source.name}")
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description="Private local media normalization; originals untouched")
    parser.add_argument("sources", nargs="+", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    files = [item for path in args.sources
             for item in (sorted(p for p in path.rglob("*") if p.is_file()) if path.is_dir() else [path])]
    records = []
    failures = 0
    for source in files:
        try:
            result = normalize(source, args.output_dir)
            records.append({"source": str(source), "normalized": str(result), "status": "ok"})
        except (ValueError, OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            failures += 1
            records.append({"source": str(source), "status": "error", "reason": str(exc)})
    output = json.dumps({"files": records, "errors": failures}, ensure_ascii=False, indent=2)
    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(output, encoding="utf-8")
    else:
        print(output)
    sys.exit(bool(failures))


if __name__ == "__main__":
    main()
