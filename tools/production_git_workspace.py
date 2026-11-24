"""Prepare owned, revision-bound sparse worktrees for one production job."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile

from . import publish_git as transport
from .puzzle_production import authoring_rulebook, catalog_io as io, current_authoring as current
from .puzzle_production import current_content as content, current_registration as registration
from .puzzle_production.authoring_builder import git_root, index_value, publish_directory, writer, write_new
from .puzzle_production.authoring_package import require
from .production_workspace.sources import GitSource, check_commit

REPO = 'venomenon328/picross'
OWNER = 'pw-local-owner.json'
BINDING = 'pw-local-worktree.json'
NORMS = ('AGENTS.md', *authoring_rulebook.PATHS, 'docs/tools/PW_B_CONTRACT.md',
         'docs/tools/PRODUCTION_GIT_WORKSPACE.md', 'docs/production/ZA1_ADAPTER.md',
         'docs/production/PUZZLE_INTEGRATION.md', 'docs/production/PUZZLE_PRODUCTION.md',
         'tools/puzzle_production/README.md')


def git(root, *args):
    return transport.git(root, '-c', 'core.hooksPath=' + os.devnull, *args).decode().strip()


def gitdir(root):
    return io.external(git(root, 'rev-parse', '--absolute-git-dir'))


def store_for(root, repository):
    root = io.external(root)
    require(root.is_dir() and repository == REPO, 'Expected existing work root and matching repository')
    base = io.safe(root, 'picross-production')
    owner = {'format': 'pw-local-store-v1', 'root': str(root), 'repository': repository}
    if not base.exists():
        with tempfile.TemporaryDirectory(dir=root, prefix='.pw-bootstrap-') as tmp:
            stage = Path(tmp) / 'store'
            stage.mkdir()
            write_new(stage / OWNER, current.encoded(owner))
            git(stage, 'init', '-q', '--bare', 'objects.git')
            db = stage / 'objects.git'
            git(db, 'config', 'extensions.worktreeConfig', 'true')
            git(db, 'config', '--worktree', 'core.bare', 'true')
            git(db, 'config', '--unset', 'core.bare')
            git(db, 'config', 'core.autocrlf', 'false')
            git(db, 'remote', 'add', 'origin', transport.REMOTE)
            (stage / 'tmp').mkdir()
            publish_directory(stage, base)
    require(io.read(base, OWNER, 4096) == current.encoded(owner), 'Foreign production workspace')
    db = io.safe(base, 'objects.git')
    require(gitdir(db) == db and git(db, 'rev-parse', '--is-bare-repository') == 'true'
            and git(db, 'remote', 'get-url', 'origin') == transport.REMOTE, 'Foreign production Git store')
    return base, db


def read_binding(root):
    if (root / '.git').is_dir():
        return None  # Managed worktrees always have a gitfile.
    state = gitdir(root)
    raw = io.read(state, BINDING, current.LIMIT, missing=True)
    if raw is None:
        return None
    value = io.json_bytes(raw, current.LIMIT)
    require(value['path'] == str(root) and value['repository'] == REPO
            and git_root(root) == io.external(value['store']), 'Worktree ownership differs')
    return value


def profile(db, commit, job, role):
    names = set(NORMS)
    if role == 'tools':
        # Imports and method freezes resolve relative to the trusted modules.
        return names | {'tools/*.py', 'tools/puzzle_production/', 'tools/production_workspace/',
                        'content/difficulty-method.json', 'content/categories.json'}
    names.update((*registration.SHARED, current.INDEX, current.path(job), '.gitattributes', '.gitignore'))
    source = GitSource(db)
    index = index_value(source.read(commit, current.INDEX, 8 * current.LIMIT))
    names.update(row['record'] for row in index['entries'])
    raw = source.read(commit, current.path(job), current.LIMIT, missing=True)
    if raw is not None:
        record = current.validate(io.json_bytes(raw, current.LIMIT))
        require(record['puzzle_id'] == job, 'Wrong job record')
        for ref in current.references(record):
            if 'asset' not in ref:
                names.add(ref['file'])
    registry = io.json_bytes(source.read(commit, content.REGISTRY, 8 * current.LIMIT), 8 * current.LIMIT)
    if any(entry['id'] == job for entry in registry['entries']):
        def selected(name, limit, *, missing=False):
            names.add(name)
            return source.read(commit, name, limit, missing)
        content.selected(None, registry, job, read=selected)
    return names


def changes(root):
    rows = transport.git(root, '--no-optional-locks', 'status', '--porcelain=v1', '-z', '--no-renames',
                         '--untracked-files=all', '--ignored=traditional').split(b'\0')
    return [(row[:2], row[3:].decode()) for row in rows if row]


def check_work(root, job, *, resumed=False):
    """Every exceptional local byte belongs to the current draft or its named originals."""
    name = current.path(job)
    raw = io.read(root, name, current.LIMIT, missing=True)
    refs = {}
    if raw:
        record = current.validate(io.json_bytes(raw, current.LIMIT))
        require(record['puzzle_id'] == job, 'Foreign local draft')
        refs = {r['file']: r for r in current.references(record) if current.own(job, r['file'])}
    for status, path in changes(root):
        require((status[:1] in (b' ', b'?', b'!') or resumed and path in (name, current.INDEX))
                and path in {name, current.INDEX, *refs},
                'Unknown staged, modified or untracked path: ' + path)
        if path in refs:
            ref = refs[path]
            require(io.file_hash(root, path, ref['bytes']) == ref['sha256'], 'Changed local original: ' + path)
    if not resumed:
        tree = GitSource(root)
        head = git(root, 'rev-parse', 'HEAD')
        before = tree.read(head, current.INDEX, 8 * current.LIMIT)
        after = io.read(root, current.INDEX, 8 * current.LIMIT)
        if before != after:
            index = index_value(before)
            index['entries'] = sorted([e for e in index['entries'] if e['record'] != name] +
                                      [{'puzzle_id': job, 'revision': 'current', 'record': name}],
                                      key=lambda r: (r['puzzle_id'], r['revision']))
            require(raw and after == current.encoded(index), 'Foreign authoring index edit')


def sparse_lines(db, commit, job, role):
    lines = set()
    for name in profile(db, commit, job, role):
        if role != 'tools':
            name = name.replace('[', r'\[').replace('*', r'\*').replace('?', r'\?')
        lines.add('/' + name)
    return sorted(lines)


def sparse_path(root):
    return io.external(git(root, 'rev-parse', '--path-format=absolute', '--git-path', 'info/sparse-checkout'))


def open_tree(base, db, leaf, commit, job, role, branch=None):
    path = io.safe(base, leaf)
    binding = {'repository': REPO, 'store': str(db), 'path': str(path), 'role': role,
               'job': job if role != 'tools' else None, 'branch': branch}
    if path.exists():
        owner = read_binding(path) if (path / '.git').is_file() else None
        require(owner and {k: owner.get(k) for k in binding} == binding, 'Foreign or incomplete worktree: ' + str(path))
        require(git(path, 'rev-parse', 'HEAD') == commit and
                git(path, 'rev-parse', '--abbrev-ref', 'HEAD') == (branch or 'HEAD'), 'Different worktree revision or branch')
        require(git(path, 'config', '--worktree', '--bool', 'core.sparseCheckout') == 'true', 'Expected sparse worktree')
        if role == 'job':
            check_work(path, job)
        else:
            require(not changes(path), 'Unexpected files in ' + role + ' worktree')
        active = sparse_path(path).read_text(encoding='utf-8').splitlines()
        needed = sparse_lines(db, commit, job, role)
        prior = owner['patterns']
        expanded = sorted(set(prior) | set(needed))
        require(sorted(active) in (prior, expanded), 'Sparse profile changed outside this workspace')
        if expanded != prior:
            # Add only newly bound paths. Reject an existing working file at a
            # new target before Git updates the profile. Never narrow a profile.
            additions = sorted(set(expanded) - set(prior))
            if sorted(active) == prior:
                for line in additions:
                    name = line[1:].replace(r'\[', '[')
                    require(not io.safe(path, name).exists(), 'Occupied sparse extension: ' + name)
                transport.git(path, 'sparse-checkout', 'add', '--stdin', data=('\n'.join(additions) + '\n').encode())
            require(sorted(sparse_path(path).read_text(encoding='utf-8').splitlines()) == expanded,
                    'Sparse extension not confirmed')
            owner['patterns'] = expanded
            current._atomic(gitdir(path), BINDING, current.encoded(owner))
        return path
    lines = sparse_lines(db, commit, job, role)
    git(db, 'worktree', 'add', '--no-checkout', *(['-b', branch] if branch else ['--detach']), str(path), commit)
    require(git_root(path) == db, 'Different common Git directory')
    git(path, 'config', '--worktree', 'core.sparseCheckout', 'true')
    git(path, 'config', '--worktree', 'core.sparseCheckoutCone', 'false')
    sparse = sparse_path(path)
    sparse.parent.mkdir(exist_ok=True)
    write_new(sparse, ('\n'.join(lines) + '\n').encode())
    git(path, 'read-tree', '-mu', 'HEAD')
    write_new(gitdir(path) / BINDING, current.encoded({**binding, 'patterns': lines}))
    return path


def prepare(root, job, tools_commit, main, expected, *, integration=None, integration_head=None, originals=False, repository=REPO):
    current.path(job)
    for oid in (tools_commit, main, expected, integration_head):
        if oid is not None:
            check_commit(oid)
    require(integration_head is None or integration is not None, 'Expected integration branch')
    if integration is not None:
        require(integration.startswith('content/') and not integration.startswith('content/pw/'),
                'Expected separate content integration branch')
    base, db = store_for(root, repository)
    with writer(io.safe(base, 'administration.lock')), writer(db / 'authoring-builder.lock'):
        def check_refs():
            require(transport.remote_head(db, 'refs/heads/main') == main and
                    transport.remote_head(db, 'refs/heads/content/pw/' + job) == expected,
                    'Main or work ref changed; refresh pinned commits')
            if integration:
                git(db, 'check-ref-format', 'refs/heads/' + integration)
                require(transport.remote_head(db, 'refs/heads/' + integration) == integration_head,
                        'Integration ref changed; bind its actual head')
        check_refs()
        transport.git(db, 'fetch', '--no-tags', '--no-write-fetch-head', '--', transport.REMOTE,
                      *sorted({main, tools_commit, expected or main, integration_head or main}))
        check_refs()
        if integration_head:
            git(db, 'merge-base', '--is-ancestor', main, integration_head)
        toolbox = open_tree(base, db, 'tools-' + tools_commit, tools_commit, job, 'tools')
        data = open_tree(base, db, 'job-' + job, expected or main, job, 'job')
        if originals:
            from .work_publish import hydrate
            from .production_worktree_publish import JOURNAL
            require(expected and not (gitdir(data) / JOURNAL).exists(), 'Expected published job without pending transaction')
            hydrate(data, job, expected)
        result = {'store': str(db), 'tools': str(toolbox), 'tool_commit': tools_commit, 'job': str(data),
                  'data_commit': expected or main, 'main': main, 'temporary': str(io.safe(base, 'tmp'))}
        if integration:
            result['integration'] = str(open_tree(base, db, 'integration-' + job, integration_head or main,
                                                  job, 'integration', integration))
        return result


def check_product(root, job, commit):
    binding = read_binding(root)
    if binding is None:
        return
    require(binding['role'] == 'job' and binding['job'] == job, 'Wrong completion worktree')
    product = io.safe(Path(binding['store']).parent, 'integration-' + job)
    owner = read_binding(product)
    require(owner and owner['store'] == binding['store'] and owner['role'] == 'integration'
            and owner['job'] == job and git(product, 'rev-parse', 'HEAD') == commit and
            git(product, 'rev-parse', '--abbrev-ref', 'HEAD') == owner['branch'] and not changes(product),
            'Completion requires the clean committed product worktree of this job')


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('job')
    cli.add_argument('--root', type=Path, required=True)
    cli.add_argument('--tools', required=True)
    cli.add_argument('--main', required=True)
    cli.add_argument('--expected', required=True, help='Full work commit or new')
    cli.add_argument('--originals', action='store_true', help='Reconstruct the pinned local draft and its originals')
    cli.add_argument('--integration', help='Owned content integration branch')
    cli.add_argument('--integration-head', help='Full head of an existing integration ref')
    cli.add_argument('--auth', choices=('env', 'GH_TOKEN', 'GITHUB_TOKEN', 'gh'), help='Explicit Git and original-read credential')
    args = cli.parse_args()
    try:
        from contextlib import nullcontext
        from . import work_publish
        from .puzzle_production.github_rest import TOKEN_NAMES
        auth = nullcontext()
        if args.auth:
            token = work_publish.select_token(args.auth)
            for key in TOKEN_NAMES:
                os.environ.pop(key, None)
            auth = work_publish.publisher_auth(args.auth, token)
        with auth:
            result = prepare(args.root, args.job, args.tools, args.main,
                             None if args.expected == 'new' else args.expected,
                             integration=args.integration, integration_head=args.integration_head, originals=args.originals)
        print(json.dumps(result))
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        cli.exit(1, f'{exc}\n')


if __name__ == '__main__':
    main()
