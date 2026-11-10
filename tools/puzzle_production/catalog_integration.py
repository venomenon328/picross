"""ZA-1 integration with external, prechecked SD-C evidence (no analysis calls)."""
from copy import deepcopy
from contextlib import ExitStack
import hashlib
from pathlib import Path
import shutil
import tempfile
import time

from . import catalog_io, catalog_background as background
from . import background_rebind as rebind
from . import operation_diagnostics as diagnostic
from .authoring_package import file_hash, file_table, require, sha
from .contract import canonical_bytes, load_json
from . import catalog_added as added, categories, catalog_rating as rating, catalog_transaction as tx, reveal_source as reveal, catalog_method


def _input(value):
    if isinstance(value, Path):
        absolute = value.absolute()
        path = tx.safe(Path(absolute.anchor), absolute.relative_to(absolute.anchor).as_posix())
        raw = rating.read_file(path)
        return rating.validate(rating.bytes_json(raw), active=False), (path, raw)
    return rating.validate(deepcopy(value), active=False), None


def _new_rating(raw, previous, checked, rebind, *, required, production_mode, active_method, new_logic):
    external = None
    if checked is not None:
        value, external = _input(checked)
    elif previous is not None and rebind:
        value = rating.checked_from_active(previous)
    else:
        require(not required, "New integration requires a complete " + active_method.removeprefix("picross-difficulty-") + " rating")
        return None, None
    if rebind:
        value = rating.rebind_checked(value, raw, production_mode=production_mode)
    else:
        rating.validate(value, active=False, definition_bytes=raw, production_mode=production_mode)
    require(value.get("production_mode") == production_mode, "New integration requires mode-bound analysis")
    require(not new_logic or rating.method(value) == active_method, "New logic requires the active production method")
    active = rating.active_record(value, previous, kind="rebind" if rebind else "analysis")
    rating.validate(active, definition_bytes=raw)
    return active, external


@diagnostic.measured("Input/Plan")
def integrate(export_dir, root, *, apply=False, expected_definition_sha256=None, difficulty=None,
              rebind_difficulty=False, fail_step=None, publication_seconds=None, recovery_seconds=None):
    diagnostic.seconds(publication_seconds)
    diagnostic.seconds(recovery_seconds)
    require(apply and expected_definition_sha256 is None or publication_seconds is None and recovery_seconds is None,
            "RI-A overrides require mutating new registration, not plan/update")
    from .content_registry import ROOT, export_entry, check_checkout, validate
    from .content_update import notice_path
    from .target_adapter import verify_export, FORMAT, MANUAL_FORMAT, PAIRED_FORMAT, BACKGROUND_EXPORT, palette_gate
    root = catalog_io.external(root)
    export_dir = catalog_io.external(export_dir)
    # Admission of v6 input never substitutes for a compatible target. This
    # fixed capability is checked before catalog capture, journals or replay.
    manifest = catalog_io.json_bytes(catalog_io.read(export_dir, "manifest.json", 8 * 1024 * 1024),
                                     8 * 1024 * 1024)
    update = expected_definition_sha256 is not None
    is_background = isinstance(manifest, dict) and manifest.get("format") == BACKGROUND_EXPORT
    if is_background:
        background.capability(root, required=True)
    if update: sha(expected_definition_sha256)
    snapshot = tx.capture(root)
    registry = snapshot["registry"]
    if diagnostic.current.get():
        diagnostic.current.get().environment["catalog_entries"] = len(registry["entries"])
    catalog = rating.bytes_json(snapshot["texts"][categories.PATH], 131072)
    from . import registration_verification as verification
    original_state = verification.inventory(export_dir) if apply and not update else None
    m, report = verify_export(export_dir)  # Existing mandatory full production check.
    require(m["format"] in (FORMAT, MANUAL_FORMAT, PAIRED_FORMAT, palette_gate.EXPORT, BACKGROUND_EXPORT), "Category-less legacy export: create a new categorized export")
    require(not m["test_only"] or root != ROOT.resolve(), "Test-only fixtures cannot be registered in the real repository")
    category = categories.lookup(catalog, m["category_id"])
    entry = export_entry(export_dir, m, report, category, background=is_background)
    existing = next((e for e in registry["entries"] if e["id"].casefold() == entry["id"].casefold()), None)
    old_background = background.load(root, registry, existing) if existing else None
    active_reveal = reveal.load(root, existing, catalog) if existing else None
    n = "game/" + entry["definition"]
    if update:
        require(existing is not None, "Update requires an existing production ID")
        require(not is_background or old_background is not None, "Legacy retrofit is unsupported")
        require(old_background is None or m["format"] in (palette_gate.EXPORT, BACKGROUND_EXPORT),
                "Background raster update requires v5 or v6")
        require(file_hash(tx.safe(root, "game/" + existing["definition"])) == expected_definition_sha256, "Stale expected definition hash")
        require(all(entry[k] == existing[k] for k in ("id", "key", "save_slot", "definition", "reveal", "visible", "category_id")),
                "Raster update must retain identity, paths, visibility, category and save slot")
        effective = reveal.resolve(root, existing, catalog)["effective_reveal_sha256"]
        require(entry["production"]["reveal_sha256"] == effective, "Raster update must retain the approved reveal bytes")
    if existing is not None:
        from .integrated_content import FORMAT as INTEGRATED
        original = load_json(root / existing["production"]["package"] / "manifest.json")
        same = reveal.normalized(root, existing) == entry
        if is_background and old_background is not None:
            exported_background = background.build(export_dir, m, report, entry)
            if not update:
                same = background.initial(old_background) == exported_background
            elif same:
                same = (next((event["export_source"] for event in reversed(old_background["events"]) if event["operation"] == "update"),
                             background.initial(old_background)) if old_background["format"] == rebind.FORMAT else
                        background.initial(old_background)) == exported_background
        if same:
            check_checkout(root, replay=not update and original.get("format") not in (INTEGRATED, background.RECEIPT_FORMAT))
            require(all(tx.read(root, name) == raw for name, raw in snapshot["texts"].items()) and
                    all(tx.file_hash(root, name) == h for name, h in snapshot["retained"].items()) and
                    tx.namespaces(root,registry)==snapshot['namespaces'], "Checkout changed during planning")
            return {"status": "no-op", "registered": True, "id": entry["id"], "category": category, "changes": []}
        require(update, "Occupied production ID/revision: update is outside ZA-1")
    raw = (export_dir / m["definition"]).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == entry["production"]["definition_sha256"], "Export definition changed during planning")
    previous = None
    if existing:
        old_raw = snapshot["texts"]["game/" + existing["definition"]]
        old_def = rating.bytes_json(old_raw, 2 * 1024 * 1024)
        require(m["runtime_revision"] > old_def["revision"], "Update requires a higher runtime revision")
        new_logic = (rating.definition(old_raw)[3] != rating.definition(raw)[3] or
                    existing["production"]["mode"] != entry["production"]["mode"])
        p = snapshot["texts"][rating.path(existing["id"])]
        previous = rating.validate(rating.bytes_json(p), definition_bytes=old_raw) if p is not None else None
        # A present rating may never silently disappear on a metadata update.
        required = new_logic or previous is not None
    else:
        required = new_logic = True
    package = entry["production"]["package"]
    active, external = _new_rating(raw, previous, difficulty, rebind_difficulty, required=required,
                                   production_mode=entry["production"]["mode"], new_logic=new_logic,
                                   active_method=catalog_method.current(catalog_method.from_bytes(snapshot["texts"][catalog_method.PATH]))["method"])
    new = deepcopy(registry)
    if existing: new["entries"][new["entries"].index(existing)] = entry
    else: new["entries"].append(entry)
    new["entries"].sort(key=lambda e: e["id"])
    source = background.build(export_dir, m, report, entry) if is_background and not existing else None
    if source is not None:
        new["format"] = background.REGISTRY_FORMAT
        new.setdefault("backgrounds", []).append({"id": entry["id"], "source": background.ref(background.path(entry["id"]), background.encoded(source))})
        new["backgrounds"].sort(key=lambda row: row["id"])
    validate(new, catalog)
    notice = notice_path(entry)
    changes = {tx.REGISTRY: canonical_bytes(new) + b"\n", n: raw,
               notice: (export_dir / ("runtime/" + notice.removeprefix("game/"))).read_bytes(),
               rating.path(entry["id"]): rating.encoded(active) if active is not None else None}
    if source is not None:
        changes[background.path(entry["id"])] = background.encoded(source)
        if source["notice"] is not None:
            changes[source["notice"]["file"]] = catalog_io.read(export_dir, m["background_notice"]["file"], 65536)
    if active_reveal:
        rebound = reveal.rebind(active_reveal, entry, m["runtime_revision"], changes[notice], catalog)
        changes[reveal.path(entry["id"])] = canonical_bytes(rebound) + b"\n"
        changes[notice] = snapshot["texts"][notice]
    if update and old_background is not None:
        rebound_record = rebound if active_reveal else None
        bound = rebind.binding(root, old_background, entry, raw,
            catalog_io.read(root, "game/" + entry["reveal"], reveal.IMAGE_LIMIT), changes[notice], rebound_record)
        rebound_background = rebind.append(old_background, existing, bound, "update",
            export_source=background.build(export_dir, m, report, entry) if is_background else None)
        name = background.path(entry["id"])
        changes[name] = background.encoded(rebound_background)
        for row in new["backgrounds"]:
            if row["id"] == entry["id"]: row["source"] = background.ref(name, changes[name])
        changes[tx.REGISTRY] = background.encoded(new)
    with tempfile.TemporaryDirectory(prefix="sd-c-integration-") as temp, ExitStack() as scope:
        stage = Path(temp) / "package"
        shutil.copytree(export_dir, stage)
        checked = (scope.enter_context(verification.verified(stage, export_dir, original_state, root, snapshot,
                    (m, report), external)) if apply and not existing else None)
        if checked is None:
            verify_export(stage)  # Preserve the existing independent staging replay.
        require(file_hash(stage / "manifest.json") == entry["production"]["package_sha256"], "Export changed during staging")
        additions = {package + "/" + name: p for name, p in file_table(stage, time.monotonic() + 300,
                     **({"original_zip": "input/package.zip"} if is_background else {})).items()}
        if diagnostic.current.get():
            diagnostic.current.get().environment["package_files"] = len(additions)
        target=tx.safe(root,package)
        if target.exists():
            parents={str(parent).replace('\\','/') for name in additions for parent in Path(name).parents}
            if is_background and not any(name.startswith("external/") for name in m["files"]) and not any(
                    m["background"][key]["storage"] == "external" for key in ("manifest", "decision", "derivation")):
                parents.add(package + "/external")
            require(target.is_dir() and all(tx.safe(root,p.relative_to(root).as_posix()).is_dir() and
                    p.relative_to(root).as_posix() in parents for p in target.rglob('*')),
                    'Update package revision already exists' if update else 'Target already exists: '+package)
        if not existing: additions["game/" + entry["reveal"]] = stage / m["reveal"]
        if source is not None and source["asset"] is not None:
            additions[source["asset"]["file"]] = stage / m["background_asset"]["file"]
        # A read-only registration plan does not allocate its first timestamp.
        if not existing and apply:
            changes[added.path(entry["id"])] = added.encoded(added.registration(entry["id"]))
        journal = tx.prepare(root, snapshot, changes, operation="update" if update else "registration", additions=additions) if existing or apply else None
        if journal is None:
            names = tx.text_names(registry) | tx.text_names(new)
            old = {name: snapshot["texts"][name] if name in snapshot["texts"] else tx.read(root, name) for name in names}
            require(all(old[name] is None for name in names - tx.text_names(registry)), "Registration plan target already exists")
            require(all(not tx.safe(root, name).exists() for name in additions), "Registration plan addition already exists")
            proposed = {name: value.decode() if value is not None else None for name, value in {**old, **changes}.items()}
            proposed[tx.RUNTIME] = tx.projection(proposed, new).decode()
            tx._stage_check(root, proposed, snapshot["retained"], additions)
            require(all(tx.read(root, name) == value for name, value in old.items()) and
                    all(tx.file_hash(root, name) == checksum for name, checksum in snapshot["retained"].items()), "Checkout changed during registration planning")
            planned_changes = [{"path": name, "operation": "add" if old[name] is None else "replace"}
                               for name in sorted(names) if old[name] != (proposed[name].encode() if proposed[name] is not None else None)]
            planned_changes.append({"path": added.path(entry["id"]), "operation": "add-on-success"})
        else:
            planned_changes = [{"path": name, "operation": "add" if journal["old"][name] is None else "replace"}
                               for name in sorted(journal["new"]) if journal["new"][name] != journal["old"][name]]
        plan = {"status": "planned-update" if update else "planned", "registered": False, "id": entry["id"], "category": category,
                "before": registry, "after": new, "changes": [{"path": package, "operation": "add"}] +
                planned_changes,
                "user_saves_modified": False}
        if update:
            plan.update(expected_definition_sha256=expected_definition_sha256, previous_runtime_revision=old_def["revision"],
                        runtime_revision=m["runtime_revision"], old_package_retained=existing["production"]["package"])
        if external: require(external[0].read_bytes() == external[1], "Checked difficulty input changed during planning")
        if not apply: return plan
        if checked is not None: checked.bind(root, journal, additions)
        tx.execute(root, journal, additions, fail_step=fail_step,
                   publication_seconds=publication_seconds, recovery_seconds=recovery_seconds,
                   **({"_verification": checked} if checked is not None else {}))
    return {**plan, "status": "updated" if update else "registered", "registered": True}
