"""GAME-APP-D one-time Windows observations on the pinned product source."""
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
from types import SimpleNamespace
from unittest.mock import patch
import winreg

sys.path.insert(0, str(Path.cwd()))

from PIL import ImageGrab, ImageStat
from tools.app_products import PG
from tools.game_app import gate
from tools.production_workspace import update_client as client, update_windows as windows
from tools.production_workspace.release import release

USER32 = ctypes.windll.user32
SHELL = ctypes.windll.shell32
ENUM = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
USER32.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
USER32.GetAncestor.restype = wintypes.HWND


def digest(file):
    with file.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def snapshot(handle, path):
    with ImageGrab.grab(window=handle) as image:
        if not any(value > 5 for value in ImageStat.Stat(image).stddev):
            raise RuntimeError('Window capture contains no visible content')
        image.save(path)
        return list(image.size)


def preview(output, work, version, requested_dpi):
    import tkinter as tk

    scale = str(round(requested_dpi * 100 / 96))
    state = work / f'layout-{scale}' / PG.state_directory
    directory = state.parent / 'Programs' / PG.install_directory
    directory.mkdir(parents=True)
    release = threading.Event()
    first_download = threading.Event()
    findings, starts, problems, calls = [], [], [], []
    original_window = gate.LauncherWindow
    original_root = tk.Tk

    def native_root():
        root = original_root()
        root.geometry('+80+80')
        root.attributes('-topmost', True)
        if requested_dpi != 96:
            root.tk.call('tk', 'scaling', requested_dpi / 72)
        return root

    def discover(version, cancel, **kwargs):
        calls.append('metadata')
        return SimpleNamespace(version='0.1.2'), {}

    def download(metadata, assets, stage, cancel, *, progress, **kwargs):
        calls.append('payload')
        progress('download', 43 * 1024**2, 100 * 1024**2)
        first_download.set()
        if not release.wait(12):
            raise TimeoutError('Review did not observe native progress')
        raise OSError('Synthetic download transport interruption')

    def open_window(version, play, choose, skip, close):
        view = original_window(version, play, choose, skip, close)
        root = view.root
        deadline = time.monotonic() + 12

        def capture(scenario):
            root.update_idletasks()
            handle = USER32.GetAncestor(root.winfo_id(), 2)
            name = f'{scale}-{scenario}.png'
            rect = snapshot(handle, output / name)
            status = view.status.cget('text')
            if view.status.winfo_width() > root.winfo_width() or view.status.winfo_x() < 0:
                raise RuntimeError('Status extends past fixed content width')
            findings.append({'scenario': scenario, 'file': name, 'native_window_px': rect,
                             'content_width_px': root.winfo_width(), 'tk_dpi': root.winfo_fpixels('1i'),
                             'windows_dpi': USER32.GetDpiForWindow(handle), 'status': status,
                             'amount': view.amount.cget('text')})

        def until(test, then):
            if test():
                guarded(then)
            elif time.monotonic() >= deadline:
                guarded(lambda: (_ for _ in ()).throw(TimeoutError('Launcher phase not shown')))
            else:
                root.after(35, lambda: until(test, then))

        def guarded(action):
            try:
                action()
            except Exception as error:
                problems.append(str(error))
                release.set()
                close()

        def first():
            capture('first')
            if view.primary.cget('text') != 'Ohne Updates spielen':
                raise RuntimeError('No first-decision offline action')
            view.setting.invoke()
            if calls or starts:
                raise RuntimeError('Consent caused activity')
            view.primary.invoke()
            until(lambda: first_download.is_set() and '43 %' in view.amount.cget('text'),
                  lambda: root.after(150, lambda: guarded(downloading)))

        def downloading():
            capture('download')
            release.set()
            until(lambda: 'nicht möglich' in view.status.cget('text'),
                  lambda: root.after(180, lambda: guarded(fallback)))

        def fallback():
            capture('error')
            if view.amount.cget('text'):
                raise RuntimeError('Error carried a success/percentage message')

        root.after(450, lambda: guarded(first))
        return view

    identity = SimpleNamespace(executable=directory / 'Picross-Game.exe', version='0.1.1')
    with patch.object(tk, 'Tk', native_root), patch.object(gate, 'LauncherWindow', open_window), \
            patch.object(windows, 'installation', return_value=identity), \
            patch.object(client, 'discover', discover), patch.object(client, 'download', download):
        gate.startup(state, directory, lambda: starts.append('existing-player'), version=version)
    if problems or calls != ['metadata', 'payload'] or starts != ['existing-player']:
        raise RuntimeError(f'Unexpected launcher trial: {problems}, {calls}, {starts}')
    if len(findings) != 3 or len({row['content_width_px'] for row in findings}) != 1:
        raise RuntimeError(f'Launcher changed its width across phases: {findings}')
    return findings


def menu():
    folder = ctypes.create_unicode_buffer(32768)
    if SHELL.SHGetFolderPathW(None, 2, None, 0, folder):
        raise RuntimeError('Could not read the Windows Programs folder')
    return Path(folder.value) / 'Picross'


def identity(version, expected_commit, shortcut_names):
    product = release(version=version, app=PG)
    installed = windows.local_appdata() / 'Programs' / PG.install_directory
    path = PG.registry + r'\Installer'
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
        version_key = winreg.QueryValueEx(key, 'Version')[0]
        code_key = winreg.QueryValueEx(key, 'ProductCode')[0]
    components = json.loads((installed / 'components.json').read_bytes())
    embedded = json.loads((installed / '_internal' / PG.package / 'build.json').read_bytes())
    links = sorted(p.name for p in menu().glob('*.lnk'))
    if (version_key != version or code_key != '{' + product['product_code'] + '}' or
            windows.installed_version(product['product_code']) != version or embedded != components or
            components['version'] != version or components['commit'] != expected_commit or
            links != sorted(shortcut_names)):
        raise RuntimeError(f'Installed identity or shortcuts mismatch: {version_key!r}, {code_key!r}, {links!r}')
    return {'version': version, 'product_code': product['product_code'], 'commit': components['commit'],
            'launcher_sha256': digest(installed / 'Picross-Game.exe'), 'start_menu': links}


def msi_progress(pid):
    dialogs = []

    @ENUM
    def inspect(hwnd, _):
        owner = wintypes.DWORD()
        USER32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
        if owner.value == pid and USER32.IsWindowVisible(hwnd):
            children = []

            @ENUM
            def child_control(child, _):
                name = ctypes.create_unicode_buffer(256)
                USER32.GetClassNameW(child, name, len(name))
                if name.value == 'msctls_progress32' and USER32.IsWindowVisible(child):
                    children.append(name.value)
                return True

            USER32.EnumChildWindows(hwnd, child_control, 0)
            if children:
                dialogs.append(hwnd)
        return True

    USER32.EnumWindows(inspect, 0)
    return dialogs[0] if dialogs else None


def msiexec(action, target, ui, log, screenshot=None):
    system = Path(os.environ['SystemRoot']) / 'System32/msiexec.exe'
    args = [str(system), action, str(target), ui, '/norestart', 'ALLUSERS=2',
            'MSIINSTALLPERUSER=1', 'REBOOT=ReallySuppress', 'MSIRESTARTMANAGERCONTROL=Disable',
            '/l*v', str(log)]
    image = None
    with subprocess.Popen(args) as process:
        end = time.monotonic() + 420
        while process.poll() is None and time.monotonic() < end:
            if screenshot is not None and image is None:
                hwnd = msi_progress(process.pid)
                if hwnd is not None:
                    try:
                        image = snapshot(hwnd, screenshot)
                    except (OSError, RuntimeError):
                        pass
            time.sleep(0.035 if image is None else 0.2)
        return {'exit': process.wait(timeout=5), 'progress_window_px': image}


def upgrade(output, work, candidate, expected_commit):
    local = windows.local_appdata()
    installed = local / 'Programs' / PG.install_directory
    if installed.exists() or menu().exists() or (local / PG.state_directory).exists():
        raise ValueError('Existing installation or PG profile. Test requires an empty runner.')
    previous, new = '0.1.2', '0.1.3'
    old_product, new_product = release(version=previous, app=PG), release(version=new, app=PG)
    original = work / old_product['filename']
    url = 'https://github.com/venomenon328/picross/releases/download/pg-v0.1.2/' + original.name
    subprocess.run(['curl.exe', '--fail', '--location', '--silent', '--show-error', '--output', str(original), url],
                   check=True, timeout=180)
    if digest(original) != '1a1204793b04fc0895fc0bdc9521caf5789fed32a5ef78f1f48465af198e4fdf':
        raise RuntimeError('Baseline download differs from the released asset')
    report = json.loads((candidate / 'delivery.json').read_bytes())
    msi = candidate / new_product['filename']
    candidate_hash = digest(msi)
    if candidate_hash != report['msi_sha256'] or report['commit'] != expected_commit:
        raise RuntimeError('MSI candidate is not bound to this product head')
    result = {'baseline_sha256': digest(original), 'candidate_sha256': candidate_hash,
              'runner_admin_token': bool(SHELL.IsUserAnAdmin())}
    try:
        result['baseline_install'] = msiexec('/i', original, '/qn', output / 'baseline-install.log')
        if result['baseline_install']['exit'] != 0:
            return result
        result['before'] = identity(previous, '86fb9e62691eea61afe2a39ba8cf278734b3e315',
                                    ['Picross.lnk', 'Picross – Update-Einstellungen.lnk'])
        result['upgrade'] = msiexec('/i', msi, '/passive', output / 'upgrade.log', output / 'msi-passive.png')
        if result['upgrade']['exit'] == 0:
            result['after'] = identity(new, expected_commit, ['Picross.lnk'])
            if result['after']['launcher_sha256'] != report['exe_sha256']:
                raise RuntimeError('Installed launcher bytes differ from the candidate')
        return result
    finally:
        if installed.exists():
            product_code = new_product['product_code'] if result.get('upgrade', {}).get('exit') == 0 else old_product['product_code']
            result['uninstall'] = msiexec('/x', '{' + product_code + '}', '/qn', work / 'test-uninstall.log')


def main():
    output, work, candidate, head = map(Path, sys.argv[1:])
    product_head = str(head)
    actual = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    if product_head != actual:
        raise ValueError('Review checkout does not match the product head')
    output.mkdir()
    work.mkdir()
    report = {'product_head': actual, 'launcher': {},
              'preview_limits': 'Native Tk, isolated preferences, synthetic channel statuses. 125% is Tk-scaled.'}
    try:
        for dpi in (96, 120):
            report['launcher'][dpi] = preview(output, work, '0.1.3', dpi)
        if str(candidate) != '-':
            report['msi'] = upgrade(output, work, candidate, actual)
            if 'after' not in report['msi'] or report['msi']['upgrade']['progress_window_px'] is None:
                raise RuntimeError('Real MSI upgrade and passive progress not both observed')
    finally:
        (output / 'review.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(report, ensure_ascii=True))


if __name__ == '__main__':
    main()
