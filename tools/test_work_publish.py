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
        branch = 'refs/heads/content/pw/pz-current'
        tag = 'refs/tags/work-prod-pz-current'
        self.assertEqual(guard.remote_head(self.root, branch), second)
        real_delete_ref = pub.delete_ref

        def interrupted_branch(root, ref, expected):
            if ref == branch:
                raise ConnectionError('Lost branch write')
            return real_delete_ref(root, ref, expected)

        with patch.object(pub, 'delete_ref', side_effect=interrupted_branch), self.assertRaises(ConnectionError):
            pub.finish(self.root, 'pz-current', second, confirmed=True)
        self.assertIsNone(guard.remote_head(self.root, tag))
        self.assertEqual(guard.remote_head(self.root, branch), second)
        self.assertEqual(pub.finish(self.root,'pz-current',second,confirmed=True),'closed')
        self.assertIsNone(guard.remote_head(self.root, branch))
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

    def test_confirmed_p2_without_local_gh_recovers_and_closes_only_bound_job(self):
        self.confirmed_p2(lose_delete_reply=True)

    def test_confirmed_p2_worker_authenticates_and_fails_closed_before_deletion(self):
        self.confirmed_p2(lose_delete_reply=False)

    def confirmed_p2(self, *, lose_delete_reply):
        from datetime import datetime, timezone
        from io import BytesIO
        import os
        import shutil
        from types import SimpleNamespace
        from urllib.error import HTTPError
        from urllib.parse import parse_qs, urlsplit
        from tools import work_removal
        from tools.production_workspace import repository as pw
        from tools.production_workspace.release_channel import GitHub
        from tools.production_workspace.server import Service
        from tools.test_production_installer import MemoryGitHub

        self.fixture.approved()
        expected = pub.push_job(self.root, 'pz-current', None)
        branch = 'content/pw/pz-current'
        request = pw.removal_request('pz-current', expected, self.main, [])
        tag = 'refs/tags/work-prod-pz-current'
        fixtures.git(self.remote, 'update-ref', 'refs/heads/content/pw/pz-other', self.main)
        state = self.fixture.work / 'p2-state'
        pw.configure(self.root, state, remote=self.remote)
        app = Service(pw.Repository(state))
        actor = {'full_name': pub.REPO}
        event = {'action': 'completed', 'repository': actor, 'workflow_run': {
            'path': '.github/workflows/work-growth.yml', 'event': 'push', 'conclusion': 'success',
            'repository': actor, 'head_repository': actor, 'head_branch': request, 'head_sha': self.main,
            'created_at': datetime.now(timezone.utc).isoformat()}}
        lock_api = GitHub('synthetic-worker-token')
        self.enterContext(patch.object(lock_api, 'request', side_effect=MemoryGitHub().request))
        worker_pages = []
        request_ref = 'refs/heads/' + request
        work_ref = 'refs/heads/' + branch
        receipt = pw.removal_receipt(expected, self.main)
        worker_prs = []
        fail_at = None
        in_worker = False

        def open_api(req, *, timeout):
            url = urlsplit(req.full_url)
            self.assertEqual((url.scheme, url.netloc, timeout), ('https', 'api.github.com', 10))
            prefix = '/repos/' + pub.REPO
            self.assertTrue(url.path.startswith(prefix))
            endpoint = url.path.removeprefix(prefix)
            self.assertEqual(req.get_method(), 'GET')
            self.assertEqual(req.get_header('Authorization'),
                             'Bearer synthetic-worker-token' if in_worker else None)
            if in_worker:
                self.assertEqual(endpoint, '/pulls')
            if endpoint == '/pulls':
                self.assertEqual(parse_qs(url.query), {
                    'state': ['all'], 'head': ['venomenon328:' + branch], 'per_page': ['100'], 'page': ['1']})
                if in_worker:
                    worker_pages.append(req.full_url)
                    if len(worker_pages) == fail_at:
                        raise HTTPError(req.full_url, 403, 'rate limit exceeded', {}, None)
                value = worker_prs if in_worker else []
            elif endpoint == '':
                value = {**actor, 'private': False}
            else:
                self.assertIn(endpoint, ('/releases/11', '/releases/tags/work-prod-pz-current'))
                if self.release is None:
                    raise HTTPError(req.full_url, 404, 'not found', {}, None)
                value = self.release
            return BytesIO(json.dumps(value).encode())

        def confirm():
            listing = app.listing(refresh=True)
            job = next(j for j in listing['jobs'] if j['ref'] == branch)
            selected = {'snapshot': listing['snapshot'], 'job_id': job['id']}
            plan = app.removal_preview(selected)
            return app.removal_confirm({**selected, 'plan_id': plan['plan_id'], 'confirmation': branch})

        real_git = Path(shutil.which('git')).resolve()
        if os.name == 'nt':
            git_path = real_git.parent
        else:
            git_path = self.fixture.work / 'git-only'
            git_path.mkdir()
            (git_path / 'git').symlink_to(real_git)
        self.enterContext(patch.dict(os.environ, PATH=str(git_path)))
        os.environ.pop('GH_TOKEN', None)
        os.environ.pop('GITHUB_TOKEN', None)
        self.assertTrue(shutil.which('git'))
        self.assertIsNone(shutil.which('gh'))
        self.enterContext(patch.object(pw, 'github_identity', side_effect=lambda url: url == self.remote))
        self.enterContext(patch.object(pw, 'build_opener', return_value=SimpleNamespace(open=open_api)))

        def worker():
            nonlocal in_worker
            worker_pages.clear()
            in_worker = True
            try:
                work_removal.service(self.root, event, lock_api)
            finally:
                in_worker = False

        def reject_worker(error):
            def rejected(_delay):
                with self.assertRaisesRegex(ValueError, error):
                    worker()
                self.assertIsNone(guard.remote_head(self.root, request_ref))

            with patch.object(pw, 'sleep', side_effect=rejected):
                result = confirm()
            self.assertFalse(result['removed'])
            self.assertNotIn('receipt_id', result)
            self.assertEqual(guard.remote_head(self.root, work_ref), expected)
            self.assertEqual(guard.remote_head(self.root, tag), self.main)
            self.assertIsNotNone(self.release)
            self.assertTrue(self.assets)

        if not lose_delete_reply:
            for fail_at in (1, 2):
                with self.subTest(failed_pr_check=fail_at):
                    reject_worker('GitHub-Status nicht prüfbar')
                    self.assertEqual(len(worker_pages), fail_at)
            fail_at = None
            for state, head, error in (
                    ('open', {'ref': branch, 'repo': actor}, 'Pull request facts changed'),
                    ('closed', {'ref': branch, 'repo': actor}, 'Pull request facts changed'),
                    ('closed', {'ref': branch, 'repo': {'full_name': 'other/picross'}}, 'PR-Quelle'),
                    ('closed', {'ref': 'content/pw/pz-other', 'repo': actor}, 'PR-Quelle')):
                with self.subTest(state=state, head=head):
                    worker_prs[:] = [{'state': state, 'number': 9, 'merged_at': None, 'head': head}]
                    reject_worker(error)
            worker_prs.clear()

        def lost_reply(_delay):
            def interrupted(path, method='GET', value=None):
                response = self.api(path, method, value)
                if method == 'DELETE':
                    raise TimeoutError('Release removed, response lost')
                return response
            with patch.object(pub, 'api', side_effect=interrupted), self.assertRaises(TimeoutError):
                worker()
            self.assertIsNone(guard.remote_head(self.root, request_ref))

        if lose_delete_reply:
            with patch.object(pw, 'sleep', side_effect=lost_reply):
                result = confirm()
            self.assertFalse(result['removed'])
            self.assertNotIn('receipt_id', result)
            self.assertIsNone(self.release)
            self.assertFalse(self.assets)
            self.assertEqual(guard.remote_head(self.root, tag), self.main)
            self.assertEqual(guard.remote_head(self.root, work_ref), expected)

        def acknowledge(_delay):
            worker()
            self.assertEqual(len(worker_pages), 3)
            self.assertEqual(guard.remote_head(self.root, request_ref), receipt)
            self.assertIsNone(self.release)
            self.assertFalse(self.assets)
            self.assertEqual(guard.remote_head(self.root, tag), self.main)
            self.assertEqual(guard.remote_head(self.root, work_ref), expected)

        with patch.object(pw, 'sleep', side_effect=acknowledge):
            self.assertTrue(confirm()['removed'])
        for ref in (request_ref, work_ref, tag):
            self.assertIsNone(guard.remote_head(self.root, ref))
        self.assertEqual(guard.remote_head(self.root, 'refs/heads/content/pw/pz-other'), self.main)
        self.assertEqual(guard.remote_head(self.root, 'refs/heads/main'), self.main)

    def test_removal_worker_requires_own_push_and_exact_request_namespace(self):
        from tools import work_removal
        actor = {'full_name': pub.REPO}
        expected = 'a' * 40
        name = 'work-prod-control/remove/pz-current/' + expected + '/' + 'b' * 32
        run = {'repository': actor, 'head_repository': actor, 'path': '.github/workflows/work-growth.yml',
               'event': 'push', 'conclusion': 'success', 'head_sha': self.main, 'head_branch': name}
        event = {'action': 'completed', 'repository': actor, 'workflow_run': run}
        self.assertEqual(work_removal.request_event(event), (name, self.main, 'pz-current', expected))
        for key, value in (('event', 'pull_request'), ('conclusion', 'skipped'), ('path', 'other.yml'),
                           ('head_repository', {'full_name': 'other/repo'}), ('head_branch', 'main'),
                           ('head_branch', name + '/extra'), ('head_branch', name.replace(expected, 'short'))):
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                work_removal.request_event({**event, 'workflow_run': {**run, key: value}})

    def test_removal_worker_rejects_stale_or_unbound_requests_before_pr_lookup(self):
        from datetime import datetime, timedelta, timezone
        from tools import work_removal

        actor = {'full_name': pub.REPO}
        expected = 'a' * 40
        name = work_removal.pw.removal_request('pz-current', expected, self.main, [])
        request = 'refs/heads/' + name
        main = 'refs/heads/main'
        work = 'refs/heads/content/pw/pz-current'
        refs = {main: self.main, request: self.main, work: expected}
        now = datetime.now(timezone.utc)
        run = {'repository': actor, 'head_repository': actor, 'path': '.github/workflows/work-growth.yml',
               'event': 'push', 'conclusion': 'success', 'head_sha': self.main, 'head_branch': name}
        for ref, changed, offset in (
                (main, 'b' * 40, 0), (request, None, 0), (work, 'b' * 40, 0),
                (main, self.main, -601), (main, self.main, 60)):
            with self.subTest(ref=ref, changed=changed, offset=offset):
                event = {'action': 'completed', 'repository': actor, 'workflow_run': {
                    **run, 'created_at': (now + timedelta(seconds=offset)).isoformat()}}
                live = {**refs, ref: changed}
                with (patch.object(guard, 'remote_head', side_effect=lambda _root, target: live[target]),
                      patch.object(guard, 'git', return_value=self.main.encode()) as git,
                      patch.object(work_removal.pw.ProductionRemoval, 'pull_requests') as prs,
                      patch.object(work_removal, 'app_catalog_writer') as lock):
                    with self.assertRaisesRegex(ValueError, 'Request expired, withdrawn or superseded'):
                        work_removal.service(self.root, event, None)
                prs.assert_not_called()
                lock.assert_not_called()
                if live[request] == self.main:
                    self.assertEqual(git.call_args.args[-1], ':' + request)
                    self.assertIn('--force-with-lease=' + request + ':' + self.main, git.call_args.args)
                else:
                    git.assert_called_once_with(self.root, 'rev-parse', 'HEAD')

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
