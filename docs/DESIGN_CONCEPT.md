# Gestaltungskonzept: Album, Rätselarbeit und Enthüllung

Stand: 22.09.2026 · Arbeitsfassung 0.1 · frühe Konzeption, keine umsetzungsreife UI-Spezifikation

## 1. Geltung und Entscheidungsstand

Dieses Dokument überträgt die Gestaltungskonversation zu Punkt 2 des Entwicklungsablaufs in die Repositoryquellen. Die [Produktdefinition](PRODUCT_DEFINITION.md) bleibt für Produktkern, Rätselregeln, Progression und Wertung maßgeblich; hier stehen die visuelle Konkretisierung und ausdrücklich noch offene Entwurfsfragen. Prüfwege und Befugnisse stehen im [Projektprofil](PROJECT_PROFILE.md).

Die ausdrücklichen Antworten des Nutzers begründen die bestätigten Entscheidungen in Abschnitt 2. Die anschließende Rückmeldung „Sieht gut aus“ zu den exemplarischen Mocks bestätigt deren grundsätzliche gestalterische Richtung, nicht jeden Bildinhalt, jede Zahl, jedes Werkzeug oder eine fertig geprüfte Bedienung. Abschnitt 3 erhält die nicht entschiedenen Themenalternativen. Abschnitte 4–5 enthalten Entwurfsansätze, nicht stillschweigend zusätzliche Anforderungen.

Es wurde kein endgültiges Thema, kein vollständiges Designsystem und kein Produktstack ausgewählt. Dieses Dokument ist weder eine Implementierungsfreigabe noch ein Nachweis abgeschlossener UX-Konzeption. Der explizite Auftrag zur Dokumentation und zum Merge ist im zugehörigen PR festzuhalten.

## 2. Bestätigte gestalterische Grundlage

| Bereich | Bestätigte Entscheidung |
| --- | --- |
| Sammlung | Bevorzugt ein Album, das sich mit erarbeiteten Bildern füllt und am Ende einen erkennbar vollständigen Zustand erreichen kann. Eine zusätzliche Raumansicht ist nicht erforderlich beschlossen. |
| Zeichenstil | Handgezeichnete 2D-Illustration; klare gezeichnete Konturen mit ruhigen, nicht zu blassen Farbflächen. Nicht automatisch Retro-Pixel-Art für die ganze Oberfläche. |
| Stimmung | Warm, neugierig und dennoch ruhig. |
| Spielbildschirm | Die Thematik bleibt zurückhaltend, aber sichtbar. Das Spiel soll auch beim Rätseln nicht steril oder seelenlos wirken; das eigentliche Raster bleibt sachlich und präzise. |
| Sammelbilder | Die gelösten Bilder selbst bilden die Sammlung. Bei monochromen Rätseln eine farbige Repräsentation des tatsächlichen Motivs, gegebenenfalls etwas höher aufgelöst, aber eindeutig dem Rastermotiv zuzuordnen. |
| Perfektion | Ein perfekter Durchgang ist ohne Fehler und ohne Undo. Die frühere ausschließlich fehlerbasierte Beschreibung wird für die Höchstwertung ergänzt; Details stehen in der Produktdefinition, Abschnitt 6.2. |
| Hypothesen | Als Möglichkeit diskutiert, nicht abschließend entschieden. Insbesondere bleibt offen, ob sie auch bei perfekten Lösungen zulässig sind. |
| Audio | Später behandeln. Kleine, angenehme und unauffällige Effekte sowie ein besonders guter Erfolgsjingle sind gewünscht; zurückhaltende Hintergrundmusik ist denkbar. |

Der Nutzer arbeitet selbst überwiegend mit sicheren Schlüssen, nicht mit versuchsweisem Setzen und Zurückspringen. Hypothesen sind daher eine mögliche Zusatzfunktion, keine notwendige Spielweise. Unverändert müssen Rätsel ohne notwendiges Raten lösbar sein.

## 3. Zwei offene Themenalternativen

### A: Thematisches Sammelalbum

Sammlungen können Themen wie Erfindungen, Tiere, Personenporträts oder stilisierte Filmposter behandeln. Das Album verbindet unterschiedliche Motivgruppen durch eine gemeinsame Präsentation und Zeichenweise. Diese Beispiele sind mögliche Inhalte, kein bestätigter Rätselkatalog und keine Assetfreigabe.

Der Nutzer hält eine sinnvolle Progression in A zunächst für leichter vorstellbar, hat A aber nicht ausgewählt. Denkbare Inszenierungen wie Bilderkabinett, Atelier oder Archiv sind Ausgestaltungsideen; eine zusätzliche begehbare Ausstellung oder Dekorationsmechanik folgt daraus nicht.

### B: Reisetagebuch beziehungsweise Weltreisealbum

Regionale Kapitel können Tiere, Gerichte, Sehenswürdigkeiten, Pflanzen und weitere Motive der jeweiligen Region verbinden. Die Weltreise ist eine reale regionale Themenidee, keine Festlegung auf eine fantastische Welt.

Ein möglicher Ansatz sind mehrere früh zugängliche Reisekapitel statt einer starren geografischen Route. Eine klar begrenzte Auswahl vervollständigbarer Kapitel ist denkbar; weder eine vollständige Abdeckung aller Länder noch konkrete Regionen oder Kapitelmengen wurden beschlossen. Die bestehenden Anforderungen an früh zugängliche große und anspruchsvolle Rätsel gelten auch für B.

### Gemeinsamer Vergleich

A und B bleiben bis zu einer ausdrücklichen Richtungsentscheidung parallel untersuchbar. Keine erzwungene Mischform. Das Album und der sachliche Arbeitsbereich können beiden dienen; ihre Atmosphäre und Kapitelorganisation unterscheiden sich.

Als Vergleichsaufgabe wurde dasselbe angearbeitete 40×40-Farbrätsel mit vier Farben vorgeschlagen: identische Hinweise, eigener Bearbeitungsstand, Miniatur, Werkzeuge und Informationsumfang. Dazu jeweils eine Albumansicht und derselbe Abschlussmoment. Das ist ein Entwurfsmaßstab, kein bereits gelieferter mathematisch identischer oder spielbarer Vergleich.

## 4. Visuelle Ausarbeitung: Vorschläge für die nächste Erprobung

### 4.1 Album und Arbeitsansicht

Ein möglicher Albumaufbau sind redaktionell komponierte Doppelseiten mit Registern, Kapitelverzierungen und unterschiedlich großen Bildplätzen. Große Panoramen könnten eigene Seiten erhalten. Fest angeordnete Seiten statt einer zusätzlichen freien Dekorationsfunktion sind ein Vorschlag, keine neue Spielmechanik.

Beim Öffnen eines Rätsels könnte dessen Blatt zur großzügigen Arbeitsfläche werden. Konturen, Materialanmutung und Kapitelakzente bleiben, während Hinweise und Raster ausreichend Raum erhalten. Die Buchmetapher soll insbesondere große Raster nicht in eine halbe Seite oder über einen störenden Buchfalz zwingen. Konkrete Perspektive, Ränder und Übergänge sind noch zu prüfen.

Leicht gebrochenes Papierweiß, dunkle Konturen, matte Akzente und dezente Materialtexturen sind mögliche Stilmittel, keine festgelegte Farbpalette. Zahlen, Linien und Zellzustände benötigen eine klare, unverzerrte Darstellung. Handschriftliche Ziffern, Flecken oder dekorative Gegenstände dürfen die Arbeit nicht erschweren. Handgezeichnet bedeutet weder verpflichtend beige noch absichtlich unpräzise.

Für die Großrasteransicht ist ein verdichteter Rahmen mit kompakteren Werkzeugen denkbar. Er soll die Identität bewahren, ohne wichtige Arbeitsfläche zu belegen. Konkrete Schriftgrößen, Abstände, Kontraste, Skalierung und Controllerfokus sind noch nicht als Designsystem definiert.

### 4.2 Bildplätze und Vollständigkeit

Ungelöste Plätze benötigen neutrale Kennungen statt vorweggenommener Motivnamen oder verräterischer Skizzen. Angefangene Rätsel könnten den eigenen Zwischenstand zeigen. Die bindende Spoilergrenze und Miniaturregel stehen in der Produktdefinition, Abschnitt 3.3.

Vorgeschlagen ist eine Unterscheidung zwischen vollständiger Grundsammlung und zusätzlicher Meisterschaft: jedes gelöste Rätsel liefert sein vollständiges Bild, unabhängig von der Bewertung; perfekte Leistungen erhalten zusätzliche Kennzeichnungen. Bonusinhalte könnten als Zusatzblätter erscheinen statt als dauerhafte Löcher in der Grundsammlung. Konkrete Zustandsbezeichnungen und Bonusplatzierung sind noch nicht beschlossen. Die bestätigten Perfektions-Bonusrätsel dürfen dadurch nicht durch rein kosmetische Belohnungen ersetzt werden.

### 4.3 Motivtreue Enthüllung

Als Ausarbeitung der bestätigten Motivtreue werden gleicher Bildaufbau, wesentliche Formen und nachvollziehbare Proportionen vorgeschlagen. Farbe und feinere Details können die Abstraktion auflösen; ein beliebiges neues Bild oder ein vollständig anderer Blickwinkel wäre kein Ersatz für die erarbeitete Lösung.

Ein möglicher Ablauf: Hinweise, Leermarkierungen und Rasterlinien treten zurück; das gelöste Motiv bleibt zunächst sichtbar; daraus entsteht die farbige Fassung; anschließend erscheinen Name und Bewertung und das Bild erhält seinen Albumeintrag. Bei Farbrätseln kann Freistellung und Präsentation genügen. Weder eine feste Animationsfolge noch eine höher aufgelöste Neuzeichnung für jedes Motiv sind beschlossen.

Eine umschaltbare Ansicht des ursprünglichen Lösungsrasters im Albumeintrag sowie überspringbare oder reduzierte Animationen sind sinnvolle Entwurfsvorschläge, keine bereits implementierten Funktionen.

## 5. Bedienung und Wertung: zu untersuchende Details

### 5.1 Präzise Eingaben und Orientierung

Die bereits bestätigte Achsenbindung eines Mausstrichs ab dem zweiten Feld bleibt verbindlich; sie wird nicht durch den früheren Vorschlag eines nur optionalen Standards ersetzt. Maus/Tastatur sind primär, Controller werden von Beginn an berücksichtigt. Sonstige Belegungen sind nicht durch das Mock festgelegt.

Vorgeschlagen sind eine feste Aktion je Ziehvorgang, ein Undo-Schritt je zusammenhängendem Strich, ein Längenzähler sowie ein echter Zellcursor für Tastatur/Controller. Verhalten bei Rückwärtsbewegung, diagonaler Bewegung, bestehenden Markierungen und Abbruch muss vor betroffener Umsetzung konkretisiert werden.

Für große Raster sind fixierte vollständige Zeilen-/Spaltenhinweise, eine aktive Linienhervorhebung, ein besonderer Fokus für lange Hinweisfolgen und eine interaktive Miniatur mit Ausschnittrahmen zu prüfen. Hinweise beziehen sich weiterhin auf ganze Linien, nicht nur auf den sichtbaren Ausschnitt. Die Miniatur zeigt den eigenen Stand einschließlich Fehlern, niemals eine korrigierte Lösung. Zoomen am Mauszeiger, Hand-Werkzeug und Lesezeichen sind Vorschläge. Speichern von Ausschnitt, Zoom, aktiver Farbe, Notizen und Undo-Verlauf ist ebenfalls noch im Detail zu entscheiden.

Rätselfarben und UI-Zustandsfarben sollen in den Entwürfen unterscheidbar sein. Ergänzende Farbsymbole oder Muster, unabhängige UI-/Raster-Skalierung und zugängliche Eingabealternativen sind zu erproben. Automatisches Abblenden von Hinweisen darf keine verdeckte Prüfung gegen die hinterlegte Lösung sein.

### 5.2 Undo und Hypothesen

Beschlossen ist der Ausschluss von Perfektion durch Undo, nicht die Abschaffung von Undo. Fehlerzahl und Rücknahmen getrennt zu erfassen ist ein Vorschlag; feste Abzüge und die Bewertung unterhalb der Höchstwertung sind offen.

Offen bleibt die zuletzt gestellte Frage, ob manuelles Löschen, Zurücksetzen auf „unbekannt“ oder Überschreiben verbindlicher Einträge ebenfalls als wertungsrelevante Rücknahme gelten. Die Empfehlung, solche Aktionen wie Undo zu behandeln, wurde noch nicht bestätigt. Auch Undo-Aufrufe ohne Wirkung, Abbruch eines noch laufenden Strichs, Neustart und reine Notizkorrekturen sind abzugrenzen.

Eine einmalige abschaltbare Bestätigung vor dem ersten wertungsrelevanten Undo ist ein Entwurfsvorschlag. Sie müsste unabhängig von bereits unbemerkt gemachten Fehlern erscheinen; sonst würde ihr Auftreten im Standardmodus verdeckte Fehlerhinweise liefern. Es ist keine Anzeige „bisher fehlerfrei“ während eines Standarddurchgangs vorgesehen.

Eine separate Notizebene für „unsicher gesetzt“ und „unsicher leer“ ist ein Untersuchungsansatz. Bei Farbrätseln müsste eine vermutete Farbe zugeordnet werden können. Vorläufige Einträge sollten mehr als nur eine schwächere Deckkraft unterscheiden; ihre Darstellung in der Miniatur ist mitzudenken.

Vorgeschlagen sind ausdrückliches Übernehmen beziehungsweise Verwerfen und keine Richtig-/Falsch-Prüfung von Notizen, auch nicht im unterstützten Modus. Notizen würden in diesem Ansatz nicht selbst als fertige Lösung gelten. Aufnahme dieser Funktion, ihre Grenzen und ihre Vereinbarkeit mit Perfektion sind noch nicht entschieden. Wer Annahmen in unbewerteten Notizen ausprobieren darf, kann bewusst eine andere Spielweise nutzen; diese Konsequenz ist vor einer Wertungsentscheidung offenzulegen.

### 5.3 Verbundraster

Als frühe Arbeitshypothese wurden zwei Raster mit tatsächlich gemeinsamen Zellen diskutiert: aktives Raster mit klar zugehörigen Hinweisen, gemeinsamer Bereich mit eindeutiger Umrandung und Kennzeichnung, anderes Raster zurückgenommen. Gemeinsame Felder nicht durch einen irreführenden Rätselfarb-Hintergrund markieren und keine zwei unlesbaren Zahlenteppiche überlagern.

Diese Darstellung und Geometrie sind nicht beschlossen. Der begrenzte Verbundraster-Prototyp muss echte logische Abhängigkeiten und verständliche Hinweiszuordnung nachweisen; ein Mosaik aus unabhängigen Einzelrätseln genügt nicht. Verbundraster bleiben eine Evaluation, keine Startvoraussetzung und kein tragendes Versprechen der gewählten Thematik.

## 6. Exemplarische Mocks und Grenzen ihrer Aussage

Referenz M-01 ist der im Gespräch vom 22.09.2026 generierte Vergleich mit den Überschriften „Thematisches Sammelalbum – Beispiel: Erfindungen“ und „Reisetagebuch – Beispiel: Japan“. Er enthält Albumansichten, Rätselbildschirme, Abschlussdarstellungen sowie Details zu Werkzeugen, Miniatur, Undo-Bestätigung und Albumeintrag. Der Nutzer bewertete die Richtung positiv. Die Bilddatei ist nicht Bestandteil dieses Dokumentationspakets; die hier übertragene textliche Einordnung vermeidet eine Abhängigkeit von einem nur im Chat erreichbaren Bild.

M-01 ist eine illustrative Stilreferenz, keine Bildschirm-für-Bildschirm-Spezifikation, kein freigegebener Rätseldatensatz und kein finales Assetpaket. Beispiele, Motive, Schriften, Papier-/Holzdetails, Texte und Beispielwerte sind nicht automatisch beschlossen. A/B wurden dadurch nicht entschieden.

Insbesondere nicht wörtlich aus M-01 übernehmen:

- Fertige Motivvorschauen während eines noch ungelösten Rätsels und erkennbare Motivskizzen in noch offenen Albumplätzen widersprechen der Spoilergrenze. Dort sind nur eigener Arbeitsstand beziehungsweise neutrale Platzhalter zulässig.
- Unterschiedliche beziehungsweise zu viele Sternsymbole und erfundene Beispielwerte begründen keine neue Skala, Schwelle oder Statistik. Die beschlossene Perfektionsbedingung bleibt ohne Fehler und ohne Undo; die Hypothesenfrage bleibt offen.
- Schematische Zahlen, Rastergrößen und nicht nachgewiesen identische Spielstände sind keine Belege mathematisch gültiger oder deduktiv lösbarer Rätsel. Der Wechsel zwischen Farb-Arbeitsansicht und monochromer Enthüllungsdarstellung ist kein geprüfter zusammenhängender Spielablauf.
- Stark ausgearbeitete Abschlussillustrationen dürfen die bestätigte Wiedererkennbarkeit des erarbeiteten Rastermotivs nicht ersetzen.

Es liegen keine praktischen Nachweise für Zoom, lange Hinweisfolgen, sehr große Raster, Controllerbedienung, Persistenz oder Verbundraster vor. Auch die Dokumentations-CI weist diese Eigenschaften nicht nach.

## 7. Offene Entscheidungen und empfohlener nächster Untersuchungsschritt

| Thema | Noch zu entscheiden oder nachzuweisen |
| --- | --- |
| Themenwahl | A oder B; konkrete Kapitel und Motivzusammenhang, ohne bestehende Progressionsanforderungen neu zu öffnen. |
| Album und Designsystem | Seitenkomposition, Bibliothekszugang, Raster-/Werkzeuglayout, Typografie, Farben, Skalierung, Fokus-/Zellzustände und Enthüllungsdetails. |
| Korrekturen und Bewertung | Manuelle Korrekturen gegenüber Undo, Aktionsgrenzen, Fehlerzählung, niedrigere Sternstufen, Wiederholungen und mögliche Hypothesen. |
| Eingabe und Wiedereinstieg | Strichverhalten, Navigation, lange Hinweise, Farbwahl, beide Eingabeformen und genauer gespeicherter Arbeitszustand. |
| Prototyptechnik und Prüfung | Bewusst begrenzter technischer Weg, Start-/Testanleitung, Testdaten und konkrete manuelle Erfolgskriterien; keine Engine-/Plattformentscheidung aus dem Dokumentsetup ableiten. |

Empfehlung, keine bereits beauftragte Umsetzung: Gestaltung und Risikoprototypen nun überlappen lassen. Die gemeinsame visuelle Richtung reicht, um die kritische Arbeitsansicht interaktiv zu untersuchen; das vollständige UI-Konzept ist damit nicht abgeschlossen. Noch mehr statische Mocks allein beantworten die Bedienungsfragen nicht.

Als erster enger Schnitt bietet sich ein Großraster-/Bedienprototyp an: wenige repräsentative klassische und farbige Testfälle, etwa ein kleineres monochromes Rätsel, ein 40×40-Farbrätsel mit vier Farben und ein 100×100-Ausschnitt mit langen Hinweisfolgen. Zu prüfen sind präzises Setzen/Leermarkieren mit Achsenbindung, Zuordnung vollständiger Hinweise, Miniatur und Zoom/Navigation, Farbwahl, Undo sowie Unterbrechen und Wiederaufnahme des Arbeitsstands. Ein einfacher Album-/Arbeitsansicht-Wechsel kann die gemeinsame visuelle Grundlage erlebbar machen. Keine vollständige Progression, Inhaltsbibliothek oder Audioarbeit in diesen Untersuchungsschnitt hineinziehen.

Vor einer Implementierung sind Umfang, Prototyptechnik, offene unmittelbar betroffene Eingaberegeln sowie automatisierte und manuelle Nachweise in einem beauftragten Paket festzulegen. Bewertungsdetails können nur dann außen vor bleiben, wenn der Prototyp ausdrücklich keine abschließende Wertung implementiert. A/B, Sound und vollständige Bonusprogression müssen den reinen Bedienversuch nicht blockieren. Der Nutzer prüft die tatsächliche Benutzbarkeit am benannten Stand; Mess-/Prüfergebnisse werden im Paket festgehalten.

Rätselproduktion und Deduktionsnachweis bilden einen eigenen frühen Risikostrang. UI-Testdaten sind nicht allein wegen eines hübschen Bildes als kuratierte Rätsel freigegeben. Die begrenzte Verbundraster-Evaluation bleibt separat prüfbar, statt den ersten Eingabeprototyp zu überladen. Danach werden Thema, Designsystem und zentrale Ansichten anhand der Erfahrungen geschärft, bevor die kleine vollständige Fassung und umfangreiche Inhaltsproduktion folgen.
