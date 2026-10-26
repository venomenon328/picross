// Cheap tests of the actual bridge. Synthetic FS callbacks are deliberately not
// presented as IndexedDB/browser evidence; C06-C08 provide those real transitions.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(process.argv[2], 'utf8');
const sandbox = {window: {}, queueMicrotask};
vm.runInNewContext(source + '\nthis.Storage = PicrossStorage;', sandbox);
const tick = () => new Promise(resolve => setImmediate(resolve));

function setup(persistent = true) {
  const label = {}, retry = {}, calls = [];
  const store = new sandbox.Storage(label, retry);
  const bridge = {syncfs: (populate, callback) => calls.push({populate, callback})};
  const idb = {reconcile: () => { throw new Error('transaction construction'); }};
  const attached = store.attach(bridge, {is_persistent: () => persistent}, idb);
  return {store, label, retry, calls, bridge, idb, attached};
}
async function confirm(t, error = null) {
  await tick();
  assert.equal(t.calls.length, 1, 'exactly one serial sync is in flight');
  t.calls.shift().callback(error);
  await tick();
}

(async () => {
  let t = setup(false);
  assert.equal(t.attached, false);
  assert.equal(t.store.ready, false);
  assert.equal(t.calls.length, 0);
  console.log('PASS unavailable persistent backend');

  t = setup(); await tick();
  assert.equal(t.store.pending, true);
  assert.equal(t.store.saved, 0);
  t.store.changed(); t.store.changed();
  await confirm(t);
  assert.equal(t.store.pending, true, 'old callback cannot confirm newer changes');
  await confirm(t);
  assert.equal(t.store.pending, false);
  assert.equal(t.store.saved, t.store.generation);
  t.store.viewChanged(); t.store.sync();
  await confirm(t);
  assert.equal(t.store.pending, true, 'view still awaits the real lifecycle flush');
  t.store.changed(); await confirm(t);
  assert.equal(t.store.pending, false);
  console.log('PASS generations and unacknowledged view');

  t = setup(); await confirm(t, new Error('quota'));
  assert.equal(t.store.pending, true);
  assert.ok(t.store.error); assert.equal(t.retry.hidden, false);
  assert.equal(t.store.saved, 0, 'failed write cannot advance durable generation');
  t.retry.onclick(); await confirm(t);
  assert.equal(t.store.error, ''); assert.equal(t.store.pending, false);
  console.log('PASS failed transaction and explicit retry');

  t = setup(); await confirm(t);
  t.store.finished('foreign', 'invalid revision'); await confirm(t);
  t.store.finished('own', ''); await confirm(t);
  assert.equal(t.store.error, 'invalid revision', 'unrelated success cannot clear another slot error');
  assert.equal(t.retry.hidden, false);
  let thrown;
  t.idb.reconcile({}, {}, error => { thrown = error.message; });
  assert.equal(thrown, 'transaction construction');
  console.log('PASS slot-error isolation and thrown IDB construction');

  t = setup(); await confirm(t);
  t.store.changed(); await tick();
  t.store.preferenceChanged(); t.store.preferenceChanged(); await tick();
  assert.equal(t.calls.length, 1, 'preference shares the serialized engine queue');
  await confirm(t, new Error('save quota'));
  await confirm(t, new Error('preference quota'));
  assert.ok(t.store.error); assert.ok(t.store.preferenceError);
  t.store.preferenceRetry(); await tick();
  t.store.preferenceChanged();
  await confirm(t);
  assert.equal(t.store.preferencePending, true, 'newest preference still needs its callback');
  await confirm(t);
  assert.equal(t.store.preferencePending, false);
  assert.equal(t.store.preferenceError, '');
  assert.ok(t.store.error, 'preference success cannot acknowledge failed puzzle saves');
  assert.equal(t.store.pending, true);
  t.retry.onclick(); await confirm(t);
  assert.equal(t.store.pending, false);
  console.log('PASS isolated preference error, latest change and retry');
})().catch(error => { console.error(error); process.exitCode = 1; });
