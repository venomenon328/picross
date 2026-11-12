"""Change-scoped P2 regressions: real synthetic Git, no production remote writes."""
from copy import deepcopy
import http.client
import json
import subprocess
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from tools.production_workspace.repository import Repository, ProductionRemoval, configure, github_identity
from tools.production_workspace.server import Service, Server
from tools.production_workspace.sources import git
from tools.test_production_workspace import commit, current_fixture

BRANCH = 'content/pw/pz-workspace-test'
REF = 'refs/heads/' + BRANCH


class TestRemoval(ProductionRemoval):
    """Owned bare fixture only; never enabled by the application's setup/API."""
    def availability(self, job):
        if job['source'] != 'remote' or job['ref'] != BRANCH or job.get('conflict'):
            return 'Testquelle nicht zugeordnet.'
        return None

    def target(self):
        assert Path(self.repository.remote).resolve() == self.test_remote.resolve()
        assert git(self.test_remote, 'rev-parse', '--is-bare-repository').strip() == b'true'
        self.check_urls()
        return 'TEST ONLY · isoliertes Bare-Remote'

    def pull_requests(self, branch):
        assert branch == BRANCH
        return deepcopy(self.prs)


class RemovalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='pw-p2-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.local = self.root / 'checkout'; self.local.mkdir()
        git(self.local, 'init', '-q', '-b', 'main')
        current_fixture(self.local, self.root / 'r01', 'r01')
        current_fixture(self.local, self.root / 'r02', 'r02')
        self.sha = commit(self.local)
        git(self.local, 'branch', BRANCH)
        self.remote = self.root / 'remote.git'; self.remote.mkdir()
        git(self.remote, 'init', '--bare', '-q')
        git(self.local, 'push', str(self.remote), 'main', BRANCH)
        git(self.remote, 'update-ref', 'refs/heads/content/pw/pz-other', self.sha)
        configure(self.local, self.root / 'state', remote=str(self.remote))
        self.repo = Repository(self.root / 'state')
        self.service = Service(self.repo)
        self.service.listing(refresh=True)
        self.writer = TestRemoval(self.repo)
        self.writer.test_remote, self.writer.prs = self.remote, []
        self.service.removal = self.writer
        self.select()

    def select(self):
        self.jid = next(j['id'] for j in self.service.current['jobs'] if j['source'] == 'remote' and j['ref'] == BRANCH)
        self.binding = {'job_id': self.jid, 'snapshot': self.service.current['snapshot']}

    def preview(self):
        return self.service.removal_preview(self.binding)

    def confirm(self, plan):
        return self.service.removal_confirm({key: plan[key] for key in ('plan_id', 'job_id', 'snapshot')} | {'confirmation': BRANCH})

    def inventory(self):
        return git(self.remote, 'show-ref').decode().splitlines()

    def test_real_delete_single_ref_main_local_retained_then_separate_cleanup(self):
        before = self.inventory()
        dirty = self.local / 'untracked-user-file'; dirty.write_text('preserve')
        plan = self.preview()
        self.assertEqual(plan['revisions'], ['r01', 'r02'])
        self.assertEqual(plan['main']['revisions'], ['r01', 'r02'])
        self.assertEqual(before, self.inventory())
        result = self.confirm(plan)
        self.assertTrue(result['removed'])
        self.assertEqual(self.inventory(), [line for line in before if not line.endswith(' ' + REF)])
        self.assertIsNone(self.writer.remote_head(REF))
        self.assertTrue(any(j['source'] == 'local' and j['ref'] == BRANCH for j in result['listing']['jobs']))
        self.assertFalse(any(j['source'] == 'remote' and j['ref'] == BRANCH for j in result['listing']['jobs']))
        self.assertEqual(dirty.read_text(), 'preserve')
        with self.assertRaisesRegex(ValueError, 'verwendet'):
            self.confirm(plan)
        cleanup = self.service.removal_preview({'receipt_id': result['receipt_id']})
        self.assertEqual(cleanup['kind'], 'local')
        self.assertTrue(self.confirm(cleanup)['removed'])
        self.assertEqual(git(self.local, 'for-each-ref', REF), b'')
        self.assertEqual(dirty.read_text(), 'preserve')

    def test_worktree_local_divergence_and_open_pr_block_whole_action(self):
        tree = self.root / 'linked'
        git(self.local, 'worktree', 'add', str(tree), BRANCH)
        try:
            (tree / 'unsaved').write_text('preserve')
            plan = self.preview()
            self.assertIsNone(plan['plan_id'])
            self.assertIn('Worktree', ' '.join(plan['blockers']))
        finally:
            # Only this synthetic test file; working tree removed through Git.
            (tree / 'unsaved').unlink()
            git(self.local, 'worktree', 'remove', str(tree))
        (self.local / 'new').write_text('new')
        new = commit(self.local)
        git(self.local, 'update-ref', REF, new, self.sha)
        self.assertIn('andere SHA', ' '.join(self.preview()['blockers']))
        git(self.local, 'update-ref', REF, self.sha, new)
        self.writer.prs = [{'number': 1, 'state': 'open', 'merged': False}]
        self.assertIn('Offener Pull', ' '.join(self.preview()['blockers']))
        self.assertEqual(self.writer.remote_head(REF), self.sha)

    def test_changed_head_and_actual_receive_pack_lease_race(self):
        plan = self.preview()
        (self.local / 'advance').write_text('advance')
        newer = commit(self.local)
        git(self.local, 'push', str(self.remote), 'main:' + REF)
        with self.assertRaisesRegex(ValueError, 'Remote-Head'):
            self.confirm(plan)
        git(self.remote, 'update-ref', REF, self.sha, newer)
        plan = self.preview()
        real = self.writer.push_delete
        def racing(facts):
            git(self.remote, 'update-ref', REF, newer, self.sha)
            return real(facts)
        with patch.object(self.writer, 'push_delete', side_effect=racing):
            result = self.confirm(plan)
        self.assertFalse(result['removed'])
        self.assertEqual(self.writer.remote_head(REF), newer)

    def test_pr_changes_fail_closed_and_closed_merged_warnings(self):
        plan = self.preview()
        self.writer.prs = [{'number': 4, 'state': 'open', 'merged': False}]
        with self.assertRaisesRegex(ValueError, 'Offener Pull'):
            self.confirm(plan)
        self.writer.prs = [{'number': 4, 'state': 'closed', 'merged': False}, {'number': 5, 'state': 'closed', 'merged': True}]
        self.assertEqual(len(self.preview()['warnings']), 2)
        with patch.object(self.writer, 'pull_requests', side_effect=ValueError('PR-Zugang fehlt')):
            with self.assertRaisesRegex(ValueError, 'PR-Zugang'):
                self.preview()
        self.assertEqual(self.writer.remote_head(REF), self.sha)

    def test_expiry_selection_change_bad_confirmation_and_foreign_plan(self):
        for change in ('expiry', 'snapshot', 'text', 'foreign'):
            plan = self.preview()
            if change == 'expiry':
                self.service.plans[plan['plan_id']]['expires'] = 0
            elif change == 'snapshot':
                self.service.listing()
            elif change == 'text':
                body = {key: plan[key] for key in ('plan_id', 'job_id', 'snapshot')} | {'confirmation': 'main'}
                with self.assertRaises(ValueError): self.service.removal_confirm(body)
            else:
                plan['plan_id'] = 'f' * 32
            with self.assertRaises(ValueError): self.confirm(plan)
            self.select()
        self.assertEqual(self.writer.remote_head(REF), self.sha)

    def test_denied_push_cache_failure_and_local_race(self):
        plan = self.preview()
        git(self.remote, 'config', 'receive.denyDeletes', 'true')
        self.assertFalse(self.confirm(plan)['removed'])
        git(self.remote, 'config', 'receive.denyDeletes', 'false')
        plan = self.preview()
        with patch.object(self.repo, 'fetch', side_effect=ValueError('offline')):
            result = self.confirm(plan)
        self.assertTrue(result['removed'])
        self.assertIn('cache_error', result)
        self.assertIsNone(self.writer.remote_head(REF))
        cleanup = self.service.removal_preview({'receipt_id': result['receipt_id']})
        (self.local / 'ahead').write_text('ahead')
        new = commit(self.local)
        git(self.local, 'update-ref', REF, new, self.sha)
        with self.assertRaisesRegex(ValueError, 'andere SHA'): self.confirm(cleanup)
        self.assertEqual(git(self.local, 'rev-parse', REF).decode().strip(), new)

    def test_production_target_identity_rewrites_pushurls_and_pr_pagination(self):
        self.assertTrue(github_identity('ssh://git@github.com/venomenon328/picross.git'))
        for url in ('http://github.com/venomenon328/picross', str(self.remote), 'https://github.com/other/picross', 'https://github.com/venomenon328/picross?token=x'):
            self.assertFalse(github_identity(url))
        git(self.local, 'remote', 'add', 'origin', str(self.remote))
        git(self.local, 'config', 'remote.origin.pushurl', str(self.root / 'other.git'))
        with self.assertRaisesRegex(ValueError, 'Pushziele'): self.preview()
        git(self.local, 'config', '--unset', 'remote.origin.pushurl')
        git(self.local, 'config', 'url.https://example.invalid/.insteadOf', 'https://github.com/')
        with self.assertRaisesRegex(ValueError, 'Umschreibung'): self.preview()
        git(self.local, 'config', '--remove-section', 'url.https://example.invalid/')
        row = {'number': 1, 'state': 'closed', 'merged_at': None, 'head': {'ref': BRANCH, 'repo': {'full_name': 'venomenon328/picross'}}}
        from tools.production_workspace import repository as module
        with patch.object(module, 'github_get', side_effect=[[row] * 100, [row]]) as get:
            rows = ProductionRemoval(self.repo).pull_requests(BRANCH)
        self.assertEqual(len(rows), 101)
        self.assertIn('state=all', get.call_args_list[0].args[0])
        self.assertIn('page=2', get.call_args_list[1].args[0])

    def test_second_session_missing_ref_and_explicit_ref_cache_purge(self):
        configure(self.local, self.root / 'state2', remote=str(self.remote), refs=['main', BRANCH])
        second = Service(Repository(self.root / 'state2'))
        writer = TestRemoval(second.repository); writer.test_remote, writer.prs = self.remote, []
        second.removal = writer; second.listing(refresh=True)
        jid = next(j['id'] for j in second.current['jobs'] if j['ref'] == BRANCH and j['source'] == 'remote')
        plan2 = second.removal_preview({'job_id': jid, 'snapshot': second.current['snapshot']})
        self.assertTrue(self.confirm(self.preview())['removed'])
        with self.assertRaisesRegex(ValueError, 'fehlt bereits'):
            second.removal_confirm({key: plan2[key] for key in ('plan_id', 'job_id', 'snapshot')} | {'confirmation': BRANCH})
        value = second.listing(refresh=True)
        self.assertIsNone(value['sync_error'])
        self.assertFalse(any(j['source'] == 'remote' and j['ref'] == BRANCH for j in value['jobs']))
        self.assertTrue(any(j['source'] == 'local' and j['ref'] == BRANCH for j in value['jobs']))

    def test_remote_timeout_and_unverified_post_push_never_claim_success(self):
        plan = self.preview()
        with patch.object(self.writer, 'remote_head', side_effect=ValueError('Git antwortet nicht rechtzeitig')):
            with self.assertRaisesRegex(ValueError, 'rechtzeitig'): self.confirm(plan)
        self.assertEqual(self.writer.remote_head(REF), self.sha)
        plan = self.preview()
        real = self.writer.remote_head
        def unverified(ref):
            if ref == REF and not git(self.remote, 'for-each-ref', REF):
                raise ValueError('offline after push')
            return real(ref)
        with patch.object(self.writer, 'remote_head', side_effect=unverified):
            result = self.confirm(plan)
        self.assertFalse(result['removed'])
        self.assertIn('nicht bestätigt', result['message'])
        self.assertIsNone(real(REF))

    def test_new_worktree_between_preview_and_confirm_and_symbolic_local_ref(self):
        plan = self.preview(); tree = self.root / 'late-worktree'
        git(self.local, 'worktree', 'add', str(tree), BRANCH)
        try:
            with self.assertRaisesRegex(ValueError, 'Worktree'): self.confirm(plan)
        finally: git(self.local, 'worktree', 'remove', str(tree))
        git(self.local, 'update-ref', '-d', REF, self.sha)
        git(self.local, 'symbolic-ref', REF, 'refs/heads/main')
        with self.assertRaisesRegex(ValueError, 'Symbolischer'): self.preview()
        self.assertEqual(self.writer.remote_head(REF), self.sha)

    def test_http_strict_bodies_status_during_transaction_and_serial_refresh(self):
        server = Server(self.service)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        self.addCleanup(server.server_close); self.addCleanup(server.shutdown)
        def request(path, body=b'{}', headers=None, method='POST'):
            connection = http.client.HTTPConnection(*server.server_address, timeout=5)
            h = {'X-Workspace-Session': self.service.secret, 'Origin': server.origin, 'Content-Type': 'application/json'}
            h.update(headers or {})
            connection.request(method, path, body, h)
            response = connection.getresponse(); raw = response.read(); connection.close()
            return response.status, json.loads(raw), dict(response.getheaders())
        path = '/api/removal/preview'
        raw = json.dumps(self.binding).encode()
        for body, headers in [(raw, {'Origin':'https://evil.invalid'}), (raw, {'Host':'evil.invalid'}), (raw, {'X-Workspace-Session':'wrong'}), (raw, {'Content-Type':'text/plain'}), (b'x'*2049, {}), (b'\xff', {}), (b'{"job_id":"x","job_id":"y"}', {}), (b'{"ref":"main"}', {}), (b'[]', {})]:
            self.assertEqual(request(path, body, headers)[0], 400)
        self.assertEqual(request('/api/refresh', raw)[0], 400)
        self.assertEqual(request('/api/removal/anything', raw)[0], 400)
        self.service.operation.acquire()
        try:
            self.assertEqual(request(path, raw)[0], 400)
            self.assertEqual(request('/api/refresh', b'')[0], 400)
            status, value, headers = request('/api/jobs', b'', method='GET')
            self.assertEqual(status, 200)
            self.assertIn("frame-ancestors 'none'", headers['Content-Security-Policy'])
        finally: self.service.operation.release()
        status, plan, _ = request(path, raw)
        self.assertEqual(status, 200)
        self.assertIsNotNone(plan['plan_id'])

    def test_actual_ui_controller_over_real_http_without_browser(self):
        server = Server(self.service)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close); self.addCleanup(server.shutdown)
        script = Path(__file__).parent / 'production_workspace/check_ui_loading.cjs'
        result = subprocess.run(['node', str(script), server.origin, self.service.secret, '[]', 'removal'],
                                capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIsNone(self.writer.remote_head(REF))


if __name__ == '__main__':
    unittest.main()
