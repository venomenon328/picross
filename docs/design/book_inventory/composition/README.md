# BP-3 · Materialgerechte UI und Zielkompositionen

Stand: 26.09.2026 · B3-01 bis B3-05 aus [#27](https://github.com/venomenon328/picross/issues/27)
unter [#21](https://github.com/venomenon328/picross/issues/21).
Statische Entscheidungsunterlage; Eigentümerwahl und native Umsetzung offen.

[Offline-Vergleichsgalerie](index.html) · [Review-ZIP](bp3-review.zip) ·
[Entscheidungsunterlage](DECISION.md) · [Prüfbericht](VERIFICATION.md) ·
[Layout](layout.json) · [Stilwerte](style.json) · [Manifest](manifest.json).

ZIP vollständig entpacken und `index.html` lokal öffnen. A/B lassen sich bei
identischem Größenfall umschalten oder nebeneinander anzeigen; Original-PNGs und
eine 1:1-Ansicht sind erreichbar. Kein Server, Netzwerk, Framework oder Tracking.
Die Galerie verwendet Systemschriften für ihren Rand; die gerenderten Spieltexte
verwenden tatsächlich geladene Fraunces und IBM Plex Sans. Die Galerie bedient kein Spiel.

## Bildindex

| Fall | A · Inventarband | B · Sammlungskatalog | Maßstab |
| --- | --- | --- | --- |
| F-02 · 1920×1080 | [PNG](views/a-f02-1920.png) | [PNG](views/b-f02-1920.png) | UI 100 %, 40×40 bei 18 px |
| F-02 · 2560×1440 | [PNG](views/a-f02-2560.png) | [PNG](views/b-f02-2560.png) | UI 100 %, dieselben 40×40 bei 18 px |
| F-01 · 2560×1440 | [PNG](views/a-f01-2560.png) | [PNG](views/b-f01-2560.png) | UI 100 %, 20×20 bei 24 px |
| F-03 · 1920×1080 | [PNG](views/a-f03-1920.png) | [PNG](views/b-f03-1920.png) | **UI-Testdatensatz, keine Rätselabnahme**; 57×28 bei 24 px, Spalten 26–82 / Zeilen 36–63 |
| F-02 · 1280×720 | [PNG](views/a-f02-1280.png) | [PNG](views/b-f02-1280.png) | UI 125 %, 29×17 bei 22 px, Spalten 1–29 / Zeilen 1–17 |

[Komponenten-/Zustandstafel](png/states-ui.png),
[720p-Zustandsprobe bei UI 125 %](png/compact-states-ui.png) und
[schematischer rechter Anschluss](png/connection-ui.png).
Alle drei sind ausdrücklich statische Beispiele, keine ausgeführten Eingaben,
Speicheroperationen oder fertig implementierten Ansichten. Die 720p-Tafel montiert
unskalierte Ausschnitte der unteren Werkzeuge, des Status und des rechten Zugangs
mit separaten Meldungs-/Tooltipbeispielen; sie ist kein sechstes Ziellayout.

`details/` enthält zehn Zahlenausschnitte und zwölf zusätzliche 720p-Ausschnitte:
Miniatur, Swatches, Werkzeugleiste, rechter und linker Zugang sowie Status, je A/B.
[Details und exakte Quellrechtecke](details.json). Ein Detailpixel entspricht
einem Pixel der zugeordneten Komposition. Die Galerie verlinkt jede Datei einzeln.

## Editierbare Ebenen

Für jeden der fünf Fälle und jede Tafel existieren drei SVGs und entsprechende PNGs:

| Suffix | Inhalt / Z-Reihenfolge |
| --- | --- |
| `-mounts` | Lokale Karten-/Metallfassungen und Werkzeuggehäuse, ohne Zahlen/Icons. |
| `-content` | Präzise Rasterdaten, eigene Miniatur, Hinweise, Symbole, Texte und Trefferrechtecke. |
| `-ui` | Gemeinsame Zusammenführung beider Ebenen; identisch auf A und B. |
| `-ui-underlay.png` | Tatsächlich gerenderte Fläche bei entfernten Texten, für lokale Kontrastmessung. |

Die unveränderten BP-2-Hintergründe liegen im Repository im Artworkpaket; im ZIP
zusätzlich unter `backgrounds/`, exakt hashgebunden. Darüber kommen Montierung
und Inhalt in der genannten Reihenfolge. SVG-Gruppen bleiben editierbar, Zahlen
sind Text und Zellen einzelne Vektorobjekte. Es gibt keine generierten Fantasiezahlen.
`layout.json` enthält die unveränderten BP-1R-Bild-/Trefferrechtecke und Transformationen.
Die Bildgröße wird ausschließlich beim Hintergrund proportional mit 1 / 0,75 / 0,5
angepasst; die jeweiligen UI-/Rastermaße bleiben unabhängig.

`inputs/` enthält die unveränderten öffentlichen Daten, Icons und Fontquellen aus
BP-1R. Die Hauptansichten zeigen denselben `z1-demo-1`-Zellstand einschließlich
seiner Fehler. Der öffentliche Snapshot enthält keine vollständige History:
Undo/Redo erscheinen in den Hauptansichten als normale Gestaltungsbeispiele,
nicht als aus einer erfundenen History abgeleitete Verfügbarkeit. Die Tafel
zeigt normale, Hover-, Druck- und deaktivierte Historyaktionen getrennt.

Die neun häufigen Arbeitsaktionen bleiben auf der Arbeitsseite. Gruppierung:
Füllen/Radierer/Hand, Undo/Redo und vier Ansichtsaktionen. Mindesttreffer 44×44 px,
bei UI 125 % 55×55 px; Iconbilder 26×26 bzw. 32,5×32,5 px. Die sichtbare Fassung
liegt innerhalb der Trefferfläche. Nur die gemeinsamen Werkzeugwannen nutzen
3 px der freien Außenreserve. Keine Materialkante liegt in Hinweis-/Zellflächen.
Farb-Innenflächen sind exakt opak in Original-RGB; Auswahlmarken liegen außerhalb.

## Herkunft und Reproduktion

Gebundene Basis `66b9d39dd3dbce908ff663a18c059351cfccf557` (BP-2), darin BP-1R
aus `4ef926fe033418090512d82b9aba151031534c5f`. Alle ursprünglichen Produktions-
und Artworkdateien, Helfer und Tests bleiben unverändert. Keine neue Bildgenerierung,
Retusche oder Fremdassetbeschaffung. Neue Materialformen sind editierbare Vektoren.

Die beiden Fonts werden nur temporär aus den gepinnten URLs in
[fonts.json](inputs/fonts.json) geladen und einschließlich OFL-Quelldateien auf
SHA-256 geprüft. Keine Fontbytes werden installiert, eingebettet oder geliefert.
SVG-Editoren ohne die Fonts können Ersatzschriften verwenden; die PNGs sind der
konkrete Rendernachweis, keine Zusage universeller SVG-Fontverfügbarkeit.

Der enge Helfer liegt unter `tools/book_inventory/composition.py` am im PR
gebundenen Repositorycommit. Aus dem Repositoryroot:

```powershell
python tools/book_inventory/composition.py verify
python -m unittest discover -s tools -p 'test_*.py' -v
python tools/check_docs.py
```

Für erneute Rasterisierung die vorhandene isolierte Umgebung mit Playwright 1.55.0,
Pillow 11.3.0 und Edge verwenden. Die vier gepinnten Dateien temporär als
`Fraunces.ttf`, `PlexSans.ttf`, `Fraunces-OFL.txt`, `PlexSans-OFL.txt` bereitstellen.
Danach `build --browser <Edge-Pfad> --fonts <temporärer-Ordner>`, dann `pack`.
Andere Browserversionen können abweichende Rasterbytes erzeugen. CI lädt weder
Schriften noch Bilder herunter und ruft keine Generierung auf.

Der eigene Draft-PR bindet Quellhead, Basis, Test-Merge, ZIP-SHA-256, aktuellen
CI-Stand und getrennten Selbstreview. Die ZIP-Bindung erfolgt über einen
unveränderlichen Commitlink, keine zirkuläre Selbstreferenz im Archiv.
