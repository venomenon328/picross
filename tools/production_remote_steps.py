"""Produce current raster offers or commit the adapter's exact product delivery."""
from copy import deepcopy

from . import production_git_workspace as ws, publish_git
from .puzzle_production import authoring_builder, catalog_io as io, catalog_integration, current_authoring as current
from .puzzle_production import current_tools
from .puzzle_production.authoring_package import require
from .puzzle_production.contract import exact_keys


def observations(draft, target, values):
    require(isinstance(values, list) and len(values) <= 128, 'Invalid visual observations')
    for value in values:
        exact_keys(value, current.findings.OBSERVATION)
        require(draft['format'] in current.findings.FORMATS, 'Structured observations require v3')
        row = {**deepcopy(value), 'target': target, 'content': current.findings.identity(draft, target), 'decision': None}
        existing = next((r for r in draft['findings'] if (r['target'], r['id']) == (target, row['id'])), None)
        if existing is None:
            draft['findings'].append(row)
        else:
            require({**existing, 'decision': None} == row, 'Existing finding changed during inspection')


def editorial(job, options, root, scratch):
    draft = deepcopy(job)
    require(draft['operation'] == 'production' and draft['selected']['raster'] is None, 'Raster choice already closed')
    if 'choice' in options:
        change = options['choice']
        candidate = change['candidate']
        motif = next((a for a in draft['assets'] if a['role'] == 'motif' and a['id'] == candidate), None)
        require(draft['state'] == 'motif_review' and draft['selected']['motif'] is None and motif and
                motif['file']['sha256'] == change['motif_sha256'], 'Different current motif offer')
        draft['selected']['motif'] = candidate
        draft['parameters']['approved'] = deepcopy(change['approved'])
        decision = {'scope': 'motif', **deepcopy(change['declaration'])}
        draft['decisions'].append(decision)
        decision['binding'] = current.binding(draft, 'motif')
        draft['state'] = 'motif_approved'
    else:
        change = options['assessment']
        candidate = change['candidate']
        raster = next((r for r in draft['rasters'] if r['id'] == candidate), None)
        require(draft['state'] in ('raster_review', 'raster_ready') and raster and
                raster['definition']['sha256'] == change['definition_sha256'] and
                raster['preview']['sha256'] == change['preview_sha256'], 'Different published raster')
        raster['review'].update(deepcopy(change['review']))
        observations(draft, candidate, change['observations'])
        draft['state'] = 'raster_ready' if change['ready'] else 'raster_review'
    current.build({'format': current.REQUEST, 'record': draft, 'expected': io.checksum(current.encoded(job)),
                   'files': []}, scratch, root)
    return {'candidate': candidate, 'state': draft['state']}


def step3(req, job, root, scratch):
    if 'design' not in req['input']:
        return editorial(job, req['input'], root, scratch)
    from .puzzle_production import images
    require(job['operation'] == 'production' and job['state'] in ('motif_approved', 'raster_review', 'raster_ready')
            and job['selected']['raster'] is None, 'Expected approved motif and an open raster choice')
    options = req['input']
    design = images.validate_design(options['design'])
    variant, = design['variants']
    motif = next((a for a in job['assets'] if a['id'] == job['selected']['motif'] and a['role'] == 'motif'), None)
    require(motif and motif['file']['sha256'] == options['motif_sha256'], 'Selected motif bytes changed')
    require(variant['id'] not in {r['id'] for r in job['rasters']}, 'Candidate ID already occupied')
    used = job['budgets']['used']['raster_candidates']
    require(max(used, len(job['rasters'])) < job['budgets']['limits']['raster_candidates'], 'Candidate budget exhausted')
    options_list = job['parameters']['approved']
    parameters = {'width': design['width'], 'height': design['height'], 'mode': design['mode'],
                  'foreground_colors': len(design['palette']), 'method': variant['method'],
                  'fit': design['fit'], 'actual_crop': design['crop']}
    require(any(parameters in p['imports'] if 'imports' in p else
                (p['mode'] == design['mode'] and all(p['size_constraint'] != 'exact' or p[k] == design[k]
                 for k in ('width', 'height')) and (p['foreground_color_constraint'] != 'exact' or
                 p['foreground_colors'] == parameters['foreground_colors'])) for p in options_list),
            'Design outside the approved motif parameters')
    design_file = scratch / 'design.json'
    design_file.write_bytes(current.encoded(design))
    output = scratch / 'candidates'
    result = current_tools.image(io.safe(root, motif['file']['file']), design_file, output,
                                 puzzle_id=req['job'], name=job['title'], profile=options['profile'])
    candidate, = result['candidates']
    row = {'id': candidate['id'], 'label': options['label'], 'review': {}, 'exceptions': []}
    files = []
    for field, ref in candidate['files'].items():
        row[field] = None
        if ref is not None:
            name = f'content/authoring/{req["job"]}/data/{candidate["id"]}/{ref["file"]}'
            row[field] = {**ref, 'file': name}
            files.append({'path': name, 'source': ref['file'], 'bytes': ref['bytes'], 'sha256': ref['sha256']})
    draft = deepcopy(job)
    draft['rasters'].append(row)
    draft['budgets']['used']['raster_candidates'] = max(used, len(job['rasters'])) + 1
    draft['state'] = 'raster_review'
    current.build({'format': current.REQUEST, 'record': draft, 'expected': io.checksum(current.encoded(job)),
                   'files': files}, output / candidate['id'], root)
    return {'raster': candidate['id'], 'certified': candidate['certified'], 'files': {k: row[k] for k in candidate['files']},
            'next': 'Inspect the published raster, proof and preview before making a visual judgment.'}


def step4(req, job, root, scratch):
    """Store the exact derivatives first. Assessments refer to their saved bytes."""
    require(job['format'] in current.findings.FORMATS and job['operation'] == 'production'
            and job['state'] in ('background_review', 'content_ready'), 'Expected a current background offer')
    draft = deepcopy(job)
    selected = draft['selected']['background']
    offers = {a['id']: a for a in draft['assets'] if a['role'] == 'background'
              and selected in (None, a['id'])}
    options = req['input']
    files = []
    if 'prepare' in options:
        require(set(options['prepare']) == set(offers), 'Different background candidate inventory')
        for key in options['prepare']:
            asset = offers[key]
            if asset['prepared'] is not None:
                continue
            original = asset['file']
            source = io.safe(root, original['file'])
            require(current.content.ref(original['file'], io.read(root, original['file'], 32 * current.LIMIT))
                    == original, 'Background original changed')
            rendered = current.prepare_background(source, scratch / (key + '.png'), profile_id=asset['profile'])
            path = f'content/authoring/{draft["puzzle_id"]}/data/prepared/{key}/{rendered["sha256"]}.png'
            asset['prepared'] = {'original_sha256': original['sha256'], 'profile': asset['profile'], 'inspection': None,
                                 'file': {**rendered, 'file': path}}
            files.append({'path': path, 'source': rendered['file'], 'bytes': rendered['bytes'], 'sha256': rendered['sha256']})
    else:
        viewed = options['assessment']
        asset = offers.get(viewed['candidate'])
        require(asset and asset['prepared'] and viewed['profile'] == asset['profile']
                and viewed['original_sha256'] == asset['file']['sha256']
                and viewed['sha256'] == asset['prepared']['file']['sha256'], 'Different prepared background')
        require(set(viewed['review']) == current.CRITERIA['background']
                and all(r['timestamp_utc'] and r['result'] != 'nicht geprüft' for r in viewed['review'].values()),
                'Incomplete background assessment')
        original_review = (asset['prepared'].get('inspection') or {}).get('original_review', asset['review'])
        asset['prepared']['inspection'] = {'sha256': viewed['sha256'], 'review': deepcopy(viewed['review']),
                                           'original_review': deepcopy(original_review)}
        observations(draft, asset['id'], viewed['observations'])
        # Summary keeps the worse result for each criterion across the two images.
        order = ('erfüllt', 'Warnung', 'nicht erfüllt', 'nicht geprüft')
        for criterion, finding in viewed['review'].items():
            original = original_review.get(criterion)
            require(original and original['timestamp_utc'] and original['result'] != 'nicht geprüft',
                    'Original background assessment missing')
            if order.index(finding['result']) > order.index(original['result']):
                asset['review'][criterion] = deepcopy(finding)
    current.build({'format': current.REQUEST, 'record': draft, 'expected': io.checksum(current.encoded(job)),
                   'files': files}, scratch, root)
    return {'backgrounds': list(offers)}


def finalize(req, job, root, scratch):
    require(job['operation'] == 'production' and job['state'] in
            ('background_review', 'content_ready', 'editorially_approved'), 'Expected a selected raster for finalization')
    draft = deepcopy(job)
    selection = req['input']['background']
    if selection is not None:
        require(draft['selected']['background'] in (None, selection), 'Changed prior background choice')
        draft['selected']['background'] = selection
    chosen = draft['selected']['background']
    if chosen not in (None, 'none', 'standard') and draft['format'] in current.findings.FORMATS:
        prepared = current.findings.subjects(draft)[chosen]['prepared']
        require(prepared and (prepared.get('inspection') or 'inspection' not in prepared and job['selected']['background'] == chosen),
                'Complete the prepared background assessment in step 4')
    for declaration in req['input'].get('finding_decisions', []):
        target, key = declaration['target'], declaration['id']
        require(target in (*draft['selected'].values(), current.findings.COMBINATION), 'Unselected finding')
        row = next((r for r in draft.get('findings', []) if (r['target'], r['id']) == (target, key)), None)
        require(row is not None and row['decision'] is None, 'Expected an existing undecided finding')
        current.findings.declare(row, **{k: v for k, v in declaration.items() if k not in ('target', 'id')})
    for choice in req['input']['decisions']:
        binding = current.binding(draft, choice['scope'])
        require(choice.get('binding', binding) == binding, 'Stale decision: ' + choice['scope'])
        choice = {**choice, 'binding': binding}
        existing = next((d for d in draft['decisions'] if d['scope'] == choice['scope']), None)
        require(existing in (None, choice), 'Changed prior decision')
        if existing is None:
            draft['decisions'].append(choice)
    require(draft['selected']['background'] and {'background', 'final', 'integration'} <=
            {d['scope'] for d in draft['decisions']}, 'Actual final and integration decisions required')
    draft['state'] = 'editorially_approved'
    authoring_builder.finalize_background({'format': current.REQUEST, 'record': draft,
        'expected': io.checksum(current.encoded(job)), 'files': []}, scratch, root)
    return draft


def package(req):
    return {'format': 'development-ci-plan/v1', 'issue': f'https://github.com/{req["repository"]}/issues/{req["issue"]}',
            'package': 'Integration-' + req['job'], 'modules': [], 'purpose': 'Gewählte finale Rätseldaten registrieren.',
            'omitted': 'Reine Inhaltsintegration. Adapter und registrierte Lieferung im Produktionslauf geprüft.',
            'test_changes': [], 'core_change': None, 'evidence': {'mode': 'none', 'purpose': None, 'expires': None}}


def step5(req, request_id, job, root, product, scratch):
    finalize(req, job, root, scratch)
    name = current.path(req['job'])
    exported = scratch / 'export'
    operation = catalog_integration.Registration(current.prepare_input(root, name, exported))
    plan = operation.run(product)
    require(plan['status'] == 'planned' and not ws.changes(product), 'Expected new registration and a clean read-only plan')
    registered = operation.run(product, apply=True)
    require(registered['status'] == 'registered' and registered['changes'] == plan['changes'],
            'Fresh registration differs from selected plan')
    paths = {r['path'] for r in plan['changes']}
    plan_path = '.ci/package.json'
    require(all(n.startswith(('game/', 'content/')) and not n.startswith('content/authoring/') for n in paths),
            'Unexpected product path')
    # The package plan can be sparse-hidden. Compare its tracked version before replacement.
    plan_file = io.safe(product, plan_path)
    existing = io.read(product, plan_path, current.LIMIT, missing=True)
    if existing is not None:
        require(existing == publish_git.git(product, 'show', req['main'] + ':' + plan_path), 'Product plan changed')
    current._atomic(product, plan_path, current.encoded(package(req)))
    paths.add(plan_path)
    ws.git(product, 'add', '--sparse', '--', *sorted(paths))
    staged = publish_git.git(product, 'diff', '--cached', '--no-renames', '--name-only', '-z').split(b'\0')[:-1]
    require({n.decode() for n in staged} == paths, 'Staged product differs from the planned delivery')
    ws.git(product, 'commit', '--no-gpg-sign', '-qm', 'Integrate ' + req['job'] + '\n\nPW-Remote: ' + request_id)
    commit = ws.git(product, 'rev-parse', 'HEAD')
    require(ws.git(product, 'show', '-s', '--format=%P', commit) == req['main'] and not ws.changes(product),
            'Committed product differs from the bound worktree')
    current.complete(root, name, commit, current_input=exported)
    return commit
