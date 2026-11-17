"""Small current-result lifecycles. No history files or real puzzle fixtures."""
from copy import deepcopy
from pathlib import Path
import json
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tests.puzzle_production.current_fixtures import checkout, make, json_file
from tools.puzzle_production import current_authoring as current, current_content as content, catalog_io as io
from tools.puzzle_production import authoring_builder, catalog_integration, integration_input
from tools.production_workspace import presentation, projector
from tools.production_workspace.sources import LocalSource
from tools.puzzle_production.contract import InvalidInput


def git(root,*args):
    return subprocess.check_output(['git','-C',str(root),*args],stderr=subprocess.PIPE).decode().strip()


def commit(root,message):
    git(root,'add','content','game');git(root,'commit','-qm',message);return git(root,'rev-parse','HEAD')


def judgment(criteria):
    return {k:{'result':'erfüllt','accepted':False,'reason':'Synthetic checked criterion',
               'method':'Synthetic fixture inspection','actor':'Synthetic test','timestamp_utc':'2026-11-17T00:00:00Z'} for k in criteria}


def decide(job,scope):
    job['decisions']=[d for d in job['decisions'] if d['scope']!=scope]
    job['decisions'].append({'scope':scope,'binding':current.binding(job,scope),'actor':'Synthetic test',
                             'timestamp_utc':'2026-11-17T00:00:00Z','statement':'Synthetic actual '+scope+' decision'})


class CurrentAuthoringTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.work=Path(self.temp.name);self.root=checkout(self.work/'checkout')
        git(self.root,'init','-q','-b','main');git(self.root,'config','core.autocrlf','false');git(self.root,'config','user.email','test@example.invalid');git(self.root,'config','user.name','Synthetic test')
        self.base=commit(self.root,'base')
        self.input=make(self.work/'input')
        self.incoming=json.loads((self.input/'manifest.json').read_bytes())
        self.payload={};self.sources=self.work/'sources';self.sources.mkdir()
        self.job={'format':current.FORMAT,'puzzle_id':'pz-current','revision':'current','source_commit':self.base,
                  'operation':'production','target':None,'title':'Synthetic','category_id':'test','state':'brief_ready','brief':'Synthetic current brief',
                  'parameters':{'approved':[],'proposed':[]},'assets':[],'rasters':[],
                  'selected':dict.fromkeys(('reveal','motif','raster','background')),
                  'decisions':[],'budgets':{'limits':{'raster_candidates':6,'repair_rounds':2,'image_corrections':2},'used':{'raster_candidates':0,'repair_rounds':0,'image_corrections':0}},'blockers':[],'test_only':True,'integration':None}

    def file(self,name,raw):
        self.payload[name]=raw
        (self.sources/name).parent.mkdir(parents=True,exist_ok=True);(self.sources/name).write_bytes(raw)
        return content.ref('content/authoring/pz-current/data/'+name,raw)

    def asset(self,id,role,filename='reveal.png'):
        return {'id':id,'role':role,'label':id,'file':self.file(id+'.png',(self.input/filename).read_bytes()),
                'rights':self.incoming['reveal']['rights'],'review':judgment(current.CRITERIA[role])}

    def request(self):
        name=current.path(self.job['puzzle_id']);raw=io.read(self.root,name,current.LIMIT,missing=True)
        used={r['file'] for r in current.references(self.job)}
        files=[{'path':'content/authoring/pz-current/data/'+n,'source':n,'bytes':len(b),'sha256':io.checksum(b)}
               for n,b in self.payload.items() if 'content/authoring/pz-current/data/'+n in used]
        return {'format':current.REQUEST,'record':deepcopy(self.job),'expected':io.checksum(raw),'files':files}

    def publish(self):
        result=authoring_builder.build(self.request(),self.sources,self.work,self.root)
        self.job=json.loads((self.root/current.path('pz-current')).read_bytes())
        return result

    def raster_ready(self):
        self.job['assets']=[self.asset('reveal-a','reveal'),self.asset('reveal-b','reveal'),self.asset('reveal-c','reveal')]
        self.job['state']='reveal_review';self.publish()
        self.assertEqual(len(list((self.root/'content/authoring/pz-current/data').glob('*.png'))),3)
        self.job['selected']['reveal']='reveal-b';decide(self.job,'reveal')
        self.job['assets'].append(self.asset('motif-a','motif'));self.job['state']='motif_review';self.publish()
        self.assertFalse((self.root/'content/authoring/pz-current/data/reveal-a.png').exists())
        parameters={'width':3,'height':3,'mode':self.incoming['entry']['mode'],'foreground_colors':len(json.loads((self.input/'definition.json').read_bytes())['palette']),
                    'size_constraint':'exact','foreground_color_constraint':'exact'}
        self.job['parameters']={'proposed':[parameters],'approved':[parameters]}
        self.job['selected']['motif']='motif-a';decide(self.job,'motif');self.job['state']='raster_review';self.publish()
        raster={'id':'raster-a','label':'Qualified synthetic raster',
                **{k:self.file(k+'.json',(self.input/self.incoming[k]['file']).read_bytes()) for k in ('definition','proof','difficulty')},
                'preview':self.file('raster.png',current.raster_preview(json.loads((self.input/'definition.json').read_bytes()))),
                'review':judgment(current.CRITERIA['raster']),'exceptions':[]}
        self.job.update(state='raster_ready',rasters=[raster]);self.publish()

    def approved(self,background='none'):
        self.raster_ready();self.job['selected']['raster']='raster-a';decide(self.job,'raster')
        self.job['state']='background_review';self.publish()
        self.job['selected']['background']=background;decide(self.job,'background')
        self.job['state']='content_ready';self.publish()
        decide(self.job,'final');decide(self.job,'integration');self.job['state']='editorially_approved';self.publish()

    def test_five_phases_without_history_and_current_ri_input(self):
        self.publish();self.approved()
        files=[p.relative_to(self.root).as_posix() for p in (self.root/'content/authoring').rglob('*') if p.is_file()]
        self.assertEqual(len([n for n in files if n.endswith('record.json')]),1)
        self.assertFalse(any(any(s in n for s in ('package.zip','handoff','inventory','workspace.json','current-view','operation.json','rulebook')) for n in files))
        source=LocalSource(self.root);raw=(self.root/current.path('pz-current')).read_bytes()
        view=current.projection(self.job,raw);facts=presentation.inspect(source,None,view)
        self.assertEqual(facts['composition']['raster'],'raster-a')
        self.assertEqual(facts['state'],'editorially_approved')
        out=self.work/'integration';current.prepare(self.root,current.path('pz-current'),out)
        integration_input.Input(out)
        self.assertEqual(catalog_integration.integrate(out,self.root,apply=True)['status'],'registered')
        self.assertEqual(catalog_integration.integrate(out,self.root,apply=True)['status'],'no-op')

    def test_choice_survives_administrative_move_but_changed_bytes_fail(self):
        self.approved();old=self.job['assets'][0]['file'];new=deepcopy(self.job)
        changed=self.file('moved.png',(self.root/old['file']).read_bytes())
        new['assets'][0]['file']=changed;self.job=new;self.publish()
        self.assertFalse((self.root/old['file']).exists())
        self.job['assets'][0]['file']['sha256']='0'*64
        with self.assertRaisesRegex(InvalidInput,'Stale decision'):self.publish()

    def test_missing_swapped_unauthorized_and_invalid_proof_fail(self):
        self.raster_ready()
        original=deepcopy(self.job)
        decide(self.job,'raster')
        self.job['rasters'][0]['definition']['sha256']='0'*64
        with self.assertRaisesRegex(InvalidInput,'Stale decision'):self.publish()
        self.job=deepcopy(original)
        self.job['selected']['raster']='raster-a';self.job['state']='background_review'
        with self.assertRaisesRegex(InvalidInput,'choice'):self.publish()
        self.job=deepcopy(original);self.job['rasters'][0]['proof']['file']=self.job['rasters'][0]['definition']['file']
        with self.assertRaises(InvalidInput):self.publish()
        self.job=deepcopy(original);proof=json.loads((self.input/'proof.json').read_bytes());proof['final_domains'][0][0]=['c1']
        self.job['rasters'][0]['proof']=self.file('bad-proof.json',current.encoded(proof))
        with self.assertRaises((InvalidInput,ValueError)):self.publish()
        self.job=deepcopy(original);(self.root/self.job['assets'][0]['file']['file']).unlink()
        self.payload.pop('reveal-b.png')
        with self.assertRaises(InvalidInput):self.publish()

    def test_safe_publication_conflict_recovery_and_idempotence(self):
        self.job['assets']=[self.asset('reveal-a','reveal')];self.job['state']='reveal_review';request=self.request()
        for boundary in ('journal','files','record','index','pruned'):
            with self.subTest(boundary=boundary):
                def crash(name):
                    if name==boundary:raise RuntimeError('synthetic interruption')
                with patch.object(current,'checkpoint',side_effect=crash):
                    with self.assertRaises(RuntimeError):current.build(request,self.sources,self.root)
                current.build(request,self.sources,self.root)
                self.assertFalse((self.root/'content/authoring/pz-current/.current-operation.json').exists())
                # Create a new actual current metadata change for the next boundary.
                self.job=json.loads((self.root/current.path('pz-current')).read_bytes());self.job['brief']+=' next'
                request=self.request()
        current.build(request,self.sources,self.root)
        before={p:(p.read_bytes(),p.stat().st_mtime_ns) for p in (self.root/'content/authoring').rglob('*') if p.is_file()}
        self.assertEqual(current.build(request,self.sources,self.root)['status'],'reused')
        self.assertEqual(before,{p:(p.read_bytes(),p.stat().st_mtime_ns) for p in before})
        for malformed in ('not-a-list',[{}]):
            bad=deepcopy(request);bad['files']=malformed
            with self.assertRaises(InvalidInput):current.build(bad,self.sources,self.root)
        bad=deepcopy(request);bad['record']['brief']='foreign';bad['expected']='0'*64
        with self.assertRaisesRegex(InvalidInput,'conflict'):current.build(bad,self.sources,self.root)
        bad=deepcopy(request);bad['record']['assets'][0]['file']['file']='../escape.png'
        with self.assertRaises(InvalidInput):current.build(bad,self.sources,self.root)

    def test_completion_and_retirement_without_work_in_integration_commit(self):
        self.approved();work_commit=commit(self.root,'current work')
        current.prepare(self.root,current.path('pz-current'),self.work/'integration')
        # Product branch starts at clean main; only final product data is integrated.
        git(self.root,'checkout','-qb','product',self.base)
        catalog_integration.integrate(self.work/'integration',self.root,apply=True)
        product=commit(self.root,'selected product only')
        self.assertFalse(git(self.root,'ls-tree','-r','--name-only',product,'--','content/authoring/pz-current'))
        git(self.root,'update-ref','refs/remotes/origin/main',product)
        # Completion runs on the work branch after product-only data is made available.
        git(self.root,'checkout','-qb','work',work_commit)
        self.assertEqual(json.loads((self.root/'content/registry.json').read_bytes())['entries'],[])
        result=projector.complete(self.root,current.path('pz-current'),product,current_input=self.work/'integration')
        self.assertEqual(result['status'],'built');commit(self.root,'completed work')
        self.assertEqual(current.retire(self.root,['pz-current'],product)['status'],'retired')
        self.assertEqual(current.retire(self.root,['pz-current'],product)['status'],'no-op')
        self.assertEqual(json.loads((self.root/'content/authoring/index.json').read_bytes())['entries'],[])

    def test_color_standard_and_accepted_editorial_result(self):
        self.input=make(self.work/'color-input',mode='color',colors=2)
        self.incoming=json.loads((self.input/'manifest.json').read_bytes())
        self.approved('standard')
        self.job['rasters'][0]['review']['Q-H01'].update(result='nicht erfüllt',accepted=True,reason='Explicit synthetic editorial exception')
        decide(self.job,'final');decide(self.job,'integration')
        for d in self.job['decisions']:
            if d['scope']=='final':d['statement']+='; accept Q-H01 explicitly'
        self.publish();current.prepare(self.root,current.path('pz-current'),self.work/'accepted-input')
        value=integration_input.Input(self.work/'accepted-input')
        self.assertEqual(value.value['background']['status'],'standard')
        review=json.loads((self.work/'accepted-input/review.json').read_bytes())
        self.assertEqual(review['criteria']['Q-H01']['result'],'failed')
        self.assertTrue(review['criteria']['Q-H01']['accepted'])

    def test_current_helpers_publish_only_result_files(self):
        from tools.puzzle_production import current_tools
        definition=json.loads((self.input/'definition.json').read_bytes())
        out=self.work/'current-raster'
        result=current_tools.raster(definition,out,mode='mono')
        self.assertTrue(result['certified'])
        self.assertEqual({p.name for p in out.iterdir()},{'definition.json','proof.json','difficulty.json','preview.png'})
        self.assertEqual(result['files']['proof'],content.ref('proof.json',(out/'proof.json').read_bytes()))

    def test_background_only_uses_active_references_and_shared_editor(self):
        from io import BytesIO
        from PIL import Image, PngImagePlugin
        from tools.puzzle_production import editor_cli, editor_change
        capability=Path(__file__).resolve().parents[2]/'game/data/background-capability.json'
        (self.root/'game/data/background-capability.json').write_bytes(capability.read_bytes())
        catalog_integration.integrate(self.input,self.root,apply=True);commit(self.root,'active product')
        entry=self.incoming['entry']
        self.job.update(operation='background',target={'definition':content.ref('game/'+entry['definition'],(self.root/('game/'+entry['definition'])).read_bytes()),
            'reveal':content.ref('game/'+entry['reveal'],(self.root/('game/'+entry['reveal'])).read_bytes()),'mode':'mono'},state='background_review')
        self.job['assets']=[{'id':'active-reveal','role':'reveal','label':'Active reveal','file':self.job['target']['reveal'],'rights':None,'review':{}}]
        self.job['selected']['reveal']='active-reveal'
        stream=BytesIO();info=PngImagePlugin.PngInfo();info.add(b'sRGB',b'\0')
        image=Image.new('RGBA',(2304,768),(0,0,0,0));image.putpixel((20,500),(50,50,50,100));image.save(stream,format='PNG',pnginfo=info)
        self.job['assets'].append({'id':'context-a','role':'background','label':'Synthetic background','file':self.file('context.png',stream.getvalue()),
                                   'rights':self.incoming['reveal']['rights'],'review':judgment(current.CRITERIA['background'])})
        self.publish()
        source=LocalSource(self.root);raw=(self.root/current.path('pz-current')).read_bytes();view=current.projection(self.job,raw)
        facts=presentation.inspect(source,None,presentation.validate(view))
        self.assertEqual(facts['composition']['raster'],'active-raster')
        preview=presentation.asset_bytes(source,None,next(a['location'] for a in view['assets'] if a['id']=='active-raster'))
        self.assertTrue(preview.startswith(b'\x89PNG'))
        self.job['selected']['background']='context-a';decide(self.job,'background');decide(self.job,'final');decide(self.job,'integration')
        self.job['state']='editorially_approved';self.publish()
        current.prepare(self.root,current.path('pz-current'),self.work/'bg-change')
        self.assertEqual({p.name for p in (self.work/'bg-change').iterdir()},{'request.json','background.png'})
        plan_path=self.work/'bg-plan.json';editor_cli.plan_file(self.root,self.work/'bg-change/request.json',plan_path)
        self.assertEqual(editor_change.apply(self.root,json.loads(plan_path.read_bytes()))['status'],'updated')
        self.assertIn(self.incoming['reveal']['rights']['usage_basis'],(self.root/'game/art/backgrounds/pz-current.txt').read_text(encoding='utf8'))
        product=commit(self.root,'changed selected background')
        notice=self.root/'game/art/backgrounds/pz-current.txt';actual_notice=notice.read_bytes()
        notice.write_bytes(b'Different rights.\n');wrong=commit(self.root,'wrong current notice')
        with self.assertRaisesRegex(InvalidInput,'rights differ'):
            projector.complete(self.root,current.path('pz-current'),wrong,current_input=self.work/'bg-change')
        notice.write_bytes(actual_notice);product=commit(self.root,'actual background rights')
        projector.complete(self.root,current.path('pz-current'),product,current_input=self.work/'bg-change')

    def test_budget_reset_and_midpublication_foreign_edit_are_rejected(self):
        self.job['budgets']['used']['raster_candidates']=2;self.publish()
        self.job['budgets']['used']['raster_candidates']=1
        with self.assertRaisesRegex(InvalidInput,'reset'):self.publish()
        self.job['budgets']['used']['raster_candidates']=2
        self.job['assets']=[self.asset('reveal-a','reveal')];self.job['state']='reveal_review';request=self.request()
        def mutate(boundary):
            if boundary=='record':(self.root/self.job['assets'][0]['file']['file']).write_bytes(b'foreign bytes')
        with patch.object(current,'checkpoint',side_effect=mutate):
            with self.assertRaisesRegex(InvalidInput,'Published current input changed'):current.build(request,self.sources,self.root)
        self.assertTrue((self.root/'content/authoring/pz-current/.current-operation.json').exists())
        with self.assertRaises(InvalidInput):current.build(request,self.sources,self.root)
        self.assertEqual((self.root/self.job['assets'][0]['file']['file']).read_bytes(),b'foreign bytes')


    def test_service_derives_views_and_current_bound_followup_without_archive(self):
        from tools.production_workspace.repository import Repository, configure
        from tools.production_workspace.server import Service
        self.raster_ready();commit(self.root,'current offer')
        state=self.work/'state';configure(self.root,state,refs=['main'])
        service=Service(Repository(state));listing=service.listing()
        self.assertEqual(listing['errors'],[])
        self.assertEqual(len(listing['jobs']),1)
        view=service.detail(listing['jobs'][0]['id'])
        self.assertEqual(view['record']['file'],current.path('pz-current'))
        self.assertEqual(view['offers'][0]['id'],'raster-a')
        self.assertEqual(view['facts']['published']['brief']['text'],self.job['brief'])
        self.assertEqual(view['facts']['published']['role'],'approved')
        self.assertIn(view['facts']['metadata']['difficulty']['level'],['L1','L2','L3','L4','L5'])
        self.assertTrue(service.picture(listing['jobs'][0]['id'],'raster-a')[0].startswith(b'\x89PNG'))
        view['source_url']='https://github.com/venomenon328/picross/tree/'+view['commit']
        module=str(Path(__file__).resolve().parents[2]/'tools/production_workspace/ui/workflow.js')
        script="const assert=require('node:assert/strict'),P=require(process.argv[1]),v=JSON.parse(process.argv[2]);const p=P.prompt(v,{kind:'raster',selection:'raster-a'},{merge:false});assert.ok(p.includes(v.record.file));assert.match(p,/einem aktuellen Metadatensatz/);assert.doesNotMatch(p,/Arbeitsbelege mitführen/);assert.throws(()=>P.prompt(v,{kind:'raster',selection:'wrong'},{}),/wählen/);"
        result=subprocess.run(['node','-e',script,module,json.dumps(view)],capture_output=True,text=True,encoding='utf8')
        self.assertEqual(result.returncode,0,result.stderr)
        (self.root/self.job['rasters'][0]['preview']['file']).write_bytes(b'stale')
        with self.assertRaises(InvalidInput):presentation.inspect(LocalSource(self.root),None,current.projection(self.job,(self.root/current.path('pz-current')).read_bytes()))

    def test_image_helper_keeps_current_outputs_and_background_png_only(self):
        from io import BytesIO
        from PIL import Image
        from tools.puzzle_production import current_tools
        source=self.work/'pixels.png';stream=BytesIO();Image.new('RGBA',(4,4),(41,62,61,255)).save(stream,format='PNG');source.write_bytes(stream.getvalue())
        design=json.loads((Path(__file__).parent/'fixtures/image-design.json').read_bytes());design['variants']=design['variants'][:1]
        design_path=self.work/'design.json';design_path.write_bytes(current.encoded(design))
        out=self.work/'image-result';result=current_tools.image(source,design_path,out,puzzle_id='pz-current',name='Synthetic')
        self.assertEqual(len(result['candidates']),1)
        self.assertEqual({p.name for p in (out/design['variants'][0]['id']).iterdir()},{'definition.json','proof.json','difficulty.json','preview.png'})
        bg_source=self.work/'bg-source.png';pixels=Image.new('RGBA',(12,4),(41,62,61,128));pixels.putpixel((0,0),(0,0,0,0));pixels.save(bg_source,format='PNG')
        bg=self.work/'prepared.png';current.prepare_background(bg_source,bg)
        with Image.open(bg) as prepared:self.assertEqual(prepared.size,(2304,768))
        self.assertFalse(any(p.name.startswith('.current-') for p in self.work.iterdir()))


    def test_background_reader_references_active_svg_after_editor_image_switch(self):
        from tools.puzzle_production import editor_change, editor_image_input
        from tools.production_workspace.repository import Repository, configure
        from tools.production_workspace.server import Service
        catalog_integration.integrate(self.input,self.root,apply=True)
        svg=b'<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12"><path d="M1 1H11V11H1Z" fill="#202020"/></svg>'
        request={'id':'pz-current','metadata':None,'text':None,'profile':None,'reveal':{'upload':'new'},'background':None}
        plan=editor_change.plan(self.root,request,uploads={'new':{'raw':svg,'suffix':'svg','checked':editor_image_input.validate_reveal(svg,'.svg')}})
        editor_change.apply(self.root,plan)
        entry=self.incoming['entry'];runtime=json.loads((self.root/content.RUNTIME).read_bytes())['entries'][0]
        self.assertNotEqual(runtime['reveal'],entry['reveal'])
        target={'definition':content.ref('game/'+entry['definition'],(self.root/('game/'+entry['definition'])).read_bytes()),
                'reveal':content.ref('game/'+runtime['reveal'],svg),'mode':'mono'}
        self.job.update(operation='background',target=target,state='background_review')
        self.job['assets']=[{'id':'active-reveal','role':'reveal','label':'Active SVG','file':target['reveal'],'rights':None,'review':{}}]
        self.job['selected']['reveal']='active-reveal';self.publish();commit(self.root,'current active SVG work')
        configure(self.root,self.work/'svg-state',refs=['main']);service=Service(Repository(self.work/'svg-state'))
        listing=service.listing();self.assertEqual(listing['errors'],[])
        jid=listing['jobs'][0]['id'];self.assertEqual(service.detail(jid)['facts']['composition']['reveal'],'active-reveal')
        self.assertEqual(service.picture(jid,'active-reveal'),(svg,'image/svg+xml'))
        self.job['target']['reveal']['file']='game/'+entry['reveal']
        with self.assertRaises(InvalidInput):self.publish()


if __name__=='__main__':unittest.main()
