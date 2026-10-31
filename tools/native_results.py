"""Fail-closed native evidence gate. Standard library only; verify delivered bytes."""
import hashlib
import gzip
import json
from pathlib import Path, PurePosixPath
import re
import zipfile

from native_contract import GROUPS, SCOPES, WORKER_CHECKS, CATALOG_MODES, artifacts, checks, coverage


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key: '+key)
        result[key] = value
    return result


def read(path):
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique)


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
                         'kat2-adapter-register', 'kat2-imported-base-copies', 'kat2-image-processing', 'ea-image-processing', 'za1-test-only-registration',
                         'current-vs2-complete', 'retained-hc92-font-samples', 'current-drawing-pixel-oracles', 'isolated-book-study'}
        if ('log' in row) != (row['name'] not in python_checks):
            raise ValueError('Missing/unexpected native process log')
        if 'log' in row:
            log = row['log']
            verify_file(directory/'logs', dict(file=log['file'], bytes=log['retained_bytes'], sha256=log['sha256']))
            if log['abbreviated'] or log['original_bytes'] != log['retained_bytes']:
                raise ValueError('Truncated native phase log')
            if row.get('required_marker') and row['required_marker'] not in (directory/'logs'/log['file']).read_text(encoding='utf-8'):
                raise ValueError('Missing native success marker')


def validate_book_study(report, directory, identity, host):
    """Require B-A's original results, not just a successful enclosing Python call."""
    study = read(directory/'report.json')
    native = read(directory/'native.json')
    assertions = native.get('assertions', [])
    required_assertions = {'three independently moving leaves', 'actual catalog pointer selects correct ID',
                           'motion and blocked pointer input preserve cells/history/redo', 'presentation creates no save action',
                           'correct ID from page half 0', 'correct ID from page half 12',
                           'empty filter is immediate and reachable', 'sort is global and immediate',
                           'fresh actual pointer gesture works after interruption',
                           'solved puzzle opens directly without replay', 'ending reset opens same empty page without book animation'}
    for target in (0, 1):
        required_assertions.update(f'{label} {target}' for label in ('pointer starts catalog turn', 'filter and sort discarded during turn',
                                  'short catalog motion settles target', 'partial last spread', 'global ordering precedes pagination', 'edge action has no animation'))
    expected_interruptions = {(kind, phase, reason) for kind in ('page', 'open') for phase in ('prepare', 'motion')
                              for reason in ('resize', 'ui-scale', 'focus', 'leave')}
    for kind, phase, reason in expected_interruptions:
        required_assertions.update(f'{label} {kind}/{phase}/{reason}' for label in
                                   ('matrix stable target', 'matrix no history or save', 'matrix releases resources'))
    if (report.get('book_study') != study or study['package'] != 'B-A-N01-T01'
            or study['host'] != host or any(study.get(k) != v for k,v in identity.items())
            or native['checks'] != len(assertions) or native['failures'] != []
            or not all(a.get('passed') is True for a in assertions)
            or not required_assertions <= {a.get('label') for a in assertions}
            or {(r['kind'], r['phase'], r['reason']) for r in native['interruptions']} != expected_interruptions
            or len(native['interruptions']) != 16 or len(native['catalog_layouts']) != 3
            or any(len(r['cards']) != 24 for r in native['catalog_layouts'])
            or [(r['target'],r['direction'],r['seconds']) for r in native['page_motions']] != [(1,1,.85),(0,-1,.85)]
            or len(native['layouts']) != 3 or len(native['handoffs']) != 3
            or native['motion_wall_seconds_quiet'] < 3.0 or not native['motion_frame_ms_quiet']
            or native['resources']['ui_capture_targets'] != 0 or native['resources']['catalog_rgba_textures'] != 0
            or native['resources']['visible_leaves'] != 0 or native['resources']['moving_leaves'] != 3
            or study['material_source']['sha256'] != '957c2eab39b2334825fb159287b9d36a17b77fff1c628ea88110f2cfb5f7a71a'):
        raise ValueError('Incomplete/wrong isolated book study assertions or binding')
    movie = read(directory/'movie.json')
    if (movie['fps'] != 30 or movie['failures'] != [] or movie['final_state'] != 'WORK' or movie['final_id'] != 'T-06'
            or [(e['kind'], e['direction'], e['seconds']) for e in movie['events']] != [('page',1,.85),('page',-1,.85),('open',1,3.0)]
            or any(e['last_frame'] <= e['first_frame'] for e in movie['events'])):
        raise ValueError('Incomplete/incorrect book motion evidence')
    expected = ['book-version', 'book-import', 'book-native', 'book-movie', 'book-regular-import']
    for target in ('windows', 'web'):
        expected += ['book-regular-'+target+s for s in ('', '-content', '-isolation')]
    for target in ('windows', 'web'):
        expected += ['book-study-'+target+s for s in ('', '-pack')]
    if host == 'Windows': expected += ['book-windows-exported-motion']
    if ([p['name'] for p in study['phases']] != expected
            or any(p['exit_code'] != 0 or p['timed_out'] or p['seconds'] < 0 for p in study['phases'])
            or study['study_web_features'] != dict(renderer='gl_compatibility', threads=False, extensions=False, browser_probe='not requested')):
        raise ValueError('Incomplete/failed book study phases or Web feature contract')
    names = set(study['files'])
    actual = {p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file()} - {'report.json'}
    required = {'opening.avi', 'movie.json', 'movie-final.png', 'native.json', 'catalog.png', 'opening-middle.png', 'opening-back.png',
                'page-forward.png', 'page-backward.png', 'material-original-detail.png', 'material-study-detail.png',
                'windows/book-study.exe', 'windows/book-study.pck', 'web/index.html', 'web/index.pck', 'web/index.wasm'}
    required.update('logs/'+name+'.log' for name in expected)
    required.update(f'{kind}-{width}.png' for kind in ('baseline', 'handoff-texture', 'work', 'catalog') for width in (1280,1920,2560))
    if names != actual or not required <= names:
        raise ValueError('Missing/unexpected book study evidence inventory')
    for name, metadata in study['files'].items():
        verify_file(directory, dict(file=name, **metadata))
    pixels = study['handoff_pixels']
    if (set(pixels['samples']) != {f'work-{w}.png' for w in (1280,1920,2560)}
            or any(s['max_channel_delta'] > 4 or max(s['mean_channel_delta']) > .1 for s in pixels['samples'].values())
            or pixels['negative_controls'] != 'one-pixel displacement and alpha mutation rejected'):
        raise ValueError('Failed/incomplete book study handoff pixels or counterexamples')


def validate_catalog_images(costs, summary, required, direct_images):
    """Separate Python crops from unchanged images already emitted by KE natively."""
    expected_crops = [dict(file=Path(capture['file']).stem+'-'+name+'.png',
                           source=capture['file'], region=rectangle)
                      for report in summary['reports'] for capture in report['captures']
                      for name,rectangle in capture['regions'].items()]
    if (costs['status'] != 'success' or summary['image_costs'] != costs
            or costs['input_frames'] != sum(len(r['captures']) for r in summary['reports'])
            or costs['crops'] != len(expected_crops) or costs['entries'] != summary['crops']
            or [{k:r[k] for k in ('file','source','region')} for r in costs['entries']] != expected_crops
            or {'kat2/'+r['file'] for r in costs['entries']} | set(direct_images)
               != {p for p in required if p.endswith('.png')}):
        raise ValueError('Incomplete native image costs/crops')


def validate_payload(result, root, player_root=None):
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
    for group in groups:
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
            validate_book_study(report, directory/'book-study', result['identity'], result['host'])
        if group == 'graphics':
            worker = read(directory/'vs2-worker/technical/product-report.json')
            if worker['status'] != 'success' or any(worker.get(k) != v for k,v in result['identity'].items()):
                raise ValueError('Incomplete/wrong graphics worker')
            check_phases(worker, WORKER_CHECKS, directory/'vs2-worker/technical')
        required = set(artifacts(group))
        if group == 'completion':
            native = read(directory/'selected/ea/native.json')
            sequence = native['sequence']
            if len(sequence) < 10:
                raise ValueError('Incomplete actual EA motion sequence')
            indices = {min(range(len(sequence)), key=lambda i:abs(sequence[i]['seconds']-t)) for t in (0,.5,1.1,1.65,2.15)}
            required.update('ea/'+sequence[i]['file'] for i in indices)
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
            costs = read(directory/'selected/kat2/image-costs.json')
            summary = read(directory/'selected/kat2/summary.json')
            validate_catalog_images(costs, summary, required,
                                    read(Path(__file__).with_name('native_artifacts.json'))['catalog_direct_images'])
            if costs['comparison'] and any(r.get('identical') is not True for r in costs['entries']):
                raise ValueError('Native PNG comparison failed')
            for entry in costs['entries']:
                if (not re.fullmatch('[0-9a-f]{64}', entry['source_sha256']) or
                        len(entry['source_size']) != 2 or len(entry['region']) != 4):
                    raise ValueError('Missing native input frame/region binding')
                if costs['comparison'] and (entry['reference'] != entry['actual'] or
                        entry['actual']['size'] != [entry['region'][2]-entry['region'][0],entry['region'][3]-entry['region'][1]]):
                    raise ValueError('Native comparison dimensions/RGBA disagree')
            if summary['reports'] != [read(directory/'selected/kat2'/(mode+'.json')) for mode in
                                      CATALOG_MODES]:
                raise ValueError('Catalog original reports disagree with summary')
            if report['kat2'] != summary:
                raise ValueError('Catalog group/summary mismatch')
            from at_evidence import native
            native(directory/'selected/kat2', read(directory/'selected/kat2/at.json'), ('small','hover'))
        if group == 'completion':
            costs = read(directory/'selected/ea/image-costs.json')
            if report['ea']['image_costs'] != costs or costs['input_frames'] != len(sequence):
                raise ValueError('EA image timing/sequence mismatch')
            if report['ea']['reports'] != [read(directory/'selected/ea'/(mode+'.json')) for mode in ('native','restart')]:
                raise ValueError('EA group/original mismatch')
            from at_evidence import native
            native(directory/'selected/ea', read(directory/'selected/ea/native.json'), ('final','reopen','blend'))
    if 'export' in groups:
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
                if not archive.read(name) or hashlib.sha256(archive.read(name)).hexdigest() != expected:
                    raise ValueError('Wrong delivered Windows export')
            if json.loads(archive.read('product-report.json'), object_pairs_hook=unique) != export:
                raise ValueError('Player source/report differs from actual export report')
        audit = read(root/'export/player-audit.json')
        if (audit['sha256'] != result['player']['sha256'] or audit['bytes'] != result['player']['bytes']
                or audit['files'] != names
                or export['content_pack']['pack_sha256'] != export['export_files']['picross-p1.pck']
                or export['content_pack']['executable_sha256'] != export['export_files']['picross-p1.exe']):
            raise ValueError('Player packaging audit mismatch')
    elif 'player' in result:
        raise ValueError('Unselected export reported')
    return dict(groups=groups, files=len(inventory), bytes=sum(r['bytes'] for r in inventory))


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
