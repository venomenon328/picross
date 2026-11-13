/* PE v1. Drafts remain in memory; only the session capability survives refresh. */
'use strict';
const $ = id => document.getElementById(id);
let token = location.hash.slice(1) || sessionStorage.getItem('pe-session') || '';
history.replaceState(null, '', '/');
if (/^[0-9a-f]{64}$/.test(token)) sessionStorage.setItem('pe-session', token);
let listing, current, plan, busy = false, dirty = false, imports = {}, blobs = [], generation = 0;
const provenanceKeys = ['author', 'usage_basis', 'source', 'changes'];
const provenanceLabels = ['Urheber', 'Nutzungsbasis / Rechte', 'Tatsächliche Quelle', 'Änderungen / unverändert übernommen'];
for (const kind of ['reveal', 'background', 'raster']) {
  provenanceKeys.forEach((key, i) => {
    const label = document.createElement('label'); label.textContent = provenanceLabels[i];
    const input = document.createElement('input'); input.id = kind + '-' + key; input.maxLength = 4096;
    label.append(input); $(kind + '-provenance').append(label);
  });
}
function message(text, error = false) { $('status').textContent = text; $('status').classList.toggle('error', error); }
function controls(value) {
  busy = value; document.body.classList.toggle('busy', value);
  for (const button of document.querySelectorAll('button')) button.disabled = value && button.id !== 'stop';
  for (const input of $('form').querySelectorAll('input,select,textarea')) input.disabled = value;
}
async function api(route, body, binaryType) {
  const headers = {'X-PE-Session': token};
  const options = {headers, cache: 'no-store'};
  if (body !== undefined) {
    options.method = 'POST'; headers['Content-Type'] = binaryType || 'application/json';
    options.body = binaryType ? body : JSON.stringify(body);
  }
  const response = await fetch('/api/pe/v1/' + route, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'Dienstfehler ' + response.status);
  return data;
}
async function job(route, body, binaryType) {
  const start = await api(route, body, binaryType);
  for (;;) {
    await new Promise(resolve => setTimeout(resolve, 250));
    const state = await api('status');
    $('recovery').hidden = !state.recovery_required;
    const item = state.job;
    if (!item || item.id !== start.job) throw new Error('Die aktive Fachoperation hat gewechselt. Neu laden.');
    message(item.stage + ' · ' + item.elapsed_seconds + ' s');
    if (item.state === 'error') throw new Error(item.error);
    if (item.state === 'done') return item.result;
  }
}
async function perform(fn) {
  if (busy) return;
  controls(true);
  try { await fn(); } catch (error) { message(error.message, true); }
  finally { controls(false); }
}
function mark() {
  dirty = true; plan = null; $('preview').hidden = true;
  $('dirty').textContent = 'Ungespeicherte Änderungen'; $('dirty').classList.add('changed');
}
function clean() {
  dirty = false; plan = null; imports = {}; $('preview').hidden = true;
  $('dirty').textContent = 'Gespeichert'; $('dirty').classList.remove('changed');
}
async function leave() {
  if ((dirty || plan) && !confirm('Ungespeicherte Änderungen und Vorschau verwerfen?')) return false;
  if (dirty || plan) await api('discard', {confirmed: true});
  clean(); return true;
}
function options(select, categories, first) {
  select.replaceChildren();
  if (first !== undefined) select.add(new Option(first, ''));
  for (const cat of categories) select.add(new Option(cat.name, cat.id));
}
async function load() {
  const status = await api('status');
  $('checkout').textContent = status.checkout; $('origin').textContent = status.origin;
  $('recovery').hidden = !status.recovery_required;
  if (status.recovery_required) { message('Recovery erforderlich. Noch keine neue Bearbeitung möglich.', true); return; }
  listing = await api('catalog');
  options($('filter'), listing.categories, 'Alle Kategorien');
  $('migration').hidden = !listing.migration_required;
  current = null; $('form').hidden = true; $('empty').hidden = false;
  renderList(); message('Aktuelle Metadaten geladen. Vollprüfung beim Öffnen.');
}
function renderList() {
  if (!listing) return;
  const query = $('search').value.toLocaleLowerCase('de');
  const cats = new Map(listing.categories.map(cat => [cat.id, cat.name]));
  const rows = listing.entries.filter(row => (!query || (row.name + ' ' + row.id).toLocaleLowerCase('de').includes(query)) && (!$('filter').value || row.category_id === $('filter').value));
  $('count').textContent = rows.length + ' / ' + listing.entries.length;
  $('list').replaceChildren();
  for (const row of rows) {
    const button = document.createElement('button'); button.className = 'entry'; button.dataset.id = row.id;
    button.classList.toggle('active', current?.detail.id === row.id);
    const title = document.createElement('strong'); title.textContent = row.name;
    const category = document.createElement('small'); category.textContent = cats.get(row.category_id);
    const id = document.createElement('small'); id.textContent = row.id;
    button.append(title, category, id); button.onclick = () => perform(async () => { if (await leave()) await select(row.id); });
    $('list').append(button);
  }
}
async function picture(asset) {
  const response = await fetch('/api/pe/v1/image/' + asset, {headers: {'X-PE-Session': token}, cache: 'no-store'});
  if (!response.ok) { const data = await response.json(); throw new Error(data.error); }
  const url = URL.createObjectURL(await response.blob()); blobs.push(url); return url;
}
async function showPictures(kind, assets) {
  const target = $(kind + '-pictures'); target.replaceChildren();
  if (!assets.length) { target.textContent = 'Kein Hintergrund wirksam'; return; }
  for (const asset of assets) {
    const image = document.createElement('img'); image.alt = kind === 'reveal' ? 'Aktuelles Abschlussbild' : 'Wirksamer Hintergrund';
    image.src = await picture(asset); target.append(image);
  }
}
function provenance(kind) { return Object.fromEntries(provenanceKeys.map(key => [key, $(kind + '-' + key).value.trim()])); }
function resetAuthority() {
  for (const kind of ['reveal', 'background', 'raster']) for (const key of provenanceKeys) $(kind + '-' + key).value = '';
  $('actor').value = ''; $('statement').value = ''; $('confirmed').checked = false;
}
async function select(id) {
  const selected = ++generation;
  const result = await job('detail', {id, snapshot: listing.snapshot});
  if (selected !== generation) return;
  for (const url of blobs) URL.revokeObjectURL(url); blobs = [];
  current = result; clean(); resetAuthority();
  $('empty').hidden = true; $('form').hidden = false;
  const row = result.detail.metadata;
  $('puzzle-id').textContent = id; $('title').textContent = row.name; $('name').value = row.name;
  options($('category'), listing.categories); $('category').value = row.category_id;
  $('background').value = result.detail.runtime.background.status;
  $('background-note').textContent = $('background').value === 'legacy' ? 'Bisherige Kategoriezeichnung. Eine erste ausdrückliche Standardzuordnung ist eine eigene Entscheidung.' : '';
  $('raster').value = result.raster.text; $('profile').value = 'line';
  $('reveal-file').value = ''; $('background-file').value = ''; $('reveal-info').textContent = ''; $('background-info').textContent = '';
  $('palette').replaceChildren();
  const empty = document.createElement('span'); empty.className = 'swatch'; empty.textContent = '0 · leer'; $('palette').append(empty);
  for (const color of result.raster.palette) {
    const span = document.createElement('span'); span.className = 'swatch';
    const swatch = document.createElement('i'); swatch.style.backgroundColor = '#' + color.color;
    span.append(swatch, document.createTextNode(color.id + ' · ' + (color.name || color.color || color.hex || ''))); $('palette').append(span);
  }
  await showPictures('reveal', result.pictures.reveal); await showPictures('background', result.pictures.background);
  grid(); renderList(); message('Detail und aktuelle Quellen geprüft. Änderungen erst nach Prüfen und Übernehmen.');
}
function clues(line) {
  const result = []; let prev = 0;
  for (const color of line) { if (color) { if (prev === color) result.at(-1).length++; else result.push({color, length: 1}); } prev = color; }
  return result;
}
function grid() {
  if (!current) return;
  try {
    const allowed = new Set([0, ...current.raster.palette.map(row => row.id)]);
    const lines = $('raster').value.replace(/\r\n/g, '\n').replace(/\n$/, '').split('\n');
    const matrix = lines.map((line, y) => {
      const tokens = line.trim().split(/\s+/);
      if (!line.trim() || y >= 50) throw new Error(`Zeile ${y + 1}, Spalte 1: leere Zeile oder mehr als 50 Zeilen`);
      return tokens.map((token, x) => {
        if (!/^[0-9]+$/.test(token) || !allowed.has(Number(token)) || x >= 50) throw new Error(`Zeile ${y + 1}, Spalte ${x + 1}: ungültige Palette-ID oder mehr als 50 Zellen`);
        return Number(token);
      });
    });
    matrix.forEach((row, y) => { if (row.length !== matrix[0].length) throw new Error(`Zeile ${y + 1}, Spalte ${Math.min(row.length, matrix[0].length) + 1}: abweichende Zeilenbreite`); });
    $('dimensions').textContent = '· ' + matrix[0].length + ' × ' + matrix.length;
    const rows = matrix.map(clues), cols = matrix[0].map((_, x) => clues(matrix.map(row => row[x])));
    $('clues').textContent = JSON.stringify({rows, columns: cols}, null, 2);
    $('grid-status').textContent = 'Textstruktur gültig. Deduktion und Rating erfolgen erst beim Prüfen.';
  } catch (error) { $('grid-status').textContent = error.message; $('clues').textContent = ''; }
}
async function upload(kind, file) {
  if (!current) throw new Error('Zuerst ein Rätsel auswählen.');
  const suffix = file.name.split('.').at(-1).toLowerCase();
  if (!['png', 'svg'].includes(suffix) || (kind === 'background' && suffix !== 'png')) throw new Error('PNG / begrenztes SVG erwartet; Hintergrund nur PNG.');
  if (!file.size || file.size > 32 * 1024 * 1024) throw new Error('Datei muss 1 Byte bis 32 MiB groß sein.');
  const result = await job('upload/' + kind + '/' + suffix, file, suffix === 'png' ? 'image/png' : 'image/svg+xml');
  imports[kind] = result.upload; mark();
  await showPictures(kind, [result.asset]);
  $(kind + '-info').textContent = file.name + ' · ' + result.bytes + ' Bytes · geprüft, noch nicht übernommen';
  if (kind === 'background') $('background').value = 'selected';
  $('authority').open = true; message('Originaldatei geprüft. Herkunft und manuelle Entscheidung ergänzen.');
}
function request() {
  const old = current.detail.metadata;
  const metadata = {};
  if ($('name').value !== old.name) metadata.name = $('name').value;
  if ($('category').value !== old.category_id) metadata.category_id = $('category').value;
  const bg = $('background').value;
  const backgroundChanged = bg !== current.detail.runtime.background.status || !!imports.background;
  if (backgroundChanged && bg === 'legacy') throw new Error('Für Rückkehr die ausdrückliche Standardpräferenz wählen.');
  const rasterChanged = $('raster').value !== current.raster.text;
  const imageChanged = !!imports.reveal || backgroundChanged;
  const authority = rasterChanged || imageChanged ? {actor: $('actor').value.trim(), statement: $('statement').value.trim(), confirmed: $('confirmed').checked, provenance: provenance('raster')} : null;
  if (authority && (!authority.actor || !authority.statement || !authority.confirmed)) { $('authority').open = true; throw new Error('Akteur, Entscheidung und ausdrückliche Bestätigung sind erforderlich.'); }
  return {snapshot: current.snapshot, id: current.detail.id, metadata: Object.keys(metadata).length ? metadata : null,
    text: rasterChanged ? $('raster').value : null, profile: $('profile').value,
    reveal: imports.reveal ? {upload: imports.reveal, provenance: provenance('reveal')} : null,
    background: backgroundChanged ? {status: bg, upload: bg === 'selected' ? imports.background || null : null, provenance: bg === 'selected' ? provenance('background') : null} : null, authority};
}
async function backgroundPreview() {
  if (!current) return;
  const status = $('background').value;
  if (status === 'standard' || status === 'legacy') {
    const result = await api('standard/' + $('category').value);
    await showPictures('background', result.assets);
  } else if (status === 'none') await showPictures('background', []);
  else if (!imports.background && current.detail.runtime.background.status === 'selected') await showPictures('background', current.pictures.background);
  else if (!imports.background) { $('background-pictures').replaceChildren(); $('background-pictures').textContent = 'Vorbereitete Datei auswählen'; }
  $('background-note').textContent = 'Vorschau der gewählten Einstellung; noch nicht übernommen.';
}
function preview(result) {
  plan = result; $('preview').hidden = false;
  $('plan-summary').replaceChildren();
  const p = document.createElement('p'); p.textContent = (result.id || 'Kategorien / Runtimeprojektion') + ' · ' + result.files.length + ' geänderte Dateien';
  $('plan-summary').append(p);
  const table = document.createElement('table');
  const header = document.createElement('tr');
  for (const text of ['Feld', 'Vorher', 'Nachher']) { const cell = document.createElement('th'); cell.textContent = text; header.append(cell); }
  table.append(header);
  const row = (label, before, after) => { const tr = document.createElement('tr'); for (const text of [label, before ?? '—', after ?? '—']) { const td = document.createElement('td'); td.textContent = String(text); tr.append(td); } table.append(tr); };
  const category = id => listing.categories.find(item => item.id === id)?.name || id;
  const metadata = (before, after) => {
    if (before?.name !== after?.name) row('Name', before?.name, after?.name);
    if (before?.category_id !== after?.category_id) row('Kategorie', category(before?.category_id), category(after?.category_id));
  };
  const background = value => ({legacy: 'Standard (ohne eigene Zuordnung)', standard: 'Standard der Kategorie', selected: 'Eigenes Bild', none: 'Kein Hintergrund'}[value]);
  if (result.kind === 'metadata') {
    for (const change of result.after) {
      if (change.kind === 'category') row('Kategorie ' + change.id, change.before?.name, change.after?.name);
      else { row('Rätsel', change.before?.name || change.id, change.after?.name || change.id); metadata(change.before, change.after); }
    }
  } else if (result.kind === 'migration') {
    row('Runtimeprojektion', result.before.format, result.after.format);
    const text = document.createElement('p'); text.textContent = 'Ausschließlich Runtimeprojektion; keine Bild- oder Rasteränderung.'; $('plan-summary').append(text);
  } else {
    metadata(result.before.metadata, result.after.metadata);
    if (JSON.stringify(result.before.reveal) !== JSON.stringify(result.after.reveal)) row('Abschlussbild', 'Bisheriges Bild', 'Geprüfter Import / aktuelle Bindung');
    if (JSON.stringify(result.before.background) !== JSON.stringify(result.after.background)) row('Hintergrund', background(result.before.runtime.background.status), background(result.after.runtime.background.status));
    if (result.kind === 'raster') {
      const dimensions = value => value.width + ' × ' + value.height + ' · Revision ' + value.revision;
      row('Raster', dimensions(result.before.definition), dimensions(result.after.definition));
      const rating = result.quality?.checked?.rating?.result;
      const text = document.createElement('p');
      text.textContent = result.logic_changed ? 'Deduktionsnachweis vollständig geprüft. Schwierigkeit: ' + (['', 'Sehr leicht', 'Leicht', 'Mittel', 'Schwer', 'Sehr schwer'][rating?.level] || 'geprüft') + '.' : 'Gleiche Rasterlogik: keine neue Revision und kein Spielstandneustart.';
      $('plan-summary').append(text);
    }
  }
  $('plan-summary').append(table);
  $('plan-files').textContent = result.files.join('\n') || 'No-op: keine Dateiänderung.';
  $('revision-warning').hidden = !result.logic_changed;
  $('preview').scrollIntoView({behavior: 'smooth', block: 'start'});
  message('Echter Plan erfolgreich geprüft. Übernehmen ist ein eigener Schritt (zehn Minuten gültig).');
}
$('search').oninput = renderList; $('filter').onchange = renderList;
$('form').addEventListener('input', event => { mark(); if (event.target.id === 'raster') grid(); });
$('form').addEventListener('change', event => { mark(); if (event.target.id === 'category' || event.target.id === 'background') perform(backgroundPreview); });
$('form').onsubmit = event => { event.preventDefault(); perform(async () => preview(await job('plan', request()))); };
for (const kind of ['reveal', 'background']) {
  $(kind + '-file').onchange = event => { const file = event.target.files[0]; if (file) perform(() => upload(kind, file)); };
  const drop = document.querySelector('[data-kind="' + kind + '"]');
  drop.ondragover = event => { event.preventDefault(); drop.classList.add('over'); };
  drop.ondragleave = () => drop.classList.remove('over');
  drop.ondrop = event => { event.preventDefault(); drop.classList.remove('over'); const file = event.dataTransfer.files[0]; if (file) perform(() => upload(kind, file)); };
}
$('discard').onclick = () => perform(async () => { const id = current.detail.id; if (await leave()) { listing = await api('catalog'); await select(id); } });
$('cancel-plan').onclick = () => perform(async () => { const id = current?.detail.id; if (await leave()) { listing = await api('catalog'); if (id) await select(id); else await load(); } });
$('apply').onclick = () => perform(async () => {
  if (!plan) throw new Error('Plan fehlt.');
  const id = plan.id;
  const result = await job('apply', {plan: plan.plan, id});
  clean(); await api('discard', {confirmed: true}); await load(); if (id) await select(id);
  message('Writer bestätigt: ' + result.status + '. Aktuellen Bestand neu gelesen. Git / Build / Veröffentlichung bleiben extern.');
});
$('reload').onclick = () => perform(async () => { if (await leave()) await load(); });
$('migrate').onclick = () => perform(async () => { if (await leave()) { await load(); preview(await job('migration', {snapshot: listing.snapshot})); } });
$('recover').onclick = () => perform(async () => { if (confirm('Bestehendes Journal prüfen und ausschließlich den gebundenen gültigen Altstand wiederherstellen?')) { await job('recover', {confirmed: true}); clean(); await load(); } });
$('stop').onclick = async () => {
  if (!confirm((dirty ? 'Ungespeicherte Änderungen gehen verloren. ' : '') + 'Editor geordnet beenden? Bereits laufende Fachoperationen werden abgeschlossen.')) return;
  try { await api('stop', {confirmed: true}); message('Editor beendet neue Arbeit und wartet auf laufende Fachoperationen.'); } catch (error) { message(error.message, true); }
};
$('categories').onclick = () => perform(async () => {
  if (!await leave()) return;
  await load();
  options($('category-target'), listing.categories); options($('category-reassign'), listing.categories, 'Keine Neuzuordnung (nur leere Kategorie)');
  $('category-confirmed').checked = false; categoryUsage(); $('category-dialog').showModal();
});
function categoryUsage() {
  const id = $('category-target').value;
  $('category-usage').textContent = (listing?.entries.filter(row => row.category_id === id).length || 0) + ' Rätsel in dieser Kategorie. Eine Löschung ordnet alle gemeinsam neu zu.';
}
$('category-target').onchange = categoryUsage;
$('category-close').onclick = () => $('category-dialog').close();
$('category-check').onclick = () => perform(async () => {
  const op = $('category-op').value, operation = {op};
  if (op !== 'category_create') operation.id = $('category-target').value;
  if (op !== 'category_delete') operation.name = $('category-name').value;
  else {
    if (!$('category-confirmed').checked) throw new Error('Löschung / vollständige Neuzuordnung ausdrücklich bestätigen.');
    if ($('category-reassign').value) operation.reassign_to = $('category-reassign').value;
  }
  const result = await job('plan', {snapshot: listing.snapshot, id: null, metadata: [operation], text: null, profile: null, reveal: null, background: null, authority: null});
  $('category-dialog').close(); preview(result);
});
window.addEventListener('beforeunload', event => { if (dirty || plan) { event.preventDefault(); event.returnValue = ''; } });
window.addEventListener('hashchange', () => {
  const fresh = location.hash.slice(1);
  history.replaceState(null, '', '/');
  if (!/^[0-9a-f]{64}$/.test(fresh) || fresh === token) return;
  if ((dirty || plan) && !confirm('Neue Editorsitzung öffnen und ungespeicherte Änderungen verwerfen?')) return;
  token = fresh; sessionStorage.setItem('pe-session', token); clean(); perform(load);
});
perform(load);
