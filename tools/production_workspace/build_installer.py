"""Explicit Windows-only product build. Never imported/invoked by Package CI."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
import uuid

from .build_windows import build, sha, ROOT, PACKAGE
from .release import release

NS = 'http://schemas.microsoft.com/wix/2006/wi'
ET.register_namespace('', NS)


def element(parent, tag, **attrs):
    return ET.SubElement(parent, '{' + NS + '}' + tag, attrs)


def wix_source(app, product, guard):
    root = ET.Element('{' + NS + '}Wix')
    p = element(root, 'Product', Id=product['product_code'], Name='Picross-Produktionsassistent', Language='1031',
                Version=product['version'], Manufacturer='venomenon328', UpgradeCode=product['upgrade_code'])
    element(p, 'Package', InstallerVersion='500', Compressed='yes', InstallScope='perUser', InstallPrivileges='limited', Platform='x64')
    element(p, 'MediaTemplate', EmbedCab='yes')
    element(p, 'MajorUpgrade', Schedule='afterInstallInitialize', DowngradeErrorMessage='Eine neuere Picross-Version ist bereits installiert.')
    upgrade = element(p, 'Upgrade', Id=product['upgrade_code'])
    element(upgrade, 'UpgradeVersion', Minimum=product['version'], Maximum=product['version'], IncludeMinimum='yes',
            IncludeMaximum='yes', OnlyDetect='yes', Property='SAMEVERSION')
    element(p, 'Condition', Message='Diese Version ist bereits installiert. Für Änderungen eine neuere Produktversion verwenden.').text = 'NOT SAMEVERSION AND (NOT Installed OR REMOVE="ALL" OR UPGRADINGPRODUCTCODE)'
    element(p, 'Property', Id='MSIRESTARTMANAGERCONTROL', Value='Disable')
    element(p, 'Property', Id='REBOOT', Value='ReallySuppress')
    element(p, 'Property', Id='ARPNOMODIFY', Value='1')
    element(p, 'Property', Id='ARPNOREPAIR', Value='1')
    element(p, 'Property', Id='INSTALLDESKTOP', Secure='yes')
    element(p, 'Icon', Id='AppIcon', SourceFile=str(PACKAGE / 'assets/launcher.ico'))
    element(p, 'Property', Id='ARPPRODUCTICON', Value='AppIcon')
    target = element(p, 'Directory', Id='TARGETDIR', Name='SourceDir')
    local = element(target, 'Directory', Id='LocalAppDataFolder')
    programs = element(local, 'Directory', Id='Programs', Name='Programs')
    install = element(programs, 'Directory', Id='INSTALLFOLDER', Name='Picross-Produktionsassistent')
    directories = {'': install}
    feature = element(p, 'Feature', Id='Application', Title='Produktionsassistent', Level='1', Absent='disallow')
    import hashlib
    def identifier(prefix, text):
        return prefix + hashlib.sha256(text.encode('utf-8')).hexdigest()[:30]
    for file in sorted(app.rglob('*')):
        if not file.is_file():
            continue
        relative = file.relative_to(app)
        for directory in reversed(relative.parents):
            name = directory.as_posix()
            if name == '.' or name in directories:
                continue
            parent = directory.parent.as_posix()
            directories[name] = element(directories['' if parent == '.' else parent], 'Directory', Id=identifier('D', name), Name=directory.name)
        parent = relative.parent.as_posix()
        name = relative.as_posix()
        component = element(directories['' if parent == '.' else parent], 'Component', Id=identifier('C', name),
                            Guid=str(uuid.uuid5(uuid.UUID(product['upgrade_code']), name)), Win64='yes')
        element(component, 'File', Id='LauncherExe' if name == 'Picross-Start.exe' else identifier('F', name), Source=str(file), KeyPath='no')
        element(component, 'RegistryValue', Root='HKCU', Key='Software\\PicrossProductionWorkspace\\Installer\\Files',
                Name=identifier('F', name), Type='string', Value=product['version'], KeyPath='yes')
        element(feature, 'ComponentRef', Id=identifier('C', name))
    menu = element(target, 'Directory', Id='ProgramMenuFolder')
    menu = element(menu, 'Directory', Id='AppMenu', Name='Picross-Produktionsassistent')
    desktop = element(target, 'Directory', Id='DesktopFolder')
    for directory, cid in ((menu, 'MenuShortcut'), (desktop, 'DesktopShortcut')):
        component = element(directory, 'Component', Id=cid, Guid='*', Win64='yes')
        if cid == 'DesktopShortcut':
            element(component, 'Condition').text = 'INSTALLDESKTOP=1'
        element(component, 'Shortcut', Id=cid + 'Link', Name='Picross-Produktionsassistent', Target='[INSTALLFOLDER]Picross-Start.exe',
                WorkingDirectory='INSTALLFOLDER', Icon='AppIcon', Advertise='no')
        element(component, 'RegistryValue', Root='HKCU', Key='Software\\PicrossProductionWorkspace\\Installer', Name=cid,
                Type='integer', Value='1', KeyPath='yes')
        if cid == 'MenuShortcut':
            element(component, 'RemoveFolder', Id='RemoveMenu', On='uninstall')
        element(feature, 'ComponentRef', Id=cid)
    # Only remove directories if empty; no wildcard or recursive deletion.
    component = element(install, 'Component', Id='EmptyFolders',
                        Guid=str(uuid.uuid5(uuid.UUID(product['upgrade_code']), 'EmptyFolders')), Win64='yes')
    element(component, 'RegistryValue', Root='HKCU', Key='Software\\PicrossProductionWorkspace\\Installer',
            Name='EmptyFolders', Type='integer', Value='1', KeyPath='yes')
    for name, directory in directories.items():
        element(component, 'RemoveFolder', Id=identifier('R', name), Directory=directory.get('Id'), On='uninstall')
    element(feature, 'ComponentRef', Id='EmptyFolders')
    element(p, 'Binary', Id='Guard', SourceFile=str(guard))
    element(p, 'CustomAction', Id='CheckStopped', BinaryKey='Guard', DllEntry='Check', Execute='immediate', Return='check')
    sequence = element(p, 'InstallExecuteSequence')
    element(sequence, 'Custom', Action='CheckStopped', Before='InstallInitialize').text = '1'
    element(p, 'UIRef', Id='WixUI_ProgressOnly')
    ui = element(p, 'UI')
    dialog = element(ui, 'Dialog', Id='InstallOptions', Width='370', Height='200', Title='Picross installieren')
    element(dialog, 'Control', Id='Info', Type='Text', X='20', Y='20', Width='330', Height='60', Text='Installiert nur für diesen Benutzer. Git für Windows bleibt erforderlich. Die unsignierte App enthält private Laufzeit und Lizenzen. Einrichtung und Produktionsdaten bleiben getrennt erhalten.')
    element(dialog, 'Control', Id='Desktop', Type='CheckBox', X='20', Y='95', Width='320', Height='18', Property='INSTALLDESKTOP', CheckBoxValue='1', Text='Zusätzlich Desktopverknüpfung anlegen')
    button = element(dialog, 'Control', Id='Install', Type='PushButton', X='205', Y='160', Width='70', Height='18', Default='yes', Text='Installieren')
    element(button, 'Publish', Event='EndDialog', Value='Return').text = '1'
    button = element(dialog, 'Control', Id='Cancel', Type='PushButton', X='280', Y='160', Width='70', Height='18', Cancel='yes', Text='Abbrechen')
    element(button, 'Publish', Event='EndDialog', Value='Exit').text = '1'
    sequence = element(ui, 'InstallUISequence')
    element(sequence, 'Show', Dialog='InstallOptions', Before='ExecuteAction').text = 'NOT Installed AND NOT WIX_DOWNGRADE_DETECTED AND NOT SAMEVERSION'
    return ET.ElementTree(root)


def run(output):
    product = release()
    build(output)  # Pins interpreter, components, clean commit, onedir and licenses.
    work = output / 'work'
    archive = work / 'wix.zip'
    urllib.request.urlretrieve(product['wix_url'], archive)
    if sha(archive) != product['wix_sha256']:
        raise RuntimeError('WiX-Download stimmt nicht mit dem gebundenen SHA-256 überein.')
    wix = work / 'wix'
    with zipfile.ZipFile(archive) as z:
        z.extractall(wix)
    sdk = wix / 'sdk'
    compiler = Path(os.environ['SystemRoot']) / 'Microsoft.NET/Framework64/v4.0.30319/csc.exe'
    assembly = work / 'Guard.dll'
    subprocess.run([str(compiler), '/nologo', '/target:library', '/platform:x64', '/out:' + str(assembly),
                    '/reference:' + str(sdk / 'Microsoft.Deployment.WindowsInstaller.dll'), str(PACKAGE / 'packaging/Guard.cs')], check=True)
    guard = work / 'Guard.CA.dll'
    subprocess.run([str(sdk / 'MakeSfxCA.exe'), str(guard), str(sdk / 'x64/SfxCA.dll'), str(assembly),
                    str(sdk / 'Microsoft.Deployment.WindowsInstaller.dll'), str(PACKAGE / 'packaging/CustomAction.config')], check=True)
    app = output / 'dist/Picross-Start'
    shutil.copyfile(wix / 'LICENSE.TXT', app / 'LICENSES/WiX.txt')
    files = [{'file': f.relative_to(app).as_posix(), 'bytes': f.stat().st_size, 'sha256': sha(f)}
             for f in sorted(app.rglob('*')) if f.is_file() and f.name != 'inventory.json']
    (app / 'inventory.json').write_text(json.dumps({'commit': json.loads((app / 'components.json').read_text())['commit'],
                                                  'files': files}, indent=2) + '\n', encoding='utf-8')
    portable = output / 'Picross-Start-windows-x64.zip'
    with zipfile.ZipFile(portable, 'w', zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(app.rglob('*')):
            if file.is_file():
                archive.write(file, 'Picross-Start/' + file.relative_to(app).as_posix())
    source = work / 'installer.wxs'
    wix_source(app, product, guard).write(source, encoding='utf-8', xml_declaration=True)
    obj = work / 'installer.wixobj'
    msi = output / product['filename']
    subprocess.run([str(wix / 'candle.exe'), '-nologo', '-arch', 'x64', '-out', str(obj), str(source)], check=True)
    subprocess.run([str(wix / 'light.exe'), '-nologo', '-ext', str(wix / 'WixUIExtension.dll'),
                    '-cultures:de-de', '-out', str(msi), str(obj)], check=True)
    checksum = sha(msi)
    (output / (msi.name + '.sha256')).write_text(checksum + '  ' + msi.name + '\n', encoding='utf-8')
    shutil.copyfile(PACKAGE / 'START-WINDOWS.txt', output / 'START.txt')
    report = json.loads((output / 'delivery.json').read_text())
    report.update(msi_file=msi.name, msi_sha256=checksum, msi_bytes=msi.stat().st_size,
                  wix_package=product['wix_package'], wix_sha256=product['wix_sha256'],
                  zip_bytes=portable.stat().st_size, zip_sha256=sha(portable))
    (output / 'delivery.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    run(parser.parse_args().output.resolve())
