"""HP-W2: synthetic file contract, independently measured pixels and real I/O."""
import copy
import hashlib
import io
import json
import os
import queue
import shutil
import signal
import struct
import subprocess
import sys
import tempfile
import threading
import unittest
import zlib
from pathlib import Path
from unittest.mock import patch

from PIL import Image, ImageCms, PngImagePlugin
from tools.puzzle_production import background_assets as assets
from tools.puzzle_production import background_io as bio
from tools.puzzle_production.background_contract import BackgroundError
from tests.puzzle_production.background_fixtures import (
    BackgroundFixture, PROFILE, canonical, chunk, chunks, diagnostic, digest,
    file_ref, gray_icc, image_bytes, insert_chunk, pixels, put, put_json,
)

ROOT = Path(__file__).resolve().parents[2]
RESULT_KEYS = {"status", "derivation", "output", "error", "remaining"}


def snapshot(root):
    return {str(path.relative_to(root)): (path.read_bytes(), path.stat().st_mtime_ns)
            for path in Path(root).rglob("*") if path.is_file()}


class BackgroundAssetsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="hp-w2-synthetic-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.number = 0

    def fixture(self, **kwargs):
        self.number += 1
        return BackgroundFixture(self.root / str(self.number), assets.describe(), **kwargs)

    def derive(self, fixture):
        return assets.derive(fixture.request, fixture.source, fixture.output)

    def report(self, fixture):
        return json.loads((fixture.target / "derivation.json").read_bytes())

    def assert_success(self, result, status, directory):
        self.assertEqual(set(result), RESULT_KEYS)
        self.assertEqual(result["status"], status, result)
        self.assertIsNone(result["error"])
        self.assertIsNone(result["remaining"])
        for key in ("derivation", "output"):
            if result[key] is not None:
                self.assertEqual(result[key], file_ref(directory, result[key]["file"]))

    def assert_error(self, result, code, status="invalid_input"):
        self.assertEqual(set(result), RESULT_KEYS)
        self.assertEqual(result["status"], status, result)
        self.assertEqual(set(result["error"]), {"code", "message", "path"})
        self.assertEqual(result["error"]["code"], code, result)
        self.assertTrue(result["error"]["message"].strip())
        self.assertIsNone(result["derivation"])
        self.assertIsNone(result["output"])
        if result["remaining"] is not None:
            self.assertTrue(Path(result["remaining"]).is_absolute())
            self.assertTrue(Path(result["remaining"]).exists())

    def cli(self, *arguments):
        completed = subprocess.run(
            [sys.executable, "-m", "tools.puzzle_production.background_assets", *map(str, arguments)],
            cwd=ROOT, capture_output=True, text=True, timeout=30)
        # json.loads also rejects a second object or trailing progress output.
        return completed.returncode, json.loads(completed.stdout), completed.stderr

    def test_describe_binds_actual_profile_modules_versions_and_import_boundary(self):
        description = assets.describe()
        self.assertEqual(set(description), {"profile", "profile_sha256", "tool", "tool_sha256"})
        self.assertEqual(description["profile"], PROFILE)
        self.assertEqual(description["profile_sha256"], digest(PROFILE))
        tool = description["tool"]
        self.assertEqual(set(tool), {"id", "commit", "dirty", "versions", "modules"})
        self.assertEqual(tool["id"], "picross-background-1")
        self.assertRegex(tool["commit"], r"^[0-9a-f]{40}$")
        self.assertIs(type(tool["dirty"]), bool)
        self.assertEqual(set(tool["versions"]), {"python", "pillow", "zlib", "littlecms"})
        self.assertEqual(tool["versions"]["pillow"], "12.3.0")
        self.assertTrue(all(isinstance(value, str) and value for value in tool["versions"].values()))
        self.assertEqual(description["tool_sha256"], digest(tool))
        names = [entry["file"] for entry in tool["modules"]]
        self.assertEqual(names, sorted(set(names)))
        self.assertIn("tools/puzzle_production/background_assets.py", names)
        for entry in tool["modules"]:
            self.assertEqual(set(entry), {"file", "sha256"})
            self.assertEqual(entry["sha256"], hashlib.sha256((ROOT / entry["file"]).read_bytes()).hexdigest())
        probe = subprocess.run([sys.executable, "-c",
            "import sys; from tools.puzzle_production import background_assets; "
            "assert not any(n in sys.modules for n in "
            "('tools.puzzle_production.solver', 'tools.puzzle_production.authoring_builder', "
            "'tools.puzzle_production.registry'))"], cwd=ROOT, capture_output=True, text=True, timeout=10)
        self.assertEqual(probe.returncode, 0, probe.stderr)

    def test_selected_exact_pixels_alpha_diagnostics_metadata_and_bound_report(self):
        original = pixels((2304, 576))
        fixture = self.fixture(image=original)
        source_before = snapshot(fixture.source)
        result = self.derive(fixture)
        self.assert_success(result, "derived", fixture.target)
        self.assertEqual(set(path.name for path in fixture.target.iterdir()), {"background.png", "derivation.json"})
        report = self.report(fixture)
        self.assertEqual(set(report), {
            "format", "request_sha256", "request", "puzzle_id", "job_id", "background_revision",
            "manifest", "decision", "outcome", "candidate_id", "source", "profile", "profile_sha256",
            "tool", "tool_sha256", "output", "diagnostics", "test_only"})
        self.assertEqual(report["format"], "picross-background-derivation-v1")
        self.assertEqual(report["request"], fixture.request)
        self.assertEqual(report["request_sha256"], digest(fixture.request))
        for field in ("manifest", "decision", "source", "profile"):
            self.assertEqual(report[field], fixture.request[field])
        self.assertEqual(report["profile_sha256"], digest(PROFILE))
        self.assertEqual(report["tool_sha256"], digest(report["tool"]))
        self.assertEqual(report["tool_sha256"], fixture.request["expected_tool_sha256"])
        self.assertTrue(report["test_only"])
        self.assertEqual((fixture.target / "derivation.json").read_bytes(), canonical(report) + b"\n")
        raw = (fixture.target / "background.png").read_bytes()
        png_chunks = chunks(raw)
        self.assertEqual({kind for kind, _ in png_chunks}, {b"IHDR", b"sRGB", b"IDAT", b"IEND"})
        self.assertEqual([value for kind, value in png_chunks if kind == b"sRGB"], [b"\0"])
        with Image.open(io.BytesIO(raw)) as image:
            image.load()
            self.assertEqual((image.format, image.mode, image.size), ("PNG", "RGBA", (2304, 576)))
            self.assertEqual(image.getpixel((0, 0)), (0, 0, 0, 0))
            self.assertEqual(image.getpixel((100, 100)), (90, 60, 30, 128))
            self.assertEqual(image.getpixel((2303, 575)), (40, 50, 60, 255))
            self.assertEqual(report["diagnostics"]["output"], diagnostic(image))
        self.assertEqual(report["diagnostics"]["source"], diagnostic(original))
        self.assertFalse(report["diagnostics"]["upscaled"])
        self.assertEqual(report["output"], file_ref(fixture.target, "background.png"))
        self.assertEqual(snapshot(fixture.source), source_before)

    def test_independent_wide_narrow_odd_padding_and_exif_geometry(self):
        # Expected geometry comes from the published formula, written as constants.
        for size, orientation, oriented, rectangle in (
            ((9, 2), None, (9, 2), (0, 64, 2304, 576)),
            ((5, 7), None, (5, 7), (946, 0, 1357, 576)),
            ((7, 5), 6, (5, 7), (946, 0, 1357, 576)),
        ):
            with self.subTest(size=size, orientation=orientation):
                fixture = self.fixture(image=pixels(size))
                if orientation is not None:
                    exif = Image.Exif()
                    exif[274] = orientation
                    fixture.replace_source(image_bytes(pixels(size), exif=exif))
                self.assert_success(self.derive(fixture), "derived", fixture.target)
                report = self.report(fixture)
                self.assertEqual((report["diagnostics"]["source"]["width"],
                                  report["diagnostics"]["source"]["height"]), oriented)
                self.assertTrue(report["diagnostics"]["upscaled"])
                with Image.open(fixture.target / "background.png") as result:
                    self.assertEqual(result.getchannel("A").getbbox(), rectangle)
                    self.assertEqual(report["diagnostics"]["output"], diagnostic(result))
                    self.assertEqual(result.getpixel((1152, 288))[3], 128)
                    if rectangle[0]:
                        self.assertEqual(result.getpixel((945, 575)), (0, 0, 0, 0))
                        self.assertEqual(result.getpixel((1357, 575)), (0, 0, 0, 0))

    def test_supported_transparency_modes_icc_and_metadata_are_normalized(self):
        palette = Image.new("P", (3, 2), 1)
        palette.putpalette([0, 0, 0, 80, 80, 80] + [0] * 762)
        palette.putpixel((0, 0), 0)
        palette.info["transparency"] = 0
        gray = Image.new("L", (3, 2), 80)
        gray.putpixel((0, 0), 0)
        gray.info["transparency"] = 0
        bilevel = gray.convert("1", dither=Image.Dither.NONE)
        bilevel.putpixel((2, 1), 255)
        bilevel.info["transparency"] = 0
        rgb = Image.new("RGB", (3, 2), (80, 80, 80))
        rgb.putpixel((0, 0), (0, 0, 0))
        rgb.info["transparency"] = (0, 0, 0)
        la = Image.new("LA", (3, 2), (80, 128))
        la.putpixel((0, 0), (80, 0))
        srgb = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
        for name, source, options in (
            ("palette", palette, {}), ("gray", gray, {}), ("bilevel", bilevel, {}),
            ("rgb-trns", rgb, {}), ("gray-alpha", la, {}),
            ("icc", pixels((3, 2)), {"icc_profile": srgb}),
        ):
            with self.subTest(mode=name):
                fixture = self.fixture()
                metadata = PngImagePlugin.PngInfo()
                metadata.add_text("Comment", "Synthetic metadata must not survive")
                fixture.replace_source(image_bytes(source, pnginfo=metadata, **options))
                self.assert_success(self.derive(fixture), "derived", fixture.target)
                self.assertEqual(self.report(fixture)["diagnostics"]["source"], diagnostic(source.convert("RGBA")))
                self.assertEqual({kind for kind, _ in chunks((fixture.target / "background.png").read_bytes())},
                                 {b"IHDR", b"sRGB", b"IDAT", b"IEND"})

    def test_gray_icc_uses_gray_samples_and_preserves_bilevel_and_la_alpha(self):
        profile = gray_icc()
        self.assertEqual(ImageCms.ImageCmsProfile(io.BytesIO(profile)).profile.xcolor_space.strip(), "GRAY")
        for mode in ("1", "L", "LA"):
            with self.subTest(mode=mode):
                gray = 255 if mode == "1" else 80
                source = Image.new(mode, (3, 2), (gray, 128) if mode == "LA" else gray)
                if mode == "LA":
                    source.putpixel((0, 0), (gray, 0))
                else:
                    source.putpixel((0, 0), 0)
                    source.info["transparency"] = 0
                raw = image_bytes(source, icc_profile=profile)
                normal, metadata, _ = assets.normalize_bytes(
                    raw, max_bytes=32 * 1024 * 1024, max_axis=8192, max_pixels=8_000_000)
                # Independent color/alpha expectations from neutral gray and
                # the sRGB transfer curve; no producer-generated golden image.
                self.assertEqual(normal.getpixel((2, 1)), (gray, gray, gray, 128 if mode == "LA" else 255))
                self.assertEqual(normal.getpixel((0, 0))[3], 0)
                self.assertEqual(metadata["color_treatment"], "ICC to sRGB, perceptual intent")
                fixture = self.fixture()
                fixture.replace_source(raw)
                self.assert_success(self.derive(fixture), "derived", fixture.target)
                self.assertEqual(self.report(fixture)["diagnostics"]["source"], {
                    "format": "PNG", "mode": "RGBA", "width": 3, "height": 2,
                    "alpha": {"min": 0, "max": 128 if mode == "LA" else 255,
                              "transparent_pixels": 1, "partial_pixels": 5 if mode == "LA" else 0,
                              "opaque_pixels": 0 if mode == "LA" else 5},
                })
                wrong_profile = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
                mismatched = self.fixture()
                mismatched.replace_source(image_bytes(source, icc_profile=wrong_profile))
                self.assert_error(self.derive(mismatched), "invalid_image")

    def test_none_and_unresolved_rights_are_explicit_technical_results(self):
        fixture = self.fixture(none=True)
        self.assert_success(self.derive(fixture), "none", fixture.target)
        report = self.report(fixture)
        self.assertEqual([path.name for path in fixture.target.iterdir()], ["derivation.json"])
        for field in ("candidate_id", "source", "output"):
            self.assertIsNone(report[field])
        self.assertEqual(report["diagnostics"], {"source": None, "output": None, "upscaled": None})
        self.assertEqual(report["outcome"], "none")
        before = snapshot(fixture.target)
        self.assert_success(self.derive(fixture), "reused", fixture.target)
        self.assertEqual(snapshot(fixture.target), before)
        prepared = self.fixture()
        provenance = prepared.manifest["candidates"][0]["provenance"]
        provenance.update(author=None, usage_basis=None, rights_status="unresolved", evidence=[])
        prepared.refresh()
        self.assert_success(self.derive(prepared), "derived", prepared.target)
        self.assertNotIn("ready", self.report(prepared))
        self.assertIsNone(prepared.manifest["candidates"][0]["review"])

    def test_request_and_nested_forms_are_closed_and_strictly_typed(self):
        for field, value, code in (
            ("format", "picross-background-derive-request-v99", "unsupported_format"),
            ("extra", True, "invalid_request"), ("output", None, "invalid_request"),
            ("profile", {**PROFILE, "upscale": 1}, "invalid_request"),
            ("profile", {**PROFILE, "width": True}, "invalid_request"),
            ("profile", {**PROFILE, "crop": False}, "invalid_request"),
            ("expected_tool_sha256", "0" * 64, "tool_mismatch"),
        ):
            with self.subTest(field=field, value=value):
                fixture = self.fixture()
                fixture.request[field] = value
                self.assert_error(self.derive(fixture), code)
                self.assertFalse(fixture.target.exists() if isinstance(fixture.request["output"], str) else False)
        mutations = (
            lambda m: m.update(extra=True),
            lambda m: m["candidate_policy"].update(count=True),
            lambda m: m["context"].update(extra="not accepted"),
            lambda m: m["candidates"][0]["generation"].update(unknown=[]),
            lambda m: m["candidates"][0]["generation"].update(parameters=[{"name": "x", "value": []}]),
            lambda m: m["candidates"][0]["provenance"].update(rights_status="approved"),
        )
        for index, mutate in enumerate(mutations):
            with self.subTest(nested=index):
                fixture = self.fixture()
                mutate(fixture.manifest)
                fixture.refresh()
                self.assert_error(self.derive(fixture), "invalid_request")
        fixture = self.fixture()
        fixture.request["profile"]["width"] = float("nan")
        self.assert_error(self.derive(fixture), "invalid_request")

    def test_json_bytes_reject_duplicates_bom_nonfinite_and_bad_encoding(self):
        for raw in (b'{"format":"x","format":"y"}', b'\xef\xbb\xbf{}', b'{"x":NaN}',
                    b'{"x":Infinity}', b'{"x":"\xff"}', b'{"x":', b'{} {}'):
            with self.subTest(raw=raw):
                fixture = self.fixture()
                fixture.request["manifest"] = put(fixture.source, "work/bg01.json", raw)
                self.assert_error(self.derive(fixture), "invalid_json")

    def test_fresh_hash_identity_revision_test_only_and_evidence_bindings(self):
        for field, value in (("puzzle_id", "pz-wrong"), ("job_id", "wrong-job"),
                             ("background_revision", "wrong-revision"), ("candidate_id", "B"),
                             ("test_only", False)):
            with self.subTest(field=field):
                fixture = self.fixture()
                fixture.decision[field] = value
                fixture.refresh_decision()
                self.assert_error(self.derive(fixture), "invalid_binding")
        for ref in ("manifest", "decision", "source"):
            with self.subTest(stale_ref=ref):
                fixture = self.fixture()
                fixture.request[ref]["sha256"] = "0" * 64
                self.assert_error(self.derive(fixture), "invalid_binding")
        fixture = self.fixture()
        (fixture.source / "evidence/decision.txt").write_bytes(b"Different actual statement")
        self.assert_error(self.derive(fixture), "invalid_binding")
        fixture = self.fixture()
        (fixture.source / "evidence/rights.txt").unlink()
        self.assert_error(self.derive(fixture), "missing_file")
        for part in ("manifest", "decision"):
            fixture = self.fixture()
            getattr(fixture, part)["format"] += "-future"
            fixture.refresh()
            self.assert_error(self.derive(fixture), "unsupported_format")

    def test_only_chosen_original_is_required_and_no_fallback_to_none(self):
        fixture = self.fixture()
        for candidate in fixture.manifest["candidates"][1:]:
            (fixture.source / candidate["original"]["file"]).unlink()
        self.assert_success(self.derive(fixture), "derived", fixture.target)
        for outcome in ("selected", "rejected"):
            with self.subTest(outcome=outcome):
                fixture = self.fixture()
                if outcome == "selected":
                    fixture.manifest["presentation"] = {"status": "pending", "evidence": None}
                else:
                    fixture.decision.update(outcome="rejected", candidate_id=None, original=None, profile=None)
                fixture.refresh()
                self.assert_error(self.derive(fixture), "invalid_binding")
        fixture = self.fixture(none=True)
        fixture.manifest["candidate_policy"]["exception"] = None
        fixture.refresh()
        self.assert_error(self.derive(fixture), "invalid_request")

    def add_predecessor(self, fixture):
        old_manifest = copy.deepcopy(fixture.manifest)
        old_manifest["revision"] = "older-manifest"
        old = copy.deepcopy(fixture.decision)
        old.update(revision="z-old", background_revision=old_manifest["revision"],
                   manifest=put_json(fixture.source, "history/old-work.json", old_manifest))
        reference = put_json(fixture.source, "history/old-decision.json", old)
        fixture.decision.update(previous_decision=reference, carried_from=copy.deepcopy(reference))
        fixture.refresh()
        return old

    def test_predecessor_and_administrative_carry_bind_exact_original_human_and_context(self):
        fixture = self.fixture()
        self.add_predecessor(fixture)
        self.assert_success(self.derive(fixture), "derived", fixture.target)
        for change in ("context", "candidate_revision", "statement", "history_identity", "cycle"):
            with self.subTest(change=change):
                fixture = self.fixture()
                old = self.add_predecessor(fixture)
                if change == "context":
                    fixture.manifest["context"]["summary"] = "Materially changed synthetic context"
                elif change == "candidate_revision":
                    fixture.manifest["candidates"][0]["revision"] = "b02"
                elif change == "statement":
                    fixture.decision["statement"] = "A different synthetic human declaration"
                elif change == "history_identity":
                    old["job_id"] = "other-job"
                    ref = put_json(fixture.source, "history/old-decision.json", old)
                    fixture.decision.update(previous_decision=ref, carried_from=copy.deepcopy(ref))
                else:
                    # A cyclic path cannot have a valid self-hash. It must still fail closed,
                    # without recursion or accepting the previous recorded bytes as current.
                    fixture.decision["previous_decision"] = copy.deepcopy(fixture.request["decision"])
                fixture.refresh()
                self.assert_error(self.derive(fixture), "invalid_binding")

    def test_image_format_depth_frames_color_and_alpha_failures_are_distinct(self):
        jpeg = io.BytesIO()
        Image.new("RGB", (2, 2)).save(jpeg, "JPEG")
        animated = io.BytesIO()
        pixels((3, 2)).save(animated, "PNG", save_all=True,
                            append_images=[pixels((3, 2), (180, 90, 60, 128))], duration=10, loop=0)
        high_depth = (b"\x89PNG\r\n\x1a\n"
                      + chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 1, 16, 6, 0, 0, 0))
                      + chunk(b"IDAT", zlib.compress(b"\0" + b"\0" * 8 + b"\xff" * 8))
                      + chunk(b"IEND", b""))
        good = image_bytes(pixels((3, 2)))
        for label, raw, code in (
            ("jpeg", jpeg.getvalue(), "invalid_image"), ("apng", animated.getvalue(), "invalid_image"),
            ("16-bit", high_depth, "invalid_image"), ("truncated", good[:-12], "invalid_image"),
            ("corrupt", b"not an image", "invalid_image"),
            ("icc", image_bytes(pixels((3, 2)), icc_profile=b"invalid ICC"), "invalid_image"),
            ("gamma", insert_chunk(good, b"gAMA", struct.pack(">I", 50000)), "invalid_image"),
            ("opaque", image_bytes(Image.new("RGBA", (3, 2), (80, 80, 80, 255))), "opaque_image"),
            ("empty", image_bytes(Image.new("RGBA", (3, 2), (80, 80, 80, 0))), "empty_image"),
        ):
            with self.subTest(image=label):
                fixture = self.fixture()
                fixture.replace_source(raw)
                self.assert_error(self.derive(fixture), code)
                self.assertFalse(fixture.target.exists())

    def test_declared_and_header_resource_limits_precede_decoding(self):
        for size in ((8193, 1), (4000, 2001)):
            with self.subTest(dimensions=size):
                fixture = self.fixture()
                raw = (b"\x89PNG\r\n\x1a\n"
                       + chunk(b"IHDR", struct.pack(">IIBBBBB", *size, 8, 6, 0, 0, 0))
                       + chunk(b"IDAT", zlib.compress(b"\0")) + chunk(b"IEND", b""))
                fixture.replace_source(raw)
                self.assert_error(self.derive(fixture), "resource_limit")
        fixture = self.fixture()
        reference = fixture.manifest["candidates"][0]["original"]
        reference["bytes"] = 32 * 1024 * 1024 + 1
        fixture.decision["original"] = copy.deepcopy(reference)
        fixture.refresh()
        self.assert_error(self.derive(fixture), "resource_limit")
        fixture = self.fixture()
        fixture.request["manifest"]["bytes"] = 2 * 1024 * 1024 + 1
        self.assert_error(self.derive(fixture), "resource_limit")
        fixture = self.fixture()
        fixture.request["manifest"] = put(fixture.source, "work/bg01.json", b"[" * 33 + b"0" + b"]" * 33)
        self.assert_error(self.derive(fixture), "resource_limit")

    def test_reference_graph_file_limit_uses_actual_small_files(self):
        fixture = self.fixture()
        candidate = fixture.manifest["candidates"][0]
        review = {}
        for criterion in ("Q-HG01", "Q-HG02", "Q-HG03", "Q-HG04"):
            evidence = [copy.deepcopy(candidate["original"])]
            evidence.extend(put(fixture.source, f"graph/{criterion}-{index}.txt", b"TEST ONLY")
                            for index in range(63))
            review[criterion] = {
                "result": "erfüllt", "reason": "TEST ONLY synthetic contract graph",
                "method": "Synthetic fixture; no real image approval",
                "norm": {"file": "docs/PUZZLE_QUALITY.md", "contract": "1.0", "document_revision": 1,
                         "commit": "a" * 40, "sha256": "b" * 64},
                "actor": "Synthetic test actor", "timestamp_utc": "2026-01-01T12:00:00Z", "evidence": evidence,
            }
        candidate["review"] = review
        fixture.refresh()
        self.assert_error(self.derive(fixture), "resource_limit")

    def test_repeat_is_byte_and_mtime_noop_and_fresh_roots_are_deterministic(self):
        fixture = self.fixture()
        self.assert_success(self.derive(fixture), "derived", fixture.target)
        before = snapshot(fixture.target)
        sources = snapshot(fixture.source)
        self.assert_success(self.derive(fixture), "reused", fixture.target)
        self.assertEqual(snapshot(fixture.target), before)
        other = fixture.root / "second-output"
        other.mkdir()
        self.assert_success(assets.derive(fixture.request, fixture.source, other),
                            "derived", other / fixture.request["output"])
        self.assertEqual({name: data for name, (data, _) in before.items()},
                         {name: data for name, (data, _) in snapshot(other / fixture.request["output"]).items()})
        self.assertEqual(snapshot(fixture.source), sources)
        (fixture.source / "evidence/decision.txt").write_bytes(b"Stale after successful derivation")
        self.assert_error(self.derive(fixture), "invalid_binding")
        self.assertEqual(snapshot(fixture.target), before)

    def test_verify_transported_embedded_request_is_read_only_for_selected_and_none(self):
        for none in (False, True):
            with self.subTest(none=none):
                fixture = self.fixture(none=none)
                self.assert_success(self.derive(fixture), "none" if none else "derived", fixture.target)
                request_path = fixture.request_file()
                request_path.unlink()
                transported = fixture.root / "transported-result"
                shutil.move(fixture.target, transported)
                embedded = json.loads((transported / "derivation.json").read_bytes())["request"]
                before_output, before_source = snapshot(transported), snapshot(fixture.source)
                self.assert_success(assets.verify(embedded, fixture.source, transported), "verified", transported)
                self.assertEqual(snapshot(transported), before_output)
                self.assertEqual(snapshot(fixture.source), before_source)
                self.assertEqual(embedded["output"], "derived/bg01")

    def test_verify_rejects_unknown_derivation_generation_without_fallback(self):
        fixture = self.fixture(none=True)
        self.assert_success(self.derive(fixture), "none", fixture.target)
        report = self.report(fixture)
        report["format"] = "picross-background-derivation-v99"
        put_json(fixture.target, "derivation.json", report)
        before_source, before_output = snapshot(fixture.source), snapshot(fixture.target)
        self.assert_error(assets.verify(fixture.request, fixture.source, fixture.target), "unsupported_format")
        self.assertEqual(snapshot(fixture.source), before_source)
        self.assertEqual(snapshot(fixture.target), before_output)

    def test_verify_rejects_forged_pixels_even_with_consistently_rewritten_metadata(self):
        for alteration in ("output", "source", "request", "report"):
            with self.subTest(alteration=alteration):
                fixture = self.fixture()
                self.assert_success(self.derive(fixture), "derived", fixture.target)
                report = self.report(fixture)
                request = copy.deepcopy(fixture.request)
                if alteration == "output":
                    with Image.open(fixture.target / "background.png") as old:
                        forged = old.copy()
                    forged.putpixel((1152, 288), (255, 0, 255, forged.getpixel((1152, 288))[3]))
                    metadata = PngImagePlugin.PngInfo()
                    metadata.add(b"sRGB", b"\0")
                    put(fixture.target, "background.png", image_bytes(
                        forged, pnginfo=metadata, compress_level=9, optimize=False))
                    report["output"] = file_ref(fixture.target, "background.png")
                    report["diagnostics"]["output"] = diagnostic(forged)
                    put_json(fixture.target, "derivation.json", report)
                elif alteration == "source":
                    with (fixture.source / request["source"]["file"]).open("ab") as handle:
                        handle.write(b"changed source")
                elif alteration == "request":
                    request["output"] = "different-original-intent"
                else:
                    report["puzzle_id"] = "pz-forged"
                    put_json(fixture.target, "derivation.json", report)
                before = snapshot(fixture.target)
                self.assert_error(assets.verify(request, fixture.source, fixture.target), "invalid_binding")
                self.assertEqual(snapshot(fixture.target), before)
                if alteration in ("output", "report"):
                    self.assert_error(self.derive(fixture), "target_conflict", "conflict")
                    self.assertEqual(snapshot(fixture.target), before)

    def test_unsafe_paths_links_aliases_and_overlapping_roots(self):
        for path in ("../escape", "/absolute", "a\\b", "a//b", "a/./b", "CON/file", "a./b", "a:b"):
            with self.subTest(path=path):
                fixture = self.fixture()
                fixture.request["output"] = path
                self.assert_error(self.derive(fixture), "unsafe_path")
        for kind in ("symlink", "hardlink", "casefold"):
            with self.subTest(kind=kind):
                fixture = self.fixture()
                original = fixture.source / fixture.request["source"]["file"]
                if kind == "casefold":
                    original.with_name(original.name.lower()).write_bytes(original.read_bytes())
                else:
                    other = fixture.source / "another-original.png"
                    original.rename(other)
                    if kind == "symlink":
                        original.symlink_to(other)
                    else:
                        os.link(other, original)
                self.assert_error(self.derive(fixture), "unsafe_path")
        fixture = self.fixture()
        self.assert_error(assets.derive(fixture.request, fixture.source, fixture.source), "unsafe_path")
        self.assert_error(assets.derive(fixture.request, fixture.root, fixture.output), "unsafe_path")
        self.assert_error(assets.derive(fixture.request, fixture.source, ROOT), "unsafe_path")

    def test_foreign_empty_partial_targets_and_publication_race_preserve_foreign_bytes(self):
        for kind in ("empty", "partial", "foreign"):
            with self.subTest(target=kind):
                fixture = self.fixture()
                fixture.target.mkdir(parents=True)
                if kind != "empty":
                    (fixture.target / ("derivation.json" if kind == "partial" else "sentinel.txt")).write_bytes(
                        b"Existing bytes must never be replaced")
                before = snapshot(fixture.target)
                self.assert_error(self.derive(fixture), "target_conflict", "conflict")
                self.assertEqual(snapshot(fixture.target), before)
        for empty in (False, True):
            with self.subTest(racing_empty=empty):
                fixture = self.fixture()
                original_publish = bio.publish_directory

                def race(stage, target):
                    Path(target).mkdir(parents=True)
                    if not empty:
                        (Path(target) / "sentinel.txt").write_bytes(b"Concurrent writer")
                    return original_publish(stage, target)

                with patch.object(bio, "publish_directory", side_effect=race):
                    self.assert_error(self.derive(fixture), "target_conflict", "conflict")
                self.assertEqual(set(path.name for path in fixture.target.iterdir()),
                                 set() if empty else {"sentinel.txt"})
                if not empty:
                    self.assertEqual((fixture.target / "sentinel.txt").read_bytes(), b"Concurrent writer")
                self.assertEqual(list(fixture.output.rglob("background.png")), [])

    def test_source_change_during_render_is_conflict_and_cleans_unpublished_stage(self):
        for change in ("bytes", "symlink", "removed_root"):
            with self.subTest(change=change):
                fixture = self.fixture()
                (fixture.output / "foreign.txt").write_bytes(b"Foreign sentinel")
                original_render = assets._render

                def change_source(*args, **kwargs):
                    rendered = original_render(*args, **kwargs)
                    source = fixture.source / fixture.request["source"]["file"]
                    if change == "bytes":
                        with source.open("ab") as handle:
                            handle.write(b"changed during derivation")
                    elif change == "symlink":
                        moved = fixture.root / "replaced-original.png"
                        source.rename(moved)
                        source.symlink_to(moved)
                    else:
                        fixture.source.rename(fixture.root / "removed-source")
                    return rendered

                with patch.object(assets, "_render", side_effect=change_source):
                    self.assert_error(self.derive(fixture), "source_changed", "conflict")
                self.assertFalse(fixture.target.exists())
                self.assertEqual((fixture.output / "foreign.txt").read_bytes(), b"Foreign sentinel")
                self.assertEqual(list(fixture.output.rglob("derivation.json")), [])
                self.assertEqual(list(fixture.output.rglob("background.png")), [])

    def test_foreign_stage_bytes_are_preserved_and_reported_even_under_an_owned_filename(self):
        for overwrite_owned_name in (False, True):
            with self.subTest(overwrite_owned_name=overwrite_owned_name):
                fixture = self.fixture()
                original_write = bio.write_file
                injected = []

                def foreign_write(path, raw):
                    original_write(path, raw)
                    if Path(path).name == "background.png":
                        foreign = Path(path) if overwrite_owned_name else Path(path).with_name("foreign.txt")
                        foreign.write_bytes(b"Foreign stage bytes must survive cleanup")
                        injected.append(foreign)
                        raise OSError("Synthetic failure after foreign stage intrusion")

                with patch.object(bio, "write_file", side_effect=foreign_write):
                    result = self.derive(fixture)
                self.assert_error(result, "io_error", "technical_error")
                self.assertIsNotNone(result["remaining"])
                remaining = Path(result["remaining"])
                self.assertEqual(len(injected), 1)
                self.assertTrue(injected[0].is_relative_to(remaining))
                self.assertEqual(injected[0].read_bytes(), b"Foreign stage bytes must survive cleanup")
                self.assertFalse(fixture.target.exists())

    def wait_line(self, stream):
        lines = queue.Queue()
        threading.Thread(target=lambda: lines.put(stream.readline()), daemon=True).start()
        return lines.get(timeout=10)

    def test_real_subprocess_holding_writer_lock_blocks_a_second_writer(self):
        fixture = self.fixture()
        code = ("import sys\nfrom pathlib import Path\n"
                "from tools.puzzle_production import background_io as bio\n"
                "with bio.writer(Path(sys.argv[1])):\n"
                "    print('locked', flush=True)\n"
                "    sys.stdin.readline()\n")
        process = subprocess.Popen([sys.executable, "-c", code, str(fixture.output)], cwd=ROOT,
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            self.assertEqual(self.wait_line(process.stdout), "locked\n")
            self.assert_error(self.derive(fixture), "target_conflict", "conflict")
            self.assertFalse(fixture.target.exists())
            _, stderr = process.communicate("release\n", timeout=10)
            self.assertEqual(process.returncode, 0, stderr)
        finally:
            if process.poll() is None:
                process.kill()
            process.communicate(timeout=10)
        self.assert_success(self.derive(fixture), "derived", fixture.target)

    def test_controlled_memory_time_interrupt_io_and_unexpected_errors_have_no_success_refs(self):
        for exception, status, code in (
            (MemoryError("synthetic exhaustion"), "aborted", "resource_exhausted"),
            (KeyboardInterrupt(), "aborted", "interrupted"),
            (OSError("synthetic I/O fault"), "technical_error", "io_error"),
            (RuntimeError("synthetic codec fault"), "technical_error", "internal_error"),
        ):
            with self.subTest(code=code):
                fixture = self.fixture()
                with patch.object(assets, "_render", side_effect=exception):
                    self.assert_error(self.derive(fixture), code, status)
                self.assertFalse(fixture.target.exists())
        fixture = self.fixture()
        with patch.object(bio.Budget, "check", side_effect=BackgroundError("deadline_exceeded", "Synthetic deadline")):
            self.assert_error(self.derive(fixture), "deadline_exceeded", "aborted")
        fixture = self.fixture()
        (fixture.output / "foreign.txt").write_bytes(b"Keep unrelated bytes")
        original_write = bio.write_file

        def failed_write(path, raw):
            original_write(path, raw)
            raise OSError("Synthetic disk failure after the first stage file")

        with patch.object(bio, "write_file", side_effect=failed_write):
            self.assert_error(self.derive(fixture), "io_error", "technical_error")
        self.assertFalse(fixture.target.exists())
        self.assertEqual((fixture.output / "foreign.txt").read_bytes(), b"Keep unrelated bytes")
        self.assertEqual(list(fixture.output.rglob("background.png")), [])
        self.assertEqual(list(fixture.output.rglob("derivation.json")), [])

    def test_cli_api_parity_success_validation_and_controlled_fault_exit_codes(self):
        exit_code, description, _ = self.cli("describe")
        self.assertEqual(exit_code, 0)
        self.assertEqual(description, assets.describe())
        fixture = self.fixture()
        request = fixture.request_file()
        code, result, _ = self.cli("derive", "--request", request,
                                  "--source-root", fixture.source, "--output-root", fixture.output)
        self.assertEqual(code, 0)
        self.assert_success(result, "derived", fixture.target)
        code, result, _ = self.cli("verify", "--request", request,
                                  "--source-root", fixture.source, "--output-dir", fixture.target)
        self.assertEqual(code, 0)
        self.assert_success(result, "verified", fixture.target)
        for arguments in ((), ("derive",), ("describe", "--unknown")):
            code, result, _ = self.cli(*arguments)
            self.assertEqual(code, 2)
            self.assert_error(result, "invalid_request")
        request.write_bytes(b'{"duplicate":0,"duplicate":1}')
        code, result, _ = self.cli("derive", "--request", request,
                                  "--source-root", fixture.source, "--output-root", fixture.output)
        self.assertEqual(code, 2)
        self.assert_error(result, "invalid_json")
        for error, expected_exit, status, error_code in (
            ("MemoryError", 4, "aborted", "resource_exhausted"),
            ("OSError", 5, "technical_error", "io_error"),
        ):
            fixture = self.fixture()
            script = ("import sys\nfrom tools.puzzle_production import background_assets as assets\n"
                      f"def fail(*args, **kwargs): raise {error}('Synthetic CLI fault')\n"
                      "assets._render = fail\nsys.exit(assets.main(sys.argv[1:]))\n")
            completed = subprocess.run([sys.executable, "-c", script, "derive", "--request", str(fixture.request_file()),
                                        "--source-root", str(fixture.source), "--output-root", str(fixture.output)],
                                       cwd=ROOT, capture_output=True, text=True, timeout=30)
            self.assertEqual(completed.returncode, expected_exit, completed.stderr)
            self.assert_error(json.loads(completed.stdout), error_code, status)

    def test_cli_sigterm_is_a_controlled_abort_with_one_json_response(self):
        fixture = self.fixture()
        script = ("import sys\nfrom tools.puzzle_production import background_assets as assets\n"
                  "def wait(*args, **kwargs):\n"
                  "    print('render-ready', file=sys.stderr, flush=True)\n"
                  "    sys.stdin.readline()\n"
                  "assets._render = wait\nsys.exit(assets.main(sys.argv[1:]))\n")
        process = subprocess.Popen([sys.executable, "-c", script, "derive", "--request", str(fixture.request_file()),
                                    "--source-root", str(fixture.source), "--output-root", str(fixture.output)],
                                   cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            self.assertEqual(self.wait_line(process.stderr), "render-ready\n")
            process.send_signal(signal.SIGTERM)
            stdout, stderr = process.communicate(timeout=10)
            self.assertEqual(process.returncode, 4, stderr)
            self.assert_error(json.loads(stdout), "interrupted", "aborted")
            self.assertFalse(fixture.target.exists())
        finally:
            if process.poll() is None:
                process.kill()
            process.communicate(timeout=10)

    def test_cli_request_file_change_during_same_run_prevents_publication(self):
        fixture = self.fixture()
        request_path = fixture.request_file()
        script = ("import sys\nfrom pathlib import Path\n"
                  "from tools.puzzle_production import background_assets as assets\n"
                  "original = assets._render\n"
                  "def change_request(*args, **kwargs):\n"
                  "    result = original(*args, **kwargs)\n"
                  "    Path(sys.argv[sys.argv.index('--request') + 1]).write_bytes(b'{}')\n"
                  "    return result\n"
                  "assets._render = change_request\nsys.exit(assets.main(sys.argv[1:]))\n")
        completed = subprocess.run([sys.executable, "-c", script, "derive", "--request", str(request_path),
                                    "--source-root", str(fixture.source), "--output-root", str(fixture.output)],
                                   cwd=ROOT, capture_output=True, text=True, timeout=30)
        self.assertEqual(completed.returncode, 2, completed.stderr)
        self.assert_error(json.loads(completed.stdout), "source_changed", "conflict")
        self.assertEqual(request_path.read_bytes(), b"{}")
        self.assertFalse(fixture.target.exists())
        self.assertEqual(list(fixture.output.rglob("background.png")), [])
        self.assertEqual(list(fixture.output.rglob("derivation.json")), [])


if __name__ == "__main__":
    unittest.main()
