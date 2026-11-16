from pathlib import Path
import json,hashlib,subprocess
base='62401382f58adc2e3d303b19c1ecb1f1dc8a5040';root=Path.cwd();out=root.parent/'t02-independent.json'
def git(*args):return subprocess.check_output(['git',*args])
def old(name):return git('show',base+':'+name)
def sha(raw):return hashlib.sha256(raw).hexdigest()
a=json.loads(old('content/registry.json'));b=json.loads((root/'content/registry.json').read_bytes());assert len(a['entries'])==len(b['entries'])==62
runtime=json.loads(old('game/data/registry.json'));assert old('game/data/registry.json')==(root/'game/data/registry.json').read_bytes()
rows={e['id']:e for e in runtime['entries']};checks=[]
for x,y in zip(a['entries'],b['entries']):
 assert {k:v for k,v in x.items() if k!='production'}|{'mode':x['production']['mode']}==y
 i=x['id'];r=rows[i];names=['game/'+x['definition'],'game/'+r['reveal'],str(Path('game/'+x['reveal']).with_suffix('.txt')).replace('\\','/'),'content/difficulty/'+i+'/rating.json','content/added/'+i+'.json']
 if r['background']['asset']:names+=['game/'+r['background']['asset']['file'],'game/art/backgrounds/'+i+'.txt']
 for name in names:assert old(name)==(root/name).read_bytes(),name
 image_revisions={}
 for kind in ('reveals','backgrounds'):
  name='content/'+kind+'/'+i+'.json';new=json.loads((root/name).read_bytes())
  proc=subprocess.run(['git','show',base+':'+name],capture_output=True)
  prior=json.loads(proc.stdout) if proc.returncode==0 else None
  if prior:
   assert prior.get('record_revision',1)==new['record_revision']
   if 'current' in prior: assert prior['current']==new['current']
   else:
    assert kind=='backgrounds' and prior['format']=='picross-catalog-background-v1'
    assert prior['asset']==new['current']['asset']
    assert {k:new['current'][k] for k in ('status','image_revision')}=={k:r['background'][k] for k in ('status','image_revision')}
  else:assert kind=='reveals' and new['current']['image_revision']==1
  image_revisions[kind]={'before':prior.get('current',r['background'])['image_revision'] if prior else None,'after':new['current']['image_revision'],'created_from_current_entry':prior is None}
 checks.append({'id':i,'mode':y['mode'],'unchanged':{n:sha(old(n)) for n in names},'image_revisions':image_revisions})
# All authoring work, including open Senf/Level lines, remains exact.
names=git('ls-tree','-rz',base,'--','content/authoring').split(b'\0');retained={}
for item in names:
 if not item:continue
 meta,name=item.split(b'\t');name=name.decode();raw=(root/name).read_bytes();assert old(name)==raw;retained[name]=sha(raw)
report={'base':base,'product_head':git('rev-parse','HEAD').decode().strip(),'entries':62,'runtime_sha256':sha(old('game/data/registry.json')),'checks':checks,'all_authoring_unchanged':retained,'metadata_equal':a['metadata']==b['metadata'],'no_solver_or_archives_opened':True}
assert report['metadata_equal'];out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('Independent Git/live comparison passed:',len(checks),'entries;',len(retained),'authoring files')
