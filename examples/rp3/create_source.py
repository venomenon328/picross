"""Create the original RP-3 example illustration from our own geometry.

This only writes a PNG. The production pipeline must subsequently decode it;
no solution matrix or hints are supplied to the importer or solver.
"""
from pathlib import Path
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parent
image = Image.new("RGBA", (640, 640), (255, 255, 255, 0))
draw = ImageDraw.Draw(image)
ink = "#293e3d"
draw.rounded_rectangle((255, 272, 385, 557), radius=34, fill=ink)
draw.ellipse((65, 80, 575, 510), fill=ink)
# The cap is the upper half of the ellipse, with a level underside. The stem
# remains a separately drawn physical shape, rather than an injected grid.
draw.rectangle((0, 300, 254, 639), fill=(255, 255, 255, 0))
draw.rectangle((386, 300, 639, 639), fill=(255, 255, 255, 0))
draw.rectangle((255, 558, 385, 639), fill=(255, 255, 255, 0))
image.save(root / "source.png")
