#!/usr/bin/env python3
"""Create a local RGBA cutout from supplied upright-coordinate polygons."""
import argparse
from pathlib import Path

from filmtools.cutout import segment
from filmtools.paths import read_json, sha256, write_json
from filmtools.portraits import upright_rgb


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=5)
    args = parser.parse_args()
    if args.output.suffix.lower() != ".png":
        parser.error("Cutout output must be PNG to preserve alpha")
    image, report = segment(upright_rgb(args.source), read_json(args.annotations), args.iterations)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output)
    write_json(args.report, {**report, "source_sha256": sha256(args.source),
                             "annotation_sha256": sha256(args.annotations)})


if __name__ == "__main__":
    main()
