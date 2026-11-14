"""YuNet candidates and explicit two-eye similarity alignment; no identity inference."""
from .checks import vector


def similarity(eyes, targets):
    import numpy as np
    points, goals = np.asarray(eyes, dtype=float), np.asarray(targets, dtype=float)
    if points.shape != (2, 2) or goals.shape != (2, 2) or not np.all(np.isfinite([points, goals])):
        raise ValueError("Expected two finite source and target eye coordinates")
    left, right = points
    first, second = goals
    delta, goal = right - left, second - first
    denominator = float(delta @ delta)
    if denominator < 1e-8 or float(goal @ goal) < 1e-8:
        raise ValueError("Eye pairs must have nonzero separation")
    a = float(delta @ goal) / denominator
    b = (delta[0] * goal[1] - delta[1] * goal[0]) / denominator
    linear = np.array([[a, -b], [b, a]])
    return np.column_stack((linear, first - linear @ left))


def rotation(image, turns):
    import cv2
    import numpy as np
    height, width = image.shape[:2]
    matrices = (np.eye(3), np.array([[0, -1, height - 1], [1, 0, 0], [0, 0, 1]]),
                np.array([[-1, 0, width - 1], [0, -1, height - 1], [0, 0, 1]]),
                np.array([[0, 1, 0], [-1, 0, width - 1], [0, 0, 1]]))
    return (image if turns == 0 else cv2.rotate(image, turns - 1)), matrices[turns]


def overlap(first, second):
    x, y, width, height = first
    a, b, w, h = second
    area = max(0, min(x + width, a + w) - max(x, a)) * max(0, min(y + height, b + h) - max(y, b))
    return area / max(1, width * height + w * h - area)


def restore(face, inverse, ratio, turns):
    import numpy as np
    x, y, width, height = face[:4]
    corners = np.array([[x, y, 1], [x + width, y, 1],
                        [x, y + height, 1], [x + width, y + height, 1]]) @ inverse.T
    left, top = corners[:, :2].min(axis=0) / ratio
    right, bottom = corners[:, :2].max(axis=0) / ratio
    landmarks = np.column_stack((face[4:14].reshape(5, 2), np.ones(5))) @ inverse.T
    points = (landmarks[:, :2] / ratio).tolist()
    return {"bbox": [float(left), float(top), float(right - left), float(bottom - top)],
            "landmarks": points, "eyes": sorted(points[:2], key=lambda p: p[0]),
            "confidence": float(face[14]), "detection_rotation": turns * 90}


def detect(image, model_path, threshold=.65, max_side=640):
    import cv2
    import numpy as np
    source = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
    ratio = min(1, max_side / max(source.shape[:2]))
    small = cv2.resize(source, None, fx=ratio, fy=ratio)
    model = cv2.FaceDetectorYN.create(str(model_path), "", (max_side, max_side), threshold, .3, 5000)
    candidates, distinct = [], []
    for turns in range(4):
        rotated, forward = rotation(small, turns)
        model.setInputSize((rotated.shape[1], rotated.shape[0]))
        _, faces = model.detect(rotated)
        if faces is not None:
            candidates.extend(restore(face, np.linalg.inv(forward), ratio, turns) for face in faces)
    for face in sorted(candidates, key=lambda item: item["confidence"], reverse=True):
        if not any(overlap(face["bbox"], other["bbox"]) > .35 for other in distinct):
            distinct.append(face)
    return sorted(distinct, key=lambda face: face["bbox"][0])


def align_image(image, eyes, target_eyes, size, feather=40, blur=40):
    import cv2
    import numpy as np
    from PIL import Image, ImageFilter, ImageOps
    vector(size, 2, "output size", positive=True)
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
