# Projektprofil: picross

## Geltung und Quellen

Repository `venomenon328/picross`, Zielbranch `main`. Vor Arbeit die aktuelle
[AGENTS.md](../AGENTS.md), den [Workflow](dev-rules/WORKFLOW.md), dieses Profil
und den vorhandenen aktuellen Issue-/Paketstand lesen. Ein beauftragter Branch
hat Vorrang vor main. Reviews binden tatsächlichen Diff, Head, Basis und Belege.

Dieses Profil hält stabile Projektbindungen und das Fachrouting. Laufende Aufträge,
Abnahmen, Ausnahmen und Lieferstatus stehen im jeweiligen Issue/PR. Frühere
Paketchronologien sind im [Profil vor der Konsolidierung](https://github.com/venomenon328/picross/blob/f3626f28899a48fa4d783716925f7425a3eb1784/docs/PROJECT_PROFILE.md)
verfügbar; ihre damaligen „offen“-/„noch umzusetzen“-Angaben sind kein heutiger Auftrag.
[Lieferberichte und Bestandsquellen](DEVELOPMENT_ARCHIVE.md) dokumentieren jeweils
ihren gebundenen Stand. Sie erweitern weder aktuelle Befugnisse noch die Haupt-CI.

| Regelbereich | Zuständige aktuelle Quelle |
| --- | --- |
| Phasen, Befugnisse, Review und Merge | [WORKFLOW](dev-rules/WORKFLOW.md) |
| Allgemeiner Test-/Artefaktlebenszyklus | [CI_CONTRACT](dev-rules/CI_CONTRACT.md) |
| Ausführbare Picross-CI, Module, Laufzeitziel, Aufbewahrung | [CI_WORKFLOW_V2](CI_WORKFLOW_V2.md); [CI_POLICY](CI_POLICY.md) als Wegweiser |
| Lokale Arbeitswurzel und Bereinigung eigener Daten | [WORKSPACE](dev-rules/WORKSPACE.md) |
| Entwicklungs-JSON und Sheet | [HANDOFF](dev-rules/HANDOFF.md), [Entwicklungssheet](workflow/Entwicklungsworkflow_Cheat-Sheet.html) |
| Ausführungs-/Modellentscheidung für noch anstehende Arbeit | [MODEL_SELECTION](dev-rules/MODEL_SELECTION.md), datierter [MODEL_CATALOG](dev-rules/MODEL_CATALOG.md) |
| Normale Rätselproduktion einschließlich Korrektur/Wiederaufnahme | [PUZZLE_AUTHORING](ai-workflows/PUZZLE_AUTHORING.md) mit eigenem JSON und eigenen Inhaltsfreigaben |
| Herkunft der lokalen Regeln | [DEV_RULES_ADOPTION](DEV_RULES_ADOPTION.md) |

## Entwicklungsbasis und Produktgrenzen

Das reguläre Spiel liegt unter [game/](../game/README.md) und verwendet die
[Buchdarstellung](BOOK_INTEGRATION.md). Aktuelle Entwicklungsbindung: Godot Standard
4.7.2-stable, typisiertes GDScript und native Windows-x64-Fassung. Maus ist der
verpflichtende Eingabepfad, Escape bricht Gesten ab. Der zusätzliche statische
Webentwicklungsweg folgt [WEB_HOSTING](WEB_HOSTING.md). Diese Bindungen sind keine
abschließende Engine-/Betriebssystemmatrix oder Veröffentlichungsfreigabe.

Der Runtimekatalog stammt ausschließlich aus `content/registry.json`; keine
festgeschriebene Bestandszahl in diesem Profil. Reguläre Rätsel sind höchstens
50×50 groß. Die alten F01–F09-Prototypen werden nicht ausgeliefert; feste synthetische
Testinputs sind davon getrennt. Keine Wertung, Live-Fehlerhilfe oder Hypothesen aus
Workflow- oder Setupentscheidungen ableiten. Produktdefinition und Fachverträge
unterscheiden beschlossene Anforderungen, Umsetzung und offene Produktentscheidungen.

P1 bleibt Vertragsname und Appidentität `picross · P1`. Save-Schema 1 und
`user://p1/saves/` bleiben erhalten; vollständige Validierung vor Normalisierung,
keine Tests an echten Saves. Aktuelle Spiel-, History-, Recovery-, Ansichts-,
Hinweis-, Typografie- und Spoilerverträge stehen in den Fachquellen unten.
Aktive Buch-/Font-/Atlasressourcen sowie ihre Lizenzen/Herkunft sind Produktdaten,
keine entbehrlichen CI-Belege.

Authoringarbeitsstände liegen unter [content/authoring](../content/authoring/README.md),
registrierte Pakete unter `content/packages/`. Nach bestätigter Endabnahme und
Main-Integration folgt der eigene Produktionsabschluss nach Authoring §9.
Runtime, Rechte, aktive Metadaten und kompakte Freigabe-/Integrationsbindungen
bleiben erhalten. Keine dauerhafte Wiederholbarkeit abgeschlossener Produktion.

## Pflichtquellen nach Auftrag

| Arbeit | Zusätzlich vollständig lesen |
| --- | --- |
| Produkt, Regeln, Inhalte, Progression, UX/UI, Eingabe, Plattform oder Architektur | [Produktdefinition](PRODUCT_DEFINITION.md) |
| Thematik, Album, Motiventhüllung, UX/UI oder Eingabe/Wertung | [Gestaltungskonzept](DESIGN_CONCEPT.md) |
| Spieltechnik, P1-Verträge, Save/Recovery | [P1](PROTOTYPE_P1.md), einschlägige Entscheidungen in [#5](https://github.com/venomenon328/picross/issues/5), [Preflight](P1_PREFLIGHT.md), [Spielanleitung](../game/README.md) |
| Buchpräsentation, Seiten-/Informationswechsel, Spielerhilfe | [Buchintegration](BOOK_INTEGRATION.md), bei gezielter historischer Nacharbeit deren verlinkte Lieferbelege |
| Native Windows-Fenstergrößen, Anzeigemodi und Display-Präferenzen | [ANZ](DISPLAY_SETTINGS.md), dazu [P1](PROTOTYPE_P1.md) und bei Abgrenzung [Webvertrag](WEB_HOSTING.md) |
| Zellgesten, Cursorzähler und Raster-/Fenstergrenzen | [CELL_DRAG](CELL_DRAG.md), [Hinweisfont](CLUE_TYPOGRAPHY.md) |
| Hinweisnavigation, Overlay, Cursorlinien oder Hinweiszustände | [CLUE_INTERACTION](CLUE_INTERACTION.md), [CLUE_TYPOGRAPHY](CLUE_TYPOGRAPHY.md), [CLUE_STATUS](CLUE_STATUS.md) nach Änderungsbezug |
| Zeichensprache, Vorschau, Zellanimation | [UI_DRAWING_STYLE](UI_DRAWING_STYLE.md), betroffene ZS-Verträge |
| UI-Schrift, kleine Rahmen, Dropdowns, Piktogramme | [HAND_DRAWN_UI](HAND_DRAWN_UI.md), [UI_DRAWING_STYLE](UI_DRAWING_STYLE.md), [Z2-Ressourcenweg](Z2_SELECTION.md) |
| Große bildbasierte Buchseitentitel und untere Informationsnavigation | [BTI-Bildtitel](VIEW_TITLE_ART.md), [Buchintegration](BOOK_INTEGRATION.md), [HZ](HAND_DRAWN_UI.md) |
| Spriteherstellung, Zellrendering, Cache/Invalidierung | [CELL_RENDERING](CELL_RENDERING.md); PERF-A/B nur bei ihrer konkreten historischen Nacharbeit |
| Sidebar/Zoomnormalisierung | [SL65](SL65_IMPLEMENTATION.md), aktuelle P1-/Saveverträge |
| Katalog, Metadaten oder Sortierung | [CATALOG_PRESENTATION](CATALOG_PRESENTATION.md), [CATALOG_SORTING](CATALOG_SORTING.md), [CATEGORIES](CATEGORIES.md) |
| Abschlussbilder, Bildrevisionen oder Katalogvorschau | [REVEAL_TRANSPARENCY](REVEAL_TRANSPARENCY.md) und dort geroutete Produktions-/Integrationsquellen |
| Neue Rätsel konzipieren, produzieren, korrigieren oder redaktionell abnehmen | [PUZZLE_AUTHORING](ai-workflows/PUZZLE_AUTHORING.md), [redaktioneller Qualitätsvertrag](PUZZLE_QUALITY.md) und deren Pflichtquellen |
| Produktionswerkzeuge, Import, Reparatur, Assets, Proofs | [PUZZLE_PRODUCTION](PUZZLE_PRODUCTION.md), [Werkzeuganleitung](../tools/puzzle_production/README.md), betroffene versionierte Manifeste/Verträge |
| Schritt-4-Integrationscode, Registrierungsbudgets, Prüfkontext, Publikationsguards/Recovery | [PUZZLE_INTEGRATION](PUZZLE_INTEGRATION.md), [ZA1_ADAPTER](ZA1_ADAPTER.md), aktuelles Paket; Soll und ausführbaren Stand unterscheiden |
| Schwierigkeit, Analyse, Kalibrierung, Bewertung oder deren Integration | [SD2](PUZZLE_DIFFICULTY_V2.md), [SD](PUZZLE_DIFFICULTY.md), je nach Änderung [SD2-Analyse](SD2_ANALYZER.md), [SD2-Kalibrierung](SD2_CALIBRATION.md), [SD2-Integration](SD2_INTEGRATION.md), kompatible [SD-Analyse](SD_ANALYZER.md), [0.3-Freeze](SD_CALIBRATION.md), [Daten-/Recoveryvertrag](SD_CATALOG.md), [Paarlinien](PAIRED_LINES.md), Kategorien/ZA-1/Katalogdarstellung |
| CI, Prüfprogramme, Artefakte oder neue Tests | [CI_WORKFLOW_V2](CI_WORKFLOW_V2.md), [CI_POLICY](CI_POLICY.md), tatsächlich betroffene [Native](CI_C_NATIVE_GROUPS.md)-/[Fach](CI_A_SELECTION.md)-/[Browser](CI_B_BROWSER_GROUPS.md)-Verträge |
| Webbuild, Browserpersistenz oder Hosting | [WEB_HOSTING](WEB_HOSTING.md) und betroffene Fachverträge |
| Bestandsbereinigung oder historische CI-Nacharbeit | [DEVELOPMENT_ARCHIVE](DEVELOPMENT_ARCHIVE.md), gegebenenfalls [CI2-Herkunft](CI_SLIMMING.md) und dort gebundene Quellen |

Normale Rätselproduktion ist vom Modellrouting ausgenommen: keine Modell-/Reasoning-
oder Ausführungsempfehlung und keine dafür veranlasste Recherche. Ihre tatsächlichen
Fähigkeiten/Zugriffe bleiben zu prüfen. Ihre Inhalts- und JSON-Verträge ersetzen
das Entwicklungs-Handoff; die allgemeine PR-CI samt aktuellem Paketplan gilt trotzdem.
Separat beauftragte Werkzeug-/Spiel-/CI-Entwicklung folgt dem Entwicklungsworkflow.

## Prüfung und Umgebungen

Die automatische Haupt-CI hat die Checks `docs` und `ci-required`. Sie liefert
den regulären Windows-Spieler bei Entwicklungsänderungen. Reine Dokumente und
reine Rätselproduktion einschließlich ihrer Datenbereinigung bleiben buildfrei;
das gilt auch im Main-Nachlauf. Maßgeblich ist der tatsächliche vollständige Diff.
Zusatzmodule werden im aktuellen `.ci/package.json` begründet ausgewählt. Zehn
Minuten sind ein weiches Ziel, keine harte Laufzeit- oder Artefaktgrößenschranke.
Chromium läuft ausschließlich auf ausdrücklichen manuellen Auftrag. Ausgewählte
Module behalten ihre funktionalen Ergebnis-/Originalprüfungen; deren technische
Dateien sind ohne konkreten befristeten Bedarf kein zusätzlicher Download.

Python 3.11+ und Standardbibliothek genügen für den kleinen lokalen Dokumentkern:

```sh
python -m unittest discover -s tools -p 'test_ci_modular.py' -v
python tools/check_docs.py
```

`tools` und `production.*` aktivieren bei Bedarf die entsprechenden weiteren
Tests. Bildbefehle verwenden die isolierte Pillow-12.3.0-Umgebung gemäß
Werkzeuganleitung. Der Spieler benötigt weder Python noch Produktionspakete.
Native Prüfung verwendet den [Gruppenharness](CI_C_NATIVE_GROUPS.md), isolierte
Projekte/Profile und unter Linux Xvfb/Mesa; echte Windowsstarts bleiben gesondert
belegt. Hashgeprüfte offizielle Archive dürfen wiederverwendet werden, Prüfergebnisse
werden dadurch nicht gecacht. Keine globale Engineinstallation oder echten Saves.

Der [Dokumentvalidator](../tools/check_docs.py) prüft UTF-8/LF, Abschlusszeile,
Whitespace, Version, Pflichtdateien und einfache lokale Inline-Dateilinks.
Anker, externe URLs, vollständige Markdownsyntax und Spielverhalten sind nicht
abgedeckt. Solche Lücken bei relevantem Diff gezielt prüfen; keine routinemäßige
doppelte Vollsuite. Aktuelle CI darf die notwendige Abschlussprüfung liefern.

## Befugnisse, Merge und Betrieb

Befugnisse folgen dem tatsächlichen Auftrag gemäß Workflow. Umsetzung erlaubt
Commit/Push/Draft-PR im Scope; ein Review allein keine Produktkorrektur.
Standardmerge ist Squash mit passender ausdrücklicher oder bedingter Freigabe.
Vor Merge aktuellen Head/Basis, vollständigen Reviewbezug, alle ausgewählten
Pflichtchecks und ausdrücklich vereinbarte Vor-Merge-Abnahmen kontrollieren.
Branchschutz nicht als ungeprüft wirksam voraussetzen oder umgehen.

Ein Merge nach main startet die Package-CI, **kein automatisches Deployment**.
Releases, Tags, manuelles Hosting, Secrets-/Berechtigungsänderungen und produktive
Daten brauchen passenden Auftrag. Der [Webweg](WEB_HOSTING.md) trennt lokale
SSH-/HTTP-Referenz und tatsächliches Zielsetup. Die frühere technische Erlaubnis
einer einzelnen Desktop-/Liveprobe ist keine pauschale Wiederholungsfreigabe.

[ChatGPT-Projekteinstellungen](CHATGPT_PROJECT_INSTRUCTIONS.md) werden separat vom
Nutzer eingesetzt. Ein Git-Merge ändert weder diese Einstellungen noch andere
Projekte oder das zentrale dev-rules-Repository.
