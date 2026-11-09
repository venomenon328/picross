"""HP-I1a: declared v6 exports never enter legacy catalog writers/readers."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools.puzzle_production import catalog_integration as integration
from tools.puzzle_production import catalog_transaction as tx
from tools.puzzle_production import content_registry as registry
from tools.puzzle_production import content_update, integrated_content, reveal_retirement, reveal_source
from tools.puzzle_production import target_adapter as adapter
from tools.puzzle_production.contract import InvalidInput, load_json, write_json
from tools.puzzle_production.za1_fixtures import ROOT, isolated_checkout
from tests.puzzle_production.catalog_fixtures import registered


V6 = "picross-target-export-v6"
BLOCKED = "Background export v6"


def snapshot(root):
    return {path.relative_to(root).as_posix(): (path.read_bytes(), path.stat().st_mtime_ns)
            for path in Path(root).rglob("*") if path.is_file()}


class BackgroundCatalogBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        temporary = tempfile.TemporaryDirectory(prefix="hp-i1a-catalog-base-")
        cls.addClassCleanup(temporary.cleanup)
        cls.base = Path(temporary.name)
        # A real, small legacy registration supplies unrelated valid catalog
        # prerequisites. It is never treated as a valid v6 production export.
        registered(cls.base, stem="hp_i1a_boundary", save_slot="hp_i1a_boundary")

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="hp-i1a-catalog-boundary-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.checkout = isolated_checkout(self.root / "checkout")
        self.exported = self.root / "background-export"
        self.exported.mkdir()
        # Deliberately no input ZIP or proof: generation rejection must precede
        # replay and must not depend on whether v6 content could be certified.
        self.manifest = {"format": V6, "integration_ready": False,
                         "catalog_ready": False, "registered": False}
        write_json(self.exported / "manifest.json", self.manifest)

    def cli(self, command, *arguments):
        completed = subprocess.run(
            [sys.executable, "-m", "tools.puzzle_production.target_adapter", command, *map(str, arguments)],
            cwd=ROOT, text=True, capture_output=True, timeout=30)
        self.assertEqual(completed.returncode, 2, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result["status"], "blocked", result)
        self.assertFalse(result["catalog_ready"])
        self.assertFalse(result["registered"])
        self.assertIn(BLOCKED, result["error"])
        return result

    def declared_catalog(self):
        shutil.copytree(self.base / "full-base", self.checkout, dirs_exist_ok=True)
        value = load_json(self.checkout / registry.REGISTRY)
        entry = value["entries"][0]
        path = self.checkout / entry["production"]["package"] / "manifest.json"
        manifest = load_json(path)
        manifest.update(self.manifest)
        write_json(path, manifest)
        entry["production"]["package_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        write_json(self.checkout / registry.REGISTRY, value)
        return deepcopy(entry)

    def git(self, *arguments):
        return subprocess.run(
            ["git", "-c", "user.name=HP-I1a synthetic test", "-c", "user.email=hp-i1a@example.invalid",
             "-c", "commit.gpgsign=false", *arguments], cwd=self.checkout,
            check=True, text=True, capture_output=True, timeout=15).stdout.strip()

    def test_new_export_apis_reject_v6_before_catalog_capture_or_full_replay(self):
        before = snapshot(self.root)
        operations = {
            "integrate-plan": lambda: integration.integrate(self.exported, self.checkout),
            "integrate-register": lambda: integration.integrate(self.exported, self.checkout, apply=True),
            "plan": lambda: registry.registration(self.exported, self.checkout),
            "register": lambda: registry.registration(self.exported, self.checkout, apply=True),
            "plan-update": lambda: content_update.update(self.exported, self.checkout, "0" * 64),
            "update": lambda: content_update.update(self.exported, self.checkout, "0" * 64, apply=True),
        }
        with patch.object(tx, "capture", side_effect=AssertionError("premature catalog capture")), \
                patch.object(adapter, "verify_export", side_effect=AssertionError("premature full replay")):
            for name, operation in operations.items():
                with self.subTest(api=name), self.assertRaisesRegex(InvalidInput, BLOCKED):
                    operation()
                self.assertEqual(snapshot(self.root), before)

    def test_new_export_cli_plan_register_and_update_reject_before_mutation(self):
        before = snapshot(self.root)
        for command in ("plan", "register", "plan-update", "update"):
            with self.subTest(command=command):
                arguments = ["--export", self.exported, "--checkout", self.checkout]
                if command in ("plan-update", "update"):
                    arguments.extend(("--expected-definition-sha256", "0" * 64))
                self.cli(command, *arguments)
                self.assertEqual(snapshot(self.root), before)

    def test_direct_export_entry_cannot_discard_background_binding(self):
        before = snapshot(self.root)
        with patch.object(registry, "file_hash", side_effect=AssertionError("projection accessed a file")), \
                self.assertRaisesRegex(InvalidInput, BLOCKED):
            registry.export_entry(self.exported, self.manifest, {}, {})
        self.assertEqual(snapshot(self.root), before)

    def test_declared_catalog_v6_is_rejected_by_quick_full_and_sync_apis(self):
        entry = self.declared_catalog()
        before = snapshot(self.root)
        operations = {
            "quick-package": lambda: reveal_source.package(self.checkout, entry),
            "quick-checkout": lambda: registry.check_checkout(self.checkout),
            "full-checkout": lambda: registry.check_checkout(self.checkout, replay=True),
            "sync": lambda: registry.sync_runtime(self.checkout),
        }
        with patch.object(adapter, "verify_export", side_effect=AssertionError("premature full replay")), \
                patch.object(tx, "execute", side_effect=AssertionError("catalog mutation")):
            for name, operation in operations.items():
                with self.subTest(api=name), self.assertRaisesRegex(InvalidInput, BLOCKED):
                    operation()
                self.assertEqual(snapshot(self.root), before)

    def test_declared_catalog_v6_is_rejected_by_check_and_sync_cli(self):
        self.declared_catalog()
        before = snapshot(self.root)
        for command in ("check-registry", "sync-runtime"):
            with self.subTest(command=command):
                self.cli(command, "--checkout", self.checkout)
                self.assertEqual(snapshot(self.root), before)

    def test_retirement_apis_and_cli_reject_declared_v6_before_deleting_sources(self):
        entry = self.declared_catalog()
        index = self.checkout / "content/authoring/index.json"
        index.parent.mkdir(parents=True, exist_ok=True)
        write_json(index, {"format": "picross-authoring-index-v1", "entries": []})
        self.git("init", "--quiet")
        self.git("add", ".")
        self.git("commit", "--quiet", "--message", "Synthetic unsupported catalog generation")
        commit = self.git("rev-parse", "HEAD")
        self.git("update-ref", "refs/remotes/origin/main", commit)
        before = snapshot(self.root)
        operations = {
            "retire-production": lambda: integrated_content.retire(self.checkout, [entry["id"]], commit),
            "retire-reveal-production": lambda: reveal_retirement.retire(
                self.checkout, [(entry["id"], "image-r01")], commit),
        }
        for name, operation in operations.items():
            with self.subTest(api=name), self.assertRaisesRegex(InvalidInput, BLOCKED):
                operation()
            self.assertEqual(snapshot(self.root), before)
        for command, selection in (
            ("retire-production", ("--puzzle-id", entry["id"])),
            ("retire-reveal-production", ("--authoring-revision", entry["id"], "image-r01")),
        ):
            with self.subTest(command=command):
                self.cli(command, "--checkout", self.checkout, "--integrated-commit", commit, *selection)
                self.assertEqual(snapshot(self.root), before)


if __name__ == "__main__":
    unittest.main()
