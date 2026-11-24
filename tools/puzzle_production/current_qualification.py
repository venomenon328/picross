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
        kind = result['kind']
        if kind in ('image', 'prepared'):
            exact_keys(result, {'kind', 'width', 'height', 'mime', 'missing'})
            require(all(type(result[k]) in (int, float) and 0 < result[k] <= 8192 for k in ('width', 'height'))
                    and isinstance(result['mime'], str), 'Invalid qualified image dimensions')
        else:
            exact_keys(result, {'kind', 'mode', 'diagnostics', 'legacy_preview', 'missing'})
            require(kind == 'raster' and result['mode'] in ('mono', 'color') and isinstance(result['diagnostics'], dict)
                    and type(result['legacy_preview']) is bool, 'Invalid qualified raster')
        require(isinstance(result['missing'], list) and all(isinstance(s, str) for s in result['missing']),
                'Invalid qualification findings')
    return value


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
        _current.get().update(deepcopy(rows))


def lookup(binding):
    return deepcopy((_current.get() or {}).get(binding))


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
