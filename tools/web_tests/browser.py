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


def state(page):
    return page.evaluate('window.picrossProbe')


def wait(page, expression):
    page.wait_for_function(expression, timeout=60000)


def saved(page):
    wait(page, 'window.picrossStorage.ready && !picrossStorage.pending && !picrossStorage.error')


def point(page, position):
    box = page.locator('canvas').bounding_box()
    dims = state(page)['canvas']
    return box['x']+position[0]*box['width']/dims[0], box['y']+position[1]*box['height']/dims[1]


def control(page, text=None, name=None, tooltip=None):
    page.wait_for_timeout(150)
    items = state(page)['controls']
    found = [item for item in items if not item['disabled'] and
             (text is None or item['text'].startswith(text)) and
             (name is None or item['name'] == name) and
             (tooltip is None or item['tooltip'].startswith(tooltip))]
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
    saved(page)
    assert not errors, errors
    return page, errors


def exercise(pw, name, root, url, output, evidence):
    results = evidence['scenarios']
    def passed(label):
        results.append(label)
        print(name, 'PASS', label, flush=True)
    with tempfile.TemporaryDirectory(prefix='picross-web-profile-', ignore_cleanup_errors=True) as profile:
        browser = getattr(pw, name)
        def launch():
            return browser.launch_persistent_context(profile, headless=True,
                viewport={'width':1920,'height':1122}, device_scale_factor=1)
        context = launch()
        page, errors = open_page(context, url)
        version = context.browser.version if context.browser else page.evaluate('navigator.userAgent')
        evidence['version'] = version
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
        context = launch(); page, errors = open_page(context, url)
        control(page, text='Blatt 01')
        for key in expected: assert state(page)[key] == expected[key], key
        control(page, name='redo'); assert state(page)['cursor'] == 2
        saved(page)
        passed('real browser process restart restores history and redo works')
        # Input and fit stay paired under CSS/browser scale, resize and fullscreen.
        control(page, name='menu'); control(page, text='UI ')
        control(page, name='nav-work')
        for width,height in ((1280,762),(1920,1122)):
            page.set_viewport_size({'width':width,'height':height}); page.wait_for_timeout(300)
            assert state(page)['fit'] and not state(page)['minimum']
            before = state(page)['cells']
            draw(page,(0,0)); assert state(page)['cells'][0] == 1
            control(page,name='undo'); assert state(page)['cells'] == before
        page.mouse.move(*cell(page,5,5)); page.mouse.wheel(0,300); page.wait_for_timeout(300)
        assert state(page)['fit']
        page.locator('#fullscreen').click(); page.wait_for_timeout(400)
        assert page.evaluate('!!document.fullscreenElement') and state(page)['fit']
        page.locator('#fullscreen').click(); page.wait_for_timeout(300)
        passed('UI125, 720p/1080p, wheel zoom, fullscreen fit and hit geometry')
        control(page,name='nav-album'); control(page,text='Blatt 02')
        before = state(page)['cells']
        # Long row 12 and column 12 from the established fixed fixture.
        for axis in ('row','column'):
            data = state(page); area = data[axis+'_area']; origin = data['origin']; step = data['cell_size']
            position = [area[0]+area[2]/2, origin[1]+11.5*step] if axis=='row' else [origin[0]+11.5*step,area[1]+area[3]/2]
            start = point(page,position)
            page.mouse.move(*start); page.mouse.down(button='middle')
            page.mouse.move(start[0]+(180 if axis=='row' else 0),start[1]+(180 if axis=='column' else 0),steps=8)
            page.mouse.up(button='middle'); page.wait_for_timeout(250)
            assert state(page)['cells'] == before
        page.screenshot(path=str(output/f'{name}-colour-clues.png'))
        passed('middle mouse clue routes preserve cells')
        control(page,name='nav-album'); control(page,text='Blatt 03')
        draw(page,(0,2),(4,2)); wait(page,'picrossProbe.ending && picrossProbe.completed')
        control(page,text='Zurück ins Album')
        control(page,text='Blatt 05')
        for index in range(8):
            control(page,name=f'color-{index+1}')
            draw(page,(index,2))
        wait(page,'picrossProbe.ending && picrossProbe.completed'); saved(page)
        passed('mono and eight-colour completion through real mouse events')
        control(page,text='Zurück ins Album'); control(page,text='Blatt 06')
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
        page.evaluate('IDBDatabase.prototype.transaction = window.originalTransaction')
        page.locator('#retry').click(); saved(page)
        passed('actual IndexedDB write failure is visible; own quit stays open; retry commits')
        # Corrupt only a test slot primary, persist it, and load real recovery after reload.
        control(page,name='nav-work'); control(page,name='nav-album'); control(page,text='Blatt 01')
        draw(page,(8,8)); saved(page)
        page.evaluate('''() => { picrossStorage.fs.writeFile(picrossProbe.root+'/t01.json','broken'); picrossStorage.changed(); }''')
        saved(page); page.reload(); wait(page,'window.picrossProbe && picrossProbe.album')
        assert state(page)['slot_status'][0] == 'recovered'
        passed('corrupt primary reload uses valid backup without silent overwrite')
        # Reset is exercised via the real confirmation dialog and preserves other slots.
        other = state(page)['slots'][4]
        control(page,tooltip='Blatt 01',text='Zurücksetzen')
        control(page,text='Zurücksetzen')
        saved(page)
        assert state(page)['slots'][0]['history'] == [] and state(page)['slots'][4] == other
        passed('confirmed reset and slot isolation')
        control(page,text='Beenden'); page.wait_for_function('document.getElementById("message").textContent.includes("Spiel beendet")')
        assert not page.evaluate('picrossStorage.pending')
        passed('own quit acknowledges durable sync and displays restart instruction')
        context.close()
    evidence['status'] = 'passed'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--browser',choices=['chromium','firefox','both'],default='both')
    args=parser.parse_args(); args.output.mkdir(parents=True,exist_ok=True)
    server,url=serve(args.build.resolve())
    report=dict(os=platform.platform(), manifest=json.loads((args.build/'build-manifest.json').read_text()),results=[])
    try:
        with sync_playwright() as pw:
            for name in (('chromium','firefox') if args.browser=='both' else (args.browser,)):
                evidence = dict(browser=name, scenarios=[], status='failed')
                report['results'].append(evidence)
                exercise(pw,name,args.build,url,args.output,evidence)
    finally:
        (args.output/'browser-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        server.shutdown()


if __name__=='__main__': main()
