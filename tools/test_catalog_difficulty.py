"""KE minimal projection, strict failures and no production prose leakage."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.puzzle_production.catalog_difficulty import project
from tools.puzzle_production.content_registry import projection, validate
from tools.puzzle_production.contract import InvalidInput, load_json, canonical_bytes


def assessment():
    return dict(method="picross-difficulty-0.1", level="L3", assessment_type="editorial_estimate",
                confidence="low", plausible_range=["L2", "L4"], rule_families={"R1": "SECRET MOTIF"},
                bottleneck="SECRET MOTIF", evidence="private-production.json")


class DifficultyTests(unittest.TestCase):
    def test_projection_is_minimal_deterministic_and_detached(self):
        raw = assessment()
        result = project(raw)
        self.assertEqual(set(result), {"method", "level", "assessment_type", "confidence", "plausible_range", "r4_required"})
        self.assertNotIn(b"SECRET", canonical_bytes(result))
        self.assertNotIn(b"private", canonical_bytes(result))
        self.assertEqual(canonical_bytes(result), canonical_bytes(project(dict(reversed(list(raw.items()))))))
        result["plausible_range"][0] = "L1"
        self.assertEqual(raw["plausible_range"], ["L2", "L4"])
        self.assertIsNone(project({}))

    def test_all_levels_and_methods_without_reassessment(self):
        for method in ("picross-difficulty-0.1", "picross-difficulty-0.2"):
            for level in ("L1", "L2", "L3", "L4", "L5"):
                raw = assessment()
                raw.update(method=method, level=level, plausible_range=["L1", "L5"])
                self.assertEqual(project(raw)["level"], level)
                self.assertFalse(project(raw)["r4_required"])

    def test_invalid_present_metadata_is_never_missing(self):
        for field, values in {
            "method": [None, "unknown", 1, []], "level": ["L0", "L6", None, []],
            "assessment_type": [True, "guess"], "confidence": [None, "certain"],
            "plausible_range": [None, [], ["L1"], ["L4", "L2"], ["L1", "L2"], [True, "L5"]],
            "rule_families": [None, {}, {"R5": "x"}, {"R1": ""}], "r4_required": [1, None, True],
        }.items():
            for value in values:
                raw = assessment(); raw[field] = value
                with self.subTest(field=field, value=value), self.assertRaises(InvalidInput): project(raw)
        for raw in (None, [], False, {"level": "L2"}):
            with self.assertRaises(InvalidInput): project(raw)

    def test_r4_requires_existing_consistent_contract(self):
        raw = assessment()
        raw.update(method="picross-difficulty-0.2", level="L5", plausible_range=["L5", "L5"],
                   assessment_type="instrumented", confidence="medium", rule_families={"R4": "verified"},
                   logical_demand="linienübergreifend / besonders hoher logischer Anspruch")
        self.assertTrue(project(raw)["r4_required"])
        for field, value in (("method", "picross-difficulty-0.1"), ("level", "L4"),
                             ("assessment_type", "editorial_estimate"), ("confidence", "high"),
                             ("logical_demand", None), ("r4_required", False)):
            changed = deepcopy(raw); changed[field] = value
            with self.subTest(field=field), self.assertRaises(InvalidInput): project(changed)

    def test_writer_and_registry_validator_share_contract(self):
        root = Path(__file__).resolve().parents[1]/"tests/puzzle_production/fixtures/catalog"
        registry, catalog = load_json(root/"validation.json"), load_json(root/"categories.json")
        runtime = projection(registry, catalog)
        self.assertEqual(runtime["format"], "picross-runtime-registry-v5")
        self.assertTrue(all(len(e) == 9 and e["difficulty"] is None and e["added_at"] is None for e in runtime["entries"]))
        registry["entries"][0]["production"]["difficulty"] = assessment()
        validate(registry, catalog)
        self.assertEqual(projection(registry, catalog)["entries"][0]["difficulty"]["level"], "L3")
        registry["entries"][0]["production"]["difficulty"]["level"] = "L6"
        for action in (validate, projection):
            with self.assertRaises(InvalidInput): action(registry, catalog)
