"""KAT-1: real categorized export, compatibility and transaction failure paths."""
from tools.puzzle_production.za1_fixtures import rated_registration
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from tools.puzzle_production import categories, content_registry as registry, target_adapter as adapter
from tools.puzzle_production.contract import InvalidInput, load_json, write_json
from tools.puzzle_production.images import file_hash
from tools.puzzle_production.za1_fixtures import ROOT, FIXTURES, approve, isolated_checkout


class CategorizedAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.checkout = isolated_checkout(self.root / "checkout")
        self.catalog_path = self.checkout / categories.PATH
        self.catalog = categories.load(self.catalog_path)

    def snapshot(self, root):
        return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}

    def export(self, destination="export", name="direct-mono", category="voegel"):
        source = FIXTURES / name
        approval = self.root / (name + "-approval.json")
        approve(source, approval)
        out = self.root / destination
        adapter.export(source, out, name="TEST ONLY", revision=7, stem="pz-test-" + name,
                       save_slot="slot_pz-test-" + name, approval_path=approval,
                       category_id=category, categories_path=self.catalog_path)
        return out

    def test_extra_category_two_inputs_and_name_change_without_code_lists(self):
        self.catalog["categories"].append({"id": "test-only-extra", "name": "TEST ONLY", "order": 50})
        write_json(self.catalog_path, self.catalog)
        registry.sync_runtime(self.checkout)
        mono = self.export(category="test-only-extra")
        color = self.export("color", "direct-color", "voegel")
        # A new display name in the target is compatible with an older export snapshot.
        self.catalog["categories"][-1]["name"] = "TEST ONLY umbenannt"
        write_json(self.catalog_path, self.catalog)
        registry.sync_runtime(self.checkout)
        before = self.snapshot(self.checkout)
        plan = rated_registration(mono, self.checkout)
        self.assertEqual(plan["category"], self.catalog["categories"][-1])
        self.assertEqual(before, self.snapshot(self.checkout))
        for out in (mono, color):
            self.assertEqual(rated_registration(out, self.checkout, apply=True)["status"], "registered")
            self.assertEqual(rated_registration(out, self.checkout, apply=True)["status"], "no-op")
        checked = registry.check_checkout(self.checkout, replay=True)
        self.assertEqual({e["category_id"] for e in checked["entries"]
                          if e["id"] in ("pz-test-direct-mono", "pz-test-direct-color")}, {"voegel", "test-only-extra"})
        self.assertEqual(load_json(self.checkout / registry.RUNTIME), registry.projection(checked, self.catalog, self.checkout))
        self.assertFalse(any(p.name == "categories.json" for p in (self.checkout / "game").rglob("*")))

    def test_missing_unknown_multiple_and_conflicting_export_category(self):
        for i, category in enumerate((None, "unknown", ["voegel", "wasserwelt"])):
            with self.subTest(category=category), self.assertRaises(InvalidInput):
                self.export(str(i), category=category)
            self.assertFalse((self.root / str(i)).exists())
        out = self.export()
        rated_registration(out, self.checkout, apply=True)
        other = self.export("other", category="wasserwelt")
        before = self.snapshot(self.checkout)
        with self.assertRaisesRegex(InvalidInput, "Occupied"):
            rated_registration(other, self.checkout, apply=True)
        self.assertEqual(before, self.snapshot(self.checkout))

    def test_tampered_category_snapshot_and_reference_fail_before_mutation(self):
        out = self.export()
        original = self.snapshot(out)
        for attack in ("category", "multiple", "missing", "reference", "snapshot", "rehashed-snapshot"):
            for path, data in original.items(): (out / path).write_bytes(data)
            m = load_json(out / "manifest.json")
            if attack == "category": m["category_id"] = "wasserwelt"
            elif attack == "multiple": m["category_id"] = ["voegel", "wasserwelt"]
            elif attack == "missing": del m["category_id"]
            elif attack == "reference": m["categories"]["sha256"] = "0" * 64
            else:
                catalog = load_json(out / "categories.json")
                catalog["categories"] = [c for c in catalog["categories"] if c["id"] != "voegel"]
                write_json(out / "categories.json", catalog)
                if attack == "rehashed-snapshot":
                    m["files"]["categories.json"] = file_hash(out / "categories.json")
                    m["categories"]["sha256"] = m["files"]["categories.json"]
            write_json(out / "manifest.json", m)
            before = self.snapshot(self.checkout)
            with self.subTest(attack=attack), self.assertRaises(InvalidInput):
                rated_registration(out, self.checkout, apply=True)
            self.assertEqual(before, self.snapshot(self.checkout))

    def test_current_target_category_required_and_stale_projection_blocks(self):
        out = self.export(category="obst-nuesse")
        self.catalog["categories"] = [c for c in self.catalog["categories"] if c["id"] != "obst-nuesse"]
        write_json(self.catalog_path, self.catalog)
        before = self.snapshot(self.checkout)
        with self.assertRaisesRegex(InvalidInput, "stale"):
            rated_registration(out, self.checkout, apply=True)
        self.assertEqual(before, self.snapshot(self.checkout))
        registry.sync_runtime(self.checkout)
        before = self.snapshot(self.checkout)
        with self.assertRaisesRegex(InvalidInput, "Unknown category"):
            rated_registration(out, self.checkout, apply=True)
        self.assertEqual(before, self.snapshot(self.checkout))

    def test_direct_registry_edit_cannot_override_bound_category(self):
        out = self.export()
        rated_registration(out, self.checkout, apply=True)
        raw = load_json(self.checkout / registry.REGISTRY)
        raw["entries"][-1]["category_id"] = "wasserwelt"
        write_json(self.checkout / registry.REGISTRY, raw)
        write_json(self.checkout / registry.RUNTIME, registry.projection(raw, self.catalog, self.checkout))
        before = self.snapshot(self.checkout)
        for action in (lambda: registry.check_checkout(self.checkout), lambda: registry.sync_runtime(self.checkout)):
            with self.assertRaisesRegex(InvalidInput, "category differs"):
                action()
            self.assertEqual(before, self.snapshot(self.checkout))

    def test_frozen_v1_replays_and_new_export_preserves_sealed_approval_bytes(self):
        legacy = self.root / "legacy"
        with zipfile.ZipFile(ROOT / "tests/puzzle_production/fixtures/za1-v1-export.zip") as z:
            z.extractall(legacy)  # Repository-owned, fixed test-only fixture.
        before = self.snapshot(legacy)
        m, report = adapter.verify_export(legacy)
        self.assertEqual(m["format"], adapter.LEGACY_FORMAT)
        self.assertTrue(report["technical"] and report["editorial_approved"] and report["legacy_catalog_ready"])
        self.assertFalse(report["catalog_ready"] or report["category_ready"])
        checkout_before = self.snapshot(self.checkout)
        with self.assertRaisesRegex(InvalidInput, "legacy export"):
            rated_registration(legacy, self.checkout, apply=True)
        self.assertEqual(checkout_before, self.snapshot(self.checkout))
        new = self.root / "new"
        adapter.export(legacy / "input", new, name="TEST ONLY", revision=m["runtime_revision"],
                       stem=m["stem"], save_slot=m["save_slot"], approval_path=legacy / "approval.json",
                       category_id="voegel", categories_path=self.catalog_path)
        current, _ = adapter.verify_export(new)
        self.assertEqual(self.snapshot(legacy), before)
        for name in ("input/handoff.json", "input/inventory.json", "approval.json", m["definition"], m["reveal"]):
            self.assertEqual((new / name).read_bytes(), (legacy / name).read_bytes())
        for field in ("handoff_sha256", "inventory_sha256", "approval_sha256", "selection"):
            self.assertEqual(current[field], m[field])
        rated_registration(new, self.checkout, apply=True)

    def test_rollback_crash_recovery_and_old_journal_block(self):
        out = self.export()
        before = self.snapshot(self.checkout)
        for step in ("files", "index", "crash", "crash-index", "crash-runtime"):
            with self.subTest(step=step), self.assertRaises(OSError):
                rated_registration(out, self.checkout, apply=True, fail_step=step)
            if step.startswith("crash"):
                with self.assertRaisesRegex(InvalidInput, "Interrupted"):
                    registry.check_checkout(self.checkout)
                registry.recover(self.checkout)
            self.assertEqual(self.snapshot(self.checkout), before)
        lock = self.checkout / "content/.registration-pending.json"
        write_json(lock, {"format": "picross-registration-journal-v1", "old": "preserve historical bytes"})
        before = self.snapshot(self.checkout)
        for action in (lambda: registry.recover(self.checkout), lambda: registry.sync_runtime(self.checkout),
                       lambda: rated_registration(out, self.checkout, apply=True)):
            with self.assertRaises(InvalidInput): action()
            self.assertEqual(self.snapshot(self.checkout), before)

    def test_category_source_races_and_recovery_preserve_foreign_edits(self):
        out = self.export()
        original = self.catalog_path.read_bytes()
        before = self.snapshot(self.checkout)
        verify = adapter.verify_export
        for trigger in (1, 2, 3):
            calls = []
            def change(path):
                result = verify(path)
                calls.append(path)
                if len(calls) == trigger:
                    changed = deepcopy(self.catalog)
                    changed["categories"][0]["name"] = "Concurrent edit"
                    write_json(self.catalog_path, changed)
                return result
            with self.subTest(trigger=trigger), patch.object(adapter, "verify_export", side_effect=change):
                with self.assertRaisesRegex(InvalidInput, "changed"):
                    rated_registration(out, self.checkout, apply=True)
            self.assertEqual(categories.load(self.catalog_path)["categories"][0]["name"], "Concurrent edit")
            self.catalog_path.write_bytes(original)
            if (self.checkout / "content/.registration-pending.json").exists():
                registry.recover(self.checkout)
            self.assertEqual(self.snapshot(self.checkout), before)
        with self.assertRaises(InterruptedError):
            rated_registration(out, self.checkout, apply=True, fail_step="crash-index")
        self.catalog_path.write_bytes(original + b" ")
        interrupted = self.snapshot(self.checkout)
        with self.assertRaisesRegex(InvalidInput, "target changed.*categories.json"):
            registry.recover(self.checkout)
        self.assertEqual(self.snapshot(self.checkout), interrupted)
        self.catalog_path.write_bytes(original)
        registry.recover(self.checkout)
        self.assertEqual(self.snapshot(self.checkout), before)

    def test_cli_category_input_report_and_no_default(self):
        source = FIXTURES / "direct-mono"
        approval = self.root / "approval.json"
        approve(source, approval)
        command = [sys.executable, "-m", "tools.puzzle_production.target_adapter", "export", "--input", str(source),
                   "--approval", str(approval), "--name", "TEST ONLY", "--runtime-revision", "1", "--stem", "test",
                   "--save-slot", "test", "--output-dir", str(self.root / "cli")]
        missing = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=60)
        self.assertEqual(missing.returncode, 2)
        self.assertFalse((self.root / "cli").exists())
        for extra in (["--category-id", "voegel"], ["--categories", str(self.catalog_path)],
                      ["--category-id", "voegel", "--category-id", "wasserwelt", "--categories", str(self.catalog_path)],
                      ["--category-id", "voegel", "--categories", str(self.catalog_path), "--categories", str(self.catalog_path)]):
            rejected = subprocess.run(command + extra, cwd=ROOT, capture_output=True, text=True, timeout=60)
            self.assertEqual(rejected.returncode, 2, rejected.stdout + rejected.stderr)
            self.assertFalse((self.root / "cli").exists())
        result = subprocess.run(command + ["--category-id", "voegel", "--categories", str(self.catalog_path)],
                                cwd=ROOT, capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["category_id"], "voegel")

    def test_category_change_after_either_index_write_preserves_journal_until_resolved(self):
        out = self.export()
        before = self.snapshot(self.checkout)
        original = self.catalog_path.read_bytes()
        from tools.puzzle_production import catalog_publication as publication
        for index in (registry.REGISTRY, registry.RUNTIME):
            triggered = []
            def change(phase, path=None):
                if phase in ('P4','P5') and path == index and not triggered:
                    triggered.append(True)
                    self.catalog_path.write_bytes(original + b" ")
            with self.subTest(index=index), patch.object(publication, "checkpoint", side_effect=change):
                with self.assertRaisesRegex(InvalidInput, "target changed.*categories.json"):
                    rated_registration(out, self.checkout, apply=True)
            self.assertTrue(triggered)
            self.assertEqual(self.catalog_path.read_bytes(), original + b" ")
            interrupted = self.snapshot(self.checkout)
            with self.assertRaises(InvalidInput): registry.recover(self.checkout)
            self.assertEqual(self.snapshot(self.checkout), interrupted)
            self.catalog_path.write_bytes(original)
            registry.recover(self.checkout)
            self.assertEqual(self.snapshot(self.checkout), before)
