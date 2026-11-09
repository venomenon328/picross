from pathlib import Path
import json, hashlib, math, os, subprocess
from PIL import Image,ImageChops
base=Path(__file__).resolve().parent
folder=base/os.environ.get('RAND_ORIGINALS','originals-current')
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=base/'repo',text=True).strip()
reports=[json.loads((folder/name).read_text(encoding='utf-8')) for name in ['native.json','native-extra.json']]
records=[]
for report in reports:
    assert report['passed'] and report['head']==head and report['assertions']
    assert all(row['ok'] for row in report['assertions'])
    records+=report['records']
assert len({row['file'] for row in records})==len(records)
files={}
for row in records:
    path=folder/row['file']
    image=Image.open(path)
    assert list(image.size)==row['viewport'] and row['head']==head
    files[row['file']]=dict(bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),viewport=row['viewport'],ui_scale=row['ui_scale'],family=row['family'],requested_cell=row['geometry']['requested_cell'],actual_cell=row['geometry']['cell_size'])
comparisons=[]
by_file={row['file']:row for row in records}
for name,row in by_file.items():
    if not name.endswith('-with.png'): continue
    without=name[:-9]+'-without.png'
    other=by_file[without]
    assert row['geometry']==other['geometry'] and row['chapter']==other['chapter'] and row['help_scroll']==other['help_scroll']
    before=Image.open(folder/name).convert('RGB');after=Image.open(folder/without).convert('RGB')
    diff=ImageChops.difference(before,after)
    bounds=diff.getbbox()
    pixels=diff.load()
    boxes=[(math.floor(x)-2,math.floor(y)-2,math.ceil(x+w)+2,math.ceil(y+h)+2) for x,y,w,h in row['boxes'] if w>0 and h>0]
    outside=changed=0
    if bounds:
        for y in range(bounds[1],bounds[3]):
            for x in range(bounds[0],bounds[2]):
                if pixels[x,y]!=(0,0,0):
                    changed+=1
                    if not any(left<=x<right and top<=y<bottom for left,top,right,bottom in boxes):outside+=1
    assert outside==0,(name,'differences outside drawing regions',outside)
    if boxes: assert changed>0,(name,'invisible candidate')
    else: assert changed==0,(name,'hidden art changes rendering')
    comparisons.append(dict(with_file=name,without_file=without,geometry_identical=True,changed_pixels=changed,outside_drawing_regions=outside,difference_bounds=bounds))
manifest=dict(package='RAND-P1',product_head=head,files=files,comparisons=comparisons,assertions=sum(len(r['assertions']) for r in reports),passed=True)
(folder/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print('VERIFIED',len(files),'PNG originals;',len(comparisons),'exact-geometry comparisons;',manifest['assertions'],'native assertions; no changed pixel outside drawing bounds')
