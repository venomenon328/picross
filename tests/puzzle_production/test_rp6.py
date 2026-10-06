"""Fixed pilot export, repair trust boundary and manifest/asset negative controls."""
import copy
import shutil
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from tools.puzzle_production.contract import InvalidInput, InvalidProof, digest, load_json, write_json
from tools.puzzle_production.images import file_hash
from tools.puzzle_production.p1_export import export_p1, export_pilot, validate_pilot_reveal
from tools.puzzle_production.rp5 import unpack_archive
from tools.puzzle_production import rp6


class PilotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)

    def test_six_complete_exports_match_registered_files(self):
        report = rp6.verify_package(self.path / "replay")
        self.assertTrue(report["accepted"])
        self.assertEqual(len(report["exports"]), 6)
        self.assertEqual([x["source"]["kind"] for x in report["exports"]], ["import"]*4+["repair"]*2)
        self.assertEqual(report["owner_trials"], "open")

    def test_manifest_cannot_omit_swap_or_self_accept(self):
        original = load_json(rp6.PILOT / "manifest.json")
        plan = rp6.plan()
        attacks = [lambda m: m["entries"].pop(),
                   lambda m: m["entries"][1].update(asset=m["entries"][2]["asset"]),
                   lambda m: m["entries"][-1].update(source_kind="import"),
                   lambda m: m["entries"][0].update(editorial_release=True),
                   lambda m: m["entries"][0]["motif_review"].update(matrix_hash="0"*64),
                   lambda m: m["files"].pop("examples/rp6/artwork/prompts.json"),
                   lambda m: m.update(owner_trials="passed"),
                   lambda m: m["files"].update({"../escape": "0"*64})]
        for attack in attacks:
            changed = copy.deepcopy(original)
            attack(changed)
            with self.subTest(attack=attack), self.assertRaises(InvalidInput):
                rp6.validate_manifest(changed, plan)

    def test_png_size_format_orientation_and_old_profile(self):
        good = self.path / "good.png"
        Image.new("RGB", (200,200), "white").save(good)
        validate_pilot_reveal(good,200)
        for size in [(199,199),(200,201)]:
            Image.new("RGB",size).save(self.path / "bad.png")
            with self.assertRaises(InvalidInput):
                validate_pilot_reveal(self.path / "bad.png",200)
        Image.new("RGB",(200,200)).save(self.path / "fake.png",format="JPEG")
        with self.assertRaises(InvalidInput):
            validate_pilot_reveal(self.path / "fake.png",200)
        exif = Image.Exif()
        exif[274] = 6
        Image.new("RGB",(200,200)).save(self.path / "oriented.png",exif=exif)
        with self.assertRaises(InvalidInput):
            validate_pilot_reveal(self.path / "oriented.png",200)
        with self.assertRaises(InvalidInput):
            export_p1(rp6.ROOT / "examples/rp3/production", "area-128", good, "Name", self.path / "old")
        with self.assertRaises(InvalidInput):
            export_pilot(rp6.ROOT / "examples/rp3/production", "area-128", good, "Name", self.path / "id", "../F-05")

    def test_complete_repair_contract_not_just_final_proof(self):
        baseline = self.path / "baseline"
        unpack_archive(rp6.ROOT / "examples/rp5/baseline.zip",load_json(rp6.ROOT / "examples/rp5/archive.json"),baseline)
        locked = rp6.plan()["selection"][-2]
        reference = rp6.ROOT / locked["reference_bundle"]
        original = baseline / locked["repair_bundle"]
        asset = rp6.ROOT / "prototypes/p1/art/f08.png"
        for kind in ("parents", "proof", "mask", "status"):
            folder = self.path / kind
            shutil.copytree(original,folder)
            if kind == "parents":
                raw = load_json(folder / "repair.json")
                raw["history"][1]["parent"] = 1
                write_json(folder / "repair.json",raw)
            elif kind == "proof":
                raw = load_json(folder / "final-proof.json",100_000_000)
                raw["final_domains"][0][0] = ["unknown"]
                write_json(folder / "final-proof.json",raw)
            elif kind == "mask":
                raw = load_json(folder / "plan.json")
                raw["mask"][0][0] = not raw["mask"][0][0]
                write_json(folder / "plan.json",raw)
            else:
                raw = load_json(folder / "result.json")
                raw["status"] = "budget_exhausted"
                write_json(folder / "result.json",raw)
            raw = load_json(folder / "repair.json")
            raw["id"] = digest({k:v for k,v in raw.items() if k not in ("id","files")})
            write_json(folder / "manifest.json", {"format":"picross-repair-manifest-v1","repair_id":raw["id"]})
            raw["files"] = {name: file_hash(folder / name) for name in raw["files"]}
            write_json(folder / "repair.json",raw)
            with self.subTest(kind=kind), self.assertRaises((InvalidInput,InvalidProof)):
                export_pilot(folder,"area-128",asset,"Tulpe",self.path / (kind+"-out"),"F-08",reference=reference)
        with self.assertRaises(InvalidInput):
            export_pilot(original,"area-128",asset,"Tulpe",self.path / "mislabel","F-08")
        with self.assertRaises(InvalidInput):
            export_pilot(baseline / "i02-direct-60x40","area-128",asset,"Unsolved",self.path / "not-found","F-08",
                         reference=rp6.ROOT / "examples/rp4/baseline/i02-direct-60x40")


if __name__ == "__main__":
    unittest.main()
