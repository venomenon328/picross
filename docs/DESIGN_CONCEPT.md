# Gestaltungskonzept: Album, Rätselarbeit und Enthüllung

Stand: 26.09.2026 · Arbeitsfassung 0.11 · frühe Konzeption mit P1-Mausfeedback, G1, H1 und Buchuntersuchung

## 1. Geltung und Entscheidungsstand

Dieses Dokument überträgt die Gestaltungskonversation zu Punkt 2 des Entwicklungsablaufs in die Repositoryquellen. Die [Produktdefinition](PRODUCT_DEFINITION.md) bleibt für Produktkern, Rätselregeln, Progression und Wertung maßgeblich; hier stehen die visuelle Konkretisierung und ausdrücklich noch offene Entwurfsfragen. Prüfwege und Befugnisse stehen im [Projektprofil](PROJECT_PROFILE.md).

Die ausdrücklichen Antworten des Nutzers begründen die bestätigten Entscheidungen in Abschnitt 2. Die Rückmeldung „Sieht gut aus“ zu exemplarischen Mocks bestätigte deren grundsätzliche gestalterische Richtung, nicht jeden Bildinhalt, jede Zahl, jedes Werkzeug oder eine fertig geprüfte Bedienung. Abschnitt 3 erhält die offenen Themenalternativen. Abschnitte 4–5 enthalten Entwurfsansätze, soweit nicht ausdrücklich durch das nachfolgende Nutzerfeedback konkretisiert.

Die reale P1.1-Mausprobe ergänzt zunächst vier Punkte: größeres Standardfenster ohne
automatisch riesige Raster, sichtbar getrennte Füllzellen auch an Fünferlinien,
direktes Neutralisieren mit dem normalen Werkzeug und detailliertere motivtreue
Abschlussbilder. Die folgende P1.2-Probe ergänzt den supersedierenden Sollstand D-11
bis D-15: keine Randnummerierung oder separate Hinweisansicht, vollständiger
In-Context-Hinweiszugriff, feinere monotone Zoomstufen, farbige Hinweiszahlen mit
optionalen Kennungen und direkte Füllung↔X-Umwandlung. Die nächste Probe konkretisiert
D-16/D-17: Überlauf lässt vollständige einzelne Hinweiszahlen sichtbar, und Zeilen-/
Spaltenhinweise erhalten zwei getrennte Panachsen bei fester Rasterzuordnung. Der
darauffolgende Feedback D-18 bis D-22 entfernt die Zusatzkennungen für P1, richtet
alle Zahlen in einem gemeinsamen Slotraster aus, gibt jeder konkreten Linie eine
eigene eingerastete Leseposition, setzt 1080p als primäre Startbasis und verlangt
auch für F-02 eine verfeinerte motivtreue Illustration. Der konkrete P1-Vertrag steht
in [PROTOTYPE_P1.md](PROTOTYPE_P1.md), nun Revision 0.13 mit G1 und H1. Die Nacharbeit in #11
ergänzt D-23 bis D-27: flüssigen Hinweisdrag mit Einrasten beim Loslassen,
geringfügig größere getrennte Füllungen, dezente Cursorbänder, geclippte X
und den geometrischen Live-Strichzähler. Nachweise stehen im P1.3-Prüfbericht;
erneute Eigentümerabnahme bleibt offen. Das ist weder eine endgültige
Themenentscheidung noch ein vollständiges Designsystem.

## 2. Bestätigte gestalterische Grundlage

| Bereich | Bestätigte Entscheidung |
| --- | --- |
| Sammlung | Ein Album füllt sich mit erarbeiteten Bildern und kann einen erkennbar vollständigen Zustand erreichen. Keine zusätzlich beschlossene Raumansicht. |
| Zeichenstil | Handgezeichnete 2D-Illustration mit klaren Konturen und ruhigen, nicht zu blassen Farbflächen. Nicht automatisch Retro-Pixel-Art für die gesamte Oberfläche. |
| Stimmung | Warm, neugierig und dennoch ruhig. |
| Spielbildschirm | Thematik bleibt dezent sichtbar, das Raster sachlich und präzise. Größere Fenster dürfen nicht zu unnötig riesigen Zellen führen. |
| Zelllesbarkeit | Füllungen bleiben einzeln erkennbar, insbesondere an kräftigen Fünferlinien. Raster und Füllung dürfen nicht optisch zu einer gemeinsamen Fläche verschmelzen. |
| Hinweise | Am Raster stehen nur Lösungshinweise, ohne laufende Randnummern. Vollständige einzeilige farbige Zahlen rasten in gemeinsame feste Plätze; jede konkrete Zeile/Spalte hat ihre eigene Leseposition. Seitengerechte Marker und vollständige Hover-Auflösung bleiben Ergänzungen im Arbeitsbild. Keine A–D-Suffixe in P1. |
| Sammelbilder | Das Rätselmotiv ist eine klar erkennbare Stilisierung des detaillierteren Ergebnisbilds. F-01 und F-02 zeigen dieselbe ruhige Kontur-/Farbflächensprache; keine Pflicht zu pixelidentischer Silhouette oder bloßer Kolorierung. |
| Perfektion | Ein perfekter Durchgang ist ohne Fehler und ohne Undo. Details und offene Wertungsfragen stehen in der Produktdefinition, Abschnitt 6.2. |
| Hypothesen | Nicht abschließend entschieden, auch nicht ihre Vereinbarkeit mit Perfektion. |
| Audio | Später behandeln. Kleine unauffällige Effekte und ein besonders guter Erfolgsjingle gewünscht; zurückhaltende Hintergrundmusik denkbar. |

Der Nutzer arbeitet überwiegend mit sicheren Schlüssen, nicht mit versuchsweisem Setzen und Zurückspringen. Hypothesen sind eine mögliche Zusatzfunktion, keine notwendige Spielweise. Rätsel müssen ohne notwendiges Raten lösbar sein.

## 3. Zwei offene Themenalternativen

### A: Thematisches Sammelalbum

Sammlungen können Themen wie Erfindungen, Tiere, Personenporträts oder stilisierte Filmposter behandeln. Das Album verbindet unterschiedliche Motivgruppen durch gemeinsame Präsentation und Zeichenweise. Dies sind mögliche Inhalte, kein bestätigter Rätselkatalog und keine Assetfreigabe.

Der Nutzer hält eine sinnvolle Progression in A zunächst für leichter vorstellbar, hat A aber nicht ausgewählt. Bilderkabinett, Atelier oder Archiv sind Ausgestaltungsideen; daraus folgt keine zusätzliche begehbare Ausstellung oder Dekorationsmechanik.

### B: Reisetagebuch beziehungsweise Weltreisealbum

Regionale Kapitel können Tiere, Gerichte, Sehenswürdigkeiten, Pflanzen und weitere Motive der Region verbinden. Dies ist eine reale regionale Themenidee, keine Festlegung auf eine fantastische Welt.

Ein möglicher Ansatz sind mehrere früh zugängliche Reisekapitel statt einer starren geografischen Route. Eine begrenzte Auswahl vervollständigbarer Kapitel ist denkbar; weder vollständige Länderabdeckung noch konkrete Regionen oder Mengen sind beschlossen. Früh verfügbare große und anspruchsvolle Rätsel bleiben auch hier gefordert.

### Gemeinsamer Vergleich

A und B bleiben bis zu einer ausdrücklichen Entscheidung parallel untersuchbar. Keine erzwungene Mischform. Album und sachlicher Arbeitsbereich können beiden dienen; Atmosphäre und Kapitelorganisation unterscheiden sich.

Als Vergleich wurde dasselbe angearbeitete 40×40-Farbrätsel mit vier Farben vorgeschlagen: identische Hinweise, eigener Stand, Miniatur, Werkzeuge und Informationsumfang, ergänzt um Albumansicht und Abschluss. Das ist ein Entwurfsmaßstab, kein bereits gelieferter mathematisch identischer oder spielbarer Vergleich.

## 4. Visuelle Ausarbeitung

### BP-1R: vergrößerte linke Buchseite

[#27 unter #21](https://github.com/venomenon328/picross/issues/27) konkretisiert
nach dem ersten nicht akzeptierten BP-2-A-Versuch die Arbeitskomposition: naher,
annähernd senkrechter Blick auf eine breite linke Seite eines detailliert
illustrierten Museums-/Inventarbands. Papierlagen, Einband, kleine sorgfältige
Randdetails und warmes Licht geben Identität; Tisch und Requisiten treten zurück.
Raster und beide Hinweisflächen liegen vollständig auf dieser einzelnen flachen
Seite. Falz rechts außerhalb, allenfalls ein schmaler rechter Seitenanschnitt.
Keine kleine halbe Bildschirmfläche, keine verzerrte Buchabbildung.

Diese Entscheidung ersetzt ausdrücklich den alten Einlegebogen über dem Mittelfalz
und die alten Masterkoordinaten/-masken. Die historische
[BP-1-Lieferung aus PR #29](https://github.com/venomenon328/picross/tree/0d3ad6a921578f94b3249ab83fbb215721549dfb/docs/design/book_inventory/production)
bleibt eine gültige Lieferung ihres damaligen Auftrags. Die
[BP-1R-Produktionsvorlage](design/book_inventory/production/README.md) schreibt
Geometrie, fünf Größenproben, Ebenen/Masken, Navigationsanschluss und Briefing fort.
Technische Vektoren bestimmen keine fertige Kunst; der ungeeignete A-Versuch wird
weder nachgezeichnet noch bloß beschnitten. Keine neue breite Stil-/Schriftrunde.

Kompakter Album-/Sammlungszugang links und Wechsel zur rechten Informationsansicht
sind getrennte echte UI-Gruppen mit eindeutigen Zielen und Rückweg. Kategorien aus
dem generierten Bild sind kein beschlossener Katalog. Zwei feste Ansichten, kein
Kamerapan und keine Kopplung an Raster-/Miniaturnavigation. Rückkehr erhält Zellen,
Undo/Redo, Farbe/Werkzeug, Rasterausschnitt/Zoom und Hinweislesepositionen;
Gestenabbruch, Pflicht-Flush und Recoverygrenzen bleiben verbindlich. Miniatur,
Koordinaten, Farbe, Werkzeuge, Undo/Redo und Zoom bleiben auf der Arbeitsansicht.
Rechts werden bestehende Einstellungen/Hilfe und ein späterer/offener Statistik-
bereich nur schematisch geplant, ohne Daten oder versteckte Live-Fehlerhilfe.

Hintergrund enthält Papier, Einband, Seitenkanten und wenig Umgebung. Registerkörper,
Labels, Icons, Zustände, Raster/Zahlen und Informationen werden separat gerendert.
Keine eingebrannten Bedienattrappen, beweglichen Werkzeugschatten, atmosphärischen
Fülltexte, Mottos oder Pseudoschrift. Detaillierte warme 2D-Materialillustration bleibt
das Ziel; einfache Vektorbuchflächen sind kein fertiger Ersatz.

BP-1R ist eine statische technische Vorlage, keine Kunst-/Bedienabnahme. Vor erneuter
BP-2-Bildproduktion eine konkret geprüfte Einzelseitenvorlage benennen: zuerst neues
A (dunkles Leder/warmes Holz), dann B als kontrollierte hellere Material-/Lichtvariation.
Finale Layout-, Schrift-, Icon-, Kontrast- und Assetwahl erst an BP-3 vor #23.
Sammelalbum/Reisealbum, Sammlungsinhalte, Progression/Wertung bleiben offen bzw.
unverändert. Kein Beginn von BP-2/BP-3/#23/#24 und keine Änderung an PR #25/#28/#29
durch diese Vorlagenlieferung.

### 4.1 Album und Arbeitsansicht

Ein möglicher Albumaufbau sind redaktionell komponierte Doppelseiten mit Registern, Kapitelverzierungen und unterschiedlich großen Bildplätzen. Große Panoramen könnten eigene Seiten erhalten. Feste Seiten statt freier Dekoration sind ein Vorschlag, keine neue Spielmechanik.

Beim Öffnen könnte das Rätselblatt zur großzügigen Arbeitsfläche werden. Materialanmutung und Kapitelakzente bleiben, Hinweise und Raster erhalten ausreichend Platz. Die linke Buchseite selbst wird zur großzügigen Bildschirmfläche; große Raster werden weder in eine kleine halbe Bildschirmfläche noch über einen Falz gezwungen. Perspektive, Ränder und Übergänge bleiben zu prüfen.

Leicht gebrochenes Papierweiß, dunkle Konturen, matte Akzente und dezente Texturen sind mögliche Stilmittel, keine festgelegte Palette. Zahlen, Linien und Zellzustände müssen klar und unverzerrt bleiben. Handschriftliche Ziffern, Flecken und dekorative Gegenstände dürfen die Arbeit nicht erschweren. Handgezeichnet bedeutet weder verpflichtend beige noch absichtlich unpräzise.

**Präzisierung aus der Mausprobe:** Fensterfläche, Oberflächenskalierung und Rasterzoom getrennt behandeln. 1080p und 1440p sollen sinnvoll nutzbar sein, ohne kleine Rätsel automatisch auf die gesamte Arbeitsfläche zu vergrößern. Mehr Fläche darf mehr Ausschnitt oder ruhige Ränder bedeuten. Konkrete Startwerte und Tests für P1 stehen ausschließlich in der P1-Spezifikation; sie sind keine allgemeingültigen Pixelwerte des späteren Designsystems.

Die gefüllten Zellen brauchen einen erkennbaren Zwischenraum beziehungsweise eine kontrastierende Trennung auch zu dunklen Fünferlinien. Innenabstand, Linienbreite, Farben und Ebenenreihenfolge gemeinsam prüfen. Der in der Mausprobe gezeigte Fall dreier angrenzender Füllzellen an einer Fünfergrenze darf nicht wie eine einzige umgedrehte L-Form aussehen. Fünfergruppen sollen dabei weiterhin gut zählbar bleiben. Prüfung an dunklen und allen angebotenen Farbzellen, Arbeitszoom und Vorschau, nicht nur an einem leeren Raster.

Für Großraster ist ein verdichteter Rahmen mit kompakteren Werkzeugen denkbar. Er soll Identität bewahren, ohne Arbeitsfläche zu verschwenden. Schriftgrößen, Abstände, Kontraste und Fokuszustände sind noch kein endgültiges Designsystem.

### 4.2 Bildplätze und Vollständigkeit

Ungelöste Plätze benötigen neutrale Kennungen statt vorweggenommener Motivnamen oder verräterischer Skizzen. Angefangene Rätsel dürfen ihren eigenen Stand zeigen. Spoilergrenze und Miniaturregel bleiben verbindlich.

Vorgeschlagen ist eine Unterscheidung zwischen vollständiger Sammlung und zusätzlicher Meisterschaft: jedes gelöste Rätsel liefert sein vollständiges Bild unabhängig von der Bewertung, perfekte Leistungen erhalten zusätzliche Kennzeichnungen. Bonusinhalte könnten als Zusatzblätter erscheinen statt dauerhaften Löchern. Konkrete Begriffe und Platzierung sind offen. Bestätigte Perfektions-Bonusrätsel nicht durch rein kosmetische Belohnung ersetzen.

### 4.3 Motivtreue, detailliertere Enthüllung

**Bestätigte Präzisierung:** Das Ergebnisbild darf sichtbar detaillierter als das Rätsel sein. Der Hauptgegenstand, wesentliche Formen, Bildaufbau und Proportionen müssen so zusammenpassen, dass das Raster sehr deutlich als Stilisierung des Bilds erkennbar ist. Feinere Konturen, Schattierungen, Oberflächen und kleinere passende Elemente sind erlaubt. Eine identische belegte Pixelmaske oder identische Auflösung ist ausdrücklich nicht erforderlich. Ein beliebiges neues Bild oder vollständig anderer Blickwinkel wäre weiterhin kein Ersatz.

Die frühere P1.1-Prüfung auf identische Silhouetten war eine enge technische Fixture-Regel, nicht das allgemeine Qualitätsziel. #9 demonstriert die breitere Richtung am positiv bestätigten F-01-Segelboot und am eigenständig verfeinerten F-02-Leuchtturm. Beide verwenden ruhige Farbflächen, klare dunkle Konturen und motivbezogene Details. F-02 erhält passend zu seinem Raster Sonne, rechts stehenden Turm und Wasseraufbau, ergänzt um Architektur-, Oberflächen- und Wellendetails. Bloßes Vergrößern der gleichen Pixel oder Neufärben genügt nicht. Die Rätsel selbst werden nicht zur Illustration passend verändert.

Ein möglicher Ablauf bleibt: Hinweise, Leermarkierungen und Raster treten zurück; das gelöste Motiv bleibt sichtbar; daraus entsteht die detailliertere Fassung; anschließend Name und gegebenenfalls spätere Bewertung/Albumeintrag. Auch bei Farbrätseln genügt die bloße Freistellung oder erneute Präsentation desselben gelösten Rasters nicht als bestätigtes Qualitätsziel; ihre Abschlussmotive folgen der konsistenten motivtreuen Verfeinerungsrichtung. Das schreibt weder identische Auflösungen noch eine allgemeine Assetpipeline oder eine hochaufgelöste Neuzeichnung jedes Motivs vor. Keine feste Animationsfolge. P1 hat weiterhin keine Wertung.

Eine umschaltbare ursprüngliche Rasteransicht und überspringbare/reduzierte Animationen bleiben sinnvolle Vorschläge, keine automatisch beauftragten Funktionen. Motiverkennung benötigt visuellen Vergleich; ein technischer Bildvalidator ersetzt diesen nicht. Die detailreiche Fassung erscheint erst nach tatsächlichem Abschluss, nie als Lösungsvorschau oder korrigierte Miniatur. Eine bloße Freistellung desselben Farbrasters genügt für F-02 ausdrücklich nicht mehr.

## 5. Bedienung und Wertung

### 5.1 Präzise Eingaben und Orientierung

Die bestätigte Achsenbindung eines Mausstrichs ab der ersten eindeutigen Bewegung in eine weitere Zelle bleibt verbindlich. Für P1 wird sie erst bei tatsächlicher Rückkehr zur Startzelle innerhalb derselben Geste wieder freigegeben; danach kann eine neue Richtung gewählt werden. Eine bloße Projektion oder ein Eingabesprung über den Start löst dies nicht aus. Produktweit bleiben alternative Eingaben vorgesehen. Für P1 gilt jedoch D-06: Maus, kein Tastatur-/Controller-Gate.

**Präzisierung aus den Mausproben:** Das normale Werkzeug neutralisiert vorhandene
Füllungen mit links und Leermarkierungen mit rechts. Zusätzlich wandelt ein linker
Setzmodus X direkt in die aktive Farbe und ein rechter Setzmodus Füllungen direkt in
X um. Die frühere allgemeine Gegenmarkierungs-Schutzregel ist damit abgelöst;
Rücknahmestriche bleiben auf den am Start vorhandenen Zieltyp beschränkt. Der konkrete,
am Strichstart festgelegte Modus einschließlich Farbverhalten, elastischer Vorschau
und Undo-Grenze steht in P1 §5.1. Kein wiederholtes Umschalten derselben Zelle beim
Zurückziehen.

Für P1 zeigt ein Live-Zähler während linker und rechter Zellgesten die gesamte
geometrische aktuelle Strichlänge inklusive Start/Ende, auch bei Vorbelegungen und
Eingabesprüngen; er folgt dem elastischen Zurückziehen und zeigt bei tatsächlicher Rückkehr zum Ursprung 1 sowie danach die Länge des neuen geraden Abschnitts. Ein Linealmodus und
weitergehende Eingabealternativen bleiben Vorschläge.
Für große Raster sind vollständig zugeordnete, unnummerierte Hinweise direkt im
Arbeitskontext, aktive Linien und eine Miniatur mit Ausschnittrahmen wichtig. Lange
Folgen werden nur an Grenzen vollständiger Einzelhinweise gekürzt; ein möglichst
großer zusammenhängender Ausschnitt bleibt direkt lesbar. Für den P1-Randfall
priorisiert Variante A nach #11/R7 den geometrisch nächsten Snap und monotone
direkte Bewegung: Am äußeren Draganschlag darf dafür ein Tokenplatz frei bleiben.
Alle Zahlen bleiben über die Lesepositionen erreichbar; eine nur per Gegenbewegung
erreichbare zusätzliche Randposition entfällt. Alle Folgen einer
Orientierung verwenden gemeinsame feste Slots, und kurze Folgen stehen ebenfalls
rasterseitig. Seitengerechte Marker zeigen verborgene Präfixe/Suffixe. Jede konkrete
Spalte lässt sich nur für sich vertikal, jede konkrete Zeile nur für sich horizontal
kontinuierlich ziehen und beim Loslassen in ganzen gemeinsamen Slots einrasten
lassen, ohne X-/Y-Zuordnung oder Nachbarfolgen zu ändern. Der temporäre Versatz
ist weder gespeicherte Leseposition noch Spielzustand.
Der vollständige Hover-Tooltip ergänzt diese Navigation statt sie zu ersetzen; eine
separate Hinweisansicht bleibt ausgeschlossen. Hinweise beziehen sich auf ganze Linien,
nicht nur den Rasterausschnitt. Die Miniatur zeigt eigene Eingaben einschließlich
Fehlern, niemals eine korrigierte Lösung. P1 konkretisiert Zoom/Pan und
Miniaturnavigation; Lesezeichen gehören nicht automatisch dazu.

Rätselfarben und UI-Zustandsfarben sollen unterscheidbar sein. Die Hinweiszahl selbst
trägt die Rätselfarbe; für P1 entfallen ergänzende A–D-Kennungen und ihr Schalter
vorerst vollständig. Das ist keine endgültige Streichung farbunabhängiger Erkennbarkeit
im Produkt und kein vorgezogener Neuentwurf der Mauspalette. Unabhängige UI-/
Rasterskalierung unterstützt die Lesbarkeit. H1 aus [#19](https://github.com/venomenon328/picross/issues/19)
ergänzt dezentes Durchstreichen eindeutig erfüllter Hinweiszahlen, bei unveränderter
Rätselfarbe, Zahlengröße und Slotposition. Es hängt am Originalindex und gilt ebenso
im vollständigen Tooltip und während des Hinweisdrags. `…` und Leerlinien-`–`
werden nicht durchgestrichen. Nur die sichtbaren Zellen einschließlich elastischer
Vorschau und die eigenen Hinweise der vollständigen Linie bestimmen den Status;
kein verdeckter Lösungsvergleich. Widerspruch oder weggefallene Eindeutigkeit nimmt
die Markierung zurück. „Erfüllte Hinweise markieren“ startet aktiv, gilt sitzungsweit
auch nach Blatt-/Albumwechsel und Reset und wird nicht gespeichert. Nach App-Neustart
ist es wieder aktiv; kein vorgezogenes dauerhaftes Produkt-Einstellungsformat.
Einzelheiten des gespeicherten Zustands werden im zuständigen Speicherpaket konkretisiert.

### 5.2 Undo und Hypothesen

Beschlossen ist der Ausschluss von Perfektion durch Undo, nicht die Abschaffung von Undo. Fehlerzahl und Rücknahmen getrennt zu erfassen bleibt ein Vorschlag; feste Abzüge und niedrigere Wertungsstufen sind offen.

Auch nach dem Wunsch zum direkten Neutralisieren ist nicht entschieden, ob manuelles Löschen, Zurücksetzen oder Überschreiben wertungsrelevante Rücknahmen sind. P1 implementiert hier Komfort, keine Wertungsregel. Undo ohne Wirkung, Vorschauabbruch, Neustart und Notizkorrekturen bleiben abzugrenzen.

Eine einmalige abschaltbare Bestätigung vor dem ersten wertungsrelevanten Undo ist ein Entwurfsvorschlag. Sie müsste unabhängig von unbemerkten Fehlern erscheinen; sonst verriete sie verdeckt den Lösungszustand. Keine Anzeige „bisher fehlerfrei“ während des Standardmodus.

Eine separate Ebene für „unsicher gesetzt/leer“, bei Farbrätseln mit vermuteter Farbe, bleibt ein Untersuchungsansatz. Mehr als schwächere Deckkraft zur Unterscheidung ist zu prüfen. Übernehmen/Verwerfen ohne Richtig-/Falsch-Prüfung ist vorgeschlagen; Notizen würden nicht als Lösung gelten. Aufnahme, Grenzen und Perfektionswirkung sind offen.

### 5.3 Verbundraster

Arbeitshypothese: zwei Raster mit wirklich gemeinsamen Zellen, aktives Raster mit zugehörigen Hinweisen, gemeinsamer Bereich klar umrandet, anderes Raster zurückgenommen. Keine irreführende Rätselfarbe als Kennzeichnung und keine unlesbaren überlagerten Hinweisflächen.

Geometrie und Darstellung sind nicht beschlossen. Ein gesonderter Prototyp muss echte logische Abhängigkeiten und verständliche Hinweiszuordnung zeigen; unabhängige Einzelrätsel ergeben keinen solchen Nachweis. Keine P1-Erweiterung durch dieses Feedback.

## 6. Referenzen und Aussagegrenzen

Referenz M-01 aus dem Gestaltungsgespräch vom 22.09.2026 ist der generierte Vergleich „Thematisches Sammelalbum – Beispiel: Erfindungen“ / „Reisetagebuch – Beispiel: Japan“. Er enthält Album-, Rätsel- und Abschlussdarstellungen sowie Details zu Werkzeugen und Undo. Die Richtung wurde positiv bewertet. Die Bilddatei ist nicht Teil dieses Dokumentpakets; die textliche Einordnung vermeidet eine Pflichtabhängigkeit von Chatbildern.

Der Mock ist keine Bildschirm-für-Bildschirm-Spezifikation, kein gültiger Rätseldatensatz und kein finales Assetpaket. A/B wurden dadurch nicht entschieden. Insbesondere keine vorzeitigen Motivvorschauen, Skizzen, fremden Assets, erfundenen Sternschwellen oder schematischen Rätselzahlen übernehmen. Detaillierte Illustrationen müssen trotz erlaubter Verfeinerung die Wiedererkennbarkeit erhalten.

Die spätere reale P1.1-Probe lieferte einen Abschluss-Screenshot und einen Rasterausschnitt mit dem beschriebenen Fünferlinienproblem. Das belegt vorhandenes Nutzerfeedback, nicht jede K-06-Einzelprüfung, tatsächliche Windows-Skalierung oder die Güte der damals noch nicht implementierten Großraster-/Zoom-/Speicherfunktionen. Aktueller Abnahmestand in #5/#8 und PR #14.

## 7. Weitere Erprobung und offene Entscheidungen

| Thema | Nächster Gegenstand |
| --- | --- |
| Themenwahl | A oder B, Kapitel und Motivzusammenhang; bestehende Progressionsanforderungen nicht neu öffnen. |
| Album/Designsystem | Layout, Typografie, Größenbandbreiten, Kontraste und Fokus anhand realer Proben ausarbeiten. |
| Rücknahmen/Wertung | Direkte Neutralisierung ist für die Bedienung festgelegt; Fehlerzählung, Sterne und Hypothesenwirkung bleiben offen. |
| P1-Bedienung | Vier Feedbackpunkte plus Farb-/Großraster, Zoom, lange Hinweise und eigene Miniatur in #9. |
| Fortsetzung | Speicherung/Recovery in #11, integrierte Erprobung in #12. |

Gestaltung und Risikoprototypen überlappen weiter. Statische Mocks allein beantworten keine Bedienungsfrage. Die bestätigte gemeinsame Richtung reicht zur Untersuchung; sie ist noch kein fertiges UI-Konzept.

Rätselproduktion und Deduktionsnachweis bleiben ein eigener früher Risikostrang. Hübsche Bilder allein sind keine qualitätsgeprüften Rätsel. Verbundraster getrennt evaluieren. Thema, Designsystem und zentrale Ansichten anhand der Erfahrungen schärfen, bevor umfangreiche Inhalte produziert werden.
