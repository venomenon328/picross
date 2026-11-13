"""Change-scoped lifecycle regressions; real locks/HTTP, synthetic data only."""
import http.client
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from tools.production_workspace import instance, runtime
from tools.production_workspace.repository import configure
from tools.production_workspace.sources import git


class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='pw-p3-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repository = self.root / 'Daten mit Umlaut ä'; self.repository.mkdir()
        git(self.repository, 'init', '-q', '-b', 'main')
        git(self.repository, '-c', 'user.name=synthetic', '-c', 'user.email=pw@example.invalid',
            'commit', '--allow-empty', '-qm', 'synthetic')
        self.state = self.root / 'Zustand ü'
        self.hosts = []
        self.addCleanup(self.stop_all)

    def stop_all(self):
        for host in self.hosts:
            if host.thread and host.thread.is_alive():
                host.request_stop()
                self.assertTrue(host.stopped.wait(10))
            host.lock.close()

    def start(self, build='b' * 40, port=None):
        lock = instance.StateLock(self.state)
        self.assertTrue(lock.acquire())
        if not (self.state / 'config.json').exists():
            configure(self.repository, self.state, refs=['main'], launcher=True)
        host = runtime.Runtime(lock, build, no_browser=True)
        self.hosts.append(host)
        host.start(port)
        return host

    def request(self, host, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection('127.0.0.1', host.metadata['port'], timeout=5)
        connection.request(method, path, body, headers or {})
        response = connection.getresponse()
        value = response.status, response.read()
        connection.close()
        return value

    def test_first_setup_can_cancel_without_config_or_instance(self):
        lock = instance.StateLock(self.state)
        self.assertTrue(lock.acquire()); lock.close()
        self.assertFalse((self.state / 'config.json').exists())
        self.assertFalse(lock.metadata.exists())
        configure(self.repository, self.state, launcher=True)
        self.assertTrue((self.state / 'config.json').exists())

    def test_competing_locks_and_stale_pid_never_authorize_action(self):
        first = instance.StateLock(self.state); second = instance.StateLock(self.state)
        self.assertTrue(first.acquire()); self.assertFalse(second.acquire())
        first.publish({'pid': 123, 'port': 1, 'untrusted': True})
        with self.assertRaises(ValueError):
            second.read()
        first.close()
        second.metadata.write_text('{"pid":1}')
        self.assertTrue(second.acquire())
        self.assertFalse(second.metadata.exists()); second.close()

    def test_authenticated_second_start_and_incompatible_build(self):
        host = self.start()
        other = instance.StateLock(self.state)
        self.assertFalse(other.acquire())
        instance.existing(other, host.build)
        self.assertTrue(host.open_requested.is_set())
        self.assertIsNone(host.service.update_thread, 'second start must not create a refresh')
        host.open_requested.clear()
        with self.assertRaisesRegex(ValueError, 'Andere Programmversion'):
            instance.existing(other, 'c' * 40)
        self.assertFalse(host.open_requested.is_set())
        bad = {**host.metadata, 'key': 'wrong' * 8}
        with self.assertRaises(ValueError):
            instance.control(bad, 'stop')
        self.assertFalse(host.stop_requested.is_set())

    def test_near_simultaneous_process_starts_share_one_server(self):
        configure(self.repository, self.state)
        arguments = [sys.executable, '-m', 'tools.production_workspace', '--headless', '--no-browser', '--state', str(self.state)]
        children = [subprocess.Popen(arguments, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) for _ in range(2)]
        lock = instance.StateLock(self.state)
        try:
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline and not any(c.poll() == 0 for c in children):
                time.sleep(0.05)
            self.assertEqual(sum(c.poll() is None for c in children), 1)
            self.assertEqual(sum(c.poll() == 0 for c in children), 1)
            metadata = lock.read()
            self.assertEqual(instance.control(metadata, 'identify')['state'], 'ready')
            instance.control(metadata, 'stop')
            for child in children:
                self.assertEqual(child.wait(timeout=10), 0)
            self.assertFalse(lock.metadata.exists())
        finally:
            for child in children:
                if child.poll() is None:
                    child.kill(); child.wait(timeout=10)  # Exact owned synthetic source-test child.

    def test_foreign_responder_cannot_learn_key_or_forge_readiness(self):
        from http.server import BaseHTTPRequestHandler, HTTPServer
        received = []
        class Foreign(BaseHTTPRequestHandler):
            def log_message(self, *_):
                pass
            def do_POST(self):
                received.append(self.rfile.read(int(self.headers['Content-Length'])))
                self.send_response(200); self.end_headers(); self.wfile.write(b'{"proof":"fake"}')
        server = HTTPServer(('127.0.0.1', 0), Foreign)
        thread = threading.Thread(target=server.handle_request); thread.start()
        try:
            value = {'port': server.server_port, 'key': 'secret' * 8, 'instance': 'a' * 48, 'build': 'b' * 40}
            with self.assertRaises(ValueError):
                instance.control(value, 'identify')
            self.assertNotIn(value['key'].encode(), received[0])
        finally:
            thread.join(5); server.server_close()

    def test_control_is_closed_and_separate_from_browser_session(self):
        host = self.start()
        status, _ = self.request(host, 'POST', '/control/v1', b'{}', {'Content-Type': 'application/json',
            'X-Workspace-Session': host.service.secret})
        self.assertEqual(status, 400)
        for path in ('/control/v1', '/api/stop'):
            status, _ = self.request(host, 'GET', path)
            self.assertEqual(status, 400)
        status, _ = self.request(host, 'GET', '/api/jobs', headers={'Origin': 'https://foreign.invalid',
            'X-Workspace-Session': host.service.secret})
        self.assertEqual(status, 400)
        self.assertFalse(host.stop_requested.is_set())

    def test_ready_precedes_slow_sync_and_stop_waits_for_worker(self):
        host = self.start()
        entered, release = threading.Event(), threading.Event()
        original = host.service.repository.refresh
        def slow():
            entered.set(); release.wait(5); return original()
        host.service.repository.refresh = slow
        self.addCleanup(release.set)
        with patch('tools.production_workspace.processes.open_browser', return_value=True) as browser:
            host.no_browser = False; host.open(); browser.assert_called_once()
        self.assertFalse(entered.is_set())
        host.refresh(); self.assertTrue(entered.wait(2))
        host.request_stop()
        self.assertFalse(host.stopped.wait(0.2))
        with self.assertRaises(ValueError):
            host.service.start_refresh()
        release.set(); self.assertTrue(host.stopped.wait(5))
        self.assertFalse(host.thread.is_alive()); self.assertFalse(host.lock.metadata.exists())

    def test_port_reuse_and_explicit_conflict_change_preserve_config(self):
        host = self.start(); port = host.metadata['port']
        config = (self.state / 'config.json').read_bytes()
        host.request_stop(); self.assertTrue(host.stopped.wait(5))
        restarted = self.start(); self.assertEqual(restarted.metadata['port'], port)
        restarted.request_stop(); self.assertTrue(restarted.stopped.wait(5))
        foreign = socket.socket()
        if os.name != 'nt':
            foreign.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        foreign.bind(('127.0.0.1', port)); foreign.listen()
        try:
            with self.assertRaises(runtime.PortConflict):
                self.start()
            self.hosts[-1].lock.close()
            changed = self.start(port=0)
            self.assertNotEqual(changed.metadata['port'], port)
            self.assertEqual((self.state / 'config.json').read_bytes(), config)
        finally:
            foreign.close()

    def test_incomplete_resources_and_unsuitable_git_fail_before_ready(self):
        with patch.object(runtime.ROOT.__class__, 'read_bytes', return_value=b''):
            with self.assertRaisesRegex(ValueError, 'Programmpaket'):
                runtime.preflight()
        with patch('tools.production_workspace.sources.git', side_effect=ValueError('git fail')):
            with self.assertRaisesRegex(ValueError, '--no-lazy-fetch'):
                runtime.preflight()
        self.assertFalse((self.state / 'config.json').exists())

    def test_unknown_configuration_is_rejected_without_rewrite(self):
        configure(self.repository, self.state)
        file = self.state / 'config.json'
        config = json.loads(file.read_bytes()); config['unknown'] = 'preserve'; file.write_bytes(instance.data(config))
        before = file.read_bytes()
        with self.assertRaises(ValueError):
            self.start()
        self.assertEqual(file.read_bytes(), before)

    def test_stop_drains_begun_synthetic_p2_once_with_unknown_result(self):
        host = self.start()
        service = host.service
        service.current = {'snapshot': 's'}
        service.jobs['j'] = {'title': 'synthetic'}; service.snapshots['s'] = ['j']
        service.plans['p'] = {'expires': time.monotonic() + 60, 'job_id': 'j', 'snapshot': 's',
                              'kind': 'remote', 'facts': {'branch': 'content/pw/pz-test'}}
        entered, release, result = threading.Event(), threading.Event(), []
        calls = []
        def transaction(*_):
            calls.append(1); entered.set(); release.wait(5)
            return {'removed': False, 'message': 'synthetischer unbekannter Ausgang'}
        service.removal.remove = transaction
        body = instance.data({'plan_id': 'p', 'job_id': 'j', 'snapshot': 's', 'confirmation': 'content/pw/pz-test'})
        worker = threading.Thread(target=lambda: result.append(self.request(host, 'POST', '/api/removal/confirm', body,
            {'Content-Type': 'application/json', 'Origin': host.server.origin, 'X-Workspace-Session': service.secret})))
        worker.start()
        try:
            self.assertTrue(entered.wait(2)); host.request_stop()
            self.assertFalse(host.stopped.wait(0.2)); self.assertEqual(calls, [1])
            from unittest.mock import Mock
            from tools.production_workspace.update_windows import Handoff
            helper = Mock(); helper.poll.return_value = None
            handoff = Handoff(helper, 'a' * 48)
            with self.assertRaisesRegex(ValueError, 'drain'):
                handoff.commit(host)
            helper.stdin.write.assert_not_called()
        finally:
            release.set(); worker.join(5)
        self.assertTrue(host.stopped.wait(5)); self.assertEqual(result[0][0], 200)
        self.assertEqual(service.removal_result, 'synthetischer unbekannter Ausgang')
        self.assertEqual(calls, [1])
        handoff.commit(host)
        helper.stdin.write.assert_called_once_with(('GO ' + 'a' * 48 + '\n').encode())


if __name__ == '__main__':
    unittest.main()
