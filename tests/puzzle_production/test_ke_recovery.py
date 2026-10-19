"""Frozen pre-KE wire bytes; no current writer, exporter, solver, Git or network."""
import base64
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.puzzle_production import content_registry as cr, content_update as cu
from tools.puzzle_production.contract import InvalidInput, canonical_bytes

FIXTURES = Path(__file__).parent/'fixtures/ke_recovery'
LOCK = 'content/.registration-pending.json'


class LegacyRecoveryTests(unittest.TestCase):
    def test_active_at_source_blocks_frozen_registration_and_update(self):
        from tools.puzzle_production.reveal_source import path
        for kind in ('registration','update'):
            root,journal=self.checkout(kind)
            entry=json.loads(journal['old'][cr.REGISTRY])['entries'][0]
            target=root/path(entry['id']);target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(b'unbound AT source must survive\n')
            before=self.snapshot(root)
            with self.assertRaises(InvalidInput):cr.recover(root)
            self.assertEqual(before,self.snapshot(root))

    def test_unbound_difficulty_blocks_exact_legacy_journals_without_mutation(self):
        from tools.puzzle_production.catalog_rating import path
        for kind in ('registration', 'update'):
            root, journal = self.checkout(kind)
            for side in ('old', 'new'):
                entries = json.loads(journal[side][cr.REGISTRY])['entries']
                target = root/path(entries[-1]['id'])
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes(b'foreign unbound difficulty\n')
                before = self.snapshot(root)
                with self.subTest(kind=kind,side=side), self.assertRaisesRegex(InvalidInput,'unbound|Unbound'):
                    cr.recover(root)
                self.assertEqual(before,self.snapshot(root))
                target.unlink()
            self.assert_recovered(root,journal,self.snapshot(root))

    def test_orphan_difficulty_blocks_legacy_recovery_before_mutation(self):
        for kind in ('registration', 'update'):
            root, journal = self.checkout(kind)
            target = root / 'content/difficulty/pz-orphan/rating.json'
            target.parent.mkdir(parents=True)
            target.write_bytes(b'foreign orphan rating\n')
            before = self.snapshot(root)
            with self.subTest(kind=kind), self.assertRaisesRegex(InvalidInput, 'Unregistered difficulty'):
                cr.recover(root)
            self.assertEqual(before, self.snapshot(root))
            target.unlink()
            self.assert_recovered(root, journal, self.snapshot(root))

    def checkout(self, kind, early=False):
        temp = tempfile.TemporaryDirectory(); self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        files = json.loads((FIXTURES/(kind+'-v2.json')).read_bytes())
        for name, encoded in files.items():
            path = root/name; path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(base64.b64decode(encoded))
        j = json.loads((root/LOCK).read_bytes())
        if early:
            for name, value in j['old'].items(): (root/name).write_bytes(value.encode())
            if kind == 'registration':
                # A killed copy before its first file; every target is still absent.
                import shutil
                for name in j['targets']:
                    p = root/name
                    shutil.rmtree(p) if p.is_dir() else p.unlink()
        return root, j

    def snapshot(self, root):
        return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob('*') if p.is_file()}

    def rewrite(self, root, journal):
        (root/LOCK).write_bytes(canonical_bytes(journal)+b'\n')

    def assert_recovered(self, root, journal, before):
        self.assertEqual(cr.recover(root)['status'], 'rolled-back')
        self.assertFalse((root/LOCK).exists())
        self.assertEqual(cr.check_checkout(root), json.loads(journal['old'][cr.REGISTRY]))
        raw = json.loads((root/cr.RUNTIME).read_bytes())
        self.assertEqual(raw['format'], 'picross-runtime-registry-v4')
        self.assertTrue(all(len(e) == 9 and 'difficulty' in e and e['added_at'] is None for e in raw['entries']))
        removed = journal.get('targets', [journal.get('package')])
        for name, data in before.items():
            if name == LOCK or name in journal['old'] or any(name == p or name.startswith(p+'/') for p in removed): continue
            self.assertEqual((root/name).read_bytes(), data, name)
        for name, value in journal['old'].items():
            if name != cr.RUNTIME: self.assertEqual((root/name).read_bytes(), value.encode())
        self.assertTrue(all(not (root/p).exists() for p in removed))

    def test_legacy_registration_early_and_advanced_and_real_update(self):
        for kind, early in [('registration', True), ('registration', False), ('update', False)]:
            with self.subTest(kind=kind, early=early):
                root, journal = self.checkout(kind, early)
                self.assertEqual(json.loads(journal['old'][cr.RUNTIME])['format'], 'picross-runtime-registry-v2')
                if kind == 'update':
                    changed = [n for n in journal['old'] if journal['old'][n] != journal['new'][n]]
                    self.assertTrue(any(n.endswith('.txt') for n in changed))
                    self.assertEqual(len(changed), 3)  # Definition, notice, registry; v2 has no revision/difficulty fields.
                self.assert_recovered(root, journal, self.snapshot(root))

    def test_each_recovery_resumes_after_its_own_v3_write(self):
        for kind, module in [('registration', cr), ('update', cu)]:
            root, journal = self.checkout(kind)
            before = self.snapshot(root)
            write = module.atomic_bytes
            def killed(path, data):
                write(path, data)
                if path == root/cr.RUNTIME: raise InterruptedError('killed after recovery v3')
            with self.subTest(kind=kind), patch.object(module, 'atomic_bytes', killed):
                with self.assertRaises(InterruptedError): cr.recover(root)
            self.assertTrue((root/LOCK).exists())
            self.assertEqual(json.loads((root/cr.RUNTIME).read_bytes())['format'], 'picross-runtime-registry-v4')
            self.assert_recovered(root, journal, before)

    def test_rejects_versions_noncanonical_and_foreign_bytes_before_any_write(self):
        attacks = ['unknown', 'mixed', 'noncanonical', 'extra-field', 'foreign-runtime',
                   'foreign-reveal', 'foreign-package', 'foreign-retained-notice', 'invalid-difficulty']
        for kind in ('registration', 'update'):
            for attack in attacks:
                with self.subTest(kind=kind, attack=attack):
                    root, journal = self.checkout(kind)
                    old = json.loads(journal['old'][cr.REGISTRY])
                    entry = old['entries'][0]
                    if attack in ('unknown', 'mixed', 'noncanonical', 'extra-field'):
                        raw = json.loads(journal['new'][cr.RUNTIME])
                        if attack == 'unknown': raw['format'] = 'picross-runtime-registry-v4'
                        if attack == 'extra-field': raw['entries'][0]['unexpected'] = False
                        if attack == 'mixed':
                            raw['format'] = 'picross-runtime-registry-v3'
                            for e in raw['entries']: e['difficulty'] = None
                        journal['new'][cr.RUNTIME] = (json.dumps(raw, indent=2) if attack == 'noncanonical' else canonical_bytes(raw).decode())+'\n'
                    elif attack == 'invalid-difficulty':
                        old['entries'][0]['production']['difficulty'] = {'level': 'L6'}
                        journal['old'][cr.REGISTRY] = canonical_bytes(old).decode()+'\n'
                    else:
                        name = {'foreign-runtime': cr.RUNTIME, 'foreign-reveal': 'game/'+entry['reveal'],
                                'foreign-package': entry['production']['package']+'/manifest.json',
                                'foreign-retained-notice': 'game/'+str(Path(entry['reveal']).with_suffix('.txt')).replace('\\','/')}[attack]
                        (root/name).write_bytes((root/name).read_bytes()+b'foreign\n')
                    self.rewrite(root, journal)
                    before = self.snapshot(root)
                    with self.assertRaises((InvalidInput, ValueError)): cr.recover(root)
                    self.assertEqual(self.snapshot(root), before)

    def test_own_intermediate_does_not_authorize_a_foreign_v3_projection(self):
        for kind, module in [('registration', cr), ('update', cu)]:
            root, _ = self.checkout(kind)
            write = module.atomic_bytes
            def killed(path, data):
                write(path, data)
                if path == root/cr.RUNTIME: raise InterruptedError()
            with patch.object(module, 'atomic_bytes', killed), self.assertRaises(InterruptedError): cr.recover(root)
            path = root/cr.RUNTIME
            path.write_bytes(path.read_bytes()+b' ')
            before = self.snapshot(root)
            with self.assertRaises(InvalidInput): cr.recover(root)
            self.assertEqual(self.snapshot(root), before)
