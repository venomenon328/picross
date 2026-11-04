"""Independent negative checks for VS2 delivery identity and coverage."""
import hashlib
import gzip
import copy
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
import vs2_delivery
from p1_preflight import PreflightError
from vs2_windows_probe import extract


class DeliveryTests(unittest.TestCase):
    def test_native_player_extraction_rejects_escape_and_duplicate_paths(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for index, names in enumerate((("../outside.exe",), ("/outside.exe",), ("same.exe", "same.exe"))):
                archive = root / f"bad-{index}.zip"
                with zipfile.ZipFile(archive, "w") as bundle:
                    for name in names:
                        bundle.writestr(name, b"invalid package")
                with self.assertRaises(ValueError):
                    extract(archive, root / f"extracted-{index}")

    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory()
        self.root=Path(self.temporary.name)
        records=[]
        for corpus,ids in ((False,(1,2,4,6,8,9)),(True,range(1,11))):
            for i in ids:
                for w,h,ui in ((1280,720,1.25),(1920,1080,1.0),(2560,1440,1.25)):
                    for mode in ("G","V"):
                        records.append(dict(corpus=corpus,id=f"VS{i:02d}" if corpus else f"T-{i:02d}",client=[w,h],ui_scale=ui,mode=mode,layout_valid=True,grid_fit=True,hidden_tokens=0,status="geometric_fit_owner_open",clipped_glyphs=0,glyph_collisions=0,cell_pitch=24))
        names={"album.png","options.png"}
        names.update(f"regular-T-{i:02d}-G-ui{ui}.png" for i in (1,6) for ui in (100,))
        names.update(f"corpus-VS{i:02d}-{mode}-ui{ui}.png" for i in (4,8,9) for mode in ("G","V") for ui in (100,))
        names.update(f"rectangular-VS{i:02d}-reveal.png" for i in (1,3,5,7,9))

        self.report=dict(failures=0,records=records,pictures=[dict(case=n.removesuffix(".png")) for n in names])
        for picture in self.report["pictures"]:
            if picture["case"].startswith(("regular-","corpus-")):
                picture["frame_pixels"]={side:{"minimum_ink_pixels":2} for side in ("top","bottom","left","right")}

    def tearDown(self): self.temporary.cleanup()

    def verify(self):
        (self.root/"vs2-matrix.json").write_text(json.dumps(self.report),encoding="utf-8")
        return vs2_delivery.verify(self.root)

    def test_complete_matrix(self):
        self.assertEqual(len(self.verify()["records"]),96)
        path = self.root / "vs2-matrix.json"
        original = path.read_bytes()
        packed = vs2_delivery.compress_geometry_report(path)
        compressed = packed.read_bytes()
        self.assertEqual(gzip.decompress(compressed), original)
        self.assertEqual(vs2_delivery.compress_geometry_report(path).read_bytes(), compressed)
        self.assertEqual(vs2_delivery.read_geometry_report(packed), self.report)
        path.unlink()
        self.assertEqual(vs2_delivery.verify(self.root), self.report)

    def test_missing_and_duplicate_case(self):
        self.report["records"][-1]=self.report["records"][0]
        with self.assertRaises(PreflightError): self.verify()

    def test_wrong_client_height_cannot_replace_expected_case(self):
        self.report["records"][0]["client"][1] += 1
        with self.assertRaises(PreflightError): self.verify()


    def test_v_cannot_hide_hints(self):
        self.report["records"][1]["hidden_tokens"]=1
        with self.assertRaises(PreflightError): self.verify()

    def test_false_positive_comfort(self):
        self.report["records"][0]["glyph_collisions"]=1
        with self.assertRaises(PreflightError): self.verify()

    def test_missing_native_picture(self):
        self.report["pictures"].pop()
        with self.assertRaises(PreflightError): self.verify()


    def test_missing_frame_edge(self):
        self.report["pictures"][0]["frame_pixels"]={"right":{"minimum_ink_pixels":0}}
        with self.assertRaises(PreflightError): self.verify()


    def test_v2_rejects_failed_or_missing_round(self):
        names = ["v2-projection-1.png", "v2-projection-4.png", "v2-mono-work.png",
                 "v2-five-crossing.png", "v2-color-work.png", "v2-mini-palette.png"]
        for name in names: (self.root/name).write_bytes(b"native-binding")
        write = dict(checks=100, failures=0, scenarios=[str(i) for i in range(19)],
                     pictures=[dict(file=n,sha256=hashlib.sha256(b"native-binding").hexdigest()) for n in names])
        read = dict(checks=8, failures=0, pictures=[], scenarios=["fresh process redo restores X"])
        def save():
            for stage, value in (("write", write), ("read", read)):
                (self.root/("v2-"+stage+".json")).write_text(json.dumps(value),encoding="utf-8")
        save()
        self.assertEqual(vs2_delivery.verify_v2(self.root)["read"]["checks"],8)
        read["failures"] = 1
        save()
        with self.assertRaises(PreflightError): vs2_delivery.verify_v2(self.root)
        read["failures"] = 0
        write["scenarios"][-1] = write["scenarios"][0]
        save()
        with self.assertRaises(PreflightError): vs2_delivery.verify_v2(self.root)
        write["scenarios"][-1] = "18"
        save()


if __name__=="__main__": unittest.main()
