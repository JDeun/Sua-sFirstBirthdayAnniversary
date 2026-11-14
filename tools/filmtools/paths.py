"""Explicit roots may be config-relative; references must remain inside those roots."""
import hashlib
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import unicodedata


def relative_name(value):
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise ValueError("Expected a nonempty POSIX relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or PureWindowsPath(value).drive or ":" in value:
        raise ValueError("Absolute paths and URLs are not allowed")
    if any(part in ("", ".", "..") for part in value.split("/")):
        raise ValueError("Reference must not contain empty, dot or parent components")
    return path


def within(root, reference, *, must_exist=True):
    root = Path(root).resolve(strict=True)
    path = root.joinpath(relative_name(reference)).resolve(strict=must_exist)
    if not path.is_relative_to(root) or path == root:
        raise ValueError("Reference escapes its declared root")
    if must_exist and not path.is_file():
        raise ValueError("Reference is not a regular file")
    return path


def config_directory(config_file, value, *, must_exist=True):
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise ValueError("Config directories must be relative POSIX paths")
    if Path(value).is_absolute() or "\x00" in value:
        raise ValueError("Config directories must be relative")
    path = (Path(config_file).resolve().parent / value).resolve(strict=must_exist)
    if must_exist and not path.is_dir():
        raise ValueError("Config source directory does not exist")
    return path


def collision_key(reference):
    return unicodedata.normalize("NFC", str(relative_name(reference))).casefold()


def unique_names(references):
    seen = {}
    for reference in references:
        key = collision_key(reference)
        if key in seen and seen[key] != reference:
            raise ValueError("Case or Unicode path collision")
        seen[key] = reference
    keys = set(seen)
    if any("/".join(key.split("/")[:i]) in keys
           for key in keys for i in range(1, len(key.split("/")))):
        raise ValueError("A file path also names a destination directory")


def sha256(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("Duplicate JSON object key")
            result[key] = value
        return result
    def invalid(value):
        raise ValueError(f"Nonfinite JSON number: {value}")
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=pairs,
                      parse_constant=invalid)


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                    encoding="utf-8")
