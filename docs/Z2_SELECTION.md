# Z2: aktive Auswahl und native Integration

Stand: 27.09.2026 · #23 / I-01 bis I-05 unter #21

Maßgeblich ist die [Eigentümerentscheidung GD-01 bis GD-05](https://github.com/venomenon328/picross/pull/32#issuecomment-5855483934)
auf `c3a5386580d7a0da29b927b41bd692f0cca59274`. Sie ersetzt die historische
Bearbeiterempfehlung B in `composition/DECISION.md`. Die hashgebundenen Pakete
production/artwork/composition bleiben unverändert. PR #25/#28 sind keine Basis.

| Auswahl | Native Umsetzung |
| --- | --- |
| GD-01: A, dunkler Inventarband | Unverändertes UI-freies PNG, SHA-256 `957c2eab39b2334825fb159287b9d36a17b77fff1c628ea88110f2cfb5f7a71a`; proportionaler Hintergrund, getrennt von Control-/Rastergeometrie. |
| GD-02: gemeinsame BP-3-UI | Gefasste Miniatur, zwei Metallhalter, gemeinsame Farbmusterfassung, Werkzeugmulden 3/2/4, abgeschrägte Controls. Auswahl aus Sessionzustand: Werkzeug dunkel/unterstrichen, Farbe mit äußeren Eckmarkierungen. |
| GD-03: Fraunces / IBM Plex Sans | Fraunces 600 für Blatttitel; Plex Sans für UI/Hinweise. Gepinnte Fontbytes und OFL offline im regulären Export, keine Systemfontsuche. |
| GD-04: C1 | Feste dunkle Kontur für Hinweisfarben 2/4 an beiden Achsen, im Drag und Tooltip; unveränderte RGB-Füllung, Originalindizes und H1. Keine neue Option. |
| GD-05: N1 | Eine native Informations-Control mit gemeinsamem Einstellungen-/Hilfebereich, drei Zugängen und Rückweg. Nur der UI-freie Hintergrund wird gespiegelt; Falz links. |

Die Wahl des A-Arbeitsassets entscheidet nicht die weiterhin offene gesamte
Themen-/Kapitelstruktur des Produkts. Kein Laufzeit-Themeschalter, neuer Spielkern,
Album-/Statistikbau oder Inhalt aus #24.

## Bereitstellung und Renderergrenzen

[Ressourcenmanifest](../prototypes/p1/art/book/manifest.json) bindet alle lokalen
Dateien. `python tools/z2_resources.py provision` lädt ausschließlich die
[gepinnten BP-3-Upstreamquellen](design/book_inventory/composition/inputs/fonts.json),
prüft Downloadhashes, normalisiert die OFL-Texte wie BP-3 und prüft deren Zielhashes.
`python tools/z2_resources.py verify` prüft lokale Bytes und A-Identität offline.
Die [Iconpfade](design/book_inventory/composition/inputs/icons.json) werden als
weiße SVG-Strokes mit nativer Zustandsfarbe bereitgestellt; keine Fremdicons.
Fontbytes gehören zur nativen Anwendung, nicht nachträglich in die statischen Pakete.

Godots ganzzahlige Outline-API wird mit einem vierfachen Glyphenmaßstab und
Rückskalierung verwendet: Außenradius 0,25 px statt 0,275 px bei UI 100 %,
0,3125 statt 0,34375 bei UI 125 %. Die originale Füllglyphe wird zuletzt gezeichnet.
Konturbreite hängt nur an UI-Skalierung, nicht Zellzoom. Ganzzahlige Fontgrößen
ergeben etwa 16 statt 16,25 px im kleinen Vergleichsfall. Native 1:1-Details sind
Teil des Review-ZIPs; Browser-/Godot-Antialiasing wird nicht als pixelidentisch behauptet.
Plex-Ziffern werden in den festen 18/22,5-px-Spaltenslots um ihren sichtbaren
Ziffernkörper geclippt; die frühere für größere Slots reservierte Oberlänge darf
keinen oberen Marker ausblenden. Render- und Dragregressionen prüfen beide Ränder.

Native Montierungen verwenden flache Materialfarben und feine Licht-/Randlinien
statt der SVG-Verläufe. Die fünf Referenzzustände werden ausdrücklich im Capture
gesetzt; das Spiel erhält gespeicherten Zoom und die bisherigen 20 Arbeitsstufen.
Zwischengrößen reservieren zuerst die tatsächlichen Trefferflächen und begrenzen
den Rasterviewport oberhalb der Werkzeuge. Kein unsichtbares Verkleinern der Zellen.

Das A-Master bleibt aufbereitetes 1672×941-Material auf 2560×1440, keine nativ
erzeugte 1440p-Illustration. Untere Retuschestelle und weichere Detailauflösung
bleiben bekannte Grenzen des [BP-2-Prozesses](design/book_inventory/artwork/PROCESS.md).
N1 ist eine reversible Hintergrundableitung, kein drittes fertiges Artwork.

## Prüfbarkeit

[Z2-Prüfbericht und Eigentümerprobe](Z2_VERIFICATION.md) trennen lokale technische
Prüfung, aktuelle CI, Selbstreview und noch offene unabhängige Abnahme. Die reguläre
App-Identität `picross · P1`, `user://p1/saves/`, Schema 1, Fixtures, Revisionen,
Deduktionsnachweise und Enthüllungsbilder bleiben erhalten.
