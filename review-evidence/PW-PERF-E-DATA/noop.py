import sys,json,pathlib,subprocess,hashlib,contextlib,io as stdio,zipfile,collections,os
from unittest.mock import patch
root=pathlib.Path(sys.argv[1]).resolve();sys.path.insert(0,str(root));out=root.parent/'evidence'
from tools.puzzle_production import target_adapter as adapter, catalog_io as io, content_registry as cr, retirement_scope as scope, catalog_background as bg
args=['retire-production','--checkout',str(root),'--integrated-commit','907d40c8e08f6c7777cd579c8f214921c67efd9b','--puzzle-id','pz-birne','--puzzle-id','pz-erdbeere','--puzzle-id','pz-zitrone','--source-commit','pz-birne','2916e94c2d2eeaf8d5ce6ebd15346fe22a20a8d8','--source-commit','pz-erdbeere','f96583bdddcdc8df2c630fe480857a6e4da1a9f7','--source-commit','pz-zitrone','b8d797dbb7d4b30c10476e3b8b68ab60780b3d22']
def snapshot():
 result={}
 for base,dirs,files in os.walk(root):
  for name in dirs+files:
   p=pathlib.Path(base)/name;st=p.lstat();result[p.relative_to(root).as_posix()]=[st.st_mode,st.st_size,st.st_mtime_ns,st.st_ctime_ns,st.st_ino]
 return result
def forbidden(*a,**kw): raise AssertionError('No-op attempted ZIP/build/write/delete/lock')
counts=collections.Counter(); rawread=io._read
def count(r,n,limit,**kw):
 p=(pathlib.Path(r)/n).absolute()
 if p.is_relative_to(root):counts[p.relative_to(root).as_posix()]+=1
 return rawread(r,n,limit,**kw)
before=snapshot();buf=stdio.StringIO();status_before=subprocess.check_output(['git','diff','--no-ext-diff','--full-index'],cwd=root)
with contextlib.redirect_stdout(buf),patch.object(zipfile,'ZipFile',side_effect=forbidden),patch.object(bg,'build',side_effect=forbidden),patch.object(cr,'atomic_bytes',side_effect=forbidden),patch.object(scope.Reads,'acquire',side_effect=forbidden),patch.object(pathlib.Path,'unlink',side_effect=forbidden),patch.object(pathlib.Path,'rmdir',side_effect=forbidden),patch.object(pathlib.Path,'write_bytes',side_effect=forbidden),patch.object(pathlib.Path,'write_text',side_effect=forbidden),patch.object(io,'_read',side_effect=count):
 code=adapter.main(args)
assert code==0,buf.getvalue(); result=json.loads(buf.getvalue());assert result['status']=='no-op',result
assert snapshot()==before
assert subprocess.check_output(['git','diff','--no-ext-diff','--full-index'],cwd=root)==status_before
ids=['pz-birne','pz-erdbeere','pz-zitrone']
assert not any(n.endswith('.zip') for n in counts)
assert not any(n.startswith('content/packages/') and not any(n.startswith('content/packages/'+i+'/') for i in ids) for n in counts)
report={'status':'PASS','native_cli_result':result,'fresh_process':True,'same_ids_source_and_integration_commits':True,'file_and_directory_stat_entries_unchanged':len(before),'full_diff_bytes_unchanged':True,'zip_open_attempts':0,'background_original_build_attempts':0,'atomic_write_lock_delete_attempts':0,'physical_catalog_reads':dict(sorted(counts.items()))}
(out/'noop.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n');(out/'noop-stdout.json').write_text(buf.getvalue(),encoding='utf8',newline='\n')
print(json.dumps({k:v for k,v in report.items() if k!='physical_catalog_reads'},indent=2))
