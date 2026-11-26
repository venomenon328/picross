"""Validate a single Drive delivery against the locally activated production order."""
from copy import deepcopy
from pathlib import PurePosixPath
from uuid import UUID

from tools.puzzle_production import catalog_io as io, current_authoring as current
from tools.puzzle_production.authoring_package import require
from tools.puzzle_production.contract import exact_keys

FORMAT = 'picross-production-inbox-v1'
REPOSITORY = 'venomenon328/picross'
PHASES = {'reveal': 'reveal_review', 'motif': 'motif_review', 'background': 'background_review'}
PRIOR = {'motif': 'reveal', 'background': 'raster'}


def uuid4_text(value):
    require(isinstance(value, str), 'UUID fehlt.')
    parsed = UUID(value)
    require(parsed.version == 4 and str(parsed) == value, 'Kanonische kleine UUIDv4 erforderlich.')
    return value


def envelope(raw, filename, order):
    value = io.json_bytes(raw, 2 * current.LIMIT)
    exact_keys(value, {'format', 'delivery_id', 'request_id', 'repository', 'puzzle_id', 'phase', 'source', 'request'})
    delivery = uuid4_text(value['delivery_id'])
    require(filename == delivery + '.json' and value['format'] == FORMAT, 'Liefername oder Format weicht ab.')
    require(uuid4_text(value['request_id']) == order['request_id'] and value['repository'] == REPOSITORY and
            all(value[key] == order[key] for key in ('puzzle_id', 'phase', 'source')), 'Lieferung gehört zu einem anderen Auftrag oder Stand.')
    request = value['request']
    exact_keys(request, {'format', 'record', 'expected', 'files'})
    require(request['format'] == current.REQUEST and request['expected'] == order['source']['record_sha256'],
            'Builderrequest ist nicht an den erwarteten Record gebunden.')
    record = request['record']
    require(isinstance(record, dict) and record.get('format') == current.findings.LOCAL and
            record.get('puzzle_id') == order['puzzle_id'] and record.get('operation') == 'production' and
            record.get('integration') is None and 'qualification' not in record, 'Aktueller v3-Draft ohne fremde Prüfergebnisse erforderlich.')
    current.validate(record)
    require(isinstance(request['files'], list) and len(request['files']) <= 100, 'Dateiinventar ungültig.')
    by_path = {a['file']['file']: a for a in record['assets'] if a['role'] == order['phase']}
    paths = set()
    for index, item in enumerate(request['files'], 1):
        exact_keys(item, {'path', 'source', 'bytes', 'sha256'})
        name = item['path']
        require(isinstance(name, str) and name in by_path and name.casefold() not in paths and
                current.own(record['puzzle_id'], name), 'Fremdes oder doppeltes Dateiziel.')
        require(PurePosixPath(name).name not in ('record.json', '.current-operation.json') and
                not any(part.startswith('.') for part in PurePosixPath(name).parts), 'Original kollidiert mit Produktionsmetadaten.')
        paths.add(name.casefold())
        suffix = PurePosixPath(name).suffix
        allowed = {'reveal': {'.png', '.svg'}, 'motif': {'.png', '.jpg', '.jpeg'}, 'background': {'.png'}}
        require(suffix in allowed[order['phase']] and item['source'] == f'{delivery}--{index}{suffix}',
                'Quelldateiname oder Bildtyp passt nicht zur Lieferung.')
        require(by_path[name]['file'] == {'file': name, 'bytes': item['bytes'], 'sha256': item['sha256']} and
                type(item['bytes']) is int and 0 < item['bytes'] <= 32 * current.LIMIT, 'Dateibindung weicht ab.')
    return value


def delta(order, request, previous):
    """Accept creative changes only on the declared role and selected correction base."""
    job = request['record']
    role, intent = order['phase'], order['intent']
    require(job['state'] == PHASES[role] and job['test_only'] is order['test_only'], 'Unzulässiger Phasen- oder Geltungswechsel.')
    prior = deepcopy(previous) if previous else {
        'format': current.findings.LOCAL, 'puzzle_id': order['puzzle_id'], 'revision': 'current',
        'source_commit': order['source']['main_commit'], 'operation': 'production', 'target': None,
        'brief': order['brief'], 'title': job['title'], 'category_id': job['category_id'],
        'assets': [], 'rasters': [], 'selected': dict.fromkeys(('reveal', 'motif', 'raster', 'background')),
        'decisions': [], 'parameters': {'proposed': [], 'approved': []},
        'instructions': {}, 'findings': [], 'blockers': [], 'test_only': order['test_only'], 'integration': None,
        'budgets': {'limits': order['limits'], 'used': dict.fromkeys(order['limits'], 0)}}
    prior.pop('qualification', None)
    require(previous or role == 'reveal' and intent == 'offer', 'Neuanlage beginnt mit einem Revealangebot.')
    for row in prior['findings']:
        binding = current.findings.binding(row)
        if binding in order.get('declarations', {}):
            row['decision'] = order['declarations'][binding]
    choice = order.get('choice')
    if choice:
        scope = PRIOR[role]
        require(prior['selected'][scope] in (None, choice['id']), 'Andere Vorauswahl ist bereits gebunden.')
        prior['selected'][scope] = choice['id']
        prior['decisions'] = [d for d in prior['decisions'] if d['scope'] != scope] + [
            {**choice['decision'], 'binding': current.binding(prior, scope)}]
    if intent == 'correction' and order.get('target') == prior['selected'][role]:
        dependent = {'reveal': ('reveal', 'motif', 'raster', 'background'),
                     'motif': ('motif', 'raster', 'background'), 'background': ('background',)}[role]
        for scope in dependent:
            prior['selected'][scope] = None
        prior['decisions'] = [d for d in prior['decisions'] if d['scope'] not in (*dependent, 'final', 'integration')]
        prior['assets'] = [a for a in prior['assets'] if a['role'] not in dependent[1:]]
        if 'raster' in dependent:
            prior['rasters'] = []
            prior['parameters']['approved'] = []
        if role == 'reveal':
            prior['parameters']['proposed'] = []
        retained = current.findings.subjects(prior)
        prior['findings'] = [r for r in prior['findings'] if r['target'] in retained]
    prior = current.compact(prior)
    old = {a['id']: a for a in prior['assets'] if a['role'] == role}
    new = {a['id']: a for a in job['assets'] if a['role'] == role}
    require(new and prior['selected'][role] is None, 'Diese Auswahl ist nicht offen.')
    require([a for a in job['assets'] if a['role'] != role] == [a for a in prior['assets'] if a['role'] != role],
            'Fremde Bildrolle verändert.')
    target = order.get('target')
    if intent == 'assessment':
        require(set(old) == set(new) and not request['files'], 'Bewertungsfortschreibung enthält neue Originale.')
        editable = {target}
    elif intent == 'correction':
        require(target in old and target not in new and len(new.keys() - old.keys()) == 1 and
                old.keys() - new.keys() == {target}, 'Genau eine gebundene Korrektur erforderlich.')
        editable = new.keys() - old.keys()
        require(new[next(iter(editable))]['file']['sha256'] != old[target]['file']['sha256'], 'Korrektur benötigt neue Originalbytes.')
        prior['budgets']['used']['image_corrections'] += 1
    else:
        require(intent == 'offer' and old.keys() <= new.keys(), 'Angebot darf keine bestehende Variante entfernen.')
        editable = new.keys() - old.keys()
        require(editable, 'Angebot enthält keine neue Variante.')
    for key in new.keys() & old.keys():
        if key in editable:
            require({k: v for k, v in new[key].items() if k != 'review'} ==
                    {k: v for k, v in old[key].items() if k != 'review'}, 'Bewertung ändert Original oder Herkunft.')
        else:
            require(new[key] == old[key], 'Unbeauftragte Änderung einer bestehenden Variante.')
    for key in editable:
        if key not in old:
            require(new[key].get('prepared') is None, 'Aufbereitung erfolgt nach dem Originaleingang.')
    required = {new[key]['file']['file'] for key in editable if key not in old}
    require(required == {item['path'] for item in request['files']}, 'Dateiliste entspricht nicht den neuen Originalen.')
    keep = set(editable) | ({target} if intent == 'correction' else set())
    require([r for r in job['findings'] if r['target'] not in keep] == [r for r in prior['findings'] if r['target'] not in keep],
            'Fremde Sichtbefunde verändert.')
    for row in job['findings']:
        if row['target'] in editable and row.get('decision'):
            require(row in prior['findings'] or row['decision']['source'] and intent == 'correction' and
                    row['decision']['source']['target'] == target, 'Keine Befundannahme durch den Lieferanten.')
    if intent == 'assessment':
        require(all(r in job['findings'] for r in prior['findings'] if r['target'] == target and r['decision']),
                'Gebundene Befundentscheidung verändert.')
    prior['instructions'] = {k: v for k, v in prior['instructions'].items() if k in current.findings.subjects(job)}
    if role == 'motif' and intent != 'assessment':
        prior['parameters']['proposed'] = job['parameters']['proposed']
    changed = {'state', 'assets', 'findings'}
    require({k: v for k, v in job.items() if k not in changed} == {k: v for k, v in prior.items() if k not in changed},
            'Recorddelta überschreitet die Auftragsbindung.')
    current.check_transition(previous, job)
