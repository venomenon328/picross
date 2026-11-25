"""Offline originals for precise PR, Git, release and CI binding."""
from base64 import b64encode
from copy import deepcopy
from hashlib import sha1, sha256
import unittest

from tools import production_remote_reader as reader


REPO = 'venomenon328/picross-remote-test'
JOB = 'pz-fixture'
MAIN, INPUT, WORK, HEAD, MERGE, REQUEST, TAG = (c*40 for c in 'abcdef1')


def observation():
    repo = dict(full_name=REPO, id=reader.REPOSITORIES[REPO], default_branch='main')
    plan = '.ci/package.json'
    registries = {'content/registry.json', 'game/data/registry.json'}
    background = f'content/backgrounds/{JOB}.json'
    definition = f'game/data/content/{JOB}.json'
    record_path = f'content/authoring/{JOB}/current/record.json'
    generation = {'id': 127, 'anchor': TAG}

    def ref(name, oid):
        return {'ref': 'refs/' + name, 'object': {'type': 'commit', 'sha': oid}}

    def record(value, commit):
        raw = (reader.canonical(value) + '\n').encode()
        return {'type': 'file', 'path': record_path, 'encoding': 'base64', 'content': b64encode(raw).decode(),
                'size': len(raw), 'sha': sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest(),
                'url': f'https://api.github.com/repos/{REPO}/contents/{record_path}?ref={commit}'}, sha256(raw).hexdigest()

    prior = {'puzzle_id': JOB, 'state': 'editorially_approved', 'work_release': generation}
    input_record, checksum = record(prior, INPUT)
    complete, _ = record(dict(prior, state='registered', integration={'commit': HEAD,
        'result': {'files': {definition: {'file': definition}}}}), WORK)
    req = dict(format='pw-remote-v2', repository=REPO, job=JOB, operation='step5', expected=INPUT,
               record_sha256=checksum, tools=MAIN, main=MAIN, issue=None, input={'background': None, 'decisions': []})
    request_id = reader.digest(req)
    marker = '\n\nPW-Remote: ' + request_id
    branch = reader.product_branch(JOB)
    tree = {'sha': '9'*40}
    pr = {'number': 3, 'state': 'open', 'draft': True, 'mergeable': True,
          'head': {'repo': repo, 'ref': branch, 'sha': HEAD},
          'base': {'repo': repo, 'ref': 'main', 'sha': MAIN},
          'body': reader.marker(JOB, request_id), 'merge_commit_sha': MERGE}
    run = {'id': 77, 'run_number': 12, 'run_attempt': 2, 'workflow_id': 19,
           'event': 'pull_request', 'path': reader.WORKFLOW_PATH, 'head_sha': HEAD, 'head_branch': branch,
           'repository': repo, 'head_repository': repo, 'pull_requests': [], 'status': 'completed',
           'conclusion': 'success'}
    names = ['docs', 'verify (source)', 'ci-required', 'review-attachment']
    jobs = [{'id': i, 'name': n, 'run_id': 77, 'run_attempt': 2, 'head_sha': HEAD, 'status': 'completed',
             'conclusion': 'skipped' if n == 'review-attachment' else 'success', 'steps': []}
            for i, n in enumerate(names, 1)]
    jobs[0]['steps'] = [{'name': f'PR 3 / {HEAD} / {MAIN} / {MERGE}', 'status': 'completed', 'conclusion': 'success'}]
    ci = {'workflow': {'id': 19, 'state': 'active', 'path': reader.WORKFLOW_PATH},
          'runs': [{'total_count': 1, 'workflow_runs': [deepcopy(run)]}],
          'run': deepcopy(run), 'attempt': deepcopy(run),
          'jobs': [{'total_count': len(jobs), 'jobs': jobs[:2]}, {'total_count': len(jobs), 'jobs': jobs[2:]}],
          'test_merge': {'sha': MERGE, 'parents': [{'sha': MAIN}, {'sha': HEAD}]}}
    data = {'repository': repo, 'main_ref': ref('heads/main', MAIN), 'main_commit': {'sha': MAIN, 'tree': tree},
            'request_sha': REQUEST, 'request_commit': {'sha': REQUEST, 'tree': tree, 'parents': [{'sha': MAIN}],
                'message': 'PW remote request v1\n\n' + reader.canonical({'mode': 'execute', 'request': req})},
            'input_record': input_record, 'completion_record': complete,
            'work_ref': ref('heads/content/pw/' + JOB, WORK),
            'work_commit': {'sha': WORK, 'parents': [{'sha': INPUT}], 'message': 'Publish' + marker},
            'product_ref': ref('heads/' + branch, HEAD),
            'product_commit': {'sha': HEAD, 'parents': [{'sha': MAIN}], 'message': 'Integrate' + marker},
            'product_diff': {'base_commit': {'sha': MAIN}, 'merge_base_commit': {'sha': MAIN},
                'total_commits': 1, 'commits': [{'sha': HEAD}], 'files': [
                    {'filename': p, 'status': 'modified' if p in registries else 'added'}
                    for p in registries | {plan, definition, background}]},
            'work_tag': ref('tags/work-prod-' + JOB, TAG),
            'release': {'id': generation['id'], 'tag_name': 'work-prod-' + JOB, 'target_commitish': TAG,
                'prerelease': True, 'draft': False, 'immutable': False, 'assets': [],
                'body': 'Picross production job ' + JOB},
            'pulls': [{'number': pr['number']}], 'pr': pr, 'ci': ci}
    return data, req


class ReaderTests(unittest.TestCase):
    def test_connector_resume_and_optional_metadata(self):
        data, req = observation()
        self.assertEqual(reader.evaluate(data)['status'], 'pr-bound')
        data['pulls'] = []
        del data['pr'], data['ci']
        ready = reader.evaluate(data)
        self.assertEqual(ready['status'], 'pr-ready')
        self.assertTrue(ready['draft_pr']['draft'])
        self.assertNotIn('issue', ready['draft_pr'])
        payload = reader.draft_metadata(dict(req, issue=42), ready['request'])
        self.assertEqual(payload['body'].splitlines()[-1], 'Zugeordnetes Issue: #42.')
        self.assertNotIn('issue', payload)

    def test_no_pr_on_stale_foreign_or_incomplete_generation(self):
        for keys, value in (
                (('main_ref', 'object', 'sha'), '0'*40),
                (('work_commit', 'parents'), []),
                (('product_commit', 'message'), 'Foreign'),
                (('completion_record', 'url'), 'https://example.invalid'),
                (('release', 'id'), 128),
                (('product_diff', 'files'), []),
                (('pr', 'state'), 'closed'),
                (('pr', 'body'), reader.marker(JOB, '0'*64)),
                (('pr', 'base', 'sha'), '0'*40),
                (('pr', 'head', 'repo', 'id'), 19),
                (('pulls',), [{'number': 3}, {'number': 4}])):
            with self.subTest(keys=keys), self.assertRaises(ValueError):
                data, _ = observation()
                row = data
                for key in keys[:-1]:
                    row = row[key]
                row[keys[-1]] = value
                reader.evaluate(data)

    def test_gate_requires_specific_actual_attempt_not_latest_jobs(self):
        data, req = observation()
        ci = data['ci']
        rows = reader.pages(ci['jobs'], 'jobs')
        self.assertEqual(reader.evaluate(data)['ci']['status'], 'checks-passed')
        self.assertEqual(reader.gate(req, data['pr'], ci['attempt'], rows)['status'], 'checks-passed')
        for state, conclusion, expected in [('queued', None, 'pending'),
                                             ('completed', 'action_required', 'approval-or-start-pending'),
                                             ('completed', 'cancelled', 'checks-incomplete'),
                                             ('completed', 'failure', 'checks-incomplete')]:
            candidate = deepcopy(data)
            original = candidate['ci']
            for run in (original['run'], original['attempt'], original['runs'][0]['workflow_runs'][0]):
                run.update(status=state, conclusion=conclusion)
            self.assertEqual(reader.evaluate(candidate)['ci']['status'], expected)
            self.assertEqual(reader.gate(req, data['pr'], original['attempt'], rows)['status'], expected)
        for keys, value in (
                (('workflow', 'path'), '.github/workflows/other.yml'),
                (('attempt', 'head_sha'), '0'*40),
                (('attempt', 'run_attempt'), 1),
                (('attempt', 'repository', 'id'), 123),
                (('run', 'pull_requests'), [{'number': 42}]),
                (('test_merge', 'parents'), [{'sha': MAIN}, {'sha': WORK}]),
                (('jobs', 1, 'jobs', 0, 'run_attempt'), 1),
                (('jobs', 0, 'jobs', 0, 'steps', 0, 'name'), 'Checkout source'),
                (('jobs', 1, 'jobs', 1, 'conclusion'), 'success'),
                (('jobs', 1, 'jobs'), [])):
            with self.subTest(keys=keys), self.assertRaises(ValueError):
                candidate = deepcopy(data)
                row = candidate['ci']
                for key in keys[:-1]:
                    row = row[key]
                row[keys[-1]] = value
                reader.evaluate(candidate)
