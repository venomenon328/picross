"""Fail-closed browser evidence validation, independent of Playwright."""
import json
import math
from pathlib import Path
import re

from web_tests.contract import BROWSERS, expected, require_browser, required_builds
from web_bundle import digest, safe_name, validate_manifest

BINDING = ('source_head', 'base_commit', 'tested_checkout', 'event', 'run_id', 'run_attempt', 'browser_request')


def read(path):
    from ci_scope import unique_object
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=unique_object)


def binding(plan):
    return {key: plan[key] for key in BINDING}


def attempt(value, minimum, maximum):
    if (not isinstance(value, str) or not re.fullmatch('[1-9][0-9]*', value)
            or not int(minimum) <= int(value) <= int(maximum)):
        raise ValueError('Invalid producer/selection/gate attempt ordering')


def file_record(path):
    return {'size': path.stat().st_size, 'sha256': digest(path)}


def validate_builds(envelope, plan, gate_attempt):
    if envelope.get('format') != 'picross-web-builds-v2' or envelope.get('binding') != binding(plan):
        raise ValueError('Build source/run binding mismatch')
    attempt(envelope.get('attempt'), plan['run_attempt'], gate_attempt)
    if set(envelope.get('builds', {})) != set(required_builds(plan['browser_groups'])):
        raise ValueError('Build inventory differs from the requested profile')
    for name, entry in envelope['builds'].items():
        manifest = validate_manifest(entry['manifest'], allow_test=name != 'web-player')
        if manifest['source_commit'] != plan['tested_checkout']:
            raise ValueError('Build uses another checkout')
        if manifest['kind'] != ('player' if name == 'web-player' else 'test'):
            raise ValueError('Wrong regular/technical build kind')
        if not re.fullmatch('[0-9a-f]{64}', entry.get('manifest_sha256', '')):
            raise ValueError('Missing manifest digest')
    if 'export' not in plan['browser_groups']:
        return
    first = envelope['builds']['web-test']['manifest']
    second = envelope['builds']['web-test-update']['manifest']
    if first['build_id'] == second['build_id'] or first['built_at'] == second['built_at']:
        raise ValueError('Update is not a distinct export')


def validate_browser(report, plan, browser, producer_attempt, gate_attempt, root):
    require_browser(browser)
    if report.get('format') != 'picross-browser-result-v2' or report.get('binding') != binding(plan):
        raise ValueError('Browser source/run/selection binding mismatch')
    if report.get('browser') != browser or report.get('attempt') != producer_attempt:
        raise ValueError('Wrong browser or producer attempt')
    attempt(producer_attempt, plan['run_attempt'], gate_attempt)
    groups = plan['browser_groups']
    required = plan['browser_expected'][browser]
    if report.get('expected') != required or report.get('status') != 'passed':
        raise ValueError('Missing/failed expected browser result')
    validate_builds(report['builds'], plan, producer_attempt)
    actual = report.get('groups')
    if not isinstance(actual, list) or len(actual) != len(groups):
        raise ValueError('Missing or extra groups')
    phases = report.get('phases')
    if (not isinstance(phases, list) or [p.get('group') for p in phases] != groups
            or any(type(p.get('exit_code')) is not int or p['exit_code'] != 0
                   or type(p.get('seconds')) not in (int, float)
                   or not math.isfinite(p['seconds']) or p['seconds'] < 0 for p in phases)):
        raise ValueError('Missing or unsuccessful group process')
    seen = set()
    required_files = set()
    for name in required_builds(groups):
        relative = 'manifests/'+name+'.json'
        required_files.add(relative)
        if (read(root/relative) != report['builds']['builds'][name]['manifest']
                or digest(root/relative) != report['builds']['builds'][name]['manifest_sha256']):
            raise ValueError('Delivered build manifest differs')
    for row in actual:
        group = row.get('group')
        if group not in groups or group in seen or row.get('status') != 'passed':
            raise ValueError('Missing, duplicate or unsuccessful group')
        seen.add(group)
        ids = row.get('scenarios')
        if (not isinstance(ids, list) or len(ids) != len(set(ids))
                or set(ids) != set(required[group])):
            raise ValueError('Missing, duplicate or unexpected scenarios')
        if row.get('browser') != browser or not row.get('graphics') or not row.get('timings'):
            raise ValueError('Missing actual browser/graphics/timing evidence')
        if (not isinstance(row.get('user_agent'), str) or not row['user_agent']
                or not isinstance(row.get('launch_options'), dict) or not row['launch_options']):
            raise ValueError('Missing browser identity/profile evidence')
        if group == 'regular' and row.get('errors') != []:
            raise ValueError('Missing or unsuccessful regular error check')
        if group == 'catalog' and not row.get('version'):
            raise ValueError('Missing catalog browser version')
        if group == 'input':
            viewports = row.get('viewports', [])
            if ([v.get('viewport') for v in viewports] != [[1280, 720], [1920, 1080]]
                    or any(v.get('fit') is not True or v.get('minimum') is not False for v in viewports)):
                raise ValueError('Missing viewport/fit evidence')
        if group == 'persistence':
            handoff = row.get('lock_handoff')
            if not isinstance(handoff, dict) or not handoff.get('held') or not handoff.get('pending'):
                raise ValueError('Missing lock-handoff evidence')
        if group == 'input' and row.get('dpi') != 1.5:
            raise ValueError('Missing live DPI evidence')
        if group == 'persistence':
            for key in ('reload', 'restart', 'retry'):
                if not isinstance(row.get(key), dict) or not row[key].get('history'):
                    raise ValueError('Missing actual persistence transition: '+key)
        timed = [t['scenario'] for t in row['timings'] if t['scenario'] != 'teardown-or-failure']
        if len(timed) != len(set(timed)) or set(timed) != set(ids):
            raise ValueError('Timing/scenario coverage mismatch')
        for measurement in row['timings']:
            if (type(measurement.get('seconds')) not in (int, float)
                    or not math.isfinite(measurement['seconds']) or measurement['seconds'] < 0
                    or not isinstance(measurement.get('operations'), dict)):
                raise ValueError('Invalid scenario measurement')
            if measurement['scenario'] != 'teardown-or-failure' and not measurement['operations']:
                raise ValueError('Empty scenario measurement')
            for operation in measurement['operations'].values():
                if (type(operation.get('calls')) is not int or operation['calls'] <= 0
                        or type(operation.get('bytes')) is not int or operation['bytes'] < 0
                        or type(operation.get('seconds')) not in (int, float)
                        or not math.isfinite(operation['seconds']) or operation['seconds'] < 0):
                    raise ValueError('Invalid operation measurement')
        raw = f'{group}/' + ('regular-report.json' if group == 'regular' else 'browser-report.json')
        required_files.add(raw)
        log = f'{group}/execution.log'
        required_files.add(log)
        execution = (root/log).read_text(encoding='utf-8')
        markers = re.findall(r'^'+re.escape(browser+' '+group)+r' PASS (\S+) ', execution, re.M) if group != 'regular' else re.findall(r'^PLAYER PASS '+re.escape(browser)+r'$', execution, re.M)
        if (markers != ids if group != 'regular' else len(markers) != 1):
            raise ValueError('Execution log does not confirm unique actual cases')
        original = read(root/raw)
        if original.get('results') != [row]:
            raise ValueError('Raw execution report differs from result')
        build_name = 'web-player' if group == 'regular' else 'web-test'
        if original.get('manifest') != report['builds']['builds'][build_name]['manifest']:
            raise ValueError('Raw report uses wrong build')
        if group != 'regular' and original.get('update_manifest') != (report['builds']['builds']['web-test-update']['manifest'] if group == 'export' else None):
            raise ValueError('Raw report uses wrong update build')
        if group in ('completion','export'):
            from at_evidence import browser as validate_at
            validate_at(root/group/group,row,report['builds']['builds'])
        for scenario in expected(browser, [group]):
            for suffix in scenario['images']:
                # Technical CLI stores group images under its own subdirectory.
                required_files.add(f'{group}/' + ('' if group == 'regular' else group+'/') + browser+'-'+suffix)
    files = report.get('files')
    if not isinstance(files, dict) or not required_files <= files.keys():
        raise ValueError('Missing mandatory evidence files')
    for name, record in files.items():
        if not safe_name(name):
            raise ValueError('Unsafe evidence path')
        path = root/name
        if path.is_symlink() or not path.is_file() or path.stat().st_size == 0 or file_record(path) != record:
            raise ValueError('Missing/empty/changed evidence: '+name)
    return {'browser': browser, 'attempt': producer_attempt, 'groups': groups,
            'scenarios': sum(len(ids) for ids in required.values()), 'status': 'passed'}


def validate_all(plan, root, outputs, gate_attempt):
    if set(outputs) != {browser+'_attempt' for browser in BROWSERS}:
        raise ValueError('Missing browser producer outputs')
    rows = []
    for browser in BROWSERS:
        directory = root/browser
        report = read(directory/'web-result.json')
        rows.append(validate_browser(report, plan, browser, outputs[browser+'_attempt'], gate_attempt, directory))
    return rows
