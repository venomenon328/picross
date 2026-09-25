# Z1 · Zwei nicht gewählte Entwürfe

Das komplette `picross-z1-windows-x86_64.zip` entpacken und `picross-z1.exe`
starten. Keine Godot-Installation erforderlich. `picross-z1.console.exe` ist
derselbe Entwurf mit technischer Konsole. Quellcommit und Prüfergebnis stehen
in START.txt und z1-report.json. Das reguläre P1-ZIP bleibt ein eigener Export.

Unten im ausdrücklich getrennten **Prüfbereich** V1/V2 und F-01/F-02/F-03 wählen.
„Beispiel zurücksetzen“ stellt den deterministischen Teilstand einschließlich
Ansicht, Farbe, Werkzeug und Undo/Redo wieder her. V1/V2 wechseln nur den Stil;
eine laufende Geste wird dabei verworfen. UI-Skalierung und der H1-Schalter bleiben
sitzungsweit erhalten. Für die Kernbilder UI 100 % wählen, dann zurücksetzen.

Diese Arbeitssitzungen leben ausschließlich im Speicher. Sie lesen, schreiben,
migrieren oder löschen keine normalen P1-Spielstände. Erneuter Start beginnt
wieder bei F-02. Es gibt hier keinen Album-, Speicher- oder Enthüllungsablauf.
F-03 ist ein UI-Testdatensatz ohne abgenommene Rätselqualität.

Farbflächen wählen die originale Rätselfarbe; Rand und Punkt markieren die Auswahl.
Füllen/Radierer/Hand sind davon getrennte Werkzeuge. „? Hilfe“ erklärt Mausstriche,
individuelle Hinweisnavigation und Miniatur. Das Menü enthält UI 100/125 %,
H1-Markierung, Hinweisrücksetzung und Beenden. Undo/Redo stehen oben; Rasterzoom,
Gesamtansicht und 100 % in der rechten Spalte. Kleine Tooltips erläutern die Aktionen.

Zum Vergleichen zunächst F-02/V1 zurücksetzen, ansehen, dann V2 wählen. Danach
F-01 und F-03 ansehen. Fenstergröße, UI-Skalierung und Rasterzoom getrennt halten.
Bei 1280×720/UI 125 % wird die Miniatur kompakter; Werkzeuge bleiben sichtbar.
Das ist eine unsignierte technische Vorschau, kein Release und keine Stilentscheidung.

Quellstart mit der gebundenen Godot-4.7.2-Standard-Engine:

```sh
godot --path prototypes/p1 res://design/main.tscn
```

Automatisierte Reproduktion erfolgt ausschließlich im isolierten Produktweg:

```powershell
$z1Cache = Join-Path $env:TEMP 'picross-p1-preflight-cache'
python tools/p1_product.py --cache-dir $z1Cache --output-dir artifacts/p1-product
```

Der Unterordner `z1/` im technischen Artefakt enthält ZIP, Bericht, Startanleitung,
Entscheidungsunterlage und `renders/`. PNGs und Renderbericht nennen Fixture,
Demo-Revision, Commit, Spielerzustand, Ansicht, UI-Skalierung und logische Fläche.
Eigentümerprobe, physische Windows-DPI und unabhängiges Review bleiben separat.
