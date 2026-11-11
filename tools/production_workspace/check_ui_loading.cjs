'use strict';
// Execute the actual UI against the real loopback service with a tiny DOM stand-in.
// This checks loading/cancellation, not browser rendering or the separate T02 gate.
const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {createHash} = require('node:crypto');
const vm = require('node:vm');
const [origin, token, expectedHash, mode = 'late'] = process.argv.slice(2);
class Element {
  constructor(tag) { this.tag = tag; this.children = []; this.dataset = {}; this.classList = {toggle(){}}; }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.children = children; }
  setAttribute() {}
  close() {}
  showModal() {}
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
const fetched = [], hashes = [];
const context = vm.createContext({
  document, location: {hash: '#' + token, pathname: '/'}, history: {replaceState(){}},
  sessionStorage: {setItem(){}, getItem(){}}, localStorage: {setItem(){}, getItem(){}},
  AbortController, setTimeout, clearTimeout,
  URL: {createObjectURL() { return 'blob:test-' + hashes.length; }, revokeObjectURL(){}},
  fetch: async (path, options) => {
    if (!path.includes('/assets/')) {
      const response = await fetch(origin + path, options);
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
  run(readFileSync(__dirname + '/ui/app.js', 'utf8'));
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
    assert(hashes.every(hash => hash === expectedHash), 'exact original PNG bytes');
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
  assert(hashes.every(hash => hash === expectedHash), 'exact original PNG bytes');
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
