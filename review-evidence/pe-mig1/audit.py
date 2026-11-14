import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
REPO = ROOT / 'repo'
EVIDENCE = ROOT / 'evidence'
EVIDENCE.mkdir(exist_ok=True)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def write(name, value):
    (EVIDENCE / name).write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n', encoding='utf-8', newline='\n')

def inventory():
    return {p.relative_to(REPO).as_posix(): {'sha256': sha(p.read_bytes()), 'bytes': p.stat().st_size, 'mtime_ns': p.stat().st_mtime_ns}
            for p in sorted(REPO.rglob('*')) if p.is_file() and p.name != '.git'}

def registry(name):
    return json.loads((REPO / name).read_bytes())

mode = sys.argv[1] if len(sys.argv) > 1 else None
if mode == 'before':
    status = subprocess.check_output(['git', 'status', '--porcelain=v1', '--untracked-files=all'], cwd=REPO, text=True)
    assert status == '', status
    content = registry('content/registry.json')
    runtime = registry('game/data/registry.json')
    assert content['format'] == 'picross-content-registry-v4'
    assert runtime['format'] == 'picross-runtime-registry-v7'
    assert len(content['entries']) == len(content['metadata']) == len(runtime['entries']) == 56
    assert len(content['backgrounds']) == 3
    assert {e['id'] for e in content['entries']} == {e['id'] for e in runtime['entries']}
    (EVIDENCE / 'runtime-before.json').write_bytes((REPO / 'game/data/registry.json').read_bytes())
    write('before-inventory.json', inventory())
    write('source-summary.json', {'base': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip(),
        'git_status': status, 'content_format': content['format'], 'runtime_format': runtime['format'],
        'entries': len(runtime['entries']), 'metadata': len(content['metadata']), 'backgrounds': len(content['backgrounds']),
        'categories': len(runtime['categories']),
        'identities': [{**{k: e[k] for k in ('id','key','save_slot','definition')},
                       'revision': registry('game/' + e['definition'].removeprefix('res://'))['revision']} for e in runtime['entries']]})
    print('Clean v4/v7 source confirmed: 56 entries, 56 metadata rows, 3 background bindings;', len(runtime['categories']), 'categories')
elif mode == 'plan':
    plan = json.loads((EVIDENCE / 'migration.json').read_bytes())
    old = json.loads((EVIDENCE / 'runtime-before.json').read_bytes())
    assert plan['old'] == old
    assert plan['new'] == {**old, 'format': 'picross-runtime-registry-v8'}
    assert plan['files'] == ['game/data/registry.json']
    assert inventory() == json.loads((EVIDENCE / 'before-inventory.json').read_bytes())
    print('Plan accepted: exactly runtime v7 -> v8; all entries/categories equal; checkout bytes/mtimes unchanged; plan SHA256', sha((EVIDENCE / 'migration.json').read_bytes()))
elif mode == 'after':
    before = json.loads((EVIDENCE / 'before-inventory.json').read_bytes())
    after = inventory()
    assert set(before) == set(after), (set(before) - set(after), set(after) - set(before))
    changed_bytes = [p for p in before if before[p]['sha256'] != after[p]['sha256']]
    changed_mtimes = [p for p in before if before[p]['mtime_ns'] != after[p]['mtime_ns']]
    assert changed_bytes == changed_mtimes == ['game/data/registry.json'], (changed_bytes, changed_mtimes)
    old_raw = (EVIDENCE / 'runtime-before.json').read_bytes()
    new_raw = (REPO / 'game/data/registry.json').read_bytes()
    assert new_raw == old_raw.replace(b'picross-runtime-registry-v7', b'picross-runtime-registry-v8', 1)
    assert registry('game/data/registry.json') == {**json.loads(old_raw), 'format': 'picross-runtime-registry-v8'}
    (EVIDENCE / 'runtime-after.json').write_bytes(new_raw)
    write('after-inventory.json', after)
    write('migration-result.json', {'changed_bytes': changed_bytes, 'changed_mtimes': changed_mtimes,
        'files_checked': len(before), 'other_files_byte_and_mtime_equal': True,
        'new_files': [], 'removed_files': [], 'runtime_before_sha256': sha(old_raw),
        'runtime_after_sha256': sha(new_raw), 'runtime_bytes': len(new_raw),
        'only_literal_format_byte_changed': True})
    print((EVIDENCE / 'migration-result.json').read_text())
elif mode == 'noop':
    assert inventory() == json.loads((EVIDENCE / 'after-inventory.json').read_bytes())
    plan = json.loads((EVIDENCE / 'noop-migration.json').read_bytes())
    assert plan['old'] == plan['new'] == registry('game/data/registry.json')
    assert plan['files'] == []
    print('Full No-op confirmed: all repository file bytes AND mtimes unchanged; no added/removed files')
