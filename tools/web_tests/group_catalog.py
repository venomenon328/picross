"""Independent real-browser group; see the versioned scenario inventory."""
from browser_actions import open_page, state, point, control, wait, click
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
    labels = state(page, 'labels')['labels']
    assert all(x['unknown'] and not x['reveal'] and x['status'] == 'Neu' for x in labels)
    assert all(x['difficulty'] == 'Nicht eingestuft' for x in labels)
    for part in ('difficulty', 'mode'):
        page.mouse.move(*point(page, state(page, 'labels')['labels'][0][part+'_center']))
        page.wait_for_timeout(900)
        page.screenshot(path=str(output/f'{name}-ke-{part}-tooltip.png'))
        click(page, point(page, state(page, 'labels')['labels'][0][part+'_center']))
        wait(page, 'picrossProbe.work')
        assert state(page, 'id')['id'] == 'T-01'
        control(page, name='nav-album')
        wait(page, 'picrossProbe.album')
    passed('KE neutral new labels and passive mode/difficulty click routes')
    assert not errors, errors
