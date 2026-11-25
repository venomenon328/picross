"""Offline originals for precise PR, Git, release and CI binding."""
from base64 import b64decode, b64encode
from contextlib import nullcontext
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from email.message import Message
from hashlib import sha1, sha256
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from zipfile import ZipFile, ZipInfo

from tools import production_remote_continuation as collect, production_remote_reader as reader


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


def connector_observation():
    data, req = observation()
    ready = reader.evaluate(data)
    for key, commit in (('input_record', INPUT), ('completion_record', WORK)):
        original = data[key]
        path = original['path']
        data[key + '_directory'] = [{k: original[k] for k in ('type', 'path', 'sha', 'size', 'url')}]
        data[key] = {'encoding': 'utf-8', 'content': b64decode(original['content']).decode(),
                     'sha': original['sha'], 'display_url': f'https://github.com/{REPO}/blob/{commit}/{path}'}

    request_ref = ready['request_ref']
    repo = data['repository']
    completed = dict(status='completed', conclusion='success')
    trigger = dict(id=20, run_attempt=1, workflow_id=18, event='push', head_branch=request_ref,
                   head_sha=REQUEST, path='.github/workflows/work-growth.yml',
                   repository=repo, head_repository=repo, **completed)
    worker = dict(id=21, run_attempt=2, workflow_id=17, event='workflow_run', head_branch='main',
                  head_sha=MAIN, path='.github/workflows/pw-remote.yml', display_title='PW remote ' + request_ref,
                  repository=repo, head_repository=repo, **completed)
    preflight_name = 'Read capabilities and trigger before image setup'
    publish_name = 'Execute and acknowledge bound operation'
    steps = [dict(name=name, started_at=f'2026-11-25T12:00:0{i}Z', completed_at=f'2026-11-25T12:00:0{i + 1}Z',
                  **completed) for i, name in ((1, preflight_name), (3, publish_name))]
    job = dict(id=42, run_id=21, run_attempt=2, head_sha=MAIN, name='worker', steps=steps, **completed)
    binding = dict(request=ready['request'], repository=REPO, main=MAIN, job=JOB, expected=INPUT,
                   record_sha256=req['record_sha256'])
    preflight = dict(binding, tool_commit=MAIN, worker=17, operation='publish', package_ci=19)
    published = dict(binding, operation='step5', tools=MAIN, status='pr-ready', head=HEAD, work=WORK,
                     published_record_sha256=ready['published_record_sha256'])
    log = ('2026-11-25T12:00:02.4123456Z ' + reader.canonical(preflight) + '\n'
           '2026-11-25T12:00:04.5123456Z ' + reader.canonical(published) + '\n')
    data['step5_worker'] = dict(trigger=trigger, run=worker, attempt=deepcopy(worker), job_id=42, log=log,
                                jobs=[dict(total_count=1, jobs=[job])])
    ci = data['ci']
    del ci['workflow']
    package = ci.pop('runs')[0]['workflow_runs'][0]
    other = dict(package, id=78, workflow_id=20, path='.github/workflows/other.yml', run_number=99)
    ci['repository_runs'] = [dict(total_count=2, workflow_runs=[row]) for row in (other, package)]
    return data

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

    def test_connector_directory_and_worker_originals_support_resume_and_ci(self):
        data = connector_observation()
        ready = reader.evaluate(data)
        self.assertEqual(ready['status'], 'pr-bound')
        self.assertEqual(ready['package_ci_workflow_id'], 19)
        self.assertEqual(ready['ci']['status'], 'checks-passed')
        self.assertEqual(ready['ci']['attempt'], 2)
        data['ci']['repository_runs'] = [{'total_count': 0, 'workflow_runs': []}]
        self.assertEqual(reader.evaluate(data)['ci']['status'], 'missing-ci')
        del data['ci'], data['pr']
        data['pulls'] = []
        self.assertEqual(reader.evaluate(data)['status'], 'pr-ready')

    def test_connector_record_and_worker_reject_changed_originals(self):
        for keys, value in (
                (('input_record_directory', 0, 'path'), 'foreign/record.json'),
                (('input_record_directory', 0, 'size'), 0),
                (('input_record_directory', 0, 'url'), 'https://api.github.com/?ref=' + WORK),
                (('completion_record_directory',), []),
                (('completion_record', 'display_url'), 'https://github.com/' + REPO + '/blob/' + INPUT),
                (('completion_record', 'sha'), '2'*40),
                (('completion_record', 'content'), '{}'),
                (('step5_worker', 'trigger', 'head_sha'), WORK),
                (('step5_worker', 'run', 'head_sha'), WORK),
                (('step5_worker', 'attempt', 'run_attempt'), 1),
                (('step5_worker', 'attempt', 'display_title'), 'another request'),
                (('step5_worker', 'job_id'), 43),
                (('step5_worker', 'jobs', 0, 'jobs', 0, 'run_attempt'), 1),
                (('ci', 'repository_runs', 0, 'total_count'), 3),
                (('ci', 'repository_runs', 1, 'workflow_runs', 0, 'workflow_id'), 22),
                (('ci', 'repository_runs', 1, 'workflow_runs', 0, 'path'), '.github/workflows/other.yml'),
                (('ci', 'attempt', 'run_attempt'), 1)):
            with self.subTest(keys=keys), self.assertRaises(ValueError):
                candidate = connector_observation()
                row = candidate
                for key in keys[:-1]:
                    row = row[key]
                row[keys[-1]] = value
                reader.evaluate(candidate)
        for before, after in (
                ('"package_ci":19', '"package_ci":null'),
                ('"package_ci":19', '"package_ci":22'),
                ('"published_record_sha256":"', '"published_record_sha256":"00'),
                ('12:00:02.4123456Z', '12:00:04.4123456Z')):
            with self.subTest(before=before, after=after), self.assertRaises(ValueError):
                candidate = connector_observation()
                candidate['step5_worker']['log'] = candidate['step5_worker']['log'].replace(before, after)
                reader.evaluate(candidate)
        data = connector_observation()
        del data['step5_worker']
        with self.assertRaises(ValueError):
            reader.evaluate(data)

    def test_connector_does_not_reuse_an_old_success_after_a_new_run_or_attempt(self):
        data = connector_observation()
        ci = data['ci']
        recent = dict(ci['run'], id=79, run_number=13, run_attempt=1, status='queued', conclusion=None)
        ci['repository_runs'].append({'total_count': 3, 'workflow_runs': [recent]})
        for page in ci['repository_runs']:
            page['total_count'] = 3
        with self.assertRaisesRegex(ValueError, 'Changed CI run or attempt'):
            reader.evaluate(data)
        ci['run'] = ci['attempt'] = recent
        self.assertEqual(reader.evaluate(data)['ci']['status'], 'pending')

    def test_connector_completion_also_needs_the_published_sha256(self):
        data = connector_observation()
        content = data['completion_record']['content'] + ' '
        raw = content.encode()
        sha = sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest()
        data['completion_record'].update(content=content, sha=sha)
        data['completion_record_directory'][0].update(size=len(raw), sha=sha)
        with self.assertRaisesRegex(ValueError, 'Different Step 5 publication result'):
            reader.evaluate(data)

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


class ContinuationTests(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.now = datetime.now(timezone.utc)
        self.code = Path(reader.__file__).read_bytes()
        self.blob = reader.blob_id(self.code)
        self.data = connector_observation()
        rest, _ = observation()
        for field in ('input_record', 'completion_record'):
            self.data[field] = rest[field]
            del self.data[field + '_directory']
        self.data['release_asset_pages'] = [[]]
        self.data['active_workflow'] = rest['ci']['workflow']
        self.data['workflow_file'] = dict(rest['input_record'], path=reader.WORKFLOW_PATH,
            url=f'https://api.github.com/repos/{REPO}/contents/{reader.WORKFLOW_PATH}?ref={MAIN}')
        self.data['ci']['repository_runs'] = [{'total_count': 1, 'workflow_runs': [rest['ci']['run']]}]
        self.context = dict(repository_id=reader.REPOSITORIES[REPO], tools=MAIN, job=JOB,
                            request_sha=REQUEST, kind='ci', run=150, attempt=2)
        self.run = dict(id=150, run_attempt=2, head_sha=MAIN, head_branch='main', status='completed',
                        conclusion='success', path='.github/workflows/pw-remote.yml',
                        repository_id=reader.REPOSITORIES[REPO])

    def bundle(self, data=None, *, extra=None, reader_code=None, context=None):
        stage = self.root / ('stage-' + str(len(list(self.root.iterdir()))))
        context = self.context if context is None else context
        collect.stage(stage, context, self.data if data is None else data,
                      self.code if reader_code is None else reader_code, self.now)
        archive = stage.with_suffix('.zip')
        with ZipFile(archive, 'w') as output:
            for entry in stage.iterdir():
                output.write(entry, arcname=entry.name)
            if extra is not None:
                output.writestr(extra, b'unsafe')
        repo = reader.REPOSITORIES[REPO]
        artifact = dict(id=9, name=reader.artifact_name(context), expired=False,
                        size_in_bytes=archive.stat().st_size, digest='sha256:' + sha256(archive.read_bytes()).hexdigest(),
                        created_at=self.now.isoformat(), expires_at=(self.now+timedelta(days=1)).isoformat(),
                        workflow_run=dict(id=context['run'], head_sha=MAIN, head_branch='main',
                                          repository_id=repo, head_repository_id=repo))
        return archive, artifact

    def verify(self, archive, artifact, **kwargs):
        return reader.verify_continuation(archive, artifact, kwargs.pop('run', self.run), tools=MAIN,
                                          reader_blob=self.blob, now=self.now, **kwargs)

    def test_verified_ci_zip_and_fresh_binding(self):
        archive, artifact = self.bundle()
        checked = self.verify(archive, artifact)
        self.assertEqual(checked['result']['ci']['status'], 'checks-passed')
        self.assertEqual(checked['expected_fresh']['ci'], '19:77:2:completed:success')
        self.assertEqual(checked['expected_fresh']['worker'], '21:2:completed:success')
        self.assertEqual(checked['expected_fresh']['slot'], '3')
        self.assertEqual(checked['expected_fresh']['work'], WORK)
        for key in ('main', 'work', 'head', 'release', 'assets', 'pr', 'ci', 'worker', 'workflow-file'):
            with self.subTest(key=key):
                fresh = checked['expected_fresh'] | {key: 'changed'}
                with self.assertRaisesRegex(ValueError, 'Fresh Connector observation differs: ' + key):
                    reader.confirm_fresh(checked, list(fresh.items()))

    def test_foreign_tampered_expired_or_unsafe_zip(self):
        archive, artifact = self.bundle()
        for patch_values in ({'id': 0}, {'name': 'other'}, {'expired': True},
                             {'size_in_bytes': 1}, {'digest': 'sha256:' + '0'*64},
                             {'expires_at': (self.now-timedelta(minutes=1)).isoformat()}):
            with self.subTest(values=patch_values), self.assertRaises(ValueError):
                self.verify(archive, artifact | patch_values)
        for run in (self.run | {'run_attempt': 3}, self.run | {'status': 'in_progress', 'conclusion': None},
                    self.run | {'repository_id': 12}, self.run | {'conclusion': 'failure'}):
            with self.subTest(run=run), self.assertRaises(ValueError):
                self.verify(archive, artifact, run=run)
        symlink = ZipInfo('linked.py')
        symlink.create_system = 3
        symlink.external_attr = 0o120777 << 16
        for name in ('../../reader.py', 'production_remote_reader.py/extra', symlink):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'Unsafe'):
                self.verify(*self.bundle(extra=name))
        with self.assertRaisesRegex(ValueError, 'Reader Git blob'):
            self.verify(*self.bundle(reader_code=self.code + b'\n'))

    def test_read_only_repeat_after_independently_bound_worker_failure(self):
        data = deepcopy(self.data)
        del data['ci'], data['pr']
        data['pulls'] = []
        evidence = data['step5_worker']
        context = self.context | {'kind': 'publication'}
        extra_job = dict(evidence['jobs'][0]['jobs'][0], id=94, name='continuation', conclusion='failure')
        evidence['jobs'][0]['jobs'].append(extra_job)
        evidence['jobs'][0]['total_count'] += 1
        for row in (evidence['run'], evidence['attempt']):
            row['conclusion'] = 'failure'
        initial = self.verify(*self.bundle(data, context=context))
        self.assertEqual(initial['result']['status'], 'pr-ready')
        self.assertEqual(initial['expected_fresh']['worker'], '21:2:completed:failure')
        self.assertEqual(initial['result']['work'], WORK)
        extra_job['name'] = 'result'
        with self.assertRaisesRegex(ValueError, 'Different Step 5 worker'):
            self.verify(*self.bundle(data, context=context))

    def test_unfinished_source_run_only_accepted_for_own_collection(self):
        data = deepcopy(self.data)
        evidence = data['step5_worker']
        for row in (evidence['run'], evidence['attempt']):
            row.update(status='in_progress', conclusion=None)
        with self.assertRaisesRegex(ValueError, 'Different Step 5 worker'):
            self.verify(*self.bundle(data))
        context = self.context | {'run': 21}
        checked = self.verify(*self.bundle(data, context=context), run=self.run | {'id': 21})
        self.assertEqual(checked['expected_fresh']['worker'], '21:2:completed:success')

    def test_collector_keeps_only_original_step_evidence_and_requires_all_pages(self):
        worker = self.data['step5_worker']
        rows = {'actions/runs/20': worker['trigger'], 'actions/runs/21': worker['run'],
                'actions/runs/21/attempts/2': worker['attempt'],
                'actions/runs/21/attempts/2/jobs?per_page=100&page=1': worker['jobs'][0]}
        raw = '2026-11-25T12:00:10Z non-selected text\n' + worker['log']
        result = collect.worker_originals(rows.__getitem__, 20, 21, lambda job: raw if job == 42 else '')
        self.assertEqual(result, worker)

        def api(endpoint):
            rows = [dict(id=n) for n in (range(100) if endpoint.endswith('=1') else range(100, 102))]
            return dict(total_count=102, jobs=rows)

        self.assertEqual(len(reader.pages(collect.paged(api, 'jobs', 'jobs'), 'jobs')), 102)
        with self.assertRaisesRegex(ValueError, 'Incomplete paged jobs'):
            collect.paged(lambda endpoint: {'total_count': 2, 'jobs': [{'id': 1}]}, 'jobs', 'jobs')

    def test_worker_log_redirect_downloads_without_forwarding_github_token(self):
        location = 'https://logstore.blob.core.windows.net/log?sig=private'
        headers = Message()
        headers['Location'] = location
        redirect = SimpleNamespace(status=302, headers=headers)
        log = BytesIO(b'actual job log\n')
        log.status = 200

        with (patch.object(collect.github_rest, 'publisher_token', return_value='private-token'),
              patch.object(collect.github_rest, 'open_api', return_value=nullcontext(redirect)) as api,
              patch.object(collect, 'build_opener') as opener):
            opener.return_value.open.return_value = log
            self.assertEqual(collect.original_log(94), 'actual job log\n')

        self.assertTrue(api.call_args.args[0].endswith('/actions/jobs/94/logs'))
        self.assertEqual(api.call_args.kwargs['token'], 'private-token')
        self.assertIs(api.call_args.kwargs['redirect'].http_error_302(None, redirect, 302, '', headers), redirect)
        request = opener.return_value.open.call_args.args[0]
        self.assertEqual(request.full_url, location)
        self.assertFalse(request.header_items())
        self.assertIsInstance(opener.call_args.args[1], collect.github_rest.NoRedirect)

    def test_worker_log_download_retries_with_a_new_location(self):
        first = 'https://logstore.blob.core.windows.net/log?sig=first'
        second = 'https://logstore.blob.core.windows.net/log?sig=second'
        log = BytesIO(b'actual job log')
        log.status = 200

        with (patch.object(collect, 'log_location', side_effect=[first, second]) as locations,
              patch.object(collect, 'build_opener') as opener,
              patch.object(collect, 'sleep') as sleep):
            download = opener.return_value.open
            download.side_effect = [HTTPError(first, 403, 'expired', {}, None), log]
            self.assertEqual(collect.original_log(94), 'actual job log')

        self.assertEqual([call.args[0] for call in locations.call_args_list], [94, 94])
        self.assertEqual([call.args[0].full_url for call in download.call_args_list], [first, second])
        sleep.assert_called_once_with(2)

    def test_worker_log_transport_errors_are_safe_and_fail_closed(self):
        signed = 'https://logstore.blob.core.windows.net.example.org/log?sig=private'
        headers = Message()
        headers['Location'] = signed
        redirect = SimpleNamespace(status=302, headers=headers)
        error = 'Cannot read original Step 5 worker job log 94'

        with (patch.object(collect.github_rest, 'publisher_token', return_value='private-token'),
              patch.object(collect.github_rest, 'open_api', return_value=nullcontext(redirect)),
              patch.object(collect, 'build_opener') as opener):
            with self.assertRaises(ValueError) as exc:
                collect.original_log(94)
            self.assertEqual(str(exc.exception), f'{error} (GitHub API: invalid response)')
            opener.assert_not_called()

        failure = collect.github_rest.Failure('access', 'ignored private-token', 403)
        with (patch.object(collect, 'log_location', side_effect=failure) as location,
              patch.object(collect, 'sleep') as sleep):
            with self.assertRaises(ValueError) as exc:
                collect.original_log(94)
            self.assertEqual(str(exc.exception), f'{error} (GitHub API: HTTP 403)')
            location.assert_called_once_with(94)
            sleep.assert_not_called()

    def test_collector_rejects_main_change_before_collection(self):
        api = {'': self.data['repository'], 'git/ref/heads/main': {
            'ref': 'refs/heads/main', 'object': {'type': 'commit', 'sha': WORK}}}.__getitem__
        with patch.object(collect.remote.work_refs, 'FIXTURE', False):
            with self.assertRaisesRegex(ValueError, 'Stale Main'):
                collect.collect(api, REPO, MAIN, JOB, 150, 2)
