"""Deterministic music-grid cut planning; no audio upload or guessed lyrics.

Use editor-supplied musical landmarks (seconds) as candidate cut positions.
The planner chooses increasing boundaries close to equal-length shot slots.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def plan_cuts(shot_count: int, story_seconds: float, landmarks: list[float],
              min_shot_seconds: float = 1.0) -> list[float]:
    if (shot_count < 1 or not math.isfinite(story_seconds) or
            not math.isfinite(min_shot_seconds) or story_seconds <= 0 or min_shot_seconds <= 0):
        raise ValueError("Invalid story length or shot count")
    if shot_count * min_shot_seconds > story_seconds + 1e-9:
        raise ValueError("Too many shots for the available story duration")
    if any(not isinstance(t, (int, float)) or isinstance(t, bool) or
           not math.isfinite(t) or not 0 < t < story_seconds for t in landmarks):
        raise ValueError("Landmarks must lie strictly inside the story duration")
    candidates = sorted(set(float(t) for t in landmarks))
    if shot_count == 1:
        return [0.0]
    if len(candidates) < shot_count - 1:
        raise ValueError("Insufficient musical landmarks for the requested shot count")
    # Dynamic programming avoids greedy early choices that leave no room later.
    # Cost penalizes distance from even pacing, while enforcing minimum duration.
    states = [(0.0, 0.0, [])]
    for index in range(1, shot_count):
        target = story_seconds * index / shot_count
        remaining = shot_count - index
        next_states = []
        for t in candidates:
            if t < index * min_shot_seconds or story_seconds - t < remaining * min_shot_seconds:
                continue
            choices = [(cost + (t - target) ** 2, t, path + [t])
                       for cost, previous, path in states if t - previous >= min_shot_seconds]
            if choices:
                next_states.append(min(choices, key=lambda entry: (entry[0], entry[2])))
        if not next_states:
            raise ValueError("Insufficient musical landmarks for the requested shot count")
        states = next_states
    return [0.0] + min(states, key=lambda entry: (entry[0], entry[2]))[2]


def main() -> None:
    parser = argparse.ArgumentParser(description="Plan exact cuts using manually approved musical landmarks")
    parser.add_argument("--approved", type=Path, required=True)
    parser.add_argument("--landmarks", type=Path, required=True)
    parser.add_argument("--story-seconds", type=float, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    approved = json.loads(args.approved.read_text(encoding="utf-8"))
    landmarks = json.loads(args.landmarks.read_text(encoding="utf-8"))
    if not isinstance(approved.get("shots"), list) or not approved["shots"]:
        raise ValueError("approved file needs nonempty shots")
    if not isinstance(landmarks.get("seconds"), list):
        raise ValueError("landmarks file needs seconds array")
    cuts = plan_cuts(len(approved["shots"]), args.story_seconds, landmarks["seconds"])
    for shot, cut in zip(approved["shots"], cuts):
        shot["cut_at_seconds"] = cut
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(approved, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
