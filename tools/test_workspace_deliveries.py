"""PW2-C: small synthetic Git deliveries, not production certification.

The metadata-only delivery helper intentionally creates no playable package.
It can follow a genuine current_fixture early step for the one-time UI probe.
"""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.production_workspace import current_view as cv, presentation as p
from tools.production_workspace.repository import Repository, configure
from tools.production_workspace.sources import GitSource, INDEX, git
from tools.puzzle_production import catalog_io as io, catalog_background as bg
from tools.puzzle_production.authoring_finalization import RECORD_KEYS
from tools.puzzle_production import content_registry as registry, reveal_source as reveal
from tools.puzzle_production.contract import digest
from tools.test_production_workspace import commit

ID = 'pz-workspace-test'


def put(root, name, value):
    raw = p.data(value) if not isinstance(value, bytes) else value
    target = root / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    return {'file': name, 'sha256': io.checksum(raw), 'bytes': len(raw)}


def metadata_job(root, revision, *, puzzle_id=ID, state='reveal_review'):
    """Indexed closed projection and record shape; no image/package proof claimed."""
    directory = f'content/authoring/{puzzle_id}/{revision}'
    record = dict.fromkeys(RECORD_KEYS | {'raster_selection', 'presentation', 'candidate'})
    record.update(format='picross-authoring-record-v3', puzzle_id=puzzle_id, revision=revision,
                  state=state, category_id='synthetic', blockers=[], document_revision=1,
                  build_request_sha256='1' * 64, repo_commit='a' * 40, inventory_sha256='2' * 64,
                  rulebook={'version': '0.8.0', 'file': 'rulebook.md', 'sha256': '3' * 64},
                  handoff={'file': directory + '/handoff.json', 'sha256': '4' * 64},
                  package={'file': directory + '/package.zip', 'sha256': '5' * 64, 'bytes': 17},
                  final_editorial_approval={'file': directory + '/approval.json', 'sha256': '6' * 64},
                  reveal_options=[], parameters=[], verification={'effective_state': state},
                  next_action='TEST ONLY', next_step='TEST ONLY · unverified synthetic metadata')
    record['package'] = put(root, directory + '/package.zip', b'TEST ONLY bytes, deliberately not a playable package\n')
    record['handoff'] = put(root, directory + '/handoff.json', {'test_only': True})
    record['final_editorial_approval'] = put(root, directory + '/approval.json', {'test_only': True})
    projection = {'format': p.CURRENT_FORMAT, 'puzzle_id': puzzle_id, 'revision': revision,
                  'record': {'commit': None, **put(root, directory + '/record.json', record)},
                  'title': 'TEST ONLY · synthetic delivery', 'assets': [], 'offers': []}
    put(root, directory + '/workspace.json', projection)
    index = p.parse((root / INDEX).read_bytes()) if (root / INDEX).exists() else {'format': 'picross-authoring-index-v1', 'entries': []}
    index['entries'].append({'puzzle_id': puzzle_id, 'revision': revision, 'record': directory + '/record.json'})
    put(root, INDEX, index)
    publish_pointer(root, puzzle_id, revision)
    return record


def publish_pointer(root, puzzle_id, revision):
    directory = f'content/authoring/{puzzle_id}/{revision}'
    value = {'format': cv.FORMAT, 'puzzle_id': puzzle_id, 'revision': revision}
    for field, leaf in (('record', 'record.json'), ('projection', 'workspace.json')):
        name = directory + '/' + leaf
        value[field] = cv.reference(name, (root / name).read_bytes())
    put(root, cv.path(puzzle_id), value)


def background_metadata(record, entry):
    """Tiny valid none-authority, declaring synthetic tool data without a run."""
    from tools.puzzle_production import background_contract as bc
    def ref(name, value):
        raw = p.data(value)
        return {'file': name, 'sha256': io.checksum(raw), 'bytes': len(raw)}
    tool = {'id': 'picross-background-1', 'commit': 'a' * 40, 'dirty': False,
            'versions': {'python': 'synthetic', 'pillow': '12.3.0', 'zlib': 'synthetic', 'littlecms': 'synthetic'},
            'modules': [{'file': 'tools/puzzle_production/' + name + '.py', 'sha256': '0' * 64}
                        for name in ('__init__', 'authoring_package', 'background_assets', 'background_contract',
                                     'background_io', 'catalog_io', 'contract', 'image_normalization', 'operation_diagnostics')]}
    manifest = ref('background/work.json', {'test_only': True})
    declaration = {'actor': 'TEST ONLY', 'timestamp_utc': '2026-11-13T00:00:00Z',
                   'statement': 'Synthetic explicit background waiver.', 'evidence': ref('evidence.txt', {'test_only': True})}
    decision = {'format': 'picross-background-decision-v1', 'puzzle_id': record['puzzle_id'], 'job_id': 'synthetic',
                'revision': 'd01', 'background_revision': 'bg01', 'manifest': manifest, 'outcome': 'none',
                'candidate_id': None, 'original': None, 'profile': None, **declaration,
                'presented_package': None, 'previous_decision': None, 'carried_from': None,
                'accepted_deviations': [], 'test_only': True}
    decision_ref = ref('background/decision.json', decision)
    request = {'format': 'picross-background-derive-request-v1', 'manifest': manifest, 'decision': decision_ref,
               'source': None, 'profile': deepcopy(bc.PROFILE), 'expected_tool_sha256': digest(tool), 'output': 'derived/bg01'}
    derivation = {'format': 'picross-background-derivation-v1', 'request': request, 'request_sha256': digest(request),
                  **{key: decision[key] for key in ('puzzle_id', 'job_id', 'background_revision', 'outcome', 'candidate_id')},
                  'manifest': manifest, 'decision': decision_ref, 'source': None, 'profile': deepcopy(bc.PROFILE),
                  'profile_sha256': digest(bc.PROFILE), 'tool': tool, 'tool_sha256': digest(tool), 'output': None,
                  'diagnostics': {'source': None, 'output': None, 'upscaled': None}, 'test_only': True}
    stored = lambda value: {'storage': 'package', 'root': '.', 'ref': value}
    binding = {'manifest': stored(manifest), 'decision': stored(decision_ref),
               'derivation': stored(ref('background/derivation.json', derivation)), 'outcome': 'none',
               'candidate_id': None, 'original': None, 'output': None, 'profile_sha256': digest(bc.PROFILE)}
    original = {'puzzle_id': record['puzzle_id'], 'revision': record['revision'],
                'original_zip_sha256': record['package']['sha256'], 'handoff_sha256': record['handoff']['sha256'],
                'inventory_sha256': record['inventory_sha256']}
    approval = {'format': 'picross-editorial-approval-v2', **{key: declaration[key] for key in ('actor', 'timestamp_utc', 'statement')},
                **original, 'test_only': True, 'selection': {'variant': 'synthetic', 'matrix_hash': 'a' * 64,
                    'logic_hash': 'b' * 64, 'reveal': {'file': 'reveal.png', 'sha256': entry['production']['reveal_sha256']}},
                'background': binding}
    source = {'format': bg.FORMAT, 'puzzle_id': entry['id'], 'identity': {'key': entry['key'], 'save_slot': entry['save_slot'],
                  'definition': {'file': 'game/' + entry['definition'], 'sha256': entry['production']['definition_sha256'], 'bytes': 4},
                  'runtime_revision': 1},
              'origin': {'package': entry['production']['package'], 'export_manifest_sha256': '0' * 64,
                         'original_package': original, 'manifest': binding['manifest'],
                         'approval_ref': ref('approval.json', approval), 'approval': approval},
              'image_revision': 1, 'candidate_revision': None, 'decision': decision, 'derivation': derivation,
              'provenance': None, 'review': None, 'asset': None, 'notice': None, 'test_only': True}
    return source, approval


def delivery_fixture(root, *, puzzle_id=ID, revision='r02', with_background=False):
    """Leave registered r02 at HEAD on the caller's production branch.

    All already indexed steps are retained byte-for-byte in registration.
    Returns bound registration/head, metadata originals and paths. No solver,
    image or completion writer runs; use current_fixture for UI-readable r01.
    """
    branch = git(root, 'branch', '--show-current').decode().strip()
    record = metadata_job(root, revision, puzzle_id=puzzle_id, state='editorially_approved')
    directory = f'content/packages/{puzzle_id}/{revision}'
    stem = puzzle_id.removeprefix('pz-').replace('-', '_')
    entry = {'id': puzzle_id, 'key': puzzle_id, 'save_slot': stem,
             'definition': 'data/content/' + stem + '.json', 'reveal': 'art/content/' + stem + '.png',
             'visible': True, 'category_id': 'synthetic', 'production': {
                 'package': directory, 'package_sha256': '0' * 64, 'revision': revision,
                 'width': 2, 'height': 2, 'mode': 'mono', 'difficulty': {}, 'status': 'registered',
                 'blockers': [], 'test_only': True, 'definition_sha256': '7' * 64, 'reveal_sha256': '8' * 64}}
    background_source = None
    if with_background:
        background_source, approval = background_metadata(record, entry)
        record['background'] = {key: approval['background'][key] for key in ('manifest', 'decision', 'derivation')}
        record['background']['history'] = None
        record['final_editorial_approval'] = put(root, f'content/authoring/{puzzle_id}/{revision}/approval.json', approval)
        ref = put(root, f'content/authoring/{puzzle_id}/{revision}/record.json', record)
        name = f'content/authoring/{puzzle_id}/{revision}/workspace.json'
        projection = p.parse((root / name).read_bytes())
        projection['record'] = {'commit': None, **ref}
        put(root, name, projection)
        publish_pointer(root, puzzle_id, revision)
    manifest = {'format': 'picross-target-export-v6', 'definition_id': puzzle_id, 'package_revision': revision,
                'technical': True, 'editorial_approved': True, 'input': {'original_package': record['package']},
                'handoff_sha256': record['handoff']['sha256'], 'inventory_sha256': record['inventory_sha256'],
                'approval_sha256': record['final_editorial_approval']['sha256'],
                'files': {'runtime/art/content/' + stem + '.txt': '9' * 64}}
    manifest_ref = put(root, directory + '/manifest.json', manifest)
    entry['production']['package_sha256'] = manifest_ref['sha256']
    catalog = {'format': registry.METADATA_FORMAT, 'entries': [entry], 'backgrounds': [],
               'metadata': [{'id': puzzle_id, 'name': 'Synthetic', 'category_id': 'synthetic'}]}
    if background_source is not None:
        background_source['origin']['export_manifest_sha256'] = manifest_ref['sha256']
        bg.validate(background_source, entry)
        ref = put(root, bg.path(puzzle_id), background_source)
        catalog['backgrounds'] = [{'id': puzzle_id, 'source': ref}]
    runtime = {'format': registry.IMAGE_RUNTIME_FORMAT,
               'entries': [{k: entry[k] for k in ('id', 'key', 'save_slot', 'definition', 'reveal')}]}
    registry_ref = put(root, registry.REGISTRY, catalog)
    runtime_ref = put(root, registry.RUNTIME, runtime)
    registration = commit(root)
    integration = {'operation': 'register', 'commit': registration,
                   'manifest': manifest_ref, 'registry': registry_ref, 'runtime': runtime_ref}
    record.update(state='registered', integration=integration, blockers=[],
                  next_step='5 · Lokal registriert; unabhängiges Review und Git-/Mainabschluss prüfen')
    name = f'content/authoring/{puzzle_id}/{revision}/record.json'
    record_ref = put(root, name, record)
    projection_name = name.replace('record.json', 'workspace.json')
    projection = p.parse((root / projection_name).read_bytes())
    projection['record'] = {'commit': None, **record_ref}
    put(root, projection_name, projection)
    publish_pointer(root, puzzle_id, revision)
    head = commit(root)
    return {'branch': branch, 'registration': registration, 'head': head, 'manifest': manifest,
            'manifest_ref': manifest_ref, 'entry': entry, 'registry': catalog, 'runtime': runtime,
            'record': record, 'record_file': name, 'projection_file': projection_name, 'background': background_source}


def integrate_fixture(root, delivery, *, mode='copy', receipt=None):
    """Integrate into main, then restore the caller's branch. Return main SHA.

    copy models an unchanged batch import with no shared delivery ancestry;
    merge and squash exercise ordinary Git paths. Optional v1/v3 retirement
    replaces only the package reference with an existing-format compact receipt.
    """
    previous = git(root, 'branch', '--show-current').decode().strip()
    git(root, 'checkout', '-q', 'main')
    if mode in ('merge', 'squash'):
        git(root, '-c', 'user.name=PW synthetic', '-c', 'user.email=pw@example.invalid',
            'merge', '--no-ff' if mode == 'merge' else '--squash', '--no-edit', delivery['head'])
        if mode == 'squash':
            commit(root)
    else:
        put(root, delivery['manifest_ref']['file'], delivery['manifest'])
        put(root, registry.REGISTRY, delivery['registry'])
        put(root, registry.RUNTIME, delivery['runtime'])
        if delivery['background'] is not None:
            put(root, bg.path(delivery['entry']['id']), delivery['background'])
        commit(root)
    if receipt is not None:
        value = {'format': receipt, 'entry': deepcopy(delivery['entry']),
                 'integrated_commit': git(root, 'rev-parse', 'HEAD').decode().strip(), 'notice_sha256': '9' * 64}
        catalog = deepcopy(delivery['registry'])
        if receipt == reveal.BACKGROUND_RECEIPT:
            value['background'] = bg.receipt_binding(delivery['background'], catalog['backgrounds'][0]['source'])
        if receipt == reveal.EDITOR_RECEIPT:
            from tools.puzzle_production import editor_image_source as images
            binding = {'entry': deepcopy(delivery['entry']), 'identity': {
                'key': delivery['entry']['key'], 'save_slot': delivery['entry']['save_slot'],
                'definition': {'file': 'game/' + delivery['entry']['definition'], 'sha256': '7' * 64, 'bytes': 4},
                'runtime_revision': 1}}
            source = {'format': images.BACKGROUND_FORMAT, 'id': delivery['entry']['id'], 'record_revision': 1,
                      'origin': {**deepcopy(binding), 'notice': None, 'source': None}, 'binding': binding,
                      'current': {'image_revision': 1, 'status': 'none', 'asset': None, 'notice': None,
                                  'authority': {'kind': 'manual', 'provenance': None, 'decision': {
                                      'actor': 'TEST ONLY', 'timestamp_utc': '2026-11-13T00:00:00Z',
                                      'statement': 'Synthetic background preference.'}}}}
            source = images._hashed(source)
            ref = put(root, bg.path(delivery['entry']['id']), source)
            catalog['backgrounds'] = [{'id': delivery['entry']['id'], 'source': ref}]
            value['background'] = {'origin_sha256': bg.origin_hash(source), 'export_source': None}
        ref = put(root, delivery['manifest_ref']['file'], value)
        catalog['entries'][0]['production']['package_sha256'] = ref['sha256']
        put(root, registry.REGISTRY, catalog)
        commit(root)
    main = git(root, 'rev-parse', 'HEAD').decode().strip()
    git(root, 'checkout', '-q', previous)
    return main


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='pw-c-deliveries-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        git(self.repo, 'init', '-q', '-b', 'main')
        put(self.repo, INDEX, {'format': 'picross-authoring-index-v1', 'entries': []})
        put(self.repo, registry.REGISTRY, {'format': registry.METADATA_FORMAT, 'entries': [], 'backgrounds': [], 'metadata': []})
        put(self.repo, registry.RUNTIME, {'format': registry.IMAGE_RUNTIME_FORMAT, 'entries': []})
        self.base = commit(self.repo)
        self.branch = 'content/pw/' + ID
        git(self.repo, 'checkout', '-qb', self.branch)
        metadata_job(self.repo, 'early-alpha')
        self.early = commit(self.repo)
        self.delivery = delivery_fixture(self.repo)
        self.remote = self.root / 'remote'
        self.remote.mkdir()
        git(self.remote, 'init', '--bare', '-q')
        self.push()
        self.state = self.root / 'state'
        configure(self.repo, self.state, remote=str(self.remote))
        self.reader = Repository(self.state)

    def push(self):
        git(self.repo, 'push', '--force', str(self.remote), 'main', self.branch)

    def integrate(self, **kwargs):
        sha = integrate_fixture(self.repo, self.delivery, **kwargs)
        self.push()
        return sha

    def test_registered_is_open_until_fresh_exact_main_and_main_change_bypasses_branch_cache(self):
        before = self.reader.refresh()
        self.assertEqual({j['revision'] for j in before['jobs']}, {'early-alpha', 'r02'})
        self.assertTrue(before['completion']['confirmed'])
        branch = git(self.repo, 'rev-parse', self.branch).decode().strip()
        main = self.integrate()
        after = self.reader.refresh()
        self.assertEqual(git(self.repo, 'rev-parse', self.branch).decode().strip(), branch)
        self.assertEqual(after['jobs'], [])
        self.assertEqual(after['completion']['main_commit'], main)
        self.assertEqual(after['completion']['completed_ids'], [ID])
        self.assertEqual(after['completion']['hidden_count'], 4)
        self.assertEqual({j['revision'] for j in after['completion']['hidden_jobs']}, {'early-alpha', 'r02'})
        # The unfiltered branch scan is still used by P2's all-revision preview.
        self.assertEqual(len(self.reader.scan(self.reader.local, branch, ID)['jobs']), 2)

    def test_normal_merge_squash_and_unrelated_batch_import_have_same_delivery_result(self):
        for mode in ('merge', 'squash', 'copy'):
            with self.subTest(mode=mode):
                git(self.repo, 'branch', '-f', 'main', self.base)
                self.integrate(mode=mode)
                self.assertEqual(self.reader.refresh()['jobs'], [])
                if mode != 'merge':
                    with self.assertRaises(ValueError):
                        git(self.repo, 'merge-base', '--is-ancestor', self.delivery['head'], 'main')

    def test_old_local_snapshot_exact_copies_disappear_but_new_same_id_stays(self):
        self.integrate()
        git(self.repo, 'reset', '--hard', self.early)
        result = self.reader.refresh()
        self.assertEqual(result['jobs'], [])
        git(self.repo, 'reset', '--hard', self.delivery['head'])
        metadata_job(self.repo, 'future-beta')
        commit(self.repo)
        result = self.reader.refresh()
        self.assertEqual([(j['source'], j['revision']) for j in result['jobs']], [('local', 'future-beta')])
        self.assertEqual(result['completion']['completed_ids'], [])

    def test_divergent_record_projection_and_new_image_work_are_retained(self):
        self.integrate()
        for field in ('package', 'candidate', 'reveal', 'background', 'projection'):
            with self.subTest(field=field):
                git(self.repo, 'reset', '--hard', self.delivery['head'])
                record = deepcopy(self.delivery['record'])
                projection = p.parse((self.repo / self.delivery['projection_file']).read_bytes())
                if field == 'projection':
                    projection['title'] = 'New projection'
                elif field == 'package':
                    record[field]['sha256'] = '0' * 64
                else:
                    record[field] = {'new_work': True}
                ref = put(self.repo, self.delivery['record_file'], record)
                projection['record'] = {'commit': None, **ref}
                put(self.repo, self.delivery['projection_file'], projection)
                publish_pointer(self.repo, ID, 'r02')
                commit(self.repo)
                active = self.reader.refresh()['jobs']
                self.assertEqual([(j['source'], j['revision']) for j in active], [('local', 'r02')])

    def test_invalid_current_view_and_unproven_earlier_bytes_stay(self):
        self.integrate()
        name = cv.path(ID)
        pointer = p.parse((self.repo / name).read_bytes())
        pointer['record']['sha256'] = '0' * 64
        put(self.repo, name, pointer)
        commit(self.repo)
        self.assertEqual({j['revision'] for j in self.reader.refresh()['jobs']}, {'early-alpha', 'r02'})
        git(self.repo, 'reset', '--hard', self.delivery['head'])
        early = f'content/authoring/{ID}/early-alpha/workspace.json'
        projection = p.parse((self.repo / early).read_bytes())
        projection['title'] = 'Unproven earlier work'
        put(self.repo, early, projection)
        commit(self.repo)
        active = self.reader.refresh()['jobs']
        self.assertEqual([(j['source'], j['revision']) for j in active], [('local', 'early-alpha')])

    def test_unchanged_record_cannot_conceal_changed_package_or_independent_image_metadata(self):
        self.integrate()
        for name in (self.delivery['record']['package']['file'], bg.path(ID), reveal.path(ID)):
            with self.subTest(changed=name):
                git(self.repo, 'reset', '--hard', self.delivery['head'])
                put(self.repo, name, b'new independent source bytes\n')
                commit(self.repo)
                value = self.reader.refresh()
                self.assertTrue(any(j['source'] == 'local' and j['revision'] == 'r02' for j in value['jobs']))
                self.assertFalse(any(j['source'] == 'remote' for j in value['jobs']))
                self.assertFalse(any(j.get('conflict') for j in value['jobs']))

    def test_unchanged_record_with_new_export_or_runtime_binding_stays_open(self):
        self.integrate()
        for change in ('export', 'runtime', 'registry'):
            with self.subTest(change=change):
                git(self.repo, 'reset', '--hard', self.delivery['head'])
                if change == 'export':
                    manifest = deepcopy(self.delivery['manifest'])
                    manifest['approval_sha256'] = '0' * 64
                    ref = put(self.repo, self.delivery['manifest_ref']['file'], manifest)
                    catalog = deepcopy(self.delivery['registry'])
                    catalog['entries'][0]['production']['package_sha256'] = ref['sha256']
                    put(self.repo, registry.REGISTRY, catalog)
                elif change == 'runtime':
                    runtime = deepcopy(self.delivery['runtime'])
                    runtime['entries'][0]['reveal'] = 'art/content/another.png'
                    put(self.repo, registry.RUNTIME, runtime)
                else:
                    catalog = deepcopy(self.delivery['registry'])
                    catalog['entries'][0]['production']['definition_sha256'] = '0' * 64
                    put(self.repo, registry.REGISTRY, catalog)
                commit(self.repo)
                active = self.reader.refresh()['jobs']
                self.assertEqual({(j['source'], j['revision']) for j in active},
                                 {('local', 'r02'), ('local', 'early-alpha')})

    def test_historical_nonfinal_current_view_cannot_close_all_indexed_work(self):
        git(self.repo, 'reset', '--hard', self.early)
        original_commit, calls = commit, []
        def committed(root):
            if not calls:
                publish_pointer(root, ID, 'early-alpha')
            calls.append(True)
            return original_commit(root)
        with patch('tools.test_workspace_deliveries.commit', committed):
            self.delivery = delivery_fixture(self.repo)
        self.integrate()
        active = self.reader.refresh()['jobs']
        self.assertEqual({j['revision'] for j in active}, {'early-alpha'})
        self.assertEqual({j['source'] for j in active}, {'local', 'remote'})

    def test_new_current_pointer_back_to_old_step_is_a_visible_resumption(self):
        self.integrate()
        publish_pointer(self.repo, ID, 'early-alpha')
        commit(self.repo)
        active = self.reader.refresh()['jobs']
        self.assertEqual([(j['source'], j['revision']) for j in active], [('local', 'early-alpha')])
        self.assertTrue(active[0]['current_view'])

    def test_background_receipt_and_rehashed_wrong_origin_or_export_anchor(self):
        git(self.repo, 'reset', '--hard', self.early)
        self.delivery = delivery_fixture(self.repo, with_background=True)
        self.integrate(receipt=reveal.BACKGROUND_RECEIPT)
        closed = self.reader.refresh()
        self.assertEqual(closed['jobs'], [])
        valid_main = git(self.repo, 'rev-parse', 'main').decode().strip()
        for field in ('origin_sha256', 'source'):
            with self.subTest(field=field):
                git(self.repo, 'checkout', '-q', 'main')
                git(self.repo, 'reset', '--hard', valid_main)
                value = p.parse((self.repo / self.delivery['manifest_ref']['file']).read_bytes())
                if field == 'source':
                    value['background']['source']['sha256'] = '0' * 64
                else:
                    value['background'][field] = '0' * 64
                ref = put(self.repo, self.delivery['manifest_ref']['file'], value)
                catalog = p.parse((self.repo / registry.REGISTRY).read_bytes())
                catalog['entries'][0]['production']['package_sha256'] = ref['sha256']
                put(self.repo, registry.REGISTRY, catalog)
                commit(self.repo)
                git(self.repo, 'checkout', '-q', self.branch)
                self.push()
                self.assertTrue(self.reader.refresh()['jobs'])

    def test_receipt_versions_and_independent_catalog_extension(self):
        for receipt in (None, reveal.RECEIPT, reveal.EDITOR_RECEIPT):
            with self.subTest(receipt=receipt):
                git(self.repo, 'branch', '-f', 'main', self.base)
                self.integrate(receipt=receipt)
                self.assertEqual(self.reader.refresh()['jobs'], [])
        # The original hashes bind historical whole documents, not new main's.
        git(self.repo, 'checkout', '-q', 'main')
        catalog = p.parse((self.repo / registry.REGISTRY).read_bytes())
        extra = deepcopy(self.delivery['entry'])
        extra.update(id='pz-other', key='pz-other', save_slot='other',
                     definition='data/content/other.json', reveal='art/content/other.png')
        extra['production'].update(package='content/packages/pz-other/r01', revision='r01')
        catalog['entries'] = sorted(catalog['entries'] + [extra], key=lambda e: e['id'])
        put(self.repo, registry.REGISTRY, catalog)
        commit(self.repo)
        git(self.repo, 'checkout', '-q', self.branch)
        self.push()
        self.assertEqual(self.reader.refresh()['jobs'], [])

    def test_main_absent_unselected_local_only_restart_and_failed_refresh_are_not_confirmation(self):
        self.integrate()
        self.assertEqual(self.reader.refresh()['jobs'], [])
        restarted = Repository(self.state).listing()
        self.assertFalse(restarted['completion']['confirmed'])
        self.assertTrue(restarted['jobs'])
        with patch.object(self.reader, 'fetch', side_effect=ValueError('offline')):
            offline = self.reader.refresh()
        self.assertFalse(offline['completion']['confirmed'])
        self.assertTrue(offline['jobs'])
        state = self.root / 'restricted'
        configure(self.repo, state, remote=str(self.remote), refs=[self.branch])
        restricted = Repository(state)
        value = restricted.refresh()
        self.assertTrue(value['remote_confirmed'])
        self.assertFalse(value['completion']['confirmed'])
        self.assertTrue(value['jobs'])
        self.assertNotIn('main', {s['ref'] for s in value['sources']})
        local_state = self.root / 'local'
        configure(self.repo, local_state)
        self.assertTrue(Repository(local_state).refresh()['jobs'])
        git(self.remote, 'update-ref', '-d', 'refs/heads/main')
        self.assertFalse(self.reader.refresh()['completion']['confirmed'])

    def test_missing_main_proof_or_historical_chain_never_hides_uncertain_work(self):
        self.integrate()
        git(self.repo, 'checkout', '-q', 'main')
        (self.repo / self.delivery['manifest_ref']['file']).unlink()
        commit(self.repo)
        git(self.repo, 'checkout', '-q', self.branch)
        self.push()
        self.assertTrue(self.reader.refresh()['jobs'])
        self.integrate()
        original = GitSource.read
        def missing_history(source, sha, name, *args, **kwargs):
            if sha == self.delivery['registration'] and name == INDEX:
                raise ValueError('historical metadata unavailable')
            return original(source, sha, name, *args, **kwargs)
        with patch.object(GitSource, 'read', missing_history):
            self.reader.scans.items.clear()
            self.assertTrue(self.reader.refresh()['jobs'])

    def test_wrong_json_shapes_are_uncertain_instead_of_losing_the_initial_listing(self):
        self.integrate()
        valid_main = git(self.repo, 'rev-parse', 'main').decode().strip()
        for name in (registry.REGISTRY, registry.RUNTIME, self.delivery['manifest_ref']['file']):
            for malformed in ([], None, 7):
                with self.subTest(name=name, shape=malformed):
                    git(self.repo, 'checkout', '-q', 'main')
                    git(self.repo, 'reset', '--hard', valid_main)
                    put(self.repo, name, malformed)
                    commit(self.repo)
                    git(self.repo, 'checkout', '-q', self.branch)
                    self.push()
                    self.assertTrue(self.reader.refresh()['jobs'])

    def test_bound_malformed_historical_documents_leave_work_visible(self):
        self.integrate()
        for field, malformed in (('manifest', []), ('registry', None), ('runtime', 7)):
            with self.subTest(field=field):
                git(self.repo, 'reset', '--hard', self.delivery['registration'])
                put(self.repo, self.delivery['record']['integration'][field]['file'], malformed)
                historical = commit(self.repo)
                record = deepcopy(self.delivery['record'])
                record['integration']['commit'] = historical
                for key in ('manifest', 'registry', 'runtime'):
                    name = record['integration'][key]['file']
                    raw = (self.repo / name).read_bytes()
                    record['integration'][key] = cv.reference(name, raw)
                ref = put(self.repo, self.delivery['record_file'], record)
                projection = p.parse((self.repo / self.delivery['projection_file']).read_bytes())
                projection['record'] = {'commit': None, **ref}
                put(self.repo, self.delivery['projection_file'], projection)
                publish_pointer(self.repo, ID, 'r02')
                commit(self.repo)
                active = self.reader.refresh()['jobs']
                self.assertTrue(any(j['source'] == 'local' and j['revision'] == 'r02' for j in active))

    def test_listing_only_reads_bounded_metadata_and_status_poll_never_runs_git(self):
        self.integrate()
        original = GitSource.read
        reads = []
        def metadata_only(source, sha, name, limit=1024 * 1024, missing=False):
            self.assertTrue(name.endswith('.json'))
            self.assertLessEqual(limit, 8 * 1024 * 1024)
            reads.append(name)
            return original(source, sha, name, limit, missing)
        with patch.object(GitSource, 'read', metadata_only), \
             patch('tools.production_workspace.sources.Archive', side_effect=AssertionError('ZIP access')), \
             patch('tools.production_workspace.presentation.image', side_effect=AssertionError('image access')), \
             patch('tools.production_workspace.projector.complete', side_effect=AssertionError('writer')):
            self.assertEqual(self.reader.refresh()['jobs'], [])
        self.assertTrue(reads)
        self.assertLessEqual(self.reader.scans.size, self.reader.scans.limit)
        self.assertLessEqual(self.reader.cached.cache.size, self.reader.cached.cache.limit)
        from tools.production_workspace.server import Service
        service = Service(self.reader)
        service.listing()
        with patch('tools.production_workspace.repository.git', side_effect=AssertionError('Git in status')):
            value = service.status()
        self.assertEqual(value['update']['state'], 'idle')


if __name__ == '__main__':
    unittest.main()
