"""Build the pinned Godot static player, separately from deployment."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import zipfile

import p1_preflight as tc
import web_bundle


def extract_web_templates(archive: Path, destination: Path) -> None:
    wanted = {'version.txt', 'web_nothreads_debug.zip', 'web_nothreads_release.zip'}
    destination.mkdir(parents=True, exist_ok=True)
    found = set()
    with zipfile.ZipFile(archive) as bundle:
        for item in bundle.infolist():
            member = tc.safe_member_name(item.filename)
            if item.filename not in {'templates/' + n for n in wanted}:
                continue
            if member.name in found:
                raise ValueError('Duplicate template')
            found.add(member.name)
            with bundle.open(item) as source, (destination/member.name).open('wb') as target:
                shutil.copyfileobj(source, target)
    if found != wanted:
        raise ValueError('Missing single-thread web templates')


def build(cache: Path, output: Path, *, test: bool = False, development: bool = False, test_reveal_revision: int = 1) -> dict:
    if test_reveal_revision not in (1, 2) or test_reveal_revision != 1 and not test:
        raise ValueError('Image revision is only supported by the isolated test player')
    root = Path(__file__).resolve().parents[1]
    # Deliberately do not trust the preflight source override: the actual tree is built.
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    dirty = bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=root, text=True).strip())
    if dirty and not development:
        raise ValueError('Clean checkout required; --development produces a non-deployable diagnostic build')
    if output.exists() and any(output.iterdir()):
        raise ValueError('Output must be empty')
    host = platform.system()
    editor = tc.EDITORS[host]
    urls = tc.official_asset_urls(tc.request_json(tc.RELEASE_API), (editor, tc.TEMPLATES))
    for asset in (editor, tc.TEMPLATES):
        tc.download_asset(urls[asset.name], cache/asset.name, asset.sha256, 1200)
    now = datetime.now(timezone.utc)
    kind = 'dirty' if dirty else 'test' if test else 'player'
    build_id = f'{commit}-{kind}-{now:%Y%m%d%H%M%S}'
    with tempfile.TemporaryDirectory(prefix='picross-web-') as temporary:
        work = Path(temporary)
        engine = str(tc.extract_editor(cache/editor.name, work/'engine', host))
        extract_web_templates(cache/tc.TEMPLATES.name, tc.template_directory(work, host))
        project = work/'game'
        shutil.copytree(root/'game', project, ignore=shutil.ignore_patterns('.godot', 'build', *(['content'] if test else [])))
        from p1_product import player_extras, player_guide, run_phase, require_clean_output
        if test:
            from product_fixtures import install_runtime_fixtures
            install_runtime_fixtures(root, project)
            from web_tests.fixtures import adapt
            adapt(project)
            from at_fixtures import install
            install(project, test_reveal_revision)
            preset = project/'export_presets.cfg'
            preset.write_text(preset.read_text(encoding='utf-8').replace('data/*.json,', 'data/fixtures/*.json,data/*.json,'), encoding='utf-8', newline='\n')
            shutil.copyfile(root/'tools/web_tests/probe.gd', project/'ui/web_probe.gd')
            scene = project/'main.tscn'
            scene.write_text(scene.read_text(encoding='utf-8').replace('res://ui/main.gd', 'res://ui/web_probe.gd'), encoding='utf-8', newline='\n')
        exported = work/'export'
        exported.mkdir()
        logs = output.parent/(output.name+'-logs')
        logs.mkdir(parents=True, exist_ok=True)
        env = tc.isolated_environment(work, host)
        for name, args, marker in (
            ('version', ['--version'], tc.EXPECTED_VERSION),
            ('import', ['--headless', '--path', str(project), '--import'], None),
            ('web-export', ['--headless', '--path', str(project), '--export-debug', 'P1 Web', str(exported/'index.html')], None),
        ):
            result = run_phase(name, [engine, *args], env, 300, logs)
            require_clean_output(result, marker)
        if not test:
            # Inspect the actual exported pack using the existing external probe.
            # This checks package boundaries, not every production puzzle.
            registry = json.loads((root/'content/registry.json').read_text(encoding='utf-8'))
            pack_env = {**env, 'ZA1_PACK_COUNT': str(sum(e['visible'] for e in registry['entries']))}
            result = run_phase('web-content-pck', [engine, '--headless', '--main-pack', str(exported/'index.pck'),
                '--script', str(root/'game/tests/content_pack_probe.gd')], pack_env, 300, logs)
            require_clean_output(result, 'CONTENT_PACK_OK')
        version = output/'releases'/build_id
        version.mkdir(parents=True)
        if test:
            shutil.copyfile(project/'tests/at-fixture.json', version/'at-fixture.json')
        for path in exported.iterdir():
            if path.name != 'index.html':
                shutil.copyfile(path, version/path.name)
        html = (exported/'index.html').read_text(encoding='utf-8').replace('@@BUILD@@', build_id).replace('@@SHORT@@', commit[:12])
        (output/'index.html').write_text(html, encoding='utf-8', newline='\n')
        (version/'entry.html').write_text(html, encoding='utf-8', newline='\n')
        shutil.copyfile(root/'game/web/storage.js', version/'storage.js')
        for name, path in player_extras(root, work).items():
            target = version/name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
        (version/'SPIELANLEITUNG.md').write_text(player_guide(root, commit), encoding='utf-8', newline='\n')
        manifest = dict(format=web_bundle.FORMAT, build_id=build_id, source_commit=commit,
                        engine=tc.RELEASE_TAG, built_at=now.isoformat(), kind=kind,
                        files=web_bundle.inventory(output))
        (output/'build-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8', newline='\n')
        if not dirty:
            web_bundle.validate(output, allow_test=test)
        return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--test', action='store_true', help='Isolated technical fixture player; never deployable')
    parser.add_argument('--development', action='store_true', help='Explicitly label a dirty diagnostic build')
    parser.add_argument('--test-reveal-revision', type=int, choices=(1, 2), default=1,
                        help='Synthetic image bytes in the isolated test export')
    args = parser.parse_args()
    try:
        manifest = build(args.cache_dir.resolve(), args.output_dir.resolve(), test=args.test, development=args.development,
                         test_reveal_revision=args.test_reveal_revision)
        print('WEB BUILD', manifest['build_id'])
        return 0
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile) as error:
        print('WEB BUILD FAILED:', error, file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
