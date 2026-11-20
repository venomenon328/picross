"""PG's committed input projection, isolated Godot import and export audit."""
import json
from pathlib import Path
import re
import shutil

from tools import p1_preflight as toolchain

TOOLS = {
    'tools/__init__.py', 'tools/app_products.py', 'tools/msi_database.py',
    'tools/build_main_player.py', 'tools/player_delivery_texts.py', 'tools/p1_preflight.py',
    'tools/background_import.py', '.github/workflows/game-installer.yml', '.gitattributes',
}
COMMON = {
    '__init__.py', 'build_installer.py', 'verify_installer.py', 'packaging/Guard.cs',
    'payload.py', 'release.py', 'release_manifest.py', 'release_channel.py',
    'release_catalog.py', 'update_verifier.py', 'requirements-update.txt',
}
BACKGROUND = {
    '__init__', 'analysis_contract', 'analysis_io', 'authoring_package', 'background_contract', 'catalog_added',
    'catalog_background', 'catalog_io', 'catalog_method', 'catalog_rating',
    'categories', 'content_registry', 'contract', 'current_content', 'difficulty_identity',
    'difficulty_rating', 'operation_diagnostics',
}
GAME_APP = {
    '__init__.py', 'assets/game.ico', 'build.py', 'inputs.py', 'inspect.py',
    'Launcher.cs', 'release.json', 'release_channel.py', 'update-trust.json', 'START.txt',
}
LICENSES = {
    'game/art/drawing/NOTICES.md', 'game/art/drawing/Bakso-NOTICES.md',
    'game/art/drawing/DelightCoffee-NOTICES.md',
}
OMITTED = {
    'game/ui/pencil_marks.gd', 'game/ui/pencil_marks.gd.uid',
    'game/art/drawing/TidyHand.ttf', 'game/art/drawing/TidyHand.ttf.import',
}
RESOURCE_TYPES = {
    '.gd', '.gdshader', '.gdshaderinc', '.import', '.json', '.png', '.svg',
    '.tres', '.tscn', '.ttf', '.txt', '.uid',
}


def runtime(path):
    if path in {'game/project.godot', 'game/export_presets.cfg', 'game/main.tscn',
                'game/web/background_loader.js'}:
        return True
    return (path.startswith(('game/art/', 'game/book/', 'game/data/', 'game/model/', 'game/ui/'))
            and path not in OMITTED and not path.startswith('game/art/drawing/tidy-hand/')
            and not re.match(r'game/data/[^/]*proof', path)
            and (Path(path).suffix in RESOURCE_TYPES
                 or path == 'game/art/drawing/delight-coffee/Read Me.pdf'))


def selected(path):
    return (path in TOOLS or path in LICENSES or path in {'game/README.md', 'content/registry.json'}
            or runtime(path)
            or re.fullmatch(r'content/backgrounds/pz-[a-z0-9][a-z0-9-]{0,59}\.json', path) is not None
            or path.removeprefix('tools/game_app/') in GAME_APP
            or path.removeprefix('tools/production_workspace/') in COMMON
            or (path.startswith('tools/puzzle_production/') and path.count('/') == 2
                and Path(path).suffix == '.py' and Path(path).stem in BACKGROUND))


def stage_project(root, project, inputs):
    """Materialize only the runtime projection. Verify every selected checkout byte."""
    for row in inputs['files']:
        name = row['file']
        original = root / name
        if original.is_symlink() or not original.is_file():
            raise ValueError('Missing or linked committed game input: ' + name)
        if original.stat().st_size != row['bytes'] or toolchain.sha256_file(original) != row['sha256']:
            raise ValueError('Checkout differs from committed game input: ' + name)
        if runtime(name):
            target = project / name.removeprefix('game/')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(original.read_bytes())


GODOT_NOTICE_COMMIT = 'ed1daf0bf001b61586d9930840f2f1394092c079'
GODOT_NOTICES = {
    'LICENSE.txt': ('Godot-MIT.txt', 'b0435e3b3e4e55238f05f4b306f30524a1b2e20147810d436eaa554fa6855c80'),
    'COPYRIGHT.txt': ('Godot-COPYRIGHT.txt', 'cb1980c88089573bcacd7221d777c689bb8bbd778799f24c27fca0fe5f774d6d'),
}


def write_export_audit(output, inputs, commit, cache, editor, backgrounds, player):
    for name, (target, digest) in GODOT_NOTICES.items():
        url = f'https://raw.githubusercontent.com/godotengine/godot/{GODOT_NOTICE_COMMIT}/{name}'
        cached = cache / target
        toolchain.download_asset(url, cached, digest, 90)
        shutil.copyfile(cached, player / 'licenses' / target)
    version = toolchain.EXPECTED_VERSION
    pack = player / 'picross-p1.pck'
    with pack.open('rb') as stream:
        if stream.read(4) != b'GDPC':
            raise ValueError('Player did not emit a separate Godot pack')
    report = {
        'format': 'picross-pg-export-audit-v1',
        'commit': commit, 'fingerprint': inputs['sha256'],
        'engine': {'version': version, 'name': editor.name, 'sha256': editor.sha256},
        'templates': {'name': toolchain.TEMPLATES.name, 'sha256': toolchain.TEMPLATES.sha256},
        'export': {'preset': 'P1 Windows x86_64', 'mode': 'debug', 'app_name': 'picross · P1'},
        'project_inputs': [row['file'] for row in inputs['files'] if runtime(row['file'])],
        'generated_background_import': backgrounds,
        'player_files': [
            {'file': member.relative_to(player).as_posix(), 'bytes': member.stat().st_size,
             'sha256': toolchain.sha256_file(member)}
            for member in sorted(player.rglob('*')) if member.is_file()
        ],
    }
    output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
