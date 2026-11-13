"""Bounded, nonrecursive HP-I1c chronology; old source generations stay closed."""
from copy import deepcopy

from . import catalog_background as bg, catalog_io as io, reveal_source as at
from .authoring_package import require
from .contract import exact_keys, integer, canonical_bytes

FORMAT = "picross-catalog-background-v3"
METADATA_FORMAT = "picross-catalog-background-v4"
UPDATE = "picross-content-update-journal-v7"
REVEAL = "picross-reveal-adoption-journal-v4"
BACKGROUND = "picross-background-adoption-journal-v2"


def is_rebound(source):
    return isinstance(source, dict) and source.get("format") in (FORMAT, METADATA_FORMAT)


def entry_shape(value):
    # Only structural entry validation. Category labels are not authority here;
    # the live registry separately validates actual category membership.
    from .content_registry import validate_entries
    require(isinstance(value, dict) and isinstance(value.get("category_id"), str), "Invalid rebound entry")
    validate_entries([value])
    return value


def normalized(source):
    if source.get("format") == bg.EDITOR_FORMAT:
        return source["binding"]["entry"]
    return source["events"][-1]["binding"]["entry"]


def image(source):
    return next((event["image"] for event in reversed(source["events"]) if event["image"] is not None),
                bg.current(source["base"]))


def reveal_hash(source):
    return (source["events"][-1]["binding"]["reveal"]["sha256"] if is_rebound(source) else
            bg.initial(source)["origin"]["approval"]["selection"]["reveal"]["sha256"])


def pointer(record):
    return {**record["current"], "record_hash": record["record_hash"]} if record is not None else None


def prefix(record, value):
    exact_keys(value, {"binding_revision", "image_revision", "record_hash"})
    b = integer(value["binding_revision"], 1, 256, "AT binding prefix")
    r = integer(value["image_revision"], 1, 256, "AT image prefix")
    require(record is not None and b <= len(record["bindings"]) and r <= len(record["revisions"]),
            "Missing background AT prefix")
    result = deepcopy(record)
    result["bindings"] = result["bindings"][:b]
    result["revisions"] = result["revisions"][:r]
    result["current"] = {"binding_revision": b, "image_revision": r}
    result["record_revision"] = b + r - 1
    result.pop("record_hash")
    result = at.hashed(result, "record_hash")
    require(result["record_hash"] == value["record_hash"], "Background AT prefix hash differs")
    return result


def binding(root, source, entry, definition, reveal_raw, notice_raw, record):
    stable = deepcopy(entry)
    if is_rebound(source) and stable["production"]["package"] == normalized(source)["production"]["package"]:
        stable["production"]["package_sha256"] = normalized(source)["production"]["package_sha256"]
    elif stable["production"]["package"] == bg.initial(source)["origin"]["package"]:
        stable["production"]["package_sha256"] = bg.initial(source)["origin"]["export_manifest_sha256"]
    return {"entry": stable,
            "identity": {"key": entry["key"], "save_slot": entry["save_slot"],
                         "definition": bg.ref("game/" + entry["definition"], definition),
                         "runtime_revision": io.json_bytes(definition, 2 * bg.LIMIT)["revision"]},
            "reveal": bg.ref("game/" + entry["reveal"], reveal_raw),
            "notice": bg.ref(at.identity(entry)["notice"], notice_raw), "at": pointer(record)}


def append(source, original_entry, value, operation, *, image=None, export_source=None):
    if is_rebound(source):
        result = deepcopy(source)
    else:
        original_entry = deepcopy(original_entry)
        original_entry["production"]["package_sha256"] = bg.initial(source)["origin"]["export_manifest_sha256"]
        result = {"format": FORMAT, "base": deepcopy(source), "entry": original_entry, "events": []}
    if value["entry"]["category_id"] != original_entry["category_id"]:
        require(operation == "update", "Only a new production may change its historical category")
        result["format"] = METADATA_FORMAT
    result["events"].append({"operation": operation,
        "previous_source": bg.ref(bg.path(original_entry["id"]), bg.encoded(source)),
        "binding": deepcopy(value), "image": deepcopy(image), "export_source": deepcopy(export_source)})
    return validate(result, value["entry"])


def validate(value, entry):
    exact_keys(value, {"format", "base", "entry", "events"})
    require(value["format"] in (FORMAT, METADATA_FORMAT) and isinstance(value["base"], dict) and
            value["base"].get("format") in (bg.FORMAT, bg.CHANGE_FORMAT), "Invalid background rebind base")
    origin_entry = entry_shape(value["entry"])
    base = bg.validate(value["base"], origin_entry)
    require(origin_entry["production"]["package_sha256"] == bg.initial(base)["origin"]["export_manifest_sha256"],
            "Background base export anchor differs")
    events = value["events"]
    require(isinstance(events, list) and 1 <= len(events) <= 256, "Background rebind needs 1..256 events")
    previous_source = base
    previous_entry = origin_entry
    previous_identity = bg.initial(base)["identity"]
    previous_reveal = origin_entry["production"]["reveal_sha256"]
    previous_notice, previous_at = None, None
    active = bg.current(base)
    packages = {origin_entry["production"]["package"]}
    category_changed = False
    for index, event in enumerate(events):
        exact_keys(event, {"operation", "previous_source", "binding", "image", "export_source"})
        require(event["previous_source"] == bg.ref(bg.path(entry["id"]), bg.encoded(previous_source)),
                "Background rebind predecessor differs")
        b = exact_keys(event["binding"], {"entry", "identity", "reveal", "notice", "at"})
        e = entry_shape(b["entry"])
        require(e["production"]["package"] == "content/packages/" + e["id"] + "/" + e["production"]["revision"],
                "Rebound package path differs")
        fixed = ("id", "key", "save_slot", "definition", "reveal", "visible") + (() if value["format"] == METADATA_FORMAT else ("category_id",))
        require(all(e[k] == origin_entry[k] == entry[k] for k in fixed) and
                e["production"]["test_only"] == origin_entry["production"]["test_only"] == entry["production"]["test_only"],
                "Background rebind changes fixed identity")
        ident = exact_keys(b["identity"], {"key", "save_slot", "definition", "runtime_revision"})
        require(all(ident[k] == e[k] for k in ("key", "save_slot")), "Background rebound identity differs")
        bg._ref(ident["definition"], name="game/" + e["definition"], limit=2 * bg.LIMIT)
        require(ident["definition"]["sha256"] == e["production"]["definition_sha256"], "Rebound definition differs")
        integer(ident["runtime_revision"], 1, 1000000, "rebound runtime revision")
        bg._ref(b["reveal"], name="game/" + e["reveal"], limit=at.IMAGE_LIMIT)
        bg._ref(b["notice"], name=at.identity(e)["notice"], limit=65536)
        if b["at"] is not None:
            exact_keys(b["at"], {"binding_revision", "image_revision", "record_hash"})
            for key in ("binding_revision", "image_revision"): integer(b["at"][key], 1, 256, key)
            at.sha(b["at"]["record_hash"])
        op = event["operation"]
        if op == "update":
            require(ident["runtime_revision"] > previous_identity["runtime_revision"] and
                    e["production"]["package"] not in packages and
                    e["production"]["reveal_sha256"] == b["reveal"]["sha256"] == previous_reveal,
                    "Invalid background raster rebind")
            packages.add(e["production"]["package"])
            require((b["at"] is None if previous_at is None else b["at"] is not None and
                    b["at"]["binding_revision"] == previous_at["binding_revision"] + 1 and
                    b["at"]["image_revision"] == previous_at["image_revision"] and b["notice"] == previous_notice),
                    "Raster rebind changes AT chronology")
            require(event["image"] is None, "Raster update changes background image")
            if event["export_source"] is not None:
                exported = bg._validate_v1(event["export_source"], e)
                require(exported["origin"]["export_manifest_sha256"] == e["production"]["package_sha256"] and
                        exported["identity"] == ident and all(exported[k] == active[k] for k in bg.IMAGE_FIELDS
                                                            if k != "image_revision"),
                        "v6 raster export changes active background decision")
            category_changed = category_changed or e["category_id"] != previous_entry["category_id"]
        elif op in ("reveal-adoption", "background-adoption"):
            require(e == previous_entry and ident == previous_identity and event["export_source"] is None,
                    "Image operation changes raster production")
            if op == "reveal-adoption":
                require(b["reveal"]["sha256"] != previous_reveal and event["image"] is None and
                        b["at"] is not None and b["at"]["binding_revision"] ==
                        (previous_at["binding_revision"] if previous_at else 1) and
                        b["at"]["image_revision"] == (previous_at["image_revision"] + 1 if previous_at else 1),
                        "Invalid background reveal rebind")
            else:
                require(index > 0 and b == events[index - 1]["binding"], "Background change resets effective binding")
                new = event["image"]
                bg.validate_image(new, bg.initial(base), e, rebound=True)
                require(new["adoption"]["target"] == {"source": event["previous_source"],
                        "origin_sha256": bg.origin_hash(base), "image_revision": active["image_revision"]} and
                        new["image_revision"] == active["image_revision"] + 1,
                        "Background image chronology differs")
                require(not (new["decision"]["outcome"] == active["decision"]["outcome"] == "none"),
                        "Unchanged none cannot create an image revision")
                require(any(new[k] != active[k] for k in bg.IMAGE_FIELDS if k != "image_revision"),
                        "Background change has no new active binding")
                active = new
        else:
            require(False, "Unknown background rebind operation")
        previous_entry, previous_identity = e, ident
        previous_reveal, previous_notice, previous_at = b["reveal"]["sha256"], b["notice"], b["at"]
        # Existing v3 predecessor refs remain byte-for-byte valid when the
        # first category-changing update creates v4. Never rehash old events.
        previous_source = {**value, "format": METADATA_FORMAT if category_changed else FORMAT,
                           "events": events[:index + 1]}
    require(value["format"] != METADATA_FORMAT or category_changed,
            "Background source v4 requires a historical category transition")
    expected = deepcopy(entry)
    expected["production"]["package_sha256"] = previous_entry["production"]["package_sha256"]
    require(expected == previous_entry, "Current background production differs")
    require(len(bg.encoded(value)) <= bg.LIMIT, "Background source exceeds 1 MiB")
    return value


def live(root, source, entry, texts=None):
    """Check every AT prefix and the actual effective bytes, without old inputs."""
    from . import categories
    catalog = io.json_bytes(bg._raw(root, categories.PATH, 131072, texts), 131072)
    record_raw = bg._raw(root, at.path(entry["id"]), at.LIMIT, texts, missing=True)
    historical_categories = at.historical_categories(root, texts)
    record = at.validate(io.json_bytes(record_raw, at.LIMIT), catalog, historical_categories=historical_categories) if record_raw is not None else None
    editor_record = record if record is not None and record["format"] == at.EDITOR_FORMAT else None
    if editor_record is not None:
        require(record_raw == bg.encoded(editor_record), "Noncanonical editor reveal source")
        # The new explicit authority preserves the entire old AT object. Old
        # background prefixes remain historical facts, never invented new AT
        # revisions or requests to reopen a displaced live image.
        record = editor_record["origin"]["source"]
    if record is not None:
        require(record["format"] == at.BACKGROUND_FORMAT and
                (editor_record is not None or record_raw == bg.encoded(record)), "Wrong background AT source")
    last = source["events"][-1]["binding"]
    require(last["at"] == pointer(record), "Background effective AT pointer differs")
    for event in source["events"]:
        b = event["binding"]
        if b["at"] is None: continue
        history = at.validate(prefix(record, b["at"]), catalog, historical_categories=historical_categories)
        binding = history["bindings"][-1]
        revision = history["revisions"][-1]
        require(binding["entry"] == b["entry"] and binding["runtime_revision"] == b["identity"]["runtime_revision"] and
                revision["reveal_sha256"] == b["reveal"]["sha256"] and
                revision["notice"]["sha256"] == b["notice"]["sha256"],
                "Background historical AT binding differs")
    for key, limit in (("reveal", at.IMAGE_LIMIT), ("notice", 65536)):
        if editor_record is None:
            bg._bound(last[key], bg._raw(root, last[key]["file"], limit, texts), limit=limit)
    if editor_record is not None:
        origin = editor_record["origin"]
        require(origin["entry"] == last["entry"] and origin["identity"] == last["identity"],
                "Editor reveal origin differs from historical background binding")
        previous_hash = record["revisions"][-1]["reveal_sha256"] if record is not None else origin["entry"]["production"]["reveal_sha256"]
        require(last["reveal"]["sha256"] == previous_hash, "Editor reveal origin loses background reveal hash")
        bg._bound(last["notice"], origin["notice"]["text"].encode("utf-8"), limit=65536)
        active = editor_record["current"]
        bg._bound(active["asset"], bg._raw(root, active["asset"]["file"], at.IMAGE_LIMIT, texts), limit=at.IMAGE_LIMIT)
        bg._bound(bg.ref(at.identity(entry)["notice"], active["notice"]["text"].encode("utf-8")),
                  bg._raw(root, at.identity(entry)["notice"], 65536, texts), limit=65536)


def historical(root, source, texts=None):
    """Check preserved HP-I1c AT prefixes without treating them as live paths."""
    from . import categories
    require(is_rebound(source), "Historical background prefixes require a rebind source")
    catalog = io.json_bytes(bg._raw(root, categories.PATH, 131072, texts), 131072)
    identifier = normalized(source)["id"]
    raw = bg._raw(root, at.path(identifier), at.LIMIT, texts, missing=True)
    record = at.validate(io.json_bytes(raw, at.LIMIT), catalog, historical_categories=True) if raw is not None else None
    if record is not None:
        require(raw == bg.encoded(record), "Noncanonical current reveal source")
        if record["format"] == at.EDITOR_FORMAT:
            record = record["origin"]["source"]
        require(record is None or record["format"] == at.BACKGROUND_FORMAT, "Wrong historical background reveal source")
    for event in source["events"]:
        old = event["binding"]
        if old["at"] is None:
            continue
        history = at.validate(prefix(record, old["at"]), catalog, historical_categories=True)
        binding, image_revision = history["bindings"][-1], history["revisions"][-1]
        require(binding["entry"] == old["entry"] and
                binding["runtime_revision"] == old["identity"]["runtime_revision"] and
                image_revision["reveal_sha256"] == old["reveal"]["sha256"] and
                image_revision["notice"]["sha256"] == old["notice"]["sha256"],
                "Preserved background AT prefix differs")


def transition(old, new, old_entry, entry, operation):
    if old.get("format") == bg.EDITOR_FORMAT or new.get("format") == bg.EDITOR_FORMAT:
        from . import editor_image_source as editor
        require(new.get("format") == bg.EDITOR_FORMAT, "A production rebind cannot downgrade editor background authority")
        if old.get("format") == bg.EDITOR_FORMAT:
            editor.transition(old, new, operation=operation)
        else:
            require(operation in ("update", "reveal-adoption") and new["origin"]["source"] == old and
                    new["origin"]["identity"] == bg.effective(old)["identity"] and editor.preserved_background(new) and
                    new["record_revision"] == max(old.get("record_revision", 0), bg.current(old)["image_revision"]) + 1,
                    "Productive background promotion changes historical image authority")
            expected = deepcopy(old_entry)
            expected["production"]["package_sha256"] = (normalized(old)["production"]["package_sha256"] if is_rebound(old) else
                                                        bg.initial(old)["origin"]["export_manifest_sha256"])
            require(new["origin"]["entry"] == expected, "Productive background promotion changes normalized origin")
            if operation == "reveal-adoption":
                require(new["binding"] == {key: new["origin"][key] for key in ("entry", "identity")},
                        "Reveal rebind changes production definition")
        bg.validate(old, old_entry)
        bg.validate(new, entry)
        return
    require(is_rebound(new), "Operation requires background rebind source")
    if is_rebound(old):
        require(new["format"] == old["format"] or old["format"] == FORMAT and new["format"] == METADATA_FORMAT and
                operation == "update" and old_entry["category_id"] != entry["category_id"], "Invalid background source generation transition")
        require(new["base"] == old["base"] and new["entry"] == old["entry"] and
                new["events"][:-1] == old["events"], "Background rebind rewrites history")
    else:
        require(new["base"] == old and len(new["events"]) == 1, "Background rebind rewrites base")
        expected = deepcopy(old_entry)
        expected["production"]["package_sha256"] = bg.initial(old)["origin"]["export_manifest_sha256"]
        require(new["entry"] == expected, "Background rebind origin entry differs")
    require(new["events"][-1]["operation"] == operation and
            new["events"][-1]["previous_source"] == bg.ref(bg.path(entry["id"]), bg.encoded(old)),
            "Wrong background rebind operation")
    if operation != "background-adoption":
        require(bg.current(new) == bg.current(old), "Rebind changes current background decision")


def delta(j, before, after, identifiers):
    require(before["format"] == after["format"], "Rebind changes registry generation")
    old_index, new_index = bg.index(before), bg.index(after)
    require(old_index.keys() == new_index.keys(), "Rebind changes background IDs")
    require({i for i in old_index if old_index[i] != new_index[i]} == set(identifiers),
            "Rebind changes unrelated background source")
    mutable = set()
    for identifier in identifiers:
        a = next(e for e in before["entries"] if e["id"] == identifier)
        b = next(e for e in after["entries"] if e["id"] == identifier)
        old = bg._source(None, before, a, j["old"])
        new = bg._source(None, after, b, j["new"])
        if old["format"] == bg.EDITOR_FORMAT or new["format"] == bg.EDITOR_FORMAT:
            transition(old, new, a, b, j["operation"])
            if j["operation"] == "update":
                raw = j["new"]["game/" + b["definition"]]
                raw = raw.encode("utf-8") if isinstance(raw, str) else raw
                bg._bound(new["binding"]["identity"]["definition"], raw, limit=2 * bg.LIMIT)
                definition = io.json_bytes(raw, 2 * bg.LIMIT)
                require(definition["id"] == b["id"] and definition["revision"] == new["binding"]["identity"]["runtime_revision"],
                        "Editor background rebind differs from actual new definition")
            mutable.add(bg.path(identifier))
            continue
        validate(old, a) if old["format"] == FORMAT else bg.validate(old, a)
        validate(new, b)
        transition(old, new, a, b, j["operation"])
        mutable.add(bg.path(identifier))
    if identifiers: mutable.add("content/registry.json")
    return mutable
