"""Shared bounded RP-3 color/EXIF decoding, without solver or engine imports.

Callers own file identity, resource accounting and Pillow version binding. The
RP-3 wrapper passes its original limits; HP-W2 additionally checks strict PNG
framing/bit depth. The shared RP-3 color path uses the grayscale input mode for
gray ICC profiles, including bilevel and gray-plus-alpha images.
"""
from __future__ import annotations

import hashlib
import io
import warnings

from PIL import Image, ImageCms, ImageOps

from .contract import InvalidInput


def normalize_bytes(original: bytes, *, max_bytes: int, max_axis: int,
                    max_pixels: int) -> tuple[Image.Image, dict, bytes]:
    if len(original) > max_bytes:
        raise InvalidInput(f"Image exceeds {max_bytes} encoded bytes")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(original), formats=("PNG", "JPEG")) as source:
                fmt, size, mode = source.format, source.size, source.mode
                if max(size) > max_axis or size[0] * size[1] > max_pixels:
                    raise InvalidInput(f"Source exceeds {max_axis} pixels/axis or {max_pixels} decoded pixels")
                if getattr(source, "n_frames", 1) != 1:
                    raise InvalidInput("Animated/multiple-frame PNG is unsupported")
                if mode not in ("1", "L", "LA", "P", "RGB", "RGBA", "CMYK"):
                    raise InvalidInput(f"Unsupported source pixel mode {mode}; no silent high-depth conversion")
                orientation = source.getexif().get(274, 1)
                if orientation not in range(1, 9):
                    raise InvalidInput("Invalid EXIF orientation")
                icc = source.info.get("icc_profile")
                gamma = source.info.get("gamma")
                srgb = source.info.get("srgb")
                if not icc and gamma is not None and srgb is None and abs(gamma - 0.45455) > 0.0001:
                    raise InvalidInput("Non-sRGB PNG gamma requires an ICC profile")
                source.load()  # Strict decoding; LOAD_TRUNCATED_IMAGES stays false.
                oriented = ImageOps.exif_transpose(source)
                alpha = oriented.convert("RGBA").getchannel("A")
                if icc:
                    profile = ImageCms.ImageCmsProfile(io.BytesIO(icc))
                    # Alpha is separate. Gray samples must enter their GRAY
                    # profile as L; palette and RGB samples use RGB components.
                    input_mode = "L" if mode in ("1", "L", "LA") else "CMYK" if mode == "CMYK" else "RGB"
                    color = ImageCms.profileToProfile(oriented.convert(input_mode), profile,
                              ImageCms.createProfile("sRGB"), renderingIntent=0, outputMode="RGB")
                    treatment = "ICC to sRGB, perceptual intent"
                else:
                    if mode == "CMYK":
                        raise InvalidInput("Unprofiled CMYK JPEG is unsupported; supply ICC")
                    color = oriented.convert("RGB")
                    treatment = "untagged/sRGB RGB or gray interpreted as sRGB"
                color.putalpha(alpha)
                # Deliberately drop EXIF/ICC/text after the explicit transform.
                normalized = Image.frombytes("RGBA", color.size, color.tobytes())
                metadata = {"format": fmt, "source_size": list(size), "source_mode": mode,
                            "orientation": orientation, "normalized_size": list(normalized.size),
                            "color_treatment": treatment, "icc_sha256": hashlib.sha256(icc).hexdigest() if icc else None,
                            "alpha": "preserved, composited against design background only during rasterization"}
                return normalized, metadata, original
    except InvalidInput:
        raise
    except (OSError, ValueError, SyntaxError, Image.DecompressionBombError,
            Image.DecompressionBombWarning, ImageCms.PyCMSError) as exc:
        raise InvalidInput(f"Damaged/unsupported PNG or JPEG: {exc}") from exc
