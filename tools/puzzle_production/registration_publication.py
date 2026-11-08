"""RI-C v6 registration boundaries; no proof authority or persistent cache.

Expectations come from the validated journal. Every comparison reads the current
filesystem. Only this generation opts in; the shared historical writer stays
unchanged. The cooperative lock cannot prevent arbitrary external OS writers.
"""
from pathlib import Path

from . import catalog_io as io, catalog_publication as pub
from . import catalog_transaction as tx, catalog_method as method
from . import operation_diagnostics as diagnostic
from .authoring_package import require


def supports(journal):
    return (isinstance(journal, dict)
            and journal.get("format") == "picross-registration-journal-v6"
            and journal.get("operation") == "registration")


def hashes(texts):
    return {name: io.checksum(text.encode() if text is not None else None)
            for name, text in texts.items()}


class Guards:
    """Exact phase expectations, never trusted observations of unchanged files."""

    def __init__(self, root, journal, raw, additions=None, *, recovering=False, staged=None):
        require(supports(journal), "Phased guards require registration v6")
        self.root, self.raw = root, raw
        self.view = pub._JournalView(journal, raw)
        self.j = self.view.j
        require(not self.j["replacements"], "Registration cannot replace binaries")
        self.additions = additions or {}
        self.staged = staged
        self.expected = {**hashes(self.j["old"]), **dict.fromkeys(self.j["additions"])}
        if recovering:
            # R0 does not reuse any forward state or B verification context.
            # Validate each observation independently before accepting it as the
            # exact current phase; the subsequent GR0 rechecks the whole view.
            for name in self.expected:
                data = self.read(name)
                allowed = ({None, self.j["additions"][name]} if name in self.j["additions"] else
                           {hashes({name: self.j[side][name]})[name] for side in ("old", "new")})
                require(io.checksum(data) in allowed, "Foreign recovery target: " + name)
                self.expected[name] = io.checksum(data)
        self.packages = {e["production"]["package"] for r in self.view.registries for e in r["entries"]}
        self.allowed_files = set(self.j["old"]) | set(self.j["retained"]) | set(self.j["additions"]) | set(self.view.temps.values())
        self.allowed_dirs = {p.as_posix() for n in self.allowed_files for p in Path(n).parents}
        self.allowed_dirs |= {"content/difficulty/reports", "content/added/reports"}
        self.temp_parents = {Path(n).parent.as_posix() for n in self.view.temps.values()}

    def read(self, name):
        return (io.read(self.root, name, 64 * 1024 * 1024, missing=True)
                if name in self.j["additions"] else tx.read(self.root, name))

    def journal(self, *, before_lock=False):
        require(pub.read_journal(self.root) == (None if before_lock or self.staged else self.raw),
                "Journal changed; preserve all transaction files")
        require(pub.staging(self.root) == ([self.staged] if self.staged else []),
                "Foreign journal staging; preserve all transaction files")
        if self.staged:
            require(pub.read_journal(self.root, self.staged) == self.raw, "Journal staging changed")

    def tree(self, name, *, recursive=True):
        directory = io.safe(self.root, name)
        if not directory.exists():
            return
        require(directory.is_dir(), "Transaction namespace is not a directory: " + name)
        for child in directory.rglob("*") if recursive else directory.iterdir():
            relative = child.relative_to(self.root).as_posix()
            child = io.safe(self.root, relative)
            require(relative in (self.allowed_dirs if child.is_dir() else self.allowed_files),
                    "Foreign transaction namespace entry: " + relative)

    def temp_namespace(self, parent):
        directory = io.safe(self.root, parent)
        if directory.exists():
            for child in directory.iterdir():
                if child.name.casefold().startswith(".registration-"):
                    name = child.relative_to(self.root).as_posix()
                    require(name in self.view.temps.values() or name in (tx.LOCK, self.staged),
                            "Foreign transaction temporary name: " + name)
                    io.safe(self.root, name)

    def full(self, boundary, *, before_lock=False, no_temps=False):
        pub._checkpoint(boundary)
        diagnostic.count("catalog_boundary_attempts")
        with diagnostic.phase(boundary):
            self.journal(before_lock=before_lock)
            # Both actual frozen source sets are read/validated, even when the
            # optional production default is absent. Names alone prove nothing.
            for name in method.METHODS:
                method.method_hash(name)
            temps = pub.guard(self.root, self.j, raw=self.raw, expected=self.expected,
                              old_only=before_lock or self.staged is not None,
                              additions=self.additions, _view=self.view)
            for name in self.packages | {"content/difficulty", "content/added", "content/reveals"}:
                self.tree(name)
            for name in self.temp_parents:
                self.temp_namespace(name)
            require(not no_temps or not temps, "Transaction temporaries remain")
            self.journal(before_lock=before_lock)
        diagnostic.count("catalog_boundaries", work=boundary + " verified")

    def target(self, name, *, source=None):
        """No catalog inventory here: only journal, this target and its subtree."""
        diagnostic.count("target_guards")
        self.journal()
        require(io.checksum(self.read(name)) == self.expected[name], "Transaction target phase changed: " + name)
        temporary = self.view.temps[name]
        pub.check_temps(self.root, self.j, self.raw, additions=self.additions,
                        temps={name: temporary}, restore=self.view.restore)
        self.temp_namespace(Path(name).parent.as_posix())
        if name.startswith("content/packages/") or name.startswith("content/difficulty/pz-"):
            self.tree(Path(name).parent.as_posix(), recursive=False)
        if source is not None:
            require(self.additions.get(name) == source and
                    io.file_hash(source.parent, source.name) == self.j["additions"][name],
                    "Staged package changed before publication")
        io.safe(self.root, name)
        io.safe(self.root, temporary)

    def written(self, name, data):
        # Read back actual own bytes before advancing the phase expectation.
        require(self.read(name) == data, "Published target readback differs: " + name)
        self.expected[name] = io.checksum(data)

    def write(self, name, data, *, source=None):
        check = lambda: self.target(name, source=source)
        check()
        pub.write(self.root, name, data, self.view.temps[name], check,
                  package_addition=name in self.j["additions"])
        self.written(name, data)

    def cleanup(self):
        # Check precisely the temp about to be removed again, not just a prior
        # inventory. Unknown files/directories are never recursively deleted.
        for name, temporary in sorted(self.view.temps.items()):
            if io.read(self.root, temporary, 64 * 1024 * 1024, missing=True) is not None:
                self.target(name)
                target = io.safe(self.root, temporary)
                target.unlink()
                pub.sync_directory(target.parent)


def execute(root, journal, additions, *, fail_step=None, under_lock=None, verification=None):
    from .content_registry import check_checkout
    if verification is not None:
        from .registration_verification import require_context
        require_context(verification)
    diagnostic.begin_segment("P0")
    tx.validate_journal(root, journal, before_write=True)
    raw = pub.journal_bytes(journal)
    state = Guards(root, journal, raw, additions)
    j, temps = state.j, state.view.temps
    state.journal(before_lock=True)
    for name in {tx.LOCK, *temps}:
        parent = io.safe(root, name).parent
        while not parent.exists():
            parent = parent.parent
        pub.sync_directory(parent)
    if pub.os.name != "nt":
        require(hasattr(pub.ctypes.CDLL(None), "renameat2"), "Atomic no-replace rename unavailable")
    pub.addition_preflight(root, [temps[n] for n in j["additions"]])
    if verification is not None:
        verification.writer(root, j, additions)
    state.full("G0", before_lock=True, no_temps=True)
    pub._checkpoint("P0")
    diagnostic.begin_segment("P1")
    stage_name = "content/.registration-journal-" + io.checksum(raw) + ".tmp"
    stage = io.safe(root, stage_name)
    state.journal(before_lock=True)
    with stage.open("xb") as stream:
        d = diagnostic.current.get()
        if d:
            d.outcome = "recovery-required"
            d.journal_state = {"journal": "staging-incomplete", "lock": "absent"}
        for offset in range(0, len(raw), io.CHUNK):
            io.tick()
            stream.write(raw[offset:offset + io.CHUNK])
            pub._checkpoint("journal-prefix")
        stream.flush()
        pub.fsync(stream.fileno())
    require(pub.read_journal(root, stage_name) == raw, "Journal staging readback differs")
    if d:
        d.journal_state["journal"] = "staging-complete"
    pub._checkpoint("journal-complete")
    require(pub.read_journal(root, stage_name) == raw and pub.staging(root) == [stage_name], "Journal staging changed")
    pub.rename(io.safe(root, stage_name), io.safe(root, tx.LOCK), replace=False)
    if d:
        d.journal_state = {"journal": "present", "lock": "present"}
    pub._checkpoint("P1")
    diagnostic.begin_segment("P2")
    state.full("G2", no_temps=True)
    # A foreign P2 view never enters automatic recovery or active mutation.
    try:
        if under_lock:
            under_lock()
        pub._checkpoint("P2")
        diagnostic.begin_segment("P3")
        for index, name in enumerate(sorted(j["additions"])):
            if verification is not None:
                verification.addition(name, additions[name])
            source = additions[name]
            data = io.read(source.parent, source.name, 64 * 1024 * 1024)
            require(io.checksum(data) == j["additions"][name], "Staged package changed")
            state.write(name, data, source=source)
            pub._checkpoint("P3", name)
            if index == 0 and fail_step == "crash":
                raise InterruptedError("Injected registration interruption")
            if index == 0 and fail_step == "files":
                raise OSError("Injected registration interruption")
        if fail_step == "crash-package":
            raise InterruptedError("Injected registration crash after package")
        package = tx._delta(j, *state.view.registries)
        if verification is None:
            from .target_adapter import verify_export
            verify_export(io.safe(root, package))
        else:
            verification.written(root, package, raw)
        diagnostic.begin_segment("P4")
        names = sorted(n for n in j["new"] if n != tx.RUNTIME and j["old"][n] != j["new"][n])
        for name in [*names, tx.RUNTIME]:
            if name == tx.RUNTIME:
                diagnostic.begin_segment("P5")
                state.full("G5a")
            if j["old"][name] != j["new"][name]:
                data = j["new"][name].encode() if j["new"][name] is not None else None
                state.write(name, data)
            pub._checkpoint("P5" if name == tx.RUNTIME else "P4", name)
            if (fail_step == "crash-" + name or name == tx.REGISTRY and fail_step == "crash-index"
                    or name == tx.RUNTIME and fail_step == "crash-runtime"):
                raise InterruptedError("Injected transaction interruption: " + name)
            if fail_step == name or name == tx.REGISTRY and fail_step == "index":
                raise OSError("Injected registration failure: " + name)
        check_checkout(root, replay=True, pending_journal=raw,
                       **({"_verification": verification} if verification is not None else {}))
        state.full("G5b")
        diagnostic.begin_segment("P6")
        state.cleanup()
        pub._checkpoint("P6")
        state.full("G6", no_temps=True)
        io.safe(root, tx.LOCK).unlink()
        pub.sync_directory(root / "content")
        diagnostic.durable("completed")
    except InterruptedError:
        raise
    except BaseException as original:
        # Use exactly the independently classified recovery and separate budget
        # of the shared writer; no forward expectations or B context cross over.
        token = io._deadline.set(None)
        forward = diagnostic.frame.get()
        if forward is not None:
            forward.next_segment()
        seconds = forward.recovery_seconds if forward is not None else None
        operation_token = diagnostic.frame.set(None)
        try:
            from .content_registry import recover as classified_recover
            classified_recover(root, recovery_seconds=seconds)
        except BaseException as recovery_error:
            if isinstance(original, (pub.Aborted, KeyboardInterrupt)):
                raise original from recovery_error
            raise
        finally:
            diagnostic.frame.reset(operation_token)
            io._deadline.reset(token)
        raise


def recover(root, journal, raw, *, staged=None):
    from .content_registry import check_checkout
    diagnostic.begin_segment("R0")
    _, runtime = tx.validate_journal(root, journal, before_write=staged is not None)
    state = Guards(root, journal, raw, recovering=staged is None, staged=staged)
    state.full("GR0", no_temps=staged is not None)
    pub._checkpoint("R0")
    if staged is None:
        diagnostic.begin_segment("R1")
        state.cleanup()
        for name in sorted(state.j["old"]):
            if name == tx.RUNTIME:
                continue
            data = state.j["old"][name]
            data = data.encode() if data is not None else None
            if state.read(name) != data:
                state.write(name, data)
            pub._checkpoint("R1-text", name)
        for name in sorted(state.j["additions"], reverse=True):
            state.target(name)
            if state.read(name) is not None:
                state.target(name)
                path = io.safe(root, name)
                path.unlink()
                pub.sync_directory(path.parent)
                state.written(name, None)
            pub._checkpoint("R1-addition", name)
        if state.read(tx.RUNTIME) != runtime.encode():
            state.write(tx.RUNTIME, runtime.encode())
        pub._checkpoint("R1-runtime")
    diagnostic.begin_segment("R2")
    check_checkout(root, **({"pending_journal": raw} if staged is None else {}))
    require(state.expected == {**hashes(state.j["old"]), **dict.fromkeys(state.j["additions"])},
            "Recovery goal differs")
    if staged is None:
        state.cleanup()
    pub._checkpoint("R2")
    state.full("GR2", no_temps=True)
    io.safe(root, staged or tx.LOCK).unlink()
    pub.sync_directory(root / "content")
    diagnostic.durable("rolled-back")
    return {"status": "rolled-back", "registered": False}
