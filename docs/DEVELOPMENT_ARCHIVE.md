# Entwicklungsbestand und historische Quellen

Inventar zu [#70](https://github.com/venomenon328/picross/issues/70), Quelle
`0f89f08729539bbb4a02a590cbd18e58fbbda305`, Tree
`763855363f4a3e91f2ce7d21008eb819fe8bbc6c`. Größen sind unkomprimierte Git-Blobs,
ohne `.git`, Importcache und lokale Artefakte. Ausgangstree: 1361 Dateien,
190.138.955 Bytes. Die endgültige Differenz und CI-Messungen stehen im Draft-PR.

| Bereich am Ausgangsstand | Dateien | Bytes |
| --- | ---: | ---: |
| `prototypes/p1/` einschließlich aktiver Ressourcen | 213 | 25.311.520 |
| `examples/perf_a/` | 16 | 6.867.718 |
| `examples/perf_b/` | 6 | 1.872.137 |
| `examples/rp*` | 571 | 91.489.330 |
| `examples/vs1/` | 282 | 43.829.417 |
| `docs/design/` | 99 | 19.223.060 |
| `tools/` | 81 | 713.696 |

## Entfernt und unveränderlich erreichbar

[DEVELOPMENT_ARCHIVE.json](DEVELOPMENT_ARCHIVE.json) nennt jede entfernte Datei
mit ursprünglichem Pfad, Git-Blob, Bytezahl und SHA-256. Die erste Bereinigung
bindet 22 Dateien mit 168.221 Bytes; N70-HIST-01 ergänzt die unten gesondert
gebundenen 48 Dateien. Wiederherstellung außerhalb des aktiven Trees, beispielsweise:

```sh
git show 0f89f08729539bbb4a02a590cbd18e58fbbda305:tools/vs1_delivery.py
git archive 0f89f08729539bbb4a02a590cbd18e58fbbda305 prototypes/p1 tools
```

| Bestand | Entscheidung und aktive Alternative |
| --- | --- |
| `tools/gp48_review.py`, `zv50_review.py`, `z2_review.py` | Abgeschlossene Vorher-/Nachherlieferungen; aktuelle GP/H1-, Buch- und Pixelassertions bleiben im regulären Product-/VS2-/ZS2-Pfad. |
| `tools/h1_owner_probe.ps1/.gd` | Historischer künstlicher Linienplayer; aktuelle H1-Logik, Tooltip-/Drag-/Pixelprüfungen bleiben. |
| `tools/vs1_delivery.py`, `vs1_windows_probe.py`, `test_vs1_delivery.py` | Separate abgelöste Studienlieferung; aktueller VS2-PCK-/Windowsprüfer erhält seine eigene sichere ZIP-Extraktion. Spieleridentität/Exportfilter bleiben geprüft. |
| `full_view_study/main.gd`, `main.tscn`, `board.gd` | Abgelöster interaktiver VS1-Player; reguläre Vollsicht ist integriert. Technische Fälle, Katalog und Save-Isolationsinput bleiben. |
| Acht `tests/vs1_*.gd` ohne `vs1_e1_cases.gd` | Studiencaptures, Studienentrypoints und Studienroundtrips; reguläre VS2/GF1/V1-Tests und das weiter benutzte E1-Fachmodul bleiben. |
| `tests/z2_before_capture.gd`, `zv50_capture.gd`, `gp48_capture.gd` | Historische Vergleiche; der weiterhin aktive `z2_capture.gd` und aktuelle Renderprüfungen bleiben. |

Die alten Hilfstests für archivierte Review-ZIPs entfallen. Die aktuelle
UTF-8-/Ressourcenprüfung bleibt in `test_z2_delivery.py`; generische Paket- und
Identitätsregressionen liegen im aktuellen Product-Prüfweg. Historische Programme
nur mit ihrem gebundenen Checkout und damaligem Vertrag ausführen.

## Bewusst erhalten

| Bestand | Bindung und Grund |
| --- | --- |
| `game/data/`, `game/art/`, einschließlich F03/F05/F07 | Unveränderte IDs, Revisionen, bestehende Speicherplätze, Hash-/Proof-/Assetbindungen. Nicht angebotene Großfälle bleiben außerhalb des Spielerexports. |
| `game/study/`, `tests/zs1_tests.gd`, `full_view_study/cases/`, Katalog/Save-Modul | Teile werden von aktuellen ZS2-/VS2-Tests geerbt oder als zertifizierte technische Prüfinputs geladen. Namen allein belegen keine Inaktivität. |
| `game/art/cells/`, `tools/cell_atlas_reference.json`, `tests/perf_b*` | Sechs unveränderte aktive Atlanten/Imports und unabhängige aktuelle Datei-/Pixel-/Mapping-/Cacheprüfung; ohne Hersteller- oder Vergleichsarchive. |
| `examples/rp1` bis `rp6`, `examples/vs1/`, Produktionsmodule und Fixtures | Quellen, Nachweise, Originalbilder, Reparaturarchive, technische Fälle und negative Prüfinputs bleiben vollständig. Die ursprüngliche Sechserproduktion bleibt im Fachreplay. |
| `docs/design/` mit Originalen/Manifesten, aktive Fonts/Nutzungshinweise | Historische und aktuelle Asset-/Quellenbindungen sind nicht sicher durch bloße generierte Ansichten ersetzbar. Keine ungeklärten Bilder gelöscht. |
| [BP-Archiv](design/book_inventory/ARCHIVE.md) | Vorhandene Archivierung von 136 Dateien/161.102.998 Bytes bleibt unverändert gebunden. |
| Historische Prüfberichte und Ownerpläne | Urteile/Abnahmegrenzen bleiben unverändert. Verschobene oder entfernte lokale Quellenlinks zeigen auf den vollständigen Commit vor Cleanup. |

Die RP6-Manifeste enthalten bewusst die ursprünglichen `prototypes/p1/`-Namen.
[current_path()](../tools/project_paths.py) löst ausschließlich diesen Prefix
auf `game/` auf; Namen und erwartete Hashes im Manifest werden nicht umgeschrieben.
Die ursprünglichen HTML-Paaransichten sind ebenfalls hashgebunden und behalten
ihre damaligen Bildpfade. Für sie den [gebundenen ursprünglichen Tree](https://github.com/venomenon328/picross/tree/0f89f08729539bbb4a02a590cbd18e58fbbda305/examples/rp6)
verwenden; aktuelle Spielbilder erzeugt der Product-Harness aus `game/`.

## Grenzen und Restpunkte

Die großen erhaltenen Archive/Bilder dominieren weiterhin die Treegröße. Weitere
Auslagerung benötigt eine belegte gleichwertige dauerhafte Quelle für sämtliche
aktiven Prüfer; sie ist kein sicherer Teil dieser Bereinigung. Kein Git-Rewrite.
Die geschützte Ownerreferenz zu #61 bleibt gemäß [CI-Policy](CI_POLICY.md) gebunden.
PR #54/#69 werden nur nach Diff-/Quellenvergleich als abgelöst geschlossen;
PR #25/#28 und ihre Issues bleiben unverändert. Kein Merge, Release oder Tag.

## Prüfung der offenen Spezifikations-PRs

Verglichen wurden vollständige Bodies und tatsächliche Diffs gegen `main@0f89f087`:

| PR/Quellhead | Vollständige inhaltliche Ablösung |
| --- | --- |
| #54 / `c82ae74f794936bca93d45f5f505ba283e971227` | Alle sechs Dokumentpfade sind in main vorhanden: `UI_DRAWING_STYLE`, `DESIGN_CONCEPT`, `PRODUCT_DEFINITION`, `PROJECT_PROFILE`, `PROTOTYPE_P1`, `Z2_SELECTION`. ZS-D01–D10 und statische Vorschau wurden durch #55/#56 übernommen; konkrete Font-/Stiftwahl, Rand-UI und gerichtetes Timing durch ZS1-E1/E2/E3 und ZS2-E2 entschieden. Miniatur-/Vollsichtfortschreibung ist über #62 integriert. Die alten offenen Auswahl-/Implementierungsstände und parallelen Ausgangseffekte sind ausdrücklich abgelöst. |
| #69 / `4a7573f3adaf7cef6df08adafb6caa767da02ad2` | Alle vier Pfade (`AGENTS`, `CELL_RENDERING`, `SL65_IMPLEMENTATION`, `VS2_OWNER_TRIAL`) sind durch #66 übernommen/fortgeschrieben. PERF-D01–D08 ab der ersten Fachüberschrift sind gegenüber main vollständig gleich, mit genau einer beschlossenen Änderung: 30 statt 20 MB technisches Budget gemäß #68/PERF-B-E1. Hersteller, Runtime, SL-R02 und Eigentümerprobe sind über #66 integriert. |

Integrationscommits: #55 `985cf08e0cd7dda4186c3dd42b5eccbba1b80e3f`,
#56 `fad885344874534629365917a2ab6a8d311cd3a7`,
#62 `e323dcf5c83b085144e61707ef98ecab2bfac39b`,
#66 `0f89f08729539bbb4a02a590cbd18e58fbbda305`.
Beide alten PRs können deshalb gemäß #70 als überholt geschlossen werden;
kein erneuter Merge und keine Branchlöschung. Ihre ursprünglichen Diffs bleiben erreichbar.

## N70-HIST-01: historische Herstellung und Vergleiche

[Eigentümerentscheidung](https://github.com/venomenon328/picross/pull/71#issuecomment-6111613992),
Archivquelle `070d3c291fd83ab380518b01638181c809574c03`, Tree
`43bb6f91550501398f31f95c6deba7d6657d206f`. Der zusätzliche Abschnitt
`historical_cleanup` im JSON-Manifest bindet 48 Dateien / 10.134.723 Bytes
mit Git-Blob, SHA-256 und Bytezahl an genau diesen Quellstand.

Vor Entfernung wurden tatsächliche Aufrufer mit Repositorysuche und Import-/
Preloadprüfung verfolgt. Entfallen: `tools/perf_a.py`, `perf_a_atlas.py`,
`perf_b.py`, `perf_b_report.py`, zwei reine A-Tests, vier A-Godotmodule,
`perf_b_measure.gd`, der isolierte `game/perf_a/`-Bestand einschließlich sechs
Duplikattexturen sowie `examples/perf_a/` und `examples/perf_b/` mit Plänen,
Originalen, Roharchiven und Reproduktionsbelegen. Die Berichte PERF_A/B bleiben
inhaltlich unverändert; ihre Quellenlinks zeigen auf diesen vollständigen Commit.

Die früheren A-Goldfälle versorgen jetzt unabhängig `perf_b_cases.gd` mit
aktueller Identitäts-, Zeit-, Region-, LOD- und Innenflächenprüfung. Product,
Ressourcenprüfer und Windows-/PCK-Prüfer greifen ausschließlich auf die neue
aktuelle Referenz zu. `historical_files()` und `install_historical_probe()`
entfallen vollständig, ebenso A-Flags/-Gates/-Artefaktpfade und reine historische
B-Quell-/Rohintervallvergleiche. Export-Denyregeln und PCK-Gegenprüfungen für
versehentlich wieder eingeführte historische Ressourcen bleiben erhalten.

Wiederherstellung als separater historischer Checkout, beispielsweise:

```sh
git archive 070d3c291fd83ab380518b01638181c809574c03 game/perf_a examples/perf_a examples/perf_b tools/perf_a.py tools/perf_a_atlas.py tools/perf_b.py tools/perf_b_report.py
```

Keine weitere RP-/VS-/ZS-/Sidebar-/Font-/Lizenzquelle entfernt. Aktuelle native
PERF-B-, Bild-, Animation-, Save-/Session-, Paket-/PCK- und Windowsprüfungen
bleiben verbindlich; technische und persönliche Abnahme bleiben getrennt.

## Einmalige Rätselzertifizierung (12.10.2026)

Quelle vor Umstellung: `60886c47098d209c4b7dc7521c3c70ea0aeffcb5`.
Rätselspezifische F01/F02-/Knoblauch-Tests und historische RP4-/RP5-/RP6-/VS1-
Korpusassertions sind aus der automatischen Test-Discovery entfernt; die RP4-/RP5-
CI-Replayjobs entfallen. Allgemeine Funktions-/Sicherheitsfälle verwenden feste
synthetische Inputs. Historische Produktionsmodule, Originalquellen und Proofs
bleiben für gezielte Diagnose erhalten; ihre alten CI-Aufrufe sind keine Pflichten.
Der doppelte Test-ZIP `tests/puzzle_production/fixtures/garlic-r03-reference.zip`
ist über den genannten Commit unverändert erreichbar. Das eigentliche Paket in
`content/authoring/` bleibt bestehen. Keine Rätsel-, Save- oder Freigabedaten geändert.
[Aktuelle Policy](CI_POLICY.md).
