"""Negative delivery boundaries; actual engine/browser/SSH evidence is separate."""
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import MagicMock, patch
import zipfile

import build_web_player
import deploy_web
import web_bundle
from p1_product import player_extras


class Delivery(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.build = 'a'*40+'-player-20261015000000'
        prefix = 'releases/'+self.build+'/'
        html = f'<base href="./{prefix}"><body data-build="{self.build}">'.encode()
        files = {'index.html':html, prefix+'entry.html':html}
        files.update({prefix+n:b'contract test only' for n in ['index.js','index.wasm','index.pck','storage.js','SPIELANLEITUNG.md']})
        files.update({prefix+'licenses/'+n:b'contract test only' for n in web_bundle.LICENSES})
        for name, data in files.items():
            path = self.root/name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        self.manifest = dict(format=web_bundle.FORMAT, build_id=self.build, source_commit='a'*40,
            engine='4.7.2-stable', built_at='2026-10-15T00:00:00+00:00', kind='player', files=web_bundle.inventory(self.root))
        self.write_manifest()

    def write_manifest(self):
        (self.root/'build-manifest.json').write_text(json.dumps(self.manifest))

    def test_manifest_and_missing_corrupt_extra_files(self):
        web_bundle.validate(self.root)
        wasm = next(self.root.rglob('*.wasm'))
        wasm.write_bytes(b'changed')
        with self.assertRaises(ValueError): web_bundle.validate(self.root)
        wasm.unlink()
        with self.assertRaises(ValueError): web_bundle.validate(self.root)

    def test_nested_manifest_is_not_hidden(self):
        (self.root/'releases'/self.build/'build-manifest.json').write_text('{}')
        with self.assertRaises(ValueError): web_bundle.validate(self.root)

    def test_current_license_inputs_and_legacy_kb_boundary(self):
        source = Path(__file__).resolve().parents[1]
        licenses = {name.removeprefix('licenses/') for name in player_extras(source, self.root)
                    if name.startswith('licenses/')}
        self.assertEqual(licenses, web_bundle.LICENSES | web_bundle.ADDITIONAL_LICENSES)
        self.assertIn('KB-168-NOTICE.txt', licenses)
        # The pre-KB v1 fixture remains a valid rollback bundle.
        web_bundle.validate(self.root)
        notice = self.root/'releases'/self.build/'licenses/KB-168-NOTICE.txt'
        notice.write_bytes((source/'game/art/book/KB-168-NOTICE.txt').read_bytes())
        self.manifest['files'] = web_bundle.inventory(self.root)
        self.write_manifest()
        web_bundle.validate(self.root)
        notice.write_bytes(b'changed')
        with self.assertRaises(ValueError): web_bundle.validate(self.root)

    def test_injected_paths_hashes_and_schema(self):
        for update in ({'kind':'test'}, {'source_commit':'b'*40}, {'engine':'latest'}, {'built_at':'yesterday'}):
            candidate = {**self.manifest, **update}
            with self.assertRaises(ValueError): web_bundle.validate_manifest(candidate)
        for path in ('../outside', '/root', 'releases/x/../../bad', 'releases/x/evil;touch secret'):
            candidate = copy.deepcopy(self.manifest)
            candidate['files'][path] = dict(size=1,sha256='a'*64)
            with self.assertRaises(ValueError): web_bundle.validate_manifest(candidate)
        candidate = copy.deepcopy(self.manifest)
        candidate['files']['index.html']['sha256'] = 'a; command'
        with self.assertRaises(ValueError): web_bundle.validate_manifest(candidate)

    def test_local_config_boundaries(self):
        path = self.root/'config.json'
        good = dict(host='example-alias',root='/srv/www/example/picross-web',url='https://example.invalid/picross/')
        path.write_text(json.dumps(good)); deploy_web.config(path)
        for update in ({'root':'/'}, {'root':'/srv/../picross-web'}, {'root':'/srv//www/picross-web'},
                       {'host':'-oProxyCommand=evil'}, {'user':4}, {'port':True}, {'url':'https:///'},
                       {'url':'https://example.invalid/no-slash'}, {'url':'http://example.invalid/'}, {'secret':'x'}):
            path.write_text(json.dumps({**good, **update}))
            with self.assertRaises(ValueError): deploy_web.config(path)

    def test_missing_web_template_fails(self):
        archive = self.root/'templates.zip'
        with zipfile.ZipFile(archive,'w') as bundle:
            bundle.writestr('templates/version.txt','4.7.2.stable')
        with self.assertRaises(ValueError): build_web_player.extract_web_templates(archive,self.root/'templates')

    def test_connection_loss_reports_unknown_activation_and_retained_lock(self):
        remote = MagicMock()
        remote.locked = True
        remote.current.side_effect = ['', '', RuntimeError('connection lost')]
        remote.upload.side_effect = RuntimeError('upload interrupted')
        remote.release.side_effect = RuntimeError('connection lost')
        with patch.object(deploy_web,'Remote',return_value=remote):
            with self.assertRaisesRegex(RuntimeError,'active=unknown.*Lock cleanup not confirmed'):
                deploy_web.deploy({'url':'https://example.invalid/'}, self.root)

    def test_batch_line_break_rejected_before_remote_access(self):
        with patch.object(deploy_web,'Remote') as remote:
            with self.assertRaises(ValueError): deploy_web.deploy({},Path('unsafe\npath'))
            remote.assert_not_called()

    def test_ssh_stdin_preserves_posix_lf_on_windows(self):
        result = subprocess.CompletedProcess([],0,stdout=b'checked\n',stderr=b'')
        with patch.object(deploy_web.subprocess,'run',return_value=result) as command:
            self.assertEqual(deploy_web.Remote({'host':'example-alias'}).run('true\n'),'checked')
            self.assertEqual(command.call_args.kwargs['input'],b'set -eu\ntrue\n')
            self.assertFalse(command.call_args.kwargs.get('text',False))


if __name__ == '__main__':
    unittest.main()
