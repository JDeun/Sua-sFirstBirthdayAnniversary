import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/audit_public.py'
SPEC = importlib.util.spec_from_file_location('audit_public', SCRIPT)
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class PublicationBoundaryTests(unittest.TestCase):
    def test_runtime_and_original_paths_cannot_be_exported(self):
        for name in ['private/project.json', 'media/photo.jpg',
                     'renderer/src/generated/plan.json', 'work/result.json']:
            with self.subTest(name=name), self.assertRaises(ValueError):
                AUDIT.check_path(name, {})

    def test_family_phrase_is_rejected_without_publishing_the_phrase_list(self):
        phrase = 'local family sentence'
        with self.assertRaises(ValueError):
            AUDIT.check_text('docs/test.md', phrase.encode(), [AUDIT.normalize(phrase)])

    def test_source_symlink_cannot_export_an_external_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'repo'
            (root / 'docs').mkdir(parents=True)
            secret = Path(directory) / 'local.txt'
            secret.write_text('unrelated local data')
            (root / 'docs/linked.md').symlink_to(secret)
            with self.assertRaises(ValueError):
                AUDIT.source_files(root)

    def test_large_encoded_payload_is_rejected_even_in_a_text_file(self):
        with self.assertRaises(ValueError):
            AUDIT.check_text('docs/example.md', b'Z' * 3000, [])

    def test_only_declared_runtime_links_are_excluded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'repo'
            (root / 'renderer/src').mkdir(parents=True)
            source = Path(directory) / 'runtime'
            source.mkdir()
            (source / 'data.json').write_text('{}')
            (root / 'renderer/src/generated').symlink_to(source, target_is_directory=True)
            self.assertEqual(AUDIT.source_files(root), [])

    def test_escaped_json_values_and_keys_are_also_checked(self):
        phrase = '비공개 테스트 문구'
        for data in [{'value': phrase}, {phrase: 'value'}]:
            with self.subTest(data=data), self.assertRaises(ValueError):
                AUDIT.check_text('examples/test.json', json.dumps(data).encode(), [AUDIT.normalize(phrase)])

    def test_escaped_json_local_path_is_rejected(self):
        path = chr(47) + 'Users/example/data'
        encoded = json.dumps({'path': path}).replace('/', r'\u002f').encode()
        with self.assertRaises(ValueError):
            AUDIT.check_text('examples/test.json', encoded, [])

    def test_private_phrase_in_filename_is_rejected(self):
        phrase = 'private family label'
        with self.assertRaises(ValueError):
            AUDIT.sensitive_text('docs/' + phrase + '.json', 'docs/' + phrase + '.json',
                                 [AUDIT.normalize(phrase)])

    def test_duplicate_json_key_cannot_discard_an_escaped_private_value(self):
        phrase = '비공개 테스트 문구'
        payload = '{"name": ' + json.dumps(phrase) + ', "name": "public"}'
        self.assertEqual(json.loads(payload)['name'], 'public')
        with self.assertRaises(ValueError):
            AUDIT.check_text('examples/test.json', payload.encode(), [AUDIT.normalize(phrase)])


if __name__ == '__main__':
    unittest.main()
