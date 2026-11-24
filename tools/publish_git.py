"""Check the exact outgoing history before sending Git objects to origin."""
import argparse
import base64
from contextlib import contextmanager
from contextvars import ContextVar
import json
import os
import re
import subprocess
from pathlib import Path

try:
    from .ci_growth import forbidden, SHA
    from .work_refs import CLEAN_MAIN, REPOSITORY
except ImportError:
    from ci_growth import forbidden, SHA
    from work_refs import CLEAN_MAIN, REPOSITORY

GITHUB_REMOTE = 'https://github.com/' + REPOSITORY + '.git'
REMOTE = GITHUB_REMOTE
_remote_token = ContextVar('git_remote_token', default=None)


@contextmanager
def use_remote_token(token):
    scope = _remote_token.set(token)
    try:
        yield
    finally:
        _remote_token.reset(scope)


def check_push_url(command, env):
    try:
        values = subprocess.run([*command, 'config', '-z', '--get-regexp', r'^url\..*\.pushinsteadof$'],
                                env=env, capture_output=True, timeout=15)
    except (OSError, subprocess.SubprocessError):
        raise ValueError('Git push destination could not be verified; inspect the Git configuration') from None
    if values.returncode not in (0, 1):
        raise ValueError('Git push destination could not be verified; inspect the Git configuration')
    for entry in values.stdout.split(b'\0'):
        _, separator, prefix = entry.partition(b'\n')
        if separator and GITHUB_REMOTE.encode().startswith(prefix):
            raise ValueError('Git push destination may be rewritten; inspect matching pushInsteadOf configuration')

def git(root, *args, data=None):
    command = ['git', '--no-replace-objects', '--no-lazy-fetch', '-C', str(root)]
    token = _remote_token.get()
    if not token or REMOTE not in args:
        return subprocess.check_output([*command, *args], input=data)
    # Resolve rewrites without giving Git any publisher credential. The fixed
    # URL is the only destination allowed to receive it.
    env = {k: v for k, v in os.environ.items()
           if not k.upper().startswith(('GIT_', 'GH_', 'GITHUB_TOKEN'))}
    if REMOTE == GITHUB_REMOTE and ('push' in args or args[-1] == 'refs/heads/main'):
        check_push_url(command, env)
    try:
        target = subprocess.check_output([*command, 'ls-remote', '--get-url', REMOTE],
                                         env=env, stderr=subprocess.PIPE, timeout=15).decode().strip()
    except (OSError, subprocess.SubprocessError, UnicodeError):
        raise ValueError('Git destination could not be verified; inspect the Git configuration') from None
    if target != REMOTE:
        raise ValueError('Git destination differs from the configured publisher repository; inspect URL rewrites')
    config = [('core.hooksPath', os.devnull), ('credential.helper', ''), ('core.askPass', ''),
              ('http.followRedirects', 'false'), ('http.sslVerify', 'true'), ('http.extraHeader', '')]
    if REMOTE == GITHUB_REMOTE:
        env['GIT_ALLOW_PROTOCOL'] = 'https'
        header = base64.b64encode(('x-access-token:' + token).encode('ascii')).decode('ascii')
        key = 'http.' + GITHUB_REMOTE + '.extraHeader'
        config.extend([(key, ''), (key, 'Authorization: Basic ' + header)])
    env.update(GIT_CONFIG_COUNT=str(len(config)), GIT_TERMINAL_PROMPT='0', GCM_INTERACTIVE='never')
    for idx, (key, value) in enumerate(config):
        env[f'GIT_CONFIG_KEY_{idx}'] = key
        env[f'GIT_CONFIG_VALUE_{idx}'] = value
    try:
        return subprocess.check_output([*command, *args], input=data, env=env, stderr=subprocess.PIPE, timeout=180)
    except subprocess.CalledProcessError as exc:
        # Git, helpers and remote hooks may return sensitive text. Classify it
        # locally and only report the operation and a fixed recovery message.
        error = (exc.stderr or b'').lower()
        operation = next((word for word in args if word in ('ls-remote', 'fetch', 'push')), 'remote')
        if b'401' in error or b'authentication failed' in error:
            detail = 'authentication failed; verify the selected GitHub credential'
        elif any(marker in error for marker in (b'403', b'permission', b'not found', b'denied')):
            detail = 'access refused; check the concrete Git ref operation in the selected context'
        elif any(marker in error for marker in (b'stale info', b'rejected', b'non-fast-forward')):
            detail = 'ref update refused; read back the ref and check its expected generation'
        elif b'429' in error or b'rate limit' in error:
            detail = 'rate limited; wait before retrying after checking the ref'
        else:
            detail = 'transport failed; check the connection and read back the ref before retrying'
        raise ValueError(f'Git {operation}: {detail}') from None
    except (OSError, subprocess.TimeoutExpired):
        raise ValueError('Git transport unavailable or timed out; check the connection and read back the ref') from None


def check_range(root, head, bases, *, anchor=None):
    anchor = anchor or CLEAN_MAIN
    if git(root, 'rev-parse', '--is-shallow-repository').strip() != b'false':
        raise ValueError('Complete Git history required')
    partial = subprocess.run(['git', '-C', str(root), 'config', '--get-regexp',
                              r'^(extensions\.partialclone|remote\..*\.(promisor|partialclonefilter))$'],
                             capture_output=True)
    if partial.returncode != 1:
        raise ValueError('Full object database required for pre-publication verification')
    if not bases or not all(SHA.fullmatch(x) for x in [head, anchor, *bases]):
        raise ValueError('Full source and boundary commits required')
    git(root, 'merge-base', '--is-ancestor', anchor, head)
    commits = git(root, 'rev-list', '--reverse', head, '--not', *bases).decode().splitlines()
    sizes = {}
    paths = set()
    for commit in commits:
        # Including every side parent prevents grafting a pre-rewrite lineage.
        git(root, 'merge-base', '--is-ancestor', anchor, commit)
        entries = git(root, 'diff-tree', '-r', '--no-renames', '--no-abbrev', '--raw',
                      '-z', '--no-commit-id', commit + '^1', commit).split(b'\0')
        for meta, name in zip(entries[0:-1:2], entries[1::2], strict=True):
            _, mode, _, oid, status = meta.decode().split()
            if status == 'D':
                continue
            path = name.decode('utf-8')
            reason = forbidden(path)
            if reason:
                raise ValueError(f'{commit} {path}: {reason}')
            if mode not in ('100644', '100755', '120000'):
                raise ValueError('Unsupported Git object at ' + path)
            paths.add(path)
            if oid not in sizes:
                sizes[oid] = int(git(root, 'cat-file', '-s', oid))
            if path.startswith('content/authoring/') and path.endswith('.json'):
                if mode != '100644' or sizes[oid] > (8 if path.endswith('/index.json') else 1) * 1024**2:
                    raise ValueError('Invalid production metadata ' + path)
                value = json.loads(git(root, 'cat-file', 'blob', oid))
                if path.endswith('/current/record.json') and value.get('format') not in ('picross-authoring-current-v2', 'picross-authoring-current-v3'):
                    raise ValueError('Only externally bound current records can be published')
    return {'commits': len(commits), 'changed_paths': len(paths), 'blobs': len(sizes), 'bytes': sum(sizes.values())}


def remote_head(root, ref):
    raw = git(root, 'ls-remote', '--refs', '--', REMOTE, ref).decode().splitlines()
    if not raw:
        return None
    oid, actual = raw[0].split('\t')
    if len(raw) != 1 or actual != ref or not SHA.fullmatch(oid):
        raise ValueError('Ambiguous remote binding')
    return oid


def publish(root, branch, head, expected, *, api=False):
    ref = 'refs/heads/' + branch
    git(root, 'check-ref-format', ref)
    if branch == 'main' or branch.startswith('-'):
        raise ValueError('Expected an owned work branch')
    main = remote_head(root, 'refs/heads/main')
    actual = remote_head(root, ref)
    if actual != expected or not main:
        raise ValueError('Remote changed; refresh before publishing')
    bases = [main] + ([actual] if actual else [])
    git(root, 'fetch', '--no-tags', '--no-write-fetch-head', '--', REMOTE, *bases)
    git(root, 'merge-base', '--is-ancestor', CLEAN_MAIN, main)
    if actual:
        git(root, 'merge-base', '--is-ancestor', CLEAN_MAIN, actual)
        git(root, 'merge-base', '--is-ancestor', actual, head)
    report = check_range(root, head, bases)
    if actual == head:
        return head
    if api:
        # GraphQL creates a single regular-file commit with a server-side parent lease.
        if not actual or git(root, 'show', '-s', '--format=%P', head).decode().strip() != actual:
            raise ValueError('API publication requires one commit on an existing branch')
        additions, deletions = [], []
        rows = git(root, 'diff', '--no-renames', '--name-status', '-z', actual, head).split(b'\0')[:-1]
        for status, name in zip(rows[::2], rows[1::2], strict=True):
            path = name.decode()
            if status == b'D':
                deletions.append({'path': path})
            else:
                if git(root, 'ls-tree', head, '--', path).split()[0] != b'100644':
                    raise ValueError('API publication supports regular files only')
                raw = git(root, 'show', head + ':' + path)
                additions.append({'path': path, 'contents': base64.b64encode(raw).decode()})
        message = git(root, 'show', '-s', '--format=%B', head).decode().strip().partition('\n')
        payload = {'query': 'mutation($input:CreateCommitOnBranchInput!){createCommitOnBranch(input:$input){commit{oid}}}',
                   'variables': {'input': {'branch': {'repositoryNameWithOwner': REPOSITORY, 'branchName': branch},
                                 'expectedHeadOid': actual, 'message': {'headline': message[0], 'body': message[2]},
                                 'fileChanges': {'additions': additions, 'deletions': deletions}}}}
        response = subprocess.check_output(['gh', 'api', '--hostname', 'github.com', 'graphql', '--input', '-'], input=json.dumps(payload).encode())
        result = json.loads(response)['data']['createCommitOnBranch']['commit']['oid']
        if not SHA.fullmatch(result):
            raise ValueError('Invalid API commit response')
        git(root, 'fetch', '--no-tags', '--no-write-fetch-head', '--', REMOTE, result)
        if (git(root, 'rev-parse', result + '^{tree}') != git(root, 'rev-parse', head + '^{tree}') or
                git(root, 'show', '-s', '--format=%P', result).decode().strip() != actual):
            raise ValueError('API commit differs from inspected tree or expected parent')
    else:
        git(root, '-c', 'push.followTags=false', 'push', '--no-verify', '--no-follow-tags', '--recurse-submodules=no',
            '--force-with-lease=' + ref + ':' + (expected or ''), '--', REMOTE, head + ':' + ref)
        result = head
    if remote_head(root, ref) != result:
        raise ValueError('Remote publication not confirmed')
    print(json.dumps(report))
    return result


def publish_completion(root, job, work, expected, product, main):
    """Both refs become visible together, including after a lost push response."""
    from .puzzle_production.current_authoring import path
    path(job)
    work_ref = 'refs/heads/content/pw/' + job
    product_ref = 'refs/heads/content/integrate-' + job
    if (not all(isinstance(oid, str) and SHA.fullmatch(oid) for oid in (work, expected, product, main))
            or git(root, 'show', '-s', '--format=%P', work).decode().strip() != expected
            or git(root, 'show', '-s', '--format=%P', product).decode().strip() != main):
        raise ValueError('Completion requires one bound work commit and one product commit on main')
    check_range(root, work, [main, expected])
    check_range(root, product, [main])
    if (remote_head(root, 'refs/heads/main') != main or remote_head(root, work_ref) != expected
            or remote_head(root, product_ref) is not None):
        raise ValueError('Completion refs changed before atomic publication')
    git(root, 'push', '--atomic', '--no-follow-tags', '--no-verify', '--recurse-submodules=no',
        '--force-with-lease=' + work_ref + ':' + expected, '--force-with-lease=' + product_ref + ':',
        '--', REMOTE, work + ':' + work_ref, product + ':' + product_ref)
    if remote_head(root, work_ref) != work or remote_head(root, product_ref) != product:
        raise ValueError('Read back both completion refs before retrying')
    return work


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('branch')
    parser.add_argument('--expected', required=True, help='Remote commit, or new')
    parser.add_argument('--head', default='HEAD')
    parser.add_argument('--api', action='store_true')
    args = parser.parse_args()
    head = git('.', 'rev-parse', '--verify', '--end-of-options', args.head + '^{commit}').decode().strip()
    print(publish(Path.cwd(), args.branch, head, None if args.expected == 'new' else args.expected, api=args.api))


if __name__ == '__main__':
    main()
