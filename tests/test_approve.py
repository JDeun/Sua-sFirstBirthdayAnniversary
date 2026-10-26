"""Approval is explicit, immutable, and local-only."""
import json
from pathlib import Path
import tempfile
import unittest

from sua_media.approve import approve_draft


class ApproveTests(unittest.TestCase):
    def test_requires_confirmation_and_preserves_original(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            draft, approved = root / "draft.json", root / "approved.json"
            data = {"shots": [{"source": "photo.jpg", "cut_at_seconds": 0}],
                    "_draft_music_edit": {"status": "REVIEW_REQUIRED"}}
            draft.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "Explicit"):
                approve_draft(draft, approved, confirmation="yes")
            self.assertFalse(approved.exists())
            result = approve_draft(draft, approved, confirmation="APPROVE")
            self.assertEqual(result["_draft_music_edit"]["status"], "APPROVED")
            self.assertEqual(json.loads(draft.read_text()), data)
            self.assertEqual(json.loads(approved.read_text()), result)
            with self.assertRaises(FileExistsError):
                approve_draft(draft, approved, confirmation="APPROVE")

    def test_rejects_non_draft_and_incomplete_cuts(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            draft, output = root / "draft.json", root / "approved.json"
            draft.write_text(json.dumps({"shots": [{"source": "a.jpg"}],
                                         "_draft_music_edit": {"status": "REVIEW_REQUIRED"}}))
            with self.assertRaisesRegex(ValueError, "cut_at_seconds"):
                approve_draft(draft, output, confirmation="APPROVE")
            self.assertFalse(output.exists())
            draft.write_text(json.dumps({"shots": [{"cut_at_seconds": 0}],
                                         "_draft_music_edit": {"status": "APPROVED"}}))
            with self.assertRaisesRegex(ValueError, "Only REVIEW_REQUIRED"):
                approve_draft(draft, output, confirmation="APPROVE")


if __name__ == "__main__":
    unittest.main()
