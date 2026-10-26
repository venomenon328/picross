"""Start the uninstrumented regular export in Chromium, online then offline."""
import argparse
import json
from pathlib import Path
import platform
import tempfile
from serve import serve
from browser_runtime import options, graphics, launch
import timing
from contract import BROWSERS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--browser', choices=BROWSERS, default='chromium')
    args = parser.parse_args()
    from playwright.sync_api import sync_playwright
    timing.install()
    args.output.mkdir(parents=True, exist_ok=True)
    server, url = serve(args.build.resolve())
    report = {'os':platform.platform(), 'manifest':json.loads((args.build/'build-manifest.json').read_text()), 'results':[]}
    try:
        with sync_playwright() as pw:
            for name in [args.browser]:
                timing.CURRENT = timing.Meter()
                with tempfile.TemporaryDirectory(prefix='picross-player-', ignore_cleanup_errors=True) as profile:
                    context = launch(pw, name, profile, viewport={'width':1920,'height':1122})
                    evidence = dict(browser=name, group='regular', scenarios=[], timings=[], status='failed', errors=[], launch_options=options(name))
                    report['results'].append(evidence)
                    try:
                        page = context.pages[0]
                        evidence['user_agent'] = page.evaluate('navigator.userAgent')
                        errors = evidence['errors']
                        page.on('pageerror', lambda error: errors.append(str(error)))
                        page.on('console', lambda msg: errors.append(msg.text) if msg.type=='error' else None)
                        page.goto(url)
                        page.wait_for_function('window.picrossStorage && picrossStorage.ready && !picrossStorage.pending && document.getElementById("message").hidden', timeout=60000)
                        assert page.evaluate('window.picrossProbe === undefined')
                        evidence['graphics'] = graphics(page)
                        context.set_offline(True)
                        page.wait_for_timeout(2000)
                        assert not errors, errors
                        page.screenshot(path=str(args.output/f'{name}-regular-catalog.png'))
                        evidence['scenarios'] = ['regular-start']
                        evidence['timings'].append(timing.CURRENT.checkpoint('regular-start'))
                        evidence['status'] = 'passed'
                        print('PLAYER PASS', name, flush=True)
                    except Exception:
                        evidence['message'] = page.locator('#message').inner_text()
                        evidence['storage'] = page.locator('#storage').inner_text()
                        page.screenshot(path=str(args.output/f'{name}-regular-failure.png'))
                        print('PLAYER FAILURE', json.dumps(evidence), flush=True)
                        raise
                    finally:
                        context.close()
                        evidence['timings'].append(timing.CURRENT.checkpoint('teardown-or-failure'))
    finally:
        server.shutdown()
        server.server_close()
        (args.output/'regular-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')


if __name__ == '__main__':
    main()
