"""Generic import-result integrity with a synthetic 2x2 image."""
from pathlib import Path
import tempfile
import unittest

from PIL import Image

from tools.puzzle_production.contract import InvalidInput, load_json, write_json
from tools.puzzle_production.images import file_hash, import_image, validate_design
from tools.puzzle_production.rp4 import inspect_trial


class ResultTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.policy = {'solver_seconds': 30, 'verifier_seconds': 30, 'max_lines': 100000}

    def bundle(self, stalled=False):
        im = Image.new('RGB', (2, 2), 'white')
        im.putpixel((0, 0), (0, 0, 0))
        if stalled:
            im.putpixel((1, 1), (0, 0, 0))
        im.save(self.root / 'source.png')
        design = load_json(Path(__file__).parent / 'fixtures/image-design.json')
        design.update(width=2, height=2, crop=[0, 0, 2, 2], variants=design['variants'][:1])
        design = validate_design(design)
        write_json(self.root / 'design.json', design)
        self.path = self.root / 'bundle'
        import_image(self.root / 'source.png', self.root / 'design.json', self.path, seconds=30)
        self.trial = {'id': 'unit', 'input': 'source.png', 'design': design}
        self.record = {'status': 'produced', 'manifest_sha256': file_hash(self.path / 'manifest.json'),
                       'candidates': load_json(self.path / 'manifest.json')['candidates']}

    def rebind_result(self, result):
        name = 'area-128-result.json'
        write_json(self.path / name, result)
        manifest = load_json(self.path / 'manifest.json')
        manifest['files'][name] = file_hash(self.path / name)
        manifest['candidates'][0]['technical'] = result
        write_json(self.path / 'manifest.json', manifest)
        self.record['manifest_sha256'] = file_hash(self.path / 'manifest.json')
        self.record['candidates'] = manifest['candidates']

    def inspect(self):
        return inspect_trial(self.root, self.path, self.trial, self.record, self.policy)[0]

    def test_actual_solved_proof_and_matrix_are_accepted(self):
        self.bundle()
        self.assertTrue(self.inspect()['logically_accepted'])

    def test_stalled_does_not_become_a_certified_puzzle(self):
        self.bundle(stalled=True)
        result = self.inspect()
        self.assertFalse(result['logically_accepted'])
        self.assertEqual(result['fresh']['status'], 'stalled')

    def test_forged_certification_rejected_even_after_all_file_rebindings(self):
        self.bundle(stalled=True)
        result = load_json(self.path / 'area-128-result.json')
        result.update(status='solved', certified=True)
        self.rebind_result(result)
        with self.assertRaisesRegex(InvalidInput, 'differs from proof replay'):
            self.inspect()

    def test_successful_replay_does_not_overwrite_original_verification_abort(self):
        self.bundle()
        self.rebind_result({'status': 'aborted', 'certified': False, 'proof_verified': False,
                            'reason': 'time_limit', 'elapsed_seconds': 30.0})
        result = self.inspect()
        self.assertTrue(result['fresh']['certified'])
        self.assertFalse(result['logically_accepted'])
        self.assertEqual(result['original']['status'], 'aborted')

    def test_wrong_source_and_unequal_budget_rejected(self):
        self.bundle()
        Image.new('RGB', (2, 2), 'black').save(self.root / 'other.png')
        self.trial['input'] = 'other.png'
        with self.assertRaisesRegex(InvalidInput, 'Wrong source'):
            self.inspect()
        self.trial['input'] = 'source.png'
        self.policy['solver_seconds'] = 31
        with self.assertRaisesRegex(InvalidInput, 'budgets'):
            self.inspect()


if __name__ == '__main__':
    unittest.main()
