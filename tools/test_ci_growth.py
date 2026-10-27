"""Synthetic metadata checks; never read the production corpus."""
from io import BytesIO
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from ci_growth import compare, tree


def entry(size=10):
    return {'mode': '100644', 'oid': 'a'*40, 'bytes': size}


class GrowthTests(unittest.TestCase):
    def test_allowed_sources_rights_and_open_production_report_actual_growth(self):
        names = ['game/art/content/test.png', 'game/fonts/test.ttf', 'game/fonts/LICENSE.txt',
                 'docs/design/active-book/paper.png', 'docs/CI2_E_VERIFICATION.md',
                 'content/authoring/pz-synthetic/r02/package.zip', 'content/packages/pz-synthetic/r01/manifest.json']
        before = {'docs/evidence/hz-a/old.zip': entry(100), 'tools/code.py': entry(5)}
        after = {n: entry() for n in names} | {'tools/code.py': entry(7)}
        result = compare(before, after)
        self.assertEqual(result['delta'], {'files': 6, 'bytes': -28})
        self.assertEqual(result['added'], {'files': 7, 'bytes': 70})
        self.assertEqual(result['removed'], {'files': 1, 'bytes': 100})
        self.assertEqual(result['modified_files'], 1)

    def test_new_archives_outputs_galleries_and_rename_destinations_block(self):
        for path in ('docs/evidence/hz-a/new.png', 'docs/evidence/new-run/result.json',
                     'docs/design/at_b_integration/new.md', 'content/authoring/pz-test/at-b-r01/approval.json',
                     'docs/new.zip', 'docs/new.tar.gz', 'docs/design/new/captures/image.png',
                     'game/build/player.wasm', 'artifacts/run.json', 'misc/test.log',
                     'misc/__pycache__/test.pyc', 'content/authoring/pz-test/../archive.zip'):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'Disallowed'):
                compare({'old/name': entry()}, {path: entry()})
        # Existing active technical inputs stay usable; no suffix-only purge.
        self.assertEqual(compare({'docs/evidence/kk/native-crops.json': entry()},
                                 {'docs/evidence/kk/native-crops.json': entry(12)})['delta']['bytes'], 2)

    def test_api_metadata_requires_complete_bounded_trees_and_never_reads_blobs(self):
        value = {'truncated': False, 'tree': [{'type': 'tree', 'path': 'docs', 'mode': '040000', 'sha': 'b'*40},
                 {'type': 'blob', 'path': 'docs/a.md', 'mode': '100644', 'sha': 'a'*40, 'size': 12}]}
        with (patch('ci_growth.urllib.request.urlopen', return_value=BytesIO(json.dumps(value).encode())) as call,
              patch('ci_growth.subprocess.check_output', side_effect=AssertionError('blob access'))):
            self.assertEqual(tree('b'*40, repository='owner/repo')['docs/a.md']['bytes'], 12)
            self.assertEqual(call.call_args.args[0].full_url, 'https://api.github.com/repos/owner/repo/git/trees/'+'b'*40+'?recursive=1')
        for bad in ({**value, 'truncated': True}, {**value, 'tree': [dict(value['tree'][1], size=None)]}):
            with patch('ci_growth.urllib.request.urlopen', return_value=BytesIO(json.dumps(bad).encode())), self.assertRaises(ValueError):
                tree('b'*40, repository='owner/repo')

    def test_local_git_metadata_sizes_and_no_lazy_fetch(self):
        with tempfile.TemporaryDirectory() as directory:
            def git(*args): return subprocess.check_output(['git','-C',directory,*args], stderr=subprocess.DEVNULL).decode().strip()
            git('init', '-q'); Path(directory, 'file.txt').write_bytes(b'12345\n'); git('add', '.')
            git('-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','TEST ONLY')
            commit = git('rev-parse', 'HEAD')
            original = subprocess.check_output
            def run(args):
                self.assertEqual(args[:3], ['git','--no-lazy-fetch','ls-tree'])
                return original(args, cwd=directory)
            with patch('ci_growth.subprocess.check_output', side_effect=run):
                self.assertEqual(tree(commit)['file.txt']['bytes'], 6)
            with patch('ci_growth.subprocess.check_output', return_value=b'100644 blob '+b'a'*40+b' BAD\tfile\0'), self.assertRaises(ValueError):
                tree(commit)
