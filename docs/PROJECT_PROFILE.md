# Projektprofil: picross

## Geltung und Quellen

- **Repository:** `venomenon328/picross`.
- **Zielbranch:** `main`; ein ausdrücklich beauftragter Arbeitsbranch hat Vorrang.
- **Zuständig für:** aktuelle Entwicklungsbindungen, Fachrouting, Prüfwege und Projektbetrieb.
- **Entwicklungsablauf und Befugnisse:** [AGENTS](../AGENTS.md) und [WORKFLOW](dev-rules/WORKFLOW.md).
- **Dokumentaufbau und Zuständigkeit:** [Dokumentationsindex](README.md).
- **Auftrag, Abnahme und tatsächlicher Lieferstatus:** aktueller zuständiger Issue-/PR-Stand. Dieses Profil ist keine Lieferchronologie.

Normale Rätselproduktion einschließlich Korrektur und Wiederaufnahme folgt dem
Produktionseinstieg in AGENTS und der [Authoringroute](production/authoring/PUZZLE_AUTHORING.md#11-pflichtquellen-nach-phase).
Dieses Profil und die Entwicklungsverträge sind dafür keine zusätzliche pauschale
Pflichtlektüre. Regel-, Werkzeug-, Spiel- und CI-Änderungen sind Entwicklungsarbeit.
Querverweise sind Zuständigkeitsangaben; nur ausdrücklich geroutete Quellen oder
Abschnitte werden zur Pflichtlektüre.

## Entwicklungsbasis und Produktgrenzen

| Bindung | Aktueller Vertrag |
| --- | --- |
| Spielprojekt | [game/](../game/README.md), Godot Standard und typisiertes GDScript; genaue Enginebindung in [TOOLCHAIN](ci/TOOLCHAIN.md) |
| Native Entwicklungsplattform | Windows x64; Maus als verpflichtender Eingabepfad, Escape zum Gestenabbruch |
| Zusätzlicher Webweg | [WEB_HOSTING](operations/WEB_HOSTING.md); gleiche Spielregeln, eigene Browserpersistenz-/Hostinggrenzen |
| Darstellung | [BOOK_INTEGRATION](game/BOOK_INTEGRATION.md) und geroutete UI-/Eingabeverträge |
| Produktanforderungen und reguläre Größen | [PRODUCT_DEFINITION](project/PRODUCT_DEFINITION.md); technische Entwicklungsbindung ist keine abschließende Veröffentlichungspolitik |
| Runtime-Inhalt | Ausschließlich aktuelle registrierte Daten; Inhaltsautorität und Runtimeprojektion nach [RI-ONE](production/PUZZLE_INTEGRATION_SINGLE_PATH.md) |
| App-/Saveidentität | `picross · P1`, Save-Schema 1, `user://p1/saves/`; vollständige Validierung vor Normalisierung nach [P1](game/PROTOTYPE_P1.md) |
| Arbeitsproduktion | Ein aktueller Job unter `content/authoring/` plus benötigte Nutzdaten; Abschluss nach [Authoring Schritt 5 §9](production/authoring/PUZZLE_AUTHORING_STEP_5.md#9-produktionsabschluss-und-bereinigung) |
| Neue kreative Produktion | Phasenbezogene Bildregeln und aktuelle Version/Dokumentrevision in [Authoring](production/authoring/PUZZLE_AUTHORING.md), technische aktuelle Form in [PW-B](tools/PW_B_CONTRACT.md) |
| Bild-/Rasterintegration und Pflege | [RI-ONE](production/PUZZLE_INTEGRATION_SINGLE_PATH.md), [ZA-1](production/ZA1_ADAPTER.md), [Bestandseditor](tools/PUZZLE_EDITOR.md) |
| Hintergrundprofile | Ausschließlich [PUZZLE_BACKGROUNDS](production/PUZZLE_BACKGROUNDS.md#hg31--zwei-geschlossene-bildprofile); keine automatische Konversion aktiver Bilder |
| Schwierigkeit | [SD2-Integration](difficulty/SD2_INTEGRATION.md) und aktive Methodendatei; keine Katalogbestandszahl in diesem Profil |

Aktive Ressourcen, Nutzungsrechte, echte Nutzerdaten und kompakte Freigabe-/
Integrationsbindungen bleiben Produktdaten. Testfixtures sind davon getrennt;
keine Prüfung an echten Saves oder wachsende Verwendung des Katalogs als Testkorpus.
Historische Produktionsoriginale behalten ihre Identität. Alt-WIP ist kein
pauschales Kompatibilitätsziel und wird nicht automatisch migriert.

## Pflichtquellen nach Entwicklungsauftrag

Vor Entwicklungsarbeit AGENTS, WORKFLOW, dieses Profil, [CI v2](ci/CI_WORKFLOW_V2.md)
und den vollständigen aktuellen Issue-/Paketstand lesen. Bei Review zusätzlich
Diff, konkret benannten Head/Basis und die tatsächlichen Originalbelege öffnen.
Die folgende Tabelle bestimmt zusätzliche Fachlektüre nach Änderungsbezug.
Für normale Inhalte gilt stattdessen die Authoringroute.

| Entwicklungsarbeit | Zusätzlich vollständig lesen |
| --- | --- |
| Produkt, Regeln, Inhalte, Progression, UX/UI, Eingabe, Plattform oder Architektur | [Produktdefinition](project/PRODUCT_DEFINITION.md) |
| Thematik, Album, Motiventhüllung, UX/UI oder Eingabe/Wertung | [Gestaltungskonzept](project/DESIGN_CONCEPT.md) |
| Spieltechnik, P1-Verträge, Save/Recovery | [P1](game/PROTOTYPE_P1.md), einschlägige Entscheidungen in [#5](https://github.com/venomenon328/picross/issues/5), [Preflight](ci/TOOLCHAIN.md), [Spielanleitung](../game/README.md) |
| Buchpräsentation, Seiten-/Informationswechsel, Spielerhilfe | [Buchintegration](game/BOOK_INTEGRATION.md), bei gezielter historischer Nacharbeit deren verlinkte Lieferbelege |
| Native Windows-Fenstergrößen, Anzeigemodi und Display-Präferenzen | [ANZ](game/DISPLAY_SETTINGS.md), dazu [P1](game/PROTOTYPE_P1.md) und bei Abgrenzung [Webvertrag](operations/WEB_HOSTING.md) |
| Zellgesten, Cursorzähler und Raster-/Fenstergrenzen | [CELL_DRAG](game/CELL_DRAG.md), [Hinweisfont](game/CLUE_TYPOGRAPHY.md) |
| Hinweisnavigation, Overlay, Cursorlinien oder Hinweiszustände | [CLUE_INTERACTION](game/CLUE_INTERACTION.md), [CLUE_TYPOGRAPHY](game/CLUE_TYPOGRAPHY.md), [CLUE_STATUS](game/CLUE_STATUS.md) nach Änderungsbezug |
| Zeichensprache, Vorschau, Zellanimation | [UI_DRAWING_STYLE](game/UI_DRAWING_STYLE.md), betroffene ZS-Verträge |
| UI-Schrift, kleine Rahmen, Dropdowns, Piktogramme | [HAND_DRAWN_UI](game/HAND_DRAWN_UI.md), [UI_DRAWING_STYLE](game/UI_DRAWING_STYLE.md), [Z2-Ressourcenweg](game/Z2_SELECTION.md) |
| Große bildbasierte Buchseitentitel und Informationsnavigation | [BTI-Bildtitel](game/VIEW_TITLE_ART.md), [Buchintegration](game/BOOK_INTEGRATION.md), [HZ](game/HAND_DRAWN_UI.md) |
| Spriteherstellung, Zellrendering, Cache/Invalidierung | [CELL_RENDERING](game/CELL_RENDERING.md); historische PERF-A/B-Reproduktion ist keine Dauerpflicht |
| Sidebar/Zoomnormalisierung | [SL65](game/SIDEBAR.md), aktuelle P1-/Saveverträge |
| Katalog, Metadaten oder Sortierung | [CATALOG_PRESENTATION](game/CATALOG_PRESENTATION.md), [CATALOG_SORTING](game/CATALOG_SORTING.md), [CATEGORIES](game/CATEGORIES.md) |
| Lokaler Bestandseditor oder unabhängige Namens-/Kategoriepflege | [PUZZLE_EDITOR](tools/PUZZLE_EDITOR.md), [Kategorien](game/CATEGORIES.md), jeweiliges Paket in [#576](https://github.com/venomenon328/picross/issues/576) und tatsächlich betroffene Fachverträge |
| Abschlussbilder, Bildrevisionen oder Katalogvorschau | [REVEAL_TRANSPARENCY](production/REVEAL_TRANSPARENCY.md), [Bildnormen nach Typ](production/images/README.md) und dort geroutete Produktions-/Integrationsquellen |
| Hintergrundzeichnungen je Rätsel, ihre Auswahl, Ableitung oder Einführung | [PUZZLE_BACKGROUNDS](production/PUZZLE_BACKGROUNDS.md), [PUZZLE_AUTHORING](production/authoring/PUZZLE_AUTHORING.md), [PUZZLE_QUALITY](production/PUZZLE_QUALITY.md), [Bildnormen nach Typ](production/images/README.md); spezifizierten Sollweg und tatsächlichen Unterstützungsstand unterscheiden |
| Änderungen am Produktionsregelwerk oder an redaktionellen Qualitätsverträgen | [PUZZLE_AUTHORING](production/authoring/PUZZLE_AUTHORING.md), [Qualitätsvertrag](production/PUZZLE_QUALITY.md), [Bildnormen nach Typ](production/images/README.md) und tatsächlich betroffene Fachquellen |
| Produktionsassistent, lokaler Git-/Bildzugriff, Launcher oder fünfstufiger Produktionsweg | [PRODUCTION_WORKSPACE](tools/PRODUCTION_WORKSPACE.md) und zuständiges aktuelles Paket; bei Authoringdaten/Projektion zusätzlich [PW_B_CONTRACT](tools/PW_B_CONTRACT.md) |
| Produktionswerkzeuge, Import, Reparatur, Assets, Proofs | [PUZZLE_PRODUCTION](production/PUZZLE_PRODUCTION.md), [Werkzeuganleitung](../tools/puzzle_production/README.md), betroffene versionierte Manifeste/Verträge |
| Batchverarbeitung, Checkpoints oder Wiederaufnahme vorbereiteter Produktions-/Integrationsjobs | [PRODUCTION_BATCH](tools/PRODUCTION_BATCH.md) und die tatsächlich verwendeten Einzelverträge; BA-A endet lokal, BA-B orchestriert separat autorisierte Einzelintegration, Gitabschluss bleibt getrennt |
| Schritt-4-Integrationscode, Registrierungsbudgets, Prüfkontext, Publikationsguards/Recovery | [PUZZLE_INTEGRATION](production/PUZZLE_INTEGRATION.md), [ZA1_ADAPTER](production/ZA1_ADAPTER.md), aktuelles Paket; Soll und ausführbaren Stand unterscheiden |
| Schwierigkeit, Analyse, Kalibrierung, Bewertung oder deren Integration | [SD2](difficulty/PUZZLE_DIFFICULTY_V2.md), [SD](difficulty/PUZZLE_DIFFICULTY.md), je nach Änderung [SD2-Analyse](difficulty/SD2_ANALYZER.md), [SD2-Kalibrierung](difficulty/SD2_CALIBRATION.md), [SD2-Integration](difficulty/SD2_INTEGRATION.md), kompatible [SD-Analyse](difficulty/SD_ANALYZER.md), [0.3-Freeze](difficulty/SD_CALIBRATION.md), [Daten-/Recoveryvertrag](difficulty/SD_CATALOG.md), [Paarlinien](production/PAIRED_LINES.md), Kategorien/ZA-1/Katalogdarstellung |
| CI, Prüfprogramme, Artefakte oder neue Tests | [CI_WORKFLOW_V2](ci/CI_WORKFLOW_V2.md), tatsächlich betroffene [Native](ci/CI_C_NATIVE_GROUPS.md)-/[Fach](ci/CI_A_SELECTION.md)-/[Browser](ci/CI_B_BROWSER_GROUPS.md)-Verträge |
| Webbuild, Browserpersistenz oder Hosting | [WEB_HOSTING](operations/WEB_HOSTING.md) und betroffene Fachverträge |
| Bestandsbereinigung oder historische CI-Nacharbeit | [Historische Quellen](history/README.md) und nur die tatsächlich betroffenen Originale |


## Entwicklungsprozess und Werkzeuge

| Regelbereich | Einzige zuständige Quelle |
| --- | --- |
| Phasen, Befugnisse, Review, Merge | [WORKFLOW](dev-rules/WORKFLOW.md) |
| Test-/Artefaktlebenszyklus | [CI_CONTRACT](dev-rules/CI_CONTRACT.md) |
| Ausführbare CI und Modulauswahl | [CI_WORKFLOW_V2](ci/CI_WORKFLOW_V2.md) |
| Lokale Arbeitswurzel und Bereinigung | [WORKSPACE](dev-rules/WORKSPACE.md) |
| Entwicklungs-JSON und Sheet | [HANDOFF](dev-rules/HANDOFF.md), [Entwicklungssheet](workflow/Entwicklungsworkflow_Cheat-Sheet.html) |
| Noch anstehende Ausführungsentscheidung | [MODEL_SELECTION](dev-rules/MODEL_SELECTION.md), [MODEL_CATALOG](dev-rules/MODEL_CATALOG.md) |
| Herkunft der lokalen Workflowregeln | [DEV_RULES_ADOPTION](project/DEV_RULES_ADOPTION.md) |
| PW-/PE-/PG-Installer und Updateprotokoll | [PRODUCTION_UPDATES](tools/PRODUCTION_UPDATES.md), [PE-Appvertrag](tools/PUZZLE_EDITOR.md#14-pe-app-a--feste-windows-produkt--und-releasebindung), [WINDOWS_BUILD](../tools/production_workspace/WINDOWS_BUILD.md), [WINDOWS_GAME_APP](operations/WINDOWS_GAME_APP.md) |

Keine Modell-/Reasoning-Empfehlung für normale Rätselproduktion. Eine erforderliche
Empfehlung für noch anstehende Entwicklung richtet sich nach den Modellregeln;
keine rückblickende Recherche nach erledigter Umsetzung.

## Prüfung und Umgebungen

Die Checks `docs` und `ci-required`, buildfreie Änderungsklassen, optionale Module
und Artefaktbehandlung sind ausschließlich in [CI v2](ci/CI_WORKFLOW_V2.md) definiert.
Der jeweilige `.ci/package.json` bestimmt die begründete konkrete Auswahl.

Python 3.11+ und Standardbibliothek genügen für den lokalen Dokument-/Paketkern:

```sh
python -m unittest discover -s tools -p 'test_ci_modular.py' -v
python tools/check_docs.py
```

Bildbefehle verwenden die isolierte Pillow-Umgebung der Werkzeuganleitung. Native
Prüfungen folgen dem [Gruppenharness](ci/CI_C_NATIVE_GROUPS.md); tatsächliche
Windowsstarts und persönliche Bedienabnahmen werden getrennt belegt. Keine
globale Engineinstallation oder Verwendung echter Saveprofile für Tests.

Der Dokumentprüfer prüft UTF-8/LF, Abschlusszeile, Whitespace, Pflichtdateien,
Workflowversion und einfache lokale Inline-Dateilinks. Anker, externe URLs,
vollständige Markdownsemantik und Spielverhalten sind nicht automatisch geprüft;
bei einschlägigem Diff diese konkrete Lücke gezielt prüfen.

## Merge und Betrieb

Standard ist Squash-Merge mit passender ausdrücklicher oder bedingter
Nutzerfreigabe nach WORKFLOW. Die aktuelle Review-/Checkbindung und vereinbarte
Vor-Merge-Abnahmen bleiben Voraussetzung; ein Sheetdefault ist keine Freigabe.

Ein Merge startet Package CI. Er deployt das Spiel nicht automatisch. Separat
autorisierte App-Releaseworkflows können nach erfolgreicher Main-CI bei relevantem
Payload veröffentlichen; Protokoll, Flags und Releaseautorität stehen im
[Updatevertrag](tools/PRODUCTION_UPDATES.md). Tatsächlichen Betriebsstatus im jeweiligen
Issue/Release prüfen. Diese Dokumentation aktiviert weder Kanäle noch Secrets.
Zusätzliche Spiel-Releases, Tags und manuelles Hosting benötigen eigenen Auftrag.

[ChatGPT-Projekteinstellungen](project/CHATGPT_PROJECT_INSTRUCTIONS.md) setzt der Nutzer
separat ein. Ein Git-Merge ändert keine externen Projekteinstellungen oder das
zentrale dev-rules-Repository.
