from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from tools.puzzle_production import fixed_raster as f, raster_parameters as rp, images
from tools.puzzle_production.contract import Aborted, Budget, digest, load_json, write_json
from tests.puzzle_production.fixed_raster_fixtures import prepare, approve_plan


class FixedRasterTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='fixed-test-'); self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def test_mono_color_edits_crop_combined_and_stalled(self):
        for mode in ('mono', 'color'):
            for change in ('edit', 'crop', 'both', 'stalled'):
                with self.subTest(mode=mode, change=change):
                    root = self.root / (mode + change)
                    p, c = prepare(root, mode, stalled=change == 'stalled')
                    if change == 'edit': p['crop'] = [0, 0, 4, 4]
                    if change == 'crop': p['edits'] = []
                    value = f.derive(root, approve_plan(root, p), root / 'fixed')
                    checked = f.inspect(root, root / 'fixed')[2]
                    self.assertTrue(checked['certified'])
                    self.assertEqual(value['base_status'], 'stalled' if change == 'stalled' else 'solved')
                    self.assertEqual(value['import_design'], c['design'])

    def test_constraints_import_identity_and_exact_axis(self):
        p, c = prepare(self.root)
        for kind in ('open', 'approximate', 'exact'):
            q = deepcopy(p['parameters'])
            q['derivation']['empty_edge_crop'] = []
            for axis in ('width', 'height'):
                q['constraints'][axis].update(kind=kind, target=None if kind == 'open' else 4)
            rp.validate(q)
            plan = deepcopy(p); plan['parameters'] = q; plan['crop'] = [0, 0, 4, 4]
            self.assertEqual(f.transform(plan, c['design'], c['matrix'])[0]['width'], 4)
            if kind != 'exact':
                q['derivation']['empty_edge_crop'] = ['left', 'top']
                plan['crop'] = [1, 1, 4, 4]
                self.assertEqual(f.transform(plan, c['design'], c['matrix'])[0]['width'], 3)
        q = deepcopy(p['parameters']); q['constraints']['width']['kind'] = 'exact'
        with self.assertRaisesRegex(ValueError, 'Exact'): rp.validate(q)
        p['parameters']['imports'].append({**p['parameters']['imports'][0], 'width': 5})
        approve_plan(self.root, p); f.reference(self.root, p)
        wrong = deepcopy(p); wrong['parameters']['derivation']['cell_edits'] = False
        with self.assertRaisesRegex(ValueError, 'corridor differs'): f.reference(self.root, wrong)
        p['import_hash'] = digest(p['parameters']['imports'][1])
        with self.assertRaisesRegex(ValueError, 'selected import'): f.reference(self.root, p)
        p['parameters']['imports'][1]['mode'] = 'color'
        with self.assertRaises(ValueError): rp.validate(p['parameters'])

    def test_negative_edit_crop_mask_and_budget_boundaries(self):
        p, c = prepare(self.root)
        cases = []
        q = deepcopy(p); q['crop'] = [2, 1, 4, 4]; cases.append(q)
        q = deepcopy(p); q['crop'] = [2, 1, 4, 4]
        q['edits'] = [{'x': 1, 'y': y, 'before': 'ink', 'after': 'empty'} for y in range(1, 4)]; cases.append(q)
        q = deepcopy(p); q['protected_mask'][0][0] = True; cases.append(q)
        q = deepcopy(p); q['protected_mask'][1][1] = True; cases.append(q)
        q = deepcopy(p); q['crop'] = [0, 0, 4, 4]; q['protected_mask'][0][0] = True
        q['edits'] = [{'x': 0, 'y': 0, 'before': 'empty', 'after': 'ink'}]; cases.append(q)
        q = deepcopy(p); q['edits'] *= 2; cases.append(q)
        q = deepcopy(p); q['edits'][0]['before'] = 'empty'; cases.append(q)
        q = deepcopy(p); q['edits'][0]['after'] = 'new-color'; cases.append(q)
        q = deepcopy(p); q['crop'] = [1, 1, 4, 4, 2]; cases.append(q)
        q = deepcopy(p); q['budgets']['max_changes'] = 0; cases.append(q)
        q = deepcopy(p); q['crop'] = [0, 0, 4, 4]; q['edits'] = []; cases.append(q)
        q = deepcopy(p); q['parameters']['constraints']['width']['kind'] = 'exact'; cases.append(q)
        q = deepcopy(p); q['edits'][0] = {'x': 0, 'y': 0, 'before': 'empty', 'after': 'ink'}; cases.append(q)
        for n, q in enumerate(cases):
            with self.subTest(case=n), self.assertRaises(ValueError): f.transform(q, c['design'], c['matrix'])

    def test_wrong_hash_extra_changes_stale_proof_and_pair_baseline(self):
        p, c = prepare(self.root, paired=True)
        f.derive(self.root, approve_plan(self.root, p), self.root / 'fixed')
        with self.assertRaises(Aborted): f.inspect(self.root, self.root / 'fixed', Budget(30, 0))
        tight = deepcopy(p); tight['budgets']['verify_lines'] = 1
        with self.assertRaises(Aborted): f.reference(self.root, tight, Budget(30, 100000))
        p['reference']['manifest_sha256'] = 'f' * 64
        with self.assertRaisesRegex(ValueError, 'manifest hash'): f.reference(self.root, p)
        directory = self.root / 'fixed'
        originals = {v.name: v.read_bytes() for v in directory.iterdir()}
        for name, mutate in (
            ('record.json', lambda v: v['matrix'][0].__setitem__(0, 'ink')),
            ('proof.json', lambda v: v.__setitem__('logic_hash', 'f' * 64)),
            ('baseline-proof.json', lambda v: v.__setitem__('logic_hash', 'f' * 64)),
            ('assessment.json', lambda v: v.__setitem__('r4_required', True))):
            with self.subTest(name=name):
                value = load_json(directory / name); mutate(value); write_json(directory / name, value)
                manifest = load_json(directory / 'manifest.json'); manifest['files'][name] = images.file_hash(directory / name)
                write_json(directory / 'manifest.json', manifest)
                with self.assertRaises(ValueError): f.inspect(self.root, directory)
                for n, raw in originals.items(): (directory / n).write_bytes(raw)
        (directory / 'baseline-proof.json').unlink()
        with self.assertRaises(ValueError): f.inspect(self.root, directory)
