"""Bounded native regression catalog, separate from the actual player export."""
from pathlib import Path
import shutil
import json


def runtime_catalog(root: Path) -> dict:
    return json.loads((root / "tests/puzzle_production/fixtures/catalog/runtime.json").read_text(encoding="utf-8"))


def install_runtime_fixtures(root: Path, project: Path, *, append: bool = False) -> None:
    """Install six synthetic geometry/interaction samples only in a disposable game.

    T01/T02/T06 retain historical clue shapes as isolated geometry inputs,
    without the original puzzles or reveals. Frozen KAT1 saves have separate inputs.
    No solver, real production package or catalog-size-dependent generation.
    """
    from tools.puzzle_production.contract import write_json
    catalog = runtime_catalog(root)
    colors = ["#343f42", "#edca78", "#bd604a", "#6c9aab"]
    for entry in catalog["entries"]:
        number = int(entry["id"][2:])
        palette_colors = ["#253342", "#637b58", "#c89d56", "#b55848"] if number == 6 else colors
        size = 20 if number in (1, 4) else 50 if number == 6 else 40
        count = 1 if number in (1, 4) else 4
        block = 4 if number == 6 else 3
        matrix = [[0 if x == 0 or y == 0 or x == size-1 or y == size-1 else
                   1 + ((x // block + y // block) % count) for x in range(size)] for y in range(size)]
        if number == 1:
            # Pending, ambiguous and bounded-complete clue-status specimens.
            matrix[3] = [0]*8 + [1]*3 + [0]*9
            for y, value in enumerate([0]*10 + [1]*3 + [0,1] + [0]*5):
                matrix[y][1] = value
        if number == 2:
            # Exact line lengths exercise the established nearest-slot drop oracle.
            matrix[11] = [0] + [4]*4 + [2]*7 + [4]*8 + [1] + [2]*7 + [1] + [4]*10 + [0]
            matrix[34] = [0] + [4]*12 + [1]*23 + [4]*3 + [0]
            matrix[35] = [0,4,1,1,1,4,4,4,4,4,1,1,1,4,4,4,4,4,1,1,1,4,4,4,4,4,1,1,1,4,4,4,4,4,1,1,1,4,4,0]
            columns = {
                11: [0] + [4]*4 + [2]*7 + [4]*23 + [1] + [4]*3 + [0],
                21: [0] + [4]*6 + [3]*3 + [2]*3 + [1]*2 + [3]*4 + [2]*4 + [3]*4 + [2]*4 + [3] + [1]*3 + [4]*3 + [1,0],
            }
            for x, values in columns.items():
                for y, value in enumerate(values):
                    matrix[y][x] = value
        if number == 6:
            # Preserve the pixel-motion oracle's glyph density on both axes.
            matrix[41] = [0]*6 + [3,2,2,2,3,0,4,4,0,3,4,3,3,4,1] + [0]*8 + [1,4,3,3,4,3,0,4,4,0,3,2,2,2,3] + [0]*6
            matrix[40] = matrix[41].copy()
            column = [0]*10 + [4,4,2,1,2,2,3,3,2,4,4,3,2,2,4,4,4,3,4,4,4,2,2,2,4,4,4,4,4,4,4,3,2,1,2,3,3,0,0,0]
            column[40] = 3
            for y, value in enumerate(column):
                matrix[y][17] = matrix[y][18] = value
        def hints(line):
            result, previous = [], 0
            for value in line:
                if value:
                    if value == previous:
                        result[-1]["length"] += 1
                    else:
                        result.append(dict(length=1, color=value))
                previous = value
            return result
        definition = dict(schema=2, id=entry["id"], revision=2, width=size, height=size,
                          test_only=True, palette=[dict(id=i+1, color=color, symbol=chr(65+i))
                                                   for i, color in enumerate(palette_colors[:count])],
                          solution=matrix, rows=[hints(row) for row in matrix],
                          columns=[hints(column) for column in zip(*matrix)],
                          reveal=dict(version=1, definition_id=entry["id"],
                                      name=f"TEST ONLY Muster {number}", image="res://"+entry["reveal"]))
        target = project / entry["definition"]
        target.parent.mkdir(parents=True, exist_ok=True)
        write_json(target, definition)
        if number in (1, 2):
            cells = [n if n > 0 else -1 for row in matrix for n in row] if number == 2 else [-1] * (size * size)
            history = [[dict(index=i, before=-1, after=n) for i, n in enumerate(cells) if n > 0]]
            if number == 1:
                cells[64] = 1
                history = [[dict(index=64, before=-1, after=1)], [dict(index=65, before=-1, after=0)]]
            saved = dict(schema=1, definition_id=entry["id"], definition_revision=2,
                         width=size, height=size, cells=cells, history=history, cursor=1,
                         undo_used=number == 1, completed=number == 2,
                         view=dict(active_color=1, center=[size/2, size/2], overview=False,
                                   tool="fill", zoom=24,
                                   row_clue_reads=[dict(anchor="grid_end") for _ in range(size)],
                                   column_clue_reads=[dict(anchor="grid_end") for _ in range(size)]))
            save_path = project / "tests/fixtures/runtime" / (entry["key"] + ".json")
            save_path.parent.mkdir(parents=True, exist_ok=True)
            write_json(save_path, saved)
        artwork = project / entry["reveal"]
        artwork.parent.mkdir(parents=True, exist_ok=True)
        artwork.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="800" height="800">'
                           f'<rect width="800" height="800" fill="{colors[(number-1)%4]}"/>'
                           '<circle cx="400" cy="400" r="200" fill="#ffffff"/></svg>\n', encoding="utf-8")
    if append:
        current = json.loads((project / "data/registry.json").read_text(encoding="utf-8"))
        catalog["categories"] = current["categories"]
        catalog["entries"] += current["entries"]
    write_json(project / "data/registry.json", catalog)


def copy_regression_game(root: Path, project: Path) -> None:
    """Never copy the growing authoring/runtime content corpus into test projects."""
    shutil.copytree(root / "game", project, ignore=shutil.ignore_patterns(".godot", "build", "content"))
    install_runtime_fixtures(root, project)


def restore_player_catalog(root: Path, project: Path) -> bool:
    """Use actual delivered content for export, without certifying/replaying it."""
    source = root / "game/data/registry.json"
    target = project / "data/registry.json"
    changed = source.read_bytes() != target.read_bytes()
    # Remove the temporary fixture resources before importing the real player.
    for name in ("data/fixtures", "art/fixtures"):
        path = (project / name).resolve()
        if not path.is_relative_to(project.resolve()):
            raise ValueError("Unsafe fixture resource path")
        if path.exists():
            shutil.rmtree(path)
            changed = True
    shutil.copyfile(source, target)
    for name in ("data/content", "art/content"):
        if (root / "game" / name).exists():
            shutil.copytree(root / "game" / name, project / name)
            changed = True
    return changed
