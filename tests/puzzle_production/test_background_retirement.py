"""HP-I1b1: real temporary Git/main proofs and compact background authority."""
from copy import deepcopy
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tests.puzzle_production.background_catalog_fixtures import prepare
from tools.puzzle_production import catalog_background as background, catalog_io as io
from tools.puzzle_production import content_registry as registry, integrated_content as integrated
from tools.puzzle_production import reveal_source, target_adapter as adapter
from tools.puzzle_production.contract import InvalidInput, load_json, write_json
from tools.puzzle_production.za1_fixtures import rated_registration


def snapshot(root):
    return {p.relative_to(root).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
            for p in root.rglob('*') if p.is_file() and '.git' not in p.relative_to(root).parts}


class BackgroundRetirementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        owner = unittest.TestCase()
        cls.addClassCleanup(owner.doCleanups)
        cls.prerequisites = {choice: prepare(owner, choice, registered=True) for choice in ('selected', 'none')}

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='hp-i1b1-retirement-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.checkout = self.root / 'checkout'

    def git(self, *arguments):
        return subprocess.run(['git', '-c', 'user.name=HP-I1b1 synthetic test',
                               '-c', 'user.email=hp-i1b1@example.invalid', '-c', 'commit.gpgsign=false',
                               *arguments], cwd=self.checkout, check=True, capture_output=True,
                              text=True, timeout=20).stdout.strip()

    def checkout_for(self, choice='selected', *, authoring=False):
        fixture = self.prerequisites[choice]
        shutil.copytree(fixture.checkout, self.checkout)
        self.entry = deepcopy(load_json(self.checkout / registry.REGISTRY)['entries'][0])
        self.identifier = self.entry['id']
        index = {'format': 'picross-authoring-index-v1', 'entries': []}
        if authoring:
            revision = self.entry['production']['revision']
            directory = 'content/authoring/' + self.identifier + '/' + revision
            archive = (self.checkout / self.entry['production']['package'] / 'input/package.zip').read_bytes()
            record = {'format': 'picross-authoring-record-v2', 'puzzle_id': self.identifier,
                      'revision': revision, 'state': 'registered', 'blockers': [],
                      'package': {'file': directory + '/package.zip', 'sha256': io.checksum(archive), 'bytes': len(archive)}}
            write_json(self.checkout / directory / 'record.json', record)
            (self.checkout / directory / 'package.zip').write_bytes(archive)
            (self.checkout / directory / 'prompt.txt').write_text('TEST ONLY completed production\n', encoding='utf-8')
            index['entries'].append({'puzzle_id': self.identifier, 'revision': revision, 'record': directory + '/record.json'})
        write_json(self.checkout / integrated.INDEX, index)
        self.git('init', '--quiet')
        return fixture

    def commit_main(self):
        self.git('add', '.')
        self.git('commit', '--quiet', '--message', 'Synthetic integrated production')
        commit = self.git('rev-parse', 'HEAD')
        self.git('update-ref', 'refs/remotes/origin/main', commit)
        return commit

    def retire(self, commit):
        return integrated.retire(self.checkout, [self.identifier], commit)

    def rewrite_receipt(self, value):
        current = load_json(self.checkout / registry.REGISTRY)
        entry = current['entries'][0]
        target = self.checkout / entry['production']['package'] / 'manifest.json'
        write_json(target, value)
        entry['production']['package_sha256'] = io.checksum(target.read_bytes())
        write_json(self.checkout / registry.REGISTRY, current)

    def test_selected_and_none_keep_source_runtime_rights_and_exact_noop(self):
        for choice in ('selected', 'none'):
            with self.subTest(choice=choice):
                if self.checkout.exists(): shutil.rmtree(self.checkout)
                fixture = self.checkout_for(choice, authoring=True)
                commit = self.commit_main()
                before = snapshot(self.checkout)
                source_path = background.path(self.identifier)
                original_source = load_json(self.checkout / source_path)
                result = self.retire(commit)
                self.assertEqual(result['status'], 'production_retired')
                value = load_json(self.checkout / registry.REGISTRY)
                entry = value['entries'][0]
                receipt = load_json(self.checkout / entry['production']['package'] / 'manifest.json')
                self.assertEqual(receipt['format'], integrated.BACKGROUND_FORMAT)
                self.assertEqual(receipt['entry'], self.entry)
                self.assertEqual(receipt['background'], background.receipt_binding(original_source, background.index(value)[self.identifier]))
                self.assertNotEqual(entry['production']['package_sha256'], self.entry['production']['package_sha256'])
                self.assertEqual((self.checkout / source_path).read_bytes(), before[source_path][0])
                after = snapshot(self.checkout)
                preserved = {n: v for n, v in before.items() if n.startswith(('game/', 'content/backgrounds/', 'content/difficulty/', 'content/added/'))}
                self.assertEqual(preserved, {n: after[n] for n in preserved})
                self.assertFalse((self.checkout / ('content/authoring/' + self.identifier)).exists())
                self.assertEqual(set((self.checkout / entry['production']['package']).iterdir()),
                                 {self.checkout / entry['production']['package'] / 'manifest.json'})
                with patch.object(background, 'build', side_effect=AssertionError('opened retired original input')), \
                        patch.object(adapter, 'verify_export', side_effect=AssertionError('replayed retired production')):
                    registry.check_checkout(self.checkout, replay=True)
                    registry.sync_runtime(self.checkout)
                    self.assertEqual(self.retire(commit)['status'], 'no-op')
                self.assertEqual(after, snapshot(self.checkout))
                self.assertEqual(rated_registration(fixture.export, self.checkout, apply=True)['status'], 'no-op')
                self.assertEqual(after, snapshot(self.checkout))

    def test_live_source_index_asset_notice_and_main_changes_block_before_deletion(self):
        self.checkout_for()
        commit = self.commit_main()
        names = [background.path(self.identifier), background.asset_path(self.identifier),
                 background.notice_path(self.identifier), registry.REGISTRY,
                 self.entry['production']['package'] + '/approval.json']
        for name in names:
            path = self.checkout / name
            raw = path.read_bytes()
            path.write_bytes(raw + b'\nTEST ONLY unmerged change')
            before = snapshot(self.checkout)
            with self.subTest(path=name), self.assertRaises((InvalidInput, ValueError)):
                self.retire(commit)
            self.assertEqual(before, snapshot(self.checkout))
            path.write_bytes(raw)
        self.git('commit', '--allow-empty', '--quiet', '--message', 'Unmerged synthetic commit')
        later = self.git('rev-parse', 'HEAD')
        before = snapshot(self.checkout)
        with self.assertRaises(InvalidInput): self.retire(later)
        self.assertEqual(before, snapshot(self.checkout))

    def test_open_or_unknown_authoring_siblings_block_even_when_on_main(self):
        self.checkout_for(authoring=True)
        index = load_json(self.checkout / integrated.INDEX)
        other = 'content/authoring/' + self.identifier + '/newer-open'
        write_json(self.checkout / other / 'record.json', {'state': 'raster_review', 'test_only': True})
        index['entries'].append({'puzzle_id': self.identifier, 'revision': 'newer-open', 'record': other + '/record.json'})
        write_json(self.checkout / integrated.INDEX, index)
        commit = self.commit_main()
        before = snapshot(self.checkout)
        with self.assertRaisesRegex(InvalidInput, 'Other authoring revisions'):
            self.retire(commit)
        self.assertEqual(before, snapshot(self.checkout))
        # Untracked foreign siblings also remain untouched.
        (self.checkout / other / 'unsaved.txt').write_text('TEST ONLY newer work', encoding='utf-8')
        before = snapshot(self.checkout)
        with self.assertRaises(InvalidInput): self.retire(commit)
        self.assertEqual(before, snapshot(self.checkout))

    def test_staged_source_and_unknown_package_file_block_before_deletion(self):
        self.checkout_for()
        commit = self.commit_main()
        name = background.path(self.identifier)
        target = self.checkout / name
        raw = target.read_bytes()
        target.write_bytes(raw + b'\n')
        self.git('add', name)
        target.write_bytes(raw)
        before = snapshot(self.checkout)
        with self.assertRaises(InvalidInput): self.retire(commit)
        self.assertEqual(before, snapshot(self.checkout))
        self.git('reset', '--quiet', 'HEAD', '--', name)
        foreign = self.checkout / self.entry['production']['package'] / 'foreign.bin'
        foreign.write_bytes(b'TEST ONLY unrelated work')
        before = snapshot(self.checkout)
        with self.assertRaises(InvalidInput): self.retire(commit)
        self.assertEqual(before, snapshot(self.checkout))

    def test_receipt_v1_downgrade_origin_change_and_source_change_are_rejected(self):
        self.checkout_for()
        commit = self.commit_main()
        self.retire(commit)
        target = self.checkout / self.entry['production']['package'] / 'manifest.json'
        receipt = load_json(target)
        mutations = []
        downgraded = deepcopy(receipt); downgraded['format'] = integrated.FORMAT; downgraded.pop('background')
        mutations.append(downgraded)
        changed = deepcopy(receipt); changed['background']['origin_sha256'] = '0' * 64; mutations.append(changed)
        changed = deepcopy(receipt); changed['background']['source']['sha256'] = '0' * 64; mutations.append(changed)
        changed = deepcopy(receipt); changed['entry']['production']['package_sha256'] = '0' * 64; mutations.append(changed)
        for altered in mutations:
            self.rewrite_receipt(altered)
            before = snapshot(self.checkout)
            with self.subTest(receipt=altered), self.assertRaises(InvalidInput): registry.check_checkout(self.checkout)
            self.assertEqual(before, snapshot(self.checkout))
            self.rewrite_receipt(receipt)
        self.git('commit', '--allow-empty', '--quiet', '--message', 'Later main proof')
        later = self.git('rev-parse', 'HEAD'); self.git('update-ref', 'refs/remotes/origin/main', later)
        before = snapshot(self.checkout)
        with self.assertRaisesRegex(InvalidInput, 'different main proof'): self.retire(later)
        self.assertEqual(before, snapshot(self.checkout))

    def test_partial_io_error_reports_actual_remaining_work_without_success(self):
        self.checkout_for()
        commit = self.commit_main()
        package = self.checkout / self.entry['production']['package']
        names = sorted(p for p in package.rglob('*') if p.is_file() and p != package / 'manifest.json')
        failure = names[1]
        original_unlink = Path.unlink
        def fail(path, *args, **kwargs):
            if path == failure: raise PermissionError('TEST ONLY denied deletion')
            return original_unlink(path, *args, **kwargs)
        game = snapshot(self.checkout / 'game')
        with patch.object(Path, 'unlink', fail), self.assertRaisesRegex(InvalidInput, 'remaining paths:') as caught:
            self.retire(commit)
        self.assertIn(str(package), str(caught.exception))
        self.assertFalse(names[0].exists())
        self.assertTrue(failure.exists())
        self.assertEqual(game, snapshot(self.checkout / 'game'))

    def test_foreign_changes_after_preflight_are_preserved_before_replacement(self):
        for kind in ('manifest', 'index', 'registry', 'new-file'):
            with self.subTest(kind=kind):
                if self.checkout.exists(): shutil.rmtree(self.checkout)
                self.checkout_for(authoring=True)
                commit = self.commit_main()
                package = self.checkout / self.entry['production']['package']
                target = {'manifest': package / 'manifest.json', 'index': self.checkout / integrated.INDEX,
                          'registry': self.checkout / registry.REGISTRY, 'new-file': package / 'foreign.txt'}[kind]
                injected = []
                original_unlink = Path.unlink
                def replace_after_guard(path, *args, **kwargs):
                    result = original_unlink(path, *args, **kwargs)
                    if not injected and path.is_relative_to(package):
                        raw = (target.read_bytes() if target.exists() else b'') + b'\nTEST ONLY foreign late bytes'
                        target.write_bytes(raw); injected.append(raw)
                    return result
                game = snapshot(self.checkout / 'game')
                with patch.object(Path, 'unlink', replace_after_guard), self.assertRaisesRegex(InvalidInput, 'remaining paths:'):
                    self.retire(commit)
                self.assertTrue(injected)
                self.assertEqual(target.read_bytes(), injected[0])
                self.assertEqual(game, snapshot(self.checkout / 'game'))


if __name__ == '__main__': unittest.main()
