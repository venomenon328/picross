"""Once-only input inventory, generated before any source change."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0, str(Path.cwd()))
from tools.puzzle_production import current_content as c, current_rating, categories
from tools.puzzle_production.contract import digest

root = Path.cwd()
target = root.parent
def read(path):
    return json.loads((root / path).read_bytes())
def hashref(path):
    raw = (root / path).read_bytes()
    return c.ref(path, raw)

index = read(c.REGISTRY)
catalog = categories.load(root/categories.PATH)
runtime = read(c.RUNTIME)
entries = []
errors = []
for e, meta, bg in zip(index['entries'], index['metadata'], index['backgrounds'], strict=True):
    identifier = e['id']
    d = c.selected(root, index, identifier)
    assert d['entry'] == e and d['metadata'] == meta and e['category_id'] == meta['category_id']
    row = c.runtime_row(d)
    assert row == next(r for r in runtime['entries'] if r['id'] == identifier)
    rating = d['rating']
    active = {k: rating[k] for k in current_rating.FIELDS - {'format','method','record_hash'}}
    active.update(format=current_rating.FORMAT, method=rating['rating']['method'])
    active['record_hash'] = digest(active)
    try:
        current_rating.validate(active, definition_bytes=d['definition'], production_mode=e['mode'], active=True)
    except Exception as exc:
        errors.append((identifier,str(exc)))
    paths = [c.source_path(identifier,'reveal'),c.source_path(identifier,'background'),c.added.path(identifier),c.rating.path(identifier)]
    rights = [c.notice_path(e)]
    if d.get('background_notice') is not None:
        rights.append('game/art/backgrounds/'+identifier+'.txt')
    reveal = d['reveal']
    background = d['background']['current']
    assets = [d['reveal']['binding']['identity']['definition'], reveal['current']['asset'], *[p['asset'] for p in reveal['catalog']['profiles']]]
    if background['asset'] is not None:
        assets.append(background['asset'])
    assert all(hashref(a['file']) == a for a in assets)
    field_values = dict(id=identifier,name=meta['name'],category_id=meta['category_id'],save_slot=e['save_slot'],mode=e['mode'],visible=e['visible'],
        definition=assets[0],added={k:d['added'][k] for k in ('added_at','provenance')},
        reveal={**reveal['current'],'catalog':{k:v for k,v in reveal['catalog'].items() if k != 'source_sha256'}},
        background=background,difficulty={k:rating[k] for k in ('rating_revision','rating','compact_analysis')} |
        {'logic_binding':{'matrix_hash':rating['logic_binding']['matrix_hash']}})
    assert rating['logic_binding']['analysis_hash'] == rating['compact_analysis']['analysis_hash']
    entries.append({'id':identifier,'expected':field_values,'removed':[hashref(p) for p in paths],
        'rights':[hashref(p) for p in rights],'assets':assets,'runtime_row_sha256':digest(row)})
result = {'base':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
          'registry':hashref(c.REGISTRY),'runtime':hashref(c.RUNTIME),'categories':hashref(categories.PATH),
          'entries':entries,'validation_errors':errors}
(target/'before.json').write_bytes(c.encoded(result))
print('IDs',len(entries),'current rating projection errors',errors)
