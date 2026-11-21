"""Technical catalog PNGs derived from the complete chosen reveal canvas."""
from copy import deepcopy
from fractions import Fraction
from io import BytesIO
from math import ceil, isfinite
from pathlib import Path
import xml.etree.ElementTree as ET

from .authoring_package import require
from .contract import exact_keys, integer

GENERATOR = "picross-catalog-reveal-1"
PROFILES = (("ui100", 264, 112), ("ui125", 329, 140))
LIMIT = 256 * 1024


def path(identifier, label):
    return f"game/art/catalog/{identifier}-{label}.png"


def dimensions(width, height, bounds, vector):
    w, h = Fraction(str(width)), Fraction(str(height))
    scale = min(bounds[0] / w, bounds[1] / h)
    if not vector:
        scale = min(1, scale)
    return max(1, ceil(w * scale)), max(1, ceil(h * scale))


def validate(catalog, identifier, original):
    from .current_content import reference
    exact_keys(catalog, {"generator", "source_width", "source_height", "source_sha256", "profiles"})
    require(catalog["generator"] == GENERATOR and catalog["source_sha256"] == original["sha256"],
            "Catalog generator or original binding differs")
    vector = original["file"].endswith(".svg")
    w, h = catalog["source_width"], catalog["source_height"]
    for axis in (w, h):
        require(type(axis) in (float, int) and 0 < axis <= 8192 and isfinite(axis)
                and (vector or type(axis) is int), "Invalid catalog source dimensions")
    require(w*h <= 8_000_000, "Oversized catalog source")
    require(isinstance(catalog["profiles"], list) and len(catalog["profiles"]) == len(PROFILES),
            "Two ordered catalog profiles required")
    for row, (label, pw, ph) in zip(catalog["profiles"], PROFILES):
        exact_keys(row, {"profile", "width", "height", "asset"})
        integer(row["width"], 1, pw, "profile width")
        integer(row["height"], 1, ph, "profile height")
        require(row["profile"] == f"catalog-{label}-v1" and
                (row["width"], row["height"]) == dimensions(w, h, (pw, ph), vector),
                "Catalog profile geometry differs")
        reference(row["asset"], name=path(identifier, label), limit=LIMIT)
    return catalog


def project(catalog):
    result = deepcopy(catalog)
    del result["generator"]
    for row in result["profiles"]:
        row["asset"]["file"] = row["asset"]["file"].removeprefix("game/")
    return result


def decode_png(raw):
    from PIL import Image
    with Image.open(BytesIO(raw), formats=("PNG",)) as image:
        rgba = image.convert("RGBA")
        gamma = image.info.get("gamma")
        # libpng simplified read uses straight alpha and a 2.2 display gamma.
        # It gives sRGB precedence and skips corrections within its 5% threshold.
        if "srgb" not in image.info and gamma and abs(2.2 * gamma - 1) > 0.05:
            exponent = 1 / (2.2 * gamma)
            lut = [int(255 * (i / 255) ** exponent + 0.5) for i in range(256)]
            rgba = rgba.point(lut * 3 + list(range(256)))
        rgba.info.clear()
        return rgba


def render_svg(raw, width, height, target):
    import resvg_py
    from PIL import Image
    require(resvg_py.__version__ == "0.5.0", "Catalog SVG requires resvg_py 0.5.0")
    # The nested source retains its own viewBox and preserveAspectRatio.
    # An explicit output viewport avoids resvg rounding a fractional source first.
    element = ET.fromstring(raw)
    wrapper = ET.Element("svg", {"xmlns": "http://www.w3.org/2000/svg",
        "width": str(target[0]), "height": str(target[1]),
        "viewBox": f"0 0 {width} {height}", "preserveAspectRatio": "none"})
    wrapper.append(element)
    png = resvg_py.svg_to_bytes(svg_string=ET.tostring(wrapper, encoding="unicode"),
                                skip_system_fonts=True, dpi=96)
    with Image.open(BytesIO(png)) as image:
        return image.convert("RGBA")


def svg_self_test():
    raw = b'<svg xmlns="http://www.w3.org/2000/svg" width="6.5" height="4"><rect width="3" height="4" fill="#2468ab"/></svg>'
    image = render_svg(raw, 6.5, 4, (26, 16))
    require(image.size == (26, 16) and image.getpixel((4, 8)) == (36, 104, 171, 255)
            and image.getpixel((24, 8))[3] == 0, "Private catalog SVG renderer failed")


def generate(identifier, original, raw):
    from PIL import Image, __version__
    from .current_content import ref
    from .editor_image_input import validate_reveal
    require(__version__ == "12.3.0", "Catalog PNG requires Pillow 12.3.0")
    require(ref(original["file"], raw) == original, "Catalog original bytes differ")
    suffix = Path(original["file"]).suffix
    checked = validate_reveal(raw, suffix)
    w, h = checked["width"], checked["height"]
    pixels = decode_png(raw) if suffix == ".png" else None
    rows, files = [], {}
    for label, pw, ph in PROFILES:
        target = dimensions(w, h, (pw, ph), pixels is None)
        if pixels is None:
            image = render_svg(raw, w, h, target)
        elif pixels.size == target:
            image = pixels
        else:
            image = pixels.convert("RGBa").resize(target, Image.Resampling.LANCZOS).convert("RGBA")
        require(image.size == target, "Catalog renderer returned wrong dimensions")
        name = path(identifier, label)
        stream = BytesIO()
        image.info.clear()
        image.save(stream, format="PNG", optimize=False, compress_level=9)
        files[name] = stream.getvalue()
        rows.append({"profile": f"catalog-{label}-v1", "width": target[0], "height": target[1],
                     "asset": ref(name, files[name])})
    catalog = {"generator": GENERATOR, "source_sha256": original["sha256"],
               "source_width": w, "source_height": h, "profiles": rows}
    return validate(catalog, identifier, original), files
