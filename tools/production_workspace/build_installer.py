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

from tools.app_products import PG, PW, PE

NS = 'http://schemas.microsoft.com/wix/2006/wi'
ET.register_namespace('', NS)


def element(parent, tag, **attrs):
    return ET.SubElement(parent, '{' + NS + '}' + tag, attrs)


def wix_source(image, product, guard, *, app=PW):
    root = ET.Element('{' + NS + '}Wix')
    p = element(root, 'Product', Id=product['product_code'], Name=app.title, Language='1031',
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
    element(p, 'Icon', Id='AppIcon', SourceFile=str(app.source / app.icon_resource))
    element(p, 'Property', Id='ARPPRODUCTICON', Value='AppIcon')
    target = element(p, 'Directory', Id='TARGETDIR', Name='SourceDir')
    local = element(target, 'Directory', Id='LocalAppDataFolder')
    install = element(local, 'Directory', Id='INSTALLFOLDER', Name=app.install_directory)
    element(p, 'SetDirectory', Id='INSTALLFOLDER', Value='[LocalAppDataFolder]Programs\\' + app.install_directory)
    directories = {'': install}
    feature = element(p, 'Feature', Id='Application', Title=app.title, Level='1', Absent='disallow')
    import hashlib
    def identifier(prefix, text):
        return prefix + hashlib.sha256(text.encode('utf-8')).hexdigest()[:30]
    for file in sorted(image.rglob('*')):
        if not file.is_file():
            continue
        relative = file.relative_to(image)
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
        element(component, 'File', Id='LauncherExe' if name == app.executable + '.exe' else identifier('F', name), Source=str(file), KeyPath='no')
        element(component, 'RegistryValue', Root='HKCU', Key=app.registry + '\\Installer\\Files',
                Name=identifier('F', name), Type='string', Value=product['version'], KeyPath='yes')
        element(feature, 'ComponentRef', Id=identifier('C', name))
    menu = element(target, 'Directory', Id='ProgramMenuFolder')
    menu = element(menu, 'Directory', Id='AppMenu', Name=app.title)
    desktop = element(target, 'Directory', Id='DesktopFolder')
    for directory, cid in ((menu, 'MenuShortcut'), (desktop, 'DesktopShortcut')):
        component = element(directory, 'Component', Id=cid, Guid='*', Win64='yes')
        if cid == 'DesktopShortcut':
            element(component, 'Condition').text = 'INSTALLDESKTOP=1'
        element(component, 'Shortcut', Id=cid + 'Link', Name=app.title, Target='[INSTALLFOLDER]' + app.executable + '.exe',
                WorkingDirectory='INSTALLFOLDER', Icon='AppIcon', Advertise='no')
        element(component, 'RegistryValue', Root='HKCU', Key=app.registry + '\\Installer', Name=cid,
                Type='integer', Value='1', KeyPath='yes')
        if cid == 'MenuShortcut':
            element(component, 'RemoveFolder', Id='RemoveMenu', On='uninstall')
        element(feature, 'ComponentRef', Id=cid)
    if app == PG:
        # The major upgrade removes the old Settings shortcut with its component.
        # Give the replacement registration its own identity and no shortcut.
        cid = 'ProductRegistration'
        update = element(install, 'Component', Id=cid,
                         Guid=str(uuid.uuid5(uuid.UUID(product['upgrade_code']), cid)), Win64='yes')
        for name, value in (('Version', product['version']), ('ProductCode', '{' + product['product_code'] + '}')):
            element(update, 'RegistryValue', Root='HKCU', Key=app.registry + '\\Installer',
                    Name=name, Type='string', Value=value, KeyPath='yes' if name == 'Version' else 'no')
        element(feature, 'ComponentRef', Id=cid)
    # Only remove directories if empty; no wildcard or recursive deletion.
    component = element(install, 'Component', Id='EmptyFolders',
                        Guid=str(uuid.uuid5(uuid.UUID(product['upgrade_code']), 'EmptyFolders')), Win64='yes')
    element(component, 'RegistryValue', Root='HKCU', Key=app.registry + '\\Installer',
            Name='EmptyFolders', Type='integer', Value='1', KeyPath='yes')
    for name, directory in directories.items():
        element(component, 'RemoveFolder', Id=identifier('R', name), Directory=directory.get('Id'), On='uninstall')
    element(feature, 'ComponentRef', Id='EmptyFolders')
    element(p, 'Binary', Id='Guard', SourceFile=str(guard))
    element(p, 'CustomAction', Id='CheckStopped', BinaryKey='Guard', ExeCommand='"[INSTALLFOLDER]."', Execute='immediate', Return='check')
    sequence = element(p, 'InstallExecuteSequence')
    element(sequence, 'Custom', Action='CheckStopped', Before='InstallValidate').text = '1'
    element(p, 'UIRef', Id='WixUI_Common')
    ui = element(p, 'UI')
    element(ui, 'Error', Id='1722').text = ('App läuft oder Zugriff ist unklar. ' +
        ('Assistent regulär beenden und Produktionsentfernung abwarten. ' if app == PW else
         'Editor regulär beenden und laufende Fachoperation abwarten. ' if app == PE else 'Picross regulär beenden. ') +
        'Dann Installer erneut starten. Kein Prozess wird beendet.')
    element(ui, 'TextStyle', Id='WixUI_Font_Normal', FaceName='Segoe UI', Size='9')
    element(ui, 'TextStyle', Id='WixUI_Font_Bigger', FaceName='Segoe UI', Size='12')
    element(ui, 'TextStyle', Id='WixUI_Font_Title', FaceName='Segoe UI', Size='10', Bold='yes')
    element(p, 'Property', Id='DefaultUIFont', Value='WixUI_Font_Normal')
    for did in ('ErrorDlg', 'FatalError', 'FilesInUse', 'ProgressDlg', 'UserExit', 'ExitDialog'):
        element(ui, 'DialogRef', Id=did)
    element(ui, 'Publish', Dialog='ExitDialog', Control='Finish', Event='EndDialog', Value='Return').text = '1'
    dialog = element(ui, 'Dialog', Id='InstallOptions', Width='370', Height='200', Title='Picross installieren')
    element(dialog, 'Control', Id='Info', Type='Text', X='20', Y='20', Width='330', Height='60', Text=('Installiert nur für diesen Benutzer. ' + ('Git für Windows bleibt erforderlich. ' if app == PW else '') + 'Die unsignierte App enthält private Laufzeit und Lizenzen. Einrichtung und Daten bleiben getrennt erhalten.'))
    element(dialog, 'Control', Id='Desktop', Type='CheckBox', X='20', Y='95', Width='320', Height='18', Property='INSTALLDESKTOP', CheckBoxValue='1', Text='Zusätzlich Desktopverknüpfung anlegen')
    button = element(dialog, 'Control', Id='Install', Type='PushButton', X='205', Y='160', Width='70', Height='18', Default='yes', Text='Installieren')
    element(button, 'Publish', Event='EndDialog', Value='Return').text = '1'
    button = element(dialog, 'Control', Id='Cancel', Type='PushButton', X='280', Y='160', Width='70', Height='18', Cancel='yes', Text='Abbrechen')
    element(button, 'Publish', Event='EndDialog', Value='Exit').text = '1'
    sequence = element(ui, 'InstallUISequence')
    element(sequence, 'Show', Dialog='InstallOptions', Before='ProgressDlg').text = 'NOT Installed AND NOT WIX_DOWNGRADE_DETECTED AND NOT SAMEVERSION'
    return ET.ElementTree(root)


def write_checksum(msi):
    checksum = sha(msi)
    msi.with_name(msi.name + '.sha256').write_text(checksum + '  ' + msi.name + '\n',
                                                 encoding='utf-8', newline='\n')
    return checksum


def run(output, *, version=None, app=PW):
    product = release(version=version, app=app)
    if app == PG:
        from tools.game_app.build import build_player_image
        build_player_image(output, product)
    else:
        build(output, version=version, app=app)  # Private Python runtime, clean source and licenses.
    work = output / 'work'
    archive = work / 'wix.zip'
    urllib.request.urlretrieve(product['wix_url'], archive)
    if sha(archive) != product['wix_sha256']:
        raise RuntimeError('WiX-Download stimmt nicht mit dem gebundenen SHA-256 überein.')
    wix = work / 'wix'
    with zipfile.ZipFile(archive) as z:
        z.extractall(wix)
    compiler = Path(os.environ['SystemRoot']) / 'Microsoft.NET/Framework64/v4.0.30319/csc.exe'
    guard = work / 'Guard.exe'
    image = output / 'dist' / app.executable
    license_path = image / ('licenses' if app == PG else 'LICENSES')
    shutil.copyfile(wix / 'LICENSE.TXT', license_path / 'WiX.txt')
    files = [{'file': f.relative_to(image).as_posix(), 'bytes': f.stat().st_size, 'sha256': sha(f)}
             for f in sorted(image.rglob('*')) if f.is_file() and f.name != 'inventory.json']
    (image / 'inventory.json').write_text(json.dumps({'commit': json.loads((image / 'components.json').read_text(encoding='utf-8'))['commit'],
                                                  'files': files}, indent=2) + '\n', encoding='utf-8')
    payload = work / 'Payload.txt'
    payload.write_text('\n'.join(f.relative_to(image).as_posix() for f in sorted(image.rglob('*')) if f.is_file()) + '\n', encoding='utf-8')
    guard_source = work / 'Guard.cs'
    guard_text = (PACKAGE / 'packaging/Guard.cs').read_text(encoding='utf-8')
    if app != PW:
        guard_text = guard_text.replace('Picross-Produktionsassistent', app.install_directory).replace('PicrossProductionWorkspace', app.state_directory)
    guard_source.write_text(guard_text, encoding='utf-8')
    definitions = ['/define:PG'] if app == PG else []
    subprocess.run([str(compiler), '/nologo', '/codepage:65001', '/target:winexe', '/platform:x64', '/out:' + str(guard),
                    '/resource:' + str(payload) + ',Payload.txt', *definitions, str(guard_source)], check=True)
    portable = output / (app.executable + '-windows-x64.zip')
    if app != PG:
        with zipfile.ZipFile(portable, 'w', zipfile.ZIP_DEFLATED) as archive:
            for file in sorted(image.rglob('*')):
                if file.is_file():
                    archive.write(file, app.executable + '/' + file.relative_to(image).as_posix())
    source = work / 'installer.wxs'
    wix_source(image, product, guard, app=app).write(source, encoding='utf-8', xml_declaration=True)
    obj = work / 'installer.wixobj'
    msi = output / product['filename']
    subprocess.run([str(wix / 'candle.exe'), '-nologo', '-arch', 'x64', '-out', str(obj), str(source)], check=True)
    # ICE91 warns about per-user files in a hypothetical per-machine install;
    # this product is explicitly per-user only. Other ICE validation stays on.
    subprocess.run([str(wix / 'light.exe'), '-nologo', '-sice:ICE91', '-ext', str(wix / 'WixUIExtension.dll'),
                    '-cultures:de-de', '-out', str(msi), str(obj)], check=True)
    checksum = write_checksum(msi)
    start = {PW: PACKAGE / 'START-WINDOWS.txt', PE: PE.source / 'README.md', PG: PG.source / 'START.txt'}
    shutil.copyfile(start[app], output / 'START.txt')
    report = json.loads((output / 'delivery.json').read_text(encoding='utf-8'))
    report.update(msi_file=msi.name, msi_sha256=checksum, msi_bytes=msi.stat().st_size,
                  wix_package=product['wix_package'], wix_sha256=product['wix_sha256'],
                  guard_sha256=sha(guard), guard_compiler_sha256=sha(compiler))
    if app != PG:
        report.update(zip_bytes=portable.stat().st_size, zip_sha256=sha(portable))
    (output / 'delivery.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--version', help='Checked release-plan version, injected without changing sources')
    args = parser.parse_args()
    run(args.output.resolve(), version=args.version)
