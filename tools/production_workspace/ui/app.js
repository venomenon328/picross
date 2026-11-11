'use strict';
const $=id=>document.getElementById(id);
let token=location.hash.slice(1);
try{if(token)sessionStorage.setItem('pw-session',token);else token=sessionStorage.getItem('pw-session')||'';}catch{}
history.replaceState(null,'',location.pathname);
let listing=null,pending=null,generation=0,controller=null,urls=[],active=null;
let detail=null,intent={},draft=null,drafts=[];
if(typeof matchMedia==='function'){
 const narrow=matchMedia('(max-width: 800px)');
 const fitNavigation=()=>{$('navigation').open=!narrow.matches;};
 fitNavigation();narrow.addEventListener('change',fitNavigation);
}
try{drafts=JSON.parse(localStorage.getItem('pw-briefs')||'[]');if(!Array.isArray(drafts))drafts=[];drafts=drafts.filter(d=>d&&typeof d.id==='string'&&typeof d.brief==='string').slice(-20);}catch{}
function saveDrafts(){try{localStorage.setItem('pw-briefs',JSON.stringify(drafts));}catch{}}
function options(){return {workroot:$('workroot').value,cleanup:$('cleanup').checked,merge:$('merge').checked};}
for(const key of ['workroot','cleanup','merge']){
 try{const saved=JSON.parse(localStorage.getItem('pw-options')||'{}');if(key==='workroot')$(key).value=saved[key]||'';else $(key).checked=saved[key]===true;}catch{}
 $(key).onchange=()=>{try{localStorage.setItem('pw-options',JSON.stringify(options()));}catch{}updatePrompt();};
}
function updatePrompt(){
 const box=$('orderText'),button=$('copyOrder'),status=$('orderStatus');
 if(!box || !button)return;
 try{
  box.value=PW.prompt(detail,intent,options());
  button.disabled=false;
  status.textContent='Den kopierten Auftrag im Chat senden.';
  status.className='hint';
 }catch(exc){
  box.value='';button.disabled=true;
  status.textContent=exc.message;
  status.className='validation';
 }
}
function remember(key,value){
 intent[key]=value;
 if(draft){
  draft[key]=value;
  saveDrafts();
 }
 updatePrompt();
}
function field(parent,label,key,placeholder){
 const wrap=node('label',label),input=node('textarea');
 input.rows=2;input.maxLength=4096;input.placeholder=placeholder||'';input.value=intent[key]||'';
 input.oninput=()=>{
  remember(key,input.value);
  if(key==='brief')renderDrafts();
 };
 wrap.append(input);parent.append(wrap);
 return input;
}
function gridFields(parent,expanded){
 const panel=node('details',undefined,'gridSettings');
 const summary=node('summary','Rastervorgaben');
 summary.append(node('small','Maße, Modus und Farbzahl'));
 panel.append(summary,node('p','Optional für das spätere Lösungsraster. Offene Werte werden bei der Motivvorlage empfohlen.','hint'));
 const grid={...PW.publishedGrid(detail),...intent.grid};
 panel.open=expanded || Boolean(grid.width || grid.height || grid.mode);
 function control(group,label,key,choices,placeholder){
  const wrap=node('label',label);
  const input=node(choices?'select':'input');
  if(choices){
   for(const [id,caption] of choices){
    const option=node('option',caption);option.value=id;input.append(option);
   }
  }else{
   input.type='text';input.inputMode='numeric';input.placeholder=placeholder;
  }
  input.value=grid[key] || (choices?choices[0][0]:'');
  input[choices?'onchange':'oninput']=()=>{
   grid[key]=input.value;
   if(key==='mode'){
    palette.hidden=grid.mode!=='color';
    if(palette.hidden){
     delete grid.colors;delete grid.colorAccuracy;
     colors.value='';precision.value='approx';
    }
   }
   remember('grid',{...intent.grid,[key]:input.value,...(key==='mode'&&grid.mode!=='color'?{colors:'',colorAccuracy:''}:{})});
  };
  wrap.append(input);group.append(wrap);
  return input;
 }
 const sizes=node('fieldset'),dims=node('div',undefined,'gridRow');
 sizes.append(node('legend','Rastergröße'),dims);
 const accuracy=[['approx','Ungefähr'],['exact','Exakt']];
 control(dims,'Breite (Zellen)','width',null,'1–50');
 control(dims,'Höhe (Zellen)','height',null,'1–50');
 control(dims,'Maßvorgabe','sizeAccuracy',accuracy);
 const modes=node('fieldset'),row=node('div',undefined,'gridRow');
 modes.append(node('legend','Rasterfarben'),row);
 control(row,'Farbmodus','mode',[['','Offen'],['mono','Monochrom'],['color','Farbig']]);
 const palette=node('div',undefined,'paletteFields');
 const colors=control(palette,'Vordergrundfarben','colors',null,'2–8 oder offen');
 const precision=control(palette,'Farbzahlvorgabe','colorAccuracy',accuracy);
 palette.hidden=grid.mode!=='color';
 row.append(palette);panel.append(sizes,modes);
 if(detail?.facts.published){
  panel.append(node('p','Vorgefüllte Werte sind Quellkontext. Änderungen werden als neue Wünsche formuliert. Leeren allein hebt keine Vorgabe auf.','hint'));
  for(const [key,label] of [['size','Rastergröße'],['mode','Rastermodus'],['colors','Farbzahl']]){
   const wrap=node('label'),check=node('input');check.type='checkbox';check.checked=intent.removeGrid?.[key]===true;
   check.onchange=()=>remember('removeGrid',{...intent.removeGrid,[key]:check.checked});
   wrap.append(check,node('span',` ${label}: bisherigen Wunsch ausdrücklich aufheben`));panel.append(wrap);
  }
 }
 parent.append(panel);
 return panel;
}
function publishedContext(view,value){
 const p=value.facts.published,section=node('section',undefined,'publishedContext');
 section.append(node('h3','Überlieferte Vorgaben & Motivbriefing'));
 const status=p.role==='approved'?'Als freigegebener Parameterkorridor überliefert; keine neue Freigabeprüfung.':p.role==='proposed'?'Veröffentlichter Wunsch, noch nicht freigegebener Parameterkorridor.':'Keine Vorgabe hinterlegt.';
 section.append(node('p',status,'sourceRole'));
 const grid=PW.publishedGrid(value);
 if(Object.keys(grid).length){
  const words=[];
  if(grid.width)words.push(`Raster: ${grid.sizeAccuracy==='exact'?'exakt':'ungefähr'} ${grid.width} × ${grid.height} Zellen (Breite × Höhe)`);
  if(grid.mode)words.push(`Modus: ${grid.mode==='mono'?'monochrom':'farbig'}`);
  if(grid.colors)words.push(`${grid.colorAccuracy==='exact'?'Exakt':'Ungefähr'} ${grid.colors} Vordergrundfarben`);
  section.append(node('p',words.join(' · ')));
 }
 const originals=node('details');originals.open=!Object.keys(grid).length;
 originals.append(node('summary','Vollständige Parameteroriginale'));
 for(const [key,label] of [['proposed','Vorgeschlagene Rasterwünsche'],['approved','Überlieferter freigegebener Korridor']]){
  if(p[key] && (!Array.isArray(p[key])||p[key].length)){
   originals.append(node('h4',label),node('pre',JSON.stringify(p[key],null,2),'sourceParameters'));
  }
 }
 if(p.role!=='absent')section.append(originals);
 section.append(node('p',`Quelle: ${active?.source==='local'?'Lokal':'Remote'} · ${active?.ref||''} · ${value.revision} · ${value.commit.slice(0,8)}. Statuswörter in den Originalangaben erteilen keine Freigabe.`,'hint'));
 const briefing=node('details');briefing.open=true;
 briefing.append(node('summary','Veröffentlichtes Motivbriefing'),node('div',p.brief.text,'briefText'));
 section.append(briefing);view.append(section);
}
function workflow(view,value){
 detail=value;
 const n=PW.step(value),order=PW.orderStep(value),section=node('section',undefined,'nextAction');
 const progress=node('ol',undefined,'steps');
 progress.setAttribute('aria-label','Produktionsschritte');
 PW.steps.forEach((label,i)=>{
  const li=node('li');
  li.append(node('span',String(i+1),'stepNumber'),node('span',label));
  if(i+1===n)li.setAttribute('aria-current','step');
  if(i+1<n)li.className='past';
  progress.append(li);
 });
 view.append(progress);
 if(value?.facts.published)publishedContext(view,value);
 section.append(node('h3',value?.facts.next_step||'Motiv beschreiben'));
 if(!value){
  field(section,'Was soll dein Rätsel zeigen?','brief','Zum Beispiel eine reife Erdbeere');
 }
 if(order===1){
  field(section,'Zusätzliche Motivhinweise (optional)','notes','Welche Details, Perspektive oder Stimmung sind dir wichtig?');
 }
 if(!value){
  const label=node('label','Referenzbild (optional)','reference'),input=node('input');
  input.type='file';input.accept='image/png,image/jpeg';
  input.onchange=()=>{intent.inputImage=input.files[0]?.name||'';updatePrompt();};
  label.append(input);section.append(label,node('p','Die ausgewählte Datei beim Senden an den Chat anhängen.','hint'));
 }
 if(value){
  const label=node('label','Nächste Aktion'),select=node('select');
  for(const [id,text] of [['continue','Fortsetzen / Entscheidung senden'],['rework','Gezielt korrigieren'],['resume','Arbeit wieder aufnehmen'],...(value.facts.state==='registered'?[['background_change','Separater Hintergrundfolgeauftrag']]:[])]){
   const opt=node('option',text);opt.value=id;select.append(opt);
  }
  label.append(select);section.append(label);
  const correction=node('div');correction.hidden=true;
  field(correction,'Was soll geändert werden?','feedback');section.append(correction);
  if(order===3)gridFields(correction,false);
  select.onchange=()=>{
   intent.action=select.value;
   correction.hidden=!['rework','background_change'].includes(select.value);
   updatePrompt();
  };
 }
 if(order===1 || order===2){
  gridFields(section,order===2);
  if(order===2)field(section,'Neue/zusätzliche Wünsche zur Motivvorlage (optional)','parameters','Zum Beispiel Merkmale, die bei der Vereinfachung erhalten bleiben sollen');
 }
 if(order===4){const d=node('details');d.append(node('summary','Optionaler Kontextwunsch'));field(d,'Kontextwunsch','context');section.append(d);}
 if(value?.facts.state==='background_review'){
  const none=node('button','Bewusst keinen Hintergrund wählen');none.onclick=()=>choose('none','background',none);section.append(none);
 }
 if(n===5)section.append(node('p',value.facts.background_choice==='none'?'Bestätigt: bewusst kein Hintergrund.':value.facts.background_choice?'Bestätigte Hintergrundwahl: '+value.facts.background_choice:'Hintergrundstatus: '+value.facts.background_status));
 if(value?.offers.length || value?.facts.state==='background_review'){
  const selected=node('p','Die gewünschte Variante auf der Bildkarte wählen.','hint');
  selected.id='selectionStatus';section.append(selected);
 }
 const actions=node('div',undefined,'orderActions');
 const copy=node('button','Auftrag kopieren','primary');copy.id='copyOrder';
 const status=node('p',undefined,'hint');status.id='orderStatus';status.setAttribute('role','status');
 const preview=node('details',undefined,'orderPreview');preview.append(node('summary','Auftrag ansehen'));
 const text=node('textarea');text.id='orderText';text.rows=10;text.readOnly=true;text.setAttribute('aria-label','Auftragstext');preview.append(text);
 copy.onclick=async()=>{
  try{
   await navigator.clipboard.writeText(text.value);
   status.textContent='Kopiert. Der Auftrag ist bereit zum Senden.';
  }catch{
   preview.open=true;text.focus();text.select();
   status.textContent='Bitte den markierten Auftrag manuell kopieren.';
  }
 };
 actions.append(copy,status);section.append(actions,preview);view.append(section);updatePrompt();
}
function choose(id,kind,button){const label=id==='none'?'kein Hintergrund':detail?.offers.find(o=>o.id===id&&o.kind===kind)?.label||id;intent.selection=id;intent.kind=kind;document.querySelectorAll('[data-choice]').forEach(b=>b.setAttribute('aria-pressed','false'));button.dataset.choice=id;button.setAttribute('aria-pressed','true');$('selectionStatus').textContent=`Vorgemerkt: ${label}. Erst der gesendete Auftrag erklärt deine Wahl.`;updatePrompt();}
function newDraft(id){
 dispose();active=null;detail=null;
 draft=drafts.find(d=>d.id===id)||{id:crypto.randomUUID(),brief:''};
 if(!drafts.includes(draft)){drafts.push(draft);drafts=drafts.slice(-20);saveDrafts();}
 intent={brief:draft.brief,notes:draft.notes||'',grid:{...draft.grid}};
 $('view').replaceChildren(node('h2','Neues Motiv'));
 workflow($('view'),null);renderDrafts();
 if(listing?.jobs.length)$('jobs').selectedIndex=-1;
}
function renderDrafts(){
 const list=$('draftList');list.replaceChildren();
 if(!drafts.length)return;
 list.append(node('p','Lokale Entwürfe','navLabel'));
 for(const d of drafts){
  const b=node('button',(d.brief.trim()||'Unbenannter Entwurf').slice(0,42),'job');
  b.setAttribute('aria-current',String(d===draft));b.onclick=()=>newDraft(d.id);list.append(b);
 }
 if(draft){
  const remove=node('button','Entwurf verwerfen','discard');
  remove.onclick=()=>{
   drafts=drafts.filter(d=>d.id!==draft.id);draft=null;saveDrafts();renderDrafts();
   if(listing?.jobs.length)open(listing.jobs[0].id);
   else if(drafts.length)newDraft(drafts.at(-1).id);
   else $('view').replaceChildren(node('p','Über „Neues Motiv“ beginnen.'));
  };
  list.append(remove);
 }
}
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
function adopt(value){const keepDraft=draft?.id;dispose();listing=value;pending=null;$('load').hidden=true;$('sourceStatus').textContent=sourceStatus(value);error(value.errors.join('\n'));$('jobs').replaceChildren();if(!value.jobs.length){
  $('jobs').append(node('option','Keine Gitstände'));
  if(active && !keepDraft){
   active=null;detail=null;intent={};
   $('view').replaceChildren(node('h2','Noch keine veröffentlichten Arbeitsstände'),node('p','Über „Neues Motiv“ beginnen oder einen lokalen Entwurf öffnen.','hint'));
  }else{
   newDraft(keepDraft || drafts.at(-1)?.id);
  }
  $('jobs').selectedIndex=0;
  return;
 }
 for(const job of value.jobs){
  let label=`${job.title} · ${job.revision} · ${job.source==='local'?'Lokal':'Remote'}: ${job.ref}`;
  if(value.jobs.some(other=>other.id!==job.id&&other.title===job.title&&other.revision===job.revision&&other.ref===job.ref&&other.source===job.source))label+=` · ${job.puzzle_id} · ${job.commit.slice(0,8)}`;
  if(job.conflict)label+=' · Quellenkonflikt';
  const opt=node('option',label);opt.value=job.id;$('jobs').append(opt);
 }
 if(keepDraft){newDraft(keepDraft);return;}const retained=value.jobs.find(j=>active&&j.puzzle_id===active.puzzle_id&&j.revision===active.revision&&j.source===active.source&&j.ref===active.ref);$('jobs').value=(retained||value.jobs[0]).id;open($('jobs').value);}
async function open(id){dispose();draft=null;detail=null;intent={};renderDrafts();const current=generation,signal=controller.signal;active=listing.jobs.find(j=>j.id===id);$('jobs').value=id;$('view').replaceChildren(node('p','Originalbindungen und Bilder werden geprüft …'));try{const value=await(await request('/api/jobs/'+id,{signal})).json();if(current!==generation)return;const view=$('view');view.replaceChildren(node('h2',value.title));view.append(node('span',({brief_ready:'Briefing bereit',reveal_review:'Abschlussbilder zur Wahl',motif_review:'Motivvorlage zur Freigabe',motif_approved:'Rasterproduktion beauftragt',raster_review:'Rasterprüfung offen',raster_ready:'Geprüfte Raster zur Wahl',background_review:'Kontextzeichnungen zur Wahl',content_ready:'Bereit zur Endabnahme',editorially_approved:'Endabnahme liegt vor',registered:'Lokal registriert'})[value.facts.state]||value.facts.state,'badge'));if(value.facts.test_only)view.append(node('span','Technische Testdaten','badge'));view.append(node('p',value.publication,'hint'));workflow(view,value);if(value.facts.blockers.length){const d=node('details');d.append(node('summary','Überlieferte offene Produktionspunkte'));const ul=node('ul');for(const b of value.facts.blockers)ul.append(node('li',b));d.append(ul);view.append(d);}
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
