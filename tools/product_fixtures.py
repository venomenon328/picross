"""Bounded native regression catalog, separate from the actual player export."""
from pathlib import Path
import shutil


def copy_regression_game(root: Path, project: Path) -> None:
    """Never copy the growing authoring/runtime content corpus into test projects."""
    from tools.puzzle_production.content_registry import projection
    from tools.puzzle_production.contract import load_json, write_json
    shutil.copytree(root / "game", project, ignore=shutil.ignore_patterns(".godot", "build", "content"))
    fixtures = root / "tests/puzzle_production/fixtures/catalog"
    registry = load_json(fixtures / "registry.json")
    catalog = load_json(fixtures / "categories.json")
    write_json(project / "data/registry.json", projection(registry, catalog))


def restore_player_catalog(root: Path, project: Path) -> bool:
    """Use actual delivered content for export, without certifying/replaying it."""
    source = root / "game/data/registry.json"
    target = project / "data/registry.json"
    changed = source.read_bytes() != target.read_bytes()
    shutil.copyfile(source, target)
    for name in ("data/content", "art/content"):
        if (root / "game" / name).exists():
            shutil.copytree(root / "game" / name, project / name)
            changed = True
    return changed
