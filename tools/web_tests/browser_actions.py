"""Real exported-player event routes, IndexedDB roundtrips and failure cases."""
from __future__ import annotations
from browser_runtime import graphics
import timing
import json

DIAGNOSTIC_OUTPUT = None
DIAGNOSTIC_EVIDENCE = None


@timing.measured('state')
def state(page, *keys):
    if not keys:
        raise ValueError('State queries must name their observed fields')
    return page.evaluate('keys => Object.fromEntries(keys.map(k => [k, window.picrossProbe[k]]))', list(keys))


def wait(page, expression):
    try:
        page.wait_for_function(expression, timeout=60000, polling=100)
    except Exception:
        if DIAGNOSTIC_OUTPUT:
            page.screenshot(path=str(DIAGNOSTIC_OUTPUT/'wait-failure.png'))
        diagnostic=page.evaluate('''() => ({probe:window.picrossProbe,html:[innerWidth,innerHeight],
          surface:[document.getElementById('surface').clientWidth,document.getElementById('surface').clientHeight]})''')
        if DIAGNOSTIC_OUTPUT:
            (DIAGNOSTIC_OUTPUT/'wait-failure.json').write_text(json.dumps(diagnostic,ensure_ascii=True),encoding='utf-8')
        print('WAIT FAILURE',expression,json.dumps({k:v for k,v in diagnostic.items() if k!='probe'}),flush=True)
        raise


@timing.measured('save_confirmation')
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
    dims = state(page, 'canvas')['canvas']
    return box['x']+position[0]*box['width']/dims[0], box['y']+position[1]*box['height']/dims[1]


def click(page, position):
    # Same genuine browser events, explicitly ordered. Playwright's convenience
    # click dispatches move/down/up concurrently when no delay is specified.
    # Keep each acknowledgement separate for the measured software-render route.
    page.mouse.move(*position)
    page.mouse.down()
    page.mouse.up()


def control(page, text=None, name=None, tooltip=None, dialog=None):
    page.wait_for_timeout(150)
    items = state(page, 'controls')['controls']
    found = [item for item in items if not item['disabled'] and
             (text is None or item['text'].startswith(text)) and
             (name is None or item['name'] == name) and
             (dialog is None or item['dialog'] == dialog) and
             (tooltip is None or item['tooltip'].startswith(tooltip))]
    if len(found) != 1 and DIAGNOSTIC_OUTPUT:
        page.screenshot(path=str(DIAGNOSTIC_OUTPUT/'control-failure.png'))
    assert len(found) == 1, (text, name, tooltip, items)
    click(page, point(page, found[0]['center']))
    page.wait_for_timeout(180)


def cell(page, x, y):
    data = state(page, 'origin', 'cell_size')
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


def open_page(context, url, before_start=None):
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
    if DIAGNOSTIC_EVIDENCE is not None:
        DIAGNOSTIC_EVIDENCE.setdefault('console_errors',[]).append(errors)
    page.goto(url)
    if before_start:
        before_start(page)
    wait(page, 'window.picrossProbe && picrossStorage.ready && document.getElementById("message").hidden')
    game_viewport(page,1920,1080)
    saved(page)
    assert not errors, errors
    if DIAGNOSTIC_EVIDENCE is not None:
        DIAGNOSTIC_EVIDENCE['graphics'] = graphics(page)
        DIAGNOSTIC_EVIDENCE['user_agent'] = page.evaluate('navigator.userAgent')
    return page, errors
