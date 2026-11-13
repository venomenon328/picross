"""Clean Windows x64 onedir/windowed build; never builds from a data checkout."""
import argparse
import hashlib
import importlib.metadata as metadata
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import zipfile
import ssl
import zlib
import pyexpat
import decimal
from .release import release, version_tuple, check_history
from .payload import fingerprint, audit_analysis

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / 'tools/production_workspace'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(destination, *, version=None):
    if sys.platform != 'win32' or platform.machine().lower() not in ('amd64', 'x86_64') or platform.python_version() != '3.13.14':
        raise RuntimeError('Build benötigt CPython 3.13.14 Windows x64.')
    import tkinter
    versions = {}
    runtime_versions = {'Tcl/Tk': tkinter.Tcl().eval('info patchlevel'), 'OpenSSL': ssl.OPENSSL_VERSION,
                        'Expat': pyexpat.EXPAT_VERSION, 'zlib': zlib.ZLIB_RUNTIME_VERSION,
                        'mpdecimal': decimal.__libmpdec_version__, 'bzip2': '1.0.8', 'liblzma': '5.2.5', 'libffi': '3.4.4'}
    if (runtime_versions['Tcl/Tk'] != '8.6.15' or runtime_versions['OpenSSL'] != 'OpenSSL 3.0.21 9 Jun 2026' or
            runtime_versions['Expat'] != 'expat_2.8.1' or runtime_versions['zlib'] != '1.3.1' or
            runtime_versions['mpdecimal'] != '4.0.0'):
        raise RuntimeError('Runtime-Komponenten passen nicht zum versionierten Lizenzinventar.')
    for line in (PACKAGE / 'requirements-windows.txt').read_text().splitlines():
        if not line or line.startswith('#'):
            continue
        name, pinned_version = line.split('==')
        if metadata.version(name) != pinned_version:
            raise RuntimeError('Falsche Buildabhängigkeit: ' + name)
        versions[name] = pinned_version
    if metadata.version('pip') != '26.1.2':
        raise RuntimeError('Build benötigt pip 26.1.2.')
    def git(*args):
        return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True).strip()
    if git('status', '--porcelain'):
        raise RuntimeError('Nur aus sauberem, gesichertem Quellstand bauen.')
    commit = git('rev-parse', 'HEAD')
    product = release(version=version)
    check_history(ROOT, product)
    inputs = fingerprint(ROOT)
    destination = destination.resolve()
    if destination.exists() or destination.is_relative_to(ROOT):
        raise RuntimeError('Neuen eigenen Buildordner außerhalb des Checkouts wählen.')
    destination.mkdir(parents=True)
    work = destination / 'work'; work.mkdir()
    env = os.environ.copy()
    env.update(PYINSTALLER_CONFIG_DIR=str(work / 'cache'), TEMP=str(work), TMP=str(work), PYTHONHASHSEED='0')
    resources = {f'ui/{name}': sha(PACKAGE / 'ui' / name) for name in ('index.html', 'app.js', 'workflow.js', 'style.css')}
    resources['assets/launcher.ico'] = sha(PACKAGE / 'assets/launcher.ico')
    manifest = {'format': 'picross-windows-app-v1', 'version': product['version'], 'commit': commit,
                'payload_fingerprint': inputs['sha256'],
                'upgrade_code': product['upgrade_code'], 'product_code': product['product_code'],
                'architecture': 'windows-x64', 'python': platform.python_version(), 'components': versions,
                'runtime_components': runtime_versions, 'resources': resources, 'signed': False}
    manifest_file = work / 'build.json'
    manifest_file.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    file_version = work / 'version.txt'
    numbers = version_tuple(product['version']) + (0,)
    file_version.write_text(
        'VSVersionInfo(ffi=FixedFileInfo(filevers=' + repr(numbers) + ', prodvers=' + repr(numbers) +
        ', mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0, date=(0,0)), '
        'kids=[StringFileInfo([StringTable("040704B0", [StringStruct("ProductName", "Picross-Produktionsassistent"), '
        'StringStruct("ProductVersion", ' + repr(product['version']) + '), StringStruct("FileVersion", ' +
        repr(product['version']) + '), StringStruct("Comments", ' + repr(commit) + ')])]), '
        'VarFileInfo([VarStruct("Translation", [1031, 1200])])])', encoding='utf-8')
    subprocess.run([sys.executable, '-m', 'PyInstaller', '--clean', '--noconfirm', '--onedir', '--windowed',
                    '--noupx', '--name', 'Picross-Start', '--icon', str(PACKAGE / 'assets/launcher.ico'),
                    '--version-file', str(file_version),
                    '--distpath', str(destination / 'dist'),
                    '--workpath', str(work / 'pyinstaller'), '--specpath', str(work), '--paths', str(ROOT),
                    '--collect-submodules', 'tools.puzzle_production',
                    '--add-data', str(PACKAGE / 'ui') + ':tools/production_workspace/ui',
                    '--add-data', str(PACKAGE / 'assets/launcher.ico') + ':tools/production_workspace/assets',
                    '--add-data', str(manifest_file) + ':tools/production_workspace',
                    str(PACKAGE / 'desktop_entry.py')], check=True, cwd=ROOT, env=env)
    audit = audit_analysis(ROOT, work / 'pyinstaller/Picross-Start/Analysis-00.toc', inputs,
                           [manifest_file, file_version])
    (destination / 'inputs.json').write_text(json.dumps(inputs, indent=2) + '\n', encoding='utf-8')
    (destination / 'input-audit.json').write_text(json.dumps(audit, indent=2) + '\n', encoding='utf-8')
    app = destination / 'dist/Picross-Start'
    shutil.copyfile(PACKAGE / 'START-WINDOWS.txt', app / 'START.txt')
    shutil.copyfile(manifest_file, app / 'components.json')
    licenses = app / 'LICENSES'; licenses.mkdir()
    shutil.copyfile(Path(sys.base_prefix) / 'LICENSE.txt', licenses / 'Python.txt')
    for notice in (PACKAGE / 'licenses').glob('*.txt'):
        shutil.copyfile(notice, licenses / notice.name)
    for name in ('Pillow', 'PyInstaller'):
        dist = metadata.distribution(name)
        copied = False
        for file in dist.files:
            if '.dist-info/licenses/' in str(file).replace('\\', '/'):
                target = licenses / name / Path(str(file).split('licenses/', 1)[-1])
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(dist.locate_file(file), target)
                copied = True
        if not copied:
            raise RuntimeError('Lizenzinventar fehlt: ' + name)
    for name in ('tcl8.6', 'tk8.6'):
        candidates = list((Path(sys.base_prefix) / 'tcl' / name).glob('*license*'))
        if not candidates:
            candidates = list((Path(sys.base_prefix) / 'tcl' / name).glob('*License*'))
        if not candidates:
            if name == 'tcl8.6':
                if tkinter.Tcl().eval('info patchlevel') != '8.6.15':
                    raise RuntimeError('Tcl-Lizenzbindung prüfen; erwartet 8.6.15.')
                candidates = [PACKAGE / 'licenses/Tcl-8.6.15.txt']
            else:
                raise RuntimeError('Tcl/Tk-Lizenz fehlt: ' + name)
        for file in candidates:
            shutil.copyfile(file, licenses / (name + '-' + file.name + '.txt'))
    files = [{'file': f.relative_to(app).as_posix(), 'bytes': f.stat().st_size, 'sha256': sha(f)}
             for f in sorted(app.rglob('*')) if f.is_file()]
    (app / 'inventory.json').write_text(json.dumps({'commit': commit, 'files': files}, indent=2) + '\n', encoding='utf-8')
    archive = destination / 'Picross-Start-windows-x64.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as output:
        for file in sorted(app.rglob('*')):
            if file.is_file():
                output.write(file, 'Picross-Start/' + file.relative_to(app).as_posix())
    report = {**manifest, 'zip_bytes': archive.stat().st_size, 'zip_sha256': sha(archive),
              'exe_bytes': (app / 'Picross-Start.exe').stat().st_size, 'exe_sha256': sha(app / 'Picross-Start.exe')}
    (destination / 'delivery.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--version', help='Explicitly planned 0.1.x publication version; source stays unchanged')
    args = parser.parse_args()
    build(args.output, version=args.version)
