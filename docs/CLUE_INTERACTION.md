# HN: Hinweisnavigation und Cursororientierung

Stand: 16.10.2026 · Spezifikation 0.1 · freigegeben, noch nicht implementiert

## Geltung und Auftrag

[Issue #192](https://github.com/venomenon328/picross/issues/192) führt ein gemeinsames
Paket für Linksdrag überlaufender Hinweisfolgen und passende Linienhervorhebung.
Der Eigentümer hat den besprochenen Sollstand ausdrücklich freigegeben und
Spezifikation samt Umsetzungsvorbereitung beauftragt, keine Produktimplementierung.
Die Freigabe bestätigt die geklärte Lesart: linke statt mittlere Maustaste.

Dieses Dokument führt dauerhafte Entscheidungen; Issue und PR führen Akzeptanz,
Startprüfung, Lieferung und Abnahmen. Die Dokumentationslieferung beginnt denselben
später fortzuführenden PR, ohne vorgeschalteten Merge oder zweites Teilprojekt.
Einstieg bleibt [AGENTS](../AGENTS.md) mit dem lokalen Workflow und
[Projektprofil](PROJECT_PROFILE.md). Zusätzlich gelten [P1](PROTOTYPE_P1.md),
[Hinweis-Typografie](CLUE_TYPOGRAPHY.md), [Hinweisstatus](CLUE_STATUS.md),
[Zellgesten](CELL_DRAG.md), [Zeichensprache](UI_DRAWING_STYLE.md) und bei der
Cursorinvalidierung [Zellrendering](CELL_RENDERING.md).

## HN-D01: Linksdrag nur bei tatsächlichem Hinweisüberlauf

Die linke Maustaste startet im zugeordneten Randhinweisbereich einer tatsächlich
gekürzten Folge deren Navigation. Die konkrete Achse und Linie werden beim Down
festgelegt. Zeilenhinweise bewegen sich nur horizontal, Spaltenhinweise nur vertikal.
Nur diese Folge folgt kontinuierlich der Maus; Nachbarfolgen bleiben unverändert.
Die mittlere Taste startet keine Hinweisnavigation mehr. Mausradzoom bleibt erhalten.

Das ist ein Wechsel der Taste, keine neue Draggeometrie: gemeinsame gemessene Slots,
Originalreihenfolge, vollständige Tokens, echte Präfix-/Suffixmarker, monotone direkte
Bewegung, geometrisch nächster gültiger Drop-Snap und der erhaltene Variante-A-
Außenanschlag bleiben. Die G-Mindestgarantie und V-Vollsicht werden nicht verändert.
Vollständig passende, kurze und leere Folgen lassen sich nicht in Leerraum ziehen.
Ein unveränderter Klick ohne wirksame Verschiebung ist keine neue Spielaktion.

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

Das Overlay selbst wird nicht verschiebbar oder anheftbar. Bestehende Öffnungs-/
Schließbedingungen, kleinere Fraunces-Überschrift, Delight-Zahlen, Papier, Rahmen,
Umbruch und zoomunabhängige Lesegröße bleiben. Die Box darf die von ihr bedeckte
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

Unverändert bleiben H1/GP48, das HS-Ganzzahl-X und seine Deckkräfte/Identitäten,
Fontbytes, Palette, G/V-/Fit-/Kapazitätsregeln, semantische Leseanker, Zellatlanten,
56-%-Vorschau, Zellanimationen, eigene Miniatur, History, Save-Schema/Recovery,
Abschluss und Spoilergrenze. Keine Bestandsrätseltests oder Neuzertifizierung.

## Gezielte Ablösung und Dokumentationsübergang

HN-D01–D05 ersetzen für dieses Paket ausschließlich die folgenden bisherigen
Sollregeln. Nicht betroffene Verträge und historische Nachweise bleiben erhalten.

| Zuständige Quelle | Gezielte Änderung |
| --- | --- |
| [P1](PROTOTYPE_P1.md), VS2 und §5.2 | Exklusive Mitteltaste für Hinweisdrag wird durch linke Taste ersetzt; Drag-/Snap-/Leseankerregeln bleiben. D-25 wird um einachsige Hinweisorientierung ergänzt. |
| [Produktdefinition](PRODUCT_DEFINITION.md), §5.1 | Mittlere Taste als ausschließliche Hinweisnavigation entfällt; vorhandene Zellgesten und Komfortgrenzen bleiben. |
| [Gestaltungskonzept](DESIGN_CONCEPT.md), §5.1 | Entsprechende Tastenbindung und Cursororientierung einschließlich Vollhinweis folgen HN. |
| [Zeichensprache](UI_DRAWING_STYLE.md), ZS-D08, und [Z2-Auswahl](Z2_SELECTION.md) | Nur die Mitteltastenbindung der Hinweise wird abgelöst, nicht Gegentastenabbruch oder Zellbewegung. |
| [Hinweis-Typografie](CLUE_TYPOGRAPHY.md) und [Zellgesten](CELL_DRAG.md) | Aktuelle Bedienverweise zu MMB folgen HN; Typografie und Ausschluss des Zellzählers bei Hinweisnavigation bleiben. |
| [Projektprofil](PROJECT_PROFILE.md) und aktive Hilfe-/Prüftexte | Nach Implementierung tatsächliche Tasten-/Orientierungsbeschreibung konsistent führen, historische MMB-Prüfberichte nicht umschreiben. |

**Jetzt ist nur die Spezifikation geliefert.** Die Laufzeit und die
[Spielanleitung](../game/README.md) beschreiben weiterhin den bisher implementierten
Stand. Spätestens im zugehörigen Implementierungs-PR werden betroffene aktive
Fachstellen, native Hilfe, Anwenderanleitung und aktuelle Prüfzuordnung inline
nachgeführt; dann auch den Sollstand-Hinweis in AGENTS aktualisieren. Dieser
explizite Übergang verhindert eine falsche Behauptung bereits gelieferter Bedienung.
Die neue Pflichtquelle ist unmittelbar im Agenteneinstieg eingebunden; keine
Änderung oder zentrale Aktualisierung von `docs/dev-rules/`.

## Prüfung und Abnahme

Issue #192 bindet HN-A01–A07 und die getrennten Gates HN-T01, HN-R01 und HN-M01
vor Implementierungsmerge. Echte Mausereignisrouten, sichtbare native Bänder/Overlay,
Zell-/History-Negativfälle, Cursorcache-Gegenprobe und aktuelle Save-/Browser-/
Windows-Exportnachweise ergänzen einander. Eine interne Hovervariable oder ein
Dokumenttest allein beweist keine sichtbare und sichere Interaktion.

[CI-Policy](CI_POLICY.md) entscheidet die vollständige Diffauswahl und die kompakte
Fenstermatrix; [Webvertrag](WEB_HOSTING.md) begrenzt den bestehenden Browserprüfweg.
Nur isolierte technische Profile, kein Zugriff auf echte Saves oder den Eigentümer-VPS.
Native Windows-Originale sind für unabhängige Prüfung tatsächlich zugänglich zu
liefern und an Head/Basis/Checkout, Run, EXE/PCK und Umgebung zu binden. Ein
Linux-Render/Windows-Export ist kein tatsächlicher Windows-Start; technische
Automation ersetzt keine persönliche Bedienabnahme.

Keine allgemeine UI-/Eingabeplattform, neue Optionen, Produktionsinhalte, Assets,
Saveformate, CI-Optimierung, Merge, Release oder Deployment aus dieser Spezifikation.
