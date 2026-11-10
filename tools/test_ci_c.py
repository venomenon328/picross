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
from native_results import bind_files, read, digest, validate_all, validate_payload, validate_rp6_capture, check_phases, validate_background_log
from p1_product import parse_args
from native_runner import requested
from test_zs2_evidence import selected_log, selected_rows

ROOT = Path(__file__).resolve().parents[1]


def rp6_report(number):
    """Small synthetic gate input, not substitute native/Save evidence."""
    labels = [
        ['fresh pilot hides reveal', 'own incorrect miniature retained', 'mouse undo', 'mouse redo',
         'album own wrong miniature and no spoiler/name', 'bound regular clue font',
         'work and critical controls accessible', 'native pixel wrong-block'],
        ['nine real visible undo clicks remove the wrong block', 'real visible plus click retains normal zoom',
         'selected partial has no reveal', 'native pixel wrong-corner'],
        ['album no hidden reveal payload', 'selected partial has no reveal', 'native pixel wrong-corner'],
        ['capture partial flush', 'native capture restores real mouse completion', 'capture completion slot freshly loaded'],
        [],
    ]
    colors = ['#343f42'] if number == 4 else ['#253342','#637b58','#c89d56','#b55848']
    size = 20 if number == 4 else 50
    width, height, scale = (1920,1080,1.0) if number == 4 else (1280,720,1.25)
    rows = []
    for i, state in enumerate(('work','detail','album-partial','completion','album-completed')):
        earned = i >= 3
        cells = [-1]*(size*size)
        cells[0] = 1
        if state == 'work':
            for y in range(2,5):
                for x in range(2,5): cells[y*size+x] = 1
        pixels = {'wrong-block' if i == 0 else 'wrong-corner':colors[0][1:]}
        if earned:
            labels[i] += ['selected earned artwork visible and proportional', 'selected earned artwork bound to slot',
                          'native pixel reveal-center','native pixel reveal-background']
            pixels = {'reveal-center':'ffffff','reveal-background':'6c9aab' if number == 4 else 'edca78'}
        rows.append(dict(id=f'{state}-{width}-ui{int(scale*100)}', definition_id=f'T-{number:02d}',
            slot=f't{number:02d}.json',size=[width,height],ui_scale=scale,completed=earned,
            reveal=dict(version=1,definition_id=f'T-{number:02d}',name=f'TEST ONLY Muster {number}',
                        image=f'res://art/fixtures/t{number:02d}.svg') if earned else {},
            palette=[dict(id=i+1,color=c,symbol=chr(65+i)) for i,c in enumerate(colors)],
            own_miniature=cells,font='Delight Coffee',layout_valid=True,grid_fit=True,pixels=pixels,
            assertions=[dict(label=label,passed=True) for label in labels[i]],checks=len(labels[i])))
    return dict(captures=rows,checks=sum(r['checks'] for r in rows),failures=0,
                failure_captures=[],pending_failures=[],pending_assertions=[])


class RP6CaptureGate(unittest.TestCase):
    def test_selected_cases_slots_pixels_and_positive_checks_fail_closed(self):
        for number in (4,6):
            original = rp6_report(number)
            validate_rp6_capture(original, number)
            mutations = [
                lambda d: d['captures'].pop(),
                lambda d: d['captures'].append(deepcopy(d['captures'][0])),
                lambda d: d['captures'].__setitem__(1,deepcopy(d['captures'][0])),
                lambda d: d['captures'][0].update(slot='t08.json'),
                lambda d: d['captures'][0].update(definition_id='T-08'),
                lambda d: d['captures'][0].update(size=[1280,720] if number == 4 else [1920,1080]),
                lambda d: d['captures'][0].update(ui_scale=2),
                lambda d: d['captures'][0].update(checks=0),
                lambda d: d['captures'][0]['assertions'][0].update(passed=False),
                lambda d: d['captures'][0]['assertions'][0].update(label='unexecuted replacement'),
                lambda d: d['captures'][1]['own_miniature'].__setitem__(2*(20 if number==4 else 50)+2,1),
                lambda d: d['captures'][2].update(reveal={'spoiler':True}),
                lambda d: d['captures'][3]['reveal'].update(definition_id='T-08'),
                lambda d: d['captures'][3]['pixels'].update(**{'reveal-center':'000000'}),
                lambda d: d['captures'][4].update(completed=False),
                lambda d: d.update(checks=d['checks']+1),
                lambda d: d.update(failures=1),
                lambda d: d.update(pending_assertions=[dict(label='unobserved',passed=True)]),
            ]
            for i, mutate in enumerate(mutations):
                changed = deepcopy(original); mutate(changed)
                with self.subTest(number=number,mutation=i), self.assertRaises(ValueError):
                    validate_rp6_capture(changed, number)

    def test_producer_and_phase_contract_remove_only_two_render_processes(self):
        from p1_product import run_pilot_visual
        from native_contract import artifacts
        expected = {f'rp6-t{n:02d}-{s}' for n in (4,6,8,9) for s in ('partial','finish','read')}
        expected |= {'rp6-t04-render','rp6-t06-render','rp6-t04-foreign-slot-write','rp6-t04-foreign-slot-control'}
        self.assertEqual({p for p in checks('adapters') if p.startswith('rp6-')},expected)
        self.assertEqual([p for p in artifacts('adapters') if p.startswith('renders/')],
                         ['renders/rp6-t04-renders.json','renders/rp6-t06-renders.json'])
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); calls=[]; environment={}
            def phase(name, command, marker):
                calls.append((name,environment['RP6_INDEX'],environment['P1_TEST_SAVE_ROOT'],marker))
            run_pilot_visual(root,root,root/'game','godot',environment,phase,'Linux')
            self.assertEqual(calls,[(f'rp6-t{n:02d}-render',str(index),str(root/'rp6-saves'),'RP6_CAPTURE_OK')
                                    for n,index in ((4,2),(6,3))])
            self.assertNotIn('RP6_INDEX',environment)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value)+'\n', encoding='utf-8')


class BackgroundEvidenceGate(unittest.TestCase):
    def test_background_result_is_one_closed_positive_integer_record(self):
        for count in (1, 7):
            text = 'Godot synthetic banner\nBACKGROUND_TESTS_OK '+json.dumps({'checks':count})+'\n'
            self.assertEqual(validate_background_log(text), count)
        payloads = [
            '{}', '[]', 'null', '{"checks":0}', '{"checks":-1}', '{"checks":true}',
            '{"checks":false}', '{"checks":null}', '{"checks":"1"}', '{"checks":1.0}',
            '{"checks":1e0}', '{"checks":NaN}', '{"checks":Infinity}', '{"checks":1e309}',
            '{"checks":1,"extra":true}', '{"checks":1,"checks":2}', '{"checks":',
        ]
        good = 'BACKGROUND_TESTS_OK {"checks":3}\n'
        malformed = ['BACKGROUND_TESTS_OK '+payload+'\n' for payload in payloads]
        malformed += ['', 'BACKGROUND_TESTS_OK\n', 'prefix '+good, good+good,
                      good+'BACKGROUND_TEST_FAILED: synthetic failed assertion\n',
                      good+'ERROR: synthetic engine failure\n',
                      good+'SCRIPT ERROR: synthetic runtime failure\n']
        for text in malformed:
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, 'BACKGROUND'):
                validate_background_log(text)

    def test_catalog_gate_rejects_rehashed_background_log_and_marker_changes(self):
        # Exercise the actual independent phase gate with the complete selected
        # catalog contract, real log bytes and fresh hashes; no native/PNG claim.
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)/'catalog'
            (directory/'logs').mkdir(parents=True)
            report = {'checks':[]}
            no_log = {'current-resource-hashes', 'verified-toolchain-assets', 'current-atlas-resources',
                      'kat2-adapter-export', 'kat2-adapter-register', 'kat2-imported-base-copies'}
            good = 'BACKGROUND_TESTS_OK {"checks":3}\n'

            def bind_log(row, text):
                path = directory/'logs'/(row['name']+'.log')
                path.write_text(text, encoding='utf-8')
                row['log'] = dict(file=path.name, retained_bytes=path.stat().st_size,
                                  original_bytes=path.stat().st_size, abbreviated=False, sha256=digest(path))

            for name in checks('catalog'):
                row = dict(name=name, status='success', seconds=.01, exit_code=0, expected_failure=False)
                if name not in no_log:
                    bind_log(row, good if name == 'background-contract' else 'synthetic process output\n')
                if name == 'background-contract':
                    row['required_marker'] = 'BACKGROUND_TESTS_OK'
                report['checks'].append(row)
            background = next(row for row in report['checks'] if row['name'] == 'background-contract')
            check_phases(report, checks('catalog'), directory)
            for text, marker in (
                ('BACKGROUND_TESTS_OK {"checks":0}\n', 'BACKGROUND_TESTS_OK'),
                ('BACKGROUND_TESTS_OK {"checks":true}\n', 'BACKGROUND_TESTS_OK'),
                ('BACKGROUND_TESTS_OK {"checks":3,"extra":true}\n', 'BACKGROUND_TESTS_OK'),
                (good+good, 'BACKGROUND_TESTS_OK'),
                (good+'SCRIPT ERROR: synthetic runtime failure\n', 'BACKGROUND_TESTS_OK'),
                ('FORGED_BACKGROUND_OK {"checks":3}\n', 'FORGED_BACKGROUND_OK'),
                ('synthetic success with no result\n', None),
                (good, None),
                (good, ''),
            ):
                bind_log(background, text)
                if marker is None:
                    background.pop('required_marker', None)
                else:
                    background['required_marker'] = marker
                with self.subTest(text=text, marker=marker), self.assertRaisesRegex(ValueError, 'BACKGROUND'):
                    check_phases(report, checks('catalog'), directory)


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
        # the album; KAT-2 also exercises completed catalog states.
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
                log.write_bytes(selected_log().encode() if name == 'current-drawing-tests' else b'synthetic process output')
                report['checks'][-1]['log']=dict(file=log.name,retained_bytes=log.stat().st_size,
                    original_bytes=log.stat().st_size,abbreviated=False,sha256=digest(log))
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

    def test_rehashed_core_log_cannot_hide_missing_or_forged_zs2_trace(self):
        log = self.root/'core/logs/current-drawing-tests.log'
        path = self.root/'core/product-report.json'
        report = read(path)
        self.check()
        for mutate in (lambda rows: rows.pop(6),
                       lambda rows: rows[6].update(id=rows[7]['id']),
                       lambda rows: rows[6]['data']['effects'][0].__setitem__(1, 1000012)):
            rows = selected_rows(); mutate(rows)
            log.write_bytes(selected_log(rows).encode())
            phase = next(p for p in report['checks'] if p['name'] == 'current-drawing-tests')
            phase['log'].update(retained_bytes=log.stat().st_size, original_bytes=log.stat().st_size, sha256=digest(log))
            write(path, report)
            self.result['files'] = bind_files(self.root, exclude={'native-result.json'})
            with self.assertRaisesRegex(ValueError, 'ZS2'): self.check()

    def test_adapter_payload_rehash_cannot_hide_missing_or_forged_selected_capture(self):
        from native_contract import artifacts
        (self.root/'core').rename(self.root/'adapters')
        directory=self.root/'adapters'; path=directory/'product-report.json'
        report=read(path); report.update(native_group='adapters',checks=[])
        for name in checks('adapters'):
            negative=name=='rp6-t04-foreign-slot-control'
            row=dict(name=name,status='success',seconds=.1,exit_code=4 if negative else 0,expected_failure=negative)
            if name not in ('current-resource-hashes','verified-toolchain-assets','current-atlas-resources','za1-test-only-registration'):
                log=directory/'logs'/(name+'.log'); log.write_bytes(b'synthetic process output')
                row['log']=dict(file=log.name,retained_bytes=24,original_bytes=24,abbreviated=False,sha256=digest(log))
            report['checks'].append(row)
        for name,scope in report['scope'].items():
            scope.update(enabled=name=='pilots',status='success' if name=='pilots' else 'not_applicable')
        selected=directory/'selected'
        for name in artifacts('adapters'):
            data=rp6_report(int(name[13:15])) if name.startswith('renders/rp6-') else dict(checks=1,failures=0)
            write(selected/name,data)
        self.result.update(groups=['adapters'],expected=coverage(['adapters']),
                           results=[dict(group='adapters',status='success',exit_code=0)])
        def refresh():
            report['selected_evidence']['files']=bind_files(selected)
            write(path,report)
            self.result['files']=bind_files(self.root,exclude={'native-result.json'})
        refresh(); validate_payload(self.result,self.root)
        original=rp6_report(6); capture=selected/'renders/rp6-t06-renders.json'
        for mutate in (lambda d:d['captures'][3].update(slot='t08.json'),
                       lambda d:d['captures'].pop(),
                       lambda d:d['captures'][4]['pixels'].update(**{'reveal-center':'000000'})):
            changed=deepcopy(original); mutate(changed); write(capture,changed); refresh()
            with self.assertRaisesRegex(ValueError,'RP6'):validate_payload(self.result,self.root)
        capture.unlink(); refresh()
        with self.assertRaisesRegex(ValueError,'mandatory files'):validate_payload(self.result,self.root)

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
        # Reproduce the manual diagnostic gate's sparse boundary in an isolated
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
                     'from native_results import read,validate_payload; '
                     'root=Path(sys.argv[2]); validate_payload(read(root/"native-result.json"),root)',
                     str(checkout/'tools'),str(self.root)]
            positive=subprocess.run(command,cwd=checkout,capture_output=True)
            self.assertEqual(positive.returncode,0,positive.stderr)
            self.assertFalse((checkout/'tools/book_contract.py').exists())
            self.assertFalse((checkout/'game/tests/book_integration.gd').exists())
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
            for width,height,ui in ((1280,720,125),):
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
            self.assertEqual(verify(root,report),5)
            path=root/rows[0]['file'];original=path.read_bytes()
            # HN requires the original RGBA readback representation.
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
