"""Two-point similarity geometry and restoration of rotated detector results."""


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
