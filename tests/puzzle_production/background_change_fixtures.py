"""Small real HP-W2 background changes; no approval or verification success stubs."""
from copy import deepcopy
from pathlib import Path
import shutil
import subprocess
from types import SimpleNamespace

from tests.puzzle_production.background_fixtures import BackgroundFixture, file_ref, put, put_json, pixels
from tools.puzzle_production import background_assets as assets, background_request as requests
from tools.puzzle_production import catalog_background as bg, content_registry as registry
from tools.puzzle_production.contract import load_json, write_json
from tools.puzzle_production.za1_fixtures import ROOT


def create_work(testcase, checkout, workspace, revision="bg-r01", choice="selected", image=None, *, install=True):
    checkout, workspace = Path(checkout), Path(workspace)
    entries = load_json(checkout / registry.REGISTRY)
    entry = next(e for e in entries["entries"] if e["id"] in bg.index(entries))
    identifier = entry["id"]
    active = bg.load(checkout, entries, entry)
    active_raw = (checkout / bg.path(identifier)).read_bytes()
    fixture = BackgroundFixture(workspace / (revision + "-fixture"), assets.describe(), none=choice == "none",
                                image=image if image is not None else pixels((7, 5), (95, 80, 65, 160)))
    fixture.manifest["puzzle_id"] = fixture.decision["puzzle_id"] = identifier
    fixture.manifest["job_id"] = fixture.decision["job_id"] = "change-" + revision
    context = fixture.manifest["context"]
    obsolete = fixture.source / "evidence/reveal.txt"
    if obsolete.exists(): obsolete.unlink()
    context["reveal"] = put(fixture.source, "context/reveal.png", (checkout / ("game/" + entry["reveal"])).read_bytes())
    context["reveal_approval"] = put(fixture.source, "context/active-source.json", active_raw)
    statement = (f"TEST ONLY: Replace {identifier} source {bg.ref(bg.path(identifier), active_raw)['sha256']} "
                 + ("with explicitly none; waive initial candidates." if choice == "none" else
                    "with the isolated candidate A and its fixed deterministic profile."))
    evidence = put(fixture.source, "evidence/decision.txt", statement.encode())
    fixture.decision.update(statement=statement, evidence=evidence)
    if choice == "none":
        fixture.manifest["candidate_policy"]["exception"].update(statement=statement, evidence=deepcopy(evidence))
    else:
        norm = {"file": "docs/PUZZLE_QUALITY.md", "contract": "1.0", "document_revision": 9,
                "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "sha256": bg.ref("quality", (ROOT / "docs/PUZZLE_QUALITY.md").read_bytes())["sha256"]}
        candidate = fixture.manifest["candidates"][0]
        candidate["review"] = {criterion: {
            "result": "erfüllt", "reason": "TEST ONLY synthetic contract judgment.",
            "method": "TEST ONLY constructed pixels", "norm": deepcopy(norm),
            "actor": "Synthetic change test", "timestamp_utc": "2026-01-01T12:00:00Z",
            "evidence": [deepcopy(candidate["original"])]}
            for criterion in ("Q-HG01", "Q-HG02", "Q-HG03", "Q-HG04")}
    fixture.refresh()
    derived = assets.derive(fixture.request, fixture.source, fixture.output)
    testcase.assertIn(derived["status"], ("derived", "none"), derived)
    source = workspace / (revision + "-work")
    shutil.copytree(fixture.source, source)
    shutil.copytree(fixture.target, source / "outputs/background")
    base = requests.selection(identifier, revision)
    def stored(root, ref):
        return {"storage": "external", "root": root, "ref": deepcopy(ref)}
    request = {"format": requests.FORMAT, "puzzle_id": identifier, "revision": revision,
               "target": {"source": bg.ref(bg.path(identifier), active_raw),
                          "origin_sha256": bg.origin_hash(active), "image_revision": bg.current(active)["image_revision"]},
               "background": {"manifest": stored(base, fixture.request["manifest"]),
                              "decision": stored(base, fixture.request["decision"]),
                              "derivation": stored(base + "/outputs", file_ref(source / "outputs", "background/derivation.json")),
                              "history": None},
               "authorization": {key: deepcopy(fixture.decision[key]) for key in ("actor", "timestamp_utc", "statement", "evidence")},
               "files": [file_ref(source, p.relative_to(source).as_posix()) for p in sorted(source.rglob("*")) if p.is_file()],
               "test_only": True}
    put_json(source, "record.json", request)
    if install:
        shutil.copytree(source, checkout / base)
        index_path = checkout / requests.INDEX
        index = load_json(index_path) if index_path.exists() else {"format": "picross-authoring-index-v1", "entries": []}
        index["entries"].append(requests.index_row(request))
        write_json(index_path, index)
    payload = {p.relative_to(source).as_posix(): p.read_bytes() for p in source.rglob("*") if p.is_file()}
    return SimpleNamespace(request=request, record_path=requests.record_name(request), source_root=source,
                           fixture=fixture, payload=payload)
