"""Synthetic geometry only: reusable alignment, explicit approval and safe batches."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

import numpy as np
from PIL import Image, ImageDraw

import build_matchcut
import face_matchcut
from face_matchcut import align_image, detect, overlap, restore, rotation, similarity
from filmtools import faces as compatibility

TOOLS = Path(__file__).resolve().parents[1]
EYES = [[28, 24], [68, 24]]


def geometric_image(color="red"):
    image = Image.new("RGB", (96, 80), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((24, 20, 32, 28), fill=color)
    draw.rectangle((64, 20, 72, 28), fill="green")
    draw.polygon(((48, 40), (40, 60), (56, 60)), fill="blue")
    return image


def detector_row(bbox, points, confidence=.9):
    return np.array([*bbox, *np.asarray(points).reshape(-1), confidence], dtype=float)


class GeometryTests(unittest.TestCase):
    def test_compatibility_exports_are_the_same_functions(self):
        for name in face_matchcut.__all__:
            self.assertIs(getattr(compatibility, name), getattr(face_matchcut, name))

    def test_package_imports_in_isolation_without_filmtools(self):
        with tempfile.TemporaryDirectory() as scratch:
            shutil.copytree(TOOLS / "face_matchcut", Path(scratch) / "face_matchcut")
            script = (f"import sys; sys.path.insert(0, {scratch!r}); import face_matchcut; "
                      "assert not any(k.startswith('filmtools') for k in sys.modules)")
            result = subprocess.run([sys.executable, "-I", "-S", "-B", "-c", script],
                                    cwd=scratch, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_exact_similarity_matrix_and_no_reflection(self):
        expected = np.array([[0, -2, 14], [2, 0, 18]], dtype=float)
        matrix = similarity([[1, 2], [5, 2]], [[10, 20], [10, 28]])
        np.testing.assert_array_equal(matrix, expected)
        for targets in ([[10, 20], [10, 28]], [[10, 20], [2, 20]], [[10, 20], [2, 12]]):
            matrix = similarity([[1, 2], [5, 2]], targets)
            self.assertGreater(np.linalg.det(matrix[:, :2]), 0)
            np.testing.assert_allclose(np.c_[np.array([[1, 2], [5, 2]]), np.ones(2)] @ matrix.T, targets)

    def test_degenerate_and_nonfinite_coordinates_are_rejected(self):
        for eyes, targets in (([[1, 1], [1, 1]], EYES), (EYES, [[1, 1], [1, 1]]),
                              ([[float("nan"), 0], [1, 1]], EYES), ([[0, 0]], EYES),
                              (EYES, [[0, 0], [float("inf"), 1]])):
            with self.subTest(eyes=eyes, targets=targets), self.assertRaises(ValueError):
                similarity(eyes, targets)

    def test_all_quarter_turns_preserve_coordinates_and_original_pixels(self):
        image = geometric_image()
        pixels = np.asarray(image)
        for turns in range(4):
            rotated, forward = rotation(pixels, turns)
            np.testing.assert_array_equal(rotated, np.rot90(pixels, -turns))
            eyes = (np.c_[np.array(EYES), np.ones(2)] @ forward.T)[:, :2]
            result, evidence = align_image(Image.fromarray(rotated), eyes, EYES, image.size, feather=1, blur=0)
            with self.subTest(turns=turns):
                np.testing.assert_array_equal(np.asarray(result), pixels)
                self.assertLess(evidence["eye_error_px"], 1e-10)
                self.assertGreater(np.linalg.det(np.array(evidence["matrix"])[:, :2]), 0)

    def test_restoration_undoes_rotation_and_detector_resize(self):
        points = np.array([[48, 20], [28, 20], [38, 27], [29, 36], [47, 36]])
        corners = np.array([[20, 12], [60, 12], [20, 40], [60, 40]])
        for turns in range(4):
            _, forward = rotation(np.zeros((40, 48, 3), dtype="uint8"), turns)
            rotated = (np.c_[corners * .5, np.ones(4)] @ forward.T)[:, :2]
            left, top = rotated.min(axis=0)
            width, height = rotated.max(axis=0) - [left, top]
            landmarks = (np.c_[points * .5, np.ones(5)] @ forward.T)[:, :2]
            result = restore(detector_row([left, top, width, height], landmarks),
                             np.linalg.inv(forward), .5, turns)
            np.testing.assert_allclose(result["bbox"], [20, 12, 40, 28])
            np.testing.assert_allclose(result["landmarks"], points)
            self.assertEqual(result["eyes"], [[28., 20.], [48., 20.]])
            self.assertEqual(result["detection_rotation"], turns * 90)
        self.assertEqual(overlap([0, 0, 10, 10], [20, 20, 2, 2]), 0)
        self.assertEqual(overlap([0, 0, 10, 10], [0, 0, 10, 10]), 1)

    def test_detection_keeps_candidates_in_x_order_without_selecting_largest(self):
        import cv2
        small = detector_row([5, 5, 12, 12], [[7, 8], [12, 8], [10, 10], [8, 13], [12, 13]], .8)
        large = detector_row([40, 5, 40, 50], [[45, 15], [65, 15], [55, 25], [45, 40], [65, 40]], .95)
        model = Mock()
        model.detect.side_effect = [(None, np.array([large, small, small])), (None, None),
                                    (None, None), (None, None)]
        with patch.object(cv2.FaceDetectorYN, "create", return_value=model):
            candidates = detect(geometric_image(), "unused-local-model.onnx")
        self.assertEqual(len(candidates), 2)
        self.assertEqual([face["bbox"][0] for face in candidates], [5, 40])
        self.assertEqual(model.setInputSize.call_count, 4)


class BatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / "project"
        (self.project / "photos").mkdir(parents=True)
        self.config = self.project / "approved.json"
        self.output = self.root / "export"
        geometric_image().save(self.project / "photos/a.png")
        geometric_image("yellow").save(self.project / "photos/b.png")
        self.data = {"version": 1, "canvas": {"width": 96, "height": 80, "target_eyes": EYES},
                     "photos": [self.photo("z-first", "photos/b.png", captured_at="2001-01-01"),
                                self.photo("../../a:second", "photos/a.png")]}

    def photo(self, identifier, source, **extra):
        digest = hashlib.sha256((self.project / source).read_bytes()).hexdigest()
        return {"id": identifier, "source": source, "source_sha256": digest, "eyes": EYES, **extra}

    def build(self, data=None, output=None):
        self.config.write_text(json.dumps(self.data if data is None else data), encoding="utf-8")
        return build_matchcut.build(self.config, self.output if output is None else output)

    def assert_rejected(self, data, message=None):
        with self.assertRaisesRegex((ValueError, OSError), message or ".*"):
            self.build(data)
        self.assertFalse(self.output.exists())
        self.assertFalse(list(self.root.glob(".matchcut-*")))

    def test_portable_output_order_names_settings_and_hash_evidence(self):
        original = deepcopy(self.data)
        manifest = self.build()
        self.assertEqual(self.data, original)
        expected = [{"id": "z-first", "asset": "photo-000001.png", "captured_at": "2001-01-01"},
                    {"id": "../../a:second", "asset": "photo-000002.png"}]
        self.assertEqual(manifest["photos"], expected)
        self.assertEqual(manifest["settings"]["canvas"], self.data["canvas"])
        self.assertEqual(manifest["settings"]["selection"], "explicit_eyes")
        self.assertEqual(manifest["status"], "visual_review_required")
        self.assertEqual(json.loads((self.output / "manifest.json").read_text()), manifest)
        relocated = self.root / "relocated"
        shutil.copytree(self.output, relocated)
        for photo, evidence, approved in zip(manifest["photos"], manifest["evidence"], self.data["photos"]):
            image = relocated / photo["asset"]
            with Image.open(image) as opened:
                self.assertEqual(opened.size, (96, 80))
            self.assertEqual(evidence["output_sha256"], hashlib.sha256(image.read_bytes()).hexdigest())
            self.assertEqual(evidence["source_sha256"], approved["source_sha256"])
            self.assertLess(evidence["eye_error_px"], 1e-10)
            self.assertNotIn(approved["source"], json.dumps(manifest))
        self.assertNotIn(str(self.project), json.dumps(manifest))

    def test_exif_rotation_uses_approved_upright_coordinates(self):
        source = self.project / "photos/rotated.png"
        exif = Image.Exif()
        exif[274] = 6
        geometric_image().save(source, exif=exif)
        _, forward = rotation(np.asarray(geometric_image()), 1)
        eyes = (np.c_[np.array(EYES), np.ones(2)] @ forward.T)[:, :2].tolist()
        photo = {**self.photo("rotated", "photos/rotated.png"), "eyes": eyes}
        manifest = self.build({**self.data, "photos": [photo]})
        self.assertEqual(manifest["evidence"][0]["source_dimensions"], [80, 96])
        with Image.open(self.output / manifest["photos"][0]["asset"]) as result:
            np.testing.assert_array_equal(np.asarray(result), np.asarray(geometric_image()))
            self.assertNotIn(274, result.getexif())

    def test_duplicate_ids_and_source_aliases_are_rejected(self):
        first, second = self.data["photos"]
        aliases = [first["source"], "photos/symlink.png", "photos/hardlink.png"]
        (self.project / aliases[1]).symlink_to(self.project / first["source"])
        (self.project / aliases[2]).hardlink_to(self.project / first["source"])
        self.assert_rejected({**self.data, "photos": [first, {**second, "id": first["id"]}]}, "Duplicate photo id")
        for source in aliases:
            photo = {**first, "id": "distinct", "source": source}
            with self.subTest(source=source):
                self.assert_rejected({**self.data, "photos": [first, photo]}, "Duplicate physical source")

    def test_missing_malformed_and_mismatched_hashes_are_rejected(self):
        first = self.data["photos"][0]
        missing = {key: value for key, value in first.items() if key != "source_sha256"}
        for photo in (missing, {**first, "source_sha256": "bad"}, {**first, "source_sha256": "0" * 64}):
            with self.subTest(photo=photo):
                self.assert_rejected({**self.data, "photos": [photo]}, "SHA256|hash differs")

    def test_source_change_after_hash_preflight_is_rejected_before_publication(self):
        original = build_matchcut._approved_image
        def changed(photo):
            if photo["id"] == self.data["photos"][1]["id"]:
                photo["source"].write_bytes(b"changed synthetic input")
            return original(photo)
        with patch("build_matchcut._approved_image", side_effect=changed):
            self.assert_rejected(self.data, "hash differs")

    def test_explicit_eyes_and_valid_canvas_dates_are_required(self):
        first = self.data["photos"][0]
        bad_rows = [{**first, "eyes": value} for value in (None, [], [[1, 1], [1, 1]],
                    [[-1, 0], [4, 4]], [[1, 1], [96, 2]], [[True, 1], [4, 4]])]
        bad_rows += [{**first, "captured_at": value} for value in (None, "", "unknown")]
        for photo in bad_rows:
            with self.subTest(photo=photo):
                self.assert_rejected({**self.data, "photos": [photo]})
        for canvas in ({**self.data["canvas"], "width": True}, {**self.data["canvas"], "height": 0},
                       {**self.data["canvas"], "target_eyes": [[1, 1], [1, 1]]}):
            self.assert_rejected({**self.data, "canvas": canvas})
        for version in (True, 2, "1"):
            self.assert_rejected({**self.data, "version": version})

    def test_source_paths_cannot_escape_config_directory(self):
        outside = self.root / "outside.png"
        outside.write_bytes((self.project / "photos/b.png").read_bytes())
        (self.project / "photos/escape.png").symlink_to(outside)
        first = self.data["photos"][0]
        for source in (str(outside), "../outside.png", "photos/escape.png", "C:/photo.png", "https://host/photo.png"):
            with self.subTest(source=source):
                self.assert_rejected({**self.data, "photos": [{**first, "source": source}]})

    def test_explicit_sibling_source_base_is_config_relative_and_not_published(self):
        source_base = self.root / "media/photos"
        shutil.copytree(self.project / "photos", source_base)
        private = self.project / "private"
        private.mkdir()
        self.config = private / "approved.json"
        photos = [{**photo, "source": Path(photo["source"]).name} for photo in self.data["photos"]]
        data = {**self.data, "source_directory": "../../media/photos", "photos": photos}
        manifest = self.build(data)
        self.assertEqual([photo["id"] for photo in manifest["photos"]], [photo["id"] for photo in photos])
        for value in ("source_directory", "../../media/photos", str(source_base)):
            self.assertNotIn(value, json.dumps(manifest))
        for output in (source_base / "aligned", source_base, source_base.parent):
            with self.subTest(output=output), self.assertRaisesRegex(ValueError, "overlaps an input"):
                self.build(data, output=output)
        # The explicit media base allows aligned assets beside private configs.
        self.build(data, output=private / "aligned")

    def test_explicit_source_base_still_rejects_traversal_and_escaping_links(self):
        source_base = self.root / "media/photos"
        source_base.mkdir(parents=True)
        outside = source_base.parent / "outside.png"
        outside.write_bytes((self.project / "photos/b.png").read_bytes())
        (source_base / "escape.png").symlink_to(outside)
        first = self.data["photos"][0]
        for source in ("../outside.png", "nested/../../outside.png", "escape.png", str(outside)):
            data = {**self.data, "source_directory": "../media/photos",
                    "photos": [{**first, "source": source}]}
            with self.subTest(source=source):
                self.assert_rejected(data)
        for directory in (None, str(source_base), "missing", "https://host/media"):
            with self.subTest(source_directory=directory):
                self.assert_rejected({**self.data, "source_directory": directory})

    def test_existing_outputs_files_and_symlinks_are_preserved(self):
        directory, file = self.root / "existing", self.root / "sentinel"
        directory.mkdir()
        file.write_text("keep")
        link, dangling = self.root / "link", self.root / "dangling"
        link.symlink_to(directory, target_is_directory=True)
        dangling.symlink_to(self.root / "absent", target_is_directory=True)
        for output in (directory, file, link, dangling):
            with self.subTest(output=output), self.assertRaisesRegex(ValueError, "already exist"):
                self.build(output=output)
        self.assertEqual(list(directory.iterdir()), [])
        self.assertEqual(file.read_text(), "keep")
        self.assertTrue(link.is_symlink() and dangling.is_symlink())

    def test_input_overlap_is_refused_and_source_bytes_are_unchanged(self):
        source = self.project / self.data["photos"][0]["source"]
        before = source.read_bytes()
        for output in (self.project, self.root, source, source.parent, self.config, self.project / "aligned"):
            with self.subTest(output=output), self.assertRaisesRegex(ValueError, "overlaps an input"):
                self.build(output=output)
        self.assertEqual(source.read_bytes(), before)

    def test_render_failure_leaves_no_output_or_staging_files(self):
        with patch("build_matchcut.align_image", side_effect=[align_image(geometric_image(), EYES, EYES, (96, 80)),
                                                              ValueError("simulated render failure")]):
            self.assert_rejected(self.data, "simulated render failure")

    def test_racing_existing_directory_is_never_replaced(self):
        original = build_matchcut._publish
        def race(stage, output, names):
            output.mkdir()
            (output / "foreign.txt").write_text("keep")
            return original(stage, output, names)
        with patch("build_matchcut._publish", side_effect=race), self.assertRaises(FileExistsError):
            self.build()
        self.assertEqual([path.name for path in self.output.iterdir()], ["foreign.txt"])
        self.assertEqual((self.output / "foreign.txt").read_text(), "keep")
        self.assertFalse(list(self.root.glob(".matchcut-*")))

    def test_publish_collision_rolls_back_only_owned_files(self):
        original = Path.hardlink_to
        def collide(target, source):
            if target.name == "photo-000002.png":
                target.write_text("concurrent file")
            return original(target, source)
        with patch.object(Path, "hardlink_to", new=collide), self.assertRaises(FileExistsError):
            self.build()
        self.assertEqual([path.name for path in self.output.iterdir()], ["photo-000002.png"])
        self.assertEqual((self.output / "photo-000002.png").read_text(), "concurrent file")
        self.assertFalse(list(self.root.glob(".matchcut-*")))

    def test_duplicate_json_keys_and_nonfinite_values_are_rejected(self):
        for contents in ('{"version":1,"version":1}', '{"version":1,"canvas":{"width":NaN}}'):
            self.config.write_text(contents)
            with self.assertRaises(ValueError):
                build_matchcut.build(self.config, self.output)
        self.assertFalse(self.output.exists())

    def test_help_documents_required_flags_and_approval_coordinates(self):
        result = subprocess.run([sys.executable, "-B", str(TOOLS / "build_matchcut.py"), "--help"],
                                cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        for text in ("--config", "--output-directory", "source_sha256", "EXIF-upright", "photo-000001.png",
                     "source_directory", "../../media/photos"):
            self.assertIn(text, result.stdout)


if __name__ == "__main__":
    unittest.main()
