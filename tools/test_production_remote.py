"""Synthetic PW-REMOTE-A transport. Git, asset bytes, proof and registration are real locally."""
from copy import deepcopy
import os
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

from tools import production_remote as remote, production_remote_pr as prs, publish_git as git, work_publish as pw
from tools import test_work_publish as publication
from tools.production_workspace.sources import GitSource
from tools.puzzle_production import catalog_io as io, current_authoring as current
from tests.puzzle_production import test_current_authoring as fixtures


class RemoteTests(unittest.TestCase):
    def setUp(self):
        fixture = publication.WorkPublicationTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.fixture = fixture
        self.f = fixture.fixture
        self.job = 'pz-current'
        self.repo = Path(fixture.remote)
        self.pr = None
        self.state = 'success'
        self.post_count = 0
        self.enterContext(patch.dict(os.environ, GIT_AUTHOR_NAME='Synthetic', GIT_COMMITTER_NAME='Synthetic',
            GIT_AUTHOR_EMAIL='fixture@example.invalid', GIT_COMMITTER_EMAIL='fixture@example.invalid'))
        self.enterContext(patch.object(pw, 'api', side_effect=self.api))
        self.enterContext(patch.object(pw, 'remote_record', side_effect=self.read_record))
        method = 'content/difficulty-method.json'
        (self.f.root / method).write_bytes((remote.TOOLS / method).read_bytes())
        self.main = fixtures.commit(self.f.root, 'synthetic current method')
        fixtures.git(self.f.root, 'push', str(self.repo), self.main + ':refs/heads/main')
        self.f.job['source_commit'] = self.main
        self.toolbox = self.f.work / 'trusted'
        subprocess.run(['git', 'clone', '-qb', 'main', str(self.repo), str(self.toolbox)], check=True)
        self.enterContext(patch.object(remote, 'TOOLS', self.toolbox))
        self.area = self.f.work / 'run'
        self.area.mkdir()

    def read_record(self, commit, job):
        return GitSource(self.repo).read(commit, current.path(job))

    def api(self, path, method='GET', value=None):
        repo = {'full_name': pw.REPO}
        if path.startswith('actions/workflows/') and '?' not in path:
            name = path.split('/')[-1]
            return {'id': 8 if name == prs.WORKFLOW else 9, 'state': 'active', 'path': '.github/workflows/' + name}
        if path.startswith('issues/'):
            return {'number': 1}
        if path.startswith('git/commits/'):
            commit = path.split('/')[-1]
            return {'sha': commit, 'parents': [{'sha': fixtures.git(self.repo, 'rev-parse', commit + '^')}],
                    'message': fixtures.git(self.repo, 'show', '-s', '--format=%B', commit)}
        if path.startswith('pulls?'):
            return [deepcopy(self.pr)] if self.pr else []
        if path == 'pulls' and method == 'POST':
            self.post_count += 1
            head = fixtures.git(self.repo, 'rev-parse', 'refs/heads/' + value['head'])
            self.pr = {'number': 2, 'state': 'open', 'body': value['body'], 'merged': False, 'merged_at': None,
                       'head': {'repo': repo, 'ref': value['head'], 'sha': head},
                       'base': {'repo': repo, 'ref': 'main', 'sha': self.main},
                       'mergeable': True, 'merge_commit_sha': 'c' * 40}
            raise ConnectionError('lost PR response')
        if path == 'pulls/2':
            return deepcopy(self.pr)
        if path.startswith('actions/workflows/8/runs?'):
            return {'workflow_runs': [] if self.state == 'missing' else [{
                'id': 11, 'workflow_id': 8, 'path': '.github/workflows/ci-modular.yml', 'event': 'pull_request',
                'head_sha': 'e' * 40 if self.state == 'wrong-head' else self.pr['head']['sha'],
                'head_branch': self.pr['head']['ref'], 'head_repository': repo, 'repository': repo,
                'run_attempt': 2, 'status': 'completed', 'conclusion': self.state if self.state == 'action_required' else 'success'}]}
        if path == 'actions/runs/11/attempts/2/jobs?per_page=100':
            head = self.pr['head']['sha']
            merge = 'd' * 40 if self.state == 'wrong-merge' else self.pr['merge_commit_sha']
            names = ('docs',) if self.state == 'missing-job' else ('docs', 'verify (source)', 'ci-required')
            return {'total_count': len(names), 'jobs': [{'name': n, 'head_sha': head, 'run_id': 11, 'conclusion': 'success',
                'steps': [{'name': f'PR 2 / {head} / {self.main} / {merge}', 'conclusion': 'success'}]} for n in names]}
        return self.fixture.api(path, method, value)

    def req(self, op, work, data, **extra):
        return {'format': 'pw-remote-v1', 'repository': pw.REPO, 'job': self.job, 'operation': op,
                'expected': work, 'record_sha256': io.checksum(self.read_record(work, self.job)),
                'main': self.main, 'tools': self.main, 'input': data, **extra}

    def execute(self, req, area=None, **kwargs):
        return remote.run(area or self.area, req, 'env', 'synthetic-token', **kwargs)

    def test_bound_raster_product_ci_recovery_and_retirement(self):
        f = self.f
        f.publish()
        f.raster_ready()
        first = pw.push_job(f.root, self.job, None)
        motif = next(a['file'] for a in f.job['assets'] if a['role'] == 'motif')
        design = {'format': 'picross-image-design-v1', 'source_id': 'motif', 'origin': 'fixture', 'rights': 'fixture',
                  'briefing': 'synthetic', 'working_mode': 'faithful', 'width': 3, 'height': 3, 'crop': [0, 0, 12, 12],
                  'fit': 'exact', 'background': '#ffffff', 'alpha_below': 1, 'mode': 'mono',
                  'palette': [{'id': 'ink', 'rgb': '#202020'}],
                  'variants': [{'id': 'remote', 'method': 'area', 'threshold': 128}]}
        raster = self.req('step3', first, {'motif_sha256': motif['sha256'], 'design': design,
                                          'profile': 'line', 'label': '3 × 3 · Monochrom · Fläche'})
        for invalid in ({'command': 'ignored'}, {'operation': 'merge'}, {'repository': 'foreign/repo'},
                        {'tools': 'a' * 40}, {'record_sha256': '0' * 64}):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                self.execute({**raster, **invalid}, diagnose=True)
        self.assertEqual(self.execute(raster, diagnose=True)['work_head'], first)
        step3 = self.execute(raster)
        self.assertTrue(step3['certified'])
        second = step3['work']
        self.assertEqual(second, self.execute(raster)['work'])
        current_ref = 'refs/heads/content/pw/' + self.job
        self.assertEqual(git.remote_head(self.repo, current_ref), second)

        # The actor now inspects and selects this actual offer. Supply final decisions separately.
        actor = f.work / 'actor'
        actor.mkdir()
        paths = remote.ws.prepare(actor, self.job, self.main, self.main, second, originals=True)
        f.root = Path(paths['job'])
        f.job = io.json_bytes((f.root / current.path(self.job)).read_bytes(), current.LIMIT)
        candidate = next(r for r in f.job['rasters'] if r['id'] == 'remote')
        candidate['review'] = fixtures.judgment(current.CRITERIA['raster'])
        f.job['selected']['raster'] = 'remote'
        fixtures.decide(f.job, 'raster')
        f.job['state'] = 'background_review'
        f.publish()
        approved = pw.push_job(f.root, self.job, second)
        f.job['selected']['background'] = 'none'
        for scope in ('background', 'final', 'integration'):
            fixtures.decide(f.job, scope)
        decisions = [d for d in f.job['decisions'] if d['scope'] in ('background', 'final', 'integration')]
        req = self.req('step5', approved, {'background': 'none', 'decisions': decisions}, issue=1)
        with self.assertRaisesRegex(ValueError, 'Actual final'):
            self.execute({**req, 'input': {'background': 'none', 'decisions': []}})
        original_push = git.publish_completion

        def lost(*args):
            original_push(*args)
            raise ConnectionError('lost atomic response')

        with patch.object(git, 'publish_completion', lost), self.assertRaises(ConnectionError):
            self.execute(req)
        fresh = f.work / 'fresh'
        fresh.mkdir()
        result = self.execute(req, fresh)
        self.assertEqual(result['status'], 'checks-passed')
        self.assertEqual(self.post_count, 1)
        self.assertEqual(result['head'], self.execute(req)['head'])
        self.assertEqual(self.post_count, 1)
        completed, product = result['work'], result['head']
        self.assertEqual(git.remote_head(self.repo, current_ref), completed)
        status = self.req('status', completed, {}, pr=2, product=product)
        for state, reported in [('missing', 'missing-ci'), ('action_required', 'approval-or-start-pending'),
                                ('missing-job', 'checks-incomplete')]:
            self.state = state
            self.assertEqual(self.execute(status)['status'], reported)
        for self.state in ('wrong-head', 'wrong-merge'):
            with self.assertRaisesRegex(ValueError, 'Foreign CI|test merge'):
                self.execute(status)
        with self.assertRaisesRegex(ValueError, 'merged product PR'):
            self.execute({**status, 'operation': 'retire'})
        with patch.dict(self.pr, body='foreign'), self.assertRaisesRegex(ValueError, 'Foreign product PR'):
            self.execute(status)
        fixtures.git(self.repo, 'update-ref', 'refs/heads/main', product, self.main)
        fixtures.git(self.toolbox, 'pull', '--ff-only')
        self.pr.update(state='closed', merged=True, merged_at='2026-11-24T10:00:00Z', merge_commit_sha=product)
        retire = {**status, 'main': product, 'tools': product, 'operation': 'retire'}
        lock = 'refs/heads/' + pw.release_catalog.LOCK_BRANCH
        fixtures.git(self.repo, 'update-ref', lock, self.main, '0' * 40)
        with self.assertRaisesRegex(ValueError, 'owns the catalog'):
            self.execute(retire, fresh)
        self.assertEqual(git.remote_head(self.repo, lock), self.main)
        fixtures.git(self.repo, 'update-ref', '-d', lock, self.main)
        self.assertEqual(self.execute(retire, fresh)['status'], 'closed')
        self.assertEqual(self.execute(retire)['status'], 'no-op')
        self.assertIsNone(self.fixture.release)
        self.assertIsNone(git.remote_head(self.repo, current_ref))
        self.assertIsNone(git.remote_head(self.repo, 'refs/tags/work-prod-' + self.job))


class RequestRefTests(unittest.TestCase):
    def test_trigger_requires_exact_main_tree_parent_live_ref_and_payload(self):
        main, source = 'a' * 40, 'b' * 40
        req = {'format': 'pw-remote-v1', 'repository': pw.REPO, 'job': 'pz-current', 'operation': 'status',
               'main': main, 'tools': main, 'expected': 'c' * 40, 'record_sha256': 'd' * 64,
               'input': {}, 'product': 'e' * 40, 'pr': 2}
        name, message = remote.envelope(req, 'execute')
        ref = 'refs/heads/' + name
        live = {'refs/heads/main': main, ref: source}
        parent = {'sha': main, 'tree': {'sha': 'f' * 40}}
        commit = {'sha': source, 'tree': parent['tree'], 'parents': [{'sha': main}], 'message': message}
        with (patch.object(git, 'remote_head', side_effect=lambda _, r: live.get(r)),
              patch.object(pw, 'api', side_effect=lambda path: parent if path.endswith(main) else commit)):
            self.assertEqual(remote.verify_request('.', name, source, main), (req, 'execute'))
            for bad in ({'tree': {'sha': source}}, {'parents': []}, {'parents': [parent, parent]},
                        {'message': message.replace('execute', 'preflight')}, {'message': message + ' extra'}):
                with patch.dict(commit, bad), self.assertRaises(ValueError):
                    remote.verify_request('.', name, source, main)
            with patch.dict(live, {ref: main}), self.assertRaisesRegex(ValueError, 'withdrawn'):
                remote.verify_request('.', name, source, main)
            with patch.dict(live, {'refs/heads/main': source}), self.assertRaisesRegex(ValueError, 'stale'):
                remote.verify_request('.', name, source, main)

    def test_concurrent_product_create_rejects_both_atomic_ref_changes(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            local = Path(tmp) / 'local'
            target = Path(tmp) / 'target.git'
            local.mkdir()
            fixtures.git(local, 'init', '-qb', 'main')
            fixtures.git(local, 'config', 'user.name', 'Fixture')
            fixtures.git(local, 'config', 'user.email', 'fixture@example.invalid')
            def commit(message):
                fixtures.git(local, 'commit', '--allow-empty', '-qm', message)
                return fixtures.git(local, 'rev-parse', 'HEAD')
            main = commit('main')
            fixtures.git(local, 'clone', '--bare', str(local), str(target))
            work = commit('old work')
            job = 'pz-current'
            work_ref = 'refs/heads/content/pw/' + job
            product_ref = 'refs/heads/' + prs.product_branch(job)
            fixtures.git(local, 'push', str(target), work + ':' + work_ref)
            successor = commit('completion')
            fixtures.git(local, 'switch', '--detach', main)
            product = commit('product')
            original = git.git
            def race(root, *args, **kwargs):
                if '--atomic' in args:
                    fixtures.git(target, 'update-ref', product_ref, main, '0' * 40)
                return original(root, *args, **kwargs)
            with (patch.object(git, 'REMOTE', str(target)), patch.object(git, 'CLEAN_MAIN', main),
                  patch.object(git, 'git', side_effect=race),
                  self.assertRaises((ValueError, subprocess.CalledProcessError))):
                git.publish_completion(local, job, successor, work, product, main)
            self.assertEqual(fixtures.git(target, 'rev-parse', work_ref), work)
            self.assertEqual(fixtures.git(target, 'rev-parse', product_ref), main)
