from pathlib import Path
import os,sys,json,subprocess,hashlib,secrets,shutil
from contextlib import ExitStack
from uuid import uuid4
root=Path.cwd();task=root.parent
sys.path.insert(0,str(root/'server/save_sync'))
from test_integration import Project, Client, compact, mutation, abandon_body
BASE='2f817f696240d834033d7a36c40e08f1b0fd56af'
run=uuid4().hex[:10];work=task/('legacy-'+run);work.mkdir()
for name in subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'server/save_sync'],text=True).splitlines():
    dest=work/name;dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(subprocess.check_output(['git','show',BASE+':'+name]))
name='picross-sync-b2-legacy-'+run;p=Project(name,name+':local',secrets.token_urlsafe(32))
p.env['COMPOSE_FILE']=str(work/'server/save_sync/compose.yaml')
with ExitStack() as stack:
    stack.callback(lambda:subprocess.run(['docker','image','rm',name+':local'],capture_output=True))
    stack.callback(p.down);p.up('--build')
    client=Client(p,'history'+run); client.register()
    view=dict(center=[.5,.5],zoom=24,overview=False,active_color=1,tool='fill',row_clue_reads=[{'anchor':'grid_end'}],column_clue_reads=[{'anchor':'grid_end'}])
    save=dict(schema=1,definition_id='old',definition_revision=1,width=1,height=1,cells=[-1],history=[],cursor=0,undo_used=False,completed=False,view=view)
    path='/v1/puzzles/old/mutations'
    raw=compact(mutation(1,0,'snapshot',save=save))
    receipt=client.http('POST',path,raw)
    p.env['COMPOSE_FILE']=str(root/'server/save_sync/compose.yaml')
    p.up('--build','--force-recreate','api')
    client.http('POST',path,raw,422)
    cp=client.get('device/checkpoint')
    assert cp['response_body'].encode()==receipt.raw and cp['last_request_hash']==abandon_body(path,raw,1,'old')['request_hash']
    assert client.http('POST','/v1/device/abandon',abandon_body(path,raw,1,'old')).body==cp
    pending=compact(mutation(2,1,'snapshot',save=save));order=abandon_body(path,pending,2,'old')
    client.http('POST',path,pending,422)
    client.http('POST','/v1/device/abandon',order,drop=True)
    abandoned=client.http('POST','/v1/device/abandon',order).body
    assert abandoned==client.get('device/checkpoint') and json.loads(abandoned['response_body'])['code']=='request_abandoned'
    assert client.get('puzzles/old')['server_revision']==1
    proof=dict(old=BASE,head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),before=raw.decode(),after=pending.decode(),original_checkpoint=cp,abandoned_checkpoint=abandoned,server_revision=1)
    (work/'legacy-receipts.json').write_text(json.dumps(proof,indent=2))
    print('PASS legacy from actual pre-PROGRESS server through migrated HTTP/PostgreSQL',flush=True)
