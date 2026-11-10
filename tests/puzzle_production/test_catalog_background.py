"""HP-I1b1 closed sources and actual target-bound first registration."""
from copy import deepcopy
from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile

from tests.puzzle_production.background_catalog_fixtures import prepare
from tests.puzzle_production import catalog_fixtures, test_background_export as export_cases
from tools.puzzle_production import catalog_background as bg, content_registry as cr, target_adapter as adapter, categories
from tools.puzzle_production.contract import InvalidInput, load_json, write_json
from tools.puzzle_production.za1_fixtures import ROOT, isolated_checkout, rated_registration


def snapshot(root):
    return {p.relative_to(root).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
            for p in Path(root).rglob("*") if p.is_file()}


class CatalogBackgroundTests(unittest.TestCase):
    def test_selected_and_none_real_plan_registration_and_repeat_preserve_originals(self):
        for choice in ("selected", "none"):
            with self.subTest(choice=choice):
                f = prepare(self, choice)
                before = snapshot(f.checkout)
                original = snapshot(f.export)
                planned = rated_registration(f.export, f.checkout)
                self.assertEqual(planned["status"], "planned")
                self.assertEqual(snapshot(f.checkout), before)
                result = rated_registration(f.export, f.checkout, apply=True)
                self.assertEqual(result["status"], "registered")
                registry = cr.check_checkout(f.checkout, replay=True)
                self.assertEqual(registry["format"], cr.BACKGROUND_FORMAT)
                entry = registry["entries"][0]
                source = bg.load(f.checkout, registry, entry)
                self.assertEqual(source["image_revision"], 1)
                self.assertEqual(source["decision"]["outcome"], choice)
                self.assertEqual(source["origin"]["approval"], load_json(f.approval))
                self.assertEqual(source["origin"]["export_manifest_sha256"], entry["production"]["package_sha256"])
                runtime = load_json(f.checkout / cr.RUNTIME)
                self.assertEqual(runtime["format"], bg.RUNTIME_FORMAT)
                self.assertEqual(runtime["entries"][0]["background"]["status"], choice)
                self.assertEqual(set(runtime["entries"][0]), {
                    "id", "key", "save_slot", "definition", "reveal", "visible", "category_id", "difficulty", "added_at", "background"})
                expected = {entry["id"] + ".png", entry["id"] + ".txt"} if choice == "selected" else set()
                directory = f.checkout / bg.ASSET_PATH
                self.assertEqual({p.name for p in directory.iterdir()} if directory.exists() else set(), expected)
                self.assertEqual(snapshot(f.export), original)
                self.assertFalse(any(f.manifest[k] for k in ("integration_ready", "catalog_ready", "registered")))
                after = snapshot(f.checkout)
                self.assertEqual(rated_registration(f.export, f.checkout, apply=True)["status"], "no-op")
                self.assertEqual(snapshot(f.checkout), after)

    def test_closed_source_rejects_type_identity_rights_and_proof_binding_changes(self):
        f = prepare(self)
        manifest, report = adapter.verify_export(f.export)
        entry = cr.export_entry(f.export, manifest, report,
            categories.lookup(load_json(f.checkout / categories.PATH), manifest["category_id"]), background=True)
        source = bg.build(f.export, manifest, report, entry)
        cases = []
        def changed(*keys, value):
            result = deepcopy(source)
            target = result
            for key in keys[:-1]: target = target[key]
            target[keys[-1]] = value
            cases.append(result)
        changed("unexpected", value=True)
        changed("image_revision", value=True)
        changed("image_revision", value=2)
        changed("identity", "runtime_revision", value=True)
        changed("identity", "definition", "sha256", value="0" * 64)
        changed("candidate_revision", value=None)
        changed("provenance", "rights_status", value="unresolved")
        changed("review", "Q-HG01", "result", value="Warnung")
        changed("origin", "approval", "puzzle_id", value="pz-foreign")
        changed("derivation", "request_sha256", value="0" * 64)
        changed("derivation", "tool", "modules", value=[])
        changed("notice", "file", value="game/art/backgrounds/other.txt")
        for altered in cases:
            with self.subTest(altered=altered), self.assertRaises((InvalidInput, ValueError)):
                bg.validate(altered, entry)
        registry = {"format": cr.BACKGROUND_FORMAT, "entries": [entry],
                    "backgrounds": [{"id": entry["id"], "source": bg.ref(bg.path(entry["id"]), bg.encoded(source))}]}
        cr.validate(registry, load_json(f.checkout / categories.PATH))
        for change in (lambda r: r["backgrounds"].append(deepcopy(r["backgrounds"][0])),
                       lambda r: r["backgrounds"][0]["source"].update(file="content/backgrounds/other.json")):
            altered = deepcopy(registry); change(altered)
            with self.assertRaises(InvalidInput): cr.validate(altered, load_json(f.checkout / categories.PATH))

    def test_first_background_preserves_existing_legacy_entry_and_projects_legacy(self):
        f = prepare(self)
        with tempfile.TemporaryDirectory(prefix="hp-i1b1-legacy-") as temporary:
            base = Path(temporary)
            catalog_fixtures.registered(base, stem="legacy_bg_neighbor", save_slot="legacy_bg_neighbor")
            shutil.copytree(base / "base", f.checkout, dirs_exist_ok=True)
            prior = load_json(f.checkout / cr.REGISTRY)["entries"]
            result = rated_registration(f.export, f.checkout, apply=True)
            self.assertEqual(result["status"], "registered")
            current = cr.check_checkout(f.checkout)
            self.assertEqual([e for e in current["entries"] if e["id"] in {p["id"] for p in prior}], prior)
            rows = {e["id"]: e for e in load_json(f.checkout / cr.RUNTIME)["entries"]}
            for entry in prior:
                self.assertEqual(rows[entry["id"]]["background"], {"status": "legacy", "image_revision": None, "asset": None})
                self.assertFalse((f.checkout / bg.path(entry["id"])).exists())

    def test_none_live_files_and_changed_source_cannot_fall_back_to_legacy(self):
        f = prepare(self, "none", registered=True)
        registry = load_json(f.checkout / cr.REGISTRY)
        entry = registry["entries"][0]
        foreign = f.checkout / bg.asset_path(entry["id"])
        foreign.parent.mkdir(parents=True, exist_ok=True)
        foreign.write_bytes(b"not an allowed none texture")
        with self.assertRaises(InvalidInput): cr.check_checkout(f.checkout)
        foreign.unlink()
        original = deepcopy(registry)
        registry["backgrounds"] = []
        write_json(f.checkout / cr.REGISTRY, registry)
        with self.assertRaises(InvalidInput): cr.check_checkout(f.checkout)
        write_json(f.checkout / cr.REGISTRY, original)
        record = load_json(f.checkout / bg.path(entry["id"]))
        record["decision"]["statement"] = "An invented replacement decision"
        raw = bg.encoded(record)
        (f.checkout / bg.path(entry["id"])).write_bytes(raw)
        original["backgrounds"][0]["source"] = bg.ref(bg.path(entry["id"]), raw)
        write_json(f.checkout / cr.REGISTRY, original)
        with self.assertRaisesRegex(InvalidInput, "original approved production"):
            cr.check_checkout(f.checkout)

    def test_late_external_selection_has_the_same_compact_authority(self):
        case = export_cases.BackgroundExportTests(); case.setUp(); self.addCleanup(case.doCleanups)
        source, fixture, handoff, archive, approval, external, binding = case.late(dot=True)
        exported, manifest = case.export(archive, approval, external=external)
        checkout = isolated_checkout(case.root / "target")
        write_json(checkout / bg.CAPABILITY, {"format": bg.CAPABILITY_FORMAT, "runtime_format": bg.RUNTIME_FORMAT,
            "profile_id": "picross-background-png2304-v1", "enabled": True})
        self.assertEqual(rated_registration(exported, checkout, apply=True)["status"], "registered")
        registry = cr.check_checkout(checkout)
        active = bg.load(checkout, registry, registry["entries"][0])
        self.assertEqual(active["origin"]["manifest"], binding["manifest"])
        self.assertEqual(active["origin"]["approval"], load_json(approval))
        self.assertIsNotNone(active["decision"]["presented_package"])

    def test_runtime_capability_is_active_with_unchanged_strict_shape(self):
        value = load_json(ROOT / bg.CAPABILITY)
        self.assertIs(value["enabled"], True)
        self.assertTrue(bg.capability(ROOT))
        f = prepare(self)
        before = snapshot(f.checkout)
        for malformed in ({**value, "enabled": 1}, {**value, "unexpected": None}, {**value, "runtime_format": "future"}):
            write_json(f.checkout / bg.CAPABILITY, malformed)
            with self.assertRaises(InvalidInput): bg.capability(f.checkout)
        (f.checkout / bg.CAPABILITY).write_bytes(before[bg.CAPABILITY][0])

    def test_single_outer_zip_root_keeps_the_original_package_paths(self):
        f = prepare(self)
        wrapped = f.case.root / "wrapped.zip"
        with zipfile.ZipFile(wrapped, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for file in sorted(f.source.rglob("*")):
                if file.is_file(): archive.write(file, "outer/" + file.relative_to(f.source).as_posix())
        approval = f.case.case.approval(f.source, wrapped, name="wrapped-approval.json")
        exported, manifest = f.case.export(wrapped, approval, name="wrapped-export")
        self.assertEqual(rated_registration(exported, f.checkout, apply=True)["status"], "registered")
        registry = cr.check_checkout(f.checkout, replay=True)
        source = bg.load(f.checkout, registry, registry["entries"][0])
        self.assertEqual(source["origin"]["approval"], load_json(approval))
        self.assertEqual(source["origin"]["original_package"]["original_zip_sha256"], manifest["input"]["original_package"]["sha256"])


if __name__ == "__main__":
    unittest.main()
