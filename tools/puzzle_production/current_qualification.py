"""Technical findings in the current PW publication. No standalone intake authority."""
from contextlib import contextmanager
from contextvars import ContextVar
from copy import deepcopy
from pathlib import PurePosixPath

from .authoring_package import require, sha
from .contract import digest, exact_keys

FORMAT = 'picross-candidate-qualification-v1'
_current = ContextVar('pw_qualification_operation', default=None)


def content_identity(value):
    if isinstance(value, list):
        return [content_identity(item) for item in value]
    if isinstance(value, dict):
        if {'file', 'bytes', 'sha256'} <= value.keys():
            return {'bytes': value['bytes'], 'sha256': value['sha256'], 'suffix': PurePosixPath(value['file']).suffix}
        return {k: content_identity(v) for k, v in value.items()}
    return value


def key(job, item, kind, inputs):
    return digest([FORMAT, job['puzzle_id'], job['operation'], job['test_only'], item['id'], kind, content_identity(inputs)])


def raster_key(job, raster):
    assets = {a['id']: a for a in job['assets']}
    return key(job, raster, 'raster', [
        {k: v for k, v in raster.items() if k not in ('label', 'review')}, job['parameters']['approved'],
        [assets[k]['file'] for k in (job['selected']['reveal'], job['selected']['motif']) if k in assets],
        [d.get('crop_protection') for d in job['decisions'] if d['scope'] == 'motif'], job['title']])


def inventory(job):
    result = {}
    for asset in job['assets']:
        if asset['role'] == 'input':
            continue
        result[key(job, asset, asset['role'], [asset['file'], asset.get('profile')])] = 'image'
        if asset.get('prepared'):
            result[key(job, asset, 'prepared', [asset['file'], asset['prepared']['file'], asset['profile']])] = 'prepared'
    for raster in job['rasters']:
        result[raster_key(job, raster)] = 'raster'
    return result


def validate(value):
    exact_keys(value, {'format', 'facts'})
    facts = value['facts']
    require(value['format'] == FORMAT and isinstance(facts, dict) and len(facts) <= 220, 'Invalid qualification inventory')
    for binding, result in facts.items():
        sha(binding)
        require(isinstance(result, dict), 'Invalid candidate qualification')
        kind = result.get('kind')
        if kind in ('image', 'prepared'):
            exact_keys(result, {'kind', 'width', 'height', 'mime', 'missing'})
            require(all(type(result[k]) in (int, float) and 0 < result[k] <= 8192 for k in ('width', 'height'))
                    and result['mime'] in ('image/png', 'image/jpeg', 'image/svg+xml', 'image/webp'), 'Invalid qualified image dimensions')
        else:
            exact_keys(result, {'kind', 'mode', 'diagnostics', 'legacy_preview', 'missing'})
            require(kind == 'raster' and result['mode'] in ('mono', 'color') and isinstance(result['diagnostics'], dict)
                    and type(result['legacy_preview']) is bool, 'Invalid qualified raster')
            diagnostics = result['diagnostics']
            require(set(diagnostics) <= {'frame', 'crop', 'qualification'}, 'Invalid qualified raster diagnostics')
            if 'qualification' in diagnostics:
                validate_raster(diagnostics['qualification'], result['missing'])
        require(isinstance(result['missing'], list) and all(isinstance(s, str) for s in result['missing']),
                'Invalid qualification findings')
    return value


def validate_raster(details, missing):
    exact_keys(details, {'logic_hash', 'certified', 'edges', 'palette_pairs', 'parameter_match'})
    sha(details['logic_hash'])
    exact_keys(details['edges'], {'left', 'right', 'top', 'bottom'})
    require(all(type(v) is bool for v in (*details['edges'].values(), details['certified'], details['parameter_match']))
            and (missing or details['certified'] and details['parameter_match']), 'Incomplete qualified proof or parameters')
    require(isinstance(details['palette_pairs'], list), 'Invalid qualified palette')
    for pair in details['palette_pairs']:
        exact_keys(pair, {'ids', 'distance_squared', 'status'})
        require(isinstance(pair['ids'], list) and len(pair['ids']) == 2 and
                type(pair['distance_squared']) is int and pair['distance_squared'] >= 0 and
                pair['status'] in ('positive', 'borderline', 'negative'), 'Invalid qualified palette pair')


def documented(row):
    return row['kind'] != 'raster' or 'qualification' in row['diagnostics']


@contextmanager
def operation():
    """Share only results obtained within this invocation or from its verified publication."""
    if _current.get() is not None:
        yield
        return
    token = _current.set({})
    try:
        yield
    finally:
        _current.reset(token)


def _published(record):
    # Called by the publisher after its independent work-ref, commit, release and
    # scope checks. A record supplied to Checked/build is never a seed.
    value = record.get('qualification')
    if value is not None and _current.get() is not None:
        rows = validate(value)['facts']
        require(inventory(record) == {k: v['kind'] for k, v in rows.items()}, 'Different published qualification inventory')
        _current.get().update({key: deepcopy(row) for key, row in rows.items() if documented(row)})
        for raster in record['rasters']:
            row = rows[raster_key(record, raster)]
            if documented(row):
                remember_raster_parts(raster, row)


def remember_raster_parts(raster, row):
    details = row['diagnostics']['qualification']
    definition = raster['definition']['sha256']
    if raster['proof'] and details['certified']:
        remember(('verified-proof', details['logic_hash'], raster['proof']['sha256']),
                 {'proof_verified': True, 'certified': True})
        remember(('end-matrix', definition, raster['proof']['sha256']), True)
    if raster['difficulty']:
        remember(('checked-rating', definition, raster['difficulty']['sha256']), True)
    remember(('raster-measurements', definition), (details['edges'], details['palette_pairs']))
    remember(('preview', definition, raster['preview']['sha256'], row['mode']), not row['legacy_preview'])


def lookup(binding):
    return deepcopy((_current.get() or {}).get(binding))


def active():
    return _current.get() is not None


def remember(binding, result):
    if _current.get() is not None:
        _current.get()[binding] = deepcopy(result)


def delivery_rating(value):
    """First-registration metadata derived from the exact qualified assessment."""
    return lookup(('first-rating', digest(value)))


def bind_delivery(definition_hash, value):
    if _current.get() is None or value is None:
        return
    active = {**value, 'rating_revision': 1}
    active['record_hash'] = digest({k: v for k, v in active.items() if k != 'record_hash'})
    remember(('first-rating', digest(value)), active)
    remember(('delivery', definition_hash, value['production_mode']), active)


def registered_rating(definition_hash, mode):
    return lookup(('delivery', definition_hash, mode))
