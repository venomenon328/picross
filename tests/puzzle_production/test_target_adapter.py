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
from tools.puzzle_production.contract import InvalidInput, InvalidProof, Aborted, digest, load_json, write_json
from tools.puzzle_production.images import file_hash
from tools.puzzle_production.authoring_inspection import inspect
from tools.puzzle_production.image_validation import validate_reveal
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


    def reseal(self, p):
        seal(p, load_json(p / "handoff.json"))

    def snapshot(self, root):
        return {p.relative_to(root).as_posix(): p.read_bytes() if p.is_file() else None
                for p in root.rglob("*")}







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
            self.assertTrue(inspect(opened, a)[0]["editorial_approved"])
            self.assertFalse(inspect(opened, a)[0]["category_ready"])
            self.assertFalse(inspect(opened, a)[0]["catalog_ready"])



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


    def test_rectangular_reveal_and_svg_boundaries(self):
        p = self.root / "reveal.svg"
        p.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="24" height="16"><rect width="24" height="16" fill="#449944"/></svg>')
        validate_reveal(p,6,4)
        for svg in ('<svg width="NaN" height="16"/>', '<svg width="24" height="16"><image href="https://example.com/a"/></svg>',
                    '<!DOCTYPE svg><svg width="24" height="16"/>', '<svg width="24" height="16" onload="x"/>'):
            p.write_text(svg)
            with self.assertRaises(InvalidInput): validate_reveal(p,6,4)



if __name__ == "__main__":
    unittest.main()
