"""Small actor-owned current-view binding. No writer is exposed by HTTP."""
import os
from pathlib import Path
import tempfile

from tools.puzzle_production import authoring_package as ap, catalog_io as io
from tools.puzzle_production.contract import exact_keys, integer
from . import presentation as p
from .sources import INDEX, JSON_LIMIT, LocalSource

FORMAT = 'picross-production-current-view-v1'
LIMIT = 4096


def path(puzzle_id):
    ap.require(isinstance(puzzle_id, str) and ap.ID.fullmatch(puzzle_id), 'Invalid current-view ID')
    return f'content/authoring/{puzzle_id}/current-view.json'


def reference(name, raw):
    return {'file': name, 'sha256': io.checksum(raw), 'bytes': len(raw)}


def validate(raw, puzzle_id):
    ap.require(len(raw) <= LIMIT, 'Current-view exceeds 4 KiB')
    value = p.parse(raw, LIMIT)
    exact_keys(value, {'format', 'puzzle_id', 'revision', 'record', 'projection'})
    ap.require(value['format'] == FORMAT and value['puzzle_id'] == puzzle_id, 'Current-view identity/format differs')
    path(puzzle_id)
    revision = value['revision']
    ap.require(isinstance(revision, str) and ap.REVISION.fullmatch(revision), 'Invalid current-view revision')
    for key, leaf in (('record', 'record.json'), ('projection', 'workspace.json')):
        ref = exact_keys(value[key], {'file', 'sha256', 'bytes'})
        ap.require(ref['file'] == f'content/authoring/{puzzle_id}/{revision}/{leaf}', 'Foreign current-view path')
        ap.sha(ref['sha256'])
        integer(ref['bytes'], 1, JSON_LIMIT, 'Current-view bytes')
    ap.require(raw == p.data(value), 'Current-view must be canonical UTF-8 JSON')
    return value


def inspect(source, commit, raw, puzzle_id, *, originals=False):
    value = validate(raw, puzzle_id)
    from tools.puzzle_production.authoring_builder import index_value
    index = index_value(source.read(commit, INDEX, 8 * JSON_LIMIT))
    row = {'puzzle_id': puzzle_id, 'revision': value['revision'], 'record': value['record']['file']}
    ap.require(row in index['entries'], 'Current-view is not indexed')
    record_raw = p.bind(source.read(commit, value['record']['file']), value['record'])
    projection = p.validate(p.parse(p.bind(source.read(commit, value['projection']['file']), value['projection'])))
    record = p.parse(record_raw)
    ap.require(projection['format'] == p.CURRENT_FORMAT and record['format'] == 'picross-authoring-record-v3' and
               all(record[k] == projection[k] == value[k] for k in ('puzzle_id', 'revision')),
               'Current-view requires matching 0.8 originals')
    p.bind(record_raw, projection['record'])
    if originals:
        p.inspect(source, commit, projection)
    return value


def observe(root, puzzle_id):
    raw = io.read(root, path(puzzle_id), LIMIT, missing=True)
    if raw is not None:
        validate(raw, puzzle_id)
    return raw


def publish(root, puzzle_id, revision, expected, *, previous=None):
    """Caller holds the common authoring writer; compare again before replace.

    previous contains only producer-proven before bytes for an interrupted in-place
    transition. An arbitrary stale pointer cannot be repaired by this operation.
    """
    source = LocalSource(root)
    name = path(puzzle_id)
    ap.require(isinstance(revision, str) and ap.REVISION.fullmatch(revision), 'Invalid current-view revision')
    observed = source.read(None, name, LIMIT, missing=True)
    ap.require(observed == expected, 'Current-view changed during publication')
    if observed is not None:
        class Before:
            def read(self, commit, file, limit=JSON_LIMIT, missing=False):
                if commit is None and previous and file in previous:
                    return previous[file]
                return source.read(commit, file, limit, missing)
        try:
            inspect(source, None, observed, puzzle_id)
        except ValueError:
            ap.require(previous is not None, 'Stale current-view requires its original producer recovery')
            inspect(Before(), None, observed, puzzle_id)
    directory = f'content/authoring/{puzzle_id}/{revision}'
    value = {'format': FORMAT, 'puzzle_id': puzzle_id, 'revision': revision}
    for key, leaf in (('record', 'record.json'), ('projection', 'workspace.json')):
        file = directory + '/' + leaf
        value[key] = reference(file, source.read(None, file))
    raw = p.data(value)
    inspect(source, None, raw, puzzle_id, originals=True)
    source.recheck()
    if observed == raw:
        return {'status': 'reused', **reference(name, raw)}
    target, staged = io.safe(source.root, name), None
    try:
        with tempfile.NamedTemporaryFile(prefix='.pw-current-view-', dir=target.parent, delete=False) as stream:
            staged = Path(stream.name)
            stream.write(raw); stream.flush(); os.fsync(stream.fileno())
        checkpoint('before-current-view-replace')
        source.recheck()
        ap.require(io.read(source.root, name, LIMIT, missing=True) == expected, 'Concurrent current-view change')
        if expected is None:
            os.link(staged, target, follow_symlinks=False)
            staged.unlink()
        else:
            os.replace(staged, target)
        checkpoint('current-view-published')
        ap.require(io.read(source.root, name, LIMIT) == raw, 'Current-view publication not confirmed')
    finally:
        if staged is not None:
            staged.unlink(missing_ok=True)
    return {'status': 'published', **reference(name, raw)}


def checkpoint(name):
    io.tick()


def handoff(root, puzzle_id, revision):
    """Explicit recovery/publication for an already complete current revision."""
    from tools.puzzle_production import authoring_builder as builder
    root = io.external(root)
    with builder.writer(builder.git_root(root) / 'authoring-builder.lock'):
        return publish(root, puzzle_id, revision, observe(root, puzzle_id))
