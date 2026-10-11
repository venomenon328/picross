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
mit ursprünglichem Pfad, Git-Blob, Bytezahl und SHA-256. Es bindet 22 Dateien mit
168.221 Bytes. Wiederherstellung außerhalb des aktiven Trees, beispielsweise:

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
| `game/perf_a/`, `examples/perf_a/`, `examples/perf_b/` | Aktiver Hersteller, native A-Verbraucher, Runtime-Hashbindung und unveränderlicher B-Vergleich samt Rohintervallen. Standardartefakte liefern diese historischen ZIPs nicht erneut aus. |
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
