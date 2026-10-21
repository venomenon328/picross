"""HZ-C actual Chromium input and original frames; observer has no state setters."""
from browser_actions import control, wait, state, game_viewport, point
from hz_b_cases import select_view


def catalog(page, name, output, evidence):
    rows = []
    before = state(page, 'slots')['slots']
    for width, height, scale in ((1280, 720, 1.25), (1920, 1080, 1.0), (2560, 1440, 1.25), (1920, 1080, 1.0)):
        if state(page, 'ui_scale')['ui_scale'] != scale:
            control(page, text='Einstellungen / Info')
            control(page, text='UI ')
            control(page, name='nav-work')
        game_viewport(page, width, height)
        data = state(page, 'hz_c', 'labels')
        fs = 15 if scale == 1 else 19
        assert data['hz_c']['small_size'] == fs
        assert data['hz_c']['normal_size'] == (14 if scale == 1 else 18)
        assert all(data['hz_c'][key] == fs for key in ('category_size', 'category_popup_size', 'sort_size', 'sort_popup_size', 'view_size', 'view_popup_size'))
        for label in data['labels']:
            assert label['hzc_sizes'] == [fs] * 5
            assert label['text_fits'] and label['single_line'] and label['footer']
            assert abs(label['hzc_body_center'] - label['hzc_footer_height'] / 2) <= 1
        assert len({label['hzc_category_y'] for label in data['labels']}) == 1
        page.screenshot(path=str(output / f'{name}-hz-c-catalog-{width}.png'))
        for choice, visible, suffix in (('catalog-category', 'picrossProbe.hz.menu.visible', 'category'), ('catalog-sort', 'picrossProbe.sort.menu.visible', 'sort')):
            control(page, name=choice)
            wait(page, visible)
            page.screenshot(path=str(output / f'{name}-hz-c-{suffix}-{width}.png'))
            page.keyboard.press('Escape')
            wait(page, '!' + visible)
        control(page, text='Einstellungen / Info')
        rect = state(page, 'hz')['hz']['help_rect']
        page.mouse.move(*point(page, [rect[0]+rect[2]/2, rect[1]+rect[3]/2]))
        page.mouse.wheel(0, -10000)
        page.wait_for_timeout(250)
        page.screenshot(path=str(output / f'{name}-hz-c-settings-{width}.png'))
        control(page, name='puzzle-view')
        wait(page, 'picrossProbe.hz_b.view_popup')
        page.screenshot(path=str(output / f'{name}-hz-c-view-{width}.png'))
        selected = state(page, 'hz_b')['hz_b']['view_selected']
        select_view(page, 1-selected)
        control(page, name='puzzle-view')
        select_view(page, selected)
        control(page, name='nav-work')
        wait(page, 'picrossProbe.album')
        rows.append(dict(viewport=[width, height], ui_scale=scale, roles=data['hz_c'], labels=data['labels']))
    after = state(page, 'slots')['slots']
    for original, current in zip(before, after):
        for key in ('definition_id', 'definition_revision', 'cells', 'history', 'cursor', 'completed'):
            assert original[key] == current[key], key
    evidence['hz_c_typography'] = rows
