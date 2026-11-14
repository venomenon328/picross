"""One-off #645 r07 evidence, outside test discovery; no historical code execution.

Run from the technique checkout using its isolated Pillow interpreter:
  python replay.py --original-root ORIGINAL --payload-root PAYLOAD --evidence-root NEW
ORIGINAL is an owned detached checkout at 58799134bf11e16bae4d946e8f6ebdadda3edfed.
PAYLOAD contains only the unchanged saved approval at the request's exact path.
The original checkout is advanced locally by the real finalizer, never registered.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from unittest.mock import patch

parser = argparse.ArgumentParser()
parser.add_argument('--original-root', required=True, type=Path)
parser.add_argument('--payload-root', required=True, type=Path)
parser.add_argument('--evidence-root', required=True, type=Path)
args = parser.parse_args()
repo = Path.cwd()
sys.path.insert(0, str(repo))
from tools.puzzle_production import background_assets as assets, authoring_package as ap
from tools.puzzle_production import background_package as bp, target_adapter as adapter
from tools.puzzle_production.background_contract import canonical

original = args.original_root.resolve()
payload = args.payload_root.resolve()
evidence = args.evidence_root.resolve()
evidence.mkdir(exist_ok=False)
revision = original / 'content/authoring/pz-fliegenpilz/r07'
saved = original / 'content/authoring/pz-fliegenpilz/evidence/r07-step5'
old = revision / 'background-choice-d01'
request = json.loads((saved / 'finalize-request.json').read_bytes())
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
assert not subprocess.check_output(['git', 'status', '--porcelain'], text=True).strip()

def save(name, value):
    (evidence / name).write_bytes(canonical(value) + b'\n')

def snapshot(root):
    return {p.relative_to(root).as_posix(): (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns)
            for p in root.rglob('*') if p.is_file()}

def cli(name, module, *arguments):
    command = [sys.executable, '-m', module, *map(str, arguments)]
    result = subprocess.run(command, cwd=repo, capture_output=True, timeout=600,
                            env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
    (evidence / (name + '.stdout.json')).write_bytes(result.stdout)
    (evidence / (name + '.stderr.log')).write_bytes(result.stderr or b'(no stderr)\n')
    print(name, result.returncode, flush=True)
    assert result.returncode == 0, (name, result.stdout.decode(), result.stderr.decode())
    return json.loads(result.stdout)

before = snapshot(original / 'content/authoring/pz-fliegenpilz')
catalog = {name: (original / name).read_bytes() for name in ('content/registry.json', 'game/data/registry.json')}
report = json.loads((old / 'derived/derivation.json').read_bytes())
stand = assets.describe()
save('current-description.json', stand)
assert stand['tool']['commit'] == head and stand['tool']['dirty'] is False
assert stand['tool']['versions'] == report['tool']['versions']

# Real central verify, with unchanged inputs assembled at explicit safe roots.
with tempfile.TemporaryDirectory() as temporary:
    source, out = Path(temporary) / 'source', Path(temporary) / 'output'
    with ap.open_files(revision / 'package.zip') as (opened, _, _):
        shutil.copytree(opened, source)
        for name, source_name in (('selected-original.png', report['source']['file']),
                                  ('selected-reveal.png', json.loads((revision / 'handoff.json').read_bytes())['reveal']['file'])):
            shutil.copyfile(opened / source_name, evidence / name)
    for path in old.rglob('*'):
        if path.is_file() and not path.is_relative_to(old / 'derived'):
            dest = source / path.relative_to(old)
            dest.parent.mkdir(parents=True, exist_ok=True)
            assert not dest.exists() or dest.read_bytes() == path.read_bytes()
            dest.write_bytes(path.read_bytes())
    shutil.copytree(old / 'derived', out)
    sources_before, output_before = snapshot(source), snapshot(out)
    checked = assets.verify(report['request'], source, out)
    assert checked['status'] == 'verified', checked
    assert checked['output']['sha256'] == 'a937d68149a2828d19e7295de6d9069da9314dede967a133547f77831536b91f'
    assert checked['derivation']['sha256'] == 'eddc3abfdfca0d60f07bfa9269434dce3b87972f2e72244b40634c3de7bd21b0'
    assert sources_before == snapshot(source) and output_before == snapshot(out)
    save('selected-verify.json', checked)
    shutil.copytree(out, evidence / 'selected-proof')
    save('derive-request.json', report['request'])

finalized = cli('finalize', 'tools.puzzle_production.authoring_builder', 'finalize-background',
    '--request', saved / 'finalize-request.json', '--source-root', payload, '--output-root', original,
    '--history-repo', original)
assert finalized['status'] == 'updated' and finalized['record']['state'] == 'editorially_approved', finalized
assert finalized['record']['background'] == request['background']
after = snapshot(original / 'content/authoring/pz-fliegenpilz')
allowed_changes = {'r07/record.json', 'r07/workspace.json', 'current-view.json'}
changed = [n for n in before if after.get(n) != before[n]]
assert set(changed) <= allowed_changes, changed
assert all(n.startswith('r07/final-editorial-v2/') for n in set(after) - set(before))
for name, raw in catalog.items():
    assert (original / name).read_bytes() == raw
save('unchanged-originals.json', {'existing_files': len(before), 'changed': changed,
    'new': sorted(set(after) - set(before)), 'all_other_existing_bytes_and_mtimes_unchanged': True,
    'catalog_bytes_unchanged': True})
again = cli('finalize-repeat', 'tools.puzzle_production.authoring_builder', 'finalize-background',
    '--request', saved / 'finalize-request.json', '--source-root', payload, '--output-root', original,
    '--history-repo', original)
assert again['status'] == 'reused' and after == snapshot(original / 'content/authoring/pz-fliegenpilz')
approval = original / request['authorizations']['approval.json']['file']
with ap.open_package(revision / 'package.zip', allow_background=True, external_root=original) as package:
    inspection = adapter.inspect(package, approval_path=approval, allow_background=True)[0]
assert inspection['effective_state'] == 'editorially_approved' and inspection['technical'] and inspection['editorial_approved']
save('final-inspection.json', inspection)
export = evidence / 'export'
cli('export', 'tools.puzzle_production.target_adapter', 'export', '--allow-background',
    '--input', revision / 'package.zip', '--external-root', original, '--approval', approval,
    '--name', 'Fliegenpilz', '--runtime-revision', '1', '--stem', 'fliegenpilz', '--save-slot', 'fliegenpilz',
    '--category-id', 'gemuese-pilze-kraeuter', '--categories', original / 'content/categories.json', '--output-dir', export)

# Remove access to the old source paths, prohibit network and history lookup.
authoring = original / 'content/authoring/pz-fliegenpilz'
hidden = original / 'content/authoring/pz-fliegenpilz-unavailable'
authoring.rename(hidden)
hidden_payload = payload.with_name(payload.name + '-unavailable')
payload.rename(hidden_payload)
try:
    with patch.object(bp, '_History', side_effect=AssertionError('Offline must not read old Git')), \
            patch('socket.socket', side_effect=AssertionError('Offline must not use network')):
        manifest, offline = adapter.verify_export(export)
    assert offline['export_verified'] and offline['effective_state'] == 'editorially_approved'
    assert not any(offline[k] for k in ('integration_ready', 'catalog_ready', 'registered'))
    assert (export / 'input/package.zip').read_bytes() == (hidden / 'r07/package.zip').read_bytes()
    assert (export / 'approval.json').read_bytes() == (hidden / 'r07/final-editorial-v2/approval.json').read_bytes()
    save('offline-verify.json', {'original_source_paths_missing': True, 'network_forbidden': True,
        'history_forbidden': True, 'manifest': manifest, 'inspection': offline})
    cli('verify-export', 'tools.puzzle_production.target_adapter', 'verify-export', '--export', export)
finally:
    hidden.rename(authoring)
    hidden_payload.rename(payload)
save('binding.json', {'product_head': head, 'base': 'e1e8caf91d9ad1e6661807e09020c338ad6b6d29',
    'original_head': '58799134bf11e16bae4d946e8f6ebdadda3edfed',
    'historical_tool_commit': report['tool']['commit'], 'historical_tool_sha256': report['tool_sha256'],
    'png_sha256': checked['output']['sha256'], 'derivation_sha256': checked['derivation']['sha256'],
    'profile_sha256': report['profile_sha256'], 'no_registration_or_completion': True,
    'expires': '2026-11-21'})
print('K01-K04: original bindings and isolated finalizer/export/offline proof passed at', head)
