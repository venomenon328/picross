"""Build the bound Godot debug player and the separate PG launcher and MSI."""
import argparse
import json
import os
from pathlib import Path
import shutil
import sys

from tools.app_products import PG
from tools.production_workspace.build_installer import run
from tools.production_workspace.build_windows import ROOT, build, sha
from tools.production_workspace.payload import canonical


def export_player(output, work, inputs):
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

    player, pack = (staged / name for name in ('picross-p1.exe', 'picross-p1.pck'))
    export_audit = json.loads(audit.read_bytes())
    return {
        'engine': export_audit['engine'], 'templates': export_audit['templates'],
        'export_audit_sha256': sha(audit),
        'player_bytes': player.stat().st_size, 'player_sha256': sha(player),
        'pck_bytes': pack.stat().st_size, 'pck_sha256': sha(pack),
    }


def finish_image(output, work, image, manifest):
    staged = work / 'player'
    for name in ('picross-p1.exe', 'picross-p1.pck', 'SPIELANLEITUNG.md'):
        shutil.copyfile(staged / name, image / name)
    shutil.copytree(staged / 'licenses', image / 'licenses', dirs_exist_ok=True)
    launcher = image / (PG.executable + '.exe')
    report = {
        **manifest, 'exe_bytes': launcher.stat().st_size, 'exe_sha256': sha(launcher),
        'frozen_audit_sha256': sha(output / 'frozen-audit.json'),
    }
    (output / 'delivery.json').write_bytes(canonical(report))


def build_player_image(output, product):
    build(output, version=product['version'], app=PG)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--version', default='0.1.1')
    args = parser.parse_args()
    run(args.output.resolve(), version=args.version, app=PG)


if __name__ == '__main__':
    main()
