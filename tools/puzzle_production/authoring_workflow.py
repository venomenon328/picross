"""PW-B phase and human raster-selection bindings, without a second solver."""
from . import authoring_package as ap, catalog_io as io
from .contract import exact_keys, integer

REQUEST = 'picross-authoring-build-request-v3'
HANDOFF = 'picross-authoring-handoff-v4'
RECORD = 'picross-authoring-record-v3'
EARLY = ('brief_ready', 'reveal_review', 'motif_review', 'motif_approved', 'raster_review', 'raster_ready')
LATE = ('background_review', 'content_ready')
NEXT = {'brief_ready': '1 · Abschlussbilder erzeugen',
        'reveal_review': '2 · Abschlussbild wählen und Motivvorlage erstellen',
        'motif_review': '3 · Motivvorlage freigeben und Raster produzieren',
        'motif_approved': '3 · Raster produzieren',
        'raster_review': '3 · Raster korrigieren und qualifizieren',
        'raster_ready': '4 · Raster wählen und Kontextzeichnungen erzeugen',
        'background_review': '4 · Hintergrund wählen, korrigieren oder bewusst verzichten',
        'content_ready': '5 · Endabnahme und Integration beauftragen',
        'editorially_approved': '5 · Ins Spiel integrieren'}


def is_current(h):
    return h.get('format') == HANDOFF


def phase(h):
    ap.require(h.get('state') in EARLY + LATE, 'Unsupported 0.8.0 original phase')
    ap.require('background' in h and 'raster_selection' in h, 'Missing 0.8.0 phase bindings')
    if h['state'] in EARLY:
        ap.require(h['background'] is None and h['raster_selection'] is None,
                   'Background work requires an explicitly selected qualified raster')
        for gate in ('background_choice', 'background_asset'):
            ap.require(h['gates'].get(gate) == 'pending' and h['gate_evidence'].get(gate) is None,
                       'Early background gates must stay pending without evidence')
        ap.require(not any(b.startswith('background') for b in h.get('blockers', []) + h.get('content_blockers', [])),
                   'Background is not an early-phase blocker')
    else:
        ap.require(h['background'] is not None and h['raster_selection'] is not None,
                   'Background phase requires a recorded qualified raster selection')


def pending_background():
    return {'status': 'pending', 'ready': False, 'blockers': [], 'binding': None,
            'manifest': None, 'decision': None, 'derivation': None, 'options': [],
            'files': set(), 'derivative_files': set(), 'external_files': set(), 'decision_refs': set()}


def presentation(value):
    from tools.production_workspace.presentation import OPTION, text, reference
    exact_keys(value, {'title', 'raster_offers'})
    text(value['title'])
    ap.require(isinstance(value['raster_offers'], list) and len(value['raster_offers']) <= 20,
               'Too many raster offers')
    ids = set()
    for offer in value['raster_offers']:
        exact_keys(offer, {'id', 'label', 'record'})
        ap.require(isinstance(offer['id'], str) and OPTION.fullmatch(offer['id']) and offer['id'] not in ids,
                   'Invalid/duplicate raster offer ID')
        ids.add(offer['id'])
        text(offer['label'])
        reference(offer['record'], False)
    return value


def selection(root, h, *, history_repo=None, verify_git=False):
    """Check immutable original copies offline; publication additionally checks Git."""
    phase(h)
    if h['raster_selection'] is None:
        return set()
    from tools.production_workspace import presentation as p
    from tools.production_workspace.sources import GitSource, check_commit, production_path, git
    used = set()

    def read(ref):
        exact_keys(ref, {'file', 'sha256'})
        ap.relative(ref['file']); ap.sha(ref['sha256'])
        raw = io.read(root, ref['file'], 1024 * 1024)
        ap.require(io.checksum(raw) == ref['sha256'], 'Raster selection file changed')
        used.add(ref['file'])
        return raw

    s = p.parse(read(h['raster_selection']))
    exact_keys(s, {'format', 'puzzle_id', 'source_commit', 'option_id', 'record', 'projection',
                   'inventory_sha256', 'candidate', 'reveal', 'motif', 'human', 'test_only'})
    ap.require(s['format'] == 'picross-raster-selection-v1' and s['puzzle_id'] == h['puzzle_id'],
               'Raster selection identity differs')
    check_commit(s['source_commit'])
    ap.require(type(s['test_only']) is bool and s['test_only'] == h.get('test_only', False), 'Selection scope differs')
    ap.require(isinstance(s['option_id'], str) and p.OPTION.fullmatch(s['option_id']), 'Invalid selected offer')
    copies = {}
    for key in ('record', 'projection'):
        ref = s[key]
        exact_keys(ref, {'file', 'sha256', 'bytes', 'copy'})
        production_path(ref['file'])
        integer(ref['bytes'], 1, 1024 * 1024, 'selection source bytes')
        raw = read({'file': ref['copy'], 'sha256': ref['sha256']})
        ap.require(len(raw) == ref['bytes'], 'Selection source size differs')
        copies[key] = raw
    r, projection = p.parse(copies['record']), p.validate(p.parse(copies['projection']))
    ap.require(r['format'] == RECORD and r['puzzle_id'] == h['puzzle_id'] and r['state'] == 'raster_ready',
               'Only a qualified raster-ready revision can be selected')
    ap.require(s['record']['file'] == f"content/authoring/{r['puzzle_id']}/{r['revision']}/record.json" and
               r['inventory_sha256'] == ap.sha(s['inventory_sha256']), 'Selected revision/inventory differs')
    ap.require(projection['puzzle_id'] == h['puzzle_id'] and
               s['projection']['file'] == f"content/authoring/{projection['puzzle_id']}/{projection['revision']}/workspace.json",
               'Selection projection identity differs')
    matches = [o for o in projection['offers'] if o['id'] == s['option_id'] and o['kind'] == 'raster']
    ap.require(len(matches) == 1, 'Selected qualified offer is missing')
    offer = matches[0]
    ap.require(all(offer['record'][k] == s['record'][k] for k in ('file', 'sha256', 'bytes')) and
               offer['record']['commit'] in (None, s['source_commit']), 'Selected offer has another source')
    v = r['verification']
    ap.require(v.get('technical') is True and v.get('effective_state') == 'raster_ready' and
               v.get('format') == 'picross-authoring-content-inspection-v2', 'Selected record lacks raster qualification')
    exact_keys(s['candidate'], {'variant', 'matrix_hash', 'logic_hash'})
    ap.require(s['candidate'] == {k: h['candidate'][k] for k in s['candidate']}, 'Selected raster changed')
    for kind in ('reveal', 'motif'):
        exact_keys(s[kind], {'file', 'sha256'})
        ap.require(s[kind] == {k: h[kind][k] for k in s[kind]} == {k: r[kind][k] for k in s[kind]},
                   'Selected image context changed')
    human = exact_keys(s['human'], {'actor', 'timestamp_utc', 'statement', 'evidence'})
    ap.string(human['actor'], 'selection actor'); ap.string(human['statement'], 'selection statement')
    ap.timestamp(human['timestamp_utc'])
    read(human['evidence'])
    if verify_git:
        ap.require(history_repo is not None, 'Raster selection requires explicit history_repo')
        source = GitSource(history_repo)
        head = git(source.root, 'rev-parse', 'HEAD').decode().strip()
        ap.require(git(source.root, 'merge-base', head, s['source_commit']).decode().strip() == s['source_commit'],
                   'Selection source is stale; source is not in current history')
        for key, raw in copies.items():
            ap.require(source.read(s['source_commit'], s[key]['file']) == raw, 'Selection original differs from Git')
            ap.require(source.read(head, s[key]['file']) == raw, 'Selection source is stale; offered original changed')
        p.inspect(source, s['source_commit'], projection)
        ctx = p.Record(source, s['source_commit'], offer['record'], h['puzzle_id'])
        try:
            ap.require(s['candidate'] == {k: ctx.handoff['candidate'][k] for k in s['candidate']},
                       'Selected candidate is not the offered original')
        finally:
            ctx.close()
    # The candidate copy in the qualified record is bound by the producer too.
    ap.require({k: r['candidate'][k] for k in s['candidate']} == s['candidate'], 'Selected candidate differs from source record')
    return used
