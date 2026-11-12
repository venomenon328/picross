"""Bounded, non-executing Git and ZIP reads. Never checks out a data branch."""
from collections import OrderedDict
from io import BytesIO
import os
from pathlib import Path
import re
import stat
import subprocess
import threading
import zipfile

from tools.puzzle_production import authoring_package as ap, catalog_io as io
from tools.puzzle_production.authoring_build_contract import names
from tools.puzzle_production.contract import InvalidInput, exact_keys
from .processes import run, external_environment

SHA1 = re.compile(r'[0-9a-f]{40}\Z')
JSON_LIMIT = 1024 * 1024
INDEX = 'content/authoring/index.json'


def check_commit(value):
    ap.require(isinstance(value, str) and SHA1.fullmatch(value), 'Vollständiger Gitcommit fehlt.')
    return value


def production_path(value):
    ap.relative(value)
    ap.require(value.startswith('content/authoring/'), 'Datei liegt außerhalb der Produktionsablage.')
    return value


def read_path(value):
    """Narrow internal completion evidence; never an HTTP path parameter."""
    ap.relative(value)
    if value in ('content/registry.json', 'game/data/registry.json') or re.fullmatch(
            r'content/packages/pz-[a-z0-9][a-z0-9-]{0,59}/[A-Za-z0-9][A-Za-z0-9._-]{0,31}/manifest\.json', value):
        return value
    return production_path(value)


class LRU:
    """Session-only decoded bytes; never persists original pictures in browser storage."""
    def __init__(self, limit=64 * 1024 * 1024):
        self.limit, self.size, self.hits = limit, 0, 0
        self.items, self.lock = OrderedDict(), threading.RLock()

    def get(self, key):
        with self.lock:
            if key not in self.items:
                return None
            self.hits += 1
            self.items.move_to_end(key)
            return self.items[key]

    def put(self, key, value):
        with self.lock:
            if key in self.items:
                self.size -= len(self.items.pop(key))
            if len(value) > self.limit:
                return
            self.items[key] = value
            self.size += len(value)
            while self.size > self.limit or len(self.items) > 512:
                self.size -= len(self.items.popitem(last=False)[1])


def git(directory, *args, timeout=30):
    env = {k: v for k, v in external_environment().items() if not k.startswith('GIT_')}
    env.update(GIT_OPTIONAL_LOCKS='0', GIT_NO_REPLACE_OBJECTS='1', GIT_NO_LAZY_FETCH='1',
               GIT_TERMINAL_PROMPT='0', GCM_INTERACTIVE='never')
    try:
        result = run(['git', '--no-lazy-fetch', '-c', 'core.hooksPath=' + os.devnull,
                                 '-c', 'core.fsmonitor=false', '-C', str(directory), *args],
                                env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                timeout=timeout)
    except FileNotFoundError as exc:
        raise InvalidInput('Git fehlt. Bitte Git installieren und erneut starten.') from exc
    except subprocess.TimeoutExpired as exc:
        raise InvalidInput('Git antwortet nicht rechtzeitig; vorhandenen Stand weiterverwenden.') from exc
    # stderr can contain credentials from remotes/helpers. Never return it to browser or logs.
    ap.require(result.returncode == 0, 'Git-Zugriff fehlgeschlagen. Quelle oder Anmeldung lokal prüfen.')
    return result.stdout


class GitSource:
    def __init__(self, repository, fetch_object=None, fetch_commit=None):
        self.root = io.external(repository)
        self.fetch_object = fetch_object
        self.fetch_commit = fetch_commit
        ap.require(self.root.is_dir(), 'Projektcheckout fehlt.')
        git(self.root, 'rev-parse', '--git-dir')
        self.cache, self.tree_cache = LRU(), LRU(4 * 1024 * 1024)
        self.commits = LRU(16384)
        self.bytes_read = 0

    def resolve(self, ref):
        ap.require(isinstance(ref, str) and (ref.startswith('refs/') or SHA1.fullmatch(ref)), 'Ungültiger Quellref.')
        commit = check_commit(git(self.root, 'rev-parse', '--verify', ref + '^{commit}').decode().strip())
        self.commits.put(commit, b'1')
        return commit

    def blob(self, commit, name, missing=False):
        check_commit(commit)
        read_path(name)
        if self.commits.get(commit) is None:
            try:
                resolved = self.resolve(commit)
            except InvalidInput:
                ap.require(self.fetch_commit is not None, 'Gebundener historischer Commit fehlt; Quelle aktualisieren.')
                self.fetch_commit(commit)
                resolved = self.resolve(commit)
            ap.require(resolved == commit, 'Historische Quelle muss ein Commit sein.')
        parent = ''
        parts = name.split('/')
        for number, part in enumerate(parts):
            tree = commit + (':' + parent if parent else '')
            raw = self.tree_cache.get(tree)
            if raw is None:
                # Tree object size is checked before ls-tree's decoded expansion.
                size = int(git(self.root, 'cat-file', '-s', tree))
                ap.require(size <= 8 * 1024 * 1024, 'Gitbaum ist zu groß.')
                raw = git(self.root, 'ls-tree', '-z', tree)
                self.tree_cache.put(tree, raw)
            entries = []
            for item in raw.split(b'\0'):
                if not item:
                    continue
                meta, leaf = item.split(b'\t', 1)
                try:
                    leaf = leaf.decode('utf-8')
                except UnicodeDecodeError as exc:
                    raise InvalidInput('Ungültiger Gitdateiname.') from exc
                if leaf.casefold() == part.casefold():
                    entries.append((leaf, *meta.decode('ascii').split()))
            if not entries and missing:
                return None
            ap.require(len(entries) == 1 and entries[0][0] == part, 'Datei fehlt oder Gitpfad kollidiert: ' + name)
            _, mode, kind, oid = entries[0]
            if number < len(parts) - 1:
                ap.require(mode == '040000' and kind == 'tree', 'Gitpfad enthält Link oder Submodul.')
            else:
                ap.require(mode in ('100644', '100755') and kind == 'blob', 'Nur reguläre Gitdateien sind lesbar.')
            parent = parent + '/' + part if parent else part
        return oid

    def read(self, commit, name, limit=JSON_LIMIT, missing=False):
        oid = self.blob(commit, name, missing)
        if oid is None:
            return None
        try:
            size = int(git(self.root, 'cat-file', '-s', oid))
        except InvalidInput:
            ap.require(self.fetch_object is not None, 'Gebundenes Gitobjekt fehlt; konfigurierte Quelle aktualisieren.')
            self.fetch_object(oid)
            size = int(git(self.root, 'cat-file', '-s', oid))
        ap.require(size <= limit, 'Gitdatei überschreitet die Lesegrenze: ' + name)
        raw = self.cache.get(oid)
        if raw is None:
            raw = git(self.root, 'cat-file', 'blob', oid)
            ap.require(len(raw) == size, 'Gitblob ist unvollständig.')
            self.bytes_read += len(raw)
            self.cache.put(oid, raw)
        return raw


class LocalSource:
    """Projector only: measure actual working sources, recheck before publication."""
    def __init__(self, root):
        self.root, self.seen = io.external(root), {}
        self.history = GitSource(root)

    def read(self, commit, name, limit=JSON_LIMIT, missing=False):
        read_path(name)
        if commit is not None:
            return self.history.read(commit, name, limit, missing)
        raw = io.read(self.root, name, limit, missing=missing)
        key = (name, limit)
        value = (None if raw is None else io.checksum(raw),
                 None if raw is None else (*io.signature(io.safe(self.root, name).stat()),
                                           io.safe(self.root, name).stat().st_ctime_ns))
        ap.require(key not in self.seen or self.seen[key] == value, 'Quellen wurden zwischenzeitlich geändert: ' + name)
        self.seen[key] = value
        return raw

    def recheck(self):
        for name, limit in list(self.seen):
            self.read(None, name, limit, missing=self.seen[(name, limit)][0] is None)


class Archive:
    """Inspect complete namespace, read only requested members; no extraction."""
    def __init__(self, raw):
        ap.require(len(raw) <= ap.MAX_ZIP, 'ZIP überschreitet 128 MiB.')
        self.stream = BytesIO(raw)
        try:
            self.zip = zipfile.ZipFile(self.stream)
            infos = self.zip.infolist()
            ap.require(len(infos) <= ap.MAX_FILES * 2, 'Zu viele ZIP-Einträge.')
            all_names, file_names, total = [], [], 0
            for item in infos:
                name = ap.relative(item.filename.rstrip('/'))
                all_names.append(name)
                mode = item.external_attr >> 16
                ap.require(stat.S_IFMT(mode) in (0, stat.S_IFREG, stat.S_IFDIR) and not item.flag_bits & 1,
                           'ZIP enthält Spezialdatei oder verschlüsselten Eintrag.')
                ap.require((stat.S_IFMT(mode) != stat.S_IFDIR or item.is_dir()) and
                           (stat.S_IFMT(mode) != stat.S_IFREG or not item.is_dir()), 'ZIP-Dateitypkonflikt.')
                ap.require(item.file_size <= ap.MAX_FILE, 'ZIP-Mitglied überschreitet 64 MiB.')
                total += item.file_size
                if not item.is_dir():
                    file_names.append(name)
            ap.require(len(file_names) <= ap.MAX_FILES and total <= ap.MAX_TOTAL, 'ZIP überschreitet Entpackgrenzen.')
            ap.require(len({n.casefold() for n in all_names}) == len(all_names), 'ZIP-Namen kollidieren.')
            names(file_names)  # Includes parent aliases and file/directory collisions.
            spellings = {}
            leaves = {n.casefold() for n in file_names}
            for name in all_names:
                parts = name.split('/')
                for n in range(1, len(parts) + 1):
                    prefix = '/'.join(parts[:n])
                    ap.require(spellings.setdefault(prefix.casefold(), prefix) == prefix, 'ZIP-Elternalias.')
                    ap.require(n == len(parts) or prefix.casefold() not in leaves, 'ZIP-Datei/Verzeichnis-Konflikt.')
            roots = {n.split('/')[0] for n in file_names}
            self.prefix = '' if 'handoff.json' in file_names else next(iter(roots)) + '/' if len(roots) == 1 else None
            ap.require(self.prefix is not None, 'ZIP hat keinen eindeutigen Paketwurzelpfad.')
            self.files = {n[len(self.prefix):]: n for n in file_names if n.startswith(self.prefix)}
        except (zipfile.BadZipFile, ValueError, NotImplementedError) as exc:
            raise InvalidInput('Ungültiges ZIP.') from exc

    def read(self, name, limit=ap.MAX_FILE):
        ap.relative(name)
        ap.require(name in self.files, 'ZIP-Datei fehlt: ' + name)
        info = self.zip.getinfo(self.files[name])
        ap.require(info.file_size <= limit, 'ZIP-Datei überschreitet Lesegrenze.')
        try:
            with self.zip.open(info) as stream:
                raw = stream.read(limit + 1)
                ap.require(len(raw) <= limit and stream.read(1) == b'' and len(raw) == info.file_size,
                           'ZIP-Dateigröße stimmt nicht.')
            return raw  # EOF checks CRC in ZipExtFile.
        except (zipfile.BadZipFile, RuntimeError, NotImplementedError, OSError) as exc:
            raise InvalidInput('ZIP-Datei beschädigt oder CRC falsch.') from exc

    def close(self):
        self.zip.close()
        self.stream.close()
