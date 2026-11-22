"""Prepare and verify a GitHub Connector publication without local network access."""
import argparse
import base64
import json
from pathlib import Path
from urllib.parse import quote

from .publish_git import REMOTE, SHA, check_range, git


REPOSITORY = REMOTE.removeprefix('https://github.com/').removesuffix('.git')
API = f'https://api.github.com/repos/{REPOSITORY}/git'


def oid(value):
    if not isinstance(value, str) or not SHA.fullmatch(value) or value == '0' * 40:
        raise ValueError('Expected a full nonzero Git SHA')
    return value


def ref_head(response, branch):
    name = 'refs/heads/' + branch
    obj = response['object']
    head = oid(obj['sha'])
    if (response['ref'] != name or response['url'] != f'{API}/{quote(name)}' or
            obj['type'] != 'commit' or obj['url'] != f'{API}/commits/{head}'):
        raise ValueError('Unexpected GitHub branch binding')
    return head


def require_absent(responses, branch):
    if not isinstance(responses, list):
        raise ValueError('Expected the GitHub matching refs response')
    for response in responses:
        name = response['ref'].removeprefix('refs/heads/')
        ref_head(response, name)
        if name == branch or name.startswith(branch + '/') or branch.startswith(name + '/'):
            raise ValueError('Branch already exists or conflicts with an existing ref')


def read_requests(branch):
    return {'main': f'{API}/ref/heads/main',
            'branch_refs': f'{API}/matching-refs/heads/{quote(branch)}',
            'branch': f'{API}/ref/heads/{quote(branch)}'}


def prepare(root, branch, head, observation, *, anchor=None):
    git(root, 'check-ref-format', 'refs/heads/' + branch)
    if not branch.startswith(('feat/', 'fix/', 'chore/', 'docs/')):
        raise ValueError('Expected an owned development work branch')
    require_absent(observation['branch_refs'], branch)
    main = ref_head(observation['main'], 'main')
    head = oid(head)
    report = check_range(root, head, [main], anchor=anchor)
    if (report['commits'] != 1 or
            git(root, 'show', '-s', '--format=%P', head).decode().strip() != main):
        raise ValueError('Connector publication requires one commit directly on the observed main')

    base_tree = oid(git(root, 'rev-parse', main + '^{tree}').decode().strip())
    tree = oid(git(root, 'rev-parse', head + '^{tree}').decode().strip())
    if tree == base_tree:
        raise ValueError('Empty publication')
    blobs, entries = {}, []
    rows = git(root, 'diff-tree', '--raw', '-r', '--no-renames', '--no-abbrev',
               '-z', '--no-commit-id', main, head).split(b'\0')[:-1]
    for meta, name in zip(rows[::2], rows[1::2], strict=True):
        old_mode, mode, _, new, status = meta[1:].decode().split()
        if status == 'D':
            mode, new = old_mode, None
        elif new not in blobs:
            content = git(root, 'cat-file', 'blob', new)
            blobs[oid(new)] = {'repository_full_name': REPOSITORY, 'encoding': 'base64',
                               'content': base64.b64encode(content).decode('ascii')}
        entries.append({'path': name.decode('utf-8'), 'mode': mode,
                        'type': 'commit' if mode == '160000' else 'blob', 'sha': new})
    message = git(root, 'show', '-s', '--format=%B', head).decode('utf-8').rstrip('\n')
    return {'branch': branch, 'head': head, 'main': main, 'report': report,
            'read': read_requests(branch), 'blobs': blobs,
            'tree': {'repository_full_name': REPOSITORY, 'base_tree_sha': base_tree, 'tree_elements': entries},
            'commit': {'repository_full_name': REPOSITORY, 'parent_sha': main, 'tree_sha': tree,
                       'message': message}}


def authorize_ref(root, branch, head, main, evidence, *, anchor=None):
    """Return the only allowed ref mutation after GitHub independently read the candidate."""
    if ref_head(evidence['main'], 'main') != oid(main):
        raise ValueError('Remote main changed during preparation')
    plan = prepare(root, branch, head, evidence, anchor=anchor)
    if evidence['blobs'] != {sha: sha for sha in plan['blobs']}:
        raise ValueError('GitHub blob SHAs do not match the inspected objects')
    expected = plan['commit']
    if evidence['tree_sha'] != expected['tree_sha']:
        raise ValueError('GitHub tree SHA does not match the complete inspected tree')
    candidate = oid(evidence['created_commit_sha'])
    commit = evidence['commit']
    if (commit['sha'] != candidate or commit['url'] != f'{API}/commits/{candidate}' or
            commit['tree']['sha'] != expected['tree_sha'] or
            [p['sha'] for p in commit['parents']] != [expected['parent_sha']] or
            commit['message'].rstrip('\n') != expected['message']):
        raise ValueError('GitHub commit differs from the inspected tree, parent or message')
    return {'repository_full_name': REPOSITORY, 'branch_name': branch, 'sha': candidate}


def verify_ref(request, response):
    if request['repository_full_name'] != REPOSITORY:
        raise ValueError('Unexpected authorized repository')
    head = ref_head(response, request['branch_name'])
    if head != request['sha']:
        raise ValueError('Remote publication not confirmed at the authorized SHA')
    return head


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('reads', 'prepare', 'authorize-ref', 'verify-ref'))
    parser.add_argument('branch')
    parser.add_argument('--input', type=Path, help='JSON input for the selected phase')
    parser.add_argument('--head', default='HEAD', help='Source commit for prepare and authorize-ref')
    parser.add_argument('--main', help='Full main SHA returned by prepare')
    args = parser.parse_args()
    if args.phase == 'reads':
        result = read_requests(args.branch)
    else:
        if args.input is None:
            parser.error('--input is required for ' + args.phase)
        data = json.loads(args.input.read_text(encoding='utf-8'))
        if args.phase in ('prepare', 'authorize-ref'):
            head = git('.', 'rev-parse', '--verify', '--end-of-options', args.head + '^{commit}').decode().strip()
        if args.phase == 'prepare':
            result = prepare('.', args.branch, head, data)
        elif args.phase == 'authorize-ref':
            if args.main is None:
                parser.error('--main is required for authorize-ref')
            result = authorize_ref('.', args.branch, head, args.main, data)
        else:
            if data['request']['branch_name'] != args.branch:
                raise ValueError('Authorized branch differs from the requested branch')
            result = {'remote_commit': verify_ref(data['request'], data['ref'])}
    print(json.dumps(result))


if __name__ == '__main__':
    main()
