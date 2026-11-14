"""Check fitted apertures and actual source endpoints, including playback rate."""
import json
from fractions import Fraction
import subprocess

from .checks import number, vector


def probe(path, executable="ffprobe", *, count_frames=False):
    command = [executable, "-v", "error", "-show_format", "-show_streams"]
    if count_frames:
        command += ["-count_frames"]
    result = subprocess.run(command + ["-of", "json", str(path)], check=True,
                            capture_output=True, text=True)
    return json.loads(result.stdout)


def video_info(data):
    stream = next(s for s in data["streams"] if s.get("codec_type") == "video")
    fps = float(Fraction(stream.get("avg_frame_rate", "0/1")))
    frames = stream.get("nb_read_frames") or stream.get("nb_frames")
    duration = float(stream.get("duration") or data.get("format", {}).get("duration", 0))
    return {"fps": number(fps, "source fps", positive=True),
            "duration_seconds": number(duration, "source duration", positive=True),
            "source_frames": int(frames) if frames and frames != "N/A" else None,
            "dimensions": [stream["width"], stream["height"]]}


def check_endpoint(duration, output_fps, source, playback_rate=1, source_offset=0):
    number(duration, "shot frames", positive=True)
    number(output_fps, "output fps", positive=True)
    number(playback_rate, "playback rate", positive=True)
    number(source_offset, "source offset", minimum=0)
    # Last displayed output frame must map to an existing source frame.
    last_time = source_offset + (duration - 1) / output_fps * playback_rate
    final_index = int(last_time * source["fps"] + 1e-8)
    count = source.get("source_frames")
    if last_time >= source["duration_seconds"] - 1e-8 or (count is not None and final_index >= count):
        raise ValueError("Video source ends before its last displayed output frame")
    return {"last_source_seconds": last_time, "last_source_frame": final_index,
            "verified_frame_count": count is not None}


def check_fit(asset, layout, *, tolerance=0.002):
    width, height = vector(asset["dimensions"], 2, "dimensions", positive=True)
    crop = vector(asset.get("crop", [0, 0, 1, 1]), 4, "crop")
    x, y, cw, ch = crop
    if min(x, y) < 0 or min(cw, ch) <= 0 or x + cw > 1 or y + ch > 1:
        raise ValueError("Crop must be a positive normalized rectangle within the source")
    rect = layout["media"]
    for key in ("x", "y", "width", "height"):
        number(rect[key], f"media.{key}")
    mat = number(layout.get("mat", 0), "mat", minimum=0)
    foot = number(layout.get("foot", 0), "foot", minimum=0)
    aperture = (rect["width"] - 2 * mat, rect["height"] - 2 * mat - foot)
    if min(aperture) <= 0:
        raise ValueError("Mat and foot leave an empty aperture")
    source_aspect = width * cw / (height * ch)
    error = abs(aperture[0] / aperture[1] / source_aspect - 1)
    if error > tolerance:
        raise ValueError("Fitted aperture aspect differs from the source/crop")
    return {"relative_aspect_error": error, "aperture": list(aperture)}


def inspect_endpoint_pixels(image, rect, canvas_size, *, threshold=6):
    """A low-variation endpoint is a review flag, never proof of a missing source."""
    import numpy as np
    sx, sy = image.width / canvas_size[0], image.height / canvas_size[1]
    x, y, width, height = (rect[k] for k in ("x", "y", "width", "height"))
    box = (round((x + width * .18) * sx), round((y + height * .18) * sy),
           round((x + width * .82) * sx), round((y + height * .82) * sy))
    if box[0] < 0 or box[1] < 0 or box[2] > image.width or box[3] > image.height:
        raise ValueError("Endpoint aperture lies outside the review frame")
    pixels = np.asarray(image.convert("L").crop(box), dtype=float)
    if not pixels.size:
        raise ValueError("Endpoint aperture is empty")
    variation = float(pixels.std())
    return {"luma_stddev": variation, "review_required": variation <= threshold}
