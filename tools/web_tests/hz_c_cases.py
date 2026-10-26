"""Current small-text observations; no screenshot matrix or state setters."""
from browser_actions import state


def typography(page, scale):
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
    return dict(ui_scale=scale, **data)
