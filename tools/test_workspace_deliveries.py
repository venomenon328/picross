"""RI-ONE current delivery/list cases using real Git refs and the PW reader."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools.production_workspace import current_view as cv, presentation as p
from tools.production_workspace.repository import Repository, configure
from tools.production_workspace.sources import GitSource, INDEX, git
from tools.puzzle_production import catalog_io as io, current_content, catalog_integration
from tools.puzzle_production.authoring_finalization import RECORD_KEYS
from tools.test_production_workspace import commit
from tests.puzzle_production.current_fixtures import make, checkout

ID='pz-workspace-test'


def put(root,name,value):
    raw=p.data(value) if not isinstance(value,bytes) else value
    target=root/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    return {'file':name,'sha256':io.checksum(raw),'bytes':len(raw)}


def publish_pointer(root,puzzle_id,revision):
    directory=f'content/authoring/{puzzle_id}/{revision}'
    value={'format':cv.FORMAT,'puzzle_id':puzzle_id,'revision':revision}
    for field,leaf in (('record','record.json'),('projection','workspace.json')):
        name=directory+'/'+leaf;value[field]=cv.reference(name,(root/name).read_bytes())
    put(root,cv.path(puzzle_id),value)


def metadata_job(root,revision,*,puzzle_id=ID,state='reveal_review'):
    directory=f'content/authoring/{puzzle_id}/{revision}'
    record=dict.fromkeys(RECORD_KEYS|{'raster_selection','presentation','candidate'})
    record.update(format='picross-authoring-record-v4',puzzle_id=puzzle_id,revision=revision,state=state,
                  category_id='test',blockers=[],document_revision=1,build_request_sha256='1'*64,repo_commit='a'*40,
                  inventory_sha256='2'*64,rulebook={},reveal_options=[],parameters=[],
                  verification={'effective_state':state},next_action='TEST ONLY',next_step='TEST ONLY')
    for field,leaf,raw in (('package','package.zip',b'Not a ZIP. Never needed for list completion.'),
                           ('handoff','handoff.json',b'{}'),('final_editorial_approval','approval.json',b'{}')):
        record[field]=put(root,directory+'/'+leaf,raw)
    projection={'format':p.CURRENT_FORMAT,'puzzle_id':puzzle_id,'revision':revision,
                'record':{'commit':None,**put(root,directory+'/record.json',record)},
                'title':'TEST ONLY synthetic','assets':[],'offers':[]}
    put(root,directory+'/workspace.json',projection)
    index=p.parse((root/INDEX).read_bytes());index['entries'].append({'puzzle_id':puzzle_id,'revision':revision,'record':directory+'/record.json'})
    put(root,INDEX,index);publish_pointer(root,puzzle_id,revision)
    return record


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory(prefix='current-pw-');self.addCleanup(temp.cleanup)
        self.root=Path(temp.name);self.repo=checkout(self.root/'repo')
        git(self.repo,'init','-q','-b','main');git(self.repo,'config','core.autocrlf','false');commit(self.repo)
        self.branch='content/pw/'+ID;git(self.repo,'checkout','-qb',self.branch)
        metadata_job(self.repo,'early-alpha');commit(self.repo)
        self.input=make(self.root/'input',identifier=ID)
        catalog_integration.integrate(self.input,self.repo,apply=True)
        metadata_job(self.repo,'r02',state='editorially_approved')
        self.integrated=commit(self.repo)
        from tools.production_workspace.projector import complete
        complete(self.repo,f'content/authoring/{ID}/r02/record.json',self.integrated,current_input=self.input)
        self.head=commit(self.repo)
        self.remote=self.root/'remote';self.remote.mkdir();git(self.remote,'init','--bare','-q');self.push()
        configure(self.repo,self.root/'state',remote=str(self.remote));self.reader=Repository(self.root/'state')

    def push(self):git(self.repo,'push','--force',str(self.remote),'main',self.branch)

    def integrate(self,mode='merge'):
        git(self.repo,'checkout','-q','main')
        if mode=='copy':
            source=GitSource(self.repo)
            from tools.puzzle_production.current_delivery import snapshot
            live=snapshot(lambda n,l,**kw:source.read(self.head,n,l,**kw),ID)
            for name in {*live['files'],current_content.REGISTRY,current_content.RUNTIME}:
                put(self.repo,name,source.read(self.head,name,64*1024*1024))
            if git(self.repo,'status','--porcelain').strip():commit(self.repo)
        else:
            git(self.repo,'-c','user.name=Synthetic','-c','user.email=test@example.invalid','merge',
                '--squash' if mode=='squash' else '--no-ff','--no-edit',self.head)
            if mode=='squash':commit(self.repo)
        main=git(self.repo,'rev-parse','HEAD').decode().strip()
        git(self.repo,'checkout','-q',self.branch);self.push();return main

    def test_fresh_main_and_unchanged_branch_hide_current_and_earlier_phases(self):
        before=self.reader.refresh();self.assertEqual({j['revision'] for j in before['jobs']},{'early-alpha','r02'})
        main=self.integrate();after=self.reader.refresh()
        self.assertEqual(after['jobs'],[],after['errors']);self.assertEqual(after['completion']['main_commit'],main)
        self.assertEqual(git(self.repo,'rev-parse','HEAD').decode().strip(),self.head)

    def test_squash_and_copy_hide_registered_id(self):
        self.integrate('squash');self.assertEqual(self.reader.refresh()['jobs'],[])
        # Independent copied delivery is covered without relying on common merge ancestry.
        git(self.repo,'checkout','-q','main');git(self.repo,'checkout','--orphan','independent-main')
        git(self.repo,'rm','-r','--cached','.');commit(self.repo)
        git(self.repo,'branch','-f','main','HEAD');git(self.repo,'checkout','-q',self.branch)
        self.integrate('copy');self.assertEqual(self.reader.refresh()['jobs'],[])

    def test_skip_registered_branches_and_main_rows_before_historical_reads(self):
        self.integrate()
        registered_branch_record = f'content/authoring/{ID}/r02/record.json'
        put(self.repo, registered_branch_record, b'{broken')
        publish_pointer(self.repo, ID, 'r02')
        branch = commit(self.repo)
        git(self.repo, 'checkout', '-q', 'main')
        put(self.repo, registered_branch_record, b'old unreadable record')
        metadata_job(self.repo, 'r01', puzzle_id='pz-open')
        metadata_job(self.repo, 'r01', puzzle_id='pz-broken')
        put(self.repo, 'content/authoring/pz-broken/r01/record.json', b'{broken')
        commit(self.repo)
        self.push()
        original = GitSource.read

        def trap(source, at, name, *args, **kwargs):
            self.assertNotEqual(at, branch, 'Registered production branch was opened')
            self.assertNotIn('/' + ID + '/', name)
            self.assertNotIn('/packages/', name)
            self.assertNotEqual(name, current_content.RUNTIME)
            self.assertFalse(name.startswith(('game/', 'content/backgrounds/', 'content/reveals/')))
            return original(source, at, name, *args, **kwargs)

        with patch.object(GitSource, 'read', trap):
            listing = self.reader.refresh()
        self.assertEqual({j['puzzle_id'] for j in listing['jobs']}, {'pz-open'})
        self.assertEqual(listing['completion']['completed_ids'], [ID])
        self.assertEqual(len(listing['errors']), 1)
        self.assertIn('pz-broken/r01', listing['errors'][0])

    def test_later_live_changes_and_reopened_phases_stay_hidden(self):
        self.integrate('copy')
        metadata_job(self.repo, 'r99', state='raster_ready')
        publish_pointer(self.repo, ID, 'early-alpha')
        commit(self.repo)
        git(self.repo, 'checkout', '-q', 'main')
        value = p.parse((self.repo / current_content.REGISTRY).read_bytes())
        value['metadata'][0]['name'] = 'Later name'
        put(self.repo, current_content.REGISTRY, value)
        put(self.repo, 'game/art/content/' + ID + '.png', b'Later live image bytes')
        commit(self.repo)
        self.push()
        listing = self.reader.refresh()
        self.assertEqual(listing['jobs'], [])
        self.assertEqual(listing['errors'], [])
        self.assertEqual(listing['completion']['completed_ids'], [ID])

    def test_local_main_progress_cannot_hide_open_remote_work(self):
        git(self.repo, 'checkout', '-q', 'main')
        catalog_integration.integrate(self.input,self.repo,apply=True)
        commit(self.repo)
        value = self.reader.refresh()
        self.assertEqual({j['puzzle_id'] for j in value['jobs']}, {ID})
        self.assertNotIn(ID, value['completion']['completed_ids'])

    def test_missing_invalid_and_offline_main_preserve_only_bound_list(self):
        from tools.production_workspace.server import Service
        self.integrate('copy')
        git(self.repo, 'checkout', '-q', 'main')
        metadata_job(self.repo, 'r01', puzzle_id='pz-open')
        main = commit(self.repo)
        self.push()
        service = Service(self.reader)
        first = service.listing(refresh=True)
        self.assertEqual({j['puzzle_id'] for j in first['jobs']}, {'pz-open'})
        self.assertTrue(first['completion']['confirmed'])

        valid = p.parse((self.repo / current_content.REGISTRY).read_bytes())
        valid['entries'].append(dict(valid['entries'][0]))
        put(self.repo, current_content.REGISTRY, valid)
        metadata_job(self.repo, 'r01', puzzle_id='pz-new')
        commit(self.repo)
        self.push()

        stale = service.listing(refresh=True)
        self.assertEqual(stale['snapshot'], first['snapshot'])
        self.assertEqual(stale['jobs'], first['jobs'])
        self.assertEqual(stale['completion']['main_commit'], main)
        self.assertFalse(stale['completion']['confirmed'])
        self.assertIn('Mainkatalog', stale['sync_error'])
        configure(self.repo, self.root / 'cold-invalid', remote=str(self.remote))
        unknown = Service(Repository(self.root / 'cold-invalid')).listing(refresh=True)
        self.assertIsNone(unknown['snapshot'])
        self.assertFalse(unknown['completion']['complete'])
        self.assertIn('Mainkatalog', unknown['sync_error'])

        git(self.remote, 'update-ref', '-d', 'refs/heads/main')
        stale = service.listing(refresh=True)
        self.assertEqual(stale['snapshot'], first['snapshot'])
        self.assertIn('Remote-main fehlt', stale['sync_error'])

        reopened = Repository(self.root / 'state')
        with patch.object(reopened, 'sync_remote', side_effect=ValueError('offline')):
            offline = reopened.refresh()
        self.assertFalse(offline['remote_confirmed'])
        self.assertFalse(offline['completion']['confirmed'])
        self.assertEqual(offline['completion']['main_commit'], main)
        self.assertEqual(offline['synced_at'], first['synced_at'])
        self.assertEqual({j['puzzle_id'] for j in offline['jobs']}, {'pz-open'})


if __name__ == '__main__':
    unittest.main()
