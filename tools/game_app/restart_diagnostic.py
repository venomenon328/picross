"""Excluded adapter for invoking the actual PG IPC and player with isolated data."""
from pathlib import Path
import os
import sys
import time
import threading
from types import SimpleNamespace
from unittest.mock import patch

from tools.app_products import PG
from tools.game_app import gate, restart
from tools.game_app.diagnose import close
from tools.game_app.player import play
from tools.production_workspace.app_updates import client, windows
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
                confirm(process, handle)
            finally:
                timer = threading.Timer(1.2, close, args=(handle,))
                timer.start()

        try:
            play(directory, current, window)
        finally:
            if timer:
                timer.join()

    if mode != 'legacy':
        directory = state.parent / 'Programs' / PG.install_directory
        installed.executable = directory / (PG.executable + '.exe')
        windows_seen, searches, statuses = [], [], []
        native = gate.LauncherWindow
        deadline = time.monotonic() + 45

        def open_window(*args):
            view = native(*args)
            windows_seen.append(view)
            def observe_completion():
                status = view.status.cget('text')
                if view.install.winfo_ismapped() or 'Wiederanlauf unbestätigt' in status:
                    statuses.append(status)
                    view.root.destroy()
                elif time.monotonic() >= deadline:
                    view.root.destroy()
                else:
                    view.root.after(75, observe_completion)
            view.root.after(100, observe_completion)
            return view

        def discover(*args, **kwargs):
            searches.append(True)
            return SimpleNamespace(version='0.1.99'), {}

        original = restart.data
        def reply(value):
            if mode in ('identity', 'challenge', 'pid', 'window'):
                field = {'identity': 'commit'}.get(mode, mode)
                value[field] = {'commit': '0' * 40, 'challenge': '0' * 48,
                                'pid': os.getpid() + 1, 'window': 0}[field]
                # Use the actual MAC for the altered fields so the helper must check the binding.
                unsigned = {k: v for k, v in value.items() if k != 'proof'}
                value['proof'] = restart.mac(secret, 'pg-launcher-ready:', unsigned)
            return original(value)

        secret = os.environ[restart.ENV[1]]
        with patch.object(restart, 'installation', return_value=installed), patch.object(restart, 'data', reply), \
                patch.object(windows, 'installation', return_value=installed), patch.object(client, 'discover', discover), \
                patch.object(gate, 'LauncherWindow', open_window):
            gate.startup(state, directory, lambda: seen.append('play'), version=installed.version,
                         confirm_launcher=lambda hwnd: restart.confirm_launcher(state, hwnd))
        require(len(windows_seen) == len(statuses) == 1 and not seen and len(searches) == int(mode == 'confirmed'),
                'Unexpected launcher, player or fresh search count')
        output.write_bytes(canonical({'scenario': mode, 'launcher_pid': os.getpid(), 'launcher_count': 1,
                                      'child_start_count': 0, 'fresh_searches': len(searches), 'status': statuses[0]}))
        return

    marker = InstallInterlock(app=PG)
    try:
        marker.acquire()
        with patch.object(restart, 'installation', return_value=installed), patch.object(restart, 'play', observe):
            restart.restart(image, build, state)
    finally:
        marker.close()
    require(len(seen) == 1, 'PG restart did not start exactly one bound player')
    output.write_bytes(canonical({'scenario': mode, 'observation': seen[0], 'child_start_count': len(seen)}))


if __name__ == '__main__':
    run(*map(Path, sys.argv[1:4]), sys.argv[4])
