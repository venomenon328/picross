"""CI-C adversarial selection, isolation, byte/pixel preservation and result gates."""
from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from ci_scope import classify, apply_event_policy, evaluate, JOBS
from native_contract import GROUPS, PATHS, SCOPES, checks, coverage
from native_results import bind_files, read, digest, validate_all, validate_payload
from p1_product import parse_args
from native_runner import requested

ROOT = Path(__file__).resolve().parents[1]


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value)+'\n', encoding='utf-8')


class Selection(unittest.TestCase):
    def test_independent_groups_common_paths_and_union(self):
        for path, groups in [
            ('tools/kat2_product.py',['catalog']), ('tools/ea_product.py',['completion']),
            ('tools/p14_integration.py',['history']),
            ('tools/za1_product.py',['adapters','export']),
            ('tools/perf_b_resources.py',['core','graphics','export']),
            ('game/ui/catalog.gd',['core','catalog','completion','adapters','graphics','export']),
            ('game/ui/completion.gd',['core','catalog','completion','adapters','graphics','export'])]:
            with self.subTest(path=path):
                self.assertEqual(classify([path])['native_groups'],groups)
        for path in ['game/ui/main.gd','game/model/save_store.gd','tools/product_fixtures.py',
                     'tools/native_runner.py','tools/native_results.py','tools/new_harness.py',
                     '.github/workflows/p1-product.yml','game/tests/new_probe.gd']:
            self.assertEqual(classify([path])['native_groups'], list(GROUPS))
        self.assertEqual(classify(['tools/ea_product.py','tools/kat2_product.py'])['native_groups'],['catalog','completion'])
        self.assertEqual(classify(['tools/ea_product.py','docs/README.md'])['native_groups'],['completion'])

    def test_catalog_and_completion_consumers_select_exact_native_and_browser_groups(self):
        # Expectations follow the active probes, independently of PATHS:
        # RP6/ZA-1 navigate cards and render album/reveal; compact capture renders
        # the album; KAT-2 KE also instantiates Completion in ke_graphics.gd.
        for path, native, browser in [
            ('game/ui/catalog.gd', ['core','catalog','completion','adapters','graphics','export'],
             ['regular','catalog','completion','persistence']),
            ('game/ui/catalog_card.gd', ['core','catalog','completion','adapters','graphics','export'],
             ['regular','catalog','completion','persistence']),
            ('game/ui/catalog_ink.gd', ['core','catalog','adapters','graphics','export'],
             ['regular','catalog']),
            ('game/ui/catalog_tip.gd', ['core','catalog','adapters','graphics','export'],
             ['regular','catalog']),
            ('game/ui/completion.gd', ['core','catalog','completion','adapters','graphics','export'],
             ['regular','completion']),
        ]:
            with self.subTest(path=path):
                self.assertTrue((ROOT/path).is_file())
                plan = classify([path])
                self.assertEqual(plan['native_groups'], native)
                self.assertEqual(plan['native_expected'], coverage(native))
                self.assertEqual(plan['browser_groups'], [])
                self.assertEqual({job for job in JOBS if plan['selected'][job]},
                                 {'docs','product'})
                self.assertFalse(plan['selected']['integration'])
                self.assertTrue(plan['selected']['pilots'])
                self.assertTrue(plan['selected']['visual'])
                self.assertTrue(plan['selected']['perf_b'])

    def test_real_difficulty_path_includes_registry_consumers_and_no_ghost_entry(self):
        path = 'game/model/catalog_difficulty.gd'
        self.assertTrue((ROOT/path).is_file())
        self.assertIn(path, PATHS)  # All groups here must be audited, not fallback.
        self.assertNotIn('game/ui/catalog_difficulty.gd', PATHS)
        for caller in ('game/ui/catalog_card.gd', 'game/model/content_registry.gd'):
            self.assertIn('preload("res://model/catalog_difficulty.gd")',
                          (ROOT/caller).read_text(encoding='utf-8'))
        plan = classify([path])
        self.assertEqual(plan['native_groups'], list(GROUPS))
        self.assertEqual(plan['browser_groups'], [])
        self.assertEqual({job for job in JOBS if plan['selected'][job]},
                         {'docs','product'})
        self.assertTrue(plan['selected']['integration'])

    def test_runtime_leaf_mixed_diffs_union_and_manual_scope_only_widens(self):
        paths = ['game/ui/catalog_ink.gd', 'game/ui/completion.gd']
        plan = classify(paths)
        self.assertEqual(plan['native_groups'],
                         ['core','catalog','completion','adapters','graphics','export'])
        self.assertEqual(plan['browser_groups'], [])
        self.assertFalse(plan['selected']['delivery'])
        for extra in ('tools/p14_integration.py', 'game/model/catalog_difficulty.gd',
                      'game/ui/main.gd', 'game/ui/new_catalog_leaf.gd'):
            with self.subTest(extra=extra):
                self.assertEqual(classify(paths+[extra])['native_groups'], list(GROUPS))
        for scope in ('native-core', 'native-catalog', 'native-export'):
            self.assertEqual(classify(paths, scope)['native_groups'], plan['native_groups'])
        self.assertEqual(classify(paths, 'native-history')['native_groups'], list(GROUPS))

    def test_manual_only_widens_and_main_content_remain_short(self):
        for group in GROUPS:
            self.assertEqual(classify([], 'native-'+group)['native_groups'], [group])
            self.assertEqual(classify(['unknown.py'], 'native-'+group)['native_groups'],list(GROUPS))
        for scope in ('all','toolchain','production'):
            self.assertEqual(classify([],scope)['native_groups'],list(GROUPS))
        for scope in ('runtime','visual','perf-b','production'):
            self.assertFalse(classify([],scope)['selected']['web'])
            self.assertIn('core',classify([],scope)['native_groups'])
            self.assertIn('export',classify([],scope)['native_groups'])
        self.assertEqual(apply_event_policy(classify(['unknown.py']), 'push')['native_groups'],[])
        self.assertEqual(classify(['game/data/content/new.json'])['native_groups'],[])
        plan=classify(['tools/kat2_product.py']);plan['native_expected']={}
        with self.assertRaises(ValueError):
            evaluate(plan,{j:{'result':'success' if plan['selected'][j] else 'skipped'} for j in JOBS})

    def test_cli_exact_groups_and_legacy_expansion(self):
        base=['--cache-dir','cache','--output-dir','out']
        self.assertEqual(requested(parse_args(base)),list(GROUPS))
        for group in GROUPS:
            self.assertEqual(requested(parse_args(base+['--groups',group])),[group])
        for value in ('', 'catalog,catalog', 'bogus', '../catalog'):
            with self.assertRaises(ValueError): requested(parse_args(base+['--groups',value]))
        self.assertEqual(requested(parse_args(base+['--no-integration','--no-pilots','--no-visual','--no-perf-b'])),['core','export'])

    def test_real_tree_rename_delete_preserve_both_group_obligations(self):
        from ci_scope import make_plan
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            def git(*args):
                return subprocess.check_output(['git',*args],cwd=root).decode().strip()
            git('init','--quiet');git('config','user.name','CI fixture');git('config','user.email','ci@example.invalid')
            write(root/'tools/kat2_product.py',{'synthetic':True});git('add','.');git('commit','--quiet','-m','base')
            base=git('rev-parse','HEAD')
            (root/'tools/kat2_product.py').rename(root/'tools/ea_product.py')
            git('add','-A');git('commit','--quiet','-m','rename')
            write(root/'README.md',{});git('add','.');git('commit','--quiet','-m','later docs')
            head=git('rev-parse','HEAD')
            with patch('ci_scope.git',side_effect=lambda *a:subprocess.check_output(['git',*a],cwd=root)):
                self.assertEqual(make_plan(base,head,'auto')['native_groups'],['catalog','completion'])


class NativeGate(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.plan=apply_event_policy(classify([], 'native-core'),'pull_request')
        self.plan.update(source_head='a'*40,base_commit='b'*40,tested_checkout='c'*40,run_id='123',run_attempt='1')
        identity=dict(source_commit='a'*40,base_commit='b'*40,tested_checkout_commit='c'*40,
                      github_run_id='123',github_run_attempt='2',github_event_name='pull_request',source_tree_dirty=False)
        report=dict(identity,status='success',native_group='core',host='Linux',
                    scope={s:dict(enabled=s=='core',status='success' if s=='core' else 'not_applicable')
                           for v in SCOPES.values() for s in v},checks=[],selected_evidence=dict(files=[],omitted=[]))
        for name in checks('core'):
            report['checks'].append(dict(name=name,status='success',seconds=.1,
                exit_code=23 if name=='expected-failure' else 0,expected_failure=name=='expected-failure'))
            if name not in ('current-resource-hashes','verified-toolchain-assets','current-atlas-resources'):
                log=self.root/'core/logs'/(name+'.log');log.parent.mkdir(parents=True,exist_ok=True)
                log.write_bytes(b'synthetic process output')
                report['checks'][-1]['log']=dict(file=log.name,retained_bytes=24,original_bytes=24,abbreviated=False,sha256=digest(log))
        report['isolation']=dict(workspace='/tmp/core',project='/tmp/core/game',output='/tmp/output/core',
            profiles={k:'/tmp/core/'+k for k in ('XDG_DATA_HOME','XDG_CONFIG_HOME','XDG_CACHE_HOME')})
        write(self.root/'core/product-report.json',report)
        self.result=dict(format='picross-native-result-v1',status='success',identity=identity,host='Linux',
                         groups=['core'],expected=coverage(['core']),selection_attempt='1',
                         results=[dict(group='core',status='success',exit_code=0)],files=bind_files(self.root))
        self.save()

    def save(self):
        write(self.root/'native-result.json',self.result)

    def check(self):
        self.save()
        return validate_all(self.plan,self.root,None,dict(product_attempt='2'),'3')

    def test_success_and_source_run_retry_mutations(self):
        self.assertEqual(self.check()['groups'],['core'])
        for key in self.result['identity']:
            good=deepcopy(self.result)
            self.result['identity'][key]='wrong'
            with self.subTest(key=key),self.assertRaises(ValueError): self.check()
            self.result=good
        for value in ('',None,'0','3'):
            with self.assertRaises(ValueError):validate_all(self.plan,self.root,None,dict(product_attempt=value),'2')

    def test_missing_duplicate_skipped_failed_cancelled_groups_checks_and_artifacts(self):
        original=deepcopy(self.result)
        for status in ('pending','running','skipped','failure','cancelled','not_applicable',''):
            self.result=deepcopy(original);self.result['results'][0]['status']=status
            with self.subTest(status=status),self.assertRaises(ValueError):self.check()
        for field in ('results','files'):
            for rows in ([],original[field]*2):
                self.result=deepcopy(original);self.result[field]=rows
                with self.assertRaises(ValueError):self.check()
        self.result=original
        path=self.root/'core/product-report.json';report=read(path)
        for operation in ('remove','duplicate','skip','exit','unselected','other'):
            changed=deepcopy(report)
            if operation=='remove':changed['checks'].pop()
            if operation=='duplicate':changed['checks'].append(changed['checks'][0])
            if operation=='skip':changed['checks'][0]['status']='skipped'
            if operation=='exit':changed['checks'][0]['exit_code']=23
            if operation=='unselected':changed['scope']['export']['status']='success'
            if operation=='other':changed['native_group']='catalog'
            write(path,changed)
            self.result['files']=bind_files(self.root,exclude={'native-result.json'})
            with self.assertRaises(ValueError):self.check()
        write(path,report)

    def test_byte_mutation_missing_empty_duplicate_json_and_path_escape(self):
        path=self.root/'core/product-report.json';original=path.read_bytes()
        for data in (b'',b'changed'):
            path.write_bytes(data)
            with self.assertRaises(ValueError):self.check()
        path.write_bytes(original)
        path.unlink()
        with self.assertRaises(ValueError):self.check()
        path.write_bytes(original)
        self.result['files'][0]['file']='../outside'
        with self.assertRaises(ValueError):self.check()
        path.write_text('{"status":"success","status":"failure"}')
        with self.assertRaises(ValueError):read(path)

    def test_actual_finish_cli_rejects_green_product_without_native_payload(self):
        plan_file=self.root/'plan.json';write(plan_file,self.plan)
        results={j:{'result':'success' if self.plan['selected'][j] else 'skipped'} for j in JOBS}
        output=self.root/'result.json'
        run=subprocess.run([sys.executable,str(ROOT/'tools/ci_scope.py'),'finish','--plan-file',str(plan_file),
                            '--results',json.dumps(results),'--output',str(output)],capture_output=True,
                           env={**os.environ,'GITHUB_ACTIONS':'false'})
        self.assertEqual(run.returncode,1,run.stderr)
        self.assertIn('native_error',read(output))

    def test_required_file_cannot_be_removed_from_both_manifest_and_payload(self):
        # History's mandatory summary is a fixed technical name. Forging the
        # producer's self-declared file list must not make it optional.
        (self.root/'core').rename(self.root/'history')
        report=read(self.root/'history/product-report.json')
        report['native_group']='history'
        report['checks']=[]
        for name in checks('history'):
            row=dict(name=name,status='success',seconds=.1,exit_code=0)
            if name not in ('current-resource-hashes','verified-toolchain-assets','current-atlas-resources'):
                log=self.root/'history/logs'/(name+'.log');log.write_bytes(b'synthetic process output')
                row['log']=dict(file=log.name,retained_bytes=24,original_bytes=24,abbreviated=False,sha256=digest(log))
            report['checks'].append(row)
        for name,scope in report['scope'].items():
            scope.update(enabled=name=='integration',status='success' if name=='integration' else 'not_applicable')
        selected=self.root/'history/selected'
        from test_p14_integration import evidence_fixture
        summary = evidence_fixture(selected/'integration')
        report['integration']=summary
        report['selected_evidence']['files']=bind_files(selected)
        write(self.root/'history/product-report.json',report)
        self.result.update(groups=['history'],expected=coverage(['history']),
                           results=[dict(group='history',status='success',exit_code=0)])
        self.result['files']=bind_files(self.root,exclude={'native-result.json'})
        validate_payload(self.result,self.root)
        # Reproduce ci-required's actual sparse file boundary in an isolated
        # interpreter, so the full development checkout cannot hide imports.
        self.save()
        workflow=(ROOT/'.github/workflows/ci-chromium.yml').read_text()
        sparse=workflow.split('  ci-required:',1)[1].split('sparse-checkout: |',1)[1].split('sparse-checkout-cone-mode:',1)[0]
        with tempfile.TemporaryDirectory() as temp:
            checkout=Path(temp)
            for pattern in sparse.splitlines():
                for source in ROOT.glob(pattern.strip()) if pattern.strip() else []:
                    target=checkout/source.relative_to(ROOT)
                    target.parent.mkdir(parents=True,exist_ok=True)
                    shutil.copyfile(source,target)
            command=[sys.executable,'-I','-c',
                     'import sys; from pathlib import Path; sys.path.insert(0,sys.argv[1]); '
                     'from book_contract import SOURCES; '
                     'assert all((Path(sys.argv[1]).parent/name).is_file() for name in SOURCES), "Missing book hash input"; '
                     'from native_results import read,validate_payload; '
                     'root=Path(sys.argv[2]); validate_payload(read(root/"native-result.json"),root)',
                     str(checkout/'tools'),str(self.root)]
            positive=subprocess.run(command,cwd=checkout,capture_output=True)
            self.assertEqual(positive.returncode,0,positive.stderr)
            help_source=checkout/'game/ui/help_panel.gd'
            original=help_source.read_bytes()
            help_source.unlink()
            missing_source=subprocess.run(command,cwd=checkout,capture_output=True)
            self.assertNotEqual(missing_source.returncode,0)
            self.assertIn(b'Missing book hash input',missing_source.stderr)
            help_source.write_bytes(original)
            (checkout/'tools/p14_integration.py').unlink()
            negative=subprocess.run(command,cwd=checkout,capture_output=True)
            self.assertNotEqual(negative.returncode,0)
            self.assertIn(b"No module named 'p14_integration'",negative.stderr)
        # Even rehashed, self-consistent manifests cannot disguise corrupt raw
        # state, a shortened trace or a changed persisted view from the oracle.
        report_path=self.root/'history/product-report.json'
        for filename,mutation in (
            ('trace.jsonl', lambda rows: [{**r,'cells':[0]+r['cells'][1:]} if i==2 else r for i,r in enumerate(rows)]),
            ('trace.jsonl', lambda rows: rows[:-1]),
            ('writer-save.json', lambda saved: {**saved,'view':{}}),
        ):
            path=selected/'integration'/filename
            original=path.read_bytes()
            data=[json.loads(line) for line in original.splitlines()] if filename.endswith('jsonl') else json.loads(original)
            changed=mutation(data)
            path.write_text(''.join(json.dumps(r)+'\n' for r in changed) if filename.endswith('jsonl') else json.dumps(changed),encoding='utf-8')
            report['selected_evidence']['files']=bind_files(selected)
            write(report_path,report)
            self.result['files']=bind_files(self.root,exclude={'native-result.json'})
            with self.subTest(raw=filename),self.assertRaisesRegex(ValueError,'bounded native history'):
                validate_payload(self.result,self.root)
            path.write_bytes(original)
        for field,value in [('actions',16),('processes',1),('effective_transactions',7),('negative_controls',[])]:
            changed={**summary,field:value}
            write(selected/'integration/summary.json',changed)
            report['integration']=changed
            report['selected_evidence']['files']=bind_files(selected)
            write(self.root/'history/product-report.json',report)
            self.result['files']=bind_files(self.root,exclude={'native-result.json'})
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'bounded native history'):
                validate_payload(self.result,self.root)
        write(selected/'integration/summary.json',summary)
        report['integration']={**summary,'actions':16}
        report['selected_evidence']['files']=bind_files(selected)
        write(self.root/'history/product-report.json',report)
        self.result['files']=bind_files(self.root,exclude={'native-result.json'})
        with self.assertRaisesRegex(ValueError,'bounded native history'):validate_payload(self.result,self.root)
        report['integration']=summary
        (selected/'integration/summary.json').unlink()
        report['selected_evidence']['files']=[]
        write(self.root/'history/product-report.json',report)
        self.result['files']=bind_files(self.root,exclude={'native-result.json'})
        with self.assertRaisesRegex(ValueError,'mandatory files'):
            validate_payload(self.result,self.root)

    def test_real_finish_accepts_native_bytes_and_rejects_wrong_producer(self):
        from ci_scope import FLAGS
        plan=deepcopy(self.plan)
        plan.update(comparison='exact-base-to-head-trees-no-renames',diff_check='full-whitespace-check')
        with tempfile.TemporaryDirectory() as temp:
            outside=Path(temp);plan_file=outside/'plan.json';write(plan_file,plan)
            output=outside/'result.json'
            write(outside/'event.json', {})
            env={**os.environ,'GITHUB_EVENT_PATH':str(outside/'event.json'),'GITHUB_EVENT_NAME':'pull_request','GITHUB_ACTIONS':'true','GITHUB_RUN_ATTEMPT':'3','GITHUB_STEP_SUMMARY':'',
                 'CI_BINDING':json.dumps({**{k:plan[k] for k in ('source_head','base_commit','tested_checkout','run_id','run_attempt','event')},'gate_attempt':'3'}),
                 'CI_OUTPUTS':json.dumps({**{k:str(plan['selected'][k]).lower() for k in FLAGS},'selection_attempt':'1','native_groups':'["core"]','production_groups':'[]','browser_request':'null'}),
                 'CI_RESULTS':json.dumps({j:{'result':'success' if plan['selected'][j] else 'skipped'} for j in JOBS})}
            for attempt,expected in [('2',0),('1',1),('4',1)]:
                env['CI_NATIVE_OUTPUTS']=json.dumps(dict(product_attempt=attempt))
                run=subprocess.run([sys.executable,str(ROOT/'tools/ci_scope.py'),'finish','--plan-file',str(plan_file),
                                    '--native-evidence',str(self.root),'--output',str(output)],capture_output=True,env=env)
                self.assertEqual(run.returncode,expected,run.stderr)
                self.assertEqual(read(output)['accepted'],expected==0)


class Isolation(unittest.TestCase):
    def test_mesa_limit_preserves_timing_oracles_windows_and_callers_environment(self):
        from p1_product import run_phase
        from types import SimpleNamespace
        usage=SimpleNamespace(ru_utime=0,ru_stime=0,ru_maxrss=1,ru_nivcsw=0)
        resource=SimpleNamespace(RUSAGE_CHILDREN=-1,getrusage=lambda _:usage)
        environment={**os.environ,'LIBGL_ALWAYS_SOFTWARE':'1','LP_NUM_THREADS':'8',
                     'GITHUB_TOKEN':'test-only-placeholder'}
        program='import os; print("THREADS="+os.environ["LP_NUM_THREADS"]); print("TOKEN_PRESENT="+str("GITHUB_TOKEN" in os.environ))'
        with tempfile.TemporaryDirectory() as t:
            for host,name,extra,expected in [
                ('Linux','kat2-regular',[],1),('Linux','kat2-information',[],8),
                ('Linux','current-drawing-capture',[],8),('Linux','perf-b-native',[],8),
                ('Linux','book-integration',[],8),('Linux','import',['--headless'],8),
                ('Windows','kat2-regular',[],8)]:
                with self.subTest(host=host,name=name),patch('p1_product.platform.system',return_value=host), \
                     patch.dict(sys.modules,{'resource':resource}):
                    result=run_phase(name,[sys.executable,'-c',program,*extra],environment,5,Path(t))
                    self.assertEqual(result['exit_code'],0)
                    self.assertIn('THREADS='+str(expected),result['output'])
                    self.assertIn('TOKEN_PRESENT=False',result['output'])
                    self.assertEqual(environment['LP_NUM_THREADS'],'8')
                    self.assertEqual(environment['GITHUB_TOKEN'],'test-only-placeholder')

    def test_verified_warm_cache_starts_renderers_without_waiting_for_core(self):
        import native_runner
        import threading
        with tempfile.TemporaryDirectory() as t:
            started = {g: threading.Event() for g in ('core','catalog','graphics')}
            finished = set()
            def process(command, **kwargs):
                group = command[command.index('--native-group')+1]
                if group in started:
                    started[group].set()
                    for event in started.values(): self.assertTrue(event.wait(5))
                if group == 'export':
                    self.assertTrue({'core','catalog','graphics'} <= finished)
                finished.add(group)
                return subprocess.CompletedProcess(command,0)
            args = parse_args(['--cache-dir',t+'/cache','--output-dir',t+'/output',
                               '--groups','core,catalog,graphics,export'])
            with patch('native_runner.subprocess.run',side_effect=process), \
                 patch('native_runner.source_identity',return_value={'github_run_attempt':'1'}), \
                 patch('native_runner.platform.system',return_value='Linux'), \
                 patch('native_runner.cached_archives_ready',return_value=True), \
                 patch('native_results.validate_payload'):
                self.assertEqual(native_runner.run(args),0)
            result = read(Path(t)/'output/technical/native-result.json')
            self.assertTrue(result['cache_preparation']['verified_warm_archives'])
            self.assertEqual(finished,{'core','catalog','graphics','export'})

    def test_archive_cache_requires_both_original_hashes(self):
        import native_runner
        import p1_preflight as tc
        with tempfile.TemporaryDirectory() as t:
            cache = Path(t)
            self.assertFalse(native_runner.cached_archives_ready(cache,'Linux'))
            for asset in (tc.EDITORS['Linux'],tc.TEMPLATES):
                (cache/asset.name).write_bytes(b'corrupt archive')
            self.assertFalse(native_runner.cached_archives_ready(cache,'Linux'))
            with patch('p1_preflight.verify_sha256') as verify:
                self.assertTrue(native_runner.cached_archives_ready(cache,'Linux'))
                self.assertEqual(verify.call_count,2)

    def test_linux_parallel_groups_are_primed_isolated_and_awaited(self):
        import native_runner
        import threading
        with tempfile.TemporaryDirectory() as t:
            started={g:threading.Event() for g in ('catalog','graphics')}
            finished=[]
            def process(command,**kwargs):
                group=command[command.index('--native-group')+1]
                if group in started:
                    self.assertIn('core',finished)
                    started[group].set()
                    self.assertTrue(started['graphics' if group=='catalog' else 'catalog'].wait(5))
                finished.append(group)
                return subprocess.CompletedProcess(command,0)
            args=parse_args(['--cache-dir',t+'/cache','--output-dir',t+'/output','--groups','core,catalog,graphics'])
            with patch('native_runner.subprocess.run',side_effect=process),patch('native_runner.source_identity',return_value={'github_run_attempt':'1'}),patch('native_runner.platform.system',return_value='Linux'),patch('native_results.validate_payload'):
                self.assertEqual(native_runner.run(args),0)
            result=read(Path(t)/'output/technical/native-result.json')
            self.assertEqual(finished[0],'core')
            self.assertEqual(set(finished),{'core','catalog','graphics'})
            self.assertEqual([r['group'] for r in result['results']],['core','catalog','graphics'])

    def test_missing_delivery_preserves_partial_failure_diagnostics(self):
        from p1_evidence import Evidence
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);evidence=Evidence(root,'Linux',dict(core=True))
            missing=root/'missing.png';existing=root/'partial.json'
            write(existing,dict(partial=True))
            with self.assertRaises(Exception):evidence.retain_files([missing,existing])
            evidence.retain_files([missing,existing],allow_partial=True)
            evidence.finish(ValueError('missing mandatory image'))
            report=read(root/'technical/product-report.json')
            self.assertEqual(report['status'],'failure')
            self.assertEqual(report['selected_evidence']['omitted'][0]['file'],'missing.png')
            self.assertTrue((root/'technical/selected/partial.json').is_file())

    def test_actual_orchestrator_continues_after_failure_with_separate_process_outputs(self):
        import native_runner
        with tempfile.TemporaryDirectory() as t:
            calls=[]
            def process(command,**kwargs):
                group=command[command.index('--native-group')+1]
                calls.append((group,command,kwargs['env']))
                return subprocess.CompletedProcess(command,23 if group=='catalog' else 0)
            args=parse_args(['--cache-dir',t+'/cache','--output-dir',t+'/output','--groups','catalog,completion,graphics'])
            with patch('native_runner.subprocess.run',side_effect=process),patch('native_runner.source_identity',return_value={'github_run_attempt':'1'}),patch('native_runner.platform.system',return_value='Windows'):
                self.assertEqual(native_runner.run(args),1)
            self.assertEqual([c[0] for c in calls],['catalog','completion','graphics'])
            for flag in ('--output-dir','--technical-dir'):
                self.assertEqual(len({c[1][c[1].index(flag)+1] for c in calls}),3)


class Pixels(unittest.TestCase):
    def test_identical_originals_are_stored_once_and_aliases_fail_closed(self):
        from native_results import deduplicate_images,original_images
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            for name,data in [('a.png',b'original bytes'),('b.png',b'original bytes'),
                              ('c.png',b'different original'),('report.json',b'{}')]:
                (root/name).write_bytes(data)
            original=bind_files(root)
            aliases=deduplicate_images(root)
            physical=bind_files(root)
            self.assertEqual(len(aliases),1)
            self.assertFalse((root/'b.png').exists())
            with original_images(root,physical,aliases):
                self.assertEqual(bind_files(root),original)
            self.assertFalse((root/'b.png').exists())
            for changed in [aliases*2,[{**aliases[0],'file':'../escape.png'}],
                            [{**aliases[0],'file':'a.png'}],[{**aliases[0],'source':'b.png'}],
                            [{**aliases[0],'sha256':'0'*64}],[{**aliases[0],'file':'false.json'}],
                            [{**aliases[0],'source':'c.png'}]]:
                with self.subTest(aliases=changed),self.assertRaises((ValueError,FileExistsError)):
                    with original_images(root,physical,changed): pass
                self.assertEqual(bind_files(root),physical)
            with self.assertRaisesRegex(ValueError,'deliberate'):
                with original_images(root,physical,aliases): raise ValueError('deliberate reader failure')
            self.assertEqual(bind_files(root),physical)
            # Even with self-consistent alias metadata, actual changed bytes fail.
            (root/'a.png').write_bytes(b'changed source')
            with self.assertRaises(ValueError):
                with original_images(root,physical,aliases): pass

    def test_hn_samples_replay_all_bands_and_reject_rehashed_pixel_mutations(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest('Isolated Product image dependency')
        import hashlib
        from hn_evidence import verify
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            rows=[]
            for width,height,ui in ((1280,720,125),(1920,1080,100),(2560,1440,125)):
                for kind,context in [('row',[-1,2]),('column',[2,-1]),('grid',[2,2]),
                                     ('complete-row',[-1,49]),('drag-row',[-1,2])]:
                    image=Image.new('RGBA',(50,100),(240,230,220,255))
                    count=0
                    for y in range(50):
                        for x in range(50):
                            if x==context[0] or y==context[1]:
                                image.putpixel((x,y),(220,210,200,255));count+=1
                    name=f'hn-{width}-ui{ui}-{kind}.png'
                    image.save(root/name)
                    rows.append(dict(kind='pixels',file=name,context=context,marked=count,unmarked=2500-count,
                                     evidence='picross-hn-samples-v1',grid_origin=[4,4],board=[10,10,60,60],
                                     overlay=[0,0,0,0],client=[width,height],ui=ui/100,cell=1,
                                     source_rgba_sha256=dict(frame='a'*64,baseline='b'*64,
                                         samples=hashlib.sha256(image.tobytes()).hexdigest())))
            report=dict(checks=1001,failures=0,records=rows)
            self.assertEqual(verify(root,report),15)
            path=root/rows[0]['file'];original=path.read_bytes()
            # HN binds raw RGBA sample bytes; this reader is intentionally not
            # migrated to RGB. A format change cannot silently pass its gate.
            with Image.open(path) as source:source.convert('RGB').save(path)
            with self.assertRaisesRegex(ValueError,'readback'):verify(root,report)
            path.write_bytes(original)
            for pixel,color in [((20,20),(220,210,200,255)),((20,2),(240,230,220,255)),
                                ((20,20),(240,230,220,0))]:
                with Image.open(path) as source:changed=source.copy()
                changed.putpixel(pixel,color);changed.save(path)
                rows[0]['source_rgba_sha256']['samples']=hashlib.sha256(changed.tobytes()).hexdigest()
                with self.subTest(pixel=pixel,color=color),self.assertRaisesRegex(ValueError,'band/phantom'):
                    verify(root,report)
                path.write_bytes(original)
            with self.assertRaisesRegex(ValueError,'readback'):verify(root,report)
            report['records']=rows[:-1]
            with self.assertRaisesRegex(ValueError,'Incomplete native HN'):verify(root,report)

    def test_native_ke_images_are_required_but_not_python_crop_work(self):
        from native_results import validate_catalog_images
        binding=dict(stored_region=[1,2,7,8],source_rgba_sha256='a'*64,stored_rgba_sha256='b'*64)
        entries=[dict(file='frame-card.png',source='frame.png',region=[1,2,7,8],source_size=[10,10],**binding)]
        costs=dict(status='success',input_frames=1,crops=1,entries=entries)
        summary=dict(image_costs=costs,crops=entries,reports=[dict(captures=[dict(file='frame.png',framebuffer=[10,10],regions=dict(card=[1,2,7,8]),**binding)])])
        required={'kat2/frame-card.png','kat2/direct.png','kat2/report.json'}
        validate_catalog_images(costs,summary,required,['kat2/direct.png'])
        for direct in ([],['kat2/direct.png','kat2/unexpected.png']):
            with self.assertRaises(ValueError):validate_catalog_images(costs,summary,required,direct)
        changed=deepcopy(summary);changed['reports'][0]['captures'][0]['regions']['card'][0]=0
        with self.assertRaises(ValueError):validate_catalog_images(costs,changed,required,['kat2/direct.png'])
        for key in binding:
            changed=deepcopy(summary);changed['reports'][0]['captures'][0][key]=None
            with self.subTest(binding=key),self.assertRaisesRegex(ValueError,'readback binding'):
                validate_catalog_images(costs,changed,required,['kat2/direct.png'])

    def test_native_precrop_preserves_the_exact_old_full_frame_pixels(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest('Isolated Product image dependency')
        from native_images import crop_native,require_identical
        from native_results import validate_catalog_originals
        import hashlib
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            im=Image.new('RGBA',(19,13))
            im.putdata([(x*7%256,x*17%256,x*31%256,x*13%256) for x in range(19*13)])
            rectangle=[1,2,17,11]
            crop=im.crop(rectangle)
            before=root/'before';before.mkdir();im.save(before/'native.png')
            after=root/'after';after.mkdir();crop.save(after/'native.png')
            record=dict(file='native.png',regions={'layout':rectangle},framebuffer=[19,13],
                        stored_region=rectangle,source_rgba_sha256=hashlib.sha256(im.tobytes()).hexdigest(),
                        stored_rgba_sha256=hashlib.sha256(crop.tobytes()).hexdigest())
            crop_native(before,[dict(captures=[dict(file='native.png',regions={'layout':rectangle})])])
            entries,cost=crop_native(after,[dict(captures=[record])],compare=True)
            require_identical(before/'native-layout.png',after/'native-layout.png')
            validate_catalog_originals(cost,after)
            actual=after/'native-layout.png';original=actual.read_bytes()
            actual.write_bytes(original+b'changed')
            with self.assertRaisesRegex(ValueError,'original native crop'):validate_catalog_originals(cost,after)
            actual.write_bytes(original)
            wrong=deepcopy(cost);wrong['entries'][0]['region']=[0,0,1,1]
            with self.assertRaisesRegex(ValueError,'original native crop'):validate_catalog_originals(wrong,after)
            self.assertEqual(entries[0]['source_size'],[19,13])
            self.assertEqual(entries[0]['stored_rgba_sha256'],record['stored_rgba_sha256'])
            self.assertLess(cost['input_bytes'],(before/'native-context.png').stat().st_size)
            for change in ('alpha','size'):
                bad=root/change;bad.mkdir();mutated=crop.copy()
                if change=='alpha':mutated.putpixel((0,0),(1,2,3,4))
                else:mutated=mutated.crop((0,0,15,9))
                mutated.save(bad/'native.png')
                with self.subTest(change=change),self.assertRaisesRegex(ValueError,'pixels/dimensions'):
                    crop_native(bad,[dict(captures=[record])])

    def test_native_rgb_crop_keeps_rgba_binding_and_rejects_lost_alpha(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest('Isolated Product image dependency')
        import hashlib
        from native_images import crop_native
        from native_results import validate_catalog_originals
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for alpha in (255, 254, 80, 0):
                directory = root / str(alpha)
                directory.mkdir()
                rgba = Image.new('RGBA', (3, 2), (56, 132, 90, alpha))
                rgba.convert('RGB').save(directory / 'native.png')
                record = dict(file='native.png', regions={'layout':[0,0,3,2]},
                              framebuffer=[3,2], stored_region=[0,0,3,2],
                              source_rgba_sha256=hashlib.sha256(rgba.tobytes()).hexdigest(),
                              stored_rgba_sha256=hashlib.sha256(rgba.tobytes()).hexdigest())
                if alpha == 255:
                    _, costs = crop_native(directory, [dict(captures=[record])])
                    validate_catalog_originals(costs, directory)
                else:
                    with self.subTest(alpha=alpha), self.assertRaisesRegex(ValueError, 'pixels/dimensions'):
                        crop_native(directory, [dict(captures=[record])])

    def test_lossless_crop_and_negative_rgba_alpha_dimension_controls(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest('Image dependency checked in isolated Product job')
        from native_images import crop_native,require_identical
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            im=Image.new('RGBA',(19,13))
            im.putdata([(x*7%256,x*17%256,x*31%256,x*13%256) for x in range(19*13)])
            im.save(root/'native.png')
            reports=[dict(captures=[dict(file='native.png',regions={'one':[1,2,17,11],'two':[0,0,19,13]})])]
            crops,costs=crop_native(root,reports,compare=True)
            self.assertEqual(costs['input_frames'],1);self.assertEqual(costs['crops'],2)
            self.assertTrue(all(r['identical'] for r in crops))
            target=root/'native-two.png'
            for mode in ('rgb','alpha','size'):
                changed=im.copy()
                if mode=='size':changed=changed.crop((0,0,18,13))
                else:
                    pixel=list(changed.getpixel((0,0)));pixel[0 if mode=='rgb' else 3]^=1;changed.putpixel((0,0),tuple(pixel))
                changed.save(root/'changed.png')
                with self.assertRaises(ValueError):require_identical(target,root/'changed.png')

    def test_partial_image_error_is_persisted(self):
        try: import PIL
        except ImportError: self.skipTest('Isolated Product image dependency')
        from native_images import crop_native
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            with self.assertRaises(OSError):crop_native(root,[dict(captures=[dict(file='missing.png',regions={})])])
            self.assertEqual(read(root/'image-costs.json')['status'],'failure')
