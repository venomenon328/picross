"""Current reveal authority and rights validation; no package history."""
from copy import deepcopy
from pathlib import Path
from .authoring_package import relative, require, sha
from .contract import canonical_bytes, digest, exact_keys, integer
from . import catalog_io as io, catalog_rating as rating, current_content
FORMAT = current_content.REVEAL
ROOT = "content/reveals"
LIMIT = 1024*1024
IMAGE_LIMIT = 32*1024*1024

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


def hashed(value, field):
    return {**value, field: digest(value)}


def check_hash(value, field):
    require(sha(value[field]) == digest({k: v for k, v in value.items() if k != field}), "Wrong reveal " + field)


def validate(value, catalog=None, **unused):
    return current_content.validate_source(value)


def normalized(root, entry):
    return deepcopy(entry)


def load(root, entry, catalog=None):
    return current_content.load_source(root, entry, "reveal")


def resolve(root, entry, catalog=None, *, record=None):
    record = load(root, entry, catalog) if record is None else current_content.validate_source(record, entry)
    ident = record["binding"]["identity"]
    raw = current_content.bound(root, ident["definition"], limit=2*1024*1024)
    require(current_content.identity(entry, raw) == ident, "Stale reveal definition binding")
    image = record["current"]["asset"]
    current_content.bound(root, image, limit=IMAGE_LIMIT)
    notice_raw = io.read(root, current_content.notice_path(entry), 65536)
    make_notice(notice_raw)
    return {"id": entry["id"], "definition_sha256": ident["definition"]["sha256"],
            "runtime_revision": ident["runtime_revision"], "effective_reveal_sha256": image["sha256"],
            "effective_notice_sha256": io.checksum(notice_raw), "record_hash": record["record_hash"],
            "effective_reveal": image["file"].removeprefix("game/"), "effective_reveal_ref": image}
