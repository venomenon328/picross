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
}
PRODUCTION_DATA = {
    'difficulty_calibration_0_3.json', 'difficulty_method_0_3.json',
    'difficulty_references_0_3.json', 'sd2_calibration_0_4.json',
    'sd2_comparison_0_4.json', 'sd2_method_0_4.json',
    'sd2_references_0_4.json', 'sd2_validation_0_4.json', 'requirements-image.txt',
}


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n').encode('utf-8')


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args])


def selected(path):
    if path in {'tools/__init__.py', '.github/workflows/pw-installer.yml'}:
        return True
    for scope in (WORKSPACE, PRODUCTION):
        if path.startswith(scope):
            local = path[len(scope):]
            if local.endswith('.md') or (scope == WORKSPACE and local in IGNORED) or (scope == PRODUCTION and local in PRODUCTION_DATA):
                return False
            if local.endswith('.py'):
                return True
            if scope == WORKSPACE and (local.startswith('ui/') or local.startswith('licenses/') or
                                      local in {'assets/launcher.ico', 'packaging/Guard.cs', 'release.json',
                                                'requirements-windows.txt', 'requirements-update.txt',
                                                'update-trust.json', 'START-WINDOWS.txt'}):
                return True
            raise ValueError('Unclassified potential package input: ' + path)
    return False


def fingerprint(root):
    rows = []
    seen = set()
    tree = git(root, 'ls-tree', '-rz', '--full-tree', 'HEAD').split(b'\0')
    for entry in tree:
        if not entry:
            continue
        metadata, name = entry.split(b'\t', 1)
        path = name.decode('utf-8')
        if not selected(path):
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


def audit_analysis(root, toc, inventory, generated):
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
    if 'tools/production_workspace/desktop_entry.py' not in observed:
        raise ValueError('Missing frozen entry point in Analysis inventory')
    return {'format': 'picross-frozen-input-audit-v1', 'fingerprint': inventory['sha256'],
            'repository_inputs': sorted(observed)}
