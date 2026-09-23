import copy
import json
import unittest
from check_f02 import DATA, placements, derive, verify


class ColoredCertificateTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((DATA / 'f02.json').read_text())
        self.proof = json.loads((DATA / 'f02-proof.json').read_text())

    def test_complete_certificate(self):
        self.assertEqual(verify(self.data, self.proof), 80)

    def test_color_spacing(self):
        self.assertEqual(placements(((1, 1), (1, 1)), 3), ((1, 0, 1),))
        self.assertEqual(placements(((1, 1), (1, 2)), 2), ((1, 2),))
        self.assertIn((1, 0, 2), placements(((1, 1), (1, 2)), 3))
        self.assertEqual(placements((), 2), ((0, 0),))
        self.assertEqual(placements(((2, 4),), 2), ((4, 4),))

    def test_solution_independent_deductions(self):
        forged = copy.deepcopy(self.data)
        forged['solution'][1][1] = 1
        self.assertEqual(derive(forged), derive(self.data))
        with self.assertRaises(ValueError):
            verify(forged, self.proof)

    def test_forged_certificate(self):
        self.proof['steps'][1]['forced'][0][1] = 7
        with self.assertRaises(ValueError):
            verify(self.data, self.proof)

    def test_wrong_revision(self):
        self.data['revision'] += 1
        with self.assertRaises(ValueError):
            verify(self.data, self.proof)
