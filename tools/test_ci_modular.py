"""Small permanent contract tests; no engine, browser, network or archived evidence."""
import copy
from datetime import date
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import ci_modular as ci


def package():
    return {'format': ci.FORMAT, 'issue': 'https://github.com/venomenon328/picross/issues/517',
            'package': 'contract-test', 'modules': ['native.history'], 'purpose': 'Save roundtrip',
            'omitted': 'No changed visual or production behavior', 'test_changes': [],
            'core_change': None, 'evidence': {'mode': 'none', 'purpose': None, 'expires': None}}


class PackageContract(unittest.TestCase):
    def validate(self, value, paths=()):
        return ci.validate_package(value, paths, repository='venomenon328/picross', today=date(2026, 11, 5))

    def test_empty_modules_are_a_valid_explicit_core_only_decision(self):
        p = package(); p['modules'] = []
        self.assertEqual(self.validate(p)['modules'], [])

    def test_unknown_duplicate_and_nonlist_modules_are_rejected(self):
        for modules in [['native.typo'], ['tools', 'tools'], 'tools', [True]]:
            p = package(); p['modules'] = modules
            with self.subTest(modules=modules), self.assertRaises(ValueError):
                self.validate(p)

    def test_schema_repository_and_duplicate_keys_are_not_trusted(self):
        for change in [{'format': 'development-ci-plan/v2'}, {'issue': 'https://github.com/other/repo/issues/1'}, {'extra': True}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.validate({**package(), **change})
        with self.assertRaises(ValueError):
            ci.strict_json('{"modules":[],"modules":["tools"]}')

    def test_core_growth_and_test_changes_need_a_decision(self):
        p = package()
        with self.assertRaisesRegex(ValueError, 'core change'):
            self.validate(p, ['tools/ci_modular.py'])
        p['core_change'] = 'A small package contract guard replaces automatic full selection'
        self.validate(p, ['tools/ci_modular.py'])
        with self.assertRaisesRegex(ValueError, 'lifecycle'):
            self.validate(p, ['tools/test_example.py'])
        p['test_changes'] = [{'path': 'tools/test_example.py', 'disposition': 'temporary', 'reason': 'Remove after this feature review'}]
        self.validate(p, ['tools/test_example.py'])

    def test_evidence_has_an_actual_purpose_and_expiry_not_a_byte_limit(self):
        p = package()
        for value in [{'mode': 'review', 'purpose': '', 'expires': '2026-11-12'},
                      {'mode': 'review', 'purpose': 'R01', 'expires': '2026-11-05'},
                      {'mode': 'forever', 'purpose': 'R01', 'expires': None}]:
            p['evidence'] = value
            with self.subTest(value=value), self.assertRaises(ValueError): self.validate(p)
        p['evidence'] = {'mode': 'review', 'purpose': 'R01 reviewer for this implementation', 'expires': '2026-11-12'}
        self.validate(p)

    def test_review_failure_and_expired_upload_selection(self):
        evidence = {'mode': 'failure', 'purpose': 'Failure investigation', 'expires': '2026-11-12'}
        self.assertFalse(ci.retain_evidence(evidence, True, today=date(2026, 11, 5)))
        self.assertTrue(ci.retain_evidence(evidence, False, today=date(2026, 11, 5)))
        self.assertFalse(ci.retain_evidence(evidence, False, today=date(2026, 11, 12)))
        self.assertFalse(ci.retain_evidence(package()['evidence'], False))

    def test_player_extraction_rejects_traversal_and_incomplete_exports(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for member in ['../escape', 'picross-p1.exe']:
                with zipfile.ZipFile(root / 'player.zip', 'w') as archive: archive.writestr(member, b'content')
                with self.assertRaises(ValueError): ci.extract_player(root / 'player.zip', root / 'player')
            self.assertFalse((root / 'escape').exists())

    def test_source_changed_after_tests_is_failure_even_when_commands_return_zero(self):
        plan = {'source_head': 'a'*40, 'base_commit': 'b'*40, 'tested_checkout': 'c'*40,
                'run_attempt': '1', 'modules': [], 'package': package()}
        with tempfile.TemporaryDirectory() as directory:
            def build(args, name, work, rows):
                (Path(directory) / 'out/player').mkdir(parents=True)
            with patch.object(ci, 'legacy_binding', return_value={'native_groups': [], 'production_groups': []}), \
                 patch.object(ci, 'command', side_effect=build), patch.object(ci, 'git', return_value='dirty'), \
                 patch.object(ci, 'summary'), patch.dict(os.environ, {'GITHUB_OUTPUT': ''}):
                report = ci.execute(plan, Path(directory)/'out', Path(directory)/'cache')
            self.assertFalse(report['accepted'])
            self.assertIn('sources changed', report['error'])
            self.assertFalse(list(Path(directory).glob('picross-ci-*')))
            self.assertFalse((Path(directory)/'out/diagnostics').exists())

    def test_native_reader_failure_cannot_be_relabelled_as_success(self):
        plan = {'source_head': 'a'*40, 'base_commit': 'b'*40, 'tested_checkout': 'c'*40,
                'run_attempt': '1', 'modules': ['native.history'], 'package': package()}
        from types import SimpleNamespace
        def reject(*args): raise ValueError('Missing original save trace')
        with tempfile.TemporaryDirectory() as directory:
            def run(args, name, work, rows):
                (Path(directory)/'out/player').mkdir(parents=True, exist_ok=True)
            with patch.object(ci, 'legacy_binding', return_value={'native_groups': ['history'], 'production_groups': []}), \
                 patch.object(ci, 'command', side_effect=run), patch.object(ci, 'summary'), \
                 patch.dict('sys.modules', {'native_results': SimpleNamespace(validate_all=reject)}), \
                 patch.dict(os.environ, {'GITHUB_OUTPUT': ''}):
                report = ci.execute(plan, Path(directory)/'out', Path(directory)/'cache')
            self.assertFalse(report['accepted'])
            self.assertEqual(report['error'], 'Missing original save trace')

    def test_failed_build_never_publishes_a_partial_player(self):
        plan = {'source_head': 'a'*40, 'base_commit': 'b'*40, 'tested_checkout': 'c'*40,
                'run_attempt': '1', 'modules': [], 'package': package()}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def fail(*args):
                (root/'out/player').mkdir(parents=True)
                (root/'out/player/picross-p1.exe').write_bytes(b'partial')
                raise ValueError('Build interrupted')
            with patch.object(ci, 'legacy_binding', return_value={'native_groups': [], 'production_groups': []}), \
                 patch.object(ci, 'command', side_effect=fail), patch.object(ci, 'summary'), \
                 patch.dict(os.environ, {'GITHUB_OUTPUT': str(root/'outputs')}):
                report = ci.execute(plan, root/'out', root/'cache')
            self.assertFalse(report['accepted'])
            self.assertIn('player=false', (root/'outputs').read_text())


class GitBinding(unittest.TestCase):
    def test_inherited_plan_fails_new_plan_passes_main_does_not_replay_it(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def git(*args):
                return subprocess.check_output(['git', *args], cwd=root, stderr=subprocess.DEVNULL).decode().strip()
            git('init', '-q'); git('config', 'user.name', 'test'); git('config', 'user.email', 'test@example.invalid')
            (root/'.ci').mkdir(); (root/ci.PLAN_PATH).write_text(json.dumps(package()))
            git('add', '.'); git('commit', '-qm', 'base'); base = git('rev-parse', 'HEAD')
            (root/'readme.md').write_text('A new package'); git('add', '.'); git('commit', '-qm', 'change')
            head = git('rev-parse', 'HEAD')
            with self.assertRaisesRegex(ValueError, 'Inherited'):
                ci.load_plan(base, head, 'pull_request', root=root)
            p = package(); p['package'] = 'new-package'
            (root/ci.PLAN_PATH).write_text(json.dumps(p)); git('add', '.'); git('commit', '-qm', 'plan')
            head = git('rev-parse', 'HEAD')
            self.assertEqual(ci.load_plan(base, head, 'pull_request', root=root)['modules'], ['native.history'])
            self.assertEqual(ci.load_plan(base, head, 'push', root=root)['modules'], [])
            self.assertEqual(ci.load_plan(base, head, 'workflow_dispatch', modules='tools', root=root)['modules'], ['tools'])
            with self.assertRaises(ValueError): ci.load_plan(base, head, 'push', modules='tools', root=root)


if __name__ == '__main__':
    unittest.main()
