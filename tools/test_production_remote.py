"""Synthetic PW-REMOTE-A transport. Git, asset bytes, proof and registration are real locally."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

from tools import production_remote as remote, production_remote_pr as prs, publish_git as git, work_publish as pw
from tools import production_remote_delivery as delivery, production_remote_inspect as inspect
from tools import test_work_publish as publication
from tools.production_workspace.sources import GitSource
from tools.puzzle_production import catalog_io as io, current_authoring as current
from tests.puzzle_production import test_current_authoring as fixtures


def background_offer(f):
    """Create two synthetic originals and bind the actor's inspection of the chosen derivative."""
    from io import BytesIO
    from PIL import Image
    f.job = current.upgrade(f.job)
    f.job['selected']['raster'] = f.job['rasters'][0]['id']
    fixtures.decide(f.job, 'raster')
    f.job['state'] = 'background_review'
    for pos, key in enumerate(('cloud', 'sky'), 1):
        pixels = Image.new('RGBA', (30, 10))
        pixels.putpixel((pos, 5), (20, 30, 40, 255))
        stream = BytesIO()
        pixels.save(stream, format='PNG')
        asset = f.asset(key, 'background')
        asset.update(file=f.file(key+'.png', stream.getvalue()), profile='picross-background-png2304x768-v1', prepared=None)
        f.job['assets'].append(asset)
    f.finding('sky', 'stroke', 'Q-HG04', 'stroke-quality')
    f.publish()
    draft = deepcopy(f.job)
    selected = current.findings.subjects(draft)['sky']
    output = f.work / 'viewed-background.png'
    viewed = current.prepare_background(f.sources/'sky.png', output, profile_id=selected['profile'])
    with Image.open(output) as image:
        assert image.size == (2304, 768)
    draft['selected']['background'] = 'sky'
    selected['prepared'] = {'original_sha256': selected['file']['sha256'], 'profile': selected['profile'], 'file': viewed}
    row = draft['findings'][0]
    f.accept(row)
    declaration = {k: v for k, v in row['decision'].items() if k not in ('source', 'binding')}
    for scope in ('background', 'final', 'integration'):
        fixtures.decide(draft, scope)
    return {'background': 'sky', 'decisions': [d for d in draft['decisions'] if d['scope'] in ('background','final','integration')],
            'prepared_review': {'sha256': viewed['sha256'], 'profile': selected['profile'],
                                'original_sha256': selected['file']['sha256'], 'review': selected['review']},
            'finding_decisions': [{**declaration, 'expected': row['decision']['binding'], 'id': row['id'], 'target': 'sky'}]}


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
        for name in (method, 'game/data/background-capability.json'):
            (self.f.root / name).write_bytes((remote.TOOLS / name).read_bytes())
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
            return {'total_count': len(names) + 1, 'jobs': [{'name': 'review-attachment', 'head_sha': head, 'run_id': 11,
                'conclusion': 'skipped'}] + [{'name': n, 'head_sha': head, 'run_id': 11, 'conclusion': 'success',
                'steps': [{'name': f'PR 2 / {head} / {self.main} / {merge}', 'conclusion': 'success'}]} for n in names]}
        return self.fixture.api(path, method, value)

    def req(self, op, work, data, **extra):
        return {'format': 'pw-remote-v1', 'repository': pw.REPO, 'job': self.job, 'operation': op,
                'expected': work, 'record_sha256': io.checksum(self.read_record(work, self.job)),
                'main': self.main, 'tools': self.main, 'input': data, **extra}

    def execute(self, req, area=None, **kwargs):
        return remote.run(area or self.area, req, 'env', 'synthetic-token', **kwargs)

    def test_v3_background_and_incomplete_asset_cleanup(self):
        f = self.f
        f.input = fixtures.make(f.work / 'current-input', method='picross-difficulty-0.4')
        f.incoming = io.json_bytes((f.input / 'manifest.json').read_bytes(), current.LIMIT)
        f.publish()
        f.raster_ready()
        options = background_offer(f)
        before = pw.push_job(f.root, self.job, None)
        self.check_background_delivery(before, options)
        req = self.req('step5', before, options, issue=1)
        missing_view = {k: v for k, v in options.items() if k != 'prepared_review'}
        cases = [(missing_view, 'Actual prepared background review'),
                 ({**options, 'finding_decisions': []}, 'Stale decision|blocked'),
                 ({**options, 'prepared_review': {**options['prepared_review'], 'sha256': '0' * 64}},
                  'Stale or incomplete prepared background review')]
        for data, error in cases:
            with self.subTest(error=error), self.assertRaisesRegex(ValueError, error):
                self.execute({**req, 'input': data})
        deleted = []
        def interrupt(path, method='GET', value=None):
            if method == 'DELETE' and path.startswith('releases/assets/'):
                deleted.append(int(path.split('/')[-1]))
                raise ConnectionError('interrupted asset removal')
            return self.api(path, method, value)
        with patch.object(pw, 'api', side_effect=interrupt), self.assertRaises(ConnectionError):
            self.execute(req)
        self.assertTrue(deleted)
        fresh = f.work / 'new-actor'
        fresh.mkdir()
        with self.assertRaisesRegex(ValueError, 'asset cleanup open.*' + str(deleted[0])):
            self.execute(req, fresh)
        self.assertEqual(self.post_count, 0)
        self.fixture.upload('work-prod-' + self.job, 'original-' + 'f' * 64, b'foreign')
        foreign = self.fixture.next_id
        with self.assertRaisesRegex(ValueError, 'unbound IDs.*' + str(foreign)):
            self.execute(req)
        self.assertEqual(self.post_count, 0)
        self.assertEqual(self.fixture.assets[foreign], b'foreign')
        self.fixture.api('releases/assets/' + str(foreign), 'DELETE')  # Independent fixture owner.
        done = self.execute(req)
        self.assertEqual(done['status'], 'checks-passed')
        self.assertEqual(self.execute(req, fresh)['head'], done['head'])
        self.assertEqual(self.post_count, 1)
        record = pw.bound_record(self.read_record(done['work'], self.job), self.job)
        self.assertEqual(record['selected']['background'], 'sky')
        self.assertEqual(record['assets'][-1]['prepared']['file']['sha256'], options['prepared_review']['sha256'])
        product_request = self.req('inspect-product', done['work'], {'items': [
            {'role': 'product-' + part, 'candidate': record['selected'][choice]}
            for part, choice in [('definition', 'raster'), ('background', 'background'), ('reveal', 'reveal')]
        ]}, product=done['head'], pr=2)
        for item in delivery.sources(product_request, record):
            ref = item['source']
            self.assertEqual(io.checksum(GitSource(self.repo).read(done['head'], ref['file'])), ref['sha256'])
        self.assertTrue(current.findings.effective(record['findings'][0]))
        fixtures.git(self.repo, 'update-ref', 'refs/heads/main', done['head'], self.main)
        fixtures.git(self.toolbox, 'pull', '--ff-only')
        self.pr.update(state='closed', merged=True, merged_at='2026-11-24T12:00:00Z', merge_commit_sha=done['head'])
        retire = self.req('retire', done['work'], {}, pr=2, product=done['head'])
        retire.update(main=done['head'], tools=done['head'])
        self.assertEqual(self.execute(retire, fresh)['status'], 'closed')
        self.assertEqual(self.execute(retire)['status'], 'no-op')

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

        review = {'candidate': 'remote', 'definition_sha256': step3['files']['definition']['sha256'],
                  'preview_sha256': step3['files']['preview']['sha256'], 'ready': True,
                  'observations': [], 'review': fixtures.judgment(current.CRITERIA['raster'])}
        bad = self.req('step3', second, {'assessment': {**review, 'preview_sha256': '0' * 64}})
        with self.assertRaisesRegex(ValueError, 'Different published raster'):
            self.execute(bad)
        assessed = self.execute(self.req('step3', second, {'assessment': review}))['work']
        self.assertEqual(pw.bound_record(self.read_record(assessed, self.job), self.job)['budgets'],
                         pw.bound_record(self.read_record(second, self.job), self.job)['budgets'])
        second = assessed
        # The actor now selects this assessed offer. Supply final decisions separately.
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


    def check_background_delivery(self, work, options):
        from zipfile import ZipFile, ZipInfo
        from tools import work_refs
        req = self.req('inspect', work, {'items': [{'role': r, 'candidate': 'sky'} for r in ('background', 'prepared')]})
        raw = self.read_record(work, self.job)
        ctx = delivery.context(req, 'b' * 40, 42, 2, 40, 1)
        self.fixture.repository['id'] = delivery.REPOSITORIES[pw.REPO]
        lock = 'refs/heads/' + pw.release_catalog.LOCK_BRANCH
        fixtures.git(self.repo, 'update-ref', lock, self.main)
        with patch.object(work_refs, 'FIXTURE', True), patch.object(work_refs, 'TEST_JOB', self.job):
            _, record, release = inspect.bound(self.repo, req)
            with self.assertRaisesRegex(ValueError, 'Stale record'):
                inspect.bound(self.repo, {**req, 'record_sha256': '0' * 64})
            with patch.dict(release, id=release['id'] + 1), patch.object(pw, 'api', side_effect=lambda path:
                    release if path.startswith('releases/') else self.api(path)), self.assertRaises(ValueError):
                inspect.bound(self.repo, req)
        files = self.f.work / 'delivery'
        reads = []
        def read(ref):
            reads.append(ref['asset']['asset_id'])
            return self.fixture.assets[reads[-1]]
        info = inspect.stage(req, record, ctx, files, read, lambda: None)
        self.assertEqual((info['original_count'], len(reads)), (1, 1))
        self.assertEqual(io.checksum((files / 'prepared.png').read_bytes()), options['prepared_review']['sha256'])
        self.assertEqual(git.remote_head(self.repo, lock), self.main)
        self.assertEqual(git.remote_head(self.repo, 'refs/heads/content/pw/' + self.job), work)
        fixtures.git(self.repo, 'update-ref', '-d', lock, self.main)
        for role, candidate in [('motif', 'sky'), ('prepared', 'absent'), ('command', 'sky')]:
            with self.assertRaises(ValueError):
                delivery.sources({**req, 'input': {'items': [{'role': role, 'candidate': candidate}]}}, record)
        archive = self.f.work / 'actual.zip'
        now = datetime.now(timezone.utc)
        def pack(extra=None):
            with ZipFile(archive, 'w') as zipfile:
                for path in files.iterdir():
                    if extra == 'symlink' and path.name == 'prepared.png':
                        link = ZipInfo(path.name)
                        link.external_attr = 0o120777 << 16
                        zipfile.writestr(link, path.read_bytes())
                    else:
                        zipfile.write(path, path.name)
                if extra and extra != 'symlink':
                    zipfile.writestr(extra, b'foreign')
            return {'id': 11, 'name': delivery.artifact_name(ctx), 'expired': False,
                    'workflow_run': {'id': 42, 'head_sha': req['main'], 'head_branch': 'main',
                                     'repository_id': ctx['repository_id'], 'head_repository_id': ctx['repository_id']},
                    'created_at': now.isoformat(), 'expires_at': (now + timedelta(days=1)).isoformat(),
                    'size_in_bytes': archive.stat().st_size, 'digest': 'sha256:' + io.checksum(archive.read_bytes())}
        def verify(row, **args):
            return delivery.verify_archive(archive, row, ctx, req, raw, artifact_id=11, **args)
        meta = pack()
        for change in ({'name': 'wrong-attempt'}, {'size_in_bytes': 1}, {'expired': True},
                       {'id': 12}, {'digest': 'sha256:' + '0' * 64}):
            with self.assertRaises(ValueError):
                verify({**meta, **change})
        output = self.f.work / 'opened'
        files_checked = verify(meta, output=output)['files']
        self.assertEqual([f['role'] for f in files_checked], ['background', 'prepared'])
        self.assertEqual((output / 'prepared.png').read_bytes(), (files / 'prepared.png').read_bytes())
        for extra in ('../foreign', 'extra.json', 'symlink', 'manifest.json'):
            with self.assertRaisesRegex(ValueError, 'archive members'):
                verify(pack(extra))
        (files / 'background.png').write_bytes(b'different')
        with self.assertRaisesRegex(ValueError, 'member length|member bytes'):
            verify(pack())


class RequestRefTests(unittest.TestCase):
    def test_fresh_archive_recovers_after_transient_missing_binary(self):
        from tempfile import TemporaryDirectory
        replies = [(1, b'HTTP 404', b'partial'), (0, b'', b'original')]
        def get(command, *, stdout, **kwargs):
            code, error, data = replies.pop(0)
            stdout.write(data)
            return subprocess.CompletedProcess(command, code, stderr=error)
        with TemporaryDirectory() as tmp, patch.object(inspect.subprocess, 'run', side_effect=get), patch.object(inspect, 'sleep'):
            archive = Path(tmp) / 'delivery.zip'
            inspect.download_uploaded(27, archive)
            self.assertEqual(archive.read_bytes(), b'original')

    def test_motif_choice_preflight_without_image_packages(self):
        import sys
        code = ("from tools.production_remote import validate_editorial; "
                "validate_editorial({'choice': {'candidate': 'motif', 'motif_sha256': 'a'*64, 'approved': [{}], "
                "'declaration': {'actor':'Test','statement':'Choose motif','timestamp_utc':'2026-11-24T00:00:00Z'}}})")
        subprocess.run([sys.executable, '-S', '-B', '-c', code], cwd=remote.TOOLS, check=True)

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
