"""V2 pixel identity: strict PNG decoding, fixed geometry and deterministic encoding.

V1 keeps its original implementation and nine-module identity in background_assets.
Only this module and image_normalization belong to the v2 render source closure.
"""
import io as bytes_io
import struct
import zlib
from pathlib import Path
import hashlib
from PIL import Image, ImageFile, PngImagePlugin
from .background_contract import BackgroundError, MAX_PNG
from .contract import InvalidInput
from .image_normalization import normalize_bytes

MAX_AXIS = 8192
MAX_PIXELS = 8_000_000
SOURCE_SHA256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()

def _png(raw, budget):
    """Validate framing, all CRCs and original bit depth before Pillow decode."""
    if len(raw) > MAX_PNG:
        raise BackgroundError("resource_limit", "PNG exceeds 32 MiB")
    if not raw.startswith(b"\x89PNG\r\n\x1a\n"):
        raise BackgroundError("invalid_image", "Selected original must be PNG")
    position, count, saw_idat, saw_end, idat_ended = 8, 0, False, False, False
    while position < len(raw):
        budget.check()
        if len(raw) - position < 12:
            raise BackgroundError("invalid_image", "Truncated PNG chunk")
        size = struct.unpack_from(">I", raw, position)[0]
        kind = raw[position + 4:position + 8]
        end = position + 12 + size
        if end > len(raw):
            raise BackgroundError("invalid_image", "Truncated PNG chunk payload")
        data = raw[position + 8:position + 8 + size]
        crc = struct.unpack_from(">I", raw, position + 8 + size)[0]
        if zlib.crc32(kind + data) & 0xffffffff != crc:
            raise BackgroundError("invalid_image", "PNG chunk checksum mismatch")
        if kind in (b"acTL", b"fcTL", b"fdAT"):
            raise BackgroundError("invalid_image", "Animated PNG is unsupported")
        if len(kind) != 4 or not all(65 <= c <= 90 or 97 <= c <= 122 for c in kind):
            raise BackgroundError("invalid_image", "Invalid PNG chunk type")
        if not count and kind != b"IHDR":
            raise BackgroundError("invalid_image", "PNG must begin with IHDR")
        if kind == b"IHDR":
            if count or size != 13:
                raise BackgroundError("invalid_image", "Invalid/duplicate PNG header")
            width, height, depth, color, compression, filtering, interlace = struct.unpack(">IIBBBBB", data)
            if width == 0 or height == 0:
                raise BackgroundError("invalid_image", "PNG dimensions must be positive")
            if max(width, height) > MAX_AXIS or width * height > MAX_PIXELS:
                raise BackgroundError("resource_limit", "PNG exceeds 8192 pixels/axis or 8000000 decoded pixels")
            valid_depths = {0: (1, 2, 4, 8), 2: (8,), 3: (1, 2, 4, 8), 4: (8,), 6: (8,)}
            if depth not in valid_depths.get(color, ()) or compression or filtering or interlace not in (0, 1):
                raise BackgroundError("invalid_image", "Unsupported PNG bit depth or encoding")
        elif kind == b"IDAT":
            if idat_ended:
                raise BackgroundError("invalid_image", "PNG IDAT chunks are not consecutive")
            saw_idat = True
        elif saw_idat:
            idat_ended = True
        if kind[0] & 32 == 0 and kind not in (b"IHDR", b"PLTE", b"IDAT", b"IEND"):
            raise BackgroundError("invalid_image", "Unknown critical PNG chunk")
        count += 1
        if kind == b"IEND":
            if size or end != len(raw) or not saw_idat:
                raise BackgroundError("invalid_image", "Invalid PNG end or trailing bytes")
            saw_end = True
            break
        position = end
    if not saw_end:
        raise BackgroundError("invalid_image", "Missing PNG end chunk")


def _diagnostic(image):
    histogram = image.getchannel("A").histogram()
    present = [value for value, count in enumerate(histogram) if count]
    if histogram[0] == 0:
        raise BackgroundError("opaque_image", "Image requires at least one fully transparent pixel")
    if histogram[0] == image.width * image.height:
        raise BackgroundError("empty_image", "Image requires at least one visible pixel")
    return {"format": "PNG", "mode": "RGBA", "width": image.width, "height": image.height,
            "alpha": {"min": present[0], "max": present[-1], "transparent_pixels": histogram[0],
                      "partial_pixels": sum(histogram[1:255]), "opaque_pixels": histogram[255]}}


def _render(raw, budget, profile=None):
    _png(raw, budget)
    if ImageFile.LOAD_TRUNCATED_IMAGES:
        raise BackgroundError("internal_error", "Strict Pillow decoding was disabled by the host process")
    try:
        with Image.open(bytes_io.BytesIO(raw), formats=("PNG",)) as probe:
            if "icc_profile" in probe.info and not probe.info["icc_profile"]:
                raise BackgroundError("invalid_image", "Empty PNG ICC profile")
            probe.verify()
        normal, _, _ = normalize_bytes(raw, max_bytes=MAX_PNG, max_axis=MAX_AXIS, max_pixels=MAX_PIXELS)
    except (InvalidInput, OSError, ValueError, SyntaxError) as exc:
        raise BackgroundError("invalid_image", str(exc) or "Invalid source PNG") from exc
    budget.check()
    source_diagnostic = _diagnostic(normal)
    width, height = normal.size
    target_width, target_height = (2304, 576) if profile is None else (profile["width"], profile["height"])
    if target_height == 768 and width != 3 * height:
        raise BackgroundError("invalid_image", "New background source must be exactly 3:1")
    if width * target_height >= height * target_width:
        fit = (target_width, max(1, height * target_width // width))
    else:
        fit = (max(1, width * target_height // height), target_height)
    scaled = (normal if normal.size == fit else
              normal.convert("RGBa").resize(fit, Image.Resampling.LANCZOS).convert("RGBA"))
    rgba = bytearray(scaled.tobytes())
    for index in range(0, len(rgba), 4):
        if rgba[index + 3] == 0:
            rgba[index:index + 3] = b"\0\0\0"
    scaled = Image.frombytes("RGBA", fit, bytes(rgba))
    canvas = Image.new("RGBA", (target_width, target_height), (0, 0, 0, 0))
    canvas.paste(scaled, ((target_width - fit[0]) // 2, target_height - fit[1]))
    _diagnostic(canvas)
    budget.check()
    info = PngImagePlugin.PngInfo()
    info.add(b"sRGB", b"\0")
    encoded = bytes_io.BytesIO()
    canvas.save(encoded, format="PNG", pnginfo=info, compress_level=9, optimize=False)
    result = encoded.getvalue()
    _png(result, budget)
    with Image.open(bytes_io.BytesIO(result), formats=("PNG",)) as actual:
        actual.load()
        if actual.mode != "RGBA" or actual.size != (target_width, target_height) or actual.info != {"srgb": 0}:
            raise BackgroundError("internal_error", "PNG encoder did not preserve the fixed profile")
        output_diagnostic = _diagnostic(actual)
    budget.check()
    return result, {"source": source_diagnostic, "output": output_diagnostic,
                    "upscaled": fit[0] > width or fit[1] > height}


