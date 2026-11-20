"""Read the real PG MSI tables and extracted bytes. No installation."""
import argparse
import json
from pathlib import Path

from tools import p1_preflight as toolchain
from tools.app_products import PG
from tools.msi_database import msi_rows
from tools.production_workspace.update_verifier import production_trust
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
            'project.binary' in audit['exported_resources'] and
            audit['export'] == {'preset': 'P1 Windows x86_64', 'mode': 'debug', 'app_name': 'picross · P1'} and
            toolchain.sha256_file(build / 'input-audit.json') == report['export_audit_sha256'],
            'Unbound regular Windows export audit')
    staged = build / 'work/player'
    actual = {path.relative_to(staged).as_posix(): binding(path)
              for path in staged.rglob('*') if path.is_file()}
    expected = {row['file']: {'bytes': row['bytes'], 'sha256': row['sha256']} for row in audit['player_files']}
    require(actual == expected and len(expected) == len(audit['player_files']), 'Actual player output differs from audit')


def verify_payload(build, root, payload, components, report, compare_build):
    require(components['format'] == 'picross-pg-build-v2' and
            all(report[key] == value for key, value in components.items()) and
            components['architecture'] == 'windows-x64' and components['signed'] is False,
            'Foreign or unbound embedded game build')
    base = '_internal/' + PG.package + '/'
    expected = {'Picross-Game.exe', 'picross-p1.exe', 'picross-p1.pck', 'SPIELANLEITUNG.md',
                'START.txt', 'components.json', 'inventory.json'}
    require(expected <= set(payload) and
            all(name.startswith(('_internal/', 'licenses/')) for name in payload.keys() - expected),
            'Unexpected PG MSI payload')
    require(payload[base + 'build.json'].read_bytes() == payload['components.json'].read_bytes() and
            binding(payload['Picross-Game.exe']) == {k: report['exe_' + k] for k in ('bytes', 'sha256')},
            'Unbound PG frozen build or executable')
    for name in ('release.json', 'update-trust.json', PG.icon_resource):
        require(payload[base + name].read_bytes() == (PG.source / name).read_bytes() and
                binding(payload[base + name])['sha256'] == components['resources'][name],
                'Foreign PG resource: ' + name)
    production_trust(app=PG)
    require(binding(payload[base + 'UpdateHelper.exe'])['sha256'] == components['resources']['UpdateHelper.exe'],
            'Unbound PG helper')
    require(not any('/puzzle_editor/' in name or '/puzzle_production/' in name or '/PIL/' in name
                    for name in payload), 'PG includes another app or production algorithm')
    require(all(any(name.startswith(prefix) for name in payload) for prefix in (
                'licenses/Python.txt', 'licenses/PyInstaller/', 'licenses/cryptography/',
                'licenses/cffi/', 'licenses/pycparser/', 'licenses/tcl8.6-', 'licenses/tk8.6-',
                'licenses/OpenSSL-4.0.3.txt')), 'Missing PG runtime license')
    if compare_build:
        staged = build / 'work/player'
        for file in staged.rglob('*'):
            if file.is_file() and file.name != 'picross-p1.console.exe':
                require(binding(payload[file.relative_to(staged).as_posix()]) == binding(file),
                        'Export member mismatch: ' + file.name)
        frozen = build / 'frozen-audit.json'
        audit = json.loads(frozen.read_bytes())
        inputs = json.loads((build / 'inputs.json').read_bytes())
        require(binding(frozen)['sha256'] == report['frozen_audit_sha256'] and
                audit['fingerprint'] == report['payload_fingerprint'] and
                set(audit['repository_inputs']) <= {row['file'] for row in inputs['files']},
                'Unbound frozen input audit')
        native = [{'file': name, **binding(file)} for name, file in sorted(payload.items())
                  if name.startswith('_internal/') and Path(name).suffix.lower() in ('.dll', '.pyd', '.exe')]
        require({row['file']: row for row in native} ==
                {row['file']: row for row in audit['native_inventory']},
                'MSI native inventory differs from the frozen build')
    for prefix, name in [('player', 'picross-p1.exe'), ('pck', 'picross-p1.pck')]:
        require(binding(payload[name]) == {k: report[prefix + '_' + k] for k in ('bytes', 'sha256')},
                'Foreign player resource: ' + name)
    for target, digest in GODOT_NOTICES.values():
        require(binding(payload['licenses/' + target])['sha256'] == digest, 'Unbound Godot license: ' + target)
    verify_write_scope(root)
    verify_database(build / report['msi_file'])


def verify_write_scope(root):
    """Constrain the decompiled MSI write/remove surfaces to the PG product."""
    directories = {node.get('Id'): node for node in root.findall('.//w:Directory', NS)}
    parents = {child.get('Id'): node.get('Id') for node in directories.values()
               for child in node.findall('w:Directory', NS)}
    require(parents['INSTALLFOLDER'] == 'LocalAppDataFolder' and parents['AppMenu'] == 'ProgramMenuFolder'
            and directories['AppMenu'].get('Name') == 'Picross', 'Foreign MSI directory')
    shortcuts = [('MenuShortcutLink', 'AppMenu', 'Picross'),
                 ('DesktopShortcutLink', 'DesktopFolder', 'Picross'),
                 ('UpdateSettingsLink', 'AppMenu', 'Picross – Update-Einstellungen')]
    for uid, directory, name in shortcuts:
        link = directories[directory].find(f'w:Component/w:Shortcut[@Id="{uid}"]', NS)
        require(link is not None and link.get('Name') == name and link.get('WorkingDirectory') == 'INSTALLFOLDER'
                and link.get('Icon') == 'AppIcon',
                'Unexpected PG shortcut location or name')
    allowed = {'INSTALLFOLDER', 'AppMenu'}
    for directory in parents:
        ancestor = directory
        while ancestor in parents:
            ancestor = parents[ancestor]
            if ancestor == 'INSTALLFOLDER':
                allowed.add(directory)
                break
    require(len(root.findall('.//w:Shortcut', NS)) == 3 and
            all(node.get('Directory') in allowed for node in root.findall('.//w:RemoveFolder', NS)) and
            all(not root.findall('.//w:' + name, NS) for name in
                ('RemoveFile', 'CopyFile', 'MoveFile', 'RemoveRegistryKey', 'RemoveRegistryValue',
                 'ServiceInstall', 'ServiceControl', 'IniFile', 'RemoveIniFile', 'Environment')),
            'Unexpected MSI write/remove operation')
    require({node.get('Id') for node in root.findall('.//w:CustomAction', NS)} ==
            {'SetINSTALLFOLDER', 'CheckStopped'}, 'Unexpected MSI custom action')
    redirect = root.find('.//w:CustomAction[@Id="SetINSTALLFOLDER"]', NS)
    require(redirect.get('Property') == 'INSTALLFOLDER' and
            redirect.get('Value') == r'[LocalAppDataFolder]Programs\PicrossGame', 'Foreign MSI target')
    for prop, value in [('REBOOT', 'ReallySuppress'), ('MSIRESTARTMANAGERCONTROL', 'Disable')]:
        node = root.find(f'.//w:Property[@Id="{prop}"]', NS)
        require(node is not None and node.get('Value') == value, 'Unexpected MSI restart policy')
    guard = root.find('.//w:CustomAction[@Id="CheckStopped"]', NS)
    require(guard is not None and guard.get('BinaryKey') == 'Guard' and guard.get('ExeCommand') == '"[INSTALLFOLDER]."',
            'Missing compiled MSI liveness guard')
    action = root.find('.//w:InstallExecuteSequence/w:Custom[@Action="CheckStopped"]', NS)
    require(action is not None and (action.text or '').strip() == '1' and action.get('Before') == 'InstallValidate',
            'Guard must run before upgrade/uninstall changes')


def verify_database(msi):
    # Dark treats formatted MSI shortcut targets as advertised, so read the
    # authoritative Shortcut table for the target/arguments.
    shortcuts = msi_rows(msi, 'Shortcut', ('Shortcut', 'Directory_', 'Target', 'Arguments'))
    require(sorted(shortcuts) == [
        ['DesktopShortcutLink', 'DesktopFolder', '[INSTALLFOLDER]Picross-Game.exe', ''],
        ['MenuShortcutLink', 'AppMenu', '[INSTALLFOLDER]Picross-Game.exe', ''],
        ['UpdateSettingsLink', 'AppMenu', '[INSTALLFOLDER]Picross-Game.exe', '--update-settings'],
    ], 'MSI shortcut target/arguments mismatch')


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
