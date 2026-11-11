'use strict';
/* Pure prompt projection. A browser choice never advances production state. */
const PW = (()=>{
 const steps=['Abschlussbilder','Motivvorlage','Rasterangebote','Kontextzeichnungen','Integration'];
 const phase={brief_ready:1,reveal_review:1,motif_review:2,motif_approved:3,raster_review:3,raster_ready:3,background_review:4,content_ready:5,editorially_approved:5,registered:5};
 function step(value){return value?phase[value.facts.state]||null:1;}
 function prompt(value,intent,options){
  const current=step(value),n=({reveal_review:2,motif_review:3,raster_ready:4})[value?.facts.state]||current,action=intent.action||'continue';
  if(!n)throw Error('Dieser Stand benötigt einen eigenen ausdrücklich beauftragten Folgeauftrag.');
  if(value&&value.facts.authoring_version!=='0.8.0')throw Error('Dieser historische Stand gehört nicht zum neuen 0.8-Produktionsweg.');
  const remote=value?.source_url?.match(/^https:\/\/github\.com\/([A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+)\/tree\/([a-f0-9]{40})$/);
  if(value&&(!remote||(value.commit&&value.commit!==remote[2])))throw Error('Remote-Sicherung nicht bestätigt. Originale und Projektion zuerst pushen, dann Quellen aktualisieren.');
  const lines=[`Auftrag an ${[1,2,4].includes(n)?'ChatGPT':'Codex'}. Repository: ${remote?.[1]||'venomenon328/picross'}. Lies AGENTS.md und docs/ai-workflows/PUZZLE_AUTHORING.md im aktuellen main. Neue Produktion nach Authoring 0.8.0.`];
  if(value){
   lines.push(`Verbindlicher Arbeitsstand: ${value.source_url}. Rätsel ${value.puzzle_id}, Revision ${value.revision}. Produktionsbranch content/pw/${value.puzzle_id}.`,
    `Lies ${value.record.file} (SHA-256 ${value.record.sha256}) und ${value.record.file.replace(/record\.json$/,'workspace.json')} aus genau diesem Commit.`);
  }else{
   if(!intent.brief?.trim())throw Error('Bitte zuerst dein Motiv beschreiben.');
   lines.push(`Neues Motiv: ${intent.brief.trim()}`);
   if(intent.inputImage)lines.push(`Eigene Eingangsdatei: ${intent.inputImage}. Ich füge die tatsächliche Datei diesem Auftrag bei; falls sie fehlt, vor Bildarbeit anfordern.`);
   lines.push('Vergib die neue Rätsel-ID erst im Produktionsauftrag und lege genau einen Branch content/pw/<puzzle_id> von main an. Es existiert noch kein Produktionsstand.');
  }
  const selected=value?.offers.find(o=>o.id===intent.selection&&o.kind===intent.kind);
  if(action==='background_change'){
   if(value?.facts.state!=='registered')throw Error('Eine spätere Hintergrundrevision braucht einen tatsächlich registrierten Stand.');
   if(!intent.feedback?.trim())throw Error('Bitte die gewünschte Hintergrundänderung beschreiben.');
   lines.push(`Separater späterer Hintergrundauftrag: ${intent.feedback.trim()}. Prüfe zuerst bestätigte Mainintegration und die tatsächliche aktive Source-/Runtimebindung. Verwende ausschließlich den bestehenden Hintergrundänderungsweg nach PUZZLE_BACKGROUNDS §7.6 und HP-I1b2: drei isolierte Originalangebote, tatsächliche Auswahl oder none, gültige Entscheidung und Ableitung, frischer Plan und sichere Adoption/Recovery. Erhalte Rasterlogik und gültige Raster-/Revealfreigaben. Kein neuer Rasterbau und keine Wiederholung der Endabnahme für unveränderte Inhalte.`);
  }else if(action==='rework'){
   if(!intent.feedback?.trim())throw Error('Bitte die gewünschte Korrektur beschreiben.');
   lines.push(`Korrektur in Schritt ${n}: ${intent.feedback.trim()}.`);
   if(selected)lines.push(`Betroffenes Angebot: ${selected.kind}/${selected.id}, Record ${selected.record.file}, SHA-256 ${selected.record.sha256}.`);
   lines.push('Erhalte freigegebene unveränderte Merkmale. Neue Bytes benötigen die abhängigen neuen Prüfungen und Entscheidungen; kein automatisches Fortschreiten.');
  }else if(action==='resume'){
   lines.push(`Nimm Schritt ${n} am gebundenen Gitstand wieder auf. Prüfe tatsächliche Eingänge, Ergebnisse und etwaige Recoveryreste; melde den nächsten ausführbaren Schritt. Keine fehlenden Entscheidungen erfinden.`);
  }else if(!value||value.facts.state==='brief_ready'){
   lines.push('Schritt 1: Erzeuge drei unterschiedliche echte detaillierte farbige Abschlussbilder und lege die gespeicherten Originale zur Auswahl vor.');
  }else if(value.facts.state==='reveal_review'){
   if(!selected||selected.kind!=='reveal')throw Error('Bitte ein Abschlussbild wählen.');
   lines.push(`Schritt 2: Ich wähle und gebe das unveränderte Abschlussbild ${selected.id} aus ${selected.record.file} (SHA-256 ${selected.record.sha256}) frei. Leite daraus eine Motivvorlage ab, empfehle den Parameterkorridor und lege beides zur Freigabe vor.`);
  }else if(value.facts.state==='motif_review'){
   lines.push('Schritt 3: Ich gebe die im gebundenen Record vorgelegte unveränderte Motivvorlage samt dort vorgeschlagenem Parameterkorridor frei. Produziere innerhalb der Authoringbudgets qualifizierte Rasterangebote; zeige brauchbare nicht qualifizierte Entwürfe getrennt mit ihren konkreten Lücken.');
  }else if(['motif_approved','raster_review'].includes(value.facts.state)){
   lines.push('Schritt 3: Setze die ausdrücklich freigegebene Rasterproduktion innerhalb der gebundenen Parameter und Budgets fort. Prüfe Proof, Eindeutigkeit durch vollständige Deduktion, Qualität, Palette und Schwierigkeit.');
  }else if(value.facts.state==='raster_ready'){
   if(!selected||selected.kind!=='raster')throw Error('Bitte ein qualifiziertes Rasterangebot wählen.');
   lines.push(`Schritt 4: Ich wähle das qualifizierte Raster ${selected.id} aus ${selected.record.file} (SHA-256 ${selected.record.sha256}) am genannten Quellcommit. Halte meine tatsächliche Auswahl mit Inventar-, Raster-, Reveal- und Motivbindung als raster-selection-v1 fest. Erzeuge danach drei unterschiedliche echte isolierte Kontextzeichnungen und veröffentliche background_review.`);
  }else if(value.facts.state==='background_review'){
   if(intent.selection==='none')lines.push('Schritt 4: Ich entscheide mich an diesem vorgelegten Arbeitsstand ausdrücklich für keinen Hintergrund. Halte diese Leerentscheidung und den geprüften Nullbefund fest; lege die vollständige Endabnahme vor.');
   else{
    if(!selected||selected.kind!=='background')throw Error('Bitte einen Hintergrund oder bewusst keinen wählen.');
    lines.push(`Schritt 4: Ich wähle die unveränderte isolierte Kontextzeichnung ${selected.id} aus ${selected.record.file} (SHA-256 ${selected.record.sha256}). Halte meine tatsächliche Entscheidung fest, prüfe Rechte und Sichtbelege und leite die ausgewählte Datei nach dem festen Profil ab. Lege die vollständige Endabnahme vor.`);
   }
  }else if(value.facts.state==='registered'){
   lines.push('Schritt 5: Die Lieferung ist am gebundenen Integrationscommit lokal registriert. Prüfe aktuellen PR, unabhängiges Review und alle offenen Gates. Keine erneute Registrierung oder Endabnahme. Melde einen Mainabschluss nur nach tatsächlich bestätigtem Merge; anschließend revisionsgenauer Produktionsabschluss gemäß Authoring §9.');
  }else if(value.facts.state==='editorially_approved'){
   lines.push('Schritt 5: Die unveränderte Lieferung besitzt bereits eine gebundene Endabnahme. Setze den bestehenden Export-, frischen Plan- und Registrierungsweg fort. Prüfe zuerst tatsächliche Registrierung/Recovery; nicht erneut freigeben oder doppelt integrieren.');
  }else{
   lines.push('Schritt 5: Ich erteile die abschließende redaktionelle Freigabe für die im gebundenen Record exakt bezeichnete Raster-, Reveal- und Hintergrundfassung einschließlich der ausdrücklichen Leerentscheidung, falls vorhanden. Integriere ausschließlich diese Lieferung über den bestehenden Finalizer-, Export-, frischen Plan- und Registrierungsweg.');
  }
  if((n===2||n===3)&&intent.parameters?.trim())lines.push(`Parameterwunsch: ${intent.parameters.trim()}. Materielle Änderungen am freigegebenen Korridor zuerst zur Entscheidung vorlegen.`);
  if(n===4&&intent.context?.trim())lines.push(`Kontextwunsch: ${intent.context.trim()}.`);
  if(options.workroot?.trim())lines.push(`Lokale Codex-Arbeitswurzel: ${options.workroot.trim()}.`);
  lines.push(options.cleanup?'Abschlussbereinigung eigener Arbeitsdaten nach WORKSPACE ausdrücklich beauftragt.':'Keine zusätzliche Abschlussbereinigung beauftragt.');
  lines.push(n===5&&options.merge?'Merge ausdrücklich nur nach aktuellem unabhängigen Review und sämtlichen Vor-Merge-Gates; bestätigten Mainabschluss getrennt melden.':'Commit, Push und Draft-PR im beauftragten Umfang; kein Merge.');
  lines.push('Vor der Übergabe neue Revision, Index und automatisch geprüfte workspace.json mit sämtlichen benötigten Originalen auf demselben Produktionsbranch committen und pushen. Nur tatsächlich erreichte Zustände melden.');
  return lines.join('\n\n');
 }
 return {steps,step,prompt};
})();
if(typeof module!=='undefined')module.exports=PW;
