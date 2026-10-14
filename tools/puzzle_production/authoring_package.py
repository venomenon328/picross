"""Bounded, read-only Authoring v2 boundary. Package text/code is never executed."""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import os
import hashlib
from pathlib import Path
import re
import stat
import tempfile
import time
import zipfile

from .contract import Aborted, InvalidInput, exact_keys, integer, load_json


def file_hash(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

MAX_FILES = 2048
MAX_FILE = 64 * 1024 * 1024
MAX_TOTAL = 512 * 1024 * 1024
MAX_ZIP = 128 * 1024 * 1024
SECONDS = 300
ID = re.compile(r"pz-[a-z0-9][a-z0-9-]{0,59}\Z")
STEM = re.compile(r"[a-z][a-z0-9_-]{0,63}\Z")
SHA = re.compile(r"[0-9a-f]{64}\Z")
REVISION = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9._-]{0,31}\Z")


def require(condition, message):
    if not condition:
        raise InvalidInput(message)


def string(value, label, maximum=4096):
    require(isinstance(value, str) and 1 <= len(value) <= maximum and bool(value.strip()),
            f"Missing/invalid {label}")
    return value


def sha(value):
    require(isinstance(value, str) and SHA.fullmatch(value), "Invalid SHA-256")
    return value


def relative(value):
    string(value, "relative path", 240)
    require("\\" not in value and not value.startswith("/") and ":" not in value,
            "Absolute/Windows path is unsupported")
    for part in value.split("/"):
        require(part not in ("", ".", "..") and not part.endswith((" ", ".")) and
                not any(ord(c) < 32 or c in '<>"|?*' for c in part) and
                part.split(".")[0].casefold() not in {"con", "prn", "aux", "nul", *(
                    f"{p}{n}" for p in ("com", "lpt") for n in range(1, 10))}, "Unsafe package path")
    return value


def timestamp(value):
    string(value, "UTC timestamp", 64)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise InvalidInput("Invalid UTC timestamp") from exc
    require(parsed.tzinfo is not None and parsed.utcoffset().total_seconds() == 0,
            "Approval timestamp must be UTC")


def file_table(root, deadline):
    """No symlinks, junctions, Windows aliases or file/directory collisions."""
    require(root.is_dir() and not root.is_symlink() and not (getattr(root.lstat(), "st_file_attributes", 0) & 1024),
            "Package directory missing/unsafe")
    files, names, total = {}, set(), 0
    for parent, dirs, leaves in os.walk(root, followlinks=False):
        for name in dirs + leaves:
            if time.monotonic() >= deadline:
                raise Aborted("time_limit")
            path = Path(parent) / name
            rel = relative(path.relative_to(root).as_posix())
            key = rel.casefold()
            require(key not in names, "Windows-colliding package paths")
            names.add(key)
            require(len(names) <= MAX_FILES * 2, "Too many package entries")
            info = path.lstat()
            require(not path.is_symlink() and not (getattr(info, "st_file_attributes", 0) & 1024),
                    "Symlinks/reparse points are unsupported")
            if path.is_file():
                require(stat.S_ISREG(info.st_mode) and info.st_size <= MAX_FILE, "Package file too large/unsafe")
                total += info.st_size
                files[rel] = path
                require(len(files) <= MAX_FILES and total <= MAX_TOTAL, "Package resource limit")
    return files


@contextmanager
def open_package(source: Path, *, allow_manual_review=False):
    deadline = time.monotonic() + SECONDS
    if source.is_dir():
        yield Package(source, deadline, allow_manual_review=allow_manual_review)
        return
    require(source.is_file() and not source.is_symlink() and source.stat().st_size <= MAX_ZIP,
            "Missing/oversized ZIP")
    archive_hash = file_hash(source)
    with tempfile.TemporaryDirectory(prefix="za1-input-") as temp:
        root = Path(temp)
        try:
            with zipfile.ZipFile(source) as archive:
                infos = archive.infolist()
                require(len(infos) <= MAX_FILES * 2, "Too many ZIP members")
                seen, total, leaves = set(), 0, []
                for info in infos:
                    name = relative(info.filename.rstrip("/"))
                    require(name.casefold() not in seen, "Duplicate/Windows-colliding ZIP names")
                    seen.add(name.casefold())
                    mode = info.external_attr >> 16
                    require(stat.S_IFMT(mode) in (0, stat.S_IFREG, stat.S_IFDIR) and not info.flag_bits & 1,
                            "ZIP special/encrypted member unsupported")
                    require(info.file_size <= MAX_FILE, "ZIP member too large")
                    total += info.file_size
                    require(total <= MAX_TOTAL, "Expanded ZIP too large")
                    if not info.is_dir():
                        leaves.append((name, info))
                require(len(leaves) <= MAX_FILES, "Too many ZIP files")
                keys = {name.casefold() for name, _ in leaves}
                require(all(not any('/'.join(name.casefold().split('/')[:n]) in keys
                                    for n in range(1, len(name.split('/')))) for name, _ in leaves),
                        "ZIP file/directory collision")
                roots = {name.split('/')[0] for name, _ in leaves}
                has_root = "handoff.json" not in keys
                require(not has_root or len(roots) == 1, "ZIP requires a single package root")
                for name, info in leaves:
                    if time.monotonic() >= deadline:
                        raise Aborted("time_limit")
                    path = root / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    # Reading to EOF checks CRC; bound the actual decoded byte count too.
                    with archive.open(info) as stream, path.open("xb") as out:
                        count = 0
                        while chunk := stream.read(1024 * 1024):
                            count += len(chunk)
                            require(count <= info.file_size and count <= MAX_FILE, "ZIP size mismatch")
                            out.write(chunk)
                    require(count == info.file_size, "ZIP size mismatch")
        except (zipfile.BadZipFile, NotImplementedError, RuntimeError) as exc:
            raise InvalidInput(f"Invalid ZIP: {exc}") from exc
        package = Package(root / next(iter(roots)) if has_root else root, deadline,
                          allow_manual_review=allow_manual_review)
        package.archive_sha256 = archive_hash
        yield package


class Package:
    def __init__(self, root, deadline, *, allow_manual_review=False):
        self.root, self.deadline = root, deadline
        self.archive_sha256 = None
        self.files = file_table(root, deadline)
        self.used = set()
        self.handoff = self.json("handoff.json")
        h = self.handoff
        require(isinstance(h, dict) and h.get("format") == "picross-authoring-handoff-v2", "Unsupported Authoring handoff")
        require(isinstance(h.get("puzzle_id"), str) and ID.fullmatch(h["puzzle_id"]), "Invalid production ID")
        require(isinstance(h.get("revision"), str) and REVISION.fullmatch(h["revision"]), "Invalid package revision")
        # Reading a historical manual handoff is not its acceptance. inspect()
        # still requires the external, exactly bound manual authorization.
        require(h.get("state") in ("content_ready", "editorially_approved", "catalog_ready") or
                allow_manual_review and h.get("state") == "raster_review" and
                isinstance(h.get("candidate"), dict) and h["candidate"].get("source_type") == "manual" or
                allow_manual_review and h.get("state") == "blocked" and
                isinstance(h.get("manual_edit_record"), str) and
                isinstance(h.get("candidate"), dict) and h["candidate"].get("source_type") == "import",
                "Package is not content_ready")
        require(isinstance(h.get("repo_commit"), str) and re.fullmatch(r"[0-9a-f]{40}", h["repo_commit"]), "Missing producer commit")
        rule = h.get("rulebook")
        require(isinstance(rule, dict) and rule.get("version") in ("0.4.0", "0.4.1"), "Unsupported authoring rulebook")
        self.bound(rule)
        inv = h.get("inventory")
        require(isinstance(inv, dict) and inv.get("file") == "inventory.json", "Missing inventory binding")
        self.bound(inv)
        inventory = self.json("inventory.json")
        require(isinstance(inventory, dict) and {"format", "puzzle_id", "revision", "files"} <= set(inventory), "Invalid inventory")
        require(inventory.get("excludes", ["inventory.json", "handoff.json"]) == ["inventory.json", "handoff.json"], "Invalid inventory exclusions")
        require(inventory["format"] == "picross-authoring-file-inventory-v1" and
                inventory["puzzle_id"] == h["puzzle_id"] and inventory["revision"] == h["revision"], "Inventory identity mismatch")
        require(isinstance(inventory["files"], list) and len(inventory["files"]) <= MAX_FILES, "Invalid inventory list")
        entries, folded = {}, set()
        for record in inventory["files"]:
            exact_keys(record, {"path", "sha256", "bytes"})
            name = relative(record["path"])
            require(name not in ("inventory.json", "handoff.json", "derivation.json") and name.casefold() not in folded,
                    "Self-reference/duplicate inventory path")
            folded.add(name.casefold())
            integer(record["bytes"], 0, MAX_FILE, "inventory bytes")
            sha(record["sha256"])
            entries[name] = record
        self.entries = entries
        self.derivation = self.json("derivation.json") if "derivation.json" in self.files else None
        if self.derivation is not None:
            require(set(self.files)-{"handoff.json","inventory.json","derivation.json"} <= set(entries),
                    "Compact file is outside original inventory")
            d = exact_keys(self.derivation, {"format", "original_zip_sha256", "handoff_sha256", "inventory_sha256", "files"})
            require(d["format"] == "picross-authoring-derivation-v1" and
                    d["handoff_sha256"] == file_hash(self.file("handoff.json")) and
                    d["inventory_sha256"] == inv["sha256"], "Invalid compact derivation binding")
            if d["original_zip_sha256"] is not None:
                sha(d["original_zip_sha256"])
            require(isinstance(d["files"], dict) and set(d["files"]) == set(self.files) - {"derivation.json"},
                    "Incomplete compact file bindings")
            for name, expected in d["files"].items():
                require(file_hash(self.files[name]) == sha(expected), "Changed compact file")
        else:
            require(set(self.files) == set(entries) | {"inventory.json", "handoff.json"}, "Inventory file set differs from package")
        for name, path in self.files.items():
            if name in entries:
                require(path.stat().st_size == entries[name]["bytes"] and file_hash(path) == entries[name]["sha256"],
                        "Inventory size/hash mismatch: " + name)
        self.used.update(("handoff.json", "inventory.json"))

    def file(self, name):
        relative(name)
        require(name in self.files, "Missing package file: " + name)
        self.used.add(name)
        if time.monotonic() >= self.deadline:
            raise Aborted("time_limit")
        return self.files[name]

    def json(self, name):
        value = load_json(self.file(name))
        return value

    def bound(self, record):
        require(isinstance(record, dict), "Missing file/hash binding")
        path = self.file(record.get("file"))
        require(file_hash(path) == sha(record.get("sha256")), "File binding mismatch")
        return path

    def bundle(self, name):
        relative(name)
        prefix = name + "/"
        members = [n for n in self.files if n.startswith(prefix)]
        require(members, "Missing production bundle")
        for n in members:
            self.file(n)
        return self.root / name

    def approval(self, record, kind):
        approval = self.json(record.get("approval"))
        require(isinstance(approval, dict) and approval.get("type") == f"human_{kind}_approval",
                "Missing/unsupported image approval")
        for key in ("actor", "statement", "revision"):
            string(approval.get(key), "image approval " + key)
        timestamp(approval.get("timestamp_utc"))
        require(approval.get("file") == record["file"] and approval.get("sha256") == record["sha256"],
                "Image approval binding mismatch")
        if kind == "motif":
            require(approval.get("derived_from_reveal_sha256") == record["derived_from_reveal_sha256"],
                    "Motif approval derivation mismatch")
        self.file(approval.get("evidence"))
        return approval

    def provenance(self, record, kind):
        name = record.get("provenance", str(Path(record["file"]).with_suffix(".provenance.json")).replace("\\", "/"))
        p = self.json(name)
        require(isinstance(p, dict) and p.get("puzzle_id") == self.handoff["puzzle_id"] and
                p.get("file") == record["file"] and p.get("sha256") == record["sha256"], "Provenance binding mismatch")
        string(p.get("usage_basis"), "usage basis")
        string(p.get("author"), "author")
        if kind == "motif":
            derived = p.get("derived_from")
            require(isinstance(derived, dict) and derived.get("file") == self.handoff["reveal"]["file"] and
                    derived.get("sha256") == record["derived_from_reveal_sha256"], "Missing motif derivation provenance")
        for key in ("prompt_file", "input"):
            if p.get(key) is not None:
                self.file(p[key])
        return p
