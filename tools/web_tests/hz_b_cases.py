"""HZ-B genuine Chromium pointer, keyboard and resize events."""
from browser_actions import control, wait, state, game_viewport, point, click


def select_view(page, index):
    # Pointer-opened menus need not initially focus their checked row.
    wait(page, 'picrossProbe.hz_b.view_popup')
    for _ in range(3):
        focused = state(page, 'hz_b')['hz_b']['view_focused']
        if focused == index:
            break
        page.keyboard.press('ArrowDown')
        wait(page, f'picrossProbe.hz_b.view_focused !== {focused}')
    assert state(page, 'hz_b')['hz_b']['view_focused'] == index
    page.keyboard.press('Enter')
    wait(page, f'!picrossProbe.hz_b.view_popup && picrossProbe.hz_b.view_selected === {index}')
