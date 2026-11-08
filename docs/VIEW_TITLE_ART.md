# BTI · Bildbasierte Hauptüberschriften der Buchansichten

**BTI-C · V2-rev1-Integration auf dem Arbeitsbranch, eigene T01/R01/M01-Gates.**
Maßgeblich ist [BTI-C mit D01–D03 und A01–A08](https://github.com/venomenon328/picross/issues/533#bti-c).
Die drei konkreten V2-rev1-Originale sind durch BTI-B-M01 persönlich freigegeben
und unabhängig am Original geprüft. Keine neue Stilwahl oder Generierung.
Die [Stilquelle](design/view_titles/STYLE.md) und das aktive Manifest binden
die unveränderten Bytes; aktuelle Integrationsnachweise stehen in
[Draft-PR #534](https://github.com/venomenon328/picross/pull/534).
Alte BTI-A-Nachweise gelten nur ihrem damaligen Stand.

## BTI-D01 · Rolle und exakte Texte

| Buchansicht | Einziger betroffener großer Seitentitel | Platz |
| --- | --- | --- |
| Katalog | **Rätselkatalog** | Kopf der linken aufgeschlagenen Buchhälfte |
| Hilfe | **Hilfe** | Kopf der rechten Informationsbuchseite; ersetzt nur den bisher sichtbaren Haupttitel „Spielerhilfe“ |
| Einstellungen | **Einstellungen** | Kopf der linken Informationsbuchseite |

Alle drei werden **als lokal gebündelte, generativ hergestellte transparente Schriftzugbilder** dargestellt, nicht als zur Laufzeit mit einem Font gesetzter Schriftzug. Keine KI-Anfrage im Spieler und keine Abhängigkeit von einem externen Dienst. Der exakte Text wird als semantischer UI-/Accessibilityname und bei fehlender Bildressource als gut lesbarer Textfallback vorgehalten; keine doppelte sichtbare Beschriftung im Normalfall. Für die Hilfe darf der interne funktionale Begriff „Spielerhilfe“ bleiben; ausschließlich die große sichtbare Überschrift lautet „Hilfe“.

**Begrenzte typografische Vorrangregel:** Auf dem BTI-C-Arbeitsbranch ersetzen diese Bilder an *genau diesen drei Stellen* die jeweiligen bisherigen Bakso-/Fraunces-Labels aus [HZ-D01/D08](HAND_DRAWN_UI.md), [ANZ](DISPLAY_SETTINGS.md), [HIL](BOOK_INTEGRATION.md) und dem [Gestaltungskonzept](DESIGN_CONCEPT.md). Die bisherigen Labels bleiben lesbare Ressourcenfallbacks. Unberührt bleiben die Bakso-Gruppentitel „Anzeige“ und „Rätselansicht“ samt Titellaschen, sonstige Kachel-/Arbeitsblatt- und Abschlussüberschriften, Hilfe-Abschnitts- und Werkzeugüberschriften in Bakso gemäß [HIL-TYPO-D01](https://github.com/venomenon328/picross/issues/535), Pangolin-Normaltext, Plex-Dialog-/Fallbacktext sowie Delight-Hinweiszahlen. Keine neue allgemeine Text- oder Fontoption.

## BTI-D02 · Die freigegebene Zeichenhand

**Freigegebene Zeichenhand: V2-rev1, dunkles neutrales offen schraffiertes Graphit.**
Individuelle leicht geneigte breite Buchstaben, raue nachgezogene Konturen,
wechselnde Höhen, Grundlinie und Abstände; grobe diagonale Striche mit offenen
Zwischenräumen. Kein dominantes Braun/Sepia, keine glatt perfekte Kalligrafie
oder nur verrauschte TTF. Die drei Originale bleiben unverändert.

Hilfe besitzt einen linkswärts aus dem unteren f-Ende wachsenden Querzug,
Einstellungen einen längeren aus dem unteren g-Bogen. Diese buchstabengebundenen
Schwünge sind freigegeben, kein pauschaler Unterstrichverzicht. Beim Katalog wird
kein Anschluss erzwungen. Keine eigenständigen Blätter, Rahmen, Banner, Icons
oder weiteren Illustrationen. Wortproportionen erhalten, Hilfe nicht strecken.
Die konkrete Familie und Details sind bereits in BTI-B-M01 freigegeben;
BTI-C-M01 beurteilt ihre tatsächliche größere Wirkung und Bedienbarkeit im Spiel.

## BTI-D03 · Nachvollziehbare spätere Produktion

Reproduzierbarkeit bedeutet hier **weitgehend konsistent fortsetzbare Letteringgestaltung**, nicht das Versprechen, dass ein generatives Bildmodell mit demselben Prompt byteidentische Ergebnisse ausgibt. Darum sind **Stilbrief, tatsächliche Vorlagen und reale Quellen-/Bearbeitungsdaten zusammen** aufzubewahren. Prompt, Seed oder Modellname allein genügen nicht.

Der textunabhängige aktuelle Brief steht in [STYLE](design/view_titles/STYLE.md).
Die tatsächlichen vollständigen Prompts und Referenzketten der V2-Erstproduktion
und vier Revisionsaufrufe bleiben in
[provenance.json](../game/art/drawing/view_titles/provenance.json) erhalten.
Backend-/Modellversion, Seed und unexponierte Parameter sind unbekannt.
G4 war generative Sprenkelbereinigung, keine manuelle oder deterministische
Retusche. Keine nachträgliche Freistellung, Beschneidung oder Neucodierung
der freigegebenen finalen Bytes. Rechte-/Herkunftsgrenzen stehen in NOTICE.

Genau drei verlustfreie RGBA-PNGs unter `game/art/drawing/view_titles/`:
`catalog.png`, `help.png`, `settings.png`. Manifest bindet Namen, Maße, Bytezahlen,
SHA-256 sowie Alphahüllen. Die optische Hülle bei Alpha ≥16 bestimmt die
Zentrierung; die gesamte PNG-Fläche einschließlich sehr schwacher Alpha-1-Reste
wird proportional um diesen Mittelpunkt eingepasst, mit vier Pixeln Reserve.
Kein Clipping der ä-/i-Punkte und f-/g-Enden. Godot importiert verlustfrei mit
Mipmaps; Windows/Web liefern Titel und aktive Herkunftsressourcen offline.
Keine dauerhafte Varianten-/Reviewgalerie. Historische Quellen nicht überschreiben.

## BTI-D04 · Geschützte Buch-/UI-Anordnung

**Katalog:** Das Bild ersetzt nur den sichtbaren `Rätselkatalog`-Titel in einem größeren, aus der Papierhöhe bestimmten Kopfbereich und ist innerhalb der *projizierten sicheren linken Papierhälfte* horizontal zentriert. Nicht fensterweit oder über dem Buchfalz. `game/book/content.gd` besitzt bereits getrennte Papierkoordinaten und eine rechte Zusammenfassung; deren Maße und die Filter-/Scroll-/Kartenflächen nicht durch einen festen Titel überdecken. Die aktuelle `title`-Labelrolle dient auch dem Arbeitsblatt und darf dafür nicht entfernt oder versehentlich zu einem Bildtitel gemacht werden.

**Hilfe/Einstellungen:** Auf der aktuell sichtbaren rechten beziehungsweise linken Informationsseite bilden drei feste Bereiche das Layout: **zentrierter Bildhaupttitel oben**, **unabhängig scrollender Inhaltsbereich in der Mitte**, **feste Navigation unten**. Haupttitel liegen außerhalb der Textscrollfläche, so dass sie beim Scrollen stehen bleiben. Bestehende Einstellungsgruppen, die begrenzte mittige Gruppengeometrie und die vier Kapitelzugänge bleiben erhalten. Gemäß [HIL-REG-A](BOOK_INTEGRATION.md#spielerhilfe--hil-1--500) steht das Kapitelregister fest außerhalb des separaten Artikelclips; bei knapper Breite als umbrechende Textleiste. Das interne Hilfe-Label „Spielerhilfe“ verschwindet nur aus der sichtbaren Hauptrolle; andere Hilfe-Kapitelüberschriften bleiben echte Textlabels.

**Untere Navigation:** Auf *beiden* Informationsbuchseiten sind `Zurück` und der Gegenansichtswechsel (`Hilfe →` beziehungsweise `← Einstellungen`) außerhalb des Scrollinhalts am unteren sicheren Papierrand anzuordnen. Linkes/rechtes Bedienziel, 44×44 bei UI100 beziehungsweise 55×55 bei UI125, stabile Tooltips/Accessibilitynamen, Hover/Fokus, nicht verdeckte Treffflächen, bestehende Hilfe-/Einstellungs-Lesestände und Besuchsursprung bleiben. Nicht mit unten reserviertem Status-/Save-Retryraum kollidieren. `game/book/information.gd` berechnet diesen sicheren Platz aus projizierter Papierfläche; auch Fenster-Resize, UI100→125→100, Blattbewegung/Camera-Capture, Fokus, Lesestellen und Ladefehler halten diese Anordnung. Die bisherige Hilfeformulierung „Rückweg oben“ wird bei Umsetzung zusammen mit dem sichtbaren UI konsistent angepasst.

**Prioritäten bei engem Platz:** echte Buch-/Papiergrenze, vollständig erreichbare Navigation und Status-/Fehlermeldung vor dekorativer Größe. Bildtitel proportional verkleinern und den Scrollraum begrenzen, statt Konturen abzuschneiden, Bedienelemente zu verstecken oder Inhalte über den Falz zu legen. 1280×720 ist der eingeschränkte Fallback; 1920×1080 primärer Komfortfall; 2560×1440 und 16:10 nutzen die zusätzliche Fläche ohne willkürliche Aufblähung. Keine Änderung an Buchkörper, Seitenlogik, Animationstiming, Saves, Rätseln, Sortierung oder Raster.

## BTI-D05 · Lieferung und Abnahmegrenzen

Die **Paketkriterien BTI-C-A01–A08**, die begründete Modulauswahl, das befristete aktuelle Original-Review sowie die **getrennten BTI-C-T01/R01/M01-Gates** stehen vollständig in [Issue #533](https://github.com/venomenon328/picross/issues/533). Bei tatsächlicher Implementierung wird im Paketplan grundsätzlich `native.catalog` mit den betroffenen Katalog-/Informationspfaden geprüft; die kurze aktuelle Standard-CI liefert den Windowsspieler. Manuelle echte Windows-/UI-Sicht auf die Bildoriginale sowie die funktionalen Navigationsregressionen bleiben zusätzliche eigenständig zu belegende Erfordernisse. `native.graphics` und Chromium werden ohne weiteren Änderungsbezug nicht ausgewählt. Keine großflächige Dauer-Screenshotmatrix und keine dauerhafte temporäre Galerie. Vor dem Produktmerge sind unabhängiger Diff-/Originalreview und **persönliche Sichtabnahme** am konkreten Spieler-Head offen.

**Spezifikations-/Implementierungsgrenze:** Eine Dokumentenfassung auf dem BTI-C-Branch ist kein Nachweis dafür, dass eines der PNGs, die Layoutänderung, ein Windowsstart oder eine Eigentümerprobe bereits stattgefunden haben.
