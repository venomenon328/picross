from pathlib import Path
from PIL import Image
import subprocess,hashlib,json,base64
r=Path(__file__).parent;out=r/'binary-blob';out.mkdir(exist_ok=True)
commit='3588efc8523654d8b00b0a4def25d6f2d2fb5f84';prefix='review/558-rz-eval-p1/'
def fetch(name):
 tree=subprocess.check_output(['git','ls-tree',commit,'--',prefix+name],cwd=r/'binary-check',text=True)
 oid=tree.split()[2]
 raw=subprocess.check_output(['gh','api','-H','Accept: application/vnd.github+json',f'repos/venomenon328/picross/git/blobs/{oid}'])
 blob=json.loads(raw);assert blob['encoding']=='base64'
 data=base64.b64decode(''.join(blob['content'].split()),validate=True)
 assert len(data)==blob['size'] and hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()==oid
 path=out/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data);return data
manifest=json.loads(fetch('manifest.json'));assert manifest['product_head']=='535403d8ac89c2da4800719f0d4a0fe0ba041950'
rows=[]
for name in ['originals/petronas-3-r3-alpha.png','owner-diagnostics/reference-4k.png','logs/test-p1-owner.log']:
 row=next(x for x in manifest['files'] if x['path']==name);data=fetch(name)
 assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],name
 if name.endswith('.png'):
  with Image.open(out/name) as image:image.load();assert list(image.size)==row['size']
 rows.append(row)
report=dict(evidence_commit=commit,product_head=manifest['product_head'],route='GitHub Git Blob API: complete base64 binary payload decoded to original bytes; Git blob SHA-1, byte length, SHA-256 and PNG decode checked. Two originals >1 MiB; exact CRLF log verified too. No truncated Contents content/preview substitute.',verified=rows)
(r/'current-binary-access.json').write_text(json.dumps(report,indent=2)+'\n',newline='\n');print(json.dumps(report))
