"""Fail-closed native evidence gate. Standard library only; verify delivered bytes."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import zipfile

from native_contract import GROUPS, SCOPES, WORKER_CHECKS, artifacts, checks, coverage


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
    if (not path.is_file() or not isinstance(row['bytes'], int) or row['bytes'] <= 0
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
        if 'log' in row:
            log = row['log']
            verify_file(directory/'logs', dict(file=log['file'], bytes=log['retained_bytes'], sha256=log['sha256']))
            if log['abbreviated'] or log['original_bytes'] != log['retained_bytes']:
                raise ValueError('Truncated native phase log')
            if row.get('required_marker') and row['required_marker'] not in (directory/'logs'/log['file']).read_text(encoding='utf-8'):
                raise ValueError('Missing native success marker')


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
    actual = sorted(p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p.name != 'native-result.json')
    if sorted(names) != actual or len(names) != len(set(names)):
        raise ValueError('Incomplete/duplicate/unexpected native delivered inventory')
    for row in inventory:
        verify_file(root, row)
    for group in groups:
        directory = root/group
        report = read(directory/'product-report.json')
        if report['status'] != 'success' or report['native_group'] != group or report['host'] != result['host']:
            raise ValueError('Wrong native group report')
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
        if group == 'catalog':
            costs = read(directory/'selected/kat2/image-costs.json')
            summary = read(directory/'selected/kat2/summary.json')
            if (costs['status'] != 'success' or summary['image_costs'] != costs
                    or costs['crops'] != len(summary['crops']) or costs['entries'] != summary['crops']
                    or {'kat2/'+r['file'] for r in costs['entries']} != {p for p in required if p.endswith('.png')}):
                raise ValueError('Incomplete native image costs/crops')
            if costs['comparison'] and any(r.get('identical') is not True for r in costs['entries']):
                raise ValueError('Native PNG comparison failed')
    if 'export' in groups:
        if player_root is None:
            raise ValueError('Selected export requires delivered player bytes')
        verify_file(player_root, result['player'])
        with zipfile.ZipFile(player_root/result['player']['file']) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)):
                raise ValueError('Duplicate player member')
            export = read(root/'export/product-report.json')
            for name, expected in export['export_files'].items():
                if not archive.read(name) or hashlib.sha256(archive.read(name)).hexdigest() != expected:
                    raise ValueError('Wrong delivered Windows export')
        audit = read(root/'export/player-audit.json')
        if audit['sha256'] != result['player']['sha256']:
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
