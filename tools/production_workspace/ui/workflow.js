'use strict';
/* Pure prompt projection. Choices and personal options never advance Git state. */
const PW = (()=>{
 const steps=['Abschlussbilder','Motivvorlage','Rasterangebote','Kontextzeichnungen','Integration'];
 const phase={brief_ready:1,reveal_review:1,motif_review:2,motif_approved:3,raster_review:3,raster_ready:3,background_review:4,content_ready:5,editorially_approved:5,registered:5};
 function step(value){return value?phase[value.facts.state]||null:1;}
 function orderStep(value){return ({reveal_review:2,motif_review:3,raster_ready:4,background_review:5})[value?.facts.state]||step(value);}
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
  if(choice==='none'){result.choice='none';return result;}
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
  if(p.mode==='color'&&Number.isInteger(p.foreground_colors)&&p.foreground_colors>=2&&p.foreground_colors<=8&&precision[p.foreground_color_constraint]){
   Object.assign(grid,{colors:String(p.foreground_colors),colorAccuracy:precision[p.foreground_color_constraint]});
  }
  return grid;
 }
 function gridChanges(value,intent){
  const base=publishedGrid(value),next={...base,...intent.grid},removed=intent.removeGrid||{};
  const changes=[];
  for(const [axis,label] of [['width','Breite'],['height','Höhe']]){
   if(removed[axis])changes.push(`${label}: bisherigen Wunsch ausdrücklich aufheben; ${label} passend zum Motiv bestimmen. Andere Vorgaben bleiben bestehen.`);
   else if((next[axis]||'')!==(base[axis]||'')||(next[axis]&&next.sizeAccuracy!==base.sizeAccuracy)){
    if(!next[axis])throw Error(`${label} ausdrücklich aufheben oder einen Wert angeben.`);
    changes.push(axisRequest(axis,next[axis],next.sizeAccuracy));
   }
  }
  for(const [group,label,keys] of [['mode','Rastermodus',['mode']],['colors','Farbzahl',['colors','colorAccuracy']]]){
   if(removed[group]){changes.push(`${label}: bisherigen Wunsch ausdrücklich aufheben; neu empfehlen und zur Entscheidung vorlegen.`);continue;}
   if(!keys.some(k=>(next[k]||'')!==(base[k]||'')))continue;
   if(group==='mode'){
    if(!next.mode){if(base.mode)throw Error('Rastermodus ausdrücklich aufheben oder einen Modus wählen.');continue;}
    changes.push(modeRequest(next.mode));
   }else{
    if(next.mode!=='color'||removed.mode)continue;
    if(!next.colors){if(base.colors)throw Error('Farbzahl ausdrücklich aufheben oder eine Farbzahl angeben.');continue;}
    changes.push(colorRequest(next.colors,next.colorAccuracy));
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
 function colorRequest(value,precision){return `Farbzahl: ${accuracy(precision)} ${integer(value,2,8,'die Farbzahl')} Vordergrundfarben (ohne Leerfelder).`;}
 function modeRequest(mode){
  if(!['mono','color'].includes(mode))throw Error('Bitte einen gültigen Rastermodus wählen.');
  return mode==='mono'?'Rastermodus: monochrom, genau eine Vordergrundfarbe.':'Rastermodus: farbig.';
 }
 function gridRequest(grid={}){
  const parts=[];
  for(const axis of ['width','height'])if(grid[axis])parts.push(axisRequest(axis,grid[axis],grid.sizeAccuracy));
  if(grid.mode)parts.push(modeRequest(grid.mode));
  if(grid.mode==='color'&&grid.colors)parts.push(colorRequest(grid.colors,grid.colorAccuracy));
  return parts.join(' ');
 }
 function prompt(value,intent={},personal={}){
  const n=orderStep(value),action=intent.action||'continue',opts=options(personal);
  if(!n)throw Error('Dieser Stand benötigt einen eigenen ausdrücklich beauftragten Folgeauftrag.');
  if(value&&value.facts.authoring_version!=='0.8.0')throw Error('Dieser historische Stand gehört nicht zum neuen 0.8-Produktionsweg.');
  const remote=value?.source_url?.match(/^https:\/\/github\.com\/([A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+)\/tree\/([a-f0-9]{40})$/);
  if(value&&(!remote||value.commit!==remote[2]))throw Error('Remote-Sicherung nicht bestätigt. Originale und Projektion zuerst pushen, dann Quellen aktualisieren.');
  if(!['continue','rework','resume','background_change'].includes(action))throw Error('Bitte eine gültige Aktion wählen.');
  const lines=[`Repository: ${remote?.[1]||'venomenon328/picross'} · Ziel: main. Lies AGENTS.md und die dort geroutete Produktionsphase im aktuellen main (Authoring 0.8.0).`];
  if(value){
   if(!/^pz-[a-z0-9]+(?:-[a-z0-9]+)*$/.test(value.puzzle_id)||!/^[A-Za-z0-9][A-Za-z0-9._-]{0,31}$/.test(value.revision)||value.record?.file!==`content/authoring/${value.puzzle_id}/${value.revision}/record.json`)throw Error('Der kanonische Produktionsrecord ist nicht eindeutig gebunden.');
   lines.push(`Produktionsdatensatz: https://github.com/${remote[1]}/blob/${remote[2]}/${value.record.file}`);
  }else{
   if(!intent.brief?.trim())throw Error('Bitte zuerst dein Motiv beschreiben.');
   lines.push(`Neues Motiv: ${intent.brief.trim()}`);
   if(intent.inputImage)lines.push(`Eigene Eingangsdatei: ${intent.inputImage}. Ich füge die tatsächliche Datei diesem Auftrag bei; falls sie fehlt, vor Bildarbeit anfordern.`);
  }
  const selected=value?.offers.find(o=>o.id===intent.selection&&o.kind===intent.kind);
  if(action==='background_change'){
   if(value?.facts.state!=='registered')throw Error('Eine spätere Hintergrundrevision braucht einen tatsächlich registrierten Stand.');
   if(!intent.feedback?.trim())throw Error('Bitte die gewünschte Hintergrundänderung beschreiben.');
   lines.push(`Separater späterer Hintergrundauftrag nach docs/PUZZLE_BACKGROUNDS.md §7.6 / HP-I1b2: ${intent.feedback.trim()}`);
  }else if(action==='rework'){
   if(!intent.feedback?.trim())throw Error('Bitte die gewünschte Korrektur beschreiben.');
   lines.push(`Korrektur in Schritt ${step(value)}: ${intent.feedback.trim()}. Korrigierten Stand zur fälligen Entscheidung vorlegen.`);
   if(selected)lines.push(`Betroffenes Angebot: ${selected.kind}/${selected.id}.`);
  }else if(action==='resume'){
   lines.push(`Schritt ${step(value)} am gebundenen Datensatz wieder aufnehmen; gültige Entscheidungen und Recoverystand prüfen. Keine neue Endabnahme oder Mergefreigabe.`);
  }else if(!value||value.facts.state==='brief_ready'){
   lines.push('Schritt 1: Drei unterschiedliche detaillierte farbige Abschlussbildoriginale zur Auswahl erstellen; als reveal_review veröffentlichen.');
  }else if(value.facts.state==='reveal_review'){
   if(!selected||selected.kind!=='reveal')throw Error('Bitte ein Abschlussbild wählen.');
   lines.push(`Schritt 2: Ich wähle und gebe das unveränderte Abschlussbild aus Angebot ${selected.id} frei. Motivvorlage und Parameterkorridor als motif_review zur Freigabe vorlegen.`);
  }else if(value.facts.state==='motif_review'){
   lines.push('Schritt 3: Ich gebe die unveränderte Motivvorlage samt vorgeschlagenem Parameterkorridor im Datensatz frei. Qualifizierte Rasterangebote als raster_ready vorlegen.');
  }else if(['motif_approved','raster_review'].includes(value.facts.state)){
   lines.push('Schritt 3: Die bereits freigegebene Rasterproduktion bis zu qualifizierten Rasterangeboten fortsetzen.');
  }else if(value.facts.state==='raster_ready'){
   if(!selected||selected.kind!=='raster')throw Error('Bitte ein qualifiziertes Rasterangebot wählen.');
   lines.push(`Schritt 4: Ich wähle das qualifizierte Raster aus Angebot ${selected.id}. Drei Kontextzeichnungen als background_review zur Auswahl vorlegen; noch keine Endabnahme oder Integration.`);
  }else{
   const final=finalAssets(value,intent);
   if(value.facts.state==='background_review'){
    lines.push(final.choice==='none'?'Schritt 5: Ich entscheide mich ausdrücklich für keinen Hintergrund.':`Schritt 5: Ich wähle die unveränderte Kontextzeichnung aus Angebot ${final.choice}.`);
    lines.push('Ich erteile die Endabnahme für diese Hintergrundentscheidung zusammen mit dem gewählten Raster und dem zugehörigen Reveal im gebundenen Datensatz und beauftrage deren Integration.');
   }else if(value.facts.state==='registered')lines.push('Schritt 5: Git-/PR-Abschluss der bereits registrierten unveränderten Lieferung fortsetzen.');
   else if(value.facts.state==='editorially_approved')lines.push('Schritt 5: Die bereits endabgenommene unveränderte Lieferung integrieren.');
   else lines.push('Schritt 5: Ich erteile die Endabnahme der gebundenen unveränderten Raster-, Reveal- und Hintergrundfassung (gegebenenfalls none) und beauftrage deren Integration.');
  }
  const published=value?.facts.published;
  if(n===1&&intent.notes?.trim())lines.push(`Neue/zusätzliche Motivhinweise:\n${intent.notes.trim()}`);
  if(n<=2||(n===3&&action==='rework')){
   const grid=value?gridChanges(value,intent):gridRequest(intent.grid);
   if(grid){
    lines.push(`${published?'Neue Absicht gegenüber den veröffentlichten Vorgaben':'Vorgaben für das spätere Lösungsraster'}: ${grid}`);
    if(n===3||published?.approved?.length)lines.push('Geänderten Parameterkorridor über den Korrekturweg zur erneuten Entscheidung vorlegen.');
   }
  }
  if((n===2||(n===3&&action==='rework'))&&intent.parameters?.trim())lines.push(`Neue/zusätzliche Wünsche zur Motivvorlage: ${intent.parameters.trim()}`);
  if(n===4&&intent.context?.trim())lines.push(`Kontextwunsch: ${intent.context.trim()}`);
  if(opts.workroot.trim())lines.push(`Lokale Codex-Arbeitswurzel: ${opts.workroot.trim()}.`);
  if(closing(value,intent)&&opts.merge)lines.push('Commit, Push und PR; unabhängiges Review, danach Squash-Merge nur bei erfüllten aktuellen Vor-Merge-Gates. Bestätigten Mainabschluss und Produktionsabschluss nach Authoring §9 durchführen.');
  else lines.push('Commit, Push und Draft-PR im beauftragten Umfang; kein Merge.');
  return lines.join('\n\n');
 }
 return {steps,step,orderStep,prompt,publishedGrid,options,closing,finalAssets};
})();
if(typeof module!=='undefined')module.exports=PW;
