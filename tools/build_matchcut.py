#!/usr/bin/env python3
"""Build portable aligned PNGs from explicitly approved, hash-bound eye pairs.

Input JSON: {"version":1,"canvas":{"width":1920,"height":1080,
"target_eyes":[[800,400],[1120,400]]},"photos":[{"id":"example",
"source":"photos/example.png","source_sha256":"<64 hex characters>",
"eyes":[[100,120],[200,120]],"captured_at":"2000-01-01"}]}.

Optional top-level source_directory is a POSIX directory path resolved relative
to the config (for example ../../media/photos); it may point outside the config
directory. It defaults to the config directory. Each photo.source is a POSIX
relative path contained within that source base; traversal and escaping links
are rejected. No source_directory or source path is emitted in the manifest.
Eyes are ordered corresponding pairs in EXIF-upright RGB pixel coordinates;
both pairs must be distinct and within their respective image/canvas bounds.
Supplying eyes explicitly approves that annotation; no detector selects faces.
IDs and physical source files must be unique. Input order is retained, dates
are optional ISO-8601 strings and never inferred. The output must not exist;
its parent must exist, and it must not overlap the source base or config file.
Existing files/directories/symlinks are never replaced.

Output: photo-000001.png, ... and manifest.json with version:1, photos containing
only {id,asset,captured_at?}, settings and per-photo evidence. Assets are relative
to the output directory. No source paths are copied into the output manifest.
Settings record canvas, feather:40, blur:40 and the coordinate/selection policy.
Evidence records hashes, upright dimensions, approved eyes, matrix and residual;
numerical alignment still requires visual review. No current film is modified.
"""
import argparse
from datetime import datetime
import hashlib
import io
import json
from pathlib import Path
import re
import tempfile

from face_matchcut import align_image, similarity
from filmtools.checks import integer, vector
from filmtools.paths import config_directory, read_json, sha256, within
from filmtools.portraits import upright_rgb


def _eyes(value, size, label):
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError(f"{label} requires two explicitly approved eyes")
    points = [vector(point, 2, label) for point in value]
    if any(not 0 <= point[axis] < size[axis] for point in points for axis in (0, 1)):
        raise ValueError(f"{label} must be within upright image/canvas bounds")
    similarity(points, points)
    return points


def _photo(photo, root):
    if not isinstance(photo, dict):
        raise ValueError("Each photo must be an object")
    identifier = photo.get("id")
    if not isinstance(identifier, str) or not identifier.strip():
        raise ValueError("Each photo requires a nonempty string id")
    digest = photo.get("source_sha256")
    if not isinstance(digest, str) or not re.fullmatch(r"[a-fA-F0-9]{64}", digest):
        raise ValueError("Each photo requires a SHA256 of 64 hex characters")
    source = within(root, photo.get("source"))
    if sha256(source) != digest.lower():
        raise ValueError(f"Source hash differs for photo {identifier!r}")
    date = {}
    if "captured_at" in photo:
        value = photo["captured_at"]
        if not isinstance(value, str) or not value.strip():
            raise ValueError("captured_at must be an ISO-8601 date/datetime string")
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        date = {"captured_at": value}
    stat = source.stat()
    return {"id": identifier, "source": source, "source_sha256": digest.lower(),
            "eyes": photo.get("eyes"), "file_key": (stat.st_dev, stat.st_ino), **date}


def _config(path):
    data = read_json(path)
    if not isinstance(data, dict) or type(data.get("version")) is not int or data["version"] != 1:
        raise ValueError("Expected manifest version 1")
    canvas = data.get("canvas")
    if not isinstance(canvas, dict):
        raise ValueError("Expected a canvas object")
    size = [integer(canvas.get(key), key, minimum=1) for key in ("width", "height")]
    targets = _eyes(canvas.get("target_eyes"), size, "target_eyes")
    rows = data.get("photos")
    if not isinstance(rows, list) or not rows:
        raise ValueError("Expected a nonempty photos list")
    source_base = config_directory(path, data["source_directory"]) if "source_directory" in data else path.parent
    photos = [_photo(row, source_base) for row in rows]
    if len({photo["id"] for photo in photos}) != len(photos):
        raise ValueError("Duplicate photo id")
    if len({photo["file_key"] for photo in photos}) != len(photos):
        raise ValueError("Duplicate physical source (including links/aliases)")
    settings = {"canvas": {"width": size[0], "height": size[1], "target_eyes": targets},
                "feather": 40, "blur": 40, "coordinate_space": "exif_upright_rgb_pixels",
                "selection": "explicit_eyes", "order": "input"}
    return photos, settings, source_base


def _output_path(directory, inputs):
    requested = Path(directory).absolute()
    output = requested.resolve()
    if any(output == source or output in source.parents or source in output.parents for source in inputs):
        raise ValueError("Output directory overlaps an input")
    if requested.exists() or requested.is_symlink():
        raise ValueError("Output directory must not already exist (including symlinks)")
    if not output.parent.is_dir():
        raise ValueError("Output parent directory must already exist")
    return output


def _approved_image(photo):
    # Hash and decode the same bytes, even if a source changes after preflight.
    contents = photo["source"].read_bytes()
    if hashlib.sha256(contents).hexdigest() != photo["source_sha256"]:
        raise ValueError(f"Source hash differs for photo {photo['id']!r}")
    return upright_rgb(io.BytesIO(contents))


def _render(photo, settings, index, stage):
    image = _approved_image(photo)
    eyes = _eyes(photo["eyes"], image.size, "eyes")
    canvas = settings["canvas"]
    result, alignment = align_image(image, eyes, canvas["target_eyes"],
                                    (canvas["width"], canvas["height"]),
                                    feather=settings["feather"], blur=settings["blur"])
    asset = f"photo-{index:06d}.png"
    with (stage / asset).open("xb") as stream:
        result.save(stream, format="PNG")
    date = {"captured_at": photo["captured_at"]} if "captured_at" in photo else {}
    return ({"id": photo["id"], "asset": asset, **date},
            {"id": photo["id"], "source_sha256": photo["source_sha256"],
             "output_sha256": sha256(stage / asset), "source_dimensions": list(image.size),
             "eyes": eyes, **alignment})


def _publish(stage, output, names):
    # Exclusive directory creation and hardlinks never replace a racing output.
    output.mkdir()
    try:
        for name in names:
            (output / name).hardlink_to(stage / name)
    except BaseException:
        for name in names:
            target, original = output / name, stage / name
            if not target.is_symlink() and target.is_file() and target.samefile(original):
                target.unlink()
        try:
            output.rmdir()
        except OSError:
            pass  # Preserve any unrelated file created concurrently.
        raise


def build(config, output_directory):
    """Validate, stage and publish a fresh batch; return its portable manifest."""
    path = Path(config).resolve(strict=True)
    photos, settings, source_base = _config(path)
    output = _output_path(output_directory, [path, source_base, *(photo["source"] for photo in photos)])
    with tempfile.TemporaryDirectory(prefix=".matchcut-", dir=output.parent) as scratch:
        stage = Path(scratch)
        rows = [_render(photo, settings, index, stage) for index, photo in enumerate(photos, 1)]
        manifest = {"version": 1, "photos": [row[0] for row in rows], "settings": settings,
                    "evidence": [row[1] for row in rows], "status": "visual_review_required"}
        with (stage / "manifest.json").open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
        _publish(stage, output, [*(row[0]["asset"] for row in rows), "manifest.json"])
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", type=Path, required=True, help="Approved version-1 JSON manifest")
    parser.add_argument("--output-directory", type=Path, required=True, help="New directory with an existing parent")
    args = parser.parse_args()
    try:
        build(args.config, args.output_directory)
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
