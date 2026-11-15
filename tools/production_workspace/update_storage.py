"""Private launcher update decisions and owned, flat staging (no checkout I/O)."""
from pathlib import Path
import os
import secrets
import stat

from .instance import private_directory
from .payload import canonical
from .release_manifest import require, shape, strict_json
from .release import release

PREFERENCE = 'picross-app-update-preference-v1'


def no_links(path):
    path = Path(os.path.abspath(path))
    for item in (*reversed(path.parents), path):
        try:
            info = item.lstat()
        except FileNotFoundError:
            continue
        require(not stat.S_ISLNK(info.st_mode) and
                not getattr(info, 'st_file_attributes', 0) & 0x400, 'Update path contains a link/reparse point')
    return path


def read_small(path, limit=32768):
    no_links(path)
    with path.open('rb') as stream:
        raw = stream.read(limit + 1)
    require(len(raw) <= limit, 'Update state exceeds its size limit')
    return strict_json(raw)


def atomic_json(path, value):
    no_links(path)
    temporary = path.with_name(path.name + '.' + secrets.token_hex(12) + '.tmp')
    try:
        with temporary.open('xb') as stream:
            stream.write(canonical(value)); stream.flush(); os.fsync(stream.fileno())
        no_links(path)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


class Preferences:
    def __init__(self, directory):
        self.directory = no_links(directory)
        private_directory(self.directory)
        self.path = self.directory / 'app-updates.json'

    def read(self):
        if not self.path.exists():
            return None
        value = read_small(self.path, 1024)
        shape(value, 'format enabled', 'Invalid update preference')
        require(value['format'] == PREFERENCE and type(value['enabled']) is bool, 'Invalid update preference')
        return value['enabled']

    def write(self, enabled):
        require(type(enabled) is bool, 'Explicit update decision required')
        atomic_json(self.path, {'format': PREFERENCE, 'enabled': enabled})


class Stage:
    """One newly created private directory; cleanup never discovers foreign files."""
    def __init__(self, launcher):
        parent = no_links(Path(launcher) / 'update-staging')
        private_directory(parent)
        self.path = parent / secrets.token_hex(24)
        self.path.mkdir(mode=0o700)
        private_directory(self.path)
        self.names = set()

    def target(self, name):
        require(type(name) is str and name and Path(name).name == name and
                not any(c in name for c in '/\\:') and not name.endswith(('.', ' ')), 'Invalid staging name')
        path = no_links(self.path / name)
        self.names.add(name)
        return path

    def write(self, name, raw):
        with self.target(name).open('xb') as stream:
            stream.write(raw); stream.flush(); os.fsync(stream.fileno())

    def cleanup(self):
        no_links(self.path)
        for name in self.names:
            no_links(self.path / name).unlink(missing_ok=True)
        self.path.rmdir()  # Unknown files cause refusal, never recursive deletion.


def recover(launcher):
    """Read a result, remove only listed completed handoff files, never resume MSI."""
    launcher = no_links(launcher)
    pending = launcher / 'update-pending.json'
    result = launcher / 'update-result.json'
    if not pending.exists():
        return None
    value = read_small(pending)
    shape(value, 'format nonce stage version files', 'Invalid pending update')
    require(value['format'] == 'picross-update-pending-v1' and
            value['stage'] == value['nonce'] and len(value['stage']) == 48 and
            all(c in '0123456789abcdef' for c in value['stage']), 'Invalid pending stage')
    stage = no_links(launcher / 'update-staging' / value['stage'])
    msi = release(version=value['version'])['filename']
    expected = {msi, msi + '.sha256', 'START.txt', 'delivery.json', 'inputs.json',
                'manifest.json', 'manifest.sig.json', 'UpdateHelper.exe', 'active'}
    require(type(value['files']) is list and len(value['files']) <= 12 and
            all(type(n) is str and n and Path(n).name == n and not any(c in n for c in '/\\:') and
                not n.endswith(('.', ' ')) for n in value['files']), 'Invalid pending inventory')
    require(set(value['files']) == expected and len(value['files']) == len(expected), 'Unowned pending inventory')
    if not result.exists():
        return 'Updateausgang unbestätigt. Assistent regulär starten; vor erneutem Versuch Installation prüfen.'
    report = read_small(result)
    shape(report, 'format nonce status version', 'Invalid update result')
    require(report['format'] == 'picross-update-result-v1' and report['nonce'] == value['nonce'] and report['version'] == value['version'] and
            report['status'] in ('installed', 'failed', 'reboot', 'unconfirmed', 'cancelled'), 'Unbound update result')
    # FileShare.None held by the helper blocks opening while it is still alive.
    if stage.exists():
        with no_links(stage / 'active').open('a+b'):
            for name in value['files']:
                if name != 'active':
                    no_links(stage / name).unlink(missing_ok=True)
        (stage / 'active').unlink(missing_ok=True)
        stage.rmdir()
    pending.unlink()
    messages = {'installed': 'Installation bestätigt; Assistent neu gestartet.',
                'failed': 'Update fehlgeschlagen. Installation prüfen und bei Bedarf manuell erneut installieren.',
                'reboot': 'Windows meldet erforderlichen Neustart. Update noch nicht als erfolgreich bestätigt.',
                'unconfirmed': 'Update oder Wiederanlauf unbestätigt. Installation prüfen und manuell starten.',
                'cancelled': 'Update abgebrochen; kein automatischer Wiederholungsversuch.'}
    return messages[report['status']]
