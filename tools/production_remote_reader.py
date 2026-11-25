"""Offline Step 5 continuation and Package CI reader for original GitHub REST JSON."""
import argparse
from base64 import b64decode
from hashlib import sha1, sha256
import json
import re
from urllib.parse import urlencode

REPOSITORIES = {'venomenon328/picross': 1381196633, 'venomenon328/picross-remote-test': 1470169013}
WORKFLOW = 'ci-modular.yml'
WORKFLOW_PATH = '.github/workflows/' + WORKFLOW
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


def record_bytes(row, repository, commit, path):
    require(row['type'] == 'file' and row['path'] == path and row['encoding'] == 'base64'
            and row['url'] == f'https://api.github.com/repos/{repository}/contents/{path}?ref={commit}',
            'Expected exact record contents')
    raw = b64decode(''.join(row['content'].split()), validate=True)
    require(len(raw) == row['size'] and sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest() == row['sha'],
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
    original = record_bytes(data['input_record'], repository, expected, path)
    completed = record_bytes(data['completion_record'], repository, work, path)
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
                assets[asset['asset_id']] = ('original-' + value['sha256'], value['bytes'])
            for child in value.values():
                collect(child)
    collect(record)
    rows = release['assets']
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


def validate_run(req, head, workflow_id, run, *, repository_id=None):
    require(run['workflow_id'] == workflow_id and run['event'] == 'pull_request' and run['path'] == WORKFLOW_PATH
            and all(run[k]['full_name'] == req['repository'] and
                    (repository_id is None or run[k]['id'] == repository_id) for k in ('repository', 'head_repository'))
            and run['head_sha'] == head and run['head_branch'] == product_branch(req['job'])
            and all(type(run[k]) is int and run[k] > 0 for k in ('id', 'run_attempt')), 'Foreign CI run or source')


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


def ci_status(req, pr, evidence, repository_id):
    workflow = evidence['workflow']
    require(workflow['state'] == 'active' and workflow['path'] == WORKFLOW_PATH
            and type(workflow['id']) is int and workflow['id'] > 0, 'Different Package CI workflow')
    head = pr['head']['sha']
    runs = pages(evidence['runs'], 'workflow_runs')
    for run in runs:
        validate_run(req, head, workflow['id'], run, repository_id=repository_id)
        require(type(run['run_number']) is int and run['run_number'] > 0, 'Invalid run number')
    require(len({r['run_number'] for r in runs}) == len(runs), 'Ambiguous current PR run')
    if not runs:
        return gate(req, pr)
    selected = max(runs, key=lambda run: run['run_number'])
    current, attempt = evidence['run'], evidence['attempt']
    keys = ('id', 'run_number', 'run_attempt', 'status', 'conclusion')
    for row in (current, attempt):
        validate_run(req, head, workflow['id'], row, repository_id=repository_id)
        require(all(row[k] == selected[k] for k in keys), 'Changed CI run or attempt; refresh the original reads')
        require(all(p['number'] == pr['number'] for p in row['pull_requests']), 'Foreign PR in CI run')
    if attempt['status'] != 'completed' or attempt['conclusion'] == 'action_required':
        return gate(req, pr, attempt)
    return gate(req, pr, attempt, pages(evidence['jobs'], 'jobs'), merge_commit=evidence.get('test_merge'), strict=True)


def evaluate(data):
    req, pr, result = binding(data)
    if 'ci' in data:
        require(pr is not None, 'Read the bound PR before its CI')
        result['ci'] = ci_status(req, pr, data['ci'], REPOSITORIES[req['repository']])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=argparse.FileType('rb'), help='JSON object of the original REST responses')
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
