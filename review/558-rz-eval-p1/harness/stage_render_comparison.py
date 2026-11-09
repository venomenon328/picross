from pathlib import Path
import io,re,subprocess,zipfile,shutil
from PIL import Image
root=Path(__file__).resolve().parent
repo=root/'repo'
work=root/'render-comparison'
if work.exists(): raise RuntimeError('Render comparison already exists')
work.mkdir()
with zipfile.ZipFile(io.BytesIO(subprocess.check_output(['git','archive','--format=zip','HEAD','game'],cwd=repo))) as bundle:
    bundle.extractall(work)
assets=work/'game/art/drawing/rz_eval'
for source in (root/'comparison').iterdir():
    if source.suffix in ('.png','.webp'): shutil.copyfile(source,assets/source.name)
for name in ('basilisk','petronas'):
    image=Image.open(assets/f'{name}-1-2304.png').convert('RGBA')
    image.save(assets/f'{name}-1-2304.q85.webp',quality=85,method=6)
    image.convert('LA').save(assets/f'{name}-1-2304.la.png',optimize=True)
    image.save(assets/f'{name}-1-2304.nomips.png',optimize=True)
template=(repo/'game/art/drawing/rz_eval/qualle-1-2304.png.import').read_text()
for target in assets.iterdir():
    if target.suffix not in ('.png','.webp'): continue
    text=template.replace('qualle-1-2304.png',target.name)
    text=re.sub(r'^(path|dest_files|uid)=.*\n','',text,flags=re.M)
    if '.nomips.' in target.name: text=text.replace('mipmaps/generate=true','mipmaps/generate=false')
    (assets/(target.name+'.import')).write_text(text,encoding='utf-8',newline='\n')
print(work/'game')
