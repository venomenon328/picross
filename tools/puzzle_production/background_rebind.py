"""Bounded, nonrecursive HP-I1c chronology; old source generations stay closed."""
from copy import deepcopy

from . import catalog_background as bg, catalog_io as io, reveal_source as at
from .authoring_package import require
from .contract import exact_keys, integer, canonical_bytes

FORMAT = "picross-catalog-background-v3"
UPDATE = "picross-content-update-journal-v7"
REVEAL = "picross-reveal-adoption-journal-v4"
BACKGROUND = "picross-background-adoption-journal-v2"


def entry_shape(value):
    # Only structural entry validation. Category labels are not authority here;
    # the live registry separately validates actual category membership.
    from .content_registry import validate
    from . import categories
    require(isinstance(value, dict) and isinstance(value.get("category_id"), str), "Invalid rebound entry")
    validate({"format": "picross-content-registry-v2", "entries": [value]},
             {"format": categories.FORMAT, "categories": [
                 {"id": value["category_id"], "name": "Binding", "order": 1}]})
    return value


def normalized(source):
    return source["events"][-1]["binding"]["entry"]


def image(source):
    return next((event["image"] for event in reversed(source["events"]) if event["image"] is not None),
                bg.current(source["base"]))


def reveal_hash(source):
    return (source["events"][-1]["binding"]["reveal"]["sha256"] if source["format"] == FORMAT else
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
    if source["format"] == FORMAT and stable["production"]["package"] == normalized(source)["production"]["package"]:
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
    if source["format"] == FORMAT:
        result = deepcopy(source)
    else:
        original_entry = deepcopy(original_entry)
        original_entry["production"]["package_sha256"] = bg.initial(source)["origin"]["export_manifest_sha256"]
        result = {"format": FORMAT, "base": deepcopy(source), "entry": original_entry, "events": []}
    result["events"].append({"operation": operation,
        "previous_source": bg.ref(bg.path(original_entry["id"]), bg.encoded(source)),
        "binding": deepcopy(value), "image": deepcopy(image), "export_source": deepcopy(export_source)})
    return validate(result, value["entry"])


def validate(value, entry):
    exact_keys(value, {"format", "base", "entry", "events"})
    require(value["format"] == FORMAT and isinstance(value["base"], dict) and
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
    for index, event in enumerate(events):
        exact_keys(event, {"operation", "previous_source", "binding", "image", "export_source"})
        require(event["previous_source"] == bg.ref(bg.path(entry["id"]), bg.encoded(previous_source)),
                "Background rebind predecessor differs")
        b = exact_keys(event["binding"], {"entry", "identity", "reveal", "notice", "at"})
        e = entry_shape(b["entry"])
        require(e["production"]["package"] == "content/packages/" + e["id"] + "/" + e["production"]["revision"],
                "Rebound package path differs")
        require(all(e[k] == origin_entry[k] == entry[k] for k in
                    ("id", "key", "save_slot", "definition", "reveal", "visible", "category_id")) and
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
        previous_source = {**value, "events": events[:index + 1]}
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
    record = at.validate(io.json_bytes(record_raw, at.LIMIT), catalog) if record_raw is not None else None
    if record is not None:
        require(record["format"] == at.BACKGROUND_FORMAT and record_raw == bg.encoded(record), "Wrong background AT source")
    last = source["events"][-1]["binding"]
    require(last["at"] == pointer(record), "Background effective AT pointer differs")
    for event in source["events"]:
        b = event["binding"]
        if b["at"] is None: continue
        history = at.validate(prefix(record, b["at"]), catalog)
        binding = history["bindings"][-1]
        revision = history["revisions"][-1]
        require(binding["entry"] == b["entry"] and binding["runtime_revision"] == b["identity"]["runtime_revision"] and
                revision["reveal_sha256"] == b["reveal"]["sha256"] and
                revision["notice"]["sha256"] == b["notice"]["sha256"],
                "Background historical AT binding differs")
    for key, limit in (("reveal", at.IMAGE_LIMIT), ("notice", 65536)):
        bg._bound(last[key], bg._raw(root, last[key]["file"], limit, texts), limit=limit)


def transition(old, new, old_entry, entry, operation):
    require(new["format"] == FORMAT, "Operation requires background Source v3")
    if old["format"] == FORMAT:
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
        validate(old, a) if old["format"] == FORMAT else bg.validate(old, a)
        validate(new, b)
        transition(old, new, a, b, j["operation"])
        mutable.add(bg.path(identifier))
    if identifiers: mutable.add("content/registry.json")
    return mutable
