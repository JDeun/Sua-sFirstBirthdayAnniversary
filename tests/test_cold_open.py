import json
from pathlib import Path
import tempfile
import unittest

from sua_media.cold_open import cold_open_markers, configure_cold_open


class ColdOpenTests(unittest.TestCase):
    def test_default_markers(self):
        self.assertEqual(cold_open_markers(12.0, 15.0), {
            "matchcutEndFrame": 240, "birthEndFrame": 360, "songStartFrame": 450,
        })

    def test_invalid_markers(self):
        for title, song in [(0, 15), (15, 12), (12, 12.3), (12, 22),
                            (float("nan"), 15)]:
            with self.subTest(title=title, song=song), self.assertRaises(ValueError):
                cold_open_markers(title, song)

    def test_preserves_approved_image_order_and_supports_sfx(self):
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / "opening-props.json"
            p.write_text(json.dumps({
                "imagePaths": ["media/matchcut/old.png", "media/matchcut/new.png"],
                "musicPath": "",
                "timing": {"verseStartFrame": 360},
            }), encoding="utf-8")
            output = configure_cold_open(
                p, 12.0, 15.0,
                music_path="media/music/suno-complete.wav",
                montage_sfx="media/sfx/montage.wav",
                title_sfx="media/sfx/hit.wav",
            )
            self.assertEqual(output["imagePaths"], [
                "media/matchcut/old.png", "media/matchcut/new.png",
            ])
            self.assertEqual(output["timing"], {
                "matchcutEndFrame": 240, "birthEndFrame": 360, "songStartFrame": 450,
            })
            self.assertEqual(output["musicPath"], "media/music/suno-complete.wav")
            self.assertEqual(output["soundEffects"]["titleImpactPath"], "media/sfx/hit.wav")
            self.assertEqual(json.loads(p.read_text(encoding="utf-8"))["timing"],
                             output["timing"])

    def test_birth_clip_settings(self):
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / 'opening.json'
            p.write_text(json.dumps({'imagePaths': ['media/matchcut/recent.png', 'media/matchcut/newborn.png']}), encoding='utf-8')
            result = configure_cold_open(p, 12, 15, birth_at=8, birth_video='media/birth/clip.mp4', birth_source_start=2.5, birth_audio=True)
            self.assertEqual(result['birthClip'], {'path': 'media/birth/clip.mp4', 'sourceStartFrame': 75, 'withAudio': True})
            self.assertEqual(result['timing']['birthEndFrame'], 360)

    def test_bad_sfx_rejected_without_mutating_props(self):
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / "props.json"
            data = '{"imagePaths":["media/matchcut/1.png"],"musicPath":""}'
            p.write_text(data, encoding="utf-8")
            with self.assertRaises(ValueError):
                configure_cold_open(
                    p, 12, 15, title_sfx="media/sfx/../../../secret.wav",
                )
            self.assertEqual(p.read_text(encoding="utf-8"), data)


if __name__ == "__main__":
    unittest.main()
