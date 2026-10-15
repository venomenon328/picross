"""Loopback-only reference host with the production MIME/cache contract."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading


class Handler(SimpleHTTPRequestHandler):
    cache_override = None
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, '.wasm':'application/wasm',
                      '.js':'text/javascript', '.pck':'application/octet-stream'}

    def end_headers(self):
        self.send_header('Cache-Control', self.cache_override or ('public, max-age=31536000, immutable' if '/releases/' in self.path else 'no-cache'))
        super().end_headers()

    def log_message(self, *_args):
        pass


def serve(root: Path):
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(root)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f'http://127.0.0.1:{server.server_port}/'


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Serve a built player on loopback for a personal local probe')
    parser.add_argument('--build',type=Path,required=True)
    parser.add_argument('--port',type=int,default=8000)
    args = parser.parse_args()
    if not (args.build/'index.html').is_file() or not 1 <= args.port <= 65535:
        parser.error('A built player directory and port 1..65535 are required')
    server = ThreadingHTTPServer(('127.0.0.1',args.port),partial(Handler,directory=str(args.build.resolve())))
    print(f'Local player: http://127.0.0.1:{args.port}/ (Ctrl+C to stop)',flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
