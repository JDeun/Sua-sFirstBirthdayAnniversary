import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from sua_media.catalog import build_catalog, filename_date, infer_date, month_age, parse_date


class ChronologyTests(unittest.TestCase):
    def test_exif_date_has_priority(self):
        result = infer_date("KakaoTalk_20260501_100101.jpg", {"DateTimeOriginal": "2026:04:30 09:20:30"})
        self.assertEqual(result["captured_at"], "2026-04-30T09:20:30")
        self.assertEqual(result["date_source"], "metadata:DateTimeOriginal")

    def test_filename_and_invalid_date(self):
        self.assertEqual(filename_date("IMG_20260304_101122.jpg"), ("2026-03-04T10:11:22", "second"))
        self.assertIsNone(filename_date("IMG_20261340.jpg"))

    def test_kakao_is_not_proven_capture(self):
        result = infer_date("KakaoTalk_20260304_101122.jpg", {})
        self.assertEqual(result["date_confidence"], "low")
        self.assertIn("possible_transfer", result["date_source"])

    def test_unknown_has_no_imaginary_capture_date(self):
        self.assertIsNone(infer_date("IMG_0012.jpg", {})["captured_at"])
        self.assertIsNone(parse_date("0000:00:00 00:00:00"))

    def test_age_month(self):
        self.assertEqual(month_age("2026-02-18", date(2025, 12, 19)), 1)
        self.assertEqual(month_age("2026-02-19", date(2025, 12, 19)), 2)

    def test_exact_duplicates_no_deletion(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "20260101_a.jpg").write_bytes(b"identical")
            (root / "20260102_b.jpg").write_bytes(b"identical")
            (root / "other.jpg").write_bytes(b"different")
            with patch("sua_media.catalog.read_metadata", return_value=({}, [])):
                with patch("sua_media.catalog.visual_hash", return_value=None):
                    output = build_catalog(root)
            self.assertEqual(output["files_total"], 3)
            self.assertEqual(output["exact_duplicates"], 1)
            self.assertEqual(output["unknown_dates"], 1)
            self.assertEqual(len(list(root.glob("*.jpg"))), 3)
            self.assertIsNone(output["media"][-1]["captured_at"])


if __name__ == "__main__":
    unittest.main()
