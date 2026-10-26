"""HC native pixel, real font metrics, and unchanged font-input evidence."""
from __future__ import annotations
import json
import copy
from pathlib import Path
import p1_preflight as toolchain
from vs2_v1_verify import require, typography


def verify_retained(directory: Path) -> list[str]:
    """The bounded delivery must keep six current open mono zoom samples."""
    report = json.loads((directory/'hc92-native.json').read_text(encoding='utf-8'))
    samples = [r for r in report['records'] if r['status']==0 and not r['colored']]
    expected = {(cell,ui,before) for cell in (16,24,40) for ui in (1,1.25) for before in (False,)}
    require(len(samples)==6 and {(r['cell'],r['ui_scale'],r['before']) for r in samples}==expected,
            'HC retained zoom comparison coverage')
    for sample in samples:
        toolchain.verify_sha256(directory/sample['file'],sample['sha256'])
    return [r['file'] for r in samples]


def verify(directory: Path) -> dict:
    from PIL import Image, ImageChops
    report = json.loads((directory/'hc92-native.json').read_text(encoding='utf-8'))
    records = report['records']
    expected = {(cell,ui,color,status,before) for cell in (16,24,40) for ui in (1,1.25)
                for color in (False,True) for status in range(3) for before in (False,)}
    key = lambda r: (r['cell'],r['ui_scale'],r['colored'],r['status'],r['before'])
    require(not report['failures'] and len(records)==36 and {key(r) for r in records}==expected,'HC full native matrix')
    indexed = {key(r):r for r in records}
    for r in records:
        toolchain.verify_sha256(directory/r['file'],r['sha256'])
        with Image.open(directory/r['file']) as image:
            red,green,blue = image.convert('RGB').split()
            mask = ImageChops.darker(ImageChops.darker(red,green),blue).point(lambda v: 255 if v/255<.85 else 0)
            measured = []
            for i in range(8):
                x,y = 20+110*(i%4),20+100*(i//4)
                box = mask.crop((x,y,x+100,y+80)).getbbox()
                require(box is not None,'HC nonempty native glyph pixels')
                measured.append([x+box[0],y+box[1],box[2]-box[0],box[3]-box[1]])
            require(measured == r['pixels'],'HC independently measured PNG ink')
        if r['before']:
            continue
        typography(dict(r,actual_cell=r['cell'],row_pitch=r['pitch'][0],column_pitch=r['pitch'][1]))
        for i,box in enumerate(r['pixels']):
            x,y,w,h = box
            require(w>0 and h>0,'HC visible complete glyph')
            center = [70+110*(i%4),60+100*(i//4)]
            extent = [r['pitch'][0],r['cell']] if i<4 else [r['cell'],r['pitch'][1]]
            require(x>=center[0]-extent[0]/2-.5 and x+w<=center[0]+extent[0]/2+.5
                    and y>=center[1]-extent[1]/2-.5 and y+h<=center[1]+extent[1]/2+.5,'HC native pixel exceeds cell/slot')
    for ui in (1,1.25):
        for color in (False,True):
            for status in range(3):
                after = [indexed[(c,ui,color,status,False)] for c in (16,24,40)]
                heights = [max(b[3] for b in r['pixels']) for r in after]
                require(heights[0]<heights[1]<heights[2],'HC visible zoom growth')
                require(after[0]['pitch'][0]<24*ui and after[0]['pitch'][0]<after[1]['pitch'][0]<after[2]['pitch'][0],'HC compact/growing common slots')
    negative_controls = []
    source = next(r for r in records if not r['before'])
    for label,mutate in [('wrong digit font',lambda r:r['typography']['selected']['row'][0].update(font='IBM Plex Sans')),
                         ('smaller grade',lambda r:r.update(font_px=r['font_px']-1)),
                         ('fixed row pitch',lambda r:r['pitch'].__setitem__(0,24*r['ui_scale'])),
                         ('wrong font bytes',lambda r:r['typography'].update(sha256='0'*64))]:
        bad = copy.deepcopy(source)
        mutate(bad)
        try:
            typography(dict(bad,actual_cell=bad['cell'],row_pitch=bad['pitch'][0],column_pitch=bad['pitch'][1]))
        except toolchain.PreflightError:
            negative_controls.append(label)
        else:
            raise toolchain.PreflightError('HC negative control escaped: '+label)
    return dict(status='success',native_records=36,digits=report['digits'],negative_controls=negative_controls,
                cases=[{k:r[k] for k in ('cell','before','font_px','pitch','pixels')}
                       for r in records if r['ui_scale']==1 and r['status']==0 and not r['colored']],
                owner_acceptance='HC-M01 OPEN',independent_review='OPEN')
