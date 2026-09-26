"""BP-1R static templates; no game, solver or background illustration.

Build uses optional Pillow/Playwright and temporary fonts; verify is stdlib only.
"""
import argparse
import base64
import hashlib
import html
import json
import math
from pathlib import Path
import struct
import subprocess
import zipfile
import zlib
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/design/book_inventory/production'
BASE = '0d3ad6a921578f94b3249ab83fbb215721549dfb'
REVISION = 'BP-1R'
REF = '9834ee834f5b83bbc5e6b17429a8fe7185c26758'
DEMO = 'df7ac589e900a6d6d7c5080599c6a5ace47c395d'
INK, PAPER = '#293e3d', '#fffaf0'
NS = {'s': 'http://www.w3.org/2000/svg'}
QUIET = ('grid', 'row_hints', 'column_hints', 'title', 'mini_card',
         'coordinates', 'palette', 'status', 'tools', 'auxiliary', 'register', 'page_navigation')
NAV = {
    'nav-album': ('Album', 'Album öffnen · Sammlung und Blattauswahl', 'album', 'M3 4 h8 v18 H3 Z M11 4 h10 v18 H11 M6 8 h2 M14 8 h4'),
    'nav-information': ('Information', 'Informationsseite öffnen · Einstellungen und Hilfe', 'information', 'M4 12 h16 m-7 -7 l7 7 -7 7'),
    'nav-work': ('Zum Rätsel', 'Zur Arbeitsseite zurück · Arbeitsstand erhalten', 'work', 'M20 12 H4 m7 -7 l-7 7 7 7'),
}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def read(name):
    return json.loads((OUT / name).read_text(encoding='utf-8'))


def write(name, value):
    p = OUT / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')


def rect(r, fill='none', stroke=INK, extra=''):
    x, y, w, h = r
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" {extra}/>'


def mask_rect(r):
    x,y,w,h=r
    return rect([math.floor(x),math.floor(y),math.ceil(x+w)-math.floor(x),math.ceil(y+h)-math.floor(y)],'#fff','none','shape-rendering="crispEdges"')


def text(x, y, label, size=14, extra=''):
    return f'<text x="{x}" y="{y}" font-family="PlexSans, sans-serif" font-size="{size}" fill="{INK}" {extra}>{html.escape(str(label))}</text>'


def path(d, color=INK, width=1.4, extra=''):
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" {extra}/>'


def svg(w, h, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'+''.join(body)+'\n</svg>\n'


def layouts():
    specs = [
        ('f02-1920', 'f02', 1920, 1080, 1, [510,252,720,720],18,[0,0],[210,126],[1410,220,180,180]),
        ('f02-2560', 'f02', 2560, 1440, 1, [830,432,720,720],18,[0,0],[210,126],[1730,400,180,180]),
        ('f01-2560', 'f01', 2560, 1440, 1, [970,470,480,480],24,[0,0],[192,144],[1630,470,200,200]),
        ('f03-1920', 'f03', 1920, 1080, 1, [310,270,1368,672],24,[25,35],[240,144],[1700,290,132,132]),
        ('f02-1280', 'f02', 1280, 720, 1.25, [300,222,638,374],22,[0,0],[210,120],[1050,220,140,140]),
    ]
    result = []
    for name, key, w, h, ui, grid, cell, origin, hints, mini in specs:
        x,y,gw,gh = grid; hw,hh = hints; mx,my,mw,mh = mini
        scale = w/2560
        groups = {'grid':grid, 'row_hints':[x-hw,y,hw,gh], 'column_hints':[x,y-hh,gw,hh],
                  'miniature':mini, 'mini_card':[mx-10,my-34,mw+20,mh+44],
                  'coordinates':[mx-10,my+mh+16, max(mw+20,150),28],
                  'palette':[mx-6,my+mh+58,110*ui,110*ui],
                  'status':[mx-10,my+mh+190*ui,max(mw+20,170*ui),62*ui],
                  'title':[110*scale,56*scale,640*scale,40],
                  'book':[40*scale,34*scale,2480*scale,1372*scale],
                  'sheet':[80*scale,48*scale,2380*scale,1340*scale],
                  'fold':[2480*scale,40*scale,16*scale,1360*scale],
                  'right_page_slice':[2496*scale,48*scale,64*scale,1340*scale]}
        # Short, coherent tool strip; auxiliary actions separately at the top edge.
        bx = 250 if w==1280 else (400 if key=='f03' else x-hw)
        by = h-106 if w==1280 else (h-102 if w==1920 else 1210)
        groups['tools'] = [bx-8,by-8,9*52*ui+8,68*ui]
        groups['auxiliary'] = [w-270*ui,48*scale,112*ui,54*ui]
        groups['register'] = [8*scale,140*scale,44*ui,44*ui]
        groups['page_navigation'] = [w-150*ui,48*scale,44*ui,44*ui]
        if key=='f03':
            groups['status'] = [1688,650,150,78]
        if w==1280:
            groups['status'] = [990,610,230,65]
            groups['coordinates'] = [1010,382,210,32]
        actions = []
        for i,k in enumerate(['fill','erase','hand','undo','redo','minus','plus','fit','work']):
            actions.append({'id':k,'rect':[bx+i*52*ui,by,44*ui,44*ui],'group':'tools'})
        for i,k in enumerate(['help','menu']):
            actions.append({'id':k,'rect':[w-264*ui+i*58*ui,54*scale,44*ui,44*ui],'group':'auxiliary'})
        for i in range(1 if key=='f01' else 4):
            actions.append({'id':f'color-{i+1}','rect':[mx+(i%2)*54*ui,my+mh+64+(i//2)*54*ui,44*ui,44*ui],'group':'palette'})
        for action_id, group in [('nav-album','register'),('nav-information','page_navigation')]:
            actions.append(navigation_action(action_id, groups[group], group, ui))
        for action in actions:
            ax,ay,aw,ah=action['rect']
            action.setdefault('image_rect',[ax+9*ui,ay+9*ui,26*ui,26*ui])
            action['normalized']=[round(v/(w if i%2==0 else h),8) for i,v in enumerate(action['rect'])]
            action['image_normalized']=[round(v/(w if i%2==0 else h),8) for i,v in enumerate(action['image_rect'])]
        normalized = {k:[round(v/(w if i%2==0 else h),8) for i,v in enumerate(r)] for k,r in groups.items()}
        result.append(dict(name=name, revision=REVISION, fixture=key, viewport=[w,h], ui_scale=ui, cell_px=cell,
                           origin_zero_based=origin, visible_cells=[gw//cell,gh//cell],
                           slots_px=[30*ui,18*ui], rects=groups, normalized=normalized, actions=actions,
                           background=dict(source_px=[2560,1440],uniform_scale=scale,crop_px=[0,0,2560,1440],offset_px=[0,0],inverse='master_rect = screen_rect / uniform_scale'),
                           decorative_edges=[[0,0,w,8*scale],[0,h-8*scale,w,8*scale],[0,8*scale,8*scale,h-16*scale],[w-8*scale,8*scale,8*scale,h-16*scale]]))
    return result


def navigation_action(key, bounds, group, ui=1, state='normal'):
    x,y,_,_=bounds
    label,tooltip,target,_=NAV[key]
    return dict(id=key,rect=list(bounds),image_rect=[x+9*ui,y+9*ui,26*ui,26*ui],
                group=group,label=label,tooltip=tooltip,target=target,state=state)


def navigation_svg(a, ui=1):
    key=a['id']; state=a['state']; ax,ay,_,_=a['image_rect']
    fill={'normal':PAPER,'hover':'#d8e5df','active':INK}[state]
    color=PAPER if state=='active' else INK
    return (f'<g data-action="{key}" data-target="{a["target"]}" data-state="{state}">'
            +rect(a['rect'],fill,INK)
            +f'<g transform="translate({ax} {ay}) scale({ui})">'+path(NAV[key][3],color,1.8)+'</g>'
            +f'<title>{html.escape(a["tooltip"])}</title></g>')


def ui_svg(g, d, icons):
    w,h=g['viewport']; ui=g['ui_scale']; r=g['rects']; x,y,gw,gh=r['grid']
    c=g['cell_px']; ox,oy=g['origin_zero_based']; cols,rows=g['visible_cells']
    colors={p['id']:p['color'] for p in d['palette']}; body=[]
    body.append('<g id="precise-ui">')
    tx,ty,_,_=r['title']
    body.append(text(tx,ty+28,f'Sammlung / {d["id"]}',28,'style="font-family:Fraunces,serif;font-weight:600" data-zone="title"'))
    body.append(f'<g id="grid" data-state="{sha(json.dumps(d["cells"]).encode())}">')
    for row in range(rows):
        for col in range(cols):
            v=d['cells'][(oy+row)*d['width']+ox+col]; xx=x+col*c; yy=y+row*c
            tag=f'data-cell="{ox+col},{oy+row},{v}"'
            if v>0: body.append(rect([xx+2.5,yy+2.5,c-5,c-5],colors[v],'none',tag))
            elif v==0: body.append(path(f'M{xx+5} {yy+5} l{c-10} {c-10} m0 -{c-10} l-{c-10} {c-10}',extra=tag))
    for n in range(cols+1): body.append(path(f'M{x+n*c} {y} v{gh}',INK if (ox+n)%5==0 else '#9baca4',1.5 if (ox+n)%5==0 else .65))
    for n in range(rows+1): body.append(path(f'M{x} {y+n*c} h{gw}',INK if (oy+n)%5==0 else '#9baca4',1.5 if (oy+n)%5==0 else .65))
    body.append('</g><g id="clues">')
    fs=(13 if c<=22 else 14)*ui; sx,sy=g['slots_px']
    for axis,count,start,capacity in [('rows',rows,oy,int((r['row_hints'][2]-8)/sx)),('columns',cols,ox,int((r['column_hints'][3]-8)/sy))]:
        for line in range(start,start+count):
            seq=d[axis][line]; items=list(enumerate(seq))
            if len(items)>capacity: items=[(-1,None)]+items[-(capacity-1):]
            if not items: items=[(-2,None)]
            for n,(idx,t) in enumerate(items):
                back=len(items)-n-.5
                xx=x-back*sx if axis=='rows' else x+(line-start+.5)*c
                yy=y+(line-start+.5)*c if axis=='rows' else y-back*sy
                label=t['length'] if t else ('…' if idx==-1 else '–'); color=colors[t['color']] if t else INK
                extra=f'text-anchor="middle" style="fill:{color}" data-zone="{ "row_hints" if axis=="rows" else "column_hints"}" data-clue="{axis},{line},{idx}"'
                if t and t['color'] in (2,4): extra+=' stroke="#293e3d" stroke-width="0.55" paint-order="stroke fill"'
                body.append(text(xx,yy+fs*(.38 if ui>1 else .32),label,fs,extra))
                if d['id']=='F-02' and axis=='rows' and line==1 and idx==0:
                    body.append(path(f'M{xx-8} {yy} h16',color,1))
    body.append('</g>')
    mx,my,mw,mh=r['miniature']; unit=mw/d['width']
    body.append(f'<g id="miniature" data-state="{sha(json.dumps(d["cells"]).encode())}">')
    body.append(rect(r['mini_card'],PAPER,INK)); body.append(text(mx,my-12,'DEIN STAND',12*ui))
    body.append(rect(r['miniature'],'none',INK))
    for row in range(d['height']):
        for col in range(d['width']):
            v=d['cells'][row*d['width']+col]; xx=mx+col*unit; yy=my+row*unit
            tag=f'data-cell="{col},{row},{v}"'
            if v>0: body.append(rect([xx,yy,unit,unit],colors[v],'none',tag))
            elif v==0: body.append(path(f'M{xx+unit*.2} {yy+unit*.2} l{unit*.6} {unit*.6} m0 -{unit*.6} l-{unit*.6} {unit*.6}',width=max(.4,unit*.15),extra=tag))
    view=[mx+ox*unit,my+oy*unit,cols*unit,rows*unit]
    body.extend([rect(view,'none',PAPER,'stroke-width="3"'),rect(view),'</g>'])
    cx,cy,_,_=r['coordinates']; body.append(text(cx+6,cy+21*ui,'Zeile –  Spalte –',13*ui,'data-zone="coordinates"'))
    for a in g['actions']:
        ax,ay,aw,ah=a['rect']; key=a['id']; active=key in ('fill','color-1')
        if key in NAV:
            body.append(navigation_svg(a,ui))
            continue
        body.append(f'<g data-action="{key}">')
        if key.startswith('color-'):
            p=colors[int(key[-1])]; title='Farbe wählen · aktiviert Füllen'
            body.append(rect(a['rect'],p,INK))
            if active:
                body.append(rect([ax-3,ay-3,aw+6,ah+6],'none',INK,'stroke-width="2"'))
                body.append(f'<circle cx="{ax+aw/2}" cy="{ay+ah/2}" r="{4*ui}" fill="{PAPER}"/>')
        else:
            title=icons[key][1]; body.append(rect(a['rect'],INK if active else PAPER,INK))
            body.append(f'<g transform="translate({ax+9*ui} {ay+9*ui}) scale({ui})">'+path(icons[key][2],PAPER if active else INK,1.8)+'</g>')
            if active: body.append(f'<path d="M{ax+16*ui} {ay+49*ui} h{12*ui} l{-6*ui} {5*ui} Z" fill="{INK}"/>')
        body.append(f'<title>{html.escape(title)}</title></g>')
    sx,sy,_,_=r['status']
    for i,label in enumerate([f'Raster {c} px · UI {round(ui*100)} %','Füllen · Farbe 1']):
        body.append(text(sx+6,sy+(20+i*24)*ui,label,12*ui,'data-zone="status"'))
    body.append('<g id="study-labels">')
    caption='BP-1R / TECHNISCHE VORLAGE · KEINE HINTERGRUNDKUNST'
    body.append(text(30,h-4,caption,12))
    if d['id']=='F-03':
        body.append(text(1200,64,'UI-Testdatensatz – Rätselqualität nicht abgenommen',14))
        body.append(text(1200,87,'Ausschnitt: Spalten 26–82 / Zeilen 36–63 · 57 × 28 Zellen',14))
    elif w==1280:
        body.append(text(90,94,'Ausschnitt: Spalten 1–29 / Zeilen 1–17',14))
    body.append('</g></g>')
    return body


def navigation():
    return dict(revision=REVISION, views=['work','information','album'],
                contract=dict(fixed_views=True,camera_pan=False,cell_action=False,
                              preserve=['cells','undo_redo','color','tool','grid_focus','grid_zoom','clue_reads'],
                              transition='Abort uncommitted gestures; preserve confirmed state; never bypass required flush or recovery lock.'),
                information=dict(viewport=[1920,1080],
                    rects={'sheet':[90,36,1770,1005], 'fold':[60,30,12,1020],
                           'title':[180,90,1450,70], 'return':[130,98,44,44],
                           'settings':[180,230,710,370], 'help':[970,230,710,370],
                           'statistics':[180,680,1500,190]},
                    actions=[navigation_action('nav-work',[130,98,44,44],'return')]))


def information_svg(info):
    r=info['rects']; body=[navigation_svg(info['actions'][0])]
    body.append(text(200,136,'Information',28,'data-zone="title" style="font-family:Fraunces,serif"'))
    sections={
        'settings':['Einstellungen · Anschluss an vorhandene Optionen',
                    'UI-Skalierung: 100 % / 125 %', 'Hinweise rasterseitig ausrichten',
                    'Erfüllte Hinweise markieren · sitzungsweit', 'Beenden · bestehende Speichergrenzen gelten'],
        'help':['Hilfe · bestehende Bedienung', 'Füllen / Radieren / Hand · links und rechts',
                'Hinweise: ganze Zahlen je Zeile oder Spalte ziehen',
                'Miniatur und Zoom bleiben auf der Arbeitsseite', 'Escape: laufende Geste abbrechen'],
        'statistics':['Statistik · später / Umfang offen',
                      'Keine Spielerdaten in dieser Anschlussvorlage.',
                      'Keine Live-Fehlerzahl oder Korrektheitsanzeige.']}
    for key,lines in sections.items():
        x,y,ww,hh=r[key]; body.append(rect(r[key],'none','#8a9c95'))
        for i,line in enumerate(lines):
            body.append(text(x+24,y+44+i*48,line,22 if i==0 else 20,f'data-zone="{key}"'))
    body.append(text(30,1068,'BP-1R / SCHEMATISCHER RECHTER ANSCHLUSS · KEINE FUNKTIONSIMPLEMENTIERUNG',12))
    return body


def navigation_board():
    body=[rect([0,0,1920,1080],PAPER,'none'), text(60,65,'BP-1R · Navigation und getrennte UI-Zustände',28)]
    for x,title,lines in [(60,'Album / Sammlung',['Neutrale Blattauswahl','Kapitelumfang offen']),
                          (670,'Arbeitsseite',['Eigene Miniatur, Farbe, Werkzeuge','Hinweise, Undo/Redo, Zoom']),
                          (1280,'Informationsseite',['Einstellungen und Hilfe','Statistik: später / offen'])]:
        body.append(rect([x,130,520,180],'none','#8a9c95'))
        body.append(text(x+24,176,title,26))
        for i,line in enumerate(lines): body.append(text(x+24,220+i*34,line,20))
    body.extend([text(585,222,'↔',32),text(1195,222,'↔',32),
                 text(60,366,'Albumzugang links · Seitenwechsel rechts · feste Ansichten, kein Kamerapan',24),
                 text(60,410,'Rückkehr erhält Zellen, Undo/Redo, Farbe/Werkzeug, Ausschnitt/Zoom und Hinweislesepositionen.',20),
                 text(60,448,'Laufende Gesten abbrechen; Pflicht-Flush und Recovery-Sperren bleiben verbindlich.',20)])
    states=['normal','hover','active']
    for row,key in enumerate(NAV):
        y=510+row*130
        body.append(text(60,y+30,NAV[key][0],24))
        body.append(text(60,y+63,key+' → '+NAV[key][2],17))
        for col,state in enumerate(states):
            x=570+col*390
            body.append(navigation_svg(navigation_action(key,[x,y,44,44],'example',state=state)))
            body.append(text(x+60,y+28,{'normal':'Normal','hover':'Hover','active':'Aktiv / Zielansicht'}[state],20))
        body.append(text(570,y+80,NAV[key][1],18))
    body.append(text(60,988,'Trefferfläche 44 × 44 px (125 %: 55 × 55); Iconbild 26 × 26 px (32,5 × 32,5).',20))
    body.append(text(60,1030,'Statische Zustandsbeispiele, keine funktionierende Navigation. Albumrückweg: nav-work.',20))
    return body


def build(browser_path, font_dir):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    cases=layouts(); icons=read('sources/icons.json')
    master_quiet=[]; files=[]; bounds=[]
    nav=navigation()
    for view in [nav['information']]:
        w,h=view['viewport']
        view['normalized']={k:[round(v/(w if i%2==0 else h),8) for i,v in enumerate(r)] for k,r in view['rects'].items()}
    write('layout.json',dict(schema=2,revision=REVISION,base=BASE,reference=REF,demo_reference=DEMO,demo_revision='z1-demo-1',cases=cases,navigation=nav))
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=browser_path,headless=True)
        page=browser.new_page(device_scale_factor=1)
        page.route('**/*',lambda route: route.abort())
        font_css=''.join(f'@font-face{{font-family:{name};src:url(data:font/ttf;base64,{base64.b64encode((font_dir/(name+".ttf")).read_bytes()).decode()})}}' for name in ('Fraunces','PlexSans'))
        for f in read('sources/fonts.json'):
            if f['file'] in ('fonts/Fraunces.ttf','fonts/PlexSans.ttf'):
                assert sha((font_dir/Path(f['file']).name).read_bytes())==f['sha256']
        def render(name,w,h,body,transparent=False,g=None):
            source=svg(w,h,body); write('svg/'+name+'.svg',source)
            page.set_viewport_size({'width':w,'height':h})
            page.set_content('<meta charset="utf-8"><style>body{margin:0}svg{display:block}'+font_css+'</style>'+source)
            page.evaluate('Promise.all([document.fonts.load("14px PlexSans"),document.fonts.load("28px Fraunces")])')
            page.evaluate('document.fonts.ready')
            boxes=page.evaluate('''() => [...document.querySelectorAll('text')].map(e=>{let r=e.getBoundingClientRect();return {text:e.textContent,zone:e.dataset.zone,box:[r.x,r.y,r.width,r.height]}})''')
            for item in boxes:
                assert inside(item['box'],[0,0,w,h]),(name,item)
                if g and item.get('zone'): assert inside(item['box'],g['rects'][item['zone']]),(name,item)
            bounds.append(dict(file=name,measured_texts=len(boxes),text_bounds=boxes,overflow=0,fonts=page.evaluate('() => [...document.fonts].map(f=>({family:f.family,status:f.status}))')))
            dest=OUT/'png'/f'{name}.png'; dest.parent.mkdir(exist_ok=True)
            page.screenshot(path=str(dest),omit_background=transparent)
            if transparent: assert Image.open(dest).getchannel('A').getextrema()==(0,255)
            files.extend([f'svg/{name}.svg',f'png/{name}.png'])
        for g in cases:
            w,h=g['viewport']; r=g['rects']; scale=w/2560; d=read('sources/'+g['fixture']+'-public-demo.json')
            ui=ui_svg(g,d,icons)
            # Deliberately neutral engineering contours, never background artwork.
            wire=[rect([0,0,w,h],'#e8edf1','none'),rect(r['book'],'#d8e0e5','#536d81'),rect(r['sheet'],PAPER,'#536d81'),rect(r['fold'],'#aec1ce','none'),rect(r['right_page_slice'],PAPER,'#536d81')]
            render(g['name']+'-layout',w,h,wire+ui,g=g)
            render(g['name']+'-ui',w,h,ui,True,g)
            quiet=[rect([0,0,w,h],'#000','none')]
            for key in QUIET:
                zone=r[key]; quiet.append(mask_rect(zone))
                master_quiet.append([v/scale for v in zone])
            render(g['name']+'-keepout',w,h,quiet)
            crop=[rect([0,0,w,h],'#000','none'),mask_rect([8*scale,8*scale,w-16*scale,h-16*scale])]
            render(g['name']+'-crop',w,h,crop)
        render('master-keepout',2560,1440,[rect([0,0,2560,1440],'#000','none')]+[mask_rect(r) for r in master_quiet])
        render('master-crop',2560,1440,[rect([0,0,2560,1440],'#000','none'),mask_rect([8,8,2544,1424])])
        info=nav['information']; r=info['rects']; content=information_svg(info)
        render('information-1920-layout',1920,1080,[rect([0,0,1920,1080],'#e8edf1','none'),rect(r['sheet'],PAPER,'#536d81'),rect(r['fold'],'#aec1ce','none')]+content,g=info)
        render('information-1920-ui',1920,1080,content,True,info)
        render('information-1920-keepout',1920,1080,[rect([0,0,1920,1080],'#000','none')]+[mask_rect(r[k]) for k in ('title','return','settings','help','statistics')])
        render('information-1920-crop',1920,1080,[rect([0,0,1920,1080],'#000','none'),mask_rect([6,6,1908,1068])])
        render('navigation',1920,1080,navigation_board())
        write('render-checks.json',dict(revision=REVISION,renderer=browser.version,device_scale_factor=1,fonts_embedded_in_delivery=False,network='blocked',records=bounds))
        browser.close()
    files += ['layout.json','render-checks.json'] + ['sources/'+p.name for p in sorted((OUT/'sources').iterdir())]
    reference_hashes={}
    for key in ('f01','f02','f03'):
        source=subprocess.check_output(['git','show',f'{REF}:docs/design/z1_1/sources/{key}-public-demo.json'],cwd=ROOT)
        assert source==(OUT/'sources'/f'{key}-public-demo.json').read_bytes()
        reference_hashes[key]=sha(source)
    write('manifest.json',dict(schema=2,revision=REVISION,base=BASE,reference=REF,demo_reference=DEMO,generator_sha256=sha(Path(__file__).read_bytes().replace(b'\r\n',b'\n')),reference_data_sha256=reference_hashes,files={n:sha((OUT/n).read_bytes()) for n in files}))


def inside(a,b):
    x,y,w,h=a; X,Y,W,H=b
    return x>=X-.01 and y>=Y-.01 and x+w<=X+W+.01 and y+h<=Y+H+.01


def overlaps(a,b):
    x,y,w,h=a; X,Y,W,H=b
    return x<X+W and X<x+w and y<Y+H and Y<y+h


def png_pixels(b):
    """Decode delivered 8-bit RGB(A) PNGs, including PNG filter reversal, stdlib only."""
    assert b[:8]==b'\x89PNG\r\n\x1a\n'
    w,h,depth,mode=struct.unpack('>IIBB',b[16:26]); assert depth==8 and mode in (2,6)
    assert b[26:29]==b'\0\0\0'  # compression, filter and non-interlaced
    channels=3 if mode==2 else 4; stride=w*channels; pos=8; chunks=[]
    while pos<len(b):
        n=struct.unpack('>I',b[pos:pos+4])[0]; typ=b[pos+4:pos+8]; data=b[pos+8:pos+8+n]
        assert zlib.crc32(typ+data)&0xffffffff==struct.unpack('>I',b[pos+8+n:pos+12+n])[0]
        if typ==b'IDAT': chunks.append(data)
        pos+=n+12
    assert typ==b'IEND' and pos==len(b)
    raw=zlib.decompress(b''.join(chunks)); assert len(raw)==h*(stride+1)
    result=bytearray(); previous=bytearray(stride)
    for y in range(h):
        offset=y*(stride+1); kind=raw[offset]; row=bytearray(raw[offset+1:offset+stride+1]); assert kind<=4
        if kind==2:
            row=bytearray((a+b)&255 for a,b in zip(row,previous))
        elif kind:
            for i in range(stride):
                left=row[i-channels] if i>=channels else 0
                up=previous[i]; corner=previous[i-channels] if i>=channels else 0
                if kind==1: predictor=left
                elif kind==3: predictor=(left+up)//2
                else:
                    p=left+up-corner; distances=(abs(p-left),abs(p-up),abs(p-corner))
                    predictor=(left,up,corner)[distances.index(min(distances))]
                row[i]=(row[i]+predictor)&255
        result.extend(row); previous=row
    return w,h,channels,bytes(result)


def verify_mask(name, regions):
    w,h,n,pixels=png_pixels((OUT/'png'/f'{name}.png').read_bytes())
    black=bytes([0,0,0]+([255] if n==4 else [])); white=bytes([255])*n
    expected=bytearray(black*w*h)
    for x,y,ww,hh in regions:
        left,top=math.floor(x),math.floor(y); right,bottom=math.ceil(x+ww),math.ceil(y+hh)
        assert 0<=left<=right<=w and 0<=top<=bottom<=h
        segment=white*(right-left)
        for row in range(top,bottom): expected[(row*w+left)*n:(row*w+right)*n]=segment
    assert pixels==expected,(name,'binary mask geometry/union differs')


def verify_navigation(root, actions):
    for a in actions:
        node=root.find(f'.//s:g[@data-action="{a["id"]}"]',NS); assert node is not None,a
        drawn=node.find('s:rect',NS)
        assert [float(drawn.get(k)) for k in ('x','y','width','height')]==a['rect']
        assert inside(a['image_rect'],a['rect'])
        if a['id'] in NAV:
            assert a['target']==NAV[a['id']][2] and a['tooltip']==NAV[a['id']][1]
            assert node.get('data-target')==a['target'] and node.find('s:title',NS).text==a['tooltip']


def verify_geometry(g):
    w,h=g['viewport']; r=g['rects']
    for key in ('grid','row_hints','column_hints','mini_card','coordinates','palette','status','tools','auxiliary','page_navigation'):
        assert inside(r[key],r['sheet']),(g['name'],key,'outside left page')
        assert not overlaps(r[key],r['fold']),(g['name'],key,'fold')
    assert r['sheet'][0]+r['sheet'][2]<r['fold'][0]
    for a in g['actions']:
        assert inside(a['rect'],r[a['group']]) and inside(a['rect'],[0,0,w,h]),a
        assert a['normalized']==[round(v/(w if i%2==0 else h),8) for i,v in enumerate(a['rect'])]
        assert a['image_normalized']==[round(v/(w if i%2==0 else h),8) for i,v in enumerate(a['image_rect'])]
        for key in ('grid','row_hints','column_hints','mini_card','coordinates','status'):
            assert not overlaps(a['rect'],r[key]),(a,key)
    for i,a in enumerate(g['actions']):
        for b in g['actions'][i+1:]: assert not overlaps(a['rect'],b['rect']),(a,b)


def verify(check_zip=True):
    manifest=read('manifest.json'); layout=read('layout.json'); cases=layout['cases']
    assert manifest['revision']==layout['revision']==REVISION
    assert manifest['generator_sha256']==sha(Path(__file__).read_bytes().replace(b'\r\n',b'\n'))
    assert len(cases)==5
    assert [(g['fixture'],g['viewport'],g['ui_scale'],g['cell_px'],g['visible_cells']) for g in cases]==[
        ('f02',[1920,1080],1,18,[40,40]),('f02',[2560,1440],1,18,[40,40]),
        ('f01',[2560,1440],1,24,[20,20]),('f03',[1920,1080],1,24,[57,28]),
        ('f02',[1280,720],1.25,22,[29,17])]
    for source in (OUT/'sources').iterdir():
        assert source.read_bytes()==subprocess.check_output(['git','show',f'{BASE}:docs/design/book_inventory/production/sources/{source.name}'],cwd=ROOT)
    for name,digest in manifest['files'].items():
        b=(OUT/name).read_bytes(); assert sha(b)==digest,name
        if name.endswith('.svg'):
            assert b'base64' not in b and b'@font-face' not in b
        if name.endswith('.png'):
            assert b[:8]==b'\x89PNG\r\n\x1a\n'; pos=8; chunks=[]
            while pos<len(b):
                n=struct.unpack('>I',b[pos:pos+4])[0]; typ=b[pos+4:pos+8]; data=b[pos+8:pos+8+n]
                assert zlib.crc32(typ+data)&0xffffffff==struct.unpack('>I',b[pos+8+n:pos+12+n])[0]
                if typ==b'IDAT': chunks.append(data)
                pos+=n+12
            width,height,depth,mode=struct.unpack('>IIBB',b[16:26])
            assert depth==8 and mode in (2,6)
            decoded=zlib.decompress(b''.join(chunks)); stride=width*(3 if mode==2 else 4)+1
            assert len(decoded)==height*stride and all(decoded[i*stride]<=4 for i in range(height))
            assert typ==b'IEND'
    for g in cases:
        d=read('sources/'+g['fixture']+'-public-demo.json')
        raw=subprocess.check_output(['git','show',f'{BASE}:prototypes/p1/data/{g["fixture"]}.json'],cwd=ROOT)
        fixture=json.loads(raw); assert sha(raw)==d['fixture_sha256']
        for key in ('id','revision','width','height','palette','rows','columns'): assert d[key]==fixture[key]
        assert set(d)=={'id','revision','width','height','palette','rows','columns','cells','fixture_sha256'}
        assert sha((OUT/'sources'/f'{g["fixture"]}-public-demo.json').read_bytes())==manifest['reference_data_sha256'][g['fixture']]
        colors={p['id']:p['color'] for p in d['palette']}
        root=ET.parse(OUT/'svg'/f'{g["name"]}-ui.svg').getroot()
        verify_geometry(g)
        expected_actions={'fill','erase','hand','undo','redo','minus','plus','fit','work','help','menu','nav-album','nav-information'}|{f'color-{i+1}' for i in range(len(d['palette']))}
        assert {a['id'] for a in g['actions']}==expected_actions
        assert {a.get('data-action') for a in root.findall('.//s:g[@data-action]',NS)}==expected_actions
        verify_navigation(root,g['actions'])
        w,h=g['viewport']; assert [int(root.get('width')),int(root.get('height'))]==[w,h]
        for a in g['actions']:
            assert inside(a['rect'],g['rects'][a['group']]) and inside(a['rect'],[0,0,w,h]),a
        for zone in g['rects'].values(): assert inside(zone,[0,0,w,h]),(g['name'],zone)
        for key,zone in g['rects'].items():
            assert g['normalized'][key]==[round(v/(w if i%2==0 else h),8) for i,v in enumerate(zone)]
        for a in g['actions']:
            for area in ('grid','row_hints','column_hints'):
                x,y,aw,ah=a['rect']; X,Y,W,H=g['rects'][area]
                assert x+aw<=X or X+W<=x or y+ah<=Y or Y+H<=y
        for area in ('grid','row_hints','column_hints'): assert inside(g['rects'][area],g['rects']['sheet'])
        for group in ('grid','miniature'):
            node=root.find(f'.//s:g[@id="{group}"]',NS); actual={}
            for el in node.iter():
                if 'data-cell' in el.attrib:
                    x,y,v=map(int,el.get('data-cell').split(',')); actual[x,y]=v
                    assert d['cells'][y*d['width']+x]==v
                    if v>0: assert el.get('fill')==colors[v]
            ox,oy=g['origin_zero_based'] if group=='grid' else [0,0]
            cols,rows=g['visible_cells'] if group=='grid' else [d['width'],d['height']]
            expected={(x,y):d['cells'][y*d['width']+x] for y in range(oy,oy+rows) for x in range(ox,ox+cols) if d['cells'][y*d['width']+x]>=0}
            assert actual==expected
        drawn=root.findall('.//s:text[@data-clue]',NS); expected_clues=set()
        ox,oy=g['origin_zero_based']; cols,rows=g['visible_cells']; sx,sy=g['slots_px']
        for axis,start,count,cap in [('rows',oy,rows,int((g['rects']['row_hints'][2]-8)/sx)),('columns',ox,cols,int((g['rects']['column_hints'][3]-8)/sy))]:
            for line in range(start,start+count):
                seq=d[axis][line]; indices=list(range(len(seq))) or [-2]
                if len(seq)>cap: indices=[-1]+list(range(len(seq)-cap+1,len(seq)))
                expected_clues.update(f'{axis},{line},{idx}' for idx in indices)
        assert {el.get('data-clue') for el in drawn}==expected_clues
        assert len(drawn)==len(expected_clues)
        for el in drawn:
            axis,line,index=el.get('data-clue').split(','); index=int(index)
            if index>=0:
                t=d[axis][int(line)][index]; assert el.text==str(t['length']) and el.get('style')=='fill:'+colors[t['color']]
        for suffix in ('layout','ui','keepout','crop'):
            name=f'png/{g["name"]}-{suffix}.png'; b=(OUT/name).read_bytes()
            assert list(struct.unpack('>II',b[16:24]))==[w,h]
        _,_,channels,pixels=png_pixels((OUT/'png'/f'{g["name"]}-ui.png').read_bytes())
        assert channels==4 and min(pixels[3::4])==0 and max(pixels[3::4])==255
        # Unknown grid cell centers must remain transparent, never an opaque page card.
        ox,oy=g['origin_zero_based']; gx,gy,_,_=g['rects']['grid']; cell=g['cell_px']
        for row in range(g['visible_cells'][1]):
            for col in range(g['visible_cells'][0]):
                if d['cells'][(oy+row)*d['width']+ox+col]==-1:
                    px=int(gx+(col+.5)*cell); py=int(gy+(row+.5)*cell)
                    assert pixels[(py*w+px)*4+3]==0
        _,_,channels,pixels=png_pixels((OUT/'png'/f'{g["name"]}-layout.png').read_bytes())
        for row in range(g['visible_cells'][1]):
            for col in range(g['visible_cells'][0]):
                value=d['cells'][(oy+row)*d['width']+ox+col]
                if value>0:
                    px=int(gx+(col+.5)*cell); py=int(gy+(row+.5)*cell)
                    assert pixels[(py*w+px)*channels:(py*w+px)*channels+3]==bytes.fromhex(colors[value].lstrip('#'))
        verify_mask(g['name']+'-keepout',[g['rects'][key] for key in QUIET])
        scale=g['background']['uniform_scale']
        assert scale==w/2560 and g['background']['offset_px']==[0,0] and g['background']['crop_px']==[0,0,2560,1440]
        verify_mask(g['name']+'-crop',[[8*scale,8*scale,w-16*scale,h-16*scale]])
    verify_mask('master-keepout',[[v/g['background']['uniform_scale'] for v in g['rects'][key]] for g in cases for key in QUIET])
    verify_mask('master-crop',[[8,8,2544,1424]])
    info=layout['navigation']['information']; r=info['rects']
    for key,zone in r.items():
        assert info['normalized'][key]==[round(v/(1920 if i%2==0 else 1080),8) for i,v in enumerate(zone)]
    assert layout['navigation']['views']==['work','information','album']
    assert layout['navigation']['contract']['preserve']==['cells','undo_redo','color','tool','grid_focus','grid_zoom','clue_reads']
    root=ET.parse(OUT/'svg/information-1920-ui.svg').getroot()
    verify_navigation(root,info['actions'])
    for key in ('title','return','settings','help','statistics'):
        assert inside(r[key],r['sheet']) and not overlaps(r[key],r['fold'])
    verify_mask('information-1920-keepout',[r[k] for k in ('title','return','settings','help','statistics')])
    verify_mask('information-1920-crop',[[6,6,1908,1068]])
    _,_,channels,pixels=png_pixels((OUT/'png/information-1920-ui.png').read_bytes())
    assert channels==4 and min(pixels[3::4])==0 and max(pixels[3::4])==255
    root=ET.parse(OUT/'svg/navigation.svg').getroot()
    assert {(n.get('data-action'),n.get('data-target'),n.get('data-state')) for n in root.findall('.//s:g[@data-action]',NS)}=={(key,NAV[key][2],state) for key in NAV for state in ('normal','hover','active')}
    checks=read('render-checks.json')['records']; assert len(checks)==27
    expected_names={g['name']+'-'+suffix for g in cases for suffix in ('layout','ui','keepout','crop')}|{'master-keepout','master-crop','navigation'}|{'information-1920-'+s for s in ('layout','ui','keepout','crop')}
    assert {c['file'] for c in checks}==expected_names
    assert {Path(n).stem for n in manifest['files'] if n.endswith('.png')}==expected_names
    assert all(c['overflow']==0 and all(f['status']=='loaded' for f in c['fonts']) for c in checks)
    for check in checks:
        g=next((case for case in cases if check['file'].startswith(case['name'])),info)
        w,h=g['viewport']
        assert check['measured_texts']==len(check['text_bounds'])
        for item in check['text_bounds']:
            assert inside(item['box'],[0,0,w,h])
            if item.get('zone'): assert inside(item['box'],g['rects'][item['zone']])
    for name in ('README.md','BRIEFING.md','VERIFICATION.md'): assert (OUT/name).is_file()
    if check_zip:
        with zipfile.ZipFile(OUT/'bp1r-review.zip') as z:
            expected={p.relative_to(OUT).as_posix():p for p in OUT.rglob('*') if p.is_file() and p.suffix!='.zip'}
            assert set(z.namelist())==set(expected) and len(z.namelist())==len(expected)
            assert not any(Path(n).suffix.lower() in ('.ttf','.otf','.woff','.woff2') for n in z.namelist())
            for n,p in expected.items(): assert z.read(n)==p.read_bytes(),n
    print('BP-1R: 5 layouts + information/navigation, 27 PNG/SVG pairs, source/data, geometry, navigation, transparency, binary masks/master union, hashes, render bounds and ZIP OK')


def pack():
    verify(check_zip=False)
    files=sorted(p for p in OUT.rglob('*') if p.is_file() and p.suffix!='.zip')
    assert not any(p.suffix.lower() in ('.ttf','.otf','.woff','.woff2') for p in files)
    with zipfile.ZipFile(OUT/'bp1r-review.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in files:
            info=zipfile.ZipInfo(p.relative_to(OUT).as_posix(),date_time=(2026,9,26,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,p.read_bytes())
    print('Review ZIP SHA-256:',sha((OUT/'bp1r-review.zip').read_bytes()))


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('mode',choices=['build','verify','pack'])
    parser.add_argument('--browser'); parser.add_argument('--fonts',type=Path)
    args=parser.parse_args()
    if args.mode=='build': build(args.browser,args.fonts)
    elif args.mode=='verify': verify()
    else: pack()
