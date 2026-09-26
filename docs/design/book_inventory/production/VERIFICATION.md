# BP-1 · Prüfbericht und Reproduktion

Stand: 26.09.2026 · Technische Vorlagen, keine Spiel- oder Kunstabnahme.

## Quellen und Stand

Basis `main@831b46f9e373e8691c18088efc9f2495fe3defb8`, Arbeitsbranch
`chore/27-buch-produktionsvorlage`. Aktuelle AGENTS.md, Workflow, Projektprofil,
Produktdefinition, Gestaltungskonzept, P1-Fachvertrag 0.13, Modellauswahl/-katalog,
vollständiger #27-Body und #21 wurden gelesen. #27 hatte beim Start keine Kommentare.
Die Bildbeschreibung im Issue war verfügbar, das ursprüngliche Chatbild nicht.

PR #28 ist nur lesende Referenz am Head
`9834ee834f5b83bbc5e6b17429a8fe7185c26758`; README, Manifest, öffentliche
Quellen, Typografie-/Iconvorlagen und Renderwerkzeuge wurden geprüft.
[R2](https://github.com/venomenon328/picross/pull/28#pullrequestreview-5325378229)
ist ein fremder vorhandener Prüfstand, kein selbst ausgeführtes neues Review.
Die überholte Auswahlpflicht S1/S2/S3 + U1/U2 ist durch den aktuellen #27-Body
ersetzt. O-01 ist kein Auftrag zur Änderung des alten PRs.

PR #25 ist nur lesende Referenz am Head
`df7ac589e900a6d6d7c5080599c6a5ace47c395d`; sein `design/demo.gd` bindet
`z1-demo-1`. [R1/B-01](https://github.com/venomenon328/picross/pull/25#pullrequestreview-5323317296)
bleibt offen. Kein Cherry-pick, kein Produktcode übernommen oder korrigiert.
Die drei öffentlichen Datenexporte wurden vor Rendering byteweise gegen die
Referenz gelesen; ihre SHA-256-Werte stehen separat im Manifest. Die Original-
Fixturehashes werden zusätzlich gegen den Basiscommit geprüft.

## Ausgeführte technische Prüfungen

Der [kleine lokale Vorlagen-/Prüfhelfer](../../../../tools/book_inventory/production.py)
enthält ausschließlich statisches Zeichnen, Renderprüfung, Lieferprüfung und
ZIP-Verpackung. Keine Eingabe-, Solver- oder H1-Engine, keine Produktabhängigkeit.
Die Lieferprüfung läuft über einen entdeckbaren Standardbibliothek-Test im
bestehenden `docs`-Job; Browser/Pillow sind dort nicht erforderlich.

Geprüft werden die tatsächlichen Dateien: fünf Fälle, 22 PNG-/SVG-Paare,
Hashes, PNG-Signaturen/Chunk-CRCs/dekomprimierte Scanlinegrößen, Dimensionen,
Quellgleichheit, öffentliche Datenfelder, Originalpalette/-hinweise,
vollständige Raster-/Miniaturzellmengen, erwartete ganze Hinweisfenster,
normierte Koordinaten, Aktionsgrenzen, Trennung von Aktionen und Hinweisen/Raster,
Arbeitsflächen innerhalb des falzverdeckenden Bogens sowie Browser-Font-/Textgrenzen.
Die transparenten UI-PNGs wurden beim Rendern auf Alpha 0 bis 255 geprüft.

Die Browserprüfung misst die tatsächlichen Fontrechtecke aller Texte gegen den
Viewport, Hinweise zusätzlich gegen ihre Flächen sowie Koordinaten/Status/Titel
gegen ihre Reserven. Sie fand anfänglich knappe Fontüberstände; die finale
Hinweisschrift/Baseline wurde so angepasst, dass alle gemessenen Grenzen passen.
Kein Test wurde dafür abgeschwächt. Die zwei aufgezeichneten Schriftfamilien wurden
explizit geladen und ihre Originaldateien vor Rendering hashgeprüft.

Renderumgebung: Windows, Python 3.13, Playwright 1.55.0, Pillow 11.3.0,
installierter Microsoft Edge. Exakte Browserversion in [render-checks.json](render-checks.json),
Device Scale Factor 1; Netzwerk im Renderkontext gesperrt. Fonts nur temporär,
keine globale Installation. Die editierbaren Liefer-SVGs enthalten keine Fontbytes.

## Sichtprüfung und Grenzen

Die fünf Arbeitskompositionen wurden in Originalgröße angesehen. Schwerpunkt:
lange F-02-/F-03-Hinweise einschließlich Präfixmarkern, unveränderte Zellen und
Farben, Trennung an Fünferlinien, Miniaturausschnitt, flache Falzabgrenzung,
kleines Fenster mit UI 125 %, vollständige Aktions-/Statusflächen.
Der technische Falz liegt nur außerhalb des Arbeitsbogens. Die 720p-Probe zeigt
29×17 Zellen und vollständige Werkzeugziele, F-03 weiterhin 57×28.
Eine kollidierende technische Randbeschriftung wurde vor der finalen Lieferung
entfernt; die eigentliche Fußzeile kennzeichnet alle Vorlagen ausdrücklich.

Die getrennten UI-/Freihalte-/Beschnittbilder wurden ebenso in Originalgröße
kontrolliert. Alle zwölf Masken wurden vollständig decodiert und enthalten nur
Schwarz und Weiß; die Freihaltegrenzen sind nach außen auf ganze Pixel gerundet.
Die Masken sind binäre Arbeitsmittel: Sie bewerten keine malerische
Qualität und beweisen keinen zukünftigen Kontrast auf noch fehlender Illustration.
Die tatsächlichen Originalbilder, Quellgeometrie und der vollständige Diff sind
Gegenstand des getrennten Selbstreviews im Draft-PR.

Kein neuer Godot-Screenshot, lokaler Produktneubau oder realer Maustest. Keine
physische DPI-Messung, Kunstabnahme, neue H1-/G1-Spielabnahme oder allgemeine
responsive Layoutgarantie. Helle Originalzahlen bleiben mit C1 als Vorschlag
gekennzeichnet; finalen Kontrast anhand der tatsächlichen Kunst in BP-3 beurteilen.

## Reproduktion

Aus dem Repositoryroot, Python 3.11 oder neuer:

```powershell
python tools/book_inventory/production.py verify
python -m unittest discover -s tools -p 'test_*.py' -v
python tools/check_docs.py
git diff --check 831b46f9e373e8691c18088efc9f2495fe3defb8 HEAD
```

Zum erneuten Rendern optional eine isolierte Python-Umgebung mit Playwright 1.55.0
und Pillow 11.3.0 verwenden. Die zwei im Fontmanifest bezeichneten TTFs aus dem
gepinnten Referenzstand in einem temporären Ordner als `Fraunces.ttf` und
`PlexSans.ttf` bereitstellen; nicht in die Lieferung kopieren. Dann:

```powershell
python tools/book_inventory/production.py build --browser 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe' --fonts artifacts/bp1-fonts
python tools/book_inventory/production.py pack
```

`build` ersetzt Layoutdaten, SVGs, PNGs und Render-/Hashmanifest. Manuelle Änderungen
zuerst in den Quelldaten/Generator übernehmen. Andere Browserstände können andere
PNG-Bytes erzeugen und erfordern erneute Sichtprüfung. Die Referenz-Commits müssen
für einen Neubau lokal erreichbar sein; `verify` benötigt nur den Basiscommit.
`pack` prüft vor Verpackung und nimmt alle Lieferdateien außer sich selbst auf;
keine Fontdateien oder privaten Inhalte. Die festen ZIP-Zeitstempel ermöglichen
bei unveränderten Dateien denselben Hash. Das ZIP enthält keine Tools; zur
Reproduktion den im PR gebundenen Repositorycommit verwenden.

Vorhandene unversionierte/ignorierte Altartefakte bleiben unangetastet. Der
Dokumentvalidator scannt auch solche Verzeichnisse; der lokale Abschlussnachweis
wird deshalb in einer temporären Kopie ausschließlich der Git-Indexdateien
geführt. Die unveränderte CI prüft zusätzlich den tatsächlichen finalen Checkout.
`product` und `preflight` bleiben aktiv und unverändert; ihre Ergebnisse stehen
im PR, ohne sie als neue Spiel-/Gestaltungsabnahme auszugeben.

## Abnahmegrenzen

P-01 bis P-04 werden technisch zur Prüfung geliefert. Unabhängiges Review und
ausdrückliche Mergefreigabe bleiben offen. Die finale Eigentümerentscheidung zu
Bild, Layout, Schrift und Kontrast erfolgt erst an BP-3 vor #23. BP-2/BP-3 und
#23/#24 wurden nicht begonnen. #27 und #21 bleiben offen; kein Merge oder Release.
