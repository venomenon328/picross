# RI-ONE: befristete Revieworiginale für A01

Produkt: [Draft-PR #670](https://github.com/venomenon328/picross/pull/670),
Head `ff828466405af3278e447f7de27b61e6ab13a496`, Basis `62401382f58adc2e3d303b19c1ecb1f1dc8a5040`.
[Maßgebliche Paketentscheidung](https://github.com/venomenon328/picross/issues/660#umsetzungsvorbereitung-ri-one).
Empfänger: unabhängiger Reviewer RI-ONE-A01. Belegeigner: Implementierer von #670
(Codex im beauftragten Konto venomenon328). Reviewref `review/660-ri-one`, vom
Produkthead abgezweigt; **kein PR nach main**. Aufbewahrung bis A01, befristet bis
**23.11.2026** (höchstens sieben Tage). Danach im beauftragten Rückbau entfernen;
bei ausstehendem Review vor Fristablauf Zugang/Frist ausdrücklich neu entscheiden.
Keine automatische Löschung oder dauerhafte Verfügbarkeit behauptet.

- [T01 Ergebnis](T01/result.json), [Originalprotokoll](T01/tests.log),
  [kleiner Runner](T01/run.py): 21 aktuelle Fälle am Produkthead, schreibfreier
  No-op, Guards/Recovery, alle Integrationsaufrufer, Archivfallen, mehrphasiger Abschluss.
  Die Testquellen liegen im Produktdiff; keine zweite Testplattform.
- [T02 Migration](T02/migration.json), [Anwendung](T02/product-application.json),
  [unabhängiger Git-/Livevergleich](T02/git-live-comparison.json),
  [frische Wiederholung](T02/repeat.json): tatsächlicher 62er-Startbestand,
  aktive Nutzdaten und alle offenen Authoringdateien erhalten; alle Bytes/mtimes
  beim zweiten Lauf gleich. Der Importer ist ausschließlich hier befristet, kein
  installierter Legacyimporter. Nach A01 endet sein Zweck.
- [T03 Vergleich](T03/comparison.json), [Vorheroriginal](T03/before.json),
  [Nachheroriginal](T03/after.json): Mono und einfarbiges Color, gleiche Python-/Pillow-
  Umgebung und gleiche finale Definition/Reveal/Notice. Export, Plan, Schreiben,
  Abschluss und tatsächliche Dateizugriffe getrennt. Vorher ca. 21,92/22,27 s,
  nachher ca. 1,95/1,93 s. Keine allgemeine Laufzeitzusage. Ausgewählte tatsächliche
  Zielbytes und aktuelle Inputs liegen unter `T03/inputs`; keine Bildgalerie.
- [CI-Bindung](CI.json), [getrenntes Selbstreview](SELF_REVIEW.md),
  [retirierte Testmatrix](test-retirement-review.json).

Reproduktion in eigenen isolierten Verzeichnissen: Python 3.13.14/Pillow 12.3.0.
T01: `python T01/run.py <Produktcheckout> <neuer Ergebnisordner>`.
T02: Basis-`content`/`game` in eine eigene Kopie übernehmen;
`python T02/migrate-portable.py <Kopie> <neuer Bericht> <eigene Arbeitswurzel> <Produktcheckout>`.
Zweimal ausführen und Dateihashes/mtime vergleichen. Nicht auf Nutzerdaten anwenden.
T03: `python T03/baseline-portable.py <Basischeckout> <Arbeitswurzel>/baseline-v8`,
danach `python T03/after-portable.py <Produktcheckout> <Arbeitswurzel>`.
Die unveränderten Originalskripte dokumentieren die tatsächlich verwendeten Pfade;
portable Varianten ändern nur Arbeits-/Codewurzeln. Producer/Analyse liegen wie
im Messoriginal außerhalb der Uhr; die neue Integration verifiziert den Proof.

`MANIFEST.json` bindet die gelieferten Dateibytes. Der Produktbranch enthält weder
diese Originale noch den einmaligen Importer. Große JSON-Dateien gegebenenfalls
über Raw/Gitblob oder Git beziehen; ein leeres Contents-API-Feld ist kein Original.
