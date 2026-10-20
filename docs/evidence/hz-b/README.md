# HZ-B · Windows- und Chromium-Originalbelege

Diese unveränderten Originaldateien ergänzen [HZ-B-T01](../../HZ_B_VERIFICATION.md)
und [Draft-PR #289](https://github.com/venomenon328/picross/pull/289).
Die abschließende Lieferhead-/CI-Bindung steht im PR; die folgenden Producer
werden nicht auf spätere Dokumentationsstände umetikettiert.

## Pflicht-CI am Runtime-Head

Das unveränderte [CI-Abschlussergebnis](ci-result-dbcf091-2.json) bindet
`dbcf091ef050630003ef8f82307c4e865515897c`: `accepted: true`, Gate-Versuch 2.
Alle sieben ausgewählten nativen Gruppen bestanden in Product-Versuch 2;
1.032 native Technikdateien wurden validiert. Chromium-Versuch 1 bestand
alle 32 Szenarien. Der erste fehlgeschlagene Product-Versuch bleibt im PR
mit seinen tatsächlichen Aufnahmewerten dokumentiert. Die CI des späteren
reinen Dokumentations-/Archivcommits wird im PR separat gebunden.

## Windows-Spieler/PCK und Controls

- Quellhead und tatsächlicher lokaler Checkout: `dbcf091ef050630003ef8f82307c4e865515897c` (sauber).
- Basis: `e9a957d1513c9c77281e738c4eb22b161bee2342`.
- Tatsächlicher CI-Checkout: `1a0e188cc388c6a79b146cd1e0b4f5d53b9d4720`.
- Head-/Test-Merge-Dateibaum: `2050b6737e978e0a72047f16132638ca88f4f315` (identisch).
- [CI 39496177761](https://github.com/venomenon328/picross/actions/runs/39496177761), Product-Versuch 2,
  Job `118901905872` erfolgreich.
- Originalartefakte: [Windows-Spieler](https://github.com/venomenon328/picross/actions/runs/39496177761/artifacts/12302954479),
  [native Technikbelege](https://github.com/venomenon328/picross/actions/runs/39496177761/artifacts/12302358773).
- Godot `4.7.2-stable (official)`, Windows, NVIDIA GeForce RTX 3070.
- Original-EXE ohne Testargumente gestartet; ausschließlich deren eigenes HWND aufgenommen.
- Tatsächliches heruntergeladenes PCK: 192 Prüfungen im ersten Prozess,
  192 im getrennten Neustartprozess, jeweils ohne Fehler.
  Die Konturbytes aller drei Konfigurationen stimmen zwischen den Prozessen überein.
- Elf native Katalogmodi: 7417 Prüfungen, darunter KK/HZ 3194, keine Fehler.
- Vor Verwendung alle 1032 gelieferten nativen CI-Technikdateien hashgeprüft.

| Archiv | Originaldateien | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| [windows-pck-dbcf091.zip](windows-pck-dbcf091.zip) · [Inventar](windows-pck-dbcf091-inventory.json) | 48 | 39447229 | `f17a4562b622ecb766fc8c87dad1a9b63ce3575135388976a550f234b7b98f66` |
| [windows-pck-restart-dbcf091.zip](windows-pck-restart-dbcf091.zip) · [Inventar](windows-pck-restart-dbcf091-inventory.json) | 23 | 38251979 | `16e8db6dbe2134947fd55bf9a6e2ede96b6955323582e4eebaacd5c4700387dd` |
| [windows-controls-dbcf091.zip](windows-controls-dbcf091.zip) · [Inventar](windows-controls-dbcf091-inventory.json) | 62 | 16752641 | `fd1243b91926073297e337172e27cda2f75b0227f1d0bbf355385810a01f9e2b` |
| [windows-regressions-a3427e9.zip](windows-regressions-a3427e9.zip) · [Inventar](windows-regressions-a3427e9-inventory.json) | 125 | 493379 | `e4feb16733eb3a1463bdff97c6a87bfbaf29d7678d485b0985e3d250697b0f4d` |
| [windows-graphics-dbcf091.zip](windows-graphics-dbcf091.zip) · [Inventar](windows-graphics-dbcf091-inventory.json) | 42 | 279872 | `37cf85429baa9137cfc5ec78c029d7a7ba97d548f7d695d3118357ae56d45e39` |
| [chromium-controls-dbcf091.zip](chromium-controls-dbcf091.zip) · [Inventar](chromium-controls-dbcf091-inventory.json) | 23 | 15268105 | `8496124165397138abd44b14d7724faf2a86f41262fef6a01120f29c3cb3d7a7` |
| [windows-tooltip-first-dbcf091.zip](windows-tooltip-first-dbcf091.zip) · [Inventar](windows-tooltip-first-dbcf091-inventory.json) | 6 | 5310254 | `dffc586f48e932cb9314bb9a14dbbcc58c9ff05fb292d6feefc27fe667f8bd24` |

`windows-pck-dbcf091.zip` enthält die vollständige `windows-binding.json`,
die Bindung beider Godot-EXEs an das offizielle verifizierte Archiv, den regulären
EXE-Start, sämtliche PCK-Originalansichten des ersten Prozesses, die externen
synthetischen Eingänge und alle nativen Prozesslogs. Die Bindung enthält
Artifact-IDs/-Digests, EXE-/PCK-Hashes, Toolchainidentität, Prüfphasen und sämtliche
lokalen Dateihashes.

`windows-pck-restart-dbcf091.zip` erhält zusätzlich alle Originalbilder und den
Bericht des getrennten PCK-Neustarts. Beide Archive bleiben unter 50 MB; kein
Bild wird dafür verkleinert, bearbeitet oder ausgelassen.

`windows-controls-dbcf091.zip` enthält sämtliche 48 HZ-A-/HZ-B-Controloriginale
und die vollständigen nativen Katalogberichte. Darin liegen die 30 HZ-B-Bilder:
Karten, Sortier-/Ansichtsmenüs, Checkboxen, Dialoge, vollständige Iconfamilie,
echter Button-Hover/Druck und echter Scrollgriff-Hover/Druck, jeweils in
1280×720/UI125, 1920×1080/UI100 und 2560×1440/UI125. Die bestehenden HZ-A-
Originale belegen zusätzlich lange Kategorien, native Scroll-/Tooltipwege und
Textbudgets. Weitere unveränderte Katalogbilder bleiben lokal und in
`windows-binding.json` hashgebunden; die vollständigen CI-Pflichtbilder liegen
im verlinkten Product-Artefakt.

Nach Entpacken liegen Controlbilder unter `source-native/kat2/hz-*.png`,
PCK-Ansichten unter `native/` beziehungsweise `native-restart/` und der reguläre
Start unter `direct-start.png`. Der native Menütest prüft den freien Hakenbereich
auch bei tatsächlich per Tastatur hervorgehobener Zeile. Popup-Scrollzustände
werden durch echte Zeigerbewegung und gehaltene Maustaste erzeugt.

## Aufbewahrter erster Windows-Tooltipbefund

`windows-tooltip-first-dbcf091.zip` erhält den ersten lokalen KK-Bericht,
Prozesslog, alle drei zugehörigen Originalbilder und die CI-Paketbindung.
Von 3.194 Prüfungen schlug dort ausschließlich die bestehende Prüfung
`KK real reset hover retains tooltip` fehl: Der Tooltip fehlte bei
1280×720, war in beiden größeren Originalbildern sichtbar. Die Prüfung
wartet unverändert 0,8 Sekunden; eine konkrete Ursache wird nicht als bewiesen
behauptet. Der vollständige Windows-/PCK-Lauf wurde ohne Quelländerung in neuen
isolierten Profilen wiederholt und bestand anschließend sämtliche Prüfungen.
Die oben archivierten Abschlussbelege stammen aus dieser Wiederholung.
Der fehlgeschlagene Erstlauf wird ausdrücklich nicht als bestanden umgedeutet.

## Aktuelle Chromium-Originale

`chromium-controls-dbcf091.zip` erhält alle neun HZ-B-Originalbilder aus
Produzentenversuch 1 von CI 39496177761 sowie dessen unveränderte JSON-Berichte,
Manifeste und Prozesslogs. Alle 32 Szenarien der fünf Gruppen bestanden. Das
vollständige [CI-Browserartefakt](https://github.com/venomenon328/picross/actions/runs/39496177761/artifacts/12302275039)
wurde heruntergeladen und mit `web_tests.results.validate_browser` erneut
validiert: alle 58 Originaldateien, Hashes und Quell-/Export-/Versuchsbindungen
stimmen. Das kleinere Repository-Archiv enthält die neun HZ-B-Bilder; weitere
Szenariobilder bleiben im vollständigen CI-Artefakt und lokal erhalten.
Die unveränderten Berichte behalten auch deren ursprüngliche Dateihashes.

## Aktueller Windows-Grafiknachweis

`windows-graphics-dbcf091.zip` erhält zusätzlich die Berichte und Logs des
sauberen aktuellen Heads `dbcf091ef050630003ef8f82307c4e865515897c`.
Die gesamte Graphics-Gruppe bestand in 489,09 Sekunden einschließlich
kontrollierter und tatsächlicher Echtzeit-Schraffur, Pixelorakeln, HF 2.531,
HN 31.495 und PERF-B 332 Prüfungen. Der CI-Aufnahmefehler des ersten Versuchs
reproduzierte sich damit auf der tatsächlichen Windows-GPU nicht.
Die aktuelle Pflicht-CI bleibt unabhängig davon erforderlich.

## Zusätzliche geschützte Windows-Regressionen

`windows-regressions-a3427e9.zip` behält den separaten sauberen Producer
`a3427e90bd85bca4037d9f5252a06c5f592923a7` auf derselben Basis.
Core, Completion und Graphics bestanden in 642,31 Sekunden:
17.106 Kernprüfungen, EA 2.327 und zehn Neustartprüfungen, HF 2.531,
HN 31.495, PERF-B 332; keine Fehler.

Die späteren Runtime-Änderungen betreffen ausschließlich Popup-Scrollzustände
und die zusätzliche Zeilenkontur im Hakenbereich; der aktuelle Windows-Katalog-
und PCK-Lauf prüft diese Änderungen. Der zusätzliche aktuelle Grafiklauf ist
oben gesondert gebunden. Die älteren geschützten Regressionen werden
nicht als unter `dbcf091` ausgeführt ausgegeben. Das Archiv erhält ihre Berichte
und Logs; zusätzliche Pixelbilder bleiben lokal erhalten.

## Gates und Quellen

Die Reproduktion verwendet den eingecheckten
[Windows-/PCK-Prüfer](../../../tools/hz_windows_probe.py), isolierte Profile und
synthetische Definitionen. Keine gepackte UI-/Font-/Iconressource wird ersetzt.
Echte Spielstände und Rätseldaten bleiben unberührt.

Die aus dem vollständigen finalen Diff ausgewählte Pflicht-CI, aktuellen
Chromium-Originale und der getrennte Selbstreview werden im PR gebunden.
HZ-B-R01 und HZ-B-M01 bleiben separat vor Merge erforderlich.
Kein Merge, Deployment oder Issue-Abschluss.
