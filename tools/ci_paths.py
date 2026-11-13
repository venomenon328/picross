"""Shared inert puzzle-content paths; no engine or legacy CI selection imports."""
from pathlib import PurePosixPath
import re


def content_path(path: str) -> bool:
    """Only inert authoring/adapter outputs; never runtime code or shared art."""
    if path.startswith('content/authoring/') and any(
            part.lower() == 'current-view.json' for part in path.split('/')):
        # The pointer has exactly one position; do not fall through to the
        # general revision-file rule for nested or otherwise malformed pointers.
        return re.fullmatch(r'content/authoring/pz-[a-z0-9][a-z0-9-]{0,59}/current-view\.json', path) is not None
    if path in {"content/categories.json", "content/registry.json", "content/authoring/index.json",
                "content/authoring/README.md", "game/data/registry.json"}:
        return True
    if re.fullmatch(r"game/data/content/[a-z][a-z0-9_-]{0,63}\.json", path):
        return True
    if re.fullmatch(r"game/art/content/[a-z][a-z0-9_-]{0,63}\.(png|svg|txt)", path):
        return True
    if re.fullmatch(r"content/added/pz-[a-z0-9][a-z0-9-]{0,59}\.json", path):
        return True
    if re.fullmatch(r"content/difficulty/pz-[a-z0-9][a-z0-9-]{0,59}/rating\.json", path):
        return True
    if re.fullmatch(r"content/reveals/pz-[a-z0-9][a-z0-9-]{0,59}\.json", path):
        return True
    if re.fullmatch(r"content/backgrounds/pz-[a-z0-9][a-z0-9-]{0,59}\.json", path):
        return True
    if re.fullmatch(r"game/art/backgrounds/pz-[a-z0-9][a-z0-9-]{0,59}\.(png|txt)", path):
        return True
    match = re.fullmatch(r"content/difficulty/reports/([a-z][a-z0-9-]{0,63})/report\.(json|md)", path)
    if match:
        return match[1] not in {"con", "prn", "aux", "nul", *(f"{p}{n}" for p in ("com", "lpt") for n in range(1, 10))}
    parts = PurePosixPath(path).parts
    return (len(parts) >= 5 and parts[:2] in (("content", "authoring"), ("content", "packages"))
            and re.fullmatch(r"pz-[a-z0-9][a-z0-9-]{0,59}", parts[2]) is not None
            and re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]{0,31}", parts[3]) is not None
            and all(part not in {".", ".."} and not part.startswith(".") for part in parts[3:])
            and "\\" not in path and PurePosixPath(path).suffix.lower() in
            {".json", ".png", ".jpg", ".jpeg", ".svg", ".txt", ".md", ".html", ".zip"})

