# BP-1R · Prüfbericht und Reproduktion

Stand: 26.09.2026 · K-01 bis K-05 · technische statische Vorlage.

## Stand und Quellen

Basis `main@0d3ad6a921578f94b3249ab83fbb215721549dfb`, Branch
`chore/27-einzelseiten-komposition`. Der eigene Draft-PR bindet den finalen
Head, ZIP-Hash, CI-/Test-Merge-Stand und den getrennten Selbstreview. Keine Prüfung
von BP-1 wird als aktueller BP-1R-Nachweis ausgegeben.

Aktuelle AGENTS.md, Workflow, Projektprofil, Produktdefinition, Gestaltungskonzept,
P1-Fachvertrag 0.13, Modellauswahl/-katalog und vollständiger aktueller #27-Body
einschließlich beider Kommentare sowie #21 gelesen. Der konsolidierte #27-Body vom
26.09.2026 ersetzt die ältere Doppelseitenentscheidung. PR #29/R1 und Merge sind
historischer Kontext. PR #25/#28 bleiben lesende Herkunftsreferenzen, kein neues
Review oder Korrekturauftrag dieser PRs. Kein Cherry-pick oder Spielquellendiff.

Der separate Worktree lässt unversionierte Altartefakte im ursprünglichen
Arbeitsbaum unangetastet. Alle fünf Quellmanifeste/-daten unter `sources/` sind
bytegleich zum integrierten BP-1-Basiscommit; dessen Herkunft liegt in PR #28
`9834ee834f5b83bbc5e6b17429a8fe7185c26758` und PR #25
`df7ac589e900a6d6d7c5080599c6a5ace47c395d`.
Original-Fixtures, Proofs, Ergebnisbilder und Produktverträge werden nicht verändert.

## Automatisierter Dateinachweis

Der bestehende [Vorlagenhelfer](../../../../tools/book_inventory/production.py)
wurde fortgeschrieben, keine zweite Pipeline angelegt. Seine Tests werden vom
unveränderten `docs`-Workflow entdeckt. `verify` verwendet nur die Standardbibliothek.

Geprüft werden die gelieferten Dateien: fünf verbindliche Größenfälle mit identischen
Zell-/Rastergrößen, Quelldaten am Basiscommit, Originalpalette/-hinweise, ganze
Hinweisfenster in gemeinsamen Slots, tatsächliche SVG-Zellmengen von Raster/Miniatur
und tatsächliche RGB-Füllzellmittelpunkte der Layout-PNGs. Keine Solver-/H1-Neuberechnung.

Neue Geometrie-/Navigationstests prüfen vollständig enthaltene Arbeitsmittel auf
der linken Seite, Abstand zum rechten Falz, getrennte Aktionsrechtecke ohne
Raster-/Hinweisüberlagerung, alle häufigen Aktionen sowie Album-/Seitenzugang,
SVG-Trefferflächen gegen Layoutdaten, benannte Ziele/Tooltips und drei Beispiel-
zustände je Navigation. Negative Regressionen verändern Falz, 720p-Status,
Navigationsposition/-ziel und Beschnittmaske; die Prüfer müssen dies ablehnen.

27 PNG-/SVG-Paare: fünf Arbeitsfälle × vier Ebenen, zwei Mastermasken,
vier rechte Anschlussdateien und eine Navigationstafel. PNG-Struktur, CRCs,
dekomprimierte Scanlines und Maße werden geprüft. 14 Masken werden vollständig
decodiert und byteweise mit unabhängig aufgebauten binären Rechteckflächen
verglichen, einschließlich exakter inverser Mastervereinigung. Keine Graukanten.
Sechs UI-PNGs werden auf Alpha 0 bis 255 geprüft; unbekannte Rasterzellmittelpunkte
müssen transparent sein. Kein opaker Ganzseitenersatz im UI.

Pixel-/Normrechtecke, proportionale Hintergrundtransformation und Fontfreiheit
werden geprüft. Dateihashes stehen im [Manifest](manifest.json), Generatorhash
ist auf LF normiert. Das ZIP wird vollständig gegen alle Paketdateien verglichen;
keine TTF/OTF/WOFF/WOFF2 und keine eingebetteten Fontbytes in SVGs.

## Tatsächlicher Render- und Sichtnachweis

Windows, Python 3.13, isolierte Playwright-1.55.0-/Pillow-11.3.0-Umgebung,
installierter Microsoft Edge, Device Scale Factor 1. Exakte Browserversion,
geladene Schriftfamilien und gemessene Einzeltextrechtecke stehen in
[render-checks.json](render-checks.json). Fraunces/PlexSans vor jedem Build gegen
die gepinnten SHA-256 geprüft, nur temporär geladen, Netzwerk im Browser blockiert.
Keine globale Fontinstallation. Die editierbaren SVGs enthalten keine Fontbytes.

Alle 27 gelieferten PNGs wurden tatsächlich betrachtet: fünf Arbeitsansichten
einzeln, rechte Anschlussansicht und Navigationstafel einzeln; alle sechs
transparenten Overlays auf neutralem Prüfpapier sowie alle 14 Masken als benannte
Übersichten. Zusätzlich unskalierte 1:1-Ausschnitte aller fünf Arbeitsfälle:
Hinweiszahlen/H1-Beispiel, Zelltrennung, aktive Werkzeuge, Status, linker Albumzugang
und rechter Seitenzugang mit Seitengrenzen. Große Gesamtbilder wurden in der
Anzeige teilweise verkleinert; die Detailprüfung stützt sich deshalb ausdrücklich
auf die unskalierten Ausschnitte, nicht auf eine behauptete Gesamtansicht bei 1:1.

Ergebnis: vollständige Zahlen, unveränderte Zellflächen, sichtbare Miniatur und
Aktionszustände; Falz außerhalb des Arbeitsfelds, keine Seite durch Statuszeilen.
F-03 weiterhin 57×28, 720p/UI 125 % weiterhin 29×17. Kein erkennbarer wesentlicher
Flächenkonflikt. Bei der Erstellung wurden der 1440p-Seitenzugang um 10 px nach
links gesetzt und die unteren Werkzeuge innerhalb die Blattgrenze gerückt.
Die Prüfung wurde dafür nicht abgeschwächt. C1 bleibt als Vorschlag gekennzeichnet;
finaler Kontrast auf tatsächlicher Kunst ist damit nicht bestätigt.

## Reproduktion und Abschlussprüfungen

Python 3.11 oder neuer, im Repositoryroot:

```powershell
python tools/book_inventory/production.py verify
python -m unittest discover -s tools -p 'test_*.py' -v
python tools/check_docs.py
git diff --check 0d3ad6a921578f94b3249ab83fbb215721549dfb HEAD
```

Für einen neuen Renderlauf optional isolierte Umgebung mit Playwright 1.55.0
und Pillow 11.3.0. Zwei TTFs aus [fonts.json](sources/fonts.json) temporär als
`Fraunces.ttf` und `PlexSans.ttf` bereitstellen. Nicht in die Lieferung kopieren.

```powershell
python tools/book_inventory/production.py build --browser 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe' --fonts artifacts/bp1r-fonts
python tools/book_inventory/production.py pack
```

`build` ersetzt Layout/SVG/PNG/Render-/Hashmanifest. Änderungen gehören zuerst
in Generator/Quelldaten; andere Browserversionen können andere PNG-Bytes erzeugen.
`pack` prüft und verpackt alle Paketdateien außer ZIPs mit festen Zeitstempeln.
Das ZIP enthält keine Tools; Reproduktion am im PR verlinkten Repositorycommit.
Die Commitbindung erfolgt über den unveränderlichen Raw-Link und SHA-256 im PR,
nicht über eine unmögliche Selbstreferenz auf den Commit, der das ZIP erst enthält.

Lokal ausgeführt: 53 Python-Tests in 24,657 Sekunden, erfolgreich mit einem
bestehenden Windows-Symlink-Skip; Liefer-/ZIP-Prüfung erfolgreich. Dokumentvalidator
und vollständiger Diffcheck erfolgreich. Der erste Dokumentlauf erfasste auch die
lokale Render-venv und meldete 154 Fremdpaket-Formatprobleme. Die temporäre venv
wurde aus dem Repository in den System-Tempordner verschoben; der unveränderte
Validator besteht danach direkt im Arbeitsbaum. Keine Prüferregel abgeschwächt.
Aktuelle CI-Ergebnisse werden im Draft-PR mit Head/Basis/Integrationscommit und
ausgeführten Schritten ausgewiesen. `product` und `preflight` bleiben unverändert aktiv. Sie prüfen den
unveränderten P1-Stand und ersetzen weder Sichtprüfung noch künstlerische Abnahme.

## Grenzen und offene Gates

Getrennter Selbstreview im eigenen Draft-PR, keine unabhängige Zweitprüfung.
Vor einem späteren Merge: unabhängiges technisches/visuelles Review und ausdrückliche
Eigentümerfreigabe. Vor erneuter Bildproduktion: konkret geprüfte BP-1R-Vorlage
benennen; keine alte BP-1-Maske verwenden. Finale Bild-/Layout-/Schrift-/Kontrastwahl
erst an BP-3 vor #23. Das ursprüngliche Chatreferenzbild liegt hier nicht als
Repositoryasset vor und wurde in diesem Lauf nicht betrachtet.

Kein Godot-Navigationsbau, keine Statistikimplementation, keine reale Maus-/DPI-
oder Spielabnahme, keine neue Hintergrundillustration. Kein neuer Beginn von
BP-2/BP-3/#23/#24. PR #25/#28/#29 bleiben unverändert, #27/#21 offen. Kein Merge/Release.
