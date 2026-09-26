# BP-1R · Einzelseiten-Komposition

Stand: 26.09.2026 · K-01 bis K-05 aus [#27](https://github.com/venomenon328/picross/issues/27)
unter [#21](https://github.com/venomenon328/picross/issues/21).
**Statische technische Vorlagen, keine Hintergrundkunst oder native Navigation.**

[Review-ZIP](bp1r-review.zip) · [Bildbriefing](BRIEFING.md) · [Layoutdaten](layout.json) ·
[Quell-/Dateimanifest](manifest.json) · [Rendergrenzen](render-checks.json) · [Prüfbericht](VERIFICATION.md).
Der eigene Draft-PR bindet ZIP-Hash, Head, Basis, CI und getrennten Selbstreview.
Das ZIP über „Download raw file“ laden. Es enthält keine Fonts.

Diese Revision ersetzt die integrierte Vorlage in derselben Pipeline. Die
[historische BP-1-Lieferung](https://github.com/venomenon328/picross/tree/0d3ad6a921578f94b3249ab83fbb215721549dfb/docs/design/book_inventory/production)
aus PR #29 bleibt unverändert in der Historie. Ihre Doppelseitenmasken und ihr
Einlegebogen sind für weitere Bildproduktion abgelöst, keine rückwirkend fehlerhafte Lieferung.
Der erste BP-2-A-Versuch wurde nicht akzeptiert; er ist keine Assetgrundlage.

## Eine breite linke Seite

Nahansicht eines ausreichend breiten Inventarbands: Die linke Seite füllt fast
den Bildschirm. Raster und beide Hinweisflächen liegen frontal auf demselben
Papier. Falz rechts außerhalb, nur ein schmaler rechter Seitenanschnitt.
Keine große zusätzliche UI-Karte und kein Einlegebogen über einer Doppelseite.
Die neutralen technischen Konturen bestimmen Geometrie, keinen Illustrationsstil.

Master 2560×1440: linke Seite `[80,48,2380,1340]`, Falz `[2480,40,16,1360]`,
rechter Anschnitt `[2496,48,64,1340]`, Buchreserve `[40,34,2480,1372]`.
Die Arbeitsseite nimmt 93 % der Bildbreite ein. Perspektive und Material dürfen
die rechteckigen Arbeitszonen nicht verformen. Der Bildausschnitt entsteht bei
der Komposition eines breiten Bands, nicht durch Strecken eines vorhandenen Bilds.

Rechts auf der **linken Arbeitsseite** stehen eigene Miniatur, separate Koordinaten,
Palette und Werkzeug-/Farbstatus; unten die neun häufigen Aktionen. Die Register-
und Seitenzugänge sind eigenständige UI. F-03 verschiebt Raster/Hinweise um 40 px
und die gleich große Miniatur um 64 px nach links, um alles vor dem Falz zu halten.
Die untere Leiste rückt bei 1080p um 24 px, bei 720p um 12 px nach oben.
Der 720p-Status liegt bei `[990,610,230,65]` vollständig innerhalb der Seite;
keine Blattkante durch die Schrift. F-01 behält bewusst ruhige freie Papierfläche.

## Fünf Größenfälle · BP-1 → BP-1R

Bildpixel, keine gemessene Windows-DPI. UI-Skalierung, Rasterzoom und Buchausschnitt
sind unabhängig. Alle Angaben in den folgenden vier Maßspalten gelten **vorher = nachher**.

| PNG / SVG | UI / Zelle / Hinweisschrift | Raster; sichtbare Zellen | Zeilen- / Spaltenhinweisfläche | Slots horizontal / vertikal |
| --- | --- | --- | --- | --- |
| [F-02 1920×1080](png/f02-1920-layout.png) / [SVG](svg/f02-1920-layout.svg) | 100 % / 18 / 13 px | 720×720; 40×40 | 210×720 / 720×126 | 30 / 18 px |
| [F-02 2560×1440](png/f02-2560-layout.png) / [SVG](svg/f02-2560-layout.svg) | 100 % / 18 / 13 px | 720×720; 40×40 | 210×720 / 720×126 | 30 / 18 px |
| [F-01 2560×1440](png/f01-2560-layout.png) / [SVG](svg/f01-2560-layout.svg) | 100 % / 24 / 14 px | 480×480; 20×20 | 192×480 / 480×144 | 30 / 18 px |
| [F-03 1920×1080](png/f03-1920-layout.png) / [SVG](svg/f03-1920-layout.svg) | 100 % / 24 / 14 px | 1368×672; 57×28 | 240×672 / 1368×144 | 30 / 18 px |
| [F-02 1280×720](png/f02-1280-layout.png) / [SVG](svg/f02-1280-layout.svg) | 125 % / 22 / 16,25 px | 638×374; 29×17 | 210×374 / 638×120 | 37,5 / 22,5 px |

F-03: Spalten 26–82 / Zeilen 36–63; UI-Testdatensatz, Rätselqualität nicht abgenommen.
F-02 klein: Spalten 1–29 / Zeilen 1–17. Alle anderen Fälle zeigen das ganze Raster.
Rasterursprünge vorher → nachher: F-02/1920 `510,252 → 510,252`, F-02/2560
`830,432 → 830,432`, F-01 `970,470 → 970,470`, F-03 `350,270 → 310,270`,
F-02/1280 `300,222 → 300,222`. Keine kleinere Schrift und kein Flächenverlust.

Navigation vorher: Hilfe/Menü je 44² px, bei 125 % je 55² px, Album nur als
Menüanschluss; kein separater Seitenzugang. Nachher zusätzlich zwei eigenständige
Ziele gleicher Größe: Album links und Information rechts. Zusätzliche Trefferfläche
3.872 px² bei UI 100 %, 6.050 px² bei 125 %. Keine breite Kategorienwand.
Alle Aktions- und Bildrechtecke sind je Größenfall in `layout.json` bemaßt.

![Arbeitskomposition 1080p](png/f02-1920-layout.png)

## Navigation und Anschlussvertrag

[Navigationstafel](png/navigation.png) / [SVG](svg/navigation.svg) und
[rechte Informationsansicht 1080p](png/information-1920-layout.png) / [SVG](svg/information-1920-layout.svg).
Sammlung ist neutraler Kontext, kein beschlossener Katalog mit „Orte“ oder „Tiere“.

| Aktion | Zweck / Ziel | Deutscher Tooltip |
| --- | --- | --- |
| `nav-album` | Kompaktes linkes Register → `album` | Album öffnen · Sammlung und Blattauswahl |
| `nav-information` | Rechter Seitenzugang → `information` | Informationsseite öffnen · Einstellungen und Hilfe |
| `nav-work` | Rückweg aus Information/Album → `work` | Zur Arbeitsseite zurück · Arbeitsstand erhalten |

Registerkörper, Icon, Tooltip und Zustand sind separate UI, niemals gemalt.
Normal: Papier, Hover: blassgrün, Aktiv/Zielansicht: dunkler Körper mit hellem Icon.
Alle drei Zustände stehen für alle drei Aktionen auf der Tafel. In den Arbeits-
vorlagen sind die beiden anderen Ziele normal; die Ansicht selbst ist `work`.
Trefferfläche und sichtbarer Körper: 44×44 px, Iconreserve darin 26×26 px mit
9 px Abstand; bei UI 125 % entsprechend 55×55, 32,5×32,5 und 11,25 px.
`rect` bezeichnet Treffer/Körper, `image_rect` nur das Iconbild.

Zwei feste Buchansichten, keine frei bewegte Kamera. Seitenwechsel sind weder
Zellaktion noch Raster-/Miniatur-Pan. Bei Rückkehr bleiben eigener Zustand,
Undo/Redo, aktive Farbe/Werkzeug, Rasterfokus/Zoom und individuelle bestätigte
Hinweislesepositionen erhalten. Laufende Gesten werden nach dem bestehenden
Abbruchvertrag verworfen. Pflicht-Flush und Recovery-Schreibsperre werden nicht
umgangen; erforderliche Übergänge bleiben bei Speicherfehler blockiert. Keine neue
Persistenzregel oder Erfolgsmeldung. Ein Albumwechsel behält seinen bisherigen Vertrag.

Hilfe/Menü oben bleiben schnelle Zugänge zu den auf der Informationsseite
schematisch benannten bestehenden Inhalten (Hilfe bzw. Einstellungen); kein neues
Parallelmenü. Füllen/Radierer/Hand, Farbe, Undo/Redo, Zoom/Fit/Arbeitsgröße,
Koordinaten und eigene Miniatur bleiben auf der Arbeitsseite. Farbauswahl aktiviert
Füllen auch nach Hand/Radierer. Die Vorlage implementiert keine Aktionen.

Die rechte Ansicht zeigt Bereiche für bestehende Einstellungen/Hilfe und einen
ausdrücklich späteren/offenen Statistikbereich. Keine erfundenen Daten, keine
Live-Fehlerzahl, Korrektheitsquote oder „bisher fehlerfrei“-Anzeige. Keine neue
Statistik-, Ranglisten-, Timer-, Audio- oder Notizfunktion. Kein zweiter Bildauftrag.

## Dateien, Masken und Transformation

Für alle fünf Größenfälle sowie den schematischen rechten Anschluss:

| Endung | Ebene / Bedeutung |
| --- | --- |
| `-layout` | Technische Seitenkonturen plus präzise UI, editierbares SVG und gerendertes PNG. |
| `-ui` | Transparente Überlagerung: Raster/Zahlen/Zellen, Miniatur, Registerkörper, Icons, Labels und Informationen; keine bildschirmfüllende Papierkarte. |
| `-keepout` | Weiß = ruhiger geschützter Untergrund; schwarz = Details innerhalb der Art Direction möglich. Keine Alpha-/Inpainting-Maske. |
| `-crop` | Weiß = erhalten; schwarz = optionaler äußerer Beschnitt. Keine Freihaltemaske. |

[Master-Freihaltung](png/master-keepout.png) / [SVG](svg/master-keepout.svg):
exakte Vereinigung der invers transformierten Arbeits-/UI-Rechtecke aller **fünf
linken Arbeitsansichten**. Schützt Raster/Hinweise, Miniatur, Palette, Koordinaten,
Status, Aktionen, Register, Seitenzugang und Titel. Keine alte ganze Einlegebogenmaske.
Die eigene rechte Freihaltemaske schützt ihre schematischen Informationsbereiche;
sie gehört zu einer anderen festen Ansicht, nicht in den linken Bildmaster.
[Master-Beschnitt](png/master-crop.png) / [SVG](svg/master-crop.svg): wie zuvor
8 Masterpixel außen optional; diese unveränderte Beschnittgeometrie wurde neu gerendert/geprüft.

`layout.json` Revision `BP-1R`, Schema 2: Pixelrechtecke `[x,y,Breite,Höhe]`,
normiert `[x/W,y/H,Breite/W,Höhe/H]`, Ursprung links oben, Enden exklusiv.
`sheet` bedeutet jetzt linke Buchseite; `fold` liegt rechts **außerhalb**.
`right_page_slice` ist nur der schmale Anschnitt. `decorative_edges` reserviert
äußere Beschnittstreifen. Unbelegte schwarze Maskenbereiche sind mögliche ruhige
Randdetails, kein Auftrag zum Füllen jedes freien Flecks.

Master → 1440p: Faktor 1; → 1080p: 0,75; → 720p: 0,5. Offset immer `[0,0]`,
Ausschnitt `[0,0,2560,1440]`. Rückrechnung jedes Rechtecks: alle vier Werte durch
den Faktor teilen, Maskengrenzen anschließend nach außen auf ganze Pixel runden.
Nur die Hintergrundkunst wird proportional angepasst. Zahlen, Iconbilder,
Trefferflächen und Raster bleiben an ihrem eigenen Pixelvertrag. Kein Mitzoomen,
kein 9-Slice des Buchs. Andere Seitenverhältnisse sind nicht untersucht.

Hintergrund enthält ausschließlich Papier, Einband, Seitenlagen und wenig Umgebung.
Keine Schrift/Pseudoschrift, Registerattrappen oder eingebrannten Werkzeugschatten.
`study-labels` kennzeichnet die technische Studie außerhalb der Ziel-UI; in BP-3
außerhalb der Produktkomposition führen. F-03s Testkennzeichnung bleibt erhalten.

## Quellen und offene Abnahmen

[F-01](sources/f01-public-demo.json), [F-02](sources/f02-public-demo.json),
[F-03](sources/f03-public-demo.json), [Icons](sources/icons.json) und
[Fontquellen](sources/fonts.json) bleiben bytegleich zum integrierten BP-1-Stand.
Öffentliche Daten aus PR #28 `9834ee834f5b83bbc5e6b17429a8fe7185c26758`,
`z1-demo-1` aus PR #25 `df7ac589e900a6d6d7c5080599c6a5ace47c395d`.
Raster und Miniatur lesen dieselbe eigene Zellliste, inklusive Fehlern und unbekanntem
Undo-Endstand. Original-Fixtures, Hinweise, Farben, Proofs und Ergebnisbilder unverändert.
G1/H1 und Spoilergrenzen bleiben verbindlich. Durchstrichenes F-02-`38` ist das
bestehende echte Zeile-2-Beispiel. C1 (0,55-px-Kontur bei Hinweisfarben 2/4) bleibt
ein Vorschlag aus #26, keine Paletteänderung oder neue H1-Engine.

Fraunces / IBM Plex Sans bleiben reversible Typografievorgaben. Fonts nur temporär,
hashgeprüft, nicht installiert/eingebettet/mitgeliefert. PNGs sind Rendernachweise;
SVG-Editoren ohne diese Fonts können Ersatzschriften verwenden. OFL-Wortlaut an
der Herkunft: [Fraunces](https://github.com/venomenon328/picross/blob/9834ee834f5b83bbc5e6b17429a8fe7185c26758/docs/design/z1_1/fonts/Fraunces-OFL.txt),
[Plex Sans](https://github.com/venomenon328/picross/blob/9834ee834f5b83bbc5e6b17429a8fe7185c26758/docs/design/z1_1/fonts/PlexSans-OFL.txt).

Unabhängiges technisches/visuelles Review und ausdrückliche Mergefreigabe offen.
Vor erneuter BP-2-Bildproduktion die konkret geprüfte BP-1R-Vorlage benennen.
Finale Kunst-/Layout-/Schrift-/Kontrastentscheidung erst an BP-3 vor #23.
Keine neue Bildproduktion, keine native Bedienabnahme, kein Beginn von BP-3/#23/#24.
#27 und #21 bleiben offen; PR #25/#28/#29 unverändert. Kein Merge/Release.
