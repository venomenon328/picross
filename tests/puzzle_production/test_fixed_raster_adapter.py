"""Small real Git/Builder checks, with synthetic decisions only."""
from copy import deepcopy
from pathlib import Path
import unittest

from tools.puzzle_production import fixed_raster as fixed, images, catalog_analysis, catalog_rating
from tools.puzzle_production.contract import canonical_bytes, digest, load_json, write_json
from tools.production_workspace import presentation, current_view
from tools.production_workspace.sources import GitSource
from tests.puzzle_production.test_authoring_workflow import WorkflowFixture
from tests.puzzle_production.fixed_raster_fixtures import prepare, approve_plan
from tests.puzzle_production.background_fixtures import put, put_json, file_ref


def fixed_workflow(case, mode):
    f = WorkflowFixture(case, mode)
    root, h = f.helper.source, f.request['handoff']
    p, c = prepare(root, mode)
    p['puzzle_id'] = h['puzzle_id']
    a = load_json(root / 'approval.json')
    a['derived_from_reveal_sha256'] = h['reveal']['sha256']
    write_json(root / 'motif-approval.json', a)
    (root / 'approval.json').unlink()
    p['motif']['approval']['file'] = 'motif-approval.json'
    value = fixed.derive(root, approve_plan(root, p), root / 'fixed')
    h['approved_parameters'] = [p['parameters']]
    h['motif'] = {'file': 'motif.png', 'sha256': a['sha256'], 'approval': 'motif-approval.json',
                  'derived_from_reveal_sha256': h['reveal']['sha256']}
    write_json(root / 'motif.provenance.json', {'puzzle_id': h['puzzle_id'], 'file': 'motif.png', 'sha256': a['sha256'],
        'author': 'TEST ONLY', 'usage_basis': 'Repository owned synthetic pixels',
        'derived_from': {k: h['reveal'][k] for k in ('file', 'sha256')}})
    h['candidate'] = {'bundle': 'fixed', 'variant': 'fixed', 'source_type': 'fixed', 'proof': 'fixed/proof.json',
                       'matrix_hash': value['matrix_hash'], 'logic_hash': value['logic_hash']}
    h['repair'] = {'type': 'fixed_edits_empty_crop', 'reference': 'import', 'reference_variant': 'area',
                   **{k: 'fixed/' + k + '.json' for k in ('plan', 'record', 'replay')}}
    difficulty = load_json(root / h['difficulty']); difficulty['logic_hash'] = value['logic_hash']
    write_json(root / h['difficulty'], difficulty)
    put(root, 'final-review.txt', ('TEST ONLY synthetic motif/reveal judgment, no actual human visual acceptance.\n' +
        value['matrix_hash'] + '\n' + value['logic_hash'] + '\n').encode())
    for gate in ('visual', 'reveal_consistency'): h['gate_evidence'][gate] = 'final-review.txt'
    definition = catalog_analysis.candidate(value['design'], value['matrix'], images.logic_from_matrix(value['matrix'], value['design']), h['puzzle_id'], 1)
    write_json(f.root / 'analysis-input.json', definition)
    checked = catalog_analysis.analyze_single(f.root / 'analysis-input.json', f.root / 'analysis-work',
                                               production_mode=mode, method='picross-difficulty-0.4')
    # The importer performs the independent full check of the actual A/B bundle.
    imported = catalog_rating.import_bundle(f.root / 'analysis-input.json', f.root / 'analysis-work')
    case.assertEqual(imported['logic_binding'], checked['logic_binding'])
    write_json(root / 'checked.json', checked)
    h['gate_evidence']['difficulty'] = 'checked.json'
    if mode == 'color':
        review = load_json(root / 'palette-review.json')
        review.update(matrix_hash=value['matrix_hash'], logic_hash=value['logic_hash'])
        # Same palette as the existing independent color fixture; actual end values are remeasured by ZA-1.
        ref = put_json(root, 'palette-review.json', review)
        h['palette_review'] = {k: ref[k] for k in ('file', 'sha256')}
    f.fixed_value, f.checked = value, checked
    return f


def rebind_phase(f):
    h, value = f.request['handoff'], f.fixed_value
    definition = catalog_analysis.candidate(value['design'], value['matrix'], images.logic_from_matrix(value['matrix'], value['design']), h['puzzle_id'], 2)
    checked = catalog_rating.rebind_checked(f.checked, canonical_bytes(definition) + b'\n', production_mode=value['design']['mode'])
    write_json(f.helper.source / 'checked.json', checked)
    return checked


class FixedRasterAdapterTests(unittest.TestCase):
    def test_real_builder_mono_color_qualified_offer_pointer_and_missing_evidence(self):
        for mode in ('mono', 'color'):
            with self.subTest(mode=mode):
                f = fixed_workflow(self, mode)
                result = f.build()
                self.assertEqual(result['record']['state'], 'raster_ready')
                self.assertIsNone(result['record']['background'])
                self.assertIsNone(result['record']['raster_selection'])
                self.assertIsNone(result['record']['final_editorial_approval'])
                commit = f.commit()
                view = load_json(f.helper.directory / 'workspace.json')
                self.assertEqual([o['kind'] for o in view['offers']], ['raster'])
                self.assertEqual(presentation.inspect(GitSource(f.helper.output), commit, view)['state'], 'raster_ready')
                current_view.inspect(GitSource(f.helper.output), commit,
                    (f.helper.output / current_view.path('pz-hp-synthetic')).read_bytes(), 'pz-hp-synthetic', originals=True)
                # A genuinely missing content proof cannot become another qualified record.
                f.request['handoff']['revision'] = 'r02'
                f.request['handoff']['gate_evidence']['difficulty'] = None
                with self.assertRaises(ValueError): f.build()

    def test_stale_analysis_and_visual_binding_are_rejected(self):
        f = fixed_workflow(self, 'mono')
        root = f.helper.source
        changed = deepcopy(f.checked)
        changed['logic_binding']['matrix_hash'] = 'f' * 64
        changed['checked_hash'] = digest({k: v for k, v in changed.items() if k != 'checked_hash'})
        write_json(root / 'checked.json', changed)
        with self.assertRaisesRegex(ValueError, 'Stale|binding'): f.build()
        write_json(root / 'checked.json', f.checked)
        put(root, 'final-review.txt', b'TEST ONLY stale content review.\n')
        with self.assertRaisesRegex(ValueError, 'Stale final content'): f.build()
