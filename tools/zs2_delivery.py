"""Independent spatial and real-time oracles for temporary native cell crops."""
from __future__ import annotations
import p1_preflight as toolchain
import zs_hatching


def x_regions(size):
    # Independent image regions; no production path, seed or stroke code imported.
    return [(int(size*a), int(size*.15), int(size*b), int(size*.48)) for a,b in ((.15,.48),(.52,.85))]


def verify_wave(renders, record):
    from PIL import Image, ImageChops
    if record['start']!=[17,2] or record['end']!=[1,2] or record['effective_cells']!=17:
        raise toolchain.PreflightError('ZS2 reversed wave evidence changed')
    def read(name):
        with Image.open(renders/name) as p:
            if p.size!=(408,24):raise toolchain.PreflightError('ZS2 wave crop changed')
            return p.convert('RGB')
    blank,preview=read(record['blank']),read(record['preview'])
    images={f['elapsed_ms']:read(f['file']) for f in record['frames']}
    if list(images)!=[0,12,105,180,210,390]:raise toolchain.PreflightError('ZS2 wave timeline incomplete')
    def same(a,b,cell):
        # The live gesture counter overlaps the top 4px of this row. Compare
        # cell ink below that UI edge; an old fill/X would still be detected.
        bounds=(cell*24+2,5,cell*24+22,22)
        return not ImageChops.difference(a.crop(bounds),b.crop(bounds)).getbbox()
    if not same(images[0],blank,16) or not all(same(images[0],preview,i) for i in range(16)):
        raise toolchain.PreflightError('ZS2 waiting targets/first cell disagree with reverse gesture')
    if not same(images[180],blank,0) or not same(images[210],images[390],16):
        raise toolchain.PreflightError('ZS2 native starts are not bounded by 180ms')
    if any(same(images[390],preview,i) or same(preview,blank,i) for i in range(17)):
        raise toolchain.PreflightError('ZS2 wave lacks distinct preview/final X targets')
    return dict(record,checks=['waiting cells equal target preview, no old fills','rightmost starts first','leftmost starts at 180ms','rightmost complete at 210ms','all final at 390ms'])


def x_order(images, blank, size):
    from PIL import ImageChops
    if ImageChops.difference(images[0], blank).getbbox():
        raise toolchain.PreflightError("ZS2 active X starts with a full underdrawing")
    distance=lambda a,b:max(abs(x-y) for x,y in zip(a,b))
    fractions=[]
    for bounds in x_regions(size):
        x0,y0,x1,y1=bounds
        pixels=[(x,y) for y in range(y0,y1) for x in range(x0,x1)
                if distance(blank.getpixel((x,y)),images[210].getpixel((x,y)))>18]
        if not pixels:raise toolchain.PreflightError("ZS2 native X quadrant has no visible ink")
        fractions.append({ms:sum(distance(picture.getpixel(p),images[210].getpixel(p))<6 for p in pixels)/len(pixels)
                          for ms,picture in images.items()})
    if fractions[0][105]<.9 or fractions[1][105]>.05 or fractions[1][210]<.9:
        raise toolchain.PreflightError("ZS2 native X does not write first stroke before second")
    return fractions


def verify_x_sizes(renders, records, *, sizes=(12,24,36)):
    from PIL import Image, ImageChops
    if [r['cell_size'] for r in records]!=list(sizes):raise toolchain.PreflightError("Missing selected X sample")
    result=[]
    for record in records:
        size=record['cell_size']
        def read(name):
            with Image.open(renders/name) as p:
                if p.size!=(size,size):raise toolchain.PreflightError("Scaled X evidence")
                return p.convert('RGB')
        blank=read(record['blank'])
        images={f['elapsed_ms']:read(f['file']) for f in record['controlled']}
        if list(images)!=[0,105,210]:raise toolchain.PreflightError("Incomplete X timeline")
        fractions=x_order(images,blank,size)
        fade={ms:Image.blend(blank,images[210],ms/210) for ms in images}
        reverse=dict(images);reverse[105]=images[105].copy()
        for region,source in zip(x_regions(size),(blank,images[210])):reverse[105].paste(source.crop(region),region[:2])
        for label,mutant in (('global fade',fade),('reversed strokes',reverse)):
            try:x_order(mutant,blank,size)
            except toolchain.PreflightError:pass
            else:raise toolchain.PreflightError('ZS2 negative control accepted '+label)
        live=record['live']
        if len(live)!=3 or any(a['elapsed_ms']>b['elapsed_ms'] for a,b in zip(live,live[1:])):
            raise toolchain.PreflightError("Invalid real-time X frames")
        early=[f for f in live if 0<f['elapsed_ms']<105]
        second=[f for f in live if 105<f['elapsed_ms']<210]
        if not early or not second or live[-1]['elapsed_ms']<210:
            raise toolchain.PreflightError("Real-time capture missed an X stroke")
        # Early native frame must visibly differ both from blank and from final.
        if not any(ImageChops.difference(read(f['file']),blank).getbbox() and
                   ImageChops.difference(read(f['file']),images[210]).getbbox() for f in early):
            raise toolchain.PreflightError("No spatial movement visible at native cell size")
        if ImageChops.difference(read(live[-1]['file']),images[210]).getbbox():
            raise toolchain.PreflightError("Real-time X ends differently from controlled X")
        result.append(dict(record,quadrant_progress=fractions,negative_controls=['global fade rejected','reversed strokes rejected']))
    return result




def verify_fill_sizes(renders, records, *, atlas_frames=False, sizes=(12,24,36)):
    from PIL import Image, ImageChops
    if [r['cell_size'] for r in records] != list(sizes):
        raise toolchain.PreflightError("Missing small/normal/large hatch evidence")
    result = []
    for record in records:
        size = record['cell_size']
        def read(name):
            with Image.open(renders / name) as picture:
                if picture.size != (size, size):
                    raise toolchain.PreflightError("Scaled hatch evidence")
                return picture.convert('RGB')
        blank = read(record['blank'])
        images = {f['elapsed_ms']: read(f['file']) for f in record['controlled']}
        if list(images) != [0,75,105,150,210]:
            raise toolchain.PreflightError("Incomplete hatching timeline")
        progress = zs_hatching.check_hatching(images, blank, size, atlas_frames=atlas_frames)
        rejected = zs_hatching.negative_controls(images, blank, size, atlas_frames=atlas_frames)
        live = record['live']
        if len(live) != 3 or any(a['elapsed_ms'] > b['elapsed_ms'] for a,b in zip(live,live[1:])):
            raise toolchain.PreflightError("Invalid real-time hatch clock")
        for low, high in [(0,105),(105,184)]:
            if not any(low < f['elapsed_ms'] < high and
                       ImageChops.difference(read(f['file']), blank).getbbox() and
                       ImageChops.difference(read(f['file']), images[210]).getbbox() for f in live):
                raise toolchain.PreflightError("Real-time capture missed visible hatch buildup")
        if live[-1]['elapsed_ms'] < 210 or ImageChops.difference(read(live[-1]['file']), images[210]).getbbox():
            raise toolchain.PreflightError("Live hatch final differs")
        result.append(dict(record, spatial_progress=progress, negative_controls=rejected))
    return result
