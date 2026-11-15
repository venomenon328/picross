"""Read-only review check over untouched native measurement originals."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).parent
load = lambda name: json.loads((root / name).read_text(encoding="utf-8"))
manifest = load("README.json")
for name, ref in manifest["files"].items():
    raw = (root / name).read_bytes()
    assert len(raw) == ref["bytes"] and hashlib.sha256(raw).hexdigest() == ref["sha256"], name
before, after, summary = load("T00-controlled.json"), load("T01-final.json"), load("T02-summary.json")
repo = root.parents[1]
for name, sha in after["modules"].items():
    assert hashlib.sha256((repo / name).read_bytes()).hexdigest() == sha, name
for i, (a, b, row) in enumerate(zip(before["rows"], after["rows"], summary["rows"])):
    operation = ("finalizer", "export", "verify-export")[i % 3]
    assert row["mode"] == a["mode"] == b["mode"]
    assert row["operation"] == operation
    assert row["before_counts"] == a["counts"] and row["after_counts"] == b["counts"]
    assert row["before_seconds"] == a["seconds"] and row["after_seconds"] == b["seconds"]
    assert all(b["counts"].get(k, 0) <= v for k, v in row["limits"].items())
    if operation != "verify-export": assert b["seconds"] <= a["seconds"]
    if operation == "finalizer":
        assert a["input_bindings"] == b["input_bindings"]
        assert a["bindings"] == b["bindings"] and a["result"] == b["result"]
        assert a["counts"]["projector_inspections"] > b["counts"]["projector_inspections"]
    elif operation == "export":
        assert set(a["bindings"]) == set(b["bindings"])
        assert all(a["bindings"][k] == b["bindings"][k] for k in a["bindings"] if k not in ("inspection.json", "manifest.json"))
        assert a["counts"]["adapter_inspections"] > b["counts"]["adapter_inspections"]
        for v in (a["result"], b["result"]): v["files"].pop("inspection.json")
        assert a["result"] == b["result"]
    else:
        for v in (a["result"], b["result"]):
            v[0]["files"].pop("inspection.json")
            v[1].pop("checked_at_utc")
            v[1]["tool"].pop("commit")
            v[1]["tool"]["modules"].pop("background_export.py")
        assert a["result"] == b["result"]
    print(row["mode"], operation, "PASS")
