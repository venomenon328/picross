"""HP-I1b1 active background authority, separate from historical production.

Only a freshly verified v6 registration creates this source. After retirement
its inner references are historical identities, never file-reading requests.
"""
from copy import deepcopy
from io import BytesIO
from pathlib import Path
import os
import re
import stat
import zipfile

from . import authoring_package as ap, background_contract as bc, background_package as bp
from . import catalog_io as io, catalog_rating as rating
from .contract import canonical_bytes, exact_keys, integer, InvalidInput

FORMAT = "picross-catalog-background-v1"
REGISTRY_FORMAT = "picross-content-registry-v3"
RUNTIME_FORMAT = "picross-runtime-registry-v6"
RECEIPT_FORMAT = "picross-integrated-content-v2"
PATH = "content/backgrounds"
ASSET_PATH = "game/art/backgrounds"
CAPABILITY = "game/data/background-capability.json"
CAPABILITY_FORMAT = "picross-runtime-background-capability-v1"
LIMIT = 1024 * 1024
CAPABILITY_LIMIT = 4096


def path(identifier):
    return PATH + "/" + rating.identity(identifier) + ".json"


def asset_path(identifier):
    return ASSET_PATH + "/" + rating.identity(identifier) + ".png"


def notice_path(identifier):
    return ASSET_PATH + "/" + rating.identity(identifier) + ".txt"


def encoded(value):
    return canonical_bytes(value) + b"\n"


def ref(name, raw):
    return {"file": name, "sha256": io.checksum(raw), "bytes": len(raw)}


def _ref(value, *, name=None, limit=ap.MAX_FILE):
    exact_keys(value, {"file", "sha256", "bytes"})
    ap.relative(value["file"]); ap.sha(value["sha256"])
    integer(value["bytes"], 0, limit, "background reference bytes")
    ap.require(name is None or value["file"] == name, "Wrong background reference path")
    return value


def _bound(value, raw, *, name=None, limit=ap.MAX_FILE):
    _ref(value, name=name, limit=limit)
    ap.require(raw is not None and value["bytes"] == len(raw) and value["sha256"] == io.checksum(raw),
               "Background reference size/hash differs: " + value["file"])
    return raw


def _raw(root, name, limit, texts=None, *, missing=False):
    if texts is not None and name in texts:
        raw = texts[name]
        raw = raw.encode("utf-8") if isinstance(raw, str) else raw
        ap.require(raw is None and missing or isinstance(raw, bytes) and len(raw) <= limit,
                   "Missing/oversized background text: " + name)
        return raw
    ap.require(root is not None, "Missing bound background text: " + name)
    return io.read(root, name, limit, missing=missing)


def capability(root, texts=None, *, required=False):
    raw = _raw(root, CAPABILITY, CAPABILITY_LIMIT, texts, missing=True)
    enabled = False
    if raw is not None:
        value = exact_keys(io.json_bytes(raw, CAPABILITY_LIMIT), {"format", "runtime_format", "profile_id", "enabled"})
        ap.require(value["format"] == CAPABILITY_FORMAT and value["runtime_format"] == RUNTIME_FORMAT and
                   value["profile_id"] == bc.PROFILE["id"] and type(value["enabled"]) is bool,
                   "Invalid background capability")
        enabled = value["enabled"]
    ap.require(not required or enabled, "Background export v6 requires enabled compatible target capability")
    return enabled


def index(registry):
    rows = registry.get("backgrounds", [])
    ap.require(isinstance(rows, list) and len(rows) <= len(registry["entries"]), "Invalid background index")
    ids = {e["id"] for e in registry["entries"]}
    found = {}
    for row in rows:
        exact_keys(row, {"id", "source"})
        identifier = rating.identity(row["id"])
        ap.require(identifier in ids and identifier not in found, "Unknown/duplicate background ID")
        found[identifier] = _ref(row["source"], name=path(identifier), limit=LIMIT)
    ap.require(list(found) == sorted(found), "Background index must be sorted")
    return found


def text_names(registry):
    return {CAPABILITY} | {name for e in registry["entries"] for name in (path(e["id"]), notice_path(e["id"]))}


def source_paths(root, *registries, temporary=()):
    ids = {identifier for registry in registries for identifier in index(registry)}
    allowed = ({path(i) for i in ids}, {p for i in ids for p in (asset_path(i), notice_path(i))})
    result = []
    for base_name, names in zip((PATH, ASSET_PATH), allowed):
        base = io.safe(root, base_name)
        found = set()
        if base.exists():
            ap.require(base.is_dir(), "Background namespace must be a directory")
            for child in base.iterdir():
                name = child.relative_to(root).as_posix()
                child = io.safe(root, name)
                ap.require(name in names or name in temporary, "Unknown/noncanonical background source: " + name)
                ap.require(child.is_file() and (os.name == "nt" or not child.stat().st_mode & 0o111),
                           "Background source must be regular nonexecutable data")
                if name not in temporary: found.add(name)
        ap.require(len(found) <= 20000, "Too many background sources")
        result.append(found)
    return tuple(result)


def _approval(value, package, test_only):
    exact_keys(value, {"format", "actor", "timestamp_utc", "statement", "puzzle_id", "revision",
                       "handoff_sha256", "inventory_sha256", "selection", "test_only", "original_zip_sha256", "background"})
    ap.require(value["format"] == "picross-editorial-approval-v2", "Wrong historical background approval format")
    for field in ("actor", "statement"): ap.string(value[field], "approval " + field)
    ap.timestamp(value["timestamp_utc"])
    ap.require(all(value[k] == package[k] for k in package) and type(value["test_only"]) is bool and
               value["test_only"] == test_only, "Historical background approval identity differs")
    selection = exact_keys(value["selection"], {"variant", "matrix_hash", "logic_hash", "reveal"})
    ap.string(selection["variant"], "approval variant")
    for field in ("matrix_hash", "logic_hash"): ap.sha(selection[field])
    exact_keys(selection["reveal"], {"file", "sha256"})
    ap.relative(selection["reveal"]["file"]); ap.sha(selection["reveal"]["sha256"])
    background = exact_keys(value["background"], {"manifest", "decision", "derivation", "outcome", "candidate_id",
                                                 "original", "output", "profile_sha256"})
    for field in ("manifest", "decision", "derivation"):
        bp._stored(background[field], False)
    ap.sha(background["profile_sha256"])
    return background


def _diagnostics(value, selected):
    exact_keys(value, {"source", "output", "upscaled"})
    if not selected:
        ap.require(all(v is None for v in value.values()), "none has image diagnostics")
        return
    ap.require(type(value["upscaled"]) is bool, "Invalid background upscale diagnostic")
    for key in ("source", "output"):
        d = exact_keys(value[key], {"format", "mode", "width", "height", "alpha"})
        ap.require(d["format"] == "PNG" and d["mode"] == "RGBA", "Invalid background image diagnostic")
        for field in ("width", "height"): integer(d[field], 1, 16384, "background axis")
        alpha = exact_keys(d["alpha"], {"min", "max", "transparent_pixels", "partial_pixels", "opaque_pixels"})
        integer(alpha["min"], 0, 255, "alpha minimum"); integer(alpha["max"], 0, 255, "alpha maximum")
        for field in ("transparent_pixels", "partial_pixels", "opaque_pixels"):
            integer(alpha[field], 0, d["width"] * d["height"], "alpha pixels")
        ap.require(alpha["min"] == 0 < alpha["max"] and alpha["transparent_pixels"] > 0 and
                   sum(alpha[f] for f in ("transparent_pixels", "partial_pixels", "opaque_pixels")) == d["width"] * d["height"] and
                   alpha["transparent_pixels"] < d["width"] * d["height"], "Invalid background alpha diagnostic")
        if key == "output": ap.require((d["width"], d["height"]) == (2304, 576), "Wrong background output dimensions")


def _derivation(value, decision, approval, test_only):
    exact_keys(value, {"format", "request_sha256", "request", "puzzle_id", "job_id", "background_revision", "manifest",
                       "decision", "outcome", "candidate_id", "source", "profile", "profile_sha256", "tool", "tool_sha256",
                       "output", "diagnostics", "test_only"})
    ap.require(value["format"] == "picross-background-derivation-v1", "Wrong historical background derivation format")
    request = bc.validate_request(value["request"])
    ap.require(ap.sha(value["request_sha256"]) == bc.digest(request) and
               all(value[k] == request[k] for k in ("manifest", "decision", "source", "profile")) and
               value["manifest"] == decision["manifest"] == approval["manifest"]["ref"] and
               value["decision"] == approval["decision"]["ref"] and
               value["source"] == decision["original"] == approval["original"] and
               all(value[k] == decision[k] for k in ("puzzle_id", "job_id", "background_revision", "outcome", "candidate_id")) and
               value["outcome"] == approval["outcome"] and value["candidate_id"] == approval["candidate_id"] and
               value["output"] == approval["output"] and
               value["profile_sha256"] == approval["profile_sha256"] == bc.digest(bc.PROFILE) and
               type(value["test_only"]) is bool and value["test_only"] == test_only,
               "Historical background derivation binding differs")
    tool = exact_keys(value["tool"], {"id", "commit", "dirty", "versions", "modules"})
    ap.require(tool["id"] == "picross-background-1" and isinstance(tool["commit"], str) and
               re.fullmatch(r"[0-9a-f]{40}", tool["commit"]) and type(tool["dirty"]) is bool,
               "Invalid historical background tool")
    versions = exact_keys(tool["versions"], {"python", "pillow", "zlib", "littlecms"})
    for v in versions.values(): ap.string(v, "historical codec")
    ap.require(versions["pillow"] == "12.3.0", "Wrong historical background Pillow contract")
    modules = tool["modules"]
    ap.require(isinstance(modules, list) and len(modules) == 9, "Invalid historical background module inventory")
    names = []
    for row in modules:
        exact_keys(row, {"file", "sha256"}); ap.relative(row["file"]); ap.sha(row["sha256"]); names.append(row["file"])
    expected_modules = ["tools/puzzle_production/" + name + ".py" for name in (
        "__init__", "authoring_package", "background_assets", "background_contract", "background_io", "catalog_io",
        "contract", "image_normalization", "operation_diagnostics")]
    ap.require(names == expected_modules and
               ap.sha(value["tool_sha256"]) == request["expected_tool_sha256"] == bc.digest(tool),
               "Historical background tool binding differs")
    _diagnostics(value["diagnostics"], decision["outcome"] == "selected")
    return value


def validate(value, entry):
    try:
        # The existing background JSON parser enforces depth 32, bounded keys,
        # duplicate-key rejection and exact JSON scalar types, without I/O.
        bc._json_tree(value)
        raw = encoded(value)
        ap.require(len(raw) <= LIMIT, "Background source exceeds 1 MiB")
        value = bc.parse_json(raw)
        exact_keys(value, {"format", "puzzle_id", "identity", "origin", "image_revision", "candidate_revision",
                           "decision", "derivation", "provenance", "review", "asset", "notice", "test_only"})
        ap.require(value["format"] == FORMAT and value["puzzle_id"] == entry["id"] and
                   type(value["test_only"]) is bool and value["test_only"] == entry["production"]["test_only"],
                   "Wrong background source identity")
        identity = exact_keys(value["identity"], {"key", "save_slot", "definition", "runtime_revision"})
        ap.require(all(identity[k] == entry[k] for k in ("key", "save_slot")), "Background slot/key differs")
        _ref(identity["definition"], name="game/" + entry["definition"], limit=2 * LIMIT)
        ap.require(identity["definition"]["sha256"] == entry["production"]["definition_sha256"], "Background definition binding differs")
        integer(identity["runtime_revision"], 1, 1000000, "background runtime revision")
        integer(value["image_revision"], 1, 1000000, "active background revision")
        ap.require(value["image_revision"] == 1, "Background replacement requires HP-I1b2")
        origin = exact_keys(value["origin"], {"package", "export_manifest_sha256", "original_package", "manifest", "approval_ref", "approval"})
        ap.require(origin["package"] == entry["production"]["package"] ==
                   "content/packages/" + entry["id"] + "/" + entry["production"]["revision"], "Background package path differs")
        ap.sha(origin["export_manifest_sha256"])
        package = exact_keys(origin["original_package"], {"puzzle_id", "revision", "original_zip_sha256", "handoff_sha256", "inventory_sha256"})
        ap.require(package["puzzle_id"] == entry["id"] and package["revision"] == entry["production"]["revision"], "Background original identity differs")
        for field in ("original_zip_sha256", "handoff_sha256", "inventory_sha256"): ap.sha(package[field])
        bp._stored(origin["manifest"], False)
        _ref(origin["approval_ref"], name="approval.json", limit=128 * 1024)
        approval = _approval(origin["approval"], package, value["test_only"])
        ap.require(origin["manifest"] == approval["manifest"], "Background original manifest differs")
        ap.require(origin["approval"]["selection"]["reveal"]["sha256"] == entry["production"]["reveal_sha256"],
                   "Historical background approval binds another reveal")
        decision = bc.validate_decision(value["decision"])
        ap.require(decision["puzzle_id"] == entry["id"] and decision["test_only"] == value["test_only"] and
                   decision["outcome"] in ("selected", "none"), "Wrong active background decision")
        derivation = _derivation(value["derivation"], decision, approval, value["test_only"])
        if decision["outcome"] == "selected":
            bc._revision(value["candidate_revision"])
            bc._provenance(value["provenance"]); bc._review(value["review"], decision["original"])
            ap.require(value["provenance"]["rights_status"] == "resolved" and value["review"] is not None,
                       "Background requires resolved rights and review")
            accepted = {r["criterion"] for r in decision["accepted_deviations"]}
            ap.require(all(row["result"] == "erfüllt" or key != "Q-HG01" and key in accepted and
                           row["result"] in ("Warnung", "nicht erfüllt") for key, row in value["review"].items()),
                       "Background review is not ready")
            _ref(derivation["output"], name="background.png", limit=bc.MAX_PNG)
            _ref(value["asset"], name=asset_path(entry["id"]), limit=bc.MAX_PNG)
            _ref(value["notice"], name=notice_path(entry["id"]), limit=65536)
            ap.require(all(value["asset"][k] == derivation["output"][k] for k in ("sha256", "bytes")), "Background output binding differs")
        else:
            ap.require(all(value[k] is None for k in ("candidate_revision", "provenance", "review", "asset", "notice")) and
                       derivation["output"] is None, "none must not carry an image, notice or candidate")
        return value
    except bc.BackgroundError as exc:
        raise InvalidInput("Background source: " + str(exc)) from exc


def build(export_dir, manifest, report, entry):
    """Project the actual bound originals; caller must first fully verify v6.

    This reads only the active original metadata; it never synthesizes a proof,
    approval or tool identity. Full input/stage replay remains the caller's gate.
    """
    try:
        return _build(export_dir, manifest, entry)
    except (bc.BackgroundError, zipfile.BadZipFile) as exc:
        raise InvalidInput("Invalid background production metadata: " + str(exc)) from exc


def _build(export_dir, manifest, entry):
    ap.require(manifest.get("format") == "picross-target-export-v6", "Background source requires a v6 export")
    approval_raw = io.read(export_dir, "approval.json", 128 * 1024)
    approval = io.json_bytes(approval_raw, 128 * 1024)
    binding = approval["background"]
    original_ref = manifest["input"]["original_package"]
    original_raw = io.read(export_dir, "input/package.zip", ap.MAX_ZIP)
    _bound(original_ref, original_raw, name="input/package.zip", limit=ap.MAX_ZIP)
    ap.require(approval["original_zip_sha256"] == original_ref["sha256"] and
               manifest["approval_sha256"] == io.checksum(approval_raw) and
               all(canonical_bytes(approval[k]) == canonical_bytes(manifest[k]) for k in ("background", "selection", "handoff_sha256", "inventory_sha256", "test_only")),
               "Original background approval/export bindings differ")
    with zipfile.ZipFile(BytesIO(original_raw)) as archive:
        # Match the existing original-ZIP namespace, including its permitted
        # single outer package directory, without extracting/replaying images.
        infos = archive.infolist()
        ap.require(len(infos) <= ap.MAX_FILES * 2, "Too many original ZIP members")
        seen, leaves, total = set(), [], 0
        for info in infos:
            name = ap.relative(info.filename.rstrip("/"))
            ap.require(name.casefold() not in seen, "Duplicate original ZIP member")
            seen.add(name.casefold())
            ap.require(stat.S_IFMT(info.external_attr >> 16) in (0, stat.S_IFREG, stat.S_IFDIR) and
                       not info.flag_bits & 1 and info.file_size <= ap.MAX_FILE,
                       "Unsafe/oversized original ZIP member")
            total += info.file_size
            ap.require(total <= ap.MAX_TOTAL, "Expanded original ZIP exceeds limit")
            if not info.is_dir(): leaves.append(name)
        ap.require(len(leaves) <= ap.MAX_FILES, "Too many original ZIP files")
        keys = {name.casefold() for name in leaves}
        ap.require(all(not any("/".join(name.casefold().split("/")[:n]) in keys
                       for n in range(1, len(name.split("/")))) for name in leaves), "Original ZIP file/directory collision")
        roots = {name.split("/")[0] for name in leaves}
        ap.require("handoff.json" in keys or len(roots) == 1, "Original ZIP requires a single package root")
        prefix = "" if "handoff.json" in keys else next(iter(roots)) + "/"
        def read(stored):
            bp._stored(stored, False)
            r = stored["ref"]
            name = bp._join(stored["root"], r["file"])
            if stored["storage"] == "package":
                info = archive.getinfo(prefix + name)
                ap.require(info.file_size <= bc.MAX_JSON, "Background metadata ZIP member exceeds limit")
                with archive.open(info) as stream: raw = stream.read(bc.MAX_JSON + 1)
            else:
                raw = io.read(export_dir, "external/" + name, bc.MAX_JSON)
            _bound(r, raw, limit=bc.MAX_JSON)
            return io.json_bytes(raw, bc.MAX_JSON)
        work = bc.validate_manifest(read(binding["manifest"]))
        decision = read(binding["decision"])
        derivation = read(binding["derivation"])
    decision = bc.validate_decision(decision)
    ap.require(work["puzzle_id"] == entry["id"] and work["test_only"] == manifest["test_only"], "Original background work identity differs")
    candidate = bc._bind_decision(work, decision)
    def live(field):
        r = manifest[field]
        if r is None: return None
        raw = io.read(export_dir, r["file"], bc.MAX_PNG if field == "background_asset" else 65536)
        _bound(r, raw)
        return {**r, "file": "game/" + r["file"].removeprefix("runtime/")}
    definition = io.read(export_dir, manifest["definition"], 2 * LIMIT)
    source = {"format": FORMAT, "puzzle_id": entry["id"],
        "identity": {"key": entry["key"], "save_slot": entry["save_slot"],
                     "definition": ref("game/" + entry["definition"], definition), "runtime_revision": manifest["runtime_revision"]},
        "origin": {"package": entry["production"]["package"],
                   "export_manifest_sha256": io.file_hash(export_dir, "manifest.json", 8 * LIMIT),
                   "original_package": {k: approval[k] for k in ("puzzle_id", "revision", "original_zip_sha256", "handoff_sha256", "inventory_sha256")},
                   "manifest": deepcopy(binding["manifest"]), "approval_ref": ref("approval.json", approval_raw), "approval": approval},
        "image_revision": 1, "candidate_revision": candidate["revision"] if candidate else None,
        "decision": decision, "derivation": derivation,
        "provenance": deepcopy(candidate["provenance"]) if candidate else None,
        "review": deepcopy(candidate["review"]) if candidate else None,
        "asset": live("background_asset"), "notice": live("background_notice"), "test_only": manifest["test_only"]}
    return validate(source, entry)


def _source(root, registry, entry, texts=None):
    refs = index(registry)
    r = refs.get(entry["id"])
    raw = _raw(root, path(entry["id"]), LIMIT, texts, missing=True)
    if r is None:
        ap.require(raw is None, "Undeclared background source")
        return None
    _bound(r, raw, name=path(entry["id"]), limit=LIMIT)
    value = validate(io.json_bytes(raw, LIMIT), entry)
    ap.require(raw == encoded(value), "Noncanonical background source")
    return value


def origin_hash(source):
    return io.checksum(canonical_bytes(source["origin"]))


def receipt_binding(source, source_ref):
    return {"origin_sha256": origin_hash(source), "source": deepcopy(source_ref)}


def _receipt(source, source_ref, receipt):
    value = exact_keys(receipt.get("background"), {"origin_sha256", "source"})
    ap.require(value == receipt_binding(source, source_ref), "Background receipt/index/origin binding differs")
    ap.require(receipt["entry"]["production"]["package_sha256"] == source["origin"]["export_manifest_sha256"],
               "Background receipt changed original export anchor")


def load(root, registry, entry, texts=None):
    source = _source(root, registry, entry, texts)
    if source is None:
        for name in (asset_path(entry["id"]), notice_path(entry["id"])):
            ap.require(not io.safe(root, name).exists(), "Legacy entry has background files")
        return None
    definition = source["identity"]["definition"]
    raw = _raw(root, definition["file"], 2 * LIMIT, texts)
    _bound(definition, raw, limit=2 * LIMIT)
    ap.require(io.json_bytes(raw, 2 * LIMIT)["revision"] == source["identity"]["runtime_revision"], "Background runtime revision differs")
    for key, name, limit in (("asset", asset_path(entry["id"]), bc.MAX_PNG), ("notice", notice_path(entry["id"]), 65536)):
        raw = _raw(root, name, limit, texts, missing=True)
        if source[key] is None: ap.require(raw is None, "none has a live background file")
        else: _bound(source[key], raw, name=name, limit=limit)
    manifest_raw = io.read(root, entry["production"]["package"] + "/manifest.json", 8 * LIMIT)
    manifest = io.json_bytes(manifest_raw, 8 * LIMIT)
    ap.require(io.checksum(manifest_raw) == entry["production"]["package_sha256"], "Background physical package binding differs")
    if manifest.get("format") == RECEIPT_FORMAT:
        _receipt(source, index(registry)[entry["id"]], manifest)
    else:
        ap.require(manifest.get("format") == "picross-target-export-v6" and
                   source["origin"]["export_manifest_sha256"] == entry["production"]["package_sha256"],
                   "Background source requires its original v6 export or v2 receipt")
        ap.require(canonical_bytes(build(io.safe(root, entry["production"]["package"]), manifest, None, entry)) == canonical_bytes(source),
                   "Active background source differs from original approved production")
    return source


def check_receipt(root, registry, entry, receipt):
    source = load(root, registry, entry)
    ap.require(source is not None and receipt.get("format") == RECEIPT_FORMAT, "Missing background receipt authority")
    _receipt(source, index(registry)[entry["id"]], receipt)
    return source


def retained_names(root, registry, texts=None):
    return {source["asset"]["file"] for entry in registry["entries"]
            if (source := _source(root, registry, entry, texts)) is not None and source["asset"] is not None}


def projection(registry, texts):
    result = {}
    for entry in registry["entries"]:
        source = _source(None, registry, entry, texts)
        result[entry["id"]] = {"status": source["decision"]["outcome"] if source else "legacy",
                               "image_revision": source["image_revision"] if source else None,
                               "asset": {**source["asset"], "file": source["asset"]["file"].removeprefix("game/")}
                               if source and source["asset"] else None}
    return result
