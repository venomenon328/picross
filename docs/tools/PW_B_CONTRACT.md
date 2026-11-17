# PW-B: aktueller Produktionsstand

Dokument-ID: `authoring-current`
Status: `active`
Stand: 17.11.2026 · [PROD-SLIM / #700](https://github.com/venomenon328/picross/issues/700)

## Phasen und Autorität

Authoring 0.8.0 verwendet genau einen aktuellen Record je Job. Die fünf Schritte
bleiben Abschlussbilder → Motivvorlage → Rasterangebote → Kontext → Integration.
Kreative Regeln und fällige Entscheidungen stehen in [Authoring](../production/authoring/PUZZLE_AUTHORING.md),
Einzelurteile in [Qualität](../production/PUZZLE_QUALITY.md). Technische Prüfung
erzeugt keine menschliche Erklärung. Es gibt keine neue persönliche Abnahmeschleife.

## Geschlossene aktuelle Form

`content/authoring/<puzzle_id>/current/record.json` ist die einzige aktuelle
Metadatenautorität. Format `picross-authoring-current-v1`, exakt:

`format,puzzle_id,revision,source_commit,operation,target,title,category_id,state,brief,parameters,assets,rasters,selected,decisions,budgets,blockers,test_only,integration`.

- `revision=current`; Git bindet den jeweiligen veröffentlichten Stand. Keine Paketkette.
- ID: `pz-[a-z0-9][a-z0-9-]{0,59}`; source_commit: volle 40-stellige kleine Git-SHA zur aktuellen Quellenzuordnung. Kein Snapshot oder historischer Erzeugerzugriff.
- operation: production/background. target ist bei production null, bei reiner Hintergrundpflege exakt definition/reveal als aktive Refs und mode=mono|color. Unveränderte aktive Raster brauchen dafür keinen neuen Proof oder Difficulty. Das aktuelle Rasterpreview wird nur transient aus der Definition gerendert.
- budgets: exakt limits/used, jeweils raster_candidates/repair_rounds/image_corrections als ganze Zähler 0–1.000.000. Used bleibt monoton; Erhöhung eines Limits braucht eine echte budget-Entscheidung. Nur aktueller Budgetverbrauch, keine Versuchsliste oder interne Historie.
- title: 1–128 Zeichen, brief: 1–16384, übrige Texte: 1–4096, ohne NUL; category_id nach Kategorienvertrag, bei ungeklärter Zuordnung null.
- parameters: exakt `proposed,approved`, jeweils Liste mit höchstens acht gültigen vorhandenen Rasterparameterobjekten. Approved braucht eine tatsächliche Motiv-/Parameterentscheidung.
- assets: höchstens 100 Objekte `id,role,label,file,rights,review`. Eindeutige ID nach `[A-Za-z0-9][A-Za-z0-9_-]{0,63}`; role: reveal/motif/background/input. label 1–512 Zeichen. file ist Ref. rights: null bei offener Klärung, sonst exakt `author,usage_basis,source,changes`, mit tatsächlichen Angaben. review: Kriterien-ID → Urteil.
- rasters: höchstens 20 Objekte `id,label,definition,proof,difficulty,preview,review,exceptions`. Definition/preview sind Refs; proof/difficulty bleiben bei ungeprüften Sichtungsentwürfen ausdrücklich null, qualifizierte Angebote brauchen alle vier Refs auf aktuelle Nutzdaten; kein Import-/Reparaturbaum. Definition und Proof müssen dieselbe endgültige Runtime-Farbsemantik verwenden. Difficulty ist der bestehende Checked-Befund. exceptions ist die aktuelle RI-ONE-Liste konkreter frame-/palette-Ausnahmen mit Erklärung und Beleg.
- Urteil: exakt `result,accepted,reason,method,actor,timestamp_utc`; result erfüllt/Warnung/nicht erfüllt/nicht geprüft, accepted bool. Negative und ungeprüfte Befunde bleiben unterscheidbar. Annahme braucht die konkrete echte Entscheidung; harte Kriterien sind nicht redaktionell heilbar.
- selected: exakt `reveal,motif,raster,background`, jeweils ID oder null; background zusätzlich none/standard. Null bedeutet offen. Angebote bleiben bis zur Entscheidung erreichbar. Danach bleiben nur gewählte Dateien und noch benötigte Eingaben.
- decisions: höchstens acht Objekte `scope,binding,actor,timestamp_utc,statement`, je Scope genau eine noch gültige echte Erklärung. scope reveal/motif/raster/background/final/integration/budget; binding ist H des aktuellen semantischen Auswahlscope nach `current_authoring.binding`. UTC explizit Z/+00:00; ein nicht überlieferter Prüfzeitpunkt im Urteil bleibt null. Keine separate kopierte Erklärung, Prompt- oder Korrekturdatei. Tatsächliche Inhaltsänderung invalidiert abhängige Entscheidungen; reine Pfad-/Beschriftungsumstellung gleicher Bytes erhält kreative Wahlen. Endabnahme/Integration binden zusätzlich aktuelles Briefing, Titel/Kategorie, Rechte, Sichturteile und technische Ausnahmen.
- blockers: höchstens 64 konkrete aktuelle Texte. test_only: bool, unveränderlicher Scope. integration: null oder `commit,result` der tatsächlich erreichten aktuellen Lieferung nach RI-ONE; keine historische Receiptdatei.

Ref: exakt `file,sha256,bytes`; sicherer repositoryrelativer POSIX-Pfad,
64 kleine Hexzeichen, positive tatsächliche Bytezahl. Zulässig sind eigene
Dateien unter `content/authoring/<id>/` und tatsächlich benötigte aktive
Produktdateien nach dem bestehenden gezielten Reader. Keine Links, Hardlinks,
Reparsepunkte, Traversal, Windowsgeräte-, Case- oder Datei-/Ordneraliase.
Record höchstens 1 MiB, Definition 2 MiB, Proof 64 MiB, Bild 32 MiB,
sonstige JSON-Nutzdatei 8 MiB, insgesamt höchstens 512 MiB/2048 aktive Dateien.
Tiefe höchstens 32; eindeutige Schlüssel und endliche Zahlen. Kein ZIP,
Regelbuch, Generator-/Codec-/Toolhasharchiv oder Inventar als neue Pflichtdatei.

## Zustände und aktuelle Prüfung

brief_ready/reveal_review brauchen gültiges Briefing und vorhandene Angebote;
motif_review zusätzlich gewähltes freigegebenes Reveal und Motivangebot;
motif_approved/raster_review zusätzlich echte Motiv-/Parameterfreigabe.
raster_ready verlangt für jedes angebotene Raster Maße/Palette/Hinweise,
vollständigen unabhängigen Proof mit Endmatrixvergleich, gebundene Difficulty,
fällige Sichturteile und passende Parameter. Hintergrundarbeit ist vorher kein
Blocker. background_review braucht eine wirkliche qualifizierte Rasterwahl.
content_ready zusätzlich gültigen Hintergrund selected/none/standard, Rechte
und Bildurteile einschließlich H-07. editorially_approved braucht echte Endabnahme
und Integrationsauftrag am aktuellen Auswahlscope; registered zusätzlich einen
frisch bestätigten tatsächlichen Registrierungsstand. Blockierte Arbeit bleibt
in ihrer wirklichen Phase mit konkreten Blockern; kein erfundener Phasenerfolg.

Prüfung beginnt bei aktuellen Ergebnissen, nicht bei ihrer Erzeugung. Kein Replay
von Import, Normalisierung, Reparatur oder Bildableitung als Zulassung. Aktuellen
Proof tatsächlich unabhängig prüfen. Bildqualität, Transparenz/Randabschluss,
Motivtreue, Parameter und reale Nutzungs-/Integrationsbefugnis bleiben erforderlich.
Kein Ergebnisflag ersetzt die jeweilige Prüfung.

## Bau, Auswahl und sichere Fortschreibung

Builderrequest `picross-authoring-current-request-v1`: exakt
`format,record,expected,files`. record ist obige Form; expected ist null für
Neuanlage oder SHA-256 der erwarteten Recordbytes; files enthält ausschließlich
neue benötigte Nutzdateien als `path,source,sha256,bytes` relativ zu explizitem
source_root. Vorhandene aktive Dateien referenzieren, nicht kopieren.
API/CLI bleiben authoring_builder.build beziehungsweise build --request
--source-root --output-root --publish-to. Der aktuelle Weg benötigt publish-to;
kein Benutzer pflegt JSON in der Oberfläche. Der Produktionsakteur erstellt den
Request aus den aktuellen Ergebnissen und tatsächlichen Erklärungen.

Der gemeinsame Authoringwriter prüft Quellen/Altbytes frisch, schreibt neue
Nutzdateien zuerst, wechselt Record und den gemeinsamen Verweisindex atomar
je Datei und entfernt nur entbehrliche zuvor gebundene eigene Nutzdateien.
Ein temporäres geschlossenes Operationsjournal dient ausschließlich einer noch
unvollständigen Publikation. Identischer Request vervollständigt nach Abbruch;
fremde Bytes stoppen. Nach Abschluss Journal und ersetzte/verworfene Dateien
entfernen. Keine Archivierung oder Wartepflicht auf Main. Dateien mit anderer
aktueller Nutzung bleiben erhalten. No-op erhält Bytes und mtimes.

Der Finalizer benutzt dieselbe Fortschreibung und dieselben Guards. Ein aktueller
Auftrag verlangt keine alte ZIP-/Handoff-/Inventar-/Regel-/Angebotskopie.
Veraltete Formen werden ausdrücklich als historische Formen behandelt;
keine automatische Migration oder Wiederherstellung gelöschter Historie.

## Veröffentlichung und Ansichten

Der gemeinsame Index enthält nur `puzzle_id,revision,record`-Verweise nach
Index v1. Aktuelle Records verwenden revision=current. Keine workspace.json
oder current-view.json pro aktuellem Job: Liste, Bilder, Angebote und Folgeauftrag
werden direkt aus dem Record abgeleitet und gegen denselben fixierten Gitstand
geprüft. Der lesende Dienst bleibt ohne fachlichen Writer. Arbeitsref
`content/pw/<id>` sichert die aktuelle Auswahl; unerreichbare Quellen bleiben Fehler.
Öffnen/Kopieren ist keine Entscheidung. Bestehende UI und sichere Remoteauswahl
bleiben erhalten. Auswahlkennungen und Inhaltsbindungen verhindern Verwechslung.

## Übergabe und Abschluss

Die ausgewählten finalen Daten werden über denselben aktuellen RI-ONE-Eingang
nach [ZA-1](../production/ZA1_ADAPTER.md) exportiert. Integration erfolgt in einem
sauberen Branch vom aktuellen Main. Nur gewählte finale Produktdaten und wirklich
benötigte aktive Metadaten übernehmen; niemals den Arbeitsbranch mit Alternativen
und Protokollen nach Main mergen. Completion vergleicht die tatsächliche Lieferung,
auch wenn der Integrationscommit keine Arbeitsdateien enthält. Retirement prüft
bestätigtes Mainergebnis und eigene ausgewählte aktuelle Arbeitsbytes am Arbeitsref;
die Arbeitsdateien müssen nie zuvor in Main gelegen haben. Neue/offene Arbeit,
fremde Bytes und echte Rechte bleiben erhalten. Kein neuer historischer Receipt.

## Historische Formen

Die früheren geschlossenen Paket-/Snapshot-/Projektionsformen sind am
[Mainanker vor PROD-SLIM](https://github.com/venomenon328/picross/blob/d389fbad01dd01860ed949a4e1e8e0b52c21362a/docs/tools/PW_B_CONTRACT.md)
dokumentiert. Ihre Erkennung erlaubt keine neue normale Archivproduktion und
verlangt keine WIP-Migration. Die aktuelle Form ist keine Umbenennung alter Originale.

## Palettenausnahme

Aktuelle Urteile und konkrete technische Ausnahmen stehen direkt am aktuellen
Raster. Die geschlossene Ausnahmeform entspricht dem RI-ONE-Eingang nach ZA-1;
negative Befunde bleiben negativ. Redaktionell ausdrücklich angenommene
Abweichungen bleiben mit result und accepted getrennt. Ungeprüft ist nie zulässig;
H-07 bleibt unabdingbar. Keine Original-ZIP-/Inventar-/Handoffbindung.

## PW-PERF-C · aktuelle Prüfung

Aktuelle Datei-/Inhaltsprüfung und gemeinsame Publikationsguards ersetzen keine
Qualität oder tatsächliche Entscheidung. Historische Ableitungsbefunde sind keine
Zulassungsbedingung für aktuelle Ergebnisse.

## PW-PERF-D · Regelquellen und Snapshotgeneration

Für aktuelle Jobs genügt der aktuelle Quellencommit. Kein neuer Regelwerksnapshot
und kein Zugriff auf frühere Erzeugerbytes. Alte Snapshotformen bleiben nur als
explizit historische Daten erkennbar; sie sind kein normaler Writerweg.
