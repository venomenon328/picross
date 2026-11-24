"""Isolated renderer for the actual palette, paper, cell atlas and clue ink at two sizes."""
from io import BytesIO
import json
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile

from . import p1_preflight as engine
from . import work_refs
from .puzzle_production import catalog_rating
from .puzzle_production.authoring_package import require

ROOT = Path(__file__).resolve().parents[1]
RESOURCES = ('ui/scribble.gd', 'ui/clue_typography.gd', 'ui/clue_font.tres', 'ui/cell_atlas.gd',
             'ui/atlas_mask.gdshader', 'art/book/PlexSans.ttf', 'art/drawing/DelightCoffee-Regular.ttf',
             'book/paper.png', 'book/paper.png.import', 'art/cells/fill-small.png', 'art/cells/fill-small.png.import',
             'art/cells/fill-medium.png', 'art/cells/fill-medium.png.import')


def resources(project):
    # The isolated test repository holds a synthetic catalog only. Its trusted
    # deployment pins the shared game art, without redistributing original fonts.
    bindings = None
    if work_refs.FIXTURE:
        import re
        bindings = json.loads((ROOT / 'tools/pw-test-art-source.json').read_bytes())
        require(re.fullmatch('[a-f0-9]{40}', bindings['commit']) and set(bindings['files']) == set(RESOURCES),
                'Unbound test drawing resources')
    for name in RESOURCES:
        target = project / name
        target.parent.mkdir(exist_ok=True, parents=True)
        if bindings is None:
            shutil.copyfile(ROOT / 'game' / name, target)
        else:
            from urllib.request import urlopen
            from hashlib import sha256
            spec = bindings['files'][name]
            url = f'https://raw.githubusercontent.com/venomenon328/picross/{bindings["commit"]}/game/{name}'
            with urlopen(url, timeout=30) as response:
                raw = response.read(spec['bytes'] + 1)
            require(len(raw) == spec['bytes'] and sha256(raw).hexdigest() == spec['sha256'], 'Different test art')
            target.write_bytes(raw)


def render(raw, private):
    from PIL import Image
    definition, _, _, _ = catalog_rating.definition(raw)
    require(max(definition['width'], definition['height']) <= 50, 'Unsupported inspection dimensions')
    host = platform.system()
    asset = engine.EDITORS[host]
    with tempfile.TemporaryDirectory(dir=private) as tmp:
        work = Path(tmp)
        project = work / 'project'
        resources(project)
        shutil.copyfile(ROOT / 'tools/production_remote_view.gd', project / 'view.gd')
        (project / 'project.godot').write_text('config_version=5\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n',
                                               encoding='utf-8')
        urls = engine.official_asset_urls(engine.request_json(engine.RELEASE_API), (asset,))
        archive = work / asset.name
        engine.download_asset(urls[asset.name], archive, asset.sha256, 300)
        executable = engine.extract_editor(archive, work / 'engine', host)
        env = engine.isolated_environment(work, host)
        env = {k: v for k, v in env.items() if not k.startswith(('GH_', 'GITHUB_', 'ACTIONS_'))}
        def invoke(command):
            result = subprocess.run(command, capture_output=True, env=env, timeout=120)
            require(result.returncode == 0 and b'SCRIPT ERROR' not in result.stderr and b'ERROR:' not in result.stderr,
                    'Inspection renderer failed: ' + result.stderr.decode('utf-8', errors='replace')[-1024:])
        invoke([executable, '--headless', '--path', project, '--import'])
        # Keep the validated input outside the trusted project and its import scan.
        data = work / 'definition.json'
        data.write_bytes(raw)
        display = ['xvfb-run', '-a'] if host == 'Linux' else []
        invoke([*display, executable, '--path', project, '--audio-driver', 'Dummy', '--rendering-method',
                'gl_compatibility', '--script', 'res://view.gd', '--', data, work])
        panels = []
        for pitch in (24, 14):
            for status in range(3):
                with Image.open(work / f'{pitch}-{status}.png') as panel:
                    panels.append(panel.convert('RGB'))
        width, height = panels[0].size
        sheet = Image.new('RGB', (3 * width, height + panels[3].height), '#faf6ec')
        for i, panel in enumerate(panels):
            sheet.paste(panel, ((i % 3) * width, height if i >= 3 else 0))
        out = BytesIO()
        sheet.save(out, format='PNG')
        return out.getvalue()
