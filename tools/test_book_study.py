"""Small reproducibility and isolation checks; actual drawing is verified natively."""
import json
from pathlib import Path
import tempfile
import unittest
from copy import deepcopy

import book_study
import ci_scope
from native_contract import checks
from native_results import bind_files, check_phases, validate_book_study


class BookStudyTests(unittest.TestCase):
    def test_checked_in_inputs_are_reproducible_and_bounded(self):
        root = Path(__file__).resolve().parents[1]
        actual = json.loads((root / "game/study/book/fixtures.json").read_text(encoding="utf-8"))
        self.assertEqual(actual, book_study.fixtures())
        self.assertEqual([(d["id"], d["width"], d["height"]) for d in actual["definitions"]],
                         [("T-01", 20, 20), ("T-06", 50, 50), ("T-08", 40, 30)])
        for data in actual["definitions"]:
            self.assertEqual(len(data["columns"]), data["width"])
            for x, clues in enumerate(data["columns"]):
                self.assertEqual(sum(c["length"] for c in clues),
                                 sum(row[x] > 0 for row in data["solution"]))
            self.assertTrue(data["test_only"])

    def test_separate_presets_exclude_real_content_and_other_studies(self):
        import configparser
        presets = configparser.ConfigParser(interpolation=None)
        presets.read_string(book_study.study_presets())
        for index in (0, 1):
            exclusions = presets[f"preset.{index}"]["exclude_filter"].strip('"').split(',')
            self.assertIn("data/*", exclusions)
            self.assertIn("art/content/*", exclusions)
            self.assertIn("tests/*", exclusions)
            self.assertIn("study/main.gd", exclusions)
            self.assertIn("study/book/verify.gd", exclusions)
            self.assertIn("study/book/pack_probe.gd", exclusions)
            self.assertNotIn("study/*", exclusions)
        self.assertEqual(presets["preset.1.options"]["variant/thread_support"], "false")
        self.assertEqual(presets["preset.1.options"]["variant/extensions_support"], "false")

    def test_actual_new_harness_diff_has_no_browser_authorization(self):
        selection = ci_scope.classify(["game/study/book/main.gd", "tools/book_study.py", "tools/p1_product.py"])
        self.assertFalse(selection["selected"]["web"])
        for job in ("product", "production", "preflight", "delivery"):
            self.assertTrue(selection["selected"][job])

    def test_study_phase_is_required_once_and_recognized_as_python(self):
        self.assertIn("isolated-book-study", checks("export"))
        self.assertNotIn("isolated-book-study", checks("graphics"))
        row = dict(name="isolated-book-study", status="success", seconds=.1, exit_code=0)
        check_phases(dict(checks=[row]), ["isolated-book-study"], Path("unused"))
        with self.assertRaises(ValueError):
            check_phases(dict(checks=[]), ["isolated-book-study"], Path("unused"))

    def test_study_gate_reads_original_assertions_phases_and_required_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            names = ["book-version", "book-import", "book-native", "book-movie", "book-regular-import",
                     "book-regular-windows", "book-regular-windows-content", "book-regular-windows-isolation",
                     "book-regular-web", "book-regular-web-content", "book-regular-web-isolation",
                     "book-study-windows", "book-study-windows-pack", "book-study-web", "book-study-web-pack"]
            files = ["opening.avi", "catalog.png", "opening-middle.png", "opening-back.png",
                     "windows/book-study.exe", "windows/book-study.pck", "web/index.html", "web/index.pck", "web/index.wasm"]
            files += ["logs/"+name+".log" for name in names]
            files += [f"{kind}-{w}.png" for kind in ("baseline", "handoff-texture", "work") for w in (1280,1920,2560)]
            for name in files:
                target = root/name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(b"synthetic test evidence")
            identity = dict(source_commit="a"*40, source_tree_dirty=False)
            native = dict(checks=96, failures=[], layouts=[{}, {}, {}], handoffs=[{}, {}, {}],
                          motion_wall_seconds_quiet=3.01, motion_frame_ms_quiet=[16.7],
                          resources=dict(ui_capture_targets=0, catalog_rgba_textures=0))
            study = dict(identity, package="B-A-T01", host="Linux",
                         phases=[dict(name=n, exit_code=0, timed_out=False, seconds=.1) for n in names],
                         study_web_features=dict(renderer="gl_compatibility", threads=False, extensions=False, browser_probe="not requested"),
                         handoff_pixels=dict(samples={f"work-{w}.png": dict(max_channel_delta=3, mean_channel_delta=[.01]*4) for w in (1280,1920,2560)},
                                             negative_controls="one-pixel displacement and alpha mutation rejected"))
            def publish(candidate, original):
                (root/"native.json").write_text(json.dumps(original), encoding="utf-8")
                candidate["files"] = {r["file"]: {k:v for k,v in r.items() if k != "file"}
                                      for r in bind_files(root, exclude={"report.json"})}
                (root/"report.json").write_text(json.dumps(candidate), encoding="utf-8")
                return dict(book_study=candidate)
            validate_book_study(publish(deepcopy(study), native), root, identity, "Linux")
            for mutation in ("assertion", "phase", "binding", "pixels", "required-file"):
                candidate, original = deepcopy(study), deepcopy(native)
                if mutation == "assertion": original["failures"] = ["input lock failed"]
                if mutation == "phase": candidate["phases"].pop()
                if mutation == "binding": candidate["source_commit"] = "b"*40
                if mutation == "pixels": candidate["handoff_pixels"]["samples"]["work-1280.png"]["max_channel_delta"] = 5
                if mutation == "required-file": (root/"opening.avi").unlink()
                with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                    validate_book_study(publish(candidate, original), root, identity, "Linux")


if __name__ == "__main__":
    unittest.main()
