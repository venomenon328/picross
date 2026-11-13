"""AT image authority, immutable production bindings and effective source resolver.

No solver, image conversion, Git lookup, actor authentication or network access.
"""
from copy import deepcopy
from datetime import datetime
from pathlib import Path
import re
import stat

from .authoring_package import relative, require, sha
from .contract import canonical_bytes, digest, exact_keys, integer
from . import catalog_io as io, catalog_rating as rating, categories

FORMAT = "picross-catalog-reveal-v1"
BACKGROUND_FORMAT = "picross-catalog-reveal-v2"
EDITOR_FORMAT = "picross-catalog-reveal-v3"
APPROVAL = "picross-reveal-approval-v1"
ROOT = "content/reveals"
LIMIT = 1024 * 1024
IMAGE_LIMIT = 32 * 1024 * 1024
RECEIPT = "picross-integrated-content-v1"
BACKGROUND_RECEIPT = "picross-integrated-content-v2"
EDITOR_RECEIPT = "picross-integrated-content-v3"


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


def receipt(value, entry, notice_hash, *, background=False, editor=False):
    """Check a receipt's closed shape without opening historical input refs.

    AT-v1 histories keep their original receipt-v1 contract. Only current
    package readers explicitly admit the independently bound background form.
    """
    is_background = isinstance(value, dict) and value.get("format") == BACKGROUND_RECEIPT
    is_editor = isinstance(value, dict) and value.get("format") == EDITOR_RECEIPT
    exact_keys(value, {"format", "entry", "integrated_commit", "notice_sha256"} |
               ({"background"} if is_background and background or is_editor and editor else set()))
    expected_format = EDITOR_RECEIPT if is_editor and editor else BACKGROUND_RECEIPT if is_background and background else RECEIPT
    require(value["format"] == expected_format and
            isinstance(value["integrated_commit"], str) and
            re.fullmatch(r"[0-9a-f]{40}", value["integrated_commit"]) and canonical_bytes(value["entry"]) == canonical_bytes(entry) and
            sha(value["notice_sha256"]) == notice_hash, "Integrated receipt identity/category/notice differs")
    if is_background:
        from . import catalog_background as backgrounds
        binding = exact_keys(value["background"], {"origin_sha256", "source"})
        sha(binding["origin_sha256"])
        ref = exact_keys(binding["source"], {"file", "sha256", "bytes"})
        relative(ref["file"]); sha(ref["sha256"])
        integer(ref["bytes"], 1, 1024 * 1024, "background source bytes")
        require(ref["file"] == backgrounds.path(entry["id"]), "Wrong receipt background source path")
    if is_editor:
        from . import catalog_background as backgrounds
        binding = exact_keys(value["background"], {"origin_sha256", "export_source"})
        sha(binding["origin_sha256"])
        if binding["export_source"] is not None:
            backgrounds._validate_v1(binding["export_source"], entry)
            require(binding["export_source"]["origin"]["export_manifest_sha256"] == entry["production"]["package_sha256"],
                    "Editor receipt export source binds another production")
    return value


def background_registry(root):
    from .content_registry import REGISTRY
    return io.json_bytes(io.read(root, REGISTRY, 8 * 1024 * 1024), 8 * 1024 * 1024)


def historical_categories(root, texts=None):
    """Current v4 FKs are validated by the registry, not historical bindings."""
    from .content_registry import REGISTRY, METADATA_FORMAT
    if texts is not None and REGISTRY in texts:
        raw = texts[REGISTRY]
        if isinstance(raw, str): raw = raw.encode("utf-8")
        registry = io.json_bytes(raw, 8 * 1024 * 1024)
    else:
        registry = background_registry(root)
    return registry.get("format") == METADATA_FORMAT


def require_legacy_target(root, entry, registry=None):
    """B1 has no contract for rebinding a background target's raster/reveal."""
    from . import catalog_background as backgrounds
    registry = background_registry(root) if registry is None else registry
    require(entry["id"] not in backgrounds.index(registry),
            "Background target reveal/raster changes require a later integration contract")


def validate(value, catalog, *, historical_categories=False):
    from .content_registry import validate_entries
    if isinstance(value, dict) and value.get("format") == EDITOR_FORMAT:
        from . import editor_image_source
        return editor_image_source.validate(value, catalog)
    exact_keys(value, {"format", "id", "record_revision", "identity", "origin", "bindings", "revisions", "current", "record_hash"})
    require(value["format"] in (FORMAT, BACKGROUND_FORMAT), "Unknown reveal source format")
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
        validate_entries([entry], None if historical_categories else catalog)
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
    if origin["receipt"] is not None:
        receipt(origin["receipt"], origin["entry"], origin["notice"]["sha256"], background=value["format"] == BACKGROUND_FORMAT)
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


def package(root, entry, *, background_snapshot=None, historical=False):
    """Check every stored export byte without replaying a deduction trace.

    A background journal may supply its old registry/text/binary view while
    live files are between publication phases. Immutable package bytes are
    still read afresh; the caller separately guards live ownership and stages
    the complete rollback view before mutating anything.
    """
    from .content_update import notice_path
    prefix = entry["production"]["package"]
    raw = io.read(root, prefix + "/manifest.json", 8 * 1024 * 1024)
    manifest = io.json_bytes(raw, 8 * 1024 * 1024)
    require(isinstance(manifest,dict), 'Invalid package manifest object')
    require(io.checksum(raw) == entry["production"]["package_sha256"], "Registered package binding changed")
    if manifest.get("format") == "picross-editor-raster-package-v1":
        from . import editor_raster
        return editor_raster.package(root, entry, manifest)
    files = {}
    base = io.safe(root, prefix)
    for p in base.rglob("*"):
        name = p.relative_to(root).as_posix()
        p = io.safe(root, name)
        if p.is_file(): files[name.removeprefix(prefix + "/")] = p
    if manifest.get("format") in (RECEIPT, BACKGROUND_RECEIPT, EDITOR_RECEIPT):
        exact_keys(manifest, {"format", "entry", "integrated_commit", "notice_sha256"} |
                   ({"background"} if manifest["format"] in (BACKGROUND_RECEIPT, EDITOR_RECEIPT) else set()))
        require(isinstance(manifest["entry"], dict) and isinstance(manifest["entry"].get("production"), dict) and
                isinstance(manifest["entry"]["production"].get("package_sha256"), str), "Invalid receipt entry")
        require(set(files) == {"manifest.json"}, "Integrated package contains unbound files")
        original = deepcopy(entry)
        original["production"]["package_sha256"] = manifest["entry"]["production"]["package_sha256"]
        receipt(manifest, original, manifest["notice_sha256"], background=True, editor=True)
        if historical:
            return original, manifest["notice_sha256"], manifest, set(prefix + "/" + n for n in files)
        from . import catalog_background as backgrounds
        registry = background_registry(root) if background_snapshot is None else background_snapshot[0]
        texts = None if background_snapshot is None else background_snapshot[1]
        declared = entry["id"] in backgrounds.index(registry)
        source = backgrounds._source(root, registry, entry, texts) if declared else None
        editor_background = source is not None and source["format"] == backgrounds.EDITOR_FORMAT
        if editor_background:
            backgrounds.check_editor_receipt(source, manifest, original)
        else:
            require(declared == (manifest["format"] == BACKGROUND_RECEIPT) and manifest["format"] != EDITOR_RECEIPT,
                    "Receipt generation differs from registered background authority")
        if manifest["format"] == BACKGROUND_RECEIPT and not editor_background:
            backgrounds.check_receipt(root, registry, entry, manifest, texts=texts)
        return original, manifest["notice_sha256"], manifest, set(prefix + "/" + n for n in files)
    require(manifest.get("format") in ("picross-target-export-v1", "picross-target-export-v2", "picross-target-export-v3", "picross-target-export-v4", "picross-target-export-v5", "picross-target-export-v6") and
            isinstance(manifest.get("files"), dict) and set(files) == set(manifest["files"]) | {"manifest.json"}, "Invalid/incomplete export inventory")
    legacy = manifest['format'].endswith('-v1')
    background = manifest['format'].endswith('-v6')
    palette = manifest['format'].endswith('-v5') or background
    paired = manifest['format'].endswith('-v4') or palette and 'deduction' in manifest
    manual = manifest['format'].endswith('-v3') or (paired or palette) and 'manual_authorization' in manifest
    exact_keys(manifest, {'format','adapter','definition_id','runtime_revision','package_revision','save_slot','stem','definition','reveal',
        'color_mapping','selection','handoff_sha256','inventory_sha256','approval_sha256','technical','editorial_approved','catalog_ready','registered','test_only','files'} |
        (set() if legacy else {'category_id','categories'}) | ({'manual_authorization'} if manual else set()) | ({'deduction'} if paired else set()) |
        ({'palette_gate'} if palette else set()) |
        ({'input','background','background_asset','background_notice','integration_ready'} if background else set()))
    require(io.checksum(raw) == entry["production"]["package_sha256"], "Export manifest binding differs")
    for name, checksum in manifest["files"].items():
        require(io.file_hash(root, prefix + "/" + name, io.export_limit(base, name)) == sha(checksum),
                "Altered export file: " + name)
    if not legacy:
        from . import categories
        reference = exact_keys(manifest["categories"], {"file", "sha256"})
        require(reference["file"] == "categories.json" and reference["sha256"] == manifest["files"].get("categories.json"),
                "Export categories snapshot binding differs")
        catalog = categories.validate(io.json_bytes(io.read(root, prefix + "/categories.json", categories.MAX_BYTES), categories.MAX_BYTES))
        categories.lookup(catalog, manifest["category_id"])
    require(manifest["definition_id"] == entry["id"] and manifest["save_slot"] == entry["save_slot"] and
            manifest["definition"] == "runtime/" + entry["definition"] and manifest["reveal"] == "runtime/" + entry["reveal"] and
            manifest["package_revision"] == entry["production"]["revision"] and manifest["test_only"] == entry["production"]["test_only"] and
            (manifest["format"].endswith("-v1") or manifest["category_id"] == entry["category_id"]), "Export identity/category differs")
    require(all(manifest["files"].get("runtime/" + entry[k]) == entry["production"][k + "_sha256"] for k in ("definition", "reveal")), "Export runtime binding differs")
    inspection = io.json_bytes(io.read(root, prefix + '/inspection.json', 8 * 1024 * 1024), 8 * 1024 * 1024)
    if palette:
        from .palette_gate import same
        same(inspection.get('format'), 'picross-target-inspection-v6' if background else 'picross-target-inspection-v5',
             'Missing matching palette/background inspection')
        same(inspection.get('palette_gate'), manifest['palette_gate'], 'Export/inspection palette binding differs')
        exact_keys(manifest['palette_gate'], {'assessment','binding','visual_review','exception','allowed'})
        require(manifest['palette_gate'].get('allowed') is True and inspection.get('technical') is True,
                'Registered palette gate is blocked')
    require(isinstance(inspection,dict) and all(k in inspection and inspection[k] == entry['production'][k] for k in ('width','height','mode','difficulty','test_only')) and
            inspection.get('package_revision') == entry['production']['revision'], 'Historical production metadata differs')
    from . import catalog_background as backgrounds
    registry = background_registry(root) if background_snapshot is None else background_snapshot[0]
    declared = not historical and entry['id'] in backgrounds.index(registry)
    if background:
        require(all(manifest[k] is False for k in ('integration_ready','catalog_ready','registered')) and
                manifest['technical'] is True and manifest['editorial_approved'] is True,
                'Invalid immutable background export readiness')
        require(declared or historical, 'Missing registered background authority')
    if declared:
        texts = None if background_snapshot is None else background_snapshot[1]
        source = backgrounds._source(root, registry, entry, texts)
        if source["format"] == backgrounds.EDITOR_FORMAT:
            require(source["binding"]["entry"] == entry, "Editor background current production binding differs")
            if background:
                # Validate the actual new export independently. Its image is
                # historical production, not a replacement of manual preference.
                backgrounds.build(base, manifest, inspection, entry)
            anchor = source["binding"]["entry"]["production"]["package_sha256"]
        else:
            source = backgrounds.load(root, registry, entry, texts=texts)
            anchor = (source["events"][-1]["binding"]["entry"]["production"]["package_sha256"]
                      if source["format"] in backgrounds.REBIND_FORMATS else backgrounds.initial(source)['origin']['export_manifest_sha256'])
        require(anchor == io.checksum(raw),
                'Background origin export binding differs')
    notice_hash=sha(manifest['files'].get('runtime/'+notice_path(entry).removeprefix('game/')))
    return deepcopy(entry), notice_hash, None, set(prefix + "/" + n for n in files)


def normalized(root, entry):
    return package(root, entry)[0]


def load(root, entry, catalog):
    raw = io.read(root, path(entry["id"]), LIMIT, missing=True)
    if raw is None: return None
    value = validate(io.json_bytes(raw, LIMIT), catalog, historical_categories=historical_categories(root))
    require(raw == canonical_bytes(value) + b"\n" and value["id"] == entry["id"], "Noncanonical/wrong reveal source")
    return value


def resolve(root, entry, catalog, *, record=None):
    from .content_update import notice_path
    from . import catalog_background as bg
    physical = io.file_hash(root, entry["production"]["package"] + "/manifest.json")
    require(physical == entry["production"]["package_sha256"], "Registered package binding changed")
    original, historical_notice, current_receipt, _ = package(root, entry)
    definition = io.read(root, "game/" + entry["definition"], 2 * 1024 * 1024)
    require(io.checksum(definition) == entry["production"]["definition_sha256"], "Registered definition binding changed")
    runtime_revision = rating.bytes_json(definition, 2 * 1024 * 1024)["revision"]
    record = load(root, entry, catalog) if record is None else validate(record, catalog, historical_categories=historical_categories(root))
    if record is not None:
        declared = entry["id"] in bg.index(background_registry(root))
        background_source = bg._source(root, background_registry(root), entry) if declared else None
        editor_background = background_source is not None and background_source["format"] == bg.EDITOR_FORMAT
        require(record["format"] == EDITOR_FORMAT or editor_background or record["format"] == (BACKGROUND_FORMAT if declared else FORMAT),
                "Reveal source generation differs from target")
        if declared and record["format"] != EDITOR_FORMAT:
            from .background_rebind import is_rebound
            require(is_rebound(background_source) or background_source["format"] == bg.EDITOR_FORMAT,
                    "Background reveal requires its current rebind authority")
    effective_image, effective_notice = entry["production"]["reveal_sha256"], historical_notice
    effective_path = "game/" + entry["reveal"]
    if record and record["format"] == EDITOR_FORMAT:
        from . import editor_image_source as editor
        require(record["binding"]["entry"] == original and
                record["binding"]["identity"]["runtime_revision"] == runtime_revision and
                record["binding"]["identity"]["definition"] == bg.ref("game/" + entry["definition"], definition),
                "Active editor reveal production binding differs")
        effective_path = record["current"]["asset"]["file"]
        effective_image = record["current"]["asset"]["sha256"]
        effective_notice = record["current"]["notice"]["sha256"]
        for alternative in editor.reveal_candidates(entry) - {effective_path}:
            require(io.read(root, alternative, IMAGE_LIMIT, missing=True) is None, "Inactive reveal alternative is present")
        historical = record["origin"]["source"]
        if historical and len(historical["bindings"]) == 1 and historical["origin"]["receipt"] is not None and \
                original == historical["origin"]["entry"]:
            require(current_receipt == historical["origin"]["receipt"], "Original reveal receipt changed")
    elif record:
        binding = record["bindings"][-1]
        require(binding["entry"] == original and binding["runtime_revision"] == runtime_revision and
                binding["notice"]["sha256"] == historical_notice, "Active reveal production binding differs")
        if len(record["bindings"]) == 1 and record["origin"]["receipt"] is not None:
            require(current_receipt == record["origin"]["receipt"], "Original reveal receipt changed")
        effective_image = record["revisions"][-1]["reveal_sha256"]
        effective_notice = record["revisions"][-1]["notice"]["sha256"]
    effective_raw = io.read(root, effective_path, IMAGE_LIMIT)
    if record and record["format"] == EDITOR_FORMAT:
        bg._bound(record["current"]["asset"], effective_raw, limit=IMAGE_LIMIT)
    require(io.checksum(effective_raw) == effective_image and
            io.file_hash(root, notice_path(entry), 65536) == effective_notice, "Effective reveal/notice binding changed")
    return {"id": entry["id"], "definition_sha256": entry["production"]["definition_sha256"],
            "runtime_revision": runtime_revision, "export_manifest_sha256": original["production"]["package_sha256"],
            "physical_manifest_sha256": physical, "historical_reveal_sha256": original["production"]["reveal_sha256"],
            "effective_reveal_sha256": effective_image, "historical_notice_sha256": historical_notice,
            "effective_notice_sha256": effective_notice, "record_hash": record["record_hash"] if record else None,
            "effective_reveal": effective_path.removeprefix("game/"),
            "effective_reveal_ref": bg.ref(effective_path, effective_raw)}


def revise(root, entry, catalog, image_hash, declaration, attribution, append=None):
    resolved = resolve(root, entry, catalog)
    old = load(root, entry, catalog)
    value = deepcopy(old)
    if value is None:
        original, _, integrated, _ = package(root, entry)
        original_notice = make_notice(io.read(root, identity(entry)["notice"], 65536))
        origin = {"entry": original, "runtime_revision": resolved["runtime_revision"], "notice": original_notice, "receipt": integrated}
        binding = hashed({"binding_revision": 1, **{k: origin[k] for k in ("entry", "runtime_revision", "notice")}, "previous_binding_hash": None}, "binding_hash")
        from . import catalog_background as bg
        declared = entry["id"] in bg.index(background_registry(root))
        value = {"format": BACKGROUND_FORMAT if declared else FORMAT, "id": entry["id"], "record_revision": 0, "identity": identity(entry),
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
    return validate(hashed(value, "record_hash"), catalog, historical_categories=historical_categories(root))


def rebind(old, entry, runtime_revision, export_notice, catalog, *, historical_categories=False, definition_ref=None):
    if old.get("format") == EDITOR_FORMAT:
        from . import editor_image_source
        require(definition_ref is not None, "Editor reveal rebind requires the actual new definition ref")
        return editor_image_source.rebind(old, entry, definition_ref, runtime_revision, catalog)
    value = deepcopy(old)
    require(entry["production"]["reveal_sha256"] == old["revisions"][-1]["reveal_sha256"], "Raster update must retain active reveal")
    value["bindings"].append(hashed({"binding_revision": len(old["bindings"]) + 1, "runtime_revision": runtime_revision,
                                   "entry": deepcopy(entry), "notice": make_notice(export_notice),
                                   "previous_binding_hash": old["bindings"][-1]["binding_hash"]}, "binding_hash"))
    value["current"]["binding_revision"] += 1
    value["record_revision"] += 1
    value.pop("record_hash")
    return validate(hashed(value, "record_hash"), catalog, historical_categories=historical_categories)
