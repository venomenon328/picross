"""Strict, shared static WEB-1 bundle contract (no engine needed for deployment)."""
from __future__ import annotations
import hashlib
from datetime import datetime
import json
from pathlib import Path, PurePosixPath
import re

FORMAT = "picross-web-v1"
BUILD_ID = re.compile(r"[0-9a-f]{40}-(player|test|dirty)-[0-9]{14}\Z")
LICENSES = {'resources.json', 'Chalkboard-NOTICES.md', 'Bakso-NOTICES.md',
            'DelightCoffee-NOTICES.md', 'delight-coffee/More Info.txt',
            'delight-coffee/Read Me.pdf', 'Fraunces-OFL.txt', 'PlexSans-OFL.txt', 'Sidebar-NOTICES.txt'}


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            result.update(block)
    return result.hexdigest()


def safe_name(name: str) -> bool:
    path = PurePosixPath(name)
    return (bool(re.fullmatch(r'[A-Za-z0-9_./ -]+', name)) and not path.is_absolute() and path.as_posix() == name
            and all(p not in {'.', '..'} and not p.startswith('.') for p in path.parts)
            and not any(c in name for c in '\\\r\n\x00'))


def inventory(root: Path) -> dict:
    result = {}
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError('Symlinks are not bundle files')
        if path.is_file() and path != root/'build-manifest.json':
            name = path.relative_to(root).as_posix()
            if not safe_name(name) or not path.stat().st_size:
                raise ValueError('Unsafe or empty bundle file')
            result[name] = {'size': path.stat().st_size, 'sha256': digest(path)}
    return result


def validate_manifest(manifest: dict, *, allow_test: bool = False) -> dict:
    if not isinstance(manifest, dict) or set(manifest) != {'format', 'build_id', 'source_commit', 'engine', 'built_at', 'kind', 'files'}:
        raise ValueError('Unexpected manifest schema')
    build = manifest['build_id']
    if (manifest['format'] != FORMAT or not isinstance(build, str) or not BUILD_ID.fullmatch(build)
            or build[:40] != manifest['source_commit'] or manifest['engine'] != '4.7.2-stable'
            or not isinstance(manifest['kind'], str)
            or manifest['kind'] not in ({'player', 'test'} if allow_test else {'player'})
            or build.split('-')[1] != manifest['kind']):
        raise ValueError('Unsupported or uncommitted build')
    if not isinstance(manifest['built_at'], str) or datetime.fromisoformat(manifest['built_at']).tzinfo is None:
        raise ValueError('Build time must include timezone')
    files = manifest['files']
    prefix = f'releases/{build}/'
    required = {'index.html', *(prefix + n for n in ('entry.html', 'index.js', 'index.wasm', 'index.pck', 'storage.js', 'SPIELANLEITUNG.md'))}
    required.update(prefix+'licenses/'+name for name in LICENSES)
    if not isinstance(files, dict) or not required <= files.keys():
        raise ValueError('Incomplete bundle')
    allowed = {'entry.html', 'index.js', 'index.wasm', 'index.pck', 'storage.js', 'SPIELANLEITUNG.md',
               'index.audio.worklet.js', 'index.audio.position.worklet.js', 'index.icon.png', 'index.apple-touch-icon.png', 'index.png'}
    allowed.update('licenses/'+name for name in LICENSES)
    for name, entry in files.items():
        if not safe_name(name) or (name != 'index.html' and (not name.startswith(prefix) or
                name[len(prefix):] not in allowed)):
            raise ValueError('Unexpected bundle member')
        if (not isinstance(entry, dict) or set(entry) != {'size', 'sha256'} or type(entry['size']) is not int
                or entry['size'] <= 0 or not isinstance(entry['sha256'], str) or not re.fullmatch('[0-9a-f]{64}', entry['sha256'])):
            raise ValueError('Invalid file integrity metadata')
    if files['index.html'] != files[prefix+'entry.html']:
        raise ValueError('Entry metadata differs')
    return manifest


def validate(root: Path, *, allow_test: bool = False) -> dict:
    if root.is_symlink() or (root/'build-manifest.json').is_symlink():
        raise ValueError('Bundle root/manifest may not be a symlink')
    manifest = validate_manifest(json.loads((root/'build-manifest.json').read_text(encoding='utf-8')), allow_test=allow_test)
    files = manifest['files']
    build = manifest['build_id']
    prefix = f'releases/{build}/'
    if inventory(root) != files:
        raise ValueError('Bundle file inventory/hash mismatch')
    if (root/'index.html').read_bytes() != (root/prefix/'entry.html').read_bytes():
        raise ValueError('Entry copies differ')
    html = (root/'index.html').read_text(encoding='utf-8')
    if f'<base href="./{prefix}">' not in html or f'data-build="{build}"' not in html:
        raise ValueError('Entry is not bound to immutable resources')
    return manifest
