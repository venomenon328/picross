"""RI-C change-scoped cases; synthetic bytes, real filesystem publication."""
from copy import deepcopy
from contextlib import nullcontext
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from tests.puzzle_production import test_registration_budgets as fixture
from tests.puzzle_production import catalog_fixtures
from tools.puzzle_production import catalog_publication as pub, catalog_transaction as tx
from tools.puzzle_production import registration_publication as phased, catalog_io as io
from tools.puzzle_production import content_registry as cr, operation_diagnostics as diag
from tools.puzzle_production import difficulty_rating, sd2_rating_freeze
from tools.puzzle_production import target_adapter as adapter, za1_fixtures as za1
from tools.puzzle_production.contract import InvalidInput, Aborted


class PublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture.PublicationTests.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name)
        self.root = self.home / 'checkout'
        shutil.copytree(self.base, self.root)

    def execute(self):
        pub.execute(self.root, deepcopy(self.journal), self.additions)

    def reset(self, name):
        self.root = self.home / name
        shutil.copytree(self.base, self.root)

    def test_every_full_boundary_preserves_foreign_bytes_and_exact_phase(self):
        for boundary in ('G0', 'G2', 'G5a', 'G5b', 'G6'):
            with self.subTest(boundary=boundary):
                self.reset(boundary)
                captured = []
                def foreign(phase, name=None):
                    if phase == boundary:
                        p = self.root / tx.categories.PATH
                        p.write_bytes(p.read_bytes() + b' ')
                        captured.append(fixture.files(self.root))
                with patch.object(pub, 'checkpoint', side_effect=foreign), self.assertRaises(InvalidInput):
                    self.execute()
                self.assertEqual(len(captured), 1)
                self.assertEqual(fixture.files(self.root), captured[0])
                self.assertEqual((self.root / tx.LOCK).exists(), boundary != 'G0')

    def test_target_temp_staging_parent_and_phase_changes_stop_locally(self):
        addition = sorted(self.journal['additions'])[0]
        text = sorted(n for n in self.journal['old'] if n != tx.RUNTIME and
                      self.journal['old'][n] != self.journal['new'][n])[0]
        for kind in ('addition', 'text', 'temporary', 'journal', 'staging', 'directory', 'hardlink', 'alias'):
            with self.subTest(kind=kind):
                self.reset(kind)
                captured = []
                def foreign(phase, name=None):
                    if captured or phase != 'temp-complete' or name != (text if kind == 'text' else addition):
                        return
                    temporary = pub.inventory(self.journal, pub.journal_bytes(self.journal))[name]
                    p = self.root / (temporary if kind == 'temporary' else tx.LOCK if kind == 'journal' else name)
                    if kind == 'staging':
                        p = self.root / 'content/.registration-journal-foreign.tmp'
                    elif kind == 'directory':
                        p = p.parent / 'foreign-directory'; p.mkdir()
                    elif kind == 'hardlink':
                        foreign_source = self.home / ('outside-' + kind); foreign_source.write_bytes(b'FOREIGN')
                        os.link(foreign_source, p)
                    elif kind == 'alias':
                        p = p.with_name(p.name.upper()); p.write_bytes(b'FOREIGN')
                    else:
                        p.write_bytes(b'FOREIGN')
                    if kind == 'staging': p.write_bytes(b'FOREIGN')
                    captured.append(fixture.files(self.root))
                with patch.object(pub, 'checkpoint', side_effect=foreign), self.assertRaises((ValueError, OSError)):
                    self.execute()
                self.assertEqual(len(captured), 1)
                self.assertEqual(fixture.files(self.root), captured[0])
                self.assertTrue((self.root / tx.LOCK).exists())

    def test_guards_are_outside_file_loops_runtime_last_and_recovery_independent(self):
        boundaries, writes = [], []
        in_write = False
        original_write, original_guard = pub.write, pub.guard
        def write(root, name, *args, **kwargs):
            nonlocal in_write
            writes.append(name); in_write = True
            try: return original_write(root, name, *args, **kwargs)
            finally: in_write = False
        def guard(*args, **kwargs):
            self.assertFalse(in_write, 'Full catalog walk inside file publication')
            return original_guard(*args, **kwargs)
        def checkpoint(phase, name=None):
            if phase.startswith('G'): boundaries.append(phase)
        with patch.object(pub, 'write', side_effect=write), patch.object(pub, 'guard', side_effect=guard), patch.object(pub, 'checkpoint', side_effect=checkpoint):
            self.execute()
        self.assertEqual(boundaries, ['G0', 'G2', 'G5a', 'G5b', 'G6'])
        self.assertEqual(writes[-1], tx.RUNTIME)
        self.reset('recovery')
        with self.assertRaises(InterruptedError):
            pub.execute(self.root, deepcopy(self.journal), self.additions, fail_step='crash-runtime')
        boundaries.clear(); writes.clear()
        with patch.object(pub, 'write', side_effect=write), patch.object(pub, 'guard', side_effect=guard), patch.object(pub, 'checkpoint', side_effect=checkpoint):
            cr.recover(self.root)
        self.assertEqual(boundaries, ['GR0', 'GR2'])
        self.assertEqual(writes[-1], tx.RUNTIME)
        self.assertEqual(cr.check_checkout(self.root)['entries'], [])

    def test_valid_but_wrong_phase_bytes_and_changed_staged_source(self):
        for boundary, side in (('G2', 'new'), ('G5b', 'old')):
            with self.subTest(boundary=boundary):
                self.reset('wrong-' + boundary)
                captured = []
                def phase_change(at, name=None):
                    if at == boundary:
                        (self.root / tx.RUNTIME).write_text(self.journal[side][tx.RUNTIME], encoding='utf-8', newline='')
                        captured.append(fixture.files(self.root))
                # Suppress automatic recovery only to inspect the forward exact-
                # phase rejection. These bytes are independently valid recovery
                # states; recovery is allowed to restore them after this check.
                with patch.object(pub, 'checkpoint', side_effect=phase_change), \
                     patch.object(cr, 'recover', side_effect=InterruptedError('inspect retained journal')), \
                     self.assertRaises((InvalidInput, InterruptedError)):
                    self.execute()
                self.assertEqual(fixture.files(self.root), captured[0])
                cr.recover(self.root)
        self.reset('staged-source')
        name = sorted(self.journal['additions'])[0]
        source = self.additions[name]; original = source.read_bytes(); reached = []
        def change(at, target=None):
            if at == 'temp-complete' and target == name and not reached:
                source.write_bytes(b'FOREIGN'); reached.append(True)
        try:
            with patch.object(pub, 'checkpoint', side_effect=change), self.assertRaises(InvalidInput): self.execute()
            self.assertEqual(reached, [True])
            self.assertEqual(source.read_bytes(), b'FOREIGN')
            self.assertFalse((self.root / tx.LOCK).exists())
            self.assertEqual(cr.check_checkout(self.root)['entries'], [])
        finally:
            source.write_bytes(original)

    def test_interruptions_staging_and_repeated_recovery(self):
        phases = [(p, 1) for p in ('P0', 'journal-prefix', 'journal-complete', 'P1', 'P2', 'P3', 'P4', 'G5a', 'P5', 'P6')]
        for phase, occurrence in [*phases, ('P3', 2), ('P4', 2)]:
            with self.subTest(phase=phase, occurrence=occurrence):
                self.reset(phase + str(occurrence))
                seen = 0
                def stop(at, name=None):
                    nonlocal seen
                    if at == phase:
                        seen += 1
                        if seen == occurrence: raise InterruptedError('controlled process boundary')
                with patch.object(io, 'CHUNK', 128) if phase == 'journal-prefix' else nullcontext():
                    with patch.object(pub, 'checkpoint', side_effect=stop), self.assertRaises(InterruptedError): self.execute()
                if phase == 'P0':
                    self.assertFalse((self.root / tx.LOCK).exists())
                elif phase == 'journal-prefix':
                    before = fixture.files(self.root)
                    with self.assertRaises(ValueError): cr.recover(self.root)
                    self.assertEqual(fixture.files(self.root), before)
                else:
                    cr.recover(self.root)
                if phase != 'journal-prefix':
                    self.assertEqual({n: v[0] for n, v in fixture.files(self.root).items()},
                                     {n: v[0] for n, v in fixture.files(self.base).items()})
        for phase in ('GR0', 'R0', 'R1-text', 'R1-addition', 'R1-runtime', 'R2', 'GR2'):
            with self.subTest(recovery=phase):
                self.reset(phase)
                with self.assertRaises(InterruptedError):
                    pub.execute(self.root, deepcopy(self.journal), self.additions, fail_step='crash-runtime')
                raw = (self.root / tx.LOCK).read_bytes()
                def stop(at, name=None):
                    if at == phase: raise InterruptedError('second interruption')
                with patch.object(pub, 'checkpoint', side_effect=stop), self.assertRaises(InterruptedError): cr.recover(self.root)
                self.assertEqual((self.root / tx.LOCK).read_bytes(), raw)
                cr.recover(self.root)
                self.assertEqual(cr.check_checkout(self.root)['entries'], [])

    def test_controlled_deadlines_at_stage_lock_file_and_commit_boundaries(self):
        for phase in ('journal-complete', 'P1', 'P2', 'P3', 'P4', 'G5a', 'P5', 'P6'):
            with self.subTest(phase=phase):
                self.reset('deadline-' + phase)
                clock = fixture.Clock()
                def expire(at, name=None):
                    if at == phase: clock.now += 1801
                with patch.object(diag.time, 'monotonic', clock), patch.object(pub, 'checkpoint', side_effect=expire), self.assertRaises(Aborted):
                    self.execute()
                if (self.root / tx.LOCK).exists() or pub.staging(self.root): cr.recover(self.root)
                self.assertEqual(cr.check_checkout(self.root)['entries'], [])

    def test_recovery_foreign_global_and_local_bytes_never_get_relabelled(self):
        for phase in ('GR0', 'R1-text', 'GR2'):
            with self.subTest(phase=phase):
                self.reset(phase)
                with self.assertRaises(InterruptedError):
                    pub.execute(self.root, deepcopy(self.journal), self.additions, fail_step='crash-runtime')
                captured = []
                def foreign(at, name=None):
                    if at == phase and not captured:
                        p = self.root / (tx.RUNTIME if phase == 'R1-text' else tx.categories.PATH)
                        p.write_bytes(b'FOREIGN')
                        captured.append(p)
                with patch.object(pub, 'checkpoint', side_effect=foreign), self.assertRaises(InvalidInput): cr.recover(self.root)
                self.assertEqual(captured[0].read_bytes(), b'FOREIGN')
                before = fixture.files(self.root)
                with self.assertRaises(InvalidInput): cr.recover(self.root)
                self.assertEqual(fixture.files(self.root), before)

    def test_real_kill_then_rekill_and_signal_keep_same_recoverable_journal(self):
        config = self.home / 'input.json'
        config.write_text(json.dumps({'journal': self.journal, 'additions': {n: str(p) for n, p in self.additions.items()}}))
        code = '''
import json, signal, sys, time
from pathlib import Path
from tools.puzzle_production import catalog_publication as pub, content_registry as cr
root, config, marker = map(Path, sys.argv[1:4])
phase, operation, mode = sys.argv[4:]
if mode == 'signal':
 def abort(*args): raise KeyboardInterrupt('actual SIGTERM')
 signal.signal(signal.SIGTERM, abort)
def checkpoint(at, name=None):
 if at == phase:
  marker.write_text('ready')
  while True: time.sleep(.02)
pub.checkpoint = checkpoint
value = json.loads(config.read_text())
if operation == 'publish': pub.execute(root, value['journal'], {n: Path(p) for n,p in value['additions'].items()})
else: cr.recover(root)
'''
        for phase, operation, mode in (('P5', 'publish', 'kill'), ('R1-addition', 'recover', 'kill'), ('R0', 'recover', 'signal')):
            marker = self.home / (phase + '.ready')
            with subprocess.Popen([sys.executable, '-c', code, str(self.root), str(config), str(marker), phase, operation, mode],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) as process:
                try:
                    deadline = time.monotonic() + 90
                    while not marker.exists() and process.poll() is None and time.monotonic() < deadline: time.sleep(.02)
                    self.assertTrue(marker.exists(), 'Real child did not reach ' + phase)
                    raw = (self.root / tx.LOCK).read_bytes()
                    if mode == 'signal': process.send_signal(signal.SIGTERM)
                    else: process.kill()
                    process.wait(timeout=20)
                    self.assertNotEqual(process.returncode, 0)
                    self.assertEqual((self.root / tx.LOCK).read_bytes(), raw)
                finally:
                    if process.poll() is None: process.kill(); process.wait()
        cr.recover(self.root)
        self.assertEqual(cr.check_checkout(self.root)['entries'], [])

    def test_current_and_legacy_dispatch_is_explicit(self):
        for generation in range(1, 7):
            j = {**self.journal, 'format': 'picross-registration-journal-v' + str(generation)}
            self.assertEqual(phased.supports(j), generation == 6)
        for operation, format_name in tx.FORMATS.items():
            self.assertEqual(phased.supports({'format': format_name, 'operation': operation}), operation == 'registration')


class SourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(); cls.home = Path(cls.temp.name)
        catalog_fixtures.registered(cls.home / 'existing', stem='ri_c_old', save_slot='ri_c_old')
        cls.base = cls.home / 'existing/full-base'
        source = za1.FIXTURES / 'direct-color'
        approval = cls.home / 'approval.json'; za1.approve(source, approval)
        exported = cls.home / 'export'
        adapter.export(source, exported, name='TEST ONLY RI-C', revision=1, stem='ri_c_new', save_slot='ri_c_new',
                       approval_path=approval, category_id='voegel', categories_path=cls.base / 'content/categories.json')
        def prepare(root, journal, additions, **kwargs): cls.journal = deepcopy(journal)
        with patch.object(tx, 'execute', side_effect=prepare):
            cr.registration(exported, cls.base, apply=True, difficulty=za1.difficulty_for_export(exported))

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def test_all_text_and_retained_authorities_and_absences_are_fresh(self):
        for name in sorted(set(self.journal['old']) | set(self.journal['retained'])):
            with self.subTest(source=name), tempfile.TemporaryDirectory() as temp:
                root = Path(temp) / 'checkout'; shutil.copytree(self.base, root)
                state = phased.Guards(root, self.journal, pub.journal_bytes(self.journal))
                target = root / name; target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((target.read_bytes() if target.exists() else b'') + b'FOREIGN')
                before = fixture.files(root)
                with self.assertRaises(ValueError): state.full('G0', before_lock=True)
                self.assertEqual(fixture.files(root), before)

    def test_complete_namespaces_and_actual_freeze_sources(self):
        package = json.loads(self.journal['old'][tx.REGISTRY])['entries'][0]['production']['package']
        for name in (package + '/unknown', 'content/difficulty/pz-foreign', 'content/difficulty/reports/foreign',
                     'content/added/unknown', 'content/reveals/unknown', 'content/.registration-foreign.tmp'):
            with self.subTest(namespace=name), tempfile.TemporaryDirectory() as temp:
                root = Path(temp) / 'checkout'; shutil.copytree(self.base, root)
                target = root / name; target.mkdir(parents=True)
                state = phased.Guards(root, self.journal, pub.journal_bytes(self.journal))
                with self.assertRaises(ValueError): state.full('G0', before_lock=True)
                self.assertTrue(target.is_dir())
        for module, filename in ((difficulty_rating, 'difficulty_method_0_3.json'), (sd2_rating_freeze, 'sd2_method_0_4.json')):
            with self.subTest(freeze=filename), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                shutil.copytree(module._ROOT, root / 'methods')
                path = root / 'methods' / filename; path.write_bytes(b'{}')
                state = phased.Guards(self.base, self.journal, pub.journal_bytes(self.journal))
                with patch.object(module, '_ROOT', root / 'methods'), self.assertRaises(ValueError):
                    state.full('G0', before_lock=True)
