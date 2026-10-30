# Agenteneinstieg für picross

Vor auftragsbezogener Arbeit vollständig lesen:

1. [Gemeinsamen Workflow](docs/dev-rules/WORKFLOW.md).
2. [Projektprofil](docs/PROJECT_PROFILE.md) und dessen auftragsbezogene Pflichtquellen.
3. Aktuellen vollständigen Issue-/Paket-Body, sofern vorhanden; bei Review/Nacharbeit zusätzlich PR, tatsächlichen Diff und konkret benannten Reviewstand.

Den beauftragten Arbeitsbranch verwenden, sonst den aktuellen `main`; geltende Bereichs-/Override-Regeln prüfen. Neue Ideen setzen kein vorhandenes Issue voraus. Fehlende Pflichtquellen nicht durch Erinnerungen ersetzen.

Bei Entwicklung an der Schritt-4-Integration, Registrierungsbudgets,
Paket-Prüfkontexten oder Publikationsguards/Recovery zusätzlich
[RI: Zuverlässige und messbare Rätselintegration](docs/PUZZLE_INTEGRATION.md)
vollständig lesen. [RI / #477](https://github.com/venomenon328/picross/issues/477)
ist seit 29.10.2026 als Sollvertrag freigegeben. RI-A ist über PR #484 auf
`864c4e6` integriert; RI-B ist auf seinem beauftragten Branch implementiert,
[B-T01](docs/RI_B_VERIFICATION.md) führt Nachweise und offene Gates. RI-C bleibt
unimplementiert. Reihenfolge: RI-A → Messauswertung und gemeinsamer
B/C-Vertragsabgleich → RI-B → RI-C. Für neue Registrierungspublikationen ist
eine Warnung nach 300 s mit vorläufig 1800 s konfigurierbarem Schutzrahmen
vorgesehen; Recovery unterstützter Registrierungsjournale erhält einen eigenen,
ebenfalls vorläufig 1800 s langen Rahmen. Andere operative Budgets sowie
Eingangs-, Proof- und Ressourcengrenzen bleiben unverändert. Bis zur jeweiligen
Lieferung gelten die bestehenden ausführbaren Grenzen und Prüfwege; die
Spezifikation beauftragt weder Implementierung noch Budgetbypass oder Merge.
Normale Authoringaufträge erhalten dadurch keinen zusätzlichen Freigabeprozess.

Bei CI, Tests, Prüfartefakten, Bestandsbereinigung oder Produktionsabschluss zusätzlich
[CI2: Kurze CI und begrenzter aktiver Bestand](docs/CI_SLIMMING.md),
[CI-Policy](docs/CI_POLICY.md) und [Bestandsinventar](docs/DEVELOPMENT_ARCHIVE.md)
vollständig lesen. CI2 / [#412](https://github.com/venomenon328/picross/issues/412)
ist am 26.10.2026 als Spezifikation freigegeben; die beauftragten Umsetzungspakete
und ihre aktuellen Nachweise stehen nachfolgend.
CI2-A / #413 ist nach separatem R01 über PR #419 auf
`94e3ea7d9674babbdcd6bde6251e233191fd096f` integriert.
CI2-B ist nach separatem R01 über PR #420 auf
`dd56d310d942eee47448df4cdcca5e4af4a49b00` integriert.
[Auswahlvertrag](docs/CI_A_SELECTION.md) und [B-T01](docs/CI2_B_VERIFICATION.md)
bleiben gebunden; CI2-B-O01 bleibt im Gesamtvorhaben offen.
CI2-C / #415 ist nach separatem R01 über PR #421 auf
`8e5e99647596bc3ef9d7bd22bd746b73fbb424d5` integriert.
[Browservertrag](docs/CI_B_BROWSER_GROUPS.md) und [C-T01](docs/CI2_C_VERIFICATION.md)
bleiben an ihre Lieferung gebunden. CI2-D / #416 ist nach separatem R01 über
PR #422 auf `8c31a69916941aed60ecd7e4d35a8d0d00637bf9` integriert;
[D-T01](docs/CI2_D_VERIFICATION.md) bleibt an seine Lieferung gebunden.
CI2-E / #417 ist nach separatem finalem R01 über PR #423 auf
`53f9c1f6d87d752e6b0f3152985fd0a83de2278b` integriert:
[E-T01](docs/CI2_E_VERIFICATION.md) bindet Revisionsabschluss, Bereinigung und
Metadatencheck. Die historischen E-Protokolle bleiben an ihre Lieferstände gebunden.
CI2-F / #424 optimiert ausschließlich die Katalog-Fachprüfung;
[F-T01](docs/CI2_F_VERIFICATION.md) bindet Messung und Lieferung.
Separates qualifiziertes CI2-F-R01 bleibt vor Merge erforderlich.
Keine Bestandslöschung oder Merge aus der Spezifikationsfreigabe ableiten.
Der aktuelle Umfang verlangt Chromium ausschließlich auf ausdrücklichen Auftrag und
ersetzt die 500er-Historyroute durch höchstens 20 semantische Benutzerkommandos,
höchstens sechs neue wirksame History-Transaktionen und genau zwei echte Spielprozesse.
Die Laufzeitziele (Docs unter einer Minute, Standard möglichst unter fünf Minuten,
relevante Integration unter zehn Minuten, kurzer Chromiumlauf höchstens acht Minuten)
und die Regeln für
begrenzte Artefaktaufbewahrung, Arbeitsabschluss und neuen Dateibestand folgen CI2.
Sie sind Sollvorgaben, keine bereits gemessene Wirkung oder neue Ausnahme vom Ergebnisgate.

Bei Abschlussbildern, deren Katalogvorschau oder Bildrevisionen zusätzlich
[AT: Transparente Abschlussbilder](docs/REVEAL_TRANSPARENCY.md) und die dort
benannten Produkt-/Produktions-/Integrationsquellen vollständig lesen.
AT-A und AT-B sind seit 19.10.2026 über
[PR #263](https://github.com/venomenon328/picross/pull/263) und
[PR #264](https://github.com/venomenon328/picross/pull/264) auf `main` integriert;
alle 26 gebundenen Bestandsbilder wurden mit tatsächlichen Bildfreigaben umgestellt.
Reine Bildänderungen erhalten Definitionsbytes, Puzzle-Revision, Identität,
Spielstände und historische Belege. Die technischen Quellen bleiben
[Daten/Freigabe](docs/ZA1_ADAPTER.md), [Auflösung/Folgeoperationen](docs/CATEGORIES.md),
[Journal/Recovery](docs/SD_CATALOG.md) und [CLI](tools/puzzle_production/README.md).
Szenen erhalten eine konkrete transparente Gestaltung, keinen pauschalen Verzicht.
[AT-A-T01](docs/AT_A_VERIFICATION.md), [AT-B-Bericht](docs/AT_B_VERIFICATION.md)
und [Eigentümerabnahme](docs/AT_B_OWNER_APPROVAL.md) bleiben historische Quellen.
Der spätere Bildarbeitsabschluss folgt [Authoring §9](docs/ai-workflows/PUZZLE_AUTHORING.md#9-produktionsabschluss-und-bereinigung)
und CI2; frühere offene Lieferstatus erteilen keinen erneuten Auftrag.

Bei UI-Schrift, kleinen Rahmen, Dropdowns oder Piktogrammen zusätzlich
[HZ: Handgezeichnete Bedienoberfläche](docs/HAND_DRAWN_UI.md) vollständig lesen.
HZ-A/B sind seit 20.10.2026 über
[PR #288](https://github.com/venomenon328/picross/pull/288) /
[PR #289](https://github.com/venomenon328/picross/pull/289), HZ-C seit 21.10.2026
über [PR #296](https://github.com/venomenon328/picross/pull/296) auf `main` integriert.
Die gewählte kleine Rolle bleibt 15 bei UI100 und 19 bei UI125; Blattkennungen 15/19.
Tidy Hand samt lokalen Fallbacks, bisherige Überschriften und die HZ-B-Konturen,
Menüs und Symbolfamilie bleiben Grundlage. Hinweisziffern/-geometrie und die drei
großen SL-Rasterrahmen behalten ihre Verträge. Die [HZ-C-Prüfzuordnung](docs/HZ_C_VERIFICATION.md)
ist ein historischer Liefernachweis; der abgeschlossene Vergleich 14/15 wird durch
CI2 nicht erneut Pflicht. Spezifikationspflege beauftragt keinen Produktcode oder Merge.

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
SD / #235 ist mit PR #240–#243 einschließlich C2 abgeschlossen; dessen Methode
`picross-difficulty-0.3` bleibt unverändert lesbar. Frühere offene SD-Gates sind historische Stände.

Die am 25.10.2026 freigegebene Folgespezifikation
[SD2: Menschennähere Schwierigkeit](docs/PUZZLE_DIFFICULTY_V2.md) / #402 ist
ebenfalls vollständig zu lesen. Zusätzlich je Auftrag vollständig lesen:
[Analysatorvertrag](docs/SD2_ANALYZER.md) bei SD2-Analyse,
[Bewertungsvertrag](docs/SD2_CALIBRATION.md) bei SD2-Bewertung und
[Integrationsvertrag](docs/SD2_INTEGRATION.md) bei SD2-Integration.
SD2-A/B/C/D (#403–#406) sind über PR #408–#411 integriert. SD2-D ist seit
26.10.2026 über [PR #411](https://github.com/venomenon328/picross/pull/411) auf
`967314538df376a281020fb4c34f93f370a491df` Teil von `main`:
alle 45 abgenommenen Vorschläge sind übernommen, aktive Ratings und Produktionsstandard
sind 0.4. Beide Freezes und historische Quellen bleiben erhalten.
Denkanspruch, Suchaufwand und Bearbeitungsumfang ergeben eine feste Fünferskala.
[SD2-D-F01/T01](docs/SD2_D_ADOPTION.md) und die A/B/C-Lieferberichte bleiben an ihre
damaligen Stände gebunden. Die Chromium-/Gesamt-CI-Ausnahmen für PR #410/#411 sind
historische Einzelentscheidungen, kein neuer pauschaler Erfolgsverzicht und keine
nachträgliche Behauptung eines vollständigen CI-Passes. Keine Katalogquantile,
echten Katalogtests oder automatische Neubewertung; Spezifikationsfreigabe allein
beauftragt keine Implementierung.

Bei Hinweisnavigation, Vollhinweis-Overlay oder Cursor-Linienhervorhebung zusätzlich [HN: Hinweisinteraktion](docs/CLUE_INTERACTION.md) vollständig lesen. HN / #192 ist implementiert; technische Nachweise und die getrennten Abnahmen HN-R01/HN-M01 stehen im Issue/PR.

Bei Zellrendering, Sprite-/Atlasherstellung, Cache-/Invalidierungsarbeit und PERF-01 zusätzlich [Zellrendering-Vertrag](docs/CELL_RENDERING.md) vollständig lesen. [PERF-A](docs/PERF_A_IMPLEMENTATION.md) und [PERF-B](docs/PERF_B_IMPLEMENTATION.md) sind historische Lieferberichte. Aktuelle Ressourcen-/Cache-/Pixelprüfungen folgen Zellrendering-Vertrag und CI-Policy; historische Hersteller- und A/B-Reproduktion ist gemäß #70/N70-HIST-01 keine Pflicht.

Nur bei Vorbereitung einer noch auszuführenden Implementierung oder konkreter noch offener technischer Nacharbeit zusätzlich [Modellauswahl](docs/dev-rules/MODEL_SELECTION.md) und [Modellkatalog](docs/dev-rules/MODEL_CATALOG.md) vollständig lesen. Keine rückblickende Empfehlung nach erledigter Arbeit.

**Projektlokale Ausnahme für die Rätselproduktion:** Normale Aufträge nach
[PUZZLE_AUTHORING](docs/ai-workflows/PUZZLE_AUTHORING.md), einschließlich Korrektur
und Wiederaufnahme, benötigen keine Modell-, Reasoning- oder Ausführungsempfehlung.
Die beiden Modellquellen dafür nicht laden und keine entsprechende Modellrecherche
ausführen. Die tatsächlichen Bild-, Datei-, Repository- und Werkzeugfähigkeiten
weiter prüfen. Für die Produktionsausgabe gilt Authoring §7: keine zusätzliche
Handoff-Markdowndatei und kein zusätzlicher kopierbarer Folgeauftrag.
Separat beauftragte Entwicklungsarbeit an Werkzeugen, Spiel oder CI bleibt vom
allgemeinen Entwicklungsworkflow erfasst.

## Unmittelbar wichtige Grenzen

Das Setup ist keine Freigabe einer Engine, Sprache, Zielplattform oder Spielmechanik. Noch nicht dokumentierte Produktentscheidungen vor der betroffenen Umsetzung klären. Keine Fach- oder Umgebungsregeln aus anderen Projekten ungeprüft übertragen.

Die Dokumentprüfung ersetzt keine späteren Produkt-, Rätsel-, UI- oder Plattformtests. Keine Secrets, privaten Daten oder ungeklärten Fremdassets committen; keine Dienste, Veröffentlichungen oder kostenpflichtigen Integrationen ohne passenden Auftrag. Erlaubte Prüfungen und die Mergewirkung stehen im [Projektprofil](docs/PROJECT_PROFILE.md).

## Code Review Rules

Beim Setup Quellenzugriff, Snapshot-Identität, Befugnisgrenzen und den tatsächlichen Umfang der Prüfbelege kontrollieren. Bei Produktarbeit die dann verbindlich beschlossenen Fachverträge und Akzeptanzkriterien prüfen, nicht Annahmen aus dem Projektnamen ableiten. Allgemeine Regeln nicht duplizieren oder ungefragt zentral aktualisieren; Herkunft in [DEV_RULES_ADOPTION.md](docs/DEV_RULES_ADOPTION.md).
