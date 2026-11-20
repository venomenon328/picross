"""Read the real PG MSI tables and extracted bytes. No installation."""
import argparse
from pathlib import Path

from tools import p1_preflight as toolchain
from tools.app_products import PG
from tools.production_workspace.verify_installer import NS, require, verify

from .inputs import GODOT_NOTICES, runtime


def binding(path):
    return {'bytes': path.stat().st_size, 'sha256': toolchain.sha256_file(path)}


def verify_audit(build, audit, inputs, report):
    editor = toolchain.EDITORS['Windows']
    require(audit['format'] == 'picross-pg-export-audit-v1' and
            audit['fingerprint'] == inputs['sha256'] and audit['commit'] == report['commit'] and
            audit['project_inputs'] == [row['file'] for row in inputs['files'] if runtime(row['file'])] and
            audit['engine'] == report['engine'] == {
                'name': editor.name, 'sha256': editor.sha256, 'version': toolchain.EXPECTED_VERSION} and
            audit['templates'] == report['templates'] == {
                'name': toolchain.TEMPLATES.name, 'sha256': toolchain.TEMPLATES.sha256} and
            audit['export'] == {'preset': 'P1 Windows x86_64', 'mode': 'debug', 'app_name': 'picross · P1'} and
            toolchain.sha256_file(build / 'input-audit.json') == report['export_audit_sha256'],
            'Unbound regular Windows export audit')
    staged = build / 'work/player'
    actual = {path.relative_to(staged).as_posix(): binding(path)
              for path in staged.rglob('*') if path.is_file()}
    expected = {row['file']: {'bytes': row['bytes'], 'sha256': row['sha256']} for row in audit['player_files']}
    require(actual == expected and len(expected) == len(audit['player_files']), 'Actual player output differs from audit')


def verify_payload(build, root, payload, components, report, compare_build):
    require(components['format'] == 'picross-pg-build-v1' and
            all(report[key] == value for key, value in components.items()) and
            components['architecture'] == 'windows-x64' and components['signed'] is False,
            'Foreign or unbound embedded game build')
    expected = {'Picross-Game.exe', 'picross-p1.exe', 'picross-p1.pck', 'SPIELANLEITUNG.md',
                'START.txt', 'components.json', 'inventory.json'}
    if compare_build:
        staged = build / 'work/player'
        expected |= {'licenses/' + f.relative_to(staged / 'licenses').as_posix()
                     for f in (staged / 'licenses').rglob('*') if f.is_file()}
        require(set(payload) == expected | {'licenses/WiX.txt'}, 'Unexpected PG MSI payload')
        for name in expected - {'Picross-Game.exe', 'START.txt', 'components.json', 'inventory.json'}:
            require(binding(payload[name]) == binding(staged / name), 'Export member mismatch: ' + name)
    elif not expected <= set(payload) or any(not name.startswith('licenses/') for name in payload.keys() - expected):
        raise RuntimeError('Unexpected PG MSI payload')
    for prefix, name in [('player', 'picross-p1.exe'), ('pck', 'picross-p1.pck')]:
        require(binding(payload[name]) == {k: report[prefix + '_' + k] for k in ('bytes', 'sha256')},
                'Foreign player resource: ' + name)
    for target, digest in GODOT_NOTICES.values():
        require(binding(payload['licenses/' + target])['sha256'] == digest, 'Unbound Godot license: ' + target)
    verify_write_scope(root)


def verify_write_scope(root):
    """Constrain the decompiled MSI write/remove surfaces to the PG product."""
    directories = {node.get('Id'): node for node in root.findall('.//w:Directory', NS)}
    parents = {child.get('Id'): node.get('Id') for node in directories.values()
               for child in node.findall('w:Directory', NS)}
    require(parents['INSTALLFOLDER'] == 'LocalAppDataFolder' and parents['AppMenu'] == 'ProgramMenuFolder'
            and directories['AppMenu'].get('Name') == 'Picross', 'Foreign MSI directory')
    for uid, directory in (('MenuShortcutLink', 'AppMenu'), ('DesktopShortcutLink', 'DesktopFolder')):
        link = directories[directory].find(f'w:Component/w:Shortcut[@Id="{uid}"]', NS)
        require(link is not None and link.get('Target') == '[INSTALLFOLDER]Picross-Game.exe',
                'Shortcut does not target the fixed PG launcher')
    allowed = {'INSTALLFOLDER', 'AppMenu'}
    for directory in parents:
        ancestor = directory
        while ancestor in parents:
            ancestor = parents[ancestor]
            if ancestor == 'INSTALLFOLDER':
                allowed.add(directory)
                break
    require(len(root.findall('.//w:Shortcut', NS)) == 2 and
            all(node.get('Directory') in allowed for node in root.findall('.//w:RemoveFolder', NS)) and
            all(not root.findall('.//w:' + name, NS) for name in
                ('RemoveFile', 'CopyFile', 'MoveFile', 'RemoveRegistryKey', 'RemoveRegistryValue',
                 'ServiceInstall', 'ServiceControl', 'IniFile', 'RemoveIniFile', 'Environment')),
            'Unexpected MSI write/remove operation')
    guard = root.find('.//w:CustomAction[@Id="CheckStopped"]', NS)
    require(guard is not None and guard.get('BinaryKey') == 'Guard' and guard.get('ExeCommand') == '"[INSTALLFOLDER]."',
            'Missing compiled MSI liveness guard')
    action = root.find('.//w:InstallExecuteSequence/w:Custom[@Action="CheckStopped"]', NS)
    require(action is not None and (action.text or '').strip() == '1', 'Guard must also run for upgrade/uninstall')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--expected-commit', required=True)
    parser.add_argument('--compare-build', action='store_true')
    parser.add_argument('--version', default='0.1.1')
    args = parser.parse_args()
    verify(args.build.resolve(), args.output.resolve(), args.expected_commit, compare_build=args.compare_build,
           version=args.version, app=PG)


if __name__ == '__main__':
    main()
