import unittest

from sua_media.drive import drive_id, safe_component
from sua_media.faces import alignment_matrix


class ImportSafetyTests(unittest.TestCase):
    def test_sanitized_names(self):
        self.assertEqual(safe_component("../../../portrait.jpg"), "_.._.._portrait.jpg")
        self.assertEqual(safe_component("  "), "untitled")
        self.assertEqual(safe_component("a/b\\c"), "a_b_c")

    def test_drive_id_validation(self):
        with self.assertRaises(ValueError):
            drive_id("' OR trashed=false")
        self.assertEqual(drive_id("1Abc_DEfg-h"), "1Abc_DEfg-h")

    def test_alignment_is_optional_dependency(self):
        # Import should not load OpenCV/numpy or require a model on scanner-only installs.
        self.assertTrue(callable(alignment_matrix))


if __name__ == "__main__":
    unittest.main()
