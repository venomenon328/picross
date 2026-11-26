"""Adapter from an activated inbox order to the installed PW-LOCAL writer."""
from pathlib import Path

from tools import production_git_workspace as ws, publish_git as git, work_publish as publisher
from tools.production_worktree_publish import previous_operation
from tools.puzzle_production import catalog_io as io, current_authoring as current
from tools.puzzle_production.authoring_package import require
from . import deliveries
from .inbox_contract import REPOSITORY, delta
from .sources import GitSource


class Writer:
    repository = REPOSITORY

    def __init__(self, state):
        self.root = Path(state) / 'import-writer'

    def publish(self, order, request, stage, save):
        require(publisher.REPO == self.repository and git.REMOTE == 'https://github.com/' + self.repository + '.git',
                'Abweichender Writer oder Git-Zielort.')
        self.root.mkdir(exist_ok=True)
        job = order['puzzle_id']
        expected = order['source']['work_head']
        with publisher.publisher_auth('gh'), current.qualification.operation():
            _, db = ws.store_for(self.root, self.repository)
            main = git.remote_head(db, 'refs/heads/main')
            actual = git.remote_head(db, 'refs/heads/content/pw/' + job)
            require(main, 'GitHub-main ist nicht erreichbar.')
            git.git(db, 'fetch', '--no-tags', '--', git.REMOTE, main)
            source = GitSource(db)
            require(job not in deliveries.registered_ids(source, main), 'ID ist registriert. Bitte den Bestandseditor verwenden.')
            if main != order['source']['main_commit']:
                # Re-evaluate the pinned contracts and any catalog entry for this job.
                pinned = order['source']['main_commit']
                git.git(db, 'fetch', '--no-tags', '--', git.REMOTE, pinned)
                git.git(db, 'merge-base', '--is-ancestor', pinned, main)
                require(not git.git(db, 'diff', '--name-only', pinned, main, '--', 'AGENTS.md',
                                    'docs/production', 'docs/tools/PW_B_CONTRACT.md', 'docs/tools/PW_IMPORT.md',
                                    'content/authoring/' + job, 'content/puzzles/' + job + '.json'),
                        'Auftragsgrundlage auf main verändert. Auftrag aktualisieren.')
            require(not source.read(main, current.path(job), current.LIMIT, missing=True),
                    'Der Job hat bereits einen Arbeitsrecord auf main.')
            name = current.path(job)
            if order['step'] == 'publish':
                work = io.safe(self.root, 'picross-production/job-' + job)
                owner = ws.read_binding(work)
                require(owner and owner['job'] == job and owner['role'] == 'job' and owner['store'] == str(db),
                        'Eigener Writer-Arbeitsstand fehlt.')
                op = previous_operation(work, job, expected)
                require(not op or op['draft'] == order['draft_sha256'], 'Publikationsjournal gehört zu einem anderen Draft.')
                require(actual == expected or op and op['target'] == actual, 'Ein anderer Arbeitsstand wurde veröffentlicht.')
                if actual == expected:
                    require(io.file_hash(work, name, current.LIMIT) == order['draft_sha256'], 'Lokaler Draft verändert.')
            else:
                require(actual == expected, 'Arbeitsbranch ist fortgeschritten. Auftrag erneut binden.')
                previous = None
                raw = publisher.remote_record(expected, job) if expected else None
                require(io.checksum(raw) == request['expected'], 'Gebundener Vorgängerrecord stimmt nicht überein.')
                if raw:
                    previous = publisher.local_record(publisher.bound_record(raw, job))
                delta(order, request, previous)
                if order['step'] == 'build':
                    work = io.safe(self.root, 'picross-production/job-' + job)
                else:
                    paths = ws.prepare(self.root, job, main, main, expected)
                    work = Path(paths['job'])
                    if expected:
                        publisher.resume(work, job, expected, auth='gh')
                    order['step'] = 'build'
                    save()
                # Hydration strips release locators. Translate the verified remote
                # hash to the canonical local predecessor before the builder CAS.
                local_hash = io.checksum(current.encoded(previous)) if previous else None
                current.build({**request, 'expected': local_hash}, stage, work)
                order.update(step='publish', draft_sha256=io.file_hash(work, name, current.LIMIT))
                save()
            context = {'main': main, 'id': order['request_id']}
            head = publisher.push_job(work, job, expected, auth='gh', remote_request=context)
            raw = publisher.remote_record(head, job)
            result = publisher.bound_record(raw, job)
            require(io.checksum(current.encoded(publisher.local_record(result))) == order['draft_sha256'] and
                    raw == GitSource(work).read(head, name, current.LIMIT), 'Record-Readback weicht vom eigenen Draft ab.')
            current.Checked(result, lambda n, limit: GitSource(work).read(head, n, limit))
            require(git.remote_head(db, 'refs/heads/content/pw/' + job) == head, 'Arbeitsref nach Veröffentlichung fortgeschritten.')
            return {'head': head, 'record_sha256': io.checksum(raw), 'release_id': result['work_release']['id']}
