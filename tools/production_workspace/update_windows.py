"""Installed-image identity and private pipe/real-handle helper handoff."""
from tools.app_products import PG, PW, PE
import ctypes
from ctypes import wintypes as w
from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading

from .payload import canonical
from .processes import external_environment, system_dlls
from .release import release, version_tuple
from .release_manifest import require, strict_json, hex_string
from .update_storage import no_links, read_small, atomic_json, recover
from .update_verifier import VerifiedCandidate, assess_update, verify_candidate
from .update_client import Cancelled

PACKAGE = Path(__file__).parent


def sha(path):
    return hashlib.sha256(no_links(path).read_bytes()).hexdigest()


def local_appdata():
    shell = ctypes.WinDLL('shell32', use_last_error=True)
    buffer = ctypes.create_unicode_buffer(32768)
    require(shell.SHGetFolderPathW(None, 0x1c, None, 0, buffer) == 0, 'Windows user folder unavailable')
    return Path(buffer.value)


def installed_version(product_code):
    msi = ctypes.WinDLL('msi', use_last_error=True)
    msi.MsiGetProductInfoExW.argtypes = [w.LPCWSTR, w.LPCWSTR, w.DWORD, w.LPCWSTR, w.LPWSTR, ctypes.POINTER(w.DWORD)]
    buffer, size = ctypes.create_unicode_buffer(128), w.DWORD(128)
    require(msi.MsiGetProductInfoExW('{' + product_code + '}', None, 2, 'VersionString', buffer,
                                   ctypes.byref(size)) == 0, 'Per-user installed product unavailable')
    return buffer.value


@dataclass(frozen=True)
class Installation:
    executable: Path
    version: str
    product_code: str
    commit: str
    helper: Path
    helper_sha256: str
    upgrade_code: str
    payload_fingerprint: str


def installation(*, app=PW):
    require(os.name == 'nt' and getattr(sys, 'frozen', False), 'Updates nur in der installierten Windows-App.')
    require(not ctypes.windll.shell32.IsUserAnAdmin(), 'App-Updates nur ohne Administratorrechte starten.')
    expected = no_links(local_appdata() / 'Programs' / app.install_directory / (app.executable + '.exe'))
    require(no_links(sys.executable) == expected, 'Portable App: Updates über manuelle Installation.')
    package = PACKAGE if app == PW else app.source
    built = read_small(package / 'build.json')
    components = read_small(expected.parent / 'components.json')
    build_format = 'picross-pg-build-v2' if app == PG else 'picross-windows-app-v1'
    require(built == components and built['format'] == build_format and
            built['architecture'] == 'windows-x64' and hex_string(built['commit'], 40) and
            hex_string(built['payload_fingerprint'], 64), 'Invalid installed build identity')
    product = release(version=built['version'], app=app)
    require(all(built[k] == product[k] for k in ('version', 'product_code', 'upgrade_code')) and
            installed_version(product['product_code']) == built['version'], 'Installed MSI version mismatch')
    if app == PG:
        import winreg
        registry = app.registry + r'\Installer'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
            require(winreg.QueryValueEx(key, 'Version')[0] == built['version'] and
                    winreg.QueryValueEx(key, 'ProductCode')[0] == '{' + built['product_code'] + '}',
                    'Registered PG application identity mismatch')
        for name in ('release.json', 'update-trust.json'):
            require(sha(no_links(package / name)) == built['resources'][name], 'Unbound PG product resource')
    helper = package / 'UpdateHelper.exe'
    require(hex_string(built['resources'].get('UpdateHelper.exe'), 64) and
            sha(helper) == built['resources']['UpdateHelper.exe'], 'Installed helper binding mismatch')
    return Installation(expected, built['version'], built['product_code'], built['commit'], helper, sha(helper),
                        built['upgrade_code'], built['payload_fingerprint'])


def parent_handle():
    """Real inherited kernel handle, never a PID reopened after parent shutdown."""
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.GetCurrentProcess.restype = w.HANDLE
    kernel.DuplicateHandle.argtypes = [w.HANDLE, w.HANDLE, w.HANDLE, ctypes.POINTER(w.HANDLE), w.DWORD, w.BOOL, w.DWORD]
    current, duplicate = kernel.GetCurrentProcess(), w.HANDLE()
    require(kernel.DuplicateHandle(current, current, current, ctypes.byref(duplicate), 0x101000, True, 0),
            'Cannot bind launcher process')
    return duplicate.value


class Handoff:
    def __init__(self, process, nonce, selection=None):
        self.selection = selection
        self.process, self.nonce, self.committed = process, nonce, False

    def commit(self, runtime):
        require(runtime.stop_requested.is_set() and runtime.stopped.is_set() and not runtime.error,
                'Complete successful runtime/P2 drain required')
        self.go()

    def go(self):
        require(self.process.poll() is None and not self.committed, 'Update helper unavailable')
        self.process.stdin.write(('GO ' + self.nonce + '\n').encode('ascii'))
        self.process.stdin.flush(); self.process.stdin.close()
        self.committed = True

    def abort(self):
        if not self.committed and self.process.stdin and not self.process.stdin.closed:
            self.process.stdin.close()  # EOF means refusal, never implicit installation.


def staged_bytes(stage, name, limit):
    with no_links(stage.path / name).open('rb') as stream:
        raw = stream.read(limit + 1)
    require(len(raw) <= limit, 'Staged file exceeds its verified size limit')
    return raw


def prepare(candidate, stage, identity, runtime, *, cancelled=None, transition=None, app=PW):
    require(type(candidate) is VerifiedCandidate, 'Full verified candidate required')
    # Revalidate bytes, packaged roots and actual installed identity at the final boundary.
    require((installation() if app == PW else installation(app=app)) == identity, 'Installed application changed')
    manifest = strict_json(candidate.manifest_bytes)
    if app == PG:
        files = {name: staged_bytes(stage, name, row['bytes']) for name, row in manifest['assets'].items()}
        raw = staged_bytes(stage, 'manifest.json', len(candidate.manifest_bytes))
        signature = staged_bytes(stage, 'manifest.sig.json', len(candidate.signature_bytes))
    else:
        files = {name: no_links(stage.path / name).read_bytes() for name in manifest['assets']}
        raw = no_links(stage.path / 'manifest.json').read_bytes()
        signature = no_links(stage.path / 'manifest.sig.json').read_bytes()
    verified = verify_candidate(raw, signature, files, app=app)
    require(verified == candidate and assess_update(verified, identity.version, app=app) == 'update', 'Candidate changed')
    report = strict_json(files['delivery.json'])
    require(hex_string(report.get('exe_sha256'), 64) and type(report.get('exe_bytes')) is int and report['exe_bytes'] > 0,
            'Missing new executable binding')
    helper_raw = no_links(identity.helper).read_bytes()
    require(hashlib.sha256(helper_raw).hexdigest() == identity.helper_sha256, 'Helper changed')
    stage.write('UpdateHelper.exe', helper_raw)
    nonce = stage.path.name
    if app == PG:
        # Compute the helper's lock expectations from verified bytes, never
        # from a second read of files that have not been locked yet.
        bindings = {**manifest['assets'],
                    'manifest.json': {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()},
                    'manifest.sig.json': {'bytes': len(signature), 'sha256': hashlib.sha256(signature).hexdigest()}}
    else:
        bindings = {name: {'bytes': (stage.path / name).stat().st_size, 'sha256': sha(stage.path / name)}
                    for name in manifest['assets'].keys() | {'manifest.json', 'manifest.sig.json'}}
    state = runtime.lock.state
    state_names = {PW: ('config.json', '.launcher/address.json', '.launcher/app-updates.json'),
                   PE: ('config.json', '.updates/app-updates.json'),
                   PG: ('.updates/app-updates.json',)}[app]
    state_hashes = {name: sha(state / name) if no_links(state / name).exists() else None for name in state_names}
    if app == PW:
        require(all(state_hashes.values()), 'Missing launcher state')
    formats = {PW: 'picross-update-handoff-v1', PE: 'picross-pe-update-handoff-v1', PG: 'picross-pg-update-handoff-v1'}
    value = {'format': formats[app], 'nonce': nonce, 'state': str(state),
             'pid': os.getpid(), 'old_version': identity.version,
             'old_product': identity.product_code, 'old_commit': identity.commit, 'old_exe_sha256': sha(identity.executable),
             'version': candidate.version, 'product': manifest['product_code'], 'upgrade': manifest['upgrade_code'],
             'commit': candidate.source_commit, 'binding': candidate.binding, 'files': bindings,
             'state_hashes': state_hashes, 'exe_sha256': report['exe_sha256'], 'exe_bytes': report['exe_bytes']}
    if app == PG:
        value['old_fingerprint'] = identity.payload_fingerprint
        value['fingerprint'] = candidate.payload_fingerprint
    else:
        value.update(instance=runtime.metadata['instance'], no_browser=runtime.no_browser)
    if app == PE:
        value['selection'] = runtime.selection
    stage.target('active')
    atomic_json(runtime.lock.directory / 'update-pending.json',
                {'format': 'picross-update-pending-v1', 'nonce': nonce, 'stage': nonce,
                 'version': candidate.version, 'files': sorted(stage.names)})
    handle = None
    process = None
    try:
        handle = parent_handle()
        value['parent_handle'] = handle
        startup = subprocess.STARTUPINFO(lpAttributeList={'handle_list': [handle]})
        with transition if transition is not None else threading.Lock():
            if (cancelled is not None and cancelled.is_set()) or runtime.stop_requested.is_set():
                raise Cancelled()
            with system_dlls():
                process = subprocess.Popen([str(stage.path / 'UpdateHelper.exe')], cwd=stage.path,
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                    startupinfo=startup, close_fds=True, creationflags=subprocess.CREATE_NO_WINDOW,
                    env=external_environment())
        process.stdin.write(canonical(value)); process.stdin.flush()
        replies = queue.Queue()
        def read_reply():
            try:
                replies.put(process.stdout.readline(128))
            except OSError:
                replies.put(b'')
        reader = threading.Thread(target=read_reply, name=app.key.upper()+'-update-handshake', daemon=True)
        reader.start()
        require(replies.get(timeout=20) == ('READY ' + nonce + '\n').encode(), 'Helper handshake failed')
        reader.join()
        return Handoff(process, nonce, value.get('selection'))
    except BaseException:
        if process and process.stdin and not process.stdin.closed:
            process.stdin.close()
        ended = process is None
        if process:
            try:
                process.wait(timeout=5)
                ended = True
            except subprocess.TimeoutExpired:
                pass
        if ended:
            atomic_json(runtime.lock.directory / 'update-result.json',
                        {'format': 'picross-update-result-v1', 'nonce': nonce,
                         'status': 'cancelled', 'version': candidate.version})
            recover(runtime.lock.directory, app=app)
        raise
    finally:
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.CloseHandle.argtypes = [w.HANDLE]
        if handle:
            kernel.CloseHandle(handle)
