"""HP-I1b1: mixed-catalog consumers preserve the complete background authority."""
from copy import deepcopy
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tests.puzzle_production.background_catalog_fixtures import prepare
from tests.puzzle_production.test_catalog_reveal import synthetic_image
from tools.puzzle_production import catalog_analysis as analysis, catalog_added as added
from tools.puzzle_production import catalog_added_history as dates, catalog_method as method, catalog_rating as rating
from tools.puzzle_production import catalog_background as background, catalog_io as io, catalog_reveal as reveal
from tools.puzzle_production import catalog_transaction as tx, content_registry as registry, content_update
from tools.puzzle_production import reveal_source, target_adapter as adapter
from tools.puzzle_production.contract import InvalidInput, canonical_bytes, load_json, write_json
from tools.puzzle_production.za1_fixtures import FIXTURES, approve, difficulty_for_export, isolated_checkout, make, rated_registration, seal


def snapshot(root):
    return {p.relative_to(root).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
            for p in root.rglob('*') if p.is_file() and '.git' not in p.relative_to(root).parts}


class BackgroundConsumerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        owner = unittest.TestCase(); cls.addClassCleanup(owner.doCleanups)
        cls.background = prepare(owner, registered=True)
        root = cls.background.case.root
        approval = root / 'legacy-approval.json'; approve(FIXTURES / 'direct-color', approval)
        cls.legacy_export = root / 'legacy-export'
        cls.legacy_manifest = adapter.export(FIXTURES / 'direct-color', cls.legacy_export,
            name='TEST ONLY legacy neighbor', revision=1, stem='legacy_neighbor', save_slot='legacy_neighbor',
            approval_path=approval, category_id='voegel', categories_path=cls.background.checkout / 'content/categories.json')
        rated_registration(cls.legacy_export, cls.background.checkout, apply=True)
        shadow = make(root / 'legacy-shadow-input', cls.background.manifest['definition_id'], 3, 3, 'mono')
        approval = root / 'legacy-shadow-approval.json'; approve(shadow, approval)
        cls.shadow_export = root / 'legacy-shadow-export'
        adapter.export(shadow, cls.shadow_export, name='TEST ONLY blocked legacy input',
            revision=8, stem='background_test', save_slot='same_slot', approval_path=approval,
            category_id='voegel', categories_path=cls.background.checkout / 'content/categories.json')

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='hp-i1b1-consumers-'); self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name); self.checkout = self.root / 'checkout'
        shutil.copytree(self.background.checkout, self.checkout)
        self.background_id = self.background.manifest['definition_id']
        self.legacy_id = self.legacy_manifest['definition_id']

    def entries(self):
        return {entry['id']: entry for entry in registry.check_checkout(self.checkout)['entries']}

    def protected(self):
        entry = self.entries()[self.background_id]
        names = {background.path(self.background_id), background.asset_path(self.background_id), background.notice_path(self.background_id),
                 'game/' + entry['definition'], 'game/' + entry['reveal'], reveal_source.identity(entry)['notice']}
        return {name: value for name, value in snapshot(self.checkout).items()
                if name in names or name.startswith(entry['production']['package'] + '/')}

    def git_commit(self):
        def git(*arguments):
            return subprocess.run(['git', '-c', 'user.name=HP-I1b1 synthetic test',
                '-c', 'user.email=hp-i1b1@example.invalid', '-c', 'commit.gpgsign=false', *arguments],
                cwd=self.checkout, check=True, text=True, capture_output=True, timeout=20).stdout.strip()
        git('init', '--quiet'); git('add', '.'); git('commit', '--quiet', '--message', 'Synthetic mixed catalog')
        return git('rev-parse', 'HEAD')

    def request(self, identifier, tag='reveal'):
        entry = self.entries()[identifier]
        directory = self.root / (tag + '-input'); directory.mkdir()
        synthetic_image(directory / 'image.png')
        catalog = load_json(self.checkout / 'content/categories.json')
        resolved = reveal_source.resolve(self.checkout, entry, catalog)
        old = reveal_source.load(self.checkout, entry, catalog)
        notice = (self.checkout / reveal_source.identity(entry)['notice']).read_bytes()
        declaration = {'format': reveal_source.APPROVAL, 'id': identifier,
            'image_revision': old['current']['image_revision'] + 1 if old else 1,
            'definition_sha256': resolved['definition_sha256'], 'previous_reveal_sha256': resolved['effective_reveal_sha256'],
            'reveal_sha256': io.checksum((directory / 'image.png').read_bytes()), 'notice_sha256': io.checksum(notice),
            'actor': 'TEST ONLY', 'timestamp_utc': '2026-11-09T12:00:00Z', 'statement': 'Synthetic reveal approval.',
            'checks': dict.fromkeys(('reveal_approved', 'motif_raster_consistent', 'final_editorial_approved'), True), 'test_only': True}
        row = {'id': identifier, 'image': 'image.png', 'approval': declaration,
               'provenance': {'author': 'Synthetic fixture', 'usage_basis': 'Project test data',
                              'source': 'Fixed test geometry', 'changes': 'TEST ONLY alpha detail'}, 'notice_append': None}
        write_json(directory / 'request.json', {'format': reveal.REQUEST, 'entries': [row]})
        return directory / 'request.json', row

    def assert_background_sources(self, sources):
        for name in (background.CAPABILITY, background.path(self.background_id),
                     background.asset_path(self.background_id), background.notice_path(self.background_id)):
            self.assertIn(name, sources)
            self.assertEqual(sources[name], io.file_hash(self.checkout, name))

    def test_rating_added_method_and_sync_keep_background_and_bind_new_plan_generations(self):
        before = self.protected()
        (self.checkout / rating.path(self.background_id)).unlink()
        (self.checkout / added.path(self.background_id)).unlink()
        registry.sync_runtime(self.checkout)
        commit = self.git_commit()
        report_dir = self.root / 'rating-report'
        report = analysis.preview(self.checkout, report_dir, 'mixed-rating', commit, ids=[self.background_id],
                                  checked_inputs={self.background_id: difficulty_for_export(self.background.export)})
        self.assertEqual(report['format'], 'picross-catalog-difficulty-report-v5')
        self.assert_background_sources(report['result']['sources'])
        self.assertEqual(analysis.adopt(self.checkout, report_dir, apply=True)['status'], 'adopted')
        after_rating = snapshot(self.checkout)
        self.assertEqual(analysis.adopt(self.checkout, report_dir, apply=True)['status'], 'no-op')
        self.assertEqual(snapshot(self.checkout), after_rating)
        added_plan = dates.plan(self.checkout, 'mixed-added', commit)
        self.assertEqual(added_plan['format'], 'picross-added-plan-v4')
        self.assert_background_sources(added_plan['sources'])
        path = self.root / 'added-plan.json'; write_json(path, added_plan)
        self.assertEqual(dates.adopt(self.checkout, path, apply=True)['status'], 'adopted')
        after_added = snapshot(self.checkout)
        self.assertEqual(dates.adopt(self.checkout, path, apply=True)['status'], 'no-op')
        self.assertEqual(snapshot(self.checkout), after_added)
        activation = method.plan(self.checkout, method.OLD, method.NEW, method.method_hash(method.NEW))
        self.assertEqual(activation['format'], 'picross-difficulty-activation-plan-v2')
        self.assert_background_sources(activation['sources'])
        self.assertEqual(method.adopt(self.checkout, activation)['status'], 'activated')
        after_activation = snapshot(self.checkout)
        self.assertEqual(method.adopt(self.checkout, activation)['status'], 'no-op')
        self.assertEqual(snapshot(self.checkout), after_activation)
        catalog = load_json(self.checkout / 'content/categories.json')
        catalog['categories'][0]['name'] += ' TEST ONLY'
        write_json(self.checkout / 'content/categories.json', catalog)
        registry.sync_runtime(self.checkout)
        after_sync = snapshot(self.checkout); registry.sync_runtime(self.checkout)
        self.assertEqual(snapshot(self.checkout), after_sync)
        self.assertEqual(self.protected(), before)
        self.assertEqual(load_json(self.checkout / registry.RUNTIME)['format'], background.RUNTIME_FORMAT)

    def test_legacy_raster_update_and_reveal_adoption_keep_background_bytes(self):
        protected = self.protected()
        entry = self.entries()[self.legacy_id]
        package = self.root / 'legacy-update-input'; shutil.copytree(self.legacy_export / 'input', package)
        handoff = load_json(package / 'handoff.json'); handoff['revision'] = 'r02'
        (package / 'inventory.json').unlink(); (package / 'derivation.json').unlink(missing_ok=True)
        seal(package, handoff)
        approval = self.root / 'legacy-update-approval.json'; approve(package, approval)
        output = self.root / 'legacy-update-export'
        adapter.export(package, output, name='TEST ONLY legacy neighbor', revision=2,
            stem='legacy_neighbor', save_slot='legacy_neighbor', approval_path=approval,
            category_id=entry['category_id'], categories_path=self.checkout / 'content/categories.json')
        self.assertEqual(content_update.update(output, self.checkout, entry['production']['definition_sha256'],
                                              apply=True, rebind_difficulty=True)['status'], 'updated')
        self.assertEqual(self.protected(), protected)
        request, _ = self.request(self.legacy_id)
        output = self.root / 'reveal-plan'
        self.assertEqual(reveal.plan(self.checkout, [self.legacy_id], request, output)['status'], 'planned')
        value = load_json(output / 'plan.json')
        self.assertEqual(value['format'], 'picross-reveal-plan-v3')
        self.assert_background_sources(value['snapshot']['sources'])
        self.assertEqual(set(value['snapshot']['namespaces']), {'reveals', 'difficulty', 'added', 'packages', 'backgrounds', 'background_assets'})
        self.assertEqual(reveal.adopt(self.checkout, output / 'plan.json')['status'], 'adopted')
        after = snapshot(self.checkout)
        self.assertEqual(reveal.adopt(self.checkout, output / 'plan.json')['status'], 'no-op')
        self.assertEqual(snapshot(self.checkout), after)
        self.assertEqual(self.protected(), protected)

    def test_background_target_raster_and_reveal_are_blocked_through_direct_apis(self):
        entries = self.entries(); entry = entries[self.background_id]
        before = snapshot(self.checkout)
        with patch.object(reveal, 'image_input', side_effect=AssertionError('background image was opened')):
            with self.assertRaisesRegex(InvalidInput, 'Background target'):
                reveal.build(self.checkout, [self.background_id], {self.background_id: {}}, self.root)
        with self.assertRaisesRegex(InvalidInput, 'Background target'):
            reveal_source.revise(self.checkout, entry, load_json(self.checkout / 'content/categories.json'),
                                 '0' * 64, {}, {})
        snapshot_value = tx.capture(self.checkout)
        texts = {n: raw.decode() if raw is not None else None for n, raw in snapshot_value['texts'].items()}
        altered = deepcopy(texts); altered[reveal_source.path(self.background_id)] = '{}'
        with self.assertRaisesRegex(InvalidInput, 'Background target'):
            reveal.validate_delta({'old': texts, 'new': altered, 'replacements': {}}, snapshot_value['registry'], self.checkout)
        for exported in (self.background.export, self.shadow_export):
            for apply in (False, True):
                with self.subTest(export=exported.name, apply=apply), self.assertRaisesRegex(InvalidInput, 'Background target'):
                    content_update.update(exported, self.checkout, entry['production']['definition_sha256'], apply=apply)
        self.assertEqual(snapshot(self.checkout), before)

    def test_capability_byte_change_stales_each_new_saved_plan_before_writes(self):
        commit = self.git_commit()
        report_dir = self.root / 'stale-rating'
        analysis.preview(self.checkout, report_dir, 'stale-rating', commit, ids=[self.background_id],
                         checked_inputs={self.background_id: difficulty_for_export(self.background.export)})
        added_plan = self.root / 'stale-added.json'; write_json(added_plan, dates.plan(self.checkout, 'stale-added', commit))
        activation = method.plan(self.checkout, method.OLD, method.NEW, method.method_hash(method.NEW))
        request, _ = self.request(self.legacy_id, 'stale-reveal')
        plan_dir = self.root / 'stale-reveal-plan'; reveal.plan(self.checkout, [self.legacy_id], request, plan_dir)
        capability = self.checkout / background.CAPABILITY
        capability.write_bytes(capability.read_bytes() + b'\n')
        before = snapshot(self.checkout)
        actions = (lambda: analysis.adopt(self.checkout, report_dir, apply=True),
                   lambda: dates.adopt(self.checkout, added_plan, apply=True),
                   lambda: method.adopt(self.checkout, activation),
                   lambda: reveal.adopt(self.checkout, plan_dir / 'plan.json'))
        for action in actions:
            with self.assertRaises(InvalidInput): action()
            self.assertEqual(snapshot(self.checkout), before)

    def test_saved_v2_reveal_plan_allows_false_capability_but_never_acquires_background_scope(self):
        self.checkout = isolated_checkout(self.root / 'legacy-only')
        rated_registration(self.legacy_export, self.checkout, apply=True)
        request, row = self.request(self.legacy_id, 'old-reveal')
        value, journal, files = reveal.build(self.checkout, [self.legacy_id], {self.legacy_id: row},
                                             request.parent, plan_format=reveal.SD2_FORMAT)
        self.assertEqual(journal['format'], tx.FORMATS['reveal-adoption'])
        self.assertNotIn(background.CAPABILITY, value['snapshot']['sources'])
        self.assertEqual(set(value['snapshot']['namespaces']), {'reveals', 'difficulty', 'added', 'packages'})
        plan_dir = self.root / 'old-reveal-plan'; plan_dir.mkdir()
        for name, raw in {'plan.json': canonical_bytes(value) + b'\n', **files}.items():
            path = plan_dir / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
        capability = load_json(self.background.checkout / background.CAPABILITY)
        write_json(self.checkout / background.CAPABILITY, capability)
        before = snapshot(self.checkout)
        with self.assertRaisesRegex(InvalidInput, 'Legacy plan'): reveal.adopt(self.checkout, plan_dir / 'plan.json')
        self.assertEqual(snapshot(self.checkout), before)
        capability['enabled'] = False; write_json(self.checkout / background.CAPABILITY, capability)
        self.assertEqual(reveal.adopt(self.checkout, plan_dir / 'plan.json')['status'], 'adopted')
        capability['enabled'] = True; write_json(self.checkout / background.CAPABILITY, capability)
        rated_registration(self.background.export, self.checkout, apply=True)
        before = snapshot(self.checkout)
        with self.assertRaisesRegex(InvalidInput, 'Legacy plan'): reveal.adopt(self.checkout, plan_dir / 'plan.json')
        self.assertEqual(snapshot(self.checkout), before)


if __name__ == '__main__': unittest.main()
