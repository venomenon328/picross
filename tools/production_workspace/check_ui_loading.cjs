'use strict';
// Execute the actual UI against the real loopback service with a tiny DOM stand-in.
// This checks loading/cancellation, not browser rendering or the separate T02 gate.
const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {createHash} = require('node:crypto');
const vm = require('node:vm');
const [origin, token, expectedHashesJson, mode = 'late', action] = process.argv.slice(2);
const expectedHashes = JSON.parse(expectedHashesJson);
class Element {
  constructor(tag) { this.tag = tag; this.children = []; this.dataset = {}; this.classList = {toggle(){}}; }
  append(...children) { this.children.push(...children); }
  before() {}
  replaceChildren(...children) { this.children = children; }
  setAttribute() {}
  close() { this.open=false; }
  showModal() { this.open=true; }
  focus() {}
  select() {}
}
const elements = new Map();
const stored = new Map();
if(mode==='parameters')stored.set('pw-options',JSON.stringify({
  workroot:'E:/Synthetic',merge:false,executors:{2:'malformed',3:'ChatGPT'}
}));
if(mode==='inbox-resume')stored.set('pw-options',JSON.stringify({
  executors:{1:'ChatGPT',2:'ChatGPT'}
}));
let copied, starts=0;
const document = {
  documentElement: new Element('html'),
  getElementById(id) {
    const view=elements.get('view');
    const match=view&&descendants(view).find(el=>el.id===id);
    if(match)return match;
    if (!elements.has(id)) elements.set(id, new Element(id));
    return elements.get(id);
  },
  querySelectorAll(selector) {
    const [,tag,attribute]=selector.match(/^(\w*)\[data-([\w-]+)\]$/);
    const key=attribute.replace(/-([a-z])/g,(_,letter)=>letter.toUpperCase());
    return descendants(this.getElementById('view')).filter(el=>(!tag||el.tag===tag)&&Object.hasOwn(el.dataset,key));
  },
  createElement: tag => new Element(tag)
};
const descendants = el => [el, ...el.children.flatMap(descendants)];
const cards = () => descendants(document.getElementById('view')).filter(el => el.tag === 'figure');
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
async function until(test, timeout = 10000) {
  const end = Date.now() + timeout;
  while (!test()) { assert(Date.now() < end, 'UI loading deadline'); await delay(10); }
}
let active = 0, peak = 0, retries = 0, forceFailure = false, failOnce = mode === 'late', oldJob;
let aborted = 0, metadataBusy = 0, imageBusy = 0;
let holdDetail=false,releaseDetail=null;
const fetched = [], hashes = [];
const context = vm.createContext({
  document, location: {hash: '#' + token, pathname: '/'}, history: {replaceState(){}},
  sessionStorage: {setItem(){}, getItem(){}},
  localStorage: {setItem(key,value){stored.set(key,value);}, getItem(key){return stored.get(key);}},
  navigator: {clipboard:{async writeText(value){copied=value;}}},
  AbortController, setTimeout, clearTimeout,
  crypto: require('node:crypto').webcrypto,
  URL: {createObjectURL() { return 'blob:test-' + hashes.length; }, revokeObjectURL(){}},
  fetch: async (path, options) => {
    if(path.startsWith('/api/removal/')||path.startsWith('/api/inbox/'))options={...options,headers:{...options.headers,Origin:origin}};
    if(mode==='inbox'&&path==='/api/jobs')return new Promise(()=>{});
    if(mode==='inbox'&&path==='/api/inbox/start'){
      starts++;
      const response=await fetch(origin+path,options);
      assert.equal(response.status,200);
      if(starts===1)throw Error('Test: Aktivierungsantwort verloren');
      return response;
    }
    if (!path.includes('/assets/')) {
      const delayed=holdDetail&&path.startsWith('/api/jobs/');
      if(delayed)holdDetail=false;
      const response = await fetch(origin + path, delayed?{...options,signal:undefined}:options);
      if(delayed)await new Promise(resolve=>{releaseDetail=resolve;});
      if (response.status === 503) metadataBusy++;
      return response;
    }
    fetched.push(path);
    if (forceFailure) return new Response('{"error":"temporary failure"}', {status: 400});
    if (failOnce) { failOnce = false; retries++; return new Response('{"error":"busy"}', {status: 503}); }
    active++; peak = Math.max(peak, active);
    try {
      // Cover both immediate transport abort and a response that arrives too late.
      const response = await fetch(origin + path, mode === 'abort' ? options : {...options, signal: undefined});
      if (response.status === 503) imageBusy++;
      const bytes = await response.arrayBuffer();
      if (response.ok) hashes.push(createHash('sha256').update(Buffer.from(bytes)).digest('hex'));
      return new Response(bytes, {status: response.status});
    } catch (error) {
      if (error.name === 'AbortError') aborted++;
      throw error;
    } finally { active--; }
  }
});
const run = code => vm.runInContext(code, context);
(async () => {
  run(readFileSync(__dirname + '/ui/workflow.js', 'utf8'));
  run(readFileSync(__dirname + '/ui/app.js', 'utf8'));
  if(mode==='inbox-resume'){
    const get=id=>document.getElementById(id);
    await until(()=>run('inboxState?.folder&&readyImages.has("one")&&detail')&&get('copyOrder').onclick);
    if(action==='copy-bound'){
      const original=run('currentOrder().prompt');
      await get('copyOrder').onclick();assert.equal(copied,original);
      console.log(JSON.stringify(copied));return;
    }
    await until(()=>run('!currentOrder()'));
    const modeSelect=get('nextActionMode');
    if(run('detail.facts.state')==='reveal_review'){
      const choice=descendants(get('view')).find(el=>el.dataset.choice==='one');
      assert.equal(choice.disabled,false);
      choice.onclick();
      const wishes=descendants(get('view')).find(el=>el.textContent?.startsWith('Neue/zusätzliche Wünsche zur Motivvorlage'));
      wishes.children[0].value='Kontur für die Motivvorlage erhalten';wishes.children[0].oninput();
    }
    modeSelect.value=action==='continue'?'continue':'resume';modeSelect.onchange();
    assert.equal(get('executor').value,'ChatGPT');
    assert.equal(get('copyOrder').textContent,'Auftrag starten und kopieren');
    assert.equal(get('copyOrder').disabled,false,get('orderStatus').textContent);
    await get('copyOrder').onclick();
    assert.equal(get('orderStatus').textContent,'Auftrag kopiert.');
    assert.match(copied,/Drive: Suche unter Root-ID fixture/);
    assert.equal(get('copyOrder').textContent,'Auftrag kopieren');
    console.log(JSON.stringify(copied));return;
  }
  if(mode==='inbox'){
    await until(()=>run('inboxState?.folder'));
    run("listing={snapshot:'snapshot',jobs:[],motifs:[],errors:[]};newDraft();remember('brief','Fuchs');personal.executors[1]='ChatGPT';updatePrompt()");
    const get=id=>document.getElementById(id);
    assert.equal(starts,0);
    assert.equal(get('orderText').value,'');
    await Promise.all([get('copyOrder').onclick(),get('copyOrder').onclick()]);
    assert.equal(starts,1);
    assert.match(get('orderStatus').textContent,/verloren/);
    context.navigator.clipboard.writeText=async()=>{throw Error('Clipboard');};
    await get('copyOrder').onclick();
    assert.match(get('orderStatus').textContent,/Kopieren fehlgeschlagen/);
    const saved=get('orderText').value;
    assert.match(saved,/pz-fuchs/);
    context.navigator.clipboard.writeText=async text=>{copied=text;};
    await get('copyOrder').onclick();
    assert.equal(copied,saved);
    assert.equal(starts,2,'re-copy uses persisted bytes without activating again');
    assert.equal(get('jobs').value,'pz-fuchs');
    const first=run('currentOrder().puzzle_id');
    const originalId=run('currentOrder().request_id');
    const reloaded=vm.createContext({...context,document,fetch:()=>new Promise(()=>{}),localStorage:{getItem(){},setItem(){}}});
    const reload=code=>vm.runInContext(code,reloaded);
    for(const file of ['workflow.js','app.js'])reload(readFileSync(__dirname+'/ui/'+file,'utf8'));
    reloaded.state=JSON.parse(run('JSON.stringify(inboxState)'));
    reload("listing={snapshot:'snapshot',jobs:[],motifs:[],errors:[]};showInbox(state)");
    assert.equal(reload('selectedId()'),first);
    assert.equal(reload('currentOrder().request_id'),originalId);
    assert.equal(get('orderText').value,saved);
    const other={...reloaded.state.orders[0],puzzle_id:'pz-zweiter',request_id:'other',inputs:{brief:'Zweiter'}};
    reloaded.state={...reloaded.state,orders:[other,...reloaded.state.orders]};
    const panel=get('orderText');reload('showInbox(state)');
    assert.equal(get('orderText'),panel);
    reload("chooseMotif('pz-zweiter')");assert.equal(reload('selectedId()'),'pz-zweiter');
    reload("chooseMotif('pz-fuchs')");assert.equal(get('orderText').value,saved);
    assert.equal(descendants(get('view')).filter(e=>e.id==='copyOrder').length,1);
    let releasePoll;
    reloaded.fetch=()=>new Promise(resolve=>{releasePoll=resolve;});
    const late=reload('pollInbox()');
    reloaded.fetch=context.fetch;reloaded.confirm=()=>true;
    await get('receiptCancel').onclick();
    assert.equal(reload('draft.brief'),'Fuchs','restore the editable briefing without browser storage');
    releasePoll(new Response(JSON.stringify(reloaded.state)));
    await late;
    assert.equal(reload('currentOrder()'),undefined,'a pre-cancel status response cannot restore the receipt');
    get('executor').value='Codex';get('executor').onchange();
    assert.match(get('orderText').value,/tatsächlichen Korrekturverbrauch klären/);
    assert.equal(starts,2);
    get('executor').value='ChatGPT';get('executor').onchange();
    await get('copyOrder').onclick();
    assert.equal(reload('selectedId()'),first);
    assert.notEqual(reload('currentOrder().request_id'),originalId);
    assert.equal(copied,get('orderText').value);
    const expired=await fetch(origin+'/api/inbox/cancel',{method:'POST',headers:{
      Origin:origin,'X-Workspace-Session':token,'Content-Type':'application/json'
    },body:JSON.stringify({puzzle_id:first,request_id:originalId})});
    assert(!expired.ok,'the old binding cannot cancel the new receipt');
    const live=reload('currentOrder()');
    reloaded.done={...live,result:{head:'b'.repeat(40)},step:'done'};
    reloaded.remote={remote_confirmed:true,jobs:[{id:'row',source:'remote',ref:'content/pw/'+first,puzzle_id:first,commit:'b'.repeat(40)}],
      motifs:[{puzzle_id:first,current_job:'row'}]};
    assert.equal(reload('resultJob(remote,done).id'),'row');
    assert.equal(reload("resultJob(remote,{...done,puzzle_id:'pz-fremd'})"),undefined);
    assert.equal(reload("resultJob(remote,{...done,result:{head:'c'.repeat(40)}})"),undefined);
    assert.equal(reload('resultJob({...remote,remote_confirmed:false},done)'),null);
    reloaded.remote.jobs[0].commit='c'.repeat(40);
    assert.equal(reload('resultJob(remote,done)'),undefined);
    reloaded.remote.jobs[0].receipt_ancestor=reloaded.done.result.head;
    assert.equal(reload('resultJob(remote,done).commit'),'c'.repeat(40));
    reloaded.fetch=()=>new Promise(resolve=>{releasePoll=resolve;});
    reload('showInbox({...inboxState,orders:[done]})');
    reload("newDraft();remember('brief','Ungesendeter Motivtext')");
    const kept=reload('generation');
    releasePoll(new Response(JSON.stringify(reloaded.remote)));
    await delay(20);
    assert.equal(reload('generation'),kept);
    assert.equal(reload('intent.brief'),'Ungesendeter Motivtext');
    reload("listing.completion={confirmed:true,completed_ids:[done.puzzle_id]}");
    assert.equal(reload('navigationRows()[0].remainder'),true);
    console.log(JSON.stringify(copied));return;
  }
  await until(()=>run('listing!==null'));
  // Pointerless synthetic legacy inputs now require a deliberate version choice.
  if(mode==='published')await run('open(listing.jobs.find(j=>j.revision==="r01").id)');
  else if(run('detail===null'))await run('open(listing.jobs[0].id)');
  if(mode==='parameters'){
    const get=id=>document.getElementById(id);
    const fields=()=>descendants(get('view'));
    const selector=()=>fields().find(el=>el.tag==='label'&&el.textContent==='Parameteralternative')?.children[0];
    const chooseMotif=()=>fields().find(el=>el.dataset.choice==='motif-a');
    const ready=()=>until(()=>chooseMotif()?.disabled===false);
    const prompt=()=>get('orderText').value;
    const executor=name=>{get('executor').value=name;get('executor').onchange();};
    const words=el=>descendants(el).map(child=>child.textContent||'').join('\n');
    async function search(){
      await get('refresh').onclick();
      await until(()=>get('load').hidden===false);
    }
    const adopt=()=>get('load').onclick();
    await ready();
    assert.equal(get('executor').value,'ChatGPT');
    assert.equal(get('workrootField').hidden,true);
    assert.equal(get('merge').checked,false);
    executor('Codex');
    assert.equal(get('copyOrder').disabled,true,'executor cannot replace motif choice');
    assert.equal(get('workrootField').hidden,false);
    assert.equal(get('workroot').value,'E:/Synthetic');
    executor('ChatGPT');
    assert.equal(selector(),undefined,'one option with two imports has no select');
    assert.match(get('orderStatus').textContent,/Motivvorlage wählen/);
    const record=run('JSON.stringify(detail.facts.originals.record)');
    chooseMotif().onclick();
    assert.equal(run('intent.parameter'),undefined);
    await get('copyOrder').onclick();
    assert.equal(copied,prompt());
    assert.match(copied,/blob\/[a-f0-9]{40}\/content\/authoring\/pz-current\/current\/record\.json/);
    assert.match(copied,/Motivvorlage motif-a und den einzigen vollständigen Vorschlag.*Eintrag 1/);
    const chat=copied, beforeSwitch=run('JSON.stringify(intent)'), requestCount=fetched.length;
    executor('Codex');
    assert.match(prompt(),/Lokale Codex-Arbeitswurzel: E:\/Synthetic/);
    await get('copyOrder').onclick();
    assert.equal(copied,prompt());
    executor('ChatGPT');
    assert.equal(prompt(),chat);
    assert.equal(run('JSON.stringify(intent)'),beforeSwitch);
    assert.equal(fetched.length,requestCount);
    assert.doesNotMatch(copied,/actual_crop|protected_features|\bimports\b/);
    assert.equal(run('JSON.stringify(detail.facts.originals.record)'),record);
    const original=get('technicalDetails');
    assert(!original.open);
    await descendants(original).find(el=>el.textContent==='Übergabedaten kopieren').onclick();
    assert.equal(JSON.parse(copied).facts.originals.record.parameters.proposed[0].imports.length,2);
    assert.match(words(get('view')),/Breite: ungefähr 20 Zellen · Untergrenze: 18 · Obergrenze: 21/);
    assert.match(words(get('view')),/Erlaubte Beschnittseiten: links, rechts/);
    const mode=get('nextActionMode');
    mode.value='rework';mode.onchange();
    assert.equal(get('executor').value,'Codex','correction uses displayed step 2');
    const correction=get('correctionBase');correction.value='motif-a';correction.onchange();
    const feedback=get('correctionFeedback');feedback.value='Kontur {A} ergänzen';feedback.oninput();
    assert.match(prompt(),/Kontur \{A\} ergänzen/);
    executor('ChatGPT');
    assert.equal(prompt(),'','creative order becomes copyable after successful activation');
    assert.equal(get('copyOrder').textContent,'Auftrag starten und kopieren');
    assert.equal(feedback.value,'Kontur {A} ergänzen');
    assert.doesNotMatch(prompt(),/gebe Motivvorlage/);
    mode.value='resume';mode.onchange();
    assert.equal(get('executor').value,'ChatGPT');
    assert.equal(get('copyOrder').textContent,'Auftrag starten und kopieren');
    assert.equal(prompt(),'','the ChatGPT resume prompt requires a bound order');
    executor('Codex');
    assert.match(prompt(),/wieder aufnehmen/);
    assert.doesNotMatch(prompt(),/gebe Motivvorlage/);
    executor('ChatGPT');
    mode.value='continue';mode.onchange();
    assert.equal(get('copyOrder').disabled,true,'a correction basis is never a motif approval');
    executor('Codex');
    chooseMotif().onclick();
    await search();
    assert.match(prompt(),/einzigen vollständigen Vorschlag/);
    adopt();
    await ready();
    assert.equal(run('intent.selection'),undefined);
    assert.equal(get('copyOrder').disabled,true);
    chooseMotif().onclick();
    assert.equal(get('copyOrder').disabled,true,'multiple options require deliberate choice');
    const select=selector();
    assert.equal(select.children[0].value,'');
    assert.match(select.children[1].textContent,/Alternative 1.*Breite ungefähr 20/);
    assert.match(select.children[2].textContent,/Alternative 2.*Breite exakt 19/);
    function selectOption(index){
      select.value=String(index);select.onchange();
      return words(fields().find(el=>el.children.some(child=>child.children.includes(select))).children[1]);
    }
    const first=selectOption(0);
    assert.match(first,/Höhe: offen · Untergrenze: 18 · Obergrenze: 26/);
    assert.match(first,/Erlaubte Beschnittseiten: links, rechts/);
    assert.match(first,/Kontur A/);
    assert.doesNotMatch(first,/Silhouette B/);
    const second=selectOption(1);
    assert.match(second,/Vordergrundfarben: offen · Untergrenze: 2 · Obergrenze: 3/);
    assert.match(second,/Erlaubte Beschnittseiten: keine/);
    assert.match(second,/Silhouette B/);
    assert.doesNotMatch(second,/Kontur A/);
    assert.match(prompt(),/ausdrücklich gewählte Alternative.*Eintrag 2/);
    const oldPrompt=prompt();
    executor('ChatGPT');
    assert.equal(run('intent.parameter'),1);
    assert.match(prompt(),/ausdrücklich gewählte Alternative.*Eintrag 2/);
    executor('Codex');
    assert.equal(prompt(),oldPrompt);
    await search();
    assert.equal(prompt(),oldPrompt,'passive search keeps choice and fixed source');
    holdDetail=true;releaseDetail=null;
    const stale=run('open(active.id)');
    await until(()=>releaseDetail!==null);
    adopt();
    await ready();
    releaseDetail();await stale;
    assert.notEqual(run('detail.commit'),oldPrompt.match(/blob\/([a-f0-9]{40})/)[1]);
    assert.equal(run('intent.selection'),undefined);
    assert.equal(run('intent.parameter'),undefined);
    assert.equal(get('copyOrder').disabled,true);
    assert.match(selector().children[1].textContent,/Alternative 1.*Breite exakt 19/);
    chooseMotif().onclick();
    assert.equal(get('copyOrder').disabled,true,'reordering never transfers old parameter choice');
    await search();adopt();
    await until(()=>run('detail?.facts.originals.record.parameters.proposed.length===0&&readyImages.has("motif-a")'));
    assert.equal(chooseMotif(),undefined,'a motif without parameters is a correction draft');
    assert.equal(selector(),undefined);
    assert.equal(get('copyOrder').disabled,true);
    assert.match(words(get('view')),/Parametervorschlag für die Motivwahl fehlt/);
    const draftMode=get('nextActionMode');draftMode.value='rework';draftMode.onchange();
    assert(get('correctionBase').children.some(option=>option.value==='motif-a'),'draft remains available for correction');
    run('dispose()');
    const reopened=vm.createContext({...context,bound:run('detail'),fetch:()=>new Promise(()=>{})});
    const read=code=>vm.runInContext(code,reopened);
    read(readFileSync(__dirname+'/ui/workflow.js','utf8'));
    read(readFileSync(__dirname+'/ui/app.js','utf8'));
    read('$("view").replaceChildren();workflow($("view"),bound)');
    assert.equal(get('merge').checked,false);
    assert.equal(get('executor').value,'Codex');
    assert.equal(get('workroot').value,'E:/Synthetic');
    get('nextActionMode').value='rework';get('nextActionMode').onchange();
    assert.equal(get('executor').value,'ChatGPT');
    assert.equal(get('workrootField').hidden,true);
    return;
  }
  if(mode==='removal'){
    await until(()=>run('detail!==null'));
    const target=run('listing.jobs.find(j=>j.source==="remote"&&j.ref==="content/pw/pz-workspace-test")');
    assert.equal(document.getElementById('jobs').children.length,1,'one motif despite source/ref/revision duplicates');
    assert.equal(run('currentMotif().versions.length'),2);
    assert.equal(run('currentMotif().versions[0].source_label'),'Remote');
    await assert.rejects(run('removalPost("preview",{job_id:active.puzzle_id,snapshot:listing.snapshot})'));
    await run(`open(${JSON.stringify(target.id)})`);
    const removeButton=()=>descendants(document.getElementById('view')).find(e=>e.textContent==='Produktion entfernen');
    assert.equal(removeButton().disabled,true,'automatic remote opening is no explicit removal source');
    run('intent.feedback="unsent old source"');
    document.getElementById('jobSource').value=target.id;
    document.getElementById('jobSource').onchange();
    await until(()=>run('detail!==null&&remoteExplicit'));
    assert.equal(run('intent.feedback'),undefined,'explicit source switch discards old intentions');
    assert.equal(removeButton().disabled,false);
    await run('previewRemoval({job_id:active.id,snapshot:listing.snapshot})');
    const nodes=()=>descendants(document.getElementById('removalBody'));
    assert(nodes().some(e=>e.textContent==='r01, r02'));
    assert(nodes().some(e=>e.textContent==='refs/heads/content/pw/pz-workspace-test'));
    const input=nodes().find(e=>e.id==='removalConfirmation');
    const button=nodes().find(e=>e.textContent==='Remote-Branch jetzt entfernen');
    assert.equal(button.disabled,true);
    input.value='main';input.oninput();assert.equal(button.disabled,true);
    input.value=target.ref;input.oninput();assert.equal(button.disabled,false);
    await button.onclick();
    assert(nodes().some(e=>e.textContent==='Remote-Branch entfernt'));
    const optional=nodes().find(e=>e.type==='checkbox');assert.equal(optional.checked,false);
    assert(nodes().find(e=>e.textContent==='Lokale Bereinigung vorprüfen').disabled);
    assert(nodes().some(e=>e.textContent?.includes('offene Lieferungen bleiben in der aktiven Auswahl sichtbar')));
    assert(nodes().some(e=>e.textContent?.includes('In main registrierte Rätsel sind aus der aktiven Produktion ausgeblendet')));
    assert(!run('listing.jobs.some(j=>j.source==="local")'),'local remainder is diagnostic only');
    assert(!run('listing.jobs.some(j=>j.source==="remote"&&j.ref==="content/pw/pz-workspace-test")'));
    console.log('P2 controller: exact branch/revisions, typed confirmation, real HTTP deletion, local remainder and default-off cleanup passed. No browser-rendering claim.');
    return;
  }
  if(mode==='published'){
    await until(()=>run('detail!==null'));
    const first=run('active.id'),second=run('listing.jobs.find(j=>j.revision==="r02").id');
    assert.equal(document.getElementById('jobs').children.length,1);
    const labels=document.getElementById('jobs').children.map(el=>el.textContent);
    assert.equal(new Set(labels).size,1);
    assert.equal(run('currentMotif().versions.length'),2);
    assert(document.getElementById('version').children.some(e=>e.textContent.includes('r02')));
    assert(!readFileSync(__dirname+'/ui/index.html','utf8').includes('id="jobList"'));
    const fields=()=>descendants(document.getElementById('view'));
    const input=label=>descendants(fields().find(el=>el.tag==='label'&&el.textContent===label)).find(el=>['input','select','textarea'].includes(el.tag));
    const originals=()=>fields().filter(el=>el.tag==='details'&&el.children.some(c=>['Technische Details & vollständige Übergabedaten','Veröffentlichtes Motivbriefing'].includes(c.textContent)));
    assert.equal(originals().length,2);assert(originals().every(el=>!el.open),'originals start closed');
    originals()[0].open=true;assert(!originals()[1].open,'independent disclosure');
    assert.equal(input('Breite').value,'18');
    assert.equal(input('Höhe').value,'18');
    assert(fields().filter(el=>el.textContent==='Zellen').length===2,'visible units');
    assert(fields().some(el=>el.tag==='legend'&&el.textContent==='Rastergröße'));
    assert(fields().some(el=>el.tag==='legend'&&el.textContent==='Rasterfarben'));
    const removal=label=>fields().find(el=>el.tag==='label'&&el.children.some(c=>c.textContent===` ${label} ausdrücklich aufheben`)).children[0];
    removal('Breite').checked=true;removal('Breite').onchange();
    assert.equal(input('Breite').disabled,true);assert.equal(input('Breite').value,'');
    assert.equal(input('Höhe').value,'18');assert.equal(input('Höhe').disabled,false);
    assert(run('intent.removeGrid.width'));assert.equal(run('PW.publishedGrid(detail).width'),'18');
    removal('Breite').checked=false;removal('Breite').onchange();
    assert.equal(input('Breite').value,'18');
    removal('Höhe').checked=true;removal('Höhe').onchange();
    assert.equal(input('Höhe').value,'');assert.equal(input('Breite').value,'18');
    removal('Höhe').checked=false;removal('Höhe').onchange();
    assert(fields().some(el=>el.tag==='div'&&el.textContent?.includes('<script>')),'brief is a text node');
    assert(!fields().some(el=>el.tag==='script'),'no active package markup');
    run("intent.findings={first:{accepted:true,treatment:'Eigener Text'}}");
    input('Breite').value='21';input('Breite').oninput();
    assert.equal(run('intent.grid.width'),'21');
    await document.getElementById('refresh').onclick();
    await until(()=>document.getElementById('load').hidden===false);
    assert.equal(input('Breite').value,'21','refresh retains active intent');
    assert.equal(run('intent.findings.first.treatment'),'Eigener Text');
    document.getElementById('load').onclick();
    await until(()=>run('detail!==null'));
    assert.equal(input('Breite').value,'27','explicit snapshot load opens current handoff and resets intent');
    assert.equal(run('intent.findings'),undefined);
    assert(originals().every(el=>!el.open),'reload closes both originals');
    holdDetail=true;
    const stale=run('open(listing.jobs[0].id)');
    await until(()=>releaseDetail!==null);
    await run('open(listing.jobs.find(j=>j.revision==="r02").id)');
    assert.equal(input('Breite').value,'27');
    assert(originals().every(el=>!el.open),'revision switch closes both originals');
    releaseDetail();await stale;
    assert.equal(input('Breite').value,'27','late old detail cannot replace source values');
    run('newDraft()');input('Was soll dein Rätsel zeigen?').value='Local draft';input('Was soll dein Rätsel zeigen?').oninput();
    input('Breite').value='33';input('Breite').oninput();
    const draftId=run('draft.id');
    await run('open(listing.jobs[0].id)');
    assert.equal(input('Breite').value,'18','local draft never overlays published values');
    run(`newDraft(${JSON.stringify(draftId)})`);assert.equal(input('Breite').value,'33');
    descendants(document.getElementById('draftList')).find(el=>el.textContent==='Entwurf verwerfen').onclick();
    await until(()=>run('detail!==null'));
    assert.equal(run('drafts.length'),0);
    assert.equal(input('Breite').value,'27');
    run('detail.facts.published={...detail.facts.published,proposed:{free:"Original survives"},approved:[]}');
    const ambiguous=new Element('section');context.ambiguous=ambiguous;
    run('publishedContext(ambiguous,detail)');
    assert(descendants(ambiguous).filter(el=>el.tag==='details').every(el=>!el.open),'free forms never auto-open');
    assert(descendants(ambiguous).some(el=>el.textContent?.includes('Keine eindeutigen Einzelwerte')));
    const corridor={format:'picross-raster-parameters-v1',constraints:{
      width:{kind:'approximate',target:20,minimum:null,maximum:null},
      height:{kind:'open',target:null,minimum:null,maximum:null},
      foreground_colors:{kind:'exact',target:2,minimum:null,maximum:null}},
      imports:[{width:20,height:25,mode:'color',foreground_colors:2,method:'area',fit:'contain',actual_crop:[0,0,80,100]}],
      derivation:{cell_edits:true,empty_edge_crop:['left','top'],protected_features:['TEST ONLY outline']}};
    run(`detail.facts.published={...detail.facts.published,approved:[${JSON.stringify(corridor)}],proposed:[]}`);
    assert.equal(run('JSON.stringify(PW.publishedGrid(detail))'),'{}','rich corridor never becomes false exact prefill');
    const rich=new Element('section');context.rich=rich;run('publishedContext(rich,detail)');
    const words=descendants(rich).map(el=>el.textContent||'').join('\n');
    assert(words.includes('Breite: ungefähr 20')&&words.includes('Höhe: offen')&&words.includes('Vordergrundfarben: exakt 2'));
    assert(words.includes('TEST ONLY outline'),'protected features stay visible');
    run('technicalDetails(rich,detail)');
    assert(descendants(rich).some(el=>el.tag==='textarea'&&el.value?.includes('actual_crop')),'complete parameter originals survive in copyable technical details');

    // Completion snapshots exercise controller adoption around real detail reads.
    const base=run('JSON.parse(JSON.stringify(listing))');
    const done=base.jobs.find(j=>j.revision==='r01'),remaining=base.jobs.find(j=>j.revision==='r02');
    const completion={confirmed:true,main_commit:'c'.repeat(40),hidden_count:2,
      completed_ids:[done.puzzle_id],note:'Registrierte Rätsel sind ausgeblendet.'};
    const nextId='pz-next-open';
    const next={...base,snapshot:'pw-done-next-id',jobs:[{...remaining,puzzle_id:nextId}],
      motifs:[{...base.motifs[0],puzzle_id:nextId,title:'Nächste offene Produktion',label:nextId,current_job:null}],
      completion};
    await run(`open(${JSON.stringify(done.id)})`);
    await until(()=>cards().length===3&&cards().every(c=>descendants(c).some(el=>el.tag==='img')));
    input('Breite').value='24';input('Breite').oninput();
    const keptView=document.getElementById('view').children,keptGeneration=run('generation');
    const keptImages=cards().map(c=>descendants(c).find(el=>el.tag==='img').src);
    context.completionSnapshot=next;
    await run('checkSources(completionSnapshot)');
    assert.equal(run('active.id'),done.id,'passive completed-list refresh retains the bound source');
    assert.equal(run('generation'),keptGeneration,'passive refresh never disposes active images');
    assert.equal(document.getElementById('view').children,keptView);
    assert.deepEqual(cards().map(c=>descendants(c).find(el=>el.tag==='img').src),keptImages);
    assert.equal(input('Breite').value,'24','unsent input survives filtered refresh');
    assert.equal(document.getElementById('load').hidden,false);
    document.getElementById('load').onclick();
    assert.equal(document.getElementById('jobs').value,nextId);
    assert.equal(run('active'),null);
    assert(fields().some(el=>el.textContent==='Nächste offene Produktion'));
    assert(document.getElementById('sourceStatus').textContent.includes('ist in main registriert'));
    assert(document.getElementById('sourceStatus').textContent.includes('nächste offene Produktion'));

    context.completionSnapshot=base;run('adopt(completionSnapshot)');
    await run(`open(${JSON.stringify(done.id)})`);
    const offline={...base,mode:'remote',remote_confirmed:false,synced_at:'2026-11-14T12:00:00Z',
      sync_error:'Offline test',completion:{confirmed:false,completed_ids:[],note:'Veralteter Listenstand'},
      update:{state:'error',error:'Offline test'}};
    context.completionSnapshot=offline;await run('checkSources(completionSnapshot)');
    assert.equal(document.getElementById('copyOrder').disabled,true,'offline observation blocks a fresh cloud follow-up');
    assert.equal(run('active.id'),done.id);
    assert.equal(document.getElementById('load').hidden,true,'failed refresh retains the existing snapshot');
    assert(document.getElementById('orderStatus').textContent.includes('Remote nicht aktuell bestätigt'));
    assert(document.getElementById('sourceStatus').textContent.includes('letzter Cache'));
    assert(document.getElementById('sourceStatus').textContent.includes('Offline test'));

    run('newDraft()');input('Was soll dein Rätsel zeigen?').value='Keep this local brief';input('Was soll dein Rätsel zeigen?').oninput();
    input('Breite').value='33';input('Breite').oninput();
    const keptDraft=run('draft.id');
    const draftView=document.getElementById('view').children,draftGeneration=run('generation');
    const reference=fields().find(el=>el.type==='file'),bytes=Uint8Array.of(1,2,3);
    reference.files=[{name:'local-reference.png',size:bytes.length,arrayBuffer:async()=>bytes.buffer}];
    await reference.onchange();
    assert.equal(run('draft.reference.sha256'),createHash('sha256').update(bytes).digest('hex'));
    const keptDraftStorage=stored.get('pw-briefs');
    const empty={...base,snapshot:'pw-done-empty',jobs:[],motifs:[],completion:{...completion,completed_ids:[done.puzzle_id]}};
    context.completionSnapshot=empty;await run('checkSources(completionSnapshot)');document.getElementById('load').onclick();
    assert.equal(run('draft.id'),keptDraft,'an active local draft survives explicit adoption');
    assert.equal(input('Was soll dein Rätsel zeigen?').value,'Keep this local brief');
    assert.equal(input('Breite').value,'33');
    assert.equal(document.getElementById('view').children,draftView,'snapshot adoption preserves the entire active draft form');
    assert.equal(run('generation'),draftGeneration);
    assert.equal(run('intent.inputImage'),'local-reference.png','selected local reference stays bound to the untouched form');
    assert.equal(document.getElementById('jobs').children[0].textContent,'Keine offenen Produktionen');
    assert.equal(stored.get('pw-briefs'),keptDraftStorage);

    context.completionSnapshot=base;run('adopt(completionSnapshot)');
    await run(`open(${JSON.stringify(done.id)})`);
    holdDetail=true;releaseDetail=null;
    const lateCompleted=run('open(active.id)');await until(()=>releaseDetail!==null);
    context.completionSnapshot=empty;await run('checkSources(completionSnapshot)');document.getElementById('load').onclick();
    releaseDetail();await lateCompleted;
    assert.equal(run('active'),null);assert.equal(run('detail'),null);assert.equal(run('draft'),null);
    assert.equal(document.getElementById('jobs').value,'');
    assert.equal(document.getElementById('versions').hidden,true);
    assert(fields().some(el=>el.textContent==='Keine offenen Produktionen'));
    assert.equal(cards().length,0,'late completed detail cannot resurrect the removed view');
    assert.equal(stored.get('pw-briefs'),keptDraftStorage,'saved drafts survive completion of all published work');
    assert.equal(run('drafts.length'),1);
    assert(document.getElementById('sourceStatus').textContent.includes('ist in main registriert'));
    run('adopt(completionSnapshot)');
    assert.equal(run('draft'),null,'empty adoption never resurrects a saved text');
    assert.equal(run('drafts.length'),1,'stored text remains explicitly reachable');
    run('dispose()');
    console.log('PW-DONE controller: bound inputs, passive refresh, explicit next/empty adoption, offline status, late detail and separate stored drafts passed.');
    return;
  }
  await until(() => cards().length === 6 && active === 2);
  if (mode === 'abort') {
    // Exact review trigger: five-second server work, two rapid job switches,
    // and real fetch cancellation. Server work must outlive its transport.
    await delay(200);
    const second = run('listing.jobs[1].id');
    await run('open(listing.jobs[1].id)');
    await until(() => fetched.some(path => path.includes('/' + second + '/')));
    await delay(200);
    const started = Date.now();
    await run('open(listing.jobs[0].id)');
    const thirdOpenSeconds = (Date.now() - started) / 1000;
    assert.equal(cards().length, 6, 'third job opens without manual navigation');
    await document.getElementById('refresh').onclick();
    await until(() => document.getElementById('load').hidden === false);
    assert(!document.getElementById('load').hidden, 'metadata refresh remains available');
    await until(() => cards().length === 6 && cards().every(c => descendants(c).some(el => el.tag === 'img')), 30000);
    assert.equal(metadataBusy, 0, 'aborted images never exhaust metadata capacity');
    assert(aborted >= 2, 'fetch really honours AbortSignal');
    assert(imageBusy > 4, 'automatic recovery outlasts the previous four-retry limit');
    assert(peak <= 2, 'bounded client image load');
    assert.equal(hashes.length, 6, 'all six current cards recover automatically');
    assert(new Set(hashes).size === 6 && hashes.every(hash => expectedHashes.includes(hash)), 'exact original PNG bytes');
    assert.equal(run('urls.length'), 6, 'no stale image URLs rendered');
    assert(cards().every(c => descendants(c).find(el => el.textContent === 'Großansicht öffnen').disabled === false));
    console.log(JSON.stringify({probe: 'real transport abort, two job switches, five-second readers',
      third_open_seconds: thirdOpenSeconds, metadata_503: metadataBusy, image_503: imageBusy,
      aborted_fetches: aborted, client_image_peak: peak, exact_current_originals: hashes.length}));
    run('dispose()');
    return;
  }
  oldJob = run('active.id');
  // Real metadata access while slow images occupy the two image slots.
  await document.getElementById('refresh').onclick();
  await until(() => document.getElementById('load').hidden === false);
    assert(!document.getElementById('load').hidden);
  await until(() => cards().length === 6 && cards().every(c => descendants(c).some(el => el.tag === 'img')));
  assert.equal(peak, 2);
  assert.equal(retries, 1);
  assert.equal(hashes.length, 6);
  assert(new Set(hashes).size === 6 && hashes.every(hash => expectedHashes.includes(hash)), 'exact original PNG bytes');
  assert(cards().every(c => descendants(c).find(el => el.textContent === 'Großansicht öffnen').disabled === false));

  // A failed card offers its own retry without reopening the complete job.
  forceFailure = true;
  await run('open(active.id)');
  await until(() => cards().every(c => descendants(c).some(el => el.textContent === 'Bild erneut laden' && el.hidden === false)));
  forceFailure = false;
  const retry = descendants(cards()[0]).find(el => el.textContent === 'Bild erneut laden');
  retry.onclick();
  await until(() => descendants(cards()[0]).some(el => el.tag === 'img'));
  assert(retry.hidden);

  await run('open(active.id)');
  await until(() => active === 2);
  const start = fetched.length;
  await run('open(listing.jobs[1].id)');
  const newJob = run('active.id');
  assert.notEqual(newJob, oldJob);
  await until(() => cards().every(c => descendants(c).some(el => el.tag === 'img')));
  assert(fetched.slice(start).every(path => path.includes('/' + newJob + '/')), 'old queued images never start');
  assert.equal(run('active.revision'), 'r02');

  // Replacing the list with an empty snapshot also invalidates in-flight renders.
  await run('open(active.id)');
  await until(() => active === 2);
  run('adopt({...listing,jobs:[],motifs:[]})');
  await until(() => active === 0);
  await delay(30);
  assert.equal(cards().length, 0);
  assert(descendants(document.getElementById('view')).some(el => el.textContent === 'Keine offenen Produktionen'));
  console.log('PW-A-B01: six exact originals, peak=2, automatic 503 retry, card retry, metadata and stale/empty-view guards passed');
})().catch(error => { console.error(error); process.exitCode = 1; });
