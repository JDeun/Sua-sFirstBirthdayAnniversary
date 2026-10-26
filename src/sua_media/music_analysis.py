"""Local-only, dependency-free audio onset landmark proposals.

Reads PCM WAV and estimates novelty from short-window RMS changes.
These are *candidate* cut points, not verified beats, lyrics or sections.
Human approval is required before invoking music_cuts.
"""
from __future__ import annotations

import argparse
import json
import math
import wave
from pathlib import Path


def propose_landmarks(path: Path, *, hop_seconds: float = 0.1,
                      min_gap_seconds: float = 1.5, sensitivity: float = 1.6) -> dict:
    if not all(math.isfinite(v) and v > 0 for v in
               (hop_seconds, min_gap_seconds, sensitivity)):
        raise ValueError("Analysis parameters must be finite positive numbers")
    with wave.open(str(path), "rb") as wav:
        if wav.getcomptype() != "NONE" or wav.getsampwidth() != 2:
            raise ValueError("Expected uncompressed 16-bit PCM WAV; normalize audio first")
        rate, channels, total = wav.getframerate(), wav.getnchannels(), wav.getnframes()
        if channels not in (1, 2) or rate < 8000:
            raise ValueError("Expected mono/stereo WAV with sample rate >= 8kHz")
        hop = max(1, round(rate * hop_seconds))
        energies = []
        while True:
            data = wav.readframes(hop)
            if not data:
                break
            from array import array
            samples = array("h")
            samples.frombytes(data)
            if not samples:
                break
            rms = math.sqrt(sum(int(x) ** 2 for x in samples) / len(samples))
            energies.append(rms)
    # Positive log-energy novelty. Silence and fades are naturally excluded.
    changes = [0.0]
    for i in range(1, len(energies)):
        changes.append(max(0.0, math.log1p(energies[i]) - math.log1p(energies[i - 1])))
    positive = sorted(x for x in changes if x > 0)
    median = positive[len(positive) // 2] if positive else 0.0
    threshold = max(0.15, median * sensitivity)
    candidates = sorted(
        ((score, i * hop / rate) for i, score in enumerate(changes)
         if score >= threshold and i * hop / rate > 0.5),
        key=lambda pair: (-pair[0], pair[1]),
    )
    selected = []
    for _, second in candidates:
        if all(abs(second - existing) >= min_gap_seconds for existing in selected):
            selected.append(round(second, 3))
    return {
        "seconds": sorted(selected),
        "analysis": "positive_log_rms_novelty",
        "status": "unreviewed_candidates",
        "duration_seconds": round(total / rate, 3),
        "parameters": {"hop_seconds": hop_seconds, "min_gap_seconds": min_gap_seconds,
                       "sensitivity": sensitivity},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Propose local WAV audio cut landmarks")
    parser.add_argument("wav", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--hop-seconds", type=float, default=0.1)
    parser.add_argument("--min-gap-seconds", type=float, default=1.5)
    parser.add_argument("--sensitivity", type=float, default=1.6)
    args = parser.parse_args()
    result = propose_landmarks(args.wav, hop_seconds=args.hop_seconds,
                               min_gap_seconds=args.min_gap_seconds,
                               sensitivity=args.sensitivity)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
