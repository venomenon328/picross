# SD-C1: Bewertungsquelle, Import und Transaktionen

Stand: 17.10.2026 · Vertrag 1.0 · SD-C-P01 aus
[#238](https://github.com/venomenon328/picross/issues/238).
Die folgenden Formate wurden vor der ersten Codeänderung festgelegt und werden
von den neuen `catalog_*`-Modulen implementiert. [Befehlsanleitung](../tools/puzzle_production/README.md).
SD-C1 liefert den technischen Weg; SD-C2 und reale Bewertungen bleiben separat.
[SD](PUZZLE_DIFFICULTY.md), [SD-A](SD_ANALYZER.md) und der eingefrorene
[SD-B-Vertrag](SD_CALIBRATION.md) gelten unverändert.

## Gemeinsame Grenzen

JSON verwendet die vorhandene Kanonisierung: sortierte Schlüssel, UTF-8, keine
Zwischenräume/BOM, keine nichtendlichen Zahlen; Dateien enden mit LF. Doppelte
oder zusätzliche Schlüssel und falsche Typen werden abgewiesen. Ganzzahlen sind
keine Booleans. SHA-256 sind 64 kleine Hexzeichen, Git-Commits 40 kleine Hexzeichen.
IDs folgen `pz-[a-z0-9][a-z0-9-]{0,59}`, Run-IDs `[a-z][a-z0-9-]{0,63}`.
Pfade werden aus geprüften IDs/Registrydaten gebildet; keine Ratingpfade öffnen.
Traversal, Windows-Aliase, Gerätepfade, Symlinks und Reparsepunkte sind verboten.

Aktive und geprüfte Einzeldateien: höchstens 96 KiB, enthaltenes SD-B-Rating
höchstens 64 KiB. Bericht: höchstens 16 MiB und 10000 eindeutige, nach ID sortierte
Einträge. Journal: höchstens 24 MiB. Grenzen stoppen vor Mutation; große Übernahmen
können in ausdrücklich gewählte Teilmengen geteilt werden. Vollständige Bundles
liegen ausschließlich im ausdrücklich angegebenen Arbeitsverzeichnis außerhalb
von `game/` und `content/difficulty/`.

## Aktive Hülle

`content/difficulty/<pz-ID>/rating.json` hat Format
`picross-catalog-difficulty-v1` und exakt diese Felder:

| Feld | Vollständiger Untervertrag |
| --- | --- |
| `format` | Obige konstante Kennung. |
| `rating_revision` | Ganzzahl 1…1000000; nur tatsächliche Übernahme/Neubindung erhöht sie. |
| `current_source` | Exakt `id`, `runtime_revision` (1…1000000), `definition_sha256`; tatsächliche aktuelle Definitionsbytes. |
| `logic_binding` | Exakt `analysis_hash`, `matrix_hash`; ersterer nach SD-A, letzterer kanonischer Hash der numerischen Schema-2-Zielmatrix. |
| `rating` | Vollständiges unverändertes `picross-difficulty-rating-v1` nach SD-B, ausschließlich `rated`, `instrumented`, `medium`. |
| `compact_analysis` | Unten definierte kompakte geprüfte Zusammenfassung. |
| `adoption` | Exakt `kind` (`analysis` oder `rebind`), `previous_record_hash` (Hash oder null), `analysis_report_hash`, `verification_hash`, `tool`, `report` (null oder exakt `run_id`, `result_hash`). |
| `record_hash` | Kanonischer Hash der Hülle ohne dieses Feld. |

`tool` hat exakt `id=picross-catalog-difficulty`, `version=1`, `modules` als
Zuordnung von genau `catalog_rating.py`, `catalog_analysis.py`,
`catalog_transaction.py`, `catalog_integration.py` zu Dateihashes. Das ist
Provenienz, keine aktive Bindung an den jeweils neuesten Werkzeugcommit.
`rating.source` bleibt auch bei Neubindung unverändert; alle seine SD-B-Felder
und deren Typen bleiben strikt. Seine ID muss der aktuellen ID entsprechen.

`compact_analysis` hat exakt `result_hash`, `trace_hash`, `metrics_hash`, `status`,
`reason`, `line_analysis_complete`, `line_fixpoint_confirmed`, `deduction_complete`,
`r4`, `metrics`. Die drei Hashes binden das vollständig geprüfte SD-A-result,
die Spur und die vollständigen ursprünglichen Metriken. Status/Grund/Booleans
und `r4` entsprechen exakt dem SD-A-Vertrag. R4 enthält nur dessen feste
Status-/Profil-/Dateihashbindungen, keine Proofschritte. `metrics` enthält exakt
die SD-A-Gesamtmetriken **ohne `waves`**: `wave_count`, `family_waves`,
`family_line_applications`, `rule_applications`, `highest_family_used`,
`unique_changed_cells`, `unique_partial_cells`, `cell_change_events`,
`new_singletons`, `partial_change_events`, `removed_values`,
`simple_fraction_all_cells`, `simple_fraction_determined`, `r0_fraction_all_cells`,
`aggregation` (null), `workload`. Familien und Regeln sind die festen SD-A-Keys.
Zähler sind nichtnegative Ganzzahlen, begrenzt durch 80000 Wellen, 100 Linien
je Welle und 2500 Zellen mit höchstens acht Vordergrundfarben; Positionszähler
höchstens Zellzahl. Bruchpaare behalten SD-A-Zähler/Nenner einschließlich des
definierten `[0,0]`; sie werden nicht gerundet. `workload` hat exakt die SD-A-Felder
`width`, `height`, `cells`, `colors`, `clue_count`, `clue_length_sum`, `total_clues`,
`total_clue_length`; die Achsenobjekte enthalten `row` und `column`.

Ratingprofil und Formelresultate werden auf Schema, Grenzen und arithmetische
Konsistenz geprüft. Ein Hash ist weder Signatur noch erneuter Deduktionsbeweis.
Ordentliche Loader/Register/Update/Sync/Recovery starten weder Solver noch
Bewertungsspur-Replay. Nur der explizite Bundleimport prüft die volle Spur und
gegebenenfalls beide R4-Proofs mit den vorhandenen eingefrorenen APIs.

## Geprüfter Arbeitsinput und Kandidatenadapter

`picross-checked-difficulty-v1` hat exakt `format`, `current_source`,
`logic_binding`, `rating`, `compact_analysis`, `analysis_report_hash`,
`verification_hash`, `tool`, `checked_hash`. Gemeinsame Felder folgen oben;
`checked_hash` bindet das Objekt ohne dieses Feld. Auch ein vollständig geprüftes
`unrated`-Ergebnis ist als Arbeitsinput erlaubt, niemals als aktive Bewertung.
Die beiden Beleg-Hashes stammen aus dem tatsächlich gelesenen SD-A-Bericht und
dem Ergebnis der vollständigen `check_bundle(..., method=...)`-Prüfung.

Der vorbereitende Adapter nimmt ausdrücklich Kandidatenmatrix, validiertes Design
und normalisierte Logik entgegen. Er verwendet `target_adapter.definition` mit
derselben Leer-/Farbabbildung und erzeugt eine Schema-2-Datei mit vorläufigem
Revealnamen/-pfad. Dieser Eingang ist keine Exportfreigabe. Die Matrix wird gegen
die Hinweise geprüft; tatsächliche Deduktions-/Herkunfts-/Endfreigaben bleiben im
normalen Produktionsweg Pflicht. Ein späterer Export darf den geprüften Input
nur bei identischer ID, Analysehash und Zielmatrix neu binden. Registrierung
verlangt dafür ausdrücklich den geprüften Input; keine heimliche Analyse.

## Quellenpriorität und Projektion

Fehlende aktive Datei erhält die unveränderte historische 0.1-/0.2-Projektion
beziehungsweise null. Eine vorhandene ungültige, veraltete oder unvollständige
Datei stoppt ausdrücklich; kein Fallback. Definitionsbytes, ID/Revision,
Analyse-/Matrixhash, Methode, Rating und kompakte Angaben müssen zusammenpassen.
Andere Registryeinträge, Git-HEAD und Produktionscleanup entwerten kein Rating.

Die Runtime bleibt v3 mit exakt sechs Difficultyfeldern. 0.3 verwendet L1…L5,
`instrumented`, `medium`, das geprüfte R4-Flag und `[Lx,Lx]` als Punktprojektion.
Der Tooltip erklärt Modellschätzung, mittlere Aussagekraft und fehlende menschliche
Kalibrierung. Diese Spanne ist kein menschliches Unsicherheitsintervall. Runtime-v2
behält exakt sieben Eintragsfelder; 0.1/0.2 bleiben unverändert lesbar.

Neue Registrierung und logikrelevante Definitionsänderung verlangen 0.3.
Identische Legacywiederholungen bleiben No-op. Reine Metadatenänderung erlaubt
ausdrücklichen Rebind ohne Analyse nur bei gleicher ID/Logik/Matrix. Gleiche
Ratingidentität und aktuelle Bindung ändern weder Bytes noch Bewertungsrevision;
operative Zeiten oder neue Berichte erzeugen allein keine Änderung.

## Auswahlbericht und getrennte Übernahme

Explizite Einzel-ID, wiederholte ID-Auswahl oder `--all` sind gegenseitig exklusiv;
kein Auswahl-Default. Der Werkzeugweg kann analysieren oder bereits vorhandene
Bundles vollständig prüfen/importieren. Ein nicht gelöster Linienlauf verwendet
R4 nur mit ausdrücklich übergebenen passenden Baseline-/Paarproofs. Ohne diese
bleibt er `unrated`; kein automatischer Paarlauf.

`content/difficulty/reports/<run-id>/report.json` verwendet
`picross-catalog-difficulty-report-v1`: exakt `format`, `run_id`, `result`,
`result_hash`, `operation`. `result` hat exakt `selection` (`ids` oder `all`),
`source_commit`, `method_hash`, `snapshot`, `entries`, `distribution`.
`snapshot` bindet exakt Dateihashes von Inhaltsregistry, Kategorien und Runtime.
`operation` enthält exakt `created_utc` (UTC-ISO-Zeit) und `phase`
(`preview` oder `adopted`); diese Ausführungsdaten sind nicht Teil von `result_hash`.

Jeder Eintrag hat exakt `id`, `current_source`, `logic_binding`, `old`, `proposed`,
`status`, `reason`, `rating_hash`, `checked_hash`, `previous_record_hash`.
`old`/`proposed` sind die sechs Runtimefelder oder null. `status` ist `rated`,
`unrated`, `invalid_input` oder `technical_error`; `reason` ist null beim Erfolg,
sonst eine nichtleere Erklärung bis 2048 Zeichen. Unbekannte Quell-/Ergebnisbindungen
sind ausdrücklich null. Kein Eintrag wird bei Fehler ausgelassen. `distribution`
hat exakt `old` und `proposed`, jeweils die Zählkeys `L1`…`L5`, `unrated`.
Sie ist rein beobachtend. `report.md` ist die deterministische lesbare Ableitung
desselben JSON-Objekts, einschließlich aller offenen Fälle und Bindungen.

Die Vorschau und geprüften Inputs werden im Arbeitsverzeichnis erzeugt.
Erst die getrennte Übernahme schreibt aktive Dateien und beide Dauerberichte.
Vorher Ausgangsbytes erneut vergleichen; unvollständige Versuche bleiben im
Bericht und ersetzen keine gültige Bewertung. Identische erneute Übernahme ist
No-op. Alle ausgewählten Eingänge müssen unverändert sein; ein fremder Zwischenstand
stoppt vor Mutation. Der gesamte Katalog wird dabei nicht neu analysiert.

## Journale und Recovery

Gemeinsamer exklusiver Lock bleibt `content/.registration-pending.json`.
Neue Formate: `picross-registration-journal-v3`,
`picross-content-update-journal-v2`, `picross-difficulty-adoption-journal-v1`.
Sie haben exakt `format`, `operation`, `old`, `new`, `retained`, `additions`,
`report_run`. Operation ist `registration`, `update`, `adoption` oder `sync`;
die letzten beiden verwenden das Adoptionsjournal. `report_run` ist null außer
bei Übernahme eines Auswahlberichts, dann die sichere Run-ID.

`old`/`new` ordnen denselben vollständig abgeleiteten Textpfaden exakte UTF-8-Bytes
als String oder ursprüngliche Abwesenheit als null zu: Registry, Kategorien,
Runtime, alle betroffenen Definitionen und Sidecars, bei Update die Notice,
bei Registrierung die neue Notice sowie bei Adoption beide Berichtsdateien.
Unveränderte Sidecars/Definitionen der Projektionsquelle werden mitgebunden.
`retained` bindet die unverändert gelesenen Manifeste, Reveals und Notices per
SHA-256. `additions` bindet neue Paketdateien und gegebenenfalls das neue Reveal
per SHA-256. Ihre Zielpfade werden strikt aus dem Registrydelta abgeleitet;
keine beliebigen Lösch-/Schreibziele aus einem Journal akzeptieren.

Vor Journalanlage werden vollständiger Zielcheckout und gelesene Quellen geprüft.
Neue Pakete behalten den vollständigen bestehenden ZA-1-Prüfweg einschließlich
Stagingprüfung. Vor und während Publikation Ausgangsbindungen vergleichen;
Runtime zuletzt. Der Lock bleibt bis zur erfolgreichen Abschlussprüfung bestehen.
Ein gewöhnlicher Fehler versucht kontrollierten Rollback; Fremdänderungen stoppen
mit erhaltenen Dateien und Journal. Prozessabbruch wird ausdrücklich wiederaufgenommen.

Recovery validiert zuerst beide Projektionen, Delta, alle aktuellen alten/neuen
Bytes, unveränderte Bindungen und den vollständigen alten Zielcheckout ohne Replay.
Sie stellt ausschließlich eigene erwartete Dateien zurück, entfernt ausschließlich
eigene erwartete Neuanlagen und publiziert die gültige aktuelle Altprojektion
zuletzt. Derselbe eigene Zwischenzustand bleibt wiederaufnehmbar. Kein nachträglich
notwendiges Sync. Rücknahme einer abgeschlossenen Übernahme ist eine neue beauftragte
Änderung, kein Missbrauch eines abgeschlossenen Journals; Git erhält die Historie.

Exakte KE-Altjournale (Registrierung v2, Update v1) bleiben unter ihrem Schema
lesbar, Registrierung v1 bleibt gesperrt. Vor Alt-Recovery müssen alle Sidecars
der alten/neuen beteiligten Registry fehlen; neue ungebundene Bewertungen blockieren
vor Mutation. Historische Journale werden nicht um neue Felder ergänzt.

## Technische Abnahme

Synthetische Prüfungen decken SD-C-A01–A04/A08–A10 sowie den technischen Anteil
A07 ab. Keine echte Kataloganalyse, keine aktiven Bestands-Sidecars. Methodenquellen,
Referenzen und Grenzen bleiben bytegleich. SD-C-T01 umfasst vollständige aktuelle
CI, einschließlich Product/Preflight/Web, und getrennten Selbstreview. SD-C-R01
für C1 bleibt ein separates qualifiziertes Review vor Merge. A05/A06, realer
A07-Anteil und SD-C-K01 gehören zu C2; #238 und #235 bleiben offen.

| Akzeptanz | Fester technischer Nachweis |
| --- | --- |
| A01/A02 | `test_catalog_integration.py`: Quellenpriorität, verschachtelte Typ-/Hash-/Statusangriffe, Kandidatenremapping, Rebind, volle Bundleprüfung und reproduzierbare Ratingidentität. |
| A03/A09 | `catalog_difficulty.py`, Godot `ke_cases.gd`: exakte sechs Difficultyfelder, fünf Stufen, null, Altmethoden/v2; `kat2_probe.gd` rendert die fünf 0.3-Stufen und gezielte Tooltips einschließlich R4 bei UI100/125. |
| A04 | `test_ke_recovery.py`: feste Altbytes und ungebundene Sidecars; `test_content_update.py`, `test_categories_adapter.py`, `test_catalog_integration.py`: Register/Update/Sync/Adoption, Abbruch/Resume, Quellenrennen und fremde Bytes. |
| A07 technisch/A08 | Neue synthetische Integration mit externem Rating, Pflicht bei neuer Logik, fehlender Input blockiert vor Mutation, Erhalt versiegelter Pakete/Saves, No-op und `retire-production` mit aktiver Bewertung. |
| A10 | `tools/test_ci_scope.py`: exakte Inhaltspfade, Modi, Löschung/Rename und breiter C1-Scope; der bestehende feste synthetische Harness wächst nicht mit dem Katalog. |
| A05/A06 technisch | Vollständige Auswahlberichte und beobachtende Verteilung an künstlichen Eingängen, unveränderter Methodenhash; keine reale A05/A06-Abnahme. |

Die Basisprüfung ergab `origin/main == b625cc6af1342eafb2582beb9eec17991ea21a12`;
keine Abweichung seit SD-C-P01. Finale Head-/Test-Merge-/Runbindungen und der
getrennte Selbstreview werden im C1-Draft-PR dokumentiert. SD-C-R01 wird dadurch
nicht ersetzt; keine Wiedereröffnung historischer KE-/KAT-Gates, kein Mergeauftrag.
