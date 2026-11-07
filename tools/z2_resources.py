"""Reproduce active book resources from pinned BP-3 inputs and the HZ-B icon source."""
from pathlib import Path
import argparse
import hashlib
import json
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/design/book_inventory"
DEST = ROOT / "game/art/book"
KB_ICONS = Path(__file__).with_name("book_icons_kb.json")
HZ_ICONS = Path(__file__).with_name("book_icons_hz.json")
ACTIVE_ICONS = {"fill", "erase", "undo", "redo", "minus", "plus", "help", "menu", "nav-album", "nav-information", "nav-work", "play", "reset", "arrow-left", "arrow-right", "arrow-up", "arrow-down", "chevron-down", "chevron-up", "check", "check-empty", "checkbox-empty", "checkbox-checked", "scroll-up", "scroll-down", "scroll-left", "scroll-right"}


def active_icons():
    icons = json.loads(HZ_ICONS.read_text(encoding="utf-8"))
    assert set(icons) == ACTIVE_ICONS
    assert all(len(entry) == 4 and all(isinstance(v, str) for v in entry) for entry in icons.values())
    return icons


def icon_svg(entry, *, filled=False):
    paths = "".join(f'<path d="{path}" stroke-width="{width}"' + (f' fill="{fill}"' if filled else "") + "/>"
                    for path, width, fill in zip(entry[2:], ("1.7", "0.85"),
                                                 ("white" if filled else "none", "none")) if path)
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 26 26">'
            '<g fill="none" stroke="white" stroke-linecap="round" stroke-linejoin="round">' + paths + '</g></svg>\n')


def hz_source():
    return dict(file="tools/book_icons_hz.json", sha256=hashlib.sha256(HZ_ICONS.read_bytes()).hexdigest(),
                generator="tools/z2_resources.py", notice="HZ-B-284-NOTICE.txt")


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
    icons = active_icons()
    (DEST / "icons.json").write_text(json.dumps(icons, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    for name, entry in icons.items():
        (DEST / (name + ".svg")).write_text(icon_svg(entry, filled=name.startswith("scroll-")), encoding="utf-8", newline="\n")
    # Path ordering differs between Windows and POSIX; manifest bytes must not.
    for path in sorted(DEST.iterdir(), key=lambda path: path.name):
        if path.suffix in (".ttf", ".txt", ".png", ".svg", ".json") and path.name != "manifest.json":
            records.append(dict(file=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    (DEST / "manifest.json").write_text(json.dumps(dict(source_commit="c3a5386580d7a0da29b927b41bd692f0cca59274", sidebar_source="SL-65; frames.json", kb_icon_source="tools/book_icons_kb.json; KB-168-NOTICE.txt", hz_icon_source=hz_source(), files=records), indent=2) + "\n", encoding="utf-8", newline="\n")


def verify():
    manifest = json.loads((DEST / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["hz_icon_source"] == hz_source(), "HZ icon source binding"
    assert "tools/book_icons_hz.json" in (DEST / "HZ-B-284-NOTICE.txt").read_text(encoding="utf-8")
    icons = json.loads((DEST / "icons.json").read_text(encoding="utf-8"))
    assert icons == active_icons()
    assert set(icons) == ACTIVE_ICONS
    assert {p.stem for p in DEST.glob("*.svg")} == ACTIVE_ICONS
    listed = [item["file"] for item in manifest["files"]]
    actual = {p.name for p in DEST.iterdir() if p.suffix in (".ttf", ".txt", ".png", ".svg", ".json") and p.name != "manifest.json"}
    assert len(listed) == len(set(listed)) and set(listed) == actual, "Resource inventory mismatch"
    for name, entry in icons.items():
        assert (DEST / (name + ".svg")).read_bytes() == icon_svg(entry, filled=name.startswith("scroll-")).encode("utf-8"), name
    for item in manifest["files"]:
        assert hashlib.sha256((DEST / item["file"]).read_bytes()).hexdigest() == item["sha256"], item["file"]
    for item in json.loads((SOURCE / "composition/inputs/fonts.json").read_text(encoding="utf-8")):
        assert hashlib.sha256((DEST / Path(item["file"]).name).read_bytes()).hexdigest() == item["sha256"]
    assert (DEST / "bp2-a-inventarband.png").read_bytes() == (SOURCE / "artwork/bp2-a-inventarband.png").read_bytes()
    # HZ-A-FONT02 is a new owner-supplied source, not a rewritten BP-3 input.
    # Provisioning the historical book assets must not replace this TTF.
    tidy = ROOT / "game/art/drawing/TidyHand.ttf"
    notice = ROOT / "game/art/drawing/tidy-hand/NOTICE.txt"
    digest = "9eacc0d857ab9decbc34b0dab150641ba5b5a9560a8d163b6494dd5babbcdfd6"
    assert hashlib.sha256(tidy.read_bytes()).hexdigest() == digest, "HZ Tidy Hand original bytes"
    text = notice.read_text(encoding="utf-8")
    assert digest in text and "https://www.dafont.com/de/tidy-hand.font" in text
    assert '"This font is free for all use."' in text and "Sean Johnson" in text
    manifest["hz_standard_text"] = dict(file="art/drawing/TidyHand.ttf", sha256=digest,
        notice="art/drawing/tidy-hand/NOTICE.txt",
        notice_sha256=hashlib.sha256(notice.read_bytes()).hexdigest())
    # PANG-A replaces the active role; the HZ original above stays historical.
    pangolin = ROOT / "game/art/drawing/Pangolin-Regular.ttf"
    license = ROOT / "game/art/drawing/pangolin/OFL.txt"
    source = ROOT / "game/art/drawing/pangolin/NOTICE.txt"
    font_hash = "a48db64eadc589c2e9f14a4ba79eed82a438c7f620f929dd19e352c20b2a922e"
    license_hash = "414e35e9875605ea0dfe549a6bdad6d1f1f3d5427c97af2060213adb6709484c"
    assert pangolin.stat().st_size == 589884 and hashlib.sha256(pangolin.read_bytes()).hexdigest() == font_hash, "PANG original font bytes"
    assert hashlib.sha256(license.read_bytes()).hexdigest() == license_hash, "PANG original OFL bytes"
    text = source.read_text(encoding="utf-8")
    assert font_hash in text and license_hash in text and "https://github.com/venomenon328/picross/issues/531" in text
    manifest["standard_text"] = dict(file="art/drawing/Pangolin-Regular.ttf", sha256=font_hash,
        license="art/drawing/pangolin/OFL.txt", license_sha256=license_hash,
        notice="art/drawing/pangolin/NOTICE.txt", notice_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["provision", "verify"])
    args = parser.parse_args()
    if args.action == "provision":
        provision()
    print(json.dumps(verify(), indent=2))
