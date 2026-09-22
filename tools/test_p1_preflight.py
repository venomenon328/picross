"""Offline tests for the P1.0 Godot preflight harness."""
from __future__ import annotations

import hashlib
import tempfile
import unittest
import zipfile
from pathlib import Path

from p1_preflight import (
    Asset,
    PreflightError,
    create_artifact,
    extract_editor,
    official_asset_urls,
    require_expected_failure,
    safe_member_name,
    verify_sha256,
)


class PreflightHarnessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_sha256_positive_and_negative(self) -> None:
        path = self.root / "asset.zip"
        path.write_bytes(b"official bytes")
        expected = hashlib.sha256(b"official bytes").hexdigest()
        self.assertEqual(expected, verify_sha256(path, expected))
        with self.assertRaisesRegex(PreflightError, "SHA-256 mismatch"):
            verify_sha256(path, "0" * 64)

    def test_release_metadata_must_match_pinned_digest(self) -> None:
        asset = Asset("editor.zip", "a" * 64)
        metadata = {
            "tag_name": "4.7.2-stable",
            "draft": False,
            "prerelease": False,
            "assets": [
                {
                    "name": asset.name,
                    "digest": f"sha256:{asset.sha256}",
                    "browser_download_url": (
                        "https://github.com/godotengine/godot-builds/releases/download/"
                        "4.7.2-stable/editor.zip"
                    ),
                }
            ],
        }
        self.assertIn(asset.name, official_asset_urls(metadata, (asset,)))
        metadata["assets"][0]["digest"] = "sha256:" + "b" * 64
        with self.assertRaisesRegex(PreflightError, "digest changed"):
            official_asset_urls(metadata, (asset,))

    def test_release_metadata_rejects_prerelease(self) -> None:
        with self.assertRaisesRegex(PreflightError, "draft or prerelease"):
            official_asset_urls(
                {"tag_name": "4.7.2-stable", "draft": False, "prerelease": True}, ()
            )

    def test_negative_path_must_fail_for_intended_reason(self) -> None:
        require_expected_failure(
            {"exit_code": 23, "output": "P1_PREFLIGHT_EXPECTED_FAILURE"},
            "P1_PREFLIGHT_EXPECTED_FAILURE",
        )
        with self.assertRaisesRegex(PreflightError, "unexpectedly returned success"):
            require_expected_failure(
                {"exit_code": 0, "output": "P1_PREFLIGHT_EXPECTED_FAILURE"},
                "P1_PREFLIGHT_EXPECTED_FAILURE",
            )
        with self.assertRaisesRegex(PreflightError, "intended failure"):
            require_expected_failure(
                {"exit_code": 23, "output": "different failure"},
                "P1_PREFLIGHT_EXPECTED_FAILURE",
            )

    def test_archive_path_traversal_is_rejected(self) -> None:
        with self.assertRaisesRegex(PreflightError, "Unsafe archive member"):
            safe_member_name("../outside")
        self.assertEqual("templates/version.txt", str(safe_member_name("templates/version.txt")))

    def test_windows_editor_extracts_console_and_required_main_binary(self) -> None:
        archive = self.root / "editor.zip"
        with zipfile.ZipFile(archive, "w") as bundle:
            bundle.writestr("Godot_v4.7.2-stable_win64.exe", b"main")
            bundle.writestr("Godot_v4.7.2-stable_win64_console.exe", b"console")
        destination = self.root / "editor"
        executable = extract_editor(archive, destination, "Windows")
        self.assertEqual("Godot_v4.7.2-stable_win64_console.exe", executable.name)
        self.assertEqual(b"main", (destination / "Godot_v4.7.2-stable_win64.exe").read_bytes())

    def test_artifact_requires_export_and_rejects_extra_files(self) -> None:
        build = self.root / "build"
        output = self.root / "output"
        build.mkdir()
        manifest = {"source_commit": "abc"}
        with self.assertRaisesRegex(PreflightError, "did not produce"):
            create_artifact(build, output, manifest)
        (build / "p1-preflight.exe").write_bytes(b"exe")
        with self.assertRaisesRegex(PreflightError, "p1-preflight.console.exe"):
            create_artifact(build, output, manifest)
        (build / "p1-preflight.console.exe").write_bytes(b"console")
        (build / "unexpected.dll").write_bytes(b"dll")
        with self.assertRaisesRegex(PreflightError, "Unexpected exported files"):
            create_artifact(build, output, manifest)

    def test_artifact_contains_evidence_and_runnable_payload(self) -> None:
        build = self.root / "build"
        output = self.root / "output"
        build.mkdir()
        (build / "p1-preflight.exe").write_bytes(b"exe")
        (build / "p1-preflight.console.exe").write_bytes(b"console")
        archive = create_artifact(build, output, {"source_commit": "abc"})
        with zipfile.ZipFile(archive) as bundle:
            self.assertEqual(
                [
                    "README.txt",
                    "preflight-report.json",
                    "windows/p1-preflight.console.exe",
                    "windows/p1-preflight.exe",
                ],
                sorted(bundle.namelist()),
            )


if __name__ == "__main__":
    unittest.main()
