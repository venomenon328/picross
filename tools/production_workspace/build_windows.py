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
from .release import release, version_tuple
from .payload import (PRODUCTION, PW_IMAGE_SOURCES, PW_WRITER_MODULES, audit_analysis, bound_input, fingerprint, git as git_bytes,
                      pw_method_files, verify_pw_reader_resources)
from .update_verifier import production_trust

from tools.app_products import PG, PW, PE

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / 'tools/production_workspace'

# Broad production-module collection must not freeze ZA-1's synthetic helpers.
# Those helpers import tests.puzzle_production, which is not app source.
FROZEN_EXCLUDES = ('tools.puzzle_production.za1_fixtures', 'tests')
# current_authoring's producer-only build/complete functions are discovered by
# PyInstaller even when the installed readers never call them. Keep the Git
# worktree/remote publication chain outside both desktop applications.
PRODUCTION_WRITER_EXCLUDES = (
    'tools.production_git_workspace', 'tools.production_worktree_publish',
    'tools.publish_git', 'tools.work_publish', 'tools.production_remote',
    'tools.production_remote_pr', 'tools.production_remote_steps',
)


def frozen_excludes(app):
    if app == PW:
        return FROZEN_EXCLUDES + ('work_ref_check', 'tools.work_ref_check') + tuple(
            name for name in PRODUCTION_WRITER_EXCLUDES if name not in PW_WRITER_MODULES)
    return FROZEN_EXCLUDES + (PRODUCTION_WRITER_EXCLUDES if app == PE else ())


def verify_no_production_writers(names, app):
    if app in (PW, PE):
        leaked = sorted(set(names) & set(frozen_excludes(app)))
        if leaked:
            raise RuntimeError('Frozen-Payload enthält Produktionswriter: ' + ', '.join(leaked))

# current_authoring's PW-only projection code imports motifs for phase labels.
# PE never runs that projection and must not freeze the PW job/history modules.
PE_WORKSPACE_EXCLUDES = ('sources', 'current_view', 'presentation', 'projector', 'motifs')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(destination, *, version=None, app=PW):
    package = app.source
    icon = package / app.icon_resource
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
    product = release(version=version, app=app)
    inputs = fingerprint(ROOT, app=app)
    destination = destination.resolve()
    if destination.exists() or destination.is_relative_to(ROOT):
        raise RuntimeError('Neuen eigenen Buildordner außerhalb des Checkouts wählen.')
    destination.mkdir(parents=True)
    work = destination / 'work'; work.mkdir()
    generated = []
    game = {}
    if app == PG:
        from tools.game_app.build import export_player
        game = export_player(destination, work, inputs)
    helper = None
    windows = Path(os.environ['SystemRoot'])
    if app in (PW, PE, PG):
        compiler = windows / 'Microsoft.NET/Framework64/v4.0.30319/csc.exe'
        helper = work / 'UpdateHelper.exe'
        subprocess.run([str(compiler), '/nologo', '/target:exe', '/platform:x64',
                        '/reference:System.Web.Extensions.dll', '/out:' + str(helper),
                        *(['/define:' + app.key.upper()] if app in (PE, PG) else []),
                        str(PACKAGE / 'packaging/UpdateHelper.cs')], check=True)
        generated.append(helper)
    env = os.environ.copy()
    # PyInstaller also resolves DLL imports through PATH. Keep unrelated
    # toolchains out of the payload while retaining Windows system DLL lookup.
    env['PATH'] = os.pathsep.join((str(windows / 'System32'), str(windows)))
    env.update(PYINSTALLER_CONFIG_DIR=str(work / 'cache'), TEMP=str(work), TMP=str(work), PYTHONHASHSEED='0')
    ui = {PW: ('index.html', 'app.js', 'workflow.js', 'style.css'),
          PE: ('index.html', 'app.js', 'style.css'), PG: ()}[app]
    resources = {f'ui/{name}': sha(package / 'ui' / name) for name in ui}
    resources[app.icon_resource] = sha(icon)
    if helper:
        resources['UpdateHelper.exe'] = sha(helper)
    production_trust(app=app)
    for name in ('release.json', 'update-trust.json'):
        resources[name] = sha(package / name)
    extra_args = []
    if app in (PW, PE):
        extra_args += ["--collect-all", "resvg_py"]
    if app == PW:
        reader_sources = PW_IMAGE_SOURCES | pw_method_files(lambda name: git_bytes(ROOT, 'show', f'{commit}:{name}'))
        expected = {row['file']: row for row in inputs['files']}
        for name in sorted(reader_sources):
            resources[name] = bound_input(ROOT / name, expected[name])
            extra_args += ['--add-data', str(ROOT / name) + ':' + PRODUCTION.rstrip('/')]
    if app == PE:
        from .payload import PE_EXCLUDED
        source_data = work / 'puzzle_production'; source_data.mkdir()
        expected = {row['file']: row for row in inputs['files']}
        # Method identities read exact source/JSON bytes, not PYZ bytecode.
        for file in sorted((ROOT / PRODUCTION).iterdir()):
            if file.is_file() and file.suffix in ('.py', '.json', '.md') and file.stem not in PE_EXCLUDED:
                relative = file.relative_to(ROOT).as_posix()
                if relative not in expected or sha(file) != expected[relative]['sha256']:
                    raise RuntimeError('Unbound method source: ' + relative)
                target = source_data / file.name
                shutil.copyfile(file, target); generated.append(target)
                resources[relative] = sha(target)
        extra_args += ['--add-data', str(source_data) + ':tools/puzzle_production',
                       '--hidden-import', 'tools.puzzle_editor.worker',
                       '--hidden-import', 'tkinter.filedialog', '--hidden-import', 'tkinter.messagebox']
        for relative in ('game/book/paper.png', 'game/book/paper.json', 'game/art/drawing/margins'):
            target = str(Path(relative).parent) if Path(relative).suffix else relative
            extra_args += ['--add-data', str(ROOT / relative) + ':' + target]
        for name in PE_EXCLUDED:
            extra_args += ['--exclude-module', 'tools.puzzle_production.' + name]
        # PE uses current targeted readers, not PW's Git/presentation endpoints.
        for name in PE_WORKSPACE_EXCLUDES:
            extra_args += ['--exclude-module', 'tools.production_workspace.' + name]
        extra_args += ['--exclude-module', 'tools.puzzle_editor.diagnostic',
                       '--exclude-module', 'tools.puzzle_editor.frozen_diagnostic']
    if app == PG:
        extra_args += [argument for name in ('PIL', 'tools.puzzle_production', 'tools.puzzle_editor')
                       for argument in ('--exclude-module', name)]
    from cryptography.hazmat.backends.openssl.backend import backend
    runtime_versions['cryptography OpenSSL'] = backend.openssl_version_text()
    if runtime_versions['cryptography OpenSSL'] != 'OpenSSL 4.0.3 29 Sep 2026':
        raise RuntimeError('Kryptografie-Runtime passt nicht zum geprüften Wheel-/Lizenzinventar.')
    manifest = {'format': 'picross-pg-build-v2' if app == PG else 'picross-windows-app-v1',
                'version': product['version'], 'commit': commit,
                'payload_fingerprint': inputs['sha256'],
                'upgrade_code': product['upgrade_code'], 'product_code': product['product_code'],
                'architecture': 'windows-x64', 'python': platform.python_version(), 'components': versions,
                'runtime_components': runtime_versions, 'resources': resources, 'signed': False, **game}
    manifest_file = work / 'build.json'
    manifest_file.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    file_version = work / 'version.txt'
    numbers = version_tuple(product['version']) + (0,)
    file_version.write_text(
        'VSVersionInfo(ffi=FixedFileInfo(filevers=' + repr(numbers) + ', prodvers=' + repr(numbers) +
        ', mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0, date=(0,0)), '
        'kids=[StringFileInfo([StringTable("040704B0", [StringStruct("ProductName", ' + repr(app.title) + '), '
        'StringStruct("ProductVersion", ' + repr(product['version']) + '), StringStruct("FileVersion", ' +
        repr(product['version']) + '), StringStruct("Comments", ' + repr(commit) + ')])]), '
        'VarFileInfo([VarStruct("Translation", [1031, 1200])])])', encoding='utf-8')
    subprocess.run([sys.executable, '-m', 'PyInstaller', '--clean', '--noconfirm', '--onedir', '--windowed',
                    '--noupx', '--name', app.executable, '--icon', str(icon),
                    '--version-file', str(file_version),
                    '--distpath', str(destination / 'dist'),
                    '--workpath', str(work / 'pyinstaller'), '--specpath', str(work), '--paths', str(ROOT),
                    *(['--collect-submodules', 'tools.puzzle_production'] if app == PW else []),
                    *(arg for name in frozen_excludes(app) for arg in ('--exclude-module', name)),
                    '--hidden-import', 'tools.production_workspace.update_verifier',
                    '--hidden-import', 'cryptography.hazmat.primitives.asymmetric.ed25519',
                    '--hidden-import', '_cffi_backend',
                    *(['--add-data', str(package / 'ui') + ':' + app.package + '/ui'] if ui else []),
                    '--add-data', str(icon) + ':' + app.package + '/assets',
                    '--add-data', str(manifest_file) + ':' + app.package,
                    *(['--add-data', str(helper) + ':' + app.package] if helper else []),
                    '--add-data', str(package / 'release.json') + ':' + app.package,
                    '--add-data', str(package / 'update-trust.json') + ':' + app.package,
                    *extra_args, str(package / 'desktop_entry.py')], check=True, cwd=ROOT, env=env)
    audit = audit_analysis(ROOT, work / 'pyinstaller' / app.executable / 'Analysis-00.toc', inputs,
                           [manifest_file, file_version, *generated], app=app)
    (destination / 'inputs.json').write_text(json.dumps(inputs, indent=2) + '\n', encoding='utf-8')
    image = destination / 'dist' / app.executable
    verify_update_payload(image, work / 'pyinstaller' / app.executable / 'PYZ-00.pyz', audit, app=app)
    if app == PW:
        if not reader_sources <= set(audit['repository_inputs']):
            raise RuntimeError('PW reader sources missing in actual PyInstaller Analysis')
        files = {PRODUCTION + member.name: member
                 for member in (image / '_internal' / PRODUCTION).iterdir() if member.is_file()}
        audit.update(verify_pw_reader_resources(inputs, resources, files))
    audit_name = 'frozen-audit.json' if app == PG else 'input-audit.json'
    (destination / audit_name).write_text(json.dumps(audit, indent=2) + '\n', encoding='utf-8')
    instructions = {PW: PACKAGE / 'START-WINDOWS.txt', PE: package / 'README.md', PG: package / 'START.txt'}
    shutil.copyfile(instructions[app], image / 'START.txt')
    shutil.copyfile(manifest_file, image / 'components.json')
    licenses = image / ('licenses' if app == PG else 'LICENSES')
    licenses.mkdir()
    shutil.copyfile(Path(sys.base_prefix) / 'LICENSE.txt', licenses / 'Python.txt')
    for notice in (PACKAGE / 'licenses').glob('*.txt'):
        shutil.copyfile(notice, licenses / notice.name)
    for name in ('PyInstaller', 'cryptography', 'cffi', 'pycparser') + (() if app == PG else ('Pillow', 'resvg_py')):
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
    if app == PG:
        from tools.game_app.build import finish_image
        finish_image(destination, work, image, manifest)
        return
    files = [{'file': f.relative_to(image).as_posix(), 'bytes': f.stat().st_size, 'sha256': sha(f)}
             for f in sorted(image.rglob('*')) if f.is_file()]
    (image / 'inventory.json').write_text(json.dumps({'commit': commit, 'files': files}, indent=2) + '\n', encoding='utf-8')
    archive = destination / (app.executable + '-windows-x64.zip')
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as output:
        for file in sorted(image.rglob('*')):
            if file.is_file():
                output.write(file, app.executable + '/' + file.relative_to(image).as_posix())
    report = {**manifest, 'zip_bytes': archive.stat().st_size, 'zip_sha256': sha(archive),
              'exe_bytes': (image / (app.executable + '.exe')).stat().st_size, 'exe_sha256': sha(image / (app.executable + '.exe'))}
    (destination / 'delivery.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))


def verify_update_payload(image, pyz, audit, *, app=PW):
    """Check real frozen code and native crypto extensions, not just source pins."""
    from PyInstaller.archive.readers import ZlibArchiveReader
    names = set(ZlibArchiveReader(str(pyz)).toc)
    verify_no_production_writers(names, app)
    required = {'tools.production_workspace.update_verifier', 'tools.production_workspace.release_manifest',
                'tools.production_workspace.release', 'tools.app_products',
                'cryptography.hazmat.primitives.asymmetric.ed25519'}
    if app in (PW, PE, PG):
        required |= {'tools.production_workspace.update_client', 'tools.production_workspace.update_storage',
                     'tools.production_workspace.update_windows', 'tools.production_workspace.app_updates'}
    if app == PW:
        required |= PW_WRITER_MODULES | {'tools.production_workspace.inbox', 'tools.production_workspace.inbox_writer',
                                         'tools.production_workspace.inbox_files', 'tools.production_workspace.inbox_contract'}
    if app == PE:
        required |= {'tools.puzzle_editor.app_updates', 'tools.puzzle_editor.server', 'tools.puzzle_editor.worker', 'tools.puzzle_editor.desktop',
                     'tools.puzzle_production.editor_change', 'tools.puzzle_production.current_content',
                     'tools.puzzle_production.editor_image_input'}
        if any(name.startswith('tools.production_workspace.') and name.rsplit('.', 1)[-1] not in
               {'release', 'payload', 'release_manifest', 'update_verifier', 'install_interlock',
                'app_updates', 'update_client', 'update_storage', 'update_windows', 'instance', 'processes'} for name in names):
            raise RuntimeError('PE includes unrelated PW application code')
    if app == PG:
        required |= {'tools.game_app.gate', 'tools.game_app.restart', 'tools.game_app.player',
                     'tools.production_workspace.install_interlock'}
        supported = required | {'tools', 'tools.game_app', 'tools.production_workspace',
                                'tools.production_workspace.instance', 'tools.production_workspace.payload',
                                'tools.production_workspace.processes'}
        if any(name.startswith('tools.') and name not in supported for name in names):
            raise RuntimeError('PG includes unrelated tooling: ' + repr(sorted(
                name for name in names if name.startswith('tools.') and name not in supported)))
    if not required <= names or any('tools.production_workspace.' + name in names for name in ('update_diagnostic', 'helper_diagnostic')):
        raise RuntimeError('Frozen Verifier-/Kryptografieinventar fehlt oder enthält den Testadapter.')
    if 'tools.puzzle_production.za1_fixtures' in names or any(
            name == 'tests' or name.startswith('tests.') for name in names):
        raise RuntimeError('Frozen-Payload enthält synthetische Testmodule.')
    observed = set(audit['repository_inputs'])
    sources = {name.replace('.', '/') + '.py' for name in required if name.startswith('tools.')}
    sources |= {app.package + '/release.json', app.package + '/update-trust.json'}
    if not sources <= observed:
        raise RuntimeError('Verifier-/Trustquellen fehlen im tatsächlichen PyInstaller-Inputabgleich.')
    if app.package + '/' + app.icon_resource not in observed:
        raise RuntimeError('App-Icon fehlt im tatsächlichen PyInstaller-Inputabgleich.')
    files = [p.relative_to(image).as_posix() for p in image.rglob('*.pyd')]
    if not any(p.endswith('cryptography/hazmat/bindings/_rust.pyd') for p in files) or not any(
            Path(p).name.startswith('_cffi_backend.') for p in files):
        raise RuntimeError('Native Kryptografiemodule fehlen im Frozen-Payload.')
    audit['update_modules'] = sorted(required)
    audit['crypto_extensions'] = sorted(p for p in files if 'cryptography/' in p or '_cffi_backend.' in p)
    if app == PG:
        observed = set(audit['repository_inputs'])
        if 'tools/game_app/desktop_entry.py' not in observed:
            raise RuntimeError('PG entry missing in real Analysis')
        audit['frozen_modules'] = sorted(name for name in names if name.startswith('tools.'))
        audit['native_inventory'] = [
            {'file': member.relative_to(image).as_posix(), 'bytes': member.stat().st_size, 'sha256': sha(member)}
            for member in sorted((image / '_internal').rglob('*'))
            if member.is_file() and member.suffix.lower() in ('.dll', '.pyd', '.exe')
        ]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--version', help='Explicitly planned 0.1.x publication version; source stays unchanged')
    args = parser.parse_args()
    build(args.output, version=args.version)
