"""Current RP-4 tests in the pinned Windows venv; optional historical R1 diagnosis."""
import argparse
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import platform
import re
import site
import struct
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import urlparse


R1_HEAD = '4b794bb4ba109f2880876972e5e39e002b661478'
R1_TEST = 'test_rp4.CorpusTests.test_original_illustrations_reproduce_without_solver'
R1_ZLIB = '1.3.1.zlib-ng'
NAMES = {'illustration-teapot.png', 'illustration-sailboat.png', 'illustration-tulip.png'}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], timeout=30).decode().strip()


def runtime():
    from PIL import Image, features
    return {'python': platform.python_version(), 'platform': platform.platform(),
            'system': platform.system(), 'machine': platform.machine(), 'bits': struct.calcsize('P') * 8,
            'pillow': Image.__version__, 'pillow_file': Image.__file__,
            'pillow_zlib': features.version_codec('zlib'),
            'executable': sys.executable, 'prefix': sys.prefix, 'base_prefix': sys.base_prefix,
            'isolated': sys.flags.isolated, 'user_site_enabled': site.ENABLE_USER_SITE}


def compare_baseline_images(root):
    from PIL import Image
    corpus = root / 'examples/rp4'
    spec = importlib.util.spec_from_file_location('r1_illustrations', corpus / 'create_illustrations.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    records = []
    with tempfile.TemporaryDirectory(prefix='rp4-r1-', dir=os.environ['RUNNER_TEMP']) as temp:
        output = Path(temp) / 'illustrations'
        module.create(output)
        require({p.name for p in output.iterdir()} == NAMES, 'Wrong R1 illustration file set')
        for name in sorted(NAMES):
            original, generated = corpus / 'sources' / name, output / name
            with Image.open(original) as left, Image.open(generated) as right:
                require(left.mode == right.mode and left.size == right.size and
                        left.tobytes() == right.tobytes(), f'R1 pixels/mode/dimensions differ: {name}')
                record = {'name': name, 'mode': left.mode, 'size': list(left.size),
                          'decoded_sha256': hashlib.sha256(left.tobytes()).hexdigest(),
                          'original_sha256': hashlib.sha256(original.read_bytes()).hexdigest(),
                          'generated_sha256': hashlib.sha256(generated.read_bytes()).hexdigest()}
            require(record['original_sha256'] != record['generated_sha256'],
                    f'R1 encoding difference not reproduced: {name}')
            records.append(record)
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['baseline', 'current'], required=True)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    root, output = args.repo.resolve(), args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    current = Path(__file__).resolve().parents[1]
    report = {'format': 'picross-rp4-windows-v2', 'phase': args.phase,
              'phase_passed': False, 'accepted': False,
              'verification': 'current-regression' if args.phase == 'current' else 'historical-r1-reproduction'}
    if args.phase == 'baseline':
        report.update(r1_head=R1_HEAD, r1_zlib=R1_ZLIB)
    try:
        report['binding'] = {
            'source_head': os.environ['RP4_SOURCE_HEAD'], 'base_commit': os.environ['RP4_BASE_COMMIT'],
            'checkout': git(current, 'rev-parse', 'HEAD'), 'run_id': os.environ['GITHUB_RUN_ID'],
            'run_attempt': os.environ['GITHUB_RUN_ATTEMPT'], 'job': os.environ['GITHUB_JOB'],
            'run_url': f"{os.environ['GITHUB_SERVER_URL']}/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}"}
        report['test_checkout'] = git(root, 'rev-parse', 'HEAD')
        report['checkout_dirty'] = bool(git(current, 'status', '--porcelain', '--untracked-files=no'))
        report['test_checkout_dirty'] = bool(git(root, 'status', '--porcelain', '--untracked-files=no'))
        require(report['binding']['checkout'] == os.environ['GITHUB_SHA'], 'Wrong integration checkout')
        require(report['test_checkout'] == (R1_HEAD if args.phase == 'baseline' else os.environ['GITHUB_SHA']),
                'Wrong test checkout')
        require(not report['checkout_dirty'] and not report['test_checkout_dirty'], 'Modified test checkout')
        report['runtime'] = data = runtime()
        require(data['python'] == '3.12.10' and data['system'] == 'Windows' and data['bits'] == 64 and
                data['machine'].lower() in ('amd64', 'x86_64'), 'Requires the pinned Windows x64 Python')
        require(data['pillow'] == '12.3.0', 'Requires the pinned Pillow version')
        if args.phase == 'baseline':
            require(data['pillow_zlib'] == R1_ZLIB,
                    'Actual zlib differs from R1; this is not the requested reproduction')
        prefix = Path(sys.prefix).resolve()
        require(prefix != Path(sys.base_prefix).resolve() and
                prefix.is_relative_to(Path(os.environ['RUNNER_TEMP']).resolve()) and
                data['isolated'] == 1 and data['user_site_enabled'] is False and
                Path(data['pillow_file']).resolve().is_relative_to(prefix), 'Image environment is not isolated')
        require('include-system-site-packages = false' in (prefix / 'pyvenv.cfg').read_text(),
                'System site packages are enabled')
        install = json.loads((output / 'pillow-install.json').read_text(encoding='utf-8'))['install']
        require(len(install) == 1, 'Unexpected image dependencies')
        report['wheel'] = install[0]['download_info']
        wheel = urlparse(report['wheel']['url'])
        require(wheel.scheme == 'https' and wheel.hostname == 'files.pythonhosted.org' and
                wheel.path.lower().endswith('/pillow-12.3.0-cp312-cp312-win_amd64.whl'),
                'The official pinned Windows Pillow wheel was not installed')

        # Each phase is a separate -I process; no modules from the other checkout survive.
        sys.path[:0] = [str(root), str(root / 'tests/puzzle_production')]
        loader = unittest.TestLoader()
        suite = (loader.loadTestsFromName(R1_TEST) if args.phase == 'baseline' else
                 loader.discover(str(root / 'tests/puzzle_production'), pattern='test_rp4*.py'))
        log = io.StringIO()
        result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
        (output / f'{args.phase}-tests.log').write_text(log.getvalue(), encoding='utf-8')
        print(log.getvalue(), end='')
        report['tests'] = {'run': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
                           'skipped': len(result.skipped), 'expected_failures': len(result.expectedFailures),
                           'unexpected_successes': len(result.unexpectedSuccesses)}
        require(not (loader.errors or result.errors or result.skipped or result.expectedFailures or
                     result.unexpectedSuccesses), 'Load/error/skip/expected-failure is not acceptance')
        if args.phase == 'baseline':
            require(result.testsRun == 1 and len(result.failures) == 1 and
                    result.failures[0][0].id() == R1_TEST and
                    'self.assertEqual(file_hash(path), file_hash(CORPUS' in result.failures[0][1] and
                    re.search(r"AssertionError: '[0-9a-f]{64}' != '[0-9a-f]{64}'", result.failures[0][1]),
                    'The original R1 test did not fail at its PNG hash assertion')
            report['images'] = compare_baseline_images(root)
            report['baseline_reproduced'] = True
        else:
            require(result.testsRun > 13 and result.wasSuccessful(), 'Current RP-4 regressions failed or missing')
            report['accepted'] = True
        report['phase_passed'] = True
    except Exception as exc:
        report['error'] = f'{type(exc).__name__}: {exc}'
    finally:
        encoded = json.dumps(report, indent=2, ensure_ascii=False) + '\n'
        (output / f'{args.phase}.json').write_text(encoded, encoding='utf-8')
        print(encoded, end='')
    return 0 if report['phase_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
