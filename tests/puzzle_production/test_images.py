"""Real image files, independent expected pixel/run values and export attacks."""
import copy
import hashlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image, ImageCms
from tools.puzzle_production.contract import InvalidInput, InvalidProof, load_json, write_json
from tools.puzzle_production import images
from tools.puzzle_production.images import (candidate, import_image, inspect_candidate,
    logic_from_matrix, normalize, rasterize, validate_design)
from tools.puzzle_production.p1_export import export_p1, validate_reveal

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples/rp3"


class ImageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.design = load_json(EXAMPLE / "design.json")

    def file(self, image, name="source.png", **params):
        path = self.root / name
        image.save(path, **params)
        return path

    def small_design(self, w, h, mode="mono"):
        d = copy.deepcopy(self.design)
        d.update(width=w, height=h, crop=[0, 0, w, h], mode=mode,
                 variants=[{"id":"area", "method":"area", "threshold":128}])
        return d

    def produce(self, image=None, d=None, folder="production"):
        d = d or self.design
        source = EXAMPLE / "source.png" if image is None else self.file(image)
        design = self.root / "design.json"
        write_json(design, d)
        output = self.root / folder
        import_image(source, design, output)
        return output

    def rebind(self, bundle, name):
        manifest = load_json(bundle / "manifest.json")
        manifest["files"][name] = images.file_hash(bundle / name)
        write_json(bundle / "manifest.json", manifest)

    def test_all_eight_exif_orientations_including_mirrors(self):
        original = Image.new("RGB", (3, 2))
        original.putdata([(i, 10+i, 20+i) for i in range(6)])
        expected = {1:[0,1,2,3,4,5], 2:[2,1,0,5,4,3], 3:[5,4,3,2,1,0],
                    4:[3,4,5,0,1,2], 5:[0,3,1,4,2,5], 6:[3,0,4,1,5,2],
                    7:[5,2,4,1,3,0], 8:[2,5,1,4,0,3]}
        for orientation in range(1,9):
            exif = Image.Exif()
            exif[274] = orientation
            path = self.file(original, exif=exif)
            normal, meta, data = normalize(path)
            self.assertEqual([p[0] for p in normal.get_flattened_data()], expected[orientation])
            self.assertEqual(normal.size, (3,2) if orientation < 5 else (2,3))
            self.assertEqual(meta["orientation"], orientation)
            self.assertEqual(data, path.read_bytes())
            self.assertFalse(normal.info)

    def test_jpeg_and_profile_normalization(self):
        image = Image.new("RGB", (8,4), (120,40,20))
        profile = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
        for filename in ("rgb.png", "rgb.jpg"):
            normal, meta, _ = normalize(self.file(image, filename, icc_profile=profile))
            self.assertEqual(normal.size, (8,4))
            self.assertIn("ICC to sRGB", meta["color_treatment"])
            self.assertEqual(meta["icc_sha256"], hashlib.sha256(profile).hexdigest())
            self.assertEqual(normal.getpixel((0,0))[3], 255)
        with self.assertRaises(InvalidInput):
            normalize(self.file(image, "bad-icc.png", icc_profile=b"invalid profile"))
        with self.assertRaises(InvalidInput):
            normalize(self.file(image.convert("CMYK"), "cmyk.jpg"))

    def test_alpha_background_and_light_foreground_are_distinct(self):
        d = self.small_design(3,1,"color")
        d.update(background="#123456", palette=[{"id":"white","rgb":"#ffffff"},{"id":"red","rgb":"#ff0000"}])
        d = validate_design(d)
        source = Image.new("RGBA", (3,1))
        source.putdata([(255,255,255,255),(255,255,255,0),(255,0,0,255)])
        normal, _, _ = normalize(self.file(source))
        self.assertEqual(rasterize(normal,d,d["variants"][0]), [["white","empty","red"]])
        self.assertEqual(normal.getpixel((1,0)),(255,255,255,0))
        partial = Image.new("RGBA",(1,1),(0,0,0,127))
        m = self.small_design(1,1)
        self.assertEqual(rasterize(partial,m,m["variants"][0]),[["empty"]])
        partial.putpixel((0,0),(0,0,0,128))
        self.assertEqual(rasterize(partial,m,m["variants"][0]),[["ink"]])

    def test_palette_png_alpha_and_gray(self):
        pal = Image.new("P", (2,1))
        pal.putpalette([0,0,0,255,255,255] + [0]*762)
        pal.putdata([0,1])
        normal, _, _ = normalize(self.file(pal, transparency=1))
        self.assertEqual(normal.getpixel((1,0))[3],0)
        self.assertEqual(normalize(self.file(Image.new("L",(1,1),20)))[0].getpixel((0,0)),(20,20,20,255))

    def test_corrupt_truncated_unsupported_and_animated_files(self):
        path = self.root / "broken.png"
        for raw in (b"",b"not an image",b"\x89PNG\r\n\x1a\n"):
            path.write_bytes(raw)
            with self.assertRaises(InvalidInput):
                normalize(path)
        for fmt in ("PNG","JPEG"):
            valid = self.file(Image.new("RGB",(8,8)),"valid."+fmt.lower(),format=fmt)
            path.write_bytes(valid.read_bytes()[:len(valid.read_bytes())//2])
            with self.assertRaises(InvalidInput):
                normalize(path)
        gif = self.file(Image.new("RGB",(1,1)),"bad.gif")
        with self.assertRaises(InvalidInput):
            normalize(gif)
        animated = self.file(Image.new("RGBA",(2,2)),"animated.png",save_all=True,
            append_images=[Image.new("RGBA",(2,2),(255,0,0,255))],duration=100)
        with self.assertRaises(InvalidInput):
            normalize(animated)

    def test_resource_boundaries_before_decoding(self):
        path = self.file(Image.new("RGB",(3,3)))
        with patch.object(images,"MAX_PIXELS",9):
            normalize(path)
        with patch.object(images,"MAX_PIXELS",8), self.assertRaises(InvalidInput):
            normalize(path)
        with patch.object(images,"MAX_BYTES",path.stat().st_size):
            normalize(path)
        with patch.object(images,"MAX_BYTES",path.stat().st_size-1), self.assertRaises(InvalidInput):
            normalize(path)
        with self.assertRaises(InvalidInput):
            normalize(self.file(Image.new("RGB",(8193,1))))
        for bad in (0,101,True):
            d = self.small_design(1,1)
            d["width"] = bad
            with self.assertRaises(InvalidInput):
                validate_design(d)
        d = self.small_design(1,1)
        d["variants"] = [{"id":f"v{i}","method":"area","threshold":128} for i in range(8)]
        validate_design(d)
        d["variants"].append({"id":"ninth","method":"area","threshold":128})
        with self.assertRaises(InvalidInput):
            validate_design(d)

    def test_explicit_crop_fit_and_rectangle_no_stretch(self):
        image = Image.new("RGBA",(4,2),(0,0,0,255))
        d = self.small_design(4,4)
        d["crop"]=[0,0,4,2]
        with self.assertRaises(InvalidInput):
            rasterize(image,d,d["variants"][0])
        d["fit"]="contain"
        self.assertEqual(rasterize(image,d,d["variants"][0]), [["empty"]*4,["ink"]*4,["ink"]*4,["empty"]*4])
        d["crop"]=[0,0,5,2]
        with self.assertRaises(InvalidInput):
            rasterize(image,d,d["variants"][0])

    def test_eight_colors_100_by_100_and_1d_rectangles(self):
        colors = [(20+i*25,5+i*20,10+i*15) for i in range(8)]
        for w,h in ((100,100),(100,1),(1,100),(17,9)):
            d = self.small_design(w,h,"color")
            d["palette"]=[{"id":f"c{i}","rgb":"#%02x%02x%02x"%c} for i,c in enumerate(colors)]
            image = Image.new("RGBA",(w,h))
            image.putdata([(*colors[i%8],255) for i in range(w*h)])
            matrix = rasterize(image,validate_design(d),d["variants"][0])
            self.assertEqual([v for row in matrix for v in row],[f"c{i%8}" for i in range(w*h)])
            logic = logic_from_matrix(matrix,d)
            self.assertEqual(logic["width"],w)
            self.assertEqual(logic["height"],h)
            self.assertEqual(logic["row_clues"][0][0],{"length":1,"color":"c0"})

    def test_color_reduction_and_tie_order(self):
        d = self.small_design(2,1,"color")
        d["palette"]=[{"id":"red","rgb":"#ff0000"},{"id":"black","rgb":"#000000"}]
        d = validate_design(d)
        image = Image.new("RGBA",(2,1))
        image.putdata([(250,2,3,255),(1,1,1,255)])
        self.assertEqual(rasterize(image,d,d["variants"][0]),[["red","black"]])
        d["palette"].reverse()
        self.assertEqual(validate_design(d)["palette"][0]["id"],"black")

    def test_real_large_color_file_import_and_written_proof(self):
        d = self.small_design(100,100,"color")
        colors=[(20+i*25,5+i*20,10+i*15) for i in range(8)]
        d["palette"]=[{"id":f"c{i}","rgb":"#%02x%02x%02x"%c} for i,c in enumerate(colors)]
        image=Image.new("RGBA",(100,100))
        image.putdata([(*colors[i%8],255) for i in range(10000)])
        bundle=self.produce(image,d)
        c, proof, checked=inspect_candidate(bundle,"area")
        self.assertTrue(checked["certified"])
        self.assertEqual(len(c["matrix"]),100)
        self.assertEqual(proof["final_domains"][99][99],["c7"])

    def test_core_cli_imports_without_pillow(self):
        from tools.puzzle_production.cli import main
        import builtins
        real_import=builtins.__import__
        def guard(name,*args,**kwargs):
            if name == "PIL" or name.startswith("PIL."):
                raise ImportError("Pillow disabled for core test")
            return real_import(name,*args,**kwargs)
        from contextlib import redirect_stdout
        with patch("builtins.__import__",guard), redirect_stdout(io.StringIO()):
            self.assertEqual(main(["solve","--input",str(ROOT/"tests/puzzle_production/fixtures/deductive.json"),"--output-dir",str(self.root/"core")]),0)

    def test_deterministic_real_bundle_exact_runs_and_contours(self):
        first = self.produce()
        second = self.produce(folder="second")
        for v in self.design["variants"]:
            a, proof, verified = inspect_candidate(first,v["id"])
            b, _, _ = inspect_candidate(second,v["id"])
            self.assertEqual(a,b)
            self.assertEqual(proof["final_domains"],[[[v] for v in row] for row in a["matrix"]])
            self.assertTrue(verified["certified"])
            for suffix in ("candidate.json","logic.json","proof.json","raster.png"):
                self.assertEqual((first/f'{v["id"]}-{suffix}').read_bytes(),(second/f'{v["id"]}-{suffix}').read_bytes())
        matrix=[["ink","ink","empty","ink"],["empty","ink","empty","empty"]]
        d=self.small_design(4,2)
        logic=logic_from_matrix(matrix,d)
        self.assertEqual(logic["row_clues"],[[{"length":2,"color":"ink"},{"length":1,"color":"ink"}],[{"length":1,"color":"ink"}]])
        self.assertEqual(logic["column_clues"][1],[{"length":2,"color":"ink"}])

    def test_real_p1_export_and_no_stale_overwrite(self):
        bundle=self.produce()
        output=self.root/"export"
        result=export_p1(bundle,"area-128",EXAMPLE/"reveal.svg","Fliegenpilz",output)
        self.assertTrue(result["certified"])
        self.assertEqual((output/"data/f04.json").read_bytes(),(ROOT/"prototypes/p1/data/f04.json").read_bytes())
        self.assertEqual(load_json(output/"manifest.json")["color_mapping"],{"empty":0,"ink":1})
        with self.assertRaises(InvalidInput):
            export_p1(bundle,"area-128",EXAMPLE/"reveal.svg","Fliegenpilz",output)
        with self.assertRaises(InvalidInput):
            self.produce()

        # Display-only RGB/art changes preserve logic, but bind a new export.
        changed = copy.deepcopy(self.design)
        changed["palette"][0]["rgb"] = "#203030"
        second = self.produce(d=changed, folder="rgb-only")
        first_candidate, proof, _ = inspect_candidate(bundle,"area-128")
        second_candidate, same_proof, _ = inspect_candidate(second,"area-128")
        self.assertNotEqual(first_candidate["id"], second_candidate["id"])
        self.assertEqual(first_candidate["logic_hash"],second_candidate["logic_hash"])
        self.assertEqual(proof,same_proof)
        artwork = self.root/"changed.svg"
        artwork.write_text((EXAMPLE/"reveal.svg").read_text().replace("#b94337","#b94438"))
        self.assertNotEqual(artwork.read_bytes(),(EXAMPLE/"reveal.svg").read_bytes())
        export_p1(second,"area-128",artwork,"Fliegenpilz",self.root/"rgb-export")
        self.assertEqual(load_json(self.root/"rgb-export/data/f04.json")["palette"][0]["color"],"203030")
        self.assertEqual((self.root/"rgb-export/art/f04.svg").read_bytes(),artwork.read_bytes())

    def test_codec_build_replay_preserves_producer_identity_and_rejects_changed_pixels(self):
        bundle=self.produce()
        manifest=load_json(bundle/"manifest.json")
        original_versions=copy.deepcopy(manifest["versions"])
        manifest["versions"]["jpeg"]="6.2"
        manifest["versions"]["zlib"]="different-build"
        for variant in self.design["variants"]:
            name=variant["id"]+"-candidate.json"
            c=load_json(bundle/name)
            expected=candidate(c["normalized_sha256"],c["design"],c["variant"],c["matrix"],manifest["versions"])
            write_json(bundle/name,expected)
            manifest["files"][name]=images.file_hash(bundle/name)
        write_json(bundle/"manifest.json",manifest)
        c,_,checked=inspect_candidate(bundle,"area-128")
        self.assertTrue(checked["certified"])
        self.assertNotEqual(c["versions"],original_versions)
        self.assertEqual(c["versions"],manifest["versions"])
        manifest["versions"]["pillow"]="12.2.0"
        write_json(bundle/"manifest.json",manifest)
        with self.assertRaises(InvalidInput):
            inspect_candidate(bundle,"area-128")
        manifest["versions"]["pillow"]=original_versions["pillow"]
        write_json(bundle/"manifest.json",manifest)
        with Image.open(bundle/"normalized.png") as normal:
            changed=normal.copy()
        changed.putpixel((0,0),(255,0,0,255))
        changed.save(bundle/"normalized.png")
        self.rebind(bundle,"normalized.png")
        with self.assertRaises(InvalidInput):
            inspect_candidate(bundle,"area-128")

    def test_tampered_proof_is_freshly_rejected_even_with_rebound_file_hash(self):
        bundle=self.produce()
        proof=load_json(bundle/"area-128-proof.json")
        proof["steps"].pop()
        write_json(bundle/"area-128-proof.json",proof)
        self.rebind(bundle,"area-128-proof.json")
        with self.assertRaises(InvalidProof):
            export_p1(bundle,"area-128",EXAMPLE/"reveal.svg","Name",self.root/"export")
        self.assertFalse((self.root/"export").exists())

    def test_changed_matrix_or_clues_invalidates_old_proof(self):
        for filename,key in (("area-128-candidate.json","matrix"),("area-128-logic.json","row_clues")):
            bundle=self.produce(folder=key)
            data=load_json(bundle/filename)
            if key=="matrix":
                data[key][0][0]="ink"
            else:
                data[key][0]=[{"length":1,"color":"ink"}]
            write_json(bundle/filename,data)
            self.rebind(bundle,filename)
            with self.assertRaises(InvalidInput):
                inspect_candidate(bundle,"area-128")
        bundle=self.produce(folder="diagnostic")
        Image.new("RGB",(20,20),"red").save(bundle/"area-128-raster.png")
        self.rebind(bundle,"area-128-raster.png")
        with self.assertRaises(InvalidInput):
            inspect_candidate(bundle,"area-128")

    def test_stall_and_abort_are_comparable_but_not_exportable(self):
        d=self.small_design(2,2)
        image=Image.new("RGBA",(2,2),(255,255,255,255))
        image.putpixel((0,0),(0,0,0,255))
        image.putpixel((1,1),(0,0,0,255))
        bundle=self.produce(image,d)
        self.assertEqual(inspect_candidate(bundle,"area")[2]["status"],"stalled")
        with self.assertRaises(InvalidInput):
            export_p1(bundle,"area",EXAMPLE/"reveal.svg","Name",self.root/"export")
        design=self.root/"abort-design.json"
        write_json(design,self.design)
        aborted=self.root/"aborted"
        import_image(EXAMPLE/"source.png",design,aborted,max_lines=0)
        self.assertFalse(load_json(aborted/"area-128-result.json")["certified"])
        with self.assertRaises(InvalidInput):
            export_p1(aborted,"area-128",EXAMPLE/"reveal.svg","Name",self.root/"abort-export")

    def test_p1_rejects_color_rectangular_and_wrong_assets(self):
        for w,h,mode in ((2,1,"mono"),(2,2,"color")):
            d=self.small_design(w,h,mode)
            image=Image.new("RGBA",(w,h),(0,0,0,255))
            bundle=self.produce(image,d,folder=mode)
            with self.assertRaises(InvalidInput):
                export_p1(bundle,"area",EXAMPLE/"reveal.svg","Name",self.root/"export")
        for svg in ('<svg width="40" height="40"><script/></svg>',
                    '<svg width="40" height="40"><image href="https://example.com"/></svg>',
                    '<!DOCTYPE svg><svg width="40" height="40"/>',
                    '<svg width="20" height="20"/>', '<svg width="40" height="41"/>'):
            path=self.root/"bad.svg"
            path.write_text(svg)
            with self.assertRaises(InvalidInput):
                validate_reveal(path,40)

    def test_safe_metadata_offline_html_and_file_handoff(self):
        d=copy.deepcopy(self.design)
        d["origin"]='<script>alert("unsafe")</script>'
        bundle=self.produce(d=d)
        markup=(bundle/"index.html").read_text(encoding="utf-8")
        self.assertNotIn('<script>',markup)
        self.assertIn('&lt;script&gt;',markup)
        self.assertIn('1 Pixel je Zelle',markup)
        self.assertIn('contour-40',markup)
        self.assertEqual((bundle/"original.png").read_bytes(),(EXAMPLE/"source.png").read_bytes())
        for name in ('normalized.png','briefing.txt','area-128-raster.png','area-128-logic.json'):
            self.assertTrue((bundle/name).is_file())

    def test_cli_real_files_and_failure_json(self):
        cmd=[sys.executable,"-m","tools.puzzle_production","import-image","--input",str(EXAMPLE/"source.png"),"--design",str(EXAMPLE/"design.json"),"--output-dir",str(self.root/"cli")]
        done=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(done.returncode,0,done.stderr)
        self.assertEqual(json.loads(done.stdout)["status"],"produced")
        done=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(done.returncode,2)
        self.assertFalse(json.loads(done.stdout)["certified"])


if __name__ == "__main__":
    unittest.main()
