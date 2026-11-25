"""Isolated renderer for the actual palette, paper, cell atlas and clue ink at two sizes."""
from contextlib import contextmanager
from io import BytesIO
import json
import os
from pathlib import Path
import platform
import shutil
import stat
import subprocess
import tempfile
from time import monotonic
from urllib.error import HTTPError

from . import p1_preflight as engine
from . import work_refs
from .puzzle_production import catalog_io, catalog_rating
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
            try:
                with urlopen(url, timeout=30) as response:
                    raw = response.read(spec['bytes'] + 1)
            except HTTPError as exc:
                raise ValueError(f'Test drawing resource {name}: HTTP {exc.code}') from exc
            require(len(raw) == spec['bytes'] and sha256(raw).hexdigest() == spec['sha256'], 'Different test art')
            target.write_bytes(raw)


def cache_key(repository):
    from .production_remote_delivery import REPOSITORIES
    host, arch = platform.system(), platform.machine().lower()
    require(arch in ('x86_64', 'amd64') and host in engine.EDITORS, 'Unsupported editor host')
    return f'pw-editor-v1-{REPOSITORIES[repository]}-{host}-x64-{engine.RELEASE_TAG}-{engine.EDITORS[host].sha256}'


def editor_archive(work, host, metrics):
    asset = engine.EDITORS[host]
    start = monotonic()
    local = work / asset.name
    cached = os.environ.get('PW_EDITOR_CACHE')
    slot = None
    state = 'disabled'
    if cached:
        root = catalog_io.external(os.environ['RUNNER_TEMP'])
        slot = root / 'pw-editor.zip'
        require(Path(cached) == slot, 'Unexpected editor cache location')
        state = 'miss'
        try:
            entry = slot.lstat()
        except FileNotFoundError:
            pass
        else:
            regular = (stat.S_ISREG(entry.st_mode) and entry.st_nlink == 1
                       and not getattr(entry, 'st_file_attributes', 0) & 0x400)
            if regular:
                try:
                    engine.verify_sha256(slot, asset.sha256)
                except engine.PreflightError:
                    pass
                else:
                    metrics.update(cache='hit', archive_bytes=entry.st_size, download=None,
                                   cache_verify=round(monotonic() - start, 6))
                    return slot
            slot.rename(work / 'rejected-editor-cache')
            state = 'rejected'
    metrics['cache_verify'] = round(monotonic() - start, 6) if slot else None
    url = f'https://github.com/godotengine/godot-builds/releases/download/{engine.RELEASE_TAG}/{asset.name}'
    start = monotonic()
    try:
        engine.download_asset(url, local, asset.sha256, 300)
    except HTTPError as exc:
        raise ValueError(f'Pinned editor download: HTTP {exc.code}') from exc
    metrics.update(cache=state, archive_bytes=local.stat().st_size, download=round(monotonic() - start, 6))
    if slot:
        local.replace(slot)
        return slot
    return local


@contextmanager
def open_renderer(private, metrics):
    host = platform.system()
    with tempfile.TemporaryDirectory(dir=private) as tmp:
        work = Path(tmp)
        project = work / 'project'
        start = monotonic()
        resources(project)
        shutil.copyfile(ROOT / 'tools/production_remote_view.gd', project / 'view.gd')
        (project / 'project.godot').write_text('config_version=5\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n',
                                               encoding='utf-8')
        metrics['resources'] = round(monotonic() - start, 6)
        archive = editor_archive(work, host, metrics)
        start = monotonic()
        executable = engine.extract_editor(archive, work / 'engine', host)
        metrics['extract'] = round(monotonic() - start, 6)
        env = engine.isolated_environment(work, host)
        env = {k: v for k, v in env.items() if not k.startswith(('GH_', 'GITHUB_', 'ACTIONS_'))}
        def invoke(command):
            result = subprocess.run(command, capture_output=True, env=env, timeout=120)
            require(result.returncode == 0 and b'SCRIPT ERROR' not in result.stderr and b'ERROR:' not in result.stderr,
                    'Inspection renderer failed: ' + result.stderr.decode('utf-8', errors='replace')[-1024:])
        start = monotonic()
        invoke([executable, '--headless', '--path', project, '--import'])
        metrics['import'] = round(monotonic() - start, 6)
        metrics['views'] = []
        display = ['xvfb-run', '-a'] if host == 'Linux' else []

        def render(raw):
            from PIL import Image
            definition, _, _, _ = catalog_rating.definition(raw)
            require(max(definition['width'], definition['height']) <= 50, 'Unsupported inspection dimensions')
            start = monotonic()
            # Each input and its output stay outside the project's import scan.
            with tempfile.TemporaryDirectory(dir=work, prefix='view-') as directory:
                view = Path(directory)
                data = view / 'definition.json'
                data.write_bytes(raw)
                invoke([*display, executable, '--path', project, '--audio-driver', 'Dummy', '--rendering-method',
                        'gl_compatibility', '--script', 'res://view.gd', '--', data, view])
                panels = []
                for pitch in (24, 14):
                    for status in range(3):
                        with Image.open(view / f'{pitch}-{status}.png') as panel:
                            panels.append(panel.convert('RGB'))
                width, height = panels[0].size
                sheet = Image.new('RGB', (3 * width, height + panels[3].height), '#faf6ec')
                for i, panel in enumerate(panels):
                    sheet.paste(panel, ((i % 3) * width, height if i >= 3 else 0))
                out = BytesIO()
                sheet.save(out, format='PNG')
            metrics['views'].append(round(monotonic() - start, 6))
            return out.getvalue()

        yield render


def render(raw, private):
    with open_renderer(private, {}) as view:
        return view(raw)
