"""PB-H typed, read-only background transport and phase checks.

Package roots, background working roots and derivation output directories are
explicit. This module does not select pictures, invent approvals, normalize
images, fetch history, or update an existing authoring record.
"""
from __future__ import annotations

from contextlib import ExitStack
import hashlib
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile
import time

from . import authoring_package as ap, background_contract as bc, catalog_io as io
from .contract import Aborted, InvalidInput, exact_keys


def _join(root, name):
    ap.relative(name)
    return name if root == "." else ap.relative(root + "/" + name)


def _root(value):
    ap.require(type(value) is str, "Background root must be a string")
    if value != ".":
        ap.relative(value)


def _stored(value, package_only):
    exact_keys(value, {"storage", "root", "ref"})
    ap.require(value["storage"] in (("package",) if package_only else ("package", "external")),
               "Handoff background references must use package storage" if package_only else "Invalid background storage")
    _root(value["root"])
    bc._ref(value["ref"])
    _join(value["root"], value["ref"]["file"])


def validate_binding(value, *, package_only=True):
    """Validate the closed BackgroundBinding form without reading any files."""
    try:
        value = bc.parse_json(bc.canonical(value))
        exact_keys(value, {"manifest", "decision", "derivation", "history"})
        _stored(value["manifest"], package_only)
        for key in ("decision", "derivation"):
            if value[key] is not None:
                _stored(value[key], package_only)
        ap.require(value["derivation"] is None or value["decision"] is not None,
                   "Background derivation requires an explicit decision")
        if value["history"] is not None:
            history = exact_keys(value["history"], {"commit", "storage", "path", "root"})
            ap.require(type(history["commit"]) is str and re.fullmatch(r"[0-9a-f]{40}", history["commit"]),
                       "Background history requires an exact commit")
            ap.require(history["storage"] in ("directory", "package"), "Invalid history storage")
            ap.relative(history["path"])
            _root(history["root"])
        return value
    except bc.BackgroundError as exc:
        raise InvalidInput("Background binding: " + str(exc)) from exc


class _Reads:
    """Fresh bounded physical reads plus a collision-checked HP-W2 source map."""

    def __init__(self, root, external, deadline):
        self.roots = {"package": io.external(root)}
        if external is not None:
            self.roots["external"] = io.external(external)
        for path in self.roots.values():
            ap.require(path.is_dir(), "Explicit background root is not a directory")
        self.root_ids = {key: io.signature(path.lstat())[:2] for key, path in self.roots.items()}
        self.deadline = deadline
        self.seen, self.assembly, self.edges = {}, {}, {}
        self.files, self.derivative_files = set(), set()
        self.total = 0

    def tick(self):
        io.tick()
        if time.monotonic() >= self.deadline:
            raise Aborted("Background package time budget exhausted")

    def location(self, stored):
        return stored["storage"], stored["root"]

    def read(self, location, ref, *, limit=bc.MAX_PNG, owner=None, assemble=True, missing=False):
        self.tick()
        bc._ref(ref)
        storage, prefix = location
        ap.require(storage in self.roots, "External background reference requires an explicit external_root")
        root, name = self.roots[storage], _join(prefix, ref["file"])
        ap.require(io.signature(io.external(root).lstat())[:2] == self.root_ids[storage],
                   "Background source root changed")
        ap.require(ref["bytes"] <= limit, "Declared background file exceeds byte limit")
        path = io.safe(root, name)
        if not path.exists():
            ap.require(missing, "Missing active background file: " + name)
            return None
        before = path.lstat()
        key = (storage, name)
        previous = self.seen.get(key)
        if previous is not None:
            ap.require((io.signature(before), before.st_ctime_ns) == previous[:2],
                       "Previously checked background source changed: " + name)
        raw = io.read(root, name, limit)
        after = io.safe(root, name).lstat()
        ap.require(io.signature(before) == io.signature(after) and before.st_ctime_ns == after.st_ctime_ns,
                   "Background source changed during reading: " + name)
        ap.require(len(raw) == ref["bytes"] and hashlib.sha256(raw).hexdigest() == ref["sha256"],
                   "Background file size/hash mismatch: " + name)
        ap.require(not name.casefold().endswith(".zip") and raw[:4] not in (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"),
                   "Embedded archives are not background files")
        observation = (io.signature(after), after.st_ctime_ns, ref["sha256"], len(raw), limit)
        ap.require(previous is None or previous[:4] == observation[:4], "Background file changed: " + name)
        if previous is None:
            self.total += len(raw)
            ap.require(len(self.seen) < ap.MAX_FILES and self.total <= ap.MAX_TOTAL,
                       "Background package reference limit exceeded")
            self.seen[key] = observation
        if storage == "package":
            self.files.add(name)
        if assemble:
            logical = ref["file"]
            ap.require(logical not in self.assembly or self.assembly[logical] == raw,
                       "Conflicting background source path: " + logical)
            self.assembly[logical] = raw
            if owner is not None:
                ap.require(owner != logical, "Self-referencing background evidence")
                self.edges.setdefault(owner, set()).add(logical)
        return raw

    def json(self, location, ref, **kwargs):
        return bc.parse_json(self.read(location, ref, limit=bc.MAX_JSON, **kwargs), ref["file"])

    def recheck(self):
        for (storage, name), (_, _, sha, size, limit) in tuple(self.seen.items()):
            self.read((storage, "."), {"file": name, "sha256": sha, "bytes": size}, limit=limit, assemble=False)
        self.tick()

    def acyclic(self):
        done, visiting = set(), set()

        def visit(name):
            self.tick()
            ap.require(name not in visiting, "Cyclic background reference graph")
            if name in done:
                return
            visiting.add(name)
            for child in self.edges.get(name, ()):
                visit(child)
            visiting.remove(name)
            done.add(name)

        for name in self.edges:
            visit(name)


class _History:
    """Only explicitly supplied local immutable Git objects; never fetch/checkout."""

    def __init__(self, value, repository, reads, stack, manifest_ref):
        ap.require(repository is not None, "Omitting discarded backgrounds requires explicit history_repo")
        self.repository = io.external(repository)
        ap.require(self.repository.is_dir(), "History repository is not a directory")
        self.value, self.reads = value, reads
        self.env = {**os.environ, "GIT_NO_LAZY_FETCH": "1", "GIT_OPTIONAL_LOCKS": "0",
                    "GIT_TERMINAL_PROMPT": "0", "GIT_NO_REPLACE_OBJECTS": "1"}
        actual = self.git("rev-parse", "--show-toplevel", limit=4096).decode("utf-8").strip()
        ap.require(io.external(actual) == self.repository, "history_repo must be the explicit checkout root")
        ap.require(self.git("cat-file", "-t", value["commit"], limit=64).strip() == b"commit",
                   "History commit is not locally available")
        self.local = None
        if value["storage"] == "package":
            raw = self.blob(value["path"], ap.MAX_ZIP)
            directory = Path(stack.enter_context(tempfile.TemporaryDirectory(prefix="pb-h-history-")))
            archive = directory / "original.zip"
            archive.write_bytes(raw)
            package_root, _, _ = stack.enter_context(ap.open_files(archive, deadline=reads.deadline))
            self.local = package_root
        original = self.read(manifest_ref)
        current = reads.assembly[manifest_ref["file"]]
        ap.require(original == current, "History does not contain the identical presented manifest")

    def git(self, *arguments, limit):
        self.reads.tick()
        timeout = min(15, max(0.001, self.reads.deadline - time.monotonic()))
        try:
            process = subprocess.run(["git", "-C", str(self.repository), *arguments],
                                     env=self.env, capture_output=True, timeout=timeout)
        except (OSError, subprocess.SubprocessError) as exc:
            raise InvalidInput("Cannot read the explicit local background history") from exc
        ap.require(process.returncode == 0 and len(process.stdout) <= limit,
                   "Missing, invalid or oversized local background history")
        return process.stdout

    def blob(self, path, limit):
        ap.relative(path)
        # Check every tree segment, including aliases and symlink/submodule modes.
        tree = self.value["commit"]
        parts = path.split("/")
        row = None
        for index, part in enumerate(parts):
            listing = self.git("ls-tree", "-z", tree, limit=2 * 1024 * 1024)
            matches = []
            for record in listing.split(b"\0"):
                if not record:
                    continue
                header, name = record.split(b"\t", 1)
                decoded = name.decode("utf-8", errors="strict")
                if decoded.casefold() == part.casefold():
                    matches.append((decoded, header.decode("ascii").split()))
            ap.require(len(matches) == 1 and matches[0][0] == part,
                       "Missing or case-colliding background history path")
            row = matches[0][1]
            if index < len(parts) - 1:
                ap.require(row[0] == "040000" and row[1] == "tree", "Unsafe background history parent")
                tree = row[2]
        ap.require(row is not None and row[0] in ("100644", "100755") and row[1] == "blob",
                   "Background history requires a regular file")
        size = self.git("cat-file", "-s", row[2], limit=64).strip()
        ap.require(size.isdigit() and int(size) <= limit, "Background history blob exceeds byte limit")
        raw = self.git("cat-file", "blob", row[2], limit=limit)
        ap.require(len(raw) == int(size), "Background history blob size mismatch")
        return raw

    def read(self, ref):
        self.reads.tick()
        name = _join(self.value["root"], ref["file"])
        if self.local is None:
            raw = self.blob(_join(self.value["path"], name), min(ap.MAX_FILE, ref["bytes"]))
        else:
            raw = io.read(self.local, name, min(ap.MAX_FILE, ref["bytes"]))
        ap.require(len(raw) == ref["bytes"] and hashlib.sha256(raw).hexdigest() == ref["sha256"],
                   "Discarded background history binding mismatch")
        ap.require(not name.casefold().endswith(".zip") and raw[:4] not in (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"),
                   "Embedded archive in background history")
        return raw


def _candidate_refs(candidate):
    yield candidate["original"]
    if candidate["generation"]["prompt"] is not None:
        yield candidate["generation"]["prompt"]
    yield from candidate["provenance"]["evidence"]
    if candidate["review"] is not None:
        for judgment in candidate["review"].values():
            yield from judgment["evidence"]


def _readiness(manifest, decision, candidate, derivation):
    if decision is None or decision["outcome"] == "rejected":
        return False, ["background_choice: human selection or explicit none pending"]
    blockers = []
    if derivation is None:
        blockers.append("background_asset: fresh bound derivation missing")
    if candidate is not None:
        if candidate["provenance"]["rights_status"] != "resolved":
            blockers.append("background_asset: usage rights unresolved")
        review = candidate["review"]
        accepted = {item["criterion"] for item in decision["accepted_deviations"]}
        for criterion in ("Q-HG01", "Q-HG02", "Q-HG03", "Q-HG04"):
            result = review[criterion]["result"] if review is not None else "nicht geprüft"
            if result == "erfüllt":
                continue
            if criterion != "Q-HG01" and result in ("Warnung", "nicht erfüllt") and criterion in accepted:
                continue
            blockers.append("background_asset: " + criterion + " " + result)
    return not blockers, blockers


def _validate(root, handoff, binding, *, history_repo, deadline, external_root, external):
    ap.require(type(handoff.get("test_only", False)) is bool, "Invalid package test_only marker")
    binding = validate_binding(binding, package_only=not external)
    deadline = min(deadline, time.monotonic() + ap.SECONDS) if deadline is not None else time.monotonic() + ap.SECONDS
    reads = _Reads(root, external_root, deadline)
    manifest_location = reads.location(binding["manifest"])
    decision_location = reads.location(binding["decision"]) if binding["decision"] else None
    current_ref = binding["manifest"]["ref"]
    manifests, decisions, visiting, revisions = {}, {}, set(), {}

    def identity(table, key, ref):
        value = (ref["sha256"], ref["bytes"])
        ap.require(key not in table or table[key] == value, "Changed bytes reuse a background revision")
        table[key] = value

    def manifest_for(ref):
        key = (ref["file"], ref["sha256"], ref["bytes"])
        if key not in manifests:
            value = bc.validate_manifest(reads.json(manifest_location, ref))
            ap.require(value["puzzle_id"] == handoff["puzzle_id"] and value["test_only"] == handoff.get("test_only", False),
                       "Background and package puzzle/test_only identities differ")
            identity(revisions, ("manifest", value["job_id"], value["revision"]), ref)
            for row in value["candidates"]:
                identity(revisions, ("image", value["job_id"], row["id"], row["revision"]), row["original"])
            manifests[key] = value
        return manifests[key]

    current = manifest_for(current_ref)
    job = (current["puzzle_id"], current["job_id"], current["test_only"])

    def manifest_sources(manifest, ref):
        owner = ref["file"]
        for field in ("reveal", "reveal_approval"):
            value = manifest["context"][field]
            if value is not None:
                reads.read(manifest_location, value, owner=owner)
        for value in (manifest["presentation"]["evidence"],
                      (manifest["candidate_policy"]["exception"] or {}).get("evidence")):
            if value is not None:
                reads.read(manifest_location, value, owner=owner)

    def visit(ref):
        key = (ref["file"], ref["sha256"], ref["bytes"])
        ap.require(key not in visiting, "Cyclic background decision predecessors")
        if key in decisions:
            return decisions[key]
        visiting.add(key)
        value = bc.validate_decision(reads.json(decision_location, ref))
        ap.require(tuple(value[k] for k in ("puzzle_id", "job_id", "test_only")) == job,
                   "Background predecessor belongs to another job")
        identity(revisions, ("decision", value["job_id"], value["revision"]), ref)
        manifest = manifest_for(value["manifest"])
        candidate = bc._bind_decision(manifest, value)
        reads.edges.setdefault(ref["file"], set()).add(value["manifest"]["file"])
        manifest_sources(manifest, value["manifest"])
        reads.read(decision_location, value["evidence"], owner=ref["file"])
        if candidate is not None:
            for item in _candidate_refs(candidate):
                reads.read(manifest_location, item, owner=value["manifest"]["file"])
        prior = {}
        for field in ("previous_decision", "carried_from"):
            if value[field] is not None:
                reads.edges[ref["file"]].add(value[field]["file"])
                prior[field] = visit(value[field])
        if "carried_from" in prior:
            bc._carry(manifest, value, candidate, prior["carried_from"])
        visiting.remove(key)
        decisions[key] = (manifest, value, candidate)
        return decisions[key]

    with ExitStack() as stack:
        manifest_sources(current, current_ref)
        decision, candidate = None, None
        if binding["decision"] is not None:
            _, decision, candidate = visit(binding["decision"]["ref"])
            ap.require(decision["manifest"] == current_ref, "Active background decision refers to another manifest")
            if not external and decision["presented_package"] is not None:
                ap.require(decision["presented_package"]["revision"] != handoff["revision"],
                           "A package cannot contain a decision referring to its own sealed bytes")
        status = decision["outcome"] if decision else current["presentation"]["status"]
        # Offered/pending declarations always retain every present candidate.
        # Only an actual choice/none can refer discarded candidates to history.
        history = None
        can_omit = status in ("selected", "none") and binding["history"] is not None
        for row in current["candidates"]:
            active = candidate is not None and row["id"] == candidate["id"]
            for ref in _candidate_refs(row):
                raw = reads.read(manifest_location, ref, owner=current_ref["file"], missing=can_omit and not active)
                if raw is None:
                    if history is None:
                        history = _History(binding["history"], history_repo, reads, stack, current_ref)
                    history.read(ref)
        selected_reveal = handoff.get("reveal")
        if current["context"]["reveal"] is not None and isinstance(selected_reveal, dict) and selected_reveal.get("file"):
            ap.require(current["context"]["reveal"]["sha256"] == selected_reveal.get("sha256"),
                       "Background context binds another selected reveal")
            approval = selected_reveal.get("approval")
            if approval:
                raw = io.read(reads.roots["package"], approval, ap.MAX_FILE)
                ap.require(hashlib.sha256(raw).hexdigest() == current["context"]["reveal_approval"]["sha256"],
                           "Background context binds another reveal approval")

        if external:
            original_binding = validate_binding(handoff["background"])
            ap.require(original_binding["manifest"]["ref"] == current_ref,
                       "Outer background decision changes the sealed manifest")
            old = original_binding["decision"]
            if old is not None and old["ref"] != (binding["decision"] or {}).get("ref"):
                old_key = tuple(old["ref"][key] for key in ("file", "sha256", "bytes"))
                ap.require(old_key in decisions, "Outer background decision does not explicitly supersede its predecessor")

        # Different physical roots must still describe one portable logical
        # source namespace, even before a derivation is supplied.
        from .authoring_build_contract import names
        names(reads.assembly)
        derivation = None
        if binding["derivation"] is not None:
            ap.require(status in ("selected", "none"), "Unselected/rejected background cannot carry a derivation")
            location = reads.location(binding["derivation"])
            ref = binding["derivation"]["ref"]
            derivation = reads.json(location, ref, assemble=False)
            ap.require(isinstance(derivation, dict) and derivation.get("format") == "picross-background-derivation-v1",
                       "Unsupported background derivation")
            request = bc.validate_request(derivation.get("request"))
            ap.require(request["manifest"] == current_ref and request["decision"] == binding["decision"]["ref"] and
                       request["source"] == decision["original"], "Background derivation uses different selected inputs")
            output_root = str(PurePosixPath(_join(location[1], ref["file"])).parent)
            output_location = (location[0], output_root)
            output = derivation.get("output")
            if status == "selected":
                bc._ref(output)
                ap.require(output["file"] == "background.png", "Background output name must be background.png")
                output_bytes = reads.read(output_location, output, assemble=False)
            else:
                ap.require(output is None, "none must not carry a background texture")
                output_bytes = None
            ap.require(PurePosixPath(ref["file"]).name == "derivation.json", "Background proof must be derivation.json")
            directory = reads.roots[location[0]] if output_root == "." else io.safe(reads.roots[location[0]], output_root)
            expected_names = {"derivation.json", "background.png"} if output is not None else {"derivation.json"}
            ap.require({p.name for p in directory.iterdir()} == expected_names,
                       "Background derivation directory contains missing or foreign entries")
            if location[0] == "package":
                reads.derivative_files.add(_join(location[1], ref["file"]))
            # Temporary roots preserve all inner paths and bytes. Only the two
            # HP-W2 output files enter the separate output directory.
            temporary = Path(stack.enter_context(tempfile.TemporaryDirectory(prefix="pb-h-verify-")))
            source, out = temporary / "source", temporary / "output"
            source.mkdir()
            out.mkdir()
            for name, raw in reads.assembly.items():
                path = source / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)
            report_bytes = reads.read(location, ref, limit=bc.MAX_JSON, assemble=False)
            (out / "derivation.json").write_bytes(report_bytes)
            if output_bytes is not None:
                (out / "background.png").write_bytes(output_bytes)
            from .background_assets import verify
            reads.tick()
            result = verify(request, source, out)
            reads.tick()
            if result["status"] == "aborted":
                raise Aborted("Background derivation verification aborted: " +
                              str((result.get("error") or {}).get("message", "aborted")))
            ap.require(result["status"] == "verified", "Background derivation verification failed: " +
                       str((result.get("error") or {}).get("message", result["status"])))

        reads.acyclic()
        ready, blockers = _readiness(current, decision, candidate, derivation)
        if not external:
            gates, evidence = handoff.get("gates", {}), handoff.get("gate_evidence", {})
            for gate, field, allowed in (("background_choice", "decision", status in ("selected", "none")),
                                         ("background_asset", "derivation", ready)):
                if gates.get(gate) == "pass":
                    ap.require(allowed and binding[field] is not None,
                               "Background pass gate lacks its actual bound result: " + gate)
                    actual = _join(binding[field]["root"], binding[field]["ref"]["file"])
                    ap.require(evidence.get(gate) == actual, "Background gate evidence path mismatch: " + gate)
                else:
                    ap.require(evidence.get(gate) is None, "Non-pass background gate evidence must be null")
            if handoff.get("state") in ("content_ready", "editorially_approved", "catalog_ready", "registered"):
                ap.require(ready and all(gates.get(gate) == "pass" for gate in ("background_choice", "background_asset")),
                           "Content readiness requires complete background readiness")
        reads.recheck()
        options = [{"ID": c["id"], "Beschreibung": c["description"], "Datei": c["original"]["file"],
                    "SHA-256": c["original"]["sha256"], "Bildrevision": c["revision"]}
                   for c in current["candidates"]] if current["presentation"]["status"] == "offered" else []
        return {"status": status, "ready": ready, "blockers": blockers, "binding": binding,
                "manifest": current, "decision": decision, "derivation": derivation,
                "options": options, "files": reads.files, "derivative_files": reads.derivative_files}


def validate(root, handoff, *, history_repo=None, deadline=None, external_root=None):
    """Read an original package binding, preserving its historical status/gates."""
    if handoff.get("format") == "picross-authoring-handoff-v2":
        ap.require("background" not in handoff and handoff.get("rulebook", {}).get("version") in
                   ("0.4.0", "0.4.1", "0.5.0", "0.6.0"), "New background data in an old handoff")
        return {"status": "legacy", "ready": False, "blockers": [], "binding": None,
                "manifest": None, "decision": None, "derivation": None, "options": [],
                "files": set(), "derivative_files": set()}
    ap.require(handoff.get("format") == "picross-authoring-handoff-v3" and
               handoff.get("rulebook", {}).get("version") == "0.7.0", "Unsupported background handoff generation")
    try:
        return _validate(root, handoff, handoff.get("background"), history_repo=history_repo,
                         deadline=deadline, external_root=external_root, external=False)
    except bc.BackgroundError as exc:
        if exc.status == "aborted":
            raise Aborted(str(exc)) from exc
        raise InvalidInput("Background package: " + str(exc)) from exc


def validate_external(root, handoff, binding, *, history_repo=None, deadline=None, external_root=None):
    """Read explicitly provided outer bindings; never change the original handoff."""
    ap.require(handoff.get("format") == "picross-authoring-handoff-v3" and
               handoff.get("rulebook", {}).get("version") == "0.7.0", "Outer background binding requires v3/0.7.0")
    try:
        return _validate(root, handoff, binding, history_repo=history_repo, deadline=deadline,
                         external_root=external_root, external=True)
    except bc.BackgroundError as exc:
        if exc.status == "aborted":
            raise Aborted(str(exc)) from exc
        raise InvalidInput("Outer background binding: " + str(exc)) from exc
