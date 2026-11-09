"""Small synthetic HP-I1a transports; all image and content readers run for real."""
from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import time
import unittest
from unittest.mock import patch

from tools.puzzle_production import authoring_package as ap, background_assets as assets
from tools.puzzle_production import background_package as bp, target_adapter as adapter
from tools.puzzle_production import background_export as export_v6
from tools.puzzle_production.contract import InvalidInput, load_json, write_json
from tools.puzzle_production.za1_fixtures import ROOT, approve, seal
from tests.puzzle_production import test_background_content as fixtures
from tests.puzzle_production.background_fixtures import file_ref, put, put_json


class BackgroundExportTests(unittest.TestCase):
    def setUp(self):
        self.case = fixtures.BackgroundContentTests()
        self.case.setUp()
        self.addCleanup(self.case.doCleanups)
        self.root = self.case.root
        self.options = {"name": "TEST ONLY", "revision": 7, "stem": "background_test", "save_slot": "same_slot",
                        "category_id": "voegel", "categories_path": ROOT / "tests/puzzle_production/fixtures/catalog/categories.json"}

    def early(self, choice="selected", *, name="package"):
        source = self.case.content(name=name)
        fixture, h = self.case.background(source, choice=choice, ready=True, state="content_ready")
        archive = self.case.archive(source, name + ".zip")
        approval = self.case.approval(source, archive, name=name + "-approval.json")
        return source, fixture, h, archive, approval

    def export(self, archive, approval, *, name="export", external=None, history=None):
        output = self.root / name
        manifest = adapter.export(archive, output, approval_path=approval, allow_background=True,
                                  external_root=external, history_repo=history, **self.options)
        return output, manifest

    def rehash(self, output, manifest=None):
        manifest = manifest or load_json(output / "manifest.json")
        manifest["files"] = {n: h for n, h in adapter.hashes(output).items() if n != "manifest.json"}
        write_json(output / "manifest.json", manifest)
        return manifest

    def late(self, *, dot=False, none=False):
        source = self.case.content()
        fixture, h = self.case.background(source, ready=True)
        archive = self.case.archive(source)
        fixture.decision["presented_package"] = {"puzzle_id": h["puzzle_id"], "revision": h["revision"],
            "original_zip_sha256": ap.file_hash(archive), "handoff_sha256": ap.file_hash(source / "handoff.json"),
            "inventory_sha256": h["inventory"]["sha256"]}
        if none:
            fixture.decision.update(outcome="none", candidate_id=None, original=None, profile=None)
        fixture.refresh_decision()
        result = assets.derive(fixture.request, fixture.source, fixture.output)
        self.assertIn(result["status"], ("derived", "none"), result)
        if dot:
            shutil.copytree(fixture.target, fixture.source / "proof/late")
            external = fixture.source
            binding = {"manifest": fixtures.stored(".", fixture.request["manifest"], "external"),
                       "decision": fixtures.stored(".", fixture.request["decision"], "external"),
                       "derivation": fixtures.stored(".", file_ref(external, "proof/late/derivation.json"), "external"),
                       "history": None}
        else:
            external = fixture.root
            binding = {"manifest": deepcopy(h["background"]["manifest"]),
                       "decision": fixtures.stored("source", fixture.request["decision"], "external"),
                       "derivation": fixtures.stored("output", file_ref(fixture.output, "derived/bg01/derivation.json"), "external"),
                       "history": None}
        with ap.open_package(archive, allow_background=True, external_root=external) as package:
            report = adapter.inspect(package, allow_background=True, background_binding=binding)[0]
            self.assertEqual(report["effective_state"], "content_ready")
            self.assertFalse(report["editorial_approved"])
            background = package.effective_background
        approval = self.case.approval(source, archive, background=background)
        return source, fixture, h, archive, approval, external, binding

    def test_early_selected_and_none_preserve_original_and_runtime_identity_offline(self):
        for choice in ("selected", "none"):
            source = self.case.content(name=choice)
            legacy_approval = self.root / (choice + "-legacy-approval.json")
            approve(source, legacy_approval)
            legacy = self.root / (choice + "-legacy")
            adapter.export(source, legacy, approval_path=legacy_approval, **self.options)
            fixture, _ = self.case.background(source, choice=choice, ready=True, state="content_ready")
            archive = self.case.archive(source, choice + ".zip")
            approval = self.case.approval(source, archive, name=choice + "-approval.json")
            original, original_approval = archive.read_bytes(), approval.read_bytes()
            output, m = self.export(archive, approval, name=choice + "-export")
            portable = self.root / (choice + "-portable")
            shutil.copytree(output, portable)
            for path in (source, fixture.root, archive, approval):
                path.rename(path.with_name(path.name + "-unavailable"))
            with patch.object(bp, "_History", side_effect=AssertionError("Offline export must not read Git history")):
                checked, report = adapter.verify_export(portable)
            self.assertEqual(checked, m)
            self.assertEqual((portable / "input/package.zip").read_bytes(), original)
            self.assertEqual((portable / "approval.json").read_bytes(), original_approval)
            for field in ("definition", "reveal"):
                self.assertEqual((portable / m[field]).read_bytes(), (legacy / m[field]).read_bytes())
            self.assertEqual((m["runtime_revision"], m["save_slot"]), (7, "same_slot"))
            self.assertTrue(report["export_verified"] and report["technical"] and report["editorial_approved"])
            self.assertEqual(report["effective_state"], "editorially_approved")
            self.assertFalse(any(report[k] for k in ("integration_ready", "catalog_ready", "registered")))
            runtime = {n for n in m["files"] if n.startswith("runtime/")}
            expected = {m["definition"], m["reveal"], "runtime/art/content/background_test.txt"}
            if choice == "selected":
                expected.update((m["background_asset"]["file"], m["background_notice"]["file"]))
                notice = (portable / m["background_notice"]["file"]).read_text()
                for value in ("HP-W2 synthetic tests", "Generated test pixels", "Repository-owned synthetic test construction"):
                    self.assertIn(value, notice)
            else:
                self.assertIsNone(m["background_asset"])
                self.assertIsNone(m["background_notice"])
            self.assertEqual(runtime, expected)

    def test_late_selected_and_none_with_split_and_dot_external_roots(self):
        # One full late selected case with root '.', one none case with split
        # roots. Both use a real unchanged original, HP-W2 and outer approval.
        for dot, none in ((True, False), (False, True)):
            if dot:
                case = self
            else:
                case = BackgroundExportTests()
                case.setUp()
                self.addCleanup(case.doCleanups)
            source, fixture, h, archive, approval, external, binding = case.late(dot=dot, none=none)
            original = archive.read_bytes(), (source / "handoff.json").read_bytes()
            with self.assertRaisesRegex(InvalidInput, "final approval|readiness"):
                case.export(archive, None, name="no-approval", external=external)
            self.assertFalse((case.root / "no-approval").exists())
            output, manifest = case.export(archive, approval, external=external)
            fixture.root.rename(fixture.root.with_name("removed-external"))
            source.rename(source.with_name("removed-original"))
            archive.unlink()
            approval.unlink()
            _, report = adapter.verify_export(output)
            self.assertEqual(report["original_state"], "raster_ready")
            self.assertEqual(report["background"]["status"], "none" if none else "selected")
            self.assertEqual((output / "input/package.zip").read_bytes(), original[0])
            self.assertEqual(manifest["background"]["manifest"], binding["manifest"])
            self.assertTrue(any(n.startswith("external/") for n in manifest["files"]))

    def compact_history(self, *, later_b=False):
        source, fixture, h, _, _ = self.early()
        if later_b:
            # Build a new synthetic original with all judgments recorded before
            # sealing, so later B selection does not alter its manifest bytes.
            review = fixture.manifest["candidates"][0]["review"]
            for row in fixture.manifest["candidates"][1:]:
                row["review"] = deepcopy(review)
                for judgment in row["review"].values():
                    judgment["evidence"] = [deepcopy(row["original"])]
            fixture.refresh()
            shutil.copytree(fixture.source, source / "background", dirs_exist_ok=True)
            fixture.request["output"] = "derived/all-reviewed"
            self.assertEqual(assets.derive(fixture.request, fixture.source, fixture.output)["status"], "derived")
            shutil.rmtree(source / "outputs/background")
            shutil.copytree(fixture.target, source / "outputs/background")
            h["background"]["manifest"]["ref"] = deepcopy(fixture.request["manifest"])
            h["background"]["decision"]["ref"] = deepcopy(fixture.request["decision"])
            h["background"]["derivation"]["ref"] = file_ref(source / "outputs", "background/derivation.json")
        history = self.root / "history"
        history.mkdir()
        shutil.copytree(fixture.source, history / "saved")
        for args in (("init", "-q"), ("config", "user.name", "TEST ONLY"),
                     ("config", "user.email", "synthetic@example.invalid"), ("add", "."),
                     ("commit", "-qm", "Synthetic immutable background originals")):
            subprocess.run(["git", "-C", str(history), *args], check=True, capture_output=True)
        h["background"]["history"] = {"commit": subprocess.check_output(["git", "-C", str(history), "rev-parse", "HEAD"], text=True).strip(),
                                       "storage": "directory", "path": "saved", "root": "."}
        for letter in ("B", "C"):
            (source / f"background/original/{letter}-b01.png").unlink()
        seal(source, h)
        archive = self.case.archive(source, "compact.zip")
        with ap.open_package(archive, allow_background=True, history_repo=history) as package:
            background = package.background
        if later_b:
            decision = deepcopy(fixture.decision)
            chosen = fixture.manifest["candidates"][1]
            decision.update(revision="d02", candidate_id="B", original=chosen["original"],
                previous_decision=deepcopy(fixture.request["decision"]),
                statement="TEST ONLY later isolated choice B.",
                evidence=put(fixture.source, "evidence/select-B.txt", b"TEST ONLY later B."),
                presented_package={"puzzle_id": h["puzzle_id"], "revision": h["revision"],
                    "original_zip_sha256": ap.file_hash(archive), "handoff_sha256": ap.file_hash(source / "handoff.json"),
                    "inventory_sha256": h["inventory"]["sha256"]})
            fixture.request.update(decision=put_json(fixture.source, "decisions/d02.json", decision),
                                   source=chosen["original"], output="derived/late-B")
            self.assertEqual(assets.derive(fixture.request, fixture.source, fixture.output)["status"], "derived")
            (fixture.source / "original/C-b01.png").unlink()
            binding = {"manifest": fixtures.stored("source", fixture.request["manifest"], "external"),
                       "decision": fixtures.stored("source", fixture.request["decision"], "external"),
                       "derivation": fixtures.stored("output", file_ref(fixture.output, "derived/late-B/derivation.json"), "external"),
                       "history": deepcopy(h["background"]["history"])}
            with ap.open_package(archive, allow_background=True, history_repo=history) as package:
                background = bp.validate_external(package.root, h, binding, history_repo=history, external_root=fixture.root)
        approval = self.case.approval(source, archive, background=background, name="compact-approval.json")
        return source, fixture, h, archive, approval, history

    def test_compact_history_is_transported_and_each_entry_must_be_needed(self):
        source, fixture, h, archive, approval, history = self.compact_history()
        with self.assertRaisesRegex(InvalidInput, "history_repo"):
            self.export(archive, approval, name="no-history")
        output, manifest = self.export(archive, approval, history=history)
        self.assertEqual([e["ref"]["file"] for e in manifest["input"]["discarded_files"]],
                         ["original/B-b01.png", "original/C-b01.png"])
        for path in (source, fixture.root, history):
            path.rename(path.with_name(path.name + "-unavailable"))
        archive.unlink()
        self.assertTrue(adapter.verify_export(output)[1]["export_verified"])
        original = deepcopy(manifest)
        entry = deepcopy(manifest["input"]["discarded_files"][0])
        manifest["input"]["discarded_files"].append(entry)
        self.rehash(output, manifest)
        with self.assertRaisesRegex(InvalidInput, "Duplicate"):
            adapter.verify_export(output)
        manifest = deepcopy(original)
        extra = {"manifest": entry["manifest"], "ref": {"file": "unused.txt", "sha256": ap.file_hash(output / "approval.json"),
                    "bytes": (output / "approval.json").stat().st_size}, "file": "input/discarded/unused.txt"}
        shutil.copyfile(output / "approval.json", output / extra["file"])
        manifest["input"]["discarded_files"].append(extra)
        self.rehash(output, manifest)
        with self.assertRaisesRegex(InvalidInput, "Unneeded"):
            adapter.verify_export(output)

    def test_original_discard_can_be_outer_active_but_supplement_never_supplies_active_read(self):
        source, fixture, h, archive, approval, history = self.compact_history(later_b=True)
        output, manifest = self.export(archive, approval, external=fixture.root, history=history)
        self.assertEqual(manifest["background"]["candidate_id"], "B")
        self.assertIn("input/discarded/original/B-b01.png", manifest["files"])
        self.assertIn("external/source/original/B-b01.png", manifest["files"])
        for path in (source, fixture.root, history):
            path.rename(path.with_name(path.name + "-unavailable"))
        archive.unlink()
        self.assertTrue(adapter.verify_export(output)[1]["export_verified"])
        (output / "external/source/original/B-b01.png").unlink()
        self.rehash(output, manifest)
        with self.assertRaisesRegex(InvalidInput, "Missing active background"):
            adapter.verify_export(output)

    def test_rehashed_runtime_approval_extra_file_and_generation_tampering_fail(self):
        _, _, _, archive, approval = self.early()
        output, manifest = self.export(archive, approval)
        for name, mutate in ((manifest["background_asset"]["file"], lambda raw: raw[:-1] + bytes([raw[-1] ^ 1])),
                             (manifest["background_notice"]["file"], lambda raw: raw + b"Invented attribution\n"),
                             ("approval.json", lambda raw: json.dumps({**json.loads(raw), "original_zip_sha256": "0" * 64}).encode()),
                             ("input/package.zip", lambda raw: raw + b"changed original")):
            original = (output / name).read_bytes()
            (output / name).write_bytes(mutate(original))
            changed = deepcopy(manifest)
            for field in ("background_asset", "background_notice"):
                if changed[field]["file"] == name:
                    changed[field] = file_ref(output, name)
            if name == "approval.json":
                changed["approval_sha256"] = ap.file_hash(output / name)
            if name == "input/package.zip":
                changed["input"]["original_package"] = file_ref(output, name)
            self.rehash(output, changed)
            with self.subTest(name=name), self.assertRaises(InvalidInput):
                adapter.verify_export(output)
            (output / name).write_bytes(original)
            self.rehash(output, deepcopy(manifest))
        (output / "unbound.txt").write_text("unbound")
        self.rehash(output, deepcopy(manifest))
        with self.assertRaisesRegex(InvalidInput, "Unbound or extra"):
            adapter.verify_export(output)
        (output / "unbound.txt").unlink()
        changed = deepcopy(manifest)
        changed["format"] = "picross-target-export-v5"
        self.rehash(output, changed)
        with self.assertRaises(InvalidInput):
            adapter.verify_export(output)

    def test_default_cli_is_closed_and_explicit_inspect_export_are_available(self):
        _, _, _, archive, approval = self.early(choice="none")
        with self.assertRaisesRegex(InvalidInput, "explicit read-only"):
            adapter.export(archive, self.root / "default", approval_path=approval, **self.options)
        import contextlib
        import io
        for args in (["inspect", "--input", str(archive), "--approval", str(approval), "--allow-background"],
                     ["export", "--input", str(archive), "--approval", str(approval), "--allow-background",
                      "--output-dir", str(self.root / "cli-export"), "--name", "TEST ONLY", "--runtime-revision", "7",
                      "--stem", "background_test", "--save-slot", "same_slot", "--category-id", "voegel",
                      "--categories", str(self.options["categories_path"])]):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(adapter.main(args), 0)
            value = json.loads(stdout.getvalue())
            self.assertFalse(value["catalog_ready"] or value["registered"])
        self.assertTrue(adapter.verify_export(self.root / "cli-export")[1]["export_verified"])

    def test_only_declared_original_zip_has_the_larger_file_limit(self):
        # Small boundary values exercise the same limit branch, without a
        # permanent or transient hundreds-of-MiB binary fixture.
        root = self.root / "limits"
        (root / "input").mkdir(parents=True)
        (root / "input/package.zip").write_bytes(b"x" * 128)
        with patch.object(ap, "MAX_FILE", 64), patch.object(ap, "MAX_ZIP", 128):
            with self.assertRaisesRegex(InvalidInput, "too large"):
                ap.file_table(root, time.monotonic() + 10)
            self.assertIn("input/package.zip", ap.file_table(root, time.monotonic() + 10, original_zip="input/package.zip"))
            (root / "input/package.zip").write_bytes(b"x" * 129)
            with self.assertRaisesRegex(InvalidInput, "too large"):
                ap.file_table(root, time.monotonic() + 10, original_zip="input/package.zip")
            (root / "input/package.zip").write_bytes(b"x")
            (root / "other.zip").write_bytes(b"x" * 65)
            with self.assertRaisesRegex(InvalidInput, "too large"):
                ap.file_table(root, time.monotonic() + 10, original_zip="input/package.zip")

    def test_unlisted_special_file_is_rejected_without_opening_it(self):
        _, _, _, archive, approval = self.early(choice="none")
        output, _ = self.export(archive, approval)
        special = output / "unbound.fifo"
        if hasattr(os, "mkfifo"):
            os.mkfifo(special)
            with self.assertRaisesRegex(InvalidInput, "Special package files"):
                adapter.verify_export(output)
        else:
            # The Linux CI uses a real FIFO. Platforms without mkfifo still
            # exercise the rejected lstat type without a skip or blocking read.
            special.write_bytes(b"test special-file metadata")
            lstat = Path.lstat

            def special_stat(path, *args, **kwargs):
                info = lstat(path, *args, **kwargs)
                if path == special:
                    return os.stat_result((stat.S_IFIFO | 0o600, *tuple(info)[1:]))
                return info

            with patch.object(Path, "lstat", special_stat):
                with self.assertRaisesRegex(InvalidInput, "Special package files"):
                    adapter.verify_export(output)

    def test_rehashed_json_boolean_and_numeric_type_substitutions_fail(self):
        _, _, _, archive, approval = self.early(choice="none")
        output, manifest = self.export(archive, approval)
        inspection = load_json(output / "inspection.json")
        definition = load_json(output / manifest["definition"])
        for label, name, mutate in (
            ("manifest boolean", "manifest.json", lambda value: value.update(test_only=1)),
            ("mapping integer", "manifest.json", lambda value: value["color_mapping"].update(empty=False)),
            ("report boolean", "inspection.json", lambda value: value.update(export_verified=1)),
            ("report nested boolean", "inspection.json", lambda value: value["background"].update(ready=1)),
            ("tool versions type", "inspection.json", lambda value: value["tool"].update(versions=False)),
            ("tool versions keys", "inspection.json", lambda value: value["tool"]["versions"].pop("zlib")),
            ("tool version value", "inspection.json", lambda value: value["tool"]["versions"].update(pillow=True)),
            ("incomplete proof report", "inspection.json", lambda value: value.update(fresh_verification={"certified": True, "status": "solved"})),
            ("forged proof report", "inspection.json", lambda value: value["fresh_verification"].update(proof_verified=False)),
            ("extra proof report", "inspection.json", lambda value: value["fresh_verification"].update(trusted=True)),
            ("definition integer", manifest["definition"], lambda value: value.update(width=float(value["width"]))),
            ("definition nested integer", manifest["definition"], lambda value: value["reveal"].update(version=True)),
        ):
            with self.subTest(label=label):
                values = {"manifest.json": deepcopy(manifest), "inspection.json": deepcopy(inspection),
                          manifest["definition"]: deepcopy(definition)}
                mutate(values[name])
                for path, value in values.items():
                    write_json(output / path, value)
                self.rehash(output, values["manifest.json"])
                with self.assertRaises(InvalidInput):
                    adapter.verify_export(output)

    def test_fully_verified_v6_still_cannot_be_projected_or_registered(self):
        from tools.puzzle_production import content_registry, content_update
        _, _, _, archive, approval = self.early(choice="none")
        output, _ = self.export(archive, approval)
        manifest, report = adapter.verify_export(output)
        checkout = self.root / "unmodified-checkout"
        checkout.mkdir()
        before = adapter.hashes(output), list(checkout.iterdir())
        for apply in (False, True):
            with self.subTest(apply=apply), self.assertRaisesRegex(InvalidInput, "HP-I1b"):
                content_registry.registration(output, checkout, apply=apply)
            with self.subTest(update=apply), self.assertRaisesRegex(InvalidInput, "HP-I1b"):
                content_update.update(output, checkout, "0" * 64, apply=apply)
        with self.assertRaisesRegex(InvalidInput, "HP-I1b"):
            content_registry.export_entry(output, manifest, report, {"id": "voegel"})
        self.assertEqual(before, (adapter.hashes(output), list(checkout.iterdir())))

    def test_source_change_and_target_race_are_rejected_before_publication(self):
        _, _, _, archive, approval = self.early(choice="none")
        verify = export_v6.verify_background_export
        original = approval.read_bytes()

        def changed_source(*args, **kwargs):
            result = verify(*args, **kwargs)
            if kwargs.get("_pending"):
                approval.write_bytes(original + b" ")
            return result

        with patch.object(export_v6, "verify_background_export", side_effect=changed_source):
            with self.assertRaisesRegex(InvalidInput, "Source changed"):
                self.export(archive, approval, name="changed-source")
        self.assertFalse((self.root / "changed-source").exists())
        approval.write_bytes(original)
        publish = export_v6.background_io.publish_directory

        def occupied_target(stage, target):
            target.mkdir()
            (target / "foreign.txt").write_bytes(b"foreign bytes")
            publish(stage, target)

        with patch.object(export_v6.background_io, "publish_directory", side_effect=occupied_target):
            with self.assertRaisesRegex(InvalidInput, "appeared"):
                self.export(archive, approval, name="occupied-target")
        self.assertEqual((self.root / "occupied-target/foreign.txt").read_bytes(), b"foreign bytes")
        self.assertEqual({p.name for p in (self.root / "occupied-target").iterdir()}, {"foreign.txt"})

    def test_failed_export_keeps_foreign_stage_bytes_and_reports_remaining_path(self):
        _, _, _, archive, approval = self.early(choice="none")
        verify = export_v6.verify_background_export
        for kind in ("additional", "truncated"):
            observed = {}

            def changed_stage(stage, *args, **kwargs):
                result = verify(stage, *args, **kwargs)
                if kwargs.get("_pending"):
                    path = stage / ("foreign.txt" if kind == "additional" else "usage.txt")
                    raw = b"foreign bytes" if kind == "additional" else path.read_bytes()[:8]
                    path.write_bytes(raw)
                    observed.update(path=path, raw=raw, remaining=stage.parent)
                    raise InvalidInput("Synthetic failure after foreign change")
                return result

            with self.subTest(kind=kind), patch.object(export_v6, "verify_background_export", side_effect=changed_stage):
                with self.assertRaises(OSError) as failure:
                    self.export(archive, approval, name="foreign-stage-" + kind)
            self.assertIn(str(observed["remaining"]), str(failure.exception))
            self.assertEqual(observed["path"].read_bytes(), observed["raw"])
            self.assertFalse((self.root / ("foreign-stage-" + kind)).exists())


if __name__ == "__main__":
    unittest.main()
