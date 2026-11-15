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

    def test_new_text_race_remains_atomic_no_replace(self):
        name = sorted(n for n in self.journal['old'] if self.journal['old'][n] is None
                      and self.journal['new'][n] is not None)[0]
        target = self.root / name
        rename = pub.rename; reached = []
        def collide(source, destination, *, replace):
            if destination == target and not reached:
                self.assertFalse(replace, 'New text must never become a replace based on a later exists()')
                target.write_bytes(b'FOREIGN'); reached.append(True)
            return rename(source, destination, replace=replace)
        with patch.object(pub, 'rename', side_effect=collide), self.assertRaises((ValueError, OSError)):
            self.execute()
        self.assertEqual(reached, [True])
        self.assertEqual(target.read_bytes(), b'FOREIGN')
        self.assertTrue((self.root / tx.LOCK).exists())

    def test_valid_empty_rollback_namespaces_do_not_block_next_registration(self):
        names = ('content/difficulty/pz-prior-rollback', 'content/difficulty/reports/prior-rollback')
        for name in names: (self.root / name).mkdir(parents=True)
        self.assertEqual(cr.check_checkout(self.root)['entries'], [])
        self.execute()
        self.assertEqual(len(cr.check_checkout(self.root)['entries']), 1)
        for name in names:
            self.assertTrue((self.root / name).is_dir())
            self.assertEqual(list((self.root / name).iterdir()), [])

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
        for generation in range(1, 11):
            j = {**self.journal, 'format': 'picross-registration-journal-v' + str(generation)}
            self.assertEqual(phased.supports(j), generation in (6, 7, 8, 9))
        for generation in (tx.FORMATS, tx.BACKGROUND_FORMATS, tx.PE_FORMATS, tx.IMAGE_FORMATS):
            for operation, format_name in generation.items():
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

    def test_new_registration_replays_only_new_export_and_guards_old_bytes(self):
        """A historical producer mismatch must not veto an unrelated new ID."""
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'checkout'
            shutil.copytree(self.base, root)
            old = cr.check_checkout(root)['entries'][0]
            old_package = (root / old['production']['package']).resolve()
            self.assertTrue((old_package / 'manifest.json').exists())

            original_verify = adapter.verify_export
            calls = {'old': 0, 'new': 0}
            def verify(path):
                if Path(path).resolve() == old_package:
                    calls['old'] += 1
                    raise InvalidInput('INT-B02 simulated old producer mismatch')
                calls['new'] += 1
                return original_verify(path)

            with patch.object(adapter, 'verify_export', side_effect=verify):
                self.assertEqual(
                    cr.registration(self.home / 'export', root, apply=True,
                                    difficulty=za1.difficulty_for_export(self.home / 'export'))['status'],
                    'registered')
                self.assertEqual(calls['old'], 0)
                self.assertGreaterEqual(calls['new'], 2)
                # Deliberate historical full audits stay strict and opt-in.
                with self.assertRaisesRegex(InvalidInput, 'INT-B02 simulated'):
                    cr.check_checkout(root, replay=True)
                self.assertEqual(calls['old'], 1)

            with self.assertRaises(InvalidInput):
                cr.check_checkout(root, replay=True, replay_package='content/packages/pz-missing/r01')
            with self.assertRaises(InvalidInput):
                cr.check_checkout(root, replay_package=old['production']['package'])

            # Omitting old proof replay must not weaken its complete stored
            # package inventory or the current live/catalog source checks.
            stale = old_package / 'usage.txt'
            stale.write_bytes(stale.read_bytes() + b'FOREIGN')
            with self.assertRaises(InvalidInput):
                cr.check_checkout(root, replay=False)

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
        for name in (package + '/unknown', 'content/difficulty/pz-foreign/unknown', 'content/difficulty/reports/foreign/unknown',
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



class CurrentGenerationTests(unittest.TestCase):
    """RI-V9: actual public producer on a slim v4/v8 mixed synthetic catalog."""
    @classmethod
    def setUpClass(cls):
        from tests.puzzle_production.background_catalog_fixtures import prepare
        from tools.puzzle_production import catalog_background as bg, editor_change as edit
        from tools.puzzle_production.contract import write_json
        owner = unittest.TestCase(); cls.addClassCleanup(owner.doCleanups)
        old = prepare(owner, 'selected', registered=True)
        cls.base = old.checkout
        cls.home = old.case.root
        # A second, compact old entry coexists with the complete v6 production.
        catalog_fixtures.registered(cls.home / 'mono', stem='v9_old', save_slot='v9_old')
        za1.rated_registration(cls.home / 'mono/export', cls.base, apply=True)
        mono = za1.difficulty_for_export(cls.home / 'mono/export')['current_source']['id']
        catalog_fixtures.compact(cls.base, [mono])
        value = cr.check_checkout(cls.base)
        runtime = json.loads((cls.base / cr.RUNTIME).read_bytes())
        runtime['format'] = cr.IMAGE_RUNTIME_FORMAT
        refs = bg.index(value)
        value['backgrounds'] = []
        for entry in value['entries']:
            row = next(r for r in runtime['entries'] if r['id'] == entry['id'])
            definition = (cls.base / 'game' / entry['definition']).read_bytes()
            reveal = edit._record(entry, definition, None, 'reveal', {
                'image_revision': 2, 'asset': bg.ref('game/' + row['reveal'],
                    (cls.base / 'game' / row['reveal']).read_bytes())})
            if entry['id'] in refs:
                source = json.loads((cls.base / bg.path(entry['id'])).read_bytes())
                current = bg.current(source)
                image = {'image_revision': 2, 'status': current['decision']['outcome'],
                         'asset': current['asset']}
            else:
                image = {'image_revision': 2, 'status': 'standard', 'asset': None}
            source = edit._record(entry, definition, None, 'background', image)
            write_json(cls.base / ('content/reveals/' + entry['id'] + '.json'), reveal)
            write_json(cls.base / bg.path(entry['id']), source)
            value['backgrounds'].append({'id': entry['id'], 'source': bg.ref(bg.path(entry['id']), bg.encoded(source))})
            row['background'] = {**image, 'asset': {**image['asset'], 'file': image['asset']['file'].removeprefix('game/')}
                                 if image['asset'] else None}
        write_json(cls.base / cr.REGISTRY, value)
        write_json(cls.base / cr.RUNTIME, runtime)
        cls.old_id = old.manifest['definition_id']
        cls.old_package = next(e['production']['package'] for e in value['entries'] if e['id'] == cls.old_id)
        (cls.base / cls.old_package / 'external').mkdir(exist_ok=True)
        request = {'id': cls.old_id, 'metadata': {'name': 'Manuell geändert', 'category_id': 'voegel'},
                   'text': None, 'profile': None, 'reveal': None, 'background': None}
        edit.apply(cls.base, edit.plan(cls.base, request))
        cr.check_checkout(cls.base)
        cls.export = cls.home / 'new-color'
        approval = cls.home / 'color-approval.json'; za1.approve(za1.FIXTURES / 'direct-color', approval)
        adapter.export(za1.FIXTURES / 'direct-color', cls.export, name='TEST ONLY v9',
                       revision=1, stem='v9_new', save_slot='v9_new', approval_path=approval,
                       category_id='voegel', categories_path=cls.base / 'content/categories.json')
        cls.difficulty = za1.difficulty_for_export(cls.export)

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / 'checkout'
        shutil.copytree(self.base, self.root)

    def register(self, **kwargs):
        return cr.registration(self.export, self.root, apply=True, difficulty=self.difficulty, **kwargs)

    def test_generated_v9_mixed_slim_sources_no_old_replay_and_noop(self):
        from tools.puzzle_production import catalog_background as bg
        before = fixture.files(self.root)
        historical = {str((self.root / e['production']['package']).resolve()) for e in cr.check_checkout(self.root)['entries']}
        original = adapter.verify_export
        calls = {'old': 0, 'new': 0}
        def verify(path):
            if str(Path(path).resolve()) in historical:
                calls['old'] += 1
                raise InvalidInput('RI-V9 intentionally unreproducible old producer')
            calls['new'] += 1
            return original(path)
        observed = []
        def writer(root, j, additions, **kwargs):
            observed.append(deepcopy(j))
            return phased_execute(root, j, additions, **kwargs)
        phased_execute = phased.execute
        with patch.object(adapter, 'verify_export', side_effect=verify), patch.object(phased, 'execute', side_effect=writer):
            self.assertEqual(self.register()['status'], 'registered')
            self.assertEqual(calls['old'], 0)
            self.assertGreaterEqual(calls['new'], 2)
            journal, = observed
            self.assertEqual(journal['format'], tx.IMAGE_FORMATS['registration'])
            self.assertEqual(json.loads(journal['old'][tx.RUNTIME])['format'], cr.IMAGE_RUNTIME_FORMAT)
            self.assertTrue(diag._early_registration(pub.journal_bytes(journal), staged=True))
            state = fixture.files(self.root)
            self.assertEqual(self.register()['status'], 'no-op')
            self.assertEqual(state, fixture.files(self.root))
            self.assertEqual(calls['old'], 0)
            with self.assertRaisesRegex(InvalidInput, 'unreproducible'):
                cr.check_checkout(self.root, replay=True)
        after = fixture.files(self.root)
        for name in before:
            if name not in (tx.REGISTRY, tx.RUNTIME):
                self.assertEqual(before[name], after[name], name)
        self.assertFalse((self.root / tx.LOCK).exists())
        self.assertEqual(len(cr.check_checkout(self.root)['entries']), 3)
        source = json.loads((self.root / bg.path(self.old_id)).read_bytes())
        self.assertIsNone(bg.initial(source))
        self.assertNotIn('origin', source)

    def test_none_current_choice_and_empty_transport_exception_are_precise(self):
        from tools.puzzle_production import catalog_background as bg, editor_change as edit
        request = {'id': self.old_id, 'metadata': None, 'text': None, 'profile': None,
                   'reveal': None, 'background': {'status': 'none', 'upload': None}}
        edit.apply(self.root, edit.plan(self.root, request))
        source = self.root / bg.path(self.old_id)
        before = source.read_bytes()
        self.assertEqual(self.register()['status'], 'registered')
        self.assertEqual(source.read_bytes(), before)
        value = cr.check_checkout(self.root)
        self.assertEqual(json.loads(before)['current']['status'], 'none')

    def test_package_runtime_and_staging_recover_v9_with_fresh_conflict_guards(self):
        for phase in ('journal-complete', 'P3', 'P5'):
            with self.subTest(phase=phase):
                original = fixture.files(self.root)
                def stop(at, name=None):
                    if at == phase: raise InterruptedError('RI-V9 interruption')
                with patch.object(pub, 'checkpoint', side_effect=stop), self.assertRaises(InterruptedError):
                    self.register()
                classified = diag.classify(self.root)
                # Classification validates the actual generated v9, including staged recovery.
                self.assertIn('picross-registration-journal-v9', str(classified))
                def restop(at, name=None):
                    if at == 'R1-addition': raise InterruptedError('RI-V9 recovery interrupted')
                if phase != 'journal-complete':
                    with patch.object(pub, 'checkpoint', side_effect=restop), self.assertRaises(InterruptedError):
                        cr.recover(self.root)
                cr.recover(self.root)
                with self.assertRaisesRegex(InvalidInput, 'Missing/ambiguous journal staging'):
                    cr.recover(self.root)
                self.assertEqual({n: raw for n, (raw, stamp) in fixture.files(self.root).items()},
                                 {n: raw for n, (raw, stamp) in original.items()})

    def test_new_unknown_generation_or_foreign_slim_bytes_never_write(self):
        from tools.puzzle_production import catalog_background as bg
        original = fixture.files(self.root)
        with patch.dict(tx.IMAGE_FORMATS, registration='picross-registration-journal-v10'):
            with self.assertRaisesRegex(InvalidInput, 'Unserved registration generation'):
                self.register()
        self.assertEqual(fixture.files(self.root), original)
        name = bg.path(self.old_id)
        (self.root / name).write_bytes((self.root / name).read_bytes() + b'FOREIGN')
        before = fixture.files(self.root)
        with self.assertRaises(ValueError): self.register()
        self.assertEqual(fixture.files(self.root), before)

    def test_new_input_and_unknown_empty_directory_reject_without_mutation(self):
        from tools.puzzle_production import catalog_rating
        before = fixture.files(self.root)
        bad = deepcopy(self.difficulty)
        bad['current_source']['definition_sha256'] = '0' * 64
        bad = catalog_rating.hashed(bad, 'checked_hash')
        with self.assertRaises(InvalidInput):
            cr.registration(self.export, self.root, apply=True, difficulty=bad)
        self.assertEqual(fixture.files(self.root), before)
        foreign = self.root / self.old_package / 'external/unknown'
        foreign.mkdir()
        with self.assertRaises(ValueError): self.register()
        self.assertTrue(foreign.is_dir())
        self.assertEqual(fixture.files(self.root), before)

    def test_every_declared_registration_generation_has_an_explicit_route(self):
        declared = {value['registration'] for value in vars(tx).values()
                    if isinstance(value, dict) and isinstance(value.get('registration'), str)}
        historical = {tx.LEGACY_FORMATS['registration'], tx.PREVIOUS_FORMATS['registration']}
        served = {name for formats, name, route in tx.REGISTRATION_GENERATIONS.values()}
        self.assertEqual(declared, historical | served)
        for generation, (formats, name, route) in tx.REGISTRATION_GENERATIONS.items():
            self.assertEqual(tx.registration_format(generation), name)
            self.assertEqual(tx.registration_route({'operation': 'registration', 'format': name}), route)
        self.assertIsNone(tx.registration_route({'operation': 'registration', 'format': 'picross-registration-journal-v10'}))
