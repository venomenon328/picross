'use strict';
/* Pure prompt projection. Choices and personal options never advance Git state. */
const PW = (()=>{
 const steps=['Abschlussbilder','Motivvorlage','Rasterangebote','Kontextzeichnungen','Integration'];
 const phase={brief_ready:1,reveal_review:1,motif_review:2,motif_approved:3,raster_review:3,raster_ready:3,background_review:4,content_ready:5,editorially_approved:5,registered:5};
 function step(value){return value?phase[value.facts.state]||null:1;}
 function orderStep(value){
  if(value?.facts.candidates&&value.facts.state==='raster_review'&&value.offers.some(o=>o.kind==='raster'))return 4;
  return ({reveal_review:2,motif_review:3,raster_ready:4,background_review:5})[value?.facts.state]||step(value);}
 function options(saved){
  const v=saved&&typeof saved==='object'&&!Array.isArray(saved)?saved:{};
  return {workroot:typeof v.workroot==='string'?v.workroot:'',merge:typeof v.merge==='boolean'?v.merge:true};
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
  return changes.join(' ');
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
  return parts.join(' ');
 }
 function choiceReady(value,target,intent){
  const card=value?.facts.candidates?.[target];
  if(!card)return !value?.facts.candidates;
  return !card.missing.length&&card.findings.every(row=>
   row.eligible&&(intent.findings?.[row.binding]?.accepted??(row.decision?.action==='accept')));
 }
 function findingOrders(value,intent){
  const lines=[];
  for(const [target,card] of Object.entries(value?.facts.candidates||{})){
   for(const row of card.findings){
    const edit=intent.findings?.[row.binding];
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
    `Ich beabsichtige die Rasterwahl ${decision.target} und die anschließende Fortsetzung in Schritt 4. Binde zuerst diese neue Parameteralternative und die davon abhängige Motiventscheidung. Prüfe die frische Endrevision, Hinweise, unabhängige vollständige Deduktion mit Endmatrixvergleich, Difficulty und alle weiteren Pflichtgates am Endraster. Publiziere die gültige Rasterwahl und die Fortsetzung erst nach erfolgreichen Prüfungen. Bleibt ein Gate offen, lege den konkreten Befund in Schritt 3 vor.`
   ];
  }
  if(decision.kind!=='frame'||!card.diagnostics?.frame||card.diagnostics.frame.exception)
   throw Error('Die aktuelle technische Randentscheidung ist nicht verfügbar.');
  const reason=intent.frameReason?.trim();
  if(!reason)throw Error('Bitte die technische frame-Ausnahme begründen.');
  return [
   `Schritt 3: Für ${identity} erkläre ich ausdrücklich eine technische frame-Ausnahme für den festgestellten H-01-Randbefund. Begründung: ${reason}`,
   'Binde meine tatsächliche Erklärung mit eigenem Beleg an genau diesen Kandidaten, diese Endrevision und den Definitionshash. Prüfe die Ausnahme technisch, zeige den weiterhin negativen Randbefund und den separaten Ausnahmebeleg. Lege den aktuellen Prüfstand mit allen übrigen Pflichtgates vor.'
  ];
 }
 function prompt(value,intent={},personal={}){
  const action=intent.action||'continue',order=orderStep(value),opts=options(personal);
  const pickingRaster=value?.facts.candidates&&value.facts.state==='raster_review'&&value.offers.some(o=>o.kind==='raster');
  const n=action==='continue'?(pickingRaster?4:order):step(value);
  if(!n)throw Error('Dieser Stand benötigt einen eigenen ausdrücklich beauftragten Folgeauftrag.');
  if(value&&value.facts.authoring_version!=='0.8.0')throw Error('Dieser historische Stand gehört nicht zum neuen 0.8-Produktionsweg.');
  const remote=value?.source_url?.match(/^https:\/\/github\.com\/([A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+)\/tree\/([a-f0-9]{40})$/);
  if(value&&(!remote||value.commit!==remote[2]))throw Error('Remote-Sicherung nicht bestätigt. Arbeitsstand zuerst mit dem PW-B-Publisher sichern, dann Quellen aktualisieren.');
  if(!['continue','rework','resume','background_change','raster_diagnosis'].includes(action))throw Error('Bitte eine gültige Aktion wählen.');
  const lines=[`Repository: ${remote?.[1]||'venomenon328/picross'} · Ziel: main. Verbindlich: AGENTS.md im aktuellen main und die dort gerouteten Pflichtquellen für Authoring 0.8.0, Schritt ${n}.`];
  if(value){
   if(!/^pz-[a-z0-9]+(?:-[a-z0-9]+)*$/.test(value.puzzle_id)||!/^[A-Za-z0-9][A-Za-z0-9._-]{0,31}$/.test(value.revision)||value.record?.file!==`content/authoring/${value.puzzle_id}/${value.revision}/record.json`)throw Error('Der kanonische Produktionsrecord ist nicht eindeutig gebunden.');
   lines.push(`Produktionsdatensatz: https://github.com/${remote[1]}/blob/${remote[2]}/${value.record.file}`);
  }else{
   if(!intent.brief?.trim())throw Error('Bitte zuerst dein Motiv beschreiben.');
   lines.push(`Neues Motiv: ${intent.brief.trim()}`);
   if(intent.inputImage)lines.push(`Beigefügte Referenzdatei: ${intent.inputImage}.`);
  }
  const selected=value?.offers.find(o=>o.id===intent.selection&&o.kind===intent.kind);
  const cards=value?.facts.candidates;
  if(cards){
   if(action!=='raster_diagnosis')lines.push(...findingOrders(value,intent));
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
   lines.push(`Spätere Hintergrundrevision nach Authoring Schritt 5 §9: ${intent.feedback.trim()}`);
  }else if(action==='rework'){
   if(!intent.feedback?.trim())throw Error('Bitte die gewünschte Korrektur beschreiben.');
   lines.push(`Korrektur in Schritt ${step(value)}: ${intent.feedback.trim()}. Korrigierten Stand zur fälligen Entscheidung vorlegen.`);
   if(cards){
    const base=intent.selection;
    if(!cards[base])throw Error('Bitte die Korrekturgrundlage wählen.');
    lines.push(`Korrekturgrundlage: ${base}. Geltende Behandlungen berücksichtigen. Korrigierte Bytes zur Wahl vorlegen.`);
    for(const text of cards[base].instructions||[])lines.push('Geltende Behandlung: '+text);
    for(const row of cards[base].findings){
     const edit=intent.findings?.[row.binding];
     if(edit&&!edit.accepted&&edit.treatment.trim()&&row.decision?.action!=='accept')
      lines.push(JSON.stringify({Befund:row.id,Korrekturhinweis:edit.treatment}));
     if(row.decision?.action==='accept'&&(!edit||edit.accepted&&edit.treatment===row.decision.treatment))
      lines.push(JSON.stringify({Befund:row.id,Behandlung:row.decision.treatment}));
    }
   }else if(selected)lines.push(`Betroffenes Angebot: ${selected.kind}/${selected.id}.`);
  }else if(action==='resume'){
   lines.push(`Schritt ${n} am gebundenen Datensatz wieder aufnehmen.`);
  }else if(!value||value.facts.state==='brief_ready'){
   lines.push('Schritt 1: Abschlussbilder als reveal_review zur Auswahl vorlegen.');
  }else if(value.facts.state==='reveal_review'){
   if(!selected||selected.kind!=='reveal')throw Error('Bitte ein Abschlussbild wählen.');
   lines.push(`Schritt 2: Ich wähle und gebe Abschlussbild ${selected.id} unverändert frei. Motivvorlage und Parameterkorridor als motif_review vorlegen.`);
  }else if(value.facts.state==='motif_review'){
   if(cards){
    const options=value.facts.published.proposed;
    if(selected?.kind!=='motif')throw Error('Bitte die Motivvorlage wählen.');
    if(!Number.isInteger(intent.parameter)||!options[intent.parameter])throw Error('Bitte eine vollständige Parameteralternative wählen.');
    lines.push(`Schritt 3: Ich gebe Motivvorlage ${selected.id} und die Parameteralternative ${intent.parameter+1} unverändert frei: ${JSON.stringify(options[intent.parameter])}. Qualifizierte Rasterangebote vorlegen.`);
   }else lines.push('Schritt 3: Ich gebe die unveränderte Motivvorlage samt vorgeschlagenem Parameterkorridor im Datensatz frei. Qualifizierte Rasterangebote als raster_ready vorlegen.');
  }else if(!pickingRaster&&['motif_approved','raster_review'].includes(value.facts.state)){
   lines.push('Schritt 3: Die bereits freigegebene Rasterproduktion bis zu qualifizierten Rasterangeboten fortsetzen.');
  }else if(pickingRaster||value.facts.state==='raster_ready'){
   if(!selected||selected.kind!=='raster')throw Error('Bitte ein qualifiziertes Rasterangebot wählen.');
   lines.push(`Schritt 4: Ich wähle das qualifizierte Rasterangebot ${selected.id}. Kontextzeichnungen als background_review zur Auswahl vorlegen.`);
  }else{
   const final=finalAssets(value,intent);
   if(value.facts.state==='background_review'){
    lines.push(final.choice==='none'?'Schritt 5: Ich entscheide mich ausdrücklich für keinen Hintergrund.':final.choice==='standard'?'Schritt 5: Ich wähle ausdrücklich den Standardhintergrund.':`Schritt 5: Ich wähle die unveränderte Kontextzeichnung aus Angebot ${final.choice}.`);
    if(cards&&final.background)lines.push('Gewähltes Profil: '+value.facts.originals.record.assets.find(a=>a.id===final.background.id).profile+'.');
    lines.push('Ich erteile die Endabnahme dieser Hintergrundentscheidung mit dem gewählten Raster und Reveal und beauftrage deren Integration.');
   }else if(value.facts.state==='registered')lines.push('Schritt 5: Git-/PR-Abschluss der bereits registrierten unveränderten Lieferung fortsetzen.');
   else if(value.facts.state==='editorially_approved')lines.push('Schritt 5: Die bereits endabgenommene unveränderte Lieferung integrieren.');
   else lines.push('Schritt 5: Ich erteile die Endabnahme der gebundenen unveränderten Raster-, Reveal- und Hintergrundfassung (gegebenenfalls none) und beauftrage deren Integration.');
  }
  const published=value?.facts.published;
  // Input controls belong to the displayed view; corrections route their actual phase.
  if(order===1&&intent.notes?.trim())lines.push(`Neue/zusätzliche Motivhinweise:\n${intent.notes.trim()}`);
  if(order<=2||(order===3&&action==='rework')){
   const grid=value?gridChanges(value,intent):gridRequest(intent.grid);
   if(grid)lines.push(`${published?'Neue Absicht gegenüber den veröffentlichten Vorgaben':'Vorgaben für das spätere Lösungsraster'}: ${grid}`);
  }
  if((order===2||(order===3&&action==='rework'))&&intent.parameters?.trim())lines.push(`Neue/zusätzliche Wünsche zur Motivvorlage: ${intent.parameters.trim()}`);
  if(order===4&&intent.context?.trim())lines.push(`Kontextwunsch: ${intent.context.trim()}`);
  if(opts.workroot.trim())lines.push(`Lokale Codex-Arbeitswurzel: ${opts.workroot.trim()}.`);
  const isClosing=closing(value,intent);
  if(isClosing&&opts.merge){
   lines.push('Commit, Push und PR; bei erfüllten Pflichtgates nach Authoring Schritt 5 §8 per Squash-Merge nach main integrieren und den Produktionsabschluss nach §9 ausführen.');
  }
  else lines.push('Commit, Push und Draft-PR im beauftragten Umfang; kein Merge.');
  return lines.join('\n\n');
 }
 return {steps,step,orderStep,prompt,choiceReady,publishedGrid,options,closing,finalAssets,axes,cropChanges};
})();
if(typeof module!=='undefined')module.exports=PW;
