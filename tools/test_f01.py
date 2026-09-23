import copy
import json
import unittest

from check_f01 import DATA, placements, verify


class F01ProofTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((DATA / "f01.json").read_text(encoding="utf-8"))
        self.proof = json.loads((DATA / "f01-proof.json").read_text(encoding="utf-8"))

    def test_complete_certificate(self):
        self.assertGreater(verify(self.data, self.proof), 0)

    def test_forged_deduction_rejected(self):
        self.proof["steps"][0]["forced"][0][1] ^= 1
        with self.assertRaises(ValueError):
            verify(self.data, self.proof)

    def test_solution_not_used_for_deduction(self):
        changed = copy.deepcopy(self.data)
        changed["solution"][0][0] = 1
        with self.assertRaises(ValueError):
            verify(changed, self.proof)

    def test_line_enumeration_spacing(self):
        self.assertEqual(placements([1, 1], 3), [[1, 0, 1]])
        self.assertEqual(placements([], 3), [[0, 0, 0]])
        self.assertEqual(placements([3], 3), [[1, 1, 1]])
        self.assertEqual(placements([2, 2], 4), [])


if __name__ == "__main__":
    unittest.main()
