"""Publish or retire one current production job. Run as python -m tools.work_publish."""
import argparse
import base64
from hashlib import sha1
from contextlib import contextmanager, nullcontext
from copy import deepcopy
import json
import os
import re
from pathlib import Path
import subprocess
import tempfile
from urllib.parse import urlencode
from uuid import uuid4

from . import publish_git as transport, production_git_workspace as workspace
from .production_worktree_publish import Publication, JOURNAL, previous_operation
from .app_products import PRODUCTS
from . import work_refs
from .puzzle_production import current_authoring as current, current_delivery, catalog_io as io, github_rest, work_assets
from .puzzle_production.authoring_builder import git_root, index_value, writer
from .puzzle_production.authoring_package import require
from .production_workspace.sources import GitSource
from .production_workspace import release_catalog

REPO = work_assets.REPOSITORY
MIB = 1024**2


OPERATIONS = ('publish', 'resume', 'retire')
AUTH_SOURCES = ('env', 'GH_TOKEN', 'GITHUB_TOKEN', 'gh')


def select_token(auth):
    require(auth in AUTH_SOURCES, 'Unknown publisher authentication context')
    if auth == 'env':
        return github_rest.publisher_environment_token()
    if auth != 'gh':
        return os.environ.get(auth, '').strip()
    env = {k: v for k, v in os.environ.items() if k.upper() not in (*github_rest.TOKEN_NAMES, 'GH_DEBUG')}
    try:
        return subprocess.check_output(['gh', 'auth', 'token', '--hostname', 'github.com'], env=env,
                                       stderr=subprocess.PIPE, timeout=15).decode('ascii').strip()
    except (OSError, subprocess.SubprocessError, UnicodeError):
        raise github_rest.Failure('auth', 'Selected gh login unavailable; check the active github.com login') from None


@contextmanager
def publisher_auth(auth, token=None):
    require(auth in AUTH_SOURCES, 'Unknown publisher authentication context')
    token = select_token(auth) if token is None else token
    with github_rest.use_publisher_token(token), transport.use_remote_token(token):
        yield


def request(endpoint, method, *, value=None, data=None, upload=False):
    token = github_rest.publisher_token()
    require(token, 'Publisher authentication context is missing')
    headers = {'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28',
               'Cache-Control': 'no-cache', 'User-Agent': 'picross-work-publish'}
    url = github_rest.API
    if upload:
        url = url.replace('api.github.com', 'uploads.github.com')
        headers['Content-Type'] = 'application/octet-stream'
    elif value is not None:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(value).encode()
    url += '/' + endpoint if endpoint else ''
    try:
        with github_rest.open_api(url, headers, timeout=90 if upload else 15, token=token,
                                  data=data, method=method, upload=upload) as response:
            raw = response.read(4 * MIB + 1)
        require(len(raw) <= 4 * MIB, 'GitHub response exceeds the publisher byte limit')
        try:
            return json.loads(raw) if raw.strip() else None
        except ValueError:
            raise ValueError(f'{method} {endpoint or REPO}: invalid GitHub JSON; check the operation before retrying') from None
    except github_rest.Failure as exc:
        if exc.kind == 'rate_limit':
            detail = str(exc)
        elif exc.kind == 'auth':
            detail = 'authentication failed; check the selected credential'
        elif exc.status in (409, 422):
            detail = 'operation rejected; inspect the bound generation and request before retrying'
        elif exc.kind == 'access':
            detail = 'operation unavailable in the selected context; check this endpoint and its concrete access'
        else:
            detail = 'transport or service error; check connectivity'
        status = f' (HTTP {exc.status})' if exc.status else ''
        recovery = '; read back the work ref and release before retrying' if method != 'GET' else ''
        raise github_rest.Failure(exc.kind, f'{method} {endpoint or REPO}{status}: {detail}{recovery}',
                                  exc.status) from None


def api(path, method='GET', value=None):
    return request(path, method, value=value)


def repository_check(repository):
    require(repository == REPO, 'Publisher repository does not match the requested repository')
    if os.environ.get('GITHUB_ACTIONS') == 'true':
        require(os.environ.get('GITHUB_REPOSITORY', '').casefold() == REPO,
                'Actions repository differs from the publisher repository')
    info = api('')
    require(isinstance(info, dict) and isinstance(info.get('full_name'), str) and info['full_name'].casefold() == REPO,
            'GitHub returned a different publisher repository')
    if work_refs.FIXTURE:
        require(info.get('id') == work_refs.TEST_ID, 'Different isolated fixture repository ID')


def creation_setting():
    try:
        settings = api('immutable-releases')
    except github_rest.Failure as exc:
        if exc.kind != 'access' or exc.status != 404:
            raise
        # GitHub hides settings behind 404 as well as using that status for
        # disabled. Prove Administration(read) with the same token and repo.
        access = api('actions/permissions')
        if isinstance(access, dict) and type(access.get('enabled')) is bool:
            return 'disabled'
        return 'unknown'
    if isinstance(settings, dict) and type(settings.get('enabled')) is bool:
        return 'enabled' if settings['enabled'] else 'disabled'
    return 'unknown'


def require_creation_setting():
    try:
        setting = creation_setting()
    except github_rest.Failure as exc:
        raise github_rest.Failure(exc.kind, 'New release setting unknown. ' + str(exc), exc.status) from None
    require(setting == 'disabled', f'New release setting {setting}; creation requires confirmed disabled immutability')
    return setting


def remote_record(commit, job):
    name = current.path(job)
    value = api(f'contents/{name}?ref={commit}')
    require(isinstance(value, dict) and value.get('type') == 'file' and value.get('path') == name and
            value.get('encoding') == 'base64' and type(value.get('size')) is int and
            0 < value['size'] <= MIB and isinstance(value.get('content'), str),
            'Invalid production record response at the expected commit')
    try:
        raw = base64.b64decode(''.join(value['content'].splitlines()), validate=True)
    except ValueError:
        raise ValueError('Invalid production record encoding') from None
    blob = sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest()
    require(len(raw) == value['size'] and value.get('sha') == blob, 'Production record bytes differ from the Git blob')
    return raw


def bound_record(raw, job):
    record = current.validate(io.json_bytes(raw, MIB))
    require(record['puzzle_id'] == job and record['format'] in current.PUBLISHED_FORMATS,
            'Published record does not match the requested job')
    return record


def fresh_generation(rows, job, anchor, binding):
    tag = 'work-prod-' + job
    listed = release_for(rows, tag)
    if listed is None:
        require(binding is None, 'Bound work release is missing; restore or recover the bound generation')
        require(anchor is None, 'Work tag is occupied without an owned release; inspect the tag')
        return None
    release_id = listed.get('id')
    require(type(release_id) is int and release_id > 0, 'Invalid work release ID')
    if binding is not None:
        require(binding['id'] == release_id and binding['anchor'] == anchor,
                'Work release generation changed; refresh the bound record')
    latest = owned_release(api('releases/' + str(release_id)), job)
    require(latest.get('id') == release_id and transport.SHA.fullmatch(anchor or '') and
            latest.get('target_commitish') == anchor, 'Work tag or release anchor changed; read back the generation')
    require(isinstance(latest.get('assets'), list), 'Invalid work release assets')
    return latest


def observe(root, operation, job, expected, repository, auth, *, read_record=None, recovery_parent=None):
    current.path(job)
    require(operation in OPERATIONS and (
        operation == 'publish' and expected is None or isinstance(expected, str) and transport.SHA.fullmatch(expected)),
        'Operation requires the expected full work commit (new only for first publication)')
    repository_check(repository)
    require(not work_refs.FIXTURE or job == work_refs.TEST_JOB, 'Isolated fixture job required')
    main = transport.remote_head(root, 'refs/heads/main')
    require(main is not None, 'Remote main missing; check the Git repository and selected credential')
    api_main = api('git/ref/heads/main')
    remote_object = api_main.get('object') if isinstance(api_main, dict) else None
    require(isinstance(remote_object, dict) and api_main.get('ref') == 'refs/heads/main' and
            remote_object.get('type') == 'commit' and remote_object.get('sha') == main,
            'Git and REST main differ; refresh both in the selected context')
    actual = transport.remote_head(root, 'refs/heads/content/pw/' + job)
    reader = read_record if read_record is not None else remote_record
    if operation == 'publish' and actual != expected:
        require(actual, 'Expected work ref is missing; refresh the bound record')
        commit = api('git/commits/' + actual)
        parents = commit.get('parents') if isinstance(commit, dict) else None
        require(isinstance(parents, list) and len(parents) == 1 and isinstance(parents[0], dict) and
                commit.get('sha') == actual and parents[0].get('sha') == (expected or recovery_parent or main),
                'Work ref changed; resume from the current record')
    elif operation == 'resume':
        require(actual == expected, 'Work ref changed; resume from the current record')
    elif operation == 'retire':
        require(actual in (expected, None), 'Different production generation; refresh the retirement target')
    binding = bound_record(reader(expected, job), job)['work_release'] if expected else None
    if operation == 'publish' and actual != expected:
        recovered = bound_record(reader(actual, job), job)['work_release']
        require(binding in (None, recovered), 'Work release generation changed; refresh the bound record')
        binding = recovered
    tag = 'work-prod-' + job
    anchor = transport.remote_head(root, 'refs/tags/' + tag)
    rows, elapsed = catalog()
    listed = release_for(rows, tag)
    if operation == 'retire' and listed is None:
        require(anchor in (None, binding['anchor']) and not any(row.get('id') == binding['id'] for row in rows),
                'Retirement release or tag generation differs; inspect remote state')
        release = None
        release_state = 'absent (retirement may already have removed it)'
    else:
        release = fresh_generation(rows, job, anchor, binding)
        release_state = 'existing mutable generation' if release else require_creation_setting()
    if operation == 'publish':
        release_catalog.capacity(rows, elapsed, tag, 0, reserved_apps=len(PRODUCTS))
    capabilities = {'git_refs': {'read': 'checked', 'write': 'unverified' if operation != 'resume' else 'not required'},
                    'release_assets': {'metadata': 'checked', 'originals': 'verify at use',
                                       'write': 'unverified' if operation != 'resume' else 'not required'},
                    'product_pr': 'outside this operation'}
    return {'repository': REPO, 'operation': operation, 'job': job, 'expected': expected,
            'auth': auth, 'main': main, 'work_head': actual, 'tag_anchor': anchor,
            'release_id': release['id'] if release else None, 'release_state': release_state,
            'capabilities': capabilities}


def preflight(root, operation, job, expected, *, repository=REPO, auth='env', token=None):
    """Read-only transport and generation diagnosis, independent of a local checkout."""
    with publisher_auth(auth, token):
        return observe(root, operation, job, expected, repository, auth)


def catalog():
    return release_catalog.catalog(api)


def owned_release(row, job):
    require(isinstance(row, dict) and row.get('tag_name') == 'work-prod-' + job and
            row.get('body') == 'Picross production job ' + job and row.get('prerelease') is True and
            row.get('draft') is False, 'Foreign work release; verify the job and tag ownership')
    require(row.get('immutable') is False, 'Work release is immutable or mutability is unknown; inspect this generation')
    return row


def delete_ref(root, ref, expected):
    if transport.remote_head(root, ref) == expected:
        transport.git(root, 'push', '--no-follow-tags', '--no-verify', '--recurse-submodules=no',
                      '--force-with-lease=' + ref + ':' + expected, '--', transport.REMOTE, ':' + ref)
    require(transport.remote_head(root, ref) is None, 'Conditional ref removal not confirmed')


@contextmanager
def catalog_writer(root, main, *, owner=None):
    """Serialize cooperating jobs across hosts. A killed process resumes from its local token."""
    git_root(root)
    state = io.external(transport.git(root, 'rev-parse', '--absolute-git-dir').decode().strip())
    pending = state / 'work-production-catalog-owner'
    ref = 'refs/heads/' + release_catalog.LOCK_BRANCH
    with writer(state / 'work-production.lock'):
        if not pending.exists():
            tree = transport.git(root, 'rev-parse', main + '^{tree}').decode().strip()
            nonce = transport.git(root, 'commit-tree', tree, '-p', main, '-m', 'Production catalog lease ' + uuid4().hex).decode().strip()
            encoded = nonce.encode('ascii') if owner is None else current.encoded({'owner': owner, 'nonce': nonce})
            current._atomic(state, pending.name, encoded)
        raw = io.read(state, pending.name, 8192)
        if owner is None:
            nonce = raw.decode('ascii')
        else:
            receipt = io.json_bytes(raw, 8192)
            require(isinstance(receipt, dict) and receipt.get('owner') == owner,
                    'Different operation owns the local catalog nonce; resume its original request')
            nonce = receipt.get('nonce')
        require(isinstance(nonce, str) and transport.SHA.fullmatch(nonce), 'Invalid local catalog owner identity')
        actual = transport.remote_head(root, ref)
        if actual is None:
            transport.publish(root, release_catalog.LOCK_BRANCH, nonce, None)
        else:
            require(actual == nonce, 'Another production transaction owns the catalog')
        try:
            yield
        finally:
            delete_ref(root, ref, nonce)
            pending.unlink()


def metadata_commit(root, parent, files, message):
    """Construct from the expected remote tree. Never stage the actor's worktree."""
    with tempfile.TemporaryDirectory(prefix='work-index-', dir=workspace.gitdir(root)) as directory:
        env = {**os.environ, 'GIT_INDEX_FILE': str(Path(directory) / 'index')}
        def git(*args, data=None):
            return subprocess.check_output(['git', '-C', str(root), *args], input=data, env=env).decode().strip()
        git('read-tree', parent)
        for name, raw in files.items():
            blob = git('hash-object', '-w', '--stdin', data=raw)
            git('update-index', '--add', '--cacheinfo', '100644', blob, name)
        return git('commit-tree', git('write-tree'), '-p', parent, '-m', message)


def upload(release_id, tag, asset_name, data):
    query = urlencode({'name': asset_name, 'label': 'picross-original:' + tag})
    request(f'releases/{release_id}/assets?{query}', 'POST', data=data, upload=True)


def release_for(rows, tag):
    require(all(isinstance(row, dict) and isinstance(row.get('tag_name'), str) for row in rows),
            'Invalid release catalog entries')
    matches = [r for r in rows if r['tag_name'] == tag]
    require(len(matches) <= 1, 'Duplicate work release')
    return matches[0] if matches else None


def push_job(root, job, expected, *, repository=REPO, auth='env', token=None, remote_request=None):
    with publisher_auth(auth, token):
        return _push_job(io.external(root), job, expected, repository, auth, remote_request)


def _push_job(root, job, expected, repository, auth, remote_request=None):
    binding = workspace.read_binding(root)
    if binding is None:
        require(remote_request is None, 'Remote requests require a managed job worktree')
        return _publish_draft(root, job, expected, repository, auth)
    require(binding['role'] == 'job' and binding['job'] == job, 'Wrong publication worktree')
    with writer(git_root(root) / 'authoring-builder.lock'):
        return _publish_draft(root, job, expected, repository, auth, managed=True, remote_request=remote_request)


def _publish_draft(root, job, expected, repository, auth, *, managed=False, remote_request=None):
    prior = previous_operation(root, job, expected) if managed else None
    report = observe(root, 'publish', job, expected, repository, auth,
                     recovery_parent=prior['parent'] if prior else None)
    main = report['main']
    if remote_request:
        require(main == remote_request['main'], 'Main changed before publication')
    operation = None
    if prior and prior['confirmed'] and report['work_head'] != expected and not (workspace.gitdir(root) / JOURNAL).exists():
        actual = report['work_head']
        require(actual == prior['target'] == workspace.git(root, 'rev-parse', 'HEAD') and
                workspace.git(root, 'write-tree') == workspace.git(root, 'rev-parse', actual + '^{tree}'),
                'Different work generation after completed publication')
        workspace.check_work(root, job)
        source = GitSource(root)
        require(io.read(root, current.path(job), MIB) == source.read(actual, current.path(job), MIB),
                'Local draft changed; publish with the current work SHA')
        return actual
    if managed and prior:
        operation = Publication(root, job, expected, main, report['work_head'])
        if operation.value['confirmed']:
            require(operation.target == report['work_head'], 'Confirmed remote commit changed')
            return operation.finish(operation.target)
    name = current.path(job)
    raw = io.read(root, name, MIB)
    draft = current.compact(current.validate(io.json_bytes(raw, MIB)))
    require(draft['puzzle_id'] == job, 'Different production identity')
    require(not work_refs.FIXTURE or draft['test_only'] is True, 'Isolated fixture requires test-only data')
    checked = current.Checked(draft, lambda n, limit: io.read(root, n, limit))
    transport.git(root, 'fetch', '--no-tags', '--', transport.REMOTE, main)
    transport.git(root, 'merge-base', '--is-ancestor', transport.CLEAN_MAIN, main)
    require(transport.remote_head(root, 'refs/heads/main') == main, 'Main advanced; refresh before acquiring the catalog lease')
    if managed and operation is None:
        operation = Publication(root, job, expected, main, report['work_head'])
    owner = {'operation': 'publish', 'job': job, 'expected': expected,
             'draft': operation.value['draft']} if operation else None
    with catalog_writer(root, main, owner=owner):
        actual = publish_locked(root, job, expected, main, checked, operation, remote_request)
        if operation:
            require(actual == operation.bind(actual), 'Different published work commit')
    return operation.finish(actual) if operation else actual


def publish_locked(root, job, expected, main, checked, operation=None, remote_request=None):
    draft = checked.job
    branch = 'content/pw/' + job
    ref = 'refs/heads/' + branch
    actual = transport.remote_head(root, ref)
    if operation is not None:
        require(actual == expected or actual is not None and actual == operation.target,
                'Work ref changed outside this local publication')
    tag = 'work-prod-' + job
    source = GitSource(root)
    if actual:
        transport.git(root, 'fetch', '--no-tags', '--', transport.REMOTE, actual)
    parent = operation.value['parent'] if operation else expected or main
    previous_raw = source.read(parent, current.path(job), MIB, missing=True)
    previous = current.validate(io.json_bytes(previous_raw, MIB)) if previous_raw else None
    if actual != expected:
        require(actual and transport.git(root, 'show', '-s', '--format=%P', actual).decode().strip() == parent,
                'Work ref changed; resume from the current record')
    if expected:
        require(previous and previous['puzzle_id'] == job and previous['format'] in current.PUBLISHED_FORMATS,
                'Expected work commit does not contain the published job')
    if previous:
        require(previous['test_only'] == draft['test_only'] and previous['operation'] == draft['operation']
                and all(draft['budgets']['used'][k] >= v for k,v in previous['budgets']['used'].items()),
                'Current work scope or budget changed')
        if any(draft['budgets']['limits'][k] > v for k,v in previous['budgets']['limits'].items()):
            require(any(d['scope'] == 'budget' for d in draft['decisions']), 'Budget increase lacks approval')
    current.check_transition(previous, draft)
    checked.check_new_previews(previous)
    rows, elapsed = catalog()
    tag_ref = 'refs/tags/' + tag
    anchor = transport.remote_head(root, tag_ref)
    binding = previous.get('work_release') if previous else None
    if actual != expected:
        recovered = bound_record(source.read(actual, current.path(job), MIB), job)['work_release']
        require(binding in (None, recovered), 'Work release generation changed; refresh the bound record')
        binding = recovered
    release = fresh_generation(rows, job, anchor, binding)
    old = {r['sha256']:r for r in current.references(previous) if 'asset' in r} if previous else {}
    refs = current.references(draft)
    own = {r['sha256']:r for r in refs if current.own(job, r['file'])}
    present = {a['name'] for a in release['assets']} if release else set()
    additions = sum('original-' + h not in present for h in own)
    release_catalog.capacity(rows, elapsed, tag, additions, reserved_apps=len(PRODUCTS))
    require(transport.remote_head(root, ref) == actual and transport.remote_head(root, tag_ref) == anchor and
            transport.remote_head(root, 'refs/heads/main') == main,
            'Main, work ref or tag changed after preflight; refresh before mutating the release')
    if release is None:
        require_creation_setting()
        require(transport.remote_head(root, tag_ref) is None and transport.remote_head(root, ref) == expected and
                transport.remote_head(root, 'refs/heads/main') == main,
                'Main, work ref or tag changed before release creation; refresh the bindings')
        created = owned_release(api('releases', 'POST', {'tag_name': tag, 'target_commitish': main, 'name': tag,
                               'body': 'Picross production job ' + job, 'draft': False, 'prerelease': True,
                               'make_latest': 'false'}), job)
        anchor = transport.remote_head(root, tag_ref)
        require(anchor == main, 'New work tag differs from the expected main anchor')
        release = fresh_generation([created], job, anchor, None)
    transport.git(root, 'merge-base', '--is-ancestor', transport.CLEAN_MAIN, anchor)
    transport.git(root, 'merge-base', '--is-ancestor', anchor, main)
    attachments = {a['name']: a for a in release['assets']}
    result = deepcopy(draft)
    result['format'] = current.findings.PUBLISHED if draft['format'] in current.findings.FORMATS else work_assets.FORMAT
    result['work_release'] = {'id':release['id'],'anchor':anchor}
    if previous and 'work_release' in previous:
        require(previous['work_release'] == result['work_release'], 'Work release generation changed')
    for r in current.references(result):
        if not current.own(job, r['file']):
            continue
        digest = r['sha256']
        if digest in old:
            identity = old[digest]['asset']
        else:
            asset_name = 'original-' + digest
            asset = attachments.get(asset_name)
            if asset is not None:
                require(asset.get('label') == 'picross-original:' + tag, 'Physical asset name already occupied')
                if asset['state'] == 'starter' and asset['size'] == 0:
                    require(actual == expected, 'Only the current transaction can recover an incomplete upload')
                    api('releases/assets/' + str(asset['id']), 'DELETE')
                    asset = None
            if asset is None:
                require(actual == expected, 'A competing record won publication')
                upload(release['id'], tag, asset_name, checked.raw[r['file']])
                latest = fresh_generation([release], job, transport.remote_head(root, tag_ref), result['work_release'])
                matches = [a for a in latest['assets'] if a['name'] == asset_name]
                require(len(matches) == 1, 'Uploaded original not confirmed; read back the work release before retrying')
                asset = matches[0]
                attachments[asset_name] = asset
            identity = {'repository':REPO,'job':job,'release_id':release['id'],'asset_id':asset['id']}
        r['asset'] = identity
    # Exercise the public reader and verify active product files against the
    # exact Git parent that will back the production snapshot.
    current.Checked(result, lambda n, limit: source.read(parent, n, limit))
    encoded = current.encoded(result)
    checked.recheck()
    if actual != expected:
        require(source.read(actual,current.path(job),MIB) == encoded, 'Competing production publication')
    elif encoded != previous_raw:
        index = index_value(source.read(parent, current.INDEX, 8*MIB))
        index['entries'] = [e for e in index['entries'] if e['puzzle_id'] != job]
        index['entries'].append({'puzzle_id':job,'revision':'current','record':current.path(job)})
        index['entries'].sort(key=lambda e:(e['puzzle_id'],e['revision']))
        message = 'Publish current ' + job
        if remote_request:
            message += '\n\nPW-Remote: ' + remote_request['id']
        head = metadata_commit(root, parent, {current.path(job):encoded,current.INDEX:current.encoded(index)}, message)
        if operation:
            head = operation.bind(head)
        if remote_request and remote_request.get('product'):
            product = remote_request['product']
            require(draft['state'] == 'registered' and draft['integration']['commit'] == product,
                    'Product commit differs from current completion')
            actual = transport.publish_completion(root, job, head, expected, product, main)
        else:
            actual = transport.publish(root, branch, head, expected)
    require(actual and transport.remote_head(root, ref) == actual, 'Publication not confirmed')
    retained = {r['asset']['asset_id'] for r in current.references(result) if 'asset' in r}
    previous_ids = {r['asset']['asset_id'] for r in old.values() if r['asset']['release_id'] == release['id']}
    obsolete = {asset['id'] for asset in attachments.values() if asset['id'] not in retained and
                (asset['id'] in previous_ids or not remote_request and asset.get('label') == 'picross-original:' + tag and
                 re.fullmatch(r'original-[0-9a-f]{64}', asset['name']))}
    if obsolete:
        try:
            require(transport.remote_head(root, ref) == actual, 'Work ref changed before asset cleanup')
            latest = fresh_generation([release], job, transport.remote_head(root, tag_ref), result['work_release'])
            for asset in latest['assets']:
                if asset['id'] in obsolete:
                    require(asset['id'] in previous_ids or (asset.get('label') == 'picross-original:' + tag and
                            re.fullmatch(r'original-[0-9a-f]{64}', asset['name'])),
                            'Obsolete asset no longer has the expected ownership')
                    api('releases/assets/' + str(asset['id']), 'DELETE')
                    obsolete.remove(asset['id'])
        except ValueError as exc:
            detail = f'Confirmed work commit {actual}; asset cleanup open for {sorted(obsolete)}. {exc}'
            if isinstance(exc, github_rest.Failure):
                raise github_rest.Failure(exc.kind, detail, exc.status) from None
            raise ValueError(detail) from None
    return actual


def verify_published_assets(root, job, parent, head, raw):
    """A committed successor alone does not acknowledge post-push cleanup."""
    previous = bound_record(remote_record(parent, job), job)
    current_record = bound_record(raw, job)
    binding = current_record['work_release']
    require(binding == previous['work_release'], 'Changed release generation after publication')
    rows, _ = catalog()
    release = fresh_generation(rows, job, transport.remote_head(root, 'refs/tags/work-prod-' + job), binding)
    def identities(record):
        return {r['asset']['asset_id'] for r in current.references(record) if 'asset' in r}
    required = identities(current_record)
    actual = {a['id'] for a in release['assets']}
    require(transport.remote_head(root, 'refs/heads/content/pw/' + job) == head, 'Published work changed')
    require(not required - actual, f'Missing bound assets {sorted(required - actual)}; inspect release {release["id"]}')
    extra = actual - required
    require(not extra, f'Confirmed work {head}; release {release["id"]} asset cleanup open. '
            f'Predecessor IDs {sorted(extra & identities(previous))}, unbound IDs {sorted(extra - identities(previous))}. '
            'Inspect unbound IDs separately. Resume the identical request from the original private publication journal.')


def finish(root, job, expected, *, confirmed=False, repository=REPO, auth='env', token=None):
    """Check the exact completed record against current main, then close its namespace."""
    with publisher_auth(auth, token):
        root = io.external(root)
        binding = workspace.read_binding(root)
        lock = writer(git_root(root) / 'authoring-builder.lock') if binding else nullcontext()
        with lock:
            return _finish(root, job, expected, confirmed, repository, auth, binding)


def _finish(root, job, expected, confirmed, repository, auth, binding):
    if binding is not None:
        require(binding['role'] == 'job' and binding['job'] == job, 'Wrong retirement worktree')
        require(not (workspace.gitdir(root) / JOURNAL).exists(), 'Finish the pending publish before retirement')
        require(workspace.git(root, 'rev-parse', 'HEAD') == expected, 'Different local retirement generation')
        workspace.check_work(root, job)
        raw = GitSource(root).read(expected, current.path(job), MIB)
        local = io.read(root, current.path(job), MIB)
        require(local in (raw, current.encoded(local_record(bound_record(raw, job)))),
                'Unpublished local draft; reconcile it before retirement')
    # The pinned commit stays locally available after the remote branch is removed.
    def read_record(commit, job):
        source = GitSource(root, fetch_commit=lambda oid: transport.git(root, 'fetch', '--no-tags', '--', transport.REMOTE, oid))
        return source.read(commit, current.path(job), MIB)

    observed = observe(root, 'retire', job, expected, repository, auth, read_record=read_record)
    main = observed['main']
    if (observed['work_head'] is None and observed['tag_anchor'] is None and observed['release_id'] is None
            and not (workspace.gitdir(root) / 'work-production-catalog-owner').exists()
            and transport.remote_head(root, 'refs/heads/' + release_catalog.LOCK_BRANCH) is None):
        return 'no-op'
    transport.git(root,'fetch','--no-tags','--',transport.REMOTE,main)
    require(transport.remote_head(root, 'refs/heads/main') == main, 'Main advanced; refresh before retirement')
    owner = {'operation': 'retire', 'job': job, 'expected': expected, 'confirmed': confirmed} if binding else None
    with catalog_writer(root, main, owner=owner):
        targets = remove_bound_release(root, job, expected, main, confirmed=confirmed)
        if targets is None:
            return 'no-op'
        branch, actual, tagref, anchor = targets
        require(transport.remote_head(root, branch) in (actual, None) and
                transport.remote_head(root, tagref) in (anchor, None),
                'Different production generation after release removal')
        if anchor:
            delete_ref(root, tagref, anchor)
        if actual:
            delete_ref(root, branch, expected)
        require(transport.remote_head(root, branch) is None and transport.remote_head(root, tagref) is None,
                'Production branch or work tag absence not confirmed')
        return 'closed'


def remove_bound_release(root, job, expected, main, *, confirmed, before_delete=None):
    """Under the catalog lease, validate the Git record and remove only its release."""
    branch = 'refs/heads/content/pw/' + job
    actual = transport.remote_head(root, branch)
    require(actual in (expected,None), 'Different production generation')
    tag = 'work-prod-' + job
    tagref = 'refs/tags/' + tag
    rows, _ = catalog()
    release = release_for(rows, tag)
    anchor = transport.remote_head(root, tagref)
    if actual:
        transport.git(root,'fetch','--no-tags','--',transport.REMOTE,actual)
    source = GitSource(root)
    record = current.validate(io.json_bytes(source.read(expected,current.path(job),MIB),MIB))
    require(record['format'] in current.PUBLISHED_FORMATS and record['puzzle_id'] == job, 'Unexpected work record')
    binding = record['work_release']
    require(not any(row['id'] == binding['id'] and row['tag_name'] != tag for row in rows),
            'Bound release has a different tag')
    if actual is None and release is None and anchor is None:
        return None
    base = transport.git(root, 'merge-base', main, expected).decode().strip()
    scope = transport.git(root, 'diff', '--no-renames', '--name-only', '-z', base, expected).split(b'\0')
    require(set(scope) <= {b'', current.INDEX.encode(), current.path(job).encode()},
            'Work ref also contains unrelated changes')
    index = index_value(source.read(expected, current.INDEX, 8*MIB))
    base_index = index_value(source.read(base, current.INDEX, 8*MIB))
    require([r for r in index['entries'] if r['puzzle_id'] != job] ==
            [r for r in base_index['entries'] if r['puzzle_id'] != job] and
            [r for r in index['entries'] if r['puzzle_id'] == job] ==
            [{'puzzle_id':job,'record':current.path(job),'revision':'current'}],
            'Unexpected work index; preserve other work')
    if not confirmed:
        require(record['state'] == 'registered' and record['integration'], 'Registration required')
        result = current_delivery.snapshot(lambda n,l,missing=False:source.read(main,n,l,missing),job)
        require(current_delivery.same(result, record['integration']['result']), 'Different confirmed main result')
        if release:
            checked = current.Checked(record, lambda n, limit: source.read(expected, n, limit), technical=False)
            checked.matches(result)
    require(anchor is None or anchor == binding['anchor'], 'Different work tag generation')
    require(release is None or release['id'] == binding['id'], 'Different release generation')
    refs = [r['asset'] for r in current.references(record) if 'asset' in r]
    if release:
        release = fresh_generation(rows, job, anchor, binding)
        require(all(r['release_id'] == release['id'] for r in refs)
                and {a['id'] for a in release['assets']} == {r['asset_id'] for r in refs},
                'Unexpected release contents; preserve other work')
    if anchor:
        transport.git(root,'merge-base','--is-ancestor',transport.CLEAN_MAIN,anchor)
        transport.git(root,'merge-base','--is-ancestor',anchor,main)
    if before_delete is not None:
        before_delete()
    if release:
        require(transport.remote_head(root, branch) == actual and
                transport.remote_head(root, tagref) == anchor and
                transport.remote_head(root, 'refs/heads/main') == main,
                'Main, production branch or work tag changed during retirement')
        api('releases/' + str(release['id']), 'DELETE')
    remaining, _ = catalog()
    require(not any(row['tag_name'] == tag or row['id'] == binding['id'] for row in remaining),
            'Release removal not confirmed')
    return branch, actual, tagref, anchor


def resume(root, job, expected, *, repository=REPO, auth='env', token=None):
    """Reopen a pinned publication for the existing local builder/finalizer."""
    with publisher_auth(auth, token):
        return _resume(io.external(root), job, expected, repository, auth)


def _resume(root, job, expected, repository, auth):
    observe(root, 'resume', job, expected, repository, auth)
    require(expected and transport.remote_head(root, 'refs/heads/content/pw/' + job) == expected,
            'Refresh the current work ref')
    require(transport.git(root, 'rev-parse', 'HEAD').decode().strip() == expected,
            'Use a dedicated worktree at the selected work commit')
    with writer(git_root(root) / 'authoring-builder.lock'):
        binding = workspace.read_binding(root)
        if binding is not None:
            require(binding['role'] == 'job' and binding['job'] == job, 'Wrong resume worktree')
            require(not (workspace.gitdir(root) / JOURNAL).exists(), 'Finish the pending publish first')
            workspace.check_work(root, job)
        return hydrate(root, job, expected)


def local_record(record):
    draft = deepcopy(record)
    draft['format'] = current.findings.LOCAL if record['format'] == current.findings.PUBLISHED else current.FORMAT
    del draft['work_release']
    for ref in current.references(draft):
        ref.pop('asset', None)
    return draft


def hydrate(root, job, expected):
    """Reconstruct a pinned draft using Git objects and the verified original reader."""
    name = current.path(job)
    raw = GitSource(root).read(expected, name, MIB)
    record = current.validate(io.json_bytes(raw, MIB))
    require(record['format'] in current.PUBLISHED_FORMATS and record['puzzle_id'] == job, 'Bound external record required')
    checked = current.Checked(record, lambda n, limit: io.read(root,n,limit))
    draft = local_record(record)
    assets = [ref for ref in current.references(record) if 'asset' in ref]
    local = io.read(root, name, MIB)
    require(local in (raw, current.encoded(draft)), 'Local record changed')
    for ref in assets:
        data = io.read(root, ref['file'], ref['bytes'], missing=True)
        require(data in (None, checked.raw[ref['file']]), 'Local original changed')
    for ref in assets:
        dest = io.safe(root, ref['file'])
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            current._create(root, ref['file'], checked.raw[ref['file']])
    require(io.read(root, name, MIB) == local, 'Local record changed during resume')
    if local != current.encoded(draft):
        current._atomic(root, name, current.encoded(draft))
    return name


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['preflight', *OPERATIONS])
    parser.add_argument('job')
    parser.add_argument('--for', dest='planned', choices=OPERATIONS, help='Operation to diagnose with preflight')
    parser.add_argument('--repository', default=REPO, help='Expected publisher repository')
    parser.add_argument('--auth', choices=AUTH_SOURCES, default='env',
                        help='Use the selected token source for REST, Git and original reads')
    parser.add_argument('--expected', required=True, help='Full published work commit (new only for first publication)')
    parser.add_argument('--workspace', type=Path, help='Data worktree when run from the trusted tools checkout')
    args = parser.parse_args()
    diagnose = args.operation == 'preflight'
    if diagnose != (args.planned is not None):
        parser.error('--for is required with preflight and only with preflight')
    operation = args.planned if diagnose else args.operation
    expected = None if args.expected == 'new' else args.expected
    if expected is None and operation != 'publish' or expected is not None and not transport.SHA.fullmatch(expected):
        parser.error('use --expected with a full commit SHA (new only for first publication)')
    root = args.workspace or Path.cwd()
    try:
        token = select_token(args.auth)
        # The selected token is passed explicitly to REST and only the required
        # Git network subprocesses. Local Git and unrelated children need none.
        for key in github_rest.TOKEN_NAMES:
            os.environ.pop(key, None)
        options = {'repository': args.repository, 'auth': args.auth, 'token': token}
        if diagnose:
            result = preflight(root, operation, args.job, expected, **options)
            print(json.dumps(result, sort_keys=True))
        else:
            execute = {'publish': push_job, 'resume': resume, 'retire': finish}[operation]
            print(execute(root, args.job, expected, **options))
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        detail = str(exc) if isinstance(exc, ValueError) else type(exc).__name__
        binding = f'Expected work commit {args.expected}.'
        state = ('Only read operations attempted.' if diagnose else
                 'If a write was attempted, check the work ref, tag and release before retrying in the same context.')
        parser.exit(1, f'{args.operation} ({operation}) {args.job}: {detail}. {binding} {state}\n')


if __name__ == '__main__':
    main()
