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


class Clock:
    now = 100.0

    def __call__(self):
        return self.now


def files(root):
    return {p.relative_to(root).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
            for p in root.rglob('*') if p.is_file()}


class BudgetTests(unittest.TestCase):
    def test_complete_catalog_registration_budget_before_lock(self):
        from tests.puzzle_production.current_fixtures import checkout, make
        from tools.puzzle_production import catalog_integration, current_registration
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            root = checkout(home / "repo")
            source = make(home / "input")
            before = files(root)
            with patch.object(current_registration, "LIMIT", 2048), self.assertRaisesRegex(ValueError, "journal"):
                catalog_integration.integrate(source, root, apply=True)
            self.assertEqual(before, files(root))

    def test_invalid_values_and_plan_update_reject_before_io(self):
        for value in (True, False, 0, -1, float('nan'), float('inf'), '1800', 10 ** 1000):
            with self.subTest(value=str(value)[:20]), patch.object(tx, 'capture', side_effect=AssertionError('I/O')):
                for name in ('publication_seconds', 'recovery_seconds'):
                    with self.assertRaises(InvalidInput):
                        cr.registration(Path('missing'), Path('missing'), apply=True, **{name: value})
                with self.assertRaises(InvalidInput):
                    cr.recover(Path('missing'), recovery_seconds=value)
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

    def test_complete_checks_count_only_successful_returns(self):
        clock = Clock()
        with patch.object(diag.time, 'monotonic', clock):
            d = diag.Diagnostics('plan')
            with diag.observe(d):
                def check(failure=None):
                    clock.now += 7
                    if failure: raise failure
                    return 'checked'
                self.assertEqual(diag.candidate_check(check), 'checked')
                progress = dict(d.last_progress)
                for failure in (InvalidInput('bad bytes'), Aborted('inside proof'), OSError('read failed')):
                    with self.assertRaises(type(failure)):
                        diag.candidate_check(check, failure)
                    self.assertEqual(d.last_progress, progress)
            self.assertEqual(d.counters['candidate_proof_check_attempts'], 4)
            self.assertEqual(d.counters['full_candidate_proof_checks'], 1)
            self.assertEqual(d.counters['completed_steps'], 1)
            self.assertEqual(d.result()['phases'][0]['seconds'], 28)

    def test_classification_cannot_revive_expired_frame_or_outer_deadline(self):
        clock = Clock()
        with patch.object(diag.time, 'monotonic', clock):
            for outer in (False, True):
                with self.subTest(outer=outer), self.assertRaises(Aborted):
                    with io.budget(10 if outer else 300), diag.operation('Recovery', 300, 'classification') as active:
                        clock.now += 11 if outer else 301
                        active.classified_limit(1800, 'registration-default')
            with self.assertRaises(Aborted), diag.operation('Publication', 10, 'outer'):
                with diag.operation('Recovery', 300, 'classification') as active:
                    clock.now += 9
                    active.classified_limit(1800, 'registration-default')
                    clock.now += 2
                    io.tick()

    def test_read_keeps_type_alias_hardlink_and_fresh_identity_guards(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); target = root/'sample'; target.write_bytes(b'own')
            with patch.object(io, 'safe', wraps=io.safe) as safe:
                self.assertEqual(tx.read(root, 'sample'), b'own')
                self.assertGreaterEqual(safe.call_count, 2)
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
