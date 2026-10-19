import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from sua_media.film import allocate_frames, prepare_film


class FilmTests(unittest.TestCase):
    def test_frame_allocation_exact(self):
        self.assertEqual(sum(allocate_frames([1, 2, 1], 301)), 301)
        self.assertTrue(all(n >= 30 for n in allocate_frames([1, 2, 1], 301)))
        with self.assertRaises(ValueError):
            allocate_frames([1, 1, 1], 85)

    @patch("sua_media.film.probe_duration_seconds")
    def test_film_audio_timeline_and_private_copies(self, probe):
        probe.return_value = 12.05
        with tempfile.TemporaryDirectory() as root:
            base = Path(root)
            photos = base / "originals"
            photos.mkdir()
            (photos / "birth.jpg").write_bytes(b"birth-photo-test-only")
            (photos / "smile.png").write_bytes(b"smile-photo-test-only")
            song = base / "suno.mp3"
            song.write_bytes(b"fake-synthetic-test-mp3")
            approved = base / "approved.json"
            approved.write_text(json.dumps({"shots": [
                {"source": "originals/birth.jpg", "weight": 2,
                 "chapter": "첫 만남", "caption": "수아의 이야기"},
                {"source": "originals/smile.png", "weight": 1,
                 "treatment": "scrapbook"},
            ]}), encoding="utf-8")
            opening = base / "opening.json"
            opening.write_text(json.dumps({"imagePaths": ["media/matchcut/1.png"],
                "musicPath": "", "timing": {"matchcutEndFrame": 270,
                    "songStartFrame": 360}}), encoding="utf-8")
            target = base / "data" / "film-props.json"
            result = prepare_film(approved, opening, song, base / "video" / "public", target)
            self.assertEqual(result["songDurationFrames"], 362)
            self.assertEqual(result["endCardFrames"], 120)
            self.assertEqual(result["shots"][0]["startFrame"], 0)
            self.assertEqual(result["shots"][1]["startFrame"],
                             result["shots"][0]["durationFrames"])
            self.assertEqual(sum(x["durationFrames"] for x in result["shots"]), 242)
            self.assertEqual(result["opening"]["timing"]["songStartFrame"], 360)
            self.assertTrue((base / "video" / "public" /
                result["opening"]["musicPath"]).is_file())
            self.assertEqual((photos / "birth.jpg").read_bytes(), b"birth-photo-test-only")
            self.assertEqual(json.loads(target.read_text(encoding="utf-8")), result)
            self.assertEqual(list((base / "video" / "public" / "media" / "story").glob("*")).__len__(), 2)
            # Idempotency: hashed copies should not proliferate on reruns.
            prepare_film(approved, opening, song, base / "video" / "public", target)
            self.assertEqual(len(list((base / "video" / "public" / "media" / "story").glob("*"))), 2)

    @patch("sua_media.film.probe_duration_seconds")
    def test_rejects_unavailable_video_without_creating_props(self, probe):
        probe.side_effect = [7.0, 1.0]
        with tempfile.TemporaryDirectory() as root:
            base = Path(root)
            (base / "video.mp4").write_bytes(b"fake-video")
            (base / "song.mp3").write_bytes(b"fake-audio")
            approved = base / "approved.json"
            approved.write_text(json.dumps({"shots": [
                {"source": "video.mp4", "weight": 1}
            ]}), encoding="utf-8")
            opening = base / "opening.json"
            opening.write_text(json.dumps({"imagePaths": [],
                "timing": {"matchcutEndFrame": 270,
                    "songStartFrame": 360}}), encoding="utf-8")
            target = base / "data" / "props.json"
            with self.assertRaisesRegex(ValueError, "동영상 길이"):
                prepare_film(approved, opening, base / "song.mp3", base / "public", target)
            self.assertFalse(target.exists())

    @patch("sua_media.film.probe_duration_seconds", return_value=8)
    def test_path_traversal_source_not_automatically_available(self, probe):
        with tempfile.TemporaryDirectory() as root:
            base = Path(root)
            (base / "song.mp3").write_bytes(b"fake-song")
            approved = base / "approved.json"
            approved.write_text(json.dumps({"shots": [
                {"source": "../not-present.jpg"}
            ]}), encoding="utf-8")
            opening = base / "opening.json"
            opening.write_text(json.dumps({"imagePaths": []}), encoding="utf-8")
            with self.assertRaises(ValueError):
                prepare_film(approved, opening, base / "song.mp3",
                             base / "public", base / "out.json")


if __name__ == "__main__":
    unittest.main()
