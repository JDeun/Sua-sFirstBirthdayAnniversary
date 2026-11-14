#!/usr/bin/env python3
"""Catalog local photos/videos with capture metadata and SHA-256; no mtime dating."""
import argparse
from datetime import datetime
from fractions import Fraction
from pathlib import Path

from filmtools.endpoints import probe
from filmtools.paths import sha256, unique_names, within, write_json

PHOTOS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp", ".heic", ".heif"}
VIDEOS = {".mp4", ".mov", ".m4v", ".mkv", ".webm"}


def photo_metadata(path):
    from PIL import Image, ImageOps
    if path.suffix.lower() in {".heic", ".heif"}:
        from pillow_heif import register_heif_opener
        register_heif_opener()
    with Image.open(path) as original:
        exif = original.getexif()
        detail = exif.get_ifd(34665)
        raw = detail.get(36867) or detail.get(36868) or exif.get(306)
        offset = detail.get(36881) or detail.get(36880)
        try:
            captured = datetime.strptime(raw, "%Y:%m:%d %H:%M:%S").isoformat()
            if offset:
                captured = datetime.fromisoformat(captured + offset).isoformat()
        except (TypeError, ValueError):
            captured = None
        upright = ImageOps.exif_transpose(original)
        return {"kind": "photo", "captured_at": captured, "dimensions": list(upright.size),
                "date_basis": {"method": "EXIF DateTimeOriginal/DateTimeDigitized/DateTime",
                               "timezone_known": bool(offset), "precision": "second"},
                "orientation": exif.get(274, 1)}


def video_metadata(path, ffprobe):
    data = probe(path, ffprobe)
    stream = next(s for s in data["streams"] if s.get("codec_type") == "video")
    tags = {**stream.get("tags", {}), **data.get("format", {}).get("tags", {})}
    raw = tags.get("com.apple.quicktime.creationdate") or tags.get("creation_time")
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        captured, known = parsed.isoformat(), parsed.tzinfo is not None
    except (AttributeError, TypeError, ValueError):
        captured, known = None, False
    side = next((s for s in stream.get("side_data_list", []) if "rotation" in s), {})
    rotation = float(side.get("rotation", tags.get("rotate", 0)))
    dimensions = [stream["width"], stream["height"]]
    if round(rotation) % 180:
        dimensions = dimensions[::-1]
    return {"kind": "video", "captured_at": captured, "dimensions": dimensions,
            "date_basis": {"method": "QuickTime creationdate/creation_time",
                           "timezone_known": known, "precision": "second"},
            "duration_seconds": float(stream.get("duration") or data["format"]["duration"]),
            "fps": float(Fraction(stream.get("avg_frame_rate", "0/1"))),
            "rotation": rotation, "hdr": stream.get("color_transfer") in {"arib-std-b67", "smpte2084"},
            "has_audio": any(s.get("codec_type") == "audio" for s in data["streams"])}


def catalog(directory, ffprobe="ffprobe"):
    directory = Path(directory).resolve(strict=True)
    names = sorted(p.relative_to(directory).as_posix() for p in directory.rglob("*")
                   if p.is_file() and p.suffix.lower() in PHOTOS | VIDEOS)
    unique_names(names)
    rows = []
    for name in names:
        path = within(directory, name)
        metadata = (photo_metadata(path) if path.suffix.lower() in PHOTOS
                    else video_metadata(path, ffprobe))
        rows.append({"canonical_original_source": "media/" + name, "source": name,
                     "sha256": sha256(path), "size_bytes": path.stat().st_size, **metadata})
    groups = {}
    for row in rows:
        groups.setdefault(row["sha256"], []).append(row["canonical_original_source"])
    return {"schema_version": "1.0", "status": "catalogued_not_selected", "sources": rows,
            "duplicate_content": [v for v in groups.values() if len(v) > 1],
            "date_policy": "Missing/naive capture timestamps require explicit placement/timezone review"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--media-directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ffprobe", default="ffprobe")
    args = parser.parse_args()
    write_json(args.output, catalog(args.media_directory, args.ffprobe))


if __name__ == "__main__":
    main()
