"""ZA-1 contracts: fresh reconstruction, approval selection and transactional adoption."""
import copy
import json
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from PIL import Image

from tools.puzzle_production import authoring_package as boundary
from tools.puzzle_production.authoring_package import open_package
from tools.puzzle_production.content_registry import registration, check_checkout, projection, validate
from tools.puzzle_production.contract import InvalidInput, InvalidProof, Aborted, digest, load_json, write_json
from tools.puzzle_production.images import file_hash
from tools.puzzle_production.target_adapter import inspect, export, verify_export, validate_reveal
from tools.puzzle_production.za1_fixtures import FIXTURES, ROOT, approve, isolated_checkout, make, seal


class TargetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def package(self, name="direct-mono"):
        p = self.root / name
        shutil.copytree(FIXTURES / name, p)
        return p

    def inspect(self, p):
        with open_package(p) as opened:
            return inspect(opened)[0]

    def export(self, p, stem=None, slot=None, dest="export"):
        h = load_json(p / "handoff.json")
        approval = self.root / (p.name + "-approval.json")
        approve(p, approval)
        out = self.root / dest
        export(p, out, name="TEST ONLY", revision=7, stem=stem or h["puzzle_id"],
               save_slot=slot or "slot_"+h["puzzle_id"], approval_path=approval)
        return out

    def reseal(self, p):
        seal(p, load_json(p / "handoff.json"))

    def snapshot(self, root):
        return {p.relative_to(root).as_posix(): p.read_bytes() if p.is_file() else None
                for p in root.rglob("*")}

    def test_manifest_reserved_save_slots_block_api_and_cli_without_writes(self):
        out = self.export(self.package())
        original = load_json(out / "manifest.json")
        self.assertTrue(verify_export(out)[1]["catalog_ready"])
        checkout = isolated_checkout(self.root / "checkout")
        before_checkout = self.snapshot(checkout)
        for slot in ("con", "nul", "prn", "aux", "com1", "lpt9"):
            changed = copy.deepcopy(original)
            changed["save_slot"] = slot  # Only this unbound manifest field changes.
            write_json(out / "manifest.json", changed)
            before_export = self.snapshot(out)
            for command in ("verify-export", "plan", "register"):
                with self.subTest(slot=slot, command=command):
                    with self.assertRaisesRegex(InvalidInput, "Unsafe package path"):
                        if command == "verify-export":
                            verify_export(out)
                        else:
                            registration(out, checkout, apply=command == "register")
                    if slot == "con":
                        args = [sys.executable, "-B", "-m", "tools.puzzle_production.target_adapter",
                                command, "--export", str(out)]
                        if command != "verify-export":
                            args += ["--checkout", str(checkout)]
                        result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=60)
                        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                        self.assertEqual(json.loads(result.stdout), {
                            "status": "blocked", "catalog_ready": False, "registered": False,
                            "error": "Unsafe package path"})
                    self.assertEqual(self.snapshot(checkout), before_checkout)
                    self.assertEqual(self.snapshot(out), before_export)

    def test_similar_legal_save_slots_export_register_and_repeat(self):
        p = self.package()
        for slot in ("con_test", "com10"):
            with self.subTest(slot=slot):
                out = self.export(p, slot=slot, dest="export-" + slot)
                self.assertEqual(verify_export(out)[0]["save_slot"], slot)
                checkout = isolated_checkout(self.root / ("checkout-" + slot))
                self.assertEqual(registration(out, checkout)["status"], "planned")
                self.assertEqual(registration(out, checkout, apply=True)["status"], "registered")
                self.assertEqual(check_checkout(checkout, replay=True)["entries"][-1]["save_slot"], slot)
                self.assertEqual(registration(out, checkout, apply=True)["status"], "no-op")

    def test_registered_reserved_save_slots_rejected_without_checkout_changes(self):
        out = self.export(self.package())
        checkout = isolated_checkout(self.root / "checkout")
        registration(out, checkout, apply=True)
        original = check_checkout(checkout, replay=True)
        for slot in ("con", "nul", "prn", "aux", "com1", "lpt9"):
            with self.subTest(slot=slot):
                changed = copy.deepcopy(original)
                changed["entries"][-1]["save_slot"] = slot
                with self.assertRaisesRegex(InvalidInput, "Unsafe package path"):
                    validate(changed)
                write_json(checkout / "content/registry.json", changed)
                # Keep projection consistent, so stale runtime data cannot mask B-01.
                write_json(checkout / "game/data/registry.json", projection(changed))
                before = self.snapshot(checkout)
                for replay in (False, True):
                    with self.assertRaisesRegex(InvalidInput, "Unsafe package path"):
                        check_checkout(checkout, replay=replay)
                    self.assertEqual(self.snapshot(checkout), before)

    def test_recovery_rejects_reserved_journal_slot_before_mutation(self):
        from tools.puzzle_production.content_registry import recover, REGISTRY, RUNTIME
        out = self.export(self.package())
        checkout = isolated_checkout(self.root / "checkout")
        with self.assertRaises(InterruptedError):
            registration(out, checkout, apply=True, fail_step="crash-index")
        lock = checkout / "content/.registration-pending.json"
        journal = load_json(lock)
        changed = json.loads(journal["new"][REGISTRY])
        changed["entries"][-1]["save_slot"] = "con"
        journal["new"][REGISTRY] = json.dumps(changed)
        journal["new"][RUNTIME] = json.dumps(projection(changed))
        write_json(lock, journal)
        before = self.snapshot(checkout)
        with self.assertRaisesRegex(InvalidInput, "Unsafe package path"):
            recover(checkout)
        self.assertEqual(self.snapshot(checkout), before)

    def test_four_origins_modes_and_orientations_export_and_recheck(self):
        for i, name in enumerate(("direct-mono", "direct-color", "repair-mono", "repair-color")):
            with self.subTest(name=name):
                p = self.package(name)
                before = {f.relative_to(p): file_hash(f) for f in p.rglob("*") if f.is_file()}
                report = self.inspect(p)
                self.assertTrue(report["technical"])
                self.assertEqual(report["blockers"], ["final_editorial: missing bound human final approval"])
                with self.assertRaisesRegex(InvalidInput, "final_editorial"):
                    export(p, self.root / "blocked", name="TEST ONLY", revision=1, stem="test", save_slot="slot")
                self.assertFalse((self.root / "blocked").exists())
                out = self.export(p, dest=f"export-{i}")
                m, checked = verify_export(out)
                d = load_json(out / m["definition"])
                self.assertEqual(d["id"], report["puzzle_id"])
                self.assertEqual(d["revision"], 7)  # r01 is NOT runtime revision 1.
                self.assertEqual(d["width"], report["width"])
                self.assertEqual(d["height"], report["height"])
                self.assertEqual([e["id"] for e in d["palette"]], list(range(1,len(d["palette"])+1)))
                if "color" in name: self.assertEqual(len(set(v for row in d["solution"] for v in row)-{0}),2)
                self.assertEqual(file_hash(out / m["reveal"]), report["selection"]["reveal"]["sha256"])
                self.assertEqual(before, {f.relative_to(p): file_hash(f) for f in p.rglob("*") if f.is_file()})

    def test_garlic_compact_original_handoff_and_missing_final_approval(self):
        source = ROOT / "tests/puzzle_production/fixtures/garlic-r03-reference.zip"
        report = self.inspect(source)
        self.assertEqual(report["original_zip_sha256"], "7013d5b29a0dda5ad9a5047730a1e71b4d06596aa284ee8a3cbdad9184dc23f1")
        self.assertEqual(report["handoff_sha256"], "8411cb079ac321b975cc51c01aa47f935fe492aee569060046aee917d594c06c")
        self.assertEqual(report["fresh_verification"]["candidates"], 3)
        self.assertTrue(report["technical"])
        self.assertFalse(report["catalog_ready"])
        with self.assertRaisesRegex(InvalidInput, "final_editorial"):
            export(source, self.root / "blocked", name="Knoblauch", revision=1, stem="garlic", save_slot="garlic")
        self.assertFalse((self.root / "blocked").exists())

    def test_rehashed_mutated_sources_matrix_clues_proof_and_status_rejected(self):
        attacks = ("source", "normalized", "matrix", "logic", "proof", "status", "reveal", "approval", "derivation", "parameter", "gate", "difficulty")
        for attack in attacks:
            with self.subTest(attack=attack), tempfile.TemporaryDirectory(dir=self.root) as temp:
                p = Path(temp) / "package"
                shutil.copytree(FIXTURES / "direct-mono", p)
                bundle = p / "production/import"
                filename = None
                if attack in ("source", "normalized"):
                    filename = "original.png" if attack == "source" else "normalized.png"
                    with Image.open(bundle / filename) as im:
                        changed = im.copy()
                    changed.putpixel((0, 0), (20, 20, 20) if changed.mode == "RGB" else (20, 20, 20, 255))
                    changed.save(bundle / filename)
                elif attack in ("matrix", "logic", "proof", "status"):
                    filename = {"matrix": "area-candidate.json", "logic": "area-logic.json", "proof": "area-proof.json", "status": "area-result.json"}[attack]
                    raw = load_json(bundle / filename)
                    if attack == "matrix": raw["matrix"][0][0] = "ink"
                    if attack == "logic": raw["row_clues"][0][0]["length"] = 1
                    if attack == "proof": raw["steps"][0]["changes"][0]["after"] = ["empty"]
                    if attack == "status": raw.update(status="aborted", certified=False, proof_verified=False)
                    write_json(bundle / filename, raw)
                elif attack == "reveal":
                    Image.new("RGB", (24, 16), "pink").save(p / "reveals/reveal.png")
                    h = load_json(p / "handoff.json")
                    h["reveal"]["sha256"] = file_hash(p / "reveals/reveal.png")
                    write_json(p / "handoff.json", h)
                elif attack in ("approval", "derivation"):
                    raw = load_json(p / "motif-approval.json")
                    raw["sha256" if attack == "approval" else "derived_from_reveal_sha256"] = "0"*64
                    write_json(p / "motif-approval.json", raw)
                elif attack == "parameter":
                    h = load_json(p / "handoff.json"); h["approved_parameters"][0]["width"] = 5
                    write_json(p / "handoff.json", h)
                elif attack == "gate":
                    h = load_json(p / "handoff.json"); h["gate_evidence"]["visual"] = "missing"
                    write_json(p / "handoff.json", h)
                elif attack == "difficulty":
                    raw = load_json(p / "difficulty.json"); raw["logic_hash"] = "0"*64
                    write_json(p / "difficulty.json", raw)
                if filename:
                    m = load_json(bundle / "manifest.json"); m["files"][filename] = file_hash(bundle / filename)
                    write_json(bundle / "manifest.json", m)
                self.reseal(p)  # Matching outer hashes are insufficient.
                with self.assertRaises((InvalidInput, InvalidProof)):
                    self.inspect(p)

    def test_repair_selection_reference_parents_protection_and_original_abort(self):
        for attack in ("selection", "reference", "parent", "mask", "abort", "proof", "plan"):
            with self.subTest(attack=attack), tempfile.TemporaryDirectory(dir=self.root) as temp:
                p = Path(temp) / "p"; shutil.copytree(FIXTURES / "repair-color", p)
                bundle = p / "production/repair"
                raw = load_json(bundle / "repair.json")
                if attack == "selection":
                    h = load_json(p / "handoff.json"); h["candidate"]["variant"] = "area"
                    write_json(p / "handoff.json", h)
                elif attack == "reference": raw["reference"]["manifest_sha256"] = "0"*64
                elif attack == "parent": raw["history"][-1]["parent"] = 99
                else:
                    filename = {"mask":"plan.json", "abort":"result.json", "proof":"final-proof.json", "plan":"plan.json"}[attack]
                    data = load_json(bundle / filename)
                    if attack == "mask": data["mask"] = [[True]*6 for _ in range(4)]
                    if attack == "abort": data.update(status="aborted", certified=False, reason="final_verification_aborted")
                    if attack == "proof": data["final_domains"][0][0] = ["empty"]
                    if attack == "plan": data["reference"]["variant"] = "other"
                    write_json(bundle / filename, data)
                    raw["files"][filename] = file_hash(bundle / filename)
                raw["id"] = digest({k:v for k,v in raw.items() if k not in ("id","files")})
                write_json(bundle / "repair.json", raw)
                self.reseal(p)
                with self.assertRaises((InvalidInput, InvalidProof)):
                    self.inspect(p)

    def test_final_approval_requires_original_handoff_and_exact_selection(self):
        p = self.package()
        a = self.root / "approval.json"; approve(p, a)
        original = load_json(a)
        for field in ("actor", "timestamp_utc", "statement", "puzzle_id", "revision", "handoff_sha256", "inventory_sha256", "selection", "test_only"):
            bad = copy.deepcopy(original)
            bad[field] = {} if field == "selection" else False if field == "test_only" else "" if field in ("actor", "statement") else "wrong"
            write_json(a, bad)
            with self.subTest(field=field), open_package(p) as opened, self.assertRaises(InvalidInput):
                inspect(opened, a)
        write_json(a, original)
        with open_package(p) as opened:
            self.assertTrue(inspect(opened, a)[0]["catalog_ready"])

    def test_registration_two_ids_explicit_slots_no_op_collisions_rollback(self):
        p = self.package(); out = self.export(p)
        checkout = isolated_checkout(self.root / "checkout")
        before = (checkout / "content/registry.json").read_bytes()
        for step in ("files", "index"):
            with self.assertRaises(OSError): registration(out, checkout, apply=True, fail_step=step)
            self.assertEqual((checkout / "content/registry.json").read_bytes(), before)
            check_checkout(checkout)
            self.assertFalse((checkout / "game/data/content/pz-test-direct-mono.json").exists())
        from tools.puzzle_production.content_registry import recover
        for step in ("crash","crash-index"):
            with self.assertRaises(InterruptedError): registration(out, checkout, apply=True, fail_step=step)
            with self.assertRaisesRegex(InvalidInput, "Interrupted"): check_checkout(checkout)
            target = checkout / "game/data/content/pz-test-direct-mono.json"
            saved = target.read_bytes()
            target.write_bytes(b"foreign modification")
            with self.assertRaisesRegex(InvalidInput,"changed"): recover(checkout)
            self.assertEqual(target.read_bytes(),b"foreign modification")
            target.write_bytes(saved)
            self.assertEqual(recover(checkout)["status"], "rolled-back")
            self.assertEqual((checkout / "content/registry.json").read_bytes(), before)
        plan = registration(out, checkout)
        self.assertFalse(plan["registered"])
        self.assertEqual((checkout / "content/registry.json").read_bytes(), before)
        registration(out, checkout, apply=True)
        self.assertEqual(registration(out, checkout, apply=True)["status"], "no-op")
        p2 = self.package("direct-color")
        collision = self.export(p2, slot="slot_pz-test-direct-mono", dest="collision")
        with self.assertRaisesRegex(InvalidInput, "collision"): registration(collision, checkout, apply=True)
        second = self.export(p2, dest="second")
        registration(second, checkout, apply=True)
        self.assertEqual(len(check_checkout(checkout, replay=True)["entries"]), 11)
        with self.assertRaisesRegex(InvalidInput, "Test-only"): registration(second, ROOT, apply=True)
        altered = load_json(out / "manifest.json"); altered["runtime_revision"] = 8
        write_json(out / "manifest.json", altered)
        with self.assertRaises(InvalidInput): registration(out, checkout, apply=True)

    def test_target_path_windows_collision_preserves_existing_bytes(self):
        out = self.export(self.package(), stem="occupied")
        root = isolated_checkout(self.root / "checkout")
        existing = root / "game/data/content/Occupied.json"
        existing.parent.mkdir(); existing.write_bytes(b"foreign work")
        with self.assertRaisesRegex(InvalidInput, "collid"): registration(out, root, apply=True)
        self.assertEqual(existing.read_bytes(), b"foreign work")
        check_checkout(root)

    def test_zip_paths_collisions_special_files_and_resource_limits(self):
        for names in (("../handoff.json",), ("C:/handoff.json",), ("a\\b",), ("a", "A"), ("a", "a/b"), ("a./b",), ("NUL.json",)):
            with self.subTest(names=names):
                z = self.root / "bad.zip"
                with zipfile.ZipFile(z, "w") as archive:
                    for n in names: archive.writestr(n, "{}")
                with self.assertRaises(InvalidInput), open_package(z): pass
        z = self.root / "symlink.zip"
        with zipfile.ZipFile(z, "w") as archive:
            info = zipfile.ZipInfo("link"); info.create_system = 3; info.external_attr = (stat.S_IFLNK | 0o777) << 16
            archive.writestr(info, "target")
        with self.assertRaises(InvalidInput), open_package(z): pass
        p = self.package()
        for limit in ("MAX_FILES", "MAX_FILE", "MAX_TOTAL"):
            with patch.object(boundary, limit, 1), self.assertRaises(InvalidInput), open_package(p): pass
        with patch.object(boundary, "SECONDS", 0), self.assertRaises(Aborted), open_package(p): pass

    def test_json_unsupported_versions_missing_files_and_invalid_numbers(self):
        for raw in ('{"format":1,"format":2}', '{"width":NaN}', '{"width":1e999}', '{"width":true}'):
            p = self.package() if not (self.root / "direct-mono").exists() else self.root / "direct-mono"
            (p / "handoff.json").write_text(raw, encoding="utf-8")
            with self.assertRaises(InvalidInput): self.inspect(p)
        p = self.package("direct-color")
        (p / "production/import/area-proof.json").unlink()
        with self.assertRaises(InvalidInput): self.inspect(p)

    def test_frame_rule_and_target_size_palette_limits(self):
        from tools.puzzle_production.target_adapter import definition
        for w,h in ((1,1),(1,5),(5,1),(50,2),(2,50),(51,2),(2,51)):
            p = self.root / f"size-{w}-{h}"
            make(p, "pz-test-size", w, h, "mono")
            if max(w,h)>50:
                with self.assertRaises(InvalidInput): self.inspect(p)
            else:
                self.assertTrue(self.inspect(p)["technical"])
        p = self.root / "colors-5"
        make(p,"pz-test-five",6,4,"color",colors=5)
        with self.assertRaisesRegex(InvalidInput,"foreground colors"): self.inspect(p)
        p4 = self.root / "colors-4"
        make(p4,"pz-test-four",6,4,"color",colors=4)
        self.assertTrue(self.inspect(p4)["technical"])
        p = self.root / "frame"
        make(p, "pz-test-frame", 6, 4, "mono")
        # A contour import has empty outer edges; even a forged pass gate fails.
        d = load_json(p / "design.json"); d["variants"][0]["method"] = "contour"
        # Build a new valid import, no malformed hashes needed to test target gate.
        from tools.puzzle_production.images import import_image
        write_json(p / "design.json", d)
        shutil.rmtree(p / "production/import")
        import_image(p / "motifs/source.png", p / "design.json", p / "production/import")
        c = load_json(p / "production/import/area-candidate.json")
        h = load_json(p / "handoff.json"); h["candidate"].update(matrix_hash=digest(c["matrix"]), logic_hash=c["logic_hash"])
        h["approved_parameters"][0]["method"] = "contour"
        a = load_json(p / "motif-approval.json"); a["parameters"]["method"] = "contour"; write_json(p / "motif-approval.json",a)
        seal(p,h)
        with self.assertRaisesRegex(InvalidInput,"frame rule"): self.inspect(p)

    def test_rectangular_reveal_and_svg_boundaries(self):
        p = self.root / "reveal.svg"
        p.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="24" height="16"><rect width="24" height="16" fill="#449944"/></svg>')
        validate_reveal(p,6,4)
        for svg in ('<svg width="NaN" height="16"/>', '<svg width="24" height="16"><image href="https://example.com/a"/></svg>',
                    '<!DOCTYPE svg><svg width="24" height="16"/>', '<svg width="24" height="16" onload="x"/>'):
            p.write_text(svg)
            with self.assertRaises(InvalidInput): validate_reveal(p,6,4)

    def test_svg_export_and_rehashed_runtime_or_report_rejected(self):
        p = self.package()
        h = load_json(p/"handoff.json")
        (p/"reveals/reveal.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" width="24" height="16"><rect width="24" height="16" fill="#449944"/></svg>\n',encoding="utf-8")
        h["reveal"].update(file="reveals/reveal.svg",sha256=file_hash(p/"reveals/reveal.svg"))
        for name in ("reveal-approval.json","reveals/reveal.provenance.json"):
            raw = load_json(p/name); raw.update(file=h["reveal"]["file"],sha256=h["reveal"]["sha256"])
            write_json(p/name,raw)
        h["reveal"]["provenance"] = "reveals/reveal.provenance.json"
        h["motif"]["derived_from_reveal_sha256"] = h["reveal"]["sha256"]
        a = load_json(p/"motif-approval.json"); a["derived_from_reveal_sha256"] = h["reveal"]["sha256"]; write_json(p/"motif-approval.json",a)
        prov = load_json(p/"motifs/source.provenance.json"); prov["derived_from"] = {k:h["reveal"][k] for k in ("file","sha256")}; write_json(p/"motifs/source.provenance.json",prov)
        seal(p,h)
        out = self.export(p)
        m, _ = verify_export(out)
        self.assertEqual(file_hash(out/m["reveal"]),h["reveal"]["sha256"])
        for name in (m["definition"],"inspection.json","usage.txt"):
            file = out/name; saved = file.read_bytes()
            raw = load_json(file)
            if name == m["definition"]: raw["solution"][0][0] = 1
            elif name == "inspection.json": raw["technical"] = False
            else: raw["production_id"] = "pz-forged"
            write_json(file,raw)
            changed = copy.deepcopy(m); changed["files"][name] = file_hash(file); write_json(out/"manifest.json",changed)
            with self.assertRaises(InvalidInput): verify_export(out)
            file.write_bytes(saved); write_json(out/"manifest.json",m)


if __name__ == "__main__":
    unittest.main()
