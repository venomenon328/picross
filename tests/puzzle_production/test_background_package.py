"""PB-H background packages: synthetic bytes and real HP-W2/history readers."""
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from unittest.mock import patch

from tools.puzzle_production import background_assets as assets
from tools.puzzle_production import background_package as package
from tools.puzzle_production.contract import InvalidInput
from tests.puzzle_production.background_fixtures import BackgroundFixture, file_ref, put, put_json


ROOT = Path(__file__).resolve().parents[2]


def stored(root, ref, storage="package"):
    return {"storage": storage, "root": root, "ref": copy.deepcopy(ref)}


class BackgroundPackageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="pb-h-background-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.counter = 0

    def fixture(self, *, none=False, decision=True, derived=False, ready=False, prefix="background"):
        self.counter += 1
        folder = self.root / str(self.counter)
        fixture = BackgroundFixture(folder / "working", assets.describe(), none=none)
        if ready and not none:
            candidate = fixture.manifest["candidates"][0]
            norm = {"file": "docs/PUZZLE_QUALITY.md", "contract": "1.0", "document_revision": 9,
                    "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                    "sha256": hashlib.sha256((ROOT / "docs/PUZZLE_QUALITY.md").read_bytes()).hexdigest()}
            candidate["review"] = {criterion: {
                "result": "erfüllt", "reason": "TEST ONLY synthetic judgment for package validation.",
                "method": "TEST ONLY fixture construction", "norm": copy.deepcopy(norm),
                "actor": "Synthetic package test", "timestamp_utc": "2026-01-01T12:00:00Z",
                "evidence": [copy.deepcopy(candidate["original"])]}
                for criterion in ("Q-HG01", "Q-HG02", "Q-HG03", "Q-HG04")}
            fixture.refresh()
        target = folder / "package"
        target.mkdir()
        destination = target if prefix == "." else target / prefix
        shutil.copytree(fixture.source, destination, dirs_exist_ok=True)
        binding = {"manifest": stored(prefix, fixture.request["manifest"]),
                   "decision": stored(prefix, fixture.request["decision"]) if decision else None,
                   "derivation": None, "history": None}
        handoff = {"format": "picross-authoring-handoff-v3", "rulebook": {"version": "0.7.0"},
                   "puzzle_id": fixture.manifest["puzzle_id"], "revision": "r01", "test_only": True,
                   "state": "raster_review", "background": binding,
                   "gates": {"background_choice": "pending", "background_asset": "pending"},
                   "gate_evidence": {"background_choice": None, "background_asset": None}}
        if derived:
            result = assets.derive(fixture.request, fixture.source, fixture.output)
            self.assertIn(result["status"], ("derived", "none"), result)
            shutil.copytree(fixture.target, target / "outputs" / "b01")
            binding["derivation"] = stored("outputs", file_ref(target / "outputs", "b01/derivation.json"))
        return fixture, target, handoff

    def sync(self, fixture, target, handoff):
        fixture.refresh()
        prefix = handoff["background"]["manifest"]["root"]
        destination = target if prefix == "." else target / prefix
        shutil.copytree(fixture.source, destination, dirs_exist_ok=True)
        handoff["background"]["manifest"]["ref"] = copy.deepcopy(fixture.request["manifest"])
        if handoff["background"]["decision"] is not None:
            handoff["background"]["decision"]["ref"] = copy.deepcopy(fixture.request["decision"])

    def gates(self, handoff, *, content_ready=False):
        for gate, field in (("background_choice", "decision"), ("background_asset", "derivation")):
            ref = handoff["background"][field]
            if ref is not None:
                handoff["gates"][gate] = "pass"
                handoff["gate_evidence"][gate] = ("" if ref["root"] == "." else ref["root"] + "/") + ref["ref"]["file"]
        if content_ready:
            handoff["state"] = "content_ready"

    def git(self, root, *arguments):
        return subprocess.check_output(["git", "-C", str(root), *arguments], stderr=subprocess.PIPE).strip()

    def history(self, fixture, *, archive=False):
        root = fixture.root.parent / "history"
        root.mkdir()
        self.git(root, "init", "-q")
        self.git(root, "config", "user.name", "Synthetic PB-H test")
        self.git(root, "config", "user.email", "synthetic@example.invalid")
        if archive:
            # This is an original test authoring ZIP, not an embedded payload.
            with zipfile.ZipFile(root / "original.zip", "w") as bundle:
                bundle.writestr("handoff.json", b"{}\n")
                for path in fixture.source.rglob("*"):
                    if path.is_file():
                        bundle.write(path, "background/" + path.relative_to(fixture.source).as_posix())
            history = {"storage": "package", "path": "original.zip", "root": "background"}
        else:
            shutil.copytree(fixture.source, root / "saved")
            history = {"storage": "directory", "path": "saved", "root": "."}
        self.git(root, "add", ".")
        self.git(root, "commit", "-qm", "Synthetic immutable background originals")
        history["commit"] = self.git(root, "rev-parse", "HEAD").decode()
        return root, history

    def test_closed_binding_forms_and_handoff_generation(self):
        _, target, handoff = self.fixture()
        self.assertEqual(package.validate_binding(handoff["background"]), handoff["background"])
        for change in (lambda b: b.update(extra=True),
                       lambda b: b["manifest"].update(root="../outside"),
                       lambda b: b["manifest"]["ref"].update(bytes=True),
                       lambda b: b["manifest"].update(storage="external")):
            value = copy.deepcopy(handoff["background"])
            change(value)
            with self.assertRaises(InvalidInput):
                package.validate_binding(value)
        legacy = {"format": "picross-authoring-handoff-v2", "rulebook": {"version": "0.6.0"}}
        self.assertEqual(package.validate(target, legacy)["status"], "legacy")
        legacy["background"] = handoff["background"]
        with self.assertRaises(InvalidInput):
            package.validate(target, legacy)

    def test_offered_all_three_originals_pending_and_rejected_stay_unready(self):
        fixture, target, handoff = self.fixture(decision=False)
        result = package.validate(target, handoff)
        self.assertEqual(result["status"], "offered")
        self.assertFalse(result["ready"])
        self.assertEqual([x["ID"] for x in result["options"]], ["A", "B", "C"])
        self.assertTrue({"background/original/A-b01.png", "background/original/B-b01.png",
                         "background/original/C-b01.png"} <= result["files"])
        fixture.decision.update(outcome="rejected", candidate_id=None, original=None, profile=None)
        handoff["background"]["decision"] = stored("background", fixture.request["decision"])
        self.sync(fixture, target, handoff)
        self.assertEqual(package.validate(target, handoff)["status"], "rejected")
        handoff["background"]["decision"] = None
        fixture.manifest["presentation"] = {"status": "pending", "evidence": None}
        fixture.manifest["candidates"] = []
        self.sync(fixture, target, handoff)
        result = package.validate(target, handoff)
        self.assertEqual((result["status"], result["options"]), ("pending", []))

    def test_missing_offered_or_active_bytes_never_become_history_or_none(self):
        fixture, target, handoff = self.fixture(decision=False)
        (target / "background/original/B-b01.png").unlink()
        with self.assertRaisesRegex(InvalidInput, "Missing active"):
            package.validate(target, handoff)
        fixture, target, handoff = self.fixture()
        repo, history = self.history(fixture)
        handoff["background"]["history"] = history
        (target / "background/original/A-b01.png").unlink()
        with self.assertRaisesRegex(InvalidInput, "Missing active"):
            package.validate(target, handoff, history_repo=repo)

    def test_selected_real_derivation_root_dot_is_ready_and_inputs_remain_unchanged(self):
        _, target, handoff = self.fixture(derived=True, ready=True, prefix=".")
        self.gates(handoff, content_ready=True)
        before = {p.relative_to(target).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
                  for p in target.rglob("*") if p.is_file()}
        result = package.validate(target, handoff)
        self.assertEqual(result["status"], "selected")
        self.assertTrue(result["ready"])
        self.assertEqual(result["blockers"], [])
        self.assertEqual(result["derivative_files"], {"outputs/b01/derivation.json"})
        self.assertIn("outputs/b01/background.png", result["files"])
        self.assertEqual(before, {p.relative_to(target).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
                                 for p in target.rglob("*") if p.is_file()})

    def test_none_requires_waiver_and_null_derivation_without_texture(self):
        fixture, target, handoff = self.fixture(none=True, derived=True)
        self.gates(handoff, content_ready=True)
        result = package.validate(target, handoff)
        self.assertEqual((result["status"], result["ready"]), ("none", True))
        self.assertIsNone(result["derivation"]["output"])
        self.assertEqual({p.name for p in (target / "outputs/b01").iterdir()}, {"derivation.json"})
        fixture.manifest["candidate_policy"] = {"count": 3, "exception": None}
        self.sync(fixture, target, handoff)
        with self.assertRaises(InvalidInput):
            package.validate(target, handoff)

    def test_rights_and_visual_judgments_are_not_created_by_derivation(self):
        fixture, target, handoff = self.fixture(derived=True)
        result = package.validate(target, handoff)
        self.assertFalse(result["ready"])
        self.assertTrue(any("Q-HG04" in reason for reason in result["blockers"]))
        self.gates(handoff, content_ready=True)
        with self.assertRaisesRegex(InvalidInput, "pass gate|readiness"):
            package.validate(target, handoff)
        fixture, target, handoff = self.fixture(ready=True)
        fixture.manifest["candidates"][0]["provenance"]["rights_status"] = "unresolved"
        fixture.manifest["candidates"][0]["review"]["Q-HG01"]["result"] = "nicht erfüllt"
        self.sync(fixture, target, handoff)
        result = package.validate(target, handoff)
        self.assertTrue(any("rights" in reason for reason in result["blockers"]))
        self.assertTrue(any("Q-HG01" in reason for reason in result["blockers"]))

    def test_tampered_report_with_rebound_output_hash_fails_fresh_verification(self):
        _, target, handoff = self.fixture(derived=True, ready=True)
        directory = target / "outputs/b01"
        raw = bytearray((directory / "background.png").read_bytes())
        raw[-1] ^= 1
        (directory / "background.png").write_bytes(raw)
        report = json.loads((directory / "derivation.json").read_bytes())
        report["output"] = file_ref(directory, "background.png")
        put_json(directory, "derivation.json", report)
        handoff["background"]["derivation"]["ref"] = file_ref(target / "outputs", "b01/derivation.json")
        with self.assertRaisesRegex(InvalidInput, "verification failed"):
            package.validate(target, handoff)

    def test_exact_gate_paths_and_wrong_selected_reveal_are_rejected(self):
        fixture, target, handoff = self.fixture(derived=True, ready=True)
        self.gates(handoff)
        handoff["gate_evidence"]["background_choice"] = "decisions/d01.json"
        with self.assertRaisesRegex(InvalidInput, "evidence path"):
            package.validate(target, handoff)
        self.gates(handoff)
        handoff["reveal"] = {"file": "elsewhere.png", "sha256": "f" * 64}
        with self.assertRaisesRegex(InvalidInput, "another selected reveal"):
            package.validate(target, handoff)

    def test_explicit_directory_and_zip_history_allow_only_discarded_originals(self):
        for archive in (False, True):
            with self.subTest(archive=archive):
                fixture, target, handoff = self.fixture(derived=True, ready=True)
                repo, history = self.history(fixture, archive=archive)
                handoff["background"]["history"] = history
                for name in ("B", "C"):
                    (target / f"background/original/{name}-b01.png").unlink()
                with self.assertRaisesRegex(InvalidInput, "explicit history_repo"):
                    package.validate(target, handoff)
                before = self.git(repo, "status", "--porcelain")
                package_before = {p.relative_to(target).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
                                  for p in target.rglob("*") if p.is_file()}
                with patch.object(package.subprocess, "run", wraps=subprocess.run) as commands:
                    result = package.validate(target, handoff, history_repo=repo)
                self.assertEqual(result["status"], "selected")
                self.assertTrue(result["ready"])
                self.assertEqual(len(result["options"]), 3)
                self.assertNotIn("background/original/B-b01.png", result["files"])
                self.assertEqual(before, self.git(repo, "status", "--porcelain"))
                self.assertEqual(package_before, {p.relative_to(target).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
                                                 for p in target.rglob("*") if p.is_file()})
                history_calls = [call for call in commands.call_args_list if call.args[0][:3] == ["git", "-C", str(repo)]]
                self.assertTrue(history_calls)
                self.assertTrue(all(call.args[0][3] in ("rev-parse", "cat-file", "ls-tree") for call in history_calls))
                self.assertTrue(all(call.kwargs["env"]["GIT_NO_LAZY_FETCH"] == "1" and
                                    call.kwargs["env"]["GIT_NO_REPLACE_OBJECTS"] == "1" for call in history_calls))
                handoff["background"]["history"]["commit"] = "f" * 40
                with self.assertRaises(InvalidInput):
                    package.validate(target, handoff, history_repo=repo)

    def test_history_must_contain_the_identical_manifest(self):
        fixture, target, handoff = self.fixture()
        repo, history = self.history(fixture)
        handoff["background"]["history"] = history
        fixture.manifest["briefing"] += " Different original manifest."
        self.sync(fixture, target, handoff)
        (target / "background/original/C-b01.png").unlink()
        with self.assertRaisesRegex(InvalidInput, "history binding mismatch|identical"):
            package.validate(target, handoff, history_repo=repo)

    def test_test_only_material_revision_and_decision_self_binding_rejected(self):
        fixture, target, handoff = self.fixture()
        handoff["test_only"] = False
        with self.assertRaisesRegex(InvalidInput, "identities"):
            package.validate(target, handoff)
        handoff["test_only"] = True
        fixture.decision["presented_package"] = {"puzzle_id": handoff["puzzle_id"], "revision": "r01",
            "original_zip_sha256": "a" * 64, "handoff_sha256": "b" * 64, "inventory_sha256": "c" * 64}
        self.sync(fixture, target, handoff)
        with self.assertRaisesRegex(InvalidInput, "own sealed"):
            package.validate(target, handoff)
        fixture.decision["presented_package"] = None
        fixture.decision["original"]["sha256"] = "d" * 64
        self.sync(fixture, target, handoff)
        with self.assertRaisesRegex(InvalidInput, "Selected candidate"):
            package.validate(target, handoff)

    def test_external_roots_are_explicit_and_do_not_modify_original_status(self):
        fixture, target, handoff = self.fixture(derived=True, ready=True)
        original = copy.deepcopy(handoff)
        external = fixture.root.parent / "external"
        external.mkdir()
        shutil.copytree(target / "background", external / "job")
        shutil.copytree(target / "outputs", external / "results")
        binding = copy.deepcopy(handoff["background"])
        binding["decision"].update(storage="external", root="job")
        binding["derivation"].update(storage="external", root="results")
        with self.assertRaisesRegex(InvalidInput, "explicit external_root"):
            package.validate_external(target, handoff, binding)
        result = package.validate_external(target, handoff, binding, external_root=external)
        self.assertTrue(result["ready"])
        self.assertEqual(original, handoff)
        self.assertEqual(result["binding"], binding)

    def test_extra_derivation_files_and_unsafe_case_aliases_fail(self):
        _, target, handoff = self.fixture(derived=True, ready=True)
        (target / "outputs/b01/unrequested.txt").write_text("foreign", encoding="utf-8")
        with self.assertRaisesRegex(InvalidInput, "foreign entries"):
            package.validate(target, handoff)
        if os.name != "nt":
            (target / "outputs/b01/unrequested.txt").unlink()
            (target / "background/Original").mkdir()
            with self.assertRaisesRegex(InvalidInput, "case collision"):
                package.validate(target, handoff)

    def test_administrative_carried_from_keeps_the_actual_declaration_material_change_fails(self):
        fixture, target, handoff = self.fixture()
        old_manifest_ref = copy.deepcopy(fixture.request["manifest"])
        old_decision_ref = copy.deepcopy(fixture.request["decision"])
        old_manifest_bytes = (fixture.source / old_manifest_ref["file"]).read_bytes()
        old_decision_bytes = (fixture.source / old_decision_ref["file"]).read_bytes()
        revised_manifest = copy.deepcopy(fixture.manifest)
        revised_manifest.update(revision="bg02", briefing="TEST ONLY administrative briefing correction.")
        new_manifest_ref = put_json(fixture.source, "work/bg02.json", revised_manifest)
        revised_decision = copy.deepcopy(fixture.decision)
        revised_decision.update(revision="d02", background_revision="bg02", manifest=new_manifest_ref,
                                previous_decision=old_decision_ref, carried_from=old_decision_ref)
        new_decision_ref = put_json(fixture.source, "decisions/d02.json", revised_decision)
        shutil.copytree(fixture.source, target / "background", dirs_exist_ok=True)
        handoff["background"]["manifest"]["ref"] = new_manifest_ref
        handoff["background"]["decision"]["ref"] = new_decision_ref
        result = package.validate(target, handoff)
        self.assertEqual(result["status"], "selected")
        self.assertEqual(result["decision"]["timestamp_utc"], fixture.decision["timestamp_utc"])
        self.assertEqual((target / "background" / old_manifest_ref["file"]).read_bytes(), old_manifest_bytes)
        self.assertEqual((target / "background" / old_decision_ref["file"]).read_bytes(), old_decision_bytes)
        revised_manifest["candidates"][0]["revision"] = "b02"
        new_manifest_ref = put_json(target / "background", "work/bg02.json", revised_manifest)
        revised_decision["manifest"] = new_manifest_ref
        handoff["background"]["manifest"]["ref"] = new_manifest_ref
        handoff["background"]["decision"]["ref"] = put_json(target / "background", "decisions/d02.json", revised_decision)
        with self.assertRaisesRegex(InvalidInput, "carried_from"):
            package.validate(target, handoff)

    def test_separate_roots_cannot_bind_different_bytes_to_the_same_logical_path(self):
        fixture, target, handoff = self.fixture()
        external = fixture.root.parent / "external-conflict"
        external.mkdir()
        decision = copy.deepcopy(fixture.decision)
        decision["evidence"] = put(external, "context/reveal.png", b"TEST ONLY conflicting declaration bytes")
        decision_ref = put_json(external, "decisions/d01.json", decision)
        binding = copy.deepcopy(handoff["background"])
        binding["decision"] = stored(".", decision_ref, storage="external")
        # Original choice is open; outer supplied declaration is the first one.
        handoff["background"]["decision"] = None
        with self.assertRaisesRegex(InvalidInput, "Conflicting background source path"):
            package.validate_external(target, handoff, binding, external_root=external)

    def test_separate_roots_require_a_portable_namespace_before_derivation(self):
        for evidence, message in (("CONTEXT/declaration.txt", "Windows parent alias"),
                                  ("context/reveal.png/approval.txt", "File/directory collision")):
            with self.subTest(evidence=evidence):
                fixture, target, handoff = self.fixture(decision=False)
                external = fixture.root.parent / "external-namespace"
                external.mkdir()
                decision = copy.deepcopy(fixture.decision)
                decision["evidence"] = put(external, evidence, b"TEST ONLY declaration")
                decision_ref = put_json(external, "decisions/d01.json", decision)
                binding = copy.deepcopy(handoff["background"])
                binding["decision"] = stored(".", decision_ref, storage="external")
                self.assertIsNone(binding["derivation"])
                with self.assertRaisesRegex(InvalidInput, message):
                    package.validate_external(target, handoff, binding, external_root=external)


if __name__ == "__main__":
    unittest.main()
