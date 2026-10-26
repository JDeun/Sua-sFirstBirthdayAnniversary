"""End-to-end synthetic music analysis -> musical cut planner contract."""
import math
import struct
import tempfile
import unittest
import wave
from pathlib import Path

from sua_media.music_analysis import propose_landmarks
from sua_media.music_cuts import plan_cuts


class MusicPipelineTests(unittest.TestCase):
    def test_analyzed_landmarks_feed_story_cut_planner(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "synthetic.wav"
            rate = 8000
            with wave.open(str(path), "wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(rate)
                for i in range(rate * 12):
                    t = i / rate
                    active = any(start <= t < start + 0.4 for start in (2, 5, 8))
                    sample = int(12000 * math.sin(2 * math.pi * 440 * t)) if active else 0
                    wav.writeframesraw(struct.pack("<h", sample))
            landmarks = propose_landmarks(path, min_gap_seconds=1.0)["seconds"]
            self.assertTrue(all(any(abs(c - target) < 0.2 for c in landmarks)
                                for target in (2, 5, 8)))
            cuts = plan_cuts(4, 12, landmarks, min_shot_seconds=1)
            self.assertEqual(len(cuts), 4)
            self.assertTrue(all(b - a >= 1 for a, b in zip(cuts, cuts[1:])))
            self.assertTrue(12 - cuts[-1] >= 1)
