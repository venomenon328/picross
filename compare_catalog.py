"""Disposable CAT-CONS-A review. Run from the actual PR testmerge checkout."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0, str(Path.cwd()))
from tools.puzzle_production import categories, puzzle_record as record, current_content as content, content_registry

root = Path.cwd()
report = root.parent / "review"
report.mkdir(exist_ok=True)
base = json.loads((root.parent / "before.json").read_bytes())
catalog = categories.load(root / categories.PATH)
assert not base["validation_errors"]
def git(*args):
    return subprocess.check_output(["git", *args])
def sha(raw):
    return hashlib.sha256(raw).hexdigest()
def verify(ref):
    data = (root / ref["file"]).read_bytes()
    assert content.ref(ref["file"], data) == ref
    return ref
head = git("rev-parse", "HEAD^2").decode().strip()
base_commit = git("rev-parse", "HEAD^1").decode().strip()
assert base["base"] == base_commit
inventory = record.inventory(root)
assert inventory == {item["id"] for item in base["entries"]}
originals = []
rows = []
removed = [base["registry"]]
for item in base["entries"]:
    key = item["id"]
    value = record.load(root, key, category_catalog=catalog)
    expected = {"format":record.FORMAT, **item["expected"]}
    assert value == expected
    assert (root / record.path(key)).read_bytes() == record.encode(expected)
    row = record.runtime_row(value)
    assert content.digest(row) == item["runtime_row_sha256"]
    rows.append(row)
    removed.extend(item["removed"])
    originals.append({"id":key, "fields":{k:{"source":expected[k], "matched":value[k] == expected[k]} for k in expected},
        "record":verify(content.ref(record.path(key),record.encode(value))),
        "runtime_row_sha256":content.digest(row),"assets":[verify(r) for r in item["assets"]],
        "rights":[verify(r) for r in item["rights"]]})
actual_removed = set(git("diff", "--name-only", "--diff-filter=D",base_commit,"HEAD","--","content").decode().splitlines())
assert actual_removed == {ref["file"] for ref in removed}
for ref in removed:
    assert not (root/ref["file"]).exists()
assert not git("diff", "--name-only", base_commit,"HEAD","--","game")
for key in ("runtime","categories"):
    verify(base[key])
projected = content.encoded({"format":content.RUNTIME_FORMAT,"entries":rows,"categories":categories.ordered(catalog)})
assert projected == (root / content.RUNTIME).read_bytes()
full = content_registry.check_checkout(root)
assert full["entries"] == len(rows)
result = {"base":base_commit,"head":head,"testmerge":git("rev-parse","HEAD").decode().strip(),"ids":len(rows),
          "baseline_inventory_sha256":sha((root.parent / "before.json").read_bytes()),"conflicts":[],
          "removed":removed,"runtime":base["runtime"],"second_projection_sha256":sha(projected),
          "full_check":full,"entries":originals}
(report/"T02.json").write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("T02",len(rows),"records;",len(removed),"removed; runtime",sha(projected))
