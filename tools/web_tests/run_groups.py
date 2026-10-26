"""Build provenance and real, independent selected-browser execution."""
import argparse
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ci_scope import evaluate, JOBS, validate_original_event
from web_bundle import validate, digest
from web_tests.contract import BROWSERS, require_browser
from web_tests.results import (BUILDS, binding, file_record, read, validate_builds,
                               validate_browser)


def write(path, data):
    path.write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8', newline='\n')


def check_current(plan):
    # Do not trust an arbitrary downloaded plan, even before the final gate.
    evaluate(plan, {job: {'result': 'success' if plan['selected'][job] else 'skipped'} for job in JOBS})
    validate_original_event(plan)
    if not plan['browser_request']:
        raise ValueError('Browser work was not explicitly requested')
    checkout = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    if checkout != plan['tested_checkout']:
        raise ValueError('Runner checkout differs from selected test merge')
    for key, env in [('run_id', 'GITHUB_RUN_ID'), ('event', 'GITHUB_EVENT_NAME'),
                     ('source_head', 'CI_HEAD'), ('base_commit', 'CI_BASE')]:
        if plan[key] != os.environ[env]:
            raise ValueError('Current event/source/run mismatch: '+key)


def seal(root, plan):
    envelope = dict(format='picross-web-builds-v1', binding=binding(plan),
                    attempt=os.environ['GITHUB_RUN_ATTEMPT'], builds={})
    for name in BUILDS:
        manifest = validate(root/name, allow_test=name != 'web-player')
        envelope['builds'][name] = dict(manifest=manifest,
                                        manifest_sha256=digest(root/name/'build-manifest.json'))
    validate_builds(envelope, plan, os.environ['GITHUB_RUN_ATTEMPT'])
    write(root/'builds.json', envelope)


def run(args, plan):
    require_browser(args.browser)
    build_root = args.build_root
    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    envelope = read(build_root/'builds.json')
    validate_builds(envelope, plan, os.environ['GITHUB_RUN_ATTEMPT'])
    if envelope['attempt'] != args.build_attempt:
        raise ValueError('Downloaded build attempt differs from scheduler')
    for name in BUILDS:
        if (validate(build_root/name, allow_test=name != 'web-player') != envelope['builds'][name]['manifest']
                or digest(build_root/name/'build-manifest.json') != envelope['builds'][name]['manifest_sha256']):
            raise ValueError('Downloaded bundle differs from sealed build')
    (output/'manifests').mkdir(exist_ok=True)
    for name in BUILDS:
        shutil.copyfile(build_root/name/'build-manifest.json', output/'manifests'/(name+'.json'))
    report = dict(format='picross-browser-result-v1', binding=binding(plan),
                  attempt=os.environ['GITHUB_RUN_ATTEMPT'], browser=args.browser,
                  expected=plan['browser_expected'][args.browser], status='failed',
                  builds=envelope, groups=[], files={}, phases=[],
                  environment=dict(platform=platform.platform(), runner=os.environ.get('RUNNER_OS'),
                                   image=os.environ.get('ImageOS'), image_version=os.environ.get('ImageVersion'),
                                   playwright='1.58.0', software=os.environ.get('PICROSS_WEB_SOFTWARE'),
                                   profiles='new empty profile and loopback host per group',
                                   build_cache='download archives only; no browser results cached'))
    failures = []
    try:
        for group in plan['browser_groups']:
            directory = output/group
            directory.mkdir()
            command = [sys.executable, str(Path(__file__).with_name('smoke.py' if group == 'regular' else 'browser.py')),
                       '--browser', args.browser, '--output', str(directory),
                       '--build', str(build_root/('web-player' if group == 'regular' else 'web-test'))]
            if group != 'regular':
                command += ['--update-build', str(build_root/'web-test-update'), '--groups', group]
            began = time.monotonic()
            # Execute each selection from scratch even after another group fails.
            with (directory/'execution.log').open('w', encoding='utf-8') as stream:
                result = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT)
            report['phases'].append(dict(group=group, seconds=round(time.monotonic()-began, 6), exit_code=result.returncode))
            raw = directory/('regular-report.json' if group == 'regular' else 'browser-report.json')
            if raw.is_file():
                report['groups'].extend(read(raw)['results'])
            if result.returncode:
                failures.append(group)
                print((directory/'execution.log').read_text(encoding='utf-8'), flush=True)
            print('GROUP RESULT', args.browser, group, report['phases'][-1], flush=True)
        report['files'] = {p.relative_to(output).as_posix(): file_record(p)
                           for p in sorted(output.rglob('*')) if p.is_file() and p.name != 'web-result.json'}
        if failures:
            raise ValueError('Failed browser groups: '+','.join(failures))
        report['status'] = 'passed'
        validate_browser(report, plan, args.browser, report['attempt'], report['attempt'], output)
    except Exception as error:
        report['status'] = 'failed'
        report['error'] = str(error)
        raise
    finally:
        write(output/'web-result.json', report)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['check', 'seal', 'run'])
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--build-root', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--browser', choices=BROWSERS)
    parser.add_argument('--build-attempt')
    args = parser.parse_args()
    plan = read(args.plan)
    check_current(plan)
    if args.command == 'check':
        return
    if args.command == 'seal':
        seal(args.build_root, plan)
    else:
        if not args.output or not args.browser or not args.build_attempt:
            parser.error('run requires output, browser and build-attempt')
        run(args, plan)


if __name__ == '__main__':
    main()
