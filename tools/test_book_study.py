"""Small reproducibility and isolation checks; actual drawing is verified natively."""
import json
from pathlib import Path
import tempfile
import unittest
from copy import deepcopy
import math
import hashlib
import os
import struct
from unittest.mock import patch
from book_contract import SOURCES, INTEGRATION_ASSERTIONS, HELP_ORIGINALS

import book_study
import ci_scope
from native_contract import checks
from native_results import bind_files, check_phases, validate_book_study, validate_book_lifecycle
from native_results import INFO_HANDOFFS as HANDOFFS, INFO_ROUTES as ROUTES, information_pose as pose, validate_n05


def information_fixture(root, png):
    catalog = dict(scroll=91,right_scroll=173,selection='T-08',criterion='size',direction='desc',page=0)
    routes = []
    for index,(source,target) in enumerate(ROUTES):
        pan = source in ('settings','help') and target in ('settings','help')
        entering = source in ('catalog','work')
        seconds = .65 if pan else .85
        routes.append(dict(source=source,target=target,kind='pan' if pan else 'enter' if entering else 'return',
                           direction=0 if pan else 1 if entering else -1,seconds=seconds,wall_seconds=seconds+.01,
                           start=pose(source),end=pose(target),samples=[[seconds/2,[(a+b)/2 for a,b in zip(pose(source),pose(target))],1 if pan else .5]],
                           leaves=0 if pan else 1,origin=dict(kind='work' if index < 4 else 'catalog',id='T-06',catalog=catalog),
                           id='T-06',catalog_after=catalog,state_unchanged=True,return_context_unchanged=True,view_before={'zoom':1},view_after={'zoom':1}))
    layouts = []
    for w,h,u in ((1280,720,1.25),(1920,1080,1.0),(2560,1440,1.25),(1920,1200,1.0)):
        factor = h/max(6.075,10.8*h/w)
        for section in ('settings','help'):
            left = w/2-5*factor+(.75*factor if section == 'help' else 0)
            top = .28*factor
            x,y = math.ceil(left)+12,math.ceil(top)+12
            name = f'info-{section}-ink-{w}x{h}.png'
            png(root/name,w,h)
            layouts.append(dict(section=section,width=w,height=h,scale=u,file=name,hull=[x,y,20,20],
                                margin=min(x-left,y-top),clip=[x,y,100,100],scroll=0,limit=0))
    logic = []
    interruptions = []
    for kind in ('enter','pan','return'):
        for phase in ('prepare','motion'):
            for reason in ('resize','ui-scale','focus','leave'):
                endpoint = 'work' if kind == 'return' or (kind == 'enter' and reason == 'leave') else 'settings' if kind == 'pan' and reason == 'leave' else 'help'
                row = dict(kind=kind,phase=phase,reason=reason,endpoint=endpoint)
                logic.append(row)
                if reason == ('leave' if phase == 'prepare' else 'focus'):
                    interruptions.append(dict(row,held_blocked=True,released=True,textures=0))
    labels = ['N05 old tab removed including signal and focus','N05 work navigation order catalog settings help',
              'N05 begun work has undo and redo history','N05 explicit clue reset remains effective',
              'N05 catalog help settings returns original context without saves',
              'N05 catalog placeholder never creates save obligation','N05 actual UI toggle 1.25','N05 actual UI toggle 1.0',
              'N05 actual controls change settings','N05 explicit settings survive work return',
              'N05 failed mandatory flush blocks preparation','N05 stable completion origin','N05 completion return never replays success']
    return dict(routes=routes,layouts=layouts,logic=logic,interruptions=interruptions,settings=dict(mode='V',mark=False,animations=False,ui=1.0)),labels


class BookStudyTests(unittest.TestCase):
    def test_targeted_product_route_and_gate_exclude_full_study_and_movie(self):
        identity = dict(source_commit='a'*40,source_tree_dirty=False)
        calls = []
        def phase(name, command, environment, timeout, logs):
            calls.append(command)
            (logs/(name+'.log')).write_text('synthetic successful native process\n')
            if name == 'book-integration':
                directory = Path(environment['BOOK_INTEGRATION_OUTPUT'])
                (directory/'integration.json').write_text(json.dumps(dict(passed=True,
                    assertions=[dict(label=label,passed=True) for label in INTEGRATION_ASSERTIONS])))
                for filename in HELP_ORIGINALS:
                    (directory/Path(filename).name).write_bytes(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'+struct.pack('>II',1920,1080))
                (directory/'saves').mkdir()
                (directory/'saves/private-fixture.json').write_text('{}')
            return dict(name=name,output='synthetic',exit_code=0,timed_out=False,seconds=.1)
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)/'proof'
            with patch.dict(os.environ, {'GITHUB_ACTIONS':'true'}), \
                    patch.object(book_study.tc,'request_json'), \
                    patch.object(book_study.tc,'official_asset_urls',return_value={book_study.tc.EDITORS[book_study.platform.system()].name:'unused'}), \
                    patch.object(book_study.tc,'download_asset'), \
                    patch.object(book_study.tc,'extract_editor',return_value=Path('synthetic-engine')), \
                    patch.object(book_study,'prepare'), patch.object(book_study,'run_phase',side_effect=phase), \
                    patch.object(book_study,'require_clean_output'), \
                    patch.object(book_study,'source_identity',return_value=identity):
                study = book_study.run_lifecycle(Path(temp)/'cache',output)
                with self.assertRaisesRegex(ValueError,'not allowed in CI'):
                    book_study.run(Path(temp)/'cache',Path(temp)/'full')
            self.assertEqual([p['name'] for p in study['phases']],['book-version','book-import','book-integration'])
            self.assertFalse(any('--write-movie' in c or 'res://study/book/verify.gd' in c for c in calls))
            self.assertEqual(study['inventory_cost']['movie_bytes'],0)
            self.assertFalse(list(output.rglob('saves')))
            host = book_study.platform.system()
            report = dict(book_lifecycle=study)
            validate_book_lifecycle(report,output,identity,host)
            # A rehashed manifest must still reject extra film, wrong sources,
            # missing assertions/originals, failed phases and false dimensions.
            original = (output/'integration/integration.json').read_bytes()
            (output/'integration/integration.json').write_text(json.dumps(dict(passed=True,assertions=[])))
            bad = deepcopy(study)
            bad['files'] = {r.pop('file'):r for r in bind_files(output,exclude={'report.json'})}
            (output/'report.json').write_text(json.dumps(bad))
            with self.assertRaises(ValueError): validate_book_lifecycle(dict(book_lifecycle=bad),output,identity,host)
            (output/'integration/integration.json').write_bytes(original)
            for mutation in ('source','phase','missing','movie','dimensions'):
                bad = deepcopy(study)
                picture = output/sorted(HELP_ORIGINALS)[0]
                pixels = picture.read_bytes()
                if mutation == 'source': bad['sources'][SOURCES[0]] = '0'*64
                if mutation == 'phase': bad['phases'][-1]['exit_code'] = 4
                if mutation == 'missing': picture.unlink()
                if mutation == 'movie': (output/'opening.avi').write_bytes(b'forbidden movie')
                if mutation == 'dimensions': picture.write_bytes(pixels[:16]+struct.pack('>II',1,1))
                bad['files'] = {r.pop('file'):r for r in bind_files(output,exclude={'report.json'})}
                bad['inventory_cost']['bytes'] = sum(r['bytes'] for r in bad['files'].values())
                (output/'report.json').write_text(json.dumps(bad))
                with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                    validate_book_lifecycle(dict(book_lifecycle=bad),output,identity,host)
                picture.write_bytes(pixels)
                (output/'opening.avi').unlink(missing_ok=True)

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
            self.assertIn("study/book/n04_cases.gd", exclusions)
            self.assertIn("study/book/n05_cases.gd", exclusions)
            self.assertIn("study/book/n06_cases.gd", exclusions)
            self.assertNotIn("study/*", exclusions)
        self.assertEqual(presets["preset.1.options"]["variant/thread_support"], "false")
        self.assertEqual(presets["preset.1.options"]["variant/extensions_support"], "false")

    def test_actual_new_harness_diff_has_no_browser_authorization(self):
        selection = ci_scope.classify(["game/study/book/main.gd", "tools/book_study.py", "tools/p1_product.py"])
        self.assertFalse(selection["selected"]["web"])
        for job in ("product", "production", "preflight", "delivery"):
            self.assertTrue(selection["selected"][job])

    def test_study_phase_is_required_once_and_recognized_as_python(self):
        self.assertIn("regular-book-integration", checks("export"))
        self.assertNotIn("regular-book-integration", checks("graphics"))
        row = dict(name="regular-book-integration", status="success", seconds=.1, exit_code=0)
        check_phases(dict(checks=[row]), ["regular-book-integration"], Path("unused"))
        with self.assertRaises(ValueError):
            check_phases(dict(checks=[]), ["regular-book-integration"], Path("unused"))

    def test_study_gate_reads_original_assertions_phases_and_required_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            names = ["book-version", "book-import", "book-integration", "book-native", "book-movie"]
            (root/'integration').mkdir()
            (root/'integration/integration.json').write_text(json.dumps(dict(passed=True, assertions=[dict(label=label,passed=True) for label in sorted(INTEGRATION_ASSERTIONS)])),encoding='utf-8')
            files = ["opening.avi", "movie-final.png", "catalog.png", "opening-middle.png", "opening-back.png",
                     "return-middle.png", "return-edited-work.png", "paper-page-one.png", "paper-page-two.png", "paper-page-two-return.png",
                     "return-handoff-texture.png","return-handoff-direct.png","control-states.png",
                     "catalog-1920x1200.png","work-1920x1200.png","return-handoff-texture-1920x1200.png","return-handoff-direct-1920x1200.png",
                     "page-forward.png", "page-backward.png", "material-original-detail.png", "material-study-detail.png",
                     "integration/integration.json"]
            files += sorted(HELP_ORIGINALS)
            files += ["logs/"+name+".log" for name in names]
            files += [f"{kind}-{w}.png" for kind in ("baseline", "handoff-texture", "work", "catalog") for w in (1280,1920,2560)]
            captions = {'direction','reset','mode','click-before','caption-after-click','fill','help','wrapped-edge'}
            empty = {'footer-0','footer-1','footer-2','whitespace'}
            files += [f'tooltip-{kind}-{w}.png' for w in (1280,1920,2560) for kind in captions | empty if kind != 'click-before']
            files += ['tooltip-negative-empty.png','hover-negative.png','hover-current.png','tooltip-after-motion-1920.png']
            files += ['tooltip-mode-empty-1920.png','tooltip-mode-whitespace-1920.png']
            configurations = ((1280,720,1.25),(1920,1080,1.0),(2560,1440,1.25),(1920,1200,1.0))
            details = [dict(file=f'edge-{kind}-{suffix}.png',source=f'catalog-{suffix}.png',width=w,height=h,rect=[0,0,20,20],scale=1)
                       for w,h,suffix in ((1280,720,'1280'),(1920,1080,'1920'),(2560,1440,'2560'),(1920,1200,'1920x1200'))
                       for kind in ('bottom-left','bottom-right','bottom-fold','top-fold','outer-left','outer-right')]
            files += [r['file'] for r in details]
            files += list(HANDOFFS | {n.replace('direct','texture') for n in HANDOFFS})
            files += ['info-pan-help-middle.png','info-pan-settings-middle.png']
            for name in files:
                target = root/name
                target.parent.mkdir(parents=True, exist_ok=True)
                if name != "integration/integration.json": target.write_bytes(b"synthetic test evidence")
            import struct, zlib
            def png(path,w,h):
                def chunk(kind,data): return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data))
                path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+
                                 chunk(b'IDAT',zlib.compress(bytes((w*4+1)*h)))+chunk(b'IEND',b''))
            for w,h,_ in configurations:
                suffix = '1920x1200' if h == 1200 else str(w)
                for kind in ('catalog','work'):
                    png(root/f'{kind}-{suffix}.png',w,h)
            for detail in details: png(root/detail['file'],20,20)
            n05,n05_labels = information_fixture(root,png)
            n06 = dict(depth_cases=[dict(case=label,file='fold-depth-'+label+'.png',gap_pixels=22 if label == 'wide-gap' else 2,
                                        raised_shoulders=label != 'flat-sheet',low_valley_flat_outer=label != 'wide-gap',
                                        accepted=label in ('rest','landed')) for label in ('rest','landed','wide-gap','flat-sheet')],
                       joint_depth=.31,minimum_cover_clearance=.006,binding=dict(vertices=8448,triangles=16026,surfaces=5),focus_reparent=True)
            for row in n06['depth_cases']: png(root/row['file'],640,128)
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
            interruptions = [dict(kind=k,phase=p,reason=r,source_offsets=[40,120],final_offsets=[0,0] if k == 'page' and r != 'leave' else [40,120]) for k in ('page','open','return') for p in ('prepare','motion')
                             for r in ('resize','ui-scale','focus','leave')]
            labels += [f"{label} {r['kind']}/{r['phase']}/{r['reason']}" for r in interruptions
                       for label in ('matrix stable target', 'matrix no history or save', 'matrix releases resources')]
            labels += ['native tooltip delay is not bypassed','negative empty tooltip reproduced by native hover',
                       'negative detached hover stroke rejected']
            labels += n05_labels
            gestures = ('left','right','outside','clue','chord','escape','lost-release','resize')
            labels += ['F01 '+label for label in ('regular BookButton default','deferred popup teardown',
                       'popup released after dispatch','lost release cancels without commit',
                       'outside releases never click another control','exact undo redo',
                       'negative synchronous popup hide rejected')]
            labels += ['F01 '+label+' '+kind for kind in gestures for label in ('starts','gesture','crosshair returns')]
            f01 = [dict(case=kind,visible=kind != 'negative-consumed-release',passed=True)
                   for kind in ('default-idle',*gestures,'negative-consumed-release','release-recovered')]
            f01 += [dict(case='negative-synchronous-hide',passed=True)]
            tips = [dict(case=kind,width=w,height=h,scale=s,caption='Useful help' if kind in captions else '',wait_seconds=.65,hovered=True,
                         visible=kind in captions, popup=[10,10,150,40],label=[130,20],text='Useful help')
                    for w,h,s in configurations[:3]
                    for kind in captions | empty | ({'mode-empty','mode-whitespace'} if w == 1920 else set())]
            tips += [dict(case=f'dismiss-{kind}-{w}',visible=False) for w in (1280,1920,2560) for kind in ('switch','leave','click')]
            tips += [dict(case='dismiss-'+kind,visible=False) for kind in ('resize','ui-scale','focus','motion-start','motion-end-no-revival')]
            tips += [dict(case='negative-controls',empty_popup=True,current_detached_pixels=0,legacy_detached_pixels=12)]
            ink = []
            for view,n in (('catalog',13),('work',4)):
                for w,h,s in configurations:
                    work = view == 'work'
                    factor = h/(max(6.075,10.8*h/w) if work else max(13.4,22*h/w))
                    paper = [w/2-5*factor if work else w/2,.28*factor if work else (h-12.4*factor)/2,10*factor,12.4*factor]
                    safe = [paper[0]+.75*factor,paper[1],paper[2]-.75*factor,paper[3]]
                    hull = [math.ceil(safe[0])+10,math.ceil(safe[1])+10,20,20]
                    margin = min(hull[0]-safe[0],hull[1]-safe[1])
                    ink += [dict(view=view,width=w,height=h,scale=s,margin=margin,hull=hull,paper=paper,flat_safe=safe)]*n
            ids = ['T-01','T-06','T-08']+[f'T-{i:02d}' for i in range(13,37)]
            counts = [dict(count=n,page=p,left=l,right=r,ids=ids[p*24:min(n,(p+1)*24)])
                      for n,p,l,r in ((0,0,0,0),(1,0,1,0),(12,0,12,0),(13,0,12,1),(24,0,12,12),(27,0,12,12),(27,1,3,0))]
            scroll = [dict(case=k,before=[40,120],after=[80,120] if k.endswith('-left') else [40,160])
                      for k in ('wheel-left','wheel-right','bar-left','bar-right','ensure-right')]
            scroll += [dict(case=k,before=[40,120],after=[40,120]) for k in ('right-edge','return-left','return-right','no-op')]
            scroll += [dict(case='empty-right',before=[80,0],after=[80,0]),dict(case='resize-clamp',before=[91,3000],after=[91,1200],right_limit=1200)]
            scroll += [dict(case='reset-'+k,after=[0,0]) for k in ('filter','sort','reverse')]
            boundaries = [dict(width=1920,height=h,scale=s,margin=10,offsets=[91,173]) for h,s in ((1200,1.25),(1192,1.0),(1208,1.0),(1088,1.0))]
            native = dict(checks=len(labels), assertions=[dict(label=l,passed=True) for l in labels],
                          n04=dict(counts=counts,scroll=scroll,boundaries=boundaries,clips=[dict(side=-1,rect=[106,125,750,900]),dict(side=1,rect=[1040,125,750,900])]),
                          tooltip_cases=tips,f01=f01,n05=n05,n06=n06,
                          interruptions=interruptions, catalog_layouts=[dict(cards=[{}]*24)]*3,
                          page_motions=[dict(target=1,direction=1,seconds=.85),dict(target=0,direction=-1,seconds=.85)],
                          failures=[], layouts=[{}, {}, {}], handoffs=[{}]*9,
                          ink_margins=ink,
                          returns=[dict(seconds=1.8,page=1)],
                          motion_wall_seconds_quiet=3.01, motion_frame_ms_quiet=[16.7],
                          resources=dict(ui_capture_targets=0, catalog_rgba_textures=0, visible_leaves=0,moving_leaves=3,information_snapshots=0,information_visit=False))
            movie = dict(fps=30,failures=[],final_state='CATALOG',final_id='T-06',edited_cursor=2,
                         events=[dict(kind=k,direction=d,seconds=s,first_frame=i*100,last_frame=i*100+90)
                                 for i,(k,d,s) in enumerate([('page',1,.85),('page',-1,.85),('open',1,3.),('return',-1,1.8)])])
            (root/'movie.json').write_text(json.dumps(movie),encoding='utf-8')
            for index,(source,target) in enumerate([('work','settings'),('settings','help'),('help','work'),('work','help'),('help','settings'),('settings','work'),('catalog','settings'),('settings','catalog'),('catalog','help'),('help','catalog')]):
                pan = source in ('settings','help') and target in ('settings','help')
                movie['events'].append(dict(kind='information',source=source,target=target,direction=0 if pan else 1 if target in ('settings','help') else -1,seconds=.65 if pan else .85,first_frame=500+index*40,last_frame=530+index*40))
            (root/'movie.json').write_text(json.dumps(movie),encoding='utf-8')
            study = dict(identity, package="B-B-T01", scope="shared-presentation-and-product-lifecycle", sources={name:hashlib.sha256((Path(__file__).resolve().parents[1]/name).read_bytes()).hexdigest() for name in SOURCES}, host="Linux",edge_details=details,
                         table=dict(sha256='5b02fe08710efb47df7b23307f460035aebaa3fa411e846b4a06558cc79678da',size=[1536,1024],imported_texture=dict(bytes=1)),
                         leather=dict(sha256='58372a4329973e3ad308fde17ab5bc77148d7f724e55671e540bb5344f8e0f41',size=[1254,1254],imported_texture=dict(bytes=1)),
                         organic_paper=dict(sha256='1af9f61957619d7cea98b69021688b0b78997d84baf93698c9f02dcbb866362f',size=[1254,1254],imported_texture=dict(bytes=1)),
                         material_source=dict(sha256='957c2eab39b2334825fb159287b9d36a17b77fff1c628ea88110f2cfb5f7a71a'),
                         phases=[dict(name=n, exit_code=0, timed_out=False, seconds=.1) for n in names],
                         study_web_features=dict(renderer="gl_compatibility", threads=False, extensions=False, browser_probe="not requested"),
                         handoff_pixels=dict(samples={name: dict(max_channel_delta=3, mean_channel_delta=[.01]*4) for name in ('work-1280.png','work-1920.png','work-2560.png','return-handoff-direct.png','return-handoff-direct-1920x1200.png')},
                                             negative_controls="one-pixel displacement and alpha mutation rejected"))
            def publish(candidate, original):
                (root/"native.json").write_text(json.dumps(original), encoding="utf-8")
                candidate["files"] = {r["file"]: {k:v for k,v in r.items() if k != "file"}
                                      for r in bind_files(root, exclude={"report.json"})}
                (root/"report.json").write_text(json.dumps(candidate), encoding="utf-8")
                return dict(book_study=candidate)
            study['handoff_pixels']['samples'].update({n:dict(max_channel_delta=2,mean_channel_delta=[.01]*4) for n in HANDOFFS})
            validate_book_study(publish(deepcopy(study), native), root, identity, "Linux")
            for mutation in ("help-omitted", "help-original", "integration-omitted", "integration-failed", "source-omitted", "source-changed", "n06-focus", "n06-missing", "n06-gap", "n06-flat", "n06-negative", "n06-joint", "n06-clearance", "n06-budget", "assertion", "omitted-assertion", "direction", "matrix", "cards", "leaves", "phase", "binding", "pixels", "margin", "return",
                             "f01-missing", "f01-failed", "f01-negative", "tooltip-delay", "tooltip-hover", "tooltip-empty", "tooltip-missing", "tooltip-stale", "tooltip-clipped", "tooltip-lifetime", "tooltip-counterexample", "hover-stroke", "edge-missing", "edge-scaled",
                             "height", "projection", "ink-hull", "left-first", "id-order", "scroll-mirrored", "scroll-return", "scroll-omitted", "abort-pair", "boundary", "table-source",
                             "info-route", "info-zoom", "info-leaf", "info-pan", "info-turn", "info-origin", "info-offset", "info-view", "info-hull", "info-clip", "info-scroll", "info-abort", "info-held", "info-handoff", "required-file"):
                candidate, original = deepcopy(study), deepcopy(native)
                integration = dict(passed=True,assertions=[dict(label=label,passed=True) for label in sorted(INTEGRATION_ASSERTIONS)])
                if mutation == 'help-omitted':
                    integration['assertions'] = [row for row in integration['assertions'] if row['label'] != 'HIL chapter and scroll survive settings pan']
                if mutation == 'integration-omitted': integration['assertions'].pop()
                if mutation == 'integration-failed': integration['assertions'][0]['passed'] = False
                if mutation == 'source-omitted': candidate['sources'].pop(SOURCES[0])
                if mutation == 'source-changed': candidate['sources'][SOURCES[0]] = '0'*64
                (root/'integration/integration.json').write_text(json.dumps(integration),encoding='utf-8')
                if mutation == 'n06-focus': original['n06']['focus_reparent'] = False
                if mutation == 'n06-missing': original['n06']['depth_cases'].pop()
                if mutation == 'n06-gap': original['n06']['depth_cases'][0]['gap_pixels'] = 8
                if mutation == 'n06-flat': original['n06']['depth_cases'][1]['raised_shoulders'] = False
                if mutation == 'n06-negative': original['n06']['depth_cases'][2]['accepted'] = True
                if mutation == 'n06-joint': original['n06']['joint_depth'] = 0
                if mutation == 'n06-clearance': original['n06']['minimum_cover_clearance'] = -.01
                if mutation == 'n06-budget': original['n06']['binding']['vertices'] = 10000
                if mutation == 'f01-missing': original['f01'].pop()
                if mutation == 'f01-failed': original['f01'][0]['passed'] = False
                if mutation == 'f01-negative': next(r for r in original['f01'] if r['case'] == 'negative-consumed-release')['visible'] = True
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
                if mutation == "tooltip-hover": original['tooltip_cases'][0]['hovered'] = False
                if mutation == "tooltip-empty": next(r for r in original['tooltip_cases'] if r.get('caption'))['caption'] = ''
                if mutation == "tooltip-missing": original['tooltip_cases'].pop(0)
                if mutation == "tooltip-stale": next(r for r in original['tooltip_cases'] if r.get('caption'))['text'] = 'Old help'
                if mutation == "tooltip-clipped": next(r for r in original['tooltip_cases'] if r.get('caption'))['popup'][2] = 3000
                if mutation == "tooltip-lifetime": next(r for r in original['tooltip_cases'] if r['case'].startswith('dismiss-'))['visible'] = True
                if mutation == "tooltip-counterexample": original['tooltip_cases'][-1]['empty_popup'] = False
                if mutation == "hover-stroke": original['tooltip_cases'][-1]['current_detached_pixels'] = 12
                if mutation == "edge-missing": candidate['edge_details'].pop()
                if mutation == "edge-scaled": candidate['edge_details'][0]['scale'] = 2
                if mutation == 'height': original['ink_margins'][-1]['height'] = 1080
                if mutation == 'projection': original['ink_margins'][0]['paper'][1] += 60
                if mutation == 'ink-hull': original['ink_margins'][0]['hull'][1] -= 20
                if mutation == 'left-first': original['n04']['counts'][3].update(left=7,right=6)
                if mutation == 'id-order': original['n04']['counts'][3]['ids'].reverse()
                if mutation == 'scroll-mirrored': original['n04']['scroll'][0]['after'] = [80,80]
                if mutation == 'scroll-return': next(r for r in original['n04']['scroll'] if r['case'] == 'return-right')['after'][1] = 0
                if mutation == 'scroll-omitted': original['n04']['scroll'].pop()
                if mutation == 'abort-pair': original['interruptions'][-1]['final_offsets'][1] = 40
                if mutation == 'boundary': original['n04']['boundaries'].pop()
                if mutation == 'table-source': candidate['table']['sha256'] = 'a'*64
                if mutation == 'info-route': original['n05']['routes'][0]['target'] = 'help'
                if mutation == 'info-zoom': original['n05']['routes'][2]['samples'][0][1][2] += .1
                if mutation == 'info-leaf': original['n05']['routes'][5]['leaves'] = 1
                if mutation == 'info-pan': original['n05']['routes'][2]['end'][0] = -5
                if mutation == 'info-turn': original['n05']['routes'][5]['samples'][0][2] = .5
                if mutation == 'info-origin': original['n05']['routes'][5]['origin']['kind'] = 'work'
                if mutation == 'info-offset': original['n05']['routes'][8]['origin']['catalog']['right_scroll'] = 91
                if mutation == 'info-view': original['n05']['routes'][0]['view_after']['zoom'] = 2
                if mutation == 'info-hull': original['n05']['layouts'][0]['hull'][0] -= 20
                if mutation == 'info-clip': original['n05']['layouts'][1]['clip'][0] = 0
                if mutation == 'info-scroll': original['n05']['layouts'][0]['limit'] = 1
                if mutation == 'info-abort': original['n05']['logic'][0]['endpoint'] = 'work'
                if mutation == 'info-held': original['n05']['interruptions'][0]['held_blocked'] = False
                if mutation == 'info-handoff': candidate['handoff_pixels']['samples'].pop(next(iter(HANDOFFS)))
                if mutation == "required-file": (root/"opening.avi").unlink()
                if mutation == 'help-original':
                    # publish() rebinds present originals; challenge omission in
                    # the required inventory without leaving later cases dirty.
                    target = root/'integration/hil-principle.png'
                    saved = target.read_bytes()
                    target.unlink()
                with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                    validate_book_study(publish(candidate, original), root, identity, "Linux")
                if mutation == 'help-original': target.write_bytes(saved)


if __name__ == "__main__":
    unittest.main()
