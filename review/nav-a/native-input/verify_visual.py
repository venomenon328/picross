from pathlib import Path
import hashlib,json,re,subprocess
root=Path.cwd();base=root.parent;project=base/'visual-final2/game'
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
assert not subprocess.check_output(['git','status','--porcelain'],text=True).strip()
observed=json.loads((base/'originals-final2/observations.json').read_text(encoding='utf-8'))
assert observed['product_head']==head and not observed['failures']
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def settings(path):
 section='';result={};key=None;value=[]
 for line in path.read_text(encoding='utf-8').splitlines():
  if key is not None:
   value.append(line)
   if line.strip()=='}':result[(section,key)]=re.sub(r'\s+','',''.join(value));key=None
  elif line.startswith('['):section=line
  elif '=' in line:
   name,body=line.split('=',1)
   if body.strip()=='{':key=name;value=[body]
   else:result[(section,name)]=re.sub(r'\s+','',body)
 return result
bindings=[]
for source in (root/'game').rglob('*'):
 if not source.is_file() or source.relative_to(root/'game').parts[0] in ('data','build','.godot'):continue
 if 'content' in source.parts:continue
 if source.relative_to(root/'game').parts[0]=='tests' and source.suffix!='.gd':continue
 target=project/source.relative_to(root/'game')
 record={'path':source.relative_to(root).as_posix(),'source_sha256':sha(source),'tested_sha256':sha(target)}
 if source.suffix=='.import':
  a,b=settings(source),settings(target)
  assert all(b.get(k)==v for k,v in a.items()),source
  record['engine_added_defaults']={section+'/'+key:value for (section,key),value in b.items() if (section,key) not in a}
 else:assert source.read_bytes()==target.read_bytes(),source
 bindings.append(record)
(base/'originals-final2/runtime-binding.json').write_text(json.dumps({'product_head':head,'runtime':'actual native root Window; product code/assets byte-equal; isolated synthetic registry; import sidecars preserve every source setting with engine-added defaults','bindings':bindings},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('BOUND',head,'runtime files',len(bindings),'all assertions',len(observed['rows']))
