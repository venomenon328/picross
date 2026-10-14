"""Bounded archive helper retained pending the CI scope decision in #116."""
from pathlib import Path
import zipfile
from .images import file_hash
from .authoring_package import require

def unpack_archive(archive, metadata, output):
    require(not output.exists(), "Use a fresh archive extraction directory")
    require(metadata["format"] == "picross-rp5-archive-v1" and archive.stat().st_size <= 8*1024*1024 and
            file_hash(archive) == metadata["sha256"], "Invalid/altered RP-5 archive")
    files = metadata["files"]
    require(isinstance(files, dict) and 1 <= len(files) <= 512, "Invalid archive file count")
    with zipfile.ZipFile(archive) as z:
        entries = z.infolist()
        names = [e.filename for e in entries]
        require(len(names) == len(set(n.casefold() for n in names)) and set(names) == set(files), "Duplicate/missing archive entries")
        expanded = sum(e.file_size for e in entries)
        require(expanded == metadata["expanded_bytes"] and expanded <= 128*1024*1024, "Archive expanded byte limit exceeded")
        for e in entries:
            path = Path(e.filename)
            require(not path.is_absolute() and "\\" not in e.filename and ":" not in e.filename and
                    all(p not in (".", "..", "") for p in e.filename.split("/")) and
                    not e.is_dir() and (e.external_attr >> 16) & 0o170000 != 0o120000,
                    "Unsafe archive member")
        output.mkdir(parents=True)
        for e in entries:
            target = output / e.filename
            require(output.resolve() in target.resolve().parents, "Unsafe archive target")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(z.read(e))
            require(file_hash(target) == files[e.filename], "Archive member bytes changed")
    return output
