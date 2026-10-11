"""Asset mutations exercise independent PERF-A spatial/resource oracles."""
import importlib.metadata
import json
import shutil
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import perf_a_atlas as atlas


def pinned_images():
    try: return importlib.metadata.version("Pillow")=="12.3.0"
    except importlib.metadata.PackageNotFoundError: return False


@unittest.skipUnless(pinned_images(), "image checks run in pinned product image environment")
class AtlasTests(unittest.TestCase):
    def test_independent_color_basis_preserves_alpha_and_white_contribution(self):
        Image, _ = atlas.image_api()
        with tempfile.TemporaryDirectory() as temporary:
            sources=Path(temporary)
            Image.new("RGBA",(1,1),(200,200,200,200)).save(sources/"fill-medium-white.png")
            Image.new("RGBA",(1,1),(20,20,20,200)).save(sources/"fill-medium-black.png")
            Image.new("RGBA",(1,1),(200,200,200,200)).save(sources/"x-medium-white.png")
            with patch.object(atlas,"SOURCES",sources):
                self.assertEqual(atlas.basis_color("medium",(51,102,153)).getpixel((0,0)),(56,92,128,200))
                self.assertEqual(atlas.basis_color("medium",(51,102,153),"x").getpixel((0,0)),(40,80,120,200))

    def test_bound_resources(self):
        resources = atlas.verify()
        self.assertEqual(resources["textures"], 6)
        self.assertLess(resources["decoded_rgba_bytes"], 50000000)

    def test_spatial_negative_controls(self):
        Image, _ = atlas.image_api()
        plan = json.loads(atlas.PLAN.read_text(encoding="utf-8"))
        level = plan["levels"][1]
        image = Image.open(atlas.ASSETS / "fill-medium.png").convert("RGBA")
        pitch, pad, pixels = level["pixels"]+4, 2, level["pixels"]
        last = image.crop((23*pitch+pad, pad, 23*pitch+pad+pixels, pad+pixels))
        for mutation in ("underdrawing", "fade", "duplicate", "padding"):
            wrong = image.copy()
            if mutation == "underdrawing": wrong.paste(last,(pad,pad))
            elif mutation == "fade":
                for f in range(1,23):
                    faded=last.copy()
                    faded.putalpha(last.getchannel("A").point(lambda a: max(1,round(a*f/23)) if a else 0))
                    wrong.paste(faded,(f*pitch+pad,pad))
            elif mutation == "duplicate": wrong.paste(last,(23*pitch+pad,pitch+pad))
            else: wrong.putpixel((0,0),(255,0,0,255))
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                atlas.spatial_oracle(wrong,plan,level,"fill")
        x=Image.open(atlas.ASSETS / "x-medium.png").convert("RGBA")
        # Horizontal reflection makes the NE/SW diagonal start first.
        for f in range(24):
            tile=x.crop((f*pitch+pad,pad,f*pitch+pad+pixels,pad+pixels)).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            x.paste(tile,(f*pitch+pad,pad))
        with self.assertRaises(ValueError): atlas.spatial_oracle(x,plan,level,"x")

    def test_file_and_import_identity_negatives(self):
        # Verification must reject changed files before expensive reproduction.
        with tempfile.TemporaryDirectory(prefix="picross-perfa-negative-") as temporary:
            assets=Path(temporary)/"atlases"
            shutil.copytree(atlas.ASSETS,assets)
            image=assets/"fill-small.png"
            original=image.read_bytes()
            image.write_bytes(original+b"altered")
            with self.assertRaisesRegex(ValueError,"identity"): atlas.verify(assets)
            image.write_bytes(original)
            settings=assets/"fill-small.png.import"
            settings.write_text(settings.read_text().replace("fix_alpha_border=false","fix_alpha_border=true"),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"import"): atlas.verify(assets)

    def test_motion_rejects_empty_and_stale_native_frames(self):
        Image, _ = atlas.image_api()
        with tempfile.TemporaryDirectory(prefix="picross-perfa-motion-negative-") as temporary:
            folder=Path(temporary)
            blank=Image.new("RGBA",(964,28))
            visible=blank.copy()
            visible.paste((120,60,30,255),(2,2,20,24))
            visible.save(folder/"motion-fill-waiting.png")
            visible.save(folder/"motion-fill-rest.png")
            records=[dict(elapsed_us=t,first_frame=f,last_frame=23,last_state=s,file=f"{i}.png")
                     for i,(t,f,s) in enumerate([(0,0,"waiting"),(10000,1,"waiting"),(20000,2,"waiting"),(450000,23,"rest")])]
            for wrong, error in ((blank,"empty"),(visible,"stale")):
                for record in records: wrong.save(folder/record["file"])
                with self.assertRaisesRegex(ValueError,error): atlas.motion_oracle(folder,records,"fill")


if __name__ == "__main__": unittest.main()
