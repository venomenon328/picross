# Z2: aktive Auswahl und native Integration

## Aktueller Stand · VS2-Erstlieferung und VS2-E1

Die gewählte A-Komposition bleibt. Die VS2-Erstlieferung in Draft-PR #62 auf
`2c332ad688315bfa851f7c0d8642d2ab4ac3709c` ordnet die Arbeitsfläche für vollständige
Raster neu: Werkzeugmulden 2/2/4, passive eigene Miniatur, benannte Ansichtsoption
nur in Einstellungen. R1 ist für diese Erstlieferung abgeschlossen. Z2-Herkunft
und historische Designs bleiben an ihren jeweiligen Stand gebunden.

Die jüngere **VS2-E1-Spezifikationsfreigabe** ergänzt kompakte Zeilenhinweise und
Ausgleich der freien Papierfläche. Miniatur und Palette werden etwas nach unten/links
versetzt, einschließlich ihrer Fassung/Beschriftung, und erhalten wie die sichtbaren
Rasterlinien eine subtile Scribble-Optik. Der Inhalt der Miniatur wird auf eigene
Füllungen beschränkt. **Diese Nacharbeit ist noch nicht implementiert.**
Dauerhafter Detailvertrag und ausdrückliche Ablösungen:
[Zeichensprache, Abschnitt VS2-E1](UI_DRAWING_STYLE.md).

Bedien-/Speichergrundlage: [P1](PROTOTYPE_P1.md). Die
[Prüfzuordnung](VS2_VERIFICATION.md) und [Windows-Probe](VS2_OWNER_TRIAL.md)
trennen Erstlieferung und offene Folgearbeit. VS2-M01 hat Änderungsfeedback und
bleibt vor Merge offen; der neue kombinierte Head benötigt technische/visuelle
Nachprüfung und passende Mergefreigabe. Keine Produktänderung durch diese Dokumentation.

Stand: 09.10.2026 · historische GD-Auswahl mit freigegebener VS2-E1-Fortschreibung

Maßgebliche historische Auswahl ist die
[Eigentümerentscheidung GD-01 bis GD-05](https://github.com/venomenon328/picross/pull/32#issuecomment-5855483934)
auf `c3a5386580d7a0da29b927b41bd692f0cca59274`. Sie ersetzt die historische
Bearbeiterempfehlung B in `composition/DECISION.md`. Die hashgebundenen Pakete
production/artwork/composition bleiben unverändert. PR #25/#28 sind keine Basis.

| Auswahl | Bisherige native Grundlage |
| --- | --- |
| GD-01: A, dunkler Inventarband | Unverändertes UI-freies PNG, SHA-256 `957c2eab39b2334825fb159287b9d36a17b77fff1c628ea88110f2cfb5f7a71a`; proportionaler Hintergrund, getrennt von Control-/Rastergeometrie. |
| GD-02: gemeinsame BP-3-UI | Gefasste Miniatur, zwei Metallhalter, gemeinsame Farbmusterfassung, Werkzeugmulden zuletzt 2/2/4, abgeschrägte Controls. Auswahl aus Sessionzustand: Werkzeug dunkel/unterstrichen, Farbe mit äußeren Eckmarkierungen. |
| GD-03: Fraunces / IBM Plex Sans | Fraunces 600 für Blatttitel; Plex Sans für UI/Hinweise als historischer Z2-Stand. ZS wählt Chalkboard für Hinweise. Gepinnte Fontbytes und Nutzungshinweise offline, keine Systemfontsuche. |
| GD-04: C1 | Feste dunkle Kontur für Hinweisfarben 2/4 an beiden Achsen, im Drag und Tooltip; unveränderte RGB-Füllung, Originalindizes und H1. Keine neue Option. |
| GD-05: N1 | Eine native Informations-Control mit gemeinsamem Einstellungen-/Hilfebereich, drei Zugängen und Rückweg. Nur der UI-freie Hintergrund wird gespiegelt; Falz links. |

**Begrenzte Fortschreibung von GD-02 durch VS2-E1:** Die gezeichnete Fassung und
sichere Lage von Miniatur/Palette sind nicht mehr an die alte native Form/Position
gebunden. Vorhandene Funktion, originale Farbflächen, klare Auswahlzustände und
Mindesthitflächen 44/55 px bleiben. Keine neuen Dekoelemente, kein neues Hintergrundbild
und kein pauschaler Umbau aller Werkzeuge. Logische Raster-/Hinweiszuordnung bleibt
präzise; eine handgezeichnete Kontur ist keine verwackelte Hitbox.

Die Wahl des A-Arbeitsassets entscheidet nicht die weiterhin offene gesamte
Themen-/Kapitelstruktur des Produkts. Kein Laufzeit-Themeschalter, neuer Spielkern,
Album-/Statistikbau oder Inhalt aus #24.

## Freigegebener Folgeschritt ZS · 07.10.2026

[ZS-1/#52](https://github.com/venomenon328/picross/issues/52) und
[ZS-2/#53](https://github.com/venomenon328/picross/issues/53) entwickelten die
vorhandene A-Arbeitsansicht gemäß [Detailspezifikation](UI_DRAWING_STYLE.md) weiter.
GD-03 und GP-03 wurden gezielt für kompakte kräftige Hinweisziffern geöffnet:
Form, Gewicht, optische Größe und gegebenenfalls bewusst ausgewählte gemeinsame
Slotmaße. Fraunces-Titel, übrige Plex-UI, C1-Semantik, grundlegende Buchkomposition
und historische hashgebundene Dateien bleiben Grundlage. Die native Wahl ist durch
ZS1-E3/M01 bestätigt; frühere feste Font-/Slotwerte beschreiben ihre jeweilige Lieferung.

E1 wählt Stiftfüllung und historisch 140/80-ms-Timing.
Die bestätigte ZS2-Nacharbeit vom 09.10.2026 verlangsamt auf 210/120 ms und
verlangt sichtbar kurze handschriftliche Schraffurzüge bei gesetzten Feldern.
Handschriftliches X und räumlicher Strichaufbau gehören zur integrierten ZS2-Fassung;
zusätzliche Rand-UI entfällt. Der Vergleich der zwei Eigentümer-TTFs erfolgte auf der
durch E2 akzeptierten Grundlage. Hintergrundarbeit bleibt separat.
Nach ZS2-E2 beginnen die kurzen gerichteten Animationen ausschließlich nach dem
atomaren Anwenden: höchstens 180 ms Startspreizung plus 210 ms je Zelle; Entfernen
sofort/120 ms. Das aktive X schreibt ohne volle Unterzeichnung. Gegentasten-Down
bricht die aktive Zellgeste bis zum Loslassen beider Tasten ab; MMB bleibt nach VS2
ausschließlich Hinweisnavigation. Die Vorschau beim Ziehen bleibt statisch und
heller/transparenter. VS2-E1 verändert diese Bewegungsregeln nicht.

ZS1-E3 wählt Chalkboard Regular. Die damalige Studien-/ZS2-Fassung verwendet
horizontale Zeilenhinweisslots links vom Raster von 26 × UI und vertikale
Spaltenslots von 18 × UI. Diese Auswahl ist mit [ZS-2](ZS2_VERIFICATION.md) regulär
integriert; die kombinierte Sichtprüfung von PR #55 ist nach dessen Merge abgeschlossen.
VS2-E1/N01 verdichtet die horizontale Weite künftig weiter bei gleichem Schriftmaßstab;
18 × UI vertikal, gemeinsame Slotsemantik und die historische Bindung bleiben erhalten.

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
Plex-Ziffern wurden in den festen 18/22,5-px-Spaltenslots um ihren sichtbaren
Ziffernkörper geclippt; die frühere für größere Slots reservierte Oberlänge darf
keinen oberen Marker ausblenden. Render- und Dragregressionen prüfen beide Ränder.

Native Montierungen verwendeten flache Materialfarben und feine Licht-/Randlinien
statt der SVG-Verläufe. Die fünf Referenzzustände wurden ausdrücklich im Capture
gesetzt; das Spiel erhält gespeicherten Zoom und die bisherigen 20 Arbeitsstufen.
Zwischengrößen reservieren zuerst die tatsächlichen Trefferflächen und begrenzen
den Rasterviewport oberhalb der Werkzeuge. Kein unsichtbares Verkleinern der Zellen.
Die in Z2 gebundenen Rastermaße sind Standard-/Referenzflächen, keine Obergrenzen
für spätere Arbeitszoomstufen. [#50](https://github.com/venomenon328/picross/issues/50)
konkretisierte deren Wachstum oberhalb 100 %; VS2 begrenzt inzwischen jeden
angebotenen Zoom auf das vollständige Raster samt Rahmen. Die neuen N01–N04
werden auf dieser Vollsichtgrundlage umgesetzt, nicht auf alten Clippingregeln.

Das A-Master bleibt aufbereitetes 1672×941-Material auf 2560×1440, keine nativ
erzeugte 1440p-Illustration. Untere Retuschestelle und weichere Detailauflösung
bleiben bekannte Grenzen des [BP-2-Prozesses](design/book_inventory/artwork/PROCESS.md).
N1 ist eine reversible Hintergrundableitung, kein drittes fertiges Artwork.

## Prüfbarkeit

[Z2-Prüfbericht und Eigentümerprobe](Z2_VERIFICATION.md) trennen technische
Nachweise und die nicht durchgeführten Z2-M01/M02/M03. Review und Mergefreigabe
von PR #33 sind abgeschlossen; der Eigentümer hob das damalige Probengate auf.
Die reguläre App-Identität `picross · P1`, `user://p1/saves/`, Schema 1, Fixtures,
Revisionen, Deduktionsnachweise und Enthüllungsbilder bleiben erhalten.

VS2-E1 wird in den zwei Teilpaketen aus #61 auf demselben PR #62 nachgearbeitet.
Alte Bilder/Reports bleiben unverändert; neue Abstands-, Anordnungs-, Strich- und
Miniaturpixeloracles erhalten eine eigene Bindung. Die persönliche VS2-M01 bewertet
die neue kombinierte Oberfläche und wird weder aus der historischen Z2-/ZS2-Abnahme
noch aus einem Dokumentationscommit abgeleitet.
