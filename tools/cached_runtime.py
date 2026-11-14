#!/usr/bin/env python3
"""Run a tool using existing compatible cached wheels, without installation/network."""
import argparse
import os
from pathlib import Path
import platform
import re
import runpy
import sys

MODULES = ("numpy", "scipy", "numba", "llvmlite", "librosa", "sklearn", "soundfile",
           "soxr", "msgpack", "lazy_loader", "decorator", "joblib", "threadpoolctl",
           "pooch", "packaging", "requests", "urllib3", "certifi", "charset_normalizer",
           "idna", "platformdirs", "audioread", "typing_extensions", "PIL", "cv2",
           "_cffi_backend", "cffi", "pycparser", "setuptools", "six", "cloudpickle",
           "pillow_heif")


def compatible(folder):
    arch = platform.machine()
    for wheel in folder.glob("*.dist-info/WHEEL"):
        for line in wheel.read_text().splitlines():
            if not line.startswith("Tag: "):
                continue
            interpreter, abi, target = line[5:].split("-", 2)
            if target == "any" and abi == "none" and "py3" in interpreter.split("."):
                return True
            native = (sys.platform == "darwin" and target.startswith("macosx_") and
                      (target.endswith(arch) or target.endswith("universal2")))
            limited = abi == "abi3" and interpreter.startswith("cp3") and int(interpreter[3:]) <= 11
            generic = abi == "none" and "py3" in interpreter.split(".")
            if native and ((interpreter == "cp311" and abi == "cp311") or limited or generic):
                return True
    return False


def contains(folder, module):
    return ((folder / module).exists() or (folder / (module + ".py")).exists()
            or any(folder.glob(module + "*.so")))


def activate(cache_directory, scratch_directory):
    if sys.version_info[:2] != (3, 11):
        raise RuntimeError("Use Python 3.11 for the cached binary dependencies")
    sys.dont_write_bytecode = True
    folders = sorted(p for p in Path(cache_directory).iterdir() if p.is_dir() and compatible(p))
    selected = [next((p for p in folders if contains(p, module)), None) for module in MODULES]
    paths = list(dict.fromkeys(str(p) for p in selected if p is not None))
    sys.path[:0] = paths
    for variable, suffix in (("NUMBA_CACHE_DIR", "numba"), ("MPLCONFIGDIR", "matplotlib"),
                             ("XDG_CACHE_HOME", "xdg")):
        directory = Path(scratch_directory) / suffix
        directory.mkdir(parents=True, exist_ok=True)
        os.environ[variable] = str(directory.resolve())
    return paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-directory", type=Path, default=Path.home() / ".cache/uv/archive-v0")
    parser.add_argument("--scratch-directory", type=Path, required=True)
    parser.add_argument("script", type=Path)
    parser.add_argument("arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    activate(args.cache_directory, args.scratch_directory)
    script = args.script.resolve(strict=True)
    sys.argv = [str(script), *args.arguments]
    sys.path.insert(0, str(script.parent))
    runpy.run_path(str(script), run_name="__main__")


if __name__ == "__main__":
    main()
