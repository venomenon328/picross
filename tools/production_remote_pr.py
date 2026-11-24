"""Read back a single job's product PR and its actual Package CI attempt."""
from urllib.parse import urlencode

from . import publish_git as git, work_publish as pw
from .puzzle_production.authoring_package import require

WORKFLOW = 'ci-modular.yml'


def product_branch(job):
    return 'content/integrate-' + job


def marker(job, request_id):
    return f'<!-- picross-production {job} {request_id} -->'


def associated(req, pr, head, owner, *, merged=False):
    branch = product_branch(req['job'])
    require(type(pr.get('number')) is int and pr['number'] > 0 and
            (req.get('pr') is None or req['pr'] == pr['number']) and
            pr['head']['repo']['full_name'] == pr['base']['repo']['full_name'] == pw.REPO and
            pr['head']['ref'] == branch and pr['head']['sha'] == head and
            pr['base']['ref'] == 'main' and marker(req['job'], owner) in (pr['body'] or '').splitlines(),
            'Foreign product PR or changed head')
    if merged:
        require(pr['state'] == 'closed' and pr['merged'] is True and pr['merged_at']
                and git.SHA.fullmatch(pr.get('merge_commit_sha') or ''), 'Verified merged product PR required')
    else:
        require(pr['state'] == 'open' and pr['base']['sha'] == req['main'], 'Product PR closed or basis changed')
    return pr


def lookup(job):
    query = urlencode({'head': pw.REPO.split('/')[0] + ':' + product_branch(job),
                       'state': 'all', 'per_page': 2})
    rows = pw.api('pulls?' + query)
    require(isinstance(rows, list) and len(rows) <= 1, 'Ambiguous product PR ownership')
    return rows[0] if rows else None


def product_pr(req, head, owner, *, create=False):
    branch = product_branch(req['job'])
    row = lookup(req['job'])
    if row is None:
        require(create, 'Expected product PR missing')
        # After a lost response, the lookup is authoritative. Never POST twice here.
        try:
            pw.api('pulls', 'POST', {'head': branch, 'base': 'main', 'draft': True,
                   'title': 'Rätsel integrieren · ' + req['job'],
                   'body': marker(req['job'], owner) + '\n\nProduktintegration für #' + str(req['issue']) + '.'})
        except (ValueError, OSError):
            row = lookup(req['job'])
            if row is None:
                raise
        else:
            row = lookup(req['job'])
    require(row is not None, 'PR creation not confirmed; repeat the same request')
    return associated(req, pw.api('pulls/' + str(row['number'])), head, owner)


def ci_status(req, pr, workflow_id):
    head = pr['head']['sha']
    branch = product_branch(req['job'])
    merge = pr.get('merge_commit_sha')
    result = {'pr': pr['number'], 'url': f'https://github.com/{pw.REPO}/pull/{pr["number"]}',
              'head': head, 'base': req['main'], 'test_merge': merge, 'checks': {},
              'next': 'Read the bound product PR again after GitHub schedules its Package CI.'}
    if pr.get('mergeable') is False or pr.get('mergeable_state') == 'dirty':
        return {**result, 'status': 'conflict', 'next': 'Resolve the changed product basis.'}
    query = urlencode({'event': 'pull_request', 'branch': branch, 'head_sha': head, 'per_page': 1})
    runs = pw.api(f'actions/workflows/{workflow_id}/runs?' + query)['workflow_runs']
    if not runs:
        return {**result, 'status': 'missing-ci'}
    run = runs[0]
    require(run['workflow_id'] == workflow_id and run['event'] == 'pull_request' and
            run['path'] == '.github/workflows/' + WORKFLOW and
            run['head_repository']['full_name'] == run['repository']['full_name'] == pw.REPO and
            run['head_sha'] == head and run['head_branch'] == branch and
            type(run['id']) is int and run['id'] > 0 and type(run['run_attempt']) is int and run['run_attempt'] > 0,
            'Foreign CI run or source')
    result.update(run=run['id'], attempt=run['run_attempt'], run_url=f'https://github.com/{pw.REPO}/actions/runs/{run["id"]}')
    if run['status'] in ('action_required', 'waiting', 'requested') or run['conclusion'] == 'action_required':
        return {**result, 'status': 'approval-or-start-pending', 'next': 'Inspect Actions approval and the PR trigger identity.'}
    if run['status'] != 'completed' or not git.SHA.fullmatch(merge or ''):
        return {**result, 'status': 'pending'}
    jobs = pw.api(f'actions/runs/{run["id"]}/attempts/{run["run_attempt"]}/jobs?per_page=100')
    rows = jobs['jobs']
    require(len(rows) == jobs['total_count'] and all(j['run_id'] == run['id'] and j['head_sha'] == head
            for j in rows), 'Incomplete or foreign CI jobs')
    # The optional attachment delivery job is present and skipped on ordinary PRs.
    attachment = [j for j in rows if j['name'] == 'review-attachment']
    require(len(attachment) <= 1 and all(j['conclusion'] == 'skipped' for j in attachment),
            'Unexpected evidence delivery on the product PR')
    rows = [j for j in rows if j['name'] != 'review-attachment']
    expected = {'docs', 'verify (source)', 'ci-required'}
    result['checks'] = {j['name']: j['conclusion'] for j in rows}
    if run['conclusion'] != 'success' or set(result['checks']) != expected or len(rows) != len(expected) or any(
            value != 'success' for value in result['checks'].values()):
        return {**result, 'status': 'checks-incomplete', 'next': 'Inspect the missing or unsuccessful Package CI jobs.'}
    docs = next(j for j in rows if j['name'] == 'docs')
    binding = f'PR {pr["number"]} / {head} / {req["main"]} / {merge}'
    require(any(s['name'] == binding and s['conclusion'] == 'success' for s in docs['steps']),
            'Package CI did not check this PR, head, basis and test merge')
    return {**result, 'status': 'checks-passed', 'next': 'Review the complete product diff and actual merge authorization.'}
