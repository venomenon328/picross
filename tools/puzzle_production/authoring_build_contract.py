"""PB-A input and phase bindings. Early phases deliberately do not certify logic."""
from pathlib import PurePosixPath
import re

from . import authoring_package as ap, catalog_io as io
from .contract import canonical_bytes, exact_keys, integer, load_json

FORMAT = 'picross-authoring-build-request-v1'
STATES = ('brief_ready', 'reveal_review', 'motif_review', 'raster_review', 'content_ready')
EXTERNAL = {'approval.json', 'manual-authorization.json', 'owner-override.json', 'palette-exception.json'}
HANDOFF_KEYS = set('format puzzle_id revision repo_commit state rulebook inventory brief report decisions effort '
                   'approved_parameters proposed_parameters reveal motif candidate repair difficulty gates gate_evidence '
                   'origin_verification palette_review palette_assessment playtest blockers content_blockers '
                   'next_action authorization test_only final_editorial_approval manual_edit_record '
                   'editorial_manual_derivation editorial'.split())
# Closed introduced production formats, not a prefix/version wildcard. Adding a
# new producer requires an explicit consumer decision, especially PB-H.
FORMATS = set('PNG JPEG picross-authoring-handoff-v2 picross-authoring-file-inventory-v1 '
              'picross-image-design-v1 picross-image-candidate-v1 '
              'picross-image-manifest-v1 picross-image-manifest-v2 '
              'picross-logic-v1 picross-logic-v2 picross-proof-v1 picross-proof-v2 picross-proof-v3 '
              'picross-result-v1 picross-deduction-assessment-v1 picross-quality-report-v1 '
              'picross-repair-plan-v1 picross-repair-plan-v2 picross-repair-v1 picross-repair-v2 '
              'picross-repair-manifest-v1 picross-repair-manifest-v2 '
              'picross-manual-edit-plan-v1 picross-manual-edit-plan-v2 '
              'picross-manual-candidate-v1 picross-manual-candidate-v2 picross-fixed-mono-import-plan-v2 '
              'picross-editorial-fixed-cell-plan-v1 picross-editorial-fixed-cell-plan-v2 '
              'picross-editorial-raster-redraw-plan-v1 picross-editorial-raster-redraw-plan-v2 '
              'picross-editorial-fixed-cell-derivation-v1 picross-editorial-fixed-cell-derivation-v2 '
              'picross-editorial-raster-redraw-v1 picross-editorial-raster-redraw-v2 '
              'picross-palette-assessment-v1 picross-palette-visual-review-v1 '
              'picross-analysis-input-v1 picross-analysis-trace-v1 picross-analysis-report-v1 '
              'picross-difficulty-rating-v1 picross-difficulty-context-v1 picross-difficulty-context-v2 '
              'picross-sd2-input-v1 picross-sd2-trace-v1 picross-sd2-report-v1 '
              'picross-sd2-evidence-v1 picross-sd2-method-v1 picross-sd2-rating-v1 '
              'picross-sd2-rating-bundle-v1 picross-checked-difficulty-v1 '
              'picross-checked-difficulty-v2 picross-checked-difficulty-v3 '
              'picross-uniqueness-v1 picross-uniqueness-check-v1 picross-solution-witness-v1 '
              'picross-editorial-approval-v1 picross-palette-editorial-exception-v1'.split())
FORMATS.update(f'picross-{kind}-v{v}' for kind in ('manual-authorization', 'owner-override') for v in range(1, 7))


def names(paths):
    """Validate complete file/directory namespace including parent case aliases."""
    files, spelling = set(), {}
    for name in paths:
        ap.relative(name)
        key = name.casefold()
        ap.require(key not in files, 'Duplicate/colliding file path: ' + name)
        files.add(key)
        parts = name.split('/')
        for n in range(1, len(parts) + 1):
            prefix = '/'.join(parts[:n])
            ap.require(spelling.setdefault(prefix.casefold(), prefix) == prefix,
                       'Windows parent alias: ' + prefix)
    ap.require(len(files) <= ap.MAX_FILES and len(spelling) <= ap.MAX_FILES * 2, 'Too many package paths')
    for name in paths:
        ap.require(all('/'.join(name.casefold().split('/')[:n]) not in files
                       for n in range(1, len(name.split('/')))), 'File/directory collision')


def source_record(value, *, member=False):
    exact_keys(value, {'source', 'sha256', 'bytes'} | ({'path'} if member else set()))
    ap.relative(value['source'])
    ap.sha(value['sha256'])
    integer(value['bytes'], 0, ap.MAX_FILE, 'source bytes')
    if member:
        ap.relative(value['path'])
        ap.require(PurePosixPath(value['path']).name not in
                   ('handoff.json', 'inventory.json', 'derivation.json', 'package.zip'),
                   'Cannot reseal or embed a sealed authoring package')
        ap.require(not value['path'].lower().endswith('.zip'), 'Embedded archives are unsupported')


def validate_request(value):
    # Roundtrip also isolates caller mutations and applies strict JSON limits to API calls.
    r = io.json_bytes(canonical_bytes(value), 8 * 1024 * 1024)
    exact_keys(r, {'format', 'handoff', 'document_revision', 'files', 'target',
                   'category_id', 'reveal_options', 'external'})
    ap.require(r['format'] == FORMAT, 'Unsupported build request')
    integer(r['document_revision'], 1, 1_000_000, 'rulebook document revision')
    ap.require(r['target'] in ('local', 'repository'), 'Invalid publication target')
    if r['category_id'] is not None:
        ap.require(isinstance(r['category_id'], str) and re.fullmatch(r'[a-z][a-z0-9-]{0,63}', r['category_id']),
                   'Invalid category ID')
    h = r['handoff']
    ap.require(isinstance(h, dict) and set(h) <= HANDOFF_KEYS, 'Unknown handoff fields; use editorial for prose')
    ap.require(h.get('format') == 'picross-authoring-handoff-v2' and h.get('inventory') is None,
               'Only unsealed Authoring v2 drafts can be built')
    ap.require(isinstance(h.get('puzzle_id'), str) and ap.ID.fullmatch(h['puzzle_id']), 'Invalid puzzle ID')
    ap.require(isinstance(h.get('revision'), str) and ap.REVISION.fullmatch(h['revision']), 'Invalid revision')
    names([h['puzzle_id'] + '/' + h['revision'] + '/record.json'])
    ap.require(h.get('state') in STATES, 'Unsupported build phase')
    ap.require(isinstance(h.get('repo_commit'), str) and re.fullmatch(r'[0-9a-f]{40}', h['repo_commit']),
               'Missing actual source commit')
    exact_keys(h.get('rulebook'), {'version', 'file', 'sha256'})
    ap.require(h['rulebook']['version'] == '0.6.0', 'New production requires Authoring 0.6.0; old packages stay sealed')
    ap.relative(h['rulebook']['file'])
    ap.sha(h['rulebook']['sha256'])
    for key in ('brief', 'next_action', 'authorization'):
        ap.string(h.get(key), key)
    ap.require(type(h.get('test_only', False)) is bool, 'Invalid test_only')
    ap.require(isinstance(h.get('gates'), dict), 'Missing phase gates')
    ap.require(set(h['gates']) <= set('reveal_approval motif provenance logic frame visual difficulty '
                                    'reveal_consistency final_editorial target_export'.split()), 'Unknown gate')
    ap.require(all(v in ('pending', 'pass', 'fail', 'blocked') for v in h['gates'].values()), 'Invalid gate status')
    ap.require(h['gates'].get('final_editorial') != 'pass' and h['gates'].get('target_export') != 'pass' and
               h.get('final_editorial_approval') is None, 'Later final approval/export belongs outside the original handoff')
    for key in ('blockers', 'content_blockers'):
        ap.require(isinstance(h.get(key, []), list), 'Invalid blockers')
        for item in h.get(key, []):
            ap.string(item, key)
    ap.require(isinstance(h.get('approved_parameters', []), list), 'Invalid parameter corridor')
    ap.require(isinstance(r['files'], list) and r['files'], 'Explicit file list required')
    for item in r['files']:
        source_record(item, member=True)
    names([item['path'] for item in r['files']] + ['handoff.json', 'inventory.json'])
    ap.require(sum(item['bytes'] for item in r['files']) <= ap.MAX_TOTAL, 'Package byte limit')
    ap.require(isinstance(r['external'], dict) and set(r['external']) <= EXTERNAL, 'Unknown external evidence')
    for item in r['external'].values():
        source_record(item)
    ap.require(('manual-authorization.json' in r['external']) == ('owner-override.json' in r['external']),
               'Manual authorization and owner evidence must be supplied together')
    ap.require('palette-exception.json' not in r['external'] or 'approval.json' in r['external'],
               'Palette exception requires a separate bound final approval')
    ap.require(isinstance(r['reveal_options'], list) and len(r['reveal_options']) <= 20, 'Invalid reveal options')
    ids = set()
    for option in r['reveal_options']:
        exact_keys(option, {'ID', 'Beschreibung', 'Datei', 'SHA-256'})
        ap.require(isinstance(option['ID'], str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', option['ID']) and
                   option['ID'] not in ids, 'Duplicate/invalid reveal option ID')
        ids.add(option['ID'])
        ap.string(option['Beschreibung'], 'option description')
        ap.relative(option['Datei'])
        ap.sha(option['SHA-256'])
    if h['state'] in ('motif_review', 'raster_review', 'content_ready'):
        ap.require(not r['reveal_options'], 'Selected reveal must not retain candidate gallery')
    if h['state'] == 'content_ready':
        ap.require(not h.get('content_blockers') and all(b == 'final_editorial: missing bound human final approval'
                   for b in h.get('blockers', [])), 'content_ready cannot contain unresolved content blockers')
    return r


class PhaseFiles:
    """Reuse file/approval/provenance contracts without changing ZA-1 admission."""
    file = ap.Package.file
    json = ap.Package.json
    bound = ap.Package.bound
    approval = ap.Package.approval
    provenance = ap.Package.provenance

    def __init__(self, root, handoff, deadline):
        self.root, self.handoff, self.deadline = root, handoff, deadline
        self.files, self.used = ap.file_table(root, deadline), set()


def references(p):
    """Close existing file references, including every RP manifest member.

    Hashes named matrix_hash/logic_hash are deliberately NOT file hashes.
    Local bundle references resolve relative to the declaring JSON; authoring
    references may use package-root paths. Ambiguity fails, never guesses.
    """
    def resolve(name, parent):
        ap.relative(name)
        candidates = {name, (parent / name).as_posix()}
        matches = candidates & p.files.keys()
        ap.require(len(matches) == 1, 'Missing/ambiguous declared file: ' + name)
        return p.file(matches.pop())

    def walk(value, parent):
        io.tick()
        if isinstance(value, list):
            for child in value:
                walk(child, parent)
        elif isinstance(value, dict):
            if 'format' in value:
                ap.require(isinstance(value['format'], str) and value['format'] in FORMATS,
                           'Unsupported declared technical format: ' + str(value['format']))
            # Historical references are deliberately external and must name an
            # exact Git location and decision. They cannot replace live inputs.
            if set(value) == {'commit', 'path', 'sha256', 'decision'}:
                ap.require(isinstance(value['commit'], str) and re.fullmatch(r'[0-9a-f]{40}', value['commit']),
                           'Invalid historical commit')
                ap.relative(value['path'])
                ap.sha(value['sha256'])
                ap.string(value['decision'], 'historical decision')
                return
            if isinstance(value.get('file'), str):
                path = resolve(value['file'], parent)
                if 'sha256' in value:
                    ap.require(ap.file_hash(path) == ap.sha(value['sha256']), 'Declared file hash mismatch')
                if 'bytes' in value:
                    ap.require(type(value['bytes']) is int and path.stat().st_size == value['bytes'], 'Declared byte mismatch')
            if isinstance(value.get('files'), dict):
                for name, expected in value['files'].items():
                    # RP manifests use bundle-local names, not root fallbacks.
                    path = p.file((parent / ap.relative(name)).as_posix())
                    ap.require(ap.file_hash(path) == ap.sha(expected), 'Manifest file hash mismatch: ' + name)
            for key, child in value.items():
                if key in ('files',):
                    continue
                if isinstance(child, str) and key in ('evidence', 'prompt_file', 'proof', 'verification',
                                                       'baseline_proof', 'assessment_file'):
                    resolve(child, parent)
                walk(child, parent)

    for name in sorted(p.files):
        with p.file(name).open('rb') as stream:
            prefix = stream.read(128).lstrip()
        if name.endswith('.json') or prefix.startswith((b'{', b'[')):
            # All JSON is data, never imported or executed. Strict parser even
            # for unformatted editorial records; unknown schemas are not dropped.
            # RP reports contain full-precision elapsed floats; the catalog-only
            # 16-character numeric-token rule does not apply to these originals.
            value = load_json(p.file(name), ap.MAX_FILE)
            walk(value, PurePosixPath(name).parent)


def validate_phase(root, r, deadline):
    h = r['handoff']
    p = PhaseFiles(root, h, deadline)
    snapshot = p.bound(h['rulebook']).read_text(encoding='utf-8')
    ap.require(re.search(r'^\*\*Version 0\.6\.0 · Dokumentrevision ' + str(r['document_revision']) + r' ·', snapshot, re.M),
               'Rulebook version/document revision does not match snapshot')
    p.file(h['brief'])
    for key in ('report', 'decisions', 'effort', 'origin_verification', 'difficulty',
                'manual_edit_record', 'editorial_manual_derivation'):
        if h.get(key) is not None:
            if isinstance(h[key], dict):
                p.bound(h[key])
            else:
                p.file(h[key])
    for key in ('palette_review', 'palette_assessment'):
        if h.get(key) is not None:
            p.bound(h[key])
    evidence = h.get('gate_evidence', {})
    ap.require(isinstance(evidence, dict), 'Invalid gate evidence')
    for gate, status in h['gates'].items():
        if status == 'pass':
            p.file(evidence.get(gate))
    for name in evidence.values():
        if name is not None:
            p.file(name)
    selected = {}
    for kind in ('reveal', 'motif'):
        record = h.get(kind)
        if record is None:
            continue
        ap.require(isinstance(record, dict) and set(record) <=
                   {'file', 'sha256', 'approval', 'provenance', 'revision', 'derived_from_reveal_sha256'},
                   'Unknown image binding fields')
        if record.get('file') is None:
            ap.require(all(v is None for v in record.values()), 'Unbound image data')
            continue
        p.bound(record)
        p.provenance(record, kind)
        selected[kind] = record
        if record.get('approval') is not None:
            p.approval(record, kind)
    for option in r['reveal_options']:
        record = {'file': option['Datei'], 'sha256': option['SHA-256']}
        p.bound(record)
        p.provenance(record, 'reveal')
    state = h['state']
    if state == 'reveal_review':
        ap.require(bool(r['reveal_options']) or 'reveal' in selected, 'Reveal review requires offered originals')
    if state in ('motif_review', 'raster_review', 'content_ready'):
        ap.require('reveal' in selected and 'motif' in selected, 'Phase requires reveal and motif originals')
        p.approval(selected['reveal'], 'reveal')
        ap.require(selected['motif'].get('derived_from_reveal_sha256') == selected['reveal']['sha256'], 'Wrong motif derivation')
    if state in ('raster_review', 'content_ready'):
        p.approval(selected['motif'], 'motif')
        ap.require(bool(h.get('approved_parameters')), 'Raster work requires approved parameters')
    for kind, gate in (('reveal', 'reveal_approval'), ('motif', 'motif')):
        if h['gates'].get(gate) == 'pass':
            ap.require(kind in selected, 'Image gate lacks original')
            p.approval(selected[kind], kind)
    if h.get('candidate'):
        c = h['candidate']
        ap.require(isinstance(c, dict) and set(c) <= {'bundle', 'variant', 'proof', 'verification', 'certification',
                   'source_type', 'repair_id', 'parent_variant', 'matrix_hash', 'logic_hash'}, 'Unknown candidate fields')
        if c.get('bundle'):
            ap.relative(c['bundle'])
            p.file(c['bundle'] + '/manifest.json')
        for key in ('proof', 'verification'):
            if c.get(key):
                p.file(c[key])
    if h.get('repair'):
        repair = h['repair']
        ap.require(isinstance(repair, dict) and set(repair) <=
                   {'reference', 'reference_variant', 'plan', 'replay', 'type', 'record'}, 'Unknown repair fields')
        if repair.get('reference'):
            p.file(ap.relative(repair['reference']) + '/manifest.json')
        for key in ('plan', 'replay', 'record'):
            if repair.get(key):
                p.file(repair[key])
    references(p)
    return p
