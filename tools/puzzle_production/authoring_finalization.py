"""HP-I1a outer authoring publication; sealed inputs and catalog stay unchanged."""
from __future__ import annotations

from copy import deepcopy
from io import BytesIO
import os
from pathlib import Path, PurePosixPath
import re
import time
import zipfile

from . import authoring_builder as builder, authoring_package as ap
from . import background_contract as background, background_package, catalog_io as io
from .authoring_build_contract import EXTERNAL, names
from .authoring_staging import OwnedStage, StageError
from .contract import Aborted, InvalidInput, canonical_bytes, digest, exact_keys, integer
from . import authoring_workflow as workflow

REQUEST = "picross-authoring-finalize-request-v1"
OPERATION = "picross-authoring-finalization-v1"
RESULT = "picross-authoring-finalize-result-v1"
RESERVED = {"operation.json", "record.before.json", "record.after.json"}
RECORD_KEYS = set("format puzzle_id revision state category_id build_request_sha256 repo_commit "
                  "document_revision rulebook package handoff inventory_sha256 final_editorial_approval "
                  "width height mode used_colors difficulty verification blockers next_action next_step "
                  "integration source_commit pr reveal motif reveal_options parameters background".split())
INTEGRATION = "integration: background integration requires HP-I1b/HP-I2"


class Conflict(InvalidInput):
    """A declared expectation or an already observed file changed."""


def checkpoint(name):
    """Publication boundaries for small real-I/O interruption/race tests."""
    io.tick()


def _ref(name, raw):
    return {"file": name, "sha256": io.checksum(raw), "bytes": len(raw)}


def _same(left, right):
    """Bound JSON identities preserve types: true, 1 and 1.0 are different."""
    return canonical_bytes(left) == canonical_bytes(right)


def _binding(value, *, limit=ap.MAX_FILE):
    try:
        background._ref(value)
    except background.BackgroundError as exc:
        raise InvalidInput(str(exc)) from exc
    ap.require(value["bytes"] <= limit, "Declared finalization input exceeds byte limit")
    return value


def _authorizations(value, directory):
    exact_keys(value, EXTERNAL)
    for item in value.values():
        if item is not None:
            _binding(item)
            ap.require(item["file"].startswith(directory + "/"),
                       "Authorization must belong to the same authoring revision")
    ap.require((value["manual-authorization.json"] is None) == (value["owner-override.json"] is None),
               "Manual authorization and owner evidence must be supplied together")
    ap.require(value["palette-exception.json"] is None or value["approval.json"] is not None,
               "Palette exception requires a bound final approval")
    names([item["file"] for item in value.values() if item is not None])
    return value


def _request(value):
    r = io.json_bytes(canonical_bytes(value), 8 * 1024 * 1024)
    exact_keys(r, {"format", "record", "sidecar_root", "background", "authorizations", "files"})
    ap.require(r["format"] in (REQUEST, 'picross-authoring-finalize-request-v2'), "Unsupported authoring finalization request")
    _binding(r["record"])
    parts = r["record"]["file"].split("/")
    repository = parts[:2] == ["content", "authoring"]
    identity = parts[2:] if repository else parts
    ap.require(len(identity) == 3 and identity[-1] == "record.json" and
               ap.ID.fullmatch(identity[0]) and ap.REVISION.fullmatch(identity[1]),
               "Finalization requires the canonical existing authoring record")
    directory = r["record"]["file"].rsplit("/", 1)[0]
    ap.relative(r["sidecar_root"])
    ap.require(r["sidecar_root"].startswith(directory + "/") and
               ".git" not in r["sidecar_root"].casefold().split("/"),
               "Sidecar must be a new folder inside this authoring revision")
    r["background"] = background_package.validate_binding(r["background"], package_only=False)
    derivation = r["background"]["derivation"]
    if derivation is not None and derivation["storage"] == "external":
        location = background_package._join(derivation["root"], derivation["ref"]["file"])
        ap.require(str(PurePosixPath(location).parent) != r["sidecar_root"],
                   "HP-W2 derivation requires its own subdirectory inside the sidecar")
    _authorizations(r["authorizations"], directory)
    ap.require(isinstance(r["files"], list) and len(r["files"]) <= ap.MAX_FILES - 3,
               "Finalization requires an explicit bounded file list")
    for item in r["files"]:
        _binding(item)
        ap.require(item["file"].startswith(r["sidecar_root"] + "/"),
                   "Every new file must be inside the declared sidecar")
        local = item["file"][len(r["sidecar_root"]) + 1:]
        ap.require(local not in RESERVED, "Reserved finalization operation filename")
    names([item["file"] for item in r["files"]] +
          [r["sidecar_root"] + "/" + name for name in RESERVED])
    ap.require(sum(item["bytes"] for item in r["files"]) <= ap.MAX_TOTAL,
               "Finalization payload exceeds total byte limit")
    return r, directory, repository


class _Reads:
    """Capture and recheck exact physical inputs; never scan an authoring tree."""

    def __init__(self, **roots):
        self.roots = roots
        self.identities = {key: io.signature(root.lstat())[:2] for key, root in roots.items()}
        self.observed = {}

    def read(self, key, name, limit=ap.MAX_FILE, *, missing=False, ref=None):
        root = self.roots[key]
        if io.signature(io.external(root).lstat())[:2] != self.identities[key]:
            raise Conflict("Finalization source root changed")
        path = io.safe(root, name)
        before = path.lstat() if path.exists() else None
        raw = io.read(root, name, limit, missing=missing)
        after = io.safe(root, name).lstat() if raw is not None else None
        observation = None if after is None else (io.signature(after), after.st_ctime_ns, io.checksum(raw))
        if before is not None and (after is None or io.signature(before) != io.signature(after) or
                                   before.st_ctime_ns != after.st_ctime_ns):
            raise Conflict("Finalization input changed while reading: " + name)
        item = (key, name)
        if item in self.observed and self.observed[item][0] != observation:
            raise Conflict("Previously checked finalization input changed: " + name)
        if ref is not None:
            ap.require(raw is not None and len(raw) == ref["bytes"] and io.checksum(raw) == ref["sha256"],
                       "Finalization source size/hash mismatch: " + name)
        self.observed[item] = observation, limit, missing
        return raw

    def recheck(self):
        for (key, name), (_, limit, missing) in tuple(self.observed.items()):
            self.read(key, name, limit, missing=missing)


def _record(raw, directory):
    value = io.json_bytes(raw, ap.MAX_FILE)
    current = value.get('format') == workflow.RECORD
    exact_keys(value, RECORD_KEYS | ({'raster_selection', 'presentation', 'candidate'} if current else set()))
    puzzle_id, revision = directory.split("/")[-2:]
    ap.require(value["format"] in ("picross-authoring-record-v2", workflow.RECORD) and
               value["puzzle_id"] == puzzle_id and value["revision"] == revision,
               "Record identity/generation differs from the declared authoring revision")
    ap.require(value["state"] in (("background_review", "content_ready", "editorially_approved") if current else ("raster_ready", "content_ready", "editorially_approved")) and
               value["integration"] is None, "Finalization requires unintegrated raster-ready authoring")
    ap.sha(value["build_request_sha256"])
    ap.sha(value["inventory_sha256"])
    ap.require(isinstance(value["repo_commit"], str) and re.fullmatch(r"[0-9a-f]{40}", value["repo_commit"]),
               "Invalid record source commit")
    integer(value["document_revision"], 1, 1_000_000, "record document revision")
    rulebook = exact_keys(value["rulebook"], {"version", "file", "sha256"})
    ap.require(rulebook["version"] == ('0.8.0' if current else "0.7.0"), "Finalization requires the matching background rulebook generation")
    ap.relative(rulebook["file"])
    ap.sha(rulebook["sha256"])
    ap.require(value["category_id"] is None or isinstance(value["category_id"], str) and
               re.fullmatch(r"[a-z][a-z0-9-]{0,63}", value["category_id"]), "Invalid record category")
    _binding(value["package"], limit=ap.MAX_ZIP)
    ap.require(value["package"]["file"] == directory + "/package.zip", "Noncanonical original package path")
    exact_keys(value["handoff"], {"file", "sha256"})
    ap.sha(value["handoff"]["sha256"])
    ap.require(value["handoff"]["file"] == directory + "/handoff.json", "Noncanonical outer handoff path")
    if value["final_editorial_approval"] is not None:
        exact_keys(value["final_editorial_approval"], {"file", "sha256"})
        ap.relative(value["final_editorial_approval"]["file"])
        ap.sha(value["final_editorial_approval"]["sha256"])
    ap.require(isinstance(value["verification"], dict) and isinstance(value["blockers"], list),
               "Invalid record verification/blockers")
    ap.require(isinstance(value["reveal_options"], list) and not value["reveal_options"],
               "Selected reveal requires an empty record options list")
    for key in ("source_commit", "pr"):
        if value[key] is not None:
            ap.string(value[key], "record " + key)
    for text in [*value["blockers"], value["next_action"], value["next_step"]]:
        ap.string(text, "record text")
    background_package.validate_binding(value["background"], package_only=False)
    return value


def _old_authorizations(record, directory, reads):
    if "authorizations" in record["verification"]:
        value = _authorizations(deepcopy(record["verification"]["authorizations"]), directory)
    else:
        value = {}
        for name in sorted(EXTERNAL):
            path = directory + "/" + name
            raw = reads.read("output", path, missing=True)
            value[name] = _ref(path, raw) if raw is not None else None
        _authorizations(value, directory)
    approval = value["approval.json"]
    ap.require(record["final_editorial_approval"] ==
               ({k: approval[k] for k in ("file", "sha256")} if approval is not None else None),
               "Record final approval localization is inconsistent")
    return value


def _copy(stage, root, name, raw):
    destination = io.safe(root, name)
    stage.write(destination.relative_to(stage.root).as_posix(), raw)


def _auth_files(refs, reads, *, new_files=None):
    result = {}
    for item in refs.values():
        if item is None:
            continue
        if new_files is not None and item["file"] in new_files:
            raw = new_files[item["file"]]
            ap.require(_ref(item["file"], raw) == item, "Authorization differs from supplied payload")
        else:
            raw = reads.read("output", item["file"], ref=item)
        result[item["file"]] = raw
    manual, owner = refs["manual-authorization.json"], refs["owner-override.json"]
    if manual is not None:
        value = io.json_bytes(result[manual["file"]], ap.MAX_FILE)
        linked = exact_keys(value.get("owner_override"), {"file", "sha256"})
        ap.relative(linked["file"])
        location = str(PurePosixPath(manual["file"]).parent / linked["file"])
        ap.require(location == owner["file"] and linked["sha256"] == owner["sha256"],
                   "Explicit owner authorization differs from the manual authorization")
    return result


def _inspect(package_path, record, external, authorizations, binding, history_repo, deadline):
    from .target_adapter import inspect
    paths = {name: io.safe(external, ref["file"]) if ref is not None else None
             for name, ref in authorizations.items()}
    with ap.open_package(package_path, allow_background=True,
                         allow_manual_review=paths["manual-authorization.json"] is not None,
                         external_root=external, history_repo=history_repo) as package:
        package.deadline = min(package.deadline, deadline)
        h = package.handoff
        ap.require(package.derivation is None and package.archive_sha256 == record["package"]["sha256"],
                   "Finalization requires the actual unchanged original ZIP")
        ap.require(all(_same(record[key], h[key]) for key in ("puzzle_id", "revision", "repo_commit", "rulebook")) and
                   record["inventory_sha256"] == h["inventory"]["sha256"] and
                   record["handoff"]["sha256"] == ap.file_hash(package.file("handoff.json")),
                   "Record and original package identities differ")
        snapshot = package.bound(h["rulebook"]).read_text(encoding="utf-8")
        ap.require(re.search(r"^\*\*Version " + re.escape(record['rulebook']['version']) + r" · Dokumentrevision " + str(record["document_revision"]) + r" ·",
                             snapshot, re.M), "Record rulebook revision differs from original snapshot")
        ap.require(_same(record["reveal"], h.get("reveal")) and _same(record["motif"], h.get("motif")) and
                   not record["reveal_options"] and _same(record["parameters"],
                   h.get("approved_parameters") or h.get("proposed_parameters") or None),
                   "Record changes sealed images, selection or parameters")
        if workflow.is_current(h):
            ap.require(record['raster_selection'] == h['raster_selection'] and record['candidate'] == h['candidate'],
                       'Record changes sealed raster selection')
        report, design, matrix, _, _ = inspect(package, paths["approval.json"],
            manual_authorization=paths["manual-authorization.json"],
            palette_exception=paths["palette-exception.json"], allow_background=True,
            background_binding=binding)
        ap.require(report["technical"] and all(
            item == "final_editorial: missing bound human final approval" or item.startswith("background")
            for item in report["blockers"]), "Finalization has unresolved raster/content errors")
        current = package.effective_background
        verification = {"format": report["format"], "technical": True,
                        "editorial_approved": report["editorial_approved"], "blockers": report["blockers"],
                        "width": design["width"], "height": design["height"], "mode": design["mode"],
                        "used_colors": len({cell for row in matrix for cell in row if cell != "empty"}),
                        "difficulty": report["difficulty"], "original_state": h["state"],
                        "effective_state": report["effective_state"], "integration_ready": False,
                        "background_ready": current["ready"]}
        return verification, current


def _proposed(before, verification, current, authorizations):
    after = deepcopy(before)
    for key in ("width", "height", "mode", "used_colors", "difficulty"):
        after[key] = verification[key]
    after.update(state=verification["effective_state"], background=current["binding"],
                 verification={**verification, "authorizations": deepcopy(authorizations)},
                 source_commit=None, pr=None, integration=None)
    approval = authorizations["approval.json"]
    after["final_editorial_approval"] = {k: approval[k] for k in ("file", "sha256")} if approval else None
    after["blockers"] = list(dict.fromkeys([*verification["blockers"], *current["blockers"],
                                           *([] if before['format'] == workflow.RECORD else [INTEGRATION]), builder.UNSAVED]))
    after["next_step"] = {"raster_ready": "4 · Hintergrundbereitschaft klären und Rätsel abnehmen",
        "content_ready": "4 · Rätsel abnehmen; finale Hintergrundintegration benötigt HP-I1b/HP-I2",
        "editorially_approved": "Finale Integration nach verfügbarer HP-I1b/HP-I2-Unterstützung",
        "background_review": workflow.NEXT['background_review']}[after["state"]]
    if before['format'] == workflow.RECORD:
        after['next_step'] = workflow.NEXT[after['state']]
    after["next_action"] = after["next_step"]
    return after


def _operation(root, r, directory):
    """Read only an exactly identified complete own publication, never adopt leftovers."""
    try:
        files = ap.file_table(root, time.monotonic() + ap.SECONDS)
        local = [{**item, "file": item["file"][len(r["sidecar_root"]) + 1:]} for item in r["files"]]
        ap.require(set(files) == RESERVED | {item["file"] for item in local},
                   "Sidecar has missing or foreign files")
        parents = {str(parent) for name in files for parent in PurePosixPath(name).parents
                   if str(parent) != "."}
        actual_parents = {str((Path(parent) / name).relative_to(root).as_posix())
                          for parent, dirs, _ in os.walk(root) for name in dirs}
        ap.require(actual_parents == parents, "Sidecar has foreign directories")
        raw = io.read(root, "operation.json", ap.MAX_FILE)
        op = io.json_bytes(raw, ap.MAX_FILE)
        exact_keys(op, {"format", "request_sha256", "record", "before", "after", "files"})
        ap.require(op["format"] == ('picross-authoring-finalization-v2' if r['format'].endswith('-v2') else OPERATION) and op["request_sha256"] == digest(r) and
                   op["record"] == r["record"]["file"] and op["files"] == local,
                   "Sidecar belongs to another finalization")
        records = []
        for name in ("before", "after"):
            item = _binding(op[name])
            ap.require(item["file"] == "record." + name + ".json", "Invalid operation record path")
            record_raw = io.read(root, item["file"], ap.MAX_FILE)
            ap.require(_ref(item["file"], record_raw) == item, "Operation record bytes changed")
            _record(record_raw, directory)
            records.append(record_raw)
        ap.require(_ref(r["record"]["file"], records[0]) == r["record"],
                   "Operation does not bind the expected prior record")
        for item in local:
            ap.require(_ref(item["file"], io.read(root, item["file"], ap.MAX_FILE)) == item,
                       "Published sidecar payload changed")
        return records[0], records[1], raw
    except (InvalidInput, ValueError, OSError) as exc:
        raise Conflict("Conflicting finalization sidecar: " + str(exc)) from exc


def _record_guard(root, r, expected):
    if io.read(root, r["record"]["file"], ap.MAX_FILE) != expected:
        raise Conflict("Expected authoring record changed")


def _operation_guard(root, r, directory, expected):
    if _operation(root, r, directory) != expected:
        raise Conflict("Written finalization operation differs from freshly checked bytes")


def _parents(root, target, made):
    path = target.parent
    pending = []
    while path != root and not path.exists():
        pending.append(path)
        path = path.parent
    for path in reversed(pending):
        io.safe(root, path.relative_to(root).as_posix()).mkdir()
        made.append(path)


def error_result(exc, remaining=None):
    status = (exc.status if isinstance(exc, StageError) else
              "conflict" if isinstance(exc, Conflict) else
              "aborted" if isinstance(exc, (Aborted, KeyboardInterrupt, MemoryError)) else
              "invalid_input" if isinstance(exc, (InvalidInput, ValueError, TypeError, KeyError, RecursionError)) else
              "technical_error")
    return {"format": RESULT, "status": status, "message": str(exc) or "Finalization interrupted",
            "remaining": getattr(exc, "remaining", None) or remaining, "next_action":
            "Inspect the current record and retained sidecar or private stage; retry the identical request after resolving the cause."}


def finalize_background(request, source_root, output_root, *, history_repo=None):
    """Return one closed result. Publication is sidecar-first and record-last."""
    remaining, made = None, []
    try:
        with io.budget(ap.SECONDS):
            deadline = time.monotonic() + ap.SECONDS
            r, directory, repository = _request(request)
            source, output = io.external(source_root), io.external(output_root)
            ap.require(source.is_dir() and output.is_dir(), "Explicit source/output roots must exist")
            ap.require(not source.is_relative_to(output) and not output.is_relative_to(source),
                       "Finalization source/output roots overlap")
            revision = io.safe(output, directory)
            ap.require(revision.is_dir(), "Existing authoring revision is missing")
            gitdir = builder.git_root(output) if repository else None
            lock = gitdir / "authoring-builder.lock" if repository else output / ".authoring-builder.lock"
            try:
                with builder.writer(lock):
                    reads = _Reads(source=source, output=output)
                    if repository:
                        index = builder.index_value(reads.read("output", builder.INDEX, 8 * 1024 * 1024))
                        row = {"puzzle_id": directory.split("/")[-2], "revision": directory.split("/")[-1],
                               "record": r["record"]["file"]}
                        ap.require(row in index["entries"], "Record is not the indexed authoring revision")
                    target = io.safe(output, r["sidecar_root"])
                    observed_record = io.read(output, r["record"]["file"], ap.MAX_FILE)
                    resumed = target.exists()
                    if resumed:
                        before_raw, saved_after, saved_operation = _operation(target, r, directory)
                        if observed_record not in (before_raw, saved_after):
                            raise Conflict("Record does not match either side of this complete finalization")
                        remaining = str(target)
                    else:
                        if _ref(r["record"]["file"], observed_record) != r["record"]:
                            raise Conflict("Stale expected authoring record")
                        before_raw, saved_after, saved_operation = observed_record, None, None
                    before = _record(before_raw, directory)
                    current_generation = before['format'] == workflow.RECORD
                    ap.require(current_generation == (r['format'] == 'picross-authoring-finalize-request-v2'),
                               'Finalizer and record generations differ')
                    original = reads.read("output", before["package"]["file"], ap.MAX_ZIP, ref=before["package"])
                    handoff = reads.read("output", before["handoff"]["file"])
                    ap.require(io.checksum(handoff) == before["handoff"]["sha256"], "Outer handoff hash mismatch")
                    with ap.open_files(output / before["package"]["file"], deadline=deadline) as (opened, _, _):
                        ap.require(io.read(opened, "handoff.json", ap.MAX_FILE) == handoff,
                                   "Outer handoff is not the byte-identical original copy")
                    old_auth = _old_authorizations(before, directory, reads)
                    old_auth_files = _auth_files(old_auth, reads)
                    old_verification, old_background = _inspect(output / before["package"]["file"], before,
                        output, old_auth, before["background"], history_repo, deadline)
                    ap.require(before["state"] == old_verification["effective_state"] and all(
                        _same(before[key], old_verification[key]) for key in ("width", "height", "mode", "used_colors", "difficulty")),
                        "Record status or raster facts differ from fresh original inspection")
                    ap.require(_same(before["background"]["manifest"]["ref"], r["background"]["manifest"]["ref"]),
                               "Finalization changes the sealed background manifest")
                    previous_decision = before["background"]["decision"]
                    next_decision = r["background"]["decision"]
                    if before["background"]["derivation"] is not None:
                        ap.require(next_decision is not None and
                                   (previous_decision["ref"] != next_decision["ref"] or
                                    r["background"]["derivation"] is not None),
                                   "Cannot silently remove a bound background derivation")
                    for name, ref in old_auth.items():
                        ap.require(ref is None or r["authorizations"][name] is not None,
                                   "Cannot silently remove a bound authorization: " + name)
                    prior_files = {name: reads.read("output", name) for name in old_background["external_files"]}
                    prior_files.update(old_auth_files)
                    payload = {}
                    for item in r["files"]:
                        raw = reads.read("source", item["file"], ref=item)
                        ap.require(not zipfile.is_zipfile(BytesIO(raw)) and not item["file"].casefold().endswith(".zip"),
                                   "Embedded archives are not finalization sidecars")
                        ap.require(item["file"] not in prior_files, "New sidecar overwrites an existing external reference")
                        payload[item["file"]] = raw
                    auth_files = _auth_files(r["authorizations"], reads, new_files=payload)
                    overlay = {**prior_files, **auth_files, **payload}
                    names(overlay)
                    ap.require(sum(map(len, overlay.values())) + len(original) <= ap.MAX_TOTAL,
                               "Finalization inputs exceed total byte limit")
                    checkpoint("inputs-read")
                    stage_parent = None if resumed and observed_record == saved_after else revision.parent
                    with OwnedStage(stage_parent, ".hp-i1a-finalize-", {
                            "purpose": "HP-I1a unpublished finalization stage", "target": str(target),
                            "request_sha256": digest(r)}) as stage:
                        work = stage.root
                        external, sidecar = stage.mkdir("external"), stage.mkdir("sidecar")
                        for name, raw in overlay.items():
                            _copy(stage, external, name, raw)
                        verification, current = _inspect(output / before["package"]["file"], before,
                            external, r["authorizations"], r["background"], history_repo, deadline)
                        previous = before["background"]["decision"]
                        if previous is not None:
                            key = tuple(previous["ref"][name] for name in ("file", "sha256", "bytes"))
                            ap.require(key in current["decision_refs"],
                                       "New background decision does not explicitly supersede the current record")
                        used = current["external_files"] | {item["file"] for item in r["authorizations"].values() if item}
                        ap.require(set(payload) <= used, "Unbound finalization payload file")
                        after = _proposed(before, verification, current, r["authorizations"])
                        after_raw = builder.json_data(after)
                        local = [{**item, "file": item["file"][len(r["sidecar_root"]) + 1:]} for item in r["files"]]
                        operation = {"format": 'picross-authoring-finalization-v2' if current_generation else OPERATION, "request_sha256": digest(r), "record": r["record"]["file"],
                            "before": _ref("record.before.json", before_raw),
                            "after": _ref("record.after.json", after_raw), "files": local}
                        operation_raw = builder.json_data(operation)
                        for item, local_ref in zip(r["files"], local):
                            _copy(stage, sidecar, local_ref["file"], payload[item["file"]])
                        for name, raw in (("record.before.json", before_raw), ("record.after.json", after_raw),
                                          ("operation.json", operation_raw)):
                            stage.write("sidecar/" + name, raw)
                        expected_operation = before_raw, after_raw, operation_raw
                        projections = None
                        if current_generation:
                            from tools.production_workspace.projector import automatic
                            projection_stage = stage.mkdir('projection')
                            stage.write('projection/package.zip', original)
                            stage.write('projection/handoff.json', handoff)
                            stage.write('projection/record.json', before_raw)
                            prior_projection = automatic(output, directory, projection_stage, index)
                            next_projection = automatic(output, directory, projection_stage, index,
                                overlay={**overlay, directory + '/record.json': after_raw})
                            projection_name = directory + '/workspace.json'
                            projections = prior_projection, next_projection
                            ap.require(io.read(output, projection_name, 1024 * 1024) in projections,
                                       'Projection changed outside this finalization')
                        _operation_guard(sidecar, r, directory, expected_operation)
                        if resumed and (saved_after != after_raw or saved_operation != operation_raw):
                            raise Conflict("Published finalization differs from freshly checked request")
                        checkpoint("before-sidecar-publication")
                        reads.recheck()
                        _record_guard(output, r, observed_record)
                        if not resumed:
                            _parents(output, target, made)
                            try:
                                builder.publish_directory(sidecar, io.safe(output, r["sidecar_root"]))
                            except FileExistsError as exc:
                                raise Conflict("Sidecar target appeared during publication") from exc
                            remaining = str(target)
                        _operation_guard(target, r, directory, expected_operation)
                        checkpoint("sidecar-published")
                        reads.recheck()
                        _record_guard(output, r, observed_record)
                        if observed_record != after_raw:
                            replacement = stage.write("record.next.json", after_raw)
                            checkpoint("before-record-replace")
                            reads.recheck()
                            _operation_guard(target, r, directory, expected_operation)
                            _record_guard(output, r, before_raw)
                            os.replace(replacement, io.safe(output, r["record"]["file"]))
                        checkpoint("record-committed")
                        reads.recheck()
                        _record_guard(output, r, after_raw)
                        _operation_guard(target, r, directory, expected_operation)
                        if projections is not None:
                            actual = io.read(output, projection_name, 1024 * 1024)
                            ap.require(actual in projections, 'Projection changed during finalization')
                            if actual != projections[1]:
                                replacement = stage.write('workspace.next.json', projections[1])
                                os.replace(replacement, io.safe(output, projection_name))
                            ap.require(io.read(output, projection_name, 1024 * 1024) == projections[1], 'Projection publication failed')
                        return {"format": 'picross-authoring-finalize-result-v2' if current_generation else RESULT, "status": "reused" if observed_record == after_raw else "updated",
                                "record": after, "sheet": builder.sheet_from_record(after, current),
                                "operation": _ref(r["sidecar_root"] + "/operation.json", operation_raw)}
            except builder.BuildError as exc:
                raise Conflict(str(exc)) from exc
    except (Exception, KeyboardInterrupt) as exc:
        result = error_result(exc, remaining)
        if isinstance(request, dict) and request.get('format') == 'picross-authoring-finalize-request-v2':
            result['format'] = 'picross-authoring-finalize-result-v2'
        return result
    finally:
        for path in reversed(made):
            try:
                path.rmdir()
            except OSError:
                pass  # Published or foreign nonempty folders are never removed.
