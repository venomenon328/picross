"""Manual RI-C-T01 only: fixed 0/1/2 catalog and 0/4/8 extra-file series.

Not part of unittest discovery or normal CI. Prepare once using the unchanged
base, then use exactly that input tree for both source trees and all platforms.
No real catalog, warm caches, three repetitions, setup measured separately.
"""
import argparse
import hashlib
import io as streams
import json
from pathlib import Path
import platform
import shutil
import statistics
import sys
import time
from unittest.mock import patch


def inventory(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('repo', 'inputs', 'work', 'output'): parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--source', required=True)
    parser.add_argument('--filesystem', required=True)
    parser.add_argument('--prepare', action='store_true')
    args = parser.parse_args()
    for name in ('repo', 'inputs', 'work', 'output'):
        setattr(args, name, getattr(args, name).resolve())
    sys.path.insert(0, str(args.repo.absolute()))
    from tools.puzzle_production import za1_fixtures as f, target_adapter as adapter
    from tools.puzzle_production import catalog_added as added, content_registry as cr
    from tools.puzzle_production import operation_diagnostics as diag, catalog_publication as pub
    from tools.puzzle_production.contract import load_json
    from tests.puzzle_production.catalog_fixtures import compact
    started = time.perf_counter()
    args.work.mkdir(parents=True, exist_ok=False)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    original_added = added.registration
    def fixed_added(identifier):
        value = original_added(identifier)
        value['added_at'] = value['provenance']['reference_time'] = '2026-11-08T00:00:00Z'
        return value
    if args.prepare:
        args.inputs.mkdir(parents=True, exist_ok=False)
        f.isolated_checkout(args.inputs / 'catalog-0')
        def export(identifier, extra):
            label = identifier + '-' + str(extra) if identifier == 'pz-ri-c-new' else identifier
            package = f.make(args.work / label, identifier, 3, 3, 'mono')
            handoff = load_json(package / 'handoff.json')
            for n, gate in enumerate(('reveal_approval', 'motif', 'provenance', 'logic', 'frame', 'visual', 'difficulty', 'reveal_consistency')[:extra]):
                name = 'extra-' + str(n) + '.txt'
                (package / name).write_bytes(b'TEST ONLY bounded extra input\n')
                handoff['gate_evidence'][gate] = name
            f.seal(package, handoff)
            approval = args.work / (identifier + '.json'); f.approve(package, approval)
            target = args.inputs / ('export-' + label)
            adapter.export(package, target, name='TEST ONLY RI-C', revision=1, stem=identifier, save_slot=identifier,
                           approval_path=approval, category_id='voegel', categories_path=args.inputs / 'catalog-0/content/categories.json')
            checked = f.difficulty_for_export(target)
            assert len(inventory(target)) == 30 + extra, 'Measurement needs actual exported additions'
            (args.inputs / ('checked-' + label + '.json')).write_text(json.dumps(checked), encoding='utf-8')
            return target, checked
        with patch.object(added, 'registration', side_effect=fixed_added):
            for n in (1, 2):
                root = args.inputs / ('catalog-' + str(n))
                shutil.copytree(args.inputs / ('catalog-' + str(n - 1)), root)
                target, checked = export('pz-ri-c-old-' + str(n), 0)
                cr.registration(target, root, apply=True, difficulty=checked)
                compact(root, [checked['current_source']['id']])
        for extra in (0, 4, 8): export('pz-ri-c-new', extra)
        (args.inputs / 'inventory.json').write_text(json.dumps(inventory(args.inputs), sort_keys=True), encoding='utf-8')
        print(json.dumps({'preparation_seconds': time.perf_counter() - started, 'inventory_sha256': hashlib.sha256((args.inputs / 'inventory.json').read_bytes()).hexdigest()}), flush=True)
        return
    expected = json.loads((args.inputs / 'inventory.json').read_text())
    actual = inventory(args.inputs); actual.pop('inventory.json')
    assert expected == actual, 'Synthetic input bytes changed'
    report = {'format': 'picross-ri-c-measurement-v1', 'source': args.source,
              'driver_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'source_inventory': inventory(args.repo / 'tools/puzzle_production'),
              'input_inventory_sha256': hashlib.sha256((args.inputs / 'inventory.json').read_bytes()).hexdigest(),
              'environment': {'os': platform.platform(), 'python': sys.version, 'pillow': __import__('PIL').__version__,
                              'filesystem': args.filesystem, 'work': str(args.work.absolute())}, 'rows': []}
    for catalog, extra in ((0, 0), (1, 0), (2, 0), (1, 4), (1, 8)):
        export = args.inputs / ('export-pz-ri-c-new-' + str(extra))
        checked = json.loads((args.inputs / ('checked-pz-ri-c-new-' + str(extra) + '.json')).read_text())
        for repetition in range(3):
            run = args.work / (str(catalog) + '-' + str(extra) + '-' + str(repetition)); run.mkdir()
            at = time.perf_counter(); shutil.copytree(args.inputs / ('catalog-' + str(catalog)), run / 'checkout')
            setup = time.perf_counter() - at
            d = diag.Diagnostics('register', stderr=streams.StringIO())
            at = time.perf_counter()
            with diag.observe(d), patch.object(added, 'registration', side_effect=fixed_added):
                result = cr.registration(export, run / 'checkout', apply=True, difficulty=checked)
            elapsed = time.perf_counter() - at
            assert result['status'] == 'registered'
            evidence = d.result()
            row = {'catalog': catalog, 'extra': extra, 'package_files': len(inventory(export)),
                   'repetition': repetition, 'setup_seconds': setup, 'seconds': elapsed,
                   'counters': evidence['counters'], 'phases': evidence['phases']}
            report['rows'].append(row)
            args.output.write_text(json.dumps(report, indent=2), encoding='utf-8')
            print(json.dumps({'catalog': catalog, 'extra': extra, 'repeat': repetition, 'seconds': elapsed,
                              'guards': evidence['counters'].get('guards'), 'proofs': evidence['counters'].get('full_candidate_proof_checks')}), flush=True)
    summary = []
    for catalog, extra in ((0, 0), (1, 0), (2, 0), (1, 4), (1, 8)):
        rows = [r for r in report['rows'] if r['catalog'] == catalog and r['extra'] == extra]
        def stats(values): return {'median': statistics.median(values), 'min': min(values), 'max': max(values)}
        summary.append({'catalog': catalog, 'extra': extra, 'package_files': rows[0]['package_files'],
                        'seconds': stats([r['seconds'] for r in rows]), 'setup_seconds': stats([r['setup_seconds'] for r in rows]),
                        'counters': {k: stats([r['counters'].get(k, 0) for r in rows]) for k in
                            ('guards', 'catalog_boundaries', 'bytes_read', 'bytes_hashed', 'staged_checkout_checks', 'full_candidate_proof_checks')},
                        'phases': {p: stats([sum(x['seconds'] for x in r['phases'] if x['name'] == p) for r in rows])
                                   for p in ('P0', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6')}})
    report['summary'] = summary
    report['total_seconds'] = time.perf_counter() - started
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    assert inventory(args.inputs) == {**expected, 'inventory.json': report['input_inventory_sha256']}
    print('RI-C-T01 ' + json.dumps({k: report[k] for k in ('source', 'driver_sha256', 'input_inventory_sha256', 'environment', 'summary')}), flush=True)


if __name__ == '__main__': main()
