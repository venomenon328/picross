# Agenteneinstieg für picross

Vor auftragsbezogener Arbeit vollständig lesen:

1. [Gemeinsamen Workflow](docs/dev-rules/WORKFLOW.md).
2. [Projektprofil](docs/PROJECT_PROFILE.md) und dessen auftragsbezogene Pflichtquellen.
3. Aktuellen vollständigen Issue-/Paket-Body, sofern vorhanden; bei Review/Nacharbeit zusätzlich PR, tatsächlichen Diff und konkret benannten Reviewstand.

Den beauftragten Arbeitsbranch verwenden, sonst den aktuellen `main`; geltende Bereichs-/Override-Regeln prüfen. Neue Ideen setzen kein vorhandenes Issue voraus. Fehlende Pflichtquellen nicht durch Erinnerungen ersetzen.

Bei Abschlussbildern, deren Katalogvorschau oder Bildrevisionen zusätzlich
[AT: Transparente Abschlussbilder](docs/REVEAL_TRANSPARENCY.md) und die dort
benannten Produkt-/Produktions-/Integrationsquellen vollständig lesen.
AT / #256 (19.10.2026) ist als Spezifikation freigegeben, noch nicht implementiert:
AT-A schafft den sicheren gemeinsamen Bildrevisionsweg; AT-B stellt danach den
gebundenen Bestand mit neuen Bildfreigaben um. Reine Bildänderungen erhalten
Definitionsbytes, Puzzle-Revision, Identität, Spielstände und historische Belege.
Szenen erhalten eine konkrete transparente Gestaltung, keinen pauschalen Verzicht.
Die Freigabe beauftragt noch keine Implementierung, Bildübernahme oder Merge.
AT-A-P01 / Umsetzungsvorbereitung V2 schließt im bestehenden Spezifikations-PR
#257 die exakten Sollverträge: [Daten/Freigabe](docs/ZA1_ADAPTER.md),
[Auflösung/Folgeoperationen](docs/CATEGORIES.md),
[Journal/Recovery](docs/SD_CATALOG.md) und
[Soll-CLI](tools/puzzle_production/README.md). Sie sind noch nicht implementiert.
Inhalts-v2, Runtime-v4 und Saves bleiben unverändert; technische Kernfragen aus
AT §4.3 sind damit spezifiziert. Integration und späterer AT-A-Auftrag bleiben separat.

Bei Katalog-/Metadatenarbeit zusätzlich [Katalogdarstellung](docs/CATALOG_PRESENTATION.md)
und [Katalogsortierung](docs/CATALOG_SORTING.md) vollständig lesen. KU / #244
ist als Sollstand freigegeben, noch nicht implementiert: KU-A umfasst Papierstreifen,
Schwierigkeitskreise, Stiftsymbole und Statusfußzeile; KU-B Sortierung und einmalige
Hinzugefügt-Metadaten. Die dort benannte Ablösung alter KE-Anzeigen ist verbindlich;
historische Liefernachweise bleiben an ihre damaligen Stände gebunden. Eine
Spezifikationsfreigabe ist weder Implementierungsauftrag noch Mergefreigabe.

Bei Schwierigkeitsanalyse, Kalibrierung oder Bewertungsmetadaten zusätzlich
[SD: Rätselschwierigkeit](docs/PUZZLE_DIFFICULTY.md) vollständig lesen.
SD-A / #236 liefert den getrennten Analysator gemäß
[technischem Vertrag](docs/SD_ANALYZER.md); zusätzlich den vollständigen
[SD-B-Methodenvertrag](docs/SD_CALIBRATION.md) lesen. SD-B / #237 bindet
`picross-difficulty-0.3`; für Katalog-/Integrationsarbeit zusätzlich
[SD-C1-Daten-/Recoveryvertrag](docs/SD_CATALOG.md) vollständig lesen.
SD-C1 ist nach qualifiziertem R2 mit PR #242 integriert. SD-C2 hat nach bestandenem
Vor-Übernahme-Review gemäß #238/SD-C2-F01 die 26 Bewertungen kontrolliert übernommen;
der identische zweite `adopt` war ein echter No-op. Separates qualifiziertes finales
SD-C-R01/C2-Datenreview und Merge bleiben offen; PR #243 bleibt Draft.
Der echte Katalog ist weder Testbestand noch
unmittelbare Kalibrierungsgrundlage für die Skalenenden.

Bei Hinweisnavigation, Vollhinweis-Overlay oder Cursor-Linienhervorhebung zusätzlich [HN: Hinweisinteraktion](docs/CLUE_INTERACTION.md) vollständig lesen. HN / #192 ist implementiert; technische Nachweise und die getrennten Abnahmen HN-R01/HN-M01 stehen im Issue/PR.

Bei Zellrendering, Sprite-/Atlasherstellung, Cache-/Invalidierungsarbeit und PERF-01 zusätzlich [Zellrendering-Vertrag](docs/CELL_RENDERING.md) vollständig lesen. [PERF-A](docs/PERF_A_IMPLEMENTATION.md) und [PERF-B](docs/PERF_B_IMPLEMENTATION.md) sind historische Lieferberichte. Aktuelle Ressourcen-/Cache-/Pixelprüfungen folgen Zellrendering-Vertrag und CI-Policy; historische Hersteller- und A/B-Reproduktion ist gemäß #70/N70-HIST-01 keine Pflicht.

Nur bei Vorbereitung einer noch auszuführenden Implementierung oder konkreter noch offener technischer Nacharbeit zusätzlich [Modellauswahl](docs/dev-rules/MODEL_SELECTION.md) und [Modellkatalog](docs/dev-rules/MODEL_CATALOG.md) vollständig lesen. Keine rückblickende Empfehlung nach erledigter Arbeit.

## Unmittelbar wichtige Grenzen

Das Setup ist keine Freigabe einer Engine, Sprache, Zielplattform oder Spielmechanik. Noch nicht dokumentierte Produktentscheidungen vor der betroffenen Umsetzung klären. Keine Fach- oder Umgebungsregeln aus anderen Projekten ungeprüft übertragen.

Die Dokumentprüfung ersetzt keine späteren Produkt-, Rätsel-, UI- oder Plattformtests. Keine Secrets, privaten Daten oder ungeklärten Fremdassets committen; keine Dienste, Veröffentlichungen oder kostenpflichtigen Integrationen ohne passenden Auftrag. Erlaubte Prüfungen und die Mergewirkung stehen im [Projektprofil](docs/PROJECT_PROFILE.md).

## Code Review Rules

Beim Setup Quellenzugriff, Snapshot-Identität, Befugnisgrenzen und den tatsächlichen Umfang der Prüfbelege kontrollieren. Bei Produktarbeit die dann verbindlich beschlossenen Fachverträge und Akzeptanzkriterien prüfen, nicht Annahmen aus dem Projektnamen ableiten. Allgemeine Regeln nicht duplizieren oder ungefragt zentral aktualisieren; Herkunft in [DEV_RULES_ADOPTION.md](docs/DEV_RULES_ADOPTION.md).
