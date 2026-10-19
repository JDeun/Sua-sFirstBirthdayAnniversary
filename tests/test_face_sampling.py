import unittest

from sua_media.faces import select_time_spread


class TemporalSamplingTests(unittest.TestCase):
    def test_balances_early_and_late_months(self):
        records = [
            {"kind": "photo", "captured_at": "2025-12-20T01:00:00",
             "relative_path": f"birth-{i}.jpg", "duplicate_of": None}
            for i in range(100)
        ]
        records.extend([
            {"kind": "photo", "captured_at": "2026-06-20T01:00:00",
             "relative_path": "summer.jpg", "duplicate_of": None},
            {"kind": "photo", "captured_at": "2026-10-01T01:00:00",
             "relative_path": "recent.jpg", "duplicate_of": None},
        ])
        result = select_time_spread(records, 12)
        self.assertEqual(len(result), 12)
        self.assertIn("summer.jpg", [r["relative_path"] for r in result])
        self.assertIn("recent.jpg", [r["relative_path"] for r in result])
        self.assertEqual(
            [r["captured_at"] for r in result],
            sorted(r["captured_at"] for r in result),
        )

    def test_skips_undated_and_duplicates(self):
        rows = [
            {"kind": "photo", "captured_at": None, "relative_path": "unknown.jpg", "duplicate_of": None},
            {"kind": "photo", "captured_at": "2026-01-01", "relative_path": "dup.jpg", "duplicate_of": "orig.jpg"},
            {"kind": "video", "captured_at": "2026-01-01", "relative_path": "clip.mov", "duplicate_of": None},
        ]
        self.assertEqual(select_time_spread(rows, 8), [])

    def test_invalid_max(self):
        with self.assertRaises(ValueError):
            select_time_spread([], 0)


if __name__ == "__main__":
    unittest.main()
