"""RI-ONE current delivery/list cases using real Git refs and the PW reader."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools.production_workspace import current_view as cv, presentation as p
from tools.production_workspace.repository import Repository, configure
from tools.production_workspace.sources import GitSource, INDEX, git
from tools.puzzle_production import catalog_io as io, content_registry as registry, current_content, catalog_integration
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

    def test_squash_and_copy_require_same_actual_delivery(self):
        self.integrate('squash');self.assertEqual(self.reader.refresh()['jobs'],[])
        # Independent copied delivery is covered without relying on common merge ancestry.
        git(self.repo,'checkout','-q','main');git(self.repo,'checkout','--orphan','independent-main')
        git(self.repo,'rm','-r','--cached','.');commit(self.repo)
        git(self.repo,'branch','-f','main','HEAD');git(self.repo,'checkout','-q',self.branch)
        self.integrate('copy');self.assertEqual(self.reader.refresh()['jobs'],[])

    def test_actual_v4_branch_registry_ignores_removed_receipt(self):
        self.integrate('copy')
        value=p.parse((self.repo/current_content.REGISTRY).read_bytes());value['format']='picross-content-registry-v4'
        entry=value['entries'][0];mode=entry.pop('mode');entry['production']={'mode':mode,'package':'content/packages/'+ID+'/r02','package_sha256':'0'*64}
        put(self.repo,current_content.REGISTRY,value)
        put(self.repo,'content/packages/'+ID+'/r02/manifest.json',{'format':'picross-integrated-content-v4','unused':'never read'})
        commit(self.repo);self.push()
        original=GitSource.read
        def trap(source,at,name,*args,**kwargs):
            if '/packages/' in name or name.endswith('.zip'):raise AssertionError('Unrelated archive read')
            return original(source,at,name,*args,**kwargs)
        with patch.object(GitSource,'read',trap):self.assertEqual(self.reader.refresh()['jobs'],[])

    def test_new_current_raster_phase_and_explicit_resumption_stay_visible(self):
        self.integrate();metadata_job(self.repo,'r01',state='raster_ready');commit(self.repo);self.push()
        self.assertIn('r01',{j['revision'] for j in self.reader.refresh()['jobs']})
        publish_pointer(self.repo,ID,'early-alpha');commit(self.repo);self.push()
        self.assertIn('early-alpha',{j['revision'] for j in self.reader.refresh()['jobs']})

    def test_changed_live_image_cannot_borrow_completed_record(self):
        self.integrate();put(self.repo,'game/art/content/'+ID+'.png',b'new actual image work');commit(self.repo);self.push()
        self.assertIn('r02',{j['revision'] for j in self.reader.refresh()['jobs']})

    def test_new_metadata_under_old_phase_is_preserved(self):
        self.integrate();name=f'content/authoring/{ID}/early-alpha/record.json';record=p.parse((self.repo/name).read_bytes())
        record['next_action']='New independent work';ref=put(self.repo,name,record)
        viewname=name.replace('record.json','workspace.json');view=p.parse((self.repo/viewname).read_bytes());view['record']={'commit':None,**ref};put(self.repo,viewname,view)
        commit(self.repo);self.push()
        self.assertIn('early-alpha',{j['revision'] for j in self.reader.refresh()['jobs']})

    def test_unconfirmed_main_and_bad_current_pointer_never_hide_work(self):
        self.integrate();self.assertEqual(self.reader.refresh()['jobs'],[])
        restarted=Repository(self.root/'state');self.assertTrue(restarted.listing()['jobs'])
        put(self.repo,cv.path(ID),b'{}');commit(self.repo);self.push()
        self.assertTrue(self.reader.refresh()['jobs'])

    def test_listing_does_not_read_archives_and_status_does_not_run_git(self):
        self.integrate();original=GitSource.read
        def trap(source,at,name,*args,**kwargs):
            self.assertNotIn('/packages/',name);self.assertFalse(name.endswith('.zip'))
            return original(source,at,name,*args,**kwargs)
        with patch.object(GitSource,'read',trap):self.assertEqual(self.reader.refresh()['jobs'],[])
        self.assertTrue(self.reader.confirmed_main)

if __name__=='__main__':unittest.main()
