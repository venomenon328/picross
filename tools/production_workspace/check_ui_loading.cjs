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
  sessionStorage: {setItem(){}, getItem(){}}, localStorage: {setItem(){}, getItem(){}},
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
  if(mode==='removal'){
    await until(()=>run('detail!==null'));
    const target=run('listing.jobs.find(j=>j.source==="remote"&&j.ref==="content/pw/pz-workspace-test")');
    await run(`open(${JSON.stringify(target.id)})`);
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
    assert(run('listing.jobs.some(j=>j.source==="local"&&j.ref==="content/pw/pz-workspace-test")'));
    assert(!run('listing.jobs.some(j=>j.source==="remote"&&j.ref==="content/pw/pz-workspace-test")'));
    console.log('P2 controller: exact branch/revisions, typed confirmation, real HTTP deletion, local remainder and default-off cleanup passed. No browser-rendering claim.');
    return;
  }
  if(mode==='published'){
    await until(()=>run('detail!==null'));
    const first=run('active.id'),second=run('listing.jobs.find(j=>j.revision==="r02").id');
    assert.equal(document.getElementById('jobs').children.length,2);
    const labels=document.getElementById('jobs').children.map(el=>el.textContent);
    assert.equal(new Set(labels).size,2);assert(labels.some(s=>s.includes('r02')));
    assert(!readFileSync(__dirname+'/ui/index.html','utf8').includes('id="jobList"'));
    const fields=()=>descendants(document.getElementById('view'));
    const input=label=>descendants(fields().find(el=>el.tag==='label'&&el.textContent===label)).find(el=>['input','select','textarea'].includes(el.tag));
    const originals=()=>fields().filter(el=>el.tag==='details'&&el.children.some(c=>['Vollständige Parameteroriginale','Veröffentlichtes Motivbriefing'].includes(c.textContent)));
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
    assert.equal(input('Breite').value,'18','explicit snapshot load resets intent');
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
    assert.equal(input('Breite').value,'18');
    run('detail.facts.published={...detail.facts.published,proposed:{free:"Original survives"},approved:[]}');
    const ambiguous=new Element('section');context.ambiguous=ambiguous;
    run('publishedContext(ambiguous,detail)');
    assert(descendants(ambiguous).filter(el=>el.tag==='details').every(el=>!el.open),'free forms never auto-open');
    assert(descendants(ambiguous).some(el=>el.textContent?.includes('Keine eindeutigen Einzelwerte')));
    run('dispose()');
    console.log('P1-T01 UI: exact source values, text briefing, single distinct dropdown, refresh/load, late detail, isolated draft/discard passed');
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
  run('adopt({...listing,jobs:[]})');
  await until(() => active === 0);
  await delay(30);
  assert.equal(cards().length, 0);
  assert(descendants(document.getElementById('view')).some(el => el.textContent === 'Noch keine veröffentlichten Arbeitsstände'));
  console.log('PW-A-B01: six exact originals, peak=2, automatic 503 retry, card retry, metadata and stale/empty-view guards passed');
})().catch(error => { console.error(error); process.exitCode = 1; });
