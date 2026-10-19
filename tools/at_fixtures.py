"""Fixed AT graphics and export identity, exclusively for disposable test players."""
import hashlib
import json
import shutil

from PIL import Image, ImageDraw

POINTS = {'outside': [4, 4], 'white': [76, 76], 'hole': [154, 154], 'soft': [16, 128], 'ink': [128, 64]}
COLORS = {1: (56, 132, 90), 2: (174, 85, 52)}


def image(path, revision=1):
    if revision not in COLORS: raise ValueError('Unknown AT synthetic image revision')
    color = COLORS[revision]
    value = Image.new('RGBA', (256,256), (0,0,0,0))
    draw = ImageDraw.Draw(value)
    draw.ellipse((8,8,247,247),fill=(*color,80))
    draw.ellipse((24,24,231,231),fill=(*color,255))
    draw.rectangle((64,64,88,88),fill=(255,255,255,255))
    draw.ellipse((140,140,168,168),fill=(0,0,0,0))
    value.save(path)
    return dict(format='picross-at-fixture-v1',test_only=True,image_revision=revision,
                image_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                rgba_sha256=hashlib.sha256(value.tobytes()).hexdigest(),size=list(value.size),
                samples={k:dict(point=p,rgba=list(value.getpixel(tuple(p)))) for k,p in POINTS.items()})


def install(project, revision=1):
    path=project/'art/fixtures/at.png';path.parent.mkdir(parents=True,exist_ok=True)
    result=image(path,revision)
    registry_path=project/'data/registry.json'
    registry=json.loads(registry_path.read_text(encoding='utf-8'))
    result['definitions']={}
    for key in ('t01','t04'):
        path=project/'data/fixtures'/f'{key}.json'
        reveal=f'art/fixtures/at-{key}.png'
        shutil.copyfile(project/'art/fixtures/at.png',project/reveal)
        data=json.loads(path.read_text(encoding='utf-8'));data['reveal']['image']='res://'+reveal
        path.write_text(json.dumps(data,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n',encoding='utf-8',newline='\n')
        entry=next(e for e in registry['entries'] if e['definition']==f'data/fixtures/{key}.json')
        entry['reveal']=reveal
        result['definitions'][data['id']]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                                         'revision':data['revision'],'save_slot':entry['save_slot']}
    registry_path.write_text(json.dumps(registry,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n',encoding='utf-8',newline='\n')
    result['registry_sha256']=hashlib.sha256(registry_path.read_bytes()).hexdigest()
    path=project/'tests/at-fixture.json';path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    return result
