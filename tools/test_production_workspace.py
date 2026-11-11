"""Small change-scoped PW-A regressions, real Git/ZIP/HTTP, no solver or catalog."""
from copy import deepcopy
from io import BytesIO
import http.client
from pathlib import Path
import stat
import subprocess
import shutil
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
import zipfile

from PIL import Image
from tools.production_workspace import presentation as p
from tools.production_workspace.projector import project
from tools.production_workspace.repository import configure, Repository
from tools.production_workspace.server import Service, Server
from tools.production_workspace.sources import Archive, GitSource, LocalSource, INDEX, git
from tools.puzzle_production import authoring_builder as builder, catalog_io as io
from tools.puzzle_production.contract import InvalidInput


def commit(root):
    git(root, 'add', '.')
    git(root, '-c', 'user.name=PW synthetic', '-c', 'user.email=pw@example.invalid', 'commit', '-qm', 'synthetic')
    return git(root, 'rev-parse', 'HEAD').decode().strip()


def fixture(root, revision='r01'):
    """Today's v3/v2 early-phase forms; synthetic source bytes, no content success."""
    directory = f'content/authoring/pz-workspace-test/{revision}'
    target = root / directory
    target.mkdir(parents=True)
    png = BytesIO(); Image.new('RGBA', (8, 5), (40, 90, 80, 128)).save(png, format='PNG')
    files = {'reveal.png': png.getvalue(), 'rulebook.md': b'**Version 0.7.0 synthetic**\n',
             'brief.txt': b'TEST ONLY\n'}
    files['reveal.provenance.json'] = p.data({'puzzle_id': 'pz-workspace-test', 'file': 'reveal.png',
            'sha256': io.checksum(files['reveal.png']), 'author': 'TEST ONLY', 'usage_basis': 'Synthetic pixels'})
    # Current closed HP-W2 pending manifest, no legacy compatibility fixtures.
    manifest = {'format': 'picross-background-work-v1', 'puzzle_id': 'pz-workspace-test', 'job_id': 'job1',
                'revision': 'bg01', 'created_utc': '2026-11-11T00:00:00Z',
                'context': {'summary': 'Synthetic', 'protected_features': [], 'excluded_subjects': [],
                            'reveal': None, 'reveal_approval': None}, 'briefing': 'Synthetic',
                'candidate_policy': {'count': 3, 'exception': None},
                'presentation': {'status': 'pending', 'evidence': None}, 'candidates': [], 'test_only': True}
    files['background.json'] = p.data(manifest)
    background = {'manifest': {'storage': 'package', 'root': '.', 'ref': {'file': 'background.json',
                   'sha256': io.checksum(files['background.json']), 'bytes': len(files['background.json'])}},
                  'decision': None, 'derivation': None, 'history': None}
    inventory = {'format': 'picross-authoring-file-inventory-v1', 'puzzle_id': 'pz-workspace-test',
                 'revision': revision, 'excludes': ['inventory.json', 'handoff.json'],
                 'files': [{'path': n, 'sha256': io.checksum(b), 'bytes': len(b)} for n, b in files.items()]}
    files['inventory.json'] = p.data(inventory)
    h = {'format': 'picross-authoring-handoff-v3', 'puzzle_id': 'pz-workspace-test', 'revision': revision,
         'repo_commit': 'a' * 40, 'state': 'reveal_review',
         'rulebook': {'version': '0.7.0', 'file': 'rulebook.md', 'sha256': io.checksum(files['rulebook.md'])},
         'inventory': {'file': 'inventory.json', 'sha256': io.checksum(files['inventory.json'])},
         'reveal': None, 'motif': None, 'candidate': None, 'test_only': True, 'brief': 'brief.txt',
         'background': background, 'next_action': 'Synthetic viewing', 'gates': {}}
    files['handoff.json'] = p.data(h)
    archive = BytesIO()
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, raw in files.items():
            z.writestr(name, raw)
    package = archive.getvalue()
    options = [{'ID': 'A', 'Beschreibung': 'Synthetic reveal', 'Datei': 'reveal.png',
                'SHA-256': io.checksum(files['reveal.png'])}]
    record = builder.record_for({'handoff': h, 'external': {}, 'category_id': None,
            'document_revision': 1, 'reveal_options': options}, directory, package,
            files['handoff.json'], None, {'ready': False, 'binding': background, 'blockers': []})
    for name, raw in {'record.json': p.data(record), 'package.zip': package,
                      'handoff.json': files['handoff.json'], 'reveal.png': files['reveal.png']}.items():
        (target / name).write_bytes(raw)
    existing = p.parse((root / INDEX).read_bytes()) if (root / INDEX).exists() else {'format': 'picross-authoring-index-v1', 'entries': []}
    existing['entries'].append({'puzzle_id': h['puzzle_id'], 'revision': revision, 'record': directory + '/record.json'})
    (root / INDEX).write_bytes(p.data(existing))
    request = {'format': p.REQUEST, 'puzzle_id': h['puzzle_id'], 'revision': revision,
               'record': {'commit': None, 'file': directory + '/record.json'}, 'title': 'Synthetisches Motiv',
               'assets': [{'id': 'reveal-A', 'role': 'reveal', 'caption': 'Abschlussbild A',
                           'location': {'commit': None, 'storage': 'package', 'container': directory + '/package.zip', 'file': 'reveal.png'}}],
               'offers': [{'id': 'A', 'kind': 'reveal', 'label': 'Variante A',
                           'record': {'commit': None, 'file': directory + '/record.json'}, 'asset_ids': ['reveal-A']}]}
    return request, files['reveal.png']


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='pw-a-unit-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'repo'; self.repo.mkdir()
        git(self.repo, 'init', '-q', '-b', 'main')
        self.request, self.png = fixture(self.repo)
        self.directory = self.repo / Path(self.request['record']['file']).parent

    def publish(self):
        project(self.request, self.repo)
        return commit(self.repo)

    def test_new_branch_namespace_skips_old_refs_and_reuses_unchanged_scans(self):
        sha = self.publish()
        updates = ''.join(f'create refs/heads/content/old-{n} {sha}\n' for n in range(300))
        subprocess.run(['git', '-C', str(self.repo), 'update-ref', '--stdin'], input=updates.encode(), check=True,
                       stdout=subprocess.DEVNULL)
        git(self.repo, 'branch', 'content/pw/pz-workspace-test')
        git(self.repo, 'branch', 'content/pw/not-a-puzzle')
        configure(self.repo, self.root / 'state')
        repo = Repository(self.root / 'state')
        with patch.object(repo.local, 'resolve', wraps=repo.local.resolve) as resolve, \
                patch.object(repo.local, 'read', wraps=repo.local.read) as read:
            first = repo.listing()
            self.assertEqual({j['ref'] for j in first['jobs']}, {'main', 'content/pw/pz-workspace-test'})
            self.assertEqual(resolve.call_count, 2)
            reads = read.call_count
            second = repo.listing()
            self.assertEqual(len(second['jobs']), 2)
            self.assertEqual(read.call_count, reads, 'unchanged commits must not reread indices/projections')
        with self.assertRaises(ValueError):
            configure(self.repo, self.root / 'bad-state', refs=['main', 'content/*'])

    def test_original_default_configuration_upgrades_only_own_filter(self):
        self.publish()
        configure(self.repo, self.root / 'state')
        path = self.root / 'state/config.json'
        value = p.parse(path.read_bytes()); value['refs'] = ['main', 'content/*']
        path.write_bytes(p.data(value))
        old_cache = self.root / 'state/git-cache'; old_cache.mkdir()
        sentinel = old_cache / 'untouched'; sentinel.write_bytes(b'old cache')
        before = (git(self.repo, 'show-ref'), (self.repo / '.git/index').read_bytes())
        repo = Repository(self.root / 'state')
        self.assertEqual(repo.refs, ['main', 'content/pw/*'])
        self.assertEqual(p.parse(path.read_bytes())['refs'], repo.refs)
        self.assertEqual((git(self.repo, 'show-ref'), (self.repo / '.git/index').read_bytes()), before)
        self.assertEqual(sentinel.read_bytes(), b'old cache')
        value['refs'] = ['main', 'content/special']; path.write_bytes(p.data(value))
        with self.assertRaises(ValueError):
            Repository(self.root / 'state')
        self.assertEqual(p.parse(path.read_bytes())['refs'], value['refs'])

    def test_shallow_remote_fetch_resolves_only_requested_historical_commit(self):
        old = self.publish()
        name = (Path(self.request['record']['file']).parent / 'reveal.png').as_posix()
        (self.repo / name).write_bytes(b'later bytes'); commit(self.repo)
        remote = self.root / 'remote'; remote.mkdir(); git(remote, 'init', '--bare', '-q')
        git(remote, 'config', 'uploadpack.allowFilter', 'true')
        git(self.repo, 'push', str(remote), 'main')
        configure(self.repo, self.root / 'state', remote=str(remote))
        repo = Repository(self.root / 'state'); repo.refresh()
        self.assertTrue((repo.cached.root / 'shallow').is_file())
        with self.assertRaises(ValueError):
            git(repo.cached.root, 'cat-file', '-t', old)
        self.assertEqual(repo.cached.read(old, name), self.png)
        self.assertEqual(git(repo.cached.root, 'cat-file', '-t', old).strip(), b'commit')

    def test_background_refresh_does_not_block_http_or_existing_snapshots(self):
        self.publish(); configure(self.repo, self.root / 'state')
        repo = Repository(self.root / 'state'); service = Service(repo)
        initial = service.listing(); jid = initial['jobs'][0]['id']
        entered, release = threading.Event(), threading.Event()
        original = repo.refresh
        def blocked():
            entered.set()
            if not release.wait(10):
                raise RuntimeError('test release missing')
            return original()
        repo.refresh = blocked
        server = Server(service)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            service.start_refresh(); self.assertTrue(entered.wait(2))
            worker = service.update_thread
            service.start_refresh(); self.assertIs(service.update_thread, worker)
            def get(path):
                c = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=2)
                c.request('GET', path, headers={'X-Workspace-Session': service.secret})
                r = c.getresponse(); value = r.read(); status = r.status; c.close()
                self.assertEqual(status, 200)
                return value
            self.assertIn(b'<!doctype html>', get('/'))
            state = p.parse(get('/api/jobs'))
            self.assertEqual(state['update']['state'], 'running')
            self.assertEqual(state['snapshot'], initial['snapshot'])
            self.assertEqual(get('/api/jobs/' + jid + '/assets/reveal-A'), self.png)
            release.set(); worker.join(10); self.assertFalse(worker.is_alive())
            self.assertEqual(service.status()['update']['state'], 'done')
            self.assertEqual(service.picture(jid, 'reveal-A')[0], self.png)
            with patch.object(repo, 'refresh', side_effect=OSError('must not leak')):
                service.start_refresh(); service.update_thread.join(2)
                state = service.status()
                self.assertEqual(state['update']['state'], 'error')
                self.assertNotIn('must not leak', state['update']['error'])
                self.assertTrue(state['jobs'])
        finally:
            release.set()
            if service.update_thread:
                service.update_thread.join(10)
            server.shutdown(); server.server_close(); thread.join()

    def test_actual_main_opens_browser_before_git_refresh_finishes(self):
        from tools.production_workspace import __main__ as application
        self.publish(); configure(self.repo, self.root / 'state')
        repo = Repository(self.root / 'state')
        entered, release, opened = threading.Event(), threading.Event(), threading.Event()
        original = repo.refresh
        server_holder, urls, result = [], [], []
        def blocked():
            entered.set(); release.wait(10)
            return original()
        def server(service, port):
            value = Server(service, port); server_holder.append(value); return value
        def browser(url):
            urls.append(url); opened.set(); return True
        repo.refresh = blocked
        with patch.object(application, 'Repository', return_value=repo), \
                patch.object(application, 'Server', side_effect=server), \
                patch.object(application.webbrowser, 'open', side_effect=browser):
            runner = threading.Thread(target=lambda: result.append(application.main(['--state', str(self.root / 'state')])))
            runner.start()
            try:
                self.assertTrue(entered.wait(2)); self.assertTrue(opened.wait(2))
                self.assertFalse(release.is_set(), 'browser opened while source is still blocked')
                c = http.client.HTTPConnection('127.0.0.1', server_holder[0].server_port, timeout=2)
                c.request('GET', '/'); response = c.getresponse()
                self.assertEqual(response.status, 200); response.read(); c.close()
            finally:
                release.set()
                if server_holder:
                    server_holder[0].service.update_thread.join(10)
                    server_holder[0].shutdown()
                runner.join(10)
            self.assertFalse(runner.is_alive()); self.assertEqual(result, [0])

    def test_single_file_launcher_bundles_exact_program_and_keeps_checkout_unchanged(self):
        from tools.production_workspace.build_launcher import build, FILES, ROOT
        launcher = (ROOT / 'Picross-Start.cmd').read_text(encoding='utf-8')
        self.assertEqual(launcher, build(), 'regenerate the launcher after changing a bundled source')
        bootstrap = launcher.split('\n# === PICROSS_PYTHON_BEGIN ===\n', 1)[1]
        scope = {'__name__': 'launcher_test'}
        exec(compile(bootstrap, 'Picross-Start.cmd', 'exec'), scope)
        destination = self.root / 'program'; destination.mkdir()
        scope['unpack_program'](destination)
        for name in FILES:
            self.assertEqual((destination / name).read_bytes(), (ROOT / name).read_bytes())
        # An older trusted checkout may lack the new DEFAULT_REFS. The launcher's
        # package overlay must still import this bundled reader, without patching it.
        baseline = self.root / 'baseline'
        package = baseline / 'tools/production_workspace'; package.mkdir(parents=True)
        (baseline / 'tools/__init__.py').write_text('')
        (package / '__init__.py').write_text('')
        (package / 'repository.py').write_text("raise RuntimeError('old reader must not run')\n")
        # The production dependencies are unchanged and stay in the trusted checkout.
        import os
        command = ('import sys; import tools; tools.__path__.append(sys.argv[2]); '
                   'import tools.production_workspace as p; p.__path__[:]=[sys.argv[1]]; '
                   'from tools.production_workspace.repository import DEFAULT_REFS; '
                   "assert DEFAULT_REFS == ['main', 'content/pw/*']")
        result = subprocess.run([__import__('sys').executable, '-c', command, str(destination), str(ROOT.parent)],
                                cwd=baseline, env={**os.environ, 'PYTHONPATH': str(baseline)},
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('old reader must not run', (package / 'repository.py').read_text())
        scope['PROGRAM_SHA256'] = '0' * 64
        with self.assertRaises(RuntimeError):
            scope['unpack_program'](destination)

    def test_projector_only_writes_view_and_reuses_identical_mtimes(self):
        before = {f: (f.read_bytes(), f.stat().st_mtime_ns) for f in self.repo.rglob('*') if f.is_file() and '.git' not in f.parts}
        self.assertEqual(project(self.request, self.repo)['status'], 'published')
        view = self.directory / 'workspace.json'
        stamp = view.stat().st_mtime_ns
        self.assertEqual(project(self.request, self.repo)['status'], 'reused')
        self.assertEqual(view.stat().st_mtime_ns, stamp)
        for f, value in before.items():
            self.assertEqual((f.read_bytes(), f.stat().st_mtime_ns), value)
        self.assertEqual(set(self.directory.glob('.pw-*')), set())

    def test_closed_request_and_invalid_roles_are_rejected(self):
        for mutate in (lambda r: r.update(approved=True),
                       lambda r: r['assets'][0].update(role='raster'),
                       lambda r: r['offers'][0].update(id='foreign'),
                       lambda r: r['offers'][0].update(kind='raster'),
                       lambda r: r['assets'][0]['location'].update(file='../escape.png')):
            value = deepcopy(self.request); mutate(value)
            with self.assertRaises(ValueError):
                project(value, self.repo)
            self.assertFalse((self.directory / 'workspace.json').exists())

    def test_source_race_and_occupied_output_preserve_existing_bytes(self):
        original = LocalSource.recheck
        original_handoff = (self.directory / 'handoff.json').read_bytes()
        def changed(source):
            path = self.directory / 'handoff.json'
            path.write_bytes(path.read_bytes() + b' ')
            original(source)
        with patch.object(LocalSource, 'recheck', changed), self.assertRaises(ValueError):
            project(self.request, self.repo)
        self.assertFalse((self.directory / 'workspace.json').exists())
        # Restore the actual original before exercising an unrelated occupied output.
        (self.directory / 'handoff.json').write_bytes(original_handoff)
        (self.directory / 'workspace.json').write_bytes(b'foreign')
        with self.assertRaises(ValueError):
            project(self.request, self.repo)
        self.assertEqual((self.directory / 'workspace.json').read_bytes(), b'foreign')

    def test_committed_snapshot_ignores_dirty_worktree_and_finds_new_revision(self):
        first = self.publish()
        (self.directory / 'reveal.png').write_bytes(b'dirty')
        status = git(self.repo, 'status', '--porcelain')
        source = GitSource(self.repo)
        self.assertEqual(source.read(first, (Path(self.request['record']['file']).parent / 'reveal.png').as_posix(), 1024), self.png)
        configure(self.repo, self.root / 'state')
        repo = Repository(self.root / 'state')
        service = Service(repo)
        a = service.listing(); jid = a['jobs'][0]['id']
        self.assertEqual(service.picture(jid, 'reveal-A')[0], self.png)
        self.assertEqual(git(self.repo, 'status', '--porcelain'), status)
        req, _ = fixture(self.repo, 'r02'); project(req, self.repo)
        second = commit(self.repo)
        b = service.listing(refresh=True)
        self.assertEqual(len(b['jobs']), 2)
        self.assertEqual(service.job(jid)['commit'], first)
        self.assertEqual(service.picture(jid, 'reveal-A')[0], self.png)
        self.assertNotEqual(second, first)
        self.assertGreaterEqual(service.metrics['image_cache_hits'], 1)

    def test_remote_cache_offline_and_user_refs_index_sentinels(self):
        self.publish()
        git(self.repo, 'branch', 'other')
        (self.repo / 'sentinel.txt').write_text('dirty')
        before = (git(self.repo, 'show-ref'), git(self.repo, 'status', '--porcelain'), (self.repo / '.git/index').read_bytes())
        remote = self.root / 'remote'; remote.mkdir(); git(remote, 'init', '--bare', '-q')
        git(remote, 'config', 'uploadpack.allowFilter', 'true')
        git(self.repo, 'push', str(remote), 'main')
        configure(self.repo, self.root / 'state', remote=str(remote), refs=['main'])
        repo = Repository(self.root / 'state'); listing = repo.refresh()
        self.assertIsNone(listing['sync_error'])
        self.assertTrue(any(j['source'] == 'remote' for j in listing['jobs']))
        remote.rename(self.root / 'offline')
        listing = repo.refresh()
        self.assertIsNotNone(listing['sync_error'])
        self.assertTrue(listing['synced_at'])
        self.assertTrue(any(j['source'] == 'remote' for j in listing['jobs']))
        self.assertEqual((git(self.repo, 'show-ref'), git(self.repo, 'status', '--porcelain'), (self.repo / '.git/index').read_bytes()), before)

    def test_conflicting_revision_and_missing_projection_are_not_guessed(self):
        self.publish()
        git(self.repo, 'checkout', '-qb', 'content/pw/pz-workspace-test')
        path = self.directory / 'workspace.json'
        value = p.parse(path.read_bytes()); value['title'] = 'Different bytes'; path.write_bytes(p.data(value)); commit(self.repo)
        configure(self.repo, self.root / 'state')
        listing = Service(Repository(self.root / 'state')).listing()
        self.assertTrue(all(j.get('conflict') for j in listing['jobs']))
        path.unlink(); commit(self.repo)
        listing = Service(Repository(self.root / 'state')).listing()
        self.assertEqual(len(listing['jobs']), 1)

    def test_bad_projection_read_is_isolated_to_its_index_entry(self):
        self.publish()
        request, _ = fixture(self.repo, 'r02'); project(request, self.repo)
        commit(self.repo)
        configure(self.repo, self.root / 'state')
        view = self.directory / 'workspace.json'
        for broken in ('oversized', 'symlink', 'invalid_json'):
            with self.subTest(broken=broken):
                git(self.repo, 'update-index', '--force-remove', view.relative_to(self.repo).as_posix())
                view.write_bytes(b' ' * (1024 * 1024 + 1) if broken == 'oversized' else b'not JSON')
                commit(self.repo)
                if broken == 'symlink':
                    # Publish a real Git symlink without requiring Windows symlink privileges.
                    oid = git(self.repo, 'rev-parse', 'HEAD:' + view.relative_to(self.repo).as_posix()).decode().strip()
                    git(self.repo, 'update-index', '--cacheinfo', '120000', oid, view.relative_to(self.repo).as_posix())
                    git(self.repo, '-c', 'user.name=PW synthetic', '-c', 'user.email=pw@example.invalid',
                        'commit', '-qm', 'synthetic symlink')
                service = Service(Repository(self.root / 'state'))
                listing = service.listing()
                self.assertEqual([j['revision'] for j in listing['jobs']], ['r02'])
                self.assertEqual(len(listing['errors']), 1)
                self.assertIn('pz-workspace-test/r01', listing['errors'][0])
                job = listing['jobs'][0]
                self.assertEqual(service.detail(job['id'])['revision'], 'r02')
                self.assertEqual(service.picture(job['id'], 'reveal-A')[0], self.png)

    def test_deleted_remote_ref_is_pruned_without_touching_foreign_refs_or_snapshots(self):
        # The only published job is on content/pw/pz-workspace-test, not main.
        (self.repo / INDEX).write_bytes(p.data({'format': 'picross-authoring-index-v1', 'entries': []}))
        commit(self.repo)
        git(self.repo, 'checkout', '-qb', 'content/pw/pz-workspace-test')
        (self.repo / INDEX).write_bytes(p.data({'format': 'picross-authoring-index-v1', 'entries': [
            {'puzzle_id': self.request['puzzle_id'], 'revision': 'r01', 'record': self.request['record']['file']}]}))
        published = self.publish()
        remote = self.root / 'remote'; remote.mkdir(); git(remote, 'init', '--bare', '-q')
        git(remote, 'config', 'uploadpack.allowFilter', 'true')
        git(self.repo, 'push', str(remote), 'main', 'content/pw/pz-workspace-test')
        git(self.repo, 'checkout', 'main'); git(self.repo, 'branch', '-D', 'content/pw/pz-workspace-test')
        (self.repo / 'sentinel.txt').write_text('dirty')
        before = (git(self.repo, 'show-ref'), git(self.repo, 'status', '--porcelain'), (self.repo / '.git/index').read_bytes())
        configure(self.repo, self.root / 'state', remote=str(remote))
        repo = Repository(self.root / 'state'); service = Service(repo)
        first = service.listing(refresh=True)
        jid = next(j['id'] for j in first['jobs'] if j['source'] == 'remote')
        self.assertEqual(service.picture(jid, 'reveal-A')[0], self.png)
        # Same namespace, but outside the configured refspecs, as well as a foreign namespace.
        for ref in ('refs/pw/other', 'refs/foreign/keep'):
            git(repo.cached.root, 'update-ref', ref, published)
        git(self.repo, 'push', str(remote), '--delete', 'content/pw/pz-workspace-test')
        second = service.listing(refresh=True)
        self.assertIsNone(second['sync_error'])
        self.assertEqual(second['jobs'], [])
        self.assertNotIn('content/pw/pz-workspace-test', [s['ref'] for s in second['sources']])
        for ref in ('refs/pw/other', 'refs/foreign/keep'):
            self.assertEqual(repo.cached.resolve(ref), published)
        self.assertEqual(service.picture(jid, 'reveal-A')[0], self.png)
        # Republish, cache, then make the remote unavailable: failure must retain its refs.
        git(self.repo, 'push', str(remote), published + ':refs/heads/content/pw/pz-workspace-test')
        service.listing(refresh=True)
        cached_refs = git(repo.cached.root, 'show-ref')
        remote.rename(self.root / 'offline')
        offline = service.listing(refresh=True)
        self.assertIsNotNone(offline['sync_error'])
        self.assertTrue(any(j['source'] == 'remote' for j in offline['jobs']))
        self.assertEqual(git(repo.cached.root, 'show-ref'), cached_refs)
        self.assertEqual((git(self.repo, 'show-ref'), git(self.repo, 'status', '--porcelain'),
                          (self.repo / '.git/index').read_bytes()), before)

    def ui_service(self):
        for request in (self.request, fixture(self.repo, 'r02')[0]):
            asset = request['assets'][0]
            request['assets'] = [{**deepcopy(asset), 'id': 'image-' + str(n)} for n in range(6)]
            request['offers'][0]['asset_ids'] = ['image-0']
            project(request, self.repo)
        commit(self.repo); configure(self.repo, self.root / 'state')
        service = Service(Repository(self.root / 'state'))
        service.listing()
        return service

    def test_ui_queues_six_slow_originals_retries_and_ignores_old_responses(self):
        service = self.ui_service()
        picture = service.picture
        def slow(jid, aid):
            time.sleep(.25)
            return picture(jid, aid)
        service.picture = slow
        server = Server(service); thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        self.addCleanup(lambda: (server.shutdown(), server.server_close(), thread.join()))
        node = shutil.which('node')
        self.assertIsNotNone(node, 'Node.js is required for the small UI loading regression (no browser).')
        check = Path(__file__).parent / 'production_workspace/check_ui_loading.cjs'
        result = subprocess.run([node, str(check), server.origin, service.secret, io.checksum(self.png)],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_real_transport_aborts_preserve_metadata_and_images_recover_automatically(self):
        service = self.ui_service()
        picture = service.picture
        counts = {'active': 0, 'peak': 0, 'completed': 0}
        condition = threading.Condition()
        def slow(jid, aid):
            with condition:
                counts['active'] += 1
                counts['peak'] = max(counts['peak'], counts['active'])
            try:
                time.sleep(5)
                return picture(jid, aid)
            finally:
                with condition:
                    counts['active'] -= 1
                    counts['completed'] += 1
                    condition.notify_all()
        service.picture = slow
        server = Server(service); thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            node = shutil.which('node')
            self.assertIsNotNone(node, 'Node.js is required for the real transport abort regression (no browser).')
            check = Path(__file__).parent / 'production_workspace/check_ui_loading.cjs'
            result = subprocess.run([node, str(check), server.origin, service.secret, io.checksum(self.png), 'abort'],
                                    capture_output=True, text=True, timeout=45)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            print(result.stdout.strip())
        finally:
            # Aborted transports leave real readers alive: wait before deleting fixtures.
            with condition:
                finished = condition.wait_for(lambda: counts['active'] == 0, timeout=10)
            server.shutdown(); server.server_close(); thread.join()
            self.assertTrue(finished, 'real image readers must finish before fixture cleanup')
        self.assertEqual(counts['peak'], 2)
        self.assertGreaterEqual(counts['completed'], 8)  # Two aborted originals plus six final cards.
        print('server_image_work: ' + p.data(counts).decode().strip())

    def test_http_capability_host_origin_paths_and_exact_original(self):
        self.publish(); configure(self.repo, self.root / 'state')
        service = Service(Repository(self.root / 'state'))
        service.listing()
        server = Server(service); thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        self.addCleanup(lambda: (server.shutdown(), server.server_close(), thread.join()))
        def call(path, headers=None, method='GET'):
            c = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=10)
            c.request(method, path, headers=headers or {})
            r = c.getresponse(); raw = r.read(); code = r.status; c.close()
            return code, raw
        auth = {'X-Workspace-Session': service.secret}
        self.assertEqual(call('/api/jobs')[0], 400)
        for headers in ({**auth, 'Origin': 'http://foreign.invalid'}, {**auth, 'Host': 'attacker.invalid'},
                        {**auth, 'Sec-Fetch-Site': 'cross-site'}):
            self.assertEqual(call('/api/jobs', headers)[0], 400)
        self.assertEqual(call('/api/jobs?file=secret', auth)[0], 400)
        self.assertEqual(call('/api/refresh', auth)[0], 400)
        code, raw = call('/api/jobs', auth); self.assertEqual(code, 200)
        job = p.parse(raw)['jobs'][0]
        code, raw = call('/api/jobs/' + job['id'] + '/assets/reveal-A', auth)
        self.assertEqual((code, raw), (200, self.png))
        self.assertEqual(call('/api/jobs/' + job['id'] + '/assets/../../secret', auth)[0], 400)
        self.assertEqual(call('/api/refresh', auth, method='POST')[0], 200)
        service.update_thread.join(10)
        self.assertFalse(service.update_thread.is_alive())

    def test_zip_guards_cover_aliases_links_sizes_and_actual_crc(self):
        for entries in ([('../escape', b'x')], [('C:/escape', b'x')], [('a.png', b'x'), ('A.png', b'x')],
                        [('dir/a', b'x'), ('Dir/b', b'x')], [('a', b'x'), ('a/b', b'x')]):
            raw = BytesIO()
            with zipfile.ZipFile(raw, 'w') as z:
                for n, b in entries: z.writestr(n, b)
            with self.assertRaises(ValueError): Archive(raw.getvalue())
        raw = BytesIO()
        with zipfile.ZipFile(raw, 'w') as z:
            info = zipfile.ZipInfo('link'); info.external_attr = (stat.S_IFLNK | 0o777) << 16; z.writestr(info, b'outside')
        with self.assertRaises(ValueError): Archive(raw.getvalue())
        raw = BytesIO()
        with zipfile.ZipFile(raw, 'w') as z:
            z.writestr('handoff.json', b'bounded')
        oversized = bytearray(raw.getvalue())
        import struct
        struct.pack_into('<I', oversized, oversized.index(b'PK\x01\x02') + 24, 64 * 1024 * 1024 + 1)
        with self.assertRaises(ValueError): Archive(bytes(oversized))
        raw = BytesIO()
        with zipfile.ZipFile(raw, 'w', compression=zipfile.ZIP_STORED) as z:
            z.writestr('handoff.json', b'known literal bytes')
        broken = raw.getvalue().replace(b'known literal bytes', b'wrong literal bytes', 1)
        z = Archive(broken)
        try:
            with self.assertRaises(ValueError): z.read('handoff.json')
        finally: z.close()

    def test_image_decode_rejects_active_and_corrupt_resources(self):
        self.assertEqual(p.image(self.png)['width'], 8)
        for raw in (b'<svg onload="alert(1)"/>', b'<html>hi</html>', self.png[:30]):
            with self.assertRaises(ValueError): p.image(raw)

    def test_git_symlink_and_missing_historical_object_fail(self):
        self.publish()
        name = (Path(self.request['record']['file']).parent / 'link.png').as_posix()
        # Git object mode is the reader's boundary; no host symlink privilege needed.
        oid = git(self.repo, 'rev-parse', 'HEAD:' + self.request['record']['file']).decode().strip()
        git(self.repo, 'update-index', '--add', '--cacheinfo', '120000', oid, name)
        git(self.repo, '-c', 'user.name=PW synthetic', '-c', 'user.email=pw@example.invalid',
            'commit', '-qm', 'synthetic symlink')
        sha = git(self.repo, 'rev-parse', 'HEAD').decode().strip()
        with self.assertRaises(ValueError): GitSource(self.repo).read(sha, name)
        with self.assertRaises(ValueError): GitSource(self.repo).read('f' * 40, self.request['record']['file'])

    def test_measured_hash_mutation_and_noncanonical_record_fail(self):
        self.publish()
        value = p.parse((self.directory / 'workspace.json').read_bytes())
        value['assets'][0]['location']['sha256'] = '0' * 64
        with self.assertRaises(ValueError): p.inspect(LocalSource(self.repo), None, value)
        value = deepcopy(self.request); value['record']['file'] = 'content/authoring/record.json'
        with self.assertRaises(ValueError): project(value, self.repo)

    def test_setup_rejects_project_cache_and_remote_helpers(self):
        for state, remote in ((self.repo / 'cache', None), (self.root / 'state', 'ext::run something'),
                              (self.root / 'state', 'https://name:secret@example.invalid/repo')):
            with self.assertRaises(ValueError): configure(self.repo, state, remote=remote)

    def test_discarded_background_history_uses_exact_manifest_and_original(self):
        # Resolve the historical transport boundary in isolation; constructor,
        # projector and HTTP admission are covered above with complete records.
        from tests.puzzle_production.background_fixtures import BackgroundFixture, PROFILE
        bg = BackgroundFixture(self.root / 'background', {'profile': PROFILE, 'tool_sha256': 'a' * 64})
        target = self.repo / 'content/authoring/history'
        import shutil
        shutil.copytree(bg.source, target)
        history_commit = commit(self.repo)
        source = GitSource(self.repo)
        ctx = object.__new__(p.Record)
        ctx.source, ctx.snapshot, ctx.commit = source, history_commit, history_commit
        ctx.allowed, ctx.offer_keys, ctx.historical_assets = {'background': {}}, {}, []
        ctx.directory = 'content/authoring/pz-workspace-test/r02'
        binding = {'manifest': {'storage': 'package', 'root': 'background', 'ref': bg.request['manifest']},
                   'decision': None, 'derivation': None,
                   'history': {'commit': history_commit, 'storage': 'directory',
                               'path': 'content/authoring/history', 'root': '.'}}
        c = bg.manifest['candidates'][1]
        name = 'background/' + c['original']['file']
        ctx.historical_background(binding, bg.manifest, c, name)
        loc = ctx.historical_assets[0][1]
        self.assertEqual(p.asset_bytes(source, history_commit, loc), (bg.source / c['original']['file']).read_bytes())
        self.assertEqual(ctx.asset_name({'role': 'background', 'location': loc}), name)
        changed = deepcopy(bg.manifest); changed['briefing'] += ' changed'
        with self.assertRaises(ValueError): ctx.historical_background(binding, changed, c, name)
        wrong = deepcopy(c); wrong['original']['sha256'] = '0' * 64
        with self.assertRaises(ValueError): ctx.historical_background(binding, bg.manifest, wrong, name)
        # The selected active candidate is never allowed to come from history.
        ctx.directory = 'content/authoring/history'
        binding['decision'] = {'storage': 'external', 'root': '.', 'ref': bg.request['decision']}
        with self.assertRaises(ValueError):
            ctx.historical_background(binding, bg.manifest, bg.manifest['candidates'][0],
                                      'background/' + bg.manifest['candidates'][0]['original']['file'])
