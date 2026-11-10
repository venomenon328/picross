"""HP-I1b2 revision cleanup against actual temporary Git/main histories."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tests.puzzle_production.background_catalog_fixtures import prepare
from tests.puzzle_production.background_change_fixtures import create_work
from tests.puzzle_production.test_background_retirement import snapshot
from tools.puzzle_production import background_retirement as retirement
from tools.puzzle_production import authoring_builder as builder
from tools.puzzle_production import catalog_background as bg, catalog_background_change as change
from tools.puzzle_production import content_registry as registry, integrated_content as integrated
from tools.puzzle_production import target_adapter as adapter
from tools.puzzle_production.contract import InvalidInput, load_json, write_json
from tools.puzzle_production.za1_fixtures import rated_registration


class BackgroundChangeRetirementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        owner = unittest.TestCase(); cls.addClassCleanup(owner.doCleanups)
        cls.fixture = prepare(owner, registered=True)

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='hp-i1b2-retirement-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.checkout = self.root / 'checkout'
        shutil.copytree(self.fixture.checkout, self.checkout)
        self.entry = load_json(self.checkout / registry.REGISTRY)['entries'][0]
        self.identifier = self.entry['id']
        write_json(self.checkout / retirement.INDEX, {'format': 'picross-authoring-index-v1', 'entries': []})
        self.git('init', '--quiet')
        self.original_commit = self.commit_main('Original background integration')

    def git(self, *arguments):
        return subprocess.run(['git', '-c', 'user.name=HP-I1b2 synthetic test',
                               '-c', 'user.email=hp-i1b2@example.invalid', '-c', 'commit.gpgsign=false',
                               *arguments], cwd=self.checkout, check=True, capture_output=True,
                              text=True, timeout=20).stdout.strip()

    def commit_main(self, message):
        self.git('add', '.')
        self.git('commit', '--quiet', '--message', message)
        commit = self.git('rev-parse', 'HEAD')
        self.git('update-ref', 'refs/remotes/origin/main', commit)
        return commit

    def changed(self, revision='bg-r01', choice='selected'):
        work = create_work(self, self.checkout, self.root, revision, choice)
        bundle = self.root / (revision + '-plan')
        self.assertEqual(change.plan(self.checkout, work.record_path, bundle)['status'], 'planned')
        self.assertEqual(change.adopt(self.checkout, bundle)['status'], 'adopted')
        return work, bundle

    def retire(self, commit, *revisions):
        return retirement.retire(self.checkout, [(self.identifier, revision) for revision in revisions], commit)

    def test_current_cleanup_and_post_cleanup_plan_noop_preserve_active_bytes(self):
        work, bundle = self.changed()
        commit = self.commit_main('Adopt independent background')
        before = snapshot(self.checkout)
        result = self.retire(commit, work.request['revision'])
        self.assertEqual(result['status'], 'background_production_retired')
        directory = str(Path(work.record_path).parent)
        after = snapshot(self.checkout)
        self.assertEqual({name: value for name, value in before.items()
                          if not name.startswith(directory + '/') and name != retirement.INDEX},
                         {name: value for name, value in after.items() if name != retirement.INDEX})
        self.assertTrue((self.checkout / Path(directory).parent).is_dir())
        proof = retirement.prove(self.checkout, [(self.identifier, work.request['revision'])], commit)[0]
        self.assertTrue(proof['absent']); self.assertTrue(proof['current'])
        self.assertEqual(proof['request'], work.request)
        self.assertEqual(self.retire(commit, work.request['revision'])['status'], 'no-op')
        with self.assertRaises(InvalidInput): change.adopt(self.checkout, bundle)
        # This is a real main ancestor, but predates this adoption. The active
        # target is already adopted and its entire work revision is absent.
        with self.assertRaisesRegex(InvalidInput, 'not integrated on main'):
            change.adopt(self.checkout, bundle, integrated_commit=self.original_commit)
        self.assertEqual(after, snapshot(self.checkout))
        self.assertEqual(change.adopt(self.checkout, bundle, integrated_commit=commit)['status'], 'no-op')
        self.assertEqual(after, snapshot(self.checkout))

    def test_superseded_cleanup_keeps_newer_open_work_and_never_fetches_old_images(self):
        first, _ = self.changed()
        first_commit = self.commit_main('Adopt first independent background')
        second, _ = self.changed('bg-r02', 'none')
        self.commit_main('Adopt explicit background removal')
        pending = create_work(self, self.checkout, self.root, 'bg-r03', 'selected')
        before = snapshot(self.checkout)
        original_git = retirement._History.git
        opened = []
        def metadata_only(history, *args):
            if args[0] == 'show':
                opened.append(args[1])
                self.assertFalse(args[1].lower().endswith(('.png', '.zip')))
            return original_git(history, *args)
        with patch.object(retirement._History, 'git', metadata_only):
            self.assertEqual(self.retire(first_commit, 'bg-r01')['status'], 'background_production_retired')
            after = snapshot(self.checkout)
            self.assertEqual(self.retire(first_commit, 'bg-r01')['status'], 'no-op')
            self.assertEqual(after, snapshot(self.checkout))
        self.assertTrue(opened)
        first_directory = str(Path(first.record_path).parent)
        self.assertEqual({name: value for name, value in before.items()
                          if not name.startswith(first_directory + '/') and name != retirement.INDEX},
                         {name: value for name, value in after.items() if name != retirement.INDEX})
        self.assertEqual({row['revision'] for row in load_json(self.checkout / retirement.INDEX)['entries']},
                         {'bg-r02', 'bg-r03'})
        self.assertTrue((self.checkout / second.record_path).is_file())
        self.assertTrue((self.checkout / pending.record_path).is_file())

    def test_original_cleanup_preserves_changed_source_and_independent_work(self):
        first, first_bundle = self.changed()
        before_main = snapshot(self.checkout)
        with self.assertRaisesRegex(InvalidInput, 'not indexed on main'):
            integrated.retire(self.checkout, [self.identifier], self.original_commit)
        self.assertEqual(before_main, snapshot(self.checkout))
        change_commit = self.commit_main('Changed background before raster retirement')
        before_receipt = snapshot(self.checkout)
        self.assertEqual(rated_registration(self.fixture.export, self.checkout, apply=True)['status'], 'no-op')
        self.assertEqual(before_receipt, snapshot(self.checkout))
        authority = {name: value for name, value in snapshot(self.checkout).items()
                     if name.startswith(('game/', 'content/backgrounds/', 'content/authoring/'))}
        result = integrated.retire(self.checkout, [self.identifier], self.original_commit)
        self.assertEqual(result['status'], 'production_retired')
        after = snapshot(self.checkout)
        self.assertEqual(authority, {name: after[name] for name in authority})
        bundle_before = snapshot(first_bundle)
        with self.assertRaisesRegex(InvalidInput, 'Stale'):
            change.adopt(self.checkout, first_bundle, integrated_commit=change_commit)
        self.assertEqual(after, snapshot(self.checkout))
        self.assertEqual(bundle_before, snapshot(first_bundle))
        entry = load_json(self.checkout / registry.REGISTRY)['entries'][0]
        receipt = load_json(self.checkout / entry['production']['package'] / 'manifest.json')
        source = load_json(self.checkout / bg.path(self.identifier))
        self.assertEqual(receipt['background']['source'], bg.initial_ref(source))
        self.assertEqual(rated_registration(self.fixture.export, self.checkout, apply=True)['status'], 'no-op')
        self.assertEqual(integrated.retire(self.checkout, [self.identifier], self.original_commit)['status'], 'no-op')
        self.assertEqual(after, snapshot(self.checkout))
        self.assertEqual(self.retire(change_commit, first.request['revision'])['status'], 'background_production_retired')
        self.commit_main('Complete original and first independent production')
        second, _ = self.changed('bg-r02', 'none')
        second_commit = self.commit_main('Change compact retired production')
        before = snapshot(self.checkout)
        self.assertEqual(integrated.retire(self.checkout, [self.identifier], self.original_commit)['status'], 'no-op')
        self.assertEqual(rated_registration(self.fixture.export, self.checkout, apply=True)['status'], 'no-op')
        self.assertEqual(before, snapshot(self.checkout))
        self.assertEqual(self.retire(second_commit, second.request['revision'])['status'], 'background_production_retired')
        after_cleanup = snapshot(self.checkout)
        self.assertEqual(integrated.retire(self.checkout, [self.identifier], self.original_commit)['status'], 'no-op')
        self.assertEqual(after_cleanup, snapshot(self.checkout))

    def test_planned_only_main_record_and_unmerged_main_argument_never_authorize_cleanup(self):
        work = create_work(self, self.checkout, self.root)
        planned_commit = self.commit_main('Unadopted background work')
        bundle = self.root / 'planned-only-plan'
        change.plan(self.checkout, work.record_path, bundle)
        change.adopt(self.checkout, bundle)
        self.commit_main('Actually adopted background')
        before = snapshot(self.checkout)
        with self.assertRaisesRegex(InvalidInput, 'not adopted'):
            self.retire(planned_commit, 'bg-r01')
        self.git('commit', '--allow-empty', '--quiet', '--message', 'Not on main')
        with self.assertRaises(InvalidInput): self.retire(self.git('rev-parse', 'HEAD'), 'bg-r01')
        self.assertEqual(before, snapshot(self.checkout))

    def test_historical_source_without_its_actual_live_output_is_not_adoption_proof(self):
        self.changed()
        target = self.checkout / bg.asset_path(self.identifier)
        correct = target.read_bytes()
        old = (self.fixture.checkout / bg.asset_path(self.identifier)).read_bytes()
        self.assertNotEqual(correct, old)
        target.write_bytes(old)
        broken_commit = self.commit_main('Synthetic source without its claimed live output')
        target.write_bytes(correct)
        self.changed('bg-r02', 'none')
        self.commit_main('Later valid compact background')
        before = snapshot(self.checkout)
        with self.assertRaisesRegex(InvalidInput, 'not its adopted HP-W2 output'):
            self.retire(broken_commit, 'bg-r01')
        self.assertEqual(before, snapshot(self.checkout))

    def test_full_batch_and_foreign_work_are_preflighted_before_any_deletion(self):
        work, _ = self.changed()
        commit = self.commit_main('Background ready for retirement')
        before = snapshot(self.checkout)
        with self.assertRaises(InvalidInput): self.retire(commit, 'bg-r01', 'missing')
        self.assertEqual(before, snapshot(self.checkout))
        directory = self.checkout / Path(work.record_path).parent
        extra = directory / 'foreign.txt'; extra.write_text('TEST ONLY foreign work', encoding='utf-8')
        before = snapshot(self.checkout)
        with self.assertRaises(InvalidInput): self.retire(commit, 'bg-r01')
        self.assertEqual(before, snapshot(self.checkout)); extra.unlink()
        name = work.record_path
        original = (self.checkout / name).read_bytes()
        (self.checkout / name).write_bytes(original + b'\n')
        self.git('add', name)
        (self.checkout / name).write_bytes(original)
        before = snapshot(self.checkout)
        with self.assertRaises(InvalidInput): self.retire(commit, 'bg-r01')
        self.assertEqual(before, snapshot(self.checkout))
        self.git('reset', '--quiet', 'HEAD', '--', name)
        index = load_json(self.checkout / retirement.INDEX)
        index['entries'] = []; write_json(self.checkout / retirement.INDEX, index)
        before = snapshot(self.checkout)
        with self.assertRaisesRegex(InvalidInput, 'Partial background retirement'): self.retire(commit, 'bg-r01')
        self.assertEqual(before, snapshot(self.checkout))

    def test_equal_revision_with_another_adoption_is_not_a_successor(self):
        work = create_work(self, self.checkout, self.root, 'bg-r01')
        rival = create_work(self, self.checkout, self.root, 'bg-rival')
        first_plan, rival_plan = self.root / 'first-plan', self.root / 'rival-plan'
        change.plan(self.checkout, work.record_path, first_plan)
        change.plan(self.checkout, rival.record_path, rival_plan)
        change.adopt(self.checkout, first_plan)
        commit = self.commit_main('First real adoption')
        # A different branch legitimately chose another job at revision 2.
        # The current source remains structurally/live valid but is not a
        # successor of the explicitly proven first adoption.
        old = load_json(first_plan / 'plan.json')['old']
        for name, text in old.items():
            if text is not None:
                (self.checkout / name).parent.mkdir(parents=True, exist_ok=True)
                (self.checkout / name).write_text(text, encoding='utf-8')
            elif (self.checkout / name).exists():
                (self.checkout / name).unlink()
        old_image = first_plan / 'previous/background.png'
        if old_image.exists(): (self.checkout / bg.asset_path(self.identifier)).write_bytes(old_image.read_bytes())
        change.adopt(self.checkout, rival_plan)
        registry.check_checkout(self.checkout)
        before = snapshot(self.checkout)
        with self.assertRaisesRegex(InvalidInput, 'not the proven adoption'):
            self.retire(commit, 'bg-r01')
        self.assertEqual(before, snapshot(self.checkout))

    def test_partial_io_failure_reports_remaining_paths_and_keeps_active_bytes(self):
        work, _ = self.changed()
        commit = self.commit_main('Background ready for bounded deletion')
        directory = self.checkout / Path(work.record_path).parent
        names = sorted(path for path in directory.rglob('*') if path.is_file())
        failure = names[1]
        active = {name: value for name, value in snapshot(self.checkout).items()
                  if not name.startswith('content/authoring/')}
        original_unlink = Path.unlink
        def fail(path, *args, **kwargs):
            if path == failure: raise PermissionError('TEST ONLY denied deletion')
            return original_unlink(path, *args, **kwargs)
        with patch.object(Path, 'unlink', fail), self.assertRaisesRegex(InvalidInput, 'remaining paths:') as caught:
            self.retire(commit, 'bg-r01')
        self.assertIn(str(directory), str(caught.exception))
        self.assertFalse(names[0].exists()); self.assertTrue(failure.exists())
        after = snapshot(self.checkout)
        self.assertEqual(active, {name: after[name] for name in active})

    def test_late_foreign_index_is_preserved_and_reported_as_partial_failure(self):
        work, _ = self.changed()
        commit = self.commit_main('Background ready for guarded index update')
        directory = self.checkout / Path(work.record_path).parent
        index = self.checkout / retirement.INDEX
        foreign = index.read_bytes() + b'\nTEST ONLY foreign late index'
        original_unlink = Path.unlink
        injected = []
        def inject(path, *args, **kwargs):
            result = original_unlink(path, *args, **kwargs)
            if not injected and path.is_relative_to(directory):
                index.write_bytes(foreign); injected.append(True)
            return result
        before = snapshot(self.checkout / 'game')
        with patch.object(Path, 'unlink', inject), self.assertRaisesRegex(InvalidInput, 'remaining paths:') as caught:
            self.retire(commit, 'bg-r01')
        self.assertIn(str(index), str(caught.exception))
        self.assertEqual(index.read_bytes(), foreign)
        self.assertEqual(before, snapshot(self.checkout / 'game'))

    def test_authoring_writer_lock_blocks_cleanup_before_any_deletion(self):
        self.changed()
        commit = self.commit_main('Background ready for cooperative cleanup')
        before = snapshot(self.checkout)
        with builder.writer(builder.git_root(self.checkout) / 'authoring-builder.lock'):
            with self.assertRaisesRegex(InvalidInput, 'Another authoring writer owns'):
                self.retire(commit, 'bg-r01')
        self.assertEqual(before, snapshot(self.checkout))
        self.assertEqual(self.retire(commit, 'bg-r01')['status'], 'background_production_retired')

    def test_late_foreign_empty_directory_is_preserved(self):
        work, _ = self.changed()
        commit = self.commit_main('Background ready for precise directory cleanup')
        directory = self.checkout / Path(work.record_path).parent
        foreign = directory / 'foreign-empty'
        original_unlink = Path.unlink
        injected = []
        def inject(path, *args, **kwargs):
            result = original_unlink(path, *args, **kwargs)
            if not injected and path.is_relative_to(directory):
                foreign.mkdir(); injected.append(True)
            return result
        index = (self.checkout / retirement.INDEX).read_bytes()
        with patch.object(Path, 'unlink', inject), self.assertRaisesRegex(InvalidInput, 'remaining paths:'):
            self.retire(commit, 'bg-r01')
        self.assertTrue(foreign.is_dir())
        self.assertEqual((self.checkout / retirement.INDEX).read_bytes(), index)

    def test_cli_dispatch_uses_explicit_revision_and_main_commit(self):
        work, _ = self.changed(choice='none')
        commit = self.commit_main('Explicit removal for CLI retirement')
        with patch('builtins.print') as output:
            code = adapter.main(['retire-background-production', '--checkout', str(self.checkout),
                '--integrated-commit', commit, '--authoring-revision', self.identifier, work.request['revision']])
        self.assertEqual(code, 0)
        self.assertIn('background_production_retired', output.call_args[0][0])
        self.assertFalse((self.checkout / work.record_path).exists())


if __name__ == '__main__': unittest.main()
