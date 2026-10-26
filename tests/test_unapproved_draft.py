"""A music-cut suggestion is never implicit human approval."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from sua_media.film import prepare_film


class UnapprovedDraftTests(unittest.TestCase):
    def test_review_required_blocks_before_any_media_copy(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            approved = root / "draft.json"
            approved.write_text(json.dumps({
                "shots": [{"source": "not-present.jpg", "cut_at_seconds": 0}],
                "_draft_music_edit": {"status": "REVIEW_REQUIRED"}
            }))
            opening = root / "opening.json"
            opening.write_text(json.dumps({"imagePaths": []}))
            with patch("sua_media.film._copy_private") as copy:
                with self.assertRaisesRegex(ValueError, "REVIEW_REQUIRED"):
                    prepare_film(approved, opening, root / "song.mp3",
                                 root / "public", root / "props.json")
                copy.assert_not_called()
            self.assertFalse((root / "props.json").exists())


if __name__ == "__main__":
    unittest.main()
