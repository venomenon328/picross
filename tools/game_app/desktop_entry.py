"""Fixed PG entry modes: normal play, settings, or helper-authenticated restart."""
import ctypes
import os
from pathlib import Path
import sys

from tools.app_products import PG
from tools.game_app.gate import settings, startup
from tools.game_app.player import play
from tools.game_app.restart import ENV, restart
from tools.production_workspace.install_interlock import InstallInterlock
from tools.production_workspace.update_storage import no_links, read_small
from tools.production_workspace.update_windows import local_appdata


def main():
    mode = sys.argv[1:]
    if mode not in ([], ['--update-settings'], ['--update-restart']):
        raise ValueError('Unbekannter Picross-Aufruf.')
    directory = no_links(Path(sys.executable)).parent
    state = no_links(local_appdata() / PG.state_directory)
    if mode == ['--update-settings']:
        settings(state)
        return
    build = read_small(PG.source / 'build.json')
    if build['format'] != 'picross-pg-build-v2':
        raise ValueError('Picross-Programmidentität fehlt.')
    marker = InstallInterlock(app=PG)
    try:
        marker.acquire()
        if mode == ['--update-restart']:
            restart(directory, build, state)
        else:
            # Any stale private launch data must stay out of the game process.
            for field in ENV:
                os.environ.pop(field, None)
            startup(state, directory, lambda: play(directory, build))
    finally:
        marker.close()


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError) as error:
        ctypes.windll.user32.MessageBoxW(None, str(error), 'Picross', 0x10)
        sys.exit(1)
