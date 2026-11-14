#!/usr/bin/env python3
"""Apply bounded global linear-light tone parameters from external JSON."""
import argparse
from pathlib import Path

from filmtools.paths import read_json, sha256, write_json
from filmtools.portraits import apply_tone, upright_rgb


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--parameters", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    image, report = apply_tone(upright_rgb(args.source), **read_json(args.parameters))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output)
    write_json(args.report, {**report, "source_sha256": sha256(args.source)})


if __name__ == "__main__":
    main()
