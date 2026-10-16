"""HS native number/X isolation, complete ink and stable identity evidence."""
from __future__ import annotations
import json
import math
from pathlib import Path

from p1_preflight import PreflightError, verify_sha256


def require(ok, message):
    if not ok:
        raise PreflightError("HS186: " + message)


def panel(images, samples):
    from PIL import ImageChops
    # Production CLOSED with just its cross suppressed must retain precisely the
    # FILLED number, including native C1 and antialiasing. Total dark ink alone
    # cannot establish this: the extra cross could hide an opaque number.
    require(ImageChops.difference(images['filled'], images['closed-number']).getbbox() is None,
            'identical FILLED/CLOSED number and C1 pixels')
    changed = ImageChops.difference(images['filled'], images['closed'])
    white = images['open'].copy()
    white.paste((255, 255, 255), (0, 0, *white.size))
    counts = dict(tokens=0, markers=0, alpha_pixels=0)
    for sample in samples:
        x, y, w, h = sample['box']
        box = (math.floor(x), math.floor(y), math.ceil(x+w), math.ceil(y+h))
        crops = {k: image.crop(box) for k, image in images.items()}
        if not sample['text'].isdecimal():
            require(crops['open'].tobytes() == crops['filled'].tobytes() == crops['closed'].tobytes(),
                    'markers never fade or receive a cross')
            require(crops['cross'].getextrema() == ((255,255),)*3, 'no marker cross pixels')
            counts['markers'] += 1
            continue
        counts['tokens'] += 1
        require(ImageChops.difference(crops['open'], crops['filled']).getbbox() is not None,
                'positive number visibly fainter')
        require(changed.crop(box).getbbox() is not None, 'visible whole-token cross')
        paths = sample['strokes']
        require(len(paths) == 2 and all(len(p) == 4 for p in paths)
                and paths[0][-1][0] > paths[0][0][0] and paths[0][-1][1] > paths[0][0][1]
                and paths[1][-1][0] < paths[1][0][0] and paths[1][-1][1] > paths[1][0][1],
                'two opposed hand-drawn diagonals across a single token')
        # Unoutlined mono/dark pixels isolate the number alpha independently
        # of cross overlap and the two-layer C1 compositing in light colors.
        if sample['color_id'] in (0, 1):
            ratios = []
            for opened, filled in zip(crops['open'].getdata(), crops['filled'].getdata()):
                a = sum(255-v for v in opened)
                if a >= 200:
                    ratios.append(sum(255-v for v in filled)/a)
            require(ratios and .58 <= sum(ratios)/len(ratios) <= .62,
                    'native number opacity is 60%, below the former 78%')
            counts['alpha_pixels'] += len(ratios)
        # Adjacent dense numbers/markers remain disjoint and all non-white
        # pixels must be enclosed by the reserved actual glyph/X/C1/AA boxes.
    for layer in ('open','filled','closed','cross'):
        outside = ImageChops.difference(images[layer], white)
        for sample in samples:
            x,y,w,h = sample['box']
            outside.paste((0,0,0),(math.floor(x),math.floor(y),math.ceil(x+w),math.ceil(y+h)))
        require(outside.getbbox() is None, 'no ink outside measured envelopes')
    for i, a in enumerate(samples):
        ax,ay,aw,ah = a['box']
        for b in samples[i+1:]:
            bx,by,bw,bh = b['box']
            require(ax+aw <= bx+.001 or bx+bw <= ax+.001 or ay+ah <= by+.001 or by+bh <= ay+.001,
                    'dense neighboring envelopes do not overlap')
    return counts


def verify(directory: Path) -> dict:
    from PIL import Image
    report = json.loads((directory/'hs-native.json').read_text(encoding='utf-8'))
    expected = {(w,h,u,c) for w,h,u in ((1280,720,1.25),(1920,1080,1),(2560,1440,1.25))
                for c in (16,24,40,23.37)}
    records = report['records']
    require(report['font_sha256'] == '4031afdb556558ffdecd48488fd1ae7eee857e804f4622ac5154cc7bb0c4cb23', 'actual selected font bytes')
    require(not report['failures'] and report['display'] != 'headless' and report['renderer'], 'native success')
    require(len(records)==12 and {(*r['client'],r['ui'],r['cell']) for r in records}==expected,
            'exact common-window/UI and fractional-cell matrix')
    checks = []
    controls = []
    for record in records:
        require(record['stable'], 'redraw/zoom/fresh-session pixel identity')
        samples = record['samples']
        require(len(samples)==64 and {(s['axis'],s['color_id'],s['text']) for s in samples} ==
                {(a,c,s) for a in ('row','column') for c in (0,1,2,4)
                 for s in ('1','11','17','23','40','50','…','–')}, 'whole-token/axis/mono/color coverage')
        images = {}
        for layer, file in record['files'].items():
            verify_sha256(directory/file['file'],file['sha256'])
            with Image.open(directory/file['file']) as image:
                images[layer] = image.convert('RGB')
        checks.append(panel(images,samples))
        if not controls:
            for label, layer, replacement in (('opaque closed number','closed-number','open'),
                                              ('missing cross','closed','filled'),
                                              ('missing fading','filled','open')):
                bad = images.copy()
                bad[layer] = images[replacement]
                try: panel(bad,samples)
                except PreflightError: controls.append(label)
                else: raise PreflightError('HS186 negative control escaped: '+label)
    result = dict(status='success',native_records=12,original_pngs=60,
                  numeric_tokens=sum(c['tokens'] for c in checks),
                  unmarked_markers=sum(c['markers'] for c in checks),
                  isolated_alpha_pixels=sum(c['alpha_pixels'] for c in checks),
                  negative_controls=controls,renderer=report['renderer'],
                  owner_acceptance='HS-M01 OPEN',independent_review='HS-R01 OPEN')
    (directory/'hs-acceptance.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result
