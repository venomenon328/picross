from pathlib import Path
import os,json,hashlib,shutil,platform
root=Path.cwd()
probe=os.environ['PROBE']
allowed=['status-ui100.png','status-ui125.png','http.json','journal.json','account-save.json','platform.json','legacy-receipts.json','barriers.json']
prefix='legacy-' if probe=='legacy' else ('proof-win-' if probe=='windows' else 'proof-'+probe+'-')
folders=[p for p in root.glob(prefix+'*') if p.is_dir()]
dst=root/'selected'
dst.mkdir()
rows=[]
if len(folders)==1:
    for name in allowed:
        p=folders[0]/name
        if p.is_file():
            b=p.read_bytes()
            shutil.copyfile(p,dst/name)
            rows.append({'name':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
(dst/'manifest.json').write_text(json.dumps({'product':os.environ['PRODUCT'],'diagnostic':os.environ['GITHUB_SHA'],'os':platform.platform(),'probe':probe,'files':rows},indent=2),encoding='utf8')
