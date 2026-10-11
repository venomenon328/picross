import json
import unittest

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


if __name__ == "__main__":
    unittest.main()
