"""Manual Actions MSI byte inspection; never installs or changes machine policy."""
import argparse
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile

from .build_windows import ROOT, sha
from .release import release
from .payload import fingerprint
from .update_verifier import production_trust
from .smoke_installer import msi_properties

NS = {'w': 'http://schemas.microsoft.com/wix/2006/wi'}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def verify(build, output, expected_commit, wix_archive=None, compare_build=False, version=None):
    require(re.fullmatch('[0-9a-f]{40}', expected_commit), 'Full expected source SHA required')
    require(not output.exists(), 'Use a new dedicated inspection directory')
    output.mkdir(parents=True)
    report = json.loads((build / 'delivery.json').read_text(encoding='utf-8'))
    product = release(version=version)
    require(report['commit'] == expected_commit, 'Unexpected build source')
    for key in ('version', 'product_code', 'upgrade_code'):
        require(report[key] == product[key], 'Release mismatch: ' + key)
    require(report['msi_file'] == product['filename'], 'Unexpected MSI filename')
    msi = build / product['filename']
    require(msi.stat().st_size == report['msi_bytes'] and sha(msi) == report['msi_sha256'], 'MSI byte mismatch')
    require((build / (msi.name + '.sha256')).read_text(encoding='utf-8') ==
            report['msi_sha256'] + '  ' + msi.name + '\n', 'Checksum file mismatch')
    if compare_build:
        inputs = fingerprint(ROOT)
        require(report['payload_fingerprint'] == inputs['sha256'], 'Source fingerprint mismatch')
        require(json.loads((build / 'inputs.json').read_bytes()) == inputs, 'Input inventory mismatch')
        audit = json.loads((build / 'input-audit.json').read_bytes())
        require(audit['fingerprint'] == inputs['sha256'] and audit['repository_inputs'], 'Frozen input audit missing')
        portable = build / 'Picross-Start-windows-x64.zip'
        require(portable.stat().st_size == report['zip_bytes'] and sha(portable) == report['zip_sha256'], 'ZIP byte mismatch')
    properties = msi_properties(msi)  # Actual Windows Installer database, not sidecar metadata.
    for field, key in (('ProductVersion', 'version'), ('ProductCode', 'product_code'), ('UpgradeCode', 'upgrade_code')):
        require(properties[field].strip('{}') == product[key], 'MSI property mismatch: ' + field)
    require(not properties.get('ALLUSERS'), 'MSI is not per-user')
    wix_archive = wix_archive or build / 'work/wix.zip'
    require(report['wix_sha256'] == product['wix_sha256'] and
            sha(wix_archive) == product['wix_sha256'], 'Unbound WiX inspector')
    app = build / 'dist/Picross-Start'
    require(not compare_build or app.is_dir(), 'Missing original build payload')
    with tempfile.TemporaryDirectory(prefix='unpacked-', dir=output) as temporary:
        work = Path(temporary)
        extracted = work / 'bytes'
        source = work / 'installer.wxs'
        wix = work / 'wix'
        with zipfile.ZipFile(wix_archive) as archive:
            archive.extractall(wix)
        subprocess.run([str(wix / 'dark.exe'), '-nologo', '-x', str(extracted),
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
        seen = set()

        def visit(directory, prefix):
            for node in directory.findall('w:Component/w:File', NS):
                relative = prefix / node.get('Name')
                require(not relative.is_absolute() and not any(p in ('..', '.') or ':' in p or '\\' in p
                                                              for p in relative.parts), 'Unsafe MSI member')
                file = Path(node.get('Source')).resolve()
                require(file.is_relative_to(extracted.resolve()) and file.is_file(), 'Missing extracted MSI member')
                key = relative.as_posix().casefold()
                require(key not in seen, 'Duplicate MSI member')
                seen.add(key)
                payload[relative.as_posix()] = file
            for child in directory.findall('w:Directory', NS):
                visit(child, prefix / child.get('Name'))

        visit(install, PurePosixPath())
        require(len(payload) == len(root.findall('.//w:File', NS)), 'Files outside program payload')
        inventory_file = payload['inventory.json']
        if compare_build:
            require(inventory_file.read_bytes() == (app / 'inventory.json').read_bytes(), 'Embedded inventory differs from build')
        inventory = json.loads(inventory_file.read_text(encoding='utf-8'))
        rows = inventory['files']
        require(inventory['commit'] == expected_commit, 'Inventory source mismatch')
        require(len({r['file'] for r in rows}) == len(rows) and
                set(payload) == {r['file'] for r in rows} | {'inventory.json'}, 'Incomplete or extra MSI payload')
        for row in rows:
            file = payload[row['file']]
            require(file.stat().st_size == row['bytes'] and sha(file) == row['sha256'],
                    'MSI payload differs from inventory: ' + row['file'])
            if compare_build:
                original = (app / row['file']).resolve()
                require(original.is_relative_to(app.resolve()) and sha(original) == row['sha256'],
                        'MSI payload differs from original build: ' + row['file'])
        components = json.loads(payload['components.json'].read_text(encoding='utf-8'))
        for key in ('commit', 'version', 'product_code', 'upgrade_code', 'payload_fingerprint', 'architecture', 'python',
                    'components', 'runtime_components', 'resources', 'signed'):
            require(components[key] == report[key], 'Embedded components mismatch: ' + key)
        require(sha(payload['Picross-Start.exe']) == report['exe_sha256'], 'Embedded EXE mismatch')
        for name in ('release.json', 'update-trust.json'):
            relative = '_internal/tools/production_workspace/' + name
            require(sha(payload[relative]) == components['resources'][name] and
                    payload[relative].read_bytes() == (ROOT / 'tools/production_workspace' / name).read_bytes(),
                    'Packaged public trust/product identity mismatch: ' + name)
        production_trust()
        extensions = [name for name in payload if name.endswith('.pyd')]
        require(any(name.endswith('cryptography/hazmat/bindings/_rust.pyd') for name in extensions) and
                any(Path(name).name.startswith('_cffi_backend.') for name in extensions),
                'MSI lacks native cryptography extensions')
        require(payload['Picross-Start.exe'].stat().st_size == report['exe_bytes'], 'Embedded EXE size mismatch')
        # Inspect the actual PE version resource, independently of sidecar JSON.
        import pefile
        with pefile.PE(str(payload['Picross-Start.exe'])) as pe:
            fixed = pe.VS_FIXEDFILEINFO[0]
        expected = tuple(map(int, product['version'].split('.'))) + (0,)
        for prefix in ('FileVersion', 'ProductVersion'):
            ms, ls = getattr(fixed, prefix + 'MS'), getattr(fixed, prefix + 'LS')
            actual = (ms >> 16, ms & 65535, ls >> 16, ls & 65535)
            require(actual == expected, 'EXE version resource mismatch')
        require(payload['START.txt'].read_bytes() == (build / 'START.txt').read_bytes(), 'Start instructions mismatch')
        guard = root.find('.//w:Binary[@Id="Guard"]', NS)
        guard_file = Path(guard.get('SourceFile')).resolve()
        require(guard_file.is_relative_to(extracted.resolve()) and sha(guard_file) == report['guard_sha256'],
                'Embedded safety guard mismatch')
        licenses = [r['file'] for r in rows if r['file'].startswith('LICENSES/')]
        require({'LICENSES/Python.txt', 'LICENSES/WiX.txt'}.issubset(licenses), 'Missing license originals')
        for package in ('cryptography', 'cffi', 'pycparser'):
            require(any(name.startswith('LICENSES/' + package + '/') for name in licenses), 'Missing crypto license: ' + package)
        require('LICENSES/OpenSSL-4.0.3.txt' in licenses, 'Missing cryptography OpenSSL license')
    result = {'format': 'picross-installer-inspection-v1', 'commit': expected_commit, 'version': report['version'],
              'payload_fingerprint': report['payload_fingerprint'],
              'msi_sha256': report['msi_sha256'], 'msi_bytes': report['msi_bytes'],
              'product_code': product['product_code'], 'upgrade_code': product['upgrade_code'],
              'inventory_files': len(rows), 'license_files': len(licenses), 'compared_to_build': compare_build,
              'limits': 'Actual MSI database and all unpacked bytes verified. No installation; T02 requires a non-elevated Windows client.'}
    (output / 'result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--expected-commit', required=True)
    parser.add_argument('--wix-archive', type=Path, help='Hash-pinned WiX archive; defaults to build/work/wix.zip')
    parser.add_argument('--compare-build', action='store_true', help='Also compare to original dist payload (required in Actions)')
    parser.add_argument('--version', help='Expected planned publication version')
    args = parser.parse_args()
    verify(args.build.resolve(), args.output.resolve(), args.expected_commit, args.wix_archive, args.compare_build, args.version)
