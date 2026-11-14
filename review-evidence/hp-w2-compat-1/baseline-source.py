import hashlib
import json
from pathlib import Path
import subprocess
import sys

task = Path(__file__).resolve().parent
repo = task / 'repo'
sys.path.insert(0, str(repo))
from tools.puzzle_production import background_assets as assets, authoring_builder as builder
from tools.puzzle_production.background_contract import canonical, digest

out = task / 'evidence'
out.mkdir(exist_ok=True)
isolated = task / 'isolated'
revision = isolated / 'content/authoring/pz-fliegenpilz/r07'
saved = isolated / 'content/authoring/pz-fliegenpilz/evidence/r07-step5'
report = json.loads((revision / 'background-choice-d01/derived/derivation.json').read_bytes())
current = assets.describe()
original = report['tool']
assert digest(original) == '23971ee3834218f28977a346e09f716de6eb18fd6fc3acb8cab25a5ad8cab691'
assert original['dirty'] is False
assert original['versions'] == current['tool']['versions']
assert report['profile'] == current['profile']
sources = []
for row in original['modules']:
    raw = subprocess.check_output(['git', 'show', original['commit'] + ':' + row['file']], cwd=repo)
    assert hashlib.sha256(raw).hexdigest() == row['sha256'], row
    sources.append({**row, 'bytes': len(raw)})
changed = [r['file'] for r, c in zip(original['modules'], current['tool']['modules']) if r != c]
assert changed == ['tools/puzzle_production/catalog_io.py', 'tools/puzzle_production/operation_diagnostics.py'], changed
payload = task / 'payload'
approval = payload / 'content/authoring/pz-fliegenpilz/r07/final-editorial-v2/approval.json'
approval.parent.mkdir(parents=True)
approval.write_bytes((saved / 'approval.json').read_bytes())
request = json.loads((saved / 'finalize-request.json').read_bytes())
def snapshot():
    return {p.relative_to(isolated).as_posix(): (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns)
            for prefix in ('content/authoring', 'content/registry.json', 'game/data/registry.json')
            for p in ([isolated / prefix] if (isolated / prefix).is_file() else (isolated / prefix).rglob('*')) if p.is_file()}
before = snapshot()
result = builder.finalize_background(request, payload, isolated, history_repo=isolated)
assert result['status'] == 'invalid_input', result
assert 'Original tool differs from the actual implementation/codecs' in result['message'], result
assert before == snapshot()
assert not (revision / 'final-editorial-v2').exists()
evidence = {'source_head': subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip(),
            'original_head': '58799134bf11e16bae4d946e8f6ebdadda3edfed',
            'historical_tool': original, 'historical_sources': sources, 'current': current,
            'changed_modules': changed, 'finalize_result': result, 'no_mutation': True}
(out / 'baseline.json').write_bytes(canonical(evidence) + b'\n')
print(json.dumps(evidence, ensure_ascii=False, indent=2))
