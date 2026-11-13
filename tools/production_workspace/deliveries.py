"""Bounded metadata proof of concrete deliveries in a freshly observed main.

This reader does not certify a package again. An original registration binds
the delivery and its earlier authoring bytes; main must contain the same
delivery, directly or through an existing retirement receipt. No PR state,
revision order, branch ancestry, ZIP, image or writer participates.
"""
from copy import deepcopy

from tools.puzzle_production import authoring_package as ap, catalog_io as io
from tools.puzzle_production import catalog_background as background, content_registry as registry
from tools.puzzle_production import reveal_source as reveal
from tools.puzzle_production.authoring_finalization import RECORD_KEYS
from tools.puzzle_production.contract import exact_keys
from . import presentation as p
from .sources import JSON_LIMIT

MAX_REGISTRATIONS = 32
COMPLETION_STEP = '5 · Lokal registriert; unabhängiges Review und Git-/Mainabschluss prüfen'
UNREADABLE = (ValueError, OSError, KeyError, TypeError, AttributeError)


def rows(value):
    ap.require(isinstance(value, dict), 'Register muss ein JSON-Objekt sein.')
    entries = value.get('entries')
    ap.require(isinstance(entries, list) and len(entries) <= 10000 and
               all(isinstance(e, dict) and isinstance(e.get('id'), str) for e in entries),
               'Registereinträge fehlen oder sind ungültig.')
    result = {entry['id']: entry for entry in entries}
    ap.require(len(result) == len(entries), 'Mehrdeutige Registeridentität.')
    return result


def completed_record(before, integration):
    """Only the existing projector.complete transition may differ historically."""
    exact_keys(before, RECORD_KEYS | {'raster_selection', 'presentation', 'candidate'})
    ap.require(before['format'] == 'picross-authoring-record-v3' and
               before['state'] == 'editorially_approved' and before['integration'] is None and
               isinstance(before['verification'], dict) and
               before['verification'].get('effective_state') == 'editorially_approved',
               'Gebundener Lieferstand ist nicht die ursprüngliche Endabnahme.')
    return {**before, 'state': 'registered', 'integration': integration, 'blockers': [],
            'next_step': COMPLETION_STEP}


def completed_projection(before, record_raw, record_file):
    value = deepcopy(before)
    for ref in [value['record'], *(offer['record'] for offer in value['offers'])]:
        if ref['commit'] is None and ref['file'] == record_file:
            ref.update(sha256=io.checksum(record_raw), bytes=len(record_raw))
    return value


class Deliveries:
    def __init__(self, repository, sources):
        self.repository = repository
        self.main = next((s['commit'] for s in sources if s['source'] == 'remote' and
                          s['ref'] == 'main' and s['commit'] == repository.confirmed_main), None)
        self.source = repository.cached
        self.entries, self.runtime, self.backgrounds = {}, {}, {}
        self.images, self.observed_images = {}, {}
        self.authorities, self.observed_deliveries = {}, {}

    def read(self, name, *, missing=False, limit=JSON_LIMIT):
        raw = self.source.read(self.main, name, limit, missing=missing)
        return p.parse(raw, limit) if raw is not None else None

    def main_registry(self):
        value = self.read(registry.REGISTRY, limit=8 * JSON_LIMIT)
        ap.require(isinstance(value, dict) and value.get('format') in (registry.FORMAT, registry.BACKGROUND_FORMAT, registry.METADATA_FORMAT),
                   'Unbekanntes Mainregister.')
        registry.validate_entries(value['entries'])
        self.entries = rows(value)
        self.backgrounds = background.index(value)
        runtime = self.read(registry.RUNTIME, limit=8 * JSON_LIMIT)
        ap.require(isinstance(runtime, dict) and runtime.get('format') in tuple('picross-runtime-registry-v' + str(n) for n in range(2, 9)),
                   'Unbekanntes Main-Runtimeregister.')
        self.runtime = rows(runtime)

    def same_delivery(self, record, source):
        """Validate historical whole-register hashes, then compare only this row."""
        integration = p.registration(source, record)
        old_registry = p.parse(source.read(integration['commit'], registry.REGISTRY, 8 * JSON_LIMIT), 8 * JSON_LIMIT)
        original = rows(old_registry)[record['puzzle_id']]
        registry.validate_entries([original])
        current = self.entries.get(record['puzzle_id'])
        ap.require(current is not None, 'Diese Lieferung ist auf main nicht registriert.')
        normalized = deepcopy(current)
        raw = self.source.read(self.main, integration['manifest']['file'], 8 * JSON_LIMIT)
        ap.require(io.checksum(raw) == current['production']['package_sha256'], 'Main-Paketbindung unterscheidet sich.')
        manifest = p.parse(raw, 8 * JSON_LIMIT)
        ap.require(isinstance(manifest, dict), 'Main-Paketbeleg muss ein JSON-Objekt sein.')
        retired = manifest.get('format') in (reveal.RECEIPT, reveal.BACKGROUND_RECEIPT, reveal.EDITOR_RECEIPT)
        original_manifest = p.parse(source.read(integration['commit'], integration['manifest']['file'], 8 * JSON_LIMIT), 8 * JSON_LIMIT)
        if retired:
            from tools.puzzle_production.content_update import notice_path
            notice = 'runtime/' + notice_path(original).removeprefix('game/')
            reveal.receipt(manifest, original, ap.sha(original_manifest['files'][notice]), background=True, editor=True)
            normalized['production']['package_sha256'] = manifest['entry']['production']['package_sha256']
        else:
            p.bind(raw, integration['manifest'])
        ap.require(normalized == original, 'Main enthält eine andere konkrete Lieferung.')

        # Current image authorities preserve immutable production, even after
        # retirement or independent image work. Read only their bound metadata.
        bg = None
        closed_images = {background.path(record['puzzle_id']): {None}, reveal.path(record['puzzle_id']): {None}}
        ref = self.backgrounds.get(record['puzzle_id'])
        if ref is not None:
            bg_raw = p.bind(self.source.read(self.main, ref['file']), ref)
            bg = background.validate(p.parse(bg_raw), normalized)
            closed_images[ref['file']].add(io.checksum(bg_raw))
            # Existing compact authorities retain prior complete source forms.
            # Admit only those exact bytes, never arbitrary work sharing an
            # export anchor. All objects were bounded by the pure validator.
            prior = bg
            for _ in range(4):
                closed_images[ref['file']].add(io.checksum(p.data(prior)))
                if prior['format'] == background.EDITOR_FORMAT:
                    prior = prior['origin']['source']
                elif prior['format'] in background.REBIND_FORMATS:
                    prior = prior['base']
                elif prior['format'] == background.CHANGE_FORMAT:
                    prior = prior['initial']
                else:
                    break
                if prior is None:
                    break
            anchor = (bg['binding']['entry']['production']['package_sha256'] if bg['format'] == background.EDITOR_FORMAT else
                      bg['events'][-1]['binding']['entry']['production']['package_sha256'] if bg['format'] in background.REBIND_FORMATS else
                      background.initial(bg)['origin']['export_manifest_sha256'])
            ap.require(anchor == integration['manifest']['sha256'], 'Hintergrund bindet eine andere Lieferung.')
            initial = background.initial(bg)
            if initial is not None and initial['origin']['package'] == original['production']['package']:
                origin = initial['origin']
                ap.require(origin['original_package']['original_zip_sha256'] == record['package']['sha256'] and
                           origin['approval_ref']['sha256'] == original_manifest['approval_sha256'] and
                           all(origin['original_package'][key] == original_manifest[key]
                               for key in ('handoff_sha256', 'inventory_sha256')),
                           'Hintergrund verliert die ursprüngliche Paket-/Abnahmebindung.')
        ap.require(record['background'] is None or bg is not None, 'Main-Hintergrundbeleg fehlt.')
        if retired:
            if manifest['format'] == reveal.EDITOR_RECEIPT:
                ap.require(bg is not None and bg['format'] == background.EDITOR_FORMAT, 'Editor-Abschlussbeleg ohne Bildautorität.')
                background.check_editor_receipt(bg, manifest, normalized)
            elif manifest['format'] == reveal.BACKGROUND_RECEIPT:
                ap.require(bg is not None, 'Hintergrund-Abschlussbeleg ohne Bildautorität.')
                background._receipt(bg, ref, manifest)
            else:
                ap.require(bg is None or bg['format'] == background.EDITOR_FORMAT,
                           'Abschlussbeleg verliert die Hintergrundbindung.')
                if bg is not None:
                    background.check_editor_receipt(bg, manifest, normalized)

        effective_reveal = original['reveal']
        image_raw = self.source.read(self.main, reveal.path(record['puzzle_id']), missing=True)
        image = p.parse(image_raw) if image_raw is not None else None
        if image is not None:
            reveal.validate(image, None, historical_categories=True)
            closed_images[reveal.path(record['puzzle_id'])].add(io.checksum(image_raw))
            if image['format'] == reveal.EDITOR_FORMAT and image['origin']['source'] is not None:
                closed_images[reveal.path(record['puzzle_id'])].add(io.checksum(p.data(image['origin']['source'])))
            binding = image['binding'] if image['format'] == reveal.EDITOR_FORMAT else image['bindings'][-1]
            ap.require(binding['entry'] == normalized, 'Abschlussbild bindet eine andere Lieferung.')
            if image['format'] == reveal.EDITOR_FORMAT:
                effective_reveal = image['current']['asset']['file'].removeprefix('game/')
        runtime = self.runtime.get(record['puzzle_id'])
        ap.require(runtime is not None and all(runtime[k] == original[k] for k in ('id', 'key', 'definition', 'save_slot')) and
                   runtime['reveal'] == effective_reveal, 'Main-Runtime gehört nicht zur Lieferung.')
        self.images[record['puzzle_id']] = closed_images
        old_runtime = rows(p.parse(source.read(integration['commit'], registry.RUNTIME, 8 * JSON_LIMIT), 8 * JSON_LIMIT))
        self.authorities[record['puzzle_id']] = {
            'entries': (original, current), 'runtime': (old_runtime[record['puzzle_id']], runtime),
            'manifest': integration['manifest']['file'],
            'hashes': {integration['manifest']['sha256'], current['production']['package_sha256']}}
        return integration

    def historical_jobs(self, job):
        record = job['_record']
        ap.require(record.get('state') == 'registered', 'Kein Registrierungsbeleg.')
        integration = self.same_delivery(record, job['_source'])
        history = self.repository.scan(job['_source'], integration['commit'], job['puzzle_id'])
        candidates = history['jobs']
        before = next((old for old in candidates if old['revision'] == job['revision']), None)
        ap.require(before is not None and not before.get('_current_invalid'), 'Historischer Lieferzusammenhang fehlt.')
        expected = completed_record(before['_record'], integration)
        expected_raw = p.data(expected)
        projection = completed_projection(before['_projection'], expected_raw, job['_projection']['record']['file'])
        ap.require(record == expected and job['_projection'] == projection and
                   job['binding'] == io.checksum(p.data(projection) + expected_raw),
                   'Aktuelle Quelle unterscheidet sich von der gebundenen Lieferung.')
        # Never infer earlier work by naming or revision order. Every old pair
        # must actually occur byte-for-byte in this explicitly bound snapshot.
        old_pairs = {(old['puzzle_id'], old['revision'], old['_fingerprint']) for old in candidates
                     if not old.get('_current_invalid')} if before['current_view'] else set()
        pairs = old_pairs | {(job['puzzle_id'], job['revision'], job['binding'])}
        return pairs, {'source': job['_source'], 'commit': integration['commit']}

    def originals_match(self, job, history):
        """Compare Git object identities, without opening a ZIP or an image.

        Matching outer records cannot conceal changed originals or independent
        source image work at a different commit of a local/remote copy.
        """
        record, projection = job['_record'], job['_projection']
        paths = {record['package']['file'], record['handoff']['file']}
        approval = record.get('final_editorial_approval')
        if approval is not None:
            paths.add(approval['file'])
        for offer in projection['offers']:
            ref = offer['record']
            if ref['commit'] is None and ref['file'] != projection['record']['file']:
                paths.add(ref['file'])
        for asset in projection['assets']:
            loc = asset['location']
            if loc['commit'] is None:
                paths.add(loc['container']['file'] if loc['storage'] == 'package' else loc['file'])
        if record['background'] is not None:
            for key in ('manifest', 'decision', 'derivation'):
                stored = record['background'].get(key)
                if stored is not None and stored['storage'] == 'external':
                    paths.add(stored['root'].rstrip('/') + '/' + stored['ref']['file'])
        for name in paths:
            old = history['source'].blob(history['commit'], name, missing=True)
            current = job['_source'].blob(job['commit'], name, missing=True)
            ap.require(old is not None and current == old, 'Gebundene Originaldatei fehlt oder unterscheidet sich.')
        key = (str(job['_source'].root), job['commit'], job['puzzle_id'])
        authority = self.authorities[job['puzzle_id']]
        if key not in self.observed_deliveries:
            state = {}
            for field, name in (('entry', registry.REGISTRY), ('runtime', registry.RUNTIME)):
                raw = job['_source'].read(job['commit'], name, 8 * JSON_LIMIT, missing=True)
                state[field] = rows(p.parse(raw, 8 * JSON_LIMIT)).get(job['puzzle_id']) if raw is not None else None
            raw = job['_source'].read(job['commit'], authority['manifest'], 8 * JSON_LIMIT, missing=True)
            state['manifest'] = io.checksum(raw) if raw is not None else None
            self.observed_deliveries[key] = state
        observed = self.observed_deliveries[key]
        if observed['entry'] is None:
            ap.require(record['state'] != 'registered' and observed['runtime'] is None,
                       'Registrierungszuordnung fehlt an dieser Quelle.')
            ap.require(observed['manifest'] is None or observed['manifest'] in authority['hashes'],
                       'Neuer unregistrierter Export bleibt offen.')
        else:
            ap.require(observed['entry'] in authority['entries'] and observed['runtime'] in authority['runtime'] and
                       observed['manifest'] in authority['hashes'] and
                       observed['entry']['production']['package_sha256'] == observed['manifest'],
                       'Abweichende Paket-/Runtimebindung ist noch nicht in main belegt.')
        if key not in self.observed_images:
            self.observed_images[key] = {
                name: io.checksum(raw) if (raw := job['_source'].read(job['commit'], name, missing=True)) is not None else None
                for name in self.images[job['puzzle_id']]}
        for name, observed in self.observed_images[key].items():
            ap.require(observed in self.images[job['puzzle_id']][name], 'Eigenständige Bildarbeit ist noch nicht in main belegt.')
            if record['state'] == 'registered' and name.startswith('content/backgrounds/') and record['background'] is not None:
                ap.require(observed is not None, 'Registrierter Hintergrundbeleg fehlt an dieser Quelle.')
        return True

    def filter(self, jobs):
        result = {'confirmed': False, 'main_commit': self.main, 'hidden_count': 0,
                  'completed_ids': [], 'hidden_jobs': [], 'note': ''}
        if not self.main:
            result['note'] = ('Main ist in diesem Quellenstand nicht aktuell bestätigt. '
                              'Vorhandene Arbeit bleibt sichtbar; Quellen mit main aktualisieren.')
            return jobs, result
        try:
            self.main_registry()
        except UNREADABLE:
            result['note'] = 'Main wurde gefunden, seine Lieferbelege sind nicht lesbar. Vorhandene Arbeit bleibt sichtbar.'
            return jobs, result
        result['confirmed'] = True
        proven, attempted, uncertain = {}, set(), False
        for job in jobs:
            if job['_record'].get('state') != 'registered' or job.get('_current_invalid'):
                continue
            key = (str(job['_source'].root), job['commit'], job['binding'])
            if key in attempted:
                continue
            if len(attempted) >= MAX_REGISTRATIONS:
                uncertain = True
                continue
            attempted.add(key)
            try:
                pairs, history = self.historical_jobs(job)
                for pair in pairs:
                    proven.setdefault(pair, []).append(history)
            except UNREADABLE:
                uncertain = True
        remaining, hidden = [], []
        registered_snapshots = {(str(j['_source'].root), j['commit'], j['puzzle_id']) for j in jobs
                                if j['_record'].get('state') == 'registered'}
        for job in jobs:
            matched = False
            resumed = (job['current_view'] and job['_record'].get('state') != 'registered' and
                       (str(job['_source'].root), job['commit'], job['puzzle_id']) in registered_snapshots)
            for history in proven.get((job['puzzle_id'], job['revision'], job['binding']), []):
                if job.get('_current_invalid') or resumed:
                    uncertain = True
                    break
                try:
                    matched = self.originals_match(job, history)
                    break
                except UNREADABLE:
                    uncertain = True
            if matched:
                hidden.append({key: job[key] for key in ('puzzle_id', 'revision', 'binding', 'commit', 'source', 'ref')})
            else:
                remaining.append(job)
        result.update(hidden_count=len(hidden), hidden_jobs=hidden,
                      completed_ids=sorted({j['puzzle_id'] for j in hidden} - {j['puzzle_id'] for j in remaining}))
        result['note'] = (f'Main aktuell bestätigt: {len(hidden)} eindeutig abgeschlossene Quellen ausgeblendet. '
                          'Offene Arbeit bleibt sichtbar.')
        if uncertain:
            result['note'] += ' Nicht eindeutig belegte Lieferungen bleiben ebenfalls sichtbar.'
        return remaining, result


def active(repository, sources, jobs):
    return Deliveries(repository, sources).filter(jobs)
