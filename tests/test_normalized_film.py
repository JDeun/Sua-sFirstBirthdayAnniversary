import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from sua_media.film import prepare_film


class NormalizedFilmTests(unittest.TestCase):
    @patch("sua_media.film.normalize")
    @patch("sua_media.film.probe_duration_seconds", return_value=9.0)
    def test_opt_in_normalization_stages_only_private_assets(self, probe, normalize):
        with tempfile.TemporaryDirectory() as root:
            base = Path(root)
            (base / "photo.jpg").write_bytes(b"synthetic-photo")
            (base / "song.mp3").write_bytes(b"synthetic-song")
            approval = base / "approved.json"
            approval.write_text(json.dumps({"shots": [{"source": "photo.jpg"}]}))
            opening = base / "opening.json"
            opening.write_text(json.dumps({"imagePaths": []}))
            public = base / "video" / "public"
            def fake_normalize(src, output):
                self.assertEqual(output, public / "media" / ".normalized-cache")
                output.mkdir(parents=True, exist_ok=True)
                ext = ".png" if src.suffix == ".jpg" else ".wav"
                target = output / (src.stem + ext)
                target.write_bytes(src.read_bytes())
                return target
            normalize.side_effect = fake_normalize
            props = prepare_film(approval, opening, base / "song.mp3", public,
                                 base / "film.json", end_card_seconds=2,
                                 normalize_media=True)
            self.assertEqual(normalize.call_count, 2)
            self.assertTrue(props["shots"][0]["path"].endswith(".png"))
            self.assertTrue(props["opening"]["musicPath"].endswith(".wav"))
            self.assertEqual((base / "photo.jpg").read_bytes(), b"synthetic-photo")
            self.assertEqual((base / "song.mp3").read_bytes(), b"synthetic-song")
            self.assertTrue(props["shots"][0]["path"].startswith("media/story/"))


if __name__ == "__main__":
    unittest.main()

    @patch("sua_media.film.probe_duration_seconds", return_value=9.0)
    def test_heic_requires_normalization(self, probe):
        with tempfile.TemporaryDirectory() as root:
            base = Path(root)
            (base / "photo.heic").write_bytes(b"synthetic-heic")
            (base / "song.mp3").write_bytes(b"synthetic-song")
            approval = base / "approved.json"
            approval.write_text(json.dumps({"shots": [{"source": "photo.heic"}]}))
            opening = base / "opening.json"
            opening.write_text(json.dumps({"imagePaths": []}))
            with self.assertRaisesRegex(ValueError, "HEIC/HEIF"):
                prepare_film(approval, opening, base / "song.mp3",
                             base / "public", base / "film.json", end_card_seconds=2)
