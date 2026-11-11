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
const v={puzzle_id:'pz-test',revision:'r01',source_url:'https://github.com/venomenon328/picross/tree/'+'b'.repeat(40),
 record,facts:{state:'reveal_review',authoring_version:'0.8.0'},offers:[]};
let text=P.prompt(null,{brief:'Synthetischer Test, keine Produktion'},opts);
assert.match(text,/Schritt 1/);assert.doesNotMatch(text,/source_commit|localhost|Hintergrund|Kontextzeichnungen/);
assert.throws(()=>P.prompt(null,{},opts),/Motiv/);
for(const [state,n,kind] of [['reveal_review',2,'reveal'],['motif_review',3,null],['motif_approved',3,null],
 ['raster_review',3,null],['raster_ready',4,'raster'],['background_review',4,'background'],['content_ready',5,null],['editorially_approved',5,null]]){
 v.facts.state=state;v.offers=kind?[{id:'A',kind,record}]:[];
 const intent={selection:kind?'A':null,kind,parameters:'etwa 25 × 20',context:'Landschaft'};
 text=P.prompt(v,intent,opts);assert.match(text,new RegExp('Schritt '+n));
 assert.match(text,/kein Merge/);assert.match(text,/content\/pw\/pz-test/);
 if(n<4)assert.doesNotMatch(text,/Kontextwunsch|Kontextzeichnungen|Hintergrundkandidaten/);
 if(kind)assert.throws(()=>P.prompt(v,{},opts),/wählen/);
 for(const action of ['resume','rework'])assert.ok(P.prompt(v,{action,feedback:'Linie korrigieren'},opts).includes(v.source_url));
}
v.facts.state='background_review';assert.match(P.prompt(v,{selection:'none'},opts),/ausdrücklich für keinen Hintergrund/);
v.facts.state='content_ready';assert.match(P.prompt(v,{}, {...opts,merge:true}),/Merge ausdrücklich nur nach/);
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
assert.match(first,/exakt 28 × 19 Zellen/);
assert.match(first,/ungefähr 4 Vordergrundfarben/);
assert.match(first,/Abschlussbild bleibt detailliert und farbig/);
assert.match(build({...grid,sizeAccuracy:'approx',colorAccuracy:'exact'}),/ungefähr 28 × 19.*exakt 4/s);
assert.match(build({mode:'mono'}),/monochrom, genau eine Vordergrundfarbe/);
assert.doesNotMatch(build({...grid,mode:'mono'}),/4 Vordergrundfarben/);
assert.doesNotMatch(build({mode:'color'}),/Farbzahl:/);
assert.doesNotMatch(build({}),/Rastergröße:|Rastermodus:|Farbzahl:/);
for(const bad of [{width:'20'},{height:'10'},{...grid,width:'0'},{...grid,height:'51'},
                  {...grid,height:'1.5'},{...grid,width:'x'},{...grid,colors:'9'},{...grid,colors:'1'}]){
 assert.throws(()=>build(bad),/Bitte/);
}
assert.match(build({...grid,width:'1',height:'50',colors:'8'}),/exakt 1 × 50/);
const record={file:'record.json',sha256:'a'.repeat(64)};
const value={source_url:'https://github.com/venomenon328/picross/tree/'+'b'.repeat(40),
 record,puzzle_id:'pz-test',revision:'r01',facts:{state:'reveal_review',authoring_version:'0.8.0'},
 offers:[{id:'A',kind:'reveal',record}]};
const intent={grid,kind:'reveal',selection:'A'};
assert.equal(P.orderStep(value),2);
assert.match(P.prompt(value,intent,{}),/Schritt 2.*exakt 28 × 19/s);
value.facts.state='motif_review';
assert.doesNotMatch(P.prompt(value,intent,{}),/exakt 28 × 19/);
const correction=P.prompt(value,{...intent,action:'rework',feedback:'Raster anpassen'},{});
assert.match(correction,/exakt 28 × 19/);
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
const record={file:'record.json',sha256:'a'.repeat(64)};
const v={source_url:'https://github.com/venomenon328/picross/tree/'+'b'.repeat(40),record,
 puzzle_id:'pz-test',revision:'r01',facts:{state:'reveal_review',authoring_version:'0.8.0',published},offers:[{id:'A',kind:'reveal',record}]};
const selected={kind:'reveal',selection:'A'};
const base=P.publishedGrid(v);
assert.deepEqual(base,{width:'18',height:'18',sizeAccuracy:'approx',mode:'color',colors:'3',colorAccuracy:'exact'});
for(const intent of [selected,{...selected,grid:base}]){
 const text=P.prompt(v,intent,{});
 assert.match(text,/Quellkontext.*keine neue Freigabe/);assert.doesNotMatch(text,/Neue Absicht|Vorgaben für das spätere Lösungsraster/);
 assert.match(text,/Schritt 2: Ich wähle/);assert.doesNotMatch(text,/Ich gebe.*Parameterkorridor frei/);
}
let text=P.prompt(v,{...selected,grid:{width:'20'},parameters:'Kelch erhalten\nMehr Platz'},{});
assert.match(text,/Neue Absicht.*ungefähr 20 × 18/);assert.match(text,/Neue\/zusätzliche Wünsche.*Kelch erhalten\nMehr Platz/);
assert.throws(()=>P.prompt(v,{...selected,grid:{mode:''}},{}),/ausdrücklich aufheben/);
assert.throws(()=>P.prompt(v,{...selected,grid:{width:'',height:''}},{}),/ausdrücklich aufheben/);
assert.throws(()=>P.prompt(v,{...selected,grid:{colors:''}},{}),/ausdrücklich aufheben/);
text=P.prompt(v,{...selected,removeGrid:{size:true,mode:true,colors:true}},{});
assert.match(text,/Rastergröße: bisherigen Wunsch ausdrücklich aufheben/);assert.match(text,/Farbzahl: bisherigen Wunsch ausdrücklich aufheben/);
published.approved=[{...p,width:22}];
assert.equal(P.publishedGrid(v).width,'22');
text=P.prompt(v,{...selected,grid:{width:'25'}},{});assert.match(text,/Korrekturweg.*erneuten Entscheidung/);
v.facts.state='motif_review';
assert.match(P.prompt(v,{},{}),/Schritt 3: Ich gebe.*Parameterkorridor frei/);
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

    def test_old_sheet_is_only_a_launcher_entry_without_embedded_state_machine(self):
        text=(ROOT/'docs/ai-workflows/Picross_Raetselproduktion_Cheat-Sheet.html').read_text(encoding='utf-8')
        self.assertIn('Picross-Start.cmd',text)
        self.assertNotIn('<script',text)
        self.assertNotIn('picross-cheatsheet-session',text)
