"""Configured local refs and optional remote sync into a private bare cache."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import threading
from urllib.parse import urlsplit
from urllib.parse import urlencode
from urllib.request import Request, build_opener, HTTPRedirectHandler

from tools.puzzle_production import authoring_package as ap, catalog_io as io
from tools.puzzle_production.authoring_builder import index_value
from tools.puzzle_production.contract import exact_keys
from .sources import git, GitSource, INDEX, JSON_LIMIT, LRU
from . import presentation as p

DEFAULT_REFS = ['main', 'content/pw/*']
PRODUCTION_BRANCH = re.compile(r'content/pw/pz-[a-z0-9]+(?:-[a-z0-9]+)*\Z')
CACHE = 'git-cache-pw-v1'
SYNC = 'sync-pw-v1.json'


def github_identity(url):
    return bool(re.fullmatch(
        r'(?:https://github\.com/|git@github\.com:|ssh://git@github\.com/)'
        r'venomenon328/picross(?:\.git)?', url or ''))


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *_args, **_kwargs):
        return None


def github_get(path):
    """Only fixed public GitHub reads; no credential discovery or redirects."""
    try:
        request = Request('https://api.github.com/repos/venomenon328/picross' + path,
                          headers={'Accept': 'application/vnd.github+json',
                                   'User-Agent': 'Picross-Production-Workspace',
                                   'X-GitHub-Api-Version': '2022-11-28'})
        with build_opener(NoRedirect).open(request, timeout=10) as response:
            return p.parse(response.read(8 * JSON_LIMIT + 1), 8 * JSON_LIMIT)
    except (ValueError, OSError) as exc:
        raise ap.InvalidInput('GitHub-Status nicht prüfbar (Zugang, Rate-Limit oder Netzwerk). Entfernung gesperrt.') from exc


class ProductionRemoval:
    """One conditional ref deletion, never a general Git writer.

    Tests subclass target()/pull_requests() for their owned synthetic bare remote.
    No config, environment or HTTP switch enables that adapter in the product.
    All methods are called under the repository's transaction lock.
    """
    def __init__(self, repository):
        self.repository = repository

    def availability(self, job):
        if not self.repository.remote:
            return 'Nur lokale Gitstände: keine Remoteentfernung möglich.'
        if job['source'] != 'remote':
            return 'Diese Quelle ist lokal. Die zugehörige Remotequelle ausdrücklich auswählen.'
        if job['ref'] != 'content/pw/' + job['puzzle_id'] or not PRODUCTION_BRANCH.fullmatch(job['ref']):
            return 'Nur der gesamte zugeordnete Produktionsbranch ist entfernbar; main bleibt erhalten.'
        if job.get('conflict'):
            return 'Widersprüchliche Quellen: erst die Veröffentlichung klären.'
        if self.repository.sync_error:
            return 'Remoteansicht ist veraltet oder offline. Quellen erst erfolgreich aktualisieren.'
        if not github_identity(self.repository.remote):
            return 'Entfernung nur für den konfigurierten GitHub-Remote venomenon328/picross über HTTPS/SSH freigegeben.'
        return None

    def target(self):
        repo = self.repository
        ap.require(github_identity(repo.remote), 'Zielrepository ist nicht zur Entfernung freigegeben.')
        self.check_urls()
        metadata = github_get('')
        ap.require(isinstance(metadata, dict) and metadata.get('full_name') == 'venomenon328/picross' and metadata.get('private') is False,
                   'GitHub-Repositoryidentität oder öffentliche PR-Sicht nicht bestätigt.')
        return 'venomenon328/picross'

    def check_urls(self):
        repo = self.repository
        ap.require(repo.cached is not None, 'Kein Remote eingerichtet.')
        for root in (repo.local.root, repo.cached.root):
            # Includes effective system/global/local config, without exposing values.
            config = git(root, 'config', '--null', '--list').decode('utf-8')
            keys = [entry.split('\n', 1)[0].lower() for entry in config.split('\0') if entry]
            ap.require(not any(k.startswith('url.') and k.endswith(('.insteadof', '.pushinsteadof')) for k in keys),
                       'Git-URL-Umschreibung gefunden; eindeutiges Löschziel nicht nachweisbar.')
            effective = git(root, 'ls-remote', '--get-url', repo.remote).decode().strip()
            ap.require(effective == repo.remote, 'Effektives Remoteziel weicht von der Einrichtung ab.')
            for name in git(root, 'remote').decode().splitlines():
                urls = git(root, 'remote', 'get-url', '--all', name).decode().splitlines()
                if repo.remote in urls or any(github_identity(u) for u in urls):
                    pushed = git(root, 'remote', 'get-url', '--push', '--all', name).decode().splitlines()
                    ap.require(urls == [repo.remote] and pushed == [repo.remote],
                               'Abweichende oder mehrere Fetch-/Pushziele gefunden. Entfernung gesperrt.')

    def remote_head(self, ref):
        from .sources import check_commit
        raw = git(self.repository.cached.root, '-c', 'http.followRedirects=false',
                  'ls-remote', '--refs', '--', self.repository.remote, ref).decode().splitlines()
        ap.require(len(raw) <= 1, 'Remote-Ref ist nicht eindeutig.')
        if not raw:
            return None
        sha, actual = raw[0].split('\t')
        ap.require(actual == ref, 'Remote lieferte einen anderen Ref.')
        return check_commit(sha)

    def pull_requests(self, branch):
        rows = []
        for page in range(1, 101):
            values = github_get('/pulls?' + urlencode({'state': 'all', 'head': 'venomenon328:' + branch,
                                                       'per_page': 100, 'page': page}))
            ap.require(isinstance(values, list), 'GitHub-PR-Antwort ist ungültig.')
            for value in values:
                ap.require(isinstance(value, dict) and value.get('state') in ('open', 'closed') and
                           isinstance(value.get('number'), int) and 'merged_at' in value,
                           'GitHub-PR-Status ist unvollständig.')
                head = value.get('head') or {}
                ap.require(isinstance(head, dict) and head.get('ref') == branch and isinstance(head.get('repo'), dict) and
                           head['repo'].get('full_name') == 'venomenon328/picross',
                           'GitHub-PR-Quelle ist nicht eindeutig zugeordnet.')
                rows.append({'number': value['number'], 'state': value['state'],
                             'merged': value['merged_at'] is not None})
            if len(values) < 100:
                return rows
        raise ap.InvalidInput('GitHub-PR-Abfrage nicht vollständig; Entfernung gesperrt.')

    def local_state(self, ref, expected):
        from .sources import check_commit
        root = self.repository.local.root
        raw = git(root, 'for-each-ref', '--format=%(refname) %(objectname) %(symref)', ref).decode().splitlines()
        # for-each-ref also matches descendants: accept only the exact ref.
        matches = [line.split(' ', 2) for line in raw if line.startswith(ref + ' ')]
        ap.require(len(matches) <= 1, 'Lokaler Ref ist nicht eindeutig.')
        ap.require(not matches or len(matches[0]) == 3 and not matches[0][2], 'Symbolischer lokaler Ref ist kein Löschziel.')
        local = check_commit(matches[0][1]) if matches else None
        worktrees = git(root, 'worktree', 'list', '--porcelain', '-z').decode('utf-8')
        checked_out = sum(item == 'branch ' + ref for item in worktrees.split('\0'))
        blockers = []
        if checked_out:
            blockers.append(f'Zielbranch ist in {checked_out} Worktree(s) ausgecheckt. Dort zuerst sicher auf einen anderen Branch wechseln.')
        if local is not None and local != expected:
            blockers.append('Lokaler Branch hat eine andere SHA (eigene oder abweichende Commits). Zuerst außerhalb des Assistenten sichern und klären.')
        return {'sha': local, 'checked_out': checked_out}, blockers

    def main_state(self, puzzle_id):
        repo = self.repository
        sha = self.remote_head('refs/heads/main')
        ap.require(sha is not None, 'Remote-main nicht prüfbar; Entfernung gesperrt.')
        # A private-cache read of the fresh main tip, never a local/main mutation.
        raw = repo.cached.read(sha, INDEX, 8 * JSON_LIMIT, missing=True)
        revisions = [e['revision'] for e in index_value(raw)['entries'] if e['puzzle_id'] == puzzle_id] if raw else []
        registry = repo.cached.read(sha, 'content/registry.json', 8 * JSON_LIMIT, missing=True)
        registered = False
        if registry:
            value = p.parse(registry, 8 * JSON_LIMIT)
            ap.require(isinstance(value, dict) and isinstance(value.get('entries'), list) and
                       all(isinstance(row, dict) and isinstance(row.get('id'), str) for row in value['entries']),
                       'Mainkatalog nicht prüfbar.')
            registered = any(row.get('id') == puzzle_id for row in value['entries'])
        return {'commit': sha, 'revisions': sorted(revisions), 'registered': registered}

    def probe(self, job):
        reason = self.availability(job)
        ap.require(reason is None, reason or '')
        repository = self.target()
        branch, expected = job['ref'], job['commit']
        ref = 'refs/heads/' + branch
        actual = self.remote_head(ref)
        ap.require(actual is not None, 'Remote-Branch fehlt bereits. Quellen neu laden; keine Entfernung ausgeführt.')
        ap.require(actual == expected, 'Remote-Head wurde geändert. Neueren Stand laden und erneut vorprüfen.')
        local, blockers = self.local_state(ref, expected)
        prs = self.pull_requests(branch)
        if any(row['state'] == 'open' for row in prs):
            blockers.append('Offener Pull Request für diesen Branch: Entfernung gesperrt.')
        main = self.main_state(job['puzzle_id'])
        scan = self.repository.scan(self.repository.cached, expected, job['puzzle_id'])
        ap.require(not scan['errors'], 'Nicht alle Produktionsrevisionen sind lesbar. Entfernung gesperrt.')
        revisions = sorted({row['revision'] for row in scan['jobs']})
        ap.require(job['revision'] in revisions, 'Ausgewählte Revision ist nicht mehr nachgewiesen.')
        warnings = []
        if any(row['state'] == 'closed' and not row['merged'] for row in prs):
            warnings.append('Geschlossener, nicht gemergter PR vorhanden. Seine Produktion wird durch die Branchentfernung nicht integriert.')
        if main['revisions'] or main['registered'] or any(row['merged'] for row in prs):
            warnings.append('Mainintegration bzw. gemergter PR vorhanden: integrierte Inhalte bleiben auf main erhalten.')
        return {'repository': repository, 'source': 'remote', 'branch': branch, 'ref': ref,
                'sha': expected, 'puzzle_id': job['puzzle_id'], 'title': job['title'], 'revisions': revisions,
                'local': local, 'prs': prs, 'main': main, 'warnings': warnings, 'blockers': blockers}

    def push_delete(self, facts):
        # Explicit URL + single refspec: no named-remote mirror/refspec/pushurl defaults.
        # Lease is enforced by receive-pack even if the tip changes AFTER the probe.
        git(self.repository.cached.root, '-c', 'http.followRedirects=false', '-c', 'protocol.allow=never',
            '-c', 'protocol.https.allow=always', '-c', 'protocol.ssh.allow=always',
            '-c', 'protocol.file.allow=always', '-c', 'push.followTags=false',
            'push', '--porcelain', '--no-verify', '--no-follow-tags', '--no-signed',
            '--recurse-submodules=no', '--receive-pack=git-receive-pack',
            '--force-with-lease=' + facts['ref'] + ':' + facts['sha'],
            '--', self.repository.remote, ':' + facts['ref'])

    def remove(self, job, facts):
        fresh = self.probe(job)
        ap.require(not fresh['blockers'], ' '.join(fresh['blockers']))
        ap.require(fresh == facts, 'Vorprüfungsbefunde haben sich geändert. Neu vorprüfen und bestätigen.')
        try:
            self.push_delete(facts)
        except ValueError:
            return {'removed': False, 'message': 'Push abgelehnt oder nicht rechtzeitig bestätigt (Lease, Rechte oder Netzwerk). Ausgang nicht als Erfolg bestätigt; Quellen neu prüfen.'}
        try:
            absent = self.remote_head(facts['ref']) is None
        except ValueError:
            absent = False
        if not absent:
            return {'removed': False, 'message': 'Push beendet, aber Fehlen des Remote-Refs nicht bestätigt. Quellen neu prüfen; kein Erfolg nachgewiesen.'}
        return {'removed': True, 'message': 'Remote-Branch entfernt und sein Fehlen geprüft. Maininhalte und lokale Quellen bleiben erhalten.'}

    def local_probe(self, facts):
        self.target()
        ap.require(self.remote_head(facts['ref']) is None, 'Remote-Branch ist wieder vorhanden. Lokale Bereinigung gesperrt.')
        local, blockers = self.local_state(facts['ref'], facts['sha'])
        ap.require(not blockers, ' '.join(blockers))
        ap.require(local['sha'] == facts['sha'], 'Lokaler Ref fehlt oder wurde geändert. Keine lokale Bereinigung.')

    def remove_local(self, facts):
        self.local_probe(facts)
        git(self.repository.local.root, 'update-ref', '--no-deref', '-d', facts['ref'], facts['sha'])
        local, _ = self.local_state(facts['ref'], facts['sha'])
        ap.require(local['sha'] is None, 'Lokale Refentfernung nicht bestätigt.')


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


def configure(repository, state, *, remote=None, refs=None, launcher=False):
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
    ap.require(not any(f for f in state.iterdir() if not (launcher and f.name == '.launcher' and f.is_dir())),
               'Neuer eigener, leerer Zustandsordner erforderlich.')
    temporary = io.safe(state, 'config-setup.tmp')
    try:
        with temporary.open('xb') as stream:
            stream.write(p.data(value))
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, config)  # Publish complete bytes, never replace existing configuration.
    finally:
        temporary.unlink(missing_ok=True)
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
                    # Fetch fails on an explicitly selected ref that disappeared.
                    # Observe first, then prune only absent exact refs after a successful fetch.
                    advertised = git(self.cached.root, 'ls-remote', '--refs', '--', self.remote,
                                     *['refs/heads/' + ref for ref in self.refs]).decode().splitlines()
                    present = {line.split('\t')[1] for line in advertised}
                    missing = [ref for ref in self.refs if '*' not in ref and 'refs/heads/' + ref not in present]
                    specs = ['+refs/heads/' + ref + ':refs/pw/' + ref for ref in self.refs if ref not in missing]
                    # Prune only the destinations of these explicit refspecs. Atomic
                    # ref updates keep the previous cache intact on a failed fetch.
                    if specs:
                        self.fetch(*specs, filtered=True, prune=True, shallow=True)
                    for ref in missing:
                        git(self.cached.root, 'update-ref', '-d', 'refs/pw/' + ref)
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
