"""Small change-scoped PW-A regressions, real Git/ZIP/HTTP, no solver or catalog."""
from copy import deepcopy
from io import BytesIO
import http.client
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import threading
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
        self.assertEqual(source.read(first, str(Path(self.request['record']['file']).parent / 'reveal.png'), 1024), self.png)
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
        git(self.repo, 'checkout', '-qb', 'content/conflict')
        path = self.directory / 'workspace.json'
        value = p.parse(path.read_bytes()); value['title'] = 'Different bytes'; path.write_bytes(p.data(value)); commit(self.repo)
        configure(self.repo, self.root / 'state')
        listing = Service(Repository(self.root / 'state')).listing()
        self.assertTrue(all(j.get('conflict') for j in listing['jobs']))
        path.unlink(); commit(self.repo)
        listing = Service(Repository(self.root / 'state')).listing()
        self.assertEqual(len(listing['jobs']), 1)

    def test_http_capability_host_origin_paths_and_exact_original(self):
        self.publish(); configure(self.repo, self.root / 'state')
        service = Service(Repository(self.root / 'state'))
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
        if hasattr(os, 'symlink'):
            os.symlink('reveal.png', self.directory / 'link.png')
            sha = commit(self.repo)
            with self.assertRaises(ValueError): GitSource(self.repo).read(sha, str(Path(self.request['record']['file']).parent / 'link.png'))
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
