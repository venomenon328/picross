"""Read back a single job's product PR and its actual Package CI attempt."""
from urllib.parse import urlencode

from . import work_publish as pw
from . import production_remote_reader as reader
from .production_remote_reader import WORKFLOW, associated, draft_metadata, product_branch, require


def lookup(job):
    return reader.pr_slot(pw.api(reader.pr_query(pw.REPO, job)))


def product_pr(req, head, owner, *, create=False, actor=False):
    branch = product_branch(req['job'])
    row = lookup(req['job'])
    if row is None:
        if actor:
            return None
        require(create, 'Expected product PR missing')
        # After a lost response, the lookup is authoritative. Never POST twice here.
        try:
            pw.api('pulls', 'POST', {'head': branch, 'base': 'main', 'draft': True,
                   'title': 'Rätsel integrieren · ' + req['job'],
                   'body': reader.marker(req['job'], owner) + '\n\nProduktintegration für #' + str(req['issue']) + '.'})
        except (ValueError, OSError):
            row = lookup(req['job'])
            if row is None:
                raise
        else:
            row = lookup(req['job'])
    require(row is not None, 'PR creation not confirmed; repeat the same request')
    return associated(req, pw.api('pulls/' + str(row['number'])), head, owner)


def ci_status(req, pr, workflow_id):
    if pr.get('mergeable') is False or pr.get('mergeable_state') == 'dirty':
        return reader.gate(req, pr)
    head = pr['head']['sha']
    query = urlencode({'event': 'pull_request', 'branch': product_branch(req['job']),
                       'head_sha': head, 'per_page': 1})
    runs = pw.api(f'actions/workflows/{workflow_id}/runs?' + query)['workflow_runs']
    if not runs:
        return reader.gate(req, pr)
    run = runs[0]
    reader.validate_run(req, head, workflow_id, run)
    # Retain the compatibility transport for older requests. The connector
    # adds verified commit parents and a fresh specific attempt to this gate.
    if run['status'] != 'completed' or run['conclusion'] == 'action_required' or not reader.SHA.fullmatch(
            pr.get('merge_commit_sha') or ''):
        return reader.gate(req, pr, run)
    path = f'actions/runs/{run["id"]}/attempts/{run["run_attempt"]}/jobs?per_page=100'
    jobs = pw.api(path)
    require(len(jobs['jobs']) == jobs['total_count'], 'Incomplete CI jobs')
    return reader.gate(req, pr, run, jobs['jobs'])
