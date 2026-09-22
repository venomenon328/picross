#!/usr/bin/env python3
"""Run the isolated Godot 4.7.2 P1 toolchain preflight.

The script fetches official release metadata and assets, verifies SHA-256
digests, runs a tiny positive and deliberately failing GDScript test, starts
the project headlessly, and exports a Windows x86_64 debug build. It does not
read or write product save data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


RELEASE_TAG = "4.7.2-stable"
RELEASE_API = (
    "https://api.github.com/repos/godotengine/godot-builds/releases/tags/"
    + RELEASE_TAG
)
EXPECTED_VERSION = "4.7.2.stable.official.ed1daf0bf"
EXPORT_PRESET = "P1 Preflight Windows x86_64"


@dataclass(frozen=True)
class Asset:
    name: str
    sha256: str


EDITORS = {
    "Windows": Asset(
        "Godot_v4.7.2-stable_win64.exe.zip",
        "731980f9608d61333e5baf54a2ef17210acc7a538446c0cb9969f002aca1e953",
    ),
    "Linux": Asset(
        "Godot_v4.7.2-stable_linux.x86_64.zip",
        "cadd3204e728a35d3f13adb7fd0d7902636b79f6b95c40c265eb73b6c35329e4",
    ),
}
TEMPLATES = Asset(
    "Godot_v4.7.2-stable_export_templates.tpz",
    "f298490b8d44d934be425a5a65a51bf15f422428b229a06a6e11d9ffea248011",
)


class PreflightError(RuntimeError):
    """A reproducible preflight failure."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_sha256(path: Path, expected: str) -> str:
    actual = sha256_file(path)
    if actual != expected:
        raise PreflightError(
            f"SHA-256 mismatch for {path.name}: expected {expected}, got {actual}"
        )
    return actual


def request_json(url: str) -> dict[str, object]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "picross-p1-preflight",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def official_asset_urls(metadata: dict[str, object], expected: tuple[Asset, ...]) -> dict[str, str]:
    if metadata.get("tag_name") != RELEASE_TAG:
        raise PreflightError(f"Unexpected release tag: {metadata.get('tag_name')!r}")
    if metadata.get("draft") is not False or metadata.get("prerelease") is not False:
        raise PreflightError("Pinned release is draft or prerelease")
    assets = {
        item.get("name"): item
        for item in metadata.get("assets", [])
        if isinstance(item, dict)
    }
    urls: dict[str, str] = {}
    for asset in expected:
        item = assets.get(asset.name)
        if not isinstance(item, dict):
            raise PreflightError(f"Official release is missing {asset.name}")
        if item.get("digest") != f"sha256:{asset.sha256}":
            raise PreflightError(f"Official digest changed for {asset.name}")
        url = item.get("browser_download_url")
        if not isinstance(url, str) or not url.startswith(
            "https://github.com/godotengine/godot-builds/releases/download/"
        ):
            raise PreflightError(f"Unexpected official URL for {asset.name}")
        urls[asset.name] = url
    return urls


def download_asset(url: str, target: Path, expected_sha256: str, max_seconds: int) -> str:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_file():
        try:
            digest = verify_sha256(target, expected_sha256)
            print(f"CACHE VERIFIED {target.name} sha256:{digest}", flush=True)
            return digest
        except PreflightError:
            target.unlink()
    partial = target.with_suffix(target.suffix + ".partial")
    partial.unlink(missing_ok=True)
    started = time.monotonic()
    request = urllib.request.Request(url, headers={"User-Agent": "picross-p1-preflight"})
    try:
        with urllib.request.urlopen(request, timeout=60) as response, partial.open("wb") as output:
            while chunk := response.read(1024 * 1024):
                output.write(chunk)
                if time.monotonic() - started > max_seconds:
                    raise PreflightError(
                        f"Download exceeded {max_seconds}s for {target.name}"
                    )
        partial.replace(target)
        digest = verify_sha256(target, expected_sha256)
    except Exception:
        partial.unlink(missing_ok=True)
        raise
    print(f"DOWNLOAD VERIFIED {target.name} sha256:{digest}", flush=True)
    return digest


def safe_member_name(name: str) -> PurePosixPath:
    member = PurePosixPath(name)
    if member.is_absolute() or ".." in member.parts:
        raise PreflightError(f"Unsafe archive member: {name}")
    return member


def extract_editor(archive: Path, destination: Path, host: str) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as bundle:
        candidates = []
        windows_main = []
        for info in bundle.infolist():
            member = safe_member_name(info.filename)
            basename = member.name
            if info.is_dir():
                continue
            if host == "Windows" and basename.endswith("_console.exe"):
                candidates.append(info)
            elif host == "Windows" and basename.endswith("_win64.exe"):
                windows_main.append(info)
            elif host == "Linux" and basename == "Godot_v4.7.2-stable_linux.x86_64":
                candidates.append(info)
        if len(candidates) != 1 or (host == "Windows" and len(windows_main) != 1):
            raise PreflightError(f"Expected one {host} editor executable, found {len(candidates)}")
        for info in candidates + windows_main:
            extracted = destination / PurePosixPath(info.filename).name
            with bundle.open(info) as source, extracted.open("wb") as output:
                shutil.copyfileobj(source, output)
        executable = destination / PurePosixPath(candidates[0].filename).name
    executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
    return executable


def template_directory(isolated_root: Path, host: str) -> Path:
    if host == "Windows":
        return isolated_root / "appdata" / "Godot" / "export_templates" / "4.7.2.stable"
    return isolated_root / "xdg-data" / "godot" / "export_templates" / "4.7.2.stable"


def extract_windows_templates(archive: Path, destination: Path) -> None:
    wanted = {
        "version.txt",
        "windows_debug_x86_64.exe",
        "windows_debug_x86_64_console.exe",
    }
    destination.mkdir(parents=True, exist_ok=True)
    found: set[str] = set()
    with zipfile.ZipFile(archive) as bundle:
        for info in bundle.infolist():
            member = safe_member_name(info.filename)
            if len(member.parts) != 2 or member.parts[0] != "templates":
                continue
            if member.name not in wanted:
                continue
            with bundle.open(info) as source, (destination / member.name).open("wb") as output:
                shutil.copyfileobj(source, output)
            found.add(member.name)
    if found != wanted:
        raise PreflightError(f"Template archive missing: {sorted(wanted - found)}")


def isolated_environment(root: Path, host: str) -> dict[str, str]:
    environment = os.environ.copy()
    environment["GODOT_SILENCE_ROOT_WARNING"] = "1"
    if host == "Windows":
        environment["APPDATA"] = str(root / "appdata")
        environment["LOCALAPPDATA"] = str(root / "localappdata")
    else:
        environment["XDG_DATA_HOME"] = str(root / "xdg-data")
        environment["XDG_CONFIG_HOME"] = str(root / "xdg-config")
        environment["XDG_CACHE_HOME"] = str(root / "xdg-cache")
    return environment


def run_command(
    name: str,
    command: list[str],
    environment: dict[str, str],
    timeout_seconds: int,
) -> dict[str, object]:
    print(f"RUN {name}: {' '.join(command)}", flush=True)
    try:
        result = subprocess.run(
            command,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise PreflightError(f"{name} exceeded {timeout_seconds}s") from exc
    output = result.stdout or ""
    print(output, end="" if output.endswith("\n") else "\n", flush=True)
    return {"name": name, "exit_code": result.returncode, "output": output[-4000:]}


def require_success(result: dict[str, object], marker: str | None = None) -> None:
    if result["exit_code"] != 0:
        raise PreflightError(f"{result['name']} failed with exit code {result['exit_code']}")
    if marker and marker not in str(result["output"]):
        raise PreflightError(f"{result['name']} did not emit {marker}")


def require_expected_failure(result: dict[str, object], marker: str) -> None:
    if result["exit_code"] == 0:
        raise PreflightError("Deliberately failing test unexpectedly returned success")
    if marker not in str(result["output"]):
        raise PreflightError("Deliberately failing test did not reach the intended failure")


def source_commit(root: Path) -> tuple[str, bool]:
    override = os.environ.get("P1_PREFLIGHT_SOURCE_COMMIT")
    if override:
        return override, False
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True, capture_output=True, check=True
    ).stdout.strip()
    dirty = bool(
        subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=root,
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
    )
    return revision, dirty


def create_artifact(
    build_directory: Path,
    output_directory: Path,
    manifest: dict[str, object],
) -> Path:
    executable = build_directory / "p1-preflight.exe"
    if not executable.is_file() or executable.stat().st_size == 0:
        raise PreflightError("Windows export did not produce p1-preflight.exe")
    allowed = {"p1-preflight.exe", "p1-preflight.console.exe", "p1-preflight.pck"}
    unexpected = sorted(
        path.name for path in build_directory.iterdir() if path.is_file() and path.name not in allowed
    )
    if unexpected:
        raise PreflightError(f"Unexpected exported files: {unexpected}")
    output_directory.mkdir(parents=True, exist_ok=True)
    report = output_directory / "preflight-report.json"
    report.write_bytes((json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    archive = output_directory / "p1-preflight-windows-x86_64.zip"
    readme = (
        "P1.0 technical smoke probe only\n"
        f"Source commit: {manifest['source_commit']}\n"
        "Run p1-preflight.console.exe on Windows to see P1_PREFLIGHT_START_OK; "
        "both executables exit immediately. This is not the P1 game or a GUI acceptance result.\n"
    )
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(build_directory.iterdir()):
            if path.is_file():
                bundle.write(path, f"windows/{path.name}")
        bundle.writestr("README.txt", readme)
        bundle.writestr("preflight-report.json", report.read_text(encoding="utf-8"))
    return archive


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--download-timeout-seconds", type=int, default=1200)
    parser.add_argument("--process-timeout-seconds", type=int, default=300)
    return parser.parse_args()


def main() -> int:
    if sys.version_info < (3, 11):
        print("Python 3.11 or newer is required", file=sys.stderr)
        return 2
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    smoke_source = Path(__file__).with_name("p1_preflight_smoke")
    host = platform.system()
    architecture = platform.machine().lower()
    if host not in EDITORS or architecture not in {"amd64", "x86_64"}:
        print(f"Unsupported preflight host: {host} {architecture}", file=sys.stderr)
        return 2
    editor_asset = EDITORS[host]
    try:
        metadata = request_json(RELEASE_API)
        urls = official_asset_urls(metadata, (editor_asset, TEMPLATES))
        downloaded: dict[str, str] = {}
        for asset in (editor_asset, TEMPLATES):
            downloaded[asset.name] = download_asset(
                urls[asset.name],
                args.cache_dir.resolve() / asset.name,
                asset.sha256,
                args.download_timeout_seconds,
            )
        with tempfile.TemporaryDirectory(prefix="picross-p1-preflight-") as temporary:
            workspace = Path(temporary).resolve()
            executable = extract_editor(
                args.cache_dir.resolve() / editor_asset.name, workspace / "engine", host
            )
            templates = template_directory(workspace, host)
            extract_windows_templates(args.cache_dir.resolve() / TEMPLATES.name, templates)
            project = workspace / "smoke"
            shutil.copytree(smoke_source, project)
            environment = isolated_environment(workspace, host)
            executable_text = str(executable)
            timeout = args.process_timeout_seconds
            results: list[dict[str, object]] = []

            version = run_command("version", [executable_text, "--version"], environment, 30)
            require_success(version, EXPECTED_VERSION)
            results.append(version)
            imported = run_command(
                "import",
                [executable_text, "--headless", "--path", str(project), "--import"],
                environment,
                timeout,
            )
            require_success(imported)
            results.append(imported)
            positive = run_command(
                "positive-test",
                [
                    executable_text,
                    "--headless",
                    "--path",
                    str(project),
                    "--script",
                    "res://test_runner.gd",
                ],
                environment,
                timeout,
            )
            require_success(positive, "P1_PREFLIGHT_TEST_OK")
            results.append(positive)
            negative_environment = environment.copy()
            negative_environment["P1_PREFLIGHT_FORCE_FAILURE"] = "1"
            negative = run_command(
                "expected-negative-test",
                [
                    executable_text,
                    "--headless",
                    "--path",
                    str(project),
                    "--script",
                    "res://test_runner.gd",
                ],
                negative_environment,
                timeout,
            )
            require_expected_failure(negative, "P1_PREFLIGHT_EXPECTED_FAILURE")
            results.append(negative)
            started = run_command(
                "controlled-start",
                [executable_text, "--headless", "--path", str(project)],
                environment,
                timeout,
            )
            require_success(started, "P1_PREFLIGHT_START_OK")
            results.append(started)
            build = project / "build" / "windows"
            build.mkdir(parents=True)
            exported = run_command(
                "windows-export",
                [
                    executable_text,
                    "--headless",
                    "--path",
                    str(project),
                    "--export-debug",
                    EXPORT_PRESET,
                    str(build / "p1-preflight.exe"),
                ],
                environment,
                timeout,
            )
            require_success(exported)
            results.append(exported)
            if host == "Windows":
                exported_start = run_command(
                    "windows-exported-start",
                    [str(build / "p1-preflight.console.exe"), "--headless"],
                    environment,
                    timeout,
                )
                require_success(exported_start, "P1_PREFLIGHT_START_OK")
                results.append(exported_start)
            commit, dirty = source_commit(root)
            manifest: dict[str, object] = {
                "schema": 1,
                "release_tag": RELEASE_TAG,
                "release_published_at": metadata.get("published_at"),
                "host": {"system": host, "architecture": architecture},
                "source_commit": commit,
                "source_tree_dirty": dirty,
                "engine_version": EXPECTED_VERSION,
                "assets": downloaded,
                "checks": [
                    {"name": item["name"], "exit_code": item["exit_code"]}
                    for item in results
                ],
                "github_run_id": os.environ.get("GITHUB_RUN_ID"),
            }
            artifact = create_artifact(build, args.output_dir.resolve(), manifest)
            print(f"ARTIFACT {artifact} sha256:{sha256_file(artifact)}", flush=True)
            print("P1 PREFLIGHT PASS", flush=True)
    except (OSError, ValueError, zipfile.BadZipFile, PreflightError) as exc:
        print(f"P1 PREFLIGHT FAIL: {exc}", file=sys.stderr, flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
