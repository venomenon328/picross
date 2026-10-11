"""Current runtime resources and approved E1 boundary regressions."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import shutil
import perf_b_resources as resources
import p1_evidence as evidence
from p1_preflight import PreflightError


class PerfBTests(unittest.TestCase):
    def test_selected_native_scope_cannot_finish_as_success_without_execution(self):
        for status in ("pending", "running", "not_run"):
            with tempfile.TemporaryDirectory() as temporary:
                bundle = evidence.Evidence(Path(temporary), "Windows", {"perf_b": True})
                bundle.report["scope"]["perf_b"]["status"] = status
                with self.assertRaisesRegex(PreflightError, "Required coverage incomplete"):
                    bundle.finish()
                self.assertEqual(bundle.report["status"], "failure")
        with tempfile.TemporaryDirectory() as temporary:
            bundle = evidence.Evidence(Path(temporary), "Windows", {"perf_b": True})
            bundle.scope_start("perf_b")
            bundle.scope_done("perf_b")
            bundle.finish()
            self.assertEqual(bundle.report["status"], "success")

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

    def copy_runtime(self, root):
        # Deliberately no manufacturer, old project, source archive or B report.
        for name in ("game/art/cells", "game/ui"):
            shutil.copytree(resources.ROOT / name, root / name)
        (root / "tools").mkdir()
        shutil.copyfile(resources.ROOT / resources.REFERENCE, root / resources.REFERENCE)

    def test_runtime_passes_without_historical_inputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.copy_runtime(root)
            result = resources.verify_runtime(root)
            self.assertEqual(result, resources.verify_runtime())
            self.assertEqual(len(result["atlases"]), 6)
            self.assertEqual(result["decoded_bytes"], 48906240)
            self.assertFalse((root / "game/perf_a").exists())
            self.assertFalse((root / "examples").exists())

    def test_runtime_rejects_missing_extra_changed_and_misimported_resources(self):
        for mutation in ("missing", "missing-import", "extra", "changed", "compression", "mipmap", "premultiplied", "srgb", "wrong-source"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                self.copy_runtime(root)
                png = root / "game/art/cells/fill-small.png"
                settings = png.with_suffix(".png.import")
                if mutation == "missing": png.unlink()
                elif mutation == "missing-import": settings.unlink()
                elif mutation == "extra": (png.parent / "obsolete.png").write_bytes(png.read_bytes())
                elif mutation == "changed": png.write_bytes(png.read_bytes() + b"changed")
                else:
                    before, after = {"compression": ("compress/mode=0", "compress/mode=2"),
                        "mipmap": ("mipmaps/generate=false", "mipmaps/generate=true"),
                        "premultiplied": ("process/premult_alpha=false", "process/premult_alpha=true"),
                        "srgb": ("process/hdr_as_srgb=false", "process/hdr_as_srgb=true"),
                        "wrong-source": ("res://art/cells/", "res://other/")}[mutation]
                    settings.write_text(settings.read_text().replace(before, after), encoding="utf-8", newline="\n")
                with self.assertRaises(ValueError): resources.verify_runtime(root)

    def test_png_contract_rejects_rebound_wrong_dimensions_or_encoding(self):
        for offset in (19, 25):  # IHDR width and color type, independently of the file hash.
            with self.subTest(offset=offset), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                self.copy_runtime(root)
                png = root / "game/art/cells/fill-small.png"
                data = bytearray(png.read_bytes())
                data[offset] ^= 1
                png.write_bytes(data)
                path = root / resources.REFERENCE
                reference = json.loads(path.read_text())
                item = next(item for item in reference["atlases"] if item["file"] == png.name)
                item["sha256"] = hashlib.sha256(data).hexdigest()
                path.write_text(json.dumps(reference), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "PNG encoding/dimensions differ"):
                    resources.verify_runtime(root)

    def test_reference_rejects_empty_duplicate_traversal_and_invalid_metadata(self):
        for mutation in ("empty", "duplicate", "traversal", "size", "memory", "hash", "version", "frames"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                self.copy_runtime(root)
                path = root / resources.REFERENCE
                data = json.loads(path.read_text())
                if mutation == "empty": data["atlases"] = []
                elif mutation == "duplicate": data["atlases"][-1] = data["atlases"][0]
                elif mutation == "traversal": data["atlases"][0]["file"] = "../fill-small.png"
                elif mutation == "size": data["atlases"][0]["size"] = [1, 1]
                elif mutation == "memory": data["atlases"][0]["decoded_bytes"] = 0
                elif mutation == "hash": data["atlases"][0]["pixel_sha256"] = "invalid"
                elif mutation == "version": data["render_version"] = "wrong"
                elif mutation == "frames": data["frames"] = 1
                path.write_text(json.dumps(data), encoding="utf-8")
                with self.assertRaises(ValueError): resources.verify_runtime(root)
