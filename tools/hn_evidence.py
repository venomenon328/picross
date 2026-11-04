"""Independent HN band oracle over the exact native sample pixels, not full paper frames."""
import hashlib
import re

from at_evidence import png


def verify(directory, report):
    rows = [r for r in report['records'] if r['kind'] == 'pixels']
    expected = {f'hn-{w}-ui{u}-{kind}.png'
                for w,u in ((1280,125),)
                for kind in ('row','column','grid','complete-row','drag-row')}
    if (report['failures'] or report['checks'] < 100 or len(rows) != len(expected)
            or {r['file'] for r in rows} != expected):
        raise ValueError('Incomplete native HN cases')
    for row in rows:
        if (row.get('evidence') != 'picross-hn-samples-v1'
                or set(row.get('source_rgba_sha256', {})) != {'frame','baseline','samples'}
                or any(not re.fullmatch('[0-9a-f]{64}',str(v)) for v in row['source_rgba_sha256'].values())):
            raise ValueError('Missing HN original source binding')
        size,pixel = png(directory/row['file'], rgba=True)
        if size != (50,100):
            raise ValueError('Wrong HN original sample dimensions')
        raw = bytes(c for y in range(100) for x in range(50) for c in pixel(x,y))
        if hashlib.sha256(raw).hexdigest() != row['source_rgba_sha256']['samples']:
            raise ValueError('HN pixels differ from native readback')
        cx,cy = row['context']
        kind = row['file'].split('-',3)[3].removesuffix('.png')
        width = int(row['file'].split('-')[1])
        height,ui = {1280:(720,1.25),1920:(1080,1.0),2560:(1440,1.25)}[width]
        context = {'row':[-1,2],'column':[2,-1],'grid':[2,2],
                   'complete-row':[-1,49],'drag-row':[-1,2]}[kind]
        if [cx,cy] != context or row['cell'] <= 0 or row['client'] != [width,height] or row['ui'] != ui:
            raise ValueError('Wrong HN band context')
        ox,oy = row['grid_origin']
        bx,by,bw,bh = row['board']
        ex,ey,ew,eh = row['overlay']
        counts = [0,0]
        for y in range(50):
            for x in range(50):
                px = ox+(x+.4)*row['cell']
                py = oy+(y+.4)*row['cell']
                if not (0 <= px < bw and 0 <= py < bh and
                        0 <= round(bx)+px < row['client'][0] and
                        0 <= round(by)+py < row['client'][1]):
                    raise ValueError('HN sample outside original board/client')
                if ew>0 and eh>0 and ex-3 <= px < ex+ew+3 and ey-3 <= py < ey+eh+3:
                    continue
                marked = x==cx or y==cy
                if (pixel(x,y) != pixel(x,y+50)) != marked:
                    raise ValueError('HN original band/phantom pixels failed')
                counts[0 if marked else 1] += 1
        if counts != [row['marked'],row['unmarked']] or counts[0] <= 0 or counts[1] <= 100:
            raise ValueError('Incomplete HN original pixel coverage')
    return len(rows)
