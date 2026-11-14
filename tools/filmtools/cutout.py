"""Non-generative GrabCut driven exclusively by external polygon annotations."""
from .checks import vector


def polygon_mask(size, points, annotation_size):
    import numpy as np
    from PIL import Image, ImageDraw
    width, height = vector(annotation_size, 2, "annotation size", positive=True)
    if not isinstance(points, list) or len(points) < 3:
        raise ValueError("Polygon requires at least three points")
    vertices = [vector(point, 2, "polygon point") for point in points]
    if any(not 0 <= x <= width or not 0 <= y <= height for x, y in vertices):
        raise ValueError("Polygon lies outside annotation coordinates")
    canvas = Image.new("L", size)
    scaled = [(round(x * size[0] / width), round(y * size[1] / height)) for x, y in vertices]
    ImageDraw.Draw(canvas).polygon(scaled, fill=255)
    return np.asarray(canvas) > 0


def initialize(size, spec):
    import cv2
    import numpy as np
    coordinates = spec["annotation_size"]
    envelope = polygon_mask(size, spec["envelope"], coordinates)
    foreground, background = np.zeros(envelope.shape, bool), ~envelope
    for points in spec["foreground"]:
        foreground |= polygon_mask(size, points, coordinates)
    for points in spec.get("background", []):
        background |= polygon_mask(size, points, coordinates)
    if not foreground.any() or not background.any() or np.any(foreground & background):
        raise ValueError("Need disjoint nonempty foreground and background seeds")
    mask = np.where(envelope, cv2.GC_PR_BGD, cv2.GC_BGD).astype("uint8")
    radius = max(1, round(min(size) * .01))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * radius + 1, 2 * radius + 1))
    mask[cv2.erode(envelope.astype("uint8"), kernel) > 0] = cv2.GC_PR_FGD
    mask[foreground], mask[background] = cv2.GC_FGD, cv2.GC_BGD
    return mask


def edge_alpha(binary):
    import cv2
    import numpy as np
    inside = cv2.distanceTransform(binary, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
    outside = cv2.distanceTransform(1 - binary, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
    return np.clip((inside - outside + 1.5) / 3 * 255, 0, 255).astype("uint8")


def segment(image, spec, iterations=5, seed=0):
    import cv2
    import numpy as np
    from PIL import Image
    if type(iterations) is not int or not 1 <= iterations <= 20:
        raise ValueError("GrabCut iterations must be between 1 and 20")
    pixels = np.asarray(image.convert("RGB"))
    mask = initialize(image.size, spec)
    initial = mask.copy()
    cv2.setRNGSeed(seed)
    cv2.grabCut(cv2.cvtColor(pixels, cv2.COLOR_RGB2BGR), mask, None,
                np.zeros((1, 65)), np.zeros((1, 65)), iterations, cv2.GC_INIT_WITH_MASK)
    binary = np.isin(mask, [cv2.GC_FGD, cv2.GC_PR_FGD]).astype("uint8")
    count, labels, stats, _ = cv2.connectedComponentsWithStats(binary, 8)
    keep = [i for i in range(1, count) if stats[i, cv2.CC_STAT_AREA] >= 24
            or np.any(initial[labels == i] == cv2.GC_FGD)]
    alpha = edge_alpha(np.isin(labels, keep).astype("uint8"))
    alpha[initial == cv2.GC_BGD], alpha[initial == cv2.GC_FGD] = 0, 255
    result = Image.fromarray(np.dstack((pixels, alpha)))
    box = result.getchannel("A").getbbox()
    if box is None:
        raise ValueError("Segmentation produced an empty subject")
    bounds = [box[0] / image.width, box[1] / image.height,
              (box[2] - box[0]) / image.width, (box[3] - box[1]) / image.height]
    return result, {"status": "visual_review_required", "alphaBounds": bounds,
                    "dimensions": list(image.size), "rgb_pixels_preserved": True}
