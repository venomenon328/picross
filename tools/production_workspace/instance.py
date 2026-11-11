"""Per-state OS lock and challenge-authenticated, closed lifecycle protocol."""
import hashlib
import hmac
import http.client
import json
import os
from pathlib import Path
import secrets
import time

PROTOCOL = 'picross-launcher-v1'


def data(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')


def mac(key, prefix, value):
    return hmac.new(key.encode('ascii'), prefix.encode('ascii') + data(value), hashlib.sha256).hexdigest()


def private_directory(path):
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    if path.is_symlink() or getattr(path, 'is_junction', lambda: False)():
        raise ValueError('Launcherzustand darf kein Link sein.')
    if os.name == 'nt':
        # Protected DACL: this process user + SYSTEM, including child files.
        import ctypes
        from ctypes import wintypes
        adv = ctypes.WinDLL('advapi32', use_last_error=True)
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.GetCurrentProcess.restype = wintypes.HANDLE
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel.LocalFree.argtypes = [ctypes.c_void_p]
        kernel.LocalFree.restype = ctypes.c_void_p
        adv.OpenProcessToken.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE)]
        adv.GetTokenInformation.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p,
                                            wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
        adv.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD,
                                                                            ctypes.POINTER(ctypes.c_void_p), ctypes.c_void_p]
        token = wintypes.HANDLE()
        if not adv.OpenProcessToken(kernel.GetCurrentProcess(), 8, ctypes.byref(token)):
            raise OSError('Eigener Windowsbenutzer nicht prüfbar.')
        try:
            size = wintypes.DWORD()
            adv.GetTokenInformation(token, 1, None, 0, ctypes.byref(size))
            buffer = ctypes.create_string_buffer(size.value)
            if not adv.GetTokenInformation(token, 1, buffer, size, ctypes.byref(size)):
                raise OSError('Windowsbenutzer nicht lesbar.')
            sid = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_void_p))[0]
            sid_text = wintypes.LPWSTR()
            adv.ConvertSidToStringSidW.argtypes = [ctypes.c_void_p, ctypes.POINTER(wintypes.LPWSTR)]
            if not adv.ConvertSidToStringSidW(sid, ctypes.byref(sid_text)):
                raise OSError('Windowsbenutzer nicht lesbar.')
            try:
                sddl = 'D:P(A;OICI;FA;;;SY)(A;OICI;FA;;;' + sid_text.value + ')'
            finally:
                kernel.LocalFree(ctypes.cast(sid_text, ctypes.c_void_p))
            descriptor = ctypes.c_void_p()
            if not adv.ConvertStringSecurityDescriptorToSecurityDescriptorW(sddl, 1, ctypes.byref(descriptor), None):
                raise OSError('Privater Launcherzustand nicht schützbar.')
            try:
                adv.SetFileSecurityW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, ctypes.c_void_p]
                if not adv.SetFileSecurityW(str(path), 0x80000004, descriptor):
                    raise OSError('Privater Launcherzustand nicht schützbar.')
            finally:
                kernel.LocalFree(descriptor)
        finally:
            kernel.CloseHandle(token)
    else:
        path.chmod(0o700)


class StateLock:
    def __init__(self, state):
        self.state = Path(state).resolve()
        if any((parent / '.git').exists() for parent in (self.state, *self.state.parents)):
            raise ValueError('Zustandsordner muss außerhalb eines Git-Arbeitsbaums liegen.')
        self.directory = self.state / '.launcher'
        private_directory(self.directory)
        self.metadata = self.directory / 'instance.json'
        self.file = None

    def acquire(self):
        path = self.directory / 'lock'
        if path.is_symlink():
            raise ValueError('Ungültiger Instanzlock.')
        stream = path.open('a+b')
        stream.seek(0, 2)
        if not stream.tell():
            stream.write(b'0'); stream.flush()
        stream.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            stream.close()
            return False
        self.file = stream
        # Acquired OS lock proves the previous owner has ended, irrespective of
        # PID reuse. Stale state is never used to kill or open anything.
        self.metadata.unlink(missing_ok=True)
        return True

    def publish(self, value):
        if self.file is None:
            raise RuntimeError('Instanzlock fehlt.')
        temporary = self.directory / 'instance.tmp'
        with temporary.open('w', encoding='ascii') as stream:
            json.dump(value, stream)
        temporary.replace(self.metadata)

    def read(self):
        if self.metadata.is_symlink() or self.metadata.stat().st_size > 4096:
            raise ValueError('Ungültige Instanzmetadaten.')
        value = json.loads(self.metadata.read_text(encoding='ascii'))
        if (set(value) != {'protocol', 'build', 'instance', 'key', 'port', 'pid'} or
                value['protocol'] != PROTOCOL or type(value['port']) is not int or
                not 1 <= value['port'] <= 65535 or
                not all(isinstance(value[k], str) and 16 <= len(value[k]) <= 160
                        for k in ('build', 'instance', 'key'))):
            raise ValueError('Instanzprotokoll ist unbekannt. Vorhandenen Starter regulär beenden.')
        return value

    def close(self):
        if self.file:
            self.metadata.unlink(missing_ok=True)
            self.file.close()
            self.file = None


def control(metadata, action):
    if action not in ('identify', 'open', 'stop'):
        raise ValueError('Unbekannte Steueraktion.')
    request = {'action': action, 'challenge': secrets.token_hex(24)}
    request['proof'] = mac(metadata['key'], 'request:', request)
    connection = http.client.HTTPConnection('127.0.0.1', metadata['port'], timeout=2)
    try:
        connection.request('POST', '/control/v1', data(request), {'Content-Type': 'application/json'})
        response = connection.getresponse()
        raw = response.read(8193)
        if response.status != 200 or len(raw) > 8192:
            raise ValueError('Laufende Instanz konnte nicht authentisiert werden.')
        value = json.loads(raw)
        fields = {'protocol', 'build', 'instance', 'challenge', 'state', 'proof'} | ({'browser_url'} if action == 'open' else set())
        if (not isinstance(value, dict) or set(value) != fields or
                not all(isinstance(v, str) for v in value.values())):
            raise ValueError('Fremder Dienst oder ungültiger Steuervertrag.')
        proof = value.pop('proof')
        if (not hmac.compare_digest(proof, mac(metadata['key'], 'response:', value)) or
                value.get('challenge') != request['challenge'] or value.get('instance') != metadata['instance'] or
                value.get('protocol') != PROTOCOL or value.get('build') != metadata['build']):
            raise ValueError('Fremder Dienst oder unpassende Instanz. Keine Aktion ausgeführt.')
        if action == 'open':
            prefix = 'http://127.0.0.1:' + str(metadata['port']) + '/#'
            token = value['browser_url'].removeprefix(prefix)
            if not value['browser_url'].startswith(prefix) or len(token) != 43 or not all(c.isalnum() or c in '_-' for c in token):
                raise ValueError('Ungültige Browseradresse der Instanz.')
        return value
    finally:
        connection.close()


def existing(lock, build, action='open', timeout=15):
    deadline = time.monotonic() + timeout
    while True:
        try:
            metadata = lock.read()
            identity = control(metadata, 'identify')
            if identity['build'] != build:
                raise ValueError('Andere Programmversion läuft. Diese zuerst regulär beenden.')
            if identity['state'] != 'ready':
                raise ValueError('Assistent wird beendet. Danach erneut starten.')
            return control(metadata, action)
        except (FileNotFoundError, ConnectionError, TimeoutError):
            if time.monotonic() >= deadline:
                raise ValueError('Start läuft noch oder ist nicht erreichbar. Warten und erneut starten; historische CMD vorher mit Strg+C beenden.') from None
            time.sleep(0.1)
