"""AT image authority, immutable production bindings and effective source resolver.

No solver, image conversion, Git lookup, actor authentication or network access.
"""
from copy import deepcopy
from datetime import datetime
from pathlib import Path
import re
import stat

from .authoring_package import require, sha
from .contract import canonical_bytes, digest, exact_keys, integer
from . import catalog_io as io, catalog_rating as rating, categories

FORMAT = "picross-catalog-reveal-v1"
APPROVAL = "picross-reveal-approval-v1"
ROOT = "content/reveals"
LIMIT = 1024 * 1024
IMAGE_LIMIT = 32 * 1024 * 1024


def path(identifier):
    return ROOT + "/" + rating.identity(identifier) + ".json"


def identity(entry):
    from .content_update import notice_path
    return {"key": entry["key"], "save_slot": entry["save_slot"],
            "definition": "game/" + entry["definition"], "reveal": "game/" + entry["reveal"],
            "notice": notice_path(entry)}


def source_paths(root, *registries, temporary=()):
    allowed = {path(e["id"]) for r in registries for e in r["entries"]}
    base = io.safe(root, ROOT)
    if not base.exists(): return set()
    require(base.is_dir(), "Reveal namespace must be a directory")
    found = set()
    for child in base.iterdir():
        name = child.relative_to(root).as_posix()
        p = io.safe(root, name)
        require(name in allowed or name in temporary, "Unknown/noncanonical reveal source: " + name)
        require(p.is_file() and (os_windows() or not p.stat().st_mode & 0o111), "Reveal source must be regular nonexecutable data")
        if name not in temporary: found.add(name)
    require(len(found) <= 10000, "Too many reveal sources")
    return found


def os_windows():
    import os
    return os.name == "nt"


def text(value, maximum):
    require(isinstance(value, str) and 1 <= len(value) <= maximum and value == value.strip() and
            not any(ord(c) < 32 or 127 <= ord(c) <= 159 for c in value), "Invalid reveal declaration text")
    value.encode("utf-8")
    return value


def notice(value):
    exact_keys(value, {"text", "sha256"})
    raw = value["text"].encode("utf-8") if isinstance(value["text"], str) else b""
    require(1 <= len(raw) <= 65536 and raw.endswith(b"\n") and b"\r" not in raw and b"\0" not in raw and
            not raw.startswith(b"\xef\xbb\xbf") and io.checksum(raw) == sha(value["sha256"]), "Invalid reveal notice")
    return value


def make_notice(raw):
    return notice({"text": raw.decode("utf-8"), "sha256": io.checksum(raw)})


def provenance(value):
    exact_keys(value, {"author", "usage_basis", "source", "changes"})
    for item in value.values(): text(item, 4096)
    return value


def approval(value, entry, revision, previous, current, notice_hash):
    exact_keys(value, {"format", "id", "image_revision", "definition_sha256", "previous_reveal_sha256",
                       "reveal_sha256", "notice_sha256", "actor", "timestamp_utc", "statement", "checks", "test_only"})
    integer(value["image_revision"], 1, 1000000, "image revision")
    require(value["format"] == APPROVAL and value["id"] == entry["id"] and value["image_revision"] == revision,
            "Wrong reveal approval identity/revision")
    for key, expected in (("definition_sha256", entry["production"]["definition_sha256"]),
                          ("previous_reveal_sha256", previous), ("reveal_sha256", current), ("notice_sha256", notice_hash)):
        require(sha(value[key]) == expected, "Wrong reveal approval " + key)
    text(value["actor"], 128); text(value["statement"], 4096)
    require(isinstance(value["timestamp_utc"], str) and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", value["timestamp_utc"]),
            "Invalid reveal approval UTC timestamp")
    datetime.strptime(value["timestamp_utc"], "%Y-%m-%dT%H:%M:%SZ")
    exact_keys(value["checks"], {"reveal_approved", "motif_raster_consistent", "final_editorial_approved"})
    require(all(v is True for v in value["checks"].values()) and type(value["test_only"]) is bool and
            value["test_only"] == entry["production"]["test_only"], "Reveal approval is incomplete or has wrong production mode")
    return value


def hashed(value, field):
    return {**value, field: digest(value)}


def check_hash(value, field):
    require(sha(value[field]) == digest({k: v for k, v in value.items() if k != field}), "Wrong reveal " + field)


def receipt(value, entry, notice_hash):
    exact_keys(value, {"format", "entry", "integrated_commit", "notice_sha256"})
    require(value["format"] == "picross-integrated-content-v1" and isinstance(value["integrated_commit"], str) and
            re.fullmatch(r"[0-9a-f]{40}", value["integrated_commit"]) and value["entry"] == entry and
            sha(value["notice_sha256"]) == notice_hash, "Integrated receipt identity/category/notice differs")
    return value


def validate(value, catalog):
    from .content_registry import validate as validate_registry, FORMAT as REGISTRY_FORMAT
    exact_keys(value, {"format", "id", "record_revision", "identity", "origin", "bindings", "revisions", "current", "record_hash"})
    require(value["format"] == FORMAT, "Unknown reveal source format")
    identifier = rating.identity(value["id"])
    exact_keys(value["identity"], {"key", "save_slot", "definition", "reveal", "notice"})
    origin = exact_keys(value["origin"], {"entry", "runtime_revision", "notice", "receipt"})
    integer(origin["runtime_revision"], 1, 1000000, "origin runtime revision")
    notice(origin["notice"])
    bindings, revisions = value["bindings"], value["revisions"]
    require(isinstance(bindings, list) and 1 <= len(bindings) <= 256 and
            isinstance(revisions, list) and 1 <= len(revisions) <= 256, "Invalid reveal history length")
    seen, packages, previous = {}, set(), None
    for index, binding in enumerate(bindings, 1):
        exact_keys(binding, {"binding_revision", "runtime_revision", "entry", "notice", "previous_binding_hash", "binding_hash"})
        integer(binding["binding_revision"], 1, 1000000, "binding revision")
        integer(binding["runtime_revision"], 1, 1000000, "binding runtime revision")
        require(binding["binding_revision"] == index and binding["previous_binding_hash"] == previous, "Broken reveal binding chain")
        entry = binding["entry"]
        validate_registry({"format": REGISTRY_FORMAT, "entries": [entry]}, catalog)
        require(entry["id"] == identifier and identity(entry) == value["identity"], "Reveal binding changes identity")
        notice(binding["notice"])
        if index == 1:
            require(all(binding[k] == origin[k] for k in ("entry", "runtime_revision", "notice")), "Reveal origin differs from first binding")
        else:
            require(binding["runtime_revision"] > bindings[index - 2]["runtime_revision"], "Reveal binding runtime revision did not increase")
        require(entry["production"]["revision"] not in packages, "Reveal binding reuses package revision")
        packages.add(entry["production"]["revision"])
        check_hash(binding, "binding_hash")
        previous = binding["binding_hash"]
        seen[previous] = binding
    if origin["receipt"] is not None: receipt(origin["receipt"], origin["entry"], origin["notice"]["sha256"])
    previous_image, previous_notice, last_binding = origin["entry"]["production"]["reveal_sha256"], origin["notice"]["text"], 1
    for index, revision in enumerate(revisions, 1):
        exact_keys(revision, {"image_revision", "binding_hash", "previous_reveal_sha256", "reveal_sha256", "notice", "approval", "provenance", "revision_hash"})
        integer(revision["image_revision"], 1, 1000000, "image revision")
        sha(revision['binding_hash'])
        require(revision["image_revision"] == index and revision["binding_hash"] in seen, "Broken reveal revision chain")
        binding = seen[revision["binding_hash"]]
        require(binding["binding_revision"] >= last_binding and (index != 1 or binding["binding_revision"] == 1), "Reveal revisions reorder bindings")
        last_binding = binding["binding_revision"]
        require(sha(revision["previous_reveal_sha256"]) == previous_image and sha(revision["reveal_sha256"]) != previous_image,
                "Reveal must replace exactly the previous image")
        notice(revision["notice"])
        require(revision["notice"]["text"].startswith(previous_notice), "Reveal notice removes prior attribution")
        approval(revision["approval"], binding["entry"], index, previous_image, revision["reveal_sha256"], revision["notice"]["sha256"])
        provenance(revision["provenance"]); check_hash(revision, "revision_hash")
        previous_image, previous_notice = revision["reveal_sha256"], revision["notice"]["text"]
    for binding in bindings[1:]:
        preceding = [r for r in revisions if seen[r["binding_hash"]]["binding_revision"] < binding["binding_revision"]]
        require(preceding and binding["entry"]["production"]["reveal_sha256"] == preceding[-1]["reveal_sha256"],
                "Historical raster rebind changes active image")
    exact_keys(value["current"], {"binding_revision", "image_revision"})
    for key in value["current"]: integer(value["current"][key], 1, 1000000, key)
    require(value["current"] == {"binding_revision": len(bindings), "image_revision": len(revisions)}, "Reveal current pointers differ")
    integer(value["record_revision"], 1, 1000000, "record revision")
    require(value["record_revision"] == len(bindings) + len(revisions) - 1, "Wrong reveal record revision")
    check_hash(value, "record_hash")
    require(len(canonical_bytes(value)) + 1 <= LIMIT, "Reveal record exceeds 1 MiB")
    return value


def package(root, entry):
    """Check every stored export byte without replaying a deduction trace."""
    from .content_update import notice_path
    prefix = entry["production"]["package"]
    raw = io.read(root, prefix + "/manifest.json", 8 * 1024 * 1024)
    manifest = io.json_bytes(raw, 8 * 1024 * 1024)
    require(isinstance(manifest,dict), 'Invalid package manifest object')
    files = {}
    base = io.safe(root, prefix)
    for p in base.rglob("*"):
        name = p.relative_to(root).as_posix()
        p = io.safe(root, name)
        if p.is_file(): files[name.removeprefix(prefix + "/")] = p
    if manifest.get("format") == "picross-integrated-content-v1":
        exact_keys(manifest, {"format", "entry", "integrated_commit", "notice_sha256"})
        require(isinstance(manifest["entry"], dict) and isinstance(manifest["entry"].get("production"), dict) and
                isinstance(manifest["entry"]["production"].get("package_sha256"), str), "Invalid receipt entry")
        require(set(files) == {"manifest.json"}, "Integrated package contains unbound files")
        original = deepcopy(entry)
        original["production"]["package_sha256"] = manifest["entry"]["production"]["package_sha256"]
        receipt(manifest, original, manifest["notice_sha256"])
        return original, manifest["notice_sha256"], manifest, set(prefix + "/" + n for n in files)
    require(manifest.get("format") in ("picross-target-export-v1", "picross-target-export-v2", "picross-target-export-v3", "picross-target-export-v4") and
            isinstance(manifest.get("files"), dict) and set(files) == set(manifest["files"]) | {"manifest.json"}, "Invalid/incomplete export inventory")
    legacy = manifest['format'].endswith('-v1')
    paired = manifest['format'].endswith('-v4')
    manual = manifest['format'].endswith('-v3') or paired and 'manual_authorization' in manifest
    exact_keys(manifest, {'format','adapter','definition_id','runtime_revision','package_revision','save_slot','stem','definition','reveal',
        'color_mapping','selection','handoff_sha256','inventory_sha256','approval_sha256','technical','editorial_approved','catalog_ready','registered','test_only','files'} |
        (set() if legacy else {'category_id','categories'}) | ({'manual_authorization'} if manual else set()) | ({'deduction'} if paired else set()))
    require(io.checksum(raw) == entry["production"]["package_sha256"], "Export manifest binding differs")
    for name, checksum in manifest["files"].items():
        require(io.file_hash(root, prefix + "/" + name) == sha(checksum), "Altered export file: " + name)
    require(manifest["definition_id"] == entry["id"] and manifest["save_slot"] == entry["save_slot"] and
            manifest["definition"] == "runtime/" + entry["definition"] and manifest["reveal"] == "runtime/" + entry["reveal"] and
            manifest["package_revision"] == entry["production"]["revision"] and manifest["test_only"] == entry["production"]["test_only"] and
            (manifest["format"].endswith("-v1") or manifest["category_id"] == entry["category_id"]), "Export identity/category differs")
    require(all(manifest["files"].get("runtime/" + entry[k]) == entry["production"][k + "_sha256"] for k in ("definition", "reveal")), "Export runtime binding differs")
    inspection = io.json_bytes(io.read(root, prefix + '/inspection.json', 8 * 1024 * 1024), 8 * 1024 * 1024)
    require(isinstance(inspection,dict) and all(k in inspection and inspection[k] == entry['production'][k] for k in ('width','height','mode','difficulty','test_only')) and
            inspection.get('package_revision') == entry['production']['revision'], 'Historical production metadata differs')
    notice_hash=sha(manifest['files'].get('runtime/'+notice_path(entry).removeprefix('game/')))
    return deepcopy(entry), notice_hash, None, set(prefix + "/" + n for n in files)


def normalized(root, entry):
    return package(root, entry)[0]


def load(root, entry, catalog):
    raw = io.read(root, path(entry["id"]), LIMIT, missing=True)
    if raw is None: return None
    value = validate(io.json_bytes(raw, LIMIT), catalog)
    require(raw == canonical_bytes(value) + b"\n" and value["id"] == entry["id"], "Noncanonical/wrong reveal source")
    return value


def resolve(root, entry, catalog, *, record=None):
    from .content_update import notice_path
    physical = io.file_hash(root, entry["production"]["package"] + "/manifest.json")
    require(physical == entry["production"]["package_sha256"], "Registered package binding changed")
    original, historical_notice, current_receipt, _ = package(root, entry)
    definition = io.read(root, "game/" + entry["definition"], 2 * 1024 * 1024)
    require(io.checksum(definition) == entry["production"]["definition_sha256"], "Registered definition binding changed")
    runtime_revision = rating.bytes_json(definition, 2 * 1024 * 1024)["revision"]
    record = load(root, entry, catalog) if record is None else validate(record, catalog)
    effective_image, effective_notice = entry["production"]["reveal_sha256"], historical_notice
    if record:
        binding = record["bindings"][-1]
        require(binding["entry"] == original and binding["runtime_revision"] == runtime_revision and
                binding["notice"]["sha256"] == historical_notice, "Active reveal production binding differs")
        if len(record["bindings"]) == 1 and record["origin"]["receipt"] is not None:
            require(current_receipt == record["origin"]["receipt"], "Original reveal receipt changed")
        effective_image = record["revisions"][-1]["reveal_sha256"]
        effective_notice = record["revisions"][-1]["notice"]["sha256"]
    require(io.file_hash(root, "game/" + entry["reveal"], IMAGE_LIMIT) == effective_image and
            io.file_hash(root, notice_path(entry), 65536) == effective_notice, "Effective reveal/notice binding changed")
    return {"id": entry["id"], "definition_sha256": entry["production"]["definition_sha256"],
            "runtime_revision": runtime_revision, "export_manifest_sha256": original["production"]["package_sha256"],
            "physical_manifest_sha256": physical, "historical_reveal_sha256": original["production"]["reveal_sha256"],
            "effective_reveal_sha256": effective_image, "historical_notice_sha256": historical_notice,
            "effective_notice_sha256": effective_notice, "record_hash": record["record_hash"] if record else None}


def revise(root, entry, catalog, image_hash, declaration, attribution, append=None):
    resolved = resolve(root, entry, catalog)
    old = load(root, entry, catalog)
    value = deepcopy(old)
    if value is None:
        original, _, integrated, _ = package(root, entry)
        original_notice = make_notice(io.read(root, identity(entry)["notice"], 65536))
        origin = {"entry": original, "runtime_revision": resolved["runtime_revision"], "notice": original_notice, "receipt": integrated}
        binding = hashed({"binding_revision": 1, **{k: origin[k] for k in ("entry", "runtime_revision", "notice")}, "previous_binding_hash": None}, "binding_hash")
        value = {"format": FORMAT, "id": entry["id"], "record_revision": 0, "identity": identity(entry),
                 "origin": origin, "bindings": [binding], "revisions": [], "current": {"binding_revision": 1, "image_revision": 0}}
    raw_notice = io.read(root, identity(entry)["notice"], 65536)
    if append is not None:
        require(isinstance(append, str), 'Notice append must be text or null')
        make_notice(append.encode("utf-8"))
        raw_notice += b"\n" + append.encode("utf-8")
    revision = {"image_revision": len(value["revisions"]) + 1, "binding_hash": value["bindings"][-1]["binding_hash"],
                "previous_reveal_sha256": resolved["effective_reveal_sha256"], "reveal_sha256": image_hash,
                "notice": make_notice(raw_notice), "approval": deepcopy(declaration), "provenance": deepcopy(attribution)}
    value["revisions"].append(hashed(revision, "revision_hash"))
    value["current"]["image_revision"] += 1
    value["record_revision"] += 1
    value.pop("record_hash", None)
    return validate(hashed(value, "record_hash"), catalog)


def rebind(old, entry, runtime_revision, export_notice, catalog):
    value = deepcopy(old)
    require(entry["production"]["reveal_sha256"] == old["revisions"][-1]["reveal_sha256"], "Raster update must retain active reveal")
    value["bindings"].append(hashed({"binding_revision": len(old["bindings"]) + 1, "runtime_revision": runtime_revision,
                                   "entry": deepcopy(entry), "notice": make_notice(export_notice),
                                   "previous_binding_hash": old["bindings"][-1]["binding_hash"]}, "binding_hash"))
    value["current"]["binding_revision"] += 1
    value["record_revision"] += 1
    value.pop("record_hash")
    return validate(hashed(value, "record_hash"), catalog)
