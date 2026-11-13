"""APP-B2-T01: synthetic signed channel, bounded transport and cancellation."""
import copy
from io import BytesIO
import os
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import Mock, patch
import urllib.error
import urllib.request

from tools import test_production_installer as fixtures
from tools.production_workspace import app_updates, update_client as client, update_verifier as verifier
from tools.production_workspace import update_diagnostic, update_windows as windows
from tools.production_workspace.update_storage import Preferences, Stage, recover, atomic_json, no_links
from tools.production_workspace.payload import canonical
from tools.production_workspace.release_manifest import strict_json


class MemoryTransport:
    def __init__(self, raw, signature, files):
        manifest = strict_json(raw)
        self.files = {**files, 'manifest.json': raw, 'manifest.sig.json': signature}
        self.calls = []
        self.row = {'id': 9, 'tag_name': manifest['tag'], 'draft': False, 'prerelease': False,
            'published_at': '2026-11-13T12:00:00Z', 'url': client.API + '/9',
            'html_url': 'https://github.com/venomenon328/picross/releases/tag/' + manifest['tag'],
            'assets': [{'id': i, 'name': name, 'size': len(raw), 'state': 'uploaded',
                        'url': 'https://api.github.com/repos/venomenon328/picross/releases/assets/' + str(i),
                        'browser_download_url': client.DOWNLOAD + manifest['tag'] + '/' + name}
                       for i, (name, raw) in enumerate(self.files.items(), 1)]}
        self.rows = [self.row]

    def read(self, url, limit, cancel, deadline):
        self.calls.append(url)
        client.checkpoint(cancel, deadline)
        return canonical(self.rows) if url.startswith(client.API + '?') else self.files[url.rsplit('/', 1)[1]]

    def transfer(self, url, output, limit, cancel, deadline, *, expected=None):
        output.write(self.read(url, limit, cancel, deadline))


class ChannelTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='app-b2-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.api = fixtures.MemoryGitHub()
        self.trust, secret = update_diagnostic.test_identity()
        self.planned, self.provenance = fixtures.AppReleaseTests.candidate(self)
        self.files = {name: (self.root / name).read_bytes() for name in self.provenance['assets']}
        self.raw, self.signature = verifier._sign(self.provenance, self.files, secret, self.trust)
        self.transport = MemoryTransport(self.raw, self.signature, self.files)
        self.cancel = threading.Event()

    def discover(self, version='0.1.0'):
        return client._discover(version, self.cancel, self.transport,
            lambda raw, sig: verifier._verify_metadata(raw, sig, self.trust))

    def test_metadata_first_then_full_bound_download(self):
        metadata, assets = self.discover()
        self.assertIs(type(metadata), verifier.VerifiedMetadata)
        self.assertEqual(len(self.transport.calls), 3)
        self.assertFalse(any(url.endswith('.msi') for url in self.transport.calls))
        stage = Stage(self.root / '.launcher')
        try:
            candidate = client._download(metadata, assets, stage, self.cancel, self.transport,
                lambda raw, sig, files: verifier._verify(raw, sig, files, self.trust))
            self.assertIs(type(candidate), verifier.VerifiedCandidate)
            self.assertEqual(candidate.binding, metadata.binding)
            self.assertEqual(len(list(stage.path.iterdir())), 7)
        finally:
            stage.cleanup()

    def test_empty_production_root_and_v1_never_authorize(self):
        with self.assertRaises(ValueError):
            verifier.verify_metadata(self.raw, self.signature)
        self.transport.files['manifest.json'] = canonical(self.provenance)
        with self.assertRaises(ValueError):
            self.discover()
        self.assertFalse(any(url.endswith('.msi') for url in self.transport.calls))

    def test_highest_broken_release_has_no_older_fallback(self):
        broken = copy.deepcopy(self.transport.row)
        broken.update(id=10, tag_name='pw-v0.1.2', assets=[])
        self.transport.rows.append(broken)
        with self.assertRaises(ValueError):
            self.discover()
        self.assertEqual(len(self.transport.calls), 1)

    def test_foreign_product_release_ignored_but_catalog_exhaustion_fails(self):
        self.transport.rows.insert(0, {'tag_name': 'game-v9', 'draft': False, 'prerelease': False})
        self.discover()
        self.transport.rows = [{'tag_name': 'game-v9', 'draft': False, 'prerelease': False}] * 100
        with self.assertRaisesRegex(ValueError, 'limit'):
            self.discover()

    def test_replay_same_version_without_binding_and_downgrade_reject(self):
        for version in ('0.1.1', '0.1.2'):
            with self.subTest(version=version), self.assertRaises(ValueError):
                self.discover(version)
        self.assertFalse(any(url.endswith('.msi') for url in self.transport.calls))

    def test_release_identity_paths_asset_sizes_and_duplicates(self):
        original = copy.deepcopy(self.transport.row)
        mutations = [lambda r: r.update(url=client.API + '/10'),
                     lambda r: r.update(html_url='https://github.com/foreign/repo/releases/tag/pw-v0.1.1'),
                     lambda r: r['assets'][0].update(browser_download_url='https://evil.invalid/file'),
                     lambda r: r['assets'][0].update(size=True),
                     lambda r: r['assets'][0].update(size=999999),
                     lambda r: r['assets'].append(r['assets'][0]),
                     lambda r: r['assets'][0].update(name='../outside'),
                     lambda r: r['assets'][0].update(state='new'),
                     lambda r: r.update(tag_name='pw-v0.1.01')]
        for mutation in mutations:
            row = copy.deepcopy(original); mutation(row); self.transport.rows = [row]
            with self.subTest(row=row.get('tag_name')), self.assertRaises(ValueError):
                self.discover()

    def test_signature_and_asset_corruption_never_handoff(self):
        self.transport.files['manifest.sig.json'] = self.signature.replace(b'Ed25519', b'Ed25518')
        with self.assertRaises(ValueError):
            self.discover()
        self.transport.files['manifest.sig.json'] = self.signature
        metadata, assets = self.discover()
        msi = next(n for n in self.files if n.endswith('.msi'))
        self.transport.files[msi] += b'bad'
        stage = Stage(self.root / '.launcher')
        try:
            with self.assertRaises(ValueError):
                client._download(metadata, assets, stage, self.cancel, self.transport, Mock())
        finally:
            stage.cleanup()

    def test_cancel_and_disk_full_leave_existing_state_unchanged(self):
        sentinel = self.root / 'config.json'; sentinel.write_bytes(b'user state')
        metadata, assets = self.discover()
        stage = Stage(self.root / '.launcher')
        try:
            self.cancel.set()
            with self.assertRaises(client.Cancelled):
                client._download(metadata, assets, stage, self.cancel, self.transport, Mock())
            self.assertEqual(sentinel.read_bytes(), b'user state')
        finally:
            stage.cleanup()
        self.cancel.clear()
        stage = Stage(self.root / '.launcher')
        try:
            with patch.object(stage, 'write', side_effect=OSError('disk full')), self.assertRaises(OSError):
                client._download(metadata, assets, stage, self.cancel, self.transport, Mock())
        finally:
            stage.cleanup()


class TransportTests(unittest.TestCase):
    class Response(BytesIO):
        status = 200
        def __init__(self, raw, headers=None, final=None):
            super().__init__(raw); self.headers = headers or {}; self.final = final or client.API + '?per_page=100&page=1'
        def geturl(self):
            return self.final

    def transfer(self, response, limit=20, expected=None):
        transport = client.Transport(); transport.opener = Mock()
        transport.opener.open.return_value = response
        output = BytesIO()
        transport.transfer(client.API + '?per_page=100&page=1', output, limit, threading.Event(), time.monotonic()+10, expected=expected)
        request = transport.opener.open.call_args.args[0]
        self.assertFalse(request.has_header('Authorization'))
        return output.getvalue()

    def test_bounded_length_encoding_and_stream(self):
        self.assertEqual(self.transfer(self.Response(b'abc', {'Content-Length': '3'}), expected=3), b'abc')
        for raw, headers, expected in [(b'abc', {'Content-Length':'4'},None), (b'abc',{},2),
                                      (b'x'*21,{},None), (b'a',{'Content-Encoding':'gzip'},None),
                                      (b'a',{'Content-Length':'-1'},None)]:
            with self.subTest(headers=headers), self.assertRaises(ValueError):
                self.transfer(self.Response(raw, headers), expected=expected)

    def test_redirects_are_exact_https_release_assets_only(self):
        handler = client.Redirects()
        request = urllib.request.Request(client.DOWNLOAD + 'pw-v0.1.1/manifest.json')
        good = 'https://release-assets.githubusercontent.com/github-production-release-asset/123/abc-def?signature=transport'
        self.assertEqual(handler.redirect_request(request, None, 302, '', {}, good).full_url, good)
        for url in ('http://release-assets.githubusercontent.com/github-production-release-asset/1/abc',
                    'https://release-assets.githubusercontent.com.evil.invalid/a', 'https://github.com/foreign/repo',
                    'https://token@release-assets.githubusercontent.com/github-production-release-asset/1/a',
                    'https://release-assets.githubusercontent.com/github-production-release-asset/1/../a',
                    'https://release-assets.githubusercontent.com:99/github-production-release-asset/1/a'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                handler.redirect_request(request, None, 302, '', {}, url)
        with self.assertRaises(ValueError):
            handler.redirect_request(urllib.request.Request(client.API+'?page=1'),None,302,'',{},good)

    def test_offline_404_429_tls_timeout_are_errors_not_current(self):
        for error in (OSError('offline'), TimeoutError(), urllib.error.URLError('TLS'),
                      urllib.error.HTTPError(client.API,404,'missing',{},None),
                      urllib.error.HTTPError(client.API,429,'rate limit',{},None)):
            transport = client.Transport(); transport.opener = Mock(); transport.opener.open.side_effect = error
            with self.subTest(error=type(error)), self.assertRaises(Exception):
                transport.read(client.API+'?page=1',100,threading.Event(),time.monotonic()+1)


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='app-b2-state-'); self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def test_preference_is_explicit_atomic_separate_and_invalid_closed(self):
        config = self.root / 'config.json'; config.write_bytes(b'preserve')
        preferences = Preferences(self.root / '.launcher')
        self.assertIsNone(preferences.read())
        preferences.write(False); self.assertIs(preferences.read(), False)
        preferences.write(True); self.assertIs(preferences.read(), True)
        for value in ({'format':'picross-app-update-preference-v1','enabled':1},
                      {'format':'unknown','enabled':True},
                      {'format':'picross-app-update-preference-v1','enabled':True,'url':'foreign'}):
            preferences.path.write_bytes(canonical(value))
            with self.assertRaises(ValueError): preferences.read()
        self.assertEqual(config.read_bytes(), b'preserve')

    def test_stage_cleanup_preserves_unknown_file(self):
        stage=Stage(self.root / '.launcher'); stage.write('own.txt',b'own')
        (stage.path/'foreign.txt').write_bytes(b'foreign')
        with self.assertRaises(OSError): stage.cleanup()
        self.assertEqual((stage.path/'foreign.txt').read_bytes(),b'foreign')
        for name in ('../outside','x:y','a\\b','a/'):
            with self.assertRaises(ValueError): stage.target(name)

    def test_reparse_directory_is_refused_before_writes(self):
        target=self.root/'target'; target.mkdir()
        link=self.root/'link'
        if os.name=='nt':
            import subprocess
            subprocess.run(['cmd','/c','mklink','/J',str(link),str(target)],check=True,capture_output=True)
        else:
            link.symlink_to(target,target_is_directory=True)
        try:
            with self.assertRaises(ValueError): Preferences(link/'.launcher')
            self.assertFalse((target/'.launcher').exists())
        finally:
            if os.name=='nt': link.rmdir()
            else: link.unlink()

    def test_recovery_only_completed_owned_files_and_no_install(self):
        launcher=self.root/'.launcher'; stage=Stage(launcher)
        from tools.production_workspace.release import release
        msi=release(version='0.1.1')['filename']
        for name in (msi,msi+'.sha256','START.txt','delivery.json','inputs.json','manifest.json','manifest.sig.json','UpdateHelper.exe','active'):
            stage.write(name,b'owned')
        nonce=stage.path.name
        atomic_json(launcher/'update-pending.json', {'format':'picross-update-pending-v1','nonce':nonce,'stage':nonce,'version':'0.1.1','files':sorted(stage.names)})
        self.assertIn('unbestätigt',recover(launcher)); self.assertTrue(stage.path.exists())
        atomic_json(launcher/'update-result.json',{'format':'picross-update-result-v1','nonce':nonce,'status':'failed','version':'0.1.1'})
        self.assertIn('fehlgeschlagen',recover(launcher)); self.assertFalse(stage.path.exists())

    def controller(self, enabled=True):
        runtime=Mock(); runtime.lock.state=self.root; runtime.lock.directory=self.root/'.launcher'; runtime.stop_requested=threading.Event()
        Preferences(runtime.lock.directory).write(enabled)
        with (patch.object(windows,'installation',return_value=Mock(version='0.1.0',executable=self.root/'program'/'Picross-Start.exe')),
              patch.object(app_updates,'production_trust',return_value={'accepted':{'test':'test'}})):
            return app_updates.Updates(runtime)

    def test_no_optin_no_download_and_once_per_instance(self):
        updates=self.controller(False)
        with patch.object(client,'discover',side_effect=OSError('offline')) as discover:
            updates.start(); self.assertIsNone(updates.thread)
            updates.choose(True); updates.thread.join(2); updates.start()
            self.assertEqual(discover.call_count,1)
            self.assertIn('nicht möglich',updates.status)
            self.assertFalse(updates.runtime.request_stop.called)

    def test_optout_cancels_inflight_without_later_helper(self):
        updates=self.controller(); entered=threading.Event(); release=threading.Event()
        def discover(*_): entered.set(); release.wait(3); return Mock(),{}
        with patch.object(client,'discover',side_effect=discover), patch.object(windows,'prepare') as prepare:
            updates.start(); self.assertTrue(entered.wait(1)); updates.choose(False); release.set(); updates.close()
            prepare.assert_not_called(); self.assertIsNone(updates.take())
            self.assertFalse(updates.runtime.request_stop.called)

    def test_helper_commit_is_explicit_and_abort_is_eof(self):
        process=Mock(); process.poll.return_value=None; process.stdin=BytesIO()
        handoff=windows.Handoff(process,'a'*48); handoff.abort()
        self.assertTrue(process.stdin.closed); self.assertFalse(handoff.committed)
        process.stdin=Mock(); handoff=windows.Handoff(process,'a'*48)
        runtime=Mock(); runtime.stop_requested=threading.Event(); runtime.stopped=threading.Event(); runtime.error=None
        with self.assertRaises(ValueError): handoff.commit(runtime)
        process.stdin.write.assert_not_called()
        runtime.stop_requested.set(); runtime.stopped.set(); handoff.commit(runtime)
        process.stdin.write.assert_called_once_with(('GO '+'a'*48+'\n').encode())
        self.assertTrue(handoff.committed)

    def test_developer_portable_never_installed(self):
        with self.assertRaises(ValueError): windows.installation()


if __name__ == '__main__':
    unittest.main()
