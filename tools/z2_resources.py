"""Reproduce the selected Z2 offline resources from the pinned BP-3 inputs."""
from pathlib import Path
import argparse
import hashlib
import json
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/design/book_inventory"
DEST = ROOT / "prototypes/p1/art/book"


def provision():
    DEST.mkdir(parents=True, exist_ok=True)
    records = []
    for item in json.loads((SOURCE / "composition/inputs/fonts.json").read_text(encoding="utf-8")):
        target = DEST / Path(item["file"]).name
        expected = item.get("upstream_sha256", item["sha256"])
        if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() == item["sha256"]:
            continue
        with urllib.request.urlopen(item["url"], timeout=120) as response:
            data = response.read()
        assert hashlib.sha256(data).hexdigest() == expected, target.name
        if target.suffix == ".txt":
            assert b"SIL OPEN FONT LICENSE" in data
            data = ("\n".join(line.rstrip() for line in data.decode().splitlines()) + "\n").encode()
        assert hashlib.sha256(data).hexdigest() == item["sha256"], target.name
        target.write_bytes(data)
    artwork = SOURCE / "artwork/bp2-a-inventarband.png"
    assert hashlib.sha256(artwork.read_bytes()).hexdigest() == "957c2eab39b2334825fb159287b9d36a17b77fff1c628ea88110f2cfb5f7a71a"
    (DEST / artwork.name).write_bytes(artwork.read_bytes())
    icons = json.loads((SOURCE / "composition/inputs/icons.json").read_text(encoding="utf-8"))
    icons.update({"nav-album": icons["album"],
                  "nav-information": ["Information", "Einstellungen und Hilfe", "M4 12 h16 m-7 -7 l7 7 -7 7"],
                  "nav-work": ["Zum Rätsel", "Zur Arbeitsseite zurück", "M20 12 H4 m7 -7 l-7 7 7 7"]})
    icons["nav-album"] = ["Album", "Zum Album", icons["album"][2]]
    (DEST / "icons.json").write_text(json.dumps(icons, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    for name, entry in icons.items():
        (DEST / (name + ".svg")).write_text('<svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 26 26"><path d="' + entry[2] + '" fill="none" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>\n', encoding="utf-8", newline="\n")
    for path in sorted(DEST.iterdir()):
        if path.suffix in (".ttf", ".txt", ".png", ".svg", ".json") and path.name != "manifest.json":
            records.append(dict(file=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    (DEST / "manifest.json").write_text(json.dumps(dict(source_commit="c3a5386580d7a0da29b927b41bd692f0cca59274", files=records), indent=2) + "\n", encoding="utf-8", newline="\n")


def verify():
    manifest = json.loads((DEST / "manifest.json").read_text(encoding="utf-8"))
    for item in manifest["files"]:
        assert hashlib.sha256((DEST / item["file"]).read_bytes()).hexdigest() == item["sha256"], item["file"]
    for item in json.loads((SOURCE / "composition/inputs/fonts.json").read_text(encoding="utf-8")):
        assert hashlib.sha256((DEST / Path(item["file"]).name).read_bytes()).hexdigest() == item["sha256"]
    assert (DEST / "bp2-a-inventarband.png").read_bytes() == (SOURCE / "artwork/bp2-a-inventarband.png").read_bytes()
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["provision", "verify"])
    args = parser.parse_args()
    if args.action == "provision":
        provision()
    print(json.dumps(verify(), indent=2))
