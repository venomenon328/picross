"""Current completion, explicit earlier phases and fresh-main list filtering."""
from copy import deepcopy
from pathlib import Path
import json
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from tests.puzzle_production.current_fixtures import checkout,make,json_file,put,fingerprints
from tools.puzzle_production import catalog_integration,integrated_content,current_content,current_delivery,catalog_io
from tools.production_workspace import projector, presentation, current_view
from tools.production_workspace.repository import Repository, configure
from tools.production_workspace.sources import GitSource


class CurrentCompletionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        # Only the new optional-notice scenarios need a selected background.
        selected=self._testMethodName in (
            'test_retire_selected_background_without_legacy_notice',
            'test_retire_rejects_foreign_notice_added_after_main')
        self.work=Path(self.temp.name);self.root=checkout(self.work/'repo')
        self.source=make(self.work/'input',background='selected' if selected else 'standard')
        self.git('init','-q','-b','main')
        catalog_integration.integrate(self.source,self.root,apply=True)
        self.rows=[]
        self.phase('r01','reveal_review');self.phase('r04','editorially_approved')
        put(self.root,'content/authoring/pz-current/shared/review.txt',b'Synthetic shared work.\n')
        self.integration=self.commit()

    def git(self,*args):
        return subprocess.check_output(['git','-C',str(self.root),*args],stderr=subprocess.PIPE).decode().strip()

    def commit(self):
        self.git('add','.')
        self.git('-c','user.name=Synthetic','-c','user.email=test@example.invalid','commit','-qm','Synthetic current work')
        return self.git('rev-parse','HEAD')

    def phase(self,revision,state):
        name=f'content/authoring/pz-current/{revision}/record.json'
        record={'format':'picross-authoring-record-v4','puzzle_id':'pz-current','revision':revision,'state':state,
                'integration':None,'blockers':[],'verification':{'effective_state':'editorially_approved'}}
        raw=current_content.encoded(record);put(self.root,name,raw)
        view={'format':presentation.CURRENT_FORMAT,'puzzle_id':'pz-current','revision':revision,
              'record':{'commit':None,**current_content.ref(name,raw)},'title':'Synthetic current work','assets':[],'offers':[]}
        json_file(self.root,name.replace('record.json','workspace.json'),view)
        put(self.root,name.replace('record.json','package.zip'),b'Not a ZIP; completion must never open it.\n')
        self.rows.append({'puzzle_id':'pz-current','revision':revision,'record':name})
        json_file(self.root,integrated_content.INDEX,{'format':'picross-authoring-index-v1','entries':self.rows})
        return name

    def close(self):
        result=projector.complete(self.root,'content/authoring/pz-current/r04/record.json',self.integration,current_input=self.source)
        self.assertEqual(result['status'],'completed')
        before=fingerprints(self.root)
        self.assertEqual(projector.complete(self.root,'content/authoring/pz-current/r04/record.json',self.integration,current_input=self.source)['status'],'reused')
        self.assertEqual(before,fingerprints(self.root))
        main=self.commit();self.git('update-ref','refs/remotes/origin/main',main)
        return main

    def test_completion_no_archives_multiphase_retirement_and_noop(self):
        main=self.close()
        live=current_delivery.snapshot(lambda n,l,missing=False:catalog_io.read(self.root,n,l,missing=missing),'pz-current')
        self.phase('r02','raster_review') # A smaller number is still new open work.
        protected=(self.root/'content/authoring/pz-current/r02/record.json').read_bytes()
        kwargs={'completed_revisions':[('pz-current','r01')],'completed_work':[('pz-current','shared')]}
        result=integrated_content.retire(self.root,['pz-current'],main,**kwargs)
        self.assertEqual(result['status'],'retired')
        self.assertFalse((self.root/'content/authoring/pz-current/r01/record.json').exists())
        self.assertFalse((self.root/'content/authoring/pz-current/r04/record.json').exists())
        self.assertFalse((self.root/current_view.path('pz-current')).exists())
        self.assertEqual((self.root/'content/authoring/pz-current/r02/record.json').read_bytes(),protected)
        self.assertEqual(current_delivery.snapshot(lambda n,l,missing=False:catalog_io.read(self.root,n,l,missing=missing),'pz-current'),live)
        before=fingerprints(self.root)
        self.assertEqual(integrated_content.retire(self.root,['pz-current'],main,**kwargs)['status'],'no-op')
        self.assertEqual(before,fingerprints(self.root))

    def test_retire_selected_background_without_legacy_notice(self):
        self.close()
        notice='game/art/backgrounds/pz-current.txt'
        self.assertTrue((self.root/notice).is_file())
        (self.root/notice).unlink()  # PE-EDIT2 never generates a replacement TXT.
        main=self.commit()
        self.git('update-ref','refs/remotes/origin/main',main)
        read=lambda n,l,missing=False:catalog_io.read(self.root,n,l,missing=missing)
        live=current_delivery.snapshot(read,'pz-current')
        self.assertIsNone(live['files'][notice])
        result=integrated_content.retire(
            self.root,['pz-current'],main,
            completed_revisions=[('pz-current','r01')],
            completed_work=[('pz-current','shared')])
        self.assertEqual(result['status'],'retired')
        self.assertTrue((self.root/'game/art/backgrounds/pz-current.png').is_file())
        self.assertFalse((self.root/notice).exists())
        self.assertEqual(current_delivery.snapshot(read,'pz-current'),live)
        before=fingerprints(self.root)
        self.assertEqual(integrated_content.retire(self.root,['pz-current'],main)['status'],'no-op')
        self.assertEqual(before,fingerprints(self.root))

    def test_retire_rejects_foreign_notice_added_after_main(self):
        self.close()
        notice='game/art/backgrounds/pz-current.txt'
        (self.root/notice).unlink()
        main=self.commit()
        self.git('update-ref','refs/remotes/origin/main',main)
        put(self.root,notice,b'Uncommitted foreign notice.\n')
        before=fingerprints(self.root)
        with self.assertRaisesRegex(ValueError,'Current selected delivery differs'):
            integrated_content.retire(self.root,['pz-current'],main,
                                      completed_work=[('pz-current','shared')])
        self.assertEqual(fingerprints(self.root),before)

    def test_retire_still_requires_reveal_notice(self):
        main=self.close()
        (self.root/'game/art/content/pz-current.txt').unlink()
        before=fingerprints(self.root)
        with self.assertRaisesRegex(ValueError,'Missing catalog file'):
            integrated_content.retire(self.root,['pz-current'],main,
                                      completed_work=[('pz-current','shared')])
        self.assertEqual(fingerprints(self.root),before)

    def test_foreign_completed_work_preserves_all_files(self):
        main=self.close()
        put(self.root,'content/authoring/pz-current/r01/foreign.txt',b'New work.\n')
        before=fingerprints(self.root)
        with self.assertRaisesRegex(ValueError,'foreign work'):
            integrated_content.retire(self.root,['pz-current'],main,completed_revisions=[('pz-current','r01')])
        self.assertEqual(before,fingerprints(self.root))

    def test_list_hides_registered_id_while_completion_stays_bound_to_live_result(self):
        main = self.close()
        source = GitSource(self.root)
        baseline = current_delivery.snapshot(lambda n, l, missing=False: source.read(main, n, l, missing),
                                             'pz-current')
        configure(self.root, self.work / 'state')
        reader = Repository(self.work / 'state')
        self.assertEqual(reader.listing()['jobs'], [])
        put(self.root, 'game/art/content/pz-current.png', b'Later changed image')
        self.phase('r99', 'raster_review')
        later = self.commit()
        self.assertNotEqual(main, later)
        value = reader.listing()
        self.assertEqual(value['jobs'], [])
        self.assertEqual(value['completion']['completed_ids'], ['pz-current'])
        edited = current_delivery.snapshot(lambda n, l, missing=False: source.read(later, n, l, missing),
                                           'pz-current')
        self.assertFalse(current_delivery.same(edited, baseline))


if __name__=='__main__':unittest.main()
