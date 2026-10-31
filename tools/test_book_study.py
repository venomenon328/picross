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
        generated = book_study.fixtures()
        self.assertEqual(actual, generated['registry'])
        self.assertEqual(len(actual['entries']), 27)
        for field in ('id','key','save_slot','definition','reveal'):
            self.assertEqual(len({e[field].lower() for e in actual['entries']}),27)
        self.assertEqual([(d["id"], d["width"], d["height"]) for d in generated["definitions"][:3]],
                         [("T-01", 20, 20), ("T-06", 50, 50), ("T-08", 40, 30)])
        for entry, data in zip(actual['entries'], generated["definitions"], strict=True):
            self.assertEqual(json.loads((root/'game/study/book'/entry['definition']).read_text(encoding='utf-8')),data)
            self.assertEqual(data['id'], entry['id'])
            self.assertEqual(data['reveal']['definition_id'],entry['id'])
            self.assertEqual(data['reveal']['image'],'res://study/book/'+entry['reveal'])
            self.assertTrue((root/'game/study/book'/entry['reveal']).is_file())
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
            self.assertIn("study/book/tooltip_cases.gd", exclusions)
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
            files = ["opening.avi", "movie-final.png", "catalog.png", "opening-middle.png", "opening-back.png",
                     "return-middle.png", "return-edited-work.png", "paper-page-one.png", "paper-page-two.png", "paper-page-two-return.png",
                     "return-handoff-texture.png","return-handoff-direct.png","control-states.png",
                     "page-forward.png", "page-backward.png", "material-original-detail.png", "material-study-detail.png",
                     "windows/book-study.exe", "windows/book-study.pck", "web/index.html", "web/index.pck", "web/index.wasm"]
            files += ["logs/"+name+".log" for name in names]
            files += [f"{kind}-{w}.png" for kind in ("baseline", "handoff-texture", "work", "catalog") for w in (1280,1920,2560)]
            captions = {'direction','reset','mode','click-before','caption-after-click','fill','help','wrapped-edge'}
            empty = {'footer-0','footer-1','footer-2','whitespace'}
            files += [f'tooltip-{kind}-{w}.png' for w in (1280,1920,2560) for kind in captions | empty if kind != 'click-before']
            files += ['tooltip-negative-empty.png','hover-negative.png','hover-current.png','tooltip-after-motion-1920.png']
            details = [dict(file=f'edge-{kind}-{w}.png',source=f'catalog-{w}.png',rect=[0,0,20,20],scale=1)
                       for w in (1280,1920,2560) for kind in ('bottom-left','bottom-right','bottom-fold','outer-left','outer-right')]
            files += [r['file'] for r in details]
            for name in files:
                target = root/name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(b"synthetic test evidence")
            identity = dict(source_commit="a"*40, source_tree_dirty=False)
            labels = ['three independently moving leaves', 'actual catalog pointer selects correct ID',
                      'motion and blocked pointer input preserve cells/history/redo', 'presentation creates no save action',
                      'correct ID from page half 0', 'correct ID from page half 12', 'empty filter is immediate and reachable',
                      'sort is global and immediate', 'fresh actual pointer gesture works after interruption',
                      'empty filter retains settings and quit',
                      'normal registry and definition validators accept all 27 instances',
                      'foreign fixture binding rejected definition_id', 'duplicate fixture binding rejected reveal',
                      'copied ID on second spread has its earned reveal', 'earned copied reveal returns to second spread',
                      'explicit catalog tab starts return', 'return starts with actual edited content',
                      'return retains exact catalog context', 'return does not mutate history or add saves',
                      'return catalog shows current edited progress', 'return cancellation never commits held gesture',
                      'idle Escape is not catalog navigation', 'stable ending accepts animated return',
                      'same logical page retains exact paper after return', 'different logical pages have different organic paper',
                      'control states retain non-color ink distinctions', 'popup remains opaque in study',
                      'solved puzzle opens directly without replay', 'ending reset opens same empty page without book animation']
            labels += [f'{label} {target}' for target in (0,1) for label in ('pointer starts catalog turn',
                       'filter and sort discarded during turn', 'short catalog motion settles target', 'partial last spread',
                       'global ordering precedes pagination', 'edge action has no animation')]
            interruptions = [dict(kind=k,phase=p,reason=r) for k in ('page','open','return') for p in ('prepare','motion')
                             for r in ('resize','ui-scale','focus','leave')]
            labels += [f"{label} {r['kind']}/{r['phase']}/{r['reason']}" for r in interruptions
                       for label in ('matrix stable target', 'matrix no history or save', 'matrix releases resources')]
            labels += ['native tooltip delay is not bypassed','negative empty tooltip reproduced by native hover',
                       'negative detached hover stroke rejected']
            tips = [dict(case=kind,width=w,scale=s,caption='Useful help' if kind in captions else '',wait_seconds=.65,
                         visible=kind in captions, popup=[10,10,150,40],label=[130,20],text='Useful help')
                    for w,s in ((1280,1.25),(1920,1.0),(2560,1.25)) for kind in captions | empty]
            tips += [dict(case=f'dismiss-{kind}-{w}',visible=False) for w in (1280,1920,2560) for kind in ('switch','leave','click')]
            tips += [dict(case='dismiss-'+kind,visible=False) for kind in ('resize','ui-scale','focus','motion-start','motion-end-no-revival')]
            tips += [dict(case='negative-controls',empty_popup=True,current_detached_pixels=0,legacy_detached_pixels=12)]
            native = dict(checks=len(labels), assertions=[dict(label=l,passed=True) for l in labels],
                          tooltip_cases=tips,
                          interruptions=interruptions, catalog_layouts=[dict(cards=[{}]*24)]*3,
                          page_motions=[dict(target=1,direction=1,seconds=.85),dict(target=0,direction=-1,seconds=.85)],
                          failures=[], layouts=[{}, {}, {}], handoffs=[{}, {}, {}, {}],
                          ink_margins=[dict(view=v,width=w,margin=8,hull=[10,10,20,20]) for v,n in (('catalog',9),('work',5)) for w in (1280,1920,2560) for _ in range(n)],
                          returns=[dict(seconds=1.8,page=1)],
                          motion_wall_seconds_quiet=3.01, motion_frame_ms_quiet=[16.7],
                          resources=dict(ui_capture_targets=0, catalog_rgba_textures=0, visible_leaves=0,moving_leaves=3))
            movie = dict(fps=30,failures=[],final_state='CATALOG',final_id='T-06',edited_cursor=2,
                         events=[dict(kind=k,direction=d,seconds=s,first_frame=i*100,last_frame=i*100+90)
                                 for i,(k,d,s) in enumerate([('page',1,.85),('page',-1,.85),('open',1,3.),('return',-1,1.8)])])
            (root/'movie.json').write_text(json.dumps(movie),encoding='utf-8')
            study = dict(identity, package="B-A-N03-T01", host="Linux",edge_details=details,
                         leather=dict(sha256='58372a4329973e3ad308fde17ab5bc77148d7f724e55671e540bb5344f8e0f41',size=[1254,1254],imported_texture=dict(bytes=1)),
                         organic_paper=dict(sha256='1af9f61957619d7cea98b69021688b0b78997d84baf93698c9f02dcbb866362f',size=[1254,1254],imported_texture=dict(bytes=1)),
                         material_source=dict(sha256='957c2eab39b2334825fb159287b9d36a17b77fff1c628ea88110f2cfb5f7a71a'),
                         phases=[dict(name=n, exit_code=0, timed_out=False, seconds=.1) for n in names],
                         study_web_features=dict(renderer="gl_compatibility", threads=False, extensions=False, browser_probe="not requested"),
                         handoff_pixels=dict(samples={name: dict(max_channel_delta=3, mean_channel_delta=[.01]*4) for name in ('work-1280.png','work-1920.png','work-2560.png','return-handoff-direct.png')},
                                             negative_controls="one-pixel displacement and alpha mutation rejected"))
            def publish(candidate, original):
                (root/"native.json").write_text(json.dumps(original), encoding="utf-8")
                candidate["files"] = {r["file"]: {k:v for k,v in r.items() if k != "file"}
                                      for r in bind_files(root, exclude={"report.json"})}
                (root/"report.json").write_text(json.dumps(candidate), encoding="utf-8")
                return dict(book_study=candidate)
            validate_book_study(publish(deepcopy(study), native), root, identity, "Linux")
            for mutation in ("assertion", "omitted-assertion", "direction", "matrix", "cards", "leaves", "phase", "binding", "pixels", "margin", "return",
                             "tooltip-delay", "tooltip-empty", "tooltip-missing", "tooltip-stale", "tooltip-clipped", "tooltip-lifetime", "tooltip-counterexample", "hover-stroke", "edge-missing", "edge-scaled", "required-file"):
                candidate, original = deepcopy(study), deepcopy(native)
                if mutation == "assertion": original["failures"] = ["input lock failed"]
                if mutation == "omitted-assertion":
                    original['assertions'].pop(0)
                    original['checks'] -= 1
                if mutation == "direction": original['page_motions'][0]['direction'] = -1
                if mutation == "matrix": original['interruptions'].pop()
                if mutation == "cards": original['catalog_layouts'][0]['cards'].pop()
                if mutation == "leaves": original['resources']['visible_leaves'] = 1
                if mutation == "phase": candidate["phases"].pop()
                if mutation == "binding": candidate["source_commit"] = "b"*40
                if mutation == "pixels": candidate["handoff_pixels"]["samples"]["work-1280.png"]["max_channel_delta"] = 5
                if mutation == "margin": original['ink_margins'][0]['margin'] = 7.9
                if mutation == "return": original['returns'][0]['seconds'] = 0
                if mutation == "tooltip-delay": original['tooltip_cases'][0]['wait_seconds'] = 0
                if mutation == "tooltip-empty": next(r for r in original['tooltip_cases'] if r.get('caption'))['caption'] = ''
                if mutation == "tooltip-missing": original['tooltip_cases'].pop(0)
                if mutation == "tooltip-stale": next(r for r in original['tooltip_cases'] if r.get('caption'))['text'] = 'Old help'
                if mutation == "tooltip-clipped": next(r for r in original['tooltip_cases'] if r.get('caption'))['popup'][2] = 3000
                if mutation == "tooltip-lifetime": next(r for r in original['tooltip_cases'] if r['case'].startswith('dismiss-'))['visible'] = True
                if mutation == "tooltip-counterexample": original['tooltip_cases'][-1]['empty_popup'] = False
                if mutation == "hover-stroke": original['tooltip_cases'][-1]['current_detached_pixels'] = 12
                if mutation == "edge-missing": candidate['edge_details'].pop()
                if mutation == "edge-scaled": candidate['edge_details'][0]['scale'] = 2
                if mutation == "required-file": (root/"opening.avi").unlink()
                with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                    validate_book_study(publish(candidate, original), root, identity, "Linux")


if __name__ == "__main__":
    unittest.main()
