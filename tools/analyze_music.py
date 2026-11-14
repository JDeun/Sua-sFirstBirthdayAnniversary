#!/usr/bin/env python3
"""Measure beats, onsets, and RMS from supplied local audio; never infer lyric timing."""
import argparse
from pathlib import Path
import subprocess

from filmtools.paths import sha256, write_json


def measure(samples, rate, hop=256, energy_stride=8):
    import librosa
    import numpy as np
    if samples.ndim != 1 or not len(samples) or not np.all(np.isfinite(samples)):
        raise ValueError("Expected nonempty finite mono audio")
    onset = librosa.onset.onset_strength(y=samples, sr=rate, hop_length=hop)
    tempo, frames = librosa.beat.beat_track(onset_envelope=onset, sr=rate, hop_length=hop)
    beats = librosa.frames_to_time(frames, sr=rate, hop_length=hop)
    onsets = librosa.onset.onset_detect(onset_envelope=onset, sr=rate, hop_length=hop, units="time")
    rms = librosa.feature.rms(y=samples, hop_length=hop)[0][::energy_stride]
    step = energy_stride * hop / rate
    return {"status": "measured_listening_review_required", "duration_seconds": len(samples) / rate,
            "tempo_bpm": float(np.asarray(tempo).ravel()[0]),
            "beats_seconds": np.round(beats, 6).tolist(), "onsets_seconds": np.round(onsets, 6).tolist(),
            "energy": [{"time": round(i * step, 6), "rms": float(v)} for i, v in enumerate(rms)],
            "energy_hop_seconds": step,
            "method": "librosa onset_strength + beat_track; measured supplied audio",
            "review": "Tempo ambiguity and downbeat phase require listening review"}


def analyze(path, ffmpeg="ffmpeg", rate=22050):
    import numpy as np
    result = subprocess.run([ffmpeg, "-nostdin", "-v", "error", "-i", str(path),
                             "-vn", "-ac", "1", "-ar", str(rate), "-f", "f32le", "pipe:1"],
                            check=True, capture_output=True)
    samples = np.frombuffer(result.stdout, dtype="<f4").copy()
    return {**measure(samples, rate), "source_sha256": sha256(path)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audio", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    args = parser.parse_args()
    write_json(args.output, analyze(args.audio, args.ffmpeg))


if __name__ == "__main__":
    main()
