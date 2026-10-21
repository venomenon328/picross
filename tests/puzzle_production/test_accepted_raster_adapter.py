"""Synthetic mono pixel sources only; never real or derived catalog fixtures."""
from copy import deepcopy
from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile

from tools.puzzle_production.authoring_package import open_package
from tools.puzzle_production.contract import InvalidInput, InvalidProof, load_json, write_json
from tools.puzzle_production.images import file_hash, import_image
from tools.puzzle_production.target_adapter import export, inspect, verify_export
from tools.puzzle_production.za1_fixtures import ROOT, make, seal, approve, isolated_checkout, rated_registration


class AcceptedRasterTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(); self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.p = make(self.root / "source", "pz-test-accepted-mono", 6, 4, "mono")
        h = load_json(self.p / "handoff.json")
        p = load_json(self.p / "reveals/reveal.provenance.json"); p["approval"] = "reveal-approval.json"
        write_json(self.p / "reveals/reveal.provenance.json", p)
        for name in ("reveals/reveal.png", "reveals/reveal.provenance.json", "reveal-approval.json", "evidence.txt"):
            target = self.p / "reference" / name; target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.p / name, target)
        h["reveal"].update(file="reference/reveals/reveal.png", approval=None, revision="test-1",
                           historical_approval="reference/reveal-approval.json")
        h.update(state="raster_review", proposed_parameters=h["approved_parameters"], approved_parameters=[],
                 blockers=["TEST ONLY: motif pending", "TEST ONLY: editorial pending"])
        h["candidate"]["source_type"] = "manual"; h["gates"]["motif"] = "pending"
        h["motif"].update(approval=None, revision="test-drawn")
        p = load_json(self.p / "motifs/source.provenance.json"); p["derived_from"]["file"] = h["reveal"]["file"]
        write_json(self.p / "motifs/source.provenance.json", p); seal(self.p, h)
        self.auth, self.approval = self.root / "manual-authorization.json", self.root / "approval.json"
        self.authorize()

    def authorize(self, archive=None):
        h = load_json(self.p / "handoff.json"); seal(self.p, h); approve(self.p, self.approval)
        common = {"puzzle_id": h["puzzle_id"], "revision": h["revision"],
            "handoff_sha256": file_hash(self.p / "handoff.json"), "inventory_sha256": h["inventory"]["sha256"],
            "selection": load_json(self.approval)["selection"], "superseded_content_blockers": h["blockers"],
            "accepted_motif": {**{k: h["motif"][k] for k in
                ("file", "sha256", "derived_from_reveal_sha256", "revision")}, "parameters": h["proposed_parameters"][0]},
            "historical_reveal": {"prefix": "reference", **{k: {"file": n, "sha256": file_hash(self.p / n)}
                for k, n in (("approval", "reference/reveal-approval.json"),
                             ("provenance", "reference/reveals/reveal.provenance.json"))}}}
        write_json(self.root / "owner-override.json", {**common, "format": "picross-owner-override-v6",
            "actor": "TEST ONLY", "statement": "Synthetic acceptance/authorization only",
            "timestamp_utc": "2026-10-22T00:00:00Z", "package_sha256": archive,
            "approval_sha256": file_hash(self.approval), "permissions": {"accepted_mono_pixel_source": True,
                "late_motif_acceptance": True, "historical_reveal_binding": True}})
        write_json(self.auth, {**common, "format": "picross-manual-authorization-v6", "original_zip_sha256": archive,
            "owner_override": {"file": "owner-override.json", "sha256": file_hash(self.root / "owner-override.json")}})

    def inspect(self, approval=True):
        with open_package(self.p, allow_manual_review=True) as p:
            return inspect(p, self.approval if approval else None, manual_authorization=self.auth)[0]

    def export(self, source, output):
        export(source, output, name="TEST ONLY", revision=1, stem="accepted_mono", save_slot="accepted_mono",
               approval_path=self.approval, manual_authorization=self.auth, category_id="voegel",
               categories_path=ROOT / "tests/puzzle_production/fixtures/catalog/categories.json")

    def test_zip_offline_export_registration_preserves_sealed_history(self):
        archive = self.root / "package.zip"
        with zipfile.ZipFile(archive, "w") as z:
            for f in self.p.rglob("*"):
                if f.is_file(): z.write(f, f.relative_to(self.p).as_posix())
        before = (self.p / "handoff.json").read_bytes(); self.authorize(file_hash(archive))
        out = self.root / "export"; self.export(archive, out); manifest, report = verify_export(out)
        self.assertEqual(manifest["format"], "picross-target-export-v3")
        self.assertTrue(report["technical"] and report["catalog_ready"] and report["late_motif_acceptance"])
        self.assertEqual(report["original_motif_gate"], "pending")
        self.assertEqual((out / "input/handoff.json").read_bytes(), before)
        for name in ("reference/reveal-approval.json", "reference/reveals/reveal.provenance.json"):
            self.assertEqual((out / "input" / name).read_bytes(), (self.p / name).read_bytes())
        self.assertEqual((out / "runtime/art/content/accepted_mono.png").read_bytes(),
                         (self.p / "reference/reveals/reveal.png").read_bytes())
        checkout = isolated_checkout(self.root / "checkout")
        self.assertEqual(rated_registration(out, checkout)["status"], "planned")
        self.assertEqual(rated_registration(out, checkout, apply=True)["status"], "registered")

    def test_explicit_auth_final_approval_and_all_other_gates_required(self):
        with self.assertRaises(InvalidInput), open_package(self.p): pass
        with open_package(self.p, allow_manual_review=True) as p, self.assertRaises(InvalidInput): inspect(p, self.approval)
        with self.assertRaisesRegex(InvalidInput, "requires bound final approval"): self.inspect(False)
        h = load_json(self.p / "handoff.json")
        for gate in ("frame", "logic", "provenance", "visual", "difficulty", "reveal_approval", "reveal_consistency"):
            h["gates"][gate] = "fail"; seal(self.p, h); self.authorize()
            with self.subTest(gate=gate), self.assertRaisesRegex(InvalidInput, "Unresolved content gate"): self.inspect()
            h["gates"][gate] = "pass"; seal(self.p, h)

    def test_rebound_authority_parameters_and_historical_aliases_rejected(self):
        for key, value in (("original_zip_sha256", "0"*64), ("handoff_sha256", "0"*64),
                           ("inventory_sha256", "0"*64), ("selection", {}), ("superseded_content_blockers", [])):
            self.authorize(); a = load_json(self.auth); a[key] = value; write_json(self.auth, a)
            with self.subTest(key=key), self.assertRaises(InvalidInput): self.inspect()
        self.authorize(); a = load_json(self.auth); a["accepted_motif"]["parameters"]["fit"] = "stretch"; write_json(self.auth, a)
        with self.assertRaisesRegex(InvalidInput, "parameter binding"): self.inspect()
        self.authorize(); o = load_json(self.root / "owner-override.json"); o["permissions"]["late_motif_acceptance"] = 1
        write_json(self.root / "owner-override.json", o)
        a = load_json(self.auth); a["owner_override"]["sha256"] = file_hash(self.root / "owner-override.json"); write_json(self.auth, a)
        with self.assertRaisesRegex(InvalidInput, "permission scope"): self.inspect()
        self.authorize(); a = load_json(self.auth); a["historical_reveal"]["prefix"] = "../reference"; write_json(self.auth, a)
        with self.assertRaises(InvalidInput): self.inspect()
        original = load_json(self.p / "reference/reveal-approval.json")
        for key, value in (("file", "reveals/other.png"), ("sha256", "0"*64), ("revision", "other"),
                           ("timestamp_utc", "invalid"), ("evidence", "missing.md")):
            changed = deepcopy(original); changed[key] = value; write_json(self.p / "reference/reveal-approval.json", changed)
            self.authorize()
            with self.subTest(history=key), self.assertRaises(InvalidInput): self.inspect()

    def test_fresh_proof_and_exact_pixels_required(self):
        bundle = self.p / "production/import"
        proof = load_json(bundle / "area-proof.json"); proof["final_domains"][0][0] = ["ink"]
        write_json(bundle / "area-proof.json", proof)
        manifest = load_json(bundle / "manifest.json"); manifest["files"]["area-proof.json"] = file_hash(bundle / "area-proof.json")
        write_json(bundle / "manifest.json", manifest); self.authorize()
        with self.assertRaises((InvalidInput, InvalidProof)): self.inspect()
        from PIL import Image
        source = self.p / "motifs/source.png"
        image = Image.open(source).convert("RGB"); image.putpixel((0, 0), (240, 240, 240)); image.save(source)
        self.assertTrue(bundle.resolve().is_relative_to(self.root.resolve())); shutil.rmtree(bundle)
        import_image(source, self.p / "design.json", bundle)
        h = load_json(self.p / "handoff.json"); h["motif"]["sha256"] = file_hash(source)
        p = load_json(self.p / "motifs/source.provenance.json"); p["sha256"] = file_hash(source)
        write_json(self.p / "motifs/source.provenance.json", p); seal(self.p, h); self.authorize()
        with self.assertRaisesRegex(InvalidInput, "exact mono RGB pixels"): self.inspect()

    def test_paired_v4_and_profile_binding(self):
        bundle = self.p / "production/import"
        self.assertTrue(bundle.resolve().is_relative_to(self.root.resolve())); shutil.rmtree(bundle)
        import_image(self.p / "motifs/source.png", self.p / "design.json", bundle, profile="paired-lines-mono")
        h = load_json(self.p / "handoff.json"); h["candidate"]["certification"] = load_json(bundle / "manifest.json")["certification"]
        (self.p / "rulebook.md").write_text("**Version 0.5.0 · synthetic test only**\n", encoding="utf-8")
        h["rulebook"] = {"version": "0.5.0", "file": "rulebook.md", "sha256": file_hash(self.p / "rulebook.md")}
        proof = load_json(bundle / "area-proof.json"); d = load_json(self.p / "difficulty.json")
        d.update(method="picross-difficulty-0.2", profile_hash=proof["profile_hash"], evidence="production/import/area-assessment.json")
        write_json(self.p / "difficulty.json", d); seal(self.p, h); self.authorize()
        out = self.root / "paired-export"; self.export(self.p, out); manifest, report = verify_export(out)
        self.assertEqual(manifest["format"], "picross-target-export-v4")
        self.assertIn("accepted_raster.py", report["tool"]["modules"])
        h["candidate"]["certification"]["max_pair_work"] += 1; seal(self.p, h); self.authorize()
        with self.assertRaisesRegex(InvalidInput, "profile binding"): self.inspect()


if __name__ == "__main__": unittest.main()
