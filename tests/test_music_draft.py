import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from sua_media.music_draft import draft_music_edit


class MusicDraftTests(unittest.TestCase):
    def test_draft_preserves_original_and_requires_review(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            approved = base / "approved.json"
            output = base / "draft.json"
            approved.write_text(json.dumps({"shots": [{"source": "a.jpg"}, {"source": "b.jpg"}]}))
            with patch("sua_media.music_draft.probe_duration_seconds", return_value=12), \
                 patch("sua_media.music_draft.analyze_audio", return_value={
                     "seconds": [5.0], "analysis": "positive_log_rms_novelty"
                 }):
                result = draft_music_edit(approved, base / "song.mp3", output)
            self.assertEqual(result["shots"][0]["cut_at_seconds"], 0.0)
            self.assertEqual(result["shots"][1]["cut_at_seconds"], 5.0)
            self.assertEqual(result["_draft_music_edit"]["status"], "REVIEW_REQUIRED")
            self.assertNotIn("cut_at_seconds", approved.read_text())
            self.assertEqual(json.loads(output.read_text())["shots"][1]["cut_at_seconds"], 5.0)

    def test_refuses_to_overwrite_manual_cuts(self):
        with tempfile.TemporaryDirectory() as temp:
            approved = Path(temp) / "approved.json"
            approved.write_text('{"shots":[{"source":"a.jpg","cut_at_seconds":0}]}')
            with self.assertRaises(ValueError):
                draft_music_edit(approved, Path(temp) / "song.mp3", Path(temp) / "out.json")
