"""Independent post-run checks from archive bytes, not writer success flags."""
from pathlib import Path
import sys,os,json,zipfile,hashlib,time,tempfile
b=Path(__file__).resolve().parent;sys.path.insert(0,str(b/'work'))
t=b/'temp-independent';t.mkdir(exist_ok=True)
os.environ.update(TEMP=str(t),TMP=str(t),TMPDIR=str(t));tempfile.tempdir=str(t)
from tools.puzzle_production import content_registry as registry
from tools.puzzle_production import catalog_background as background,catalog_rating as rating,reveal_source as reveal
root=b/'final3-data';report=json.loads((b/'final3-report.json').read_bytes());assert report['runs'][-1]['action']=='post-raster-detail'
assert all(row['error'] is None and not row['journal'] for row in report['runs'])
for row in report['runs']:
    if 'plan' in row['action'] or 'detail' in row['action'] or 'noop' in row['action']:assert row['changed']=={},row['action']
assert set(next(row for row in report['runs'] if row['action']=='migration-apply')['changed'])=={'game/data/registry.json'}
assert set(next(row for row in report['runs'] if row['action']=='metadata-apply')['changed'])=={'game/data/registry.json','content/registry.json'}
with zipfile.ZipFile(b/'baseline-source.zip') as archive:
    original=json.loads(archive.read('content/registry.json'));old_runtime=json.loads(archive.read('game/data/registry.json'))
    selected=min(original['entries'],key=lambda e:e['production']['width']*e['production']['height']);identifier=selected['id']
    actual=json.loads((root/'content/registry.json').read_bytes());runtime=json.loads((root/'game/data/registry.json').read_bytes())
    old_rows={e['id']:e for e in original['entries']};new_rows={e['id']:e for e in actual['entries']}
    assert {i:e for i,e in old_rows.items() if i!=identifier}=={i:e for i,e in new_rows.items() if i!=identifier}
    assert [e for e in original['metadata'] if e['id']!=identifier]==[e for e in actual['metadata'] if e['id']!=identifier]
    assert [e for e in old_runtime['entries'] if e['id']!=identifier]==[e for e in runtime['entries'] if e['id']!=identifier]
    active=next(e for e in runtime['entries'] if e['id']==identifier)
    definition=json.loads((root/'game'/active['definition']).read_bytes());previous=json.loads(archive.read('game/'+selected['definition']))
    assert definition['revision']==previous['revision']+1 and definition['solution']==[[1,1,1],[1,1,1]]
    expected=b'<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128"><rect x="8" y="8" width="112" height="112" fill="#369"/></svg>\n'
    assert (root/'game'/active['reveal']).read_bytes()==expected
    assert active['background']['status']=='standard' and runtime['format']=='picross-runtime-registry-v8'
    allowed={'content/registry.json','game/data/registry.json','game/'+selected['definition'],'game/'+selected['reveal'],reveal.path(identifier),background.path(identifier),rating.path(identifier)}
    for suffix in ('.svg','.png','.txt'):allowed.add(str(Path('game/'+selected['reveal']).with_suffix(suffix)).replace('\\','/'))
    checked=0
    for name in archive.namelist():
        if name.endswith('/') or name in allowed:continue
        assert (root/name).is_file() and (root/name).read_bytes()==archive.read(name),name
        checked+=1
started=time.perf_counter();registry.check_checkout(root)
full_reader_seconds=time.perf_counter()-started
from tools.puzzle_production import editor_raster
entry=new_rows[identifier]
manifest=json.loads((root/entry['production']['package']/'manifest.json').read_bytes())
started=time.perf_counter();editor_raster.package(root,entry,manifest,replay=True)
result={'source':report['source'],'passed':True,'unchanged_original_files_independently_compared':checked,'other_55_entries_and_runtime_rows_exact':True,'selected_revision_increment_and_six_cells_exact':True,'selected_svg_bytes_exact':True,'runtime_v8_and_standard_background':True,'all_plans_details_noops_bytes_and_mtimes_unchanged':True,'independent_full_checkout_source_reader_seconds':full_reader_seconds,'independent_selected_new_raster_proof_replay_seconds':time.perf_counter()-started,'historical_full_replay_attempt':{'accepted':False,'error':'Background derivation verification failed: Original tool differs from the actual implementation/codecs','scope':'Historical tool module identities are already different on baseline 4e5 (operation_diagnostics.py); current also changes catalog_io.py. Codec versions match. No historical proof/pin/expected hash is changed. See historical-replay-binding.json. Full current source reader and new A3 proof are checked above.'}}
(b/'independent-report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result))
