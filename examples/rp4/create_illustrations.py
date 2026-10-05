"""Create three original flat geometric illustrations at source resolution.

This is source artwork authoring, not a second raster/puzzle pipeline.
Pillow 12.3.0; no solver, hints, puzzle grid or outcome-dependent adjustment.
"""
from pathlib import Path

from PIL import Image, ImageDraw


def create(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    ink, red, green, ochre = '#253342', '#b55848', '#637b58', '#c89d56'
    # Teapot: real source curves; essential protected negative space in handle.
    im = Image.new('RGB', (800, 800), 'white')
    d = ImageDraw.Draw(im)
    d.ellipse((505, 255, 735, 565), fill=ink)
    d.ellipse((550, 305, 685, 510), fill='white')
    d.polygon([(230, 355), (100, 275), (90, 340), (185, 485), (280, 515)], fill=ink)
    d.ellipse((190, 265, 605, 645), fill=ink)
    d.rectangle((220, 590, 570, 645), fill=ink)
    d.ellipse((245, 230, 555, 300), fill=ink)
    d.ellipse((367, 175, 433, 243), fill=ink)
    im.save(output / 'illustration-teapot.png')
    # Sailboat: two distinct sails, open gap, hull and waves, no small-grid input.
    im = Image.new('RGB', (900, 600), 'white')
    d = ImageDraw.Draw(im)
    d.polygon([(205, 405), (755, 405), (650, 485), (290, 485)], fill=ink)
    d.rectangle((452, 105, 472, 405), fill=ink)
    d.polygon([(440, 130), (440, 378), (225, 378)], fill=red)
    d.polygon([(487, 163), (487, 378), (715, 378)], fill=ochre)
    d.arc((145, 470, 385, 540), 0, 160, fill=green, width=15)
    d.arc((390, 470, 630, 540), 20, 180, fill=green, width=15)
    d.arc((635, 470, 815, 540), 0, 160, fill=green, width=15)
    im.save(output / 'illustration-sailboat.png')
    # Tulip: asymmetric leaves and broad three-point flower crown.
    im = Image.new('RGB', (800, 800), 'white')
    d = ImageDraw.Draw(im)
    d.rectangle((382, 325, 417, 700), fill=green)
    d.polygon([(392, 610), (265, 595), (190, 440), (325, 485)], fill=green)
    d.polygon([(410, 665), (540, 600), (610, 415), (472, 515)], fill=green)
    d.ellipse((245, 170, 555, 400), fill=red)
    d.polygon([(245, 270), (230, 115), (340, 175), (400, 90),
               (463, 175), (570, 115), (555, 270)], fill=red)
    im.save(output / 'illustration-tulip.png')


if __name__ == '__main__':
    create(Path(__file__).resolve().parent / 'sources')
