"""RI-B: small synthetic bindings and representative publication/recovery paths."""
from copy import copy, deepcopy
import io as streams
import json
import os
from pathlib import Path
import pickle
import shutil
import tempfile
import unittest
from unittest.mock import patch

from tools.puzzle_production import catalog_publication as pub, catalog_transaction as tx
from tools.puzzle_production import content_registry as cr, operation_diagnostics as diag
from tools.puzzle_production import registration_verification as verification, target_adapter as adapter
from tools.puzzle_production.contract import InvalidInput, Aborted
from tools.puzzle_production.za1_fixtures import FIXTURES, approve, isolated_checkout, difficulty_for_export


def files(root):
    return {p.relative_to(root).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
            for p in root.rglob('*') if p.is_file()}


class VerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.home = Path(cls.temp.name)
        package = cls.home / 'input'
        shutil.copytree(FIXTURES / 'direct-mono', package)
        approve(package, cls.home / 'approval.json')
        cls.empty = isolated_checkout(cls.home / 'empty')
        cls.exported = cls.home / 'export'
        adapter.export(package, cls.exported, name='TEST ONLY RI-B', revision=1,
                       stem='ri_b', save_slot='ri_b', approval_path=cls.home / 'approval.json',
                       category_id='voegel', categories_path=cls.empty / 'content/categories.json')
        cls.rating = difficulty_for_export(cls.exported)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.checkout = self.root / 'checkout'
        self.export = self.root / 'export'
        shutil.copytree(self.empty, self.checkout)
        shutil.copytree(self.exported, self.export)

    def register(self, **kwargs):
        return cr.registration(self.export, self.checkout, apply=True, difficulty=self.rating, **kwargs)

    def intercepted(self, callback):
        def execute(root, journal, additions, **kwargs):
            context = kwargs['_verification']
            callback(context, root, journal, additions)
        with patch.object(tx, 'execute', side_effect=execute):
            return self.register()

    def test_positive_two_full_checks_and_unchanged_guards_plan_noop(self):
        before = files(self.checkout)
        d = diag.Diagnostics('plan', stderr=streams.StringIO())
        with diag.observe(d):
            self.assertEqual(cr.registration(self.export, self.checkout, difficulty=self.rating)['status'], 'planned')
        self.assertEqual(d.counters['full_candidate_proof_checks'], 2)
        self.assertEqual(files(self.checkout), before)
        d = diag.Diagnostics('register', stderr=streams.StringIO())
        with diag.observe(d), patch.object(pub, 'guard', wraps=pub.guard) as guard:
            self.assertEqual(self.register()['status'], 'registered')
        self.assertEqual(d.counters['full_candidate_proof_checks'], 2)
        self.assertEqual(d.counters['verified_package_reuses'], 2)
        self.assertEqual(guard.call_count, 80)
        entry = cr.check_checkout(self.checkout, replay=True)['entries'][0]
        for kind in ('definition', 'reveal'):
            self.assertEqual((self.checkout / ('game/' + entry[kind])).read_bytes(),
                             (self.export / ('runtime/' + entry[kind])).read_bytes())
        after = files(self.checkout)
        self.assertEqual(self.register()['status'], 'no-op')
        self.assertEqual(files(self.checkout), after)
        self.assertFalse(verification._active)

    def test_staging_bytes_approval_inventory_and_same_byte_exchange(self):
        for mutation in ('bytes', 'approval', 'extra', 'missing', 'empty-dir', 'file-exchange', 'stage-exchange'):
            with self.subTest(mutation=mutation):
                before = files(self.checkout)
                def change(context, root, journal, additions):
                    stage = context.stage
                    leaf = stage / ('approval.json' if mutation == 'approval' else 'usage.txt')
                    if mutation in ('bytes', 'approval'): leaf.write_bytes(leaf.read_bytes() + b' ')
                    elif mutation == 'extra': (stage / 'foreign.txt').write_bytes(b'foreign')
                    elif mutation == 'missing': leaf.unlink()
                    elif mutation == 'empty-dir': (stage / 'foreign').mkdir()
                    elif mutation == 'file-exchange':
                        other = stage / 'replacement'
                        shutil.copy2(leaf, other); os.replace(other, leaf)
                    else:
                        moved = stage.with_name('exchanged')
                        stage.rename(moved); shutil.copytree(moved, stage)
                    with self.assertRaises(InvalidInput): context.writer(root, journal, additions)
                    with self.assertRaises(InvalidInput): verification.require_context(context)
                    raise InvalidInput('expected synthetic rejection')
                with self.assertRaises(InvalidInput): self.intercepted(change)
                self.assertEqual(files(self.checkout), before)

    def test_source_journal_method_and_external_pass_cannot_reuse(self):
        for mutation in ('category', 'journal', 'mapping', 'method', 'original', 'checkout'):
            with self.subTest(mutation=mutation):
                before = files(self.checkout)
                def change(context, root, journal, additions):
                    if mutation == 'category':
                        target = root / 'content/categories.json'; target.write_bytes(target.read_bytes() + b' ')
                    elif mutation == 'journal': journal['new'][tx.RUNTIME] += ' '
                    elif mutation == 'mapping': additions[next(iter(additions))] = self.export / 'usage.txt'
                    elif mutation == 'original':
                        target = self.export / 'approval.json'; target.write_bytes(target.read_bytes() + b' ')
                    elif mutation == 'checkout':
                        moved = root.with_name('exchanged-checkout')
                        root.rename(moved); shutil.copytree(moved, root)
                    if mutation == 'category':
                        # Global source guards remain the independent authority.
                        with self.assertRaises(InvalidInput): pub.execute(root, journal, additions, _verification=context)
                    elif mutation == 'method':
                        with patch.object(verification, '_methods', return_value=('different actual bytes',)):
                            with self.assertRaises(InvalidInput): context.writer(root, journal, additions)
                    else:
                        with self.assertRaises(InvalidInput): context.writer(root, journal, additions)
                    raise InvalidInput('expected synthetic rejection')
                with self.assertRaises(InvalidInput): self.intercepted(change)
                # Restore only our own synthetic modifications for the next case.
                if mutation == 'category': (self.checkout / 'content/categories.json').write_bytes(before['content/categories.json'][0])
                if mutation == 'original': shutil.copy2(self.exported / 'approval.json', self.export / 'approval.json')
                self.assertFalse((self.checkout / tx.LOCK).exists())
        with self.assertRaises(InvalidInput):
            cr.check_checkout(self.checkout, replay=True, _verification={'pass': True})

    def test_lifetime_process_thread_copy_and_failed_replay(self):
        kept = []
        def examine(context, root, journal, additions):
            kept.append(context)
            for clone in (copy, deepcopy, pickle.dumps):
                with self.assertRaises(TypeError): clone(context)
            for attribute in ('getpid', 'get_ident'):
                module = verification.os if attribute == 'getpid' else verification.threading
                original = getattr(module, attribute)()
                with patch.object(module, attribute, return_value=original + 1):
                    with self.assertRaises(InvalidInput): verification.require_context(context)
            context.writer(root, journal, additions)
        self.intercepted(examine)
        with self.assertRaises(InvalidInput): verification.require_context(kept[0])
        with self.assertRaises(InvalidInput): verification.require_context(object.__new__(verification._Verification))
        actual = adapter.verify_export
        calls = 0
        def fail_stage(path):
            nonlocal calls
            calls += 1
            if calls == 2: raise InvalidInput('failed independent replay')
            return actual(path)
        with patch.object(adapter, 'verify_export', side_effect=fail_stage), self.assertRaises(InvalidInput): self.register()
        self.assertFalse(verification._active)

    def test_checked_source_exchange_and_written_package_readback(self):
        checked = self.root / 'checked.json'
        checked.write_text(json.dumps(self.rating), encoding='utf-8')
        def exchange(root, journal, additions, **kwargs):
            context = kwargs['_verification']
            replacement = self.root / 'replacement.json'
            shutil.copy2(checked, replacement); os.replace(replacement, checked)
            with self.assertRaises(InvalidInput): context.writer(root, journal, additions)
            raise InvalidInput('checked input exchanged')
        with patch.object(tx, 'execute', side_effect=exchange), self.assertRaises(InvalidInput):
            cr.registration(self.export, self.checkout, apply=True, difficulty=checked)
        def readback(context, root, journal, additions):
            package = root / context.package
            shutil.copytree(context.stage, package)
            context.written(root, context.package, context.raw)
            leaf = package / 'approval.json'
            replacement = package / 'replacement.json'
            shutil.copy2(leaf, replacement); os.replace(replacement, leaf)
            with self.assertRaises(InvalidInput): context.written(root, context.package, context.raw)
            raise InvalidInput('published input exchanged')
        with self.assertRaises(InvalidInput): self.intercepted(readback)
        self.assertFalse((self.checkout / tx.LOCK).exists())

    def test_error_abort_and_crash_recovery_never_use_context(self):
        before = files(self.checkout)
        for failure in ('files', 'crash'):
            with self.subTest(failure=failure):
                with self.assertRaises(OSError if failure == 'files' else InterruptedError): self.register(fail_step=failure)
                self.assertFalse(verification._active)
                if failure == 'crash':
                    journal = json.loads((self.checkout / tx.LOCK).read_bytes())
                    target = next(self.checkout / n for n in journal['additions'] if (self.checkout / n).is_file())
                    own = target.read_bytes()
                    target.write_bytes(b'foreign')
                    foreign = files(self.checkout)
                    with self.assertRaises(InvalidInput): cr.recover(self.checkout)
                    self.assertEqual(files(self.checkout), foreign)
                    target.write_bytes(own)
                    with patch.object(verification._Verification, 'written', side_effect=AssertionError('context in recovery')):
                        self.assertEqual(cr.recover(self.checkout)['status'], 'rolled-back')
                self.assertEqual({n: b for n, (b, _) in files(self.checkout).items()},
                                 {n: b for n, (b, _) in before.items()})
        original = pub.checkpoint
        def abort(phase, name=None):
            original(phase, name)
            if phase == 'P3': raise Aborted('synthetic resource stop')
        with patch.object(pub, 'checkpoint', side_effect=abort), self.assertRaises(Aborted): self.register()
        self.assertFalse((self.checkout / tx.LOCK).exists())
        self.assertFalse(verification._active)
