import unittest

from sua_media.music_cuts import plan_cuts


class MusicCutsTests(unittest.TestCase):
    def test_prefers_evenly_spaced_landmarks(self):
        self.assertEqual(plan_cuts(4, 16, [2, 4, 7, 8, 12, 14]), [0.0, 4.0, 8.0, 12.0])

    def test_rejects_insufficient_landmarks(self):
        with self.assertRaisesRegex(ValueError, "Insufficient"):
            plan_cuts(4, 12, [3, 6])

    def test_enforces_minimum_shot_duration(self):
        with self.assertRaises(ValueError):
            plan_cuts(3, 2, [0.5, 1])
        self.assertEqual(plan_cuts(3, 9, [1, 3, 3.5, 6]), [0.0, 3.0, 6.0])

    def test_rejects_invalid_landmarks(self):
        for landmarks in ([0], [12], [-1], [True], [float("nan")], [float("inf")]):
            with self.subTest(landmarks=landmarks), self.assertRaises(ValueError):
                plan_cuts(2, 12, landmarks)

    def test_single_shot(self):
        self.assertEqual(plan_cuts(1, 6, []), [0.0])

    def test_nonfinite_story_length(self):
        for length in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(length=length), self.assertRaises(ValueError):
                plan_cuts(2, length, [1])

    def test_rejects_invalid_shot_count(self):
        for count in (0, -1, True, 2.5):
            with self.subTest(count=count), self.assertRaises(ValueError):
                plan_cuts(count, 12, [3, 6])

    def test_minimum_shot_duration_configurable(self):
        self.assertEqual(plan_cuts(3, 12, [2, 4, 8, 10], min_shot_seconds=3),
                         [0.0, 4.0, 8.0])
        with self.assertRaises(ValueError):
            plan_cuts(3, 12, [2, 4, 8, 10], min_shot_seconds=5)
