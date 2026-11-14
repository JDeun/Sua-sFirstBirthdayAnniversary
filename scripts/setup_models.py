"""Verify pinned model bytes; download an optional model only when explicitly requested."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def contained(root, filename):
    relative = PurePosixPath(filename)
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('Model filenames must remain inside the model directory.')
    result = (root / filename).resolve()
    if not result.is_relative_to(root.resolve()):
        raise ValueError('Model path escapes the model directory.')
    return result


def valid(path, item):
    return path.is_file() and path.stat().st_size == item['size_bytes'] and sha256(path) == item['sha256']


def download(item, path):
    url = item['download_url']
    if not url.startswith(('https://media.githubusercontent.com/', 'https://openaipublic.azureedge.net/')):
        raise ValueError('Model URL is outside the pinned official download hosts.')
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.part')
    try:
        with urllib.request.urlopen(url, timeout=30) as source, temporary.open('wb') as target:
            while chunk := source.read(1024 * 1024):
                target.write(chunk)
        if not valid(temporary, item):
            raise ValueError('Downloaded model does not match its pinned SHA256 and size.')
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', help='Model id; default verifies all bundled models.')
    parser.add_argument('--cache-dir', type=Path, default=ROOT / 'models')
    parser.add_argument('--download', action='store_true')
    args = parser.parse_args()
    registry = json.loads((ROOT / 'models/registry.json').read_text())
    selected = [item for item in registry['models'] if item['id'] == args.model or
                args.model is None and item['bundled']]
    if not selected:
        parser.error('Unknown model id.')
    for item in selected:
        bundled = contained(ROOT / 'models', item['filename'])
        path = bundled if valid(bundled, item) else contained(args.cache_dir, item['filename'])
        if not valid(path, item) and args.download:
            download(item, path)
        if not valid(path, item):
            raise SystemExit(f"Missing or invalid {item['id']}; rerun with --download to fetch pinned bytes.")
        print(f"Verified {item['id']}: {path}")


if __name__ == '__main__':
    main()
