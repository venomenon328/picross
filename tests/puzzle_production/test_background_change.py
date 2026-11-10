"""HP-I1b2 real work/plan/adoption boundaries and compact transition sequence."""
from copy import deepcopy
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tests.puzzle_production.background_catalog_fixtures import prepare
from tests.puzzle_production.background_change_fixtures import create_work
from tests.puzzle_production.background_fixtures import pixels
from tools.puzzle_production import background_request as requests, catalog_background as bg
from tools.puzzle_production import catalog_background_change as change, catalog_transaction as tx
from tools.puzzle_production import catalog_publication as publication, content_registry as cr
from tools.puzzle_production import integrated_content as integrated, authoring_builder as builder
from tools.puzzle_production.contract import InvalidInput, load_json, write_json, digest


def snapshot(root):
    return {p.relative_to(root).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
            for p in root.rglob("*") if p.is_file() and ".git" not in p.relative_to(root).parts}


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), "-c", "user.name=Synthetic background test",
        "-c", "user.email=test@example.invalid", "-c", "commit.gpgsign=false", *args], stderr=subprocess.PIPE, text=True).strip()


class BackgroundChangeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        owner = unittest.TestCase()
        cls.addClassCleanup(owner.doCleanups)
        cls.bases = {}
        for choice in ("selected", "none"):
            f = prepare(owner, choice, registered=True)
            write_json(f.checkout / requests.INDEX, {"format": "picross-authoring-index-v1", "entries": []})
            git(f.checkout, "init", "-q")
            git(f.checkout, "add", ".")
            git(f.checkout, "commit", "-qm", "Synthetic first integration")
            commit = git(f.checkout, "rev-parse", "HEAD")
            git(f.checkout, "update-ref", "refs/remotes/origin/main", commit)
            identifier = load_json(f.checkout / cr.REGISTRY)["entries"][0]["id"]
            integrated.retire(f.checkout, [identifier], commit)
            cls.bases[choice] = f.checkout

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="hp-i1b2-change-")
        self.addCleanup(temporary.cleanup)
        self.work = Path(temporary.name)
        self.checkout = self.work / "checkout"

    def start(self, choice="selected"):
        shutil.copytree(self.bases[choice], self.checkout, ignore=shutil.ignore_patterns(".git"))
        self.entry = load_json(self.checkout / cr.REGISTRY)["entries"][0]
        self.identifier = self.entry["id"]

    def working(self, revision="bg-r01", choice="selected", **kwargs):
        return create_work(self, self.checkout, self.work, revision, choice, **kwargs)

    def planned(self, working, name="plan"):
        path = self.work / name
        before = snapshot(self.checkout)
        self.assertEqual(change.plan(self.checkout, working.record_path, path)["status"], "planned")
        self.assertEqual(snapshot(self.checkout), before)
        return path

    def active(self):
        return {name: value for name, value in snapshot(self.checkout).items() if not name.startswith("content/authoring/")}

    def test_selected_none_selected_and_further_revision_keep_identity_receipt_and_exact_noop(self):
        self.start()
        initial = load_json(self.checkout / bg.path(self.identifier))
        preserved_names = {"game/" + self.entry["definition"], "game/" + self.entry["reveal"],
            "content/difficulty/" + self.identifier + "/rating.json", "content/added/" + self.identifier + ".json",
            self.entry["production"]["package"] + "/manifest.json"}
        original = snapshot(self.checkout)
        plans = []
        for number, choice in enumerate(("selected", "none", "selected", "selected"), 1):
            work = self.working("bg-r0" + str(number), choice)
            plan = self.planned(work, "plan" + str(number))
            plans.append(plan)
            before = snapshot(self.checkout)
            if number == 4:
                self.assertEqual(load_json(plan / "plan.json")["old"][bg.notice_path(self.identifier)],
                                 load_json(plan / "plan.json")["new"][bg.notice_path(self.identifier)])
            self.assertEqual(change.adopt(self.checkout, plan)["status"], "adopted")
            active = load_json(self.checkout / bg.path(self.identifier))
            self.assertEqual(active["initial"], initial)
            self.assertEqual(bg.current(active)["image_revision"], number + 1)
            self.assertEqual(bg.current(active)["decision"]["outcome"], choice)
            self.assertEqual(load_json(self.checkout / cr.REGISTRY)["entries"][0], self.entry)
            after = snapshot(self.checkout)
            self.assertEqual({n: after[n] for n in preserved_names}, {n: original[n] for n in preserved_names})
            self.assertEqual({n: v for n, v in before.items() if n.startswith("content/authoring/")},
                             {n: v for n, v in after.items() if n.startswith("content/authoring/")})
            if number == 4: self.assertEqual(after[bg.asset_path(self.identifier)], before[bg.asset_path(self.identifier)])
            self.assertEqual(change.adopt(self.checkout, plan)["status"], "no-op")
            self.assertEqual(snapshot(self.checkout), after)
            cr.check_checkout(self.checkout, replay=True)
        before = snapshot(self.checkout)
        with self.assertRaisesRegex(InvalidInput, "Stale"):
            change.adopt(self.checkout, plans[0])
        self.assertEqual(snapshot(self.checkout), before)

    def test_none_to_selected_and_none_to_none_rejection(self):
        self.start("none")
        none = self.working("empty", "none")
        before = snapshot(self.checkout)
        with self.assertRaisesRegex(InvalidInput, "none"):
            change.plan(self.checkout, none.record_path, self.work / "empty-plan")
        self.assertEqual(snapshot(self.checkout), before)
        selected = self.working("chosen")
        plan = self.planned(selected)
        self.assertNotIn("previous/background.png", {r["file"] for r in load_json(plan / "plan.json")["files"]})
        self.assertEqual(change.adopt(self.checkout, plan)["status"], "adopted")
        self.assertEqual(bg.current(load_json(self.checkout / bg.path(self.identifier)))["image_revision"], 2)

    def test_closed_work_record_inventory_roots_and_types(self):
        self.start()
        work = self.working()
        variants = []
        def alter(path, value):
            request = deepcopy(work.request); obj = request
            for key in path[:-1]: obj = obj[key]
            obj[path[-1]] = value; variants.append(request)
        alter(("format",), "picross-authoring-record-v2")
        alter(("unexpected",), True)
        alter(("target", "image_revision"), True)
        alter(("test_only",), 1)
        alter(("target", "source", "file"), "content/backgrounds/pz-other.json")
        alter(("background", "manifest", "storage"), "package")
        alter(("background", "decision", "root"), "content/authoring/pz-other/bg-r01")
        alter(("background", "derivation"), None)
        alter(("authorization", "timestamp_utc"), "not-a-time")
        alter(("authorization", "evidence"), {"file": "missing.txt", "sha256": "0" * 64, "bytes": 3})
        alter(("files",), list(reversed(work.request["files"])))
        alter(("files",), work.request["files"] + [work.request["files"][-1]])
        for request in variants:
            with self.subTest(request=request), self.assertRaises((ValueError, InvalidInput)):
                requests.validate(request)
        with self.assertRaisesRegex(InvalidInput, "Unsupported authoring record family"):
            builder.sheet_from_record(work.request)

    def test_work_extra_file_alias_missing_authorization_and_stale_index_are_rejected(self):
        self.start()
        work = self.working()
        directory = self.checkout / requests.directory(work.request)
        extra = directory / "foreign.txt"
        extra.write_bytes(b"foreign")
        before = snapshot(self.checkout)
        with self.assertRaisesRegex(InvalidInput, "inventory"):
            change.plan(self.checkout, work.record_path, self.work / "extra-plan")
        self.assertEqual(snapshot(self.checkout), before)
        extra.unlink()
        evidence = directory / work.request["authorization"]["evidence"]["file"]
        evidence.unlink()
        with self.assertRaises(InvalidInput): change.plan(self.checkout, work.record_path, self.work / "missing-plan")
        evidence.write_bytes(work.payload[work.request["authorization"]["evidence"]["file"]])
        index = load_json(self.checkout / requests.INDEX)
        write_json(self.checkout / requests.INDEX, {**index, "entries": []})
        with self.assertRaisesRegex(InvalidInput, "index"):
            change.plan(self.checkout, work.record_path, self.work / "index-plan")
        write_json(self.checkout / requests.INDEX, index)
        linked = directory / "evidence/alias.txt"
        os.link(evidence, linked)
        with self.assertRaisesRegex(InvalidInput, "hardlink"):
            change.plan(self.checkout, work.record_path, self.work / "alias-plan")

    def test_plan_hash_does_not_authorize_forged_text_or_incomplete_bundle(self):
        self.start()
        work = self.working()
        plan = self.planned(work)
        value = load_json(plan / "plan.json")
        forged = deepcopy(value)
        definition = "game/" + self.entry["definition"]
        forged["new"][definition] += "\n"
        forged["plan_hash"] = digest({k: v for k, v in forged.items() if k != "plan_hash"})
        write_json(plan / "plan.json", forged)
        before = snapshot(self.checkout)
        with self.assertRaises(InvalidInput): change.adopt(self.checkout, plan)
        self.assertEqual(snapshot(self.checkout), before)
        write_json(plan / "plan.json", value)
        for malformed in ([], 7, {"current": None}):
            for rehash_index in (False, True):
                forged = deepcopy(value)
                name = bg.path(self.identifier)
                forged["old"][name] = json.dumps(malformed)
                if rehash_index:
                    # A matching index hash still cannot authorize malformed source data.
                    catalog = json.loads(forged["old"][tx.REGISTRY])
                    row = next(r for r in catalog["backgrounds"] if r["id"] == self.identifier)
                    row["source"] = bg.ref(name, forged["old"][name].encode())
                    forged["old"][tx.REGISTRY] = bg.encoded(catalog).decode()
                forged["plan_hash"] = digest({k: v for k, v in forged.items() if k != "plan_hash"})
                write_json(plan / "plan.json", forged)
                with self.subTest(malformed=malformed, rehash_index=rehash_index), self.assertRaises(InvalidInput):
                    change.adopt(self.checkout, plan)
                self.assertEqual(snapshot(self.checkout), before)
        write_json(plan / "plan.json", value)
        candidate = plan / "input" / requests.directory(work.request) / "original/B-b01.png"
        candidate.unlink()
        with self.assertRaisesRegex(InvalidInput, "inventory"):
            change.adopt(self.checkout, plan)
        self.assertEqual(snapshot(self.checkout), before)

    def test_capability_missing_false_invalid_and_changed_plan_stop_before_mutation(self):
        self.start()
        work = self.working()
        plan = self.planned(work)
        path = self.checkout / bg.CAPABILITY
        original = path.read_bytes()
        for value in (None, {**load_json(path), "enabled": False}, {**load_json(path), "enabled": 1}):
            if value is None: path.unlink()
            else: write_json(path, value)
            before = snapshot(self.checkout)
            with self.subTest(value=value), self.assertRaises((InvalidInput, ValueError)):
                change.adopt(self.checkout, plan)
            self.assertEqual(snapshot(self.checkout), before)
            path.write_bytes(original)
        path.write_bytes(original + b"\n")
        before = snapshot(self.checkout)
        with self.assertRaises(InvalidInput): change.adopt(self.checkout, plan)
        self.assertEqual(snapshot(self.checkout), before)

    def test_changed_work_after_lock_is_detected_before_active_mutation(self):
        self.start()
        work = self.working()
        plan = self.planned(work)
        before = self.active()
        changed = self.checkout / requests.directory(work.request) / "evidence/decision.txt"
        observed = []
        def race(phase, name=None):
            if phase == "P1":
                self.assertTrue((self.checkout / tx.LOCK).exists())
                changed.write_bytes(b"TEST ONLY competing changed work")
                observed.append(phase)
            if phase == "P3": self.fail("Active binary was mutated before work recheck")
        with patch.object(publication, "checkpoint", side_effect=race):
            with self.assertRaisesRegex(InvalidInput, "Background work file binding changed"):
                change.adopt(self.checkout, plan)
        self.assertEqual(observed, ["P1"])
        self.assertEqual(self.active(), before)
        self.assertEqual(changed.read_bytes(), b"TEST ONLY competing changed work")
        self.assertFalse((self.checkout / tx.LOCK).exists())

    def test_missing_work_cannot_publish_and_noop_after_removal_requires_main_proof(self):
        self.start()
        work = self.working()
        plan = self.planned(work)
        directory = self.checkout / requests.directory(work.request)
        shutil.rmtree(directory)
        write_json(self.checkout / requests.INDEX, {"format": "picross-authoring-index-v1", "entries": []})
        before = snapshot(self.checkout)
        with self.assertRaisesRegex(InvalidInput, "Main proof"):
            change.adopt(self.checkout, plan, integrated_commit="0" * 40)
        self.assertEqual(snapshot(self.checkout), before)
        shutil.copytree(work.source_root, directory)
        write_json(self.checkout / requests.INDEX, {"format": "picross-authoring-index-v1", "entries": [requests.index_row(work.request)]})
        change.adopt(self.checkout, plan)
        shutil.rmtree(directory)
        write_json(self.checkout / requests.INDEX, {"format": "picross-authoring-index-v1", "entries": []})
        before = snapshot(self.checkout)
        with self.assertRaisesRegex(InvalidInput, "Main proof"):
            change.adopt(self.checkout, plan)
        self.assertEqual(snapshot(self.checkout), before)

    def test_store_explicit_immutable_family_noop_and_conflict_preserve_other_rows(self):
        self.start()
        git(self.checkout, "init", "-q")
        work = self.working(install=False)
        sibling = {"puzzle_id": "pz-other", "revision": "open", "record": "content/authoring/pz-other/open/record.json"}
        write_json(self.checkout / requests.INDEX, {"format": "picross-authoring-index-v1", "entries": [sibling]})
        before = self.active()
        self.assertEqual(change.store(self.checkout, work.source_root / "record.json", work.source_root)["status"], "stored")
        self.assertEqual(self.active(), before)
        self.assertEqual(load_json(self.checkout / requests.INDEX)["entries"], [sibling, requests.index_row(work.request)])
        stored = snapshot(self.checkout)
        self.assertEqual(change.store(self.checkout, work.source_root / "record.json", work.source_root)["status"], "no-op")
        self.assertEqual(snapshot(self.checkout), stored)
        plan = self.planned(work)
        change.adopt(self.checkout, plan)
        stored = snapshot(self.checkout)
        self.assertEqual(change.store(self.checkout, work.source_root / "record.json", work.source_root)["status"], "no-op")
        self.assertEqual(snapshot(self.checkout), stored)
        target = self.checkout / work.record_path
        target.write_bytes(target.read_bytes() + b"\n")
        before = snapshot(self.checkout)
        with self.assertRaises(InvalidInput):
            change.store(self.checkout, work.source_root / "record.json", work.source_root)
        self.assertEqual(snapshot(self.checkout), before)

    def test_published_plan_fsync_failure_reports_actual_owned_remaining_path(self):
        self.start()
        work = self.working()
        output = self.work / "published-plan"
        before = snapshot(self.checkout)
        real_sync = publication.sync_directory
        def fail_parent(path):
            if path == output.parent and output.exists(): raise OSError("Synthetic post-publication fsync failure")
            return real_sync(path)
        with patch.object(publication, "sync_directory", side_effect=fail_parent):
            with self.assertRaises(builder.BuildError) as caught:
                change.plan(self.checkout, work.record_path, output)
        self.assertEqual(caught.exception.remaining, str(output))
        self.assertEqual(caught.exception.code, "io_error")
        self.assertTrue(output.is_dir())
        change.load_plan(output)
        self.assertEqual(snapshot(self.checkout), before)

    def test_published_work_fsync_failure_reports_partial_publication_without_index_row(self):
        self.start()
        git(self.checkout, "init", "-q")
        work = self.working(install=False)
        target = self.checkout / requests.directory(work.request)
        before = self.active()
        index_before = (self.checkout / requests.INDEX).read_bytes()
        real_sync = publication.sync_directory
        def fail_parent(path):
            if path == target.parent and target.exists(): raise OSError("Synthetic post-publication fsync failure")
            return real_sync(path)
        with patch.object(publication, "sync_directory", side_effect=fail_parent):
            with self.assertRaises(builder.BuildError) as caught:
                change.store(self.checkout, work.source_root / "record.json", work.source_root)
        self.assertEqual(caught.exception.remaining, str(target))
        self.assertEqual(caught.exception.code, "io_error")
        self.assertTrue(target.is_dir())
        requests.read(self.checkout, work.record_path, require_index=False)
        self.assertEqual((self.checkout / requests.INDEX).read_bytes(), index_before)
        self.assertEqual(self.active(), before)
        with self.assertRaisesRegex(InvalidInput, "Partial"):
            change.store(self.checkout, work.source_root / "record.json", work.source_root)

    def test_cli_actual_plan_adopt_and_duplicate_option_error(self):
        self.start()
        work = self.working()
        plan = self.work / "cli-plan"
        command = [sys.executable, "-m", "tools.puzzle_production.catalog_background_change"]
        planned = subprocess.run([*command, "plan", "--root", str(self.checkout), "--record", work.record_path,
                                  "--output", str(plan)], capture_output=True, text=True, timeout=300)
        self.assertEqual(planned.returncode, 0, planned.stderr + planned.stdout)
        self.assertEqual(json.loads(planned.stdout)["status"], "planned")
        adopted = subprocess.run([*command, "adopt", "--root", str(self.checkout), "--plan", str(plan)],
                                 capture_output=True, text=True, timeout=300)
        self.assertEqual(adopted.returncode, 0, adopted.stderr + adopted.stdout)
        self.assertEqual(json.loads(adopted.stdout)["status"], "adopted")
        bad = subprocess.run([*command, "adopt", "--root", str(self.checkout), "--root", str(self.checkout), "--plan", str(plan)],
                            capture_output=True, text=True, timeout=30)
        self.assertEqual(bad.returncode, 2)
        self.assertIn("Duplicate option", json.loads(bad.stdout)["error"]["message"])
        invalid_roots = [self.work / "absent-root"]
        if os.name != "nt":
            unsafe = self.work / "symlink-root"
            unsafe.symlink_to(self.checkout, target_is_directory=True)
            invalid_roots.append(unsafe)
        for root in invalid_roots:
            bad = subprocess.run([*command, "adopt", "--root", str(root), "--plan", str(plan)],
                                 capture_output=True, text=True, timeout=30)
            self.assertEqual(bad.returncode, 2, bad.stderr + bad.stdout)
            self.assertEqual(json.loads(bad.stdout)["status"], "invalid_input")
            self.assertEqual(bad.stderr, "")


if __name__ == "__main__": unittest.main()
