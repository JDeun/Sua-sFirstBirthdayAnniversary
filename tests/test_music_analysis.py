import math
import subprocess
import struct
import tempfile
import unittest
import wave
from pathlib import Path

from sua_media.music_analysis import propose_landmarks, analyze_audio


class MusicAnalysisTests(unittest.TestCase):
    def make_wav(self, path, bursts=True):
        rate = 8000
        with wave.open(str(path), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(rate)
            for i in range(rate * 5):
                active = bursts and (1 <= i / rate < 1.4 or 3 <= i / rate < 3.4)
                sample = int(12000 * math.sin(2 * math.pi * 440 * i / rate)) if active else 0
                wav.writeframesraw(struct.pack("<h", sample))

    def test_detects_synthetic_onsets(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bursts.wav"
            self.make_wav(path)
            result = propose_landmarks(path, min_gap_seconds=0.8)
            self.assertEqual(result["status"], "unreviewed_candidates")
            self.assertTrue(any(abs(x - 1) < 0.2 for x in result["seconds"]))
            self.assertTrue(any(abs(x - 3) < 0.2 for x in result["seconds"]))

    def test_silence_produces_no_landmarks(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "silence.wav"
            self.make_wav(path, bursts=False)
            self.assertEqual(propose_landmarks(path)["seconds"], [])

    def test_rejects_invalid_parameters(self):
        with self.assertRaises(ValueError):
            propose_landmarks(Path("unused.wav"), hop_seconds=float("nan"))

    def test_mp3_is_decoded_locally_and_analyzed(self):
        with tempfile.TemporaryDirectory() as tmp:
            wav_path = Path(tmp) / "bursts.wav"
            mp3_path = Path(tmp) / "bursts.mp3"
            self.make_wav(wav_path)
            subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                            "-i", str(wav_path), str(mp3_path)],
                           check=True, capture_output=True)
            result = analyze_audio(mp3_path, min_gap_seconds=0.8)
            self.assertTrue(any(abs(x - 1) < 0.3 for x in result["seconds"]))
            self.assertTrue(any(abs(x - 3) < 0.3 for x in result["seconds"]))
