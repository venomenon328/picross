# SD-C1: Bewertungsquelle, Import und Transaktionen

**AT · Abschlussbildtransparenz, Umsetzungsvorbereitung V3 vom 19.10.2026; AT-A in Umsetzung:**
[AT-A](REVEAL_TRANSPARENCY.md) ergänzt den gemeinsamen Quellen-/Transaktionsweg
für getrennte aktive Bildfassungen und einen abgesicherten Binärersatz. Ratings,
Bewertungsrevisionen, Hinzugefügt-Daten und historische Produktionsbindungen
bleiben bei reinen Bildupdates unverändert. AT-B verwendet den Weg erst nach
Integration von AT-A und gesondertem Auftrag für den gebundenen Bestand.
Diese Lieferung führt keine reale Bild-/Bewertungsübernahme oder neue Analyse aus.

**KU / #244, freigegebene Ergänzung vom 18.10.2026; Umsetzung offen:**
[Katalogdarstellung](CATALOG_PRESENTATION.md) ersetzt mit KU-A ausschließlich
sichtbare Schwierigkeitsziffern durch gefüllte Kreise und entfernt die bisherigen
Schwierigkeitstooltips. Das löst die entsprechenden unten beschriebenen
KE-/SD-C1-Anzeigepflichten ab, ohne Ratings, Aussagegrenzen oder die sechs
Difficultyfelder zu ändern. KU-B ergänzt nach
[Katalogsortierung](CATALOG_SORTING.md) eigene Hinzugefügt-Metadaten und eine
gemeinsame kompatible Projektion/Recovery; die exakt dokumentierten v2/v3-
Runtimeformate dürfen dafür nicht still umgedeutet werden. Keine neue
Schwierigkeitsanalyse, Kalibrierung oder Bewertungsübernahme durch KU.

Stand: 18.10.2026 · Vertrag 1.1 · SD-C-P01 und SD-C-R01/C1-N01 aus
[#238](https://github.com/venomenon328/picross/issues/238).
Die folgenden Formate wurden vor der ersten Codeänderung festgelegt und werden
von den neuen `catalog_*`-Modulen implementiert. [Befehlsanleitung](../tools/puzzle_production/README.md).
SD-C1 ist nach qualifiziertem R2 mit PR #242 integriert. SD-C2 hat nach bestandenem
Vor-Übernahme-Review gemäß SD-C2-F01 die 26 Bewertungen kontrolliert übernommen;
separates qualifiziertes finales Datenreview und Merge bleiben offen.
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
können ausdrücklich gewählte Teilmengen verwenden; auch dann muss die gesamte
mitgebundene Projektionsquelle in das Journal passen. Vollständige Bundles
liegen ausschließlich im ausdrücklich angegebenen Arbeitsverzeichnis außerhalb
von `game/` und `content/difficulty/`.

## Aktive Hülle

`content/difficulty/<pz-ID>/rating.json` hat Format
`picross-catalog-difficulty-v2` und exakt diese Felder:

| Feld | Vollständiger Untervertrag |
| --- | --- |
| `format` | Obige konstante Kennung. |
| `rating_revision` | Ganzzahl 1…1000000; nur tatsächliche Übernahme/Neubindung erhöht sie. |
| `current_source` | Exakt `id`, `runtime_revision` (1…1000000), `definition_sha256`; tatsächliche aktuelle Definitionsbytes. |
| `logic_binding` | Exakt `analysis_hash`, `matrix_hash`; ersterer nach SD-A, letzterer kanonischer Hash der numerischen Schema-2-Zielmatrix. |
| `production_mode` | Exakt `mono` oder `color`, separat zur normalisierten Runtime-Logik; muss zur registrierten Produktionsart passen. Mono benötigt genau eine Vordergrundfarbe. |
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

`picross-checked-difficulty-v2` hat exakt `format`, `production_mode`, `current_source`,
`logic_binding`, `rating`, `compact_analysis`, `analysis_report_hash`,
`verification_hash`, `tool`, `checked_hash`. Gemeinsame Felder folgen oben;
`checked_hash` bindet das Objekt ohne dieses Feld. Auch ein vollständig geprüftes
`unrated`-Ergebnis ist als Arbeitsinput erlaubt, niemals als aktive Bewertung.
Die beiden Beleg-Hashes stammen aus dem tatsächlich gelesenen SD-A-Bericht
**ohne dessen `operation`** und dem Ergebnis der vollständigen
`check_bundle(..., method=...)`-Prüfung. So gehen Ausführungszeiten und verbrauchte
Budgets weder in `checked_hash` noch indirekt in die reproduzierbare
Auswahlberichtidentität ein. Der volle operative Bericht bleibt im Arbeitsbundle.

`analyze` verlangt ausdrücklich `--production-mode mono|color` aus dem geprüften
Design beziehungsweise Produktionskontext; die Auswahlvorschau verwendet die
geprüfte Registry. Schema 2 enthält diesen Modus nicht. Der Wrapper schreibt im
neuen Bundle zusätzlich `catalog-context.json`: exakt `format` mit
`picross-difficulty-context-v1`, `production_mode`, `source` (derselbe Vertrag wie
`current_source`) und `context_hash` (kanonischer Hash ohne dieses Feld).
`import` prüft das vollständige Bundle und diese gebundene Kontextdatei. Er bietet
keine nachträgliche Moduszuweisung. `rebind` verlangt den expliziten Zielmodus;
Register/Update beziehen ihn aus dem frisch geprüften Export. Alter und neuer
Modus müssen übereinstimmen, auch bei Mono↔Einfarb-Color mit identischen Hinweisen.
`checked_from_active` erhält die Modusbindung. Ein Wechsel benötigt neue Analyse;
SD-B-Rating, dessen `source.production_mode=unknown` und Methodenfreeze bleiben gleich.

Die bisherigen aktiven/geprüften v1-Hüllen bleiben mit exakt ihren alten Feldern
lesbar, projizierbar und in alten Journalen wiederherstellbar. Sie enthalten keine
nachgewiesene Produktionsart. Bundles ohne Kontextdatei liefern weiterhin checked-v1;
eine Neubindung oder neue Integration darf daraus keinen Modus erfinden. Dafür ist
eine neue ausdrückliche Analyse erforderlich. Identische bereits registrierte
Legacy-Wiederholungen bleiben No-op. Es gibt keine automatische Bestandsmigration.

Der vorbereitende Adapter nimmt ausdrücklich Kandidatenmatrix, validiertes Design
und normalisierte Logik entgegen. Er verwendet `target_adapter.definition` mit
derselben Leer-/Farbabbildung und erzeugt eine Schema-2-Datei mit vorläufigem
Revealnamen/-pfad. Dieser Eingang ist keine Exportfreigabe. Die Matrix wird gegen
die Hinweise geprüft; tatsächliche Deduktions-/Herkunfts-/Endfreigaben bleiben im
normalen Produktionsweg Pflicht. Ein späterer Export darf den geprüften Input
nur bei identischer ID, Produktionsmodus, Analysehash und Zielmatrix neu binden. Registrierung
verlangt dafür ausdrücklich den geprüften Input; keine heimliche Analyse.

## Quellenpriorität und Projektion

Fehlende aktive Datei erhält die unveränderte historische 0.1-/0.2-Projektion
beziehungsweise null. Eine vorhandene ungültige, veraltete oder unvollständige
Datei stoppt ausdrücklich; kein Fallback. Definitionsbytes, ID/Revision,
Analyse-/Matrixhash, Methode, Rating und kompakte Angaben müssen zusammenpassen.
Andere Registryeinträge, Git-HEAD und Produktionscleanup entwerten kein Rating.

Die gemeinsame Quellenprüfung inventarisiert den gesamten aktiven Namensraum:
unregistrierte IDs, falsche Unterordner, zusätzliche/aliasartige Ratingdateien,
Symlinks und Reparsepunkte sind Fehler vor Mutation. Nur exakt registrierte
`<pz-ID>/rating.json` sind aktiv. `reports/<run-id>/report.json|report.md` ist
ein gesonderter zulässiger Namensraum; Berichte sind keine Ersatz-Sidecars.
Leere kanonische Verzeichnisse dürfen nach Rollback verbleiben. Diese Prüfung
gilt auch in Transaktionsguards und vor neuer wie alter Recovery; fremde Dateien
werden weder ignoriert noch bereinigt. Ein wirklich fehlendes Sidecar bleibt zulässig.

Die Runtime bleibt v3 mit exakt sechs Difficultyfeldern. 0.3 verwendet L1…L5,
`instrumented`, `medium`, das geprüfte R4-Flag und `[Lx,Lx]` als Punktprojektion.
Die bisherige KE-/SD-C1-Anzeige erläutert diese Angaben im Tooltip; die freigegebene
KU-A-Darstellung entfernt diesen Tooltip. Modellschätzung, mittlere Aussagekraft
und fehlende menschliche Kalibrierung bleiben fachlich unverändert. Diese Spanne
ist kein menschliches Unsicherheitsintervall. Runtime-v2
behält exakt sieben Eintragsfelder; 0.1/0.2 bleiben unverändert lesbar.

Neue Registrierung und logikrelevante Definitionsänderung verlangen 0.3.
Identische Legacywiederholungen bleiben No-op. Reine Metadatenänderung erlaubt
ausdrücklichen Rebind ohne Analyse nur bei gleicher ID/Modus/Logik/Matrix. Gleiche
Ratingidentität und aktuelle Bindung ändern weder Bytes noch Bewertungsrevision;
operative Zeiten oder neue Berichte erzeugen allein keine Änderung.

## Auswahlbericht und getrennte Übernahme

Explizite Einzel-ID, wiederholte ID-Auswahl oder `--all` sind gegenseitig exklusiv;
kein Auswahl-Default. Der Werkzeugweg kann analysieren oder bereits vorhandene
Bundles vollständig prüfen/importieren. Ein nicht gelöster Linienlauf verwendet
R4 nur mit ausdrücklich übergebenen passenden Baseline-/Paarproofs. Ohne diese
bleibt er `unrated`; kein automatischer Paarlauf.

`content/difficulty/reports/<run-id>/report.json` verwendet
`picross-catalog-difficulty-report-v2`: exakt `format`, `run_id`, `result`,
`result_hash`, `operation`. `result` hat exakt `selection` (`ids` oder `all`),
`source_commit`, `method_hash`, `snapshot`, `sources`, `entries`, `distribution`.
`snapshot` bindet exakt Dateihashes von Inhaltsregistry, Kategorien und Runtime.
`sources` bindet alle übrigen gelesenen Definitions-, Sidecar-, Notice-, Manifest-
und Revealpfade an ihre Dateihashes, ursprüngliche Sidecar-Abwesenheit an null.
Höchstens 70003 Einträge; die exakte Pfadmenge wird aus dem geprüften Checkout
abgeleitet. Es werden keine frei im Bericht angegebenen Pfade geöffnet.
`operation` enthält exakt `created_utc` (UTC-ISO-Zeit) und `phase`
(`preview` oder `adopted`); diese Ausführungsdaten sind nicht Teil von `result_hash`.

Jeder Eintrag hat exakt `id`, `current_source`, `logic_binding`, `old`, `proposed`,
`status`, `reason`, `rating_hash`, `checked_hash`, `previous_record_hash`,
`previous_rating_revision` (positive ursprüngliche Bewertungsrevision oder null
genau bei fehlendem Vorgängerrating; nur Report-v2).
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

Vor einem positiven Wiederholungs-No-op müssen Registry/Kategorien und sämtliche
gebundenen Quellen dem Ausgangsstand oder dem exakt zu diesem Bericht gehörigen
Übernahmezustand entsprechen. Die ursprüngliche Runtimeprojektion wird nur im
Speicher mit den ausgewählten Altwerten rekonstruiert und gegen ihren Hash geprüft;
die absichtlich neue Projektion ist kein Stale-Fehler. Geänderte aktive Sidecars
benötigen die identische checked-Bindung sowie Berichts-/Vorgängerbindung dieser
Übernahme, die erwartete nächste Revision und kanonische Dateibytes.
Fremde Änderungen, auch bei gleicher sichtbarer Stufe, stoppen Plan und
Übernahme ohne Mutation, Journal oder neue Revision. Ein neuer Bericht ist nötig.
Report-v1 bleibt unter dem exakten alten Schema übernehmbar, wiederholbar und in
Journalen wiederherstellbar. Auch sein No-op prüft Registry, Kategorien, rekonstruierte
Altprojektion und ausgewählte Bindungen; die erst in v2 vorhandenen vollständigen
Quellenhashes und Vorgängerrevisionen werden für v1 nicht nachträglich behauptet.

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

Synthetische C1-Prüfungen decken SD-C-A01–A04/A08–A10 sowie den technischen Anteil
A07 ab. C1 enthielt keine echte Kataloganalyse und keine aktiven Bestands-Sidecars.
Methodenquellen, Referenzen und Grenzen bleiben bytegleich. SD-C-T01/C1 und
qualifiziertes SD-C-R01/C1 R2 sind erfüllt: PR #242 ist als
`e93444e5db48e2138d15890e314c60ec4291fea3` integriert, finale C1-CI
[39071026774](https://github.com/venomenon328/picross/actions/runs/39071026774)
mit allen sechs damaligen Pflichtjobs erfolgreich. Die C2-Lieferung umfasst
Status-Markdown und die erlaubten Bewertungsdaten; gemäß vollständigem Diff/CI-Policy sind dafür
`docs` und `ci-required` erforderlich, keine C1-Vollwiederholung.
A05/A06 haben das qualifizierte Vor-Übernahme-Review bestanden. A07 real und
SD-C-K01 sind mit Übernahme/No-op technisch belegt; separates qualifiziertes finales
R01/C2-Datenreview bleibt offen. #238 und #235 bleiben offen.

| Akzeptanz | Fester technischer Nachweis |
| --- | --- |
| A01/A02 | `test_catalog_integration.py`: Quellenpriorität, verschachtelte Typ-/Hash-/Statusangriffe, Kandidatenremapping, Rebind, volle Bundleprüfung und reproduzierbare Ratingidentität. |
| A03/A09 | `catalog_difficulty.py`, Godot `ke_cases.gd`: exakte sechs Difficultyfelder, fünf Stufen, null, Altmethoden/v2; `kat2_probe.gd` rendert die fünf 0.3-Stufen und gezielte Tooltips einschließlich R4 bei UI100/125. |
| A04 | `test_ke_recovery.py`: feste Altbytes und ungebundene Sidecars; `test_content_update.py`, `test_categories_adapter.py`, `test_catalog_integration.py`: Register/Update/Sync/Adoption, Abbruch/Resume, Quellenrennen und fremde Bytes. |
| A07 technisch/A08 | Neue synthetische Integration mit externem Rating, Pflicht bei neuer Logik, fehlender Input blockiert vor Mutation, Erhalt versiegelter Pakete/Saves, No-op und `retire-production` mit aktiver Bewertung. |
| A10 | `tools/test_ci_scope.py`: exakte Inhaltspfade, Modi, Löschung/Rename und breiter C1-Scope; der bestehende feste synthetische Harness wächst nicht mit dem Katalog. |
| A05/A06 technisch | Vollständige Auswahlberichte und beobachtende Verteilung an künstlichen Eingängen, unveränderter Methodenhash; keine reale A05/A06-Abnahme. |

`test_catalog_review.py` ergänzt die vor dem Fix reproduzierten R1-01–03:
Mono↔Einfarb-Color, alte/geprüfte/aktive Rebindinputs und frische Analyse;
verwaiste/falsch platzierte Sidecars einschließlich Recovery; echter No-op sowie
Stale-Kategorie-/Quellenänderung bei Plan und Übernahme. Alle Eingänge sind synthetisch.

Die historische C1-Basis war `b625cc6af1342eafb2582beb9eec17991ea21a12`.
Finale Head-/Test-Merge-/Runbindungen und der getrennte Selbstreview stehen in
[PR #242](https://github.com/venomenon328/picross/pull/242), qualifiziertes
[R2](https://github.com/venomenon328/picross/pull/242#pullrequestreview-5560294023)
bestätigt den C1-Abschluss. Keine Wiedereröffnung historischer KE-/KAT-Gates.

## SD-C2 · Erstbericht vor Übernahme

Am 18.10.2026 wurde gemäß #238/SD-C2-P01 einmalig `preview --all` mit Run-ID
`sd-c2-first-20261018-a` ausgeführt. Quell- und Werkzeugcommit sind beide
`e93444e5db48e2138d15890e314c60ec4291fea3`; nach Fetch keine Änderung seit P01.
Alle 835 versionierten Dateien entsprachen vor dem Lauf ihren Git-Blobbytes.
Methodenhash `8f7efa0d5ac76a1bd73fbae3618fec18dba28cf704887188eba2fcf020b9df79`
und sämtliche Freezequellen/-referenzen sind unverändert.

Alle 26 registrierten IDs haben `rated`, vollständige geprüfte Linienableitung
und `confidence=medium`. Alt: 19 × L2, 7 × L3; Vorschlag: L1=0, L2=0,
L3=17, L4=8, L5=1, offen=0. Sechs L4 beruhen unmittelbar auf R2/Enge;
zwei auf logischer Basis 3 plus zulässigem Größenbeitrag 1. L5 beruht auf R3
mit starker Enge, ohne R4. Kein Paar-/Suchlauf war erforderlich. Verteilung
nur beobachtet; keine menschliche Kalibrierung oder Lösungszeitbehauptung.

`plan-adoption` endete lesend als `planned-adoption`, `open_ids=[]`,
`report_hash=51c785039579474658362c127112c70dea9079e5aeace473f646a6622f1fe37e`.
Geplant sind 26 Sidecars, zwei Dauerberichte und `game/data/registry.json`.
Nach Vorschau und Plan waren sämtliche versionierten Bytes unverändert;
kein aktives Rating, Dauerbericht oder Journal wurde angelegt, keine Saves berührt.

Die unveränderten JSON-/Markdownberichte, Einzelbelege, Plausibilitätsauswertung,
Dateihashes und der konkrete Plan stehen im zugehörigen Draft-PR; der Belegindex
ist über [#238](https://github.com/venomenon328/picross/issues/238) erreichbar.
Vollständige Bundles/checked-Dateien bleiben bis zur Fortsetzung
unter `E:/Zeuch/Coding/picross-sdc2-evidence/sd-c2-first-20261018-a` erhalten,
außerhalb des Repositorys und gewöhnlicher CI-Artefakte. Previewberichte dürfen
nicht vorab in die kanonischen Dauerpfade kopiert werden.

Der beschriebene Erstbericht blieb bis zum separaten qualifizierten
[Vor-Übernahme-Review SD-C-R01/C2 R1](https://github.com/venomenon328/picross/pull/243#pullrequestreview-5560549886)
unverändert. Dieses Gate ist für Head `8ed57c6499a03d8cef05267ae6a6b93d4f27e185`
bestanden; der Folgeauftrag SD-C2-F01 autorisiert die anschließende Übernahme.

## SD-C2-F01 · Kontrollierte Übernahme, finales Datenreview offen

Am 18.10.2026 wurden auf `chore/238-bestandsbewertung` / Draft-PR #243
der bestehende Bericht und die 26 unveränderten checked-v2-Dateien verwendet.
Starthead war `8ed57c6499a03d8cef05267ae6a6b93d4f27e185`, aktuelle Basis weiterhin
`e93444e5db48e2138d15890e314c60ec4291fea3`. Vor Mutation wurden alle 835
versionierten Dateien gegen Git-Blobbytes, sämtliche 210 Originalarbeitsdateien
gegen Manifest und Sicherungs-ZIP sowie die veröffentlichten Report-/checked-Bytes
gegen die lokalen Originale geprüft. Alle 130 Quellenbindungen, die drei
Snapshotbindungen und der SD-B-Freeze passen weiterhin; keine erneute Gesamtanalyse.

`plan-adoption` bestätigte lesend exakt den ursprünglichen Plan: 29 Pfade,
`open_ids=[]`, unveränderter `report_hash`. Anschließend schrieb allein
`catalog_analysis adopt` die 26 kanonischen aktiven v2-Sidecars mit
`rating_revision=1`, die beiden Dauerberichte als `phase=adopted` und
`game/data/registry.json`. Der [dauerhafte JSON-Bericht](../content/difficulty/reports/sd-c2-first-20261018-a/report.json)
und seine [lesbare Ableitung](../content/difficulty/reports/sd-c2-first-20261018-a/report.md)
behalten dieselbe Ergebnisidentität; nur die operative Phase wechselt.

Der vollständige Dateivergleich unmittelbar nach Übernahme belegt genau diese
29 Datenpfade: 28 Neuanlagen und eine Änderung. Alle übrigen 834 vorhandenen
versionierten Dateien waren bytegleich zum Starthead. In der Runtime änderten
sich ausschließlich die sechs Difficultyfelder je ID; Kategorien, IDs, Keys,
Slots, Reihenfolge und übrige Eintragsfelder sind identisch. Definitionen samt
Runtime-Revisionen, Hinweise, Assets, historische `production.difficulty` und
kompakte Integrationsmanifeste bleiben bytegleich. Die anschließende
Statusdokumentation ist davon getrennt im PR-Diff erkennbar; Saves wurden nicht benutzt.

Der **identische zweite `adopt`-Aufruf** endete mit Exit 0 als `no-op`,
`changes=[]` und demselben `report_hash`. Vollständiges Dateiinventar,
SHA-256/Bytezahlen und Dateiänderungszeiten waren vor/nach diesem Aufruf identisch;
sämtliche Bewertungsrevisionen bleiben 1. Alle 210 Originalarbeitsdateien bleiben
unverändert. Kein Journal vor dem Lauf oder nach beiden abgeschlossenen Aufrufen;
kein Recoveryaufruf nötig. Die vorhandene Transaktion prüft alten/neuen Zustand,
publiziert Runtime zuletzt und entfernt den Lock erst nach Abschlussprüfung.
Keine Fehlerinjektion am echten Bestand: die synthetischen C1-Recoverybelege bleiben
unverändert maßgeblich, bei Abbruch gilt weiterhin der obige Recoveryvertrag.

Aktiv sind 17 × L3, 8 × L4 und 1 × L5, alle `instrumented/medium`, keine offene ID.
A07 real/SD-C-K01 sind damit technisch belegt. Ausführungs-/Hashbelege, Endhead,
Basis, tatsächlicher Test-Merge, ausgewählte CI und getrennter Selbstreview stehen
in [PR #243](https://github.com/venomenon328/picross/pull/243).
**Endgrenze:** separates qualifiziertes finales SD-C-R01/C2-Datenreview am
tatsächlichen Endhead vor Merge. Der Selbstreview ersetzt dieses Gate nicht.
Die bedingte Eigentümer-Mergefreigabe ist in #238 dokumentiert; dieser
Implementierungsauftrag stoppt vor dem finalen Review und führt keinen Merge aus.
#238/#235 bleiben offen; keine neuen Katalogtests oder CI-Änderungen.

## KU-B · Gemeinsame Journale mit Hinzugefügt-Quellen

Neue Journale heißen `picross-registration-journal-v4`,
`picross-content-update-journal-v3` und `picross-catalog-metadata-journal-v1`.
Letzteres trägt `adoption`, `sync` oder `added-adoption`; die ersten beiden
behalten `registration` beziehungsweise `update`. Exakte Felder bleiben
`format,operation,old,new,retained,additions,report_run`, maximal 24 MiB.
`report_run` bezeichnet bei `added-adoption` den Added-Bericht, bei
Schwierigkeitsadoption den bisherigen SD-Bericht; sonst null.

Der gemeinsame Lock bleibt `content/.registration-pending.json`. `old/new`
enthalten zusätzlich jede abgeleitete ID-Added-Datei (Text oder null); vorhandene
Herkunftsberichte sind vollständig hashgebundene behaltene Quellen. Ein neuer
Added-Bericht ist explizites Textziel nur seiner Adoption. Vollständige
Namespacevalidierung, Quellensnapshot, Guard vor jedem Schreiben, fremde Bytes
bewahren und Runtime als letzter Veröffentlichungs-/Recovery-Schritt bleiben
Pflicht. Beide Zustände werden vor Mutation vollständig isoliert geprüft.

Delta: Registrierung darf genau den neuen ID-Record ergänzen; Update, Sync und
Schwierigkeitsadoption dürfen keinen Added-Record ändern. `added-adoption` darf
nur die im vollständig gebundenen Plan benannten Added-Records, seinen neuen
Bericht und Runtime ändern. Keine Definitionen/Ratings/Produktionsbindungen.
Kein Journal und kein Rewrite bei byteidentischer Wiederholung.

Bisherige registration-v3/update-v2/difficulty-adoption-v1-Journale werden mit
ihrem ursprünglichen Zielumfang und ihrer v3-Projektion validiert; unbelegte
Added-Quellen verhindern Recovery. Frühere registration-v2/update-v1 bleiben
auf genau einheitliche v2- oder v3-Projektionen begrenzt; registration-v1 bleibt
gesperrt. Die endgültige sichere Rückführung projiziert unmittelbar die aktuelle
v4 mit unbekannten Daten, ohne anschließenden Sync. Ihr eigener abgeleiteter
v4-Zwischenstand wird bei erneut unterbrochener Recovery akzeptiert, fremde
Runtimebytes nicht. Historische Journale erhalten keine nachträglich erfundenen
Metadaten oder Uhrzeiten.

## AT · Gemeinsame Quellenprüfung und Binärersatz

Der freigegebene [AT-A-Sollvertrag](REVEAL_TRANSPARENCY.md) ergänzt denselben
exklusiven Lock und dieselbe gemeinsame Quellenprüfung um die aktive Bildbindung.
Register, Rasterupdate, Sync, Bewertungs-/Hinzugefügt-Übernahme, Cleanup und
Recovery müssen sie gleichermaßen prüfen und erhalten. Bildänderungen dürfen
keine aktive Bewertung neu binden oder deren Revision erhöhen; Definitionsbytes,
Logik/Matrix, Modus, Slots und Added-Records bleiben unverändert.

Ein vorhandenes Reveal ist im bisherigen Journal eine unveränderte binäre
`retained`-Quelle; `old/new` enthalten UTF-8-Text, `additions` nur Neuanlagen.
AT-A darf einen PNG-Ersatz daher nicht in diese alten Bedeutungen einschmuggeln.
P01 schließt nachfolgend die exakten Feld-/Format-/Ressourcenverträge vor der
Codeänderung. Datenbindung und Auflösung stehen in [ZA-1](ZA1_ADAPTER.md) und
[Projektion](CATEGORIES.md). [AT-A-T01](AT_A_VERIFICATION.md) führt Umsetzung und
Prüfung dieser Formate. Keine zweite unabhängige Schreibstrecke oder Delete+Add
am Bildpfad.

Plan und Übernahme prüfen Alt-/Zielzustand samt tatsächlichen Bildbytes,
Bildfreigaben, Quellen und unveränderten historischen Belegen vor Mutation.
Fremde Änderungen und veraltete Erwartungen stoppen mit erhaltenen Dateien;
dies gilt auch vor einem beanspruchten Wiederholungs-No-op. Nur der exakt
gebundene bereits erreichte eigene Zielzustand darf als identische Wiederholung
ohne Rewrite, Journal, Zeitstempeländerung oder neue Bildrevision bestätigt
werden. Neue Quellen oder andere Bildbytes verlangen eine neue gebundene Planung.

Recovery prüft vollständig, bevor sie eigene alte Bild-/Metadatenbytes
wiederherstellt oder eigene Neuanlagen entfernt. Fremde Bytes und das Journal
bleiben bei Konflikten erhalten; derselbe eigene Zwischenstand bleibt nach
erneutem Abbruch wiederaufnehmbar. Erfolgreiche Recovery hinterlässt unmittelbar
einen vollständig gültigen aktuellen Checkout, ohne nachträgliches Pflicht-Sync.
Die Runtime wird bei einer notwendigen Projektionsänderung zuletzt publiziert.

Die bisher unterstützten Journalaltformate behalten ihre exakten alten Felder
und Quellbindungen; bereits gesperrte Formate bleiben gesperrt. Eine neue
ungebundene aktive Bildquelle darf nicht durch Alt-Recovery ignoriert oder
überschrieben werden. Kompatible Übergänge und
gegebenenfalls konkrete Blockaden sind vorab abzugrenzen und mit synthetischen
Altfällen zu prüfen; keine Umschreibung alter Journale oder Freigaben. Der
Versionierungsbedarf einer Runtimeprojektion folgt allein ihrer tatsächlichen
Schemaänderung, nicht der neuen Bildrevision. Die allgemeinen Regressionen
verwenden ausschließlich feste synthetische Bilder, Rätsel und Speicherstände.

### AT-P01-D05 · Generationen und vollständige Mengen

Gemeinsamer exklusiver Lock ist weiterhin `content/.registration-pending.json`.
Alle gemeinsamen Einstiegspunkte prüfen außerdem Journalstagingreste unter
`content/.registration-journal-*.tmp`: keine aktive Operation am Rest vorbei.
Der gemeinsame Recoveryeinstieg behandelt ohne Lock ausschließlich einen
vollständigen, strikt validierten Stagingrest mit unverändert gültigem Altcheckout
als bereinigbar; Teilreste/mehrdeutige oder fremde Stände bewahrt er mit Exit 2.
Alle neuen Journale haben exakt
`format,operation,old,new,retained,additions,report_run,replacements`.
Die sieben bisherigen Felder behalten ihre Bedeutung; `old/new` sind Maps aus
repositoryrelativen Textpfaden auf vollständige UTF-8-Strings/null. Null bedeutet
ausschließlich abwesende Datei, kein Löschauftrag für fremde Bytes.
`retained/additions` sind Maps aus hergeleiteten Pfaden auf Dateihashes.

| Format | Einzig erlaubte Operation(en) | `report_run` | Binärersatz |
| --- | --- | --- | --- |
| `picross-registration-journal-v5` | `registration` | null | `{}` |
| `picross-content-update-journal-v4` | `update` | null | `{}` |
| `picross-catalog-metadata-journal-v2` | `adoption,sync,added-adoption` | SD-/Added-Run-ID bei Adoption; sonst null | `{}` |
| `picross-reveal-adoption-journal-v1` | `reveal-adoption` | null | Genau die geänderten ausgewählten vorhandenen Revealpfade |

Für Registry R sei `T(R)` exakt Registry, Kategorien, Runtime und für **jede**
registrierte ID deren Definition, Live-Notice, Ratingpfad, Addedpfad und
`content/reveals/<id>.json`. Fehlende zulässige Sidecars werden null gebunden.
`old/new` besitzen exakt dieselbe Schlüsselmenge `T(Ralt) ∪ T(Rneu) ∪ Q`.
Q ist ausschließlich das Paar neuer SD-Berichtdateien bei `adoption`, der neue
Added-Bericht bei `added-adoption`, sonst leer. Alle übrigen Definitionen,
Sidecars und Notices sind unveränderte Textquellen; keine Duplikate in `retained`.
Kategorien dürfen in diesen Operationen nicht geändert werden; Sync bindet ihren
aktuellen Stand. Sämtliche Mengen werden aus den validierten Registryeinträgen
und Berichtsverträgen hergeleitet, niemals frei aus dem Journal übernommen.

`K(Ralt)` ist exakt die Menge aller Live-Reveals, aller regulären Dateien der
aktuell gebundenen Produktionspakete (bei kompaktem Receipt nur `manifest.json`),
aller vorhandenen zulässigen SD-Dauerberichte und referenzierten Added-Berichte.
Paketdateien folgen dem sicheren vollständigen Paketbaum und seinem validierten
Inventar. Damit sind auch bei Exportprüfung gelesene Originale gebunden;
ungebundene/fremde Paketdateien blockieren. Neue Berichtziele stehen in Q mit
`old=null`, vorhandene Berichte bleiben behaltene Quellen.
`retained = K(Ralt) − keys(old) − keys(replacements)` exakt. Paketnotices sind
historische Quellen, Live-Notices Textquellen.
`additions` ist leer außer Registrierung/Update: exakt das vollständig geprüfte
neue Paketinventar unter dem hergeleiteten neuen Paketpfad, bei Registrierung
zusätzlich das neue Live-Bild. Keine Überschneidung mit Text/Retained/Replacement,
keine belegten/aliasierenden Neuanlageziele. Neue AT-Dateien sind Textziele.
Die Namespaceprüfung umfasst Alt-/Neuregistry und ausschließlich ihre im Journal
gebundenen Zwischenstände. Geprüfte leere kanonische Elternordner sind zulässig.

`replacements` ordnet dem hergeleiteten **vorhandenen** Live-Revealpfad exakt
`old,new` zu. Jede Seite hat exakt `sha256,bytes,base64`: `bytes` Ganzzahl
1…33554432, SHA-256 der vollständigen dekodierten Bytes, `base64` kanonisches
RFC-4648-Standardalphabet mit notwendigem Padding, ohne Whitespace/Zeilenumbruch.
Striktes Dekodieren und exaktes Rekodieren müssen denselben String ergeben.
Vor Dekodierung Länge `4*ceil(bytes/3)` und Maximum 44739244 prüfen.
Alt-/Neuhash sind verschieden und stimmen mit Vorgänger-/Zielrecord überein.
Format/Maße werden nach Dekodierung mit dem bestehenden Revealprüfer validiert.
Kein UTF-8-PNG und kein Delete+Add am belegten Bildpfad.

Jede Generation prüft die vollständigen [Operationsdeltas](CATEGORIES.md):
Registrierung genau eine ID; Update genau eine Produktion samt optionalem
AT-Rebind; SD-/Added-Adoption nur eigene Records/Berichte/Runtime; Sync nur Runtime;
Bildadoption nur ausgewählte Bilder/AT/Notice. Bei Bildadoption sind
`additions={}`, Registry/Kategorien/Runtime/Definition/Rating/Added bytegleich.
`replacements` enthält exakt das aus den geänderten Records hergeleitete Bilddelta.
Unveränderte Texte werden gebunden, nie neu geschrieben. Neue Records müssen
exakt der Append-/Rebindregel aus dem alten gültigen Record beziehungsweise der
gültigen historischen Quelle entsprechen. Kein Löschen vorhandener AT-Records
und keine Legitimation beliebiger Hüllen durch bloßes Neuberechnen ihrer Hashes.

### Limits und gemeinsamer Dispatchreader

Alte und neue nichtbinäre Journale bleiben höchstens **24 MiB** inklusive LF.
Nur `picross-reveal-adoption-journal-v1` darf **128 MiB** inklusive LF haben.
Beide Binärseiten zusammen höchstens 96 MiB dekodiert, jede höchstens 32 MiB;
zusätzlich gilt das strengere tatsächliche 128-MiB-Limit nach Base64 und JSON.
Ein Paar mit je 32 MiB passt grundsätzlich; bei zu großer zusammenhängender
Mehrfachadoption vollständiger Abbruch vor Lock/Mutation, ausdrücklich neu teilen.
Kein automatisches Vorziehen einzelner IDs, Kürzen der Historie oder Anheben
historischer Limits.

Dispatch prüft zuerst Dateityp und Größe (maximal 128 MiB), dann höchstens 4096
Präfixbytes. Neue Journale haben ein kanonisches **Wirelayout mit `format` zuerst**,
danach alle übrigen Schlüssel lexikografisch, kompakt, UTF-8 plus LF; ihr
Dateihash bindet genau dieses Layout. Die normale Objektkanonisierung für
Record-/Planhashes bleibt unverändert. Nur die exakte Bildkennung im Präfix
erlaubt weiteres Lesen oberhalb 24 MiB. Alte Journale bis 24 MiB werden unter
ihrem originalen Vertrag ohne neuen Präfixzwang gelesen. Gesamtes JSON danach
begrenzt und mit Duplicate-/Typ-/Tiefenprüfung laden; gefälschter Präfix erlaubt
keine andere Kennung oder Fremdschlüssel. Base64-Längen und Summen vor deren
Dekodierung prüfen, Bilder einzeln begrenzt dekodieren/hashen; Zwischenpuffer
maximal 1 MiB. Kein gleichzeitiges unbegrenztes Dekodieren sämtlicher Bilder.
Neue AT-Texte maximal 1 MiB, SD-Berichte weiterhin 16 MiB; übrige Quelllimits
unverändert. JSON-Tiefe höchstens 32; keine Fremdpfade aus dem Journal öffnen.

### Alt-/Neu-Kompatibilitätsmatrix

Jede Zeile behält ihre ursprünglichen vollständigen Schlüssel-/Pfad-/Delta-/
Retainedregeln und Limits. `replacements` ist in Altformaten ein Fehler.
Vor Mutation zusätzlich alle heutigen sicheren Namespaces prüfen. „Keine AT“
heißt: keine ID-Datei und keine fremde Datei im ganzen neuen Namensraum;
leerer kanonischer Ordner erlaubt.

| Journal | Exakter historischer Umfang / Runtime-Snapshots | Zusätzliche Recoverybedingung |
| --- | --- | --- |
| Registrierung v1 | Weiter gesperrt | Journal/Dateien erhalten; alter Werkzeug-/Checkoutvertrag erforderlich. |
| Registrierung v2 | Exakt `format,targets,files,old,new,categories`; Indizes in `old/new`, vier hergeleitete Ziele, unveränderte Kategoriebytes; einheitlich Runtime-v2 oder v3 | Keine ungebundenen Rating-, Added- oder AT-Quellen. |
| Update v1 | Exakt `format,package,files,categories,old,new`; `old/new` genau Registry, Runtime, Definition, Notice der einen Update-ID; neue Paketdateien und behaltenes Bild/Altpaket; einheitlich v2 oder v3 | Keine ungebundenen Rating-, Added- oder AT-Quellen; feste Identität, höhere Runtime-Revision. |
| Registrierung v3 / Update v2 / Difficulty-Adoption v1 | Exakt sieben Felder, damaliges T ohne Added/AT und damaliges Retained, v3 | Keine ungebundenen Added-/AT-Quellen. |
| Registrierung v4 / Update v3 / Catalog-Metadata v1 | Exakt sieben Felder, T mit Added ohne AT, damaliges Retained, v4; v2/v3-Start nur ohne Added gemäß KU-B | Keine ungebundenen AT-Quellen. |
| Registrierung v5 / Update v4 / Catalog-Metadata v2 | Exakt acht Felder, obiges T/K, `replacements={}`, neues Ziel v4 | Alle AT-/SD-/Added-Quellen gebunden; kompatibler v2/v3-Start weiterhin nur nach bestehender Added-Regel. |
| Reveal-Adoption v1 | Exakt acht Felder, T/K plus Binärersatz; Alt-/Zielruntime bytegleich und bereits gültig v2/v3/v4 | Gesamter Alt-/Zielcheckout gültig; kein Projektionsupgrade durch Bildwechsel. |

Alt-Recovery rekonstruiert aus damaligen Quellen direkt eine gültige aktuelle
v4-Altprojektion mit unbekannten fehlenden Added-Werten, ohne erfundene Zeit.
Nur gebundene Alt-/Neuruntime und exakt diese eigene abgeleitete v4 sind zulässige
Zwischenstände. Bild-Recovery erhält die bereits gültige Runtime bytegleich.
Sync-Recovery darf die aus vollständig validierten Quellen hergeleitete aktuelle
v4 schreiben. Fremde Quellen sperren jede Generation vor Mutation und bleiben
mit Journal erhalten. Historische Reports werden niemals nachträglich erweitert.

### AT-P01-D06 · Phasen und temporäre Eigentümerschaft

`J` ist der Dateihash des vollständigen Journals. Tempziele sind deterministisch
hergeleitete Schwesterdateien `.registration-<J>-<n>.tmp`, n als dezimale
nullbasierte Nummer im lexikografisch geordneten gesamten Schreibzielinventar.
Keine frei wählbaren Temp-/Sicherungspfade. Exklusive Erstellung ohne Linkfolge,
auf demselben Dateisystem wie Ziel, sichere Eltern vor jedem Öffnen prüfen.
Vor Beginn müssen alle fehlen. Mit gültigem Journal sind nur vollständige
erwartete Schreibbytes oder deren exakter Präfix als eigener unterbrochener
Tempzustand erlaubt; andere Bytes/Links/Kollisionen blockieren mit Journal.
Tempdateien ohne prüfbares Journal werden nie allein aufgrund ihres Namens gelöscht.

| Phase | Aktion und Prüfung | Unterbrechung/Fehler und Recovery |
| --- | --- | --- |
| P0 | Plan/Eingänge, gesamte Quellenmenge/Namespaces und isolierte vollständige Alt-/Zielcheckouts prüfen. Exaktes No-op hier beenden; Journalgröße vorab berechnen. | Repositoryquellen unverändert. Ungültig/stale/Limit: kein Lock. |
| P1 | Vollständiges Journal exklusiv als `content/.registration-journal-<J>.tmp` schreiben, flush/fsync, zurücklesen; atomar **ohne Ersetzen** unter Locknamen publizieren (Hardlink/no-replace), Verzeichniseintrag sichern, Staginglink entfernen. Nie einen halben Lock direkt schreiben. | Vor Lock keine aktive Mutation. Verwaistes vollständiges Stagingjournal nur nach Prüfung seines gesamten Altcheckouts und fehlendem Lock bereinigen; Teiljournal/anderer Lock/fremde Bytes bewahren und konkret blockieren. |
| P2 | Dauerhafter Lock bytegleich; alle Ausgangsquellen und Abwesenheiten unter Lock erneut vergleichen. | Fremder Zustand: Lock behalten, keine aktive Mutation. Eigener gewöhnlicher Fehler darf kontrolliert zurückrollen. |
| P3 | Register/Update: vollständige Paketneuanlagen sicher publizieren, notwendige ZA-1-Staging-/Paketprüfung erhalten. Bildadoption: in Pfadreihenfolge neue Binärbytes in sichere Tempdatei, flush/fsync, Rücklesen/Hash, Guard, atomar auf vorhandenes eigenes Altbild ersetzen. | Altbytes bereits vollständig im Journal. Kein gelöschter Bildpfad. Eigene Bild-/Paket-/Tempzwischenstände recoverbar. |
| P4 | Nur geänderte Textziele in Pfadreihenfolge, Runtime ausgenommen; je Temp, flush/fsync, Rücklesen, Guard, atomar ersetzen oder neue Datei ohne Ersetzen publizieren. | Bild/Record dürfen unter Lock vorübergehend eigene unterschiedliche Phasen haben; reguläre Leser stoppen am Lock. |
| P5 | Runtime nur bei Änderung zuletzt schreiben. Vollständigen Zielcheckout prüfen; alle Ziele exakt neu, Retained gleich, Additions vollständig. Guards vor jedem Schreiben, vor/nach Endprüfung und vor Lockentfernung. | Auch bei schon gültigem Ziel bleibt vor Lockentfernung Recovery ein Rollback, keine automatische Fortsetzung. |
| P6 | Geprüfte eigene Temps entfernen, Verzeichniseinträge sichern; Lock erst nach vollständigem Erfolg entfernen und Entfernung sichern. | Danach abgeschlossene Adoption; Rücknahme braucht neuen Auftrag. Wiederholung desselben Plans ohne Journal. |
| R0 | Journalgröße/Schema/Delta/Namespaces und sämtliche Text-/Binär-/Addition-/Retained-/Tempbytes vor Mutation prüfen; vollständigen gültigen alten Zielcheckout isoliert konstruieren. | Nur eigene Alt-/Neu-/erlaubte Projektionen zulässig; vorhandene Bilder dürfen nicht fehlen. Fremd-/Ressourcenfehler: keine Recoverymutation, Journal bleibt. |
| R1 | Guards vor jedem Schritt; Binäraltbytes atomar zurück, geänderte Alttexte zurück, eigene neue Textziele nur bei altem null entfernen; nur hashgeprüfte eigene Paketdateien einzeln entfernen. Runtime als letzter Datenpfad nur bei nötiger Änderung zurück. | Erneuter Abbruch bleibt mit demselben Journal wiederholbar. Keine rekursive Löschung fremder Bäume. |
| R2 | Vollständigen alten Checkout, exakte Altziele und fehlende eigene Additions prüfen; eigene Temps entfernen, zuletzt Lock entfernen. | Unmittelbar gültiger Checkout, kein Pflicht-Sync. Leere kanonische Ordner dürfen bleiben. |

Guards prüfen auch Lockbytes und die erwartete aktuelle Phasenbelegung jedes
Ziels; nicht bloß beliebige Alt-/Neu-Kombinationen. Recovery darf alle vollständig
geprüften eigenen Kombinationen zurückführen. Binäraltbytes haben genau eine
Sicherungsautorität im Journal. Rückführung verwendet dieselben sicheren Temp-
und atomaren Schreibregeln; ihr eigener zulässiger Präfix bezieht sich auf die
Altbytes. Gleiche Bytes werden auch bei Recovery nicht neu geschrieben.

Datei- und Verzeichnisveröffentlichung werden mit den passenden dauerhaften
OS-Aufrufen abgesichert; fehlt benötigte Atomizität/Dauerhaftigkeit, vor aktiver
Mutation blockieren. Kein Versprechen gegen defekte Datenträger. Manuelle
Paralleländerungen sind unzulässig; erkannte Rennen bewahren fremde Bytes.
Gewöhnlicher Fehler nach P2 versucht denselben Recoveryweg; nach erfolgreicher
Rückführung Exit 2 und gültiger Altcheckout. Ressourcen-/Signalende Exit 4;
kontrollierter Rollback nur nach vollständiger Vorprüfung mit eigenem 300-s-Budget.
Harter Kill garantiert kein JSON-Ergebnis. Ist Rückführung nicht sicher möglich,
bleiben Journal und Dateien erhalten, `recovery_required=true`. Recovery selbst
hat 300 s; erneutes Ressourcenende/Fremdbytes halten den Lock. Kein Erfolg für
Teilpublikation oder gescheiterte Rückführung.
