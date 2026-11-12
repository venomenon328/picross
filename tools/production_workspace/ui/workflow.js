'use strict';
/* Pure prompt projection. A browser choice never advances production state. */
const PW = (()=>{
 const steps=['Abschlussbilder','Motivvorlage','Rasterangebote','Kontextzeichnungen','Integration'];
 const phase={brief_ready:1,reveal_review:1,motif_review:2,motif_approved:3,raster_review:3,raster_ready:3,background_review:4,content_ready:5,editorially_approved:5,registered:5};
 function step(value){return value?phase[value.facts.state]||null:1;}
 function orderStep(value){
  return ({reveal_review:2,motif_review:3,raster_ready:4})[value?.facts.state] || step(value);
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
  // Only losslessly representable fields are prefilled. Raw originals stay visible.
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
   if(removed[axis]){
    changes.push(`${label}: bisherigen Wunsch ausdrücklich aufheben; ${label} passend zum Motiv bestimmen. Andere Vorgaben bleiben bestehen.`);
   }else if((next[axis]||'')!==(base[axis]||'')||(next[axis]&&next.sizeAccuracy!==base.sizeAccuracy)){
    if(!next[axis])throw Error(`${label} ausdrücklich aufheben oder einen Wert angeben.`);
    changes.push(axisRequest(axis,next[axis],next.sizeAccuracy));
   }
  }
  const groups=[['mode','Rastermodus',['mode']],['colors','Farbzahl',['colors','colorAccuracy']]];
  for(const [group,label,keys] of groups){
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
 function integer(value, min, max, label){
  if(!/^\d+$/.test(value) || Number(value)<min || Number(value)>max){
   throw Error(`Bitte für ${label} eine ganze Zahl von ${min} bis ${max} eingeben.`);
  }
  return Number(value);
 }
 function accuracy(value){
  if(!value || value==='approx')return 'ungefähr';
  if(value==='exact')return 'exakt';
  throw Error('Bitte die Genauigkeit der Rastervorgabe wählen.');
 }
 function axisRequest(axis,value,precision){
  const label=axis==='width'?'Breite':'Höhe';
  return `${label}: ${accuracy(precision)} ${integer(value,1,50,'die '+label)} Zellen.`;
 }
 function colorRequest(value,precision){
  return `Farbzahl: ${accuracy(precision)} ${integer(value,2,8,'die Farbzahl')} Vordergrundfarben (ohne Leerfelder).`;
 }
 function modeRequest(mode){
  if(!['mono','color'].includes(mode))throw Error('Bitte einen gültigen Rastermodus wählen.');
  return mode==='mono'?'Rastermodus: monochrom, genau eine Vordergrundfarbe.':'Rastermodus: farbig.';
 }
 function gridRequest(grid = {}){
  const parts = [];
  for(const [axis,label] of [['width','Breite'],['height','Höhe']]){
   parts.push(grid[axis]?axisRequest(axis,grid[axis],grid.sizeAccuracy):`${label} passend zum Motiv bestimmen.`);
  }
  if(grid.mode)parts.push(modeRequest(grid.mode));
  if(grid.mode==='color'){
   if(grid.colors)parts.push(colorRequest(grid.colors,grid.colorAccuracy));
  }
  return parts.join(' ');
 }
 function prompt(value,intent,options){
  const n=orderStep(value),action=intent.action||'continue';
  if(!n)throw Error('Dieser Stand benötigt einen eigenen ausdrücklich beauftragten Folgeauftrag.');
  if(value&&value.facts.authoring_version!=='0.8.0')throw Error('Dieser historische Stand gehört nicht zum neuen 0.8-Produktionsweg.');
  const remote=value?.source_url?.match(/^https:\/\/github\.com\/([A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+)\/tree\/([a-f0-9]{40})$/);
  if(value&&(!remote||value.commit!==remote[2]))throw Error('Remote-Sicherung nicht bestätigt. Originale und Projektion zuerst pushen, dann Quellen aktualisieren.');
  if(!['continue','rework','resume','background_change'].includes(action))throw Error('Bitte eine gültige Aktion wählen.');
  const lines=[`Repository: ${remote?.[1]||'venomenon328/picross'}. Verbindlich: AGENTS.md und docs/ai-workflows/PUZZLE_AUTHORING.md (Authoring 0.8.0) im aktuellen main.`];
  if(value){
   if(!/^pz-[a-z0-9]+(?:-[a-z0-9]+)*$/.test(value.puzzle_id)||
      !/^[A-Za-z0-9][A-Za-z0-9._-]{0,31}$/.test(value.revision)||
      value.record?.file!==`content/authoring/${value.puzzle_id}/${value.revision}/record.json`){
    throw Error('Der kanonische Produktionsrecord ist nicht eindeutig gebunden.');
   }
   lines.push(`Produktionsdatensatz: https://github.com/${remote[1]}/blob/${remote[2]}/${value.record.file}`);
  }else{
   if(!intent.brief?.trim())throw Error('Bitte zuerst dein Motiv beschreiben.');
   lines.push(`Neues Motiv: ${intent.brief.trim()}`);
   if(intent.inputImage)lines.push(`Eigene Eingangsdatei: ${intent.inputImage}. Ich füge die tatsächliche Datei diesem Auftrag bei; falls sie fehlt, vor Bildarbeit anfordern.`);
   lines.push('Es existiert noch kein Produktionsdatensatz.');
  }
  const selected=value?.offers.find(o=>o.id===intent.selection&&o.kind===intent.kind);
  if(action==='background_change'){
   if(value?.facts.state!=='registered')throw Error('Eine spätere Hintergrundrevision braucht einen tatsächlich registrierten Stand.');
   if(!intent.feedback?.trim())throw Error('Bitte die gewünschte Hintergrundänderung beschreiben.');
   lines.push(`Separater späterer Hintergrundauftrag nach docs/PUZZLE_BACKGROUNDS.md §7.6 / HP-I1b2: ${intent.feedback.trim()}`);
  }else if(action==='rework'){
   if(!intent.feedback?.trim())throw Error('Bitte die gewünschte Korrektur beschreiben.');
   lines.push(`Korrektur in Schritt ${n}: ${intent.feedback.trim()}.`);
   if(selected)lines.push(`Betroffenes Angebot: ${selected.kind}/${selected.id}.`);
  }else if(action==='resume'){
   lines.push(`Schritt ${n} am gebundenen Datensatz wieder aufnehmen; vorhandene Entscheidungen und etwaige Recoveryreste prüfen.`);
  }else if(!value||value.facts.state==='brief_ready'){
   lines.push('Schritt 1: Erzeuge drei unterschiedliche echte detaillierte farbige Abschlussbilder und lege die gespeicherten Originale zur Auswahl vor.');
   lines.push('Prüfe Motiv, Stil, Transparenz und Alphakanten direkt an den Originalen, bei Bedarf auf neutralem Grund oder Schachbrett. Keine routinemäßigen Buch-/Katalogmontagen, Überblendungsproben oder Testintegrationen und keine Verlagerung dieser Arbeit in spätere Schritte.');
  }else if(value.facts.state==='reveal_review'){
   if(!selected||selected.kind!=='reveal')throw Error('Bitte ein Abschlussbild wählen.');
   lines.push(`Schritt 2: Ich wähle und gebe das unveränderte Abschlussbild aus Angebot ${selected.id} frei. Motivvorlage und empfohlenen Parameterkorridor zur Freigabe vorlegen.`);
  }else if(value.facts.state==='motif_review'){
   lines.push('Schritt 3: Ich gebe die im gebundenen Datensatz vorgelegte unveränderte Motivvorlage samt vorgeschlagenem Parameterkorridor frei. Rasterangebote produzieren.');
  }else if(['motif_approved','raster_review'].includes(value.facts.state)){
   lines.push('Schritt 3: Die bereits freigegebene Rasterproduktion fortsetzen.');
  }else if(value.facts.state==='raster_ready'){
   if(!selected||selected.kind!=='raster')throw Error('Bitte ein qualifiziertes Rasterangebot wählen.');
   lines.push(`Schritt 4: Ich wähle das qualifizierte Raster aus Angebot ${selected.id}. Drei Kontextzeichnungen zur Auswahl erstellen; dies ist noch keine Endabnahme oder Integrationsfreigabe.`);
  }else if(value.facts.state==='background_review'){
   if(intent.selection==='none')lines.push('Schritt 4: Ich entscheide mich ausdrücklich für keinen Hintergrund. Zur Endabnahme vorbereiten.');
   else{
    if(!selected||selected.kind!=='background')throw Error('Bitte einen Hintergrund oder bewusst keinen wählen.');
    lines.push(`Schritt 4: Ich wähle die unveränderte Kontextzeichnung aus Angebot ${selected.id}. Zur Endabnahme vorbereiten.`);
   }
  }else if(value.facts.state==='registered'){
   lines.push('Schritt 5: Den Git-/PR-Abschluss der gebundenen registrierten Lieferung prüfen und im erteilten Umfang fortsetzen.');
  }else if(value.facts.state==='editorially_approved'){
   lines.push('Schritt 5: Die bereits endabgenommene unveränderte Lieferung integrieren; vorhandene Registrierung/Recovery berücksichtigen.');
  }else{
   lines.push('Schritt 5: Ich erteile die abschließende redaktionelle Freigabe für die im gebundenen Datensatz bezeichnete Raster-, Reveal- und Hintergrundfassung (gegebenenfalls none) und beauftrage deren Integration.');
  }
  const published=value?.facts.published;
  if(n===1 && intent.notes?.trim())lines.push(`Neue/zusätzliche Motivhinweise für die Abschlussbilder:\n${intent.notes.trim()}`);
  if(n<=2 || (n===3 && action==='rework')){
   const grid=value?gridChanges(value,intent):gridRequest(intent.grid);
   if(grid){
    lines.push(`${published?'Neue Absicht gegenüber den veröffentlichten Vorgaben':'Vorgaben für das spätere Lösungsraster'}: ${grid}`);
    if(n===1)lines.push('Halte diese Vorgaben im veröffentlichten Motivbriefing für den Folgeauftrag fest. Das Abschlussbild bleibt detailliert und farbig.');
    if(n===3||published?.approved?.length)lines.push('Lege den geänderten Parameterkorridor über den Korrekturweg zur erneuten Entscheidung vor. Bis dahin gilt die bisherige Freigabe.');
   }
  }
  if((n===2||(n===3&&action==='rework'))&&intent.parameters?.trim())lines.push(`Neue/zusätzliche Wünsche zur Motivvorlage: ${intent.parameters.trim()}. Materielle Änderungen am freigegebenen Korridor zuerst zur Entscheidung vorlegen.`);
  if(n===3)lines.push('Offene/ungefähre Endvorgaben trotz konkreter Importstarts erhalten. Kleine motivische Rastermängel und erlaubte leere Außenlinien auch bei gelöster Logik über den regulären festen C-Weg korrigieren; echte Freigabe, Schutzmaske und kumulative Budgets beachten. Historische manuelle Sonderwege bleiben getrennt.');
  if(n===4&&intent.context?.trim())lines.push(`Kontextwunsch: ${intent.context.trim()}.`);
  if(options.workroot?.trim()){
   lines.push(`Lokale Codex-Arbeitswurzel: ${options.workroot.trim()}.`);
   lines.push('Neue eigene Checkouts, Worktrees, Downloads und temporäre Arbeitsdaten ausschließlich innerhalb dieser Arbeitswurzel anlegen. Ist sie nicht verfügbar, den Konflikt melden und keinen Ersatzpfad wählen.');
  }
  lines.push('Keine zusätzliche Abschlussbereinigung lokaler Arbeitsdaten beauftragt; der fachliche Produktionsabschluss nach Authoring §9 bleibt davon getrennt.');
  lines.push(n===5&&options.merge?'Merge ausdrücklich nur nach aktuellem unabhängigen Review und sämtlichen Vor-Merge-Gates; bestätigten Mainabschluss getrennt melden.':'Commit, Push und Draft-PR im beauftragten Umfang; kein Merge.');
  return lines.join('\n\n');
 }
 return {steps,step,orderStep,prompt,publishedGrid};
})();
if(typeof module!=='undefined')module.exports=PW;
