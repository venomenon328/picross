"""Run exactly the selected Python Fachgruppen and their real integrations."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import production_contract as contract
from production_tests import run_tests


def binding():
    def git(*args):
        return subprocess.check_output(['git', *args], text=True).strip()
    return {'source_head': os.environ.get('RP1_SOURCE_HEAD') or git('rev-parse', 'HEAD'),
            'base_commit': os.environ.get('RP1_BASE_COMMIT') or git('rev-parse', 'HEAD'),
            'tested_checkout': git('rev-parse', 'HEAD'),
            'run_id': os.environ.get('GITHUB_RUN_ID'),
            'run_attempt': os.environ.get('GITHUB_RUN_ATTEMPT'),
            'selection_attempt': os.environ.get('CI_SELECTION_ATTEMPT'),
            'git_status': git('status', '--porcelain')}


def run(groups, directory):
    directory.mkdir(parents=True, exist_ok=False)
    report = {'format': 'picross-production-result-v1', 'groups': groups,
              'expected': contract.coverage(groups), 'binding': binding(),
              'accepted': False, 'integrations': []}
    if os.environ.get('GITHUB_ACTIONS') == 'true' and report['binding']['git_status']:
        raise ValueError('CI Fachtests require clean tested sources')
    started = time.perf_counter()
    try:
        tests = run_tests(groups, directory)
        report['tests_accepted'] = tests['accepted']
        for group, name, command in (
            ('solver', 'references', [sys.executable, '-m', 'tools.puzzle_production.benchmark',
                                      '--output-dir', str(directory / 'references')]),
            ('adapter', 'za1-replay', [sys.executable, '-m', 'tools.puzzle_production.za1_fixtures',
                                      '--output-dir', str(directory / 'za1-replay')]),
        ):
            if group not in groups:
                continue
            at = time.perf_counter()
            with (directory / (name + '.log')).open('w', encoding='utf-8') as log:
                log.write('Selected integration: ' + name + '\n'); log.flush()
                result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=600)
            report['integrations'].append({'name': name, 'group': group, 'exit_code': result.returncode,
                                           'seconds': time.perf_counter() - at})
        current = binding()
        report['source_unchanged'] = current == report['binding']
        report['accepted'] = tests['accepted'] and report['source_unchanged'] and all(r['exit_code'] == 0 for r in report['integrations'])
    except Exception as error:
        report['error'] = str(error)
        raise
    finally:
        report['seconds'] = time.perf_counter() - started
        # Only compact reports/logs and independently required proof inputs are
        # delivered. The synthetic mutable ZA checkout is never an artifact.
        from production_results import files
        report['files'] = files(directory)
        (directory / 'production-result.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
        if os.environ.get('GITHUB_STEP_SUMMARY'):
            with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as summary:
                summary.write('## Fachtests including setup and cleanup\n\n')
                if (directory / 'tests.json').is_file():
                    measured = json.loads((directory / 'tests.json').read_text(encoding='utf-8'))
                    summary.write('| Group | Tests | Tests including setUp/cleanup (s) | Class/module fixtures (s) | Total (s) |\n'
                                  '| --- | ---: | ---: | ---: | ---: |\n')
                    for group, row in measured['group_times'].items():
                        summary.write(f"| {group} | {row['tests']} | {row['test_seconds']:.3f} | {row['fixture_seconds']:.3f} | {row['seconds']:.3f} |\n")
                    summary.write('\nSlowest ten tests (including setUp, tearDown and cleanups):\n\n')
                    for row in measured['top10']:
                        summary.write(f"- {row['seconds']:.3f}s: `{row['id']}`\n")
                    summary.write('\nMeasured calls: `' + json.dumps(measured['calls'], sort_keys=True) + '`\n')
                summary.write(f"\nComplete Fachtest/integration runner: {report['seconds']:.3f}s; accepted={report['accepted']}.\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--groups', required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    report = run(contract.parse_groups(args.groups), args.output_dir)
    print(json.dumps(report))
    return 0 if report['accepted'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
