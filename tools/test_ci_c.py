"""CI-C adversarial selection, isolation, byte/pixel preservation and result gates."""
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from ci_scope import classify, apply_event_policy, evaluate, JOBS
from native_contract import GROUPS, SCOPES, checks, coverage
from native_results import bind_files, read, validate_all, validate_payload
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
            ('game/ui/catalog.gd',['core','catalog','completion','export']),
            ('game/ui/completion.gd',['core','completion','graphics','export'])]:
            with self.subTest(path=path):
                self.assertEqual(classify([path])['native_groups'],groups)
        for path in ['game/ui/main.gd','game/model/save_store.gd','tools/product_fixtures.py',
                     'tools/native_runner.py','tools/native_results.py','tools/new_harness.py',
                     '.github/workflows/p1-product.yml','game/tests/new_probe.gd']:
            self.assertEqual(classify([path])['native_groups'], list(GROUPS))
        self.assertEqual(classify(['tools/ea_product.py','tools/kat2_product.py'])['native_groups'],['catalog','completion'])
        self.assertEqual(classify(['tools/ea_product.py','docs/README.md'])['native_groups'],['completion'])

    def test_manual_only_widens_and_main_content_remain_short(self):
        for group in GROUPS:
            self.assertEqual(classify([], 'native-'+group)['native_groups'], [group])
            self.assertEqual(classify(['unknown.py'], 'native-'+group)['native_groups'],list(GROUPS))
        for scope in ('all','toolchain','production'):
            self.assertEqual(classify([],scope)['native_groups'],list(GROUPS))
        for scope in ('runtime','visual','perf-b','production'):
            self.assertTrue(classify([],scope)['selected']['web'])
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


class Isolation(unittest.TestCase):
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
