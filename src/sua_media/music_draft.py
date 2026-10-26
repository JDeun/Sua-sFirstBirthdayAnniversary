"""Build a *draft* music-aligned edit decision list from private local audio.

Never modifies the approved source JSON. Human review is required before film render.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from .film import probe_duration_seconds
from .music_analysis import analyze_audio
from .music_cuts import plan_cuts


def draft_music_edit(approved: Path, song: Path, output: Path, *,
                     end_card_seconds: float = 4.0,
                     min_shot_seconds: float = 1.0,
                     min_gap_seconds: float = 1.5,
                     sensitivity: float = 1.6) -> dict:
    if not math.isfinite(end_card_seconds) or end_card_seconds < 0:
        raise ValueError("end card duration must be nonnegative and finite")
    source = json.loads(approved.read_text(encoding="utf-8"))
    shots = source.get("shots")
    if not isinstance(shots, list) or not shots or any(not isinstance(x, dict) for x in shots):
        raise ValueError("approved file must contain nonempty shot objects")
    if any("cut_at_seconds" in shot for shot in shots):
        raise ValueError("existing manual cut positions must not be overwritten")
    duration = probe_duration_seconds(song)
    # Same 30fps rounding convention as film.prepare_film.
    song_frames = math.ceil(duration * 30)
    story_seconds = (song_frames - round(end_card_seconds * 30)) / 30
    if story_seconds <= 0:
        raise ValueError("end card consumes entire song")
    analysis = analyze_audio(song, min_gap_seconds=min_gap_seconds, sensitivity=sensitivity)
    cuts = plan_cuts(len(shots), story_seconds, analysis["seconds"],
                     min_shot_seconds=min_shot_seconds)
    for shot, cut in zip(shots, cuts):
        shot["cut_at_seconds"] = cut
    source["_draft_music_edit"] = {
        "status": "REVIEW_REQUIRED",
        "analysis": analysis["analysis"],
        "candidate_count": len(analysis["seconds"]),
        "song_duration_seconds": duration,
        "story_seconds": story_seconds,
        "note": "Energy-based cut suggestions only; manually verify lyric timing and shots.",
    }
    if output.resolve() == approved.resolve():
        raise ValueError("output must differ from original approved shot list")
    if output.exists():
        raise FileExistsError(f"draft already exists; review it before replacing: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(source, ensure_ascii=False, indent=2), encoding="utf-8")
    return source


def main() -> None:
    parser = argparse.ArgumentParser(description="Draft local music-aligned cuts for manual review")
    parser.add_argument("--approved", type=Path, required=True)
    parser.add_argument("--song", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--end-card-seconds", type=float, default=4.0)
    parser.add_argument("--min-shot-seconds", type=float, default=1.0)
    parser.add_argument("--min-gap-seconds", type=float, default=1.5)
    parser.add_argument("--sensitivity", type=float, default=1.6)
    args = parser.parse_args()
    result = draft_music_edit(args.approved, args.song, args.output,
                              end_card_seconds=args.end_card_seconds,
                              min_shot_seconds=args.min_shot_seconds,
                              min_gap_seconds=args.min_gap_seconds,
                              sensitivity=args.sensitivity)
    print(f"Draft saved: {args.output} ({len(result['shots'])} shots; review required)")


if __name__ == "__main__":
    main()
