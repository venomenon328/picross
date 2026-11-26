"""Current background preference and asset, without an export origin."""
import os
from copy import deepcopy
from pathlib import Path
from . import authoring_package as ap, background_contract as bc, current_content
from . import catalog_io as io, catalog_rating as rating
from .contract import canonical_bytes, exact_keys, integer, InvalidInput
RUNTIME_FORMAT = "picross-runtime-registry-v6"
ASSET_PATH = "game/art/backgrounds"
CAPABILITY = "game/data/background-capability.json"
CAPABILITY_FORMAT = "picross-runtime-background-capability-v1"
LIMIT = 1024*1024
CAPABILITY_LIMIT = 4096

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
