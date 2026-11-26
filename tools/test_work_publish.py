"""Bounded production transport regressions, using a private Git remote and synthetic pixels."""
import base64
from copy import deepcopy
from hashlib import sha1
from io import BytesIO
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from tools import publish_git as guard, work_publish as pub
from tools.puzzle_production import current_authoring as current, github_rest, work_assets
from tools.production_workspace import presentation
from tools.production_workspace.sources import GitSource
from tests.puzzle_production import test_current_authoring as fixtures


class WorkPublicationTests(unittest.TestCase):
    def test_qualified_local_delivery_across_publish_cli_and_batch_resume(self):
        from tools.puzzle_production import authoring_builder, catalog_profiles, current_rating, verifier, target_adapter
        from tools.puzzle_production import integration_batch_runner as batch, integration_input
        from tests.puzzle_production.test_current_integration import registration_batch
        _, open_job = self.managed()
        f = self.fixture
        f.job = current.upgrade(f.job)
        counts = {}
        for module, fn in ((current, 'image_facts'), (current.Checked, 'raster'), (verifier, 'verify'),
                           (current_rating, 'validate'), (catalog_profiles, 'render_profiles')):
            original = getattr(module, fn)
            def count(*args, _fn=fn, _original=original, **kwargs):
                counts[_fn] = counts.get(_fn, 0) + 1
                return _original(*args, **kwargs)
            self.enterContext(patch.object(module, fn, count))
        f.approved()
        self.assertEqual(counts, {'image_facts':4, 'raster':1, 'verify':1, 'validate':1})
        counts.clear()
        head = pub.push_job(self.root, 'pz-current', None)
        pub.resume(self.root, 'pz-current', head)
        name = current.path('pz-current')
        output = self.area / 'delivery'
        repo = Path(__file__).resolve().parents[1]
        product = Path(open_job(head, integration='content/synthetic-product')['integration'])
        self.assertEqual(authoring_builder.main(['prepare-integration', '--repository', str(self.root),
            '--record', name, '--output-dir', str(output)]), 0)
        args = ['--input', str(output), '--checkout', str(product), '--pw-worktree', str(self.root)]
        # Restart the documented CLI with only the fixture Git endpoint and
        # release metadata. The hydrated originals are already on disk.
        program = """
import sys
from tools import publish_git
from tools.puzzle_production import current_authoring as c, current_rating, catalog_profiles, verifier
from tools.puzzle_production import target_adapter, work_assets
publish_git.REMOTE = sys.argv[1]
release = sys.stdin.buffer.read()
work_assets.get = lambda *args, **kwargs: release
functions = {f.__code__ for f in (c.image_facts, c.Checked.raster, c.prepared_facts, c.render_background,
             c.Checked.crop_diagnosis, current_rating.validate, catalog_profiles.render_profiles, verifier.verify)}
calls = []
def observe(frame, event, arg):
    if event == 'call' and frame.f_code in functions:
        calls.append(frame.f_code.co_name)
sys.setprofile(observe)
code = target_adapter.main(sys.argv[2:])
sys.setprofile(None)
assert code == 0 and not calls, (code, calls)
"""
        subprocess.run([sys.executable, '-B', '-c', program, self.remote, 'plan', *args],
                       cwd=repo, input=json.dumps(self.release).encode(), check=True)
        self.assertFalse(fixtures.git(product, 'status', '--porcelain'))
        self.assertEqual(counts, {})
        self.assertEqual(target_adapter.main(['register', *args]), 0)
        self.assertEqual(target_adapter.main(['register', *args]), 0)
        self.assertEqual(counts, {'render_profiles':1})

        record = self.root / name
        plan = registration_batch(self.area, output, repo, record=record)
        path = f.work / 'plan.json'
        path.write_bytes(current.encoded(plan))
        target = fixtures.checkout(f.work / 'batch-target')
        batch_args = (path, self.area, repo, target, f.work / 'batch-work')
        self.assertEqual(batch.run(*batch_args)['status'], 'completed')
        self.assertEqual(batch.resume(*batch_args)['status'], 'completed')
        self.assertEqual(counts, {'render_profiles':2})

        proof = output / 'proof.json'
        original = proof.read_bytes()
        proof.write_bytes(original[:-1] + b'X')
        with self.assertRaisesRegex(ValueError, 'Input changed'):
            integration_input.open_input(output, pw_root=self.root)
        proof.write_bytes(original)
        fixtures.git(product, 'add', '--sparse', '--', 'content', 'game')
        fixtures.git(product, 'commit', '-qm', 'synthetic delivery')
        product_commit = fixtures.git(product, 'rev-parse', 'HEAD')
        current.complete(self.root, name, product_commit, current_input=output)
        self.assertEqual(counts, {'render_profiles':2})
        with self.assertRaisesRegex(ValueError, 'Stale PW delivery'):
            integration_input.open_input(output, pw_root=self.root)
        with self.assertRaisesRegex(ValueError, 'PW worktree'):
            integration_input.open_input(output)

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
        self.api_calls = []
        self.immutability = {'enabled': False}
        self.repository = {'full_name': pub.REPO, 'permissions': {'push': False}}
        for module, name, value in [(guard,'REMOTE',self.remote),(guard,'CLEAN_MAIN',self.main),
                                    (pub,'api',self.api),(pub,'upload',self.publisher_upload),
                                    (pub,'remote_record',self.read_record),
                                    (pub,'select_token',lambda auth: 'synthetic-token'),
                                    (work_assets,'get',self.get)]:
            self.enterContext(patch.object(module,name,value))

    def managed(self, *, test_catalog=True):
        from tools import production_git_workspace as space
        self.area = self.fixture.work / 'Rätsel mit Leerzeichen'
        self.area.mkdir()
        seed = self.fixture.root
        (seed / 'game/art/unused').mkdir(parents=True)
        (seed / 'game/art/unused/unselected.bin').write_bytes(b'x' * 8192)
        # The data revision intentionally has no Python entry point.
        (seed / '.gitignore').write_text('/content/authoring/pz-*/**\n!/content/authoring/pz-*/current/\n'
                                         '!/content/authoring/pz-*/current/record.json\n', encoding='utf-8')
        fixtures.git(seed, 'add', '.gitignore')
        if not test_catalog:
            from tools.puzzle_production.catalog_integration import TEST_CATALOG
            (seed / TEST_CATALOG[0]).unlink()
        self.main = fixtures.commit(seed, 'synthetic data base')
        fixtures.git(seed, 'push', self.remote, self.main + ':refs/heads/main')
        norm = seed / 'docs/production/PAIRED_LINES.md'
        norm.parent.mkdir(parents=True)
        norm.write_text('Synthetic paired-profile instructions.\n', encoding='utf-8')
        fixtures.git(seed, 'add', 'docs/production/PAIRED_LINES.md')
        (seed / 'tools').mkdir()
        (seed / 'tools/version.py').write_text('VERSION = 1\n', encoding='utf-8')
        fixtures.git(seed, 'add', 'tools/version.py')
        fixtures.git(seed, 'commit', '-qm', 'independent synthetic tool revision')
        self.tool = fixtures.git(seed, 'rev-parse', 'HEAD')
        fixtures.git(seed, 'push', self.remote, self.tool + ':refs/heads/trusted-tools')

        def open_job(expected=None, **options):
            return space.prepare(self.area, 'pz-current', self.tool, self.main, expected, **options)
        paths = open_job()
        self.root = self.fixture.root = Path(paths['job'])
        self.fixture.job['source_commit'] = self.main
        fixtures.git(paths['store'], 'config', 'user.name', 'Synthetic writer')
        fixtures.git(paths['store'], 'config', 'user.email', 'local@example.invalid')
        return paths, open_job

    def test_shared_sparse_job_publish_recovery_and_completion(self):
        from tools import production_git_workspace as space, production_worktree_publish as follow
        from tools.puzzle_production import catalog_integration as integration, target_adapter
        from tools.production_workspace import projector
        paths, open_job = self.managed()
        job = 'pz-current'
        branch = 'refs/heads/content/pw/' + job
        f = self.fixture
        other = space.prepare(self.area, 'pz-second', self.tool, self.main, None)
        self.assertNotEqual(paths['job'], other['job'])
        for root in (paths['job'], other['job'], paths['tools']):
            self.assertEqual(space.git_root(Path(root)), Path(paths['store']))
            self.assertFalse((Path(root) / 'game/art/unused/unselected.bin').exists())
        self.assertTrue((Path(paths['tools']) / 'tools/version.py').is_file())
        self.assertTrue((Path(paths['tools']) / 'docs/production/PAIRED_LINES.md').is_file())
        self.assertEqual(fixtures.git(self.root, 'rev-parse', 'origin/main'), self.main)
        self.assertFalse((self.root / 'tools/version.py').exists())
        second_root = Path(other['job'])
        brief = deepcopy(f.job)
        brief.update(puzzle_id='pz-second', title='Independent second job')
        current.build({'format': current.REQUEST, 'record': brief, 'expected': None, 'files': []}, f.sources, second_root)
        other_head = pub.push_job(second_root, 'pz-second', None)
        pub.resume(second_root, 'pz-second', other_head)
        self.assertFalse((self.root / current.path('pz-second')).exists())
        self.assertEqual(pub.finish(second_root, 'pz-second', other_head, confirmed=True), 'closed')
        f.publish()
        self.assertEqual(open_job(), paths)
        first = pub.push_job(self.root, job, None)
        self.assertEqual(fixtures.git(self.root, 'rev-parse', 'HEAD'), first)
        self.assertEqual(pub.push_job(self.root, job, None), first)
        pub.resume(self.root, job, first)
        f.assert_budget_increase()
        f.approved()
        with self.assertRaisesRegex(ValueError, 'Unpublished local draft'):
            pub.finish(self.root, job, first, confirmed=True)
        before = deepcopy(f.job['decisions'])
        real_publish = guard.publish
        def lost_response(root, ref, head, expected, **kwargs):
            result = real_publish(root, ref, head, expected, **kwargs)
            if ref == 'content/pw/' + job:
                raise ConnectionError('lost confirmed ref response')
            return result
        with patch.object(guard, 'publish', lost_response), self.assertRaises(ConnectionError):
            pub.push_job(self.root, job, first)
        second = guard.remote_head(self.root, branch)
        self.assertNotEqual(second, first)
        self.assertEqual(fixtures.git(self.root, 'rev-parse', 'HEAD'), first)
        def interrupt(step):
            if step == 'readback':
                raise InterruptedError('confirmed')
        with patch.object(follow, 'checkpoint', interrupt), self.assertRaises(InterruptedError):
            pub.push_job(self.root, job, first)

        # A new OS process dies at each local write boundary. Its pending state
        # and detached HEAD/index survive and the public publisher finishes it.
        program = """import os, sys
from pathlib import Path
from tools import production_worktree_publish as follow
root, job, parent, base, target, boundary = sys.argv[1:]
op = follow.Publication(Path(root), job, parent, base, target)
follow.checkpoint = lambda step: os._exit(73) if step == boundary else None
op.finish(target)
"""
        for boundary in ('head', 'index', 'record', 'authoring-index'):
            child = subprocess.run([sys.executable, '-B', '-c', program, str(self.root), job, first,
                                    self.main, second, boundary], cwd=Path(__file__).resolve().parents[1])
            self.assertEqual(child.returncode, 73, boundary)
        self.assertEqual(pub.push_job(self.root, job, first), second)
        generation = deepcopy(self.assets)
        self.assertEqual(open_job(second, originals=True)['job'], str(self.root))
        local = json.loads((self.root/current.path(job)).read_bytes())
        self.assertEqual(local['decisions'], before)
        self.assertEqual(self.assets, generation)
        output = f.work / 'final'
        current.prepare(self.root, current.path(job), output)
        export = f.work / 'export'
        target_adapter.export(output, export)
        product_branch = 'content/synthetic-product'
        product = Path(open_job(second, integration=product_branch)['integration'])
        patterns = space.sparse_path(product)
        before_patterns = patterns.read_bytes()
        self.assertFalse((product / integration.TEST_CATALOG[0]).exists())
        self.assertEqual(space.git_root(product), space.git_root(self.root))
        # Occupation is checked against Git even when the path is invisible.
        collision = f.work / 'occupied-product'
        fixtures.git(product, 'worktree', 'add', '--detach', '--no-checkout', str(collision), self.main)
        fixtures.git(collision, 'sparse-checkout', 'set', '--no-cone', '/content/', '/game/data/registry.json',
                     '/game/data/background-capability.json')
        fixtures.git(collision, 'read-tree', '-mu', 'HEAD')
        hidden = 'game/data/content/pz-current.json'
        oid = subprocess.check_output(['git', '-C', str(collision), 'hash-object', '-w', '--stdin'], input=b'occupied').strip().decode()
        fixtures.git(collision, 'update-index', '--add', '--cacheinfo', '100644', oid, hidden)
        fixtures.git(collision, 'commit', '-qm', 'occupied sparse product')
        self.assertFalse((collision / hidden).exists())
        for apply in (False, True):
            with self.assertRaisesRegex(ValueError, 'Occupied sparse'):
                integration.integrate(export, collision, apply=apply)
        plan = integration.integrate(export, product)
        self.assertFalse(space.changes(product))
        with self.assertRaisesRegex(RuntimeError, 'interruption'):
            integration.integrate(export, product, apply=True, fail_step=2)
        from tools.puzzle_production import current_registration
        self.assertEqual(current_registration.recover(product)['status'], 'rolled-back')
        registered = integration.integrate(export, product, apply=True)
        self.assertEqual(registered['status'], 'registered')
        names = [r['path'] for r in plan['changes']]
        fixtures.git(product, 'add', '--sparse', '--', *names)
        fixtures.git(product, 'commit', '-qm', 'selected synthetic product')
        commit = fixtures.git(product, 'rev-parse', 'HEAD')
        self.assertEqual(set(fixtures.git(product, 'diff', '--name-only', self.main, commit).splitlines()), set(names))
        self.assertEqual(guard.publish(product, product_branch, commit, None), commit)
        self.assertEqual(patterns.read_bytes(), before_patterns)
        self.assertFalse(space.changes(product))
        target = product / hidden
        before = target.read_bytes()
        self.assertNotIn(('/' + hidden).encode(), before_patterns.splitlines())

        # Git status can hide an edited path that is marked assume-unchanged.
        fixtures.git(product, 'update-index', '--assume-unchanged', '--', hidden)
        target.write_bytes(b'foreign replacement')
        self.assertFalse(space.changes(product))
        with self.assertRaisesRegex(ValueError, 'Occupied sparse extension'):
            open_job(second, integration=product_branch, integration_head=commit)
        self.assertEqual(target.read_bytes(), b'foreign replacement')
        self.assertEqual(patterns.read_bytes(), before_patterns)
        target.write_bytes(before)
        fixtures.git(product, 'update-index', '--no-assume-unchanged', '--', hidden)
        timestamps = {name: (product / name).stat().st_mtime_ns for name in names}

        (product / 'foreign.txt').write_bytes(b'keep this untracked file')
        with self.assertRaisesRegex(ValueError, 'Unexpected files'):
            open_job(second, integration=product_branch, integration_head=commit)
        (product / 'foreign.txt').unlink()
        reopened = open_job(second, integration=product_branch, integration_head=commit)
        self.assertEqual(Path(reopened['integration']), product)
        self.assertIn(('/' + hidden).encode(), patterns.read_bytes().splitlines())
        self.assertEqual({name: (product / name).stat().st_mtime_ns for name in names}, timestamps)
        self.assertEqual(fixtures.git(product, 'rev-parse', 'HEAD'), commit)
        self.assertEqual(guard.remote_head(product, 'refs/heads/' + product_branch), commit)
        self.assertFalse(space.changes(product))
        self.assertEqual(integration.integrate(export, product)['status'], 'no-op')
        projector.complete(self.root, current.path(job), commit, current_input=export)
        completed = pub.push_job(self.root, job, second)
        fixtures.git(product, 'push', self.remote, commit + ':refs/heads/main')
        self.assertEqual(pub.finish(self.root, job, completed), 'closed')
        self.assertEqual(pub.finish(self.root, job, completed), 'no-op')

    def test_test_only_input_requires_bound_synthetic_catalog(self):
        from tests.puzzle_production.current_fixtures import fingerprints
        from tools.puzzle_production.catalog_integration import TEST_CATALOG
        _, open_job = self.managed(test_catalog=False)
        product = Path(open_job(integration='content/distinct-product')['integration'])
        tool_checkout = Path(__file__).resolve().parents[1]
        self.assertNotEqual(product, tool_checkout)
        name, marker = TEST_CATALOG
        for copied_marker in (False, True):
            if copied_marker:
                (product / name).write_bytes(marker)
            before = fingerprints(product)
            for command in ('plan', 'register'):
                with self.subTest(command=command, copied_marker=copied_marker):
                    result = subprocess.run(
                        [sys.executable, '-B', '-m', 'tools.puzzle_production.target_adapter', command,
                         '--input', str(self.fixture.input), '--checkout', str(product)],
                        cwd=tool_checkout, capture_output=True, check=False, timeout=60)
                    self.assertEqual(result.returncode, 2, result.stderr.decode())
                    self.assertIn('Test-only input cannot enter product catalog', json.loads(result.stdout)['error'])
                    self.assertEqual(fingerprints(product), before)

    def test_workspace_conflicts_and_sparse_namespace(self):
        from tools import production_git_workspace as space
        from tools.puzzle_production.current_registration import Snapshot
        paths, open_job = self.managed()
        with self.assertRaises(ValueError):
            space.prepare(self.area, 'pz-current', self.tool, self.main, None, repository='foreign/repo')
        occupied = self.area / 'foreign'
        occupied.mkdir()
        (occupied / 'picross-production').mkdir()
        with self.assertRaises(ValueError):
            space.store_for(occupied, space.REPO)
        from tools.puzzle_production.authoring_builder import writer
        lock = Path(paths['store']) / 'authoring-builder.lock'
        with writer(lock):
            code = """import sys
from pathlib import Path
from tools.puzzle_production.authoring_builder import writer, BuildError
try:
    with writer(Path(sys.argv[1])):
        sys.exit(1)
except BuildError:
    sys.exit(0)
"""
            child = subprocess.run([sys.executable, '-B', '-c', code, str(lock)],
                                   cwd=Path(__file__).resolve().parents[1])
            self.assertEqual(child.returncode, 0)
            with self.assertRaisesRegex(ValueError, 'writer owns'):
                open_job()
        # Losing the response to lease creation preserves the local nonce.
        owner = {'operation': 'retire', 'job': 'pz-current', 'expected': self.main}
        real_publish = guard.publish
        def lost_lease(*args, **kwargs):
            real_publish(*args, **kwargs)
            raise ConnectionError('lost lease response')
        with patch.object(guard, 'publish', lost_lease), self.assertRaises(ConnectionError):
            with pub.catalog_writer(self.root, self.main, owner=owner):
                self.fail('lost response reached mutation')
        nonce = guard.remote_head(self.root, 'refs/heads/' + pub.release_catalog.LOCK_BRANCH)
        self.assertIsNotNone(nonce)
        with self.assertRaisesRegex(ValueError, 'Different operation owns'):
            with pub.catalog_writer(self.root, self.main, owner={**owner, 'operation': 'publish'}):
                self.fail('foreign nonce admitted')
        with pub.catalog_writer(self.root, self.main, owner=owner):
            self.assertEqual(guard.remote_head(self.root, 'refs/heads/' + pub.release_catalog.LOCK_BRANCH), nonce)
        foreign = self.root / 'unknown'
        foreign.write_bytes(b'preserve')
        with self.assertRaisesRegex(ValueError, 'Unknown staged'):
            open_job()
        fixtures.git(self.root, 'add', '--sparse', 'unknown')
        with self.assertRaisesRegex(ValueError, 'Unknown staged'):
            open_job()
        self.assertEqual(foreign.read_bytes(), b'preserve')
        product = Path(paths['store']).parent / 'collision-test'
        fixtures.git(self.root, 'worktree', 'add', '--detach', '--no-checkout', str(product), self.main)
        fixtures.git(product, 'sparse-checkout', 'set', '--no-cone', '/content/', '/game/data/')
        fixtures.git(product, 'read-tree', '-mu', 'HEAD')
        snapshot = Snapshot(product, 'pz-current')
        for name in ('game/art/unused/unselected.bin', 'game/ART/unused/new', 'game/art/unused/unselected.bin/child',
                     'game/art/unused'):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'Occupied'):
                snapshot.read(name, missing=True)
        self.assertIsNone(snapshot.read('game/art/unused/new.png', missing=True))
        fixtures.git(product, 'add', '--sparse', '-f', '--', 'content/categories.json')
        (product / 'content/categories.json').write_bytes(b'changed')
        with self.assertRaises(ValueError):
            snapshot.recheck()
        if os.name == 'nt':
            with self.assertRaisesRegex(ValueError, 'case collision|Foreign production workspace'):
                space.store_for(self.area.with_name(self.area.name.upper()), space.REPO)
            link = self.area / 'junction'
            subprocess.run(['cmd', '/c', 'mklink', '/J', str(link), str(occupied)], check=True, capture_output=True)
            with self.assertRaisesRegex(ValueError, 'reparse'):
                space.store_for(link, space.REPO)
            link.rmdir()

    def read_record(self, commit, job):
        return GitSource(self.root).read(commit, current.path(job))

    def api(self,path,method='GET',value=None):
        self.api_calls.append((path, method))
        if path == '':
            return self.repository
        if path == 'git/ref/heads/main':
            return {'ref': 'refs/heads/main',
                    'object': {'type': 'commit', 'sha': guard.remote_head(self.root, 'refs/heads/main')}}
        if path.startswith('git/commits/'):
            oid = path.rsplit('/', 1)[1]
            parents = fixtures.git(self.remote, 'show', '-s', '--format=%P', oid).split()
            return {'sha': oid, 'parents': [{'sha': parent} for parent in parents]}
        if path == 'immutable-releases':
            if isinstance(self.immutability, Exception):
                raise self.immutability
            return self.immutability
        if path == 'actions/permissions':
            result = getattr(self, 'settings_access', None)
            if isinstance(result, Exception):
                raise result
            return result
        if path.startswith('releases?'):
            return [deepcopy(self.release)] if self.release else []
        if path == 'releases' and method == 'POST':
            self.assertEqual(value['make_latest'],'false')
            fixtures.git(self.remote,'update-ref','refs/tags/' + value['tag_name'],value['target_commitish'])
            self.release = {**value,'id':11,'immutable':False,'assets':[]}
        if path.startswith('releases/assets/') and method == 'DELETE':
            id_ = int(path.rsplit('/',1)[1])
            self.release['assets'] = [a for a in self.release['assets'] if a['id'] != id_]
            del self.assets[id_]
        if path == 'releases/11' and method == 'DELETE':
            self.release = None
            self.assets.clear()
        return deepcopy(self.release)

    def publisher_upload(self, release_id, tag, name, data):
        self.assertEqual(release_id, self.release['id'])
        self.upload(tag, name, data)

    def upload(self,tag,name,data):
        self.assertEqual(tag, self.release['tag_name'])
        self.next_id += 1
        self.release['assets'].append({'id':self.next_id,'name':name,'size':len(data),'state':'uploaded','label':'picross-original:'+tag})
        self.assets[self.next_id] = data

    def get(self,path,limit,*,binary=False):
        if binary:
            leaf = path.rsplit('/', 1)[1]
            row = next(a for a in self.release['assets'] if leaf in (a['name'], str(a['id'])))
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
        real_upload=self.publisher_upload
        def interrupted(*args):
            real_upload(*args)
            raise ConnectionError('lost upload response')
        plan = pub.preflight(self.root, 'publish', 'pz-current', None)
        self.assertEqual(plan['release_state'], 'disabled')
        self.assertIsNone(self.release)
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
        self.immutability = github_rest.Failure('access', 'no Administration read', 403)
        self.api_calls.clear()
        second=publish(first)
        self.assertNotIn(('immutable-releases', 'GET'), self.api_calls)
        self.assertNotEqual(second,first)
        self.assertEqual(guard.remote_head(self.root, 'refs/heads/content/pw/pz-current'), second)
        resume_root = self.fixture.work / 'resume'
        fixtures.git(self.root, 'worktree', 'add', '--detach', str(resume_root), second)
        pub.preflight(resume_root, 'resume', 'pz-current', second)
        self.assertEqual(pub.resume(resume_root, 'pz-current', second), current.path('pz-current'))
        self.assertEqual((resume_root / view['file']).read_bytes(), original)
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
        pub.preflight(self.root, 'retire', 'pz-current', second)
        self.assertEqual(pub.finish(self.root,'pz-current',second,confirmed=True),'closed')
        self.assertIsNone(guard.remote_head(self.root, branch))
        self.assertEqual(pub.finish(self.root,'pz-current',second,confirmed=True),'no-op')
        self.assertFalse(self.assets)
        self.assertIsNone(guard.remote_head(self.root,'refs/tags/work-prod-pz-current'))

    def assert_early_rejection(self, expected, message):
        refs = fixtures.git(self.remote, 'show-ref')
        self.api_calls.clear()
        with (patch.object(current, 'Checked') as originals, patch.object(pub, 'catalog_writer') as lock,
              self.assertRaisesRegex(ValueError, message)):
            pub.push_job(self.root, 'pz-current', expected)
        originals.assert_not_called()
        lock.assert_not_called()
        self.assertTrue(all(method == 'GET' for _, method in self.api_calls))
        self.assertEqual(fixtures.git(self.remote, 'show-ref'), refs)

    def test_preflight_setting_matrix_and_read_only_404_disambiguation(self):
        failure = github_rest.Failure
        cases = [({'enabled': True}, None, 'setting enabled'),
                 ({'enabled': 0}, None, 'setting unknown'),
                 (None, None, 'setting unknown'),
                 (failure('auth', 'HTTP 401', 401), None, 'HTTP 401'),
                 (failure('access', 'HTTP 403', 403), None, 'HTTP 403'),
                 (failure('access', 'HTTP 404', 404), None, 'setting unknown'),
                 (failure('access', 'HTTP 404', 404), failure('access', 'HTTP 404', 404), 'HTTP 404'),
                 (failure('rate_limit', 'HTTP 429', 429), None, 'HTTP 429'),
                 (failure('network', 'network error'), None, 'network error')]
        for setting, access, message in cases:
            with self.subTest(message=message):
                self.immutability, self.settings_access = setting, access
                self.assert_early_rejection(None, message)
        self.immutability = failure('access', 'HTTP 404', 404)
        self.settings_access = {'enabled': True}
        report = pub.preflight(self.root, 'publish', 'pz-current', None)
        self.assertEqual(report['release_state'], 'disabled')
        self.assertEqual(report['capabilities']['git_refs']['write'], 'unverified')
        self.assertEqual(report['capabilities']['release_assets']['write'], 'unverified')
        self.assertEqual(report['capabilities']['product_pr'], 'outside this operation')
        self.assertIsNone(self.release)

    def test_existing_release_must_be_fresh_owned_and_bound(self):
        self.fixture.approved()
        first = pub.push_job(self.root, 'pz-current', None)
        original = deepcopy(self.release)
        self.repository.pop('permissions')
        self.immutability = {'enabled': True}
        self.api_calls.clear()
        report = pub.preflight(self.root, 'publish', 'pz-current', first)
        self.assertEqual(report['release_id'], original['id'])
        self.assertNotIn(('immutable-releases', 'GET'), self.api_calls)
        for field, value, error in [('immutable', True, 'immutable'), ('immutable', None, 'mutability'),
                                    ('body', 'foreign', 'Foreign work release'),
                                    ('id', 21, 'generation changed'),
                                    ('target_commitish', first, 'anchor changed')]:
            with self.subTest(field=field, value=value):
                self.release = {**original, field: value}
                if value is None:
                    del self.release[field]
                self.assert_early_rejection(first, error)
        self.release = None
        self.assert_early_rejection(first, 'Bound work release is missing')
        self.release = original
        fixtures.git(self.remote, 'update-ref', 'refs/tags/work-prod-pz-current', first)
        self.assert_early_rejection(first, 'generation changed')

    def test_repository_job_and_generation_disagreement_fail_before_originals(self):
        with self.assertRaisesRegex(ValueError, 'requested repository'):
            pub.preflight(self.root, 'publish', 'pz-current', None, repository='another/repo')
        self.repository['full_name'] = 'another/repo'
        self.assert_early_rejection(None, 'different publisher repository')
        self.repository['full_name'] = pub.REPO
        self.assert_early_rejection(self.main, 'Expected work ref is missing')
        with patch.object(pub, 'api', side_effect=lambda path: {'full_name': pub.REPO} if not path else {}):
            self.assert_early_rejection(None, 'Git and REST main differ')
        with self.assertRaises(ValueError):
            pub.preflight(self.root, 'publish', '../invalid-job', None)

    def test_setting_is_rechecked_before_create_after_early_preflight(self):
        self.fixture.approved()
        real_api = self.api
        calls = 0

        def settings_change(path, method='GET', value=None):
            nonlocal calls
            if path == 'immutable-releases':
                calls += 1
                return {'enabled': calls > 1}
            return real_api(path, method, value)

        with patch.object(pub, 'api', settings_change), self.assertRaisesRegex(ValueError, 'setting enabled'):
            pub.push_job(self.root, 'pz-current', None)
        self.assertEqual(calls, 2)
        self.assertIsNone(self.release)
        self.assertIsNone(guard.remote_head(self.root, 'refs/tags/work-prod-pz-current'))
        self.assertIsNone(guard.remote_head(self.root, 'refs/heads/' + pub.release_catalog.LOCK_BRANCH))

    def test_publication_preserves_only_an_already_bound_legacy_mono_preview(self):
        f = self.fixture
        f.raster_ready()
        definition = json.loads((f.input/'definition.json').read_bytes())
        legacy = current.raster_preview(definition, mode='color')
        f.job['rasters'][0]['preview'] = f.file('legacy.png', legacy)
        with patch.object(current.Checked, 'check_new_previews'):
            f.publish()
        with self.assertRaisesRegex(ValueError, 'New mono raster preview'):
            pub.push_job(self.root, 'pz-current', None)
        self.assertIsNone(self.release)
        with patch.object(current.Checked, 'check_new_previews'):
            first = pub.push_job(self.root, 'pz-current', None)
        _, _, original = self.record(first)
        previous = original['rasters'][0]['preview']
        f.job['rasters'][0]['label'] = '3 × 3 · Monochrom · Aussparungen'
        f.publish()
        second = pub.push_job(self.root, 'pz-current', first)
        source, raw, record = self.record(second)
        self.assertEqual(record['rasters'][0]['preview'], previous)
        self.assertEqual(work_assets.read(previous, 1024), legacy)
        projection = current.projection(record, raw)
        facts = presentation.inspect(source, second, projection)
        raster = next(a for a in projection['assets'] if a['id'] == 'raster-a')
        self.assertEqual(presentation.asset_bytes(source, second, raster['location'],
                                                  mode=facts['raster_modes']['raster-a']),
                         current.raster_preview(definition, mode='mono'))

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
        fixtures.git(root,'mv','game/data/registry.json','content/authoring/output.json')
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
                        raise HTTPError(req.full_url, 403, 'rate limit exceeded',
                                        {'X-RateLimit-Remaining': '0'}, None)
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
        self.enterContext(patch.object(pw.github_rest, 'build_opener', return_value=SimpleNamespace(open=open_api)))

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
                    reject_worker('GitHub-Anfragelimit erreicht')
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
        # A new job must leave room for all three signed app channels.
        with self.assertRaisesRegex(ValueError, 'terminating page'):
            capacity(rows, 1, 'work-prod-new', 1, reserved_apps=len(pub.PRODUCTS))
        capacity(rows[:395], 1, 'work-prod-new', 1, reserved_apps=len(pub.PRODUCTS))
        capacity(rows, 1, 'pw-v1', 7, reserved_apps=0)
        rows.append({'tag_name': 'pw-v1', 'assets': []})
        with self.assertRaisesRegex(ValueError, 'terminating page'):
            capacity(rows, 1, 'pe-v1', 7, reserved_apps=0)
        rows = rows[:100]
        with self.assertRaisesRegex(ValueError, 'metadata budget'):
            capacity(rows, 45, rows[0]['tag_name'], 0, reserved_apps=len(pub.PRODUCTS))
        rows[1]['body'] = 'x' * (4 * 1024**2 - 180000)
        capacity(rows, 1, rows[0]['tag_name'], 1, reserved_apps=0)
        with self.assertRaisesRegex(ValueError, 'metadata page'):
            capacity(rows, 1, rows[0]['tag_name'], 1, reserved_apps=len(pub.PRODUCTS))

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


class PublisherTransportTests(unittest.TestCase):
    def test_auth_context_is_explicit_and_workspace_shielding_remains(self):
        with (patch.dict(os.environ, {'GH_TOKEN': 'one', 'GITHUB_TOKEN': 'two'}, clear=True),
              patch.object(github_rest, '_workspace_token', None)):
            with self.assertRaisesRegex(ValueError, 'Conflicting publisher credentials'):
                pub.select_token('env')
            self.assertEqual(pub.select_token('GITHUB_TOKEN'), 'two')
            github_rest.load_workspace_token()
            self.assertNotIn('GH_TOKEN', os.environ)
            self.assertNotIn('GITHUB_TOKEN', os.environ)
            with pub.publisher_auth('env'):
                self.assertEqual(github_rest.publisher_token(), 'one')
                with self.assertRaisesRegex(ValueError, 'credential changed'):
                    with pub.publisher_auth('env', 'different'):
                        self.fail('Unexpected credential change')
            self.assertIsNone(github_rest.publisher_token())
            with patch.object(pub.subprocess, 'check_output', side_effect=OSError) as gh:
                with self.assertRaisesRegex(ValueError, 'Selected gh login unavailable'):
                    pub.select_token('gh')
                self.assertNotIn('GH_TOKEN', gh.call_args.kwargs['env'])
            with self.assertRaisesRegex(ValueError, 'Missing or invalid publisher credential'):
                with pub.publisher_auth('GH_TOKEN'):
                    self.fail('An absent explicit token fell back to the workspace')

    def test_git_remote_uses_token_only_in_ephemeral_subprocess_config(self):
        token = 'synthetic-git-credential'
        with (guard.use_remote_token(token),
              patch.object(guard, 'check_push_url'),
              patch.object(guard.subprocess, 'check_output', side_effect=[(guard.REMOTE + '\n').encode(), b'']) as run):
            guard.git('.', 'ls-remote', '--refs', '--', guard.REMOTE, 'refs/heads/main')
        (resolve, remote) = run.call_args_list
        self.assertNotIn(token, repr(resolve))
        self.assertNotIn(token, repr(remote.args))
        header = base64.b64encode(('x-access-token:' + token).encode()).decode()
        self.assertNotIn(header, repr(remote.args))
        self.assertIn('Authorization: Basic ' + header, remote.kwargs['env'].values())
        self.assertEqual(remote.kwargs['env']['GIT_TERMINAL_PROMPT'], '0')
        with (guard.use_remote_token(token),
              patch.object(guard, 'check_push_url'),
              patch.object(guard.subprocess, 'check_output', return_value=b'https://another.invalid/repo\n') as run,
              self.assertRaisesRegex(ValueError, 'Git destination differs')):
            guard.remote_head('.', 'refs/heads/main')
        self.assertEqual(run.call_count, 1)
        rewrite = SimpleNamespace(returncode=0, stdout=b'url.https://other.invalid/.pushinsteadof\nhttps://github.com/\0')
        with (guard.use_remote_token(token), patch.object(guard.subprocess, 'run', return_value=rewrite),
              patch.object(guard.subprocess, 'check_output') as network,
              self.assertRaisesRegex(ValueError, 'matching pushInsteadOf')):
            guard.remote_head('.', 'refs/heads/main')
        network.assert_not_called()

    def test_http_errors_and_originals_use_the_selected_token(self):
        token = 'synthetic-rest-credential'
        responses = [HTTPError('unused', 401, '', {}, BytesIO(b'')),
                     HTTPError('unused', 403, '', {}, BytesIO(b'')),
                     HTTPError('unused', 404, '', {}, BytesIO(b'')),
                     HTTPError('unused', 403, '', {'Retry-After': '60'}, BytesIO(b'')),
                     OSError('synthetic-rest-credential must never be printed'), BytesIO(b'original')]
        opener = SimpleNamespace(open=lambda req, **_: respond(req))

        def respond(req):
            self.assertEqual(req.get_header('Authorization'), 'Bearer ' + token)
            result = responses.pop(0)
            if isinstance(result, Exception):
                raise result
            return result

        with (pub.publisher_auth('env', token),
              patch.object(github_rest, 'build_opener', return_value=opener)):
            for wanted in ('auth', 'access', 'access', 'rate_limit', 'network'):
                with self.assertRaises(github_rest.Failure) as error:
                    pub.api('releases/11')
                self.assertEqual(error.exception.kind, wanted)
                self.assertIn('GET releases/11', str(error.exception))
                self.assertNotIn(token, str(error.exception))
            self.assertEqual(work_assets.get('/releases/assets/42', 8, binary=True), b'original')
        self.assertIsNone(github_rest.publisher_token())

    def test_remote_record_binds_the_exact_contents_to_its_git_blob(self):
        job = 'pz-current'
        raw = b'{"synthetic": true}'
        result = {'path': current.path(job), 'size': len(raw), 'type': 'file', 'encoding': 'base64',
                  'content': base64.b64encode(raw).decode(),
                  'sha': sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest()}
        with patch.object(pub, 'api', return_value=result) as api:
            self.assertEqual(pub.remote_record('a' * 40, job), raw)
            api.assert_called_once_with(f'contents/{current.path(job)}?ref=' + 'a' * 40)
            result['sha'] = 'b' * 40
            with self.assertRaisesRegex(ValueError, 'differ from the Git blob'):
                pub.remote_record('a' * 40, job)
