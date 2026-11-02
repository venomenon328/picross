"""Two bounded browser cases for real edits and geometry transitions."""
from browser_actions import open_page, control, wait, draw, state, saved, game_viewport, cell
from hz_c_cases import typography


def exercise(pw, name, root, update, url, output, evidence, session):
    passed = session.passed
    context = session.launch()
    page, errors = open_page(context, url)
    control(page, text='Blatt 01'); wait(page, 'picrossProbe.work')
    draw(page, (2,2), (8,2), retract=(5,2))
    data = state(page, 'cells', 'cursor')
    assert data['cells'][42:46] == [1]*4 and data['cells'][46] == -1 and data['cursor'] == 1
    draw(page, (2,3), (4,3), button='right')
    edited = state(page, 'cells', 'history', 'cursor')
    assert edited['cells'][62:65] == [0]*3 and edited['cursor'] == 2
    control(page, name='undo')
    assert state(page, 'cursor')['cursor'] == 1
    control(page, name='redo')
    assert state(page, 'cells', 'history', 'cursor') == edited
    page.mouse.move(*cell(page,3,5)); page.mouse.down()
    page.mouse.move(*cell(page,8,5), steps=3)
    # Observe the live gesture, then the Escape cancellation before releasing.
    # An initially false, asynchronously published probe is not an event ack;
    # neither should Mouse.up race the keyboard event on a software renderer.
    wait(page, 'picrossProbe.gesture')
    page.keyboard.press('Escape')
    wait(page, '!picrossProbe.gesture')
    cancelled = state(page, 'cells', 'history', 'cursor')
    assert cancelled == edited, dict(before=edited, after_escape=cancelled)
    page.mouse.up()
    wait(page, '!picrossProbe.gesture')
    released = state(page, 'cells', 'history', 'cursor')
    assert released == edited, dict(before=edited, after_release=released)
    evidence['cancellation'] = dict(active_observed=True, escape_cancelled_before_release=True,
                                    cells_history_cursor_unchanged=True)
    saved(page)
    page.screenshot(path=str(output/f'{name}-input.png'))
    passed('real elastic edit, atomic undo, redo and cancellation')

    evidence['viewports'] = []
    evidence['typography'] = []
    for width, height, scale in ((1280,720,1.25),(1920,1080,1.0)):
        control(page, name='menu'); control(page, text='UI ')
        control(page, name='nav-work'); wait(page, 'picrossProbe.work')
        game_viewport(page, width, height)
        evidence['typography'].append(typography(page, scale))
        data = state(page, 'viewport', 'fit', 'minimum')
        assert data['fit'] and not data['minimum']
        evidence['viewports'].append(data)
    before = state(page, 'cells', 'history', 'cursor')
    cdp = context.new_cdp_session(page)
    cdp.send('Emulation.setDeviceMetricsOverride', dict(**page.viewport_size,deviceScaleFactor=1.5,mobile=False))
    wait(page, 'devicePixelRatio === 1.5 && picrossProbe.fit')
    draw(page, (1,0)); assert state(page, 'cells')['cells'][1] == 1
    control(page, name='undo')
    assert state(page, 'cells')['cells'] == before['cells']
    assert state(page, 'cursor')['cursor'] == before['cursor']
    evidence['dpi'] = page.evaluate('devicePixelRatio')
    cdp.send('Emulation.clearDeviceMetricsOverride')
    assert not errors, errors
    passed('resize and live DPI preserve fit and hit geometry')
