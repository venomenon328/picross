"""Resolve current files referenced by immutable pre-move input manifests."""
from pathlib import Path, PurePosixPath


def current_path(root: Path, recorded: str) -> Path:
    """Keep recorded names/hashes intact; relocate only the former game prefix."""
    path = PurePosixPath(recorded)
    if not recorded or path.is_absolute() or ".." in path.parts or "\\" in recorded or ":" in recorded:
        raise ValueError("Unsafe recorded repository path")
    if recorded.startswith("prototypes/p1/"):
        recorded = "game/" + recorded.removeprefix("prototypes/p1/")
    return root / recorded
