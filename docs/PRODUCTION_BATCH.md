# BA-A: lokale Batchverarbeitung und Wiederaufnahme

Vertrag vor konsumierendem Code, 10.11.2026. Maßgeblich:
[BA-A / #491](https://github.com/venomenon328/picross/issues/491#issuecomment-6779908657),
[Produktionsvertrag](PUZZLE_PRODUCTION.md),
[Authoring](ai-workflows/PUZZLE_AUTHORING.md),
[Hintergründe](PUZZLE_BACKGROUNDS.md) und
[Werkzeuganleitung](../tools/puzzle_production/README.md).
Dieser Vertrag schließt D01–D07 und BA-A-K01–K12. Tatsächlicher Liefer- und
Reviewstand bleibt im Produkt-PR. BA-B und echte Inhaltsproduktion sind nicht
Teil dieses Pakets; BA-A schließt das Gesamtissue nicht.

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
