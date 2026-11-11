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

    def test_old_sheet_is_only_a_launcher_entry_without_embedded_state_machine(self):
        text=(ROOT/'docs/ai-workflows/Picross_Raetselproduktion_Cheat-Sheet.html').read_text(encoding='utf-8')
        self.assertIn('Picross-Start.cmd',text)
        self.assertNotIn('<script',text)
        self.assertNotIn('picross-cheatsheet-session',text)
