"""One-time P3-T02 smoke of an unpacked delivery, not a CI/browser test family."""
import argparse
from contextlib import contextmanager
import hashlib
import http.client
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
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
        except (ConnectionError, TimeoutError, ValueError):
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
        fake_git = destination / 'ungeeignetes Git'; fake_git.mkdir()
        stub = fake_git / 'git.cs'
        stub.write_text('public class GitStub { public static int Main() { return 129; } }\n')
        compiler = Path(os.environ['SystemRoot']) / 'Microsoft.NET/Framework64/v4.0.30319/csc.exe'
        if not compiler.is_file():
            raise RuntimeError('T02-Teststub benötigt den vorhandenen Windows-.NET-Framework-C#-Compiler; keine Installation.')
        subprocess.run([str(compiler), '/nologo', '/target:winexe', '/out:' + str(fake_git / 'git.exe'), str(stub)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
        unsuitable = {**env, 'PATH': str(fake_git) + os.pathsep + str(Path(os.environ['SystemRoot']) / 'System32')}
        if start(environment=unsuitable).wait(timeout=15) != 2:
            raise RuntimeError('Ungeeignetes Git nicht früh erkannt.')
        resource = app / '_internal/tools/production_workspace/ui/app.js'
        saved = resource.read_bytes(); resource.write_bytes(b'')
        try:
            if start().wait(timeout=15) != 2:
                raise RuntimeError('Beschädigtes Bundle nicht früh erkannt.')
        finally:
            resource.write_bytes(saved)
        if (state / 'config.json').read_bytes() != config_bytes or git(repo, 'show-ref') != before[1] or git(repo, 'status', '--porcelain') != before[2]:
            raise RuntimeError('Testcheckout oder Konfiguration wurde verändert.')
        checks.append('missing/unsuitable Git and corrupt UI rejected; config and data refs/files preserved')
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


def raster_fixture(repo, root):
    from tests.puzzle_production.current_fixtures import checkout, make, put
    from tests.puzzle_production.test_current_authoring import decide, judgment
    from tools.puzzle_production import current_authoring as current
    from tools.test_production_workspace import commit

    checkout(repo)
    git(repo, 'init', '-q', '-b', 'main')
    base = commit(repo)
    entries = []
    for version in ('0.4', '0.3'):
        identifier = 'pz-frozen-' + version.replace('.', '')
        method = 'picross-difficulty-' + version
        fixture = make(root / identifier, identifier=identifier, method=method)
        incoming = json.loads((fixture / 'manifest.json').read_bytes())
        prefix = f'content/authoring/{identifier}/data/'
        assets = [
            {'id': role + '-a', 'role': role, 'label': role,
             'file': put(repo, prefix + role + '.png', (fixture / 'reveal.png').read_bytes()),
             'rights': incoming['reveal']['rights'], 'review': judgment(current.CRITERIA[role])}
            for role in ('reveal', 'motif')
        ]
        definition = json.loads((fixture / 'definition.json').read_bytes())
        raster = {'id': 'raster-a', 'label': 'Synthetisches Raster',
                  **{key: put(repo, prefix + key + '.json', (fixture / incoming[key]['file']).read_bytes())
                     for key in ('definition', 'proof', 'difficulty')},
                  'preview': put(repo, prefix + 'preview.png', current.raster_preview(definition, mode='mono')),
                  'review': judgment(current.CRITERIA['raster']), 'exceptions': []}
        parameters = {'width': 3, 'height': 3, 'mode': 'mono', 'foreground_colors': 1,
                      'size_constraint': 'exact', 'foreground_color_constraint': 'exact'}
        limits = {'raster_candidates': 6, 'repair_rounds': 2, 'image_corrections': 2}
        record = {'format': current.FORMAT, 'puzzle_id': identifier, 'revision': 'current',
                  'source_commit': base, 'operation': 'production', 'target': None, 'title': identifier,
                  'category_id': 'test', 'state': 'raster_ready', 'brief': 'Synthetischer Methoden-Smoke',
                  'parameters': {'proposed': [parameters], 'approved': [parameters]}, 'assets': assets,
                  'rasters': [raster], 'selected': {'reveal': 'reveal-a', 'motif': 'motif-a',
                  'raster': None, 'background': None}, 'decisions': [], 'blockers': [], 'test_only': True,
                  'budgets': {'limits': limits, 'used': dict.fromkeys(limits, 0)}, 'integration': None}
        for scope in ('reveal', 'motif'):
            decide(record, scope)
        current.validate(record)
        name = current.path(identifier)
        put(repo, name, current.encoded(record))
        entries.append({'puzzle_id': identifier, 'revision': 'current', 'record': name})
    put(repo, current.INDEX, current.encoded({'format': 'picross-authoring-index-v1', 'entries': entries}))
    commit_id = commit(repo)
    paths = git(repo, 'ls-tree', '-r', '--name-only', commit_id).decode().splitlines()
    if not paths or any(not name.startswith(('content/', 'game/data/')) or Path(name).suffix not in {'.json', '.png'}
                        for name in paths):
        raise RuntimeError('Synthetischer Datencheckout enthält ausführbare Quellen oder fremde Ressourcen.')
    return commit_id, paths, entries


def start_frozen(app, state, work, *extra):
    # In particular, source Python, a developer venv and the checkout CWD
    # cannot supply importable code or original method files to this process.
    env = {name: value for name, value in os.environ.items() if not name.upper().startswith('PYTHON')}
    git_path = Path(shutil.which('git')).parent
    env['PATH'] = os.pathsep.join((str(git_path), str(Path(os.environ['SystemRoot']) / 'System32')))
    env['TEMP'] = env['TMP'] = str(work)
    return subprocess.Popen([str(app / 'Picross-Start.exe'), '--headless', '--no-browser', '--state', str(state), *extra],
                            cwd=work, env=env, creationflags=subprocess.CREATE_NO_WINDOW,
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


@contextmanager
def frozen_reader(app, state, work, commit):
    lock = StateLock(state)
    with start_frozen(app, state, work) as child:
        metadata = None
        try:
            def ready():
                if child.poll() is not None:
                    raise RuntimeError('Frozen-Start fehlgeschlagen: ' + child.stderr.read().decode('utf-8', errors='replace'))
                if lock.metadata.exists():
                    identity = lock.read()
                    if control(identity, 'identify')['state'] == 'ready':
                        return identity
                return None
            metadata = wait_for(ready)
            if metadata['build'] != commit:
                raise RuntimeError('Frozen-Instanz meldet einen fremden Buildcommit.')
            session = control(metadata, 'open')['browser_url'].split('#', 1)[1]

            def request(path):
                connection = http.client.HTTPConnection('127.0.0.1', metadata['port'], timeout=30)
                try:
                    connection.request('GET', path, headers={'X-Workspace-Session': session})
                    response = connection.getresponse()
                    return response.status, json.loads(response.read())
                finally:
                    connection.close()

            def finished():
                status, listing = request('/api/jobs')
                if status != 200:
                    raise RuntimeError('Frozen-Jobliste nicht lesbar.')
                return listing if listing['update']['state'] in ('done', 'error') else None

            listing = wait_for(finished, timeout=120)
            yield listing, request
        finally:
            if metadata and child.poll() is None:
                try:
                    control(metadata, 'stop')
                    if child.wait(timeout=30) != 0:
                        raise RuntimeError('Frozen-Instanz konnte nicht regulär beenden.')
                finally:
                    if child.poll() is None:
                        child.kill()
                        child.wait(timeout=10)
            elif child.poll() is None:
                child.kill()
                child.wait(timeout=10)


def verify_method_candidate(app, build, inspection):
    audit = json.loads((inspection / 'method-resources.json').read_bytes())
    delivery = json.loads((build / 'delivery.json').read_bytes())
    result = json.loads((inspection / 'result.json').read_bytes())
    keys = ('commit', 'payload_fingerprint', 'msi_sha256')
    if not result['compared_to_build'] or any(audit[key] != result[key] or audit[key] != delivery[key] for key in keys):
        raise RuntimeError('Frozen-Smoke ohne zugeordnete MSI-Inspektion.')
    inventory_path = app / 'inventory.json'
    inventory_raw = inventory_path.read_bytes()
    inventory = json.loads(inventory_raw)
    if hashlib.sha256(inventory_raw).hexdigest() != audit['inventory_sha256'] or inventory['commit'] != audit['commit']:
        raise RuntimeError('Frozen-Dateiinventar weicht vom inspizierten MSI ab.')
    files = {name.relative_to(app).as_posix() for name in app.rglob('*') if name.is_file()}
    if files != {row['file'] for row in inventory['files']} | {'inventory.json'}:
        raise RuntimeError('Frozen-Dateimenge weicht vom inspizierten MSI ab.')
    for row in inventory['files']:
        raw = (app / row['file']).read_bytes()
        if len(raw) != row['bytes'] or hashlib.sha256(raw).hexdigest() != row['sha256']:
            raise RuntimeError('Frozen-Datei weicht vom inspizierten MSI ab: ' + row['file'])
    return audit


def method_smoke(build, inspection, destination):
    if os.name != 'nt':
        raise RuntimeError('PW-SD2-A benötigt Windows.')
    destination.mkdir()
    app = build / 'dist/Picross-Start'
    audit = verify_method_candidate(app, build, inspection)
    commit = audit['commit']
    with tempfile.TemporaryDirectory(prefix='method-smoke-', dir=destination) as temporary:
        work = Path(temporary)
        repo, state = work / 'Daten ä', work / 'Zustand ü'
        data_commit, data_paths, entries = raster_fixture(repo, work)
        configure(repo, state, refs=['main'])
        cwd = work / 'Fremder Startordner ö'; cwd.mkdir()
        (cwd / 'tools.py').write_text('raise RuntimeError("FOREIGN MODULE MUST NOT RUN")\n', encoding='utf-8')
        projections = {}
        with frozen_reader(app, state, cwd, commit) as (listing, request):
            if listing['update']['state'] != 'done' or listing['errors'] or len(listing['jobs']) != len(entries):
                raise RuntimeError('Frozen-Jobliste enthält nicht genau die synthetischen Rasterangebote.')
            for job in listing['jobs']:
                status, detail = request('/api/jobs/' + job['id'])
                if status != 200:
                    raise RuntimeError('Frozen-Detailreader: ' + repr(detail))
                facts = detail['facts']
                method = {'pz-frozen-04': 'picross-difficulty-0.4', 'pz-frozen-03': 'picross-difficulty-0.3'}[job['puzzle_id']]
                expected = {'width': 3, 'height': 3, 'mode': 'mono', 'used_colors': 1,
                            'difficulty': {'method': method, 'level': 'L1', 'assessment_type': 'instrumented',
                                           'confidence': 'medium', 'plausible_range': ['L1', 'L1'], 'r4_required': False}}
                if (job['commit'] != data_commit or not facts['test_only'] or facts['state'] != 'raster_ready'
                        or facts['metadata'] != expected or [(offer['kind'], offer['id']) for offer in detail['offers']]
                        != [('raster', 'raster-a')]):
                    raise RuntimeError('Unerwartete Frozen-Rasterprojektion: ' + repr(facts['metadata']))
                projections[job['puzzle_id']] = facts['metadata']

        negatives = []
        for name in ('difficulty_method_0_3.json', 'sd2_rating_freeze.py'):
            relative = 'tools/puzzle_production/' + name
            for mutation in ('missing', 'changed'):
                with tempfile.TemporaryDirectory(prefix='broken-', dir=work) as broken:
                    root = Path(broken)
                    copy = Path(shutil.copytree(app, root / 'app'))
                    broken_state = root / 'state'
                    member = copy / '_internal' / relative
                    if mutation == 'missing':
                        member.unlink()
                    else:
                        member.write_bytes(b'changed')
                    with start_frozen(copy, broken_state, cwd, '--repository', str(repo)) as child:
                        try:
                            _, raw = child.communicate(timeout=45)
                        finally:
                            if child.poll() is None:
                                child.kill()
                                child.wait(timeout=10)
                        error = raw.decode('utf-8').strip()
                        if child.returncode != 2 or broken_state.exists() or not error.startswith(
                                'Programmpaket unvollständig oder beschädigt. Interne Dateien der Bewertungsmethoden'):
                            raise RuntimeError(f'Frozen-Preflight akzeptierte {mutation} {name}: {child.returncode} {error!r}')
                        negatives.append({'file': relative, 'mutation': mutation, 'exit': child.returncode, 'error': error,
                                          'state_created': False})
        if git(repo, 'status', '--porcelain') or git(repo, 'rev-parse', 'HEAD').decode().strip() != data_commit:
            raise RuntimeError('Der synthetische Datencheckout wurde verändert.')
    result = {**audit, 'format': 'picross-pw-method-smoke-v1', 'exe_sha256': hashlib.sha256(
              (app / 'Picross-Start.exe').read_bytes()).hexdigest(), 'data_commit': data_commit,
              'data_tree_files': data_paths, 'projections': projections, 'preflight_rejections': negatives}
    output = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    (destination / 'frozen-methods.json').write_text(output, encoding='utf-8')
    print(output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--archive', type=Path)
    mode.add_argument('--method-build', type=Path)
    parser.add_argument('--inspection', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.method_build:
        if not args.inspection:
            parser.error('--method-build benötigt --inspection')
        method_smoke(args.method_build.resolve(), args.inspection.resolve(), args.output.resolve())
    else:
        smoke(args.archive.resolve(), args.output.resolve())
