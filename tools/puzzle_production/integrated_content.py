"""Compact receipts for completed production; never an export/certification input."""
from copy import deepcopy
import os
from pathlib import PurePosixPath
import re
import stat
import subprocess

from . import catalog_io as io
from .authoring_package import require, MAX_ZIP
from .contract import Aborted, canonical_bytes, InvalidInput

FORMAT = "picross-integrated-content-v1"
BACKGROUND_FORMAT = "picross-integrated-content-v2"
EDITOR_FORMAT = "picross-integrated-content-v3"
FORMATS = (FORMAT, BACKGROUND_FORMAT, EDITOR_FORMAT)
INDEX = "content/authoring/index.json"
LIMIT = 8 * 1024 * 1024


def check(root, entry, receipt):
    """Validate the physical receipt and live authority, never removed inputs."""
    from . import categories, reveal_source
    original, notice, stored, _ = reveal_source.package(root, entry)
    require(stored is not None and canonical_bytes(stored) == canonical_bytes(receipt),
            "Integration receipt differs from the registered package")
    reveal_source.receipt(receipt, original, notice, background=True, editor=True)
    resolved = reveal_source.resolve(root, entry, categories.load(root / categories.PATH))
    require(resolved["historical_notice_sha256"] == notice, "Historical player notice differs")


def _tree(root, directory, *, empty=()):
    """Read an owned namespace, retaining directory identities for preflight."""
    base = io.safe(root, directory)
    if not base.exists():
        return set(), set()
    require(base.is_dir(), "Production scope is not a directory: " + directory)
    files, directories = set(), set()
    for child in base.rglob("*"):
        name = child.relative_to(root).as_posix()
        child = io.safe(root, name)
        if child.is_file(): files.add(name)
        else: directories.add(name)
    parents = {str(parent) for name in files for parent in PurePosixPath(name).parents}
    require(directories <= parents | set(empty), "Unknown empty production directory: " + directory)
    return files, directories


def retire(root, ids, integrated_commit):
    """Prepare a local diff after the whole selected production reached main.

    Git tree identities bind current bytes. Already retired sources use their
    compact receipt and live files; no historical ZIP or proof is reconstructed.
    """
    from . import catalog_background as backgrounds, catalog_transaction as tx
    from . import catalog_added, catalog_rating, categories, content_registry as registry, reveal_source
    from .reveal_retirement import blob_id, index_rows, selection
    root = io.external(root)

    def git(*args):
        result = subprocess.run(["git", *args], cwd=root, capture_output=True)
        require(result.returncode == 0, "Cannot verify integration source: " + result.stderr.decode(errors="replace").strip())
        return result.stdout

    require(root == io.external(git("rev-parse", "--show-toplevel").decode().strip()), "Use the checkout root")
    require(isinstance(integrated_commit, str) and re.fullmatch(r"[0-9a-f]{40}", integrated_commit),
            "Use the full verified main commit")
    # Refreshing origin/main belongs to the workflow. No network or Git writes.
    for ref in ("origin/main", "HEAD"):
        git("merge-base", "--is-ancestor", integrated_commit, ref)
    snapshot = tx.capture(root)
    current = snapshot["registry"]
    require(isinstance(ids, (list, tuple)) and ids and all(isinstance(i, str) for i in ids) and
            len(ids) == len(set(ids)), "Unknown/duplicate production IDs")
    for identifier in ids: reveal_source.path(identifier)
    catalog = io.json_bytes(snapshot["texts"][categories.PATH], 131072)
    old_catalog = categories.validate(io.json_bytes(git("show", integrated_commit + ":" + categories.PATH), 131072))
    original = registry.validate(io.json_bytes(git("show", integrated_commit + ":" + registry.REGISTRY), LIMIT), old_catalog)
    old_entries = {entry["id"]: entry for entry in original["entries"]}
    by_id = {entry["id"]: entry for entry in current["entries"]}
    require(set(ids) <= by_id.keys() and set(ids) <= old_entries.keys(), "Production is not integrated on main")
    index_bytes = io.read(root, INDEX, LIMIT)
    index = io.json_bytes(index_bytes, LIMIT)
    rows = index_rows(index)
    original_rows = index_rows(io.json_bytes(git("show", integrated_commit + ":" + INDEX), LIMIT))
    def git_tree(commit):
        result = {}
        for item in git("ls-tree", "-rz", commit).split(b"\0"):
            if item:
                meta, name = item.split(b"\t", 1)
                result[name.decode("utf-8")] = tuple(meta.decode().split())
        return result

    tree = git_tree(integrated_commit)
    # A later background adoption does not change the original completion
    # receipt. Its actual current bytes must nevertheless already be on main.
    main_tree = git_tree("origin/main")
    main_catalog = categories.validate(io.json_bytes(git("show", "origin/main:" + categories.PATH), 131072))
    main_registry = registry.validate(io.json_bytes(git("show", "origin/main:" + registry.REGISTRY), LIMIT), main_catalog)
    main_runtime = io.json_bytes(git("show", "origin/main:" + registry.RUNTIME), LIMIT)

    def committed(name, raw, expected_tree=None):
        expected_tree = tree if expected_tree is None else expected_tree
        if raw is None:
            require(name not in expected_tree, "Missing integrated source: " + name)
        else:
            require(expected_tree.get(name) == ("100644", "blob", blob_id(raw)), "Unmerged or modified production file: " + name)
            if os.name != "nt":
                require(not io.safe(root, name).stat().st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH),
                        "Production file mode changed: " + name)

    retained, main_retained, removed, plans, scopes = set(), set(), {}, [], {}
    current_backgrounds, original_backgrounds = backgrounds.index(current), backgrounds.index(original)
    for identifier in ids:
        entry = by_id[identifier]
        prefix = entry["production"]["package"]
        revision = entry["production"]["revision"]
        require(prefix == "content/packages/" + identifier + "/" + revision, "Unexpected package path")
        old_entry, historical_notice, existing_receipt, _ = reveal_source.package(root, entry)
        require(canonical_bytes(old_entry) == canonical_bytes(old_entries[identifier]), "Production differs from integrated main entry")
        manifest = io.json_bytes(io.read(root, prefix + "/manifest.json", LIMIT), LIMIT)
        if manifest.get("format") == "picross-editor-raster-package-v1":
            # These are the live manual proof/decision authorities, not an
            # authoring export eligible for compaction into a receipt. Verify
            # the complete captured source view on main and retain it intact.
            for name in set(snapshot["texts"]) | set(snapshot["retained"]):
                committed(name, io.read(root, name, tx.file_limit(root, name), missing=True), main_tree)
            continue
        authoring = "content/authoring/" + identifier
        selected = selection(identifier, revision)
        current_rows = {name: row for name, row in rows.items() if row["puzzle_id"] == identifier}
        old_rows = {name: row for name, row in original_rows.items() if row["puzzle_id"] == identifier}
        bg = identifier in current_backgrounds
        siblings = (set(current_rows) | set(old_rows)) - {selected}
        if siblings:
            require(bg, "Other authoring revisions need a separate completion decision: " + authoring)
            from .background_request import validate as validate_request
            for name in sorted(siblings):
                for selected_rows, historical in ((current_rows, False), (old_rows, True)):
                    if name not in selected_rows: continue
                    record_path = selected_rows[name]["record"]
                    if historical:
                        require(tree.get(record_path, ())[:2] == ("100644", "blob") and
                                int(git("cat-file", "-s", integrated_commit + ":" + record_path)) <= 2 * 1024 * 1024,
                                "Other authoring revisions need a separate completion decision: " + name)
                        raw = git("show", integrated_commit + ":" + record_path)
                    else:
                        raw = io.read(root, record_path, 2 * 1024 * 1024)
                    record = io.json_bytes(raw, 2 * 1024 * 1024)
                    require(isinstance(record, dict) and record.get("format") in ("picross-background-adoption-request-v1", "picross-background-adoption-request-v2"),
                            "Other authoring revisions need a separate completion decision: " + name)
                    record = validate_request(record)
                    require(selection(record["puzzle_id"], record["revision"]) == name,
                            "Background authoring sibling has the wrong identity")
        # Preserve explicitly indexed background jobs, including newer/open
        # ones. Unknown families or unindexed siblings remain a concrete block.
        scopes[authoring] = _tree(root, authoring)
        authoring_files_all, _ = scopes[authoring]
        require(not io.safe(root, authoring).exists() or current_rows or bg and not any(scopes[authoring]),
                "Unindexed authoring work prevents retirement: " + authoring)
        require(all(any(name.startswith(directory + "/") for directory in current_rows)
                    for name in authoring_files_all), "Unindexed authoring work prevents retirement: " + authoring)
        selected_rows = {name: row for name, row in current_rows.items() if name == selected}
        original_selected_rows = {name: row for name, row in old_rows.items() if name == selected}
        if existing_receipt is not None:
            require(existing_receipt["integrated_commit"] == integrated_commit,
                    "Already retired production has a different main proof")
            require(not selected_rows and not io.safe(root, selected).exists(),
                    "Retired production still has original authoring work: " + selected)
            scopes[prefix] = _tree(root, prefix)
            require(scopes[prefix][0] == {prefix + "/manifest.json"}, "Retired package has remaining work")
        else:
            require(selected_rows == original_selected_rows, "Unmerged authoring index changes: " + selected)
            scopes[prefix] = _tree(root, prefix, empty={prefix + "/external"} if bg else ())
            scopes[selected] = _tree(root, selected)
            package_files, package_dirs = scopes[prefix]
            authoring_files, authoring_dirs = scopes[selected]
            require(not io.safe(root, selected).exists() or selected_rows,
                    "Unindexed authoring work prevents retirement: " + selected)
            if selected_rows:
                require(authoring_files, "Incomplete original authoring revision: " + selected)
                record = io.json_bytes(io.read(root, selected_rows[selected]["record"], LIMIT), LIMIT)
                require(isinstance(record, dict) and record.get("format") in ("picross-authoring-record-v1", "picross-authoring-record-v2", "picross-authoring-record-v3") and
                        record.get("puzzle_id") == identifier and record.get("revision") == revision and
                        record.get("state") == "registered" and record.get("blockers") == [],
                        "Authoring revision is not completed: " + selected)
            names = package_files | authoring_files
            expected = {name for name in tree if name.startswith(prefix + "/") or name.startswith(selected + "/")}
            require(names == expected, "Unmerged additions/deletions in production: " + identifier)
            for name in sorted(names):
                # Only the exact declared original archive receives its 128 MiB
                # allowance. Arbitrary catalog/authoring files remain at 64 MiB.
                limit = tx.file_limit(root, name)
                if selected_rows and name == selected + "/package.zip":
                    package_ref = record.get("package", {})
                    require(isinstance(package_ref, dict) and package_ref.get("file") == name,
                            "Unbound authoring archive")
                    limit = MAX_ZIP
                raw = io.read(root, name, limit)
                committed(name, raw)
                if selected_rows and name == selected + "/package.zip":
                    require(package_ref.get("bytes") == len(raw) and package_ref.get("sha256") == io.checksum(raw),
                            "Authoring archive binding differs")
                removed[name] = (io.checksum(raw), len(raw), limit)
            source = backgrounds.load(root, current, entry) if bg else None
            editor_background = source is not None and source.get("format") == "picross-catalog-background-v5"
            receipt = {"format": EDITOR_FORMAT if editor_background else BACKGROUND_FORMAT if bg else FORMAT, "entry": deepcopy(entry),
                       "integrated_commit": integrated_commit, "notice_sha256": historical_notice}
            if bg:
                if editor_background:
                    manifest = io.json_bytes(io.read(root, prefix + "/manifest.json", LIMIT), LIMIT)
                    exported = (backgrounds.build(io.safe(root, prefix), manifest, None, entry)
                                if manifest.get("format") == "picross-target-export-v6" else None)
                    receipt["background"] = {"origin_sha256": backgrounds.origin_hash(source), "export_source": exported}
                else:
                    receipt["background"] = backgrounds.receipt_binding(source, current_backgrounds[identifier])
            reveal_source.receipt(receipt, entry, historical_notice, background=True, editor=True)
            plans.append((entry, prefix, selected, receipt, package_dirs, authoring_dirs))
        active_reveal = reveal_source.load(root, entry, catalog)
        is_editor_reveal = active_reveal is not None and active_reveal.get("format") == "picross-catalog-reveal-v3"
        source = backgrounds.load(root, current, entry) if bg else None
        editor_background = source is not None and source.get("format") == "picross-catalog-background-v5"
        require((identifier in current_backgrounds) == (identifier in original_backgrounds) or
                editor_background and identifier not in original_backgrounds and source["origin"]["source"] is None and
                source["origin"]["entry"] == old_entry,
                "Background index membership differs from integrated main")
        retained.update(("game/" + entry["definition"], catalog_rating.path(identifier), catalog_added.path(identifier)))
        if is_editor_reveal:
            main_retained.update((active_reveal["current"]["asset"]["file"], reveal_source.identity(entry)["notice"], reveal_source.path(identifier)))
        else:
            retained.update(("game/" + entry["reveal"], reveal_source.identity(entry)["notice"], reveal_source.path(identifier)))
        if identifier in current_backgrounds:
            source = backgrounds.load(root, current, entry)
            require(backgrounds.index(main_registry).get(identifier) == current_backgrounds[identifier],
                    "Current background is not indexed on main")
            main_formats = ((registry.METADATA_RUNTIME_FORMAT, registry.IMAGE_RUNTIME_FORMAT) if main_registry["format"] == registry.METADATA_FORMAT
                           else (backgrounds.RUNTIME_FORMAT,))
            require(isinstance(main_runtime, dict) and main_runtime.get("format") in main_formats and
                    isinstance(main_runtime.get("entries"), list), "Current background runtime is not on main")
            matches = [row for row in main_runtime["entries"] if isinstance(row, dict) and row.get("id") == identifier]
            minimal = {"format": main_registry["format"], "entries": [entry],
                       "backgrounds": [{"id": identifier, "source": current_backgrounds[identifier]}]}
            if main_registry["format"] == registry.METADATA_FORMAT:
                active_metadata = registry.current_metadata(main_registry, main_catalog)[identifier]
                minimal["metadata"] = [active_metadata]
            expected_projection = backgrounds.projection(minimal,
                {backgrounds.path(identifier): backgrounds.encoded(source)})[identifier]
            require(len(matches) == 1 and matches[0].get("background") == expected_projection,
                    "Current background runtime differs from main")
            if main_registry["format"] == registry.METADATA_FORMAT:
                require(all(matches[0].get(key) == active_metadata[key] for key in ("name", "category_id")),
                        "Current background runtime metadata differs from main")
            if identifier in original_backgrounds:
                old_ref = original_backgrounds[identifier]
                require(tree.get(old_ref["file"], ())[:2] == ("100644", "blob") and
                        int(git("cat-file", "-s", integrated_commit + ":" + old_ref["file"])) <= backgrounds.LIMIT,
                        "Missing bounded original background source on main")
                old_raw = git("show", integrated_commit + ":" + old_ref["file"])
                old_source = backgrounds.validate(io.json_bytes(old_raw, backgrounds.LIMIT), old_entries[identifier])
                require(backgrounds.ref(old_ref["file"], old_raw) == old_ref and old_raw == backgrounds.encoded(old_source) and
                        (source["origin"] == old_source["origin"] if editor_background and old_source.get("format") == "picross-catalog-background-v5"
                         else backgrounds.initial(source) == backgrounds.initial(old_source)),
                        "Original background authority differs from integrated main")
            main_retained.update((backgrounds.CAPABILITY, backgrounds.path(identifier),
                                  backgrounds.asset_path(identifier), backgrounds.notice_path(identifier)))
        resolved = reveal_source.resolve(root, entry, catalog)
        require(resolved["historical_notice_sha256"] == historical_notice, "Historical notice changed during retirement")

    for name in sorted(retained):
        committed(name, io.read(root, name, tx.file_limit(root, name), missing=True))
    for name in sorted(main_retained):
        committed(name, io.read(root, name, tx.file_limit(root, name), missing=True), main_tree)
    affected = sorted(set(snapshot["texts"]) | set(snapshot["retained"]) | {INDEX} | set(scopes))
    for start in range(0, len(affected), 20):
        git("diff", "--cached", "--quiet", "--", *affected[start:start + 20])
    require(all(tx.read(root, name) == raw for name, raw in snapshot["texts"].items()) and
            all(tx.file_hash(root, name) == checksum for name, checksum in snapshot["retained"].items()) and
            tx.namespaces(root, current) == snapshot["namespaces"] and io.read(root, INDEX, LIMIT) == index_bytes,
            "Checkout sources changed during retirement planning")
    for directory, expected in scopes.items():
        require(_tree(root, directory, empty={directory + "/external"}) == expected,
                "Production namespace changed during retirement planning: " + directory)
    for name, (checksum, _, limit) in removed.items():
        require(io.file_hash(root, name, limit) == checksum, "Production bytes changed during retirement planning: " + name)
    if not plans:
        return {"status": "no-op", "ids": ids, "integrated_commit": integrated_commit, "replaced_files": 0, "replaced_bytes": 0}

    registry.require_current(current)
    try:
        for entry, prefix, selected, receipt, package_dirs, authoring_dirs in plans:
            # Individual checked paths only. A racing foreign file survives and
            # prevents directory removal; recursive deletion would erase it.
            for name, (checksum, _, limit) in removed.items():
                if (name.startswith(prefix + "/") and name != prefix + "/manifest.json") or name.startswith(selected + "/"):
                    require(io.file_hash(root, name, limit) == checksum, "Production changed before deletion: " + name)
                    io.safe(root, name).unlink()
            for directory in sorted(package_dirs | authoring_dirs, key=lambda name: len(name.split("/")), reverse=True):
                io.safe(root, directory).rmdir()
            if io.safe(root, selected).exists():
                io.safe(root, selected).rmdir()
                authoring = str(PurePosixPath(selected).parent)
                if not any(io.safe(root, authoring).iterdir()): io.safe(root, authoring).rmdir()
            manifest = prefix + "/manifest.json"
            checksum, _, limit = removed[manifest]
            require(_tree(root, prefix) == ({manifest}, set()) and io.file_hash(root, manifest, limit) == checksum,
                    "Package manifest/namespace changed before receipt replacement: " + prefix)
            raw = canonical_bytes(receipt) + b"\n"
            registry.atomic_bytes(io.safe(root, manifest), raw)
            entry["production"]["package_sha256"] = io.checksum(raw)
        completed = {plan[2] for plan in plans}
        index["entries"] = [row for row in index["entries"] if selection(row["puzzle_id"], row["revision"]) not in completed]
        updated_index = canonical_bytes(index) + b"\n"
        require(io.read(root, INDEX, LIMIT) == index_bytes, "Authoring index changed before retirement replacement")
        if updated_index != index_bytes: registry.atomic_bytes(io.safe(root, INDEX), updated_index)
        require(tx.read(root, registry.REGISTRY) == snapshot["texts"][registry.REGISTRY],
                "Registry changed before retirement replacement")
        registry.atomic_bytes(io.safe(root, registry.REGISTRY), canonical_bytes(current) + b"\n")
        registry.check_checkout(root)
    except (Exception, KeyboardInterrupt) as exc:
        # This command deliberately supplies no synthetic rollback or old ZIP
        # reconstruction. Leave the actual reviewable remnants and name them.
        remaining = []
        for name in sorted(set(scopes) | {INDEX, registry.REGISTRY}):
            try:
                if (root / name).exists(): remaining.append(str(root / name))
            except OSError:
                remaining.append(str(root / name) + " (unreadable)")
        message = "Production retirement did not complete: " + (str(exc) or "interrupted") + "; remaining paths: " + ", ".join(remaining)
        if isinstance(exc, (Aborted, KeyboardInterrupt)): raise Aborted(message) from exc
        raise InvalidInput(message) from exc
    return {"status": "production_retired", "ids": ids, "integrated_commit": integrated_commit,
            "replaced_files": len(removed), "replaced_bytes": sum(size for _, size, _ in removed.values())}
