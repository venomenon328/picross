"""Fast data/projection contract, standard library only."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.puzzle_production import puzzle_record
from tests.puzzle_production.catalog_fixtures import registered
from tempfile import TemporaryDirectory
from tools.puzzle_production.contract import InvalidInput, load_json
from ci_scope import classify, FLAGS


class RegistryTests(unittest.TestCase):
    def test_production_registry_identity_fields(self):
        with TemporaryDirectory() as temp:
            root = Path(temp) / "base"
            registered(Path(temp), stem="contract", save_slot="contract")
            record = puzzle_record.load(root, "pz-current", category_catalog=None)
            raw = (root / record["definition"]["file"]).read_bytes()
            for field, value in (("save_slot", "con"), ("visible", 1), ("id", "pz-new"), ("extra", 1)):
                with self.subTest(field=field), self.assertRaises(InvalidInput):
                    puzzle_record.validate({**record, field: value}, "pz-current", raw)
            encoded = puzzle_record.encode(record)
            for malformed in (encoded.replace(b'"visible":', b'"visible":true,"visible":'), encoded + b" "):
                with self.assertRaises(ValueError):
                    puzzle_record.decode(malformed, "pz-current")

    def test_registry_and_new_harness_select_required_work(self):
        p = classify(["content/puzzles/pz-current.json"])["selected"]
        self.assertFalse(any(p[k] for k in FLAGS))
        plan = classify(["tools/za1_product.py"])
        self.assertEqual(plan["native_groups"], ["adapters", "export"])
        self.assertTrue(plan["selected"]["product"] and plan["selected"]["pilots"])
