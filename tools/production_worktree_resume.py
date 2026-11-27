"""Advance an owned job worktree to the exact published successor."""
import os
import subprocess

from . import production_git_workspace as ws, publish_git as transport, work_publish as publisher
from .production_workspace.sources import GitSource, check_commit
from .puzzle_production import catalog_io as io, current_authoring as current, work_assets
from .puzzle_production.authoring_builder import index_value, publish_directory, write_new
from .puzzle_production.authoring_package import require
from .puzzle_production.contract import exact_keys

JOURNAL = 'pw-local-resume.json'
STAGE = 'pw-local-resume.stage'
LIMITS = {current.INDEX: 8 * current.LIMIT}
ORIGINAL_LIMIT = 64 * current.LIMIT


class UnsecuredWork(ValueError):
    """Only an explicitly revoked Inbox build may leave these bytes in place."""


def unsecured(condition, message):
    if not condition:
        raise UnsecuredWork(message)


def checkpoint(step):
    """Local interruption boundary for the Windows and offline regressions."""


def metadata(root, oid, names):
    rows = transport.git(root, '--literal-pathspecs', 'ls-tree', '-z', oid, '--', *names)
    return {row.split(b'\t', 1)[1].decode(): row for row in rows.split(b'\0') if row}


def checked_profile(root):
    require(ws.git(root, 'config', '--worktree', '--bool', 'core.sparseCheckout') == 'true' and
            ws.git(root, 'config', '--worktree', '--bool', 'core.sparseCheckoutCone') == 'false',
            'Unsafe sparse configuration; inspect the owned worktree')
    raw = io.read(ws.gitdir(root), 'info/sparse-checkout', 8 * current.LIMIT)
    return raw.decode().splitlines()


def published_history(root, job, start, target):
    """Accept only linear PW metadata commits for this job and release."""
    source = GitSource(root)
    name = current.path(job)
    try:
        ws.git(root, 'merge-base', '--is-ancestor', start, target)
    except subprocess.CalledProcessError:
        raise ValueError('Divergent local revision; refresh the pinned ref and preserve this worktree') from None
    oids = ws.git(root, 'rev-list', '--first-parent', '--reverse', start + '..' + target).splitlines()
    records = {}
    index = source.read(start, current.INDEX, LIMITS[current.INDEX])
    allowed_index = {index}
    entries = index_value(index)['entries']
    others = [row for row in entries if row['record'] != name]
    row = {'puzzle_id': job, 'revision': 'current', 'record': name}
    parent = start
    generation = scope = None
    for oid in (start, *oids):
        raw = source.read(oid, name, current.LIMIT, missing=oid == start)
        if oid != start:
            changed = set(transport.git(root, 'diff-tree', '-r', '--no-commit-id',
                                        '--name-only', '--no-renames', '-z', parent, oid).split(b'\0')) - {b''}
            require(ws.git(root, 'show', '-s', '--format=%P', oid) == parent and
                    name.encode() in changed and changed <= {name.encode(), current.INDEX.encode()},
                    'Divergent or foreign Git history; refresh the pinned ref and preserve this worktree')
            index = source.read(oid, current.INDEX, LIMITS[current.INDEX])
            require(sorted(index_value(index)['entries'], key=lambda r: r['record']) ==
                    sorted([*others, row], key=lambda r: r['record']),
                    'Successor edits another authoring index entry; inspect the published history')
            allowed_index.add(index)
        if raw is not None:
            record = publisher.bound_record(raw, job)
            binding = record['work_release']
            require(generation in (None, binding), 'Work release generation changed; preserve this worktree')
            identity = (record['operation'], record['test_only'])
            require(scope in (None, identity), 'Published job scope changed; inspect the generation')
            generation, scope = binding, identity
            records[oid] = (raw, record)
        parent = oid
    require(parent == target and target in records, 'Divergent local revision; refresh the pinned ref and preserve this worktree')
    return records, allowed_index


def same_draft(raw, published, record):
    if raw == published:
        return True
    if raw is None:
        return False
    draft = publisher.local_record(record)
    local = current.validate(io.json_bytes(raw, current.LIMIT))
    if 'qualification' not in local:
        draft.pop('qualification', None)
    return local == draft


def local_index(root, head, allowed, target):
    flags = transport.git(root, 'ls-files', '-v', '-z').split(b'\0')
    require(all(row[:1] in (b'H', b'S') for row in flags if row),
            'Unsafe Git index flags or unresolved entries; inspect the owned index')
    tracking = {row[2:].decode(): row[:1] for row in flags if row}
    state = ws.gitdir(root)
    for name in ('index.lock', 'HEAD.lock'):
        require(not io.safe(state, name).exists(), 'Git holds ' + name + '; finish the current writer and retry')
    staged = transport.git(root, 'diff-index', '--cached', '--name-only', '--no-renames', '-z', head, '--').split(b'\0')
    for name in (row.decode() for row in staged if row):
        require(name in allowed, 'Unsecured staged path ' + name + '; preserve and resolve the local change')
        entry = transport.git(root, '--literal-pathspecs', 'ls-files', '--stage', '-z', '--', name)
        parts = entry.split(b'\t', 1)[0].split()
        if not entry and None in allowed[name]:
            continue  # The owned initial job record has not entered the index yet.
        require(entry.count(b'\0') == 1 and len(parts) == 3 and parts[0] == b'100644' and parts[2] == b'0',
                'Unsecured staged metadata ' + name + '; preserve and resolve the local change')
        oid = parts[1].decode()
        require(int(ws.git(root, 'cat-file', '-s', oid)) <= LIMITS.get(name, current.LIMIT) and
                transport.git(root, 'cat-file', 'blob', oid) in allowed[name],
                'Unsecured staged metadata ' + name + '; preserve and resolve the local change')
    for name, row in target.items():
        require(row.startswith(b'100644 blob '), 'Unsafe published metadata mode: ' + name)
    return tracking


def release_snapshot(root, job, record):
    tag = 'work-prod-' + job
    binding = record['work_release']
    release = publisher.owned_release(io.json_bytes(work_assets.get('/releases/tags/' + tag, 4 * current.LIMIT),
                                                    4 * current.LIMIT), job)
    require(release['id'] == binding['id'] and release['target_commitish'] == binding['anchor'] and
            transport.remote_head(root, 'refs/tags/' + tag) == binding['anchor'],
            'Unexpected work release generation; read back the pinned work tag')
    assets = release['assets']
    by_id = {row['id']: row for row in assets}
    require(len(by_id) == len(assets), 'Duplicate published asset identity; inspect the release')
    for ref in current.references(record):
        if 'asset' in ref:
            row = by_id.get(ref['asset']['asset_id'])
            require(ref['asset']['release_id'] == binding['id'] and row and row['name'] == 'original-' + ref['sha256']
                    and row['size'] == ref['bytes'] and row['state'] == 'uploaded',
                    'Missing or changed bound original: ' + ref['file'] + '; verify the work release and access')
    return {tag: release}


def is_original(raw, ref):
    return raw is not None and len(raw) == ref['bytes'] and io.checksum(raw) == ref['sha256']


def original_plan(root, job, target, record, history, tracking, releases, hydrate):
    """Bind every exceptional path before any local write."""
    active = {ref['file']: ref for ref in current.references(record)}
    own = {}
    for _, prior in history.values():
        for ref in current.references(prior):
            if 'asset' in ref:
                own.setdefault(ref['file'], []).append(ref)
    for status, name in ws.changes(root):
        if name in (current.path(job), current.INDEX):
            continue
        unsecured(status in (b'??', b'!!') and (name in own or name in active and 'asset' not in active[name]),
                  'Unsecured local path ' + name + '; preserve and resolve the local change')
    add, remove = {}, {}
    source = GitSource(root)
    for name in sorted(set(active) | set(own)):
        raw = io.read(root, name, ORIGINAL_LIMIT, missing=True)
        ref = active.get(name)
        if ref is not None and 'asset' not in ref:
            git_bytes = source.read(target, name, ORIGINAL_LIMIT)
            require(is_original(git_bytes, ref) and name in tracking and
                    (raw == git_bytes or raw is None and tracking[name] == b'S'),
                    'Changed or missing tracked original: ' + name + '; inspect the pinned worktree')
            if raw is None:
                add[name] = (None, git_bytes)
        elif ref is not None:
            require(name not in tracking and (raw is None or any(is_original(raw, old) for old in own[name])),
                    'Changed or colliding local original: ' + name + '; preserve its bytes')
            if not is_original(raw, ref):
                if hydrate:
                    add[name] = (raw, work_assets.read(ref, ORIGINAL_LIMIT, releases=releases))
                elif raw is not None:
                    remove[name] = raw
        elif raw is not None:
            require(name not in tracking and any(is_original(raw, old) for old in own[name]),
                    'Unsecured older original: ' + name + '; preserve its bytes')
            remove[name] = raw
    return add, remove


def atomic_file(state, root, name, before, after, limit):
    """Stage beside Git administration, never in the sparse data tree."""
    if before == after:
        return
    target = io.safe(root, name)
    require(io.read(root, name, limit, missing=True) == before, 'Local bytes changed during resume: ' + name)
    if after is None:
        target.unlink()
        return
    stage = io.safe(state, STAGE)
    if stage.exists():
        stage.unlink()  # A private incomplete write from this bound transaction.
    target.parent.mkdir(parents=True, exist_ok=True)
    write_new(stage, after)
    require(io.read(state, STAGE, limit) == after, 'Incomplete resume staging')
    require(io.read(root, name, limit, missing=True) == before, 'Local bytes changed during resume: ' + name)
    if before is None:
        publish_directory(stage, target)
    else:
        os.replace(stage, target)


def resume(root, job, expected, *, originals, check_refs):
    """Caller holds the store administration lock followed by the writer lock."""
    state = ws.gitdir(root)
    owner = ws.read_binding(root)
    require(owner and owner['role'] == 'job' and owner['job'] == job and owner['branch'] is None and
            ws.git(root, 'rev-parse', '--abbrev-ref', 'HEAD') == 'HEAD',
            'Different job branch or ownership; use the owned detached worktree')
    head = ws.git(root, 'rev-parse', 'HEAD')
    active = checked_profile(root)
    pending = io.read(state, JOURNAL, current.LIMIT, missing=True)
    journal = io.json_bytes(pending, current.LIMIT) if pending is not None else None
    start = head
    if journal is not None:
        exact_keys(journal, {'owner', 'start', 'targets', 'patterns'})
        require(journal['owner'] == {k: v for k, v in owner.items() if k != 'patterns'},
                'Foreign resume journal; preserve the worktree for inspection')
        start = check_commit(journal['start'])
        require(isinstance(journal['targets'], list) and journal['targets'], 'Invalid local resume targets')
        for oid in journal['targets']:
            check_commit(oid)
    else:
        require(not io.safe(state, STAGE).exists(), 'Unowned resume staging file; inspect the worktree administration')
    history, index_forms = published_history(root, job, start, expected)
    require(head == start or head in history, 'Local HEAD changed during resume; inspect the owned journal')
    targets = journal['targets'] if journal else []
    require(all(oid in history for oid in targets), 'Pending resume has a different release lineage; preserve the worktree')
    name = current.path(job)
    published, record = history[expected]
    names = (name, current.INDEX)
    source = GitSource(root)
    index_bytes = source.read(expected, current.INDEX, LIMITS[current.INDEX])
    old_record = io.read(root, name, current.LIMIT, missing=True)
    old_index = io.read(root, current.INDEX, LIMITS[current.INDEX])
    def secured(raw):
        return (raw is None and start not in history or
                any(same_draft(raw, data, job_record) for data, job_record in history.values()))
    unsecured(secured(old_record), 'Unsecured local record; preserve the draft and reconcile it with the published work')
    if old_index not in index_forms:
        local_index_value = index_value(old_index)
        base = index_value(source.read(start, current.INDEX, LIMITS[current.INDEX]))
        proposed = [row for row in base['entries'] if row['record'] != name]
        proposed.append({'puzzle_id': job, 'revision': 'current', 'record': name})
        require(local_index_value['entries'] == sorted(proposed, key=lambda row: (row['puzzle_id'], row['revision'])),
                'Unsecured authoring index edit; preserve the local index')
        index_forms.add(old_index)
    entries = metadata(root, expected, names)
    require(set(entries) == set(names), 'Missing published metadata')
    record_forms = {old_record, *(raw for raw, _ in history.values())}
    if start not in history and (journal or head == start):
        record_forms.add(None)
    allowed = {name: record_forms, current.INDEX: index_forms}
    tracking = local_index(root, head, allowed, entries)
    original_patterns = journal['patterns'] if journal else owner['patterns']
    expanded = original_patterns
    permitted = [original_patterns]
    for oid in targets:
        expanded = sorted(set(expanded) | set(ws.sparse_lines(root, oid, job, 'job')))
        permitted.append(expanded)
    require(sorted(active) in permitted and owner['patterns'] in permitted,
            'Sparse profile changed outside this workspace; preserve the local worktree')
    if not targets or targets[-1] != expected:
        expanded = sorted(set(expanded) | set(ws.sparse_lines(root, expected, job, 'job')))
        targets = [*targets, expected]
    releases = release_snapshot(root, job, record)
    add, remove = original_plan(root, job, expected, record, history, tracking, releases, originals)
    wanted_record = current.encoded(publisher.local_record(record)) if originals else published
    if head == expected and not originals and old_record is not None:
        wanted_record = old_record
    check_refs()
    if (pending is None and head == expected and not add and not remove and old_record == wanted_record and
            old_index == index_bytes and sorted(active) == expanded and
            ws.git(root, 'write-tree') == ws.git(root, 'rev-parse', expected + '^{tree}')):
        return
    value = {'owner': {k: v for k, v in owner.items() if k != 'patterns'},
             'start': start, 'targets': targets, 'patterns': original_patterns}
    journal_bytes = current.encoded(value)
    if pending != journal_bytes:
        current._atomic(state, JOURNAL, journal_bytes)
    checkpoint('journal')

    # The only Git tree delta is the job record and its index row. Do not run
    # a checkout, which could refresh files beyond those proven here.
    if head != expected:
        ws.git(root, 'update-ref', '--no-deref', 'HEAD', expected, head)
    checkpoint('head')
    local_index(root, expected, allowed, entries)
    transport.git(root, 'update-index', '-z', '--index-info', data=b'\0'.join(entries.values()) + b'\0')
    checkpoint('index')
    atomic_file(state, root, name, old_record, wanted_record, current.LIMIT)
    checkpoint('record')
    atomic_file(state, root, current.INDEX, old_index, index_bytes, LIMITS[current.INDEX])
    checkpoint('authoring-index')
    for name_added, (before, after) in add.items():
        atomic_file(state, root, name_added, before, after, ORIGINAL_LIMIT)
    tracked_add = [name for name in add if name in tracking]
    if tracked_add:
        ws.git(root, 'update-index', '--no-skip-worktree', '--', *tracked_add)
    for obsolete, raw in remove.items():
        atomic_file(state, root, obsolete, raw, None, ORIGINAL_LIMIT)
    checkpoint('originals')
    sparse = 'info/sparse-checkout'
    raw = io.read(state, sparse, 8 * current.LIMIT)
    atomic_file(state, state, sparse, raw, ('\n'.join(expanded) + '\n').encode(), 8 * current.LIMIT)
    if owner['patterns'] != expanded:
        current._atomic(state, ws.BINDING, current.encoded({**owner, 'patterns': expanded}))
    checkpoint('profile')
    require(ws.git(root, 'rev-parse', 'HEAD') == expected and
            ws.git(root, 'write-tree') == ws.git(root, 'rev-parse', expected + '^{tree}') and
            io.read(root, name, current.LIMIT) == wanted_record and
            io.read(root, current.INDEX, LIMITS[current.INDEX]) == index_bytes and checked_profile(root) == expanded,
            'Local resume readback differs; retry the bound workspace')
    for ref in current.references(record):
        local = io.read(root, ref['file'], ORIGINAL_LIMIT, missing=True)
        require(is_original(local, ref) or local is None and not originals and 'asset' in ref,
                'Local original readback differs: ' + ref['file'])
    require(all(not io.safe(root, path).exists() for path in remove), 'Obsolete local originals still present')
    release_snapshot(root, job, record)
    check_refs()
    require(io.read(state, JOURNAL, current.LIMIT) == journal_bytes, 'Local resume owner changed')
    io.safe(state, STAGE).unlink(missing_ok=True)
    io.safe(state, JOURNAL).unlink()
