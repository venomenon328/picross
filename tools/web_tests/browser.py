"""Real exported-player event routes, IndexedDB roundtrips and failure cases."""
from __future__ import annotations
import argparse
import json
import platform
from pathlib import Path
import shutil
import tempfile
import time
from playwright.sync_api import sync_playwright
from serve import serve
from browser_runtime import options, graphics

DIAGNOSTIC_OUTPUT = None


def state(page):
    return page.evaluate('window.picrossProbe')


def wait(page, expression):
    page.wait_for_function(expression, timeout=60000)


def saved(page):
    wait(page, 'window.picrossStorage.ready && !picrossStorage.pending && !picrossStorage.error')


def game_viewport(page, width, height):
    # Browser/OS button metrics change the header height. The contract names
    # logical game area, not outer HTML viewport minus a guessed 42 pixels.
    page.set_viewport_size({'width':width, 'height':height+80})
    def settled():
        wait(page, f'''window.picrossProbe && innerWidth==={width} &&
          picrossProbe.viewport[0]===document.getElementById('surface').clientWidth &&
          picrossProbe.viewport[1]===document.getElementById('surface').clientHeight''')
        # At narrow widths the pending/saved label can wrap the header. Measure
        # its stable saved state, after Godot has handled the actual resize.
        saved(page)
    settled()
    overhead = page.evaluate('innerHeight - document.getElementById("surface").clientHeight')
    page.set_viewport_size({'width':width, 'height':height+overhead})
    settled()
    try:
        wait(page, f'window.picrossProbe && picrossProbe.viewport[0]==={width} && picrossProbe.viewport[1]==={height}')
    except Exception:
        print('VIEWPORT FAILURE', page.evaluate('''() => {
          const surface=document.getElementById('surface');
          return {html:[innerWidth,innerHeight],surface:[surface.clientWidth,surface.clientHeight],
            viewport:window.picrossProbe?.viewport,canvas:window.picrossProbe?.canvas,minimum:window.picrossProbe?.minimum,
            fit:window.picrossProbe?.fit}; }'''),flush=True)
        if DIAGNOSTIC_OUTPUT: page.screenshot(path=str(DIAGNOSTIC_OUTPUT/'viewport-failure.png'))
        raise


def point(page, position):
    box = page.locator('canvas').bounding_box()
    dims = state(page)['canvas']
    return box['x']+position[0]*box['width']/dims[0], box['y']+position[1]*box['height']/dims[1]


def control(page, text=None, name=None, tooltip=None, dialog=None):
    page.wait_for_timeout(150)
    items = state(page)['controls']
    found = [item for item in items if not item['disabled'] and
             (text is None or item['text'].startswith(text)) and
             (name is None or item['name'] == name) and
             (dialog is None or item['dialog'] == dialog) and
             (tooltip is None or item['tooltip'].startswith(tooltip))]
    if len(found) != 1 and DIAGNOSTIC_OUTPUT:
        page.screenshot(path=str(DIAGNOSTIC_OUTPUT/'control-failure.png'))
    assert len(found) == 1, (text, name, tooltip, items)
    page.mouse.click(*point(page, found[0]['center']))
    page.wait_for_timeout(180)


def cell(page, x, y):
    data = state(page)
    return point(page, [data['origin'][0]+(x+.5)*data['cell_size'], data['origin'][1]+(y+.5)*data['cell_size']])


def draw(page, start, end=None, button='left', retract=None):
    page.mouse.move(*cell(page,*start))
    page.mouse.down(button=button)
    if end:
        page.mouse.move(*cell(page,*end), steps=5)
    if retract:
        page.mouse.move(*cell(page,*retract), steps=4)
    page.mouse.up(button=button)
    page.wait_for_timeout(180)


def open_page(context, url):
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
    page.goto(url)
    wait(page, 'window.picrossProbe && picrossStorage.ready && document.getElementById("message").hidden')
    game_viewport(page,1920,1080)
    saved(page)
    assert not errors, errors
    return page, errors


def exercise(pw, name, root, update, url, output, evidence):
    results = evidence['scenarios']
    began = time.monotonic()
    def passed(label):
        results.append(label)
        evidence['elapsed_seconds'] = round(time.monotonic()-began, 2)
        print(name, 'PASS', label, flush=True)
    with tempfile.TemporaryDirectory(prefix='picross-web-profile-', ignore_cleanup_errors=True) as profile:
        browser = getattr(pw, name)
        def launch(scale=1):
            return browser.launch_persistent_context(profile, **options(name),
                viewport={'width':1920,'height':1122}, device_scale_factor=scale)
        context = launch()
        page, errors = open_page(context, url)
        version = context.browser.version if context.browser else page.evaluate('navigator.userAgent')
        evidence['version'] = version
        evidence['launch_options'] = options(name)
        evidence['graphics'] = graphics(page)
        passed('export/catalog startup')
        control(page, text='Blatt 01')
        wait(page, 'picrossProbe.work')
        draw(page, (2,2), (8,2), retract=(5,2))
        data = state(page)
        assert data['cells'][42:46] == [1]*4 and data['cells'][46] == -1 and data['cursor'] == 1
        draw(page, (2,3), (4,3), button='right')
        assert state(page)['cells'][62:65] == [0]*3
        control(page, name='undo')
        assert state(page)['cursor'] == 1 and len(state(page)['history']) == 2
        expected = {key: state(page)[key] for key in ('cells','history','cursor','view')}
        saved(page)
        page.screenshot(path=str(output/f'{name}-mono.png'))
        passed('left/right elastic stroke, atomic undo and redo branch')
        # Discard via Escape, opposite button and actual DOM focus loss.
        for cancel in ('escape', 'opposite', 'blur'):
            page.mouse.move(*cell(page,3,5)); page.mouse.down()
            page.mouse.move(*cell(page,8,5), steps=3)
            if cancel == 'escape': page.keyboard.press('Escape')
            elif cancel == 'opposite': page.mouse.down(button='right'); page.mouse.up(button='right')
            else: page.locator('#fullscreen').focus()
            page.mouse.up()
            page.wait_for_timeout(200)
            assert state(page)['cells'] == expected['cells'] and not state(page)['gesture'], cancel
        passed('Escape/opposite-button/focus cancellation without phantom commit')
        # A competing real document must be rejected before filesystem hydration.
        second = context.new_page(); second.goto(url)
        second.wait_for_function('document.getElementById("message").textContent.includes("anderen Tab")')
        assert not second.evaluate('window.picrossStorage.ready')
        second.close(); page.bring_to_front()
        passed('second writer blocked')
        page.reload(); wait(page, 'window.picrossProbe && picrossProbe.album'); saved(page)
        control(page, text='Blatt 01')
        for key in expected: assert state(page)[key] == expected[key], key
        passed('reload restores cells, complete history/redo and view')
        context.close()
        context = launch(1.25); page, errors = open_page(context, url)
        assert page.evaluate('devicePixelRatio') == 1.25
        control(page, text='Blatt 01')
        for key in expected: assert state(page)[key] == expected[key], key
        control(page, name='redo'); assert state(page)['cursor'] == 2
        saved(page)
        passed('real browser process restart at DPI125 restores history and redo works')
        expected_update = {key:state(page)[key] for key in ('cells','history','cursor','view')}
        identity = state(page)['root']
        # Install a second genuine export at the same entry; keep old resources.
        for release in (update/'releases').iterdir():
            shutil.copytree(release, root/'releases'/release.name, dirs_exist_ok=True)
        shutil.copyfile(update/'index.html',root/'next.html')
        (root/'next.html').replace(root/'index.html')
        page.reload(); wait(page,'window.picrossProbe && picrossProbe.album'); saved(page)
        assert page.locator('body').get_attribute('data-build') == json.loads((update/'build-manifest.json').read_text())['build_id']
        control(page,text='Blatt 01')
        assert state(page)['root'] == identity
        for key in expected_update: assert state(page)[key] == expected_update[key], key
        passed('second genuine compatible export retains IndexedDB identity and progress')
        # Input and fit stay paired under CSS/browser scale, resize and fullscreen.
        control(page, name='menu'); control(page, text='UI ')
        control(page, name='nav-work')
        evidence['viewports'] = []
        for width,height in ((1280,720),(1920,1080)):
            game_viewport(page,width,height)
            data = state(page)
            evidence['viewports'].append({'html':page.viewport_size, 'viewport':data['viewport'], 'canvas':data['canvas'],
                                          'fit':data['fit'], 'minimum':data['minimum']})
            assert data['fit'] and not data['minimum'], evidence['viewports']
            before = state(page)['cells']
            draw(page,(0,0)); assert state(page)['cells'][0] == 1
            control(page,name='undo'); assert state(page)['cells'] == before
        page.mouse.move(*cell(page,5,5)); page.mouse.wheel(0,300); page.wait_for_timeout(300)
        assert state(page)['fit']
        page.locator('#fullscreen').click(); page.wait_for_timeout(400)
        assert page.evaluate('!!document.fullscreenElement') and state(page)['fit']
        page.locator('#fullscreen').click(); page.wait_for_timeout(300)
        game_viewport(page,640,480)
        assert state(page)['minimum']
        game_viewport(page,1920,1080)
        assert state(page)['fit'] and not state(page)['minimum']
        passed('UI125, 720p/1080p, wheel zoom, fullscreen fit and hit geometry')
        if name == 'chromium':
            cdp = context.new_cdp_session(page)
            cdp.send('Emulation.setDeviceMetricsOverride',dict(**page.viewport_size,deviceScaleFactor=1.5,mobile=False))
            page.wait_for_timeout(300)
            assert page.evaluate('devicePixelRatio') == 1.5
            before = state(page)['cells']
            draw(page,(1,0)); assert state(page)['cells'][1] == 1
            control(page,name='undo'); assert state(page)['cells'] == before and state(page)['fit']
            cdp.send('Emulation.clearDeviceMetricsOverride')
            passed('live DPI change to 150 percent preserves hit geometry')
        # The rectangular row and square column really overflow at this geometry.
        for axis in ('row','column'):
            game_viewport(page,1920,1080)
            control(page,name='nav-album'); control(page,text='Blatt 06' if axis=='row' else 'Blatt 02')
            game_viewport(page,1280,720)
            before = state(page)['cells']
            data = state(page); area = data[axis+'_area']; origin = data['origin']; step = data['cell_size']
            lines = data['rows' if axis=='row' else 'columns']
            index = max(range(len(lines)), key=lambda i:len(lines[i]))
            position = [area[0]+area[2]/2, origin[1]+(index+.5)*step] if axis=='row' else [origin[0]+(index+.5)*step,area[1]+area[3]/2]
            start = point(page,position)
            old_steps = data[axis+'_steps']
            page.mouse.move(*start); page.mouse.down(button='middle')
            page.mouse.move(start[0]+(180 if axis=='row' else 0),start[1]+(180 if axis=='column' else 0),steps=8)
            page.mouse.up(button='middle'); page.wait_for_timeout(250)
            assert state(page)['cells'] == before
            assert state(page)[axis+'_steps'] != old_steps, (axis,old_steps,state(page)[axis+'_steps'])
            page.screenshot(path=str(output/f'{name}-colour-{axis}-clues.png'))
        passed('middle mouse moves long row/column clue windows and preserves cells')
        game_viewport(page,1920,1080)
        control(page,name='nav-album'); control(page,text='Blatt 03')
        draw(page,(0,2),(4,2)); wait(page,'picrossProbe.ending && picrossProbe.completed')
        wait(page,'!picrossProbe.ea_active && !picrossProbe.ea_processing && picrossProbe.ea_caption_alpha===1')
        assert state(page)['ea_title'].startswith('Blatt 03') and state(page)['ea_art']
        saved(page)
        completed_slot = state(page)['slots'][2]
        control(page,name='reset',tooltip='Rätsel zurücksetzen')
        control(page,text='Abbrechen',dialog=True)
        assert state(page)['ending'] and state(page)['slots'][2] == completed_slot
        page.reload(); wait(page,'window.picrossProbe && picrossProbe.album'); saved(page)
        control(page,text='Blatt 03')
        assert state(page)['ending'] and not state(page)['ea_active'] and not state(page)['ea_processing']
        assert state(page)['slots'][2] == completed_slot
        foreign_slot = state(page)['slots'][0]
        control(page,name='reset',tooltip='Rätsel zurücksetzen')
        control(page,text='Zurücksetzen',dialog=True); saved(page)
        assert state(page)['work'] and not state(page)['completed'] and not state(page)['ea_art']
        assert state(page)['slots'][2]['history'] == [] and state(page)['slots'][0] == foreign_slot
        draw(page,(0,2),(4,2)); wait(page,'picrossProbe.ending && picrossProbe.completed')
        assert state(page)['ea_active']
        passed('EA completion, late caption, neutral heading, cancel, durable browser reload, origin-bound reset and repeated animation')
        control(page,name='nav-album')
        control(page,text='Blatt 05')
        for index in range(8):
            control(page,name=f'color-{index+1}')
            draw(page,(index,2))
        wait(page,'picrossProbe.ending && picrossProbe.completed'); saved(page)
        passed('mono and eight-colour completion through real mouse events')
        control(page,name='nav-album'); control(page,text='Blatt 06')
        assert state(page)['dimensions'] == [50,30] and state(page)['fit']
        control(page,name='color-8'); draw(page,(2,2)); assert state(page)['cells'][102] == 8
        passed('50x30 rectangle, colour ID 8 and full-grid fit')
        assert not errors, errors
        # Real IDB transaction boundary throws quota failure, then an actual retry commits.
        page.evaluate('''() => { window.originalTransaction = IDBDatabase.prototype.transaction;
          IDBDatabase.prototype.transaction = function(...args) { if(args[1]==='readwrite') throw new DOMException('test quota','QuotaExceededError'); return originalTransaction.apply(this,args); }; }''')
        draw(page,(3,2)); wait(page,'!!picrossStorage.error')
        control(page,name='menu'); control(page,text='Beenden')
        page.wait_for_timeout(500)
        assert page.locator('#retry').is_visible() and not page.locator('#message').is_visible()
        page.evaluate('() => { IDBDatabase.prototype.transaction = window.originalTransaction; }')
        page.locator('#retry').click(); saved(page)
        passed('actual IndexedDB write failure is visible; own quit stays open; retry commits')
        # End a document without beforeunload while a real transaction fails.
        control(page,name='nav-work')
        durable = state(page)['cells']
        page.evaluate('''() => { IDBDatabase.prototype.transaction = function(...args) { if(args[1]==='readwrite') throw new DOMException('blocked','QuotaExceededError'); return originalTransaction.apply(this,args); }; }''')
        draw(page,(4,2)); wait(page,'!!picrossStorage.error')
        page.close(run_before_unload=False)
        page, errors = open_page(context,url)
        control(page,text='Blatt 06')
        assert state(page)['cells'] == durable
        passed('abrupt tab close loses unacknowledged edit but retains last acknowledged state')
        # Corrupt only a test slot primary, persist it, and load real recovery after reload.
        control(page,name='nav-album'); control(page,text='Blatt 01')
        draw(page,(8,8)); saved(page)
        page.evaluate('''() => { picrossStorage.fs.writeFile(picrossProbe.root+'/t01.json','broken'); picrossStorage.changed(); }''')
        saved(page); page.reload(); wait(page,'window.picrossProbe && picrossProbe.album')
        assert state(page)['slot_status'][0] == 'recovered'
        passed('corrupt primary reload uses valid backup without silent overwrite')
        assert page.evaluate("picrossStorage.fs.readFile(picrossProbe.root+'/t01.json',{encoding:'utf8'})") == 'broken'
        control(page,text='Backup übernehmen'); control(page,text='Übernehmen',dialog=True)
        saved(page)
        assert state(page)['slot_status'][0] == 'loaded'
        passed('explicit backup confirmation repairs primary through existing validation')
        # Both copies become incompatible; startup must leave their bytes intact.
        page.evaluate('''() => { for (const suffix of ['.json','.bak']) {
          const path=picrossProbe.root+'/t01'+suffix;
          const data=JSON.parse(picrossStorage.fs.readFile(path,{encoding:'utf8'}));
          data.definition_revision+=1; picrossStorage.fs.writeFile(path,JSON.stringify(data));
        } picrossStorage.changed(); }''')
        saved(page)
        incompatible = page.evaluate("picrossStorage.fs.readFile(picrossProbe.root+'/t01.json',{encoding:'utf8'})")
        page.reload(); wait(page,'window.picrossProbe && picrossProbe.album'); saved(page)
        assert state(page)['slot_status'][0] == 'error'
        assert page.evaluate("picrossStorage.fs.readFile(picrossProbe.root+'/t01.json',{encoding:'utf8'})") == incompatible
        passed('incompatible revisions rejected without migration or overwrite')
        # Reset is exercised via the real confirmation dialog and preserves other slots.
        other = state(page)['slots'][4]
        control(page,name='reset-T-01',tooltip='Rätsel zurücksetzen')
        control(page,text='Zurücksetzen',dialog=True)
        saved(page)
        assert state(page)['slots'][0]['history'] == [] and state(page)['slots'][4] == other
        passed('confirmed reset and slot isolation')
        # Same origin under a path prefix still runs the real export and shares saves.
        nested = root/'nested'
        if not nested.exists(): shutil.copytree(update,nested)
        page.goto(url+'nested/'); wait(page,'window.picrossProbe && picrossProbe.album'); saved(page)
        assert state(page)['slots'][4] == other
        control(page,text='Blatt 06')
        context.set_offline(True)
        before = state(page)['cells']; draw(page,(7,7)); assert state(page)['cells'] != before
        control(page,name='undo'); assert state(page)['cells'] == before
        saved(page); context.set_offline(False)
        passed('real subpath startup, stable saves and offline-after-load input')
        assert not errors, errors
        control(page,name='nav-album')
        control(page,text='Beenden'); page.wait_for_function('document.getElementById("message").textContent.includes("Spiel beendet")')
        assert not page.evaluate('picrossStorage.pending')
        assert page.evaluate('picrossStorage.exitCode') == 0
        # This pinned-engine diagnostic occurs only during engine teardown,
        # including in the uninstrumented player. Keep it visible in evidence;
        # gameplay/navigation errors above and all new restart errors still fail.
        exit_errors = list(errors)
        known_exit = ['ERROR: Pages in use exist at exit in PagedAllocator: N16WorkerThreadPool5GroupE',
                      '   at: ~PagedAllocator (./core/templates/paged_allocator.h:170)']
        evidence['exit_diagnostics'] = exit_errors
        assert exit_errors in ([], known_exit), exit_errors
        page.reload()
        wait(page,'window.picrossProbe && picrossProbe.album && picrossStorage.ready && document.getElementById("message").hidden')
        saved(page)
        assert state(page)['slots'][4] == other
        assert errors == exit_errors, errors
        passed('own quit acknowledges durable sync, exits zero and reload restores saved state')
        context.close()
        with tempfile.TemporaryDirectory(prefix='picross-blocked-',ignore_cleanup_errors=True) as blocked_profile:
            blocked = browser.launch_persistent_context(blocked_profile,**options(name))
            try:
                blocked.add_init_script("indexedDB.open = () => { throw new DOMException('blocked by test policy','SecurityError'); };")
                denied = blocked.pages[0]; denied.goto(url)
                try:
                    denied.wait_for_function('document.getElementById("message").textContent.includes("Browserspeicher nicht verfügbar")',timeout=60000)
                except Exception:
                    denied.screenshot(path=str(output/f'{name}-blocked-failure.png'))
                    evidence['blocked_failure_message'] = denied.locator('#message').inner_text()
                    raise
                assert not denied.evaluate('picrossStorage.ready')
                passed('blocked IndexedDB startup displays failure before gameplay')
            finally: blocked.close()
    evidence['status'] = 'passed'


def main():
    global DIAGNOSTIC_OUTPUT
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--update-build',type=Path,required=True)
    parser.add_argument('--browser',choices=['chromium','firefox','both'],default='both')
    args=parser.parse_args(); args.output.mkdir(parents=True,exist_ok=True)
    DIAGNOSTIC_OUTPUT = args.output
    hosting = tempfile.TemporaryDirectory(prefix='picross-browser-host-')
    root = Path(hosting.name)/'site'
    shutil.copytree(args.build,root)
    server,url=serve(root)
    report=dict(os=platform.platform(), manifest=json.loads((args.build/'build-manifest.json').read_text()),
                update_manifest=json.loads((args.update_build/'build-manifest.json').read_text()),results=[])
    try:
        with sync_playwright() as pw:
            for name in (('chromium','firefox') if args.browser=='both' else (args.browser,)):
                evidence = dict(browser=name, scenarios=[], status='failed')
                report['results'].append(evidence)
                shutil.copyfile(args.build/'index.html',root/'index.html')
                exercise(pw,name,root,args.update_build,url,args.output,evidence)
    finally:
        (args.output/'browser-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        server.shutdown()
        hosting.cleanup()


if __name__=='__main__': main()
