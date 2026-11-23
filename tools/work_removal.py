"""Complete the release-only part of a Git-confirmed P2 request on trusted main."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re

from . import publish_git as transport, work_publish
from .production_workspace import repository as pw
from .production_workspace.release_channel import GitHub, app_catalog_writer
from .puzzle_production import github_rest
from .puzzle_production.authoring_package import require


def request_event(event):
    run = event['workflow_run']
    repo = work_publish.REPO
    require(event['action'] == 'completed' and event['repository']['full_name'] == repo
            and run['head_repository']['full_name'] == repo and run['repository']['full_name'] == repo
            and run['path'] == '.github/workflows/work-growth.yml' and run['event'] == 'push'
            and run['conclusion'] == 'success', 'Unexpected removal trigger')
    name, source = run['head_branch'], run['head_sha']
    match = re.fullmatch(re.escape(pw.REMOVAL_PREFIX) + r'(pz-[a-z0-9][a-z0-9-]{0,59})/([0-9a-f]{40})/[0-9a-f]{32}', name)
    require(match and transport.SHA.fullmatch(source), 'Invalid removal request')
    return name, source, match[1], match[2]


def service(root, event, api):
    name, main, job, expected = request_event(event)
    require(transport.git(root, 'rev-parse', 'HEAD').decode().strip() == main,
            'Worker must execute the triggering main commit')
    ref = 'refs/heads/' + name
    branch = 'content/pw/' + job
    created = datetime.fromisoformat(event['workflow_run']['created_at'])
    receipt = pw.removal_receipt(expected, main)

    def check_live():
        age = (datetime.now(timezone.utc) - created).total_seconds()
        require(0 <= age < 600 and transport.remote_head(root, 'refs/heads/main') == main
                and transport.remote_head(root, ref) == main
                and transport.remote_head(root, 'refs/heads/' + branch) == expected,
                'Request expired, withdrawn or superseded')
        prs = pw.ProductionRemoval.pull_requests(branch, token=api.token)
        require(not any(row['state'] == 'open' for row in prs)
                and pw.removal_request(job, expected, main, prs) == name,
                'Pull request facts changed')

    def update_request(new):
        transport.git(root, '-c', 'credential.helper=', '-c', 'credential.helper=!gh auth git-credential',
                      'push', '--no-follow-tags', '--no-verify', '--recurse-submodules=no',
                      '--force-with-lease=' + ref + ':' + main, '--', transport.REMOTE, new + ':' + ref)

    try:
        check_live()
        with app_catalog_writer(api, main), github_rest.use_publisher_token(api.token):
            work_publish.remove_bound_release(root, job, expected, main, confirmed=True, before_delete=check_live)
            check_live()
            # Only acknowledge. The installed client owns work/tag ref removal.
            update_request(receipt)
    finally:
        # A rejected run wakes the waiting client. A lost response to a
        # successful receipt push must not revoke that receipt.
        if transport.remote_head(root, ref) == main:
            update_request('')


if __name__ == '__main__':
    require(os.environ['GITHUB_REPOSITORY'] == work_publish.REPO and os.environ['GITHUB_REF'] == 'refs/heads/main'
            and os.environ['GITHUB_EVENT_NAME'] == 'workflow_run', 'Trusted default-branch workflow required')
    service(Path.cwd(), json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_bytes()), GitHub(os.environ['GH_TOKEN']))
