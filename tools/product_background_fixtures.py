"""Two fixed neutral PNG2304 patterns for isolated HP-I2 evidence only.

These functions create pixels, not catalog entries, approvals or integration
authority. A through-path probe must use the ordinary synthetic integration.
"""
import hashlib
from pathlib import Path
import struct
import zlib


IDS = {"a": "pz-hp-i2-a", "b": "pz-hp-i2-b", "none": "pz-hp-i2-none"}
SIZE = (2304, 576)


def _chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff)


def pixels(variant="a") -> bytes:
    """Return the exact RGBA basis, with transparent black outside sparse lines."""
    if variant not in ("a", "b"):
        raise ValueError("Unknown fixed background pattern")
    width, height = SIZE
    data = bytearray(width * height * 4)

    def dot(x, y, radius=3, alpha=205):
        color = bytes((72, 65, 55, alpha))
        for yy in range(max(0, y-radius), min(height, y+radius+1)):
            begin = (yy * width + max(0, x-radius)) * 4
            end = (yy * width + min(width, x+radius+1)) * 4
            data[begin:end] = color * ((end-begin)//4)

    def line(x1, y1, x2, y2, radius=3, alpha=205):
        steps = max(abs(x2-x1), abs(y2-y1))
        for step in range(steps+1):
            dot(x1+(x2-x1)*step//max(steps,1), y1+(y2-y1)*step//max(steps,1), radius, alpha)

    # Both patterns cover the same canvas and use the same ink. Their distinct
    # silhouettes make stale A/B/return images visible without a motif gallery.
    line(96, 520, 2208, 520, 2, 175)
    if variant == "a":
        for center, radius in ((420, 250), (1140, 360), (1860, 240)):
            for x in range(center-radius, center+radius+1):
                y = 450 - (radius*radius-(x-center)**2) // max(radius,1)
                dot(x, y, 3)
        line(340, 520, 340, 355, 3)
        line(1510, 520, 1510, 360, 3)
    else:
        for left, top, right in ((200, 215, 680), (900, 120, 1380), (1600, 235, 2080)):
            for segment in ((left,500,left,top),(left,top,right,top),(right,top,right,500)):
                line(*segment)
            line(left, top, right, 500, 2, 175)
    # A one-pixel line and partial alpha are fixed mipmap/alpha counterexamples.
    line(112, 550, 2192, 550, 0, 96)
    return bytes(data)


def png(variant="a") -> tuple[bytes, bytes]:
    rgba = pixels(variant)
    width, height = SIZE
    stride = width * 4
    scanlines = b"".join(b"\0" + rgba[y*stride:(y+1)*stride] for y in range(height))
    raw = (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", struct.pack(">IIBBBBB", width,height,8,6,0,0,0))
           + _chunk(b"sRGB", b"\0") + _chunk(b"IDAT", zlib.compress(scanlines,9)) + _chunk(b"IEND", b""))
    return raw, rgba


def write_image(path: Path, variant="a") -> dict:
    raw, rgba = png(variant)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return dict(variant=variant, size=list(SIZE), source_bytes=len(raw),
                source_sha256=hashlib.sha256(raw).hexdigest(), rgba_bytes=len(rgba),
                rgba_sha256=hashlib.sha256(rgba).hexdigest())
