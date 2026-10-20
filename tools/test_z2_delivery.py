import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import shutil
import hashlib

import z2_resources


class Z2DeliveryTests(unittest.TestCase):
    def test_hz_rejects_changed_font_or_missing_permission(self):
        manifest = z2_resources.verify()
        self.assertEqual(manifest["hz_standard_text"]["sha256"],
                         "9eacc0d857ab9decbc34b0dab150641ba5b5a9560a8d163b6494dd5babbcdfd6")
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            drawing = root / "game/art/drawing"
            (drawing / "tidy-hand").mkdir(parents=True)
            source = z2_resources.ROOT / "game/art/drawing"
            font = drawing / "TidyHand.ttf"
            notice = drawing / "tidy-hand/NOTICE.txt"
            shutil.copyfile(source / "TidyHand.ttf", font)
            shutil.copyfile(source / "tidy-hand/NOTICE.txt", notice)
            with patch.object(z2_resources, "ROOT", root):
                z2_resources.verify()
                font.write_bytes(font.read_bytes() + b"changed")
                with self.assertRaisesRegex(AssertionError, "original bytes"):
                    z2_resources.verify()
                shutil.copyfile(source / "TidyHand.ttf", font)
                notice.write_text("No author permission", encoding="utf-8")
                with self.assertRaises(AssertionError):
                    z2_resources.verify()

    def test_resources_match_selected_hashes_and_utf8_labels(self):
        manifest = z2_resources.verify()
        self.assertEqual(manifest["source_commit"], "c3a5386580d7a0da29b927b41bd692f0cca59274")
        icons = json.loads((z2_resources.DEST / "icons.json").read_text(encoding="utf-8"))
        source = json.loads((z2_resources.SOURCE / "composition/inputs/icons.json").read_text(encoding="utf-8"))
        self.assertEqual(icons["fill"][:2], source["fill"][:2])
        self.assertNotEqual(icons["fill"][2], source["fill"][2])
        self.assertEqual(icons["fill"][0], "Füllen")
        self.assertTrue({"Fraunces-OFL.txt", "PlexSans-OFL.txt", "Fraunces.ttf", "PlexSans.ttf"}
                        <= {entry["file"] for entry in manifest["files"]})

    def test_kb_provision_is_idempotent_and_verifies_active_icon_bytes(self):
        with TemporaryDirectory() as temporary:
            destination = Path(temporary) / "book"
            shutil.copytree(z2_resources.DEST, destination)
            with patch.object(z2_resources, "DEST", destination):
                before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in destination.iterdir() if p.is_file()}
                z2_resources.provision()
                z2_resources.verify()
                binding = destination / "manifest.json"
                original = binding.read_bytes()
                manifest = json.loads(original)
                manifest["hz_icon_source"]["sha256"] = "0" * 64
                binding.write_text(json.dumps(manifest), encoding="utf-8")
                with self.assertRaisesRegex(AssertionError, "HZ icon source"):
                    z2_resources.verify()
                binding.write_bytes(original)
                self.assertEqual(before, {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in destination.iterdir() if p.is_file()})
                self.assertNotEqual((destination / "reset.svg").read_bytes(), (destination / "undo.svg").read_bytes())
                (destination / "play.svg").write_text("corrupted", encoding="utf-8")
                with self.assertRaises(AssertionError):
                    z2_resources.verify()
                z2_resources.provision()
                z2_resources.verify()
                (destination / "extra.svg").write_text("extra", encoding="utf-8")
                with self.assertRaises(AssertionError):
                    z2_resources.verify()


if __name__ == "__main__":
    unittest.main()
