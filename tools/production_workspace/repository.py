"""Configured local refs and optional remote sync into a private bare cache."""
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import threading
from urllib.parse import urlsplit

from tools.puzzle_production import authoring_package as ap, catalog_io as io
from tools.puzzle_production.authoring_builder import index_value
from tools.puzzle_production.contract import exact_keys
from .sources import git, GitSource, INDEX, JSON_LIMIT, LRU
from . import presentation as p

DEFAULT_REFS = ['main', 'content/pw/*']
PRODUCTION_BRANCH = re.compile(r'content/pw/pz-[a-z0-9]+(?:-[a-z0-9]+)*\Z')
CACHE = 'git-cache-pw-v1'
SYNC = 'sync-pw-v1.json'


def patterns(values):
    ap.require(isinstance(values, list) and 1 <= len(values) <= 20 and len(set(values)) == len(values), 'Ungültige Refauswahl.')
    for value in values:
        ap.require(value in ('main', 'content/pw/*') or
                   isinstance(value, str) and PRODUCTION_BRANCH.fullmatch(value),
                   'Nur main und Produktionsbranches content/pw/<puzzle_id> sind erlaubt. Einrichtung mit neuem Zustandsordner wiederholen.')
        ap.require(isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9/_.*-]{0,150}', value) and
                   not value.startswith('refs/') and not any(x in value for x in ('..', '//', '@{')) and
                   (value.count('*') == 0 or value.endswith('/*') and value.count('*') == 1), 'Ungültiges Branchmuster.')
        git_check = value.replace('*', 'pw-placeholder')
        ap.require(not git_check.endswith(('/', '.', '.lock')) and all(not part.startswith('.') and
                   not part.endswith('.lock') for part in git_check.split('/')), 'Ungültiger Branchname.')
    return values


def remote_url(value):
    ap.require(isinstance(value, str) and len(value) <= 2048 and not any(ord(c) < 32 for c in value) and
               not value.startswith('-') and '::' not in value, 'Ungültiges Remoteziel.')
    parsed = urlsplit(value)
    if parsed.scheme in ('https', 'http', 'ssh'):
        ap.require(parsed.hostname and parsed.password is None and parsed.query == '' and parsed.fragment == '' and
                   (parsed.scheme == 'ssh' or parsed.username is None), 'Remote darf keine eingebetteten Zugangsdaten enthalten.')
    elif re.fullmatch(r'[A-Za-z0-9_.-]+@[A-Za-z0-9_.-]+:[A-Za-z0-9_./-]+', value):
        pass  # Conventional explicitly configured SSH URL, no custom remote helper.
    else:
        ap.require(Path(value).is_absolute() and Path(value).is_dir(), 'Nur HTTPS/HTTP/SSH oder ein lokales Testremote sind erlaubt.')
    return value


def configure(repository, state, *, remote=None, refs=None):
    root, state = io.external(repository), io.external(state)
    ap.require(root.is_dir(), 'Projektcheckout fehlt.')
    actual = Path(git(root, 'rev-parse', '--show-toplevel').decode().strip())
    ap.require(actual == root, 'Bitte die Wurzel des Projektcheckouts angeben.')
    ap.require(not state.is_relative_to(root) and not root.is_relative_to(state), 'Zustandsordner und Projekt müssen getrennt liegen.')
    # An existing parent working tree is foreign state; do not put the cache there.
    ancestor = state
    while not ancestor.exists():
        ancestor = ancestor.parent
    try:
        git(ancestor, 'rev-parse', '--git-dir')
    except ValueError:
        pass
    else:
        raise ap.InvalidInput('Zustandsordner liegt in einem fremden Git-Arbeitsbaum.')
    value = {'format': 'picross-production-workspace-config-v1', 'repository': str(root),
             'remote': remote_url(remote) if remote else None, 'refs': patterns(refs or DEFAULT_REFS.copy())}
    state.mkdir(parents=True, exist_ok=True)
    config = io.safe(state, 'config.json')
    ap.require(not config.exists(), 'Einrichtung existiert bereits; den vorhandenen Starter verwenden.')
    ap.require(not any(state.iterdir()), 'Neuer eigener, leerer Zustandsordner erforderlich.')
    with config.open('xb') as stream:
        stream.write(p.data(value))
    return value


class Repository:
    def __init__(self, state):
        self.state = io.external(state)
        c = p.parse(io.read(self.state, 'config.json', JSON_LIMIT))
        exact_keys(c, {'format', 'repository', 'remote', 'refs'})
        ap.require(c['format'] == 'picross-production-workspace-config-v1', 'Einrichtung ist ungültig.')
        # Only the original, unchanged default is upgraded. Never silently widen
        # a deliberately restricted source selection or touch the user's refs.
        if c['refs'] == ['main', 'content/*']:
            c['refs'] = DEFAULT_REFS.copy()
            temporary = io.safe(self.state, 'config.tmp')
            temporary.write_bytes(p.data(c))
            temporary.replace(io.safe(self.state, 'config.json'))
        self.refs = patterns(c['refs'])
        self.local = GitSource(c['repository'])
        ap.require(not self.state.is_relative_to(self.local.root) and not self.local.root.is_relative_to(self.state),
                   'Zustandsordner liegt im Projekt.')
        self.remote = remote_url(c['remote']) if c['remote'] else None
        self.cached = None
        self.sync_error, self.synced_at = None, None
        self.lock = threading.RLock()
        self.scans = LRU(8 * 1024 * 1024)
        if self.remote:
            # The previous broad cache can be large or incomplete. Do not scan,
            # migrate or delete it; this reader owns its narrowly scoped cache.
            cache = io.safe(self.state, CACHE)
            if not cache.exists():
                cache.mkdir()
                git(cache, 'init', '--bare', '-q')
            # Refuse link/reparse redirection before any cache mutation.
            for name in ('config', 'objects', 'refs'):
                io.safe(self.state, CACHE + '/' + name)
            # A named promisor remote is required for filtered fetch (raw URLs do not
            # establish the promised-object contract). Config is private cache state.
            git(cache, 'config', 'remote.pw-source.url', self.remote)
            git(cache, 'config', 'remote.pw-source.promisor', 'true')
            git(cache, 'config', 'remote.pw-source.partialclonefilter', 'blob:none')
            self.cached = GitSource(cache, self.fetch_object, self.fetch_commit)
            status = io.read(self.state, SYNC, JSON_LIMIT, missing=True)
            if status:
                self.synced_at = p.parse(status)['synced_at']

    def fetch(self, *specs, filtered=False, prune=False, shallow=False, refetch=False):
        # All mutations are confined to this application's private bare cache.
        size = sum(f.stat().st_size for f in (self.cached.root / 'objects').rglob('*') if f.is_file())
        ap.require(size < 384 * 1024 * 1024, 'Gitcache ist voll (512 MiB). Neuen eigenen Zustandsordner einrichten.')
        git(self.cached.root, '-c', 'protocol.allow=never', '-c', 'protocol.https.allow=always',
            '-c', 'protocol.http.allow=always', '-c', 'protocol.ssh.allow=always', '-c', 'protocol.file.allow=always',
            'fetch', '--no-tags', '--no-auto-maintenance', '--no-recurse-submodules', '--no-write-fetch-head',
            *(['--prune', '--atomic'] if prune else []),
            *(['--depth=1'] if shallow else []),
            *(['--refetch'] if refetch else []),
            *(['--filter=blob:none'] if filtered else ['--no-filter']), '--', 'pw-source', *specs, timeout=30)
        after = sum(f.stat().st_size for f in (self.cached.root / 'objects').rglob('*') if f.is_file())
        ap.require(after <= 512 * 1024 * 1024, 'Gitcache überschreitet 512 MiB; neuen eigenen Zustand einrichten.')

    def fetch_object(self, oid):
        from .sources import check_commit
        check_commit(oid)  # Hash grammar also applies to tree-discovered blob OIDs.
        with self.lock:
            # A blob is no commit negotiation tip. In a shallow promisor cache,
            # ordinary negotiation can fail with "bad revision" for this want.
            self.fetch(oid, refetch=True)

    def fetch_commit(self, oid):
        from .sources import check_commit
        check_commit(oid)
        with self.lock:
            self.fetch(oid, filtered=True, shallow=True)

    def refresh(self):
        with self.lock:
            self.sync_error = None
            if self.remote:
                try:
                    specs = ['+refs/heads/' + ref + ':refs/pw/' + ref for ref in self.refs]
                    # Prune only the destinations of these explicit refspecs. Atomic
                    # ref updates keep the previous cache intact on a failed fetch.
                    self.fetch(*specs, filtered=True, prune=True, shallow=True)
                    self.synced_at = datetime.now(timezone.utc).isoformat()
                    raw = p.data({'synced_at': self.synced_at})
                    temporary = io.safe(self.state, 'sync-pw-v1.tmp')
                    temporary.write_bytes(raw)
                    temporary.replace(io.safe(self.state, SYNC))
                except (ValueError, OSError) as exc:
                    self.sync_error = 'Remote nicht erreichbar oder Anmeldung fehlgeschlagen. Vorhandene Snapshots bleiben lesbar.'
            return self.listing()

    def scan(self, source, commit, puzzle_id):
        key = (str(source.root), commit, puzzle_id)
        cached = self.scans.get(key)
        if cached is not None:
            return p.parse(cached, 8 * JSON_LIMIT)
        jobs, errors = [], []
        index_raw = source.read(commit, INDEX, 8 * JSON_LIMIT, missing=True)
        if index_raw is not None:
            index = index_value(index_raw)
            for row in index['entries']:
                if puzzle_id and row['puzzle_id'] != puzzle_id:
                    continue
                file = row['record'].rsplit('/', 1)[0] + '/workspace.json'
                try:
                    raw = source.read(commit, file, JSON_LIMIT, missing=True)
                    if raw is None:
                        continue
                    projection = p.validate(p.parse(raw))
                    ap.require(projection['puzzle_id'] == row['puzzle_id'] and projection['revision'] == row['revision'],
                               'Index und Projektion stimmen nicht.')
                    record_raw = source.read(commit, row['record'])
                    p.bind(record_raw, projection['record'])
                    jobs.append({'puzzle_id': row['puzzle_id'], 'revision': row['revision'], 'title': projection['title'],
                                 'file': file, 'status': 'Bilder noch nicht geprüft', '_projection': projection,
                                 '_fingerprint': io.checksum(raw + record_raw)})
                except (ValueError, OSError, KeyError, TypeError) as exc:
                    errors.append('Ungültige Projektion für ' + row['puzzle_id'] + '/' + row['revision'] + ': ' + str(exc))
        value = {'jobs': jobs, 'errors': errors}
        # An offline object may become reachable on the next refresh. Do not
        # turn a transient read failure into a cached permanent failure.
        if not errors:
            self.scans.put(key, p.data(value))
        return value

    def listing(self):
        with self.lock:
            return self._listing()

    def _listing(self):
        jobs, errors, sources = [], [], []
        candidates = [('local', self.local, 'refs/heads/')]
        if self.cached:
            candidates.append(('remote', self.cached, 'refs/pw/'))
        bindings = {}
        for origin, source, prefix in candidates:
            raw = git(source.root, 'for-each-ref', '--format=%(refname)', *[prefix + ref for ref in self.refs])
            for ref in raw.decode().splitlines():
                branch = ref[len(prefix):]
                if branch != 'main' and not PRODUCTION_BRANCH.fullmatch(branch):
                    continue
                if not any(branch == pattern or pattern.endswith('/*') and branch.startswith(pattern[:-1])
                           for pattern in self.refs):
                    continue
                try:
                    commit = source.resolve(ref)
                    sources.append({'source': origin, 'ref': ref[len(prefix):], 'commit': commit})
                    value = self.scan(source, commit, None if branch == 'main' else branch.rsplit('/', 1)[1])
                    errors.extend(value['errors'])
                    for job in value['jobs']:
                        identity = (job['puzzle_id'], job['revision'])
                        fingerprint = job.pop('_fingerprint')
                        entry = {**job, 'commit': commit, 'source': origin, 'ref': branch, '_source': source}
                        if identity in bindings and bindings[identity] != fingerprint:
                            for prior in jobs:
                                if (prior['puzzle_id'], prior['revision']) == identity:
                                    prior['conflict'] = True
                            entry['conflict'] = True
                        bindings.setdefault(identity, fingerprint)
                        jobs.append(entry)
                except (ValueError, OSError) as exc:
                    errors.append('Quellstand konnte nicht geladen werden: ' + str(exc))
        remote_commits = {s['commit'] for s in sources if s['source'] == 'remote'}
        remote_match = re.fullmatch(r'(?:https://github\.com/|git@github\.com:)([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?)(?:\.git)?', self.remote or '')
        cloud_repository = 'https://github.com/' + remote_match[1] if remote_match else None
        for job in jobs:
            job['source_url'] = cloud_repository + '/tree/' + job['commit'] if cloud_repository and job['commit'] in remote_commits else None
            job['publication'] = ('Im konfigurierten Remote gefunden' if job['commit'] in remote_commits else
                                  'Nur lokal nachgewiesen; Remote-Sicherung nicht bestätigt')
        return {'jobs': jobs, 'errors': errors, 'sources': sources, 'synced_at': self.synced_at,
                'sync_error': self.sync_error, 'mode': 'remote' if self.remote else 'local'}
