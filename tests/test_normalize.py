import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from sua_media.normalize import normalize


class NormalizeTests(TestCase):
    @patch("sua_media.normalize.subprocess.run")
    @patch("sua_media.normalize.inspect")
    def test_video_cfr_sdr_and_original_untouched(self, inspect, run):
        inspect.return_value = {"status": "ok", "warnings": []}
        with tempfile.TemporaryDirectory() as root:
            base = Path(root)
            original = base / "clip.mov"
            original.write_bytes(b"synthetic-original")
            def fake_run(command, **kwargs):
                Path(command[-1]).write_bytes(b"synthetic-normalized")
            run.side_effect = fake_run
            target = normalize(original, base / "normalized")
            self.assertEqual(target.suffix, ".mp4")
            self.assertEqual(original.read_bytes(), b"synthetic-original")
            self.assertEqual(target.read_bytes(), b"synthetic-normalized")
            cmd = run.call_args.args[0]
            self.assertIn("fps=30,format=yuv420p", cmd)
            self.assertIn("libx264", cmd)
            normalize(original, base / "normalized")
            self.assertEqual(run.call_count, 1)

    @patch("sua_media.normalize.subprocess.run")
    @patch("sua_media.normalize.inspect")
    def test_hdr_uses_tonemap(self, inspect, run):
        inspect.return_value = {"status": "ok", "warnings": ["HDR footage"]}
        with tempfile.TemporaryDirectory() as root:
            original = Path(root) / "clip.mp4"
            original.write_bytes(b"synthetic-hdr")
            run.side_effect = lambda command, **kwargs: Path(command[-1]).write_bytes(b"converted")
            normalize(original, Path(root) / "out")
            self.assertTrue(any("tonemap=" in part for part in run.call_args.args[0]))

    @patch("sua_media.normalize.inspect")
    def test_rejects_bad_file_without_output(self, inspect):
        inspect.return_value = {"status": "error", "warnings": ["bad codec"]}
        with tempfile.TemporaryDirectory() as root:
            original = Path(root) / "bad.mp4"
            original.write_bytes(b"synthetic")
            with self.assertRaises(ValueError):
                normalize(original, Path(root) / "out")
            self.assertFalse((Path(root) / "out").exists())
