"""Bound background sources and one texture profile in disposable Godot copies.

The source inventory binds PNG/TXT bytes before import. Engine import/output
bytes are separate evidence; a source PNG hash is never a compressed texture hash.
This module deliberately needs only the standard library in the player build.
"""
from __future__ import annotations

import configparser
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct


FORMAT = "picross-background-import-v1"
NAMESPACE = "art/backgrounds"
SIZE = (2304, 576)
PROFILE = {
    "compress/mode": "0",
    "compress/high_quality": "false",
    "compress/normal_map": "2",
    "mipmaps/generate": "true",
    "mipmaps/limit": "-1",
    "roughness/mode": "1",
    "process/channel_remap/red": "0",
    "process/channel_remap/green": "1",
    "process/channel_remap/blue": "2",
    "process/channel_remap/alpha": "3",
    "process/fix_alpha_border": "false",
    "process/premult_alpha": "false",
    "process/normal_map_invert_y": "false",
    "process/hdr_as_srgb": "false",
    "process/size_limit": "0",
    "detect_3d/compress_to": "0",
}


def _hash(raw):
    return hashlib.sha256(raw).hexdigest()


def _regular(path: Path) -> Path:
    if path.is_symlink() or not path.is_file():
        raise ValueError("Background input must be a regular file: " + str(path))
    return path


def _read_bound(project, ref):
    name = ref["file"]
    if not re.fullmatch(r"art/backgrounds/[A-Za-z0-9_-]+\.(png|txt)", name):
        raise ValueError("Invalid background input path")
    path = project / name
    if path.resolve().parent != (project / NAMESPACE).resolve():
        raise ValueError("Background input escaped its namespace")
    raw = _regular(path).read_bytes()
    if len(raw) != ref["bytes"] or _hash(raw) != ref["sha256"]:
        raise ValueError("Background source size/hash differs: " + name)
    if name.endswith(".png"):
        if (len(raw) < 33 or raw[:16] != b"\x89PNG\r\n\x1a\n\0\0\0\rIHDR"
                or struct.unpack(">IIBBBBB", raw[16:29]) != (*SIZE, 8, 6, 0, 0, 0)):
            raise ValueError("Background source is not PNG2304 RGBA: " + name)
    return raw


def _names(project):
    directory = project / NAMESPACE
    if not directory.exists():
        return set()
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("Background namespace must be a real directory")
    return {(_regular(p)).relative_to(project).as_posix() for p in directory.iterdir()}


def source_inventory(root: Path) -> dict:
    """Read compact authority, selected sources and notices; never replay puzzles."""
    from tools.puzzle_production import catalog_background as background, catalog_io as io, content_registry as catalog

    root = root.resolve()
    if (root / "content/.registration-pending.json").exists():
        raise ValueError("Interrupted registration: recovery required before player export")
    game = root / "game"
    raw = (game / "data/registry.json").read_bytes()
    runtime = json.loads(raw)
    registry = io.json_bytes(io.read(root, "content/registry.json", 8 * 1024 * 1024), 8 * 1024 * 1024)
    background.source_paths(root, registry)
    indexed = background.index(registry)
    modern = registry["format"] in (catalog.BACKGROUND_FORMAT, catalog.METADATA_FORMAT)
    background.capability(root, required=registry["format"] == catalog.BACKGROUND_FORMAT or bool(indexed))
    formats = {catalog.FORMAT: tuple("picross-runtime-registry-v" + str(v) for v in (2, 3, 4, 5)),
               catalog.BACKGROUND_FORMAT: (background.RUNTIME_FORMAT,),
               catalog.METADATA_FORMAT: (catalog.METADATA_RUNTIME_FORMAT,)}
    if runtime["format"] not in formats.get(registry["format"], ()):
        raise ValueError("Background runtime/source generation differs")
    texts = {name: io.read(root, name, background.LIMIT, missing=True)
             for name in background.text_names(registry)}
    projected = background.projection(registry, texts)
    entries = runtime["entries"]
    if len(entries) != len(projected) or {e["id"] for e in entries} != set(projected):
        raise ValueError("Background runtime/source IDs differ")
    assets = []
    for entry in entries:
        identifier = entry["id"]
        expected = projected[identifier]
        if modern and entry.get("background") != expected or not modern and "background" in entry:
            raise ValueError("Background runtime projection is stale: " + identifier)
        if expected["status"] != "selected":
            continue
        # projection() already checked the compact source against its indexed hash
        # and closed source schema. The notice is not repeated in runtime data.
        source = io.json_bytes(texts[indexed[identifier]["file"]], background.LIMIT)
        notice = background.current(source)["notice"]
        row = dict(id=identifier, image_revision=expected["image_revision"], asset=expected["asset"],
                   notice={**notice, "file": notice["file"].removeprefix("game/")})
        _read_bound(game, row["asset"])
        _read_bound(game, row["notice"])
        assets.append(row)
    wanted = {row[key]["file"] for row in assets for key in ("asset", "notice")}
    if _names(game) != wanted:
        raise ValueError("Active background source inventory differs")
    return dict(format=FORMAT, source_game=str(game), registry_sha256=_hash(raw),
                assets=sorted(assets, key=lambda row: row["id"]))


def require_isolated(project, inventory=None):
    """Reject source/ancestor destinations before any disposable-copy mutation."""
    project = project.resolve()
    real_game = Path(__file__).resolve().parents[1] / "game"
    sources = [real_game]
    if inventory is not None and inventory.get("source_game"):
        sources.append(Path(inventory["source_game"]).resolve())
    if any(project == source or project.is_relative_to(source) or source.is_relative_to(project)
           for source in sources):
        raise ValueError("Background import requires an isolated game copy")


def _verify_sources(project, inventory, *, imports):
    if inventory["format"] != FORMAT or _hash((project / "data/registry.json").read_bytes()) != inventory["registry_sha256"]:
        raise ValueError("Background inventory/runtime binding differs")
    wanted = set()
    for row in inventory["assets"]:
        for key in ("asset", "notice"):
            _read_bound(project, row[key])
            wanted.add(row[key]["file"])
        if imports:
            wanted.add(row["asset"]["file"] + ".import")
    if _names(project) != wanted:
        raise ValueError("Isolated background inventory differs")


def remap_path(asset: str) -> str:
    path = "res://" + asset
    digest = hashlib.md5(path.encode("utf-8"), usedforsecurity=False).hexdigest()
    return "res://.godot/imported/" + Path(asset).name + "-" + digest + ".ctex"


def prepare_import(project: Path, inventory: dict | None = None) -> dict:
    """Set the common profile before --import, only in a separate engine copy.

    Selected inputs require source_inventory(source_checkout). Legacy regression
    copies need no original source corpus and return an empty inventory.
    """
    require_isolated(project, inventory)
    if inventory is None:
        raw = (project / "data/registry.json").read_bytes()
        runtime = json.loads(raw)
        if any(e.get("background", {}).get("status") == "selected" for e in runtime["entries"]):
            raise ValueError("Selected backgrounds require a bound source inventory")
        inventory = dict(format=FORMAT, source_game="", registry_sha256=_hash(raw), assets=[])
    # Repeated preparation is permitted only for the exact bound files and their
    # own technical sidecars; no candidates or unknown files can be imported.
    wanted = {row[key]["file"] for row in inventory["assets"] for key in ("asset", "notice")}
    allowed = wanted | {row["asset"]["file"] + ".import" for row in inventory["assets"]}
    if not wanted <= _names(project) <= allowed:
        raise ValueError("Isolated background inventory differs")
    if inventory["format"] != FORMAT or _hash((project / "data/registry.json").read_bytes()) != inventory["registry_sha256"]:
        raise ValueError("Background inventory/runtime binding differs")
    for row in inventory["assets"]:
        for key in ("asset", "notice"):
            _read_bound(project, row[key])
    for row in inventory["assets"]:
        asset = row["asset"]["file"]
        remap = remap_path(asset)
        text = ('[remap]\n\nimporter="texture"\ntype="CompressedTexture2D"\n'
                + 'path=' + json.dumps(remap) + '\nmetadata={"vram_texture": false}\n\n[deps]\n\n'
                + 'source_file=' + json.dumps("res://" + asset) + '\n'
                + 'dest_files=' + json.dumps([remap]) + '\n\n[params]\n\n'
                + ''.join(key + '=' + value + '\n' for key, value in PROFILE.items()))
        (project / (asset + ".import")).write_text(text, encoding="utf-8", newline="\n")
    return inventory


def verify_import(project: Path, inventory: dict) -> dict:
    """Check actual remaps/profile/output after Godot; decoding is the PCK probe."""
    _verify_sources(project, inventory, imports=True)
    rows = []
    for row in inventory["assets"]:
        asset = row["asset"]["file"]
        path = project / (asset + ".import")
        config = configparser.ConfigParser(interpolation=None, delimiters=("=",), allow_no_value=True)
        config.read_string(path.read_text(encoding="utf-8"))
        remap = remap_path(asset)
        if (config.get("remap", "importer", fallback="") != '"texture"'
                or config.get("remap", "type", fallback="") != '"CompressedTexture2D"'
                or json.loads(config.get("remap", "path", fallback='""')) != remap
                or json.loads(config.get("deps", "source_file", fallback='""')) != "res://" + asset
                or json.loads(config.get("deps", "dest_files", fallback="[]")) != [remap]
                or any(config.get("params", key, fallback="") != value for key, value in PROFILE.items())):
            raise ValueError("Background import profile/remap differs: " + asset)
        imported = _regular(project / remap.removeprefix("res://")).read_bytes()
        if (len(imported) < 52 or imported[:4] != b"GST2"
                or struct.unpack_from("<8I", imported, 4) != (1, *SIZE, 1 << 23, 0xffffffff, 0, 0, 0)):
            raise ValueError("Background imported texture header differs: " + asset)
        codec, width, height, mipmaps, image_format = struct.unpack_from("<IHHII", imported, 36)
        if codec not in (1, 2) or (width, height, mipmaps, image_format) != (*SIZE, 11, 5):
            raise ValueError("Background imported lossless/RGBA/mipmap header differs: " + asset)
        offset = 52
        for _ in range(mipmaps + 1):
            if offset + 4 > len(imported):
                raise ValueError("Background imported mipmap blocks differ: " + asset)
            length = struct.unpack_from("<I", imported, offset)[0]
            offset += 4 + length
            if length == 0 or offset > len(imported):
                raise ValueError("Background imported mipmap blocks differ: " + asset)
        if offset != len(imported):
            raise ValueError("Background imported mipmap blocks differ: " + asset)
        rows.append(dict(id=row["id"], image_revision=row["image_revision"], asset=row["asset"], notice=row["notice"],
                         import_config_sha256=_hash(path.read_bytes()),
                         imported=dict(file=remap.removeprefix("res://"), bytes=len(imported), sha256=_hash(imported),
                                       mipmap_count=mipmaps, codec="lossless-png" if codec == 1 else "lossless-webp")))
    return dict(format=FORMAT, registry_sha256=inventory["registry_sha256"], images=rows,
                source_bytes=sum(r["asset"]["bytes"] for r in rows),
                imported_bytes=sum(r["imported"]["bytes"] for r in rows))


def restore_sources(root: Path, project: Path, inventory: dict | None = None) -> dict:
    """Replace only the isolated background namespace and its imported caches."""
    inventory = source_inventory(root) if inventory is None else inventory
    require_isolated(project, inventory)
    directory = project / NAMESPACE
    _names(project)  # Refuse links/non-files before removing the disposable namespace.
    imported = project / ".godot/imported"
    if imported.is_symlink():
        raise ValueError("Imported cache must be an isolated real directory")
    if imported.exists():
        for path in imported.iterdir():
            match = re.fullmatch(r"(.+\.png)-([0-9a-f]{32})\..+", path.name)
            if match and Path(remap_path(NAMESPACE + "/" + match[1])).name.startswith(match[1] + "-" + match[2] + "."):
                _regular(path).unlink()
    if directory.exists():
        shutil.rmtree(directory)
    for row in inventory["assets"]:
        for key in ("asset", "notice"):
            name = row[key]["file"]
            destination = project / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / "game" / name, destination)
    return inventory
