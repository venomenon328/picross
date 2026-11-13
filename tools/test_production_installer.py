"""P4-T01: inexpensive source/metadata guards, never build or install an MSI."""
import json
from pathlib import Path
import tempfile
import unittest
import subprocess
import os
import threading
import uuid
import copy
import urllib.error
import urllib.parse
from unittest.mock import patch, MagicMock
import xml.etree.ElementTree as ET

from tools.production_workspace import build_installer as installer
from tools.production_workspace.release import release, version_tuple, check_history
from tools.production_workspace import payload, release_channel as channel, verify_installer

ROOT = Path(__file__).resolve().parents[1]
NS = {'w': installer.NS}


class InstallerContractTests(unittest.TestCase):
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

    def test_source_history_refuses_decrease_or_upgrade_identity_change(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'release.json'
            product = release()
            source.write_text(json.dumps(product))
            for args in (('init', '-q'), ('add', '.'), ('-c', 'user.name=P4 test', '-c', 'user.email=p4@example.invalid', 'commit', '-qm', 'synthetic')):
                subprocess.run(['git', '-C', str(root), *args], check=True, stdout=subprocess.DEVNULL)
            with patch('tools.production_workspace.release.SOURCE', source):
                check_history(root, product)
                with self.assertRaisesRegex(ValueError, 'monoton'):
                    check_history(root, {**product, 'version': '0.0.1'})
                with self.assertRaisesRegex(ValueError, 'Upgradeidentität'):
                    check_history(root, {**product, 'upgrade_code': '11111111-1111-1111-1111-111111111111'})

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
    def __init__(self):
        self.source = 'a' * 40
        repo = {'id': channel.REPOSITORY_ID, 'full_name': channel.REPOSITORY}
        self.run = {'workflow_id': 8, 'path': '.github/workflows/ci-modular.yml', 'name': 'Package CI',
                    'event': 'push', 'head_branch': 'main', 'head_sha': self.source, 'status': 'completed',
                    'conclusion': 'success', 'repository': repo, 'head_repository': copy.deepcopy(repo), 'run_attempt': 1}
        self.jobs = [{'name': n, 'status': 'completed', 'conclusion': 'success'} for n in ('docs', 'ci-required')]
        self.entries, self.blobs, self.tags, self.writes = [], {}, {}, []
        self.fail_upload = None
        self.change_main_after_upload = False

    def request(self, path, *, method='GET', value=None, raw=None, binary=False, upload=False):
        path = path.removeprefix(channel.PREFIX)
        parts = urllib.parse.urlsplit(path)
        route = parts.path
        query = urllib.parse.parse_qs(parts.query)
        if method != 'GET':
            self.writes.append((method, route))
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
                return copy.deepcopy(self.entries) if query.get('page', ['1']) == ['1'] else []
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

    def candidate(self, version='0.1.1', previous=None):
        product = release(version=version)
        rows = [{'file': 'synthetic.py', 'mode': '100644', 'bytes': 1, 'sha256': '0' * 64}]
        inputs = {'format': 'picross-app-inputs-v1', 'sha256': channel.digest(payload.canonical(rows)), 'files': rows}
        planned = {'version': version, 'source_commit': self.api.source, 'run_id': 9, 'run_attempt': 1,
                   'payload_fingerprint': inputs['sha256'], 'diagnostic': False, 'authority': previous}
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
        manifest = channel.seal(self.root, inspection_file, planned)
        return planned, manifest

    def test_first_version_noop_and_monotone_continuation(self):
        self.assertEqual(channel.next_version({'sha256': 'x'}, None), '0.1.1')
        with patch.object(channel, 'release', return_value={'version': '0.1.20'}):
            with self.assertRaisesRegex(ValueError, 'start anchor'):
                channel.next_version({'sha256': 'x'}, None)
        planned, _ = self.candidate()
        channel.publish(self.api, self.root, planned, enabled=True)
        previous = channel.authority(self.api)
        self.assertIsNone(channel.next_version({'sha256': planned['payload_fingerprint']}, previous))
        self.assertEqual(channel.next_version({'sha256': 'new'}, previous), '0.1.2')
        previous['manifest']['version'] = '0.1.65535'
        with self.assertRaisesRegex(ValueError, 'exhausted'):
            channel.next_version({'sha256': 'new'}, previous)

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
            channel.publish(self.api, self.root, planned, enabled=True)
        self.assertTrue(self.api.entries[0]['draft'])
        self.assertIsNone(channel.authority(self.api))
        channel.publish(self.api, self.root, planned, enabled=True)
        self.assertFalse(self.api.entries[0]['draft'])
        self.assertEqual(channel.authority(self.api)['manifest'], manifest)
        self.assertEqual(len(self.api.blobs), 6)
        self.assertTrue(all(method in {'POST', 'PATCH'} for method, _ in self.api.writes))
        # A duplicate event is planned as a no-op; a stale pre-publication plan
        # cannot overwrite the already published same version.
        writes = list(self.api.writes)
        with self.assertRaisesRegex(ValueError, 'authority changed'):
            channel.publish(self.api, self.root, planned, enabled=True)
        self.assertEqual(writes, self.api.writes)

    def test_same_version_conflicting_assets_or_tags_are_not_overwritten(self):
        planned, manifest = self.candidate()
        self.api.fail_upload = 'START.txt'
        with self.assertRaises(RuntimeError):
            channel.publish(self.api, self.root, planned, enabled=True)
        self.api.blobs[1] = b'changed'
        writes = len(self.api.writes)
        with self.assertRaises(ValueError):
            channel.publish(self.api, self.root, planned, enabled=True)
        self.assertEqual(len(self.api.writes), writes)
        self.api.tags[manifest['tag']] = 'c' * 40
        with self.assertRaisesRegex(ValueError, 'Conflicting PW release tag'):
            channel.publish(self.api, self.root, planned, enabled=True)

    def test_activation_diagnostic_and_main_race_cannot_publish(self):
        planned, _ = self.candidate()
        with self.assertRaisesRegex(ValueError, 'gate is closed'):
            channel.publish(self.api, self.root, planned, enabled=False)
        with self.assertRaisesRegex(ValueError, 'gate is closed'):
            channel.publish(self.api, self.root, {**planned, 'diagnostic': True}, enabled=True)
        self.assertEqual(self.api.writes, [])
        self.api.change_main_after_upload = True
        with self.assertRaisesRegex(ValueError, 'superseded'):
            channel.publish(self.api, self.root, planned, enabled=True)
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
        def changed(api):
            calls.append(1)
            return original(api) if len(calls) == 1 else {'changed': True}
        with patch.object(channel, 'authority', side_effect=changed):
            with self.assertRaisesRegex(ValueError, 'authority changed'):
                channel.publish(self.api, self.root, planned, enabled=True)
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
        write('tools/puzzle_production/reader.py', b'reader=1\n'); commit()
        first = payload.fingerprint(root)
        for name in ('content/a.json', 'game/main.gd', 'docs/NOT-PACKAGED.md', 'tools/ci_modular.py'):
            write(name, b'irrelevant'); commit()
            self.assertEqual(first, payload.fingerprint(root))
        write('tools/puzzle_production/new_reader.py', b'new=1\n'); commit()
        second = payload.fingerprint(root)
        self.assertNotEqual(first['sha256'], second['sha256'])
        payload.git(root, 'update-index', '--chmod=+x', 'tools/puzzle_production/new_reader.py')
        payload.git(root, '-c', 'user.name=synthetic', '-c', 'user.email=synthetic@example.invalid', 'commit', '-qm', 'mode')
        self.assertNotEqual(second['sha256'], payload.fingerprint(root)['sha256'])
        blob = payload.git(root, 'rev-parse', 'HEAD:tools/puzzle_production/new_reader.py').decode().strip()
        payload.git(root, 'update-index', '--add', '--cacheinfo', '120000,' + blob + ',tools/puzzle_production/link.py')
        payload.git(root, '-c', 'user.name=synthetic', '-c', 'user.email=synthetic@example.invalid', 'commit', '-qm', 'link')
        with self.assertRaisesRegex(ValueError, 'Unsafe'):
            payload.fingerprint(root)

    def test_unknown_inputs_and_actual_collector_drift_are_errors(self):
        with self.assertRaisesRegex(ValueError, 'Unclassified'):
            payload.selected('tools/puzzle_production/new-resource.bin')
        entry = self.root / 'tools/production_workspace/desktop_entry.py'
        entry.parent.mkdir(parents=True); entry.write_bytes(b'entry')
        row = {'file': 'tools/production_workspace/desktop_entry.py', 'sha256': channel.digest(b'entry')}
        toc = self.root / 'Analysis.toc'
        toc.write_text(repr([('entry', str(entry), 'PYSOURCE')]))
        result = payload.audit_analysis(self.root, toc, {'sha256': 'x', 'files': [row]}, [])
        self.assertEqual(result['repository_inputs'], [row['file']])
        unknown = self.root / 'outside.py'; unknown.write_bytes(b'not fingerprinted')
        toc.write_text(repr([('entry', str(entry), 'PYSOURCE'), ('new', str(unknown), 'PYMODULE')]))
        with self.assertRaisesRegex(ValueError, 'absent'):
            payload.audit_analysis(self.root, toc, {'sha256': 'x', 'files': [row]}, [])


if __name__ == '__main__':
    unittest.main()
