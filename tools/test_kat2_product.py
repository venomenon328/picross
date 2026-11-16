"""Small P2-E-A-V02 selection/checkpoint/boundary counterexamples; no renderer."""
from copy import deepcopy
import math
import json
from pathlib import Path
import tempfile
import unittest

from ci_scope import classify
from native_contract import CATALOG_CASES, CATALOG_MODES, checks
from native_results import validate_catalog_cases


def report(mode):
    cases = [dict(id=name, checks=1) for name in CATALOG_CASES[mode]]
    result = dict(mode=mode, checks=len(cases), failures=[], catalog_cases=cases)
    if mode == 'ke':
        # Independent simple physical example: available = window/2 - 200.
        # Two 400px cards plus 15px gap cross at physical width 2030.
        result['resize_samples'] = [dict(width=w, height=math.floor(w*9/16+0.5),
            ui_scale=1.25, role=role, minimum_width=400, gap=15, available=w/2-200,
            columns=columns) for w, role, columns in
            [(1280, 'reference', 1), (1920, 'reference', 1), (2560, 'reference', 2),
             (2022, 'below', 1), (2038, 'above', 2)]]
    return result


class CatalogMatrix(unittest.TestCase):
    def test_selected_native_cases_and_all_eleven_modes(self):
        for mode in ('ke', 'kk', 'pages'):
            validate_catalog_cases(report(mode))
        self.assertEqual(CATALOG_MODES, ('regular', 'restart', 'pages', 'empty', 'invalid',
                         'adapter', 'information', 'kb', 'kk', 'ke', 'at'))
        for mode in CATALOG_MODES:
            self.assertIn('kat2-'+mode, checks('catalog'))
        for path in ('game/tests/kat2_probe.gd', 'tools/test_kat2_product.py'):
            plan = classify([path])
            self.assertEqual(plan['native_groups'], ['catalog'])
            self.assertEqual(plan['browser_groups'], [])

    def test_adapter_historical_fixture_has_exact_v5_fields_and_preserves_sources(self):
        from tests.puzzle_production import current_fixtures as fixture
        from tests.puzzle_production.catalog_fixtures import pre_metadata
        from tools.puzzle_production import content_registry
        from product_fixtures import install_runtime_fixtures

        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            checkout = fixture.checkout(home / 'checkout')
            package = fixture.make(home / 'input', identifier='pz-test-kat2-adapter')
            content_registry.registration(package, checkout, apply=True)
            before = fixture.fingerprints(checkout)
            original = json.loads((checkout / 'game/data/registry.json').read_bytes())
            pre_metadata(checkout, runtime_version=5)
            install_runtime_fixtures(Path(__file__).resolve().parents[1], checkout / 'game', append=True)
            runtime = json.loads((checkout / 'game/data/registry.json').read_bytes())
            self.assertEqual(runtime['format'], 'picross-runtime-registry-v5')
            fields = {'id', 'key', 'save_slot', 'definition', 'reveal', 'visible',
                      'difficulty', 'added_at', 'category_id'}
            for entry in runtime['entries']:
                self.assertEqual(set(entry), fields)
            adapted = next(e for e in runtime['entries'] if e['id'] == 'pz-test-kat2-adapter')
            self.assertEqual(adapted, {k: v for k, v in original['entries'][0].items() if k in fields})
            self.assertEqual(runtime['categories'], original['categories'])
            after = fixture.fingerprints(checkout)
            for name, fingerprint in before.items():
                if name != 'game/data/registry.json':
                    self.assertEqual(after[name], fingerprint, name)

    def test_missing_duplicate_reordered_unexecuted_or_failed_case_is_rejected(self):
        for mode in ('ke', 'kk', 'pages'):
            original = report(mode)
            for index in range(len(original['catalog_cases'])):
                changed = deepcopy(original)
                changed['catalog_cases'].pop(index)
                changed['checks'] -= 1  # Even a consistently shortened summary fails.
                with self.subTest(mode=mode, index=index), self.assertRaises(ValueError):
                    validate_catalog_cases(changed)
            for mutate in (
                lambda r: r['catalog_cases'].append(r['catalog_cases'][0]),
                lambda r: r['catalog_cases'].reverse(),
                lambda r: r['catalog_cases'][0].update(checks=0),
                lambda r: r['catalog_cases'][0].update(checks=True),
                lambda r: r.update(checks=999),
                lambda r: r.update(failures=['native assertion']),
            ):
                changed = deepcopy(original)
                mutate(changed)
                with self.assertRaises(ValueError):
                    validate_catalog_cases(changed)

    def test_missing_forged_or_non_crossing_resize_evidence_is_rejected(self):
        original = report('ke')
        for mutate in (
            lambda r: r.pop(),
            lambda r: r[0].update(width=1279),
            lambda r: r[1].update(available=r[2]['available']),
            lambda r: r[3].update(width=2023),
            lambda r: r[3].update(columns=2),
            lambda r: r[4].update(available=814, columns=1),
            lambda r: r[4].update(height=1080),
            lambda r: r[4].update(available=float('nan')),
            lambda r: r[4].update(minimum_width=401),
            lambda r: r[4].update(role='reference'),
        ):
            changed = deepcopy(original)
            mutate(changed['resize_samples'])
            with self.assertRaises(ValueError):
                validate_catalog_cases(changed)


if __name__ == '__main__':
    unittest.main()
