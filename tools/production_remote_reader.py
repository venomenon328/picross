"""Offline Step 5 continuation and Package CI reader for GitHub originals."""
import argparse
from base64 import b64decode
from datetime import datetime, timedelta, timezone
from hashlib import file_digest, sha1, sha256
import json
from pathlib import Path
import re
import stat
from urllib.parse import urlencode
from zipfile import BadZipFile, ZipFile

REPOSITORIES = {'venomenon328/picross': 1381196633, 'venomenon328/picross-remote-test': 1470169013}
WORKFLOW = 'ci-modular.yml'
WORKFLOW_PATH = '.github/workflows/' + WORKFLOW
PREFLIGHT_STEP = 'Read capabilities and trigger before image setup'
PUBLISH_STEP = 'Execute and acknowledge bound operation'
SHA = re.compile('[0-9a-f]{40}')
DIGEST = re.compile('[0-9a-f]{64}')
JOB = re.compile(r'pz-[a-z0-9][a-z0-9-]{0,59}')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def digest(value):
    return sha256(canonical(value).encode()).hexdigest()


def product_branch(job):
    return 'content/integrate-' + job


def marker(job, owner):
    return f'<!-- picross-production {job} {owner} -->'


def draft_metadata(req, owner):
    job = req['job']
    issue = req['issue']
    body = marker(job, owner) + '\n\nProduktintegration für ' + job + '.'
    if issue is not None:
        body += '\n\nZugeordnetes Issue: #' + str(issue) + '.'
    return {'head': product_branch(job), 'base': 'main', 'draft': True,
            'title': 'Rätsel integrieren · ' + job, 'body': body}


def pr_query(repository, job):
    return 'pulls?' + urlencode({'head': repository.split('/')[0] + ':' + product_branch(job),
                                 'state': 'all', 'per_page': 2})


def pr_slot(rows):
    require(isinstance(rows, list) and len(rows) <= 1, 'Ambiguous product PR ownership')
    return rows[0] if rows else None


def associated(req, pr, head, owner, *, merged=False, draft=False, repository_id=None):
    repository = req['repository']
    marks = [line for line in (pr.get('body') or '').splitlines()
             if line.strip().startswith('<!-- picross-production')]
    require(type(pr.get('number')) is int and pr['number'] > 0 and
            (req.get('pr') is None or req['pr'] == pr['number']) and
            all(pr[side]['repo']['full_name'] == repository and
                (repository_id is None or pr[side]['repo']['id'] == repository_id) for side in ('head', 'base')) and
            pr['head']['ref'] == product_branch(req['job']) and pr['head']['sha'] == head and
            pr['base']['ref'] == 'main' and marks == [marker(req['job'], owner)],
            'Foreign product PR or changed head')
    if merged:
        require(pr['state'] == 'closed' and pr['merged'] is True and pr['merged_at']
                and SHA.fullmatch(pr.get('merge_commit_sha') or ''), 'Verified merged product PR required')
    else:
        require(pr['state'] == 'open' and pr['base']['sha'] == req['main'], 'Product PR closed or basis changed')
        require(not draft or pr.get('draft') is True, 'Expected the associated draft PR')
    return pr


def commit_parents(row, sha, parents):
    require(SHA.fullmatch(sha) and row['sha'] == sha and [p['sha'] for p in row['parents']] == parents,
            'Different Git commit or parents')


def owner(row, sha, parent):
    commit_parents(row, sha, [parent])
    match = re.fullmatch(r'.+\n\nPW-Remote: ([a-f0-9]{64})\n?', row['message'])
    require(match, 'Commit is not bound to this remote operation')
    return match[1]


def ref(row, name):
    require(row['ref'] == 'refs/' + name and row['object']['type'] == 'commit'
            and SHA.fullmatch(row['object']['sha']), 'Different Git reference: ' + name)
    return row['object']['sha']


def record_bytes(row, repository, commit, path, *, directory=None):
    require(SHA.fullmatch(commit), 'Expected a pinned record commit')
    api = f'https://api.github.com/repos/{repository}'
    if directory is None:
        entry = row
        require(row['encoding'] == 'base64', 'Expected original REST record contents')
        raw = b64decode(''.join(row['content'].split()), validate=True)
    else:
        require(isinstance(directory, list), 'Expected original record directory listing')
        matches = [entry for entry in directory if entry['path'] == path]
        require(len(matches) == 1, 'Missing or ambiguous record path at pinned commit')
        entry = matches[0]
        require(row['encoding'] == 'utf-8' and row['sha'] == entry['sha']
                and row['display_url'] == f'https://github.com/{repository}/blob/{commit}/{path}',
                'Different connector record or pinned commit')
        raw = row['content'].encode('utf-8')
    require(entry['type'] == 'file' and entry['path'] == path
            and entry['url'] == f'{api}/contents/{path}?ref={commit}',
            'Expected exact record path at pinned commit')
    require(type(entry['size']) is int and len(raw) == entry['size']
            and sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest() == entry['sha'],
            'Record blob bytes differ')
    return raw

def parse(raw):
    def unique(pairs):
        value = dict(pairs)
        require(len(value) == len(pairs), 'Duplicate JSON key')
        return value

    return json.loads(raw, object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('Non-finite JSON number')))


def binding(data):
    repository = data['repository']['full_name']
    repository_id = REPOSITORIES.get(repository)
    require(repository_id and data['repository']['id'] == repository_id
            and data['repository']['default_branch'] == 'main', 'Different repository identity')
    main = ref(data['main_ref'], 'heads/main')
    invocation = data['request_commit']
    prefix, sep, body = invocation['message'].rstrip('\n').partition('\n\n')
    envelope = parse(body)
    req = envelope['request']
    job, expected = req['job'], req['expected']
    request_id = digest(req)
    require(prefix == 'PW remote request v1' and sep and set(envelope) == {'mode', 'request'}
            and envelope['mode'] == 'execute' and canonical(envelope) == body
            and req['operation'] == 'step5' and req['format'] in ('pw-remote-v1', 'pw-remote-v2')
            and req['main'] == req['tools'] == main and req['repository'] == repository
            and JOB.fullmatch(job), 'Different Step 5 request or main')
    commit_parents(invocation, data['request_sha'], [main])
    require(data['main_commit']['sha'] == main and invocation['tree']['sha'] == data['main_commit']['tree']['sha'],
            'Different request tree')
    path = f'content/authoring/{job}/current/record.json'
    work = ref(data['work_ref'], 'heads/content/pw/' + job)
    original = record_bytes(data['input_record'], repository, expected, path,
                            directory=data.get('input_record_directory'))
    completed = record_bytes(data['completion_record'], repository, work, path,
                             directory=data.get('completion_record_directory'))
    prior, record = parse(original), parse(completed)
    head = ref(data['product_ref'], 'heads/' + product_branch(job))
    require(owner(data['work_commit'], work, expected) == owner(data['product_commit'], head, main) == request_id
            and sha256(original).hexdigest() == req['record_sha256']
            and prior['puzzle_id'] == record['puzzle_id'] == job
            and record['state'] == 'registered' and record['integration']['commit'] == head
            and prior['work_release'] == record['work_release'], 'Different Completion or Step 5 owner')
    release = data['release']
    tag = 'work-prod-' + job
    anchor = ref(data['work_tag'], 'tags/' + tag)
    require(record['work_release'] == {'id': release['id'], 'anchor': anchor}
            and release['target_commitish'] == anchor and release['tag_name'] == tag
            and release['body'] == 'Picross production job ' + job
            and release['prerelease'] is True and release['draft'] is False and release['immutable'] is False,
            'Different work release generation')
    assets = {}
    def collect(value):
        if isinstance(value, list):
            for child in value:
                collect(child)
        elif isinstance(value, dict):
            if {'asset', 'file', 'bytes', 'sha256'} == value.keys() and isinstance(value['asset'], dict):
                asset = value['asset']
                require(asset['repository'] == repository and asset['job'] == job
                        and asset['release_id'] == release['id'], 'Foreign original asset')
                expected = ('original-' + value['sha256'], value['bytes'])
                require(assets.setdefault(asset['asset_id'], expected) == expected, 'Conflicting original asset ID')
            for child in value.values():
                collect(child)
    collect(record)
    rows = release['assets']
    if 'release_asset_pages' in data:
        rows = [asset for page in data['release_asset_pages'] for asset in page]
        require(all(asset in rows for asset in release['assets']), 'Release and paged assets changed')
    require(len(rows) == len(assets) and {row['id']: (row['name'], row['size']) for row in rows} == assets
            and all(row['label'] == 'picross-original:' + tag and row['state'] == 'uploaded' for row in rows),
            'Incomplete or changed work release assets')
    diff = data['product_diff']
    require(diff['base_commit']['sha'] == diff['merge_base_commit']['sha'] == main
            and diff['total_commits'] == 1 and [c['sha'] for c in diff['commits']] == [head],
            'Different product comparison')
    delivery = {p for p, row in record['integration']['result']['files'].items() if row is not None}
    expected_paths = delivery | {'content/registry.json', 'game/data/registry.json', '.ci/package.json',
                                 f'content/backgrounds/{job}.json'}
    files = diff['files']
    require(len(files) == len(expected_paths) and {row['filename'] for row in files} == expected_paths
            and all(row['status'] == 'added' if row['filename'] not in
                    {'content/registry.json', 'game/data/registry.json', '.ci/package.json'}
                    else row['status'] in ('modified', 'added') for row in files),
            'Incomplete or foreign product diff')
    row = pr_slot(data['pulls'])
    pr = data.get('pr')
    if row is None:
        require(pr is None, 'Unexpected PR readback')
    else:
        require(pr and row['number'] == pr['number'], 'Missing exact PR readback')
        associated(req, pr, head, request_id, repository_id=repository_id)
    result = {'status': 'pr-bound' if pr else 'pr-ready', 'repository': repository, 'main': main,
              'head': head, 'work': work, 'published_record_sha256': sha256(completed).hexdigest(),
              'request': request_id, 'request_ref': f'work-prod-control/remote/{job}/{digest(envelope)}',
              'draft_pr': draft_metadata(req, request_id), 'pr': pr['number'] if pr else None,
              'draft': pr['draft'] if pr else None}
    return req, pr, result


def run_query(job, head, page=1):
    return urlencode({'event': 'pull_request', 'branch': product_branch(job), 'head_sha': head,
                      'per_page': 100, 'page': page})


def pages(values, field):
    rows = [row for page in values for row in page[field]]
    require(values and all(page['total_count'] == len(rows) for page in values)
            and len({row['id'] for row in rows}) == len(rows), 'Incomplete or duplicate ' + field)
    return rows


def run_source(run, repository, repository_id, *, event, branch, head):
    return (run['event'] == event and run['head_sha'] == head and run['head_branch'] == branch
            and all(run[k]['full_name'] == repository and
                    (repository_id is None or run[k]['id'] == repository_id) for k in ('repository', 'head_repository'))
            and all(type(run[k]) is int and run[k] > 0 for k in ('id', 'run_attempt', 'workflow_id')))


def validate_run(req, head, workflow_id, run, *, repository_id=None):
    require(run['workflow_id'] == workflow_id and run['path'] == WORKFLOW_PATH
            and run_source(run, req['repository'], repository_id, event='pull_request',
                           branch=product_branch(req['job']), head=head), 'Foreign CI run or source')


def matching_fields(row, expected):
    return all(row.get(key) == value for key, value in expected.items())


def worker_log_row(log, steps, name, field, *, original=False):
    matches = [step for step in steps if step['name'] == name]
    require(len(matches) == 1 and matches[0]['status'] == 'completed'
            and matches[0]['conclusion'] == 'success', 'Missing successful Step 5 worker step: ' + name)
    step = matches[0]
    start, end = (datetime.fromisoformat(step[key]) for key in ('started_at', 'completed_at'))
    require(isinstance(log, str), 'Expected the original Step 5 worker log text')
    rows = []
    for line in log.splitlines():
        stamp, _, payload = line.partition(' ')
        if payload.startswith('{'):
            when = datetime.fromisoformat(stamp).replace(microsecond=0)
            if start <= when <= end:
                row = parse(payload)
                if isinstance(row, dict) and field in row:
                    rows.append(line if original else row)
    require(len(rows) == 1, 'Missing or ambiguous Step 5 worker log row: ' + field)
    return rows[0]


def connector_workflow(req, result, request_sha, evidence, repository_id, *, collection=None):
    """Use the active workflow checked by the published generation's Step 5 worker."""
    repository, main = req['repository'], req['main']
    request_ref = result['request_ref']
    trigger = evidence['trigger']
    require(run_source(trigger, repository, repository_id, event='push', branch=request_ref, head=request_sha)
            and trigger['path'] == '.github/workflows/work-growth.yml'
            and trigger['status'] == 'completed' and trigger['conclusion'] == 'success',
            'Different Step 5 request trigger')
    run, attempt = evidence['run'], evidence['attempt']
    jobs = pages(evidence['jobs'], 'jobs')
    failures = [job for job in jobs if job['conclusion'] not in ('success', 'skipped')]
    # A failed downstream read job cannot undo the confirmed double push.
    # Recovery needs the actual successful worker and only this read failure.
    read_failure = (len(failures) == 1 and failures[0]['name'] == 'continuation'
                    and failures[0]['status'] == 'completed'
                    and failures[0]['conclusion'] in ('failure', 'cancelled', 'timed_out'))
    for row in (run, attempt):
        require(run_source(row, repository, repository_id, event='workflow_run', branch='main', head=main)
                and row['path'] == '.github/workflows/pw-remote.yml'
                and row['display_title'] == 'PW remote ' + request_ref
                and (row['status'] == 'completed' and (row['conclusion'] == 'success'
                                                      or read_failure and row['conclusion'] in ('failure', 'cancelled', 'timed_out'))
                     or collection == (row['id'], row['run_attempt'])
                     and row['status'] == 'in_progress' and row['conclusion'] is None),
                'Different Step 5 worker run or request')
    require(matching_fields(attempt, {key: run[key] for key in ('id', 'workflow_id', 'run_attempt')}),
            'Different Step 5 worker attempt')
    require(all(matching_fields(job, {'run_id': run['id'], 'run_attempt': run['run_attempt'], 'head_sha': main})
                for job in jobs), 'Different Step 5 worker jobs')
    workers = [job for job in jobs if job['name'] == 'worker']
    require(len(workers) == 1 and matching_fields(workers[0], {'id': evidence['job_id'],
            'status': 'completed', 'conclusion': 'success'}), 'Different Step 5 worker log job')
    steps, log = workers[0]['steps'], evidence['log']
    checked = worker_log_row(log, steps, PREFLIGHT_STEP, 'package_ci')
    published = worker_log_row(log, steps, PUBLISH_STEP, 'published_record_sha256')
    binding = {'request': result['request'], 'repository': repository, 'main': main, 'job': req['job'],
               'expected': req['expected'], 'record_sha256': req['record_sha256']}
    require(matching_fields(checked, {**binding, 'tool_commit': main, 'operation': 'publish',
                                      'worker': run['workflow_id']})
            and type(checked['package_ci']) is int and checked['package_ci'] > 0,
            'Different active Package CI workflow or Step 5 preflight')
    require(matching_fields(published, {**binding, 'tools': main, 'operation': 'step5',
                'head': result['head'], 'work': result['work'],
                'published_record_sha256': result['published_record_sha256']})
            and published['status'] in ('pr-ready', 'pr-bound'), 'Different Step 5 publication result')
    return checked['package_ci']

def gate(req, pr, run=None, jobs=(), *, merge_commit=None, strict=False):
    head = pr['head']['sha']
    merge = pr.get('merge_commit_sha')
    result = {'pr': pr['number'], 'url': f'https://github.com/{req["repository"]}/pull/{pr["number"]}',
              'head': head, 'base': req['main'], 'test_merge': merge, 'checks': {},
              'next': 'Read the bound product PR again after GitHub schedules its Package CI.'}
    if pr.get('mergeable') is False or pr.get('mergeable_state') == 'dirty':
        return {**result, 'status': 'conflict', 'next': 'Resolve the changed product basis.'}
    if run is None:
        return {**result, 'status': 'missing-ci'}
    result.update(run=run['id'], attempt=run['run_attempt'],
                  run_url=f'https://github.com/{req["repository"]}/actions/runs/{run["id"]}')
    if run['status'] in ('action_required', 'waiting', 'requested') or run['conclusion'] == 'action_required':
        return {**result, 'status': 'approval-or-start-pending', 'next': 'Inspect Actions approval and the PR trigger identity.'}
    if run['status'] != 'completed' or not SHA.fullmatch(merge or ''):
        return {**result, 'status': 'pending'}
    if strict:
        if merge_commit is None or pr.get('mergeable') is not True:
            return {**result, 'status': 'pending'}
        commit_parents(merge_commit, merge, [req['main'], head])
    require(all(j['run_id'] == run['id'] and j['head_sha'] == head
                and (not strict or j['run_attempt'] == run['run_attempt'] and j['status'] == 'completed')
                for j in jobs), 'Incomplete or foreign CI jobs')
    attachment = [j for j in jobs if j['name'] == 'review-attachment']
    require(len(attachment) <= 1 and (not strict or len(attachment) == 1)
            and all(j['conclusion'] == 'skipped' for j in attachment),
            'Unexpected evidence delivery on the product PR')
    rows = [j for j in jobs if j['name'] != 'review-attachment']
    expected = {'docs', 'verify (source)', 'ci-required'}
    result['checks'] = {j['name']: j['conclusion'] for j in rows}
    if run['conclusion'] != 'success' or set(result['checks']) != expected or len(rows) != len(expected) or any(
            value != 'success' for value in result['checks'].values()):
        return {**result, 'status': 'checks-incomplete', 'next': 'Inspect the missing or unsuccessful Package CI jobs.'}
    docs = next(j for j in rows if j['name'] == 'docs')
    step = f'PR {pr["number"]} / {head} / {req["main"]} / {merge}'
    require(sum(s['name'] == step for s in docs['steps']) == 1
            and any(s['name'] == step and s['conclusion'] == 'success'
                    and (not strict or s['status'] == 'completed') for s in docs['steps']),
            'Package CI did not check this PR, head, basis and test merge')
    return {**result, 'status': 'checks-passed', 'next': 'Review the complete product diff and actual merge authorization.'}


def ci_status(req, pr, evidence, repository_id, *, workflow_id=None):
    head = pr['head']['sha']
    if workflow_id is None:
        workflow = evidence['workflow']
        require(workflow['state'] == 'active' and workflow['path'] == WORKFLOW_PATH
                and type(workflow['id']) is int and workflow['id'] > 0, 'Different Package CI workflow')
        workflow_id = workflow['id']
        runs = pages(evidence['runs'], 'workflow_runs')
    else:
        runs = [run for run in pages(evidence['repository_runs'], 'workflow_runs')
                if run['workflow_id'] == workflow_id or run['path'] == WORKFLOW_PATH]
    for run in runs:
        validate_run(req, head, workflow_id, run, repository_id=repository_id)
        require(type(run['run_number']) is int and run['run_number'] > 0, 'Invalid run number')
    require(len({r['run_number'] for r in runs}) == len(runs), 'Ambiguous current PR run')
    if not runs:
        return gate(req, pr)
    selected = max(runs, key=lambda run: run['run_number'])
    current, attempt = evidence['run'], evidence['attempt']
    keys = ('id', 'run_number', 'run_attempt', 'status', 'conclusion')
    for row in (current, attempt):
        validate_run(req, head, workflow_id, row, repository_id=repository_id)
        require(all(row[k] == selected[k] for k in keys), 'Changed CI run or attempt; refresh the original reads')
        require(all(p['number'] == pr['number'] for p in row['pull_requests']), 'Foreign PR in CI run')
    if attempt['status'] != 'completed' or attempt['conclusion'] == 'action_required':
        return gate(req, pr, attempt)
    return gate(req, pr, attempt, pages(evidence['jobs'], 'jobs'), merge_commit=evidence.get('test_merge'), strict=True)


def evaluate(data, *, collection=None):
    req, pr, result = binding(data)
    repository_id = REPOSITORIES[req['repository']]
    workflow_id = None
    if 'step5_worker' in data:
        workflow_id = connector_workflow(req, result, data['request_sha'], data['step5_worker'], repository_id,
                                         collection=collection)
        result['package_ci_workflow_id'] = workflow_id
    else:
        require('input_record_directory' not in data and 'completion_record_directory' not in data,
                'Read the bound Step 5 worker for connector originals')
    if 'active_workflow' in data:
        require(matching_fields(data['active_workflow'], {'path': WORKFLOW_PATH, 'state': 'active',
                                                         'id': workflow_id}), 'Package CI workflow changed')
    if 'ci' in data:
        require(pr is not None, 'Read the bound PR before its CI')
        result['ci'] = ci_status(req, pr, data['ci'], repository_id, workflow_id=workflow_id)
    return result


FORMAT = 'pw-remote-continuation-v1'
PURPOSE = 'step5-pr-ci'
READER_FILE = 'production_remote_reader.py'
ORIGINALS_FILE = 'originals.json'
MEMBER_LIMITS = {'manifest.json': 16_384, READER_FILE: 131_072, ORIGINALS_FILE: 16 * 1024**2}
BASE_KEYS = {'repository', 'main_ref', 'main_commit', 'request_sha', 'request_commit', 'work_ref',
             'work_commit', 'input_record', 'completion_record', 'step5_worker', 'product_ref',
             'product_commit', 'product_diff', 'work_tag', 'release', 'release_asset_pages',
             'pulls', 'active_workflow', 'workflow_file'}


def artifact_name(context):
    return f'pw-continue-{context["job"]}-{context["request_sha"]}-{context["run"]}-{context["attempt"]}'


def blob_id(raw):
    return sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest()


def closed(row, keys, message):
    require(isinstance(row, dict) and set(row) == keys, message)


def archive_contents(archive, artifact):
    limit = sum(MEMBER_LIMITS.values())
    require(0 < archive.stat().st_size == artifact['size_in_bytes'] <= limit + 65536,
            'Actions ZIP length differs or exceeds the continuation limit')
    with archive.open('rb') as stream:
        require('sha256:' + file_digest(stream, 'sha256').hexdigest() == artifact['digest'],
                'Actions ZIP digest differs')
        stream.seek(0)
        with ZipFile(stream) as bundle:
            entries = bundle.infolist()
            require(len(entries) == len(MEMBER_LIMITS)
                    and {row.orig_filename for row in entries} == MEMBER_LIMITS.keys()
                    and all(row.orig_filename == row.filename and not row.is_dir() and not row.flag_bits & 1
                            and stat.S_IFMT(row.external_attr >> 16) in (0, stat.S_IFREG)
                            and not row.external_attr & 0x410
                            and 0 < row.file_size <= MEMBER_LIMITS[row.filename] for row in entries),
                    'Unsafe, oversized, missing or extra continuation ZIP member')
            return {name: bundle.read(name) for name in MEMBER_LIMITS}


def expiry(value):
    result = datetime.fromisoformat(value)
    require(result.tzinfo is not None, 'Expected an explicit UTC offset')
    return result


def delivery_metadata(context, artifact, collection, now):
    run = artifact['workflow_run']
    require(type(artifact['id']) is int and artifact['id'] > 0
            and artifact['name'] == artifact_name(context) and artifact['expired'] is False
            and run['id'] == context['run'] and run['head_sha'] == context['tools']
            and run['head_branch'] == 'main'
            and run['repository_id'] == run['head_repository_id'] == context['repository_id'],
            'Different or expired Actions artifact')
    require(matching_fields(collection, {'id': context['run'], 'run_attempt': context['attempt'],
                                         'head_sha': context['tools'], 'head_branch': 'main',
                                         'path': '.github/workflows/pw-remote.yml',
                                         'status': 'completed', 'conclusion': 'success'})
            and collection['repository_id'] == context['repository_id'],
            'Read back the successful current collection run and attempt')
    created, expires = (expiry(artifact[k]) for k in ('created_at', 'expires_at'))
    require(created <= now < expires <= created + timedelta(days=1, minutes=5),
            'Expired or unexpected continuation retention')
    return expires


def evaluate_originals(data, context):
    optional = {'pr', 'ci'} & data.keys()
    closed(data, BASE_KEYS | optional, 'Unexpected continuation originals')
    evidence = data['step5_worker']
    closed(evidence, {'trigger', 'run', 'attempt', 'jobs', 'job_id', 'log'},
           'Unexpected Step 5 worker originals')
    require(len(evidence['log'].splitlines()) == 2, 'Expected only the two original worker evidence lines')
    req, pr, _ = binding(data)
    require(req['format'] == 'pw-remote-v2' and req['job'] == context['job']
            and req['main'] == context['tools'] and data['request_sha'] == context['request_sha']
            and REPOSITORIES[req['repository']] == context['repository_id']
            and ('ci' in data) == (context['kind'] == 'ci'), 'Different continuation scope')
    record_bytes(data['workflow_file'], req['repository'], req['main'], WORKFLOW_PATH)
    if 'ci' in data:
        ci = data['ci']
        fields = {'repository_runs'}
        if ci['repository_runs'][0]['total_count']:
            fields |= {'run', 'attempt'}
            if ci['attempt']['status'] == 'completed' and ci['attempt']['conclusion'] != 'action_required':
                fields.add('jobs')
                if SHA.fullmatch(pr.get('merge_commit_sha') or ''):
                    fields.add('test_merge')
        closed(ci, fields, 'Unexpected Package CI originals')
    return evaluate(data, collection=(context['run'], context['attempt']))


def fresh_values(data, result):
    """Fixed scalar projections of volatile GitHub reads. No record or log transfer."""
    evidence = data['step5_worker']
    release = data['release']
    pr = data.get('pr')

    def attempt(row):
        return ':'.join(atom(row[k]) for k in ('id', 'run_attempt', 'status', 'conclusion'))

    def atom(value):
        return json.dumps(value) if value is None or isinstance(value, bool) else str(value)

    asset_rows = [asset for page in data['release_asset_pages'] for asset in page]
    assets = [':'.join(str(row[k]) for k in ('id', 'name', 'size', 'label', 'state')) for row in asset_rows]
    state = {'main': result['main'], 'work': result['work'], 'head': result['head'],
             'repository': str(data['repository']['id']), 'request-commit': data['request_sha'],
             'trigger': attempt(evidence['trigger']), 'worker': attempt(evidence['run'])
             if evidence['run']['status'] == 'completed' else
             f'{evidence["run"]["id"]}:{evidence["run"]["run_attempt"]}:completed:success',
             'tag': ref(data['work_tag'], 'tags/' + release['tag_name']),
             'release': ':'.join(str(x) for x in (release['id'], release['target_commitish'],
                                                 atom(release['draft']), atom(release['prerelease']),
                                                 atom(release['immutable']))),
             'assets': ','.join(sorted(assets)) or 'empty',
             'workflow-file': data['workflow_file']['sha'],
             'slot': 'empty' if pr is None else str(pr['number'])}
    if pr:
        state['pr'] = ':'.join(atom(x) for x in (pr['number'], pr['state'], atom(pr['draft']),
            atom(pr['mergeable']), pr.get('mergeable_state'), pr.get('merge_commit_sha'),
            pr['base']['sha'], pr['head']['sha'], result['request']))
    if 'ci' in data:
        ci = data['ci']
        state['ci'] = (str(ci['run']['workflow_id']) + ':' + attempt(ci['run'])) if 'run' in ci else 'missing'
    return state


def verify_continuation(archive, artifact, collection, *, tools, reader_blob, now=None, staging=False):
    now = now or datetime.now(timezone.utc)
    raw = archive_contents(archive, artifact)
    manifest = parse(raw['manifest.json'])
    closed(manifest, {'format', 'purpose', 'context', 'expires', 'files'}, 'Invalid continuation manifest')
    context = manifest['context']
    closed(context, {'repository_id', 'tools', 'job', 'request_sha', 'kind', 'run', 'attempt'},
           'Unexpected continuation context')
    require(manifest['format'] == FORMAT and manifest['purpose'] == PURPOSE
            and context['tools'] == tools and SHA.fullmatch(tools)
            and SHA.fullmatch(context['request_sha']) and JOB.fullmatch(context['job'])
            and context['kind'] in ('publication', 'ci')
            and all(type(context[k]) is int and context[k] > 0 for k in ('repository_id', 'run', 'attempt'))
            and blob_id(raw[READER_FILE]) == reader_blob,
            'Different continuation purpose, scope or trusted Reader Git blob')
    # The collector can verify the upload before its own run completes. Only the
    # actor can supply the successful independent run read for a continuation.
    metadata = collection
    if staging:
        metadata = {**collection, 'status': 'completed', 'conclusion': 'success'}
    expires = delivery_metadata(context, artifact, metadata, now)
    require(now < expiry(manifest['expires']) <= expires, 'Expired or different continuation manifest')
    expected_files = {name: {'bytes': len(raw[name]), 'sha256': sha256(raw[name]).hexdigest()}
                      for name in (ORIGINALS_FILE, READER_FILE)}
    require(manifest['files'] == expected_files, 'Different continuation member bytes')
    data = parse(raw[ORIGINALS_FILE])
    result = evaluate_originals(data, context)
    return {'context': context, 'artifact': artifact['id'], 'digest': artifact['digest'],
            'result': result, 'expected_fresh': fresh_values(data, result)}


def arguments(parser):
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--tools', required=True)
    parser.add_argument('--reader-blob', required=True)
    parser.add_argument('--artifact', nargs=12, required=True,
                        metavar=('ID', 'NAME', 'BYTES', 'SHA256', 'CREATED', 'EXPIRES',
                                 'RUN', 'HEAD', 'REPO', 'HEAD_REPO', 'BRANCH', 'EXPIRED'))
    parser.add_argument('--collection', nargs=8, required=True,
                        metavar=('RUN', 'ATTEMPT', 'HEAD', 'BRANCH', 'PATH', 'REPO', 'STATUS', 'CONCLUSION'))
    parser.add_argument('--fresh', nargs=2, action='append', default=[], metavar=('SOURCE', 'VALUE'))
    parser.add_argument('--expect-draft', action='store_true')


def confirm_fresh(result, values):
    fresh = dict(values)
    expected = result['expected_fresh']
    for key in sorted(set(expected) | set(fresh)):
        require(key in expected and fresh.get(key) == expected[key], 'Fresh Connector observation differs: ' + key)
    require(len(fresh) == len(values), 'Duplicate fresh observation')


def continuation(argv):
    parser = argparse.ArgumentParser(description='Verify an Actions continuation ZIP. Use fresh Connector reads.')
    arguments(parser)
    args = parser.parse_args(argv)
    try:
        ident, name, size, checksum, created, expires, run, head, repo, origin, branch, expired = args.artifact
        artifact = dict(id=int(ident), name=name, size_in_bytes=int(size), digest=checksum, created_at=created,
                        expires_at=expires, expired={'true': True, 'false': False}[expired],
                        workflow_run=dict(id=int(run), head_sha=head, head_branch=branch,
                                          repository_id=int(repo), head_repository_id=int(origin)))
        run, attempt, head, branch, path, repo, status, conclusion = args.collection
        collection = dict(id=int(run), run_attempt=int(attempt), head_sha=head, head_branch=branch,
                          path=path, repository_id=int(repo), status=status, conclusion=conclusion)
        result = verify_continuation(args.archive, artifact, collection, tools=args.tools, reader_blob=args.reader_blob)
        fresh = dict(args.fresh)
        if not fresh:
            # The first call identifies the required observations. It grants no
            # continuation and omits the draft mutation and CI gate output.
            print(json.dumps({'status': 'read-live', 'context': result['context'],
                              'sources': sorted(result['expected_fresh']),
                              'request': result['result']['request'], 'pr': result['result']['pr'],
                              'release': result['expected_fresh']['release'].split(':', 1)[0],
                              'trigger_run': result['expected_fresh']['trigger'].split(':', 1)[0],
                              'worker_run': result['expected_fresh']['worker'].split(':', 1)[0],
                              'package_ci_workflow_id': result['result']['package_ci_workflow_id']}, sort_keys=True))
            return
        confirm_fresh(result, args.fresh)
        del result['expected_fresh']
        require(not args.expect_draft or result['result']['draft'] is True, 'Expected associated draft PR')
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    except (BadZipFile, KeyError, ValueError, TypeError, OSError) as exc:
        parser.exit(1, f'Continuation blocked: {exc}\n')


def main():
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'continuation':
        return continuation(sys.argv[2:])
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=argparse.FileType('rb'), help='JSON object of the original connector or REST responses')
    parser.add_argument('--expect-draft', action='store_true', help='Require draft on readback of a newly opened PR')
    args = parser.parse_args()
    try:
        result = evaluate(parse(args.input.read()))
        require(not args.expect_draft or result['draft'] is True, 'Expected the associated draft PR')
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    except (KeyError, ValueError, TypeError) as exc:
        parser.exit(1, f'PR/CI binding blocked: {exc}\n')


if __name__ == '__main__':
    main()
