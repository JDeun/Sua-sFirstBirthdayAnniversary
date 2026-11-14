"""EXIF-aware sRGB loading and bounded global tone utilities."""
import io

from .checks import number, vector


def upright_rgb(path):
    from PIL import Image, ImageCms, ImageOps
    with Image.open(path) as original:
        result = ImageOps.exif_transpose(original).convert("RGB")
        icc = original.info.get("icc_profile")
        if icc:
            result = ImageCms.profileToProfile(result, ImageCms.ImageCmsProfile(io.BytesIO(icc)),
                                               ImageCms.createProfile("sRGB"), outputMode="RGB")
        return result


def apply_tone(image, exposure_ev=0, rgb_gains=(1, 1, 1), saturation=1):
    """Global linear-light exposure/white balance; no local skin or face processing."""
    import numpy as np
    from PIL import Image
    number(exposure_ev, "exposure_ev")
    gains = vector(rgb_gains, 3, "rgb_gains", positive=True)
    number(saturation, "saturation", minimum=0)
    if abs(exposure_ev) > 2 or max(gains) > 2 or min(gains) < .5 or saturation > 2:
        raise ValueError("Tone controls exceed the bounded global adjustment range")
    encoded = np.asarray(image.convert("RGB"), dtype=np.float64) / 255
    linear = np.where(encoded <= .04045, encoded / 12.92, ((encoded + .055) / 1.055) ** 2.4)
    adjusted = linear * (2 ** exposure_ev) * np.asarray(gains)
    luma = adjusted @ np.array([.2126, .7152, .0722])
    adjusted = luma[..., None] + (adjusted - luma[..., None]) * saturation
    clipped = np.clip(adjusted, 0, 1)
    encoded = np.where(clipped <= .0031308, clipped * 12.92, 1.055 * clipped ** (1 / 2.4) - .055)
    result = Image.fromarray(np.rint(encoded * 255).astype("uint8"))
    return result, {"status": "visual_review_required", "clipped_channel_fraction":
                    float(np.mean((adjusted < 0) | (adjusted > 1)))}
