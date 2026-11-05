"""Fail-closed native evidence gate. Standard library only; verify delivered bytes."""
import hashlib
import gzip
import json
import math
from pathlib import Path, PurePosixPath
import re
import zipfile
from contextlib import contextmanager
import shutil
import time

from native_contract import GROUPS, SCOPES, WORKER_CHECKS, CATALOG_MODES, CATALOG_CASES, artifacts, checks, coverage
from book_contract import SOURCES as BOOK_SOURCES, INTEGRATION_ASSERTIONS
def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key: '+key)
        result[key] = value
    return result


def read(path):
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique)


def validate_catalog_cases(report):
    """Read original native checkpoints and measured resize evidence, fail closed.

    Checkpoints attest execution, not replacement oracles for removed variants.
    File/source/run binding and original failures are checked by validate_payload.
    """
    mode = report['mode']
    if mode not in CATALOG_CASES:
        return
    rows = report.get('catalog_cases', [])
    if (not isinstance(rows, list) or any(not isinstance(r, dict) for r in rows)
            or [r.get('id') for r in rows] != list(CATALOG_CASES[mode])
            or any(set(r) != {'id', 'checks'} or type(r['checks']) is not int
                   or r['checks'] <= 0 for r in rows)
            or sum(r['checks'] for r in rows) != report['checks']
            or report.get('failures') != []):
        raise ValueError('Incomplete/failed selected catalog cases: '+mode)
    if mode != 'ke':
        return
    samples = report.get('resize_samples', [])
    keys = {'width', 'height', 'ui_scale', 'role', 'minimum_width', 'gap', 'available', 'columns'}
    if (not isinstance(samples, list) or len(samples) != 5
            or any(not isinstance(r, dict) or set(r) != keys for r in samples)):
        raise ValueError('Incomplete KE resize sample')
    for r in samples:
        if (any(type(r[k]) not in (int, float) or not math.isfinite(r[k]) or r[k] <= 0
                for k in keys-{'role'})
                or any(r[k] != int(r[k]) for k in ('width', 'height', 'columns'))
                or r['ui_scale'] != 1.25 or r['gap'] != 15
                or r['height'] != math.floor(r['width']*9/16+0.5)
                or r['columns'] != min(6, max(1, math.floor(
                    (r['available']+r['gap'])/(r['minimum_width']+r['gap']))))):
            raise ValueError('Invalid KE native resize geometry')
    middle, large, below, above = samples[1:]
    slope = (large['available']-middle['available'])/(2560-1920)
    if ([(r['width'], r['role']) for r in samples[:3]] !=
            [(1280, 'reference'), (1920, 'reference'), (2560, 'reference')]
            or (below['role'], above['role']) != ('below', 'above')
            or len({r['minimum_width'] for r in samples}) != 1 or slope <= 0):
        raise ValueError('Invalid KE resize reference/derivation')
    crossing = middle['width']+(2*large['minimum_width']+large['gap']-middle['available'])/slope
    if (below['width'] != math.floor(crossing)-8 or above['width'] != math.ceil(crossing)+8
            or (below['columns'], above['columns']) != (1, 2)
            or not 1280 <= below['width'] < above['width'] <= 2560):
        raise ValueError('KE sample does not cross derived native column boundary')


def safe(root, name):
    p = PurePosixPath(name)
    if (not name or p.is_absolute() or '..' in p.parts or '\\' in name or ':' in name
            or p.as_posix() != name or (root/name).is_symlink()
            or not (root/name).resolve().is_relative_to(root.resolve())):
        raise ValueError('Unsafe native evidence path')
    return root/name


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bind_files(root, exclude=(), only=None):
    return [dict(file=p.relative_to(root).as_posix(), bytes=p.stat().st_size, sha256=digest(p))
            for p in sorted(root.rglob('*')) if p.is_file() and p.relative_to(root).as_posix() not in exclude
            and (only is None or p.relative_to(root).as_posix() in only)]


def deduplicate_images(root):
    """Store identical original PNG bytes once, retaining each logical binding."""
    originals = {}
    aliases = []
    for row in bind_files(root, exclude={'native-result.json'}):
        if not row['file'].endswith('.png'):
            continue
        key = (row['sha256'],row['bytes'])
        if key in originals:
            source = originals[key]
            # Hash collisions never authorize discarding different original bytes.
            if safe(root,row['file']).read_bytes() != safe(root,source).read_bytes():
                raise ValueError('Different native images share a digest')
            aliases.append(dict(row, source=source))
            safe(root,row['file']).unlink()
        else:
            originals[key] = row['file']
    return aliases


def validate_image_alias(root, row, physical, names):
    """Check one binding without reconstructing or accepting a payload."""
    name, source = row['file'], row['source']
    safe(root, name)
    safe(root, source)
    if (set(row) != {'file','source','bytes','sha256'} or name in names
            or source not in physical or not name.endswith('.png') or not source.endswith('.png')
            or any(row[k] != physical[source][k] for k in ('bytes','sha256'))):
        raise ValueError('Invalid/duplicate/chained native image alias')
    verify_file(root, physical[source])


@contextmanager
def original_images(root, inventory, aliases):
    """Reconstruct exact original paths only during independent verification."""
    physical = {r['file']:r for r in inventory}
    if len(physical) != len(inventory):
        raise ValueError('Duplicate native physical inventory')
    names = set(physical)
    for row in aliases:
        validate_image_alias(root, row, physical, names)
        name = row['file']
        names.add(name)
    created = []
    try:
        for row in aliases:
            target = safe(root,row['file'])
            target.parent.mkdir(parents=True,exist_ok=True)
            # Refuse to overwrite any actual delivery (including unlisted files).
            with target.open('xb') as stream:
                created.append(target)
                with safe(root,row['source']).open('rb') as original:
                    shutil.copyfileobj(original,stream)
            verify_file(root,row)
        yield
    finally:
        for path in created:
            path.unlink()


def verify_file(root, row):
    path = safe(root, row['file'])
    if (not path.is_file() or type(row['bytes']) is not int or row['bytes'] <= 0
            or path.stat().st_size != row['bytes'] or digest(path) != row['sha256']):
        raise ValueError('Missing/empty/changed native evidence: '+row['file'])


def check_phases(report, expected, directory):
    rows = report['checks']
    if sorted(r['name'] for r in rows) != sorted(expected):
        raise ValueError('Missing/duplicate/unexpected native checks')
    for row in rows:
        if (row['status'] != 'success' or row.get('timed_out') or
                not isinstance(row.get('seconds'), (float, int)) or row['seconds'] < 0):
            raise ValueError('Unsuccessful/incomplete native phase')
        negative = row['name'] in ('expected-failure', 'rp6-t04-foreign-slot-control')
        expected_exit = 23 if row['name'] == 'expected-failure' else 4 if negative else 0
        if row.get('exit_code') != expected_exit or bool(row.get('expected_failure')) != negative:
            raise ValueError('Incorrect native process outcome')
        python_checks = {'current-resource-hashes', 'verified-toolchain-assets', 'current-atlas-resources', 'kat2-adapter-export',
                         'kat2-adapter-register', 'kat2-imported-base-copies', 'za1-test-only-registration',
                         'current-vs2-complete', 'current-drawing-pixel-oracles', 'regular-book-integration'}
        if ('log' in row) != (row['name'] not in python_checks):
            raise ValueError('Missing/unexpected native process log')
        if 'log' in row:
            log = row['log']
            verify_file(directory/'logs', dict(file=log['file'], bytes=log['retained_bytes'], sha256=log['sha256']))
            if log['abbreviated'] or log['original_bytes'] != log['retained_bytes']:
                raise ValueError('Truncated native phase log')
            if row.get('required_marker') and row['required_marker'] not in (directory/'logs'/log['file']).read_text(encoding='utf-8'):
                raise ValueError('Missing native success marker')


def validate_book_lifecycle(report, directory, identity, host):
    study = read(directory/'report.json')
    expected_phases = ['book-version', 'book-import', 'book-integration']
    expected_files = {'integration/integration.json'} | {'logs/'+name+'.log' for name in expected_phases}
    source_root = Path(__file__).resolve().parents[1]
    if (report.get('book_lifecycle') != study or study.get('package') != 'HIL-1-T01'
            or study.get('scope') != 'help-and-product-lifecycle' or study.get('host') != host
            or any(study.get(k) != v for k,v in identity.items())
            or set(study.get('sources', {})) != set(BOOK_SOURCES)
            or any(study['sources'][name] != hashlib.sha256((source_root/name).read_bytes()).hexdigest() for name in BOOK_SOURCES)
            or [p['name'] for p in study.get('phases', [])] != expected_phases
            or any(p['exit_code'] != 0 or p['timed_out'] or p['seconds'] < 0 for p in study['phases'])):
        raise ValueError('Incomplete/failed help and product lifecycle binding')
    actual = {p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file()} - {'report.json'}
    if set(study.get('files', {})) != expected_files or actual != expected_files:
        raise ValueError('Missing/unexpected targeted help evidence; no movie or gallery permitted')
    for name,metadata in study['files'].items():
        verify_file(directory, dict(file=name, **metadata))
    integration = read(directory/'integration/integration.json')
    if (integration.get('passed') is not True or not integration.get('assertions')
            or any(row.get('passed') is not True for row in integration['assertions'])
            or not INTEGRATION_ASSERTIONS <= {row.get('label') for row in integration['assertions']}):
        raise ValueError('Incomplete/failed targeted help assertions')
    cost = study.get('inventory_cost', {})
    if cost != dict(files=len(expected_files), bytes=sum(f['bytes'] for f in study['files'].values()),
                    pngs=0):
        raise ValueError('Incorrect targeted help inventory cost')


def validate_payload(result, root, player_root=None):
    began = time.monotonic()
    inventory = result['files']
    aliases = result.get('image_aliases', [])
    actual = sorted(p.relative_to(root).as_posix() for p in root.rglob('*')
                    if p.is_file() and p.relative_to(root).as_posix() != 'native-result.json')
    if sorted(r['file'] for r in inventory) != actual:
        raise ValueError('Incomplete/unexpected native physical inventory')
    reconstruction_began = time.monotonic()
    with original_images(root,inventory,aliases):
        reconstruction_seconds = time.monotonic()-reconstruction_began
        expanded = dict(result, files=inventory+[{k:v for k,v in row.items() if k!='source'} for row in aliases])
        context = {}
        try:
            summary = validate_original_payload(expanded, root, player_root, context)
        except (ValueError, OSError, KeyError, TypeError) as error:
            error.native_group = context.get('group')
            raise
    return dict(summary, files=len(inventory), bytes=sum(r['bytes'] for r in inventory),
                logical_files=len(inventory)+len(aliases), shared_original_pngs=len(aliases),
                reconstruction_seconds=round(reconstruction_seconds,6),
                total_validation_seconds=round(time.monotonic()-began,6))


def validate_original_payload(result, root, player_root=None, failure_context=None):
    failure_context = failure_context if failure_context is not None else {}
    groups = result['groups']
    if (result.get('format') != 'picross-native-result-v1' or result['status'] != 'success'
            or groups != [g for g in GROUPS if g in groups] or not groups
            or result['expected'] != coverage(groups)):
        raise ValueError('Invalid native selection/result')
    rows = result['results']
    if [r['group'] for r in rows] != groups or any(r['status'] != 'success' or r['exit_code'] != 0 for r in rows):
        raise ValueError('Missing/duplicate/failed native groups')
    inventory = result['files']
    names = [r['file'] for r in inventory]
    actual = sorted(p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p.relative_to(root).as_posix() != 'native-result.json')
    if sorted(names) != actual or len(names) != len(set(names)):
        raise ValueError('Incomplete/duplicate/unexpected native delivered inventory')
    for row in inventory:
        verify_file(root, row)
    isolation_roots = set()
    verification_times = {}
    for group in groups:
        failure_context['group'] = group
        group_began = time.monotonic()
        directory = root/group
        report = read(directory/'product-report.json')
        if report['status'] != 'success' or report['native_group'] != group or report['host'] != result['host']:
            raise ValueError('Wrong native group report')
        isolation = report['isolation']
        workspace = isolation['workspace'].replace('\\', '/')
        if not workspace or workspace in isolation_roots:
            raise ValueError('Shared native group workspace/profile')
        isolation_roots.add(workspace)
        profiles = isolation['profiles']
        expected_profiles = {'APPDATA','LOCALAPPDATA'} if result['host'] == 'Windows' else {'XDG_DATA_HOME','XDG_CONFIG_HOME','XDG_CACHE_HOME'}
        if set(profiles) != expected_profiles or any(not str(v).replace('\\','/').startswith(workspace+'/')
                                                   for v in [isolation['project'],*profiles.values()]):
            raise ValueError('Native project/profile escapes its isolated workspace')
        for key, value in result['identity'].items():
            if report.get(key) != value:
                raise ValueError('Native original report binding mismatch: '+key)
        enabled = set(SCOPES[group])
        if set(report['scope']) != {s for v in SCOPES.values() for s in v}:
            raise ValueError('Incomplete native scope declaration')
        for name, scope in report['scope'].items():
            if scope['enabled'] != (name in enabled) or scope['status'] != ('success' if name in enabled else 'not_applicable'):
                raise ValueError('Unselected/skipped scope misreported')
        check_phases(report, checks(group, result['host']), directory)
        if group == 'export':
            validate_book_lifecycle(report, directory/'book-lifecycle', result['identity'], result['host'])
        if group == 'graphics':
            import vs2_delivery
            worker = read(directory/'vs2-worker/technical/product-report.json')
            if worker['status'] != 'success' or any(worker.get(k) != v for k,v in result['identity'].items()):
                raise ValueError('Incomplete/wrong graphics worker')
            check_phases(worker, WORKER_CHECKS, directory/'vs2-worker/technical')
            from hn_evidence import verify as verify_hn
            hn = read(directory/'selected/hn192/hn-native.json')
            if report['visual']['vs2']['hn192'] != hn:
                raise ValueError('HN original/group report mismatch')
            verify_hn(directory/'selected/hn192', hn)
            # Re-read selected originals in the independent artifact gate.
            matrix = vs2_delivery.verify(directory/'selected/vs2-renders')
            for row in matrix['records']:
                vs2_delivery.vs2_v1_verify.record(row['v1'])
            if (report['visual']['vs2']['records'] != len(matrix['records'])
                    or report['visual']['vs2']['rendered'] != len(matrix['pictures'])
                    or report['visual']['vs2']['failures'] != matrix['failures']):
                raise ValueError('VS2 selected original/group report mismatch')
            render_reports = []
            for stage in ('layout','cells-f1','cells-f2','axis','h1'):
                original = read(directory/'selected/renders'/f'render-report-{stage}.json')
                vs2_delivery.verify_compact_stage(stage, original)
                render_reports.append(original)
            combined = vs2_delivery.compact_summary(render_reports)
            if (read(directory/'selected/renders/render-report.json') != combined
                    or report['visual']['compact'] != combined):
                raise ValueError('Compact render original/group report mismatch')
        required = set(artifacts(group))
        selected = report['selected_evidence']['files']
        if sorted(r['file'] for r in selected) != sorted(required) or report['selected_evidence']['omitted']:
            raise ValueError('Missing/duplicate/unexpected mandatory files for '+group)
        for row in selected:
            verify_file(directory/'selected', row)
        contracts = read(Path(__file__).with_name('native_artifacts.json'))['report_contracts']
        for name in required & contracts.keys():
            path = directory/'selected'/name
            data = json.loads(gzip.decompress(path.read_bytes()), object_pairs_hook=unique) if name.endswith('.gz') else read(path)
            for field, rule in contracts[name].items():
                if field not in data:
                    raise ValueError('Missing original native assertion field: '+name+'/'+field)
                value = data[field]
                accepted = (value == rule['equals'] if isinstance(rule,dict) else
                            type(value) is int and value > 0 if rule == 'positive-int' else
                            type(value) is int and value == 0 if rule == 'zero-int' else
                            value == [] if rule == 'empty-list' else value is False)
                if not accepted:
                    raise ValueError('Failed original native assertions: '+name+'/'+field)
        if group == 'history':
            summary = read(directory/'selected/integration/summary.json')
            from p14_integration import verify_evidence
            try:
                actual = verify_evidence(directory/'selected/integration')
                if report.get('integration') != summary or summary != actual:
                    raise AssertionError('summary disagrees with complete native evidence')
            except (AssertionError, KeyError, TypeError) as error:
                raise ValueError('Incomplete/inconsistent bounded native history evidence: '+str(error)) from error
        if group == 'catalog':
            reuse = read(directory/'selected/kat2/import-copies.json')
            copies = reuse['copies']
            if (reuse.get('base_unchanged') is not True or len(copies) != len(CATALOG_MODES)
                    or not re.fullmatch('[0-9a-f]{64}', reuse['base_sha256'])
                    or len({r['project'] for r in copies}) != len(CATALOG_MODES)
                    or any(r['base_sha256'] != reuse['base_sha256'] or r['files'] != reuse['base_files']
                           or r['bytes'] != reuse['base_bytes'] or r['seconds'] < 0
                           or not r['project'].replace('\\','/').startswith(workspace+'/kat2-') for r in copies)):
                raise ValueError('Incomplete/changed/shared catalog imported base copies')
            summary = read(directory/'selected/kat2/summary.json')
            if summary['reports'] != [read(directory/'selected/kat2'/(mode+'.json')) for mode in
                                      CATALOG_MODES]:
                raise ValueError('Catalog original reports disagree with summary')
            if report['kat2'] != summary:
                raise ValueError('Catalog group/summary mismatch')
            for mode in CATALOG_CASES:
                validate_catalog_cases(read(directory/'selected/kat2'/(mode+'.json')))
            from at_evidence import native
            native(directory/'selected/kat2', read(directory/'selected/kat2/at.json'), ('small','hover'))
        if group == 'completion':
            if report['ea']['reports'] != [read(directory/'selected/ea'/(mode+'.json')) for mode in ('native','restart')]:
                raise ValueError('EA group/original mismatch')
            from at_evidence import native
            native(directory/'selected/ea', read(directory/'selected/ea/native.json'), ('final','reopen','blend'))
        verification_times[group] = round(time.monotonic()-group_began,6)
    if 'export' in groups:
        failure_context['group'] = 'export'
        player_began = time.monotonic()
        if player_root is None:
            raise ValueError('Selected export requires delivered player bytes')
        verify_file(player_root, result['player'])
        with zipfile.ZipFile(player_root/result['player']['file']) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)):
                raise ValueError('Duplicate player member')
            export = read(root/'export/product-report.json')
            if set(export['export_files']) != {'picross-p1.exe','picross-p1.console.exe','picross-p1.pck'}:
                raise ValueError('Incomplete export file contract')
            for name, expected in export['export_files'].items():
                # Hash the actual decompressed member once. Reading it twice
                # doubled decompression/allocation of the large Windows binary.
                with archive.open(name) as stream:
                    hasher = hashlib.sha256()
                    size = 0
                    for chunk in iter(lambda:stream.read(1024*1024), b''):
                        hasher.update(chunk)
                        size += len(chunk)
                if not size or hasher.hexdigest() != expected:
                    raise ValueError('Wrong delivered Windows export')
            if json.loads(archive.read('product-report.json'), object_pairs_hook=unique) != export:
                raise ValueError('Player source/report differs from actual export report')
        audit = read(root/'export/player-audit.json')
        if (audit['sha256'] != result['player']['sha256'] or audit['bytes'] != result['player']['bytes']
                or audit['files'] != names
                or export['content_pack']['pack_sha256'] != export['export_files']['picross-p1.pck']
                or export['content_pack']['executable_sha256'] != export['export_files']['picross-p1.exe']):
            raise ValueError('Player packaging audit mismatch')
        verification_times['player_bytes'] = round(time.monotonic()-player_began,6)
    elif 'player' in result:
        raise ValueError('Unselected export reported')
    return dict(groups=groups, files=len(inventory), bytes=sum(r['bytes'] for r in inventory),
                verification_seconds=verification_times)


def validate_all(plan, root, player_root, outputs, gate_attempt):
    result = read(root/'native-result.json')
    identity = result['identity']
    for key, field in (('source_commit','source_head'), ('base_commit','base_commit'),
                       ('tested_checkout_commit','tested_checkout'), ('github_run_id','run_id'), ('github_event_name','event')):
        if not plan.get(field) or identity.get(key) != plan[field]:
            raise ValueError('Native source/run binding mismatch: '+key)
    attempt = outputs.get('product_attempt')
    attempts = [plan['run_attempt'], attempt, gate_attempt]
    if (any(not isinstance(v,str) or not re.fullmatch(r'[1-9][0-9]*',v) for v in attempts)
            or not int(attempts[0]) <= int(attempts[1]) <= int(attempts[2])
            or identity['github_run_attempt'] != attempt or result['selection_attempt'] != plan['run_attempt']):
        raise ValueError('Native producer/selection/gate attempt mismatch')
    if identity['source_tree_dirty'] is not False or result['groups'] != plan['native_groups'] or result['expected'] != plan['native_expected']:
        raise ValueError('Native actual selection/source mismatch')
    return dict(validate_payload(result, root, player_root), attempt=attempt)
