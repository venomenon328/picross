"""Build the offline gallery and compact contact sheets after rendering screens."""
import base64
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from generate import OUT, sheet, save


def thumbnail(s,name,x,y,w,h):
    encoded=base64.b64encode((OUT/'png'/f'{name}.png').read_bytes()).decode()
    s.add(f'<image x="{x}" y="{y}" width="{w}" height="{h}" href="data:image/png;base64,{encoded}"/>')


def main():
    m=json.loads((OUT/'manifest.json').read_text(encoding='utf-8'))
    m['records']=[r for r in m['records'] if r['name'] not in ('sizes','comparison')]
    s=sheet('Drei Richtungen · ein Arbeitsstand','S1 / S2 / S3 · F-02 · 1920 × 1080 · U1 · dieselben Daten, Farben und Flächen',1920,690)
    for i,(name,title) in enumerate([('s1-u1-f02-1920','S1 · Illustrationsalbum'),('s2-u1-f02-1920','S2 · Reisejournal'),('s3-u1-f02-1920','S3 · Atelier')]):
        x=32+i*634
        s.text(x,229,title,23,font='Fraunces',weight=600)
        thumbnail(s,name,x,252,610,343)
    s.text(56,649,'Vergleichsübersicht, verkleinert. Vollauflösende PNGs und editierbare SVGs in der Galerie öffnen.',17)
    m['records'].append(save('comparison',s))
    s=sheet('Größenprobe · U1 und U2','Sechs eigene Layouts. Miniaturen unten verkleinert; die verlinkten Einzelbilder behalten die angegebenen Pixelmaße.',1920,1670)
    for row,(key,w,h,ui) in enumerate([('f01',2560,1440,100),('f03',1920,1080,100),('f02',1280,720,125)]):
        for j,u in enumerate(('u1','u2')):
            name=f's1-{u}-{key}-{w}'; r=next(r for r in m['records'] if r['name']==name); g=r['geometry']
            x=56+j*930; y=215+row*465
            cell=g['cell']; ox,oy=g['origin']; _,_,gw,gh=g['grid']; hw,hh=g['hints']; mw=g['mini'][2]
            s.text(x,y,f'{u.upper()} · {key.upper().replace("F0","F-0")} · {w} × {h} / UI {ui} %',24,font='Fraunces',weight=600)
            thumbnail(s,name,x,y+18,590,332)
            s.text(x+610,y+65,f'Zelle {cell} px / Zoom {round(cell/24*100,2)} %',15)
            s.text(x+610,y+98,f'Ausschnitt {ox+1}–{ox+int(gw/cell)} / {oy+1}–{oy+int(gh/cell)}',15)
            s.text(x+610,y+131,f'Raster {gw} × {gh}',15)
            s.text(x+610,y+164,f'Links {hw} × {gh}',15)
            s.text(x+610,y+197,f'Oben {gw} × {hh}',15)
            s.text(x+610,y+230,f'Miniatur {mw} × {mw}',15)
            s.text(x+610,y+263,f'Hintergrund {r["visible_background_percent"]} %',15)
            s.text(x,y+388,'Ausschnitt = Spalten / Zeilen, einsbasiert. Hintergrund = vollständig unbedeckte Pixel.',14)
    s.text(56,1630,'720p: bewusste Arbeitszoomprobe 22 px für 16,25-px-Ziffern. UI-Ziele 55 px, kein Skalieren des gesamten Screens.',17)
    m['records'].append(save('sizes',s))
    (OUT/'manifest.json').write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
    groups=[('Stilrichtungen',['comparison','s1-u1-f02-1920','s2-u1-f02-1920','s3-u1-f02-1920']),('Anordnung',['s1-u1-f02-1920','s1-u2-f02-1920','layouts']),('Details und Schrift',['s1-detail','s2-detail','s3-detail','icons','typography']),('Größen',['sizes']+[r['name'] for r in m['records'] if 'geometry' in r and r['name'] not in ['s1-u1-f02-1920','s2-u1-f02-1920','s3-u1-f02-1920','s1-u2-f02-1920']]),('Hintergrundstudien',['s1-background','s2-background','s3-background'])]
    body=[]
    for section,names in groups:
        body.append(f'<section><h2>{section}</h2><div class="grid">')
        for name in names:
            r=next(r for r in m['records'] if r['name']==name)
            body.append(f'<article><h3>{name}</h3><a href="png/{name}.png"><img loading="lazy" src="png/{name}.png" alt="Statische Entwurfsstudie {name}" width="{r["dimensions"][0]}" height="{r["dimensions"][1]}"></a><p><a href="png/{name}.png">PNG in Originalgröße</a> · <a href="svg/{name}.svg">Editierbares SVG</a></p></article>')
        body.append('</div></section>')
    page='''<!doctype html>
<html lang="de"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Picross · Z1.1 · Visuelle Studie</title>
<style>
@font-face{font-family:Fraunces;src:url(fonts/Fraunces.ttf)}
@font-face{font-family:Plex;src:url(fonts/PlexSans.ttf)}
*{box-sizing:border-box}body{margin:0;background:#efe9dc;color:#293e3d;font:17px Plex,sans-serif}
header,main{max-width:1600px;margin:auto;padding:36px}header{border-bottom:3px solid #293e3d}
h1{font:600 52px Fraunces,serif;margin:16px 0}h2{font:600 30px Fraunces,serif;margin-top:54px}
h3{font-size:16px}a{color:#843d2d}p{line-height:1.6;max-width:1000px}.eyebrow{letter-spacing:.15em;font-size:13px}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px}article{background:#fffaf0;padding:18px;border:1px solid #a0a994}
img{display:block;width:100%;height:auto;border:1px solid #a0a994}a:focus{outline:3px solid #843d2d;outline-offset:4px}
@media(max-width:800px){.grid{grid-template-columns:1fr}header,main{padding:20px}h1{font-size:36px}}
</style>
<header><div class="eyebrow">PICROSS / ISSUE 26 / ENTSCHEIDUNGSVORLAGE</div><h1>Ein Blatt. Drei eigene Stimmen.</h1>
<p>21 statische Tafeln, keine Spielintegration. S1/S2/S3 halten F-02 und U1 konstant; U1/U2 halten S1 konstant.
Alle Screens verwenden explizite Beispieleingaben, originale Hinweise und unveränderte Rätselfarben.
Die Konturhilfe C1 ist ein Vorschlag. Keine Stilwahl ist getroffen.</p>
<p><a href="README.md">Entscheidungsunterlage</a> · <a href="BACKGROUNDS.md">Bildbriefings</a> · <a href="SOURCES.md">Quellen und Reproduktion</a> · <a href="manifest.json">Rendermanifest</a></p>
<p>Zum Lesen der Hinweise das PNG in Originalgröße öffnen. Die Galerie passt Vorschauen dem Fenster an;
das ist keine Behauptung, die verkleinerten Vorschauen seien spielbare Oberflächen.</p></header><main>'''+''.join(body)+'''<p>Eigentümerentscheidung zu Stil, Anordnung, Schrift und Kontrast vor #27/#23. Technisches Review und Mergefreigabe separat.</p></main></html>
'''
    (OUT/'index.html').write_text(page,encoding='utf-8',newline='\n')


if __name__=='__main__': main()
