"""Closed approval corridor for regular fixed raster work (#596/C)."""
from .authoring_package import require, string
from .contract import digest, exact_keys, integer

FORMAT = 'picross-raster-parameters-v1'
IMPORT_KEYS = {'width', 'height', 'mode', 'foreground_colors', 'method', 'fit', 'actual_crop'}
SIDES = ('left', 'top', 'right', 'bottom')


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
        seen.add(digest(entry)); modes.add(entry['mode'])
        require(entry['mode'] in ('mono', 'color'), 'Invalid import mode')
        for axis in ('width', 'height'):
            integer(entry[axis], 1, 50, axis)
        integer(entry['foreground_colors'], 1 if entry['mode'] == 'mono' else 2,
                1 if entry['mode'] == 'mono' else 8, 'foreground colors')
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
            'foreground_colors': len({v for row in matrix for v in row} - {'empty'}),
            'method': next(v['method'] for v in design['variants'] if v['id'] == variant),
            'actual_crop': design['crop']}


def result(p, design, matrix):
    values = {'width': design['width'], 'height': design['height'],
              'foreground_colors': len({v for row in matrix for v in row} - {'empty'})}
    for axis in ('width', 'height'):
        integer(values[axis], 1, 50, axis)
    integer(values['foreground_colors'], 1 if design['mode'] == 'mono' else 2,
            1 if design['mode'] == 'mono' else 8, 'actual foreground colors')
    for key, c in p['constraints'].items():
        require(accepts(c, values[key]), 'Final raster outside constraint: ' + key)


def binding(approved, approval):
    require(isinstance(approved, list) and len(approved) == 1, 'New corridor requires exactly one approval object')
    p = validate(approved[0])
    require(digest(p) == digest(approval.get('parameters')), 'Motif approval corridor differs')
    return p
