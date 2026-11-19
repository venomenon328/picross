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
        self.release['assets'].append({'id':self.next_id,'name':name,'size':len(data),'state':'uploaded','label':'picross-original:'+tag})
        self.assets[self.next_id] = data

    def get(self,path,limit,*,binary=False):
        if binary:
            row = next(a for a in self.release['assets'] if a['name'] == path.rsplit('/',1)[1])
            return self.assets[row['id']]
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
        def lost_delete(path, method='GET', value=None):
            response = self.api(path, method, value)
            if path == 'releases/11' and method == 'DELETE':
                raise TimeoutError('Release removed, response lost')
            return response

        with patch.object(pub, 'api', side_effect=lost_delete), self.assertRaises(TimeoutError):
            pub.finish(self.root, 'pz-current', second, confirmed=True)
        self.assertIsNone(self.release)
        self.assertEqual(guard.remote_head(self.root, 'refs/heads/content/pw/pz-current'), second)
        self.assertEqual(pub.finish(self.root,'pz-current',second,confirmed=True),'closed')
        self.assertEqual(pub.finish(self.root,'pz-current',second,confirmed=True),'no-op')
        self.assertFalse(self.assets)
        self.assertIsNone(guard.remote_head(self.root,'refs/tags/work-prod-pz-current'))

    def test_selection_prunes_only_the_superseded_physical_identity(self):
        from io import BytesIO
        from PIL import Image
        f = self.fixture
        selected, discarded = f.asset('selected','reveal'), f.asset('discarded','reveal')
        buf = BytesIO()
        Image.new('RGBA',(2,3),(80,120,30,255)).save(buf,format='PNG')
        discarded['file'] = f.file('other.png',buf.getvalue())
        f.job.update(state='reveal_review',assets=[selected,discarded])
        f.publish()
        head = pub.push_job(self.root,'pz-current',None)
        _, _, old = self.record(head)
        chosen, gone = [a['file'] for a in old['assets']]
        self.upload(self.release['tag_name'],'foreign-original',b'foreign')
        foreign = self.next_id
        f.job['selected']['reveal'] = 'selected'
        fixtures.decide(f.job,'reveal')
        f.publish()
        next_head = pub.push_job(self.root,'pz-current',head)
        self.assertNotEqual(head,next_head)
        self.assertEqual(set(self.assets),{chosen['asset']['asset_id'],foreign})
        with self.assertRaisesRegex(ValueError,'Original asset missing'):
            work_assets.read(gone,1024)
        self.assertEqual(work_assets.read(chosen,1024),f.payload['selected.png'])

    def test_background_preparation_completion_and_confirmed_main_closure(self):
        from tools.puzzle_production import editor_change, editor_cli
        from tools.production_workspace import projector
        f = self.fixture
        f.test_background_only_uses_active_references_and_shared_editor()
        name = current.path('pz-current')
        registered = json.loads((self.root/name).read_bytes())
        active = fixtures.git(self.root,'log','--format=%H','--grep=^active product$','-1')
        fixtures.git(self.root,'push',self.remote,active + ':refs/heads/main')
        self.main = active
        draft = deepcopy(registered)
        draft.update(state='background_review', integration=None, decisions=[])
        draft['selected']['background'] = None
        other = deepcopy(draft['assets'][-1])
        other.update(id='other-context',label='Other synthetic offer')
        draft['assets'].append(other)
        (self.root/name).write_bytes(current.encoded(draft))
        first = pub.push_job(self.root,'pz-current',None)
        source,raw,record = self.record(first)
        self.assertEqual(len(current.projection(record,raw)['offers']),2)
        draft = deepcopy(registered)
        draft.update(state='editorially_approved',integration=None)
        (self.root/name).write_bytes(current.encoded(draft))
        second = pub.push_job(self.root,'pz-current',first)
        product_root = f.work/'product'
        fixtures.git(self.root,'worktree','add','-q','--detach',str(product_root),active)
        work_root = f.work/'external'
        fixtures.git(self.root,'worktree','add','-q','--detach',str(work_root),second)
        incoming = f.work/'external-input'
        current.prepare(work_root,name,incoming)
        plan = f.work/'external-plan.json'
        editor_cli.plan_file(product_root,incoming/'request.json',plan)
        editor_change.apply(product_root,json.loads(plan.read_bytes()))
        product = fixtures.commit(product_root,'Only selected final background')
        projector.complete(work_root,name,product,current_input=incoming)
        last = pub.push_job(work_root,'pz-current',second)
        with self.assertRaisesRegex(ValueError,'Different confirmed main'):
            pub.finish(work_root,'pz-current',last)
        fixtures.git(product_root,'push',self.remote,product + ':refs/heads/main')
        self.assertEqual(pub.finish(work_root,'pz-current',last),'closed')
        self.assertEqual(pub.finish(work_root,'pz-current',last),'no-op')

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

    def test_imported_parent_and_renamed_repository_output_are_rejected(self):
        root = self.root
        tree = fixtures.git(root,'rev-parse','HEAD^{tree}')
        imported = fixtures.git(root,'commit-tree',tree,'-m','unrelated historic root')
        merged = fixtures.git(root,'commit-tree',tree,'-p',self.main,'-p',imported,'-m','import')
        with self.assertRaises(subprocess.CalledProcessError):
            guard.check_range(root,merged,[self.main])
        fixtures.git(root,'mv','content/registry.json','content/authoring/output.json')
        fixtures.git(root,'commit','-qm','rename to a working output')
        head = fixtures.git(root,'rev-parse','HEAD')
        with self.assertRaisesRegex(ValueError,'production working file'):
            guard.check_range(root,head,[self.main])

    def test_capacity_checks_existing_and_new_releases(self):
        capacity = pub.release_catalog.capacity
        rows = [{'tag_name': 'work-prod-' + str(n), 'assets': []} for n in range(398)]
        # At 398, a new job must leave room for BOTH signed app releases.
        with self.assertRaisesRegex(ValueError, 'terminating page'):
            capacity(rows, 1, 'work-prod-new', 1, reserved_apps=2)
        capacity(rows[:396], 1, 'work-prod-new', 1, reserved_apps=2)
        capacity(rows, 1, 'pw-v1', 7, reserved_apps=0)
        rows.append({'tag_name': 'pw-v1', 'assets': []})
        with self.assertRaisesRegex(ValueError, 'terminating page'):
            capacity(rows, 1, 'pe-v1', 7, reserved_apps=0)
        rows = rows[:100]
        with self.assertRaisesRegex(ValueError, 'metadata budget'):
            capacity(rows, 45, rows[0]['tag_name'], 0, reserved_apps=2)
        rows[1]['body'] = 'x' * (4 * 1024**2 - 180000)
        capacity(rows, 1, rows[0]['tag_name'], 1, reserved_apps=0)
        with self.assertRaisesRegex(ValueError, 'metadata page'):
            capacity(rows, 1, rows[0]['tag_name'], 1, reserved_apps=2)

    def test_app_writer_contends_with_actual_git_work_lease(self):
        from tools.production_workspace import release_channel as channel
        from unittest.mock import Mock
        api = Mock(spec=channel.GitHub)
        ref = 'refs/heads/' + pub.release_catalog.LOCK_BRANCH

        def backed(path, **kwargs):
            method = kwargs.get('method', 'GET')
            if path.endswith('/git/ref/' + ref.removeprefix('refs/')):
                owner = guard.remote_head(self.root, ref)
                return {'object': {'sha': owner}} if owner else None
            if path.endswith('/git/refs') and method == 'POST':
                fixtures.git(self.remote, 'update-ref', ref, kwargs['value']['sha'], '0' * 40)
                return {}
            if method == 'DELETE' and path.endswith(ref.removeprefix('refs/')):
                fixtures.git(self.remote, 'update-ref', '-d', ref, self.main)
                return None
            self.fail('Unexpected lease request: ' + path)

        with patch.object(api, 'request', side_effect=backed):
            with pub.catalog_writer(self.root, self.main):
                with patch.object(channel.time, 'monotonic', side_effect=[0, 301]):
                    with self.assertRaisesRegex(ValueError, 'lease busy'):
                        with channel.app_catalog_writer(api, self.main):
                            self.fail('App entered occupied lease')
            with channel.app_catalog_writer(api, self.main):
                with self.assertRaisesRegex(ValueError, 'owns the catalog'):
                    with pub.catalog_writer(self.root, self.main):
                        self.fail('Work publisher entered occupied lease')
            self.assertIsNone(guard.remote_head(self.root, ref))
