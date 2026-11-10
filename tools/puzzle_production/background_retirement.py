"""Main-bound, revision-scoped retirement of independent background work.

Historical image/ZIP bodies are never fetched. Small committed documents bind
the adopted decision; Git tree identities bind its live image to its declared
HP-W2 output. Present work is checked byte-for-byte before any selected deletion.
"""
from copy import deepcopy
import os
from pathlib import PurePosixPath
import re
import stat
import subprocess

from . import background_contract as bc, catalog_background as background
from . import catalog_io as io, catalog_transaction as tx, categories
from . import content_registry as registry
from .authoring_package import require
from .contract import Aborted, InvalidInput, canonical_bytes
from .reveal_retirement import INDEX, LIMIT, blob_id, index_rows, selection, tree_files


class _History:
    """Read bounded metadata and object identities from one verified main tree."""

    def __init__(self, root, commit):
        self.root, self.commit = root, commit
        require(root == io.external(self.git('rev-parse', '--show-toplevel').decode().strip()),
                'Use the checkout root')
        require(isinstance(commit, str) and re.fullmatch(r'[0-9a-f]{40}', commit),
                'Use the full verified main commit')
        for ref in ('origin/main', 'HEAD'):
            self.git('merge-base', '--is-ancestor', commit, ref)
        self.tree = {}
        for item in self.git('ls-tree', '-rz', commit).split(b'\0'):
            if item:
                metadata, name = item.split(b'\t', 1)
                self.tree[name.decode('utf-8')] = tuple(metadata.decode().split())

    def git(self, *args):
        io.tick()
        result = subprocess.run(['git', *args], cwd=self.root, capture_output=True, timeout=60)
        require(result.returncode == 0, 'Cannot verify background main proof: ' +
                result.stderr.decode(errors='replace').strip())
        io.tick()
        return result.stdout

    def regular(self, name):
        value = self.tree.get(name)
        require(value is not None and value[:2] == ('100644', 'blob'),
                'Missing/nonregular committed background file: ' + name)
        return value

    def size(self, name):
        self.regular(name)
        return int(self.git('cat-file', '-s', self.commit + ':' + name))

    def read(self, name, limit):
        require(self.size(name) <= limit, 'Committed metadata exceeds byte limit: ' + name)
        raw = self.git('show', self.commit + ':' + name)
        require(len(raw) <= limit and self.regular(name)[2] == blob_id(raw),
                'Committed metadata identity differs: ' + name)
        return raw

    def json(self, name, limit=bc.MAX_JSON):
        return io.json_bytes(self.read(name, limit), limit)

    def bound(self, name, ref, limit):
        raw = self.read(name, limit)
        require(len(raw) == ref['bytes'] and io.checksum(raw) == ref['sha256'],
                'Committed background reference differs: ' + name)
        return raw


def _stored_name(value):
    return value['ref']['file'] if value['root'] == '.' else value['root'] + '/' + value['ref']['file']


def _historical_adoption(history, old_registry, old_entry, row):
    from .background_request import validate as validate_request
    identifier, revision = row['puzzle_id'], row['revision']
    directory = selection(identifier, revision)
    record_raw = history.read(row['record'], bc.MAX_JSON)
    request = validate_request(io.json_bytes(record_raw, bc.MAX_JSON))
    require(record_raw == canonical_bytes(request) + b'\n' and
            request['puzzle_id'] == identifier and request['revision'] == revision,
            'Wrong committed background request identity')
    request_ref = background.ref(row['record'], record_raw)
    source_name = background.path(identifier)
    source_ref = background.index(old_registry).get(identifier)
    require(source_ref is not None, 'Background revision has no main source')
    source_raw = history.bound(source_name, source_ref, background.LIMIT)
    source = background.validate(io.json_bytes(source_raw, background.LIMIT), old_entry)
    require(source.get('format') in ('picross-catalog-background-v2', 'picross-catalog-background-v3') and
            source_raw == background.encoded(source), 'Background revision was not adopted on main')
    current = background.current(source)
    expected_adoption = {'request': request_ref, **{key: request[key] for key in
                         ('revision', 'target', 'background', 'authorization')}}
    require(current['adoption'] == expected_adoption and
            current['image_revision'] == request['target']['image_revision'] + 1 and
            request['test_only'] == old_entry['production']['test_only'],
            'Main source does not adopt the selected background request')

    declared = {directory + '/' + ref['file']: ref for ref in request['files']}
    files = set(declared) | {row['record']}
    require({name for name in history.tree if name.startswith(directory + '/')} == files,
            'Committed background work differs from its exact request inventory')
    for name, ref in declared.items():
        require(history.size(name) == ref['bytes'], 'Committed work byte count differs: ' + name)

    documents = {}
    for key in ('manifest', 'decision', 'derivation'):
        stored = request['background'][key]
        name = _stored_name(stored)
        require(name in declared and {**declared[name], 'file': stored['ref']['file']} == stored['ref'],
                'Background document is not bound by its request inventory')
        documents[key] = io.json_bytes(history.bound(name, stored['ref'], bc.MAX_JSON), bc.MAX_JSON)
    manifest = bc.validate_manifest(documents['manifest'])
    require(documents['decision'] == current['decision'] and documents['derivation'] == current['derivation'] and
            manifest['puzzle_id'] == identifier and manifest['test_only'] == request['test_only'],
            'Main selection/derivation differs from the committed work')
    if current['decision']['outcome'] == 'selected':
        candidates = [candidate for candidate in manifest['candidates']
                      if candidate['id'] == current['decision']['candidate_id']]
        require(len(candidates) == 1 and candidates[0]['original'] == current['decision']['original'] and
                candidates[0]['revision'] == current['candidate_revision'] and
                candidates[0]['provenance'] == current['provenance'] and candidates[0]['review'] == current['review'],
                'Main choice/rights/review differs from the committed candidate')

    # The compact prior source and the reveal copy are small/identity-bound
    # context, not a reason to fetch the original raster package or old images.
    context = manifest['context']
    manifest_root = request['background']['manifest']['root']
    require(context['reveal'] is not None and context['reveal_approval'] is not None,
            'Background work lacks its retained context bindings')
    context_source = _stored_name({'root': manifest_root, 'ref': context['reveal_approval']})
    prior_raw = history.bound(context_source, context['reveal_approval'], background.LIMIT)
    require(background.ref(source_name, prior_raw) == request['target']['source'],
            'Committed context is not the requested predecessor source')
    prior = background.validate(io.json_bytes(prior_raw, background.LIMIT), old_entry)
    require(prior_raw == background.encoded(prior) and background.initial(prior) == background.initial(source) and
            background.origin_hash(prior) == request['target']['origin_sha256'] and
            background.current(prior)['image_revision'] == request['target']['image_revision'],
            'Committed predecessor changes the immutable background origin')
    context_reveal = _stored_name({'root': manifest_root, 'ref': context['reveal']})
    from .background_rebind import reveal_hash
    require(context_reveal in declared and declared[context_reveal]['sha256'] == reveal_hash(source) and
            declared[context_reveal]['bytes'] == context['reveal']['bytes'] and
            context['reveal']['sha256'] == reveal_hash(source) and
            history.regular(context_reveal) == history.regular('game/' + old_entry['reveal']),
            'Committed live reveal differs from the retained context')
    definition = background.effective(source)['identity']['definition']
    history.bound('game/' + old_entry['definition'], definition, 2 * 1024 * 1024)
    background.capability(None, {background.CAPABILITY: history.read(background.CAPABILITY, background.CAPABILITY_LIMIT)},
                          required=True)

    asset_name, notice_name = background.asset_path(identifier), background.notice_path(identifier)
    if current['asset'] is None:
        require(asset_name not in history.tree and notice_name not in history.tree,
                'Committed none background has live image/notice files')
    else:
        derivation = request['background']['derivation']
        output_name = str(PurePosixPath(_stored_name(derivation)).parent / current['derivation']['output']['file'])
        output_ref = declared.get(output_name)
        require(output_ref is not None and
                all(output_ref[key] == current['asset'][key] for key in ('sha256', 'bytes')) and
                history.regular(asset_name) == history.regular(output_name),
                'Committed live background is not its adopted HP-W2 output')
        history.bound(notice_name, current['notice'], background.LIMIT)
    runtime = history.json(registry.RUNTIME, LIMIT)
    entries = runtime.get('entries') if isinstance(runtime, dict) else None
    require(isinstance(runtime, dict) and runtime.get('format') == background.RUNTIME_FORMAT and isinstance(entries, list),
            'Committed background runtime generation differs')
    matches = [entry for entry in entries if isinstance(entry, dict) and entry.get('id') == identifier]
    minimal = {'format': background.REGISTRY_FORMAT, 'entries': [old_entry],
               'backgrounds': [{'id': identifier, 'source': source_ref}]}
    expected = background.projection(minimal, {source_name: source_raw})[identifier]
    require(len(matches) == 1 and matches[0].get('background') == expected and
            all(matches[0].get(key) == old_entry[key] for key in
                ('id', 'key', 'save_slot', 'definition', 'reveal', 'visible', 'category_id')),
            'Committed runtime does not contain the adopted background')
    return {'directory': directory, 'row': row, 'request': request, 'request_ref': request_ref,
            'source': source, 'entry': old_entry, 'files': files, 'declared': declared}


def _file_identity(info):
    return io.signature(info), stat.S_IMODE(info.st_mode), info.st_ctime_ns


def _active_fresh(root, state):
    snapshot = state['snapshot']
    require(all(tx.read(root, name) == raw for name, raw in snapshot['texts'].items()) and
            all(tx.file_hash(root, name) == checksum for name, checksum in snapshot['retained'].items()) and
            tx.namespaces(root, snapshot['registry']) == snapshot['namespaces'] and
            io.read(root, INDEX, LIMIT) == state['index_bytes'],
            'Checkout changed during background retirement planning')


def _fresh(root, state):
    _active_fresh(root, state)
    affected = state['affected']
    for start in range(0, len(affected), 20):
        state['history'].git('diff', '--cached', '--quiet', '--', *affected[start:start + 20])
    for proof in state['proofs']:
        expected = set() if proof['absent'] else proof['files']
        require(tree_files(root, proof['directory']) == expected and
                (not proof['absent'] or not io.safe(root, proof['directory']).exists()),
                'Background authoring namespace changed during retirement planning')
    for name, (checksum, size, identity) in state['removed'].items():
        require(io.file_hash(root, name, bc.MAX_PNG) == checksum and
                _file_identity(io.safe(root, name).stat()) == identity,
                'Background work changed during retirement planning: ' + name)


def _prepare_checked(root, revisions, integrated_commit, snapshot=None):
    root = io.external(root)
    history = _History(root, integrated_commit)
    require(isinstance(revisions, (list, tuple)) and revisions, 'Select authoring revisions explicitly')
    directories = []
    for pair in revisions:
        require(isinstance(pair, (list, tuple)) and len(pair) == 2, 'Expected ID and authoring revision')
        directories.append(selection(*pair))
    require(len({name.casefold() for name in directories}) == len(directories), 'Duplicate authoring revisions')
    snapshot = tx.capture(root) if snapshot is None else snapshot
    entries = {entry['id']: entry for entry in snapshot['registry']['entries']}
    index_bytes = io.read(root, INDEX, LIMIT)
    index = io.json_bytes(index_bytes, LIMIT)
    rows = index_rows(index)
    old_rows = index_rows(history.json(INDEX, LIMIT))
    old_catalog = categories.validate(history.json(categories.PATH, 131072))
    old_registry = registry.validate(history.json(registry.REGISTRY, LIMIT), old_catalog)
    old_entries = {entry['id']: entry for entry in old_registry['entries']}
    proofs, removed = [], {}
    for (identifier, revision), directory in zip(revisions, directories):
        require(identifier in entries and identifier in old_entries and directory in old_rows,
                'Background revision is not integrated on main: ' + directory)
        proof = _historical_adoption(history, old_registry, old_entries[identifier], old_rows[directory])
        active = background.load(root, snapshot['registry'], entries[identifier])
        require(active is not None and background.initial(active) == background.initial(proof['source']),
                'Current background has a different immutable origin/identity')
        current, historical = background.current(active), background.current(proof['source'])
        require(current['image_revision'] >= historical['image_revision'] and
                (current['image_revision'] != historical['image_revision'] or active == proof['source']),
                'Current background is not the proven adoption or its later successor')
        files = tree_files(root, directory)
        absent = directory not in rows
        if absent:
            require(not io.safe(root, directory).exists(),
                    'Partial background retirement: revision remains without index entry')
        else:
            require(rows[directory] == proof['row'] and files == proof['files'],
                    'Unmerged background index or revision files')
            for name in sorted(files):
                raw = io.read(root, name, bc.MAX_PNG if name != proof['row']['record'] else bc.MAX_JSON)
                require(history.regular(name)[2] == blob_id(raw), 'Unmerged/modified background work: ' + name)
                if name in proof['declared']:
                    ref = proof['declared'][name]
                    require(len(raw) == ref['bytes'] and io.checksum(raw) == ref['sha256'],
                            'Background work differs from its request inventory: ' + name)
                info = io.safe(root, name).stat()
                require(os.name == 'nt' or not info.st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH),
                        'Background work file mode changed: ' + name)
                removed[name] = (io.checksum(raw), len(raw), _file_identity(info))
        proof.update(current_source=active, current=current['image_revision'] == historical['image_revision'], absent=absent)
        proofs.append(proof)
    affected = sorted(set(snapshot['texts']) | set(snapshot['retained']) | {INDEX} | set(directories))
    state = {'root': root, 'proofs': proofs, 'snapshot': snapshot, 'index': index,
             'index_bytes': index_bytes, 'removed': removed, 'history': history, 'affected': affected}
    _fresh(root, state)
    return state


def _prepare(root, revisions, integrated_commit, snapshot=None):
    try:
        return _prepare_checked(root, revisions, integrated_commit, snapshot)
    except bc.BackgroundError as exc:
        raise InvalidInput('Invalid background retirement source: ' + str(exc)) from exc


def prove(root, revisions, integrated_commit, *, snapshot=None):
    """Return read-only historical/current proofs, including complete absence.

    Used by adoption's post-cleanup no-op path. Its caller must additionally
    require the exact plan target; this proof also permits later valid revisions.
    """
    with io.budget():
        return _prepare(root, revisions, integrated_commit, snapshot)['proofs']


def retire(root, revisions, integrated_commit):
    """Prepare a local diff, preserving every unselected work revision."""
    from . import authoring_builder as builder
    with io.budget():
        state = _prepare(root, revisions, integrated_commit)
        root, removed = state['root'], state['removed']
        present = {proof['directory'] for proof in state['proofs'] if not proof['absent']}
        if not present:
            return {'status': 'no-op', 'revisions': revisions, 'integrated_commit': integrated_commit,
                    'removed_files': 0, 'removed_bytes': 0}
        try:
            # Cooperate with store and the existing authoring builder across
            # the final comparison and index replacement, not just the read.
            with builder.writer(builder.git_root(root) / 'authoring-builder.lock'):
                _fresh(root, state)
                for name, (checksum, size, identity) in removed.items():
                    require(io.file_hash(root, name, bc.MAX_PNG) == checksum and
                            _file_identity(io.safe(root, name).stat()) == identity,
                            'Background work changed before deletion: ' + name)
                    io.safe(root, name).unlink()
                for directory in sorted(present):
                    # Only directories implied by the preflighted file set
                    # belong to this cleanup. A late foreign empty directory
                    # survives and makes the enclosing rmdir fail honestly.
                    owned = {str(parent) for name in removed if name.startswith(directory + '/')
                             for parent in PurePosixPath(name).parents
                             if str(parent).startswith(directory + '/')}
                    for name in sorted(owned, key=lambda item: len(item.split('/')), reverse=True):
                        io.safe(root, name).rmdir()
                    io.safe(root, directory).rmdir()
                _active_fresh(root, state)
                updated = deepcopy(state['index'])
                updated['entries'] = [row for row in updated['entries']
                                      if selection(row['puzzle_id'], row['revision']) not in present]
                registry.atomic_bytes(io.safe(root, INDEX), canonical_bytes(updated) + b'\n')
        except (Exception, KeyboardInterrupt) as exc:
            remaining = []
            for name in sorted(present | {INDEX}):
                try:
                    if (root / name).exists(): remaining.append(str(root / name))
                except OSError:
                    remaining.append(str(root / name) + ' (unreadable)')
            message = 'Background retirement did not complete: ' + (str(exc) or 'interrupted') + \
                      '; remaining paths: ' + ', '.join(remaining)
            if isinstance(exc, (Aborted, KeyboardInterrupt)): raise Aborted(message) from exc
            raise InvalidInput(message) from exc
        return {'status': 'background_production_retired', 'revisions': revisions,
                'integrated_commit': integrated_commit, 'removed_files': len(removed),
                'removed_bytes': sum(value[1] for value in removed.values())}
