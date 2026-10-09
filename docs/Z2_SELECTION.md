# Z2: aktive Auswahl und native Integration

## Aktueller regulärer Stand · VS2 (#61)

Die gewählte A-Komposition bleibt. VS2 ordnet die Arbeitsfläche für vollständige
Raster neu; Werkzeugmulden 2/2/4, passive eigene Miniatur, benannte Ansichtsoption
ausschließlich in Einstellungen. Z2-Herkunft und historische Designs bleiben.

Bedien-/Speichervertrag: [P1](PROTOTYPE_P1.md). Aktuelle
[Prüfzuordnung](VS2_VERIFICATION.md) und [Windows-Probe](VS2_OWNER_TRIAL.md).
VS2-M01, unabhängiges technisches/visuelles Review und passende Mergefreigabe
bleiben vor Merge offen. Historische Nachweise bleiben commitgebunden.


Stand: 27.09.2026 · #23 / I-01 bis I-05 unter #21

Maßgeblich ist die [Eigentümerentscheidung GD-01 bis GD-05](https://github.com/venomenon328/picross/pull/32#issuecomment-5855483934)
auf `c3a5386580d7a0da29b927b41bd692f0cca59274`. Sie ersetzt die historische
Bearbeiterempfehlung B in `composition/DECISION.md`. Die hashgebundenen Pakete
production/artwork/composition bleiben unverändert. PR #25/#28 sind keine Basis.

| Auswahl | Native Umsetzung |
| --- | --- |
| GD-01: A, dunkler Inventarband | Unverändertes UI-freies PNG, SHA-256 `957c2eab39b2334825fb159287b9d36a17b77fff1c628ea88110f2cfb5f7a71a`; proportionaler Hintergrund, getrennt von Control-/Rastergeometrie. |
| GD-02: gemeinsame BP-3-UI | Gefasste Miniatur, zwei Metallhalter, gemeinsame Farbmusterfassung, Werkzeugmulden 2/2/4, abgeschrägte Controls. Auswahl aus Sessionzustand: Werkzeug dunkel/unterstrichen, Farbe mit äußeren Eckmarkierungen. |
| GD-03: Fraunces / IBM Plex Sans | Fraunces 600 für Blatttitel; Plex Sans für UI/Hinweise. Gepinnte Fontbytes und OFL offline im regulären Export, keine Systemfontsuche. |
| GD-04: C1 | Feste dunkle Kontur für Hinweisfarben 2/4 an beiden Achsen, im Drag und Tooltip; unveränderte RGB-Füllung, Originalindizes und H1. Keine neue Option. |
| GD-05: N1 | Eine native Informations-Control mit gemeinsamem Einstellungen-/Hilfebereich, drei Zugängen und Rückweg. Nur der UI-freie Hintergrund wird gespiegelt; Falz links. |

Die Wahl des A-Arbeitsassets entscheidet nicht die weiterhin offene gesamte
Themen-/Kapitelstruktur des Produkts. Kein Laufzeit-Themeschalter, neuer Spielkern,
Album-/Statistikbau oder Inhalt aus #24.

## Freigegebener Folgeschritt ZS · 07.10.2026

[ZS-1/#52](https://github.com/venomenon328/picross/issues/52) und
[ZS-2/#53](https://github.com/venomenon328/picross/issues/53) entwickeln die
vorhandene A-Arbeitsansicht gemäß [Detailspezifikation](UI_DRAWING_STYLE.md) weiter.
GD-03 und GP-03 werden gezielt für kompakte kräftige Hinweisziffern geöffnet:
Form, Gewicht, optische Größe und gegebenenfalls bewusst ausgewählte gemeinsame
Slotmaße. Fraunces-Titel, übrige Plex-UI, C1-Semantik, grundlegende Buchkomposition
und historische hashgebundene Dateien bleiben Grundlage. Die native Wahl ist durch ZS1-E3/M01 bestätigt; frühere feste Font-/Slotwerte
unten beschreiben den historischen integrierten Z2-Stand.

E1 wählt Stiftfüllung und historisch 140/80-ms-Timing.
Die bestätigte ZS2-Nacharbeit vom 09.10.2026 verlangsamt auf 210/120 ms und
verlangt sichtbar kurze handschriftliche Schraffurzüge bei gesetzten Feldern. Es folgen ein handschriftlicheres X
und räumlicher Strichaufbau; zusätzliche Rand-UI entfällt. Der Vergleich der zwei
Eigentümer-TTFs erfolgt auf der durch E2 akzeptierten Grundlage. Hintergrundarbeit bleibt separat.
Nach ZS2-E2 beginnen die kurzen gerichteten Animationen ausschließlich nach dem
atomaren Anwenden: höchstens 180 ms Startspreizung plus 210 ms je Zelle; Entfernen
sofort/120 ms. Das aktive X schreibt ohne volle Unterzeichnung. Gegentasten-Down
bricht die aktive Zellgeste bis zum Loslassen beider Tasten ab; MMB bleibt ausschließlich Hinweisnavigation.
Die Vorschau beim Ziehen bleibt statisch und heller/transparenter. Die neue
Spezifikation ist keine bereits gelieferte oder abgenommene Z2-Änderung.


ZS1-E3 wählt Chalkboard Regular. Für die Studienfassung werden nur die horizontalen
Zeilenhinweisslots links vom Raster auf 26 × UI-Skalierung verdichtet; die
Spaltenhinweisslots bleiben 18 × UI. Diese Auswahl wird mit der beauftragten [ZS-2-Integration](ZS2_VERIFICATION.md)
regulär verwendet. Die kombinierte Sichtprüfung von PR #55 ist nach dessen Merge auf main abgeschlossen.

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
Die in Z2 gebundenen Rastermaße sind Standard-/Referenzflächen, keine Obergrenzen
für spätere Arbeitszoomstufen. [#50](https://github.com/venomenon328/picross/issues/50)
konkretisiert dies: oberhalb 100 % darf der native Viewport in freie Papierfläche
wachsen, solange dieselben Treffer-/Hinweis-/Bediengrenzen erhalten bleiben.

Das A-Master bleibt aufbereitetes 1672×941-Material auf 2560×1440, keine nativ
erzeugte 1440p-Illustration. Untere Retuschestelle und weichere Detailauflösung
bleiben bekannte Grenzen des [BP-2-Prozesses](design/book_inventory/artwork/PROCESS.md).
N1 ist eine reversible Hintergrundableitung, kein drittes fertiges Artwork.

## Prüfbarkeit

[Z2-Prüfbericht und Eigentümerprobe](Z2_VERIFICATION.md) trennen technische
Nachweise und die nicht durchgeführten Z2-M01/M02/M03. Review und Mergefreigabe
von PR #33 sind abgeschlossen; der Eigentümer hob das damalige Probengate auf. Die reguläre
App-Identität `picross · P1`, `user://p1/saves/`, Schema 1, Fixtures, Revisionen,
Deduktionsnachweise und Enthüllungsbilder bleiben erhalten.
