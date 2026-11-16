"""Current ratings, dates, metadata, methods and separate image publication."""
from pathlib import Path
import json
import tempfile
import unittest
from tests.puzzle_production.current_fixtures import checkout,make,fingerprints,json_file,put
from tools.puzzle_production import catalog_integration as core,catalog_method as method,catalog_analysis as analysis
from tools.puzzle_production import catalog_rating as rating,catalog_added as added,current_content as content
from tools.puzzle_production import content_registry as registry,catalog_transaction as tx,catalog_metadata as metadata
from tools.puzzle_production import editor_cli,catalog_background_change as images
from tools.puzzle_production.contract import digest


class CurrentConsumerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.work=Path(self.temp.name);self.root=checkout(self.work/'repo')
        self.source=make(self.work/'input');core.integrate(self.source,self.root,apply=True)

    def activate(self):
        plan=method.plan(self.root,method.OLD,method.NEW,method.method_hash(method.NEW))
        self.assertEqual(method.adopt(self.root,plan)['status'],'activated')
        before=fingerprints(self.root)
        self.assertEqual(method.adopt(self.root,plan)['status'],'no-op')
        self.assertEqual(before,fingerprints(self.root))
        return plan

    def test_activation_new_one_color_and_multicolor_keep_existing_rating_and_dates(self):
        original=(self.root/rating.path('pz-current')).read_bytes()
        date=(self.root/added.path('pz-current')).read_bytes()
        self.activate()
        for count in (1,2):
            source=make(self.work/str(count),identifier='pz-color-'+str(count),mode='color',colors=count,method=method.NEW)
            self.assertEqual(core.integrate(source,self.root,apply=True)['status'],'registered')
        self.assertEqual((self.root/rating.path('pz-current')).read_bytes(),original)
        self.assertEqual((self.root/added.path('pz-current')).read_bytes(),date)
        registry.check_checkout(self.root)

    def test_current_preview_adopt_repeat_and_source_change_guard(self):
        self.activate();output=self.work/'preview'
        analysis.preview(self.root,output,'current-review','a'*40,ids=['pz-current'],method=method.NEW)
        self.assertEqual(analysis.adopt(self.root,output,apply=True)['status'],'adopted')
        before=fingerprints(self.root)
        self.assertEqual(analysis.adopt(self.root,output,apply=True)['status'],'no-op')
        self.assertEqual(before,fingerprints(self.root))
        registry.check_checkout(self.root)
        self.assertNotIn('adoption',json.loads((self.root/rating.path('pz-current')).read_bytes()))

    def test_current_catalog_recovery_restores_method_and_repeats(self):
        plan=method.plan(self.root,method.OLD,method.NEW,method.method_hash(method.NEW))
        before=fingerprints(self.root)
        with self.assertRaises(RuntimeError):method.adopt(self.root,plan,fail_step=4)
        self.assertEqual(registry.recover(self.root)['status'],'rolled-back')
        self.assertEqual({n:v[0] for n,v in fingerprints(self.root).items()},{n:v[0] for n,v in before.items()})
        self.assertEqual(registry.recover(self.root)['status'],'no-op')

    def test_current_metadata_and_date_readers_need_no_reports_or_archives(self):
        index=json.loads((self.root/content.REGISTRY).read_bytes())
        self.assertEqual(list(added.load_sources(self.root,index)),['pz-current'])
        self.assertEqual(list(rating.load_sources(self.root,index)),['pz-current'])
        plan=metadata.plan(self.root,[{'op':'set_metadata','id':'pz-current','name':'Current name'}])
        self.assertEqual(metadata.apply(self.root,plan)['status'],'updated')
        self.assertEqual(metadata.view(self.root)['entries'][0]['name'],'Current name')
        registry.check_checkout(self.root)

    def test_separate_current_background_request_repeat_and_reverse(self):
        request={'format':editor_cli.REQUEST,'id':'pz-current','metadata':None,'text':None,'profile':None,
                 'reveal':None,'background':{'status':'none','upload':None},'imports':{}}
        path=self.work/'request.json';path.write_bytes(content.encoded(request))
        output=self.work/'image-plan'
        images.plan(self.root,path,output)
        self.assertEqual(images.adopt(self.root,output)['status'],'adopted')
        before=fingerprints(self.root)
        self.assertEqual(images.adopt(self.root,output)['status'],'no-op')
        self.assertEqual(before,fingerprints(self.root))
        registry.check_checkout(self.root)


if __name__=='__main__':unittest.main()
