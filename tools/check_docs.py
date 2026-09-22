#!/usr/bin/env python3
"""Offline setup checks, adapted from dev-rules@a662d3c2c1ba004de5bb65fbd16f8091c4abcce4.

Checks simple inline file links outside fenced/inline code. Fragments, reference
links, external URLs and game behavior are not verified. Standard library only.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

TEXT_SUFFIXES = {".md", ".py", ".yml", ".yaml", ".json", ".toml", ".txt"}
TEXT_NAMES = {"VERSION", ".gitignore", ".gitattributes"}
SKIP_DIRS = {".git", "__pycache__", ".venv", "node_modules"}
REQUIRED = (
    "README.md", "AGENTS.md", "docs/PROJECT_PROFILE.md",
    "docs/DEV_RULES_ADOPTION.md", "docs/CHATGPT_PROJECT_INSTRUCTIONS.md",
    "docs/dev-rules/WORKFLOW.md", "docs/dev-rules/MODEL_SELECTION.md",
    "docs/dev-rules/MODEL_CATALOG.md", "docs/dev-rules/VERSION",
    "docs/dev-rules/CHANGELOG.md", ".github/workflows/setup.yml",
    "tools/check_docs.py", "tools/test_check_docs.py",
)
VERSION_RE = re.compile(r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:-rc\.[1-9]\d*)?")
LINK_RE = re.compile(r"!?\[[^\]\n]*\]\(([^)\n]*)\)")


def prose_only(text: str) -> str:
    """Remove fenced code and simple inline code before inspecting file links."""
    output: list[str] = []
    fence_char = ""
    fence_length = 0
    for line in text.splitlines():
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})(.*)$", line)
        if marker:
            run, rest = marker.groups()
            if not fence_char:
                fence_char, fence_length = run[0], len(run)
                continue
            if run[0] == fence_char and len(run) >= fence_length and not rest.strip():
                fence_char = ""
                continue
        if not fence_char:
            output.append(re.sub(r"`+[^`\n]*`+", "", line))
    return "\n".join(output)


def check_links(path: Path, text: str, root: Path) -> list[str]:
    """Check local paths and keep snapshot links inside docs/dev-rules/."""
    errors: list[str] = []
    portable = root / "docs" / "dev-rules"
    label = path.relative_to(root).as_posix()
    for match in LINK_RE.finditer(prose_only(text)):
        raw = match.group(1).strip()
        if raw.startswith("<") and ">" in raw:
            raw = raw[1:raw.index(">")]
        else:
            raw = raw.split(maxsplit=1)[0] if raw else ""
        try:
            url = urlsplit(raw)
        except ValueError:
            errors.append(f"{label}: invalid link target {raw!r}")
            continue
        if url.scheme in {"https", "http", "mailto"}:
            continue
        if url.scheme or url.netloc or url.path.startswith("/"):
            errors.append(f"{label}: unsupported/non-relative local link {raw!r}")
            continue
        if not url.path:
            continue
        target = (path.parent / unquote(url.path)).resolve()
        if not target.is_relative_to(root):
            errors.append(f"{label}: link leaves repository: {raw}")
            continue
        if path.is_relative_to(portable) and not target.is_relative_to(portable):
            errors.append(f"{label}: link leaves portable rules package: {raw}")
        if not target.exists():
            errors.append(f"{label}: missing link target: {raw}")
    return errors


def check_tree(root: Path) -> list[str]:
    """Return structural problems without network calls or file mutations."""
    root = root.resolve()
    if not root.is_dir():
        return [f"Not a directory: {root}"]
    errors: list[str] = []
    texts: dict[str, str] = {}
    for required in REQUIRED:
        if not (root / required).is_file():
            errors.append(f"Missing required file: {required}")
    for directory, dirs, names in os.walk(root, followlinks=False):
        base = Path(directory)
        kept: list[str] = []
        for name in sorted(dirs):
            child = base / name
            if name in SKIP_DIRS:
                continue
            if child.is_symlink():
                errors.append(f"Symlink directory not supported: {child.relative_to(root)}")
            else:
                kept.append(name)
        dirs[:] = kept
        for name in sorted(names):
            path = base / name
            label = path.relative_to(root).as_posix()
            if path.is_symlink():
                errors.append(f"Symlink file not supported: {label}")
                continue
            if path.suffix not in TEXT_SUFFIXES and name not in TEXT_NAMES:
                continue
            try:
                data = path.read_bytes()
                text = data.decode("utf-8")
            except (OSError, UnicodeError) as exc:
                errors.append(f"{label}: cannot read UTF-8 text: {exc}")
                continue
            texts[label] = text
            if data.startswith(b"\xef\xbb\xbf"):
                errors.append(f"{label}: UTF-8 BOM is not allowed")
            if b"\r" in data:
                errors.append(f"{label}: use LF line endings")
            if not text or not text.endswith("\n"):
                errors.append(f"{label}: non-empty text and final newline required")
            for number, line in enumerate(text.splitlines(), 1):
                if line.rstrip(" \t") != line:
                    errors.append(f"{label}:{number}: trailing whitespace")
            if path.suffix == ".md":
                errors.extend(check_links(path, text, root))
    version = texts.get("docs/dev-rules/VERSION", "").strip()
    if not VERSION_RE.fullmatch(version):
        errors.append("docs/dev-rules/VERSION: expected MAJOR.MINOR.PATCH or MAJOR.MINOR.PATCH-rc.N")
    elif not re.search(r"^## " + re.escape(version) + r"(?:\s|$)",
                       texts.get("docs/dev-rules/CHANGELOG.md", ""), flags=re.MULTILINE):
        errors.append("docs/dev-rules/CHANGELOG.md: current version heading is missing")
    return errors


def main() -> int:
    if sys.version_info < (3, 11):
        print("Python 3.11 or newer is required", file=sys.stderr)
        return 2
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = check_tree(args.root)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        print(f"FAIL: {len(errors)} documentation problem(s)", file=sys.stderr)
        return 1
    print("PASS: text conventions, inline file links, version and rules portability")
    print("Not checked: anchors, reference links, external URLs, snapshot identity, game behavior")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
