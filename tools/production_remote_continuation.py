"""Collect Step 5 and PR CI originals from the trusted read-only Actions job."""
import argparse
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from time import sleep
from urllib.parse import urlencode, urlsplit
from urllib.request import ProxyHandler, Request, build_opener

from . import production_remote as remote, production_remote_reader as reader, work_publish as publisher
from .production_remote_inspect import download_uploaded
from .puzzle_production import github_rest

require = reader.require


def paged(api, endpoint, field=None, *, query=None):
    """Read complete REST pages, checking totals where the endpoint supplies one."""
    pages = []
    for number in range(1, 101):
        params = {**(query or {}), 'per_page': 100, 'page': number}
        row = api(endpoint + '?' + urlencode(params))
        pages.append(row)
        items = row[field] if field else row
        if field and sum(len(page[field]) for page in pages) >= row['total_count']:
            reader.pages(pages, field)
            return pages
        if len(items) < 100:
            require(field is None, f'Incomplete paged {field}')
            return pages
    raise ValueError('Too many original pages: ' + endpoint)


def invocation(commit):
    _, separator, payload = commit['message'].rstrip('\n').partition('\n\n')
    require(separator, 'Expected a bound Step 5 invocation')
    envelope = reader.parse(payload)
    req = remote.request(envelope['request'])
    require(envelope['mode'] == 'execute' and req['format'] == 'pw-remote-v2'
            and req['operation'] == 'step5', 'Expected an executed v2 Step 5 invocation')
    return req


def locate(api, main, job, owner, explicit):
    if explicit:
        return tuple(explicit)

    # A lost chat need not remember the run IDs. Start from the immutable
    # owner trailer of the published product, then match the original trigger.
    prefix = 'PW remote ' + remote.PREFIX + job + '/'
    query = {'event': 'workflow_run', 'branch': 'main', 'head_sha': main, 'status': 'completed'}
    runs = reader.pages(paged(api, 'actions/workflows/pw-remote.yml/runs', 'workflow_runs', query=query),
                        'workflow_runs')
    checked = {}
    matches = []
    for run in runs:
        title = run['display_title']
        if not title.startswith(prefix) or not reader.DIGEST.fullmatch(title[len(prefix):]):
            continue
        branch = title.removeprefix('PW remote ')
        if branch not in checked:
            triggers = reader.pages(paged(api, 'actions/workflows/work-growth.yml/runs', 'workflow_runs',
                query={'event': 'push', 'branch': branch, 'status': 'success'}), 'workflow_runs')
            candidates = []
            for trigger in triggers:
                commit = api('git/commits/' + trigger['head_sha'])
                _, _, body = commit['message'].rstrip('\n').partition('\n\n')
                envelope = reader.parse(body)
                if reader.digest(envelope['request']) == owner and remote.PREFIX + job + '/' + reader.digest(envelope) == branch:
                    candidates.append(trigger)
            require(len(candidates) <= 1, 'Ambiguous original Step 5 trigger; supply the independently bound run IDs')
            checked[branch] = candidates[0] if candidates else None
        trigger = checked[branch]
        if trigger and trigger['run_started_at'] <= run['created_at']:
            matches.append((trigger['id'], run['id']))
    require(len(matches) == 1, 'Cannot identify a unique original Step 5 run; supply the independently bound run IDs')
    return matches[0]


class LogRedirect(github_rest.NoRedirect):
    """Return GitHub's redirect so its download can use a separate client."""

    def http_error_302(self, request, response, code, message, headers):
        return response


def log_location(job_id):
    require(type(job_id) is int and job_id > 0, 'Expected an Actions job ID')
    return signed_location(f'actions/jobs/{job_id}/logs')


def signed_location(endpoint):
    token = github_rest.publisher_token()
    require(token, 'Expected the Actions read credential')
    url = f'{github_rest.API}/{endpoint}'
    with github_rest.open_api(url, {'Accept': 'application/vnd.github+json'}, timeout=30,
                              token=token, redirect=LogRedirect()) as response:
        locations = response.headers.get_all('Location', [])
        require(response.status == 302 and len(locations) == 1, 'Expected one HTTP 302 download location')
        location, = locations
    # The signed URL is an ephemeral credential. Accept only the dedicated
    # HTTPS log storage host; never include the URL in errors or follow it again.
    try:
        target = urlsplit(location)
    except ValueError:
        raise ValueError('Invalid Actions log download location') from None
    require(target.scheme == 'https' and re.fullmatch(r'[a-z0-9]{3,24}\.blob\.core\.windows\.net', target.netloc)
            and target.path.startswith('/') and target.query and not target.fragment
            and not re.search(r'[\s\x00-\x1f\x7f\\]', location), 'Invalid Actions log download location')
    return location


def signed_opener():
    return build_opener(ProxyHandler({}), github_rest.NoRedirect())


def original_log(job_id):
    limit = 8 * 1024**2
    for delay in (0, 2, 5, 10):
        if delay:
            sleep(delay)
        stage = 'GitHub API'
        try:
            location = log_location(job_id)
            stage = 'signed download'
            # This opener has no GitHub credentials, proxies or redirect handler
            # capable of forwarding a signed URL to another origin.
            http = signed_opener()
            with github_rest.transport_errors():
                with http.open(Request(location), timeout=30) as response:
                    require(response.status == 200, 'Expected HTTP 200 for the Actions log')
                    raw = response.read(limit + 1)
            require(0 < len(raw) <= limit, 'Missing or oversized Actions log')
            return raw.decode('utf-8')
        except github_rest.Failure as exc:
            if delay < 10 and (exc.status in (404, 502, 503, 504)
                               or stage == 'signed download' and exc.status == 403
                               or exc.kind == 'network' and exc.status is None):
                continue
            detail = f'HTTP {exc.status}' if exc.status is not None else exc.kind
        except UnicodeError:
            detail = 'invalid UTF-8'
        except ValueError:
            detail = 'invalid response'
        raise ValueError(f'Cannot read original Step 5 worker job log {job_id} ({stage}: {detail})') from None


def worker_originals(api, trigger_id, worker_id, read_log):
    trigger = api(f'actions/runs/{trigger_id}')
    run = api(f'actions/runs/{worker_id}')
    require(trigger['id'] == trigger_id and run['id'] == worker_id
            and type(run['run_attempt']) is int and run['run_attempt'] > 0,
            'Different trigger or worker run ID')
    attempt_path = f'actions/runs/{worker_id}/attempts/{run["run_attempt"]}'
    attempt = api(attempt_path)
    jobs = paged(api, attempt_path + '/jobs', 'jobs')
    workers = [job for job in reader.pages(jobs, 'jobs') if job['name'] == 'worker']
    require(len(workers) == 1 and reader.matching_fields(workers[0], {
        'run_id': worker_id, 'run_attempt': run['run_attempt'], 'head_sha': run['head_sha'],
        'status': 'completed', 'conclusion': 'success'}), 'No successful Step 5 worker job in that attempt')
    job = workers[0]
    raw = read_log(job['id'])
    relevant = [reader.worker_log_row(raw, job['steps'], step, field, original=True)
                for step, field in ((reader.PREFLIGHT_STEP, 'package_ci'),
                                    (reader.PUBLISH_STEP, 'published_record_sha256'))]
    return {'trigger': trigger, 'run': run, 'attempt': attempt, 'jobs': jobs,
            'job_id': job['id'], 'log': '\n'.join(relevant) + '\n'}


def ci_originals(api, job, pr, workflow_id):
    query = {'event': 'pull_request', 'branch': reader.product_branch(job), 'head_sha': pr['head']['sha']}
    pages = paged(api, f'actions/workflows/{workflow_id}/runs', 'workflow_runs', query=query)
    evidence = {'repository_runs': pages}
    runs = reader.pages(pages, 'workflow_runs')
    if not runs:
        return evidence
    latest = max(runs, key=lambda row: row['run_number'])
    path = f'actions/runs/{latest["id"]}'
    attempt_path = path + f'/attempts/{latest["run_attempt"]}'
    evidence.update(run=api(path), attempt=api(attempt_path))
    if evidence['attempt']['status'] == 'completed' and evidence['attempt']['conclusion'] != 'action_required':
        evidence['jobs'] = paged(api, attempt_path + '/jobs', 'jobs')
        merge = pr.get('merge_commit_sha')
        if reader.SHA.fullmatch(merge or ''):
            evidence['test_merge'] = api('git/commits/' + merge)
    return evidence


def collect(api, repository, main, job, run_id, attempt, *, source=None, control=None, read_log=original_log):
    require(reader.SHA.fullmatch(main) and reader.JOB.fullmatch(job), 'Unbound collection source')
    require(not remote.work_refs.FIXTURE or job == remote.work_refs.TEST_JOB, 'Different isolated fixture job')
    repo = api('')
    require(repo['full_name'] == repository and repo['id'] == reader.REPOSITORIES[repository],
            'Different collection repository')
    main_ref = api('git/ref/heads/main')
    require(reader.ref(main_ref, 'heads/main') == main, 'Stale Main: use the bound recovery path')
    work_branch = 'content/pw/' + job
    branch = reader.product_branch(job)
    work_ref, product_ref = (api('git/ref/heads/' + name) for name in (work_branch, branch))
    work, product = (reader.ref(row, 'heads/' + name)
                     for row, name in ((work_ref, work_branch), (product_ref, branch)))
    work_commit, product_commit = (api('git/commits/' + oid) for oid in (work, product))
    owner = reader.owner(product_commit, product, main)
    if control is None:
        trigger, worker = source
        kind = 'publication'
    else:
        require(work == control['expected'], 'Continuation work ref changed')
        options = control['input']
        explicit = (options['trigger'], options['worker']) if options['worker'] is not None else None
        trigger, worker = locate(api, main, job, owner, explicit)
        kind = options['kind']
    evidence = worker_originals(api, trigger, worker, read_log)
    request_sha = evidence['trigger']['head_sha']
    require(reader.SHA.fullmatch(request_sha), 'Invalid Step 5 request SHA')
    request_commit = api('git/commits/' + request_sha)
    req = invocation(request_commit)
    require(req['job'] == job and req['main'] == main and reader.digest(req) == owner,
            'Stale Step 5 basis or different publication owner; use the bound recovery path')
    path = 'contents/' + remote.current.path(job)
    original = api(path + '?ref=' + req['expected'])
    completion = api(path + '?ref=' + work)
    raw = reader.record_bytes(completion, repository, work, path.removeprefix('contents/'))
    record = publisher.bound_record(raw, job)
    if remote.work_refs.FIXTURE:
        require(record['test_only'] is True, 'Expected an isolated fixture record')
    if control is not None:
        require(reader.sha256(raw).hexdigest() == control['record_sha256'], 'Continuation record bytes changed')
    release_id = record['work_release']['id']
    tag = 'work-prod-' + job
    release = api(f'releases/{release_id}')
    asset_pages = paged(api, f'releases/{release_id}/assets')
    pulls = api(reader.pr_query(repository, job))
    active = api('actions/workflows/' + reader.WORKFLOW)
    data = dict(repository=repo, main_ref=main_ref, main_commit=api('git/commits/' + main),
                request_sha=request_sha, request_commit=request_commit, work_ref=work_ref, work_commit=work_commit,
                input_record=original, completion_record=completion, step5_worker=evidence, product_ref=product_ref,
                product_commit=product_commit, product_diff=api(f'compare/{main}...{product}?per_page=100&page=1'),
                work_tag=api('git/ref/tags/' + tag), release=release, release_asset_pages=asset_pages,
                pulls=pulls, active_workflow=active,
                workflow_file=api('contents/' + reader.WORKFLOW_PATH + '?ref=' + main))
    pr = reader.pr_slot(pulls)
    if pr:
        data['pr'] = api(f'pulls/{pr["number"]}')
    if kind == 'ci':
        require(pr is not None, 'Read the actual associated product PR before collecting CI')
        data['ci'] = ci_originals(api, job, data['pr'], active['id'])
    context = dict(repository_id=repo['id'], tools=main, job=job, request_sha=request_sha,
                   kind=kind, run=run_id, attempt=attempt)
    reader.evaluate_originals(data, context)
    return context, data


def stage(output, context, data, code, now):
    files = {reader.ORIGINALS_FILE: (reader.canonical(data) + '\n').encode(), reader.READER_FILE: code}
    # Actions reports its retention deadline at second precision and can
    # timestamp it just before the runner's staging clock.
    expires = now.replace(microsecond=0) + timedelta(hours=23, minutes=59)
    manifest = dict(format=reader.FORMAT, purpose=reader.PURPOSE, context=context,
                    expires=expires.isoformat(),
                    files={name: {'bytes': len(raw), 'sha256': reader.sha256(raw).hexdigest()}
                           for name, raw in files.items()})
    files['manifest.json'] = (reader.canonical(manifest) + '\n').encode()
    require(all(0 < len(raw) <= reader.MEMBER_LIMITS[name] for name, raw in files.items()),
            'Continuation original exceeds its byte limit')
    output.mkdir()
    for name, raw in files.items():
        (output / name).write_bytes(raw)
    return manifest


def collection_read(api, run_id):
    row = api(f'actions/runs/{run_id}')
    return {**row, 'repository_id': row['repository']['id']}


def verify_upload(root, context, tools_blob):
    ident = int(os.environ['PW_ARTIFACT_ID'])
    name = reader.artifact_name(context)
    for delay in (0, 2, 5, 10):
        if delay:
            sleep(delay)
        try:
            row = publisher.api(f'actions/artifacts/{ident}')
        except github_rest.Failure as exc:
            if exc.status == 400:
                rows = publisher.api(f'actions/runs/{context["run"]}/artifacts?name=' + name)['artifacts']
                matches = [item for item in rows if item['id'] == ident]
                require(len(matches) == 1, 'Cannot identify the uploaded continuation ZIP')
                row, = matches
                break
            if delay == 10 or exc.status not in (404, 502, 503, 504):
                raise
        else:
            break
    require(row['id'] == ident and row['digest'] == 'sha256:' + os.environ['PW_ARTIFACT_DIGEST'].removeprefix('sha256:'),
            'Upload and Actions artifact metadata differ')
    with tempfile.TemporaryDirectory(dir=root) as temp:
        archive = Path(temp) / 'continuation.zip'
        download_uploaded(ident, archive, size=row['size_in_bytes'])
        run = collection_read(publisher.api, context['run'])
        result = reader.verify_continuation(archive, row, run, tools=context['tools'],
                                            reader_blob=tools_blob, staging=True)
        require(result['context'] == context, 'Uploaded context differs from staged continuation')
    return {'artifact': ident, 'name': name, 'bytes': row['size_in_bytes'], 'sha256': row['digest'],
            'expires': row['expires_at'], 'run': context['run'], 'attempt': context['attempt']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['stage', 'verify', 'ack'])
    parser.add_argument('--root', type=Path, required=True)
    args = parser.parse_args()
    try:
        token = publisher.select_token('GH_TOKEN')
        for name in github_rest.TOKEN_NAMES:
            os.environ.pop(name, None)
        root = remote.io.external(args.root)
        require(root.is_dir() and os.environ['GITHUB_EVENT_NAME'] == 'workflow_run'
                and os.environ['GITHUB_REPOSITORY'] == publisher.REPO
                and os.environ['GITHUB_REF'] == 'refs/heads/main'
                and os.environ['GITHUB_WORKFLOW_REF'] == f'{publisher.REPO}/.github/workflows/pw-remote.yml@refs/heads/main',
                'Expected the trusted Main continuation job')
        main = os.environ['GITHUB_SHA']
        require(main == os.environ['GITHUB_WORKFLOW_SHA']
                and remote.ws.git(remote.TOOLS, 'rev-parse', 'HEAD') == main
                and not remote.ws.changes(remote.TOOLS), 'Expected clean pinned collector tools')
        event = reader.parse(Path(os.environ['GITHUB_EVENT_PATH']).read_bytes())
        trigger = event['workflow_run']
        require(event['action'] == 'completed' and event['repository']['full_name'] == publisher.REPO
                and event['repository']['id'] == reader.REPOSITORIES[publisher.REPO]
                and trigger['path'] == '.github/workflows/work-growth.yml' and trigger['event'] == 'push'
                and trigger['conclusion'] == 'success', 'Unexpected continuation trigger')
        directory = root / 'pw-continuation'
        with publisher.publisher_auth('GH_TOKEN', token):
            if args.action == 'verify':
                manifest = reader.parse((directory / 'manifest.json').read_bytes())
                blob = remote.ws.git(remote.TOOLS, 'rev-parse', 'HEAD:tools/' + reader.READER_FILE)
                print(json.dumps(verify_upload(root, manifest['context'], blob), sort_keys=True))
                return
            control = None
            job = trigger['head_branch'].split('/')[-2]
            if os.environ['PW_COLLECTION_ROUTE'] == 'continue' or args.action == 'ack':
                control, mode, ref, source = remote.event_request(root)
                require(mode == 'execute' and control['operation'] == 'continue', 'Expected read-only continuation request')
                if args.action == 'ack':
                    publisher.delete_ref(remote.TOOLS, ref, source)
                    return
                job = control['job']
            run_id = int(os.environ['GITHUB_RUN_ID'])
            attempt = int(os.environ['GITHUB_RUN_ATTEMPT'])
            ctx, data = collect(publisher.api, publisher.REPO, main, job, run_id, attempt,
                                source=(trigger['id'], run_id), control=control)
            # Use the exact committed bytes, even when a checkout uses CRLF.
            code = remote.git.git(remote.TOOLS, 'show', 'HEAD:tools/' + reader.READER_FILE)
            stage(directory, ctx, data, code, datetime.now(timezone.utc))
            remote.outputs({'artifact': reader.artifact_name(ctx)})
            print(json.dumps({'artifact': reader.artifact_name(ctx), 'purpose': reader.PURPOSE}, sort_keys=True))
    except (OSError, ValueError, TypeError, KeyError, subprocess.SubprocessError) as exc:
        parser.exit(1, f'PW continuation blocked: {exc}. Read back the work and product refs before retrying.\n')


if __name__ == '__main__':
    main()
