# Agenteneinstieg für picross

Vor auftragsbezogener Arbeit vollständig lesen:

1. [Gemeinsamen Workflow](docs/dev-rules/WORKFLOW.md).
2. [Projektprofil](docs/PROJECT_PROFILE.md) und dessen auftragsbezogene Pflichtquellen.
3. Aktuellen vollständigen Issue-/Paket-Body, sofern vorhanden; bei Review/Nacharbeit zusätzlich PR, tatsächlichen Diff und konkret benannten Reviewstand.

Den beauftragten Arbeitsbranch verwenden, sonst den aktuellen `main`; geltende Bereichs-/Override-Regeln prüfen. Neue Ideen setzen kein vorhandenes Issue voraus. Fehlende Pflichtquellen nicht durch Erinnerungen ersetzen.

Bei Schwierigkeitsanalyse, Kalibrierung oder Bewertungsmetadaten zusätzlich
[SD: Rätselschwierigkeit](docs/PUZZLE_DIFFICULTY.md) vollständig lesen.
SD-A / #236 liefert den getrennten Analysator gemäß
[technischem Vertrag](docs/SD_ANALYZER.md). SD-B/SD-C und Bestandsbewertung
bleiben nachgelagert. Der echte Katalog ist weder Testbestand noch
unmittelbare Kalibrierungsgrundlage für die Skalenenden.

Bei Hinweisnavigation, Vollhinweis-Overlay oder Cursor-Linienhervorhebung zusätzlich [HN: Hinweisinteraktion](docs/CLUE_INTERACTION.md) vollständig lesen. HN / #192 ist implementiert; technische Nachweise und die getrennten Abnahmen HN-R01/HN-M01 stehen im Issue/PR.

Bei Zellrendering, Sprite-/Atlasherstellung, Cache-/Invalidierungsarbeit und PERF-01 zusätzlich [Zellrendering-Vertrag](docs/CELL_RENDERING.md) vollständig lesen. [PERF-A](docs/PERF_A_IMPLEMENTATION.md) und [PERF-B](docs/PERF_B_IMPLEMENTATION.md) sind historische Lieferberichte. Aktuelle Ressourcen-/Cache-/Pixelprüfungen folgen Zellrendering-Vertrag und CI-Policy; historische Hersteller- und A/B-Reproduktion ist gemäß #70/N70-HIST-01 keine Pflicht.

Nur bei Vorbereitung einer noch auszuführenden Implementierung oder konkreter noch offener technischer Nacharbeit zusätzlich [Modellauswahl](docs/dev-rules/MODEL_SELECTION.md) und [Modellkatalog](docs/dev-rules/MODEL_CATALOG.md) vollständig lesen. Keine rückblickende Empfehlung nach erledigter Arbeit.

## Unmittelbar wichtige Grenzen

Das Setup ist keine Freigabe einer Engine, Sprache, Zielplattform oder Spielmechanik. Noch nicht dokumentierte Produktentscheidungen vor der betroffenen Umsetzung klären. Keine Fach- oder Umgebungsregeln aus anderen Projekten ungeprüft übertragen.

Die Dokumentprüfung ersetzt keine späteren Produkt-, Rätsel-, UI- oder Plattformtests. Keine Secrets, privaten Daten oder ungeklärten Fremdassets committen; keine Dienste, Veröffentlichungen oder kostenpflichtigen Integrationen ohne passenden Auftrag. Erlaubte Prüfungen und die Mergewirkung stehen im [Projektprofil](docs/PROJECT_PROFILE.md).

## Code Review Rules

Beim Setup Quellenzugriff, Snapshot-Identität, Befugnisgrenzen und den tatsächlichen Umfang der Prüfbelege kontrollieren. Bei Produktarbeit die dann verbindlich beschlossenen Fachverträge und Akzeptanzkriterien prüfen, nicht Annahmen aus dem Projektnamen ableiten. Allgemeine Regeln nicht duplizieren oder ungefragt zentral aktualisieren; Herkunft in [DEV_RULES_ADOPTION.md](docs/DEV_RULES_ADOPTION.md).
