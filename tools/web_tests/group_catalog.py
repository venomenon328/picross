"""Independent real-browser group; see the versioned scenario inventory."""
from browser_actions import open_page, state, point, control, wait, click, game_viewport
from browser_runtime import options, graphics


def exercise(pw, name, root, update, url, output, evidence, session):
    passed = session.passed
    context = session.launch()
    page, errors = open_page(context, url)
    version = context.browser.version if context.browser else page.evaluate('navigator.userAgent')
    evidence['version'] = version
    evidence['launch_options'] = options(name)
    evidence['graphics'] = graphics(page)
    passed('export/catalog startup')
    evidence['catalog_geometry'] = []
    for width, height, scale in ((1280,720,1.25),(1920,1080,1.0),(2560,1440,1.25)):
        if state(page, 'ui_scale')['ui_scale'] != scale:
            control(page, name='menu'); control(page, text='UI ')
            control(page, name='nav-album')
        game_viewport(page,width,height)
        page.wait_for_timeout(200)
        labels = state(page, 'labels')['labels']
        assert all(x['unknown'] and not x['reveal'] and x['status'] == 'Neu' for x in labels)
        assert all(x['difficulty'] == 'Nicht eingestuft' for x in labels)
        assert all(x['text_fits'] and x['single_line'] and x['footer'] and x['status_kind'] == x['status'] for x in labels)
        assert all(x['size'] == labels[0]['size'] for x in labels)
        evidence['catalog_geometry'].append(dict(viewport=[width,height],ui_scale=scale,labels=labels))
        page.screenshot(path=str(output/f'{name}-ku-{width}-ui{int(scale*100)}.png'))
    first = state(page, 'labels')['labels'][0]
    for part in ('difficulty_icon','difficulty'):
        page.mouse.move(*point(page, first['centers'][part]))
        page.wait_for_timeout(900)
        assert state(page, 'visible_popups')['visible_popups'] == 0
    first = state(page, 'labels')['labels'][0]
    assert first['difficulty_tip'] == first['fallback_tip'] == '' and not first['mode_popup']
    page.screenshot(path=str(output/f'{name}-ku-no-difficulty-tooltip.png'))
    page.mouse.move(*point(page, first['mode_center']))
    wait(page, 'picrossProbe.labels[0].mode_popup')
    assert first['mode_tip'] == 'Monochromes Rätsel'
    page.screenshot(path=str(output/f'{name}-ku-mode-tooltip.png'))
    for part in ('dimensions','difficulty_icon','difficulty','mode_tip','paper','leaf','status_icon','note'):
        click(page, point(page, state(page, 'labels')['labels'][0]['centers'][part]))
        wait(page, 'picrossProbe.work')
        assert state(page, 'id')['id'] == 'T-01'
        control(page, name='nav-album')
        wait(page, 'picrossProbe.album')
    passed('KU-A single-line metadata, footer, tooltip boundaries and passive click routes')
    assert not errors, errors
