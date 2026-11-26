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

    def test_ui_activate_prompt_and_bound_delta(self):
        # Execute the real click handler, capturing only its outbound HTTP body.
        probe = r"""
const fs=require('node:fs'),vm=require('node:vm');
const elements=new Map(),messages=[];
const document={documentElement:{dataset:{}},getElementById(id){
 if(!elements.has(id))elements.set(id,{replaceChildren(){}});
 return elements.get(id);
}};
const ctx=vm.createContext({document,location:{hash:'',pathname:'/'},history:{replaceState(){}},
 sessionStorage:{getItem(){}},localStorage:{getItem(){}},AbortController,setTimeout,clearTimeout,
 PW:require('./tools/production_workspace/ui/workflow.js'),fetch:(url,opts)=>{
  if(url!=='/api/inbox/activate')return new Promise(()=>{});
  messages.push(JSON.parse(opts.body));return {ok:true,json:async()=>({orders:[]})};
 }});
vm.runInContext(fs.readFileSync('tools/production_workspace/ui/app.js','utf8'),ctx);
const previous={facts:{published:{proposed:[{width:20,height:18,size_constraint:'exact'}]}}};
const cases=[
 ['reveal','offer',null,{brief:'Fuchs',notes:'Im Profil',grid:{width:'17',sizeAccuracy:'exact'}}],
 ['motif','offer',previous,{parameters:'Ohren erhalten',removeGrid:{width:true}}],
 ['reveal','correction',previous,{action:'rework',selection:'one',kind:'reveal',feedback:'Ohr abrunden'}],
 ['background','offer',previous,{context:'Waldrand bei Nacht'}],
 ['reveal','offer',null,{brief:'Fuchs',inputImage:'vorlage.png'}]
];
(async()=>{
 for(const [role,action,value,inputs] of cases){
  ctx.value=value;ctx.inputs=inputs;
  vm.runInContext("listing={snapshot:'snapshot'};detail=value;active=value?{id:'row',puzzle_id:'pz-current'}:null;intent=inputs;readyImages.add('one')",ctx);
  for(const [key,v] of Object.entries({inboxPhase:role,inboxIntent:action,inboxJob:'pz-current'}))
   document.getElementById(key).value=v;
  await document.getElementById('inboxStart').onclick();
  if(document.getElementById('inboxMessage').textContent)throw Error(document.getElementById('inboxMessage').textContent);
 }
 console.log(JSON.stringify(messages));
})().catch(e=>{console.error(e);process.exitCode=1});
"""
        bodies = json.loads(subprocess.check_output(['node', '-e', probe], cwd=Path(__file__).resolve().parents[1]))
        main, head = 'a' * 40, 'b' * 40
        self.service.repository.remote = 'https://github.com/venomenon328/picross.git'
        self.service.status = Mock(return_value={'snapshot': 'snapshot', 'remote_confirmed': True,
                                                'completion': {'main_commit': main}})
        repo = self.service.removal = Mock()
        repo.main_state.return_value = {'commit': main, 'registered': False, 'revisions': []}
        repo.availability.return_value = None
        self.service.operation = threading.Lock()
        self.service.acquire_operation = self.service.operation.acquire
        from http.client import HTTPConnection
        from tools.production_workspace.server import Server
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
        def activate(body):
            connection = HTTPConnection(*server.server_address, timeout=5)
            try:
                connection.request('POST', '/api/inbox/activate', body=json.dumps(body).encode(),
                    headers={'Content-Type': 'application/json', 'Origin': server.origin,
                             'X-Workspace-Session': self.service.secret})
                response = connection.getresponse()
                return response.status, json.loads(response.read())
            finally:
                connection.close()

        expected = [('Fuchs', 'Zusätzliche Motivhinweise: Im Profil', 'Breite: exakt 17 Zellen.'),
                    ('Ohren erhalten', 'Breite: bisherigen Wunsch ausdrücklich aufheben.'),
                    ('Ohr abrunden',), ('Waldrand bei Nacht',)]
        for body, phrases in zip(bodies[:4], expected, strict=True):
            with self.subTest(role=body['phase'], action=body['intent']):
                self.inbox.data['orders'].clear()
                old = deepcopy(self.value['request']['record']) if body['jid'] else None
                repo.remote_head.return_value = head if old else None
                if old:
                    old['test_only'] = False
                    if body['phase'] in contract.PRIOR:
                        old['selected'][contract.PRIOR[body['phase']]] = 'one' if body['phase'] == 'motif' else 'raster'
                    self.service.selected = Mock(return_value={'puzzle_id': 'pz-current', 'commit': head,
                        '_record': {**old, 'format': current.findings.PUBLISHED},
                        '_projection': {'record': {'sha256': 'c' * 64}}})
                status, result = activate(body)
                self.assertEqual(status, 200, result)
                order = Inbox(self.service).data['orders']['pz-current']
                for phrase in phrases:
                    self.assertIn(phrase, order['brief'])
                    self.assertIn(phrase, order['prompt'])
                self.assertNotIn('Höhe:', order['brief'])
                request = deepcopy(self.value['request'])
                job = request['record']
                job['test_only'] = False
                job['brief'] = (old['brief'] + '\n\n' if old else '') + order['brief']
                job['state'] = contract.PHASES[body['phase']]
                if old:
                    job['selected'] = deepcopy(old['selected'])
                    candidate = job['assets'].pop()
                    job['assets'] = deepcopy(old['assets']) if body['intent'] == 'offer' else []
                    candidate.update(id='new', role=body['phase'], file=content.ref(
                        'content/authoring/pz-current/data/new.png', b'new'))
                    if body['phase'] == 'background':
                        candidate.update(prepared=None, profile='picross-background-png2304x768-v1')
                    if body['intent'] == 'correction':
                        job['budgets']['used']['image_corrections'] += 1
                    job['assets'].append(candidate)
                    request['files'] = [{'path': candidate['file']['file']}]
                contract.delta(order, request, old)
                job['brief'] = old['brief'] if old else 'Fuchs'
                with self.assertRaises(ValueError):
                    contract.delta(order, request, old)
        self.inbox.data['orders'].clear()
        status, result = activate(bodies[-1])
        self.assertEqual(status, 400)
        self.assertRegex(result['error'], 'Referenzbild.*nicht erreichbar')
        self.assertFalse(self.inbox.data['orders'])

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
            resumed.action('activate', {'snapshot': 'fresh', 'jid': 'row', 'puzzle_id': job, 'phase': 'reveal',
                            'intent': 'offer', 'target': '', 'selection': '', 'findings': '{}', 'inputs': {**inputs, 'grid': []}})
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
