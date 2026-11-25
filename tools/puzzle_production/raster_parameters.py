"""Closed approval corridor for regular fixed raster work (#596/C)."""
import math
from copy import deepcopy
from .authoring_package import require, string
from .contract import digest, exact_keys, integer

FORMAT = 'picross-raster-parameters-v1'
IMPORT_KEYS = {'width', 'height', 'mode', 'foreground_colors', 'method', 'fit', 'actual_crop'}
SIDES = ('left', 'top', 'right', 'bottom')


def require_color_count(mode, count):
    require(mode in ('mono', 'color'), 'Explicit production mode must be mono or color')
    if mode == 'mono':
        integer(count, 1, 1, 'Mono foreground color count')
    else:
        integer(count, 2, 8, 'Color foreground color count')


def used_foreground(matrix, empty=0):
    return {cell for row in matrix for cell in row if cell != empty}


def frame_edges(matrix):
    return dict(left=any(row[0] for row in matrix), right=any(row[-1] for row in matrix),
                top=any(matrix[0]), bottom=any(matrix[-1]))


def frame_failures(edges):
    return [axis for axis, sides in (('width', ('left', 'right')), ('height', ('top', 'bottom')))
            if not any(edges[side] for side in sides)]


def crop_rectangle(crop, width, height, mask, permitted, matrix, *, empty):
    require(isinstance(mask, list) and len(mask) == height and
            all(isinstance(row, list) and len(row) == width and all(type(v) is bool for v in row)
                for row in mask), 'Full boolean protection mask required')
    require(isinstance(crop, list) and len(crop) == 4, 'Cell crop must be one rectangle')
    for value in crop:
        integer(value, 0, 50, 'cell crop')
    left, top, right, bottom = crop
    require(0 <= left < right <= width and 0 <= top < bottom <= height, 'Invalid cell crop rectangle')
    removed = dict(zip(SIDES, (left, top, width - right, height - bottom)))
    require(all(not count or side in permitted for side, count in removed.items()), 'Unapproved empty-edge crop')
    for y, row in enumerate(matrix):
        for x, value in enumerate(row):
            if not (left <= x < right and top <= y < bottom):
                require(value == empty and not mask[y][x], 'Crop removes nonempty or protected reference cell')
    return removed


def edit_rectangle(matrix, mask, crop, edits, permissions, max_changes, colors, *, empty):
    """Apply the same original-coordinate checks to import and current definitions."""
    w, h = len(matrix[0]), len(matrix)
    crop_rectangle(crop, w, h, mask, permissions['empty_edge_crop'], matrix, empty=empty)
    l, t, r, b = crop
    require(isinstance(edits, list) and len(edits) <= max_changes, 'Fixed change budget exceeded')
    require(not edits or permissions['cell_edits'], 'Cell edits not approved')
    allowed = {empty, *colors}
    seen, result = set(), deepcopy(matrix)
    for edit in edits:
        exact_keys(edit, {'x', 'y', 'before', 'after'})
        x, y = integer(edit['x'], 0, w - 1, 'x'), integer(edit['y'], 0, h - 1, 'y')
        require((x, y) not in seen and l <= x < r and t <= y < b, 'Duplicate or cropped edit coordinate')
        seen.add((x, y))
        require(not mask[y][x], 'Protected cell edit')
        require(type(edit['before']) is type(empty) and type(edit['after']) is type(empty) and
                   edit['before'] == matrix[y][x] and edit['after'] in allowed and edit['after'] != edit['before'],
                   'Wrong before, palette value or no-op edit')
        result[y][x] = edit['after']
    return [row[l:r] for row in result[t:b]]


def constraint(value):
    c = exact_keys(value, {'kind', 'target', 'minimum', 'maximum'})
    require(c['kind'] in ('exact', 'approximate', 'open'), 'Unknown constraint kind')
    if c['kind'] == 'open':
        require(c['target'] is None, 'Open constraint has no target')
    else:
        integer(c['target'], 1, 50, 'constraint target')
    for key in ('minimum', 'maximum'):
        if c[key] is not None:
            integer(c[key], 1, 50, key)
    lo, hi = c['minimum'] or 1, c['maximum'] or 50
    require(lo <= hi and (c['target'] is None or lo <= c['target'] <= hi), 'Conflicting constraint bounds')
    return c


def accepts(c, value):
    return ((c['kind'] != 'exact' or value == c['target']) and
            (c['minimum'] is None or value >= c['minimum']) and
            (c['maximum'] is None or value <= c['maximum']))


def validate(value):
    p = exact_keys(value, {'format', 'constraints', 'imports', 'derivation'})
    require(p['format'] == FORMAT, 'Unsupported raster parameters')
    exact_keys(p['constraints'], {'width', 'height', 'foreground_colors'})
    for c in p['constraints'].values():
        constraint(c)
    imports = p['imports']
    require(isinstance(imports, list) and 1 <= len(imports) <= 8, 'Expected 1..8 explicit imports')
    seen, modes = set(), set()
    for entry in imports:
        exact_keys(entry, IMPORT_KEYS)
        require(digest(entry) not in seen, 'Duplicate import')
        seen.add(digest(entry))
        for axis in ('width', 'height'):
            integer(entry[axis], 1, 50, axis)
        require_color_count(entry['mode'], entry['foreground_colors'])
        modes.add(entry['mode'])
        for key, c in p['constraints'].items():
            require(accepts(c, entry[key]), 'Import outside constraint: ' + key)
        require(entry['method'] in ('area', 'contour') and entry['fit'] in ('exact', 'contain'), 'Invalid import method/fit')
        crop = entry['actual_crop']
        require(isinstance(crop, list) and len(crop) == 4, 'Invalid image crop')
        for n in crop:
            integer(n, 0, 8192, 'image crop')
        require(crop[0] < crop[2] and crop[1] < crop[3], 'Empty image crop')
    require(len(modes) == 1, 'Mixed modes in corridor')
    d = exact_keys(p['derivation'], {'cell_edits', 'empty_edge_crop', 'protected_features'})
    require(type(d['cell_edits']) is bool, 'Invalid cell edit permission')
    sides = d['empty_edge_crop']
    require(isinstance(sides, list) and all(s in SIDES for s in sides) and len(sides) == len(set(sides)), 'Invalid crop permissions')
    for axis, forbidden in (('width', {'left', 'right'}), ('height', {'top', 'bottom'})):
        require(p['constraints'][axis]['kind'] != 'exact' or not forbidden.intersection(sides), 'Exact axis forbids crop permission')
    require(isinstance(d['protected_features'], list) and len(d['protected_features']) <= 64, 'Invalid protected features')
    for feature in d['protected_features']:
        string(feature, 'protected feature')
    return p


def import_entry(design, matrix, variant):
    return {**{k: design[k] for k in ('width', 'height', 'mode', 'fit')},
            'foreground_colors': len(used_foreground(matrix, 'empty')),
            'method': next(v['method'] for v in design['variants'] if v['id'] == variant),
            'actual_crop': design['crop']}


def result(p, design, matrix, *, empty='empty'):
    values = {'width': design['width'], 'height': design['height'],
              'foreground_colors': len(used_foreground(matrix, empty))}
    for axis in ('width', 'height'):
        integer(values[axis], 1, 50, axis)
    require_color_count(design['mode'], values['foreground_colors'])
    for key, c in p['constraints'].items():
        require(accepts(c, values[key]), 'Final raster outside constraint: ' + key)


def binding(approved, approval):
    require(isinstance(approved, list) and len(approved) == 1, 'New corridor requires exactly one approval object')
    p = validate(approved[0])
    require(digest(p) == digest(approval.get('parameters')), 'Motif approval corridor differs')
    return p


def validate_search(config, width, height):
    c = exact_keys(config, {"max_changes", "max_steps", "max_candidates", "search_seconds",
                               "final_seconds", "search_lines", "final_lines", "seed", "order", "operators"})
    for name, low, high in (("max_changes", 0, width * height),
                            ("max_steps", 0, 1024), ("max_candidates", 1, 128),
                            ("search_lines", 0, 1_000_000), ("final_lines", 0, 1_000_000),
                            ("seed", 0, 2**32 - 1)):
        integer(c[name], low, high, name)
    for name, high in (("search_seconds", 600), ("final_seconds", 120)):
        require(type(c[name]) in (int, float) and math.isfinite(c[name]) and 0 <= c[name] <= high,
                f"{name} must be finite in 0..{high}")
    require(c["order"] == "seeded-frontier-v1" and c["operators"] == ["single-cell"],
            "Unsupported search order/operators")
    return c
