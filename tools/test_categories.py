"""Fast KAT-1 schema, bounds, initial inventory and projection checks."""
from copy import deepcopy
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.puzzle_production import categories
from tools.puzzle_production.content_registry import validate, projection, check_checkout
from tools.puzzle_production.contract import InvalidInput, load_json, write_json
from ci_scope import classify

ROOT = Path(__file__).resolve().parents[1]


class CategoryTests(unittest.TestCase):
    def setUp(self):
        self.catalog = categories.load(ROOT / "tests/puzzle_production/fixtures/catalog/categories.json")
        self.registry = load_json(ROOT / "tests/puzzle_production/fixtures/catalog/registry.json")

    def test_frozen_pre_migration_inputs(self):
        folder = ROOT / "game/tests/fixtures/kat1"
        provenance = load_json(folder / "provenance.json")
        self.assertTrue(provenance["test_only"])
        self.assertEqual(provenance["source_commit"], "0da2bb67f15c3fad90ed276518b3d31f225d9c41")
        files = {folder / name: digest for name, digest in provenance["saves"].items()}
        files[ROOT / "game/tests/kat1_save_seed.gd"] = provenance["seed_script_sha256"]
        files[ROOT / "tests/puzzle_production/fixtures/za1-v1-export.zip"] = provenance["legacy_export_sha256"]
        for path, digest in files.items():
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest, path.name)

    def test_initial_inventory_and_assignments(self):
        expected = [
            ("obst-nuesse", "Obst & Nüsse"), ("gemuese-pilze-kraeuter", "Gemüse, Pilze & Kräuter"),
            ("gerichte-herzhaftes", "Gerichte & Herzhaftes"), ("suesses-getraenke", "Süßes & Getränke"),
            ("saeuger", "Säugetiere"), ("voegel", "Vögel"), ("wasserwelt", "Wasserwelt"),
            ("insekten-kleine-tiere", "Insekten & kleine Tiere"), ("blumen-pflanzen", "Blumen & Pflanzen"),
            ("landschaften-natur", "Landschaften & Natur"), ("gebaeude-bauwerke", "Gebäude & Bauwerke"),
            ("fahrzeuge-verkehr", "Fahrzeuge & Verkehr"), ("technik-erfindungen", "Technik & Erfindungen"),
            ("werkzeuge-handwerk", "Werkzeuge & Handwerk"), ("haushalt-alltag", "Haushalt & Alltag"),
            ("kleidung-accessoires", "Kleidung & Accessoires"), ("musik-buehne", "Musik & Bühne"),
            ("sport-spiele", "Sport & Spiele"), ("menschen-berufe", "Menschen & Berufe"),
            ("mythen-fantasie", "Mythen & Fantasie")]
        self.assertEqual([(c["id"], c["name"]) for c in categories.ordered(self.catalog)], expected)
        self.assertEqual([c["order"] for c in categories.ordered(self.catalog)], list(range(1, 21)))
        self.assertEqual([e["category_id"] for e in self.registry["entries"][:9]], [
            "fahrzeuge-verkehr", "gebaeude-bauwerke", None, "gemuese-pilze-kraeuter", None,
            "gebaeude-bauwerke", None, "blumen-pflanzen", "voegel"])
        check_checkout(ROOT)

    def test_category_fields_types_duplicates_and_limits(self):
        for field, values in {
            "id": [None, [], "", "Ä", "Upper", "a_b", "a" * 65, "a\n"],
            "name": [None, "", " ", " x", "x\n", "x\x7f", "x" * 129],
            "order": [None, True, 1.5, 0, 10001],
        }.items():
            for value in values:
                raw = deepcopy(self.catalog)
                raw["categories"][0][field] = value
                with self.subTest(field=field, value=value), self.assertRaises(InvalidInput):
                    categories.validate(raw)
        for field in ("id", "order"):
            raw = deepcopy(self.catalog)
            raw["categories"][1][field] = raw["categories"][0][field]
            with self.assertRaisesRegex(InvalidInput, "Duplicate category"):
                categories.validate(raw)
        for raw in ({**self.catalog, "format": "unknown"}, {**self.catalog, "extra": True},
                    {**self.catalog, "categories": {}},
                    {**self.catalog, "categories": [{}] * 257}):
            with self.assertRaises(InvalidInput): categories.validate(raw)
        raw = {"format": categories.FORMAT, "categories": [
            {"id": "a" + str(i), "name": "x" * 128, "order": i + 1} for i in range(256)]}
        categories.validate(raw)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "categories.json"
            for data in ('{"format":1,"format":2}', '{"order":NaN}', ' ' * (categories.MAX_BYTES + 1)):
                path.write_text(data, encoding="utf-8")
                with self.assertRaises(InvalidInput): categories.load(path)
            write_json(path, raw)
            self.assertEqual(categories.load(path), raw)

    def test_association_required_and_reference_removal_rejected(self):
        for value in (None, "missing", [], ["voegel", "wasserwelt"]):
            raw = deepcopy(self.registry)
            raw["entries"][0]["category_id"] = value
            with self.assertRaises(InvalidInput): validate(raw, self.catalog)
        raw = deepcopy(self.registry)
        del raw["entries"][0]["category_id"]
        with self.assertRaises(InvalidInput): validate(raw, self.catalog)
        raw = deepcopy(self.registry)
        raw["entries"][0]["category_ids"] = ["voegel"]
        with self.assertRaises(InvalidInput): validate(raw, self.catalog)
        catalog = deepcopy(self.catalog)
        catalog["categories"] = [c for c in catalog["categories"] if c["id"] != "voegel"]
        with self.assertRaisesRegex(InvalidInput, "Unknown category_id: voegel"):
            validate(self.registry, catalog)

    def test_order_is_data_and_names_are_not_puzzle_identity(self):
        catalog = deepcopy(self.catalog)
        catalog["categories"].reverse()
        self.assertEqual(projection(self.registry, catalog), projection(self.registry, self.catalog))
        catalog["categories"][0]["name"] = "Neuer Name"
        validate(self.registry, catalog)
        self.assertEqual(projection(self.registry, catalog)["entries"], projection(self.registry, self.catalog)["entries"])
        for path in (categories.PATH, "game/data/registry.json", "tools/puzzle_production/categories.py"):
            selected = classify([path])["selected"]
            self.assertEqual(selected["production"], path == "tools/puzzle_production/categories.py", path)
