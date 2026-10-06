"""Check the exact neutral GP-48 player ZIP, separate from technical evidence."""
import hashlib
import json
import zipfile
from pathlib import Path

import p1_preflight as toolchain

PLAYER_FILES = {
    "picross-p1.exe", "picross-p1.console.exe", "README.txt", "product-report.json",
    "GP48-SPIELPROBE.md", "gp48-owner.ps1", "licenses/Fraunces-OFL.txt",
    "licenses/PlexSans-OFL.txt", "licenses/resources.json",
}


def verify_player_package(archive: Path, manifest: dict) -> dict:
    with zipfile.ZipFile(archive) as bundle:
        names = bundle.namelist()
        exports = set(manifest["export_files"])
        executables = {"picross-p1.exe", "picross-p1.console.exe"}
        if not executables <= exports or exports - executables - {"picross-p1.pck"}:
            raise toolchain.PreflightError("Unexpected GP-48 export files")
        expected = PLAYER_FILES | (exports - executables)
        if set(names) != expected or len(names) != len(expected):
            raise toolchain.PreflightError("Unexpected GP-48 player ZIP contents")
        if json.loads(bundle.read("product-report.json")) != manifest:
            raise toolchain.PreflightError("Player report differs from technical report")
        for name, digest in manifest["export_files"].items():
            if hashlib.sha256(bundle.read(name)).hexdigest() != digest:
                raise toolchain.PreflightError("Player executable hash mismatch")
        if manifest["source_commit"].encode() not in bundle.read("README.txt"):
            raise toolchain.PreflightError("Player README lacks source identity")
        return dict(file=archive.name, sha256=toolchain.sha256_file(archive), files=names,
                    bytes=archive.stat().st_size)
