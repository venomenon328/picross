"""CI-C selection and exact active native coverage, shared by scheduler and gate."""
from pathlib import Path
import json

GROUPS = ('core', 'history', 'catalog', 'completion', 'adapters', 'graphics', 'export')
SCOPES = dict(core=('core',), history=('integration',), catalog=('catalog',),
              completion=('completion',), adapters=('pilots',),
              graphics=('visual', 'perf_b'), export=('export',))
CATALOG_MODES = ('regular', 'restart', 'large', 'empty', 'invalid', 'adapter', 'information', 'kb', 'kk', 'ke')
# Exact paths only. Shared main/session/save/fixtures and unknown effects select all.
PATHS = {
    **{f'game/ui/{name}.gd': ('core', 'catalog', 'export') for name in
       ('catalog_ink', 'catalog_tip', 'catalog_difficulty')},
    **{f'game/ui/{name}.gd': ('core', 'catalog', 'completion', 'export') for name in
       ('catalog', 'catalog_card')},
    'game/ui/completion.gd': ('core', 'completion', 'graphics', 'export'),
    'tools/kat2_product.py': ('catalog',),
    'tools/test_kat2_product.py': ('catalog',),
    'tools/native_images.py': ('catalog',),
    'tools/ea_product.py': ('completion',),
    'tools/p14_integration.py': ('history',),
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
    common = ['current-resource-hashes', 'verified-toolchain-assets', 'version', 'import']
    cases = {
        'core': ['tests', 'current-drawing-tests', 'expected-failure', 'roundtrip-write', 'roundtrip-read', 'controlled-start'],
        'history': [f'integration-{n+1:03d}-{n+100:03d}' for n in range(0, 500, 100)]+['integration-restart'],
        'catalog': [name for mode in CATALOG_MODES for name in ('kat2-'+mode+'-import', 'kat2-'+mode)]
                   + ['kat2-adapter-export', 'kat2-adapter-register', 'kat2-image-processing'],
        'completion': ['ea-import', 'ea-native', 'ea-restart'],
        'adapters': [f'rp6-t{n:02d}-{s}' for n in (4,6,8,9) for s in ('partial','finish','read','render')]
                    + ['rp6-t04-foreign-slot-write', 'rp6-t04-foreign-slot-control', 'za1-test-only-registration',
                       'za1-import', 'za1-save-recovery', 'za1-seed-old-slots', 'za1-windows-export', 'za1-pck-resources']
                    + [f'za1-pz-test-direct-{c}-{s}' for c in ('mono','color') for s in
                       (('partial','finish','read','reset') if c == 'mono' else ('partial','finish','read','oldreset','reset'))],
        'graphics': ['current-vs2-complete', 'perf-b-native', 'retained-hc92-font-samples'],
        'export': ['player-content-import', 'windows-export', 'player-content-pck'],
    }
    if host == 'Windows':
        cases['adapters'] += ['za1-windows-exported-start']
        cases['export'] += ['windows-exported-start', 'windows-exported-gui-start']
    return sorted(common+cases[group])


WORKER_CHECKS = sorted(['vs2-roundtrip-write', 'vs2-roundtrip-read', 'vs2-gf1-tests',
    'hf149-write', 'hf149-read', 'hf149-native', 'vs2-regular-matrix', 'vs2-v1-focused',
    'vs2-v2-write', 'vs2-v2-read', 'vs2-v3-current', 'hc92-native-font-pixels',
    'hs186-native-number-cross-pixels', 'hn192-native-input-cursor', 'current-book-capture',
    'current-drawing-capture', 'current-drawing-pixel-oracles']+
    ['render-'+s for s in ('layout','cells-f1','cells-f2','axis','h1')])


def coverage(groups):
    return {g: dict(checks=checks(g), worker_checks=WORKER_CHECKS if g == 'graphics' else []) for g in groups}


def artifacts(group):
    value = json.loads(Path(__file__).with_name('native_artifacts.json').read_text(encoding='utf-8'))
    return value['groups'][group]
