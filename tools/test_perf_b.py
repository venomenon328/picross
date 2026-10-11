"""B provenance and approved E1 boundary regressions."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import shutil
import perf_b_resources as resources
import perf_b_report
import p1_evidence as evidence
from p1_preflight import PreflightError


class PerfBTests(unittest.TestCase):
    def test_comparison_rejects_changed_runtime_archive_and_summary(self):
        source = resources.ROOT / "examples/perf_b"
        self.assertEqual(perf_b_report.verify(source)["current_cases"], 120)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            report = json.loads((source / "b1-windows.json").read_text())
            target = root / "b1-windows.json"
            target.write_text(json.dumps(report))
            archive = root / report["raw_archive"]["file"]
            shutil.copyfile(source / archive.name, archive)
            report["current_cases"][0]["after"]["wall_us"]["p50"] = -1
            target.write_text(json.dumps(report))
            with self.assertRaisesRegex(ValueError, "archived summaries"):
                perf_b_report.verify(root)
            shutil.copyfile(source / target.name, target)
            with archive.open("ab") as stream: stream.write(b"x")
            with self.assertRaisesRegex(ValueError, "archive identity"):
                perf_b_report.verify(root)
            runtime = root / "prototypes/p1/ui"
            runtime.mkdir(parents=True)
            for filename in report["runtime_files"]:
                shutil.copyfile(resources.ROOT / "prototypes/p1/ui" / filename, runtime / filename)
            with (runtime / "atlas_marks.gd").open("ab") as stream: stream.write(b"\n")
            with self.assertRaisesRegex(ValueError, "Measured runtime changed"):
                perf_b_report.verify(source, root)

    def test_historical_manufacturer_is_not_current_adapter(self):
        files = resources.historical_files()
        self.assertNotEqual(files["tools/perf_a_atlas.py"], (resources.ROOT / "tools/perf_a_atlas.py").read_bytes())
        with tempfile.TemporaryDirectory() as temporary:
            snapshot = Path(temporary) / "wrong.zip"
            with zipfile.ZipFile(snapshot, "w") as archive:
                for path, data in files.items():
                    archive.writestr(path, data + b"\n" if path.endswith("pencil_marks.gd") else data)
            with self.assertRaisesRegex(ValueError, "archive identity"):
                resources.historical_files(snapshot)
            # Even if someone rebinds the container, original manufacturer hashes
            # still reject substituting B for A.
            plan = json.loads((resources.ROOT / "examples/perf_b/plan.json").read_text())
            plan["a_source_archive_sha256"] = hashlib.sha256(snapshot.read_bytes()).hexdigest()
            original = json.loads
            def loads(text, **kwargs):
                result = original(text, **kwargs)
                return plan if result.get("format") == "picross-perf-b-plan-v1" else result
            with patch.object(resources.json, "loads", side_effect=loads), self.assertRaisesRegex(ValueError, "manufacturer identity"):
                resources.historical_files(snapshot)

    def test_active_atlases_preserve_a_bytes(self):
        self.assertEqual(len(resources.verify_runtime()["atlases"]), 6)

    def test_e1_exact_technical_and_total_boundaries(self):
        self.assertEqual((evidence.TECHNICAL_LIMIT, evidence.TOTAL_LIMIT), (30_000_000, 75_000_000))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = evidence.Evidence(root, "Windows", {})
            technical = bundle.technical / "native-evidence.bin"
            player = root / "player.zip"
            existing = bundle.enforce_budget()["technical_bytes"]
            with technical.open("wb") as stream: stream.truncate(30_000_000 - existing)
            with player.open("wb") as stream: stream.truncate(45_000_000)
            self.assertEqual(bundle.enforce_budget(player)["total_bytes"], 75_000_000)
            with technical.open("ab") as stream: stream.write(b"x")
            with self.assertRaises(PreflightError): bundle.enforce_budget()
            with technical.open("r+b") as stream: stream.truncate(30_000_000 - existing)
            with player.open("ab") as stream: stream.write(b"x")
            with self.assertRaises(PreflightError): bundle.enforce_budget(player)
