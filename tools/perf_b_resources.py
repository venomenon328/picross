"""Separate historical A manufacture from the active B resource contract."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "examples/perf_b/a-source.zip"


def historical_files(snapshot=SNAPSHOT):
    manifest = json.loads((ROOT / "prototypes/p1/perf_a/atlases/manifest.json").read_text())
    expected = {**manifest["generator_files"],
                **{"prototypes/p1/" + p: h for p, h in manifest["source_files"].items()},
                **{"prototypes/p1/perf_a/" + p: h for p, h in manifest["consumer_contract"].items()}}
    plan = json.loads((ROOT / "examples/perf_b/plan.json").read_text())
    if hashlib.sha256(snapshot.read_bytes()).hexdigest() != plan["a_source_archive_sha256"]:
        raise ValueError("Historical A source archive identity differs")
    with zipfile.ZipFile(snapshot) as archive:
        if sorted(archive.namelist()) != sorted(expected):
            raise ValueError("Historical A source inventory differs")
        files = {p: archive.read(p) for p in expected}
    if any(hashlib.sha256(files[p]).hexdigest() != h for p, h in expected.items()):
        raise ValueError("Historical A source/manufacturer identity differs")
    return files


def install_historical_probe(project):
    """Only in disposable test projects; original byte bindings precede relocation."""
    files = historical_files()
    binding = {}
    for path, data in files.items():
        if not path.startswith("prototypes/p1/") or "/perf_a/" in path:
            continue
        relative = path.removeprefix("prototypes/p1/")
        text = data.decode("utf-8")
        for original in ("ui/board.gd", "ui/grid_view.gd", "ui/pencil_marks.gd"):
            text = text.replace("res://" + original, "res://perf_a/original/" + original)
        # The probe entry remains where existing A consumers expect it.
        target = project / (relative if relative.startswith("tests/") else "perf_a/original/" + relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="\n")
        binding[relative] = dict(original_sha256=hashlib.sha256(data).hexdigest(),
                                 relocated_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    return binding


def verify_runtime(root=ROOT):
    manifest = json.loads((root / "prototypes/p1/perf_a/atlases/manifest.json").read_text())
    import perf_a_atlas
    result = {}
    for item in manifest["atlases"]:
        path = root / "prototypes/p1/art/cells" / item["file"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError("Runtime atlas differs from original A bytes")
        settings = path.with_suffix(".png.import").read_text()
        source = "res://art/cells/" + path.name
        expected = perf_a_atlas.import_settings(path.name)
        old = "res://perf_a/atlases/" + path.name
        expected = expected.replace(hashlib.md5(old.encode()).hexdigest(), hashlib.md5(source.encode()).hexdigest()).replace(old, source)
        if settings != expected:
            raise ValueError("Runtime atlas import contract differs")
        result[path.name] = item["sha256"]
    return dict(atlases=result, a_manifest_sha256=hashlib.sha256((root / "prototypes/p1/perf_a/atlases/manifest.json").read_bytes()).hexdigest(),
                runtime_files={p: hashlib.sha256((root / "prototypes/p1/ui" / p).read_bytes()).hexdigest()
                               for p in ("atlas_marks.gd", "atlas_mask.gdshader", "cell_atlas.gd", "drawing_board.gd")})
