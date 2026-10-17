"""Fixed synthetic raster updates, never real production packages or saves."""
from copy import deepcopy
from pathlib import Path
import shutil
import tempfile
import unittest

from tools.puzzle_production.authoring_package import file_hash
from tools.puzzle_production.contract import InvalidInput, load_json, write_json
from tools.puzzle_production.za1_fixtures import rated_registration as registration
from tools.puzzle_production.content_registry import check_checkout, recover
from tools.puzzle_production.za1_fixtures import rated_update as update
from tools.puzzle_production.target_adapter import export
from tools.puzzle_production.za1_fixtures import make, seal, approve, isolated_checkout, ROOT


class UpdateTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.checkout=isolated_checkout(self.root/'checkout')
        self.first=self.make_export('first','pz-test-update','r01',1,5)
        registration(self.first,self.checkout,apply=True)
        other=self.make_export('other','pz-test-other','r01',1,1)
        registration(other,self.checkout,apply=True)
        self.second=self.make_export('second','pz-test-update','r02',2,8)
        self.entry=next(e for e in check_checkout(self.checkout)['entries'] if e['id']=='pz-test-update')
        self.definition='game/'+self.entry['definition']
        self.expected=file_hash(self.checkout/self.definition)
        (self.checkout/'saves').mkdir()
        (self.checkout/'saves/untouched.json').write_bytes(b'not a real save; preserve bytes\n')

    def make_export(self,name,pid,package_revision,runtime_revision,colors,slot=None,category='voegel',changed_reveal=False):
        p=make(self.root/name,pid,10,4,'mono' if colors==1 else 'color',colors=colors)
        h=load_json(p/'handoff.json');h['revision']=package_revision
        if changed_reveal:
            from PIL import Image
            reveal=p/h['reveal']['file']
            with Image.open(reveal) as im:
                altered=im.copy();altered.putpixel((0,0),(100,100,100));altered.save(reveal)
            value=file_hash(reveal);h['reveal']['sha256']=value
            h['motif']['derived_from_reveal_sha256']=value
            for name in ('reveal-approval.json','reveals/reveal.provenance.json'):
                data=load_json(p/name);data['sha256']=value;write_json(p/name,data)
            data=load_json(p/'motif-approval.json');data['derived_from_reveal_sha256']=value;write_json(p/'motif-approval.json',data)
            data=load_json(p/'motifs/source.provenance.json');data['derived_from']['sha256']=value;write_json(p/'motifs/source.provenance.json',data)
        seal(p,h)
        approval=self.root/(name+'-approval.json');approve(p,approval)
        out=self.root/(name+'-export')
        export(p,out,name='TEST ONLY',revision=runtime_revision,stem=pid,save_slot=slot or 'slot_'+pid,
               approval_path=approval,category_id=category,categories_path=ROOT/'tests/puzzle_production/fixtures/catalog/categories.json')
        return out

    def snapshot(self):
        return {p.relative_to(self.checkout).as_posix():p.read_bytes() for p in self.checkout.rglob('*') if p.is_file()}

    def test_plan_is_read_only_and_update_preserves_identity_old_package_other_entry_and_saves(self):
        before=self.snapshot();registry=check_checkout(self.checkout)
        plan=update(self.second,self.checkout,self.expected)
        self.assertEqual(plan['status'],'planned-update');self.assertEqual(before,self.snapshot())
        with self.assertRaisesRegex(InvalidInput,'Occupied production ID'):
            registration(self.second,self.checkout,apply=True)
        result=update(self.second,self.checkout,self.expected,apply=True)
        self.assertEqual(result['status'],'updated');self.assertEqual(result['runtime_revision'],2)
        after=check_checkout(self.checkout,replay=True)
        self.assertEqual([e for e in registry['entries'] if e['id']!='pz-test-update'],
                         [e for e in after['entries'] if e['id']!='pz-test-update'])
        self.assertEqual(load_json(self.checkout/self.definition)['revision'],2)
        self.assertEqual(len(load_json(self.checkout/self.definition)['palette']),8)
        for name,data in before.items():
            if name.startswith(('content/packages/','saves/')):
                self.assertEqual((self.checkout/name).read_bytes(),data)
        with self.assertRaisesRegex(InvalidInput,'Stale'):
            update(self.second,self.checkout,self.expected,apply=True)
        self.assertEqual(update(self.second,self.checkout,file_hash(self.checkout/self.definition),apply=True)['status'],'no-op')

    def test_changed_logic_requires_new_rating_and_metadata_rebind_preserves_original(self):
        from tools.puzzle_production.content_update import update as actual_update
        from tools.puzzle_production import catalog_rating
        before = self.snapshot()
        with self.assertRaisesRegex(InvalidInput,'complete 0.3'):
            actual_update(self.second,self.checkout,self.expected,apply=True)
        with self.assertRaisesRegex(InvalidInput,'Rebind changes'):
            actual_update(self.second,self.checkout,self.expected,apply=True,rebind_difficulty=True)
        self.assertEqual(before,self.snapshot())
        metadata = self.make_export('metadata','pz-test-update','r03',2,5)
        prior = load_json(self.checkout/catalog_rating.path('pz-test-update'))
        actual_update(metadata,self.checkout,self.expected,apply=True,rebind_difficulty=True)
        current = load_json(self.checkout/catalog_rating.path('pz-test-update'))
        self.assertEqual(current['rating'],prior['rating'])
        self.assertEqual(current['rating_revision'],prior['rating_revision']+1)
        self.assertEqual(current['current_source']['runtime_revision'],2)
        check_checkout(self.checkout)

    def test_update_preserves_the_two_existing_export_checks_without_replaying_neighbors(self):
        from unittest.mock import patch
        from tools.puzzle_production import target_adapter
        original=target_adapter.verify_export
        with patch.object(target_adapter,'verify_export',wraps=original) as verify:
            update(self.second,self.checkout,self.expected,apply=True)
        self.assertEqual(verify.call_count,2)  # supplied export and independent staged export
        self.assertEqual(verify.call_args_list[0].args[0],self.second)
        self.assertTrue(all(not call.args[0].is_relative_to(self.checkout) for call in verify.call_args_list))

    def test_rejects_stale_revision_slot_category_reveal_and_occupied_package_without_writes(self):
        candidates=[(self.second,'0'*64,'Stale')]
        for revision in (1,):
            out=self.make_export('same-revision','pz-test-update','r03',revision,8)
            candidates.append((out,self.expected,'higher runtime revision'))
        candidates.append((self.make_export('slot','pz-test-update','r04',2,8,slot='changed_slot'),self.expected,'retain identity'))
        candidates.append((self.make_export('category','pz-test-update','r05',2,8,category='wasserwelt'),self.expected,'retain identity'))
        candidates.append((self.make_export('reveal','pz-test-update','r06',2,8,changed_reveal=True),self.expected,'retain the approved reveal'))
        out=self.make_export('occupied','pz-test-update','r01',2,8)
        candidates.append((out,self.expected,'package revision already exists'))
        for out,expected,error in candidates:
            before=self.snapshot()
            with self.subTest(error=error),self.assertRaisesRegex(InvalidInput,error):
                update(out,self.checkout,expected,apply=True)
            self.assertEqual(before,self.snapshot())

    def test_normal_failures_restore_exact_old_bytes(self):
        for step in (self.definition,'content/registry.json','game/data/registry.json'):
            before=self.snapshot()
            with self.subTest(step=step),self.assertRaisesRegex(OSError,'Injected update failure'):
                update(self.second,self.checkout,self.expected,apply=True,fail_step=step)
            self.assertEqual(before,self.snapshot())
            check_checkout(self.checkout)

    def test_crash_recovery_preflights_then_restores_every_phase(self):
        for step in ('crash-package','crash-'+self.definition,'crash-content/registry.json','crash-game/data/registry.json'):
            before=self.snapshot()
            with self.subTest(step=step),self.assertRaises(InterruptedError):
                update(self.second,self.checkout,self.expected,apply=True,fail_step=step)
            with self.assertRaisesRegex(InvalidInput,'Interrupted registration'):
                check_checkout(self.checkout)
            self.assertEqual(recover(self.checkout)['status'],'rolled-back')
            self.assertEqual(before,self.snapshot())

    def test_foreign_changes_block_recovery_before_any_mutation(self):
        with self.assertRaises(InterruptedError):
            update(self.second,self.checkout,self.expected,apply=True,fail_step='crash-package')
        destination=self.checkout/'content/packages/pz-test-update/r02/unexpected.txt'
        destination.write_bytes(b'foreign work\n')
        before=self.snapshot()
        with self.assertRaisesRegex(InvalidInput,'package changed'):
            recover(self.checkout)
        self.assertEqual(before,self.snapshot())
        destination.unlink()
        target=self.checkout/self.definition;old=target.read_bytes();target.write_bytes(b'foreign definition\n')
        before=self.snapshot()
        with self.assertRaisesRegex(InvalidInput,'target changed'):
            recover(self.checkout)
        self.assertEqual(before,self.snapshot())
        target.write_bytes(old);recover(self.checkout)

    def test_update_from_completed_compact_receipt(self):
        from tools.puzzle_production.integrated_content import FORMAT
        from tools.puzzle_production.content_registry import projection
        registry=check_checkout(self.checkout)
        entry=next(e for e in registry['entries'] if e['id']=='pz-test-update')
        package=self.checkout/entry['production']['package']
        receipt={'format':FORMAT,'entry':deepcopy(entry),'integrated_commit':'a'*40,
                 'notice_sha256':file_hash((self.checkout/'game'/entry['reveal']).with_suffix('.txt'))}
        shutil.rmtree(package);package.mkdir();write_json(package/'manifest.json',receipt)
        entry['production']['package_sha256']=file_hash(package/'manifest.json')
        write_json(self.checkout/'content/registry.json',registry)
        catalog=load_json(self.checkout/'content/categories.json')
        write_json(self.checkout/'game/data/registry.json',projection(registry,catalog,self.checkout))
        self.assertEqual(update(self.second,self.checkout,self.expected,apply=True)['status'],'updated')
        self.assertEqual(load_json(package/'manifest.json'),receipt)

    def test_recovery_rejects_tampered_notice_backup_without_mutation(self):
        with self.assertRaises(InterruptedError):
            update(self.second,self.checkout,self.expected,apply=True,fail_step='crash-content/registry.json')
        journal_path=self.checkout/'content/.registration-pending.json'
        journal=load_json(journal_path)
        notice='game/'+str(Path(self.entry['reveal']).with_suffix('.txt')).replace('\\','/')
        journal['old'][notice]='forged old rights notice\n'
        write_json(journal_path,journal)
        before=self.snapshot()
        with self.assertRaisesRegex(InvalidInput,'target changed|notice'):
            recover(self.checkout)
        self.assertEqual(before,self.snapshot())
