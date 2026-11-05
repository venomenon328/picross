"""Package-selected CI. Originals are verified in the producing job, not archived by default."""
from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = '.ci/package.json'
FORMAT = 'development-ci-plan/v1'
NATIVE = ('core', 'history', 'catalog', 'completion', 'adapters', 'graphics', 'export')
PRODUCTION = ('solver', 'images', 'adapter', 'catalog')
MODULES = ('tools', 'preflight', 'delivery', *(f'native.{g}' for g in NATIVE),
           *(f'production.{g}' for g in PRODUCTION))
CORE_PATHS = {__file__.replace(str(ROOT) + '/', ''), 'tools/test_ci_modular.py',
              '.github/workflows/ci-modular.yml', 'tools/build_main_player.py'}
SOFT_SECONDS = 600


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Duplicate JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('Non-finite JSON number')))


def text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('Missing ' + name)
    return value


def selected_modules(value):
    if (not isinstance(value, list) or any(not isinstance(v, str) or v not in MODULES for v in value)
            or len(value) != len(set(value))):
        raise ValueError('Unknown or duplicate CI module')
    return [module for module in MODULES if module in value]


def validate_package(plan, changed, *, repository, today=None):
    if (not isinstance(plan, dict) or set(plan) != {'format', 'issue', 'package', 'modules', 'purpose',
            'omitted', 'test_changes', 'core_change', 'evidence'} or plan['format'] != FORMAT):
        raise ValueError('Missing or unsupported package plan')
    if not re.fullmatch(r'https://github\.com/' + re.escape(repository) + r'/issues/[1-9][0-9]*', plan['issue']):
        raise ValueError('Issue must belong to this repository')
    for name in ('package', 'purpose', 'omitted'):
        text(plan[name], name)
    selected_modules(plan['modules'])
    if CORE_PATHS.intersection(changed):
        text(plan['core_change'], 'reason for a core change')
    elif plan['core_change'] is not None and not isinstance(plan['core_change'], str):
        raise ValueError('Invalid core change')
    rows = plan['test_changes']
    if not isinstance(rows, list):
        raise ValueError('Missing test lifecycle decisions')
    seen = set()
    for row in rows:
        if (not isinstance(row, dict) or set(row) != {'path', 'disposition', 'reason'}
                or row['disposition'] not in {'core', 'change-scoped', 'temporary', 'remove'}):
            raise ValueError('Invalid test lifecycle decision')
        path = text(row['path'], 'test path')
        if path in seen or path not in changed:
            raise ValueError('Duplicate or unchanged lifecycle path: ' + path)
        seen.add(path)
        text(row['reason'], 'test purpose/retirement')
    required = {p for p in changed if re.search(r'(^|/)(test_[^/]+\.py|[^/]*_test\.py)$', p)
                or p.startswith('game/tests/')}
    if required - seen:
        raise ValueError('Missing lifecycle decisions: ' + ', '.join(sorted(required - seen)))
    evidence = plan['evidence']
    if not isinstance(evidence, dict) or set(evidence) != {'mode', 'purpose', 'expires'}:
        raise ValueError('Missing evidence lifecycle')
    if evidence['mode'] == 'none':
        if evidence['purpose'] is not None or evidence['expires'] is not None:
            raise ValueError('Unused evidence must not declare retention')
    elif evidence['mode'] in {'failure', 'review'}:
        text(evidence['purpose'], 'evidence recipient and purpose')
        expires = date.fromisoformat(text(evidence['expires'], 'evidence deadline'))
        if expires.isoformat() != evidence['expires'] or expires <= (today or date.today()):
            raise ValueError('Expired evidence request')
    else:
        raise ValueError('Unknown evidence mode')
    return plan


def git(*args, root=ROOT):
    return subprocess.check_output(['git', *args], cwd=root).decode('utf-8').strip()


def load_plan(base, head, event, *, modules='', repository='venomenon328/picross', root=ROOT):
    for sha in (base, head):
        if not re.fullmatch('[0-9a-f]{40}', sha):
            raise ValueError('A full base/head SHA is required')
    if event not in {'pull_request', 'push', 'workflow_dispatch'}:
        raise ValueError('Unsupported CI event')
    checkout = git('rev-parse', 'HEAD', root=root)
    if event == 'pull_request':
        # Read the PR head, never a working file or an inherited plan on main.
        raw = git('show', f'{head}:{PLAN_PATH}', root=root)
        previous = subprocess.run(['git', 'show', f'{base}:{PLAN_PATH}'], cwd=root,
                                  capture_output=True, text=True)
        if previous.returncode == 0 and raw == previous.stdout.strip():
            raise ValueError('Inherited package plan: update .ci/package.json for this PR')
        changed = git('diff', '--name-only', '--no-renames', base, head, root=root).splitlines()
        package = validate_package(strict_json(raw), changed, repository=repository)
        selected = selected_modules(package['modules'])
        if modules:
            raise ValueError('PR modules come exclusively from its package plan')
    else:
        if event == 'push' and modules:
            raise ValueError('Main push runs only the core')
        selected = selected_modules(modules.split(',') if modules else [])
        # A dispatch is an explicit selection, not permission to reuse old review uploads.
        package = {'package': 'manual' if event == 'workflow_dispatch' else 'main',
                   'purpose': 'Explicit module dispatch' if selected else 'Core integration',
                   'evidence': {'mode': 'none', 'purpose': None, 'expires': None}}
        raw = json.dumps(package, sort_keys=True)
    return {'format': 'development-ci-run/v1', 'source_head': head, 'base_commit': base,
            'tested_checkout': checkout, 'event': event, 'run_id': os.environ.get('GITHUB_RUN_ID', 'local'),
            'run_attempt': os.environ.get('GITHUB_RUN_ATTEMPT', '1'), 'modules': selected,
            'package': package, 'plan_sha256': hashlib.sha256(raw.encode()).hexdigest()}


def original_plan():
    event = os.environ.get('GITHUB_EVENT_NAME', '')
    payload = strict_json(Path(os.environ['GITHUB_EVENT_PATH']).read_text())
    repository = text(payload.get('repository', {}).get('full_name'), 'repository identity')
    if event == 'pull_request':
        base, head = payload['pull_request']['base']['sha'], payload['pull_request']['head']['sha']
        modules = ''
    else:
        head = os.environ['GITHUB_SHA']
        base = payload.get('before') or head
        if base == '0' * 40:
            base = head
        modules = payload.get('inputs', {}).get('modules', '') if event == 'workflow_dispatch' else ''
    if git('rev-parse', 'HEAD') != os.environ['GITHUB_SHA']:
        raise ValueError('Checkout differs from the original event SHA')
    if event == 'pull_request':
        parents = git('show', '-s', '--format=%P', 'HEAD').split()
        if parents != [base, head]:
            raise ValueError('Test merge does not bind the original base and head')
    return load_plan(base, head, event, modules=modules, repository=repository)


def summary(message):
    print(message, flush=True)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as stream:
            stream.write(message + '\n')


def command(args, name, work, rows):
    started = time.monotonic()
    log = work / (name + '.log')
    with log.open('w', encoding='utf-8') as stream:
        process = subprocess.Popen(args, cwd=ROOT, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, text=True, bufsize=1)
        try:
            for line in process.stdout:
                stream.write(line)
                print(line, end='', flush=True)
            result = process.wait()
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
    rows.append({'module': name, 'exit_code': result, 'seconds': round(time.monotonic() - started, 3)})
    if result:
        raise ValueError(f'{name} failed with exit {result}')


def legacy_binding(plan):
    import native_contract
    import production_contract
    native = [g for g in NATIVE if 'native.' + g in plan['modules']]
    production = [g for g in PRODUCTION if 'production.' + g in plan['modules']]
    return {**plan, 'native_groups': native, 'native_expected': native_contract.coverage(native),
            'production_groups': production, 'production_expected': production_contract.coverage(production)}


def copy_file(source, destination):
    if source.is_symlink() or not source.is_file():
        raise ValueError('Unsafe diagnostic file: ' + str(source))
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def extract_player(archive, destination):
    with zipfile.ZipFile(archive) as zipped:
        names = zipped.namelist()
        if len(names) != len(set(names)):
            raise ValueError('Duplicate player members')
        for info in zipped.infolist():
            path = PurePosixPath(info.filename)
            if (path.is_absolute() or '..' in path.parts or '\\' in info.filename
                    or (info.external_attr >> 16) & 0o170000 == 0o120000):
                raise ValueError('Unsafe player archive')
        # The native archive also contains its technical product report.
        # Reuse only runtime files, user guidance and licenses in the download.
        for info in zipped.infolist():
            if (info.filename in {'picross-p1.exe', 'picross-p1.console.exe',
                                  'picross-p1.pck', 'README.txt', 'SPIELANLEITUNG.md'}
                    or info.filename.startswith('licenses/')):
                zipped.extract(info, destination)
    required = ('picross-p1.exe', 'picross-p1.console.exe', 'picross-p1.pck')
    if not all((destination / p).is_file() and (destination / p).stat().st_size > 0 for p in required):
        raise ValueError('Missing or empty Windows player exports')


def retain_evidence(evidence, success, *, today=None):
    if evidence['mode'] == 'none':
        return False
    if date.fromisoformat(evidence['expires']) <= (today or date.today()):
        return False
    return evidence['mode'] == 'review' or not success


def execute(plan, output, cache):
    output.mkdir(parents=True, exist_ok=False)
    player, diagnostics = output / 'player', output / 'diagnostics'
    started, rows, success, error = time.monotonic(), [], False, None
    player_ready = False
    elapsed_before = max(0, time.time() - float(os.environ.get('CI_STARTED_AT', time.time())))
    warning = threading.Timer(max(0, SOFT_SECONDS - elapsed_before), lambda: print(
        '::warning::CI exceeded the 10 minute soft goal; verification continues.', flush=True))
    warning.daemon = True
    warning.start()
    package = plan['package']
    attempt = plan['run_attempt']
    os.environ.update(P1_PREFLIGHT_SOURCE_COMMIT=plan['source_head'], P1_BASE_COMMIT=plan['base_commit'],
                      RP1_SOURCE_HEAD=plan['source_head'], RP1_BASE_COMMIT=plan['base_commit'],
                      CI_SELECTION_ATTEMPT=attempt)
    try:
        with tempfile.TemporaryDirectory(prefix='picross-ci-', dir=output.parent) as temporary:
            work = Path(temporary)
            binding = legacy_binding(plan)
            try:
                # Build a playable package even when a requested test later fails.
                if 'native.export' not in plan['modules']:
                    command([sys.executable, 'tools/build_main_player.py', '--cache-dir', str(cache),
                             '--output-dir', str(player)], 'windows-player', work, rows)
                    player_ready = True
                if 'tools' in plan['modules']:
                    command([sys.executable, '-m', 'unittest', 'discover', '-s', 'tools', '-p', 'test_*.py', '-v'],
                            'tools', work, rows)
                if 'preflight' in plan['modules']:
                    command([sys.executable, 'tools/p1_preflight.py', '--cache-dir', str(cache),
                             '--output-dir', str(work / 'preflight')], 'preflight', work, rows)
                if binding['native_groups']:
                    command([sys.executable, 'tools/p1_product.py', '--cache-dir', str(cache),
                             '--output-dir', str(work / 'native'), '--groups', ','.join(binding['native_groups'])],
                            'native', work, rows)
                    from native_results import validate_all
                    validate_all(binding, work / 'native/technical', work / 'native', {'product_attempt': attempt}, attempt)
                    if 'export' in binding['native_groups']:
                        extract_player(work / 'native/picross-p1-windows-x86_64.zip', player)
                        player_ready = True
                if binding['production_groups']:
                    command([sys.executable, 'tools/production_ci.py', '--groups', ','.join(binding['production_groups']),
                             '--output-dir', str(work / 'production')], 'production', work, rows)
                    from production_results import validate_all
                    validate_all(binding, work / 'production', {'production_attempt': attempt}, attempt)
                if 'delivery' in plan['modules']:
                    command([sys.executable, 'tools/build_web_player.py', '--cache-dir', str(cache),
                             '--output-dir', str(work / 'web-player')], 'delivery-build', work, rows)
                    command([sys.executable, 'tools/web_tests/ssh_reference.py', '--build', str(work / 'web-player'),
                             '--output', str(work / 'delivery')], 'delivery', work, rows)
                if not player_ready or not player.is_dir():
                    raise ValueError('Mandatory Windows player missing')
                if git('status', '--porcelain') or git('rev-parse', 'HEAD') != plan['tested_checkout']:
                    raise ValueError('Tested sources changed during CI')
                success = True
            except Exception as exc:
                error = str(exc)
            finally:
                if retain_evidence(package['evidence'], success):
                    diagnostics.mkdir()
                    for log in work.glob('*.log'):
                        copy_file(log, diagnostics / log.name)
                    if (work / 'native/technical').exists():
                        from native_delivery import stage
                        from p1_evidence import source_identity
                        stage(work / 'native', diagnostics / 'native', 'success' if success else 'failure', source_identity(ROOT))
                    if (work / 'production/production-result.json').is_file():
                        from production_results import files
                        for row in files(work / 'production', staging=True):
                            copy_file(work / 'production' / row['file'], diagnostics / 'production' / row['file'])
                        copy_file(work / 'production/production-result.json', diagnostics / 'production/production-result.json')
                    (diagnostics / 'request.json').write_text(json.dumps(package['evidence'], indent=2) + '\n')
    except Exception as exc:
        success, error = False, str(exc)
    finally:
        warning.cancel()
        seconds = round(time.monotonic() - started, 3)
        def size(directory):
            return sum(p.stat().st_size for p in directory.rglob('*') if p.is_file()) if directory.exists() else 0
        report = {'accepted': success, 'binding': plan, 'modules': rows, 'seconds': seconds,
                  'ci_seconds_before_upload': round(elapsed_before + seconds, 3),
                  'soft_goal_exceeded': elapsed_before + seconds > SOFT_SECONDS, 'player_bytes': size(player),
                  'diagnostic_bytes': size(diagnostics), 'error': error}
        # Compact metadata is an Actions log/summary, not an additional artifact.
        summary('## Modular CI result\n\n```json\n' + json.dumps(report, indent=2) + '\n```')
        if os.environ.get('GITHUB_OUTPUT'):
            with open(os.environ['GITHUB_OUTPUT'], 'a') as stream:
                stream.write('player=' + str(player_ready).lower() + '\n')
                stream.write('diagnostics=' + str(diagnostics.is_dir()).lower() + '\n')
                if diagnostics.is_dir():
                    stream.write('retention=' + str(max(1, min(7, (date.fromisoformat(package['evidence']['expires']) - date.today()).days))) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['plan', 'run'])
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--cache-dir', type=Path)
    args = parser.parse_args()
    try:
        plan = original_plan()
        if args.action == 'plan':
            summary('## CI selection\n\n```json\n' + json.dumps(plan, indent=2) + '\n```')
            if os.environ.get('GITHUB_OUTPUT'):
                with open(os.environ['GITHUB_OUTPUT'], 'a') as stream:
                    for key, value in {'modules': ','.join(plan['modules']),
                                       'images': str(any(m == 'tools' or m.startswith(('native.', 'production.')) for m in plan['modules'])).lower(),
                                       'delivery': str('delivery' in plan['modules']).lower()}.items():
                        stream.write(key + '=' + value + '\n')
            return 0
        if not args.output_dir or not args.cache_dir:
            parser.error('run requires output and cache directories')
        return 0 if execute(plan, args.output_dir.resolve(), args.cache_dir.resolve())['accepted'] else 1
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        print('CI FAIL: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
