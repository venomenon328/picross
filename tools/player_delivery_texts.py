"""Shared user guide and third-party notices for regular player delivery."""
from pathlib import Path
import re
from urllib.parse import quote, urlsplit

from p1_preflight import PreflightError


def player_extras(root: Path, output: Path) -> dict[str, Path]:
    extras = {}
    for name, source in (
        ("SPIELANLEITUNG.md", "game/README.md"),
        ("licenses/resources.json", "game/art/book/manifest.json"),
        ("licenses/ViewTitles-NOTICE.txt", "game/art/drawing/view_titles/NOTICE.txt"),
        ("licenses/ViewTitles-manifest.json", "game/art/drawing/view_titles/manifest.json"),
        ("licenses/ViewTitles-provenance.json", "game/art/drawing/view_titles/provenance.json"),
        ("licenses/Book-paper.json", "game/book/paper.json"),
        ("licenses/Book-leather.json", "game/book/leather.json"),
        ("licenses/Book-table.json", "game/book/table.json"),
        ("licenses/Margins-NOTICE.txt", "game/art/drawing/margins/NOTICE.txt"),
        ("licenses/Margins-provenance.json", "game/art/drawing/margins/provenance.json"),
        ("licenses/Chalkboard-NOTICES.md", "game/art/drawing/NOTICES.md"),
        ("licenses/Bakso-NOTICES.md", "game/art/drawing/Bakso-NOTICES.md"),
        ("licenses/pangolin/NOTICE.txt", "game/art/drawing/pangolin/NOTICE.txt"),
        ("licenses/pangolin/OFL.txt", "game/art/drawing/pangolin/OFL.txt"),
        ("licenses/DelightCoffee-NOTICES.md", "game/art/drawing/DelightCoffee-NOTICES.md"),
        ("licenses/delight-coffee/More Info.txt", "game/art/drawing/delight-coffee/More Info.txt"),
        ("licenses/delight-coffee/Read Me.pdf", "game/art/drawing/delight-coffee/Read Me.pdf"),
    ):
        extras[name] = root / source
    for path in sorted((root / "game/art/book").glob("*.txt")):
        extras["licenses/" + path.name] = path
    return extras


def player_guide(root: Path, source_commit: str) -> str:
    """Make repository links usable after the player ZIP is extracted elsewhere."""
    def bound_link(match):
        target = match.group(2)
        url = urlsplit(target)
        if url.scheme or not url.path:
            return match.group(0)
        path = (root / "game" / url.path).resolve()
        # Existence is checked by the mandatory repository document validator;
        # packaging fixtures need only the actual payload sources.
        if not path.is_relative_to(root.resolve()):
            raise PreflightError("Invalid player guide link: " + target)
        bound = "https://github.com/venomenon328/picross/blob/" + source_commit + "/" + quote(path.relative_to(root.resolve()).as_posix())
        return "[" + match.group(1) + "](" + bound + ("#" + url.fragment if url.fragment else "") + ")"
    return re.sub(r"\[([^\]\n]*)\]\(([^)\n]*)\)", bound_link,
                  (root / "game/README.md").read_text(encoding="utf-8"))


def project_name(project_file: Path) -> str:
    for line in project_file.read_text(encoding="utf-8").splitlines():
        if line.startswith('config/name="') and line.endswith('"'):
            value = line[len('config/name="'):-1]
            if value != EXPECTED_PROJECT_NAME:
                raise PreflightError(f"Unexpected project name: {value!r}")
            return value
    raise PreflightError("Missing project name")
