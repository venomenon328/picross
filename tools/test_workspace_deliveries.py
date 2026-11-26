"""RI-ONE current delivery/list cases using real Git refs and the PW reader."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools.production_workspace import presentation as p
from tools.production_workspace.repository import Repository, configure
from tools.production_workspace.sources import GitSource, INDEX, git
from tools.puzzle_production import catalog_io as io, current_content, catalog_integration
from tools.puzzle_production import current_authoring, current_delivery
from tools.test_production_workspace import commit
from tests.puzzle_production.current_fixtures import make, checkout, brief_job

ID='pz-workspace-test'


def put(root,name,value):
    raw=p.data(value) if not isinstance(value,bytes) else value
    target=root/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    return {'file':name,'sha256':io.checksum(raw),'bytes':len(raw)}


def metadata_job(root, puzzle_id=ID, title="Synthetic"):
    record = brief_job(puzzle_id, git(root,"rev-parse","HEAD").decode().strip())
    record["title"] = title
    name = current_authoring.path(puzzle_id)
    put(root,name,record)
    index = p.parse((root/INDEX).read_bytes())
    if not any(row["puzzle_id"] == puzzle_id for row in index["entries"]):
        index["entries"].append({"puzzle_id":puzzle_id,"revision":"current","record":name})
        put(root,INDEX,index)


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory(prefix='current-pw-');self.addCleanup(temp.cleanup)
        self.root=Path(temp.name);self.repo=checkout(self.root/'repo')
        git(self.repo,'init','-q','-b','main');git(self.repo,'config','core.autocrlf','false');commit(self.repo)
        self.branch='content/pw/'+ID;git(self.repo,'checkout','-qb',self.branch)
        metadata_job(self.repo);commit(self.repo)
        self.input=make(self.root/'input',identifier=ID)
        catalog_integration.integrate(self.input,self.repo,apply=True)
        self.head=commit(self.repo)
        self.remote=self.root/'remote';self.remote.mkdir();git(self.remote,'init','--bare','-q');self.push()
        configure(self.repo,self.root/'state',remote=str(self.remote));self.reader=Repository(self.root/'state')

    def push(self):git(self.repo,'push','--force',str(self.remote),'main',self.branch)

    def integrate(self,mode='merge'):
        git(self.repo,'checkout','-q','main')
        if mode=='copy':
            source=GitSource(self.repo)
            live=current_delivery.from_source(source,self.head,ID)
            for name in {*live['files'],current_content.RUNTIME}:
                put(self.repo,name,source.read(self.head,name,64*1024*1024))
            if git(self.repo,'status','--porcelain').strip():commit(self.repo)
        else:
            git(self.repo,'-c','user.name=Synthetic','-c','user.email=test@example.invalid','merge',
                '--squash' if mode=='squash' else '--no-ff','--no-edit',self.head)
            if mode=='squash':commit(self.repo)
        main=git(self.repo,'rev-parse','HEAD').decode().strip()
        git(self.repo,'checkout','-q',self.branch);self.push();return main

    def test_fresh_main_and_unchanged_branch_hide_registered_job(self):
        before=self.reader.refresh();self.assertEqual({j['revision'] for j in before['jobs']},{'current'})
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
        registered_branch_record = current_authoring.path(ID)
        put(self.repo, registered_branch_record, b'{broken')
        branch = commit(self.repo)
        git(self.repo, 'checkout', '-q', 'main')
        put(self.repo, registered_branch_record, b'old unreadable record')
        metadata_job(self.repo, puzzle_id='pz-open')
        metadata_job(self.repo, puzzle_id='pz-broken')
        put(self.repo, current_authoring.path('pz-broken'), b'{broken')
        commit(self.repo)
        self.push()
        original = GitSource.read

        def trap(source, at, name, *args, **kwargs):
            self.assertNotEqual(at, branch, 'Registered production branch was opened')
            self.assertNotIn('/' + ID + '/', name)
            self.assertNotIn('/packages/', name)
            self.assertTrue(name == current_content.RUNTIME or not name.startswith(('game/','content/puzzles/')))
            return original(source, at, name, *args, **kwargs)

        with patch.object(GitSource, 'read', trap):
            listing = self.reader.refresh()
        self.assertEqual({j['puzzle_id'] for j in listing['jobs']}, {'pz-open'})
        self.assertEqual(listing['completion']['completed_ids'], [ID])
        self.assertEqual(len(listing['errors']), 1)
        self.assertIn('pz-broken/current', listing['errors'][0])

    def test_later_live_changes_and_reopened_phases_stay_hidden(self):
        self.integrate('copy')
        metadata_job(self.repo,title='Reopened')
        commit(self.repo)
        git(self.repo, 'checkout', '-q', 'main')
        from tools.puzzle_production import catalog_metadata as metadata
        metadata.apply(self.repo,metadata.plan(self.repo,[{"op":"set_metadata","id":ID,"name":"Later name"}]))
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
        metadata_job(self.repo, puzzle_id='pz-open')
        main = commit(self.repo)
        self.push()
        service = Service(self.reader)
        first = service.listing(refresh=True)
        self.assertEqual({j['puzzle_id'] for j in first['jobs']}, {'pz-open'})
        self.assertTrue(first['completion']['confirmed'])

        valid = p.parse((self.repo / current_content.RUNTIME).read_bytes())
        valid['entries'].append(dict(valid['entries'][0]))
        put(self.repo, current_content.RUNTIME, valid)
        metadata_job(self.repo, puzzle_id='pz-new')
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
