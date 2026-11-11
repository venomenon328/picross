'use strict';
// Execute the actual UI against the real loopback service with a tiny DOM stand-in.
// This checks loading/cancellation, not browser rendering or the separate T02 gate.
const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {createHash} = require('node:crypto');
const vm = require('node:vm');
const [origin, token, expectedHash] = process.argv.slice(2);
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
async function until(test) {
  const end = Date.now() + 10000;
  while (!test()) { assert(Date.now() < end, 'UI loading deadline'); await delay(10); }
}
let active = 0, peak = 0, retries = 0, forceFailure = false, failOnce = true, oldJob;
const fetched = [], hashes = [];
const context = vm.createContext({
  document, location: {hash: '#' + token, pathname: '/'}, history: {replaceState(){}},
  sessionStorage: {setItem(){}, getItem(){}}, localStorage: {setItem(){}, getItem(){}},
  AbortController, setTimeout, clearTimeout,
  URL: {createObjectURL() { return 'blob:test-' + hashes.length; }, revokeObjectURL(){}},
  fetch: async (path, options) => {
    if (!path.includes('/assets/')) return fetch(origin + path, options);
    fetched.push(path);
    if (forceFailure) return new Response('{"error":"temporary failure"}', {status: 400});
    if (failOnce) { failOnce = false; retries++; return new Response('{"error":"busy"}', {status: 503}); }
    active++; peak = Math.max(peak, active);
    try {
      // Deliberately allow old requests to finish, exercising the generation guard
      // even when an I/O implementation does not honour AbortSignal promptly.
      const response = await fetch(origin + path, {...options, signal: undefined});
      const bytes = await response.arrayBuffer();
      if (response.ok) hashes.push(createHash('sha256').update(Buffer.from(bytes)).digest('hex'));
      return new Response(bytes, {status: response.status});
    } finally { active--; }
  }
});
const run = code => vm.runInContext(code, context);
(async () => {
  run(readFileSync(__dirname + '/ui/app.js', 'utf8'));
  await until(() => cards().length === 6 && active === 2);
  oldJob = run('active.id');
  // Real metadata access while slow images occupy the two image slots.
  await document.getElementById('refresh').onclick();
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
