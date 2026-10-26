"""Regression tests for the agent-facing single-command production orchestrator."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from sua_media.produce import produce


class ProduceTests(unittest.TestCase):
    def test_renders_and_reads_qa_report(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            video = root / "video"
            (video / "src").mkdir(parents=True)
            (video / "src" / "index.ts").write_text("")
            (video / "public").mkdir()
            props = root / "props.json"
            output = root / "film.mp4"
            report = root / "qa.json"
            film = {"opening": {"timing": {"songStartFrame": 450}},
                    "songDurationFrames": 300}
            calls = []

            def fake_run(command, **kwargs):
                calls.append(command)
                if "remotion" in command:
                    output.write_bytes(b"synthetic mp4 placeholder")
                else:
                    report.write_text(json.dumps({"status": "pass", "errors": []}))

            with patch("sua_media.produce.prepare_film", return_value=film), \
                 patch("sua_media.produce.subprocess.run", side_effect=fake_run):
                result = produce(approved=root / "approved.json",
                                 opening_props=root / "opening.json",
                                 song=root / "song.mp3", public_dir=video / "public",
                                 props=props, output=output, report=report,
                                 video_dir=video)
            self.assertEqual(result["expected_frames"], 750)
            self.assertEqual(result["qa"]["status"], "pass")
            self.assertEqual(len(calls), 2)
            self.assertIn("--expected-frames", calls[1])

    def test_existing_output_is_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            video = root / "video"
            (video / "src").mkdir(parents=True)
            (video / "src" / "index.ts").write_text("")
            (video / "public").mkdir()
            output = root / "film.mp4"
            output.write_bytes(b"important existing film")
            with patch("sua_media.produce.prepare_film") as prepare:
                with self.assertRaises(FileExistsError):
                    produce(approved=root / "approved.json",
                            opening_props=root / "opening.json",
                            song=root / "song.mp3", public_dir=video / "public",
                            props=root / "props.json", output=output,
                            report=root / "qa.json", video_dir=video)
                prepare.assert_not_called()
            self.assertEqual(output.read_bytes(), b"important existing film")

    def test_rejects_source_output_collision(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            video = root / "video"
            (video / "src").mkdir(parents=True)
            (video / "src" / "index.ts").write_text("")
            (video / "public").mkdir()
            approved = root / "approved.json"
            approved.write_text("important approved edits")
            with patch("sua_media.produce.prepare_film") as prepare:
                with self.assertRaisesRegex(ValueError, "source inputs"):
                    produce(approved=approved, opening_props=root / "opening.json",
                            song=root / "song.mp3", public_dir=video / "public",
                            props=approved, output=root / "film.mp4",
                            report=root / "qa.json", video_dir=video)
                prepare.assert_not_called()
            self.assertEqual(approved.read_text(), "important approved edits")

    def test_failed_render_cleans_partial_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            video = root / "video"
            (video / "src").mkdir(parents=True)
            (video / "src" / "index.ts").write_text("")
            (video / "public").mkdir()
            output = root / "film.mp4"

            def broken_render(command, **kwargs):
                output.write_bytes(b"incomplete")
                raise RuntimeError("render failed")

            with patch("sua_media.produce.prepare_film", return_value={
                "opening": {"timing": {"songStartFrame": 450}},
                "songDurationFrames": 300,
            }), patch("sua_media.produce.subprocess.run", side_effect=broken_render):
                with self.assertRaisesRegex(RuntimeError, "render failed"):
                    produce(approved=root / "approved.json",
                            opening_props=root / "opening.json",
                            song=root / "song.mp3", public_dir=video / "public",
                            props=root / "props.json", output=output,
                            report=root / "qa.json", video_dir=video)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
