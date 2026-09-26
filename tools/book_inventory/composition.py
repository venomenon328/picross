"""BP-3 static composition only. Read BP-1R/BP-2; never write their files.

Optional build: existing isolated Playwright/Pillow, Edge and temporary pinned fonts.
Delivery verification and ZIP use the standard library; no browser/network in CI.
"""
import argparse
import base64
import copy
import html
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET

try:
    from . import production as p, artwork as a
except ImportError:
    import production as p, artwork as a

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/design/book_inventory/composition'
BASE = '66b9d39dd3dbce908ff663a18c059351cfccf557'
INK, PAPER, BRASS = '#293e3d', '#fffaf0', '#8c7047'
ET.register_namespace('', p.NS['s'])
STATES = ['normal', 'hover', 'pressed', 'active', 'disabled']
STATE_LABELS = ['Normal', 'Hover', 'Gedrückt', 'Ausgewählt', 'Deaktiviert']
DEFS = '''<defs>
<linearGradient id="card" x2="0" y2="1"><stop stop-color="#fffaf0"/><stop offset="1" stop-color="#eee2c9"/></linearGradient>
<linearGradient id="brass" x2="0" y2="1"><stop stop-color="#d6bd83"/><stop offset="0.45" stop-color="#a68a55"/><stop offset="1" stop-color="#746042"/></linearGradient>
<linearGradient id="enamel" x2="0" y2="1"><stop stop-color="#395957"/><stop offset="1" stop-color="#243c3b"/></linearGradient>
</defs>'''


def write(name, data):
    target = OUT / name
    target.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, str):
        target.write_text(data, encoding='utf-8', newline='\n')
    else:
        a.write_json(target, data)


def txt(x, y, label, size=14, zone=None, extra=''):
    return p.text(x, y, label, size, (f'data-zone="{zone}" ' if zone else '') + extra)


def chamfer(r, fill, stroke=BRASS, cut=4, extra=''):
    x, y, w, h = r
    return (f'<path d="M{x+cut} {y} H{x+w-cut} L{x+w} {y+cut} V{y+h-cut} '
            f'L{x+w-cut} {y+h} H{x+cut} L{x} {y+h-cut} V{y+cut} Z" '
            f'fill="{fill}" stroke="{stroke}" {extra}/>')


def inset(r, n):
    x, y, w, h = r
    return [x+n, y+n, w-2*n, h-2*n]


def serialize(node):
    return ET.tostring(node, encoding='unicode')


def action(a0, colors, icons, ui=1, state='normal'):
    """Hit rect stays exact; all paint incl. selection lies inside it."""
    key = a0['id']; r = a0['rect']; x, y, w, h = r
    nav = key in p.NAV
    tooltip = p.NAV[key][1] if nav else ('Farbe wählen · aktiviert Füllen' if key.startswith('color-') else icons[key][1])
    attrs = f'data-action="{key}" data-state="{state}"'
    if nav:
        attrs += f' data-target="{p.NAV[key][2]}"'
    hit = p.rect(r, 'none', 'none', 'data-hit="true"')
    fill = {'normal':'url(#card)', 'hover':'#e0ece6', 'pressed':'#c5d6cd', 'active':'url(#enamel)', 'disabled':'#e9e2d4'}[state]
    mounting = chamfer(inset(r, .5), 'url(#brass)', '#68583f', 4*ui)
    mounting += chamfer(inset(r, 2*ui), fill, '#b9a578', 3*ui)
    # A slim top highlight and lower recess, both inside the original hit area.
    mounting += p.path(f'M{x+6*ui} {y+4*ui} H{x+w-6*ui}', '#fff5d6', .7)
    mounting += p.path(f'M{x+6*ui} {y+h-3*ui} H{x+w-6*ui}', '#74664d', .7)
    content = ''
    if key.startswith('color-'):
        content += p.rect(inset(r, 5*ui), colors[int(key.split('-')[1])], 'none', 'data-swatch="true"')
        if state == 'active':
            # Selection is outside the true RGB swatch, never a tint/check on the colour.
            corners = f'M{x+2*ui} {y+14*ui} V{y+2*ui} H{x+14*ui} M{x+w-14*ui} {y+h-2*ui} H{x+w-2*ui} V{y+h-14*ui}'
            content += p.path(corners, INK, 3*ui)+p.path(corners, PAPER, ui)
    else:
        ix, iy = a0['image_rect'][:2]
        icon = p.NAV[key][3] if nav else icons[key][2]
        color = PAPER if state == 'active' else ('#757970' if state == 'disabled' else INK)
        shift = ui if state == 'pressed' else 0
        content += f'<g transform="translate({ix} {iy+shift}) scale({ui})">'+p.path(icon, color, 1.8, 'stroke-linecap="round" stroke-linejoin="round"')+'</g>'
        if state == 'active':
            content += p.path(f'M{x+11*ui} {y+h-6*ui} H{x+w-11*ui}', PAPER, 2*ui)
    if state == 'disabled':
        content += p.path(f'M{x+6*ui} {y+h-7*ui} h{4*ui}', '#757970', 1.5*ui)
    return ('<g '+attrs+'>'+hit+mounting+'</g>',
            '<g '+attrs+'>'+hit+content+f'<title>{html.escape(tooltip)}</title></g>')


def main_layers(g):
    root = ET.parse(p.OUT/'svg'/f'{g["name"]}-ui.svg').getroot()
    precise = root.find('s:g', p.NS)
    content = []
    for key in ('grid', 'clues', 'miniature'):
        node = copy.deepcopy(precise.find(f's:g[@id="{key}"]', p.NS))
        if key == 'miniature':
            # Card and label are redesigned; the entire miniature graphic stays intact.
            node.remove(node[0]); node.remove(node[0])
        content.append(serialize(node))
    r = g['rects']; ui = g['ui_scale']; mx, my, mw, mh = r['miniature']
    mounting = []
    cr = r['mini_card']; cx, cy, cw, ch = cr
    # Everything stays within the pre-existing card reserve, including the shadow.
    mounting += [chamfer(inset(cr, .5), '#a38b65', '#77684f', 3),
                 chamfer([cx+1, cy+1, cw-4, ch-4], 'url(#card)', '#d7c49c', 2),
                 p.rect(r['miniature'], PAPER, 'none')]
    for xx in (cx+3, cx+cw-7):
        mounting.append(p.rect([xx, cy+7, 3, 13], 'url(#brass)', '#8c7047', 'stroke-width="0.5"'))
    mounting.append(p.path(f'M{cx+9} {my-5} H{cx+cw-9}', '#c1b18d', .7))
    content.append(txt(mx+2, my-13, 'Dein Stand', 12*ui, 'mini_card', 'font-weight="600" letter-spacing="0.25"'))
    # Three tool wells share one language, with functional grouping 3 / 2 / 4.
    tools = [v for v in g['actions'] if v['group']=='tools']
    for group in (tools[:3], tools[3:5], tools[5:]):
        first, last = group[0]['rect'], group[-1]['rect']
        well = [first[0]-3*ui, first[1]-3*ui, last[0]+last[2]-first[0]+6*ui, first[3]+6*ui]
        mounting.append(chamfer(well, '#cbb991', '#8b7652', 5*ui))
    pr = r['palette']
    if g['fixture']=='f01':pr=[*pr[:2],56,56]
    # The mounting stays behind the swatches; its edge cannot intrude on their hits.
    mounting.append(chamfer(inset(pr, 1), 'url(#card)', '#ad936a', 5))
    icons = p.read('sources/icons.json'); d = p.read('sources/'+g['fixture']+'-public-demo.json')
    colors = {v['id']:v['color'] for v in d['palette']}
    for item in g['actions']:
        state = 'active' if item['id'] in ('fill', 'color-1') else 'normal'
        m, c = action(item, colors, icons, ui, state)
        mounting.append(m); content.append(c)
    tx, ty = r['title'][:2]
    content.append(txt(tx, ty+28, 'Sammlung / '+d['id'], 28, 'title', 'style="font-family:Fraunces,serif;font-weight:600"'))
    x, y = r['coordinates'][:2]
    content.append(txt(x+6, y+21*ui, 'Zeile –  Spalte –', 13*ui, 'coordinates'))
    x, y = r['status'][:2]
    for i, label in enumerate([f'Raster {g["cell_px"]} px · UI {round(ui*100)} %', 'Füllen · Farbe 1']):
        content.append(txt(x+6, y+(20+i*24)*ui, label, 12*ui, 'status', 'font-weight="500"' if i else ''))
    return mounting, content


def state_board():
    w, h = 1600, 1320
    m = [p.rect([0,0,w,h], PAPER, 'none')]
    c = [txt(48, 52, 'Werkzeuge, Farben und Rückwege', 28, extra='style="font-family:Fraunces,serif;font-weight:600"'),
         txt(48, 84, 'Statische Zustandsbeispiele · keine ausgeführten Aktionen oder Speichervorgänge', 17)]
    icons = p.read('sources/icons.json'); d = p.read('sources/f02-public-demo.json')
    colors = {v['id']:v['color'] for v in d['palette']}
    rows = ['fill','erase','hand','color-2','undo','redo','nav-album','nav-information','nav-work']
    for col, label in enumerate(STATE_LABELS):
        c.append(txt(390+col*225, 130, label, 17))
    for row, key in enumerate(rows):
        y = 155+row*70
        label = p.NAV[key][0] if key in p.NAV else ('Farbmuster 2' if key.startswith('color-') else icons[key][0])
        c.append(txt(48, y+29, label, 18))
        for col, state in enumerate(STATES):
            x = 390+col*225
            applicable = not (state=='active' and key in ('undo','redo')) and not (state=='disabled' and key in ('fill','erase','hand','color-2'))
            if not applicable:
                c.append(txt(x, y+27, '—', 18)); continue
            item = {'id':key, 'rect':[x,y,44,44], 'image_rect':[x+9,y+9,26,26]}
            mm, cc = action(item, colors, icons, state=state)
            m.append(mm); c.append(cc)
        c.append(p.path(f'M48 {y+58} H1530', '#d4c7a9', .6))
    c += [txt(48, 812, 'Auswahl: Unterstrich am Werkzeug, helle Eckmarken am Farbmuster; zusätzlich dauerhafter Werkzeug-/Farbstatus.', 16),
          txt(48, 839, 'Farbauswahl aktiviert Füllen, auch nach Hand/Radierer. Undo/Redo sind Aktionen ohne dauerhaften Auswahlzustand.', 16),
          txt(48, 866, 'Deaktivierte Navigation: Beispiel eines durch Pflicht-Flush blockierten Übergangs. Rückweg und Zustand bleiben erhalten.', 16)]
    # Two exact original hint examples, one overflowing line and the established H1 row.
    m.append(chamfer([48,900,1480,125], 'url(#card)', BRASS, 4))
    c.append(txt(68,925,'Tooltip · F-02 / vollständige Originalfolge, Spalte 20 · BP-1R-Quelldaten',16))
    for i, token in enumerate(d['columns'][19]):
        color = colors[token['color']]
        ex = f'style="fill:{color}" data-clue-example="columns,19,{i}"'
        if token['color'] in (2,4): ex += ' stroke="#293e3d" stroke-width="0.55" paint-order="stroke fill"'
        c.append(txt(78+i*34, 957, token['length'], 16.25, extra=ex))
    c.append(txt(68,998,'H1 · Zeile 2:',16))
    token = d['rows'][1][0]
    c += [txt(180,998,token['length'],16.25,extra=f'style="fill:{colors[token["color"]]}" data-clue-example="rows,1,0" stroke="#293e3d" stroke-width="0.55" paint-order="stroke fill"'),
          p.path('M178 992 h24',colors[token['color']],1), txt(230,998,'bestehendes Beispiel aus z1-demo-1; kein Lösungsvergleich.',16)]
    for x, title, lines in [
        (48,'Speicherfehler',['Temporäre Datei nicht schreibbar.', 'Pflicht-Flush fehlgeschlagen: Übergang bleibt blockiert.']),
        (808,'Backup geladen',['Primärstand beschädigt. Vor weiterem Speichern', 'Backup bewusst übernehmen. Schreibsperre bleibt aktiv.'])]:
        m += [chamfer([x,1060,720,150], 'url(#card)', BRASS, 5), p.rect([x+1,1065,4,139],INK,'none')]
        c.append(txt(x+24,1095,title,21,extra='font-weight="600"'))
        for i,line in enumerate(lines): c.append(txt(x+24,1127+i*28,line,16))
    c += [txt(48,1245,'Quellen: P1 §6; ui/main.gd und model/save_store.gd am Inputcommit. Beispielzustände, keine neue Meldungssemantik.',16),
          txt(48,1275,'Tooltip der Aktion Füllen: „Füllen · links Farbe setzen, rechts leer markieren“. Treffer 44 × 44 px; Icon 26 × 26 px.',16)]
    return [w,h],m,c


def connection_board():
    w,h=1280,720
    m=[p.rect([0,0,w,h],PAPER,'none')]
    c=[txt(40,54,'Anschluss der Informationsseite',28,extra='style="font-family:Fraunces,serif;font-weight:600"'),
       txt(40,86,'Schematischer rechter Anschluss · kein drittes Buchbild, keine native Navigation',17)]
    icons=p.read('sources/icons.json')
    for x,key,title,desc in [(40,'nav-album','Album','Sammlung / Blattauswahl'),(450,'nav-work','Arbeitsseite','Raster / eigene Miniatur / Werkzeuge'),(860,'nav-information','Information','Einstellungen / Hilfe')]:
        m.append(chamfer([x,125,370,135],'url(#card)',BRASS,4))
        mm,cc=action({'id':key,'rect':[x+18,144,44,44],'image_rect':[x+27,153,26,26]}, {},icons,state='active' if key=='nav-work' else 'normal')
        m.append(mm);c += [cc,txt(x+78,174,title,22),txt(x+18,217,desc,16),txt(x+18,242,key+' → '+p.NAV[key][2],14)]
    for x,title,lines in [
        (40,'Einstellungen',['UI-Skalierung: 100 % / 125 %','Hinweise rasterseitig ausrichten','Erfüllte Hinweise markieren · sitzungsweit','Beenden · Pflicht-Flush bleibt verbindlich']),
        (660,'Hilfe',['Füllen / Radierer / Hand','Hinweisfolgen einzeln ziehen; Tooltip ergänzt','Escape verwirft die laufende Geste','Statistik: später / Umfang offen'])]:
        m.append(chamfer([x,300,570,218],'url(#card)',BRASS,4))
        c.append(txt(x+24,340,title,23,extra='font-weight="600"'))
        for i,line in enumerate(lines): c.append(txt(x+24,376+i*33,line,17))
    c += [txt(40,564,'Rückweg aus Album und Information: nav-work → work · „Zur Arbeitsseite zurück · Arbeitsstand erhalten“',17),
          txt(40,598,'Erhalten: Zellen, Undo/Redo, Farbe/Werkzeug, Rasterfokus/Zoom und bestätigte Hinweislesepositionen.',17),
          txt(40,632,'Gesten vorher abbrechen. Pflicht-Flush und Recovery-Schreibsperre nicht umgehen. Keine Live-Korrektheitsanzeige.',17),
          txt(40,682,'Präsentationsumschaltung in der Galerie prüft keine dieser nativen Funktionen.',16)]
    return [w,h],m,c


def compact_board():
    """Actual 125% components at 1:1; a labelled board, not a sixth target layout."""
    g=p.read('layout.json')['cases'][-1];mounts,content=main_layers(g)
    m=[p.rect([0,0,1280,720],PAPER,'none')]
    c=[txt(32,40,'720p / UI 125 % · unskalierte Zustands- und Randprobe',25,extra='style="font-family:Fraunces,serif;font-weight:600"'),
       txt(32,70,'Statische Ausschnitte des 1280er Falls und Meldungsbeispiele; kein zusätzlicher Spielscreen.',16)]
    # Cropped local SVG viewports: translation only, exactly one source pixel per pixel.
    for dest,box in [([32,100],[240,602,600,90]),([700,100],[984,604,240,80]),([995,100],[943,19,212,70])]:
        dx,dy=dest;x,y,w,h=box
        prefix=f'<svg x="{dx}" y="{dy}" width="{w}" height="{h}" viewBox="{x} {y} {w} {h}">'
        subset=[]
        for fragment in content:
            node=ET.fromstring(fragment)
            key=node.get('data-action')
            item=next((v for v in g['actions'] if v['id']==key),None)
            if (item and p.inside(item['rect'],box)) or (node.get('data-zone')=='status' and x==984):subset.append(fragment)
        m.append(prefix+''.join(mounts)+'</svg>');c.append(prefix+''.join(subset)+'</svg>')
    c.append(txt(32,224,'Tooltip einer langen Folge · F-02 / Spalte 20 · Originaldaten, 16,25 px',18.75))
    m.append(chamfer([32,245,1216,82],'url(#card)',BRASS,5))
    d=p.read('sources/f02-public-demo.json');colors={v['id']:v['color'] for v in d['palette']}
    for i,t in enumerate(d['columns'][19]):
        ex=f'style="fill:{colors[t["color"]]}" data-clue-example="columns,19,{i}"'
        if t['color'] in (2,4):ex+=' stroke="#293e3d" stroke-width="0.55" paint-order="stroke fill"'
        c.append(txt(56+i*37.5,276,t['length'],16.25,extra=ex))
    c.append(txt(56,310,'Ganze Zahlen bleiben erreichbar; Tooltip ergänzt die Leseposition jeder einzelnen Folge.',18.75))
    for y,title,lines in [(356,'Speicherfehler',['Temporäre Datei nicht schreibbar.','Pflicht-Flush fehlgeschlagen: Der angeforderte Übergang bleibt blockiert.']),
                          (532,'Backup geladen',['Primärstand beschädigt. Vor weiterem Speichern Backup bewusst übernehmen.','Schreibsperre bleibt bis zur bewussten Übernahme aktiv.'])]:
        m.append(chamfer([32,y,1216,148],'url(#card)',BRASS,5));m.append(p.rect([33,y+5,5,138],INK,'none'))
        c.append(txt(56,y+37,title,23.75,extra='font-weight="600"'))
        for i,line in enumerate(lines):c.append(txt(56,y+75+i*34,line,18.75))
    return [1280,720],m,c


def source_svg(size, parts):
    return p.svg(*size,[DEFS]+parts)


def validate_fonts(font_dir):
    records=[]
    for f in p.read('sources/fonts.json'):
        path=font_dir/Path(f['file']).name
        raw=path.read_bytes()
        assert p.sha(raw)==f.get('upstream_sha256',f['sha256']), f['file']
        if path.suffix=='.txt': assert b'SIL OPEN FONT LICENSE' in raw
        records.append(dict(file=path.name,sha256=p.sha(raw),url=f['url']))
    return records


def build(browser_path,font_dir):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    font_records=validate_fonts(font_dir)
    cases=p.read('layout.json')['cases']; records=[]
    write('layout.json',dict(input_commit=BASE,cases=cases,navigation=p.read('layout.json')['navigation']))
    for f in sorted((p.OUT/'sources').iterdir()):
        target=OUT/'inputs'/f.name; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(f.read_bytes())
    write('style.json',dict(fonts={'title':['Fraunces',28,600],'body':['PlexSans',14,400],'miniature':['PlexSans',12,600], 'clues':'unchanged BP-1R: 13 / 14 / 16.25 px'},
          ink=INK,paper=PAPER,brass=BRASS,icon_stroke=1.8,icon_image_px=26,minimum_hit_px=44,
          layer_order=['unchanged BP-2 background','local mounts','precise data/icons/text'],
          selection={'tool':'light underline + dark enamel + explicit status','color':'light corner brackets outside untouched RGB interior + explicit status'},
          paint={'action':'chamfer within original hit; 2 px bevel, 5 px swatch inset','miniature':'original image rect unchanged; mounts inside mini_card reserve','tools':'three shared wells: 3 tools / 2 history / 4 view actions; 3 px outer reserve'},
          c1='proposal only: original 0.55 px dark outline on hint colors 2/4',states=STATES))
    with sync_playwright() as api:
        browser=api.chromium.launch(executable_path=browser_path,headless=True)
        page=browser.new_page(device_scale_factor=1);page.route('**/*',lambda route:route.abort())
        cdp=page.context.new_cdp_session(page);cdp.send('DOM.enable');cdp.send('CSS.enable')
        css=''.join(f'@font-face{{font-family:{n};font-weight:100 900;src:url(data:font/ttf;base64,{base64.b64encode((font_dir/(n+".ttf")).read_bytes()).decode()})}}' for n in ('Fraunces','PlexSans'))
        def render(name,size,parts,measure=False,g=None):
            source=source_svg(size,parts);write('svg/'+name+'.svg',source)
            page.set_viewport_size(dict(zip(('width','height'),size)))
            page.set_content('<meta charset="utf-8"><style>body{margin:0}svg{display:block}'+css+'</style>'+source)
            page.evaluate('Promise.all([document.fonts.load("600 28px Fraunces"),document.fonts.load("14px PlexSans"),document.fonts.load("600 12px PlexSans")])')
            page.evaluate('document.fonts.ready')
            if measure:
                bounds=page.evaluate('''() => [...document.querySelectorAll('text')].map(e=>{let b=e.getBoundingClientRect(),s=getComputedStyle(e);return {text:e.textContent,zone:e.dataset.zone||null,clue:e.hasAttribute('data-clue')||e.hasAttribute('data-clue-example'),box:[b.x,b.y,b.width,b.height],fill:s.fill,family:s.fontFamily,size:s.fontSize,weight:s.fontWeight}})''')
                for item in bounds:
                    assert p.inside(item['box'],[0,0,*size]),(name,item)
                    if g and item['zone']: assert p.inside(item['box'],g['rects'][item['zone']]),(name,item)
                doc=cdp.send('DOM.getDocument')['root']['nodeId']
                ids=cdp.send('DOM.querySelectorAll',{'nodeId':doc,'selector':'text'})['nodeIds']
                assert len(ids)==len(bounds)
                for item,node_id in zip(bounds,ids):
                    fonts=cdp.send('CSS.getPlatformFontsForNode',{'nodeId':node_id})['fonts']
                    item['actual_fonts']=fonts
                    assert fonts and all(f['isCustomFont'] for f in fonts),(name,item)
                records.append(dict(file=name,viewport=size,texts=bounds,fonts=page.evaluate('() => [...document.fonts].map(f=>({family:f.family,status:f.status}))')))
            dest=OUT/'png'/f'{name}.png';dest.parent.mkdir(exist_ok=True)
            page.screenshot(path=str(dest),omit_background=True)
            if measure:
                page.evaluate("document.querySelectorAll('text').forEach(e=>e.remove())")
                page.screenshot(path=str(OUT/'png'/f'{name}-underlay.png'),omit_background=True)
        scenes=[]
        for g in cases:
            m,c=main_layers(g); scenes.append((g['name'],g['viewport'],m,c,g))
        for name,fn in [('states',state_board),('connection',connection_board),('compact-states',compact_board)]:
            size,m,c=fn();scenes.append((name,size,m,c,None))
        for name,size,m,c,g in scenes:
            render(name+'-mounts',size,m)
            render(name+'-content',size,c)
            render(name+'-ui',size,m+c,True,g)
            # Assemble from the independently editable rendered layers. Chromium's
            # direct paint can differ at overlapping antialiased edges; the PNG
            # delivery deliberately uses explicit layer source-over instead.
            mounted=Image.open(OUT/'png'/f'{name}-mounts.png').convert('RGBA')
            content_image=Image.open(OUT/'png'/f'{name}-content.png').convert('RGBA')
            Image.alpha_composite(mounted,content_image).save(OUT/'png'/f'{name}-ui.png')
        write('render-checks.json',dict(renderer=browser.version,python=sys.version.split()[0],platform=sys.platform,device_scale_factor=1,network='blocked',temporary_fonts=font_records,records=records))
        browser.close()
    # PNG composition uses exactly the rendered common UI; no A/B-specific overlay.
    compose(True)
    gallery()


def contrast(bg, record):
    w,h,n,pixels=bg; result=[]
    for item in record['texts']:
        if item['clue']: continue
        rgb=tuple(map(int,re.findall(r'\d+',item['fill'])))
        assert len(rgb)==3
        ink=a.luminance(rgb);x,y,W,H=item['box'];lowest=100
        for yy in range(math.floor(y),math.ceil(y+H)):
            for xx in range(math.floor(x),math.ceil(x+W)):
                pos=(yy*w+xx)*n;lum=a.luminance(tuple(pixels[pos:pos+3]))
                lowest=min(lowest,(max(lum,ink)+.05)/(min(lum,ink)+.05))
        assert lowest>=4.5,(record['file'],item['text'],lowest)
        result.append(dict(text=item['text'],box=item['box'],fill=item['fill'],minimum=round(lowest,4)))
    return result


def compose(build=False):
    checks=a.read(OUT/'render-checks.json'); cases=a.read(OUT/'layout.json')['cases']
    contrasts={};details={}; cache={}
    def decode(path):
        if path not in cache: cache[path]=p.png_pixels(path.read_bytes())
        return cache[path]
    def deliver(name,img):
        if build: a.png_write(OUT/name,img)
        else: assert decode(OUT/name)==img, 'composition/crop mismatch: '+name
    for variant,filename in a.NAMES.items():
        master=decode(a.OUT/filename);backgrounds={}
        for g in cases:
            name=g['name'];W,H=g['viewport']
            if W not in backgrounds: backgrounds[W]=a.resample(master,(W,H))
            bg=backgrounds[W]
            ui=decode(OUT/'png'/f'{name}-ui.png')
            composed=a.montage(bg,ui);deliver(f'views/{variant}-{name}.png',composed)
            underlay=a.montage(bg,decode(OUT/'png'/f'{name}-ui-underlay.png'))
            record=next(v for v in checks['records'] if v['file']==name+'-ui')
            contrasts[variant+'-'+name]=contrast(underlay,record)
            gx,gy=g['rects']['grid'][:2]
            zones={'numbers':[gx-72,gy-76,gx+250,gy+172]}
            if W==1280:
                zones.update(miniature=[1034,180,1208,376],swatches=[1038,414,1185,557],
                             tools=[240,602,840,689],navigation=[943,19,1155,89],album=[0,64,66,132],status=[984,604,1224,684])
            for label,box in zones.items():
                key=f'details/{variant}-{name}-{label}.png';deliver(key,a.crop(composed,box));details[key]=dict(source=f'views/{variant}-{name}.png',box=box,scale=1)
    for name in ('states','connection','compact-states'):
        record=next(v for v in checks['records'] if v['file']==name+'-ui')
        bg=decode(OUT/'png'/f'{name}-ui-underlay.png')
        # Boards have their own fully opaque real substrate.
        assert bg[2]==3 or (bg[2]==4 and min(bg[3][3::4])==255)
        contrasts[name]=contrast(bg,record)
    if build:
        write('contrast.json',contrasts);write('details.json',details)
    else:
        assert a.read(OUT/'contrast.json')==contrasts and a.read(OUT/'details.json')==details
    return contrasts


def gallery():
    cases=a.read(OUT/'layout.json')['cases']
    options=''.join(f'<option value="{g["name"]}">{g["name"].upper()} · {g["viewport"][0]} × {g["viewport"][1]} · UI {round(g["ui_scale"]*100)} %'+(' · UI-Testdatensatz, keine Rätselabnahme' if g['fixture']=='f03' else '')+'</option>' for g in cases)
    links=''.join(f'<li><a href="{name}">{Path(name).stem} · 1:1</a></li>' for name in a.read(OUT/'details.json'))
    write('index.html','''<!doctype html>
<html lang="de"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>BP-3 · Zielkompositionen A/B</title>
<style>body{margin:0;background:#efe7d7;color:#293e3d;font:16px system-ui,sans-serif}header,section{padding:22px 32px}h1{font:600 30px Georgia,serif;margin:0 0 10px}button,select,a{font:inherit}button,select{padding:9px 14px;border:1px solid #736448;background:#fffaf0;color:#293e3d}button[aria-pressed=true]{background:#293e3d;color:#fffaf0}nav{display:flex;gap:12px;align-items:center;flex-wrap:wrap}.stage{overflow:auto;background:#34352e}.stage img{display:block;max-width:100%;height:auto;margin:auto}.stage.native img{max-width:none}a{color:#214e58}details{margin:16px 0}li{margin:6px 0}.compare{display:grid;grid-template-columns:1fr 1fr;gap:12px}.compare img{width:100%;height:auto}small{display:block;margin:10px 0}footer{padding:20px 32px}</style>
<header><h1>Ein Buch. Eine gemeinsame Arbeitsoberfläche.</h1>
<p>BP-3 · B3-01 bis B3-05 · Statischer Entwurf zur Entscheidung. Eigentümerwahl offen.</p>
<nav><label>Größenfall <select id="case">'''+options+'''</select></label>
<button id="a" aria-pressed="true">A · Inventarband</button><button id="b" aria-pressed="false">B · Sammlungskatalog</button>
<button id="size" aria-pressed="false">1:1 anzeigen</button><a id="original" href="views/a-f02-1920.png">Original-PNG öffnen</a></nav>
<small id="caption"></small></header>
<div class="stage" id="stage"><img id="view" src="views/a-f02-1920.png" alt="Zielkomposition A, F-02 1920"></div>
<section><details><summary>A/B nebeneinander · identischer Größenfall</summary><div class="compare"><figure><figcaption>A · Inventarband</figcaption><img id="side-a" src="views/a-f02-1920.png" alt="Kandidat A"></figure><figure><figcaption>B · Sammlungskatalog</figcaption><img id="side-b" src="views/b-f02-1920.png" alt="Kandidat B"></figure></div></details>
<p><a href="png/states-ui.png">Komponenten und Zustände</a> · <a href="png/compact-states-ui.png">720p / UI 125 %: Zustandsprobe</a> · <a href="png/connection-ui.png">Schematischer rechter Anschluss</a> · <a href="DECISION.md">Entscheidungsunterlage</a> · <a href="README.md">Bildindex und Ebenen</a> · <a href="VERIFICATION.md">Prüfbericht</a></p>
<details><summary>Unskalierte Details · Zahlen, Miniatur, Farbe und 720p-Ränder</summary><ul>'''+links+'''</ul></details>
<p>Die Präsentationsumschaltung ist keine native Spielnavigation. F-03 bleibt ein UI-Testdatensatz. Keine endgültige Gestaltungswahl.</p></section>
<script>let variant='a';const byId=id=>document.getElementById(id);function show(){const name=byId('case').value,path='views/'+variant+'-'+name+'.png';byId('view').src=path;byId('view').alt='Zielkomposition '+variant.toUpperCase()+', '+name;byId('original').href=path;for(const v of ['a','b']){byId(v).setAttribute('aria-pressed',v===variant);byId('side-'+v).src='views/'+v+'-'+name+'.png'}byId('caption').textContent=byId('case').selectedOptions[0].text+' · gleicher UI-Layer auf A/B · Originalmaß, kein skalierter Gesamtscreenshot';}for(const v of ['a','b'])byId(v).onclick=()=>{variant=v;show()};byId('case').onchange=show;byId('size').onclick=()=>{const native=byId('stage').classList.toggle('native');byId('size').setAttribute('aria-pressed',native);byId('size').textContent=native?'An Fenster anpassen':'1:1 anzeigen'};show();</script>
</html>
''')


def package_files():
    return sorted(v for v in OUT.rglob('*') if v.is_file() and v.name!='bp3-review.zip')


def input_hashes():
    paths=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'--',
        'docs/design/book_inventory/production','docs/design/book_inventory/artwork',
        'tools/book_inventory/production.py','tools/book_inventory/artwork.py',
        'tools/book_inventory/test_production.py','tools/book_inventory/test_artwork.py'],cwd=ROOT,text=True).splitlines()
    result={}
    for name in paths:
        raw=(ROOT/name).read_bytes()
        old=subprocess.check_output(['git','show',BASE+':'+name],cwd=ROOT)
        assert raw==old,'protected input changed: '+name
        result[name]=p.sha(raw)
    return result


def pack():
    files={v.relative_to(OUT).as_posix():dict(sha256=p.sha(v.read_bytes()),bytes=v.stat().st_size) for v in package_files() if v.name!='manifest.json'}
    write('manifest.json',dict(package='BP-3 / B3-01..B3-05',input_commit=BASE,inputs=input_hashes(),files=files,
          generator_sha256=p.sha(Path(__file__).read_bytes().replace(b'\r\n',b'\n')),
          zip_binding='Immutable commit download URL and ZIP SHA-256 in own PR; no circular self-hash.',
          zip_inputs={f'backgrounds/{n}':p.sha((a.OUT/n).read_bytes()) for n in a.NAMES.values()}))
    with zipfile.ZipFile(OUT/'bp3-review.zip','w',zipfile.ZIP_DEFLATED) as z:
        pairs=[(v.relative_to(OUT).as_posix(),v) for v in package_files()]+[(f'backgrounds/{n}',a.OUT/n) for n in a.NAMES.values()]
        for name,path in pairs:
            info=zipfile.ZipInfo(name,(2026,9,26,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,path.read_bytes())
    print('BP-3 ZIP SHA-256',p.sha((OUT/'bp3-review.zip').read_bytes()))


def verify_data(root,g):
    original=ET.parse(p.OUT/'svg'/f'{g["name"]}-ui.svg').getroot()
    for key in ('grid','clues','miniature'):
        expected=copy.deepcopy(original.find(f'.//s:g[@id="{key}"]',p.NS))
        if key=='miniature': expected.remove(expected[0]);expected.remove(expected[0])
        actual=root.find(f'.//s:g[@id="{key}"]',p.NS)
        assert actual is not None and serialize(actual)==serialize(expected),(g['name'],key,'original data/geometry changed')
    assert root.find('.//s:g[@id="study-labels"]',p.NS) is None


def verify_actions(root,g):
    nodes=root.findall('.//s:g[@data-action]',p.NS)
    assert len(nodes)==len(g['actions']) and {n.get('data-action') for n in nodes}=={v['id'] for v in g['actions']}
    for item in g['actions']:
        node=next(n for n in nodes if n.get('data-action')==item['id'])
        hit=node.find('s:rect[@data-hit="true"]',p.NS)
        assert [float(hit.get(k)) for k in ('x','y','width','height')]==item['rect']
        assert min(item['rect'][2:])>=44*g['ui_scale']
        assert node.find('s:title',p.NS) is not None
        if item['id'] in p.NAV: assert node.get('data-target')==p.NAV[item['id']][2]
        if not item['id'].startswith('color-'):
            icon=node.find('s:g',p.NS);ix,iy=item['image_rect'][:2]
            assert icon.get('transform')==f'translate({ix} {iy}) scale({g["ui_scale"]})'
            path=p.NAV[item['id']][3] if item['id'] in p.NAV else p.read('sources/icons.json')[item['id']][2]
            assert icon.find('s:path',p.NS).get('d')==path


def verify_states():
    root=ET.parse(OUT/'svg/states-content.svg').getroot()
    expected={(key,state) for key in ('fill','erase','hand','color-2','undo','redo',*p.NAV)
              for state in STATES if not (state=='active' and key in ('undo','redo'))
              and not (state=='disabled' and key in ('fill','erase','hand','color-2'))}
    nodes=root.findall('.//s:g[@data-action]',p.NS)
    assert len(nodes)==len(expected) and {(n.get('data-action'),n.get('data-state')) for n in nodes}==expected
    for node in nodes:
        if node.get('data-action') in p.NAV:assert node.get('data-target')==p.NAV[node.get('data-action')][2]
    d=p.read('sources/f02-public-demo.json');colors={v['id']:v['color'] for v in d['palette']}
    for name in ('states','compact-states'):
        board=ET.parse(OUT/'svg'/f'{name}-content.svg').getroot()
        sequence=board.findall('.//s:text[@data-clue-example]',p.NS)
        assert len(sequence)==len(d['columns'][19])+(name=='states')
        for node in sequence:
            axis,line,index=node.get('data-clue-example').split(',');token=d[axis][int(line)][int(index)]
            assert node.text==str(token['length']) and node.get('style')=='fill:'+colors[token['color']]


def verify_links():
    source=(OUT/'index.html').read_text(encoding='utf-8')
    for link in re.findall(r'(?:src|href)="([^"]+)"',source):
        assert not re.match(r'\w+:|//',link) and (OUT/link).is_file(),link
    assert 'fetch(' not in source and '@font-face' not in source
    for g in a.read(OUT/'layout.json')['cases']:
        for v in 'ab': assert (OUT/'views'/f'{v}-{g["name"]}.png').is_file()


def gallery_check(browser_path):
    """Exercise the file:// gallery from an extracted review ZIP, with no network."""
    from playwright.sync_api import sync_playwright
    results=[];errors=[];external=[]
    with tempfile.TemporaryDirectory(prefix='picross-bp3-gallery-') as temp:
        folder=Path(temp)
        with zipfile.ZipFile(OUT/'bp3-review.zip') as z:
            assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist())
            z.extractall(folder)
        with sync_playwright() as api:
            browser=api.chromium.launch(executable_path=browser_path,headless=True)
            page=browser.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
            page.on('pageerror',lambda e:errors.append(str(e)))
            def intercept(route):
                if route.request.url.startswith('file:'):route.continue_()
                else:external.append(route.request.url);route.abort()
            page.route('**/*',intercept)
            page.goto((folder/'index.html').as_uri())
            for g in a.read(OUT/'layout.json')['cases']:
                page.select_option('#case',g['name'])
                for variant in 'ab':
                    page.click('#'+variant)
                    page.locator('#view').evaluate('(e)=>e.decode()')
                    actual=page.locator('#view').evaluate('(e)=>[e.naturalWidth,e.naturalHeight]')
                    assert actual==g['viewport']
                    assert page.locator('#original').get_attribute('href')==f'views/{variant}-{g["name"]}.png'
                    results.append(dict(case=g['name'],variant=variant,natural_size=actual))
            page.click('#size')
            assert page.locator('#view').evaluate('(e)=>e.getBoundingClientRect().width')==1280
            page.click('#size');page.locator('summary').first.click()
            for selector in ('#side-a','#side-b'):page.locator(selector).evaluate('(e)=>e.decode()')
            page.select_option('#case','f02-1920');page.click('#a')
            page.locator('#view').evaluate('(e)=>e.decode()')
            dest=OUT/'checks';dest.mkdir(exist_ok=True)
            page.screenshot(path=str(dest/'gallery.png'))
            assert not errors and not external,(errors,external)
            write('gallery-checks.json',dict(renderer=browser.version,source='extracted bp3-review.zip, file protocol',
                  index_sha256=p.sha((OUT/'index.html').read_bytes()),cases=results,external_requests=external,javascript_errors=errors,
                  native_size_toggle=True,side_by_side=True))
            browser.close()


def verify_layer_pixels(mounts,content,combined):
    """Check independent rendered layers against the assembled UI raster.

    Intermediate straight-alpha quantization may round a channel by one.
    Compare over both black and white to cover RGB and alpha errors.
    """
    W,H,N=combined[:3]
    assert mounts[:3]==content[:3]==combined[:3]==(W,H,4)
    for base in (0,255):
        for pos in range(W*H):
            i=pos*4;ma=mounts[3][i+3];ca=content[3][i+3];ua=combined[3][i+3]
            if not (ma or ca or ua):continue
            for channel in range(3):
                back=(mounts[3][i+channel]*ma+base*(255-ma)+127)//255
                expected=(content[3][i+channel]*ca+back*(255-ca)+127)//255
                actual=(combined[3][i+channel]*ua+base*(255-ua)+127)//255
                assert abs(expected-actual)<=1,('layer montage differs',pos,channel,expected,actual)


def verify():
    manifest=a.read(OUT/'manifest.json')
    assert manifest['input_commit']==BASE and manifest['inputs']==input_hashes()
    assert manifest['generator_sha256']==p.sha(Path(__file__).read_bytes().replace(b'\r\n',b'\n'))
    assert manifest['files']=={v.relative_to(OUT).as_posix():dict(sha256=p.sha(v.read_bytes()),bytes=v.stat().st_size) for v in package_files() if v.name!='manifest.json'}
    for path in package_files():
        assert path.suffix.lower() not in ('.ttf','.otf','.woff','.woff2')
        if path.suffix in ('.svg','.html'): assert b'base64' not in path.read_bytes() and b'@font-face' not in path.read_bytes()
    cases=a.read(OUT/'layout.json')['cases'];assert cases==p.read('layout.json')['cases']
    for path in (OUT/'inputs').iterdir():assert path.read_bytes()==(p.OUT/'sources'/path.name).read_bytes()
    for g in cases:
        p.verify_geometry(g)
        content=ET.parse(OUT/'svg'/f'{g["name"]}-content.svg').getroot()
        verify_data(content,g);verify_actions(content,g)
        mounts=p.png_pixels((OUT/'png'/f'{g["name"]}-mounts.png').read_bytes())
        pixels=p.png_pixels((OUT/'png'/f'{g["name"]}-content.png').read_bytes())
        ui=p.png_pixels((OUT/'png'/f'{g["name"]}-ui.png').read_bytes())
        assert mounts[:3]==ui[:3]==(*g['viewport'],4)
        verify_layer_pixels(mounts,pixels,ui)
        assert min(ui[3][3::4])==0 and max(ui[3][3::4])==255
        # Material may not enter any grid, hint, coordinate or status rectangle.
        for key in ('grid','row_hints','column_hints','coordinates','status'):
            x,y,w,h=g['rects'][key]
            for yy in range(math.ceil(y),math.floor(y+h)):
                start=(yy*mounts[0]+math.ceil(x))*4+3;stop=(yy*mounts[0]+math.floor(x+w))*4
                assert not any(mounts[3][start:stop:4]),(g['name'],key,'mount overlap')
        d=p.read('sources/'+g['fixture']+'-public-demo.json');colors={v['id']:bytes.fromhex(v['color'][1:]) for v in d['palette']}
        gx,gy=g['rects']['grid'][:2];ox,oy=g['origin_zero_based'];cell=g['cell_px'];W=ui[0]
        for row in range(g['visible_cells'][1]):
            for col in range(g['visible_cells'][0]):
                value=d['cells'][(oy+row)*d['width']+ox+col]
                pos=(int(gy+(row+.5)*cell)*W+int(gx+(col+.5)*cell))*4
                if value>0: assert ui[3][pos:pos+4]==colors[value]+b'\xff'
                elif value==-1: assert ui[3][pos+3]==0
        for item in g['actions']:
            if item['id'].startswith('color-'):
                x,y,w,h=item['rect'];pos=(int(y+h/2)*W+int(x+w/2))*4
                assert ui[3][pos:pos+4]==colors[int(item['id'].split('-')[1])]+b'\xff'
                margin=5*g['ui_scale']
                for yy in range(math.ceil(y+margin),math.floor(y+h-margin)):
                    for xx in range(math.ceil(x+margin),math.floor(x+w-margin)):
                        pos=(yy*W+xx)*4
                        assert ui[3][pos:pos+4]==colors[int(item['id'].split('-')[1])]+b'\xff'
    records=a.read(OUT/'render-checks.json')['records'];assert len(records)==8
    for record in records:
        assert {f['family'] for f in record['fonts']}=={'Fraunces','PlexSans'} and all(f['status']=='loaded' for f in record['fonts'])
        for item in record['texts']:
            assert p.inside(item['box'],[0,0,*record['viewport']])
            assert item['family'].split(',')[0] in ('PlexSans','Fraunces')
            assert item['actual_fonts'] and all(f['isCustomFont'] for f in item['actual_fonts'])
            families={f['familyName'] for f in item['actual_fonts']}
            assert all(('Fraunces' in family if item['family'].startswith('Fraunces') else 'Plex Sans' in family) for family in families)
    # Fully decode every PNG, not merely its header or checksum.
    for path in (v for v in package_files() if v.suffix=='.png'): p.png_pixels(path.read_bytes())
    compose();verify_links();verify_states()
    gallery_record=a.read(OUT/'gallery-checks.json')
    assert gallery_record['index_sha256']==p.sha((OUT/'index.html').read_bytes())
    assert not gallery_record['external_requests'] and not gallery_record['javascript_errors']
    assert gallery_record['cases']==[dict(case=g['name'],variant=v,natural_size=g['viewport']) for g in cases for v in 'ab']
    expected={v.relative_to(OUT).as_posix():v.read_bytes() for v in package_files()}
    expected.update({f'backgrounds/{n}':(a.OUT/n).read_bytes() for n in a.NAMES.values()})
    with zipfile.ZipFile(OUT/'bp3-review.zip') as z:
        assert len(z.namelist())==len(expected) and set(z.namelist())==set(expected)
        for name,raw in expected.items(): assert z.read(name)==raw,name
    print('BP-3: unchanged inputs, original data/geometry, common A/B UI, real pixels/contrast, layers, local links and complete ZIP OK')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['build','pack','verify','gallery-check'])
    parser.add_argument('--browser');parser.add_argument('--fonts',type=Path);args=parser.parse_args()
    if args.command=='build': build(args.browser,args.fonts)
    elif args.command=='pack': pack()
    elif args.command=='gallery-check': gallery_check(args.browser)
    else: verify()
