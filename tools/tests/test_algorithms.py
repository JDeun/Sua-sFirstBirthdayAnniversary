"""Small synthetic signals and geometry verify the reusable numerical algorithms."""
import hashlib
from pathlib import Path
import tempfile
import unittest

import numpy as np
from PIL import Image

from analyze_music import measure
from catalog_media import catalog
from check_endpoint_frames import check_frames
from filmtools.cutout import segment
from filmtools.faces import similarity
from filmtools.lyrics import phrase_cue
from filmtools.portraits import apply_tone


class AlgorithmTests(unittest.TestCase):
    def test_similarity_maps_both_eyes_and_rejects_degenerate_annotations(self):
        eyes = np.array([[12, 21], [48, 35]])
        goals = np.array([[100, 80], [200, 80]])
        projected = np.column_stack((eyes, np.ones(2))) @ similarity(eyes, goals).T
        np.testing.assert_allclose(projected, goals, atol=1e-10)
        with self.assertRaises(ValueError):
            similarity([[1, 1], [1, 1]], goals)

    def test_grabcut_keeps_seeded_subject_original_rgb_and_full_canvas(self):
        pixels = np.full((96, 96, 3), 235, dtype='uint8')
        pixels[20:76, 25:71] = [30, 80, 140]
        spec = {'annotation_size': [96, 96], 'envelope': [[15, 10], [80, 10], [80, 85], [15, 85]],
                'foreground': [[[32, 28], [60, 28], [60, 65], [32, 65]]], 'background': []}
        image, report = segment(Image.fromarray(pixels), spec, iterations=2)
        output = np.asarray(image)
        np.testing.assert_array_equal(output[:, :, :3], pixels)
        self.assertEqual(output[40, 40, 3], 255)
        self.assertEqual(output[0, 0, 3], 0)
        self.assertEqual(report['dimensions'], [96, 96])
        spec['background'] = spec['foreground']
        with self.assertRaises(ValueError):
            segment(Image.fromarray(pixels), spec)

    def test_catalog_uses_capture_metadata_and_hash_without_filesystem_date_guess(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            exif = Image.Exif()
            exif[306], exif[274] = '2000:01:02 03:04:05', 6
            Image.new('RGB', (30, 20), 'blue').save(root / 'photo.jpg', exif=exif)
            Image.new('RGB', (20, 20), 'red').save(root / 'undated.png')
            rows = {r['source']: r for r in catalog(root)['sources']}
            self.assertEqual(rows['photo.jpg']['dimensions'], [20, 30])
            self.assertEqual(rows['photo.jpg']['captured_at'], '2000-01-02T03:04:05')
            self.assertIsNone(rows['undated.png']['captured_at'])
            self.assertEqual(rows['photo.jpg']['sha256'], hashlib.sha256((root / 'photo.jpg').read_bytes()).hexdigest())

    def test_word_aligned_cues_reject_partial_word_boundaries(self):
        segment = {'text': 'Bright sky', 'words': [{'word': 'Bright', 'start': 1, 'end': 1.4},
                                                 {'word': 'sky', 'start': 1.5, 'end': 1.9}]}
        cue = phrase_cue(segment, {'id': 'label', 'text': 'sky'}, [1.5, 1.8], 30)
        self.assertEqual((cue['start_frame'], cue['end_frame']), (45, 57))
        self.assertEqual(cue['accent_beat_frames'], [45])
        with self.assertRaises(ValueError):
            phrase_cue(segment, {'id': 'bad', 'text': 'ight'}, [], 30)

    def test_identity_tone_is_bit_exact_and_extreme_controls_rejected(self):
        pixels = np.arange(60, dtype='uint8').reshape(4, 5, 3)
        result, _ = apply_tone(Image.fromarray(pixels))
        np.testing.assert_array_equal(np.asarray(result), pixels)
        with self.assertRaises(ValueError):
            apply_tone(result, exposure_ev=10)

    def test_endpoint_evidence_requires_coverage_and_actual_last_movie_frame(self):
        plan = {'opening': {'duration_in_frames': 10}, 'shots': [
            {'id': 'clip', 'kind': 'video', 'usage': 'baseline', 'song_end_frame': 60,
             'frameLayout': {'media': {'x': 0, 'y': 0, 'width': 100, 'height': 100}}}]}
        manifest = {'canvas_size': [100, 100], 'frames': []}
        with tempfile.TemporaryDirectory() as scratch:
            self.assertEqual(check_frames(plan, manifest, scratch)['status'], 'incomplete')
            Image.new('RGB', (100, 100), 'gray').save(Path(scratch) / 'last.png')
            manifest['frames'] = [{'shot_id': 'clip', 'frame': 69, 'image': 'last.png'}]
            self.assertEqual(check_frames(plan, manifest, scratch)['status'], 'review_required')
            manifest['frames'][0]['frame'] = 68
            with self.assertRaises(ValueError):
                check_frames(plan, manifest, scratch)

    def test_energy_times_use_actual_stride_not_dense_hop(self):
        rate = 22050
        samples = np.zeros(rate * 8, dtype=np.float32)
        for second in np.arange(.5, 7.6, .5):
            start = round(second * rate)
            samples[start:start + 220] = np.hanning(220)
        report = measure(samples, rate)
        times = np.array([r['time'] for r in report['energy']])
        self.assertAlmostEqual(times[-1], (len(times) - 1) * report['energy_hop_seconds'], places=5)
        self.assertGreater(report['tempo_bpm'], 0)
        self.assertGreater(len(report['beats_seconds']), 5)
        self.assertEqual(report['status'], 'measured_listening_review_required')


if __name__ == '__main__':
    unittest.main()
