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
from .update_verifier import production_trust

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
    pins = '\n'.join((PACKAGE / name).read_text() for name in ('requirements-windows.txt', 'requirements-update.txt'))
    for line in pins.splitlines():
        if not line or line.startswith('#'):
            continue
        if line == '-r requirements-update.txt':
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
    compiler = Path(os.environ['SystemRoot']) / 'Microsoft.NET/Framework64/v4.0.30319/csc.exe'
    helper = work / 'UpdateHelper.exe'
    subprocess.run([str(compiler), '/nologo', '/target:exe', '/platform:x64',
                    '/reference:System.Web.Extensions.dll', '/out:' + str(helper),
                    str(PACKAGE / 'packaging/UpdateHelper.cs')], check=True)
    env = os.environ.copy()
    env.update(PYINSTALLER_CONFIG_DIR=str(work / 'cache'), TEMP=str(work), TMP=str(work), PYTHONHASHSEED='0')
    resources = {f'ui/{name}': sha(PACKAGE / 'ui' / name) for name in ('index.html', 'app.js', 'workflow.js', 'style.css')}
    resources['assets/launcher.ico'] = sha(PACKAGE / 'assets/launcher.ico')
    resources['UpdateHelper.exe'] = sha(helper)
    production_trust()  # Fail the build on malformed public roots, even if unprovisioned.
    for name in ('release.json', 'update-trust.json'):
        resources[name] = sha(PACKAGE / name)
    from cryptography.hazmat.backends.openssl.backend import backend
    runtime_versions['cryptography OpenSSL'] = backend.openssl_version_text()
    if runtime_versions['cryptography OpenSSL'] != 'OpenSSL 4.0.3 29 Sep 2026':
        raise RuntimeError('Kryptografie-Runtime passt nicht zum geprüften Wheel-/Lizenzinventar.')
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
                    '--hidden-import', 'tools.production_workspace.update_verifier',
                    '--hidden-import', 'cryptography.hazmat.primitives.asymmetric.ed25519',
                    '--hidden-import', '_cffi_backend',
                    '--add-data', str(PACKAGE / 'ui') + ':tools/production_workspace/ui',
                    '--add-data', str(PACKAGE / 'assets/launcher.ico') + ':tools/production_workspace/assets',
                    '--add-data', str(manifest_file) + ':tools/production_workspace',
                    '--add-data', str(helper) + ':tools/production_workspace',
                    '--add-data', str(PACKAGE / 'release.json') + ':tools/production_workspace',
                    '--add-data', str(PACKAGE / 'update-trust.json') + ':tools/production_workspace',
                    str(PACKAGE / 'desktop_entry.py')], check=True, cwd=ROOT, env=env)
    audit = audit_analysis(ROOT, work / 'pyinstaller/Picross-Start/Analysis-00.toc', inputs,
                           [manifest_file, file_version, helper])
    (destination / 'inputs.json').write_text(json.dumps(inputs, indent=2) + '\n', encoding='utf-8')
    app = destination / 'dist/Picross-Start'
    verify_update_payload(app, work / 'pyinstaller/Picross-Start/PYZ-00.pyz', audit)
    (destination / 'input-audit.json').write_text(json.dumps(audit, indent=2) + '\n', encoding='utf-8')
    shutil.copyfile(PACKAGE / 'START-WINDOWS.txt', app / 'START.txt')
    shutil.copyfile(manifest_file, app / 'components.json')
    licenses = app / 'LICENSES'; licenses.mkdir()
    shutil.copyfile(Path(sys.base_prefix) / 'LICENSE.txt', licenses / 'Python.txt')
    for notice in (PACKAGE / 'licenses').glob('*.txt'):
        shutil.copyfile(notice, licenses / notice.name)
    for name in ('Pillow', 'PyInstaller', 'cryptography', 'cffi', 'pycparser'):
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


def verify_update_payload(app, pyz, audit):
    """Check real frozen code and native crypto extensions, not just source pins."""
    from PyInstaller.archive.readers import ZlibArchiveReader
    names = set(ZlibArchiveReader(str(pyz)).toc)
    required = {'tools.production_workspace.update_verifier', 'tools.production_workspace.release_manifest',
                'tools.production_workspace.update_client', 'tools.production_workspace.update_storage',
                'tools.production_workspace.update_windows', 'tools.production_workspace.app_updates',
                'tools.production_workspace.release', 'cryptography.hazmat.primitives.asymmetric.ed25519'}
    if not required <= names or any('tools.production_workspace.' + name in names for name in ('update_diagnostic', 'helper_diagnostic')):
        raise RuntimeError('Frozen Verifier-/Kryptografieinventar fehlt oder enthält den Testadapter.')
    observed = set(audit['repository_inputs'])
    sources = {name.replace('.', '/') + '.py' for name in required if name.startswith('tools.')}
    sources |= {'tools/production_workspace/release.json', 'tools/production_workspace/update-trust.json'}
    if not sources <= observed:
        raise RuntimeError('Verifier-/Trustquellen fehlen im tatsächlichen PyInstaller-Inputabgleich.')
    files = [p.relative_to(app).as_posix() for p in app.rglob('*.pyd')]
    if not any(p.endswith('cryptography/hazmat/bindings/_rust.pyd') for p in files) or not any(
            Path(p).name.startswith('_cffi_backend.') for p in files):
        raise RuntimeError('Native Kryptografiemodule fehlen im Frozen-Payload.')
    audit['update_modules'] = sorted(required)
    audit['crypto_extensions'] = sorted(p for p in files if 'cryptography/' in p or '_cffi_backend.' in p)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--version', help='Explicitly planned 0.1.x publication version; source stays unchanged')
    args = parser.parse_args()
    build(args.output, version=args.version)
