'use strict';
const $=id=>document.getElementById(id);
let token=location.hash.slice(1);
try{if(token)sessionStorage.setItem('pw-session',token);else token=sessionStorage.getItem('pw-session')||'';}catch{}
history.replaceState(null,'',location.pathname);
let listing=null,pending=null,generation=0,controller=null,urls=[],active=null;
const roleNames={reveal:'Abschlussbilder',motif:'Motivvorlage',raster:'Rasterangebote',raster_draft:'Sichtungsentwürfe',background:'Hintergrundangebote'};
function node(tag,text,cls){const el=document.createElement(tag);if(text!==undefined)el.textContent=text;if(cls)el.className=cls;return el;}
function error(text){$('error').textContent=text;$('error').hidden=!text;}
function pause(ms,signal){return new Promise((resolve,reject)=>{
 const abort=()=>{clearTimeout(timer);reject(signal.reason);};
 const timer=setTimeout(()=>{signal?.removeEventListener('abort',abort);resolve();},ms);
 if(signal?.aborted)abort();else signal?.addEventListener('abort',abort,{once:true});
});}
async function request(path,options={}){
 for(let attempt=0;;attempt++){
  options.signal?.throwIfAborted();
  const response=await fetch(path,{...options,headers:{'X-Workspace-Session':token},cache:'no-store'});
  if(response.ok)return response;
  let body;try{body=await response.json();}catch{body={error:'Lokaler Dienst nicht erreichbar. Starter erneut öffnen.'};}
  if(response.status!==503||attempt===4)throw new Error(body.error);
  await pause(250*2**attempt,options.signal);
 }
}
// Leave capacity in the four-operation service for metadata and job changes.
let imageLoads=0;
const imageQueue=[];
function drainImages(){
 while(imageLoads<2&&imageQueue.length){
  const task=imageQueue.shift();
  if(task.signal.aborted){task.reject(task.signal.reason);continue;}
  imageLoads++;
  request(task.path,{signal:task.signal}).then(r=>r.blob()).then(task.resolve,task.reject)
   .finally(()=>{imageLoads--;drainImages();});
 }
}
function imageRequest(path,signal){return new Promise((resolve,reject)=>{imageQueue.push({path,signal,resolve,reject});drainImages();});}
function dispose(){generation++;controller?.abort();controller=new AbortController();for(const url of urls)URL.revokeObjectURL(url);urls=[];$('large').close();}
function sourceStatus(value){return (value.mode==='local'?'Nur lokale Gitstände · Remote-Sicherung nicht bestätigt':value.sync_error||('Remote zuletzt geladen: '+(value.synced_at?new Date(value.synced_at).toLocaleString('de-DE'):'noch nicht synchronisiert')));}
function adopt(value){dispose();listing=value;pending=null;$('load').hidden=true;$('sourceStatus').textContent=sourceStatus(value);error(value.errors.join('\n'));$('jobs').replaceChildren();$('jobList').replaceChildren();if(!value.jobs.length){$('jobs').append(node('option','Keine veröffentlichten Jobs'));$('view').replaceChildren(node('h2','Noch keine veröffentlichten Arbeitsstände'),node('p','Der Produktionsakteur muss Record, Originale und die geprüfte workspace.json gemeinsam in Git sichern. Bestehende WIP werden nicht konvertiert.'));return;}
 for(const job of value.jobs){const label=`${job.title} · ${job.revision} · ${job.ref} (${job.source==='local'?'lokal':'Remote'})`;const opt=node('option',label);opt.value=job.id;$('jobs').append(opt);const button=node('button',job.title,'job');button.dataset.job=job.id;button.append(node('small',`${job.revision} · ${job.ref}${job.conflict?' · Quellenkonflikt':''}`));button.onclick=()=>{$('jobs').value=job.id;open(job.id);};$('jobList').append(button);}
 const retained=value.jobs.find(j=>active&&j.puzzle_id===active.puzzle_id&&j.revision===active.revision&&j.source===active.source);$('jobs').value=(retained||value.jobs[0]).id;open($('jobs').value);}
async function open(id){dispose();const current=generation,signal=controller.signal;active=listing.jobs.find(j=>j.id===id);for(const el of $('jobList').children)el.setAttribute('aria-current',String(el.dataset.job===id));$('view').replaceChildren(node('p','Originalbindungen und Bilder werden geprüft …'));try{const value=await(await request('/api/jobs/'+id,{signal})).json();if(current!==generation)return;const view=$('view');view.replaceChildren(node('h2',value.title));view.append(node('span',value.revision,'badge'),node('span',value.facts.state,'badge'));if(value.facts.test_only)view.append(node('span','Technische Testdaten','badge'));view.append(node('p',value.publication,'hint'),node('p',value.facts.verification,'hint'));if(value.facts.blockers.length){const d=node('details');d.append(node('summary','Überlieferte offene Produktionspunkte'));const ul=node('ul');for(const b of value.facts.blockers)ul.append(node('li',b));d.append(ul);view.append(d);}
 const groups=[['reveal','motif'],['raster'],['raster_draft'],['background']];for(const roles of groups){const assets=value.assets.filter(a=>roles.includes(a.role));if(!assets.length)continue;view.append(node('h3',roles.length===2?'Abschlussbild & Motiv im Vergleich':roleNames[roles[0]],'sectionTitle'));const cards=node('div',undefined,'cards');view.append(cards);for(const asset of assets){const figure=node('figure',undefined,'card'),canvas=node('div',undefined,'canvas'),status=node('p','Original wird geladen …');canvas.append(status);const caption=node('figcaption');caption.append(node('h3',asset.caption),node('p',roleNames[asset.role]+' · unveränderte Quelldatei'));const offered=value.offers.filter(o=>o.asset_ids.includes(asset.id));for(const offer of offered)caption.append(node('p','Angebot: '+offer.label));const button=node('button','Großansicht öffnen');button.disabled=true;caption.append(button);figure.append(canvas,caption);cards.append(figure);
 const retry=node('button','Bild erneut laden');retry.hidden=true;caption.append(retry);
 const load=()=>{retry.hidden=true;status.textContent='Original wird geladen …';status.className='';canvas.replaceChildren(status);
  imageRequest('/api/jobs/'+id+'/assets/'+asset.id,signal).then(blob=>{if(current!==generation)return;const url=URL.createObjectURL(blob);urls.push(url);const img=node('img');img.src=url;img.alt=asset.caption;canvas.replaceChildren(img);button.disabled=false;button.onclick=()=>{$('largeTitle').textContent=asset.caption;$('largeImage').src=url;$('largeImage').alt=asset.caption;$('zoom').value='fit';zoom();$('large').showModal();};}).catch(exc=>{if(current===generation&&exc.name!=='AbortError'){status.textContent=exc.message;status.className='error';retry.hidden=false;}});
 };retry.onclick=load;load();}}
 const details=node('details');details.append(node('summary','Technische Quellenbindungen'));details.append(node('pre',JSON.stringify({commit:value.commit,record:value.record,assets:value.assets,offers:value.offers},null,2)));view.append(details);
 }catch(exc){if(current===generation&&exc.name!=='AbortError')$('view').replaceChildren(node('h2','Arbeitsstand kann nicht geöffnet werden'),node('p',exc.message,'error'),node('p','Quellenveröffentlichung korrigieren und danach neuere Ergebnisse suchen.','hint'));}}
function zoom(){const img=$('largeImage'),value=$('zoom').value;img.classList.toggle('zoomed',value!=='fit');if(value==='fit')img.removeAttribute('width');else img.width=img.naturalWidth*Number(value);}
$('largeImage').onload=zoom;$('zoom').onchange=zoom;$('close').onclick=()=>$('large').close();$('jobs').onchange=()=>open($('jobs').value);
$('refresh').onclick=async()=>{const button=$('refresh');button.disabled=true;try{pending=await(await request('/api/refresh',{method:'POST'})).json();$('sourceStatus').textContent=sourceStatus(pending)+' · aktive Ansicht bleibt unverändert';$('load').hidden=false;error(pending.errors.join('\n'));}catch(exc){error(exc.message);}finally{button.disabled=false;}};
$('load').onclick=()=>{if(pending)adopt(pending);};
function theme(value){document.documentElement.dataset.theme=value;try{localStorage.setItem('pw-theme',value);}catch{}}
$('theme').onchange=()=>theme($('theme').value);try{$('theme').value=localStorage.getItem('pw-theme')||'system';}catch{}theme($('theme').value);
request('/api/jobs').then(r=>r.json()).then(adopt).catch(exc=>error(exc.message));
