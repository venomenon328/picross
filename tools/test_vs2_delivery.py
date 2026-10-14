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
        for name in names: (self.root/name).write_bytes(b"bound-test-image")
        self.report=dict(failures=0,records=records,pictures=[dict(file=n,sha256=hashlib.sha256(b"bound-test-image").hexdigest()) for n in names])
        for picture in self.report["pictures"]:
            if picture["file"].startswith(("regular-","corpus-")):
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

    def test_focused_and_recovery_identity_not_just_count(self):
        from vs2_v1_verify import verify_focused_coverage
        records = [dict(recovery=False, id=s, client=[1920,1080], ui_scale=u,
                        mode=m, requested_cell=z)
                   for s in ("T-01", "VS04", "VS08", "VS09")
                   for u in (1,1.25) for m in ("G","V") for z in (24,72)]
        records += [dict(recovery=True, id=s, client=[w,h], ui_scale=u, mode=m)
                    for s in ("T-01","T-02","T-06")
                    for w,h,u in ((1280,720,1.25),(1920,1080,1),(2560,1440,1.25))
                    for m in ("G","V")]
        report = dict(failures=0, records=records)
        verify_focused_coverage(report)
        for index in (0,32):
            broken = copy.deepcopy(report)
            broken['records'][index] = broken['records'][index+1]
            with self.subTest(index=index), self.assertRaises(PreflightError):
                verify_focused_coverage(broken)

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

    def test_v3_rejects_duplicate_case_failed_assertion_and_changed_picture(self):
        def axes(w,h,u):
            buttons=[[w-(187.5 if w<1700 else 150)-(2-i)*58*u-20*u,h/30+12*u,44*u,44*u] for i in range(3)]
            axis=buttons[1][0]+22*u
            return dict(material=[0,0,w,h],navigation_buttons=buttons,navigation=axis,frames=[axis]*3,controls=[axis]*4)
        names = ['v3-sl-720-125-color-G.png', 'v3-sl-720-100-mono-V.png', 'v3-sl-900-100-color-V.png', 'v3-sl-900-125-mono-G.png', 'v3-sl-1440-125-color-V.png', 'v3-sl-720-125-recovery.png', 'v3-sidebar-detail.png'] + ["v3-tight-rail.png", "v3-T01-work.png", "v3-T08-work.png", "v3-title.png", "v3-fills-five.png"]
        for name in names: (self.root/name).write_bytes(b"native-binding")
        report = dict(checks=1000, failures=0,
                      sidebar_metadata_sha256=hashlib.sha256((Path(__file__).resolve().parents[1]/"game/art/book/frames.json").read_bytes()).hexdigest(),
                      sidebar_assets=json.loads((Path(__file__).resolve().parents[1]/"game/art/book/frames.json").read_text(encoding="utf-8")),
                      frame_pixels=[dict(changed_pixels=101) for _ in range(3)],
                      records=[dict(id=s, client=[w,h], ui=u, mode=m, fit=f,sidebar_axes=axes(w,h,u))
                               for s in ("T-01","T-02","T-08") for w,h,u in ((1280,720,1.25),(1920,1080,1.0),(2560,1440,1.25)) for m in ("G","V") for f in (False,True)],
                      pictures=[dict(file=n,sha256=hashlib.sha256(b"native-binding").hexdigest()) for n in names])
        def verify():
            (self.root/"v3-report.json").write_text(json.dumps(report),encoding="utf-8")
            return vs2_delivery.verify_v3(self.root)
        self.assertEqual(len(verify()["records"]),36)
        native_path=self.root/'v3-report.json'
        native_value=json.loads(native_path.read_text(encoding='utf-8'))
        native_path.write_text(json.dumps(native_value,indent=2),encoding='utf-8')
        original_size=native_path.stat().st_size
        vs2_delivery.compact_geometry_reports([native_path])
        self.assertEqual(json.loads(native_path.read_text(encoding='utf-8')),native_value)
        self.assertLess(native_path.stat().st_size,original_size)
        self.assertEqual(len(vs2_delivery.verify_v3(self.root)['records']),36)
        original_axes=copy.deepcopy(report['records'][0]['sidebar_axes'])
        for kind in ('frames','controls','both','upper','missing'):
            a=copy.deepcopy(original_axes)
            if kind in ('frames','both','upper'): a['frames']=[v+16 for v in a['frames']]
            if kind in ('controls','both','upper'): a['controls']=[v+16 for v in a['controls']]
            if kind=='upper':
                a['navigation']+=16
                a['navigation_buttons']=[[b[0]+16,*b[1:]] for b in a['navigation_buttons']]
            report['records'][0]['sidebar_axes']={} if kind=='missing' else a
            with self.subTest(axis_mutation=kind), self.assertRaises(PreflightError): verify()
        report['records'][0]['sidebar_axes']=original_axes
        for item in report["sidebar_assets"]["derivatives"]:
            item["safe"] = [float(format(v,".15g")) for v in item["safe"]]
        self.assertEqual(len(verify()["records"]),36)
        original_safe = report["sidebar_assets"]["derivatives"][0]["safe"][0]
        report["sidebar_assets"]["derivatives"][0]["safe"][0] += 0.01
        with self.assertRaises(PreflightError): verify()
        report["sidebar_assets"]["derivatives"][0]["safe"][0] = original_safe
        original_hash = report["sidebar_metadata_sha256"]
        report["sidebar_metadata_sha256"] = "0"*64
        with self.assertRaises(PreflightError): verify()
        report["sidebar_metadata_sha256"] = original_hash
        report["frame_pixels"][0]["changed_pixels"] = 0
        with self.assertRaises(PreflightError): verify()
        report["frame_pixels"][0]["changed_pixels"] = 101
        report["sidebar_assets"]["source"] = "wrong asset source"
        with self.assertRaises(PreflightError): verify()
        report["sidebar_assets"]=json.loads((Path(__file__).resolve().parents[1]/"game/art/book/frames.json").read_text(encoding="utf-8"))
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
