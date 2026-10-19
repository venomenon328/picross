"""AT-S01/S03/S04: fixed synthetic images and isolated catalog snapshots only."""
from copy import deepcopy
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image, ImageDraw

from tools.puzzle_production import catalog_reveal as at, reveal_source as source, catalog_io as io
from tools.puzzle_production import content_registry as cr, catalog_transaction as tx
from tools.puzzle_production.contract import canonical_bytes, digest, InvalidInput, load_json, write_json
from tools.puzzle_production.za1_fixtures import FIXTURES, approve, isolated_checkout, difficulty_for_export
from tools.puzzle_production.target_adapter import export


def snapshot(root):
    return {p.relative_to(root).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
            for p in root.rglob('*') if p.is_file() and '.git' not in p.relative_to(root).parts}


def synthetic_image(path, variant=1, size=(80, 80)):
    """An opaque white detail, interior hole and soft edge; never a catalog asset."""
    im = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    draw.ellipse((4, 4, size[0]-5, size[1]-5), fill=(40, 130, 80 + variant, 80))
    draw.ellipse((8, 8, size[0]-9, size[1]-9), fill=(40 + variant, 130, 80, 255))
    draw.rectangle((20, 20, 30, 30), fill=(255, 255, 255, 255))
    draw.ellipse((40, 40, 54, 54), fill=(0, 0, 0, 0))
    im.save(path)


class RevealTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shared = tempfile.TemporaryDirectory(); cls.home = Path(cls.shared.name)
        cls.base = isolated_checkout(cls.home/'base')
        approval = cls.home/'approval.json'; approve(FIXTURES/'direct-mono', approval)
        cls.exported = cls.home/'export'
        export(FIXTURES/'direct-mono', cls.exported, name='TEST ONLY', revision=1, stem='at_test', save_slot='at_test',
               approval_path=approval, category_id='voegel', categories_path=cls.base/'content/categories.json')
        cr.registration(cls.exported, cls.base, apply=True, difficulty=difficulty_for_export(cls.exported))
        cls.entry = cr.check_checkout(cls.base)['entries'][0]
        cls.identifier = cls.entry['id']

    @classmethod
    def tearDownClass(cls): cls.shared.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name); self.checkout = self.root/'checkout'
        shutil.copytree(self.base, self.checkout)

    def request(self, variant=1, append=None):
        self.entry = next(e for e in cr.check_checkout(self.checkout)['entries'] if e['id'] == self.identifier)
        directory = self.root/('input'+str(variant)); directory.mkdir()
        synthetic_image(directory/'image.png', variant)
        catalog = load_json(self.checkout/'content/categories.json')
        resolved = source.resolve(self.checkout, self.entry, catalog)
        old = source.load(self.checkout, self.entry, catalog)
        notice = (self.checkout/source.identity(self.entry)['notice']).read_bytes()
        if append is not None: notice += b'\n' + append.encode()
        declaration = {'format': source.APPROVAL, 'id': self.identifier,
                       'image_revision': old['current']['image_revision'] + 1 if old else 1,
                       'definition_sha256': resolved['definition_sha256'],
                       'previous_reveal_sha256': resolved['effective_reveal_sha256'],
                       'reveal_sha256': io.checksum((directory/'image.png').read_bytes()),
                       'notice_sha256': io.checksum(notice), 'actor': 'TEST ONLY',
                       'timestamp_utc': '2026-10-19T10:00:00Z', 'statement': 'Synthetic test approval only.',
                       'checks': dict.fromkeys(('reveal_approved','motif_raster_consistent','final_editorial_approved'), True), 'test_only': True}
        value = {'format': at.REQUEST, 'entries': [{'id': self.identifier, 'image': 'image.png', 'approval': declaration,
                    'provenance': {'author':'Synthetic fixture','usage_basis':'Project test data','source':'Generated fixed geometry','changes':'Alpha test '+str(variant)},
                    'notice_append': append}]}
        write_json(directory/'request.json', value)
        return directory/'request.json'

    def make_plan(self, variant=1, append=None):
        request = self.request(variant, append)
        output = self.root/('plan'+str(variant))
        result = at.plan(self.checkout, [self.identifier], request, output)
        self.assertEqual(result['status'], 'planned')
        return output/'plan.json'

    def test_first_second_revision_readonly_plan_historical_noop_and_mtimes(self):
        before = snapshot(self.checkout)
        plan = self.make_plan(append='TEST ONLY additional attribution\n')
        self.assertEqual(before, snapshot(self.checkout))
        with patch('tools.puzzle_production.target_adapter.verify_export', side_effect=AssertionError('image adoption replayed solver')):
            self.assertEqual(at.adopt(self.checkout, plan)['status'], 'adopted')
            after = snapshot(self.checkout)
            self.assertEqual(at.adopt(self.checkout, plan)['status'], 'no-op')
            self.assertEqual(after, snapshot(self.checkout))
        permitted = {source.path(self.identifier), 'game/'+self.entry['reveal'], source.identity(self.entry)['notice']}
        self.assertEqual({n for n in set(before)|set(after) if before.get(n) != after.get(n)}, permitted)
        self.assertEqual(cr.registration(self.exported, self.checkout, apply=True)['status'], 'no-op')
        self.assertEqual(after, snapshot(self.checkout))
        old = load_json(self.checkout/source.path(self.identifier))
        second = self.make_plan(2)
        at.adopt(self.checkout, second)
        new = load_json(self.checkout/source.path(self.identifier))
        self.assertEqual(new['revisions'][:-1], old['revisions'])
        self.assertEqual(new['origin'], old['origin'])
        self.assertEqual(new['bindings'], old['bindings'])
        self.assertEqual(new['record_revision'], 2)
        with self.assertRaisesRegex(InvalidInput, 'Stale'): at.adopt(self.checkout, plan)

    def test_approval_notice_and_plan_tampering_rejected_without_mutation(self):
        request = self.request()
        value = load_json(request)
        before = snapshot(self.checkout)
        for field, bad in [('image_revision', True), ('test_only', False), ('timestamp_utc', '2026-02-30T10:00:00Z'), ('actor', ' leading')]:
            modified = deepcopy(value); modified['entries'][0]['approval'][field] = bad; write_json(request, modified)
            with self.subTest(field=field), self.assertRaises((ValueError, InvalidInput)):
                at.plan(self.checkout, [self.identifier], request, self.root/'invalid')
            self.assertEqual(before, snapshot(self.checkout))
        write_json(request, value)
        at.plan(self.checkout, [self.identifier], request, self.root/'valid')
        plan = self.root/'valid/plan.json'; original = load_json(plan)
        changed = deepcopy(original); changed['entries'][0]['new_record']['text'] += ' '
        changed['entries'][0]['new_record']['sha256'] = io.checksum(changed['entries'][0]['new_record']['text'].encode())
        changed['plan_hash'] = digest({k:v for k,v in changed.items() if k != 'plan_hash'}); write_json(plan,changed)
        with self.assertRaises(ValueError): at.adopt(self.checkout, plan)
        self.assertEqual(before, snapshot(self.checkout))

    def test_unregistered_namespace_and_hardlinks_block_all_entrypoints(self):
        plan = self.make_plan()
        directory = self.checkout/'content/reveals'; directory.mkdir()
        (directory/'pz-unregistered.json').write_bytes(b'{}\n')
        before = snapshot(self.checkout)
        for operation in (lambda: cr.check_checkout(self.checkout), lambda: cr.sync_runtime(self.checkout), lambda: at.adopt(self.checkout, plan)):
            with self.assertRaises(ValueError): operation()
            self.assertEqual(before, snapshot(self.checkout))

    def test_strict_json_boundaries(self):
        for raw in (b'\xef\xbb\xbf{}', b'{"x":1,"x":2}', b'NaN', b'1e999', b'"\\ud800"',
                    b'['*33+b'0'+b']'*33, b'12345678901234567'):
            with self.subTest(raw=raw), self.assertRaises(ValueError): io.json_bytes(raw, 65536)
        self.assertEqual(io.json_bytes(b'{"finite":0.5}', 65536), {'finite':0.5})

    def integrated_commit(self):
        index = self.checkout/'content/authoring/index.json'
        index.parent.mkdir(parents=True,exist_ok=True)
        if not index.exists(): write_json(index, {'format':'picross-authoring-index-v1','entries':[]})
        def git(*args): return subprocess.check_output(['git','-C',str(self.checkout),*args],stderr=subprocess.DEVNULL).decode().strip()
        if not (self.checkout/'.git').exists(): git('init','-q')
        git('add','.')
        git('-c','user.name=Synthetic AT','-c','user.email=test@example.invalid','commit','-qm','TEST ONLY integrated state')
        commit=git('rev-parse','HEAD');git('update-ref','refs/remotes/origin/main',commit)
        return commit

    def test_first_after_cleanup_and_later_revision_keep_receipt_and_export_anchor(self):
        from tools.puzzle_production.integrated_content import retire
        retire(self.checkout,[self.identifier],self.integrated_commit())
        first=self.make_plan();at.adopt(self.checkout,first)
        old=load_json(self.checkout/source.path(self.identifier))
        self.assertIsNotNone(old['origin']['receipt'])
        second=self.make_plan(2);at.adopt(self.checkout,second)
        new=load_json(self.checkout/source.path(self.identifier))
        self.assertEqual(old['origin'],new['origin'])
        self.assertEqual(cr.registration(self.exported,self.checkout,apply=True)['status'],'no-op')

    def test_cleanup_after_revision_keeps_record_bytes_and_stales_saved_plan(self):
        from tools.puzzle_production.integrated_content import retire
        first=self.make_plan(append='TEST ONLY new attribution\n');at.adopt(self.checkout,first)
        record=(self.checkout/source.path(self.identifier)).read_bytes()
        second=self.make_plan(2)
        commit=self.integrated_commit()
        retire(self.checkout,[self.identifier],commit)
        self.assertEqual(record,(self.checkout/source.path(self.identifier)).read_bytes())
        self.assertIsNone(load_json(self.checkout/source.path(self.identifier))['origin']['receipt'])
        with self.assertRaisesRegex(ValueError,'Stale'):at.adopt(self.checkout,second)
        third=self.make_plan(3);at.adopt(self.checkout,third)
        self.assertEqual(cr.registration(self.exported,self.checkout,apply=True)['status'],'no-op')

    def test_raster_rebind_retains_active_image_notice_approvals_and_added(self):
        from tools.puzzle_production.za1_fixtures import seal, approve
        from tools.puzzle_production.content_update import update
        from tools.puzzle_production import catalog_added
        first=self.make_plan(append='TEST ONLY active attribution\n');at.adopt(self.checkout,first)
        previous=load_json(self.checkout/source.path(self.identifier))
        before=snapshot(self.checkout)
        package=self.root/'updated-input';shutil.copytree(self.exported/'input',package)
        handoff=load_json(package/'handoff.json');handoff['revision']='r02'
        image=package/handoff['reveal']['file'];image.write_bytes((self.checkout/'game'/self.entry['reveal']).read_bytes())
        checksum=io.checksum(image.read_bytes());handoff['reveal']['sha256']=checksum;handoff['motif']['derived_from_reveal_sha256']=checksum
        for name in ('reveal-approval.json','reveals/reveal.provenance.json'):
            data=load_json(package/name);data['sha256']=checksum;write_json(package/name,data)
        data=load_json(package/'motif-approval.json');data['derived_from_reveal_sha256']=checksum;write_json(package/'motif-approval.json',data)
        data=load_json(package/'motifs/source.provenance.json');data['derived_from']['sha256']=checksum;write_json(package/'motifs/source.provenance.json',data)
        (package/'inventory.json').unlink()
        (package/'derivation.json').unlink(missing_ok=True)
        seal(package,handoff);approval=self.root/'updated-approval.json';approve(package,approval)
        exported=self.root/'updated-export'
        export(package,exported,name='TEST ONLY',revision=2,stem='at_test',save_slot='at_test',approval_path=approval,
               category_id=self.entry['category_id'],categories_path=self.checkout/'content/categories.json')
        update(exported,self.checkout,self.entry['production']['definition_sha256'],apply=True,rebind_difficulty=True)
        current=load_json(self.checkout/source.path(self.identifier))
        self.assertEqual(current['origin'],previous['origin']);self.assertEqual(current['revisions'],previous['revisions'])
        self.assertEqual(current['bindings'][:-1],previous['bindings']);self.assertEqual(current['current'],{'binding_revision':2,'image_revision':1})
        self.assertEqual(current['record_revision'],2)
        for n in ('game/'+self.entry['reveal'],source.identity(self.entry)['notice'],catalog_added.path(self.identifier)):
            self.assertEqual(before[n],snapshot(self.checkout)[n])
        with self.assertRaisesRegex(ValueError,'Occupied'):cr.registration(self.exported,self.checkout,apply=True)
        self.assertEqual(cr.registration(exported,self.checkout,apply=True)['status'],'no-op')
        second=self.make_plan(2);at.adopt(self.checkout,second)
        latest=load_json(self.checkout/source.path(self.identifier))
        self.assertEqual(latest['revisions'][-1]['binding_hash'],latest['bindings'][-1]['binding_hash'])
        self.assertEqual(latest['revisions'][0],previous['revisions'][0])

    def test_full_snapshot_binds_unselected_package_files_and_absence(self):
        plan=self.make_plan()
        package=self.checkout/self.entry['production']['package']
        target=package/'approval.json';original=target.read_bytes();target.write_bytes(original+b'\n')
        before=snapshot(self.checkout)
        with self.assertRaises(ValueError):at.adopt(self.checkout,plan)
        self.assertEqual(before,snapshot(self.checkout));target.write_bytes(original)
        import os
        link=self.root/'hardlink.json';os.link(self.checkout/'content/registry.json',link)
        before=snapshot(self.checkout)
        with self.assertRaisesRegex(ValueError,'hardlink'):at.adopt(self.checkout,plan)
        self.assertEqual(before,snapshot(self.checkout));link.unlink()

    def test_record_approval_notice_types_and_boundaries(self):
        plan=load_json(self.make_plan())
        import json
        record=json.loads(plan['entries'][0]['new_record']['text'])
        catalog=load_json(self.checkout/'content/categories.json')
        mutations=[(('id',),'pz-foreign'),(('record_revision',),True),(('current','image_revision'),2),
                   (('origin','runtime_revision'),None),(('origin','receipt'),{}),
                   (('bindings',0,'binding_hash'),'0'*64),(('revisions',0,'binding_hash'),[]),
                   (('revisions',0,'previous_reveal_sha256'),'0'*64),
                   (('revisions',0,'approval','definition_sha256'),'0'*64),
                   (('revisions',0,'approval','checks','reveal_approved'),1),
                   (('revisions',0,'approval','timestamp_utc'),'2026-02-30T10:00:00Z'),
                   (('revisions',0,'approval','timestamp_utc'),'2026-10-19T10:00:00+00:00'),
                   (('revisions',0,'provenance','source'),None),
                   (('revisions',0,'notice','text'),'removed\n'),(('foreign',),True)]
        for keys,value in mutations:
            changed=deepcopy(record);target=changed
            for key in keys[:-1]:target=target[key]
            target[keys[-1]]=value
            with self.subTest(keys=keys),self.assertRaises(ValueError):source.validate(changed,catalog)
        for count in (127,128):self.assertEqual(source.text('x'*count,128),'x'*count)
        with self.assertRaises(ValueError):source.text('x'*129,128)
        for count in (65535,65536):source.make_notice(b'x'*(count-1)+b'\n')
        for raw in (b'x'*65536+b'\n',b'\xef\xbb\xbfhello\n',b'hello\r\n',b'hello\0\n',b'no newline'):
            with self.assertRaises(ValueError):source.make_notice(raw)
        before=snapshot(self.checkout)
        for arguments in ([],['--all'],['plan','--check',str(self.checkout)],['adopt','--checkout',str(self.checkout),'--plan','none','--force']):
            import sys
            result=subprocess.run([sys.executable,'-m','tools.puzzle_production.catalog_reveal',*arguments],capture_output=True,text=True)
            self.assertEqual(result.returncode,2,result.stderr)
            self.assertEqual(json.loads(result.stdout)['status'],'invalid_input')
        self.assertEqual(before,snapshot(self.checkout))

    def test_linked_checkout_root_is_not_silently_resolved(self):
        import os
        alias=self.root/'linked-checkout'
        if os.name=='nt':
            result=subprocess.run(['cmd','/c','mklink','/J',str(alias),str(self.checkout)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.addCleanup(os.rmdir,alias)
        else:
            alias.symlink_to(self.checkout,target_is_directory=True);self.addCleanup(alias.unlink)
        before=snapshot(self.checkout)
        for operation in (lambda:tx.capture(alias),lambda:cr.check_checkout(alias),lambda:cr.sync_runtime(alias)):
            with self.assertRaisesRegex(ValueError,'link/reparse'):operation()
            self.assertEqual(before,snapshot(self.checkout))

    def test_sd_added_and_sync_preserve_at_and_invalidate_old_plans(self):
        from tools.puzzle_production import catalog_analysis as sd,catalog_rating as rating,catalog_added as added,catalog_added_history as dates
        (self.checkout/rating.path(self.identifier)).unlink()
        (self.checkout/added.path(self.identifier)).unlink()
        cr.sync_runtime(self.checkout);base=self.integrated_commit()
        checked=difficulty_for_export(self.exported)
        old_sd=self.root/'sd-before';sd.preview(self.checkout,old_sd,'at-before',base,ids=[self.identifier],checked_inputs={self.identifier:checked})
        old_added=self.root/'added-before.json';write_json(old_added,dates.plan(self.checkout,'at-before',base))
        image_plan=self.make_plan();at.adopt(self.checkout,image_plan)
        preserved=(self.checkout/source.path(self.identifier)).read_bytes()
        for operation in (lambda:sd.adopt(self.checkout,old_sd,apply=True),lambda:dates.adopt(self.checkout,old_added,apply=True)):
            before=snapshot(self.checkout)
            with self.assertRaises(ValueError):operation()
            self.assertEqual(before,snapshot(self.checkout))
        new_sd=self.root/'sd-after';sd.preview(self.checkout,new_sd,'at-after',base,ids=[self.identifier],checked_inputs={self.identifier:checked})
        self.assertEqual(sd.adopt(self.checkout,new_sd,apply=True)['status'],'adopted')
        self.assertEqual((self.checkout/source.path(self.identifier)).read_bytes(),preserved)
        new_added=self.root/'added-after.json';write_json(new_added,dates.plan(self.checkout,'at-after',base))
        self.assertEqual(dates.adopt(self.checkout,new_added,apply=True)['status'],'adopted')
        self.assertEqual((self.checkout/source.path(self.identifier)).read_bytes(),preserved)
        before=snapshot(self.checkout);cr.sync_runtime(self.checkout)
        self.assertEqual(before,snapshot(self.checkout))
        with self.assertRaises(ValueError):at.adopt(self.checkout,image_plan)
        self.assertEqual(before,snapshot(self.checkout))


if __name__ == '__main__': unittest.main()
