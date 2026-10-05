"""RP-5 package selection, immutable originals and bounded ZIP extraction."""
from pathlib import Path
import tempfile
import unittest
import zipfile
from copy import deepcopy

from tools.puzzle_production.contract import InvalidInput, load_json
from tools.puzzle_production.images import file_hash
from tools.puzzle_production import rp5


class RP5Tests(unittest.TestCase):
    def test_fixed_nine_plans_have_colored_and_empty_protection(self):
        lock, plans = rp5.plans()
        self.assertEqual(len(plans), 9)
        self.assertEqual({rp5.load_json(rp5.RP4 / 'baseline' / t['trial'] / f"{t['variant']}-candidate.json")['design']['mode']
                          for t, p in plans}, {'mono', 'color'})
        for t, p in plans:
            self.assertGreater(t['protected_empty_cells'], 0)
            self.assertGreater(t['protected_cells'], t['protected_empty_cells'])
            self.assertEqual((p['config']['max_candidates'], p['config']['max_steps'], p['config']['seed']), (16, 96, 39))

    def test_original_48_rows_preserved_in_comparison(self):
        report = load_json(rp5.RP5 / 'comparison.json')
        repairs = {r['trial']: r['repair'] for r in report['rows'] if r['selected_for_repair']}
        rebuilt = rp5.comparison(repairs)
        self.assertEqual(report['rows'], rebuilt['rows'])
        self.assertEqual((len(rebuilt['rows']), rebuilt['selected'], rebuilt['not_selected']), (48, 9, 39))
        self.assertEqual(sum(r['original']['certified'] for r in rebuilt['rows']), 19)
        self.assertEqual(sum(r['original']['certified'] and r['original_motif']['motif_usable_for_comparison'] for r in rebuilt['rows']), 14)

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
