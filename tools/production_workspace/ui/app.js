'use strict';
const $=id=>document.getElementById(id);
const sideNames={left:'links',top:'oben',right:'rechts',bottom:'unten'};
let token=location.hash.slice(1);
try{if(token)sessionStorage.setItem('pw-session',token);else token=sessionStorage.getItem('pw-session')||'';}catch{}
history.replaceState(null,'',location.pathname);
let listing=null,pending=null,generation=0,controller=null,urls=[],active=null;
let detail=null,intent={},draft=null,drafts=[];
let inboxState=null, folderDirty=false, starting=false;
let localSelection=null, inboxEpoch=0, viewEdited=0, navSignature=null;
let lastSelection='';
try{lastSelection=sessionStorage.getItem('pw-selection')||'';}catch{}
function rememberSelection(id){
 lastSelection=id;
 try{sessionStorage.setItem('pw-selection',id);}catch{}
}
function selectedId(){return active?.puzzle_id||localSelection;}
function setText(element,text){if(element.textContent!==text)element.textContent=text;}
let remoteExplicit=false;
let remoteFresh=null;
let assetLoads=new Map(),readyImages=new Set();
try{drafts=JSON.parse(localStorage.getItem('pw-briefs')||'[]');if(!Array.isArray(drafts))drafts=[];drafts=drafts.filter(d=>d&&typeof d.id==='string'&&typeof d.brief==='string').slice(-20);}catch{}
function saveDrafts(){try{localStorage.setItem('pw-briefs',JSON.stringify(drafts));}catch{}}
let savedOptions={};
try{savedOptions=JSON.parse(localStorage.getItem('pw-options')||'{}');}catch{}
const personal=PW.options(savedOptions);
function saveOptions(){
 try{localStorage.setItem('pw-options',JSON.stringify(personal));}catch{}
}
$('merge').checked=personal.merge;
$('merge').onchange=()=>{
 personal.merge=$('merge').checked;saveOptions();
 if($('finalMerge'))$('finalMerge').checked=personal.merge;
 updatePrompt();
};
function refreshChoices(){
 if(!detail?.facts.candidates)return;
 const targetAction=['rework','assessment'].includes(intent.action);
 const targets=targetAction?new Set(PW.actionTargets(detail,intent.action).map(asset=>asset.id)):null;
 document.querySelectorAll('[data-rework-shortcut]').forEach(button=>{button.hidden=intent.action==='rework';});
 document.querySelectorAll('[data-readiness]').forEach(status=>{
  const card=detail.facts.candidates[status.dataset.readiness];
  const open=card.findings.filter(row=>!row.eligible||!(intent.findings?.[row.binding]?.accepted??(row.decision?.action==='accept'))).length;
  const ready=!card.missing.length&&!open;
  status.dataset.ready=String(ready);
  status.textContent=ready?'Auswahl möglich':card.missing.length?'Prüfung ausstehend':open===1?'1 offener Befund':open+' offene Befunde';
 });
 document.querySelectorAll('button[data-diagnosis]').forEach(button=>{
  const target=button.dataset.target,kind=button.dataset.diagnosis;
  const crop=detail.facts.candidates[target].diagnostics.crop;
  button.disabled=!readyImages.has(target)||(kind==='crop'&&!readyImages.has(crop.before_asset));
  button.setAttribute('aria-pressed',String(intent.action==='raster_diagnosis'&&intent.diagnosis?.target===target&&intent.diagnosis.kind===kind));
 });
 document.querySelectorAll('button[data-candidate]').forEach(button=>{
  const target=button.dataset.candidate;
  button.disabled=!readyImages.has(target)||(targetAction?!targets.has(target):!PW.choiceReady(detail,target,intent));
  button.textContent=intent.action==='assessment'?'Zur Neubewertung wählen':intent.action==='rework'?'Als Korrekturgrundlage wählen':'Diese Variante wählen';
  button.setAttribute('aria-pressed',String(intent.selection===target));
 });
}
function updatePrompt(){
 refreshChoices();
 const box=$('orderText'),button=$('copyOrder'),status=$('orderStatus');
 if(!box||!button)return;
 const order=currentOrder();
 $('orderFields').hidden=Boolean(order);
 $('orderExecution').hidden=Boolean(order);
 $('receiptInfo').hidden=!order;
 if(order){showOrder(order);return;}
 $('orderSecondary').hidden=true;
 $('orderPreview').hidden=false;
 button.hidden=false;
 const route=PW.orderTarget(detail,intent),executor=personal.executors[route.step];
 $('executor').value=executor||'';
 $('executor').disabled=!executor;
 $('workrootField').hidden=executor!=='Codex';
 $('executorHint').textContent=executor==='ChatGPT'
  ?'Auftrag in einem neuen ChatGPT-Chat senden. Bei Unterbrechung den zuletzt veröffentlichten Stand laden und wieder aufnehmen.'
  :executor==='Codex'?'Auftrag in Codex senden.':'';
 const imageOrder=usesInbox(),final=PW.closing(detail,intent)&&!imageOrder;
 button.textContent=final?(detail.facts.state==='registered'?'Git-Abschluss: Auftrag kopieren':'Endabnahme & Integration: Auftrag kopieren'):'Auftrag kopieren';
 if(imageOrder)button.textContent='Auftrag starten und kopieren';
 if($('finalScope'))$('finalScope').hidden=!final;
 try{
  if(route.error)throw Error(route.error);
  if(detail&&remoteFresh===false)throw Error('Remote nicht aktuell bestätigt. Vor einem Cloudfolgeauftrag die Quellen erfolgreich aktualisieren.');
  if(final){
   const images=PW.finalAssets(detail,intent);
   if([images.raster,images.reveal,images.background].filter(Boolean).some(a=>!readyImages.has(a.id))){
    throw Error('Die Originalbilder der Schlussauswahl zuerst vollständig laden. Bei einem Bildfehler gezielt erneut laden.');
   }
  }
  if(intent.action==='raster_diagnosis'&&intent.diagnosis){
   if(pending&&!pending.jobs.some(job=>job.puzzle_id===active.puzzle_id&&job.ref===active.ref&&job.commit===active.commit)){
    throw Error('Die Rasterquelle hat sich geändert. Neuen Stand laden und den Befund erneut wählen.');
   }
   const cards=detail.facts.candidates,target=intent.diagnosis.target;
   const before=cards[target]?.diagnostics?.crop?.before_asset;
   if(!readyImages.has(target)||(intent.diagnosis.kind==='crop'&&!readyImages.has(before))){
    throw Error('Die gebundenen Originalbilder zuerst vollständig laden.');
   }
  }
  if(imageOrder){
   startBody();box.value='';
   $('orderPreview').hidden=true;
   $('executorHint').textContent='Der genaue Auftrag entsteht beim Start. PW bindet deine Vorgaben, prüft die eingehenden Originale und veröffentlicht den passenden Arbeitsstand.';
  }else{
   box.value=PW.prompt(detail,intent,personal);
   const unpublished=!detail&&inboxState?.drafts?.[draft?.id];
   if(unpublished)box.value+='\n\nNoch unveröffentlichte Produktions-ID: '+unpublished+'.';
  }
  button.disabled=starting;
  status.textContent=final?(personal.merge?'Auftrag bis main und Produktionsabschluss – nach erfüllten Pflichtgates.':'Auftrag bis Draft-PR – kein Merge.'):'';
  status.className='hint';
 }catch(exc){
  box.value='';button.disabled=true;status.textContent=exc.message;status.className='validation';
 }
}
function remember(key,value){
 viewEdited++;
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
 panel.open=expanded||Boolean(grid.width||grid.height||grid.mode||grid.colors);
 function control(group,label,key,choices,placeholder,unit){
  const wrap=node('label',label),input=node(choices?'select':'input');
  if(choices){for(const [id,caption] of choices){const option=node('option',caption);option.value=id;input.append(option);}}
  else{input.type='text';input.inputMode='numeric';input.placeholder=placeholder;}
  input.value=grid[key]||(choices?choices[0][0]:'');
  input[choices?'onchange':'oninput']=()=>{
   grid[key]=input.value;
   if(key==='mode'){
    palette.hidden=grid.mode==='mono';
    if(palette.hidden){delete grid.colors;delete grid.colorAccuracy;colors.value='';precision.value='approx';}
   }
   remember('grid',{...intent.grid,[key]:input.value,...(key==='mode'&&grid.mode==='mono'?{colors:'',colorAccuracy:''}:{})});
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
 const colors=control(palette,'Vordergrundfarben','colors',null,'1–8');colors.className='shortNumber';
 const precision=control(palette,'Farbzahlvorgabe','colorAccuracy',accuracy);
 palette.hidden=grid.mode==='mono';row.append(palette);panel.append(sizes,modes);
 if(detail?.facts.published){
  panel.append(node('p','Vorgefüllte Werte sind Quellkontext. Änderungen werden als neue Wünsche formuliert. Leeren allein hebt keine Vorgabe auf.','hint'));
  removal(modes,'mode','Rastermodus',[['mode',mode]],removed=>{palette.hidden=removed||grid.mode==='mono';});
  removal(palette,'colors','Farbzahl',[['colors',colors]]);
 }
 parent.append(panel);return panel;
}
const parameterKinds={exact:'exakt',approximate:'ungefähr',open:'offen'};
function parameterConstraint(option,axis){
 if(option.constraints)return option.constraints[axis];
 return {kind:option[axis==='foreground_colors'?'foreground_color_constraint':'size_constraint'],
         target:option[axis],minimum:null,maximum:null};
}
function parameterTarget(c,unit=''){
 return c.kind==='open'?'offen':`${parameterKinds[c.kind]} ${c.target}${unit}`;
}
function parameterSummary(section,option){
 for(const [axis,label] of Object.entries(PW.axes)){
  const c=parameterConstraint(option,axis),unit=axis==='foreground_colors'?'':' Zellen';
  section.append(node('p',`${label}: ${parameterTarget(c,unit)} · Untergrenze: ${c.minimum??'keine'} · Obergrenze: ${c.maximum??'keine'}`));
 }
 const mode=option.imports?.[0].mode??option.mode;
 section.append(node('p',`Modus: ${mode==='color'?'farbig':'monochrom'}`));
 const sides=option.derivation?.empty_edge_crop.map(side=>sideNames[side]);
 const features=option.derivation?.protected_features;
 section.append(node('p',`Erlaubte Beschnittseiten: ${sides?.join(', ')||'keine'}.`),
                node('p',`Geschützte Merkmale: ${features?.join('; ')||'keine benannt'}.`));
}
function parameterLabel({option,index}){
 const goals=Object.entries(PW.axes).map(([axis,label])=>`${label} ${parameterTarget(parameterConstraint(option,axis))}`);
 return `Alternative ${index+1} · ${goals.join(' · ')}`;
}
function publishedContext(view,value){
 const p=value.facts.published,section=node('section',undefined,'publishedContext');
 section.append(node('h3','Überlieferte Vorgaben & Motivbriefing'));
 const forMotif=value.facts.candidates&&value.facts.state==='motif_review'&&p.proposed?.length;
 const status=forMotif?'Parametervorschläge zur Motivfreigabe':p.role==='approved'?'Überlieferter freigegebener Parameterkorridor':p.role==='proposed'?'Veröffentlichte Wünsche – Korridor noch nicht freigegeben':'Keine strukturierten Rastervorgaben; siehe Motivbriefing.';
 section.append(node('p',status,'sourceRole'));
 const grid=PW.publishedGrid(value),alternatives=PW.parameterOptions(!forMotif&&p.approved?.length?p.approved:p.proposed);
 if(alternatives.length===1)parameterSummary(section,alternatives[0].option);
 else if(alternatives.length>1){
  for(const entry of alternatives){
   const item=node('details');item.append(node('summary',parameterLabel(entry)));
   parameterSummary(item,entry.option);section.append(item);
  }
 }else if(Object.keys(grid).length){
  const words=[];
  for(const [axis,label] of [['width','Breite'],['height','Höhe']])if(grid[axis])words.push(`${label}: ${grid.sizeAccuracy==='exact'?'exakt':'ungefähr'} ${grid[axis]} Zellen`);
  if(grid.mode)words.push(`Modus: ${grid.mode==='mono'?'monochrom':'farbig'}`);
  if(grid.colors)words.push(`${grid.colorAccuracy==='exact'?'Exakt':'Ungefähr'} ${grid.colors} Vordergrundfarben`);
  section.append(node('p',words.join(' · ')));
 }else if(p.role!=='absent')section.append(node('p','Keine eindeutigen Einzelwerte; vollständige Parameter stehen in den technischen Details.','hint'));
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
 const n=PW.step(value),order=PW.orderStep(value),panel=node('section',undefined,'nextAction');
 const section=node('div');section.id='orderFields';panel.append(section);
 const motifReview=value?.facts.candidates&&value.facts.state==='motif_review';
 const selectionHint='Die gewünschte Variante auf der Bildkarte wählen.';
 section.append(node('h3',PW.closing(value,intent)?(value.facts.state==='registered'?'Git-Abschluss fortsetzen':'Schlussauswahl abnehmen & integrieren'):value?.facts.next_step||'Motiv beschreiben'));
 if(!value)field(section,'Was soll dein Rätsel zeigen?','brief','Zum Beispiel eine reife Erdbeere').id='motifBrief';
 if(order===1)field(section,'Zusätzliche Motivhinweise (optional)','notes','Welche Details, Perspektive oder Stimmung sind dir wichtig?');
 if(!value){
  const label=node('label','Referenzbild (optional)','reference'),input=node('input');input.type='file';input.accept='image/png,image/jpeg';
  input.onchange=async()=>{
   const file=input.files[0],owner=draft;
   delete intent.referenceError;
   remember('reference',null);remember('inputImage',file?.name||'');
   if(!file)return;
   try{
    if(file.size>32*1024*1024||!file.size)throw Error('Referenzbild muss zwischen 1 Byte und 32 MiB groß sein.');
    const digest=await crypto.subtle.digest('SHA-256',await file.arrayBuffer());
    if(draft===owner&&input.files[0]===file)remember('reference',{name:file.name,bytes:file.size,
     sha256:Array.from(new Uint8Array(digest),b=>b.toString(16).padStart(2,'0')).join('')});
   }catch(exc){if(draft===owner&&input.files[0]===file){intent.referenceError=exc.message;updatePrompt();}}
  };
  const hint=node('p',intent.inputImage?'Beim Senden anhängen: '+intent.inputImage:'Die ausgewählte Datei beim Senden des Auftrags anhängen.','hint');
  label.append(input);section.append(label,hint);
  if(intent.inputImage){
   const remove=node('button','Referenz aus dem Entwurf entfernen');
   remove.onclick=()=>{input.value='';input.onchange();hint.textContent='Dateiauswahl aufgehoben.';remove.hidden=true;};
   section.append(remove);
  }
 }
 let parameterChoice;
 if(value){
  const label=node('label','Nächste Aktion'),select=node('select');select.id='nextActionMode';
  const diagnosticStage=['raster_review','raster_ready'].includes(value.facts.state)&&!value.facts.originals?.record?.selected?.raster;
  const canDecide=diagnosticStage&&Object.values(value.facts.candidates||{}).some(({diagnostics:d})=>
   d&&(d.frame&&!d.frame.exception||d.crop&&PW.cropChanges(d.crop).length));
  const actions=[['continue','Fortsetzen / Entscheidung senden'],['rework','Gezielt korrigieren'],['resume','Arbeit wieder aufnehmen']];
  if(PW.actionTargets(value,'assessment').length)
   actions.push(['assessment','Bild neu bewerten']);
  if(canDecide)actions.push(['raster_diagnosis','Technische Rasterentscheidung']);
  if(value.facts.state==='registered')actions.push(['background_change','Separater Hintergrundfolgeauftrag']);
  for(const [id,text] of actions){
   const opt=node('option',text);opt.value=id;select.append(opt);
  }
  if(PW.pendingBackground(value)&&!value.offers.some(o=>o.kind==='background')&&!intent.action){
   intent.action='resume';select.value='resume';
  }
  label.append(select);section.append(label);
  const correction=node('div');correction.hidden=true;field(correction,'Was soll geändert werden?','feedback').id='correctionFeedback';section.append(correction);
  let refreshTargets=()=>{};
  if(value.facts.candidates){
   const base=node('select'),baseLabel=node('label'),baseTitle=node('span');
   refreshTargets=()=>{
    const action=intent.action==='assessment'?'assessment':'rework',targets=PW.actionTargets(value,action);
    baseTitle.textContent=action==='assessment'?'Bild zur Neubewertung':'Korrekturgrundlage';
    const empty=node('option','Bitte wählen');empty.value='';base.replaceChildren(empty);
    for(const asset of targets){const option=node('option',asset.caption);option.value=asset.id;base.append(option);}
    if(['rework','assessment'].includes(intent.action)&&!targets.some(asset=>asset.id===intent.selection)){
     delete intent.selection;delete intent.kind;
    }
    base.value=intent.selection||'';
   };
   base.id='correctionBase';base.onchange=()=>{intent.selection=base.value;intent.kind=value.assets.find(a=>a.id===base.value)?.role;updatePrompt();};
   baseLabel.append(baseTitle,base);correction.append(baseLabel);refreshTargets();
  }
  if(order===3)gridFields(correction,false);
  const diagnosis=node('div');diagnosis.hidden=true;
  const diagnosisTarget=node('p',undefined,'hint');diagnosis.append(diagnosisTarget);
  const frameReason=node('div');const reasonInput=field(frameReason,'Warum ist die Randabweichung für dieses Raster akzeptabel?','frameReason');
  reasonInput.id='frameReason';diagnosis.append(frameReason);section.append(diagnosis);
  select.onchange=()=>{
   if(['rework','assessment'].includes(intent.action)&&!['rework','assessment'].includes(select.value)){
    delete intent.selection;delete intent.kind;
    if($('selectionStatus'))$('selectionStatus').textContent=selectionHint;
   }
   intent.action=select.value;
   if(parameterChoice)parameterChoice.hidden=select.value!=='continue';
   refreshTargets();
   correction.hidden=!['rework','background_change','assessment'].includes(select.value);
   $('correctionFeedback').hidden=select.value==='assessment';
   diagnosis.hidden=select.value!=='raster_diagnosis';
   if(diagnosis.hidden){delete intent.diagnosis;delete intent.frameReason;reasonInput.value='';}
   diagnosisTarget.textContent=intent.diagnosis?`Auftrag für ${intent.diagnosis.target} · Endrevision ${intent.diagnosis.revision}`:'Bitte den Beschnitt oder den Randbefund auf der Bildkarte wählen.';
   frameReason.hidden=intent.diagnosis?.kind!=='frame';
   updatePrompt();
  };
 }

 if(order===1||order===2){gridFields(section,order===2);if(order===2)field(section,'Neue/zusätzliche Wünsche zur Motivvorlage (optional)','parameters','Zum Beispiel Merkmale, die bei der Vereinfachung erhalten bleiben sollen');}
 if(order===4){const d=node('details');d.append(node('summary','Optionaler Kontextwunsch'));field(d,'Kontextwunsch','context');section.append(d);}
 if(motifReview){
  const alternatives=PW.parameterOptions(value.facts.published?.proposed);
  if(alternatives.length>1){
   parameterChoice=node('div');
   const label=node('label','Parameteralternative'),select=node('select');
   const empty=node('option','Bitte wählen');empty.value='';select.append(empty);
   for(const entry of alternatives){
    const item=node('option',parameterLabel(entry));item.value=String(entry.index);select.append(item);
   }
   const description=node('div',undefined,'hint');description.setAttribute('aria-live','polite');
   select.onchange=()=>{
    intent.parameter=select.value===''?null:Number(select.value);
    const entry=alternatives.find(({index})=>index===intent.parameter);
    description.replaceChildren();
    if(entry)parameterSummary(description,entry.option);
    updatePrompt();
   };
   label.append(select);parameterChoice.append(label,description);section.append(parameterChoice);
  }
 }
 if(value?.offers.length||value?.facts.state==='background_review'){
  const selected=node('p',selectionHint,'hint');selected.id='selectionStatus';section.append(selected);
 }
 if(value?.facts.state==='background_review'){
  const none=node('button','Bewusst keinen Hintergrund wählen');none.onclick=()=>choose('none','background',none);none.dataset.choice='none';none.setAttribute('aria-pressed','false');section.append(none);
  if(value.facts.candidates){const standard=node('button','Standardhintergrund wählen');standard.dataset.choice='standard';standard.onclick=()=>choose('standard','background',standard);section.append(standard);}
 }
 if(n===5)section.append(node('p',value.facts.background_choice==='none'?'Bestätigt: bewusst kein Hintergrund.':value.facts.background_choice?'Bestätigte Hintergrundwahl: '+value.facts.background_choice:'Hintergrundentscheidung noch offen.','hint'));
 if(PW.closing(value)){
  const scope=node('div',undefined,'finalScope');scope.id='finalScope';
  const label=node('label'),merge=node('input');merge.type='checkbox';merge.id='finalMerge';merge.checked=personal.merge;
  merge.onchange=()=>{$('merge').checked=merge.checked;$('merge').onchange();};
  label.append(merge,node('span',' Nach erfüllten Pflichtgates nach main mergen und Produktion abschließen'));
  scope.append(label,node('p','Erst der gesendete Auftrag erklärt die Endabnahme und den gewählten Umfang. Klicken, Kopieren und Aktualisieren bestätigen nichts.','hint'));section.append(scope);
 }
 orderControls(view,panel);
}
function orderControls(view,panel){
 const receipt=node('div');receipt.id='receiptInfo';
 const heading=node('h3');heading.id='receiptHeading';
 const state=node('p',undefined,'receiptState');state.id='receiptState';state.setAttribute('role','status');
 const info=node('details');info.id='receiptDetails';
 const reason=node('p');reason.id='receiptReason';
 info.append(node('summary','Details zur Übernahme'),reason);receipt.append(heading,state,info);
 const review=node('a');review.id='receiptSource';review.target='_blank';review.rel='noopener noreferrer';receipt.append(review);
 const execution=node('div',undefined,'orderExecution'),executorLabel=node('label','Auftrag ausführen mit:'),executor=node('select');
 execution.id='orderExecution';executor.id='executor';
 for(const name of PW.executors){const option=node('option',name);option.value=name;executor.append(option);}
 executor.onchange=()=>{
  const phase=PW.promptStep(detail,intent);
  if(!phase||!PW.executors.includes(executor.value))return;
  personal.executors[phase]=executor.value;saveOptions();updatePrompt();
 };
 const workrootLabel=node('label','Codex-Arbeitswurzel'),workroot=node('input');
 workrootLabel.id='workrootField';workroot.id='workroot';workroot.placeholder='Optionaler lokaler Pfad';
 workroot.value=personal.workroot;
 workroot.oninput=()=>{personal.workroot=workroot.value;saveOptions();updatePrompt();};
 executorLabel.append(executor);workrootLabel.append(workroot);execution.append(executorLabel,workrootLabel);
 const destination=node('p',undefined,'hint');destination.id='executorHint';destination.setAttribute('role','status');
 const actions=node('div',undefined,'orderActions'),copy=node('button','Auftrag kopieren','primary');copy.id='copyOrder';
 const status=node('p',undefined,'hint');status.id='orderStatus';status.setAttribute('role','status');
 const preview=node('details',undefined,'orderPreview');preview.id='orderPreview';preview.append(node('summary','Auftrag ansehen'));
 const text=node('textarea');text.id='orderText';text.rows=10;text.readOnly=true;text.setAttribute('aria-label','Auftragstext');preview.append(text);
 copy.onclick=async()=>{
  updatePrompt();if(copy.disabled||starting)return;
  let order=currentOrder();
  if(order?.result){await loadResult(order,true);return;}
  if(!order&&usesInbox()){
   if(!inboxState?.folder){
    $('inbox').open=true;$('inboxFolder').focus();
    status.textContent='Zuerst den privaten Drive-Stammordner speichern. Deine Eingaben bleiben hier erhalten.';return;
   }
   const body=startBody(),epoch=generation;
   const view=$('view');view.inert=true;
   starting=true;copy.disabled=true;
   try{
    const value=await inboxAction('start',body,false);
    if(epoch!==generation)return;
    order=value.orders.find(o=>o.puzzle_id===value.started);
    if(!order||order.result)throw Error('Auftragsstatus hat sich geändert. Bitte den aktuellen Stand prüfen.');
    if(draft)chooseMotif(order.puzzle_id);
    else{viewEdited=0;updatePrompt();}
   }catch(exc){if(epoch===generation)status.textContent=exc.message;return;}
   finally{
    starting=false;view.inert=false;copy.disabled=false;
    if(epoch!==generation||currentOrder())updatePrompt();
   }
   $('copyOrder').focus();
  }
  const target=$('orderText'),message=$('orderStatus'),shown=$('orderPreview'),epoch=generation;
  const stillSelected=()=>epoch===generation&&order?.request_id===currentOrder()?.request_id;
  try{
   await navigator.clipboard.writeText(order?order.prompt:target.value);
   if(stillSelected())message.textContent='Auftrag kopiert.';
  }catch{
   if(!stillSelected())return;
   shown.open=true;target.focus();target.select();message.textContent='Kopieren fehlgeschlagen. Den markierten Auftrag manuell oder erneut kopieren.';
  }
 };
 const secondary=node('div',undefined,'receiptActions');secondary.id='orderSecondary';
 const retry=node('button');retry.id='receiptRetry';retry.onclick=()=>changeReceipt('retry');
 const cancel=node('button','Automatische Übernahme abbrechen');cancel.id='receiptCancel';cancel.onclick=()=>changeReceipt('cancel');
 const explanation=node('p',undefined,'hint');explanation.id='cancelHint';
 secondary.append(retry,cancel,explanation);
 actions.append(copy,status);panel.append(receipt,execution,destination,actions,preview,secondary);view.append(panel);updatePrompt();
}
function choose(id,kind,button){
 viewEdited++;
 if(intent.action==='raster_diagnosis'){
  const mode=$('nextActionMode');mode.value='continue';mode.onchange();
 }
 const label=id==='none'?'kein Hintergrund':detail?.offers.find(o=>o.id===id&&o.kind===kind)?.label||id;
 intent.selection=id;intent.kind=kind;if($('correctionBase'))$('correctionBase').value=id;
 document.querySelectorAll('[data-choice]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.choice===id)));
 if(button.dataset.choice){button.setAttribute('aria-pressed','true');}
 if($('selectionStatus'))$('selectionStatus').textContent=intent.action==='assessment'?`Neubewertung: ${label}.`:intent.action==='rework'?`Korrekturgrundlage: ${label}.`:`Wahl vorgemerkt: ${label}.`;
 refreshFinalPreview();const alternatives=$('backgroundOptions');if(alternatives)alternatives.open=false;updatePrompt();
}
function newDraft(id){
 const mapped=id&&inboxState?.drafts?.[id];
 rememberSelection('');dispose();active=null;detail=null;$('versions').hidden=true;$('motifStatus').textContent='Lokaler Entwurf';
 draft=drafts.find(d=>d.id===id)||{id:crypto.randomUUID(),brief:''};
 if(mapped&&orderById(mapped))draft={...draft,id:crypto.randomUUID()};
 if(!drafts.includes(draft)){drafts.push(draft);drafts=drafts.slice(-20);saveDrafts();}
 intent={brief:draft.brief,notes:draft.notes||'',grid:{...draft.grid},inputImage:draft.inputImage,reference:draft.reference};
 $('view').replaceChildren(node('h2','Neues Motiv'));progress($('view'),null);workflow($('view'),null);renderDrafts();
 $('jobs').selectedIndex=-1;
}
function renderDrafts(){
 const list=$('draftList');list.replaceChildren();if(!drafts.length)return;
 const label=node('label','Gespeicherten Motivtext als Entwurf öffnen'),select=node('select');
 const empty=node('option','Motivtext wählen …');empty.value='';select.append(empty);
 for(const d of drafts){const option=node('option',(d.brief.trim()||'Unbenannter Motivtext').slice(0,60));option.value=d.id;select.append(option);}
 select.value=draft?.id||'';select.onchange=()=>{if(select.value)newDraft(select.value);};label.append(select);list.append(label);
 if(draft){
  const remove=node('button','Entwurf verwerfen','discard');remove.onclick=()=>{
   drafts=drafts.filter(d=>d.id!==draft.id);draft=null;saveDrafts();renderDrafts();
   if(navigationRows().length)chooseMotif(navigationRows()[0].id);else $('view').replaceChildren(node('p','Über „Neues Motiv“ beginnen oder einen gespeicherten Motivtext ausdrücklich öffnen.'));
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
function dispose(){$('view').inert=false;localSelection=null;viewEdited=0;closeRemoval();generation++;controller?.abort();controller=new AbortController();for(const url of urls)URL.revokeObjectURL(url);urls=[];assetLoads=new Map();readyImages=new Set();$('large').close();}
function sourceStatus(value){
 const age=value.synced_at?new Date(value.synced_at).toLocaleString('de-DE'):'unbekannt';
 const source=value.mode==='local'?'Nur lokale Gitstände · Remote-Sicherung nicht bestätigt':!value.remote_confirmed?['Remote nicht aktuell bestätigt','letzter Cache: '+age,value.sync_error].filter(Boolean).join(' · '):'Remote zuletzt geladen: '+age;
 return [source,value.completion?.note].filter(Boolean).join(' · ');
}
function currentMotif(){return listing?.motifs.find(m=>m.puzzle_id===selectedId());}
function versionControls(motif,id){
 $('versions').hidden=false;$('version').replaceChildren();
 const empty=node('option','Version bewusst wählen');empty.value='';$('version').append(empty);
 for(const [n,v] of motif.versions.entries()){const option=node('option',`${v.current?'Aktuell · ':''}${v.phase} · ${v.revision}`);option.value=String(n);$('version').append(option);}
 const index=motif.versions.findIndex(v=>v.sources.includes(id));$('version').value=index<0?'':String(index);
 $('jobSource').replaceChildren();
 const bound=listing.jobs.find(j=>j.id===id),placeholder=node('option',bound?`Aktiv: ${bound.source==='local'?'Lokal':'Remote'} · ${bound.commit.slice(0,8)} · Quelle wählen`:'Quelle wählen');placeholder.value='';$('jobSource').append(placeholder);
 const version=motif.versions[index];$('versionOrigin').textContent=version?.source_label||'';
 if(version)for(const jid of version.sources){const job=listing.jobs.find(j=>j.id===jid),option=node('option',`${job.source==='local'?'Lokal':'Remote'} · ${job.ref==='main'?'main':'Produktionsbranch'} · ${job.commit.slice(0,8)}`);option.value=jid;$('jobSource').append(option);}
 $('jobSource').value=remoteExplicit?id||'':'';$('jobSource').disabled=!version;setText($('motifStatus'),currentOrder()?orderStatus(currentOrder()):motif.status);$('versionNotes').textContent=motif.notes.join(' ');
}
function chooseMotif(puzzleId){
 const motif=listing?.motifs?.find(m=>m.puzzle_id===puzzleId),order=orderById(puzzleId);
 if(!motif&&!order)return;
 rememberSelection(puzzleId);$('jobs').value=puzzleId;
 $('jobs').title=$('jobs').selectedOptions?.[0]?.title||motif?.label||orderTitle(order);
 if(motif?.current_job)return open(motif.current_job);
 dispose();active=null;localSelection=puzzleId;draft=null;detail=null;intent={};remoteExplicit=false;renderDrafts();
 const view=$('view');view.replaceChildren(node('h2',motif?.title||orderTitle(order)));
 if(motif){
  versionControls(motif,null);
  view.append(node('p','Aktuelle Übergabe nicht eindeutig. Bitte eine Version wählen.','validation'),node('p',motif.notes.join(' '),'hint'));
 }else{
  $('versions').hidden=true;setText($('motifStatus'),orderStatus(order));
  const completed=completedIn(listing,puzzleId);
  if(!completed&&order.phase==='reveal'&&!order.work_head)progress(view,null);
  const origin=completed?'In main abgeschlossen · lokale Nachbereitung':order.result?'Veröffentlichung bestätigt':
   order.work_head?'Der gebundene Gitstand ist hier noch nicht geladen.':'Erster Bildauftrag · noch nicht veröffentlicht';
  view.append(node('p',origin,'sourceRole'));
  if(order.brief)view.append(node('h3','Gebundenes Motivbriefing'),node('p',order.brief,'briefText'));
 }
 if(order)receiptPanel(view);
}
function receiptPanel(view){
 const panel=node('section',undefined,'nextAction'),fields=node('div');
 fields.id='orderFields';panel.append(fields);orderControls(view,panel);
}
function completedIn(source,id){return source?.completion?.confirmed&&source.completion.completed_ids.includes(id);}
function navigationRows(){
 const rows=new Map((listing?.motifs||[]).map(m=>[m.puzzle_id,{id:m.puzzle_id,label:m.label||m.title||m.puzzle_id}]));
 for(const order of inboxState?.orders||[]){
  const id=order.puzzle_id,motif=listing?.motifs?.find(m=>m.puzzle_id===id);
  const remainder=completedIn(listing,id);
  const title=motif?.title||orderTitle(order),status=orderStatus(order);
  const short=title.length>40?title.slice(0,39)+'…':title;
  rows.set(id,{id,label:short+' – '+(remainder?'Abschlussrest':status),title:title+' – '+status,remainder});
 }
 return [...rows.values()];
}
function renderNavigation(){
 const rows=navigationRows(),signature=JSON.stringify(rows),select=$('jobs');
 if(signature!==navSignature){
  navSignature=signature;select.replaceChildren();
  const rest=node('optgroup');rest.label='Abschlussnachbereitung';
  for(const row of rows){
   const option=node('option',row.label);option.value=row.id;option.title=row.title||row.label;
   (row.remainder?rest:select).append(option);
  }
  if(rows.some(row=>row.remainder))select.append(rest);
  if(!rows.length){const empty=node('option','Keine offenen Produktionen');empty.value='';select.append(empty);select.value='';}
 }
 const selected=rows.find(row=>row.id===selectedId());select.title=selected?.title||selected?.label||'Offene Produktionen';
 if(selected)select.value=selected.id;else if(draft)select.selectedIndex=-1;
 return rows;
}
function adopt(value,loadedJob=null){
 const keepDraft=draft?.id,keepId=selectedId()||lastSelection;
 const completed=!keepDraft&&value.completion?.confirmed&&value.completion.completed_ids.includes(keepId);
 const notice=completed?'Die bisherige Produktion ('+keepId+') ist in main registriert. '+(value.motifs.length?'Die nächste offene Produktion ist ausgewählt.':'Die aktive Liste enthält keine offenen Produktionen. Gespeicherte Motivtexte bleiben erhalten.') : '';
 listing=value;pending=null;$('load').hidden=true;$('sourceStatus').textContent=[sourceStatus(value),notice].filter(Boolean).join(' · ');error(value.errors.join('\n'));
 const rows=renderNavigation();
 if(keepDraft)return;
 if(!rows.length){
  dispose();active=null;detail=null;intent={};remoteExplicit=false;
  $('versions').hidden=true;$('motifStatus').textContent='';$('view').replaceChildren(node('h2','Keine offenen Produktionen'),node('p',drafts.length?'Über „Neues Motiv“ beginnen oder einen gespeicherten Motivtext ausdrücklich öffnen.':'Über „Neues Motiv“ beginnen.'));
  return;
 }
 if(loadedJob)return open(loadedJob.id,false,loadedJob.detail);
 return chooseMotif(rows.find(r=>r.id===keepId)?.id||rows.find(r=>!r.remainder)?.id||rows[0].id);
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
function findingControls(parent,value,target){
 const card=value.facts.candidates?.[target];if(!card)return;
 for(const instruction of card.instructions||[])parent.append(node('p','Geltende Vorgabe: '+instruction));
 for(const reason of card.missing)parent.append(node('p',reason,'validation'));
 for(const row of card.findings){
  const group=node('fieldset',undefined,'finding'),info=node('details'),state=node('p',undefined,'findingState');
  const legend=node('legend');legend.append(node('span',row.criterion,'criterion'),node('span',row.description));group.append(legend);
  const facts=node('dl');
  for(const [label,text] of [['Eigenschaft',row.properties],['Kontext',row.context],['Wirkung',row.effect],['Umfang',row.extent],['Geprüft mit',row.method]])facts.append(node('dt',label),node('dd',text));
  info.append(node('summary','Befund erklären'),facts);
  group.append(info,state);parent.append(group);
  if(!row.eligible){state.textContent=row.result+' · Voraussetzung offen';continue;}
  const check=node('input'),label=node('label'),treatment=node('textarea'),textLabel=node('label','Umgang mit diesem Befund');
  check.type='checkbox';treatment.maxLength=4096;treatment.rows=2;
  const stored=row.decision,edit=intent.findings?.[row.binding];
  check.checked=edit?.accepted??(stored?.action==='accept');
  treatment.value=edit?.treatment??stored?.treatment??'';
  const source=stored?.source?'Übernommen von '+stored.source.target:stored?.action==='accept'?'Annahme veröffentlicht':stored?.action==='revoke'?'Widerruf veröffentlicht':'Offen';
  function show(){const changed=intent.findings?.[row.binding];state.textContent=row.result+' · '+source+(changed?(check.checked?' · Annahme vorgemerkt':stored?.action==='accept'?' · Widerruf vorgemerkt':' · offen'):'');}
  function save(){
   (intent.findings??={})[row.binding]={accepted:check.checked,treatment:treatment.value};
   show();updatePrompt();
  }
  check.onchange=()=>{if(check.checked&&!treatment.value.trim())treatment.value=stored?.treatment||'Unverändert beibehalten';save();};
  treatment.oninput=save;
  treatment.onblur=()=>{if(check.checked&&!treatment.value.trim()){treatment.value=stored?.treatment||'Unverändert beibehalten';save();}};
  label.append(check,node('span',' Abweichung annehmen'));textLabel.append(treatment);group.append(label,textLabel);show();
 }
}
function rasterDiagnosis(parent,value,asset,card){
 const {frame,crop}=card.diagnostics;
 const diagnosticStage=['raster_review','raster_ready'].includes(value.facts.state)&&!value.facts.originals.record.selected.raster;
 const button=(kind,label)=>{
  const option=node('button',label);option.dataset.diagnosis=kind;option.dataset.target=asset.id;option.disabled=true;
  option.onclick=()=>{
   const mode=$('nextActionMode');
   if(intent.diagnosis?.target!==asset.id||intent.diagnosis?.kind!==kind){delete intent.frameReason;$('frameReason').value='';}
   intent.diagnosis={kind,target:asset.id,sha:card.definition_sha256,revision:card.revision,parameters:crop?.parameters_sha256};
   mode.value='raster_diagnosis';mode.onchange();
   (kind==='frame'?$('frameReason'):$('copyOrder')).focus();
  };parent.append(option);
 };
 if(!card.qualified)parent.append(node('p','Sichtungsentwurf – nicht integrationsbereit','validation'));
 if(frame){
  const detail=node('details',undefined,'finding');
  detail.append(node('summary','H-01 · Randregel: nicht erfüllt'),
    node('p',`Kandidat ${asset.id}, Endrevision ${card.revision}, ${card.width} × ${card.height} Zellen`),
    node('p',['left','right','top','bottom'].map(side=>`${sideNames[side]} ${frame.edges[side]?'belegt':'leer'}`).join(' · ')),
    node('p','Betroffene Achsen: '+frame.axes.map(axis=>PW.axes[axis]).join(', ')),
    node('p','Definitions-SHA-256: '+card.definition_sha256));
  parent.append(detail);
  if(frame.exception){
   const evidence=node('details',undefined,'finding');const e=frame.exception;
   evidence.append(node('summary','Gebundene technische frame-Ausnahme'),
    node('p',`${e.actor} · ${e.timestamp_utc}`),node('p',e.statement),
    node('p',`Beleg ${e.evidence.file} · SHA-256 ${e.evidence.sha256}`));
   parent.append(evidence);
  }else if(diagnosticStage)button('frame','Technische frame-Ausnahme erklären');
 }
 if(crop){
  const comparison=node('details',undefined,'finding');comparison.open=true;
  const d=size=>`${size.width} × ${size.height}`;
  comparison.append(node('summary','Gemessener Außenbeschnitt'),
   node('p',`Vorher ${d(crop.before)} → nachher ${d(crop.after)} Zellen`),
   node('p',Object.entries(crop.removed).filter(([,n])=>n).map(([side,n])=>
    `${sideNames[side]} ${n} ${['left','right'].includes(side)?'Spalte(n)':'Zeile(n)'}`).join(' · ')+` · ${crop.removed_cells} leere Zellen`));
  const limits=Object.keys(crop.changes).map(axis=>{
   const c=crop.constraints[axis];
   return `${PW.axes[axis]}: Ziel ${c.target}, Minimum ${c.minimum}, Maximum ${c.maximum??'offen'}`;
  });
  if(limits.length)comparison.append(node('p',`Alternative ${crop.parameter+1} · ${limits.join(' · ')}`),
    node('p',`Vorschlag · ${PW.cropChanges(crop).join(' · ')} · alle übrigen Werte bleiben gültig.`));
  parent.append(comparison);
  if(diagnosticStage&&limits.length)button('crop','Korridor ändern und Rasterwahl beabsichtigen');
 }
}
function assetCard(value,id,asset,selectable=true){
 const current=generation,signal=controller.signal;
 const figure=node('figure',undefined,'card'),canvas=node('div',undefined,'canvas'),status=node('p','Original wird geladen …');
 canvas.dataset.role=asset.role;canvas.append(status);
 const caption=node('figcaption');caption.append(node('h3',asset.caption));
 const card=value.facts.candidates?.[asset.id];
 const offered=value.offers.some(o=>o.asset_ids.includes(asset.id));
 if(card?.diagnostics)rasterDiagnosis(caption,value,asset,card);
 if(card&&offered&&selectable){
  const status=node('p',undefined,'readiness');status.dataset.readiness=asset.id;caption.append(status);
 }
 if(selectable||PW.step(value)===5||asset.role!=='background')findingControls(caption,value,asset.id);
 const choices=[];
 if(selectable)for(const offer of value.offers.filter(o=>o.asset_ids.includes(asset.id)&&PW.step(value)<5)){
  if(!card||offer.label!==asset.caption)caption.append(node('p',offer.label));
  const select=node('button','Diese Variante wählen');select.dataset.choice=offer.id;if(value.facts.candidates)select.dataset.candidate=asset.id;select.setAttribute('aria-pressed',String(intent.selection===offer.id));select.disabled=true;select.onclick=()=>choose(offer.id,offer.kind,select);caption.append(select);choices.push(select);
 }
 if(card&&selectable&&(offered||asset.role==='raster_draft')){
  const correction=node('button','Korrigieren');correction.dataset.reworkShortcut='true';
  correction.onclick=()=>{
   const mode=$('nextActionMode');mode.value='rework';mode.onchange();
   choose(asset.id,asset.role==='raster_draft'?'raster':asset.role,correction);
   $('correctionFeedback').focus();
  };caption.append(correction);
 }
 const button=node('button','Großansicht öffnen');button.disabled=true;caption.append(button);
 figure.append(canvas,caption);
 const beforeId=card?.diagnostics?.crop?.before_asset;
 if(beforeId){
  const before=value.assets.find(a=>a.id===beforeId);
  if(before)figure.append(assetCard(value,id,before,false));
 }
 const retry=node('button','Bild erneut laden');retry.hidden=true;caption.append(retry);
 const load=async()=>{
  retry.hidden=true;status.textContent='Original wird geladen …';status.className='';canvas.replaceChildren(status);
  try{
   const url=await assetURL(id,asset,current,signal);if(current!==generation)return;
   const img=node('img');img.src=url;img.alt=asset.caption;
   if(typeof img.decode==='function')await img.decode();
   if(current!==generation)return;
   canvas.replaceChildren(img);readyImages.add(asset.id);button.disabled=false;choices.forEach(b=>b.disabled=false);
   button.onclick=()=>{$('largeTitle').textContent=asset.caption;$('largeImage').dataset.role=asset.role;$('largeImage').src=url;$('largeImage').alt=asset.caption;$('zoom').value='fit';zoom();$('large').showModal();};
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
 const roles=[['raster','Gewähltes Raster'],['reveal','Zugehöriges Abschlussbild']];
 if(value.facts.candidates&&value.facts.originals.record.selected.motif)roles.push(['motif','Gewählte Motivvorlage']);
 for(const [role,label] of roles){
  const slot=node('div');slot.append(node('h4',label));
  const assets=value.assets.filter(a=>a.id===(value.facts.composition?.[role]??value.facts.originals?.record?.selected?.[role])&&a.role===role);
  if(assets.length===1)slot.append(assetCard(value,id,assets[0],false));else slot.append(node('p','Originalbindung fehlt oder ist uneindeutig.','validation'));
  cards.append(slot);
 }
 const background=node('div',undefined,'summaryBackground');background.id='summaryBackground';cards.append(background);
 section.append(cards);findingControls(section,value,'@selection');view.append(section);refreshFinalPreview();
}
function refreshFinalPreview(){
 const slot=$('summaryBackground');if(!slot||!detail||!active)return;
 slot.replaceChildren(node('h4',detail.facts.state==='background_review'?'Vorgemerkter Hintergrund':'Bestätigter Hintergrund'));
 try{
  const result=PW.finalAssets(detail,intent);
  if(['none','standard'].includes(result.choice))slot.append(node('p',result.choice==='none'?'Bewusst kein Hintergrund':'Standardhintergrund','noneChoice'));
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
async function open(id,explicit=false,loadedDetail=null){
 dispose();draft=null;detail=null;intent={};remoteExplicit=explicit;renderDrafts();
 const current=generation,signal=controller.signal;active=listing.jobs.find(j=>j.id===id);$('jobs').value=active.puzzle_id;versionControls(currentMotif(),id);
 $('view').replaceChildren(node('p','Originalbindungen und Bilder werden geprüft …'));
 try{
  const value=loadedDetail||await(await request('/api/jobs/'+id,{signal})).json();if(current!==generation)return;
  detail=value;
  const view=$('view');view.replaceChildren(node('h2',value.title));
  view.append(node('span',({brief_ready:'Briefing bereit',reveal_review:'Abschlussbilder zur Wahl',motif_review:'Motivvorlage zur Freigabe',motif_approved:'Rasterproduktion beauftragt',raster_review:'Rasterprüfung offen',raster_ready:'Geprüfte Raster zur Wahl',background_review:'Kontextzeichnungen zur Wahl',content_ready:'Bereit zur Endabnahme',editorially_approved:'Endabnahme liegt vor',registered:'Lokal registriert'})[value.facts.state]||value.facts.state,'badge'));
  if(value.facts.test_only)view.append(node('span','Technische Testdaten','badge'));
  progress(view,value);metadata(view,value);
  if(value.facts.published)publishedContext(view,value);
  // Original pending gates are historical context, not fresh reader failures.
  const points=[];
  for(const blocker of value.facts.blockers){
   const key=blocker.split(':',1)[0];
   if(key==='final_editorial'){
    if(['background_review','content_ready'].includes(value.facts.state))points.push(['Die Endabnahme wird erst mit dem gesendeten Schlussauftrag erteilt.','hint']);
   }else if(key==='background_choice'){
    if(value.facts.state==='background_review')points.push(['Wähle einen Hintergrund oder verzichte ausdrücklich darauf.','hint']);
   }else if(key==='storage'){
    if(!value.source_url)points.push(['Remote-Veröffentlichung noch nicht bestätigt. Originale sichern und Quellen aktualisieren.','validation']);
   }else points.push([blocker,'validation']);
  }
  if(points.length){
   const issues=node('section',undefined,'openPoints');issues.append(node('h3','Noch zu entscheiden oder zu prüfen'));
   for(const [text,style] of points)issues.append(node('p',text,style));view.append(issues);
  }
  const final=PW.closing(value);
  if(final)finalOverview(view,value,id);
  const groups=final?(value.facts.state==='background_review'?[['background']]:[]):[['reveal','motif'],['raster'],['raster_draft']];
  let gallery=view;
  if(value.facts.state==='background_review'){gallery=node('details',undefined,'backgroundOptions');gallery.id='backgroundOptions';gallery.open=true;gallery.append(node('summary','Kontextzeichnungen vergleichen & wählen'));view.append(gallery);}
  const shownComparisons=new Set();
  const comparisonAssets=new Set(Object.values(value.facts.candidates||{}).map(c=>c.diagnostics?.crop?.before_asset));
  for(const roles of groups){
   const assets=value.assets.filter(a=>{
    if(!roles.includes(a.role)||comparisonAssets.has(a.id))return false;
    if(!value.facts.candidates&&['reveal','motif'].includes(a.role)){const key=a.role+':'+a.location.sha256;if(shownComparisons.has(key))return false;shownComparisons.add(key);}
    if(a.role==='raster'&&PW.step(value)===3&&value.offers.some(o=>o.kind==='raster')&&!value.offers.some(o=>o.kind==='raster'&&o.asset_ids.includes(a.id)))return false;
    return true;
   });
   if(!assets.length)continue;
   gallery.append(node('h3',roles.length===2?'Abschlussbild & Motiv im Vergleich':roleNames[roles[0]],'sectionTitle'));
   const cards=node('div',undefined,'cards');gallery.append(cards);for(const asset of assets)cards.append(assetCard(value,id,asset));
  }
  workflow(view,value);technicalDetails(view,value);removalAction(view,value);
  reconcileResult();
 }catch(exc){
  if(current!==generation||exc.name==='AbortError')return;
  detail=null;
  const view=$('view');view.replaceChildren(node('h2',currentMotif()?.title||'Arbeitsstand kann nicht geöffnet werden'),node('p',exc.message,'error'));
  if(currentOrder())receiptPanel(view);
 }
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
   if(!local&&plan.external_assets)confirm.textContent='Warte auf den bestätigten Releaseabbau …';
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
  body.append(node('p','Der lokale Branch bleibt zunächst erhalten; offene Lieferungen bleiben in der aktiven Auswahl sichtbar.','hint'),label,button);
 }
 body.append(node('p','Maininhalte und weitere lokale Stände bleiben erhalten. In main registrierte Rätsel sind aus der aktiven Produktion ausgeblendet.','hint'));
 if(!dialog.open)dialog.showModal();
}
$('removalClose').onclick=()=>{if(!removalBusy)closeRemoval();};
$('removal').oncancel=e=>{if(removalBusy)e.preventDefault();else closeRemoval();};
let pollTimer=null,sourceRequest=0;
async function checkSources(value){
 clearTimeout(pollTimer);
 const update=value.update||{state:'done'};
 if(update.state!=='running'){
  remoteFresh=value.mode==='remote'?value.remote_confirmed===true&&update.state!=='error':null;
  updatePrompt();
 }
 $('refresh').disabled=update.state==='running';
 if(update.state==='running'){$('sourceStatus').textContent=`Arbeitsstände werden gesucht · ${Math.floor(update.elapsed_seconds||0)} Sekunden`;}
 else if(!listing&&value.snapshot){adopt(value);}
 else if(listing&&value.snapshot!==listing.snapshot&&value.snapshot!==pending?.snapshot){
  pending=value;$('load').hidden=false;$('sourceStatus').textContent=sourceStatus(value)+' · aktive Ansicht bleibt unverändert';error(value.errors.join('\n'));updatePrompt();
 }
 if(update.state==='error'){
  if(value.snapshot===listing?.snapshot){pending=null;$('load').hidden=true;}
  else if(value.snapshot===pending?.snapshot)pending=value;
  $('sourceStatus').textContent=sourceStatus(value);
  error([update.error||'Aktualisierung fehlgeschlagen. Erneut suchen.',...value.errors].filter((msg,i,all)=>all.indexOf(msg)===i).join('\n'));
 }
 if(update.state==='running')pollTimer=setTimeout(pollSources,1000);
}
async function pollSources(){const epoch=++sourceRequest;try{const value=await(await request('/api/jobs')).json();if(epoch===sourceRequest)await checkSources(value);}catch(exc){if(epoch===sourceRequest){$('refresh').disabled=false;error(exc.message);}}}
$('refresh').onclick=async()=>{const epoch=++sourceRequest,button=$('refresh');clearTimeout(pollTimer);button.disabled=true;try{const value=await(await request('/api/refresh',{method:'POST'})).json();if(epoch===sourceRequest)await checkSources(value);}catch(exc){if(epoch===sourceRequest){error(exc.message);button.disabled=false;}}};
$('load').onclick=()=>{if(pending)adopt(pending);};
function theme(value){document.documentElement.dataset.theme=value;try{localStorage.setItem('pw-theme',value);}catch{}}
$('theme').onchange=()=>theme($('theme').value);try{$('theme').value=localStorage.getItem('pw-theme')||'system';}catch{}theme($('theme').value);
$('view').oninput=$('view').onchange=()=>{viewEdited++;};

function currentOrder(){
 return orderById(selectedId());
}
function orderById(id){return inboxState?.orders.find(order=>order.puzzle_id===id);}
function usesInbox(){
 const route=PW.orderTarget(detail,intent);
 return !route.error&&route.inbox&&personal.executors[route.step]==='ChatGPT';
}
function startBody(){
 if(!listing||pending)throw Error('Zuerst den aktuellen Quellenstand laden.');
 const route=PW.orderTarget(detail,intent);
 if(route.error)throw Error(route.error);
 if(!route.inbox)throw Error('Diese Handlung verwendet den regulären Folgeauftrag.');
 if(detail&&intent.action==='rework'&&!intent.feedback?.trim())throw Error('Bitte die gewünschte Korrektur beschreiben.');
 const action=intent.action||'continue',resume=action==='resume',candidate=resume?'':(intent.selection||'');
 if(!detail&&!intent.brief?.trim())throw Error('Bitte zuerst dein Motiv beschreiben.');
 if(detail&&action==='continue'&&['reveal_review','raster_review','raster_ready'].includes(detail.facts.state)&&!candidate)
  throw Error('Bitte die gewünschte Variante wählen. Ein ausstehendes Angebot über „Arbeit wieder aufnehmen“ fortsetzen.');
 if(candidate&&!readyImages.has(candidate))throw Error('Die gewählte Variante zuerst vollständig laden.');
 if(detail&&action==='continue'&&candidate&&!PW.choiceReady(detail,candidate,intent))throw Error('Offene Voraussetzungen für '+candidate+'.');
 if(intent.inputImage&&!intent.reference)throw Error(intent.referenceError||'Die Referenzdatei für die Byteprüfung auswählen.');
 const job=active?.puzzle_id||inboxState?.drafts?.[draft?.id];
 const inputs=PW.inboxInputs(detail,intent,action==='rework'?'correction':action);
 if(resume&&detail?.facts.state==='reveal_review')inputs.parameters='';
 return {snapshot:listing.snapshot,jid:active?.id||'',draft_id:draft?.id||'',candidate,action,inputs,
  findings:JSON.stringify(PW.inboxFindings(detail,intent)),expected:currentOrder()?.request_id||inboxState?.generations?.[job]||''};
}
function orderTitle(order){
 return order?.inputs?.brief?.trim().split('\n')[0]||order?.brief?.trim().split('\n')[0]||order?.puzzle_id||'';
}
function orderStatus(order){
 if(order.step==='cleanup')return order.paused?'Veröffentlicht · Bereinigung offen':'Veröffentlicht · Eingang wird bereinigt';
 if(order.result)return 'Veröffentlichung bestätigt';
 if(order.step==='blocked')return 'Lieferung gesperrt';
 if(order.step==='stale')return 'Produktionsstand geändert';
 if(order.paused)return 'Übernahme unterbrochen';
 return ({scan:'Wartet auf Bilder',stage:'Dateien werden geprüft',build:'Übernahme läuft',publish:'Veröffentlichung läuft'})[order.step]||'Empfang prüfen';
}
function showOrder(order){
 const phase={reveal:'Abschlussbilder',motif:'Motivvorlage',background:'Kontextzeichnungen'}[order.phase]||'Bildauftrag';
 const action={offer:'Angebot',assessment:'Neubewertung',correction:'Korrektur'}[order.intent]||'Auftrag';
 setText($('receiptHeading'),phase+' · '+action);
 setText($('receiptState'),orderStatus(order));setText($('motifStatus'),orderStatus(order));
 $('receiptDetails').hidden=!order.status;setText($('receiptReason'),order.status||'');
 const cancel=['scan','stage','stale','blocked'].includes(order.step);
 const retry=order.paused&&['scan','stage','build','publish','cleanup'].includes(order.step);
 const source=pending||listing,match=order.result&&resultJob(source,order);
 const loaded=detail&&match&&active?.id===match.id;
 const review=$('receiptSource');
 review.hidden=!order.result||Boolean(match)||completedIn(source,order.puzzle_id);
 if(!review.hidden){
  const tip=source?.sources?.find(s=>s.source==='remote'&&s.ref==='content/pw/'+order.puzzle_id)?.commit;
  const compare=source?.remote_confirmed&&tip&&tip!==order.result.head;
  review.href='https://github.com/venomenon328/picross/'+(compare?'compare/'+order.result.head+'...'+tip:'commit/'+order.result.head);
  setText(review,compare?'Import und aktuellen Arbeitsstand auf GitHub vergleichen':'Bestätigten Import auf GitHub ansehen');
 }
 const copy=$('copyOrder');copy.hidden=Boolean(order.result&&loaded);
 copy.disabled=starting||busyReceipt===order.request_id;
 setText(copy,order.result?'Veröffentlichten Arbeitsstand laden':'Auftrag kopieren');
 const preview=$('orderPreview');preview.hidden=Boolean(order.result);
 if($('orderText').value!==order.prompt)$('orderText').value=order.prompt||'';
 setText($('executorHint'),order.result?(loaded?'Der bestätigte Gitstand ist geöffnet.':'Quellen aktualisieren. Bleibt die Zuordnung offen, den bestätigten Import prüfen und den Produktionsbranch mit der zuständigen Person klären.'):
  order.paused?(['build','publish'].includes(order.step)?'Die Veröffentlichung ist bereits begonnen. Prüfe die Quelle und setze dieselbe Übernahme fort.':'Prüfe die Details zur Übernahme.'):'Der Auftrag ist für ChatGPT gespeichert. Du kannst ihn erneut kopieren.');
 $('orderSecondary').hidden=!cancel&&!retry;
 const recovery=$('receiptRetry');recovery.hidden=!retry;recovery.disabled=copy.disabled;
 setText(recovery,order.result?'Bereinigung fortsetzen':'Übernahme fortsetzen');
 recovery.className=copy.hidden?'primary':'';
 const stop=$('receiptCancel');stop.hidden=!cancel;stop.disabled=copy.disabled;
 $('cancelHint').hidden=!cancel;
 setText($('cancelHint'),'Ein Abbruch beendet den Empfang in PW. Chat, Originale und Gitstand bleiben erhalten. Anschließend kannst du Vorgaben ändern oder zu Codex wechseln.');
}
let busyReceipt=null;
function receiptBinding(order){return {request_id:order.request_id,puzzle_id:order.puzzle_id};}
async function changeReceipt(action){
 const order=currentOrder();if(!order||busyReceipt)return;
 const name=currentMotif()?.title||orderTitle(order);
 if(action==='cancel'&&!confirm('Automatische Übernahme für „'+name+'“ abbrechen? Der bisherige Auftrag wird nicht mehr angenommen. Ein laufender Chat läuft weiter. Originale und veröffentlichte Stände bleiben erhalten.'))return;
 if(action==='cancel'&&!order.work_head&&order.draft_id)saveReceiptDraft(order,order.draft_id);
 const epoch=generation;
 busyReceipt=order.request_id;showOrder(order);
 try{
  await inboxAction(action,receiptBinding(order));
  if(epoch===generation&&action==='retry')setText($('orderStatus'),'Fortsetzung angefordert.');
  if(epoch===generation&&action==='cancel'&&detail)$('executor').focus();
 }catch(exc){if(epoch===generation)setText($('orderStatus'),exc.message);}
 finally{busyReceipt=null;if(currentOrder()&&$('copyOrder'))showOrder(currentOrder());}
}
function saveReceiptDraft(order,id){
 if(drafts.some(d=>d.id===id))return;
 const input=order.inputs||{},grid={},notes=[input.notes];
 for(const line of input.grid||[]){
  const axis=line.match(/^(Breite|Höhe): (exakt|ungefähr) (\d+) Zellen\.$/);
  const colors=line.match(/^Farbzahl: (exakt|ungefähr) (eine|\d+) Vordergrundfarben?\.$/);
  if(axis){
   grid[axis[1]==='Breite'?'width':'height']=axis[3];grid.sizeAccuracy=axis[2]==='exakt'?'exact':'approx';
  }else if(colors){
   grid.colors=colors[2]==='eine'?'1':colors[2];grid.colorAccuracy=colors[1]==='exakt'?'exact':'approx';
  }else if(line==='Rastermodus: monochrom.'||line==='Rastermodus: farbig.')grid.mode=line.includes('monochrom')?'mono':'color';
  else notes.push(line);
 }
 drafts.push({id,brief:input.brief||order.brief||'',notes:notes.filter(Boolean).join('\n'),grid,inputImage:input.reference?.name||''});
 drafts=drafts.slice(-20);saveDrafts();
}
function recoverDraft(order){
 const id=order.draft_id||Object.keys(inboxState.drafts||{}).find(key=>inboxState.drafts[key]===order.puzzle_id);
 if(!id)return false;
 saveReceiptDraft(order,id);
 newDraft(id);$('motifBrief').focus();
 setText($('orderStatus'),'Übernahme beendet. Vor einem neuen Auftrag vorhandene Originale und verbrauchte Korrekturen prüfen.');
 return true;
}
async function inboxAction(action,body,navigate=true){
 if(inboxEpoch%2)throw Error('Die aktuelle Empfangsaktion wird noch abgeschlossen.');
 ++inboxEpoch;
 try{
  const response=await request('/api/inbox/'+action,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const value=await response.json();showInbox(value,navigate);return value;
 }finally{++inboxEpoch;}
}
function showInbox(value,navigate=true){
 const previous=currentOrder();
 if(!folderDirty){
  $('inboxFolder').value=value.folder?.id||'';
  $('inboxDirectory').value=value.folder?.directory||'';
 }
 inboxState=value;
 const rows=renderNavigation(),order=currentOrder();
 if(!navigate)return;
 if(draft&&orderById(value.drafts?.[draft.id])&&!starting){chooseMotif(value.drafts[draft.id]);}
 else if(!selectedId()&&!draft&&rows.length&&listing)chooseMotif(rows.find(r=>r.id===lastSelection)?.id||rows[0].id);
 else if(previous&&!order&&localSelection){
  if(currentMotif())chooseMotif(localSelection);
  else if(previous.result||!recoverDraft(previous))adopt(listing);
 }else if(JSON.stringify(previous)!==JSON.stringify(order)){
  if(order&&localSelection&&!currentMotif()&&previous?.request_id!==order.request_id){
   chooseMotif(localSelection);return;
  }
  if($('copyOrder'))updatePrompt();
  if(!order&&currentMotif())setText($('motifStatus'),currentMotif().status);
 }
 reconcileResult();
}
let loadingResult=null;
function resultJob(source,order){
 if(!source?.remote_confirmed||source.update?.state==='error')return null;
 const motif=source.motifs.find(m=>m.puzzle_id===order.puzzle_id);
 return source.jobs.find(j=>j.id===motif?.current_job&&j.source==='remote'&&j.ref==='content/pw/'+order.puzzle_id&&j.puzzle_id===order.puzzle_id&&
  (j.commit===order.result.head||j.receipt_ancestor===order.result.head));
}
function reconcileResult(){
 const order=currentOrder();
 const background=inboxState?.orders.find(other=>other!==order&&other.step==='done'&&
  (completedIn(listing,other.puzzle_id)||resultJob(listing,other)));
 if(background&&!(inboxEpoch%2)){
  inboxAction('acknowledge',receiptBinding(background)).catch(exc=>setText($('inboxMessage'),exc.message));
 }
 if(!order?.result||draft)return;
 const loaded=detail&&active?.id===resultJob(pending||listing,order)?.id;
 if(loaded?order.step==='done':!viewEdited&&!remoteExplicit&&(!active||detail))loadResult(order,false);
}
async function loadResult(order,explicit){
 if(loadingResult===order.request_id)return;
 const epoch=generation,edits=viewEdited;
 const stillHere=()=>currentOrder()?.request_id===order.request_id&&generation===epoch&&viewEdited===edits;
 loadingResult=order.request_id;
 try{
  if(explicit&&viewEdited&&!confirm('Den veröffentlichten Stand laden und die ungesendeten Eingaben dieser Ansicht verwerfen?'))return;
  const source=await(await request('/api/jobs')).json();if(!stillHere())return;
  const job=resultJob(source,order);
  if(job){
   if(!detail||active?.id!==job.id||active?.commit!==job.commit){
    const loaded=await(await request('/api/jobs/'+job.id)).json();
    if(!stillHere())return;
    if(loaded.puzzle_id!==order.puzzle_id||loaded.commit!==job.commit)throw Error('Quellenstand inzwischen geändert. Arbeitsstand erneut laden.');
    await adopt(source,{id:job.id,detail:loaded});
   }
   if(!detail||currentOrder()?.request_id!==order.request_id||active?.id!==job.id)return;
  }else if(!completedIn(source,order.puzzle_id)){
   if(explicit)await $('refresh').onclick();
   if(stillHere())setText($('orderStatus'),'Der passende Remote-Stand ist noch nicht verfügbar. Arbeitsstand erneut laden.');
   return;
  }
  if(order.step==='done'){
   if(!job){
    await inboxAction('acknowledge',receiptBinding(order),false);
    if(generation===epoch&&selectedId()===order.puzzle_id)adopt(source);
   }else await inboxAction('acknowledge',receiptBinding(order));
  }
 }catch(exc){if(currentOrder()?.request_id===order.request_id&&$('orderStatus'))setText($('orderStatus'),exc.message);}
 finally{if(loadingResult===order.request_id)loadingResult=null;}
}
$('inboxFolder').oninput=$('inboxDirectory').oninput=()=>{folderDirty=true;};
$('inboxSetup').onclick=async()=>{
 try{
  await inboxAction('configure',{folder_id:$('inboxFolder').value.trim(),directory:$('inboxDirectory').value.trim()});
  folderDirty=false;showInbox(inboxState);$('inboxMessage').textContent='Drive-Stammordner gespeichert.';
 }catch(exc){$('inboxMessage').textContent=exc.message;}
};
async function pollInbox(){
 try{
  const epoch=inboxEpoch,value=await (await request('/api/inbox/status')).json();
  if(epoch===inboxEpoch&&epoch%2===0){
   if(JSON.stringify(value)!==JSON.stringify(inboxState))showInbox(value);
   else reconcileResult();
  }
 }catch(exc){$('inboxMessage').textContent=exc.message;}
 const timer=setTimeout(pollInbox,3000);
 timer.unref?.();
}
pollInbox().finally(pollSources);
