# Produktdefinition: picross

Stand: 25.09.2026 · Arbeitsfassung 0.3 · Produktkonzept mit begrenzter H1-Komfortentscheidung

## 1. Geltung und Herkunft

Dieses Dokument konsolidiert das Produktgespräch einschließlich der ausdrücklich beantworteten Fragen 1–22 und der anschließenden Gestaltungskonversation vom 22.09.2026. Maßgeblich sind die zuletzt bestätigten Nutzerentscheidungen. Frühere Alternativen und Empfehlungen werden nicht allein durch ihre Erwähnung zu Anforderungen. Das [Gestaltungskonzept](DESIGN_CONCEPT.md) ergänzt die bestätigte visuelle Grundlage, offene Themenalternativen und noch zu prüfende Interaktionen.

Die Abschnitte 2–9 beschreiben die beschlossene Produktausrichtung und kennzeichnen verbleibende Detailfragen. Abschnitt 10 sammelt Ausgestaltungsideen und verweist bei inzwischen bestätigtem Komfort ausdrücklich auf den neuen Vertrag; Abschnitt 11 hält offene Entscheidungen fest. Der Ablauf in Abschnitt 12 ist eine grobe Orientierung, kein beauftragter Implementierungsplan. Lieferumfang, Akzeptanz und Fortschritt konkreter Pakete stehen weiterhin in den jeweiligen Issues und PRs.

Dieses Dokument entscheidet keine Engine, Programmiersprache, Betriebssystemmatrix oder Architektur. Es ersetzt weder konkrete Fachverträge noch eine spätere Prüfung der technischen und wirtschaftlichen Machbarkeit. Projektregeln und Prüfwege stehen im [Projektprofil](PROJECT_PROFILE.md).

## 2. Produktkern und Zielgruppe

Ein thematisch zusammenhängendes Nonogramm-Spiel für PC, dessen Hauptreiz in logischen Erkenntnissen und dem Bearbeiten größerer Bildrätselprojekte liegt. Eine präzise, komfortable Bedienung soll auch große Raster und mehrteilige Spielsitzungen angenehm machen. Anspruch entsteht aus dem Rätsel, nicht aus vermeidbarem Zählen, Fehlbedienung oder Orientierungsverlust.

Die Zielgruppe sind erfahrene Nonogramm-Spieler sowie interessierte Rätselspieler, die sich schnell einfinden. Es gibt einen Erklärungsbereich oder kurze Tutorial-Rätsel. Menschen umfassend das Nonogramm-Lösen beizubringen, ist nicht der Schwerpunkt; umfangreiche Hilfen und Übungsstrecken sind ausdrücklich nachrangig.

Prioritäten des Spielerlebnisses:

1. Logische Erkenntnisse und das Bewältigen großer Projekte.
2. Erkennbare Motive und ihre befriedigende Enthüllung als wesentlicher Bestandteil der Belohnung.
3. Persönliche Entwicklung und Leistungsvergleich als Ergänzung, nicht als dominierender Spielzweck.

Groß und schwierig sind unterschiedliche Eigenschaften. Ein großes, flüssig lösbares Projekt und ein kleines, sehr kniffliges Rätsel dürfen beide ihren Platz haben. Ein neuartiger Regel-Twist ist keine Voraussetzung für ein eigenständiges Basisprodukt.

## 3. Rätselbestand und Qualitätsversprechen

### 3.1 Umfang und Größen

Für die erste Veröffentlichung sind einige Hundert vorab erstellte und kuratierte Rätsel ein angemessenes Wunschziel. Exakte Stückzahlen, das Verhältnis der Varianten und die Größenverteilung werden nach einer repräsentativen Testproduktion festgelegt, nicht bereits als zugesicherter Lieferumfang behandelt.

Rätsel jenseits von ungefähr 40×40 sollen ein dauerhaft substanzielles Angebot bilden, nicht nur einzelne Abschlussaufgaben. Auch um 100×100 soll eine vernünftige Auswahl angestrebt werden. Übertriebene Riesenprojekte deutlich jenseits von 100×100 sind denkbar, dürfen aber selten bleiben und sind keine bestätigte Startvoraussetzung. Kleinere und mittlere Formate bleiben ebenfalls Bestandteil des Spiels.

Ein größeres Rätsel darf sich über mehrere Sitzungen erstrecken. Die Bedienung und Fortschrittsspeicherung müssen diesen Nutzungsfall von Anfang an berücksichtigen.

### 3.2 Lösbarkeit und Schwierigkeit

Die Rätsel sollen eindeutig und vollständig deduktiv lösbar sein. Notwendiges Raten beziehungsweise das versuchsweise Durchspielen von Annahmen mit anschließendem Zurückspringen ist ausgeschlossen. Eindeutigkeit allein reicht nicht als Nachweis dieses Versprechens.

Über einzelne Zeilen und Spalten hinausgehende Schlussfolgerungen sind erlaubt. Ein sinnvoll gestaffeltes Schwierigkeitssystem ist gewünscht; Rastergröße, Bearbeitungsumfang und logischer Anspruch dürfen nicht zu einer einzigen undifferenzierten Eigenschaft zusammenfallen. Die zugelassenen Schlussregeln und der konkrete Nachweis werden noch spezifiziert.

Es gibt keine zusätzlichen redaktionell vorgegebenen Startfelder. Klassische und farbige Rätsel müssen aus ihren regulären Randhinweisen heraus lösbar sein. Unmittelbar aus diesen Hinweisen ableitbare Felder sind davon zu unterscheiden.

### 3.3 Motive und Abschlussansicht

Jedes reguläre Rätsel soll ein erkennbares Bild ergeben, gegebenenfalls stark abstrahiert. Zufälliges Rauschen und reine abstrakte Formen gehören nicht in den Katalog. Allenfalls bei den kleinsten Dimensionen sind begründete Ausnahmen denkbar, wenn ein tatsächliches Motiv kaum darstellbar ist; Kriterien hierfür sind noch offen.

Ein monochromes Raster muss sein Motiv nicht bereits im uneingefärbten Ergebnis zweifelsfrei erkennen lassen. Eine kolorierte Abschlussansicht soll die Abstraktion zu einem klaren Motiv auflösen können. Das gelöste Raster und die Enthüllung sollen dabei nachvollziehbar zusammengehören. Farbige Rätsel sollen bereits selbst als Bild erkennbar sein.

Gesammelt werden die erarbeiteten Bilder selbst, nicht davon unabhängige Belohnungsillustrationen. Bei monochromen Rätseln ist eine farbige Repräsentation des tatsächlichen Motivs vorgesehen; sie darf gegebenenfalls etwas höher aufgelöst sein, muss aber klar als Repräsentation des gelösten Rastermotivs erkennbar bleiben. Eine zusätzliche hochaufgelöste Fassung jedes Motivs ist damit nicht verpflichtend. Konkrete Übergänge und Darstellungsregeln werden im [Gestaltungskonzept](DESIGN_CONCEPT.md) untersucht.

Vor Abschluss werden weder das fertige Lösungsbild noch der Motivname gezeigt. Während des Lösens ist jederzeit eine Miniatur des aktuellen eigenen Bearbeitungsstands sichtbar. Sie basiert nur auf den Eingaben des Spielers, einschließlich möglicher Fehler, nicht auf einer korrigierten oder vorweggenommenen Lösung. Darstellung und Platzierung werden im UI-Konzept ausgearbeitet.

### 3.4 Inhaltsproduktion

Das Basisprodukt enthält eine vorab kuratierte Sammlung, keinen notwendigen Laufzeitgenerator und keine Abhängigkeit von Community-Nachschub. Gewünscht ist ein externes Produktionswerkzeug, das Entwürfe aus Beschreibungen oder bereitgestellten Bildern unterstützt.

Der vorgesehene Arbeitsablauf ist: Motividee oder Vorlage, Rasterentwurf, logische Prüfung, Überarbeitung und redaktionelle Freigabe einschließlich der Abschlussansicht. Wie weit die Schritte automatisiert werden können, ist zu untersuchen. Eine Bildvorlage liefert nicht automatisch ein geeignetes Rätsel.

Logische Prüfung sowie gestalterische und spielerische Kuratierung sind getrennte Qualitätsaufgaben. Die interne Prüfung der deduktiven Lösbarkeit wird früh benötigt, auch wenn die spielerseitige Hilfefunktion erst deutlich später kommt.

Spielerseitiger Bildimport beziehungsweise Generierung ist eine mögliche ferne Erweiterung. Ein DLC wurde als Möglichkeit angesprochen, aber weder beschlossen noch als Finanzierungsmodell festgelegt.

## 4. Varianten und Priorisierung

| Variante | Produktstatus |
| --- | --- |
| Klassische monochrome Nonogramme | Verbindlicher Kern des Basisprodukts. |
| Farbige Nonogramme | Verbindlicher Kern; Farben werden früh in Daten- und Bedienkonzept berücksichtigt. |
| Logisch verknüpfte Verbundraster | Früh mit einem begrenzten Prototyp evaluieren; kein notwendiges Merkmal der ersten Veröffentlichung. |
| Zusätzliche Regionenbedingungen | Ebenfalls evaluierbar, aber mit geringerer Priorität als Verbundraster. |
| Unvollständige beziehungsweise unbekannte Hinweise | Vorerst ausdrücklich außen vor. |

Für farbige Nonogramme gilt: Aufeinanderfolgende Blöcke derselben Farbe benötigen mindestens ein leeres Feld dazwischen. Blöcke unterschiedlicher Farbe dürfen unmittelbar aneinandergrenzen, müssen es aber nicht. Die Hinweise geben Blocklänge und Farbe an.

Verbundraster bezeichnen echte logische Abhängigkeiten durch gemeinsame Felder oder Bereiche, nicht bloß unabhängige Einzelrätsel, die am Ende ein großes Bild ergeben. Der erste Prototyp soll prüfen, ob solche Abhängigkeiten interessant und verständlich sind. Die konkrete Geometrie ist nicht festgelegt.

Regionenbedingungen würden zusätzliche Bedingungen für markierte Bereiche ergänzen, etwa eine Anzahl gefüllter Felder. Ihre genaue Form und Aufnahme in das Produkt sind nicht entschieden.

## 5. Bedienung, Orientierung und visuelle Identität

### 5.1 Verbindliche Leitlinien

Die Handhabung soll intuitiv, präzise und unkompliziert sein. Große Raster sind ein zentraler Auslegungsfall, kein späterer Belastungstest. Zoom ist dafür wichtig, reicht aber ohne gute Orientierung beim Scrollen nicht aus. Im Ausschnitt müssen Arbeitsposition und zugehörige Hinweise nachvollziehbar bleiben; die Rückkehr zu relevanten Bereichen und der Wiedereinstieg nach einer Pause sind früh zu gestalten.

Maus und Tastatur sind die primäre Eingabeform. Controller werden von Beginn an als alternative Eingabemethode vorgesehen und in die Interaktionskonzeption einbezogen, nicht erst nachträglich auf eine ausschließlich mausabhängige Oberfläche aufgesetzt. Touch oder eine Mobile-Version sind nicht beschlossen.

Ein ausdrücklich gewünschtes Steuerungsdetail: Beim Zeichnen mit gedrückter Maustaste wird die Bewegung ab dem zweiten Feld auf die aktuelle Zeile oder Spalte beschränkt; innerhalb dieses Strichs werden keine Kurven gezeichnet. Verhalten bei Rückwärtsbewegung, vorhandenen Einträgen, Abbruch und diagonalen Bewegungen wird noch spezifiziert.

Speichern, Unterbrechen und Fortsetzen großer Rätsel sowie verlässliches Rückgängigmachen gehören zum Komfortkonzept. Wie viel des Arbeitszustands zusätzlich zum Raster gespeichert wird, ist im Detail offen; entsprechende Ideen stehen in Abschnitt 10. Die Nutzung von Undo schließt eine perfekte Bewertung des betroffenen Durchgangs aus, ohne die Funktion zu verbieten; siehe Abschnitt 6.2.

Bestätigt in [#19/H1](https://github.com/venomenon328/picross/issues/19): Hinweise
werden optional, standardmäßig aktiv als erfüllt markiert, wenn ihr bereits vollständig
gesetzter Block in jeder mit den sichtbaren Zellen vereinbaren Belegung der ganzen
Linie eindeutig denselben Hinweis realisiert. Bei Widerspruch entfällt jede Markierung
dieser Linie. Nur deren eigene Hinweise, Farben, Füllungen und X zählen; kein Vergleich
mit der hinterlegten Lösung oder kreuzenden Hinweisen. Das ist keine Fehlerhilfe,
kein manuelles Abhaken und kein automatisches Setzen. Der begrenzte P1-Vertrag samt
Vorschau, Durchstreichung und Sitzungsschalter steht in P1 §5.2.

Hypothesen als mögliche Zustände „unsicher gesetzt“ und „unsicher leer“ wurden zur Untersuchung vorgeschlagen. Die Funktion ist noch nicht abschließend spezifiziert; insbesondere ist nicht entschieden, ob ihre Nutzung mit einer perfekten Bewertung vereinbar ist. Der Nutzer setzt selbst überwiegend nur sicher hergeleitete Felder. Hypothesen ändern nicht das Versprechen, dass Rätsel ohne notwendiges Raten lösbar sein müssen.

### 5.2 Frühe visuelle Arbeit

Thematik, visuelle Identität und weit ausgearbeitete UI-Konzepte werden früh und parallel zur Funktionalität bearbeitet. Die Gestaltung ist kein abschließender Skin über einer bereits fertigen Oberfläche. Ebenso werden frühe Entwürfe nicht vor praktischer Erprobung unveränderlich festgeschrieben.

Das Spiel soll eine spürbare thematische Tätigkeit vermitteln und seine Sammlungen, Bearbeitung und Enthüllungen gestalterisch zusammenführen. Eine komplexe Geschichte ist nicht erforderlich. Eine zusätzliche Wirtschaftssimulation, Währungen oder ein Aufbauspiel folgen daraus nicht automatisch.

Als gemeinsame Grundlage ist ein sich füllendes Album beschlossen. Die Gestaltung geht in Richtung handgezeichneter 2D-Illustration mit klaren gezeichneten Konturen und ruhigen, nicht zu blassen Farbflächen. Die Stimmung soll warm, neugierig und dennoch ruhig sein. Die Thematik bleibt auch während des Rätsels zurückhaltend sichtbar; die Arbeitsansicht soll nicht steril wirken, das Raster selbst aber sachlich und präzise bleiben.

Die endgültige Themenwahl bleibt ausdrücklich offen: A ist ein thematisches Sammelalbum, B ein Reisetagebuch beziehungsweise Weltreisealbum mit regionalen Motiven. Die näheren Entscheidungen, Beispiele und offenen Interaktionen stehen im [Gestaltungskonzept](DESIGN_CONCEPT.md). Die positive Rückmeldung zu einem exemplarischen Mock legt weder eine dieser Alternativen noch alle darin dargestellten Details verbindlich fest.

Die zentralen Ansichten werden auch mit langen Hinweisfolgen, farbigen Rätseln, großen Rastern und beiden Eingabeformen überprüft. Lesbarkeit und Bedienbarkeit haben Vorrang vor dekorativer Inszenierung. Sound wird vorerst nach hinten gestellt. Als spätere Richtung sind kleine angenehme und unauffällige Effekte sowie ein besonders gelungener Abschlussjingle gewünscht; zurückhaltende Hintergrundmusik ist denkbar. Eine konkrete Audioproduktion ist noch nicht beauftragt.

### 5.3 Persönliche Referenzen aus dem Produktgespräch

Dies sind vom Nutzer benannte Erfahrungen und Vorbilder, keine recherchierte Marktanalyse:

- Mario's Picross (Game Boy) und Mario's Super Picross (SNES): positive Referenzen für Präsentation und Progression. Insbesondere die kolorierte Auflösung abstrahierter monochromer Motive dient als Anschauung für das gewünschte Erlebnis.
- Griddlers (PC): Erfahrung mit sehr großen und farbigen Rätseln. Trotz Zoom kam es beim Scrollen großer Raster zu Orientierungsverlust; genau diese Schwäche soll das eigene Bedienkonzept vermeiden.

Die Referenzen legen weder eine Nachbildung ihrer Gestaltung noch die Übernahme fremder Assets nahe.

## 6. Sammlungen, Sterne und Progression

### 6.1 Echte Progression mit Bibliothek

Reguläre Sammlungen beziehungsweise Rätselpakete dürfen zunächst gesperrt sein und über erreichte Sternschwellen geöffnet werden. Nicht jedes vorangehende Rätsel muss zwingend gelöst werden, um weiterzukommen.

Mehrere Zugänge sollen früh verfügbar sein, darunter große und anspruchsvolle Rätsel. Erfahrene Spieler müssen nicht erst eine lange Pflichtstrecke aus kleinen Einsteigerrätseln absolvieren, bevor sie ihre bevorzugte Rätselart erreichen.

Die thematische Präsentation bildet den Zusammenhang. Ergänzend bündelt eine Bibliothek alle bereits freigeschalteten Rätsel unabhängig von dieser Navigation. Bibliothekszugriff bedeutet daher nicht, dass sämtliche Inhalte von Anfang an entsperrt sind.

Die bevorzugte Sammlungspräsentation ist ein Album, das sich mit den erarbeiteten Bildern nach und nach füllt und einen erkennbaren vollständigen Zustand erreichen kann. Eine zusätzliche Raum-/Ausstellungsansicht ist keine bestätigte Anforderung. Konkrete Kapitel, Seitenaufteilung und die visuelle Unterscheidung von Sammlungsvollständigkeit und Meisterschaft bleiben auszugestalten.

### 6.2 Fehlerbasierte Bewertung und Perfektionsbedingung

Eine einfache Bewertung, voraussichtlich auf einer dreistufigen Skala, ist gewünscht. „Sterne“ ist ein vorläufiger Arbeitsbegriff, keine Entscheidung für das spätere visuelle Motiv.

Fehler bestimmen die Bewertung; für Perfektion gilt zusätzlich die ausdrücklich bestätigte Bedingung: ein Durchgang ohne Fehler und ohne Undo. Damit ist die frühere Formulierung „ausschließlich fehlerbasiert“ für die Höchstwertung abgelöst. Im bisherigen Drei-Sterne-Arbeitsmodell schließt eine tatsächlich ausgeführte Rücknahme drei Sterne aus, auch wenn der zurückgenommene Eintrag korrekt war. Undo bleibt als Komfortfunktion verfügbar.

Die Perfektionsbedingung bezieht sich auf den gesamten Durchgang. Redo oder Speichern und Fortsetzen machen eine bereits ausgeführte Rücknahme nicht ungeschehen. Ein Neustart ist davon getrennt zu spezifizieren. Ob manuelles Löschen, Zurücksetzen auf „unbekannt“ oder Überschreiben wie Undo zählen und ob Hypothesen mit Perfektion vereinbar sind, bleibt ausdrücklich offen; keine Entscheidung allein aus den Mocks ableiten.

Die Lösungszeit fließt aus Gründen der Barrierefreiheit weder in Sterne noch in Freischaltungen ein. Sie darf weiterhin dokumentiert und für freiwillige Ranglistenvergleiche verwendet werden.

Die genaue Skala unterhalb der Höchstwertung, Fehlertoleranz und Fehlerdefinition sind noch nicht beschlossen. Auch die Behandlung von Wiederholungen und Bestbewertungen wird separat spezifiziert; Empfehlungen dazu stehen in Abschnitt 10. Beispielhafte Zahlen aus dem Gespräch sind keine verbindlichen Schwellen. Aus „Undo verhindert Perfektion“ folgt keine bereits beschlossene Anzahl zusätzlicher Fehler oder feste Bewertung für einen Durchgang mit Undo.

### 6.3 Bonusrätsel und Perfektion

Zusätzliche Bonusrätsel bei bestimmten Sternschwellen sind eine gewünschte Ausgestaltungsmöglichkeit; ihre genaue Verteilung ist offen. Verbindlich ist: Die perfekte Lösung aller regulären Rätsel einer Sammlung schaltet mindestens ein weiteres Bonusrätsel frei. Diese Belohnung wird nicht durch eine rein kosmetische Anerkennung ersetzt.

Meisterschaftsziele bilden optionale Vertiefungen neben der regulären Weiterreise. Sie sollen nicht zur Pflicht werden, um weitere reguläre Sammlungen erreichen zu können. Die für ein Bonusrätsel relevante Menge regulärer Rätsel und seine Voraussetzungen müssen eindeutig definiert werden, ohne zirkuläre Freischaltungen.

Was die ebenfalls perfekte Lösung des oder der Bonusrätsel belohnt, bleibt ausdrücklich offen. Achievements sind dafür ein gewünschter möglicher Anreiz, insbesondere bei einer Steam-Veröffentlichung. Zusätzliche Abschlussbelohnungen werden später gesondert betrachtet; eine endlose Folge weiterer Bonusrätsel ist nicht festgelegt. Bezeichnungen wie „abgeschlossen“, „perfektioniert“ und „gemeistert“ sind bisher nur Vorschläge.

## 7. Spielmodi, Fehler und Leistungsvergleich

### 7.1 Standard und Fehlerhinweise

Im Standardmodus gibt es während des Lösens keine unmittelbaren Hinweise auf falsch gesetzte Felder. Fehler werden für die spätere Auswertung protokolliert, aber nicht über einen live sichtbaren Fehlerzähler oder eine sinkende Sterneanzeige verraten. Die Anzeige darf die ausgeschaltete Fehlerhilfe nicht indirekt wieder einführen.

Ein optionaler einfacherer Modus weist auf Fehler hin. Entsprechende Durchgänge werden im Logbuch eindeutig gekennzeichnet. Ranglisten für unterstützte und nicht unterstützte Leistungen werden getrennt geführt.

Sterne aus unterstützten Durchgängen zählen gleichberechtigt für Freischaltungen. Der Inhalt soll nicht hinter einem erzwungenen Wechsel in den Standardmodus liegen. Welche Leistung unter welchen Bedingungen erbracht wurde, bleibt trotzdem dokumentiert und getrennt vergleichbar.

Die technische Behandlung eines Moduswechsels innerhalb eines Durchgangs wird noch spezifiziert. Als konsistenter Vorschlag gilt, einen einmal unterstützten Durchgang nicht durch späteres Ausschalten der Fehlerhinweise nachträglich als ununterstützt zu werten. Zoom, Achsenbindung und vergleichbare Eingabekomfortfunktionen sind keine lösungsverratenden Hilfen.

### 7.2 Logbuch, Ranglisten und Offline-Spiel

Das persönliche Logbuch erfasst mindestens Lösungszeit, Fehlerzahl, Ergebnis beziehungsweise Bewertung und den verwendeten Unterstützungsmodus. Globale und Freundesranglisten gehören zur gewünschten Produktausrichtung; genaue Vergleichsmetriken und Plattformintegration folgen später. Wochenherausforderungen sind eine mögliche spätere Erweiterung, keine Startvoraussetzung.

Das vollständige Solo-Spiel funktioniert offline, einschließlich Fortschritt und persönlicher Statistik. Offline gespielte Durchgänge werden lokal protokolliert und können später optional für Ranglisten übertragen werden. Eine dauerhafte Onlineverbindung ist keine Voraussetzung für reguläre Rätsel oder ihre Freischaltungen.

Ein plausibles Prüf- und Übertragungsmodell ist zu spezifizieren. Es wird kein manipulationssicherer Wettkampf und keine nachweisbare Verhinderung externer Lösungshilfen versprochen. Online-Ranglisten ergänzen das Spiel, bestimmen aber nicht seinen Hauptzweck.

## 8. Entwicklungs- und Veröffentlichungsrahmen

Das Projekt wird als Solo-Entwicklung mit dem mittelfristigen Ziel einer kommerziellen Veröffentlichung und späterer Erweiterung geplant. Unterstützung durch befreundete Designer wird für Grafiken in Betracht gezogen. Umfang, Budget, Zeitplan und konkrete Zusammenarbeit sind noch nicht festgelegt. Sound hat vorerst geringere Priorität.

PC ist die beschlossene grundsätzliche Zielrichtung; konkrete Betriebssysteme, Engine, Programmiersprache, Datenhaltung und Build-/Exportwege bleiben offen. Steam ist ein angestrebter beziehungsweise naheliegender Veröffentlichungskontext, aber keine bereits eingerichtete oder abschließend spezifizierte Integration. Preis, Lizenzierung und ein konkretes Erweiterungsmodell sind nicht beschlossen.

Die vorhandenen Python-Dokumentprüfer sind keine Festlegung des Produktstacks. Vor Produktimplementierung sind die tatsächlich betroffenen Fachverträge, technischen Entscheidungen und Akzeptanzkriterien zu konkretisieren.

## 9. Abgrenzung des ersten Produkts

Zum Produktkern gehören klassische und farbige kuratierte Bildrätsel, ein nennenswerter Großrasterbestand, komfortable Bearbeitung und Fortsetzung, frühe thematische/UI-Konzeption, Sammlungsprogression, Perfektions-Bonusrätsel, die beiden Fehler-Rückmeldungsmodi sowie Logbuch und vorgesehene Leistungsvergleiche.

Nicht als Startvoraussetzung beschlossen sind Verbundraster, Regionenbedingungen, extreme Raster weit jenseits von 100×100, ein öffentlicher Editor, Community-/Workshop-Inhalte, Koop, spielerseitige Bildgenerierung, Wochenherausforderungen und umfangreiche Lern- oder Erklärhilfen. Diese Themen dürfen nicht stillschweigend den verbindlichen Umfang vergrößern. Unvollständige Hinweise sind vorerst ausgeschlossen.

Eine umfangreiche Geschichte, ein zusätzliches Wirtschaftsspiel, ein Mobile-/Touch-Produkt und laufend verpflichtend zu liefernde neue Inhalte wurden nicht beauftragt. Marktpotenzial und Verkaufszahlen sind nicht belegt; die angenommene Positionierung ist keine bestätigte Nachfrageprognose.

## 10. Bereits diskutierte, noch zu prüfende Ausgestaltungsideen

Die folgende Sammlung bewahrt sinnvolle Ansätze aus dem Gespräch, ohne sie zu fertigen Fachverträgen oder zugesagtem Releaseumfang zu erklären:

| Bereich | Vorschlag beziehungsweise Untersuchung |
| --- | --- |
| Großraster | Fixierte Hinweise, Hervorhebung der aktiven Zeile/Spalte, vollständiger In-Context-Zugriff bei Überlauf, Lesezeichen und aussagekräftige Ausschnittnavigation. |
| Eingaben | Eindeutige Aktion pro Ziehvorgang statt unerwartetem Umschalten überfahrener Felder; Längenzähler, Linealmodus und Abbruchmöglichkeit. |
| Undo/Redo | Rücknahme zusammenhängender Aktionen beziehungsweise ganzer Striche; Fehlerhistorie, manuelle Korrekturen und genaue Aktionsgrenzen spezifizieren. Der Perfektionsausschluss durch Undo ist bereits in Abschnitt 6.2 beschlossen. |
| Hypothesen | „Unsicher gesetzt“ beziehungsweise „unsicher leer“, bei Farben mit Farbzuordnung; separate Notizebene als Vorschlag. Aufnahme, Übernahme-/Verwerfverhalten und Verträglichkeit mit Perfektion bleiben offen. |
| Arbeitszustand | Neben dem Raster auch Zoom, Ausschnitt, aktive Farbe und gegebenenfalls Notizen speichern; optionale Hervorhebung der letzten Änderungen beim Wiedereinstieg. |
| Farbdarstellung | Symbole oder Muster zusätzlich zu Farben, geeignete Paletten und schnelle Farbwahl über Hinweise. |
| Automatischer Komfort | Die lösungsunabhängige optionale Erfüllungsmarkierung ist durch #19/H1 bestätigt; siehe §5.1 und P1 §5.2. Weitere Hilfen sind dadurch nicht freigegeben. |
| Qualitätssicherung | Erklärender Solver mit vollständigem Deduktionsprotokoll und gegebenenfalls unabhängiger Eindeutigkeitsprüfung; konkrete Verfahren noch offen. |
| Sterne | Ein Stern für Abschluss und zwei bei begrenzten Fehlern bleiben Vorschläge ohne feste Schwellen. Für die Höchstwertung gilt bereits: ohne Fehler und ohne Undo; Hypothesenfrage offen. |
| Wiederholungen | Beste Bewertung je Rätsel für Fortschritt verwenden; Sterne nicht durch wiederholtes Lösen aufsummieren und bestehende Freischaltungen nicht durch schlechtere Ergebnisse verlieren. |
| Fehlerbehandlung | Keine Leben, erzwungenen Abbrüche oder Strafsekunden; fehlerhafte Aktionen und betroffene Felder gegebenenfalls getrennt erfassen. |
| Zeitmessung | Explizite Pausen und Sitzungswechsel definieren, Denkzeit nicht durch bloße Inaktivität herausrechnen; Erstlösungen und Wiederholungen unterscheiden. |
| Spätere Erweiterungen | Erklärende Hilfen, Technik-Übungsstrecken, öffentlicher Editor mit Prüfung, Community-Inhalte und Koop wurden diskutiert, aber nicht für das Basisprodukt zugesagt. |

## 11. Offene Entscheidungen für die weitere Spezifikation

| Kennung | Offene Entscheidung |
| --- | --- |
| O-01 | Wahl zwischen thematischem Sammelalbum und Reisealbum; konkrete Kapitel, Layouts, Designsystem und Enthüllungsdetails auf Basis der bestätigten Album-/Illustrationsrichtung. |
| O-02 | Prüffähige Definition der zugelassenen Deduktionen, Eindeutigkeitsprüfung und Schwierigkeitseinstufung. |
| O-03 | Exakte Startmenge, Größen- und Variantenverteilung; Auswahlkriterien und zulässige Ausnahmen bei winzigen Motiven. |
| O-04 | Produktionsverfahren aus Beschreibungen/Bildvorlagen, Kurationsaufwand und Nutzungsrechte der eingesetzten Vorlagen und Assets. |
| O-05 | Was als Fehler zählt; Behandlung falscher Leer-/Farbmarkierungen, Striche und Wiederholungen; Abgrenzung manueller Korrekturen zu Undo und mögliche Hypothesen. |
| O-06 | Skala/Fehlertoleranzen unterhalb der Höchstwertung, Bestbewertungen und Wiederholungen, Wechsel zwischen Unterstützungsmodi; Vereinbarkeit von Hypothesen mit der bestätigten Perfektionsregel ohne Fehler und ohne Undo. |
| O-07 | Aufbau und frühe Zugänge der Sammlungen, konkrete Freischaltschwellen, Abhängigkeiten und Umfang der Bonusinhalte. |
| O-08 | Belohnungen nach perfekter Lösung der Bonusrätsel, Achievement-Katalog und gegebenenfalls weitere Abschlussinszenierung. |
| O-09 | Detailverhalten von Maus-/Tastatur- und Controllersteuerung, Zoom/Scrollen, Miniatur, Hinweisen und Arbeitszustand. |
| O-10 | Zeitmessung und Pausen, Erst-/Wiederholungslösungen, Ranglistenmetriken, Offline-Upload und Ergebnisprüfung. |
| O-11 | Engine, Sprache, konkrete PC-Betriebssysteme, Persistenz, Datenformate, Migrationen und Produkt-Teststrategie. |
| O-12 | Veröffentlichungskanal und Integration, Preis, Lizenz-/Erweiterungsmodell, Budget und Umfang externer Unterstützung. |
| O-13 | Ergebnis der Verbundraster-Erprobung; gegebenenfalls spätere Entscheidung über Regionenbedingungen. |

Diese offenen Punkte verhindern nicht die Arbeit an unabhängigen Konzepten. Sie sind jedoch vor einer davon abhängigen Implementierung gezielt zu entscheiden. Die bereits bestätigten Antworten werden dabei nicht unnötig erneut zur Disposition gestellt.

## 12. Grober Spezifikations- und Entwicklungsablauf

Diese Reihenfolge bewahrt den besprochenen Ablauf als Orientierung. Sie setzt keine Termine, erzeugt keine Umsetzungspakete und ersetzt keine Issue-/PR-Planung.

1. **Produktkern und Prioritäten:** Gemeinsames Produktbild festhalten. Dieses Dokument konsolidiert die bisherigen Entscheidungen; konkrete Fachverträge folgen.
2. **Thematik, visuelles Konzept und Bedienung:** Mehrere Richtungen anhand derselben repräsentativen Spielansichten vergleichen, eine Richtung auswählen und zentrale Abläufe weit ausarbeiten. Kleine, farbige und sehr große Raster berücksichtigen. Die bestätigte gemeinsame Grundlage und der noch nicht abschließende Mockstand stehen im [Gestaltungskonzept](DESIGN_CONCEPT.md).
3. **Risikoprototypen:** Parallel zur Gestaltung die Orientierung und Eingabe in Großrastern, die Erzeugung/Prüfung guter Bildrätsel und einen begrenzten Verbundraster-Prototyp untersuchen. Gestaltung anhand der Ergebnisse korrigieren, bevor umfangreiche Assets produziert werden.
4. **Kleine vollständige Fassung:** Einen zusammenhängenden Ablauf von Auswahl bis Abschluss in der gewählten Gestaltung herstellen, mit wenigen repräsentativen Rätseln einschließlich eines großen, Speicherung/Fortsetzung und grundlegender Auswertung.
5. **Ausbau und Inhalte:** Beschlossenen Funktionsumfang, Produktionswerkzeuge und kuratierte Sammlung ausbauen. Konkrete Lieferpakete erst anhand der vorherigen Ergebnisse festlegen.
6. **Erprobung und Veröffentlichung:** Bedienbarkeit, Rätselqualität, Performance, Spielstände und tatsächliche Zielplattformen prüfen und verfeinern. Externe Spieltests beginnen bereits mit geeigneten Prototypen und nicht erst am Ende.

Ein wesentlicher erster Nachweis ist erreicht, wenn ein anspruchsvolles großes Rätsel angenehm spielbar ist, das Spiel bereits eine erkennbare Identität besitzt und die Rätselqualität mit einem geeigneten Verfahren überprüft werden kann. Eine grüne Dokumentations-CI weist davon noch nichts nach.
