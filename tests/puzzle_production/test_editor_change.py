"""PE-EDIT2 targeted edits. No normal action may certify other content.

The synthetic prerequisite represents externally migrated current sources;
constructing it is not an editor migration API or a production converter.
"""
from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from tests.puzzle_production.catalog_fixtures import registered
from tools.puzzle_production import editor_change as edit, catalog_io as io
from tools.puzzle_production import content_registry as registry, catalog_background as bg
from tools.puzzle_production.contract import write_json, digest


def current_fixture(root):
    return json.loads((root/registry.REGISTRY).read_bytes())["entries"][0]


class EditorChangeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = tempfile.TemporaryDirectory(prefix='pe-edit2-base-')
        home = Path(cls.fixture.name)
        registered(home, stem='edit2', save_slot='edit2')
        cls.entry = current_fixture(home/'base')

    @classmethod
    def tearDownClass(cls): cls.fixture.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='pe-edit2-')
        self.home = Path(self.temp.name)
        self.root = self.home/'checkout'
        shutil.copytree(Path(self.fixture.name)/'base', self.root)

    def tearDown(self): self.temp.cleanup()

    def request(self, **changes):
        return {'id': self.entry['id'], 'metadata': None, 'text': None,
                'profile': None, 'reveal': None, 'background': None, **changes}

    def metadata_plan(self):
        return edit.plan(self.root, self.request(metadata={'name': 'Neuer Name', 'category_id': 'voegel'}))

    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
                for p in self.root.rglob('*') if p.is_file()}

    def test_metadata_reads_only_indices_and_noop_writes_nothing(self):
        original = io.read
        reads = []
        def bounded(root, name, limit, **kw):
            if Path(root) == self.root:
                self.assertTrue(name in edit.INDEXES or name in (edit.LOCK, edit.STAGE) or '/.editor-' in name, name)
                reads.append(name)
            return original(root, name, limit, **kw)
        with patch.object(io, 'read', side_effect=bounded), patch.object(registry, 'check_checkout', side_effect=AssertionError('full scan')):
            edit.listing(self.root)
            plan = self.metadata_plan()
            edit.apply(self.root, plan)
            self.assertEqual(set(plan['reads']), set(edit.INDEXES))
            before = self.snapshot()
            noop = self.metadata_plan()
            self.assertFalse(noop['changes'])
            self.assertEqual(edit.apply(self.root, noop)['status'], 'noop')
            self.assertEqual(before, self.snapshot())

    def test_relevant_same_mtime_change_rejects_and_releases_own_lock(self):
        plan = self.metadata_plan()
        path = self.root/registry.RUNTIME
        stamp = path.stat()
        raw = path.read_bytes()+b' '
        path.write_bytes(raw); os.utime(path, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
        with self.assertRaisesRegex(ValueError, 'Relevant input changed'): edit.apply(self.root, plan)
        self.assertEqual(path.read_bytes(), raw)
        self.assertFalse((self.root/edit.LOCK).exists())

    def test_interruptions_restore_only_bound_files_and_repeat(self):
        for phase in ('before-journal', 'after-journal', 'before-target', 'after-target', 'after-runtime'):
            with self.subTest(phase=phase):
                before = {k: v[0] for k, v in self.snapshot().items()}
                plan = self.metadata_plan()
                def stop(where, name=None):
                    if where == phase: raise RuntimeError('simulated process death')
                with patch.object(edit, 'checkpoint', side_effect=stop), self.assertRaises(RuntimeError):
                    edit.apply(self.root, plan)
                edit.recover(self.root)
                self.assertEqual(edit.recover(self.root)['status'], 'noop')
                self.assertEqual(before, {k: v[0] for k, v in self.snapshot().items()})

    def test_foreign_state_and_unknown_journal_survive(self):
        plan = self.metadata_plan()
        with patch.object(edit, 'checkpoint', side_effect=lambda phase, name=None: (_ for _ in ()).throw(RuntimeError()) if phase == 'after-journal' else None):
            with self.assertRaises(RuntimeError): edit.apply(self.root, plan)
        (self.root/registry.RUNTIME).write_bytes(b'foreign')
        before = self.snapshot()
        with self.assertRaises(ValueError): edit.recover(self.root)
        self.assertEqual(before, self.snapshot())

    def test_hardlink_target_and_forged_path_reject_before_write(self):
        plan = self.metadata_plan()
        os.link(self.root/registry.RUNTIME, self.home/'foreign')
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, 'hardlink'): edit.apply(self.root, plan)
        self.assertEqual(before, self.snapshot())
        (self.home/'foreign').unlink()
        plan['reads']['game/saves/user.json'] = None
        plan['changes']['game/saves/user.json'] = {'old': None, 'new': edit.pack(b'bad')}
        plan['plan_hash'] = digest({k: v for k, v in plan.items() if k != 'plan_hash'})
        with self.assertRaisesRegex(ValueError, 'Unrelated'): edit.apply(self.root, plan)
        self.assertFalse((self.root/'game/saves').exists())


    def test_same_matrix_needs_no_solver_or_sources(self):
        detail = edit.detail(self.root, self.entry['id'])
        with patch.object(edit, '_prepare_raster', side_effect=AssertionError('solver')):
            plan = edit.plan(self.root, self.request(text=detail['raster']['text'].replace(' ', '  ')+'\n', profile='line'))
        self.assertFalse(plan['changes'])
        self.assertEqual(set(plan['reads']), set(edit.INDEXES)|{'game/'+self.entry['definition']})

    def test_image_change_no_provenance_and_explicit_shared_diagnostic(self):
        from io import BytesIO
        from PIL import Image
        image = BytesIO(); Image.new('RGBA', (128, 128), (20, 30, 40, 128)).save(image, format='PNG')
        image = image.getvalue()
        plan = edit.plan(self.root, self.request(reveal={'upload': 'image'}),
                         uploads={'image': {'raw': image, 'suffix': 'png', 'checked': {'sha256': io.checksum(image), 'width': 128, 'height': 128}}})
        self.assertNotIn('provenance', json.dumps(plan))
        edit.apply(self.root, plan)
        registry.check_checkout(self.root)
        self.assertEqual((self.root/'game'/self.entry['reveal']).read_bytes(), image)

    def test_actual_raster_and_shared_diagnostic(self):
        import hashlib
        previous = (self.root/'game'/self.entry['definition']).read_bytes()
        original = hashlib.sha256
        streams = []
        def counted(raw=b'', **kwargs):
            if raw == previous: streams.append(len(raw))
            return original(raw, **kwargs)
        with patch.object(hashlib, 'sha256', side_effect=counted):
            plan = edit.plan(self.root, self.request(text='1 1 1\n0 0 0', profile='line'), work=self.home)
            self.assertIsNotNone(plan['quality'])
            edit.apply(self.root, plan)
        self.assertLessEqual(len(streams), 4)
        registry.check_checkout(self.root)
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError,"Occupied ID"):
            registry.registration(Path(self.fixture.name)/"export", self.root, apply=True)
        self.assertEqual(before, self.snapshot())


    def test_lost_ack_is_a_new_noop_without_new_revision(self):
        request = self.request(metadata={'name': 'Neuer Name', 'category_id': 'voegel'})
        with patch.object(edit, 'checkpoint', side_effect=lambda phase, name=None: (_ for _ in ()).throw(RuntimeError('ack lost')) if phase == 'complete' else None):
            with self.assertRaises(RuntimeError): edit.apply(self.root, edit.plan(self.root, request))
        before = self.snapshot()
        self.assertEqual(edit.apply(self.root, edit.plan(self.root, request))['status'], 'noop')
        self.assertEqual(before, self.snapshot())

    def test_forged_selected_identity_and_unbound_image_delta_reject(self):
        plan = self.metadata_plan()
        plan['entry']['definition'] = 'data/content/foreign.json'
        plan['plan_hash'] = digest({k: v for k, v in plan.items() if k != 'plan_hash'})
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, 'Selected plan entry'): edit.apply(self.root, plan)
        self.assertEqual(before, self.snapshot())
        raw = b'<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128"/>'
        from tools.puzzle_production.editor_image_input import validate_reveal
        plan = edit.plan(self.root, self.request(reveal={'upload': 'image'}), uploads={
            'image': {'raw': raw, 'suffix': 'svg', 'checked': validate_reveal(raw, '.svg')}})
        del plan['changes']['content/reveals/'+self.entry['id']+'.json']
        plan['plan_hash'] = digest({k: v for k, v in plan.items() if k != 'plan_hash'})
        with self.assertRaisesRegex(ValueError, 'lacks current image source|without current source'): edit.apply(self.root, plan)
        self.assertEqual(before, self.snapshot())

    def test_hg31_new_prepared_profile_requires_v2_and_preserves_unrelated_bytes(self):
        from io import BytesIO
        from PIL import Image
        from tools.puzzle_production.editor_image_input import validate_background
        image = Image.new('RGBA', (2304,768), (0,0,0,0)); image.putpixel((100,700),(60,60,60,128))
        stream = BytesIO(); image.save(stream, format='PNG'); raw=stream.getvalue()
        checked=validate_background(raw)
        self.assertEqual(checked['profile'], 'picross-prepared-background-png2304x768-v1')
        request=self.request(background={'status':'selected','upload':'background'})
        uploads={'background':{'raw':raw,'suffix':'png','checked':checked}}
        before=self.snapshot()
        with self.assertRaisesRegex(ValueError,'capability'): edit.plan(self.root,request,uploads=uploads)
        self.assertEqual(before,self.snapshot())
        write_json(self.root/bg.CAPABILITY, {'format':'picross-runtime-background-capability-v2',
            'runtime_format':'picross-runtime-registry-v8','profile_ids':['picross-background-png2304-v1','picross-background-png2304x768-v1'],'enabled':True})
        before=self.snapshot()
        plan=edit.plan(self.root,request,uploads=uploads)
        edit.apply(self.root,plan)
        self.assertEqual((self.root/bg.asset_path(self.entry['id'])).read_bytes(),raw)
        changed=set(plan['changes'])
        for name,value in before.items():
            if name not in changed: self.assertEqual(self.snapshot()[name],value,name)
        after=self.snapshot()
        self.assertEqual(edit.apply(self.root,edit.plan(self.root,request,uploads=uploads))['status'],'noop')
        self.assertEqual(after,self.snapshot())
        for status in ('none','standard'):
            plan=edit.plan(self.root,self.request(background={'status':status,'upload':None}))
            edit.apply(self.root,plan)
            self.assertFalse((self.root/bg.asset_path(self.entry['id'])).exists())
