"""Check audio continuity at synthetic opening boundaries without private media."""
from __future__ import annotations

import math
from pathlib import Path
import struct
import subprocess
import sys


def rms_at(path: Path, second: float, duration: float = 0.18) -> float:
    """Decode a short stereo-safe segment to signed 16-bit mono PCM."""
    data = subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", str(second),
         "-i", str(path), "-t", str(duration), "-vn", "-f", "s16le",
         "-ac", "1", "-ar", "16000", "-"],
        check=True, capture_output=True,
    ).stdout
    if not data or len(data) % 2:
        raise AssertionError(f"No PCM samples at {second:.2f}s")
    count = len(data) // 2
    values = struct.unpack(f"<{count}h", data)
    return math.sqrt(sum(v * v for v in values) / count) / 32768


def main() -> None:
    path = Path(sys.argv[1])
    # The MP4 begins at global frame 235; sample windows avoid edit boundaries.
    offset = 235 / 30
    checks = [
        ("pre-birth silence", 7.88, False),
        ("birth natural sound", 9.0, True),
        ("title silence", 13.0, False),
        ("song after frame 450", 15.1, True),
    ]
    for label, absolute, audible in checks:
        level = rms_at(path, absolute - offset)
        print(f"{label}: RMS={level:.6f}")
        if audible and level < 0.004:
            raise AssertionError(f"{label}: expected audible synthetic tone")
        if not audible and level > 0.002:
            raise AssertionError(f"{label}: expected silence")


if __name__ == "__main__":
    main()
