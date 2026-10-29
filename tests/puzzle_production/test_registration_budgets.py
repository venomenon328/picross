"""RI-A: fixed synthetic bytes and a controlled monotonic clock; no long sleeps."""
from contextlib import redirect_stdout, redirect_stderr
from copy import deepcopy
import io as streams
import json
import math
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from tools.puzzle_production import catalog_io as io, catalog_transaction as tx
from tools.puzzle_production import catalog_publication as pub, content_registry as cr
from tools.puzzle_production import operation_diagnostics as diag, target_adapter as adapter
from tools.puzzle_production.contract import Aborted, InvalidInput
from tools.puzzle_production.za1_fixtures import FIXTURES, approve, isolated_checkout, difficulty_for_export


class Clock:
    now = 100.0

    def __call__(self):
        return self.now


def files(root):
    return {p.relative_to(root).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
            for p in root.rglob('*') if p.is_file()}


class BudgetTests(unittest.TestCase):
    def test_invalid_values_and_plan_update_reject_before_io(self):
        for value in (True, False, 0, -1, float('nan'), float('inf'), '1800', 10 ** 1000):
            with self.subTest(value=str(value)[:20]), patch.object(tx, 'capture', side_effect=AssertionError('I/O')):
                for name in ('publication_seconds', 'recovery_seconds'):
                    with self.assertRaises(InvalidInput):
                        cr.registration(Path('missing'), Path('missing'), apply=True, **{name: value})
                with self.assertRaises(InvalidInput):
                    cr.recover(Path('missing'), recovery_seconds=value)
        from tools.puzzle_production.catalog_integration import integrate
        for call in (lambda: cr.registration(None, None, publication_seconds=1),
                     lambda: integrate(None, None, apply=True, expected_definition_sha256='a'*64, recovery_seconds=1)):
            with patch.object(tx, 'capture', side_effect=AssertionError('I/O')), self.assertRaises(InvalidInput):
                call()
        self.assertEqual(diag.seconds(.01), .01)
        with self.assertRaises(InvalidInput):
            diag.seconds(1e308, now=1e308)

    def test_warning_once_nested_deadlines_and_durable_unwind(self):
        clock = Clock(); output = streams.StringIO()
        with patch.object(diag.time, 'monotonic', clock):
            d = diag.Diagnostics('register', stderr=output)
            with diag.observe(d), diag.operation('Publication', 1800, 'test'):
                clock.now += 300
                io.tick(); io.tick()
                clock.now += 1
                io.tick()
            self.assertEqual(output.getvalue().count('warning-300s'), 1)
            with self.assertRaises(Aborted), io.budget(10), diag.operation('Publication', 1800, 'test'):
                clock.now += 11
                io.tick()
            with self.assertRaises(Aborted), diag.operation('Publication', 20, 'test'), io.budget(30):
                clock.now += 21
                io.tick()
            with io.budget(1), diag.operation('Publication', 2, 'test'):
                clock.now += 3
                diag.durable('completed')
            # A later operation receives no exemption from an earlier commit.
            with self.assertRaises(Aborted), io.budget(1):
                clock.now += 2

    def test_progress_stall_and_nested_phase_accounting(self):
        clock = Clock(); output = streams.StringIO()
        with patch.object(diag.time, 'monotonic', clock):
            d = diag.Diagnostics('plan', stderr=output)
            with diag.observe(d), diag.phase('outer'):
                with diag.phase('inner'):
                    clock.now += 31
                    io.tick()
                diag.count('files', 1, work='verified one file')
            report = d.result()
        self.assertIn('no proven progress for 30s', output.getvalue())
        self.assertEqual(report['counters'], {'files': 1})
        self.assertEqual([p['seconds'] for p in report['phases']], [31, 31])
        self.assertTrue(all(p['inclusive'] for p in report['phases']))
        self.assertEqual(report['last_progress']['elapsed_seconds'], 31)

    def test_read_keeps_type_alias_hardlink_and_fresh_identity_guards(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); target = root/'sample'; target.write_bytes(b'own')
            with patch.object(io, 'safe', wraps=io.safe) as safe:
                self.assertEqual(tx.read(root, 'sample'), b'own')
                self.assertEqual(safe.call_count, 2)
            self.assertIsNone(tx.read(root, 'absent'))
            (root/'folder').mkdir()
            for name in ('folder', 'Sample'):
                with self.assertRaises(InvalidInput): tx.read(root, name)
            os.link(target, root/'linked')
            with self.assertRaises(InvalidInput): tx.read(root, 'sample')
            (root/'linked').unlink()
            original = io.safe; count = 0
            def changed(*args):
                nonlocal count
                count += 1
                if count == 2:
                    target.unlink(); target.write_bytes(b'foreign bytes')
                return original(*args)
            with patch.object(io, 'safe', side_effect=changed), self.assertRaises(InvalidInput):
                tx.read(root, 'sample')
            self.assertEqual(target.read_bytes(), b'foreign bytes')

    def test_report_new_atomic_collision_and_cli_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); checkout = root/'checkout'; checkout.mkdir()
            with self.assertRaises(InvalidInput): diag.report_target(checkout/'report.json', [checkout])
            with self.assertRaises(InvalidInput): diag.report_target(root/'missing'/'report.json', [])
            target = diag.report_target(root/'report.json', [checkout])
            diag.write_report(target, {'format': diag.FORMAT})
            before = target.read_bytes()
            with self.assertRaises(InvalidInput): diag.write_report(target, {})
            self.assertEqual(target.read_bytes(), before)
            for cmd in ('plan', 'update', 'export'):
                with redirect_stderr(streams.StringIO()), self.assertRaises(SystemExit):
                    adapter.main([cmd, '--publication-seconds', '1800'])


class PublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.home = Path(cls.temp.name)
        cls.base = isolated_checkout(cls.home/'base')
        cls.exported = cls.home/'export'
        approval = cls.home/'approval.json'; approve(FIXTURES/'direct-mono', approval)
        adapter.export(FIXTURES/'direct-mono', cls.exported, name='TEST ONLY RI-A', revision=1,
                       stem='ri_a', save_slot='ri_a', approval_path=approval,
                       category_id='voegel', categories_path=cls.base/'content/categories.json')
        cls.checked = difficulty_for_export(cls.exported)
        def prepared(root, journal, additions, **kwargs):
            cls.journal = deepcopy(journal)
            cls.additions = {}
            for i, (name, path) in enumerate(additions.items()):
                target = cls.home/('addition-' + str(i)); shutil.copyfile(path, target)
                cls.additions[name] = target
        with patch.object(tx, 'execute', side_effect=prepared):
            cr.registration(cls.exported, cls.base, apply=True, difficulty=cls.checked)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(); self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)/'checkout'
        shutil.copytree(self.base, self.root)
        self.clock = Clock()
        self.d = diag.Diagnostics('register')

    def execute(self, **kwargs):
        return pub.execute(self.root, deepcopy(self.journal), self.additions, **kwargs)

    def test_warning_then_success_and_noop_mtimes(self):
        def step(phase, name=None):
            if phase == 'P2': self.clock.now += 301
        with patch.object(diag.time, 'monotonic', self.clock), patch.object(pub, 'checkpoint', side_effect=step), diag.observe(self.d):
            self.execute()
        self.assertEqual(self.d.outcome, 'completed')
        self.assertEqual(self.d.limits[0]['protection_seconds'], 1800)
        self.assertFalse((self.root/tx.LOCK).exists())
        before = files(self.root)
        result = cr.registration(self.exported, self.root, apply=True)
        self.assertEqual(result['status'], 'no-op')
        self.assertEqual(files(self.root), before)

    def test_timeout_prevalidation_before_any_mutation(self):
        original = tx.validate_journal
        def validate(*args, **kwargs):
            self.clock.now += 1801
            return original(*args, **kwargs)
        before = files(self.root)
        with patch.object(diag.time, 'monotonic', self.clock), patch.object(tx, 'validate_journal', side_effect=validate), self.assertRaises(Aborted):
            self.execute()
        self.assertEqual(files(self.root), before)

    def test_expired_publication_has_independent_recovery_and_original_abort(self):
        def step(phase, name=None):
            if phase == 'P3': self.clock.now += 1801
            if phase == 'R0': self.clock.now += 301
        with patch.object(diag.time, 'monotonic', self.clock), patch.object(pub, 'checkpoint', side_effect=step), diag.observe(self.d), self.assertRaises(Aborted):
            self.execute()
        self.assertEqual(self.d.outcome, 'rolled-back')
        self.assertEqual([p['protection_seconds'] for p in self.d.limits], [1800, 1800])
        self.assertFalse((self.root/tx.LOCK).exists())
        self.assertEqual(cr.check_checkout(self.root)['entries'], [])

    def test_recovery_expiry_preserves_lock_and_repeated_recovery_finishes(self):
        def step(phase, name=None):
            if phase == 'P3': self.clock.now += 11
            if phase == 'R0': self.clock.now += 21
        with patch.object(diag.time, 'monotonic', self.clock), patch.object(pub, 'checkpoint', side_effect=step), self.assertRaises(Aborted):
            self.execute(publication_seconds=10, recovery_seconds=20)
        self.assertTrue((self.root/tx.LOCK).exists())
        self.assertEqual(cr.recover(self.root)['status'], 'rolled-back')

    def test_late_deadline_after_durable_p6_is_success_even_nested(self):
        original = pub.sync_directory; reached = False
        def checkpoint(phase, name=None):
            nonlocal reached
            if phase == 'P6': reached = True
        def sync(path):
            original(path)
            if reached and not (self.root/tx.LOCK).exists(): self.clock.now += 2000
        with patch.object(diag.time, 'monotonic', self.clock), patch.object(pub, 'checkpoint', side_effect=checkpoint), patch.object(pub, 'sync_directory', side_effect=sync), diag.observe(self.d), io.budget(300):
            self.execute()
        self.assertEqual(self.d.outcome, 'completed')
        self.assertTrue(cr.check_checkout(self.root)['entries'])

    def test_foreign_bytes_block_rollback_and_preserve_resource_exit(self):
        name = sorted(self.journal['additions'])[0]
        def step(phase, target=None):
            if phase == 'P3':
                (self.root/name).write_bytes(b'FOREIGN')
                self.clock.now += 1801
        with patch.object(diag.time, 'monotonic', self.clock), patch.object(pub, 'checkpoint', side_effect=step), self.assertRaises(Aborted):
            self.execute()
        before = files(self.root)
        with self.assertRaises(InvalidInput): cr.recover(self.root)
        self.assertEqual(files(self.root), before)

    def test_classification_current_legacy_fake_staging_and_other_override(self):
        lock = self.root/tx.LOCK
        for generation in (tx.FORMATS, tx.AT_FORMATS, tx.PREVIOUS_FORMATS, tx.LEGACY_FORMATS):
            value = deepcopy(self.journal); value['format'] = generation['registration']
            if not tx.modern(value): value.pop('replacements')
            lock.write_bytes(pub.journal_bytes(value))
            self.assertEqual(diag.classify(self.root)[0], 'registration')
        for value in ({'format': 'picross-registration-journal-v1'},
                      {**self.journal, 'operation': 'sync'},
                      {**self.journal, 'unknown': True}):
            lock.write_bytes(pub.journal_bytes(value)); before = files(self.root)
            with self.assertRaises(ValueError): cr.recover(self.root, recovery_seconds=1800)
            self.assertEqual(files(self.root), before)
        value = deepcopy(self.journal); value.update(operation='sync', format=tx.FORMATS['sync'])
        lock.write_bytes(pub.journal_bytes(value)); before = files(self.root)
        with self.assertRaisesRegex(InvalidInput, 'override'): cr.recover(self.root, recovery_seconds=1)
        self.assertEqual(files(self.root), before)
        lock.unlink()
        raw = pub.journal_bytes(self.journal)
        staging = self.root/('content/.registration-journal-' + io.checksum(raw) + '.tmp')
        staging.write_bytes(raw[:-3])
        with self.assertRaises(ValueError): cr.recover(self.root)
        staging.write_bytes(raw)
        self.assertEqual(cr.recover(self.root)['status'], 'rolled-back')
        self.assertFalse(staging.exists())

    def test_recovery_deadline_origin_includes_classification(self):
        with self.assertRaises(InterruptedError): self.execute(fail_step='crash')
        original = diag.classify
        def classify(root):
            value = original(root); self.clock.now += 11; return value
        before = files(self.root)
        with patch.object(diag.time, 'monotonic', self.clock), patch.object(diag, 'classify', side_effect=classify), self.assertRaises(Aborted):
            cr.recover(self.root, recovery_seconds=10)
        self.assertEqual(files(self.root), before)

    def test_other_recovery_retains_300_seconds_and_original_origin(self):
        journal = tx.prepare(self.root, tx.capture(self.root), {}, operation='sync')
        (self.root/tx.LOCK).write_bytes(pub.journal_bytes(journal))
        before = files(self.root)
        original = diag.classify
        def classify(root):
            value = original(root); self.clock.now += 301; return value
        with patch.object(diag.time, 'monotonic', self.clock), patch.object(diag, 'classify', side_effect=classify), diag.observe(self.d), self.assertRaises(Aborted):
            cr.recover(self.root)
        self.assertEqual(files(self.root), before)
        self.assertEqual(self.d.limits[-1]['protection_seconds'], 300)
        self.assertEqual(self.d.operation_class, 'sync-recovery')

    def test_original_journal_bytes_remain_bound_after_classification(self):
        with self.assertRaises(InterruptedError): self.execute(fail_step='crash')
        original = diag.classify
        def classify(root):
            value = original(root)
            (root/tx.LOCK).write_bytes(value[1] + b' ')
            return value
        with patch.object(diag, 'classify', side_effect=classify), self.assertRaisesRegex(InvalidInput, 'classification'):
            cr.recover(self.root)
        self.assertTrue((self.root/tx.LOCK).read_bytes().endswith(b' '))

    def test_cli_single_json_report_failure_does_not_reclassify_commit(self):
        out = streams.StringIO(); err = streams.StringIO()
        target = self.root.parent/'diagnostic.json'
        checked = self.root.parent/'checked.json'
        checked.write_text(json.dumps(self.checked))
        with redirect_stdout(out), redirect_stderr(err), patch.object(diag, 'write_report', side_effect=OSError('disk full')):
            code = adapter.main(['register', '--export', str(self.exported), '--checkout', str(self.root),
                                 '--difficulty', str(checked), '--operation-report', str(target)])
        result = json.loads(out.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(result['status'], 'registered')
        self.assertEqual(result['operation_diagnostics']['outcome'], 'completed')
        self.assertIn('diagnostic failure', err.getvalue())
