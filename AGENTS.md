# Agenteneinstieg für picross

Vor auftragsbezogener Arbeit vollständig lesen:

1. [Gemeinsamen Workflow](docs/dev-rules/WORKFLOW.md).
2. [Projektprofil](docs/PROJECT_PROFILE.md) und dessen auftragsbezogene Pflichtquellen.
3. Aktuellen vollständigen Issue-/Paket-Body, sofern vorhanden; bei Review/Nacharbeit zusätzlich PR, tatsächlichen Diff und konkret benannten Reviewstand.

Den beauftragten Arbeitsbranch verwenden, sonst den aktuellen `main`; geltende Bereichs-/Override-Regeln prüfen. Neue Ideen setzen kein vorhandenes Issue voraus. Fehlende Pflichtquellen nicht durch Erinnerungen ersetzen.

Bei Abschlussbildern, deren Katalogvorschau oder Bildrevisionen zusätzlich
[AT: Transparente Abschlussbilder](docs/REVEAL_TRANSPARENCY.md) und die dort
benannten Produkt-/Produktions-/Integrationsquellen vollständig lesen.
AT / #256 (19.10.2026), Umsetzungsvorbereitung V4: AT-A ist nach qualifiziertem
AT-A-R01 über PR #263 auf `a0cb25eda49d29d3062fd3bcfeab9fda220c7aa9` integriert;
AT-A schafft den sicheren gemeinsamen Bildrevisionsweg; AT-B stellt danach den
gebundenen Bestand mit neuen Bildfreigaben um. Reine Bildänderungen erhalten
Definitionsbytes, Puzzle-Revision, Identität, Spielstände und historische Belege.
Szenen erhalten eine konkrete transparente Gestaltung, keinen pauschalen Verzicht.
AT-B-V01 liefert den vollständigen gebundenen Bildsatz in Draft-PR #264.
Die anschließende [Eigentümerabnahme](docs/AT_B_OWNER_APPROVAL.md) erlaubt AT-B-F01
auf `chore/256-transparente-bestandsbilder`: kontrolliertes `catalog_reveal plan/adopt`
aller 26 freigegebenen Bilder und AT-B-T01. [AT-B-Bericht](docs/AT_B_VERIFICATION.md).
Keine Rasterproduktion, echte Spielstände, Merge, Deployment oder Issue-Schließung.
Das qualifizierte separate AT-B-R01 am Integrationshead bleibt offen.
AT-A-P01 / Umsetzungsvorbereitung V2 ist mit PR #257 auf
`9cc58651518e3a28e97f46932d69554210b0abcb` integriert und schließt die Verträge:
[Daten/Freigabe](docs/ZA1_ADAPTER.md),
[Auflösung/Folgeoperationen](docs/CATEGORIES.md),
[Journal/Recovery](docs/SD_CATALOG.md) und
[CLI](tools/puzzle_production/README.md).
Inhalts-v2, Runtime-v4 und Saves bleiben unverändert; technische Kernfragen aus
AT §4.3 sind damit spezifiziert. [AT-A-T01](docs/AT_A_VERIFICATION.md) führt
technische Nachweise und getrenntes Selbstreview des damaligen AT-A-Stands;
der aktuelle AT-B-Auftrag ersetzt diese historischen Belege nicht.

Bei UI-Schrift, kleinen Rahmen, Dropdowns oder Piktogrammen zusätzlich
[HZ: Handgezeichnete Bedienoberfläche](docs/HAND_DRAWN_UI.md) vollständig lesen.
HZ-A/B sind über PR #288/#289 integriert und in #284 separat abgenommen.
HZ-C / [#294](https://github.com/venomenon328/picross/issues/294) ist seit
21.10.2026 auf `fix/294-tidy-typografie` implementiert; technische Lieferung in
[Draft-PR #296](https://github.com/venomenon328/picross/pull/296).
[HZ-C-Prüfzuordnung](docs/HZ_C_VERIFICATION.md) bindet Ursache, stabile Grundlinien
und den korrigierten Vergleich 14/15 einschließlich Kategorienamen. Gewählte
kleine Rolle ist 15 bei UI100 und 19 bei UI125; Blattkennungen bleiben 15/19.
HZ-C-R01 und HZ-C-M01 bleiben getrennt vor Merge offen.
Tidy Hand samt lokalen Fallbacks, bisherige Überschriften und die HZ-B-Konturen,
Menüs und Symbolfamilie bleiben Grundlage.
Hinweisziffern/-geometrie und die drei großen SL-Rasterrahmen behalten ihre Verträge.
Spezifikationspflege beauftragt keinen Produktcode oder Merge.

Bei Katalog-/Metadatenarbeit zusätzlich [Katalogdarstellung](docs/CATALOG_PRESENTATION.md)
und [Katalogsortierung](docs/CATALOG_SORTING.md) vollständig lesen. KU / #244
ist mit KU-A/PR #254 und KU-B/PR #255 integriert: Papierstreifen,
Schwierigkeitskreise, Stiftsymbole, Statusfußzeile, Sortierung und einmalige
Hinzugefügt-Metadaten. Die offenen persönlichen KU-Abnahmen bleiben in #244;
HZ nimmt sie nicht ab. Die Ablösung alter KE-Anzeigen ist verbindlich;
historische Liefernachweise bleiben an ihre damaligen Stände gebunden. Eine
Spezifikationsfreigabe ist weder Implementierungsauftrag noch Mergefreigabe.

Bei Schwierigkeitsanalyse, Kalibrierung oder Bewertungsmetadaten zusätzlich
[SD: Rätselschwierigkeit](docs/PUZZLE_DIFFICULTY.md),
[SD-A-Analysator](docs/SD_ANALYZER.md),
[SD-B-Methodenvertrag](docs/SD_CALIBRATION.md) und
[SD-C1-Daten-/Recoveryvertrag](docs/SD_CATALOG.md) vollständig lesen.
SD / #235 ist mit PR #240–#243 einschließlich C2 abgeschlossen; aktive Methode
bleibt `picross-difficulty-0.3`. Frühere offene SD-Gates sind historische Stände.

Die am 25.10.2026 freigegebene Folgespezifikation
[SD2: Menschennähere Schwierigkeit](docs/PUZZLE_DIFFICULTY_V2.md) / #402 ist
ebenfalls vollständig zu lesen. SD2-A/B/C/D (#403–#406) trennen neue Regeln und
Messprofile, Referenzkalibrierung, kompatible Integration und Bestandsumstellung.
SD2-A ist nach separatem R01 über PR #408 auf
`c7c6156ac27dc033036443bc06ef398bbf94f32f` integriert und liefert den separat versionierten
[technischen Vertrag](docs/SD2_ANALYZER.md) (bei SD2-Analyse vollständig lesen),
Analysator/Prüfer, drei Rohprofile und eigene CLI. [Nachweise](docs/SD2_A_VERIFICATION.md)
bleiben an den historischen A-Lieferhead gebunden.
SD2-B liefert in Draft-PR #409 den [Bewertungsvertrag](docs/SD2_CALIBRATION.md)
(bei SD2-Bewertung vollständig lesen), 36 neue synthetische Referenzen,
getrennte Validierung und den eigenständigen eingefrorenen 0.4-Bewertungsweg.
[SD2-B-T01](docs/SD2_B_VERIFICATION.md); separates SD2-B-R01 und Merge bleiben offen.
Denkanspruch, Suchaufwand und Bearbeitungsumfang ergeben eine feste Fünferskala.
0.4 ist eigenständig implementiert, nicht gemeinsam integriert oder aktiviert. 0.3-Freeze und aktive Werte
bleiben bis zum gesonderten Auftrag erhalten. Keine Katalogquantile, echten
Katalogtests, automatische Neubewertung oder Implementierung aus Spezifikationsfreigabe.

Bei Hinweisnavigation, Vollhinweis-Overlay oder Cursor-Linienhervorhebung zusätzlich [HN: Hinweisinteraktion](docs/CLUE_INTERACTION.md) vollständig lesen. HN / #192 ist implementiert; technische Nachweise und die getrennten Abnahmen HN-R01/HN-M01 stehen im Issue/PR.

Bei Zellrendering, Sprite-/Atlasherstellung, Cache-/Invalidierungsarbeit und PERF-01 zusätzlich [Zellrendering-Vertrag](docs/CELL_RENDERING.md) vollständig lesen. [PERF-A](docs/PERF_A_IMPLEMENTATION.md) und [PERF-B](docs/PERF_B_IMPLEMENTATION.md) sind historische Lieferberichte. Aktuelle Ressourcen-/Cache-/Pixelprüfungen folgen Zellrendering-Vertrag und CI-Policy; historische Hersteller- und A/B-Reproduktion ist gemäß #70/N70-HIST-01 keine Pflicht.

Nur bei Vorbereitung einer noch auszuführenden Implementierung oder konkreter noch offener technischer Nacharbeit zusätzlich [Modellauswahl](docs/dev-rules/MODEL_SELECTION.md) und [Modellkatalog](docs/dev-rules/MODEL_CATALOG.md) vollständig lesen. Keine rückblickende Empfehlung nach erledigter Arbeit.

## Unmittelbar wichtige Grenzen

Das Setup ist keine Freigabe einer Engine, Sprache, Zielplattform oder Spielmechanik. Noch nicht dokumentierte Produktentscheidungen vor der betroffenen Umsetzung klären. Keine Fach- oder Umgebungsregeln aus anderen Projekten ungeprüft übertragen.

Die Dokumentprüfung ersetzt keine späteren Produkt-, Rätsel-, UI- oder Plattformtests. Keine Secrets, privaten Daten oder ungeklärten Fremdassets committen; keine Dienste, Veröffentlichungen oder kostenpflichtigen Integrationen ohne passenden Auftrag. Erlaubte Prüfungen und die Mergewirkung stehen im [Projektprofil](docs/PROJECT_PROFILE.md).

## Code Review Rules

Beim Setup Quellenzugriff, Snapshot-Identität, Befugnisgrenzen und den tatsächlichen Umfang der Prüfbelege kontrollieren. Bei Produktarbeit die dann verbindlich beschlossenen Fachverträge und Akzeptanzkriterien prüfen, nicht Annahmen aus dem Projektnamen ableiten. Allgemeine Regeln nicht duplizieren oder ungefragt zentral aktualisieren; Herkunft in [DEV_RULES_ADOPTION.md](docs/DEV_RULES_ADOPTION.md).
