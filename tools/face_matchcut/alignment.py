"""Align original RGB pixels with a feathered edge over a blurred background."""
import math

from .geometry import similarity


def _output_size(size):
    if not isinstance(size, (list, tuple)) or len(size) != 2:
        raise ValueError("output size must have 2 entries")
    for value in size:
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError("output size must be a finite number")
        if value <= 0:
            raise ValueError("output size is out of range")


def align_image(image, eyes, target_eyes, size, feather=40, blur=40):
    import cv2
    import numpy as np
    from PIL import Image, ImageFilter, ImageOps
    _output_size(size)
    matrix = similarity(eyes, target_eyes)
    pixels = np.asarray(image)
    sharp = cv2.warpAffine(pixels, matrix, tuple(size), flags=cv2.INTER_CUBIC)
    valid = cv2.warpAffine(np.full(pixels.shape[:2], 255, dtype="uint8"), matrix, tuple(size))
    distance = cv2.distanceTransform((valid > 250).astype("uint8"), cv2.DIST_L2, 3)
    if feather <= 0 or blur < 0:
        raise ValueError("Feather must be positive and blur nonnegative")
    alpha = np.clip(distance / feather, 0, 1)[..., None]
    background = np.asarray(ImageOps.fit(image, tuple(size)).filter(ImageFilter.GaussianBlur(blur)))
    blended = sharp * alpha + background * (1 - alpha)
    projected = np.column_stack((eyes, np.ones(2))) @ matrix.T
    return Image.fromarray(np.clip(blended, 0, 255).astype("uint8")), {
        "matrix": matrix.tolist(), "eye_error_px": float(np.max(np.abs(projected - target_eyes))),
        "review": "Numerical eye residual does not verify annotation or visual quality"}
