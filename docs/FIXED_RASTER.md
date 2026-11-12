# Reguläre feste Rasterableitung · #596/C

Vertrag vor Code, 12.11.2026. Maßgeblich ist [Paket C](https://github.com/venomenon328/picross/issues/596#issuecomment-6823856141).
Authoring 0.8.0, Dokumentrevision 4; Handoff v4, Record v3 und Präsentation v2
bleiben unverändert. Historische manuelle Autorisierungen bleiben getrennt.

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
entspricht vollständig einem Eintrag. Die normalen Kandidatenbudgets (vier,
begründet sechs) gelten weiterhin kumulativ; acht ist nur die technische Grenze.

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
Sie gelten für einen vollständigen festen Versuch, nicht je Zelle. Wiederholungen
oder neue Namen setzen den fachlichen Aufwand nicht zurück. Certification ist
null für Linien oder die bestehende exakte Paarprofilkonfiguration. Ein
Paarimport verlangt dieselbe Konfiguration; kein Downgrade. Rationale ist ein
nichtleerer Text bis 4096 Zeichen, benennt den konkreten Motivfehler/Leerraum.
Auch solved-Eingänge dürfen so verbessert werden; gute Kandidaten unverändert
lassen. Ein vollständig unveränderter Plan wird als No-op ohne neues Bundle
abgewiesen. Materielle Änderungen außerhalb der Freigabe benötigen Entscheidung.

## Ergebnis, Dateien und Replay

CLI: `python -m tools.puzzle_production.fixed_raster derive --root ROOT --plan PLAN --output OUT`.
OUT muss fehlen; keine Überschreibung. Fehler liefern Exit 2, Ressourcenende 4.
`inspect --root ROOT --bundle BUNDLE` prüft das geschriebene Bundle erneut.
Alle JSON-Dateien sind kanonisches UTF-8 mit End-LF; semantische Hashes binden
kanonisches JSON ohne End-LF, Dateihashes tatsächliche Bytes. Dateinamen sind
geschlossen, keine Links oder zusätzlichen Dateien. Plan/Record je höchstens
1 MiB, Proofs behalten die bestehenden profilabhängigen Grenzen.

`picross-fixed-raster-manifest-v1` hat exakt `format,tool,files`.
Tool ist exakt `{name,version,modules}` mit name `fixed-raster`, version 1 und
SHA-256 der Produzentenmodule fixed_raster.py/raster_parameters.py. Die Hashes
dokumentieren den Produzenten; aktuelle Prüfung rekonstruiert alle Inhalte.
Files bindet exakt `plan.json,record.json,logic.json,proof.json,result.json,
replay.json,raster.png`, bei Paarprofil zusätzlich `baseline-proof.json,assessment.json`.

`picross-fixed-raster-v1` hat exakt `format,puzzle_id,revision,plan_sha256,
reference_manifest_sha256,import_design,design,matrix,matrix_hash,logic_hash,base_status`.
Importdesign bleibt unverändert; design ist dessen Kopie mit allein abgeleiteten
Endmaßen. Matrix ist exakt die editierte Originalmatrix im Crop. Base_status ist
der frisch bestätigte solved/stalled-Status, kein umetikettiertes Zertifikat.
Replay ist exakt `{plan_sha256,matrix_hash,logic_hash,status,proof_verified,certified}`.
Result folgt dem bestehenden Verifierresultat. Beide müssen solved und zertifiziert
sein; der endgültige Proof entsteht unbekannt startend, wird von einem frischen
unabhängigen Prozess geprüft und muss exakt die Endmatrix ergeben. Paarproof,
getrennte Baseline und R4-Assessment behalten ihre bisherigen Regeln.

Vor jedem Replay werden Original, Normalisierung, Importmatrix, Hinweise und
gespeicherter Originalproof frisch geprüft. Ein gültiger bestätigter stalled-Import
ist zulässig. Abbruch/Widerspruch/ungültiger Proof sind keine Ausgangsbasis.
Dateihashes, Planidentität und rekonstruierte Recordbytes müssen exakt stimmen.

## Reguläre Übergabe

Candidate hat `source_type=fixed`, `variant=fixed`, proof `BUNDLE/proof.json`.
Repair hat exakt `type=fixed_edits_empty_crop,reference,reference_variant,plan,
record,replay`; die drei Dateien liegen im ausgewählten Bundle. Keine externe
manuelle Autorisierung. Unveränderte Bildfreigaben bleiben gültig. Matrixgebundene
Hinweise, Proofs, Paletten-/Sichturteile, Motiv-/Revealbeurteilung und Schwierigkeit
müssen zum Ende passen. Die Randregel bleibt (left OR right) AND (top OR bottom).

Die historische production.difficulty 0.1/0.2 bleibt getrennt. Der bestehende
`catalog_analysis candidate → analyze --method picross-difficulty-0.4 → import`
erzeugt zusätzlich eine echte Checked-v3-Bewertung aus dem Enddesign, der Endmatrix
und Endlogik. Der aktive Default steht in content/difficulty-method.json; der
CLI-Default 0.3 ist dafür ungeeignet. Das Checked-Objekt liegt in der inventarisierten
Analyseablage, nicht im historischen difficulty-Objekt. Identische vollständige
Bindung darf frisch geprüft wiederverwendet werden; geänderte Matrix erfordert
neue Analyse, Metadatenänderung allein den bestehenden Rebind.

Builder liest das tatsächlich geschriebene ZIP frisch. Erst alle Inhaltsgates
ergeben raster_ready, qualifiziertes Rasterangebot, workspace.json und current-view.
Background und raster_selection bleiben null; keine Endfreigabe wird erfunden.
Fehlende Nachweise blockieren oder bleiben raster_review. Der HTTP-Leser prüft
Datei-/Matrixbindungen ohne Solver/Writer. Späterer Export prüft denselben regulären
Ableitungsweg mit den dann wirklich vorliegenden Auswahl-/Hintergrund-/Endfreigaben.
