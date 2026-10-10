"""Independent negative checks for VS2 delivery identity and coverage."""
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest
import vs2_delivery
from p1_preflight import PreflightError
from vs2_windows_probe import embedded_pack


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory()
        self.root=Path(self.temporary.name)
        records=[]
        for corpus,count in ((False,9),(True,10)):
            for i in range(1,count+1):
                for w,h in ((1280,720),(1600,900),(1920,1080),(2560,1440)):
                    for ui in (1.0,1.25):
                        for mode in ("G","V"):
                            records.append(dict(corpus=corpus,id=f"VS{i:02d}" if corpus else f"F-{i:02d}",client=[w,h],ui_scale=ui,mode=mode,layout_valid=True,grid_fit=True,hidden_tokens=0,status="geometric_fit_owner_open",clipped_glyphs=0,glyph_collisions=0,cell_pitch=24))
        names={"album.png","options.png"}
        names.update(f"regular-F-{i:02d}-G-ui{ui}.png" for i in (1,7) for ui in (100,125))
        names.update(f"corpus-VS{i:02d}-{mode}-ui{ui}.png" for i in (4,8,9) for mode in ("G","V") for ui in (100,125))
        names.update(f"rectangular-VS{i:02d}-reveal.png" for i in (1,3,5,7,9))
        for name in names: (self.root/name).write_bytes(b"bound-test-image")
        self.report=dict(failures=0,records=records,pictures=[dict(file=n,sha256=hashlib.sha256(b"bound-test-image").hexdigest()) for n in names])
        for picture in self.report["pictures"]:
            if picture["file"].startswith(("regular-","corpus-")):
                picture["frame_pixels"]={side:{"minimum_ink_pixels":2} for side in ("top","bottom","left","right")}

    def tearDown(self): self.temporary.cleanup()

    def verify(self):
        (self.root/"vs2-matrix.json").write_text(json.dumps(self.report),encoding="utf-8")
        return vs2_delivery.verify(self.root)

    def test_complete_matrix(self): self.assertEqual(len(self.verify()["records"]),304)

    def test_missing_and_duplicate_case(self):
        self.report["records"][-1]=self.report["records"][0]
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

    def test_replaced_native_picture(self):
        (self.root/self.report["pictures"][0]["file"]).write_bytes(b"different")
        with self.assertRaises(PreflightError): self.verify()

    def test_missing_frame_edge(self):
        self.report["pictures"][0]["frame_pixels"]={"right":{"minimum_ink_pixels":0}}
        with self.assertRaises(PreflightError): self.verify()

    def test_embedded_pack_hash_and_bounds(self):
        pack=b"GDPCexact embedded payload"
        executable=self.root/"test.exe"
        executable.write_bytes(b"MZtemplate"+pack+struct.pack("<Q",len(pack))+b"GDPC")
        self.assertEqual(embedded_pack(executable)["sha256"],hashlib.sha256(pack).hexdigest())
        executable.write_bytes(b"MZtemplate"+pack+struct.pack("<Q",len(pack)+999)+b"GDPC")
        with self.assertRaises(ValueError): embedded_pack(executable)

    def test_v3_rejects_duplicate_case_failed_assertion_and_changed_picture(self):
        names = ['v3-sl-720-125-color-G.png', 'v3-sl-720-100-mono-V.png', 'v3-sl-900-100-color-V.png', 'v3-sl-900-125-mono-G.png', 'v3-sl-1440-125-color-V.png', 'v3-sl-720-125-recovery.png', 'v3-sidebar-detail.png'] + ["v3-tight-rail.png", "v3-F01-work.png", "v3-F02-work.png", "v3-F08-work.png", "v3-title.png", "v3-fills-five.png"]
        for name in names: (self.root/name).write_bytes(b"native-binding")
        report = dict(checks=1000, failures=0,
                      sidebar_assets=json.loads((Path(__file__).resolve().parents[1]/"prototypes/p1/art/book/frames.json").read_text(encoding="utf-8")),
                      frame_pixels=[dict(changed_pixels=101) for _ in range(3)],
                      records=[dict(id=s, client=[w,h], ui=u, mode=m, fit=f)
                               for s in ("F-01","F-02","F-08") for w,h in ((1280,720),(1600,900),(1920,1080),(2560,1440))
                               for u in (1.0,1.25) for m in ("G","V") for f in (False,True)],
                      pictures=[dict(file=n,sha256=hashlib.sha256(b"native-binding").hexdigest()) for n in names])
        def verify():
            (self.root/"v3-report.json").write_text(json.dumps(report),encoding="utf-8")
            return vs2_delivery.verify_v3(self.root)
        self.assertEqual(len(verify()["records"]),96)
        report["frame_pixels"][0]["changed_pixels"] = 0
        with self.assertRaises(PreflightError): verify()
        report["frame_pixels"][0]["changed_pixels"] = 101
        report["sidebar_assets"]["source"] = "wrong asset source"
        with self.assertRaises(PreflightError): verify()
        report["sidebar_assets"]=json.loads((Path(__file__).resolve().parents[1]/"prototypes/p1/art/book/frames.json").read_text(encoding="utf-8"))
        original = report["records"][-1]
        report["records"][-1] = report["records"][0]
        with self.assertRaises(PreflightError): verify()
        report["records"][-1] = original
        report["failures"] = 1
        with self.assertRaises(PreflightError): verify()
        report["failures"] = 0
        (self.root/names[0]).write_bytes(b"different pixels")
        with self.assertRaises(PreflightError): verify()

    def test_v2_rejects_failed_or_missing_round_and_modified_image(self):
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
        (self.root/names[0]).write_bytes(b"changed-pixels")
        with self.assertRaises(PreflightError): vs2_delivery.verify_v2(self.root)


if __name__=="__main__": unittest.main()
