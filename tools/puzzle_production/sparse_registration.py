"""Bind sparse registration reads to the complete Git namespace, including the index."""
import subprocess

from .authoring_package import require
from . import catalog_io as io


class TrackedPaths:
    def __init__(self, root):
        self.root = root
        self.names = None
        if not (root / '.git').exists():
            return
        result = subprocess.run(['git', '-C', str(root), 'config', '--bool', '--get', 'core.sparseCheckout'],
                                capture_output=True, check=False)
        require(result.returncode in (0, 1), 'Cannot determine sparse checkout configuration')
        if result.stdout.strip() != b'true':
            return
        self.index = io.external(self.git('rev-parse', '--path-format=absolute', '--git-path', 'index').decode().strip())
        self.head = self.git('rev-parse', 'HEAD').strip().decode('ascii')
        self.stamp = self.signature()
        self.names = {}
        tree = {}
        for row in self.git('ls-tree', '-r', '-z', self.head).split(b'\0')[:-1]:
            meta, raw = row.split(b'\t', 1)
            mode, _, oid = meta.split()
            tree[raw] = (mode, oid)
        index = {}
        for row in self.git('ls-files', '--stage', '-z').split(b'\0')[:-1]:
            meta, raw = row.split(b'\t', 1)
            mode, oid, stage = meta.split()
            require(stage == b'0', 'Unmerged sparse registration index')
            index[raw] = (mode, oid)
        require(index == tree, 'Staged sparse changes conflict with registration')
        for raw, (mode, _) in tree.items():
            parts = raw.decode().split('/')
            for i in range(1, len(parts) + 1):
                path = '/'.join(parts[:i])
                entry = (path, mode if i == len(parts) else b'tree')
                self.names.setdefault(path.casefold(), set()).add(entry)
        self.recheck()

    def git(self, *args):
        return subprocess.check_output(['git', '--no-replace-objects', '-C', str(self.root), *args])

    def signature(self):
        stat = self.index.stat()
        return stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns

    def recheck(self):
        if self.names is not None:
            require(self.signature() == self.stamp and self.git('rev-parse', 'HEAD').strip().decode() == self.head,
                    'Sparse Git HEAD or index changed during registration')

    def check(self, name):
        if self.names is None:
            return
        parts = name.split('/')
        for i in range(1, len(parts) + 1):
            path = '/'.join(parts[:i])
            entries = self.names.get(path.casefold())
            if not entries:
                return
            if i < len(parts):
                require(entries == {(path, b'tree')}, 'Occupied Git parent or case collision: ' + path)
            else:
                require(entries in ({(path, b'100644')}, {(path, b'100755')}) and io.safe(self.root, path).is_file(),
                        'Occupied sparse Git path; materialize the bound file: ' + path)
