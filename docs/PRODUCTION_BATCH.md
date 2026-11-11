# Batchverarbeitung: lokale Produktion und autorisierte Einzelintegration

Vertrag vor konsumierendem Code, 10.11.2026. Maßgeblich:
[BA-A / #491](https://github.com/venomenon328/picross/issues/491#issuecomment-6779908657),
[Produktionsvertrag](PUZZLE_PRODUCTION.md),
[Authoring](ai-workflows/PUZZLE_AUTHORING.md),
[Hintergründe](PUZZLE_BACKGROUNDS.md) und
[Werkzeuganleitung](../tools/puzzle_production/README.md).
Dieser Vertrag schließt D01–D07 und BA-A-K01–K12. Tatsächlicher Liefer- und
Reviewstand bleibt im Produkt-PR. Die Abschnitte 1–7 beschreiben ausschließlich
BA-A; die eigenständige BA-B-Formfamilie steht anschließend. Echte Inhaltsproduktion
ist kein Bestandteil der Werkzeugentwicklung; ein Teilpaket schließt das Gesamtissue nicht.

## 1. Grenze und Aufruf

`python -m tools.puzzle_production.batch_cli validate|run|resume|status`
verarbeitet eine ausdrücklich gewählte, geordnete Jobliste seriell. `validate`
und `status` sind lesend. `run` benötigt einen neuen leeren Arbeitsroot;
`resume` den ausdrücklich benannten eigenen bisherigen Root. `--plan`,
`--source-root`, `--work-root`, `--repo-root` und optional `--history-root`
sind konkrete lokale Pfade. `status` braucht nur `--work-root` und prüft keinen
Fachnachweis neu; seine Anzeige ist ausdrücklich historisch/unverifiziert.

Die Python-API bietet dieselben Funktionen in `batch_runner`. Rootpfade sind
API-Argumente, keine frei ausführbaren Plandaten. Der Runner ruft ausschließlich
die folgende feste Fachpositivliste auf. Keine Shell-/Pluginengine, Modell-API,
Bildwahl, neue Freigabe, Gitmutation, Netzwerkoperation, gemeinsame Katalogmutation,
Finalisierung, Spielerexport, Registrierung, Adoption, Sync oder Retirement.
Paketbau ausschließlich `target=local`, `publish_to=None`.
Ein angegebener Historiencheckout wird nur vom vorhandenen Builder lesend genutzt.

## 2. Geschlossene äußere Formen

Jedes Objekt hat exakt die genannten Schlüssel. Optionale Inhalte werden als
ausdrückliches `null` gespeichert, nicht durch fehlende Schlüssel ersetzt.
JSON: UTF-8 ohne BOM, eindeutige Schlüssel, endliche Zahlen, höchstens Tiefe 32.
Ein Zahlenlexem umfasst höchstens 128 Zeichen; Bool ist keine Zahl.
Plan höchstens 2 MiB, Checkpoint/Report/Einzelledger höchstens 16 MiB.
Höchstens 32 Jobs, 32 Stufen je Job, insgesamt 256 Stufen und 4096 gebuchte Versuche.
Kennungen sind 1–64 ASCII-Zeichen `[a-z0-9][a-z0-9_-]*`; pz-ID und Produktionsrevision
folgen dem vorhandenen Authoringvertrag. Datei-SHA-256 bindet die gesamten
gespeicherten Bytes einschließlich eines vorhandenen End-LF.

| Objekt | Exakte Schlüssel |
| --- | --- |
| Plan | `format,batch_id,revision,previous_plan_sha256,source_commit,jobs` |
| Job | `job_id,puzzle_id,revision,background_revision,rulebook,decisions,stages` |
| Regelbindung | `version,document_revision,snapshot` |
| Entscheidungen | `motif,parameters,repair,background` |
| Stufe | `stage_id,kind,operation,inputs,parameters,limits,max_attempts,tool_binding` |
| Versuchsrahmen | `produce,revalidate` |
| Quellenref | `kind,file,sha256,bytes` mit `kind=source` |
| Ausgaberef | `kind,stage,slot,candidate_id` mit `kind=output` |

Planformat `picross-batch-plan-v1`; ganzzahlige Planrevision von 1 bis 1.000.000. Erste
Revision 1 hat `previous_plan_sha256=null`, danach exakt die SHA-256 der letzten
vollständigen Plandatei und Revision + 1. Bei `run` und jedem neuen Nachfolgeplan
muss `source_commit` dem tatsächlichen vollen Git-HEAD des ausdrücklich genannten
Werkzeugcheckouts entsprechen. Beim Resume desselben gespeicherten Plans darf
sein ursprünglicher Commit bestehen bleiben, sofern er im Checkout noch als
Commit bekannt ist. Die tatsächlich verwendeten Werkzeugbytes und Bindungen
werden auch dann frisch gegen den aktuellen Stand geprüft. Dirty-Dateien werden
dadurch nicht als Commitinhalt ausgegeben. Ein bloß anderer HEAD ist kein
Wiederverwendungsschlüssel; die lokale Gitprüfung liest nur die Herkunft.

Regelversion 0.6.0 oder ausdrücklich 0.7.0, ganzzahlige Dokumentrevision von 1 bis 1.000.000 und
`snapshot:SourceRef` müssen zum tatsächlich gelesenen vorhandenen Regeltext passen.
Entscheidungsfelder sind `SourceRef|null`. `motif` bindet den vorhandenen echten
`human_motif_approval`, `parameters` das Originalhandoff samt `approved_parameters`;
Originale, Evidenz und tatsächliche Motiv-/Parameterbindung werden fachlich geprüft.
`repair` bindet den vorhandenen vollständigen Reparaturplan innerhalb dieses
Auftrags, keinen erfundenen neuen menschlichen Freigabetyp. `background` bindet,
sofern angegeben, die vorhandene Erklärung des HP-W2-Requests. Der Request behält
seine eigene verbindliche Entscheidungsprüfung. Unbekannte Erklärungen sind keine
Zustimmung; der Runner erzeugt weder Eigentümer noch Text oder Zeit einer Freigabe.

Produzierende Rasterstufen brauchen Motiv-/Parameterentscheidung; `repair/search`
zusätzlich die konkrete Planbindung. Rein lesende Verifikation fordert keine neue
inhaltliche Freigabe. Null an einem erforderlichen Entscheid bedeutet
`waiting_human`. Ein unzutreffender deklarierter Beleg ist ein Fehler.

SourceRefs bezeichnen reguläre Dateien unter dem lesenden Quellenroot;
nichtnegative Bytezahl bis zur strengeren jeweiligen Fachgrenze, absolut höchstens
128 MiB. Pfade sind relative POSIX-Pfade ohne Traversal, Alias oder Links.
Bundleeingänge als SourceRef benennen den vorhandenen kanonischen Einstiegspfad:
Import/Reparatur `manifest.json`, Difficulty mit Kontext `catalog-context.json`,
historische Difficulty 0.3 ohne Kontext ausschließlich `report.json`, Hintergrund
`derivation.json`;
der Adapter gewinnt ausschließlich dessen fachlich geprüften Bundleordner.
OutputRefs erlauben ausschließlich frühere Stufen desselben Jobs und deren
feste Slots. `candidate_id=null`, außer für die ausdrücklich angegebene Variante.
Keine freien JSON-Pfade, Globs, Ausdrücke oder Vorwärts-/Querjobreferenzen.
Vollständig deklarierte fehlende oder geänderte Quellbytes scheitern vor Produktion.

## 3. Feste Operationen, Eingänge und Ergebnisse

Alle Ein- und Parameterfelder sind Pflichtfelder. Nur die in der letzten Spalte
genannten Eingänge dürfen ausdrücklich null sein; kein Parameterfeld ist nullable.
„Leer“ bedeutet exakt `{}`. Nicht genannte Felder sind unzulässig. Die
Einzelverträge bleiben Autorität für Wertebereiche, Profile, Zertifizierung und Phasen.

| Art / Operation | Exakte `inputs` | Exakte `parameters` | Als null zulässige Eingänge |
| --- | --- | --- | --- |
| `image_import / produce` | `image,design,approval` | `profile,candidates` | `approval` |
| `candidate_verify / verify` | `bundle` | `candidate` | keine |
| `logic_certify / solve` | `logic` | `profile,order` | keine |
| `repair / search` | `reference,plan,approval` | leer | `approval` |
| `repair / verify` | `reference,bundle` | leer | keine |
| `difficulty / analyze` | `design,matrix,logic,proof,baseline,r4_proof,r4_baseline` | `puzzle_id,runtime_revision,production_mode,method` | `baseline,r4_proof,r4_baseline` |
| `difficulty / import` | `candidate,bundle` | `method` | keine |
| `background / derive` | `request` | leer | `request` |
| `background / verify` | `request,bundle` | leer | `request` |
| `authoring_build / build` | `request` | leer | `request` |

Die Parameter haben folgende geschlossene Typen und Wertebereiche:

| Parameter | Typ und zulässiger Wert |
| --- | --- |
| `profile` | Zeichenkette `full-line-mono`, `full-line-color`, `paired-lines-mono` oder `paired-lines-color`; passend zur tatsächlichen Logik |
| `candidates` | Liste mit 1–8 unterschiedlichen Variantenkennungen; jede Zeichenkette entspricht `[a-z][a-z0-9_-]{0,31}` |
| `candidate` | Genau eine Variantenkennung derselben Form |
| `order` | Zeichenkette `rows-first`, `columns-first` oder `reverse`; Paarprofile ausschließlich `rows-first` |
| `puzzle_id` | Vorhandene pz-ID als Zeichenkette, identisch zur Jobbindung |
| `runtime_revision` | Ganzzahl von 1 bis 1.000.000 |
| `production_mode` | Zeichenkette `mono` oder `color` |
| `method` | Ausdrückliche Methodenkennung nach dem Analyse-/Importvertrag unten |

Ein fehlender vollständiger Builderrequest wartet als `waiting_input`; er wird
nicht automatisch erzeugt. Ein fehlender Hintergrundrequest wartet als
`waiting_human`. Fehlende fachlich notwendige Belege erhalten keine Zertifizierung.
Import-/Reparaturapproval entspricht der Motiventscheidung; Reparaturplan entspricht
`decisions.repair`. Ein später gelieferter Request kommt mit einem ausdrücklich
fortgeschriebenen Plan, ohne vorherige Arbeit oder verbrauchte Budgets zu löschen.

Die ausgewählte Jobidentität bleibt an die tatsächlichen Quellen gebunden:

| Quelle / Operation | Geprüfte Identitätsbindung |
| --- | --- |
| Erforderliches Parameterhandoff | `handoff.puzzle_id == job.puzzle_id` vor Reservierung und Fachaufruf |
| `difficulty / analyze` | `parameters.puzzle_id == job.puzzle_id` bereits bei der Planprüfung |
| Hintergrundrequest | Sein bytegebundenes Manifest hat `puzzle_id == job.puzzle_id` und `revision == job.background_revision`. |
| Lokaler Builderrequest | `handoff.puzzle_id == job.puzzle_id` und `handoff.revision == job.revision` vor Reservierung und Fachaufruf |

Die vorhandenen Fachprüfer prüfen zusätzlich die tatsächlichen Freigaben,
Parameter, Quellen und Phasen; die Identitätsbindung ersetzt diese Prüfungen nicht.

| Operation | Tatsächlicher Weg und Slots |
| --- | --- |
| Import / Kandidatenprüfung | `images.import_image` / `images.inspect_candidate`; `bundle` und je gewählter Variante `design,matrix,logic,proof`, bei bestehendem Paarprofil auch `baseline,assessment`. Proofslots nur wenn wirklich vorhanden. |
| Solve | vorhandener Solver und unabhängiger `verifier.verify`/Produktionsprüfer; `logic,proof` und tatsächlich vorhandene `baseline,assessment`. Keine Profil-/R4-Eskalation. |
| Reparatur | `repair.search` und frisches `inspect_repair`; `repair_bundle`. Qualifiziertes Final: `logic,proof,baseline,assessment` aus den vorhandenen `final-*`-Originalen sowie fest geprüfte `design,matrix`-Projektionen. Kein Finalslot bei Nichtfund/Abbruch. |
| Difficulty | `catalog_analysis.candidate`→`analyze_single` einschließlich seiner frischen `catalog_rating.import_bundle`-Prüfung; Import prüft vollständige vorhandene Bundles. `candidate,analysis_bundle,checked_difficulty`, soweit tatsächlich geliefert. |
| Hintergrund | ausschließlich `background_assets.derive/verify`; `background_finding` und nur bei Illustration `background_png`. None erzeugt kein Platzhalterbild. |
| Builder | unveränderter vollständiger Builderrequest v1/v2; `package,handoff,record` und `sheet_update` als unveränderte `sheet`-Projektion aus dem Producerergebnis. Vollständige ZIP-/Phasenprüfung bleibt. |

Variantenplätze sind intern `slot:candidate_id`; der Plan verwendet die getrennten
Ausgabereffelder. Matrix stammt aus dem geprüften Kandidatenobjekt, nicht aus einer
behaupteten ursprünglichen matrix.json. Zulässige Materialisierungen und
Sheetprojektion sind gesonderte deterministische Runnerdateien mit Originalbindung.
Alle versiegelten Originale bleiben unverändert.

Neue Difficultyanalyse (`difficulty / analyze`) bindet ausdrücklich die aktive Methode aus
`content/difficulty-method.json`, derzeit `picross-difficulty-0.4`, einschließlich
Freeze `5508f0742aa858a6adc31aa621433e68298b915fb0fd6b8d9e74e576ba87caaf`.
Kein unbemerkter API-Default 0.3. Produktionsmodus, eigene Definition/Logik/Matrix
und nötige getrennte R4-Belege werden geprüft. `proof/baseline` binden die
Originallogik; `r4_proof/r4_baseline` sind explizite, unabhängige passende Belege
der normalisierten Runtimekandidatenlogik. Keine Proofumschreibung oder versteckte
Solversuche. Fehlende notwendige Belege bleiben ein konkreter offener Rest. Rating ist keine menschliche Endabnahme.

Bei `difficulty / import` ist `parameters.method` ausdrücklich entweder
`picross-difficulty-0.3` oder `picross-difficulty-0.4` und muss zur Methode des
frisch über den vorhandenen nativen Reader geprüften vollständigen Bundles passen.
Gültige historische 0.3-Ergebnisse bleiben in ihrer ursprünglichen Form lesbar:
mit `catalog-context.json` als `picross-checked-difficulty-v2`, ohne Kontext über
den festen `report.json`-Einstieg als `picross-checked-difficulty-v1`.
Der kontextlose v1-Befund erhält keinen erfundenen `production_mode`.
0.4 verwendet weiterhin seinen vollständigen Kontext und den nativen
`picross-checked-difficulty-v3`-Befund. Import und Wiederprüfung bewahren diese
Formen und ihre tatsächliche Methode; sie schreiben weder Originale um noch
führen sie eine neue Analyse aus. Historische Lesbarkeit erlaubt keinen
0.3-Fallback für neue Analyse.

Adapterresultat exakt `status,domain,certified,exit_code,slots,details`.
`domain` erhält den tatsächlichen fachlichen Status, `certified` ist bool|null,
`exit_code` der tatsächliche entsprechende Fachausgang.
`details` exakt `reason,candidates,method,state,usage`; Textwerte string|null,
`candidates` eine Liste exakter `candidate_id,status,certified`-Objekte.
`usage` exakt `lines,pair_work,pair_records,steps,candidates,rule_work,waves`,
jeweils nichtnegative Ganzzahl oder null für nicht gemessene/berichtete Werte.
Keine beliebigen API-Objekte oder Erfolgsflags als Vertrauenskontext speichern.

Der interne Dateislot ist exakt `kind,path,sha256,bytes`, der Verzeichnisslot
`kind,path,files` mit exakten Inventareinträgen `file,sha256,bytes`.
Der Runner normalisiert absolute Pfade zu bytegebundenen Artefaktrefs:
Datei `kind,root,file,sha256,bytes`, Verzeichnis `kind,root,file,files`;
`root` ist ausschließlich `source` oder `work`. Nur für einen Verzeichnisroot
darf `file` leer sein. Inventare sind sortiert, vollständig, ohne Link-/Casealiase.
Pro ausgewähltem Inventar höchstens 2048 Dateien / 512 MiB nach dem bestehenden
Authoringrahmen; strengere Einzel-Fachgrenzen gelten weiter. Insbesondere behält
RP-5 seine 256-MiB-Grenze; gültige 128-Kandidaten-Bundles werden nicht auf
256 Dateien verkleinert.

## 4. Werkzeugbindung, Budgets und gezielte Invalidierung

`tool_binding` exakt `format,python,modules,versions,norms`, Format
`picross-batch-tool-v1`. `python` ist die tatsächliche Zeichenkette aus
`platform.python_version()`, nicht leer, ohne NUL und höchstens 128 Zeichen lang.
`versions` hat je Art exakt die folgende Form; Werte sind tatsächliche
Versionszeichenketten ohne NUL mit 1–128 Zeichen oder null, falls der vorhandene
Versionsprüfer keinen Wert liefert:

| Art | Exakte Schlüssel in `versions` |
| --- | --- |
| `logic_certify` | keine, exakt `{}` |
| `background` | `python,pillow,littlecms,zlib` |
| `image_import,candidate_verify,repair,difficulty,authoring_build` | `tool,pillow,jpeg,jpeg_turbo,littlecms,zlib` |

Der Adapter bestimmt die vollständige feste relevante Modul-/Normmenge und
tatsächliche Laufzeit-/Codecwerte; Nutzer können keine Pflichtdatei weglassen.
`modules` und `norms` sind jeweils Listen mit 1–256 exakten
`file,sha256,bytes`-Dateirefs, nach Pfad sortiert, eindeutig und ohne Casefoldaliase.
Pfad und SHA-256 folgen der bestehenden Dateiform; die Bytezahl ist positiv und
höchstens 128 MiB. Die erwartete Menge ist je Operation im Adapter festgelegt
und wird vor Ausführung frisch gegen die wirklichen Dateien geprüft. Bereits
geladener Code muss denselben gebundenen Modulbytes entsprechen; eine relevante
Dateiänderung im laufenden Prozess erfordert einen frischen Prozess. Keine
pauschale Bindung an den Gesamt-Git-HEAD. HP-W2 behält zusätzlich seine vollständige eigene
derive-Bindung; verify erlaubt ausschließlich seine bestehende enge
Commit-/Dirty-Abweichung bei unveränderten Modul-/Codec-/Profilbytes und frischem
vollständigem Replay. Kein Umschreiben alter Werkzeughashes.

`limits` exakt `produce,revalidate`: pro Operation die tatsächlich verwendete
geschlossene Budgetform; `produce=null` bei rein lesender Operation.
Logikbudget: `seconds,max_lines,max_pair_work,max_pair_records`.
Analysebudget: `seconds,max_lines,max_rule_work,max_waves,max_pair_work,max_pair_records`.
Reparatursuche: `search_seconds,final_seconds,search_lines,final_lines,max_steps,max_candidates,max_changes`,
exakt passend zum vorhandenen Reparaturplan; Wiederprüfung hat Logikbudget.
HP-W2 und Builder: exakt `seconds:300`, vorhandene feste Schutzrahmen.
Strengere bestehende Datei-/Pixel-/Prooflimits bleiben unberührt.
Zeitwerte sind endliche nichtnegative Zahlen; `search_seconds` höchstens 600,
`final_seconds` höchstens 120. Arbeitszähler sind nichtnegative Ganzzahlen:
`max_lines`, `search_lines` und `final_lines` höchstens 1.000.000,
`max_pair_work` und `max_rule_work` höchstens 100.000.000,
`max_pair_records` höchstens 1.000.000, `max_waves` höchstens 80.000,
`max_steps` höchstens 1024 und `max_changes` höchstens 10.000.
`max_candidates` ist eine Ganzzahl von 1 bis 128. Bool ist auch hier kein
Zahlenwert; ein fachlich zu kleiner erlaubter Rahmen bleibt ein echter Abbruch.

`max_attempts` exakt `produce,revalidate`, jeweils ganzzahlige Werte von 0 bis 100;
der angeforderte Typ braucht eine positive Erlaubnis. Erzeugung samt verpflichtender interner Prüfung
verbraucht einen produce-Versuch; erste lesende Operation und jede spätere
Wiederaufnahmeprüfung einen revalidate-Versuch. Vor Start werden Budgets dauerhaft
reserviert. Keine automatische Wiederholung, Aufweitung oder Erhöhung.
Der Runner begrenzt zusätzlich die tatsächliche Prozessdauer auf den reservierten
Rahmen; ein unbekannter Zähler nach hartem Abbruch bleibt null und die Reservierung
wird konservativ vollständig angerechnet.

Der äußere Prozessrahmen `reserved_limits.seconds` folgt exakt
`batch_operations.reservation_limits`. In der Tabelle bezeichnet `P` den Wert
`limits.produce.seconds`, `R` den Wert `limits.revalidate.seconds` und `N` die
Anzahl der ausdrücklich ausgewählten Importkandidaten. Jeder Rahmen enthält
zusätzlich genau 30 Sekunden für Prozessstart und I/O; diese feste Zugabe
erhöht keine fachliche Such-, Änderungs- oder Versuchsgrenze. Auch das berechnete
Gesamtergebnis muss endlich bleiben.

| Versuch / Operation | Reservierte Prozessdauer in Sekunden |
| --- | --- |
| produce: `image_import / produce` | `N * (3 * P + R) + 30` |
| produce: `logic_certify / solve` | `P + R + 30` |
| produce: `repair / search` | `limits.produce.search_seconds + limits.produce.final_seconds + R + 30` |
| produce: `difficulty / analyze` | `P + 3 * R + 30` |
| produce: `background / derive`, `authoring_build / build` | `P + 30`, also 330 |
| revalidate: `image_import / produce` | `N * R + 30` |
| revalidate: `difficulty / analyze` | `2 * R + 30` |
| revalidate: alle übrigen Operationen | `R + 30` |

Eine produce-Reservierung speichert die beiden unveränderten Fachrahmen
`produce` und `revalidate`; bei einer revalidate-Reservierung ist `produce=null`.
Die Multiplikatoren berücksichtigen die tatsächlich getrennten Fachaufrufe
einschließlich ihrer verpflichtenden Prüfung, ohne weitere Versuche zu erlauben.

Zähler-/Budgetlinie ist `(puzzle_id,kind,operation)`, nicht Job-/Stufenname oder
Revisionsnummer. Alte Linien bleiben über alle gespeicherten Pläne erhalten;
Umbenennen, Entfernen/Wiedereinfügen, anderer Fingerprint oder neues rXX füllt
keinen Zähler auf. Innerhalb derselben Batchlinie lassen sich Budgets/Versuchslimits
nicht erhöhen. Eine tatsächlich neu autorisierte erweiterte Produktion benötigt
eine neue ausdrücklich vorbereitete Auftragslinie; Resume erteilt sie nicht.

Fingerprint bindet die tatsächlichen erforderlichen Eingänge/Entscheidungen,
Parameter, relevanten Werkzeuge/Normen und Regelbindung der konkreten Stufe.
Nur wirklich abhängige Zweige werden stale. Reine Hintergrundbytes/-auswahl
invalidieren Bild-/Paketstufen, nicht unveränderte Logik-/Proof-/Difficultyartefakte
oder andere Jobs. Titel-/Kategorie-/Revealänderungen lösen keine neue Logiksuche
aus, soweit deren tatsächliche Logikeingänge unverändert bleiben. Abhängige Stufen
erhalten nur vorhandene, frisch geprüfte Slots, keine erfundene Zertifizierung.

## 5. Eigener Root, unveränderliche Buchführung und Checkpoint

Ein Root enthält eigene `owner.json`, `plans/`, `attempts/`, `checkpoint.json`,
`report.json` sowie die stabilen `.batch-writer.lock` und `.batch-worker.lock`.
Hinzu kommen ausschließlich die unten beschriebenen inerten temporären Einträge.
`owner.json` ist exakt `format,batch_id,work_identity,source_root,source_identity,repo_root,history_root`,
Format `picross-batch-owner-v1`; Identität je exakt `device,inode`.
Quellen-/Arbeitsroots dürfen sich nicht überlappen, auch nicht per Casefoldalias.
Ausgabe darf weder Quellen noch aktive Spiel-/Katalogbäume überdecken.
Vorhandene unzugeordnete Ziele, Dateikollisionen, Link-/Reparse-/Hardlinkpfade
und fremde Bytes sind Fehler. Vorhandene sichere I/O-Prüfer werden wiederverwendet.

`.batch-writer.lock` erlaubt genau einen kooperativen Runner je Root.
Der Fachworker hält während seiner Operation zusätzlich `.batch-worker.lock`;
Resume prüft diesen Lock vor neuer Planung. Ein noch laufender Worker verhindert
damit den nächsten Lauf. Sein eigener Watchdog beendet ihn bei Verlust des
Elternprozesses oder Ablauf seines reservierten Prozessrahmens. Der Runner
begrenzt die Workerprozessdauer zusätzlich von außen. Fremde
HP-W2-/Builder-/RI-Locks werden weder geändert noch entfernt. Beide eigenen
Lockdateien bleiben als stabile Inodes liegen.
Quellen und verbrauchte Originale werden vor/nach Fachverbrauch frisch gelesen.

Temporäre Metadateneinträge heißen exakt `.batch-pending-<32 kleine Hexzeichen>.json`.
Sie dürfen im Arbeitsroot, unter `plans/` sowie innerhalb eines veröffentlichten
oder gestagten Versuchsordners zurückbleiben. Ein noch nicht veröffentlichter
Versuchsordner heißt `attempts/.batch-attempt-<32 kleine Hexzeichen>` und darf
nur reguläre `reservation.json` oder solche Pendingdateien enthalten. Diese
Einträge werden auf sichere Pfade einschließlich Link-/Reparse-/Hardlink- und
Aliasverbote geprüft. Sie bleiben inert, erteilen keine Versuchserlaubnis und
werden nicht als Plan, Ergebnis oder gebuchte Reservation übernommen. Unbekannte
Namen oder Staginginhalte sind Fehler; fremde Reste werden nicht gelöscht.

Planrefs exakt `revision,file,sha256,bytes`, auf unverändert gespeicherte
Originalplandateien unter `plans/`. Eigene Versuchspfade
`attempts/<sechsstellige Nummer>/` enthalten unveränderliche `reservation.json`,
gegebenenfalls `result.json` und den eigenen `output/`-Ordner.
Reservierungsdatei exakt `format,number,plan_sha256,job_id,stage_id,puzzle_id,kind,operation,attempt_type,fingerprint,input_bindings,tool_binding,reserved_limits,output_dir`;
Format `picross-batch-reservation-v1`.
`input_bindings` exakt `inputs,decisions,rulebook`; Inputs/Entscheidungen haben nur
ihre bereits geschlossenen Namen und aufgelösten Artefaktrefs beziehungsweise null.

Ein gespeicherter Versuch enthält exakt die Reservierungsfelder ohne `format`
sowie `status,result,inventory,seconds,error`. Status `running,completed,failed,aborted,interrupted`.
`result` ist das normalisierte Adapterresultat oder null, `inventory` die vollständige
Ausgabeinventarliste `file,sha256,bytes`, `seconds` endliche nichtnegative Zahl|null,
`error` string|null. `reserved_limits` ist exakt `produce,revalidate,seconds`;
die ersten zwei Felder enthalten die tatsächlichen Fachrahmen, seconds den
endlichen Prozessrahmen einschließlich verpflichtender zusätzlicher Prüfaufrufe
und der dokumentierten festen Start-/I/O-Zugabe. `result.json` speichert exakt
diesen vollständigen Versuch.

Unveränderliche Metadatendateien werden zunächst vollständig in eine eigene
Pendingdatei geschrieben und synchronisiert, dann atomar ohne Ersetzen eines
vorhandenen Ziels veröffentlicht. Für eine neue Reservation geschieht dies im
eigenen gestagten Versuchsordner; erst dessen atomare Veröffentlichung als
`attempts/<Nummer>/` bucht den Versuch. Elternverzeichnisse werden ebenfalls
synchronisiert. Danach wird der Checkpoint atomar aktualisiert; erst hinter
beiden Veröffentlichungen darf der Fachprozess starten. Ein Ergebnis wird erst
nach frischer Fach-/Byteprüfung als vollständiges dauerhaftes `result.json`
veröffentlicht und im Checkpoint gebucht. Ein Abbruch während des Schreibens
hinterlässt damit eine inerte Pendingdatei statt einer partiellen endgültigen
Ergebnisdatei. Alle fremden Änderungen vor Replace erkennen.

Checkpoint exakt `format,batch_id,plan,plans,attempts,stages,status`, Format
`picross-batch-checkpoint-v1`. Stufenzustand exakt
`job_id,stage_id,status,fingerprint,attempt,reused,reason,next_step`;
`attempt` Nummer|null, `reused` bool, übrige optionale Aussagen string|null.
Checkpoint und unveränderliche Ledger werden gegeneinander geprüft. Unbekannte
Form, gekürzte/ersetzte Historie, widersprüchlicher Erfolgsstand oder fremde
Dateien stoppen den gesamten Runner. Ein nach hartem Abbruch zusätzlich vollständig
gebuchter Reservierungspräfix wird konservativ als verbraucht rekonstruiert;
fehlende Abschlussbuchung ist kein Erfolg. Gespeicherte Erfolge benötigen vor
Wiederverwendung stets neue fachliche Prüfung mit eigener Reservierung.

Atomare Checkpointveröffentlichung erhält den vorherigen vollständigen Stand
bei Fehler. Die Inventarprüfung erkennt fehlende, geänderte und zusätzliche
Ausgaben. Bei Wiederverwendung werden sowohl der letzte Prüfversuch als auch
die ursprünglichen ausgabebesitzenden Versuche der erhaltenen Slots inventarisiert.
Historische Pläne/Versuche bleiben erhalten, auch wenn ihre Stufe im
aktuellen Plan nicht mehr ausgewählt ist. Kein dauerhafter serialisierter RI-Prüfkontext.

## 6. Zustände und Bericht

Stufenstatus: `pending,running,completed,waiting_input,waiting_human,blocked,failed,aborted,interrupted,stale`.
`completed` besagt nur, dass der angeforderte technische Schritt sein definiertes
Ergebnis geliefert hat. `produced/0`, `stalled/0`, Widerspruch, gültige unrated-Analyse
und korrekt geprüfter Nichtfund werden nicht in Inhaltseignung umgedeutet.
Fachstatus, Zertifizierung, Rating und tatsächliche menschliche Erklärung bleiben
getrennt. Ein fehlender notwendiger Slot blockiert nur seine abhängigen Stufen.
Unabhängige Zweige und Jobs laufen weiter; Abbruchsignal stoppt weitere Planung.

Gesamtstatus und CLI-Exit: `completed/0`, `invalid_input/2`, `incomplete/3`,
`aborted/4`, `technical_error/5`. Technisch vollständige Auswahl kann weiterhin
fachlich ungeeignete Ergebnisse enthalten; kein Exit vergibt Inhaltsfreigabe.
Unsicherer gemeinsamer Root, widersprüchliche Historie oder fehlgeschlagener
Checkpoint stoppt insgesamt. `budget_exhausted` nennt den konkreten verbrauchten
Versuchstyp; kein versteckter zweiter Versuch.

Report exakt `format,batch_id,plan,source_commit,status,jobs,attempts,elapsed_seconds,execution_seconds,verification_seconds,human_seconds,next_step`;
Format `picross-batch-report-v1`. Job exakt `job_id,status,stages`, Stufen wie im
Checkpoint. Versuche enthalten die vollständigen gebundenen Originale und alle
Fehlversuche. Die Zeitfelder haben getrennte Bezugsgrößen:

| Feld | Tatsächlich gemessener Umfang |
| --- | --- |
| `elapsed_seconds` | Übergreifende gemessene Dauer der Runner-Ausführungsschleifen aus `run` und den anschließenden Resumeaufrufen, sofern die ganze Folge belegt ist; sonst null |
| `execution_seconds` | Summe der gemessenen Sekunden aller produce-Versuche der vollständigen Historie, einschließlich ihrer verpflichtenden internen Prüfungen |
| `verification_seconds` | Summe der gemessenen Sekunden aller revalidate-Versuche der vollständigen Historie |
| `human_seconds` | Ohne Messung immer null |

Nur der ausdrücklich neue `run` beginnt mit bekannter Vorgängerdauer 0.
Bei Resume wird eine bisherige `elapsed_seconds` ausschließlich aus einem
vollständigen gespeicherten Report übernommen, dessen Batch-/Planbindung,
Stufen, Status und gesamte Versuchshistorie zum vorherigen gespeicherten
Checkpoint beziehungsweise seiner rekonstruierten Historie passen. Auf eine
bekannte Vorgängerdauer wird die aktuelle gemessene Ausführungsschleife addiert.
Fehlt dieser passende Report, bleibt eine durch Abbruch oder unberichteten Lauf
nicht belegte Dauer unbekannt; das gilt auch bei bislang leerer Versuchshistorie.
Ein bereits unbekannter Vorgängerwert bleibt null.

Enthält die Erzeugungs- oder Prüfzeitsumme eine unbekannte Versuchszeit, bleibt
auch diese jeweilige Summe null. Diese beiden Teilsummen werden nicht zusätzlich
zur bereits umfassenden `elapsed_seconds` addiert. Zeit zwischen Aufrufen,
ImageGen- und Entscheidungswartezeit ist keine gemessene Runnerzeit. `status`
zeigt ohne neue Messung `elapsed_seconds=null` sowie im CLI-Umschlag ausdrücklich
`fresh=false`; es schreibt keine neue Prüfbescheinigung.

## 7. Prüfung und Lebenszyklus

Pflichtkern einschließlich regulärem Windowsbau sowie genau `tools` und
`production.adapter` vollständig. Kleine synthetische Regressionen sichern
geschlossene Formen, echte Dispatch-/Fachresultate, sichere Roots/Lock,
menschliche Gates, Crashgrenzen, erhaltene Budgets, manipulierte Originale,
gezielte Invalidierung und lokalen Builder-No-op/Konflikt. Keine echten Rätsel,
Bestandsfixtures, neuen Algorithmen, Freezes, Writer oder Runtimeänderungen.

BA-A-T01 bleibt ein einmaliger echter CLI-Durchstich, kein neuer CI-Job:
mindestens 3 synthetische Jobs, Raster/0.4, selected/none, offenes Menschengate,
harter Abbruch nach Buchung, Resume, Artefaktmanipulation, reine Bildänderung bei
erhaltener Logik und explizit später gelieferter lokaler Bauauftrag.
Genau 6 Originale: `plan-initial.json`, `plan-resume.json`, `checkpoint.json`,
`report.json`, `cli.log`, `manifest.json`. Fixturequellen liegen im Produktdiff;
Originale am Produkt-Head separat für BA-A-A01, spätestens 17.11.2026 bzw. bei
späterem Beginn vorher neu konkret datiert. Normale CI `evidence.mode=none`.
Unabhängiges BA-A-A01 vor Merge bleibt ein eigenes Gate; Selbstreview ersetzt es
nicht. Nachweise, tatsächliche CI, Head und Rückbau stehen im Draft-PR.

## 8. BA-B: autorisierte serielle Einzelintegration

Vertrag vor konsumierendem Code, 11.11.2026. Maßgeblich ist die
[BA-B-Paketentscheidung D01–D06/K01–K12](https://github.com/venomenon328/picross/issues/491#issuecomment-6782256272).
BA-A und seine geschlossenen v1-Formen bleiben unverändert. BA-B bietet genau
`register` und `background_adopt`, keinen zusätzlichen Fachwriter, keine
Gesamttransaktion und keine kreative Arbeit. Bestehende Export-, Proof-,
Endfreigabe-, Difficulty-, Quellen-, Transaktions- und Recoveryverträge bleiben
zuständig. Der Runner erzeugt weder Entscheidungen noch Requests oder Ratings.
Er führt keine Gitmutation, Netzbeschaffung, Retirement oder echte Inhaltsproduktion
als Werkzeugtest aus. Ein Abschluss bezeichnet ausschließlich den Zielcheckout.

### 8.1 Einstieg, Roots und vorgezogene Prüfung

`python -m tools.puzzle_production.integration_batch_cli validate|run|resume|status`
und die gleichnamigen Funktionen in `integration_batch_runner` verwenden
`plan_path,source_root,repo_root,target_root,work_root,history_root` als API-Argumente.
CLI: `--plan`, `--source-root`, `--repo-root` (ausführender Werkzeugcheckout),
`--target-root` (genau ein Zielcheckout), `--work-root`, optional `--history-root`.
Bei `validate` ist der Arbeitsroot optional; `status` benötigt nur `--work-root`.
`validate` und `status` schreiben nichts. Status ist historisch, `fresh=false`.
Run benötigt einen noch nicht vorhandenen eigenen Root, Resume dessen ausdrücklich
benannten vorhandenen Stand. Kein impliziter Quellen-/Historywechsel.

Alle Pfade sind lokale reguläre Dateien/Verzeichnisse; UTF-8, eindeutige JSON-Schlüssel,
höchstens Tiefe 32, Zahlenlexeme höchstens 128 Zeichen, keine NaN/Infinity oder
Bool-Zahlen. Unbekannte Felder, Traversal, Links, Hardlinks, Reparsepunkte und
abweichende Groß-/Kleinschreibung werden verworfen. Pfade in Refs sind relative
POSIX-Pfade. Eigene Arbeits-/Ausgaberoots dürfen weder Eingänge noch Ziel-/History-
oder Werkzeugroots überdecken. Werkzeug- und Zielcheckout dürfen identisch sein;
native Authoringquellen dürfen ausdrücklich innerhalb des Zielcheckouts liegen.
Ausgaben entstehen ausschließlich unter dem eigenen Versuchspfad. Die Fachwege
dürfen ihre eigenen sicheren temporären Bereiche wie bisher verwenden.

Vor dem ersten Fachschreiber prüft BA-B den gesamten ausgewählten Plan: Form,
Identitäten, Pfade, alle deklarierten Bytes und vollständigen Inventare, Zuordnung
der Aufträge und Budgets. Fehlende optionale Erklärung bleibt `waiting_human`,
fehlender noch nicht deklarierter Eingang `waiting_input`; deklarierte fehlende,
veränderte oder widersprüchliche Bytes sind ungültige Eingaben. Teure Proof-/Export-
und Katalogprüfungen gehören weiterhin zum nativen zuständigen Einzelaufruf.

### 8.2 Exakte neue Planformen

Jedes Objekt hat exakt die genannten Schlüssel. Nullable Felder sind vorhanden
und ausdrücklich `null`. Namen entsprechen `[a-z0-9][a-z0-9_-]{0,63}`;
`puzzle_id` und Produktions-/Bildrevision folgen dem Authoringvertrag. SHA-256
hat 64 kleine Hexzeichen, Commit-SHA 40. Plan maximal 2 MiB, Checkpoint/Report/
einzelner Ledger maximal 16 MiB. Native strengere Grenzen gelten zusätzlich.
Dateirefs maximal 128 MiB, vollständige Inventare höchstens 512 Dateien und
512 MiB. Das native Einzeldateilimit von 64 MiB bleibt erhalten; allein das
deklarierte Original-ZIP im v6-Transport darf nach seiner bestehenden eng
geprüften Ausnahme bis 128 MiB groß sein. Inventare sind nach `file` sortiert,
case-eindeutig und vollständig.

| Objekt | Exakte Schlüssel und Typen |
| --- | --- |
| Plan | `format` = `picross-integration-batch-plan-v1`; `batch_id`: Name; `revision`: Integer 1..1000000; `previous_plan_sha256`: Hash/null; `source_commit`: Commit; `jobs`: geordnete Liste 1..32 Jobs |
| Job | `job_id`: Name; `puzzle_id`: pz-ID; `revision`: Produktions-/Bildrevision; `operation`: `register`/`background_adopt`; `rulebook`: Regelbindung; `authorization`: FileRef/null; `inputs`: artspezifisch; `parameters`: artspezifisch; `budgets`: artspezifisch; `max_attempts`: artspezifisch |
| Regelbindung | `version`: `0.6.0`/`0.7.0`; `document_revision`: Integer 1..1000000; `snapshot`: FileRef |
| FileRef | `file`: relativer Pfad; `sha256`: Hash; `bytes`: Integer 0..134217728 |
| DirectoryRef | `directory`: relativer Pfad oder `.`; `files`: vollständige Liste FileRef relativ zu diesem Verzeichnis |

Eine pz-ID kommt genau einmal in der gesamten Auswahl vor, auch über beide
Jobarten. `job_id` ist ebenfalls eindeutig. Revision 1 hat keinen Vorgänger;
ein Nachfolgeplan hat genau Revision +1 und die SHA-256 der vorherigen vollständigen
Datei einschließlich End-LF. Initialer Plan und neue Planrevision nennen den
tatsächlichen Werkzeug-HEAD. Beim unveränderten Resume bleibt dessen bekannte
ursprüngliche Commitprovenienz erhalten. Ein Commit ist weder Katalogsnapshot
noch Wiederverwendungsbeweis. Der Regeltext muss seine deklarierte Version/
Dokumentrevision tatsächlich tragen; native zulässige historische Regeln werden
nicht durch einen aktuellen Text ersetzt. Der Runner verändert keine Originale.

| Art | Exakte `inputs` | Exakte `parameters` |
| --- | --- | --- |
| `register` | `package`: FileRef/DirectoryRef/null; `handoff,record,approval,manual_authorization,palette_exception,difficulty`: FileRef/null; `external`: DirectoryRef/null | `name`: nichtleerer Text bis 256 Zeichen; `runtime_revision`: Integer 1..1000000; `stem,save_slot`: native Stem-Kennung; `category_id`: nichtleerer Text bis 128 Zeichen; `allow_background,rebind_difficulty`: echte Bool |
| `background_adopt` | `request`: FileRef/null; `work`: DirectoryRef/null | exakt `{}` |

Ein Paketverzeichnis bindet alle Originale durch sein Inventar, eine Paketdatei
das unveränderte ZIP. `handoff`/`record` sind nur für tatsächlich separat vorhandene
Originale gesetzt; der Runner fordert keinen künstlichen Authoring-Store.
Interne Handoffs/Endabnahmen behalten ihre native Bedeutung. `external` bindet
genau die explizite äußere Wurzel samt vollständigem Inventar. Keine Ausgabe-Refs,
Globs oder noch unbekannten Ergebnisse anderer Jobs. Difficulty bleibt die echte
geprüfte Eingangsdatei; null ist ausschließlich für einen fachlich bestätigten
historischen identischen No-op zulässig, nicht für ein neues Rating.

Für `register` bezeichnet `authorization` einen unveränderten ausdrücklich
vorbereiteten Integrationsauftrag mit Format `picross-integration-order-v1` und
exakt `format,operation,puzzle_id,revision,actor,timestamp_utc,statement,evidence,test_only`.
`operation` ist `register`, ID/Revision sind gleich dem Job; `actor,statement`
sind nichtleere Texte bis 4096 Zeichen, `timestamp_utc` ein nativer UTC-Zeitstempel,
`evidence` ein FileRef unter dem Quellenroot auf die tatsächliche ursprüngliche
Auftragserklärung; `test_only` ist Bool und muss zur Produktion passen.
Die Dateiform transportiert eine bereits erklärte Befugnis; sie erteilt sich
nicht selbst eine, und wird vom Runner niemals erstellt/ergänzt. Sie ersetzt
auch keine native Endabnahme. Synthetische Fixtures markieren alle Erklärungen
ausdrücklich `test_only` und behaupten keine reale Eigentümerfreigabe.

Bei `background_adopt` ist `authorization` exakt derselbe FileRef wie `request`:
der unveränderte native `picross-background-adoption-request-v1` enthält seinen
eigenen passenden Bildänderungsauftrag, Zielsource und Revision; seine
Hintergrundrefs binden Auswahl/none, Herkunft und Q-HG der tatsächlichen
Arbeitsdateien. BA-B dupliziert diese Angaben nicht in einem editierbaren
zweiten Objekt. `work` bindet das vollständige zu speichernde Arbeitsverzeichnis
einschließlich Originalrecord; Root-/Recordbedeutungen prüft der native Reader.

### 8.3 Budgets und feste Einzelaufrufe

| Art | Exakte `budgets` | Exakte `max_attempts` |
| --- | --- | --- |
| `register` | `export_seconds,plan_seconds,reconcile_seconds` jeweils 300; `publication_seconds,recovery_seconds` getrennte endliche positive Zahlen bis 86400, regulär jeweils 1800 | `export,plan,apply,reconcile`: je Integer 1..100 |
| `background_adopt` | `store_seconds,plan_seconds,adopt_seconds,recovery_seconds,reconcile_seconds` jeweils 300 | `store,plan,adopt,reconcile`: je Integer 1..100 |

Die unveränderte Warnschwelle der Registrierung ist 300 s. Die beiden expliziten
Registrierungswerte werden nur beim mutierenden Einzelaufruf als die vorhandenen
Overrides übergeben. Kein äußerer Gesamtdeadline über diesen Aufruf kürzt dessen
separaten Recoveryrahmen. Bildplan/-adoption/-recovery bleiben je 300 s; keine
Registrierungsdefaults für Bildoperationen. BA-B startet keinen Workerprozess:
der OS-Lock und alle synchronen Fachaufrufe gehören demselben CLI-Prozess. Harte
Beendigung hinterlässt dadurch keinen unabhängig weiterlaufenden Batchworker.
Native kooperative Abbruch-/Budget- und automatische Rollbackpfade bleiben erhalten.

`register`: `target_adapter.export` prüft seine Ein-/Ausgaben vollständig, danach
unmittelbar `content_registry.registration(apply=False)`, danach genau ein
`registration(apply=True)` mit denselben gebundenen Eingängen. Kein routinemäßiges
zusätzliches inspect/verify-export. Zweiter Job plant nach dem ersten Erfolg.
Der Apply-Aufruf plant intern selbst erneut; BA-B behauptet keine zusätzliche
atomare Snapshotbindung zwischen diesen getrennten nativen Aufrufen. Ein nativer
Konflikt stoppt ohne automatische Neuplanung/Mutation. Ein vollständig frischer
Plan-No-op kann den Job ohne mutierenden Wiederholungsaufruf abschließen.

`background_adopt`: natives `store` auf Originalrequest/Dateien, danach frisches
`plan`, danach `adopt` mit genau diesem erhaltenen vollständigen Planbundle.
Store-No-op ist keine Ziel-/Auswahlfreigabe. Keine Raster-/Revealersetzung,
Legacy-Erstnachrüstung, neue Analyse, Modell-API oder zusätzliche Buchsicht.

### 8.4 Lock, Auftragslinie und dauerhafte Formen

Der stabile OS-Lock liegt unter `<target>/.picross-integration-batches/`, außerhalb
von content/game/authoring, unversioniert. Kanonischer geprüfter Root und seine
Dateisystemidentität binden ihn unabhängig vom Arbeitsroot. Native Writerlocks
gelten zusätzlich. Nicht löschen/reparieren, keine parallelen BA-B-Schreiber.
Der Kontrollordner enthält `owner.json`, `.batch-writer.lock`, `claims/` und
`anchors/`. Claims binden den unveränderten Auftragshash sowie pz-ID/Operation
an genau den eigenen Workroot. Umbenennung, Planrevision oder neuer Workroot
derselben Auftragslinie füllt keine Erlaubnis auf. Im bisherigen Planverlauf
werden Versuche pro pz-ID/Operation/Phase gezählt, nicht pro Jobnamen/Revision;
Budgets und Maxima dürfen in einer Fortschreibung nur gleich bleiben/sinken.

Der Arbeitsroot enthält ausschließlich `owner.json`, `plans/`, `attempts/`,
`checkpoint.json`, `report.json` und eigene atomare Schreibreste. Pro Versuch
`attempts/NNNNNN/reservation.json`, optional `result.json` und `output/`.
Höchstens 4096 dauerhaft reservierte Versuche. Vor *jedem* Fachaufruf, auch
Abgleich, werden Reservation und Checkpoint samt externem Anchor dauerhaft
geschrieben und gelesen. Jede Reservation bleibt unverändert; Ergebnis separat
append-only. Die ursprünglichen Plandateien bleiben unter
`plans/NNNNNN-<sha256>.json`. Plan-/Versuchslücken, unbekannte Ledgerdateien,
gekürzte Historie oder ein widersprüchlicher Checkpoint sind ein gemeinsamer
technischer Stopp. Atomarer Replace überschreibt nur die zuletzt gelesenen Bytes.
Ein Ergebnisfile ohne bestätigten externen Anchor bleibt erhalten, aber im
Checkpoint ausdrücklich `result=null`: erst der passende native lesende Abgleich
darf den unbekannten Abschluss feststellen, niemals dessen gespeicherter Flag.
Genau eine vor dem Anchor unterbrochene Ergebnisbuchung ist auch innerhalb einer
vorreservierten Abgleichgruppe erkennbar; sie erzeugt keine Erfolgsautorität.
Eine noch nicht im Anchor bestätigte Reservation kann kein Fachresultat besitzen,
weil vor dessen Bestätigung kein Fachaufruf starten darf. Der Anker bindet sowohl
alle vorhandenen Resultbytes als auch separat die Liste bestätigter Resultslots.
Erhaltene unbestätigte Dateien bleiben dadurch gegen spätere Veränderung gebunden,
ohne im Checkpoint eine Erfolgsautorität zu erhalten.
Bei einem direkten Nachfolgeplan darf ausschließlich dessen Anchor hinter dem
vollständig geschriebenen Checkpoint zurückliegen: lückenlose Originalplankette,
identische Reservierungs-/Result-/Bestätigungshashes und noch keine Reservation
der neuen Revision sind zwingend. Die unveränderten Writerbarrieren werden auch
für diesen erneut eingelesenen Plan geprüft. Reines status schreibt nichts;
erst ein ausdrückliches resume bestätigt den belegten Planübergang dauerhaft,
bevor es gegebenenfalls eine weitere Nachfolgerevision annimmt.
Offene oder erfolglos gebuchte mutierende Linien bleiben bis zu ihrem tatsächlich
bestätigten Abschluss im Plan. Ein Nachfolgeplan darf sie weder entfernen/ersetzen
noch durch neue Writer davor überholen; zuvor abgeschlossene Jobs dürfen davor
weiterhin ausschließlich lesend abgeglichen werden.

| Objekt | Exakte Schlüssel |
| --- | --- |
| PlanRef | `revision,file,sha256,bytes` (Datei relativ zum Workroot) |
| Bindings | `source_root,repo_root,target_root,work_root,history_root,work_identity,target_identity,tool_binding` |
| Identity | `device,inode` (nichtnegative Integer) |
| ToolBinding | `files,python,pillow,codecs`; files = sortiertes vollständiges relevantes FileRef-Inventar relativ zum Werkzeugroot, python = vollständiger Versionstext, pillow = Versionstext, codecs = `zlib,littlecms,jpeg,jpeg_turbo` als Text/null |
| Owner | `format` = `picross-integration-batch-owner-v1`, `batch_id,bindings` |
| Kontrollowner | `format` = `picross-integration-batch-control-v1`, `target_root,target_identity` |
| Claim | `format` = `picross-integration-batch-claim-v1`, `lineage,puzzle_id,operation,authorization_sha256,work_root,work_identity` |
| Anchor | `format` = `picross-integration-batch-anchor-v1`, `batch_id,work_root,work_identity,plan_sha256,attempts,reservations_sha256,results_sha256,acknowledged_sha256` |
| Reservation | `format` = `picross-integration-batch-reservation-v1`, `number,plan_sha256,job_id,puzzle_id,operation,phase,ordinal,inputs_sha256,tool_sha256,budgets,output_dir` |
| Result | `format` = `picross-integration-batch-result-v1`, `number,status,native,diagnostics,elapsed_seconds,error,exit_code,reached,output_files,remaining` |
| Attempt | `reservation,result` (Result/null; null heißt unklar/unterbrochen, niemals erfolgreich) |
| Reached | `entry,files` (unveränderter nativer Registryeintrag und sortierte FileRefs relativ zum Zielcheckout) |
| Lesender Batchabgleich | `status` = `reconciled`, `id`, `reached`; beziehungsweise `status` = `rollback-confirmed`, `id`, `plan_hash` für den vollständig frisch bestätigten alten Bildplanstand, niemals für Erfolg |
| JobView | `job_id,puzzle_id,operation,status,historical_completed,current_verified,attempt,reached,reason,next_step` |
| Checkpoint | `format` = `picross-integration-batch-checkpoint-v1`, `batch_id,plan,plans,bindings,attempts,jobs,status` |
| Report | `format` = `picross-integration-batch-report-v1`, `batch_id,plan,source_commit,tool_binding,status,exit_code,jobs,attempts,journal,elapsed_seconds,execution_seconds,reconciliation_seconds,waiting_seconds,human_seconds,fresh,next_step` |
| JournalView | `pending,staging` (relative Pfade/null beziehungsweise Pfadliste) |

Alle neuen Formen sind geschlossen geprüft. Roots sind absolute Texte, History
Text/null. `bindings` enthält tatsächliche relevante Modul-/Norm-/Methodenbytes
und Codec-/Pythonbindung; auch ausgeführte Module müssen zu `repo_root` passen.
Die Commitprovenienz allein reicht nicht. Toolwechsel stoppt Wiederverwendung
als stale; Originale werden weder umgehasht noch allein wegen eines anderen
Git-HEAD neu erzeugt. Die historische Bindung bleibt lesbar.

Reservation: `number` Integer 1..4096, `ordinal` Integer 1..100, Phase eine der
festen Schlüssel aus `max_attempts`, drei Hashfelder echte SHA-256, Budgets
exakt der zugehörigen historischen Planzeile, `output_dir` exakt
`attempts/NNNNNN/output`. `inputs_sha256` bindet das vollständige unveränderte
Jobobjekt ohne Namen/Budgets/Versuchszähler; Identität/Originale/Regeln/Parameter
bleiben darin. `tool_sha256` bindet die tatsächliche ToolBinding. Anchorzähler
ist Integer 0..4096, seine Hashes binden geordnete Listen tatsächlicher
Reservation-/Resultbytes (fehlende Datei null), einschließlich konservativ
verbrauchter Erlaubnisse. `acknowledged_sha256` bindet die entsprechend geordnete
Boolliste tatsächlich bestätigter Resultslots. Claims/Anchor sind keine Inhaltsfreigabe.

Result: Status `completed,blocked,failed,aborted,interrupted,recovery_required`;
`native` das unveränderte vollständige native JSON-Ergebnis, das oben ausdrücklich
geschlossene lesende BA-B-Abgleichergebnis oder null,
`diagnostics` das vollständige reale RI-Diagnoseobjekt, `elapsed_seconds`
endliche nichtnegative Zahl/null, `error` Text/null, `exit_code` Integer 0..255,
`reached` Reached/null, `output_files` vollständiges Inventar relativ zu output,
`remaining` Liste eigener Restpfade. Native Objekte behalten ihre eigenen
geschlossenen Verträge; BA-B führt keine zweite vereinfachte Fachautorität ein.
Unbekannte Crashzeit bleibt null. Native `planned,stored,registered,adopted,no-op`,
Blockade, vollständiger Rollback und offener Recoveryfall bleiben unterscheidbar.

### 8.5 Stopp, Crash und drei getrennte Resumewege

Jobs laufen strikt in Planreihenfolge. Der erste ungeklärte Eingang, Fachfehler,
Abbruch, Teil-Store, fremde Bytekonflikt oder Ledger-/Checkpointfehler stoppt vor
jedem folgenden Writer. Die vorhandene gemeinsame Erkennung erfasst sowohl
`content/.registration-pending.json` als auch `.registration-journal-*.tmp`.
Der vollständig erfolgreiche Präfix bleibt erhalten. Automatischer nativer
Rollback innerhalb des laufenden Einzelaufrufs bleibt erlaubt; danach offene
Recovery wird niemals im Runner gestartet. Erst ausdrücklich separat autorisierte
native Recovery, dann frisches Resume. Kein Locklöschen als Reparatur.

1. Register publiziert, Result noch nicht gebucht: erhaltenen vollständigen Export
   byteprüfen, frisches natives `registration(apply=False)` mit Ergebnis
   `no-op,registered=true,changes=[]` bestätigt den eigenen Abschluss. Kein
   mutierender Wiederholungsaufruf zur Diagnose. Bei nachgewiesenem vollständigem
   Rollback darf erst ein ausdrückliches Resume und verbleibende Erlaubnis wieder
   frisch planen/apply aufrufen; kein automatischer Retry im selben Lauf.
2. Hintergrund publiziert, Result noch nicht gebucht: altes unverändertes Bundle
   verwenden, **kein neuer Plan**. `catalog_background_change.adopt(...,
   no_op_only=True)` hat denselben vollständigen nativen Plan-/Work-/Quellen- und
   Snapshotprüfpfad. Er bestätigt ausschließlich den exakten eigenen Zielstand;
   sonst zwingende Ablehnung im selben Kontrollfluss vor `tx.execute`. Keine
   Vorprüfung mit anschließend allgemeinem mutierenden adopt und kein Rückspielen
   alter Bilder. Fehlendes Bundle oder unbekannter Stand braucht Diagnose.
   Nach separat erfolgter Recovery darf ein ausdrücklich gestartetes Resume
   den vollständig erhaltenen alten Planstand lesend bestätigen: unverändertes
   zuvor gebuchtes Planbundle, nativer vollständiger aktueller Snapshot und exakt
   dessen alte Quellen-/Namespacebindung. `rollback-confirmed` ist kein Erfolg;
   erst dann darf dieselbe ausdrückliche Wiederaufnahme eine verbleibende
   Plan-/Adopterlaubnis verwenden. Der alte Plan wird dabei nicht erneut
   mutierend angewandt. Ein nicht übereinstimmender Stand führt ausschließlich
   in den nativen No-op-only-Pfad oder zum Stopp, nie zu einem Mutationsfallback.
3. Gebuchter Erfolg, danach weitere Erfolge: alten Bildplan nicht mehr aufrufen.
   Beim Resume wird der aktuelle Gesamtkatalog für den gebuchten Erfolgspräfix
   einmal über `catalog_transaction.capture` vollständig frisch gelesen; für jeden
   Job zuvor getrennte endliche Abgleicherlaubnis reservieren. Danach den aktuellen
   Registryeintrag und jobbezogene Source-/Request-/Revision-/PNG-/Notice- oder
   Register-/Receiptbytes gegen die tatsächlich gebuchte `reached`-Bindung prüfen.
   Der Gesamtsnapshot ist nur im Prozess verwendbar; kein serialisierter RI-Kontext.
   Dieser `reconciled`-Abgleich ist kein gelockerter nativer Bild-No-op.

Nach neu ausgeführten Fachaufrufen bestätigt ein abschließender lesender Abgleich
die gesamte erreichte Auswahl anhand genau eines frischen Gesamtsnapshots und
der jobbezogenen Refs. Auch dafür je Job eine vorher dauerhaft gebuchte endliche
`reconcile`-Erlaubnis; keine automatische Aufstockung. Ein reines Resume einer
bereits vollständig gebuchten Auswahl verwendet nur seinen bereits beschriebenen
einen Abgleich. Das Ergebnis ist eine aktuelle geprüfte Momentaufnahme, keine
atomare Zusicherung gegen erst später schreibende fremde native Prozesse.

Nur aktuell vollständig bestätigte eigene Ziele werden übersprungen. Historischer
Erfolg bleibt `historical_completed=true`, auch wenn heute `current_verified=false`
und `status=stale`. Fremder/abweichender/retirierter Stand stoppt ohne Rekonstruktion.
Verbrauchte Versuche bleiben bei Crash, Umbenennung und neuer Planrevision verbraucht.
Separate Resumeprüfungen zählen `reconcile`. Keine automatische Erhöhung oder
unendliche Wiederholung. Ein gebuchtes P6 wird durch späteren Berichtfehler nicht
als fachlicher Rollback ausgegeben; Originalresult/Journalzustand bleiben sichtbar.

Eine ungebuchte Exportausgabe besitzt keine Wiederverwendungsautorität und wird
niemals für Registrierung konsumiert. Ihre Bytes bleiben erhalten. Ausschließlich
ein ausdrücklich gestartetes Resume darf mit einer verbleibenden bereits
gebundenen Exporterlaubnis einen neuen lokalen Exportversuch in einem neuen
Versuchspfad aus den erneut gebundenen Originalen ausführen. Erst dessen echtes
Fachresultat und vollständig gebuchtes Inventar dürfen zur Registrierung führen.
Ohne verbleibende Erlaubnis Stopp; kein Retry im ursprünglichen Lauf und kein
Neuaufbau allein wegen eines anderen Git-Heads.

### 8.6 Ergebnisse, Nachweise und Lebenszyklus

Jobstatus exakt `pending,running,completed,waiting_input,waiting_human,blocked,
failed,aborted,interrupted,stale,recovery_required`. `historical_completed` und
`current_verified` sind echte Bool, `attempt` Integer 1..4096/null, `reason` und
`next_step` Text/null, `reached` Reached/null. Checkpoint-/Report-Gesamtstatus und
Exit: `completed/0,invalid_input/2,incomplete/3,aborted/4,technical_error/5`.
Completed erfordert jeden Job historisch erfolgreich und aktuell bestätigt.
Report führt vollständige Attempts, ursprüngliche Fachresultate/Exitcodes,
Bindings und aktuelle Journalreste. Fresh ist bei ausgeführtem Lauf true,
historischem status false. Reine Statuslektüre erneuert keine Zielaussage und
führt ohne neue Prüfung `incomplete/3` mit erhaltenem historischem Einzelabschluss.

Reportzeiten sind endliche nichtnegative Zahlen/null. `execution_seconds` summiert
bekannte Einzelaufrufe außer reconcile; `reconciliation_seconds` nur Abgleiche.
Bei unbekanntem enthaltenem Crashintervall ist die jeweilige Summe und die
Gesamtlaufzeit null. Inklusive RI-Phasen werden nicht zusätzlich addiert.
`waiting_seconds,human_seconds` bleiben ohne Messung null. Kein behaupteter
Zeitgewinn und keine Inhalts-/Mainfreigabe durch completed.

Prüfbedarf: Pflichtkern `docs/ci-required` einschließlich Windowsbau sowie genau
`tools,production.adapter,production.catalog` vollständig. Kleine neue echte
synthetische BA-B-Regressionen gehören ausdrücklich zu catalog. Bestehende Reader-
und Importinventare werden konsistent nachgeführt. Kein neuer Algorithmus-/Bild-
oder Runtimeprüfauftrag, kein neuer permanenter CI-Job.

BA-B-T01 ist die einmalige tatsächliche CLI-Probe mit zwei neuen endabgenommenen
test_only-Paketen selected/none, eigenem Hintergrundwechsel vor weiterem Register,
echtem Prozessabbruch, Resume, Journal-/Stagingstopp, erhaltenem Präfix und separat
ausgeführter nativer Recovery. Die Fixtures und Probe liegen im Produktdiff.
Genau sechs Textoriginale: `batch-plan.json,checkpoint.json,report.json,cli.log,
operations.jsonl,manifest.json`; tatsächliche Nachfolgepläne zusätzlich, falls
verwendet. Vollständige native Objekte/RI-Ausgaben in operations, Head/Umgebung/
sauberer Stand/Hashinventar/Szenario-/Byte-/mtimebelege im Manifest. Native Bundles
und Binärdateien im Erzeugerlauf durch Reader prüfen, keine Galerie archivieren.

Normale CI `evidence.mode=none`. Originale getrennt auf temporärem
`review/491-ba-b` vom endgültigen Produkt-Head, unveränderliche überprüfte Direktlinks
im Draft-PR. Empfänger BA-B-A01 mit Repositoryzugriff, Aufbewahrung bis unabhängiger
Prüfung und beauftragtem Rückbau, spätestens 18.11.2026; Refablauf ist nicht automatisch.
BA-B-A01 bleibt unabhängiges A-Gate vor Merge, Selbstreview separat. Kein Merge
oder Gesamtabschluss von #491 durch die Implementierungslieferung.
