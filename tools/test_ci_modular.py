"""Small permanent contract tests; no engine, browser, network or archived evidence."""
import copy
from datetime import date
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch
import zipfile

import ci_modular as ci


BACKGROUND_PATHS = ('content/backgrounds/pz-synthetic.json',
                    'game/art/backgrounds/pz-synthetic.png',
                    'game/art/backgrounds/pz-synthetic.txt')


def package():
    return {'format': ci.FORMAT, 'issue': 'https://github.com/venomenon328/picross/issues/517',
            'package': 'contract-test', 'modules': ['native.history'], 'purpose': 'Save roundtrip',
            'omitted': 'No changed visual or production behavior', 'test_changes': [],
            'core_change': None, 'evidence': {'mode': 'none', 'purpose': None, 'expires': None}}


class PackageContract(unittest.TestCase):
    def test_execution_parts_cover_exact_selection_and_reuse_export_player(self):
        plan = {'modules': ['production.catalog', 'tools', 'native.core'],
                'player': {'required': True, 'reason': 'Code change'}}
        parts = ci.execution_parts(plan)
        self.assertEqual(parts, ['player', 'tools', 'native.core', 'production.catalog'])
        original = copy.deepcopy(plan)
        for part in parts:
            selected = ci.execution_plan(plan, part)
            self.assertEqual(selected['modules'], [] if part == 'player' else [part])
            self.assertEqual(selected['player']['required'], part == 'player')
        self.assertEqual(plan, original)
        for part in ('source', 'native.graphics', 'production.images', '', 'tools,production.catalog'):
            with self.assertRaises(ValueError): ci.execution_plan(plan, part)
        plan['modules'].append('native.export')
        self.assertNotIn('player', ci.execution_parts(plan))
        self.assertTrue(ci.execution_plan(plan, 'native.export')['player']['required'])
        self.assertEqual(ci.execution_parts({'modules': [], 'player': {'required': False}}), ['source'])
        with self.assertRaises(ValueError):
            ci.execution_parts({'modules': ['tools', 'tools'], 'player': {'required': False}})

    def validate(self, value, paths=()):
        return ci.validate_package(value, paths, repository='venomenon328/picross', today=date(2026, 11, 5))

    def test_part_executes_only_its_work_but_reports_the_original_full_binding(self):
        plan = {'source_head': 'a'*40, 'base_commit': 'b'*40, 'tested_checkout': 'c'*40,
                'run_attempt': '1', 'modules': ['tools', 'production.catalog'],
                'player': {'required': False}, 'package': package()}
        for failing in (False, True):
            with self.subTest(failing=failing), tempfile.TemporaryDirectory() as directory:
                with patch.object(ci, 'command', side_effect=ValueError('actual module failure') if failing else None) as command, \
                     patch.object(ci, 'summary'), patch.object(ci, 'git', side_effect=['', 'c'*40]), \
                     patch.dict(os.environ, {'GITHUB_OUTPUT': ''}):
                    report = ci.execute(plan, Path(directory)/'output', Path(directory)/'cache', part='tools')
                self.assertEqual(report['accepted'], not failing)
                self.assertEqual([call.args[1] for call in command.call_args_list], ['tools'])
                self.assertEqual(report['binding'], plan)
                self.assertEqual(report['execution']['modules'], ['tools'])

    def test_empty_modules_are_a_valid_explicit_core_only_decision(self):
        p = package(); p['modules'] = []
        self.assertEqual(self.validate(p)['modules'], [])

    def test_core_paths_are_repository_relative_posix_paths_on_this_platform(self):
        self.assertIn('tools/ci_modular.py', ci.CORE_PATHS)
        for path in ci.CORE_PATHS:
            with self.subTest(path=path):
                self.assertFalse(Path(path).is_absolute())
                self.assertNotIn('\\', path)
                self.assertTrue((ci.ROOT / path).is_file())

    def test_current_view_exception_is_exact_and_never_hides_development(self):
        valid = [f'content/authoring/{identity}/current-view.json'
                 for identity in ('pz-synthetic', 'pz-0', 'pz-' + 'a' * 60)]
        invalid = [
            'content/authoring/pz-synthetic/Current-view.json',
            'content/authoring/pz-synthetic/current-view.JSON',
            'content/authoring/pz-Synthetic/current-view.json',
            'content/authoring/PZ-synthetic/current-view.json',
            'content/authoring/pz-/current-view.json',
            'content/authoring/pz-' + 'a' * 61 + '/current-view.json',
            'content/authoring/pz-bad_id/current-view.json',
            'content/authoring/current-view.json',
            'content/authoring//current-view.json',
            'content/authoring/pz-synthetic/current-view.txt',
            'content/authoring/pz-synthetic/current-view.json.py',
            'content/authoring/pz-synthetic/current-view.json/',
            'content/authoring/pz-synthetic/r01/current-view.json',
            'content/authoring/pz-synthetic/current-view.json/extra.json',
            'content/authoring/pz-synthetic/../current-view.json',
            'content/authoring/pz-synthetic/./current-view.json',
            'content/authoring//pz-synthetic/current-view.json',
            r'content/authoring/pz-synthetic\current-view.json',
            'content/packages/pz-synthetic/current-view.json',
            'content/authoring/pz-synthetic/unknown.json',
        ]
        for path in valid + invalid:
            with self.subTest(path=path):
                self.assertEqual(ci.content_path(path), path in valid)
                for event in ('pull_request', 'push'):
                    self.assertEqual(ci.player_requirement([path, ci.PLAN_PATH], [], event=event)['required'],
                                     path in invalid)
        pointer = valid[0]
        for path in ('tools/ci_modular.py', 'tools/ci_paths.py', 'tools/helper.py',
                     '.github/workflows/ci-modular.yml', 'game/main.gd'):
            for event in ('pull_request', 'push'):
                with self.subTest(path=path, event=event):
                    self.assertTrue(ci.player_requirement([pointer, path], [], event=event)['required'])
        for modules in (['native.core'], ['preflight'], ['delivery']):
            self.assertTrue(ci.player_requirement([pointer], modules, event='pull_request')['required'])
        self.assertTrue(ci.player_requirement([pointer], [], event='workflow_dispatch')['required'])
        self.assertTrue(ci.player_requirement([pointer], [], event='push', nonregular=[pointer])['required'])

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
        cases += [([path], [], False) for path in BACKGROUND_PATHS]
        cases += [(list(BACKGROUND_PATHS), modules, False)
                  for modules in ([], ['tools'], ['production.images'])]
        cases += [([f'{prefix}/{identity}.{suffix}'], [], False)
                  for prefix, suffix in (('content/backgrounds', 'json'), ('game/art/backgrounds', 'png'),
                                         ('game/art/backgrounds', 'txt'))
                  for identity in ('pz-0', 'pz-' + 'a' * 60)]
        cases += [(list(BACKGROUND_PATHS), [module], True)
                  for module in ('preflight', 'delivery', *(f'native.{group}' for group in ci.NATIVE))]
        cases += [(list(BACKGROUND_PATHS) + [path], [], True) for path in (
            'content/backgrounds/pz-.json', 'content/backgrounds/pz-Upper.json',
            'content/backgrounds/pz-bad_id.json', 'content/backgrounds/pz-' + 'a' * 61 + '.json',
            'content/backgrounds/pz-synthetic/record.json', 'content/backgrounds/../pz-synthetic.json',
            'content/backgrounds/pz-synthetic.json/', 'content/backgrounds/pz-synthetic.json.py',
            'content/backgrounds/pz-synthetic.JSON', 'content/backgrounds/pz-synthetic.png',
            'game/art/backgrounds/pz-synthetic.json', 'game/art/backgrounds/pz-synthetic.PNG',
            'game/art/backgrounds/pz-synthetic.png.import', 'game/art/backgrounds/pz-synthetic.gdshader',
            'game/art/backgrounds/loader.gd', 'game/data/background-capability.json',
            'game/art/backgrounds/shared.png', 'game/art/book/paper.png',
            'tools/ci_paths.py', 'tools/puzzle_production/solver.py',
            '.github/workflows/ci-modular.yml', 'game/main.gd', 'unknown.json')]
        for paths, modules, expected in cases:
            for event in ('pull_request', 'push'):
                with self.subTest(paths=paths, modules=modules, event=event):
                    self.assertEqual(ci.player_requirement(paths, modules, event=event)['required'], expected)
        self.assertTrue(ci.player_requirement(['README.md'], [], event='workflow_dispatch')['required'])
        self.assertTrue(ci.player_requirement(['README.md'], [], event='push', nonregular=['README.md'])['required'])
        self.assertTrue(ci.player_requirement(BACKGROUND_PATHS, [], event='workflow_dispatch')['required'])

    def test_build_free_content_runs_selected_production_without_player_or_upload(self):
        from types import SimpleNamespace
        for modules in ([], ['production.solver']):
            plan = {'source_head': 'a'*40, 'base_commit': 'b'*40, 'tested_checkout': 'c'*40,
                    'player': ci.player_requirement(BACKGROUND_PATHS, modules, event='pull_request'),
                    'run_attempt': '1', 'modules': modules, 'package': package()}
            self.assertFalse(plan['player']['required'])
            with self.subTest(modules=modules), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                binding = {'native_groups': [], 'production_groups': ['solver'] if modules else []}
                validate = Mock()
                with patch.object(ci, 'legacy_binding', return_value=binding), \
                     patch.object(ci, 'command') as command, patch.object(ci, 'summary'), \
                     patch.object(ci, 'git', side_effect=['', plan['tested_checkout']]), \
                     patch.dict('sys.modules', {'production_results': SimpleNamespace(
                         files=lambda *args, **kwargs: [], validate_all=validate)}), \
                     patch.object(ci, 'copy_file'), \
                     patch.dict(os.environ, {'GITHUB_OUTPUT': str(root/'outputs')}):
                    report = ci.execute(plan, root/'out', root/'cache')
                self.assertTrue(report['accepted'], report['error'])
                self.assertEqual([call.args[1] for call in command.call_args_list], ['production'] if modules else [])
                self.assertEqual(report['player_bytes'], 0)
                self.assertEqual(report['diagnostic_bytes'], 0)
                self.assertFalse((root/'out/player').exists())
                self.assertFalse((root/'cache').exists())
                self.assertIn('player=false', (root/'outputs').read_text())
                self.assertIn('diagnostics=false', (root/'outputs').read_text())
                if modules:
                    validate.assert_called_once()
                else:
                    validate.assert_not_called()

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
        for path in ('tools/ci_modular.py', 'tools/ci_paths.py'):
            for reason in (None, '', '   '):
                p['core_change'] = reason
                with self.subTest(path=path, reason=reason), self.assertRaisesRegex(ValueError, 'core change'):
                    self.validate(p, [path])
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
    def test_current_view_production_diff_is_build_free_for_pr_and_main_push(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def git(*args):
                return subprocess.check_output(['git', *args], cwd=root, stderr=subprocess.DEVNULL).decode().strip()
            def commit(message):
                git('add', '.'); git('commit', '-qm', message)
                return git('rev-parse', 'HEAD')
            git('init', '-q'); git('config', 'user.name', 'test'); git('config', 'user.email', 'test@example.invalid')
            (root/'.ci').mkdir(); (root/ci.PLAN_PATH).write_text(json.dumps(package()))
            base = commit('base')
            p = package(); p['package'] = 'synthetic-content'; p['modules'] = []
            (root/ci.PLAN_PATH).write_text(json.dumps(p))
            pointer = 'content/authoring/pz-synthetic/current-view.json'
            for path in (pointer, 'content/authoring/index.json',
                         'content/authoring/pz-synthetic/r01/record.json',
                         'content/authoring/pz-synthetic/r01/workspace.json',
                         'content/authoring/pz-synthetic/r01/package.zip'):
                target = root/path; target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(b'synthetic path classification only\n')
            head = commit('production and package plan')
            for event in ('pull_request', 'push'):
                plan = ci.load_plan(base, head, event, root=root)
                self.assertEqual(plan['modules'], [])
                self.assertFalse(plan['player']['required'])
            # All nonregular Git modes stay build-required without OS symlink privileges.
            blob = git('hash-object', '-w', pointer)
            for mode in ('100755', '120000', '160000'):
                oid = head if mode == '160000' else blob
                git('update-index', '--cacheinfo', f'{mode},{oid},{pointer}')
                git('commit', '-qm', 'synthetic nonregular mode')
                changed = git('rev-parse', 'HEAD')
                for event in ('pull_request', 'push'):
                    with self.subTest(mode=mode, event=event):
                        self.assertTrue(ci.load_plan(base, changed, event, root=root)['player']['required'])

    def test_background_production_diff_is_build_free_for_pr_and_main_push(self):
        # CI-PB-T01: real Git metadata, synthetic bytes; no puzzle corpus or engine.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            p = package(); p['modules'] = ['production.solver']
            def git(*args):
                return subprocess.check_output(['git', *args], cwd=root, stderr=subprocess.DEVNULL).decode().strip()
            def commit(message, *, stage_all=True):
                p['package'] = message
                (root/ci.PLAN_PATH).write_text(json.dumps(p))
                git('add', '.' if stage_all else ci.PLAN_PATH)
                git('commit', '-qm', message)
                return git('rev-parse', 'HEAD')
            def assert_player(base, head, required):
                for event in ('pull_request', 'push'):
                    with self.subTest(base=base, head=head, event=event):
                        plan = ci.load_plan(base, head, event, root=root)
                        self.assertEqual(plan['player']['required'], required)
                        self.assertEqual(plan['modules'], ['production.solver'] if event == 'pull_request' else [])
            git('init', '-q'); git('config', 'user.name', 'test'); git('config', 'user.email', 'test@example.invalid')
            (root/'.ci').mkdir()
            base = commit('base')
            for path in (*BACKGROUND_PATHS, 'content/registry.json', 'content/authoring/index.json',
                         'content/authoring/pz-synthetic/current-view.json',
                         'content/authoring/pz-synthetic/r01/record.json',
                         'content/packages/pz-synthetic/r01/package.zip',
                         'content/reveals/pz-synthetic.json', 'content/added/pz-synthetic.json',
                         'content/difficulty/pz-synthetic/rating.json',
                         'content/difficulty/reports/synthetic/report.json',
                         'game/data/registry.json', 'game/data/content/synthetic.json',
                         'game/art/content/synthetic.png'):
                target = root/path; target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text('synthetic path classification: ' + path + '\n')
            head = commit('add production including backgrounds'); assert_player(base, head, False)
            base = head
            for path in BACKGROUND_PATHS:
                (root/path).write_text('changed synthetic background: ' + path + '\n')
            head = commit('change backgrounds'); assert_player(base, head, False)
            # Both sides of each rename must remain visible, including a source
            # renamed to inert content and the reverse direction.
            source = BACKGROUND_PATHS[1]
            renamed = 'game/art/backgrounds/pz-renamed.png'
            code = 'game/ui/background_loader.gd'
            for old, new, required in ((source, renamed, False), (renamed, code, True), (code, renamed, True)):
                (root/new).parent.mkdir(parents=True, exist_ok=True)
                (root/old).rename(root/new)
                base = head; head = commit('rename ' + old + ' to ' + new)
                paths, _ = ci.changed_metadata(base, head, root=root)
                self.assertTrue({old, new}.issubset(paths))
                assert_player(base, head, required)
            for path in (BACKGROUND_PATHS[0], renamed, BACKGROUND_PATHS[2]):
                (root/path).unlink()
            base = head; head = commit('remove backgrounds'); assert_player(base, head, False)
            source = BACKGROUND_PATHS[0]
            (root/source).write_text('synthetic background\n')
            base = head; head = commit('restore source'); assert_player(base, head, False)
            blob = git('hash-object', '-w', source)
            for mode in ('100755', '120000', '160000'):
                oid = head if mode == '160000' else blob
                git('update-index', '--cacheinfo', f'{mode},{oid},{source}')
                base = head; head = commit('nonregular ' + mode, stage_all=False)
                assert_player(base, head, True)
                git('update-index', '--force-remove', source)
                base = head; head = commit('remove nonregular ' + mode, stage_all=False)
                assert_player(base, head, True)
                base = head; head = commit('restore regular after ' + mode)
                assert_player(base, head, False)

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

