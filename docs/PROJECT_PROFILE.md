# Projektprofil: picross

**Aktuelle Inhalts-CI (12.10.2026):** Die [CI-Policy](CI_POLICY.md) ersetzt die
unten historisch beschriebenen RP-Korpus-/Zertifikats-Replays. Reine neue
Rätseldateien erhalten nur Pfad-/Dateimodusprüfung und `ci-required`, keine
Tool-/Spiel-/Render-/Exporttests. Sämtliche konkreten Rätselprüfungen erfolgen im
Produktionsauftrag; keine rätselspezifischen Unit-Tests anlegen. Allgemeine
Code-Regressionen verwenden einen festen technischen Testbestand.

[KAT-1](CATEGORIES.md) bindet `content/categories.json`, genau eine Kategorie je sichtbarem Rätsel, Registry-/Runtimeformat v2 und kategorisierte ZA-1-v2-Exporte. Bei Kategorien-/Katalog-/Adapterarbeit zusätzlich diesen Vertrag und [ZA-1](ZA1_ADAPTER.md) vollständig lesen. [KAT-1-Prüfzuordnung](KAT1_VERIFICATION.md) ergänzt die bestehenden Prüfwege; Saves, Definitionen und Freigabebindungen bleiben unverändert. KAT-2 (#79) verwendet diesen Vertrag für den regulären Katalogstart. Bei Katalogarbeit zusätzlich [KAT-2-Prüfzuordnung](KAT2_VERIFICATION.md) lesen; unabhängiges Review und Eigentümerabnahme KAT2-M01 bleiben vor Merge erforderlich.

**CI-Folgearbeit #116 (14.10.2026):** Die freigegebene aktuelle Grafikabdeckung
und ihre drei gemeinsamen Fenster-/UI-Konfigurationen stehen in der
[CI-Policy](CI_POLICY.md). Historische erzwungene Raster-Replays entfallen;
aktuelle gezielte Funktions-/Pixelprüfungen bleiben. Der Windows-Debugexport
liefert Ressourcen separat in `picross-p1.pck`; EXE und PCK gehören zusammen.

## Entwicklungsbasis und Grenzen

Das reguläre Spiel liegt unter [game/](../game/README.md). Ausgangspunkt der
Konsolidierung #70 ist `main@0f89f08729539bbb4a02a590cbd18e58fbbda305`, einschließlich
[PR #66](https://github.com/venomenon328/picross/pull/66) (Sidebar und PERF-A/B).
Frühere Draft-/Mergegate-Meldungen zu #47/#55/#56/#62/#66 sind historische Lieferstände.
Die dortigen Abnahmen bleiben an ihre jeweiligen Quellen gebunden.

Der Katalog enthält ausschließlich registrierte Workflow-Inhalte aus
`content/registry.json`, aktuell elf Rätsel einschließlich Warnemünde, Brandenburger Tor und
Kölner Dom. [#114](https://github.com/venomenon328/picross/issues/114) ersetzt die
frühere aktive Reservierung der Prototypen F-01 bis F-09. Definitionen und Reveals
werden nicht mehr mit dem Spieler ausgeliefert. Historische Nachweise bleiben
commitgebunden; eingefrorene Save-Kompatibilitätsinputs liegen nur unter Tests.
Reguläre Rätsel sind gemäß #68 höchstens 50×50 groß. IDs, Revisionen, Dateien und
Freigabebindungen aller Workflow-Rätsel bleiben unverändert. Appidentität, Save-Schema
und Speicherroot bleiben erhalten; verwaiste Savedateien werden nicht angefasst.

Laufende Arbeitsstände und ZIPs der Rätselproduktion liegen in
[content/authoring](../content/authoring/README.md); Wiederaufnahme und Integration
folgen [PUZZLE_AUTHORING](ai-workflows/PUZZLE_AUTHORING.md), Abschnitten 6 und 8.
Die Arbeitsablage ist keine Runtime-Registrierung. Nach Endabnahme und Main-Merge
werden Produktionsdaten nach PUZZLE_AUTHORING §9 entfernt; kompakte Integrations-
bindung und Runtime-Dateien genügen. Keine dauerhafte Wiederholbarkeitspflicht.

[ZA-1](ZA1_ADAPTER.md) ermöglicht weitere freigegebene Workflow-Inhalte über eine
zentrale Datenregistry mit expliziten Slots, einschließlich Mono/Farbe und Rechtecken.
Künstliche Fixtures bleiben isoliert. Registrierte Pakete tragen ihre eigenen
gebundenen Freigaben; frühere Aussagen zu offenen Einzelfreigaben sind historisch.

Aktuelle Bindung: Godot Standard 4.7.2-stable, typisiertes GDScript, native
Windows-Desktopfassung, Maus als verpflichtender Eingabepfad (D-06), Escape als
Gestenabbruch. Keine Wertung, Live-Fehlerhilfe oder Hypothesen. Endgültige Engine,
Sprache, Betriebssystemmatrix, Produktpersistenz und Veröffentlichungsdetails
bleiben offen. Der Entwicklungsablauf erteilt keine Produkt- oder Releasefreigabe.
Die offenen Designarbeiten #25/#28 und ihre Issues bleiben unentschieden.

## Pflichtquellen nach Auftrag

Immer [AGENTS.md](../AGENTS.md), [Workflow](dev-rules/WORKFLOW.md), dieses Profil
und den vollständigen aktuellen Issue-/Paketbody lesen; bei Review/Nacharbeit
zusätzlich PR, tatsächlichen Diff und den konkret benannten Reviewstand.
Bei Vorbereitung noch offener Implementierung/Nacharbeit zusätzlich die
[Modellauswahl](dev-rules/MODEL_SELECTION.md) und den
[Modellkatalog](dev-rules/MODEL_CATALOG.md) vollständig lesen.

| Arbeit | Zusätzlich vollständig lesen |
| --- | --- |
| Produkt, Regeln, Inhalte, Progression, UX/UI, Eingabe, Plattform oder Architektur | [Produktdefinition](PRODUCT_DEFINITION.md) |
| Thematik, Album, Motiventhüllung, UX/UI oder Eingabe/Wertung | [Gestaltungskonzept](DESIGN_CONCEPT.md) |
| Spieltechnik und P1-Verträge | [P1](PROTOTYPE_P1.md), [Issue #5](https://github.com/venomenon328/picross/issues/5) samt Entscheidungen, [Preflight](P1_PREFLIGHT.md), [Spielanleitung](../game/README.md) |
| Zeichensprache, statische Vorschau, Zellanimationen | [UI_DRAWING_STYLE](UI_DRAWING_STYLE.md), betroffene ZS-Verträge/-Nachweise |
| Spriteherstellung, Zellrendering, Cache/Invalidierung, PERF-01 | [CELL_RENDERING](CELL_RENDERING.md), [PERF-A](PERF_A_IMPLEMENTATION.md), [PERF-B](PERF_B_IMPLEMENTATION.md) |
| Sidebar/Zoomnormalisierung | [SL65](SL65_IMPLEMENTATION.md), aktuelle P1-/Saveverträge |
| Neue Rätsel konzipieren, gestalten, produzieren oder redaktionell abnehmen | [KI-Arbeitsanweisung zur Rätselproduktion](ai-workflows/PUZZLE_AUTHORING.md) und deren Pflichtquellen |
| Produktion, Import, Reparatur, Assets, Proofs | [PUZZLE_PRODUCTION](PUZZLE_PRODUCTION.md), [Werkzeuganleitung](../tools/puzzle_production/README.md), betroffene versionierte Manifeste und Paketnachweise |
| CI, Prüfprogramme, Artefakte, Archivierung | [CI_POLICY](CI_POLICY.md), [Bestandsinventar](DEVELOPMENT_ARCHIVE.md) |

PERF-A/PERF-B sind historische Lieferberichte, keine aktuellen Hersteller- oder
A/B-Vergleichsgates. #70/N70-HIST-01 entfernt deren Reproduktion; die sechs
aktiven Zellatlanten, Import-/Shader-/Rendererverträge und native PERF-B-/PCK-
Prüfungen bleiben unabhängig über `tools/cell_atlas_reference.json` gebunden.

Historische Nachweise führen ihren damaligen Test-/Abnahmestand. Aktuelle
Fachentscheidungen stehen in den verlinkten Verträgen; Auswahl und Aufbewahrung in der
CI-Policy ersetzen deren ältere pauschale Sechs-Job-/Vollrenderpflichten.
Bei konkreter historischer Nacharbeit zusätzlich sämtliche dort gebundenen
Quellen und damaligen Issues lesen; Erinnerungen ersetzen keinen Quellenzugriff.

## Aktuelle Spielverträge

[HC / #92](CLUE_TYPOGRAPHY.md) bindet Delight Coffee für Hinweisziffern samt
gemeinsamer gemessener Schrift-/Slot-/Fit-/Draggeometrie und Exportnachweis.
Bei Hinweisarbeit zusätzlich diesen Vertrag lesen. Originalhinweise und
HC-E01-Quellenentscheidung werden mitgeliefert; HC-M01 und unabhängiges Review
bleiben vor Merge offen. Historische Chalkboard-/24/18-Maße sind abgelöst.

P1 bleibt der Vertragsname. Vollsicht und Hinweise sind nach VS2 integriert:
Sammlungsstart, Rasteransicht/Gesamtansicht, passives proportionales Miniaturbild,
MMB ausschließlich für eine konkrete überlaufende Hinweisfolge, keine Hand- oder
Raster-/Miniaturverschiebung. Raster samt Außenrahmen bleibt innerhalb der
angebotenen Fitgrenze sichtbar. Die sechs Sidebaraktionen stehen in 2×3 mit
gezeichneten Rahmen; UI 100/125 % und Rückweg bleiben erreichbar.

Schema 1 und Appname `picross · P1` bleiben erhalten. Saves liegen unter
`user://p1/saves/`. Vollständige Validierung geht der Normalisierung alter
Ansichtswerte voraus; `overview=false`, gültiger Zoomwunsch, Inhalte, History/Redo
und Recoverygrenzen bleiben gemäß SL65/P1 erhalten. Keine Tests an echten Saves.

Startzustandsschutz und Hinweiszustände nach GP48, statische 56-%-Vorschau,
gerichteter Strichaufbau und Gegentasten-Abbruch nach ZS2 bleiben aktiv.
Spielaktion, History, Save und Abschluss werden durch Animation nicht verzögert.
Chalkboard-/Bakso-Nutzungshinweise und OFL-Texte sind mitzuliefern; keine
unbegründeten Lizenzannahmen. Details stehen in den Fachverträgen, keine neue
Abnahme wird aus alten grünen Läufen oder Standbildern abgeleitet.

## Befugnisse und Abnahme

Zielbranch `main`, reguläre Arbeit auf dem beauftragten Branch; Standardmerge
Squash nur mit passender ausdrücklicher/bedingter Freigabe. #70 beauftragt
Commit, Push und Draft-PR, keinen Merge. Kein Force-Push, Branchlöschen, Release,
Tag, Hosting, Branchschutz-/Secretwechsel oder kostenpflichtiger Dienst.
Technischer Branchschutz ist nicht als wirksam verifiziert; keine Schutzregeln umgehen.

`docs` und `ci-required` sowie alle ausgewählten Fach-/Produkt-/Toolchainjobs
müssen für den finalen Head/zugehörigen Test-Merge tatsächlich erfolgreich sein.
Head, Basis, Checkout und Run auseinanderhalten. Fehlend, abgebrochen oder
übersprungen ist bei Pflichtjobs kein Pass. Vollständiger Diff und getrennter
Selbstreview sind erforderlich; eigener Selbstreview ist keine unabhängige Zweitprüfung.
Persönliche Abnahme, technische Prüfung, Mergefreigabe und Release sind getrennt.
Die abgeschlossene Produktionsphase #34 wird nicht erneut geöffnet; offene
persönliche Befunde aus #24 werden durch Cleanup nicht abgenommen.

## Dokumentprüfung und Umgebungen

Python 3.11+, Standardbibliothek für den schnellen Pfad. Kleine lokale Prüfungen
in geeigneter vorhandener Umgebung sind erlaubt; aktuelle CI darf die
Abschlussprüfung liefern. Keine ritualisierte doppelte Vollprüfung.
Unbekannte Ressourcen-/Konfigurationsgrenzen prüfen; globale Workstation-
Einstellungen sind nicht als geprüft bestätigt.

```sh
python -m unittest discover -s tools -p 'test_*.py' -v
python tools/check_docs.py
```

Der [Dokumentvalidator](../tools/check_docs.py) prüft Pflichtdateien, UTF-8/LF,
Abschlusszeile, Whitespace, Versionsformat und einfache lokale Inline-Links.
Externe URLs, Anker, Referenzlinks und vollständige Markdownsyntax sind nicht
abgedeckt. Die [Regelkopie](DEV_RULES_ADOPTION.md) bei deren Aktualisierung separat
gegen den Quellcommit prüfen; keine ungefragte zentrale Regeländerung.

## Produktionswerkzeuge

Eigenes headless Werkzeug unter `tools/puzzle_production/`, Python 3.11+;
Bildbefehle nutzen Pillow exakt 12.3.0. Fachtests unter `tests/puzzle_production/`
verwenden feste synthetische Inputs für Solver, unabhängigen Verifier, Import,
Reparatur, Export, Registrierung und abgeschlossene Integrationsbindungen.
Der Spieler benötigt weder Python noch Produktionspakete. Aktuelle Befehle und
Formate stehen in der [Werkzeuganleitung](../tools/puzzle_production/README.md)
und [ZA-1](ZA1_ADAPTER.md). CI-Auswahl und Nachweise regelt ausschließlich die Policy.

```sh
python3 -m unittest discover -s tests/puzzle_production -p 'test_*.py' -v
python3 -m tools.puzzle_production.benchmark --output-dir artifacts/puzzle-production
```

Abgeschlossene RP1–RP6-Korpusproduktionen, Codec-/Reparaturstudien und damalige
Abnahmen sind [historische Quellen](DEVELOPMENT_ARCHIVE.md). Sie sind keine
aktuellen Start-, Replay- oder CI-Pflichten. Allgemeine Code- und Sicherheits-
regressionen bleiben bis zu einer gesonderten Umfangsentscheidung aktiv.

## Toolchain, Product und Betriebswirkung

[Preflight](P1_PREFLIGHT.md) bindet offizielle Editor-/Exportarchive mit
vollständigen SHA-256-Hashes. Keine globale Engineinstallation, keine gecachten
Prüfergebnisse. Bei Preflightänderungen echten Download-/Import-/Test-/Start-/
Exportweg nachweisen. Der [Product-Harness](../tools/p1_product.py) kopiert `game/`
in ein temporäres Projekt und isoliert APPDATA/LOCALAPPDATA beziehungsweise XDG.
Tests erhalten zusätzliche temporäre Speicherroots. Native Windows-Prüfungen
sind erlaubt. Linux-Renderprüfung benötigt Xvfb/Mesa, Bildprüfung eine eigene
Pillow-12.3.0-venv. Grenzen, Auswahl und Aufbewahrung stehen in der CI-Policy.

```powershell
$gameCache = Join-Path $env:TEMP 'picross-p1-preflight-cache'
python tools/p1_product.py --cache-dir $gameCache --output-dir artifacts/p1-product
```

Alle vier ergänzenden Bereiche sind lokal standardmäßig aktiv, CI übergibt jede Auswahl explizit.
Der allgemeine Harness verwendet sechs feste synthetische Muster T-01/T-02/T-04/
T-06/T-08/T-09, unabhängig vom Produktionsbestand. Der weiterhin `--pilots` genannte
Bereich prüft vier dieser technischen Fälle; echte Rätsel werden nicht replayt.
Spielerexport und tatsächlicher PCK-Inhalt sind zusätzlich zu Tests zu kontrollieren.
Laufzeiten und Artefaktgrößen werden ohne feste CI-Optimierungsbudgets gemessen. Historische Studien-/Vergleichspakete entstehen im Standardpfad
nicht neu. Notwendige Referenzen, Quellen, Lizenzen und Prüfinputs bleiben erhalten.

Keine Laufzeitdienste eingerichtet. Nur isolierte temporäre Prüfdaten, keine
echten Spielstände, privaten Daten oder Secrets. Öffentliche gebundene
Godot-Archive dürfen geladen werden. Neue Assets/Abhängigkeiten auf Notwendigkeit
und Nutzungsrechte prüfen. CI arbeitet mit lesenden Repositoryrechten.
[ChatGPT-Projekteinstellungen](CHATGPT_PROJECT_INSTRUCTIONS.md) setzt der Nutzer
separat ein. Frühere Paketchronologie ist im
[gebundenen Profil vor Cleanup](https://github.com/venomenon328/picross/blob/0f89f08729539bbb4a02a590cbd18e58fbbda305/docs/PROJECT_PROFILE.md) erreichbar.
