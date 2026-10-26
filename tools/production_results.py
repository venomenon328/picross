"""Verify actual Fachtest reports, selected scope and delivered bytes fail closed."""
import hashlib
import json
import math
from pathlib import Path
import re

import production_contract as contract

ROOT = Path(__file__).resolve().parents[1]


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate production JSON key: ' + key)
        result[key] = value
    return result


def read(path):
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique)


def checksum(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def files(root):
    if root.is_symlink() or any(p.is_symlink() for p in root.rglob('*')):
        raise ValueError('Linked production evidence')
    return [{'file': p.relative_to(root).as_posix(), 'bytes': p.stat().st_size, 'sha256': checksum(p)}
            for p in sorted(root.rglob('*')) if p.is_file()
            and p.name != 'production-result.json'
            and (not p.is_relative_to(root / 'za1-replay') or p == root / 'za1-replay/replay.json')]


def seconds(value):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ValueError('Invalid production duration')


def validate_tests(report, groups, root=ROOT):
    expected = contract.expected_tests(root, groups)
    if report.get('format') != 'picross-production-tests-v1' or report.get('accepted') is not True or report.get('groups') != groups:
        raise ValueError('Unsuccessful or incorrect production test scope')
    rows = report['tests']
    if (not isinstance(rows, list) or sorted(r['id'] for r in rows) != sorted(expected)
            or any(r['status'] != 'success' or r['group'] != expected[r['id']] for r in rows)):
        raise ValueError('Missing/duplicate/unknown/unsuccessful production tests')
    for row in rows + report['fixtures']:
        seconds(row['seconds'])
    seconds(report['seconds'])
    if report['top10'] != sorted(rows, key=lambda r: (-r['seconds'], r['id']))[:10]:
        raise ValueError('Incorrect slowest production tests')
    if set(report['group_times']) != set(groups):
        raise ValueError('Missing production group measurement')
    for group in groups:
        measured = report['group_times'][group]
        test_time = sum(r['seconds'] for r in rows if r['group'] == group)
        fixture_time = sum(r['seconds'] for r in report['fixtures'] if r['group'] == group)
        if (measured != dict(tests=sum(r['group'] == group for r in rows), test_seconds=test_time,
                             fixture_seconds=fixture_time, seconds=test_time + fixture_time)):
            raise ValueError('Production fixture/group time omitted')
    return len(expected)


def validate_all(plan, directory, outputs, gate_attempt, source_root=ROOT):
    groups = plan['production_groups']
    expected = contract.coverage(groups)
    if not groups or plan['production_expected'] != expected:
        raise ValueError('Missing production selection')
    report = read(directory / 'production-result.json')
    if (report.get('format') != 'picross-production-result-v1' or report.get('accepted') is not True
            or report.get('tests_accepted') is not True or report.get('groups') != groups or report.get('expected') != expected):
        raise ValueError('Incomplete/incorrect production result')
    binding = report['binding']
    for key in ('source_head', 'base_commit', 'tested_checkout', 'run_id'):
        if not plan.get(key) or binding.get(key) != plan[key]:
            raise ValueError('Mismatched production source/run: ' + key)
    attempt = outputs.get('production_attempt')
    if (set(outputs) != {'production_attempt'} or not isinstance(attempt, str)
            or not re.fullmatch('[1-9][0-9]*', attempt) or binding.get('run_attempt') != attempt
            or binding.get('selection_attempt') != plan['run_attempt']
            or not int(plan['run_attempt']) <= int(attempt) <= int(gate_attempt)):
        raise ValueError('Invalid production attempt binding')
    declared = report['files']
    required = {'tests.json', 'tests.log'}
    if 'solver' in groups:
        required |= {'references.log', 'references/benchmark.json'}
        required |= {'references/' + case + '/' + name for case in contract.REFERENCES for name in (
            'logic.json', 'proof.json', 'result.json', 'fresh-verification.json',
            'solve-metrics.json', 'verify-metrics.json', 'solve.log', 'verify.log')}
    if 'adapter' in groups:
        required |= {'za1-replay.log', 'za1-replay/replay.json'}
    if (not isinstance(declared, list) or not declared or declared != files(directory)
            or {r['file'] for r in declared} != required or any(r['bytes'] <= 0 for r in declared)):
        raise ValueError('Missing/empty/changed/duplicate production files')
    count = validate_tests(read(directory / 'tests.json'), groups, source_root)
    integrations = report['integrations']
    names = ['references'] if 'solver' in groups else []
    names += ['za1-replay'] if 'adapter' in groups else []
    if [r['name'] for r in integrations] != names or any(type(r['exit_code']) is not int or r['exit_code'] != 0 for r in integrations):
        raise ValueError('Missing/duplicate/failed production integration')
    for row in integrations:
        seconds(row['seconds'])
    if 'solver' in groups:
        reference = read(directory / 'references/benchmark.json')
        if (reference.get('accepted') is not True or reference.get('source_head') != binding['source_head']
                or reference.get('base_commit') != binding['base_commit'] or reference.get('checkout_commit') != binding['tested_checkout']
                or [c['name'] for c in reference['cases']] != list(contract.REFERENCES)
                or any(c.get('accepted') is not True for c in reference['cases'])):
            raise ValueError('Missing or unsuccessful independent solver references')
    if 'adapter' in groups:
        replay = read(directory / 'za1-replay/replay.json')
        ids = ['pz-test-direct-color', 'pz-test-direct-mono', 'pz-test-repair-color', 'pz-test-repair-mono']
        if (replay.get('accepted') is not True or [r['puzzle_id'] for r in replay['reports']] != ids
                or any(r.get('catalog_ready') is not True for r in replay['reports'])):
            raise ValueError('Missing or unsuccessful synthetic ZA-1 integration')
    seconds(report['seconds'])
    return {'groups': groups, 'tests': count, 'attempt': attempt, 'seconds': report['seconds']}
