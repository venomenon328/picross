"""Bounded production transport regressions, using a private Git remote and synthetic pixels."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tools import publish_git as guard, work_publish as pub
from tools.puzzle_production import current_authoring as current, work_assets
from tools.production_workspace import presentation
from tools.production_workspace.sources import GitSource
from tests.puzzle_production import test_current_authoring as fixtures


class WorkPublicationTests(unittest.TestCase):
    def setUp(self):
        fixture = fixtures.CurrentAuthoringTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.fixture = fixture
        self.root = fixture.root
        self.main = fixture.base
        self.remote = str(fixture.work / 'remote.git')
        subprocess.run(['git','clone','-q','--bare',str(self.root),self.remote],check=True)
        self.release = None
        self.assets = {}
        self.next_id = 100
        for module, name, value in [(guard,'REMOTE',self.remote),(guard,'CLEAN_MAIN',self.main),
                                    (pub,'api',self.api),(pub,'upload',self.upload),
                                    (work_assets,'get',self.get)]:
            self.enterContext(patch.object(module,name,value))

    def api(self,path,method='GET',value=None):
        if path == '':
            return {'permissions':{'push':True}}
        if path == 'immutable-releases':
            return {'enabled':False}
        if path.startswith('releases?'):
            return [deepcopy(self.release)] if self.release else []
        if path == 'releases' and method == 'POST':
            self.assertEqual(value['make_latest'],'false')
            fixtures.git(self.remote,'update-ref','refs/tags/' + value['tag_name'],self.main)
            self.release = {**value,'id':11,'immutable':False,'assets':[]}
        if path.startswith('releases/assets/') and method == 'DELETE':
            id_ = int(path.rsplit('/',1)[1])
            self.release['assets'] = [a for a in self.release['assets'] if a['id'] != id_]
            del self.assets[id_]
        if path == 'releases/11' and method == 'DELETE':
            self.release = None
            self.assets.clear()
        return deepcopy(self.release)

    def upload(self,tag,name,data):
        self.assertEqual(tag, self.release['tag_name'])
        self.next_id += 1
        self.release['assets'].append({'id':self.next_id,'name':name,'size':len(data),'state':'uploaded'})
        self.assets[self.next_id] = data

    def get(self,path,limit,*,binary=False):
        if binary:
            return self.assets[int(path.rsplit('/',1)[1])]
        return json.dumps(self.release).encode()

    def record(self,commit):
        source=GitSource(self.root)
        raw=source.read(commit,current.path('pz-current'))
        return source,raw,json.loads(raw)

    def test_upload_readback_conflict_resume_selection_and_retirement(self):
        f=self.fixture
        f.approved()
        publish=lambda expected: pub.push_job(self.root,'pz-current',expected)
        real_upload=self.upload
        def interrupted(*args):
            real_upload(*args)
            raise ConnectionError('lost upload response')
        with patch.object(pub,'upload',interrupted), self.assertRaises(ConnectionError):
            publish(None)
        self.assertIsNone(guard.remote_head(self.root,'refs/heads/content/pw/pz-current'))
        first=publish(None)
        self.assertEqual(publish(None),first)
        source,raw,record=self.record(first)
        self.assertTrue(all('asset' in r for r in current.references(record)))
        projection=current.projection(record,raw)
        self.assertEqual(presentation.inspect(source,first,projection)['state'],'editorially_approved')
        view=projection['assets'][0]['location']
        original=presentation.asset_bytes(source,first,view)
        self.assertEqual(original, f.payload['reveal-b.png'])
        names=fixtures.git(self.root,'diff','--name-only',self.main,first).splitlines()
        self.assertEqual(set(names),{current.INDEX,current.path('pz-current')})
        f.job['title']='New choice'
        fixtures.decide(f.job,'final')
        fixtures.decide(f.job,'integration')
        f.publish()
        with self.assertRaises(ValueError):
            publish(None)
        second=publish(first)
        self.assertNotEqual(second,first)
        self.assertEqual(presentation.asset_bytes(source,first,view),original)
        with self.assertRaises(ValueError):
            pub.finish(self.root,'pz-current',first,confirmed=True)
        self.upload(self.release['tag_name'],'foreign',b'foreign')
        with self.assertRaisesRegex(ValueError,'Unexpected release contents'):
            pub.finish(self.root,'pz-current',second,confirmed=True)
        self.api('releases/assets/'+str(self.next_id),'DELETE')
        self.assertEqual(pub.finish(self.root,'pz-current',second,confirmed=True),'closed')
        self.assertEqual(pub.finish(self.root,'pz-current',second,confirmed=True),'no-op')
        self.assertFalse(self.assets)
        self.assertIsNone(guard.remote_head(self.root,'refs/tags/work-prod-pz-current'))

    def test_outgoing_checks_include_transient_outputs_and_renames(self):
        root=self.root
        file=root/'review-originals'/'local.png'
        file.parent.mkdir()
        file.write_bytes(b'original')
        fixtures.git(root,'add','.')
        fixtures.git(root,'commit','-qm','temporary')
        file.unlink()
        fixtures.git(root,'commit','-qam','remove')
        head=fixtures.git(root,'rev-parse','HEAD')
        with self.assertRaisesRegex(ValueError,'review delivery'):
            guard.check_range(root,head,[self.main])
        fixtures.git(root,'checkout','-qb','source',self.main)
        (root/'game'/'final.png').write_bytes(b'final resource')
        fixtures.git(root,'add','game/final.png')
        fixtures.git(root,'commit','-qm','product')
        head=fixtures.git(root,'rev-parse','HEAD')
        self.assertEqual(guard.check_range(root,head,[self.main])['bytes'],14)
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(['git','clone','-q','--depth=1',root.as_uri(),tmp],check=True)
            with self.assertRaisesRegex(ValueError,'Complete Git history'):
                guard.check_range(tmp,head,[self.main])

    def test_capacity_checks_existing_and_new_releases(self):
        rows=[{'tag_name':'work-prod-'+str(n),'assets':[]} for n in range(399)]
        pub.capacity(rows,1,rows[0]['tag_name'],1)
        with self.assertRaisesRegex(ValueError,'terminating page'):
            pub.capacity(rows,1,'new',0)
        with self.assertRaisesRegex(ValueError,'metadata budget'):
            pub.capacity(rows,60,rows[0]['tag_name'],0)
        rows[1]['body']='x'*(4*1024**2-10000)
        with self.assertRaisesRegex(ValueError,'metadata page'):
            pub.capacity(rows,1,rows[0]['tag_name'],1)
