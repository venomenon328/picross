"""Closed PW-A contract and original-source cross checks, without certification."""
from copy import deepcopy
from io import BytesIO
from pathlib import PurePosixPath as PurePath
import re
import warnings

from tools.puzzle_production import authoring_package as ap, catalog_io as io
from tools.puzzle_production.authoring_build_contract import names
from tools.puzzle_production.authoring_builder import index_value
from tools.puzzle_production.authoring_finalization import RECORD_KEYS
from tools.puzzle_production.background_contract import validate_manifest, BackgroundError
from tools.puzzle_production.background_package import validate_binding
from tools.puzzle_production.contract import InvalidInput, canonical_bytes, exact_keys, integer, load_json
from .sources import Archive, JSON_LIMIT, INDEX, check_commit, production_path

FORMAT = 'picross-production-presentation-v1'
REQUEST = 'picross-production-presentation-request-v1'
ROLES = ('reveal', 'motif', 'raster', 'raster_draft', 'background')
OPTION = re.compile(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}\Z')


class RawJSON:
    def __init__(self, raw):
        self.raw = raw

    def open(self, _mode):
        return BytesIO(self.raw)


def parse(raw, limit=JSON_LIMIT):
    return load_json(RawJSON(raw), limit)


def data(value):
    return canonical_bytes(value) + b'\n'


def text(value):
    ap.string(value, 'Anzeigetext', 512)
    ap.require(not any(ord(c) < 32 or ord(c) == 127 for c in value), 'Anzeigetext enthält Steuerzeichen.')


def reference(value, measured):
    exact_keys(value, {'commit', 'file'} | ({'sha256', 'bytes'} if measured else set()))
    if value['commit'] is not None:
        check_commit(value['commit'])
    production_path(value['file'])
    if measured:
        ap.sha(value['sha256'])
        integer(value['bytes'], 0, ap.MAX_ZIP, 'Dateigröße')


def validate(value, measured=True):
    value = parse(data(value))
    exact_keys(value, {'format', 'puzzle_id', 'revision', 'record', 'title', 'assets', 'offers'})
    ap.require(value['format'] == (FORMAT if measured else REQUEST), 'Unbekanntes Projektionsformat.')
    ap.require(isinstance(value['puzzle_id'], str) and ap.ID.fullmatch(value['puzzle_id']), 'Ungültige Rätsel-ID.')
    ap.require(isinstance(value['revision'], str) and ap.REVISION.fullmatch(value['revision']), 'Ungültige Revision.')
    reference(value['record'], measured)
    expected = f"content/authoring/{value['puzzle_id']}/{value['revision']}/record.json"
    ap.require(value['record']['file'] == expected and value['record']['commit'] is None,
               'Äußerer Record muss der aktuellen kanonischen Revision entsprechen.')
    text(value['title'])
    ids = set()
    ap.require(isinstance(value['assets'], list) and len(value['assets']) <= 100, 'Zu viele Assets.')
    for a in value['assets']:
        exact_keys(a, {'id', 'role', 'caption', 'location'})
        ap.require(isinstance(a['id'], str) and OPTION.fullmatch(a['id']) and a['id'] not in ids, 'Asset-ID fehlt oder ist doppelt.')
        ids.add(a['id'])
        ap.require(a['role'] in ROLES, 'Unbekannte Bildrolle.')
        text(a['caption'])
        loc = a['location']
        exact_keys(loc, {'commit', 'storage', 'container', 'file'} | ({'sha256', 'bytes'} if measured else set()))
        if loc['commit'] is not None:
            check_commit(loc['commit'])
        ap.relative(loc['file'])
        if measured:
            ap.sha(loc['sha256'])
            integer(loc['bytes'], 1, 32 * 1024 * 1024, 'Bilddateigröße')
        ap.require(loc['storage'] in ('repository', 'package'), 'Unbekannter Bildspeicher.')
        if loc['storage'] == 'repository':
            ap.require(loc['container'] is None, 'Direktdatei darf keinen Container haben.')
            production_path(loc['file'])
        else:
            if measured:
                exact_keys(loc['container'], {'file', 'sha256', 'bytes'})
                production_path(loc['container']['file'])
                ap.sha(loc['container']['sha256'])
                integer(loc['container']['bytes'], 1, ap.MAX_ZIP, 'Paketgröße')
            else:
                production_path(loc['container'])
    offered = set()
    ap.require(isinstance(value['offers'], list) and len(value['offers']) <= 20, 'Zu viele Angebote.')
    for offer in value['offers']:
        exact_keys(offer, {'id', 'kind', 'label', 'record', 'asset_ids'})
        ap.require(isinstance(offer['id'], str) and OPTION.fullmatch(offer['id']) and offer['id'] not in offered,
                   'Angebots-ID fehlt oder ist doppelt.')
        offered.add(offer['id'])
        ap.require(offer['kind'] in ('reveal', 'raster', 'background'), 'Unbekannte Angebotsart.')
        text(offer['label'])
        reference(offer['record'], measured)
        ap.require(isinstance(offer['asset_ids'], list) and 0 < len(offer['asset_ids']) <= 100 and
                   all(isinstance(n, str) and n in ids for n in offer['asset_ids']) and
                   len(set(offer['asset_ids'])) == len(offer['asset_ids']), 'Ungültige Angebotsbilder.')
    return value


def bind(raw, ref):
    ap.require(io.checksum(raw) == ref['sha256'] and ('bytes' not in ref or len(raw) == ref['bytes']),
               'Dateibindung stimmt nicht: ' + ref['file'])
    return raw


def image(raw):
    from PIL import Image
    ap.require(len(raw) <= 32 * 1024 * 1024 and raw.startswith((b'\x89PNG\r\n\x1a\n', b'\xff\xd8\xff')),
               'Nur PNG-/JPEG-Originale sind als Bild erlaubt.')
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(BytesIO(raw), formats=('PNG', 'JPEG')) as im:
                w, h = im.size
                ap.require(0 < w <= 8192 and 0 < h <= 8192 and w * h <= 8_000_000 and
                           getattr(im, 'n_frames', 1) == 1, 'Bildressourcengrenze überschritten.')
                im.verify()
            with Image.open(BytesIO(raw), formats=('PNG', 'JPEG')) as im:
                im.load()
                return {'width': w, 'height': h, 'mime': 'image/png' if im.format == 'PNG' else 'image/jpeg'}
    except (OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise InvalidInput('Bild ist beschädigt oder nicht dekodierbar.') from exc


class Record:
    """Read original package metadata and only referenced members, never replay logic."""
    def __init__(self, source, snapshot, ref, puzzle_id):
        self.source, self.commit = source, ref['commit'] if ref['commit'] is not None else snapshot
        self.raw = source.read(self.commit, ref['file'])
        if 'sha256' in ref:
            bind(self.raw, ref)
        self.value = r = parse(self.raw)
        exact_keys(r, RECORD_KEYS)
        ap.require(r['format'] == 'picross-authoring-record-v2' and r['puzzle_id'] == puzzle_id and
                   isinstance(r['revision'], str) and ap.REVISION.fullmatch(r['revision']), 'Recordgeneration oder Identität stimmt nicht.')
        self.directory = f"content/authoring/{puzzle_id}/{r['revision']}"
        ap.require(ref['file'] == self.directory + '/record.json', 'Nichtkanonischer Angebotsrecord.')
        ap.require(r['rulebook']['version'] == '0.7.0', 'Nur aktuelle veröffentlichte v3-/v2-Arbeitsstände sind lesbar.')
        ap.require(r['state'] in ('brief_ready', 'reveal_review', 'motif_review', 'motif_approved', 'raster_review',
                                 'raster_ready', 'content_ready', 'editorially_approved'), 'Unbekannter Produktionszustand.')
        ap.require(isinstance(r['verification'], dict) and isinstance(r['reveal_options'], list) and
                   isinstance(r['blockers'], list), 'Ungültige Recordmetadaten.')
        ap.sha(r['build_request_sha256'])
        ap.sha(r['inventory_sha256'])
        check_commit(r['repo_commit'])
        validate_binding(r['background'], package_only=False)
        ap.require(r['package']['file'] == self.directory + '/package.zip' and
                   r['handoff']['file'] == self.directory + '/handoff.json', 'Paket-/Handoffpfad stimmt nicht.')
        raw = source.read(self.commit, r['package']['file'], ap.MAX_ZIP)
        bind(raw, r['package'])
        self.archive = Archive(raw)
        try:
            handoff_raw = self.archive.read('handoff.json', JSON_LIMIT)
            ap.require(handoff_raw == source.read(self.commit, r['handoff']['file']), 'Äußerer Handoff unterscheidet sich vom Original.')
            bind(handoff_raw, r['handoff'])
            self.handoff = h = parse(handoff_raw)
            ap.require(h['format'] == 'picross-authoring-handoff-v3' and h['puzzle_id'] == puzzle_id and
                       h['revision'] == r['revision'] and h['rulebook'] == r['rulebook'], 'Handoffidentität stimmt nicht.')
            for key in ('reveal', 'motif'):
                ap.require(r[key] == h.get(key), 'Bildbezug weicht vom Handoff ab.')
            inv_raw = self.archive.read('inventory.json', JSON_LIMIT)
            bind(inv_raw, h['inventory'])
            ap.require(io.checksum(inv_raw) == r['inventory_sha256'], 'Inventarbindung stimmt nicht.')
            inv = parse(inv_raw)
            ap.require(inv['format'] == 'picross-authoring-file-inventory-v1' and
                       inv['puzzle_id'] == puzzle_id and inv['revision'] == r['revision'] and
                       inv.get('excludes') == ['inventory.json', 'handoff.json'], 'Inventaridentität stimmt nicht.')
            self.entries = {}
            for item in inv['files']:
                exact_keys(item, {'path', 'sha256', 'bytes'})
                ap.relative(item['path']); ap.sha(item['sha256'])
                integer(item['bytes'], 0, ap.MAX_FILE, 'Inventargröße')
                ap.require(item['path'] not in self.entries, 'Doppelter Inventareintrag.')
                self.entries[item['path']] = item
            names(list(self.entries))
            ap.require(set(self.archive.files) == set(self.entries) | {'handoff.json', 'inventory.json'}, 'Inventar und Paketsatz unterscheiden sich.')
            self.member(h['rulebook']['file'], h['rulebook']['sha256'])
            self.allowed, self.offer_keys = {role: {} for role in ROLES}, {}
            self._images()
            self.close()  # Retain only tiny validated metadata, not a ZIP per offered revision.
        except BaseException as exc:
            self.close()
            if isinstance(exc, BackgroundError):
                raise InvalidInput('Ungültiges Hintergrundmanifest: ' + str(exc)) from exc
            raise

    def close(self):
        self.archive.close()

    def member(self, name, expected=None):
        ap.relative(name)
        ap.require(name in self.entries, 'Datei ist nicht inventarisiert: ' + name)
        raw = self.archive.read(name)
        item = self.entries[name]
        ap.require(io.checksum(raw) == item['sha256'] and len(raw) == item['bytes'] and
                   (expected is None or expected == item['sha256']), 'Inventarisierte Bytes stimmen nicht: ' + name)
        return raw

    def json(self, name, expected=None):
        return parse(self.member(name, expected), 8 * JSON_LIMIT)

    def allow(self, role, ref, key=None):
        self.member(ref['file'], ref['sha256'])
        self.allowed[role][ref['file']] = ref['sha256']
        if key is not None:
            self.offer_keys[(role, key)] = ref['file']

    def provenance(self, ref, role):
        name = ref.get('provenance', str(PurePath(ref['file']).with_suffix('.provenance.json')))
        value = self.json(name)
        ap.require(value.get('puzzle_id') == self.value['puzzle_id'] and
                   value.get('file') == ref['file'] and value.get('sha256') == ref['sha256'],
                   'Bildherkunft stimmt nicht zum Original.')
        ap.string(value.get('author'), 'Bildurheber'); ap.string(value.get('usage_basis'), 'Nutzungsgrundlage')
        if role == 'motif':
            ap.require(ref.get('derived_from_reveal_sha256') == self.handoff['reveal']['sha256'] and
                       value.get('derived_from') == {k: self.handoff['reveal'][k] for k in ('file', 'sha256')},
                       'Motiv und Abschlussbild sind nicht passend gebunden.')
        if ref.get('approval'):
            approval = self.json(ref['approval'])
            ap.require(approval.get('type') == 'human_' + role + '_approval' and
                       approval.get('file') == ref['file'] and approval.get('sha256') == ref['sha256'],
                       'Überlieferte Bildentscheidung stimmt nicht zum Original.')
            self.member(approval['evidence'])

    def _images(self):
        h, r = self.handoff, self.value
        ap.require(not r['reveal_options'] or h.get('reveal') is None, 'Angebote und gewähltes Reveal widersprechen sich.')
        for offer in r['reveal_options']:
            exact_keys(offer, {'ID', 'Beschreibung', 'Datei', 'SHA-256'})
            ap.require(isinstance(offer['ID'], str) and OPTION.fullmatch(offer['ID']), 'Ungültige Revealoption.')
            self.allow('reveal', {'file': offer['Datei'], 'sha256': offer['SHA-256']}, offer['ID'])
            self.provenance({'file': offer['Datei'], 'sha256': offer['SHA-256']}, 'reveal')
        for role in ('reveal', 'motif'):
            if h.get(role) is not None:
                self.allow(role, h[role])
                self.provenance(h[role], role)
        c = h.get('candidate')
        if c:
            bundle, variant = ap.relative(c['bundle']), c['variant']
            ap.require(isinstance(variant, str) and re.fullmatch(r'[a-z][a-z0-9_-]{0,31}', variant), 'Ungültiger Rasterkandidat.')
            m = self.json(bundle + '/manifest.json')
            if m.get('format') in ('picross-image-manifest-v1', 'picross-image-manifest-v2'):
                candidates = [a for a in m['candidates'] if a['variant'] == variant]
                ap.require(len(candidates) == 1, 'Rasterkandidat fehlt oder ist doppelt.')
                name = variant + '-raster.png'
                candidate = self.json(bundle + '/' + variant + '-candidate.json', m['files'][variant + '-candidate.json'])
                ap.require(candidate['id'] == candidates[0]['id'] and candidate['variant']['id'] == variant,
                           'Kandidatenbindung stimmt nicht.')
                # Matrix and logic identities are checked directly; no solver call.
                from tools.puzzle_production.contract import digest
                ap.require(digest(candidate['matrix']) == c['matrix_hash'] and candidate['logic_hash'] == c['logic_hash'],
                           'Handoffkandidat passt nicht zu Matrix/Logik.')
                expected = m['files'][name]
                ready = candidates[0]['technical'].get('certified') is True
            elif m.get('format') in ('picross-repair-manifest-v1', 'picross-repair-manifest-v2'):
                repair = self.json(bundle + '/repair.json')
                ap.require(repair['id'] == c['repair_id'] == m['repair_id'], 'Reparaturkandidat stimmt nicht.')
                from tools.puzzle_production.contract import digest
                ap.require(digest(repair['matrix']) == c['matrix_hash'], 'Reparaturraster stimmt nicht.')
                name, expected = 'after.png', repair['files']['after.png']
                ready = self.json(bundle + '/result.json', repair['files']['result.json']).get('certified') is True
            else:
                raise InvalidInput('Rastermanifest wird nicht unterstützt.')
            v = r['verification']
            complete = (v.get('technical') is True and r['state'] in ('raster_ready', 'content_ready', 'editorially_approved') and
                        v.get('format') == 'picross-authoring-content-inspection-v1' and
                        v.get('original_state') == h['state'] and v.get('effective_state') == r['state'] and
                        v.get('integration_ready') is False and
                        all(v.get(k) == r[k] for k in ('width', 'height', 'mode', 'used_colors', 'difficulty')) and
                        all(b == 'final_editorial: missing bound human final approval' or b.startswith('background')
                            for b in v.get('blockers', [])))
            role = 'raster' if ready and complete else 'raster_draft'
            self.allow(role, {'file': bundle + '/' + name, 'sha256': expected}, variant if role == 'raster' else None)
        binding = r['background']
        if binding['manifest']:
            stored = binding['manifest']
            ref, root = stored['ref'], stored['root']
            name = ref['file'] if root == '.' else root + '/' + ref['file']
            if stored['storage'] == 'package':
                manifest = validate_manifest(self.json(name, ref['sha256']))
                ap.require(manifest['puzzle_id'] == r['puzzle_id'], 'Hintergrundmotiv stimmt nicht.')
                for candidate in manifest['candidates']:
                    ref = deepcopy(candidate['original'])
                    ref['file'] = ref['file'] if root == '.' else root + '/' + ref['file']
                    self.allow('background', ref, candidate['id'] if manifest['presentation']['status'] == 'offered' else None)
            else:
                # Finalizer may bind external, but still repository-published, background work.
                raw = self.source.read(self.commit, self.directory + '/' + name)
                bind(raw, ref)
                manifest = validate_manifest(parse(raw))
                ap.require(manifest['puzzle_id'] == r['puzzle_id'], 'Hintergrundmotiv stimmt nicht.')
                for candidate in manifest['candidates']:
                    inner = candidate['original']
                    path = ('' if root == '.' else root + '/') + inner['file']
                    original = self.source.read(self.commit, self.directory + '/' + path, 32 * JSON_LIMIT)
                    bind(original, inner)
                    self.allowed['background'][path] = inner['sha256']
                    if manifest['presentation']['status'] == 'offered':
                        self.offer_keys[('background', candidate['id'])] = path

    def matches(self, asset):
        loc, role = asset['location'], asset['role']
        actual_commit = loc['commit'] if loc['commit'] is not None else self.snapshot
        if actual_commit != self.commit:
            return False
        name = loc['file']
        if loc['storage'] == 'repository':
            prefix = self.directory + '/'
            if not name.startswith(prefix):
                return False
            name = name[len(prefix):]
        elif loc['container']['file'] != self.value['package']['file'] or loc['container']['sha256'] != self.value['package']['sha256']:
            return False
        return self.allowed[role].get(name) == loc['sha256']


def asset_bytes(source, snapshot, loc):
    commit = loc['commit'] if loc['commit'] is not None else snapshot
    if loc['storage'] == 'repository':
        return bind(source.read(commit, loc['file'], 32 * JSON_LIMIT), loc)
    raw = source.read(commit, loc['container']['file'], ap.MAX_ZIP)
    bind(raw, loc['container'])
    archive = Archive(raw)
    try:
        return bind(archive.read(loc['file'], 32 * JSON_LIMIT), loc)
    finally:
        archive.close()


def inspect(source, snapshot, value):
    """Validate every offered role against its original revision; no new approval."""
    p = validate(value)
    refs = [p['record'], *(o['record'] for o in p['offers'])]
    contexts, outer, asset_owners = {}, None, {}
    try:
        for ref in refs:
            key = (ref['commit'], ref['file'])
            if key in contexts:
                bind(contexts[key].raw, ref)
                continue
            # Offer records must also be index-published in their explicit snapshot.
            commit = ref['commit'] if ref['commit'] is not None else snapshot
            index = index_value(source.read(commit, INDEX, 8 * JSON_LIMIT))
            ap.require(any(e['record'] == ref['file'] for e in index['entries']), 'Angebotsrecord ist nicht indexiert.')
            ctx = Record(source, snapshot, ref, p['puzzle_id'])
            ctx.snapshot = snapshot
            if outer is None:
                outer = ctx
            contexts[key] = ctx
        for a in p['assets']:
            owners = [key for key, ctx in contexts.items() if ctx.matches(a)]
            ap.require(owners, 'Bildrolle oder Originalquelle stimmt nicht: ' + a['id'])
            image(asset_bytes(source, snapshot, a['location']))
            asset_owners[a['id']] = owners
        for offer in p['offers']:
            key = (offer['record']['commit'], offer['record']['file'])
            ctx = contexts[key]
            name = ctx.offer_keys.get((offer['kind'], offer['id']))
            # Raster IDs in the UI may be actor-assigned; identity is the bound single candidate revision.
            if offer['kind'] == 'raster':
                matches = [n for (role, _), n in ctx.offer_keys.items() if role == 'raster']
                name = matches[0] if len(matches) == 1 else None
            ap.require(name is not None, 'Fremdes oder unvollständiges Angebot: ' + offer['id'])
            for aid in offer['asset_ids']:
                a = next(a for a in p['assets'] if a['id'] == aid)
                loc = a['location']
                inner = loc['file'] if loc['storage'] == 'package' else loc['file'][len(ctx.directory) + 1:]
                ap.require(key in asset_owners[aid] and a['role'] == offer['kind'] and inner == name,
                           'Angebot verweist auf ein fremdes Bild oder einen Sichtungsentwurf.')
        # Require presentation of original images actually offered/selected by its outer record.
        for role in ROLES:
            for name, sha in outer.allowed[role].items():
                ap.require(any(a['role'] == role and a['location']['sha256'] == sha and
                               (p['record']['commit'], p['record']['file']) in asset_owners[a['id']] for a in p['assets']),
                           'Pflichtbild fehlt in der Projektion: ' + name)
        return {'state': outer.value['state'], 'blockers': outer.value['blockers'],
                'test_only': outer.handoff.get('test_only', False), 'verification': 'Überlieferter Produktionsbefund; keine neue Inhaltsprüfung.'}
    finally:
        for ctx in contexts.values():
            ctx.close()
