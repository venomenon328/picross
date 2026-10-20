"""HZ-B genuine Chromium pointer, keyboard and resize events."""
from browser_actions import control, wait, state, game_viewport, point


def catalog(page, name, output, evidence):
    rows = []
    before = state(page, 'slots')['slots']
    for width, height, scale in ((1280, 720, 1.25), (1920, 1080, 1.0), (2560, 1440, 1.25)):
        if state(page, 'ui_scale')['ui_scale'] != scale:
            control(page, text='Einstellungen / Info')
            control(page, text='UI ')
            control(page, name='nav-work')
        game_viewport(page, width, height)
        assert state(page, 'hz_b')['hz_b']['notice']
        direction = state(page, 'sort')['sort']['direction']
        assert state(page, 'hz_b')['hz_b']['sort_icon'].endswith(
            'arrow-up.svg' if direction == 'asc' else 'arrow-down.svg')
        control(page, name='catalog-sort')
        wait(page, 'picrossProbe.sort.menu.visible')
        page.screenshot(path=str(output / f'{name}-hz-b-sort-{width}.png'))
        # Outside click must dismiss without activating the information button.
        item = next(c for c in state(page, 'controls')['controls'] if c['text'] == 'Einstellungen / Info')
        page.mouse.click(*point(page, item['center']))
        wait(page, '!picrossProbe.sort.menu.visible')
        assert state(page, 'album')['album']
        control(page, name='catalog-category')
        wait(page, 'picrossProbe.hz.menu.visible')
        game_viewport(page, width + 1, height)
        wait(page, '!picrossProbe.hz.menu.visible')
        game_viewport(page, width, height)
        control(page, text='Einstellungen / Info')
        rect = state(page, 'hz')['hz']['help_rect']
        page.mouse.move(*point(page, [rect[0]+rect[2]/2, rect[1]+rect[3]/2]))
        page.mouse.wheel(0, 10000)
        page.wait_for_timeout(250)
        old = state(page, 'hz_b')['hz_b']['animations']
        control(page, text='Zellanimationen')
        wait(page, f'picrossProbe.hz_b.animations === {str(not old).lower()}')
        page.keyboard.press('Space')
        wait(page, f'picrossProbe.hz_b.animations === {str(old).lower()}')
        page.screenshot(path=str(output / f'{name}-hz-b-settings-{width}.png'))
        page.mouse.wheel(0, -10000)
        page.wait_for_timeout(250)
        control(page, name='puzzle-view')
        wait(page, 'picrossProbe.hz_b.view_popup')
        assert state(page, 'hz_b')['hz_b']['view_checked']
        page.screenshot(path=str(output / f'{name}-hz-b-view-{width}.png'))
        old_view = state(page, 'hz_b')['hz_b']['view_selected']
        page.keyboard.press('Home' if old_view else 'End')
        page.keyboard.press('Enter')
        wait(page, '!picrossProbe.hz_b.view_popup')
        wait(page, f'picrossProbe.hz_b.view_selected === {1-old_view}')
        control(page, name='puzzle-view')
        page.keyboard.press('Home' if not old_view else 'End')
        page.keyboard.press('Enter')
        wait(page, f'!picrossProbe.hz_b.view_popup && picrossProbe.hz_b.view_selected === {old_view}')
        control(page, name='puzzle-view')
        page.keyboard.press('Escape')
        wait(page, '!picrossProbe.hz_b.view_popup')
        rows.append(dict(viewport=[width, height], ui_scale=scale, controls=state(page, 'hz_b')['hz_b']))
        control(page, name='nav-work')
        wait(page, 'picrossProbe.album')
    # View settings may be persisted; puzzle edits/history must never change.
    after = state(page, 'slots')['slots']
    for a, b in zip(before, after):
        for key in ('definition_id', 'definition_revision', 'cells', 'history', 'cursor', 'completed'):
            assert a[key] == b[key], key
    evidence['hz_b_controls'] = rows
