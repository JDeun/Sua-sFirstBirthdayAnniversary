"""Reusable RGB eye alignment and optional local YuNet candidate detection.

Requires NumPy, Pillow and OpenCV at call time. Coordinates refer to pixels in
the supplied upright RGB image. Detection returns candidates, never identities
or an automatically selected face. ``align_image`` uses only the given eyes.
This package has no project, renderer, model-registry or filmtools dependency.
"""
from .alignment import align_image
from .detection import detect
from .geometry import overlap, restore, rotation, similarity

__all__ = ["align_image", "detect", "overlap", "restore", "rotation", "similarity"]
