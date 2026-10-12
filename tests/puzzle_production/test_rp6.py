"""Generic size/codec boundaries of the retained pilot adapter profiles."""
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from PIL import Image

from tools.puzzle_production.contract import InvalidInput
from tools.puzzle_production.p1_export import export_p1, export_pilot, validate_pilot_reveal


class PilotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)


    def test_both_p1_export_profiles_reject_51_on_either_axis(self):
        bundle = self.path / "unused-bundle"
        bundle.mkdir()
        (bundle / "manifest.json").write_text("{}\n")
        for width, height in ((51,50),(50,51)):
            candidate = {"design":{"width":width,"height":height,"mode":"mono"},
                         "matrix":[["ink"]],"id":"bound-test"}
            checked = {"certified":True,"status":"solved"}
            with patch("tools.puzzle_production.p1_export.inspect_candidate",
                       return_value=(candidate,{},checked)):
                for profile in ("first","pilot"):
                    with self.subTest(width=width,height=height,profile=profile), self.assertRaisesRegex(InvalidInput,"at most 50"):
                        args = (bundle,"area-128",self.path/"unused.png","Name",self.path/"unused")
                        if profile=="first": export_p1(*args)
                        else: export_pilot(*args,"F-06")


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


if __name__ == "__main__":
    unittest.main()
