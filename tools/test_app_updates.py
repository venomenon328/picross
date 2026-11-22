"""APP-B2-T01: synthetic signed channel, bounded transport and cancellation."""
import copy
from dataclasses import replace
from types import SimpleNamespace
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
from tools.production_workspace.desktop import Startup


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

    def transfer(self, url, output, limit, cancel, deadline, *, expected=None, received=None):
        raw = self.read(url, limit, cancel, deadline)
        if received is None:
            output.write(raw)
        else:
            for offset in range(0, len(raw), 64):
                client.checkpoint(cancel, deadline)
                size = output.write(raw[offset:offset + 64])
                received(size)
            client.checkpoint(cancel, deadline)


class ChannelTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='app-b2-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.api = fixtures.MemoryGitHub()
        self.trust, self.secret = update_diagnostic.test_identity()
        self.planned, self.provenance = fixtures.AppReleaseTests.candidate(self)
        self.files = {name: (self.root / name).read_bytes() for name in self.provenance['assets']}
        self.raw, self.signature = verifier._sign(self.provenance, self.files, self.secret, self.trust)
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

    def test_progress_aggregates_authenticated_assets_and_stops_on_cancel(self):
        metadata, assets = self.discover()
        total = sum(len(raw) for raw in self.files.values())
        for abort in (False, True):
            with self.subTest(abort=abort):
                observed = []
                cancel = threading.Event()
                stage = Stage(self.root / '.launcher')

                def progress(phase, received, expected):
                    observed.append((phase, received, expected))
                    if abort and received:
                        cancel.set()

                authenticate = Mock(side_effect=lambda raw, sig, files: verifier._verify(raw, sig, files, self.trust))
                try:
                    if abort:
                        with self.assertRaises(client.Cancelled):
                            client._download(metadata, assets, stage, cancel, self.transport,
                                             authenticate, progress=progress)
                        self.assertEqual(len(observed), 2)
                        self.assertLess(observed[-1][1], total)
                        authenticate.assert_not_called()
                    else:
                        client._download(metadata, assets, stage, cancel, self.transport, authenticate, progress=progress)
                        self.assertEqual(observed[-2:], [('download', total, total), ('verify', total, total)])
                        self.assertEqual(sorted({row[1] for row in observed[:-1]}),
                                         [row[1] for row in observed[:-1]])
                        authenticate.assert_called_once()
                    self.assertEqual(observed[0], ('download', 0, total))
                    self.assertTrue(all(row[2] == total for row in observed))
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

    def same_release(self):
        self.planned, self.provenance = fixtures.AppReleaseTests.candidate(self, version='0.1.3')
        self.files = {name: (self.root / name).read_bytes() for name in self.provenance['assets']}
        self.raw, self.signature = verifier._sign(self.provenance, self.files, self.secret, self.trust)
        self.transport = MemoryTransport(self.raw, self.signature, self.files)

    def test_same_013_signed_publication_starts_work_once_without_staging(self):
        self.same_release(); self.signed_client()
        flow = self.startup(version='0.1.3')
        preference = flow.updates.preferences.path.read_bytes()
        with (patch.object(windows, 'installation', return_value=flow.updates.identity),
              patch.object(app_updates, 'Stage') as stage,
              patch.object(windows, 'prepare') as prepare):
            flow.begin(); flow.updates.thread.join(3)
            self.assertFalse(flow.updates.thread.is_alive())
            for _ in range(3): flow.poll(); flow.begin(); flow.skip(); flow.updates.start()
            stage.assert_not_called(); prepare.assert_not_called()
        self.assertEqual(flow.updates.status, 'Keine neuere Appversion veröffentlicht.')
        self.assertIsNone(flow.updates.stage); self.assertIsNone(flow.updates.take())
        self.assertEqual(len(self.transport.calls), 3, 'only catalog, manifest and signature')
        flow.runtime.open.assert_called_once(); flow.runtime.refresh.assert_called_once()
        self.assertEqual(flow.updates.preferences.path.read_bytes(), preference)
        metadata = verifier._verify_metadata(self.raw, self.signature, self.trust)
        with self.assertRaises(ValueError): verifier.assess_update(metadata, '0.1.3')

    def test_same_013_identity_conflicts_warn_without_download(self):
        self.same_release(); self.signed_client()
        for field, value in (('commit', 'f' * 40), ('payload_fingerprint', 'f' * 64),
                             ('product_code', 'foreign'), ('upgrade_code', 'foreign'),
                             ('payload_fingerprint', None)):
            with self.subTest(field=field, value=value):
                flow = self.startup(version='0.1.3')
                flow.updates.identity = replace(flow.updates.identity, **{field: value})
                with patch.object(app_updates, 'Stage') as stage, patch.object(windows, 'prepare') as prepare:
                    flow.begin(); flow.updates.thread.join(3); flow.poll(); flow.poll()
                    stage.assert_not_called(); prepare.assert_not_called()
                self.assertIn('Installationsidentität passt nicht', flow.updates.status)
                flow.runtime.open.assert_called_once(); flow.runtime.refresh.assert_called_once()
        with self.assertRaises(ValueError):
            self.discover('0.1.3')  # Unknown installed context keeps the original guard.
        self.assertFalse(any(url.endswith('.msi') for url in self.transport.calls))

    def test_same_013_broken_channel_never_reports_no_newer_release(self):
        self.same_release()
        for failure in ('signature', 'manifest', 'asset', 'root', 'blocked', 'catalog',
                        'offline', '404', '429', 'tls', 'timeout', 'older'):
            with self.subTest(failure=failure):
                flow = self.startup(version='0.1.4' if failure == 'older' else '0.1.3')
                transport = MemoryTransport(self.raw, self.signature, self.files)
                trust = copy.deepcopy(self.trust)
                if failure == 'signature': transport.files['manifest.sig.json'] = b'invalid'
                if failure == 'manifest': transport.files['manifest.json'] = self.raw.replace(b'0.1.3', b'0.1.2')
                if failure == 'asset': transport.row['assets'][0]['size'] += 1
                if failure == 'root': trust['accepted'] = {}; trust['active_signer'] = None
                if failure == 'blocked': trust['blocked'] = list(trust['accepted'])
                if failure == 'catalog':
                    transport.rows = [{'tag_name': 'game-v9', 'draft': False, 'prerelease': False}] * 100
                errors = {'offline': OSError('offline'), 'tls': urllib.error.URLError('TLS'),
                          'timeout': TimeoutError(), **{str(code): urllib.error.HTTPError(
                              client.API, code, 'synthetic', {}, None) for code in (404, 429)}}
                if failure in errors: transport.read = Mock(side_effect=errors[failure])
                def discover(version, cancel, **kwargs):
                    return client._discover(version, cancel, transport,
                        lambda raw, sig: verifier._verify_metadata(raw, sig, trust), **kwargs)
                with (patch.object(client, 'discover', side_effect=discover),
                      patch.object(app_updates, 'Stage') as stage, patch.object(windows, 'prepare') as prepare):
                    flow.begin(); flow.updates.thread.join(3); flow.poll(); flow.poll()
                    stage.assert_not_called(); prepare.assert_not_called()
                self.assertIn('nicht möglich', flow.updates.status)
                flow.runtime.open.assert_called_once(); flow.runtime.refresh.assert_called_once()

    def test_same_013_skip_optout_stop_and_changed_installation(self):
        self.same_release(); self.signed_client()
        for action in ('skip', 'optout', 'stop', 'changed'):
            with self.subTest(action=action):
                flow = self.startup(version='0.1.3')
                entered, resume = threading.Event(), threading.Event()
                self.addCleanup(resume.set)
                def installation():
                    entered.set()
                    if not resume.wait(3): raise TimeoutError('test boundary')
                    return replace(flow.updates.identity, commit='f' * 40) if action == 'changed' else flow.updates.identity
                with (patch.object(windows, 'installation', side_effect=installation),
                      patch.object(app_updates, 'Stage') as stage, patch.object(windows, 'prepare') as prepare):
                    try:
                        flow.begin(); self.assertTrue(entered.wait(2))
                        flow.runtime.open_requested.set(); flow.poll()
                        flow.runtime.open.assert_not_called(); flow.runtime.refresh.assert_not_called()
                        if action == 'skip': flow.skip()
                        elif action == 'optout': flow.updates.choose(False)
                        elif action == 'stop': flow.stop()
                    finally:
                        resume.set(); flow.updates.thread.join(3)
                    for _ in range(3): flow.poll(); flow.begin(); flow.updates.start()
                    stage.assert_not_called(); prepare.assert_not_called()
                if action == 'stop':
                    flow.runtime.open.assert_not_called(); flow.runtime.refresh.assert_not_called()
                else:
                    flow.runtime.open.assert_called_once(); flow.runtime.refresh.assert_called_once()
                self.assertNotEqual(flow.updates.status, 'Keine neuere Appversion veröffentlicht.')
                self.assertIs(flow.updates.preferences.read(), action != 'optout')

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

    def test_cancel_before_download_leaves_existing_state_unchanged(self):
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

    def test_cancel_during_stream_and_short_write_never_verify_candidate(self):
        metadata, assets = self.discover()
        for failure in ('cancel', 'disk', 'short'):
            stage = Stage(self.root / '.launcher')
            authenticate = Mock()
            original = self.transport.transfer
            def partial(url, output, limit, cancel, deadline, *, expected=None):
                if not url.endswith('.msi'):
                    return original(url, output, limit, cancel, deadline, expected=expected)
                output.write(b'partial')
                if failure == 'cancel':
                    cancel.set(); client.checkpoint(cancel, deadline)
                if failure == 'disk':
                    raise OSError('synthetic disk full after partial write')
            try:
                self.cancel.clear()
                with patch.object(self.transport, 'transfer', side_effect=partial), self.assertRaises((OSError, ValueError)):
                    client._download(metadata, assets, stage, self.cancel, self.transport, authenticate)
                authenticate.assert_not_called()
            finally:
                stage.cleanup()

    def test_closed_helper_boundary_rejects_metadata_only(self):
        metadata, _ = self.discover()
        with self.assertRaisesRegex(ValueError, 'Full verified'):
            windows.prepare(metadata, Mock(), Mock(), Mock())

    def local_identity(self, version):
        product = windows.release(version=version)
        return windows.Installation(self.root / 'program/Picross-Start.exe', version,
            product['product_code'], self.provenance['source_commit'], self.root / 'helper.exe', 'e' * 64,
            product['upgrade_code'], self.provenance['payload_fingerprint'])

    def startup(self, enabled=True, version='0.1.0'):
        host = Mock()
        host.lock.state = self.root
        host.lock.directory = self.root / '.launcher'
        host.stop_requested, host.stopped, host.open_requested = (threading.Event() for _ in range(3))
        host.error = None
        host.request_stop.side_effect = host.stop_requested.set
        if enabled is not None:
            Preferences(host.lock.directory).write(enabled)
        with (patch.object(windows, 'installation', return_value=self.local_identity(version)),
              patch.object(app_updates, 'production_trust', return_value=self.trust)):
            updates = app_updates.Updates(host)
        self.addCleanup(updates.close)
        return Startup(host, updates, Mock())

    def signed_client(self):
        """Real metadata/candidate verification; no public channel or key files."""
        discover = patch.object(client, 'discover', side_effect=lambda version, cancel, **kwargs:
            client._discover(version, cancel, self.transport,
                lambda raw, sig: verifier._verify_metadata(raw, sig, self.trust), **kwargs))
        download = patch.object(client, 'download', side_effect=lambda metadata, assets, stage, cancel:
            client._download(metadata, assets, stage, cancel, self.transport,
                lambda raw, sig, files: verifier._verify(raw, sig, files, self.trust)))
        discover.start(); download.start()
        self.addCleanup(discover.stop); self.addCleanup(download.stop)

    def test_start_gate_signed_candidate_handoff_then_go_without_work(self):
        flow = self.startup(); self.signed_client()
        helper = Mock(); helper.poll.return_value = None
        handoff = windows.Handoff(helper, 'a' * 48)
        def prepare(candidate, *_args, **_kwargs):
            self.assertIs(type(candidate), verifier.VerifiedCandidate)
            flow.runtime.open.assert_not_called(); flow.runtime.refresh.assert_not_called()
            return handoff
        with patch.object(windows, 'prepare', side_effect=prepare):
            flow.begin(); flow.updates.thread.join(3)
        self.assertFalse(flow.updates.thread.is_alive())
        flow.poll()
        self.assertIs(flow.handoff, handoff); self.assertTrue(flow.closing)
        flow.skip(); flow.updates.choose(False); flow.poll()
        self.assertTrue(flow.updates.preferences.read(), 'accepted handoff owns the decision')
        flow.runtime.open.assert_not_called(); flow.runtime.refresh.assert_not_called()
        helper.stdin.write.assert_not_called()
        flow.runtime.stopped.set(); handoff.commit(flow.runtime)
        helper.stdin.write.assert_called_once_with(('GO ' + 'a' * 48 + '\n').encode())

    def test_failure_and_version_decisions_release_work_once(self):
        for failure in ('offline', '429', 'timeout', 'signature', 'empty', 'same', 'old'):
            with self.subTest(failure=failure):
                flow = self.startup(version={'same': '0.1.1', 'old': '0.1.2'}.get(failure, '0.1.0'))
                transport = MemoryTransport(self.raw, self.signature, self.files)
                if failure == 'signature': transport.files['manifest.sig.json'] = b'invalid'
                if failure == 'empty': transport.rows = []
                errors = {'offline': OSError('offline'), '429': urllib.error.HTTPError(client.API, 429, '', {}, None),
                          'timeout': TimeoutError()}
                def discover(version, cancel, **kwargs):
                    if failure in errors: raise errors[failure]
                    # Deliberately omit identity: the original same-version
                    # guard still rejects an unknown installed context.
                    return client._discover(version, cancel, transport,
                        lambda raw, sig: verifier._verify_metadata(raw, sig, self.trust))
                with patch.object(client, 'discover', side_effect=discover), patch.object(windows, 'prepare') as prepare:
                    flow.begin(); flow.updates.thread.join(3)
                    for _ in range(3): flow.poll(); flow.begin(); flow.skip()
                    flow.runtime.open.assert_called_once(); flow.runtime.refresh.assert_called_once()
                    prepare.assert_not_called(); self.assertIn('nicht möglich', flow.updates.status)
                    flow.updates.close()

    def test_skip_optout_stop_at_network_download_and_handoff_boundaries(self):
        self.signed_client()
        for phase in ('metadata', 'download', 'handoff'):
            for action in ('skip', 'optout', 'stop'):
                with self.subTest(phase=phase, action=action):
                    flow = self.startup()
                    entered, release = threading.Event(), threading.Event()
                    self.addCleanup(release.set)
                    helper = Mock(); helper.poll.return_value = None
                    helper.stdin.closed = False
                    helper.stdin.close.side_effect = lambda: setattr(helper.stdin, 'closed', True)
                    handoff = windows.Handoff(helper, 'b' * 48)
                    def pause():
                        entered.set()
                        if not release.wait(3): raise TimeoutError('test boundary not released')
                    original = self.transport.transfer
                    def transfer(*args, **kwargs):
                        if phase == 'download' and args[0].endswith('.msi'): pause()
                        return original(*args, **kwargs)
                    def discover(version, cancel, **kwargs):
                        if phase == 'metadata': pause()
                        return client._discover(version, cancel, self.transport,
                            lambda raw, sig: verifier._verify_metadata(raw, sig, self.trust))
                    def prepare(candidate, *_args, **_kwargs):
                        self.assertIs(type(candidate), verifier.VerifiedCandidate)
                        if phase == 'handoff': pause()  # Child began before click, no GO yet.
                        return handoff
                    with (patch.object(client, 'discover', side_effect=discover),
                          patch.object(self.transport, 'transfer', side_effect=transfer),
                          patch.object(windows, 'prepare', side_effect=prepare) as prepared):
                        try:
                            flow.begin(); self.assertTrue(entered.wait(2))
                            flow.runtime.open_requested.set(); flow.poll()
                            flow.runtime.open.assert_not_called(); flow.runtime.refresh.assert_not_called()
                            if action == 'skip': flow.skip()
                            elif action == 'optout': flow.updates.choose(False); flow.poll()
                            else: flow.stop()
                            self.assertTrue(flow.updates.thread.is_alive(), 'GUI must not wait on network/handshake')
                            if action == 'stop':
                                flow.runtime.open.assert_not_called(); flow.runtime.refresh.assert_not_called()
                            else:
                                flow.runtime.open.assert_called_once(); flow.runtime.refresh.assert_called_once()
                            self.assertIs(flow.updates.preferences.read(), action != 'optout')
                        finally:
                            release.set(); flow.updates.close()
                        for _ in range(3): flow.poll(); flow.skip()
                        self.assertIsNone(flow.handoff); self.assertIsNone(flow.updates.take())
                        helper.stdin.write.assert_not_called()
                        if phase == 'handoff': self.assertTrue(helper.stdin.close.called)
                        else: prepared.assert_not_called()
                        if flow.updates.stage: self.assertFalse(flow.updates.stage.path.exists())

    def test_completed_handoff_can_be_skipped_before_gui_takes_it(self):
        flow = self.startup(); self.signed_client()
        helper = Mock(); handoff = windows.Handoff(helper, 'c' * 48)
        helper.stdin.closed = False
        helper.stdin.close.side_effect = lambda: setattr(helper.stdin, 'closed', True)
        with patch.object(windows, 'prepare', return_value=handoff):
            flow.begin(); flow.updates.thread.join(3)
        self.assertTrue(flow.updates.pending)
        flow.skip(); flow.poll()
        flow.runtime.open.assert_called_once(); flow.runtime.refresh.assert_called_once()
        self.assertIsNone(flow.handoff); helper.stdin.write.assert_not_called()
        helper.stdin.close.assert_called_once()

    def test_completion_between_take_and_pending_cannot_release_browser(self):
        flow = self.startup(); self.signed_client()
        handoff = windows.Handoff(Mock(), 'd' * 48)
        with patch.object(windows, 'prepare', return_value=handoff):
            flow.begin(); flow.updates.thread.join(3)
        # Model the exact poll that observed a live thread just before completion.
        with patch.object(flow.updates, 'take', return_value=None): flow.poll()
        flow.runtime.open.assert_not_called(); flow.runtime.refresh.assert_not_called()
        flow.poll(); self.assertIs(flow.handoff, handoff)

    def test_no_optin_and_browser_error_do_not_repeat_initial_work(self):
        for enabled in (None, False):
            with self.subTest(enabled=enabled):
                flow = self.startup(enabled=enabled)
                flow.runtime.open.side_effect = OSError('no browser')
                with patch.object(client, 'discover') as discover:
                    flow.begin(); flow.begin(); flow.poll()
                    discover.assert_not_called()
                flow.runtime.open.assert_called_once(); flow.runtime.refresh.assert_called_once()
                flow.browser_error.assert_called_once()
                flow.runtime.open.side_effect = None
                flow.runtime.open_requested.set(); flow.poll()
                self.assertEqual(flow.runtime.open.call_count, 2)
                flow.runtime.refresh.assert_called_once()

    def test_cancellation_before_native_spawn_prevents_late_helper(self):
        # Exercise the real Python prepare path up to Popen with no Windows API
        # or executable process. Trust/installation are isolated test adapters.
        metadata, assets = self.discover()
        stage = Stage(self.root / '.launcher')
        candidate = client._download(metadata, assets, stage, self.cancel, self.transport,
            lambda raw, sig, files: verifier._verify(raw, sig, files, self.trust))
        host = self.startup().runtime
        helper = self.root / 'helper.exe'; helper.write_bytes(b'synthetic, never executed')
        executable = self.root / 'app.exe'; executable.write_bytes(b'synthetic app')
        identity = replace(self.local_identity('0.1.0'), executable=executable, helper=helper, helper_sha256=windows.sha(helper))
        host.metadata = {'instance': 'a' * 48}; host.no_browser = True
        (self.root / 'config.json').write_bytes(b'config')
        (host.lock.directory / 'address.json').write_bytes(b'address')
        report = {**strict_json(self.files['delivery.json']), 'exe_sha256': 'e' * 64, 'exe_bytes': 10}
        def handle(): self.cancel.set(); return None  # Skip wins just before spawn.
        original_json = windows.strict_json
        def decode(raw):
            return report if raw == self.files['delivery.json'] else original_json(raw)
        try:
            with (patch.object(windows, 'installation', return_value=identity),
                  patch.object(windows, 'verify_candidate', return_value=candidate),
                  patch.object(windows, 'strict_json', side_effect=decode),
                  patch.object(windows, 'parent_handle', side_effect=handle),
                  patch.object(windows.ctypes, 'WinDLL', create=True),
                  patch.object(windows.subprocess, 'STARTUPINFO', create=True),
                  patch.object(windows.subprocess, 'Popen') as spawn):
                with self.assertRaises(client.Cancelled):
                    windows.prepare(candidate, stage, identity, host, cancelled=self.cancel, transition=threading.Lock())
                spawn.assert_not_called()
            self.assertFalse(stage.path.exists())
        finally:
            if stage.path.exists(): stage.cleanup()


class InstallationTests(unittest.TestCase):
    def test_identity_reads_packaged_build_and_registered_msi(self):
        with tempfile.TemporaryDirectory(prefix='app-b2-n-identity-') as folder:
            root = Path(folder)
            executable = root / 'Programs/Picross-Produktionsassistent/Picross-Start.exe'
            executable.parent.mkdir(parents=True); executable.write_bytes(b'synthetic exe')
            package = root / 'packaged'; package.mkdir()
            helper = package / 'UpdateHelper.exe'; helper.write_bytes(b'synthetic helper')
            product = windows.release(version='0.1.3')
            built = {'format': 'picross-windows-app-v1', 'architecture': 'windows-x64',
                     'version': product['version'], 'product_code': product['product_code'],
                     'upgrade_code': product['upgrade_code'], 'commit': 'a' * 40,
                     'payload_fingerprint': 'b' * 64, 'resources': {'UpdateHelper.exe': windows.sha(helper)}}
            def write(value, components=None):
                (package / 'build.json').write_bytes(canonical(value))
                (executable.parent / 'components.json').write_bytes(canonical(value if components is None else components))
            write(built)
            with (patch.object(windows, 'os', SimpleNamespace(name='nt')),
                  patch.object(windows, 'sys', SimpleNamespace(frozen=True, executable=str(executable))),
                  patch.object(windows, 'PACKAGE', package),
                  patch.object(windows, 'local_appdata', return_value=root),
                  patch.object(windows.ctypes, 'windll', create=True) as dll,
                  patch.object(windows, 'installed_version', return_value='0.1.3') as registered):
                dll.shell32.IsUserAnAdmin.return_value = False
                identity = windows.installation()
                self.assertEqual((identity.version, identity.commit, identity.payload_fingerprint,
                                  identity.product_code, identity.upgrade_code),
                                 ('0.1.3', 'a' * 40, 'b' * 64, product['product_code'], product['upgrade_code']))
                registered.assert_called_once_with(product['product_code'])
                for field, value in (('payload_fingerprint', None), ('payload_fingerprint', 'invalid'),
                                     ('commit', 'short'), ('product_code', 'foreign'), ('upgrade_code', 'foreign')):
                    with self.subTest(field=field, value=value):
                        write({**built, field: value})
                        with self.assertRaises(ValueError): windows.installation()
                write(built, {**built, 'payload_fingerprint': 'c' * 64})
                with self.assertRaises(ValueError): windows.installation()
                write(built); registered.return_value = '0.1.2'
                with self.assertRaises(ValueError): windows.installation()
                registered.side_effect = ValueError('MSI not registered')
                with self.assertRaises(ValueError): windows.installation()


class TransportTests(unittest.TestCase):
    class Response(BytesIO):
        status = 200
        def __init__(self, raw, headers=None, final=None):
            super().__init__(raw); self.headers = headers or {}; self.final = final or client.API + '?per_page=100&page=1'
        def geturl(self):
            return self.final

    def transfer(self, response, limit=20, expected=None):
        transport = client.Transport()
        opener = Mock()
        opener.open.return_value = response
        output = BytesIO()
        with patch.object(client.github_rest, 'build_opener', return_value=opener):
            transport.transfer(client.API + '?per_page=100&page=1', output, limit, threading.Event(),
                               time.monotonic()+10, expected=expected)
        request = opener.open.call_args.args[0]
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
        for error, kind in ((OSError('offline'), 'network'), (TimeoutError(), 'network'),
                            (urllib.error.URLError('TLS'), 'network'),
                            (urllib.error.HTTPError(client.API, 404, 'missing', {}, None), 'source'),
                            (urllib.error.HTTPError(client.API, 429, 'rate limit', {}, None), 'rate_limit')):
            transport = client.Transport()
            opener = Mock()
            opener.open.side_effect = error
            with self.subTest(error=type(error)), patch.object(client.github_rest, 'build_opener', return_value=opener):
                with self.assertRaises(client.github_rest.Failure) as failure:
                    transport.read(client.API+'?page=1', 100, threading.Event(), time.monotonic()+1)
                self.assertEqual(failure.exception.kind, kind)


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
        def discover(*_, **_kwargs): entered.set(); release.wait(3); return Mock(),{}
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

    def test_empty_root_never_starts_check_even_with_stored_optin(self):
        runtime=Mock(); runtime.lock.state=self.root; runtime.lock.directory=self.root/'.launcher'
        runtime.stop_requested = threading.Event(); runtime.open_requested = threading.Event()
        Preferences(runtime.lock.directory).write(True)
        with (patch.object(windows,'installation',return_value=Mock(version='0.1.0',executable=self.root/'program'/'Picross-Start.exe')),
              patch.object(app_updates,'production_trust',return_value={'accepted':{}}),
              patch.object(client,'discover') as discover):
            updates=app_updates.Updates(runtime)
            flow = Startup(runtime, updates, self.fail)
            flow.begin(); flow.poll(); flow.begin()
            runtime.open.assert_called_once(); runtime.refresh.assert_called_once()
            self.assertIn('inaktiv',updates.status); discover.assert_not_called()
            for _ in range(12): updates.poll_result()
            self.assertEqual(updates.recovery_attempts,10)



class EditorUpdateTests(unittest.TestCase):
    """PE exercises the same signed channel and GUI controller, without MSI execution."""
    def setUp(self):
        from tools.app_products import PE
        self.app = PE
        temp = tempfile.TemporaryDirectory(prefix="pe-app-b-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.api = fixtures.MemoryGitHub(app=PE)
        self.trust, self.secret = update_diagnostic.test_identity(app=PE)
        self.plan, manifest = fixtures.AppReleaseTests.candidate(self, app=PE)
        self.files = {n: (self.root/n).read_bytes() for n in manifest["assets"]}
        self.raw, self.signature = verifier._sign(manifest, self.files, self.secret, self.trust, app=PE)
        self.transport = MemoryTransport(self.raw, self.signature, self.files)
        self.cancel = threading.Event()

    def discover(self, version="0.2.0", **kwargs):
        return client._discover(version, self.cancel, self.transport,
            lambda raw, sig: verifier._verify_metadata(raw, sig, self.trust, app=self.app), app=self.app, **kwargs)

    def identity(self):
        m = strict_json(self.raw)
        return SimpleNamespace(version=m["version"], commit=m["source_commit"], payload_fingerprint=m["payload_fingerprint"],
            product_code=m["product_code"], upgrade_code=m["upgrade_code"], executable=self.root/"program"/"editor.exe")

    def test_editor_channel_full_bytes_and_cross_app(self):
        metadata, assets = self.discover()
        self.assertEqual(len(self.transport.calls), 3)
        stage = Stage(self.root/"state"/".updates")
        try:
            result = client._download(metadata, assets, stage, self.cancel, self.transport,
                lambda raw, sig, files: verifier._verify(raw, sig, files, self.trust, app=self.app))
            self.assertIs(type(result), verifier.VerifiedCandidate)
            with self.assertRaises(ValueError): verifier.assess_update(result, "0.1.0")
            with self.assertRaises(ValueError): verifier.assess_update(result, "0.2.2", app=self.app)
        finally: stage.cleanup()
        self.transport.rows = [{**self.transport.row, "tag_name":"pw-v0.1.99"}]
        with self.assertRaises(ValueError): self.discover()

    def test_same_version_authenticates_local_source_and_never_downloads(self):
        local = self.identity()
        result, _ = self.discover(local.version, installation=local)
        self.assertEqual(result.version, local.version)
        self.assertEqual(len(self.transport.calls), 3)
        self.transport.calls.clear()
        for field in ("commit", "payload_fingerprint", "product_code", "upgrade_code"):
            with self.subTest(field=field):
                different = SimpleNamespace(**{**vars(local), field:"foreign"})
                with self.assertRaises(client.InstallationMismatch): self.discover(local.version, installation=different)
        self.assertFalse(any(u.endswith(".msi") for u in self.transport.calls))

    def controller(self, enabled=True):
        from tools.puzzle_editor.app_updates import Controller
        state = self.root/"state"
        if enabled is not None: Preferences(state/".updates").write(enabled)
        identity = self.identity(); identity.version="0.2.0"
        with patch.object(windows,"installation",return_value=identity), patch.object(verifier,"production_trust",return_value=self.trust):
            # Delay starting until each test has attached its controlled worker.
            with patch.object(app_updates.Updates,"start",return_value=False): controller=Controller(state)
        self.addCleanup(lambda: controller.finish("test cleanup"))
        return controller

    def test_no_consent_portable_and_invalid_preference_never_request(self):
        from tools.puzzle_editor.app_updates import Controller
        with patch.object(windows,"installation",side_effect=ValueError("portable")), patch.object(client,"discover") as request:
            portable=Controller(self.root/"portable-state")
            portable.poll(); portable.choose(True); portable.finish()
            self.assertFalse((self.root/"portable-state").exists()); request.assert_not_called()
        controller=self.controller(None)
        self.assertTrue(controller.waiting)
        with patch.object(client,"discover") as request:
            controller.poll(); request.assert_not_called()
            controller.skip(); self.assertFalse(controller.waiting)
            controller.choose(True); request.assert_not_called()
            self.assertTrue(controller.updates.preferences.read())
        controller.finish()
        (self.root/"state"/".updates"/"app-updates.json").write_bytes(b'{"enabled":"yes"}')
        controller=self.controller(None)
        with patch.object(client,"discover") as request:
            self.assertFalse(controller.updates.start()); request.assert_not_called()
            self.assertIsNone(controller.updates.enabled)

    def test_skip_and_optout_before_helper_take_prevent_go(self):
        for action in ("skip", "optout", "stop"):
            with self.subTest(action=action):
                controller=self.controller()
                entered, release = threading.Event(), threading.Event()
                def delayed(*a, **kw):
                    entered.set(); self.assertTrue(release.wait(5))
                    return self.discover()
                with patch.object(client,"discover",side_effect=delayed), patch.object(windows,"prepare") as prepare:
                    controller.waiting=controller.updates.start()
                    self.assertTrue(entered.wait(5))
                    if action=="skip": controller.skip()
                    elif action=="optout": controller.choose(False)
                    else: controller.stopping()
                    release.set(); controller.updates.thread.join(5); controller.poll()
                    prepare.assert_not_called(); self.assertIsNone(controller.handoff)
                self.assertEqual(controller.updates.preferences.read(), action!="optout")
                controller.finish()

    def test_taken_handoff_locks_choice_and_requires_successful_finally(self):
        controller=self.controller()
        handoff=Mock(committed=False,selection=controller.runtime.selection)
        controller.updates.thread=Mock(); controller.updates.thread.is_alive.return_value=False
        controller.updates.handoff=handoff
        self.assertIs(controller.poll(),handoff)
        controller.skip(); controller.choose(False)
        self.assertTrue(controller.waiting); self.assertTrue(controller.updates.preferences.read())
        controller.finish("drain failed")
        handoff.commit.assert_not_called(); handoff.abort.assert_called()

    def test_editor_recovery_inventory_cannot_accept_pw_or_foreign_files(self):
        from tools.production_workspace.release import release
        launcher=self.root/"state"/".updates"
        stage=Stage(launcher)
        msi=release(version="0.2.1",app=self.app)["filename"]
        names={msi,msi+".sha256","START.txt","delivery.json","inputs.json","manifest.json","manifest.sig.json","UpdateHelper.exe","active"}
        for name in names: stage.write(name,b"test")
        pending={"format":"picross-update-pending-v1","nonce":stage.path.name,"stage":stage.path.name,"version":"0.2.1","files":sorted(names)}
        atomic_json(launcher/"update-pending.json",pending)
        self.assertIn("unbestätigt",recover(launcher,app=self.app))
        with self.assertRaises(ValueError): recover(launcher)
        atomic_json(launcher/"update-result.json",{"format":"picross-update-result-v1","nonce":stage.path.name,"version":"0.2.1","status":"cancelled"})
        (stage.path/"foreign.txt").write_bytes(b"preserve")
        with self.assertRaises(OSError): recover(launcher,app=self.app)
        self.assertEqual((stage.path/"foreign.txt").read_bytes(),b"preserve")
        (stage.path/"foreign.txt").unlink()
        self.assertIn("abgebrochen",recover(launcher,app=self.app))
        self.assertFalse(stage.path.exists())

    def test_hardlink_update_input_rejected_without_touching_original(self):
        original=self.root/"original"; original.write_bytes(b"preserve")
        alias=self.root/"alias"
        try: os.link(original,alias)
        except OSError as exc: self.skipTest(str(exc))
        with self.assertRaises(ValueError): no_links(alias)
        self.assertEqual(original.read_bytes(),b"preserve")

    def test_changed_selection_aborts_before_drain_and_config_is_untouched(self):
        controller=self.controller()
        handoff=Mock(committed=False,selection=controller.runtime.selection)
        controller.updates.thread=Mock(); controller.updates.thread.is_alive.return_value=False
        controller.updates.handoff=handoff
        controller.select({"checkout": "C:/other ü", "port": "1234"})
        self.assertIsNone(controller.poll())
        self.assertFalse(controller.waiting); handoff.abort.assert_called()
        controller.finish(); handoff.commit.assert_not_called()
        self.assertFalse((self.root/"state/config.json").exists())

    def test_restart_selection_is_canonical_and_only_display_data(self):
        from tools.puzzle_editor.app_updates import restored_selection, selection_data
        selection={"checkout": 'C:/path ü \"quoted\"', "port": "bad"}
        raw=selection_data(selection)
        with patch.dict(os.environ,{"PICROSS_PE_READY_SELECTION":raw,"PICROSS_PE_READY_KEY":"a"*48,"PICROSS_PE_READY_NONCE":"b"*48}):
            self.assertEqual(restored_selection("ignored",0),selection)
            self.assertNotIn("PICROSS_PE_READY_SELECTION",os.environ)
        for value in ({"checkout":"", "port":0}, {"checkout":"","port":"0","command":"bad"}):
            with self.assertRaises(ValueError): selection_data(value)


    def test_first_editor_start_and_late_selection_change_cannot_install(self):
        controller=self.controller(False)
        with patch.object(client,"discover") as network:
            controller.skip()  # Same release called by the first manual editor start.
            controller.choose(True)
            network.assert_not_called()
            self.assertTrue(controller.updates.preferences.read())
        controller.finish()
        controller=self.controller()
        handoff=Mock(committed=False,selection=controller.runtime.selection)
        controller.updates.thread=Mock(); controller.updates.thread.is_alive.return_value=False
        controller.updates.handoff=handoff
        self.assertIs(controller.poll(),handoff)
        controller.select({"checkout":"late","port":"12"})
        controller.finish()
        handoff.commit.assert_not_called(); handoff.abort.assert_called()


if __name__ == '__main__':
    unittest.main()
