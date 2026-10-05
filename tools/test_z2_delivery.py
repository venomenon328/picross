import json
import tempfile
import unittest
import zipfile
from pathlib import Path

import z2_resources
import z2_review
from p1_preflight import sha256_file


class Z2DeliveryTests(unittest.TestCase):
    def test_resources_match_selected_hashes_and_utf8_labels(self):
        manifest = z2_resources.verify()
        self.assertEqual(manifest["source_commit"], z2_review.BASE)
        icons = json.loads((z2_resources.DEST / "icons.json").read_text(encoding="utf-8"))
        source = json.loads((z2_resources.SOURCE / "composition/inputs/icons.json").read_text(encoding="utf-8"))
        self.assertEqual(icons["fill"], source["fill"])
        self.assertEqual(icons["fill"][0], "Füllen")
        self.assertTrue({"Fraunces-OFL.txt", "PlexSans-OFL.txt", "Fraunces.ttf", "PlexSans.ttf"}
                        <= {entry["file"] for entry in manifest["files"]})

    def test_review_binds_exact_images_and_windows_archive(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "docs").mkdir()
            (root / "docs/Z2_VERIFICATION.md").write_text("OPEN: owner", encoding="utf-8")
            (root / "renders").mkdir()
            image = root / "renders/z2-f02-1920.png"
            image.write_bytes(b"exact render bytes")
            windows = root / "windows.zip"
            windows.write_bytes(b"exact export bytes")
            manifest = dict(source_commit="a" * 40, tested_checkout_commit="b" * 40,
                            source_tree_dirty=False, base_commit=z2_review.BASE,
                            github_run_id="123", host="Windows", book_resources={})
            archive = z2_review.package(root, root, manifest, windows)
            with zipfile.ZipFile(archive) as bundle:
                binding = json.loads(bundle.read("z2-binding.json"))
                self.assertEqual(binding["windows_zip"]["sha256"], sha256_file(windows))
                self.assertEqual(binding["images"][image.name], sha256_file(image))
                self.assertEqual(bundle.read("renders/" + image.name), image.read_bytes())
                self.assertEqual(binding["tested_checkout_commit"], "b" * 40)
                self.assertIn("NOT PERFORMED: Z2-M01/M02/M03", binding["owner_acceptance"])
                self.assertIn("owner waived gate for merged PR #33", binding["owner_acceptance"])
                self.assertIn("RP3 review remains separate", binding["owner_acceptance"])
                self.assertNotIn("windows.zip", bundle.namelist())


if __name__ == "__main__":
    unittest.main()
