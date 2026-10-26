"""One representative current catalog flow, not the historical KU/AT/HZ matrices."""
from browser_actions import open_page, state, point, control, wait, click
from group_persistence import choose_sort
from hz_c_cases import typography
from hz_b_cases import select_view


def exercise(pw, name, root, update, url, output, evidence, session):
    passed = session.passed
    context = session.launch()
    page, errors = open_page(context, url)
    evidence['version'] = page.evaluate('navigator.userAgent')
    before = state(page, 'slots')['slots']
    data = state(page, 'hz', 'hz_b', 'labels', 'sort')
    assert data['hz']['standard'] == 'Tidy Hand' and data['hz']['local_only'] and data['hz']['notice']
    assert data['hz_b']['notice']
    assert data['sort']['criterion'] == 'category' and data['sort']['direction'] == 'asc'
    assert all(x['unknown'] and not x['reveal'] and x['status'] == 'Neu' for x in data['labels'])
    assert {x['difficulty'] for x in data['labels']} == {'Nicht eingestuft','Sehr leicht','Leicht','Mittel','Schwer','Sehr schwer'}
    evidence['typography'] = [typography(page, 1)]
    page.screenshot(path=str(output/f'{name}-catalog.png'))
    control(page, name='catalog-category'); wait(page, 'picrossProbe.hz.menu.visible')
    menu = state(page, 'hz')['hz']['menu']
    assert menu['font'] == 'Tidy Hand'
    x, y = menu['position']; w, h = menu['size']
    assert x >= 0 and y >= 0 and x+w <= 1920 and y+h <= 1080
    page.screenshot(path=str(output/f'{name}-category.png'))
    page.keyboard.press('Escape'); wait(page, '!picrossProbe.hz.menu.visible')
    # One criterion and both directions exercise the browser wiring. The full
    # comparator/tie/unknown-value matrix remains in native small logic tests.
    choose_sort(page, 1)
    evidence['sorting'] = []
    for direction in ('asc', 'desc'):
        if direction == 'desc':
            control(page, name='catalog-direction')
            wait(page, "picrossProbe.sort.direction === 'desc'")
        current = state(page, 'sort')['sort']
        assert current['primary'] == sorted(current['primary'], reverse=direction == 'desc')
        evidence['sorting'].append(current)
    control(page, name='catalog-sort'); wait(page, 'picrossProbe.sort.menu.visible')
    page.screenshot(path=str(output/f'{name}-sort.png'))
    item = next(c for c in state(page, 'controls')['controls'] if c['text'] == 'Einstellungen / Info')
    click(page, point(page, item['center']))
    wait(page, '!picrossProbe.sort.menu.visible'); assert state(page, 'album')['album']
    # Passive metadata opens its own stable ID even after sorting.
    current = state(page, 'sort', 'labels')
    chosen = current['sort']['visible_ids'][0]
    click(page, point(page, current['labels'][0]['centers']['paper']))
    wait(page, 'picrossProbe.work'); assert state(page, 'id')['id'] == chosen
    control(page, name='nav-album'); wait(page, 'picrossProbe.album')
    assert state(page, 'sort')['sort']['selected'] == chosen
    control(page, text='Einstellungen / Info')
    control(page, name='puzzle-view'); wait(page, 'picrossProbe.hz_b.view_popup')
    assert state(page, 'hz_b')['hz_b']['view_checked']
    page.screenshot(path=str(output/f'{name}-view.png'))
    selected = state(page, 'hz_b')['hz_b']['view_selected']
    select_view(page, 1-selected)
    control(page, name='puzzle-view'); select_view(page, selected)
    control(page, name='nav-work'); wait(page, 'picrossProbe.album')
    after = state(page, 'slots')['slots']
    for a, b in zip(before, after, strict=True):
        for key in ('definition_id', 'definition_revision', 'cells', 'history', 'cursor', 'completed'):
            assert a[key] == b[key], key
    assert not errors, errors
    passed('current catalog, sorting and paper controls')
