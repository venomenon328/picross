"""Revision-scoped retirement of merged reveal work; no package reconstruction."""
import hashlib
import re
import subprocess

from . import catalog_io as io, catalog_transaction as tx, reveal_source as source
from .authoring_package import require
from .contract import exact_keys, write_json

INDEX = 'content/authoring/index.json'
LIMIT = 8 * 1024 * 1024


def selection(identifier, revision):
    require(isinstance(identifier, str) and re.fullmatch(r'pz-[a-z0-9][a-z0-9-]{0,59}', identifier),
            'Invalid authoring puzzle ID')
    require(isinstance(revision, str) and re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9._-]{0,31}', revision),
            'Invalid authoring revision')
    return f'content/authoring/{identifier}/{revision}'


def index_rows(value):
    exact_keys(value, {'format', 'entries'})
    require(value['format'] == 'picross-authoring-index-v1' and isinstance(value['entries'], list),
            'Invalid authoring index')
    result = {}
    folded = set()
    for row in value['entries']:
        exact_keys(row, {'puzzle_id', 'revision', 'record'})
        directory = selection(row['puzzle_id'], row['revision'])
        require(row['record'] == directory + '/record.json' and directory.casefold() not in folded,
                'Duplicate/noncanonical authoring index entry')
        folded.add(directory.casefold())
        result[directory] = row
    return result


def blob_id(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def tree_files(root, directory):
    base = io.safe(root, directory)
    if not base.exists():
        return set()
    require(base.is_dir(), 'Authoring revision is not a directory')
    result = set()
    for child in base.rglob('*'):
        name = child.relative_to(root).as_posix()
        child = io.safe(root, name)
        if child.is_file():
            result.add(name)
        else:
            require(any(child.iterdir()), 'Foreign empty authoring directory: ' + name)
    return result


def retire(root, revisions, integrated_commit):
    """Preflight the whole batch, then remove only explicitly selected revisions.

    The caller refreshes origin/main. Git tree IDs bind local bytes; only small
    index/record/approval documents are read from history, never old packages.
    This prepares a reviewable worktree diff, not a commit or merge.
    """
    root = io.external(root)

    def git(*args):
        result = subprocess.run(['git', *args], cwd=root, capture_output=True)
        require(result.returncode == 0, 'Cannot verify retirement source: ' + result.stderr.decode(errors='replace').strip())
        return result.stdout

    require(root == io.external(git('rev-parse', '--show-toplevel').decode().strip()), 'Use the checkout root')
    require(isinstance(integrated_commit, str) and re.fullmatch(r'[0-9a-f]{40}', integrated_commit),
            'Use the full verified main commit')
    for ref in ('origin/main', 'HEAD'):
        git('merge-base', '--is-ancestor', integrated_commit, ref)
    require(isinstance(revisions, (list, tuple)) and revisions, 'Select authoring revisions explicitly')
    directories = []
    for pair in revisions:
        require(isinstance(pair, (list, tuple)) and len(pair) == 2, 'Expected ID and authoring revision')
        directories.append(selection(*pair))
    require(len(set(d.casefold() for d in directories)) == len(directories), 'Duplicate authoring revisions')

    # Validate active authority before looking at historical authoring records.
    snapshot = tx.capture(root)
    entries = {e['id']: e for e in snapshot['registry']['entries']}
    index_bytes = io.read(root, INDEX, LIMIT)
    index = io.json_bytes(index_bytes, LIMIT)
    rows = index_rows(index)
    original_rows = index_rows(io.json_bytes(git('show', integrated_commit + ':' + INDEX), LIMIT))
    old_registry = io.json_bytes(git('show', integrated_commit + ':' + tx.REGISTRY), LIMIT)
    old_entries = {e['id']: e for e in old_registry['entries']}
    tree = {}
    for item in git('ls-tree', '-rz', integrated_commit).split(b'\0'):
        if item:
            meta, name = item.split(b'\t', 1)
            mode, kind, oid = meta.decode().split()
            tree[name.decode('utf-8')] = (mode, kind, oid)

    def committed_bytes(name, raw):
        require(tree.get(name) == ('100644', 'blob', blob_id(raw)), 'Unmerged or modified source: ' + name)

    def historical_json(name):
        require(name in tree and tree[name][:2] == ('100644', 'blob'), 'Missing regular integration record: ' + name)
        return io.json_bytes(git('show', integrated_commit + ':' + name), LIMIT)

    retained = set()
    removed = {}
    present = []
    for (identifier, revision), directory in zip(revisions, directories):
        require(identifier in entries and directory in original_rows, 'Revision is not integrated on main: ' + directory)
        entry = entries[identifier]
        row = original_rows[directory]
        record = historical_json(row['record'])
        require(isinstance(record, dict) and record.get('format') == 'picross-authoring-record-v1' and record.get('puzzle_id') == identifier and
                record.get('revision') == revision and record.get('state') == 'registered' and record.get('blockers') == [],
                'Authoring revision is not completed')
        integration = record.get('integration', {})
        require(isinstance(integration, dict), 'Invalid authoring integration binding')
        active = source.path(identifier)
        active_raw = io.read(root, active, source.LIMIT)
        require(integration.get('operation') == 'catalog_reveal adopt' and integration.get('active_record') == active and
                integration.get('active_record_sha256') == io.checksum(active_raw), 'Stale reveal integration binding')
        authority = io.json_bytes(active_raw, source.LIMIT)
        require(integration.get('image_revision') == authority['current']['image_revision'], 'Wrong completed image revision')
        approval = record.get('final_editorial_approval', {})
        require(isinstance(approval, dict), 'Invalid authoring approval binding')
        approval_name = directory + '/approval.json'
        require(approval.get('file') == approval_name, 'Wrong authoring approval path')
        approval_raw = git('show', integrated_commit + ':' + approval_name)
        committed_bytes(approval_name, approval_raw)
        require(approval.get('sha256') == io.checksum(approval_raw) and
                io.json_bytes(approval_raw, LIMIT) == authority['revisions'][-1]['approval'],
                'Completed approval is not retained by active reveal authority')
        # Exact selected active sources, including original receipt, rating and
        # added metadata. Unrelated open authoring revisions are never traversed.
        retained.update((active, 'game/' + entry['definition'], 'game/' + entry['reveal'],
                         source.identity(entry)['notice'], entry['production']['package'] + '/manifest.json',
                         'content/difficulty/' + identifier + '/rating.json', 'content/added/' + identifier + '.json'))
        require(entry == old_entries.get(identifier),
                'Active entry differs from integrated main')
        original = {n for n in tree if n.startswith(directory + '/')}
        files = tree_files(root, directory)
        if directory not in rows:
            require(not io.safe(root, directory).exists(), 'Partial retirement: revision remains without index entry')
            continue
        require(rows[directory] == row and files == original, 'Unmerged authoring index or revision files')
        for name in sorted(files):
            raw = io.read(root, name, 256 * 1024 * 1024)
            committed_bytes(name, raw)
            removed[name] = (io.checksum(raw), len(raw))
        present.append(directory)

    for name in sorted(retained):
        raw = io.read(root, name, 64 * 1024 * 1024, missing=True)
        if raw is None:
            require(name not in tree, 'Missing active source: ' + name)
        else:
            committed_bytes(name, raw)
    affected = sorted(set(snapshot['texts']) | set(snapshot['retained']) | {INDEX} | set(directories))
    # A staged change is foreign even if the worktree was restored afterwards.
    for start in range(0, len(affected), 20):
        git('diff', '--cached', '--quiet', '--', *affected[start:start+20])
    require(all(tx.read(root, n) == raw for n, raw in snapshot['texts'].items()) and
            all(io.file_hash(root, n) == h for n, h in snapshot['retained'].items()) and
            tx.namespaces(root, snapshot['registry']) == snapshot['namespaces'] and
            io.read(root, INDEX, LIMIT) == index_bytes, 'Checkout changed during retirement planning')
    for directory in directories:
        require(tree_files(root, directory) == {n for n in removed if n.startswith(directory + '/')},
                'Authoring namespace changed during retirement planning')
    for name, (checksum, _) in removed.items():
        require(io.file_hash(root, name, 256 * 1024 * 1024) == checksum, 'Authoring bytes changed during retirement planning')
    if not present:
        return {'status': 'no-op', 'revisions': revisions, 'integrated_commit': integrated_commit,
                'removed_files': 0, 'removed_bytes': 0}
    # Never recursively delete the ID directory. Unexpected newly created files
    # survive and make rmdir fail. All normal rejection paths precede mutation.
    for name in removed:
        io.safe(root, name).unlink()
    for directory in present:
        base = io.safe(root, directory)
        for child in sorted(base.rglob('*'), key=lambda p: len(p.parts), reverse=True):
            io.safe(root, child.relative_to(root).as_posix()).rmdir()
        base.rmdir()
    index['entries'] = [row for row in index['entries'] if selection(row['puzzle_id'], row['revision']) not in present]
    write_json(io.safe(root, INDEX), index)
    return {'status': 'reveal_production_retired', 'revisions': revisions, 'integrated_commit': integrated_commit,
            'removed_files': len(removed), 'removed_bytes': sum(size for _, size in removed.values())}
