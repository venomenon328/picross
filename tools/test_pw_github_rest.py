"""Exercise PW authentication through urllib's real request and redirect handling."""
from email.message import Message
from http.client import HTTPConnection
from io import BytesIO
import json
import os
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.error import URLError
from urllib.request import HTTPSHandler
from urllib.response import addinfourl

from tools.production_workspace import repository, server, update_client
from tools.production_workspace.processes import external_environment
from tools.puzzle_production import current_content, github_rest as rest, work_assets

TOKEN = 'test-workspace-credential'
CDN = 'https://release-assets.githubusercontent.com/github-production-release-asset/42/abc'


class GitHubRestTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.object(rest, '_workspace_token', TOKEN))
        self.requests = []

    def responses(self, *rows):
        rows = iter(rows)

        def https_open(_, request):
            self.requests.append((request.full_url, request.get_header('Authorization')))
            status, values, body = next(rows)
            headers = Message()
            for key, value in values.items():
                headers[key] = value
            reply = addinfourl(BytesIO(body), headers, request.full_url, code=status)
            reply.msg = 'synthetic HTTP response'
            return reply

        return patch.object(HTTPSHandler, 'https_open', https_open)

    def test_startup_prefers_gh_token_and_removes_both_exported_values(self):
        for variables, expected in (
            ({'GH_TOKEN': '  ' + TOKEN, 'GITHUB_TOKEN': 'fallback'}, TOKEN),
            ({'GH_TOKEN': ' ', 'GITHUB_TOKEN': ' fallback '}, 'fallback'),
            ({}, None),
        ):
            with self.subTest(expected=expected), patch.dict(os.environ, variables, clear=True), \
                    patch.object(rest, '_windows_user_token', return_value=None) as user_token:
                rest.load_workspace_token()
                with self.responses((200, {}, b'{}')):
                    repository.github_get('')
                self.assertEqual(self.requests[-1][1], 'Bearer ' + expected if expected else None)
                self.assertTrue(all(name not in os.environ and name not in external_environment()
                                    for name in rest.TOKEN_NAMES))
                self.assertEqual(user_token.call_count, int(not variables and os.name == 'nt'))

    def test_clean_windows_update_restart_uses_current_user_variable(self):
        empty_environment = SimpleNamespace(name='nt', environ={})
        with patch.object(rest, 'os', empty_environment), \
                patch.object(rest, '_windows_user_token', return_value=TOKEN) as user_token:
            rest.load_workspace_token()
            user_token.assert_called_once()
        with self.responses((200, {}, b'{}')):
            repository.github_get('')
        self.assertEqual(self.requests[-1][1], 'Bearer ' + TOKEN)

    def test_origin_and_redirects_are_rejected_on_api_reads(self):
        for target in (CDN, rest.API + '/pulls', 'https://example.invalid/'):
            with self.subTest(target=target), self.responses((302, {'Location': target}, b'')):
                with self.assertRaisesRegex(rest.Failure, 'umgeleitet'):
                    repository.github_get('')
        self.assertEqual(self.requests, [(rest.API, 'Bearer ' + TOKEN)] * 3)
        for foreign in ('http://api.github.com/repos/' + rest.REPOSITORY,
                        rest.API.replace('api.github.com', 'api.github.com@example.invalid'),
                        rest.API.replace('api.github.com', 'api.github.com.example.invalid')):
            with self.subTest(foreign=foreign), self.responses(), self.assertRaisesRegex(ValueError, 'URL'):
                with rest.open_api(foreign, {}, timeout=1):
                    self.fail('Unexpected request')

    def test_original_reads_authenticate_metadata_and_keep_downloads_anonymous(self):
        job = 'pz-synthetic'
        raw = b'production original'
        ref = current_content.ref('content/authoring/' + job + '/original.png', raw)
        ref['asset'] = {'repository': rest.REPOSITORY, 'job': job, 'release_id': 1, 'asset_id': 2}
        asset = {'id': 2, 'name': 'original-' + ref['sha256'], 'size': len(raw), 'state': 'uploaded'}
        tag = 'work-prod-' + job
        release = {'id': 1, 'tag_name': tag, 'prerelease': True, 'draft': False, 'assets': [asset]}
        rows = ((200, {}, json.dumps(release).encode()),
                (302, {'Location': CDN}, b''))
        with self.responses(*rows, (200, {}, raw)):
            self.assertEqual(work_assets.read(ref, 100), raw)
        self.assertEqual(self.requests, [
            (rest.API + '/releases/tags/' + tag, 'Bearer ' + TOKEN),
            (update_client.DOWNLOAD + tag + '/' + asset['name'], None),
            (CDN, None),
        ])
        with self.responses(*rows, (200, {}, b'wrong bytes')), self.assertRaisesRegex(ValueError, 'bytes differ'):
            work_assets.read(ref, 100)

    def test_pr_reads_authenticate_but_absence_proof_is_public(self):
        branch = 'content/pw/pz-synthetic'
        rows = [{'number': 3, 'state': 'open', 'merged_at': None,
                 'head': {'ref': branch, 'repo': {'full_name': rest.REPOSITORY}}}]
        with self.responses((200, {}, json.dumps(rows).encode()), (404, {}, b''),
                            (403, {'X-RateLimit-Remaining': '0'}, b'')):
            self.assertEqual(repository.ProductionRemoval.pull_requests(branch),
                             [{'number': 3, 'state': 'open', 'merged': False}])
            self.assertIsNone(repository.github_get('/releases/1', missing=True))
            with self.assertRaisesRegex(rest.Failure, 'Entfernung gesperrt'):
                repository.github_get('/releases/1', missing=True)
        self.assertTrue(self.requests[0][0].startswith(rest.API + '/pulls?'))
        self.assertEqual([token for _, token in self.requests], ['Bearer ' + TOKEN, None, None])

    def test_update_catalog_uses_pw_auth_and_download_redirect_does_not(self):
        transport = update_client.Transport(use_workspace_token=True)
        args = (100, threading.Event(), time.monotonic() + 5)
        catalog = update_client.API + '?page=1'
        download = update_client.DOWNLOAD + 'pw-v0.1.4/manifest.json'
        with self.responses((200, {}, b'[]'), (302, {'Location': CDN}, b''), (200, {}, b'{}'),
                            (200, {}, b'[]')):
            self.assertEqual(transport.read(catalog, *args), b'[]')
            self.assertEqual(transport.read(download, *args), b'{}')
            self.assertEqual(update_client.Transport().read(catalog, *args), b'[]')
        self.assertEqual(self.requests, [(catalog, 'Bearer ' + TOKEN), (download, None), (CDN, None), (catalog, None)])

    def test_error_classes_discard_response_text_and_details(self):
        for token, status, headers, body, expected in (
            (TOKEN, 401, {}, TOKEN.encode(), 'auth'),
            (TOKEN, 403, {}, TOKEN.encode(), 'access'),
            (TOKEN, 403, {'X-RateLimit-Remaining': '0'}, b'', 'rate_limit'),
            (TOKEN, 403, {'Retry-After': '15'}, b'', 'rate_limit'),
            (None, 403, {}, b'{"message":"secondary rate limit"}', 'rate_limit'),
            (None, 429, {}, b'', 'rate_limit'),
            (TOKEN, 404, {}, b'', 'access'),
            (None, 404, {}, b'', 'source'),
            (TOKEN, 500, {}, b'', 'network'),
        ):
            with self.subTest(status=status, kind=expected), patch.object(rest, '_workspace_token', token), \
                    self.responses((status, headers, body)):
                with self.assertRaises(rest.Failure) as failure:
                    work_assets.get('/releases/tags/work-prod-pz-synthetic', 200)
                self.assertEqual(failure.exception.kind, expected)
                self.assertNotIn(TOKEN, str(failure.exception))
                self.assertEqual('Veröffentlichung prüfen' in str(failure.exception), expected == 'source')
        with patch.object(HTTPSHandler, 'https_open', side_effect=URLError(TOKEN)):
            with self.assertRaisesRegex(rest.Failure, 'Verbindung prüfen') as failure:
                repository.github_get('')
            self.assertNotIn(TOKEN, str(failure.exception))
        with patch.object(rest, '_workspace_token', TOKEN + '\r\nInjected: x'), self.responses():
            with self.assertRaisesRegex(rest.Failure, 'ungültiges Format'):
                repository.github_get('')

    def test_rate_limit_reports_a_bounded_wait(self):
        for headers, message in (
            ({'Retry-After': '120'}, '120 Sekunden'),
            ({'X-RateLimit-Remaining': '0', 'X-RateLimit-Reset': '1700000000'}, '22:13:20 UTC'),
            ({'Retry-After': TOKEN}, 'mindestens eine Minute'),
        ):
            with self.subTest(headers=headers), self.responses((429, headers, b'')):
                with self.assertRaisesRegex(rest.Failure, message) as failure:
                    work_assets.get('/releases/tags/work-prod-pz-synthetic', 200)
                self.assertNotIn(TOKEN, str(failure.exception))

    def test_loopback_reports_github_limit_without_source_correction_or_retry_status(self):
        service = server.Service(None)
        with server.Server(service) as http, patch.object(
                service, 'detail', side_effect=rest.Failure('rate_limit', 'GitHub-Anfragelimit erreicht.')):
            worker = threading.Thread(target=http.serve_forever)
            worker.start()
            client = HTTPConnection('127.0.0.1', http.server_port, timeout=5)
            try:
                client.request('GET', '/api/jobs/synthetic', headers={'X-Workspace-Session': service.secret})
                response = client.getresponse()
                self.assertEqual(response.status, 429)
                self.assertEqual(json.loads(response.read()),
                                 {'error': 'GitHub-Anfragelimit erreicht.', 'code': 'rate_limit'})
            finally:
                client.close()
                http.shutdown()
                worker.join()


if __name__ == '__main__':
    unittest.main()
