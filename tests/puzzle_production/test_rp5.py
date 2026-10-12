"""RP-5 package selection, immutable originals and bounded ZIP extraction."""
from pathlib import Path
import tempfile
import unittest
import zipfile
from copy import deepcopy

from tools.puzzle_production.contract import InvalidInput
from tools.puzzle_production.images import file_hash
from tools.puzzle_production import rp5


class RP5Tests(unittest.TestCase):


    def test_archive_bytes_member_hashes_and_path_limits(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / 'test.zip'
            source = root / 'source'
            source.write_bytes(b'proof\n')
            with zipfile.ZipFile(archive, 'w') as z:
                z.write(source, 'trial/proof.json')
            metadata = {'format': 'picross-rp5-archive-v1', 'sha256': file_hash(archive), 'expanded_bytes': 6,
                        'files': {'trial/proof.json': file_hash(source)}}
            rp5.unpack_archive(archive, metadata, root / 'good')
            self.assertEqual((root / 'good/trial/proof.json').read_bytes(), b'proof\n')
            for field, value in (('sha256', '0'*64), ('expanded_bytes', 128*1024*1024+1), ('files', {'trial/proof.json': '0'*64})):
                m = deepcopy(metadata)
                m[field] = value
                with self.subTest(field=field), self.assertRaises(InvalidInput):
                    rp5.unpack_archive(archive, m, root / field)
            for i, name in enumerate(('../escape', '/absolute', 'a\\b', 'C:outside')):
                with zipfile.ZipFile(archive, 'w') as z:
                    z.writestr(name, b'proof\n')
                m = {**metadata, 'sha256': file_hash(archive), 'files': {name: file_hash(source)}}
                with self.subTest(name=name), self.assertRaises(InvalidInput):
                    rp5.unpack_archive(archive, m, root / f'bad-{i}')


if __name__ == '__main__':
    unittest.main()
