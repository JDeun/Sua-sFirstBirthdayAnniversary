import json
from pathlib import Path
import tempfile
import unittest

from sua_media.audio_cues import merge_props, onset_candidates, validate_markers


class AudioCueTests(unittest.TestCase):
    def test_transient_candidates_are_candidates_not_sections(self):
        rms = [0.005] * 20 + [0.65] + [0.01] * 20 + [0.8] + [0.01] * 20
        cues = onset_candidates(rms)
        self.assertEqual(len(cues), 2)
        self.assertAlmostEqual(cues[0]["time_sec"], 0.4, places=2)
        self.assertAlmostEqual(cues[1]["time_sec"], 0.82, places=2)

    def test_validate_manual_markers(self):
        self.assertEqual(validate_markers(9.0, 12.0),
                         {"matchcutEndFrame": 270, "verseStartFrame": 360})
        with self.assertRaises(ValueError):
            validate_markers(12.0, 9.0)
        with self.assertRaises(ValueError):
            validate_markers(9.0, 9.3)
        with self.assertRaises(ValueError):
            validate_markers(9.0, 19.0)

    def test_merge_preserves_photo_approvals(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "opening-props.json"
            path.write_text(json.dumps({
                "imagePaths": ["media/matchcut/a.png"],
                "musicPath": "",
            }), encoding="utf-8")
            merge_props(path, {"matchcutEndFrame": 270, "verseStartFrame": 360},
                        "media/music/intro.wav")
            result = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(result["imagePaths"], ["media/matchcut/a.png"])
            self.assertEqual(result["musicPath"], "media/music/intro.wav")
            self.assertEqual(result["timing"]["verseStartFrame"], 360)

    def test_reject_unsafe_music_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "props.json"
            path.write_text('{"imagePaths":[]}', encoding="utf-8")
            with self.assertRaises(ValueError):
                merge_props(path, {}, "media/music/../../secret.wav")


if __name__ == "__main__":
    unittest.main()
