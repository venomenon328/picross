# Projektprofil: picross

**SD / #235 (18.10.2026), SD-A/SD-B/SD-C1 integriert; SD-C2 übernommen, finales Review offen:**
[Rätselschwierigkeit](PUZZLE_DIFFICULTY.md) bindet die wiederholbare
Einstufung 1–5: instrumentierte Logik und Lösungsfluss, begrenzter Größenbeitrag,
feste Grenzen anhand unabhängiger synthetischer Referenzen. Der aktuelle Katalog
muss nicht alle Stufen enthalten und kalibriert keine Skalenenden. Analyse und
Übernahme erfolgen ausdrücklich, außerhalb von CI und Runtime; neue Rätsel
verwenden nach der Umstellung denselben Methodenstand. Automatisierte Tests
dürfen weder den realen Katalog noch daraus kopierte oder abgeleitete Fälle nutzen.
SD-A/SD-B/SD-C liefern Analyse, gebundene Methode und Katalog-/Integrationsweg.
[SD-A](SD_ANALYZER.md) liefert Regeln, synchrone Bewertungsspur und den unveränderten
v1-Einzelbericht. [SD-B](SD_CALIBRATION.md) ergänzt opt-in die eingefrorene Methode
0.3, unabhängige Referenzen und separat prüfbare Ratings. SD-B-R01/SD-B-M01 sind
abgeschlossen; PR #241 ist als `b625cc6af1342eafb2582beb9eec17991ea21a12`
integriert, einschließlich erfolgreicher vollständiger CI.
[SD-C1](SD_CATALOG.md) ergänzt Sidecars, explizite Vorschau/Übernahme und
gemeinsame Register-/Update-/Sync-/Recoverywege. Neue Registrierung oder geänderte
Logik benötigt vollständig geprüftes 0.3; historische Produktionsbindungen bleiben.
SD-C1 ist nach qualifiziertem SD-C-R01/C1 R2 mit PR #242 als
`e93444e5db48e2138d15890e314c60ec4291fea3` integriert; T01 und R01/C1 erfüllt.
Der ausdrücklich gestartete SD-C2-Erstlauf an diesem Quell-/Werkzeugcommit
lieferte 26 vollständig geprüfte Vorschläge: 17 × L3, 8 × L4, 1 × L5,
keine offenen IDs. Nach bestandenem qualifiziertem Vor-Übernahme-Review hat
SD-C2-F01 über den vorhandenen Transaktionsweg alle 26 Bewertungen übernommen.
[C2-Belege und Gategrenze](SD_CATALOG.md) dokumentieren A07 real/K01:
26 Sidecars, zwei Dauerberichte und ausschließlich die Runtime-Difficultyprojektion;
historische Bindungen unverändert, identischer zweiter Aufruf ohne Byte-/Revisionsänderung.
Separates qualifiziertes finales SD-C-R01/C2-Datenreview und Merge bleiben offen;
aktuelle ausgewählte CI und getrennter Selbstreview werden im Draft-PR #243 gebunden.
#238/#235 bleiben offen.

**KE / #233 (17.10.2026), mit PR #234 in `main` integriert:**
Bei Katalog-/Metadatenarbeit zusätzlich [Katalogdarstellung](CATALOG_PRESENTATION.md)
vollständig lesen. Papieretikett mit Größe, Moduspiktogramm, Schwierigkeit und
Status; gezeichnetes Fragezeichen nur für Neu. KE ersetzt gezielt KK-Metadaten,
Fußzeilenstatus und leere Neu-Vorschau, ergänzt gezielte Modus-/Schwierigkeits-
Tooltips und eine minimale kompatible Runtimeprojektion der Schwierigkeit.
KE-T01, KE-R01, KE-M01 und zugehörige Abnahmeentscheidungen bleiben in #233/PR #234
dokumentiert; SD öffnet diese Lieferung nicht erneut.
Der folgende KK-Abschnitt beschreibt die integrierte Ausgangsbasis; die historischen
offenen KK-R01/KK-M01 in #174 werden durch KE weder erledigt noch erneut beauftragt.

**EA / #170:** Abschlussenthüllung auf dem integrierten KB-Stand aus PR #169.
[EA-Prüfzuordnung](EA_VERIFICATION.md) zusätzlich lesen: sofortiger Commit/Save,
transiente 2,15-s-Präsentation, neutrale Blattüberschrift, proportionale Bildfläche,
ursprungsgebundener Reset. EA-T01 verlangt aktuelle technische Lieferung samt
nativer Bewegung, Windows und Browsern; EA-R01 und EA-M01 bleiben getrennt vor Merge.

**KK / #174:** Feste gleiche Katalogkarten/-Grid-Zellen, zweizeilige kleinere
Bakso-Motivüberschrift oder `???`, feste Metadaten/Bildfläche/Fußzeile. Kartenfläche
öffnet; Reset allein oben rechts, bei gültigem fehlerfreiem Neu verborgen, bei
Bearbeitung und Speicher-/Recoveryzuständen erreichbar. Fehler und Backupaktionen
bleiben innerhalb des Bildraums, Kacheltooltips entfallen. KK löst gezielt die
betroffenen KB-D01/D02-Regeln ab; BookButtons, Ressourcen, KAT/EA und Saveverträge
bleiben. [KK-Prüfzuordnung](KK_VERIFICATION.md) zusätzlich zu
[KB](KB_VERIFICATION.md), KAT-1/ZA-1/KAT-2 und EA lesen. KK-T01 bindet technische
Lieferung samt Windows/Web; **KK-R01 und KK-M01 bleiben getrennt vor Merge**.

**ZR / #143 (15.10.2026):** [Zellstriche und Cursorzähler](CELL_DRAG.md) ist als
Sollvertrag freigegeben und im PR #145 umgesetzt. Zähler ab Länge 2 in der aktiven
Hinweisfont, ohne Kasten, am tatsächlichen Cursor; außerhalb des Fensters bleibt er
am inneren Clientrand sichtbar. Begonnene Striche folgen der Maus bis zum Rasterrand,
auch über anderer UI und bei fokussiertem Windows-Fenster außerhalb der Clientfläche.
Fokusverlust bleibt vollständiger Abbruch. Der Vertrag ersetzt gezielt die alten
P1-/Designregeln zu sichtbarer 1, Strichendanker und eingefrorenem Außenendpunkt;
Laufzeit, Spielanleitung und native Hilfe folgen dem ZR-Vertrag.
[Prüfzuordnung](CELL_DRAG_VERIFICATION.md) und #143/#145 führen aktuelle Nachweise;
native Windows-Eingabeprüfung bleibt getrennt von CI und Eigentümerprobe gebunden.
Der Eigentümer hat am 15.10.2026 für diesen Merge ausdrücklich auf das unabhängige
Review und ZR-M01 verzichtet. Beide gelten damit nicht als durchgeführt;
Pflicht-CI und technische native Windows-Probe bleiben erforderlich.

**WEB-1 / #162:** Zusätzlich ist ein statischer Godot-Webentwicklungsweg für
Desktop/Maus in Chromium und Firefox beauftragt. [Webanleitung und Grenzen](WEB_HOSTING.md)
binden Browserpersistenz, getrennten Build, manuelles SSH-Deployment und isolierte
Referenztests. Windows bleibt erhalten; keine endgültige Plattformmatrix oder
Livefreigabe. Bei Web-/Hostingarbeit diese Anleitung zusätzlich vollständig lesen.

**Aktuelle Inhalts-CI (12.10.2026):** Die [CI-Policy](CI_POLICY.md) ersetzt die
unten historisch beschriebenen RP-Korpus-/Zertifikats-Replays. Reine neue
Rätseldateien erhalten nur Pfad-/Dateimodusprüfung und `ci-required`, keine
Tool-/Spiel-/Render-/Exporttests. Sämtliche konkreten Rätselprüfungen erfolgen im
Produktionsauftrag; keine rätselspezifischen Unit-Tests anlegen. Allgemeine
Code-Regressionen verwenden einen festen technischen Testbestand.

[KAT-1](CATEGORIES.md) bindet `content/categories.json`, genau eine Kategorie je sichtbarem Rätsel, Inhaltsregistry v2 und Runtimeprojektion v3 (Loader auch v2, KE) und kategorisierte ZA-1-v2-Exporte. Bei Kategorien-/Katalog-/Adapterarbeit zusätzlich diesen Vertrag und [ZA-1](ZA1_ADAPTER.md) vollständig lesen. [KAT-1-Prüfzuordnung](KAT1_VERIFICATION.md) ergänzt die bestehenden Prüfwege; Saves, Definitionen und Freigabebindungen bleiben unverändert. KAT-2 (#79) verwendet diesen Vertrag für den regulären Katalogstart. Bei Katalogarbeit zusätzlich [KAT-2-Prüfzuordnung](KAT2_VERIFICATION.md) lesen; unabhängiges Review und Eigentümerabnahme KAT2-M01 bleiben vor Merge erforderlich.

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
`content/registry.json`; diese Registry führt den aktuellen Bestand.
[#114](https://github.com/venomenon328/picross/issues/114) ersetzt die
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
bindung und Runtime-Dateien genügen für die abgeschlossene Produktion; keine
dauerhafte Wiederholungspflicht für Bild-/Rasterproduktion oder alte Proofs.
SD-C1 ergänzt dauerhaft erhaltene kompakte Bewertungsdaten und Berichte
für ausdrücklich beauftragte Neueinstufungen aus den vorhandenen Definitionen.

[ZA-1](ZA1_ADAPTER.md) ermöglicht weitere freigegebene Workflow-Inhalte über eine
zentrale Datenregistry mit expliziten Slots, einschließlich Mono/Farbe und Rechtecken.
Künstliche Fixtures bleiben isoliert. Registrierte Pakete tragen ihre eigenen
gebundenen Freigaben; frühere Aussagen zu offenen Einzelfreigaben sind historisch.

[#139 B/C](PAIRED_LINES.md) ergänzt ausdrücklich gewählte Paarlinienprofile,
unabhängige Proof-v3-Prüfung und Schwierigkeit 0.2/R4 innerhalb L5. Authoring
0.5.0 und ZA-1-v4 binden die neue Zertifizierung; Paket A und alte Linienverträge
bleiben erhalten. Diese Werkzeugänderung registriert keine neuen Inhalte.

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
| Zellgesten, Cursorzähler oder deren Raster-/Fenstergrenzen | [ZR-Vertrag](CELL_DRAG.md), aktuelles [Paket #143](https://github.com/venomenon328/picross/issues/143), [Hinweisfont](CLUE_TYPOGRAPHY.md) |
| Zeichensprache, statische Vorschau, Zellanimationen | [UI_DRAWING_STYLE](UI_DRAWING_STYLE.md), betroffene ZS-Verträge/-Nachweise |
| Spriteherstellung, Zellrendering, Cache/Invalidierung, PERF-01 | [CELL_RENDERING](CELL_RENDERING.md), [PERF-A](PERF_A_IMPLEMENTATION.md), [PERF-B](PERF_B_IMPLEMENTATION.md) |
| Sidebar/Zoomnormalisierung | [SL65](SL65_IMPLEMENTATION.md), aktuelle P1-/Saveverträge |
| Neue Rätsel konzipieren, gestalten, produzieren oder redaktionell abnehmen | [KI-Arbeitsanweisung zur Rätselproduktion](ai-workflows/PUZZLE_AUTHORING.md) und deren Pflichtquellen |
| Produktion, Import, Reparatur, Assets, Proofs | [PUZZLE_PRODUCTION](PUZZLE_PRODUCTION.md), [Werkzeuganleitung](../tools/puzzle_production/README.md), betroffene versionierte Manifeste und Paketnachweise |
| Schwierigkeitsanalyse, Kalibrierung, Bewertungsdaten oder deren Katalog-/Integrationsweg | [SD-Fachvertrag](PUZZLE_DIFFICULTY.md), [SD-A](SD_ANALYZER.md), [SD-B](SD_CALIBRATION.md), [SD-C1](SD_CATALOG.md), [Rätselproduktion](PUZZLE_PRODUCTION.md), [Paarlinienvertrag](PAIRED_LINES.md), [Kategorien](CATEGORIES.md), [ZA-1](ZA1_ADAPTER.md), [Katalogdarstellung](CATALOG_PRESENTATION.md), [CI-Policy](CI_POLICY.md) |
| CI, Prüfprogramme, Artefakte, Archivierung | [CI_POLICY](CI_POLICY.md), [Bestandsinventar](DEVELOPMENT_ARCHIVE.md) |

PERF-A/PERF-B sind historische Lieferberichte, keine aktuellen Hersteller- oder
A/B-Vergleichsgates. #70/N70-HIST-01 entfernt deren Reproduktion; die sechs
aktiven Zellatlanten, Import-/Shader-/Rendererverträge und native PERF-B-/PCK-
Prüfungen bleiben unabhängig über `tools/cell_atlas_reference.json` gebunden.

Historische Nachweise führen ihren damaligen Test-/Abnahmestand. Aktuelle
Fachentscheidungen stehen in den verlinkten Verträgen; Auswahl und Aufbewahrung in der
CI-Policy ersetzen deren ältere pauschalen Sechs-Job-/Vollrenderpflichten.
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
Linksdrag ausschließlich für eine konkrete überlaufende Hinweisfolge gemäß
[HN](CLUE_INTERACTION.md), MMB ohne Hinweisnavigation, keine Hand- oder
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
