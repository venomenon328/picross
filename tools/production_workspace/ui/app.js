'use strict';
const $=id=>document.getElementById(id);
let token=location.hash.slice(1);
try{if(token)sessionStorage.setItem('pw-session',token);else token=sessionStorage.getItem('pw-session')||'';}catch{}
history.replaceState(null,'',location.pathname);
let listing=null,pending=null,generation=0,controller=null,urls=[],active=null;
let detail=null,intent={},draft=null,drafts=[];
let remoteExplicit=false;
let assetLoads=new Map(),readyImages=new Set();
if(typeof matchMedia==='function'){
 const narrow=matchMedia('(max-width: 800px)');
 const fitNavigation=()=>{$('navigation').open=!narrow.matches;};
 fitNavigation();narrow.addEventListener('change',fitNavigation);
}
try{drafts=JSON.parse(localStorage.getItem('pw-briefs')||'[]');if(!Array.isArray(drafts))drafts=[];drafts=drafts.filter(d=>d&&typeof d.id==='string'&&typeof d.brief==='string').slice(-20);}catch{}
function saveDrafts(){try{localStorage.setItem('pw-briefs',JSON.stringify(drafts));}catch{}}
function options(){return {workroot:$('workroot').value,merge:$('merge').checked};}
let savedOptions={};
try{savedOptions=JSON.parse(localStorage.getItem('pw-options')||'{}');}catch{}
const initialOptions=PW.options(savedOptions);
$('workroot').value=initialOptions.workroot;$('merge').checked=initialOptions.merge;
for(const key of ['workroot','merge']){
 $(key).onchange=()=>{
  try{localStorage.setItem('pw-options',JSON.stringify(options()));}catch{}
  if($('finalMerge'))$('finalMerge').checked=$('merge').checked;
  updatePrompt();
 };
}
function updatePrompt(){
 const box=$('orderText'),button=$('copyOrder'),status=$('orderStatus');
 if(!box||!button)return;
 const final=PW.closing(detail,intent);
 button.textContent=final?(detail.facts.state==='registered'?'Git-Abschluss: Auftrag kopieren':'Endabnahme & Integration: Auftrag kopieren'):'Auftrag kopieren';
 if($('finalScope'))$('finalScope').hidden=!final;
 try{
  if(final){
   const images=PW.finalAssets(detail,intent);
   if([images.raster,images.reveal,images.background].filter(Boolean).some(a=>!readyImages.has(a.id))){
    throw Error('Die Originalbilder der Schlussauswahl zuerst vollständig laden. Bei einem Bildfehler gezielt erneut laden.');
   }
  }
  box.value=PW.prompt(detail,intent,options());
  button.disabled=false;
  status.textContent=final?(options().merge?'Auftrag bis main – erst nach unabhängigem Review und allen Gates.':'Auftrag bis Draft-PR – kein Merge.'):'Den kopierten Auftrag im Chat senden.';
  status.className='hint';
 }catch(exc){
  box.value='';button.disabled=true;status.textContent=exc.message;status.className='validation';
 }
}
function remember(key,value){
 intent[key]=value;
 if(draft){draft[key]=value;saveDrafts();}
 updatePrompt();
}
function field(parent,label,key,placeholder){
 const wrap=node('label',label),input=node('textarea');
 input.rows=2;input.maxLength=4096;input.placeholder=placeholder||'';input.value=intent[key]||'';
 input.oninput=()=>{remember(key,input.value);if(key==='brief')renderDrafts();};
 wrap.append(input);parent.append(wrap);return input;
}
function gridFields(parent,expanded){
 const panel=node('details',undefined,'gridSettings');
 const summary=node('summary','Rastervorgaben');summary.append(node('small','Maße, Modus und Farbzahl'));
 panel.append(summary,node('p','Optional für das spätere Lösungsraster. Offene Werte werden bei der Motivvorlage empfohlen.','hint'));
 const grid={...PW.publishedGrid(detail),...intent.grid};
 panel.open=expanded||Boolean(grid.width||grid.height||grid.mode);
 function control(group,label,key,choices,placeholder,unit){
  const wrap=node('label',label),input=node(choices?'select':'input');
  if(choices){for(const [id,caption] of choices){const option=node('option',caption);option.value=id;input.append(option);}}
  else{input.type='text';input.inputMode='numeric';input.placeholder=placeholder;}
  input.value=grid[key]||(choices?choices[0][0]:'');
  input[choices?'onchange':'oninput']=()=>{
   grid[key]=input.value;
   if(key==='mode'){
    palette.hidden=grid.mode!=='color';
    if(palette.hidden){delete grid.colors;delete grid.colorAccuracy;colors.value='';precision.value='approx';}
   }
   remember('grid',{...intent.grid,[key]:input.value,...(key==='mode'&&grid.mode!=='color'?{colors:'',colorAccuracy:''}:{})});
  };
  if(unit){const measure=node('span',undefined,'numberUnit');measure.append(input,node('span',unit));wrap.append(measure);}
  else wrap.append(input);
  group.append(wrap);return input;
 }
 function removal(group,key,label,inputs,onSync){
  if(!detail?.facts.published)return;
  const wrap=node('label',undefined,'removeGrid'),check=node('input');check.type='checkbox';check.checked=intent.removeGrid?.[key]===true;
  function sync(){for(const [name,input] of inputs){input.disabled=check.checked;input.value=check.checked?'':grid[name]||'';}if(onSync)onSync(check.checked);}
  check.onchange=()=>{sync();remember('removeGrid',{...intent.removeGrid,[key]:check.checked});};
  wrap.append(check,node('span',` ${label} ausdrücklich aufheben`));group.append(wrap);sync();
 }
 const sizes=node('fieldset'),dims=node('div',undefined,'gridRow');sizes.append(node('legend','Rastergröße'),dims);
 const accuracy=[['approx','Ungefähr'],['exact','Exakt']];
 for(const [key,label] of [['width','Breite'],['height','Höhe']]){
  const axis=node('div',undefined,'axisField');dims.append(axis);
  const input=control(axis,label,key,null,'1–50','Zellen');removal(axis,key,label,[[key,input]]);
 }
 control(dims,'Genauigkeit der ausgefüllten Achsen','sizeAccuracy',accuracy);
 const modes=node('fieldset'),row=node('div',undefined,'gridRow');modes.append(node('legend','Rasterfarben'),row);
 const mode=control(row,'Farbmodus','mode',[['','Offen'],['mono','Monochrom'],['color','Farbig']]);
 const palette=node('div',undefined,'paletteFields');
 const colors=control(palette,'Vordergrundfarben','colors',null,'2–8');colors.className='shortNumber';
 const precision=control(palette,'Farbzahlvorgabe','colorAccuracy',accuracy);
 palette.hidden=grid.mode!=='color';row.append(palette);panel.append(sizes,modes);
 if(detail?.facts.published){
  panel.append(node('p','Vorgefüllte Werte sind Quellkontext. Änderungen werden als neue Wünsche formuliert. Leeren allein hebt keine Vorgabe auf.','hint'));
  removal(modes,'mode','Rastermodus',[['mode',mode]],removed=>{palette.hidden=removed||grid.mode!=='color';});
  removal(palette,'colors','Farbzahl',[['colors',colors]]);
 }
 parent.append(panel);return panel;
}
function publishedContext(view,value){
 const p=value.facts.published,section=node('section',undefined,'publishedContext');
 section.append(node('h3','Überlieferte Vorgaben & Motivbriefing'));
 const status=p.role==='approved'?'Überlieferter freigegebener Parameterkorridor':p.role==='proposed'?'Veröffentlichte Wünsche – Korridor noch nicht freigegeben':'Keine strukturierten Rastervorgaben; siehe Motivbriefing.';
 section.append(node('p',status,'sourceRole'));
 const grid=PW.publishedGrid(value),parameterList=p.approved?.length?p.approved:p.proposed;
 const corridor=Array.isArray(parameterList)?parameterList.find(v=>v?.format==='picross-raster-parameters-v1'):null;
 if(corridor){
  const kind={exact:'exakt',approximate:'ungefähr',open:'offen'};
  for(const [axis,label] of [['width','Breite'],['height','Höhe'],['foreground_colors','Vordergrundfarben']]){
   const c=corridor.constraints[axis];
   section.append(node('p',`${label}: ${kind[c.kind]}${c.target===null?'':` ${c.target}`} · Untergrenze: ${c.minimum??'keine'} · Obergrenze: ${c.maximum??'keine'}`));
  }
  section.append(node('p',`Geschützte Merkmale: ${corridor.derivation.protected_features.join('; ')||'keine benannt'}.`));
 }
 if(Object.keys(grid).length){
  const words=[];
  for(const [axis,label] of [['width','Breite'],['height','Höhe']])if(grid[axis])words.push(`${label}: ${grid.sizeAccuracy==='exact'?'exakt':'ungefähr'} ${grid[axis]} Zellen`);
  if(grid.mode)words.push(`Modus: ${grid.mode==='mono'?'monochrom':'farbig'}`);
  if(grid.colors)words.push(`${grid.colorAccuracy==='exact'?'Exakt':'Ungefähr'} ${grid.colors} Vordergrundfarben`);
  section.append(node('p',words.join(' · ')));
 }else if(p.role!=='absent'&&!corridor)section.append(node('p','Keine eindeutigen Einzelwerte; vollständige Parameter stehen in den technischen Details.','hint'));
 const briefing=node('details');briefing.append(node('summary','Veröffentlichtes Motivbriefing'),node('div',p.brief.text,'briefText'));
 section.append(briefing);view.append(section);
}
function progress(view,value){
 const n=PW.step(value),list=node('ol',undefined,'steps');list.setAttribute('aria-label','Produktionsschritte');
 PW.steps.forEach((label,i)=>{const li=node('li');li.append(node('span',String(i+1),'stepNumber'),node('span',label));if(i+1===n)li.setAttribute('aria-current','step');if(i+1<n)li.className='past';list.append(li);});
 view.append(list);
}
function metadata(view,value){
 const m=value?.facts.metadata;
 if(!m)return;
 const words=[];
 if(Number.isInteger(m.width)&&Number.isInteger(m.height))words.push(`${m.width} × ${m.height} Zellen`);
 if(m.mode)words.push(m.mode==='mono'?'Monochrom':'Farbig');
 if(Number.isInteger(m.used_colors))words.push(`${m.used_colors} Vordergrundfarbe${m.used_colors===1?'':'n'}`);
 const raw=typeof m.difficulty==='number'?m.difficulty:m.difficulty?.level;
 const level=typeof raw==='string'&&/^L[1-5]$/.test(raw)?Number(raw.slice(1)):raw;
 if(Number.isInteger(level)&&level>=1&&level<=5)words.push(['','Sehr leicht','Leicht','Mittel','Schwer','Sehr schwer'][level]);
 if(words.length)view.append(node('p',words.join(' · '),'puzzleMetadata'));
}
function workflow(view,value){
 detail=value;
 const n=PW.step(value),order=PW.orderStep(value),section=node('section',undefined,'nextAction');
 section.append(node('h3',PW.closing(value,intent)?(value.facts.state==='registered'?'Git-Abschluss fortsetzen':'Schlussauswahl abnehmen & integrieren'):value?.facts.next_step||'Motiv beschreiben'));
 if(!value)field(section,'Was soll dein Rätsel zeigen?','brief','Zum Beispiel eine reife Erdbeere');
 if(order===1)field(section,'Zusätzliche Motivhinweise (optional)','notes','Welche Details, Perspektive oder Stimmung sind dir wichtig?');
 if(!value){
  const label=node('label','Referenzbild (optional)','reference'),input=node('input');input.type='file';input.accept='image/png,image/jpeg';
  input.onchange=()=>{intent.inputImage=input.files[0]?.name||'';updatePrompt();};
  label.append(input);section.append(label,node('p','Die ausgewählte Datei beim Senden an den Chat anhängen.','hint'));
 }
 if(value){
  const label=node('label','Nächste Aktion'),select=node('select');
  for(const [id,text] of [['continue','Fortsetzen / Entscheidung senden'],['rework','Gezielt korrigieren'],['resume','Arbeit wieder aufnehmen'],...(value.facts.state==='registered'?[['background_change','Separater Hintergrundfolgeauftrag']]:[])]){
   const opt=node('option',text);opt.value=id;select.append(opt);
  }
  label.append(select);section.append(label);
  const correction=node('div');correction.hidden=true;field(correction,'Was soll geändert werden?','feedback');section.append(correction);
  if(order===3)gridFields(correction,false);
  select.onchange=()=>{intent.action=select.value;correction.hidden=!['rework','background_change'].includes(select.value);updatePrompt();};
 }
 if(order===1||order===2){gridFields(section,order===2);if(order===2)field(section,'Neue/zusätzliche Wünsche zur Motivvorlage (optional)','parameters','Zum Beispiel Merkmale, die bei der Vereinfachung erhalten bleiben sollen');}
 if(order===4){const d=node('details');d.append(node('summary','Optionaler Kontextwunsch'));field(d,'Kontextwunsch','context');section.append(d);}
 if(value?.offers.length||value?.facts.state==='background_review'){
  const selected=node('p','Die gewünschte Variante auf der Bildkarte wählen.','hint');selected.id='selectionStatus';section.append(selected);
 }
 if(value?.facts.state==='background_review'){
  const none=node('button','Bewusst keinen Hintergrund wählen');none.onclick=()=>choose('none','background',none);none.dataset.choice='none';none.setAttribute('aria-pressed','false');section.append(none);
 }
 if(n===5)section.append(node('p',value.facts.background_choice==='none'?'Bestätigt: bewusst kein Hintergrund.':value.facts.background_choice?'Bestätigte Hintergrundwahl: '+value.facts.background_choice:'Hintergrundentscheidung noch offen.','hint'));
 if(PW.closing(value)){
  const scope=node('div',undefined,'finalScope');scope.id='finalScope';
  const label=node('label'),merge=node('input');merge.type='checkbox';merge.id='finalMerge';merge.checked=options().merge;
  merge.onchange=()=>{$('merge').checked=merge.checked;$('merge').onchange();};
  label.append(merge,node('span',' Nach unabhängigem Review und allen Gates nach main mergen'));
  scope.append(label,node('p','Erst der gesendete Auftrag erklärt die Endabnahme und den gewählten Umfang. Klicken, Kopieren und Aktualisieren bestätigen nichts.','hint'));section.append(scope);
 }
 const actions=node('div',undefined,'orderActions'),copy=node('button','Auftrag kopieren','primary');copy.id='copyOrder';
 const status=node('p',undefined,'hint');status.id='orderStatus';status.setAttribute('role','status');
 const preview=node('details',undefined,'orderPreview');preview.append(node('summary','Auftrag ansehen'));
 const text=node('textarea');text.id='orderText';text.rows=10;text.readOnly=true;text.setAttribute('aria-label','Auftragstext');preview.append(text);
 copy.onclick=async()=>{
  updatePrompt();if(copy.disabled)return;
  try{await navigator.clipboard.writeText(text.value);status.textContent='Kopiert. Erst im Chat senden, um den Auftrag zu erteilen.';}
  catch{preview.open=true;text.focus();text.select();status.textContent='Bitte den markierten Auftrag manuell kopieren.';}
 };
 actions.append(copy,status);section.append(actions,preview);view.append(section);updatePrompt();
}
function choose(id,kind,button){
 const label=id==='none'?'kein Hintergrund':detail?.offers.find(o=>o.id===id&&o.kind===kind)?.label||id;
 intent.selection=id;intent.kind=kind;
 document.querySelectorAll('[data-choice]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.choice===id)));
 button.dataset.choice=id;button.setAttribute('aria-pressed','true');
 if($('selectionStatus'))$('selectionStatus').textContent=`Vorgemerkt: ${label}. Erst der gesendete Auftrag erklärt deine Wahl.`;
 refreshFinalPreview();const alternatives=$('backgroundOptions');if(alternatives)alternatives.open=false;updatePrompt();
}
function newDraft(id){
 dispose();active=null;detail=null;$('versions').hidden=true;$('motifStatus').textContent='Lokaler Entwurf';
 draft=drafts.find(d=>d.id===id)||{id:crypto.randomUUID(),brief:''};
 if(!drafts.includes(draft)){drafts.push(draft);drafts=drafts.slice(-20);saveDrafts();}
 intent={brief:draft.brief,notes:draft.notes||'',grid:{...draft.grid}};
 $('view').replaceChildren(node('h2','Neues Motiv'));progress($('view'),null);workflow($('view'),null);renderDrafts();
 if(listing?.jobs.length)$('jobs').selectedIndex=-1;
}
function renderDrafts(){
 const list=$('draftList');list.replaceChildren();if(!drafts.length)return;
 list.append(node('p','Lokale Entwürfe','navLabel'));
 for(const d of drafts){const b=node('button',(d.brief.trim()||'Unbenannter Entwurf').slice(0,42),'job');b.setAttribute('aria-current',String(d===draft));b.onclick=()=>newDraft(d.id);list.append(b);}
 if(draft){
  const remove=node('button','Entwurf verwerfen','discard');remove.onclick=()=>{
   drafts=drafts.filter(d=>d.id!==draft.id);draft=null;saveDrafts();renderDrafts();
   if(listing?.motifs.length)chooseMotif(listing.motifs[0].puzzle_id);else if(drafts.length)newDraft(drafts.at(-1).id);else $('view').replaceChildren(node('p','Über „Neues Motiv“ beginnen.'));
  };list.append(remove);
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
  const response=await fetch(path,{...options,headers:{...options.headers,'X-Workspace-Session':token},cache:'no-store'});
  if(response.ok)return response;
  let body;try{body=await response.json();}catch{body={error:'Lokaler Dienst nicht erreichbar. Starter erneut öffnen.'};}
  if(options.method==='POST'||response.status!==503||(!waitForImageSlot&&attempt===4))throw new Error(body.error);
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
  request(task.path,{signal:task.signal},true).then(r=>r.blob()).then(task.resolve,task.reject).finally(()=>{imageLoads--;drainImages();});
 }
}
function imageRequest(path,signal){return new Promise((resolve,reject)=>{imageQueue.push({path,signal,resolve,reject});drainImages();});}
function dispose(){closeRemoval();generation++;controller?.abort();controller=new AbortController();for(const url of urls)URL.revokeObjectURL(url);urls=[];assetLoads=new Map();readyImages=new Set();$('large').close();}
function sourceStatus(value){return (value.mode==='local'?'Nur lokale Gitstände · Remote-Sicherung nicht bestätigt':value.sync_error||(!value.remote_confirmed?'Remote nicht aktuell bestätigt · letzter Cache: '+(value.synced_at?new Date(value.synced_at).toLocaleString('de-DE'):'unbekannt'):('Remote zuletzt geladen: '+(value.synced_at?new Date(value.synced_at).toLocaleString('de-DE'):'noch nicht synchronisiert'))));}
function currentMotif(){return listing?.motifs.find(m=>m.puzzle_id===$('jobs').value);}
function versionControls(motif,id){
 $('versions').hidden=false;$('version').replaceChildren();
 const empty=node('option','Version bewusst wählen');empty.value='';$('version').append(empty);
 for(const [n,v] of motif.versions.entries()){const option=node('option',`${v.current?'Aktuell · ':''}${v.phase} · ${v.revision}`);option.value=String(n);$('version').append(option);}
 const index=motif.versions.findIndex(v=>v.sources.includes(id));$('version').value=index<0?'':String(index);
 $('jobSource').replaceChildren();
 const bound=listing.jobs.find(j=>j.id===id),placeholder=node('option',bound?`Aktiv: ${bound.source==='local'?'Lokal':'Remote'} · ${bound.commit.slice(0,8)} · Quelle wählen`:'Quelle wählen');placeholder.value='';$('jobSource').append(placeholder);
 const version=motif.versions[index];$('versionOrigin').textContent=version?.source_label||'';
 if(version)for(const jid of version.sources){const job=listing.jobs.find(j=>j.id===jid),option=node('option',`${job.source==='local'?'Lokal':'Remote'} · ${job.ref==='main'?'main':'Produktionsbranch'} · ${job.commit.slice(0,8)}`);option.value=jid;$('jobSource').append(option);}
 $('jobSource').value=remoteExplicit?id||'':'';$('jobSource').disabled=!version;$('motifStatus').textContent=motif.status;$('versionNotes').textContent=motif.notes.join(' ');
}
function chooseMotif(puzzleId){
 const motif=listing.motifs.find(m=>m.puzzle_id===puzzleId);if(!motif)return;$('jobs').value=puzzleId;
 if(motif.current_job){open(motif.current_job);return;}
 dispose();active=null;draft=null;detail=null;intent={};remoteExplicit=false;renderDrafts();versionControls(motif,null);
 $('view').replaceChildren(node('h2',motif.title),node('p','Aktuelle Übergabe nicht eindeutig. Bitte eine Version wählen.','validation'),node('p',motif.notes.join(' '),'hint'));
}
function adopt(value){
 const keepDraft=draft?.id,keepId=active?.puzzle_id||$('jobs').value;
 dispose();listing=value;pending=null;$('load').hidden=true;$('sourceStatus').textContent=sourceStatus(value);error(value.errors.join('\n'));$('jobs').replaceChildren();
 for(const motif of value.motifs){const option=node('option',motif.label);option.value=motif.puzzle_id;$('jobs').append(option);}
 if(keepDraft){newDraft(keepDraft);return;}
 if(!value.motifs.length){
  $('jobs').append(node('option','Keine Gitstände'));active=null;detail=null;intent={};
  if(drafts.length)newDraft(drafts.at(-1).id);else{$('versions').hidden=true;$('motifStatus').textContent='';$('view').replaceChildren(node('h2','Noch keine veröffentlichten Arbeitsstände'),node('p','Über „Neues Motiv“ beginnen.'));}
  return;
 }
 chooseMotif(value.motifs.find(m=>m.puzzle_id===keepId)?.puzzle_id||value.motifs[0].puzzle_id);
}
function assetURL(id,asset,current,signal){
 if(!assetLoads.has(asset.id)){
  const cache=assetLoads;
  const promise=imageRequest('/api/jobs/'+id+'/assets/'+asset.id,signal).then(blob=>{
   if(current!==generation)throw new DOMException('Ansicht gewechselt','AbortError');
   const url=URL.createObjectURL(blob);urls.push(url);return url;
  }).catch(exc=>{cache.delete(asset.id);throw exc;});
  cache.set(asset.id,promise);
 }
 return assetLoads.get(asset.id);
}
function assetCard(value,id,asset,selectable=true){
 const current=generation,signal=controller.signal;
 const figure=node('figure',undefined,'card'),canvas=node('div',undefined,'canvas'),status=node('p','Original wird geladen …');
 canvas.dataset.role=asset.role;canvas.append(status);
 const caption=node('figcaption');caption.append(node('h3',asset.caption));
 const choices=[];
 if(selectable)for(const offer of value.offers.filter(o=>o.asset_ids.includes(asset.id)&&PW.step(value)<5)){
  caption.append(node('p',offer.label));
  const select=node('button','Diese Variante wählen');select.dataset.choice=offer.id;select.setAttribute('aria-pressed',String(intent.selection===offer.id));select.disabled=true;select.onclick=()=>choose(offer.id,offer.kind,select);caption.append(select);choices.push(select);
 }
 const button=node('button','Großansicht öffnen');button.disabled=true;caption.append(button);
 figure.append(canvas,caption);
 const retry=node('button','Bild erneut laden');retry.hidden=true;caption.append(retry);
 const load=async()=>{
  retry.hidden=true;status.textContent='Original wird geladen …';status.className='';canvas.replaceChildren(status);
  try{
   const url=await assetURL(id,asset,current,signal);if(current!==generation)return;
   const img=node('img');img.src=url;img.alt=asset.caption;
   if(typeof img.decode==='function')await img.decode();
   if(current!==generation)return;
   canvas.replaceChildren(img);readyImages.add(asset.id);button.disabled=false;choices.forEach(b=>b.disabled=false);
   button.onclick=()=>{$('largeTitle').textContent=asset.caption;$('largeImage').src=url;$('largeImage').alt=asset.caption;$('zoom').value='fit';zoom();$('large').showModal();};
   updatePrompt();
  }catch(exc){
   if(current===generation&&exc.name!=='AbortError'){
    readyImages.delete(asset.id);assetLoads.delete(asset.id);status.textContent=exc.message;status.className='error';retry.hidden=false;updatePrompt();
   }
  }
 };retry.onclick=load;load();return figure;
}
function finalOverview(view,value,id){
 const section=node('section',undefined,'finalOverview');section.append(node('h3','Deine Schlussauswahl','sectionTitle'));
 section.append(node('p','Gewähltes Raster und zugehöriges Abschlussbild. Die Hintergrundwahl wird erst mit dem gesendeten Schlussauftrag bestätigt.','hint'));
 const cards=node('div',undefined,'closingCards');
 for(const [role,label] of [['raster','Gewähltes Raster'],['reveal','Zugehöriges Abschlussbild']]){
  const slot=node('div');slot.append(node('h4',label));
  const assets=value.assets.filter(a=>a.id===value.facts.composition?.[role]&&a.role===role);
  if(assets.length===1)slot.append(assetCard(value,id,assets[0],false));else slot.append(node('p','Originalbindung fehlt oder ist uneindeutig.','validation'));
  cards.append(slot);
 }
 const background=node('div',undefined,'summaryBackground');background.id='summaryBackground';cards.append(background);
 section.append(cards);view.append(section);refreshFinalPreview();
}
function refreshFinalPreview(){
 const slot=$('summaryBackground');if(!slot||!detail||!active)return;
 slot.replaceChildren(node('h4',detail.facts.state==='background_review'?'Vorgemerkter Hintergrund':'Bestätigter Hintergrund'));
 try{
  const result=PW.finalAssets(detail,intent);
  if(result.choice==='none')slot.append(node('p','Bewusst kein Hintergrund','noneChoice'));
  else slot.append(assetCard(detail,active.id,result.background,false));
 }catch(exc){slot.append(node('p',exc.message,'validation'));}
}
function technicalDetails(view,value){
 const panel=node('details',undefined,'technicalDetails');panel.id='technicalDetails';panel.append(node('summary','Technische Details & vollständige Übergabedaten'));
 panel.append(node('p',value.facts.verification,'hint'));
 const text=node('textarea');text.readOnly=true;text.rows=14;text.setAttribute('aria-label','Technische Übergabedaten');
 text.value=JSON.stringify({commit:value.commit,source_url:value.source_url,publication:value.publication,record:value.record,facts:value.facts,assets:value.assets,offers:value.offers},null,2);
 const copy=node('button','Übergabedaten kopieren'),status=node('p',undefined,'hint');status.setAttribute('role','status');
 copy.onclick=async()=>{try{await navigator.clipboard.writeText(text.value);status.textContent='Übergabedaten kopiert.';}catch{text.focus();text.select();status.textContent='Bitte die markierten Übergabedaten manuell kopieren.';}};
 panel.append(copy,status,text);view.append(panel);
}
async function open(id,explicit=false){
 dispose();draft=null;detail=null;intent={};remoteExplicit=explicit;renderDrafts();
 const current=generation,signal=controller.signal;active=listing.jobs.find(j=>j.id===id);$('jobs').value=active.puzzle_id;versionControls(currentMotif(),id);
 $('view').replaceChildren(node('p','Originalbindungen und Bilder werden geprüft …'));
 try{
  const value=await(await request('/api/jobs/'+id,{signal})).json();if(current!==generation)return;
  detail=value;
  const view=$('view');view.replaceChildren(node('h2',value.title));
  view.append(node('span',({brief_ready:'Briefing bereit',reveal_review:'Abschlussbilder zur Wahl',motif_review:'Motivvorlage zur Freigabe',motif_approved:'Rasterproduktion beauftragt',raster_review:'Rasterprüfung offen',raster_ready:'Geprüfte Raster zur Wahl',background_review:'Kontextzeichnungen zur Wahl',content_ready:'Bereit zur Endabnahme',editorially_approved:'Endabnahme liegt vor',registered:'Lokal registriert'})[value.facts.state]||value.facts.state,'badge'));
  if(value.facts.test_only)view.append(node('span','Technische Testdaten','badge'));
  progress(view,value);metadata(view,value);
  if(value.facts.published)publishedContext(view,value);
  if(value.facts.blockers.length){
   const issues=node('section',undefined,'openPoints');issues.append(node('h3','Noch offene Produktionspunkte'));
   for(const b of value.facts.blockers)issues.append(node('p',b,'validation'));view.append(issues);
  }
  const final=PW.closing(value);
  if(final)finalOverview(view,value,id);
  const groups=final?(value.facts.state==='background_review'?[['background']]:[]):[['reveal','motif'],['raster'],['raster_draft']];
  let gallery=view;
  if(value.facts.state==='background_review'){gallery=node('details',undefined,'backgroundOptions');gallery.id='backgroundOptions';gallery.open=true;gallery.append(node('summary','Kontextzeichnungen vergleichen & wählen'));view.append(gallery);}
  const shownComparisons=new Set();
  for(const roles of groups){
   const assets=value.assets.filter(a=>{
    if(!roles.includes(a.role))return false;
    if(['reveal','motif'].includes(a.role)){const key=a.role+':'+a.location.sha256;if(shownComparisons.has(key))return false;shownComparisons.add(key);}
    if(a.role==='raster'&&PW.step(value)===3&&value.offers.some(o=>o.kind==='raster')&&!value.offers.some(o=>o.kind==='raster'&&o.asset_ids.includes(a.id)))return false;
    return true;
   });
   if(!assets.length)continue;
   gallery.append(node('h3',roles.length===2?'Abschlussbild & Motiv im Vergleich':roleNames[roles[0]],'sectionTitle'));
   const cards=node('div',undefined,'cards');gallery.append(cards);for(const asset of assets)cards.append(assetCard(value,id,asset));
  }
  workflow(view,value);technicalDetails(view,value);removalAction(view,value);
 }catch(exc){if(current===generation&&exc.name!=='AbortError')$('view').replaceChildren(node('h2','Arbeitsstand kann nicht geöffnet werden'),node('p',exc.message,'error'),node('p','Quellenveröffentlichung korrigieren und danach neuere Ergebnisse suchen.','hint'));}
}
function zoom(){const img=$('largeImage'),value=$('zoom').value;img.classList.toggle('zoomed',value!=='fit');if(value==='fit')img.removeAttribute('width');else img.width=img.naturalWidth*Number(value);}
$('largeImage').onload=zoom;$('zoom').onchange=zoom;$('close').onclick=()=>$('large').close();$('jobs').onchange=()=>chooseMotif($('jobs').value);
$('version').onchange=()=>{const version=currentMotif()?.versions[Number($('version').value)];if($('version').value!==''&&version)open(version.sources[0]);};
$('jobSource').onchange=()=>{if($('jobSource').value)open($('jobSource').value,true);};
// Destructive plans live only in this dialog, never in browser storage.
let removalEpoch=0,removalBusy=false;
function closeRemoval(){removalEpoch++;$('removal')?.close();}
async function removalPost(route,body){
 return (await request('/api/removal/'+route,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)})).json();
}
function removalAction(view,value){
 const area=node('section',undefined,'removalAction'),button=node('button','Produktion entfernen','danger');
 const reason=value.removal_unavailable||(!remoteExplicit?'Zur Entfernung zuerst die konkrete Remotequelle ausdrücklich wählen.':null);
 button.disabled=Boolean(reason);
 button.onclick=()=>previewRemoval({job_id:active.id,snapshot:listing.snapshot});
 area.append(button,node('p',reason||'Entfernt den ganzen Produktionsbranch im Remote. Zunächst werden Ziel und Schutzbedingungen geprüft.','hint'));
 view.append(area);
}
async function previewRemoval(binding){
 closeRemoval();const epoch=removalEpoch,dialog=$('removal'),body=$('removalBody');
 body.replaceChildren(node('h2','Produktion entfernen'),node('p','Ziel, PRs und lokale Sicherheit werden geprüft …'));
 $('removalClose').disabled=false;dialog.showModal();
 try{
  const plan=await removalPost('preview',binding);
  if(epoch!==removalEpoch)return;
  const local=plan.kind==='local';
  body.replaceChildren(node('h2',local?'Lokalen Branchref bereinigen':'Produktion entfernen'));
  body.append(node('p',local?'Die Remoteentfernung ist bereits bestätigt. Dieser zusätzliche Schritt entfernt ausschließlich den lokalen Ref.':'Der gesamte Remote-Branch mit allen aufgeführten Revisionen wird entfernt.'));
  const facts=node('dl',undefined,'removalFacts');
  const rows=[['Repository',plan.repository],['Quelle',local?'Lokaler Branchref nach Remoteentfernung':'Remote'],['Branch',plan.branch],['Voller Ref',plan.ref],['Geprüfte SHA',plan.sha],['Produktion',plan.title+' · '+plan.puzzle_id],['Betroffene Revisionen',plan.revisions.join(', ')],['Lokaler Ref',plan.local.sha||'Nicht vorhanden'],['Worktrees',plan.local.checked_out?`${plan.local.checked_out} mit ausgechecktem Zielbranch`:'Zielbranch in keinem Worktree ausgecheckt'],['Pull Requests',plan.prs.length?plan.prs.map(p=>`#${p.number}: ${p.merged?'gemergt':p.state==='open'?'offen':'geschlossen, nicht gemergt'}`).join('; '):'Keine passenden PRs'],['Auf main',plan.main.revisions.length||plan.main.registered?`Revisionen: ${plan.main.revisions.join(', ')||'keine Authoringstände'} · Katalog: ${plan.main.registered?'vorhanden':'nicht verzeichnet'}`:'Keine Stände dieser Produktion verzeichnet']];
  for(const [label,text] of rows)facts.append(node('dt',label),node('dd',text));
  body.append(facts);
  for(const warning of plan.warnings)body.append(node('p',warning,'validation'));
  if(plan.blockers.length){for(const blocker of plan.blockers)body.append(node('p',blocker,'error'));return;}
  body.append(node('p','Maininhalte, Arbeitsdateien und Worktrees bleiben erhalten. Diese Bestätigung gilt drei Minuten.','hint'));
  const label=node('label','Zur Bestätigung den exakten Branchnamen selbst eingeben'),input=node('input');
  input.type='text';input.autocomplete='off';input.spellcheck=false;input.id='removalConfirmation';label.append(input);
  const confirm=node('button',local?'Lokalen Ref jetzt entfernen':'Remote-Branch jetzt entfernen','danger');confirm.disabled=true;
  input.oninput=()=>{confirm.disabled=input.value!==plan.branch;};
  input.onpaste=e=>e.preventDefault();input.ondrop=e=>e.preventDefault();
  body.append(label,confirm);input.focus();
  confirm.onclick=async()=>{
   if(removalBusy||input.value!==plan.branch)return;
   removalBusy=true;confirm.disabled=true;input.disabled=true;$('removalClose').disabled=true;
   try{
    const result=await removalPost('confirm',{plan_id:plan.plan_id,job_id:plan.job_id,snapshot:plan.snapshot,confirmation:input.value});
    if(epoch!==removalEpoch)return;
    if(result.listing){adopt(result.listing);}
    showRemovalResult(result);
   }catch(exc){showRemovalResult({removed:false,message:exc.message+' Keine weitere Aktion ausgeführt oder bestätigt. Vor einem neuen Versuch Quellen neu prüfen.'});}
   finally{removalBusy=false;$('removalClose').disabled=false;}
  };
 }catch(exc){if(epoch===removalEpoch)body.replaceChildren(node('h2','Entfernung nicht möglich'),node('p',exc.message,'error'));}
}
function showRemovalResult(result){
 const dialog=$('removal'),body=$('removalBody');
 body.replaceChildren(node('h2',result.removed?(result.kind==='local'?'Lokaler Ref entfernt':'Remote-Branch entfernt'):'Entfernung nicht bestätigt'),node('p',result.message,result.removed?'':'error'));
 if(result.branch)body.append(node('p',result.branch,'removalBranch'));
 if(result.cache_error)body.append(node('p',result.cache_error,'error'));
 if(result.receipt_id){
  const label=node('label'),choice=node('input'),button=node('button','Lokale Bereinigung vorprüfen');
  choice.type='checkbox';choice.checked=false;button.disabled=true;
  label.append(choice,node('span',' Optional auch den sicheren lokalen Branchref bereinigen'));
  choice.onchange=()=>{button.disabled=!choice.checked;};
  button.onclick=()=>previewRemoval({receipt_id:result.receipt_id});
  body.append(node('p','Der lokale Branch bleibt zunächst als eigene Quelle in der Auswahl erhalten.','hint'),label,button);
 }
 body.append(node('p','Weitere lokale und auf main veröffentlichte Stände bleiben in „Veröffentlichte Stände“ erreichbar.','hint'));
 if(!dialog.open)dialog.showModal();
}
$('removalClose').onclick=()=>{if(!removalBusy)closeRemoval();};
$('removal').oncancel=e=>{if(removalBusy)e.preventDefault();else closeRemoval();};
let pollTimer=null;
async function checkSources(value){
 clearTimeout(pollTimer);
 const update=value.update||{state:'done'};
 $('refresh').disabled=update.state==='running';
 if(update.state==='running'){$('sourceStatus').textContent=`Arbeitsstände werden gesucht · ${Math.floor(update.elapsed_seconds||0)} Sekunden`;}
 else if(!listing&&value.snapshot){adopt(value);}
 else if(listing&&value.snapshot!==listing.snapshot&&value.snapshot!==pending?.snapshot){pending=value;$('load').hidden=false;$('sourceStatus').textContent=sourceStatus(value)+' · aktive Ansicht bleibt unverändert';error(value.errors.join('\n'));}
 if(update.state==='error')error(update.error||'Aktualisierung fehlgeschlagen. Erneut suchen.');
 if(update.state==='running')pollTimer=setTimeout(pollSources,1000);
}
async function pollSources(){try{await checkSources(await(await request('/api/jobs')).json());}catch(exc){$('refresh').disabled=false;error(exc.message);}}
$('refresh').onclick=async()=>{const button=$('refresh');button.disabled=true;try{await checkSources(await(await request('/api/refresh',{method:'POST'})).json());}catch(exc){error(exc.message);button.disabled=false;}};
$('load').onclick=()=>{if(pending)adopt(pending);};
function theme(value){document.documentElement.dataset.theme=value;try{localStorage.setItem('pw-theme',value);}catch{}}
$('theme').onchange=()=>theme($('theme').value);try{$('theme').value=localStorage.getItem('pw-theme')||'system';}catch{}theme($('theme').value);
pollSources();
