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
CURRENT_FORMAT = "picross-integrated-content-v4"
FORMATS = (FORMAT, BACKGROUND_FORMAT, EDITOR_FORMAT, CURRENT_FORMAT)
INDEX = "content/authoring/index.json"
LIMIT = 8 * 1024 * 1024


def check(root, entry, receipt):
    """Validate the physical receipt and live authority, never removed inputs."""
    from . import categories, reveal_source
    original, notice, stored, _ = reveal_source.package(root, entry)
    require(stored is not None and canonical_bytes(stored) == canonical_bytes(receipt),
            "Integration receipt differs from the registered package")
    reveal_source.receipt(receipt, original, notice, background=True, editor=True)
    resolved = reveal_source.resolve(root, entry, categories.validate(io.json_bytes(io.read(root, categories.PATH, categories.MAX_BYTES), categories.MAX_BYTES)))
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


def _within(name, directory):
    return name == directory or name.startswith(directory + "/")


def _completed_selection(ids, revisions, work):
    """Explicit work ownership, never inferred from revision names or ID alone."""
    from .authoring_package import relative
    from .reveal_retirement import selection
    result = {identifier: {"revisions": set(), "work": set()} for identifier in ids}
    for values, kind in ((revisions, "revisions"), (work, "work")):
        values = [] if values is None else values
        require(isinstance(values, (list, tuple)), "Expected completed work pairs")
        for pair in values:
            require(isinstance(pair, (list, tuple)) and len(pair) == 2 and
                    all(isinstance(value, str) for value in pair), "Expected ID and completed work path")
            identifier, value = pair
            require(identifier in result, "Completed work belongs to an unselected production")
            if kind == "revisions":
                name = selection(identifier, value)
            else:
                relative(value)
                require(value.split("/")[0].casefold() != "current-view.json",
                        "Remove the verified completed current view separately")
                name = "content/authoring/" + identifier + "/" + value
            names = result[identifier][kind]
            folded = name.casefold()
            require(not any(_within(folded, other.casefold()) or _within(other.casefold(), folded)
                            for other in names), "Duplicate or overlapping completed work selection")
            names.add(name)
    return result


def retire(root, ids, integrated_commit, *, source_commits=None,
           completed_revisions=None, completed_work=None):
    from .retirement_scope import operation
    root = io.external(root)
    with operation(root) as reads:
        return _retire(root, ids, integrated_commit, reads, {} if source_commits is None else source_commits,
                       completed_revisions, completed_work)


def _retire(root, ids, integrated_commit, reads, source_commits, completed_revisions, completed_work):
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
    require(isinstance(ids, (list, tuple)) and ids and all(isinstance(i, str) for i in ids) and
            len(ids) == len(set(ids)), "Unknown/duplicate production IDs")
    for identifier in ids: reveal_source.path(identifier)
    completion = _completed_selection(ids, completed_revisions, completed_work)
    require(isinstance(source_commits, dict) and set(source_commits) <= set(ids), "Foreign source commit ID")
    for commit in source_commits.values():
        require(isinstance(commit,str) and re.fullmatch(r"[0-9a-f]{40}",commit), "Use full source commit")
        require(git("cat-file", "-t", commit).strip() == b"commit",
                "Source Git identity must be a commit object")
    from .retirement_scope import capture
    snapshot = capture(root, ids)
    live_dependencies = set(reads.data)
    current = snapshot["registry"]
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

    def historical_record(name):
        require(tree.get(name, ())[:2] == ("100644", "blob") and
                int(git("cat-file", "-s", integrated_commit + ":" + name)) <= 2 * 1024 * 1024,
                "Missing regular integrated authoring record: " + name)
        return io.json_bytes(git("show", integrated_commit + ":" + name), 2 * 1024 * 1024)
    # A later background adoption does not change the original completion
    # receipt. Its actual current bytes must nevertheless already be on main.
    main_commit = git("rev-parse", "origin/main").decode().strip()
    git("merge-base", "--is-ancestor", main_commit, "HEAD")
    main_tree = git_tree(main_commit)
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
        main_entry = next((e for e in main_registry["entries"] if e["id"] == identifier), None)
        require(main_entry is not None, "Selected production is absent from current main")
        comparable = deepcopy(main_entry)
        comparable["production"]["package_sha256"] = entry["production"]["package_sha256"]
        require(comparable == entry, "Selected entry differs from current main")
        require(next(r for r in current["metadata"] if r["id"] == identifier) ==
                next(r for r in main_registry["metadata"] if r["id"] == identifier), "Selected metadata differs from main")
        if identifier in current_backgrounds:
            require(backgrounds.index(main_registry).get(identifier) == current_backgrounds[identifier],
                    "Current background is not indexed on main")
        runtime = io.json_bytes(snapshot["texts"][registry.RUNTIME], LIMIT)
        require(next(r for r in runtime["entries"] if r["id"] == identifier) ==
                next(r for r in main_runtime["entries"] if r["id"] == identifier), "Selected runtime differs from main")
        prefix = entry["production"]["package"]
        revision = entry["production"]["revision"]
        require(prefix == "content/packages/" + identifier + "/" + revision, "Unexpected package path")
        old_entry, historical_notice, existing_receipt, package_dependencies = reveal_source.package(root, entry)
        require(canonical_bytes(old_entry) == canonical_bytes(old_entries[identifier]), "Production differs from integrated main entry")
        manifest = io.json_bytes(io.read(root, prefix + "/manifest.json", LIMIT), LIMIT)
        if manifest.get("format") in ("picross-editor-raster-package-v1", "picross-editor-raster-package-v2"):
            require(not any(completion[identifier].values()), "Editor raster authority has no production work to retire")
            # These are the live manual proof/decision authorities, not an
            # authoring export eligible for compaction into a receipt. Verify
            # the complete captured source view on main and retain it intact.
            for name in set(reads.data) | package_dependencies:
                committed(name, io.read(root, name, tx.file_limit(root, name), missing=True), main_tree)
            continue
        authoring = "content/authoring/" + identifier
        selected = selection(identifier, revision)
        current_rows = {name: row for name, row in rows.items() if row["puzzle_id"] == identifier}
        old_rows = {name: row for name, row in original_rows.items() if row["puzzle_id"] == identifier}
        extra_revisions, extra_work = completion[identifier]["revisions"], completion[identifier]["work"]
        require(selected not in extra_revisions, "Integrated revision is already selected")
        completed = {selected} | extra_revisions
        records = {}
        if extra_revisions:
            from .authoring_workflow import EARLY, LATE, RECORDS
            for directory in sorted(extra_revisions):
                require(directory in old_rows, "Completed revision is not indexed at integrated main: " + directory)
                record = historical_record(old_rows[directory]["record"])
                require(isinstance(record, dict) and record.get("format") in RECORDS and
                        record.get("puzzle_id") == identifier and
                        selection(identifier, record.get("revision")) == directory and
                        record.get("state") in EARLY + LATE + ("editorially_approved",) and
                        record.get("integration") is None and isinstance(record.get("blockers"), list),
                        "Not a completed prior production phase: " + directory)
                records[directory] = record
        expected_work = set()
        for name in sorted(extra_work):
            folded = name.casefold()
            require(not any(_within(folded, directory.casefold()) or _within(directory.casefold(), folded)
                            for directory in set(current_rows) | set(old_rows) | completed),
                    "Completed work overlaps an authoring revision: " + name)
            expected = {path for path in tree if _within(path, name)}
            require(expected and all(tree[path][:2] == ("100644", "blob") for path in expected),
                    "Completed work is not regular work at integrated main: " + name)
            require(not expected & live_dependencies, "Completed work is still an active source: " + name)
            expected_work.update(expected)
        bg = identifier in current_backgrounds
        siblings = (set(current_rows) | set(old_rows)) - completed
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
        require(all(any(name.startswith(directory + "/") for directory in current_rows) or
                    any(_within(name, path) for path in extra_work)
                    for name in authoring_files_all), "Unindexed authoring work prevents retirement: " + authoring)
        selected_rows = {name: row for name, row in current_rows.items() if name in completed}
        original_selected_rows = {name: row for name, row in old_rows.items() if name in completed}
        if existing_receipt is not None:
            if identifier in source_commits:
                require(existing_receipt.get("provenance", {}).get("source_commit") == source_commits[identifier],
                        "Already retired production has a different source proof")
            require(existing_receipt["integrated_commit"] == integrated_commit,
                    "Already retired production has a different main proof")
            require(not selected_rows and not any(io.safe(root, name).exists() for name in completed | extra_work),
                    "Retired production still has original authoring work: " + selected)
            scopes[prefix] = _tree(root, prefix)
            require(scopes[prefix][0] == {prefix + "/manifest.json"}, "Retired package has remaining work")
        else:
            require(selected_rows == original_selected_rows, "Unmerged authoring index changes: " + selected)
            scopes[prefix] = _tree(root, prefix, empty={prefix + "/external"} if bg else ())
            package_files, package_dirs = scopes[prefix]
            authoring_files = set()
            for directory in sorted(completed):
                scopes[directory] = _tree(root, directory)
                authoring_files.update(scopes[directory][0])
            for name in sorted(extra_work):
                path = io.safe(root, name)
                if name in tree:
                    require(path.is_file(), "Incomplete completed work file: " + name)
                    authoring_files.add(name)
                else:
                    scopes[name] = _tree(root, name)
                    require(path.is_dir(), "Incomplete completed work directory: " + name)
                    authoring_files.update(scopes[name][0])
            preserved = authoring_files_all - authoring_files
            authoring_dirs = {name for name in scopes[authoring][1]
                              if not any(_within(path, name) for path in preserved)}
            require(not io.safe(root, selected).exists() or selected_rows,
                    "Unindexed authoring work prevents retirement: " + selected)
            if selected in selected_rows:
                require(scopes[selected][0], "Incomplete original authoring revision: " + selected)
                record = io.json_bytes(io.read(root, selected_rows[selected]["record"], LIMIT), LIMIT)
                require(isinstance(record, dict) and record.get("format") in ("picross-authoring-record-v1", "picross-authoring-record-v2", "picross-authoring-record-v3", "picross-authoring-record-v4") and
                        record.get("puzzle_id") == identifier and record.get("revision") == revision and
                        record.get("state") == "registered" and record.get("blockers") == [],
                        "Authoring revision is not completed: " + selected)
                records[selected] = record
            names = package_files | authoring_files
            expected = {name for name in tree if name.startswith(prefix + "/") or
                        any(name.startswith(directory + "/") for directory in completed)} | expected_work
            require(names == expected, "Unmerged additions/deletions in production: " + identifier)
            archives = {directory + "/package.zip": record.get("package", {})
                        for directory, record in records.items()}
            for name in sorted(names):
                # Only the exact declared original archive receives its 128 MiB
                # allowance. Arbitrary catalog/authoring files remain at 64 MiB.
                limit = tx.file_limit(root, name)
                if name in archives:
                    package_ref = archives[name]
                    require(isinstance(package_ref, dict) and package_ref.get("file") == name,
                            "Unbound authoring archive")
                    limit = MAX_ZIP
                raw = io.read(root, name, limit)
                committed(name, raw)
                if name in archives:
                    require(package_ref.get("bytes") == len(raw) and package_ref.get("sha256") == io.checksum(raw),
                            "Authoring archive binding differs")
                removed[name] = (io.checksum(raw), len(raw), limit)
            source = backgrounds.load(root, current, entry) if bg else None
            from .editor_change import slim
            active_source = reveal_source.load(root, entry, catalog)
            modern = slim(source) or source is None and slim(active_source)
            editor_background = source is not None and source.get("format") == "picross-catalog-background-v5"
            receipt = {"format": EDITOR_FORMAT if editor_background else BACKGROUND_FORMAT if bg else FORMAT, "entry": deepcopy(entry),
                       "integrated_commit": integrated_commit, "notice_sha256": historical_notice}
            if modern:
                from .retirement_receipt import build
                receipt = build(root, entry, manifest, historical_notice, integrated_commit,
                                main_commit, source_commits.get(identifier, integrated_commit), git)
            elif bg:
                if editor_background:
                    manifest = io.json_bytes(io.read(root, prefix + "/manifest.json", LIMIT), LIMIT)
                    exported = (backgrounds.build(io.safe(root, prefix), manifest, None, entry)
                                if manifest.get("format") == "picross-target-export-v6" else None)
                    receipt["background"] = {"origin_sha256": backgrounds.origin_hash(source), "export_source": exported}
                else:
                    receipt["background"] = backgrounds.receipt_binding(source, current_backgrounds[identifier])
            reveal_source.receipt(receipt, entry, historical_notice, background=True, editor=True)
            plans.append((entry, prefix, completed, receipt, package_dirs, authoring_dirs, authoring_files))
        active_reveal = reveal_source.load(root, entry, catalog)
        is_editor_reveal = active_reveal is not None and active_reveal.get("format") in ("picross-catalog-reveal-v3", "picross-catalog-reveal-v4")
        source = backgrounds.load(root, current, entry) if bg else None
        editor_background = source is not None and source.get("format") == "picross-catalog-background-v5"
        from .editor_change import slim
        modern_background = slim(source)
        require(modern_background or (identifier in current_backgrounds) == (identifier in original_backgrounds) or
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
            if identifier in original_backgrounds and not modern_background:
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
    affected = sorted(set(reads.data) | {INDEX} | set(scopes))
    for start in range(0, len(affected), 20):
        git("diff", "--cached", "--quiet", "--", *affected[start:start + 20])
    require(all(tx.read(root, name) == raw for name, raw in snapshot["texts"].items()) and
            all(tx.file_hash(root, name) == checksum for name, checksum in snapshot["retained"].items()) and
            io.read(root, INDEX, LIMIT) == index_bytes,
            "Checkout sources changed during retirement planning")
    for directory, expected in scopes.items():
        require(_tree(root, directory, empty={directory + "/external"}) == expected,
                "Production namespace changed during retirement planning: " + directory)
    for name, (checksum, _, limit) in removed.items():
        require(io.file_hash(root, name, limit) == checksum, "Production bytes changed during retirement planning: " + name)
    reads.recheck()
    require(git("rev-parse", "origin/main").decode().strip() == main_commit, "Main changed during retirement")
    if not plans:
        return {"status": "no-op", "ids": ids, "integrated_commit": integrated_commit, "replaced_files": 0, "replaced_bytes": 0}

    registry.require_current(current)
    try:
        reads.acquire(ids, integrated_commit)
        for entry, prefix, completed, receipt, package_dirs, authoring_dirs, authoring_files in plans:
            # Individual checked paths only. A racing foreign file survives and
            # prevents directory removal; recursive deletion would erase it.
            for name, (checksum, _, limit) in removed.items():
                if (name.startswith(prefix + "/") and name != prefix + "/manifest.json") or name in authoring_files:
                    require(io.file_hash(root, name, limit) == checksum, "Production changed before deletion: " + name)
                    io.safe(root, name).unlink()
                    reads.forget(name)
            for directory in sorted(package_dirs | authoring_dirs, key=lambda name: len(name.split("/")), reverse=True):
                io.safe(root, directory).rmdir()
            authoring = "content/authoring/" + entry["id"]
            if io.safe(root, authoring).exists() and not any(io.safe(root, authoring).iterdir()):
                io.safe(root, authoring).rmdir()
            manifest = prefix + "/manifest.json"
            checksum, _, limit = removed[manifest]
            require(_tree(root, prefix) == ({manifest}, set()) and io.file_hash(root, manifest, limit) == checksum,
                    "Package manifest/namespace changed before receipt replacement: " + prefix)
            raw = canonical_bytes(receipt) + b"\n"
            registry.atomic_bytes(io.safe(root, manifest), raw)
            reads.forget(manifest)
            entry["production"]["package_sha256"] = io.checksum(raw)
        completed = set().union(*(plan[2] for plan in plans))
        index["entries"] = [row for row in index["entries"] if selection(row["puzzle_id"], row["revision"]) not in completed]
        updated_index = canonical_bytes(index) + b"\n"
        require(io.read(root, INDEX, LIMIT) == index_bytes, "Authoring index changed before retirement replacement")
        if updated_index != index_bytes:
            registry.atomic_bytes(io.safe(root, INDEX), updated_index)
            reads.forget(INDEX)
        require(tx.read(root, registry.REGISTRY) == snapshot["texts"][registry.REGISTRY],
                "Registry changed before retirement replacement")
        registry.atomic_bytes(io.safe(root, registry.REGISTRY), canonical_bytes(current) + b"\n")
        reads.forget(registry.REGISTRY)
        capture(root, ids)
        reads.recheck()
        reads.release()
    except (Exception, KeyboardInterrupt) as exc:
        # This command deliberately supplies no synthetic rollback or old ZIP
        # reconstruction. Leave the actual reviewable remnants and name them.
        remaining = []
        for name in sorted(set(scopes) | {INDEX, registry.REGISTRY, tx.LOCK}):
            try:
                if (root / name).exists(): remaining.append(str(root / name))
            except OSError:
                remaining.append(str(root / name) + " (unreadable)")
        message = "Production retirement did not complete: " + (str(exc) or "interrupted") + "; remaining paths: " + ", ".join(remaining)
        if isinstance(exc, (Aborted, KeyboardInterrupt)): raise Aborted(message) from exc
        raise InvalidInput(message) from exc
    return {"status": "production_retired", "ids": ids, "integrated_commit": integrated_commit,
            "replaced_files": len(removed), "replaced_bytes": sum(size for _, size, _ in removed.values())}
