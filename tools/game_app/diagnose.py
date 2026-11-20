"""Non-installing Windows diagnosis against actual MSI/build bytes and isolated data."""
import argparse
from contextlib import contextmanager
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
import time

from tools import p1_preflight as toolchain
from tools.app_products import PG
from tools.production_workspace.payload import canonical


def window(pid):
    user = ctypes.windll.user32
    windows = []
    enum_proc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    @enum_proc
    def collect(handle, _):
        owner = wintypes.DWORD()
        user.GetWindowThreadProcessId(handle, ctypes.byref(owner))
        if owner.value == pid and user.IsWindowVisible(handle):
            title = ctypes.create_unicode_buffer(512)
            user.GetWindowTextW(handle, title, len(title))
            if title.value:
                windows.append((handle, title.value))
        return True

    user.EnumWindows(collect, 0)
    return windows[0] if windows else None


def close(handle):
    if not ctypes.windll.user32.PostMessageW(handle, 0x10, 0, 0):  # WM_CLOSE
        raise RuntimeError('Could not close isolated diagnostic window')


def wait(check, description):
    until = time.monotonic() + 45
    while time.monotonic() < until:
        result = check()
        if result:
            return result
        time.sleep(0.25)
    raise RuntimeError('Timed out waiting for ' + description)


def powershell(command, env):
    return subprocess.check_output(
        ['powershell.exe', '-NoProfile', '-NonInteractive', '-Command', command],
        env=env, encoding='utf-8', timeout=30,
    ).strip()


def player_child(pid, env):
    path = powershell(
        f"[Console]::OutputEncoding=[Text.UTF8Encoding]::new(); "
        f"Get-CimInstance Win32_Process -Filter \"ParentProcessId={pid} AND Name='picross-p1.exe'\" "
        "| Select-Object ProcessId,ExecutablePath | ConvertTo-Json -Compress",
        env,
    )
    return json.loads(path) if path else None


def guard_check(guard, local, image, code):
    command = """$ErrorActionPreference='Stop'
    $guard=[Reflection.Assembly]::LoadFile($env:PG_DIAG_GUARD).GetType('Guard')
    $check=$guard.GetMethod('Check',[Reflection.BindingFlags]'Static,NonPublic')
    $argsToCheck=[Object[]] @(([string[]] @($env:PG_DIAG_TARGET)), $env:PG_DIAG_ROOT)
    $check.Invoke($null,$argsToCheck)
    """
    result = powershell(command, {**os.environ, 'PG_DIAG_GUARD': str(guard),
                                  'PG_DIAG_TARGET': str(image), 'PG_DIAG_ROOT': str(local)})
    if result != str(code):
        raise RuntimeError(f'Guard decision {result!r}, expected {code}')


@contextmanager
def started(program, cwd, env):
    with subprocess.Popen([str(program)], cwd=cwd, env=env) as process:
        try:
            yield process
        finally:
            if process.poll() is None:
                # Test-run cleanup only. The installed launcher and guard never kill.
                process.terminate()
                process.wait(timeout=15)


def diagnose(build, output):
    output.mkdir(parents=True, exist_ok=False)
    report = json.loads((build / 'delivery.json').read_bytes())
    guard = build / 'work/Guard.exe'
    with TemporaryDirectory(prefix='isolated-', dir=output) as scratch:
        private = Path(scratch)
        local = private / 'localappdata'
        image = local / 'Programs' / PG.install_directory
        shutil.copytree(build / 'dist' / PG.executable, image)
        foreign_cwd = private / 'unrelated'
        foreign_cwd.mkdir()
        (foreign_cwd / 'picross-p1.exe').write_bytes(b'not the packaged player')
        env = toolchain.isolated_environment(private, 'Windows')
        env['PATH'] = str(foreign_cwd) + os.pathsep + env['PATH']
        user = private / 'appdata/Godot/app_userdata/picross · P1'
        saves = user / 'p1/saves'
        saves.mkdir(parents=True)
        synthetic = saves / 'isolated-sentinel.txt'
        synthetic.write_bytes(b'synthetic existing profile data')

        launcher = image / (PG.executable + '.exe')
        player = image / 'picross-p1.exe'
        pck = image / 'picross-p1.pck'
        guard_check(guard, local, image, 0)
        guard_check(guard, local, foreign_cwd, 2)
        with pck.open('rb'):
            guard_check(guard, local, image, 2)

        # Existing catalog marker from the real exported console wrapper.
        console = build / 'work/player/picross-p1.console.exe'
        marker = toolchain.run_command('pg-catalog', [str(console), '--headless', '--', '--p1-smoke'], env, 60)
        (output / 'catalog.log').write_text(marker['output'], encoding='utf-8')
        toolchain.require_success(marker, 'P1_START_OK')
        if 'SCRIPT ERROR:' in marker['output'] or 'ERROR:' in marker['output']:
            raise RuntimeError('Catalog smoke logged a Godot error')

        with started(launcher, foreign_cwd, env) as normal:
            child = wait(lambda: player_child(normal.pid, env), 'fixed player child')
            if Path(child['ExecutablePath']) != player or normal.poll() is not None:
                raise RuntimeError('Launcher did not hold the actual player')
            handle, title = wait(lambda: window(child['ProcessId']), 'real player window')
            try:
                guard_check(guard, local, image, 2)
            finally:
                close(handle)
            if normal.wait(timeout=30) != 0:
                raise RuntimeError('Launcher did not observe a clean child exit')
        guard_check(guard, local, image, 0)

        with started(player, foreign_cwd, env) as direct:
            handle, _ = wait(lambda: window(direct.pid), 'direct player window')
            try:
                guard_check(guard, local, image, 2)
            finally:
                close(handle)
            if direct.wait(timeout=30) != 0:
                raise RuntimeError('Direct player did not exit cleanly')
        guard_check(guard, local, image, 0)

        # A damaged PCK yields a native error instead of spawning the player.
        pck.rename(image / 'original.pck')
        pck.write_bytes(b'invalid')
        with started(launcher, foreign_cwd, env) as damaged:
            handle, error_title = wait(lambda: window(damaged.pid), 'native damaged payload error')
            if error_title != 'Picross' or player_child(damaged.pid, env):
                raise RuntimeError('Damaged payload did not stop before player start')
            close(handle)
            if damaged.wait(timeout=15) != 1:
                raise RuntimeError('Damaged launcher did not report failure')
        if synthetic.read_bytes() != b'synthetic existing profile data':
            raise RuntimeError('Isolated existing data changed')
    result = {
        'commit': report['commit'], 'msi_sha256': report['msi_sha256'],
        'launcher_sha256': report['exe_sha256'], 'pck_sha256': report['pck_sha256'],
        'catalog_marker': 'P1_START_OK', 'observed_window_title': title,
        'guard': 'idle allowed; foreign target, open PCK, active launcher and direct player refused',
        'damaged_payload': 'launcher dialog and exit 1, no child',
        'isolated_profile_sentinel_unchanged': True,
        'limits': 'Automated Windows diagnosis of build bytes. No installation or personal catalog/controls probe.',
    }
    (output / 'start-guard.json').write_bytes(canonical(result))
    print(json.dumps(result, ensure_ascii=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    diagnose(args.build.resolve(), args.output.resolve())
