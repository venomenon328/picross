"""Build the existing debug player and its PG launcher/installer on Windows."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from tools.app_products import PG
from tools.production_workspace.build_installer import run
from tools.production_workspace.build_windows import ROOT, sha
from tools.production_workspace.payload import canonical, fingerprint, git


def build_player_image(output, product):
    if os.name != 'nt':
        raise RuntimeError('PG installer build needs Windows x64')
    commit = git(ROOT, 'rev-parse', 'HEAD').decode().strip()
    if git(ROOT, 'status', '--porcelain'):
        raise ValueError('PG installer build needs a clean source checkout')
    output.mkdir(parents=True, exist_ok=False)
    work = output / 'work'
    image = output / 'dist' / PG.executable
    image.mkdir(parents=True)
    work.mkdir()
    inputs = fingerprint(ROOT, app=PG)
    (output / 'inputs.json').write_bytes(canonical(inputs))

    # The normal entry point runs with tools/ on the module search path.
    sys.path.insert(0, str(ROOT / 'tools'))
    try:
        from tools.build_main_player import main as export
        staged = work / 'player'
        audit = output / 'input-audit.json'
        cache = Path(os.environ.get('PG_BUILD_CACHE', work / 'cache')).resolve()
        if export(['--cache-dir', str(cache), '--output-dir', str(staged)],
                  app_inputs=inputs, audit=audit):
            raise RuntimeError('Regular Windows player export failed')
    finally:
        sys.path.pop(0)

    for name in ('picross-p1.exe', 'picross-p1.pck', 'SPIELANLEITUNG.md'):
        shutil.copyfile(staged / name, image / name)
    shutil.copytree(staged / 'licenses', image / 'licenses')
    shutil.copyfile(PG.source / 'START.txt', image / 'START.txt')
    player, pack = (image / name for name in ('picross-p1.exe', 'picross-p1.pck'))
    version = product['version']
    identity = work / 'BuildIdentity.cs'
    # PE file/product resources support the complete MSI patch range.
    # The CLR assembly identity reserves 65535 and is private to the launcher.
    identity.write_text(
        f'[assembly: System.Reflection.AssemblyFileVersion("{version}.0")]\n'
        f'[assembly: System.Reflection.AssemblyInformationalVersion("{version}.0")]\n'
        '[assembly: System.Reflection.AssemblyTitle("Picross")]\n'
        'internal static class BuildIdentity {\n'
        f'    internal const string PlayerHash = "{sha(player)}";\n'
        f'    internal const string PackHash = "{sha(pack)}";\n'
        '}\n', encoding='utf-8')
    launcher = image / (PG.executable + '.exe')
    compiler = Path(os.environ['SystemRoot']) / 'Microsoft.NET/Framework64/v4.0.30319/csc.exe'
    subprocess.run([str(compiler), '/nologo', '/codepage:65001', '/target:winexe', '/platform:x64',
                    '/out:' + str(launcher), '/win32icon:' + str(PG.source / PG.icon_resource),
                    str(PG.source / 'Launcher.cs'), str(identity)], check=True)
    export_audit = json.loads(audit.read_bytes())
    report = {
        'format': 'picross-pg-build-v1', 'commit': commit, 'version': version,
        'product_code': product['product_code'], 'upgrade_code': product['upgrade_code'],
        'architecture': 'windows-x64', 'payload_fingerprint': inputs['sha256'],
        'engine': export_audit['engine'], 'templates': export_audit['templates'],
        'export_audit_sha256': sha(audit), 'launcher_compiler_sha256': sha(compiler),
        'exe_bytes': launcher.stat().st_size, 'exe_sha256': sha(launcher),
        'player_bytes': player.stat().st_size, 'player_sha256': sha(player),
        'pck_bytes': pack.stat().st_size, 'pck_sha256': sha(pack), 'signed': False,
    }
    (image / 'components.json').write_bytes(canonical(report))
    (output / 'delivery.json').write_bytes(canonical(report))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--version', default='0.1.1')
    args = parser.parse_args()
    run(args.output.resolve(), version=args.version, app=PG)


if __name__ == '__main__':
    main()
