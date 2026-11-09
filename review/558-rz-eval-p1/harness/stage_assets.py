from pathlib import Path
import json, shutil
root=Path(__file__).resolve().parent
assets=root/'repo/game/art/drawing/rz_eval'
comparison=root/'comparison'
comparison.mkdir(exist_ok=True)
provenance=json.loads((assets/'provenance.json').read_text(encoding='utf-8'))
(comparison/'manifest.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
for file in assets.iterdir():
    if file.suffix not in ('.png','.webp'): continue
    shutil.copyfile(file,comparison/file.name)
    if not file.name.endswith('-2304.png'): file.unlink()
for row in provenance['images']:
    row['derivatives']=[d for d in row['derivatives'] if d['path'].endswith('-2304.png')]
    for item in row['derivatives']: item.pop('encode_ms',None)
provenance['comparison']='Other profiles/formats are temporary comparison data on the separate review ref; only 2304 PNG candidates ship in this experiment.'
(assets/'provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Staged 15 runtime candidates; 90 comparison derivatives separate.')
