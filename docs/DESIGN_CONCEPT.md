# Gestaltungskonzept: Album, Rätselarbeit und Enthüllung

Stand: 09.10.2026 · Arbeitsfassung 0.23 · Z2/GP-48/ZV-50 integriert; zeichnerische UI spezifiziert

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
in [PROTOTYPE_P1.md](PROTOTYPE_P1.md), nun Revision 0.16 mit G1, H1, Z2 und F-04. Die Nacharbeit in #11
ergänzt D-23 bis D-27: flüssigen Hinweisdrag mit Einrasten beim Loslassen,
geringfügig größere getrennte Füllungen, dezente Cursorbänder, geclippte X
und den geometrischen Live-Strichzähler. Nachweise stehen im P1.3-Prüfbericht;
die spätere P1-Gesamtabnahme erfolgte in #12. Z2 ist integriert; seine nicht
durchgeführte Eigentümerprobe wurde für PR #33 ausdrücklich als Gate aufgehoben.
Das ist weder eine endgültige Themenentscheidung noch ein vollständiges
Designsystem.

Die Spezifikationsfreigabe vom 07.10.2026 ergänzt die
[zeichnerische UI](UI_DRAWING_STYLE.md): kräftigere kompakte Hinweisziffern,
eigene Füll-/X-Striche und kurze Zellanimationen. E1 wählt Stiftfüllung und
historisch 140/80-ms-Timing; zusätzliche Rand-UI entfällt, Hintergrundarbeit bleibt separat.
Die ausdrücklich korrigierte Bewegungsregel gilt: statische hellere Vorschau
während des Ziehens, Animation erst beim tatsächlichen Anwenden. Diese
Folgearbeit liegt als [isolierte ZS-1-Studie](ZS1_VERIFICATION.md) vor.
Chalkboard/Stift/X/Timing sind nach ZS1-M01 bestätigt; die
[reguläre ZS-2-Integration](ZS2_VERIFICATION.md) übernimmt diese Kombination.

## 2. Bestätigte gestalterische Grundlage

| Bereich | Bestätigte Entscheidung |
| --- | --- |
| Sammlung | Ein Album füllt sich mit erarbeiteten Bildern und kann einen erkennbar vollständigen Zustand erreichen. Keine zusätzlich beschlossene Raumansicht. |
| Zeichenstil | Handgezeichnete 2D-Illustration mit klaren Konturen und ruhigen, nicht zu blassen Farbflächen. Nicht automatisch Retro-Pixel-Art für die gesamte Oberfläche. |
| Stimmung | Warm, neugierig und dennoch ruhig. |
| Spielbildschirm | Thematik bleibt dezent sichtbar; das geometrisch präzise Raster trägt selbst den gezeichneten Spielcharakter. Größere Fenster dürfen nicht zu unnötig riesigen Zellen führen. |
| Zelllesbarkeit | Füllungen bleiben einzeln erkennbar, insbesondere an kräftigen Fünferlinien. Raster und Füllung dürfen nicht optisch zu einer gemeinsamen Fläche verschmelzen. |
| Zellstil | Kräftige Farbflächen mit dezenter stabiler Strichtextur; gezeichnete X bleiben gegenüber dem Motiv zurückhaltend. Textur bei kleinen Zellen vereinfachen, Miniatur bewusst ruhig halten. |
| Hinweise | Am Raster stehen nur Lösungshinweise, ohne laufende Randnummern. Vollständige einzeilige farbige Zahlen rasten in gemeinsame feste Plätze; jede konkrete Zeile/Spalte hat ihre eigene Leseposition. Seitengerechte Marker und vollständige Hover-Auflösung bleiben Ergänzungen im Arbeitsbild. Keine A–D-Suffixe in P1. |
| Hinweisgestalt | Kompaktere, optisch kräftigere Ziffern mit klaren Innenräumen; alle drei Hinweiszustände, Farben, Konturen und die gemeinsame Slotzuordnung bleiben lesbar. Konkrete Auswahl durch die native Gestaltungsprobe. |
| Zellbewegung | Statische hellere/transparente Vorschau während des Ziehens; erst angewendete Änderungen zeichnen kurz vom Gestenstart zum finalen Abschnittsende (maximal 390 ms). Abschaltbar, ohne zusätzliche Eingabesperre oder Verzögerung des Spielzustands. |
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

A und B bleiben bis zu einer ausdrücklichen Entscheidung parallel untersuchbar. Keine erzwungene Mischform. Album und präziser gezeichneter Arbeitsbereich können beiden dienen; Atmosphäre und Kapitelorganisation unterscheiden sich.

Als Vergleich wurde dasselbe angearbeitete 40×40-Farbrätsel mit vier Farben vorgeschlagen: identische Hinweise, eigener Stand, Miniatur, Werkzeuge und Informationsumfang, ergänzt um Albumansicht und Abschluss. Das ist ein Entwurfsmaßstab, kein bereits gelieferter mathematisch identischer oder spielbarer Vergleich.

## 4. Visuelle Ausarbeitung

Für #23 gilt die [aktive Auswahl GD-01 bis GD-05](Z2_SELECTION.md): A-Inventarband,
gemeinsame BP-3-Montierungen, Fraunces/Plex Sans, feste C1-Kontur und eine echte
native N1-Informationsseite. Diese konkrete Arbeitsansicht ersetzt die historische
BP-3-Empfehlung B, nicht die noch offene gesamte Themen-/Kapitelentscheidung.
Raster und UI werden getrennt auf unverzerrtem A-Papier gezeichnet. N1 nutzt
nur eine Hintergrundspiegelung; Text und Bedienung bleiben nativ. Einstellungen,
Hinweisreset, H1, Bedienhilfe und Beenden teilen sich eine Seite mit Rückweg.
Keine neue Statistik/Albumarchitektur oder Vorwegnahme von #24. Native Abweichungen,
Offline-Fonts und die historische Eigentümeranleitung stehen im [Z2-Prüfbericht](Z2_VERIFICATION.md).
Die native Umsetzung ist über [PR #33](https://github.com/venomenon328/picross/pull/33)
integriert. Reviewbefunde und Mergefreigabe sind dort und im
[Paketstatus #23](https://github.com/venomenon328/picross/issues/23) abgeschlossen.
Z2-M01/M02/M03 wurden nicht durchgeführt; der Eigentümer hob das damalige Gate
für diesen Merge auf. RP-3 ist nach eigenem technischem/visuellem Review R2
über PR #44 integriert; die reale Eigentümer-Lösung bleibt RP-6-Gate.
Die [RP-4-Sichtprüfung](RP4_VERIFICATION.md) bewertet neue Produktionsraster,
keine neue P1-Bedienabnahme.

Die neue ZS-Folgearbeit aus Abschnitt 4.4 öffnet GD-03 ausschließlich für die
Gestaltung der Hinweisziffern. Fraunces für Titel, Plex Sans für übrige UI,
A-Arbeitsasset, Buchkomposition, N1 und die C1-Farb-/Kontursemantik bleiben die
Grundlage. Konkrete abweichende Ziffern-, Schriftgrad- oder Slotwerte werden
erst im nativen Vergleich begründet gewählt; eine Änderung dieser Werte ist
kein Selbstzweck. Die historischen GD-Auswahl- und Abnahmenachweise bleiben
an ihren jeweiligen Stand gebunden.

### BP-1R bis BP-3: Entwurfsverlauf und integrierte Grundlagen

Der folgende Verlauf ordnet die bereits integrierten Vorlagen und Studien ein.
Frühere Start- und Auswahlgrenzen sind keine erneut offenen Z2-Entscheidungen;
maßgeblich sind GD-01 bis GD-05 und der aktuelle #23-Vertrag. Die historischen
hashgebundenen Bilder, ZIPs, Manifeste und Prüfberichte bleiben unverändert.

[#27 unter #21](https://github.com/venomenon328/picross/issues/27) konkretisierte
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
Rechts wurden in BP-1R bestehende Einstellungen/Hilfe und mögliche spätere Statistiken
nur schematisch geplant. GD-05 begrenzt den jetzigen N1-Umfang ausdrücklich auf
vorhandene Einstellungen und Hilfe; kein Statistikbereich oder Live-Fehlerhinweis.

Hintergrund enthält Papier, Einband, Seitenkanten und wenig Umgebung. Registerkörper,
Labels, Icons, Zustände, Raster/Zahlen und Informationen werden separat gerendert.
Keine eingebrannten Bedienattrappen, beweglichen Werkzeugschatten, atmosphärischen
Fülltexte, Mottos oder Pseudoschrift. Detaillierte warme 2D-Materialillustration bleibt
das Ziel; einfache Vektorbuchflächen sind kein fertiger Ersatz.

BP-1R war die statische technische Grundlage, keine Kunst-/Bedienabnahme. Darauf
folgten die erneute BP-2-Bildproduktion mit A (dunkles Leder/warmes Holz) und B als
kontrollierter hellerer Material-/Lichtvariation sowie die vollständigen BP-3-Ansichten.
Die Auswahl vor #23 ist inzwischen mit GD-01 bis GD-05 erfolgt. Sammelalbum/Reisealbum,
Sammlungsinhalte, Progression/Wertung bleiben davon getrennt offen bzw. unverändert.

BP-1R ist über PR #30 integriert. Die separate
[BP-2-Artworklieferung](design/book_inventory/artwork/README.md) enthält zwei
tatsächlich erzeugte UI-freie Materialvarianten und unveränderte BP-1R-Prüfmontagen.
Native Auflösung, A-Korrekturen, A→B-Ableitung und Prüfumfang sind dort dokumentiert.
BP-2 wurde über PR #31 zunächst ohne endgültige Kunstwahl integriert.
Das [BP-3-Kompositionspaket](design/book_inventory/composition/README.md) ist über
PR #32 integriert: gemeinsame UI auf beiden unveränderten Bildern, gefasste
Inventarkarte, Originalfarbmuster, gruppierte Werkzeuge und getrennte Blattzugänge.
Zehn Größen-/Artworkkompositionen und statische Zustandsnachweise bildeten die
Entscheidungsgrundlage. Technisches/visuelles Review und Mergefreigabe dieses
Studienstands sind abgeschlossen. Der Eigentümer wählte anschließend A, die gemeinsame
UI, Fraunces/IBM Plex Sans und C1; die frühere Bearbeiterempfehlung B ist historisch.
#27 ist damit geschlossen. #23 ist über PR #33 integriert; die dort nicht
durchgeführte Eigentümerprobe wurde ausdrücklich als damaliges Mergegate
aufgehoben. #24 wurde noch nicht begonnen.

### 4.1 Album und Arbeitsansicht

Ein möglicher Albumaufbau sind redaktionell komponierte Doppelseiten mit Registern, Kapitelverzierungen und unterschiedlich großen Bildplätzen. Große Panoramen könnten eigene Seiten erhalten. Feste Seiten statt freier Dekoration sind ein Vorschlag, keine neue Spielmechanik.

Beim Öffnen könnte das Rätselblatt zur großzügigen Arbeitsfläche werden. Materialanmutung und Kapitelakzente bleiben, Hinweise und Raster erhalten ausreichend Platz. Die linke Buchseite selbst wird zur großzügigen Bildschirmfläche; große Raster werden weder in eine kleine halbe Bildschirmfläche noch über einen Falz gezwungen. Perspektive, Ränder und Übergänge bleiben zu prüfen.

Leicht gebrochenes Papierweiß, dunkle Konturen, matte Akzente und dezente Texturen sind mögliche Stilmittel, keine festgelegte Palette. Zahlen, Linien und Zellzustände müssen klar und unverzerrt bleiben. Handschriftliche Ziffern, Flecken und dekorative Gegenstände dürfen die Arbeit nicht erschweren. Handgezeichnet bedeutet weder verpflichtend beige noch absichtlich unpräzise.

**Präzisierung aus der Mausprobe:** Fensterfläche, Oberflächenskalierung und Rasterzoom getrennt behandeln. 1080p und 1440p sollen sinnvoll nutzbar sein, ohne kleine Rätsel automatisch auf die gesamte Arbeitsfläche zu vergrößern. Mehr Fläche darf mehr Ausschnitt oder ruhige Ränder bedeuten. Konkrete Startwerte und Tests für P1 stehen ausschließlich in der P1-Spezifikation; sie sind keine allgemeingültigen Pixelwerte des späteren Designsystems.

**ZV-50 / #50:** Die ruhige Standarddarstellung eines kleinen Rasters bleibt erhalten, darf aber den späteren Arbeitszoom nicht als unsichtbare feste Clippingbox begrenzen. Oberhalb 100 % nutzt das Raster im nicht kompakten Buchlayout die freie Papierfläche bis zu echten Hinweis-/Titel-, Miniatur- und Werkzeuggrenzen. Für 20×20 sind bei 1920×1080/UI 100 % alle Arbeitsstufen bis einschließlich 150 % vollständig sichtbar; erst danach ist ein Ausschnitt legitim. Kleinere Flächen/UI 125 % werden nach ihrem realen Platz beurteilt. Die größere sichtbare Fläche darf weder Zellen, Hinweise noch Trefferflächen verkleinern oder unter Bedienung zeichnen.

Die gefüllten Zellen brauchen einen erkennbaren Zwischenraum beziehungsweise eine kontrastierende Trennung auch zu dunklen Fünferlinien. Innenabstand, Linienbreite, Farben und Ebenenreihenfolge gemeinsam prüfen. Der in der Mausprobe gezeigte Fall dreier angrenzender Füllzellen an einer Fünfergrenze darf nicht wie eine einzige umgedrehte L-Form aussehen. Fünfergruppen sollen dabei weiterhin gut zählbar bleiben. Prüfung an dunklen und allen angebotenen Farbzellen, Arbeitszoom und Vorschau, nicht nur an einem leeren Raster.

Für reguläre Rätsel gilt [VS-D01](VS1_DECISION.md): Vollsicht einschließlich Rahmen, bevorzugt G, ergänzend V, Format-/Hinweislastprüfung bei 1080p. VS-GF1 nutzt freie rechte Papierbreite für Zeilenhinweise und versetzt Raster samt Spaltenhinweisen und Treffergeometrie gemeinsam, ohne Zell-/Schriftverkleinerung. Die reguläre P1-Integration bleibt separat. Für mögliche Großraster-Sonderfälle ist ein verdichteter Rahmen mit kompakteren Werkzeugen denkbar. Er soll Identität bewahren, ohne Arbeitsfläche zu verschwenden. Schriftgrößen, Abstände, Kontraste und Fokuszustände sind noch kein endgültiges Designsystem.

### 4.2 Bildplätze und Vollständigkeit

Ungelöste Plätze benötigen neutrale Kennungen statt vorweggenommener Motivnamen oder verräterischer Skizzen. Angefangene Rätsel dürfen ihren eigenen Stand zeigen. Spoilergrenze und Miniaturregel bleiben verbindlich.

Vorgeschlagen ist eine Unterscheidung zwischen vollständiger Sammlung und zusätzlicher Meisterschaft: jedes gelöste Rätsel liefert sein vollständiges Bild unabhängig von der Bewertung, perfekte Leistungen erhalten zusätzliche Kennzeichnungen. Bonusinhalte könnten als Zusatzblätter erscheinen statt dauerhaften Löchern. Konkrete Begriffe und Platzierung sind offen. Bestätigte Perfektions-Bonusrätsel nicht durch rein kosmetische Belohnung ersetzen.

### 4.3 Motivtreue, detailliertere Enthüllung

**Bestätigte Präzisierung:** Das Ergebnisbild darf sichtbar detaillierter als das Rätsel sein. Der Hauptgegenstand, wesentliche Formen, Bildaufbau und Proportionen müssen so zusammenpassen, dass das Raster sehr deutlich als Stilisierung des Bilds erkennbar ist. Feinere Konturen, Schattierungen, Oberflächen und kleinere passende Elemente sind erlaubt. Eine identische belegte Pixelmaske oder identische Auflösung ist ausdrücklich nicht erforderlich. Ein beliebiges neues Bild oder vollständig anderer Blickwinkel wäre weiterhin kein Ersatz.

Die frühere P1.1-Prüfung auf identische Silhouetten war eine enge technische Fixture-Regel, nicht das allgemeine Qualitätsziel. #9 demonstriert die breitere Richtung am positiv bestätigten F-01-Segelboot und am eigenständig verfeinerten F-02-Leuchtturm. Beide verwenden ruhige Farbflächen, klare dunkle Konturen und motivbezogene Details. F-02 erhält passend zu seinem Raster Sonne, rechts stehenden Turm und Wasseraufbau, ergänzt um Architektur-, Oberflächen- und Wellendetails. Bloßes Vergrößern der gleichen Pixel oder Neufärben genügt nicht. Die Rätsel selbst werden nicht zur Illustration passend verändert.

Ein möglicher Ablauf bleibt: Hinweise, Leermarkierungen und Raster treten zurück; das gelöste Motiv bleibt sichtbar; daraus entsteht die detailliertere Fassung; anschließend Name und gegebenenfalls spätere Bewertung/Albumeintrag. Auch bei Farbrätseln genügt die bloße Freistellung oder erneute Präsentation desselben gelösten Rasters nicht als bestätigtes Qualitätsziel; ihre Abschlussmotive folgen der konsistenten motivtreuen Verfeinerungsrichtung. Das schreibt weder identische Auflösungen noch eine allgemeine Assetpipeline oder eine hochaufgelöste Neuzeichnung jedes Motivs vor. Keine feste Animationsfolge. P1 hat weiterhin keine Wertung.

Eine umschaltbare ursprüngliche Rasteransicht und überspringbare/reduzierte Abschlussanimationen bleiben sinnvolle Vorschläge, keine automatisch beauftragten Funktionen. Davon getrennt ist das Abschalten der Zellanimationen inzwischen durch ZS bestätigt. Motiverkennung benötigt visuellen Vergleich; ein technischer Bildvalidator ersetzt diesen nicht. Die detailreiche Fassung erscheint erst nach tatsächlichem Abschluss, nie als Lösungsvorschau oder korrigierte Miniatur. Eine bloße Freistellung desselben Farbrasters genügt für F-02 ausdrücklich nicht mehr.

### 4.4 Zeichnerische Hinweiszahlen und Zellmarkierungen nach E1

Die am 07.10.2026 freigegebene Richtung führt die Buchgestaltung innerhalb der
Arbeitsfläche fort. Hinweisziffern und Zellmarkierungen haben Vorrang; die
bestehenden funktionalen Werkzeuge und Miniaturfassung bleiben erhalten. Die
[detaillierte Spezifikation](UI_DRAWING_STYLE.md) führt den Vertrag und die
Pakete [ZS-1 / #52](https://github.com/venomenon328/picross/issues/52)
(native Gestaltungsprobe) und [ZS-2 / #53](https://github.com/venomenon328/picross/issues/53)
(Integration) unter #21.

Hinweisziffern sollen ihren Platz optisch besser ausfüllen und durch klare
Strichstärken kompakter wirken. Ziffernform, Gewicht, Größe und Ausrichtung
werden zuerst beurteilt; geänderte Slotabstände benötigen eine begründete
Wahl im Vergleich und erhalten das gemeinsame regelmäßige Hinweisraster.
Ein- und mehrstellige Zahlen einschließlich `1`, `11`, `17`, `40` und `100`
müssen in normalem, abgeschwächtem und durchgestrichenem Zustand lesbar
bleiben. Unregelmäßige Handschrift, abgeschnittene Ziffern und verdrängte
Überlaufmarker erfüllen das Ziel nicht.

Gefüllte Zellen erhalten eine kräftige Grundfläche in der jeweiligen
Rätselfarbe und eine zurückhaltende Schraffur beziehungsweise Strichtextur.
Variationen bleiben pro Zelle stabil, auch bei erneutem Zeichnen; die
Fläche darf im Inneren leicht organisch wirken. Sie bleibt von Nachbarzellen
und Fünferlinien zuverlässig getrennt. Reine dünne Schraffuren ohne tragende
Grundfläche sind kein bevorzugter Ansatz. Bei kleinen Zellgrößen werden
Texturdetails vereinfacht, damit Motive zusammenhängend erkennbar bleiben.
Ein dominanter Sepiafilter oder schwarze Textur darf die Rätselfarben nicht
einander angleichen.

X bestehen aus zwei kurzen, klaren gezeichneten Stiftstrichen. Auch bei sehr
vielen Auskreuzungen dominiert das entstehende Motiv. Unbekannte Felder
bleiben ruhig; Status und Treffergeometrie sind eindeutig. Die Miniatur
zeigt weiterhin ausschließlich eigene Eingaben einschließlich Fehlern und
Vorschau, verwendet zur Orientierung aber eine einfachere Flächendarstellung
ohne jede kleinteilige Schraffur oder eigene Animationsfolge.

Zusätzliche Randverzierungen als UI-Layer werden nach ZS1-E1/N05 entfernt.
Funktionale Montierungen und ZV-50-Arbeitsfläche bleiben erhalten. Spätere
Hintergrundbildarbeit ist eine zurückgestellte Möglichkeit, kein aktueller
Assetauftrag und kein Gate. Historische Artworkpakete bleiben unverändert.

ZS1-E1 wählt die Stiftfüllung. Das überarbeitete X verwendet zwei stabile,
weniger gleichförmige Stiftzüge. Genau zwei Eigentümer-TTFs, Bakso Daging und
Chalkboard, werden gemäß [E2/Fontinput](ZS1_FONT_INPUT.md) auf derselben
Zellgestaltung verglichen; kein neues breites Font-/Themenscreening. Dieselben echten
Mono-/Farbspielstände, viele X, lange Hinweise und ein Großrasterausschnitt
dienen dem Vergleich bei tatsächlicher Spielgröße. Die ausgewählte Kombination
aus konkreter Hinweisfont, überarbeitetem X und Strichaufbau ist nach ZS1-M01 bestätigt;
ZS-2 integriert sie mit gezielten Regressionen. #24 beurteilt anschließend
die längere reale Nutzung. Die Spezifikationsfreigabe beginnt keines dieser
Umsetzungspakete und ersetzt keine spätere Gestaltungs- oder Bedienabnahme.


**ZS1-E3:** Chalkboard Regular ist die ausgewählte Hinweisfont. Die
Zeilenhinweise links vom Raster werden gegenüber dem 30-px-Studienstand moderat
verdichtet und verwenden 26 logische Pixel gemeinsame Slotweite bei UI 100 %;
die vertikale Staffel der Spaltenhinweise bleibt unverändert. Die kombinierte
Sichtprüfung ist nach Merge von PR #55 auf `main` erfolgreich abgeschlossen.

## 5. Bedienung und Wertung

### 5.1 Präzise Eingaben und Orientierung

Die bestätigte Achsenbindung eines Mausstrichs ab der ersten eindeutigen Bewegung in eine weitere Zelle bleibt verbindlich. Für P1 wird sie erst bei tatsächlicher Rückkehr zur Startzelle innerhalb derselben Geste wieder freigegeben; danach kann eine neue Richtung gewählt werden. Eine bloße Projektion oder ein Eingabesprung über den Start löst dies nicht aus. Produktweit bleiben alternative Eingaben vorgesehen. Für P1 gilt jedoch D-06: Maus, kein Tastatur-/Controller-Gate.

**GP-01/#48 präzisiert D-15:** Das normale Werkzeug neutralisiert vorhandene
Füllungen mit links und X mit rechts. Eine auf unbekannt gestartete Geste setzt
nur unbekannte Zellen und schützt alle Vorbelegungen. Start auf X plus links
wandelt X und unbekannt in die eingefrorene aktive Farbe; Start auf Füllung plus
rechts wandelt Füllungen aller Farb-IDs und unbekannt in X. Rücknahmestriche
bleiben auf Füllungen beziehungsweise X beschränkt, kein direktes Umfärben.
Snapshot, Aktionsmodus und Farbe bleiben auch nach G1-Achsenwechsel fest.
Der konkrete sechszeilige Vertrag steht in P1 §5.1.

**ZS / statische Vorschau, Animation bei Übernahme:** Während der Zellgeste
erscheint die vorgesehene endgültige Markierung ohne Bewegung, leicht heller
beziehungsweise transparenter. Verlängern, Zurückziehen und Abbrechen
aktualisieren diese Vorschau unmittelbar. Erst beim Loslassen und tatsächlichen
Anwenden startet die gerichtete Folge der wirksam geänderten Zellen vom
Gestenstart zum finalen Ende; höchstens 180 ms Startspreizung. Unveränderte oder geschützte Zellen animieren nicht;
Abbruch erzeugt keinen Effekt. Eine neue Vorschau oder Änderung derselben
Zelle hat Vorrang vor einem älteren Effekt.

Der Zeichenauftrag baut die kräftige Füllung räumlich entlang kurzer Stiftzüge
auf oder schreibt sichtbar zuerst den ersten, dann den zweiten X-Zug. Noch nicht
geschriebene Teile eines gestarteten X bleiben unsichtbar; wartende Ziele bleiben
abgeschwächt sichtbar. Effekte bleiben innerhalb ihrer Zelle. Die bestätigte Nacharbeit vom 09.10.2026 verlangsamt Setzen/Umwandeln auf
210 ms je Zelle und Entfernen auf 120 ms. Kurze schräge Schraffurzüge bauen die
Füllung sichtbar strichweise auf; unbeschriebene Abschnitte der aktiven Füllung
bleiben frei. Bloßes Einfaden oder ein flächiger Aufbau genügen nicht. Die Setzfolge endet spätestens nach 390 ms;
Entfernen bleibt ungestaffelt. Schutzlücken zählen nicht für die Staffelung. Eine nächste Eingabe,
Undo/Redo oder ein Seitenwechsel warten nicht auf Animationen. Zellzustand,
Hinweisermittlung, atomare History und Speicherung sind unabhängig vom
Animationsfortschritt. Zellanimationen lassen sich abschalten; der endgültige
Zustand erscheint dann unmittelbar. Einzelheiten und gezielte Prüffälle
stehen in [UI_DRAWING_STYLE.md](UI_DRAWING_STYLE.md). ZS2-E2 ergänzt den Abbruch
durch Gegentasten-Down auch außerhalb des Boards: beide Tasten loslassen, dann
frisch starten; MMB/Hand-Navigation bleibt erhalten.

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
im Produkt. Der spätere separate Z2-Auftrag ersetzt die provisorische Mauspalette
durch unbeschriftete Originalfarbfelder mit formaler Auswahlmarkierung und numerischem
Status/Tooltip; die Hinweisregeln bleiben erhalten. Unabhängige UI-/
Rasterskalierung unterstützt die Lesbarkeit. H1 aus [#19](https://github.com/venomenon328/picross/issues/19)
bleibt die exakte eindeutige Zuordnungsgrundlage. GP-02/#48 unterscheidet normale
Zahlen, leicht abgeschwächte eindeutig gesetzte Blöcke und durchgestrichene
zusätzlich beidseitig abgegrenzte Blöcke. X, echter Rasterrand und direkt andere
Füllfarbe zählen; unbekannte Nachbarn und Viewportränder nicht. GP-03 verwendet
auf dem integrierten Stand kräftigere Plex-Sans-Ziffern mit Gewicht 600 bei bisherigem
Schriftgrad; ZS darf diese Darstellung nach dem engen nativen Vergleich gemäß
Abschnitt 4.4 weiterentwickeln. Nur der
mittlere Zustand erhält 78 % Deckkraft, einschließlich seiner C1-Kontur. Farben
bleiben unterscheidbar; Statuswechsel ändern weder Größe noch Slotposition. Es hängt am Originalindex und gilt ebenso
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

Die spätere reale P1.1-Probe lieferte einen Abschluss-Screenshot und einen Rasterausschnitt mit dem beschriebenen Fünferlinienproblem. Das belegt vorhandenes Nutzerfeedback, nicht jede K-06-Einzelprüfung, tatsächliche Windows-Skalierung oder die Güte der damals noch nicht implementierten Großraster-/Zoom-/Speicherfunktionen. Der damalige Stand ist in #5/#8 und PR #14 nachvollziehbar; die spätere P1-Gesamtabnahme in #12 gilt nicht automatisch für Z2. Aktuelle Z2-Befunde und Gates stehen in #23/PR #33.

Der Squeakross-Screenshot aus dem Gespräch vom 07.10.2026 dient ausschließlich
als Vergleich für eine charaktervolle Spieloberfläche. Er ist ausdrücklich
keine Vorlage für Layout, Zellformen, Motive oder eigene Assets. Die textliche
ZS-Spezifikation trägt die beschlossenen Anforderungen ohne dauerhafte
Pflichtabhängigkeit von diesem fremden Spielbild. Weder der Vergleich noch
die Freigabe dieses Sollstands belegen bereits dessen Implementierung.

## 7. Weitere Erprobung und offene Entscheidungen

| Thema | Nächster Gegenstand |
| --- | --- |
| Themenwahl | Thematisches Sammelalbum oder Reisealbum, Kapitel und Motivzusammenhang; nicht mit dem gewählten Arbeitsasset A verwechseln. Bestehende Progressionsanforderungen nicht neu öffnen. |
| Album/Designsystem | ZS-1 bestätigt nach E1-Nacharbeit die gewählte Stiftgrundlage mit neuem X/Strichaufbau und zwei durch E2 akzeptierten Eigentümer-TTFs; ZS-2 integriert diese Auswahl ohne zusätzliche Rand-UI. Ein vollständiger Albumneubau ist nicht beauftragt. |
| Rücknahmen/Wertung | Direkte Neutralisierung ist für die Bedienung festgelegt; Fehlerzählung, Sterne und Hypothesenwirkung bleiben offen. |
| P1-Bedienung | P1/Z2 ist integriert; Z2-M01/M02 wurden nicht durchgeführt, ihr damaliges Mergegate aufgehoben. Eigene aktuelle RP-3-Nachweise stehen im [Prüfbericht](RP3_VERIFICATION.md). |
| Fortsetzung | Speicherung/Recovery bleiben Regressionsumfang; Z2-M03 wurde nicht durchgeführt und für PR #33 als Gate aufgehoben. F-04 erhält einen eigenen isolierten Neustartnachweis. |
| Designphase | Längere reale Nutzung und Phasenabschluss folgen in #24 nach der technisch geprüften ZS-2-Fassung. Pflichtregressionen gehören bereits zur Umsetzung. |

Gestaltung und Risikoprototypen überlappen weiter. Statische Mocks allein beantworten keine Bedienungsfrage. GD-01 bis GD-05 legen die konkrete Zielrichtung für Z2 fest, ersetzen aber keine native Bedienabnahme oder vollständige Produktgestaltung.

Rätselproduktion und Deduktionsnachweis bleiben ein eigener früher Risikostrang. Hübsche Bilder allein sind keine qualitätsgeprüften Rätsel. Verbundraster getrennt evaluieren. Thema, Designsystem und zentrale Ansichten anhand der Erfahrungen schärfen, bevor umfangreiche Inhalte produziert werden.

Die [Produktionsspezifikation](PUZZLE_PRODUCTION.md) vom 03.10.2026 konkretisiert
diesen Risikostrang mit Motivschutz, getrenntem Deduktionsnachweis und Pilotabnahme.
ChatGPT-/Codex-Arbeit liefert gespeicherte Vorlagen und Abschlussbilder; das
Produktionswerkzeug verwendet keine direkte Modell-API. Die hier festgelegte
Motivtreue und die Spoilergrenze bleiben für sämtliche neuen Inhalte verbindlich.

## VS-1 · experimentelle Vollsichtprobe (#57)

Der [VS-1-Studienvertrag](VS1_STUDY.md) bindet zehn native Beispiele, aktuell G/V nach VS-E1-R2,
die ausgewählte ZS-1-Zeichenschicht und getrennte Studienfortsetzung.
[Prüfzuordnung](VS1_VERIFICATION.md) und [Eigentümerprobe](VS1_OWNER_TRIAL.md)
trennen technische Lieferung und persönliche Komfortbefunde. [VS-D01](VS1_DECISION.md)
ist strategisch entschieden: reguläres Vollsichtziel 40×40, mindestens 30×30,
geeignete 40×30/50×30, 1080p, bevorzugt G und ergänzend V. Sehr große Rätsel
bleiben mögliche Sonderfälle. PR #58 ist als `c19b3547…` integriert; VS-GF1/#59
liefert zusätzliche Zeilenkapazität aus freier G-Breite bei unverändertem Fit.
Die reguläre P1-Umstellung bleibt separat. VS-M01 ist nicht vollständig persönlich
durchgeführt; unabhängiges Review, GF-M01 und Mergefreigabe des neuen Heads bleiben offen.

VS-E1-R2 aus #57 §11 ersetzt für diese Studie die früheren R-/Hand- und
pauschalen Hinweisreserven. Achsengetrennter tatsächlicher Bedarf, fünf vollständige
zusammenhängende Zahlen auch im Drag und eine harte Raster-Fitgrenze sind aktiv.
Historische Erstlieferung bleibt gebunden; normale P1-Defaults bleiben bestehen.
