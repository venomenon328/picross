"""One-time measured source/import/full-player-export comparison; not CI."""
from pathlib import Path
import hashlib, io, json, os, re, shutil, statistics, subprocess, sys, time, zipfile
from PIL import Image

root=Path(__file__).resolve().parent
repo=root/'repo'
work=root/'measurements-owner-revision'
work.mkdir(exist_ok=True)
project=work/'game'
if not project.exists():
    raw=subprocess.check_output(['git','archive','--format=zip','HEAD','game'],cwd=repo)
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        archive.extractall(work)
env=os.environ.copy()
env.update(TEMP=str(root/'temp'),TMP=str(root/'temp'),APPDATA=str(work/'profile/roaming'),LOCALAPPDATA=str(work/'profile/local'))
engine=r'E:\Zeuch\Coding\Parkey-Tools\Godot-4.7.2\Godot_v4.7.2-stable_win64_console.exe'
archive=Path(r'E:\Zeuch\Coding\picross_codex\485-k-a\cache\Godot_v4.7.2-stable_export_templates.tpz')
expected='f298490b8d44d934be425a5a65a51bf15f422428b229a06a6e11d9ffea248011'
digest=hashlib.file_digest(archive.open('rb'),'sha256').hexdigest()
assert digest==expected
templates=Path(env['APPDATA'])/'Godot/export_templates/4.7.2.stable'
templates.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(archive) as bundle:
    for name in bundle.namelist():
        base=Path(name).name
        if base in ('version.txt','windows_debug_x86_64.exe','windows_debug_x86_64_console.exe') or (base.startswith('web_') and base.endswith('_debug.zip')):
            (templates/base).write_bytes(bundle.read(name))

def command(label,args,binary=engine):
    start=time.perf_counter()
    log=work/(label+'.log')
    with log.open('wb') as stream:
        result=subprocess.run([binary,*args],env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=300)
    text=log.read_text(encoding='utf-8',errors='replace')
    if result.returncode or any(x in text for x in ('ERROR:','SCRIPT ERROR:','SHADER ERROR:')):
        raise RuntimeError(label+' failed: '+text[-5000:])
    return (time.perf_counter()-start)*1000

names=('tomate','qualle','hills','petronas','basilisk')
choices={'tomate':1,'qualle':2,'hills':1,'petronas':3,'basilisk':3}
assets=project/'art/drawing/rz_eval'
for file in list(assets.iterdir()):
    if file.suffix in ('.png','.webp','.import'): file.unlink()
profiles=[('baseline',None,None,False),('png-reference-2304',2304,'reference',True),
          ('png-1536',1536,'png',True),('png-2304',2304,'png',True),('png-3072',3072,'png',True),
          ('webp-lossless-1536',1536,'webp',True),('webp-lossless-2304',2304,'webp',True),('webp-lossless-3072',3072,'webp',True),
          ('webp-q85-2304',2304,'lossy',True),('png-2304-no-mips',2304,'png',False),('png-LA-2304',2304,'LA',True)]
report=[]
for label,width,kind,mips in profiles:
    started=time.perf_counter()
    for file in list(assets.iterdir()):
        if file.suffix in ('.png','.webp','.import'): file.unlink()
    # Repeated same-path sources must not inherit an orphaned import remap or
    # stale settings. Remove ONLY these five owned illustration cache families.
    for name in names:
        for file in (project/'.godot/imported').glob(name+'-'+str(choices[name])+'-*'):
            file.unlink()
    image_rows=[]
    for name in names if width else ():
        source=root/'comparison'/f'{name}-{choices[name]}-{width}.png'
        image=Image.open(source).convert('RGBA')
        ext='webp' if kind in ('webp','lossy') else 'png'
        target=assets/f'{name}-{choices[name]}-{width}.{ext}'
        if kind in ('png','webp'): shutil.copyfile(root/'comparison'/target.name,target)
        elif kind=='reference': image.save(target,compress_level=6,optimize=False)
        elif kind=='lossy': image.save(target,quality=85,method=6,lossless=False)
        elif kind=='LA': image.convert('LA').save(target,optimize=True)
        # Explicit common import: same compression and alpha policy, only mips vary.
        config=repo/'game/art/drawing/rz_eval'/f'{name}-{choices[name]}-2304.png.import'
        original=config.read_text(encoding='utf-8')
        source_name=f'{name}-{choices[name]}-2304.png'
        text=original.replace(source_name,target.name)
        text=text.replace('mipmaps/generate=true','mipmaps/generate='+str(mips).lower())
        # Let Godot resolve the path-based destination hash; remove stale remap path.
        text=re.sub(r'^path=.*\n','',text,flags=re.M)
        text=re.sub(r'^dest_files=.*\n','',text,flags=re.M)
        text=re.sub(r'^uid=.*\n','',text,flags=re.M)
        (assets/(target.name+'.import')).write_text(text,encoding='utf-8',newline='\n')
        times=[]
        for _ in range(7):
            t=time.perf_counter()
            with Image.open(target) as decoded: decoded.convert('RGBA').load()
            times.append((time.perf_counter()-t)*1000)
        with Image.open(target) as decoded: rgba=decoded.convert('RGBA')
        image_rows.append(dict(name=name,candidate=choices[name],file=target.name,source_bytes=target.stat().st_size,
            decoded_rgba_bytes=width*(width//4)*4,decode_pillow_ms_median=statistics.median(times),
            pixel_equal_to_png=rgba.tobytes()==image.tobytes(),sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
    import_ms=command(label+'-import',['--headless','--path',str(project),'--editor','--import'])
    for row in image_rows:
        imported=list((project/'.godot/imported').glob(row['file']+'-*.ctex'))
        assert len(imported)==1,(row,imported)
        row['imported_bytes']=imported[0].stat().st_size
    destination=work/'exports'/label
    destination.mkdir(parents=True,exist_ok=True)
    win_ms=command(label+'-windows',['--headless','--path',str(project),'--export-debug','P1 Windows x86_64',str(destination/'picross-p1.exe')])
    web_ms=command(label+'-web',['--headless','--path',str(project),'--export-debug','P1 Web',str(destination/'index.html')])
    env['RZ_PACK_OUTPUT']=str(work/(label+'-pack.json'))
    env['RZ_PACK_WIDTH']=str(width or 0)
    env['RZ_PACK_MIPS']=str(mips).lower()
    env['RZ_PACK_PATHS']=json.dumps(['res://art/drawing/rz_eval/'+r['file'] for r in image_rows])
    command(label+'-pack-read',['--headless','--main-pack',str(destination/'picross-p1.pck'),'--script',str(root/'temp/pack_read.gd')])
    packed=json.loads(Path(env['RZ_PACK_OUTPUT']).read_text())
    assert packed['failures']==[],packed
    windows_bytes=(destination/'picross-p1.pck').stat().st_size
    web_bytes=(destination/'index.pck').stat().st_size
    windows_total=sum(p.stat().st_size for p in destination.iterdir() if p.name.startswith('picross-p1'))
    web_total=sum(p.stat().st_size for p in destination.iterdir() if not p.name.startswith('picross-p1'))
    row=dict(profile=label,size=[width,width//4] if width else None,mipmaps=mips,images=image_rows,packed_read=packed,
        import_ms=import_ms,windows_export_ms=win_ms,web_export_ms=web_ms,windows_pck_bytes=windows_bytes,
        web_pck_bytes=web_bytes,windows_total_bytes=windows_total,web_total_bytes=web_total,wall_ms=(time.perf_counter()-started)*1000)
    report.append(row)
    baseline=report[0]
    row['windows_pck_growth']=windows_bytes-baseline['windows_pck_bytes']
    row['web_pck_growth']=web_bytes-baseline['web_pck_bytes']
    (work/'profiles.json').write_text(json.dumps(dict(source_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip(),template_sha256=digest,profiles=report),indent=2)+'\n',encoding='utf-8',newline='\n')
    print(label,'source',sum(i['source_bytes'] for i in image_rows),'import',sum(i['imported_bytes'] for i in image_rows),'win growth',row['windows_pck_growth'],'web growth',row['web_pck_growth'],flush=True)
