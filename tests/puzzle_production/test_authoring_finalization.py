"""Real small HP-I1a publications; synthetic statements are never owner approvals."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools.puzzle_production import authoring_builder as builder, authoring_finalization as finalizer
from tools.puzzle_production import background_assets as assets, background_package
from tools.puzzle_production.authoring_staging import OwnedStage, StageError
from tools.puzzle_production.authoring_package import open_package
from tools.puzzle_production.contract import Aborted, load_json, write_json
from tests.puzzle_production import test_background_content as content_tests
from tests.puzzle_production.background_fixtures import file_ref, put, put_json


class AuthoringFinalizationTests(unittest.TestCase):
    def setUp(self):
        self.content = content_tests.BackgroundContentTests()
        self.content.setUp()
        self.addCleanup(self.content.doCleanups)
        self.root = self.content.root
        self.source = self.content.content()
        self.fixture, self.handoff = self.content.background(self.source, choice="offered", ready=True)
        for name in ("handoff.json", "inventory.json"):
            (self.source / name).unlink()
        self.handoff.update(inventory=None, authorization="TEST ONLY synthetic late-finalization source",
                            next_action="Record the actual late background choice.", blockers=[])
        self.build_request = {"format": "picross-authoring-build-request-v2", "handoff": self.handoff,
            "document_revision": 1, "files": [{"path": p.relative_to(self.source).as_posix(),
                "source": p.relative_to(self.source).as_posix(), **{k: file_ref(self.source,
                p.relative_to(self.source).as_posix())[k] for k in ("sha256", "bytes")}}
                for p in sorted(self.source.rglob("*")) if p.is_file()],
            "target": "local", "category_id": "voegel", "reveal_options": [], "external": {}}
        self.output = self.root / "authoring"
        self.output.mkdir()
        self.payload = self.root / "new-files"
        self.payload.mkdir()

    def build(self, *, repository=False):
        staging = self.output
        if repository:
            self.output = self.root / "checkout"
            self.output.mkdir()
            subprocess.run(["git", "init", "-q", str(self.output)], check=True, capture_output=True)
            path = self.output / builder.INDEX
            path.parent.mkdir(parents=True)
            write_json(path, {"format": "picross-authoring-index-v1", "entries": []})
            self.build_request["target"] = "repository"
        result = builder.build(self.build_request, self.source, staging,
                               self.output if repository else None)
        self.directory = Path(result["directory"])
        self.record_path = self.directory / "record.json"
        self.record_name = self.record_path.relative_to(self.output).as_posix()
        return result

    def request(self, *, outcome="selected", approval=False, revision="late01"):
        record = load_json(self.record_path)
        h = load_json(self.directory / "handoff.json")
        sidecar = self.directory.relative_to(self.output).as_posix() + "/sidecars/" + revision
        fixture = self.fixture
        fixture.decision["presented_package"] = {"puzzle_id": record["puzzle_id"], "revision": record["revision"],
            "handoff_sha256": record["handoff"]["sha256"],
            "inventory_sha256": h["inventory"]["sha256"], "original_zip_sha256": record["package"]["sha256"]}
        if outcome == "none":
            fixture.decision.update(outcome="none", candidate_id=None, original=None, profile=None)
            fixture.decision["statement"] = "TEST ONLY explicit late choice of no background."
            fixture.decision["evidence"] = put(fixture.source, "evidence/decision.txt",
                b"TEST ONLY explicit late choice of no background.")
        fixture.refresh_decision()
        result = assets.derive(fixture.request, fixture.source, fixture.output)
        self.assertIn(result["status"], ("derived", "none"), result)
        binding = deepcopy(record["background"])
        binding["decision"] = content_tests.stored(sidecar, fixture.request["decision"], "external")
        binding["derivation"] = content_tests.stored(sidecar, file_ref(fixture.output,
            fixture.request["output"] + "/derivation.json"), "external")
        for name in (fixture.request["decision"]["file"], fixture.decision["evidence"]["file"]):
            put(self.payload, sidecar + "/" + name, (fixture.source / name).read_bytes())
        for path in sorted(fixture.target.iterdir()):
            put(self.payload, sidecar + "/" + fixture.request["output"] + "/" + path.name, path.read_bytes())
        refs = {name: None for name in ("approval.json", "manual-authorization.json", "owner-override.json", "palette-exception.json")}
        if approval:
            with open_package(self.directory / "package.zip", allow_background=True, external_root=self.payload) as package:
                checked = background_package.validate_external(package.root, package.handoff, binding,
                    deadline=package.deadline, external_root=self.payload)
                approval_path = self.content.approval(package.root, self.directory / "package.zip", background=checked)
            refs["approval.json"] = put(self.payload, sidecar + "/approval.json", approval_path.read_bytes())
        return {"format": finalizer.REQUEST, "record": file_ref(self.output, self.record_name),
            "sidecar_root": sidecar, "background": binding, "authorizations": refs,
            "files": [file_ref(self.payload, p.relative_to(self.payload).as_posix())
                      for p in sorted((self.payload / sidecar).rglob("*")) if p.is_file()]}

    def run_finalize(self, request):
        return builder.finalize_background(request, self.payload, self.output)

    def approval_request(self, revision="late02"):
        record = load_json(self.record_path)
        sidecar = self.directory.relative_to(self.output).as_posix() + "/sidecars/" + revision
        with open_package(self.directory / "package.zip", allow_background=True, external_root=self.output) as package:
            checked = background_package.validate_external(package.root, package.handoff, record["background"],
                deadline=package.deadline, external_root=self.output)
            path = self.content.approval(package.root, self.directory / "package.zip", background=checked)
        approval = put(self.payload, sidecar + "/approval.json", path.read_bytes())
        authorizations = deepcopy(record["verification"]["authorizations"])
        authorizations["approval.json"] = approval
        return {"format": finalizer.REQUEST, "record": file_ref(self.output, self.record_name),
            "sidecar_root": sidecar, "background": record["background"], "authorizations": authorizations,
            "files": [approval]}

    def successor(self, *, previous=True, revision="late02"):
        record = load_json(self.record_path)
        sidecar = self.directory.relative_to(self.output).as_posix() + "/sidecars/" + revision
        fixture = self.fixture
        fixture.decision.update(revision="d02", outcome="none", candidate_id=None, original=None, profile=None,
            previous_decision=deepcopy(record["background"]["decision"]["ref"]) if previous else None,
            statement="TEST ONLY explicit successor choosing no background.",
            evidence=put(fixture.source, "evidence/decision02.txt", b"TEST ONLY explicit later none choice."))
        fixture.request.update(decision=put_json(fixture.source, "decisions/d02.json", fixture.decision),
                               source=None, output="derived/" + revision)
        result = assets.derive(fixture.request, fixture.source, fixture.output)
        self.assertEqual(result["status"], "none", result)
        binding = deepcopy(record["background"])
        binding["decision"] = content_tests.stored(sidecar, fixture.request["decision"], "external")
        binding["derivation"] = content_tests.stored(sidecar, file_ref(fixture.output,
            fixture.request["output"] + "/derivation.json"), "external")
        names = ["decisions/d02.json", "evidence/decision02.txt"]
        if previous:
            names += ["decisions/d01.json", "evidence/decision.txt"]
        for name in names:
            put(self.payload, sidecar + "/" + name, (fixture.source / name).read_bytes())
        put(self.payload, sidecar + "/" + fixture.request["output"] + "/derivation.json",
            (fixture.target / "derivation.json").read_bytes())
        return {"format": finalizer.REQUEST, "record": file_ref(self.output, self.record_name),
            "sidecar_root": sidecar, "background": binding,
            "authorizations": deepcopy(record["verification"]["authorizations"]),
            "files": [file_ref(self.payload, p.relative_to(self.payload).as_posix())
                      for p in sorted((self.payload / sidecar).rglob("*")) if p.is_file()]}

    @staticmethod
    def bytes_and_times(root):
        return {p.relative_to(root).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
                for p in root.rglob("*") if p.is_file() and p.name != ".authoring-builder.lock"}

    def test_selected_approval_updates_only_record_and_new_sidecar_and_repeats_without_write(self):
        built = self.build()
        request = self.request(approval=True)
        original = self.bytes_and_times(self.output)
        source = self.bytes_and_times(self.payload)
        result = self.run_finalize(request)
        self.assertEqual(result["status"], "updated", result)
        self.assertEqual(set(result), {"format", "status", "record", "sheet", "operation"})
        self.assertEqual(result["record"]["state"], "editorially_approved")
        self.assertEqual(result["record"]["verification"]["authorizations"], request["authorizations"])
        self.assertFalse(result["record"]["verification"]["integration_ready"])
        self.assertIsNone(result["record"]["integration"])
        self.assertIsNone(result["record"]["source_commit"])
        self.assertIsNone(result["record"]["pr"])
        self.assertEqual(result["sheet"]["format"], "picross-cheatsheet-update-v3")
        self.assertEqual(result["sheet"]["Hintergrundauswahl"], "A")
        after = self.bytes_and_times(self.output)
        for name, value in original.items():
            if name != self.record_name:
                self.assertEqual(after[name], value, name)
        self.assertEqual(source, self.bytes_and_times(self.payload))
        self.assertEqual(built["record"]["background"]["decision"], None)
        directory_times = {p: p.stat().st_mtime_ns for p in [self.output, *self.output.rglob("*")] if p.is_dir()}
        self.assertEqual(self.run_finalize(request), {**result, "status": "reused"})
        self.assertEqual(after, self.bytes_and_times(self.output))
        self.assertEqual(directory_times, {p: p.stat().st_mtime_ns for p in directory_times})

    def test_none_has_real_null_derivation_and_no_png(self):
        self.build()
        request = self.request(outcome="none")
        result = self.run_finalize(request)
        self.assertEqual(result["status"], "updated", result)
        self.assertEqual(result["record"]["state"], "content_ready")
        self.assertEqual(result["sheet"]["Hintergrundauswahl"], "none")
        self.assertFalse(result["record"]["verification"]["editorial_approved"])
        sidecar = self.output / request["sidecar_root"]
        self.assertFalse(list(sidecar.rglob("*.png")))
        report = load_json(sidecar / self.fixture.request["output"] / "derivation.json")
        self.assertIsNone(report["output"])
        self.assertEqual(self.run_finalize(request)["status"], "reused")

    def test_followup_approval_keeps_prior_sidecars_and_authorization_cannot_disappear(self):
        self.build()
        initial = self.request(outcome="none")
        self.assertEqual(self.run_finalize(initial)["status"], "updated")
        old_sidecar = self.bytes_and_times(self.output / initial["sidecar_root"])
        request = self.approval_request()
        result = self.run_finalize(request)
        self.assertEqual(result["status"], "updated", result)
        self.assertEqual(result["record"]["state"], "editorially_approved")
        self.assertEqual(old_sidecar, self.bytes_and_times(self.output / initial["sidecar_root"]))
        self.assertEqual(self.run_finalize(request)["status"], "reused")
        removal = {**deepcopy(request), "record": file_ref(self.output, self.record_name),
                   "sidecar_root": request["sidecar_root"] + "-removed", "files": []}
        removal["authorizations"]["approval.json"] = None
        result = self.run_finalize(removal)
        self.assertEqual(result["status"], "invalid_input", result)
        self.assertIn("Cannot silently remove", result["message"])
        self.assertFalse((self.output / removal["sidecar_root"]).exists())

    def test_early_original_choice_is_reused_for_late_derivation_and_approval(self):
        # This is still an unsealed synthetic build draft: the original early
        # human bytes become part of its first package, never a resealed input.
        put(self.source, "background/decisions/d01.json",
            (self.fixture.source / "decisions/d01.json").read_bytes())
        self.handoff["background"]["decision"] = content_tests.stored("background", self.fixture.request["decision"])
        self.handoff["gates"]["background_choice"] = "pass"
        self.handoff["gate_evidence"]["background_choice"] = "background/decisions/d01.json"
        self.build_request["files"].append({"path": "background/decisions/d01.json",
            "source": "background/decisions/d01.json", **{k: file_ref(self.source,
                "background/decisions/d01.json")[k] for k in ("sha256", "bytes")}})
        self.build()
        record = load_json(self.record_path)
        result = assets.derive(self.fixture.request, self.fixture.source, self.fixture.output)
        self.assertEqual(result["status"], "derived", result)
        sidecar = self.directory.relative_to(self.output).as_posix() + "/sidecars/early-derived"
        binding = deepcopy(record["background"])
        binding["derivation"] = content_tests.stored(sidecar, file_ref(self.fixture.output,
            self.fixture.request["output"] + "/derivation.json"), "external")
        files = [put(self.payload, sidecar + "/" + self.fixture.request["output"] + "/" + path.name,
                     path.read_bytes()) for path in sorted(self.fixture.target.iterdir())]
        request = {"format": finalizer.REQUEST, "record": file_ref(self.output, self.record_name),
            "sidecar_root": sidecar, "background": binding,
            "authorizations": {name: None for name in ("approval.json", "manual-authorization.json",
                "owner-override.json", "palette-exception.json")}, "files": files}
        result = self.run_finalize(request)
        self.assertEqual(result["status"], "updated", result)
        self.assertEqual(result["record"]["state"], "content_ready")
        self.assertEqual(result["record"]["background"]["decision"], record["background"]["decision"])
        result = self.run_finalize(self.approval_request())
        self.assertEqual(result["status"], "updated", result)
        self.assertEqual(result["record"]["state"], "editorially_approved")

    def test_changed_choice_requires_explicit_current_outer_predecessor(self):
        self.build()
        initial = self.request()
        self.assertEqual(self.run_finalize(initial)["status"], "updated")
        before = self.bytes_and_times(self.output)
        missing = self.successor(previous=False, revision="unbound")
        result = self.run_finalize(missing)
        self.assertEqual(result["status"], "invalid_input", result)
        self.assertIn("explicitly supersede", result["message"])
        self.assertEqual(before, self.bytes_and_times(self.output))
        request = self.successor()
        result = self.run_finalize(request)
        self.assertEqual(result["status"], "updated", result)
        self.assertEqual(result["sheet"]["Hintergrundauswahl"], "none")
        self.assertEqual(result["record"]["state"], "content_ready")
        for name, value in before.items():
            if name != self.record_name:
                self.assertEqual(self.bytes_and_times(self.output)[name], value)

    def test_publication_interruptions_resume_exactly_and_never_reseal(self):
        self.build()
        request = self.request(outcome="none")
        before = self.record_path.read_bytes()
        for boundary in ("before-sidecar-publication", "sidecar-published", "before-record-replace", "record-committed"):
            def stop(name):
                if name == boundary:
                    raise Aborted("TEST ONLY interrupted " + name)
            with self.subTest(boundary=boundary), patch.object(finalizer, "checkpoint", stop):
                result = self.run_finalize(request)
            self.assertEqual(result["status"], "aborted", result)
            if boundary == "before-sidecar-publication":
                self.assertIsNone(result["remaining"])
                self.assertFalse((self.output / request["sidecar_root"]).exists())
            else:
                self.assertEqual(result["remaining"], str(self.output / request["sidecar_root"]))
            if boundary != "record-committed":
                self.assertEqual(self.record_path.read_bytes(), before)
            self.assertFalse(list(self.directory.parent.glob(".hp-i1a-finalize-*")))
        committed = self.bytes_and_times(self.output)
        result = self.run_finalize(request)
        self.assertEqual(result["status"], "reused", result)
        self.assertEqual(committed, self.bytes_and_times(self.output))

    def test_stale_record_foreign_target_and_shared_lock_fail_without_overwrite(self):
        self.build()
        request = self.request(outcome="none")
        stale = deepcopy(request)
        stale["record"]["sha256"] = "0" * 64
        self.assertEqual(self.run_finalize(stale)["status"], "conflict")
        sidecar = self.output / request["sidecar_root"]
        sidecar.mkdir(parents=True)
        self.assertEqual(self.run_finalize(request)["status"], "conflict")
        self.assertEqual(list(sidecar.iterdir()), [])
        sidecar.rmdir()
        with builder.writer(self.output / ".authoring-builder.lock"):
            result = self.run_finalize(request)
        self.assertEqual(result["status"], "conflict", result)
        self.assertFalse(sidecar.exists())

    def test_mutating_observed_source_or_record_is_conflict_and_preserves_foreign_bytes(self):
        self.build()
        request = self.request(outcome="none")
        name = request["files"][0]["file"]
        path = self.payload / name
        original = path.read_bytes()
        def mutate(name):
            if name == "before-sidecar-publication":
                path.write_bytes(b"foreign source bytes")
        with patch.object(finalizer, "checkpoint", mutate):
            result = self.run_finalize(request)
        self.assertEqual(result["status"], "conflict", result)
        self.assertFalse((self.output / request["sidecar_root"]).exists())
        path.write_bytes(original)
        before = self.record_path.read_bytes()
        def change_record(name):
            if name == "before-record-replace":
                self.record_path.write_bytes(before + b" ")
        with patch.object(finalizer, "checkpoint", change_record):
            result = self.run_finalize(request)
        self.assertEqual(result["status"], "conflict", result)
        self.assertEqual(self.record_path.read_bytes(), before + b" ")
        self.assertEqual(result["remaining"], str(self.output / request["sidecar_root"]))

    def test_coherent_foreign_operation_rewrite_is_a_conflict_before_record_commit(self):
        self.build()
        request = self.request(outcome="none")
        before = self.record_path.read_bytes()
        sidecar = self.output / request["sidecar_root"]
        def rewrite(name):
            if name == "before-record-replace":
                after = load_json(sidecar / "record.after.json")
                after["next_action"] = "Foreign replacement of the proposed action."
                write_json(sidecar / "record.after.json", after)
                operation = load_json(sidecar / "operation.json")
                operation["after"] = file_ref(sidecar, "record.after.json")
                write_json(sidecar / "operation.json", operation)
        with patch.object(finalizer, "checkpoint", rewrite):
            result = self.run_finalize(request)
        self.assertEqual(result["status"], "conflict", result)
        self.assertIn("freshly checked bytes", result["message"])
        self.assertEqual(self.record_path.read_bytes(), before)
        self.assertEqual(load_json(sidecar / "record.after.json")["next_action"],
                         "Foreign replacement of the proposed action.")
        self.assertEqual(self.run_finalize(request)["status"], "conflict")

    def test_foreign_stage_file_survives_aborted_finalization_at_reported_path(self):
        self.build()
        request = self.request(outcome="none")
        before = self.record_path.read_bytes()
        def interrupt(name):
            if name == "before-sidecar-publication":
                stage = next(self.directory.parent.glob(".hp-i1a-finalize-*"))
                (stage / "foreign.txt").write_bytes(b"foreign bytes must remain")
                raise Aborted("TEST ONLY interrupted stage with foreign bytes")
        with patch.object(finalizer, "checkpoint", interrupt):
            result = self.run_finalize(request)
        self.assertEqual(result["status"], "aborted", result)
        self.assertEqual(self.record_path.read_bytes(), before)
        remaining = Path(result["remaining"])
        self.assertEqual((remaining / "foreign.txt").read_bytes(), b"foreign bytes must remain")
        self.assertIn(str(remaining), result["message"])
        self.assertFalse((self.output / request["sidecar_root"]).exists())

    def test_cleanup_blockade_after_record_commit_reports_rest_and_allows_true_retry(self):
        self.build()
        request = self.request(outcome="none")
        with patch.object(OwnedStage, "_cleanup", side_effect=PermissionError("TEST ONLY locked stage")):
            result = self.run_finalize(request)
        self.assertEqual(result["status"], "technical_error", result)
        self.assertEqual(set(result), {"format", "status", "message", "remaining", "next_action"})
        self.assertTrue(Path(result["remaining"]).is_dir())
        self.assertEqual(load_json(self.record_path)["state"], "content_ready")
        completed = self.bytes_and_times(self.directory)
        self.assertEqual(self.run_finalize(request)["status"], "reused")
        self.assertEqual(completed, self.bytes_and_times(self.directory))

    def test_repository_index_and_original_bytes_stay_unchanged(self):
        self.build(repository=True)
        request = self.request(outcome="none")
        index = self.output / builder.INDEX
        original = index.read_bytes(), index.stat().st_mtime_ns
        with builder.writer(builder.git_root(self.output) / "authoring-builder.lock"):
            self.assertEqual(self.run_finalize(request)["status"], "conflict")
        result = self.run_finalize(request)
        self.assertEqual(result["status"], "updated", result)
        self.assertEqual((index.read_bytes(), index.stat().st_mtime_ns), original)

    def test_request_and_new_payload_are_closed(self):
        self.build()
        request = self.request(outcome="none")
        for mutation in ("extra-key", "bad-hash", "unused", "reserved", "wrong-presented"):
            changed = deepcopy(request)
            if mutation == "extra-key":
                changed["trusted"] = True
            elif mutation == "bad-hash":
                changed["files"][0]["sha256"] = "0" * 64
            elif mutation == "unused":
                changed["files"].append(put(self.payload, changed["sidecar_root"] + "/unused.txt", b"unused"))
            elif mutation == "reserved":
                changed["files"].append(put(self.payload, changed["sidecar_root"] + "/operation.json", b"reserved"))
            else:
                changed["background"]["manifest"]["ref"]["sha256"] = "0" * 64
            with self.subTest(mutation=mutation):
                result = self.run_finalize(changed)
                self.assertEqual(result["status"], "invalid_input", result)
                self.assertFalse((self.output / request["sidecar_root"]).exists())

    def test_record_field_types_cannot_be_relabelled_by_a_new_expected_hash(self):
        self.build()
        request = self.request(outcome="none")
        before = self.record_path.read_bytes()
        parameters = json.loads(before)["parameters"]
        parameters[0]["width"] = float(parameters[0]["width"])
        for key, value in (("reveal_options", {}), ("reveal_options", None),
                           ("source_commit", []), ("pr", False), ("width", 3.0),
                           ("used_colors", True), ("parameters", parameters)):
            changed = json.loads(before)
            changed[key] = value
            write_json(self.record_path, changed)
            request["record"] = file_ref(self.output, self.record_name)
            with self.subTest(field=key, value=value):
                result = self.run_finalize(request)
                self.assertEqual(result["status"], "invalid_input", result)
                self.assertFalse((self.output / request["sidecar_root"]).exists())
        self.record_path.write_bytes(before)

    def test_cli_produces_one_json_result_for_parse_and_input_failures(self):
        for flags in (("--missing",), ("--request", str(self.root / "absent.json"),
                "--source-root", str(self.payload), "--output-root", str(self.output))):
            run = subprocess.run([sys.executable, "-m", "tools.puzzle_production.authoring_builder",
                "finalize-background", *flags], capture_output=True, text=True)
            self.assertEqual(run.returncode, 2, run.stderr)
            result = json.loads(run.stdout)
            self.assertEqual(result["format"], finalizer.RESULT)
            self.assertEqual(set(result), {"format", "status", "message", "remaining", "next_action"})


class OwnedStageTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="hp-i1a-stage-tests-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def test_nested_owned_replacement_and_moved_payload_leave_no_private_rest(self):
        target = self.root / "published"
        with OwnedStage(self.root, ".private-", {"purpose": "TEST ONLY"}) as stage:
            owned = stage.root
            stage.mkdir("export/external")
            stage.write("export/inspection.json", b'{"verified":false}\n')
            stage.replace("export/inspection.json", b'{"verified":true}\n')
            self.assertEqual((stage.root / "export/inspection.json").read_bytes(), b'{"verified":true}\n')
            builder.publish_directory(stage.root / "export", target)
        self.assertFalse(owned.exists())
        self.assertEqual((target / "inspection.json").read_bytes(), b'{"verified":true}\n')

    def test_changed_owned_prefix_and_foreign_files_are_preserved(self):
        for change in ("prefix", "foreign"):
            with self.subTest(change=change), self.assertRaises(StageError) as caught:
                with OwnedStage(self.root, ".private-", {"purpose": "TEST ONLY"}) as stage:
                    path = stage.write("payload/data.bin", b"complete owned bytes")
                    if change == "prefix":
                        path.write_bytes(b"complete")
                    else:
                        (stage.root / "foreign.txt").write_bytes(b"foreign")
            self.assertEqual(caught.exception.status, "conflict")
            self.assertEqual(caught.exception.remaining, str(stage.root))
            self.assertTrue(path.exists())
            self.assertEqual(path.read_bytes(), b"complete" if change == "prefix" else b"complete owned bytes")
            self.assertIn(str(stage.root), str(caught.exception))

    def test_replace_refuses_changed_own_file_and_exclusive_write_preserves_preexisting_file(self):
        with self.assertRaises(StageError):
            with OwnedStage(self.root, ".private-", {"purpose": "TEST ONLY"}) as stage:
                path = stage.write("payload/data.bin", b"own")
                path.write_bytes(b"foreign")
                stage.replace("payload/data.bin", b"replacement")
        self.assertEqual(path.read_bytes(), b"foreign")
        with self.assertRaises(StageError):
            with OwnedStage(self.root, ".private-", {"purpose": "TEST ONLY"}) as stage:
                path = stage.root / "foreign.bin"
                path.write_bytes(b"same bytes")
                stage.write("foreign.bin", b"same bytes")
        self.assertEqual(path.read_bytes(), b"same bytes")


if __name__ == "__main__":
    unittest.main()
