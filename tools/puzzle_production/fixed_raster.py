"""Approval-bound fixed edits/empty-edge crop; no search and no manual override."""
from __future__ import annotations

import argparse
from copy import deepcopy
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import time

from . import authoring_package as ap, certification, images, raster_parameters as parameters
from .contract import (Aborted, Budget, InvalidInput, canonical_bytes, digest, exact_keys,
                       integer, load_json, validate_logic, write_json)

PLAN = 'picross-fixed-raster-plan-v1'
RECORD = 'picross-fixed-raster-v1'
MANIFEST = 'picross-fixed-raster-manifest-v1'
LIMIT = 1024 * 1024


def path(root, name):
    ap.relative(name)
    target = root / name
    ap.require(target.resolve().is_relative_to(root.resolve()) and
               not any(p.is_symlink() or getattr(p, 'is_junction', lambda: False)()
                       for p in [target, *target.parents] if p != root.parent),
               'Unsafe fixed raster path')
    return target


def validate_plan(value):
    p = exact_keys(value, {'format', 'puzzle_id', 'revision', 'reference', 'motif', 'parameters',
                          'import_hash', 'protected_mask', 'edits', 'crop', 'budgets', 'certification', 'rationale'})
    ap.require(p['format'] == PLAN and isinstance(p['puzzle_id'], str) and ap.ID.fullmatch(p['puzzle_id']) and
               isinstance(p['revision'], str) and ap.REVISION.fullmatch(p['revision']), 'Invalid fixed plan identity')
    r = exact_keys(p['reference'], {'bundle', 'variant', 'manifest_sha256', 'matrix_hash', 'logic_hash'})
    ap.relative(r['bundle'])
    ap.require(isinstance(r['variant'], str) and images.ID.fullmatch(r['variant']), 'Invalid reference variant')
    for key in ('manifest_sha256', 'matrix_hash', 'logic_hash'):
        ap.sha(r[key])
    m = exact_keys(p['motif'], {'file', 'sha256', 'approval'})
    exact_keys(m['approval'], {'file', 'sha256'})
    for ref in (m, m['approval']):
        ap.relative(ref['file']); ap.sha(ref['sha256'])
    parameters.validate(p['parameters']); ap.sha(p['import_hash'])
    b = exact_keys(p['budgets'], {'max_changes', 'solve_seconds', 'solve_lines', 'verify_seconds', 'verify_lines'})
    integer(b['max_changes'], 0, 2500, 'max_changes')
    for kind in ('solve', 'verify'):
        n = b[kind + '_seconds']
        ap.require(type(n) in (int, float) and math.isfinite(n) and 0 < n <= 120, 'Invalid finite time budget')
        integer(b[kind + '_lines'], 1, 1_000_000, 'line budget')
    if p['certification'] is not None:
        certification.validate_config(p['certification'])
    ap.string(p['rationale'], 'fixed rationale')
    return p


def transform(p, design, matrix):
    """Pure replay against the untouched reference, including protected empties."""
    p = validate_plan(p)
    w, h = design['width'], design['height']
    mask = p['protected_mask']
    ap.require(isinstance(mask, list) and len(mask) == h and all(isinstance(row, list) and len(row) == w and
               all(type(v) is bool for v in row) for row in mask), 'Full boolean protection mask required')
    crop = p['crop']
    ap.require(isinstance(crop, list) and len(crop) == 4, 'Cell crop must be one rectangle')
    for n in crop:
        integer(n, 0, 50, 'cell crop')
    l, t, r, b = crop
    ap.require(0 <= l < r <= w and 0 <= t < b <= h, 'Invalid cell crop rectangle')
    permissions = p['parameters']['derivation']
    for side, changed in zip(parameters.SIDES, (l != 0, t != 0, r != w, b != h)):
        ap.require(not changed or side in permissions['empty_edge_crop'], 'Unapproved empty-edge crop')
    for y, row in enumerate(matrix):
        for x, v in enumerate(row):
            if not (l <= x < r and t <= y < b):
                ap.require(v == 'empty' and not mask[y][x], 'Crop removes nonempty or protected reference cell')
    edits = p['edits']
    ap.require(isinstance(edits, list) and len(edits) <= p['budgets']['max_changes'], 'Fixed change budget exceeded')
    ap.require(not edits or permissions['cell_edits'], 'Cell edits not approved')
    allowed = {'empty', *(v['id'] for v in design['palette'])}
    seen, result = set(), deepcopy(matrix)
    for edit in edits:
        exact_keys(edit, {'x', 'y', 'before', 'after'})
        x, y = integer(edit['x'], 0, w - 1, 'x'), integer(edit['y'], 0, h - 1, 'y')
        ap.require((x, y) not in seen and l <= x < r and t <= y < b, 'Duplicate or cropped edit coordinate')
        seen.add((x, y))
        ap.require(not mask[y][x], 'Protected cell edit')
        ap.require(edit['before'] == matrix[y][x] and edit['after'] in allowed and edit['after'] != edit['before'],
                   'Wrong before, palette value or no-op edit')
        result[y][x] = edit['after']
    ap.require(edits or crop != [0, 0, w, h], 'Unchanged fixed plan is a no-op; retain the import')
    result = [row[l:r] for row in result[t:b]]
    derived = {**design, 'width': r - l, 'height': b - t}
    parameters.result(p['parameters'], derived, result)
    return derived, result


def budget(p, kind):
    b = p['budgets']
    if p['certification']:
        return certification.bounded_budget(b[kind + '_seconds'], b[kind + '_lines'], p['certification'])
    return Budget(b[kind + '_seconds'], b[kind + '_lines'])


def reference(root, p, outer_budget=None):
    p = validate_plan(p)
    r, m = p['reference'], p['motif']
    directory = path(root, r['bundle'])
    ap.require(images.file_hash(directory / 'manifest.json') == r['manifest_sha256'], 'Reference manifest hash differs')
    manifest = load_json(directory / 'manifest.json')
    ap.require(manifest.get('format') in ('picross-image-manifest-v1', 'picross-image-manifest-v2'), 'Only direct RP-3 reference supported')
    ap.require(p['certification'] == manifest.get('certification'), 'Reference certification cannot be changed/downgraded')
    limits = budget(p, 'verify')
    if outer_budget is not None:
        limits.deadline = min(limits.deadline, outer_budget.deadline)
        limits.max_lines = min(limits.max_lines, max(0, outer_budget.max_lines - outer_budget.lines))
        limits.max_pair_work = min(limits.max_pair_work, max(0, outer_budget.max_pair_work - outer_budget.pair_work))
        limits.max_pair_records = min(limits.max_pair_records, outer_budget.max_pair_records)
    try:
        c, proof, checked = images.inspect_candidate(directory, r['variant'], limits)
    finally:
        if outer_budget is not None:
            outer_budget.lines += limits.lines
            outer_budget.pair_work += limits.pair_work
            outer_budget.pair_peak_records = max(outer_budget.pair_peak_records, limits.pair_peak_records)
    stored = load_json(directory / (r['variant'] + '-result.json'))
    ap.require(checked['proof_verified'] and checked['status'] in ('solved', 'stalled') and
               stored.get('status') == checked['status'] and stored.get('proof_verified') is True and
               stored.get('certified') == checked['certified'], 'Reference proof/status is incomplete or stale')
    ap.require(digest(c['matrix']) == r['matrix_hash'] and c['logic_hash'] == r['logic_hash'], 'Reference matrix/logic differs')
    for ref in (m, m['approval']):
        ap.require(images.file_hash(path(root, ref['file'])) == ref['sha256'], 'Motif/approval file hash differs')
    a = load_json(path(root, m['approval']['file']))
    ap.require(a.get('type') == 'human_motif_approval' and a.get('file') == m['file'] and
               a.get('sha256') == m['sha256'], 'Missing actual motif approval')
    for key in ('actor', 'statement', 'revision'):
        ap.string(a.get(key), 'motif approval ' + key)
    ap.timestamp(a.get('timestamp_utc')); ap.sha(a.get('derived_from_reveal_sha256'))
    ap.require(path(root, a.get('evidence')).is_file(), 'Missing actual motif decision evidence')
    parameters.binding([p['parameters']], a)
    ap.require(images.file_hash(directory / manifest['original']) == m['sha256'], 'Reference is not approved motif')
    entry = parameters.import_entry(c['design'], c['matrix'], r['variant'])
    ap.require(entry in p['parameters']['imports'] and digest(entry) == p['import_hash'], 'Wrong selected import/corridor')
    parameters.result(p['parameters'], c['design'], c['matrix'])
    limits.check()
    return c, checked


def record(p, plan_sha, c, base):
    design, matrix = transform(p, c['design'], c['matrix'])
    return {'format': RECORD, 'puzzle_id': p['puzzle_id'], 'revision': p['revision'], 'plan_sha256': plan_sha,
            'reference_manifest_sha256': p['reference']['manifest_sha256'], 'import_design': c['design'],
            'design': design, 'matrix': matrix, 'matrix_hash': digest(matrix),
            'logic_hash': digest(images.logic_from_matrix(matrix, design)), 'base_status': base['status']}


def proof_check(directory, p, seconds=None, lines=None, pair_work=None, pair_records=None):
    puzzle = validate_logic(load_json(directory / 'logic.json'))
    limits = budget(p, 'verify')
    if seconds is not None:
        ap.require(math.isfinite(seconds) and seconds >= 0, 'Invalid remaining time')
        limits.deadline = min(limits.deadline, time.monotonic() + seconds)
    if lines is not None: limits.max_lines = min(limits.max_lines, integer(lines, 0, 1_000_000, 'remaining lines'))
    if pair_work is not None: limits.max_pair_work = min(limits.max_pair_work, integer(pair_work, 0, 100_000_000, 'remaining pair work'))
    if pair_records is not None: limits.max_pair_records = min(limits.max_pair_records, integer(pair_records, 0, 1_000_000, 'remaining pair records'))
    if p['certification']:
        proof, checked = certification.inspect(puzzle, directory, '', p['certification'], limits)
    else:
        from .verifier import verify
        proof = load_json(directory / 'proof.json', puzzle.proof_byte_limit)
        certification.require_legacy(puzzle, proof)
        checked = verify(puzzle, proof, limits)
    ap.require(checked['status'] == 'solved' and checked['certified'] and checked['proof_verified'], 'Final proof is not certified solved')
    matrix = load_json(directory / 'record.json', LIMIT)['matrix']
    ap.require(proof['final_domains'] == [[[v] for v in row] for row in matrix], 'Final proof matrix differs')
    return checked


def fresh_check(directory, p, seconds=None, lines=None, pair_work=None, pair_records=None):
    command = [sys.executable, '-m', 'tools.puzzle_production.fixed_raster', '_verify', '--bundle', str(directory.resolve())]
    for flag, value in (('--seconds', seconds), ('--lines', lines), ('--pair-work', pair_work), ('--pair-records', pair_records)):
        if value is not None: command.extend((flag, str(value)))
    try:
        result = subprocess.run(command, cwd=Path(__file__).resolve().parents[2], capture_output=True,
                                timeout=p['budgets']['verify_seconds'] + 10)
    except subprocess.TimeoutExpired as exc:
        raise Aborted('fixed_verifier_timeout') from exc
    if result.returncode == 4:
        raise Aborted('fixed_verifier_budget')
    ap.require(result.returncode == 0, 'Fresh independent fixed proof verification failed: ' + result.stderr.decode('utf-8', errors='replace')[:2048])
    import json
    return json.loads(result.stdout)


def replay_record(p, value):
    return {k: value[k] for k in ('plan_sha256', 'matrix_hash', 'logic_hash')} | {
        'status': 'solved', 'proof_verified': True, 'certified': True}


def inspect(root, directory, outer_budget=None):
    root, directory = Path(root), Path(directory)
    m = exact_keys(load_json(directory / 'manifest.json', LIMIT), {'format', 'tool', 'files'})
    ap.require(m['format'] == MANIFEST, 'Unsupported fixed raster manifest')
    tool = exact_keys(m['tool'], {'name', 'version', 'modules'})
    ap.require(tool['name'] == 'fixed-raster' and type(tool['version']) is int and tool['version'] == 1, 'Invalid fixed tool')
    exact_keys(tool['modules'], {'fixed_raster.py', 'raster_parameters.py'})
    for value in tool['modules'].values(): ap.sha(value)
    p = validate_plan(load_json(directory / 'plan.json', LIMIT))
    names = {'plan.json', 'record.json', 'logic.json', 'proof.json', 'result.json', 'replay.json', 'raster.png'}
    if p['certification']: names.update(('baseline-proof.json', 'assessment.json'))
    ap.require(isinstance(m['files'], dict) and set(m['files']) == names and
               {f.name for f in directory.iterdir()} == names | {'manifest.json'}, 'Fixed bundle file set differs')
    for name, sha in m['files'].items():
        f = path(directory, name)
        ap.require(f.is_file() and f.stat().st_nlink == 1 and images.file_hash(f) == ap.sha(sha), 'Fixed file hash differs')
    c, base = reference(root, p, outer_budget)
    expected = record(p, images.file_hash(directory / 'plan.json'), c, base)
    value = load_json(directory / 'record.json', LIMIT)
    ap.require(canonical_bytes(value) == canonical_bytes(expected), 'Fixed record differs from exact replay')
    ap.require(load_json(directory / 'logic.json') == images.logic_from_matrix(value['matrix'], value['design']), 'Fixed clues differ')
    from PIL import Image
    with Image.open(directory / 'raster.png', formats=('PNG',)) as raster:
        image = images.raster_image(value['matrix'], value['design'])
        ap.require(raster.mode == image.mode and raster.size == image.size and not raster.info and
                   getattr(raster, 'n_frames', 1) == 1 and raster.tobytes() == image.tobytes(), 'Fixed raster image differs')
    if outer_budget is not None:
        outer_budget.check()
        # The subprocess can only tighten the recorded limits. Its original
        # plan bytes remain unchanged and all counters come from fresh replay.
        remaining = min(p['budgets']['verify_seconds'], outer_budget.deadline - time.monotonic())
        max_lines = min(p['budgets']['verify_lines'], max(0, outer_budget.max_lines - outer_budget.lines))
        checked = fresh_check(directory, p, remaining, max_lines,
                              max(0, outer_budget.max_pair_work - outer_budget.pair_work), outer_budget.max_pair_records)
        outer_budget.lines += checked['line_evaluations']
        outer_budget.pair_work += checked.get('pair_work', 0)
        outer_budget.pair_peak_records = max(outer_budget.pair_peak_records, checked.get('pair_peak_records', 0))
        outer_budget.check()
    else:
        checked = fresh_check(directory, p)
    stored = load_json(directory / 'result.json')
    # Timings/counters are observations; status and identities must still agree.
    for key in ('status', 'certified', 'proof_verified', 'logic_hash', 'profile', 'profile_hash'):
        ap.require(stored.get(key) == checked.get(key), 'Stale fixed result')
    ap.require(load_json(directory / 'replay.json') == replay_record(p, value), 'Stale fixed replay')
    for name, sha in m['files'].items():
        ap.require(images.file_hash(path(directory, name)) == sha, 'Fixed bundle changed during verification')
    ap.require(load_json(directory / 'manifest.json', LIMIT) == m, 'Fixed manifest changed during verification')
    return value, load_json(directory / 'proof.json', validate_logic(load_json(directory / 'logic.json')).proof_byte_limit), checked


def derive(root, plan_path, output):
    root, output = Path(root), Path(output)
    ap.require(not output.exists(), 'Fixed output already exists')
    p = validate_plan(load_json(plan_path, LIMIT))
    c, base = reference(root, p)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='fixed-', dir=output.parent) as tmp:
        stage = Path(tmp)
        write_json(stage / 'plan.json', p)
        value = record(p, images.file_hash(stage / 'plan.json'), c, base)
        write_json(stage / 'record.json', value)
        logic = images.logic_from_matrix(value['matrix'], value['design'])
        write_json(stage / 'logic.json', logic)
        puzzle = validate_logic(logic)
        if p['certification']:
            certification.produce(puzzle, stage, '', p['certification'], budget(p, 'solve'), budget(p, 'verify'))
        else:
            from .solver import solve
            write_json(stage / 'proof.json', solve(puzzle, budget(p, 'solve')))
        checked = fresh_check(stage, p)
        write_json(stage / 'result.json', checked)
        write_json(stage / 'replay.json', replay_record(p, value))
        images.raster_image(value['matrix'], value['design']).save(stage / 'raster.png')
        write_json(stage / 'manifest.json', {'format': MANIFEST,
            'tool': {'name': 'fixed-raster', 'version': 1, 'modules': {n: images.file_hash(Path(__file__).with_name(n))
                     for n in ('fixed_raster.py', 'raster_parameters.py')}},
            'files': {f.name: images.file_hash(f) for f in sorted(stage.iterdir())}})
        inspect(root, stage)
        images.publish_bundle(stage, output)
    return value


def inspect_package(package, outer_budget):
    h, c = package.handoff, package.handoff['candidate']
    ap.require(h['format'] == 'picross-authoring-handoff-v4' and h['rulebook']['version'] == '0.8.0', 'Fixed requires Authoring 0.8')
    r = exact_keys(h['repair'], {'type', 'reference', 'reference_variant', 'plan', 'record', 'replay'})
    ap.require(r['type'] == 'fixed_edits_empty_crop' and c['variant'] == 'fixed', 'Wrong regular fixed selection')
    directory = package.bundle(c['bundle'])
    for key in ('plan', 'record', 'replay'):
        ap.require(r[key] == c['bundle'] + '/' + key + '.json', 'Wrong fixed file selection')
        package.file(r[key])
    p = package.json(r['plan'])
    original_revision = h['revision']
    if h.get('raster_selection'):
        selection = package.json(h['raster_selection']['file'])
        original_revision = package.json(selection['record']['copy'])['revision']
    ap.require(p['puzzle_id'] == h['puzzle_id'] and p['revision'] == original_revision and
               r['reference'] == p['reference']['bundle'] and r['reference_variant'] == p['reference']['variant'], 'Wrong fixed reference/identity')
    reference_dir = package.bundle(r['reference'])
    ap.require(p['motif'] == {k: h['motif'][k] for k in ('file', 'sha256')} | {
        'approval': {'file': h['motif']['approval'], 'sha256': images.file_hash(package.file(h['motif']['approval']))}}, 'Wrong fixed motif approval')
    parameters.binding(h['approved_parameters'], package.approval(h['motif'], 'motif'))
    ap.require(h['approved_parameters'] == [p['parameters']], 'Wrong approved fixed corridor')
    value, proof, checked = inspect(package.root, directory, outer_budget)
    from . import catalog_analysis, catalog_rating
    rating = package.json(h['gate_evidence']['difficulty'])
    ap.require(rating.get('format') == 'picross-checked-difficulty-v3', 'Fixed raster requires active 0.4 checked difficulty')
    definition = catalog_analysis.candidate(value['design'], value['matrix'],
        images.logic_from_matrix(value['matrix'], value['design']), h['puzzle_id'], rating['current_source']['runtime_revision'])
    catalog_rating.validate(rating, active=False, definition_bytes=canonical_bytes(definition) + b'\n',
                            production_mode=value['design']['mode'])
    ap.require(rating['rating']['result']['status'] == 'rated', 'Incomplete active difficulty')
    for gate in ('visual', 'reveal_consistency'):
        report = package.file(h['gate_evidence'][gate]).read_text(encoding='utf-8')
        ap.require(value['matrix_hash'] in report and value['logic_hash'] in report, 'Stale final content judgment: ' + gate)
    source = {'kind': 'fixed', 'variant': 'fixed', 'candidate_id': digest(value), 'reference': p['reference']}
    return value['design'], value['matrix'], proof, checked, source, reference_dir


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('derive', 'inspect', '_verify'))
    parser.add_argument('--root', type=Path); parser.add_argument('--plan', type=Path)
    parser.add_argument('--output', type=Path); parser.add_argument('--bundle', type=Path)
    parser.add_argument('--seconds', type=float, help=argparse.SUPPRESS)
    parser.add_argument('--lines', type=int, help=argparse.SUPPRESS)
    parser.add_argument('--pair-work', type=int, help=argparse.SUPPRESS)
    parser.add_argument('--pair-records', type=int, help=argparse.SUPPRESS)
    a = parser.parse_args(argv)
    try:
        if a.command == '_verify':
            result = proof_check(a.bundle, validate_plan(load_json(a.bundle / 'plan.json', LIMIT)),
                                 a.seconds, a.lines, a.pair_work, a.pair_records)
        elif a.command == 'derive':
            ap.require(a.root is not None and a.plan is not None and a.output is not None, 'derive requires root/plan/output')
            result = derive(a.root, a.plan, a.output)
        else:
            ap.require(a.root is not None and a.bundle is not None, 'inspect requires root/bundle')
            result = inspect(a.root, a.bundle)[2]
        sys.stdout.buffer.write(canonical_bytes(result) + b'\n')
        return 0
    except Aborted as exc:
        print(str(exc), file=sys.stderr); return 4
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(str(exc), file=sys.stderr); return 2


if __name__ == '__main__':
    raise SystemExit(main())
