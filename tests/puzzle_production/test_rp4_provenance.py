"""Bind RP-4's preserved original commit bytes to its unchanged report."""
import hashlib
from pathlib import Path
import unittest

from tools.puzzle_production.contract import load_json


CORPUS = Path(__file__).resolve().parents[2] / 'examples' / 'rp4'


class ProducerProvenanceTests(unittest.TestCase):
    def test_original_commit_bytes_bind_the_report_and_published_tree(self):
        payload = (CORPUS / 'provenance' / 'producer-726e89d.commit').read_bytes()
        self.assertEqual(len(payload), 268)
        self.assertEqual(
            hashlib.sha256(payload).hexdigest(),
            '4e4b747ad959ee9c7c267c04e0f4ed60d35b692c8d00858e43bec1a27c8a2cac',
        )
        git_object = b'commit ' + str(len(payload)).encode('ascii') + b'\0' + payload
        original_commit = hashlib.sha1(git_object).hexdigest()
        self.assertEqual(original_commit, '726e89d573558a558c6b64f883c33331a26b8365')
        headers, _ = payload.split(b'\n\n', 1)
        self.assertEqual(headers.splitlines()[:2], [
            b'tree 80201bbde68240dd51f8583acdb103db4a791bbe',
            b'parent 37c97a6215a550a6e74fd2536a30c8ff13d9baba',
        ])
        report = CORPUS / 'baseline' / 'production.json'
        self.assertEqual(load_json(report)['producer_checkout'], original_commit)
        self.assertEqual(
            hashlib.sha256(report.read_bytes()).hexdigest(),
            '63568a23fe97f3465a419e46a4dbf202b4a252ac88c59f358a1a0269a9ac2d3e',
        )


if __name__ == '__main__':
    unittest.main()
