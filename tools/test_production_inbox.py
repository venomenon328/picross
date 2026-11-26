"""Bounded regressions for the activated Drive receiver."""
from copy import deepcopy
from io import BytesIO
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
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
