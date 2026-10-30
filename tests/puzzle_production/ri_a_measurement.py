"""Manual RI-A-T01 bounded comparison. Never run against a real catalog.

Run this same driver with --repo pointing to each source tree. --inputs must
contain the fixed test-only export and checked.json made by --prepare.
"""
import argparse
from copy import deepcopy
from contextlib import ExitStack, nullcontext
import functools
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import statistics
import sys
import time
from unittest.mock import patch


class Meter:
    def __init__(self):
        self.rows = {}; self.stack = []; self.counters = {}

    def add(self, name, amount=1):
        self.counters[name] = self.counters.get(name, 0) + amount

    def wrap(self, original, name):
        @functools.wraps(original)
        def call(*args, **kwargs):
            at = time.perf_counter(); frame = [0.0]; self.stack.append(frame)
            row = self.rows.setdefault(name, {'calls': 0, 'inclusive_seconds': 0., 'self_seconds': 0.})
            row['calls'] += 1
            if name == 'safe':
                self.add('path_components', len(Path(args[0]).absolute().parts) - 1 + len(args[1].split('/')))
            if name == 'checksum' and args[0] is not None: self.add('hashed_bytes', len(args[0]))
            try:
                result = original(*args, **kwargs)
                if name == 'read' and result is not None: self.add('read_bytes', len(result))
                if name == 'write' and args[2] is not None:
                    self.add('published_files'); self.add('published_bytes', len(args[2]))
                return result
            finally:
                elapsed = time.perf_counter() - at
                self.stack.pop()
                if self.stack: self.stack[-1][0] += elapsed
                row['inclusive_seconds'] += elapsed; row['self_seconds'] += elapsed - frame[0]
        return call


def inventory(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--inputs', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--source', required=True)
    parser.add_argument('--repetitions', type=int, default=3, choices=(2, 3, 4))
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--observe', action='store_true', help='Also collect the operative RI-A diagnostics (RI-A sources only)')
    args = parser.parse_args()
    sys.path.insert(0, str(args.repo.absolute()))
    from tools.puzzle_production import target_adapter as adapter, za1_fixtures as fixtures
    from tools.puzzle_production import content_registry as registry, catalog_transaction as tx
    from tools.puzzle_production import catalog_io as io, catalog_publication as pub
    from tools.puzzle_production import images, verifier, catalog_method, difficulty_rating
    from tools.puzzle_production import sd2_rating_freeze
    args.work.mkdir(parents=True, exist_ok=False)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    def export(output):
        return adapter.export(args.inputs/'package', output, name='TEST ONLY RI-A-T01', revision=1,
                              stem='ri_t01', save_slot='ri_t01', approval_path=args.inputs/'approval.json',
                              category_id='voegel', categories_path=args.inputs/'empty/content/categories.json')
    if args.prepare:
        args.inputs.mkdir(parents=True, exist_ok=False)
        shutil.copytree(fixtures.FIXTURES/'direct-mono', args.inputs/'package')
        fixtures.approve(args.inputs/'package', args.inputs/'approval.json')
        fixtures.isolated_checkout(args.inputs/'empty')
        export(args.inputs/'export')
        (args.inputs/'checked.json').write_text(json.dumps(fixtures.difficulty_for_export(args.inputs/'export')), encoding='utf-8')
        (args.inputs/'inventory.json').write_text(json.dumps(inventory(args.inputs), sort_keys=True), encoding='utf-8')
        return
    expected = json.loads((args.inputs/'inventory.json').read_text())
    observed = inventory(args.inputs); observed.pop('inventory.json')
    assert expected == observed, 'Synthetic input inventory changed'
    checked = json.loads((args.inputs/'checked.json').read_text())
    assert json.loads((args.inputs/'export/manifest.json').read_text())['test_only'] is True
    report = {'format': 'picross-ri-a-measurement-v1', 'source': args.source,
              'driver_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'sources': inventory(args.repo/'tools/puzzle_production'), 'input_inventory': expected,
              'environment': {'os': platform.platform(), 'python': sys.version, 'pillow': __import__('PIL').__version__,
                              'work': str(args.work.absolute()), 'filesystem': None},
              'catalog_entries_before': 0, 'catalog_entries_after': 1,
              'package_files': len(inventory(args.inputs/'export')), 'repetitions': [],
              'missing_measurements': ['filesystem recorded separately in T01',
                  'read bytes count successful catalog_io reads only; prefix/other readers excluded',
                  'path components count successful complete traversals in this positive fixture']}
    for repeat in range(args.repetitions):
        meter = Meter(); phases = {}; phase_operations = {}; run = args.work/str(repeat); run.mkdir()
        def timed(name, fn):
            prior = deepcopy(meter.rows); counters = dict(meter.counters)
            diagnostics = None
            if args.observe and name not in ('setup', 'recovery_setup'):
                from tools.puzzle_production import operation_diagnostics as diagnostic
                diagnostics = diagnostic.Diagnostics({'recovery': 'recover-registration', 'interrupted_registration': 'register'}.get(name, name))
                diagnostics.environment['tool_commit'] = args.source
            at = time.perf_counter()
            with diagnostic.observe(diagnostics) if diagnostics else nullcontext():
                result = fn()
            phases[name] = time.perf_counter() - at
            phase_operations[name] = {'operations': {k: {field: value - prior.get(k, {}).get(field, 0)
                                         for field, value in row.items()} for k, row in meter.rows.items()},
                                      'counters': {k: value - counters.get(k, 0) for k, value in meter.counters.items()}}
            if diagnostics:
                if name != 'interrupted_registration': diagnostics.outcome = 'completed' if name != 'recovery' else 'rolled-back'
                phase_operations[name]['diagnostics'] = diagnostics.result()
            return result
        with ExitStack() as stack:
            for module, name in ((adapter, 'export'), (adapter, 'verify_export'), (images, 'inspect_candidate'),
                                 (verifier, 'verify'),
                                 (io, 'safe'), (io, 'read'), (io, 'checksum'),
                                 (tx, 'capture'), (tx, 'prepare'), (tx, '_stage_check'), (tx, 'validate_journal'),
                                 (pub, 'guard'), (pub, 'execute'), (pub, 'recover'), (pub, 'write'),
                                 (pub, 'sync_directory'), (os, 'fsync'), (catalog_method, 'method_hash'),
                                 (difficulty_rating, 'frozen_method'), (sd2_rating_freeze, 'frozen_method')):
                original = getattr(module, name); wrapped = meter.wrap(original, name)
                for loaded in list(sys.modules.values()):
                    if loaded is module or getattr(loaded, '__name__', '').startswith('tools.puzzle_production.'):
                        for alias, value in list(vars(loaded).items()):
                            if value is original: stack.enter_context(patch.object(loaded, alias, wrapped))
            timed('setup', lambda: shutil.copytree(args.inputs/'empty', run/'checkout'))
            timed('export', lambda: export(run/'export'))
            timed('plan', lambda: registry.registration(args.inputs/'export', run/'checkout', difficulty=checked))
            timed('register', lambda: registry.registration(args.inputs/'export', run/'checkout', apply=True, difficulty=checked))
            timed('recovery_setup', lambda: shutil.copytree(args.inputs/'empty', run/'recovery'))
            def interrupt():
                try: registry.registration(args.inputs/'export', run/'recovery', apply=True, difficulty=checked, fail_step='crash')
                except InterruptedError: return
                raise AssertionError('Missing injected crash')
            timed('interrupted_registration', interrupt)
            timed('recovery', lambda: registry.recover(run/'recovery'))
        report['repetitions'].append({'phases': phases, 'phase_operations': phase_operations,
                                     'operations': meter.rows, 'counters': meter.counters})
        args.output.write_text(json.dumps(report, indent=2), encoding='utf-8')
        print(json.dumps({'repeat': repeat, 'phases': phases}), flush=True)
    report['summary'] = {name: {'median': statistics.median(r['phases'][name] for r in report['repetitions']),
                                'min': min(r['phases'][name] for r in report['repetitions']),
                                'max': max(r['phases'][name] for r in report['repetitions'])} for name in phases}
    assert inventory(args.inputs) == {**expected, 'inventory.json': observed.get('inventory.json', hashlib.sha256((args.inputs/'inventory.json').read_bytes()).hexdigest())}
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
