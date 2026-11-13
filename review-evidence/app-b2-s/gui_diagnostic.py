"""Temporary APP-B2-S source-GUI wiring diagnosis; no installer or live channel."""
import json
import os
from pathlib import Path
import platform
import sys
import tempfile
import threading
import time
import tkinter as tk
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).parent / 'worktree'))
from tools.production_workspace import desktop, app_updates, update_windows, update_client
from tools.production_workspace.instance import StateLock
from tools.production_workspace.repository import configure
from tools.production_workspace.sources import git
from tools.production_workspace.update_storage import Preferences

HEAD = '1b9665ca5db330f75fc2ec63c85e5dccfef83d58'
results = []
for case in ('skip', 'stop', 'offline', 'optout', 'developer', 'portable'):
    with tempfile.TemporaryDirectory(prefix='gui-') as temp:
        root_path = Path(temp)
        repo = root_path / 'repo'; repo.mkdir()
        git(repo, 'init', '-q', '-b', 'main')
        git(repo, '-c', 'user.name=synthetic', '-c', 'user.email=test@example.invalid',
            'commit', '--allow-empty', '-qm', 'synthetic')
        state = root_path / 'state'
        configure(repo, state, refs=['main'], launcher=True)
        lock = StateLock(state); assert lock.acquire()
        Preferences(lock.directory).write(case != 'optout')
        before = (state / 'config.json').read_bytes()
        entered, release = threading.Event(), threading.Event()
        calls, errors, events, hosts = [], [], [], []
        main_thread = threading.get_ident()
        start = time.monotonic()
        def event(name): events.append({'event': name, 'seconds': round(time.monotonic() - start, 3)})
        def discover(*_):
            assert threading.get_ident() != main_thread
            entered.set(); event('metadata_worker_waiting')
            if not release.wait(10): raise TimeoutError('diagnostic did not release worker')
            raise OSError('synthetic offline')
        real_runtime = desktop.Runtime
        def runtime(*args, **kwargs):
            host = real_runtime(*args, **kwargs); hosts.append(host)
            for name in ('open', 'refresh'):
                original = getattr(host, name)
                def traced(original=original, name=name):
                    assert threading.get_ident() == main_thread
                    calls.append(name); event(name); return original()
                setattr(host, name, traced)
            return host
        real_tk = tk.Tk
        def tk_root():
            window = real_tk(); window.withdraw()  # No user-visible diagnostic window.
            def callback_error(kind, value, trace):
                errors.append(str(value)); release.set(); window.quit()
            window.report_callback_exception = callback_error
            def widgets(parent):
                for child in parent.winfo_children():
                    yield child; yield from widgets(child)
            acted = False
            def drive():
                nonlocal_dummy = None
                nonlocal_vars = None
                # State is kept on this function to avoid a secondary GUI thread.
                try:
                    assert threading.get_ident() == main_thread
                    if time.monotonic() - start > 10: raise AssertionError('GUI timeout')
                    buttons = {w.cget('text'): w for w in widgets(window) if w.winfo_class() in ('TButton', 'TCheckbutton')}
                    if not getattr(drive, 'acted', False):
                        if case in ('skip', 'stop', 'offline'):
                            if not entered.is_set(): window.after(20, drive); return
                            assert calls == []
                            assert str(buttons['Im Browser öffnen'].cget('state')) == 'disabled'
                            assert str(buttons['Ohne Update fortfahren'].cget('state')) == 'normal'
                            # An authenticated second start is reduced to focus during this gate.
                            hosts[0].open_requested.set()
                            if not getattr(drive, 'second', False):
                                drive.second = True; window.after(150, drive); return
                            assert calls == []
                            event('native_controls_respond_while_metadata_waits')
                            if case == 'skip':
                                buttons['Ohne Update fortfahren'].invoke()
                                assert calls == ['open', 'refresh']
                            elif case == 'stop':
                                buttons['Assistent beenden'].invoke()
                                assert calls == []
                            release.set()
                        else:
                            if calls != ['open', 'refresh']: window.after(20, drive); return
                            assert not entered.is_set()
                        drive.acted = True
                    if case == 'stop': return
                    if calls != ['open', 'refresh']: window.after(20, drive); return
                    assert str(buttons['Im Browser öffnen'].cget('state')) == 'normal' or case == 'skip'
                    buttons['Assistent beenden'].invoke(); event('regular_stop')
                except Exception as exc:
                    errors.append(repr(exc)); release.set(); window.quit()
            window.after(20, drive)
            return window
        try:
            with (patch.object(tk, 'Tk', side_effect=tk_root),
                  patch.object(desktop, 'Runtime', side_effect=runtime),
                  patch.object(sys, 'frozen', case != 'developer', create=True),
                  patch.object(update_windows, 'installation', side_effect=ValueError('portable') if case == 'portable' else None,
                               return_value=Mock(version='0.1.0', executable=root_path / 'program/app.exe')),
                  patch.object(app_updates, 'production_trust', return_value={'accepted': {'synthetic': 'synthetic'}}),
                  patch.object(update_client, 'discover', side_effect=discover),
                  patch.object(desktop, 'error_dialog', side_effect=lambda *a: errors.append(str(a[0])))):
                assert desktop.run_gui(desktop.arguments(['--state', str(state), '--no-browser']), lock, HEAD) == 0
            assert not errors, errors
            assert calls == ([] if case == 'stop' else ['open', 'refresh']), calls
            assert (state / 'config.json').read_bytes() == before
            assert Preferences(lock.directory).read() is (case != 'optout')
            assert hosts[0].stopped.is_set() and not hosts[0].thread.is_alive()
            assert not lock.metadata.exists()
            results.append({'case': case, 'passed': True, 'events': events, 'work_calls': calls,
                            'state_preserved': True, 'http_thread_ended': True})
        finally:
            release.set(); lock.close()

report = {'source_head': HEAD, 'platform': platform.platform(), 'python': platform.python_version(),
          'tk': tk.TkVersion, 'results': results,
          'limits': 'Actual Tk event loop with hidden window and real local HTTP/Git lifecycle; source execution, synthetic installation identity/offline channel, no browser process, MSI, installed app, or T03 claim.'}
output = Path(__file__).parent / 'gui-startup.json'
output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
