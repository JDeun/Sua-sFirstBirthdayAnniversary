#!/usr/bin/env python3
"""Validate the eight runtime inputs without changing the renderer."""
import argparse
import json
from pathlib import Path

from filmtools.runtime import load_runtime, validate_runtime


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-directory", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(validate_runtime(load_runtime(args.runtime_directory))))


if __name__ == "__main__":
    main()
