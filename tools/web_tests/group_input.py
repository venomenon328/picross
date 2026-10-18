"""Independent real-browser group; see the versioned scenario inventory."""
from browser_actions import open_page, control, wait, draw, state, saved, game_viewport, cell, point


def exercise(pw, name, root, update, url, output, evidence, session):
    passed = session.passed
    context = session.launch(1.25)
    page, errors = open_page(context, url)
    control(page, text='Blatt 01')
    wait(page, 'picrossProbe.work')
    draw(page, (2,2), (8,2), retract=(5,2))
    data = state(page, 'cells', 'cursor')
    assert data['cells'][42:46] == [1]*4 and data['cells'][46] == -1 and data['cursor'] == 1
    draw(page, (2,3), (4,3), button='right')
    assert state(page, 'cells')['cells'][62:65] == [0]*3
    control(page, name='undo')
    assert state(page, 'cursor')['cursor'] == 1 and len(state(page, 'history')['history']) == 2
    expected = state(page, 'cells', 'history', 'cursor', 'view')
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
        assert state(page, 'cells')['cells'] == expected['cells'] and not state(page, 'gesture')['gesture'], cancel
    passed('Escape/opposite-button/focus cancellation without phantom commit')
    # Input and fit stay paired under CSS/browser scale, resize and fullscreen.
    control(page, name='menu'); control(page, text='UI ')
    control(page, name='nav-work')
    evidence['viewports'] = []
    for width,height in ((1280,720),(1920,1080)):
        game_viewport(page,width,height)
        data = state(page, 'viewport', 'canvas', 'fit', 'minimum')
        evidence['viewports'].append({'html':page.viewport_size, 'viewport':data['viewport'], 'canvas':data['canvas'],
                                      'fit':data['fit'], 'minimum':data['minimum']})
        assert data['fit'] and not data['minimum'], evidence['viewports']
        before = state(page, 'cells')['cells']
        draw(page,(0,0)); assert state(page, 'cells')['cells'][0] == 1
        control(page,name='undo'); assert state(page, 'cells')['cells'] == before
    page.mouse.move(*cell(page,5,5)); page.mouse.wheel(0,300); page.wait_for_timeout(300)
    assert state(page, 'fit')['fit']
    page.locator('#fullscreen').click(); page.wait_for_timeout(400)
    assert page.evaluate('!!document.fullscreenElement') and state(page, 'fit')['fit']
    page.locator('#fullscreen').click(); page.wait_for_timeout(300)
    game_viewport(page,640,480)
    assert state(page, 'minimum')['minimum']
    game_viewport(page,1920,1080)
    assert state(page, 'fit')['fit'] and not state(page, 'minimum')['minimum']
    passed('UI125, 720p/1080p, wheel zoom, fullscreen fit and hit geometry')
    if name == 'chromium':
        cdp = context.new_cdp_session(page)
        cdp.send('Emulation.setDeviceMetricsOverride',dict(**page.viewport_size,deviceScaleFactor=1.5,mobile=False))
        page.wait_for_timeout(300)
        assert page.evaluate('devicePixelRatio') == 1.5
        before = state(page, 'cells')['cells']
        draw(page,(1,0)); assert state(page, 'cells')['cells'][1] == 1
        control(page,name='undo'); assert state(page, 'cells')['cells'] == before and state(page, 'fit')['fit']
        cdp.send('Emulation.clearDeviceMetricsOverride')
        passed('live DPI change to 150 percent preserves hit geometry')
    # The rectangular row and square column really overflow at this geometry.
    for axis in ('row','column'):
        game_viewport(page,1920,1080)
        control(page,name='nav-album'); control(page,text='Blatt 06' if axis=='row' else 'Blatt 02')
        game_viewport(page,1280,720)
        before = state(page, 'cells')['cells']
        data = state(page, axis+'_area', 'origin', 'cell_size', 'rows' if axis=='row' else 'columns', axis+'_steps'); area = data[axis+'_area']; origin = data['origin']; step = data['cell_size']
        lines = data['rows' if axis=='row' else 'columns']
        index = max(range(len(lines)), key=lambda i:len(lines[i]))
        position = [area[0]+area[2]/2, origin[1]+(index+.5)*step] if axis=='row' else [origin[0]+(index+.5)*step,area[1]+area[3]/2]
        start = point(page,position)
        old_steps = data[axis+'_steps']
        page.mouse.move(*start); page.mouse.down(button='left')
        page.mouse.move(start[0]+(180 if axis=='row' else 0),start[1]+(180 if axis=='column' else 0),steps=8)
        page.mouse.up(button='left'); page.wait_for_timeout(250)
        assert state(page, 'cells')['cells'] == before
        assert state(page, axis+'_steps')[axis+'_steps'] != old_steps, (axis,old_steps,state(page, axis+'_steps')[axis+'_steps'])
        page.screenshot(path=str(output/f'{name}-colour-{axis}-clues.png'))
    passed('left mouse moves long row/column clue windows and preserves cells')
    game_viewport(page,1920,1080)
    control(page,name='nav-album'); control(page,text='Blatt 06')
    assert state(page, 'dimensions')['dimensions'] == [50,30] and state(page, 'fit')['fit']
    control(page,name='color-8'); draw(page,(2,2)); assert state(page, 'cells')['cells'][102] == 8
    passed('50x30 rectangle, colour ID 8 and full-grid fit')
    assert not errors, errors
