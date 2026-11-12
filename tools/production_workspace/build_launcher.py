"""Build the single-file Windows launcher from this exact trusted reader source."""
import base64
import hashlib
from io import BytesIO
from pathlib import Path
import zipfile

ROOT = Path(__file__).parent
FILES = ['__init__.py', '__main__.py', 'desktop.py', 'instance.py', 'runtime.py', 'processes.py', 'install_interlock.py',
         'presentation.py', 'repository.py', 'server.py', 'sources.py', 'current_view.py', 'motifs.py',
         'ui/index.html', 'ui/workflow.js', 'ui/app.js', 'ui/style.css', 'assets/launcher.ico']


def build():
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in FILES:
            info = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            info.create_system = 3  # Stable ZIP bytes on Windows and Linux producers.
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, (ROOT / name).read_bytes())
    raw = buffer.getvalue()
    payload = ('PROGRAM_SHA256 = ' + repr(hashlib.sha256(raw).hexdigest()) + '\n' +
               'PROGRAM_FILES = ' + repr(FILES) + '\n' +
               'PROGRAM_ARCHIVE = ' + repr(base64.b64encode(raw).decode('ascii')))
    bootstrap = (ROOT / 'launcher_bootstrap.py').read_text(encoding='utf-8')
    return ((ROOT / 'launcher_header.cmd').read_text(encoding='utf-8') +
            bootstrap.replace('# __PICROSS_PROGRAM_PAYLOAD__', payload))


if __name__ == '__main__':
    (ROOT / 'Picross-Start.cmd').write_text(build(), encoding='utf-8', newline='\n')
