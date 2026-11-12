"""Manual P4-T02 only: real per-user MSI lifecycle using exclusively synthetic data."""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import time
import winreg

from .build_windows import ROOT, sha
from .instance import StateLock, control
from .repository import configure
from .release import version_tuple
from .smoke_windows import wait_for
from .sources import git


def msi_properties(msi):
    # Windows Installer COM queries the real binary, not a sidecar report.
    command = r'''$ErrorActionPreference='Stop'; $i=New-Object -ComObject WindowsInstaller.Installer; $d=$i.OpenDatabase($env:P4_MSI,0); $v=$d.OpenView('SELECT `Property`, `Value` FROM `Property`'); $v.Execute(); $p=@{}; while($r=$v.Fetch()) {$p[$r.StringData(1)]=$r.StringData(2)}; $p | ConvertTo-Json -Compress'''
    return json.loads(subprocess.check_output(['powershell.exe', '-NoProfile', '-Command', command],
                                             env={**os.environ, 'P4_MSI': str(msi)}, text=True))


def smoke(build, output):
    if os.name != 'nt' or ctypes.windll.shell32.IsUserAnAdmin():
        raise RuntimeError('Installerprobe benötigt einen nicht erhöhten Windows-Testbenutzer.')
    if output.exists():
        raise RuntimeError('Neuen eigenen Smokeordner wählen.')
    output.mkdir(parents=True)
    report = json.loads((build / 'delivery.json').read_text())
    msi = build / report['msi_file']
    properties = msi_properties(msi)
    if (sha(msi) != report['msi_sha256'] or properties['ProductVersion'] != report['version'] or
            properties['ProductCode'].strip('{}') != report['product_code'] or
            properties['UpgradeCode'].strip('{}') != report['upgrade_code']):
        raise RuntimeError('MSI-Bytes/Identitäten stimmen nicht mit Lieferreport überein.')
    installed = Path(os.environ['LOCALAPPDATA']) / 'Programs/Picross-Produktionsassistent'
    arp_root = r'Software\Microsoft\Windows\CurrentVersion\Uninstall'
    def registered(code):
        try:
            return winreg.OpenKey(winreg.HKEY_CURRENT_USER, arp_root + '\\{' + code + '}')
        except FileNotFoundError:
            return None
    if installed.exists() or registered(report['product_code']):
        raise RuntimeError('Bestehende echte Installation bleibt geschützt; frisches Testprofil verwenden.')
    calls, children = [], []
    installed_code = None
    def execute(target, action='/i', success=True, **props):
        logfile = output / ('msi-' + str(len(calls)) + '.log')
        args = ['msiexec.exe', action, str(target), '/qn', '/norestart', '/l*v', str(logfile),
                *[k + '=' + v for k, v in props.items()]]
        process = subprocess.run(args, timeout=180, creationflags=subprocess.CREATE_NO_WINDOW)
        calls.append({'action': action, 'target': Path(str(target)).name, 'exit': process.returncode, 'log': logfile.name})
        if (process.returncode == 0) != success:
            raise RuntimeError('Unerwarteter MSI-Exitcode ' + str(process.returncode) + '; siehe ' + str(logfile))
    def verify_inventory():
        inventory = json.loads((installed / 'inventory.json').read_text())
        for row in inventory['files']:
            file = installed / row['file']
            if file.stat().st_size != row['bytes'] or sha(file) != row['sha256']:
                raise RuntimeError('Installiertes Dateiinventar nicht bytegleich: ' + row['file'])
        return inventory
    from tools.test_production_workspace import current_fixture, commit
    repo = output / 'Daten ohne Code ä'; repo.mkdir()
    git(repo, 'init', '-q', '-b', 'main')
    current_fixture(repo, output / 'Quellen'); commit(repo)
    git(repo, 'branch', 'content/pw/pz-installer-synthetic')
    state = output / 'Zustand ü'
    configure(repo, state, refs=['main', 'content/pw/*'])
    cache = state / 'git-cache-pw-v1'; cache.mkdir()
    git(cache, 'init', '--bare', '-q'); git(cache, 'fetch', '--no-tags', str(repo), 'main:refs/pw/main')
    config = json.loads((state / 'config.json').read_text()); config['remote'] = str(repo)
    (state / 'config.json').write_text(json.dumps(config))
    (state / 'sync-pw-v1.json').write_text('{"synced_at":"2026-11-12T00:00:00Z"}\n')
    before = ((state / 'config.json').read_bytes(), git(repo, 'show-ref'), git(cache, 'show-ref'), git(repo, 'status', '--porcelain'))
    def preserved():
        actual = ((state / 'config.json').read_bytes(), git(repo, 'show-ref'), git(cache, 'show-ref'), git(repo, 'status', '--porcelain'))
        if actual != before:
            raise RuntimeError('Konfiguration/Checkout/Refs/Cache wurden verändert.')
    exe = installed / 'Picross-Start.exe'
    def launch():
        process = subprocess.Popen([str(exe), '--headless', '--no-browser', '--state', str(state)],
                                   creationflags=subprocess.CREATE_NO_WINDOW)
        children.append(process)
        def ready():
            try:
                identity = StateLock(state).read()
                return identity if control(identity, 'identify')['state'] == 'ready' else None
            except (OSError, ValueError):
                return None
        return process, wait_for(ready)
    def stop(process, identity):
        control(identity, 'stop')
        if process.wait(timeout=30) != 0:
            raise RuntimeError('Installierte App nicht regulär beendet.')
    try:
        # Build a genuine previous MSI from a clean synthetic SOURCE COMMIT.
        # No production version override and no relabelled MSI/App metadata.
        previous_source = output / 'previous-source'
        subprocess.run(['git', 'clone', '--quiet', '--shared', str(ROOT), str(previous_source)], check=True)
        source = previous_source / 'tools/production_workspace/release.json'
        old = json.loads(source.read_text()); parts = list(version_tuple(old['version']))
        if parts[2]:
            parts[2] -= 1
        elif parts[1]:
            parts[1] -= 1; parts[2] = 65535
        else:
            parts[0] -= 1; parts[1:] = [255, 65535]
        old['version'] = '.'.join(map(str, parts)); source.write_text(json.dumps(old, indent=2) + '\n')
        subprocess.run(['git', '-C', str(previous_source), 'add', str(source)], check=True)
        subprocess.run(['git', '-C', str(previous_source), '-c', 'user.name=P4 synthetic test', '-c', 'user.email=synthetic@example.invalid',
                        'commit', '--quiet', '-m', 'Synthetic predecessor version, never distribute'], check=True)
        previous_build = output / 'previous-build'
        subprocess.run([sys.executable, '-m', 'tools.production_workspace.build_installer', '--output', str(previous_build)],
                       cwd=previous_source, check=True)
        older = json.loads((previous_build / 'delivery.json').read_text())
        older_msi = previous_build / older['msi_file']
        execute(older_msi, INSTALLDESKTOP='1'); installed_code = older['product_code']
        verify_inventory()
        link = Path(os.environ['APPDATA']) / 'Microsoft/Windows/Start Menu/Programs/Picross-Produktionsassistent/Picross-Produktionsassistent.lnk'
        if not link.is_file() or not registered(installed_code):
            raise RuntimeError('Startmenü/Windows-Anwendungseintrag fehlt.')
        first, identity = launch(); port = identity['port']; preserved()
        # Actual running installed EXE: neither upgrade nor uninstall may touch files.
        exe_hash = sha(exe)
        execute(msi, success=False); execute('{' + installed_code + '}', action='/x', success=False)
        if first.poll() is not None or sha(exe) != exe_hash:
            raise RuntimeError('Laufende App wurde verändert/unterbrochen.')
        second, second_identity = launch()
        if second.wait(timeout=20) != 0 or second_identity['instance'] != identity['instance']:
            raise RuntimeError('Installierter Zweitstart nicht wiederverwendet.')
        stop(first, identity)
        # A foreign holder of a program file must also block upgrade.
        with (installed / 'components.json').open('rb'):
            execute(msi, success=False)
        execute(msi, INSTALLDESKTOP='1'); installed_code = report['product_code']
        current_inventory = verify_inventory(); preserved()
        if registered(older['product_code']) or not registered(installed_code):
            raise RuntimeError('Upgrade hat alten Produkteintrag nicht vollständig ersetzt.')
        execute(msi, success=False)  # same version
        execute(older_msi, success=False)  # downgrade
        restarted, identity = launch()
        if identity['port'] != port:
            raise RuntimeError('Origin beim Upgrade verändert.')
        stop(restarted, identity); preserved()
        # A genuinely entered synthetic P2 request holds the product marker
        # through a requested stop. No test bypass is shipped in the frozen app.
        from .install_interlock import InstallInterlock
        from .runtime import Runtime
        from .instance import data
        import http.client
        gate = InstallInterlock(); gate.acquire()
        lock = StateLock(state)
        if not lock.acquire():
            raise RuntimeError('Synthetischer Zustand nicht frei.')
        runtime = Runtime(lock, 'a' * 40, no_browser=True); runtime.start()
        service = runtime.service
        service.current = {'snapshot': 's'}
        service.jobs['j'] = {'title': 'synthetic'}; service.snapshots['s'] = ['j']
        service.plans['p'] = {'expires': time.monotonic() + 120, 'job_id': 'j', 'snapshot': 's',
                             'kind': 'remote', 'facts': {'branch': 'content/pw/pz-installer-synthetic'}}
        entered, release = threading.Event(), threading.Event()
        def transaction(*_):
            entered.set()
            if not release.wait(120):
                raise RuntimeError('Synthetic transaction release missing')
            return {'removed': False, 'message': 'synthetischer unbekannter Ausgang; keine echten Produktionsrefs'}
        service.removal.remove = transaction
        results = []
        def request():
            connection = http.client.HTTPConnection('127.0.0.1', runtime.metadata['port'], timeout=120)
            connection.request('POST', '/api/removal/confirm', data({'plan_id': 'p', 'job_id': 'j', 'snapshot': 's',
                'confirmation': 'content/pw/pz-installer-synthetic'}), {'Content-Type': 'application/json',
                'Origin': runtime.server.origin, 'X-Workspace-Session': service.secret})
            response = connection.getresponse(); response.read(); results.append(response.status); connection.close()
        worker = threading.Thread(target=request); worker.start()
        try:
            if not entered.wait(10):
                raise RuntimeError('P2-Testrequest hat Transaktion nicht erreicht.')
            runtime.request_stop()
            execute(msi, success=False)
            execute('{' + installed_code + '}', action='/x', success=False)
            if runtime.stopped.is_set() or not worker.is_alive():
                raise RuntimeError('MSI hat begonnenen P2-Drain unterbrochen.')
        finally:
            release.set(); worker.join(20); runtime.stopped.wait(20); gate.close(); lock.close()
        if results != [200] or not runtime.stopped.is_set():
            raise RuntimeError('Synthetischer P2-Drain nicht vollständig beendet.')
        preserved()
        address = (state / '.launcher/address.json').read_bytes()
        execute('{' + installed_code + '}', action='/x'); installed_code = None
        if exe.exists() or link.exists() or registered(report['product_code']):
            raise RuntimeError('Programm/Startmenü/Produkteintrag nach Uninstall vorhanden.')
        preserved()
        if (state / '.launcher/address.json').read_bytes() != address:
            raise RuntimeError('Persistenter Port bei Deinstallation verändert.')
        execute(msi); installed_code = report['product_code']; verify_inventory()
        again, identity = launch()
        if identity['port'] != port:
            raise RuntimeError('Wiederinstallation hat Origin verändert.')
        stop(again, identity); preserved()
        result = {'format': 'picross-installer-smoke-v1', 'commit': report['commit'], 'version': report['version'],
                  'msi_sha256': sha(msi), 'exe_sha256': sha(exe), 'product_code': report['product_code'],
                  'upgrade_code': report['upgrade_code'], 'previous_commit': older['commit'], 'previous_version': older['version'],
                  'inventory_files': len(current_inventory['files']), 'port_preserved': True, 'msi_calls': calls,
                  'limits': 'Actual MSI/process/HTTP test under non-elevated user. P2 uses entered source-runtime synthetic transaction, no production deletion. Desktop/browser observation is separate T03.'}
        (output / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps(result))
        return result
    finally:
        for child in children:
            if child.poll() is None:
                try:
                    control(StateLock(state).read(), 'stop'); child.wait(timeout=30)
                except Exception:
                    # Never hard-kill a transaction; leave explicit failure.
                    raise RuntimeError('Eigene Testinstanz noch aktiv; Zustand für regulären Stop erhalten.')
        if installed_code:
            execute('{' + installed_code + '}', action='/x')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    smoke(args.build.resolve(), args.output.resolve())
