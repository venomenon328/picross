"""Excluded Windows UI probe with an isolated state and gated channel."""
import os
import time
import threading

from PIL import ImageGrab
from types import SimpleNamespace
from unittest.mock import patch

from tools.app_products import PG
from tools.game_app import gate
from tools.game_app.player import visible_window
from tools.production_workspace.app_updates import client, windows
from tools.production_workspace.release_manifest import require
from tools.production_workspace.update_storage import Preferences


def probe(work, output, metadata, assets, download_offer, *, capture):
    directory = work / 'Programs' / PG.install_directory
    directory.mkdir(parents=True)
    state = work / PG.state_directory
    preferences = Preferences(state / '.updates')
    calls, starts, downloads, observations = [], [], [], []
    native_window = gate.LauncherWindow
    release_search = threading.Event()

    def discover(version, cancel, **_):
        calls.append(scenario)
        deadline = time.monotonic() + 12
        while not release_search.wait(0.02):
            client.checkpoint(cancel, deadline)
        return metadata, assets

    def download(meta, links, stage, cancel, *, progress, app):
        downloads.append(scenario)
        require(meta is metadata and links is assets, 'Offered candidate changed')
        def count(phase, received, total):
            progress(phase, received, total)
            if received > total // 4:
                deadline = time.monotonic() + 12
                while not cancel.is_set():
                    client.checkpoint(cancel, deadline)
                    time.sleep(0.02)
        return download_offer(meta, links, stage, cancel, progress=count, app=app)

    def open_window(*args):
        view = native_window(*args)
        root = view.root
        deadline = time.monotonic() + 15
        errors = []
        def fail(exc, value, trace):
            errors.append(str(value))
            root.destroy()
        root.report_callback_exception = fail
        observations.append({'scenario': scenario, 'observed': [], 'errors': errors})
        def record(name):
            handle = int(root.wm_frame(), 0)
            require(handle and visible_window(os.getpid()), 'No visible launcher')
            observations[-1]['observed'].append({'state': name, 'status': view.status.cget('text'),
                'amount': view.amount.cget('text'), 'buttons': [button.cget('text') for button in
                (view.primary, view.setting, view.install) if button.winfo_ismapped()]})
            if capture and name in ('search', 'offer', 'download'):
                root.update_idletasks()
                ImageGrab.grab(window=handle).save(output / ('launcher-' + name + '.png'))

        def act():
            require(time.monotonic() < deadline, 'Native action timed out: ' + scenario)
            if scenario == 'first':
                record('first')
                view.primary.invoke()
            elif scenario == 'enable' and preferences.read() is not True:
                view.setting.invoke()
                root.after(100, act)
            elif scenario in ('enable', 'close', 'opt_out') and scenario in calls:
                record('search' if scenario == 'enable' else scenario)
                if scenario == 'opt_out':
                    view.setting.invoke()
                root.tk.call(root.protocol('WM_DELETE_WINDOW'))
            elif scenario == 'play_search' and scenario in calls:
                view.primary.invoke()
            elif scenario in ('play_offer', 'download') and view.install.winfo_ismapped():
                if scenario == 'play_offer':
                    record('offer')
                    view.primary.invoke()
                else:
                    view.install.invoke()
                    view.install.invoke()
                    root.after(100, act)
            elif scenario == 'download' and view.amount.cget('text') and int(view.amount.cget('text').split()[0]) >= 25:
                record('download')
                view.primary.invoke()
            else:
                root.after(75, act)
        root.after(150, act)
        return view

    identity = SimpleNamespace(executable=directory / (PG.executable + '.exe'), version=PG.anchor)
    with patch.object(gate, 'LauncherWindow', open_window), patch.object(windows, 'installation', return_value=identity), \
            patch.object(client, 'discover', discover), patch.object(client, 'download', download):
        for scenario in ('first', 'enable', 'close', 'play_search', 'play_offer', 'download', 'opt_out'):
            if scenario in ('play_offer', 'download'):
                release_search.set()
            else:
                release_search.clear()
            gate.startup(state, directory, lambda: starts.append(scenario), version=PG.anchor)
            require(not observations[-1]['errors'], str(observations[-1]['errors']))
            require(preferences.read() is (scenario not in ('first', 'opt_out')), 'Unexpected saved consent')
    require(calls == ['enable', 'close', 'play_search', 'play_offer', 'download', 'opt_out'] and
            starts == ['first', 'play_search', 'play_offer', 'download'] and downloads == ['download'],
            'Wrong discovery, download or player dispatch count')
    return {'native': observations, 'player_dispatch': starts, 'metadata': calls, 'downloads': downloads,
            'limits': 'Native Tk, isolated state, authenticated synthetic publication, real staged asset progress.'}
