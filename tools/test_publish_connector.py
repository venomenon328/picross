import base64
import copy
import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools import publish_connector as publisher


BRANCH = 'fix/824-test'
FOREIGN = 'e' * 40


def ref(branch, sha):
    return {'ref': f'refs/heads/{branch}', 'url': f'{publisher.API}/refs/heads/{branch}',
            'object': {'type': 'commit', 'sha': sha, 'url': f'{publisher.API}/commits/{sha}'}}


class ConnectorPublicationTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.git('init', '-q')
        self.git('config', 'user.name', 'Connector Test')
        self.git('config', 'user.email', 'connector@example.invalid')
        self.git('config', 'commit.gpgsign', 'false')
        self.git('config', 'core.autocrlf', 'false')
        (self.root / 'old.txt').write_bytes(b'old')
        (self.root / 'keep.txt').write_bytes(b'keep')
        self.base = self.commit('base')
        self.observation = {'main': ref('main', self.base), 'branch_refs': []}

    def git(self, *args):
        return publisher.git(self.root, *args).decode().strip()

    def commit(self, message, *, stage=True):
        if stage:
            self.git('add', '-A')
        self.git('commit', '-qm', message)
        return self.git('rev-parse', 'HEAD')

    def prepare(self, head, observation=None, *, branch=BRANCH):
        return publisher.prepare(self.root, branch, head, observation or self.observation, anchor=self.base)

    def changes(self):
        self.git('mv', 'old.txt', 'new.txt')
        (self.root / 'keep.txt').write_bytes(b'\x00\xff\r\n')
        (self.root / 'same.bin').write_bytes(b'\x00\xff\r\n')
        self.git('add', '-A')
        self.git('update-index', '--chmod=+x', 'new.txt')
        return self.commit('planned change\n\nfull body', stage=False)

    def evidence(self, plan):
        return {**copy.deepcopy(self.observation), 'created_commit_sha': FOREIGN,
                'blobs': {sha: sha for sha in plan['blobs']}, 'tree_sha': plan['commit']['tree_sha'],
                'commit': {'sha': FOREIGN, 'url': f'{publisher.API}/commits/{FOREIGN}',
                           'tree': {'sha': plan['commit']['tree_sha']},
                           'parents': [{'sha': self.base}], 'message': plan['commit']['message']}}

    def authorize(self, head, evidence):
        return publisher.authorize_ref(self.root, BRANCH, head, self.base, evidence, anchor=self.base)

    def test_plan_uses_complete_committed_bytes_paths_modes_and_tree(self):
        head = self.changes()
        (self.root / 'keep.txt').write_bytes(b'uncommitted edit')
        plan = self.prepare(head)
        entries = {row['path']: row for row in plan['tree']['tree_elements']}
        self.assertEqual(set(entries), {'old.txt', 'new.txt', 'keep.txt', 'same.bin'})
        self.assertIsNone(entries['old.txt']['sha'])
        self.assertEqual(entries['new.txt']['mode'], '100755')
        binary = entries['keep.txt']['sha']
        self.assertEqual(binary, entries['same.bin']['sha'])
        self.assertEqual(len(plan['blobs']), 2)
        raw = base64.b64decode(plan['blobs'][binary]['content'])
        self.assertEqual(raw, b'\x00\xff\r\n')
        self.assertEqual(hashlib.sha1(b'blob 4\x00' + raw).hexdigest(), binary)
        self.assertEqual(plan['tree']['base_tree_sha'], self.git('rev-parse', self.base + '^{tree}'))
        self.assertEqual(plan['commit']['tree_sha'], self.git('rev-parse', head + '^{tree}'))
        self.assertEqual(plan['commit']['parent_sha'], self.base)

    def test_blocks_transient_outputs_uninspected_history_and_partial_clone(self):
        (self.root / 'review-originals').mkdir()
        review = self.root / 'review-originals' / 'review.png'
        review.write_bytes(b'original')
        self.commit('forbidden')
        review.unlink()
        (self.root / 'keep.txt').write_bytes(b'next')
        transient = self.commit('remove forbidden')
        with self.assertRaisesRegex(ValueError, 'review delivery'):
            self.prepare(transient)
        self.git('reset', '--hard', self.base)
        first = self.changes()
        (self.root / 'keep.txt').write_bytes(b'next')
        second = self.commit('second clean commit')
        with self.assertRaisesRegex(ValueError, 'one commit directly'):
            self.prepare(second)
        shallow = Path(self.enterContext(tempfile.TemporaryDirectory()))
        subprocess.run(['git', 'clone', '-q', '--depth=1', self.root.as_uri(), str(shallow)], check=True)
        with self.assertRaisesRegex(ValueError, 'Complete Git history'):
            publisher.prepare(shallow, BRANCH, second, self.observation, anchor=self.base)
        self.git('config', 'remote.origin.promisor', 'true')
        with self.assertRaisesRegex(ValueError, 'Full object database'):
            self.prepare(first)

    def test_ref_and_candidate_bindings_fail_closed(self):
        head = self.changes()
        plan = self.prepare(head)
        good = self.evidence(plan)
        altered = {
            'main': ref('main', FOREIGN),
            'branch_refs': [ref(BRANCH, FOREIGN)],
            'blobs': {},
            'tree_sha': FOREIGN,
            'created_commit_sha': '0' * 40,
        }
        for key, value in altered.items():
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.authorize(head, {**good, key: value})
        for key, value in {'sha': self.base, 'parents': [{'sha': FOREIGN}],
                           'tree': {'sha': FOREIGN}, 'message': 'another commit',
                           'url': 'https://api.github.com/repos/other/repo/git/commits/' + FOREIGN}.items():
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.authorize(head, {**good, 'commit': {**good['commit'], key: value}})
        for branch in ('main', 'content/pw/pz-example'):
            with self.subTest(branch=branch), self.assertRaisesRegex(ValueError, 'owned development'):
                self.prepare(head, branch=branch)
        with self.assertRaisesRegex(ValueError, 'already exists'):
            self.prepare(head, {**self.observation, 'branch_refs': [ref(BRANCH + '/child', FOREIGN)]})

    def test_readback_requires_exact_authorized_branch_and_commit(self):
        head = self.changes()
        request = self.authorize(head, self.evidence(self.prepare(head)))
        self.assertEqual(request, {'repository_full_name': publisher.REPOSITORY,
                                   'branch_name': BRANCH, 'sha': FOREIGN})
        self.assertEqual(publisher.verify_ref(request, ref(BRANCH, FOREIGN)), FOREIGN)
        with self.assertRaisesRegex(ValueError, 'not confirmed'):
            publisher.verify_ref(request, ref(BRANCH, self.base))
        with self.assertRaisesRegex(ValueError, 'branch binding'):
            publisher.verify_ref(request, ref('fix/someone-else', FOREIGN))
        with self.assertRaisesRegex(ValueError, 'repository'):
            publisher.verify_ref({**request, 'repository_full_name': 'other/repo'}, ref(BRANCH, FOREIGN))


if __name__ == '__main__':
    unittest.main()
