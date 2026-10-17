"""Completed production must not be needed by later registration or metadata edits."""
from tools.puzzle_production.za1_fixtures import rated_registration
from copy import deepcopy
import subprocess
import unittest
from unittest.mock import patch

import test_categories_adapter as fixtures
from tools.puzzle_production import content_registry as registry, integrated_content
from tools.puzzle_production.contract import InvalidInput, load_json, write_json


class IntegratedContentTests(unittest.TestCase):
    setUp = fixtures.CategorizedAdapterTests.setUp
    snapshot = fixtures.CategorizedAdapterTests.snapshot
    export = fixtures.CategorizedAdapterTests.export

    def prepare(self):
        out = self.export()
        rated_registration(out, self.checkout, apply=True)
        index = self.checkout / "content/authoring/index.json"
        index.parent.mkdir(parents=True)
        write_json(index, {"format": "picross-authoring-index-v1", "entries": []})
        def git(*args):
            return subprocess.check_output(["git", *args], cwd=self.checkout).decode().strip()
        git("init", "-q")
        git("add", ".")
        git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "integrated fixture")
        commit = git("rev-parse", "HEAD")
        git("update-ref", "refs/remotes/origin/main", commit)
        return out, commit


    def test_lifecycle(self):
        out, commit = self.prepare()
        before = self.snapshot(self.checkout / "game")
        integrated_content.retire(self.checkout, ["pz-test-direct-mono"], commit)
        self.assertEqual(before, self.snapshot(self.checkout / "game"))
        with patch("tools.puzzle_production.target_adapter.verify_export", side_effect=AssertionError("replay")):
            registry.check_checkout(self.checkout, replay=True)
            registry.sync_runtime(self.checkout)
        self.assertEqual(rated_registration(out, self.checkout, apply=True)["status"], "no-op")
        color = self.export("color", "direct-color", "voegel")
        self.assertEqual(rated_registration(color, self.checkout, apply=True)["status"], "registered")


    def test_unmerged_bytes_block_before_deletion(self):
        _, commit = self.prepare()
        entry = load_json(self.checkout / registry.REGISTRY)["entries"][0]
        package = self.checkout / entry["production"]["package"]
        (package / "unmerged.txt").write_text("new work")
        before = self.snapshot(self.checkout)
        with self.assertRaises(InvalidInput):
            integrated_content.retire(self.checkout, [entry["id"]], commit)
        self.assertEqual(before, self.snapshot(self.checkout))

    def test_deleted_input_blocks_before_deletion(self):
        _, commit = self.prepare()
        entry = load_json(self.checkout / registry.REGISTRY)["entries"][0]
        package = self.checkout / entry["production"]["package"]
        next(p for p in package.rglob("*") if p.is_file() and p.name != "manifest.json").unlink()
        before = self.snapshot(self.checkout)
        with self.assertRaises(InvalidInput):
            integrated_content.retire(self.checkout, [entry["id"]], commit)
        self.assertEqual(before, self.snapshot(self.checkout))

    def test_staged_work_blocks_even_if_worktree_matches_main(self):
        _, commit = self.prepare()
        path = self.checkout / registry.REGISTRY
        original = path.read_bytes()
        path.write_bytes(original + b"\n")
        subprocess.check_call(["git", "add", registry.REGISTRY], cwd=self.checkout)
        path.write_bytes(original)
        before = self.snapshot(self.checkout)
        with self.assertRaises(InvalidInput):
            integrated_content.retire(self.checkout, ["pz-test-direct-mono"], commit)
        self.assertEqual(before, self.snapshot(self.checkout))


    def test_receipt_runtime_notice_and_metadata_tampering(self):
        _, commit = self.prepare()
        integrated_content.retire(self.checkout, ["pz-test-direct-mono"], commit)
        entry = load_json(self.checkout / registry.REGISTRY)["entries"][0]
        path = self.checkout / entry["production"]["package"] / "manifest.json"
        receipt = load_json(path)
        for key in ("category_id", "save_slot", "definition", "reveal"):
            altered = deepcopy(receipt)
            altered["entry"][key] = "changed"
            with self.subTest(key=key), self.assertRaises(InvalidInput):
                integrated_content.check(self.checkout, entry, altered)
        for file in (self.checkout/"game"/entry["definition"],
                     (self.checkout/"game"/entry["reveal"]).with_suffix(".txt"), path):
            original = file.read_bytes()
            file.write_bytes(original+b"changed")
            with self.assertRaises(InvalidInput):
                registry.check_checkout(self.checkout, replay=True)
            file.write_bytes(original)
