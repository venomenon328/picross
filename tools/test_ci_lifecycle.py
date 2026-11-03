"""Cheap lifecycle counterexamples at the real diff, reader and workflow boundaries."""
from copy import deepcopy
from datetime import date
from io import BytesIO
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from ci_lifecycle import (FORMAT, MANIFEST, REPO, cost, digest, fingerprint, guarded,
                          executable_anchor, is_feature_open, owner_decision, strict_json, validate)
from ci_scope import classify

TODAY = date(2026, 11, 3)
FEATURE = REPO + 'issues/999999'
SOURCE = 'tools/test_current.py'
READER = '.github/workflows/check.yml'


def selection(paths):
    value = classify(paths)
    return {k: value[k] for k in ('selected', 'native_groups', 'production_groups', 'browser_request')}


def fixture(kind='permanent-small', path=SOURCE):
    blobs = {path: b'assert 2 + 2 == 4\n', READER: b"on:\n  pull_request:\njobs:\n  check:\n    run: python3 -m unittest discover -s tools -p 'test_*.py'\n"}
    after = {p: 'a' * 40 for p in blobs}
    record = dict(id='current', kind=kind, purpose='Current exact state regression',
                  level='small deterministic Python oracle', feature=FEATURE, owner='venomenon328',
                  sources={path: {'before': None, 'after': after[path]}},
                  readers=[dict(path=READER, anchor="python3 -m unittest discover -s tools -p 'test_*.py'", sources=[path])],
                  selection=selection([path]), cost=dict(cpu_seconds=0.1, wall_seconds=0.2, files=0, bytes=0, pngs=0),
                  coverage='Fixed synthetic state; no engine, render, process matrix or production replay',
                  expires=None if kind == 'permanent-small' else '2026-11-10',
                  retire_when=None if kind == 'permanent-small' else 'feature-closeout-or-deadline', owner_decision=None)
    manifest = dict(format=FORMAT, records=[record], closeout=dict(feature=FEATURE, status='in-progress',
                    added='One current small regression', removed='None',
                    temporary=['current'] if kind == 'temporary' else [], cost_change='Measured in T01'))
    before = {READER: after[READER]}
    return before, after, blobs, manifest


class LifecycleTests(unittest.TestCase):
    def check(self, data, *, old=None, decision=None, opened=True, today=TODAY):
        before, after, blobs, manifest = data
        return validate(before, after, old, manifest, blobs.__getitem__, today=today,
                        decision=decision or owner_decision, feature_open=lambda _: opened)

    def test_small_current_regression_and_bounded_introduction_are_accepted(self):
        self.assertTrue(self.check(fixture())['accepted'])
        value = self.check(fixture('temporary'))
        self.assertEqual(value['records'][0]['expires'], '2026-11-10')
        self.assertEqual(value['changed_surfaces'], [SOURCE])
        self.assertEqual(value['records'][0]['readers'][0]['sha256'], digest(fixture()[2][READER]))

    def test_missing_classification_catches_film_generator_jobs_and_renamed_outputs(self):
        for path in ('tools/film.py', 'game/tests/new_render.gd', 'misc/comparison.machine',
                     'new/location/result.dat', 'docs/gallery/pixels.bin', '.github/workflows/optional.yml'):
            data = fixture()
            data[1][path] = 'b' * 40
            data[2][path] = b'new source or output'
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'Unclassified'):
                self.check(data)
        # Modifying the existing real runner/upload/manifest is equally covered.
        for path in ('tools/p1_product.py', 'tools/native_artifacts.json', 'tools/production_ci.py', READER):
            data = fixture()
            data[0][path] = 'c' * 40
            data[1][path] = 'd' * 40
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'Unclassified'):
                self.check(data)

    def test_missing_deadline_and_feature_binding_fail_closed(self):
        for field, value in (('expires', None), ('expires', 'soon'), ('expires', '2026-11-03'),
                             ('expires', '2026-11-02'), ('retire_when', None), ('feature', '#999999')):
            data = fixture('temporary'); data[3]['records'][0][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                self.check(data)
        with self.assertRaisesRegex(ValueError, 'Expired'):
            self.check(fixture('temporary'), today=date(2026, 11, 10))

    def test_feature_completion_cannot_keep_a_temporary_standard_check(self):
        data = fixture('temporary'); data[3]['closeout']['status'] = 'complete'
        with self.assertRaisesRegex(ValueError, 'Feature complete'):
            self.check(data)
        with self.assertRaisesRegex(ValueError, 'Feature complete'):
            self.check(fixture('temporary'), opened=False)
        data = fixture('temporary'); data[3]['closeout']['temporary'] = []
        with self.assertRaisesRegex(ValueError, 'hides temporary'):
            self.check(data)

    def test_retirement_removes_sources_and_record_without_deleting_existing_regressions(self):
        before, after, blobs, manifest = fixture('temporary')
        old = deepcopy(manifest)
        before.update(after)
        del after[SOURCE]
        manifest['records'] = []
        manifest['closeout'].update(status='complete', temporary=[], removed='Temporary introduction removed')
        # Explicit deletion delta still needs its small source/reader accounting.
        removed = deepcopy(old['records'][0])
        removed.update(id='retirement', kind='permanent-small', expires=None, retire_when=None, readers=[])
        removed['sources'][SOURCE] = {'before': before[SOURCE], 'after': None}
        manifest['records'] = [removed]
        self.assertTrue(self.check((before, after, blobs, manifest), old=old)['accepted'])

    def test_relabel_rename_or_deadline_extension_needs_exact_owner_decision(self):
        for action in ('extend', 'relabel', 'rename', 'feature', 'owner'):
            data = fixture('temporary'); old = deepcopy(data[3]); record = data[3]['records'][0]
            if action == 'extend': record['expires'] = '2026-11-11'
            elif action == 'rename': record['id'] = 'different'; data[3]['closeout']['temporary'] = ['different']
            elif action == 'feature': record['feature'] = REPO + 'issues/999998'
            elif action == 'owner': record['owner'] = 'other package'
            else:
                record.update(kind='permanent-small', expires=None, retire_when=None)
                data[3]['closeout']['temporary'] = []
            with self.subTest(action=action), self.assertRaises(ValueError):
                self.check(data, old=old)

    def test_heavy_current_exception_requires_owner_and_finite_review(self):
        data = fixture('permanent-heavy'); record = data[3]['records'][0]
        record['cost'].update(cpu_seconds=100, wall_seconds=60, files=300, bytes=90000000, pngs=100)
        with self.assertRaisesRegex(ValueError, 'owner decision'):
            self.check(data)
        approved = []
        self.assertTrue(self.check(data, decision=lambda r: approved.append(fingerprint(r)))['accepted'])
        self.assertEqual(approved, [fingerprint(record)])
        record['expires'] = None
        with self.assertRaisesRegex(ValueError, 'deadline'):
            self.check(data, decision=lambda _: None)

    def test_small_label_does_not_allow_png_gallery_or_large_estimated_costs(self):
        for field, value in (('pngs', 1), ('files', 300), ('bytes', 90000000), ('cpu_seconds', 60), ('wall_seconds', 60)):
            data = fixture(); data[3]['records'][0]['cost'][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'Small regression'):
                self.check(data)
        for value in ({}, dict(cpu_seconds=True, wall_seconds=0, files=0, bytes=0, pngs=0),
                      dict(cpu_seconds=float('nan'), wall_seconds=0, files=0, bytes=0, pngs=0)):
            with self.assertRaises(ValueError): cost(value)

    def test_delta_both_rename_sides_and_exact_reader_are_bound(self):
        for field in ('before', 'after'):
            data = fixture(); data[3]['records'][0]['sources'][SOURCE][field] = 'f' * 40
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'Stale'):
                self.check(data)
        for mutation in ('anchor', 'source', 'missing', 'selection'):
            data = fixture(); record = data[3]['records'][0]
            if mutation == 'anchor': record['readers'][0]['anchor'] = 'optional imaginary reader'
            elif mutation == 'source': record['readers'][0]['sources'] = ['other.py']
            elif mutation == 'missing': record['readers'] = []
            else: record['selection']['selected']['web'] = True
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): self.check(data)
        data = fixture(); data[1]['elsewhere/current.py'] = data[1].pop(SOURCE)
        with self.assertRaises(ValueError): self.check(data)

    def test_untouched_baseline_negative_fixtures_and_history_are_not_name_banned(self):
        data = fixture()
        for path in ('old/movie.avi', 'game/tests/old_render.gd', 'docs/BOOK_STUDY.md'):
            data[0][path] = data[1][path] = 'e' * 40
        data[2][SOURCE] += b"negative_fixture = '--write-movie gallery.png'\n"
        self.assertTrue(self.check(data)['accepted'])
        self.assertFalse(guarded('content/authoring/pz-synthetic/r01/package.zip', added=True))
        self.assertFalse(guarded('docs/history.md', added=True))

    def test_duplicate_json_keys_and_duplicate_classification_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            strict_json('{"records": [], "records": []}')
        data = fixture(); data[3]['records'].append(deepcopy(data[3]['records'][0]))
        with self.assertRaisesRegex(ValueError, 'Duplicate'): self.check(data)

    def test_reader_prose_comments_and_negative_strings_are_not_executable_entrypoints(self):
        self.assertFalse(executable_anchor('docs/old.md', b'python3 tools/new.py', 'tools/new.py'))
        self.assertFalse(executable_anchor('tools/reader.py', b"fixture = 'tools/new.py'\n", 'tools/new.py'))
        self.assertFalse(executable_anchor('tools/reader.py', b"print('tools/new.py')\n", 'tools/new.py'))
        self.assertTrue(executable_anchor('tools/reader.py', b"Path('tools/new.py').read_text()\n", 'tools/new.py'))
        self.assertTrue(executable_anchor('tools/reader.py', b'import new\n', 'import new'))
        self.assertFalse(executable_anchor(READER, b'# run: python3 tools/new.py\n', 'tools/new.py'))
        self.assertFalse(executable_anchor(READER, b'name: python3 tools/new.py\n', 'tools/new.py'))
        self.assertTrue(executable_anchor(READER, b'    run: |\n      python3 tools/new.py\n', 'tools/new.py'))

    def test_owner_comment_binds_identity_source_cost_and_expiry(self):
        record = fixture('permanent-heavy')[3]['records'][0]
        url = REPO + 'issues/999999#issuecomment-123'
        record['owner_decision'] = url
        comment = dict(user=dict(login='venomenon328'), html_url=url, body='CI-LIFECYCLE-APPROVE ' + fingerprint(record))
        with patch('ci_lifecycle.api', return_value=comment):
            owner_decision(record)
            for field in ('cost', 'expires', 'sources'):
                changed = deepcopy(record)
                changed[field] = {'cpu_seconds': 999} if field == 'cost' else 'changed'
                with self.subTest(field=field), self.assertRaises(ValueError): owner_decision(changed)
        with patch('ci_lifecycle.api', return_value={**comment, 'user': {'login': 'someone-else'}}), self.assertRaises(ValueError):
            owner_decision(record)
        with patch('ci_lifecycle.api', return_value={**comment, 'body': '> ' + comment['body']}), self.assertRaises(ValueError):
            owner_decision(record)
        with patch('ci_lifecycle.api', return_value={'state': 'closed'}):
            self.assertFalse(is_feature_open(FEATURE))

    def test_workflow_runs_guard_before_tool_tests_with_exact_diff_and_retains_browser_gate(self):
        workflow = Path(__file__).parents[1].joinpath('.github/workflows/ci-chromium.yml').read_text(encoding='utf-8')
        block = workflow.split('      - name: Enforce test lifecycle and feature closeout\n')[1].split('      - name:')[0]
        self.assertIn("if: steps.scope.outputs.content_only != 'true'", block)
        self.assertIn('--base "$CI_BASE" --head "$CI_HEAD"', block)
        self.assertNotIn('continue-on-error', block)
        self.assertLess(workflow.index('Enforce test lifecycle'), workflow.index('Fast tool contracts'))
        self.assertIn('${{ runner.temp }}/ci-lifecycle.json', workflow)
        selected = classify(['tools/ci_lifecycle.py', MANIFEST, '.github/workflows/ci-chromium.yml'])
        self.assertTrue(all(value for key, value in selected['selected'].items() if key != 'web'))
        self.assertFalse(selected['selected']['web'])
        self.assertIsNone(selected['browser_request'])

    def test_real_git_cli_fails_for_unclassified_new_machine_without_running_it(self):
        with tempfile.TemporaryDirectory() as directory:
            def git(*args):
                return subprocess.check_output(['git', '-C', directory, *args], stderr=subprocess.DEVNULL).decode().strip()
            def write(path, raw):
                output = Path(directory, path); output.parent.mkdir(parents=True, exist_ok=True); output.write_bytes(raw)
            def commit():
                git('add', '.'); git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'synthetic')
                return git('rev-parse', 'HEAD')
            git('init', '-q')
            before, after, blobs, manifest = fixture()
            write(READER, blobs[READER]); base = commit()
            write(SOURCE, blobs[SOURCE]); after[SOURCE] = git('hash-object', SOURCE)
            manifest['records'][0]['sources'][SOURCE]['after'] = after[SOURCE]
            write(MANIFEST, (json.dumps(manifest) + '\n').encode()); head = commit()
            command = [sys.executable, str(Path(__file__).with_name('ci_lifecycle.py').resolve()), '--base', base, '--head', head,
                       '--output', str(Path(directory, '.git', 'report.json'))]
            result = subprocess.run(command, cwd=directory, capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(Path(directory, '.git', 'report.json').read_text())
            self.assertEqual(report['source_head'], head); self.assertEqual(report['base_commit'], base)
            write('different/optional.machine', b'NEVER EXECUTE THIS GENERATOR\n'); head = commit()
            command[command.index('--head') + 1] = head
            result = subprocess.run(command, cwd=directory, capture_output=True, text=True, timeout=15)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Unclassified', result.stderr)
            self.assertIn('different/optional.machine', result.stderr)
