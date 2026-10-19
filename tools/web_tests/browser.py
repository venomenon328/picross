"""Run independently initialized technical groups against genuine exports."""
from __future__ import annotations
import argparse
import importlib
import json
from pathlib import Path
import platform
import shutil
import tempfile
import time
import browser_actions
from browser_runtime import options, launch
from contract import GROUPS, BROWSERS, expected
from serve import serve
import timing


class Session:
    def __init__(self, pw, browser, profile, evidence):
        self.pw, self.browser, self.profile, self.evidence = pw, browser, profile, evidence
        self.contexts = []
        self.began = time.monotonic()

    def launch(self, scale=1):
        context = launch(self.pw, self.browser, self.profile, viewport={'width':1920,'height':1122},
            device_scale_factor=scale)
        self.contexts.append(context)
        return context

    def passed(self, label):
        scenarios = expected(self.browser, [self.evidence['group']])
        matches = [row for row in scenarios if row['label'] == label]
        if len(matches) != 1 or matches[0]['id'] in self.evidence['scenarios']:
            raise ValueError('Unexpected or duplicate assertion: ' + label)
        self.evidence['scenarios'].append(matches[0]['id'])
        self.evidence['timings'].append(timing.CURRENT.checkpoint(matches[0]['id']))
        print(self.browser, self.evidence['group'], 'PASS', matches[0]['id'], label, flush=True)

    def close(self):
        for context in reversed(self.contexts):
            context.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--update-build', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--browser', choices=BROWSERS, default='chromium')
    parser.add_argument('--groups', default=','.join(GROUPS[1:]))
    args = parser.parse_args()
    groups = args.groups.split(',')
    if not groups or len(set(groups)) != len(groups) or any(g not in GROUPS[1:] for g in groups):
        parser.error('Expected unique technical groups')
    from playwright.sync_api import sync_playwright
    timing.install()
    args.output.mkdir(parents=True, exist_ok=True)
    report = dict(os=platform.platform(), manifest=json.loads((args.build/'build-manifest.json').read_text()),
                  update_manifest=json.loads((args.update_build/'build-manifest.json').read_text()), results=[])
    try:
        with sync_playwright() as pw:
            for name in [args.browser]:
                for group in groups:
                    # Only persistence deliberately keeps its own profile/origin
                    # over genuine process restarts. Groups share no mutable host.
                    with tempfile.TemporaryDirectory(prefix='picross-browser-') as host, \
                         tempfile.TemporaryDirectory(prefix='picross-profile-', ignore_cleanup_errors=True) as profile:
                        root = Path(host)/'site'
                        shutil.copytree(args.build, root)
                        server, url = serve(root)
                        output = args.output/group
                        output.mkdir(exist_ok=True)
                        browser_actions.DIAGNOSTIC_OUTPUT = output
                        evidence = dict(browser=name, group=group, scenarios=[], status='failed', timings=[],
                                        launch_options=options(name), origin=url)
                        report['results'].append(evidence)
                        browser_actions.DIAGNOSTIC_EVIDENCE = evidence
                        session = Session(pw, name, profile, evidence)
                        timing.CURRENT = timing.Meter()
                        try:
                            importlib.import_module('group_'+group).exercise(
                                pw, name, root, args.update_build, url, output, evidence, session)
                            if set(evidence['scenarios']) != {s['id'] for s in expected(name, [group])}:
                                raise ValueError('Incomplete scenario coverage')
                            evidence['status'] = 'passed'
                        finally:
                            session.close()
                            evidence['timings'].append(timing.CURRENT.checkpoint('teardown-or-failure'))
                            evidence['elapsed_seconds'] = round(time.monotonic()-session.began, 6)
                            server.shutdown()
                            server.server_close()
    finally:
        (args.output/'browser-report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
