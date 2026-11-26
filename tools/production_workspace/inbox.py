"""One durable, explicit receipt per job. All mutations share the PW operation lock."""
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import threading
from uuid import uuid4

from tools.puzzle_production import catalog_io as io, current_authoring as current
from tools.puzzle_production.authoring_package import require
from tools.puzzle_production.contract import exact_keys
from . import inbox_contract as contract, inbox_files as files
from .inbox_writer import Writer
from .repository import github_identity

STATE = 'inbox-v1.json'
ACTIVE = {'scan', 'stage', 'build', 'publish', 'cleanup'}


class Inbox:
    def __init__(self, service):
        self.service = service
        self.root = service.repository.state
        raw = io.read(self.root, STATE, 8 * current.LIMIT, missing=True)
        self.data = io.json_bytes(raw, 8 * current.LIMIT) if raw else {'folder': None, 'orders': {}}
        self.writer = Writer(self.root)
        self.stop = threading.Event()
        self.thread = None
        self.view_lock = threading.Lock()
        self.update_view()

    def update_view(self):
        with self.view_lock:
            self.view = {'folder': self.data['folder'], 'orders': [
                {k: order.get(k) for k in ('puzzle_id', 'request_id', 'phase', 'step', 'status', 'result', 'prompt')}
                for order in self.data['orders'].values()]}

    def save(self):
        current._atomic(self.root, STATE, current.encoded(self.data))
        self.update_view()

    def start(self):
        if self.thread is None:
            self.thread = threading.Thread(target=self.run, name='PW-Originaleingang')
            self.thread.start()

    def run(self):
        while not self.stop.wait(2):
            if not self.service.operation.acquire(blocking=False):
                continue
            refresh = False
            try:
                for order in list(self.data['orders'].values()):
                    if self.stop.is_set():
                        break
                    if order['step'] in ACTIVE:
                        refresh |= self.advance(order)
            finally:
                self.service.operation.release()
            if refresh and not self.stop.is_set():
                try:
                    self.service.start_refresh()
                except ValueError:
                    pass

    def action(self, action, body):
        self.service.acquire_operation()
        try:
            if action == 'configure':
                exact_keys(body, {'folder_id', 'directory'})
                require(re.fullmatch('[A-Za-z0-9_-]{1,160}', body['folder_id']), 'Drive-Ordner-ID erforderlich.')
                supplied = Path(body['directory'])
                require(supplied.is_absolute(), 'Absolutes lokales Eingangsverzeichnis erforderlich.')
                folder = io.external(supplied)
                require(folder.is_dir() and folder != Path(folder.anchor), 'Eigenen privaten Eingangsordner wählen.')
                for own in (self.root, self.service.repository.local.root):
                    require(not folder.is_relative_to(own) and not own.is_relative_to(folder), 'Git- und Eingangsordner müssen getrennt sein.')
                require(not self.data['orders'], 'Vor einer neuen Ordnerbindung laufende Aufträge beenden.')
                self.data['folder'] = {'id': body['folder_id'], 'directory': str(folder)}
            elif action == 'activate':
                self.activate(body)
            else:
                exact_keys(body, {'puzzle_id', 'request_id'})
                order = self.data['orders'].get(body['puzzle_id'])
                require(order and order['request_id'] == body['request_id'], 'Empfangsauftrag ist abgelaufen.')
                if action == 'cancel':
                    require(order['step'] in ('scan', 'stage', 'blocked', 'done'), 'Begonnene Veröffentlichung zuerst fortsetzen.')
                    self.discard_stage(order)
                    del self.data['orders'][order['puzzle_id']]
                elif action == 'retry':
                    require(order['step'] in ACTIVE, 'Auftrag kann nicht fortgesetzt werden.')
                    order['paused'] = False
                else:
                    raise ValueError('Unbekannte Empfangsaktion.')
            self.save()
            return self.view
        finally:
            self.service.operation.release()

    def activate(self, body):
        exact_keys(body, {'snapshot', 'jid', 'puzzle_id', 'phase', 'intent', 'target', 'brief', 'selection', 'findings'})
        folder = self.data['folder']
        require(folder and github_identity(self.service.repository.remote), 'Privaten Eingang und Produktionsremote einrichten.')
        status = self.service.status()
        require(status.get('remote_confirmed') and status['snapshot'] == body['snapshot'], 'Aktuelle Remotequellen laden.')
        job, phase, intent = body['puzzle_id'], body['phase'], body['intent']
        current.path(job)
        require(phase in contract.PHASES and intent in ('offer', 'assessment', 'correction'), 'Ungültiger Auftragsumfang.')
        prior = self.data['orders'].get(job)
        require(not prior or prior['step'] == 'done', 'Bestehenden Auftrag zuerst abschließen oder abbrechen.')
        repo = self.service.removal
        main = repo.main_state(job)
        require(not main['registered'] and not main['revisions'], 'ID bereits auf main. Registrierte IDs im Bestandseditor pflegen.')
        require(main['commit'] == status['completion']['main_commit'], 'Main hat sich geändert. Quellen neu laden.')
        head = repo.remote_head('refs/heads/content/pw/' + job)
        now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        choice = None
        declarations = {}
        edits = io.json_bytes(body['findings'].encode('utf-8'), 16384)
        require(isinstance(edits, dict), 'Ungültige Befunderklärungen.')
        target = body['target']
        brief = body['brief']
        require(isinstance(brief, str) and 0 < len(brief.strip()) <= 4096, 'Auftragsbeschreibung erforderlich.')
        if body['jid']:
            row = self.service.selected(body['jid'], body['snapshot'])
            require(not repo.availability(row) and row['puzzle_id'] == job and row['commit'] == head and
                    row['_record']['format'] == current.findings.PUBLISHED, 'Aktuelle veröffentlichte v3-Quelle erforderlich.')
            record = row['_record']
            require(record['operation'] == 'production' and not record['test_only'] and not record['integration'], 'Unzulässiger Produktionstyp.')
            source_hash = row['_projection']['record']['sha256']
            limits = record['budgets']['limits']
            for finding in record['findings']:
                binding = current.findings.binding(finding)
                if binding not in edits:
                    continue
                edit = exact_keys(edits.pop(binding), {'accepted', 'treatment'})
                require(type(edit['accepted']) is bool and finding['target'] in (body['selection'], target),
                        'Befundentscheidung gehört nicht zur gewählten Variante.')
                row_copy = dict(finding)
                current.findings.declare(row_copy, expected=binding, action='accept' if edit['accepted'] else 'revoke',
                    treatment=edit['treatment'] or current.findings.DEFAULT, actor='PW-Nutzer', timestamp_utc=now,
                    statement='Erklärung beim Start des gebundenen Empfangsauftrags.')
                declarations[binding] = row_copy['decision']
            if phase in contract.PRIOR and not record['selected'][contract.PRIOR[phase]]:
                scope = contract.PRIOR[phase]
                key = body['selection']
                card = self.service.detail(body['jid'])['facts']['candidates'].get(key)
                require(card and not card['missing'] and all(r['eligible'] and
                        (declarations.get(r['binding']) or r['decision'] or {}).get('action') == 'accept' for r in card['findings']) and key in {a['id'] for a in
                        (record['rasters'] if scope == 'raster' else record['assets']) if a.get('role', 'raster') == scope},
                        'Eine qualifizierte bestehende Variante ausdrücklich auswählen.')
                choice = {'id': key, 'decision': {'scope': scope, 'actor': 'PW-Nutzer', 'timestamp_utc': now,
                          'statement': 'Ausdrückliche Auswahl von ' + key + ' für diesen Folgeauftrag.'}}
            else:
                require(not body['selection'], 'Keine weitere Vorauswahl vorgesehen.')
            if intent != 'offer':
                require(target in {a['id'] for a in record['assets'] if a['role'] == phase}, 'Konkrete Korrektur-/Bewertungsgrundlage erforderlich.')
            reopening = intent == 'correction' and target == record['selected'][phase]
            require(reopening or not record['selected'][phase] and current.PHASES.index(record['state']) <= current.PHASES.index(contract.PHASES[phase]),
                    'Die gewählte Produktionsphase ist abgeschlossen.')
        else:
            require(head is None and phase == 'reveal' and intent == 'offer' and not body['selection'], 'Neue unbenutzte Produktions-ID erforderlich.')
            source_hash = None
            limits = {'raster_candidates': 6, 'repair_rounds': 2, 'image_corrections': 2}
        require(not edits, 'Befund ist veraltet oder gehört nicht zu dieser Auswahl.')
        require(intent != 'offer' or not target, 'Angebot enthält eine unerwartete Zielvariante.')
        order = {'request_id': str(uuid4()), 'puzzle_id': job, 'phase': phase, 'intent': intent, 'target': target,
                 'source': {'main_commit': main['commit'], 'work_head': head, 'record_sha256': source_hash},
                 'choice': choice, 'declarations': declarations, 'limits': limits, 'brief': brief, 'test_only': False, 'step': 'scan',
                 'status': 'Wartet auf die Lieferung.', 'files': {}, 'paused': False}
        binding = {k: order[k] for k in ('request_id', 'puzzle_id', 'phase', 'intent', 'target', 'source', 'brief', 'choice', 'declarations', 'limits')}
        order['prompt'] = ('Arbeite gemäß AGENTS.md, Authoring und docs/tools/PW_IMPORT.md in ' + contract.REPOSITORY +
            '. Stelle die nativen Einzeloriginale byteidentisch in meinem privaten Drive-Ordner ' + folder['id'] +
            ' bereit. Lade das Manifest zuletzt. Verwende folgende bestätigte Bindung: ' +
            json.dumps(binding, ensure_ascii=False) + '. Erfolg erst nach GitHub-Readback. ' +
            ('Danach den beauftragten Schritt 4 mit prepare, Zustellung, tatsächlicher Sichtung und Assessment am veröffentlichten Stand fortsetzen.'
             if phase == 'background' else ''))
        self.data['orders'][job] = order

    def stage(self, order):
        return io.safe(self.root, 'inbox-stage/' + contract.uuid4_text(order['request_id']))

    def discard_stage(self, order):
        directory = self.stage(order)
        if directory.is_dir():
            for name in order.get('files', {}):
                path = io.safe(directory, name)
                if path.exists():
                    require(io.file_hash(directory, name, 32 * current.LIMIT) == order['files'][name]['sha256'],
                            'Eigene Arbeitskopie verändert.')
                    path.unlink()
            directory.rmdir()

    def receive(self, order, folder):
        matches = []
        candidates = 0
        for entry in files.entries(folder):
            if not re.fullmatch(r'[0-9a-fA-F-]{36}\.json', entry.name, re.I):
                continue
            candidates += 1
            require(candidates <= 32, 'Zu viele Liefermanifeste im privaten Eingang.')
            try:
                raw, identity = files.read(folder, entry.name, 2 * current.LIMIT)
            except files.Waiting:
                continue
            try:
                # Route a bounded parse. Duplicate-key deliveries with a bound
                # request are errors, even if the last occurrence claims a different ID.
                route = io.json_bytes(raw, 2 * current.LIMIT)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            except ValueError:
                if order['request_id'].encode('ascii') in raw:
                    raise
                continue
            if entry.name == order.get('manifest'):
                require(identity['sha256'] == order['manifest_hash'], 'Lieferkennung mit geänderten Manifestbytes.')
            if isinstance(route, dict) and route.get('request_id') == order['request_id']:
                matches.append((entry.name, raw, identity))
                require(len(matches) == 1, 'Konflikt: mehrere Lieferungen für diesen Auftrag.')
        if not matches:
            raise files.Waiting
        name, raw, manifest_id = matches[0]
        value = contract.envelope(raw, name, order)
        require(order.get('manifest', name) == name and order.get('manifest_hash', manifest_id['sha256']) == manifest_id['sha256'],
                'Lieferkennung oder Manifestbytes wurden ausgetauscht.')
        if 'manifest' not in order:
            order.update(manifest=name, manifest_hash=manifest_id['sha256'], step='stage')
            self.save()
        directory = self.stage(order)
        directory.mkdir(parents=True, exist_ok=True)
        def copy(filename, content, binding):
            prior = order['files'].get(filename)
            require(not prior or prior == binding, 'Identität einer gebundenen Datei verändert.')
            if not prior:
                order['files'][filename] = binding
                self.save()
            path = io.safe(directory, filename)
            if path.exists():
                require(io.file_hash(directory, filename, len(content)) == binding['sha256'], 'Eigene Arbeitskopie verändert.')
            else:
                current._atomic(directory, filename, content)
        copy(name, raw, manifest_id)
        for item in value['request']['files']:
            content, observed = files.read(folder, item['source'], 32 * current.LIMIT, item)
            suffix = Path(item['source']).suffix
            if suffix == '.svg':
                from tools.puzzle_production.editor_image_input import validate_reveal
                validate_reveal(content, suffix)
            else:
                from .presentation import image
                expected_mime = 'image/png' if suffix == '.png' else 'image/jpeg'
                require(image(content)['mime'] == expected_mime, 'Bildformat weicht vom Dateieintrag ab.')
            copy(item['source'], content, observed)
        for filename, expected in order['files'].items():
            _, observed = files.read(folder, filename, expected['bytes'], expected)
            require(observed == expected, 'Eingang während der Prüfung geändert.')
        return value

    def advance(self, order):
        if order.get('paused'):
            return False
        folder = Path(self.data['folder']['directory'])
        published = False
        try:
            if order['step'] != 'cleanup':
                if order['step'] in ('scan', 'stage'):
                    value = self.receive(order, folder)
                else:
                    raw = io.read(self.stage(order), order['manifest'], 2 * current.LIMIT)
                    require(io.checksum(raw) == order['manifest_hash'], 'Gesicherte Lieferbytes verändert.')
                    value = contract.envelope(raw, order['manifest'], order)
                result = self.writer.publish(order, value['request'], self.stage(order), self.save)
                order.update(step='cleanup', result=result, remaining=list(order['files']),
                             status='GitHub-Veröffentlichung bestätigt. Eingangsbereinigung läuft.')
                self.save()
                published = True
            for name in order['remaining'][:]:
                files.retire(folder, name, order['files'][name])
                order['remaining'].remove(name)
                self.save()
            self.discard_stage(order)
            order.update(step='done', status='Veröffentlicht. Lokaler Eingang bereinigt. Drive synchronisiert separat.')
            order.pop('files')
            self.save()
        except files.Waiting:
            self.message(order, 'Wartet auf vollständige Dateien.')
        except (OSError, ValueError, RuntimeError, KeyError, TypeError, subprocess.SubprocessError) as exc:
            if order['step'] == 'cleanup':
                message = 'Veröffentlicht. Bereinigungsrest: ' + ', '.join(order['remaining'])
            elif order['step'] in ('build', 'publish'):
                message = 'Writer unterbrochen. Identischen Auftrag nach Quellenprüfung fortsetzen.'
            elif isinstance(exc, (OSError, subprocess.SubprocessError)):
                message = 'Eingang oder Quelle nicht erreichbar. Verbindung prüfen und fortsetzen.'
            else:
                order['step'] = 'blocked'
                message = 'Lieferung gesperrt: ' + str(exc)[:320]
            order['paused'] = True
            self.message(order, message)
        return published

    def message(self, order, message):
        if order['status'] != message or order.get('paused'):
            order['status'] = message
            self.save()
