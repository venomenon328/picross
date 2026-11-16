"""Shared current reveal validation for integration and creative preparation."""
import math
import re
import xml.etree.ElementTree as ET
from .images import MAX_BYTES,normalize,file_hash
from .authoring_package import require
from .contract import InvalidInput

def validate_reveal(path, width, height):
    """Current bounded PNG/SVG reveal validation."""
    require(path.stat().st_size <= MAX_BYTES, "Reveal exceeds image byte limit")
    if path.suffix == ".png":
        image, meta, _ = normalize(path)
        require(meta["format"] == "PNG" and meta["orientation"] == 1,
                "Reveal requires an oriented PNG; no implicit conversion")
        w, h = image.size
    else:
        require(path.suffix == ".svg", "Reveal requires PNG or bounded local SVG")
        raw = path.read_bytes()
        require(b"<!" not in raw, "SVG declarations/entities unsupported")
        try:
            root = ET.fromstring(raw)
        except ET.ParseError as exc:
            raise InvalidInput("Damaged SVG") from exc
        allowed = {"svg", "g", "path", "rect", "circle", "ellipse", "line", "polyline", "polygon",
                   "defs", "linearGradient", "stop", "title", "desc"}
        require(len(list(root.iter())) <= 10000, "SVG element limit")
        for node in root.iter():
            require(node.tag.rsplit("}", 1)[-1] in allowed, "Unsupported SVG element")
            for key, value in node.attrib.items():
                require(not key.rsplit("}", 1)[-1].lower().startswith("on") and "href" not in key.lower() and
                        not any(v in value.lower() for v in ("@import", "javascript:", "http:", "https:", "file:", "data:")) and
                        (not re.search(r"url\s*\(", value, re.I) or re.fullmatch(r"url\(#[a-zA-Z0-9_-]+\)", value)),
                        "External/executable SVG content unsupported")
        try:
            w, h = float(root.attrib["width"]), float(root.attrib["height"])
        except (KeyError, ValueError) as exc:
            raise InvalidInput("SVG requires explicit numeric dimensions") from exc
        require(root.tag.rsplit("}", 1)[-1] == "svg", "Not an SVG root")
    require(math.isfinite(w) and math.isfinite(h) and 2 * width <= w <= 8192 and
            2 * height <= h <= 8192 and w * h <= 8_000_000,
            "Reveal requires >=2 pixels per cell/axis within image limits")
    return {"width": w, "height": h, "sha256": file_hash(path)}
