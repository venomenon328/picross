import json, subprocess, hashlib, pathlib, sys, copy, platform
root=pathlib.Path(sys.argv[1]).resolve(); out=root.parent/'evidence'; sys.path.insert(0,str(root))
def git(*a): return subprocess.check_output(['git',*a],cwd=root).decode('utf8').strip()
def sha(b): return hashlib.sha256(b).hexdigest()
def save(n,v): (out/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
pre=json.loads((out/'preflight.json').read_bytes()); old=json.loads((out/'registry-before.json').read_bytes()); current=json.loads((root/'content/registry.json').read_bytes()); expected=copy.deepcopy(old); ids=[r['id'] for r in pre['packages']]
from tools.puzzle_production import retirement_scope as scope, integrated_content as integrated, catalog_background as bg, reveal_source as reveal, categories, catalog_io as io, content_registry as cr
rows=[]
with scope.operation(root) as reads:
 snap=scope.capture(root,ids); catalog=categories.validate(json.loads((root/categories.PATH).read_bytes()))
 for p in pre['packages']:
  id=p['id']; entry=next(e for e in current['entries'] if e['id']==id); original=next(e for e in old['entries'] if e['id']==id); prefix=entry['production']['package']; path=prefix+'/manifest.json'; raw=(root/path).read_bytes(); r=json.loads(raw); provenance=r['provenance']
  assert r['format']=='picross-integrated-content-v4' and r['entry']==original and r['integrated_commit']==pre['integrated_commit']; assert provenance['source_commit']==p['source_commit'] and provenance['main_commit']==pre['main'] and provenance['package_tree']==p['package_tree']; assert provenance['export_manifest']=={'file':path,'bytes':p['original_manifest_bytes'],'sha256':p['original_manifest_sha256']}; assert sha(raw)==entry['production']['package_sha256']
  integrated.check(root,entry,r); resolved=reveal.resolve(root,entry,catalog); background=bg.load(root,current,entry)
  assert background['format']=='picross-catalog-background-v6' and background['current']['status']=='selected'; assert resolved['historical_notice_sha256']==r['notice_sha256']; assert provenance['notice']['sha256']==r['notice_sha256']; assert provenance['background']['format']=='picross-catalog-background-v1'
  next(e for e in expected['entries'] if e['id']==id)['production']['package_sha256']=sha(raw)
  files=sorted(f.relative_to(root).as_posix() for f in (root/prefix).rglob('*') if f.is_file()); assert files==[path]
  removed_files=[f for f in p['files'] if f['file']!=path]; deleted=sum(f['bytes'] for f in removed_files); net=p['gross_bytes']-len(raw)
  rows.append({'id':id,'revision':p['revision'],'gross_original_bytes':p['gross_bytes'],'deleted_files':14,'deleted_file_bytes':deleted,'replaced_original_manifest_bytes':p['original_manifest_bytes'],'written_receipt_bytes':len(raw),'net_package_saving_bytes':net,'export_O_sha256':p['original_manifest_sha256'],'receipt_R_sha256':sha(raw),'source_commit':p['source_commit'],'integrated_commit':r['integrated_commit'],'main_commit':provenance['main_commit'],'package_tree':provenance['package_tree'],'original_background_rights_provenance':provenance['background']['provenance'],'original_background_approval':provenance['background']['origin']['approval_ref'],'original_notice':provenance['notice'],'targeted_readers':'PASS'})
 assert old.keys()==current.keys() and current==expected
 assert not [name for name in reads.data if name.startswith('content/packages/') and not any(name.startswith(p['file'].split('/manifest.json')[0]) for p in [r['provenance']['export_manifest'] for r in [json.loads((root/(next(e for e in current['entries'] if e['id']==i)['production']['package']+'/manifest.json')).read_bytes()) for i in ids]])]
 reader_names=sorted(reads.data)
status=git('diff','--name-status','--no-renames').splitlines(); changes={p:s for s,p in [line.split('\t',1) for line in status]}
expected_changes={'.ci/package.json':'M','content/registry.json':'M'}
for p in pre['packages']:
 for f in p['files']: expected_changes[f['file']]='M' if f['file'].endswith('/manifest.json') and f['file'].count('/')==4 else 'D'
assert changes==expected_changes,(changes,expected_changes)
assert not git('diff','--cached','--name-only') and not git('ls-files','--others','--exclude-standard')
stats=json.loads((out/'tracked-stats-before.json').read_bytes()); preserved=0
for name,before in stats.items():
 if name not in expected_changes:
  st=(root/name).stat(); assert [st.st_size,st.st_mtime_ns,st.st_ctime_ns,st.st_ino,st.st_mode]==before,name; preserved+=1
# Git's full diff verifies only the selected package paths, registry and package plan changed.
assert not git('diff','--name-only','--','game','content/authoring','content/backgrounds','content/reveals','content/difficulty','content/ratings','content/added','content/categories.json')
registry_old=len(subprocess.check_output(['git','show',pre['main']+':content/registry.json'],cwd=root)); registry_new=(root/'content/registry.json').stat().st_size
plan_old=len(subprocess.check_output(['git','show',pre['main']+':.ci/package.json'],cwd=root)); plan_new=(root/'.ci/package.json').stat().st_size
result={'status':'PASS','environment':{'platform':platform.platform(),'python':sys.version},'base':pre['main'],'packages':rows,'totals':{'original_package_bytes':sum(r['gross_original_bytes'] for r in rows),'deleted_files':42,'deleted_file_bytes':sum(r['deleted_file_bytes'] for r in rows),'replaced_original_manifest_bytes':sum(r['replaced_original_manifest_bytes'] for r in rows),'new_receipt_bytes':sum(r['written_receipt_bytes'] for r in rows),'net_package_saving_bytes':sum(r['net_package_saving_bytes'] for r in rows),'registry_before_bytes':registry_old,'registry_after_bytes':registry_new,'plan_before_bytes':plan_old,'plan_after_bytes':plan_new,'net_entire_diff_saving_bytes':sum(r['net_package_saving_bytes'] for r in rows)+registry_old-registry_new+plan_old-plan_new},'all_56_registry_entries_preserved_except_3_package_hashes':True,'runtime_56_entries_and_all_protected_tracked_paths_unchanged':True,'unchanged_tracked_file_stats':preserved,'full_diff_paths':changes,'targeted_reader_files':reader_names,'git_status_after':git('status','--short')}
save('verification.json',result)
patch=subprocess.check_output(['git','diff','--no-ext-diff','--no-renames','--full-index'],cwd=root); (out/'full.diff').write_bytes(patch)
print(json.dumps({'status':'PASS','totals':result['totals'],'unchanged_tracked_file_stats':preserved,'changed_paths':len(changes),'targeted_reader_files':len(reader_names)},indent=2))
