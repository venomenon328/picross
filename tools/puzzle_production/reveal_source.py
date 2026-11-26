"""Current reveal authority and rights validation; no package history."""
from .authoring_package import require, sha
from .contract import exact_keys
from . import catalog_io as io

IMAGE_LIMIT = 32 * 1024 * 1024


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
