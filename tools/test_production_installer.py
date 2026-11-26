"""P4-T01: inexpensive source/metadata guards, never build or install an MSI."""
import json
from pathlib import Path
import tempfile
import unittest
import os
import threading
import uuid
import copy
import urllib.error
import urllib.parse
from unittest.mock import patch, MagicMock
import xml.etree.ElementTree as ET

from tools.production_workspace import build_installer as installer
from tools.production_workspace.release import release, version_tuple
from tools.production_workspace import payload, release_channel as channel, verify_installer, update_verifier
from tools.production_workspace.update_diagnostic import test_identity

ROOT = Path(__file__).resolve().parents[1]
NS = {'w': installer.NS}


class InstallerContractTests(unittest.TestCase):
    def test_pw_raster_fixture_keeps_committed_marker_and_both_methods(self):
        from tools.production_workspace.smoke_windows import check_raster_data_tree, git, raster_fixture
        from tools.puzzle_production.catalog_integration import TEST_CATALOG

        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = root / 'data'
            commit_id, paths, cases = raster_fixture(repo, root)
            marker, expected = TEST_CATALOG
            self.assertIn(marker, paths)
            self.assertEqual(git(repo, 'show', f'{commit_id}:{marker}'), expected)
            methods = {}
            for puzzle_id in cases:
                path = f'content/authoring/{puzzle_id}/current/record.json'
                raw = git(repo, 'show', f'{commit_id}:{path}')
                record = json.loads(raw)
                difficulty = record['rasters'][0]['difficulty']['file']
                methods[puzzle_id] = json.loads(git(repo, 'show', f'{commit_id}:{difficulty}'))['method']
            self.assertEqual(methods, {'pz-frozen-04': 'picross-difficulty-0.4',
                                       'pz-frozen-03': 'picross-difficulty-0.3'})
            previous = git(repo, 'rev-parse', 'HEAD^').decode('ascii').strip()
            with self.assertRaisesRegex(RuntimeError, 'anderen Commit'):
                check_raster_data_tree(repo, previous)

    def test_pw_raster_fixture_rejects_invalid_marker_and_foreign_files(self):
        from tests.puzzle_production import current_fixtures
        from tools.production_workspace.smoke_windows import raster_fixture
        from tools.puzzle_production.catalog_integration import TEST_CATALOG
        from tools.puzzle_production.contract import InvalidInput

        checkout = current_fixtures.checkout
        marker = TEST_CATALOG[0]
        marker_error = 'Test-only input cannot enter product catalog'
        for name, raw, error, message in (
            (marker, b'wrong marker\n', InvalidInput, marker_error),
            (marker, None, InvalidInput, marker_error),
            ('content/unexpected', b'foreign', RuntimeError, 'content/unexpected'),
            ('game/data/unexpected.py', b'raise RuntimeError\n', RuntimeError, r'game/data/unexpected\.py'),
        ):
            with self.subTest(path=name, raw=raw), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)

                def modified_checkout(repo):
                    checkout(repo)
                    if raw is None:
                        (repo / name).unlink()
                    else:
                        current_fixtures.put(repo, name, raw)

                with patch.object(current_fixtures, 'checkout', side_effect=modified_checkout):
                    with self.assertRaisesRegex(error, message):
                        raster_fixture(root / 'data', root)

    @unittest.skipUnless(os.name == 'nt', 'Actual Windows kernel mutex regression')
    def test_idle_versus_held_kernel_mutex_without_touching_real_msi(self):
        import ctypes
        from ctypes import wintypes as w
        from tools.production_workspace.install_interlock import _mutex_busy
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.CreateMutexW.argtypes = [ctypes.c_void_p, w.BOOL, w.LPCWSTR]
        kernel.CreateMutexW.restype = w.HANDLE
        kernel.CloseHandle.argtypes = [w.HANDLE]
        kernel.ReleaseMutex.argtypes = [w.HANDLE]
        name = 'Local\\Picross.P4.Test.' + uuid.uuid4().hex
        self.assertFalse(_mutex_busy(name))
        idle = kernel.CreateMutexW(None, False, name)
        try:
            self.assertTrue(idle)
            self.assertFalse(_mutex_busy(name))
        finally:
            kernel.CloseHandle(idle)
        entered, release = threading.Event(), threading.Event()
        def owner():
            handle = kernel.CreateMutexW(None, True, name)
            try:
                entered.set(); release.wait(10)
            finally:
                kernel.ReleaseMutex(handle); kernel.CloseHandle(handle)
        thread = threading.Thread(target=owner); thread.start()
        try:
            self.assertTrue(entered.wait(5))
            self.assertTrue(_mutex_busy(name))
        finally:
            release.set(); thread.join(5)
        self.assertFalse(_mutex_busy(name))

    def test_release_checkout_uses_shallow_bounded_git_without_history_scan(self):
        # The signed published release, not every intermediate Git commit, is version authority.
        for source in ('tools/production_workspace/release.py',
                       'tools/production_workspace/build_windows.py'):
            self.assertNotIn('check_history', (ROOT / source).read_text(encoding='utf-8'))
        for name in ('pe-installer.yml', 'pw-installer.yml'):
            workflow = (ROOT / '.github/workflows' / name).read_text(encoding='utf-8')
            checkouts = workflow.split('      - uses: actions/checkout@')[1:]
            self.assertEqual(len(checkouts), 4, name)
            self.assertNotIn('fetch-depth: 0', workflow)
            for checkout in checkouts:
                self.assertIn('\n        timeout-minutes: 10\n        with:\n', checkout[:210], name)
                self.assertIn('\n          fetch-depth: 1\n', checkout[:400], name)
                self.assertIn('\n          persist-credentials: false\n', checkout[:470], name)

    def test_strict_msi_versions_and_identity(self):
        for invalid in ('01.2.3', '1.0', '1.2.3.4', '1.2.3-rc1', '256.0.0', '1.256.0', '1.0.65536', '0.0.0', '1.2.3\n'):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                version_tuple(invalid)
        product = release()
        self.assertIn(product['version'], product['filename'])
        self.assertEqual(product['product_code'], release()['product_code'])
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'release.json'
            other = {**product, 'version': '255.255.65535'}
            path.write_text(json.dumps(other))
            updated = release(path)
            self.assertEqual(updated['upgrade_code'], product['upgrade_code'])
            self.assertNotEqual(updated['product_code'], product['product_code'])
            self.assertGreater(version_tuple(updated['version']), version_tuple(product['version']))

    def test_generated_installer_is_per_user_preserves_state_and_refuses_running_or_same_version(self):
        with tempfile.TemporaryDirectory() as folder:
            app = Path(folder); (app / 'Picross-Start.exe').write_bytes(b'synthetic')
            (app / 'LICENSES').mkdir(); (app / 'LICENSES/Python.txt').write_text('synthetic')
            root = installer.wix_source(app, release(), app / 'guard.dll').getroot()
            package = root.find('.//w:Package', NS)
            self.assertEqual(package.get('InstallScope'), 'perUser')
            self.assertEqual(package.get('InstallPrivileges'), 'limited')
            self.assertEqual(root.find('.//w:MajorUpgrade', NS).get('Schedule'), 'afterInstallInitialize')
            self.assertIn('NOT SAMEVERSION', root.find('.//w:Product/w:Condition', NS).text)
            self.assertEqual(root.find('.//w:UpgradeVersion', NS).get('IncludeMaximum'), 'yes')
            check = root.find('.//w:InstallExecuteSequence/w:Custom', NS)
            self.assertEqual(check.get('Before'), 'InstallValidate')
            self.assertEqual(check.text, '1')  # Includes fresh install, upgrade AND uninstall.
            self.assertIsNone(root.find('.//w:RemoveFile', NS))
            self.assertEqual(len(root.findall('.//w:File', NS)), 2)
            self.assertTrue(all(e.get('Root') == 'HKCU' for e in root.findall('.//w:RegistryValue', NS)))
            text = ET.tostring(root).decode()
            self.assertNotIn('PicrossProductionWorkspace/.launcher', text)
            guard = (ROOT / 'tools/production_workspace/packaging/Guard.cs').read_text()
            self.assertIn('RmGetList', guard)
            self.assertIn('FileShare.None', guard)
            self.assertNotIn('RmShutdown(', guard)

    def test_release_workflow_is_isolated_and_write_access_is_gated(self):
        workflow = (ROOT / '.github/workflows/pw-installer.yml').read_text()
        triggers = workflow.split('\non:\n', 1)[1].split('\npermissions:', 1)[0]
        self.assertIn('workflow_dispatch:', triggers)
        self.assertNotIn('inputs:', triggers)
        self.assertIn('workflow_run:', triggers)
        self.assertIn('workflows: [Package CI]', triggers)
        self.assertIn("vars.PW_RELEASE_ENABLED == 'true'", workflow)
        self.assertIn("vars.PW_UPDATE_SIGNING_ENABLED == 'true'", workflow)
        self.assertEqual(workflow.count('environment: pw-app-release'), 1)
        self.assertEqual(workflow.count('secrets.PW_UPDATE_SIGNING_KEY'), 1)
        self.assertNotIn('secrets.PW_UPDATE_SIGNING_KEY', workflow.split('\n  publish:', 1)[0])
        self.assertIn("needs.publication-gate.outputs.authorized == 'true'", workflow)
        self.assertIn("github.event_name == 'workflow_run' && github.ref == 'refs/heads/main'", workflow)
        self.assertEqual(workflow.count('contents: write'), 1)
        self.assertNotIn('contents: write', workflow.split('\n  publish:', 1)[0])
        self.assertIn('-m tools.production_workspace.verify_installer', workflow)
        self.assertIn('--compare-build', workflow)
        self.assertNotIn('smoke-user.ps1', workflow)
        for forbidden in ('pull_request:', 'push:', 'schedule:', 'workflow_call:'):
            self.assertNotIn(forbidden, triggers)
        for path in (ROOT / '.github/workflows/ci-modular.yml', ROOT / 'tools/ci_modular.py'):
            self.assertNotIn('build_installer', path.read_text())
            self.assertNotIn('smoke_installer', path.read_text())

    def test_build_version_is_injected_without_changing_start_anchor(self):
        before = channel.release.__globals__['SOURCE'].read_bytes()
        product = release(version='0.1.1')
        self.assertEqual(product['version'], '0.1.1')
        self.assertEqual(product['upgrade_code'], release()['upgrade_code'])
        self.assertNotEqual(product['product_code'], release()['product_code'])
        self.assertEqual(channel.release.__globals__['SOURCE'].read_bytes(), before)
        for version in ('0.0.9', '1.0.0', '0.2.0', '0.1.65536'):
            with self.subTest(version=version), self.assertRaises(ValueError):
                release(version=version)

    def test_checksum_producer_uses_canonical_bytes_on_windows_and_linux(self):
        with tempfile.TemporaryDirectory() as folder:
            msi = Path(folder) / 'synthetic.msi'
            msi.write_bytes(b'Synthetic MSI bytes')
            checksum = installer.write_checksum(msi)
            raw = (msi.parent / (msi.name + '.sha256')).read_bytes()
            self.assertEqual(raw, (checksum + '  synthetic.msi\n').encode('utf-8'))
            self.assertNotIn(b'\r', raw)


class MemoryGitHub(channel.GitHub):
    """Synthetic API only; records writes and supports lost upload responses."""
    def __init__(self, *, app=None):
        from tools.app_products import PW
        self.app = app or PW
        self.source = 'a' * 40
        repo = {'id': channel.REPOSITORY_ID, 'full_name': channel.REPOSITORY}
        self.run = {'workflow_id': 8, 'path': '.github/workflows/ci-modular.yml', 'name': 'Package CI',
                    'event': 'push', 'head_branch': 'main', 'head_sha': self.source, 'status': 'completed',
                    'conclusion': 'success', 'repository': repo, 'head_repository': copy.deepcopy(repo), 'run_attempt': 1}
        self.jobs = [{'name': n, 'status': 'completed', 'conclusion': 'success'} for n in ('docs', 'ci-required')]
        self.entries, self.blobs, self.tags, self.writes = [], {}, {}, []
        self.catalog_owner = None
        self.fail_upload = None
        self.change_main_after_upload = False

    def request(self, path, *, method='GET', value=None, raw=None, binary=False, upload=False):
        path = path.removeprefix(channel.PREFIX)
        parts = urllib.parse.urlsplit(path)
        route = parts.path
        query = urllib.parse.parse_qs(parts.query)
        ref = 'heads/' + channel.release_catalog.LOCK_BRANCH
        if route == '/git/ref/' + ref:
            return {'object': {'sha': self.catalog_owner}} if self.catalog_owner else None
        if route == '/git/refs' and method == 'POST' and value['ref'] == 'refs/' + ref:
            if self.catalog_owner:
                raise channel.RefAlreadyExists('Catalog ref already exists')
            self.catalog_owner = value['sha']
            return {'ref': value['ref']}
        if route == '/git/refs/' + ref and method == 'DELETE':
            assert self.catalog_owner
            self.catalog_owner = None
            return None
        if method != 'GET':
            self.writes.append((method, route))
        if route == '/environments/' + self.app.environment:
            return {'name': self.app.environment, 'deployment_branch_policy':
                    {'protected_branches': False, 'custom_branch_policies': True}}
        if route == '/environments/' + self.app.environment + '/deployment-branch-policies':
            return {'branch_policies': [{'name': 'main', 'type': 'branch'}]}
        if route == '/actions/workflows/ci-modular.yml':
            return {'id': 8}
        if route == '/actions/runs/9':
            return copy.deepcopy(self.run)
        if route == '/actions/runs/9/attempts/1/jobs':
            return {'jobs': copy.deepcopy(self.jobs)}
        if route == '/git/ref/heads/main':
            return {'object': {'type': 'commit', 'sha': self.source}}
        if route.startswith('/git/ref/tags/'):
            sha = self.tags.get(route.rsplit('/', 1)[-1])
            return {'object': {'type': 'commit', 'sha': sha}} if sha else None
        if route.startswith('/releases/assets/'):
            return self.blobs[int(route.rsplit('/', 1)[-1])]
        if route == '/releases':
            if method == 'GET':
                start = 100 * (int(query['page'][0]) - 1)
                return copy.deepcopy(self.entries[start:start + 100])
            entry = {**value, 'id': len(self.entries) + 1, 'assets': [], 'html_url': 'https://github.com/synthetic/release'}
            self.entries.append(entry)
            return copy.deepcopy(entry)
        match = __import__('re').fullmatch(r'/releases/(\d+)(/assets)?', route)
        if match:
            entry = self.entries[int(match[1]) - 1]
            if match[2]:
                if method == 'GET':
                    return copy.deepcopy(entry['assets'])
                name = query['name'][0]
                asset_id = len(self.blobs) + 1
                self.blobs[asset_id] = raw
                entry['assets'].append({'id': asset_id, 'name': name, 'state': 'uploaded',
                                        'size': len(raw), 'digest': 'sha256:' + channel.digest(raw)})
                if self.change_main_after_upload:
                    self.source = 'b' * 40
                if self.fail_upload == name:
                    self.fail_upload = None
                    raise RuntimeError('synthetic lost upload response')
                return b'{}'
            if method == 'PATCH':
                entry.update(value)
                self.tags[entry['tag_name']] = entry['target_commitish']
            return copy.deepcopy(entry)
        raise AssertionError((method, path))


class AppReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='app-a-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.api = MemoryGitHub()
        self.trust, self.secret = test_identity()
        roots = patch.object(update_verifier, 'production_trust', return_value=self.trust)
        roots.start(); self.addCleanup(roots.stop)

    def publish(self, *args, **kwargs):
        return channel.publish(*args, signing_enabled=True, secret=self.secret, **kwargs)

    def signed(self, manifest):
        files = {name: (self.root / name).read_bytes() for name in manifest['assets']}
        return channel.strict_json(update_verifier._sign(manifest, files, self.secret, self.trust)[0])

    def candidate(self, version=None, previous=None, *, app=None):
        from tools.app_products import PW
        app = app or PW
        version = version or app.anchor[:-1] + '1'
        product = release(version=version, app=app)
        rows = [{'file': 'synthetic.py', 'mode': '100644', 'bytes': 1, 'sha256': '0' * 64}]
        inputs = {'format': 'picross-app-inputs-v1', 'sha256': channel.digest(payload.canonical(rows)), 'files': rows}
        planned = {'version': version, 'source_commit': self.api.source, 'run_id': 9, 'run_attempt': 1,
                   'payload_fingerprint': inputs['sha256'], 'diagnostic': False, 'authority': previous,
                   'trust_sha256': channel.digest(payload.canonical(self.trust))}
        raw = b'SYNTHETIC MSI; not an installation test'
        report = {'version': version, 'commit': self.api.source, 'payload_fingerprint': inputs['sha256'],
                  'product_code': product['product_code'], 'upgrade_code': product['upgrade_code'],
                  'msi_file': product['filename'], 'msi_bytes': len(raw), 'msi_sha256': channel.digest(raw)}
        files = {product['filename']: raw, product['filename'] + '.sha256':
                 (channel.digest(raw) + '  ' + product['filename'] + '\n').encode(),
                 'START.txt': b'Synthetic instructions', 'inputs.json': payload.canonical(inputs),
                 'delivery.json': payload.canonical(report)}
        for name, data in files.items():
            (self.root / name).write_bytes(data)
        inspection = {'commit': self.api.source, 'version': version, 'payload_fingerprint': inputs['sha256'],
                      'compared_to_build': True, 'msi_sha256': channel.digest(raw), 'msi_bytes': len(raw),
                      'format': 'picross-installer-inspection-v1', 'product_code': product['product_code'],
                      'upgrade_code': product['upgrade_code'], 'inventory_files': 10, 'license_files': 2,
                      'limits': 'Synthetic API regression; no installation.'}
        inspection_file = self.root / 'inspection.json'
        inspection_file.write_bytes(payload.canonical(inspection))
        manifest = channel.seal(self.root, inspection_file, planned, app=app)
        return planned, manifest

    def test_first_version_noop_and_monotone_continuation(self):
        self.assertEqual(channel.next_version({'sha256': 'x'}, None), '0.1.1')
        with patch.object(channel, 'release', return_value={'version': '0.1.20'}):
            with self.assertRaisesRegex(ValueError, 'start anchor'):
                channel.next_version({'sha256': 'x'}, None)
        planned, _ = self.candidate()
        self.publish(self.api, self.root, planned, enabled=True)
        previous = channel.authority(self.api)
        self.assertIsNone(channel.next_version({'sha256': planned['payload_fingerprint']}, previous))
        self.assertEqual(channel.next_version({'sha256': 'new'}, previous), '0.1.2')
        previous['manifest']['version'] = '0.1.65535'
        with self.assertRaisesRegex(ValueError, 'exhausted'):
            channel.next_version({'sha256': 'new'}, previous)

    def test_signed_publication_checks_catalog_before_draft_and_at_visibility(self):
        planned, _ = self.candidate()
        self.api.entries = [{'id': i + 1, 'tag_name': 'work-prod-' + str(i), 'assets': []}
                            for i in range(399)]
        with self.assertRaisesRegex(ValueError, 'terminating page'):
            self.publish(self.api, self.root, planned, enabled=True)
        self.assertEqual(self.api.writes, [])
        self.api.entries.pop()
        self.api.entries[0]['body'] = 'x' * (4 * 1024**2 - 64000)
        with self.assertRaisesRegex(ValueError, 'metadata page'):
            self.publish(self.api, self.root, planned, enabled=True)
        del self.api.entries[0]['body']
        self.publish(self.api, self.root, planned, enabled=True)
        self.assertEqual(len(self.api.entries), 399)
        self.assertEqual(channel.authority(self.api)['manifest']['version'], planned['version'])

    def test_work_then_three_signed_apps_remain_visible_to_installed_clients(self):
        from tools.app_products import PW, PE, PG, PRODUCTS
        from tools.production_workspace import update_client
        from unittest.mock import Mock
        self.api.entries = [{'tag_name': 'work-prod-' + str(i), 'id': i + 1, 'assets': [],
                             'prerelease': True, 'draft': False} for i in range(395)]
        channel.release_catalog.capacity(self.api.entries, 1, 'work-prod-new', 1, reserved_apps=len(PRODUCTS))
        self.api.entries.append(dict(self.api.entries[-1], tag_name='work-prod-new', id=396))
        for app in (PW, PE, PG):
            self.api.app = app
            self.trust, self.secret = test_identity(app=app)
            planned, _ = self.candidate(app=app)
            with patch.object(update_verifier, 'production_trust', return_value=self.trust):
                self.publish(self.api, self.root, planned, enabled=True, app=app)
        self.assertEqual(len(self.api.entries), 399)

        def page(url, limit, cancel, deadline):
            result = self.api.request(channel.PREFIX + '/releases?' + url.split('?')[1])
            raw = payload.canonical(result)
            self.assertLess(len(raw), limit)
            return raw

        transport = Mock(read=page)
        for before_removal in (True, False):
            if not before_removal:
                del self.api.entries[:396]
            for app, expected_id in ((PW, 397), (PE, 398)):
                row = update_client.latest_release(transport, None, 60, app=app)
                self.assertEqual(row['id'], expected_id)

    def test_pg_authority_requires_signed_correct_product_and_main_push(self):
        from tools.app_products import PE, PG, PW
        self.api.app = PG
        self.trust, self.secret = test_identity(app=PG)
        with patch.object(update_verifier, 'production_trust', return_value=self.trust):
            planned, provenance = self.candidate(app=PG)
            for app in (PW, PE):
                with self.assertRaises(ValueError):
                    channel.validate_manifest(provenance, app=app)
            self.api.run['event'] = 'pull_request'
            with self.assertRaisesRegex(ValueError, 'main pushes'):
                self.publish(self.api, self.root, planned, enabled=True, app=PG)
            self.assertEqual(self.api.writes, [])
            self.api.run['event'] = 'push'
            self.publish(self.api, self.root, planned, enabled=True, app=PG)
            previous = channel.authority(self.api, app=PG)
            self.assertEqual(previous['manifest']['format'], 'picross-pg-release-v2')
            self.assertIsNone(channel.next_version({'sha256': planned['payload_fingerprint']}, previous, app=PG))
            self.assertEqual(channel.next_version({'sha256': 'runtime-change'}, previous, app=PG), '0.1.2')
            self.assertIsNone(channel.authority(self.api, app=PE))

    def test_published_history_binding_is_specific_to_release_and_original_manifest(self):
        planned, manifest = self.candidate()
        self.publish(self.api, self.root, planned, enabled=True)
        entry = self.api.entries[0]
        signed = self.signed(manifest)
        identity = (entry['id'], channel.digest(payload.canonical(signed)))
        migrated = 'd' * 40
        self.api.tags[manifest['tag']] = migrated
        with patch.dict(channel.MIGRATED_RELEASE_TAGS, {identity: migrated}, clear=True):
            self.assertEqual(channel.release_files(self.api, entry), signed)
            with self.assertRaisesRegex(ValueError, 'Conflicting'):
                channel.verify_tag(self.api, signed, allow_missing=True)
            with self.assertRaisesRegex(ValueError, 'Conflicting'):
                channel.release_files(self.api, {**entry, 'draft': True})
            with patch.dict(channel.MIGRATED_RELEASE_TAGS, {(entry['id'], '0' * 64): migrated}, clear=True):
                with self.assertRaisesRegex(ValueError, 'Conflicting'):
                    channel.release_files(self.api, entry)
            with patch.dict(channel.MIGRATED_RELEASE_TAGS, {(entry['id'] + 1, identity[1]): migrated}, clear=True):
                with self.assertRaisesRegex(ValueError, 'Conflicting'):
                    channel.release_files(self.api, entry)
            self.api.tags[manifest['tag']] = 'e' * 40
            with self.assertRaisesRegex(ValueError, 'Conflicting'):
                channel.release_files(self.api, entry)

    def test_trust_gates_reject_pr_fork_dispatch_failed_and_nonmain(self):
        channel.trusted_run(self.api, 9, self.api.source)
        cases = [('event', 'pull_request'), ('event', 'workflow_dispatch'), ('conclusion', 'failure'),
                 ('conclusion', 'skipped'), ('status', 'in_progress'), ('head_branch', 'feature'),
                 ('head_sha', 'c' * 40), ('workflow_id', 99)]
        for key, value in cases:
            with self.subTest(key=key, value=value):
                before = self.api.run[key]; self.api.run[key] = value
                with self.assertRaises(ValueError):
                    channel.trusted_run(self.api, 9, 'a' * 40)
                self.api.run[key] = before
        self.api.run['head_repository']['id'] = 1
        with self.assertRaisesRegex(ValueError, 'Foreign'):
            channel.trusted_run(self.api, 9, 'a' * 40)
        self.assertEqual(self.api.writes, [])

    def test_missing_required_check_and_stale_main_fail(self):
        self.api.jobs[1]['conclusion'] = 'skipped'
        with self.assertRaisesRegex(ValueError, 'required check'):
            channel.trusted_run(self.api, 9, self.api.source)
        self.api.jobs[1]['conclusion'] = 'success'; self.api.source = 'b' * 40
        with self.assertRaisesRegex(ValueError, 'superseded'):
            channel.trusted_run(self.api, 9, 'a' * 40)

    def test_partial_upload_is_hidden_and_resumes_without_overwriting(self):
        planned, manifest = self.candidate()
        self.api.fail_upload = 'START.txt'
        with self.assertRaisesRegex(RuntimeError, 'lost upload'):
            self.publish(self.api, self.root, planned, enabled=True)
        self.assertTrue(self.api.entries[0]['draft'])
        self.assertIsNone(channel.authority(self.api))
        self.publish(self.api, self.root, planned, enabled=True)
        self.assertFalse(self.api.entries[0]['draft'])
        self.assertEqual(channel.authority(self.api)['manifest'], self.signed(manifest))
        self.assertEqual(len(self.api.blobs), 7)
        self.assertTrue(all(method in {'POST', 'PATCH'} for method, _ in self.api.writes))
        # A duplicate event is planned as a no-op; a stale pre-publication plan
        # cannot overwrite the already published same version.
        writes = list(self.api.writes)
        with self.assertRaisesRegex(ValueError, 'authority changed'):
            self.publish(self.api, self.root, planned, enabled=True)
        self.assertEqual(writes, self.api.writes)

    def test_same_version_conflicting_assets_or_tags_are_not_overwritten(self):
        planned, manifest = self.candidate()
        self.api.fail_upload = 'START.txt'
        with self.assertRaises(RuntimeError):
            self.publish(self.api, self.root, planned, enabled=True)
        self.api.blobs[1] = b'changed'
        writes = len(self.api.writes)
        with self.assertRaises(ValueError):
            self.publish(self.api, self.root, planned, enabled=True)
        self.assertEqual(len(self.api.writes), writes)
        self.api.tags[manifest['tag']] = 'c' * 40
        with self.assertRaisesRegex(ValueError, 'Conflicting PW release tag'):
            self.publish(self.api, self.root, planned, enabled=True)

    def test_activation_diagnostic_and_main_race_cannot_publish(self):
        planned, _ = self.candidate()
        with self.assertRaisesRegex(ValueError, 'gate is closed'):
            self.publish(self.api, self.root, planned, enabled=False)
        with self.assertRaisesRegex(ValueError, 'gate is closed'):
            self.publish(self.api, self.root, {**planned, 'diagnostic': True}, enabled=True)
        self.assertEqual(self.api.writes, [])
        self.api.change_main_after_upload = True
        with self.assertRaisesRegex(ValueError, 'superseded'):
            self.publish(self.api, self.root, planned, enabled=True)
        self.assertTrue(self.api.entries[0]['draft'])

    def test_wrong_msi_manifest_inventory_and_foreign_versions_fail_closed(self):
        planned, manifest = self.candidate()
        for name in manifest['assets']:
            files = {n: (self.root / n).read_bytes() for n in manifest['assets']}
            files[name] += b'corrupted'
            with self.subTest(name=name), self.assertRaises(ValueError):
                channel.verify_files(manifest, files)
        for version in ('0.1.0', '0.0.9', '1.0.0', '0.1.01'):
            with self.subTest(version=version), self.assertRaises(ValueError):
                channel.validate_manifest({**manifest, 'version': version, 'tag': 'pw-v' + version})
        with self.assertRaises(ValueError):
            channel.validate_manifest({**manifest, 'repository': 'foreign/repo'})
        with self.assertRaises(ValueError):
            channel.strict_json(b'{"version":1,"version":2}')

    def test_signing_activation_missing_secret_roots_and_main_environment_fail_before_writes(self):
        planned, _ = self.candidate()
        for enabled, signing in ((False, False), (False, True), (True, False)):
            with self.subTest(enabled=enabled, signing=signing), self.assertRaises(ValueError):
                channel.publish(self.api, self.root, planned, enabled=enabled, signing_enabled=signing, secret=self.secret)
        for secret in (None, 'malformed', test_identity()[1]):
            with self.subTest(secret_present=bool(secret)), self.assertRaises(ValueError):
                channel.publish(self.api, self.root, planned, enabled=True, signing_enabled=True, secret=secret)
        for trust in ({'format': 'picross-pw-trust-v1', 'accepted': {}, 'blocked': [], 'active_signer': None},
                      {**self.trust, 'blocked': [self.trust['active_signer']]}):
            with patch.object(update_verifier, 'production_trust', return_value=trust), self.assertRaises(ValueError):
                self.publish(self.api, self.root, planned, enabled=True)
        original = self.api.request
        for environment in (None, {'name': self.api.app.environment, 'deployment_branch_policy': None}):
            def request(path, **kwargs):
                return environment if path.endswith('/environments/pw-app-release') else original(path, **kwargs)
            with patch.object(self.api, 'request', side_effect=request), self.assertRaises(ValueError):
                self.publish(self.api, self.root, planned, enabled=True)
        with patch.object(self.api, 'pages', wraps=self.api.pages) as pages:
            original_pages = self.api.pages._mock_wraps
            pages.side_effect = lambda path, key=None: [{'name': '*', 'type': 'branch'}] if 'deployment-branch-policies' in path else original_pages(path, key)
            with self.assertRaisesRegex(ValueError, 'only the main'):
                self.publish(self.api, self.root, planned, enabled=True)
        self.assertEqual(self.api.writes, [])

    def test_signature_partial_upload_conflict_and_changed_trust_do_not_overwrite(self):
        planned, _ = self.candidate()
        self.api.fail_upload = update_verifier.SIGNATURE
        with self.assertRaises(RuntimeError):
            self.publish(self.api, self.root, planned, enabled=True)
        self.assertTrue(self.api.entries[0]['draft'])
        writes = list(self.api.writes)
        other, _ = test_identity()
        changed = {**self.trust, 'accepted': {**self.trust['accepted'], **other['accepted']}}
        with patch.object(update_verifier, 'production_trust', return_value=changed), self.assertRaisesRegex(ValueError, 'configuration changed'):
            self.publish(self.api, self.root, planned, enabled=True)
        signature_asset = next(a for a in self.api.entries[0]['assets'] if a['name'] == update_verifier.SIGNATURE)
        self.api.blobs[signature_asset['id']] += b'changed'
        with self.assertRaises(ValueError):
            self.publish(self.api, self.root, planned, enabled=True)
        self.assertEqual(self.api.writes, writes)

    def test_historical_v1_authority_remains_readable_but_cannot_authorize_installation(self):
        _, manifest = self.candidate()
        entry = {'id': 1, 'tag_name': manifest['tag'], 'target_commitish': manifest['source_commit'],
                 'draft': False, 'prerelease': False, 'assets': []}
        self.api.entries.append(entry)
        self.api.tags[manifest['tag']] = manifest['source_commit']
        for name in [*manifest['assets'], 'manifest.json']:
            raw = (self.root / name).read_bytes()
            identity = len(self.api.blobs) + 1; self.api.blobs[identity] = raw
            entry['assets'].append({'id': identity, 'name': name, 'state': 'uploaded',
                                    'size': len(raw), 'digest': 'sha256:' + channel.digest(raw)})
        self.assertEqual(channel.authority(self.api)['manifest'], manifest)
        self.assertEqual(channel.next_version({'sha256': 'changed'}, channel.authority(self.api)), '0.1.2')
        with self.assertRaisesRegex(ValueError, 'Legacy'):
            update_verifier.verify_candidate((self.root / 'manifest.json').read_bytes(), b'', {})
        # A corrupt published v2 authority cannot be skipped/reset to the anchor.
        raw, signed = update_verifier._sign(manifest, {name: (self.root / name).read_bytes() for name in manifest['assets']},
                                            self.secret, self.trust)
        manifest_asset = next(a for a in entry['assets'] if a['name'] == 'manifest.json')
        self.api.blobs[manifest_asset['id']] = raw
        manifest_asset.update(size=len(raw), digest='sha256:' + channel.digest(raw))
        with self.assertRaisesRegex(ValueError, 'Unexpected release assets'):
            channel.authority(self.api)  # Missing signature; no unsigned fallback.

    def test_real_inspector_rejects_wrong_portable_zip_hash_before_msi_access(self):
        planned, manifest = self.candidate()
        report = json.loads((self.root / 'delivery.json').read_bytes())
        report.update(zip_bytes=7, zip_sha256='0' * 64)
        (self.root / 'delivery.json').write_bytes(payload.canonical(report))
        (self.root / 'Picross-Start-windows-x64.zip').write_bytes(b'bad-zip')
        (self.root / 'input-audit.json').write_bytes(payload.canonical(
            {'fingerprint': planned['payload_fingerprint'], 'repository_inputs': ['synthetic.py']}))
        inputs = json.loads((self.root / 'inputs.json').read_bytes())
        with patch.object(verify_installer, 'fingerprint', return_value=inputs), \
                patch.object(verify_installer, 'msi_properties') as msi:
            with self.assertRaisesRegex(RuntimeError, 'ZIP byte mismatch'):
                verify_installer.verify(self.root, self.root / 'inspection-output', planned['source_commit'],
                                        compare_build=True, version=planned['version'])
            msi.assert_not_called()

    def test_authority_change_during_upload_leaves_draft_unpublished(self):
        planned, _ = self.candidate()
        original = channel.authority
        calls = []
        def changed(api, **kwargs):
            calls.append(1)
            return original(api) if len(calls) <= 2 else {'changed': True}
        with patch.object(channel, 'authority', side_effect=changed):
            with self.assertRaisesRegex(ValueError, 'authority changed'):
                self.publish(self.api, self.root, planned, enabled=True)
        self.assertTrue(self.api.entries[0]['draft'])

    def test_transient_get_is_retried_but_mutation_is_not(self):
        error = urllib.error.HTTPError('https://api.github.com', 503, 'synthetic', {}, None)
        response = MagicMock()
        response.__enter__.return_value.read.return_value = b'{"id":1}'
        opener = MagicMock()
        opener.open.side_effect = [error, response]
        with patch.object(channel.urllib.request, 'build_opener', return_value=opener), patch.object(channel.time, 'sleep'):
            self.assertEqual(channel.GitHub('synthetic').request(channel.PREFIX + '/releases/1'), {'id': 1})
            self.assertEqual(opener.open.call_count, 2)
            opener.open.side_effect = error
            with self.assertRaises(RuntimeError):
                channel.GitHub('synthetic').request(channel.PREFIX + '/releases', method='POST', value={})
            self.assertEqual(opener.open.call_count, 3)

    def test_committed_fingerprint_ignores_irrelevant_changes_and_includes_new_modules_modes(self):
        root = self.root
        def write(name, raw):
            path = root / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
        def commit():
            payload.git(root, 'add', '.')
            payload.git(root, '-c', 'user.name=synthetic', '-c', 'user.email=synthetic@example.invalid', 'commit', '-qm', 'synthetic')
        payload.git(root, 'init', '-q')
        source = Path(__file__).resolve().parents[1]
        methods = payload.pw_method_files(lambda name: (source / name).read_bytes())
        for name in sorted(methods):
            write(name, (source / name).read_bytes())
        write('tools/puzzle_production/reader.py', b'reader=1\n'); commit()
        first = payload.fingerprint(root)
        self.assertTrue(methods <= {row['file'] for row in first['files']})
        for name in ('tools/puzzle_production/za1_fixtures.py', 'tools/production_workspace/smoke_windows.py'):
            write(name, b'test-only fixture\n')
        commit()
        self.assertEqual(first, payload.fingerprint(root), 'Test-only code must not trigger an app update')
        for name in ('content/a.json', 'game/main.gd', 'docs/NOT-PACKAGED.md', 'tools/ci_modular.py',
                     'tools/work_ref_check.py'):
            write(name, b'irrelevant'); commit()
            self.assertEqual(first, payload.fingerprint(root))
        for name in ('tools/ci_growth.py', 'tools/publish_git.py', 'tools/work_publish.py',
                     'tools/puzzle_production/sd2_validation_0_4.json', 'tools/puzzle_production/sd2_rating_freeze.py'):
            with self.subTest(name=name):
                write(name, (source / name).read_bytes() + b'\n')
                self.assertEqual(first, payload.fingerprint(root), 'Working bytes must not define the fingerprint')
                commit()
                updated = payload.fingerprint(root)
                self.assertNotEqual(first['sha256'], updated['sha256'])
                first = updated
        write('tools/work_refs.py', b'CLEAN_MAIN = "anchor"\n'); commit()
        with_anchor = payload.fingerprint(root)
        self.assertNotEqual(first['sha256'], with_anchor['sha256'])
        self.assertIn('tools/work_refs.py', {row['file'] for row in with_anchor['files']})
        write('tools/puzzle_production/new_reader.py', b'new=1\n'); commit()
        second = payload.fingerprint(root)
        self.assertNotEqual(with_anchor['sha256'], second['sha256'])
        payload.git(root, 'update-index', '--chmod=+x', 'tools/puzzle_production/new_reader.py')
        payload.git(root, '-c', 'user.name=synthetic', '-c', 'user.email=synthetic@example.invalid', 'commit', '-qm', 'mode')
        self.assertNotEqual(second['sha256'], payload.fingerprint(root)['sha256'])
        blob = payload.git(root, 'rev-parse', 'HEAD:tools/puzzle_production/new_reader.py').decode().strip()
        payload.git(root, 'update-index', '--add', '--cacheinfo', '120000,' + blob + ',tools/puzzle_production/link.py')
        payload.git(root, '-c', 'user.name=synthetic', '-c', 'user.email=synthetic@example.invalid', 'commit', '-qm', 'link')
        with self.assertRaisesRegex(ValueError, 'Unsafe'):
            payload.fingerprint(root)

    def test_pw_payload_matches_input_bytes_and_reader_paths(self):
        from tools.puzzle_production import background_assets, background_render, image_normalization

        source = Path(__file__).resolve().parents[1]
        methods = payload.pw_method_files(lambda name: (source / name).read_bytes())
        images = set(background_assets._MODULES) | {
            payload.PRODUCTION + Path(module.__file__).name for module in (background_render, image_normalization)
        }
        self.assertEqual(payload.PW_IMAGE_SOURCES, images)
        self.assertEqual(sum(name.endswith('.py') for name in methods), 27)
        self.assertEqual(sum(name.endswith('.json') for name in methods), 8)
        files, hashes, rows = {}, {}, []
        for name in sorted(methods | images):
            raw = (source / name).read_bytes()
            file = self.root / '_internal' / name
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(raw)
            files[name] = file
            hashes[name] = channel.digest(raw)
            rows.append({'file': name, 'bytes': len(raw), 'sha256': hashes[name]})
        self.assertEqual(payload.verify_pw_reader_resources({'files': rows}, hashes, files),
                         {'method_resources': {name: hashes[name] for name in methods},
                          'image_resources': {name: hashes[name] for name in images}})
        for leaf in ('difficulty_calibration_0_3.json', 'image_normalization.py', 'background_render.py', 'background_io.py'):
            name = payload.PRODUCTION + leaf
            with self.subTest(resource=name):
                with self.assertRaisesRegex(ValueError, 'Incomplete'):
                    payload.verify_pw_reader_resources({'files': rows}, hashes,
                                                       {k: file for k, file in files.items() if k != name})
                with self.assertRaisesRegex(ValueError, 'Incomplete'):
                    payload.verify_pw_reader_resources({'files': rows}, {k: h for k, h in hashes.items() if k != name}, files)
                with self.assertRaisesRegex(ValueError, 'Unbound'):
                    payload.verify_pw_reader_resources({'files': rows}, {**hashes, name: '0' * 64}, files)
                original = files[name].read_bytes()
                files[name].write_bytes(original + b'\n')
                with self.assertRaisesRegex(ValueError, 'differs from committed input'):
                    payload.verify_pw_reader_resources({'files': rows}, hashes, files)
                files[name].write_bytes(original)

    def test_pe_frozen_excludes_pw_motifs_but_retains_strict_source_binding(self):
        # PROD-SLIM added a PW-only phase-label import to current_authoring.
        # PyInstaller discovers imports in functions even when PE never calls them.
        from tools.app_products import PE, PW
        from tools.production_workspace import build_windows
        self.assertIn('motifs', build_windows.PE_WORKSPACE_EXCLUDES)
        self.assertEqual(len(build_windows.PE_WORKSPACE_EXCLUDES),
                         len(set(build_windows.PE_WORKSPACE_EXCLUDES)))
        self.assertFalse(payload.selected('tools/production_workspace/motifs.py', app=PE))
        self.assertTrue(payload.selected('tools/production_workspace/motifs.py', app=PW))
        self.assertTrue(payload.selected('tools/puzzle_production/current_authoring.py', app=PE))
        self.assertTrue(payload.selected('tools/puzzle_production/editor_change.py', app=PE))
        self.assertFalse(set(build_windows.PE_WORKSPACE_EXCLUDES) &
                         {Path(name).stem for name in payload.PE_SHARED if name.endswith('.py')})

    def test_production_writers_excluded_from_frozen_apps_not_fingerprinted(self):
        from tools.app_products import PE, PG, PW
        from tools.production_workspace import build_windows
        expected = {
            'tools.production_git_workspace', 'tools.production_worktree_publish',
            'tools.publish_git', 'tools.work_publish', 'tools.production_remote',
            'tools.production_remote_pr', 'tools.production_remote_steps',
        }
        self.assertEqual(set(build_windows.PRODUCTION_WRITER_EXCLUDES), expected)
        for app in (PW, PE):
            with self.subTest(app=app.key):
                excluded = expected - payload.PW_WRITER_MODULES if app == PW else expected
                self.assertTrue(excluded <= set(build_windows.frozen_excludes(app)))
                if app == PW:
                    self.assertFalse(payload.PW_WRITER_MODULES & set(build_windows.frozen_excludes(app)))
                    for name in payload.PW_WRITER_MODULES:
                        self.assertTrue(payload.selected(name.replace('.', '/') + '.py', app=app))
                self.assertTrue(payload.selected('tools/work_refs.py', app=app))
                for name in excluded:
                    self.assertFalse(payload.selected(name.replace('.', '/') + '.py', app=app))
                    with self.assertRaisesRegex(RuntimeError, 'Produktionswriter'):
                        build_windows.verify_no_production_writers({name}, app)
                build_windows.verify_no_production_writers({'tools.work_refs'}, app)
        self.assertEqual(build_windows.frozen_excludes(PG), build_windows.FROZEN_EXCLUDES)

    def test_unknown_inputs_and_actual_collector_drift_are_errors(self):
        from tools.production_workspace import build_windows
        self.assertEqual(build_windows.FROZEN_EXCLUDES, ('tools.puzzle_production.za1_fixtures', 'tests'))
        self.assertFalse(payload.selected('tools/puzzle_production/za1_fixtures.py'))
        self.assertFalse(payload.selected('tests/puzzle_production/current_fixtures.py'))
        self.assertTrue(payload.selected('tools/puzzle_production/current_content.py'))
        with self.assertRaisesRegex(ValueError, 'Unclassified'):
            payload.selected('tools/puzzle_production/new-resource.bin')
        entry = self.root / 'tools/production_workspace/desktop_entry.py'
        entry.parent.mkdir(parents=True); entry.write_bytes(b'entry')
        row = {'file': 'tools/production_workspace/desktop_entry.py', 'sha256': channel.digest(b'entry')}
        toc = self.root / 'Analysis.toc'
        toc.write_text(repr([('entry', str(entry), 'PYSOURCE')]))
        result = payload.audit_analysis(self.root, toc, {'sha256': 'x', 'files': [row]}, [])
        self.assertEqual(result['repository_inputs'], [row['file']])
        entry.write_bytes(b'different working bytes')
        with self.assertRaisesRegex(ValueError, 'differs from committed input'):
            payload.audit_analysis(self.root, toc, {'sha256': 'x', 'files': [row]}, [])
        entry.write_bytes(b'entry')
        unknown = self.root / 'outside.py'; unknown.write_bytes(b'not fingerprinted')
        toc.write_text(repr([('entry', str(entry), 'PYSOURCE'), ('new', str(unknown), 'PYMODULE')]))
        with self.assertRaisesRegex(ValueError, 'absent'):
            payload.audit_analysis(self.root, toc, {'sha256': 'x', 'files': [row]}, [])
        # The exact failure observed in the real Windows PyInstaller Analysis.
        leaked = self.root / 'tests/puzzle_production/current_fixtures.py'
        leaked.parent.mkdir(parents=True); leaked.write_bytes(b'test-only')
        toc.write_text(repr([('entry', str(entry), 'PYSOURCE'), ('leaked', str(leaked), 'PYMODULE')]))
        with self.assertRaisesRegex(ValueError, 'Frozen input absent from fingerprint: tests/puzzle_production/current_fixtures.py'):
            payload.audit_analysis(self.root, toc, {'sha256': 'x', 'files': [row]}, [])


if __name__ == '__main__':
    unittest.main()
