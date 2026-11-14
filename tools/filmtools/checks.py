"""Numerical guards shared by runtime, geometry, and media checks."""
import math


def number(value, label, *, minimum=None, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{label} must be a finite number")
    if (minimum is not None and value < minimum) or (positive and value <= 0):
        raise ValueError(f"{label} is out of range")
    return value


def integer(value, label, *, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError(f"{label} must be an integer >= {minimum}")
    return value


def vector(value, length, label, *, positive=False):
    if not isinstance(value, (list, tuple)) or len(value) != length:
        raise ValueError(f"{label} must have {length} entries")
    return [number(x, label, positive=positive) for x in value]


def frame(seconds, fps):
    return math.floor(number(seconds, "seconds", minimum=0) *
                      number(fps, "fps", positive=True) + 0.5)
