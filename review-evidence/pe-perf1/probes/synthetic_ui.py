import os,sys,json,time,shutil,subprocess,hashlib
from pathlib import Path
HOME=Path(__file__).parent;REPO=HOME/'work';sys.path.insert(0,str(REPO))
os.environ.update(TEMP=str(HOME/'temp-synthetic-ui'),TMP=str(HOME/'temp-synthetic-ui'),TMPDIR=str(HOME/'temp-synthetic-ui'))
from tools.puzzle_editor.server import Service
from tests.puzzle_production.test_catalog_images import SVG,png
from playwright.sync_api import sync_playwright

def main():
    root=HOME/'synthetic-ui-data'
    if not root.exists():shutil.copytree(HOME/'synthetic-seed-636',root)
    # Tiny synthetic pilot inputs for an actual current-category preview.
    margins=root/'game/art/drawing/margins';margins.mkdir(parents=True,exist_ok=True)
    for side in ('left','right'):(margins/f'water_{side}.png').write_bytes(png((64,64)))
    assets=HOME/'browser-inputs';assets.mkdir(exist_ok=True)
    (assets/'reveal.svg').write_bytes(SVG);(assets/'background.png').write_bytes(png((2304,576)))
    (assets/'invalid.png').write_bytes(png((20,20)))
    evidence=HOME/'synthetic-ui-originals';evidence.mkdir(exist_ok=True)
    s=Service(root,temporary=HOME/'temp-synthetic-ui');s.bind()
    report={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),'resolution':[1600,1000],'steps':[],'operations':[],'headless':True,'native_test':False}
    def record(name):report['steps'].append(name);print('PASS',name,flush=True)
    with sync_playwright() as p:
        browser=p.chromium.launch(channel='msedge',headless=True,args=['--no-first-run','--no-default-browser-check'])
        report['browser']=browser.version
        context=browser.new_context(viewport={'width':1600,'height':1000},device_scale_factor=1)
        page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        def idle(error=False):
            deadline=time.monotonic()+330
            while page.locator('body.busy').count():
                if time.monotonic()>deadline:raise AssertionError('Browser job timeout')
                time.sleep(.1)
            if not error:assert 'error' not in (page.locator('#status').get_attribute('class') or ''),page.locator('#status').inner_text()
        def select():page.locator('.entry[data-id="pz-test-direct-mono"]').click();idle();assert page.locator('#form').is_visible()
        def auth(raster=False):
            page.locator('#authority').evaluate('(e)=>e.open=true')
            page.locator('#actor').fill('Browser test operator');page.locator('#statement').fill('Explicit synthetic browser decision; own test geometry only.')
            page.locator('#confirmed').check()
            if raster:prov('raster')
        def prov(kind):
            for key,value in {'author':'Synthetic fixture','usage_basis':'Repository-owned test pixels','source':'Local synthetic geometry','changes':'Prepared unchanged test asset'}.items():page.locator('#'+kind+'-'+key).fill(value)
        def apply():
            t=time.perf_counter();page.locator('#apply').click();idle();report['operations'].append({'action':'apply','wall_seconds':time.perf_counter()-t})
        def check():
            t=time.perf_counter();page.locator('#check').click();idle();assert page.locator('#preview').is_visible();report['operations'].append({'action':'plan','wall_seconds':time.perf_counter()-t})
        def picture_input(kind,file):
            with page.expect_file_chooser() as chooser:page.locator('#'+kind+'-file').click()
            chooser.value.set_files(str(assets/file));idle()
        def shot(name):
            if name=='02-change-preview.png':
                page.locator('#preview').evaluate('(e)=>e.scrollIntoView({behavior:"instant",block:"start"})');time.sleep(.4)
            if name=='01-list-detail.png': return
            page.locator('#preview' if name=='02-change-preview.png' else '#status').screenshot(path=str(evidence/name))
        try:
            page.goto(s.url());idle();assert page.locator('.entry').count()==2
            assert page.url==s.origin+'/'
            page.locator('#search').fill('TEST ONLY');assert page.locator('.entry').count()==1
            page.locator('#search').fill('');page.locator('#filter').select_option('voegel');assert page.locator('.entry').count()==2
            select();assert page.locator('.entry.active img').count()==1;record('real Edge search/filter/select and current detail with lazy current-image catalog preview')
            page.evaluate('window.scrollTo(0,0)');shot('01-list-detail.png')
            page.locator('#name').fill('Unsaved browser text')
            page.once('dialog',lambda d:d.dismiss());page.locator('.entry[data-id="pz-test-direct-color"]').click();idle()
            assert page.locator('#name').input_value()=='Unsaved browser text';assert page.locator('#puzzle-id').inner_text()=='pz-test-direct-mono'
            page.once('dialog',lambda d:d.accept());page.locator('#discard').click();idle();assert page.locator('#name').input_value()=='TEST ONLY'
            record('unsaved ID switch guard and explicit discard')
            page.locator('#categories').click();idle();page.locator('#category-name').fill('Browsergruppe')
            page.locator('#category-check').click();idle();apply()
            assert page.locator('#filter option',has_text='Browsergruppe').count()==1
            record('separate category creation via actual plan and apply')
            new_category=page.locator('#filter option',has_text='Browsergruppe').get_attribute('value')
            page.locator('#filter').select_option('');select()
            page.locator('#category').select_option(new_category);idle();check();apply()
            assert page.locator('#category').input_value()==new_category
            page.locator('#categories').click();idle()
            page.locator('#category-op').select_option('category_rename');page.locator('#category-target').select_option(new_category)
            page.locator('#category-name').fill('Browser renamed group');page.locator('#category-check').click();idle();apply()
            assert page.locator('#filter option',has_text='Browser renamed group').count()==1
            page.locator('#categories').click();idle()
            page.locator('#category-op').select_option('category_delete');page.locator('#category-target').select_option(new_category)
            page.locator('#category-reassign').select_option('voegel');page.locator('#category-confirmed').check()
            page.locator('#category-check').click();idle();apply()
            assert page.locator('#category').input_value()=='voegel'
            assert page.locator('#filter option[value="'+new_category+'"]').count()==0
            assert page.locator('#migration').is_visible()
            record('actual category assignment, rename and occupied delete plus explicit reassign; v7 retained')
            page.locator('#filter').select_option('');select()
            page.locator('#migrate').click();idle();assert 'v7' in page.locator('#plan-summary').inner_text();apply()
            assert not page.locator('#migration').is_visible();select();record('explicit browser v7 to v8 migration preview and confirmation')
            # Invalid upload and actual server-side raster error, without content mutation.
            with page.expect_file_chooser() as chooser:page.locator('#background-file').click()
            chooser.value.set_files(str(assets/'invalid.png'));idle(error=True)
            assert '2304' in page.locator('#status').inner_text()
            picture_input('reveal','reveal.svg');prov('reveal')
            page.locator('#raster').evaluate('(e)=>e.closest("details").open=true')
            page.locator('#raster').fill('1 9\n1 1\n');auth(raster=True)
            assert 'Zeile 1, Spalte 2' in page.locator('#grid-status').inner_text()
            page.locator('#check').click();idle(error=True);assert 'Zeile 1, Spalte 2' in page.locator('#status').inner_text()
            page.locator('#raster').scroll_into_view_if_needed();shot('03-error.png');record('headless file-input chooser event, invalid dimension and actual backend cell error; no native-dialog claim')
            page.locator('#raster').fill('1 1 1\n1 1 1\n')
            # Real DOM drop handler against the real service; no mocked fetch/DOM implementation.
            raw=list((assets/'background.png').read_bytes())
            page.locator('[data-kind="background"]').evaluate('(el, bytes)=>{const dt=new DataTransfer();dt.items.add(new File([new Uint8Array(bytes)],"background.png",{type:"image/png"}));el.dispatchEvent(new DragEvent("drop",{dataTransfer:dt,bubbles:true,cancelable:true}));}',raw)
            idle();prov('background');page.locator('#name').fill('Browser combo');page.locator('#category').select_option('wasserwelt');idle();auth(raster=True)
            check();assert page.locator('#revision-warning').is_visible();shot('02-change-preview.png');apply()
            assert page.locator('#title').inner_text()=='Browser combo';assert page.locator('#background').input_value()=='selected'
            record('file drop plus one actual A3 metadata/image/background/raster apply and readback')
            page.locator('#background').select_option('none');idle();auth();check();apply();assert page.locator('#background').input_value()=='none'
            page.locator('#background').select_option('standard');idle();assert page.locator('#background-pictures img').count()==2;auth();check();apply();assert page.locator('#background').input_value()=='standard'
            record('selected none standard UI roundtrip and actual category pilot preview')
            page.locator('#name').fill('Not saved on refresh');page.once('dialog',lambda d:d.accept());page.reload();idle();select();assert page.locator('#name').input_value()=='Browser combo'
            record('real refresh unsaved warning and no implicit persistence')
            port=s.http.server_port;s.close();s=None
            page.locator('#reload').click();idle(error=True);assert 'fetch' in page.locator('#status').inner_text().lower()
            s=Service(root,temporary=HOME/'temp-synthetic-ui');s.bind(port)
            page.goto(s.url());idle();select();assert page.locator('#name').input_value()=='Browser combo'
            record('real connection failure retry and fresh-session restart with retained checkout')
            assert not errors,errors
            report['passed']=True;report['page_errors']=errors
            report['screenshots']=[{'file':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted(evidence.glob('*.png'))]
            assert len(report['screenshots'])==2
            (HOME/'synthetic-ui-report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        finally:
            context.close();browser.close()
            if s:s.close()

if __name__=='__main__':
    (HOME/'temp-synthetic-ui').mkdir(exist_ok=True)
    main()
