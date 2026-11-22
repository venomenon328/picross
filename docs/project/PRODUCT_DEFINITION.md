# Produktdefinition: picross

## 1. Geltung und Zuständigkeit

- **Status:** bestätigte Produktausrichtung; konkrete Lieferung und Abnahme stehen im zuständigen Issue/PR.
- **Zuständig für:** Produktkern, Zielgruppe, Varianten, Progression, Wertung und ausdrücklich offene Produktentscheidungen.
- **Technischer Entwicklungsstand:** [Projektprofil](../PROJECT_PROFILE.md).
- **Visuelle Konzeption:** [Gestaltungskonzept](DESIGN_CONCEPT.md).
- **Konkrete Bedienung und Speicherung:** [Spielvertrag](../game/PROTOTYPE_P1.md).
- **Produktionsablauf:** [Authoring](../production/authoring/PUZZLE_AUTHORING.md); Bildnormen und technische Verträge werden dort nach Operation geroutet.
- **Leseregel:** Ein Vorschlag ist keine Anforderung; eine Anforderung ist kein Implementierungs- oder Abnahmenachweis. Diese Datei beauftragt keine zusätzlichen Pakete.

Die Produktgespräche vom 22.09.2026 und ihre bestätigten Folgeentscheidungen sind
in den folgenden Anforderungen konsolidiert. Historische Paketchronologien stehen
im [gebundenen Vorgänger](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/PRODUCT_DEFINITION.md).

## 2. Produktkern und Zielgruppe

Ein thematisch zusammenhängendes Nonogramm-Spiel für PC, dessen Hauptreiz in logischen Erkenntnissen und dem Bearbeiten größerer Bildrätselprojekte liegt. Eine präzise, komfortable Bedienung soll auch große Raster und mehrteilige Spielsitzungen angenehm machen. Anspruch entsteht aus dem Rätsel, nicht aus vermeidbarem Zählen, Fehlbedienung oder Orientierungsverlust.

Die Zielgruppe sind erfahrene Nonogramm-Spieler sowie interessierte Rätselspieler, die sich schnell einfinden. Die Spielerhilfe bietet vier direkt erreichbare Bereiche: Spielprinzip, farbige Rätsel, Bedienung und kurze freiwillige Lösungstipps. Feste passive Lehrbeispiele erklären vollständig bestimmte Linien, das Zusammenwirken von Zeile und Spalte, Überlappungen sowie Farbkontakt und Farbabstand. Sie verwenden die normalen Spielzeichen auf der rechten Buchseite. Menschen umfassend das Nonogramm-Lösen beizubringen, ist nicht der Schwerpunkt; umfangreiche Lernstrecken bleiben nachrangig ([HIL-1 / #500](https://github.com/venomenon328/picross/issues/500)).

Prioritäten des Spielerlebnisses:

1. Logische Erkenntnisse und das Bewältigen großer Projekte.
2. Erkennbare Motive und ihre befriedigende Enthüllung als wesentlicher Bestandteil der Belohnung.
3. Persönliche Entwicklung und Leistungsvergleich als Ergänzung, nicht als dominierender Spielzweck.

Groß und schwierig sind unterschiedliche Eigenschaften. Ein großes, flüssig lösbares Projekt und ein kleines, sehr kniffliges Rätsel dürfen beide ihren Platz haben. Ein neuartiger Regel-Twist ist keine Voraussetzung für ein eigenständiges Basisprodukt.

## 3. Rätselbestand und Qualitätsversprechen

### 3.1 Umfang und Größen

Für die erste Veröffentlichung sind einige Hundert vorab erstellte und kuratierte Rätsel ein angemessenes Wunschziel. Exakte Stückzahlen, das Verhältnis der Varianten und die Größenverteilung werden nach einer repräsentativen Testproduktion festgelegt, nicht bereits als zugesicherter Lieferumfang behandelt.

Reguläre Rätsel haben höchstens 50 Spalten und 50 Zeilen. Die verbindliche
[Vollsichtstrategie](../game/VS1_DECISION.md) bestimmt Zielkapazität, geeignete Rechtecke
und Darstellungsgrenzen. Kleine Rätsel sind zulässig; ein Format allein garantiert
keine Bedienbarkeit. 100×100 ist ausschließlich eine theoretische Stressgröße,
kein reguläres Inhaltsformat.

Ein größeres Rätsel darf sich über mehrere Sitzungen erstrecken. Die Bedienung und Fortschrittsspeicherung müssen diesen Nutzungsfall von Anfang an berücksichtigen.

Eigentümerauftrag vom 15.10.2026 / [#144](https://github.com/venomenon328/picross/issues/144):
Mehr als vier Vordergrundfarben werden unterstützt. Der aktuelle Zielvertrag
begrenzt sie auf acht plus Leer, passend zum Produktionskern. Farbwahl und
Rasterhinweise müssen alle unterstützten IDs unverändert zugänglich halten.
Die [aktuelle Rasterpflege](../tools/PUZZLE_EDITOR.md#9-raster-und-spielstandrevision) erlaubt ausdrücklich beauftragten Ersatz
eines Rasters unter gleicher ID und höherer Runtime-Revision; alte Spielstände
werden dabei nicht stillschweigend auf eine geänderte Definition übertragen.

### 3.2 Lösbarkeit und Schwierigkeit

- **MUSS:** eindeutig und vollständig deduktiv aus den regulären Randhinweisen lösbar sein, ohne notwendiges Raten oder versuchsweises Zurückspringen.
- **MUSS:** Deduktionsnachweis und Eindeutigkeitsdiagnose unterscheiden; Eindeutigkeit allein erfüllt das Lösbarkeitsversprechen nicht.
- **DARF:** über einzelne Linien hinausgehende zwingende Schlüsse verwenden. Zulässige Profile und unabhängige Prüfung stehen in [Produktion](../production/PUZZLE_PRODUCTION.md) und [Paarlinien](../production/PAIRED_LINES.md).
- **DARF NICHT:** zusätzliche redaktionelle Startfelder voraussetzen. Direkt aus Hinweisen ableitbare Felder sind keine solchen Vorgaben.

Die fachliche Schwierigkeitsdefinition gehört ausschließlich in
[SD2](../difficulty/PUZZLE_DIFFICULTY_V2.md), die aktive Methodenauswahl und Altkompatibilität in
[SD2-Integration](../difficulty/SD2_INTEGRATION.md). Die Beurteilung unterscheidet Denkanspruch,
Suchaufwand und Bearbeitungsumfang. Lösungszeit, Größe und zusätzliche Farben sind
keine pauschalen Belege hohen logischen Anspruchs. Die sichtbare Fünferskala
ist eine instrumentierte Modellschätzung, keine empirisch zugesicherte Lösungszeit.
Schwierigkeitseinstufung ändert weder Rätsellogik noch Sterne-/Progressionsregeln.

### 3.3 Motive und Abschlussansicht

- **MUSS:** ein tatsächliches Motiv darstellen; zufälliges Rauschen und reine abstrakte Formen gehören nicht in den regulären Katalog. Für die kleinsten Dimensionen wurden begründete Ausnahmen lediglich erwogen; ihre Kriterien sind weiterhin offen (§11, O-03). Daraus entsteht kein bereits freigegebener Ausnahmeweg.
- **MUSS:** als Belohnung das erarbeitete Motiv selbst zeigen. Das Verhältnis von Illustration, Motivvorlage und Lösungsraster sowie die unterschiedlichen Erkennbarkeitsmaßstäbe für Mono/Farbe stehen in den [Bildnormen](../production/images/README.md).
- **MUSS:** vor Abschluss Lösungsbild und Motivname verbergen. Die eigene Miniatur zeigt ausschließlich tatsächliche Spielereingaben einschließlich Fehlern; sie darf keine korrigierte Lösung vorwegnehmen.
- **MUSS:** Katalogvorschau und Abschluss aus derselben freigegebenen Bildquelle darstellen; die Anzeigegröße darf sich unterscheiden.

Abschlussbewegung, stabiler Endzustand und die Umschaltung **Bild | Raster** werden
im [Spielvertrag §5.4](../game/PROTOTYPE_P1.md#54-abschluss-und-detaillierteres-ergebnisbild)
definiert. Die [Katalogdarstellung](../game/CATALOG_PRESENTATION.md) besitzt die konkrete
Spoiler- und Vorschausemantik. Künstlerischer Bildstandard und technische
Bildrevision sind getrennte Quellen im Produktionsrouting; diese Produktdefinition
wiederholt ihre Einzelregeln nicht.

### 3.4 Inhaltsproduktion

Das Basisprodukt enthält eine vorab kuratierte Sammlung. Laufzeitgenerator,
Community-Nachschub und spielerseitiger Bildimport sind keine Voraussetzungen.
[Authoring](../production/authoring/PUZZLE_AUTHORING.md) ist die einzige Ablaufautorität für
neue Produktionen, Bildkorrekturen und Wiederaufnahme. [Qualität](../production/PUZZLE_QUALITY.md)
definiert redaktionelle Kriterien, Urteile und zulässige Abweichungen;
[Produktion](../production/PUZZLE_PRODUCTION.md) die technischen Raster-/Proofgarantien.
Ein generiertes Bild ist noch kein geeignetes oder freigegebenes Rätsel.

**Produktgrenze KI:** Modellnutzung erfolgt ausschließlich in ChatGPT oder Codex.
Das lokale Produktionswerkzeug besitzt keine direkte Modell-API-Anbindung,
benötigt keine Modell-API-Keys und startet keine automatischen Modellaufrufe.
Reproduzierbare Verarbeitung beginnt bei den tatsächlich gespeicherten
Eingabedateien; ein Prompt ersetzt keine Bildquelle.

Ausbeute, Kurationsaufwand und konkrete Quellenrechte bleiben anhand realer
Produktionen zu beurteilen. Ein DLC oder spielerseitige Generierung sind
unentschiedene Erweiterungsmöglichkeiten.

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

- **MUSS:** präzise, intuitive Bearbeitung, Unterbrechung und Fortsetzung auch über mehrere Sitzungen unterstützen. Anspruch entsteht aus dem Rätsel, nicht aus vermeidbarem Orientierungsverlust.
- **MUSS:** reguläre Darstellung nach [Vollsichtstrategie](../game/VS1_DECISION.md) und [Spielvertrag](../game/PROTOTYPE_P1.md) ausführen. Fenstergröße, UI-Skalierung und Rasterzoom sind verschiedene Größen.
- **MUSS:** Maus und Tastatur als primäre Produktausrichtung sowie Controller als geplante alternative Eingabe berücksichtigen. Der tatsächlich verpflichtende Entwicklungs-Eingabepfad steht im Projektprofil; daraus folgt keine bereits gelieferte Controllersteuerung.
- **MUSS:** komfortables Undo/Redo ermöglichen. Die Auswirkung auf Perfektion gehört ausschließlich in §6.2.

| Konkrete Regel | Einzige Fachautorität |
| --- | --- |
| Achsenbindung, Zellgesten, Umwandlung, History, Speicherung | [P1](../game/PROTOTYPE_P1.md) |
| Strichzähler, Raster-/Fensterränder | [CELL_DRAG](../game/CELL_DRAG.md) |
| Hinweiszugriff und Cursororientierung | [CLUE_INTERACTION](../game/CLUE_INTERACTION.md) |
| Lösungsunabhängige Erfüllungsmarkierung | [CLUE_STATUS](../game/CLUE_STATUS.md) und dort bezeichnete P1-Logik |
| Vorschau, Markierungen, Zellanimation | [UI_DRAWING_STYLE](../game/UI_DRAWING_STYLE.md) |
| Fenster- und Vollbildoptionen | [DISPLAY_SETTINGS](../game/DISPLAY_SETTINGS.md) |

Hypothesen sind weiterhin eine unentschiedene Zusatzfunktion. Sie verändern
weder das deduktive Lösbarkeitsversprechen noch automatisch die Wertung.

### 5.2 Visuelle Identität

Das [Gestaltungskonzept](DESIGN_CONCEPT.md) besitzt die bestätigte Albumrichtung,
Atmosphäre und die offenen Themenalternativen. Die konkrete Buchdarstellung
folgt [BOOK_INTEGRATION](../game/BOOK_INTEGRATION.md); Fonts, Controls, Katalog und
Bildproduktion besitzen jeweils eigene Fachverträge. Visuelle Erprobung und
funktionale Entwicklung erfolgen gemeinsam; ein Mock ist keine Bedienabnahme.

Sound ist nachrangig. Kleine unauffällige Effekte und ein guter Erfolgsjingle
sind gewünscht, zurückhaltende Hintergrundmusik ist denkbar. Eine konkrete
Audioproduktion ist nicht beauftragt.

### 5.3 Persönliche Referenzen aus dem Produktgespräch

Dies sind vom Nutzer benannte Erfahrungen und Vorbilder, keine recherchierte Marktanalyse:

- Mario's Picross (Game Boy) und Mario's Super Picross (SNES): positive Referenzen für Präsentation und Progression. Insbesondere die kolorierte Auflösung abstrahierter monochromer Motive dient als Anschauung für das gewünschte Erlebnis.
- Griddlers (PC): Erfahrung mit sehr großen und farbigen Rätseln. Trotz Zoom kam es beim Scrollen großer Raster zu Orientierungsverlust; genau diese Schwäche soll das eigene Bedienkonzept vermeiden.
- Squeakross (Screenshotvergleich vom 07.10.2026): veranschaulicht den gewünschten Grad einer charaktervollen Spieloberfläche. Ausdrücklich keine Vorlage für das eigene UI, seine Anordnung oder seine Assets; die eigene Buchrichtung bleibt Grundlage.

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

Optionale Spielerkonten und gemeinsame Spielstände zwischen Web und mehreren
Windowsgeräten sind als [SYNC-Spezifikation](../game/SAVE_SYNC.md) freigegeben.
Ohne Konto bleibt die bisherige lokale Speicherung getrennt. Ein Kontoprofil
arbeitet ebenfalls offline und synchronisiert vollständige Spielstände später;
Gastübernahme, Konfliktentscheidung und Wiederherstellung sind ausdrücklich.
Der eigene Konto-/Speicherdienst wird vor der Clientanbindung und dem separat
beauftragten Livebetrieb geliefert. Diese Entscheidung behauptet keine bereits
implementierte Synchronisierung und führt keine neue Wertung, Rangliste oder
dauerhafte „jemals gelöst“-Statistik ein. Lieferstatus: [#821](https://github.com/venomenon328/picross/issues/821).

Ein plausibles Prüf- und Übertragungsmodell ist zu spezifizieren. Es wird kein manipulationssicherer Wettkampf und keine nachweisbare Verhinderung externer Lösungshilfen versprochen. Online-Ranglisten ergänzen das Spiel, bestimmen aber nicht seinen Hauptzweck.

## 8. Entwicklungs- und Veröffentlichungsrahmen

Das Projekt wird als Solo-Entwicklung mit dem mittelfristigen Ziel einer kommerziellen Veröffentlichung und späterer Erweiterung geplant. Unterstützung durch befreundete Designer wird für Grafiken in Betracht gezogen. Umfang, Budget, Zeitplan und konkrete Zusammenarbeit sind noch nicht festgelegt. Sound hat vorerst geringere Priorität.

PC ist die beschlossene Produktzielrichtung. Die aktuelle Entwicklungsbindung für Engine, Sprache, Windows/Web, Datenhaltung und Prüfwege steht im [Projektprofil](../PROJECT_PROFILE.md); eine abschließende Veröffentlichungsplattformmatrix folgt daraus nicht. Steam ist ein angestrebter beziehungsweise naheliegender Veröffentlichungskontext, aber keine bereits eingerichtete oder abschließend spezifizierte Integration. Preis, Lizenzierung und ein konkretes Erweiterungsmodell sind nicht beschlossen.

Konkrete neue Implementierungen folgen ihren Fachverträgen und dem aktuellen Issue-/PR-Umfang. Dokumentprüfung allein belegt kein Produktverhalten.

## 9. Abgrenzung des ersten Produkts

Zum Produktkern gehören klassische und farbige kuratierte Bildrätsel, das reguläre Vollsichtziel mit 40×40 und mindestens 30×30 Größenkapazität, geeigneten Rechtecken und möglichen Großraster-Sonderfällen, komfortable Bearbeitung und Fortsetzung, die vierteilige Grundhilfe mit festen Lehrbeispielen und kurzen optionalen Strategien, frühe thematische/UI-Konzeption, Sammlungsprogression, Perfektions-Bonusrätsel, die beiden Fehler-Rückmeldungsmodi sowie Logbuch und vorgesehene Leistungsvergleiche.

Nicht als Startvoraussetzung beschlossen sind Verbundraster, Regionenbedingungen, Raster jenseits von 50×50, ein öffentlicher Editor, Community-/Workshop-Inhalte, Koop, spielerseitige Bildgenerierung, Wochenherausforderungen und umfangreiche Lern- oder Erklärhilfen. Diese Themen dürfen nicht stillschweigend den verbindlichen Umfang vergrößern. Unvollständige Hinweise sind vorerst ausgeschlossen.

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
| Qualitätssicherung | Linien- und Paarlinienprofil samt unabhängigen Nachweisen sind in [Rätselproduktion](../production/PUZZLE_PRODUCTION.md) spezifiziert. Separate Eindeutigkeitsdiagnose ersetzt keinen Deduktionsnachweis. Weitere Profile, Spielerhilfe und menschliche Kalibrierung bleiben Folgearbeit. |
| Sterne | Ein Stern für Abschluss und zwei bei begrenzten Fehlern bleiben Vorschläge ohne feste Schwellen. Für die Höchstwertung gilt bereits: ohne Fehler und ohne Undo; Hypothesenfrage offen. |
| Wiederholungen | Beste Bewertung je Rätsel für Fortschritt verwenden; Sterne nicht durch wiederholtes Lösen aufsummieren und bestehende Freischaltungen nicht durch schlechtere Ergebnisse verlieren. |
| Fehlerbehandlung | Keine Leben, erzwungenen Abbrüche oder Strafsekunden; fehlerhafte Aktionen und betroffene Felder gegebenenfalls getrennt erfassen. |
| Zeitmessung | Explizite Pausen und Sitzungswechsel definieren, Denkzeit nicht durch bloße Inaktivität herausrechnen; Erstlösungen und Wiederholungen unterscheiden. |
| Spätere Erweiterungen | Erklärende Hilfen, Technik-Übungsstrecken, öffentlicher Editor mit Prüfung, Community-Inhalte und Koop wurden diskutiert, aber nicht für das Basisprodukt zugesagt. |

## 11. Offene Entscheidungen für die weitere Spezifikation

| Kennung | Offene Entscheidung |
| --- | --- |
| O-01 | Wahl zwischen thematischem Sammelalbum und Reisealbum; konkrete Kapitel, Layouts, Designsystem und Enthüllungsdetails auf Basis der bestätigten Album-/Illustrationsrichtung. |
| O-02 | Die bestehenden Deduktionsprofile und die aktive [Schwierigkeitsmethode](../difficulty/SD2_INTEGRATION.md) sind festgelegt. Darüber hinausgehende Profile und empirische menschliche Kalibrierung bleiben offen; daraus entsteht kein neues Gate für bestehende Methoden. |
| O-03 | Exakte Startmenge, Größen- und Variantenverteilung; Auswahlkriterien und zulässige Ausnahmen bei winzigen Motiven. |
| O-04 | Dateibasierte Produktion mit KI ausschließlich in ChatGPT/Codex, ohne direkte Modell-API, und die erste Vergleichs-/Pilotphase sind spezifiziert. Offen bleiben die nachzuweisende Ausbeute, der reale Kurationsaufwand, Rechte konkreter Quellen und weitere ausdrücklich beauftragte Erweiterungen der bestehenden [Produktionsoberfläche](../tools/PRODUCTION_WORKSPACE.md). |
| O-05 | Was als Fehler zählt; Behandlung falscher Leer-/Farbmarkierungen, Striche und Wiederholungen; Abgrenzung manueller Korrekturen zu Undo und mögliche Hypothesen. |
| O-06 | Skala/Fehlertoleranzen unterhalb der Höchstwertung, Bestbewertungen und Wiederholungen, Wechsel zwischen Unterstützungsmodi; Vereinbarkeit von Hypothesen mit der bestätigten Perfektionsregel ohne Fehler und ohne Undo. |
| O-07 | Aufbau und frühe Zugänge der Sammlungen, konkrete Freischaltschwellen, Abhängigkeiten und Umfang der Bonusinhalte. |
| O-08 | Belohnungen nach perfekter Lösung der Bonusrätsel, Achievement-Katalog und gegebenenfalls weitere Abschlussinszenierung. |
| O-09 | Zusätzliche Tastatur-/Controllerbedienung und über den aktuellen [Spielvertrag](../game/PROTOTYPE_P1.md) hinausgehende Komfortfunktionen. Bereits konkretisierte Maus-, Hinweis-, Ansichts- und Saveverträge bleiben entschieden. |
| O-10 | Zeitmessung und Pausen, Erst-/Wiederholungslösungen, Ranglistenmetriken, Offline-Upload und Ergebnisprüfung. |
| O-11 | Abschließende Veröffentlichungsplattformen und künftige technische Erweiterungen. Aktuelle Engine, Sprache, Persistenz, Datenformen und Prüfstrategie sind im [Projektprofil](../PROJECT_PROFILE.md) und seinen Fachverträgen gebunden. |
| O-12 | Veröffentlichungskanal und Integration, Preis, Lizenz-/Erweiterungsmodell, Budget und Umfang externer Unterstützung. |
| O-13 | Ergebnis der Verbundraster-Erprobung; gegebenenfalls spätere Entscheidung über Regionenbedingungen. |

Diese offenen Punkte verhindern nicht die Arbeit an unabhängigen Konzepten. Sie sind jedoch vor einer davon abhängigen Implementierung gezielt zu entscheiden. Die bereits bestätigten Antworten werden dabei nicht unnötig erneut zur Disposition gestellt.
