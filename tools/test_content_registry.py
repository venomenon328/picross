"""Fast data/projection contract, standard library only."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.puzzle_production.content_registry import check_checkout, validate
from tools.puzzle_production.contract import InvalidInput, load_json
from ci_scope import classify, FLAGS


class RegistryTests(unittest.TestCase):
    def test_production_registry_identity_fields(self):
        registry = load_json(Path(__file__).resolve().parents[1] / "tests/puzzle_production/fixtures/catalog/validation.json")
        validate(registry, load_json(Path(__file__).resolve().parents[1] / "tests/puzzle_production/fixtures/catalog/categories.json"))
        for field,value in (("save_slot","con"),("visible",1),("id","pz-new")):
            changed = deepcopy(registry)
            changed["entries"][0][field] = value
            with self.assertRaises(InvalidInput): validate(changed, load_json(Path(__file__).resolve().parents[1] / "tests/puzzle_production/fixtures/catalog/categories.json"))

    def test_registry_and_new_harness_select_required_work(self):
        p = classify(["content/registry.json"])["selected"]
        self.assertFalse(any(p[k] for k in FLAGS))
        plan = classify(["tools/za1_product.py"])
        self.assertEqual(plan["native_groups"], ["adapters", "export"])
        self.assertTrue(plan["selected"]["product"] and plan["selected"]["pilots"])
