"""PE-A2 current image authority over an immutable production origin.

These functions validate or derive data; they never publish files, authenticate
an actor, transform an image, or manufacture a production approval. Historical
source generations retain their own validators and are never recursive bases.
"""
from copy import deepcopy
from datetime import datetime
from pathlib import PurePosixPath
import re

from . import catalog_io as io, catalog_rating as rating
from .authoring_package import require, sha
from .contract import canonical_bytes, digest, exact_keys, integer, InvalidInput

REVEAL_FORMAT = "picross-catalog-reveal-v3"
BACKGROUND_FORMAT = "picross-catalog-background-v5"
RECEIPT_FORMAT = "picross-integrated-content-v3"
FORMATS = (REVEAL_FORMAT, BACKGROUND_FORMAT)
LIMIT = 1024 * 1024
IMAGE_LIMIT = 32 * 1024 * 1024
NOTICE_LIMIT = 65536
FIELDS = {"format", "id", "record_revision", "origin", "binding", "current", "record_hash"}


def is_editor(value):
    return isinstance(value, dict) and value.get("format") in FORMATS


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


def reveal_path(entry, record=None):
    """Resource-relative effective path; historical production stays untouched."""
    return (record["current"]["asset"]["file"].removeprefix("game/")
            if is_editor(record) and record["format"] == REVEAL_FORMAT else entry["reveal"])


def _asset(value, entry):
    from . import catalog_background as bg
    bg._ref(value, limit=IMAGE_LIMIT)
    integer(value["bytes"], 1, IMAGE_LIMIT, "image bytes")
    require(value["file"] in reveal_candidates(entry), "Reveal asset leaves its technical stem or format")
    return value


def validate_binding(value, identifier=None):
    from .content_registry import validate_entries
    from . import catalog_background as bg
    exact_keys(value, {"entry", "identity"})
    entry = value["entry"]
    validate_entries([entry])
    require(identifier is None or entry["id"] == identifier, "Image binding changes puzzle ID")
    ident = exact_keys(value["identity"], {"key", "save_slot", "definition", "runtime_revision"})
    require(all(ident[key] == entry[key] for key in ("key", "save_slot")), "Image binding changes stable identity")
    bg._ref(ident["definition"], name="game/" + entry["definition"], limit=2 * LIMIT)
    integer(ident["definition"]["bytes"], 1, 2 * LIMIT, "definition bytes")
    require(ident["definition"]["sha256"] == entry["production"]["definition_sha256"],
            "Image binding definition hash differs")
    integer(ident["runtime_revision"], 1, 1000000, "image binding runtime revision")
    return value


def _same_identity(first, later):
    a, b = first["entry"], later["entry"]
    require(all(a[key] == b[key] for key in ("id", "key", "save_slot", "definition", "visible")) and
            a["production"]["test_only"] == b["production"]["test_only"] and
            reveal_candidates(a) == reveal_candidates(b), "Image source changes fixed production identity")
    require(later["identity"]["runtime_revision"] >= first["identity"]["runtime_revision"],
            "Image source decreases its runtime revision")
    if a == b:
        require(first["identity"] == later["identity"], "Unchanged production has another definition identity")
    else:
        require(a["production"]["package"] != b["production"]["package"] and
                later["identity"]["runtime_revision"] > first["identity"]["runtime_revision"],
                "Changed production requires a new package and runtime revision")


def _origin(value, catalog):
    from . import reveal_source as at, catalog_background as bg
    origin = exact_keys(value["origin"], {"entry", "identity", "notice", "source"})
    anchor = {key: origin[key] for key in ("entry", "identity")}
    validate_binding(anchor, value["id"])
    source = origin["source"]
    if origin["notice"] is not None:
        at.notice(origin["notice"])
    if value["format"] == REVEAL_FORMAT:
        require(origin["notice"] is not None, "Reveal origin requires its actual notice")
        if source is not None:
            require(isinstance(source, dict) and source.get("format") in (at.FORMAT, at.BACKGROUND_FORMAT),
                    "Reveal origin must be an unchanged old source, never another editor wrapper")
            at.validate(source, catalog, historical_categories=True)
            binding = source["bindings"][-1]
            require(source["id"] == value["id"] and binding["entry"] == origin["entry"] and
                    binding["runtime_revision"] == origin["identity"]["runtime_revision"] and
                    source["revisions"][-1]["notice"] == origin["notice"],
                    "Reveal origin differs from its preserved source")
    elif source is None:
        require(origin["notice"] is None, "Source-free background origin cannot invent a notice")
    else:
        require(isinstance(source, dict) and source.get("format") in (bg.FORMAT, bg.CHANGE_FORMAT, *bg.REBIND_FORMATS),
                "Background origin must be an unchanged old source, never another editor wrapper")
        bg.validate(source, origin["entry"])
        expected_hash = (source["events"][-1]["binding"]["entry"]["production"]["package_sha256"]
                         if source["format"] in bg.REBIND_FORMATS else bg.initial(source)["origin"]["export_manifest_sha256"])
        require(origin["entry"]["production"]["package_sha256"] == expected_hash,
                "Background origin loses its normalized export anchor")
        require(bg.effective(source)["identity"] == origin["identity"], "Background origin identity differs")
        active = bg.current(source)
        if active["notice"] is None:
            require(origin["notice"] is None, "Image-free background origin has a notice")
        else:
            require(origin["notice"] is not None, "Background origin loses its attribution")
            bg._bound(active["notice"], origin["notice"]["text"].encode("utf-8"), limit=NOTICE_LIMIT)
    return anchor


def _old_image_revision(source):
    from . import catalog_background as bg
    if source is None:
        return 0
    if source["format"] in (REVEAL_FORMAT, BACKGROUND_FORMAT, "picross-catalog-reveal-v1", "picross-catalog-reveal-v2"):
        return source["current"]["image_revision"]
    return bg.current(source)["image_revision"]


def _manual(authority, provenance, *, image):
    from . import reveal_source as at
    exact_keys(authority, {"kind", "decision", "provenance"})
    require(authority["kind"] == "manual", "Unknown manual image authority")
    decision(authority["decision"])
    if image:
        at.provenance(authority["provenance"])
    else:
        require(authority["provenance"] is None, "Image-free decision cannot carry file provenance")
    require(authority["provenance"] == provenance, "Manual image provenance differs")


def validate_context(context, entry):
    from . import catalog_background as bg, reveal_source as at
    exact_keys(context, {"source", "production", "reveal"})
    require((context["source"] is None) != (context["production"] is None),
            "Reveal context requires exactly one actual authority")
    if context["source"] is not None:
        bg._ref(context["source"], name=at.path(entry["id"]), limit=LIMIT)
        integer(context["source"]["bytes"], 1, LIMIT, "reveal source bytes")
    else:
        validate_binding(context["production"], entry["id"])
    _asset(context["reveal"], entry)
    if context["production"] is not None:
        production = context["production"]["entry"]
        require(all(production[key] == entry[key] for key in ("id", "key", "save_slot", "definition", "visible")) and
                production["production"]["test_only"] == entry["production"]["test_only"] and
                reveal_candidates(production) == reveal_candidates(entry) and
                context["reveal"]["file"] == "game/" + production["reveal"] and
                context["reveal"]["sha256"] == production["production"]["reveal_sha256"],
                "Source-free reveal context differs from its real production")
    return context


def _production_background(value):
    from . import catalog_background as bg, background_contract as bc, background_package as bp
    current, entry = value["current"], value["binding"]["entry"]
    authority = exact_keys(current["authority"], {"kind", "candidate_revision", "decision", "derivation",
                                                "provenance", "review", "adoption"})
    require(authority["kind"] == "production", "Unknown background production authority")
    if preserved_background(value):
        # A new compatible binding may carry an actual old production image.
        # Its original proof has already passed the closed old validator in
        # _origin. No new adoption, context, candidate or image revision exists.
        return
    adoption = exact_keys(authority["adoption"], {"request", "revision", "target", "background", "authorization", "context"})
    bc._revision(adoption["revision"])
    directory = "content/authoring/" + value["id"] + "/" + adoption["revision"]
    bg._ref(adoption["request"], name=directory + "/record.json", limit=bc.MAX_JSON)
    target = exact_keys(adoption["target"], {"source", "origin_sha256", "image_revision"})
    bg._ref(target["source"], name=bg.path(value["id"]), limit=LIMIT)
    initial = value["origin"]["source"]
    first_target = ({"source": bg.ref(bg.path(value["id"]), bg.encoded(initial)),
                     "origin_sha256": bg.origin_hash(initial), "image_revision": _old_image_revision(initial)}
                    if initial is not None else None)
    if first_target is not None and target["source"] == first_target["source"]:
        require(target == first_target, "First background adoption changes its actual old target")
    else:
        require(sha(target["origin_sha256"]) == digest(value["origin"]), "Background adoption changes editor origin")
    integer(target["image_revision"], 1, 999999, "previous background revision")
    require(current["image_revision"] == target["image_revision"] + 1, "Background adoption revision differs")
    binding = bp.validate_binding(adoption["background"], package_only=False)
    require(binding["history"] is None, "Background adoption cannot retrieve discarded history")
    for key in ("manifest", "decision", "derivation"):
        stored = binding[key]
        require(stored is not None and stored["storage"] == "external" and
                bp._join(stored["root"], stored["ref"]["file"]).startswith(directory + "/"),
                "Background adoption reference leaves its authoring revision")
    bc._human(adoption["authorization"])
    validate_context(adoption["context"], entry)
    active = {key: current[key] for key in ("image_revision", "asset", "notice")}
    active.update({key: authority[key] for key in ("candidate_revision", "decision", "derivation", "provenance", "review")})
    selected = bc.validate_decision(authority["decision"])
    require(current["status"] == selected["outcome"], "Background status differs from production decision")
    derivation = authority["derivation"]
    require(isinstance(derivation, dict), "Missing background derivation")
    approved = {**{key: binding[key] for key in ("manifest", "decision", "derivation")},
                "outcome": selected["outcome"], "candidate_id": selected["candidate_id"],
                "original": selected["original"], "output": derivation.get("output"),
                "profile_sha256": derivation.get("profile_sha256")}
    bg._active(active, entry, approved, entry["production"]["test_only"])
    for key in ("decision", "derivation"):
        require(binding[key]["ref"] == bg.ref(binding[key]["ref"]["file"], bg.encoded(authority[key])),
                "Background adoption " + key + " differs from its retained bytes")
    if current["status"] == "selected":
        candidate = {"id": selected["candidate_id"], "revision": authority["candidate_revision"], "provenance": authority["provenance"]}
        bg._bound(current["notice"], bg.notice_bytes(value["id"], candidate), name=bg.notice_path(value["id"]), limit=NOTICE_LIMIT)


def validate(value, catalog=None):
    """Validate a complete source without requiring its new live files yet."""
    from . import catalog_background as bg, background_contract as bc, reveal_source as at
    try:
        bc._json_tree(value)
        exact_keys(value, FIELDS)
        require(value["format"] in FORMATS, "Unsupported editor image source")
        rating.identity(value["id"])
        integer(value["record_revision"], 1, 1000000, "image record revision")
        anchor = _origin(value, catalog)
        binding = validate_binding(value["binding"], value["id"])
        _same_identity(anchor, binding)
        current = value["current"]
        integer(current.get("image_revision") if isinstance(current, dict) else None, 1, 1000000, "active image revision")
        old = value["origin"]["source"]
        old_revision = _old_image_revision(old)
        retained_production = value["format"] == BACKGROUND_FORMAT and preserved_background(value)
        require((current["image_revision"] > old_revision or retained_production) and
                value["record_revision"] > max(old.get("record_revision", 0) if old else 0, old_revision) and
                value["record_revision"] >= current["image_revision"], "Editor image revision resets its origin")
        if value["format"] == REVEAL_FORMAT:
            exact_keys(current, {"image_revision", "asset", "notice", "provenance", "authority"})
            _asset(current["asset"], binding["entry"])
            at.notice(current["notice"])
            at.provenance(current["provenance"])
            require(current["notice"]["text"].startswith(value["origin"]["notice"]["text"]), "Reveal notice removes origin attribution")
            authority = current["authority"]
            require(isinstance(authority, dict), "Missing reveal decision authority")
            if authority.get("kind") == "manual":
                _manual(authority, current["provenance"], image=True)
                block = manual_notice(b"", authority["provenance"], authority["decision"])
                require(current["notice"]["text"].encode("utf-8").endswith(block), "Manual reveal notice differs from its decision")
            else:
                exact_keys(authority, {"kind", "approval", "binding"})
                require(authority["kind"] == "production", "Unknown reveal authority")
                approved_binding = validate_binding(authority["binding"], value["id"])
                _same_identity(anchor, approved_binding)
                _same_identity(approved_binding, binding)
                approval = authority["approval"]
                require(isinstance(approval, dict), "Missing actual reveal approval")
                at.approval(approval, approved_binding["entry"], current["image_revision"],
                            sha(approval.get("previous_reveal_sha256")), current["asset"]["sha256"], current["notice"]["sha256"])
                require(approval["previous_reveal_sha256"] != current["asset"]["sha256"], "Production reveal does not replace an image")
        else:
            exact_keys(current, {"image_revision", "status", "asset", "notice", "authority"})
            require(current["status"] in ("standard", "selected", "none"), "Unknown editor background preference")
            selected = current["status"] == "selected"
            if selected:
                bg._ref(current["asset"], name=bg.asset_path(value["id"]), limit=IMAGE_LIMIT)
                integer(current["asset"]["bytes"], 1, IMAGE_LIMIT, "background image bytes")
                bg._ref(current["notice"], name=bg.notice_path(value["id"]), limit=NOTICE_LIMIT)
                integer(current["notice"]["bytes"], 1, NOTICE_LIMIT, "background notice bytes")
            else:
                require(current["asset"] is None and current["notice"] is None, "Image-free background carries a file")
            authority = current["authority"]
            require(isinstance(authority, dict), "Missing background decision authority")
            if authority.get("kind") == "manual":
                _manual(authority, authority.get("provenance"), image=selected)
            else:
                require(current["status"] != "standard", "Production cannot manufacture a Standard preference")
                _production_background(value)
        require(sha(value["record_hash"]) == digest({key: item for key, item in value.items() if key != "record_hash"}),
                "Editor image record hash differs")
        require(len(canonical_bytes(value)) + 1 <= LIMIT, "Editor image source exceeds 1 MiB")
        return value
    except bc.BackgroundError as exc:
        raise InvalidInput("Editor image source: " + str(exc)) from exc


def _hashed(value, catalog=None):
    value.pop("record_hash", None)
    value["record_hash"] = digest(value)
    return validate(value, catalog)


def make_binding(root, entry):
    from . import reveal_source as at, catalog_background as bg
    original = at.normalized(root, entry)
    raw = io.read(root, "game/" + entry["definition"], 2 * LIMIT)
    definition = io.json_bytes(raw, 2 * LIMIT)
    require(definition.get("id") == entry["id"], "Image definition ID differs")
    return validate_binding({"entry": original,
        "identity": {"key": entry["key"], "save_slot": entry["save_slot"],
                     "definition": bg.ref("game/" + entry["definition"], raw), "runtime_revision": definition.get("revision")}}, entry["id"])


def _new_source(kind, entry, binding, old, notice):
    if is_editor(old):
        result = deepcopy(old)
    else:
        result = {"format": kind, "id": entry["id"], "record_revision": max(old.get("record_revision", 0) if old else 0,
                    _old_image_revision(old)), "origin": {**deepcopy(binding), "notice": deepcopy(notice), "source": deepcopy(old)},
                  "binding": deepcopy(binding)}
    require(result["format"] == kind, "Image source kind changes")
    result["record_revision"] += 1
    return result


def manual_reveal(root, entry, catalog, asset, provenance, declaration):
    from . import reveal_source as at, catalog_background as bg
    _asset(asset, entry)
    at.provenance(provenance)
    decision(declaration)
    resolved = at.resolve(root, entry, catalog)
    old = at.load(root, entry, catalog)
    name = resolved.get("effective_reveal", entry["reveal"])
    raw = io.read(root, "game/" + name, IMAGE_LIMIT)
    current_asset = bg.ref("game/" + name, raw)
    old_provenance = (old["current"]["provenance"] if is_editor(old) else
                      old["revisions"][-1]["provenance"] if old else None)
    if asset == current_asset and provenance == old_provenance:
        return deepcopy(old)
    original_notice = at.make_notice(io.read(root, at.identity(entry)["notice"], NOTICE_LIMIT))
    result = _new_source(REVEAL_FORMAT, entry, make_binding(root, entry), old, original_notice)
    result["current"] = {"image_revision": _old_image_revision(old) + 1, "asset": deepcopy(asset),
        "notice": at.make_notice(manual_notice(original_notice["text"], provenance, declaration)),
        "provenance": deepcopy(provenance),
        "authority": {"kind": "manual", "decision": deepcopy(declaration), "provenance": deepcopy(provenance)}}
    return _hashed(result, catalog)


def manual_background(root, registry, entry, status, asset, provenance, declaration):
    from . import catalog_background as bg, reveal_source as at
    require(status in ("standard", "selected", "none"), "Unknown background preference")
    decision(declaration)
    if status == "selected":
        bg._ref(asset, name=bg.asset_path(entry["id"]), limit=IMAGE_LIMIT)
        integer(asset["bytes"], 1, IMAGE_LIMIT, "background image bytes")
        at.provenance(provenance)
    else:
        require(asset is None and provenance is None, "Image-free preference cannot carry image input")
    old = bg.load(root, registry, entry)
    active = bg.current(old) if old is not None else None
    old_status = (active["status"] if is_editor(old) else active["decision"]["outcome"]) if old else "legacy"
    old_provenance = (active["authority"].get("provenance") if is_editor(old) else active["provenance"]) if old else None
    if active is not None and old_status == status and active["asset"] == asset and old_provenance == provenance:
        return deepcopy(old)
    previous_notice = io.read(root, bg.notice_path(entry["id"]), NOTICE_LIMIT, missing=True)
    original_notice = at.make_notice(previous_notice) if previous_notice is not None else None
    result = _new_source(BACKGROUND_FORMAT, entry, make_binding(root, entry), old, original_notice)
    prefix = previous_notice if previous_notice is not None else (
        result["origin"]["notice"]["text"].encode("utf-8") if result["origin"]["notice"] is not None else b"")
    raw = manual_notice(prefix, provenance, declaration) if status == "selected" else None
    result["current"] = {"image_revision": _old_image_revision(old) + 1, "status": status, "asset": deepcopy(asset),
        "notice": bg.ref(bg.notice_path(entry["id"]), raw) if raw is not None else None,
        "authority": {"kind": "manual", "decision": deepcopy(declaration), "provenance": deepcopy(provenance)}}
    return _hashed(result)


def preserved_background(value):
    """Only the exact already validated old HP image may omit a new context."""
    from . import catalog_background as bg
    if value.get("format") != BACKGROUND_FORMAT:
        return False
    old = value.get("origin", {}).get("source")
    current = value.get("current")
    if not isinstance(old, dict) or old.get("format") not in (bg.FORMAT, bg.CHANGE_FORMAT, *bg.REBIND_FORMATS) or not isinstance(current, dict):
        return False
    previous = bg.current(old)
    expected = {key: deepcopy(previous[key]) for key in ("image_revision", "asset", "notice")}
    expected["status"] = previous["decision"]["outcome"]
    expected["authority"] = {"kind": "production", **{key: deepcopy(previous[key]) for key in
        ("candidate_revision", "decision", "derivation", "provenance", "review")},
        "adoption": deepcopy(previous.get("adoption"))}
    return current == expected


def promote_background(root, registry, entry, new_entry, definition_ref, runtime_revision, *, manual_raster=False):
    """Rebind an existing HP image alongside an explicit editor reveal authority.

    This operation preserves the image and genuine old proofs. It is not a
    manual background selection or a new HP-W2 adoption.
    """
    from . import catalog_background as bg, reveal_source as at, categories
    old = bg.load(root, registry, entry)
    require(old is not None, "Cannot promote a source-free background")
    if old["format"] == BACKGROUND_FORMAT:
        return rebind(old, new_entry, definition_ref, runtime_revision)
    record = at.load(root, entry, categories.load(root / categories.PATH))
    require(manual_raster or record is not None and record["format"] == REVEAL_FORMAT,
            "Productive background promotion requires an actual current editor reveal")
    active = bg.current(old)
    raw = io.read(root, bg.notice_path(entry["id"]), NOTICE_LIMIT, missing=True)
    notice = at.make_notice(raw) if raw is not None else None
    result = _new_source(BACKGROUND_FORMAT, entry, make_binding(root, entry), old, notice)
    result["binding"] = validate_binding({"entry": deepcopy(new_entry), "identity": {
        "key": new_entry["key"], "save_slot": new_entry["save_slot"], "definition": deepcopy(definition_ref),
        "runtime_revision": runtime_revision}}, entry["id"])
    result["current"] = {key: deepcopy(active[key]) for key in ("image_revision", "asset", "notice")}
    result["current"]["status"] = active["decision"]["outcome"]
    result["current"]["authority"] = {"kind": "production", **{key: deepcopy(active[key]) for key in
        ("candidate_revision", "decision", "derivation", "provenance", "review")},
        "adoption": deepcopy(active.get("adoption"))}
    return _hashed(result)


def rebind(value, entry, definition_ref, runtime_revision, catalog=None):
    """Advance only the current raster binding; retain the actual image decision."""
    validate(value, catalog)
    new_binding = validate_binding({"entry": deepcopy(entry), "identity": {
        "key": entry["key"], "save_slot": entry["save_slot"], "definition": deepcopy(definition_ref),
        "runtime_revision": runtime_revision}}, value["id"])
    if new_binding == value["binding"]:
        return deepcopy(value)
    _same_identity(value["binding"], new_binding)
    result = deepcopy(value)
    result["binding"] = new_binding
    result["record_revision"] += 1
    return _hashed(result, catalog)


def adopt_reveal(value, asset, notice, provenance, approval, catalog=None):
    from . import reveal_source as at
    validate(value, catalog)
    require(value["format"] == REVEAL_FORMAT, "Reveal adoption requires a reveal source")
    old = value["current"]
    if isinstance(notice, bytes):
        notice = at.make_notice(notice)
    at.notice(notice)
    require(notice["text"].startswith(old["notice"]["text"]), "Reveal adoption removes attribution")
    at.approval(approval, value["binding"]["entry"], old["image_revision"] + 1,
                old["asset"]["sha256"], asset["sha256"], notice["sha256"])
    result = deepcopy(value)
    result["record_revision"] += 1
    result["current"] = {"image_revision": old["image_revision"] + 1, "asset": deepcopy(asset),
        "notice": deepcopy(notice), "provenance": deepcopy(provenance),
        "authority": {"kind": "production", "approval": deepcopy(approval), "binding": deepcopy(value["binding"])}}
    return _hashed(result, catalog)


def adopt_background(value, current, catalog=None):
    """Retain verified HP-W2/HP-I1b2 fields, never relabel them as manual."""
    from . import catalog_background as bg
    validate(value, catalog)
    require(value["format"] == BACKGROUND_FORMAT, "Background adoption requires a background source")
    exact_keys(current, set(bg.IMAGE_FIELDS) | {"adoption"})
    require(current["adoption"]["target"] == {"source": bg.ref(bg.path(value["id"]), bg.encoded(value)),
            "origin_sha256": digest(value["origin"]), "image_revision": value["current"]["image_revision"]},
            "Background adoption does not bind the immediately previous source")
    require(current["image_revision"] == value["current"]["image_revision"] + 1,
            "Background adoption must advance exactly one image revision")
    require(not (value["current"]["status"] == current["decision"]["outcome"] == "none"),
            "Unchanged none cannot create another image revision")
    result = deepcopy(value)
    result["record_revision"] += 1
    result["current"] = {key: deepcopy(current[key]) for key in ("image_revision", "asset", "notice")}
    result["current"]["status"] = current["decision"]["outcome"]
    result["current"]["authority"] = {"kind": "production", **{key: deepcopy(current[key]) for key in
        ("candidate_revision", "decision", "derivation", "provenance", "review", "adoption")}}
    return _hashed(result, catalog)


def adopt_background_from_old(root, registry, entry, current):
    """First genuine v2 adoption targets the real old source, not a virtual v5."""
    from . import catalog_background as bg, reveal_source as at
    old = bg.load(root, registry, entry)
    require(old is not None and old["format"] != BACKGROUND_FORMAT,
            "First productive editor adoption requires a real old background source")
    exact_keys(current, set(bg.IMAGE_FIELDS) | {"adoption"})
    require(current["adoption"]["target"] == {"source": bg.ref(bg.path(entry["id"]), bg.encoded(old)),
            "origin_sha256": bg.origin_hash(old), "image_revision": _old_image_revision(old)} and
            current["image_revision"] == _old_image_revision(old) + 1,
            "First editor adoption does not bind the actual prior background")
    require(not (bg.current(old)["decision"]["outcome"] == current["decision"]["outcome"] == "none"),
            "Unchanged none cannot create another image revision")
    raw = io.read(root, bg.notice_path(entry["id"]), NOTICE_LIMIT, missing=True)
    notice = at.make_notice(raw) if raw is not None else None
    result = _new_source(BACKGROUND_FORMAT, entry, make_binding(root, entry), old, notice)
    result["current"] = {key: deepcopy(current[key]) for key in ("image_revision", "asset", "notice")}
    result["current"]["status"] = current["decision"]["outcome"]
    result["current"]["authority"] = {"kind": "production", **{key: deepcopy(current[key]) for key in
        ("candidate_revision", "decision", "derivation", "provenance", "review", "adoption")}}
    return _hashed(result)


def transition(old, new, *, operation):
    """Check immutable origin and exact one-step source progression."""
    validate(old)
    validate(new)
    require(old["format"] == new["format"] and old["id"] == new["id"] and old["origin"] == new["origin"],
            "Image transition changes its immutable origin")
    require(new["record_revision"] == old["record_revision"] + 1, "Image transition skips a record revision")
    if operation == "update":
        require(new["current"] == old["current"] and new["binding"] != old["binding"],
                "Raster rebind changes the active image authority")
        _same_identity(old["binding"], new["binding"])
    else:
        require(operation in ("editor-images", "reveal-adoption", "background-adoption") and
                new["binding"] == old["binding"] and
                new["current"]["image_revision"] == old["current"]["image_revision"] + 1,
                "Image transition changes production or skips an image revision")
        expected = "manual" if operation == "editor-images" else "production"
        require(new["current"]["authority"]["kind"] == expected, "Image transition mislabels its real authority")
        if operation == "reveal-adoption":
            from . import reveal_source as at
            require(new["format"] == REVEAL_FORMAT and new["current"]["authority"]["binding"] == old["binding"],
                    "Reveal adoption changes its actual approval context")
            previous, current = old["current"], new["current"]
            at.approval(current["authority"]["approval"], old["binding"]["entry"], current["image_revision"],
                        previous["asset"]["sha256"], current["asset"]["sha256"], current["notice"]["sha256"])
            require(current["notice"]["text"].startswith(previous["notice"]["text"]), "Reveal adoption removes prior attribution")
        elif operation == "background-adoption":
            from . import catalog_background as bg
            require(new["format"] == BACKGROUND_FORMAT and new["current"]["authority"]["adoption"]["target"] == {
                "source": bg.ref(bg.path(old["id"]), bg.encoded(old)), "origin_sha256": digest(old["origin"]),
                "image_revision": old["current"]["image_revision"]}, "Background adoption changes its actual predecessor")
            require(not (old["current"]["status"] == new["current"]["status"] == "none"),
                    "Unchanged none cannot create another image revision")
        elif new["format"] == REVEAL_FORMAT:
            previous, current = old["current"], new["current"]
            require((previous["asset"], previous["provenance"]) != (current["asset"], current["provenance"]),
                    "Unchanged reveal cannot create another manual image revision")
            require(current["notice"]["text"].encode("utf-8") == manual_notice(previous["notice"]["text"],
                    current["provenance"], current["authority"]["decision"]), "Manual reveal notice is not the exact authorized append")
        else:
            previous, current = old["current"], new["current"]
            require((previous["status"], previous["asset"], previous["authority"].get("provenance")) !=
                    (current["status"], current["asset"], current["authority"]["provenance"]),
                    "Unchanged background cannot create another manual image revision")
    return new
