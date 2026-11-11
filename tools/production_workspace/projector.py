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
    result['format'] = p.FORMAT
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


def main(argv=None):
    parser = argparse.ArgumentParser(description='Geprüfte Produktionsansicht veröffentlichen')
    parser.add_argument('--request', required=True, type=Path)
    parser.add_argument('--repository', required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        raw = io.read(args.request.absolute().parent, args.request.name, JSON_LIMIT)
        result = project(p.parse(raw), args.repository)
        print(p.data(result).decode(), end='')
        return 0
    except (ValueError, OSError, RuntimeError, KeyError, TypeError) as exc:
        print(p.data({'status': 'invalid_input', 'message': str(exc)}).decode(), end='')
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
