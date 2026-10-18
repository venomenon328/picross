"""Run independent native groups, retaining progressive evidence even on failure."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

from native_contract import GROUPS, coverage
from p1_evidence import source_identity, now


def requested(args):
    if args.groups is not None:
        groups = args.groups.split(',')
        if not groups or len(set(groups)) != len(groups) or any(g not in GROUPS for g in groups):
            raise ValueError('Expected unique native groups: '+','.join(GROUPS))
        return [g for g in GROUPS if g in groups]
    # Backwards-compatible manual defaults. The old integration flag widens to
    # history/catalog/completion; exact new groups can be chosen independently.
    groups = ['core', 'export']
    if args.integration:
        groups += ['history', 'catalog', 'completion']
    if args.pilots:
        groups += ['adapters']
    if args.visual or args.perf_b:
        groups += ['graphics']
    return [g for g in GROUPS if g in groups]


def run(args):
    from native_results import bind_files, validate_payload
    groups = requested(args)
    root = Path(__file__).resolve().parents[1]
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        raise ValueError('Output directory must be empty')
    technical = output / 'technical'
    technical.mkdir(parents=True)
    identity = source_identity(root)
    result = dict(format='picross-native-result-v1', status='running', identity=identity,
                  selection_attempt=os.environ.get('CI_SELECTION_ATTEMPT', identity['github_run_attempt']),
                  groups=groups, expected=coverage(groups), started_at=now(), results=[],
                  host=platform.system(), overlap='graphics on isolated Xvfb; other groups serial'
                  if platform.system() == 'Linux' else 'serial; native windows own focus')
    began = time.monotonic()
    path = technical / 'native-result.json'
    def flush():
        result['elapsed_seconds'] = round(time.monotonic()-began, 6)
        path.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    flush()

    def execute(group):
        start = time.monotonic()
        log = technical / (group+'-process.log')
        command = [sys.executable, str(root/'tools/p1_product.py'), '--native-group', group,
                   '--cache-dir', str(args.cache_dir.resolve()), '--output-dir', str(output/'groups'/group),
                   '--technical-dir', str(technical/group),
                   '--process-timeout-seconds', str(args.process_timeout_seconds),
                   '--download-timeout-seconds', str(args.download_timeout_seconds)]
        env = os.environ.copy()
        if args.compare_native_png:
            env['P1_COMPARE_NATIVE_PNG'] = '1'
        print('NATIVE GROUP START '+group, flush=True)
        with log.open('wb') as stream:
            completed = subprocess.run(command, env=env, stdout=stream, stderr=subprocess.STDOUT)
        print('NATIVE GROUP END '+group+' exit='+str(completed.returncode), flush=True)
        return dict(group=group, exit_code=completed.returncode,
                    status='success' if completed.returncode == 0 else 'failure',
                    seconds=round(time.monotonic()-start, 6))

    # Prime only the verified download cache via the first real group before
    # overlapping the independent graphics process. No imported project, profile
    # or result is shared. Do not race two initial archive downloads.
    serial = [g for g in groups if g != 'graphics']
    primed = False
    if serial:
        result['results'].append(execute(serial.pop(0)))
        primed = result['results'][-1]['status'] == 'success'
        flush()
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(execute, 'graphics') if 'graphics' in groups and platform.system() == 'Linux' and primed else None
        for group in serial:
            result['results'].append(execute(group))
            flush()
        if 'graphics' in groups:
            result['results'].append(future.result() if future else execute('graphics'))
            flush()
    result['results'].sort(key=lambda r: GROUPS.index(r['group']))
    result.update(status='success' if all(r['status'] == 'success' for r in result['results']) else 'failure',
                  finished_at=now(), files=bind_files(technical, exclude={'native-result.json'}))
    player = output/'groups/export/picross-p1-windows-x86_64.zip'
    if player.is_file():
        shutil.copyfile(player, output/player.name)
        result['player'] = bind_files(output, only={player.name})[0]
    try:
        validate_payload(result, technical, output if 'export' in groups else None)
    except (ValueError, OSError, KeyError, TypeError) as error:
        result.update(status='failure', validation_error=str(error))
        print('NATIVE EVIDENCE FAIL: '+str(error), flush=True)
    flush()
    print('NATIVE RESULT '+json.dumps({k:result[k] for k in ('status','groups','elapsed_seconds')}), flush=True)
    return 0 if result['status'] == 'success' else 1
