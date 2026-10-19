import json
from pathlib import Path
import tempfile
import unittest

from sua_media.matchcut import prepare_matchcut


class MatchCutTests(unittest.TestCase):
    def test_approved_order_and_local_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            aligned = root / "faces"
            aligned.mkdir()
            (aligned / "a.png").write_bytes(b"older")
            (aligned / "b.png").write_bytes(b"newer")
            (aligned / "report.json").write_text(json.dumps({
                "items": [
                    {"output": "a.png", "status": "aligned", "captured_at": "2025-12-19"},
                    {"output": "b.png", "status": "aligned", "captured_at": "2026-09-19"},
                ]
            }), encoding="utf-8")
            selection = root / "approved.json"
            selection.write_text(json.dumps({"approved_outputs": ["a.png", "b.png"]}), encoding="utf-8")
            props = prepare_matchcut(aligned / "report.json", selection,
                                     root / "video/public/media/matchcut",
                                     root / "data/props.json")
            self.assertEqual(props["imagePaths"],
                             ["media/matchcut/a.png", "media/matchcut/b.png"])
            self.assertEqual((aligned / "a.png").read_bytes(), b"older")
            self.assertEqual((root / "video/public/media/matchcut/b.png").read_bytes(), b"newer")

    def test_reject_traversal_and_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "report.json").write_text(json.dumps({"items": [
                {"output": "a.png", "status": "aligned"},
            ]}), encoding="utf-8")
            selection = root / "selection.json"
            selection.write_text(json.dumps({"approved_outputs": ["../../a.png"]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                prepare_matchcut(root / "report.json", selection, root / "public", root / "props.json")


if __name__ == "__main__":
    unittest.main()
