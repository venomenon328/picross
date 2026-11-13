"""PW-B prompt regressions replacing superseded offline-session tests."""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AuthoringPromptTests(unittest.TestCase):
    def test_actual_generator_for_all_five_steps_correction_resume_and_source_guards(self):
        probe = r"""
const assert=require('node:assert/strict');
const P=require('./tools/production_workspace/ui/workflow.js');
const opts={workroot:'E:/synthetic',cleanup:true,merge:false};
const record={file:'content/authoring/pz-test/r01/record.json',sha256:'a'.repeat(64)};
const v={puzzle_id:'pz-test',revision:'r01',commit:'b'.repeat(40),source_url:'https://github.com/venomenon328/picross/tree/'+'b'.repeat(40),
 record,facts:{state:'reveal_review',authoring_version:'0.8.0',composition:{raster:'r',reveal:'v'},background_choice:'none'},
 assets:[{id:'r',role:'raster'},{id:'v',role:'reveal'},{id:'bg',role:'background',location:{sha256:'c'.repeat(64)}}],offers:[]};
let text=P.prompt(null,{brief:'Synthetischer Test, keine Produktion'},opts);
assert.match(text,/Schritt 1/);assert.doesNotMatch(text,/source_commit|localhost|Hintergrund|Kontextzeichnungen/);
assert.match(text,/Lokale Codex-Arbeitswurzel: E:\/synthetic/);
assert.doesNotMatch(text,/Abschlussbereinigung|ausschließlich innerhalb dieser Arbeitswurzel/);
assert.doesNotMatch(text,/Abschlussbereinigung eigener Arbeitsdaten nach WORKSPACE ausdrücklich beauftragt/);
assert.equal(text,P.prompt(null,{brief:'Synthetischer Test, keine Produktion'},{...opts,cleanup:false}));
assert.throws(()=>P.prompt(null,{},opts),/Motiv/);
for(const [state,n,kind] of [['reveal_review',2,'reveal'],['motif_review',3,null],['motif_approved',3,null],
 ['raster_review',3,null],['raster_ready',4,'raster'],['background_review',5,'background'],['content_ready',5,null],['editorially_approved',5,null]]){
 v.facts.state=state;v.offers=kind?[{id:'A',kind,record,asset_ids:['bg']}]:[];
 const intent={selection:kind?'A':null,kind,parameters:'etwa 25 × 20',context:'Landschaft'};
 text=P.prompt(v,intent,opts);assert.match(text,new RegExp('Schritt '+n));
 assert.match(text,/kein Merge/);assert.ok(text.includes(record.file));assert.ok(text.includes('b'.repeat(40)));
 if(n<4)assert.doesNotMatch(text,/Kontextwunsch|Kontextzeichnungen|Hintergrundkandidaten/);
 if(kind)assert.throws(()=>P.prompt(v,{},opts),/wählen/);
 for(const action of ['resume','rework'])assert.ok(P.prompt(v,{action,feedback:'Linie korrigieren'},opts).includes(record.file));
}
v.facts.state='background_review';assert.match(P.prompt(v,{selection:'none'},opts),/ausdrücklich für keinen Hintergrund/);
v.facts.state='content_ready';assert.match(P.prompt(v,{}, {...opts,merge:true}),/Squash-Merge nur bei erfüllten aktuellen Vor-Merge-Gates/);
for(const url of [null,'http://localhost:1234/job','https://github.com/venomenon328/picross/tree/main']){
 v.source_url=url;assert.throws(()=>P.prompt(v,{},opts),/Remote-Sicherung/);
}
v.source_url='https://github.com/venomenon328/picross/tree/'+'b'.repeat(40);v.facts.state='registered';
assert.doesNotMatch(P.prompt(v,{},opts),/Ich erteile/);
assert.match(P.prompt(v,{action:'background_change',feedback:'Mehr Wald'},opts),/HP-I1b2/);
v.source_url='https://github.com/venomenon328/picross/tree/'+'b'.repeat(40);v.facts.authoring_version='0.7.0';
assert.throws(()=>P.prompt(v,{},opts),/historische/);
"""
        result=subprocess.run(['node','-e',probe],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(result.returncode,0,result.stderr)

    def test_motif_notes_and_independent_raster_constraints(self):
        probe = r"""
const assert = require('node:assert/strict');
const P = require('./tools/production_workspace/ui/workflow.js');
const base = {brief: 'Erdbeere', notes: 'Kelch erhalten.\nDreiviertelansicht.'};
const grid = {width:'28', height:'19', sizeAccuracy:'exact', mode:'color', colors:'4', colorAccuracy:'approx'};
const build = settings => P.prompt(null,{...base,grid:settings},{});
const first = build(grid);
assert.ok(first.includes(base.notes));
assert.match(first,/Breite: exakt 28 Zellen.*Höhe: exakt 19 Zellen/s);
assert.match(first,/ungefähr 4 Vordergrundfarben/);
assert.match(first,/detaillierte farbige Abschlussbildoriginale/);
assert.match(build({...grid,sizeAccuracy:'approx',colorAccuracy:'exact'}),/Breite: ungefähr 28 Zellen.*Höhe: ungefähr 19 Zellen.*exakt 4/s);
assert.match(build({mode:'mono'}),/monochrom, genau eine Vordergrundfarbe/);
assert.doesNotMatch(build({...grid,mode:'mono'}),/4 Vordergrundfarben/);
assert.doesNotMatch(build({mode:'color'}),/Farbzahl:/);
assert.doesNotMatch(build({}),/Rastergröße:|Rastermodus:|Farbzahl:/);
for(const bad of [{...grid,width:'0'},{...grid,height:'51'},
                  {...grid,height:'1.5'},{...grid,width:'x'},{...grid,colors:'9'},{...grid,colors:'1'}]){
 assert.throws(()=>build(bad),/Bitte/);
}
assert.match(build({...grid,width:'1',height:'50',colors:'8'}),/Breite: exakt 1 Zellen.*Höhe: exakt 50 Zellen/s);
const record={file:'content/authoring/pz-test/r01/record.json',sha256:'a'.repeat(64)};
const value={commit:'b'.repeat(40),source_url:'https://github.com/venomenon328/picross/tree/'+'b'.repeat(40),
 record,puzzle_id:'pz-test',revision:'r01',facts:{state:'reveal_review',authoring_version:'0.8.0'},
 offers:[{id:'A',kind:'reveal',record}]};
const intent={grid,kind:'reveal',selection:'A'};
assert.equal(P.orderStep(value),2);
assert.match(P.prompt(value,intent,{}),/Schritt 2.*Breite: exakt 28 Zellen/s);
value.facts.state='motif_review';
assert.doesNotMatch(P.prompt(value,intent,{}),/Breite: exakt 28 Zellen/);
const correction=P.prompt(value,{...intent,action:'rework',feedback:'Raster anpassen'},{});
assert.match(correction,/Breite: exakt 28 Zellen/);
assert.doesNotMatch(correction,/Ich gebe.*frei/);
"""
        result = subprocess.run(['node', '-e', probe], cwd=ROOT, capture_output=True,
                                text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_published_context_changes_removal_and_approval_boundaries(self):
        probe = r"""
const assert=require('node:assert/strict'),P=require('./tools/production_workspace/ui/workflow.js');
const p={width:18,height:18,mode:'color',foreground_colors:3,size_constraint:'approximate',foreground_color_constraint:'exact',status:'approved'};
const published={proposed:[p],approved:[],role:'proposed',brief:{file:'brief.md',sha256:'c'.repeat(64)}};
const record={file:'content/authoring/pz-test/r01/record.json',sha256:'a'.repeat(64)};
const v={commit:'b'.repeat(40),source_url:'https://github.com/venomenon328/picross/tree/'+'b'.repeat(40),record,
 puzzle_id:'pz-test',revision:'r01',facts:{state:'reveal_review',authoring_version:'0.8.0',published},offers:[{id:'A',kind:'reveal',record}]};
const selected={kind:'reveal',selection:'A'};
const base=P.publishedGrid(v);
assert.deepEqual(base,{width:'18',height:'18',sizeAccuracy:'approx',mode:'color',colors:'3',colorAccuracy:'exact'});
for(const intent of [selected,{...selected,grid:base}]){
 const text=P.prompt(v,intent,{});
 assert.ok(text.includes(record.file));assert.doesNotMatch(text,/Auftrag an|SHA-256|workspace.json|brief.md|foreground_colors/);assert.doesNotMatch(text,/Neue Absicht|Vorgaben für das spätere Lösungsraster/);
 assert.match(text,/Schritt 2: Ich wähle/);assert.doesNotMatch(text,/Ich gebe.*Parameterkorridor frei/);
}
let text=P.prompt(v,{...selected,grid:{width:'20'},parameters:'Kelch erhalten\nMehr Platz'},{});
assert.match(text,/Neue Absicht.*Breite: ungefähr 20 Zellen/);assert.match(text,/Neue\/zusätzliche Wünsche.*Kelch erhalten\nMehr Platz/);
assert.throws(()=>P.prompt(v,{...selected,grid:{mode:''}},{}),/ausdrücklich aufheben/);
assert.throws(()=>P.prompt(v,{...selected,grid:{width:'',height:''}},{}),/ausdrücklich aufheben/);
assert.throws(()=>P.prompt(v,{...selected,grid:{colors:''}},{}),/ausdrücklich aufheben/);
text=P.prompt(v,{...selected,removeGrid:{width:true,height:true,mode:true,colors:true}},{});
assert.match(text,/Breite: bisherigen Wunsch ausdrücklich aufheben/);assert.match(text,/Farbzahl: bisherigen Wunsch ausdrücklich aufheben/);
published.approved=[{...p,width:22}];
assert.equal(P.publishedGrid(v).width,'22');
text=P.prompt(v,{...selected,grid:{width:'25'}},{});assert.match(text,/Korrekturweg.*erneuten Entscheidung/);
v.facts.state='motif_review';
assert.match(P.prompt(v,{},{}),/Schritt 3: Ich gebe.*Parameterkorridor.*frei/);
text=P.prompt(v,{action:'rework',feedback:'Anpassen',grid:{width:'25'}},{});
assert.match(text,/Neue Absicht/);assert.doesNotMatch(text,/Ich gebe.*frei/);
published.approved=[];published.proposed=[p,{width:30}];assert.deepEqual(P.publishedGrid(v),{});
published.proposed=[{...p,width:[15,20]}];assert.equal(P.publishedGrid(v).width,undefined);
published.proposed=[{...p,free_corridor:'around 18'}];assert.deepEqual(P.publishedGrid(v),{});
published.proposed={free:'fully preserved'};assert.deepEqual(P.publishedGrid(v),{});
published.proposed=null;assert.deepEqual(P.publishedGrid(v),{});
"""
        result = subprocess.run(['node', '-e', probe], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_partial_axes_differential_intent_and_canonical_source(self):
        probe = r"""
const assert=require('node:assert/strict'),P=require('./tools/production_workspace/ui/workflow.js');
const build=grid=>P.prompt(null,{brief:'Testmotiv',grid},{});
for(const sizeAccuracy of ['approx','exact'])for(const axes of [{},{width:'28'},{height:'30'},{width:'28',height:'19'}]){
 const text=build({...axes,sizeAccuracy}),precision=sizeAccuracy==='exact'?'exakt':'ungefähr';
 for(const [axis,label] of [['width','Breite'],['height','Höhe']]){
  if(axes[axis])assert.ok(text.includes(`${label}: ${precision} ${axes[axis]} Zellen`));
  else assert.doesNotMatch(text,new RegExp(label+':|'+label+' passend'));
 }
 assert.match(text,/Neues Motiv: Testmotiv/);assert.match(text,/AGENTS.md/);assert.match(text,/reveal_review/);
}
for(const axis of ['width','height'])for(const value of ['0','-1','51','1.5','x',' ','NaN'])assert.throws(()=>build({[axis]:value}),/Bitte/);
for(const colors of ['0','1','9','x','2.5'])assert.throws(()=>build({mode:'color',colors}),/Bitte/);
for(const colorAccuracy of ['approx','exact'])for(const colors of ['2','8']){
 assert.ok(build({mode:'color',colors,colorAccuracy}).includes(`${colors} Vordergrundfarben`));
}
assert.throws(()=>build({height:'30',sizeAccuracy:'unknown'}),/Genauigkeit/);
const p={width:18,height:30,size_constraint:'exact',mode:'color',foreground_colors:3,foreground_color_constraint:'exact'};
const published={proposed:[p],approved:[],role:'proposed',brief:{text:'ORIGINAL_BRIEF_NOT_TO_COPY'}};
const record={file:'content/authoring/pz-test/r01/record.json',sha256:'a'.repeat(64)};
const v={puzzle_id:'pz-test',revision:'r01',commit:'b'.repeat(40),
 source_url:'https://github.com/venomenon328/picross/tree/'+'b'.repeat(40),record,
 facts:{state:'reveal_review',authoring_version:'0.8.0',published},offers:[{id:'A',kind:'reveal',record}]};
const selected={kind:'reveal',selection:'A'},base=P.publishedGrid(v);
for(const intent of [selected,{...selected,grid:base}]){
 const text=P.prompt(v,intent,{});
 assert.doesNotMatch(text,/Neue Absicht|18|30|ORIGINAL_BRIEF|foreground_colors|brief.md|SHA-256|workspace.json|Auftrag an/);
 assert.equal(text.split(record.file).length,2,'one canonical entry');
 assert.ok(text.includes('/blob/'+v.commit+'/'+record.file));
}
for(const [axis,label,other] of [['width','Breite','Höhe'],['height','Höhe','Breite']]){
 const text=P.prompt(v,{...selected,removeGrid:{[axis]:true}},{});
 assert.ok(text.includes(`${label}: bisherigen Wunsch ausdrücklich aufheben`));
 assert.doesNotMatch(text,new RegExp(other+':|'+other+' passend'));
 assert.match(text,/Andere Vorgaben bleiben bestehen/);
 assert.deepEqual(P.publishedGrid(v),base,'removal never mutates source');
 assert.throws(()=>P.prompt(v,{...selected,grid:{[axis]:''}},{}),/ausdrücklich aufheben/);
}
let text=P.prompt(v,{...selected,removeGrid:{width:true},grid:{width:'bad',height:'32'}},{});
assert.match(text,/Breite: bisherigen Wunsch ausdrücklich aufheben.*Höhe: exakt 32/);
text=P.prompt(v,{...selected,grid:{width:'20'}},{});assert.doesNotMatch(text,/Höhe:|30 Zellen/);
text=P.prompt(v,{...selected,grid:{mode:'mono'}},{});assert.doesNotMatch(text,/Breite|Höhe|Farbzahl:/);
text=P.prompt(v,{...selected,grid:{colors:'4'}},{});assert.match(text,/Farbzahl: exakt 4/);assert.doesNotMatch(text,/Rastermodus:/);
for(const [source,expected] of [[{height:30,size_constraint:'exact'},{height:'30',sizeAccuracy:'exact'}],
 [{width:28,size_constraint:'approximate'},{width:'28',sizeAccuracy:'approx'}]]){
 published.proposed=[source];assert.deepEqual(P.publishedGrid(v),expected);
 assert.doesNotMatch(P.prompt(v,selected,{}),/Neue Absicht/);
}
published.proposed=[{...p,width:[15,20]}];assert.equal(P.publishedGrid(v).height,'30');assert.equal(P.publishedGrid(v).width,undefined);
for(const commit of [undefined,'c'.repeat(40)])assert.throws(()=>P.prompt({...v,commit},selected,{}),/Remote-Sicherung/);
for(const file of ['record.json','content/authoring/pz-other/r01/record.json','../record.json']){
 assert.throws(()=>P.prompt({...v,record:{file}},selected,{}),/kanonische/);
}
assert.throws(()=>P.prompt(v,{action:'unknown'},{}),/gültige Aktion/);
v.facts.composition={raster:'r',reveal:'v'};v.facts.background_choice='none';v.assets=[{id:'r',role:'raster'},{id:'v',role:'reveal'}];
for(const state of ['motif_approved','raster_review','editorially_approved','registered']){
 v.facts.state=state;assert.doesNotMatch(P.prompt(v,{},{}),/Ich gebe|Ich erteile|Ich wähle/);
}
v.revision='proposal.v2';v.record={file:'content/authoring/pz-test/proposal.v2/record.json'};
assert.ok(P.prompt(v,{},{}).includes(v.record.file));
"""
        result = subprocess.run(['node', '-e', probe], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_final_order_exact_objects_personal_defaults_and_no_authority_from_resume(self):
        probe = r"""
const assert=require('node:assert/strict'),P=require('./tools/production_workspace/ui/workflow.js');
const record={file:'content/authoring/pz-test/r02/record.json',sha256:'a'.repeat(64)};
const v={puzzle_id:'pz-test',revision:'r02',commit:'b'.repeat(40),
 source_url:'https://github.com/venomenon328/picross/tree/'+'b'.repeat(40),record,
 facts:{state:'background_review',authoring_version:'0.8.0',composition:{raster:'r',reveal:'v',background:null},background_choice:null},
 assets:[{id:'r',role:'raster'},{id:'v',role:'reveal'},{id:'bg',role:'background',location:{sha256:'c'.repeat(64)}}],
 offers:[{id:'A',kind:'background',record,asset_ids:['bg']}]};
const selected={selection:'A',kind:'background'};
for(const saved of [undefined,null,[],{}, {merge:null}, {merge:'false'}])assert.equal(P.options(saved).merge,true);
for(const merge of [false,true])assert.equal(P.options({merge}).merge,merge);
assert.deepEqual(P.options({workroot:'E:/Own',merge:false,cleanup:true}),{workroot:'E:/Own',merge:false});
assert.equal(P.orderStep(v),5);assert.equal(P.step(v),4,'copy does not advance displayed Git phase');
for(const intent of [selected,{selection:'none'}]){
 const before=JSON.stringify(v), text=P.prompt(v,intent,{});
 assert.match(text,/Schritt 5/);assert.match(text,/Ich erteile die Endabnahme/);assert.match(text,/Integration/);
 assert.match(text,/unabhängiges Review/);assert.match(text,/Squash-Merge.*Vor-Merge-Gates/);assert.match(text,/Authoring §9/);
 assert.doesNotMatch(text,/Zur Endabnahme vorbereiten|Keine zusätzliche Abschlussbereinigung|SHA-256|workspace.json/);
 assert.equal(text.split(record.file).length,2);assert.equal(JSON.stringify(v),before);
 const draft=P.prompt(v,intent,{merge:false});assert.match(draft,/Draft-PR.*kein Merge/);assert.doesNotMatch(draft,/Squash-Merge/);
}
for(const action of ['resume','rework']){
 const text=P.prompt(v,{...selected,action,feedback:'Striche korrigieren'},{merge:true});
 assert.doesNotMatch(text,/Ich erteile|Ich wähle|Squash-Merge/);assert.match(text,/kein Merge/);
}
for(const intent of [{},{selection:'missing',kind:'background'},{selection:'A',kind:'raster'}])assert.throws(()=>P.prompt(v,intent,{}));
assert.throws(()=>P.prompt({...v,facts:{...v.facts,composition:null}},selected,{}),/Schlussübersicht/);
for(const role of ['raster','reveal']){
 const invalid={...v,assets:v.assets.filter(a=>a.role!==role)};
 assert.throws(()=>P.prompt(invalid,selected,{}),/Schlussübersicht/);
}
const duplicate={...v,assets:[...v.assets,{id:'other',role:'background',location:{sha256:'d'.repeat(64)}}],
 offers:[{...v.offers[0],asset_ids:['bg','other']}]};
assert.throws(()=>P.prompt(duplicate,selected,{}),/nicht eindeutig/);
v.facts.state='editorially_approved';v.facts.background_choice='A';v.facts.composition.background='bg';v.offers=[];
const retained=P.prompt(v,{},{});assert.doesNotMatch(retained,/Ich erteile|Ich wähle/);assert.match(retained,/bereits endabgenommene/);
v.facts.state='registered';assert.doesNotMatch(P.prompt(v,{},{}),/Ich erteile|Ich wähle/);
"""
        result = subprocess.run(['node', '-e', probe], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_existing_theme_storage_reloads_explicit_system_light_dark(self):
        probe = r"""
const assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
const storage=new Map(),code=fs.readFileSync('tools/production_workspace/ui/app.js','utf8');
function load(){
 const elements=new Map(),document={documentElement:{dataset:{}},getElementById(id){
  if(!elements.has(id))elements.set(id,{replaceChildren(){}});return elements.get(id);
 }};
 vm.runInNewContext(code,{document,location:{hash:'',pathname:'/'},history:{replaceState(){}},
  sessionStorage:{getItem(){},setItem(){}},PW:require('./tools/production_workspace/ui/workflow.js'),
  localStorage:{getItem:k=>storage.get(k),setItem:(k,v)=>storage.set(k,v)},
  fetch:()=>new Promise(()=>{}),setTimeout,clearTimeout,AbortController});
 return {document,theme:elements.get('theme')};
}
assert.equal(load().theme.value,'system');
for(const value of ['dark','light','system']){
 const app=load();app.theme.value=value;app.theme.onchange();
 assert.equal(storage.get('pw-theme'),value);
 const reloaded=load();assert.equal(reloaded.theme.value,value);
 assert.equal(reloaded.document.documentElement.dataset.theme,value);
}
assert.deepEqual([...storage.keys()],['pw-theme'],'no second settings store');
"""
        result = subprocess.run(['node', '-e', probe], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_development_sheet_ignores_legacy_cleanup_and_preserves_workroot(self):
        probe = r"""
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const html=fs.readFileSync('docs/workflow/Entwicklungsworkflow_Cheat-Sheet.html','utf8');
assert.doesNotMatch(html,/id="cleanupToggle"/);
const found=html.match(/function workspaceText\(\)\{[\s\S]*?\n\}/);
assert.ok(found,'workspaceText exists');
for(const cleanup of [true,false]){
 const ctx={profile:()=>({root:'E:/Work',cleanup,task:{fields:{executor:'Codex'}}}),JSON};
 vm.runInNewContext(found[0],ctx);
 const text=ctx.workspaceText();
 assert.match(text,/Lokale Codex-Arbeitswurzel/);
 assert.match(text,/ausschließlich innerhalb dieser Arbeitswurzel/);
 assert.match(text,/Keine zusätzliche Abschlussbereinigung lokaler Arbeitsdaten beauftragt/);
 assert.doesNotMatch(text,/ausdrücklich beauftragt/);
}
"""
        result = subprocess.run(['node', '-e', probe], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_old_sheet_is_only_a_launcher_entry_without_embedded_state_machine(self):
        text=(ROOT/'docs/ai-workflows/Picross_Raetselproduktion_Cheat-Sheet.html').read_text(encoding='utf-8')
        self.assertIn('Picross-Start.exe',text)
        self.assertNotIn('<script',text)
        self.assertNotIn('picross-cheatsheet-session',text)
