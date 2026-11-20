"""Excluded adapter for invoking the actual PG IPC and player with isolated data."""
from pathlib import Path
import sys
import threading
from types import SimpleNamespace
from unittest.mock import patch

from tools.app_products import PG
from tools.game_app import restart
from tools.game_app.diagnose import close
from tools.game_app.player import play
from tools.production_workspace.install_interlock import InstallInterlock
from tools.production_workspace.payload import canonical
from tools.production_workspace.release_manifest import require, strict_json


def run(state, image, output, mode):
    build = strict_json((image / 'components.json').read_bytes())
    installed = SimpleNamespace(version=build['version'], commit=build['commit'],
                                payload_fingerprint=build['payload_fingerprint'])
    seen = []

    def observe(directory, current, confirm):
        timer = None

        def window(process, handle):
            nonlocal timer
            seen.append({'pid': process.pid, 'window': handle})
            try:
                if mode != 'lost':
                    confirm(process, handle)
            finally:
                timer = threading.Timer(1.2, close, args=(handle,))
                timer.start()

        try:
            play(directory, current, window)
        finally:
            if timer:
                timer.join()

    real_mac = restart.mac

    def authenticate(key, prefix, value):
        if mode == 'forged' and prefix == 'pg-started:':
            return '0' * 64
        return real_mac(key, prefix, value)

    marker = InstallInterlock(app=PG)
    try:
        marker.acquire()
        with patch.object(restart, 'installation', return_value=installed), patch.object(restart, 'play', observe), \
                patch.object(restart, 'mac', authenticate):
            restart.restart(image, build, state)
    finally:
        marker.close()
    require(len(seen) == 1, 'PG restart did not start exactly one bound player')
    output.write_bytes(canonical({'scenario': mode, 'observation': seen[0], 'child_start_count': len(seen)}))


if __name__ == '__main__':
    run(*map(Path, sys.argv[1:4]), sys.argv[4])
