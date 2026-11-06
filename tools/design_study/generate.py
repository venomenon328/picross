"""Generate editable SVG studies from explicit demo inputs and fixture clues.

Run from repository root: python tools/design_study/generate.py
Rendering is a separate optional step; this module uses only the standard library.
"""
from pathlib import Path
import base64
import hashlib
import html
import json

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/design/z1_1'
BASE = '831b46f9e373e8691c18088efc9f2495fe3defb8'
REF = 'df7ac589e900a6d6d7c5080599c6a5ace47c395d'
INK = '#293e3d'
PAPER = '#fffaf0'
STYLES = {
    's1': dict(name='Das Studienblatt', sub='ILLUSTRATIONSALBUM', display='Fraunces', ui='PlexSans', accent='#843d2d', paper='#fffaf0'),
    's2': dict(name='Unterwegs im Stillen', sub='REISEJOURNAL', display='Fraunces', ui='PlexSans', accent='#285e60', paper='#f5f6ed'),
    's3': dict(name='Farbe nimmt Form an', sub='ATELIER / DRUCKBOGEN', display='Barlow', ui='PlexMono', accent='#873e29', paper='#fff9eb'),
}
ICONS = {
    'fill': ('Füllen', 'Füllen · links Farbe setzen, rechts leer markieren', 'M4 17 L15 6 L19 10 L8 21 L3 22 Z M13 8 L17 12 M16 3 L21 8'),
    'erase': ('Radierer', 'Radierer · Markierungen entfernen', 'M3 15 L13 5 L22 14 L14 22 H10 Z M8 10 L17 19 M14 22 H23'),
    'hand': ('Hand', 'Hand · Raster oder einzelne Hinweisfolge verschieben', 'M7 13 V7 Q7 4 10 6 V12 V3 Q13 1 14 4 V12 V5 Q17 3 18 6 V13 V9 Q21 7 22 10 V17 Q21 23 15 23 H12 Q9 23 7 20 L3 14 Q3 11 6 12 Z'),
    'undo': ('Rückgängig', 'Letzten Strich rückgängig machen', 'M9 5 L3 11 L9 17 M3 11 H15 Q23 11 22 20'),
    'redo': ('Wiederholen', 'Zurückgenommenen Strich wiederholen', 'M17 5 L23 11 L17 17 M23 11 H11 Q3 11 4 20'),
    'minus': ('Verkleinern', 'Raster verkleinern', 'M5 13 H21'),
    'plus': ('Vergrößern', 'Raster vergrößern', 'M5 13 H21 M13 5 V21'),
    'fit': ('Gesamtansicht', 'Ganzes Raster anzeigen', 'M3 10 V3 H10 M16 3 H23 V10 M23 16 V23 H16 M10 23 H3 V16 M9 9 H17 V17 H9 Z'),
    'work': ('Arbeitsgröße', 'Zur Arbeitsgröße zurückkehren', 'M3 3 H9 V9 H3 Z M11 3 H17 V9 H11 Z M3 11 H9 V17 H3 Z M14 22 L22 14 M16 14 H22 V20'),
    'help': ('Hilfe', 'Mausbedienung und Zeichen erklären', 'M8 8 Q8 2 15 3 Q22 5 18 11 L13 15 V17 M13 21 V22'),
    'menu': ('Menü', 'Ansicht, Hinweise und Beenden', 'M4 6 H22 M4 13 H22 M4 20 H22'),
    'album': ('Zum Album', 'Zurück zum Album · Anschlussstelle', 'M12 4 H23 V22 H12 Q8 19 3 22 V4 Q8 1 12 4 V22'),
}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def demo_cells(key, width, height):
    """Transcription of z1-demo-1's disjoint committed strokes, not a solver."""
    cells = [-1] * (width * height)
    strokes = {
        'f01': [(3, 8, 9, 8, 1), (4, 9, 9, 9, 1), (2, 7, 10, 7, 0)],
        'f02': [(1, 1, 38, 1, 4), (0, 0, 12, 0, 0)] + [(5, y, 10, y, 2) for y in range(6, 12)] + [(19, y, 22, y, 3) for y in range(13, 18)] + [(4, 12, 12, 12, 0), (14, 20, 24, 20, 1), (14, 21, 20, 21, 1)],
        'f03': [(40, y, 45, y, 1 + y % 4) for y in range(42, 49)] + [(39, 49, 53, 49, 0), (50, 40, 50, 47, 3)],
    }[key]
    for x1, y1, x2, y2, value in strokes:
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                cells[y * width + x] = value
    return cells


def data(key):
    source = ROOT / f'prototypes/p1/data/{key}.json'
    raw = json.loads(source.read_text())
    # Deliberately whitelist public fields; no solution/reveal enters the SVG data.
    d = {k: raw[k] for k in ('id', 'revision', 'width', 'height', 'palette', 'rows', 'columns')}
    d['cells'] = demo_cells(key, d['width'], d['height'])
    d['fixture_sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
    return d


class SVG:
    def __init__(self, w, h, fonts=('Fraunces', 'PlexSans')):
        self.w, self.h, self.parts = w, h, []
        self.actions = []
        rules = []
        for font in fonts:
            encoded = base64.b64encode((OUT / 'fonts' / f'{font}.ttf').read_bytes()).decode()
            rules.append(f'@font-face{{font-family:{font};src:url(data:font/ttf;base64,{encoded})}}')
        self.parts.append('<defs><style>' + ''.join(rules) + '</style></defs>')

    def add(self, s):
        self.parts.append(s)

    def rect(self, x, y, w, h, fill, stroke='none', sw=1, rx=0, attrs=''):
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {attrs}/>')

    def path(self, path, fill='none', stroke=INK, sw=2, attrs=''):
        self.add(f'<path d="{path}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" {attrs}/>')

    def text(self, x, y, label, size=18, fill=INK, font='PlexSans', weight=400, anchor='start', attrs=''):
        self.add(f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" {attrs}>{html.escape(str(label))}</text>')

    def circle(self, x, y, r, fill, stroke='none', sw=1):
        self.add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def group(self, attrs):
        self.add('<g ' + attrs + '>')

    def end(self):
        self.add('</g>')

    def xml(self, metadata=None):
        meta = html.escape(json.dumps(metadata or {}, ensure_ascii=False))
        return f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}"><title>Z1.1 · Statische Entwurfsstudie</title><metadata>{meta}</metadata>' + ''.join(self.parts) + '</svg>\n'


def background(s, style):
    s.group(f'id="background-{style}" transform="scale({s.w / 1920} {s.h / 1080})"')
    if style == 's1':
        s.rect(0, 0, 1920, 1080, '#dccba9')
        s.path('M0 580 Q380 310 920 570 T1920 400 V1080 H0 Z', '#adb597', 'none')
        s.path('M0 830 Q400 650 860 820 T1920 680 V1080 H0 Z', '#77856e', 'none')
        # A landscape of broad stone strata, not a leaf wallpaper.
        for x, y, w, h in [(1430, 660, 380, 190), (1580, 540, 390, 150), (-70, 780, 300, 230)]:
            s.path(f'M{x} {y+h} L{x+30} {y+45} Q{x+w*.6} {y-15} {x+w} {y+30} L{x+w+30} {y+h} Z', '#c6b792', '#596858', 3)
            s.path(f'M{x+40} {y+80} Q{x+w*.6} {y+50} {x+w-10} {y+70}', 'none', '#968866', 2)
        # A single etched grass clump at the margin, with seed heads.
        for i in range(9):
            x=75+i*16
            s.path(f'M170 1025 Q{x-35} 820 {x} {550+i*15}', 'none', '#3e5147', 3)
            for j in range(4):
                yy=580+i*15+j*27
                s.path(f'M{x} {yy+12} Q{x-30} {yy-20} {x-26} {yy-27} Q{x+4} {yy-17} {x} {yy+12}', '#e3d6ad', '#3e5147', 2)
        s.circle(1710, 160, 74, '#f1e3bc')
    elif style == 's2':
        s.rect(0, 0, 1920, 1080, '#cbdcd5')
        s.circle(1510, 206, 97, '#f4d8a4')
        s.path('M0 520 L180 290 L390 490 L650 275 L920 530 L1230 350 L1480 540 L1780 305 L1920 410 V1080 H0 Z', '#849e96', '#557b78', 3)
        s.path('M0 670 Q380 540 750 650 T1500 600 T1920 700 V1080 H0 Z', '#557b78', 'none')
        s.path('M0 770 Q560 690 1100 775 T1920 740 V1080 H0 Z', '#294f54', 'none')
        s.path('M1340 1080 Q1550 870 1780 900 L1920 950 V1080 Z', '#b3c7b5', '#193f47', 3)
        for yy in (810, 855, 940, 997):
            s.path(f'M1420 {yy} Q1620 {yy-18} 1850 {yy+5}', 'none', '#97b9ad', 2)
        s.path('M0 1080 V940 L120 880 L225 920 L320 1080 Z', '#183f46', 'none')
    else:
        s.rect(0, 0, 1920, 1080, '#dfbb99')
        s.path('M0 0 H810 L420 1080 H0 Z', '#eddbc2', 'none')
        s.path('M1460 0 H1920 V1080 H1320 Z', '#c97655', 'none')
        s.path('M1510 0 L1220 1080 H1420 L1710 0 Z', '#f2ddad', 'none')
        # Abstract folded paper and an ink roller silhouette, no puzzle imagery.
        s.path('M1450 800 L1810 720 L1950 915 L1640 1000 Z', '#efe7d3', '#7c4c39', 3)
        s.path('M1450 800 L1620 846 L1810 720 M1620 846 L1640 1000', 'none', '#9d7757', 3)
        s.group('transform="translate(100 680) rotate(-18)"')
        s.rect(0, 0, 125, 195, '#365751', '#293e3d', 4, 14)
        s.path('M-10 60 H-28 V210 H60 V265', 'none', '#624536', 10)
        s.rect(42, 248, 36, 130, '#9b4c33', '#624536', 3, 9)
        s.end()
        for x in range(30, 1920, 90):
            s.path(f'M{x} 1032 h35', 'none', '#b28766', 1)
    s.end()


def button(s, x, y, key, style, state='normal', scale=1):
    s.actions.append(dict(action=key,rect=[x,y,44*scale,44*scale],state=state))
    t = STYLES[style]
    bg = {'normal': t['paper'], 'hover': '#ddd9bd', 'active': t['accent'], 'disabled': '#e6e5da'}[state]
    fg = '#fffaf0' if state == 'active' else ('#77827a' if state == 'disabled' else INK)
    s.group(f'transform="translate({x} {y}) scale({scale})" data-action="{key}" data-state="{state}"')
    s.add(f'<title>{html.escape(ICONS[key][1])}</title>')
    if style == 's2':
        s.circle(22, 22, 21, bg, INK, 1.5)
    elif style == 's3':
        s.path('M0 0 H38 L44 6 V44 H0 Z', bg, INK, 1.5)
    else:
        s.rect(0, 0, 44, 44, bg, INK, 1.5)
        s.path('M3 41 H41', 'none', INK, 1)
    s.group('transform="translate(9 9)"')
    s.path(ICONS[key][2], 'none', fg, 1.8)
    s.end()
    if state == 'active':
        s.path('M16 49 H28 L22 54 Z', INK, 'none')
    if state == 'disabled':
        s.path('M4 39 L40 5', 'none', '#77827a', 1)
    s.end()


def geometry(key, w, h, ui, layout):
    if w == 1280:
        # Explicit 22 px working zoom for larger clue type, not whole-screen scaling.
        return dict(grid=[300 if layout=='u1' else 310, 222, 29*22, 17*22], cell=22, origin=[0, 0], hints=[210, 120], mini=[1050, 220, 140, 140], tools=[250, 626], title=[90, 71], ui=ui)
    if key == 'f01':
        return dict(grid=[890, 440, 480, 480], cell=24, origin=[0, 0], hints=[192, 144], mini=[1590, 440, 200, 200], tools=[778, 1000], title=[706, 228], ui=ui)
    if key == 'f03':
        return dict(grid=[350, 270, 57*24, 28*24], cell=24, origin=[25, 35], hints=[240, 144], mini=[1764, 290, 132, 132], tools=[400, 992], title=[108, 91], ui=ui)
    return dict(grid=[510 if layout=='u1' else 420, 252, 720, 720], cell=18, origin=[0, 0], hints=[210, 126], mini=[1410 if layout=='u1' else 1450, 220 if layout=='u1' else 650, 180, 180], tools=[325, 1004], title=[300 if layout=='u1' else 210, 90], ui=ui)


def tokens(sequence, capacity):
    """Static raster-end read only, whole tokens and a reserved prefix marker."""
    if len(sequence) <= capacity:
        return [(i, t) for i, t in enumerate(sequence)]
    return [(-1, None)] + list(enumerate(sequence))[-(capacity-1):]


def board(s, d, g, style):
    x,y,w,h=g['grid']; cell=g['cell']; ox,oy=g['origin']; hw,hh=g['hints']; ui=g['ui']
    colors={p['id']:p['color'] for p in d['palette']}
    cols,rows=int(w/cell),int(h/cell)
    paper=STYLES[style]['paper']
    s.group('id="work-surface"')
    s.rect(x-hw-16,y-hh-14,w+hw+32,h+hh+30,paper,INK,2)
    if style=='s1':
        s.rect(x-hw-24,y-hh-14,8,h+hh+30,STYLES[style]['accent'])
        for yy in (y-hh+24,y+h-24):
            s.circle(x-hw-20,yy,3,PAPER)
    elif style=='s2':
        s.path(f'M{x-hw-8} {y-hh-6} h{w+hw+16} v{h+hh+14} h-{w+hw+16} Z','none','#6e8981',1,attrs='stroke-dasharray="5 5"')
        s.path(f'M{x+w-20} {y-hh-14} l36 36 v-36 Z','#ccd8c8',INK,1)
    else:
        for xx,yy in [(x-hw-24,y-hh-22),(x+w+24,y-hh-22),(x-hw-24,y+h+24),(x+w+24,y+h+24)]:
            s.path(f'M{xx-9} {yy} h18 M{xx} {yy-9} v18','none',INK,1)
    s.rect(x,y,w,h,'#faf6ec')
    s.group(f'id="grid" data-cells-sha256="{digest(d["cells"])}"')
    for r in range(rows):
        for c in range(cols):
            value=d['cells'][(oy+r)*d['width']+ox+c]
            xx,yy=x+c*cell,y+r*cell
            if value>0:
                s.rect(xx+2.5,yy+2.5,cell-5,cell-5,colors[value],attrs=f'data-cell="{ox+c},{oy+r},{value}"')
            elif value==0:
                s.path(f'M{xx+5} {yy+5} l{cell-10} {cell-10} M{xx+cell-5} {yy+5} l-{cell-10} {cell-10}','none',INK,1.4,attrs=f'data-cell="{ox+c},{oy+r},0"')
    for c in range(cols+1):
        bold=(ox+c)%5==0
        s.path(f'M{x+c*cell} {y} v{h}','none',INK if bold else '#9baca4',1.5 if bold else .65)
    for r in range(rows+1):
        bold=(oy+r)%5==0
        s.path(f'M{x} {y+r*cell} h{w}','none',INK if bold else '#9baca4',1.5 if bold else .65)
    s.end()
    # Clue baseline and orthogonal centers are tied to actual cells; no row numbering.
    fs=13*ui if cell<=22 else 15*ui
    sx,sy=30*ui,18*ui
    s.group('id="clues"')
    for axis in ('rows','columns'):
        count=rows if axis=='rows' else cols
        start=oy if axis=='rows' else ox
        capacity=int((hw-8)/sx) if axis=='rows' else int((hh-8)/sy)
        for k in range(count):
            seq=d[axis][start+k]
            visible=tokens(seq,capacity)
            if not seq: visible=[(-2,None)]
            for n,(idx,t) in enumerate(visible):
                back=len(visible)-n-.5
                xx=x-back*sx if axis=='rows' else x+(k+.5)*cell
                yy=y+(k+.5)*cell+fs*.34 if axis=='rows' else y-back*sy+fs*.34
                label=str(t['length']) if t else ('…' if idx==-1 else '–')
                color=colors[t['color']] if t else INK
                # Deliberate C1 proposal: original fill + narrow dark outline.
                outline='stroke="#293e3d" stroke-width="0.55" paint-order="stroke fill"' if t and t['color'] in (2,4) else ''
                s.text(xx,yy,label,fs,color,STYLES[style]['ui'],500,'middle',f'{outline} data-clue="{axis},{start+k},{idx}"')
                if d['id']=='F-02' and axis=='rows' and start+k==1 and idx==0:
                    s.path(f'M{xx-8} {yy-fs*.31} h16','none',color,1)
    s.end(); s.end()


def miniature(s,d,g,style):
    x,y,w,h=g['mini']; colors={p['id']:p['color'] for p in d['palette']}; unit=w/d['width']
    s.group(f'id="miniature" data-cells-sha256="{digest(d["cells"])}"')
    s.rect(x-14,y-42,w+28,h+87,STYLES[style]['paper'],INK,2)
    s.text(x,y-17,'DEIN STAND',12,INK,STYLES[style]['ui'],500)
    s.rect(x,y,w,h,'#faf6ec',INK)
    for r in range(d['height']):
        for c in range(d['width']):
            v=d['cells'][r*d['width']+c]
            if v>0:
                s.rect(x+c*unit,y+r*unit,unit,unit,colors[v],attrs=f'data-cell="{c},{r},{v}"')
            elif v==0:
                s.path(f'M{x+c*unit+unit*.2} {y+r*unit+unit*.2} l{unit*.6} {unit*.6} m0 -{unit*.6} l-{unit*.6} {unit*.6}','none',INK,max(.5,unit*.15),attrs=f'data-cell="{c},{r},0"')
    ox,oy=g['origin']; cell=g['cell']; _,_,gw,gh=g['grid']
    s.rect(x+ox*unit,y+oy*unit,gw/cell*unit,gh/cell*unit,'none','#fffaf0',3)
    s.rect(x+ox*unit,y+oy*unit,gw/cell*unit,gh/cell*unit,'none',INK,1)
    s.text(x,y+h+26,'Zeile –   Spalte –',12,INK,STYLES[style]['ui'])
    s.end()


def palette(s,x,y,d,style,scale=1,wrap=4):
    s.group(f'id="palette" transform="translate({x} {y}) scale({scale})"')
    for i,p in enumerate(d['palette']):
        xx=(i%wrap)*48
        s.group(f'transform="translate(0 {(i//wrap)*48})"')
        if style=='s2': s.circle(xx+18,18,18,p['color'],INK,1)
        elif style=='s3': s.path(f'M{xx} 0 H{xx+36} V30 L{xx+30} 36 H{xx} Z',p['color'],INK,1)
        else: s.rect(xx,0,36,36,p['color'],INK)
        if i==0:
            s.rect(xx-4,-4,44,44,'none',INK,2)
            s.circle(xx+18,18,4,'#fffaf0',INK,1)
        s.end()
    s.end()


def screen(style='s1',layout='u1',key='f02',w=1920,h=1080,ui=1):
    t=STYLES[style]; s=SVG(w,h,(t['display'],t['ui'])); background(s,style)
    d=data(key); g=geometry(key,w,h,ui,layout)
    tx,ty=g['title']; x,y,gw,gh=g['grid']; hw,hh=g['hints']
    s.group('id="title"')
    if style=='s1':
        s.rect(tx-12,ty-65,555,83,t['paper'],INK,2)
        s.text(tx+6,ty-39,t['sub'],11,t['accent'],t['ui'],600)
        s.text(tx+6,ty-3,t['name'],34,INK,t['display'],650)
        s.rect(tx+460,ty-65,83,83,t['accent'])
        s.text(tx+501,ty-16,d['id'][-2:],36,PAPER,t['display'],650,'middle')
    elif style=='s2':
        s.path(f'M{tx-18} {ty-57} H{tx+535} L{tx+552} {ty-17} L{tx+535} {ty+18} H{tx-18} Z',t['paper'],INK,1.5)
        s.text(tx,ty-26,t['sub'],11,t['accent'],t['ui'],600)
        s.text(tx,ty+5,t['name'],32,INK,t['display'],450,attrs='font-style="normal"')
        s.circle(tx+505,ty-16,23,'none',t['accent'],1)
        s.path(f'M{tx+505} {ty-32} l7 23 l-7 -5 l-7 5 Z','none',t['accent'],1)
    else:
        s.rect(tx-12,ty-64,574,87,t['paper'])
        s.rect(tx-12,ty-64,574,10,t['accent'])
        s.text(tx,ty-28,t['sub'],11,t['accent'],t['ui'])
        s.text(tx,ty+10,t['name'].upper(),39,INK,t['display'],600)
    s.end()
    board(s,d,g,style); miniature(s,d,g,style)
    # A short dock vs distributed edge groups. No full-height sidebar.
    scale=ui; gap=52*scale
    if key=='f03':
        bx,by=400,h-77
    elif layout=='u1':
        bx,by=g['tools']
    else:
        bx,by=(x-hw-16,h-94 if w==1280 else h-78)
    if layout=='u1':
        s.rect(bx-12,by-10,11*gap+12,64*scale,t['paper'],INK,1)
        for i,k in enumerate(list(ICONS)[:11]): button(s,bx+i*gap,by,k,style,'active' if k=='fill' else 'normal',scale)
    else:
        for i,k in enumerate(['fill','erase','hand','undo','redo']): button(s,bx+i*gap,by,k,style,'active' if k=='fill' else 'normal',scale)
        navx=w-5*gap-38
        for i,k in enumerate(['minus','plus','fit','work']): button(s,navx+i*gap,h-78,k,style,scale=scale)
        button(s,w-136*scale,35,'help',style,scale=scale)
        button(s,w-78*scale,35,'menu',style,scale=scale)
    mx,my,mw,mh=g['mini']
    palette(s,mx,my+mh+74,d,style,scale,2 if key=='f03' else 4)
    if key=='f03':
        s.rect(mx-8,my+mh+176,148,65,t['paper'])
        s.text(mx,my+mh+198,'Raster 100 %',13,INK,t['ui'])
        s.text(mx,my+mh+222,'UI 100 %',13,INK,t['ui'])
    else:
        s.rect(mx-14,my+mh+126*scale,210*scale,30*scale,t['paper'])
        s.text(mx,my+mh+146*scale,f'Raster {round(g["cell"]/24*100)} %  ·  UI {round(ui*100)} %',13*scale,INK,t['ui'])
    # Study caption is outside the product work surface; no invented save success.
    caption=f'{style.upper()} / {layout.upper()}  ·  {d["id"]} / {d["width"]} × {d["height"]}  ·  Beispielteilstand  ·  Statische Studie / C1'
    if key=='f03': caption='F-03 · UI-Testdatensatz – Rätselqualität nicht abgenommen · Statische Studie / C1'
    s.rect(730,30, max(620,len(caption)*7),27,t['paper']) if key=='f03' else None
    cy=49 if key=='f03' else h-9
    cx=1050 if w==1920 and key=='f02' else 24
    if key!='f03': s.rect(cx,h-26, max(640,len(caption)*7),23,t['paper'])
    s.text(cx+10 if key!='f03' else 740,cy,caption,12,INK,t['ui'])
    exported_geometry={k:v for k,v in g.items() if k!='tools'}
    meta=dict(style=style,layout=layout,fixture=key,data_sha256=digest(d),cells_sha256=digest(d['cells']),geometry=exported_geometry,actions=s.actions,dimensions=[w,h],palette=d['palette'],demo_revision='z1-demo-1',contrast_proposal='C1: original fill plus 0.55 px ink outline on colors 2/4')
    return s,meta


def sheet(title,sub,w=1920,h=1080,fonts=('Fraunces','PlexSans')):
    s=SVG(w,h,tuple(dict.fromkeys((*fonts,'PlexSans')))); s.rect(0,0,w,h,PAPER)
    s.text(56,58,'PICROSS / Z1.1 / ENTWURFSSTUDIE',13)
    s.text(56,120,title,42,font=fonts[0],weight=600)
    s.text(56,158,sub,17)
    s.path(f'M56 184 H{w-56}','none',INK,2)
    return s


def icon_sheet():
    s=sheet('Kleine Zeichen, klare Aktionen','26 px Zeichnung · 44 px Ziel · einheitlich 1,8 px Strich · tatsächliche Größe, keine Emoji',h=1160)
    for j,state in enumerate(['Normal','Hover','Aktiv','Deaktiviert']): s.text(570+j*125,222,state,15)
    for i,(key,(name,tip,_)) in enumerate(ICONS.items()):
        yy=250+i*65
        s.text(60,yy+28,name,18)
        for j,state in enumerate(['normal','hover','active','disabled']): button(s,590+j*125,yy,key,'s1',state)
        s.text(1110,yy+28,tip,15)
    s.text(56,1097,'Aktiv: Fläche + Dreieck. Deaktiviert: gedämpft + Diagonale. Zustandsmuster, keine neuen Schalter für Einmalaktionen.',17)
    s.text(56,1127,'Farbauswahl aktiviert Füllen, auch nach Hand/Radierer. Rechtsklick, G1, H1 und atomare Rücknahme bleiben unverändert.',17)
    return s


def typography_sheet():
    s=sheet('Zwei Stimmen für dasselbe Blatt','P1: Fraunces + IBM Plex Sans     /     P2: Barlow Condensed + IBM Plex Mono',fonts=('Fraunces','PlexSans','Barlow','PlexMono'))
    for x,title,font,ui in [(56,'P1 · Redaktionelle Wärme','Fraunces','PlexSans'),(1000,'P2 · Druck und Präzision','Barlow','PlexMono')]:
        s.text(x,243,title,30,font=font,weight=600)
        s.text(x,310,'Ein Bild entsteht',40,font=font,weight=600)
        s.text(x,362,'Füllen · Größe · Rückgängig · ÄÖÜ äöü ß',18,font=ui)
        s.text(x,408,'1 / 7     3 / 8     11 17 38 100',18,font=ui)
        s.text(x,451,'Hinweise 13 px / UI 100 %',16)
        s.text(x,480,'1 7 3 8 11 17 38 100 1 7 3 8 11 17 38',13,font=ui)
        s.text(x,524,'Hinweise 16,25 px / UI 125 %',16)
        s.text(x,555,'1 7 3 8 11 17 38 100 1 7 3 8',16.25,font=ui)
        s.text(x,602,'Echtes H1-Beispiel: F-02, Zeile 2, Originalhinweis 38',16)
        s.text(x+20,639,'38',18,'#6c9aab',ui,anchor='middle',attrs='stroke="#293e3d" stroke-width="0.55" paint-order="stroke fill"')
        s.path(f'M{x+8} 633 h24','none','#6c9aab',1)
        s.text(x+62,639,'38 blaue eigene Zellen: Spalte 2–39; übrige unbekannt.',15,font=ui)
    s.path('M56 682 H1864','none',INK,1)
    s.text(56,726,'C0 / C1 · Helle Originalhinweise',27,font='Fraunces',weight=600)
    s.text(56,764,'Links unverändert; rechts gleicher Farbwert + feine dunkle Kontur. C1 ist eine offene Darstellungsentscheidung.',17)
    for x,outline in [(70,''),(440,'stroke="#293e3d" stroke-width="0.55" paint-order="stroke fill"')]:
        for i,(label,col) in enumerate([('7','#edca78'),('38','#6c9aab'),('11','#bd604a')]):
            s.text(x+i*95,820,label,24,col,attrs=outline)
    s.text(840,814,'Kein Umfärben, kein Zahlenstapeln, keine Perspektive.',18)
    s.text(56,891,'P1: weiche, kräftige Displayserifen; ruhige offene UI-Ziffern. Für S1 und das leichtere S2.',18)
    s.text(56,930,'P2: schmale plakative Überschriften; feste Ziffernbreiten als Drucksatz-Anmutung. Für S3; mehr Platzbedarf.',18)
    s.text(56,984,'Quellen: Google Fonts, jeweilige OFL 1.1 im Paket. Eingebettete Originaldateien, keine Systemfontkopien.',17)
    s.text(56,1021,'UI-Tinte bleibt dunkel auf opakem Papier; Konturprobe betrifft nur Hinweise. Keine Accessibility-Zertifizierung.',17)
    return s


def detail_sheet(style):
    t=STYLES[style]; full,meta=screen(style)
    s=sheet(f'{style.upper()} · {t["name"]}','Identität ohne Landschaft: echte Ausschnitte derselben Hauptkomposition.',fonts=(t['display'],t['ui']))
    # Nested viewports crop the actual editable screen groups, not a loose moodboard.
    content=''.join(full.parts[1:])
    for x,y,w,h,vb in [(56,220,800,650,'275 18 1000 812.5'),(920,220,400,400,'1360 165 400 400'),(920,650,900,100,'310 992 650 72.222')]:
        s.add(f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="{vb}"><style>#background-{style}{{display:none}}</style>{content}</svg>')
    descriptions={
        's1':['Registerzunge + dunkle Bindekante, kräftige Buchserifen.', 'Werkzeuge als quadratische Druckfelder mit Unterstrich.', 'Material: helles, flaches Papier; kein großflächiger Panelcontainer.'],
        's2':['Schmales Journalbanner + genähter Doppelrahmen.', 'Runde Instrumente und ringförmige Farbchips.', 'Material: kühles Schreibblatt, gefaltete Ecke; präzise Ebene.'],
        's3':['Plakatzeile + Beschnitt-/Passmarken am Druckbogen.', 'Angeschnittene Werkzeugfelder, Chips mit abgeschnittener Ecke.', 'Material: unbeschichteter Bogen; streng rechtwinklig, ohne 3D-Zwang.'],
    }
    for i,line in enumerate(descriptions[style]): s.text(930,789+i*38,line,17,font=t['ui'])
    for i,col in enumerate([t['paper'],t['accent'],INK,'#faf6ec']):
        s.rect(60+i*190,925,160,46,col,INK)
        s.text(60+i*190,999,col,15,font=t['ui'])
    s.text(930,959,'Alle Ausschnitte stammen aus F-02 / U1.',17,font=t['ui'])
    s.text(930,998,'Hintergrund ausgeblendet; Raster und Originalpalette unverändert.',15,font=t['ui'])
    return s


def layout_sheet():
    s=sheet('U1 / U2 · Gleiche Werkzeuge, anderer Rhythmus','S1 und F-02 konstant. Bemaßte Flächen; sichtbarer Hintergrund als echte Restfläche, nicht als Panelinhalt.')
    for j,layout in enumerate(['u1','u2']):
        x=56+j*936; g=geometry('f02',1920,1080,1,layout)
        s.text(x,238,layout.upper()+(' · Kurze Randwerkzeugleiste' if j==0 else ' · Offene Eckgruppen'),26,font='Fraunces',weight=600)
        s.group(f'transform="translate({x} 270) scale(.455)"')
        s.rect(0,0,1920,1080,'#c6cebb')
        gx,gy,gw,gh=g['grid']; hw,hh=g['hints']
        s.rect(gx-hw-16,gy-hh-14,gw+hw+32,gh+hh+30,PAPER,INK,2)
        s.rect(gx,gy,gw,gh,'#b6c9bf',INK,2)
        s.rect(gx-hw,gy,hw,gh,'#ebce94',INK)
        s.rect(gx,gy-hh,gw,hh,'#ebce94',INK)
        mx,my,mw,mh=g['mini']; s.rect(mx,my,mw,mh,'#cc947d',INK)
        if j==0: s.rect(313,994,584,64,INK)
        else:
            s.rect(194,1002,260,64,INK); s.rect(1622,1002,208,64,INK); s.rect(1784,35,110,44,INK)
        for xx,yy,txt in [(gx+gw/2,gy+gh/2,'720 × 720'),(gx-hw/2,gy+gh/2,'210 × 720'),(gx+gw/2,gy-hh/2,'720 × 126'),(mx+90,my+90,'180 × 180')]:
            s.text(xx,yy,txt,25,INK,anchor='middle')
        s.end()
        s.text(x,810,'Raster: 518.400 px²  /  Hinweisstreifen: 241.920 px²',17)
        s.text(x,849,'Miniatur: 32.400 px²  /  11 Ziele: je 44 × 44 px',17)
        s.text(x,888,'Rasterzelle: 18 px · 75 % Arbeitszoom · UI 100 %',17)
    s.text(56,967,'U1 bündelt die Suche nach Aktionen. U2 verteilt Bearbeitung unten links, Zoom unten rechts, Hilfe/Menü oben rechts.',18)
    s.text(56,1008,'Exakte Rechtecke und berechnete freie Hintergrundfläche je Screen: manifest.json. Keine durchgehende rechte Sidebar.',17)
    return s


def save(name,s,meta=None):
    (OUT/'svg'/f'{name}.svg').write_text(s.xml(meta),encoding='utf-8',newline='\n')
    return {'name':name,'dimensions':[s.w,s.h],**(meta or {})}


def main():
    records=[]
    for key in ('f01','f02','f03'):
        d=data(key)
        compact='{\n'+',\n'.join('  '+json.dumps(k)+': '+json.dumps(v,ensure_ascii=False,separators=(',',':')) for k,v in d.items())+'\n}\n'
        (OUT/'sources'/f'{key}-public-demo.json').write_text(compact,encoding='utf-8',newline='\n')
    for style in STYLES:
        s,meta=screen(style); records.append(save(f'{style}-u1-f02-1920',s,meta))
        records.append(save(f'{style}-detail',detail_sheet(style)))
        bg=SVG(1920,1080,()); background(bg,style); records.append(save(f'{style}-background',bg))
    s,meta=screen('s1','u2'); records.append(save('s1-u2-f02-1920',s,meta))
    for layout in ('u1','u2'):
        for key,w,h,ui in [('f01',2560,1440,1),('f03',1920,1080,1),('f02',1280,720,1.25)]:
            s,meta=screen('s1',layout,key,w,h,ui)
            records.append(save(f's1-{layout}-{key}-{w}',s,meta))
    records.append(save('icons',icon_sheet()))
    records.append(save('typography',typography_sheet()))
    records.append(save('layouts',layout_sheet()))
    manifest=dict(base=BASE,reference_head=REF,demo_revision='z1-demo-1',demo_source_sha256=hashlib.sha256((OUT/'sources/demo.gd.txt').read_bytes()).hexdigest(),study='Static SVG compositions; not Godot captures',records=records)
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
    print(f'Generated {len(records)} editable SVGs')


if __name__=='__main__':
    main()
