from pathlib import Path
import hashlib,json,os,subprocess
root=Path(__file__).resolve().parent
work=root/'measurements-final-revision'
report=json.loads((work/'profiles.json').read_text())
bindings=[]
env=os.environ.copy()
env.update(APPDATA=str(root/'temp/extract-profile/roaming'),LOCALAPPDATA=str(root/'temp/extract-profile/local'))
engine=r'E:\Zeuch\Coding\Parkey-Tools\Godot-4.7.2\Godot_v4.7.2-stable_win64_console.exe'
for row in report['profiles']:
    label=row['profile']
    win=work/'exports'/label/'picross-p1.pck'
    web=work/'exports'/label/'index.pck'
    win_hash=hashlib.file_digest(win.open('rb'),'sha256').hexdigest()
    web_hash=hashlib.file_digest(web.open('rb'),'sha256').hexdigest()
    assert win_hash==web_hash
    destination=root/'import-originals'/label
    env['RZ_PACK_PATHS']=json.dumps(['res://art/drawing/rz_eval/'+i['file'] for i in row['images']])
    env['RZ_PACK_EXTRACT']=str(destination)
    result=subprocess.run([engine,'--headless','--main-pack',str(win),'--script',str(root/'temp/extract_imports.gd')],env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30,text=True)
    assert result.returncode==0 and 'ERROR:' not in result.stdout,result.stdout
    items=json.loads((destination/'mapping.json').read_text())
    for item,original in zip(items,row['images']):
        file=destination/item['file']
        assert file.stat().st_size==item['bytes']==original['imported_bytes']
        item['sha256']=hashlib.sha256(file.read_bytes()).hexdigest()
    bindings.append(dict(profile=label,windows_web_identical=True,pck_bytes=win.stat().st_size,pck_sha256=win_hash,imports=items))
(work/'export-bindings.json').write_text(json.dumps(dict(source_head=report['source_head'],profiles=bindings),indent=2)+'\n',encoding='utf-8',newline='\n')
print('Verified identical Windows/Web PCK bytes and extracted',sum(len(r['imports']) for r in bindings),'original packed textures.')
