"""Local-only media preflight. Does not copy or upload private originals."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}
VIDEO_EXT = {".mp4", ".mov", ".m4v"}
AUDIO_EXT = {".wav", ".mp3", ".m4a", ".aac"}


def inspect(path: Path) -> dict:
    result = {"path": str(path), "status": "ok", "warnings": []}
    if not path.is_file():
        return {**result, "status": "error", "warnings": ["file missing"]}
    suffix = path.suffix.lower()
    if suffix not in IMAGE_EXT | VIDEO_EXT | AUDIO_EXT:
        return {**result, "status": "error", "warnings": ["unsupported extension"]}
    if path.stat().st_size == 0:
        return {**result, "status": "error", "warnings": ["empty file"]}
    if suffix in IMAGE_EXT:
        if suffix in {".heic", ".heif"}:
            result["warnings"].append("HEIC requires local conversion to JPEG/PNG before film preparation")
        return result
    try:
        completed = subprocess.run(
            ["ffprobe", "-v", "error", "-show_streams", "-show_format",
             "-of", "json", str(path)],
            capture_output=True, text=True, check=True, timeout=30,
        )
        metadata = json.loads(completed.stdout)
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired, ValueError) as exc:
        return {**result, "status": "error", "warnings": [f"ffprobe failed: {type(exc).__name__}"]}
    streams = metadata.get("streams", [])
    kind = "video" if suffix in VIDEO_EXT else "audio"
    matches = [s for s in streams if s.get("codec_type") == kind]
    if not matches:
        return {**result, "status": "error", "warnings": [f"no {kind} stream"]}
    if kind == "video":
        stream = matches[0]
        result["codec"] = stream.get("codec_name")
        result["width"] = stream.get("width")
        result["height"] = stream.get("height")
        result["rotation"] = next((s.get("rotation") for s in stream.get("side_data_list", []) if "rotation" in s), 0)
        if stream.get("avg_frame_rate") != stream.get("r_frame_rate"):
            result["warnings"].append("possible variable frame rate; normalize to constant 30fps")
        if stream.get("color_transfer") in {"smpte2084", "arib-std-b67"}:
            result["warnings"].append("HDR footage; tone-map to SDR for consistent output")
        if result["rotation"]:
            result["warnings"].append("rotation metadata; verify orientation")
    result["duration_seconds"] = metadata.get("format", {}).get("duration")
    return result


def preflight(paths: list[Path]) -> dict:
    records = [inspect(p) for p in paths]
    return {"files": records, "errors": sum(r["status"] == "error" for r in records),
            "warnings": sum(len(r["warnings"]) for r in records)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Private local media preflight; no uploads")
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    paths = [file for p in args.paths for file in (sorted(p.rglob("*")) if p.is_dir() else [p]) if file.is_file() or not p.is_dir()]
    report = preflight(paths)
    output = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output, encoding="utf-8")
    else:
        print(output)
    sys.exit(1 if report["errors"] else 0)


if __name__ == "__main__":
    main()
