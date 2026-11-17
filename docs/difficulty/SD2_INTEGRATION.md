# Difficulty: Datenformen, Reader und Produktionsstandard

- Dokument-ID: `SD2-INTEGRATION`.
- Status: aktive methodenübergreifende Datenverträge und ausdrücklich benannte historische Reader.
- Dokumentstand: 17.11.2026.
- Zuständigkeit: Rating-/Checked-Unterformen, Auswahlberichte, Defaultrecord und Aktivierungsplan.
- Normsprache: MUSS ist verpflichtend; DARF NICHT ist ein Verbot; DARF erlaubt eine Option.

## Zuständigkeiten

| Gegenstand | Definierende Quelle |
| --- | --- |
| Gemeinsame Fachgrenzen und Methodenbedeutung | [SD](PUZZLE_DIFFICULTY.md), [SD2](PUZZLE_DIFFICULTY_V2.md) |
| 0.3-Regeln/Formel/Freeze | [SD-Analyzer](SD_ANALYZER.md), [SD-Kalibrierung](SD_CALIBRATION.md) |
| 0.4-Regeln/Formel/Freeze | [SD2-Analyzer](SD2_ANALYZER.md), [SD2-Kalibrierung](SD2_CALIBRATION.md) |
| Aktive Hülle, Quellenpriorität, Ratingadoption und aktuelles Katalogjournal | [SD-Catalog](SD_CATALOG.md) |
| Erstintegration und ihre Recovery | [RI](../production/PUZZLE_INTEGRATION.md), [RI-ONE](../production/PUZZLE_INTEGRATION_SINGLE_PATH.md) |
| Gezielte Raster-/Bild-/Metadatenpflege | [Editor §13](../tools/PUZZLE_EDITOR.md#13-pe-edit2-gezielte-pflege-statt-vollbestandsprüfung) |
| Runtime-/Spiel-/Savevertrag und sichtbare Bewertung | [P1](../game/PROTOTYPE_P1.md), [Katalogdarstellung](../game/CATALOG_PRESENTATION.md) |

Die folgenden historischen Rating-/Berichtsreader sind tatsächlich noch
implementiert. Ihre Lesbarkeit erlaubt keine frühere Export-, Registrierungs-
oder Journalgeneration. Aktuelle Integration verlangt weder Producercommit noch
alte Werkzeugdateien, Originalexport, Paket-/Receipthistorie oder deren Replay.

## C-V01-01 · Methoden und tatsächliche Readergrenze

0.3 und 0.4 MÜSSEN mit den unveränderten Freezes ihrer Kalibrierungsverträge
geprüft werden. Beide Quellen-/JSON-Sätze bleiben unverändert; neue Integration
liegt außerhalb der Freezes. Die Methodenprüfung bindet die tatsächlich lokalen
gefrorenen Dateien, nicht nur einen behaupteten Hash. Das ist keine Forderung
nach historischen Producer-/Integrationsbytes.

| Form | Methoden | Heutige Verwendung |
| --- | --- | --- |
| `picross-current-difficulty-v1` | 0.3, 0.4 | Aktive Hülle für neue Integration und Ratingübernahme; SD-Catalog definiert sie. |
| `picross-catalog-difficulty-v1`, `picross-catalog-difficulty-v2` | nur 0.3 | Bestehende aktive Dateien bleiben direkt lesbar. |
| `picross-catalog-difficulty-v3` | nur 0.4 | Bestehende aktive Dateien bleiben direkt lesbar. |
| `picross-checked-difficulty-v1`, `picross-checked-difficulty-v2` | nur 0.3 | Geprüfte Analyse-Arbeitsdaten; v1 besitzt keine Modusbindung. |
| `picross-checked-difficulty-v3` | nur 0.4 | Geprüfte Analyse-Arbeitsdaten. |
| SD-A-v1, SD2-A-v1 und SD2-B-v1 | jeweils eigener Analyzer-/Methodenvertrag | Eigenständige geschlossene Analyse-/Bewertungsbundles. |
| `picross-catalog-difficulty-report-v1` bis `-v6` | v1–v3 nur 0.3; v4–v6 0.3/0.4 | Struktur-/Markdownreader; aktuelle Vorschau/Adoption verwendet ausschließlich v6. |
| `picross-difficulty-activation-plan-v1` bis `-v3` | 0.3/0.4 | Strukturreader; aktuelle Aktivierung verwendet ausschließlich v3. |

Unbekannte/doppelte Schlüssel, nichtendliche Zahlen, falsche Typen einschließlich
bool statt Integer und fremde Methoden sind Fehler. Eine fehlende oder defekte
heute erforderliche aktive Ratingdatei stoppt den Reader; es gibt keinen
Fallback auf `entry.production`. Historische 0.1-/0.2-Werte bleiben nur in ihren
unterstützten Projektions-/Berichtsformen lesbar.

Ausführbare Reader:
[`catalog_rating`](../../tools/puzzle_production/catalog_rating.py),
[`current_rating`](../../tools/puzzle_production/current_rating.py),
[`sd2_catalog_rating`](../../tools/puzzle_production/sd2_catalog_rating.py),
[`catalog_analysis`](../../tools/puzzle_production/catalog_analysis.py),
[`catalog_method`](../../tools/puzzle_production/catalog_method.py).

## C-V01-02 · Geschlossene Rating- und Arbeitsformen

### Gemeinsame Bindungen

| Objekt | Exakte Felder und Werte |
| --- | --- |
| `current_source` | `id,runtime_revision,definition_sha256`; Revision 1…1000000, SHA-256 der aktuellen Definitionsbytes. |
| `logic_binding` | `analysis_hash,matrix_hash`; SHA-256 des normalisierten methodenspezifischen Analyseinputs beziehungsweise der Lösungsmatrix. |
| `production_mode` | `mono` oder `color`; ausdrücklich gebunden, keine Ableitung aus der Palettengröße. Mono verlangt eine Vordergrundfarbe; einfarbiges Color bleibt Color. |
| Ursprüngliches `rating.source` | `sha256,bytes,kind,engine_logic_hash,definition_id,runtime_revision,production_mode`; Runtime-Eingang mit `kind=runtime`, `production_mode=unknown`, Bytes 1…2 MiB und Revision 1…1000000. |

Für 0.3 bindet `analysis_hash` den SD-A-Input, für 0.4
`picross-sd2-input-v1`. Die ursprüngliche Bewertungsquelle bleibt bei Rebind
unverändert. Rebind benötigt gleiche ID, normalisierte Logik, Matrix und Modus;
nur `current_source` und der äußere Hash ändern sich. Echte Logik-/Modusänderung
benötigt die neue passende Analyse der aktiven Produktionsmethode.

### Checked-Hüllen und weiterhin lesbare aktive Alt-Hüllen

Basismenge `B = {current_source,logic_binding,rating,compact_analysis}`.
Die Feldmengen sind geschlossen:

| Hülle | Exakte äußere Feldmenge |
| --- | --- |
| Checked v1 | `format` + B + `analysis_report_hash,verification_hash,tool,checked_hash` |
| Checked v2/v3 | Checked-v1-Felder + `production_mode` |
| Aktive v1 | `format` + B + `rating_revision,adoption,record_hash` |
| Aktive v2/v3 | Aktive-v1-Felder + `production_mode` |
| Historische `adoption` | `kind,previous_record_hash,analysis_report_hash,verification_hash,tool,report`; kind `analysis`/`rebind`, Vorgänger null oder SHA-256, report null oder exakt `run_id,result_hash`. |

Äußere Dateien höchstens **96 KiB**, eingebettete Bewertung **64 KiB**.
`rating_revision` liegt in 1…1000000. Der jeweilige äußere Hash bindet alle
anderen Felder. Aktive Hüllen verlangen `rated`; unvollständige, widersprüchliche
oder abgebrochene Befunde dürfen Checked-Arbeitsdaten sein, jedoch keine aktive
Bewertung. Ihre Nichtübernahme erhält gültige Altwerte.

`tool` hat exakt `id,version,modules`, ID `picross-catalog-difficulty`.
Version 1 bindet die Hashfelder für `catalog_rating.py`, `catalog_analysis.py`,
`catalog_transaction.py`, `catalog_integration.py`; Version 2 zusätzlich
`sd2_catalog_rating.py`, `catalog_method.py`. 0.3-Hüllen verwenden Version 1,
0.4-Hüllen Version 2. Historische Werkzeugidentitäten werden strukturell geprüft,
nicht gegen spätere lokale Integrationsbytes verglichen. Die aktuelle Hülle
benötigt diese Provenienzfelder nicht; ihre Definition bleibt in SD-Catalog.

### Eingebettete Bewertung und kompakte Analyse

0.3 verwendet das unveränderte `picross-difficulty-rating-v1` aus
[SD-Kalibrierung](SD_CALIBRATION.md). Sein `method` enthält den vollständigen
Methodensatz. 0.4 verwendet `picross-catalog-sd2-rating-v1` mit exakt
`format,method,method_hash,analysis_result_hash,source,result,rating_hash`.
Hier ist `method` die Zeichenfolge `picross-difficulty-0.4`, `result` das
vollständige `picross-sd2-rating-v1` aus SD2-Kalibrierung. `rating_hash` bindet
alle übrigen Felder; `analysis_result_hash` bindet den geprüften Rohbefund.

| Methode | Exakte Felder von `compact_analysis` |
| --- | --- |
| 0.3 | `result_hash,trace_hash,metrics_hash,status,reason,line_analysis_complete,line_fixpoint_confirmed,deduction_complete,r4,metrics` |
| 0.4 | `result_hash,analysis_hash,trace_hash,profiles_hash,status,reason,line_analysis_complete,line_fixpoint_confirmed,deduction_complete,r4,structure,wave_count,new_singletons` |

0.3-`metrics` enthält exakt `wave_count,family_waves,family_line_applications,
rule_applications,highest_family_used,unique_changed_cells,unique_partial_cells,
cell_change_events,new_singletons,partial_change_events,removed_values,
simple_fraction_all_cells,simple_fraction_determined,r0_fraction_all_cells,
aggregation,workload`; `aggregation=null`, Bedeutungen nach SD-Analyzer.
`workload` hat exakt `width,height,cells,colors,clue_count,clue_length_sum,
total_clues,total_clue_length`; beide Achsenobjekte haben `row,column`.

0.4-`profiles_hash` bindet die vollständigen drei Rohprofile im externen A-Bundle.
`structure` ist exakt das Workload-Strukturobjekt aus SD2-Analyzer und wird ohne
Deduktionssuche gegen die Definition geprüft. `wave_count` liegt in 0…80000,
`new_singletons` in 0…Zellzahl; `solved` verlangt sämtliche Zellen.
Status, Gründe, Vollständigkeit und R4-Bindung folgen dem jeweiligen Analyzer.

Das gemeinsame optionale `r4` hat exakt `required,label,necessity,proof,baseline,
proof_profile_hash,baseline_profile_hash,proof_status,baseline_status,
proof_verified,baseline_verified,instrumentation`. Proof-/Baseline-Refs sind
exakt `sha256,bytes` mit 1…64 MiB; beide Verifikationsflags sind true.
`instrumentation=separate_R4_evidence_not_synchronous_waves`. `necessity` ist
`required`, `not_required` oder `unproven` nach den bestehenden Analyzerregeln;
erforderliches R4 verlangt den passenden stalled-Fixpunkt und vollständigen
solved-Paarproof, keine vollständig gemessenen Paarwellen.

Die eingebettete Bewertung MUSS strukturell und arithmetisch dem eingefrorenen
Zahlenvertrag entsprechen. 0.4-Rationale sind gekürzt, Zähler in 0…10^100,
Nenner in 1…10^100, keine bools. Beiträge, Score, Grenzen/Abstände, Stufe ohne
Umfang und Umfangsschutz werden geprüft. Vollständige Linienfälle verwenden
die B-Signale, R4 den festen Anker. Datenprüfung ist kein erneuter Deduktionsproof.

### Expliziter Bundleimport

Nur der explizite Import prüft das externe Analyse-/Bewertungsbundle frisch und
unabhängig. Er vergleicht alle Eingangsbytes vor und nach der Prüfung. Die
geschlossenen A-/B-Dateimengen bleiben bei ihren Analyzer-/Kalibrierverträgen.

| Moduskontext | Exakte Felder und Verzeichnisgrenze |
| --- | --- |
| `picross-difficulty-context-v1` | `format,production_mode,source,context_hash`; 0.3-Arbeitsbundle mit optionalem `catalog-context.json`. Ohne Kontext entsteht Checked v1 ohne Modusbindung. |
| `picross-difficulty-context-v2` | `format,production_mode,source,method,method_hash,context_hash`; ausschließlich 0.4. Äußere Arbeitsmappe exakt `catalog-context.json` und `rating/`; `rating/` bleibt das geschlossene B-Bundle. |

Quelle, Modus und Methode MÜSSEN konsistent zum tatsächlichen Runtimeinput sein.
Kontextdateien dürfen nicht in das geschlossene SD2-A-/B-Bundle eingeschoben
werden. Modusgebundene Neubewertung und Rebind verlangen den ausdrücklichen Modus.
Ein bestehendes identisches Registrierungsergebnis wird durch eine spätere
Defaultänderung nicht nachträglich bewertet; RI definiert diesen No-op.

## C-V01-03 · Auswahlbericht und Runtime

### Aktueller Bericht v6 und historische Strukturreader

Alle Berichtsversionen haben exakt `format,run_id,result,result_hash,operation`.
`run_id` erfüllt `[a-z][a-z0-9-]{0,63}`. Limit **16 MiB**, höchstens **10000**
eindeutige sortierte IDs, Grundtext **1…2048** Zeichen bei offenen Fällen.
`result_hash` bindet ausschließlich `result`; `operation` liegt außerhalb der
Ergebnisidentität und hat exakt `created_utc,phase`, Phase `preview`/`adopted`,
UTC-Zeit `YYYY-MM-DDTHH:MM:SSZ`.

| Version | Exakte `result`-Felder | Zusätzliche Zeilenfelder / Quellenlimit |
| --- | --- | --- |
| v1 | `selection,source_commit,method_hash,snapshot,entries,distribution` | keine / kein `sources` |
| v2 | v1 + `sources` | `previous_rating_revision` / 70003 |
| v3 | v2 | `previous_rating_revision` / 80003 |
| v4–v6 | v2 + `method` | `previous_rating_revision,assessment` / 80004 |

Jede Zeile hat als Basismenge exakt `id,current_source,logic_binding,old,proposed,
status,reason,rating_hash,checked_hash,previous_record_hash` plus die oben
benannten Versionsfelder. `status` ist `rated`, `unrated`, `invalid_input` oder
`technical_error`. Bei rated ist `reason=null` und proposed eine gültige
Projektion der Zielmethode; andernfalls ist proposed null und ein Grund Pflicht.
Rated/unrated binden Quelle, Logik, Rating- und Checked-Hash vollständig.
Eine vorhandene Vorgängerbewertung bindet Hash und Revision 1…1000000;
bei fehlendem Vorgänger sind beide null.

`selection` ist `ids` oder `all`, `source_commit` ein 40-stelliger kleiner
Git-SHA. `snapshot` hat exakt `content/registry.json,game/data/registry.json,
content/categories.json` mit SHA-256-Werten. `sources` bildet relative aktuelle
Dateinamen auf SHA-256 oder erwartete Abwesenheit null ab. Die aktuelle
Quellenmenge ist in SD-Catalog definiert; frühere Quelleninventare werden nicht
stillschweigend vervollständigt.

Pro Bericht gilt genau eine Zielmethode. V1–v3 bedeuten 0.3; v4–v6 führen sie
explizit. `old` darf alle vier unterstützten Projektionsmethoden oder null
enthalten; `proposed` ausschließlich die Zielmethode. `assessment` ist bei
rated 0.4 exakt das B-Assessment, sonst null. Übernahme bindet es zusätzlich
an das Checked-Ergebnis. Markdown nennt Alt-/Neumethode und Teilwerte.
`distribution` enthält ausschließlich gezählte Alt-/Vorschlagswerte
`L1,L2,L3,L4,L5,unrated`, keine Kalibrierung.

`validate_report` und Markdown lesen v1–v6. Aktuelle Vorschau schreibt v6;
aktuelle Adoption verlangt v6 und einen frisch passenden aktuellen Quellenstand.
Lesbarkeit historischer Berichte ist keine heutige Übernahmeberechtigung.

### Difficultyprojektion

Die Projektion ist null oder exakt `method,level,assessment_type,confidence,
plausible_range,r4_required`. 0.3/0.4 verlangen `instrumented`, `medium`,
L1…L5, `[level,level]` und bei notwendigem R4 L5. Keine Scores, Profile oder
Freitexte gelangen in die Runtime. `null` bedeutet „Nicht eingestuft“.

Der Godot-Reader liest Runtime v2–v8 unter den jeweiligen geschlossenen
Feldmengen: v2 ohne Difficulty, v3/v4 mit Methoden bis 0.3, v5–v8 zusätzlich
0.4. Der **aktuelle Writer** projiziert ausschließlich Runtime v8; seine
übrigen Inhalts-/Bildfelder gehören zu RI/P1. Historische Runtime-lesbarkeit
reaktiviert keine alten Writer oder Journale.

## C-V01-04 · Explizite Aktivierung

Der vorhandene gültige Record [`content/difficulty-method.json`](../../content/difficulty-method.json)
wählt aktuell `picross-difficulty-0.4`. Nur eine tatsächlich fehlende Datei
bedeutet im Methodenreader den historischen Default 0.3. Eine vorhandene
ungültige Datei darf nicht ignoriert werden.

`picross-difficulty-default-v1` hat exakt
`format,revision,method,method_hash,previous_record_hash,activation_hash,record_hash`.
Limit **4096 Bytes**; Revision 1…1000000. Bei Revision 1 ist der Vorgänger null,
sonst SHA-256. Methode 0.3/0.4 benötigt ihren gültigen Freeze. Der Record ist
Produktions-/Werkzeugkontext, keine Runtime-/Saveinformation und keine
Bestandsneubewertung.

Alle Aktivierungspläne v1/v2/v3 haben exakt
`format,expected,target,sources,result_hash`:

- `expected`: exakt `method,method_hash,record_hash,revision`; bei fehlendem Record null und Revision 0, sonst dessen Revision 1…1000000.
- `target`: exakt `method,method_hash`; andere unterstützte Methode als expected.
- `sources`: relative aktuelle Dateinamen auf SHA-256 oder null, einschließlich Defaultpfad.
- `result_hash`: kanonischer Hash aller übrigen Felder.

Limit **16 MiB/80004 Quellen**. Der Strukturreader akzeptiert v1–v3, der
aktuelle Planer/Adopter ausschließlich `picross-difficulty-activation-plan-v3`.
`catalog_method plan` benötigt Checkout, erwartete Methode, Zielmethode, exakten
Zielhash und neuen externen Ausgabepfad. Gleiche Ziel-/Ausgangsmethode erzeugt
keinen Aktivierungsplan.

`adopt` prüft beide Freezes, Quellen, Erwartung und Planhash vor Mutation.
Ausschließlich der Defaultrecord ändert sich; Runtime/Bewertungen bleiben
bytegleich. Wiederholung akzeptiert exakt den eigenen Record mit Vorgängerhash,
`expected.revision + 1` und sonst identischen Quellen, ohne Rewrite/Lock/mtime.
Gleiche Methode oder beliebig höhere Revision genügt nicht. Fremde Änderung oder
zwischenzeitliche andere Aktivierung macht den Plan stale.

Neue Registrierung und echte Logik-/Modusänderung benötigen die aktive Methode.
Reine Metadatenpflege darf die gültige Bewertung rebindend erhalten. Explizite
Katalogbewertung darf beide Methoden unabhängig vom Produktionsdefault wählen.
Lesen, Sync, Cleanup, Recovery, Build, Spielstart oder CI aktivieren nichts.

## C-V01-05 · Getrennte aktuelle Schreibwege

[SD-Catalog](SD_CATALOG.md#aktuelle-katalogjournale) definiert allein das aktuelle
Katalogjournal für Bewertung, Datum, Standard, Metadaten und Sync. Es schreibt
keine Definitionen/Bilder und registriert keine neue ID. Erstintegration folgt
RI; gezielte Editorpflege verwendet den eigenen kleinen Plan/Journal aus §13.
Eine breite Quellenbindung einer ausdrücklichen Kataloganalyse ist keine
Vollbestandsprüfungspflicht für Editor-Detail oder Metadatenpflege.

Alte registration-/content-update-/metadata-/reveal-/difficulty-activation-
Journale sind **keine aktuellen Recoveryeingänge**. Die frühere Export- und
Fullcheckoutmatrix samt damaligen Limits, T/K-Mengen, Runtimegenerationen und
HP-I1b1-Zusatz bleibt nur im
[festen historischen Vertragsstand](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/SD2_INTEGRATION.md#c-v01-05--gemeinsame-transaktion-und-altjournalmatrix).
Sie erzeugt keine zusätzliche heutige Reader-/Writerpflicht.

## C-V01-06 · CLI, Produktion und Prüfung

`catalog_analysis analyze/preview/preview-checked --method` wählt ausdrücklich
0.3 oder 0.4; **ohne Option bleibt dieser CLI-Default 0.3**. Er ist nicht der
Produktionsdefault. Neue Produktionsbewertungen MÜSSEN die aktive Methode
explizit wählen. Import dispatcht nach dem geschlossenen Kontext; alte Bundles
bleiben alt. Ressourcenflags und getrennte Analyse-/Prüfbudgets bleiben beim
jeweiligen Analyzer; 0.4 verwendet den unveränderten SD2-Budgettyp.

`candidate`, Analyse/Import und Rebind sind Arbeitswerkzeuge. Der finale
Integrationsinput und `target_adapter`-Aufruf folgen ausschließlich RI/ZA-1;
der frühere Export-/Register-/Updatepfad wird hier nicht wiederhergestellt.
Plan/Adopt analysieren nicht. Registrierung, Sync, Cleanup, Recovery, Export,
Build und Spielstart enthalten keine verborgene Schwierigkeitsanalyse.
Der ausdrücklich benötigte Logiknachweis bleibt davon getrennt.

Exit 0 bedeutet Erfolg/Plan/No-op, 2 Daten-/Vertrags-/Stalefehler, 4 Abbruch oder
Ressourcenende. Fehlgeschlagene Einzelanalysen bleiben mit Grund offen.
Arbeitsdateien liegen außerhalb der Runtime und dauerhaften Ratingquellen.
Die [CLI-Anleitung](../../tools/puzzle_production/README.md) führt die Bedienung;
[CI_WORKFLOW_V2](../ci/CI_WORKFLOW_V2.md) bestimmt neue Prüfungen aus dem Diff.
Methoden- und Integrationsfälle bleiben unabhängig synthetisch. Frühere
SD2-C-T01-/Review-/Webausnahmen sind historische Nachweise, keine heutigen Gates.
