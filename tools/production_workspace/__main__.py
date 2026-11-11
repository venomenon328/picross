"""Python/Git launcher, persists only explicit setup and private cache state."""
import argparse
import os
from pathlib import Path
import shutil
import sys
import threading
import webbrowser

from .repository import configure, Repository
from .server import Service, Server
from tools.puzzle_production.contract import InvalidInput


def main(argv=None):
    parser = argparse.ArgumentParser(description='Picross · lokale Produktionsansicht')
    default = Path(os.environ.get('LOCALAPPDATA', str(Path.home() / '.local' / 'share'))) / 'PicrossProductionWorkspace'
    parser.add_argument('--state', type=Path, default=default)
    parser.add_argument('--setup', action='store_true')
    parser.add_argument('--repository', type=Path)
    parser.add_argument('--remote', help='Ausdrücklich gewählte Remote-URL; sonst nur lokale Gitstände')
    parser.add_argument('--ref', action='append', dest='refs')
    parser.add_argument('--port', type=int, default=0)
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args(argv)
    try:
        if sys.version_info < (3, 11):
            raise InvalidInput('Python 3.11 oder neuer ist erforderlich.')
        if not shutil.which('git'):
            raise InvalidInput('Git fehlt. Bitte Git installieren und den Starter erneut öffnen.')
        try:
            import PIL  # noqa: F401 -- fail before serving a partially working UI
        except ImportError as exc:
            raise InvalidInput('Bildleser fehlt. Pillow in der isolierten Pythonumgebung gemäß Anleitung installieren.') from exc
        if args.setup or not (args.state / 'config.json').exists():
            repository = args.repository
            if repository is None:
                repository = Path(input('Projektcheckout (Ordner): ').strip().strip('"'))
            remote = args.remote
            if remote is None and not args.setup:
                choice = input('Quelle: [1] Nur lokale Gitstände [2] Mit Remote aktualisieren (1): ').strip()
                if choice == '2':
                    remote = input('Bewusst gewählte Remote-URL (HTTPS/SSH): ').strip()
            configure(repository, args.state, remote=remote, refs=args.refs)
        elif args.repository or args.remote or args.refs:
            raise InvalidInput('Einrichtung existiert bereits. Änderungen benötigen einen neuen eigenen Zustandsordner.')
        if not 0 <= args.port <= 65535:
            raise InvalidInput('Port muss zwischen 0 und 65535 liegen.')
        repository = Repository(args.state)
        repository.refresh()
        service = Service(repository)
        try:
            server = Server(service, args.port)
        except OSError as exc:
            raise InvalidInput('Port ist belegt. Ohne --port automatisch einen freien Port wählen.') from exc
        url = server.origin + '/#' + service.secret
        print('Produktionsansicht läuft. Beenden mit Strg+C. Sitzungsschlüssel werden nicht protokolliert.')
        if not args.no_browser:
            if not webbrowser.open(url):
                raise InvalidInput('Browser konnte nicht geöffnet werden. Standardbrowser einrichten und Starter erneut ausführen.')
        try:
            server.serve_forever(poll_interval=0.25)
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
        return 0
    except (ValueError, OSError, RuntimeError) as exc:
        print('Start nicht möglich: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
