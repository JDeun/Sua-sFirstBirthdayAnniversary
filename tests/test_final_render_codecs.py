"""Verify final-render QA rejects incompatible codecs without private media."""
import unittest
from unittest.mock import patch
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_final_render import inspect_render


class CodecTests(unittest.TestCase):
    def test_rejects_wrong_codecs(self):
        probe = {"streams": [
            {"codec_type": "video", "codec_name": "vp9", "avg_frame_rate": "30/1"},
            {"codec_type": "audio", "codec_name": "opus"}],
            "format": {"duration": "10"}}
        with patch("check_final_render._run", return_value=json.dumps(probe)):
            result = inspect_render(Path("synthetic.mp4"), 300)
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("video codec mismatch" in e for e in result["errors"]))
        self.assertTrue(any("audio codec mismatch" in e for e in result["errors"]))

    def test_accepts_expected_codecs(self):
        probe = {"streams": [
            {"codec_type": "video", "codec_name": "h264", "avg_frame_rate": "30/1"},
            {"codec_type": "audio", "codec_name": "aac"}],
            "format": {"duration": "10"}}
        with patch("check_final_render._run", return_value=json.dumps(probe)):
            self.assertEqual(inspect_render(Path("synthetic.mp4"), 300)["status"], "pass")


if __name__ == "__main__":
    unittest.main()
