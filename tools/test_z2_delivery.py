import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import shutil
import hashlib

import z2_resources


class Z2DeliveryTests(unittest.TestCase):
    def test_resources_match_selected_hashes_and_utf8_labels(self):
        manifest = z2_resources.verify()
        self.assertEqual(manifest["source_commit"], "c3a5386580d7a0da29b927b41bd692f0cca59274")
        icons = json.loads((z2_resources.DEST / "icons.json").read_text(encoding="utf-8"))
        source = json.loads((z2_resources.SOURCE / "composition/inputs/icons.json").read_text(encoding="utf-8"))
        self.assertEqual(icons["fill"], source["fill"])
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
