from pathlib import Path
from PIL import Image,ImageOps
import json,hashlib,shutil,time
r=Path(__file__).parent;a=r/'repo/game/art/drawing/rz_eval';c=r/'comparison'
raw=json.loads((r/'generations.json').read_text())
new=json.loads((r/'kl-city.json').read_text())+json.loads((r/'kl-alpha.json').read_text())
assert len(new)==6
provenance=json.loads((a/'provenance.json').read_text())
for row in provenance['images']:
 if row['id'] in ['petronas-1-r2','petronas-2','petronas-3']:
  row['status']='rejected by owner: needs more metropolitan city atmosphere';row['derivatives']=[]
for source_row in new:
 row=source_row.copy();source=Path(row.pop('path'));original=r/'originals'/(row['id']+'.png')
 shutil.copyfile(source,original)
 image=Image.open(original).convert('RGBA');assert image.size==(2172,724)
 row.update(bytes=original.stat().st_size,sha256=hashlib.sha256(original.read_bytes()).hexdigest(),size=list(image.size),alpha_extrema=list(image.getchannel('A').getextrema()),alpha_bbox=image.getchannel('A').getbbox(),derivatives=[])
 if not row['id'].endswith('-alpha'):
  row['status']='rejected implementation attempt: unwanted opaque white fills; corrected by linked ImageGen alpha edit'
 else:
  name='-'.join(row['id'].split('-')[:2])
  for width in [1536,2304,3072]:
   fitted=ImageOps.contain(image,(width,width//4),Image.Resampling.LANCZOS)
   canvas=Image.new('RGBA',(width,width//4),(0,0,0,0));canvas.alpha_composite(fitted,((width-fitted.width)//2,width//4-fitted.height))
   for ext,opts in [('png',dict(optimize=True)),('webp',dict(lossless=True,method=6))]:
    target=c/f'{name}-{width}.{ext}';start=time.perf_counter();canvas.save(target,**opts)
    d=dict(path=target.name,size=list(canvas.size),bytes=target.stat().st_size,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),encode_ms=(time.perf_counter()-start)*1000)
    row['derivatives'].append(d)
    if width==2304 and ext=='png':shutil.copyfile(target,a/target.name)
 provenance['images'].append(row)
raw.extend(new);(r/'generations.json').write_text(json.dumps(raw,ensure_ascii=False,indent=2)+'\n')
provenance['source']='OpenAI built-in image_gen via imagegen skill; 20 independent generations plus 3 transparency correction edits, no third-party image inputs. Edit parent IDs preserve exact source provenance.'
provenance['owner_feedback']='Owner selected Tomate 1, Qualle 2, Hills 1/rev2, Basilisk 3 on the book. Previous KL trio rejected for missing big-city atmosphere; replacement trio pending. Clues must share grid transparency; no hard art cuts, soft edge fade permitted, whole motifs inside area preferred.'
provenance['selection']={'tomate':1,'qualle':2,'hills':1,'petronas':None,'basilisk':3}
provenance['processing']+=' Shared runtime shader edge fade, not baked image retouch. KL alpha corrections were performed exclusively by ImageGen against the named parent originals.'
(c/'manifest.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
for row in provenance['images']:
 row['derivatives']=[{k:v for k,v in d.items() if k!='encode_ms'} for d in row['derivatives'] if d['path'].endswith('-2304.png')]
(a/'provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
print('23 ImageGen calls, 20 independent originals + 3 edits; 15 current candidates, 8 superseded/rejected attempts.')
