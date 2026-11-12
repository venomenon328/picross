"""Deterministic PB-A/PB-H package builder; no Git writes or approval creation."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import ctypes
from io import BytesIO
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import zipfile

from . import authoring_package as ap, catalog_io as io
from .authoring_build_contract import BACKGROUND_FORMAT, validate_request, validate_phase
from .contract import Aborted, InvalidInput, canonical_bytes, digest, exact_keys
from . import authoring_workflow as workflow

INDEX = 'content/authoring/index.json'
UNSAVED = 'storage: local working bytes; no verified Git backup commit'


class BuildError(InvalidInput):
    def __init__(self, message, remaining=None):
        super().__init__(message)
        self.remaining = remaining


def checkpoint(name):
    """Named publication boundaries for synthetic interruption/race tests."""
    io.tick()


def json_data(value):
    return canonical_bytes(value) + b'\n'


def write_new(path, raw):
    with path.open('xb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def mkdir(root, name):
    path = io.safe(root, name)
    path.mkdir(parents=True, exist_ok=True)
    ap.require(io.safe(root, name).is_dir(), 'Output parent is not a safe directory')
    return path


@contextmanager
def writer(lock):
    """Stable lock inode, released by OS on exit/kill; never delete a live lock."""
    lock = io.external(lock)
    with lock.open('a+b') as stream:
        if stream.seek(0, os.SEEK_END) == 0:
            stream.write(b'\0')
            stream.flush()
        stream.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise BuildError('Another authoring writer owns the publication lock') from exc
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == 'nt':
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def publish_directory(stage, target):
    """Atomic whole-directory publication, including no replacement of empty dirs."""
    if os.name == 'nt':
        os.rename(stage, target)  # Windows rename never replaces an existing target.
    elif sys.platform.startswith('linux'):
        libc = ctypes.CDLL(None, use_errno=True)
        rename = libc.renameat2
        rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        rename.restype = ctypes.c_int
        if rename(-100, os.fsencode(stage), -100, os.fsencode(target), 1):
            code = ctypes.get_errno()
            raise OSError(code, os.strerror(code), str(target))
    else:
        raise BuildError('No no-replace directory publication implementation on this platform')


def index_value(raw):
    value = io.json_bytes(raw, 8 * 1024 * 1024)
    exact_keys(value, {'format', 'entries'})
    ap.require(value['format'] == 'picross-authoring-index-v1' and isinstance(value['entries'], list), 'Invalid authoring index')
    paths = []
    for row in value['entries']:
        exact_keys(row, {'puzzle_id', 'revision', 'record'})
        ap.require(isinstance(row['puzzle_id'], str) and ap.ID.fullmatch(row['puzzle_id']) and
                   isinstance(row['revision'], str) and ap.REVISION.fullmatch(row['revision']), 'Invalid index identity')
        expected = f"content/authoring/{row['puzzle_id']}/{row['revision']}/record.json"
        ap.require(row['record'] == expected, 'Noncanonical index record path')
        paths.append(expected)
    from .authoring_build_contract import names
    names(paths)
    return value


def git_root(root):
    def git(*args):
        run = subprocess.run(['git', '-C', str(root), *args], capture_output=True, timeout=15)
        ap.require(run.returncode == 0, 'Repository publication requires a verified Git checkout')
        return run.stdout.decode('utf-8').strip()
    ap.require(io.external(git('rev-parse', '--show-toplevel')) == root, 'publish-to must be the checkout root')
    # A common Git directory keeps worktree writers cooperative without adding
    # lock files to the versioned authoring tree. These are read-only Git calls.
    return io.external(git('rev-parse', '--path-format=absolute', '--git-common-dir'))


def source_bytes(root, item):
    path = io.safe(root, item['source'])
    # A sealed package is a reading/derivation input, not a fresh build draft.
    for parent in (path.parent, *path.parents):
        if parent.is_relative_to(root):
            ap.require(not (parent / 'handoff.json').exists() and not (parent / 'inventory.json').exists(),
                       'Sealed source package cannot be resealed; use its existing bytes/ZA-1 derivation')
    raw = io.read(root, item['source'], ap.MAX_FILE)
    ap.require(len(raw) == item['bytes'] and io.checksum(raw) == item['sha256'],
               'Source size/hash changed: ' + item['source'])
    ap.require(not zipfile.is_zipfile(BytesIO(raw)), 'Embedded archive bytes are unsupported')
    return raw


def verify_sources(root, request):
    for item in [*request['files'], *request['external'].values()]:
        source_bytes(root, item)


def zip_payload(payload, destination, files):
    with zipfile.ZipFile(destination, 'x', compression=zipfile.ZIP_STORED, allowZip64=False) as archive:
        for name in sorted(files):
            io.tick()
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_STORED
            archive.writestr(info, io.read(payload, name, ap.MAX_FILE))
    ap.require(destination.stat().st_size <= ap.MAX_ZIP, 'Written ZIP exceeds ZA-1 limit')


def verify_zip(path, expected, handoff_raw, request, deadline, *, history_repo=None):
    io.tick()
    with ap.open_files(path, deadline=deadline) as (root, _, archive_hash):
        files = ap.file_table(root, deadline)
        ap.require(set(files) == set(expected), 'Written ZIP file set mismatch')
        for name, binding in expected.items():
            raw = io.read(root, name, ap.MAX_FILE)
            ap.require(len(raw) == binding['bytes'] and io.checksum(raw) == binding['sha256'],
                       'Written ZIP byte/hash mismatch: ' + name)
        ap.require(io.read(root, 'handoff.json', ap.MAX_FILE) == handoff_raw, 'Outer handoff copy differs')
        phase = validate_phase(root, request, deadline, history_repo=history_repo)
        background = getattr(phase, 'background', None)
    return {'archive_sha256': archive_hash, 'background': background}


def inspect_zip(path, external, state, deadline, *, allow_background=False, history_repo=None):
    if state != 'content_ready' and not (allow_background and state in ('raster_ready', 'background_review')):
        return None
    from .target_adapter import inspect
    options = ({'allow_background': True, 'history_repo': history_repo,
                'external_root': path.parent} if allow_background else {})
    with ap.open_package(path, allow_manual_review='manual-authorization.json' in external, **options) as package:
        package.deadline = min(package.deadline, deadline)
        report, design, matrix, _, approval = inspect(package,
            approval_path=external.get('approval.json'),
            manual_authorization=external.get('manual-authorization.json'),
            palette_exception=external.get('palette-exception.json'),
            **({'allow_background': True} if allow_background else {}))
    ap.require(report['technical'] and all(
        b == 'final_editorial: missing bound human final approval' or
        allow_background and state in ('raster_ready', 'background_review') and b.startswith('background')
        for b in report['blockers']), 'Written ZIP has unresolved content errors')
    # Only stable facts become identity bytes. Timings/check timestamps stay out
    # of the record, and are never reused as a substitute for a fresh inspection.
    result = {'format': report['format'], 'technical': True,
            'editorial_approved': report['editorial_approved'], 'blockers': report['blockers'],
            'width': design['width'], 'height': design['height'], 'mode': design['mode'],
            'used_colors': len({v for row in matrix for v in row if v != 'empty'}),
            'difficulty': report['difficulty']}
    if allow_background:
        background = approval['background'] if approval is not None else package.background
        result.update(original_state=state, effective_state=report['effective_state'],
                      integration_ready=False, background_ready=background['ready'])
        return result, background
    return result


def record_for(r, directory, package_raw, handoff_raw, inspection, background=None):
    h = r['handoff']
    current = workflow.is_current(h)
    blockers = list(dict.fromkeys([*h.get('blockers', []), *h.get('content_blockers', [])]))
    if inspection:
        # Original open choice/final gates remain historical in the handoff.
        # A valid supplied approval may resolve them in this new outer record.
        blockers = (list(inspection['blockers']) if background is not None else
                    list(dict.fromkeys([*blockers, *inspection['blockers']])))
    else:
        for kind, gate in (('reveal', 'reveal_approval'), ('motif', 'motif')):
            if not isinstance(h.get(kind), dict) or not h[kind].get('approval'):
                blockers.append(gate + ': human decision pending')
    if background is not None:
        blockers.extend(background['blockers'])
        if not current:
            blockers.append('integration: background integration requires HP-I1/HP-I2')
    blockers = list(dict.fromkeys([*blockers, UNSAVED]))
    def ref(name, raw):
        return {'file': directory + '/' + name, 'sha256': io.checksum(raw)}
    approval = r['external'].get('approval.json')
    state = inspection.get('effective_state', h['state']) if inspection else h['state']
    next_step = {'brief_ready': '1 · Abschlussbilder erzeugen',
                 'reveal_review': '2 · Bild freigeben & abstrahieren',
                 'motif_review': '3 · Motiv freigeben & produzieren',
                 'motif_approved': '3 · Rätsel produzieren',
                 'raster_review': 'Korrigieren oder Fehler beheben',
                 'raster_ready': '4 · Hintergrundbereitschaft klären und Rätsel abnehmen',
                 'background_review': workflow.NEXT['background_review'],
                 'content_ready': '4 · Abnehmen & ins Spiel integrieren',
                 'editorially_approved': 'Finale Integration nach verfügbarer HP-I1/HP-I2-Unterstützung'}[state]
    if background is not None and state == 'content_ready':
        next_step = '4 · Rätsel abnehmen; finale Hintergrundintegration benötigt HP-I1/HP-I2'
    record = {'format': 'picross-authoring-record-v2' if background is not None else 'picross-authoring-record-v1',
            'puzzle_id': h['puzzle_id'], 'revision': h['revision'],
            'state': state, 'category_id': r['category_id'], 'build_request_sha256': digest(r),
            'repo_commit': h['repo_commit'], 'document_revision': r['document_revision'], 'rulebook': h['rulebook'],
            'package': {**ref('package.zip', package_raw), 'bytes': len(package_raw)},
            'handoff': ref('handoff.json', handoff_raw), 'inventory_sha256': h['inventory']['sha256'],
            'final_editorial_approval': {'file': directory + '/approval.json', 'sha256': approval['sha256']} if approval else None,
            'width': inspection['width'] if inspection else None, 'height': inspection['height'] if inspection else None,
            'mode': inspection['mode'] if inspection else None, 'used_colors': inspection['used_colors'] if inspection else None,
            'difficulty': inspection['difficulty'] if inspection else None,
            'verification': inspection or {'technical': False, 'scope': 'phase file bindings only'},
            'blockers': blockers, 'next_action': h['next_action'], 'next_step': next_step,
            'integration': None, 'source_commit': None, 'pr': None,
            'reveal': h.get('reveal'), 'motif': h.get('motif'), 'reveal_options': r['reveal_options'],
            'parameters': h.get('approved_parameters') or h.get('proposed_parameters') or None}
    if background is not None:
        record['background'] = background['binding']
        if inspection is None:
            record['verification'] = {'technical': False, 'scope': 'phase and background file bindings only',
                                      'background_ready': background['ready'], 'integration_ready': False}
    if current:
        record.update(format=workflow.RECORD, raster_selection=h['raster_selection'],
                      presentation=r['presentation'], candidate=h.get('candidate'), next_step=workflow.NEXT[state])
    return record


def sheet_from_record(record, background=None):
    """Project the record and its freshly read bound manifest; no second state."""
    if record.get('format') == workflow.RECORD:
        return None
    ap.require(record.get('format') in ('picross-authoring-record-v1', 'picross-authoring-record-v2'),
               'Unsupported authoring record family for the current sheet; background change work uses its own CLI')
    def image(kind):
        value = record[kind]
        return (value['file'] + ' · SHA-256 ' + value['sha256']) if value and value.get('file') else None
    parameters = record['parameters']
    sheet = {'format': 'picross-cheatsheet-update-v2', 'Motiv': None,
            'Rasterbreite': record['width'], 'Rasterhöhe': record['height'], 'Größenvorgabe': 'Ungefähr',
            'Rätselmodus': {'mono': 'Monochrom', 'color': 'Farbig'}.get(record['mode'], 'KI empfiehlt'),
            'Farbanzahl': None, 'Farbvorgabe': 'Ungefähr', 'Verwendete Farben': record['used_colors'],
            'Rätsel-ID': record['puzzle_id'], 'Paketrevision': record['revision'], 'Paketpfad': record['package']['file'],
            'Abschlussbild': None if record['reveal_options'] else image('reveal'),
            'Abschlussbild-Optionen': record['reveal_options'], 'Rastervariante': None, 'Raster-Optionen': [],
            'Motivvorlage': image('motif'), 'Parameterkorridor': canonical_bytes(parameters).decode() if parameters else None,
            'Inventar-SHA-256': record['inventory_sha256'], 'Quellbranch / Commit': record['source_commit'],
            'PR': record['pr'], 'Produktionsstatus': record['state'], 'Nächster Schritt': record['next_step']}
    if record['format'] == 'picross-authoring-record-v2':
        ap.require(background is not None and background['binding'] == record['background'],
                   'Sheet v3 requires the verified background bound by this record')
        decision = background['decision']
        choice = (decision['candidate_id'] if background['status'] == 'selected' else
                  'none' if background['status'] == 'none' else None)
        sheet.update(format='picross-cheatsheet-update-v3', Hintergrunddaten=record['background'],
                     Hintergrundstatus=background['status'], Hintergrundauswahl=choice)
        sheet['Hintergrund-Optionen'] = background['options']
    return sheet


def same_revision(target, stage):
    ap.require(target.is_dir(), 'Revision collision: target is not a directory')
    expected = {p.name for p in stage.iterdir()}
    ap.require({p.name for p in target.iterdir()} == expected, 'Revision collision: file set changed')
    for name in sorted(expected):
        limit = ap.MAX_ZIP if name == 'package.zip' else ap.MAX_FILE
        ap.require(io.read(target, name, limit) == io.read(stage, name, limit), 'Revision collision: different bytes/plan: ' + name)


def verify_revision(target, expected):
    ap.require({p.name for p in target.iterdir()} == set(expected), 'Published revision file set changed')
    for name, binding in expected.items():
        raw = io.read(target, name, ap.MAX_ZIP if name == 'package.zip' else ap.MAX_FILE)
        ap.require(len(raw) == binding['bytes'] and io.checksum(raw) == binding['sha256'],
                   'Published revision changed: ' + name)


def build(request, source_root, output_root, publish_to=None, *, history_repo=None):
    remaining = None
    try:
        with io.budget(ap.SECONDS):
            deadline = time.monotonic() + ap.SECONDS
            r = validate_request(request)
            current = r['format'] == workflow.REQUEST
            background_enabled = r['format'] in (BACKGROUND_FORMAT, workflow.REQUEST)
            ap.require(not current or r['target'] == 'repository', '0.8.0 handoffs require repository publication')
            ap.require(background_enabled or history_repo is None, 'history-repo is only supported by build request v2')
            ap.require((r['target'] == 'repository') == (publish_to is not None), 'Request target and publish-to differ')
            sources, output = io.external(source_root), io.external(output_root)
            ap.require(sources.is_dir() and output.is_dir(), 'Source/output roots must exist')
            ap.require(not output.is_relative_to(sources) and not sources.is_relative_to(output), 'Source/output roots overlap')
            root = io.external(publish_to) if publish_to is not None else output
            gitdir = git_root(root) if publish_to is not None else None
            directory = (f"content/authoring/" if gitdir else '') + r['handoff']['puzzle_id'] + '/' + r['handoff']['revision']
            target = io.safe(root, directory)
            before = io.read(root, INDEX, 8 * 1024 * 1024) if gitdir else None
            index = index_value(before) if before is not None else None
            # Capture the index before the long validation, not only at commit.
            checkpoint('index-read')
            parent = mkdir(root, directory.rsplit('/', 1)[0])
            lock = gitdir / 'authoring-builder.lock' if gitdir else output / '.authoring-builder.lock'
            with writer(lock):
                if current:
                    from tools.production_workspace import current_view
                    view_before = current_view.observe(root, r['handoff']['puzzle_id'])
                if gitdir:
                    ap.require(io.read(root, INDEX, 8 * 1024 * 1024) == before, 'Index changed before writer acquisition')
                with tempfile.TemporaryDirectory(prefix='.pb-a-build-', dir=parent) as temporary:
                    work = Path(temporary)
                    write_new(work / 'owner.json', json_data({'purpose': 'PB-A unpublished build stage',
                              'pid': os.getpid(), 'started_unix': time.time(), 'target': str(target),
                              'request_sha256': digest(r)}))
                    payload, stage = work / 'payload', work / 'revision'
                    payload.mkdir()
                    stage.mkdir()
                    entries = []
                    for item in sorted(r['files'], key=lambda f: f['path']):
                        raw = source_bytes(sources, item)
                        path = io.safe(payload, item['path'])
                        path.parent.mkdir(parents=True, exist_ok=True)
                        write_new(path, raw)
                        entries.append({'path': item['path'], 'bytes': len(raw), 'sha256': io.checksum(raw)})
                    external = {}
                    for name, item in r['external'].items():
                        write_new(stage / name, source_bytes(sources, item))
                        external[name] = stage / name
                    # Draft validation precedes sealing; the copied inputs remain unchanged.
                    validate_phase(payload, r, deadline, history_repo=history_repo)
                    inv = json_data({'format': 'picross-authoring-file-inventory-v1',
                                     'puzzle_id': r['handoff']['puzzle_id'], 'revision': r['handoff']['revision'],
                                     'excludes': ['inventory.json', 'handoff.json'], 'files': entries})
                    write_new(payload / 'inventory.json', inv)
                    # Keep the request hash independent from the newly generated inventory.
                    request_hash = digest(r)
                    r['handoff']['inventory'] = {'file': 'inventory.json', 'sha256': io.checksum(inv)}
                    handoff = json_data(r['handoff'])
                    write_new(payload / 'handoff.json', handoff)
                    expected = {e['path']: {'bytes': e['bytes'], 'sha256': e['sha256']} for e in entries}
                    expected.update({name: {'bytes': len(raw), 'sha256': io.checksum(raw)}
                                     for name, raw in [('inventory.json', inv), ('handoff.json', handoff)]})
                    ap.require(sum(b['bytes'] for b in expected.values()) <= ap.MAX_TOTAL, 'Sealed package exceeds byte limit')
                    zip_payload(payload, stage / 'package.zip', expected)
                    write_new(stage / 'handoff.json', handoff)
                    checkpoint('zip-written')
                    verified = verify_zip(stage / 'package.zip', expected, handoff, r, deadline, history_repo=history_repo)
                    background = verified['background']
                    inspection = inspect_zip(stage / 'package.zip', external, r['handoff']['state'], deadline,
                        **({'allow_background': True, 'history_repo': history_repo} if background_enabled else {}))
                    if background_enabled and inspection is not None:
                        inspection, background = inspection
                    # External final approval has meaning only after the full adapter check.
                    ap.require(not external or inspection is not None, 'External authorizations require content_ready inspection')
                    package_raw = io.read(stage, 'package.zip', ap.MAX_ZIP)
                    record = record_for(r, directory, package_raw, handoff, inspection, background)
                    record['build_request_sha256'] = request_hash
                    write_new(stage / 'record.json', json_data(record))
                    if current:
                        from tools.production_workspace.projector import automatic
                        write_new(stage / 'workspace.json', automatic(root, directory, stage, index))
                    revision_files = {p.name: {'bytes': p.stat().st_size, 'sha256': ap.file_hash(p)}
                                      for p in sorted(stage.iterdir())}
                    checkpoint('before-publication')
                    verify_sources(sources, r)
                    if gitdir:
                        ap.require(io.read(root, INDEX, 8 * 1024 * 1024) == before, 'Index changed during build')
                    reused = target.exists()
                    if reused:
                        same_revision(io.safe(root, directory), stage)
                        verify_zip(target / 'package.zip', expected, handoff, r, deadline, history_repo=history_repo)
                    else:
                        publish_directory(stage, io.safe(root, directory))
                    remaining = str(target)
                    checkpoint('revision-published')
                    verify_revision(target, revision_files)
                    if gitdir:
                        ap.require(io.read(root, INDEX, 8 * 1024 * 1024) == before, 'Index conflict after complete revision publication')
                        row = {'puzzle_id': record['puzzle_id'], 'revision': record['revision'], 'record': directory + '/record.json'}
                        matches = [e for e in index['entries'] if e['record'].casefold() == row['record'].casefold()]
                        ap.require(not matches or matches == [row], 'Authoring index collision')
                        if not matches:
                            updated = json_data({**index, 'entries': [*index['entries'], row]})
                            replacement = work / 'index.json'
                            write_new(replacement, updated)
                            checkpoint('before-index-replace')
                            ap.require(io.read(root, INDEX, 8 * 1024 * 1024) == before, 'Concurrent index change')
                            os.replace(replacement, io.safe(root, INDEX))
                        ap.require(row in index_value(io.read(root, INDEX, 8 * 1024 * 1024))['entries'], 'Index publication not confirmed')
                    checkpoint('publication-verified')
                    # Check every sidecar as well as ZIP/record before and after
                    # indexing; never return a success for changed approval bytes.
                    verify_revision(target, revision_files)
                    if current:
                        current_view.publish(root, record['puzzle_id'], record['revision'], view_before)
                    return {'format': 'picross-authoring-build-result-v3' if current else 'picross-authoring-build-result-v2' if background_enabled else 'picross-authoring-build-result-v1',
                            'status': 'reused' if reused else 'built',
                            'directory': str(target), 'indexed': gitdir is not None, 'record': record,
                            'sheet': sheet_from_record(record, background), 'files': revision_files}
    except (InvalidInput, OSError, ValueError, Aborted, KeyboardInterrupt, MemoryError, RecursionError,
            subprocess.SubprocessError) as exc:
        error = BuildError(str(exc), remaining)
        if isinstance(exc, (Aborted, KeyboardInterrupt, MemoryError)):
            error.aborted = True
        raise error from exc


def finalize_background(request, source_root, output_root, *, history_repo=None):
    """Advance an existing outer record without rebuilding its sealed package."""
    from .authoring_finalization import finalize_background as finalize
    return finalize(request, source_root, output_root, history_repo=history_repo)


def main(argv=None):
    arguments = list(sys.argv[1:] if argv is None else argv)
    class FinalizerParser(argparse.ArgumentParser):
        def error(self, message):
            if arguments[:1] == ['finalize-background']:
                raise InvalidInput(message)
            super().error(message)
    parser = FinalizerParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    command = sub.add_parser('build')
    for option in ('request', 'source-root', 'output-root'):
        command.add_argument('--' + option, type=Path, required=True)
    command.add_argument('--publish-to', type=Path)
    command.add_argument('--history-repo', type=Path, help='Explicit local read-only Git history for PB-H discarded candidates')
    finalizer = sub.add_parser('finalize-background')
    for option in ('request', 'source-root', 'output-root'):
        finalizer.add_argument('--' + option, type=Path, required=True)
    finalizer.add_argument('--history-repo', type=Path, help='Explicit local read-only Git history for PB-H discarded candidates')
    try:
        args = parser.parse_args(arguments)
    except InvalidInput as exc:
        from .authoring_finalization import error_result
        print(canonical_bytes(error_result(exc)).decode('utf-8'))
        return 2
    request = None
    try:
        path = io.external(args.request)
        request = io.json_bytes(io.read(path.parent, path.name, 8 * 1024 * 1024), 8 * 1024 * 1024)
        if args.command == 'finalize-background':
            result = finalize_background(request, args.source_root, args.output_root, history_repo=args.history_repo)
            code = {'updated': 0, 'reused': 0, 'invalid_input': 2, 'conflict': 2,
                    'aborted': 4, 'technical_error': 5}[result['status']]
        else:
            result = build(request, args.source_root, args.output_root, args.publish_to, history_repo=args.history_repo)
            code = 0
    except (InvalidInput, OSError, ValueError, Aborted, KeyboardInterrupt) as exc:
        aborted = isinstance(exc, (Aborted, KeyboardInterrupt)) or getattr(exc, 'aborted', False)
        if args.command == 'finalize-background':
            from .authoring_finalization import error_result
            result = error_result(exc)
            code = {'invalid_input': 2, 'conflict': 2, 'aborted': 4, 'technical_error': 5}[result['status']]
        else:
            result = {'format': ('picross-authoring-build-result-v3' if isinstance(request, dict) and request.get('format') == workflow.REQUEST else
                                'picross-authoring-build-result-v2' if isinstance(request, dict) and request.get('format') == BACKGROUND_FORMAT
                                 else 'picross-authoring-build-result-v1'), 'status': 'aborted' if aborted else 'invalid_input',
                      'message': str(exc), 'remaining': getattr(exc, 'remaining', None),
                      'next_action': 'Inspect the retained complete revision/index; repeat the unchanged request after resolving the conflict.'}
            code = 4 if aborted else 2
    print(canonical_bytes(result).decode('utf-8'))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
