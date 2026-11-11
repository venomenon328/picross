"""Explicit production-actor writer: publishes only workspace.json, never HTTP."""
import argparse
from copy import deepcopy
import os
from pathlib import Path
import tempfile

from tools.puzzle_production import authoring_package as ap, catalog_io as io
from . import presentation as p
from .sources import LocalSource, Archive, JSON_LIMIT


def project(request, root):
    r = p.validate(request, measured=False)
    source = LocalSource(root)
    result = deepcopy(r)
    result['format'] = p.CURRENT_FORMAT if r['format'] == p.CURRENT_REQUEST else p.FORMAT
    for ref in [result['record'], *(o['record'] for o in result['offers'])]:
        raw = source.read(ref['commit'], ref['file'])
        ref.update(sha256=io.checksum(raw), bytes=len(raw))
    for a in result['assets']:
        loc = a['location']
        if loc['storage'] == 'repository':
            raw = source.read(loc['commit'], loc['file'], 32 * JSON_LIMIT)
        else:
            name = loc['container']
            archive_raw = source.read(loc['commit'], name, ap.MAX_ZIP)
            loc['container'] = {'file': name, 'sha256': io.checksum(archive_raw), 'bytes': len(archive_raw)}
            archive = Archive(archive_raw)
            try:
                raw = archive.read(loc['file'], 32 * JSON_LIMIT)
            finally:
                archive.close()
        loc.update(sha256=io.checksum(raw), bytes=len(raw))
    p.inspect(source, None, result)
    raw = p.data(result)
    ap.require(len(raw) <= JSON_LIMIT, 'Projektion überschreitet 1 MiB.')
    target_name = str(Path(r['record']['file']).with_name('workspace.json')).replace('\\', '/')
    target = io.safe(source.root, target_name)
    before = io.read(source.root, target_name, JSON_LIMIT, missing=True)
    source.recheck()
    if before is not None:
        ap.require(before == raw, 'Vorhandene fremde/abweichende Projektion wird nicht überschrieben.')
        return {'status': 'reused', 'file': target_name, 'sha256': io.checksum(raw), 'bytes': len(raw)}
    stage = None
    try:
        with tempfile.NamedTemporaryFile(prefix='.pw-projection-', dir=target.parent, delete=False) as stream:
            stage = Path(stream.name)
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        source.recheck()
        ap.require(io.safe(source.root, target_name) == target, 'Projektionsziel wurde geändert.')
        # Atomic no-replace publication on NTFS/POSIX, not replace/rename-overwrite.
        os.link(stage, target, follow_symlinks=False)
    except FileExistsError as exc:
        raise ap.InvalidInput('Projektionsziel wurde während der Veröffentlichung belegt.') from exc
    finally:
        if stage is not None:
            stage.unlink(missing_ok=True)
    return {'status': 'published', 'file': target_name, 'sha256': io.checksum(raw), 'bytes': len(raw)}


def automatic(root, directory, stage, index, *, overlay=None):
    """Build and validate the complete v2 view before a producer commits its record.

    The isolated stage overlays only the exact new revision. Old offers use the
    ordinary bounded source reader. No Git writes and no arbitrary directory scan.
    """
    from .sources import INDEX
    base = LocalSource(root)
    overlay = overlay or {}
    class View:
        def read(self, commit, name, limit=JSON_LIMIT, missing=False):
            if commit is None:
                if name in overlay:
                    raw = overlay[name]
                elif name == INDEX:
                    record = p.parse(io.read(stage, 'record.json', JSON_LIMIT))
                    row = {'puzzle_id': record['puzzle_id'], 'revision': record['revision'], 'record': directory + '/record.json'}
                    raw = p.data({**index, 'entries': [e for e in index['entries'] if e['record'] != row['record']] + [row]})
                elif name in (directory + '/record.json', directory + '/handoff.json', directory + '/package.zip'):
                    raw = io.read(stage, name.rsplit('/', 1)[1], limit)
                else:
                    return base.read(commit, name, limit, missing)
                ap.require(len(raw) <= limit, 'Projection source exceeds bound')
                return raw
            return base.read(commit, name, limit, missing)
    source = View()
    record = p.parse(source.read(None, directory + '/record.json'))
    own_ref = {'commit': None, 'file': directory + '/record.json'}
    offers = record['presentation']['raster_offers']
    refs = [own_ref, *(o['record'] for o in offers)]
    value = {'format': p.CURRENT_FORMAT, 'puzzle_id': record['puzzle_id'], 'revision': record['revision'],
             'record': {}, 'title': record['presentation']['title'], 'assets': [], 'offers': []}
    seen = set()
    for ref in refs:
        key = (ref['commit'], ref['file'])
        if key in seen:
            continue
        seen.add(key)
        ctx = p.Record(source, None, ref, record['puzzle_id'])
        measured = {**ref, 'sha256': io.checksum(ctx.raw), 'bytes': len(ctx.raw)}
        if ref == own_ref:
            value['record'] = measured
        for role, files in ctx.allowed.items():
            for name, sha in files.items():
                aid = 'asset-' + str(len(value['assets']) + 1)
                historical = next((loc for n, loc in ctx.historical_assets if n == name), None)
                if historical:
                    loc = deepcopy(historical)
                elif role == 'background' and ctx.value['background']['manifest']['storage'] == 'external':
                    loc = {'commit': ref['commit'], 'storage': 'repository', 'container': None,
                           'file': ctx.directory + '/' + name, 'sha256': sha}
                    loc['bytes'] = len(source.read(ref['commit'], loc['file'], 32 * JSON_LIMIT))
                else:
                    loc = {'commit': ref['commit'], 'storage': 'package', 'container': ctx.value['package'],
                           'file': name, 'sha256': sha, 'bytes': ctx.entries[name]['bytes']}
                caption = {'reveal': 'Abschlussbild', 'motif': 'Motivvorlage', 'background': 'Isolierte Kontextzeichnung',
                           'raster': 'Geprüftes Raster', 'raster_draft': 'Sichtungsentwurf'}[role]
                if role in ('raster', 'raster_draft') and ctx.value['width'] is not None:
                    caption += f" · {ctx.value['width']} × {ctx.value['height']} · " + ('Farbig' if ctx.value['mode'] == 'color' else 'Monochrom')
                if role == 'reveal':
                    caption = next((o['Beschreibung'] for o in ctx.value['reveal_options'] if o['Datei'] == name), caption)
                if role == 'background':
                    caption = ctx.background_labels.get(name, caption)
                value['assets'].append({'id': aid, 'role': role, 'caption': caption, 'location': loc})
                keys = [option for (kind, option), path in ctx.offer_keys.items() if kind == role and path == name]
                if role == 'raster':
                    chosen = [o for o in offers if o['record'] == ref]
                    # An empty list does not silently promote a draft; only a freshly
                    # qualified current raster has an automatically offered identity.
                    if not offers and ref == own_ref and ctx.value['state'] == 'raster_ready':
                        chosen = [{'id': keys[0], 'label': 'Raster ' + ctx.value['revision']}] if keys else []
                    for o in chosen:
                        value['offers'].append({'id': o['id'], 'kind': role, 'label': o['label'], 'record': measured, 'asset_ids': [aid]})
                elif ref == own_ref and role in ('reveal', 'background'):
                    for option in keys:
                        value['offers'].append({'id': option, 'kind': role, 'label': option, 'record': measured, 'asset_ids': [aid]})
        ctx.close()
    ap.require(all(any(o['id'] == offered['id'] and o['kind'] == 'raster' for o in value['offers']) for offered in offers),
               'Declared raster offer is not qualified')
    p.inspect(source, None, value)
    base.recheck()
    raw = p.data(value)
    ap.require(len(raw) <= JSON_LIMIT, 'Projection exceeds 1 MiB')
    return raw


def complete(root, record_path, commit):
    """Close only authoring metadata after an existing committed registration."""
    from tools.puzzle_production import authoring_builder as builder
    from .sources import INDEX, check_commit, production_path, git
    production_path(record_path); check_commit(commit)
    root = io.external(root)
    ap.require(git(root, 'merge-base', 'HEAD', commit).decode().strip() == commit, 'Registration is not in current history')
    with builder.writer(builder.git_root(root) / 'authoring-builder.lock'):
        source = LocalSource(root)
        before_raw = source.read(None, record_path)
        before = p.parse(before_raw)
        ap.require(before['format'] == 'picross-authoring-record-v3' and
                   before['state'] in ('editorially_approved', 'registered'), 'Completion requires actual final approval')
        after = deepcopy(before)
        if before['state'] != 'registered':
            binding = {'operation': 'register', 'commit': commit}
            for key, name in (('manifest', f"content/packages/{before['puzzle_id']}/{before['revision']}/manifest.json"),
                              ('registry', 'content/registry.json'), ('runtime', 'game/data/registry.json')):
                raw = source.read(commit, name, 8 * JSON_LIMIT)
                binding[key] = {'file': name, 'sha256': io.checksum(raw), 'bytes': len(raw)}
            after.update(state='registered', integration=binding, blockers=[],
                         next_step='5 · Lokal registriert; unabhängiges Review und Git-/Mainabschluss prüfen')
        ap.require(after['integration']['commit'] == commit, 'Completion belongs to another registration')
        p.registration(source, after)
        directory = record_path.rsplit('/', 1)[0]
        index = builder.index_value(source.read(None, INDEX, 8 * JSON_LIMIT))
        after_raw = p.data(after)
        projection = automatic(root, directory, root / directory, index, overlay={record_path: after_raw})
        projection_path = directory + '/workspace.json'
        previous = source.read(None, projection_path)
        # A restart may find the new record with the old derived view. Only its
        # own record references can be rebound; other foreign view bytes stop.
        old_view, new_view = p.parse(previous), p.parse(projection)
        for view in (old_view, new_view):
            for ref in [view['record'], *(o['record'] for o in view['offers'])]:
                if ref['commit'] is None and ref['file'] == record_path:
                    ref['sha256'], ref['bytes'] = '', 0
        ap.require(old_view == new_view, 'Completion would replace a foreign projection')
        source.recheck()
        with tempfile.TemporaryDirectory(prefix='.pw-completion-', dir=root / directory) as temporary:
            for name, raw, observed in ((record_path, after_raw, before_raw), (projection_path, projection, previous)):
                ap.require(io.read(root, name, JSON_LIMIT) == observed, 'Completion target changed')
                if raw != observed:
                    staged = Path(temporary) / Path(name).name
                    builder.write_new(staged, raw)
                    os.replace(staged, io.safe(root, name))
        return {'status': 'reused' if before_raw == after_raw and previous == projection else 'completed',
                'state': 'registered', 'record': record_path, 'integration_commit': commit}


def main(argv=None):
    parser = argparse.ArgumentParser(description='Geprüfte Produktionsansicht veröffentlichen')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--request', type=Path)
    group.add_argument('--complete-record')
    parser.add_argument('--integration-commit')
    parser.add_argument('--repository', required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.complete_record:
            result = complete(args.repository, args.complete_record, args.integration_commit)
        else:
            ap.require(args.integration_commit is None, 'Integration commit only belongs to completion')
            raw = io.read(args.request.absolute().parent, args.request.name, JSON_LIMIT)
            result = project(p.parse(raw), args.repository)
        print(p.data(result).decode(), end='')
        return 0
    except (ValueError, OSError, RuntimeError, KeyError, TypeError) as exc:
        print(p.data({'status': 'invalid_input', 'message': str(exc)}).decode(), end='')
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
