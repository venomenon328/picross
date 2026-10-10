import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import p1_evidence
import p1_current_visual
import p1_product
from p1_preflight import PreflightError


class CurrentProductEvidenceTests(unittest.TestCase):
    def test_manual_scope_is_conservative_and_ci_can_disable_independently(self):
        required = ["--cache-dir", "cache", "--output-dir", "output"]
        default = p1_product.parse_args(required)
        self.assertTrue(default.integration and default.pilots and default.visual)
        chosen = p1_product.parse_args(required + ["--no-integration", "--pilots", "--no-visual"])
        self.assertFalse(chosen.integration)
        self.assertTrue(chosen.pilots)
        self.assertFalse(chosen.visual)

    def test_failure_keeps_actual_scope_and_partial_phase_evidence(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            evidence = p1_evidence.Evidence(output, "Linux", {"core": True, "pilots": True, "visual": False})
            evidence.scope_start("core")
            record = evidence.start("import")
            initial = json.loads((output / "technical/product-report.json").read_text())
            self.assertEqual(initial["active_phase"], "import")
            error = PreflightError("native import failed")
            evidence.complete(record, {"exit_code": -11, "seconds": 2.5}, error)
            evidence.finish(error)
            report = json.loads((output / "product-report.json").read_text())
            self.assertEqual(report["status"], "failure")
            self.assertEqual(report["checks"][0]["status"], "failure")
            self.assertEqual(report["scope"]["core"]["status"], "failure")
            self.assertEqual(report["scope"]["pilots"]["status"], "not_run")
            self.assertEqual(report["scope"]["visual"]["status"], "not_applicable")
            self.assertIn("--no-visual", report["scope"]["visual"]["reason"])
            self.assertEqual((output / "product-report.json").read_bytes(),
                             (output / "technical/product-report.json").read_bytes())

    def test_process_failure_and_timeout_retain_diagnostics(self):
        with tempfile.TemporaryDirectory() as temporary, contextlib.redirect_stdout(io.StringIO()):
            logs = Path(temporary)
            failed = p1_product.run_phase("failed", [sys.executable, "-c", "print('useful failure'); raise SystemExit(7)"], os.environ.copy(), 5, logs)
            self.assertEqual(failed["exit_code"], 7)
            self.assertIn("useful failure", (logs / "failed.log").read_text())
            timed = p1_product.run_phase("timeout", [sys.executable, "-u", "-c", "import time; print('before timeout'); time.sleep(5)"], os.environ.copy(), 0.2, logs)
            self.assertTrue(timed["timed_out"])
            self.assertIsNone(timed["exit_code"])
            self.assertIn("before timeout", (logs / "timeout.log").read_text())

    def test_log_abbreviation_cannot_hide_a_success_exit_engine_error(self):
        with tempfile.TemporaryDirectory() as temporary, contextlib.redirect_stdout(io.StringIO()):
            command = [sys.executable, "-c", "print('A'*100000); print('SCRIPT ERROR: middle'); print('B'*400000); print('OK')"]
            result = p1_product.run_phase("large", command, os.environ.copy(), 5, Path(temporary))
            self.assertLessEqual((Path(temporary) / "large.log").stat().st_size, p1_evidence.LOG_LIMIT)
            self.assertTrue(result["log"]["abbreviated"])
            with self.assertRaisesRegex(PreflightError, "engine error"):
                p1_product.require_clean_output(result, "OK")

    def test_native_selection_preserves_original_bytes_and_records_budget_omissions(self):
        with tempfile.TemporaryDirectory() as temporary, patch.object(p1_evidence, "IMAGE_LIMIT", 8):
            output = Path(temporary)
            renders = output / "renders"
            renders.mkdir()
            first, second = renders / "first.png", renders / "second.png"
            first.write_bytes(b"original")
            second.write_bytes(b"original-two")
            evidence = p1_evidence.Evidence(output, "Linux", {"visual": True})
            evidence.retain_files([first, second])
            selected = output / "technical/selected/renders/first.png"
            self.assertEqual(selected.read_bytes(), first.read_bytes())
            self.assertEqual(len(evidence.report["selected_evidence"]["omitted"]), 1)
            evidence.retain_files([second])
            self.assertFalse(selected.exists())

    def test_aggregate_budget_counts_player_and_technical_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            evidence = p1_evidence.Evidence(output, "Linux", {"core": True})
            player = output / "player.zip"
            player.write_bytes(b"player")
            exact = evidence.enforce_budget(player)
            self.assertEqual(exact["total_bytes"], exact["technical_bytes"] + 6)
            with patch.object(p1_evidence, "TOTAL_LIMIT", exact["total_bytes"] - 1):
                with self.assertRaisesRegex(PreflightError, "byte budget"):
                    evidence.enforce_budget(player)

    def test_source_override_does_not_hide_dirty_checkout_or_change_tested_identity(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            def git(*args):
                return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True).stdout.strip()
            git("init", "--quiet")
            (root / "tracked.txt").write_text("initial\n")
            git("add", "tracked.txt")
            git("-c", "user.name=CI test", "-c", "user.email=ci@example.invalid", "commit", "--quiet", "-m", "fixture")
            checkout = git("rev-parse", "HEAD")
            (root / "tracked.txt").write_text("modified\n")
            with patch.dict(os.environ, {"P1_PREFLIGHT_SOURCE_COMMIT": "a" * 40, "P1_BASE_COMMIT": "b" * 40, "GITHUB_ACTIONS": "true"}):
                identity = p1_evidence.source_identity(root)
            self.assertEqual(identity["source_commit"], "a" * 40)
            self.assertEqual(identity["base_commit"], "b" * 40)
            self.assertEqual(identity["tested_checkout_commit"], checkout)
            self.assertTrue(identity["source_tree_dirty"])

    def test_early_download_failure_still_writes_uploadable_report(self):
        with tempfile.TemporaryDirectory() as temporary, contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            output = Path(temporary) / "output"
            source = {"source_commit": "a" * 40, "base_commit": "b" * 40,
                      "tested_checkout_commit": "c" * 40, "source_tree_dirty": False}
            with patch("p1_product.source_identity", return_value=source), \
                    patch("p1_product.toolchain.request_json", side_effect=OSError("download unavailable")):
                result = p1_product.main(["--cache-dir", str(Path(temporary) / "cache"),
                    "--output-dir", str(output), "--no-integration", "--no-pilots", "--no-visual"])
            self.assertEqual(result, 1)
            report = json.loads((output / "technical/product-report.json").read_text())
            self.assertEqual(report["status"], "failure")
            self.assertEqual(report["source_commit"], "a" * 40)
            self.assertEqual(report["checks"][-1]["name"], "verified-toolchain-assets")
            self.assertIn("download unavailable", (output / "technical/logs/failure.log").read_text())

    def test_failed_pixel_oracle_keeps_its_report_bound_crops_before_other_images(self):
        with tempfile.TemporaryDirectory() as temporary, patch.object(p1_evidence, "IMAGE_LIMIT", 8):
            output = Path(temporary)
            renders = output / "drawing-renders"
            renders.mkdir()
            crop, context, unrelated = (renders / name for name in ("x-crop.png", "x-context.png", "a-unrelated.png"))
            for path in (crop, context, unrelated):
                path.write_bytes(b"raw!")
            inputs = [{"controlled": [{"file": crop.name}], "context": context.name}]
            (renders / "zs2-after.json").write_text(json.dumps({
                "rework_sequences": inputs, "captures": [{"file": unrelated.name}]}))
            def failing_oracle():
                raise PreflightError("native X stroke order is wrong")
            with self.assertRaises(PreflightError) as raised:
                p1_current_visual.pixel_oracle(renders, inputs, failing_oracle)
            files, priority = p1_evidence.native_failure_sources(
                output, "current-drawing-pixel-oracles", raised.exception.p1_failure_images)
            self.assertEqual(set(priority), {crop, context})
            evidence = p1_evidence.Evidence(output, "Linux", {"visual": True})
            evidence.retain_files(files, priority_sources=priority)
            selected = output / "technical/selected/drawing-renders"
            self.assertEqual((selected / crop.name).read_bytes(), crop.read_bytes())
            self.assertEqual((selected / context.name).read_bytes(), context.read_bytes())
            self.assertFalse((selected / unrelated.name).exists())
            self.assertTrue((selected / "zs2-after.json").is_file())

    def test_native_failure_frames_use_phase_reports_and_reject_unbound_paths(self):
        for phase, filename in (("current-book-capture", "z2-renders.json"),
                                ("rp6-f07-render", "rp6-f07-renders.json")):
            with self.subTest(phase=phase), tempfile.TemporaryDirectory() as temporary:
                output = Path(temporary)
                renders = output / "renders"
                renders.mkdir()
                failed = renders / "failed-native.png"
                failed.write_bytes(b"original failed frame")
                outside = output / "outside.png"
                outside.write_bytes(b"outside report directory")
                report = {"captures": [{"file": "missing.png"}, {"file": "../outside.png"}],
                          "failure_captures": [{"file": failed.name}]}
                (renders / filename).write_text(json.dumps(report))
                files, priority = p1_evidence.native_failure_sources(output, phase, [outside])
                self.assertEqual(priority, [failed])
                self.assertIn(failed, files)
                self.assertNotIn(outside, files)
                self.assertNotIn(renders / "missing.png", files)
