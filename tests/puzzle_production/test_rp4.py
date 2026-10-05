"""RP-4 coverage, pairing and result-integrity regressions."""
import copy
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

from PIL import Image

from tools.puzzle_production.contract import InvalidInput, load_json, write_json
from tools.puzzle_production.images import file_hash, import_image, validate_design
from tools.puzzle_production.rp4 import CORPUS, check_reviews, inspect_trial, local, validate_inputs


class CorpusTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'corpus'
        shutil.copytree(CORPUS, self.root, ignore=shutil.ignore_patterns('baseline', 'views', '__pycache__'))

    def test_complete_paired_input_and_icc_reference_reconstruction(self):
        plan, lock = validate_inputs(self.root)
        self.assertEqual(len(plan['sources']), 12)
        self.assertEqual(len(lock['trials']), 24)
        self.assertEqual(sum(len(t['design']['variants']) for t in lock['trials']), 48)
        self.assertEqual(len({t['source_id'] for t in lock['trials'] if t['design']['width'] == t['design']['height'] == 100}), 4)

    def test_missing_duplicate_or_wrong_class_sources_rejected(self):
        original = load_json(self.root / 'plan.json')
        for change in ('missing', 'duplicate', 'class'):
            plan = copy.deepcopy(original)
            if change == 'missing':
                plan['sources'].pop()
            elif change == 'duplicate':
                plan['sources'][-1] = plan['sources'][-2]
            else:
                plan['sources'][-1]['class'] = 'illustration'
            write_json(self.root / 'plan.json', plan)
            with self.assertRaises(InvalidInput):
                validate_inputs(self.root)

    def test_removed_pair_or_changed_palette_rejected(self):
        original = load_json(self.root / 'inputs.json')
        for change in ('missing', 'palette', 'dimensions', 'duplicate'):
            lock = copy.deepcopy(original)
            if change == 'missing':
                lock['trials'].pop()
            elif change == 'palette':
                lock['trials'][-1]['design']['palette'][0]['rgb'] = '#000001'
            elif change == 'dimensions':
                lock['trials'][-1]['design']['width'] = 99
            else:
                lock['trials'][-1] = lock['trials'][-2]
            write_json(self.root / 'inputs.json', lock)
            with self.assertRaisesRegex(InvalidInput, 'paired trial'):
                validate_inputs(self.root)

    def test_prompt_change_is_not_hidden_by_unchanged_images(self):
        (self.root / 'briefings/p01-stylized.txt').write_text('different prompt\n')
        with self.assertRaisesRegex(InvalidInput, 'input bindings'):
            validate_inputs(self.root)

    def test_reference_pixel_change_and_missing_image_rejected(self):
        p = self.root / 'references/p01.png'
        with Image.open(p) as im:
            im.putpixel((0, 0), (255, 0, 0))
            im.save(p)
        with self.assertRaisesRegex(InvalidInput, 'Style reference'):
            validate_inputs(self.root)
        (self.root / 'stylized/p01.png').unlink()
        with self.assertRaises(InvalidInput):
            validate_inputs(self.root)

    def test_paths_do_not_escape_corpus(self):
        for path in ('../other.png', '/etc/passwd', 'sources\\other.png'):
            with self.assertRaises(InvalidInput):
                local(self.root, path)

    def test_original_illustrations_reproduce_without_solver(self):
        spec = importlib.util.spec_from_file_location('rp4_illustrations', CORPUS / 'create_illustrations.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        output = Path(self.temp.name) / 'illustrations'
        module.create(output)
        self.assertEqual(len(list(output.iterdir())), 3)
        for path in output.iterdir():
            self.assertEqual(file_hash(path), file_hash(CORPUS / 'sources' / path.name))
        invalid = Path(self.temp.name) / 'not-directory'
        invalid.write_text('existing file')
        with self.assertRaises(OSError):
            module.create(invalid)

    def test_missing_visual_judgment_is_an_open_evidence_gap(self):
        lock = load_json(self.root / 'inputs.json')
        reviews = load_json(self.root / 'reviews.json')
        reviews.pop(next(iter(reviews)))
        write_json(self.root / 'reviews.json', reviews)
        with self.assertRaisesRegex(InvalidInput, 'visual review coverage'):
            check_reviews(self.root, lock, [])


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
        design = load_json(CORPUS / 'designs/i01-direct-40x40.json')
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
