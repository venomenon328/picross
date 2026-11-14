"""External repository migrations only; excluded from the portable editor."""
from copy import deepcopy
from .catalog_images import (io, tx, registry, source, reveal, bg, require, encoded,
    MIGRATION, _hash_plan, _outside, _validate_plan, _source)


def plan_migration(root, output=None, *, seconds=300):
    with io.budget(seconds):
        root = io.external(root)
        snapshot = tx.capture(root)
        registry.require_current(snapshot["registry"])
        journal = tx.prepare(root, snapshot, {}, operation="editor-image-migration", generation="images")
        result = _hash_plan({"format": MIGRATION, "snapshot": tx.image_snapshot(snapshot),
            "old": io.json_bytes(journal["old"][tx.RUNTIME].encode(), 8 * 1024 * 1024),
            "new": io.json_bytes(journal["new"][tx.RUNTIME].encode(), 8 * 1024 * 1024),
            "files": [tx.RUNTIME] if journal["old"][tx.RUNTIME] != journal["new"][tx.RUNTIME] else []})
        if output is not None:
            output = _outside(output, root)
            require(not output.exists(), "Migration plan output must be new")
            output.parent.mkdir(parents=True, exist_ok=True)
            with output.open("xb") as stream: stream.write(encoded(result))
        return result


def apply_migration(root, value, *, seconds=300, fail_step=None):
    with io.budget(seconds):
        root = io.external(root)
        value = _validate_plan(deepcopy(value))
        require(value["format"] == MIGRATION, "Expected image migration plan")
        snapshot = tx.capture(root)
        if value["old"]["format"] == registry.METADATA_RUNTIME_FORMAT:
            require(all(not source.is_editor(_source(snapshot["texts"], name)) for entry in snapshot["registry"]["entries"]
                        for name in (reveal.path(entry["id"]), bg.path(entry["id"]))),
                    "Runtime v7 cannot be the old image migration state of editor sources")
        actual = tx.image_snapshot(snapshot)
        if actual != value["snapshot"]:
            inverse = deepcopy(actual)
            inverse["sources"][tx.RUNTIME] = io.checksum(encoded(value["old"]))
            require(io.json_bytes(snapshot["texts"][tx.RUNTIME], 8 * 1024 * 1024) == value["new"] and
                    inverse == value["snapshot"], "Image migration plan is stale")
            return {"status": "noop", "files": [], "plan_hash": value["plan_hash"]}
        journal = tx.prepare(root, snapshot, {}, operation="editor-image-migration", generation="images")
        require(io.json_bytes(journal["old"][tx.RUNTIME].encode(), 8 * 1024 * 1024) == value["old"] and
                io.json_bytes(journal["new"][tx.RUNTIME].encode(), 8 * 1024 * 1024) == value["new"] and
                value["files"] == ([tx.RUNTIME] if journal["old"][tx.RUNTIME] != journal["new"][tx.RUNTIME] else []),
                "Migration preview differs from fresh reconstruction")
        if value["files"]: tx.execute(root, journal, fail_step=fail_step)
        return {"status": "migrated" if value["files"] else "noop", "files": value["files"], "plan_hash": value["plan_hash"]}


from . import catalog_metadata as legacy_metadata

@io.bounded
def plan_metadata_migration(root):
    """Explicit v2/v3 to v4 migration, with all other sources left byte-identical."""
    root = io.external(root)
    snapshot = tx.capture(root)
    before = snapshot["registry"]
    require(not tx.image_generation(snapshot),
            "Metadata migration keeps its v4/v7 contract; the checkout already uses the explicit v8 image projection")
    catalog = legacy_metadata._catalog(snapshot["texts"])
    after = deepcopy(before)
    if before["format"] != registry.METADATA_FORMAT:
        metadata = legacy_metadata._metadata(before, catalog, snapshot["texts"])
        after.update(format=registry.METADATA_FORMAT,
                     metadata=[metadata[key] for key in sorted(metadata)],
                     backgrounds=deepcopy(before.get("backgrounds", [])))
    registry.validate(after, catalog)
    return legacy_metadata._plan(root, snapshot, after, catalog, [], "metadata-migration")

