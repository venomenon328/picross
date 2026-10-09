"""Independent pixel checks for native hand-hatched fills (no renderer imports)."""
from __future__ import annotations

import p1_preflight as toolchain


def distance(a, b):
    return max(abs(x - y) for x, y in zip(a, b))


def check_hatching(images, blank, size):
    from PIL import ImageChops
    final = images[210]
    if ImageChops.difference(images[0], blank).getbbox():
        raise toolchain.PreflightError("Hatching starts with an underdrawn area")
    core = [(x, y) for y in range(2, size - 2) for x in range(2, size - 2)
            if distance(blank.getpixel((x, y)), final.getpixel((x, y))) > 70]
    if not core:
        raise toolchain.PreflightError("No visible final fill")
    coverage = {}
    for ms, picture in images.items():
        painted = [p for p in core if distance(picture.getpixel(p), final.getpixel(p)) < 40]
        paper = [p for p in core if distance(picture.getpixel(p), blank.getpixel(p)) < 8]
        coverage[ms] = len(painted) / len(core)
        if ms in (75, 105, 150) and (not painted or not paper):
            raise toolchain.PreflightError("Short opaque strokes and untouched paper must coexist")
        # Outer pixel ring is the cell/grid separation, never a painting surface.
        border = [(x, y) for y in range(size) for x in range(size)
                  if x in (0, size - 1) or y in (0, size - 1)]
        if any(picture.getpixel(p) != blank.getpixel(p) for p in border):
            raise toolchain.PreflightError("Hatching crosses cell separation")
    if not .1 < coverage[75] < coverage[150] < 1:
        raise toolchain.PreflightError("Fill does not accumulate spatially")
    # Separate pen tracks leave interior paper seams, unlike a solid area wipe.
    runs = 0
    for x in range(size // 4, 3 * size // 4):
        previous = False
        count = 0
        for y in range(2, size - 2):
            ink = distance(images[105].getpixel((x, y)), blank.getpixel((x, y))) > 70
            if ink and not previous:
                count += 1
            previous = ink
        runs = max(runs, count)
    if size >= 24 and runs < 2:
        raise toolchain.PreflightError("No distinct short hatch strokes visible")
    if size == 12:
        # At the smallest pitch seams can fall between pixel centers; two partial
        # passes must still grow in opposite directions, not sweep one full area.
        def added_center(a, b):
            added = [x for x, y in core if distance(images[a].getpixel((x, y)), images[b].getpixel((x, y))) > 70]
            if not added:
                raise toolchain.PreflightError("Missing small-cell pen movement")
            return sum(added) / len(added)
        if 45 in images and added_center(30, 45) >= added_center(60, 75):
            raise toolchain.PreflightError("Small-cell strokes do not alternate direction")
    return {"coverage": coverage, "separate_tracks_at_105ms": runs}


def negative_controls(images, blank, size):
    from PIL import Image
    final = images[210]
    fade = {ms: Image.blend(blank, final, ms / 210) for ms in images}
    wipe = {}
    instant = {}
    for ms in images:
        wipe[ms] = blank.copy()
        height = round(size * ms / 210)
        if height:
            wipe[ms].paste(final.crop((0, 0, size, height)), (0, 0))
        instant[ms] = blank if ms == 0 else final
    rejected = []
    for label, mutant in (("global fade", fade), ("solid area wipe", wipe), ("instant full area", instant)):
        try:
            check_hatching(mutant, blank, size)
        except toolchain.PreflightError:
            rejected.append(label)
        else:
            raise toolchain.PreflightError("Hatching oracle accepted " + label)
    return rejected
