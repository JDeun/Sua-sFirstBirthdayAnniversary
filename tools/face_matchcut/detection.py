"""Optional local YuNet candidates, without model download or face selection."""
from .geometry import overlap, restore, rotation


def detect(image, model_path, threshold=.65, max_side=640):
    import cv2
    import numpy as np
    source = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
    ratio = min(1, max_side / max(source.shape[:2]))
    small = cv2.resize(source, None, fx=ratio, fy=ratio)
    model = cv2.FaceDetectorYN.create(str(model_path), "", (max_side, max_side), threshold, .3, 5000)
    candidates, distinct = (), ()
    for turns in range(4):
        rotated, forward = rotation(small, turns)
        model.setInputSize((rotated.shape[1], rotated.shape[0]))
        _, faces = model.detect(rotated)
        if faces is not None:
            candidates = (*candidates, *(restore(face, np.linalg.inv(forward), ratio, turns) for face in faces))
    for face in sorted(candidates, key=lambda item: item["confidence"], reverse=True):
        if not any(overlap(face["bbox"], other["bbox"]) > .35 for other in distinct):
            distinct = (*distinct, face)
    return sorted(distinct, key=lambda face: face["bbox"][0])
