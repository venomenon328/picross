"""Current background preference and asset, without an export origin."""
import os
from copy import deepcopy
from pathlib import Path
from . import authoring_package as ap, background_contract as bc, current_content
from . import catalog_io as io, catalog_rating as rating
from .contract import canonical_bytes, exact_keys, integer, InvalidInput
FORMAT = current_content.BACKGROUND
REGISTRY_FORMAT = current_content.FORMAT
RUNTIME_FORMAT = "picross-runtime-registry-v6"
PATH = "content/backgrounds"
ASSET_PATH = "game/art/backgrounds"
CAPABILITY = "game/data/background-capability.json"
CAPABILITY_FORMAT = "picross-runtime-background-capability-v1"
LIMIT = 1024*1024
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


def capability(root, texts=None, *, required=False, profile_id=None):
    raw = _raw(root, CAPABILITY, CAPABILITY_LIMIT, texts, missing=True)
    enabled, profiles = False, []
    if raw is not None:
        value = io.json_bytes(raw, CAPABILITY_LIMIT)
        ap.require(isinstance(value, dict), "Invalid background capability")
        if value.get("format") == CAPABILITY_FORMAT:
            exact_keys(value, {"format", "runtime_format", "profile_id", "enabled"})
            ap.require(value["runtime_format"] == RUNTIME_FORMAT and value["profile_id"] == bc.PROFILE["id"],
                       "Invalid background capability")
            profiles = [bc.PROFILE["id"]]
        else:
            exact_keys(value, {"format", "runtime_format", "profile_ids", "enabled"})
            ap.require(value["format"] == "picross-runtime-background-capability-v2" and
                       value["runtime_format"] == "picross-runtime-registry-v8" and
                       value["profile_ids"] == list(bc.PROFILES), "Invalid background capability")
            profiles = value["profile_ids"]
        ap.require(type(value["enabled"]) is bool, "Invalid background capability")
        enabled = value["enabled"]
    ap.require(not required or enabled, "Selected/none background requires enabled target capability")
    ap.require(profile_id is None or enabled and profile_id in profiles, "Background profile requires compatible enabled target capability")
    return enabled


def image_profile(raw):
    """Geometry of already validated PNG bytes, never a new assetref field."""
    import struct
    ap.require(len(raw) >= 33 and raw[:16] == b"\x89PNG\r\n\x1a\n\0\0\0\rIHDR", "Invalid background PNG header")
    profile = bc.SIZES.get(struct.unpack_from(">II", raw, 16))
    ap.require(profile is not None, "Unsupported background dimensions")
    return profile


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


def notice_bytes(identifier, candidate):
    """Use the original background notice wording for a checked candidate."""
    if candidate is None:
        return None
    p = candidate["provenance"]
    lines = ["Production ID: " + identifier, "Background: " + candidate["id"],
             "Image revision: " + candidate["revision"], "Artwork: " + p["author"], "Source: " + p["source"],
             "Usage basis: " + p["usage_basis"]]
    if p["attribution"] is not None:
        lines.append("Attribution: " + p["attribution"])
    raw = ("\n".join(lines) + "\n").encode("utf-8")
    ap.require(len(raw) <= 65536, "Background notice exceeds byte limit")
    return raw


def validate(value, entry):
    return current_content.validate_source(value, entry)


def current(source):
    validate(source, None)
    return source["current"]


def effective(source):
    return {**current(source), "identity": source["binding"]["identity"]}


def _source(root, registry, entry, texts=None):
    name = path(entry["id"])
    raw = _raw(root, name, LIMIT, texts)
    ap.require(index(registry).get(entry["id"]) == ref(name,raw), "Background source/index mismatch")
    return validate(io.json_bytes(raw,LIMIT),entry)


def load(root, registry, entry, texts=None):
    source = _source(root, registry, entry, texts)
    ident = source["binding"]["identity"]
    raw = _raw(root,ident["definition"]["file"],2*LIMIT,texts)
    ap.require(current_content.identity(entry,raw) == ident,"Stale background definition")
    active = current(source)
    capability(root,texts,required=active["status"] in ("selected","none"))
    if active["asset"]:
        raw = _bound(active["asset"],_raw(root,active["asset"]["file"],32*1024*1024,texts))
        capability(root, texts, required=True, profile_id=image_profile(raw))
    return source


def retained_names(root, registry, texts=None):
    return {asset["file"] for entry in registry["entries"]
            if (asset := _source(root,registry,entry,texts)["current"]["asset"]) is not None}


def projection(registry, texts):
    result = {}
    for entry in registry["entries"]:
        active = deepcopy(_source(None,registry,entry,texts)["current"])
        if active["asset"]: active["asset"]["file"] = active["asset"]["file"].removeprefix("game/")
        result[entry["id"]] = active
    return result
