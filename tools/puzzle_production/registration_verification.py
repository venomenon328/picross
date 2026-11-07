"""Private, invocation-local proof reuse. Never an authorization or recovery input."""
from contextlib import contextmanager
from copy import deepcopy
import os
from pathlib import Path
import stat
import sys
import threading

from . import catalog_io as io, operation_diagnostics as diagnostic
from .authoring_package import file_table, require

_active = {}


def require_context(value):
    require(type(value) is _Verification, "Untrusted registration verification context")
    value._live()


def inventory(directory, *, contents=True):
    """Fresh safe tree, including empty directories and actual file identities."""
    import time
    root = io.external(directory)
    before = root.lstat()
    require(stat.S_ISDIR(before.st_mode), "Verification tree is not a directory")
    files = file_table(root, time.monotonic() + 300)
    nodes = {".": (before.st_dev, before.st_ino)}
    hashes = {}
    for path in sorted(root.rglob("*")):
        name = path.relative_to(root).as_posix()
        info = io.safe(root, name).lstat()
        require(stat.S_ISDIR(info.st_mode) or name in files, "Verification tree changed")
        nodes[name] = ((info.st_dev, info.st_ino) if stat.S_ISDIR(info.st_mode)
                       else (*io.signature(info), info.st_ctime_ns))
        if name in files and contents:
            hashes[name] = io.file_hash(root, name)
            require(nodes[name] == (*io.signature(path.lstat()), path.lstat().st_ctime_ns),
                    "Verification source changed while binding")
    require(nodes["."] == (root.lstat().st_dev, root.lstat().st_ino), "Verification tree exchanged")
    require(set(files) == {n for n in nodes if n != "." and not stat.S_ISDIR((root / n).lstat().st_mode)},
            "Verification inventory changed")
    return nodes, hashes


def _methods():
    """Bind actual implementation/configuration bytes, not method names alone."""
    import PIL
    from PIL import _imaging, features
    base = Path(__file__).parent
    paths = {p for p in base.iterdir() if p.suffix in (".py", ".json")}
    paths.update((Path(sys.executable).resolve(), Path(_imaging.__file__).resolve()))
    library = Path(sys.base_prefix) / ("python%d%d.dll" % sys.version_info[:2])
    if library.is_file(): paths.add(library.resolve())
    bindings = {}
    for path in sorted(paths):
        info = io.safe(path.parent, path.name).lstat()
        identity = (*io.signature(info), info.st_ctime_ns)
        checksum = io.file_hash(path.parent, path.name)
        after = path.lstat()
        require(identity == (*io.signature(after), after.st_ctime_ns), "Verification method exchanged while binding")
        bindings[str(path)] = identity, checksum
    return sys.version, PIL.__version__, features.version("zlib"), bindings


class _Verification:
    def __reduce_ex__(self, protocol):
        raise TypeError("Registration verification cannot be serialized/copied")

    def _live(self):
        require(_active.get(id(self)) is self and self.owner == (os.getpid(), threading.get_ident()),
                "Inactive/foreign registration verification context")
        info = self.root.lstat()
        require((info.st_dev, info.st_ino) == self.root_identity, "Verification checkout exchanged")

    @contextmanager
    def _checking(self):
        try:
            self._live()
            yield
        except BaseException:
            _active.pop(id(self), None)
            raise

    def _sources(self):
        require(inventory(self.original) == self.original_state, "Original export changed/exchanged")
        require(inventory(self.stage) == self.stage_state, "Verified staging changed/exchanged")
        require(_methods() == self.methods, "Verification implementation/method changed")
        if self.external:
            path, raw, identity = self.external
            require(io.read(path.parent, path.name, 64 * 1024 * 1024) == raw and
                    (*io.signature(path.lstat()), path.lstat().st_ctime_ns) == identity,
                    "Checked difficulty source changed/exchanged")

    def bind(self, root, journal, additions):
        from . import catalog_transaction as tx, catalog_publication as pub
        with self._checking():
            require(self.raw is None and io.external(root) == self.root, "Verification already bound/foreign checkout")
            require(journal["operation"] == "registration" and tx.sd2(journal) and not journal["replacements"],
                    "Verification requires a new current registration")
            before, after = (io.json_bytes(journal[s][tx.REGISTRY].encode(), 8 * 1024 * 1024) for s in ("old", "new"))
            self.package = tx._delta(journal, before, after)
            require(before == self.snapshot["registry"] and journal["retained"] == self.snapshot["retained"] and
                    all(journal["old"].get(n) == (b.decode() if b is not None else None)
                        for n, b in self.snapshot["texts"].items()), "Verification source snapshot differs")
            require(all(tx.read(root, n) == b for n, b in self.snapshot["texts"].items()) and
                    all(io.file_hash(root, n) == h for n, h in self.snapshot["retained"].items()) and
                    tx.namespaces(root, before) == self.snapshot["namespaces"], "Verification sources changed")
            expected = {self.package + "/" + n: self.stage / n for n in self.stage_state[1]}
            manifest = self.result[0]
            expected["game/" + manifest["reveal"].removeprefix("runtime/")] = self.stage / manifest["reveal"]
            require(additions == expected and set(journal["additions"]) == set(expected), "Verification addition mapping differs")
            require(all(journal["additions"][n] == self.stage_state[1][p.relative_to(self.stage).as_posix()]
                        for n, p in expected.items()), "Verification addition bytes differ")
            self._sources()
            self.raw = pub.journal_bytes(journal)
            self.additions = dict(expected)

    def writer(self, root, journal, additions):
        from .catalog_publication import journal_bytes
        with self._checking():
            require(self.raw is not None and io.external(root) == self.root and
                    journal_bytes(journal) == self.raw and additions == self.additions,
                    "Verification journal/checkout/additions differ")
            self._sources()

    def addition(self, name, source):
        with self._checking():
            require(self.raw is not None and self.additions.get(name) == source,
                    "Unbound verification addition")
            require(inventory(self.stage, contents=False)[0] == self.stage_state[0],
                    "Verified staging changed/exchanged before addition")

    def checkout(self, root, raw):
        with self._checking():
            require(self.raw is not None and raw == self.raw and io.external(root) == self.root,
                    "Verification checkout/journal differs")

    @diagnostic.measured("Verified package readback", attempt_counter="verified_package_check_attempts")
    def written(self, root, package, raw):
        with self._checking():
            self.checkout(root, raw)
            require(package == self.package, "Verification package differs")
            self._sources()
            nodes, hashes = inventory(io.safe(root, package))
            expected_dirs = {"."} | {parent.as_posix() for n in hashes for parent in Path(n).parents}
            require(hashes == self.stage_state[1] and set(nodes) == set(hashes) | expected_dirs,
                    "Written package differs from verified bytes/inventory")
            require(self.published is None or nodes == self.published, "Published verification package exchanged")
            self.published = nodes
            diagnostic.count("verified_package_reuses")
            return deepcopy(self.result)


@contextmanager
def verified(stage, original, original_state, root, snapshot, expected, external=None):
    """Only this successful full replay can mint an active internal instance."""
    from .target_adapter import verify_export
    context = _Verification()
    context.owner = (os.getpid(), threading.get_ident())
    context.stage, context.original, context.root = map(io.external, (stage, original, root))
    root_info = context.root.lstat()
    context.root_identity = root_info.st_dev, root_info.st_ino
    context.original_state = deepcopy(original_state)
    context.snapshot = deepcopy(snapshot)
    context.raw = None
    context.published = None
    context.external = None
    if external:
        path, raw = external
        context.external = (path, raw, (*io.signature(path.lstat()), path.lstat().st_ctime_ns))
    context.stage_state = inventory(context.stage)
    context.methods = _methods()
    context.result = deepcopy(verify_export(context.stage))
    # checked_at_utc is operational, not a differing candidate or authority.
    manifest, report = context.result
    prior_manifest, prior_report = expected
    require(manifest == prior_manifest and all(report[k] == prior_report[k] for k in report
            if k not in ("checked_at_utc", "tool", "fresh_verification")), "Staging replay differs from checked input")
    context._sources()
    _active[id(context)] = context
    try:
        yield context
    finally:
        _active.pop(id(context), None)
