"""One-time P3-T02 smoke of an unpacked delivery, not a CI/browser test family."""
import argparse
import hashlib
import http.client
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import time
import zipfile

from .instance import StateLock, control
from .repository import configure
from .sources import git


def wait_for(check, timeout=30):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = check()
        if value:
            return value
        time.sleep(0.1)
    raise RuntimeError('Smoke: erwarteter Zustand nicht erreicht.')


def smoke(archive, destination):
    if os.name != 'nt':
        raise RuntimeError('T02 benötigt Windows.')
    if destination.exists():
        raise RuntimeError('Neuen eigenen Smokeordner wählen.')
    destination.mkdir(parents=True)
    with zipfile.ZipFile(archive) as delivery:
        # Only consume a locally selected, trusted build/download; reject traversal.
        for name in delivery.namelist():
            target = (destination / name).resolve()
            if not target.is_relative_to(destination.resolve()):
                raise RuntimeError('Unsicherer Lieferpfad.')
        delivery.extractall(destination)
    app = destination / 'Picross-Start'
    inventory = json.loads((app / 'inventory.json').read_bytes())
    for row in inventory['files']:
        raw = (app / row['file']).read_bytes()
        if len(raw) != row['bytes'] or hashlib.sha256(raw).hexdigest() != row['sha256']:
            raise RuntimeError('Lieferdownload stimmt nicht mit Inventar überein.')
    from tools.test_production_workspace import current_fixture, commit
    repo = destination / 'Daten ä ohne Programm'; repo.mkdir()
    git(repo, 'init', '-q', '-b', 'main')
    current_fixture(repo, destination / 'synthetische Quelle')
    commit(repo)
    state = destination / 'Zustand ü'
    configure(repo, state, refs=['main'])
    before = (state / 'config.json').read_bytes(), git(repo, 'show-ref'), git(repo, 'status', '--porcelain')
    # Preserve a genuine populated, selected private cache and sync status.
    cached = state / 'git-cache-pw-v1'; cached.mkdir()
    git(cached, 'init', '--bare', '-q')
    git(cached, 'fetch', '--no-tags', str(repo), 'main:refs/pw/main')
    (state / 'sync-pw-v1.json').write_text('{"synced_at":"2026-11-12T00:00:00Z"}\n')
    config = json.loads(before[0]); config['remote'] = str(repo)
    (state / 'config.json').write_text(json.dumps(config))
    config_bytes = (state / 'config.json').read_bytes()
    cwd = destination / 'fremder Startordner ö'; cwd.mkdir()
    for name in ('tools.py', 'authoring_workflow.py', 'PIL.py', 'tkinter.py'):
        (cwd / name).write_text('raise RuntimeError("FOREIGN MODULE MUST NOT RUN")\n')
    env = {k: v for k, v in os.environ.items() if k not in ('PYTHONPATH', 'PYTHONHOME')}
    git_path = Path(shutil.which('git')).parent
    env['PATH'] = str(git_path) + os.pathsep + str(Path(os.environ['SystemRoot']) / 'System32')
    env['TEMP'] = env['TMP'] = str(destination)
    executable = app / 'Picross-Start.exe'
    children = []
    active = None
    def start(*extra, environment=env):
        process = subprocess.Popen([str(executable), '--headless', '--no-browser', '--state', str(state), *extra],
                                   cwd=cwd, env=environment, creationflags=subprocess.CREATE_NO_WINDOW)
        children.append(process)
        return process
    def ready():
        lock = StateLock(state)
        if not lock.metadata.exists():
            return None
        metadata = lock.read()
        try:
            return metadata if control(metadata, 'identify')['state'] == 'ready' else None
        except (ConnectionError, TimeoutError):
            return None
    def stop(process, metadata):
        control(metadata, 'stop')
        if process.wait(timeout=30) != 0:
            raise RuntimeError('Stop fehlgeschlagen.')
        if (state / '.launcher/instance.json').exists():
            raise RuntimeError('Instanzmetadaten blieben erhalten.')
        with socket.socket() as sock:
            if sock.connect_ex(('127.0.0.1', metadata['port'])) == 0:
                raise RuntimeError('Port nach Stop noch offen.')
    checks = []
    try:
        active = start(); identity = wait_for(ready)
        url = control(identity, 'open')['browser_url']
        session = url.split('#', 1)[1]
        def get(path):
            c = http.client.HTTPConnection('127.0.0.1', identity['port'], timeout=5)
            c.request('GET', path, headers={'X-Workspace-Session': session})
            response = c.getresponse(); raw = response.read(); c.close()
            if response.status != 200:
                raise RuntimeError('Frozen HTTP-Leser hat Quelle abgewiesen.')
            return raw
        def jobs():
            value = json.loads(get('/api/jobs'))
            return value if value['update']['state'] in ('done', 'error') else None
        listed = wait_for(jobs)
        if listed['update']['state'] != 'done' or not listed['jobs']:
            raise RuntimeError('Frozen-Reader konnte synthetischen 0.8-Job nicht lesen.')
        jid = listed['jobs'][0]['id']
        detail = json.loads(get('/api/jobs/' + jid))
        if detail['format'] != 'picross-production-presentation-v2':
            raise RuntimeError('Heutige Projektion nicht gelesen.')
        for asset in detail['assets']:
            raw = get('/api/jobs/' + jid + '/assets/' + asset['id'])
            if hashlib.sha256(raw).hexdigest() != asset['location']['sha256']:
                raise RuntimeError('Originalbild nicht bytegleich aus Frozen-Reader erhalten.')
        second = start()
        if second.wait(timeout=15) != 0 or ready()['instance'] != identity['instance']:
            raise RuntimeError('Zweitstart hat Instanz nicht wiederverwendet.')
        checks.append('Frozen authoring_workflow/0.8 job/original image hashes, UI/Tcl resources, data-only checkout, foreign CWD, second start')
        stop(active, identity); active = None
        active = start(); restarted = wait_for(ready)
        if restarted['port'] != identity['port']:
            raise RuntimeError('Browserorigin wurde geändert.')
        stop(active, restarted); active = None
        checks.append('normal stop, actual process/port end, restart, stable origin')
        with socket.socket() as foreign:
            foreign.bind(('127.0.0.1', identity['port'])); foreign.listen()
            failure = start()
            if failure.wait(timeout=15) != 2:
                raise RuntimeError('Fremdport nicht als Startfehler erkannt.')
            active = start('--port', '0'); changed = wait_for(ready)
            if changed['port'] == identity['port']:
                raise RuntimeError('Expliziter Portwechsel nicht wirksam.')
            stop(active, changed); active = None
        checks.append('foreign port rejected; explicit port change')
        active = start(); crashed = wait_for(ready)
        active.kill(); active.wait(timeout=10); active = None  # Owned read-only synthetic instance, no transaction.
        active = start(); recovered = wait_for(ready)
        if crashed['instance'] == recovered['instance']:
            raise RuntimeError('Absturzreste nicht erneuert.')
        stop(active, recovered); active = None
        checks.append('owned synthetic crash recovery; PID never trusted')
        missing_git = {**env, 'PATH': str(Path(os.environ['SystemRoot']) / 'System32')}
        if start(environment=missing_git).wait(timeout=15) != 2:
            raise RuntimeError('Fehlendes Git nicht früh erkannt.')
        resource = app / '_internal/tools/production_workspace/ui/app.js'
        saved = resource.read_bytes(); resource.write_bytes(b'')
        try:
            if start().wait(timeout=15) != 2:
                raise RuntimeError('Beschädigtes Bundle nicht früh erkannt.')
        finally:
            resource.write_bytes(saved)
        if (state / 'config.json').read_bytes() != config_bytes or git(repo, 'show-ref') != before[1] or git(repo, 'status', '--porcelain') != before[2]:
            raise RuntimeError('Testcheckout oder Konfiguration wurde verändert.')
        checks.append('missing Git/corrupt UI rejected; config and data refs/files preserved')
        result = {'format': 'picross-launcher-smoke-v1', 'commit': inventory['commit'],
                  'zip_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
                  'exe_sha256': hashlib.sha256(executable.read_bytes()).hexdigest(), 'checks': checks,
                  'limits': 'Automated process/HTTP only. Actual desktop/browser observation remains T03.'}
        print(json.dumps(result, ensure_ascii=False))
        return result
    finally:
        if active and active.poll() is None:
            current = ready()
            if current:
                stop(active, current)
        for child in children:
            if child.poll() is None:
                child.kill(); child.wait(timeout=10)  # Only exact synthetic children created above.


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    smoke(args.archive.resolve(), args.output.resolve())
