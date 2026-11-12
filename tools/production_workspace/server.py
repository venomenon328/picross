"""Loopback capability API. Data branches never supply executable UI code."""
from collections import OrderedDict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import secrets
import threading
from urllib.parse import urlsplit
from pathlib import Path
import hmac
import time
import json
import re
import os
import socket

from tools.puzzle_production import authoring_package as ap, catalog_io as io
from . import presentation as p
from .sources import LRU
from .repository import ProductionRemoval
from .instance import PROTOCOL, mac

UI = Path(__file__).parent / 'ui'


class Service:
    def __init__(self, repository):
        self.repository, self.secret = repository, secrets.token_urlsafe(32)
        self.snapshots, self.jobs, self.views = OrderedDict(), {}, LRU()
        self.lock = threading.RLock()
        self.workers = threading.BoundedSemaphore(4)
        # Transport cancellation does not stop a running Python reader. Keep
        # its image slot until completion, reserving two total slots for metadata.
        self.image_workers = threading.BoundedSemaphore(2)
        self.metrics = {'image_requests': 0, 'image_cache_hits': 0, 'image_seconds': 0.0}
        self.current = None
        self.update_thread = None
        self.update_id, self.update_started = 0, 0
        self.update_state, self.update_error = 'idle', None
        self.operation = threading.Lock()
        self.removal = ProductionRemoval(repository)
        self.plans, self.receipts = {}, {}
        self.stopping = False
        self.removal_result = None

    def begin_stop(self):
        with self.lock:
            self.stopping = True
            self.plans.clear()

    def acquire_operation(self):
        with self.lock:
            ap.require(not self.stopping, 'Assistent wird beendet. Keine neue Arbeit gestartet.')
            ap.require(self.operation.acquire(blocking=False), 'Quellenoperation läuft. Danach erneut versuchen.')

    def start_refresh(self):
        with self.lock:
            ap.require(not self.stopping, 'Assistent wird beendet.')
            if self.update_state == 'running':
                return
            ap.require(self.operation.acquire(blocking=False), 'Entfernung läuft; danach Quellen erneut suchen.')
            self.plans.clear()
            self.update_id += 1
            self.update_started = time.monotonic()
            self.update_state, self.update_error = 'running', None
            self.update_thread = threading.Thread(target=self._refresh, name='PW-source-update')
            self.update_thread.start()

    def _refresh(self):
        try:
            value = self.listing(refresh=True)
            with self.lock:
                self.update_error = value.get('sync_error')
                self.update_state = 'error' if self.update_error else 'done'
        except Exception:
            # A background failure must not strand the UI in "loading". Do not
            # expose arbitrary exception text, paths or remote credentials.
            with self.lock:
                self.update_state = 'error'
                self.update_error = 'Quellen konnten nicht geladen werden. Git-Zugang prüfen und erneut suchen.'
        finally:
            self.operation.release()

    def status(self):
        # Never run Git in a status request. A slow refresh owns no HTTP slot and
        # cannot hold this lock while reading repository objects.
        with self.lock:
            value = self.current or {'jobs': [], 'errors': [], 'sources': [], 'snapshot': None,
                                     'mode': 'remote' if self.repository.remote else 'local',
                                     'synced_at': None, 'sync_error': None}
            return {**value, 'update': {'id': self.update_id, 'state': self.update_state,
                                      'elapsed_seconds': round(time.monotonic() - self.update_started, 1)
                                      if self.update_state == 'running' else 0,
                                      'error': self.update_error}}

    def listing(self, refresh=False):
        value = self.repository.refresh() if refresh else self.repository.listing()
        snapshot = secrets.token_hex(16)
        ids, public = [], []
        with self.lock:
            for job in value['jobs']:
                jid = secrets.token_hex(16)
                ids.append(jid)
                self.jobs[jid] = job
                public.append({**{k: v for k, v in job.items() if not k.startswith('_')}, 'id': jid})
            self.snapshots[snapshot] = ids
            while len(self.snapshots) > 8:
                _, expired = self.snapshots.popitem(last=False)
                for jid in expired:
                    self.jobs.pop(jid, None)
            from .motifs import group
            motifs = group(public, value.get('relations', {}), confirmed=value.get('remote_confirmed', False), remote=self.repository.remote)
            self.current = {**value, 'snapshot': snapshot, 'jobs': public, 'motifs': motifs}
            return self.current

    def selected(self, jid, snapshot):
        with self.lock:
            ap.require(self.current and self.current['snapshot'] == snapshot and
                       jid in self.snapshots.get(snapshot, []),
                       'Auswahl ist veraltet. Neueren Stand laden und erneut vorprüfen.')
        return self.job(jid)

    def removal_preview(self, body):
        self.acquire_operation()
        try:
            with self.repository.lock:
                now = time.monotonic()
                self.plans.clear()  # One active confirmation per server session.
                self.receipts = {key: row for key, row in self.receipts.items() if row['expires'] > now}
                if set(body) == {'job_id', 'snapshot'}:
                    job = self.selected(body['job_id'], body['snapshot'])
                    facts = self.removal.probe(job)
                    plan = {'kind': 'remote', 'job_id': body['job_id'], 'snapshot': body['snapshot'],
                            'facts': facts, 'expires': now + 180}
                else:
                    ap.require(set(body) == {'receipt_id'}, 'Ungültige Vorprüfungsfelder.')
                    receipt = self.receipts.pop(body['receipt_id'], None)
                    ap.require(receipt is not None, 'Quittung fehlt oder ist abgelaufen. Lokaler Ref bleibt erhalten.')
                    self.removal.local_probe(receipt['facts'])
                    plan = {**receipt, 'kind': 'local', 'snapshot': self.current['snapshot'],
                            'expires': now + 180}
                    facts = plan['facts']
                pid = None
                if not facts['blockers']:
                    pid = secrets.token_hex(16)
                    self.plans[pid] = plan
                return {**facts, 'plan_id': pid, 'kind': plan['kind'], 'expires_seconds': 180,
                        'job_id': plan['job_id'], 'snapshot': plan['snapshot']}
        finally:
            self.operation.release()

    def removal_confirm(self, body):
        self.acquire_operation()
        try:
            with self.repository.lock:
                ap.require(set(body) == {'plan_id', 'job_id', 'snapshot', 'confirmation'}, 'Ungültige Bestätigungsfelder.')
                plan = self.plans.pop(body['plan_id'], None)  # Burn even on bad confirmation or failed Git.
                ap.require(plan is not None and plan['expires'] > time.monotonic(),
                           'Plan fehlt, ist abgelaufen oder wurde schon verwendet. Erneut vorprüfen.')
                facts = plan['facts']
                ap.require(body['confirmation'] == facts['branch'], 'Branchname stimmt nicht exakt. Erneut vorprüfen.')
                ap.require(body['job_id'] == plan['job_id'] and body['snapshot'] == plan['snapshot'] and
                           self.current['snapshot'] == plan['snapshot'], 'Auswahl wurde geändert. Erneut vorprüfen.')
                if plan['kind'] == 'local':
                    self.removal.remove_local(facts)
                    result = {'removed': True, 'kind': 'local', 'message': 'Nur der lokale Branchref wurde entfernt. Arbeitsdateien und Worktrees bleiben erhalten.'}
                    try:
                        value = self.listing()
                    except (ValueError, OSError):
                        value = None
                        result['cache_error'] = 'Lokale Refentfernung bestätigt, Anzeige konnte nicht aktualisiert werden. Erneut suchen.'
                else:
                    job = self.selected(plan['job_id'], plan['snapshot'])
                    result = {**self.removal.remove(job, facts), 'kind': 'remote'}
                    if not result['removed']:
                        self.removal_result = result['message']
                        return result
                    try:
                        value = self.listing(refresh=True)
                        if value['sync_error']:
                            result['cache_error'] = 'Remoteentfernung bestätigt, Cacheaktualisierung fehlgeschlagen. Angezeigte Remotequellen können veraltet sein; erneut suchen.'
                    except (ValueError, OSError):
                        value = None
                        result['cache_error'] = 'Remoteentfernung bestätigt, Anzeige konnte nicht aktualisiert werden. Erneut suchen.'
                    if facts['local']['sha'] == facts['sha']:
                        rid = secrets.token_hex(16)
                        self.receipts = {rid: {**plan, 'expires': time.monotonic() + 180}}
                        result['receipt_id'] = rid
                self.removal_result = result['message']
                return {**result, 'listing': value, 'branch': facts['branch']}
        except Exception:
            self.removal_result = 'Entfernung nicht vollständig bestätigt. Ausgang vor einer weiteren Aktion frisch prüfen.'
            raise
        finally:
            self.operation.release()

    def job(self, jid):
        with self.lock:
            ap.require(jid in self.jobs, 'Ansicht ist abgelaufen. Aktuelle Jobliste laden.')
            job = self.jobs[jid]
        return job

    def detail(self, jid):
        job = self.job(jid)
        facts = p.inspect(job['_source'], job['commit'], job['_projection'])
        self.views.put(('validated', job['commit'], io.checksum(p.data(job['_projection']))), b'1')
        return {**job['_projection'], 'facts': facts, 'source': job['source'], 'commit': job['commit'],
                'source_url': job.get('source_url'), 'branch': job['ref'],
                'removal_unavailable': self.removal.availability(job),
                'publication': job['publication'], 'status': 'Originalbindungen und Bildbytes geprüft; keine neue Inhaltsfreigabe'}

    def picture(self, jid, aid):
        started = time.perf_counter()
        job = self.job(jid)
        projection = job['_projection']
        ap.require(any(a['id'] == aid for a in projection['assets']), 'Unbekannte Bildkennung.')
        # detail validation must complete before ANY image resource is released.
        key = ('validated', job['commit'], io.checksum(p.data(projection)))
        if self.views.get(key) is None:
            self.detail(jid)
            self.views.put(key, b'1')
        loc = next(a['location'] for a in projection['assets'] if a['id'] == aid)
        cache_key = ('pw-reader-1', job['commit'], p.data(loc))
        raw = self.views.get(cache_key)
        self.metrics['image_requests'] += 1
        if raw is None:
            raw = p.asset_bytes(job['_source'], job['commit'], loc)
            p.image(raw)
            self.views.put(cache_key, raw)
        else:
            self.metrics['image_cache_hits'] += 1
        self.metrics['image_seconds'] += time.perf_counter() - started
        return raw, 'image/png' if raw.startswith(b'\x89PNG') else 'image/jpeg'


class Server(ThreadingHTTPServer):
    daemon_threads = False
    block_on_close = True
    request_queue_size = 16

    def server_bind(self):
        if os.name == 'nt':
            self.allow_reuse_address = False
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()

    def __init__(self, service, port=0):
        self.service = service
        self.lifecycle = None
        self.control_nonces = set()
        super().__init__(('127.0.0.1', port), Handler)
        self.origin = 'http://127.0.0.1:' + str(self.server_address[1])


class Handler(BaseHTTPRequestHandler):
    server_version = 'PicrossWorkspace'
    sys_version = ''

    def log_message(self, *_args):
        pass  # Avoid URLs, session secrets, paths, remote credential output.

    def reply(self, status, raw, mime):
        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Cross-Origin-Resource-Policy', 'same-origin')
        self.send_header('Content-Security-Policy', "default-src 'none'; script-src 'self'; style-src 'self'; img-src blob:; "
                         "connect-src " + self.server.origin + "; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        self.handle_request('GET')

    def do_POST(self):
        self.handle_request('POST')

    def lifecycle_request(self):
        runtime = self.server.lifecycle
        ap.require(runtime is not None, 'Kein Launcherprotokoll verfügbar.')
        ap.require(not self.headers.get('Transfer-Encoding') and
                   self.headers.get_all('Content-Type') == ['application/json'] and
                   len(self.headers.get_all('Content-Length', [])) == 1,
                   'Ungültiger Steuervertrag.')
        length = self.headers.get('Content-Length', '')
        ap.require(length.isascii() and length.isdecimal() and 1 <= int(length) <= 512, 'Ungültige Steuerlänge.')
        raw = self.rfile.read(int(length))
        ap.require(len(raw) == int(length), 'Unvollständige Steueranfrage.')
        def unique(pairs):
            value = {}
            for key, item in pairs:
                ap.require(key not in value, 'Doppeltes Steuerfeld.')
                value[key] = item
            return value
        request = json.loads(raw.decode('ascii'), object_pairs_hook=unique)
        ap.require(isinstance(request, dict) and set(request) == {'action', 'challenge', 'proof'} and
                   all(isinstance(v, str) for v in request.values()), 'Ungültige Steuerfelder.')
        proof = request.pop('proof')
        ap.require(request['action'] in ('identify', 'open', 'stop') and
                   re.fullmatch('[0-9a-f]{48}', request['challenge']) and
                   hmac.compare_digest(proof, mac(runtime.metadata['key'], 'request:', request)),
                   'Steueridentität nicht bestätigt.')
        with self.server.service.lock:
            ap.require(request['challenge'] not in self.server.control_nonces, 'Steueranfrage bereits benutzt.')
            ap.require(len(self.server.control_nonces) < 4096, 'Steuersitzung ist ausgeschöpft. Regulär im Steuerfenster beenden.')
            self.server.control_nonces.add(request['challenge'])
            state = 'stopping' if runtime.stop_requested.is_set() else 'ready'
            if request['action'] == 'open':
                ap.require(state == 'ready', 'Assistent wird beendet.')
                runtime.open_requested.set()
            if request['action'] == 'stop':
                runtime.stop_requested.set()
        value = {'protocol': PROTOCOL, 'build': runtime.build, 'instance': runtime.metadata['instance'],
                 'challenge': request['challenge'], 'state': state}
        if request['action'] == 'open':
            value['browser_url'] = self.server.origin + '/#' + self.server.service.secret
        value['proof'] = mac(runtime.metadata['key'], 'response:', value)
        return self.reply(200, p.data(value), 'application/json')

    def handle_request(self, method):
        service = self.server.service
        acquired = image_acquired = False
        try:
            self.connection.settimeout(10)
            ap.require(self.headers.get('Host') == urlsplit(self.server.origin).netloc, 'Fremder Host abgewiesen.')
            origin = self.headers.get('Origin')
            ap.require(origin is None or origin == self.server.origin, 'Fremder Browserursprung abgewiesen.')
            ap.require(self.headers.get('Sec-Fetch-Site') in (None, 'none', 'same-origin'), 'Fremder Browserzugriff abgewiesen.')
            path = urlsplit(self.path)
            ap.require(not path.query and not path.fragment and path.path == self.path, 'Ungültiger API-Pfad.')
            if method == 'POST' and self.path == '/control/v1':
                return self.lifecycle_request()
            ap.require(not service.stopping, 'Assistent wird beendet. Keine neue Arbeit gestartet.')
            if method == 'GET' and path.path in ('/', '/app.js', '/workflow.js', '/style.css'):
                name, mime = {'/': ('index.html', 'text/html; charset=utf-8'),
                              '/app.js': ('app.js', 'text/javascript; charset=utf-8'),
                              '/workflow.js': ('workflow.js', 'text/javascript; charset=utf-8'),
                              '/style.css': ('style.css', 'text/css; charset=utf-8')}[path.path]
                return self.reply(200, (UI / name).read_bytes(), mime)
            token = self.headers.get('X-Workspace-Session', '')
            ap.require(hmac.compare_digest(token.encode(), service.secret.encode()), 'Sitzung fehlt oder ist ungültig. Starter erneut öffnen.')
            ap.require(not self.headers.get('Transfer-Encoding'), 'Transfer-Encoding ist nicht erlaubt.')
            removal = method == 'POST' and self.path in ('/api/removal/preview', '/api/removal/confirm')
            body = None
            if removal:
                ap.require(origin == self.server.origin, 'Entfernung benötigt den eigenen Browserursprung.')
                ap.require(self.headers.get_all('Content-Type') == ['application/json'] and
                           len(self.headers.get_all('Content-Length', [])) == 1,
                           'Genau ein JSON-Content-Type und Content-Length erforderlich.')
                length = self.headers.get('Content-Length', '')
                ap.require(length.isascii() and length.isdecimal() and 0 < int(length) <= 2048,
                           'JSON-Anfrage muss 1–2048 Bytes enthalten.')
                raw = self.rfile.read(int(length))
                ap.require(len(raw) == int(length), 'Unvollständiger Anfrageinhalt.')
                def unique(pairs):
                    value = {}
                    for key, item in pairs:
                        ap.require(key not in value, 'Doppeltes JSON-Feld.')
                        value[key] = item
                    return value
                body = json.loads(raw.decode('utf-8'), object_pairs_hook=unique)
                ap.require(isinstance(body, dict) and all(isinstance(v, str) and 0 < len(v) <= 160 for v in body.values()),
                           'Nur kurze Textkennungen sind erlaubt.')
            else:
                ap.require(self.headers.get('Content-Length', '0') == '0', 'Anfrageinhalt ist nicht erlaubt.')
            # Status must stay available even while all reader/transaction slots are busy.
            if method == 'GET' and self.path == '/api/jobs':
                return self.reply(200, p.data(service.status()), 'application/json; charset=utf-8')
            parts = self.path.strip('/').split('/')
            if method == 'GET' and len(parts) == 5 and parts[:2] == ['api', 'jobs'] and parts[3] == 'assets':
                image_acquired = service.image_workers.acquire(blocking=False)
                if not image_acquired:
                    return self.reply(503, p.data({'error': 'Bilder werden noch geladen; gleich erneut versuchen.'}), 'application/json')
            acquired = service.workers.acquire(blocking=False)
            if not acquired:
                return self.reply(503, p.data({'error': 'Dienst ist beschäftigt; gleich erneut versuchen.'}), 'application/json')
            if method == 'GET' and self.path == '/api/jobs':
                value = service.status()
            elif method == 'POST' and self.path == '/api/refresh':
                service.start_refresh()
                value = service.status()
            elif removal:
                value = service.removal_preview(body) if self.path.endswith('/preview') else service.removal_confirm(body)
            else:
                ap.require(method == 'GET' and len(parts) in (3, 5) and parts[:2] == ['api', 'jobs'], 'Unbekannter API-Aufruf.')
                if len(parts) == 3:
                    value = service.detail(parts[2])
                else:
                    ap.require(parts[3] == 'assets', 'Unbekannter Bildaufruf.')
                    raw, mime = service.picture(parts[2], parts[4])
                    return self.reply(200, raw, mime)
            return self.reply(200, p.data(value), 'application/json; charset=utf-8')
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass  # A closed transport is not a source failure; finally releases the slots.
        except (ValueError, OSError, RuntimeError, KeyError, TypeError) as exc:
            # All errors are data; never include source URLs or a Python traceback.
            message = str(exc) if isinstance(exc, ValueError) else 'Quelle konnte nicht vollständig gelesen werden. Veröffentlichung prüfen und neu laden.'
            return self.reply(400, p.data({'error': message}), 'application/json; charset=utf-8')
        finally:
            if acquired:
                service.workers.release()
            if image_acquired:
                service.image_workers.release()
