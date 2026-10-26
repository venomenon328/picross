"""CI2-B positive/negative scope, transport, measured execution and evidence tests.

Synthetic gate fixtures claim no real production success; real CI uses the runner.
"""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import production_contract as contract
from production_results import validate_all, validate_tests, files
from production_tests import MeasuredResult, MeasuredSuite
from ci_scope import FLAGS, JOBS, classify, apply_event_policy, evaluate, validate_binding

ROOT = Path(__file__).resolve().parents[1]


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def fixture(plan, directory):
    """Small deliberately synthetic input to the actual report validator."""
    directory.mkdir(parents=True, exist_ok=True)
    groups = plan['production_groups']
    expected = contract.expected_tests(ROOT, groups)
    rows = [dict(id=name, group=group, status='success', seconds=0) for name, group in expected.items()]
    owners = {(module,kind) for module in {name.split('.')[0] for name in expected}
              for kind in ('module-load','module-setup','module-teardown')}
    owners |= {(owner,kind) for owner in {name.rsplit('.',1)[0] for name in expected}
               for kind in ('class-setup','class-teardown')}
    module_groups = {name.split('.')[0]:group for name,group in expected.items()}
    fixtures = [dict(owner=owner,kind=kind,group=module_groups[owner.split('.')[0]],seconds=0) for owner,kind in sorted(owners)]
    tests = dict(format='picross-production-tests-v1', accepted=True, groups=groups, tests=rows, fixtures=fixtures,
                 group_times={g:dict(tests=sum(r['group']==g for r in rows), test_seconds=0,fixture_seconds=0,seconds=0) for g in groups},
                 top10=sorted(rows,key=lambda r:r['id'])[:10], seconds=0)
    write(directory/'tests.json', tests)
    (directory/'tests.log').write_text('SYNTHETIC GATE FIXTURE ONLY\n', encoding='utf-8')
    integrations=[]
    if 'solver' in groups:
        integrations.append(dict(name='references',group='solver',exit_code=0,seconds=0))
        cases=[]
        for case in contract.REFERENCES:
            status='stalled' if 'sparse' in case else 'solved'
            result=dict(status=status,proof_verified=True,certified=status=='solved',logic_hash='a'*64,
                        profile_hash='b'*64,profile={'synthetic':True})
            metric=dict(exit_code=0,peak_rss_bytes=1)
            for name in ('logic.json','proof.json','result.json','fresh-verification.json','solve-metrics.json',
                         'verify-metrics.json','solve.log','verify.log'):
                write(directory/'references'/case/name, result if name in ('result.json','fresh-verification.json') else
                      metric if name.endswith('-metrics.json') else {'synthetic':True})
            from production_results import checksum
            cases.append(dict(name=case,accepted=True,result=result,fresh_verification=result,
                              proof_sha256=checksum(directory/'references'/case/'proof.json'),
                              processes=[dict(mode=mode,**metric) for mode in ('solve','verify')],
                              logic_hash='a'*64,profile_hash='b'*64,profile={'synthetic':True}))
        write(directory/'references/benchmark.json',dict(accepted=True, source_head=plan['source_head'],
            base_commit=plan['base_commit'], checkout_commit=plan['tested_checkout'],cases=cases))
        write(directory/'references.log',{'synthetic':True})
    if 'adapter' in groups:
        integrations.append(dict(name='za1-replay',group='adapter',exit_code=0,seconds=0))
        write(directory/'za1-replay/replay.json',dict(accepted=True,reports=[dict(puzzle_id='pz-test-'+name,catalog_ready=True)
            for name in ('direct-color','direct-mono','repair-color','repair-mono')]))
        write(directory/'za1-replay.log', {'synthetic':True})
    binding={k:plan[k] for k in ('source_head','base_commit','tested_checkout','run_id','run_attempt')}
    report=dict(format='picross-production-result-v1',accepted=True,tests_accepted=True,source_unchanged=True,groups=groups,
                expected=contract.coverage(groups),binding={**binding,'selection_attempt':plan['run_attempt'],'git_status':''},
                integrations=integrations,seconds=0,files=files(directory))
    write(directory/'production-result.json', report)
    return report


def plan_for(paths):
    result=apply_event_policy(classify(paths),'pull_request')
    result.update(source_head='a'*40,base_commit='b'*40,tested_checkout='c'*40,run_id='123',run_attempt='1',
                  comparison='exact-base-to-head-trees-no-renames',diff_check='full-whitespace-check')
    return result


class SelectionTests(unittest.TestCase):
    def test_current_import_consumers_and_every_test_module_are_assigned(self):
        self.assertEqual(contract.audited_consumers(ROOT),contract.SOURCE_GROUPS)
        ids=contract.expected_tests(ROOT,list(contract.GROUPS))
        self.assertTrue(ids)
        self.assertEqual(len(ids),len(set(ids)))
        # A future module must fail the existing path, not silently disappear.
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);directory=root/'tests/puzzle_production';directory.mkdir(parents=True)
            (directory/'test_unassigned.py').write_text('pass\n')
            with self.assertRaises(ValueError):contract.expected_tests(root,['solver'])

    def test_narrow_cases_union_shared_sources_and_main_policy(self):
        for path,groups in (('tests/puzzle_production/test_lines.py',['solver']),
                            ('tests/puzzle_production/test_images.py',['images']),
                            ('tests/puzzle_production/test_target_adapter.py',['adapter']),
                            ('tests/puzzle_production/test_content_update.py',['catalog'])):
            self.assertEqual(classify([path])['production_groups'],groups)
        paths=['tests/puzzle_production/test_lines.py','tests/puzzle_production/test_content_update.py']
        self.assertEqual(classify(paths)['production_groups'],['solver','catalog'])
        for path in ('tools/puzzle_production/contract.py','tools/puzzle_production/new_module.py',
                     '.github/workflows/puzzle-production.yml','tools/ci_scope.py'):
            plan=classify([path]);self.assertEqual(plan['production_groups'],list(contract.GROUPS))
            self.assertFalse(plan['selected']['web'])
        plan=apply_event_policy(classify(paths),'push')
        self.assertEqual(plan['production_groups'],[]);self.assertEqual(plan['production_expected'],{})
        self.assertEqual(classify([], 'production')['production_groups'],list(contract.GROUPS))

    def test_selection_and_canonical_scheduler_scope_fail_closed(self):
        plan=plan_for(['tests/puzzle_production/test_lines.py'])
        results={j:dict(result='success' if plan['selected'][j] else 'skipped') for j in JOBS}
        self.assertTrue(all(r['accepted'] for r in evaluate(plan,results)))
        outputs={**{k:str(plan['selected'][k]).lower() for k in FLAGS},'selection_attempt':'1','native_groups':'[]',
                 'production_groups':contract.output(plan['production_groups']),'browser_request':'null'}
        binding={k:plan[k] for k in ('source_head','base_commit','tested_checkout','run_id','run_attempt','event')}
        validate_binding(plan,{**binding,'gate_attempt':'2'},outputs)
        for value in ('', '[]', '["solver","solver"]', '["unknown"]', '[ "solver" ]', None):
            with self.assertRaises(ValueError):validate_binding(plan,{**binding,'gate_attempt':'2'},{**outputs,'production_groups':value})
        for key in ('production_groups','production_expected'):
            changed=deepcopy(plan);changed[key]=[]
            with self.assertRaises(ValueError):evaluate(changed,results)
        with self.assertRaises(ValueError):contract.parse_groups('solver,solver')
        with self.assertRaises(ValueError):contract.parse_groups('')
        with self.assertRaises(ValueError):contract.parse_groups('unknown')


class EvidenceTests(unittest.TestCase):
    def test_selected_tests_integrations_bytes_and_attempts_are_required(self):
        plan=plan_for(['tools/ci_scope.py'])
        with tempfile.TemporaryDirectory() as temporary:
            directory=Path(temporary);report=fixture(plan,directory)
            outputs={'production_attempt':'1'}
            self.assertTrue(validate_all(plan,directory,outputs,'2')['tests'])
            for key,value in (('accepted',False),('groups',[]),('integrations',[]),('files',[])):
                changed=deepcopy(report);changed[key]=value;write(directory/'production-result.json',changed)
                with self.assertRaises(ValueError):validate_all(plan,directory,outputs,'2')
            for key in report['binding']:
                changed=deepcopy(report);changed['binding'][key]='wrong';write(directory/'production-result.json',changed)
                with self.assertRaises(ValueError):validate_all(plan,directory,outputs,'2')
            write(directory/'production-result.json',report)
            for bad in ({},{'production_attempt':''},{'production_attempt':'2'},{'production_attempt':'1','other':'1'}):
                with self.assertRaises(ValueError):validate_all(plan,directory,bad,'2')
            reference=directory/'references/benchmark.json'
            original=json.loads(reference.read_text(encoding='utf-8'))
            for change in ('missing-process','failed-process','false-proof'):
                changed=deepcopy(original)
                case=changed['cases'][0]
                if change=='missing-process':case['processes'].pop()
                elif change=='failed-process':case['processes'][0]['exit_code']=1
                else:case['fresh_verification']['proof_verified']=False
                write(reference,changed)
                # Even recomputing the enclosing file manifest cannot turn
                # missing/unsuccessful integration evidence into a pass.
                write(directory/'production-result.json',{**report,'files':files(directory)})
                with self.assertRaises(ValueError):validate_all(plan,directory,outputs,'2')
            write(reference,original);write(directory/'production-result.json',report)
            (directory/'tests.log').write_bytes(b'changed')
            with self.assertRaises(ValueError):validate_all(plan,directory,outputs,'2')

    def test_missing_duplicate_failed_skipped_unknown_tests_and_omitted_setup_fail(self):
        plan=plan_for(['tests/puzzle_production/test_lines.py'])
        with tempfile.TemporaryDirectory() as temporary:
            directory=Path(temporary);fixture(plan,directory)
            original=json.loads((directory/'tests.json').read_text(encoding='utf-8'))
            validate_tests(original,['solver'])
            attacks=[lambda r:r['tests'].pop(),lambda r:r['tests'].append(r['tests'][0]),
                     lambda r:r['tests'][0].update(id='unknown'),lambda r:r['tests'][0].update(status='failure'),
                     lambda r:r['tests'][0].update(status='skipped'),lambda r:r['tests'][0].update(seconds=True),
                     lambda r:r['fixtures'].pop(),lambda r:r['fixtures'].append(r['fixtures'][0]),
                     lambda r:r['group_times']['solver'].update(fixture_seconds=1)]
            for attack in attacks:
                changed=deepcopy(original);attack(changed)
                with self.assertRaises(ValueError):validate_tests(changed,['solver'])

    def test_real_unittest_lifecycle_times_setup_cleanup_and_class_fixture(self):
        import io
        clock=[0]
        class Probe(unittest.TestCase):
            @classmethod
            def setUpClass(cls):clock[0]+=3
            def setUp(self):clock[0]+=2;self.addCleanup(lambda:clock.__setitem__(0,clock[0]+5))
            def test_body(self):clock[0]+=7
        suite=MeasuredSuite([Probe('test_body')])
        with patch('production_tests.time.perf_counter',side_effect=lambda:clock[0]):
            result=unittest.TextTestRunner(stream=io.StringIO(),resultclass=MeasuredResult).run(suite)
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(result.rows[0]['seconds'],14)
        self.assertEqual(sum(r['seconds'] for r in suite.fixtures),3)


if __name__=='__main__':unittest.main()
