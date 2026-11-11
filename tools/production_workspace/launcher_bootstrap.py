import base64
import hashlib
from io import BytesIO
import os
from pathlib import Path
import shutil
import subprocess
import sys
import venv
import tempfile
import zipfile

# __PICROSS_PROGRAM_PAYLOAD__


def usable_python(executable):
    if not executable.is_file():
        return False
    try:
        result = subprocess.run(
            [str(executable), '-c',
             'import sys; sys.exit(0 if sys.version_info >= (3,11) and sys.prefix != sys.base_prefix else 1)'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15,
        )
        return result.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def environment_python(environment):
    return environment / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')


def ensure_environment(requested):
    requested.mkdir(parents=True, exist_ok=True)
    # Resolve from INSIDE Python: Store Python may virtualize LOCALAPPDATA and
    # profile folders may also be junctions. cmd.exe does not see that same view.
    environment = Path(os.path.realpath(requested))
    executable = environment_python(environment)
    if executable.is_symlink():
        raise RuntimeError('Die Pythonumgebung verwendet einen externen Python-Link. Bitte einen eigenen Umgebungsordner verwenden.')
    if not usable_python(executable):
        print('Eigene Pythonumgebung wird eingerichtet oder vervollstaendigt ...', flush=True)
        venv.EnvBuilder(with_pip=True, symlinks=False).create(str(environment))
        executable = environment_python(environment)
    # Resolve the executable as well, as CPython venv does for Windows redirects.
    if os.name == 'nt':
        executable = Path(os.path.realpath(executable))
    if not usable_python(executable):
        raise RuntimeError('Pythonumgebung kann nicht gestartet werden: ' + str(executable))
    pip = subprocess.run([str(executable), '-m', 'pip', '--version'],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15)
    if pip.returncode:
        subprocess.run([str(executable), '-m', 'ensurepip', '--upgrade'], check=True)
    return executable


def is_repository(path):
    return ((path / '.git').exists()
            and (path / 'tools/production_workspace/__main__.py').is_file()
            and (path / 'tools/puzzle_production/requirements-image.txt').is_file())


def find_repository():
    for candidate in (Path(os.environ['PW_START_FILE']).parent, Path.cwd()):
        if is_repository(candidate):
            return candidate.resolve()
    print('Bitte den vollstaendigen Pfad zum aktualisierten Picross-Ordner angeben.')
    value = input('Picross-Ordner: ').strip().strip('"')
    if not value:
        raise RuntimeError('Kein Picross-Ordner angegeben.')
    candidate = Path(value)
    if not is_repository(candidate):
        raise RuntimeError('Der angegebene Ordner ist kein aktualisierter Picross-Checkout mit PW-A.')
    return candidate.resolve()


APPLICATION_ENTRY = r'''
import argparse
import os
from pathlib import Path
import sys
import tools.production_workspace as package
package.__path__[:] = [sys.argv.pop(1)]
from tools.production_workspace.__main__ import main
arguments = list(sys.argv[1:])
options = argparse.ArgumentParser(add_help=False)
options.add_argument('--state', type=Path)
options.add_argument('--repository')
known, _ = options.parse_known_args(arguments)
state = known.state
if state is None:
    requested = Path(os.environ['LOCALAPPDATA']) / 'PicrossProductionWorkspace'
    requested.mkdir(parents=True, exist_ok=True)
    state = Path(os.path.realpath(requested))
    arguments.extend(['--state', str(state)])
if known.repository is None and not (state / 'config.json').is_file():
    arguments.extend(['--repository', str(Path.cwd().resolve())])
raise SystemExit(main(arguments))
'''


def unpack_program(destination):
    # This archive is generated from the trusted program files and
    # embedded in this single launcher. Production branches never supply code.
    raw = base64.b64decode(PROGRAM_ARCHIVE, validate=True)
    if hashlib.sha256(raw).hexdigest() != PROGRAM_SHA256:
        raise RuntimeError('Die Startdatei ist unvollstaendig oder beschaedigt. Bitte erneut herunterladen.')
    with zipfile.ZipFile(BytesIO(raw)) as archive:
        if archive.namelist() != PROGRAM_FILES:
            raise RuntimeError('Unerwarteter Inhalt der Startdatei.')
        for name in PROGRAM_FILES:
            path = destination / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(archive.read(name))
    return destination


def main():
    print('Picross - lokale Produktionsansicht (PW-A2)\n', flush=True)
    if sys.version_info < (3, 11):
        raise RuntimeError('Python 3.11 oder neuer ist erforderlich.')
    if not shutil.which('git'):
        raise RuntimeError('Git fehlt oder ist nicht im PATH. Bitte aktuelles Git fuer Windows installieren.')
    local = os.environ.get('LOCALAPPDATA')
    if not local:
        raise RuntimeError('LOCALAPPDATA fehlt. Bitte in einer normalen Windows-Sitzung starten.')
    repository = find_repository()
    executable = ensure_environment(Path(local) / 'Picross-PW-Python')
    installed = subprocess.run([str(executable), '-c',
        'import PIL,sys; sys.exit(0 if PIL.__version__ == "12.3.0" else 1)'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15)
    if installed.returncode:
        print('Bildleser wird in der eigenen Pythonumgebung installiert ...', flush=True)
        subprocess.run([str(executable), '-m', 'pip', 'install', '--disable-pip-version-check',
                        '--only-binary=:all:', '-r', str(repository / 'tools/puzzle_production/requirements-image.txt')],
                       check=True, cwd=str(repository))
    print('\nProduktionsansicht wird gestartet. Beenden mit Strg+C.', flush=True)
    print('Der Browser oeffnet sich sofort; Git wird dort im Hintergrund geladen.\n', flush=True)
    with tempfile.TemporaryDirectory(prefix='Picross-PW-program-') as directory:
        program = unpack_program(Path(os.path.realpath(directory)))
        process = subprocess.Popen([str(executable), '-c', APPLICATION_ENTRY, str(program), *sys.argv[1:]],
                                   cwd=str(repository))
        try:
            return process.wait()
        except KeyboardInterrupt:
            try:
                return process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.terminate()
                return process.wait()



if __name__ == '__main__':
    try:
        code = main()
    except KeyboardInterrupt:
        code = 130
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print('\nStart nicht moeglich: ' + str(error), file=sys.stderr)
        code = 2
    raise SystemExit(code)
