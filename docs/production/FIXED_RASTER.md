# Reguläre feste Rasterableitung · #596/C

Dokument-ID: `fixed-raster`
Status: `active`
Zuständigkeit: Parameter, Plan, reproduzierbares Bundle und Replay der festen
Rasterableitung. Aktuelle Handoff-/Recordgenerationen und Quellenauswahl stehen
in [Authoring](authoring/PUZZLE_AUTHORING.md) und [PW-B](../tools/PW_B_CONTRACT.md).
Die Einführung ist in [#596/C](https://github.com/venomenon328/picross/issues/596#issuecomment-6823856141)
gebunden; historische manuelle Autorisierungen bleiben eigene Verträge.

## Parameter und Befugnis

`picross-raster-parameters-v1` hat exakt `format,constraints,imports,derivation`.
`constraints` enthält exakt `width,height,foreground_colors`, jeweils exakt
`kind,target,minimum,maximum`. Kind ist `exact`, `approximate` oder `open`.
Open verlangt target null, sonst positive Ganzzahl. Grenzen sind null oder
positive Ganzzahlen, geordnet und mit target vereinbar. Nur ausdrücklich
freigegebene Grenzen eintragen; approximate erfindet keine Prozenttoleranz.
Exact verlangt Gleichheit. Start und Ende liegen in 1..50 je Achse; tatsächlich
genutzt werden mono genau eine, color zwei bis acht Vordergrundfarben.

`imports` enthält 1..8 kanonisch unterschiedliche Einträge mit exakt
`width,height,mode,foreground_colors,method,fit,actual_crop`. Methode area/contour,
Fit exact/contain, actual_crop sind vier orientierte Bildpixelkoordinaten wie RP-3,
kein Zellbeschnitt. Alle Einträge haben denselben Modus. Der ausgewählte Import
entspricht vollständig einem Eintrag. Das redaktionelle Kandidatenbudget folgt [Authoring Schritt 3](authoring/PUZZLE_AUTHORING_STEP_3.md);
acht ist ausschließlich die technische Grenze dieser Parameterform.

`derivation` enthält exakt `cell_edits` (bool), `empty_edge_crop` (eindeutige
Liste aus left/top/right/bottom), `protected_features` (höchstens 64 nichtleere
Merkmaltexte, je höchstens 4096 Zeichen). Exact width verbietet left/right,
exact height top/bottom bereits im Korridor. Vor Ausführung werden alle Merkmale
in einer vollständigen booleschen Zellmaske abgebildet, auch geschützte Leerzellen.
Die fachliche Richtigkeit dieser Zuordnung bleibt redaktionell zu beurteilen.
`approved_parameters` enthält genau diesen einen Korridor; die echte
Motivfreigabe trägt kanonisch denselben in `parameters`. Vorschläge dürfen
dieselbe Form verwenden, erteilen aber keine Befugnis. Alte einfache Formen
behalten ihren Vertrag. Die Ansicht zeigt den vollständigen Korridor, ohne
offene oder ungefähre Vorgaben als exakte Formulareingaben auszugeben.

Liegt ein motivtreuer Zuschnitt aus ausschließlich erlaubten, ursprünglich
leeren und ungeschützten Außenlinien unter dem freigegebenen Minimum einer
ungefähren Achse, die tatsächlichen Maße und Ansichten vor und nach dem
Beschnitt mit der verletzten Grenze nach
[Schritt 3 §4.5](authoring/PUZZLE_AUTHORING_STEP_3.md#45-geprüfte-raster-zur-menschlichen-auswahl)
als `Sichtungsentwurf – nicht integrationsbereit` zeigen. Konkret angeben,
welche Unter- oder Obergrenze geändert werden soll und welche Werte gelten
bleiben. Den Vorschlag ausdrücklich freigeben lassen und den aktualisierten
Korridor identisch an Parameter und Motivfreigabe binden, bevor eine gültige
feste Ableitung darauf gestützt wird. Eine Befundannahme ändert diese Bindung
nicht. Die regulären Grenzen und der Motivschutz gelten für jeden Vorschlag.

## Geschlossener Plan

`picross-fixed-raster-plan-v1` hat exakt `format,puzzle_id,revision,reference,
motif,parameters,import_hash,protected_mask,edits,crop,budgets,certification,rationale`.
ID/Revision folgen Authoring. Reference ist exakt
`{bundle,variant,manifest_sha256,matrix_hash,logic_hash}`; bundle ist ein sicherer
relativer Pfad ab Quellenwurzel. Nur direkte RP-3-Manifeste v1/v2 sind erlaubt,
keine RP-5- oder Ableitungsketten. Motif ist exakt `{file,sha256,approval}`,
approval exakt `{file,sha256}`, beide Pfade ab Quellenwurzel. Der Import muss
dieses unveränderte Original benutzen. `import_hash` ist der kanonische SHA-256
des vollständigen ausgewählten Importobjekts, niemals ein Listenindex.

Maske ist exakt Höhe × Breite bool. Edits sind höchstens 2500 eindeutige Objekte
`{x,y,before,after}`, nullbasierte Originalkoordinaten, echte Vorwerte und
unterschiedliche Nachwerte aus unveränderten Palette-IDs oder empty. Geschützte
Zellen sind unveränderbar. Crop ist `[left,top,right,bottom]`, halb offen im
Originalzellraster; voller Ausschnitt bedeutet keinen Beschnitt. Alle Edits liegen
im erhaltenen Rechteck. Jede entfernte Zelle muss schon im unberührten Original
leer und ungeschützt sein. Nur freigegebene Außenseiten dürfen entfallen.
Kein inneres Löschen, Skalieren, Spiegeln, Umfärben oder verstecktes Edit.

Budgets hat exakt `max_changes,solve_seconds,solve_lines,verify_seconds,verify_lines`:
0..2500 Änderungen, Zeit jeweils endlich >0 bis 120 Sekunden, Linien 1..1000000.
Solve gilt für das vollständige Endzertifikat; Verify begrenzt jeweils die
Quellrekonstruktion und die separate unabhängige Endprüfung, nicht jede Zelle.
Ein engerer umgebender Prüfer begrenzt beide zusätzlich kumulativ. Wiederholungen
oder neue Namen setzen den fachlichen Aufwand nicht zurück. Certification ist
null für Linien oder die bestehende exakte Paarprofilkonfiguration. Ein
Paarimport verlangt dieselbe Konfiguration; kein Downgrade. Rationale ist ein
nichtleerer Text bis 4096 Zeichen, benennt den konkreten Motivfehler/Leerraum.
Auch solved-Eingänge dürfen so verbessert werden; gute Kandidaten unverändert
lassen. Ein vollständig unveränderter Plan wird als No-op ohne neues Bundle
abgewiesen. Materielle Änderungen außerhalb der Freigabe benötigen Entscheidung.

## Ergebnis und aktuelle Übergabe

Feste Änderungen und Schutzmaske werden vor der konkreten Operation geprüft.
Die Endprüfung verlangt für tatsächliche Endmaße und verwendete Farbzahl
die Einhaltung des gebundenen genehmigten `picross-raster-parameters-v1`-Korridors.
Ein diagnostischer Zuschnitt außerhalb dieses Korridors besteht die Endprüfung
nicht. Jede Zell- oder Maßänderung, auch reiner leerer Außenbeschnitt,
erfordert eine neue Rasterrevision, neu erzeugte Hinweise, einen vollständigen
frischen Deduktionsproof mit unabhängiger Prüfung und Endmatrixvergleich sowie
eine neu gebundene Difficulty aus der frischen Bewertung des Endrasters.
Der bestehende Ableitungshelfer darf seine gebundenen Pläne/Quellen während der
laufenden Operation temporär benötigen. Sie sind keine dauerhafte Voraussetzung
für das aktuelle Ergebnis. Keine erfolglosen Raster/Proofs, Reparaturpläne oder
Normalisierungs-/Generator-/Toolhashketten veröffentlichen oder rekonstruieren.

Die aktuelle Übergabe nach [PW-B](../tools/PW_B_CONTRACT.md) besteht aus endgültiger
Definition/Matrix/Hinweisen/Palette, aktuellem Proof mit unabhängiger Prüfung und
Endmatrixvergleich, passender aktueller Difficulty, Rasterpreview und gebundenen
aktuellen Sichturteilen. Motiv-/Parameterkonformität und echte Freigaben bleiben
Pflicht. Geänderte Logik verlangt neue aktuelle Nachweise; unveränderte Bilder
verlangen keine neue kreative Entscheidung.

`python -m tools.puzzle_production.current_tools raster --input DEFINITION
--mode mono|color --output-dir NEU` benutzt die vorhandenen Solver-/Verifier-/
Analysealgorithmen, prüft den geschriebenen Proof zusätzlich in einem frischen
Prozess und erhält nur aktuelle Nutzdateien. Paarprofil wird ausdrücklich mit
`--profile paired` gewählt. Bei stalled bleibt Difficulty null und das Ergebnis
ein Sichtungsentwurf. Die Integration konsumiert ausschließlich den aktuellen
RI-ONE-Eingang, kein Import-/Reparaturreplay oder altes Paket.

Die früheren geschlossenen Plan-/Record-/Manifest-/Replayformen bleiben am
[Mainanker vor PROD-SLIM](https://github.com/venomenon328/picross/blob/d389fbad01dd01860ed949a4e1e8e0b52c21362a/docs/production/FIXED_RASTER.md)
dokumentiert; ihr damaliger Fortbestand ist keine neue Ergebniszulassung.
