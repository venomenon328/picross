"""Excluded Windows UI probe with an isolated state and gated channel."""
import os
import time
from types import SimpleNamespace
from unittest.mock import patch

from tools.app_products import PG
from tools.game_app import gate
from tools.game_app.player import visible_window
from tools.production_workspace.app_updates import client, windows
from tools.production_workspace.release_manifest import require
from tools.production_workspace.update_storage import Preferences


def probe(work):
    directory = work / 'Programs' / PG.install_directory
    directory.mkdir(parents=True)
    state = work / PG.state_directory
    preferences = Preferences(state / '.updates')
    calls, starts, observations = [], [], []
    native_window = gate.LauncherWindow
    scenario = ''

    def discover(version, cancel, **_):
        calls.append(scenario)
        if scenario in ('skip', 'close'):
            deadline = time.monotonic() + 8
            while not cancel.is_set() and time.monotonic() < deadline:
                time.sleep(0.02)
            require(cancel.is_set(), 'Native cancellation did not release synthetic transport')
            raise client.Cancelled()
        raise OSError('Isolated offline diagnosis')

    def open_window(version, play, choose, skip, close):
        view = native_window(version, play, choose, skip, close)
        root = view.root
        seen = {'scenario': scenario, 'title': root.title()}
        observations.append(seen)

        def observe():
            seen['window'] = visible_window(os.getpid())
            seen['status'] = view.status.cget('text')
            seen['buttons'] = [button.cget('text') for button in (view.primary, view.setting, view.skip)
                               if button.winfo_ismapped()]
            if scenario == 'skip':
                view.skip.invoke()
            elif scenario == 'close':
                root.tk.call(root.protocol('WM_DELETE_WINDOW'))

        def act():
            if scenario == 'settings':
                observe()
                view.setting.invoke()
                close()
            elif scenario in ('first', 'declined'):
                observe()
                view.primary.invoke()
            else:
                view.primary.invoke()
                root.after(400, observe)

        root.after(400, act)
        return view

    identity = SimpleNamespace(executable=directory / (PG.executable + '.exe'), version=PG.anchor)
    with patch.object(gate, 'LauncherWindow', open_window), patch.object(windows, 'installation', return_value=identity), \
            patch.object(client, 'discover', discover):
        for scenario in ('first', 'declined', 'settings', 'skip', 'close', 'offline'):
            gate.startup(state, directory, lambda: starts.append(scenario), version=PG.anchor)
            if scenario == 'first':
                require(preferences.read() is False, 'First decline not atomically stored')
            if scenario in ('settings', 'skip', 'close'):
                require(preferences.read() is True, 'Unexpected consent change')
    require(calls == ['skip', 'close', 'offline'] and starts == ['first', 'declined', 'skip', 'offline'],
            'Wrong PG request or game start count')
    require(all(row.get('window') for row in observations), 'No visible native PG gate')
    require('nicht möglich' in observations[-1]['status'], 'Offline fallback lacked understandable status')
    return {'native': observations, 'game_start_decisions': starts, 'channel_attempts': calls,
            'limits': 'Native Tk and production callbacks with a synthetic channel, isolated state and counted player dispatch.'}
