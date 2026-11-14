"""Containment, collision, and transaction regressions using isolated projects."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from build_demo import build
from filmtools.paths import read_json, unique_names, within, write_json
from prepare_project import commit_jobs, prepare


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.demo = self.root / 'project'
        build(self.demo)
        self.config = self.demo / 'project.json'
        config = read_json(self.config)
        write_json(self.config, {**config, 'renderer_directory': '../renderer'})

    def test_config_is_relative_to_file_and_check_is_read_only(self):
        report = prepare(self.config, check_only=True)
        self.assertEqual(report['runtime_files'], 8)
        self.assertFalse((self.root / 'renderer').exists())
        prepare(self.config, copy_assets=True)
        target = self.root / 'renderer/public/demo/scene-a.svg'
        self.assertEqual(target.read_bytes(), (self.demo / 'assets/demo/scene-a.svg').read_bytes())
        self.assertEqual(len(list((self.root / 'renderer/src/generated').glob('*.json'))), 8)

    def test_existing_different_asset_rejected_before_runtime_writes(self):
        target = self.root / 'renderer/public/demo/scene-a.svg'
        target.parent.mkdir(parents=True)
        target.write_text('unrelated content')
        with self.assertRaisesRegex(ValueError, 'collision'):
            prepare(self.config)
        self.assertFalse((self.root / 'renderer/src/generated').exists())
        self.assertEqual(target.read_text(), 'unrelated content')

    def test_source_and_destination_parent_symlink_escape(self):
        outside = self.root / 'outside'
        outside.mkdir()
        (outside / 'secret').write_text('unrelated')
        (self.demo / 'assets/link').symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError):
            within(self.demo / 'assets', 'link/secret')
        public = self.root / 'renderer/public'
        public.mkdir(parents=True)
        (public / 'demo').symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'escapes'):
            prepare(self.config)

    def test_explicit_root_symlinks_are_noop_and_never_written_through(self):
        renderer = self.root / 'renderer'
        (renderer / 'src').mkdir(parents=True)
        (renderer / 'src/generated').symlink_to(self.demo / 'runtime', target_is_directory=True)
        (renderer / 'public').symlink_to(self.demo / 'assets', target_is_directory=True)
        before = {p.name: p.read_bytes() for p in (self.demo / 'runtime').iterdir()}
        self.assertEqual(prepare(self.config)['status'], 'prepared')
        self.assertEqual(before, {p.name: p.read_bytes() for p in (self.demo / 'runtime').iterdir()})

    def test_unicode_case_and_file_directory_collisions(self):
        for names in (['photos/A.jpg', 'photos/a.jpg'], ['café.jpg', 'cafe\u0301.jpg'], ['a', 'a/b']):
            with self.subTest(names=names), self.assertRaises(ValueError):
                unique_names(names)
        for reference in ('../x', '/x', 'C:/x', 'x\\y', 'x//y', 'x/./y', 'https://host/x'):
            with self.subTest(reference=reference), self.assertRaises(ValueError):
                within(self.demo, reference)

    def test_repeated_content_under_different_original_names_is_rejected(self):
        first, second = (self.demo / 'sources' / n for n in ('scene-a.svg', 'scene-b.svg'))
        second.write_bytes(first.read_bytes())
        with self.assertRaisesRegex(ValueError, 'duplicate content'):
            prepare(self.config)

    def test_live_asset_hash_is_enforced_but_unused_old_evidence_is_ignored(self):
        path = self.demo / 'runtime/narrative-media.json'
        evidence = read_json(path)
        evidence['assets']['unused'] = {'asset': 'absent/old.mp4', 'output_sha256': '0' * 64}
        write_json(path, evidence)
        self.assertEqual(prepare(self.config, check_only=True)['referenced_assets'], 2)
        evidence['assets']['scene-a']['output_sha256'] = '0' * 64
        write_json(path, evidence)
        with self.assertRaisesRegex(ValueError, 'hash differs'):
            prepare(self.config)
        self.assertFalse((self.root / 'renderer').exists())

    def test_copy_fallback_when_relative_symlinks_are_unavailable(self):
        with patch('pathlib.Path.symlink_to', side_effect=OSError('links unavailable')):
            prepare(self.config)
        target = self.root / 'renderer/public/demo/scene-a.svg'
        self.assertFalse(target.is_symlink())
        self.assertEqual(target.read_bytes(), (self.demo / 'assets/demo/scene-a.svg').read_bytes())

    def test_failed_transaction_restores_existing_runtime(self):
        source = self.root / 'source'
        source.write_text('new')
        target = self.root / 'target'
        target.write_text('old')
        other = self.root / 'other'
        import os
        original = os.replace
        def fail_second(src, dst):
            if Path(dst) == other:
                raise OSError('simulated disk failure')
            return original(src, dst)
        with patch('prepare_project.os.replace', side_effect=fail_second), self.assertRaises(OSError):
            commit_jobs([(source, target, 'copy'), (source, other, 'copy')])
        self.assertEqual(target.read_text(), 'old')
        self.assertFalse(other.exists())
        self.assertFalse(list(self.root.glob('*.film-stage-tmp')))

    def test_duplicate_json_keys_and_nonfinite_inputs_are_rejected(self):
        path = self.root / 'bad.json'
        for text in ('{"x":1,"x":2}', '{"x":NaN}'):
            path.write_text(text)
            with self.assertRaises(ValueError):
                read_json(path)


if __name__ == '__main__':
    unittest.main()
