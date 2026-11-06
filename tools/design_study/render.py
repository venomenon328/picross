"""Optional local render: Playwright 1.55.0 and an explicitly selected Chromium.

python tools/design_study/render.py --browser PATH
The finished gallery and verification tests have no renderer/network dependency.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from io import BytesIO

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/design/z1_1'


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--browser',required=True)
    args=parser.parse_args()
    from playwright.sync_api import sync_playwright
    from PIL import Image
    manifest=json.loads((OUT/'manifest.json').read_text(encoding='utf-8'))
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=args.browser,headless=True)
        page=browser.new_page(device_scale_factor=1)
        for record in manifest['records']:
            name=record['name']; w,h=record['dimensions']
            page.set_viewport_size(dict(width=w,height=h))
            svg=(OUT/'svg'/f'{name}.svg').read_text(encoding='utf-8')
            page.set_content('<html><meta charset="utf-8"><style>body{margin:0}svg{display:block}</style>'+svg+'</html>')
            page.evaluate('document.fonts.ready')
            page.screenshot(path=str(OUT/'png'/f'{name}.png'))
            record['svg_sha256']=hashlib.sha256(svg.encode()).hexdigest()
            record['png_sha256']=hashlib.sha256((OUT/'png'/f'{name}.png').read_bytes()).hexdigest()
            # Geometric text bounds catch actual font overflow at the screen edges.
            record['outer_text_overflow']=page.evaluate('''() => [...document.querySelectorAll('text')].filter(e=>e.ownerSVGElement===document.querySelector('svg')).filter(e=>{const r=e.getBoundingClientRect(); return r.left<0 || r.top<0 || r.right>innerWidth+1 || r.bottom>innerHeight+1}).map(e=>e.textContent)''')
            record['fonts_loaded']=page.evaluate('() => [...document.fonts].map(f=>({family:f.family,status:f.status}))')
            if 'geometry' in record:
                page.evaluate("document.querySelector('[id^=background-]').style.display='none'")
                mask=Image.open(BytesIO(page.screenshot(omit_background=True))).convert('RGBA')
                clear=mask.getchannel('A').histogram()[0]
                record['visible_background_pixels']=clear
                record['visible_background_percent']=round(100*clear/(w*h),2)
            print(name,record['outer_text_overflow'])
        manifest['renderer']=dict(engine='Chromium / Microsoft Edge',version=browser.version,playwright='1.55.0',device_scale_factor=1,python=sys.version.split()[0],font_wait='document.fonts.ready',network='none during rendering')
        browser.close()
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')


if __name__=='__main__':
    main()
