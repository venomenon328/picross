"""Fast data/projection contract, standard library only."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.puzzle_production.content_registry import check_checkout, validate
from tools.puzzle_production.contract import InvalidInput
from ci_scope import classify, FLAGS


class RegistryTests(unittest.TestCase):
    def test_runtime_is_exact_projection_and_old_reservations_immutable(self):
        registry = check_checkout(Path(__file__).resolve().parents[1])
        self.assertEqual([e["key"] for e in registry["entries"] if e["visible"]][:6], ["f01","f02","f04","f06","f08","f09"])
        for field,value in (("save_slot","other"),("visible",True),("id","pz-new")):
            changed = deepcopy(registry)
            changed["entries"][2][field] = value
            with self.assertRaises(InvalidInput): validate(changed)

    def test_registry_and_new_harness_select_required_work(self):
        p = classify(["content/registry.json"])["selected"]
        self.assertTrue(all(p[k] for k in ("production","product","pilots","visual","perf_b")))
        p = classify(["tools/za1_product.py"])["selected"]
        self.assertTrue(all(p[k] for k in FLAGS))
