import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent / 'repo'
SOURCE = 'e3b177673011c5477dd605c24420fef589e8f878'
BASE = '5fc8effc740dc37eafc7d513a253c7a6a6ff6e07'
PID = 'pz-fliegenpilz'
PREFIX = f'content/authoring/{PID}'

def git(*args, input=None):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], input=input)

def old_json(path):
    return json.loads(git('show', f'{BASE}:{path}'))

def current(path):
    return json.loads((ROOT / path).read_bytes())

originals = {}
mutable = {f'{PREFIX}/r07/record.json', f'{PREFIX}/r07/workspace.json', f'{PREFIX}/current-view.json'}
for row in git('ls-tree', '-r', SOURCE, PREFIX).decode().splitlines():
    info, path = row.split('\t')
    if path not in mutable:
        originals[path] = info.split()[2]
observed = git('hash-object', '--stdin-paths', input=('\n'.join(originals)+'\n').encode()).decode().splitlines()
assert observed == list(originals.values()), 'Original production bytes changed'

content = current('content/registry.json')
runtime = current('game/data/registry.json')
for path, new, fields in [('content/registry.json', content, ['entries','metadata','backgrounds']),
                          ('game/data/registry.json', runtime, ['entries'])]:
    old = old_json(path)
    assert new['format'] == old['format']
    for field in fields:
        assert [x for x in new[field] if x['id'] != PID] == old[field], (path,field)
    assert len(new['entries']) == len(old['entries']) + 1
assert runtime['categories'] == old_json('game/data/registry.json')['categories']
index = current('content/authoring/index.json')['entries']
assert [e for e in index if e['puzzle_id'] != PID] == old_json('content/authoring/index.json')['entries']

old_changes = []
for row in git('diff', '--name-status', BASE, '--', 'content', 'game').decode().splitlines():
    status, path = row.split('\t')
    if status != 'A':
        assert path in {'content/registry.json', 'game/data/registry.json', 'content/authoring/index.json'}, row
        old_changes.append(path)

entry = next(e for e in runtime['entries'] if e['id'] == PID)
definition = current('game/' + entry['definition'])
assert (definition['width'], definition['height'], definition['revision']) == (14,22,1)
assert len(definition['palette']) == 2
assert entry['save_slot'] == 'fliegenpilz_001'
assert entry['difficulty']['level'] == 'L2'
assert entry['difficulty']['method'] == 'picross-difficulty-0.4'
assert entry['background']['status'] == 'selected'
for path, expected in [('game/art/content/fliegenpilz_001.png','e18b0894bed89ca950289554ffe3944b739efdbe8eeb3c9b64303ed1b6f26db9'),
                       ('game/art/backgrounds/pz-fliegenpilz.png','a937d68149a2828d19e7295de6d9069da9314dede967a133547f77831536b91f'),
                       (f'{PREFIX}/r07/package.zip','0ca64ae2eee8c317d7ed1d34978180f26029cb91e3276bf7201a682b444057bd'),
                       (f'{PREFIX}/r07/final-editorial-v2/approval.json','b360b8c5f3c686d8fc717887ca62a0ffbf69a89851a23698c70cab4033af426f')]:
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == expected, path
assert not (ROOT/'content/.registration-pending.json').exists()
assert not list((ROOT/'content').glob('.registration-journal-*.tmp'))
result = {'source_commit':SOURCE, 'base_commit':BASE, 'unchanged_original_files':len(originals),
          'preserved_existing_catalog_entries':len(runtime['entries'])-1,
          'existing_files_changed':old_changes, 'runtime':entry,
          'dimensions':[14,22], 'colors':2, 'runtime_revision':1,
          'no_pending_registration':True, 'test_only':False}
print(json.dumps(result,ensure_ascii=False))
