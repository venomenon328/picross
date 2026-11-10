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
FORMATS = (FORMAT, BACKGROUND_FORMAT)
INDEX = "content/authoring/index.json"
LIMIT = 8 * 1024 * 1024


def check(root, entry, receipt):
    """Validate the physical receipt and live authority, never removed inputs."""
    from . import categories, reveal_source
    original, notice, stored, _ = reveal_source.package(root, entry)
    require(stored is not None and canonical_bytes(stored) == canonical_bytes(receipt),
            "Integration receipt differs from the registered package")
    reveal_source.receipt(receipt, original, notice, background=True)
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
    tree = {}
    for item in git("ls-tree", "-rz", integrated_commit).split(b"\0"):
        if item:
            meta, name = item.split(b"\t", 1)
            mode, kind, oid = meta.decode().split()
            tree[name.decode("utf-8")] = (mode, kind, oid)

    def committed(name, raw):
        if raw is None:
            require(name not in tree, "Missing integrated source: " + name)
        else:
            require(tree.get(name) == ("100644", "blob", blob_id(raw)), "Unmerged or modified production file: " + name)
            if os.name != "nt":
                require(not io.safe(root, name).stat().st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH),
                        "Production file mode changed: " + name)

    retained, removed, plans, scopes = set(), {}, [], {}
    current_backgrounds, original_backgrounds = backgrounds.index(current), backgrounds.index(original)
    for identifier in ids:
        entry = by_id[identifier]
        prefix = entry["production"]["package"]
        revision = entry["production"]["revision"]
        require(prefix == "content/packages/" + identifier + "/" + revision, "Unexpected package path")
        old_entry, historical_notice, existing_receipt, _ = reveal_source.package(root, entry)
        require(canonical_bytes(old_entry) == canonical_bytes(old_entries[identifier]), "Production differs from integrated main entry")
        authoring = "content/authoring/" + identifier
        selected = selection(identifier, revision)
        current_rows = {name: row for name, row in rows.items() if row["puzzle_id"] == identifier}
        old_rows = {name: row for name, row in original_rows.items() if row["puzzle_id"] == identifier}
        require(set(old_rows) <= {selected}, "Other authoring revisions need a separate completion decision: " + authoring)
        if existing_receipt is not None:
            require(existing_receipt["integrated_commit"] == integrated_commit,
                    "Already retired production has a different main proof")
            require(not current_rows and not io.safe(root, authoring).exists(),
                    "Retired production still has authoring work: " + authoring)
            scopes[prefix] = _tree(root, prefix)
            require(scopes[prefix][0] == {prefix + "/manifest.json"}, "Retired package has remaining work")
        else:
            require(current_rows == old_rows, "Unmerged authoring index changes: " + authoring)
            bg = identifier in current_backgrounds
            scopes[prefix] = _tree(root, prefix, empty={prefix + "/external"} if bg else ())
            scopes[authoring] = _tree(root, authoring)
            package_files, package_dirs = scopes[prefix]
            authoring_files, authoring_dirs = scopes[authoring]
            require(not io.safe(root, authoring).exists() or current_rows,
                    "Unindexed authoring work prevents retirement: " + authoring)
            if current_rows:
                require(authoring_files and all(name.startswith(selected + "/") for name in authoring_files) and
                        authoring_dirs <= {selected} | {str(p) for n in authoring_files for p in PurePosixPath(n).parents},
                        "Unknown/open authoring siblings prevent retirement: " + authoring)
                record = io.json_bytes(io.read(root, current_rows[selected]["record"], LIMIT), LIMIT)
                require(isinstance(record, dict) and record.get("format") in ("picross-authoring-record-v1", "picross-authoring-record-v2") and
                        record.get("puzzle_id") == identifier and record.get("revision") == revision and
                        record.get("state") == "registered" and record.get("blockers") == [],
                        "Authoring revision is not completed: " + selected)
            names = package_files | authoring_files
            expected = {name for name in tree if name.startswith(prefix + "/") or name.startswith(authoring + "/")}
            require(names == expected, "Unmerged additions/deletions in production: " + identifier)
            for name in sorted(names):
                # Only the exact declared original archive receives its 128 MiB
                # allowance. Arbitrary catalog/authoring files remain at 64 MiB.
                limit = tx.file_limit(root, name)
                if current_rows and name == selected + "/package.zip":
                    package_ref = record.get("package", {})
                    require(isinstance(package_ref, dict) and package_ref.get("file") == name,
                            "Unbound authoring archive")
                    limit = MAX_ZIP
                raw = io.read(root, name, limit)
                committed(name, raw)
                if current_rows and name == selected + "/package.zip":
                    require(package_ref.get("bytes") == len(raw) and package_ref.get("sha256") == io.checksum(raw),
                            "Authoring archive binding differs")
                removed[name] = (io.checksum(raw), len(raw), limit)
            receipt = {"format": BACKGROUND_FORMAT if bg else FORMAT, "entry": deepcopy(entry),
                       "integrated_commit": integrated_commit, "notice_sha256": historical_notice}
            if bg:
                source = backgrounds.load(root, current, entry)
                receipt["background"] = backgrounds.receipt_binding(source, current_backgrounds[identifier])
            reveal_source.receipt(receipt, entry, historical_notice, background=True)
            plans.append((entry, prefix, authoring, receipt, package_dirs, authoring_dirs))
        require(current_backgrounds.get(identifier) == original_backgrounds.get(identifier),
                "Background index differs from integrated main")
        retained.update(("game/" + entry["definition"], "game/" + entry["reveal"], reveal_source.identity(entry)["notice"],
                         reveal_source.path(identifier), catalog_rating.path(identifier), catalog_added.path(identifier)))
        if identifier in current_backgrounds:
            retained.update((backgrounds.CAPABILITY, backgrounds.path(identifier),
                             backgrounds.asset_path(identifier), backgrounds.notice_path(identifier)))
        resolved = reveal_source.resolve(root, entry, catalog)
        require(resolved["historical_notice_sha256"] == historical_notice, "Historical notice changed during retirement")

    for name in sorted(retained):
        committed(name, io.read(root, name, tx.file_limit(root, name), missing=True))
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

    try:
        for entry, prefix, authoring, receipt, package_dirs, authoring_dirs in plans:
            # Individual checked paths only. A racing foreign file survives and
            # prevents directory removal; recursive deletion would erase it.
            for name, (checksum, _, limit) in removed.items():
                if (name.startswith(prefix + "/") and name != prefix + "/manifest.json") or name.startswith(authoring + "/"):
                    require(io.file_hash(root, name, limit) == checksum, "Production changed before deletion: " + name)
                    io.safe(root, name).unlink()
            for directory in sorted(package_dirs | authoring_dirs, key=lambda name: len(name.split("/")), reverse=True):
                io.safe(root, directory).rmdir()
            if io.safe(root, authoring).exists(): io.safe(root, authoring).rmdir()
            manifest = prefix + "/manifest.json"
            checksum, _, limit = removed[manifest]
            require(_tree(root, prefix) == ({manifest}, set()) and io.file_hash(root, manifest, limit) == checksum,
                    "Package manifest/namespace changed before receipt replacement: " + prefix)
            raw = canonical_bytes(receipt) + b"\n"
            registry.atomic_bytes(io.safe(root, manifest), raw)
            entry["production"]["package_sha256"] = io.checksum(raw)
        index["entries"] = [row for row in index["entries"] if row["puzzle_id"] not in ids]
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
