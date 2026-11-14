'use strict';
// Execute the actual UI against the real loopback service with a tiny DOM stand-in.
// This checks loading/cancellation, not browser rendering or the separate T02 gate.
const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {createHash} = require('node:crypto');
const vm = require('node:vm');
const [origin, token, expectedHashesJson, mode = 'late'] = process.argv.slice(2);
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
}
const elements = new Map();
const stored = new Map();
const document = {
  documentElement: new Element('html'),
  getElementById(id) { if (!elements.has(id)) elements.set(id, new Element(id)); return elements.get(id); },
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
  AbortController, setTimeout, clearTimeout,
  crypto: require('node:crypto').webcrypto,
  URL: {createObjectURL() { return 'blob:test-' + hashes.length; }, revokeObjectURL(){}},
  fetch: async (path, options) => {
    if(path.startsWith('/api/removal/'))options={...options,headers:{...options.headers,Origin:origin}};
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
  await until(()=>run('listing!==null'));
  // Pointerless synthetic legacy inputs now require a deliberate version choice.
  if(mode==='published')await run('open(listing.jobs.find(j=>j.revision==="r01").id)');
  else if(run('detail===null'))await run('open(listing.jobs[0].id)');
  if(mode==='removal'){
    await until(()=>run('detail!==null'));
    const target=run('listing.jobs.find(j=>j.source==="remote"&&j.ref==="content/pw/pz-workspace-test")');
    assert.equal(document.getElementById('jobs').children.length,1,'one motif despite source/ref/revision duplicates');
    assert.equal(run('currentMotif().versions.length'),2);
    assert.equal(run('currentMotif().versions[0].source_label'),'Lokal und Remote');
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
    assert(nodes().some(e=>e.textContent?.includes('Nachweislich auf main abgeschlossene Lieferungen erscheinen nicht in der aktiven Auswahl')));
    assert(run('listing.jobs.some(j=>j.source==="local"&&j.ref==="content/pw/pz-workspace-test")'));
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
    input('Breite').value='21';input('Breite').oninput();
    assert.equal(run('intent.grid.width'),'21');
    await document.getElementById('refresh').onclick();
    await until(()=>document.getElementById('load').hidden===false);
    assert.equal(input('Breite').value,'21','refresh retains active intent');
    document.getElementById('load').onclick();
    await until(()=>run('detail!==null'));
    assert.equal(input('Breite').value,'27','explicit snapshot load opens current handoff and resets intent');
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

    // PW2-C controller cases use synthetic completion metadata around the real
    // published details/images. These do not prove the backend's main decision.
    const base=run('JSON.parse(JSON.stringify(listing))');
    const done=base.jobs.find(j=>j.revision==='r01'),remaining=base.jobs.find(j=>j.revision==='r02');
    const completion={confirmed:true,main_commit:'c'.repeat(40),hidden_count:1,completed_ids:[],
      hidden_jobs:[done],note:'Bestätigte Mainintegration: 1 abgeschlossene Lieferung ausgeblendet.'};
    const sameId={...base,snapshot:'pw2-c-same-id',completion,jobs:[remaining],motifs:[{
      ...base.motifs[0],current_job:remaining.id,versions:base.motifs[0].versions
        .filter(v=>v.sources.includes(remaining.id)).map(v=>({...v,sources:[remaining.id]}))}]};
    await run(`open(${JSON.stringify(done.id)})`);
    context.completionSnapshot={...base,snapshot:'pw2-c-retained-copy',
      motifs:[{...base.motifs[0],current_job:done.id}],
      completion:{...completion,hidden_jobs:[{...done,source:'remote',ref:'content/pw/'+done.puzzle_id}]}};
    await run('checkSources(completionSnapshot)');document.getElementById('load').onclick();
    await until(()=>run('detail!==null&&active.revision==="r01"'));
    assert(!document.getElementById('sourceStatus').textContent.includes('Die bisherige Produktion'),
      'a hidden source copy does not imply removal while the same delivery remains visible');
    context.completionSnapshot={...base,snapshot:'pw2-c-unbound-old-source',jobs:[],motifs:[],
      completion:{...completion,completed_ids:[done.puzzle_id],hidden_jobs:[remaining]}};
    await run('checkSources(completionSnapshot)');document.getElementById('load').onclick();
    assert(!document.getElementById('sourceStatus').textContent.includes('Die bisherige Produktion'),
      'a completed ID alone never proves the vanished active historical delivery');
    context.completionSnapshot=base;run('adopt(completionSnapshot)');
    await run(`open(${JSON.stringify(done.id)})`);
    await until(()=>cards().length===3&&cards().every(c=>descendants(c).some(el=>el.tag==='img')));
    input('Breite').value='24';input('Breite').oninput();
    const keptView=document.getElementById('view').children,keptGeneration=run('generation');
    const keptImages=cards().map(c=>descendants(c).find(el=>el.tag==='img').src);
    context.completionSnapshot=sameId;
    await run('checkSources(completionSnapshot)');
    assert.equal(run('active.id'),done.id,'passive completed-list refresh retains the bound source');
    assert.equal(run('generation'),keptGeneration,'passive refresh never disposes active images');
    assert.equal(document.getElementById('view').children,keptView);
    assert.deepEqual(cards().map(c=>descendants(c).find(el=>el.tag==='img').src),keptImages);
    assert.equal(input('Breite').value,'24','unsent input survives filtered refresh');
    assert.equal(document.getElementById('load').hidden,false);
    document.getElementById('load').onclick();
    await until(()=>run('detail!==null&&active.revision==="r02"'));
    assert.equal(run('active.id'),remaining.id,'explicit adoption selects the remaining same-ID work');
    assert.equal(input('Breite').value,'27','only explicit adoption replaces source inputs');
    assert(document.getElementById('sourceStatus').textContent.includes('nach bestätigter Mainintegration'));
    assert(document.getElementById('sourceStatus').textContent.includes('offene Arbeit zur gleichen ID'));
    assert.equal(document.getElementById('jobs').children.length,1);

    // A fresh remote alone is no main confirmation; show the dedicated note.
    const unconfirmed={...base,snapshot:'pw2-c-unconfirmed-main',mode:'remote',remote_confirmed:true,sync_error:null,
      completion:{confirmed:false,main_commit:null,hidden_count:0,completed_ids:[],hidden_jobs:[],
        note:'Main nicht aktuell bestätigt; mögliche Abschlüsse bleiben sichtbar.'}};
    context.completionSnapshot=unconfirmed;await run('checkSources(completionSnapshot)');
    assert.equal(run('active.id'),remaining.id);
    assert(document.getElementById('sourceStatus').textContent.includes(unconfirmed.completion.note));
    document.getElementById('load').onclick();await until(()=>run('detail!==null'));
    assert.equal(run('listing.jobs.length'),base.jobs.length,'unconfirmed candidates remain available');
    assert(!document.getElementById('sourceStatus').textContent.includes('Die bisherige Produktion'));

    // A remaining motif may need a deliberate version choice; select that motif
    // instead of keeping the removed one or inventing an unambiguous source.
    await run(`open(${JSON.stringify(done.id)})`);
    const nextId='pz-next-open';
    context.completionSnapshot={...sameId,snapshot:'pw2-c-next-id',jobs:[{...remaining,puzzle_id:nextId}],
      motifs:[{...sameId.motifs[0],puzzle_id:nextId,title:'Nächste offene Produktion',label:nextId,current_job:null}],
      completion:{...completion,completed_ids:[done.puzzle_id]}};
    await run('checkSources(completionSnapshot)');document.getElementById('load').onclick();
    assert.equal(document.getElementById('jobs').value,nextId);
    assert.equal(run('active'),null);
    assert(fields().some(el=>el.textContent==='Nächste offene Produktion'));
    assert(document.getElementById('sourceStatus').textContent.includes('nächste offene Produktion'));

    run('newDraft()');input('Was soll dein Rätsel zeigen?').value='Keep this local brief';input('Was soll dein Rätsel zeigen?').oninput();
    input('Breite').value='33';input('Breite').oninput();
    const keptDraft=run('draft.id'),keptDraftStorage=stored.get('pw-briefs');
    const draftView=document.getElementById('view').children,draftGeneration=run('generation');
    const reference=fields().find(el=>el.type==='file');reference.files=[{name:'local-reference.png'}];reference.onchange();
    const empty={...base,snapshot:'pw2-c-empty',jobs:[],motifs:[],completion:{...completion,completed_ids:[done.puzzle_id]}};
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
    assert(document.getElementById('sourceStatus').textContent.includes('nach bestätigter Mainintegration'));
    run('dispose()');
    console.log('P1/PW2-C controller: source values, filtered passive refresh, explicit same-ID/next/empty adoption, unconfirmed main, late detail and separate stored drafts passed. Synthetic completion snapshots; no browser-rendering or backend-completion claim.');
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
