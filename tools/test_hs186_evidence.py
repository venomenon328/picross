"""Windows original-byte transport and exclusion of private probe profiles."""
import base64
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import hs186_evidence as evidence


class EvidenceTests(unittest.TestCase):
    def test_curated_zip_excludes_profiles_saves_and_reconstructs_original_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ('logs','hs186','hf149','technical','profile','hf149/isolated-saves'):
                (root/name).mkdir(parents=True,exist_ok=True)
            proof = dict(host='Windows-11',windows_hs=dict(status='success'),head='head',
                         base='base',checkout='merge',run='run',exports={},artifacts=[])
            (root/'hs-windows-proof.json').write_text(json.dumps(proof))
            for name in ('windows-proof.json','technical/product-report.json',
                         'hf149/hf-write.json','hf149/hf-read.json','hf149/hf-native.json',
                         'hf149/hf-acceptance.json'):
                (root/name).write_text('{}')
            (root/'hs186/original.png').write_bytes(bytes(range(256))*5000)
            (root/'profile/private.txt').write_text('DO NOT UPLOAD')
            (root/'hf149/isolated-saves/slot.json').write_text('DO NOT UPLOAD')
            target = root/'original.zip'
            manifest = evidence.package(root,target)
            with zipfile.ZipFile(target) as archive:
                self.assertNotIn('profile/private.txt',archive.namelist())
                self.assertNotIn('hf149/isolated-saves/slot.json',archive.namelist())
                self.assertEqual(archive.read('hs186/original.png'),bytes(range(256))*5000)
            with patch.object(evidence.subprocess,'run') as upload:
                upload.return_value.stdout = json.dumps(dict(id='id',history=[dict(version='rev')],html_url='https://gist.github.com/id')).encode()
                result = evidence.publish(target,manifest)
                sent = json.loads(upload.call_args.kwargs['input'])
            binding = json.loads(sent['files']['manifest.json']['content'])
            restored = b''.join(base64.b64decode(sent['files'][p['name']]['content'],validate=True)
                                for p in binding['parts'])
            self.assertEqual(restored,target.read_bytes())
            self.assertEqual(evidence.digest(restored),result['zip_sha256'])
            self.assertFalse(sent['public'])

    def test_publication_rejects_changed_original_zip(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)/'original.zip'
            target.write_bytes(b'changed')
            with patch.object(evidence.subprocess,'run') as upload:
                with self.assertRaisesRegex(ValueError,'Changed ZIP'):
                    evidence.publish(target,dict(sha256='different'))
                upload.assert_not_called()
