import json
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parent
ui=Path.cwd()/'tools/production_workspace/ui'
job={'title':'Erdbeere','puzzle_id':'pz-erdbeere','revision':'r01','id':'test','source':'remote'}
record={'file':'content/authoring/pz-erdbeere/r01/record.json','sha256':'a'*64}
source='https://github.com/venomenon328/picross/tree/'+'b'*40
state={'jobs':[], 'phase':'reveal_review'}
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(ui),**kwargs)
    def do_GET(self):
        if self.path.startswith('/api/'):
            if self.path=='/api/jobs':
                payload={'jobs':state['jobs'],'mode':'remote','snapshot':'test','synced_at':'2026-11-11T19:22:00Z','errors':[]}
            elif self.path=='/api/jobs/test':
                payload={**job,'record':record,'publication':'Testquelle · fester Gitstand','source_url':source,
                         'facts':{'state':state['phase'],'authoring_version':'0.8.0','blockers':[],'next_step':'Abschlussbild wählen','verification':''},
                         'offers':[{'kind':'reveal','id':'A','label':'Ansicht A','asset_ids':['A'],'record':record}],
                         'assets':[{'role':'reveal','id':'A','caption':'Ansicht A','location':{'sha256':'a'*64}}]}
            elif self.path=='/api/jobs/test/assets/A':
                import base64
                self.send_response(200);self.send_header('Content-Type','image/png');self.end_headers()
                self.wfile.write(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9WIHmjwAAAAASUVORK5CYII='));return
            else: self.send_error(404);return
            self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers()
            self.wfile.write(json.dumps(payload).encode());return
        super().do_GET()
    def log_message(self,*args): pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()

with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=browser.new_context(viewport={'width':1440,'height':975},color_scheme='light',permissions=['clipboard-read','clipboard-write'])
    ctx.set_default_timeout(8000)
    page=ctx.new_page()
    errors=[]
    page.on('pageerror',lambda err: errors.append(str(err)))
    page.goto(f'http://127.0.0.1:{server.server_port}/#test')
    brief=page.get_by_label('Was soll dein Rätsel zeigen?')
    notes=page.get_by_label('Zusätzliche Motivhinweise')
    brief.fill('Erdbeere');notes.fill('Eine einzelne reife Frucht, schräg von vorn.\nDer grüne Blattkelch soll auffallen.')
    page.screenshot(path=str(root/'desktop-light.png'),full_page=True)
    page.get_by_text('Rastervorgaben',exact=False).first.click()
    w=page.get_by_label('Breite (Zellen)');h=page.get_by_label('Höhe (Zellen)')
    copy=page.get_by_role('button',name='Auftrag kopieren')
    w.fill('28');assert copy.is_disabled()
    h.fill('19');page.get_by_label('Maßvorgabe').select_option('exact')
    mode=page.get_by_label('Farbmodus');mode.select_option('color')
    count=page.get_by_label('Vordergrundfarben')
    count.fill('9');assert copy.is_disabled()
    count.fill('4');page.get_by_label('Farbzahlvorgabe').select_option('approx')
    copy.click()
    prompt=page.evaluate('navigator.clipboard.readText()')
    assert all(s in prompt for s in ['exakt 28 × 19','ungefähr 4 Vordergrundfarben','Der grüne Blattkelch','Schritt 1'])
    page.get_by_label('Darstellung').select_option('dark')
    page.screenshot(path=str(root/'desktop-dark.png'),full_page=True)
    page.get_by_role('button',name='Neues Motiv',exact=False).click()
    assert brief.input_value()=='' and notes.input_value()=='' and mode.input_value()==''
    brief.fill('Qualle')
    page.get_by_role('button',name='Erdbeere',exact=True).click()
    assert h.input_value()=='19' and count.input_value()=='4' and 'Blattkelch' in notes.input_value()
    page.reload()
    page.get_by_role('button',name='Erdbeere',exact=True).click()
    assert count.input_value()=='4' and page.get_by_label('Darstellung').input_value()=='dark'
    for width in [1280,820,768,390,320]:
        page.set_viewport_size({'width':width,'height':840})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), width
    page.set_viewport_size({'width':390,'height':844})
    nav=page.get_by_text('Entwürfe und Gitstände',exact=True)
    assert nav.is_visible() and not page.get_by_role('button',name='Qualle',exact=True).is_visible()
    nav.click()
    assert page.get_by_role('button',name='Qualle',exact=True).is_visible()
    nav.click()
    page.screenshot(path=str(root/'mobile-dark.png'),full_page=True)
    mode.select_option('mono')
    assert not count.is_visible()
    copy.click()
    prompt=page.evaluate('navigator.clipboard.readText()')
    assert 'monochrom' in prompt and '4 Vordergrundfarben' not in prompt and 'farbig' in prompt
    state['jobs']=[job]
    page.reload();page.get_by_role('button',name='Diese Variante wählen').click()
    assert w.is_visible()
    w.fill('50');h.fill('35')
    copy.click()
    assert 'Schritt 2' in (prompt:=page.evaluate('navigator.clipboard.readText()')) and 'ungefähr 50 × 35' in prompt
    state['phase']='motif_review';page.reload()
    page.get_by_label('Nächste Aktion').select_option('rework')
    page.get_by_label('Was soll geändert').fill('Kleineres Raster')
    page.get_by_text('Rastervorgaben',exact=False).first.click();w.fill('25');h.fill('18');copy.click()
    assert 'ungefähr 25 × 18' in (prompt:=page.evaluate('navigator.clipboard.readText()')) and 'Ich gebe die' not in prompt
    page.get_by_label('Nächste Aktion').select_option('continue')
    copy.click()
    assert '25 × 18' not in page.evaluate('navigator.clipboard.readText()')
    assert not errors,errors
    print('OK. Chromium',browser.version,'· Drafts, reload, themes, 320–1440 px, clipboard, validation and published phases.')
    browser.close()
server.shutdown()
