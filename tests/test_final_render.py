import tempfile
from pathlib import Path
import subprocess
import unittest

from scripts.check_final_render import inspect_render


class FinalRenderQATests(unittest.TestCase):
    def test_video_and_audio_duration(self):
        with tempfile.TemporaryDirectory() as tmp:
            video = Path(tmp) / "synthetic.mp4"
            subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                            "-f", "lavfi", "-i", "color=c=white:s=64x64:r=30:d=2",
                            "-f", "lavfi", "-i", "sine=frequency=440:duration=2",
                            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
                            "-shortest", str(video)], check=True)
            self.assertEqual(inspect_render(video, 60)["status"], "pass")
            self.assertEqual(inspect_render(video, 90)["status"], "fail")

    def test_missing_audio(self):
        with tempfile.TemporaryDirectory() as tmp:
            video = Path(tmp) / "silent.mp4"
            subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                            "-f", "lavfi", "-i", "color=c=white:s=64x64:r=30:d=1",
                            "-c:v", "libx264", "-pix_fmt", "yuv420p", str(video)], check=True)
            self.assertIn("audio stream missing", inspect_render(video, 30)["errors"])

    def test_frame_rate_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            video = Path(tmp) / "wrong-fps.mp4"
            subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                            "-f", "lavfi", "-i", "color=c=white:s=64x64:r=24:d=2",
                            "-f", "lavfi", "-i", "sine=frequency=440:duration=2",
                            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
                            "-shortest", str(video)], check=True)
            self.assertTrue(any("frame rate mismatch" in error
                                for error in inspect_render(video, 60)["errors"]))
