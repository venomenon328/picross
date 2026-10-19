"""CI-B coverage, dependency, build provenance and fail-closed evidence tests."""
import ast
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from ci_scope import classify, apply_event_policy, evaluate, JOBS, FLAGS
from web_bundle import LICENSES
from web_tests.contract import BROWSERS, GROUPS, SCENARIOS, expected
from web_tests.results import (BUILDS, binding, file_record, read, validate_all,
                               validate_browser, validate_builds)
from web_tests.run_groups import run
from web_tests import timing
from test_ci_a import run_blocks

ROOT = Path(__file__).resolve().parents[1]


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data)+'\n', encoding='utf-8')


def plan_for(paths=None, force='auto'):
    plan = apply_event_policy(classify(paths or ['tools/ci_scope.py'], force), 'pull_request')
    plan.update(source_head='a'*40, base_commit='b'*40, tested_checkout='c'*40,
                run_id='123', run_attempt='1', comparison='exact-base-to-head-trees-no-renames',
                diff_check='full-whitespace-check')
    return plan


def envelope(plan, root):
    result = dict(format='picross-web-builds-v1', binding=binding(plan), attempt='1', builds={})
    for index, name in enumerate(BUILDS):
        kind = 'player' if index == 0 else 'test'
        build = plan['tested_checkout']+'-'+kind+'-2026101800000'+str(index)
        prefix = 'releases/'+build+'/'
        record = dict(size=1, sha256='d'*64)
        files = {n: record for n in ['index.html', *[prefix+n for n in (
            'entry.html','index.js','index.wasm','index.pck','storage.js','SPIELANLEITUNG.md')],
            *[prefix+'licenses/'+n for n in LICENSES]]}
        manifest = dict(format='picross-web-v1', build_id=build, source_commit=plan['tested_checkout'],
                        engine='4.7.2-stable', built_at=f'2026-10-18T00:00:0{index}+00:00', kind=kind, files=files)
        path = root/'manifests'/(name+'.json')
        write(path, manifest)
        result['builds'][name] = dict(manifest=manifest, manifest_sha256=file_record(path)['sha256'])
    return result


def fixture(plan, browser, root):
    report = dict(format='picross-browser-result-v1', binding=binding(plan), attempt='1', browser=browser,
                  expected=plan['browser_expected'][browser], status='passed',
                  builds=envelope(plan, root), groups=[], files={}, phases=[])
    for group in plan['browser_groups']:
        ids = plan['browser_expected'][browser][group]
        row = dict(browser=browser, group=group, scenarios=ids[:], status='passed',
                   graphics={'version':'synthetic test only'},
                   user_agent='synthetic test only', launch_options={'headless':True},
                   timings=[dict(scenario=key, seconds=1, operations={'query':{'calls':1,'seconds':1,'bytes':1}}) for key in ids])
        if group == 'regular': row['errors'] = []
        if group == 'catalog': row['version'] = 'synthetic test only'
        if group == 'input': row['viewports'] = [dict(viewport=size,fit=True,minimum=False) for size in [[1280,720],[1920,1080]]]
        if group == 'persistence': row.update(lock_handoff={'held':[{}],'pending':[{}]},exit_diagnostics=[])
        report['groups'].append(row)
        report['phases'].append(dict(group=group, exit_code=0, seconds=1))
        raw = dict(results=[row], manifest=report['builds']['builds']['web-player' if group=='regular' else 'web-test']['manifest'])
        if group != 'regular': raw['update_manifest'] = report['builds']['builds']['web-test-update']['manifest']
        write(root/group/('regular-report.json' if group=='regular' else 'browser-report.json'), raw)
        for scenario in expected(browser,[group]):
            for suffix in scenario['images']:
                path = root/group/(browser+'-'+suffix) if group=='regular' else root/group/group/(browser+'-'+suffix)
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes(b'synthetic evidence, not a browser image')
    report['files'] = {p.relative_to(root).as_posix(): file_record(p) for p in root.rglob('*') if p.is_file()}
    write(root/'web-result.json',report)
    return report


class Selection(unittest.TestCase):
    def test_audited_leaf_and_shared_dependencies(self):
        examples = {
            'game/ui/catalog_ink.gd': ['regular','catalog'],
            'game/ui/catalog_tip.gd': ['regular','catalog'],
            'game/ui/catalog_card.gd': ['regular','catalog','completion','persistence'],
            'game/ui/gesture_counter.gd': ['regular','input'],
            'game/ui/completion.gd': ['regular','completion'],
            'game/ui/board.gd': ['regular','input','completion','persistence'],
            'tools/web_tests/group_persistence.py': ['regular','persistence'],
        }
        for path, groups in examples.items():
            with self.subTest(path=path):
                self.assertTrue((ROOT/path).is_file())
                plan = classify([path])
                self.assertEqual(plan['browser_groups'], groups)
                self.assertFalse(plan['selected']['delivery'])
        for path in ['game/ui/main.gd','game/model/save_store.gd','game/model/session.gd',
                     'game/web/storage.js','tools/web_tests/browser_actions.py',
                     'tools/web_tests/probe.gd','tools/build_web_player.py','unknown.py']:
            self.assertEqual(classify([path])['browser_groups'],list(GROUPS),path)

    def test_union_manual_scopes_never_narrow_and_main_stays_short(self):
        paths=['game/ui/catalog_ink.gd','game/ui/completion.gd']
        self.assertEqual(classify(paths)['browser_groups'],['regular','catalog','completion'])
        for group in GROUPS[1:]:
            self.assertEqual(classify([], 'browser-'+group)['browser_groups'],['regular',group])
            self.assertEqual(classify(['game/ui/main.gd'], 'browser-'+group)['browser_groups'],list(GROUPS))
            self.assertTrue(classify(['tools/deploy_web.py'], 'browser-'+group)['selected']['delivery'])
        for scope in ['all','toolchain','runtime','visual','perf-b','production']:
            self.assertEqual(classify([],scope)['browser_groups'],list(GROUPS))
        for path in ['docs/WEB_HOSTING.md','tools/deploy_web.py','tools/puzzle_production/analysis.py']:
            self.assertEqual(classify([path])['browser_groups'],[])
        self.assertEqual(apply_event_policy(classify(['unknown.py']), 'push')['browser_expected'],{})

    def test_selection_cannot_drop_expected_browser_or_group(self):
        original = plan_for()
        results = {job:{'result':'success'} for job in JOBS}
        for key,value in [('browser_groups',[]),('browser_expected',{}),
                          ('browser_expected',{'firefox':original['browser_expected']['chromium']}),
                          ('browser_expected',{'chromium':{'regular':['regular-start']}})]:
            plan=deepcopy(original);plan[key]=value
            with self.assertRaises(ValueError): evaluate(plan,results)

    def test_every_existing_assertion_belongs_to_one_group(self):
        self.assertEqual(len(expected('chromium', GROUPS)),27)
        self.assertEqual(BROWSERS, ('chromium',))
        with self.assertRaises(ValueError): expected('firefox', GROUPS)
        labels=[]
        for group in GROUPS[1:]:
            source=(ROOT/f'tools/web_tests/group_{group}.py').read_text(encoding='utf-8')
            found=[n.args[0].value for n in ast.walk(ast.parse(source)) if isinstance(n,ast.Call)
                   and isinstance(n.func,ast.Name) and n.func.id=='passed']
            self.assertEqual(set(found),{s['label'] for s in expected('chromium',[group])})
            labels.extend(found)
        self.assertEqual(len(labels),len(set(labels)))
        self.assertEqual({s['id'] for s in SCENARIOS},
                         {'regular-start', 'KU-B01', 'KU-B02', *[f'B{i:02}' for i in range(1,25)]})
        self.assertTrue(all(s['browsers']==['chromium'] for s in SCENARIOS))


class EvidenceGate(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.plan=plan_for()
        self.reports={b:fixture(self.plan,b,self.root/b) for b in BROWSERS}
        self.outputs={b+'_attempt':'1' for b in BROWSERS}

    def check(self, report):
        return validate_browser(report,self.plan,'chromium','1','2',self.root/'chromium')

    def test_full_coverage_and_same_run_retry(self):
        rows=validate_all(self.plan,self.root,self.outputs,'2')
        self.assertEqual([r['scenarios'] for r in rows],[27])
        for key in self.outputs:
            outputs=dict(self.outputs);outputs[key]='2'
            with self.assertRaises(ValueError): validate_all(self.plan,self.root,outputs,'2')

    def test_only_chromium_attempt_is_required_and_unexpected_outputs_fail(self):
        self.assertEqual(self.outputs, {'chromium_attempt':'1'})
        self.assertFalse((self.root/'firefox').exists())
        for outputs in ({}, {'firefox_attempt':'1'},
                        {**self.outputs,'firefox_attempt':'1'},
                        {'chromium_attempt':''}, {'chromium_attempt':None}):
            with self.subTest(outputs=outputs), self.assertRaises(ValueError):
                validate_all(self.plan,self.root,outputs,'2')

    def test_missing_empty_duplicate_wrong_or_unsuccessful_results(self):
        good=self.reports['chromium']
        mutations=[lambda r:r.update(groups=[]),lambda r:r['groups'].append(r['groups'][0]),
                   lambda r:r.update(phases=[]),lambda r:r['phases'][0].update(exit_code=23),
                   lambda r:r['phases'][0].update(seconds=float('nan')),
                   lambda r:r['groups'][0]['timings'][0].update(operations={}),
                   lambda r:r.update(browser='firefox'),lambda r:r.update(expected={}),
                   lambda r:r['groups'][1].update(scenarios=[]),
                   lambda r:r['groups'][1]['scenarios'].append(r['groups'][1]['scenarios'][0]),
                   lambda r:r['groups'][1].update(scenarios=['unknown']),
                   lambda r:r['groups'][1].update(graphics={}),
                   lambda r:r['groups'][2].update(viewports=[]),
                   lambda r:r['groups'][4].pop('lock_handoff'),
                   lambda r:r['groups'][4].pop('exit_diagnostics'),
                   lambda r:r['groups'][1].update(timings=[]),lambda r:r.update(files={})]
        for status in ['failed','failure','cancelled','skipped','',None]:
            mutations.extend([lambda r,s=status:r.update(status=s),
                              lambda r,s=status:r['groups'][1].update(status=s)])
        for mutate in mutations:
            candidate=deepcopy(good);mutate(candidate)
            with self.assertRaises((ValueError,OSError)): self.check(candidate)
        for key in binding(self.plan):
            candidate=deepcopy(good);candidate['binding'][key]='wrong'
            with self.assertRaises(ValueError): self.check(candidate)
        path=self.root/'chromium/web-result.json';path.unlink()
        with self.assertRaises(OSError): validate_all(self.plan,self.root,self.outputs,'2')

    def test_files_raw_reports_and_export_identity(self):
        good=self.reports['chromium']
        image=self.root/'chromium/regular/chromium-regular-catalog.png'
        original=image.read_bytes()
        for value in [b'',b'changed']:
            image.write_bytes(value)
            with self.assertRaises(ValueError): self.check(good)
        image.write_bytes(original)
        candidate=deepcopy(good);candidate['groups'][1]['scenarios'].reverse()
        with self.assertRaises(ValueError): self.check(candidate)  # raw report differs
        candidate=deepcopy(good)
        candidate['builds']['builds']['web-test-update']=deepcopy(candidate['builds']['builds']['web-test'])
        with self.assertRaises(ValueError): self.check(candidate)
        for attempt in ['0','3','',None]:
            candidate=deepcopy(good);candidate['builds']['attempt']=attempt
            with self.assertRaises(ValueError): self.check(candidate)
        path=self.root/'chromium/web-result.json'
        path.write_text('{"status":"passed","status":"failed"}')
        with self.assertRaises(ValueError): read(path)

    def test_green_web_job_without_evidence_cannot_pass_cli(self):
        plan_file=self.root/'plan.json';write(plan_file,self.plan)
        results={job:{'result':'success'} for job in JOBS}
        output=self.root/'result.json'
        result=subprocess.run([sys.executable,str(ROOT/'tools/ci_scope.py'),'finish',
            '--plan-file',str(plan_file),'--results',json.dumps(results),'--output',str(output)],
            capture_output=True,env={**os.environ,'GITHUB_ACTIONS':'false'})
        self.assertEqual(result.returncode,1,result.stderr)
        self.assertFalse(read(output)['accepted'])
        self.assertIn('browser_error',read(output))

    def test_real_finish_cli_accepts_only_complete_bound_chromium_evidence(self):
        # This case isolates browser evidence. CI-C additionally rejects a green
        # Product job without its own actual native payload (test_ci_c).
        self.plan.update(classify(['tools/web_tests/browser.py']))
        plan_file=self.root/'plan.json';write(plan_file,self.plan)
        output=self.root/'result.json'
        env={**os.environ,'GITHUB_ACTIONS':'true','GITHUB_RUN_ATTEMPT':'2','GITHUB_STEP_SUMMARY':'',
             'CI_BINDING':json.dumps({**binding(self.plan),'gate_attempt':'2'}),
             'CI_OUTPUTS':json.dumps({**{key:str(self.plan['selected'][key]).lower() for key in FLAGS},'selection_attempt':'1','native_groups':''}),
             'CI_RESULTS':json.dumps({job:{'result':'success' if self.plan['selected'][job] else 'skipped'} for job in JOBS})}
        for attempt,code in [('1',0),('2',1)]:
            env['CI_WEB_OUTPUTS']=json.dumps({'chromium_attempt':attempt})
            result=subprocess.run([sys.executable,str(ROOT/'tools/ci_scope.py'),'finish',
                '--plan-file',str(plan_file),'--web-evidence',str(self.root),'--output',str(output)],
                capture_output=True,env=env)
            self.assertEqual(result.returncode,code,result.stderr)
            self.assertEqual(read(output)['accepted'],code==0)
        env['CI_WEB_OUTPUTS']=json.dumps(self.outputs)
        path=self.root/'chromium/web-result.json'
        good=read(path)
        broken=[None, '', '{invalid json',
                json.dumps({**good,'browser':'firefox'}),
                json.dumps({**good,'status':'failed'}),
                json.dumps({**good,'groups':[]})]
        for payload in broken:
            with self.subTest(payload=payload and payload[:80]):
                if payload is None: path.unlink(missing_ok=True)
                else: path.write_text(payload,encoding='utf-8')
                result=subprocess.run([sys.executable,str(ROOT/'tools/ci_scope.py'),'finish',
                    '--plan-file',str(plan_file),'--web-evidence',str(self.root),'--output',str(output)],
                    capture_output=True,env=env)
                self.assertEqual(result.returncode,1,result.stderr)
                self.assertFalse(read(output)['accepted'])
                self.assertIn('browser_error',read(output))


class Execution(unittest.TestCase):
    def test_measurement_attributes_real_transport_and_confirmation_once(self):
        meter=timing.Meter()
        inner=timing.measured('query')(lambda: {'cells':[1,0]})
        outer=timing.measured('state')(inner)
        save=timing.measured('save_confirmation')(timing.measured('wait')(lambda: None))
        with patch.object(timing,'CURRENT',meter), patch.object(timing.time,'perf_counter',side_effect=[1,4,5,7,8,9]):
            self.assertEqual(outer(),{'cells':[1,0]})
            save()
            result=meter.checkpoint('scenario')
        self.assertEqual(result['operations']['state']['seconds'],3)
        self.assertGreater(result['operations']['state']['bytes'],0)
        self.assertEqual(result['operations']['save_confirmation']['seconds'],2)
        self.assertNotIn('query',result['operations'])
        self.assertNotIn('wait',result['operations'])

    def test_state_projection_preserves_values_and_requires_explicit_fields(self):
        import importlib
        with patch.object(sys,'path',[str(ROOT/'tools/web_tests'),*sys.path]):
            actions=importlib.import_module('browser_actions')
        payload={'cells':[1,0,-1],'cursor':2,'controls':[{'name':'undo'}],'unused':[0]*10000}
        class Page:
            def evaluate(self, expression, keys):
                self.keys=keys
                return {k:deepcopy(payload[k]) for k in keys}
        page=Page()
        self.assertEqual(actions.state(page,'cells','cursor'),{k:payload[k] for k in ('cells','cursor')})
        self.assertEqual(page.keys,['cells','cursor'])
        with self.assertRaises(ValueError):actions.state(page)

    def test_click_keeps_real_pointer_move_down_up_order(self):
        import importlib
        from unittest.mock import Mock, call
        with patch.object(sys,'path',[str(ROOT/'tools/web_tests'),*sys.path]):
            actions=importlib.import_module('browser_actions')
        page=Mock()
        actions.click(page,(80,90))
        self.assertEqual(page.mouse.method_calls,[call.move(80,90),call.down(),call.up()])

    def test_each_selected_group_is_a_fresh_process_even_after_failure(self):
        for selected in GROUPS[1:]:
            plan=plan_for(['tools/web_tests/group_'+selected+'.py'])
            with tempfile.TemporaryDirectory() as temporary:
                root=Path(temporary)
                source=root/'source'
                original=fixture(plan,'chromium',source)
                builds=root/'builds'
                for name in BUILDS:
                    write(builds/name/'build-manifest.json',original['builds']['builds'][name]['manifest'])
                write(builds/'builds.json',original['builds'])
                args=SimpleNamespace(build_root=builds, output=root/'out', browser='chromium', build_attempt='1')
                calls=[]
                def process(command, **kwargs):
                    import shutil
                    group=selected if 'browser.py' in command[1] else 'regular'
                    directory=Path(command[command.index('--output')+1])
                    for path in (source/group).iterdir():
                        if path.is_dir(): shutil.copytree(path,directory/path.name)
                        else: shutil.copyfile(path,directory/path.name)
                    kwargs['stdout'].write('synthetic process probe\n')
                    calls.append(command)
                    return SimpleNamespace(returncode=23 if group=='regular' else 0)
                def build(path, **kwargs):
                    return original['builds']['builds'][path.name]['manifest']
                with patch.dict(os.environ,{'GITHUB_RUN_ATTEMPT':'1'}), \
                     patch('web_tests.run_groups.validate',side_effect=build), \
                     patch('web_tests.run_groups.platform.platform',return_value='synthetic runner'), \
                     patch('web_tests.run_groups.subprocess.run',side_effect=process):
                    with self.assertRaisesRegex(ValueError,'regular'): run(args,plan)
                self.assertEqual(len(calls),2)
                self.assertIn('--groups',calls[1]);self.assertEqual(calls[1][-1],selected)
                self.assertNotEqual(calls[0][calls[0].index('--output')+1],calls[1][calls[1].index('--output')+1])
                self.assertEqual(read(args.output/'web-result.json')['status'],'failed')

    @unittest.skipUnless(sys.platform=='linux','Executes Linux workflow shell blocks')
    def test_actual_build_and_browser_shells_preserve_failures(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);bin_dir=root/'bin';bin_dir.mkdir()
            venv=root/'web-venv/bin';venv.mkdir(parents=True)
            stub='#!'+sys.executable+'\n'+textwrap.dedent('''\
                import json, os, sys
                from pathlib import Path
                args=[Path(sys.argv[0]).name,*sys.argv[1:]]
                with open(os.environ['JOURNAL'],'a') as out: out.write(json.dumps(args)+'\\n')
                if os.environ.get('FAIL_COMMAND') and os.environ['FAIL_COMMAND'] in ' '.join(args): sys.exit(23)
                ''')
            for p in [bin_dir/n for n in ('python3','xvfb-run')]+[venv/n for n in ('pip','playwright','python')]:
                p.write_text(stub);p.chmod(0o755)
            for filename in ('web.yml','web-browser.yml'):
                blocks=run_blocks((ROOT/'.github/workflows'/filename).read_text())
                for browser in BROWSERS:
                    journal=root/'commands.jsonl'
                    def execute(failure=''):
                        journal.write_text('')
                        env={**os.environ,'PATH':str(bin_dir)+os.pathsep+os.environ['PATH'],
                             'JOURNAL':str(journal),'GITHUB_RUN_ATTEMPT':'2','GITHUB_OUTPUT':str(root/'output'),
                             'BROWSER':browser,'BUILD_ATTEMPT':'1','FAIL_COMMAND':failure}
                        for block in blocks:
                            result=subprocess.run(['bash','--noprofile','--norc','-eo','pipefail','-c',
                                block.replace('${{ runner.temp }}',temporary)],cwd=root,env=env,capture_output=True)
                            if result.returncode:return result.returncode
                        return 0
                    self.assertEqual(execute(),0)
                    calls=[json.loads(line) for line in journal.read_text().splitlines()]
                    self.assertFalse(any('ssh' in ' '.join(c) for c in calls))
                    if filename=='web.yml':
                        builds=[c for c in calls if 'tools/build_web_player.py' in c]
                        self.assertEqual(len(builds),3);self.assertEqual(sum('--test' in c for c in builds),2)
                        self.assertFalse(any('playwright' in ' '.join(c) for c in calls))
                        failures=('build_web_player.py','run_groups.py seal')
                    else:
                        self.assertFalse(any('build_web_player.py' in ' '.join(c) for c in calls))
                        self.assertTrue(any(c[-2:]==['--with-deps',browser] for c in calls))
                        self.assertTrue(any('run_groups.py' in ' '.join(c) and c[c.index('--browser')+1]==browser for c in calls))
                        failures=('playwright','run_groups.py run')
                    print('CI_B_EXECUTION_PROBE '+json.dumps({'workflow':filename,'browser':browser,'commands':calls}),flush=True)
                    for failure in failures:self.assertEqual(execute(failure),23)
                    if filename == 'web-browser.yml':
                        for browser in ('firefox', 'webkit', 'both', '', 'Chromium', 'chromium firefox'):
                            with self.subTest(rejected_browser=browser):
                                self.assertEqual(execute(), 1)
                                # The actual first step must stop before venv, pip,
                                # Playwright installation or the runner command.
                                self.assertEqual(journal.read_text(), '')


if __name__ == '__main__':
    unittest.main()
