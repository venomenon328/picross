"""One durable, explicit receipt per job. All mutations share the PW operation lock."""
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import threading
import unicodedata
from uuid import uuid4

from tools.puzzle_production import catalog_io as io, current_authoring as current
from tools.puzzle_production.authoring_package import require
from tools.puzzle_production.contract import exact_keys
from . import inbox_contract as contract, inbox_files as files
from .inbox_writer import StaleBuild, Writer
from .repository import github_identity

STATE = 'inbox-v1.json'
ACTIVE = {'scan', 'stage', 'build', 'publish', 'cleanup'}


class Inbox:
    def __init__(self, service):
        self.service = service
        self.root = service.repository.state
        raw = io.read(self.root, STATE, 8 * current.LIMIT, missing=True)
        self.data = io.json_bytes(raw, 8 * current.LIMIT) if raw else {'folder': None, 'orders': {}}
        self.data.setdefault('drafts', {})
        self.data.setdefault('generations', {})
        # Existing receipts used the flat configured folder. Freeze it before any edit.
        for order in self.data['orders'].values():
            order.setdefault('folder', self.data['folder'])
        self.writer = Writer(self.root)
        self.stop = threading.Event()
        self.thread = None
        self.view_lock = threading.Lock()
        self.update_view()

    def update_view(self):
        with self.view_lock:
            self.view = {'folder': self.data['folder'], 'drafts': dict(self.data['drafts']),
                         'generations': dict(self.data['generations']), 'orders': [
                {**{k: order.get(k) for k in ('puzzle_id', 'request_id', 'draft_id', 'phase', 'step', 'status',
                                              'paused', 'result', 'prompt', 'brief', 'inputs', 'intent')},
                 'work_head': order['source']['work_head']}
                for order in self.data['orders'].values()]}

    def confirmed_successors(self, listing):
        """Bind descendants during source refresh. Polling only reads the resulting snapshot."""
        from .motifs import Relations
        if not listing.get('remote_confirmed') or not github_identity(self.service.repository.remote):
            return {}
        with self.view_lock:
            heads = {o['puzzle_id']: o['result']['head'] for o in self.view['orders']
                     if o.get('result') and o['step'] in ('cleanup', 'done')}
        history = Relations(self.service.repository)
        successors = {}
        for row in listing['jobs']:
            job, tip = row['puzzle_id'], row['commit']
            head = heads.get(job)
            if (head and tip != head and row['source'] == 'remote' and row['ref'] == 'content/pw/' + job
                    and row.get('current_view') and history.compare(tip, head) == 'ahead'):
                successors[job, tip] = head
        return successors

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
        before = deepcopy(self.data)
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
                # Legacy flat operations keep their original root across reconfiguration.
                for order in self.data['orders'].values():
                    order.setdefault('folder', self.data['folder'])
                self.data['folder'] = {'id': body['folder_id'], 'directory': str(folder)}
            elif action == 'start':
                job = self.start_order(body)
                self.save()
                return {**self.view, 'started': job}
            else:
                exact_keys(body, {'puzzle_id', 'request_id'})
                order = self.data['orders'].get(body['puzzle_id'])
                require(order and order['request_id'] == body['request_id'], 'Empfangsauftrag ist abgelaufen.')
                if action in ('cancel', 'acknowledge'):
                    allowed = ('done',) if action == 'acknowledge' else ('scan', 'stage', 'blocked', 'stale')
                    require(order['step'] in allowed, 'Begonnene Veröffentlichung zuerst fortsetzen.')
                    if action == 'acknowledge':
                        source = self.service.status()
                        completed = source.get('completion', {})
                        job = order['puzzle_id']
                        jid = next((m['current_job'] for m in source.get('motifs', []) if m['puzzle_id'] == job), None)
                        row = next((j for j in source.get('jobs', []) if jid and j['id'] == jid), None)
                        matched = (row and row['source'] == 'remote' and row['ref'] == 'content/pw/' + job
                                   and row['puzzle_id'] == job and order['result']['head'] in
                                   (row['commit'], row.get('receipt_ancestor')))
                        registered = completed.get('confirmed') and job in completed.get('completed_ids', [])
                        require(source.get('remote_confirmed') and (matched or registered),
                                'Bestätigten Arbeitsstand zuerst aus den Gitquellen laden.')
                    if order['step'] != 'stale':
                        self.discard_stage(order)
                    if action == 'cancel' and not order['source']['work_head'] and order['puzzle_id'] not in self.data['drafts'].values():
                        self.data['drafts'][str(uuid4())] = order['puzzle_id']
                    self.data['generations'][order['puzzle_id']] = str(uuid4())
                    del self.data['orders'][order['puzzle_id']]
                elif action == 'retry':
                    require(order['step'] in ACTIVE, 'Auftrag kann nicht fortgesetzt werden.')
                    order['paused'] = False
                else:
                    raise ValueError('Unbekannte Empfangsaktion.')
            self.save()
            return self.view
        except Exception:
            self.data = before
            raise
        finally:
            self.service.operation.release()

    def start_order(self, body):
        exact_keys(body, {'snapshot', 'jid', 'draft_id', 'action', 'candidate', 'inputs', 'findings', 'expected'})
        status = self.service.status()
        require(status.get('remote_confirmed') and status['snapshot'] == body['snapshot'], 'Aktuelle Remotequellen laden.')
        require(self.data['folder'], 'Privaten Drive-Stammordner in den Einstellungen speichern.')
        require(github_identity(self.service.repository.remote), 'Produktionsremote einrichten.')
        require(isinstance(body['inputs'].get('brief'), str), 'Motivbriefing erforderlich.')
        draft = body['draft_id']
        action = body['action']
        require(action in ('continue', 'rework', 'assessment', 'resume'), 'Unbekannte Bildhandlung.')
        # Resuming an offer never declares a candidate choice or a new finding decision.
        candidate = '' if action == 'resume' else body['candidate']
        findings = '{}' if action == 'resume' else body['findings']
        if body['jid']:
            require(not draft, 'Ein veröffentlichter Auftrag hat keinen lokalen Entwurf.')
            row = self.service.selected(body['jid'], body['snapshot'])
            require(row.get('_record') and row['_record']['format'] == current.findings.PUBLISHED,
                    'Aktuelle veröffentlichte v3-Quelle erforderlich.')
            job, record = row['puzzle_id'], row['_record']
            head = row['commit']
        else:
            contract.uuid4_text(draft)
            require(action in ('continue', 'resume') and not candidate, 'Neuer Entwurf beginnt mit dem Abschlussbild.')
            job = self.data['drafts'].get(draft)
            if not job:
                job = self.free_id(body['inputs']['brief'], status)
            record = None
            head = None
        prior = self.data['orders'].get(job)
        generation = prior['request_id'] if prior else self.data['generations'].get(job, '')
        signature = io.checksum(current.encoded([head, action, candidate, body['inputs'], findings]))
        if prior and action == 'resume' and prior['step'] != 'done':
            require(prior['source']['work_head'] == head, 'Quelle des offenen Auftrags hat sich geändert. Gebundenen Auftrag prüfen.')
            return job
        if prior and (signature == prior.get('signature') or action == 'resume' and prior['source']['work_head'] == head):
            require(prior['step'] != 'done' or action != 'resume', 'Veröffentlichten Stand für die Fortsetzung öffnen.')
            return job
        require(body['expected'] == generation, 'Auftrag inzwischen geändert. Aktuellen Auftrag prüfen.')
        require(not prior or prior['step'] in ('scan', 'stage', 'blocked', 'done'), 'Begonnene Veröffentlichung zuerst fortsetzen.')
        require(not prior or prior['step'] != 'done',
                'Auftrag bereits veröffentlicht. Aktuellen Stand öffnen.')
        role, intent, selection, target = 'reveal', 'offer', '', ''
        if record:
            state = record['state']
            assets = {a['id']: a['role'] for a in record['assets']}
            require(action != 'continue' or not record['blockers'], 'Auftragsweite Voraussetzung zuerst klären.')
            if action in ('rework', 'assessment'):
                role = assets.get(candidate)
                require(role in contract.PHASES, 'Konkretes Bild für diese Handlung wählen.')
                require(action != 'assessment' or role != 'background', 'Hintergrund am veröffentlichten Stand über PW-REMOTE bewerten.')
                target = candidate
                intent = 'correction' if action == 'rework' else 'assessment'
            elif action == 'resume':
                require(state in ('brief_ready', 'reveal_review', 'motif_review'),
                        'Diese Handlung verwendet den regulären Folgeauftrag.')
                if state == 'motif_review':
                    role = 'motif'
            elif state == 'reveal_review' and candidate:
                require(assets.get(candidate) == 'reveal', 'Abschlussbild wählen.')
                role, selection = 'motif', candidate
            elif state in ('raster_review', 'raster_ready'):
                require(candidate in {r['id'] for r in record['rasters']}, 'Qualifiziertes Raster wählen.')
                role, selection = 'background', candidate
            else:
                require(state in ('brief_ready', 'reveal_review') and not candidate,
                        'Diese Handlung verwendet den regulären Folgeauftrag.')
        self.writer.check_access()
        self.activate({'snapshot': body['snapshot'], 'jid': body['jid'], 'puzzle_id': job,
                       'phase': role, 'intent': intent, 'selection': selection, 'target': target,
                       'inputs': body['inputs'], 'findings': findings})
        order = self.data['orders'][job]
        order.update(signature=signature, draft_id=draft or None)
        if draft:
            self.data['drafts'][draft] = job
        return job

    def free_id(self, brief, status):
        title = unicodedata.normalize('NFKD', brief).encode('ascii', 'ignore').decode().lower()
        stem = re.sub('[^a-z0-9]+', '-', title).strip('-')[:48].rstrip('-') or 'motiv'
        used = set(self.data['orders']) | set(self.data['drafts'].values())
        used.update(row['puzzle_id'] for row in status.get('jobs', []))
        repo = self.service.removal
        job = 'pz-' + stem
        while True:
            if job not in used:
                main = repo.main_state(job)
                if not main['registered'] and not main['revisions'] and not repo.remote_head('refs/heads/content/pw/' + job):
                    return job
            job = 'pz-' + stem + '-' + uuid4().hex[:8]

    def activate(self, body):
        exact_keys(body, {'snapshot', 'jid', 'puzzle_id', 'phase', 'intent', 'target', 'inputs', 'selection', 'findings'})
        folder = self.data['folder']
        status = self.service.status()
        require(status.get('remote_confirmed') and status['snapshot'] == body['snapshot'], 'Aktuelle Remotequellen laden.')
        job, phase, intent = body['puzzle_id'], body['phase'], body['intent']
        current.path(job)
        require(phase in contract.PHASES and intent in ('offer', 'assessment', 'correction'), 'Ungültiger Auftragsumfang.')
        # Replacement authority was checked against the observed request ID.
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
        brief = contract.creative_brief(body['inputs'], phase, intent, new=not body['jid'])
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
                require(not body['selection'] or phase in contract.PRIOR and
                        record['selected'][contract.PRIOR[phase]] == body['selection'], 'Andere Vorauswahl ist bereits gebunden.')
            if intent != 'offer':
                require(target in {a['id'] for a in record['assets'] if a['role'] == phase}, 'Konkrete Korrektur-/Bewertungsgrundlage erforderlich.')
            reopening = intent == 'correction' and target == record['selected'][phase]
            require(reopening or not record['selected'][phase] and current.PHASES.index(record['state']) <= current.PHASES.index(contract.PHASES[phase]),
                    'Die gewählte Produktionsphase ist abgeschlossen.')
        else:
            require(head is None and phase == 'reveal' and intent == 'offer' and not body['selection'], 'Neue unbenutzte Produktions-ID erforderlich.')
            source_hash = None
            limits = {'raster_candidates': 6, 'repair_rounds': 2, 'image_corrections': 2}
        brief_length = len(brief)
        if body['jid']:
            brief_length += len(record['brief']) + (2 if brief else 0)
        require(brief_length <= 16384, 'Gesamtes Motivbriefing zu lang. Neue Eingaben kürzen.')
        require(not edits, 'Befund ist veraltet oder gehört nicht zu dieser Auswahl.')
        require(intent != 'offer' or not target, 'Angebot enthält eine unerwartete Zielvariante.')
        order = {'request_id': str(uuid4()), 'puzzle_id': job, 'phase': phase, 'intent': intent, 'target': target,
                 'source': {'main_commit': main['commit'], 'work_head': head, 'record_sha256': source_hash},
                 'choice': choice, 'declarations': declarations, 'limits': limits, 'brief': brief, 'inputs': body['inputs'], 'test_only': False, 'step': 'scan',
                 'status': 'Wartet auf die Lieferung.', 'files': {}, 'paused': False}
        binding = {k: order[k] for k in ('request_id', 'puzzle_id', 'phase', 'intent', 'target', 'source', 'brief', 'choice', 'declarations', 'limits')}
        # The prompt contains only the remote folder binding.
        order['folder'] = dict(folder)
        order['child'] = job
        order['prompt'] = contract.producer_prompt(folder['id'], binding, body['inputs']['reference'])
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
            order.update(manifest=name, manifest_hash=manifest_id['sha256'], step='stage',
                         status='Liefermanifest eingetroffen. Originaldateien werden geprüft.')
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
        binding = order.get('folder', self.data['folder'])
        published = False
        try:
            folder = None
            if order['step'] in ('scan', 'stage', 'cleanup'):
                folder = files.destination(binding, order.get('child'))
            if order['step'] != 'cleanup':
                if order['step'] in ('scan', 'stage'):
                    value = self.receive(order, folder)
                else:
                    raw = io.read(self.stage(order), order['manifest'], 2 * current.LIMIT)
                    require(io.checksum(raw) == order['manifest_hash'], 'Gesicherte Lieferbytes verändert.')
                    value = contract.envelope(raw, order['manifest'], order)
                self.message(order, 'Übernahme läuft. Arbeitsstand und Originale werden geprüft und veröffentlicht.')
                result = self.writer.publish(order, value['request'], self.stage(order), self.save)
                order.update(step='cleanup', result=result, remaining=list(order['files']),
                             status='GitHub-Veröffentlichung bestätigt. Eingangsbereinigung läuft.')
                self.save()
                published = True
            folder = files.destination(binding, order.get('child'))
            for name in order['remaining'][:]:
                files.retire(folder, name, order['files'][name])
                order['remaining'].remove(name)
                self.save()
            self.discard_stage(order)
            order.update(step='done', status='Veröffentlicht. Lokaler Eingang bereinigt. Drive synchronisiert separat.')
            order.pop('files')
            self.save()
        except StaleBuild as exc:
            order.update(step='stale', paused=True)
            self.message(order, str(exc))
        except files.Waiting as exc:
            self.message(order, str(exc) or 'Wartet auf vollständige Dateien.')
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
