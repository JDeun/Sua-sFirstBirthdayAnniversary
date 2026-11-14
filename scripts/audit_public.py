"""Allowlist public source files and reject accidental family data before export."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
TOP_FILES = {'README.md', 'AGENTS.md', '.gitignore', 'package.json', 'package-lock.json',
             'requirements.txt', 'pyproject.toml', 'LICENSE', 'NOTICE', '.gitattributes',
             'THIRD_PARTY_NOTICES.md'}
TOP_DIRS = {'renderer', 'tools', 'scripts', 'schemas', 'examples', 'tests', 'docs', 'models', '.github'}
TEXT_SUFFIXES = {'.py', '.ts', '.tsx', '.mjs', '.cjs', '.json', '.md', '.txt', '.yml',
                 '.yaml', '.toml', '.svg', '.gitignore', '.gitattributes'}
EXCLUDED = {'renderer/node_modules', 'renderer/public', 'renderer/src/generated',
            'renderer/.cache', 'renderer/build', 'renderer/output', 'examples/demo/output',
            '.git', '.cache', '.venv'}
EXCLUDED_FILES = {'renderer/project.local.json'}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def normalize(text):
    return re.sub(r'[^\w]', '', unicodedata.normalize('NFC', text)).casefold()


def private_phrases(args):
    phrases = []
    for path, minimum in [(args.lyrics_file, 4), (args.private_tokens, 2)]:
        if not path:
            continue
        for line in path.read_text().splitlines():
            clean = normalize(line)
            if len(clean) >= minimum and not line.lstrip().startswith(('#', '[')):
                phrases.append(clean)
    return phrases


def model_allowlist(root):
    registry = json.loads((root / 'models/registry.json').read_text())
    result = {}
    for model in registry['models']:
        if not model['bundled']:
            continue
        name = PurePosixPath(model['filename'])
        if name.is_absolute() or '..' in name.parts or name.suffix != '.onnx':
            raise ValueError('Bundled model path must be a contained ONNX file.')
        if not re.fullmatch(r'[0-9a-f]{64}', model['sha256']):
            raise ValueError('Model requires a pinned SHA256.')
        result['models/' + str(name)] = model
    return result


def source_files(root):
    result = []
    for directory, dirs, files in os.walk(root, followlinks=False):
        base = Path(directory)
        dirs[:] = [name for name in dirs if (base / name).relative_to(root).as_posix() not in EXCLUDED
                   and name not in {'__pycache__', 'node_modules', '.git'}]
        for name in dirs:
            if (base / name).is_symlink():
                raise ValueError('Unexpected source symlink: ' + str((base / name).relative_to(root)))
        for name in files:
            if name == '.DS_Store' or name.endswith(('.pyc', '.pyo')):
                continue
            path = base / name
            if path.relative_to(root).as_posix() in EXCLUDED_FILES:
                continue
            if path.is_symlink():
                raise ValueError('Unexpected file symlink: ' + str(path.relative_to(root)))
            result.append(path)
    return sorted(result)


def check_path(relative, models):
    parts = relative.split('/')
    if len(parts) == 1:
        if relative not in TOP_FILES:
            raise ValueError('Unapproved root file: ' + relative)
    elif parts[0] not in TOP_DIRS:
        raise ValueError('Unapproved source directory: ' + relative)
    if relative.startswith('renderer/') and relative.endswith('.json') and relative not in {
            'renderer/package.json', 'renderer/package-lock.json', 'renderer/tsconfig.json'}:
        raise ValueError('Unapproved renderer data file: ' + relative)
    if relative in models:
        return
    path = Path(relative)
    if path.suffix not in TEXT_SUFFIXES and path.name not in {'LICENSE', 'NOTICE', '.gitignore'}:
        raise ValueError('Unapproved file type: ' + relative)
    if any(part.casefold() in {'private', 'media', 'output', 'work', 'generated'} for part in parts):
        raise ValueError('Private/generated path in export: ' + relative)


def sensitive_text(relative, text, phrases):
    forbidden = [chr(47) + 'Users/', chr(67) + ':\\Users\\', 'personal_' + 'work/',
                 'data:image/' + 'jpeg;base64,', 'data:image/' + 'png;base64,']
    if any(value in text for value in forbidden):
        raise ValueError('Local path or embedded photograph found: ' + relative)
    if re.search(r'IMG_' + r'\d{4}|_talkv_' + r'[A-Za-z0-9]', text):
        raise ValueError('Personal source filename found: ' + relative)
    if re.search(r'[A-Za-z0-9+/]{2048,}={0,2}', text):
        raise ValueError('Unexpected embedded binary payload: ' + relative)
    normalized = normalize(text)
    if any(phrase in normalized for phrase in phrases):
        raise ValueError('Private lyric or project text found: ' + relative)


def json_strings(value):
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [text for child in value for text in json_strings(child)]
    if isinstance(value, dict):
        return [text for key, child in value.items() for text in [key, *json_strings(child)]]
    return []


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON keys are not allowed in a public file.')
        result[key] = value
    return result


def check_text(relative, raw, phrases):
    text = raw.decode('utf-8')
    sensitive_text(relative, text, phrases)
    if relative.endswith('.json'):
        # Decode keys and values, so escaped names/paths cannot bypass the scan.
        decoded = '\n'.join(json_strings(json.loads(text, object_pairs_hook=unique_object)))
    else:
        decoded = re.sub(r'\\u([0-9a-fA-F]{4})', lambda match: chr(int(match[1], 16)), text)
    sensitive_text(relative, decoded, phrases)


def audit(root, phrases):
    models, records = model_allowlist(root), []
    for path in source_files(root):
        relative = path.relative_to(root).as_posix()
        check_path(relative, models)
        sensitive_text(relative, relative, phrases)
        raw = path.read_bytes()
        if relative in models:
            item = models[relative]
            if digest(raw) != item['sha256'] or len(raw) != item['size_bytes']:
                raise ValueError('Model bytes differ from the pinned registry: ' + relative)
        else:
            check_text(relative, raw, phrases)
        records.append({'path': relative, 'size': len(raw), 'sha256': digest(raw),
                        'binary_model': relative in models})
    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--lyrics-file', type=Path)
    parser.add_argument('--private-tokens', type=Path)
    parser.add_argument('--manifest', type=Path)
    args = parser.parse_args()
    records = audit(args.root.resolve(), private_phrases(args))
    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps({'status': 'passed', 'files': records}, indent=2) + '\n')
    print(f'Public export passed: {len(records)} allowlisted files; no personal media or lyric input included.')


if __name__ == '__main__':
    main()
