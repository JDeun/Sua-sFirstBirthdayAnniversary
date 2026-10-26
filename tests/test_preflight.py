import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch
import subprocess

from sua_media.preflight import inspect, preflight


class PreflightTests(TestCase):
    def test_missing_and_empty(self):
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / "missing.mp4"
            self.assertEqual(inspect(p)["status"], "error")
            p.write_bytes(b"")
            self.assertEqual(inspect(p)["status"], "error")

    def test_heic_conversion_warning(self):
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / "image.heic"
            p.write_bytes(b"synthetic")
            self.assertEqual(inspect(p)["status"], "ok")
            self.assertIn("HEIC", inspect(p)["warnings"][0])

    @patch("sua_media.preflight.subprocess.run")
    def test_vfr_hdr_rotation(self, run):
        run.return_value.stdout = ('{"streams":[{"codec_type":"video","codec_name":"hevc",'
                                   '"width":1920,"height":1080,"avg_frame_rate":"30000/1001",'
                                   '"r_frame_rate":"30/1","color_transfer":"arib-std-b67",'
                                   '"side_data_list":[{"rotation":90}]}],'
                                   '"format":{"duration":"4.5"}}')
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / "clip.mov"
            p.write_bytes(b"synthetic")
            report = preflight([p])
            self.assertEqual(report["errors"], 0)
            self.assertEqual(report["warnings"], 3)
            self.assertEqual(report["files"][0]["rotation"], 90)

    @patch("sua_media.preflight.subprocess.run", side_effect=subprocess.CalledProcessError(1, "ffprobe"))
    def test_corrupt_video(self, run):
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / "clip.mp4"
            p.write_bytes(b"synthetic")
            self.assertEqual(inspect(p)["status"], "error")
