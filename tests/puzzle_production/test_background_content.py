"""Synthetic PB-H read-only content admission; no real assets or catalog writes."""
from copy import deepcopy
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from PIL import Image

from tools.puzzle_production import background_assets as assets, background_package, certification, images
from tools.puzzle_production import palette_gate, target_adapter as adapter
from tools.puzzle_production.authoring_package import file_hash, open_package
from tools.puzzle_production.contract import Budget, InvalidInput, InvalidProof, load_json, validate_logic, write_json
from tools.puzzle_production.za1_fixtures import ROOT, approve, isolated_checkout, make, seal
from tests.puzzle_production.background_fixtures import BackgroundFixture, file_ref, put


def stored(root, ref, storage="package"):
    return {"storage": storage, "root": root, "ref": deepcopy(ref)}


class BackgroundContentTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="pb-h-content-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.counter = 0

    def content(self, *, mode="mono", colors=None, name="package"):
        target = self.root / name
        original = images.import_image

        def recolor(source, design_path, output, *args, **kwargs):
            design = load_json(design_path)
            if colors:
                mapping = {tuple(bytes.fromhex(e["rgb"][1:])): tuple(bytes.fromhex(rgb[1:]))
                           for e, rgb in zip(design["palette"], colors)}
                with Image.open(source) as image:
                    image.load()
                    changed = image.copy()
                for y in range(changed.height):
                    for x in range(changed.width):
                        old = changed.getpixel((x, y))
                        changed.putpixel((x, y), mapping.get(old, old))
                changed.save(source)
                for entry, rgb in zip(design["palette"], colors):
                    entry["rgb"] = rgb
                write_json(design_path, design)
            return original(source, design_path, output, *args, **kwargs)

        with patch("tools.puzzle_production.za1_fixtures.import_image", side_effect=recolor):
            make(target, "pz-hp-synthetic", 3, 3, mode)
        return target

    def background(self, target, *, choice="offered", ready=False, state="raster_ready", presented=None):
        self.counter += 1
        h = load_json(target / "handoff.json")
        fixture = BackgroundFixture(self.root / ("background-" + str(self.counter)), assets.describe(),
                                    none=choice == "none")
        fixture.manifest["puzzle_id"] = fixture.decision["puzzle_id"] = h["puzzle_id"]
        fixture.decision["presented_package"] = deepcopy(presented)
        if choice != "none":
            fixture.manifest["context"].update(
                reveal=put(fixture.source, "context/reveal.png", (target / h["reveal"]["file"]).read_bytes()),
                reveal_approval=put(fixture.source, "context/reveal-approval.json",
                                    (target / h["reveal"]["approval"]).read_bytes()))
            if ready:
                norm = {"file": "docs/PUZZLE_QUALITY.md", "contract": "1.0", "document_revision": 9,
                        "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                        "sha256": file_hash(ROOT / "docs/PUZZLE_QUALITY.md")}
                candidate = fixture.manifest["candidates"][0]
                candidate["review"] = {criterion: {
                    "result": "erfüllt", "reason": "TEST ONLY synthetic judgment.",
                    "method": "Synthetic test construction", "norm": deepcopy(norm),
                    "actor": "TEST ONLY", "timestamp_utc": "2026-01-01T12:00:00Z",
                    "evidence": [deepcopy(candidate["original"])]}
                    for criterion in ("Q-HG01", "Q-HG02", "Q-HG03", "Q-HG04")}
        fixture.refresh()
        shutil.copytree(fixture.source, target / "background")
        binding = {"manifest": stored("background", fixture.request["manifest"]),
                   "decision": None if choice == "offered" else stored("background", fixture.request["decision"]),
                   "derivation": None, "history": None}
        if choice == "offered":
            (target / "background/decisions/d01.json").unlink()
        elif ready:
            result = assets.derive(fixture.request, fixture.source, fixture.output)
            self.assertIn(result["status"], ("derived", "none"), result)
            shutil.copytree(fixture.target, target / "outputs/background")
            binding["derivation"] = stored("outputs", file_ref(target / "outputs", "background/derivation.json"))
        # An explicitly synthetic new-generation fixture, never a production
        # snapshot relabel or a writer for previously sealed user inputs.
        (target / "rulebook.md").write_text("# PB-H synthetic fixture\n\n"
            "**Version 0.7.0 · Dokumentrevision 1 · TEST ONLY**\n", encoding="utf-8")
        h.update(format="picross-authoring-handoff-v3", state=state, background=binding,
                 rulebook={"version": "0.7.0", "file": "rulebook.md", "sha256": file_hash(target / "rulebook.md")})
        for gate, field in (("background_choice", "decision"), ("background_asset", "derivation")):
            ref = binding[field]
            h["gates"][gate] = "pass" if ref is not None else "pending"
            h["gate_evidence"][gate] = ref["root"] + "/" + ref["ref"]["file"] if ref is not None else None
        seal(target, h)
        return fixture, h

    def inspect(self, source, approval=None, *, manual=None, exception=None, external=None):
        with open_package(source, allow_background=True, allow_manual_review=manual is not None,
                          external_root=external) as package:
            return adapter.inspect(package, approval, allow_background=True,
                                   manual_authorization=manual, palette_exception=exception)[0]

    def archive(self, source, name="original.zip"):
        target = self.root / name
        with zipfile.ZipFile(target, "w") as archive:
            for path in sorted(source.rglob("*")):
                if path.is_file():
                    archive.write(path, path.relative_to(source).as_posix())
        return target

    def approval(self, source, archive, *, background=None, name="approval.json"):
        h = load_json(source / "handoff.json")
        if background is None:
            with open_package(archive, allow_background=True) as package:
                background = package.background
        decision, derived = background["decision"], background["derivation"]
        path = self.root / name
        write_json(path, {"format": "picross-editorial-approval-v2", "actor": "TEST ONLY",
            "timestamp_utc": "2026-11-09T12:00:00Z", "statement": "Synthetic explicit final statement, not owner acceptance.",
            "puzzle_id": h["puzzle_id"], "revision": h["revision"], "handoff_sha256": file_hash(source / "handoff.json"),
            "inventory_sha256": h["inventory"]["sha256"], "original_zip_sha256": file_hash(archive),
            "selection": {"variant": h["candidate"]["variant"], "matrix_hash": h["candidate"]["matrix_hash"],
                          "logic_hash": h["candidate"]["logic_hash"],
                          "reveal": {k: h["reveal"][k] for k in ("file", "sha256")}},
            "background": {**{k: background["binding"][k] for k in ("manifest", "decision", "derivation")},
                "outcome": decision["outcome"], "candidate_id": decision["candidate_id"],
                "original": decision["original"], "output": derived["output"],
                "profile_sha256": derived["profile_sha256"]}, "test_only": True})
        return path

    def review(self, target):
        report = self.inspect(target)
        assessment = report["palette_gate"]["assessment"]
        write_json(target / "palette-review.json", {"format": palette_gate.VISUAL,
            "puzzle_id": report["puzzle_id"], "revision": report["package_revision"],
            "matrix_hash": report["selection"]["matrix_hash"], "logic_hash": report["selection"]["logic_hash"],
            "palette_sha256": assessment["palette_sha256"], "criteria": {criterion: {
                "result": "erfüllt", "accepted": False, "actor": "TEST ONLY",
                "timestamp_utc": "2026-11-09T12:00:00Z", "statement": "Synthetic palette judgment.",
                "reason": "Test-only boundary evidence.",
                "evidence": [{"file": "evidence.txt", "sha256": file_hash(target / "evidence.txt")}]}
                for criterion in palette_gate.CRITERIA}})
        h = load_json(target / "handoff.json")
        h["palette_review"] = {"file": "palette-review.json", "sha256": file_hash(target / "palette-review.json")}
        seal(target, h)

    def test_raster_ready_keeps_open_choice_separate_and_inspection_is_read_only(self):
        target = self.content()
        self.background(target)
        archive = self.archive(target)
        before = adapter.hashes(target), archive.read_bytes()
        report = self.inspect(archive)
        self.assertEqual(report["format"], adapter.BACKGROUND_INSPECTION)
        self.assertTrue(report["technical"])
        self.assertEqual((report["original_state"], report["effective_state"]), ("raster_ready", "raster_ready"))
        self.assertEqual((report["background"]["status"], report["background"]["ready"]), ("offered", False))
        self.assertTrue(any(b.startswith("background_choice:") for b in report["blockers"]))
        self.assertFalse(report["catalog_ready"] or report["integration_ready"] or report["editorial_approved"])
        self.assertEqual(before, (adapter.hashes(target), archive.read_bytes()))
        with self.assertRaisesRegex(InvalidInput, "explicit read-only"), open_package(archive):
            pass
        with open_package(archive, allow_background=True) as package:
            with self.assertRaisesRegex(InvalidInput, "explicit read-only"):
                adapter.inspect(package)
            with self.assertRaisesRegex(InvalidInput, "catalog integration"):
                adapter.categorize(report, {}, "unused")

    def test_content_ready_requires_background_readiness_and_preserves_old_hard_gates(self):
        target = self.content()
        _, h = self.background(target)
        h["state"] = "content_ready"
        seal(target, h)
        with self.assertRaisesRegex(InvalidInput, "readiness"):
            self.inspect(target)
        h["state"] = "raster_ready"
        for gate in ("logic", "provenance", "motif", "frame", "difficulty", "reveal_consistency"):
            changed = deepcopy(h)
            changed["gates"][gate] = "fail"
            seal(target, changed)
            with self.subTest(gate=gate), self.assertRaisesRegex(InvalidInput, "content gate"):
                self.inspect(target)
        h["content_blockers"] = ["Unresolved raster contradiction"]
        seal(target, h)
        with self.assertRaisesRegex(InvalidInput, "content blockers"):
            self.inspect(target)

    def test_rehashed_bad_proof_and_incomplete_certification_are_rejected(self):
        target = self.content()
        _, h = self.background(target)
        bundle = target / "production/import"
        manifest = load_json(bundle / "manifest.json")
        for filename, mutation in (("area-proof.json", {"logic_hash": "0" * 64}),
                                   ("area-result.json", {"certified": False, "proof_verified": False})):
            original = (bundle / filename).read_bytes()
            value = load_json(bundle / filename)
            value.update(mutation)
            write_json(bundle / filename, value)
            manifest["files"][filename] = file_hash(bundle / filename)
            write_json(bundle / "manifest.json", manifest)
            seal(target, h)
            with self.subTest(filename=filename), self.assertRaises((InvalidInput, InvalidProof)):
                self.inspect(target)
            (bundle / filename).write_bytes(original)
            manifest["files"][filename] = file_hash(bundle / filename)
            write_json(bundle / "manifest.json", manifest)

    def test_paired_baseline_profile_and_difficulty_guarantees_survive_new_version(self):
        from test_paired_production import package as paired_package
        target = self.root / "paired"
        paired_package(target)
        _, h = self.background(target)
        report = self.inspect(target)
        self.assertTrue(report["technical"])
        self.assertTrue(report["deduction"]["assessment"]["r4_required"])
        self.assertEqual(report["difficulty"]["level"], "L5")
        difficulty = load_json(target / "difficulty.json")
        for values in ({"profile_hash": "0" * 64}, {"method": "picross-difficulty-0.1"},
                       {"level": "L4", "plausible_range": ["L4", "L5"]}):
            write_json(target / "difficulty.json", {**difficulty, **values})
            seal(target, h)
            with self.subTest(values=values), self.assertRaises(InvalidInput):
                self.inspect(target)
        write_json(target / "difficulty.json", difficulty)
        for filename, values in (("area-baseline-proof.json", {"status": "aborted", "reason": "work_limit"}),
                                 ("area-assessment.json", {"r4_required": False})):
            path = target / "paired-import" / filename
            original = path.read_bytes()
            write_json(path, {**load_json(path), **values})
            manifest_path = path.parent / "manifest.json"
            manifest = load_json(manifest_path)
            manifest["files"][filename] = file_hash(path)
            write_json(manifest_path, manifest)
            seal(target, h)
            with self.subTest(filename=filename), self.assertRaises((InvalidInput, InvalidProof)):
                self.inspect(target)
            path.write_bytes(original)
            manifest["files"][filename] = file_hash(path)
            write_json(manifest_path, manifest)
        h["candidate"]["certification"]["max_pair_work"] += 1
        seal(target, h)
        with self.assertRaisesRegex(InvalidInput, "profile binding"):
            self.inspect(target)

    def test_palette_visual_negative_and_stale_assessment_cannot_be_skipped(self):
        for negative in (False, True):
            target = self.content(mode="color", colors=["#447799", "#487b9d"] if negative else None,
                                  name="color-" + str(negative))
            self.background(target)
            self.assertFalse(self.inspect(target)["technical"])
            self.review(target)
            report = self.inspect(target)
            self.assertEqual(report["technical"], not negative)
            self.assertEqual(report["palette_gate"]["assessment"]["status"], "negative" if negative else "positive")
            write_json(target / "palette.json", {**report["palette_gate"]["assessment"], "source_fingerprint": "0" * 64})
            h = load_json(target / "handoff.json")
            h["palette_assessment"] = {"file": "palette.json", "sha256": file_hash(target / "palette.json")}
            seal(target, h)
            with self.assertRaisesRegex(InvalidInput, "Stale"):
                self.inspect(target)

    def test_negative_palette_exception_still_needs_exact_actual_final_approval(self):
        target = self.content(mode="color", colors=["#447799", "#487b9d"])
        self.background(target, choice="none", ready=True, state="content_ready")
        self.review(target)
        archive = self.archive(target)
        approval = self.approval(target, archive)
        report = self.inspect(archive, approval)
        self.assertFalse(report["technical"])
        palette = report["palette_gate"]
        value = {"format": palette_gate.EXCEPTION, "binding": palette["binding"],
                 "negative_pairs": palette["assessment"]["negative_pairs"], "actor": "TEST ONLY",
                 "timestamp_utc": "2026-11-09T12:00:00Z", "statement": "Synthetic exception statement.",
                 "reason": "Test-only negative pair acceptance.", "approval_sha256": file_hash(approval),
                 "test_only": True}
        path = self.root / "palette-exception.json"
        write_json(path, value)
        report = self.inspect(archive, approval, exception=path)
        self.assertTrue(report["technical"])
        self.assertEqual(report["palette_gate"]["assessment"]["status"], "negative")
        self.assertFalse(report["integration_ready"])
        for change in ({"negative_pairs": []}, {"approval_sha256": "0" * 64}, {"test_only": False}):
            write_json(path, {**value, **change})
            with self.subTest(change=change), self.assertRaises(InvalidInput):
                self.inspect(archive, approval, exception=path)
        write_json(path, value)
        with self.assertRaisesRegex(InvalidInput, "actual final approval"):
            self.inspect(archive, exception=path)

    def test_supplied_selected_and_none_approval_bind_actual_original_and_remain_read_only(self):
        for choice in ("selected", "none"):
            target = self.content(name=choice)
            self.background(target, choice=choice, ready=True, state="content_ready")
            archive = self.archive(target, choice + ".zip")
            approval = self.approval(target, archive, name=choice + "-approval.json")
            original = load_json(approval)
            before = adapter.hashes(target), archive.read_bytes(), approval.read_bytes()
            report = self.inspect(archive, approval)
            self.assertTrue(report["technical"] and report["editorial_approved"])
            self.assertEqual(report["effective_state"], "editorially_approved")
            self.assertFalse(report["catalog_ready"] or report["integration_ready"])
            self.assertEqual(before, (adapter.hashes(target), archive.read_bytes(), approval.read_bytes()))
            for mutate in (lambda a: a.update(original_zip_sha256="0" * 64),
                           lambda a: a.update(handoff_sha256="0" * 64),
                           lambda a: a.update(inventory_sha256="0" * 64),
                           lambda a: a.update(test_only=False),
                           lambda a: a["selection"].update(matrix_hash="0" * 64),
                           lambda a: a["background"].update(profile_sha256="0" * 64),
                           lambda a: a["background"].update(candidate_id="wrong"),
                           lambda a: a["background"].update(output={"file": "background.png", "bytes": 1, "sha256": "0" * 64})):
                value = deepcopy(original)
                mutate(value)
                write_json(approval, value)
                with self.assertRaises(InvalidInput):
                    self.inspect(archive, approval)
            write_json(approval, original)
            with self.assertRaisesRegex(InvalidInput, "original ZIP"):
                self.inspect(target, approval)

    def test_original_early_choice_can_retain_its_historical_presented_package(self):
        target = self.content()
        earlier = self.archive(target, "earlier.zip")
        h = load_json(target / "handoff.json")
        binding = {"puzzle_id": h["puzzle_id"], "revision": h["revision"],
                   "original_zip_sha256": file_hash(earlier), "handoff_sha256": file_hash(target / "handoff.json"),
                   "inventory_sha256": h["inventory"]["sha256"]}
        h["revision"] = "r02"
        seal(target, h)
        self.background(target, choice="none", ready=True, state="content_ready", presented=binding)
        archive = self.archive(target)
        approval = self.approval(target, archive)
        report = self.inspect(archive, approval)
        self.assertTrue(report["editorial_approved"])
        self.assertEqual(report["package_revision"], "r02")

    def test_existing_external_choice_is_read_against_original_raster_package(self):
        target = self.content()
        fixture, h = self.background(target, ready=True)
        archive = self.archive(target)
        fixture.decision["presented_package"] = {"puzzle_id": h["puzzle_id"], "revision": h["revision"],
            "original_zip_sha256": file_hash(archive), "handoff_sha256": file_hash(target / "handoff.json"),
            "inventory_sha256": h["inventory"]["sha256"]}
        fixture.refresh_decision()
        result = assets.derive(fixture.request, fixture.source, fixture.output)
        self.assertEqual(result["status"], "derived", result)
        binding = {"manifest": deepcopy(h["background"]["manifest"]),
                   "decision": stored("source", fixture.request["decision"], "external"),
                   "derivation": stored("output", file_ref(fixture.output, "derived/bg01/derivation.json"), "external"),
                   "history": None}
        with open_package(archive, allow_background=True) as package:
            background = background_package.validate_external(package.root, h, binding, external_root=fixture.root)
        approval = self.approval(target, archive, background=background)
        before = archive.read_bytes(), adapter.hashes(fixture.root)
        report = self.inspect(archive, approval, external=fixture.root)
        self.assertEqual((report["original_state"], report["effective_state"]), ("raster_ready", "editorially_approved"))
        self.assertEqual(before, (archive.read_bytes(), adapter.hashes(fixture.root)))
        with self.assertRaisesRegex(InvalidInput, "external_root"):
            self.inspect(archive, approval)

    def test_paired_manual_content_still_requires_exact_manual_authorization(self):
        from test_manual_adapter import ManualAdapterTests
        from test_paired_production import difficulty
        case = ManualAdapterTests()
        case.setUp()
        self.addCleanup(case.doCleanups)
        target = case.package
        h = load_json(target / "handoff.json")
        puzzle = validate_logic(load_json(target / "manual/logic.json"))
        cfg = certification.configuration(puzzle, "paired-lines-mono")
        _, checked = certification.produce(puzzle, target / "manual/certificate", "", cfg, Budget())
        checked["format"] = "picross-result-v1"
        write_json(target / "manual/certificate/result.json", checked)
        plan = load_json(target / "manual/plan.json")
        plan.update(format="picross-manual-edit-plan-v2", certification=cfg)
        write_json(target / "manual/plan.json", plan)
        raw = load_json(target / "manual/candidate.json")
        raw.update(format="picross-manual-candidate-v2", plan_sha256=file_hash(target / "manual/plan.json"))
        write_json(target / "manual/candidate.json", raw)
        difficulty(target, h, h["candidate"]["proof"])
        seal(target, h)
        self.background(target)
        case.authorize()
        report = self.inspect(target, manual=case.auth)
        self.assertTrue(report["technical"])
        self.assertIn("deduction", report)
        with self.assertRaisesRegex(InvalidInput, "manual authorization"):
            self.inspect(target)
        h = load_json(target / "handoff.json")
        h["blockers"] = ["Unresolved separate content requirement"]
        seal(target, h)
        case.authorize()
        with self.assertRaisesRegex(InvalidInput, "content blockers"):
            self.inspect(target, manual=case.auth)
        h["blockers"] = []
        h["gates"]["provenance"] = "fail"
        seal(target, h)
        case.authorize()
        with self.assertRaisesRegex(InvalidInput, "content gate"):
            self.inspect(target, manual=case.auth)

    def test_old_export_verify_and_registry_entry_cannot_admit_v3_inputs(self):
        target = self.content()
        h = load_json(target / "handoff.json")
        (target / "rulebook.md").write_text("**Version 0.6.0 · TEST ONLY**\n", encoding="utf-8")
        h["rulebook"] = {"version": "0.6.0", "file": "rulebook.md", "sha256": file_hash(target / "rulebook.md")}
        seal(target, h)
        approval = self.root / "old-approval.json"
        approve(target, approval)
        output = self.root / "old-export"
        options = {"name": "TEST ONLY", "revision": 1, "stem": "background_test", "save_slot": "background_test",
                   "category_id": "voegel", "categories_path": ROOT / "tests/puzzle_production/fixtures/catalog/categories.json"}
        adapter.export(target, output, approval_path=approval, **options)
        self.background(target)
        with self.assertRaisesRegex(InvalidInput, "explicit read-only"):
            adapter.export(target, self.root / "forbidden-export", **options)
        self.assertFalse((self.root / "forbidden-export").exists())
        shutil.rmtree(output / "input")
        shutil.copytree(target, output / "input")
        manifest = load_json(output / "manifest.json")
        manifest["files"] = {k: v for k, v in adapter.hashes(output).items() if k != "manifest.json"}
        write_json(output / "manifest.json", manifest)
        before = adapter.hashes(output)
        with self.assertRaisesRegex(InvalidInput, "explicit read-only"):
            adapter.verify_export(output)
        from tools.puzzle_production.content_registry import registration
        checkout = isolated_checkout(self.root / "checkout")
        checkout_before = adapter.hashes(checkout)
        with self.assertRaises(InvalidInput):
            registration(output, checkout, apply=True)
        self.assertEqual(checkout_before, adapter.hashes(checkout))
        self.assertEqual(before, adapter.hashes(output))


if __name__ == "__main__":
    unittest.main()
