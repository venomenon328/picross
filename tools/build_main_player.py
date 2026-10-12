#!/usr/bin/env python3
"""Build a playable Windows player from the checked-out game, without the test harness."""
from __future__ import annotations

import argparse
from pathlib import Path, PurePosixPath
import platform
import shutil
import sys
import tempfile
import zipfile

import p1_preflight as toolchain


EXPECTED_EXPORTS = {"picross-p1.exe", "picross-p1.console.exe"}
ALLOWED_EXPORTS = EXPECTED_EXPORTS | {"picross-p1.pck"}


def stage_player(build: Path, destination: Path, source_commit: str,
                 guide: str, extras: dict[str, Path]) -> list[str]:
    """Stage direct download contents. GitHub upload-artifact supplies the only ZIP."""
    export_files = {path.name: path for path in build.iterdir() if path.is_file()}
    if not EXPECTED_EXPORTS <= export_files.keys() or set(export_files) - ALLOWED_EXPORTS:
        raise toolchain.PreflightError(f"Incomplete/unexpected Windows export: {sorted(export_files)}")
    if any(path.stat().st_size == 0 for path in export_files.values()):
        raise toolchain.PreflightError("Empty Windows export file")
    if destination.exists() and any(destination.iterdir()):
        raise toolchain.PreflightError("Player output must be empty")

    # Product is the single source of bundled notices and licenses.
    # Owner probes and the original guide are not part of this plain player build.
    shipped = {name: path for name, path in extras.items()
               if name not in {"rp6-owner.ps1", "SPIELANLEITUNG.md"}}
    expected = set(export_files) | set(shipped) | {"README.txt", "SPIELANLEITUNG.md"}
    for name, path in shipped.items():
        member = PurePosixPath(name)
        if (member.is_absolute() or ".." in member.parts or not member.parts
                or member.as_posix() != name or name.lower().endswith((".zip", ".tar", ".7z"))):
            raise toolchain.PreflightError(f"Unsafe/non-player extra: {name}")
        if not path.is_file():
            raise toolchain.PreflightError(f"Missing player extra: {name}")
        if name in export_files or name in {"README.txt", "SPIELANLEITUNG.md"}:
            raise toolchain.PreflightError(f"Duplicate player file: {name}")
    if not guide.strip() or len(source_commit) != 40 or any(c not in "0123456789abcdef" for c in source_commit):
        raise toolchain.PreflightError("Missing player guide or invalid source SHA")

    destination.mkdir(parents=True, exist_ok=True)
    for name, path in export_files.items():
        shutil.copyfile(path, destination / name)
    for name, path in shipped.items():
        target = destination.joinpath(*PurePosixPath(name).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    (destination / "SPIELANLEITUNG.md").write_text(guide, encoding="utf-8", newline="\n")
    (destination / "README.txt").write_text(
        "picross · P1 – Windows x86_64\n"
        "Unsignierte Debug-Entwicklungsfassung (kein Release/Installer)\n"
        f"Quellcommit (main): {source_commit}\n"
        f"Godot: {toolchain.RELEASE_TAG}\n\n"
        "Dieses eine Archiv vollständig entpacken und picross-p1.exe starten.\n"
        "picross-p1.console.exe zeigt bei Bedarf technische Meldungen.\n"
        "Spielanleitung: SPIELANLEITUNG.md; Nutzungsrechte: licenses/.\n"
        "Keine Godot-Installation erforderlich. Spielstände gehören nicht zum Archiv.\n",
        encoding="utf-8", newline="\n",
    )
    files = {str(path.relative_to(destination)).replace("\\", "/")
             for path in destination.rglob("*") if path.is_file()}
    if files != expected:
        raise toolchain.PreflightError(f"Player staging differs: {sorted(files ^ expected)}")
    return sorted(files)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--download-timeout-seconds", type=int, default=180)
    parser.add_argument("--process-timeout-seconds", type=int, default=300)
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    host = platform.system()
    if host not in toolchain.EDITORS or platform.machine().lower() not in {"x86_64", "amd64"}:
        parser.error("Only Windows/Linux x86_64 builders are supported")
    try:
        source_commit, dirty = toolchain.source_commit(root)
        if dirty:
            raise toolchain.PreflightError("Player builds require a clean checkout")
        editor = toolchain.EDITORS[host]
        metadata = toolchain.request_json(toolchain.RELEASE_API)
        urls = toolchain.official_asset_urls(metadata, (editor, toolchain.TEMPLATES))
        cache = args.cache_dir.resolve()
        for asset in (editor, toolchain.TEMPLATES):
            toolchain.download_asset(urls[asset.name], cache / asset.name,
                                     asset.sha256, args.download_timeout_seconds)

        with tempfile.TemporaryDirectory(prefix="picross-main-player-") as temporary:
            workspace = Path(temporary).resolve()
            engine = str(toolchain.extract_editor(cache / editor.name, workspace / "engine", host))
            toolchain.extract_windows_templates(cache / toolchain.TEMPLATES.name,
                                                toolchain.template_directory(workspace, host))
            project = workspace / "game"
            shutil.copytree(root / "game", project,
                            ignore=shutil.ignore_patterns(".godot", "build"))
            from p1_product import player_extras, player_guide, project_name
            project_name(project / "project.godot")
            env = toolchain.isolated_environment(workspace, host)
            commands = (
                ("version", [engine, "--version"], toolchain.EXPECTED_VERSION),
                ("import", [engine, "--headless", "--path", str(project), "--import"], None),
                ("windows-export", [engine, "--headless", "--path", str(project),
                                    "--export-debug", "P1 Windows x86_64",
                                    str(project / "build/windows/picross-p1.exe")], None),
            )
            (project / "build/windows").mkdir(parents=True, exist_ok=True)
            for name, command, marker in commands:
                result = toolchain.run_command(name, command, env,
                                               args.process_timeout_seconds)
                toolchain.require_success(result, marker)
                if "SCRIPT ERROR:" in result["output"] or "ERROR:" in result["output"]:
                    raise toolchain.PreflightError(f"{name} logged a Godot error")
            extra_dir = workspace / "extras"
            extra_dir.mkdir()
            files = stage_player(project / "build/windows", args.output_dir.resolve(),
                                 source_commit, player_guide(root, source_commit),
                                 player_extras(root, extra_dir))
            print(f"PLAYER SOURCE {source_commit}", flush=True)
            print("PLAYER FILES " + ", ".join(files), flush=True)
            print("PLAYER BUILD PASS (Windows launch not run on Linux)", flush=True)
    except (OSError, ValueError, zipfile.BadZipFile, toolchain.PreflightError) as exc:
        print(f"PLAYER BUILD FAIL: {exc}", file=sys.stderr, flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
