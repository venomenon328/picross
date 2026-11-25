"""Run one closed PW request using trusted main tools. The request is data, never a command."""
import argparse
from contextlib import contextmanager
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from time import monotonic

from . import work_refs, production_remote_delivery as delivery
from . import production_git_workspace as ws, production_remote_pr as prs, publish_git as git, work_publish as pw
from .production_workspace.sources import check_commit
from .puzzle_production import catalog_io as io, current_authoring as current, github_rest
from .puzzle_production.authoring_package import require, sha
from .puzzle_production.contract import digest, exact_keys, integer

WORKFLOW = 'pw-remote.yml'
LIMIT = 60000
TOOLS = Path(__file__).resolve().parents[1]


def validate_editorial(data):
    if 'choice' in data:
        change = exact_keys(data['choice'], {'candidate', 'motif_sha256', 'approved', 'declaration'})
        sha(change['motif_sha256'])
        decision = change['declaration']
        exact_keys(decision, {'actor', 'statement', 'timestamp_utc'} | ({'crop_protection'} & decision.keys()))
        current.human(decision)
        require(isinstance(change['approved'], list) and change['approved'], 'Actual approved parameters required')
    else:
        change = exact_keys(data['assessment'], {'candidate', 'definition_sha256', 'preview_sha256', 'review',
                                                'observations', 'ready'})
        for key in ('definition_sha256', 'preview_sha256'):
            sha(change[key])
        current.findings.check_summaries(change['review'], current.CRITERIA['raster'])
        require(type(change['ready']) is bool and isinstance(change['observations'], list), 'Invalid raster inspection')
    current.identifier(change['candidate'])


def request(value):
    common = {'format', 'repository', 'job', 'operation', 'expected', 'record_sha256', 'tools', 'main', 'input'}
    require(isinstance(value, dict), 'Expected PW remote request')
    op = value.get('operation')
    require(op in ('step3', 'step4', 'step5', 'status', 'retire', 'continue', *delivery.READS), 'Unknown PW operation')
    v2 = value.get('format') == delivery.WIRE_V2
    extra = {'product', 'pr'} if op in ('inspect-product', 'status', 'retire') else {'issue'} if op == 'step5' else set()
    if v2 and op in ('step3', 'step4') and 'delivery' in value:
        extra.add('delivery')
    exact_keys(value, common | extra)
    require((value['format'] == 'pw-remote-v1' and op != 'continue'
             or v2 and op in ('inspect', 'step3', 'step4', 'step5', 'continue'))
            and value['repository'] == pw.REPO, 'Different format or repository')
    require(len(current.encoded(value)) <= LIMIT, 'Oversized remote request')
    current.path(value['job'])
    for field in ('expected', 'tools', 'main'):
        check_commit(value[field])
    require(value['tools'] == value['main'], 'Worker tools must be the bound main revision')
    sha(value['record_sha256'])
    data = value['input']
    if 'product' in extra:
        check_commit(value['product'])
        integer(value['pr'], 1, 2**53-1, 'product PR')
    if op in delivery.READS:
        delivery.selectors(value)
    elif op == 'step3' and isinstance(data, dict) and set(data) in ({'choice'}, {'assessment'}):
        validate_editorial(data)
    elif op == 'step3' and isinstance(data, dict) and len(data) == 1:
        from .production_remote_raster import validate
        validate(data)
        require(v2 or 'protection' not in data.get('fixed', {}), 'Combined protection requires pw-remote-v2')
    elif op == 'step3':
        exact_keys(data, {'motif_sha256', 'design', 'profile', 'label'})
        sha(data['motif_sha256'])
        require(data['profile'] in ('line', 'paired'), 'Unknown proof profile')
        current.text(data['label'], 'raster label', 512)
        design = data['design']
        require(isinstance(design, dict) and isinstance(design.get('variants'), list) and
                len(design['variants']) == 1, 'One explicitly selected candidate per attempt')
        if 'delivery' in value:
            require(isinstance(design['variants'][0], dict), 'Expected an explicitly named import result')
            current.identifier(design['variants'][0].get('id'))
    elif op == 'step4':
        require(isinstance(data, dict) and set(data) in ({'prepare'}, {'assessment'}), 'Expected background preparation or assessment')
        if 'prepare' in data:
            ids = data['prepare']
            require(isinstance(ids, list) and 0 < len(ids) <= 100, 'Expected offered background IDs')
            for candidate in ids:
                current.identifier(candidate)
            require(len(set(ids)) == len(ids), 'Duplicate background candidate')
        else:
            change = exact_keys(data['assessment'], {'candidate', 'original_sha256', 'sha256', 'profile', 'review', 'observations'})
            current.identifier(change['candidate'])
            sha(change['original_sha256'])
            sha(change['sha256'])
            current.findings.check_summaries(change['review'], current.CRITERIA['background'])
            require(isinstance(change['observations'], list), 'Invalid background observations')
    elif op == 'continue':
        exact_keys(data, {'kind', 'trigger', 'worker'})
        require(data['kind'] in ('publication', 'ci') and
                (data['trigger'] is None) == (data['worker'] is None), 'Invalid continuation source')
        if data['worker'] is not None:
            for key in ('trigger', 'worker'):
                integer(data[key], 1, 2**53-1, key + ' run')
    elif op == 'step5':
        if not v2 or value['issue'] is not None:
            integer(value['issue'], 1, 2**53-1, 'product issue')
        require(isinstance(data, dict), 'Expected finalization input')
        optional = {'finding_decisions'} & data.keys()
        exact_keys(data, {'background', 'decisions'} | optional)
        declarations = data.get('finding_decisions', [])
        require(isinstance(declarations, list) and len(declarations) <= 128, 'Invalid finding declarations')
        seen = set()
        for row in declarations:
            exact_keys(row, {'target', 'id', 'expected', 'action', 'treatment', 'actor', 'timestamp_utc', 'statement'})
            sha(row['expected'])
            require(isinstance(row['target'], str) and isinstance(row['id'], str) and
                    (row['target'], row['id']) not in seen and row['action'] == 'accept', 'Invalid finding acceptance')
            seen.add((row['target'], row['id']))
            current.human(row)
        if data['background'] not in (None, 'none', 'standard'):
            current.identifier(data['background'])
        require(isinstance(data['decisions'], list) and len(data['decisions']) <= 3, 'Invalid final decisions')
        scopes = set()
        for d in data['decisions']:
            exact_keys(d, {'scope', 'actor', 'timestamp_utc', 'statement'} | ({'binding'} & d.keys()))
            require(d['scope'] in ('background', 'final', 'integration') and d['scope'] not in scopes,
                    'Unexpected final decision scope')
            scopes.add(d['scope'])
            if 'binding' in d:
                sha(d['binding'])
            current.human(d)
    else:
        exact_keys(data, set())
    if 'delivery' in value:
        delivery.result_selection(value)
    return value


def workflow(name):
    row = pw.api('actions/workflows/' + name)
    require(row['path'] == '.github/workflows/' + name and row['state'] == 'active'
            and type(row['id']) is int and row['id'] > 0, 'Required workflow unavailable: ' + name)
    return row['id']


def owner(commit, *, parent=None):
    row = pw.api('git/commits/' + commit)
    require(row['sha'] == commit and len(row['parents']) == 1 and
            (parent is None or row['parents'][0]['sha'] == parent), 'Different work or product generation')
    match = re.fullmatch(r'.+\n\nPW-Remote: ([a-f0-9]{64})\n?', row['message'])
    require(match, 'Commit is not bound to this remote operation')
    return match[1]


def preflight(root, req, auth):
    op, job, expected = req['operation'], req['job'], req['expected']
    if op in delivery.READS:
        from .production_remote_inspect import bound
        bound(root, req)
        return {'request': digest(req), 'work_head': expected, 'main': req['main'], 'operation': op}
    require(git.remote_head(root, 'refs/heads/main') == req['main'], 'Stale main or tool binding')
    operation = 'retire' if op == 'retire' else 'resume' if op == 'status' else 'publish'
    observed = pw.observe(root, operation, job, expected, pw.REPO, auth)
    require(observed['main'] == req['main'], 'Stale main')
    original = pw.remote_record(expected, job)
    require(sha256(original).hexdigest() == req['record_sha256'], 'Pinned record hash differs')
    record = pw.bound_record(original, job)
    require(not work_refs.FIXTURE or job == work_refs.TEST_JOB and record['test_only'] is True,
            'Expected the bound test-only fixture')
    work = observed['work_head']
    request_id = digest(req)
    product = git.remote_head(root, 'refs/heads/' + prs.product_branch(job))
    lock = git.remote_head(root, 'refs/heads/' + pw.release_catalog.LOCK_BRANCH)
    ci = workflow(prs.WORKFLOW) if op not in ('step3', 'step4') else None
    worker = workflow(WORKFLOW)
    if op in ('step3', 'step4', 'step5') and work != expected:
        require(work and owner(work, parent=expected) == request_id, 'Work changed outside this request')
        record = pw.bound_record(pw.remote_record(work, job), job)
    if op == 'step3' and 'design' in req['input']:
        data = req['input']
        motif = next((a for a in record['assets'] if a['id'] == record['selected']['motif']), None)
        require(motif and motif['file']['sha256'] == data['motif_sha256'], 'Selected motif bytes changed')
    if op == 'step3' and work == expected and not {'assessment', 'choice', 'design'}.intersection(req['input']):
        from .production_remote_raster import check_published
        check_published(next(iter(req['input'].values())), record)
    if op == 'step5':
        if record['format'] in current.findings.FORMATS:
            qualification = record.get('qualification')
            require(qualification is not None and all(current.qualification.documented(row)
                    for row in qualification['facts'].values()),
                    'Bound candidate qualification missing. Complete the affected production phase first.')
        if req['issue'] is not None:
            issue = pw.api('issues/' + str(req['issue']))
            require(issue['number'] == req['issue'] and 'pull_request' not in issue, 'Expected production issue')
        existing = prs.lookup(job)
        if work == expected:
            require(product is None and existing is None, 'Occupied product branch or PR')
        else:
            require(record['state'] == 'registered' and product == record['integration']['commit']
                    and owner(product, parent=req['main']) == request_id, 'Different completed product')
            if existing:
                prs.associated(req, existing, product, request_id)
    if op in ('status', 'retire'):
        require(record['state'] == 'registered' and record['integration']['commit'] == req['product']
                and (product == req['product'] or op == 'retire' and product is None),
                'Work record and expected product generation differ')
        pr_owner = owner(req['product'], parent=req['main'] if op == 'status' else None)
        prs.associated(req, pw.api('pulls/' + str(req['pr'])), req['product'], pr_owner, merged=op == 'retire')
    return {**observed, 'auth_source': os.environ.get('PW_REMOTE_AUTH_KIND') or auth,
            'request': request_id, 'record_sha256': req['record_sha256'], 'tool_commit': req['tools'],
            'product': product, 'worker': worker, 'package_ci': ci, 'catalog_lease': 'occupied' if lock else 'free',
            'transport': {'invocation': 'expected-new request ref; verify upstream push and Main worker',
                          'originals': 'bound Git and release assets; hashes checked at resume',
                          'refs': 'Git expected-ref push and readback', 'product_pr': 'GitHub REST; write unverified',
                          'ci': 'PR Package CI; actual attempt required', 'retirement': 'generation-bound release and Git refs'}}


@contextmanager
def measured(timings, key):
    start = monotonic()
    try:
        yield
    finally:
        timings[key] = round((timings[key] or 0) + monotonic() - start, 3)


def retire(root, req, auth, token):
    # A fresh process needs the pinned Git objects, even after the work ref was removed.
    base, db = ws.store_for(root, pw.REPO)
    git.git(db, 'fetch', '--no-tags', '--', git.REMOTE, req['expected'], req['main'])
    pr = pw.api('pulls/' + str(req['pr']))
    prs.associated(req, pr, req['product'], owner(req['product']), merged=True)
    ws.git(db, 'merge-base', '--is-ancestor', pr['merge_commit_sha'], req['main'])
    require(git.remote_head(db, 'refs/heads/main') == req['main'], 'Refresh confirmed main before retirement')
    data = ws.open_tree(base, db, 'job-' + req['job'], req['expected'], req['job'], 'job')
    return pw.finish(data, req['job'], req['expected'], auth=auth, token=token)


def run(root, req, auth, token, *, diagnose=False, recover_delivery=False, check_invocation=lambda: None):
    request(req)
    require(req['operation'] != 'continue', 'Send the continuation to the Actions reader')
    require(not recover_delivery or 'delivery' in req, 'Recovery requires the original v2 request with delivery')
    require(ws.git(TOOLS, 'rev-parse', 'HEAD') == req['tools'] and not ws.changes(TOOLS),
            'Execute from the clean, explicitly pinned trusted tool checkout')
    times = dict.fromkeys(('queue', 'bootstrap', 'fetch_originals', 'computation', 'publication', 'ci', 'wait'))
    with pw.publisher_auth(auth, token), current.qualification.operation():
        with measured(times, 'fetch_originals'):
            report = preflight(root, req, auth)
        if diagnose:
            return {**report, 'seconds': times}
        require(req['operation'] not in delivery.READS, 'Submit a bound Actions request for binary delivery')
        job, expected, op = req['job'], req['expected'], req['operation']
        req_id = report['request']
        result = {'request': req_id, 'repository': pw.REPO, 'job': job, 'operation': op, 'expected': expected,
                  'main': req['main'], 'tools': req['tools'], 'record_sha256': req['record_sha256'], 'seconds': times}
        if op == 'status':
            pr = pw.api('pulls/' + str(req['pr']))
            prs.associated(req, pr, req['product'], owner(req['product'], parent=req['main']))
            with measured(times, 'ci'):
                result.update(prs.ci_status(req, pr, report['package_ci']))
            return result
        # The private local root may recover its own nonce. A fresh runner cannot claim a remote lease.
        area = io.safe(root, 'pw-' + req_id[:16])
        if not recover_delivery:
            try:
                area.mkdir(mode=0o700)
            except FileExistsError:
                pass
            else:
                from .puzzle_production.authoring_builder import write_new
                write_new(area / 'request-id', req_id.encode())
        require(io.read(area, 'request-id', 64, missing=recover_delivery) == req_id.encode(),
                'Original private request directory required')
        if op == 'retire':
            with measured(times, 'publication'):
                check_invocation()
                status = retire(area, req, auth, token)
            return {**result, 'status': status, 'next': 'Retirement verified against confirmed main.'}
        work, product = report['work_head'], report['product']
        replay_delivery = 'delivery' in req and work != expected
        replay_step5 = op == 'step5' and req['format'] == delivery.WIRE_V2 and work != expected
        replay = replay_delivery or replay_step5
        intent = None
        if io.safe(area, 'picross-production').exists():
            base, db = ws.store_for(area, pw.REPO)
            data = io.safe(base, 'job-' + job)
            if data.exists():
                binding = ws.read_binding(data)
                require(binding and binding['role'] == 'job' and binding['job'] == job and Path(binding['store']) == db,
                        'Foreign local operation directory')
                state = ws.gitdir(data)
                pending = (state / pw.JOURNAL).exists()
                if not replay or pending:
                    raw = io.read(state, 'pw-remote-intent.json', 4096, missing=not pending or not replay)
                    if raw:
                        intent = exact_keys(io.json_bytes(raw, 4096), {'id', 'main', 'product'})
                        require(intent['id'] == req_id and intent['main'] == req['main']
                                and (op == 'step5' or intent['product'] is None), 'Different private operation intent')
        require(not recover_delivery or replay_delivery and intent,
                'Resume the pushed successor with its original private intent and pending publisher journal')
        local_owner = intent and (ws.gitdir(data) / 'work-production-catalog-owner').is_file()
        require(report['catalog_lease'] == 'free' or local_owner,
                'Catalog lease occupied. Owning operator must resume with the original private worktree and journal.')
        if intent:
            product = intent['product']
            if product is not None:
                ws.check_product(data, job, product)
            with measured(times, 'publication'):
                check_invocation()
                work = pw.push_job(data, job, expected, auth=auth, token=token,
                                   remote_request={**intent, 'recover_pushed': True} if replay else intent)
        elif work == expected:
            with measured(times, 'bootstrap'):
                paths = ws.prepare(area, job, req['tools'], req['main'], expected,
                                   integration=prs.product_branch(job) if op == 'step5' else None)
            data = Path(paths['job'])
            with measured(times, 'fetch_originals'):
                pw.resume(data, job, expected, auth=auth, token=token)
            original = io.json_bytes(io.read(data, current.path(job), current.LIMIT), current.LIMIT)
            from . import production_remote_steps as steps
            with measured(times, 'computation'), tempfile.TemporaryDirectory(dir=paths['temporary']) as tmp:
                if op == 'step3':
                    result.update(steps.step3(req, original, data, Path(tmp)))
                elif op == 'step4':
                    result.update(steps.step4(req, original, data, Path(tmp)))
                else:
                    product = steps.step5(req, req_id, original, data, Path(paths['integration']), Path(tmp))
            if result.get('status') in ('no-op', 'diagnosed'):
                check_invocation()
                require(preflight(root, req, auth)['work_head'] == expected, 'Read-only raster source changed')
                return {**result, 'work': expected}
            with measured(times, 'publication'):
                check_invocation()
                intent = {'id': req_id, 'main': req['main'], 'product': product if op == 'step5' else None}
                current._atomic(ws.gitdir(data), 'pw-remote-intent.json', current.encoded(intent))
                work = pw.push_job(data, job, expected, auth=auth, token=token, remote_request=intent)
        require(git.remote_head(root, 'refs/heads/content/pw/' + job) == work and
                owner(work, parent=expected) == req_id, 'Work publication not confirmed')
        published = pw.remote_record(work, job)
        pw.verify_published_assets(root, job, expected, work, published)
        result.update(work=work, published_record_sha256=sha256(published).hexdigest(), status='published',
                      next='Inspect the published raster offer.')
        if 'delivery' in req:
            prior = pw.bound_record(pw.remote_record(expected, job), job)
            record = pw.bound_record(published, job)
            result['deliver'] = delivery.result_available(req, prior, record)
        if op == 'step3' and 'choice' in req['input']:
            result['next'] = 'Read the approved motif and parameters for the raster design.'
        if op == 'step3' and 'assessment' in req['input']:
            result['next'] = 'Read the published assessments and present the current offers or inspection drafts.'
        if op == 'step3' and 'select' in req['input']:
            result['next'] = 'Continue with background offers in step 4.'
        if op == 'step4':
            result['next'] = ('Inspect the bound original and prepared PNG of each candidate.'
                              if 'prepare' in req['input'] else 'Read the current background assessments.')
        if op == 'step5':
            completed = pw.bound_record(published, job)
            require(completed['state'] == 'registered' and completed['integration']['commit'] == product,
                    'Published Completion does not bind the product commit')
            require(git.remote_head(root, 'refs/heads/main') == req['main'] and
                    git.remote_head(root, 'refs/heads/' + prs.product_branch(job)) == product and
                    owner(product, parent=req['main']) == req_id, 'Product publication not confirmed on bound basis')
            with measured(times, 'publication'):
                check_invocation()
                if req['format'] == delivery.WIRE_V2:
                    metadata = prs.draft_metadata(req, req_id)
                    pr = prs.product_pr(req, product, req_id, actor=True)
                    return {**result, 'status': 'pr-bound' if pr else 'pr-ready', 'head': product,
                            'pr': pr['number'] if pr else None, 'draft_pr': metadata,
                            'next': 'Read the published generation and bind the product PR through the connector.'}
                try:
                    pr = prs.product_pr(req, product, req_id, create=True)
                except github_rest.Failure as exc:
                    if exc.status != 403 or os.environ.get('PW_REMOTE_AUTH_KIND') != 'workflow-token':
                        raise
                    return {**result, 'status': 'pr-access-required', 'head': product,
                            'next': 'The invoking actor must repeat this request with its authorized PR identity.'}
            with measured(times, 'ci'):
                result.update(prs.ci_status(req, pr, report['package_ci']))
        return result


PREFIX = 'work-prod-control/remote/'
TITLE = 'PW remote request v1'


def envelope(req, mode):
    require(mode in ('preflight', 'execute') and (req.get('operation') != 'continue' or mode == 'execute'),
            'Invalid request mode')
    value = {'mode': mode, 'request': request(req)}
    name = PREFIX + req['job'] + '/' + digest(value)
    message = TITLE + '\n\n' + current.encoded(value).decode().rstrip('\n')
    return name, message


def submit(root, req, mode):
    name, message = envelope(req, mode)
    ref = 'refs/heads/' + name
    require(git.remote_head(root, 'refs/heads/main') == req['main'], 'Request main changed')
    existing = git.remote_head(root, ref)
    if existing is None:
        tree = ws.git(root, 'rev-parse', req['main'] + '^{tree}')
        candidate = git.git(root, 'commit-tree', tree, '-p', req['main'], data=message.encode()).decode().strip()
        git.publish(root, name, candidate, None)
    else:
        candidate = existing
    verify_request(root, name, candidate, req['main'])
    return {'status': 'submitted', 'ref': name, 'commit': candidate, 'request': digest(req),
            'next': 'Read the Working ref publication check and its PW remote workflow_run.'}


def verify_request(root, name, source, main):
    require(isinstance(name, str) and re.fullmatch(PREFIX + r'pz-[a-z0-9][a-z0-9-]{0,59}/[0-9a-f]{64}', name),
            'Unexpected remote request namespace')
    check_commit(source)
    check_commit(main)
    require(git.remote_head(root, 'refs/heads/main') == main and
            git.remote_head(root, 'refs/heads/' + name) == source, 'Request withdrawn, replaced or stale')
    commit = pw.api('git/commits/' + source)
    parent = pw.api('git/commits/' + main)
    require(commit['sha'] == source and parent['sha'] == main and commit['tree']['sha'] == parent['tree']['sha']
            and [p['sha'] for p in commit['parents']] == [main], 'Request must contain only the unchanged Main tree')
    title, separator, body = commit['message'].partition('\n\n')
    require(title == TITLE and separator and len(body.encode()) <= LIMIT, 'Invalid request envelope')
    value = exact_keys(io.json_bytes(body.encode(), LIMIT), {'mode', 'request'})
    req, mode = request(value['request']), value['mode']
    canonical_name, canonical_message = envelope(req, mode)
    require(req['main'] == main and canonical_name == name and commit['message'].rstrip('\n') == canonical_message,
            'Request digest, canonical bytes or tool revision differs')
    return req, mode


def event_request(root):
    require(os.environ.get('GITHUB_EVENT_NAME') == 'workflow_run' and os.environ.get('GITHUB_REPOSITORY') == pw.REPO
            and os.environ.get('GITHUB_REF') == 'refs/heads/main'
            and os.environ.get('GITHUB_WORKFLOW_REF') == f'{pw.REPO}/.github/workflows/{WORKFLOW}@refs/heads/main',
            'Trusted default-branch worker required')
    event = io.json_bytes(Path(os.environ['GITHUB_EVENT_PATH']).read_bytes(), 1024 * 1024)
    run = event['workflow_run']
    main = os.environ['GITHUB_SHA']
    require(event['action'] == 'completed' and event['repository']['full_name'] == pw.REPO
            and run['repository']['full_name'] == run['head_repository']['full_name'] == pw.REPO
            and run['path'] == '.github/workflows/work-growth.yml' and run['event'] == 'push'
            and run['conclusion'] == 'success' and main == os.environ['GITHUB_WORKFLOW_SHA'], 'Unexpected worker trigger')
    req, mode = verify_request(root, run['head_branch'], run['head_sha'], main)
    return req, mode, 'refs/heads/' + run['head_branch'], run['head_sha']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('preflight', 'execute', 'recover', 'submit', 'worker', 'worker-preflight',
                                          'route', 'inspect-stage', 'inspect-verify', 'inspect-ack'))
    parser.add_argument('--root', type=Path, default=Path.cwd(), help='Existing private work root for this actor')
    parser.add_argument('--auth', choices=pw.AUTH_SOURCES, default='env')
    parser.add_argument('--diagnose-only', action='store_true', help='Submit a read-only capability request')
    args = parser.parse_args()
    try:
        token = pw.select_token(args.auth)
        for key in github_rest.TOKEN_NAMES:
            os.environ.pop(key, None)
        root = io.external(args.root)
        require(root.is_dir(), 'Existing private work root required')
        with pw.publisher_auth(args.auth, token):
            if args.action not in ('preflight', 'execute', 'recover', 'submit'):
                req, mode, ref, source = event_request(root)
                diagnose = args.action == 'worker-preflight' or mode == 'preflight'
                def check_invocation():
                    require(git.remote_head(root, ref) == source and git.remote_head(root, 'refs/heads/main') == req['main'],
                            'Invocation withdrawn or main advanced before publication')
                if args.action == 'route' or args.action.startswith('inspect-'):
                    from . import production_remote_inspect as inspect
                    require(ws.git(TOOLS, 'rev-parse', 'HEAD') == req['tools'] and not ws.changes(TOOLS),
                            'Clean pinned tool checkout required')
                    if args.action == 'route':
                        if req['operation'] == 'continue':
                            require(mode == 'execute', 'Continuation is already read-only')
                            outputs({'route': 'continue'})
                            print(json.dumps({'route': 'continue'}, sort_keys=True))
                            return
                        reading = req['operation'] in delivery.READS
                        if reading:
                            _, record, _ = inspect.bound(root, req)
                        result = {'route': 'read' if reading else 'write', 'mode': mode}
                        if reading and mode == 'execute':
                            result['artifact'] = delivery.artifact_name(inspect.github_context(req, source))
                            derived = {spec['derive'] for spec in delivery.sources(req, record)}
                            result['images'] = str(bool(derived - {None})).lower()
                            result['cells'] = str('cells-clues' in derived).lower()
                            if result['cells'] == 'true':
                                from .production_remote_view import cache_key
                                result['editor_key'] = cache_key(req['repository'])
                        outputs(result)
                    else:
                        result = inspect.process(args.action, root, req, mode, ref, source, check_invocation)
                        if args.action == 'inspect-stage' and 'delivery' in req:
                            outputs({'artifact': result['artifact']})
                    print(json.dumps(result, sort_keys=True))
                    return
                require(req['operation'] not in (*delivery.READS, 'continue'), 'Reader request sent to the product writer')
                result = run(root, req, args.auth, token, diagnose=diagnose, check_invocation=check_invocation)
                if args.action == 'worker-preflight':
                    if mode == 'execute' and req['operation'] != 'status':
                        require(result['catalog_lease'] == 'free',
                                'Catalog lease occupied. Resume from the owning private journal before starting a new runner.')
                    images = (mode == 'execute' and req['operation'] != 'status'
                              and not (('delivery' in req or req['operation'] == 'step5'
                                        and req['format'] == delivery.WIRE_V2)
                                       and result['work_head'] != req['expected']))
                    outputs({'images': str(images).lower()})
                else:
                    handoff = result.get('deliver', False)
                    if handoff:
                        cells = any(i['role'] == 'cells-clues' for i in req['delivery'])
                        values = {'deliver': 'true', 'cells': str(cells).lower()}
                        if cells:
                            from .production_remote_view import cache_key
                            values['editor_key'] = cache_key(req['repository'])
                        outputs(values)
                        result['next'] = 'Publication confirmed. Verify delivery in this run or rerun the bound request.'
                    else:
                        check_invocation()
                        pw.delete_ref(TOOLS, ref, source)
                        result['request_ref_removed'] = True
                        if (mode == 'execute' and req['operation'] == 'step5' and req['format'] == delivery.WIRE_V2
                                and result.get('status') in ('pr-ready', 'pr-bound')):
                            outputs({'continuation': 'true'})
                        if 'delivery' in req and mode == 'execute':
                            result['next'] = 'No requested result was published. Inspect an existing candidate separately.'
            else:
                req = request(io.json_bytes(sys.stdin.buffer.read(LIMIT + 1), LIMIT))
                if args.action == 'submit':
                    pw.repository_check(pw.REPO)
                    result = submit(TOOLS, req, 'preflight' if args.diagnose_only else 'execute')
                else:
                    require(req['operation'] != 'continue' and (args.action != 'execute' or 'delivery' not in req),
                            'Submit result delivery through Actions')
                    result = run(root, req, args.auth, token, diagnose=args.action == 'preflight',
                                 recover_delivery=args.action == 'recover')
        print(json.dumps(result, sort_keys=True))
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        message = str(exc) if isinstance(exc, ValueError) else type(exc).__name__
        parser.exit(1, f'PW remote blocked: {message}. Read back the bound work, product and PR. '
                       'For an interrupted lease resume only from its owning private journal.\n')


def outputs(values):
    with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as out:
        for key, value in values.items():
            print(key + '=' + value, file=out)


if __name__ == '__main__':
    main()
