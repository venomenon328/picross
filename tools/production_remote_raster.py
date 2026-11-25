"""Closed operations on the current PW raster record. Producer imports stay inside execution."""
from copy import deepcopy
from time import monotonic

from .puzzle_production import catalog_io as io, current_authoring as current, raster_parameters as parameters
from .puzzle_production.authoring_package import require, sha
from .puzzle_production.contract import digest, exact_keys, integer

DECLARATION = {'actor', 'statement', 'timestamp_utc'}
SOURCE = {'candidate', 'revision', 'definition_sha256', 'matrix_sha256', 'proof_sha256',
          'motif_sha256', 'parameters_sha256'}
DERIVE = {'source', 'cells', 'mask_sha256', 'output', 'label', 'profile', 'rationale'}
FIELDS = {
    'diagnosis': {'source', 'uniqueness', 'max_nodes'},
    'profile_check': {'source', 'profile', 'rationale'},
    'fixed': DERIVE | {'edits', 'crop', 'max_changes'},
    'repair': DERIVE | {'config', 'extra_changes_reason'},
    'select': {'source', 'declaration', 'finding_decisions'},
    'findings': {'source', 'finding_decisions'},
    'exception': {'source', 'criterion', 'evidence', 'declaration'},
    'parameters': {'motif_sha256', 'previous', 'approved', 'declaration'},
    'budget': {'previous', 'limits', 'declaration'},
}


def validate(data):
    op, = data
    require(op in FIELDS, 'Unknown raster operation')
    value = data[op]
    extra = {'feature_cells'} & value.keys() if isinstance(value, dict) and op in ('fixed', 'repair') else set()
    if isinstance(value, dict) and op == 'repair' and 'region' in value:
        extra.add('region')
    change = exact_keys(value, FIELDS[op] | extra)
    if 'source' in change:
        source = exact_keys(change['source'], SOURCE)
        current.identifier(source['candidate'])
        integer(source['revision'], 1, 1000000, 'revision')
        for field in SOURCE - {'candidate', 'revision'}:
            if field != 'proof_sha256' or source[field] is not None:
                sha(source[field])
    if 'declaration' in change:
        d = change['declaration']
        extra = {'crop_protection'} & d.keys() if op == 'parameters' else set()
        exact_keys(d, DECLARATION | extra)
        current.human(d)
        if extra:
            require(isinstance(d['crop_protection'], dict) and 0 < len(d['crop_protection']) <= 20, 'Invalid mask bindings')
            for source, mask in d['crop_protection'].items():
                sha(source)
                sha(mask)
    if 'profile' in change:
        require(change['profile'] in ('line', 'paired'), 'Invalid raster profile')
        current.text(change['rationale'], 'operation rationale')
    if op in ('repair', 'fixed'):
        current.identifier(change['output'])
        current.text(change['label'], 'raster label', 512)
        sha(change['mask_sha256'])
        cells = change['cells']
        require(isinstance(cells, list) and 0 < len(cells) <= 50 and all(
            isinstance(row, list) and 0 < len(row) <= 50 and all(type(v) is bool for v in row) for row in cells),
            'Expected a bounded boolean protection mask')
        if 'feature_cells' in change:
            features = change['feature_cells']
            require(isinstance(features, list) and len(features) <= 64, 'Invalid feature mapping')
            for feature in features:
                exact_keys(feature, {'feature', 'cells'})
                current.text(feature['feature'], 'protected feature')
                require(isinstance(feature['cells'], list) and 0 < len(feature['cells']) <= 2500, 'Missing feature cells')
                for point in feature['cells']:
                    require(isinstance(point, list) and len(point) == 2, 'Invalid feature coordinate')
                    for n in point:
                        integer(n, 0, 49, 'feature coordinate')
    if op == 'fixed':
        integer(change['max_changes'], 0, 2500, 'max_changes')
        require(isinstance(change['edits'], list) and len(change['edits']) <= change['max_changes'], 'Invalid fixed edits')
        for edit in change['edits']:
            exact_keys(edit, {'x', 'y', 'before', 'after'})
            for k in edit:
                integer(edit[k], 0, 49 if k in ('x', 'y') else 8, k)
        require(isinstance(change['crop'], list) and len(change['crop']) == 4, 'Expected crop rectangle')
        for n in change['crop']:
            integer(n, 0, 50, 'crop')
    if op == 'repair':
        parameters.validate_search(change['config'], 50, 50)
        if 'region' in change:
            points = change['region']
            require(isinstance(points, list) and 0 < len(points) <= 2500, 'Invalid repair region')
            for point in points:
                require(isinstance(point, list) and len(point) == 2, 'Invalid repair coordinate')
                for n in point:
                    integer(n, 0, 49, 'repair coordinate')
            require(len(set(map(tuple, points))) == len(points), 'Duplicate repair coordinate')
        if change['extra_changes_reason'] is not None:
            current.text(change['extra_changes_reason'], 'additional changes rationale')
    if op == 'diagnosis':
        require(type(change['uniqueness']) is bool, 'Explicit uniqueness request required')
        integer(change['max_nodes'], 0, 100000, 'diagnosis nodes')
    if op in ('parameters', 'budget'):
        sha(change['previous'])
    if op == 'parameters':
        sha(change['motif_sha256'])
        current.findings.validate_parameters({'proposed': [], 'approved': change['approved']})
        require(change['approved'], 'Expected approved parameters')
    if op == 'budget':
        exact_keys(change['limits'], {'raster_candidates', 'repair_rounds', 'image_corrections'})
        for n in change['limits'].values():
            integer(n, 0, 1000000, 'budget')
    if op == 'exception':
        current.text(change['criterion'], 'exception criterion', 32)
        current.text(change['evidence'], 'exception evidence')
    if 'finding_decisions' in change:
        rows = change['finding_decisions']
        require(isinstance(rows, list) and len(rows) <= 128, 'Invalid finding declarations')
        for row in rows:
            exact_keys(row, DECLARATION | {'id', 'expected', 'action', 'treatment'})
            current.human(row)
            current.text(row['id'], 'finding ID', 64)
            sha(row['expected'])
            require(row['action'] in ('accept', 'revoke'), 'Expected a finding decision')
            current.text(row['treatment'], 'treatment')


def bound_bytes(root, ref):
    raw = io.read(root, ref['file'], min(ref['bytes'], 64 * current.LIMIT))
    require(current.content.ref(ref['file'], raw) == current.work_assets.local_ref(ref), 'Current original changed')
    return raw


def source_binding(job, row, definition):
    motif = current.findings.subjects(job)[job['selected']['motif']]
    return {'candidate': row['id'], 'revision': definition['revision'], 'definition_sha256': row['definition']['sha256'],
            'matrix_sha256': digest(definition['solution']), 'proof_sha256': row['proof'] and row['proof']['sha256'],
            'motif_sha256': motif['file']['sha256'], 'parameters_sha256': digest(job['parameters']['approved'])}


def check_published(change, job):
    """Reject stale choices against the pinned record before fetching large originals."""
    require(job['operation'] == 'production' and job['selected']['raster'] is None and
            job['state'] in ('motif_approved', 'raster_review', 'raster_ready'), 'Expected an open raster decision')
    assets = current.findings.subjects(job)
    motif = assets[job['selected']['motif']]['file']['sha256']
    if 'source' in change:
        source = change['source']
        row = next((r for r in job['rasters'] if r['id'] == source['candidate']), None)
        require(row and row['definition']['sha256'] == source['definition_sha256'] and
                (row['proof'] and row['proof']['sha256']) == source['proof_sha256'] and
                source['motif_sha256'] == motif and source['parameters_sha256'] == digest(job['parameters']['approved']),
                'Stale raster operation source')
    elif 'approved' in change:
        require(change['motif_sha256'] == motif and change['previous'] == digest(job['parameters']['approved']),
                'Stale motif or parameters')
    else:
        require(change['previous'] == digest(job['budgets']['limits']), 'Stale budget decision')


def replace_decision(job, scope, declaration):
    job['decisions'] = [d for d in job['decisions'] if d['scope'] != scope]
    decision = {'scope': scope, **deepcopy(declaration)}
    job['decisions'].append(decision)
    decision['binding'] = current.binding(job, scope)


def save(job, draft, files, root, scratch):
    current.build({'format': current.REQUEST, 'record': draft, 'expected': io.checksum(current.encoded(job)),
                   'files': files}, scratch, root)


def file_ref(job, key, name, raw, scratch, files):
    checksum = io.checksum(raw)
    path = f'content/authoring/{job["puzzle_id"]}/data/{key}/{checksum}/{name}'
    (scratch / name).write_bytes(raw)
    ref = current.content.ref(path, raw)
    files.append({'path': path, 'source': name, 'sha256': checksum, 'bytes': len(raw)})
    return ref


def compatible_crop(option, crop, before, protection):
    if option.get('format') != parameters.FORMAT:
        return False
    colors = len(before['palette'])
    mode = 'mono' if colors == 1 else 'color'
    if mode not in current.findings.matching_modes([option], before, colors):
        return False
    left, top, right, bottom = crop['rectangle']
    removed = (left, top, before['width'] - right, before['height'] - bottom)
    permissions = option['derivation']
    if any(count and side not in permissions['empty_edge_crop'] for side, count in zip(parameters.SIDES, removed)):
        return False
    if crop.get('edits') and not permissions['cell_edits']:
        return False
    pinned = protection.get(crop['before']['sha256'])
    if (pinned is not None or permissions['protected_features']) and pinned != crop['protection']['sha256']:
        return False
    for axis, size in (('width', right - left), ('height', bottom - top)):
        bound = option['constraints'][axis]
        if not parameters.accepts(bound, size):
            # Preserve the existing diagnostic route for a pure crop below an approximate minimum.
            if crop.get('edits') or bound['kind'] != 'approximate' or size >= (bound['minimum'] or 1):
                return False
    return True


def revise_parameters(job, change, root):
    motif = current.findings.subjects(job)[job['selected']['motif']]
    old = job['parameters']['approved']
    require(change['previous'] == digest(old) and change['motif_sha256'] == motif['file']['sha256'],
            'Stale motif or parameters')
    new = change['approved']
    old_decision = next(d for d in job['decisions'] if d['scope'] == 'motif')
    declaration = {k: deepcopy(v) for k, v in old_decision.items() if k == 'crop_protection'}
    declaration.update(change['declaration'])
    retired = []
    for row in job['rasters']:
        crop = row.get('crop_diagnosis')
        if crop:
            before = io.json_bytes(bound_bytes(root, crop['before']), 2 * current.LIMIT)
            allowed = [digest(p) for p in new if compatible_crop(p, crop, before, declaration.get('crop_protection', {}))]
            if not allowed:
                retired.append(row['id'])
            elif crop['parameters_sha256'] not in allowed:
                crop['parameters_sha256'] = allowed[0]
    if retired:
        used = job['budgets']['used']
        used['raster_candidates'] = max(used['raster_candidates'], len(job['rasters']))
        job['rasters'] = [r for r in job['rasters'] if r['id'] not in retired]
        job['findings'] = [r for r in job['findings'] if r['target'] not in retired]
        for candidate in retired:
            job['instructions'].pop(candidate, None)
    job['parameters']['approved'] = deepcopy(new)
    replace_decision(job, 'motif', declaration)
    job['state'] = 'raster_review' if job['rasters'] else 'motif_approved'
    return retired


def assess_findings(job, candidate, declarations):
    rows = {r['id']: r for r in job.get('findings', ()) if r['target'] == candidate}
    seen = set()
    for declaration in declarations:
        key = declaration['id']
        require(key in rows and key not in seen, 'Unknown or duplicate candidate finding')
        seen.add(key)
        current.findings.declare(rows[key], **{k: v for k, v in declaration.items() if k != 'id'})


def execute(options, job, root, scratch):
    validate(options)
    op, = options
    change = options[op]
    check_published(change, job)
    draft = deepcopy(job)
    files = []
    result = {}
    if op == 'parameters':
        result['retired_crops'] = revise_parameters(draft, change, root)
    elif op == 'budget':
        require(change['previous'] == digest(job['budgets']['limits']), 'Stale budget decision')
        draft['budgets']['limits'] = deepcopy(change['limits'])
        replace_decision(draft, 'budget', change['declaration'])
    else:
        candidate = change['source']['candidate']
        row = next((r for r in draft['rasters'] if r['id'] == candidate), None)
        require(row is not None, 'Missing current raster')
        raw = bound_bytes(root, row['definition'])
        definition = io.json_bytes(raw, 2 * current.LIMIT)
        require(change['source'] == source_binding(job, row, definition), 'Stale raster operation source')
        if op in ('select', 'findings'):
            assess_findings(draft, candidate, change['finding_decisions'])
            if op == 'select':
                if job['format'] in current.findings.FORMATS:
                    key = current.qualification.raster_key(job, row)
                    require(key in job.get('qualification', {}).get('facts', {}), 'Assess the published raster before selection')
                draft['selected']['raster'] = candidate
                replace_decision(draft, 'raster', change['declaration'])
                draft['state'] = 'background_review'
        elif op == 'exception':
            criterion = change['criterion']
            require(job['format'] in current.findings.FORMATS, 'Scoped technical exceptions require v3')
            facts = job.get('qualification', {}).get('facts', {}).get(current.qualification.raster_key(job, row), {})
            detail = facts.get('diagnostics', {}).get('qualification', {})
            require(detail, 'Assess the raster before recording an exception')
            eligible = {'palette:' + ':'.join(map(str, p['ids'])) for p in detail['palette_pairs'] if p['status'] == 'negative'}
            if parameters.frame_failures(detail['edges']):
                eligible.add('frame')
            require(criterion in eligible and all(e['criterion'] != criterion for e in row['exceptions']),
                    'Unknown, duplicate or inapplicable raster exception')
            evidence = file_ref(job, candidate, 'evidence.txt', change['evidence'].encode(), scratch, files)
            exception = {'criterion': criterion, 'definition_sha256': row['definition']['sha256'],
                         'evidence': evidence, **change['declaration']}
            if criterion == 'frame':
                exception.update(candidate_id=candidate, revision=definition['revision'])
            row['exceptions'].append(exception)
        else:
            from .production_remote_derivation import produce
            start = monotonic()
            result = produce(op, change, job, draft, row, raw, definition, root, scratch, files)
            result['production_seconds'] = round(monotonic() - start, 6)
            if result['status'] not in ('diagnosed', 'no-op'):
                start = monotonic()
                save(job, draft, files, root, scratch)
                result['builder_seconds'] = round(monotonic() - start, 6)
            return result
    save(job, draft, files, root, scratch)
    return {'state': draft['state'], 'decision': op, **result}
