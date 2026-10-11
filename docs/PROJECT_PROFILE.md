# Projektprofil: picross

## Entwicklungsbasis und Grenzen

Das reguläre Spiel liegt unter [game/](../game/README.md). Ausgangspunkt der
Konsolidierung #70 ist `main@0f89f08729539bbb4a02a590cbd18e58fbbda305`, einschließlich
[PR #66](https://github.com/venomenon328/picross/pull/66) (Sidebar und PERF-A/B).
Frühere Draft-/Mergegate-Meldungen zu #47/#55/#56/#62/#66 sind historische Lieferstände.
Die dortigen Abnahmen bleiben an ihre jeweiligen Quellen gebunden.

Der Katalog enthält genau F01, F02, F04, F06, F08 und F09. Nach der
[Eigentümerentscheidung #68](https://github.com/venomenon328/picross/issues/68#issuecomment-6109644419)
sind reguläre Rätsel höchstens 50×50 groß. F03/F05/F07 bleiben als historische
Dateien mit bestehenden Speicherplätzen und Nachweisbindungen erhalten. 100×100
ist eine optionale theoretische Stressgröße. Die Bereinigung ändert keine Rätsel,
IDs, Revisionen, Spielregeln, Save-Schemata oder vorhandenen Spielstände.

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
| Spieltechnik und P1-Verträge | [P1](PROTOTYPE_P1.md), [Issue #5](https://github.com/venomenon328/picross/issues/5) samt Entscheidungen, [Preflight](P1_PREFLIGHT.md), [Spielanleitung](../game/README.md), historische [P1.1](P1_1_VERIFICATION.md), [P1.2](P1_2_VERIFICATION.md) und [P1.3](P1_3_VERIFICATION.md) |
| Zeichensprache, statische Vorschau, Zellanimationen | [UI_DRAWING_STYLE](UI_DRAWING_STYLE.md), betroffene ZS-Verträge/-Nachweise |
| Spriteherstellung, Zellrendering, Cache/Invalidierung, PERF-01 | [CELL_RENDERING](CELL_RENDERING.md), [PERF-A](PERF_A_IMPLEMENTATION.md), [PERF-B](PERF_B_IMPLEMENTATION.md) |
| Sidebar/Zoomnormalisierung | [SL65](SL65_IMPLEMENTATION.md), aktuelle P1-/Saveverträge |
| Produktion, Import, Reparatur, Assets, Proofs | [PUZZLE_PRODUCTION](PUZZLE_PRODUCTION.md), [Werkzeuganleitung](../tools/puzzle_production/README.md), betroffene versionierte Manifeste und Paketnachweise |
| CI, Prüfprogramme, Artefakte, Archivierung | [CI_POLICY](CI_POLICY.md), [Bestandsinventar](DEVELOPMENT_ARCHIVE.md) |

Historische Nachweise führen ihren damaligen Test-/Abnahmestand. Aktuelle
Fachentscheidungen stehen in den verlinkten Verträgen; Auswahl und Budgets in der
CI-Policy ersetzen deren ältere pauschale Sechs-Job-/Vollrenderpflichten.
Bei konkreter historischer Nacharbeit zusätzlich sämtliche dort gebundenen
Quellen und damaligen Issues lesen; Erinnerungen ersetzen keinen Quellenzugriff.

## Aktuelle Spielverträge

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

## RP-1/RP-2-Prüfkern

Eigenes Werkzeug unter `tools/puzzle_production/`, Fachtests unter
`tests/puzzle_production/`; kein P1-Code übernommen. Versionierter Logik-/Profil-/
Nachweisvertrag, Zell-Domains, headless CLI und unabhängiger Blockpositions-Prüfer
stehen in der [Anleitung](../tools/puzzle_production/README.md).
RP-2 unterstützt 1..8 Vordergrundfarben plus Leer, gemeinsame Farblinienlogik und
partielle Domainverluste. Alte Monoformate/-hashes bleiben erhalten; Farbformate
und Profile sind separat versioniert. Keine Laufzeitabhängigkeit des Spiels vom Produktionswerkzeug.

```sh
python3 -m tools.puzzle_production solve --input tests/puzzle_production/fixtures/deductive.json --output-dir artifacts/rp1-example
python3 -m tools.puzzle_production verify --input tests/puzzle_production/fixtures/deductive.json --proof artifacts/rp1-example/proof.json
python3 -m tools.puzzle_production solve --input tests/puzzle_production/fixtures/color-four.json --output-dir artifacts/rp2-example
python3 -m tools.puzzle_production verify --input tests/puzzle_production/fixtures/color-four.json --proof artifacts/rp2-example/proof.json
python3 -m unittest discover -s tests/puzzle_production -p 'test_*.py' -v
python3 -m tools.puzzle_production.benchmark --output-dir artifacts/puzzle-production
```

[Eigene CI](../.github/workflows/puzzle-production.yml), Job `puzzle-production`:
Ubuntu 24.04, Python 3.11+, lesende Rechte, 15 Minuten. Fachoracles,
Negativtests und Referenzläufe bleiben für RP-3 vollständig aktiv. Referenzbudgets:
120 Sekunden je Fall inklusive frischer Prüfung, 512 MiB gemessener Peak-RSS je
Linux-Prozess; separates hartes virtuelles Speicherlimit 1024 MiB im Benchmark.
Fehlende Messung oder Abbruch ist keine Abnahme. Reports und geprüfte Nachweise
unter `artifacts/puzzle-production/` werden als CI-Artefakt mit Commitbindung bereitgestellt.
Historische RP-2-Ergebnisse/Integrationsbindung stehen im abgeschlossenen PR #43.
#41/#42/#43 sind integriert;
die alte gestapelte Basis gehört ausschließlich zur RP-1-Historie. Mono-Balken-/
Langlinienreferenzen bleiben erhalten; gemeinsame CI ergänzt vierfarbige
40×40-/100×100-Fälle und schwierige farbige 100er-Linien mit frischer Prüfung.
Bestehende `docs`-/`product`-/`preflight`-Workflows bleiben aktiv.
Eine reale Motiv-/Spielprobe ist für den reinen RP-1/RP-2-Logikkern nicht anwendbar.

## RP-3-Bildimport und früher P1-Export

Python 3.11+ und **Pillow exakt 12.3.0** in einer eigenen venv; nur Bildbefehle
laden Pillow. Die bisherigen Kernbefehle bleiben ohne Zusatzpakete nutzbar.
Installation und vollständiger Daten-/Normalisierungsvertrag stehen in der
[Werkzeuganleitung](../tools/puzzle_production/README.md), reale Dateien in
[examples/rp3](../examples/rp3/README.md). Keine Modell-API oder Laufzeitdienste.

```sh
python3 -m venv .venv/rp3
.venv/rp3/bin/python -m pip install --only-binary=:all: -r tools/puzzle_production/requirements-image.txt
.venv/rp3/bin/python -m tools.puzzle_production.rp3_demo --output-dir artifacts/rp3-demo
```

Unter Windows die venv über `.venv/rp3/Scripts/python.exe` verwenden. Die
betroffenen CI-Jobs `puzzle-production` und `product` installieren diese separate
Anforderung ausschließlich in einer temporären venv. `docs` und `preflight`
benötigen weiterhin nur Standardbibliothek. Vollständige Fachtests benötigen
wegen der neuen Bildtests die Image-Umgebung.

Grenzen: PNG/JPEG, 32 MiB kodiert, 8 Millionen dekodierte Pixel, 8192 je
Quellachse, 1..8 Varianten, 1..100 Zielzellen je Achse und 1..8 Vordergrundfarben
plus Leer. P1-Adapter v1 bleibt quadratisch monochrom mit F-04/SVG. RP-6 ergänzt
versioniert v2: quadratische F-05 bis F-09, bis vier Farben plus Leer, lokale
begrenzte PNG-/SVG-Ressourcen und vollständiger RP-5-Replay für Reparaturen. Kein öffentlicher Import oder Saveformatwechsel.
Die Exportfreigabe rekonstruiert Quelle/Raster/Hinweise und prüft die geschriebene
Nachweisdatei unabhängig neu; bewiesene Enddomains müssen der Matrix entsprechen.

RP3-A01 bis A06 einschließlich unabhängigem technischem/visuellem Review R2
sind im integrierten PR #44 abgeschlossen. Die dort gebundenen Fachtests/Benchmark,
`docs`, `product`, `preflight`, Diffcheck, Windows-Artefakt und Sichtkontrolle
bleiben historische Nachweise dieses Stands. Die reguläre Hauptszene wird
mit F-04 in drei isolierten Prozessen bearbeitet, abgeschlossen und wieder geladen;
echte Renderbilder prüfen eigene falsche Einträge und die Spoilergrenze.
Die RP-6-Abnahmeentscheidungen sind im integrierten PR #47 gebunden.
Windows-Export, Windows-Start und persönliche Lösung bleiben getrennte Nachweise.
Die Machbarkeitsphase #34 ist seit 07.10.2026 abgeschlossen; wirtschaftliche
Serienproduktion und weitergehende Produktionsoberfläche bleiben Folgearbeiten.

## RP-4-Regression und Herkunftsnachweis

R1-N1 zu PR #45 prüft Neuerzeugungen der drei eigenen Illustrationen auf exakte
Dateimenge, Modus, Abmessungen und dekodierte Pixel. Gespeicherte Originale,
Erzeugungsskript und Input-Lock bleiben bytegebunden. Der tatsächliche ursprüngliche
Commitpayload wird als kleine Datei bereitgestellt und mit seinem Git-Objekthash,
Tree und unverändertem Produktionsreport verbunden; [Prüfzuordnung](RP4_VERIFICATION.md).

Der aktuelle Linux-Fachjob bleibt für Produktionsänderungen aktiv. Ein begrenzter
Windows-x64-Job im Fachworkflow führt nur `test_rp4*.py` aus: Python 3.12.10,
offizielles Pillow-12.3.0-Wheel in temporärer venv, `contents: read`, zehn Minuten
hartes Joblimit. Er verlangt erfolgreiche aktuelle Tests ohne erneute Produktion
des alten R1-Fehlers. Die isolierte historische Reproduktion bleibt ein gezielter
Diagnoseweg. Tatsächliche Laufzeit-/Codec-
daten und Head/Basis/Checkout/Run stehen im kleinen Nachweisartefakt. Kein Windows-
Benchmark, keine zusätzliche P1-/Eigentümerprobe. R2 hat beide R1-Befunde
und die aktuellen technischen Checks bestätigt; RP-4 ist über PR #45 integriert.
Die eingefrorenen Daten und historischen offenen Felder behalten ihre Bindung.

## RP-5-Reparaturprüfung

Eigener additiver Reparatur-/Replayvertrag nach dem bestehenden Importprüfpfad;
Mono und Farbe, einzelne Zelländerungen, harte Masken und separate kumulative
Änderungs-/Vorschlags-/Kandidaten-/Linien-/Zeitgrenzen. Alle Parameter wurden vor
dem ersten Vergleichslauf in Commit `55f9e0f` fixiert. Endnachweise entstehen
frisch vom unbekannten Raster und werden unabhängig geprüft; keine neue Regel
im Zertifizierer. Der v1-P1-Export weist Reparaturbundles weiterhin zurück. RP-5 selbst
veränderte keine P1-Datei; RP-6 ergänzt dafür den getrennten v2-Adapter.

```sh
python -m tools.puzzle_production.rp5 verify --output-dir artifacts/rp5-replay
python -m unittest discover -s tests/puzzle_production -p 'test_repair.py' -v
python -m unittest discover -s tests/puzzle_production -p 'test_rp5.py' -v
```

Gleiche isolierte Image-Umgebung. Job `rp5-repair` auf Ubuntu 24.04,
lesende Rechte, zehn Minuten hartes Joblimit, sechs Minuten Schrittlimit;
Paketreplay kooperativ 300 s, Einzelbundle-Prüfung 60 s / 1000000 Linien.
Der Job entpackt das bytegebundene Originalarchiv mit Mengen-/Größen-/Pfadkontrolle,
prüft alle Kandidaten/Eltern/Proofs, 48 Originalresultate und neun Sichturteile.
Source-Head, Basis, Test-Merge und Run stehen im Artefakt. Gemeinsamer Fachjob
behält sämtliche Oracles, sechs Referenzen, RP-3-Demo und RP-4-Replay;
Windowsregression, `docs`, `product` und `preflight` bleiben aktiv.

RP5-A01 bis A06 und unabhängiges technisches/visuelles Review R1 sind
im integrierten PR #46 abgeschlossen. Historische Baseline-/Reviewfelder
bleiben unverändert; eigene Sichtung ersetzt weiterhin keine Zweitprüfung. Persönliche Lösung und finale Pilotabnahme gehören zum historischen RP-6-Auftrag;
dessen Entscheidungen stehen im integrierten PR #47. Die Machbarkeitsphase #34 ist seit 07.10.2026 abgeschlossen; wirtschaftliche
Serienproduktion und weitergehende Produktionsoberfläche bleiben Folgearbeiten.

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

Alle Bereiche sind lokal standardmäßig aktiv, CI übergibt jede Auswahl explizit.
Der aktuelle Katalog hat vier Produktionspiloten F04/F06/F08/F09; die ursprüngliche
Sechserproduktion einschließlich F05/F07 bleibt vollständig im Fachreplay geprüft.
Spielerexport und tatsächlicher PCK-Inhalt sind zusätzlich zu Tests zu kontrollieren.
Technische Daten höchstens 30.000.000 Bytes, gemeinsam mit Spielerpaket höchstens
75.000.000 Bytes. Historische Studien-/Vergleichspakete entstehen im Standardpfad
nicht neu. Notwendige Referenzen, Quellen, Lizenzen und Prüfinputs bleiben erhalten.

Keine Laufzeitdienste eingerichtet. Nur isolierte temporäre Prüfdaten, keine
echten Spielstände, privaten Daten oder Secrets. Öffentliche gebundene
Godot-Archive dürfen geladen werden. Neue Assets/Abhängigkeiten auf Notwendigkeit
und Nutzungsrechte prüfen. CI arbeitet mit lesenden Repositoryrechten.
[ChatGPT-Projekteinstellungen](CHATGPT_PROJECT_INSTRUCTIONS.md) setzt der Nutzer
separat ein. Frühere Paketchronologie ist im
[gebundenen Profil vor Cleanup](https://github.com/venomenon328/picross/blob/0f89f08729539bbb4a02a590cbd18e58fbbda305/docs/PROJECT_PROFILE.md) erreichbar.
