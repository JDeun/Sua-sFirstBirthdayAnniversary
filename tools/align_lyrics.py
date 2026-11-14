#!/usr/bin/env python3
"""Optional offline known-lyric estimates with explicit text/hash provenance."""
import argparse
import os
from pathlib import Path

from filmtools.lyrics import normalize, occurrences, provenance
from filmtools.models import registered_model
from filmtools.paths import read_json, sha256, write_json


def align_local(audio, text, model, language):
    import torch
    import stable_whisper
    torch.set_num_threads(min(4, os.cpu_count() or 1))
    # A verified file path bypasses Whisper's model-name download branch.
    local = stable_whisper.load_model(str(model), device="cpu")
    result = local.align(str(audio), text, language=language, original_split=True,
                         suppress_silence=False, nonspeech_skip=None,
                         max_word_dur=4, word_dur_factor=2.5, verbose=False)
    if result is None:
        raise ValueError("The local model could not align the supplied text")
    return result.to_dict()


def build_report(native, text, spec, audio_hash, fps, beats):
    coverage = normalize("".join(s["text"] for s in native["segments"])) == normalize(text)
    if not coverage:
        raise ValueError("Alignment does not cover the exact supplied text")
    return {"status": "auto_aligned_review_required", "review_status": "not_reviewed", "fps": fps,
            "song_asset": spec["song_asset"], "song_sha256": audio_hash,
            "method": "local stable-ts known-text alignment", "lyric_coverage_matches": True,
            "timing_policy": "Estimated vocal timestamps; beat accents remain independent",
            "occurrences": occurrences(native, spec["occurrences"], beats, fps)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audio", type=Path, required=True)
    parser.add_argument("--lyrics", type=Path, required=True)
    parser.add_argument("--phrases", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--native-output", type=Path, required=True)
    parser.add_argument("--from-result", type=Path)
    parser.add_argument("--music-map", type=Path)
    parser.add_argument("--registry", type=Path, default=Path(__file__).resolve().parents[1] / "models/registry.json")
    parser.add_argument("--model-directory", type=Path)
    parser.add_argument("--language", required=True)
    parser.add_argument("--fps", type=int, default=30)
    args = parser.parse_args()
    if args.fps < 1:
        parser.error("fps must be positive")
    model = registered_model(args.registry, "whisper-small", args.model_directory)
    text = args.lyrics.read_text(encoding="utf-8").strip()
    evidence = provenance(sha256(args.audio), text, sha256(model), args.language)
    native = read_json(args.from_result) if args.from_result else align_local(args.audio, text, model, args.language)
    if args.from_result and native.get("alignment_provenance") != evidence:
        raise ValueError("Cached estimates have different or missing audio/text/model provenance")
    native = {**native, "alignment_provenance": evidence}
    beats = read_json(args.music_map)["beats_seconds"] if args.music_map else []
    report = build_report(native, text, read_json(args.phrases), evidence["song_sha256"], args.fps, beats)
    write_json(args.native_output, native)
    write_json(args.output, report)


if __name__ == "__main__":
    main()
