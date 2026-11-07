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

    def test_player_exception_is_diff_bound_and_never_hides_development(self):
        cases = [
            (['README.md', ci.PLAN_PATH], [], False),
            (['docs/workflow/Entwicklungsworkflow_Cheat-Sheet.html'], [], False),
            (['content/authoring/pz-test/r1/package.zip'], [], False),
            (['content/registry.json', 'content/packages/pz-test/r1/manifest.json',
              'game/data/content/test.json', 'game/art/content/test.png', 'docs/CI_POLICY.md', ci.PLAN_PATH], [], False),
            (['content/reveals/pz-test.json'], ['production.images'], False),
            (['README.md'], ['tools'], False),
            (['README.md'], ['native.history'], True),
            (['README.md'], ['preflight'], True),
            (['README.md'], ['delivery'], True),
            (['README.md', 'game/main.gd'], [], True),
            (['content/registry.json', 'tools/puzzle_production/solver.py'], [], True),
            (['.github/workflows/ci-modular.yml'], [], True),
            (['docs/helper.py'], [], True),
            (['examples/rp1/SELECTION.md'], [], True),
            (['game/art/shared.svg'], [], True),
            (['game/data/content/new.gd'], [], True),
            (['unknown'], [], True),
            ([], [], True),
        ]
        for paths, modules, expected in cases:
            for event in ('pull_request', 'push'):
                with self.subTest(paths=paths, modules=modules, event=event):
                    self.assertEqual(ci.player_requirement(paths, modules, event=event)['required'], expected)
        self.assertTrue(ci.player_requirement(['README.md'], [], event='workflow_dispatch')['required'])
        self.assertTrue(ci.player_requirement(['README.md'], [], event='push', nonregular=['README.md'])['required'])

    def test_build_free_content_runs_selected_production_without_player_or_upload(self):
        from types import SimpleNamespace
        for modules in ([], ['production.solver']):
            plan = {'source_head': 'a'*40, 'base_commit': 'b'*40, 'tested_checkout': 'c'*40,
                    'player': {'required': False}, 'run_attempt': '1', 'modules': modules, 'package': package()}
            with self.subTest(modules=modules), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                binding = {'native_groups': [], 'production_groups': ['solver'] if modules else []}
                with patch.object(ci, 'legacy_binding', return_value=binding), \
                     patch.object(ci, 'command') as command, patch.object(ci, 'summary'), \
                     patch.object(ci, 'git', side_effect=['', plan['tested_checkout']]), \
                     patch.dict('sys.modules', {'production_results': SimpleNamespace(
                         files=lambda *args, **kwargs: [], validate_all=lambda *args: None)}), \
                     patch.object(ci, 'copy_file'), \
                     patch.dict(os.environ, {'GITHUB_OUTPUT': str(root/'outputs')}):
                    report = ci.execute(plan, root/'out', root/'cache')
                self.assertTrue(report['accepted'], report['error'])
                self.assertEqual([call.args[1] for call in command.call_args_list], ['production'] if modules else [])
                self.assertEqual(report['player_bytes'], 0)
                self.assertEqual(report['diagnostic_bytes'], 0)
                self.assertFalse((root/'out/player').exists())
                self.assertIn('player=false', (root/'outputs').read_text())

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
            with zipfile.ZipFile(root / 'player.zip', 'w') as archive:
                for name in ['picross-p1.exe', 'picross-p1.console.exe', 'picross-p1.pck',
                             'licenses/NOTICE.txt', 'product-report.json', 'rp6-owner.ps1']:
                    archive.writestr(name, b'content')
            ci.extract_player(root / 'player.zip', root / 'player')
            self.assertTrue((root / 'player/licenses/NOTICE.txt').is_file())
            self.assertFalse((root / 'player/product-report.json').exists())
            self.assertFalse((root / 'player/rp6-owner.ps1').exists())

    def test_source_changed_after_tests_is_failure_even_when_commands_return_zero(self):
        plan = {'source_head': 'a'*40, 'base_commit': 'b'*40, 'tested_checkout': 'c'*40,
                'player': {'required': True}, 'run_attempt': '1', 'modules': [], 'package': package()}
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
                'player': {'required': True}, 'run_attempt': '1', 'modules': ['native.history'], 'package': package()}
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
                'player': {'required': True}, 'run_attempt': '1', 'modules': [], 'package': package()}
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

    def test_soft_goal_does_not_reject_a_clean_successful_run(self):
        plan = {'source_head': 'a'*40, 'base_commit': 'b'*40, 'tested_checkout': 'c'*40,
                'player': {'required': True}, 'run_attempt': '1', 'modules': [], 'package': package()}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def build(*args): (root/'out/player').mkdir(parents=True)
            with patch.object(ci, 'legacy_binding', return_value={'native_groups': [], 'production_groups': []}), \
                 patch.object(ci, 'command', side_effect=build), patch.object(ci, 'summary'), \
                 patch.object(ci, 'git', side_effect=['', plan['tested_checkout']]), \
                 patch.object(ci.threading, 'Timer') as timer, \
                 patch.dict(os.environ, {'GITHUB_OUTPUT': '', 'CI_STARTED_AT': '1'}):
                report = ci.execute(plan, root/'out', root/'cache')
            self.assertTrue(report['accepted'])
            self.assertTrue(report['soft_goal_exceeded'])
            self.assertEqual(timer.call_args.args[0], 0)


class GitBinding(unittest.TestCase):
    def test_real_git_diff_includes_renames_and_nonregular_document_modes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def git(*args):
                return subprocess.check_output(['git', *args], cwd=root, stderr=subprocess.DEVNULL).decode().strip()
            def commit(message):
                git('add', '.'); git('commit', '-qm', message)
                return git('rev-parse', 'HEAD')
            git('init', '-q'); git('config', 'user.name', 'test'); git('config', 'user.email', 'test@example.invalid')
            (root/'.ci').mkdir(); p = package(); p['modules'] = []
            (root/ci.PLAN_PATH).write_text(json.dumps(p))
            (root/'game').mkdir(); (root/'game/main.gd').write_text('extends Node\n')
            base = commit('base')
            p['package'] = 'docs'; (root/ci.PLAN_PATH).write_text(json.dumps(p))
            (root/'README.md').write_text('Documentation\n')
            head = commit('documents')
            for event in ('pull_request', 'push'):
                self.assertFalse(ci.load_plan(base, head, event, root=root)['player']['required'])
            (root/'game/main.gd').rename(root/'game/main.md')
            head = commit('rename code to documentation')
            self.assertTrue(ci.load_plan(base, head, 'pull_request', root=root)['player']['required'])
            base = head
            p['package'] = 'link'; (root/ci.PLAN_PATH).write_text(json.dumps(p))
            # Set Git mode directly: this needs no Windows symlink privilege.
            (root/'README.md').write_text('game/main.md')
            git('add', '.')
            git('update-index', '--cacheinfo', '120000,' + git('hash-object', '-w', 'README.md') + ',README.md')
            git('commit', '-qm', 'document symlink'); head = git('rev-parse', 'HEAD')
            self.assertTrue(ci.load_plan(base, head, 'pull_request', root=root)['player']['required'])

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

