"""Read-only observation plus real browser controls; fixed synthetic export."""
from browser_actions import control, wait, state, game_viewport, point


def catalog(page, name, output, evidence):
    rows = []
    for width, height, scale in ((1280,720,1.25),(1920,1080,1.0),(2560,1440,1.25)):
        if state(page, 'ui_scale')['ui_scale'] != scale:
            control(page, text='Einstellungen / Info')
            control(page, text='UI ')
            control(page, name='nav-work')
        game_viewport(page, width, height)
        data = state(page, 'hz', 'labels')
        assert data['hz']['standard'] == 'Tidy Hand' and data['hz']['local_only'] and data['hz']['notice']
        assert all(label['text_fits'] for label in data['labels'])
        control(page, name='catalog-category')
        wait(page, 'picrossProbe.hz.menu.visible')
        menu = state(page, 'hz')['hz']['menu']
        assert menu['font'] == 'Tidy Hand'
        x, y = menu['position']; w, h = menu['size']
        assert x >= 0 and y >= 0 and x+w <= width and y+h <= height
        page.screenshot(path=str(output/f'{name}-hz-menu-{width}.png'))
        page.keyboard.press('Escape')
        wait(page, '!picrossProbe.hz.menu.visible')
        control(page, text='Einstellungen / Info')
        control(page, name='help-access')
        wait(page, 'picrossProbe.information')
        hz = state(page, 'hz')['hz']
        assert hz['help_font'] == 'Tidy Hand'
        rect = hz['help_rect']
        page.mouse.move(*point(page, [rect[0]+rect[2]/2, rect[1]+rect[3]/2]))
        page.mouse.wheel(0, 10000)
        wait(page, 'picrossProbe.hz.help_scroll > 0 || picrossProbe.hz.help_fits')
        page.screenshot(path=str(output/f'{name}-hz-help-{width}.png'))
        rows.append(dict(viewport=[width,height],ui_scale=scale,menu=menu,
                         help=state(page,'hz')['hz'],labels=data['labels']))
        control(page, name='nav-work')
        wait(page, 'picrossProbe.album')
    evidence['hz_text'] = rows
