"""Closed PW-PERF-D rulebook generation; legacy snapshots keep their own bytes."""
import re
from .contract import exact_keys, integer
from . import catalog_io as io

FORMAT = 'picross-authoring-rulebook-v2'
HANDOFF = 'picross-authoring-handoff-v5'
REQUEST = 'picross-authoring-build-request-v4'
RECORD = 'picross-authoring-record-v4'
PATHS = tuple(sorted([
    'docs/ai-workflows/PUZZLE_AUTHORING.md',
    *[f'docs/ai-workflows/PUZZLE_AUTHORING_STEP_{n}.md' for n in range(1, 6)],
    'docs/PUZZLE_IMAGE_STYLE.md', 'docs/PUZZLE_QUALITY.md']))


def shape(rule, handoff_format, repo_commit, revision=None):
    from . import authoring_package as ap
    if handoff_format != HANDOFF:
        exact_keys(rule, {'version', 'file', 'sha256'})
        ap.relative(rule['file']); ap.sha(rule['sha256'])
        ap.require(rule['version'] != '0.8.0' or revision is None or revision <= 6,
                   'Rev7 requires the new rulebook generation')
        return False
    exact_keys(rule, {'format', 'version', 'document_revision', 'source_commit', 'sources'})
    ap.require(rule['format'] == FORMAT and rule['version'] == '0.8.0' and
               type(rule['document_revision']) is int and rule['document_revision'] == 9,
               'Unsupported rulebook generation/document revision')
    ap.require(isinstance(repo_commit, str) and re.fullmatch(r'[0-9a-f]{40}', repo_commit) and
               rule['source_commit'] == repo_commit, 'Rulebook source commit differs from producer')
    ap.require(revision is None or revision == rule['document_revision'], 'Rulebook document revision mismatch')
    ap.require(isinstance(rule['sources'], list) and len(rule['sources']) == len(PATHS), 'Missing rulebook sources')
    for item, path in zip(rule['sources'], PATHS):
        exact_keys(item, {'path', 'file', 'sha256', 'bytes'})
        ap.require(item['path'] == path and item['file'] == 'rulebook/' + path, 'Noncanonical rulebook source set')
        ap.sha(item['sha256']); integer(item['bytes'], 1, 1024 * 1024, 'rulebook source bytes')
    return True


def validate(rule, handoff_format, repo_commit, read, revision=None, *, history_repo=None, verify_git=False):
    from . import authoring_package as ap
    new = shape(rule, handoff_format, repo_commit, revision)
    if not new:
        raw = read(rule['file'])
        ap.require(io.checksum(raw) == rule['sha256'], 'Rulebook snapshot hash mismatch')
        text = raw.decode('utf-8')
        reject_relabel(rule, raw)
        if revision is not None:
            pattern = r'^\*\*Version ' + re.escape(rule['version']) + r' · Dokumentrevision ' + str(revision) + r' ·'
            ap.require(re.search(pattern, text, re.M), 'Rulebook version/document revision does not match snapshot')
        elif rule['version'] in ('0.5.0', '0.6.0', '0.7.0', '0.8.0'):
            ap.require(re.search(r'^\*\*Version ' + re.escape(rule['version']) + r'(?: | ·)', text, re.M),
                       'Rulebook requires a matching versioned snapshot')
        else:
            ap.require(not re.search(r'^\*\*Version 0\.[678]\.0(?: | ·)', text, re.M),
                       'Legacy rulebook label conflicts with snapshot')
        return
    source = None
    if verify_git:
        from tools.production_workspace.sources import git
        ap.require(history_repo is not None, 'New rulebook requires explicit history-repo')
        git(history_repo, 'merge-base', '--is-ancestor', rule['source_commit'], 'HEAD')
        source = history_repo
    for item in rule['sources']:
        raw = read(item['file'])
        ap.require(len(raw) == item['bytes'] and io.checksum(raw) == item['sha256'],
                   'Rulebook source bytes/hash mismatch: ' + item['path'])
        if '/ai-workflows/' in item['path']:
            ap.require(re.search(rb'^\*\*Version 0\.8\.0 \xc2\xb7 Dokumentrevision 9 \xc2\xb7', raw, re.M),
                       'Rulebook source header/document revision mismatch')
        if source is not None:
            ap.require(read_git(source, rule['source_commit'], item['path']) == raw,
                       'Rulebook source differs from Git commit: ' + item['path'])


def capture(repository, commit):
    """Return the new rule binding and immutable payload bytes from one Git commit.

    Caller stages these bytes under the returned package-relative paths and adds
    them to its explicit build files. No writes, fetches, approvals or resealing.
    """
    from tools.production_workspace.sources import check_commit, git
    check_commit(commit)
    git(repository, 'merge-base', '--is-ancestor', commit, 'HEAD')
    payload = {'rulebook/' + path: read_git(repository, commit, path) for path in PATHS}
    rule = {'format': FORMAT, 'version': '0.8.0', 'document_revision': 9,
            'source_commit': commit, 'sources': [
                {'path': path, 'file': 'rulebook/' + path,
                 'sha256': io.checksum(payload['rulebook/' + path]), 'bytes': len(payload['rulebook/' + path])}
                for path in PATHS]}
    validate(rule, HANDOFF, commit, payload.__getitem__, 9)
    return rule, payload


def read_git(repository, commit, path):
    """Fixed norm allowlist; never widens the service's production-file API."""
    from tools.production_workspace.sources import git, check_commit
    from . import authoring_package as ap
    check_commit(commit)
    ap.require(path in PATHS, 'Unknown rulebook Git path')
    rows = git(repository, 'ls-tree', '-z', commit, '--', path).split(b'\0')
    rows = [row for row in rows if row]
    ap.require(len(rows) == 1, 'Missing rulebook Git source: ' + path)
    meta, actual = rows[0].split(b'\t', 1)
    mode, kind, oid = meta.decode('ascii').split()
    ap.require(actual.decode('utf-8') == path and mode == '100644' and kind == 'blob',
               'Rulebook Git source must be a regular canonical file')
    ap.require(int(git(repository, 'cat-file', '-s', oid)) <= 1024 * 1024, 'Rulebook Git source too large')
    return git(repository, 'cat-file', 'blob', oid)


def reject_relabel(rule, raw):
    """Prevent Rev7-as-single-file without imposing new legacy viewing gates."""
    from . import authoring_package as ap
    declared = re.search(rb'^\*\*Version 0\.8\.0 \xc2\xb7 Dokumentrevision ([0-9]+) \xc2\xb7', raw, re.M)
    ap.require(rule['version'] != '0.8.0' or declared is None or int(declared[1]) <= 6,
               'Rev7 requires the new rulebook generation')
