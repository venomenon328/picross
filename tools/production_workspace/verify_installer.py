"""Manual Actions MSI byte inspection; never installs or changes machine policy."""
import argparse
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET

from .build_windows import ROOT, sha
from .release import release
from .smoke_installer import msi_properties

NS = {'w': 'http://schemas.microsoft.com/wix/2006/wi'}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def verify(build, output, expected_commit):
    require(re.fullmatch('[0-9a-f]{40}', expected_commit), 'Full expected source SHA required')
    require(not output.exists(), 'Use a new dedicated inspection directory')
    output.mkdir(parents=True)
    report = json.loads((build / 'delivery.json').read_text(encoding='utf-8'))
    product = release()
    require(report['commit'] == expected_commit, 'Unexpected build source')
    for key in ('version', 'product_code', 'upgrade_code'):
        require(report[key] == product[key], 'Release mismatch: ' + key)
    require(report['msi_file'] == product['filename'], 'Unexpected MSI filename')
    msi = build / product['filename']
    require(msi.stat().st_size == report['msi_bytes'] and sha(msi) == report['msi_sha256'], 'MSI byte mismatch')
    require((build / (msi.name + '.sha256')).read_text(encoding='utf-8') ==
            report['msi_sha256'] + '  ' + msi.name + '\n', 'Checksum file mismatch')
    properties = msi_properties(msi)  # Actual Windows Installer database, not sidecar metadata.
    for field, key in (('ProductVersion', 'version'), ('ProductCode', 'product_code'), ('UpgradeCode', 'upgrade_code')):
        require(properties[field].strip('{}') == product[key], 'MSI property mismatch: ' + field)
    require(not properties.get('ALLUSERS'), 'MSI is not per-user')
    require(report['wix_sha256'] == product['wix_sha256'] and
            sha(build / 'work/wix.zip') == product['wix_sha256'], 'Unbound WiX inspector')
    app = build / 'dist/Picross-Start'
    with tempfile.TemporaryDirectory(prefix='unpacked-', dir=output) as temporary:
        work = Path(temporary)
        extracted = work / 'bytes'
        source = work / 'installer.wxs'
        subprocess.run([str(build / 'work/wix/dark.exe'), '-nologo', '-x', str(extracted),
                        '-o', str(source), str(msi)], check=True)
        root = ET.parse(source).getroot()
        package = root.find('.//w:Package', NS)
        require(package.get('Platform') == 'x64' and package.get('InstallPrivileges') == 'limited',
                'Unexpected MSI architecture/privileges')
        require(all(node.get('Root') == 'HKCU' for node in root.findall('.//w:RegistryValue', NS)),
                'Unexpected machine registry payload')
        install = root.find('.//w:Directory[@Id="INSTALLFOLDER"]', NS)
        require(install is not None, 'Missing program directory')
        payload = {}

        def visit(directory, prefix):
            for node in directory.findall('w:Component/w:File', NS):
                relative = prefix / node.get('Name')
                require(not relative.is_absolute() and not any(p in ('..', '.') or ':' in p or '\\' in p
                                                              for p in relative.parts), 'Unsafe MSI member')
                file = Path(node.get('Source')).resolve()
                require(file.is_relative_to(extracted.resolve()) and file.is_file(), 'Missing extracted MSI member')
                require(relative.as_posix().casefold() not in {p.casefold() for p in payload}, 'Duplicate MSI member')
                payload[relative.as_posix()] = file
            for child in directory.findall('w:Directory', NS):
                visit(child, prefix / child.get('Name'))

        visit(install, PurePosixPath())
        require(len(payload) == len(root.findall('.//w:File', NS)), 'Files outside program payload')
        inventory_file = payload['inventory.json']
        require(inventory_file.read_bytes() == (app / 'inventory.json').read_bytes(), 'Embedded inventory differs from build')
        inventory = json.loads(inventory_file.read_text(encoding='utf-8'))
        rows = inventory['files']
        require(inventory['commit'] == expected_commit, 'Inventory source mismatch')
        require(len({r['file'] for r in rows}) == len(rows) and
                set(payload) == {r['file'] for r in rows} | {'inventory.json'}, 'Incomplete or extra MSI payload')
        for row in rows:
            file = payload[row['file']]
            original = (app / row['file']).resolve()
            require(original.is_relative_to(app.resolve()), 'Unsafe inventory path')
            require(file.stat().st_size == row['bytes'] and sha(file) == row['sha256'] and
                    sha(original) == row['sha256'], 'MSI payload differs from inventory/build: ' + row['file'])
        components = json.loads(payload['components.json'].read_text(encoding='utf-8'))
        for key in ('commit', 'version', 'product_code', 'upgrade_code', 'architecture', 'python',
                    'components', 'runtime_components', 'resources', 'signed'):
            require(components[key] == report[key], 'Embedded components mismatch: ' + key)
        require(sha(payload['Picross-Start.exe']) == report['exe_sha256'], 'Embedded EXE mismatch')
        require(payload['START.txt'].read_bytes() == (build / 'START.txt').read_bytes(), 'Start instructions mismatch')
        guard = root.find('.//w:Binary[@Id="Guard"]', NS)
        guard_file = Path(guard.get('SourceFile')).resolve()
        require(guard_file.is_relative_to(extracted.resolve()) and sha(guard_file) == report['guard_sha256'],
                'Embedded safety guard mismatch')
        licenses = [r['file'] for r in rows if r['file'].startswith('LICENSES/')]
        require({'LICENSES/Python.txt', 'LICENSES/WiX.txt'}.issubset(licenses), 'Missing license originals')
    result = {'format': 'picross-installer-inspection-v1', 'commit': expected_commit, 'version': report['version'],
              'msi_sha256': report['msi_sha256'], 'msi_bytes': report['msi_bytes'],
              'product_code': product['product_code'], 'upgrade_code': product['upgrade_code'],
              'inventory_files': len(rows), 'license_files': len(licenses),
              'limits': 'Actual MSI database and all unpacked bytes verified. No installation; T02 requires a non-elevated Windows client.'}
    (output / 'result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--expected-commit', required=True)
    args = parser.parse_args()
    verify(args.build.resolve(), args.output.resolve(), args.expected_commit)
