'use strict';
const $=id=>document.getElementById(id);
let token=location.hash.slice(1);
try{if(token)sessionStorage.setItem('pw-session',token);else token=sessionStorage.getItem('pw-session')||'';}catch{}
history.replaceState(null,'',location.pathname);
let listing=null,pending=null,generation=0,controller=null,urls=[],active=null;
let detail=null,intent={},draft=null,drafts=[];
try{drafts=JSON.parse(localStorage.getItem('pw-briefs')||'[]');if(!Array.isArray(drafts))drafts=[];drafts=drafts.filter(d=>d&&typeof d.id==='string'&&typeof d.brief==='string').slice(-20);}catch{}
function saveDrafts(){try{localStorage.setItem('pw-briefs',JSON.stringify(drafts));}catch{}}
function options(){return {workroot:$('workroot').value,cleanup:$('cleanup').checked,merge:$('merge').checked};}
for(const key of ['workroot','cleanup','merge']){
 try{const saved=JSON.parse(localStorage.getItem('pw-options')||'{}');if(key==='workroot')$(key).value=saved[key]||'';else $(key).checked=saved[key]===true;}catch{}
 $(key).onchange=()=>{try{localStorage.setItem('pw-options',JSON.stringify(options()));}catch{}updatePrompt();};
}
function updatePrompt(){
 const box=$('orderText'),button=$('copyOrder');if(!box||!button)return;
 try{box.value=PW.prompt(detail,intent,options());button.disabled=false;$('orderStatus').textContent='In ChatGPT oder Codex senden. Kopieren bestätigt noch keine Entscheidung.';}
 catch(exc){box.value='';button.disabled=true;$('orderStatus').textContent=exc.message;}
}
function field(parent,label,key,placeholder){
 const wrap=node('label',label),input=node('textarea');input.rows=2;input.maxLength=4096;input.placeholder=placeholder||'';input.value=intent[key]||'';
 input.oninput=()=>{intent[key]=input.value;if(draft&&key==='brief'){draft.brief=input.value;saveDrafts();}updatePrompt();};wrap.append(input);parent.append(wrap);return input;
}
function workflow(view,value){
 detail=value;const n=PW.step(value),section=node('section',undefined,'nextAction');
 const progress=node('ol',undefined,'steps');PW.steps.forEach((label,i)=>{const li=node('li',`${i+1} ${label}`);if(i+1===n)li.setAttribute('aria-current','step');progress.append(li);});view.append(progress);
 section.append(node('h3',value?.facts.next_step||'1 · Dein Motiv beschreiben'));
 if(!value){
  field(section,'Was soll dein Rätsel zeigen?','brief','Motiv, wichtige Merkmale und gewünschte Stimmung');
  const label=node('label','Optional: eigenes Eingangsbild'),input=node('input');input.type='file';input.accept='image/png,image/jpeg';
  input.onchange=()=>{intent.inputImage=input.files[0]?.name||'';updatePrompt();};label.append(input);section.append(label,node('p','Die Datei anschließend selbst an den Chat anhängen. Sie wird hier nicht hochgeladen.','hint'));
 }
 if(value){
  const label=node('label','Nächste Aktion'),select=node('select');
  for(const [id,text] of [['continue','Fortsetzen / Entscheidung senden'],['rework','Gezielt korrigieren'],['resume','Arbeit wieder aufnehmen'],...(value.facts.state==='registered'?[['background_change','Separater Hintergrundfolgeauftrag']]:[])]){const opt=node('option',text);opt.value=id;select.append(opt);}
  select.onchange=()=>{intent.action=select.value;correction.hidden=!['rework','background_change'].includes(select.value);updatePrompt();};label.append(select);section.append(label);
  const correction=node('div');correction.hidden=true;field(correction,'Was soll geändert werden?','feedback');section.append(correction);
 }
 if(n===2||n===3){const d=node('details');d.append(node('summary','Optional: Größe, Modus und Farbzahl'));field(d,'Dein Parameterwunsch','parameters','Beispiel: etwa 30 × 25, farbig, KI empfiehlt die Farbzahl');section.append(d);}
 if(n===4){const d=node('details');d.append(node('summary','Optional: gewünschter Kontext'));field(d,'Kontextwunsch','context');section.append(d);}
 if(value?.facts.state==='background_review'){
  const none=node('button','Bewusst keinen Hintergrund wählen');none.onclick=()=>choose('none','background',none);section.append(none);
 }
 if(n===5)section.append(node('p',value.facts.background_choice==='none'?'Bestätigt: bewusst kein Hintergrund.':value.facts.background_choice?'Bestätigte Hintergrundwahl: '+value.facts.background_choice:'Hintergrundstatus: '+value.facts.background_status));
 const selected=node('p','Noch keine neue Auswahl gesendet.','hint');selected.id='selectionStatus';section.append(selected);
 const copy=node('button','Auftrag kopieren','primary');copy.id='copyOrder';
 copy.onclick=async()=>{try{await navigator.clipboard.writeText($('orderText').value);$('orderStatus').textContent='Kopiert. Sende den Auftrag jetzt im Chat; der Produktionsstand bleibt bis zu neuen Gitdaten unverändert.';}catch{$('orderText').focus();$('orderText').select();$('orderStatus').textContent='Bitte den markierten Auftrag manuell kopieren.';}};
 const status=node('p',undefined,'hint');status.id='orderStatus';const d=node('details');d.append(node('summary','Auftrag ansehen'));const text=node('textarea');text.id='orderText';text.rows=12;text.readOnly=true;d.append(text);section.append(copy,status,d);view.append(section);updatePrompt();
}
function choose(id,kind,button){const label=id==='none'?'kein Hintergrund':detail?.offers.find(o=>o.id===id&&o.kind===kind)?.label||id;intent.selection=id;intent.kind=kind;document.querySelectorAll('[data-choice]').forEach(b=>b.setAttribute('aria-pressed','false'));button.dataset.choice=id;button.setAttribute('aria-pressed','true');$('selectionStatus').textContent=`Vorgemerkt: ${label}. Erst der gesendete Auftrag erklärt deine Wahl.`;updatePrompt();}
function newDraft(id){dispose();active=null;detail=null;draft=drafts.find(d=>d.id===id)||{id:crypto.randomUUID(),brief:''};if(!drafts.includes(draft)){drafts.push(draft);drafts=drafts.slice(-20);saveDrafts();}intent={brief:draft.brief};$('view').replaceChildren(node('h2','Neues Motiv'));workflow($('view'),null);renderDrafts();}
function renderDrafts(){let list=$('draftList');if(!list){list=node('div');list.id='draftList';$('jobList').before(list);}list.replaceChildren();for(const d of drafts){const b=node('button',(d.brief||'Neues Motiv').slice(0,42),'job');b.onclick=()=>newDraft(d.id);list.append(b);}if(draft){const remove=node('button','Diesen lokalen Entwurf verwerfen');remove.onclick=()=>{drafts=drafts.filter(d=>d.id!==draft.id);draft=null;saveDrafts();renderDrafts();if(listing?.jobs.length)open(listing.jobs[0].id);else $('view').replaceChildren(node('p','Über „Neues Motiv“ beginnen.'));};list.append(remove);}}
$('newJob').onclick=()=>newDraft();renderDrafts();
const roleNames={reveal:'Abschlussbilder',motif:'Motivvorlage',raster:'Rasterangebote',raster_draft:'Sichtungsentwürfe',background:'Hintergrundangebote'};
function node(tag,text,cls){const el=document.createElement(tag);if(text!==undefined)el.textContent=text;if(cls)el.className=cls;return el;}
function error(text){$('error').textContent=text;$('error').hidden=!text;}
function pause(ms,signal){return new Promise((resolve,reject)=>{
 const abort=()=>{clearTimeout(timer);reject(signal.reason);};
 const timer=setTimeout(()=>{signal?.removeEventListener('abort',abort);resolve();},ms);
 if(signal?.aborted)abort();else signal?.addEventListener('abort',abort,{once:true});
});}
async function request(path,options={},waitForImageSlot=false){
 for(let attempt=0;;attempt++){
  options.signal?.throwIfAborted();
  const response=await fetch(path,{...options,headers:{'X-Workspace-Session':token},cache:'no-store'});
  if(response.ok)return response;
  let body;try{body=await response.json();}catch{body={error:'Lokaler Dienst nicht erreichbar. Starter erneut öffnen.'};}
  if(response.status!==503||(!waitForImageSlot&&attempt===4))throw new Error(body.error);
  // Image slots can remain occupied after aborting their HTTP transports.
  // Keep the current cards pending until the server finishes, or the user leaves.
  await pause(250*2**Math.min(attempt,3),options.signal);
 }
}
// Bound client requests as well as the server's independently held image slots.
let imageLoads=0;
const imageQueue=[];
function drainImages(){
 while(imageLoads<2&&imageQueue.length){
  const task=imageQueue.shift();
  if(task.signal.aborted){task.reject(task.signal.reason);continue;}
  imageLoads++;
  request(task.path,{signal:task.signal},true).then(r=>r.blob()).then(task.resolve,task.reject)
   .finally(()=>{imageLoads--;drainImages();});
 }
}
function imageRequest(path,signal){return new Promise((resolve,reject)=>{imageQueue.push({path,signal,resolve,reject});drainImages();});}
function dispose(){generation++;controller?.abort();controller=new AbortController();for(const url of urls)URL.revokeObjectURL(url);urls=[];$('large').close();}
function sourceStatus(value){return (value.mode==='local'?'Nur lokale Gitstände · Remote-Sicherung nicht bestätigt':value.sync_error||('Remote zuletzt geladen: '+(value.synced_at?new Date(value.synced_at).toLocaleString('de-DE'):'noch nicht synchronisiert')));}
function adopt(value){const keepDraft=draft?.id;dispose();listing=value;pending=null;$('load').hidden=true;$('sourceStatus').textContent=sourceStatus(value);error(value.errors.join('\n'));$('jobs').replaceChildren();$('jobList').replaceChildren();if(!value.jobs.length){$('jobs').append(node('option','Keine veröffentlichten Jobs'));if(keepDraft){newDraft(keepDraft);return;}$('view').replaceChildren(node('h2','Noch keine veröffentlichten Arbeitsstände'),node('p','Der Produktionsakteur muss Record, Originale und die geprüfte workspace.json gemeinsam in Git sichern. Bestehende WIP werden nicht konvertiert.'));return;}
 for(const [jobIndex,job] of value.jobs.entries()){const label=`${job.title} · Stand ${jobIndex+1} (${job.source==='local'?'lokal':'Remote'})`;const opt=node('option',label);opt.value=job.id;$('jobs').append(opt);const button=node('button',job.title,'job');button.dataset.job=job.id;button.append(node('small',`Stand ${jobIndex+1}${job.conflict?' · Quellenkonflikt':''}`));button.onclick=()=>{$('jobs').value=job.id;open(job.id);};$('jobList').append(button);}
 if(keepDraft){newDraft(keepDraft);return;}const retained=value.jobs.find(j=>active&&j.puzzle_id===active.puzzle_id&&j.revision===active.revision&&j.source===active.source);$('jobs').value=(retained||value.jobs[0]).id;open($('jobs').value);}
async function open(id){dispose();draft=null;detail=null;intent={};renderDrafts();const current=generation,signal=controller.signal;active=listing.jobs.find(j=>j.id===id);for(const el of $('jobList').children)el.setAttribute('aria-current',String(el.dataset.job===id));$('view').replaceChildren(node('p','Originalbindungen und Bilder werden geprüft …'));try{const value=await(await request('/api/jobs/'+id,{signal})).json();if(current!==generation)return;const view=$('view');view.replaceChildren(node('h2',value.title));view.append(node('span',({brief_ready:'Briefing bereit',reveal_review:'Abschlussbilder zur Wahl',motif_review:'Motivvorlage zur Freigabe',motif_approved:'Rasterproduktion beauftragt',raster_review:'Rasterprüfung offen',raster_ready:'Geprüfte Raster zur Wahl',background_review:'Kontextzeichnungen zur Wahl',content_ready:'Bereit zur Endabnahme',editorially_approved:'Endabnahme liegt vor',registered:'Lokal registriert'})[value.facts.state]||value.facts.state,'badge'));if(value.facts.test_only)view.append(node('span','Technische Testdaten','badge'));view.append(node('p',value.publication,'hint'));workflow(view,value);if(value.facts.blockers.length){const d=node('details');d.append(node('summary','Überlieferte offene Produktionspunkte'));const ul=node('ul');for(const b of value.facts.blockers)ul.append(node('li',b));d.append(ul);view.append(d);}
 const phase=value.facts.state;const groups=phase==='background_review'?[['background']]:[['reveal','motif'],['raster'],['raster_draft'],...(PW.step(value)===5?[['background']]:[])];const shownComparisons=new Set();for(const roles of groups){const assets=value.assets.filter(a=>{
  if(!roles.includes(a.role))return false;
  if(['reveal','motif'].includes(a.role)){const key=a.role+':'+a.location.sha256;if(shownComparisons.has(key))return false;shownComparisons.add(key);}
  if(a.role==='raster'&&PW.step(value)===3&&value.offers.some(o=>o.kind==='raster')&&!value.offers.some(o=>o.kind==='raster'&&o.asset_ids.includes(a.id)))return false;
  return a.role!=='background'||PW.step(value)!==5||value.offers.some(o=>o.kind==='background'&&o.id===value.facts.background_choice&&o.asset_ids.includes(a.id));
 });if(!assets.length)continue;view.append(node('h3',roles.length===2?'Abschlussbild & Motiv im Vergleich':roleNames[roles[0]],'sectionTitle'));const cards=node('div',undefined,'cards');view.append(cards);for(const asset of assets){const figure=node('figure',undefined,'card'),canvas=node('div',undefined,'canvas'),status=node('p','Original wird geladen …');canvas.dataset.role=asset.role;canvas.append(status);const caption=node('figcaption');caption.append(node('h3',asset.caption),node('p',roleNames[asset.role]+' · unveränderte Quelldatei'));const offered=value.offers.filter(o=>o.asset_ids.includes(asset.id));const choices=[];for(const offer of offered.filter(o=>PW.step(value)<5)){caption.append(node('p',offer.label));const select=node('button','Diese Variante wählen');select.dataset.choice=offer.id;select.disabled=true;select.onclick=()=>choose(offer.id,offer.kind,select);caption.append(select);choices.push(select);}const button=node('button','Großansicht öffnen');button.disabled=true;caption.append(button);figure.append(canvas,caption);cards.append(figure);
 const retry=node('button','Bild erneut laden');retry.hidden=true;caption.append(retry);
 const load=()=>{retry.hidden=true;status.textContent='Original wird geladen …';status.className='';canvas.replaceChildren(status);
  imageRequest('/api/jobs/'+id+'/assets/'+asset.id,signal).then(blob=>{if(current!==generation)return;const url=URL.createObjectURL(blob);urls.push(url);const img=node('img');img.src=url;img.alt=asset.caption;canvas.replaceChildren(img);button.disabled=false;choices.forEach(b=>b.disabled=false);button.onclick=()=>{$('largeTitle').textContent=asset.caption;$('largeImage').src=url;$('largeImage').alt=asset.caption;$('zoom').value='fit';zoom();$('large').showModal();};}).catch(exc=>{if(current===generation&&exc.name!=='AbortError'){status.textContent=exc.message;status.className='error';retry.hidden=false;}});
 };retry.onclick=load;load();}}
 const details=node('details');details.append(node('summary','Technische Quellenbindungen'));details.append(node('p',value.facts.verification));details.append(node('pre',JSON.stringify({commit:value.commit,record:value.record,assets:value.assets,offers:value.offers},null,2)));view.append(details);
 }catch(exc){if(current===generation&&exc.name!=='AbortError')$('view').replaceChildren(node('h2','Arbeitsstand kann nicht geöffnet werden'),node('p',exc.message,'error'),node('p','Quellenveröffentlichung korrigieren und danach neuere Ergebnisse suchen.','hint'));}}
function zoom(){const img=$('largeImage'),value=$('zoom').value;img.classList.toggle('zoomed',value!=='fit');if(value==='fit')img.removeAttribute('width');else img.width=img.naturalWidth*Number(value);}
$('largeImage').onload=zoom;$('zoom').onchange=zoom;$('close').onclick=()=>$('large').close();$('jobs').onchange=()=>open($('jobs').value);
let pollTimer=null;
async function checkSources(value){
 clearTimeout(pollTimer);
 const update=value.update||{state:'done'};
 $('refresh').disabled=update.state==='running';
 if(update.state==='running'){
  $('sourceStatus').textContent=`Arbeitsstände werden gesucht · ${Math.floor(update.elapsed_seconds||0)} Sekunden`;
 }else if(!listing&&value.snapshot){adopt(value);}
 else if(listing&&value.snapshot!==listing.snapshot&&value.snapshot!==pending?.snapshot){
  pending=value;$('load').hidden=false;$('sourceStatus').textContent=sourceStatus(value)+' · aktive Ansicht bleibt unverändert';error(value.errors.join('\n'));
 }
 if(update.state==='error')error(update.error||'Aktualisierung fehlgeschlagen. Erneut suchen.');
 if(update.state==='running')pollTimer=setTimeout(pollSources,1000);
}
async function pollSources(){try{await checkSources(await(await request('/api/jobs')).json());}catch(exc){$('refresh').disabled=false;error(exc.message);}}
$('refresh').onclick=async()=>{const button=$('refresh');button.disabled=true;try{await checkSources(await(await request('/api/refresh',{method:'POST'})).json());}catch(exc){error(exc.message);button.disabled=false;}};
$('load').onclick=()=>{if(pending)adopt(pending);};
function theme(value){document.documentElement.dataset.theme=value;try{localStorage.setItem('pw-theme',value);}catch{}}
$('theme').onchange=()=>theme($('theme').value);try{$('theme').value=localStorage.getItem('pw-theme')||'system';}catch{}theme($('theme').value);
pollSources();
