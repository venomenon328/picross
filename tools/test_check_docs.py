"""Setup validator tests adapted from the pinned dev-rules source, not game tests."""
from __future__ import annotations

import subprocess
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

from check_docs import REQUIRED, check_links, check_tree, prose_only


class DocumentationChecks(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        for name in REQUIRED:
            self.write(name, "# Document\n")
        self.write("docs/dev-rules/VERSION", "0.1.0-rc.1\n")
        self.write("docs/dev-rules/CHANGELOG.md", "# Changes\n\n## 0.1.0-rc.1 – 2026-09-09\n")

    def write(self, name: str, text: str) -> None:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))

    def test_valid_tree(self) -> None:
        self.assertEqual([], check_tree(self.root))

    def test_local_link_and_fragment(self) -> None:
        self.write("README.md", "[Rules](docs/dev-rules/WORKFLOW.md#deliberately-unchecked)\n")
        self.assertEqual([], check_tree(self.root))

    def test_missing_target(self) -> None:
        self.write("README.md", "[Missing](missing.md)\n")
        self.assertTrue(any("missing link target" in e for e in check_tree(self.root)))

    def bind_export_input(self, text: str, relative: str = "input/report.md") -> Path:
        package = "content/packages/pz-example/r03/"
        self.write(package + relative, text)
        self.write(package + "manifest.json", json.dumps({
            "format": "picross-target-export-v1", "definition_id": "pz-example",
            "package_revision": "r03",
            "files": {relative: hashlib.sha256(text.encode("utf-8")).hexdigest()},
        }) + "\n")
        return self.root / (package + relative)

    def test_sealed_export_original_retains_historical_link_context(self) -> None:
        self.bind_export_input("[Historical comparison](views/omitted.png)\n")
        self.assertEqual([], check_tree(self.root))
        self.write("docs/current.md", "[Current comparison](missing.png)\n")
        self.assertTrue(any("docs/current.md: missing link target" in e for e in check_tree(self.root)))

    def test_changed_or_unbound_export_original_keeps_link_check(self) -> None:
        path = self.bind_export_input("[Original](omitted.png)\n")
        path.write_bytes(b"[Changed](also-omitted.png)\n")
        self.assertTrue(any("missing link target" in e for e in check_tree(self.root)))
        for manifest_text in ("{}\n", "not JSON\n", json.dumps({
            "format": "picross-target-export-v1", "definition_id": "pz-other",
            "package_revision": "r03", "files": {"input/report.md": hashlib.sha256(path.read_bytes()).hexdigest()},
        }) + "\n"):
            with self.subTest(manifest=manifest_text):
                self.write("content/packages/pz-example/r03/manifest.json", manifest_text)
                self.assertTrue(any("missing link target" in e for e in check_tree(self.root)))

    def test_sealed_export_text_conventions_still_apply(self) -> None:
        self.bind_export_input("[Historical](omitted.png) \r\nNo final newline")
        errors = check_tree(self.root)
        self.assertTrue(any("LF line endings" in e for e in errors))
        self.assertTrue(any("trailing whitespace" in e for e in errors))
        self.assertTrue(any("final newline" in e for e in errors))

    def test_export_manifest_does_not_exempt_runtime_documentation(self) -> None:
        self.bind_export_input("[Missing](missing.png)\n", "runtime/guide.md")
        self.assertTrue(any("missing link target" in e for e in check_tree(self.root)))

    def test_code_examples_do_not_create_links(self) -> None:
        self.write("README.md", "```text\n[Example](missing.md)\n```\n`[Inline](missing.md)`\n")
        self.assertEqual([], check_tree(self.root))

    def test_tilde_and_long_fences(self) -> None:
        self.assertEqual("kept", prose_only("~~~~text\n[No](x.md)\n~~~\n~~~~\nkept"))

    def test_external_urls_are_not_fetched(self) -> None:
        self.write("README.md", "[External](https://example.invalid/unreachable)\n")
        self.assertEqual([], check_tree(self.root))

    def test_package_link_must_stay_inside_rules(self) -> None:
        self.write("docs/dev-rules/WORKFLOW.md", "[Profile](../PROJECT_PROFILE.md)\n")
        self.assertTrue(any("leaves portable rules package" in e for e in check_tree(self.root)))

    def test_internal_package_link(self) -> None:
        self.write("docs/dev-rules/WORKFLOW.md", "[Selection](MODEL_SELECTION.md)\n")
        self.assertEqual([], check_tree(self.root))

    def test_repository_escape(self) -> None:
        self.write("README.md", "[Outside](../outside.md)\n")
        self.assertTrue(any("leaves repository" in e for e in check_tree(self.root)))

    def test_absolute_file_link(self) -> None:
        self.write("README.md", "[Local](file:///tmp/data.md)\n")
        self.assertTrue(any("non-relative local link" in e for e in check_tree(self.root)))

    def test_encoded_filename(self) -> None:
        self.write("two words.md", "# Target\n")
        self.write("README.md", "[Target](two%20words.md)\n")
        self.assertEqual([], check_tree(self.root))

    def test_trailing_whitespace(self) -> None:
        self.write("README.md", "# Title \n")
        self.assertTrue(any("trailing whitespace" in e for e in check_tree(self.root)))

    def test_crlf_and_missing_final_newline(self) -> None:
        (self.root / "README.md").write_bytes(b"# Title\r\nNo final newline")
        errors = check_tree(self.root)
        self.assertTrue(any("LF line endings" in e for e in errors))
        self.assertTrue(any("final newline" in e for e in errors))

    def test_invalid_utf8(self) -> None:
        (self.root / "README.md").write_bytes(b"\xff\n")
        self.assertTrue(any("cannot read UTF-8" in e for e in check_tree(self.root)))

    def test_bom(self) -> None:
        self.write("README.md", "\ufeff# Title\n")
        self.assertTrue(any("BOM" in e for e in check_tree(self.root)))

    def test_version_and_changelog(self) -> None:
        self.write("docs/dev-rules/VERSION", "1.0.0\n")
        self.assertTrue(any("version heading" in e for e in check_tree(self.root)))
        self.write("docs/dev-rules/VERSION", "1.0.0-rc.0\n")
        self.assertTrue(any("expected MAJOR" in e for e in check_tree(self.root)))

    def test_missing_required_file(self) -> None:
        (self.root / "docs/dev-rules/MODEL_SELECTION.md").unlink()
        self.assertTrue(any("Missing required file" in e for e in check_tree(self.root)))

    def test_ignored_cache(self) -> None:
        self.write("__pycache__/ignore.md", "[Missing](missing.md)")
        self.assertEqual([], check_tree(self.root))

    def test_package_remains_linkable_after_copy(self) -> None:
        relocated = self.root / "project/docs/dev-rules"
        relocated.mkdir(parents=True)
        for source in (self.root / "docs/dev-rules").iterdir():
            (relocated / source.name).write_bytes(source.read_bytes())
        target = relocated / "WORKFLOW.md"
        text = "[Selection](MODEL_SELECTION.md)\n"
        self.assertEqual([], check_links(target, text, self.root / "project"))

    def test_symlink_file_rejected(self) -> None:
        try:
            (self.root / "alias.md").symlink_to(self.root / "README.md")
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks unavailable in this environment")
        self.assertTrue(any("Symlink file" in e for e in check_tree(self.root)))

    def test_cli_exit_codes(self) -> None:
        script = Path(__file__).with_name("check_docs.py")
        result = subprocess.run([sys.executable, str(script), "--root", str(self.root)],
                                capture_output=True, text=True, check=False)
        self.assertEqual(0, result.returncode, result.stderr)
        self.write("README.md", "[Broken](missing.md)\n")
        result = subprocess.run([sys.executable, str(script), "--root", str(self.root)],
                                capture_output=True, text=True, check=False)
        self.assertEqual(1, result.returncode)
        self.assertIn("missing link target", result.stderr)

    def test_project_profile_is_required(self) -> None:
        (self.root / "docs/PROJECT_PROFILE.md").unlink()
        self.assertIn("Missing required file: docs/PROJECT_PROFILE.md", check_tree(self.root))

    def test_ci_definition_is_required(self) -> None:
        (self.root / ".github/workflows/setup.yml").unlink()
        self.assertIn("Missing required file: .github/workflows/setup.yml", check_tree(self.root))


if __name__ == "__main__":
    unittest.main()
