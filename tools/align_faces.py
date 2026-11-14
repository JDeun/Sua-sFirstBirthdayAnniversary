#!/usr/bin/env python3
"""Detect local YuNet face candidates; align only an explicitly selected face."""
import argparse
from pathlib import Path

from filmtools.faces import align_image, detect
from filmtools.models import registered_model
from filmtools.paths import sha256, write_json
from filmtools.portraits import upright_rgb


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="Candidate/alignment JSON")
    parser.add_argument("--registry", type=Path, default=Path(__file__).resolve().parents[1] / "models/registry.json")
    parser.add_argument("--model-directory", type=Path)
    parser.add_argument("--face-index", type=int)
    parser.add_argument("--aligned-output", type=Path)
    parser.add_argument("--target-eyes", nargs=4, type=float, metavar=("LX", "LY", "RX", "RY"))
    parser.add_argument("--size", nargs=2, type=int, default=(1920, 1080))
    args = parser.parse_args()
    model = registered_model(args.registry, "yunet-2023mar", args.model_directory)
    image = upright_rgb(args.source)
    faces = detect(image, model)
    report = {"status": "candidates_require_selection_and_visual_review", "source_sha256": sha256(args.source),
              "model_sha256": sha256(model), "dimensions": list(image.size), "faces": faces}
    if args.face_index is not None:
        if not args.aligned_output or not args.target_eyes or not 0 <= args.face_index < len(faces):
            parser.error("Alignment requires a valid face index, output, and target eye pair")
        targets = [args.target_eyes[:2], args.target_eyes[2:]]
        result, evidence = align_image(image, faces[args.face_index]["eyes"], targets, args.size)
        args.aligned_output.parent.mkdir(parents=True, exist_ok=True)
        result.save(args.aligned_output)
        report = {**report, "selected_face_index": args.face_index, "alignment": evidence}
    write_json(args.output, report)


if __name__ == "__main__":
    main()
