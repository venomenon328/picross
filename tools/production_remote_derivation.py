"""Evaluate current candidate bytes with the existing solver, fixed edit and RP-5 kernels."""
from copy import deepcopy
from time import monotonic

from .production_remote_raster import bound_bytes, file_ref
from .puzzle_production import catalog_io as io, catalog_rating, current_authoring as current, current_tools
from .puzzle_production import diagnosis, editor_raster, raster_parameters as params, repair, verifier
from .puzzle_production.authoring_package import require
from .puzzle_production.contract import Budget, digest


def same_design(left, right):
    return all(left[k] == right[k] for k in ('width', 'height', 'palette', 'solution'))


def duplicate(job, definition, root):
    for candidate in job['rasters']:
        other = io.json_bytes(bound_bytes(root, candidate['definition']), 2 * current.LIMIT)
        if same_design(definition, other):
            return candidate['id']
    return None


def read_proof(root, row, puzzle):
    require(row['proof'], 'A bound deduction proof is required')
    proof = io.json_bytes(bound_bytes(root, row['proof']), 64 * current.LIMIT)
    checked = current.qualification.lookup(('verified-proof', puzzle.logic_hash, row['proof']['sha256']))
    if checked is None:
        checked = verifier.verify(puzzle, proof, Budget(120, 1000000))
        require(checked['proof_verified'], 'Current proof was not independently verified')
        current.qualification.remember(('verified-proof', puzzle.logic_hash, row['proof']['sha256']), checked)
    return proof


def diagnose(change, puzzle, proof):
    unresolved = [[x, y, values] for y, row in enumerate(proof['final_domains'])
                  for x, values in enumerate(row) if len(values) > 1]
    result = {'status': 'diagnosed', 'source': change['source'], 'proof_status': proof['status'],
              'profile': proof['profile'], 'reason': proof['reason'], 'open_domains': unresolved,
              'rows': sorted({y for x, y, d in unresolved}), 'columns': sorted({x for x, y, d in unresolved})}
    if change['uniqueness'] and proof['status'] != 'solved':
        report = diagnosis.diagnose(puzzle, diagnosis.DiagnosisBudget(120, 100000, change['max_nodes']))
        witnesses = [w['matrix'] for w in report['witnesses']]
        result['uniqueness'] = {k: report[k] for k in ('status', 'reason', 'statistics', 'budgets')}
        result['uniqueness']['witnesses'] = witnesses
        if len(witnesses) == 2:
            result['uniqueness']['differences'] = [[x, y] for y, row in enumerate(witnesses[0])
                                                  for x, value in enumerate(row) if value != witnesses[1][y][x]]
    return result


def reserve(job, *, search):
    used, limits = job['budgets']['used'], job['budgets']['limits']
    used['raster_candidates'] = max(used['raster_candidates'], len(job['rasters']))
    require(used['raster_candidates'] < limits['raster_candidates'], 'Candidate budget exhausted')
    if search:
        require(used['repair_rounds'] < limits['repair_rounds'], 'Repair rounds exhausted')
        used['repair_rounds'] += 1
    used['raster_candidates'] += 1


def protected(job, row, definition, change, option):
    mask = {'before_sha256': row['definition']['sha256'], 'motif_sha256': change['source']['motif_sha256'],
            'cells': change['cells']}
    pinned = next(d for d in job['decisions'] if d['scope'] == 'motif').get('crop_protection', {}).get(mask['before_sha256'])
    checksum = io.checksum(current.encoded(mask))
    require(checksum == change['mask_sha256'] and (pinned == checksum or
            pinned is None and not option['derivation']['protected_features']), 'Stale or unapproved protection mask')
    params.crop_rectangle([0, 0, definition['width'], definition['height']], definition['width'], definition['height'],
                          mask['cells'], [], definition['solution'], empty=0)
    return mask


def search(matrix, definition, proof, option, change, round_number, scratch):
    config = params.validate_search(change['config'], definition['width'], definition['height'])
    require(config['max_changes'] <= 2 or round_number > 1 and change['extra_changes_reason'],
            'Additional changes need a motivated later round')
    require(round_number > 1 or config['max_candidates'] <= 64 and config['max_steps'] <= 512,
            'First repair round exceeds the candidate or step limit')
    require(config['final_seconds'] > 0 and config['final_lines'] > 0, 'Reserve a fresh final certification')
    require(option['derivation']['cell_edits'], 'Cell repair not approved')
    colors = [{'id': 'c' + str(p['id']), 'rgb': '#' + p['color']} for p in definition['palette']]
    # Current definitions always use v2 runtime clues, including one-colour puzzles.
    design = {'source_id': change['source']['candidate'], 'width': definition['width'], 'height': definition['height'],
              'mode': 'color', 'palette': colors}
    wire = [['c' + str(v) if v else 'empty' for v in row] for row in matrix]
    palette = {p['id'] for p in colors}
    cert = None if change['profile'] == 'line' else {
        'profile': 'paired-lines-color', 'max_pair_work': 20000000, 'max_pair_records': 250000}
    budget = Budget(config['search_seconds'], config['search_lines'])
    start = monotonic()
    status, reason, selected, frontier, history, attempts = repair.explore(
        wire, design, change['cells'], proof['final_domains'], config, budget, scratch, cert,
        admissible=lambda trial: params.used_foreground(trial, 'empty') == palette)
    result = {'outcome': status, 'reason': reason, 'candidates': len(history) +
              sum(a['outcome'] == 'evaluation_aborted' for a in attempts),
              'proposals': len(attempts), 'lines': budget.lines, 'pair_work': budget.pair_work,
              'search_seconds': round(monotonic() - start, 6)}
    if selected is None:
        return None, result
    chosen = frontier.states[selected]['matrix']
    return [[0 if value == 'empty' else int(value[1:]) for value in row] for row in chosen], result


def stage_raster(job, row, result, output, scratch, files):
    for field, ref in result['files'].items():
        previous = row.get(field)
        if ref is None:
            row[field] = None
        elif previous is None or previous['sha256'] != ref['sha256']:
            raw = io.read(output, ref['file'], ref['bytes'])
            require(io.checksum(raw) == ref['sha256'], 'Changed certification output')
            row[field] = file_ref(job, row['id'], ref['file'], raw, scratch, files)


def produce(op, change, job, draft, row, raw, definition, root, scratch, files):
    from .puzzle_production import palette_gate

    mode = 'mono' if len(definition['palette']) == 1 else 'color'
    _, puzzle, _, _ = catalog_rating.definition(raw)
    proof = read_proof(root, row, puzzle) if op in ('diagnosis', 'repair') or op == 'profile_check' and row['proof'] else None
    if op == 'diagnosis':
        return diagnose(change, puzzle, proof)
    result = {'status': 'computed', 'source': change['source'], 'operation': op}
    output = scratch / 'certified'
    if op == 'profile_check':
        same_profile = proof and proof['profile']['id'].startswith('paired-') == (change['profile'] == 'paired')
        if proof and (row['difficulty'] and proof['status'] == 'solved' or same_profile and proof['status'] == 'stalled'):
            return {**result, 'status': 'no-op', 'proof_status': proof['status']}
        certified = current_tools.raster(raw, output, mode=mode, profile=change['profile'])
        if row['proof'] and row['proof']['sha256'] == certified['files']['proof']['sha256'] and not (
                row['difficulty'] or certified['files']['difficulty']):
            return {**result, 'status': 'no-op', 'proof_status': certified['status']}
        # Q-H03 describes the logic profile. The inspected image and cell geometry are unchanged.
        row['review'].pop('Q-H03', None)
        if 'findings' in draft:
            draft['findings'] = [r for r in draft['findings'] if (r['target'], r['criterion']) != (row['id'], 'Q-H03')]
        stage_raster(job, row, certified, output, scratch, files)
        draft['state'] = 'raster_review'
        return {**result, 'candidate': row['id'], 'proof_status': certified['status'], 'certified': certified['certified']}
    options = job['parameters']['approved']
    require(len(options) == 1 and options[0].get('format') == params.FORMAT, 'Explicit derivation corridor required')
    option = params.validate(options[0])
    require(mode == option['imports'][0]['mode'], 'Raster mode differs from approved corridor')
    mask = protected(job, row, definition, change, option)
    matrix = definition['solution']
    limits = {}
    crop = None
    if op == 'fixed':
        rectangle = change['crop']
        changed = params.edit_rectangle(matrix, mask['cells'], rectangle, change['edits'], option['derivation'],
                      change['max_changes'], {p['id'] for p in definition['palette']}, empty=0)
        if changed == matrix:
            return {**result, 'status': 'no-op'}
        if rectangle != [0, 0, definition['width'], definition['height']]:
            crop = {'format': current.CROP_DIAGNOSIS, 'before': row['definition'], 'preview': row['preview'],
                    'rectangle': rectangle, 'parameters_sha256': digest(option)}
            if change['edits']:
                crop['edits'] = change['edits']
    require(change['output'] not in current.findings.subjects(job), 'Output candidate ID occupied')
    reserve(draft, search=op == 'repair')
    if op == 'repair':
        plan_hash = digest({k: change[k] for k in ('source', 'profile', 'mask_sha256', 'config')})
        require(row.get('last_repair', {}).get('plan') != plan_hash, 'This repair plan has already run')
        require(proof['status'] in ('stalled', 'aborted'), 'Repair requires an unresolved current proof')
        require(change['profile'] == 'paired' or not proof['profile']['id'].startswith('paired-'), 'Paired reference requires paired repair')
        params.result(option, {**definition, 'mode': mode}, matrix, empty=0)
        changed, summary = search(matrix, definition, proof, option, change, draft['budgets']['used']['repair_rounds'], scratch)
        result['search'] = summary
        row['last_repair'] = {'plan': plan_hash, 'definition_sha256': row['definition']['sha256'],
                              **{k: summary[k] for k in ('outcome', 'reason', 'candidates', 'proposals')}}
        if changed is None:
            return {**result, 'candidate': row['id'], 'outcome': summary['outcome']}
        limits = {'solve_seconds': change['config']['final_seconds'], 'solve_lines': change['config']['final_lines']}
    next_def = editor_raster.definition(definition, changed)
    require(params.used_foreground(changed) == {p['id'] for p in definition['palette']}, 'Used palette changed')
    effective = deepcopy(option)
    if crop and not change['edits']:
        for axis in ('width', 'height'):
            bound = effective['constraints'][axis]
            if bound['kind'] == 'approximate' and bound['minimum'] and next_def[axis] < bound['minimum']:
                bound['minimum'] = next_def[axis]
    params.result(effective, {**next_def, 'mode': mode}, changed, empty=0)
    prior = duplicate(job, next_def, root)
    if prior:
        return {**result, 'candidate': prior, 'outcome': 'duplicate'}
    palette = [{'id': 'c' + str(p['id']), 'rgb': '#' + p['color']} for p in definition['palette']]
    palette_gate.early([['c'+str(v) if v else 'empty' for v in line] for line in changed],
                       {'palette': palette, 'source_id': change['output']})
    certified = current_tools.raster(next_def, output, mode=mode, profile=change['profile'], **limits)
    if op == 'repair' and not certified['certified']:
        result['search'].update(outcome='aborted', reason='final_' + certified['status'])
        row['last_repair'].update(outcome='aborted', reason=result['search']['reason'])
        return {**result, 'candidate': row['id'], 'outcome': 'aborted'}
    successor = {'id': change['output'], 'label': change['label'], 'review': {}, 'exceptions': []}
    stage_raster(job, successor, certified, output, scratch, files)
    if crop:
        crop['protection'] = file_ref(job, successor['id'], 'protection.json', current.encoded(mask), scratch, files)
        successor['crop_diagnosis'] = crop
    draft['rasters'].append(successor)
    draft['state'] = 'raster_review'
    return {**result, 'candidate': successor['id'], 'proof_status': certified['status'], 'certified': certified['certified']}
