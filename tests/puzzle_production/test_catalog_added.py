"""KU-B synthetic metadata, transaction, history and no-op regressions."""
from copy import deepcopy
import os
from pathlib import Path
import shutil
import subprocess
import unittest
from unittest.mock import patch

from tests.puzzle_production import test_catalog_integration as fixtures
snapshot = fixtures.snapshot
from tools.puzzle_production import catalog_added as added, catalog_added_history as history
from tools.puzzle_production import catalog_transaction as tx, content_registry as cr
from tools.puzzle_production.contract import InvalidInput, canonical_bytes, load_json
from tools.puzzle_production.za1_fixtures import isolated_checkout


class AddedTests(unittest.TestCase):
    setUpClass = classmethod(fixtures.CatalogTests.setUpClass.__func__)
    tearDownClass = classmethod(fixtures.CatalogTests.tearDownClass.__func__)
    setUp = fixtures.CatalogTests.setUp

    def unstamp(self):
        (self.checkout / added.path(self.identifier)).unlink()
        registry = load_json(self.checkout / cr.REGISTRY)
        categories = load_json(self.checkout / 'content/categories.json')
        (self.checkout / cr.RUNTIME).write_bytes(canonical_bytes(cr.projection(registry, categories, self.checkout, version=3)) + b'\n')

    def git(self, *args, date='2024-01-01T12:00:00Z'):
        env = {**os.environ, 'GIT_AUTHOR_DATE': date, 'GIT_COMMITTER_DATE': date,
               'GIT_AUTHOR_NAME': 'Synthetic KU-B', 'GIT_COMMITTER_NAME': 'Synthetic KU-B',
               'GIT_AUTHOR_EMAIL': 'synthetic@example.invalid', 'GIT_COMMITTER_EMAIL': 'synthetic@example.invalid'}
        return subprocess.check_output(['git', '-C', str(self.checkout), *args], env=env, stderr=subprocess.DEVNULL).decode().strip()

    def historical_plan(self):
        self.unstamp()
        self.git('init'); self.git('add', '.'); self.git('commit', '-m', 'synthetic visible catalog')
        base = self.git('rev-parse', 'HEAD')
        value = history.plan(self.checkout, 'synthetic-first', base)
        path = self.root / 'plan.json'; path.write_bytes(canonical_bytes(value) + b'\n')
        return value, path

    def test_read_only_registration_plan_then_timestamp_and_repeat_noop(self):
        root = isolated_checkout(self.root / 'empty')
        before = snapshot(root)
        with patch.object(added, 'registration', side_effect=AssertionError('planning must not read clock')):
            result = cr.registration(self.exported, root, difficulty=self.checked)
        self.assertEqual(result['status'], 'planned')
        self.assertEqual(snapshot(root), before)
        cr.registration(self.exported, root, apply=True, difficulty=self.checked)
        value = load_json(root / added.path(self.identifier))
        self.assertEqual(value['provenance']['kind'], 'registration')
        self.assertEqual(load_json(root / cr.RUNTIME)['entries'][0]['added_at'], value['added_at'])
        before = snapshot(root); mtimes = {p: p.stat().st_mtime_ns for p in root.rglob('*') if p.is_file()}
        with patch.object(added, 'registration', side_effect=AssertionError('repeat cannot read clock')):
            self.assertEqual(cr.registration(self.exported, root, apply=True)['status'], 'no-op')
            cr.sync_runtime(root)
        self.assertEqual(snapshot(root), before)
        self.assertEqual(mtimes, {p: p.stat().st_mtime_ns for p in root.rglob('*') if p.is_file()})

    def test_strict_dates_schema_namespace_and_no_fallback(self):
        name = self.checkout / added.path(self.identifier)
        original = load_json(name)
        for bad in (True, 0, {}, [], '2023-02-29T00:00:00Z', '2024-01-01T24:00:00Z',
                    '2024-01-01T00:00:60Z', '2024-01-01T00:00:00+00:00', '2024-01-01T00:00:00.1Z'):
            value = deepcopy(original); value['added_at'] = bad
            name.write_bytes(canonical_bytes(value) + b'\n')
            before = snapshot(self.checkout)
            for action in (lambda: cr.check_checkout(self.checkout), lambda: cr.sync_runtime(self.checkout)):
                with self.assertRaises(ValueError): action()
                self.assertEqual(before, snapshot(self.checkout))
        name.write_bytes(added.encoded(original))
        rogue = self.checkout / 'content/added/pz-foreign.json'
        rogue.write_bytes(added.encoded(original))
        with self.assertRaises(ValueError): cr.check_checkout(self.checkout)
        rogue.unlink()
        name.write_bytes(b'{"format":"wrong","format":"picross-added-v1"}\n')
        with self.assertRaisesRegex(ValueError, 'Duplicate'): cr.check_checkout(self.checkout)

    def test_historical_plan_separate_apply_durable_provenance_and_exact_repeat(self):
        value, path = self.historical_plan()
        self.assertEqual(value['entries'][0]['proposed'], '2024-01-01T12:00:00Z')
        before = snapshot(self.checkout)
        history.adopt(self.checkout, path)
        self.assertEqual(snapshot(self.checkout), before)
        history.adopt(self.checkout, path, apply=True)
        self.assertEqual(added.load_sources(self.checkout, cr.check_checkout(self.checkout))[self.identifier]['added_at'], '2024-01-01T12:00:00Z')
        after = snapshot(self.checkout)
        mtimes = {p: p.stat().st_mtime_ns for p in self.checkout.rglob('*') if p.is_file()}
        with patch.object(subprocess, 'run', side_effect=AssertionError('adopt must not read Git')):
            self.assertEqual(history.adopt(self.checkout, path, apply=True)['status'], 'no-op')
        self.assertEqual(snapshot(self.checkout), after)
        self.assertEqual(mtimes, {p: p.stat().st_mtime_ns for p in self.checkout.rglob('*') if p.is_file()})
        immutable = {n: b for n, b in before.items() if n != cr.RUNTIME}
        self.assertTrue(all(after[n] == b for n, b in immutable.items()))

    def test_historical_crash_recovery_foreign_guard_and_stale_plan(self):
        _, path = self.historical_plan()
        before = snapshot(self.checkout)
        with self.assertRaises(InterruptedError):
            history.adopt(self.checkout, path, apply=True, fail_step='crash-' + added.path(self.identifier))
        owned = self.checkout / added.path(self.identifier)
        own_bytes = owned.read_bytes()
        owned.write_bytes(own_bytes + b'foreign')
        foreign = snapshot(self.checkout)
        with self.assertRaises(ValueError): cr.recover(self.checkout)
        self.assertEqual(snapshot(self.checkout), foreign)
        owned.write_bytes(own_bytes)
        cr.recover(self.checkout)
        self.assertFalse((self.checkout / added.path(self.identifier)).exists())
        self.assertFalse((self.checkout / tx.LOCK).exists())
        cr.check_checkout(self.checkout)
        # Recovery is current v4 immediately, so the v3-bound old plan is stale.
        with self.assertRaisesRegex(ValueError, 'sources changed'):
            history.adopt(self.checkout, path, apply=True)
        self.assertTrue(all((self.checkout/n).read_bytes() == b for n,b in before.items() if n != cr.RUNTIME))

    def test_retained_metadata_in_new_plan_and_repeat_planning(self):
        value, path = self.historical_plan()
        history.adopt(self.checkout, path, apply=True)
        before = snapshot(self.checkout)
        self.assertEqual(history.plan(self.checkout, value['run_id'], value['base_commit']), value)
        next_plan = history.plan(self.checkout, 'next-plan', value['base_commit'])
        self.assertEqual(next_plan['entries'][0]['old'], value['entries'][0]['proposed'])
        next_path = self.root / 'next.json'; next_path.write_bytes(canonical_bytes(next_plan) + b'\n')
        self.assertEqual(history.adopt(self.checkout, next_path, apply=True)['status'], 'no-op')
        self.assertEqual(before, snapshot(self.checkout))

    def test_direct_priority_conflict_and_never_visible_unknown(self):
        value, _ = self.historical_plan()
        def receipt(key, date):
            raw = canonical_bytes({'id': self.identifier, 'event': 'first-playable-registration', 'success': True, 'registered_at': date}) + b'\n'
            return {'key': key, 'kind': 'direct', 'commit': value['base_commit'], 'path': 'receipt.json',
                    'content': raw.decode(), 'sha256': history.hashed(raw), 'reference_time': date, 'integration': None}
        first = receipt('direct-a', '2023-01-01T00:00:00Z')
        plan = history.plan(self.checkout, 'direct', value['base_commit'], direct=[first])
        self.assertEqual(plan['entries'][0]['kind'], 'direct')
        self.assertEqual(plan['entries'][0]['proposed'], first['reference_time'])
        conflict = history.plan(self.checkout, 'conflict', value['base_commit'], direct=[first, receipt('direct-b','2023-01-02T00:00:00Z')])
        self.assertIsNone(conflict['entries'][0]['proposed'])
        self.assertIn('Conflicting', conflict['entries'][0]['reason'])
        # A separate synthetic history whose only snapshot is hidden.
        registry = load_json(self.checkout/cr.REGISTRY); registry['entries'][0]['visible'] = False
        (self.checkout/cr.REGISTRY).write_bytes(canonical_bytes(registry)+b'\n')
        categories = load_json(self.checkout/'content/categories.json')
        (self.checkout/cr.RUNTIME).write_bytes(canonical_bytes(cr.projection(registry,categories,self.checkout))+b'\n')
        self.git('checkout','--orphan','hidden-only'); self.git('add','.'); self.git('commit','-m','hidden catalog')
        unknown = history.plan(self.checkout,'hidden',self.git('rev-parse','HEAD'))
        self.assertIsNone(unknown['entries'][0]['proposed'])
        self.assertIn('no valid visible',unknown['entries'][0]['reason'])

    def test_legacy_v3_journal_recovers_directly_to_v4(self):
        self.unstamp()
        snapshot_before = tx.capture(self.checkout)
        journal = tx.prepare(self.checkout, snapshot_before, {}, operation='sync')
        journal['format'] = tx.LEGACY_FORMATS['sync']
        journal.pop('replacements')
        from tools.puzzle_production import reveal_source
        journal['old'].pop(reveal_source.path(self.identifier)); journal['new'].pop(reveal_source.path(self.identifier))
        journal['retained'] = tx.historical_snapshot(snapshot_before)['retained']
        journal['old'].pop(added.path(self.identifier)); journal['new'].pop(added.path(self.identifier))
        journal['new'][cr.RUNTIME] = journal['old'][cr.RUNTIME]
        (self.checkout / tx.LOCK).write_bytes(canonical_bytes(journal) + b'\n')
        cr.recover(self.checkout)
        self.assertEqual(load_json(self.checkout / cr.RUNTIME)['format'], 'picross-runtime-registry-v4')
        self.assertIsNone(load_json(self.checkout / cr.RUNTIME)['entries'][0]['added_at'])
        cr.check_checkout(self.checkout)

    def test_missing_unknown_survives_sync_without_clock(self):
        self.unstamp()
        with patch.object(added, 'registration', side_effect=AssertionError('sync cannot invent time')):
            cr.sync_runtime(self.checkout)
        self.assertFalse((self.checkout / added.path(self.identifier)).exists())
        self.assertIsNone(load_json(self.checkout / cr.RUNTIME)['entries'][0]['added_at'])
