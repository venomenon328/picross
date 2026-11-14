import hashlib
import json
from pathlib import Path
import shutil

root = Path(__file__).resolve().parent
repo = root / 'repo'
project = root / 'temp' / 'reader-project'
project.mkdir()
runtime = json.loads((repo / 'game/data/registry.json').read_bytes())
assert runtime['format'] == 'picross-runtime-registry-v8'
names = ['model/content_registry.gd', 'model/catalog_difficulty.gd', 'model/definition.gd',
         'data/registry.json', 'data/background-capability.json'] + [e['definition'] for e in runtime['entries']]
manifest = {}
for name in names:
    source = repo / 'game' / name
    target = project / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    assert target.read_bytes() == source.read_bytes()
    manifest['game/' + name] = hashlib.sha256(source.read_bytes()).hexdigest()
(root / 'evidence' / 'reader-inputs.json').write_text(json.dumps(manifest, sort_keys=True, indent=2) + '\n', encoding='utf-8')
shutil.copyfile(root / 'reader_probe.gd', project / 'probe.gd')
(project / 'project.godot').write_text('config_version=5\n[application]\nconfig/name="PE-MIG1 isolated reader"\nconfig/use_custom_user_dir=true\nconfig/custom_user_dir_name="PE-MIG1-isolated-reader"\n', encoding='utf-8')
print('Prepared isolated reader project with byte-identical production readers, v8 registry, capability and all 56 definitions; no SaveStore code or user saves')
