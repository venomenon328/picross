"""Publish or retire one current production job. Run as python -m tools.work_publish."""
import argparse
from contextlib import contextmanager
from copy import deepcopy
import json
import os
import re
from pathlib import Path
import subprocess
import tempfile
from uuid import uuid4

from . import publish_git as transport
from .app_products import PRODUCTS
from .puzzle_production import current_authoring as current, current_delivery, catalog_io as io, work_assets
from .puzzle_production.authoring_builder import git_root, index_value, writer
from .puzzle_production.authoring_package import require
from .production_workspace.sources import GitSource
from .production_workspace import release_catalog

REPO = work_assets.REPOSITORY
MIB = 1024**2


def api(path, method='GET', value=None):
    args = ['gh', 'api', '--hostname', 'github.com', '-X', method, ('repos/' + REPO + '/' + path).rstrip('/')]
    if value is not None:
        args += ['--input', '-']
    raw = subprocess.check_output(args, input=json.dumps(value).encode() if value is not None else None, timeout=60)
    return json.loads(raw) if raw.strip() else None


def catalog():
    return release_catalog.catalog(api)


def owned_release(row, job):
    require(row['tag_name'] == 'work-prod-' + job and row['body'] == 'Picross production job ' + job
            and row['prerelease'] is True and row['draft'] is False and row['immutable'] is False,
            'Foreign or immutable work release')
    return row


def delete_ref(root, ref, expected):
    if transport.remote_head(root, ref) == expected:
        transport.git(root, 'push', '--no-follow-tags', '--no-verify', '--recurse-submodules=no',
                      '--force-with-lease=' + ref + ':' + expected, '--', transport.REMOTE, ':' + ref)
    require(transport.remote_head(root, ref) is None, 'Conditional ref removal not confirmed')


@contextmanager
def catalog_writer(root, main):
    """Serialize cooperating jobs across hosts. A killed process resumes from its local token."""
    git_root(root)
    state = io.external(transport.git(root, 'rev-parse', '--absolute-git-dir').decode().strip())
    pending = state / 'work-production-catalog-owner'
    ref = 'refs/heads/' + release_catalog.LOCK_BRANCH
    with writer(state / 'work-production.lock'):
        if not pending.exists():
            tree = transport.git(root, 'rev-parse', main + '^{tree}').decode().strip()
            nonce = transport.git(root, 'commit-tree', tree, '-p', main, '-m', 'Production catalog lease ' + uuid4().hex).decode().strip()
            with pending.open('x', encoding='ascii') as stream:
                stream.write(nonce)
                stream.flush()
                os.fsync(stream.fileno())
        nonce = pending.read_text(encoding='ascii')
        require(transport.SHA.fullmatch(nonce), 'Invalid local catalog owner identity')
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
    with tempfile.TemporaryDirectory(prefix='work-index-') as directory:
        env = {**os.environ, 'GIT_INDEX_FILE': str(Path(directory) / 'index')}
        def git(*args, data=None):
            return subprocess.check_output(['git', '-C', str(root), *args], input=data, env=env).decode().strip()
        git('read-tree', parent)
        for name, raw in files.items():
            blob = git('hash-object', '-w', '--stdin', data=raw)
            git('update-index', '--add', '--cacheinfo', '100644', blob, name)
        return git('commit-tree', git('write-tree'), '-p', parent, '-m', message)


def upload(tag, asset_name, data):
    with tempfile.TemporaryDirectory(prefix='work-upload-') as tmp:
        file = Path(tmp) / asset_name
        file.write_bytes(data)
        subprocess.run(['gh', 'release', 'upload', tag, str(file) + '#picross-original:' + tag, '--repo', REPO], check=True, timeout=300)


def release_for(rows, tag):
    matches = [r for r in rows if r['tag_name'] == tag]
    require(len(matches) <= 1, 'Duplicate work release')
    return matches[0] if matches else None


def push_job(root, job, expected):
    root = io.external(root)
    name = current.path(job)
    raw = io.read(root, name, MIB)
    draft = current.compact(current.validate(io.json_bytes(raw, MIB)))
    require(draft['puzzle_id'] == job, 'Different production identity')
    checked = current.Checked(draft, lambda n, limit: io.read(root, n, limit))
    main = transport.remote_head(root, 'refs/heads/main')
    transport.git(root, 'fetch', '--no-tags', '--', transport.REMOTE, main)
    transport.git(root, 'merge-base', '--is-ancestor', transport.CLEAN_MAIN, main)
    require(api('')['permissions']['push'] and api('immutable-releases')['enabled'] is False,
            'Writable mutable release repository required')
    with catalog_writer(root, main):
        return publish_locked(root, job, expected, main, checked)


def publish_locked(root, job, expected, main, checked):
    draft = checked.job
    branch = 'content/pw/' + job
    ref = 'refs/heads/' + branch
    actual = transport.remote_head(root, ref)
    tag = 'work-prod-' + job
    source = GitSource(root)
    if actual:
        transport.git(root, 'fetch', '--no-tags', '--', transport.REMOTE, actual)
    parent = expected or main
    previous_raw = source.read(parent, current.path(job), MIB, missing=True)
    previous = current.validate(io.json_bytes(previous_raw, MIB)) if previous_raw else None
    if actual != expected:
        require(actual and transport.git(root, 'show', '-s', '--format=%P', actual).decode().strip() == parent,
                'Work ref changed; resume from the current record')
    if previous:
        require(previous['test_only'] == draft['test_only'] and previous['operation'] == draft['operation']
                and all(draft['budgets']['used'][k] >= v for k,v in previous['budgets']['used'].items()),
                'Current work scope or budget changed')
        if any(draft['budgets']['limits'][k] > v for k,v in previous['budgets']['limits'].items()):
            require(any(d['scope'] == 'budget' for d in draft['decisions']), 'Budget increase lacks approval')
    checked.check_new_previews(previous)
    rows, elapsed = catalog()
    release = release_for(rows, tag)
    old = {r['sha256']:r for r in current.references(previous) if 'asset' in r} if previous else {}
    refs = current.references(draft)
    own = {r['sha256']:r for r in refs if current.own(job, r['file'])}
    present = {a['name'] for a in release['assets']} if release else set()
    additions = sum('original-' + h not in present for h in own)
    release_catalog.capacity(rows, elapsed, tag, additions, reserved_apps=len(PRODUCTS))
    tag_ref = 'refs/tags/' + tag
    anchor = transport.remote_head(root, tag_ref)
    if release is None:
        require(actual == expected and not (previous and 'work_release' in previous) and anchor is None,
                'Work release missing or tag occupied')
        release = api('releases', 'POST', {'tag_name': tag, 'target_commitish': main, 'name': tag,
                      'body': 'Picross production job ' + job, 'draft':False, 'prerelease':True, 'make_latest':'false'})
        anchor = transport.remote_head(root, tag_ref)
    owned_release(release, job)
    require(anchor == release['target_commitish'], 'Work tag identity changed')
    transport.git(root, 'merge-base', '--is-ancestor', transport.CLEAN_MAIN, anchor)
    transport.git(root, 'merge-base', '--is-ancestor', anchor, main)
    attachments = {a['name']: a for a in release['assets']}
    result = deepcopy(draft)
    result['format'] = work_assets.FORMAT
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
                upload(tag, asset_name, checked.raw[r['file']])
                latest = owned_release(api('releases/' + str(release['id'])), job)
                asset = next(a for a in latest['assets'] if a['name'] == asset_name)
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
        head = metadata_commit(root, parent, {current.path(job):encoded,current.INDEX:current.encoded(index)},
                               'Publish current ' + job)
        actual = transport.publish(root, branch, head, expected)
    require(actual and transport.remote_head(root, ref) == actual, 'Publication not confirmed')
    retained = {r['asset']['asset_id'] for r in current.references(result) if 'asset' in r}
    previous_ids = {r['asset']['asset_id'] for r in old.values() if r['asset']['release_id'] == release['id']}
    for asset in attachments.values():
        owned = (asset.get('label') == 'picross-original:' + tag and
                 re.fullmatch(r'original-[0-9a-f]{64}',asset['name']))
        if asset['id'] not in retained and (asset['id'] in previous_ids or owned):
            api('releases/assets/' + str(asset['id']), 'DELETE')
    return actual


def finish(root, job, expected, *, confirmed=False):
    """Check the exact completed record against current main, then close its namespace."""
    root = io.external(root)
    current.path(job)
    require(transport.SHA.fullmatch(expected or ''), 'Expected work commit required')
    main = transport.remote_head(root, 'refs/heads/main')
    require(main is not None, 'Remote main missing; integration cannot be confirmed')
    transport.git(root,'fetch','--no-tags','--',transport.REMOTE,main)
    with catalog_writer(root, main):
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
    require(record['format'] == work_assets.FORMAT and record['puzzle_id'] == job, 'Unexpected work record')
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
        owned_release(release,job)
        require(release['target_commitish'] == anchor and all(r['release_id'] == release['id'] for r in refs)
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


def resume(root, job, expected):
    """Reopen a pinned publication for the existing local builder/finalizer."""
    root = io.external(root)
    name = current.path(job)
    require(expected and transport.remote_head(root, 'refs/heads/content/pw/' + job) == expected,
            'Refresh the current work ref')
    require(transport.git(root, 'rev-parse', 'HEAD').decode().strip() == expected,
            'Use a dedicated worktree at the selected work commit')
    with writer(git_root(root) / 'authoring-builder.lock'):
        raw = GitSource(root).read(expected, name, MIB)
        record = current.validate(io.json_bytes(raw, MIB))
        require(record['format'] == work_assets.FORMAT, 'Bound external record required')
        checked = current.Checked(record, lambda n, limit: io.read(root,n,limit))
        draft = deepcopy(record)
        draft['format'] = current.FORMAT
        del draft['work_release']
        for ref in current.references(draft):
            if ref.pop('asset', None):
                data = io.read(root,ref['file'],ref['bytes'],missing=True)
                require(data in (None, checked.raw[ref['file']]), 'Local original changed')
                if data is None:
                    dest = io.safe(root, ref['file'])
                    dest.parent.mkdir(parents=True,exist_ok=True)
                    current._create(root,ref['file'],checked.raw[ref['file']])
        local = io.read(root,name,MIB)
        require(local in (raw,current.encoded(draft)), 'Local record changed')
        current._atomic(root,name,current.encoded(draft))
    return name


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['publish','resume','retire'])
    parser.add_argument('job')
    parser.add_argument('--expected', required=True, help='Full published work commit (new only for first publication)')
    args = parser.parse_args()
    expected = None if args.expected == 'new' else args.expected
    if expected is not None and not transport.SHA.fullmatch(expected):
        parser.error('--expected must be a full commit SHA')
    if args.operation == 'retire' and expected is None:
        parser.error('retire requires the full published work commit as --expected')
    root = Path.cwd()
    if args.operation == 'retire':
        current.path(args.job)
        try:
            print(finish(root, args.job, expected))
        except (ValueError, OSError, subprocess.SubprocessError) as exc:
            detail = str(exc) if isinstance(exc, ValueError) else type(exc).__name__
            tag = 'work-prod-' + args.job
            parser.exit(1, f'Produktionsabschluss offen ({detail}). '
                        f'Produktionsbranch content/pw/{args.job}, Arbeitsrelease und Tag {tag} prüfen.\n'
                        f'Nach Klärung im selben Checkout wiederholen: '
                        f'python -m tools.work_publish retire {args.job} --expected {expected}\n')
        return
    operation = {'publish':push_job, 'resume':resume}[args.operation]
    print(operation(root, args.job, expected))


if __name__ == '__main__':
    main()
