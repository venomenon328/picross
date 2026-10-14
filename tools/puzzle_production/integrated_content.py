"""Compact receipts for completed production; never an export/certification input."""
from copy import deepcopy
import json
import re
import shutil
import subprocess

from .authoring_package import require, file_hash, sha, file_table
from .contract import exact_keys, load_json, write_json

FORMAT = "picross-integrated-content-v1"


def check(root, entry, receipt):
    exact_keys(receipt, {"format", "entry", "integrated_commit", "notice_sha256"})
    require(receipt["format"] == FORMAT and isinstance(receipt["integrated_commit"], str)
            and re.fullmatch(r"[0-9a-f]{40}", receipt["integrated_commit"]), "Invalid integration receipt")
    require(isinstance(receipt["entry"], dict) and isinstance(receipt["entry"].get("production"), dict)
            and "package_sha256" in receipt["entry"]["production"], "Invalid integration receipt entry")
    original = deepcopy(entry)
    original["production"]["package_sha256"] = receipt["entry"]["production"]["package_sha256"]
    sha(original["production"]["package_sha256"])
    require(receipt["entry"] == original, "Integrated receipt identity/category differs")
    notice = (root / "game" / entry["reveal"]).with_suffix(".txt")
    require(file_hash(notice) == sha(receipt["notice_sha256"]), "Player notice differs")


def retire(root, ids, integrated_commit):
    """Prepare a reviewable Git diff only after the exact inputs reached main."""
    from . import content_registry as registry
    root = root.resolve()

    def git(*args):
        result = subprocess.run(["git", *args], cwd=root, capture_output=True)
        require(result.returncode == 0, "Cannot verify integration source: " + result.stderr.decode(errors="replace").strip())
        return result.stdout

    require(isinstance(integrated_commit, str) and re.fullmatch(r"[0-9a-f]{40}", integrated_commit),
            "Use the full verified main commit")
    # The workflow refreshes origin/main before this command. A local draft is insufficient.
    require(subprocess.run(["git", "merge-base", "--is-ancestor", integrated_commit, "origin/main"],
                           cwd=root, capture_output=True).returncode == 0, "Integration is not on origin/main")
    current = registry.check_checkout(root)
    original = json.loads(git("show", integrated_commit + ":" + registry.REGISTRY))
    old_entries = {e["id"]: e for e in original["entries"]}
    by_id = {e["id"]: e for e in current["entries"]}
    require(ids and len(ids) == len(set(ids)) and set(ids) <= by_id.keys(), "Unknown/duplicate production IDs")
    index_path = root / "content/authoring/index.json"
    index = load_json(index_path)
    original_index = json.loads(git("show", integrated_commit+":content/authoring/index.json"))
    require([e for e in index["entries"] if e["puzzle_id"] in ids] ==
            [e for e in original_index["entries"] if e["puzzle_id"] in ids], "Unmerged authoring index changes")
    plans = []
    # Preflight every selected ID before deleting anything. No production replay.
    for id in ids:
        entry = by_id[id]
        require(entry == old_entries.get(id), "Production differs from integrated main entry")
        package = root / entry["production"]["package"]
        require(package == root / "content/packages" / id / entry["production"]["revision"], "Unexpected package path")
        manifest = load_json(package / "manifest.json")
        require(manifest.get("format") != FORMAT, "Production already retired")
        package_files = file_table(package, float("inf"))
        authoring = root / "content/authoring" / id
        files = {p.relative_to(root).as_posix(): p for p in package_files.values()}
        if authoring.exists():
            files.update({p.relative_to(root).as_posix(): p for p in file_table(authoring, float("inf")).values()})
        original_files = git("ls-tree", "-rz", "--name-only", integrated_commit, "--",
                             str(package.relative_to(root)), str(authoring.relative_to(root)))
        require(set(files) == set(original_files.decode().rstrip("\0").split("\0")),
                "Unmerged additions/deletions in production: " + id)
        for name in ["game/"+entry["definition"], "game/"+entry["reveal"],
                     str((root/"game"/entry["reveal"]).with_suffix(".txt").relative_to(root)), *files]:
            require((root/name).read_bytes() == git("show", integrated_commit+":"+name),
                    "Unmerged or modified production file: " + name)
        receipt = {"format": FORMAT, "entry": deepcopy(entry), "integrated_commit": integrated_commit,
                   "notice_sha256": file_hash((root/"game"/entry["reveal"]).with_suffix(".txt"))}
        plans.append((entry, package, authoring, receipt, len(files), sum(p.stat().st_size for p in files.values())))
    affected = [registry.REGISTRY, str(index_path.relative_to(root))]
    for _, package, authoring, _, _, _ in plans:
        affected.extend([str(package.relative_to(root)), str(authoring.relative_to(root))])
    require(subprocess.run(["git", "diff", "--cached", "--quiet", "--", *affected],
                           cwd=root, capture_output=True).returncode == 0,
            "Staged production changes must be resolved before retirement")
    for entry, package, authoring, receipt, _, _ in plans:
        # Runtime files and projection are never rewritten. Git retains the prior production.
        shutil.rmtree(package)
        package.mkdir(parents=True)
        write_json(package/"manifest.json", receipt)
        entry["production"]["package_sha256"] = file_hash(package/"manifest.json")
        if authoring.exists():
            shutil.rmtree(authoring)
    index["entries"] = [e for e in index["entries"] if e["puzzle_id"] not in ids]
    write_json(index_path, index)
    write_json(root/registry.REGISTRY, current)
    registry.check_checkout(root)
    return {"status": "production_retired", "ids": ids, "integrated_commit": integrated_commit,
            "replaced_files": sum(p[4] for p in plans), "replaced_bytes": sum(p[5] for p in plans)}
