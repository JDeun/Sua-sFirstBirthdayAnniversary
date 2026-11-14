"""Timeline and physical source checks for failures that previously reached rendering."""
from copy import deepcopy
import unittest

from build_demo import runtime
from filmtools.edl import validate_edl
from filmtools.endpoints import check_endpoint, check_fit
from filmtools.runtime import validate_runtime


class TimelineTests(unittest.TestCase):
    def setUp(self):
        self.data = runtime()
        self.plan = self.data['narrative-edit.json']

    def test_renamed_derivative_cannot_repeat_a_canonical_original(self):
        self.plan['shots'][1]['canonical_original_source'] = self.plan['shots'][0]['canonical_original_source']
        self.plan['assets']['scene-b']['original'] = self.plan['assets']['scene-a']['original']
        with self.assertRaisesRegex(ValueError, 'Repeated'):
            validate_edl(self.plan, {'excluded_stems': []})

    def test_gaps_overlaps_and_forged_durations_are_rejected(self):
        for field, value in [('song_start_frame', 61), ('song_start_frame', 59), ('duration_in_frames', 59)]:
            plan = deepcopy(self.plan)
            plan['shots'][1][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                validate_edl(plan, {'excluded_stems': []})

    def test_reverse_and_missing_dates_fail_but_precision_overlap_is_explicit(self):
        self.plan['shots'][1]['captured_at'] = '1999-01-01T00:00:00Z'
        with self.assertRaisesRegex(ValueError, 'backwards'):
            validate_edl(self.plan, {'excluded_stems': []})
        self.plan['shots'][1]['captured_at'] = None
        with self.assertRaisesRegex(ValueError, 'unknown_capture'):
            validate_edl(self.plan, {'excluded_stems': []})
        self.plan['shots'][1]['date_basis'] = {'sort_interval': ['1999-12-31', '2000-01-02']}
        report = validate_edl(self.plan, {'excluded_stems': []})
        self.assertFalse(report['chronology_proven'])
        self.assertEqual(report['chronology_review_required'][0]['code'], 'overlapping_date_precision')

    def test_exclusion_applies_across_asset_treatments(self):
        with self.assertRaisesRegex(ValueError, 'excluded'):
            validate_edl(self.plan, {'excluded_stems': ['SCENE-A']})

    def test_last_displayed_frame_with_fractional_rate_and_source_offset(self):
        source = {'fps': 30, 'source_frames': 60, 'duration_seconds': 2}
        self.assertEqual(check_endpoint(120, 30, source, .5)['last_source_frame'], 59)
        with self.assertRaises(ValueError):
            check_endpoint(121, 30, source, .5)
        with self.assertRaises(ValueError):
            check_endpoint(60, 30, source, 1, .1)

    def test_crop_mat_and_foot_define_the_actual_aperture(self):
        asset = {'dimensions': [1600, 1200], 'crop': [.25, 0, .5, 1]}
        layout = {'media': {'x': 1, 'y': 2, 'width': 420, 'height': 650}, 'mat': 10, 'foot': 30}
        self.assertAlmostEqual(check_fit(asset, layout)['relative_aspect_error'], 0)
        layout['media']['height'] = 640
        with self.assertRaises(ValueError):
            check_fit(asset, layout)
        asset['crop'] = [.9, 0, .5, 1]
        with self.assertRaises(ValueError):
            check_fit(asset, layout)

    def test_runtime_fps_boolean_and_bad_word_range_are_rejected(self):
        self.plan['fps'] = True
        with self.assertRaises(ValueError):
            validate_runtime(self.data)
        self.plan['fps'] = 30
        self.data['outro-alignment.json']['lines'][0]['words'][0]['end_frame'] = 121
        with self.assertRaises(ValueError):
            validate_runtime(self.data)


if __name__ == '__main__':
    unittest.main()
