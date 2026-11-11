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
from .sources import git, GitSource, INDEX, JSON_LIMIT
from . import presentation as p


def patterns(values):
    ap.require(isinstance(values, list) and 1 <= len(values) <= 20 and len(set(values)) == len(values), 'Ungültige Refauswahl.')
    for value in values:
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
             'remote': remote_url(remote) if remote else None, 'refs': patterns(refs or ['main', 'content/*'])}
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
        self.refs = patterns(c['refs'])
        self.local = GitSource(c['repository'])
        ap.require(not self.state.is_relative_to(self.local.root) and not self.local.root.is_relative_to(self.state),
                   'Zustandsordner liegt im Projekt.')
        self.remote = remote_url(c['remote']) if c['remote'] else None
        self.cached = None
        self.sync_error, self.synced_at = None, None
        self.lock = threading.RLock()
        if self.remote:
            cache = io.safe(self.state, 'git-cache')
            if not cache.exists():
                cache.mkdir()
                git(cache, 'init', '--bare', '-q')
            # Refuse link/reparse redirection before any cache mutation.
            for name in ('config', 'objects', 'refs'):
                io.safe(self.state, 'git-cache/' + name)
            # A named promisor remote is required for filtered fetch (raw URLs do not
            # establish the promised-object contract). Config is private cache state.
            git(cache, 'config', 'remote.pw-source.url', self.remote)
            git(cache, 'config', 'remote.pw-source.promisor', 'true')
            git(cache, 'config', 'remote.pw-source.partialclonefilter', 'blob:none')
            self.cached = GitSource(cache, self.fetch_object)
            status = io.read(self.state, 'sync.json', JSON_LIMIT, missing=True)
            if status:
                self.synced_at = p.parse(status)['synced_at']

    def fetch(self, *specs, filtered=False):
        # All mutations are confined to this application's private bare cache.
        size = sum(f.stat().st_size for f in (self.cached.root / 'objects').rglob('*') if f.is_file())
        ap.require(size < 384 * 1024 * 1024, 'Gitcache ist voll (512 MiB). Neuen eigenen Zustandsordner einrichten.')
        git(self.cached.root, '-c', 'protocol.allow=never', '-c', 'protocol.https.allow=always',
            '-c', 'protocol.http.allow=always', '-c', 'protocol.ssh.allow=always', '-c', 'protocol.file.allow=always',
            'fetch', '--no-tags', '--no-auto-maintenance', '--no-recurse-submodules', '--no-write-fetch-head',
            *(['--filter=blob:none'] if filtered else []), '--', 'pw-source', *specs, timeout=30)
        after = sum(f.stat().st_size for f in (self.cached.root / 'objects').rglob('*') if f.is_file())
        ap.require(after <= 512 * 1024 * 1024, 'Gitcache überschreitet 512 MiB; neuen eigenen Zustand einrichten.')

    def fetch_object(self, oid):
        from .sources import check_commit
        check_commit(oid)  # Hash grammar also applies to tree-discovered blob OIDs.
        with self.lock:
            self.fetch(oid)

    def refresh(self):
        with self.lock:
            self.sync_error = None
            if self.remote:
                try:
                    specs = ['+refs/heads/' + ref + ':refs/pw/' + ref for ref in self.refs]
                    self.fetch(*specs, filtered=True)
                    self.synced_at = datetime.now(timezone.utc).isoformat()
                    raw = p.data({'synced_at': self.synced_at})
                    temporary = io.safe(self.state, 'sync.tmp')
                    temporary.write_bytes(raw)
                    temporary.replace(io.safe(self.state, 'sync.json'))
                except (ValueError, OSError) as exc:
                    self.sync_error = 'Remote nicht erreichbar oder Anmeldung fehlgeschlagen. Vorhandene Snapshots bleiben lesbar.'
            return self.listing()

    def listing(self):
        jobs, errors, sources = [], [], []
        candidates = [('local', self.local, 'refs/heads/')]
        if self.cached:
            candidates.append(('remote', self.cached, 'refs/pw/'))
        bindings = {}
        for origin, source, prefix in candidates:
            raw = git(source.root, 'for-each-ref', '--format=%(refname)', *[prefix + ref for ref in self.refs])
            for ref in raw.decode().splitlines():
                branch = ref[len(prefix):]
                if not any(branch == pattern or pattern.endswith('/*') and branch.startswith(pattern[:-1])
                           for pattern in self.refs):
                    continue
                try:
                    commit = source.resolve(ref)
                    sources.append({'source': origin, 'ref': ref[len(prefix):], 'commit': commit})
                    index_raw = source.read(commit, INDEX, 8 * JSON_LIMIT, missing=True)
                    if index_raw is None:
                        continue
                    index = index_value(index_raw)
                    for row in index['entries']:
                        file = row['record'].rsplit('/', 1)[0] + '/workspace.json'
                        raw = source.read(commit, file, JSON_LIMIT, missing=True)
                        if raw is None:
                            continue
                        try:
                            projection = p.validate(p.parse(raw))
                            ap.require(projection['puzzle_id'] == row['puzzle_id'] and projection['revision'] == row['revision'],
                                       'Index und Projektion stimmen nicht.')
                            record_raw = source.read(commit, row['record'])
                            p.bind(record_raw, projection['record'])
                            # Cheap collision binding: exact view/record/package bindings; no ZIP reads here.
                            identity = (row['puzzle_id'], row['revision'])
                            fingerprint = io.checksum(raw + record_raw)
                            entry = {'puzzle_id': row['puzzle_id'], 'revision': row['revision'], 'title': projection['title'],
                                     'commit': commit, 'source': origin, 'ref': ref[len(prefix):], 'file': file,
                                     'status': 'Bilder noch nicht geprüft', '_projection': projection, '_source': source}
                            if identity in bindings and bindings[identity] != fingerprint:
                                for prior in jobs:
                                    if (prior['puzzle_id'], prior['revision']) == identity:
                                        prior['conflict'] = True
                                entry['conflict'] = True
                            bindings.setdefault(identity, fingerprint)
                            jobs.append(entry)
                        except (ValueError, OSError, KeyError, TypeError) as exc:
                            errors.append('Ungültige Projektion für ' + row['puzzle_id'] + '/' + row['revision'] + ': ' + str(exc))
                except (ValueError, OSError) as exc:
                    errors.append('Quellstand konnte nicht geladen werden: ' + str(exc))
        remote_commits = {s['commit'] for s in sources if s['source'] == 'remote'}
        for job in jobs:
            job['publication'] = ('Im konfigurierten Remote gefunden' if job['commit'] in remote_commits else
                                  'Nur lokal nachgewiesen; Remote-Sicherung nicht bestätigt')
        return {'jobs': jobs, 'errors': errors, 'sources': sources, 'synced_at': self.synced_at,
                'sync_error': self.sync_error, 'mode': 'remote' if self.remote else 'local'}
