#!/usr/bin/env python3
"""Review actual final baseline-video frames using explicit fitted apertures."""
import argparse
from pathlib import Path

from filmtools.endpoints import inspect_endpoint_pixels
from filmtools.paths import read_json, within, write_json


def check_frames(plan, manifest, directory):
    from PIL import Image
    expected = {s["id"]: s for s in plan["shots"]
                if s["kind"] == "video" and s["usage"] == "baseline"}
    results, seen = [], set()
    for row in manifest["frames"]:
        key = row["shot_id"]
        if key not in expected or key in seen:
            raise ValueError("Endpoint evidence has an unknown or repeated video shot")
        shot = expected[key]
        last = plan["opening"]["duration_in_frames"] + shot["song_end_frame"] - 1
        if row["frame"] != last:
            raise ValueError("Endpoint evidence must use the actual last displayed movie frame")
        layout = shot["frameLayout"]
        rect = layout["media"]
        mat, foot = layout.get("mat", 0), layout.get("foot", 0)
        aperture = {"x": rect["x"] + mat, "y": rect["y"] + mat,
                    "width": rect["width"] - 2 * mat, "height": rect["height"] - 2 * mat - foot}
        with Image.open(within(directory, row["image"])) as image:
            result = inspect_endpoint_pixels(image, aperture, manifest["canvas_size"])
        results.append({"shot_id": key, "frame": last, **result})
        seen.add(key)
    missing = sorted(set(expected) - seen)
    return {"status": "incomplete" if missing else "review_required" if any(
            r["review_required"] for r in results) else "no_flat_apertures_detected",
            "expected_videos": len(expected), "checked_videos": len(results),
            "missing_shots": missing, "frames": results,
            "scope": "Luminance variation is a heuristic, not proof of source visibility"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--edit", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--frames-directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = check_frames(read_json(args.edit), read_json(args.manifest), args.frames_directory)
    write_json(args.output, report)
    return 1 if report["status"] == "incomplete" else 0


if __name__ == "__main__":
    raise SystemExit(main())
