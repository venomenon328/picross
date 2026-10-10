"""Reproduce SL-65 technical derivatives of the image-tool original (Pillow 12.3)."""
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "prototypes/p1/art/book"
ORIGINAL = ROOT / "docs/design/sidebar_frames/original.png"


def build():
    digest = hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()
    assert digest == "9e7f10b394caf8cd6b89eb7c990fe443d113286a7ac873ca730b1938ea1c4e33"
    image = Image.open(ORIGINAL).convert("RGBA")
    alpha = image.getchannel("A").point(lambda value: 0 if value <= 1 else value)
    alpha.paste(0, (210, 205, 1050, 1040))
    image.putalpha(alpha)
    bounds = alpha.getbbox()
    image = image.crop(bounds)
    records = []
    for name, size in [("preview", (384, 384)), ("palette", (288, 288)), ("tools", (320, 480))]:
        derived = image.resize(size, Image.Resampling.LANCZOS)
        path = DEST / ("frame-" + name + ".png")
        derived.save(path)
        sx, sy = size[0] / image.width, size[1] / image.height
        x, y = (210-bounds[0])*sx+3, (205-bounds[1])*sy+3
        w, h = 840*sx-6, 835*sy-6
        x, y = max(x, size[0]-x-w), max(y, size[1]-y-h)
        safe = [x, y, size[0]-2*x, size[1]-2*y]
        assert derived.getchannel("A").crop((int(x)+1, int(y)+1, int(size[0]-x)-1, int(size[1]-y)-1)).getextrema() == (0, 0)
        canonical = bytearray(derived.tobytes())
        for i in range(0, len(canonical), 4):
            if canonical[i+3] == 0:
                canonical[i:i+3] = b"\0\0\0"
        records.append(dict(file=path.name, size=list(size), safe=safe,
                            alpha_bounds=list(derived.getchannel("A").getbbox()),
                            sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                            rgba_sha256=hashlib.sha256(canonical).hexdigest()))
    metadata = dict(source="SL-65 native image tool, 2026-10-10", original_sha256=digest,
                    crop=list(bounds), derivatives=records)
    (DEST / "frames.json").write_text(json.dumps(metadata, indent=2)+"\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    build()
