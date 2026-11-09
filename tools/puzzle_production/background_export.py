"""HP-I1a: sealed original transport and independently checked export v6.

This module does not publish a catalog. Its only history fallback is called by
the background reader after a file is proven missing and inactive in that
particular original/outer context. Active reads never use the supplement.
"""
from copy import deepcopy
from pathlib import Path, PurePosixPath
import re
import time

from . import authoring_package as ap, background_contract as bc, catalog_io as io
from . import background_io, background_package as bp, categories, palette_gate
from .authoring_staging import OwnedStage
from .contract import canonical_bytes, exact_keys, integer, InvalidInput

FORMAT = "picross-target-export-v6"
INSPECTION = "picross-target-inspection-v6"
ORIGINAL = "input/package.zip"
JSON_LIMIT = 8 * 1024 * 1024
BASE_KEYS = {"format", "adapter", "definition_id", "category_id", "categories",
             "runtime_revision", "package_revision", "save_slot", "stem", "definition", "reveal",
             "color_mapping", "selection", "handoff_sha256", "inventory_sha256", "approval_sha256",
             "technical", "editorial_approved", "catalog_ready", "registered", "test_only", "files", "palette_gate",
             "input", "background", "background_asset", "background_notice", "integration_ready"}


def _ref(name, raw):
    return {"file": ap.relative(name), "sha256": io.checksum(raw), "bytes": len(raw)}


def _check_ref(ref, raw, *, name=None, limit=ap.MAX_FILE):
    exact_keys(ref, {"file", "sha256", "bytes"})
    ap.relative(ref["file"])
    ap.sha(ref["sha256"])
    integer(ref["bytes"], 0, limit, "Export reference bytes")
    ap.require((name is None or ref["file"] == name) and
               len(raw) == ref["bytes"] and io.checksum(raw) == ref["sha256"],
               "Export reference size/hash/path mismatch")
    return raw


def _key(manifest, ref):
    return tuple(manifest[k] for k in ("file", "sha256", "bytes")) + tuple(ref[k] for k in ("file", "sha256", "bytes"))


class Transport:
    """Explicit per-export collector/resolver; never a general package fallback."""

    def __init__(self, directory=None, declared=None):
        self.offline = directory is not None
        self.directory = directory
        self.external, self.discarded, self.used, self.payload = {}, {}, set(), {}
        if self.offline:
            ap.require(isinstance(declared, list) and len(declared) <= ap.MAX_FILES,
                       "Invalid discarded background supplement list")
            for entry in declared:
                exact_keys(entry, {"manifest", "ref", "file"})
                for ref, limit in ((entry["manifest"], bc.MAX_JSON), (entry["ref"], ap.MAX_FILE)):
                    exact_keys(ref, {"file", "sha256", "bytes"})
                    ap.relative(ref["file"])
                    ap.sha(ref["sha256"])
                    integer(ref["bytes"], 0, limit, "Supplement reference bytes")
                ap.require(entry["file"] == "input/discarded/" + entry["ref"]["file"],
                           "Invalid discarded supplement path")
                ap.relative(entry["file"])
                key = _key(entry["manifest"], entry["ref"])
                ap.require(key not in self.discarded, "Duplicate discarded supplement")
                self.discarded[key] = deepcopy(entry)
            ap.require(declared == self.entries(), "Discarded supplements must be sorted by manifest/ref path")

    def _remember(self, name, raw):
        ap.relative(name)
        ap.require(name not in self.payload or self.payload[name] == raw,
                   "Conflicting background transport bytes: " + name)
        self.payload[name] = raw
        ap.require(len(self.payload) <= ap.MAX_FILES and sum(map(len, self.payload.values())) <= ap.MAX_TOTAL,
                   "Background transport exceeds export limits")

    def external_file(self, name, raw):
        self._remember("external/" + name, raw)
        self.external[name] = raw

    def discarded_file(self, manifest, ref, raw=None):
        key = _key(manifest, ref)
        entry = {"manifest": deepcopy(manifest), "ref": deepcopy(ref),
                 "file": "input/discarded/" + ref["file"]}
        if self.offline:
            ap.require(raw is None and self.discarded.get(key) == entry,
                       "Missing explicitly bound inactive supplement")
            raw = io.read(self.directory, entry["file"], min(ap.MAX_FILE, ref["bytes"]))
        else:
            ap.require(raw is not None, "History bytes required before supplement transport")
            ap.require(key not in self.discarded or self.discarded[key] == entry,
                       "Conflicting discarded supplement")
            self.discarded[key] = entry
        _check_ref(ref, raw)
        ap.require(not ref["file"].casefold().endswith(".zip") and
                   raw[:4] not in (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"),
                   "Embedded archive in discarded supplement")
        self._remember(entry["file"], raw)
        self.used.add(key)
        return raw

    def entries(self):
        return sorted(self.discarded.values(), key=lambda e: (e["manifest"]["file"], e["ref"]["file"]))

    def finish(self):
        ap.require(self.used == set(self.discarded), "Unneeded or active-only discarded supplement")

    def recheck_external(self, root):
        for name, raw in self.external.items():
            ap.require(root is not None and io.read(root, name, ap.MAX_FILE) == raw,
                       "External background source changed during export")


def _json(value):
    return canonical_bytes(value) + b"\n"


def _same(actual, expected):
    """Bound JSON keeps its types; Python treats True, 1 and 1.0 as equal."""
    return canonical_bytes(actual) == canonical_bytes(expected)


def _report(report, catalog, category_id, *, verified):
    from . import target_adapter as adapter
    ap.require(report["format"] == adapter.BACKGROUND_INSPECTION and report["technical"] and
               report["editorial_approved"] and report["background"]["ready"] and
               report["effective_state"] == "editorially_approved",
               "Background export requires full content readiness and final approval v2")
    categories.lookup(catalog, category_id)
    return {**report, "format": INSPECTION, "category_id": category_id, "category_ready": True,
            "export_verified": verified, "integration_ready": False, "catalog_ready": False, "registered": False}


def _background_bytes(package):
    checked = package.effective_background
    if checked["status"] == "none":
        return None, None
    ap.require(checked["status"] == "selected" and checked["ready"], "Unready selected background")
    binding = checked["binding"]["derivation"]
    root = package.root if binding["storage"] == "package" else package.external_root
    directory = str(PurePosixPath(bp._join(binding["root"], binding["ref"]["file"])).parent)
    ref = checked["derivation"]["output"]
    raw = io.read(root, bp._join(directory, ref["file"]), bc.MAX_PNG)
    _check_ref(ref, raw, name="background.png", limit=bc.MAX_PNG)
    candidate = next(c for c in checked["manifest"]["candidates"] if c["id"] == checked["decision"]["candidate_id"])
    p = candidate["provenance"]
    lines = ["Production ID: " + package.handoff["puzzle_id"], "Background: " + candidate["id"],
             "Image revision: " + candidate["revision"], "Artwork: " + p["author"], "Source: " + p["source"],
             "Usage basis: " + p["usage_basis"]]
    if p["attribution"] is not None:
        lines.append("Attribution: " + p["attribution"])
    return raw, ("\n".join(lines) + "\n").encode("utf-8")


def _paths(stem, suffix, puzzle_id, selected):
    return {"definition": "runtime/data/content/" + stem + ".json",
            "reveal": "runtime/art/content/" + stem + suffix,
            "notice": "runtime/art/content/" + stem + ".txt",
            "background_asset": "runtime/art/backgrounds/" + puzzle_id + ".png" if selected else None,
            "background_notice": "runtime/art/backgrounds/" + puzzle_id + ".txt" if selected else None}


def _identity(path):
    info = io.external(path).lstat()
    return io.signature(info), info.st_ctime_ns


def export_background(source, output, *, name, revision, stem, save_slot, approval_path,
                      category_id, categories_path, manual_authorization, palette_exception,
                      external_root, history_repo):
    from . import target_adapter as adapter
    source, output = io.external(source), io.external(output)
    ap.require(source.is_file(), "Background export requires the unchanged original ZIP")
    ap.require(not output.exists(), "Export output exists; use a new path")
    ap.require(isinstance(save_slot, str) and ap.STEM.fullmatch(save_slot), "Invalid explicit save slot")
    ap.require(isinstance(stem, str) and ap.STEM.fullmatch(stem), "Invalid explicit file stem")
    ap.require(categories_path is not None, "Explicit categories source is required")
    if external_root is not None:
        external_root = io.external(external_root)
    sources = {}

    def read_source(path, limit):
        path = io.external(path)
        before = _identity(path)
        raw = io.read(path.parent, path.name, limit)
        ap.require(_identity(path) == before, "Export source changed while reading")
        sources[path] = (before, raw, limit)
        return raw

    with io.budget():
        original = read_source(source, ap.MAX_ZIP)
        transport = Transport()
        with ap.open_package(source, allow_background=True, allow_manual_review=manual_authorization is not None,
                             external_root=external_root, history_repo=history_repo, transport=transport) as package:
            ap.require(package.background_enabled and package.archive_sha256 == io.checksum(original),
                       "Background export requires a stable original 0.7.0 ZIP")
            inspected, design, matrix, logic, approval = adapter.inspect(package, approval_path,
                allow_background=True, manual_authorization=manual_authorization, palette_exception=palette_exception)
            catalog_raw = read_source(categories_path, 128 * 1024)
            catalog = categories.validate(io.json_bytes(catalog_raw, 128 * 1024))
            report = _report(inspected, catalog, category_id, verified=False)
            approval_raw = read_source(approval["path"], 128 * 1024)
            ap.require(io.checksum(approval_raw) == approval["sha256"], "Final approval changed during export")
            transport.finish()
            png, notice = _background_bytes(package)
            paths = _paths(stem, Path(package.handoff["reveal"]["file"]).suffix, report["puzzle_id"], png is not None)
            definition, mapping = adapter.definition(report, design, matrix, logic, name, revision, Path(paths["reveal"]).name)
            payload = {ORIGINAL: original, "approval.json": approval_raw, "categories.json": _json(catalog),
                       paths["definition"]: _json(definition),
                       paths["reveal"]: package.file(package.handoff["reveal"]["file"]).read_bytes(),
                       paths["notice"]: adapter.player_notice(package, report).encode("utf-8"),
                       "usage.txt": _json({"production_id": report["puzzle_id"],
                                           "sources": adapter.source_provenances(package, report)}),
                       "inspection.json": _json(report), **transport.payload}
            if png is not None:
                payload[paths["background_asset"]] = png
                payload[paths["background_notice"]] = notice
            if manual_authorization is not None:
                from .manual_derivation import authorization, AUTH_FILE, OWNER_FILE
                auth = authorization(package, manual_authorization)
                payload[AUTH_FILE] = read_source(auth["path"], ap.MAX_FILE)
                payload[OWNER_FILE] = read_source(auth["owner_path"], ap.MAX_FILE)
                ap.require(io.checksum(payload[AUTH_FILE]) == report["manual_authorization_sha256"] and
                           io.checksum(payload[OWNER_FILE]) == report["owner_override_sha256"],
                           "Manual authorization changed during export")
            if palette_exception is not None:
                payload[palette_gate.EXCEPTION_FILE] = read_source(palette_exception, ap.MAX_FILE)
                ap.require(io.checksum(payload[palette_gate.EXCEPTION_FILE]) == report["palette_gate"]["exception"]["sha256"],
                           "Palette exception changed during export")
            manifest = {"format": FORMAT, "adapter": adapter.ADAPTER, "definition_id": report["puzzle_id"],
                "category_id": category_id, "categories": {"file": "categories.json", "sha256": io.checksum(payload["categories.json"])},
                "runtime_revision": revision, "package_revision": report["package_revision"], "save_slot": save_slot,
                "stem": stem, "definition": paths["definition"], "reveal": paths["reveal"], "color_mapping": mapping,
                "selection": report["selection"], "handoff_sha256": report["handoff_sha256"], "inventory_sha256": report["inventory_sha256"],
                "approval_sha256": approval["sha256"], "technical": True, "editorial_approved": True,
                "catalog_ready": False, "registered": False, "integration_ready": False, "test_only": report["test_only"],
                "files": {n: io.checksum(raw) for n, raw in sorted(payload.items())}, "palette_gate": report["palette_gate"],
                "input": {"original_package": _ref(ORIGINAL, original), "external_root": "external",
                          "discarded_files": transport.entries()},
                "background": deepcopy(approval["record"]["background"]),
                "background_asset": _ref(paths["background_asset"], png) if png is not None else None,
                "background_notice": _ref(paths["background_notice"], notice) if notice is not None else None}
            if manual_authorization is not None:
                manifest["manual_authorization"] = {"file": AUTH_FILE, "sha256": io.checksum(payload[AUTH_FILE])}
            if "deduction" in report:
                manifest["deduction"] = report["deduction"]
            output.parent.mkdir(parents=True, exist_ok=True)
            with OwnedStage(output.parent, ".hp-i1a-export-", "HP-I1a background export") as temporary:
                stage = temporary.mkdir("export")
                temporary.mkdir("export/external")
                for filename, raw in payload.items():
                    temporary.write("export/" + filename, raw)
                temporary.write("export/manifest.json", _json(manifest))
                # The private candidate explicitly has no export success flag.
                # Only the actual, independently read staged transport promotes it.
                _, verified = verify_background_export(stage, manifest, _json(manifest), _pending=True)
                temporary.replace("export/inspection.json", _json(verified))
                manifest["files"]["inspection.json"] = io.checksum(_json(verified))
                temporary.replace("export/manifest.json", _json(manifest))
                adapter.verify_export(stage)
                for path, (identity, raw, limit) in sources.items():
                    ap.require(_identity(path) == identity and io.read(path.parent, path.name, limit) == raw,
                               "Source changed before export publication")
                transport.recheck_external(external_root)
                io.tick()
                io.external(output)
                try:
                    background_io.publish_directory(stage, output)
                except bc.BackgroundError as exc:
                    raise InvalidInput(str(exc)) from exc
        return manifest


def _snapshot(directory, manifest):
    files = ap.file_table(directory, time.monotonic() + ap.SECONDS, original_zip=ORIGINAL)
    ap.require(isinstance(manifest["files"], dict) and set(files) == set(manifest["files"]) | {"manifest.json"},
               "Invalid/incomplete background export inventory")
    observations = {}
    for name, path in files.items():
        limit = ap.MAX_ZIP if name == ORIGINAL else ap.MAX_FILE
        identity = _identity(path)
        raw = io.read(directory, name, limit)
        ap.require(_identity(path) == identity, "Export file changed while reading")
        checksum = io.checksum(raw)
        if name != "manifest.json":
            ap.require(checksum == ap.sha(manifest["files"][name]), "Altered background export file: " + name)
        observations[name] = (identity, checksum)
    allowed_dirs = {"external"} | {str(parent) for n in files for parent in PurePosixPath(n).parents if str(parent) != "."}
    actual_dirs = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_dir()}
    ap.require(actual_dirs == allowed_dirs, "Unbound background export directory")
    return files, observations


def verify_background_export(directory, manifest, manifest_bytes, *, _pending=False):
    """Full fresh v6 read. The private pending mode is only for staged production."""
    from . import target_adapter as adapter
    with io.budget():
        directory = io.external(directory)
        root_id = _identity(directory)[0][:2]
        manual = "manual_authorization" in manifest
        paired = "deduction" in manifest
        exact_keys(manifest, BASE_KEYS | ({"manual_authorization"} if manual else set()) | ({"deduction"} if paired else set()))
        ap.require(manifest["format"] == FORMAT and manifest["adapter"] == adapter.ADAPTER, "Unsupported background export")
        inputs = exact_keys(manifest["input"], {"original_package", "external_root", "discarded_files"})
        exact_keys(inputs["original_package"], {"file", "sha256", "bytes"})
        ap.require(inputs["external_root"] == "external" and inputs["original_package"].get("file") == ORIGINAL,
                   "Invalid original ZIP/external transport location")
        files, observed = _snapshot(directory, manifest)
        ap.require(io.read(directory, "manifest.json", JSON_LIMIT) == manifest_bytes, "Export manifest changed")
        raw = io.read(directory, ORIGINAL, ap.MAX_ZIP)
        _check_ref(inputs["original_package"], raw, name=ORIGINAL, limit=ap.MAX_ZIP)
        transport = Transport(directory, inputs["discarded_files"])
        category_ref = exact_keys(manifest["categories"], {"file", "sha256"})
        ap.require(category_ref == {"file": "categories.json", "sha256": manifest["files"].get("categories.json")},
                   "Invalid categories reference")
        catalog = categories.load(files["categories.json"])
        manual_path = None
        if manual:
            from .manual_derivation import AUTH_FILE, OWNER_FILE
            exact_keys(manifest["manual_authorization"], {"file", "sha256"})
            ap.require(manifest["manual_authorization"] == {"file": AUTH_FILE, "sha256": manifest["files"].get(AUTH_FILE)},
                       "Manual export authorization binding mismatch")
            manual_path = files[AUTH_FILE]
        gate = exact_keys(manifest["palette_gate"], {"assessment", "binding", "visual_review", "exception", "allowed"})
        exception = files.get(palette_gate.EXCEPTION_FILE) if gate["exception"] is not None else None
        ap.require((exception is not None) == (gate["exception"] is not None), "Missing palette exception original")
        with ap.open_package(files[ORIGINAL], allow_background=True, allow_manual_review=manual,
                             external_root=directory / "external", transport=transport) as package:
            ap.require(package.background_enabled, "Export v6 requires original handoff v3 / Authoring 0.7.0")
            inspected, design, matrix, logic, approval = adapter.inspect(package, files["approval.json"], allow_background=True,
                manual_authorization=manual_path, palette_exception=exception)
            report = _report(inspected, catalog, manifest["category_id"], verified=not _pending)
            ap.require(approval is not None and manifest["approval_sha256"] == approval["sha256"] and
                       _same(manifest["background"], approval["record"]["background"]), "Final background approval differs")
            palette_gate.same(gate, report["palette_gate"], "Stale or altered export palette gate")
            ap.require(manual == ("manual_authorization_sha256" in report), "Export manual authorization generation differs")
            ap.require(paired == ("deduction" in report) and (not paired or _same(manifest["deduction"], report["deduction"])),
                       "Export deduction binding differs")
            ap.require(isinstance(manifest["stem"], str) and ap.STEM.fullmatch(manifest["stem"]) and
                       isinstance(manifest["save_slot"], str) and ap.STEM.fullmatch(manifest["save_slot"]), "Invalid export mapping")
            paths = _paths(manifest["stem"], Path(package.handoff["reveal"]["file"]).suffix,
                           report["puzzle_id"], package.effective_background["status"] == "selected")
            ap.require(all(manifest[k] == paths[k] for k in ("definition", "reveal")), "Invalid runtime export paths")
            d = io.json_bytes(io.read(directory, paths["definition"], ap.MAX_FILE), ap.MAX_FILE)
            expected, mapping = adapter.definition(report, design, matrix, logic, d["reveal"]["name"],
                                                   manifest["runtime_revision"], Path(paths["reveal"]).name)
            ap.require(_same(d, expected) and _same(manifest["color_mapping"], mapping) and
                       manifest["files"][paths["reveal"]] == report["selection"]["reveal"]["sha256"],
                       "Written runtime content differs from certified input")
            ap.require(io.read(directory, paths["notice"], ap.MAX_FILE) == adapter.player_notice(package, report).encode("utf-8"),
                       "Missing/changed player notice")
            ap.require(_same(io.json_bytes(io.read(directory, "usage.txt", ap.MAX_FILE), ap.MAX_FILE), {
                       "production_id": report["puzzle_id"], "sources": adapter.source_provenances(package, report)}),
                       "Usage notice differs from input provenance")
            png, notice = _background_bytes(package)
            for field, expected_raw in (("background_asset", png), ("background_notice", notice)):
                ref = manifest[field]
                if expected_raw is None:
                    ap.require(ref is None, "none must not carry a background asset or notice")
                else:
                    actual = io.read(directory, paths[field], ap.MAX_FILE)
                    _check_ref(ref, actual, name=paths[field])
                    ap.require(actual == expected_raw, "Runtime background/notice differs from verified active source")
            transport.finish()
            allowed = {ORIGINAL, "approval.json", "categories.json", "inspection.json", "usage.txt", "manifest.json",
                       *[n for n in paths.values() if n is not None], *transport.payload}
            if manual:
                allowed.update((AUTH_FILE, OWNER_FILE))
            if exception is not None:
                allowed.add(palette_gate.EXCEPTION_FILE)
            ap.require(set(files) == allowed, "Unbound or extra background export files")
            ap.require(manifest["definition_id"] == report["puzzle_id"] and _same(manifest["package_revision"], report["package_revision"]) and
                       all(_same(manifest[k], report[k]) for k in ("selection", "handoff_sha256", "inventory_sha256", "test_only")) and
                       all(manifest[k] is True for k in ("technical", "editorial_approved")) and
                       all(manifest[k] is False for k in ("catalog_ready", "registered", "integration_ready")),
                       "Invalid export gates/identity")
            stored = io.json_bytes(io.read(directory, "inspection.json", JSON_LIMIT), JSON_LIMIT)
            ap.require(isinstance(stored, dict) and set(stored) == set(report) and
                       all(_same(stored[k], report[k]) for k in report if k not in ("checked_at_utc", "tool", "fresh_verification")),
                       "Inspection record differs")
            ap.timestamp(stored["checked_at_utc"])
            tool = exact_keys(stored["tool"], {"adapter", "commit", "versions", "modules"})
            ap.require(tool["adapter"] == adapter.ADAPTER and isinstance(tool["modules"], dict) and
                       set(tool["modules"]) == set(report["tool"]["modules"]) and
                       (tool["commit"] is None or isinstance(tool["commit"], str) and re.fullmatch(r"[0-9a-f]{40}", tool["commit"])),
                       "Invalid inspection tool identity")
            for checksum in tool["modules"].values():
                ap.sha(checksum)
            versions = exact_keys(tool["versions"], {"tool", "pillow", "jpeg", "jpeg_turbo", "littlecms", "zlib"})
            ap.require(all(isinstance(versions[k], str) and 1 <= len(versions[k]) <= 128 for k in ("tool", "pillow")) and
                       all(value is None or isinstance(value, str) and 1 <= len(value) <= 128
                           for value in versions.values()), "Invalid inspection tool versions")
            ap.require(_same(stored["fresh_verification"], report["fresh_verification"]),
                       "Invalid stored fresh verification")
        _, after = _snapshot(directory, manifest)
        ap.require(root_id == _identity(directory)[0][:2] and after == observed and
                   io.read(directory, "manifest.json", JSON_LIMIT) == manifest_bytes,
                   "Background export changed during verification")
        report["export_verified"] = True
        return manifest, report
