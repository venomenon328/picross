"""Current image declarations and identity binding, without production origin."""
from copy import deepcopy

from datetime import datetime

from pathlib import PurePosixPath

import re

from . import catalog_io as io, catalog_rating as rating

from .authoring_package import require, sha

from .contract import canonical_bytes, digest, exact_keys, integer, InvalidInput

def decision(value):
    from . import reveal_source as at
    exact_keys(value, {"actor", "timestamp_utc", "statement"})
    at.text(value["actor"], 128)
    at.text(value["statement"], 4096)
    require(isinstance(value["timestamp_utc"], str) and
            re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", value["timestamp_utc"]),
            "Invalid manual image decision UTC timestamp")
    try:
        datetime.strptime(value["timestamp_utc"], "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise InvalidInput("Invalid manual image decision UTC timestamp") from exc
    return value

def manual_notice(prefix, provenance, declaration):
    """Append exactly the published PE-A2 attribution block, with no new date."""
    from . import reveal_source as at
    at.provenance(provenance)
    decision(declaration)
    if isinstance(prefix, str):
        prefix = prefix.encode("utf-8")
    require(isinstance(prefix, bytes), "Manual notice prefix must be UTF-8 bytes")
    if prefix:
        at.make_notice(prefix)
    lines = ["Manuelle Bildpflege (PE-A2)"]
    lines += [key + ": " + provenance[key] for key in ("author", "usage_basis", "source", "changes")]
    lines += [key + ": " + declaration[key] for key in ("actor", "timestamp_utc", "statement")]
    raw = prefix + (b"\n" if prefix else b"") + ("\n".join(lines) + "\n").encode("utf-8")
    at.make_notice(raw)
    return raw

def reveal_candidates(entry):
    stem = PurePosixPath("game/" + entry["reveal"]).with_suffix("")
    return {str(stem) + ".png", str(stem) + ".svg"}
