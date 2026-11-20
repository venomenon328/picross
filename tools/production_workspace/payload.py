"""Audited source inputs for the frozen application and MSI builder.

Only committed bytes are fingerprinted. The real PyInstaller Analysis TOC is
checked against this inventory before a build can be delivered.
"""
import ast
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import re

from tools.app_products import PW, PE

WORKSPACE = 'tools/production_workspace/'
PRODUCTION = 'tools/puzzle_production/'
# These files are neither collected nor read by the MSI/App builder. New unknown
# files in either packaging scope fail closed until explicitly classified.
IGNORED = {
    'Picross-Start.cmd', 'launcher_header.cmd', 'start-production-workspace.cmd',
    'check_ui_loading.cjs', 'presentation.schema.json', 'request.schema.json',
    'assets/launcher.png', 'smoke_installer.py', 'smoke_windows.py',
    'build_launcher.py', 'launcher_bootstrap.py',
    'update_diagnostic.py',  # Isolated synthetic signing adapter; never frozen.
    'helper_diagnostic.py', 'packaging/HelperDiagnostic.cs',  # Explicit, non-installing T02 adapter.
}
PRODUCTION_DATA = {
    'difficulty_calibration_0_3.json', 'difficulty_method_0_3.json',
    'difficulty_references_0_3.json', 'sd2_calibration_0_4.json',
    'sd2_comparison_0_4.json', 'sd2_method_0_4.json',
    'sd2_references_0_4.json', 'sd2_validation_0_4.json', 'requirements-image.txt',
}
# Synthetic ZA-1 support is deliberately excluded from the Windows executable.
PRODUCTION_TEST_ONLY = {'za1_fixtures.py'}


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n').encode('utf-8')


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args])


PE_SHARED = {
    '__init__.py',
    'release.py', 'payload.py', 'release_manifest.py', 'update_verifier.py',
    'release_channel.py', 'release_catalog.py', 'build_windows.py', 'build_installer.py',
    'verify_installer.py', 'smoke_installer.py', 'install_interlock.py',
    'requirements-windows.txt', 'requirements-update.txt', 'packaging/Guard.cs',
    'packaging/UpdateHelper.cs', 'app_updates.py', 'update_client.py',
    'update_storage.py', 'update_windows.py', 'instance.py', 'processes.py',
}
PE_EXCLUDED = {'images_cli', 'metadata_cli', 'raster_cli', 'editor_cli', 'za1_fixtures'}
PE_DIAGNOSTIC = {'diagnostic.py', 'frozen_diagnostic.py'}


def pe_selected(path):
    if path in {'tools/__init__.py', 'tools/app_products.py', 'tools/msi_database.py', '.github/workflows/pe-installer.yml'}:
        return True
    if path.startswith('tools/puzzle_editor/'):
        local = path[len('tools/puzzle_editor/'):]
        if local in PE_DIAGNOSTIC:
            return False
        if (local.endswith('.py') or local.startswith('ui/') or
                local in {PE.icon_resource, 'README.md', 'requirements-windows.txt', 'release.json', 'update-trust.json'}):
            return True
        raise ValueError('Unclassified potential package input: ' + path)
    if path.startswith(WORKSPACE):
        local = path[len(WORKSPACE):]
        return local in PE_SHARED or local.startswith('licenses/') and local.endswith('.txt')
    if path.startswith(PRODUCTION):
        local = path[len(PRODUCTION):]
        if local.endswith('.py'):
            return Path(local).stem not in PE_EXCLUDED
        if '/' not in local and Path(local).suffix in {'.json', '.md'}:
            return True  # Actually copied method/configuration bytes, including README.
        if local in {'requirements-image.txt'}:
            return False
        raise ValueError('Unclassified potential package input: ' + path)
    if path in {'game/book/paper.png', 'game/book/paper.json'} or path.startswith('game/art/drawing/margins/'):
        return True
    return False


def selected(path, *, app=PW):
    if app == PE:
        return pe_selected(path)
    if path in {'tools/__init__.py', 'tools/app_products.py', 'tools/msi_database.py',
                'tools/work_refs.py', '.github/workflows/pw-installer.yml'}:
        return True
    for scope in (WORKSPACE, PRODUCTION):
        if path.startswith(scope):
            local = path[len(scope):]
            if local.endswith('.md') or (scope == WORKSPACE and local in IGNORED) or (scope == PRODUCTION and local in PRODUCTION_DATA | PRODUCTION_TEST_ONLY):
                return False
            if local.endswith('.py'):
                return True
            if scope == WORKSPACE and (local.startswith('ui/') or local.startswith('licenses/') or
                                      local in {PW.icon_resource, 'packaging/Guard.cs', 'packaging/UpdateHelper.cs', 'release.json',
                                                'requirements-windows.txt', 'requirements-update.txt',
                                                'update-trust.json', 'START-WINDOWS.txt'}):
                return True
            raise ValueError('Unclassified potential package input: ' + path)
    return False


def fingerprint(root, *, app=PW):
    rows = []
    seen = set()
    tree = git(root, 'ls-tree', '-rz', '--full-tree', 'HEAD').split(b'\0')
    for entry in tree:
        if not entry:
            continue
        metadata, name = entry.split(b'\t', 1)
        path = name.decode('utf-8')
        if not selected(path, app=app):
            continue
        mode, kind, blob = metadata.decode().split()
        parts = PurePosixPath(path).parts
        if (kind != 'blob' or mode not in {'100644', '100755'} or path.casefold() in seen or
                PurePosixPath(path).is_absolute() or PurePosixPath(path).as_posix() != path or
                any(p in {'.', '..'} or p.endswith((' ', '.')) or
                    re.search(r'[\x00-\x1f<>:"\\|?*]', p) or
                    re.fullmatch(r'(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(\..*)?', p) for p in parts)):
            raise ValueError('Unsafe package input: ' + path)
        seen.add(path.casefold())
        raw = git(root, 'cat-file', 'blob', blob)
        rows.append({'file': path, 'mode': mode, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
    rows.sort(key=lambda row: row['file'])
    if not rows:
        raise ValueError('Empty package input inventory')
    return {'format': 'picross-app-inputs-v1', 'sha256': hashlib.sha256(canonical(rows)).hexdigest(), 'files': rows}


def audit_analysis(root, toc, inventory, generated, *, app=PW):
    """Reject every repository input absent from the prebuild fingerprint.

    Walk the Analysis literal, not its version-dependent tuple offsets. External
    Python/wheel files are pinned separately by the private build environment.
    Generated build.json/version files live outside the source tree.
    """
    root = root.resolve()
    expected = {row['file']: row for row in inventory['files']}
    observed = set()
    generated = {p.resolve() for p in generated}

    def visit(value):
        if isinstance(value, (tuple, list)):
            for item in value:
                visit(item)
        elif isinstance(value, str):
            path = Path(value)
            if not path.is_absolute() or not path.is_file() or path.resolve() in generated:
                return
            path = path.resolve()
            if path.is_relative_to(root):
                relative = path.relative_to(root).as_posix()
                if relative not in expected:
                    raise ValueError('Frozen input absent from fingerprint: ' + relative)
                if hashlib.sha256(path.read_bytes()).hexdigest() != expected[relative]['sha256']:
                    raise ValueError('Frozen source differs from committed input: ' + relative)
                observed.add(relative)

    visit(ast.literal_eval(toc.read_text(encoding='utf-8')))
    if app.package + '/desktop_entry.py' not in observed:
        raise ValueError('Missing frozen entry point in Analysis inventory')
    return {'format': 'picross-frozen-input-audit-v1', 'fingerprint': inventory['sha256'],
            'repository_inputs': sorted(observed)}
