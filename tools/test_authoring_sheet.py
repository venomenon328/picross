"""PW-B prompt regressions replacing superseded offline-session tests."""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AuthoringPromptTests(unittest.TestCase):
    def test_concrete_decisions_are_independent_and_correction_accepts_a_blocked_base(self):
        probe = r"""
const assert=require('node:assert/strict'), P=require('./tools/production_workspace/ui/workflow.js');
const sha='a'.repeat(40), puzzle_id='pz-test';
const row={id:'one',criterion:'Q-H02',binding:'b'.repeat(64),eligible:true,decision:null};
const other={...row,id:'two',binding:'c'.repeat(64)};
const cards={A:{missing:[],findings:[row,other]},B:{missing:['Proof fehlt'],findings:[]}};
const v={puzzle_id,revision:'current',commit:sha,source_url:'https://github.com/venomenon328/picross/tree/'+sha,
 record:{file:'content/authoring/pz-test/current/record.json'},assets:[{id:'A',role:'raster'},{id:'B',role:'raster'}],offers:[{id:'A',kind:'raster'},{id:'B',kind:'raster'}],
 facts:{state:'raster_review',authoring_version:'0.8.0',candidates:cards}};
const intent={selection:'A',kind:'raster',findings:{[row.binding]:{accepted:true,treatment:'Blau behalten'}}};
assert.throws(()=>P.prompt(v,intent),/Offene Voraussetzungen/);
intent.findings[other.binding]={accepted:true,treatment:'Unverändert beibehalten'};
const order=P.prompt(v,intent);
for(const word of ['Blau behalten','Unverändert beibehalten',row.binding,other.binding,'Schritt 4','Rasterangebot A'])assert(order.includes(word));
assert.throws(()=>P.prompt(v,{...intent,selection:'B'}),/Offene Voraussetzungen/);
const correction=P.prompt(v,{action:'rework',selection:'B',kind:'raster',feedback:'Proof ergänzen'});
assert.match(correction,/Korrekturgrundlage: raster\/B/);assert.doesNotMatch(correction,/Ich wähle/);
"""
        subprocess.run(['node','-e',probe],cwd=ROOT,check=True)

    def test_target_phase_open_assessment_and_resume_keep_their_own_scope(self):
        probe = r"""
const assert=require('node:assert/strict'),P=require('./tools/production_workspace/ui/workflow.js');
const sha='a'.repeat(40),hash='b'.repeat(64),row={id:'outline',criterion:'Q-B02',binding:hash,eligible:true,decision:null};
const assets=[{id:'v',role:'reveal'},{id:'v-other',role:'reveal'},{id:'m',role:'motif'},
 {id:'r',role:'raster'},{id:'d',role:'raster_draft'},{id:'bg',role:'background'}];
const v={puzzle_id:'pz-test',revision:'current',commit:sha,source_url:'https://github.com/venomenon328/picross/tree/'+sha,
 record:{file:'content/authoring/pz-test/current/record.json'},assets,offers:[],
 facts:{state:'motif_review',authoring_version:'0.8.0',
  candidates:Object.fromEntries(assets.map((a,i)=>[a.id,{missing:['Sichtung fehlt'],
   findings:[{...row,binding:a.id==='m'?hash:(i+2).toString(16).repeat(64)}]}])),
  originals:{record:{selected:{reveal:'v',motif:null,raster:null,background:null},assets}},
  published:{proposed:[],approved:[]}}};
const personal={workroot:'E:/synthetic',merge:true,executors:{1:'Codex',2:'ChatGPT',3:'Codex',4:'ChatGPT',5:'Codex'}};
const correction={action:'rework',selection:'v',kind:'reveal',feedback:'Kontur erhalten.\nNur den Zweig verkürzen.'};
let text=P.prompt(v,correction,personal);
assert.equal(P.promptStep(v,correction),1);assert.match(text,/Authoring 0.8.0, Schritt 1/);
assert.match(text,/Ausführung mit Codex/);assert.ok(text.includes(correction.feedback));
assert.ok(text.includes('/blob/'+sha+'/'+v.record.file));assert.match(text,/reveal\/v/);
assert.doesNotMatch(text,/Ich wähle|Ich gebe|Ich erteile|Draft-PR|Squash-Merge|PW_REMOTE/);
assert.throws(()=>P.prompt(v,{...correction,selection:'v-other'},personal),/Korrekturgrundlage/);
assert.throws(()=>P.prompt(v,{...correction,kind:'motif'},personal),/Rolle/);
assert.deepEqual(P.actionTargets(v,'assessment').map(a=>a.id),['m']);
for(const executor of P.executors){
 const opts={...personal,executors:{2:executor}};
 const assessment={action:'assessment',selection:'m',kind:'motif',brief:'NICHT SENDEN',notes:'NICHT SENDEN',
  feedback:'NICHT SENDEN',parameters:'NICHT SENDEN',context:'NICHT SENDEN',inputImage:'NICHT SENDEN.png',
  reference:{name:'NICHT SENDEN.png'},grid:{width:'unfertig'},removeGrid:{height:true}};
 const draft=JSON.stringify(assessment);
 assert.deepEqual(P.inboxInputs(v,assessment,'assessment'),
  {brief:'',notes:'',parameters:'',context:'',feedback:'',reference:'',grid:[]});
 text=P.prompt(v,assessment,opts);
 assert.equal(P.promptStep(v,assessment),2);assert.match(text,/unveränderte Angebot motif\/m neu sichten und bewerten/);
 assert.ok(text.includes('Ausführung mit '+executor));
 assert.doesNotMatch(text,/NICHT SENDEN|Breite:|Höhe:|Ich wähle|Ich gebe|Ich erteile|Draft-PR|Squash-Merge|Korrekturgrundlage/);
 assert.equal(JSON.stringify(assessment),draft);
 assert.throws(()=>P.prompt(v,{...assessment,selection:'v',kind:'reveal'},opts),/offenes Reveal- oder Motivangebot/);
 const accepted=P.prompt(v,{...assessment,findings:{[hash]:{accepted:true,treatment:'Rand erhalten'}}},opts);
 assert.match(accepted,/"Entscheidung":"Annahme"/);assert.match(accepted,/Rand erhalten/);
 const foreign=v.facts.candidates.v.findings[0],own={accepted:true,treatment:'Rand erhalten'};
 for(const [stored,edit] of [[null,{accepted:true,treatment:'Fremde Annahme'}],
  [{action:'accept',treatment:'Veröffentlicht'},{accepted:false,treatment:'Widerrufen'}],
  [{action:'accept',treatment:'Veröffentlicht'},{accepted:true,treatment:'Andere Behandlung'}]]){
  foreign.decision=stored;
  const invalid={...assessment,findings:{[hash]:own,[foreign.binding]:edit}},before=JSON.stringify(invalid);
  assert.throws(()=>P.prompt(v,invalid,opts),/nicht zum Bewertungsziel/);
  assert.throws(()=>P.inboxInputs(v,invalid,'assessment'),/nicht zum Bewertungsziel/);
  assert.throws(()=>P.inboxFindings(v,invalid),/nicht zum Bewertungsziel/);
  assert.equal(JSON.stringify(invalid),before,'reject without changing unsent declarations');
 }
 foreign.decision={action:'accept',treatment:'Veröffentlicht'};
 const unchanged={...assessment,findings:{[hash]:own,[foreign.binding]:{accepted:true,treatment:'Veröffentlicht'}}};
 assert.deepEqual(P.inboxFindings(v,unchanged),{[hash]:own},'already published foreign value is no new declaration');
 assert.doesNotMatch(P.prompt(v,unchanged,opts),/Veröffentlicht|"Kandidat":"v"/);
 assert.equal(P.inboxInputs(v,unchanged,'assessment').feedback,'');
 assert.throws(()=>P.prompt(v,{...assessment,findings:{unknown:own}},opts),/Befundbindung/);
 foreign.decision=null;
}
v.facts.state='reveal_review';v.facts.originals.record.selected.reveal=null;
assert.deepEqual(P.actionTargets(v,'assessment').map(a=>a.id),['v','v-other']);
v.facts.state='content_ready';Object.assign(v.facts.originals.record.selected,{reveal:'v',motif:'m',raster:'r',background:'bg'});
for(const [selection,kind,n] of [['v','reveal',1],['m','motif',2],['r','raster',3],['bg','background',4]]){
 const intent={action:'rework',selection,kind,feedback:'Ein gezielter Wunsch'};
 assert.equal(P.promptStep(v,intent),n);assert.match(P.prompt(v,intent,personal),new RegExp('Authoring 0.8.0, Schritt '+n));
}
v.facts.state='raster_review';v.facts.originals.record.selected.raster=null;
assert.equal(P.promptStep(v,{action:'rework',selection:'d',kind:'raster'}),3);
v.facts.state='motif_review';v.facts.originals.record.selected.motif=null;
const resume={action:'resume',selection:'m',kind:'motif',findings:{[hash]:{accepted:true,treatment:'NICHT ERKLÄREN'}}};
text=P.prompt(v,resume,personal);assert.equal(P.promptStep(v,resume),2);
assert.doesNotMatch(text,/NICHT ERKLÄREN|"Entscheidung"|Ich wähle|Ich gebe|Ich erteile|Draft-PR|Squash-Merge/);
v.facts.state='background_review';v.facts.originals.record.selected.background=null;
for(const executor of P.executors){
 text=P.prompt(v,{action:'resume'},{...personal,executors:{4:executor}});
 assert.match(text,/Hintergrundangebote fertig aufbereiten und bewerten/);
 assert.equal(text.includes('PW_REMOTE.md'),executor==='ChatGPT');
 if(executor==='Codex')assert.doesNotMatch(text,/ChatGPT|Inbox|Request|Drive/);
 else assert.doesNotMatch(text,/Codex|E:\/synthetic/);
}
v.facts.state='registered';assert.deepEqual(P.actionTargets(v,'rework'),[]);
assert.throws(()=>P.prompt(v,{action:'rework',selection:'bg',kind:'background',feedback:'Mehr Wald'}),/Korrekturgrundlage/);
const reference={name:'reference.png',bytes:1234,sha256:'c'.repeat(64)};
text=P.prompt(null,{brief:'Neues Motiv',inputImage:reference.name,reference},personal);
for(const item of [reference.name,String(reference.bytes),reference.sha256])assert.ok(text.includes(item));
assert.doesNotMatch(text,/Produktionsdatensatz|Draft-PR|Squash-Merge/);
for(const ref of [undefined,null,{}, {...reference,bytes:undefined},{...reference,bytes:0},
 {...reference,bytes:32*1024*1024+1},{...reference,sha256:'incomplete'},{...reference,name:'other.png'}]){
 const input={brief:'Neues Motiv',inputImage:reference.name,reference:ref};
 for(const executor of P.executors)assert.throws(()=>P.prompt(null,input,{executors:{1:executor}}),/Referenzdatei/);
 assert.throws(()=>P.inboxInputs(null,input,'continue'),/Referenzdatei/);
}
const failed={brief:'Motiv',inputImage:'reference.png',referenceError:'Hashprüfung fehlgeschlagen'};
assert.throws(()=>P.prompt(null,failed),/Hashprüfung fehlgeschlagen/);
assert.throws(()=>P.inboxInputs(null,failed,'continue'),/Hashprüfung fehlgeschlagen/);
assert.deepEqual(P.inboxInputs(null,{brief:'Motiv',inputImage:reference.name,reference},'continue').reference,reference);
"""
        result = subprocess.run(['node', '-e', probe], cwd=ROOT, capture_output=True,
                                text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_actual_generator_for_all_five_steps_correction_resume_and_source_guards(self):
        probe = r"""
const assert=require('node:assert/strict');
const P=require('./tools/production_workspace/ui/workflow.js');
const opts={workroot:'E:/synthetic',cleanup:true,merge:false};
function both(value,intent,phase,remote=phase>=3){
 const [chat,codex]=['ChatGPT','Codex'].map(executor=>
  P.prompt(value,intent,{...opts,executors:{[phase]:executor}}));
 assert.equal(P.promptStep(value,intent),phase);
 assert.match(chat,new RegExp('Authoring 0.8.0, Schritt '+phase));
 assert.match(chat,/Ausführung mit ChatGPT/);
 assert.doesNotMatch(chat,/Codex|E:\/synthetic|localhost|vorherige Unterhaltung|Requestref/);
 assert.equal(chat.includes('docs/tools/PW_REMOTE.md'),remote);
 assert.match(codex,/Ausführung mit Codex.*docs\/tools\/PRODUCTION_GIT_WORKSPACE\.md/);
 assert.doesNotMatch(codex,/PW_REMOTE|ChatGPT|Requestref/);
 assert.match(codex,/Lokale Codex-Arbeitswurzel: E:\/synthetic/);
 const facts=text=>text.split('\n\n').filter(line=>!/^Ausführung mit |^Lokale Codex-Arbeitswurzel:/.test(line));
 assert.deepEqual(facts(chat),facts(codex),'executor choice preserves the exact decisions and inputs');
 assert.doesNotMatch(P.prompt(value,intent,{workroot:'  ',executors:{[phase]:'Codex'}}),/Lokale Codex-Arbeitswurzel/);
 return chat;
}
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
const fresh=both(null,{brief:'Erstes Motiv',inputImage:'reference.png',
 reference:{name:'reference.png',bytes:1234,sha256:'c'.repeat(64)},notes:'Kelch erhalten',grid:{width:'20'}},1);
for(const part of ['Erstes Motiv','reference.png','Kelch erhalten','20 Zellen','PW_IMPORT.md'])assert.ok(fresh.includes(part));
for(const mode of ['mono','color'])for(const [state,n,current,kind] of [['brief_ready',1,1,null],['reveal_review',2,1,'reveal'],['motif_review',3,2,null],['motif_approved',3,3,null],
 ['raster_review',3,3,null],['raster_ready',4,3,'raster'],['background_review',5,4,'background'],['content_ready',5,5,null],['editorially_approved',5,5,null],['registered',5,5,null]]){
 v.facts.published={proposed:[{mode,foreground_colors:mode==='mono'?1:3}],approved:[]};
 v.facts.state=state;v.offers=kind?[{id:'A',kind,record,asset_ids:['bg']}]:[];
 const intent={selection:kind?'A':null,kind,parameters:'etwa 25 × 20',context:'Landschaft'};
 both(v,intent,n);
 text=P.prompt(v,intent,opts);assert.match(text,new RegExp('Schritt '+n));
 if(n===5)assert.match(text,/kein Merge/);else assert.doesNotMatch(text,/Draft-PR|Commit, Push|Merge/);assert.ok(text.includes(record.file));assert.ok(text.includes('b'.repeat(40)));
 assert.match(text,new RegExp('AGENTS.md.*Authoring 0.8.0, Schritt '+n+'\\.'));
 assert.doesNotMatch(text,/monochrom|Monochrom|RGB|tools\.(work_publish|publish_git)|RI-ONE|Proof|Copilot|Reviewer|Endmatrix/);
 if(n<4)assert.doesNotMatch(text,/Kontextwunsch|Kontextzeichnungen|Hintergrundkandidaten/);
 if(kind)assert.throws(()=>P.prompt(v,{},opts),/wählen/);
 for(const action of ['resume']){
  both(v,{action,feedback:'Linie korrigieren'},current);
  const changed=P.prompt(v,{action,feedback:'Linie korrigieren'},opts);
  assert.ok(changed.includes(record.file));
  assert.match(changed,new RegExp('Authoring 0.8.0, Schritt '+current+'\\.'));
  assert.doesNotMatch(changed,/Ich wähle|Ich gebe|Ich erteile|Squash-Merge|Integration|monochrom|Monochrom|tools\./);
  assert.doesNotMatch(changed,/Commit, Push|Draft-PR/);
 }
}
v.facts.state='background_review';assert.match(P.prompt(v,{selection:'none'},opts),/ausdrücklich für keinen Hintergrund/);
v.facts.state='content_ready';assert.match(P.prompt(v,{}, {...opts,merge:true}),/bei erfüllten Pflichtgates nach Authoring Schritt 5 §8 per Squash-Merge nach main integrieren/);
for(const url of [null,'http://localhost:1234/job','https://github.com/venomenon328/picross/tree/main']){
 v.source_url=url;assert.throws(()=>P.prompt(v,{},opts),/Remote-Sicherung/);
}
v.source_url='https://github.com/venomenon328/picross/tree/'+'b'.repeat(40);v.facts.state='registered';
assert.doesNotMatch(P.prompt(v,{},opts),/Ich erteile/);
assert.match(both(v,{action:'background_change',feedback:'Mehr Wald'},5,false),/Bestands- und Revisionsweg.*Schritt 5 §9/);
const backgroundChange=P.prompt(v,{action:'background_change',feedback:'Mehr Wald'},opts);
assert.match(backgroundChange,/Hintergrundrevision nach Authoring Schritt 5 §9: Mehr Wald/);
assert.doesNotMatch(backgroundChange,/als aktuellen RI-ONE-Eingang vorbereiten/);
v.source_url='https://github.com/venomenon328/picross/tree/'+'b'.repeat(40);v.facts.authoring_version='0.7.0';
assert.throws(()=>P.prompt(v,{},opts),/historische/);
v.facts.authoring_version='0.8.0';v.facts.state='background_review';v.revision='current';
v.record={file:'content/authoring/pz-test/current/record.json',sha256:'d'.repeat(64)};
text=P.prompt(v,{selection:'standard'},opts);
assert.match(text,/Standardhintergrund/);assert.match(text,/AGENTS.md.*Authoring 0.8.0, Schritt 5/);
assert.ok(text.includes(v.record.file));assert.match(text,/beauftrage deren Integration/);
assert.doesNotMatch(text,/Arbeitsbelege mitführen/);
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
assert.match(first,/Abschlussbilder als reveal_review.*zur Auswahl/);
assert.doesNotMatch(first,/Monochrom|monochrom|ohne Leerfelder/);
assert.match(build({...grid,sizeAccuracy:'approx',colorAccuracy:'exact'}),/Breite: ungefähr 28 Zellen.*Höhe: ungefähr 19 Zellen.*exakt 4/s);
assert.match(build({mode:'mono'}),/Rastermodus: monochrom\./);
assert.doesNotMatch(build({...grid,mode:'mono'}),/4 Vordergrundfarben/);
assert.doesNotMatch(build({mode:'color'}),/Farbzahl:/);
assert.match(build({colors:'1',colorAccuracy:'exact'}),/Farbzahl: exakt eine Vordergrundfarbe\./);
assert.doesNotMatch(build({colors:'1',colorAccuracy:'exact'}),/Parameterfestlegung|Monochrom/);
assert.throws(()=>build({mode:'color',colors:'1',colorAccuracy:'exact'}),/2 bis 8/);
assert.doesNotMatch(build({}),/Rastergröße:|Rastermodus:|Farbzahl:/);
for(const bad of [{...grid,width:'0'},{...grid,height:'51'},
                  {...grid,height:'1.5'},{...grid,width:'x'},{...grid,colors:'9'},{...grid,colors:'1'}]){
 assert.throws(()=>build(bad),/Bitte/);
}
assert.match(build({...grid,width:'1',height:'50',colors:'8'}),/Breite: exakt 1 Zellen.*Höhe: exakt 50 Zellen/s);
const record={file:'content/authoring/pz-test/r01/record.json',sha256:'a'.repeat(64)};
const value={commit:'b'.repeat(40),source_url:'https://github.com/venomenon328/picross/tree/'+'b'.repeat(40),
 record,puzzle_id:'pz-test',revision:'r01',facts:{state:'reveal_review',authoring_version:'0.8.0'},
 assets:[{id:'A',role:'reveal'},{id:'M',role:'motif'}],offers:[{id:'A',kind:'reveal',record}]};
const intent={grid,kind:'reveal',selection:'A'};
assert.equal(P.orderStep(value),2);
assert.match(P.prompt(value,intent,{}),/Schritt 2.*Breite: exakt 28 Zellen/s);
value.facts.state='motif_review';
assert.doesNotMatch(P.prompt(value,intent,{}),/Breite: exakt 28 Zellen/);
assert.doesNotMatch(P.prompt(value,intent,{}),/Monochrom|RGB|Angebotslabel/);
const correction=P.prompt(value,{...intent,action:'rework',selection:'M',kind:'motif',feedback:'Raster anpassen'},{});
assert.match(correction,/Breite: exakt 28 Zellen/);
assert.match(correction,/Authoring 0.8.0, Schritt 2/);
assert.doesNotMatch(correction,/Ich gebe.*frei/);
value.facts.state='reveal_review';
assert.throws(()=>P.prompt(value,{...intent,action:'rework',feedback:'Kontur korrigieren',parameters:'Kelch erhalten'},{}),/Motivvorlagenwünsche gehören/);
const revealCorrection=P.prompt(value,{...intent,action:'rework',feedback:'Kontur korrigieren',notes:'Kelch erhalten'},{});
assert.match(revealCorrection,/Authoring 0.8.0, Schritt 1/);
assert.match(revealCorrection,/Breite: exakt 28 Zellen/);assert.match(revealCorrection,/Motivhinweise:.*Kelch erhalten/s);
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
text=P.prompt(v,{...selected,grid:{width:'25'}},{});assert.match(text,/Neue Absicht.*Breite: ungefähr 25 Zellen/);
v.facts.state='motif_review';
assert.match(P.prompt(v,{},{}),/Schritt 3: Ich gebe.*Parameterkorridor.*frei/);
v.assets=[{id:'M',role:'motif'}];
text=P.prompt(v,{action:'rework',selection:'M',kind:'motif',feedback:'Anpassen',grid:{width:'25'}},{});
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
const defaults={1:'Codex',2:'Codex',3:'ChatGPT',4:'Codex',5:'ChatGPT'};
assert.deepEqual(P.options({workroot:'E:/Own',merge:false,cleanup:true}),{workroot:'E:/Own',merge:false,executors:defaults});
for(const executors of [undefined,null,[],false,'ChatGPT'])assert.deepEqual(P.options({executors}).executors,defaults);
assert.deepEqual(P.options({workroot:42,merge:'false',executors:{2:'ChatGPT',3:'Codex',4:'other',5:false,6:'Codex'}}),
 {workroot:'',merge:true,executors:{...defaults,2:'ChatGPT',3:'Codex'}});
assert.equal(P.orderStep(v),5);assert.equal(P.step(v),4,'copy does not advance displayed Git phase');
for(const intent of [selected,{selection:'none'}]){
 const before=JSON.stringify(v), text=P.prompt(v,intent,{});
 const draft=P.prompt(v,intent,{merge:false});
 for(const order of [text,draft]){
  assert.match(order,/AGENTS.md.*Pflichtquellen für Authoring 0.8.0, Schritt 5/);
  assert.doesNotMatch(order,/Copilot|Reviewer|Zweitreview|Proof|Endmatrix|PR-Diff|RI-ONE|tools\./);
 }
 assert.match(text,/Schritt 5/);assert.match(text,/Ich erteile die Endabnahme/);assert.match(text,/Integration/);
 assert.match(text,/bei erfüllten Pflichtgates nach Authoring Schritt 5 §8 per Squash-Merge nach main integrieren/);
 assert.match(text,/Produktionsabschluss nach §9 ausführen/);
 assert.doesNotMatch(text,/Zur Endabnahme vorbereiten|Keine zusätzliche Abschlussbereinigung|SHA-256|workspace.json/);
 assert.equal(text.split(record.file).length,2);assert.equal(JSON.stringify(v),before);
 assert.match(draft,/Draft-PR.*kein Merge/);assert.doesNotMatch(draft,/Squash-Merge|Produktionsabschluss/);
}
for(const action of ['resume','rework']){
 const text=P.prompt(v,{selection:action==='rework'?'bg':'A',kind:'background',action,feedback:'Striche korrigieren'},{merge:true});
 assert.doesNotMatch(text,/Ich erteile|Ich wähle|Squash-Merge|work_publish retire|Commit, Push|Draft-PR/);
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
 assert.ok(text.includes('E:/Work'));
 assert.doesNotMatch(text,/ausschließlich innerhalb|Abschlussbereinigung|nicht verfügbar|Ersatzpfad/);
}
for(const root of ['',null]){
 const ctx={profile:()=>({root,task:{fields:{executor:'Codex'}}}),JSON};
 vm.runInNewContext(found[0],ctx);assert.equal(ctx.workspaceText(),'');
}
"""
        result = subprocess.run(['node', '-e', probe], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stderr)
