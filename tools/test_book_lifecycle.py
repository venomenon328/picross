"""Explicit diagnostic binding and standard CI's deliberately smaller export scope."""
import json
import ast
from pathlib import Path
import tempfile
import unittest
from copy import deepcopy
import os
import subprocess
import hashlib
import sys
from unittest.mock import patch
from book_contract import SOURCES, INTEGRATION_ASSERTIONS

import book_lifecycle
import ci_scope
from native_contract import checks
from native_results import bind_files, check_phases, validate_book_lifecycle


class BookLifecycleTests(unittest.TestCase):
    def test_targeted_product_route_and_gate_exclude_full_study_and_movie(self):
        identity = dict(source_commit='a'*40, source_tree_dirty=False,
                        base_commit='b'*40, tested_checkout_commit='c'*40,
                        github_run_id='17', github_run_attempt='2')
        calls = []
        def phase(name, command, environment, timeout, logs):
            calls.append(command)
            (logs/(name+'.log')).write_text('synthetic successful native process\n')
            if name == 'book-integration':
                directory = Path(environment['BOOK_INTEGRATION_OUTPUT'])
                (directory/'integration.json').write_text(json.dumps(dict(passed=True,
                    assertions=[dict(label=label,passed=True) for label in INTEGRATION_ASSERTIONS])))
                (directory/'saves').mkdir()
                (directory/'saves/private-fixture.json').write_text('{}')
            return dict(name=name,output='synthetic',exit_code=0,timed_out=False,seconds=.1)
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)/'proof'
            with patch.dict(os.environ, {'GITHUB_ACTIONS':'true'}), \
                    patch.object(book_lifecycle.tc,'request_json'), \
                    patch.object(book_lifecycle.tc,'official_asset_urls',return_value={book_lifecycle.tc.EDITORS[book_lifecycle.platform.system()].name:'unused'}), \
                    patch.object(book_lifecycle.tc,'download_asset'), \
                    patch.object(book_lifecycle.tc,'extract_editor',return_value=Path('synthetic-engine')), \
                    patch.object(book_lifecycle,'copy_regression_game'), patch.object(book_lifecycle,'run_phase',side_effect=phase), \
                    patch.object(book_lifecycle,'require_clean_output'), \
                    patch.object(book_lifecycle,'source_identity',return_value=identity):
                study = book_lifecycle.run_lifecycle(Path(temp)/'cache',output)
            self.assertEqual([p['name'] for p in study['phases']],['book-version','book-import','book-integration'])
            self.assertFalse(any('--write-movie' in c or 'res://study/book/verify.gd' in c for c in calls))
            self.assertFalse(list(output.rglob('saves')))
            host = book_lifecycle.platform.system()
            report = dict(book_lifecycle=study)
            validate_book_lifecycle(report,output,identity,host)
            # The same otherwise valid evidence fails when the checkout lacks
            # an actual source in an incomplete explicit diagnostic checkout.
            with patch('native_results.__file__',str(Path(temp)/'missing-checkout/tools/native_results.py')):
                with self.assertRaises(FileNotFoundError):
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
            for mutation in ('source','source-omitted','phase','phase-omitted','phase-duplicate','phase-timeout',
                             'missing','original-omitted','movie','movie-json','movie-final',
                             'assertion-omitted','assertion-failed','summary-failed','assertion-duplicate-key',
                             'head','base','checkout','run','attempt','aggregate'):
                bad = deepcopy(study)
                picture = output/'integration/integration.json'
                pixels = picture.read_bytes()
                if mutation == 'source': bad['sources'][SOURCES[0]] = '0'*64
                if mutation == 'source-omitted': bad['sources'].pop(SOURCES[0])
                if mutation == 'phase-omitted': bad['phases'].pop()
                if mutation == 'phase-duplicate': bad['phases'].append(deepcopy(bad['phases'][-1]))
                if mutation == 'phase': bad['phases'][-1]['exit_code'] = 4
                if mutation == 'phase-timeout': bad['phases'][-1]['timed_out'] = True
                field = {'head':'source_commit','base':'base_commit','checkout':'tested_checkout_commit',
                         'run':'github_run_id','attempt':'github_run_attempt'}.get(mutation)
                if field: bad[field] = 'forged'
                integration = json.loads(original)
                if mutation == 'assertion-omitted': integration['assertions'].pop()
                if mutation == 'assertion-failed': integration['assertions'][0]['passed'] = False
                if mutation == 'summary-failed': integration['passed'] = False
                (output/'integration/integration.json').write_text(json.dumps(integration))
                if mutation == 'assertion-duplicate-key':
                    (output/'integration/integration.json').write_text('{"passed":false,"passed":true,"assertions":[]}')
                if mutation in ('movie','movie-json','movie-final'):
                    forbidden = output/{'movie':'opening.avi','movie-json':'movie.json','movie-final':'movie-final.png'}[mutation]
                    forbidden.write_bytes(b'forbidden recording')
                if mutation in ('missing','original-omitted'): picture.unlink()
                bad['files'] = {r.pop('file'):r for r in bind_files(output,exclude={'report.json'})}
                if mutation == 'missing': bad['files'][picture.relative_to(output).as_posix()] = study['files'][picture.relative_to(output).as_posix()]
                bad['inventory_cost']['bytes'] = sum(r['bytes'] for r in bad['files'].values())
                (output/'report.json').write_text(json.dumps(bad))
                with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                    aggregate = {**bad, 'phases': []} if mutation == 'aggregate' else bad
                    validate_book_lifecycle(dict(book_lifecycle=aggregate),output,identity,host)
                picture.write_bytes(pixels)
                (output/'integration/integration.json').write_bytes(original)
                for filename in ('opening.avi','movie.json','movie-final.png'):
                    (output/filename).unlink(missing_ok=True)

    def test_actual_new_harness_diff_has_no_browser_authorization(self):
        selection = ci_scope.classify(["game/tests/book_windows_observer.gd", "tools/book_lifecycle.py", "tools/p1_product.py"])
        self.assertFalse(selection["selected"]["web"])
        for job in ("product", "production", "preflight", "delivery"):
            self.assertTrue(selection["selected"][job])

    def test_standard_export_accepts_remaining_processes_and_rejects_retired_evidence(self):
        expected = sorted(['current-resource-hashes', 'verified-toolchain-assets', 'current-atlas-resources',
                           'version', 'import', 'player-content-import', 'windows-export', 'player-content-pck'])
        self.assertEqual(checks('export'), expected)
        self.assertEqual(checks('export', 'Windows'), sorted(expected + ['windows-exported-start', 'windows-exported-gui-start']))
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            (directory/'logs').mkdir()
            rows = []
            for name in expected:
                row = dict(name=name, status='success', seconds=.1, exit_code=0)
                if name not in ('current-resource-hashes', 'verified-toolchain-assets', 'current-atlas-resources'):
                    payload = (name+' OK\n').encode()
                    (directory/'logs'/name).write_bytes(payload)
                    row['log'] = dict(file=name, retained_bytes=len(payload), original_bytes=len(payload),
                                      sha256=hashlib.sha256(payload).hexdigest(), abbreviated=False)
                rows.append(row)
            report = dict(checks=rows)
            check_phases(report, expected, directory)
            for name in expected:
                with self.subTest(missing=name), self.assertRaises(ValueError):
                    check_phases(dict(checks=[r for r in rows if r['name'] != name]), expected, directory)
                bad = deepcopy(report)
                next(r for r in bad['checks'] if r['name'] == name)['exit_code'] = 4
                with self.subTest(failed=name), self.assertRaises(ValueError):
                    check_phases(bad, expected, directory)
            with self.assertRaises(ValueError):
                check_phases(dict(checks=rows+[dict(name='regular-book-integration')]), expected, directory)
            with self.assertRaises(ValueError):
                check_phases(dict(report, book_lifecycle={}), expected, directory)
            (directory/'book-lifecycle').mkdir()
            with self.assertRaises(ValueError):
                check_phases(report, expected, directory)

    def test_current_cli_rejects_retired_scopes_and_recording(self):
        root = Path(__file__).resolve().parents[1]
        for flag in ('--write-fixtures','--study-exports','--native-only','--movie','--write-movie','--fixed-fps'):
            result = subprocess.run([sys.executable, str(root/'tools/book_lifecycle.py'),
                                     '--cache-dir','unused','--output-dir','unused',flag],capture_output=True)
            self.assertEqual(result.returncode,2,result.stderr)
        for name in ('book_lifecycle.py','p1_product.py','native_runner.py'):
            source = ast.parse((root/'tools'/name).read_text(encoding='utf-8'))
            literals = {n.value for n in ast.walk(source) if isinstance(n,ast.Constant) and isinstance(n.value,str)}
            self.assertFalse(literals & {'--write-movie','--fixed-fps','--movie','opening.avi',
                                         'movie.json','movie-final.png','book-movie','movie_bytes'})

    def test_windows_reader_uses_regular_export_and_external_test_observer(self):
        import book_windows_probe
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(book_windows_probe.OBSERVER, root/'game/tests/book_windows_observer.gd')
        self.assertTrue(book_windows_probe.OBSERVER.is_file())
        with tempfile.TemporaryDirectory() as temp:
            source, output = Path(temp)/'source', Path(temp)/'output'
            source.mkdir()
            head = 'a'*40
            (source/'report.json').write_text(json.dumps(dict(source_commit=head,
                source_tree_dirty=False,package='B-B-T01')))
            with patch.object(book_windows_probe.platform,'system',return_value='Windows'), \
                    patch.object(book_windows_probe.subprocess,'check_output',side_effect=[head,'']):
                with self.assertRaisesRegex(ValueError,'current regular Windows product export'):
                    book_windows_probe.probe(source,output,head)
            self.assertFalse(output.exists())
