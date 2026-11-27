"""Recover the local half of a publication in its owned detached worktree."""
import os

from . import production_git_workspace as ws, publish_git as transport
from .production_workspace.sources import GitSource, check_commit
from .puzzle_production import catalog_io as io, current_authoring as current
from .puzzle_production.authoring_builder import write_new
from .puzzle_production.authoring_package import require

JOURNAL = 'pw-local-publish.json'
RECEIPT = 'pw-local-last-publish.json'


def previous_operation(root, job, expected):
    state = ws.gitdir(root)
    for filename in (JOURNAL, RECEIPT):
        raw = io.read(state, filename, 8192, missing=True)
        if raw:
            value = io.json_bytes(raw, 8192)
            if value['job'] == job and value['expected'] == expected and value['path'] == str(root):
                return value
            require(filename != JOURNAL, 'Resume the owning publish operation')
    return None


def recover(root, job, expected, main, check_refs):
    """Complete only the already-pushed local publication owned by this job."""
    from . import work_publish as publisher
    state = ws.gitdir(root)
    value = io.json_bytes(io.read(state, JOURNAL, 8192), 8192)
    prior = value.get('expected')
    target = value.get('target')
    require(expected is not None and expected == target and previous_operation(root, job, prior) == value,
            'Own publication pending; retry its original publisher command and read back the work ref')
    require(ws.git(root, 'show', '-s', '--format=%B', target) == 'Publish current ' + job,
            'Bound remote or Inbox publication pending; retry its original request')
    check_refs()
    with current.qualification.operation():
        operation = Publication(root, job, prior, main, expected)
        if not operation.value['confirmed']:
            owner = {'operation': 'publish', 'job': job, 'expected': prior, 'draft': value['draft']}
            publisher.check_catalog_owner(root, owner)
            with publisher.catalog_writer(root, main, owner=owner):
                publisher.finish_pushed_request(root, job, prior, main, target)
        check_refs()
        return operation.finish(target)


def checkpoint(step):
    """Interruption boundary for the managed publisher."""


class Publication:
    def __init__(self, root, job, expected, main, remote):
        self.root = root
        self.state = ws.gitdir(root)
        self.job = job
        self.name = current.path(job)
        self.expected = expected
        self.source = GitSource(root)
        require(ws.git(root, 'rev-parse', '--abbrev-ref', 'HEAD') == 'HEAD', 'Job worktree must remain detached')
        pending = io.read(self.state, JOURNAL, 8192, missing=True)
        raw = io.read(root, self.name, current.LIMIT)
        if pending:
            self.value = io.json_bytes(pending, 8192)
            require(self.value['job'] == job and self.value['expected'] == expected
                    and self.value['path'] == str(root), 'Resume the owning publish operation')
            check_commit(self.value['parent'])
            if self.target:
                check_commit(self.target)
            require(remote in (expected, self.target), 'Different remote publication; preserve the local operation')
        else:
            parent = expected or main
            ws.check_work(root, job)
            require(remote == expected and ws.git(root, 'rev-parse', 'HEAD') == parent
                    and ws.git(root, 'write-tree') == ws.git(root, 'rev-parse', parent + '^{tree}'),
                    'Stale worktree, Git index or expected remote SHA')
            self.value = {'path': str(root), 'job': job, 'expected': expected, 'parent': parent,
                          'draft': io.checksum(raw), 'index': io.file_hash(root, current.INDEX, 8 * current.LIMIT),
                          'target': None, 'confirmed': False}
            write_new(self.state / JOURNAL, current.encoded(self.value))
        self.verify()

    @property
    def target(self):
        return self.value['target']

    def verify(self):
        parent = self.value['parent']
        heads = {parent}
        drafts = {self.value['draft']}
        indices = {self.value['index']}
        if self.target:
            heads.add(self.target)
            drafts.add(io.checksum(self.source.read(self.target, self.name, current.LIMIT)))
            indices.add(io.checksum(self.source.read(self.target, current.INDEX, 8 * current.LIMIT)))
        require(ws.git(self.root, 'rev-parse', 'HEAD') in heads and ws.git(self.root, 'write-tree') in
                {ws.git(self.root, 'rev-parse', h + '^{tree}') for h in heads}, 'Foreign local HEAD or staged files')
        require(io.file_hash(self.root, self.name, current.LIMIT) in drafts and
                io.file_hash(self.root, current.INDEX, 8 * current.LIMIT) in indices,
                'Foreign local record or index during publication')
        ws.check_work(self.root, self.job, resumed=True)

    def save(self):
        current._atomic(self.state, JOURNAL, current.encoded(self.value))

    def bind(self, target):
        if self.target:
            require(ws.git(self.root, 'rev-parse', target + '^{tree}') ==
                    ws.git(self.root, 'rev-parse', self.target + '^{tree}'), 'Different publication candidate')
            return self.target
        self.verify()
        self.value['target'] = target
        self.save()
        return target

    def finish(self, target):
        require(self.target == target, 'Publication does not match the owned local transaction')
        self.value['confirmed'] = True
        self.save()
        checkpoint('readback')
        self.verify()
        root = self.root
        if ws.git(root, 'rev-parse', 'HEAD') != target:
            ws.git(root, 'update-ref', '--no-deref', 'HEAD', target, self.value['parent'])
        checkpoint('head')
        self.verify()
        entries = transport.git(root, 'ls-tree', '-z', target, '--', self.name, current.INDEX)
        require(len(entries.rstrip(b'\0').split(b'\0')) == 2, 'Missing published metadata')
        transport.git(root, 'update-index', '-z', '--index-info', data=entries)
        checkpoint('index')
        self.verify()
        for name, limit in ((self.name, current.LIMIT), (current.INDEX, 8 * current.LIMIT)):
            raw = self.source.read(target, name, limit)
            if io.read(root, name, limit) != raw:
                current._atomic(root, name, raw)
            require(io.read(root, name, limit) == raw, 'Published metadata readback differs')
            checkpoint('record' if name == self.name else 'authoring-index')
        require(ws.git(root, 'write-tree') == ws.git(root, 'rev-parse', target + '^{tree}'),
                'Local Git index differs from publication')
        require(io.read(self.state, JOURNAL, 8192) == current.encoded(self.value), 'Local owner changed')
        os.replace(self.state / JOURNAL, self.state / RECEIPT)
        return target
