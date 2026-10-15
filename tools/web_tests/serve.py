"""Loopback-only reference host with the production MIME/cache contract."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading


class Handler(SimpleHTTPRequestHandler):
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, '.wasm':'application/wasm',
                      '.js':'text/javascript', '.pck':'application/octet-stream'}

    def end_headers(self):
        self.send_header('Cache-Control', 'public, max-age=31536000, immutable' if '/releases/' in self.path else 'no-cache')
        super().end_headers()

    def log_message(self, *_args):
        pass


def serve(root: Path):
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(root)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f'http://127.0.0.1:{server.server_port}/'
