import json, subprocess, hashlib, pathlib, sys
root=pathlib.Path(sys.argv[1]).resolve(); out=root.parent/'evidence'
def git(*a): return subprocess.check_output(['git',*a],cwd=root).decode('utf8').strip()
def show(ref,p): return subprocess.check_output(['git','show',ref+':'+p],cwd=root)
def sha(b): return hashlib.sha256(b).hexdigest()
def save(n,v): (out/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
main=git('rev-parse','origin/main'); integrated='907d40c8e08f6c7777cd579c8f214921c67efd9b'
assert not git('status','--porcelain=v1'); assert git('rev-parse','HEAD')==main
sources={'pz-birne':'2916e94c2d2eeaf8d5ce6ebd15346fe22a20a8d8','pz-erdbeere':'f96583bdddcdc8df2c630fe480857a6e4da1a9f7','pz-zitrone':'b8d797dbb7d4b30c10476e3b8b68ab60780b3d22'}
expected={'pz-birne':('f5d6aaee9e9b986285417a8692bb046b07bad4f3',16107114),'pz-erdbeere':('c94e8cf9bcdd02a6de923c34448e91b8930d84ff',21714958),'pz-zitrone':('d49fd7755f2ac9742951bff0b3fe1a39dfc19291',17355973)}
reg=json.loads((root/'content/registry.json').read_bytes()); runtime=json.loads((root/'game/data/registry.json').read_bytes()); index=json.loads((root/'content/authoring/index.json').read_bytes())
assert reg['format']=='picross-content-registry-v4' and runtime['format']=='picross-runtime-registry-v8'; assert len(reg['entries'])==len(runtime['entries'])==len(reg['metadata'])==len(reg['backgrounds'])==56
assert not any(r['puzzle_id'] in sources for r in index['entries'])
for c in [integrated,main]: assert git('cat-file','-t',c)=='commit'
git('merge-base','--is-ancestor',integrated,main)
sys.path.insert(0,str(root))
from tools.puzzle_production import catalog_publication as pub, catalog_transaction as tx
assert not (root/tx.LOCK).exists() and not pub.staging(root)
rows=[]
for id,source in sources.items():
 assert git('cat-file','-t',source)=='commit'
 entry=next(e for e in reg['entries'] if e['id']==id); prefix=entry['production']['package']; rev=entry['production']['revision']
 trees=[git('rev-parse',c+':'+prefix) for c in [source,integrated,main]]; assert len(set(trees))==1 and trees[0]==expected[id][0]
 assert json.loads(show(source,'content/registry.json'))['entries'].count(entry)==1
 sourceindex=json.loads(show(source,'content/authoring/index.json')); row=next(r for r in sourceindex['entries'] if r['puzzle_id']==id and r['revision']==rev); record=json.loads(show(source,row['record'])); assert record['state']=='registered' and record['blockers']==[]
 assert not (root/'content/authoring'/id).exists()
 manifest=(root/prefix/'manifest.json').read_bytes(); m=json.loads(manifest); assert m['format']=='picross-target-export-v6' and sha(manifest)==entry['production']['package_sha256']
 items=[]
 for line in git('ls-tree','-rl',main,'--',prefix).splitlines():
  metadata,path=line.split('\t',1); mode,kind,oid,size=metadata.split(); p=root/path; assert mode=='100644' and kind=='blob' and p.is_file() and not p.is_symlink() and p.stat().st_size==int(size)
  items.append({'file':path,'bytes':int(size),'blob':oid,'mtime_ns':p.stat().st_mtime_ns})
 assert len(items)==15 and sum(i['bytes'] for i in items)==expected[id][1]
 reveal=json.loads((root/'content/reveals'/(id+'.json')).read_bytes()); bg=json.loads((root/'content/backgrounds'/(id+'.json')).read_bytes()); assert reveal['format']=='picross-catalog-reveal-v4' and bg['format']=='picross-catalog-background-v6' and bg['current']['status']=='selected'
 rows.append({'id':id,'source_commit':source,'revision':rev,'package_tree':trees[0],'files':items,'gross_bytes':sum(i['bytes'] for i in items),'original_manifest_bytes':len(manifest),'original_manifest_sha256':sha(manifest),'registered_record':row['record'],'registered_record_sha256':sha(show(source,row['record']))})
save('preflight.json',{'status':'PASS','main':main,'integrated_commit':integrated,'git_status_before':git('status','--porcelain=v1'),'registry_entries':56,'runtime_entries':56,'selected_index_rows':0,'lock_or_staging':False,'packages':rows,'total_files':sum(len(r['files']) for r in rows),'gross_bytes':sum(r['gross_bytes'] for r in rows)})
save('registry-before.json',reg)
tracked=git('ls-files','-z').split('\0'); stats={}
for name in tracked:
 if name:
  p=root/name; st=p.stat(); stats[name]=[st.st_size,st.st_mtime_ns,st.st_ctime_ns,st.st_ino,st.st_mode]
save('tracked-stats-before.json',stats)
print(json.dumps({'status':'PASS','main':main,'packages':[{k:r[k] for k in ['id','revision','package_tree','gross_bytes','original_manifest_bytes']} for r in rows],'total_files':45,'gross_bytes':sum(r['gross_bytes'] for r in rows)},indent=2))
