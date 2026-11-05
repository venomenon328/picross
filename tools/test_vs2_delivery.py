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
        for corpus, name, w, h, ui, mode in vs2_delivery.MATRIX_CASES:
            invalid = w == 1280 and mode == 'V' and name in ('T-06','VS06')
            records.append(dict(corpus=corpus,id=name,client=[w,h],ui_scale=ui,mode=mode,
                                layout_valid=not invalid,grid_fit=not invalid,hidden_tokens=0,
                                status="geometric_fit_owner_open" if not invalid else "blocked",
                                clipped_glyphs=0,glyph_collisions=0,cell_pitch=24 if not invalid else 1))
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
        self.assertEqual(len(self.verify()["records"]),18)
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

    def test_selected_matrix_rejects_every_missing_case_extra_and_false_valid(self):
        original = copy.deepcopy(self.report)
        for index in range(18):
            self.report = copy.deepcopy(original)
            self.report['records'].pop(index)
            with self.assertRaises(PreflightError): self.verify()
        self.report = copy.deepcopy(original)
        self.report['records'].append(dict(self.report['records'][0], id='T-08'))
        with self.assertRaises(PreflightError): self.verify()
        self.report = copy.deepcopy(original)
        next(r for r in self.report['records'] if not r['layout_valid'])['layout_valid'] = True
        with self.assertRaises(PreflightError): self.verify()

    def test_compact_stage_rejects_omitted_duplicate_wrong_metadata_and_counters(self):
        for stage, count in (('layout',0),('cells-f1',27),('cells-f2',76),('axis',117),('h1',180)):
            frames, samples = [], []
            for name, (w,h,ui,fixture) in vs2_delivery.compact_frames(stage).items():
                pitch = int(name.split('-')[2]) if stage.startswith('cells-') else 24
                f = dict(name=name,logical_surface=[w,h],ui_scale=ui,fixture=fixture,
                         cell_pitch=pitch,retained=False,crop=False)
                if name.startswith('h1-') and name.endswith('-on'):
                    f['h1_pair'] = dict(off_frame=name[:-2]+'off',searches_on_toggle=0,
                                        marked_tokens=dict(row=1,column=1),colors=['ink'])
                frames.append(f)
                if name.startswith('zr-'):
                    samples.append(dict(name=name,requested_zoom=int(name.split('-')[3][1:]),
                                        actual_cell=pitch,ui=ui,font_size=round(24*ui),length=5,
                                        rect=[0,0,20,30],changed_pixels=30))
            good = dict(failed=False,compact=True,failure='',failure_captures=[],captures=[],
                        retained_count=0,rendered_count=len(frames),pixel_checks=count,
                        frames=frames,zr_samples=samples)
            vs2_delivery.verify_compact_stage(stage,good)
            for mutation in ('missing','duplicate','extra','surface','pixels','retained','pair' if stage=='h1' else 'samples'):
                bad = copy.deepcopy(good)
                if mutation == 'missing': bad['frames'].pop()
                elif mutation == 'duplicate': bad['frames'][-1] = bad['frames'][0]
                elif mutation == 'extra': bad['frames'].append(dict(bad['frames'][0],name='removed-case'))
                elif mutation == 'surface': bad['frames'][0]['logical_surface'][0] += 1
                elif mutation == 'pixels': bad['pixel_checks'] += 1
                elif mutation == 'retained': bad['frames'][0]['retained'] = True
                elif mutation == 'pair': next(f for f in bad['frames'] if 'h1_pair' in f)['h1_pair']['searches_on_toggle'] = 1
                elif samples: bad['zr_samples'][0]['rect'] = [-1,0,20,30]
                else: bad['zr_samples'].append(dict(name='unrequested'))
                with self.subTest(stage=stage,mutation=mutation), self.assertRaises(PreflightError):
                    vs2_delivery.verify_compact_stage(stage,bad)


    def test_v_cannot_hide_hints(self):
        next(r for r in self.report["records"] if r["mode"] == "V")["hidden_tokens"]=1
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
