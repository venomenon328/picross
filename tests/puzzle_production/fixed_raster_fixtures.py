"""Independent tiny synthetic sources; all decisions are explicitly TEST ONLY."""
from copy import deepcopy
from pathlib import Path
from PIL import Image
from tools.puzzle_production import fixed_raster as fixed, images, raster_parameters as parameters
from tools.puzzle_production.contract import digest, load_json, write_json
from tools.puzzle_production.za1_fixtures import ROOT


def prepare(root, mode='mono', *, stalled=False, paired=False):
    root.mkdir(parents=True, exist_ok=True)
    d = deepcopy(load_json(ROOT / 'tests/puzzle_production/fixtures/image-design.json'))
    d.update(width=4, height=4, mode=mode, crop=[0, 0, 4, 4], fit='exact',
             variants=[{'id': 'area', 'method': 'area', 'threshold': 128}], background='#ffffff',
             palette=[{'id': 'ink', 'rgb': '#202020'}] if mode == 'mono' else
                     [{'id': 'red', 'rgb': '#cc3333'}, {'id': 'blue', 'rgb': '#2678bd'}])
    ids = [p['id'] for p in d['palette']]
    matrix = [['empty' if x == 0 or y == 0 else ids[(x - 1) % len(ids)] for x in range(4)] for y in range(4)]
    if stalled:
        matrix = [['empty'] * 4 for _ in range(4)]
        matrix[1][1] = matrix[2][2] = ids[0]
        if mode == 'color': matrix[3][3] = ids[1]
    images.raster_image(matrix, d).save(root / 'motif.png')
    write_json(root / 'design.json', d)
    config = {'profile': 'paired-lines-' + mode, 'max_pair_work': 20000000, 'max_pair_records': 250000} if paired else None
    images.import_image(root / 'motif.png', root / 'design.json', root / 'import', profile=config['profile'] if config else None)
    c = load_json(root / 'import/area-candidate.json')
    entry = parameters.import_entry(c['design'], c['matrix'], 'area')
    corridor = {'format': parameters.FORMAT,
        'constraints': {k: {'kind': 'approximate', 'target': entry[k], 'minimum': None, 'maximum': None}
                        for k in ('width', 'height', 'foreground_colors')},
        'imports': [entry], 'derivation': {'cell_edits': True, 'empty_edge_crop': ['left', 'top'], 'protected_features': ['TEST ONLY retained lower right cell']}}
    (root / 'decision.txt').write_text('TEST ONLY synthetic approval, no human product decision.\n', encoding='utf-8')
    approval = {'type': 'human_motif_approval', 'actor': 'TEST ONLY', 'statement': 'Synthetic fixture only',
                'timestamp_utc': '2026-11-12T12:00:00Z', 'revision': 'r01', 'file': 'motif.png',
                'sha256': images.file_hash(root / 'motif.png'), 'derived_from_reveal_sha256': '0' * 64,
                'parameters': corridor, 'evidence': 'decision.txt'}
    write_json(root / 'approval.json', approval)
    mask = [[False] * 4 for _ in range(4)]; mask[3][3] = True
    edits = ([{'x': 2, 'y': 1, 'before': 'empty', 'after': ids[0]}] if stalled else
             [{'x': 1, 'y': 1, 'before': ids[0], 'after': 'empty'}])
    p = {'format': fixed.PLAN, 'puzzle_id': 'pz-fixed-synthetic', 'revision': 'r01',
         'reference': {'bundle': 'import', 'variant': 'area', 'manifest_sha256': images.file_hash(root / 'import/manifest.json'),
                       'matrix_hash': digest(c['matrix']), 'logic_hash': c['logic_hash']},
         'motif': {'file': 'motif.png', 'sha256': approval['sha256'],
                   'approval': {'file': 'approval.json', 'sha256': images.file_hash(root / 'approval.json')}},
         'parameters': corridor, 'import_hash': digest(entry), 'protected_mask': mask, 'edits': edits,
         'crop': [1, 1, 4, 4], 'budgets': {'max_changes': 4, 'solve_seconds': 30, 'solve_lines': 100000,
                                        'verify_seconds': 30, 'verify_lines': 100000},
         'certification': config, 'rationale': 'TEST ONLY remove empty exterior and repair one tiny synthetic corner'}
    return p, c


def approve_plan(root, p):
    a = load_json(root / p['motif']['approval']['file']); a['parameters'] = p['parameters']
    write_json(root / p['motif']['approval']['file'], a)
    p['motif']['approval']['sha256'] = images.file_hash(root / p['motif']['approval']['file'])
    write_json(root / 'plan.json', p)
    return root / 'plan.json'
