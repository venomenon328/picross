"""Offline regressions for the manual main player build and flat artifact."""
from pathlib import Path
import tempfile
import unittest

from build_main_player import stage_player
import p1_preflight as toolchain

ROOT = Path(__file__).resolve().parents[1]
SHA = "0123456789abcdef" * 2 + "01234567"


class MainPlayerBuildTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.workspace = Path(self.temporary.name)
        self.build = self.workspace / "build"
        self.build.mkdir()
        (self.build / "picross-p1.exe").write_bytes(b"win-main")
        (self.build / "picross-p1.console.exe").write_bytes(b"win-console")
        self.output = self.workspace / "output"
        self.license = self.workspace / "LICENSE.txt"
        self.license.write_text("license\n", encoding="utf-8")

    def stage(self, extras=None):
        return stage_player(self.build, self.output, SHA, "Spielanleitung\n",
                            {"licenses/LICENSE.txt": self.license} if extras is None else extras)

    def test_single_flat_player_archive_input(self):
        (self.build / "picross-p1.pck").write_bytes(b"pack")
        files = self.stage({"licenses/LICENSE.txt": self.license,
                            "rp6-owner.ps1": self.license,
                            "SPIELANLEITUNG.md": self.license})
        self.assertEqual(files, [
            "README.txt", "SPIELANLEITUNG.md", "licenses/LICENSE.txt",
            "picross-p1.console.exe", "picross-p1.exe", "picross-p1.pck"])
        self.assertEqual((self.output / "picross-p1.exe").read_bytes(), b"win-main")
        self.assertEqual((self.output / "picross-p1.pck").read_bytes(), b"pack")
        self.assertIn(SHA, (self.output / "README.txt").read_text(encoding="utf-8"))
        self.assertEqual((self.output / "SPIELANLEITUNG.md").read_text(encoding="utf-8"),
                         "Spielanleitung\n")
        self.assertFalse(list(self.output.rglob("*.zip")))
        self.assertFalse((self.output / "rp6-owner.ps1").exists())

    def test_no_empty_or_missing_executables(self):
        (self.build / "picross-p1.exe").write_bytes(b"")
        with self.assertRaisesRegex(toolchain.PreflightError, "Empty Windows"):
            self.stage()
        self.assertFalse(self.output.exists())
        (self.build / "picross-p1.exe").unlink()
        with self.assertRaisesRegex(toolchain.PreflightError, "Incomplete"):
            self.stage()

    def test_reject_unexpected_export_or_preexisting_output(self):
        (self.build / "unknown.txt").write_bytes(b"oops")
        with self.assertRaisesRegex(toolchain.PreflightError, "unexpected Windows"):
            self.stage()
        (self.build / "unknown.txt").unlink()
        self.output.mkdir()
        (self.output / "old.exe").write_bytes(b"old")
        with self.assertRaisesRegex(toolchain.PreflightError, "must be empty"):
            self.stage()

    def test_reject_missing_unsafe_and_archived_extras(self):
        for name, source in (
            ("licenses/missing.txt", self.workspace / "missing.txt"),
            ("../escape.txt", self.license),
            ("licenses/another.zip", self.license),
            ("README.txt", self.license),
        ):
            with self.subTest(name=name), self.assertRaises(toolchain.PreflightError):
                self.stage({name: source})
            self.assertFalse(self.output.exists())

    def test_real_player_extras_and_commit_bound_guide(self):
        # Reuse the existing production source list; don't clone it in this builder.
        from p1_product import player_extras, player_guide
        extras_dir = self.workspace / "extras"
        extras_dir.mkdir()
        extras = player_extras(ROOT, extras_dir)
        guide = player_guide(ROOT, SHA)
        files = stage_player(self.build, self.output, SHA, guide, extras)
        self.assertIn("licenses/resources.json", files)
        self.assertIn("licenses/Chalkboard-NOTICES.md", files)
        self.assertIn("licenses/Bakso-NOTICES.md", files)
        self.assertNotIn("rp6-owner.ps1", files)
        self.assertIn("github.com/venomenon328/picross/blob/" + SHA,
                      (self.output / "SPIELANLEITUNG.md").read_text(encoding="utf-8"))

    def test_workflow_manual_main_and_folder_upload_only(self):
        source = (ROOT / ".github/workflows/build-main-player.yml").read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", source)
        self.assertNotIn("pull_request:", source)
        self.assertNotIn("  push:", source)
        self.assertIn("ref: refs/heads/main", source)
        self.assertIn("tools/build_main_player.py", source)
        self.assertIn("path: ${{ runner.temp }}/picross-main-player/", source)
        self.assertEqual(source.count("actions/upload-artifact@"), 1)
        self.assertNotIn("p1_product.py", source)


if __name__ == "__main__":
    unittest.main()
