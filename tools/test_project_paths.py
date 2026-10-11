"""Protect immutable manifest names while resolving the moved live project."""
from pathlib import Path
import tempfile
import unittest

from project_paths import current_path


class RecordedPaths(unittest.TestCase):
    def test_old_and_current_name_resolve_the_same_unchanged_input(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "game/data/f04.json"
            source.parent.mkdir(parents=True)
            source.write_bytes(b"immutable production input")
            self.assertEqual(current_path(root, "prototypes/p1/data/f04.json"), source)
            self.assertEqual(current_path(root, "game/data/f04.json").read_bytes(), source.read_bytes())
            self.assertEqual(current_path(root, "examples/rp6/manifest.json"), root / "examples/rp6/manifest.json")

    def test_untrusted_recorded_paths_cannot_escape_repository(self):
        for name in ("", "../other", "game/../../other", "/etc/file", "C:/file", "C:file", "game\\file"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                current_path(Path("root"), name)
