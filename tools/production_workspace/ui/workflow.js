'use strict';
/* Pure prompt projection. Choices and personal options never advance Git state. */
const PW = (()=>{
 const steps=['Abschlussbilder','Motivvorlage','Rasterangebote','Kontextzeichnungen','Integration'];
 const phase={brief_ready:1,reveal_review:1,motif_review:2,motif_approved:3,raster_review:3,raster_ready:3,background_review:4,content_ready:5,editorially_approved:5,registered:5};
 const executors=['ChatGPT','Codex'];
 const defaultExecutors={1:'Codex',2:'Codex',3:'ChatGPT',4:'Codex',5:'ChatGPT'};
 const roleStep={reveal:1,motif:2,raster:3,raster_draft:3,background:4};
 function step(value){return value?phase[value.facts.state]||null:1;}
 function orderStep(value){
  if(value?.facts.candidates&&value.facts.state==='raster_review'&&value.offers.some(o=>o.kind==='raster'))return 4;
  return ({reveal_review:2,motif_review:3,raster_ready:4,background_review:5})[value?.facts.state]||step(value);}
 function actionTargets(value,action){
  if(!value||value.facts.state==='registered'||!['rework','assessment'].includes(action))return [];
  const selected=value.facts.originals?.record?.selected||{},current=step(value);
  return (value.assets||[]).filter(asset=>{
   const n=roleStep[asset.role],role=asset.role==='raster_draft'?'raster':asset.role;
   if(!n||value.facts.candidates&&!Object.hasOwn(value.facts.candidates,asset.id))return false;
   if(action==='assessment')return ['reveal','motif'].includes(role)&&
    value.facts.state===role+'_review'&&!selected[role];
   return selected[role]===asset.id||!selected[role]&&current<=n;
  });
 }
 function orderTarget(value,intent={}){
  const action=intent.action||'continue',state=value?.facts.state;
  const invalid=error=>({step:null,role:null,target:null,inbox:false,error});
  if(!['continue','rework','assessment','resume','background_change','raster_diagnosis'].includes(action))
   return invalid('Bitte eine gültige Aktion wählen.');
  if(!value&&!['continue','resume'].includes(action))return invalid('Ein neuer Entwurf beginnt mit dem Abschlussbildauftrag.');
  let n=action==='continue'?orderStep(value):step(value),role=null,target=null,inbox=false;
  if(['rework','assessment'].includes(action)){
   const asset=actionTargets(value,action).find(a=>a.id===intent.selection);
   if(!asset)return invalid(action==='assessment'
    ?'Bitte ein offenes Reveal- oder Motivangebot dieser Phase zur Neubewertung wählen.'
    :'Bitte eine verfügbare Korrekturgrundlage wählen.');
   if(intent.kind&&intent.kind!==asset.role&&!(asset.role==='raster_draft'&&intent.kind==='raster'))
    return invalid('Die gewählte Rolle passt nicht zur Korrektur-/Bewertungsgrundlage.');
   role=asset.role;target=asset.id;n=roleStep[role];
   inbox=Boolean(value.facts.candidates)&&['reveal','motif','background'].includes(role);
  }else if(action==='background_change'){
   if(state!=='registered')return invalid('Eine spätere Hintergrundrevision braucht einen tatsächlich registrierten Stand.');
   n=5;role='background';
  }else if(action==='raster_diagnosis'){
   n=3;role='raster';target=intent.diagnosis?.target||null;
  }else{
   role=({1:'reveal',2:'motif',3:'raster',4:'background'})[n]||null;
   inbox=(!value||Boolean(value.facts.candidates))&&(action==='continue'?[1,2,4].includes(n):
    !value||['brief_ready','reveal_review','motif_review'].includes(state));
  }
  if(!n)return invalid('Dieser Stand benötigt einen eigenen ausdrücklich beauftragten Folgeauftrag.');
  return {step:n,role,target,inbox,error:null};
 }
 function promptStep(value,intent={}){return orderTarget(value,intent).step;}
 function options(saved){
  const v=saved&&typeof saved==='object'&&!Array.isArray(saved)?saved:{};
  const selected=v.executors&&typeof v.executors==='object'&&!Array.isArray(v.executors)?v.executors:{};
  const preferences={};
  for(const [step,executor] of Object.entries(defaultExecutors)){
   preferences[step]=executors.includes(selected[step])?selected[step]:executor;
  }
  return {workroot:typeof v.workroot==='string'?v.workroot:'',merge:typeof v.merge==='boolean'?v.merge:true,executors:preferences};
 }
 function executionOrder(route,action,opts){
  const n=route.step;
  if(opts.executors[n]==='Codex'){
   const lines=['Ausführung mit Codex. Nutze den lokalen Produktionsweg nach docs/tools/PRODUCTION_GIT_WORKSPACE.md.'];
   if(opts.workroot.trim())lines.push(`Lokale Codex-Arbeitswurzel: ${opts.workroot.trim()}.`);
   return lines;
  }
  let entry='Nutze den gebundenen Einstieg in docs/tools/PW_REMOTE.md.';
  if(action==='background_change')
   entry='Nutze den gezielten Bestands- und Revisionsweg nach Authoring Schritt 5 §9.';
  else if(route.inbox||n<3)entry='Nutze den gebundenen Bildauftrag nach docs/tools/PW_IMPORT.md.';
  return [`Ausführung mit ChatGPT. ${entry}`];
 }
 function pendingBackground(value){
  return value?.facts.state==='background_review'&&value.facts.originals?.record?.assets?.some(
   asset=>asset.role==='background'&&(!asset.prepared||!asset.prepared.inspection));
 }
 function closing(value,intent={}){
  return (intent.action||'continue')==='continue'&&['background_review','content_ready','editorially_approved','registered'].includes(value?.facts.state);
 }
 function finalAssets(value,intent={}){
  const ids=value?.facts.composition;
  if(!ids)throw Error('Die gebundene Schlussübersicht fehlt. Quellen prüfen.');
  const assets=value.assets||[];
  const bound=(role,id)=>{
   const found=assets.filter(a=>a.id===id&&a.role===role);
   if(found.length!==1)throw Error(`Die Schlussübersicht ist nicht eindeutig: ${role}.`);
   return found[0];
  };
  const result={raster:bound('raster',ids.raster),reveal:bound('reveal',ids.reveal),background:null};
  const pending=value.facts.state==='background_review';
  const choice=pending?intent.selection:value.facts.background_choice;
  if(['none','standard'].includes(choice)){result.choice=choice;return result;}
  if(!pending&&ids.background){result.background=bound('background',ids.background);result.choice=choice;return result;}
  if(pending&&intent.kind!=='background')throw Error('Bitte einen Hintergrund oder bewusst keinen wählen.');
  const offers=(value.offers||[]).filter(o=>o.kind==='background'&&o.id===choice);
  if(offers.length!==1)throw Error('Bitte einen eindeutig gebundenen Hintergrund oder bewusst keinen wählen.');
  // An offer may reference the same original more than once, but not different images.
  const originals=offers[0].asset_ids.map(id=>bound('background',id));
  if(!originals.length||new Set(originals.map(a=>a.location.sha256)).size!==1)throw Error('Die Hintergrundwahl ist nicht eindeutig gebunden.');
  result.background=originals[0];result.choice=choice;
  return result;
 }
 function publishedGrid(value){
  const source=value?.facts.published;
  const parameters=source?.approved?.length?source.approved:source?.proposed;
  if(!Array.isArray(parameters)||parameters.length!==1)return {};
  const p=parameters[0];
  if(!p||typeof p!=='object'||Array.isArray(p))return {};
  const known=['width','height','mode','foreground_colors','size_constraint','foreground_color_constraint','status'];
  if(Object.keys(p).some(k=>!known.includes(k)))return {};
  const grid={},precision={approximate:'approx',exact:'exact'};
  for(const axis of ['width','height']){
   if(Number.isInteger(p[axis])&&p[axis]>=1&&p[axis]<=50&&precision[p.size_constraint]){
    grid[axis]=String(p[axis]);grid.sizeAccuracy=precision[p.size_constraint];
   }
  }
  if(['mono','color'].includes(p.mode))grid.mode=p.mode;
  else if(p.mode==null&&p.foreground_colors===1&&p.foreground_color_constraint==='exact')grid.mode='mono';
  if(p.mode==='color'&&Number.isInteger(p.foreground_colors)&&p.foreground_colors>=2&&p.foreground_colors<=8&&precision[p.foreground_color_constraint]){
   Object.assign(grid,{colors:String(p.foreground_colors),colorAccuracy:precision[p.foreground_color_constraint]});
  }
  return grid;
 }
 function gridChanges(value,intent){
  const base=publishedGrid(value),next={...base,...intent.grid},removed=intent.removeGrid||{};
  const changes=[];
  for(const [axis,label] of [['width','Breite'],['height','Höhe']]){
   if(removed[axis])changes.push(`${label}: bisherigen Wunsch ausdrücklich aufheben.`);
   else if((next[axis]||'')!==(base[axis]||'')||(next[axis]&&next.sizeAccuracy!==base.sizeAccuracy)){
    if(!next[axis])throw Error(`${label} ausdrücklich aufheben oder einen Wert angeben.`);
    changes.push(axisRequest(axis,next[axis],next.sizeAccuracy));
   }
  }
  for(const [group,label,keys] of [['mode','Rastermodus',['mode']],['colors','Farbzahl',['colors','colorAccuracy']]]){
   if(removed[group]){changes.push(`${label}: bisherigen Wunsch ausdrücklich aufheben.`);continue;}
   if(!keys.some(k=>(next[k]||'')!==(base[k]||'')))continue;
   if(group==='mode'){
    if(!next.mode){if(base.mode)throw Error('Rastermodus ausdrücklich aufheben oder einen Modus wählen.');continue;}
    changes.push(modeRequest(next.mode));
   }else{
    if(next.mode==='mono'||removed.mode)continue;
    if(!next.colors){if(base.colors)throw Error('Farbzahl ausdrücklich aufheben oder eine Farbzahl angeben.');continue;}
    changes.push(colorRequest(next.colors,next.colorAccuracy,next.mode));
   }
  }
  return changes;
 }
 function integer(value,min,max,label){
  if(!/^\d+$/.test(value)||Number(value)<min||Number(value)>max)throw Error(`Bitte für ${label} eine ganze Zahl von ${min} bis ${max} eingeben.`);
  return Number(value);
 }
 function accuracy(value){
  if(!value||value==='approx')return 'ungefähr';
  if(value==='exact')return 'exakt';
  throw Error('Bitte die Genauigkeit der Rastervorgabe wählen.');
 }
 function axisRequest(axis,value,precision){
  const label=axis==='width'?'Breite':'Höhe';
  return `${label}: ${accuracy(precision)} ${integer(value,1,50,'die '+label)} Zellen.`;
 }
 function colorRequest(value,precision,mode){
  const count=integer(value,mode==='color'||precision!=='exact'?2:1,8,'die Farbzahl');
  if(count===1)return 'Farbzahl: exakt eine Vordergrundfarbe.';
  return `Farbzahl: ${accuracy(precision)} ${count} Vordergrundfarben.`;
 }
 function modeRequest(mode){
  if(!['mono','color'].includes(mode))throw Error('Bitte einen gültigen Rastermodus wählen.');
  return mode==='mono'?'Rastermodus: monochrom.':'Rastermodus: farbig.';
 }
 function gridRequest(grid={}){
  const parts=[];
  for(const axis of ['width','height'])if(grid[axis])parts.push(axisRequest(axis,grid[axis],grid.sizeAccuracy));
  if(grid.mode)parts.push(modeRequest(grid.mode));
  if(grid.mode!=='mono'&&grid.colors)parts.push(colorRequest(grid.colors,grid.colorAccuracy,grid.mode));
  return parts;
 }
 function correctionInputs(value,intent,grid){
  if(intent.action!=='rework')return;
  const route=orderTarget(value,intent);
  if(route.error)throw Error(route.error);
  for(const [key,phases,label] of [['notes',[1],'Motivhinweise gehören zum Abschlussbildauftrag'],
   ['parameters',[2,3],'Motivvorlagenwünsche gehören zum Motiv- oder Rasterauftrag'],
   ['context',[4],'Kontextwünsche gehören zum Hintergrundauftrag']]){
   if(intent[key]?.trim()&&!phases.includes(route.step))throw Error(label+'. Eingabe oder Korrekturgrundlage anpassen.');
  }
  if(grid.length&&route.step===4)throw Error('Rasterwünsche gehören zum Abschlussbild-, Motiv- oder Rasterauftrag. Eingabe oder Korrekturgrundlage anpassen.');
 }
 function referenceInput(value,intent){
  const ref=intent.reference;
  if(value||!intent.inputImage&&!ref)return ref||'';
  if(!ref||typeof ref!=='object'||Array.isArray(ref)||Object.keys(ref).sort().join(',')!=='bytes,name,sha256'||
     typeof ref.name!=='string'||!ref.name||ref.name.length>255||/[\\/:\x00-\x1f]/.test(ref.name)||
     !/\.(png|jpe?g)$/i.test(ref.name)||intent.inputImage&&ref.name!==intent.inputImage||
     !Number.isInteger(ref.bytes)||ref.bytes<1||ref.bytes>32*1024*1024||
     typeof ref.sha256!=='string'||!/^[a-f0-9]{64}$/.test(ref.sha256))
   throw Error(intent.referenceError||'Die Referenzdatei benötigt eine vollständige passende Bindung aus Name, Bytezahl und SHA-256. Datei erneut auswählen.');
  return ref;
 }
 function inboxFindings(value,intent){
  if(intent.action==='resume')return {};
  const edits=intent.findings||{};
  if(intent.action!=='assessment')return edits;
  const route=orderTarget(value,intent),result={};
  if(route.error)throw Error(route.error);
  for(const [binding,edit] of Object.entries(edits)){
   const found=Object.entries(value.facts.candidates||{}).flatMap(([target,card])=>
    card.findings.filter(row=>row.binding===binding).map(row=>({target,row})));
   if(found.length!==1||!edit||typeof edit.accepted!=='boolean'||typeof edit.treatment!=='string')
    throw Error('Befundbindung für die Neubewertung ist veraltet oder nicht eindeutig. Vormerkung prüfen.');
   const {target,row}=found[0],stored=row.decision;
   if(edit.accepted===(stored?.action==='accept')&&(!edit.accepted||edit.treatment===stored?.treatment))continue;
   if(target!==route.target)throw Error('Die neue Befundentscheidung gehört nicht zum Bewertungsziel '+route.target+'. Andere Vormerkung zuerst klären.');
   if(!row.eligible)throw Error('Die Befundentscheidung am Bewertungsziel ist nicht verfügbar.');
   if(edit.accepted&&!edit.treatment.trim())throw Error('Bitte den Umgang mit dem Befund bestätigen.');
   result[binding]=edit;
  }
  return result;
 }
 function orderIntent(intent,action=intent.action){
  if(action!=='assessment')return intent;
  return {action,selection:intent.selection,kind:intent.kind,findings:intent.findings};
 }
 function inboxInputs(value,intent,action){
  intent=orderIntent(intent,action);
  if(action!=='correction'&&['rework','background_change'].includes(intent.action)&&intent.feedback?.trim())
   throw Error('Für den eingegebenen Änderungswunsch den Empfangsauftrag „Gewählte Variante korrigieren“ wählen.');
  const grid=value?gridChanges(value,intent):gridRequest(intent.grid);
  correctionInputs(value,intent,grid);
  inboxFindings(value,intent);
  const reference=referenceInput(value,intent);
  return {
   brief:value?'':(intent.brief||'').trim(), notes:(intent.notes||'').trim(),
   parameters:(intent.parameters||'').trim(), context:(intent.context||'').trim(),
   feedback:action==='correction'?(intent.feedback||'').trim():'',
   reference, grid
  };
 }
 function choiceReady(value,target,intent){
  const card=value?.facts.candidates?.[target];
  if(!card)return !value?.facts.candidates;
  return !card.missing.length&&card.findings.every(row=>
   row.eligible&&(intent.findings?.[row.binding]?.accepted??(row.decision?.action==='accept')));
 }
 function findingOrders(value,intent){
  const lines=[],edits=inboxFindings(value,intent);
  for(const [target,card] of Object.entries(value?.facts.candidates||{})){
   for(const row of card.findings){
    const edit=edits[row.binding];
    const stored=row.decision;
    if(!edit||!row.eligible)continue;
    if(edit.accepted&&!edit.treatment.trim())throw Error('Bitte den Umgang mit dem Befund bestätigen.');
    if(edit.accepted===(stored?.action==='accept')&&(!edit.accepted||edit.treatment===stored?.treatment))continue;
    lines.push(JSON.stringify({Kandidat:target,Befund:row.id,Kriterium:row.criterion,Bindung:row.binding,
     Entscheidung:edit.accepted?'Annahme':'Widerruf',Behandlung:edit.treatment}));
   }
  }
  return lines;
 }
 const axes={width:'Breite',height:'Höhe',foreground_colors:'Vordergrundfarben'};
 function parameterOptions(parameters){
  if(!Array.isArray(parameters))return [];
  // The reader validates every published option. Keep the original indices and
  // require the complete projected shape before offering a choice.
  return parameters.flatMap((option,index)=>{
   if(option?.format==='picross-raster-parameters-v1'){
    const {constraints,imports,derivation}=option;
    const complete=Object.keys(axes).every(axis=>{
     const c=constraints?.[axis];
     return c&&['approximate','exact','open'].includes(c.kind)&&
      (c.kind==='open'?c.target===null:Number.isInteger(c.target))&&
      [c.minimum,c.maximum].every(n=>n===null||Number.isInteger(n));
    });
    if(complete&&Array.isArray(imports)&&imports.length&&imports.every(entry=>entry&&
       Object.keys(axes).every(axis=>Number.isInteger(entry[axis]))&&['mono','color'].includes(entry.mode)&&
       typeof entry.method==='string'&&typeof entry.fit==='string'&&Array.isArray(entry.actual_crop)&&entry.actual_crop.length===4)&&
       typeof derivation?.cell_edits==='boolean'&&Array.isArray(derivation.empty_edge_crop)&&
       Array.isArray(derivation.protected_features))return [{option,index}];
   }else if(option&&option.format===undefined&&Object.keys(axes).every(axis=>Number.isInteger(option[axis]))&&
            ['exact','approximate'].includes(option.size_constraint)&&['exact','approximate'].includes(option.foreground_color_constraint)&&
            (['mono','color'].includes(option.mode)||option.mode==null&&option.foreground_colors===1&&option.foreground_color_constraint==='exact')){
    return [{option,index}];
   }
   return [];
  });
 }
 function cropChanges(crop){
  return Object.entries(crop.changes).map(([axis,c])=>`${axes[axis]}: Minimum ${c.previous} → ${c.proposed}`);
 }
 function diagnosisOrder(value,intent){
  const decision=intent.diagnosis;
  const card=value.facts.candidates?.[decision?.target];
  const record=value.facts.originals?.record;
  if(!card||record?.selected?.raster||!['raster_review','raster_ready'].includes(value.facts.state)||
     card.definition_sha256!==decision.sha||card.revision!==decision.revision)
   throw Error('Bitte einen aktuellen Rasterbefund für den Auftrag wählen.');
  const identity=`Kandidat ${decision.target}, Endrevision ${card.revision}, Definitions-SHA-256 ${card.definition_sha256}`;
  if(decision.kind==='crop'){
   const crop=card.diagnostics?.crop;
   if(!crop||decision.parameters!==crop.parameters_sha256||!cropChanges(crop).length)
    throw Error('Der gebundene Beschnittvorschlag fehlt oder ist veraltet.');
   const dimensions=d=>`${d.width} × ${d.height}`;
   return [
    `Schritt 3: Für ${identity} genehmige ich die konkrete Parameter-/Korridorneufreigabe der Alternative ${crop.parameter+1} (bisheriger SHA-256 ${crop.parameters_sha256}): ${cropChanges(crop).join(', ')}. Alle übrigen Werte dieser Alternative und die übrigen Alternativen bleiben gültig. Der belegte Zuschnitt führt von ${dimensions(crop.before)} auf ${dimensions(crop.after)} Zellen.`,
    `Ich beabsichtige die Rasterwahl ${decision.target} und die Fortsetzung in Schritt 4 nach erfolgreicher Qualifikation mit dieser neuen Parameterbindung. Andernfalls den offenen Befund in Schritt 3 vorlegen.`
   ];
  }
  if(decision.kind!=='frame'||!card.diagnostics?.frame||card.diagnostics.frame.exception)
   throw Error('Die aktuelle technische Randentscheidung ist nicht verfügbar.');
  const reason=intent.frameReason?.trim();
  if(!reason)throw Error('Bitte die technische frame-Ausnahme begründen.');
  return [
   `Schritt 3: Für ${identity} erkläre ich ausdrücklich eine technische frame-Ausnahme für den festgestellten H-01-Randbefund. Begründung: ${reason}`,
   'Die Ausnahme binden und den aktuellen Prüfstand mit Randbefund und Ausnahmebeleg veröffentlichen und vorlegen.'
  ];
 }
 function prompt(value,intent={},personal={}){
  intent=orderIntent(intent);
  const action=intent.action||'continue',order=orderStep(value),opts=options(personal),route=orderTarget(value,intent);
  const n=route.step;
  if(route.error)throw Error(route.error);
  const editedGrid=(n<=2||action==='rework')?(value?gridChanges(value,intent):gridRequest(intent.grid)):[];
  correctionInputs(value,intent,editedGrid);
  const reference=referenceInput(value,intent);
  if(value&&value.facts.authoring_version!=='0.8.0')throw Error('Dieser historische Stand gehört nicht zum neuen 0.8-Produktionsweg.');
  const remote=value?.source_url?.match(/^https:\/\/github\.com\/([A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+)\/tree\/([a-f0-9]{40})$/);
  if(value&&(!remote||value.commit!==remote[2]))throw Error('Remote-Sicherung nicht bestätigt. Arbeitsstand zuerst mit dem PW-B-Publisher sichern, dann Quellen aktualisieren.');
  const lines=[`Repository: ${remote?.[1]||'venomenon328/picross'} · Ziel: main. Verbindlich: AGENTS.md im aktuellen main und die dort gerouteten Pflichtquellen für Authoring 0.8.0, Schritt ${n}.`];
  if(value){
   if(!/^pz-[a-z0-9]+(?:-[a-z0-9]+)*$/.test(value.puzzle_id)||!/^[A-Za-z0-9][A-Za-z0-9._-]{0,31}$/.test(value.revision)||value.record?.file!==`content/authoring/${value.puzzle_id}/${value.revision}/record.json`)throw Error('Der kanonische Produktionsrecord ist nicht eindeutig gebunden.');
   lines.push(`Produktionsdatensatz: https://github.com/${remote[1]}/blob/${remote[2]}/${value.record.file}`);
  }else{
   if(!intent.brief?.trim())throw Error('Bitte zuerst dein Motiv beschreiben.');
   lines.push(`Neues Motiv: ${intent.brief.trim()}`);
   if(reference)lines.push(`Beigefügte Referenzdatei: ${JSON.stringify(reference)}.`);
  }
  const selected=value?.offers.find(o=>o.id===intent.selection&&o.kind===intent.kind);
  const cards=value?.facts.candidates;
  if(cards){
   if(!['raster_diagnosis','resume'].includes(action))lines.push(...findingOrders(value,intent));
   if(action==='continue'){
    if(value.facts.blockers?.length)throw Error('Auftragsweite Voraussetzung offen: '+value.facts.blockers[0]);
    const required=new Set(selected?[selected.id]:[]);
    if(closing(value,intent)){
     for(const id of Object.values(value.facts.originals?.record?.selected||{}))if(cards[id])required.add(id);
     if(cards['@selection'])required.add('@selection');
    }
    for(const id of required)if(!choiceReady(value,id,intent))throw Error('Offene Voraussetzungen für '+id+'.');
   }
  }
  if(action==='raster_diagnosis'){
   if(!cards||value.facts.blockers?.length)throw Error('Auftragsweite Voraussetzung für den Rasterauftrag offen.');
   lines.push(...diagnosisOrder(value,intent));
  }else if(action==='background_change'){
   if(value?.facts.state!=='registered')throw Error('Eine spätere Hintergrundrevision braucht einen tatsächlich registrierten Stand.');
   if(!intent.feedback?.trim())throw Error('Bitte die gewünschte Hintergrundänderung beschreiben.');
   lines.push(`Spätere Hintergrundrevision nach Authoring Schritt 5 §9: ${intent.feedback.trim()}\nDie neue Hintergrundfassung zur Entscheidung vorlegen.`);
  }else if(action==='rework'){
   if(!intent.feedback?.trim())throw Error('Bitte die gewünschte Korrektur beschreiben.');
   lines.push(`Korrekturgrundlage: ${route.role}/${route.target}. Änderungswunsch:\n${intent.feedback.trim()}\nKorrigierten Stand veröffentlichen und zur fälligen Entscheidung vorlegen.`);
   if(cards){
    const base=route.target;
    for(const row of cards[base].findings){
     const edit=intent.findings?.[row.binding];
     if(edit&&!edit.accepted&&edit.treatment.trim()&&row.decision?.action!=='accept')
      lines.push(JSON.stringify({Kandidat:base,Befund:row.id,Bindung:row.binding,Korrekturhinweis:edit.treatment}));
    }
   }
  }else if(action==='assessment'){
   lines.push(`Ausschließlich das vorhandene unveränderte Angebot ${route.role}/${route.target} neu sichten und bewerten; die Bewertung am Arbeitsstand veröffentlichen.`);
  }else if(action==='resume'){
   if(!value)lines.push('Schritt 1: Abschlussbilder als reveal_review veröffentlichen und zur Auswahl vorlegen.');
   else if(n===5)lines.push('Nur den offenen Git-/PR-/Abschlussrest am gebundenen Stand mit der bereits tatsächlich erteilten Befugnis fortsetzen.');
   else if(pendingBackground(value))lines.push('Die veröffentlichten Hintergrundangebote fertig aufbereiten und bewerten, dann als qualifizierte Angebote veröffentlichen und zur Wahl vorlegen.');
   else lines.push(`Die noch offene Arbeit in Schritt ${n} am gebundenen Stand fortsetzen und sichern; bestehende gültige Angebote und Entscheidungen erhalten.`);
  }else if(!value||value.facts.state==='brief_ready'){
   lines.push('Schritt 1: Abschlussbilder als reveal_review veröffentlichen und zur Auswahl vorlegen.');
  }else if(value.facts.state==='reveal_review'){
   if(!selected||selected.kind!=='reveal')throw Error('Bitte ein Abschlussbild wählen.');
   lines.push(`Schritt 2: Ich wähle und gebe Abschlussbild ${selected.id} unverändert frei. Motivvorlage und Parameterkorridor als motif_review veröffentlichen und zur Wahl vorlegen.`);
  }else if(value.facts.state==='motif_review'){
   if(cards){
    const proposed=parameterOptions(value.facts.published?.proposed);
    if(!proposed.length)throw Error('Im gebundenen Datensatz fehlt ein vollständiger Parametervorschlag.');
    if(selected?.kind!=='motif')throw Error('Bitte die Motivvorlage wählen.');
    const choice=intent.parameter===undefined&&proposed.length===1?proposed[0]:proposed.find(({index})=>index===intent.parameter);
    if(!choice)throw Error('Bitte eine vollständige Parameteralternative wählen.');
    lines.push(`Schritt 3: Ich gebe Motivvorlage ${selected.id} und parameters.proposed, Eintrag ${choice.index+1} (von 1 gezählt), unverändert frei. Qualifizierte Rasterangebote veröffentlichen und zur Wahl vorlegen.`);
   }else lines.push('Schritt 3: Ich gebe die unveränderte Motivvorlage samt vorgeschlagenem Parameterkorridor im Datensatz frei. Qualifizierte Rasterangebote als raster_ready vorlegen.');
  }else if(order===3){
   lines.push('Schritt 3: Die bereits freigegebene Rasterproduktion einschließlich nötiger zulässiger Iterationen bis zu qualifizierten Rasterangeboten fortsetzen; veröffentlichen und zur Wahl vorlegen.');
  }else if(order===4){
   if(!selected||selected.kind!=='raster')throw Error('Bitte ein qualifiziertes Rasterangebot wählen.');
   lines.push(`Schritt 4: Ich wähle das qualifizierte Rasterangebot ${selected.id}. Qualifizierte Hintergrundangebote mit Originalen, fertiger Ableitung und Urteilen als background_review veröffentlichen und zur Wahl vorlegen.`);
  }else{
   const final=finalAssets(value,intent);
   if(value.facts.state==='background_review'){
    lines.push(final.choice==='none'?'Schritt 5: Ich entscheide mich ausdrücklich für keinen Hintergrund.':final.choice==='standard'?'Schritt 5: Ich wähle ausdrücklich den Standardhintergrund.':`Schritt 5: Ich wähle die unveränderte Kontextzeichnung aus Angebot ${final.choice}.`);
    lines.push('Ich erteile die Endabnahme dieser Hintergrundentscheidung mit dem gewählten Raster und Reveal und beauftrage deren Integration.');
   }else if(value.facts.state==='registered')lines.push('Schritt 5: Git-/PR-Abschluss der bereits registrierten unveränderten Lieferung fortsetzen.');
   else if(value.facts.state==='editorially_approved')lines.push('Schritt 5: Die bereits endabgenommene unveränderte Lieferung integrieren.');
   else lines.push('Schritt 5: Ich erteile die Endabnahme der gebundenen unveränderten Raster-, Reveal- und Hintergrundfassung (gegebenenfalls none) und beauftrage deren Integration.');
  }
  const published=value?.facts.published;
  if(n===1&&intent.notes?.trim())lines.push(`Neue/zusätzliche Motivhinweise:\n${intent.notes.trim()}`);
  if(n<=2||(n===3&&action==='rework')){
   const grid=editedGrid.join(' ');
   if(grid)lines.push(`${published?'Neue Absicht gegenüber den veröffentlichten Vorgaben':'Vorgaben für das spätere Lösungsraster'}: ${grid}`);
  }
  if((n===2||(n===3&&action==='rework'))&&intent.parameters?.trim())lines.push(`Neue/zusätzliche Wünsche zur Motivvorlage: ${intent.parameters.trim()}`);
  if(n===4&&intent.context?.trim())lines.push(`Kontextwunsch: ${intent.context.trim()}`);
  lines.push(...executionOrder(route,action,opts));
  const isClosing=closing(value,intent);
  if(isClosing&&opts.merge){
   lines.push('Commit, Push und PR; bei erfüllten Pflichtgates nach Authoring Schritt 5 §8 per Squash-Merge nach main integrieren und den Produktionsabschluss nach §9 ausführen.');
  }
  else if(isClosing)lines.push('Commit, Push und Draft-PR nach Authoring Schritt 5 §§8–9; kein Merge.');
  return lines.join('\n\n');
 }
 return {steps,step,orderStep,orderTarget,actionTargets,promptStep,executors,prompt,inboxInputs,inboxFindings,choiceReady,publishedGrid,parameterOptions,options,closing,pendingBackground,finalAssets,axes,cropChanges};
})();
if(typeof module!=='undefined')module.exports=PW;
