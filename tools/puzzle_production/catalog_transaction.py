"""Shared SD-C publication/rollback, bounded journals and foreign-byte guards.

Recovery only restores the validated old view. It never replays a solver and
never removes a file whose bytes are not owned by this transaction.
"""
from copy import deepcopy
import hashlib
import os
from pathlib import Path
import tempfile
import time

from . import catalog_io
from .authoring_package import require, file_hash as package_hash, file_table, sha, relative
from .contract import canonical_bytes, exact_keys
from . import catalog_rating as rating, categories, catalog_added as added, catalog_io as io, reveal_source as reveal, catalog_method
from . import operation_diagnostics as diagnostic
from . import catalog_background as background_source
from . import background_rebind as rebind

REBIND_FORMATS = {"update": rebind.UPDATE, "reveal-adoption": rebind.REVEAL, "background-adoption": rebind.BACKGROUND}

LOCK = "content/.registration-pending.json"
REGISTRY = "content/registry.json"
RUNTIME = "game/data/registry.json"
LIMIT = 24 * 1024 * 1024
LEGACY_FORMATS = {"registration": "picross-registration-journal-v3", "update": "picross-content-update-journal-v2",
           "adoption": "picross-difficulty-adoption-journal-v1", "sync": "picross-difficulty-adoption-journal-v1"}

PREVIOUS_FORMATS = {"registration": "picross-registration-journal-v4", "update": "picross-content-update-journal-v3",
           "adoption": "picross-catalog-metadata-journal-v1", "sync": "picross-catalog-metadata-journal-v1",
           "added-adoption": "picross-catalog-metadata-journal-v1"}
AT_FORMATS = {"registration": "picross-registration-journal-v5", "update": "picross-content-update-journal-v4",
           "adoption": "picross-catalog-metadata-journal-v2", "sync": "picross-catalog-metadata-journal-v2",
           "added-adoption": "picross-catalog-metadata-journal-v2", "reveal-adoption": "picross-reveal-adoption-journal-v1"}
FORMATS = {"registration": "picross-registration-journal-v6", "update": "picross-content-update-journal-v5",
           "adoption": "picross-catalog-metadata-journal-v3", "sync": "picross-catalog-metadata-journal-v3",
           "added-adoption": "picross-catalog-metadata-journal-v3", "reveal-adoption": "picross-reveal-adoption-journal-v2",
           "method-activation": "picross-difficulty-activation-journal-v1"}
BACKGROUND_FORMATS = {"registration": "picross-registration-journal-v7", "update": "picross-content-update-journal-v6",
           "adoption": "picross-catalog-metadata-journal-v4", "sync": "picross-catalog-metadata-journal-v4",
           "added-adoption": "picross-catalog-metadata-journal-v4", "reveal-adoption": "picross-reveal-adoption-journal-v3",
           "method-activation": "picross-difficulty-activation-journal-v2",
           "background-adoption": "picross-background-adoption-journal-v1"}
PE_FORMATS = {"registration": "picross-registration-journal-v8", "update": "picross-content-update-journal-v8",
           "adoption": "picross-catalog-metadata-journal-v5", "sync": "picross-catalog-metadata-journal-v5",
           "added-adoption": "picross-catalog-metadata-journal-v5", "reveal-adoption": "picross-reveal-adoption-journal-v5",
           "method-activation": "picross-difficulty-activation-journal-v3",
           "background-adoption": "picross-background-adoption-journal-v3",
           "metadata": "picross-editor-metadata-journal-v1", "metadata-migration": "picross-editor-migration-journal-v1"}
REVEAL_LIMIT = 128 * 1024 * 1024
IMAGE_FORMATS = {"registration": "picross-registration-journal-v9", "update": "picross-content-update-journal-v9",
    "adoption": "picross-catalog-metadata-journal-v6", "sync": "picross-catalog-metadata-journal-v6",
    "added-adoption": "picross-catalog-metadata-journal-v6", "reveal-adoption": "picross-reveal-adoption-journal-v6",
    "method-activation": "picross-difficulty-activation-journal-v4", "background-adoption": "picross-background-adoption-journal-v4",
    "metadata": "picross-editor-metadata-journal-v2", "editor-images": "picross-editor-images-journal-v1",
    "editor-image-migration": "picross-editor-image-migration-journal-v1"}

RASTER_FORMAT = "picross-editor-raster-journal-v1"
IMAGE_FORMATS["editor-raster"] = RASTER_FORMAT


def images(j):
    return isinstance(j, dict) and j.get("format") in IMAGE_FORMATS.values()


def image_generation(snapshot):
    raw = snapshot["texts"][RUNTIME]
    if isinstance(raw, str): raw = raw.encode()
    try: value = io.json_bytes(raw, 8 * 1024 * 1024)
    except (ValueError, TypeError): return False  # Existing opaque stale-sync input.
    return isinstance(value, dict) and value.get("format") == "picross-runtime-registry-v8"


def image_candidates(registry):
    """Only fixed live stems; never a caller-supplied deletion namespace."""
    names = set()
    for entry in registry["entries"]:
        stem = Path("game/" + entry["reveal"])
        candidates = {stem.with_suffix(suffix).as_posix() for suffix in (".png", ".svg")}
        candidates.add(background_source.asset_path(entry["id"]))
        require(not {name.casefold() for name in names} & {name.casefold() for name in candidates},
                "Image candidate stems collide")
        names.update(candidates)
    return names


def active_reveal(entry, texts):
    raw = texts.get(reveal.path(entry["id"]))
    if isinstance(raw, str): raw = raw.encode()
    if raw is not None:
        value = io.json_bytes(raw, reveal.LIMIT)
        if value.get("format") == "picross-catalog-reveal-v3":
            from . import editor_image_source
            value = editor_image_source.validate(value)
            return value["current"]["asset"]["file"]
    return "game/" + entry["reveal"]


def image_snapshot(snapshot):
    sources = {**snapshot["retained"], **{name: io.checksum(raw.encode() if isinstance(raw, str) else raw)
                                       for name, raw in snapshot["texts"].items()}}
    registry = snapshot.get("registry")
    if registry is None:
        raw = snapshot["texts"][REGISTRY]
        registry = io.json_bytes(raw.encode() if isinstance(raw, str) else raw, 8 * 1024 * 1024)
    for name in image_candidates(registry): sources.setdefault(name, None)
    namespaces = deepcopy(snapshot.get("namespaces", {}))
    namespaces["reveal_assets"] = sorted(name for name, checksum in sources.items()
        if checksum is not None and name.startswith("game/art/content/") and Path(name).suffix in (".png", ".svg", ".txt"))
    return {"sources": sources, "namespaces": namespaces}


def reveal_assets(root, *registries, temporary=()):
    allowed = {name for registry in registries for name in image_candidates(registry)
               if name.startswith("game/art/content/")}
    allowed |= {Path(name).with_suffix(".txt").as_posix() for name in allowed}
    base = io.safe(root, "game/art/content")
    if not base.exists(): return set()
    require(base.is_dir(), "Reveal asset namespace must be a directory")
    found = set()
    for child in base.iterdir():
        name = child.relative_to(root).as_posix()
        path = io.safe(root, name)
        require(name in allowed or name in temporary, "Unbound reveal asset: " + name)
        require(path.is_file(), "Reveal asset must be a regular file: " + name)
        if name not in temporary: found.add(name)
    return found


def modern(j):
    return isinstance(j, dict) and j.get("format") in (*IMAGE_FORMATS.values(), *PE_FORMATS.values(), *REBIND_FORMATS.values(), *BACKGROUND_FORMATS.values(), *FORMATS.values(), *AT_FORMATS.values())


def sd2(j):
    return isinstance(j, dict) and j.get("format") in (*IMAGE_FORMATS.values(), *PE_FORMATS.values(), *REBIND_FORMATS.values(), *BACKGROUND_FORMATS.values(), *FORMATS.values())


def background(j):
    return isinstance(j, dict) and j.get("format") in (*IMAGE_FORMATS.values(), *PE_FORMATS.values(), *REBIND_FORMATS.values(), *BACKGROUND_FORMATS.values())


def metadata(j):
    return isinstance(j, dict) and j.get("format") in (*IMAGE_FORMATS.values(), *PE_FORMATS.values())


def safe(root, name):
    from .content_update import path_in
    return path_in(root, name)


def file_limit(root, name, journal=None):
    """Derive the exact v6 original ZIP limit, including an incomplete writer.

    Once a journal exists its validated source/origin and manifest/ZIP hashes
    provide the binding even before the new manifest is published, or after it
    has been removed during rollback. All other files keep their old limit.
    """
    from .authoring_package import MAX_FILE, MAX_ZIP
    parts = name.split("/")
    if len(parts) != 6 or parts[:2] != ["content", "packages"] or parts[4:] != ["input", "package.zip"]:
        return MAX_FILE
    prefix = "/".join(parts[:4])
    if journal is None:
        return io.export_limit(safe(root, prefix), "input/package.zip")
    if not background(journal):
        return MAX_FILE
    bound = {**journal["retained"], **journal["additions"]}
    for side in ("old", "new"):
        registry = io.json_bytes(journal[side][REGISTRY].encode(), 8 * 1024 * 1024)
        refs = background_source.index(registry)
        for entry in registry["entries"]:
            if entry["production"]["package"] != prefix or entry["id"] not in refs:
                continue
            raw = journal[side].get(background_source.path(entry["id"]))
            require(isinstance(raw, str), "Missing journal background source")
            raw = raw.encode()
            ref = refs[entry["id"]]
            require(len(raw) == ref["bytes"] and io.checksum(raw) == ref["sha256"], "Journal background source binding differs")
            source = background_source.validate(io.json_bytes(raw, background_source.LIMIT), entry)
            if source.get("format") == "picross-catalog-background-v5":
                if (source["binding"]["entry"]["production"]["package"] == prefix and
                        bound.get(prefix + "/manifest.json") == entry["production"]["package_sha256"] and name in bound):
                    return MAX_ZIP  # Complete staged export/receipt validation still precedes publication.
                continue
            origin = background_source.initial(source)["origin"]
            if rebind.is_rebound(source):
                update = next((e for e in reversed(source["events"]) if e["operation"] == "update"), None)
                if update and update["export_source"] is not None: origin = update["export_source"]["origin"]
            if (origin["package"] == prefix and bound.get(name) == origin["original_package"]["original_zip_sha256"] and
                    bound.get(prefix + "/manifest.json") == origin["export_manifest_sha256"]):
                return MAX_ZIP
    return MAX_FILE


def file_hash(root, name, journal=None):
    return io.file_hash(root, name, file_limit(root, name, journal))


def _addition_limit(registry, name, source):
    """Plan/staging policy before any target manifest or journal exists."""
    refs = background_source.index(registry)
    if (source.name == "package.zip" and source.parent.name == "input" and
            any(e["id"] in refs and name == e["production"]["package"] + "/input/package.zip" for e in registry["entries"])):
        return io.export_limit(source.parent.parent, "input/package.zip")
    return 64 * 1024 * 1024


def read(root, name, journal=None):
    if name == LOCK:
        from .catalog_publication import read_journal
        return read_journal(root)
    limit = (background_source.CAPABILITY_LIMIT if name == background_source.CAPABILITY else
             background_source.LIMIT if name.startswith(background_source.PATH + "/") else
             65536 if name.startswith(background_source.ASSET_PATH + "/") and name.endswith(".txt") else
             catalog_method.LIMIT if name == catalog_method.PATH else reveal.LIMIT if name.startswith(reveal.ROOT + "/") else 131072 if name == categories.PATH else
             added.REPORT_LIMIT if name.startswith(added.ROOT + "/reports/") else
             added.LIMIT if name.startswith(added.ROOT + "/") else
             rating.LIMIT if name.startswith("content/difficulty/pz-") else
             16 * 1024 * 1024 if name.startswith("content/difficulty/reports/") else
             8 * 1024 * 1024 if name in (REGISTRY,RUNTIME) else
             2 * 1024 * 1024 if name.startswith("game/data/content/") else file_limit(root, name, journal))
    return io.read(root, name, limit, missing=True)


def text_names(registry, *, legacy=False, previous=False, sd2=True, background=True):
    from .content_update import notice_path
    names = {REGISTRY, RUNTIME, categories.PATH}
    if sd2: names.add(catalog_method.PATH)
    for e in registry["entries"]:
        names.update(("game/" + e["definition"], notice_path(e), rating.path(e["id"])))
    if not legacy: names.update(added.path(e["id"]) for e in registry["entries"])
    if not legacy and not previous: names.update(reveal.path(e["id"]) for e in registry["entries"])
    if background: names.update(background_source.text_names(registry))
    return names


def retained_names(root, registry, *, reports=None, previous=False, exclude=(), texts=None, background=True,
                   background_snapshot=None):
    from .content_update import notice_path
    if reports is None: _, reports = added.source_paths(root, registry)
    names = set(reports)
    if background: names.update(background_source.retained_names(root, registry, texts))
    if not previous:
        # Namespace validation belongs to capture/guard, with both registries
        # during recovery: a newly registered rating is a valid own text target.
        directory = safe(root, "content/difficulty/reports")
        if directory.exists():
            names.update(p.relative_to(root).as_posix() for p in directory.rglob("*") if p.is_file())
        for entry in registry["entries"]:
            names.add(active_reveal(entry, texts) if texts is not None else
                      reveal.resolve(root, entry, categories.load(root / categories.PATH)).get("effective_reveal_ref", {}).get("file", "game/" + entry["reveal"]))
            names.update(reveal.package(root, entry, **({"background_snapshot": background_snapshot}
                         if background_snapshot is not None else {}))[3])
        return names - set(exclude)
    for e in registry["entries"]:
        manifest = e["production"]["package"] + "/manifest.json"
        names.update((manifest, "game/" + e["reveal"]))
        data = rating.bytes_json(read(root, manifest), 8 * 1024 * 1024)
        if data.get("format") != "picross-integrated-content-v1":
            names.add(e["production"]["package"] + "/runtime/" + notice_path(e).removeprefix("game/"))
    return names


@diagnostic.measured("Snapshot", "snapshots")
def capture(root, *, allow_stale=False):
    from .content_registry import check_checkout, validate
    root = catalog_io.external(root)
    from .catalog_publication import staging
    require(read(root, LOCK) is None and not staging(root), "Interrupted registration: recovery required")
    # Snapshot first, then validate it against the same checkout. No later read
    # may silently replace this starting point during expensive export checks.
    registry = rating.bytes_json(read(root, REGISTRY), 8 * 1024 * 1024)
    validate(registry, io.json_bytes(read(root, categories.PATH), 131072))
    initial_namespaces = namespaces(root, registry)
    names = text_names(registry)
    texts = {n: read(root, n) for n in names}
    retained = {n: file_hash(root, n) for n in retained_names(root, registry, texts=texts)}
    check_checkout(root, check_projection=not allow_stale)
    require(all(read(root, n) == b for n, b in texts.items()) and
            all(file_hash(root, n) == h for n, h in retained.items()), "Checkout changed during snapshot")
    require(namespaces(root, registry) == initial_namespaces, 'Checkout namespace changed during snapshot')
    return {"registry": registry, "texts": texts, "retained": retained, "namespaces": initial_namespaces}


def namespaces(root, *registries, temporary=(), images=None):
    catalog_method.load(root)
    reveals = reveal.source_paths(root, *registries, temporary=temporary)
    difficulty = rating.source_paths(root, *registries)
    reports = safe(root, "content/difficulty/reports")
    if reports.exists(): difficulty |= {p.relative_to(root).as_posix() for p in reports.rglob("*") if p.is_file()}
    dates, evidence = added.source_paths(root, *registries)
    packages = set()
    for r in registries:
        for e in r["entries"]:
            base = safe(root, e["production"]["package"])
            if base.exists():
                manifest = io.json_bytes(io.read(root,e["production"]["package"]+"/manifest.json",8*1024*1024),8*1024*1024)
                if manifest.get("format") == "picross-editor-raster-package-v1":
                    packages.update(reveal.package(root,e)[3])
            if base.exists():
                for p in base.rglob("*"):
                    p = safe(root, p.relative_to(root).as_posix())
                    if p.is_file(): packages.add(p.relative_to(root).as_posix())
    backgrounds, assets = background_source.source_paths(root, *registries, temporary=temporary)
    result = {"reveals": sorted(reveals), "difficulty": sorted(difficulty), "added": sorted(set(dates) | evidence),
              "packages": sorted(packages), "backgrounds": sorted(backgrounds), "background_assets": sorted(assets)}
    if images is None:
        raw = read(root, RUNTIME)
        images = raw is not None and image_generation({"texts": {RUNTIME: raw}})
    if images: result["reveal_assets"] = sorted(reveal_assets(root, *registries, temporary=temporary))
    return result


def require_legacy_background(root, *registries, runtimes=()):
    """Old journals never acquire new authorities; valid false is inert only."""
    require(all(r.get("format") == "picross-content-registry-v2" for r in registries),
            "Legacy journal cannot bind background registry")
    require(not background_source.capability(root), "Legacy journal cannot bind enabled background capability")
    sources, assets = background_source.source_paths(root, *registries)
    require(not sources and not assets, "Legacy journal cannot bind background namespace")
    for raw in (*runtimes, read(root, RUNTIME)):
        if raw is None: continue
        if isinstance(raw, str): raw = raw.encode()
        try: runtime = io.json_bytes(raw, 8 * 1024 * 1024)
        except (ValueError, TypeError): continue  # Existing opaque stale-sync rule.
        require(not isinstance(runtime, dict) or runtime.get("format") != background_source.RUNTIME_FORMAT,
                "Legacy journal cannot bind background runtime")


def pre_background_snapshot(snapshot):
    """Project a compatible inactive snapshot to its exact historical scope."""
    registry = io.json_bytes(snapshot["texts"][REGISTRY], 8 * 1024 * 1024)
    require(registry.get("format") == "picross-content-registry-v2", "Legacy plan cannot bind background registry")
    require(not background_source.capability(None, {background_source.CAPABILITY: snapshot["texts"].get(background_source.CAPABILITY)}),
            "Legacy plan cannot bind enabled background capability")
    prefixes = (background_source.PATH + "/", background_source.ASSET_PATH + "/")
    require(all(raw is None for n, raw in snapshot["texts"].items() if n.startswith(prefixes)) and
            not any(n.startswith(prefixes) for n in snapshot["retained"]), "Legacy plan cannot bind background sources")
    runtime = io.json_bytes(snapshot["texts"][RUNTIME], 8 * 1024 * 1024)
    require(runtime.get("format") in tuple("picross-runtime-registry-v" + str(v) for v in (2, 3, 4, 5)),
            "Legacy plan cannot bind background runtime")
    result = {**snapshot, "texts": {n: raw for n, raw in snapshot["texts"].items()
              if n != background_source.CAPABILITY and not n.startswith(prefixes)}}
    if "namespaces" in snapshot:
        require(not snapshot["namespaces"].get("backgrounds") and not snapshot["namespaces"].get("background_assets"),
                "Legacy plan cannot bind background namespace")
        result["namespaces"] = {k: v for k, v in snapshot["namespaces"].items() if k not in ("backgrounds", "background_assets")}
    return result


def pre_sd2_snapshot(snapshot):
    """Old plans cannot silently bind new method/default/runtime authorities."""
    snapshot = pre_background_snapshot(snapshot)
    require(snapshot["texts"].get(catalog_method.PATH) is None, "Legacy plan cannot bind production default")
    runtime = io.json_bytes(snapshot["texts"][RUNTIME], 8 * 1024 * 1024)
    require(runtime["format"] != "picross-runtime-registry-v5", "Legacy plan cannot bind runtime v5")
    for name, raw in snapshot["texts"].items():
        if name.startswith("content/difficulty/pz-") and raw is not None:
            require(rating.method(rating.validate(rating.bytes_json(raw))) == catalog_method.OLD, "Legacy plan cannot bind SD2 rating")
    return {**snapshot, "texts": {n: b for n, b in snapshot["texts"].items() if n != catalog_method.PATH}}


def historical_snapshot(snapshot):
    """Exact pre-AT source scope for stored reports, never an AT fallback."""
    from .content_update import notice_path
    snapshot = pre_background_snapshot(snapshot)
    r = rating.bytes_json(snapshot["texts"][REGISTRY], 8 * 1024 * 1024)
    require(all(snapshot["texts"].get(reveal.path(e["id"])) is None for e in r["entries"]), "Legacy plan/report cannot bind active reveal sources")
    names = {n for n in snapshot["retained"] if n.startswith(added.ROOT + "/reports/")}
    for e in r["entries"]:
        names |= {"game/" + e["reveal"], e["production"]["package"] + "/manifest.json"}
        n = e["production"]["package"] + "/runtime/" + notice_path(e).removeprefix("game/")
        if n in snapshot["retained"]: names.add(n)
    return {"texts": {n: b for n, b in snapshot["texts"].items() if not n.startswith(reveal.ROOT + "/")},
            "retained": {n: snapshot["retained"][n] for n in names}}


def report_names(run, operation="adoption"):
    if operation == "added-adoption": return {added.report_path(run)}
    if run is None: return set()
    from .catalog_analysis import run_id
    run_id(run)
    return {"content/difficulty/reports/" + run + "/report." + ext for ext in ("json", "md")}


def projection(texts, registry, *, version=None):
    from .content_registry import projection as project, validate
    catalog = rating.bytes_json(texts[categories.PATH].encode(), 131072)
    validate(registry, catalog)
    default = texts.get(catalog_method.PATH)
    catalog_method.from_bytes(default.encode() if default is not None else None)
    records = {}
    for e in registry["entries"]:
        raw = texts["game/" + e["definition"]].encode()
        require(hashlib.sha256(raw).hexdigest() == e["production"]["definition_sha256"], "Wrong transaction definition binding")
        value = texts[rating.path(e["id"])]
        if value is not None:
            records[e["id"]] = rating.validate(rating.bytes_json(value.encode()), definition_bytes=raw,
                                              production_mode=e["production"]["mode"])
    dates = {}
    for e in registry["entries"]:
        value = texts.get(added.path(e["id"]))
        if value is not None: dates[e["id"]] = added.validate(rating.bytes_json(value.encode(), added.LIMIT), e["id"])
    from .content_registry import METADATA_FORMAT
    if version is None:
        version = 7 if registry["format"] == METADATA_FORMAT else 6 if registry["format"] == background_source.REGISTRY_FORMAT else 5
        if version == 7 and texts.get(RUNTIME) is not None and image_generation({"texts": texts}): version = 8
    backgrounds = background_source.projection(registry, texts) if version >= 6 else None
    reveals = {e["id"]: active_reveal(e, texts).removeprefix("game/") for e in registry["entries"]} if version == 8 else None
    result = project(registry, catalog, ratings=records, added=dates, version=3 if version == 2 else version, backgrounds=backgrounds, reveals=reveals)
    if version == 2:
        result["format"] = "picross-runtime-registry-v2"
        for e in result["entries"]: del e["difficulty"]
    return canonical_bytes(result) + b"\n"


@diagnostic.measured("Staging/Proof", "staged_checkout_checks")
def _stage_check(root, texts, retained, additions=None, replacements=None, legacy=False, journal=None):
    """Check a complete target view in isolation; no user saves or source replay."""
    from .content_registry import check_checkout, ROOT
    registry = rating.bytes_json(texts[REGISTRY].encode(), 8 * 1024 * 1024)
    if legacy:
        # Historical journals bind the manifest, which in turn binds the full
        # inventory. Reconstruct that inventory without altering journal fields.
        retained = dict(retained)
        for e in registry['entries']:
            for n in reveal.package(root, e)[3]: retained[n] = file_hash(root, n, journal)
    require(root != ROOT.resolve() or all(not e["production"]["test_only"] for e in registry["entries"]),
            "Test-only content cannot enter the real catalog")
    with tempfile.TemporaryDirectory(prefix="sd-c-check-") as temp:
        stage = Path(temp)
        for name in sorted(set(retained) | set(texts) | set(additions or {}) | set(replacements or {})):
            if name in texts:
                data = texts[name].encode() if texts[name] is not None else None
            elif additions and name in additions:
                limit = file_limit(root, name, journal) if journal is not None else _addition_limit(registry, name, additions[name])
                data = io.read(additions[name].parent, additions[name].name, limit)
            elif replacements and name in replacements:
                from .catalog_publication import decode_binary
                data = decode_binary(replacements[name]) if replacements[name] is not None else None
            else:
                data = read(root, name, journal)
            if data is None: continue
            target = stage / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        check_checkout(stage)


def prepare(root, snapshot, changes, *, operation, additions=None, report_run=None, replacements=None, generation="metadata"):
    additions = additions or {}
    require(operation in PE_FORMATS or operation in IMAGE_FORMATS, "Unknown transaction operation")
    before = snapshot["registry"]
    require(generation in ("images", "metadata", "rebind", "background", "sd2", "at"), "Unknown journal generation")
    if before["format"] == "picross-content-registry-v4" and image_generation(snapshot): generation = "images"
    if operation in ("editor-images", "editor-image-migration"): generation = "images"
    if generation == "images":
        require(operation in IMAGE_FORMATS, "Image catalog requires a compatible operation")
        require(operation == "editor-image-migration" or image_generation(snapshot), "Explicit image projection migration required")
    from .content_registry import METADATA_FORMAT, require_current
    if before["format"] == METADATA_FORMAT and generation in ("background", "rebind"):
        generation = "metadata"
    if generation in ("metadata", "images") and operation != "metadata-migration":
        require_current(before)
    require(operation not in ("metadata", "metadata-migration") or generation in ("metadata", "images"), "Editor operation requires its own journal generation")
    if generation == "background" and operation in REBIND_FORMATS and any(
            changes.get(background_source.path(e["id"]), snapshot["texts"].get(background_source.path(e["id"]))) !=
            snapshot["texts"].get(background_source.path(e["id"])) and
            (operation != "background-adoption" or
             rebind.is_rebound(io.json_bytes(snapshot["texts"][background_source.path(e["id"])], background_source.LIMIT)))
            for e in before["entries"] if e["id"] in background_source.index(before)):
        generation = "rebind"
    require(operation != "background-adoption" or generation in ("images", "metadata", "background", "rebind"),
            "Background adoption requires its own journal generation")
    backgrounds = generation in ("images", "metadata", "background", "rebind")
    current = generation != "at"
    if not backgrounds: snapshot = pre_background_snapshot(snapshot)
    if not current: snapshot = pre_sd2_snapshot(snapshot)
    after_raw = changes.get(REGISTRY, snapshot["texts"][REGISTRY])
    after = rating.bytes_json(after_raw, 8 * 1024 * 1024)
    names = text_names(before, sd2=current, background=backgrounds) | text_names(after, sd2=current, background=backgrounds) | report_names(report_run, operation)
    require(set(changes) <= names and not (set(additions) & names), "Unexpected transaction write target")
    old = {n: snapshot["texts"].get(n) if n in snapshot["texts"] else read(root, n) for n in names}
    # New ID resources and sidecars must not pre-exist outside the source registry.
    for n in names - text_names(before, sd2=current, background=backgrounds) - report_names(report_run, operation):
        require(old[n] is None, "Target already exists/collides: " + n)
    new = {**old, **changes}
    require(all(b is None or isinstance(b, bytes) for b in new.values()), "Invalid transaction bytes")
    j = {"format": (IMAGE_FORMATS if generation == "images" else PE_FORMATS if generation == "metadata" else REBIND_FORMATS if generation == "rebind" else BACKGROUND_FORMATS if backgrounds else FORMATS if current else AT_FORMATS)[operation], "operation": operation,
         "old": {n: b.decode("utf-8") if b is not None else None for n, b in old.items()},
         "new": {n: b.decode("utf-8") if b is not None else None for n, b in new.items()},
         "retained": {n: h for n, h in snapshot["retained"].items() if n not in (replacements or {})},
         "additions": {}, "report_run": report_run, "replacements": replacements or {}}
    # Bind source bytes before deriving the journal-based ZIP exception.
    for n, p in additions.items():
        limit = _addition_limit(after, n, p)
        j["additions"][n] = io.file_hash(p.parent, p.name, limit)
    if operation not in ("reveal-adoption", "method-activation") or generation == "images":
        j["new"][RUNTIME] = projection(j["new"], after, version=8 if generation == "images" else None if backgrounds else 5 if current else 4).decode()
    validate_journal(root, j, before_write=True)
    _stage_check(root, j["new"], j["retained"], additions, {n: pair["new"] for n, pair in j["replacements"].items()}, journal=j)
    from .catalog_publication import journal_bytes
    journal_bytes(j)
    return j


def _delta(j, before, after, root=None):
    from .content_update import notice_path
    from .content_registry import METADATA_FORMAT, current_metadata
    op = j["operation"]
    if op == "editor-raster":
        from .catalog_raster import validate_delta
        return validate_delta(j, before, after, root)
    if op in ("editor-images", "editor-image-migration"):
        from .catalog_images import validate_delta
        return validate_delta(j, before, after, root)
    changed = {n for n in j["old"] if j["old"][n] != j["new"][n]}
    mutable = {RUNTIME}
    package = None
    reveal_target = None
    background_target = None
    before_backgrounds, after_backgrounds = background_source.index(before), background_source.index(after)
    rebound = j["format"] in REBIND_FORMATS.values() or metadata(j) and op in REBIND_FORMATS
    if op not in ("registration", "background-adoption", "metadata-migration") and not rebound:
        require(before["format"] == after["format"] and before_backgrounds == after_backgrounds,
                "Operation changes background registry authority")
    if op in ("metadata", "metadata-migration"):
        require(metadata(j) and after["format"] == METADATA_FORMAT and
                before["entries"] == after["entries"] and before_backgrounds == after_backgrounds and
                j["report_run"] is None and not j["replacements"], "Invalid editor metadata delta")
        mutable.add(REGISTRY)
        if op == "metadata-migration":
            require(before["format"] in ("picross-content-registry-v2", "picross-content-registry-v3") or
                    before == after and not changed,
                    "Migration requires v2/v3 source or an unchanged v4 no-op")
            catalog = io.json_bytes(j["old"][categories.PATH].encode(), categories.MAX_BYTES)
            expected = current_metadata(before, catalog, definitions={e["id"]: j["old"]["game/" + e["definition"]] for e in before["entries"]})
            require(after["metadata"] == list(expected.values()), "Migration changes current metadata")
        else:
            require(before["format"] == METADATA_FORMAT, "Metadata edit requires migrated source")
            mutable.add(categories.PATH)
    elif op == "registration":
        new_entries = [e for e in after["entries"] if e not in before["entries"]]
        require(len(new_entries) == 1 and [e for e in after["entries"] if e not in new_entries] == before["entries"], "Invalid registration delta")
        e = new_entries[0]
        mutable |= {REGISTRY, "game/" + e["definition"], notice_path(e), rating.path(e["id"])}
        require(all(after_backgrounds.get(identifier) == ref for identifier, ref in before_backgrounds.items()) and
                set(after_backgrounds) - set(before_backgrounds) <= {e["id"]}, "Registration changes existing backgrounds")
        has_background = e["id"] in after_backgrounds
        require(after["format"] == (METADATA_FORMAT if metadata(j) else background_source.REGISTRY_FORMAT if has_background else before["format"]),
                "Registration changes registry generation without a new background")
        if metadata(j):
            definition = io.json_bytes(j["new"]["game/" + e["definition"]].encode(), 2 * 1024 * 1024)
            expected = {"id": e["id"], "name": definition["reveal"]["name"], "category_id": e["category_id"]}
            require(after["metadata"] == sorted(before["metadata"] + [expected], key=lambda row: row["id"]),
                    "Registration changes existing metadata or omits new metadata")
        if has_background:
            require(background(j), "Background registration requires its bound journal generation")
            source_name, notice_name = background_source.path(e["id"]), background_source.notice_path(e["id"])
            source = background_source.validate(io.json_bytes(j["new"][source_name].encode(), background_source.LIMIT), e)
            require(source["format"] == background_source.FORMAT, "First registration requires background Source v1")
            require(source["origin"]["export_manifest_sha256"] == e["production"]["package_sha256"], "Wrong new background export anchor")
            mutable.update((source_name, notice_name))
            if source["asset"] is not None:
                background_target = source["asset"]["file"]
                require(j["additions"].get(background_target) == source["asset"]["sha256"], "Wrong new background asset binding")
                require(j["new"][notice_name] is not None and io.checksum(j["new"][notice_name].encode()) == source["notice"]["sha256"],
                        "Wrong new background notice binding")
                for key in ("asset", "notice"):
                    packaged = e["production"]["package"] + "/runtime/" + source[key]["file"].removeprefix("game/")
                    require(j["additions"].get(packaged) == source[key]["sha256"], "Wrong package background output binding")
            else:
                require(j["new"][notice_name] is None, "none cannot publish a background notice")
        if j["format"] in (IMAGE_FORMATS["registration"], PE_FORMATS["registration"], BACKGROUND_FORMATS["registration"], FORMATS["registration"], AT_FORMATS["registration"], PREVIOUS_FORMATS["registration"]):
            mutable.add(added.path(e["id"]))
            value = j["new"][added.path(e["id"])]
            require(value is not None and added.validate(rating.bytes_json(value.encode(), added.LIMIT), e["id"])["provenance"]["kind"] == "registration", "Registration needs its first added timestamp")
        require(all(j["old"][n] is None for n in mutable - {REGISTRY, RUNTIME}), "Occupied registration target")
        require(j["new"][rating.path(e["id"])] is not None, "New registration requires difficulty 0.3")
        package, reveal_target = e["production"]["package"], "game/" + e["reveal"]
    elif op == "update":
        pairs = [(a, b) for a, b in zip(before["entries"], after["entries"]) if a != b]
        require(len(before["entries"]) == len(after["entries"]) and len(pairs) == 1, "Invalid update delta")
        a, e = pairs[0]
        require(a["id"] not in before_backgrounds or j["format"] in (rebind.UPDATE, PE_FORMATS["update"], IMAGE_FORMATS["update"]),
                "Background target raster update requires bound journal v7")
        if rebound:
            mutable |= rebind.delta(j, before, after, [a["id"]] if a["id"] in before_backgrounds else [])
        active = j["old"].get(reveal.path(a["id"]))
        active = io.json_bytes(active.encode(), reveal.LIMIT) if active is not None else None
        fixed = ("id", "key", "save_slot", "definition", "reveal", "visible") + (() if metadata(j) else ("category_id",))
        editor_reveal = active is not None and active.get("format") == "picross-catalog-reveal-v3"
        require(all(a[k] == e[k] for k in fixed) and (images(j) and editor_reveal or
                (active["revisions"][-1]["reveal_sha256"] if active else a["production"]["reveal_sha256"]) == e["production"]["reveal_sha256"]), "Update changes fixed identity/reveal")
        n = "game/" + e["definition"]
        old_def = rating.bytes_json(j["old"][n].encode(), 2 * 1024 * 1024)
        new_def = rating.bytes_json(j["new"][n].encode(), 2 * 1024 * 1024)
        require(old_def["id"] == new_def["id"] == e["id"] and new_def["revision"] > old_def["revision"], "Invalid update revision")
        mutable |= {REGISTRY, n, notice_path(e), rating.path(e["id"])}
        if active:
            mutable.add(reveal.path(e["id"]))
            fresh = io.json_bytes(j["new"][reveal.path(e["id"])].encode(), reveal.LIMIT)
            catalog = rating.bytes_json(j["old"][categories.PATH].encode(), 131072)
            if editor_reveal:
                expected = reveal.rebind(active, e, new_def["revision"], b"", catalog,
                    historical_categories=True, definition_ref=background_source.ref(n, j["new"][n].encode()))
            else:
                expected = reveal.rebind(active, e, new_def["revision"], fresh["bindings"][-1]["notice"]["text"].encode(), catalog,
                                         historical_categories=metadata(j))
            require(fresh == expected and j["new"][notice_path(e)] == j["old"][notice_path(e)], "Invalid reveal rebind delta")
        if (rating.definition(j["old"][n].encode())[3] != rating.definition(j["new"][n].encode())[3] or
                a["production"]["mode"] != e["production"]["mode"]):
            require(j["new"][rating.path(e["id"])] is not None, "Changed logic requires difficulty 0.3")
        package = e["production"]["package"]
        require(package != a["production"]["package"], "Update reuses old package")
    elif op == "background-adoption":
        require(j["report_run"] is None, "Background adoption cannot adopt reports")
        mutable |= background_source.validate_delta(j, before, after, root)
    else:
        require(before["entries"] == after["entries"] if rebound else before == after,
                "Difficulty operation changes production registry")
        if op == "method-activation":
            mutable = {catalog_method.PATH}
            require(j["report_run"] is None and sd2(j), "Invalid activation transaction")
            prior = catalog_method.from_bytes(j["old"][catalog_method.PATH].encode() if j["old"][catalog_method.PATH] is not None else None)
            current = catalog_method.from_bytes(j["new"][catalog_method.PATH].encode())
            plan_format = catalog_method.IMAGE_PLAN if images(j) else catalog_method.PLAN if background(j) else catalog_method.LEGACY_PLAN
            sources = catalog_method.source_hashes({"retained": j["retained"], "texts": {n: b.encode() if b is not None else None for n, b in j["old"].items()}}, plan_format)
            plan = rating.hashed({"format": plan_format, "expected": catalog_method.current(prior),
                "target": {k: current[k] for k in ("method", "method_hash")}, "sources": sources}, "result_hash")
            catalog_method.validate_plan(plan)
            require(current == catalog_method.record_for(plan, prior), "Invalid activation delta")
        elif op == "reveal-adoption":
            require(j["report_run"] is None, "Reveal adoption cannot adopt reports")
            require(rebound or not any("game/" + e["reveal"] in j["replacements"] for e in before["entries"] if e["id"] in before_backgrounds),
                    "Background target reveal adoption requires a later package")
            from .catalog_reveal import validate_delta
            mutable |= validate_delta(j, before, root)
            if rebound:
                affected = {identifier for identifier, ref in before_backgrounds.items()
                            if after_backgrounds.get(identifier) != ref}
                reveal_ids = {e["id"] for e in before["entries"]
                              if j["old"][reveal.path(e["id"])] != j["new"][reveal.path(e["id"])]}
                require(affected <= reveal_ids, "Reveal adoption changes an unrelated background")
                mutable |= rebind.delta(j, before, after, sorted(affected))
        elif op == "adoption": mutable |= {rating.path(e["id"]) for e in before["entries"]} | report_names(j["report_run"], j["operation"])
        elif op == "added-adoption":
            mutable |= {added.path(e["id"]) for e in before["entries"]} | report_names(j["report_run"], op)
            from .catalog_added_history import validate_delta
            validate_delta(j, before)
        else: require(j["report_run"] is None, "Sync cannot adopt reports")
    if metadata(j) and op not in ("metadata", "metadata-migration", "registration"):
        require(before["metadata"] == after["metadata"], "Operation changes current puzzle metadata")
    require(changed <= mutable, "Unexpected transaction source mutation")
    if package:
        rating_name = rating.path(e["id"])
        prior = rating.bytes_json(j["old"][rating_name].encode()) if j["old"][rating_name] is not None else None
        current = rating.bytes_json(j["new"][rating_name].encode()) if j["new"][rating_name] is not None else None
        if sd2(j):
            new_logic = op == "registration" or rating.definition(j["old"][n].encode())[3] != rating.definition(j["new"][n].encode())[3] or a["production"]["mode"] != e["production"]["mode"]
            default = catalog_method.from_bytes(j["old"][catalog_method.PATH].encode() if j["old"][catalog_method.PATH] is not None else None)
            require(not new_logic or current is not None and rating.method(current) == catalog_method.current(default)["method"], "New logic requires active production method")
        require(prior is None or current is not None, "Update cannot remove active difficulty")
        if current is not None and prior != current:
            require(current["rating_revision"] == (prior["rating_revision"] + 1 if prior else 1) and
                    current["adoption"]["previous_record_hash"] == (prior["record_hash"] if prior else None) and
                    current["adoption"]["report"] is None, "Invalid integration rating revision/provenance")
        require(package == "content/packages/" + e["id"] + "/" + e["production"]["revision"], "Invalid package target")
        require(all(n.startswith(package + "/") or n in (reveal_target, background_target) for n in j["additions"]), "Invalid package addition target")
        require(j["additions"].get(package + "/manifest.json") == e["production"]["package_sha256"], "Wrong package manifest binding")
        exported_notice = (j["additions"].get(package + "/runtime/" + notice_path(e).removeprefix("game/"))
                           if op == "update" and editor_reveal else
                           fresh["bindings"][-1]["notice"]["sha256"] if op == "update" and active else
                           hashlib.sha256(j["new"][notice_path(e)].encode()).hexdigest())
        for n, h in (("runtime/" + e["definition"], e["production"]["definition_sha256"]),
                     ("runtime/" + e["reveal"], e["production"]["reveal_sha256"]),
                     ("runtime/" + notice_path(e).removeprefix("game/"), exported_notice)):
            require(j["additions"].get(package + "/" + n) == h, "Wrong package runtime binding")
        if reveal_target: require(j["additions"].get(reveal_target) == e["production"]["reveal_sha256"], "Wrong new reveal binding")
        require(not any(n == package or n.startswith(package + "/") for n in j["retained"]), "Addition overlaps retained package")
    else:
        require(not j["additions"], "Unexpected difficulty additions")
    return package


@diagnostic.measured("Journal validation", "journal_validations")
def validate_journal(root, j, *, before_write=False):
    require(isinstance(j, dict) and isinstance(j.get("format"), str), "Invalid catalog journal")
    current_generation = modern(j)
    new_generation = sd2(j)
    background_generation = background(j)
    exact_keys(j, {"format", "operation", "old", "new", "retained", "additions", "report_run"} | ({"replacements"} if current_generation else set()))
    require(isinstance(j["format"], str) and isinstance(j["operation"], str) and
            any(formats.get(j["operation"]) == j["format"] for formats in
                (IMAGE_FORMATS, PE_FORMATS, REBIND_FORMATS, BACKGROUND_FORMATS, FORMATS, AT_FORMATS, PREVIOUS_FORMATS, LEGACY_FORMATS)),
            "Unsupported catalog journal")
    legacy = j["format"] in LEGACY_FORMATS.values()
    for k in ("old", "new", "retained", "additions"): require(isinstance(j[k], dict), "Invalid journal map")
    require(all(v is None or isinstance(v, str) for side in ("old", "new") for v in j[side].values()), "Invalid journal text")
    for side in ("old", "new"):
        for n in (REGISTRY, RUNTIME, categories.PATH): require(isinstance(j[side].get(n), str), "Missing journal source")
    before, after = (rating.bytes_json(j[s][REGISTRY].encode(), 8 * 1024 * 1024) for s in ("old", "new"))
    from .content_registry import validate, METADATA_FORMAT
    require(isinstance(before, dict) and isinstance(after, dict), "Invalid journal registry object")
    if metadata(j):
        require(after.get("format") == METADATA_FORMAT and (before.get("format") == METADATA_FORMAT or
                j["operation"] == "metadata-migration" and before.get("format") in ("picross-content-registry-v2", "picross-content-registry-v3")),
                "Metadata journal requires its exact registry generation")
    else:
        require(before.get("format") != METADATA_FORMAT and after.get("format") != METADATA_FORMAT,
                "Historical journal cannot bind metadata registry v4")
    for side, registry in (("old",before),("new",after)):
        validate(registry, io.json_bytes(j[side][categories.PATH].encode(), 131072))
    names = text_names(before, legacy=legacy, previous=not current_generation, sd2=new_generation, background=background_generation) | text_names(after, legacy=legacy, previous=not current_generation, sd2=new_generation, background=background_generation) | report_names(j["report_run"], j["operation"])
    if background_generation:
        for side, registry in (("old", before), ("new", after)):
            projected = background_source.projection(registry, j[side])
            background_source.capability(None, j[side], required=registry["format"] == background_source.REGISTRY_FORMAT or
                                         any(row["status"] in ("selected", "none") for row in projected.values()))
        require(j["old"].get(background_source.CAPABILITY) == j["new"].get(background_source.CAPABILITY),
                "Transaction changes background capability")
    else:
        require_legacy_background(root, before, after, runtimes=(j["old"][RUNTIME], j["new"][RUNTIME]))
    if not new_generation:
        require(catalog_method.load(root) is None, "Legacy journal cannot bind production default")
        # Old sync permits opaque stale bytes, but must never downgrade the
        # recognized C authority under that exception.
        try: old_runtime = io.json_bytes(j["old"][RUNTIME].encode(), 8 * 1024 * 1024)
        except ValueError: old_runtime = None
        require(not isinstance(old_runtime, dict) or old_runtime.get("format") != "picross-runtime-registry-v5",
                "Legacy journal cannot bind runtime v5")
    if not current_generation:
        require(not reveal.source_paths(root, before, after), "Legacy journal cannot bind reveal sources")
    else:
        from .catalog_publication import validate_replacements
        validate_replacements(j, before)
    if legacy:
        present, reports = added.source_paths(root, before, after)
        require(not present and not reports, "Legacy journal cannot bind added sources")
    require(set(j["old"]) == set(j["new"]) == names, "Invalid journal target set")
    old_reports = set()
    for e in before["entries"]:
        raw = j["old"].get(added.path(e["id"]))
        if raw is not None:
            source = added.validate(rating.bytes_json(raw.encode(), added.LIMIT), e["id"])["provenance"]["evidence"]
            if source: old_reports.add(source["path"])
    old_background = None
    if background_generation:
        from .catalog_publication import decode_binary
        # Package bindings are immutable, but live source/image writes can be
        # between phases. Validate inventory against the journal's old view;
        # full live ownership guards and the isolated rollback check follow.
        old_background = (before, {**j["old"], **{
            name: decode_binary(pair["old"]) if pair["old"] is not None else None
            for name, pair in j["replacements"].items()}})
    retained = retained_names(root, before, reports=old_reports, previous=not current_generation,
                              exclude=set(j.get("replacements", {})) | report_names(j["report_run"], j["operation"]),
                              texts=j["old"], background=background_generation, background_snapshot=old_background)
    require(set(j["retained"]) == retained, "Invalid retained source set")
    for side, registry in (("old", before), ("new", after)):
        from .content_registry import validate
        validate(registry, rating.bytes_json(j[side][categories.PATH].encode(), 131072))
        require(j[side][REGISTRY].encode() == canonical_bytes(registry) + b"\n", "Noncanonical journal registry")
        versions = [5] if new_generation else [3] if legacy else [4]
        if j["operation"] in ("reveal-adoption", "method-activation") or new_generation and side == "old": versions = [4, 5] if new_generation else [4]
        if not legacy and side == "old" and all(j[side].get(added.path(e["id"])) is None for e in registry["entries"]): versions += [2, 3]
        if j["operation"] in ("reveal-adoption", "method-activation") and all(j[side].get(added.path(e["id"])) is None for e in registry["entries"]): versions += [2, 3]
        if background_generation and registry["format"] == background_source.REGISTRY_FORMAT: versions = [6]
        if metadata(j) and registry["format"] == METADATA_FORMAT: versions = [7]
        if images(j): versions = [7, 8] if side == "old" and j["operation"] == "editor-image-migration" else [8]
        if side == "new" or j["operation"] != "sync":
            raw = j[side][RUNTIME].encode()
            runtime = io.json_bytes(raw, 8 * 1024 * 1024)
            matching = [v for v in versions if runtime.get("format") == "picross-runtime-registry-v" + str(v)]
            require(matching and raw == projection(j[side], registry, version=matching[0]), "Invalid journal projection")
    package = _delta(j, before, after, root)
    for n, h in {**j["retained"], **j["additions"]}.items(): relative(n); sha(h); safe(root, n)
    if j["report_run"] is not None and j["operation"] != "added-adoption":
        from .catalog_analysis import validate_report, markdown
        prefix = "content/difficulty/reports/" + j["report_run"] + "/report."
        report = validate_report(rating.bytes_json(j["new"][prefix + "json"].encode(), 16 * 1024 * 1024))
        require(report["run_id"] == j["report_run"] and j["new"][prefix + "md"] == markdown(report), "Conflicting journal report")
        require(j["operation"] == "adoption" and report["operation"]["phase"] == "adopted" and
                all(j["old"][n] is None for n in report_names(j["report_run"], j["operation"])), "Report is not a new adoption")
        require(all(hashlib.sha256(j["old"][n].encode()).hexdigest() == h for n,h in report["result"]["snapshot"].items()),
                "Wrong report snapshot")
        from .catalog_analysis import SOURCE_FORMATS, source_hashes
        if report["format"] in SOURCE_FORMATS:
            captured = {"retained": j["retained"], "texts": {n: j["old"][n].encode() if j["old"][n] is not None else None
                        for n in text_names(before, legacy=legacy, previous=not current_generation, sd2=new_generation, background=background_generation)}}
            require(report["result"]["sources"] == source_hashes(captured, report["format"]), "Wrong report source snapshot")
        entries = {e["id"]: e for e in before["entries"]}
        rows = {r["id"]: r for r in report["result"]["entries"]}
        require(set(rows) <= set(entries) and (report["result"]["selection"] != "all" or set(rows) == set(entries)), "Wrong report selection")
        from .catalog_difficulty import project as historical
        for identifier, entry in entries.items():
            name = rating.path(identifier)
            prior = rating.bytes_json(j["old"][name].encode()) if j["old"][name] is not None else None
            current = rating.bytes_json(j["new"][name].encode()) if j["new"][name] is not None else None
            row = rows.get(identifier)
            if row is None:
                require(prior == current, "Unselected rating changed")
                continue
            require(row["previous_record_hash"] == (prior["record_hash"] if prior else None) and
                    row["old"] == (rating.project(prior) if prior else historical(entry["production"]["difficulty"])), "Wrong report old rating")
            if report["format"] in SOURCE_FORMATS:
                require(row["previous_rating_revision"] == (prior["rating_revision"] if prior else None), "Wrong report old revision")
            if row["current_source"] is not None:
                _, _, source, logic = rating.definition(j["old"]["game/" + entry["definition"]].encode(), method=report["result"].get("method", catalog_method.OLD))
                require(row["current_source"] == source and row["logic_binding"] == logic, "Wrong report definition binding")
            if row["status"] != "rated":
                require(prior == current, "Incomplete attempt changed active rating")
            else:
                require(current is not None and rating.project(current) == row["proposed"] and
                        current["rating"]["rating_hash"] == row["rating_hash"], "Wrong adopted report rating")
                from .catalog_analysis import METHOD_FORMATS
                if report["format"] in METHOD_FORMATS:
                    require(row["assessment"] == current["rating"]["result"].get("assessment"), "Wrong adopted report assessment")
                if prior != current:
                    require(current["rating_revision"] == (prior["rating_revision"] + 1 if prior else 1) and
                            current["adoption"]["previous_record_hash"] == row["previous_record_hash"] and
                            current["adoption"]["report"] == {"run_id": report["run_id"], "result_hash": report["result_hash"]} and
                            rating.checked_from_active(current)["checked_hash"] == row["checked_hash"], "Wrong adopted report provenance")
    else:
        require(j["operation"] != "adoption", "Adoption requires a report")
    guard(root, j, old_only=before_write)
    # The rollback goal is checked in full before any real mutation. A sync may
    # have started with a stale projection; recovery directly restores current v4.
    old = deepcopy(j["old"])
    old[RUNTIME] = restore_runtime(j, before)
    _stage_check(root, old, j["retained"], replacements={n: pair["old"] for n, pair in j.get("replacements", {}).items()}, legacy=not current_generation, journal=j)
    return package, old[RUNTIME]


def restore_runtime(j, registry):
    if j["operation"] in ("reveal-adoption", "method-activation") or sd2(j) and j["operation"] != "sync":
        return j["old"][RUNTIME]
    if sd2(j):
        raw = j["old"][RUNTIME].encode()
        try:
            runtime = io.json_bytes(raw, 8 * 1024 * 1024)
            version = next((v for v in (2, 3, 4, 5, 6, 7, 8) if runtime.get("format") == "picross-runtime-registry-v" + str(v)), None)
            if version is not None and raw == projection(j["old"], registry, version=version): return j["old"][RUNTIME]
        except (ValueError, TypeError, KeyError):
            pass  # A sync may have begun with stale bytes; sources remain strict.
    return projection(j["old"], registry, version=None if background(j) else 5 if sd2(j) else 4).decode()


def guard(root, j, *, old_only=False, journal_bytes=None):
    if modern(j):
        from .catalog_publication import guard as current_guard
        return current_guard(root, j, old_only=old_only, raw=journal_bytes)
    from . import catalog_method
    require(catalog_method.load(root) is None, "Legacy journal cannot bind production default")
    registries = [rating.bytes_json(j[s][REGISTRY].encode(), 8 * 1024 * 1024) for s in ("old", "new")]
    require_legacy_background(root, *registries, runtimes=(j["old"][RUNTIME], j["new"][RUNTIME]))
    require(not reveal.source_paths(root, *registries), "Legacy journal cannot bind reveal sources")
    for e in registries[0]['entries']: reveal.package(root, e)
    rating.source_paths(root, *registries)
    extras = set(j["retained"]) & {n for n in j["retained"] if n.startswith(added.ROOT + "/reports/")}
    if j["operation"] == "added-adoption": extras |= report_names(j["report_run"], j["operation"])
    added.source_paths(root, *registries, extra_reports=extras)
    if journal_bytes is not None:
        require(read(root, LOCK) == journal_bytes, "Journal changed; preserve all transaction files")
    for n, old in j["old"].items():
        allowed = [old]
        if not old_only:
            allowed.append(j["new"][n])
            if n == RUNTIME:
                registry = rating.bytes_json(j["old"][REGISTRY].encode(), 8 * 1024 * 1024)
                allowed.append(restore_runtime(j, registry))
        current = read(root, n)
        require(current in [v.encode() if v is not None else None for v in allowed], "Transaction target changed; preserve journal: " + n)
    for n, h in j["retained"].items():
        p = safe(root, n)
        require(p.is_file() and package_hash(p) == h, "Retained source changed; preserve journal: " + n)
    for n, h in j["additions"].items():
        p = safe(root, n)
        require(not p.exists() if old_only else not p.exists() or p.is_file() and package_hash(p) == h,
                "Transaction package changed; preserve journal: " + n)
    # Unknown files in an added package belong to somebody else. Never rmtree.
    packages = set()  # roots derived below, not supplied by callers
    for n in j["additions"]:
        if n.startswith("content/packages/"):
            packages.add("/".join(n.split("/")[:4]))
    for name in packages:
        p = safe(root, name)
        if p.exists():
            present = file_table(p, time.monotonic() + 300)
            require(all(name + "/" + n in j["additions"] for n in present), "Transaction package changed; unexpected file")


def _write(root, name, text, *, create=False):
    from .content_registry import atomic_bytes
    target = safe(root, name)
    if text is None:
        target.unlink(missing_ok=True)
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        if create: _publish_new(target, text.encode())
        else: atomic_bytes(target, text.encode())


def _publish_new(target, data):
    """Publish complete new bytes without replacing a concurrently created file."""
    fd, temporary = tempfile.mkstemp(dir=target.parent, prefix=".sd-c-new-")
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data); stream.flush(); os.fsync(stream.fileno())
        os.link(temporary, target)  # Atomic no-replace on the same filesystem.
    finally:
        Path(temporary).unlink(missing_ok=True)


def execute(root, j, additions=None, *, fail_step=None, publication_seconds=None, recovery_seconds=None,
            source_check=None, _verification=None):
    diagnostic.seconds(publication_seconds)
    diagnostic.seconds(recovery_seconds)
    require(isinstance(j, dict), "Invalid catalog journal")
    require(modern(j) and j.get("operation") == "registration" or publication_seconds is None and recovery_seconds is None,
            "RI-A overrides require a new registration")
    if modern(j):
        from .catalog_publication import execute as current_execute
        return current_execute(root, j, additions, fail_step=fail_step,
                               publication_seconds=publication_seconds, recovery_seconds=recovery_seconds,
                               **({"source_check": source_check} if source_check is not None else {}),
                               **({"_verification": _verification} if _verification is not None else {}))
    require(source_check is None, "Source recheck requires background adoption")
    require(_verification is None, "Verification context cannot enter a legacy writer")
    from .content_registry import check_checkout
    additions = additions or {}
    validate_journal(root, j, before_write=True)
    raw = canonical_bytes(j) + b"\n"
    require(len(raw) <= LIMIT, "Transaction journal exceeds 24 MiB")
    lock = safe(root, LOCK)
    with lock.open("xb") as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    try:
        guard(root, j, old_only=True, journal_bytes=raw)
        for index, (n, h) in enumerate(sorted(j["additions"].items())):
            guard(root, j, journal_bytes=raw)
            data = additions[n].read_bytes()
            require(hashlib.sha256(data).hexdigest() == h, "Staged package changed")
            target = safe(root, n)
            target.parent.mkdir(parents=True, exist_ok=True)
            require(not target.exists(), "Addition appeared during publication")
            _publish_new(target, data)
            if index == 0 and fail_step == "crash": raise InterruptedError("Injected registration interruption")
            if index == 0 and fail_step == "files": raise OSError("Injected registration interruption")
        if fail_step == "crash-package": raise InterruptedError("Injected update crash after package")
        if j["operation"] == "registration":
            from .target_adapter import verify_export
            before, after = (rating.bytes_json(j[s][REGISTRY].encode(), 8 * 1024 * 1024) for s in ("old", "new"))
            package = _delta(j, before, after)
            verify_export(safe(root, package))  # Retain mandatory ZA-1 written-package verification.
        names = sorted(n for n in j["new"] if n != RUNTIME and j["old"][n] != j["new"][n]) + [RUNTIME]
        for n in names:
            guard(root, j, journal_bytes=raw)
            require(read(root, n) == (j["old"][n].encode() if j["old"][n] is not None else None), "Transaction target changed during publication")
            _write(root, n, j["new"][n], create=j["old"][n] is None and j["new"][n] is not None)
            if fail_step == "crash-" + n or n == REGISTRY and fail_step == "crash-index" or n == RUNTIME and fail_step == "crash-runtime":
                raise InterruptedError("Injected transaction interruption: " + n)
            if fail_step == n or n == REGISTRY and fail_step == "index": raise OSError("Injected update failure: " + n)
        guard(root, j, journal_bytes=raw)
        check_checkout(root, replay=j["operation"] == "registration", pending_journal=raw)
        guard(root, j, journal_bytes=raw)
        require(all(read(root, n) == (v.encode() if v is not None else None) for n,v in j["new"].items()), "Publication changed before completion")
        require(lock.read_bytes() == raw, "Journal changed during publication")
        lock.unlink()
    except InterruptedError:
        raise
    except BaseException:
        # Recovery refuses foreign changes and keeps the lock if rollback is unsafe.
        require(read(root, LOCK) == raw, "Journal changed; preserve all transaction files")
        recover(root)
        raise


def recover(root):
    if diagnostic.frame.get() is None or diagnostic.frame.get().kind != "Recovery":
        from .content_registry import recover as classified_recover
        return classified_recover(root)
    return _recover(root)


def _recover(root):
    from .content_registry import check_checkout
    root = catalog_io.external(root)
    raw = read(root, LOCK)
    if raw is None or modern(io.json_bytes(raw, REVEAL_LIMIT)):
        from .catalog_publication import recover as current_recover
        return current_recover(root)
    j = rating.bytes_json(raw, LIMIT)
    _, runtime = validate_journal(root, j)
    # Delete only individually hash-checked additions. Empty directory cleanup is
    # cosmetic; retaining empty parents cannot conceal or destroy foreign work.
    diagnostic.begin_segment("R1")
    for n in sorted(j["additions"], reverse=True):
        guard(root, j, journal_bytes=raw)
        safe(root, n).unlink(missing_ok=True)
    for n in sorted(j["old"]):
        if n == RUNTIME or j["old"][n] == j["new"][n]: continue
        guard(root, j, journal_bytes=raw)
        _write(root, n, j["old"][n])
    guard(root, j, journal_bytes=raw)
    _write(root, RUNTIME, runtime)
    diagnostic.begin_segment("R2")
    check_checkout(root, pending_journal=raw)
    guard(root, j, journal_bytes=raw)
    goal = {**j["old"], RUNTIME: runtime}
    require(all(read(root, n) == (v.encode() if v is not None else None) for n,v in goal.items()) and
            all(read(root, n) is None for n in j["additions"]), "Recovery goal changed before completion")
    require(read(root, LOCK) == raw, "Journal changed during recovery")
    safe(root, LOCK).unlink()
    # Only remove verified empty directories under the new package/sidecar roots.
    for n in sorted(set(j["additions"]) | {n for n in j["old"] if j["old"][n] is None}, reverse=True):
        p = safe(root, n).parent
        while p != root and p.is_relative_to(root) and p not in (root/"content", root/"game"):
            try: p.rmdir()
            except OSError: break
            p = p.parent
    return {"status": "rolled-back", "registered": False}
