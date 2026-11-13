"""Installed-image identity and private pipe/real-handle helper handoff."""
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


def installation():
    require(os.name == 'nt' and getattr(sys, 'frozen', False), 'Updates nur in der installierten Windows-App.')
    require(not ctypes.windll.shell32.IsUserAnAdmin(), 'App-Updates nur ohne Administratorrechte starten.')
    expected = no_links(local_appdata() / 'Programs/Picross-Produktionsassistent/Picross-Start.exe')
    require(no_links(sys.executable) == expected, 'Portable App: Updates über manuelle Installation.')
    built = read_small(PACKAGE / 'build.json')
    components = read_small(expected.parent / 'components.json')
    require(built == components and built['format'] == 'picross-windows-app-v1' and
            built['architecture'] == 'windows-x64' and hex_string(built['commit'], 40), 'Invalid installed build identity')
    product = release(version=built['version'])
    require(all(built[k] == product[k] for k in ('version', 'product_code', 'upgrade_code')) and
            installed_version(product['product_code']) == built['version'], 'Installed MSI version mismatch')
    helper = PACKAGE / 'UpdateHelper.exe'
    require(hex_string(built['resources'].get('UpdateHelper.exe'), 64) and
            sha(helper) == built['resources']['UpdateHelper.exe'], 'Installed helper binding mismatch')
    return Installation(expected, built['version'], built['product_code'], built['commit'], helper, sha(helper))


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
    def __init__(self, process, nonce):
        self.process, self.nonce, self.committed = process, nonce, False

    def commit(self, runtime):
        require(runtime.stop_requested.is_set() and runtime.stopped.is_set() and not runtime.error,
                'Complete successful runtime/P2 drain required')
        require(self.process.poll() is None and not self.committed, 'Update helper unavailable')
        self.process.stdin.write(('GO ' + self.nonce + '\n').encode('ascii'))
        self.process.stdin.flush(); self.process.stdin.close()
        self.committed = True

    def abort(self):
        if not self.committed and self.process.stdin and not self.process.stdin.closed:
            self.process.stdin.close()  # EOF means refusal, never implicit installation.


def prepare(candidate, stage, identity, runtime):
    require(type(candidate) is VerifiedCandidate, 'Full verified candidate required')
    # Revalidate bytes, packaged roots and actual installed identity at the final boundary.
    require(installation() == identity, 'Installed application changed')
    manifest = strict_json(candidate.manifest_bytes)
    files = {name: no_links(stage.path / name).read_bytes() for name in manifest['assets']}
    verified = verify_candidate(no_links(stage.path / 'manifest.json').read_bytes(),
                                no_links(stage.path / 'manifest.sig.json').read_bytes(), files)
    require(verified == candidate and assess_update(verified, identity.version) == 'update', 'Candidate changed')
    report = strict_json(files['delivery.json'])
    require(hex_string(report.get('exe_sha256'), 64) and type(report.get('exe_bytes')) is int and report['exe_bytes'] > 0,
            'Missing new executable binding')
    helper_raw = no_links(identity.helper).read_bytes()
    require(hashlib.sha256(helper_raw).hexdigest() == identity.helper_sha256, 'Helper changed')
    stage.write('UpdateHelper.exe', helper_raw)
    nonce = stage.path.name
    bindings = {name: {'bytes': (stage.path / name).stat().st_size, 'sha256': sha(stage.path / name)}
                for name in manifest['assets'].keys() | {'manifest.json', 'manifest.sig.json'}}
    state = runtime.lock.state
    state_hashes = {name: sha(state / name) for name in ('config.json', '.launcher/address.json', '.launcher/app-updates.json')}
    value = {'format': 'picross-update-handoff-v1', 'nonce': nonce, 'state': str(state),
             'pid': os.getpid(), 'instance': runtime.metadata['instance'], 'old_version': identity.version,
             'old_product': identity.product_code, 'old_commit': identity.commit, 'old_exe_sha256': sha(identity.executable),
             'version': candidate.version, 'product': manifest['product_code'], 'upgrade': manifest['upgrade_code'],
             'commit': candidate.source_commit, 'binding': candidate.binding, 'files': bindings,
             'state_hashes': state_hashes, 'exe_sha256': report['exe_sha256'], 'exe_bytes': report['exe_bytes'],
             'no_browser': runtime.no_browser}
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
        threading.Thread(target=read_reply, name='PW-update-handshake', daemon=True).start()
        require(replies.get(timeout=20) == ('READY ' + nonce + '\n').encode(), 'Helper handshake failed')
        return Handoff(process, nonce)
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
            recover(runtime.lock.directory)
        raise
    finally:
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.CloseHandle.argtypes = [w.HANDLE]
        if handle:
            kernel.CloseHandle(handle)
