"""One-time RZ-EVAL derivation, explicitly requested size/format comparison."""
from pathlib import Path
from PIL import Image, ImageOps
import hashlib, json, time, shutil

root = Path(__file__).resolve().parent
assets = root / 'repo/game/art/drawing/rz_eval'
assets.mkdir(parents=True, exist_ok=True)
originals = root / 'originals'
originals.mkdir(exist_ok=True)
rows = json.loads((root/'generations.json').read_text(encoding='utf-8'))
manifest = []
for row in rows:
    source = Path(row.pop('path'))
    target = originals / (row['id']+'.png')
    shutil.copyfile(source, target)
    row.update(bytes=target.stat().st_size, sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    image = Image.open(target).convert('RGBA')
    row['size'] = list(image.size)
    row['alpha_extrema'] = list(image.getchannel('A').getextrema())
    row['alpha_bbox'] = image.getchannel('A').getbbox()
    row['derivatives'] = []
    if row['id'] in ('petronas-1','hills-1'):
        manifest.append(row)
        continue
    name = row['id'].replace('-r2','')
    for width in (1536,2304,3072):
        size = (width,width//4)
        fitted = ImageOps.contain(image,size,Image.Resampling.LANCZOS)
        canvas = Image.new('RGBA',size,(0,0,0,0))
        # One identical contain/centre/bottom rule, no per-image crop or position.
        canvas.alpha_composite(fitted,((width-fitted.width)//2,size[1]-fitted.height))
        for ext,opts in [('png',dict(optimize=True)),('webp',dict(lossless=True,method=6))]:
            file = assets/f'{name}-{width}.{ext}'
            start = time.perf_counter()
            canvas.save(file,**opts)
            row['derivatives'].append(dict(path=file.name,size=list(size),bytes=file.stat().st_size,
                sha256=hashlib.sha256(file.read_bytes()).hexdigest(),encode_ms=(time.perf_counter()-start)*1000))
    manifest.append(row)
Image.new('RGBA',(3072,768),(0,0,0,0)).save(originals/'transparent-control.png')
provenance = dict(format='picross-rz-eval-provenance-v1',package='RZ-EVAL-P1',created='2026-11-09',
    decision='https://github.com/venomenon328/picross/issues/558#issuecomment-6739323575',
    source='OpenAI built-in image_gen via imagegen skill; 16 independent original generations, no input/third-party asset bytes',
    rights='User-authorized original generations for this project; no exclusive-rights claim; final owner image approval pending.',
    processing='Pillow 12.3.0. Same proportional LANCZOS contain, horizontal centre and bottom anchor on RGBA 4:1 canvas at every size; no crop, no art retouch, no alpha replacement, no per-ID layout. Original bytes preserved on separate expiring review ref.',
    owner_feedback='No puzzle subject in drawings. Prefer level/U/half-U silhouette with low centre, not a strict height restriction. Three-tower central peak rejected; others considered okay as drafts, not final book approval.',
    images=manifest)
(assets/'provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
(assets/'NOTICE.txt').write_text('RZ-EVAL-P1 / issue 558\nOriginal ImageGen illustrations generated for this project on 2026-11-09.\nNo third-party image inputs. No claim of exclusive rights.\nExperimental candidates, no final owner image approval or stock adoption.\nSee provenance.json for exact briefs, hashes, derivations and owner feedback.\n',encoding='utf-8',newline='\n')
print(json.dumps(dict(originals=len(rows),derivatives=sum(len(r['derivatives']) for r in manifest),bytes=sum(p.stat().st_size for p in assets.iterdir())),indent=2))
