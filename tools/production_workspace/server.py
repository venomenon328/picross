"""Loopback capability API. Data branches never supply executable UI code."""
from collections import OrderedDict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import secrets
import threading
from urllib.parse import urlsplit
from pathlib import Path
import hmac
import time

from tools.puzzle_production import authoring_package as ap, catalog_io as io
from . import presentation as p
from .sources import LRU

UI = Path(__file__).parent / 'ui'


class Service:
    def __init__(self, repository):
        self.repository, self.secret = repository, secrets.token_urlsafe(32)
        self.snapshots, self.jobs, self.views = OrderedDict(), {}, LRU()
        self.lock = threading.RLock()
        self.workers = threading.BoundedSemaphore(4)
        self.metrics = {'image_requests': 0, 'image_cache_hits': 0, 'image_seconds': 0.0}

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
        return {**value, 'snapshot': snapshot, 'jobs': public}

    def job(self, jid):
        with self.lock:
            ap.require(jid in self.jobs, 'Ansicht ist abgelaufen. Aktuelle Jobliste laden.')
            job = self.jobs[jid]
        ap.require(not job.get('conflict'), 'Widersprüchliche Quellen für dieselbe ID/Revision. Veröffentlichung klären.')
        return job

    def detail(self, jid):
        job = self.job(jid)
        facts = p.inspect(job['_source'], job['commit'], job['_projection'])
        return {**job['_projection'], 'facts': facts, 'source': job['source'], 'commit': job['commit'],
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
    daemon_threads = True
    block_on_close = False
    request_queue_size = 16

    def __init__(self, service, port=0):
        self.service = service
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

    def handle_request(self, method):
        service = self.server.service
        acquired = False
        try:
            self.connection.settimeout(10)
            ap.require(self.headers.get('Host') == urlsplit(self.server.origin).netloc, 'Fremder Host abgewiesen.')
            origin = self.headers.get('Origin')
            ap.require(origin is None or origin == self.server.origin, 'Fremder Browserursprung abgewiesen.')
            ap.require(self.headers.get('Sec-Fetch-Site') in (None, 'none', 'same-origin'), 'Fremder Browserzugriff abgewiesen.')
            path = urlsplit(self.path)
            ap.require(not path.query and not path.fragment and path.path == self.path, 'Ungültiger API-Pfad.')
            if method == 'GET' and path.path in ('/', '/app.js', '/style.css'):
                name, mime = {'/': ('index.html', 'text/html; charset=utf-8'),
                              '/app.js': ('app.js', 'text/javascript; charset=utf-8'),
                              '/style.css': ('style.css', 'text/css; charset=utf-8')}[path.path]
                return self.reply(200, (UI / name).read_bytes(), mime)
            token = self.headers.get('X-Workspace-Session', '')
            ap.require(hmac.compare_digest(token.encode(), service.secret.encode()), 'Sitzung fehlt oder ist ungültig. Starter erneut öffnen.')
            ap.require(not self.headers.get('Transfer-Encoding') and self.headers.get('Content-Length', '0') == '0', 'Anfrageinhalt ist nicht erlaubt.')
            acquired = service.workers.acquire(blocking=False)
            if not acquired:
                return self.reply(503, p.data({'error': 'Dienst ist beschäftigt; gleich erneut versuchen.'}), 'application/json')
            if method == 'GET' and self.path == '/api/jobs':
                value = service.listing()
            elif method == 'POST' and self.path == '/api/refresh':
                value = service.listing(refresh=True)
            else:
                parts = self.path.strip('/').split('/')
                ap.require(method == 'GET' and len(parts) in (3, 5) and parts[:2] == ['api', 'jobs'], 'Unbekannter API-Aufruf.')
                if len(parts) == 3:
                    value = service.detail(parts[2])
                else:
                    ap.require(parts[3] == 'assets', 'Unbekannter Bildaufruf.')
                    raw, mime = service.picture(parts[2], parts[4])
                    return self.reply(200, raw, mime)
            return self.reply(200, p.data(value), 'application/json; charset=utf-8')
        except (ValueError, OSError, RuntimeError, KeyError, TypeError) as exc:
            # All errors are data; never include source URLs or a Python traceback.
            message = str(exc) if isinstance(exc, ValueError) else 'Quelle konnte nicht vollständig gelesen werden. Veröffentlichung prüfen und neu laden.'
            return self.reply(400, p.data({'error': message}), 'application/json; charset=utf-8')
        finally:
            if acquired:
                service.workers.release()
