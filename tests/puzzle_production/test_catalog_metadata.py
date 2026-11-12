"""PE-A1: current metadata, explicit migration and shared transaction boundaries.

Only small synthetic registered inputs are used. Historical receipts remain
independently checked; no real catalog, player profile or image is modified.
"""
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tests.puzzle_production.catalog_fixtures import pre_metadata, registered
from tools.puzzle_production import catalog_background as background
from tools.puzzle_production import catalog_io as io, catalog_metadata as metadata
from tools.puzzle_production import catalog_transaction as tx, categories, content_registry as registry
from tools.puzzle_production.contract import load_json, write_json
from tools.puzzle_production.za1_fixtures import ROOT


def snapshot(root):
    return {p.relative_to(root).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
            for p in root.rglob("*") if p.is_file()}


def contents(root):
    return {name: row[0] for name, row in snapshot(root).items()}


class MetadataTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name)
        self.checked = registered(self.home, stem="pe_test", save_slot="pe_test")
        self.root = self.home / "base"
        self.original = registry.check_checkout(self.root)
        self.entry = self.original["entries"][0]
        self.identifier = self.entry["id"]

    def edit(self, operations):
        plan = metadata.plan(self.root, operations)
        return metadata.apply(self.root, plan)

    def current(self):
        return load_json(self.root / registry.REGISTRY)["metadata"]

    def test_view_resolves_current_metadata_without_definition_image_or_proof_reads(self):
        self.edit([{"op": "set_metadata", "id": self.identifier,
                    "name": "Aktueller Name", "category_id": "wasserwelt"}])
        reads = []
        original_read = io.read

        def observe(root, name, *args, **kwargs):
            reads.append(name)
            return original_read(root, name, *args, **kwargs)

        before = snapshot(self.root)
        with patch.object(io, "read", side_effect=observe):
            cached = metadata.MetadataView(self.root)
            view = cached.document()
        self.assertEqual(view["format"], "picross-metadata-view-v1")
        self.assertEqual(view["entries"], [{"id": self.identifier, "name": "Aktueller Name",
                                            "category_id": "wasserwelt"}])
        self.assertEqual(reads, [categories.PATH, registry.REGISTRY])
        with patch.object(io, "read", side_effect=AssertionError("Cached lookup opened a source")):
            for _ in range(3):
                self.assertEqual(cached.lookup(self.identifier), view["entries"][0])
            self.assertEqual(cached.document(), view)
        self.assertEqual(snapshot(self.root), before)

    def test_view_rejects_pending_publication_and_racing_indexes(self):
        original_read = io.read
        markers = (tx.LOCK, "content/.registration-journal-" + "a" * 64 + ".tmp")
        for name in markers:
            marker = self.root / name
            marker.write_bytes(b"foreign pending publication\n")
            before = snapshot(self.root)
            with self.subTest(marker=name, phase="before"), \
                    patch.object(io, "read", side_effect=AssertionError("Read a pending catalog")), \
                    self.assertRaisesRegex(ValueError, "recovery required"):
                metadata.view(self.root)
            self.assertEqual(snapshot(self.root), before)
            marker.unlink()
            raced = {}

            def pending_after_read(root, source, *args, **kwargs):
                raw = original_read(root, source, *args, **kwargs)
                if source == registry.REGISTRY:
                    marker.write_bytes(b"new foreign publication\n")
                    raced["state"] = snapshot(self.root)
                return raw

            with self.subTest(marker=name, phase="after"), \
                    patch.object(io, "read", side_effect=pending_after_read), \
                    self.assertRaisesRegex(ValueError, "recovery required"):
                metadata.view(self.root)
            self.assertEqual(snapshot(self.root), raced["state"])
            marker.unlink()
        for name in (categories.PATH, registry.REGISTRY):
            before = snapshot(self.root)

            def replace_after_read(root, source, *args, **kwargs):
                raw = original_read(root, source, *args, **kwargs)
                if source == name:
                    target = self.root / name
                    info = target.stat()
                    replacement = self.home / "replacement-index.json"
                    replacement.write_bytes(raw)
                    os.utime(replacement, ns=(info.st_atime_ns, info.st_mtime_ns))
                    replacement.replace(target)
                return raw

            # Even identical bytes/size/mtime from a replaced index cannot be
            # combined into a view captured from different file identities.
            with self.subTest(index=name), patch.object(io, "read", side_effect=replace_after_read), \
                    self.assertRaisesRegex(ValueError, "Catalog changed"):
                metadata.view(self.root)
            self.assertEqual(snapshot(self.root), before)

    def test_strict_metadata_table_has_no_historical_fallback(self):
        good = deepcopy(self.original)
        attacks = {
            "missing": [],
            "duplicate": good["metadata"] * 2,
            "foreign": [dict(good["metadata"][0], id="pz-foreign")],
            "unknown-category": [dict(good["metadata"][0], category_id="missing")],
            "empty-name": [dict(good["metadata"][0], name="")],
            "whitespace-name": [dict(good["metadata"][0], name=" \t ")],
            "long-name": [dict(good["metadata"][0], name="x" * 129)],
            "name-type": [dict(good["metadata"][0], name=True)],
            "extra-field": [dict(good["metadata"][0], alias="no")],
        }
        for kind, rows in attacks.items():
            broken = deepcopy(good)
            broken["metadata"] = rows
            write_json(self.root / registry.REGISTRY, broken)
            before = snapshot(self.root)
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                metadata.view(self.root)
            self.assertEqual(snapshot(self.root), before)
        write_json(self.root / registry.REGISTRY, good)
        self.edit([{"op": "set_metadata", "id": self.identifier, "name": "x" * 128}])
        self.assertEqual(self.current()[0]["name"], "x" * 128)

    def test_plan_is_read_only_and_edit_changes_only_registry_projection(self):
        before = contents(self.root)
        plan = metadata.plan(self.root, [{"op": "set_metadata", "id": self.identifier,
                                          "name": "Neuer Motivname", "category_id": "wasserwelt"}])
        self.assertEqual(contents(self.root), before)
        self.assertEqual(plan["format"], "picross-editor-metadata-plan-v1")
        self.assertEqual(set(plan["files"]), {registry.REGISTRY, registry.RUNTIME})
        self.assertEqual(metadata.apply(self.root, plan)["status"], "updated")
        after = contents(self.root)
        self.assertEqual({name for name in before if before[name] != after[name]},
                         {registry.REGISTRY, registry.RUNTIME})
        self.assertEqual(set(after), set(before))
        current = registry.check_checkout(self.root)
        self.assertEqual(current["entries"], self.original["entries"])
        runtime = load_json(self.root / registry.RUNTIME)
        self.assertEqual(runtime["format"], "picross-runtime-registry-v7")
        self.assertEqual(runtime["entries"][0]["name"], "Neuer Motivname")
        self.assertEqual(runtime["entries"][0]["category_id"], "wasserwelt")

    def test_repeated_identical_edit_and_empty_plan_preserve_bytes_and_mtimes(self):
        request = [{"op": "set_metadata", "id": self.identifier, "name": "Erhalten"}]
        self.edit(request)
        before = snapshot(self.root)
        self.assertEqual(self.edit(request)["status"], "noop")
        self.assertEqual(self.edit([])["status"], "noop")
        self.assertEqual(snapshot(self.root), before)
        noop = metadata.plan(self.root, [])
        (self.root / tx.LOCK).write_bytes(b'pending foreign journal\n')
        pending = snapshot(self.root)
        with self.assertRaises(ValueError):
            metadata.apply(self.root, noop)
        self.assertEqual(snapshot(self.root), pending)

    def test_noop_rejects_publication_appearing_after_final_source_guard(self):
        noop = metadata.plan(self.root, [])
        original_guard = tx.guard
        for name in (tx.LOCK, "content/.registration-journal-" + "b" * 64 + ".tmp"):
            marker = self.root / name
            raced = {}

            def guarded(*args, **kwargs):
                result = original_guard(*args, **kwargs)
                marker.write_bytes(b"foreign publication after source guard\n")
                raced["state"] = snapshot(self.root)
                return result

            with self.subTest(marker=name), patch.object(tx, "guard", side_effect=guarded), \
                    self.assertRaisesRegex(ValueError, "recovery required"):
                metadata.apply(self.root, noop)
            self.assertEqual(snapshot(self.root), raced["state"])
            marker.unlink()

    def test_real_cli_plan_apply_and_invalid_request_preserve_source_bytes(self):
        operations = self.home / "operations.json"
        plan = self.home / "cli-plan.json"
        write_json(operations, [{"op": "set_metadata", "id": self.identifier,
                                 "name": "Überarbeiteter Motivname"}])

        def run(command, *arguments):
            return subprocess.run([sys.executable, "-m", "tools.puzzle_production.metadata_cli",
                                   command, "--target-root", str(self.root), *map(str, arguments)],
                                  cwd=ROOT, capture_output=True, text=True, timeout=60)

        before = snapshot(self.root)
        planned = run("plan", "--operations", operations, "--output", plan)
        self.assertEqual(planned.returncode, 0, planned.stdout + planned.stderr)
        self.assertEqual(json.loads(planned.stdout)["status"], "written")
        self.assertFalse(plan.read_bytes().startswith(b"\xef\xbb\xbf"))
        self.assertIn("Überarbeiteter Motivname", plan.read_text(encoding="utf-8"))
        self.assertEqual(snapshot(self.root), before)
        applied = run("apply", "--plan", plan)
        self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
        self.assertEqual(json.loads(applied.stdout)["status"], "updated")
        self.assertEqual(self.current()[0]["name"], "Überarbeiteter Motivname")
        write_json(operations, [{"op": "category_delete", "id": "voegel"}])
        before = snapshot(self.root)
        rejected = run("plan", "--operations", operations)
        self.assertEqual(rejected.returncode, 2, rejected.stdout + rejected.stderr)
        self.assertEqual(json.loads(rejected.stdout)["status"], "invalid_input")
        self.assertEqual(snapshot(self.root), before)

    def test_category_creation_rename_assignment_and_empty_deletion(self):
        before = categories.load(self.root / categories.PATH)
        plan = metadata.plan(self.root, [{"op": "category_create", "name": "Neue Kategorie"}])
        identifier = plan["operations"][0]["id"]
        self.assertRegex(identifier, categories.ID)
        metadata.apply(self.root, plan)
        created = categories.lookup(categories.load(self.root / categories.PATH), identifier)
        self.assertEqual(created["order"], max(row["order"] for row in before["categories"]) + 1)
        self.edit([{"op": "category_rename", "id": identifier, "name": "Umbenannt"},
                   {"op": "set_metadata", "id": self.identifier, "category_id": identifier}])
        self.assertEqual(self.current()[0]["category_id"], identifier)
        self.assertEqual(categories.lookup(categories.load(self.root / categories.PATH), identifier)["name"], "Umbenannt")
        self.edit([{"op": "set_metadata", "id": self.identifier, "category_id": "voegel"},
                   {"op": "category_delete", "id": identifier}])
        self.assertEqual(categories.load(self.root / categories.PATH), before)

    def test_occupied_category_requires_other_target_and_preserves_historical_origin(self):
        before = snapshot(self.root)
        for request in ({"op": "category_delete", "id": "voegel"},
                        {"op": "category_delete", "id": "voegel", "reassign_to": "voegel"},
                        {"op": "category_delete", "id": "voegel", "reassign_to": "missing"}):
            with self.subTest(request=request), self.assertRaises(ValueError):
                metadata.plan(self.root, [request])
            self.assertEqual(snapshot(self.root), before)
        self.edit([{"op": "category_delete", "id": "voegel", "reassign_to": "wasserwelt"}])
        current = registry.check_checkout(self.root)
        self.assertEqual(current["entries"], self.original["entries"])
        self.assertEqual(self.current()[0]["category_id"], "wasserwelt")
        self.assertNotIn("voegel", {row["id"] for row in categories.load(self.root / categories.PATH)["categories"]})
        # The compact receipt still contains the actual original category and
        # all other production fields; merely matching its ID is insufficient.
        receipt = self.root / self.entry["production"]["package"] / "manifest.json"
        self.assertEqual(receipt.read_bytes(), before[receipt.relative_to(self.root).as_posix()][0])
        tampered = load_json(receipt)
        tampered["entry"]["category_id"] = "wasserwelt"
        write_json(receipt, tampered)
        with self.assertRaises(ValueError):
            registry.check_checkout(self.root)

    def test_migration_is_explicit_lossless_and_idempotent(self):
        for legacy_format in ("picross-content-registry-v2", "picross-content-registry-v3"):
            with self.subTest(format=legacy_format):
                pre_metadata(self.root)
                if legacy_format.endswith("v3"):
                    old = load_json(self.root / registry.REGISTRY)
                    old.update(format=legacy_format, backgrounds=[])
                    write_json(self.root / registry.REGISTRY, old)
                    write_json(self.root / background.CAPABILITY, {
                        "format": background.CAPABILITY_FORMAT,
                        "runtime_format": background.RUNTIME_FORMAT,
                        "profile_id": "picross-background-png2304-v1", "enabled": True})
                    write_json(self.root / registry.RUNTIME, registry.projection(
                        old, categories.load(self.root / categories.PATH), self.root))
                registry.check_checkout(self.root)
                before = contents(self.root)
                plan = metadata.plan_migration(self.root)
                self.assertEqual(contents(self.root), before)
                self.assertEqual(metadata.apply(self.root, plan)["status"], "migrated")
                after = contents(self.root)
                self.assertEqual(set(before), set(after))
                self.assertEqual({name for name in before if before[name] != after[name]},
                                 {registry.REGISTRY, registry.RUNTIME})
                self.assertEqual(registry.check_checkout(self.root)["entries"], self.original["entries"])
                self.assertEqual(self.current(), self.original["metadata"])
                unchanged = snapshot(self.root)
                self.assertEqual(metadata.apply(self.root, metadata.plan_migration(self.root))["status"], "noop")
                self.assertEqual(snapshot(self.root), unchanged)

    def test_legacy_mutations_stop_with_migration_instruction(self):
        pre_metadata(self.root)
        before = snapshot(self.root)
        registry.sync_runtime(self.root)
        self.assertEqual(snapshot(self.root), before)
        # An already correct old projection is a valid no-op. Rebuilding an
        # earlier valid projection would write and requires explicit migration.
        pre_metadata(self.root, runtime_version=4)
        before = snapshot(self.root)
        for action in (lambda: metadata.plan(self.root, [{"op": "set_metadata", "id": self.identifier, "name": "X"}]),
                       lambda: registry.sync_runtime(self.root)):
            with self.assertRaisesRegex(ValueError, "[Mm]igrat"):
                action()
            self.assertEqual(snapshot(self.root), before)
        self.assertEqual(metadata.view(self.root)["entries"], self.original["metadata"])

    def test_stale_plan_preserves_foreign_sources_and_unknown_namespace(self):
        request = [{"op": "set_metadata", "id": self.identifier, "name": "Planned"}]
        for name in (categories.PATH, "game/" + self.entry["definition"],
                     "content/difficulty/" + self.identifier + "/rating.json"):
            plan = metadata.plan(self.root, request)
            target = self.root / name
            old = target.read_bytes()
            target.write_bytes(old + b" ")
            before = snapshot(self.root)
            with self.subTest(name=name), self.assertRaises(ValueError):
                metadata.apply(self.root, plan)
            self.assertEqual(snapshot(self.root), before)
            target.write_bytes(old)
        plan = metadata.plan(self.root, request)
        stranger = self.root / "content/added/pz-foreign.json"
        stranger.write_bytes(b"foreign namespace\n")
        before = snapshot(self.root)
        with self.assertRaises(ValueError):
            metadata.apply(self.root, plan)
        self.assertEqual(snapshot(self.root), before)

    def test_edit_after_planning_makes_first_plan_stale(self):
        first = metadata.plan(self.root, [{"op": "set_metadata", "id": self.identifier, "name": "First"}])
        self.edit([{"op": "set_metadata", "id": self.identifier, "category_id": "wasserwelt"}])
        before = snapshot(self.root)
        with self.assertRaises(ValueError):
            metadata.apply(self.root, first)
        self.assertEqual(snapshot(self.root), before)

    def test_migration_and_combined_category_delete_recover_without_mixed_state(self):
        for operation in ("migration", "category-delete"):
            if operation == "migration":
                pre_metadata(self.root)
                plan = metadata.plan_migration(self.root)
            else:
                metadata.apply(self.root, metadata.plan_migration(self.root))
                plan = metadata.plan(self.root, [{"op": "category_delete", "id": "voegel", "reassign_to": "wasserwelt"}])
            before = contents(self.root)
            with self.subTest(operation=operation), self.assertRaises(InterruptedError):
                metadata.apply(self.root, plan, fail_step="crash-index")
            self.assertTrue((self.root / tx.LOCK).exists())
            with self.assertRaises(ValueError):
                metadata.plan(self.root, [])
            metadata.recover(self.root)
            self.assertEqual(contents(self.root), before)
            self.assertFalse((self.root / tx.LOCK).exists())
            registry.check_checkout(self.root)

    def test_foreign_recovery_target_and_tampered_plan_are_not_overwritten(self):
        plan = metadata.plan(self.root, [{"op": "set_metadata", "id": self.identifier, "name": "Changed"}])
        broken = deepcopy(plan)
        broken["operations"][0]["name"] = "Unbound change"
        before = snapshot(self.root)
        with self.assertRaises(ValueError):
            metadata.apply(self.root, broken)
        self.assertEqual(snapshot(self.root), before)
        with self.assertRaises(InterruptedError):
            metadata.apply(self.root, plan, fail_step="crash-index")
        target = self.root / registry.REGISTRY
        own = target.read_bytes()
        target.write_bytes(own + b"foreign\n")
        foreign = snapshot(self.root)
        with self.assertRaises(ValueError):
            metadata.recover(self.root)
        self.assertEqual(snapshot(self.root), foreign)
        target.write_bytes(own)
        metadata.recover(self.root)
        registry.check_checkout(self.root)

    def test_category_and_puzzle_value_boundaries_reject_before_mutation(self):
        before = snapshot(self.root)
        operations = [
            {"op": "set_metadata", "id": "pz-missing", "name": "X"},
            {"op": "set_metadata", "id": self.identifier, "category_id": "missing"},
            {"op": "set_metadata", "id": self.identifier, "name": " \n "},
            {"op": "set_metadata", "id": self.identifier, "name": "x" * 129},
            {"op": "category_create", "name": " leading"},
            {"op": "category_create", "name": "bad\nname"},
            {"op": "category_rename", "id": "voegel", "name": ""},
            {"op": "category_delete", "id": "missing"},
            {"op": "replace_registry", "entries": []},
        ]
        for operation in operations:
            with self.subTest(operation=operation), self.assertRaises(ValueError):
                metadata.plan(self.root, [operation])
            self.assertEqual(snapshot(self.root), before)


if __name__ == "__main__":
    unittest.main()
