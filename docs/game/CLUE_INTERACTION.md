# HN · Hinweisnavigation und Cursororientierung

## Geltung und Zuständigkeit

Dieser Vertrag besitzt Hinweisdrag, geometrischen Drop, Eingabebesitz,
Cursorlinien und die Interaktion des Vollhinweis-Overlays. Die Regeln im aktuellen
Git-Stand sind vom Liefer- und Abnahmestand im Issue/PR zu unterscheiden.

| Detail | Maßgebliche Quelle |
| --- | --- |
| Schrift, Slots, Fit und Overlaydarstellung | [CLUE_TYPOGRAPHY](CLUE_TYPOGRAPHY.md) |
| Sichtbarer Hinweisstatus | [CLUE_STATUS](CLUE_STATUS.md) |
| H1-Erkennung, semantische Anker und Speicherung | [P1](PROTOTYPE_P1.md) |
| Zellgeste / Fortsetzung an Rändern | [P1](PROTOTYPE_P1.md), [CELL_DRAG](CELL_DRAG.md) |
| Cursor-/Rendercachetrennung | [CELL_RENDERING](CELL_RENDERING.md) |

## HN-D01: Linksdrag nur bei tatsächlichem Hinweisüberlauf

Die linke Maustaste startet im zugeordneten Randhinweisbereich einer tatsächlich
gekürzten Folge deren Navigation. Die konkrete Achse und Linie werden beim Down
festgelegt. Zeilenhinweise bewegen sich nur horizontal, Spaltenhinweise nur vertikal.
Nur diese Folge folgt kontinuierlich der Maus; Nachbarfolgen bleiben unverändert.
Die mittlere Taste startet keine Hinweisnavigation. Mausradzoom bleibt erhalten.

Gemeinsame gemessene Slots, vollständige Tokens, echte Präfix-/Suffixmarker,
G-Mindestgarantie und V-Vollsicht folgen [CLUE_TYPOGRAPHY](CLUE_TYPOGRAPHY.md).
Der Drag bewegt die Originalfolge monoton und direkt; Drop bestätigt die
geometrisch nächste gültige ganzzahlige Slotlage.
Vollständig passende, kurze und leere Folgen lassen sich nicht in Leerraum ziehen.
Ein unveränderter Klick ohne wirksame Verschiebung ist keine neue Spielaktion.

Der geometrische Außenanschlag ist selbst
`outer_start`; dort darf ein physisch möglicher Tokenplatz frei bleiben, wenn seine
Belegung die Zahlen entgegen der bisherigen Dragrichtung verschieben würde.
Es gibt keinen zusätzlichen, nur durch Gegenbewegung erreichbaren Randzustand.
Wiederholtes Ziehen mit gleichem Vorzeichen führt vom Rasterende bis zum äußeren
Anfang; der Rückweg verwendet durchgehend das Gegenzeichen. Die Darstellung wird
bereits während des Drags an diesen geometrischen Grenzen begrenzt. Alle Tokens
müssen über die erreichbare Zustandsfolge vollständig lesbar bleiben.

## HN-D02: Eindeutiger Eingabebesitz bis zum Abschluss

Ein im Hinweisbereich gestarteter Linksdrag bleibt Hinweisnavigation, auch beim
Überfahren oder Loslassen über Raster, Nachbarhinweisen, Overlay oder anderer UI.
Er wird niemals zu Füllen, Radieren, X-Setzen oder einer zusätzlichen Buttonaktion.
Down, Bewegung und zugehöriges Up müssen derselben Geste zugeordnet bleiben.
Ein im nicht navigierbaren Hinweisbereich begonnener Klick darf beim Hineinziehen
ins Raster ebenfalls keine Zellgeste nachträglich beginnen.

Umgekehrt bleibt eine im Raster begonnene Zellgeste dem bestehenden P1-/ZR-Vertrag
unterworfen; beim Überfahren von Hinweisen entsteht kein Hinweisdrag. Während einer
Zellgeste ist neue Hinweisnavigation gesperrt. Achsenneuwahl, Vorbelegungsschutz,
Gegentastenabbruch, atomarer Commit, Undo/Redo und ZR-Randfortsetzung bleiben erhalten.
Hinweisnavigation zeigt keinen Zellgestenzähler und erzeugt keine Zellvorschau.

Die Freigabe der Ursprungstaste bestätigt ausschließlich den zulässigen
Hinweislesezustand. Falsches Up beendet keinen Drag. Escape, echter Fokusverlust
und die bestehenden Layout-/Ansichts-/Sessionübergänge verwerfen den temporären
Versatz zugunsten der letzten bestätigten Leseposition. Verlorene oder mehrdeutige
Tastenzustellung darf weder nachträglich committen noch eine Phantomgeste starten.
Nach Abbruch bleibt die normale neue Eingabe möglich; kein Hängen der Erfassung
oder Sperre. Konkurrenz mit linker/rechter Zellbedienung gezielt absichern, keine
neue allgemeine Tasten-/Modifierkonfiguration einführen.

Nur bestätigte semantische Leseanker werden wie bisher als Ansicht gesichert.
Temporäre Dragposition, Hover und hervorgehobene Linie sind kein Saveinhalt.
History, Zellen, Farbe, Rasterzentrum/-zoom und Miniatur bleiben durch Hinweisdrag
unverändert; die vorhandene Sicherung bestätigter Ansichtsänderungen bleibt wirksam.

## HN-D03: Hervorhebung aus der gültigen Kontextquelle

| Kontext | Hervorhebung im Raster und zugehörigen Hinweisbereich |
| --- | --- |
| Gültiger Rastertreffer ohne laufende Geste | Aktuelle Zeile und Spalte wie bisher; Schnittpunkt nicht doppelt betonen. |
| Zeilenhinweisbereich mit gültigem Linienindex | Ausschließlich diese Zeile. |
| Spaltenhinweisbereich mit gültigem Linienindex | Ausschließlich diese Spalte. |
| Laufender Hinweisdrag | Ausschließlich die am Start eingefrorene Quellenlinie, auch beim Überfahren anderer Linien oder des Rasters. |
| Laufende Zellgeste | Vorhandener gültiger Gestenendpunkt gemäß P1/ZR, keine Umdeutung in Hinweis-Hover. |
| Kein gültiger Kontext mehr | Keine veraltete Markierung; nach einem Kontextwechsel frisch zuordnen. |

Hinweis-Hover besitzt nur eine gültige Achse. Die andere wird nicht aus dem letzten
Rastertreffer übernommen oder durch Begrenzung auf eine Randzelle erfunden. Der
reine Orientierungskontext darf insbesondere keine editierbare Zelle vortäuschen.
Die Regel gilt auch bei vollständigen Folgen ohne Overlay und ohne Dragmöglichkeit.
Hinweiswerte, Farben und Erledigtzustände ändern die Quellenzuordnung nicht.

Die vorhandene dezente Bandgestaltung bleibt: unter lesbaren Füllungen, X und
Rasterlinien, ohne neue Warnfarbe, doppelte Kreuzungsstärke oder neue Animation.
Keine Hervorhebung außerhalb der gültigen Raster-/Hinweisgeometrie. Ein Wechsel
zwischen Raster, Zeilenhinweisen und Spaltenhinweisen entfernt die alte zweite Achse
unmittelbar; keine dauerhaft gepinnte Auswahl.

## HN-D04: Vollhinweis ergänzt die Orientierung statt sie zu unterbrechen

Solange der bestehende nichtmodale Vollhinweis eine gültige Hinweisquelle anzeigt,
bleibt deren Zeile beziehungsweise Spalte hervorgehoben. Das Einblenden allein
entfernt diese Orientierung nicht. Die Quellenlinie und eine gegebenenfalls aktive
Hinweisgeste werden gemeinsam ausgewertet; kein zufälliger Bezug auf Zellen hinter
der Box. Bei Wechsel der Hinweisquelle folgt die Markierung der neuen Quelle.

Das Overlay selbst wird nicht verschiebbar oder anheftbar. Darstellung, Umbruch, Rahmen, zoomunabhängige Lesegröße und sichere Hüllen
stehen in [HC/HF](CLUE_TYPOGRAPHY.md), die Überschriftrolle in HZ.
Die Box darf die von ihr bedeckte
Rasterfläche weiterhin abdecken; Bänder werden nicht über Text oder Rahmen gemalt.
Die passende Markierung bleibt außerhalb dieser natürlichen Überdeckung sichtbar.

Klicks auf die sichtbare Box werden weiterhin konsumiert und erreichen keine
Rasterzelle darunter. Die Bandanzeige erteilt kein Durchklickrecht. Beim Schließen
keine unsichtbare Trefferfläche zurücklassen; kein neuer Pin-, Scroll-, Klick- oder
Overlay-Dragmodus. Dekorative Markierungen fangen selbst keine Eingaben ab.

Zoom, Resize, UI-Skalierung, G/V-, Definitions-/Blattwechsel und Wiederherstellung
bewerten Quelle, Bandgeometrie sowie Overlay-/Trefferrechteck gemeinsam neu, auch
unter ruhender Maus. Eine nun vollständige oder ungültige Folge behält kein altes
Overlay. Gültiger Hinweis-Hover kann bei Vollanzeige weiterhin seine eine Linie
markieren. Fokus-/Seitenverlust darf keinen alten Quellenzustand in ein neues Blatt
übertragen; Wiederkehr verwendet nur einen aktuell gültigen Kontext.

## HN-D05: Getrennte Cursoraktualisierung und unveränderte Verträge

Der reguläre optimierte Motionpfad und der eigenständige Cursorzeichner müssen
Raster-Hover, Hinweisquelle und eingefrorenes Dragziel konsistent verwenden.
Quellenwechsel und relevante Geometrieänderungen gehören in dessen transienten
Invalidierungszustand. Ein gültiges X-und-Y-Paar ist keine Voraussetzung für ein
einzelnes Zeilen- oder Spaltenband. Ein bloßer Konstanten- oder Z-Index-Tausch
ist kein Nachweis des gesamten Verhaltens.

Die Cachetrennung nach PERF-D05 bleibt. Reines Hover oder ein Quellenwechsel
bauen nicht den ruhenden Zellbestand vollständig neu auf und lösen keine neue
H1-Analyse aus. Keine pro Frame neu geladene Ressource, unbeschränkte Historie
von Hoverzuständen oder Vollneuberechnung des Fits. Bestehende Glyphen-/Slot-/
Statushüllen und Zell-/Overlayressourcen werden nicht für die Eingabe neu gestaltet.

H1-Erkennung, bestätigte Leseanker und Speicherregeln folgen P1; die
Darstellung der abgeleiteten Statuswerte folgt CLUE_STATUS. HN ergänzt keine
Produktions-, Eingabe-, Save- oder Spielmechanik.

## Prüfung und Abnahme

HN-A01–A07 und ursprüngliche T01/R01/M01-Ergebnisse stehen in
[#192 / PR #193](https://github.com/venomenon328/picross/pull/193).
Echte Mausereignisrouten, sichtbare Bänder/Overlay, negative Zell-/Historyfälle
und Cursorcache-Gegenproben belegen unterschiedliche Aspekte. Eine interne
Hovervariable oder ein Dokumenttest allein belegt keine sichtbare Interaktion.
Aktuelle Modulauswahl folgt [CI_WORKFLOW_V2](../ci/CI_WORKFLOW_V2.md), Stichprobe und
bewusste Lücken [CI_C_NATIVE_GROUPS](../ci/CI_C_NATIVE_GROUPS.md).

## Herkunft und Nachweise

Fachentscheidungen und tatsächliche Review-/Abnahmeergebnisse: [#192](https://github.com/venomenon328/picross/issues/192) und [PR #193](https://github.com/venomenon328/picross/pull/193).
Der [historische Dokumentstand](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/CLUE_INTERACTION.md)
erhält frühere Lieferchronologie und ersetzte Regeln. Er ist keine zusätzliche
Normquelle oder dauerhafte Prüfpflicht. Aktuelle Prüfungen folgen dem
[Paketvertrag](../ci/CI_WORKFLOW_V2.md) und dem jeweils betroffenen Modul.
