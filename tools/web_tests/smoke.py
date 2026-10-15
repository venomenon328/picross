"""Start the uninstrumented regular export in both real browsers, online then offline."""
import argparse
import json
from pathlib import Path
import platform
import tempfile
from playwright.sync_api import sync_playwright
from serve import serve


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    server, url = serve(args.build.resolve())
    report = {'os':platform.platform(), 'manifest':json.loads((args.build/'build-manifest.json').read_text()), 'results':[]}
    try:
        with sync_playwright() as pw:
            for name in ('chromium', 'firefox'):
                with tempfile.TemporaryDirectory(prefix='picross-player-', ignore_cleanup_errors=True) as profile:
                    context = getattr(pw, name).launch_persistent_context(profile, headless=True, viewport={'width':1920,'height':1122})
                    try:
                        page = context.pages[0]
                        errors = []
                        page.on('pageerror', lambda error: errors.append(str(error)))
                        page.on('console', lambda msg: errors.append(msg.text) if msg.type=='error' else None)
                        page.goto(url)
                        page.wait_for_function('window.picrossStorage && picrossStorage.ready && !picrossStorage.pending && document.getElementById("message").hidden', timeout=60000)
                        assert page.evaluate('window.picrossProbe === undefined')
                        context.set_offline(True)
                        page.wait_for_timeout(2000)
                        assert not errors, errors
                        page.screenshot(path=str(args.output/f'{name}-regular-catalog.png'))
                        report['results'].append(dict(browser=name, user_agent=page.evaluate('navigator.userAgent'), status='passed'))
                        print('PLAYER PASS', name, flush=True)
                    finally:
                        context.close()
    finally:
        server.shutdown()
        (args.output/'regular-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')


if __name__ == '__main__':
    main()
