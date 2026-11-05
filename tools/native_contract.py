"""CI-C selection and exact active native coverage, shared by scheduler and gate."""
from pathlib import Path
import json

GROUPS = ('core', 'history', 'catalog', 'completion', 'adapters', 'graphics', 'export')
SCOPES = dict(core=('core',), history=('integration',), catalog=('catalog',),
              completion=('completion',), adapters=('pilots',),
              graphics=('visual', 'perf_b'), export=('export',))
CATALOG_MODES = ('regular', 'restart', 'pages', 'empty', 'invalid', 'adapter', 'information', 'kb', 'kk', 'ke', 'at')
# P2-F-A: representative real RP6 saves, not a presentation cross product.
RP6_CAPTURES = {4: (2, 1920, 1080, 1.0), 6: (3, 1280, 720, 1.25)}
RP6_STATES = ('work', 'detail', 'album-partial', 'completion', 'album-completed')
# P2-E-A-V02 / D02: selected native cases, deliberately not the old cross product.
CATALOG_CASES = {
    'ke': ('ke-layout-1280-ui125', 'ke-metadata-null', 'ke-metadata-current',
           'ke-negative-delayed-hover', 'ke-metadata-legacy',
           'ke-roundtrip-and-mode-tooltip', 'ke-pointer-card', 'ke-pointer-difficulty_icon',
           'ke-layout-1920-ui100', 'ke-resize-boundary', 'ke-own-fill-undo-x-spoiler'),
    'kk': ('kk-basic-1280-ui125', 'kk-empty-save', 'kk-pointer-edit-undo-spoiler',
           'kk-solved-save-reveal-pixels', 'kk-wide-tall-artwork',
           'kk-long-name-reset-tooltip-roundtrip', 'kk-reset-target-foreign-slots',
           'kk-basic-1920-ui100', 'kk-basic-2560-ui125', 'kk-recovery-pointer',
           'kk-aspect-endpoints', 'kk-empty-write-error'),
}
# Exact paths only. Shared main/session/save/fixtures and unknown effects select all.
PATHS = {
    **{f'game/art/cells/{kind}-{size}.png{suffix}': ('core', 'graphics', 'export')
       for kind in ('fill','x') for size in ('small','medium','large') for suffix in ('','.import')},
    # RP6/ZA-1 captures render cards; compact graphics also renders the album.
    **{f'game/ui/{name}.gd': ('core', 'catalog', 'adapters', 'graphics', 'export') for name in
       ('catalog_ink', 'catalog_tip')},
    **{f'game/ui/{name}.gd': ('core', 'catalog', 'completion', 'adapters', 'graphics', 'export') for name in
       ('catalog', 'catalog_card')},
    # Besides card display, Difficulty.valid gates the shared runtime registry.
    'game/model/catalog_difficulty.gd': GROUPS,
    # The regular book root shares session, save, input and export boundaries.
    **{f'game/book/{name}': GROUPS for name in (
        'main.gd', 'content.gd', 'binding.gd', 'catalog.gd', 'information.gd',
        'information_routes.gd', 'surface.gd', 'page.gdshader', 'material.gdshader',
        'fold.gdshaderinc', 'paper.png', 'paper.png.import', 'paper.json',
        'leather.png', 'leather.png.import', 'leather.json',
        'table.png', 'table.png.import', 'table.json')},
    **{f'game/ui/{name}.gd': GROUPS for name in ('help_panel', 'help_example', 'help_examples')},
    'game/tests/help_cases.gd': ('core',),
    # Diagnostic-source changes still select ordinary regression/build groups;
    # these mappings do not schedule the opt-in book lifecycle itself (D03).
    'game/tests/help_native.gd': GROUPS,
    'game/tests/book_fixture.gd': GROUPS,
    'game/tests/book_integration.gd': GROUPS,
    'game/tests/book-save-v1.json': GROUPS,
    'tools/book_contract.py': GROUPS,
    'tools/book_lifecycle.py': GROUPS,
    'game/tests/book_windows_observer.gd': GROUPS,
    # KAT-2 and RP6/ZA-1 exercise the real completion view too.
    'game/ui/completion.gd': ('core', 'catalog', 'completion', 'adapters', 'graphics', 'export'),
    'tools/kat2_product.py': ('catalog',),
    'tools/test_kat2_product.py': ('catalog',),
    'tools/ea_product.py': ('completion',),
    'tools/p14_integration.py': ('history',),
    'tools/native_metrics.py': GROUPS,
    'tools/hn_evidence.py': ('graphics',),
    'game/tests/p14_integration.gd': ('history',),
    'tools/za1_product.py': ('adapters', 'export'),
    'game/tests/kat2_probe.gd': ('catalog',),
    'game/tests/ea_probe.gd': ('completion',),
    'game/tests/rp6_probe.gd': ('adapters',),
    'game/tests/rp6_capture.gd': ('adapters',),
    'game/tests/za1_probe.gd': ('adapters',),
    'game/tests/za1_save_cases.gd': ('adapters',),
    'game/tests/content_pack_probe.gd': ('adapters', 'export'),
    **{p: ('core', 'graphics', 'export') for p in (
        'tools/perf_b_resources.py', 'tools/test_perf_b_resources.py', 'tools/cell_atlas_reference.json',
        'tools/p1_current_visual.py', 'game/tests/perf_b_probe.gd', 'game/tests/perf_b_cases.gd',
        'game/ui/cell_atlas.gd', 'game/ui/atlas_marks.gd', 'game/ui/atlas_mask.gdshader',
        'game/ui/pencil_marks.gd', 'game/tests/capture.gd', 'game/tests/zs2_capture.gd')},
}


def select_groups(reasons):
    selected = set()
    for reason in reasons:
        if reason.startswith('explicit scope: native-'):
            name = reason.removeprefix('explicit scope: native-')
            if name not in GROUPS:
                raise ValueError('Unknown native scope')
            selected.add(name)
        elif reason.startswith('explicit scope: '):
            scope = reason.removeprefix('explicit scope: ')
            selected.update({'runtime': ('core', 'history', 'catalog', 'completion', 'export'),
                             'visual': ('core', 'graphics', 'export'),
                             'perf-b': ('core', 'graphics', 'export'),
                             'production': GROUPS}.get(scope, GROUPS))
        else:
            path = reason.replace('prototypes/p1/', 'game/', 1)
            selected.update(PATHS.get(path, GROUPS))
    return [g for g in GROUPS if g in selected]


def checks(group, host='Linux'):
    common = ['current-resource-hashes', 'verified-toolchain-assets', 'current-atlas-resources', 'version', 'import']
    cases = {
        'core': ['tests', 'current-drawing-tests', 'expected-failure', 'roundtrip-write', 'roundtrip-read', 'controlled-start'],
        'history': ['integration-writer', 'integration-reader'],
        'catalog': ['kat2-'+mode for mode in CATALOG_MODES]+['kat2-pages-import','kat2-adapter-import','kat2-at-import','kat2-imported-base-copies']
                   + ['kat2-adapter-export', 'kat2-adapter-register'],
        'completion': ['ea-import', 'ea-native', 'ea-restart'],
        'adapters': [f'rp6-t{n:02d}-{s}' for n in (4,6,8,9) for s in ('partial','finish','read')]
                    + [f'rp6-t{n:02d}-render' for n in RP6_CAPTURES]
                    + ['rp6-t04-foreign-slot-write', 'rp6-t04-foreign-slot-control', 'za1-test-only-registration',
                       'za1-import', 'za1-save-recovery', 'za1-seed-old-slots', 'za1-windows-export', 'za1-pck-resources']
                    + [f'za1-pz-test-direct-{c}-{s}' for c in ('mono','color') for s in
                       (('partial','finish','read','reset') if c == 'mono' else ('partial','finish','read','oldreset','reset'))],
        'graphics': ['current-vs2-complete', 'perf-b-native'],
        'export': ['player-content-import', 'windows-export', 'player-content-pck'],
    }
    if host == 'Windows':
        cases['adapters'] += ['za1-windows-exported-start']
        cases['export'] += ['windows-exported-start', 'windows-exported-gui-start']
    return sorted(common+cases[group])


WORKER_CHECKS = sorted(['vs2-roundtrip-write', 'vs2-roundtrip-read', 'vs2-gf1-tests',
    'hf149-write', 'hf149-read', 'hf149-native', 'vs2-regular-matrix',
    'vs2-v2-write', 'vs2-v2-read',
    'hs186-native-number-cross-pixels', 'hn192-native-input-cursor',
    'current-drawing-capture', 'current-drawing-pixel-oracles']+
    ['render-'+s for s in ('layout','cells-f1','cells-f2','axis','h1')])


def coverage(groups):
    return {g: dict(checks=checks(g), worker_checks=WORKER_CHECKS if g == 'graphics' else []) for g in groups}


def artifacts(group):
    value = json.loads(Path(__file__).with_name('native_artifacts.json').read_text(encoding='utf-8'))
    return value['groups'][group]
