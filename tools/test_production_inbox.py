"""Bounded regressions for the activated Drive receiver."""
from copy import deepcopy
from io import BytesIO
import json
import subprocess
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
import threading
from uuid import uuid4

from PIL import Image
from tests.puzzle_production.current_fixtures import brief_job
from tools.production_workspace import inbox_contract as contract, inbox_files as files
from tools.production_workspace.inbox import Inbox
from tools.puzzle_production import current_authoring as current, current_content as content


class InboxTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.folder = self.root / 'input'
        self.folder.mkdir()
        state = self.root / 'state'
        state.mkdir()
        self.service = SimpleNamespace(repository=SimpleNamespace(state=state))
        self.inbox = Inbox(self.service)
        self.inbox.data['folder'] = {'directory': str(self.folder), 'id': 'fixture'}
        job = current.upgrade(brief_job('pz-current', 'a'*40))
        job['state'] = 'reveal_review'
        img = Image.new('RGBA', (10, 10))
        img.putpixel((5, 5), (0, 0, 0, 255))
        stream = BytesIO()
        img.save(stream, format='PNG')
        self.png = stream.getvalue()
        delivery = str(uuid4())
        self.filename = delivery + '--1.png'
        self.manifest = delivery + '.json'
        ref = content.ref('content/authoring/pz-current/data/reveal.png', self.png)
        job['assets'].append({'id': 'one', 'role': 'reveal', 'label': 'Original', 'file': ref, 'review': {}, 'rights': None})
        self.order = {'request_id': str(uuid4()), 'puzzle_id': job['puzzle_id'], 'phase': 'reveal', 'intent': 'offer',
                      'source': {'main_commit': job['source_commit'], 'work_head': None, 'record_sha256': None},
                      'limits': job['budgets']['limits'], 'brief': job['brief'], 'test_only': True,
                      'step': 'scan', 'files': {}, 'status': ''}
        self.value = {'format': contract.FORMAT, 'repository': contract.REPOSITORY, 'delivery_id': delivery,
                      **{k: self.order[k] for k in ('request_id','puzzle_id','phase','source')},
                      'request': {'format': current.REQUEST, 'record': job, 'expected': None,
                                  'files': [{'path': ref['file'], 'source': self.filename,
                                             'bytes': ref['bytes'], 'sha256': ref['sha256']}]}}
        self.inbox.data['orders'][job['puzzle_id']] = self.order

    def deliver(self):
        (self.folder / self.manifest).write_bytes(current.encoded(self.value))

    def test_arrival_restart_and_exact_snapshot(self):
        self.deliver()
        with self.assertRaises(files.Waiting):
            self.inbox.receive(self.order, self.folder)
        with (self.folder / self.filename).open('wb') as f:
            f.write(self.png[:8])
        with self.assertRaises(files.Waiting):
            self.inbox.receive(self.order, self.folder)
        restarted = Inbox(self.service)
        order = restarted.data['orders']['pz-current']
        (self.folder / self.filename).write_bytes(self.png)
        v = restarted.receive(order, self.folder)
        contract.delta(order, v['request'], None)
        (self.folder / self.filename).write_bytes(b'x'*len(self.png))
        self.assertEqual((restarted.stage(order)/self.filename).read_bytes(), self.png)
        with self.assertRaises(ValueError):
            restarted.receive(order, self.folder)
        with self.assertRaises(ValueError):
            files.retire(self.folder, self.filename, order['files'][self.filename])
        self.assertTrue((self.folder / self.filename).exists())

    def prepare_service(self):
        self.service.repository.remote = 'https://github.com/venomenon328/picross.git'
        self.service.repository.local = SimpleNamespace(root=self.root / 'git')
        self.service.operation = threading.Lock()
        self.service.acquire_operation = self.service.operation.acquire
        self.service.status = Mock(return_value={'snapshot': 'snapshot', 'remote_confirmed': True,
                                                'completion': {'main_commit': 'a' * 40}})
        repo = self.service.removal = Mock()
        repo.main_state.return_value = {'commit': 'a' * 40, 'registered': False, 'revisions': []}
        repo.remote_head.return_value = None
        repo.availability.return_value = None
        self.inbox.writer.check_access = Mock()

    def new_start(self):
        return {'snapshot': 'snapshot', 'jid': '', 'draft_id': str(uuid4()), 'action': 'continue',
                'candidate': '', 'expected': '', 'findings': '{}',
                'inputs': {'brief': 'Fuchs', 'notes': 'Im Profil', 'parameters': '', 'context': '',
                           'feedback': '', 'reference': '', 'grid': ['Breite: exakt 17 Zellen.']}}

    def test_normal_copy_handshake_through_loopback(self):
        from tools.production_workspace.server import Server
        self.prepare_service()
        self.inbox.data['orders'].clear()
        self.inbox.save()
        self.service.stopping = False
        self.service.secret = 'test-session'
        self.service.workers = threading.BoundedSemaphore(4)
        self.service.inbox = self.inbox
        server = Server(self.service)
        self.addCleanup(server.server_close)
        thread = threading.Thread(target=server.serve_forever, kwargs={'poll_interval': 0.02})
        thread.start()
        self.addCleanup(thread.join)
        self.addCleanup(server.shutdown)
        probe = Path(__file__).parent / 'production_workspace/check_ui_loading.cjs'
        result = subprocess.check_output(['node', str(probe), server.origin, self.service.secret, '[]', 'inbox'],
                                         cwd=probe.parents[2], timeout=25).decode()
        order, = Inbox(self.service).data['orders'].values()
        self.assertEqual(json.loads(result.strip()), order['prompt'])
        self.assertEqual(order['puzzle_id'], 'pz-fuchs')
        self.assertNotIn(str(self.folder), order['prompt'])

    def test_root_change_draft_identity_and_legacy_operation(self):
        self.prepare_service()
        body = self.new_start()
        self.inbox.action('start', body)
        job = 'pz-fuchs'
        order = self.inbox.data['orders'][job]
        self.assertFalse(self.inbox.advance(order))
        self.assertIn('synchronisierten Rätselordner', order['status'])
        self.assertFalse((self.folder / job).exists())
        other = self.root / 'other'
        other.mkdir()
        self.inbox.action('configure', {'directory': str(other), 'folder_id': 'other'})
        resumed = Inbox(self.service)
        resumed.writer.check_access = Mock()
        resumed.action('start', body)
        self.assertEqual(resumed.data['orders'][job]['request_id'], order['request_id'])
        self.assertEqual(resumed.data['orders']['pz-current']['folder']['directory'], str(self.folder))
        self.assertEqual(resumed.data['orders'][job]['folder']['directory'], str(self.folder))
        body['inputs']['brief'] = 'Neuer Titel'
        with self.assertRaisesRegex(ValueError, 'inzwischen geändert'):
            resumed.action('start', body)
        body['expected'] = order['request_id']
        resumed.action('start', body)
        replacement = resumed.data['orders'][job]
        self.assertNotEqual(replacement['request_id'], order['request_id'])
        self.assertEqual(replacement['folder']['directory'], str(other))
        second = resumed.action('start', self.new_start())['started']
        self.assertNotEqual(second, job)
        (other / second).write_text('kein Ordner')
        with self.assertRaisesRegex(ValueError, 'kein Verzeichnis'):
            files.destination(replacement['folder'], second)

    def test_bound_route_uses_the_actual_candidate_and_state(self):
        self.prepare_service()
        self.inbox.data['orders'].clear()
        record = deepcopy(self.value['request']['record'])
        record.update(format=current.findings.PUBLISHED, test_only=False)
        body = self.new_start()
        body.update(jid='row', draft_id='', candidate='one')
        body['inputs'].update(brief='', notes='', grid=[])
        self.service.removal.remote_head.return_value = 'b' * 40
        self.service.selected = Mock(return_value={'puzzle_id': 'pz-current', 'commit': 'b' * 40,
            '_record': record, '_projection': {'record': {'sha256': 'c' * 64}}})
        self.service.detail = Mock(return_value={'facts': {'candidates': {
            'one': {'missing': [], 'findings': []}, 'grid': {'missing': [], 'findings': []}}}})
        for state, action, target, role in [('reveal_review', 'assessment', 'one', 'reveal'),
                ('reveal_review', 'continue', 'one', 'motif'), ('raster_review', 'continue', 'grid', 'background'),
                ('background_review', 'rework', 'one', 'reveal')]:
            record['state'] = state
            record['rasters'] = [{'id': 'grid'}]
            record['selected']['reveal'] = 'one' if state in ('raster_review', 'background_review') else None
            body.update(action=action, candidate=target)
            body['inputs']['feedback'] = 'Kontur ändern' if action == 'rework' else ''
            self.inbox.action('start', body)
            order = self.inbox.data['orders']['pz-current']
            self.assertEqual(order['phase'], role)
            self.assertEqual(order['child'], 'pz-current')
            self.assertEqual(order['choice']['id'] if order['choice'] else order['target'], target)
            body['expected'] = order['request_id']

    def test_only_exact_native_attachment_can_enter_first_reveal(self):
        request = self.value['request']
        source = deepcopy(request['record']['assets'][0])
        source.update(id='ref', role='input', label='Vorlage')
        stream = BytesIO()
        Image.new('RGB', (4, 4), 'blue').save(stream, format='PNG')
        source['file'] = content.ref('content/authoring/pz-current/data/reference.png', stream.getvalue())
        request['record']['assets'].append(source)
        reference = {'name': 'Vorlage.png', 'bytes': source['file']['bytes'], 'sha256': source['file']['sha256']}
        self.order['inputs'] = {'reference': reference}
        request['files'].append({'path': source['file']['file'], 'source': self.value['delivery_id'] + '--2.png',
                                 'bytes': reference['bytes'], 'sha256': reference['sha256']})
        contract.reference_binding(reference)
        contract.envelope(current.encoded(self.value), self.manifest, self.order)
        contract.delta(self.order, request, None)
        reveal = request['record']['assets'][0]['file']
        with patch.dict(reveal, {'sha256': reference['sha256']}), self.assertRaisesRegex(ValueError, 'Bildangebot'):
            contract.envelope(current.encoded(self.value), self.manifest, self.order)
        reference['sha256'] = 'f' * 64
        with self.assertRaises(ValueError):
            contract.envelope(current.encoded(self.value), self.manifest, self.order)
        with self.assertRaises(ValueError):
            contract.delta(self.order, request, None)
        self.order['inputs']['reference'] = ''
        with self.assertRaises(ValueError):
            contract.envelope(current.encoded(self.value), self.manifest, self.order)

    def test_persisted_build_can_rebind_but_unknown_publish_cannot(self):
        from contextlib import nullcontext
        from tests.puzzle_production.current_fixtures import checkout
        from tools import production_git_workspace as ws, publish_git as git, work_publish as publisher
        from tools.production_worktree_publish import JOURNAL
        from tools.puzzle_production import catalog_io as io

        remote = checkout(self.root / 'remote')
        def commit(message):
            ws.git(remote, 'add', '.')
            ws.git(remote, '-c', 'user.email=fixture@example.invalid', '-c', 'user.name=Fixture', 'commit', '-qm', message)
            return ws.git(remote, 'rev-parse', 'HEAD')

        ws.git(remote, 'init', '-q', '-b', 'main')
        ws.git(remote, 'config', 'core.autocrlf', 'false')
        main = commit('main')
        job = self.order['puzzle_id']
        ws.git(remote, 'switch', '-qc', 'content/pw/' + job)
        path = remote / current.path(job)
        path.parent.mkdir(parents=True)
        record = current.upgrade(brief_job(job, main))
        record.update(format=current.findings.PUBLISHED, work_release={'id': 1, 'anchor': main})
        path.write_bytes(current.encoded(record))
        expected = commit('prior work')
        self.order['source'].update(main_commit=main, work_head=expected, record_sha256=io.checksum(path.read_bytes()))
        self.value['request']['expected'] = self.order['source']['record_sha256']
        self.deliver()
        (self.folder / self.filename).write_bytes(self.png)
        self.inbox.receive(self.order, self.folder)
        # Only the transport endpoints are substituted. Refs, commits, ownership
        # bindings, locks, local drafts, staged originals and receipts use disk.
        original_git = git.git
        def local_git(root, *args, **kwargs):
            if 'fetch' in args or 'ls-remote' in args:
                args = tuple(str(remote) if arg == git.REMOTE else arg for arg in args)
            return original_git(root, *args, **kwargs)
        def read_record(head, puzzle_id):
            return original_git(remote, 'show', head + ':' + current.path(puzzle_id))
        self.inbox.writer.root.mkdir()
        self.service.operation = threading.Lock()
        self.service.acquire_operation = self.service.operation.acquire
        binding = {k: self.order[k] for k in ('puzzle_id', 'request_id')}
        with patch.object(git, 'git', side_effect=local_git), patch.object(publisher, 'publisher_auth', return_value=nullcontext()), \
             patch.object(publisher, 'remote_record', side_effect=read_record), patch.object(publisher, 'push_job') as push:
            paths = ws.prepare(self.inbox.writer.root, job, main, main, expected, inbox=True)
            work = Path(paths['job'])
            foreign = work / 'unsaved.txt'
            foreign.write_text('local changes')
            record.update(brief=record['brief'] + ' changed elsewhere', test_only=False)
            path.write_bytes(current.encoded(record))
            successor = commit('competing work')
            # A publish receipt with an uncertain response stays resumable only.
            self.order.update(step='publish', draft_sha256='a' * 64)
            self.inbox.save()
            resumed = Inbox(self.service)
            order = resumed.data['orders'][job]
            resumed.advance(order)
            self.assertEqual((order['step'], order['paused']), ('publish', True))
            with self.assertRaises(ValueError):
                resumed.action('cancel', binding)
            # The failed cancel rolled back the transaction. Observe the durable order.
            resumed = Inbox(self.service)
            order = resumed.data['orders'][job]
            # Even a saved build must respect a publication journal.
            order.update(step='build', paused=False)
            journal = ws.gitdir(work) / JOURNAL
            journal.write_bytes(current.encoded({'job': job, 'path': str(work), 'expected': expected}))
            resumed.save()
            resumed = Inbox(self.service)
            order = resumed.data['orders'][job]
            resumed.advance(order)
            self.assertEqual((order['step'], order['paused']), ('build', True))
            journal.unlink()
            resumed.action('retry', binding)
            resumed.advance(order)
            self.assertEqual(order['step'], 'stale')
            self.assertIn(successor, order['status'])
            resumed = Inbox(self.service)
            resumed.action('cancel', binding)
            self.assertNotIn(job, resumed.data['orders'])
            self.service.repository.remote = 'https://github.com/venomenon328/picross.git'
            self.service.status = Mock(return_value={'snapshot': 'fresh', 'remote_confirmed': True,
                                                    'completion': {'main_commit': main}})
            repo = self.service.removal = Mock()
            repo.main_state.return_value = {'commit': main, 'registered': False, 'revisions': []}
            repo.remote_head.return_value = successor
            repo.availability.return_value = None
            self.service.selected = Mock(return_value={'puzzle_id': job, 'commit': successor, '_record': record,
                '_projection': {'record': {'sha256': io.checksum(path.read_bytes())}}})
            inputs = dict.fromkeys(('notes', 'parameters', 'context', 'brief', 'feedback', 'reference'), '')
            resumed.writer.check_access = Mock()
            resumed.action('start', {'snapshot': 'fresh', 'jid': 'row', 'draft_id': '', 'action': 'resume',
                            'candidate': '', 'expected': resumed.data['generations'][job],
                            'findings': '{}', 'inputs': {**inputs, 'grid': []}})
            replacement = resumed.data['orders'][job]
            self.assertNotEqual(replacement['request_id'], order['request_id'])
            self.assertEqual(replacement['source']['work_head'], successor)
            next_paths = ws.prepare(resumed.writer.root, job, main, main, replacement['source']['work_head'], inbox=True)
            new_work = Path(next_paths['job'])
            self.assertNotEqual(work, new_work)
            self.assertEqual(ws.git(new_work, 'rev-parse', 'HEAD'), successor)
            self.assertEqual(foreign.read_text(), 'local changes')
            self.assertEqual((resumed.stage(order) / self.filename).read_bytes(), self.png)
            self.assertEqual((self.folder / self.filename).read_bytes(), self.png)
            push.assert_not_called()

    def test_duplicate_delivery_and_manifest_mutation(self):
        self.deliver()
        (self.folder / self.filename).write_bytes(self.png)
        self.inbox.receive(self.order, self.folder)
        second = self.folder / (str(uuid4()) + '.json')
        second.write_bytes(current.encoded(self.value))
        with self.assertRaisesRegex(ValueError, 'mehrere'):
            self.inbox.receive(self.order, self.folder)
        second.unlink()
        (self.folder / self.manifest).write_bytes(current.encoded(self.value) + b' ')
        with self.assertRaisesRegex(ValueError, 'Lieferkennung'):
            self.inbox.receive(self.order, self.folder)

    def test_closed_request_no_injected_authority(self):
        raw = current.encoded(self.value)
        for invalid in (raw.replace(b'"format":', b'"format":"old","format":', 1),
                        raw.replace(self.filename.encode(), b'../link.png'), raw.replace(b'"reveal"', b'"motif"', 1)):
            with self.assertRaises(ValueError):
                contract.envelope(invalid, self.manifest, self.order)
        request = deepcopy(self.value['request'])
        request['record']['budgets']['limits']['repair_rounds'] += 1
        with self.assertRaises(ValueError):
            contract.delta(self.order, request, None)

    def test_role_scoped_assessment_and_correction(self):
        for phase in contract.PHASES:
            with self.subTest(phase=phase):
                old = deepcopy(self.value['request']['record'])
                asset = old['assets'][0]
                asset['role'] = phase
                if phase == 'background':
                    asset.update(prepared=None, profile='picross-background-png2304x768-v1')
                old['state'] = contract.PHASES[phase]
                order = {**self.order, 'phase': phase, 'intent': 'assessment', 'target': 'one'}
                request = {**self.value['request'], 'record': deepcopy(old), 'files': []}
                contract.delta(order, request, old)
                request['record']['assets'][0]['label'] = 'other'
                with self.assertRaises(ValueError):
                    contract.delta(order, request, old)
                request['record'] = deepcopy(old)
                altered = request['record']['assets'][0]
                altered['id'] = 'two'
                altered['file'] = content.ref('content/authoring/pz-current/data/two.png', b'new')
                request['record']['budgets']['used']['image_corrections'] += 1
                request['files'] = [{'path': altered['file']['file']}]
                contract.delta({**order, 'intent': 'correction'}, request, old)

    def test_restart_after_publish_and_cleanup_does_not_consume_order_twice(self):
        self.deliver()
        (self.folder / self.filename).write_bytes(self.png)
        self.service.operation = threading.Lock()
        self.service.acquire_operation = self.service.operation.acquire
        confirmed = {'head': 'b' * 40, 'record_sha256': 'd' * 64, 'release_id': 42}
        publications = {}

        def publish(order, request, stage, save):
            order['step'] = 'publish'
            save()
            if not publications:
                publications[order['request_id']] = confirmed
                raise ConnectionError('response lost')
            return publications[order['request_id']]

        self.inbox.writer.publish = publish
        self.inbox.advance(self.order)
        self.assertTrue(self.order['paused'])
        binding = {k: self.order[k] for k in ('puzzle_id', 'request_id')}
        resumed = Inbox(self.service)
        resumed.writer.publish = Mock(side_effect=publish)
        order = resumed.data['orders'][binding['puzzle_id']]
        resumed.action('retry', binding)
        with patch.object(files, 'retire', side_effect=PermissionError):
            resumed.advance(order)
        self.assertEqual((order['step'], order['result']), ('cleanup', confirmed))
        restarted = Inbox(self.service)
        restarted.writer.publish = Mock(side_effect=AssertionError('Duplicate publication'))
        restarted.action('retry', binding)
        order = restarted.data['orders'][binding['puzzle_id']]
        def retire(root, name, expected):
            self.assertEqual(files.read(root, name, expected['bytes'])[1], expected)
            (root / name).unlink()
        with patch.object(files, 'retire', side_effect=retire):
            restarted.advance(order)
        self.assertEqual(order['step'], 'done')
        with self.assertRaises(ValueError):
            restarted.action('retry', binding)
        restarted.action('cancel', binding)
        self.deliver()
        with self.assertRaises(ValueError):
            restarted.action('retry', binding)
        self.assertEqual(Inbox(self.service).data['orders'], {})
        restarted.writer.publish.assert_not_called()

    def test_wrong_job_format_and_windows_delivery_alias_are_rejected(self):
        for key, value in [('puzzle_id', 'pz-other'), ('format', 'unknown')]:
            altered = {**self.value, key: value}
            with self.assertRaises(ValueError):
                contract.envelope(current.encoded(altered), self.manifest, self.order)
        for alias in (self.filename.upper(), self.filename + '.', self.filename + ':payload'):
            altered = deepcopy(self.value)
            altered['request']['files'][0]['source'] = alias
            with self.assertRaises(ValueError):
                contract.envelope(current.encoded(altered), self.manifest, self.order)

    @unittest.skipUnless(os.name == 'nt', 'Windows file disposition')
    def test_confirmed_cleanup_deletes_only_opened_file(self):
        self.deliver()
        (self.folder / self.filename).write_bytes(self.png)
        foreign = self.folder / 'other.png'
        foreign.write_bytes(self.png)
        self.inbox.receive(self.order, self.folder)
        files.retire(self.folder, self.filename, self.order['files'][self.filename])
        self.assertFalse((self.folder / self.filename).exists())
        self.assertEqual(foreign.read_bytes(), self.png)
