"""Non-destructive media inventory with conservative chronology and deduplication."""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import date, datetime
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any

EXTENSIONS = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp",
              ".tif", ".tiff", ".mp4", ".mov", ".m4v", ".avi", ".mkv"}
PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp", ".tif", ".tiff"}
DATE_TAGS = ("DateTimeOriginal", "SubSecDateTimeOriginal",
             "CreationDate", "MediaCreateDate", "TrackCreateDate", "CreateDate")
DATE_PATTERN = re.compile(
    r"(?<!\d)((?:19|20)\d{2})[-_.]?(\d{2})[-_.]?(\d{2})"
    r"(?:[T _.-]?(\d{2})[:._-]?(\d{2})[:._-]?(\d{2}))?(?!\d)"
)


def parse_date(value: Any) -> tuple[str, str] | None:
    """Accept ExifTool EXIF/QuickTime dates and return ISO and precision."""
    if not value:
        return None
    text = str(value).strip()
    match = re.match(
        r"^(\d{4})[:-](\d{2})[:-](\d{2})"
        r"(?:[ T](\d{2}):(\d{2}):(\d{2}))?(?:\.\d+)?"
        r"(?:\s*(Z|[+-]\d{2}:?\d{2}))?", text
    )
    if not match:
        return None
    year, month, day = map(int, match.group(1, 2, 3))
    if year < 1990 or year > 2100:
        return None
    try:
        day_value = date(year, month, day)
        if match.group(4) is None:
            return day_value.isoformat(), "day"
        hour, minute, second = map(int, match.group(4, 5, 6))
        instant = datetime(year, month, day, hour, minute, second)
    except ValueError:
        return None
    tz = match.group(7)
    suffix = ""
    if tz:
        suffix = "+00:00" if tz == "Z" else tz[:3] + ":" + tz[-2:]
    return instant.isoformat(timespec="seconds") + suffix, "second"


def filename_date(name: str) -> tuple[str, str] | None:
    """File naming is only evidence; KakaoTalk names can reflect a save date."""
    for match in DATE_PATTERN.finditer(name):
        try:
            year, month, day = map(int, match.group(1, 2, 3))
            value = date(year, month, day).isoformat()
            if match.group(4) is not None:
                hour, minute, second = map(int, match.group(4, 5, 6))
                value = datetime(year, month, day, hour, minute, second).isoformat()
                return value, "second"
            return value, "day"
        except ValueError:
            continue
    return None


def infer_date(filename: str, metadata: dict[str, Any]) -> dict[str, Any]:
    for tag in DATE_TAGS:
        parsed = parse_date(metadata.get(tag))
        if parsed:
            return {"captured_at": parsed[0], "date_precision": parsed[1],
                    "date_source": "metadata:" + tag,
                    "date_confidence": "high" if tag in DATE_TAGS[:2] else "medium"}
    parsed = filename_date(filename)
    if parsed:
        kakao = "kakao" in filename.lower()
        return {"captured_at": parsed[0], "date_precision": parsed[1],
                "date_source": "filename:kakao_possible_transfer" if kakao else "filename",
                "date_confidence": "low" if kakao else "medium"}
    return {"captured_at": None, "date_precision": None,
            "date_source": "unknown", "date_confidence": "unknown"}


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_metadata(paths: list[Path]) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """Call ExifTool in batches rather than one process per image."""
    if not shutil.which("exiftool"):
        return {}, ["ExifTool not found: using filename date inference only."]
    result: dict[str, dict[str, Any]] = {}
    warnings: list[str] = []
    for start in range(0, len(paths), 60):
        batch = paths[start:start + 60]
        cmd = ["exiftool", "-json", "-api", "QuickTimeUTC=1",
               "-DateTimeOriginal", "-SubSecDateTimeOriginal", "-CreationDate",
               "-MediaCreateDate", "-TrackCreateDate", "-CreateDate",
               "-ImageWidth", "-ImageHeight", "-Orientation",
               *[str(p) for p in batch]]
        try:
            run = subprocess.run(cmd, capture_output=True, text=True, timeout=180, check=False)
            if run.returncode != 0:
                warnings.append("ExifTool warnings: " + run.stderr.strip()[:500])
            for row in json.loads(run.stdout or "[]"):
                result[str(Path(row["SourceFile"]).resolve())] = row
        except (OSError, subprocess.TimeoutExpired, ValueError, KeyError) as error:
            warnings.append(f"ExifTool batch failed: {error}")
    return result, warnings


def visual_hash(path: Path) -> str | None:
    """dHash for suggestions only. Never auto-delete based on this value."""
    try:
        from PIL import Image, ImageOps
        try:
            import pillow_heif
            pillow_heif.register_heif_opener()
        except ImportError:
            pass
        with Image.open(path) as image:
            upright = ImageOps.exif_transpose(image)
            pixels = list(upright.convert("L").resize((9, 8)).getdata())
        bits = sum((1 << (row * 8 + col))
                   for row in range(8) for col in range(8)
                   if pixels[row * 9 + col] > pixels[row * 9 + col + 1])
        return f"{bits:016x}"
    except (ImportError, OSError, ValueError):
        return None


def month_age(when: str | None, birth: date | None) -> int | None:
    if not when or birth is None:
        return None
    try:
        value = date.fromisoformat(when[:10])
    except ValueError:
        return None
    months = (value.year - birth.year) * 12 + value.month - birth.month
    months -= value.day < birth.day
    return months if months >= 0 else None


def build_catalog(source: Path, birth: date | None = None) -> dict[str, Any]:
    source = source.expanduser().resolve()
    if not source.is_dir():
        raise ValueError(f"Not a directory: {source}")
    paths = sorted((p.resolve() for p in source.rglob("*")
                    if p.is_file() and p.suffix.lower() in EXTENSIONS))
    metadata, warnings = read_metadata(paths)
    rows = []
    duplicates: dict[str, str] = {}
    for path in paths:
        item = metadata.get(str(path), {})
        stamp = infer_date(path.name, item)
        checksum = file_sha256(path)
        canonical = duplicates.setdefault(checksum, str(path.relative_to(source)))
        record = {
            "path": str(path),
            "relative_path": str(path.relative_to(source)),
            "filename": path.name,
            "kind": "photo" if path.suffix.lower() in PHOTO_EXTENSIONS else "video",
            "size_bytes": path.stat().st_size,
            "sha256": checksum,
            "duplicate_of": canonical if canonical != str(path.relative_to(source)) else None,
            "file_mtime_observed": datetime.fromtimestamp(path.stat().st_mtime).astimezone().isoformat(),
            "age_month": month_age(stamp["captured_at"], birth),
            **stamp,
            "width": item.get("ImageWidth"),
            "height": item.get("ImageHeight"),
            "visual_hash": visual_hash(path) if path.suffix.lower() in PHOTO_EXTENSIONS else None,
            "similar_candidates": [],
            "reviewed": False,
        }
        rows.append(record)

    # Restrict comparisons to similarly shaped images to reduce false positives.
    candidates = [(row, int(row["visual_hash"], 16)) for row in rows
                  if row["kind"] == "photo" and row["visual_hash"]
                  and row["duplicate_of"] is None]
    for i, (left, lh) in enumerate(candidates):
        for right, rh in candidates[i + 1:]:
            if (lh ^ rh).bit_count() <= 3:
                left["similar_candidates"].append(right["relative_path"])
                right["similar_candidates"].append(left["relative_path"])
    rows.sort(key=lambda r: (r["captured_at"] is None,
                            r["captured_at"][:10] if r["captured_at"] else "",
                            r["captured_at"] or "", r["relative_path"]))
    return {
        "schema_version": 1,
        "source": str(source),
        "generated_at": datetime.now().astimezone().isoformat(),
        "files_total": len(rows),
        "exact_duplicates": sum(row["duplicate_of"] is not None for row in rows),
        "unknown_dates": sum(row["captured_at"] is None for row in rows),
        "warnings": warnings,
        "media": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Inventory local family media without changing originals.")
    parser.add_argument("source", type=Path, help="Local path, e.g. downloaded Google Drive folder")
    parser.add_argument("--out", type=Path, default=Path("data/manifest.json"))
    parser.add_argument("--birth-date", type=date.fromisoformat, default=None,
                        metavar="YYYY-MM-DD", help="Optional child birth date for month-age grouping")
    args = parser.parse_args()
    manifest = build_catalog(args.source, args.birth_date)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Indexed {manifest['files_total']} media; "
          f"{manifest['exact_duplicates']} exact duplicate copies; "
          f"{manifest['unknown_dates']} undated. Wrote {args.out}")


if __name__ == "__main__":
    main()
