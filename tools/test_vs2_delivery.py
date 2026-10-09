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


if __name__=="__main__": unittest.main()
