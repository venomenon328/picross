"""HP-I1c: real synthetic exports, AT approvals, image work and common readers."""
from copy import deepcopy
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tests.puzzle_production.background_catalog_fixtures import prepare
from tests.puzzle_production.background_change_fixtures import create_work
from tests.puzzle_production import test_background_consumers as consumers, test_background_retirement as retirement
from tests.puzzle_production.test_background_consumers import snapshot
from tools.puzzle_production import catalog_background as bg, background_rebind as binding
from tools.puzzle_production import catalog_background_change as change, catalog_reveal as reveal
from tools.puzzle_production import content_registry as registry, content_update, reveal_source as at
from tools.puzzle_production import catalog_io as io, catalog_transaction as tx, catalog_publication as publication
from tools.puzzle_production import integrated_content, background_retirement, target_adapter as adapter
from tools.puzzle_production import catalog_analysis as analysis, catalog_added_history as dates, catalog_method as method
from tools.puzzle_production.contract import InvalidInput, load_json, write_json
from tools.puzzle_production.za1_fixtures import ROOT, make, seal, approve, rated_registration, difficulty_for_export


class BackgroundRebindTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        owner = unittest.TestCase()
        cls.addClassCleanup(owner.doCleanups)
        cls.fixtures = {choice: prepare(owner, choice, registered=True) for choice in ("selected", "none")}

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="hp-i1c-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.checkout = self.root / "checkout"

    def start(self, choice="selected"):
        fixture = self.fixtures[choice]
        shutil.copytree(fixture.checkout, self.checkout)
        self.identifier = fixture.manifest["definition_id"]
        self.fixture = fixture
        return fixture

    def entries(self):
        return {e["id"]: e for e in registry.check_checkout(self.checkout)["entries"]}

    def source(self):
        return bg.load(self.checkout, load_json(self.checkout / registry.REGISTRY), self.entries()[self.identifier])

    def request(self, tag="reveal"):
        return consumers.BackgroundConsumerTests.request(self, self.identifier, tag)[0]

    def git(self, *args):
        return retirement.BackgroundRetirementTests.git(self, *args)

    def commit(self):
        if not (self.checkout / ".git").exists(): self.git("init", "--quiet")
        return retirement.BackgroundRetirementTests.commit_main(self)

    def retire(self):
        index = self.checkout / integrated_content.INDEX
        if not index.exists(): write_json(index, {"format": "picross-authoring-index-v1", "entries": []})
        commit = self.commit()
        return integrated_content.retire(self.checkout, [self.identifier], commit)

    def background(self, choice, revision="bg-new"):
        work = create_work(self, self.checkout, self.root, revision, choice)
        plan = self.root / (revision + "-plan")
        change.plan(self.checkout, work.record_path, plan)
        change.adopt(self.checkout, plan)
        return work, plan

    def export_update(self, revision=8, *, category_id=None):
        entry = self.entries()[self.identifier]
        package = make(self.root / ("input-" + str(revision)), self.identifier, 3, 3, "mono")
        h = load_json(package / "handoff.json")
        h["revision"] = "r" + str(revision)
        (package / "rulebook.md").write_text(
            "**Version 0.6.0 · Dokumentrevision 1 · TEST ONLY**\nSynthetic unchanged legacy-contract fixture.\n",
            encoding="utf-8")
        h["rulebook"] = {"version": "0.6.0", "file": "rulebook.md", "sha256": io.file_hash(package, "rulebook.md")}
        # A new, explicitly approved test package consumes the actual active reveal.
        image = (self.checkout / ("game/" + entry["reveal"])).read_bytes()
        (package / "reveals/reveal.png").write_bytes(image)
        h["reveal"]["sha256"] = io.checksum(image)
        h["motif"]["derived_from_reveal_sha256"] = io.checksum(image)
        for name in ("reveal-approval.json", "motif-approval.json", "reveals/reveal.provenance.json", "motifs/source.provenance.json"):
            record = load_json(package / name)
            if "reveal" in name: record["sha256"] = io.checksum(image)
            if "derived_from_reveal_sha256" in record: record["derived_from_reveal_sha256"] = io.checksum(image)
            if "derived_from" in record: record["derived_from"]["sha256"] = io.checksum(image)
            write_json(package / name, record)
        seal(package, h)
        approval = self.root / ("approval-" + str(revision) + ".json")
        approve(package, approval)
        exported = self.root / ("export-" + str(revision))
        adapter.export(package, exported, name="TEST ONLY", revision=revision, stem="background_test",
                       save_slot=entry["save_slot"], approval_path=approval, category_id=category_id or entry["category_id"],
                       categories_path=self.checkout / "content/categories.json")
        self.assertEqual(load_json(exported / "manifest.json")["format"], "picross-target-export-v5")
        return exported

    def update(self, exported):
        entry = self.entries()[self.identifier]
        return content_update.update(exported, self.checkout, entry["production"]["definition_sha256"],
                                     apply=True, rebind_difficulty=True)

    def export_v6(self, choice, tag):
        fixture = self.fixtures[choice]
        source = self.root / (tag + "-input")
        shutil.copytree(fixture.source, source)
        h = load_json(source / "handoff.json"); h["revision"] = "r08"
        seal(source, h)
        case = fixture.case.case
        archive = case.archive(source, tag + ".zip")
        approval = case.approval(source, archive, name=tag + "-approval.json")
        exported = self.root / (tag + "-export")
        options = {**fixture.case.options, "revision": 8}
        adapter.export(archive, exported, approval_path=approval, allow_background=True, **options)
        return exported

    def test_v6_update_preserves_exact_choice_and_rejects_combined_change(self):
        self.start()
        rejected = self.export_v6("none", "v6-other")
        before = snapshot(self.checkout)
        with self.assertRaisesRegex(InvalidInput, "changes active background"):
            self.update(rejected)
        self.assertEqual(before, snapshot(self.checkout))
        exported = self.export_v6("selected", "v6-same")
        self.assertEqual(self.update(exported)["status"], "updated")
        self.assertIsNotNone(self.source()["events"][-1]["export_source"])
        before = snapshot(self.checkout)
        self.assertEqual(self.update(exported)["status"], "no-op")
        self.assertEqual(before, snapshot(self.checkout))
        self.retire()
        registry.check_checkout(self.checkout, replay=True)
        # These independent consumers must bind v3 without replacing its image authority.
        protected = (self.checkout / bg.path(self.identifier)).read_bytes()
        commit = self.commit()
        report = self.root / "v3-rating"
        analysis.preview(self.checkout, report, "v3-rating", commit, ids=[self.identifier],
                         checked_inputs={self.identifier: difficulty_for_export(exported)})
        analysis.adopt(self.checkout, report, apply=True)
        added_plan = self.root / "v3-added.json"
        write_json(added_plan, dates.plan(self.checkout, "v3-added", commit))
        dates.adopt(self.checkout, added_plan, apply=True)
        activation = method.plan(self.checkout, method.OLD, method.NEW, method.method_hash(method.NEW))
        method.adopt(self.checkout, activation)
        self.assertEqual((self.checkout / bg.path(self.identifier)).read_bytes(), protected)
        registry.check_checkout(self.checkout)

    def test_explicit_none_v1_and_v2_allow_both_rebind_operations(self):
        for changed in (False, True):
            with self.subTest(source="v2" if changed else "v1"):
                self.checkout = self.root / ("checkout-" + str(changed))
                self.start("selected" if changed else "none")
                if changed: self.background("none", "bg-none")
                else: self.retire()
                previous = self.source()
                exported = self.export_update(9 if changed else 8)
                self.update(exported)
                plan = self.root / ("none-reveal-" + str(changed))
                reveal.plan(self.checkout, [self.identifier], self.request("none-" + str(changed)), plan)
                reveal.adopt(self.checkout, plan / "plan.json")
                self.assertEqual(self.source()["base"], previous)
                self.assertEqual(bg.current(self.source())["decision"]["outcome"], "none")
                self.assertFalse((self.checkout / bg.asset_path(self.identifier)).exists())
                registry.check_checkout(self.checkout, replay=True)

    def test_selected_raster_reveal_background_order_and_noops(self):
        self.start()
        initial = self.source()
        exported = self.export_update()
        self.assertEqual(self.update(exported)["status"], "updated")
        self.assertEqual(bg.current(self.source()), initial)
        plan = self.root / "reveal-plan"
        reveal.plan(self.checkout, [self.identifier], self.request(), plan)
        self.assertEqual(load_json(plan / "plan.json")["format"], reveal.REBIND_FORMAT)
        reveal.adopt(self.checkout, plan / "plan.json")
        after = snapshot(self.checkout)
        self.assertEqual(reveal.adopt(self.checkout, plan / "plan.json")["status"], "no-op")
        self.assertEqual(after, snapshot(self.checkout))
        self.assertEqual(bg.initial(self.source()), initial)
        self.background("none")
        source = self.source()
        self.assertEqual([e["operation"] for e in source["events"]], ["update", "reveal-adoption", "background-adoption"])
        self.assertEqual(bg.current(source)["decision"]["outcome"], "none")
        with self.assertRaises(InvalidInput): reveal.adopt(self.checkout, plan / "plan.json")
        before = snapshot(self.checkout)
        self.assertEqual(rated_registration(self.fixture.export, self.checkout, apply=True)["status"], "no-op")
        self.assertEqual(before, snapshot(self.checkout))
        registry.check_checkout(self.checkout, replay=True)
        registry.sync_runtime(self.checkout)
        self.assertEqual(before, snapshot(self.checkout))

    def test_none_receipt_background_reveal_raster_and_retirement(self):
        self.start("none")
        self.retire()
        original_manifest = self.entries()[self.identifier]["production"]["package"] + "/manifest.json"
        original_receipt = (self.checkout / original_manifest).read_bytes()
        self.background("selected", "bg-first")
        base = self.source()
        plan = self.root / "reveal-plan"
        reveal.plan(self.checkout, [self.identifier], self.request(), plan)
        reveal.adopt(self.checkout, plan / "plan.json")
        self.update(self.export_update())
        self.assertEqual(self.source()["base"], base)
        self.assertEqual(bg.current(self.source()), bg.current(base))
        self.assertEqual((self.checkout / original_manifest).read_bytes(), original_receipt)
        work, _ = self.background("none", "bg-after")
        commit = self.commit()
        self.assertEqual(background_retirement.retire(self.checkout, [(self.identifier, "bg-after")], commit)["status"],
                         "background_production_retired")
        registry.check_checkout(self.checkout)
        self.retire()
        registry.check_checkout(self.checkout, replay=True)
        self.assertEqual((self.checkout / original_manifest).read_bytes(), original_receipt)

    def test_current_metadata_survives_category_changing_source_v4_and_retirement(self):
        from tools.puzzle_production import catalog_metadata as metadata
        self.start()
        self.update(self.export_update())
        historical = self.source()
        self.assertEqual(historical["format"], binding.FORMAT)
        metadata.apply(self.checkout, metadata.plan(self.checkout, [
            {"op": "set_metadata", "id": self.identifier, "name": "Aktuelles Motiv"},
            {"op": "category_delete", "id": "voegel", "reassign_to": "wasserwelt"},
        ]))
        active = deepcopy(load_json(self.checkout / registry.REGISTRY)["metadata"])
        exported = self.export_update(9, category_id="obst-nuesse")
        self.update(exported)
        source = self.source()
        self.assertEqual(source["format"], binding.METADATA_FORMAT)
        self.assertEqual(source["base"], historical["base"])
        self.assertEqual(source["entry"], historical["entry"])
        self.assertEqual(source["events"][:-1], historical["events"])
        self.assertEqual(source["events"][-1]["binding"]["entry"]["category_id"], "obst-nuesse")
        self.assertEqual(bg.current(source), bg.current(historical))
        # A v3 label cannot silently acquire the new historical-category rule.
        downgraded = deepcopy(source); downgraded["format"] = binding.FORMAT
        with self.assertRaises(InvalidInput): bg.validate(downgraded, self.entries()[self.identifier])
        plan = self.root / "metadata-reveal"
        reveal.plan(self.checkout, [self.identifier], self.request("metadata"), plan)
        reveal.adopt(self.checkout, plan / "plan.json")
        self.background("none", "bg-metadata")
        commit = self.commit()
        background_retirement.retire(self.checkout, [(self.identifier, "bg-metadata")], commit)
        self.retire()
        registry.check_checkout(self.checkout, replay=True)
        self.assertEqual(load_json(self.checkout / registry.REGISTRY)["metadata"], active)
        runtime = load_json(self.checkout / registry.RUNTIME)["entries"][0]
        self.assertEqual((runtime["name"], runtime["category_id"]), ("Aktuelles Motiv", "wasserwelt"))
        before = snapshot(self.checkout)
        self.assertEqual(rated_registration(self.fixture.export, self.checkout, apply=True)["status"], "no-op")
        registry.sync_runtime(self.checkout)
        self.assertEqual(snapshot(self.checkout), before)

    def test_reveal_journal_rollback_foreign_bytes_and_old_scope(self):
        self.start()
        request = self.request()
        plan = self.root / "plan"
        reveal.plan(self.checkout, [self.identifier], request, plan)
        before = snapshot(self.checkout)
        script = """import os, sys
from pathlib import Path
from tools.puzzle_production import catalog_publication as p, catalog_reveal as r
def stop(phase, name=None):
    if phase == 'P4': os._exit(77)
p.checkpoint = stop
r.adopt(Path(sys.argv[1]), Path(sys.argv[2]))
"""
        process = subprocess.run([sys.executable, "-c", script, str(self.checkout), str(plan / "plan.json")],
                                 cwd=ROOT, capture_output=True, timeout=300)
        self.assertEqual(process.returncode, 77, process.stderr.decode(errors="replace"))
        self.assertTrue((self.checkout / tx.LOCK).exists())
        journal = io.json_bytes(publication.read_journal(self.checkout), publication.LIMIT)
        self.assertEqual(journal["format"], tx.PE_FORMATS["reveal-adoption"])
        downgraded = deepcopy(journal); downgraded["format"] = tx.BACKGROUND_FORMATS["reveal-adoption"]
        with self.assertRaises(InvalidInput): tx.validate_journal(self.checkout, downgraded)
        name = bg.notice_path(self.identifier)
        actual = (self.checkout / name).read_bytes()
        (self.checkout / name).write_bytes(actual + b"foreign")
        conflict = snapshot(self.checkout)
        with self.assertRaises(InvalidInput): registry.recover(self.checkout)
        self.assertEqual(conflict, snapshot(self.checkout))
        (self.checkout / name).write_bytes(actual)
        def stop_recovery(phase, name=None):
            if phase == "R1-binary": raise InterruptedError("synthetic recovery interruption")
        with patch.object(publication, "checkpoint", side_effect=stop_recovery), self.assertRaises(InterruptedError):
            registry.recover(self.checkout)
        registry.recover(self.checkout)
        self.assertFalse((self.checkout / tx.LOCK).exists())
        self.assertEqual({n: v[0] for n, v in before.items()}, {n: v[0] for n, v in snapshot(self.checkout).items()})
        after = snapshot(self.checkout)
        with self.assertRaises(InvalidInput): registry.recover(self.checkout)
        self.assertEqual(after, snapshot(self.checkout))

    def test_rehashed_source_history_and_mixed_mutation_are_rejected(self):
        with self.assertRaisesRegex(InvalidInput, "registry generation"):
            binding.delta({}, {"format": registry.FORMAT, "entries": []},
                          {"format": registry.BACKGROUND_FORMAT, "entries": [], "backgrounds": []}, [])
        self.start("none")
        self.update(self.export_update())
        source = self.source()
        entry = self.entries()[self.identifier]
        with self.assertRaisesRegex(InvalidInput, "cannot downgrade"):
            bg._transition(source, source["base"])
        for mutate in (
            lambda v: v["events"][0]["binding"]["identity"].update(runtime_revision=True),
            lambda v: v["events"][0]["binding"]["reveal"].update(sha256="0" * 64),
            lambda v: v["events"][0]["binding"]["entry"]["production"].update(revision="other"),
            lambda v: v["events"][0].update(image=deepcopy(bg.current(v))),
            lambda v: v["events"][0]["previous_source"].update(sha256="0" * 64),
        ):
            changed = deepcopy(source); mutate(changed)
            with self.assertRaises(InvalidInput): bg.validate(changed, entry)
        before = snapshot(self.checkout)
        request = self.request()
        value = load_json(request); value["entries"][0]["approval"]["previous_reveal_sha256"] = "0" * 64
        write_json(request, value)
        with self.assertRaises(InvalidInput):
            reveal.plan(self.checkout, [self.identifier], request, self.root / "invalid-plan")
        self.assertEqual(before, snapshot(self.checkout))

    def test_update_journal_recovery_and_rebind_stale_saved_plans(self):
        self.start()
        request = self.request()
        plan = self.root / "old-reveal-plan"
        reveal.plan(self.checkout, [self.identifier], request, plan)
        work = create_work(self, self.checkout, self.root, "stale-bg", "none")
        background_plan = self.root / "old-background-plan"
        change.plan(self.checkout, work.record_path, background_plan)
        exported = self.export_update()
        entry = self.entries()[self.identifier]
        before = snapshot(self.checkout)
        with self.assertRaises(InterruptedError):
            content_update.update(exported, self.checkout, entry["production"]["definition_sha256"],
                                  apply=True, rebind_difficulty=True, fail_step="crash-runtime")
        journal = io.json_bytes(publication.read_journal(self.checkout), publication.LIMIT)
        self.assertEqual(journal["format"], tx.PE_FORMATS["update"])
        downgraded = deepcopy(journal); downgraded["format"] = tx.BACKGROUND_FORMATS["update"]
        with self.assertRaises(InvalidInput): tx.validate_journal(self.checkout, downgraded)
        result = subprocess.run([sys.executable, "-m", "tools.puzzle_production.target_adapter",
            "recover-registration", "--checkout", str(self.checkout)], cwd=ROOT, capture_output=True, timeout=300)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        self.assertEqual({n: v[0] for n, v in before.items()}, {n: v[0] for n, v in snapshot(self.checkout).items()})
        self.update(exported)
        after = snapshot(self.checkout)
        for action in (lambda: reveal.adopt(self.checkout, plan / "plan.json"),
                       lambda: change.adopt(self.checkout, background_plan)):
            with self.assertRaises(InvalidInput): action()
            self.assertEqual(after, snapshot(self.checkout))

    def test_reveal_plan_rechecked_under_lock_and_receipt_stales_noop(self):
        self.start()
        plan = self.root / "plan"
        reveal.plan(self.checkout, [self.identifier], self.request(), plan)
        before = snapshot(self.checkout)
        original = (plan / "plan.json").read_bytes()
        def changed(phase, name=None):
            if phase == "P1": (plan / "plan.json").write_bytes(original + b" ")
        with patch.object(publication, "checkpoint", side_effect=changed), self.assertRaises(InvalidInput):
            reveal.adopt(self.checkout, plan / "plan.json")
        self.assertEqual(before, snapshot(self.checkout))
        (plan / "plan.json").write_bytes(original)
        reveal.adopt(self.checkout, plan / "plan.json")
        self.retire()
        after = snapshot(self.checkout)
        with self.assertRaises(InvalidInput): reveal.adopt(self.checkout, plan / "plan.json")
        self.assertEqual(after, snapshot(self.checkout))


if __name__ == "__main__": unittest.main()
