# SD2: Fachliche Bewertung mit Methode 0.4

- Dokument-ID: `SD2`.
- Status: aktive Methode `picross-difficulty-0.4`.
- Dokumentstand: 17.11.2026; fachlicher Methodenvertrag unverändert 1.0.
- Zuständigkeit: Bedeutung und Anforderungen der drei Bewertungsprofile.
- Normsprache: MUSS ist verpflichtend; DARF NICHT ist ein Verbot; DARF erlaubt eine Option.

## 1. Geltung und Abgrenzung zur Methode 0.3

Der gültige [Defaultrecord](../../content/difficulty-method.json) wählt 0.4 für
neue Produktion. Die historische Methode 0.3 bleibt mit ihren exakten Regeln,
Referenzen, Formeln, Hashes und unterstützten Datenformen lesbar. Die Methoden
werden nicht ineinander umetikettiert. Aktivierung, explizite Methodenwahl und
Readergrenzen stehen in [SD2-Integration](SD2_INTEGRATION.md).

0.4 unterscheidet gewöhnliche eingeschränkte Überlappungen und eindeutige
Verlängerungen von tatsächlich kombinierten Bedingungen. Denkanspruch,
Suchaufwand und Bearbeitungsumfang werden getrennt gemessen. Damit ersetzt sie
für 0.4 die konkrete 0.3-Technik-/Flusszuordnung, nicht deren historische
Bedeutung. [SD](PUZZLE_DIFFICULTY.md) definiert die gemeinsamen Grenzen für
Deduktion, Umfang, Versionierung, Auftrag, Fehlerbehandlung und Tests.

Die damalige Bestandsbeobachtung und Aktivierungsabfolge sind im
[festen historischen Stand](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/PUZZLE_DIFFICULTY_V2.md)
erhalten. Beobachtete Verteilungen sind weder Sollhistogramm noch Testkorpus.

## 2. Bedeutung der Bewertung

Die sichtbare Stufe beschreibt den modellierten menschlichen Lösungsanspruch.
**Denkanspruch, Suchaufwand und Bearbeitungsumfang** werden intern getrennt
begründet und zu einer Stufe zusammengeführt. Denkanspruch dominiert; Suche
und Umfang tragen nachvollziehbar bei. Eine fünfmal längere Bearbeitung ist
nicht automatisch fünfmal schwieriger. CPU-Zeit ist kein Bewertungsmerkmal.

| Stufe | Fachliche Orientierung für 0.4 |
| --- | --- |
| 1 · Sehr leicht | Durchgehend unmittelbar verständlicher, flüssiger Fortschritt; auch große direkte Fälle. |
| 2 · Leicht | Übliche einfache Techniken einschließlich sicher eingeschränkter Überlappungen und eindeutiger Verlängerungen; gut auffindbarer regelmäßiger Fortschritt. |
| 3 · Mittel | Wiederholt Informationen kombinieren und/oder deutlich erhöhte Suche nach tragfähigem Fortschritt, ohne anhaltend hohen Gesamtanspruch. |
| 4 · Schwer | Anspruchsvolle Kombinationen, erheblicher Suchaufwand oder wiederkehrende relevante Engstellen bei entsprechendem logischem Profil. |
| 5 · Sehr schwer | Sehr anspruchsvolle reine Linienlogik mit ausgeprägten Anforderungen oder separat nachgewiesene notwendige Paarlinienlogik. |

Die exakte Zuordnung erfolgt allein durch [SD2-Kalibrierung §5](SD2_CALIBRATION.md#5-exakter-zahlenvertrag-sd2-rating-formula-1).
Die Methode führt keine zusätzliche UI-Achse, Zeitprognose, Scoreanzeige,
Sortierart, Sterne- oder Progressionsänderung ein. Darstellung bleibt bei der
[Katalogdarstellung](../game/CATALOG_PRESENTATION.md), Spielverhalten bei
[P1](../game/PROTOTYPE_P1.md).

## 3. SD2-D01 · Menschennähere einfache Regeln

Die endliche Regelliste MUSS übliche einfache Schlüsse abbilden: Überlappungen
innerhalb sicher eingeschränkter Bereiche, eindeutige Blockzuordnungen und
daraus folgende Verlängerungen. Ein bekanntes Leerfeld oder eine sichere Grenze
allein macht eine Überlappung nicht zu einer anspruchsvollen Kombination.
Gemeinsame Zuordnung mehrerer Blöcke/Bedingungen bleibt separat unterscheidbar;
alte R2-Schlüsse dürfen nicht pauschal als einfach umbenannt werden.

[SD2-Analyzer §2](SD2_ANALYZER.md#2-endliche-regeln) ist die einzige Definition
von Voraussetzungen, Folgerungen, Grenzen und E0–E3-Familien. Der gemeinsame
schwache Fixpunkt, unbekannte Startzustand und unabhängige Prüfnachweis folgen
SD-D03–D05. Der bestehende Zertifizierungs-/Paarlinienvertrag wird nicht gelockert.
Erforderliches R4 bleibt L5 und benötigt die dort definierten separaten Belege.

## 4. SD2-D02 · Drei getrennte Messprofile

| Profil | Fachlich zu erfassende Aspekte |
| --- | --- |
| Denkanspruch | Tatsächlich nötige Schlüsse, anspruchsvoller Informationsanteil, zusammenwirkende Bedingungen, Zuordnungsmehrdeutigkeit und anspruchsvolle Spitzen. |
| Suchaufwand | Auffindbarkeit des nächsten Schritts, gleichzeitiges Fortschrittsangebot, Gewinn pro Welle, kleinteilige Verläufe sowie Stärke/Häufigkeit/Dauer früher und später Engstellen. |
| Bearbeitungsumfang | Rastermaße, Hinweis-/Blockstruktur und erforderliche Bearbeitung; lange zusammenhängende Füllzüge gegenüber vielen kleinen Abschnitten. |

Hinweiszahl, kurze/lange Blöcke, verbleibende Platzierungsfreiheit und Farbstruktur
sind Zustandsindizien. Ihr Einfluss MUSS am Verlauf und an Gegenbeispielen
begründet sein. Viele kleine Hinweise können vollständig gepackt und direkt
eindeutig sein; Farben können Zuordnungen erleichtern oder Kleinteiligkeit
erzeugen. Ein pauschaler Farb- oder Kleinzahlaufschlag ist unzulässig.

[SD2-Analyzer §3](SD2_ANALYZER.md#3-drei-rohprofile-exakte-messdefinitionen)
definiert allein Feldmengen, Zähler, Nenner, offene/gelöste Linien, neue
Singletons, partielle Farbausschlüsse, Positionen, Ereignisse und Nullfälle.
Mehrfache parallele Begründungen zählen keinen mehrfachen Informationsgewinn.

Der Analyzer sieht alle Linien; das Suchprofil modelliert daraus menschlichen
Suchaufwand und behauptet keine gemessene Suchzeit. Umfangsproxies sind keine
tatsächlichen Klicks oder Gesten. Rechner, Auflösung, Zoom, Schriftgröße und
Zeilenabarbeitungsreihenfolge beeinflussen die Stufe nicht.

## 5. SD2-D03 · Aggregation und Schutz vor Fehlbewertungen

Die interne Gesamtbewertung MUSS feste Grenzen für L1–L5 verwenden. Die
numerische Skala, Gewichte, Nichtlinearitäten, Grenzwerte, Arithmetik und
Gleichheitsbehandlung stehen ausschließlich in SD2-Kalibrierung; sie werden
nicht aus diesem Überblick neu hergeleitet.

Die Formel MUSS folgende Eigenschaften erfüllen:

- Anspruchsvolle Spitzen und späte Schlüsselstellen werden nicht durch triviales Ausfüllen in einem globalen Mittelwert verdeckt.
- Wiederkehrende Engstellen und dauerhaft kleinteiliger Fortschritt bleiben erkennbar; einfache Wiederholung erzeugt keinen hohen Denkanspruch.
- Der reine Umfangsbeitrag erhöht die Bewertung gegenüber Denkanspruch/Suche höchstens um eine Nachbarstufe. Er erzeugt allein keine 4/5; unmittelbare flüssige Fälle bleiben auch groß 1.
- Korrelierte Merkmale wie Zellzahl, Hinweiszahl und Kleinteiligkeit werden nicht unbesehen mehrfach addiert. Weglassen einzelner Gruppen, Gegenproben und Sensitivitätsvergleiche begründen ihren Beitrag.
- Gleiche vollständige Eingabe/Methode liefert gleiche Teilwerte und Stufe. Transposition, Spiegelung und reine Farb-ID-Umbenennung erhalten die skalare Bewertung.
- Motivname, Kategorie, Bildästhetik und erwartetes Histogramm beeinflussen die Bewertung nicht. Fehlender vollständiger Nachweis erzeugt keine Note.

Der Bericht MUSS Teilwerte, Gesamtscore, Stufe, wichtigste Beiträge und Grenznähe
ausweisen. Binnenunterschiede sind Modellwerte, keine präzise menschliche
Messung. Zusätzliche Runtimefreitexte oder Spoiler bleiben unzulässig.
Nicht identifizierte Vergleichsrätsel erhalten keine erfundene ID oder Zielnote.

## 6. SD2-D04 · Referenzen und unabhängige Validierung

Die Referenzbasis MUSS unabhängig vom Produktionskatalog aufgebaut sein.
Auswahlgrund, Herkunft und fachlich begründete Erwartungsstufe beziehungsweise
Vergleichsordnung werden vor Betrachtung neuer Scores und finaler Parameterwahl
persistiert. Der tatsächliche feste Satz und seine Ergebnisse stehen allein
in [SD2-Kalibrierung](SD2_CALIBRATION.md).

Die Abdeckung umfasst alle fünf Stufen, mehrere Größen, Mono/Farbe, lange/kurze
Hinweise, direkte/eingeschränkte Überlappungen, flüssigen/kleinteiligen Fortschritt,
frühe/späte/wiederkehrende Engstellen, kleine schwierige und große einfache Fälle.
Jede Stufe benötigt mehrere unabhängige Muster; L5 umfasst reine Linienlogik
und notwendiges R4. Jede Eigenschaft benötigt konkrete Belege, jedoch keine
starre vollständige Kreuzproduktquote.

Vor Parametrisierung MUSS ein separater Validierungssatz zurückgehalten werden.
Ähnliche Varianten, Rotationen und nahe Ableitungen eines Musters bleiben in
derselben Gruppe. Ergebnisse werden getrennt ausgewertet. Eine Nachjustierung
anhand dieser Fälle verbraucht ihre unabhängige Rolle und benötigt eine neue
unabhängige Prüfung. Erwartungen dürfen nicht passend zum Ergebnis umetikettiert
werden. Widersprüche zu Ankern/Ordnungen sind vor Freeze zu klären.

Eine gewünschte Notenverteilung ersetzt keine fachliche Begründung. Spätere
Bestandsbeobachtungen sind keine Kalibrierung und kein wachsender CI-Testkorpus.
Freiwillige menschliche Vergleiche unterscheiden Erfahrung, Erstlösung oder
Wiederholung, Hilfen, Pausen und subjektiven Denkanspruch. Zeit allein ist kein
Label. Ohne solche Daten bleibt die Methode eine instrumentierte Modellschätzung
höchstens mittlerer Aussagekraft ohne Lösungsminuten oder empirischen Anspruch.

## 7. SD2-D05 · Versionierung und gemeinsame Integration

0.4 ist ein eigener eingefrorener Methodensatz. Die gemeinsame
[Versionierungsregel SD-D02](PUZZLE_DIFFICULTY.md#sd-d02--versionierung-und-gezielte-ablösung)
verbietet Neuversiegelung oder Umdeutung von 0.3. Neue Integrationsmodule liegen
außerhalb der Methodenfreezes. Noch unterstützte alte Analyse-/Bewertungsformen
behalten ihre ursprüngliche Bedeutung; daraus entsteht kein alter Writer.

Einzel-, Auswahl-, Bestands- und Produktionsanalysen verwenden denselben
Methodensatz. Analyse, Vorschau, Übernahme und Produktionsaktivierung bleiben
unterschiedliche Operationen. Gemischte gültige 0.3-/0.4-Bewertungen bleiben
zulässig und redaktionell erkennbar. Die derzeit aktive Methode wird allein
aus dem gültigen Defaultrecord gelesen.

[SD-Catalog](SD_CATALOG.md) definiert aktuelle Bewertungsquellen/Übernahme,
[SD2-Integration](SD2_INTEGRATION.md) geschlossene Methoden-/Berichts-/Defaultformen,
[RI](../production/PUZZLE_INTEGRATION.md) den Erstintegrationsweg und
[Editor §13](../tools/PUZZLE_EDITOR.md#13-pe-edit2-gezielte-pflege-statt-vollbestandsprüfung)
die gezielte Pflege. Aktuelle Quellbindungen ersetzen keine historischen
Produktionsfreigaben und verlangen deren Replay nicht. Reine Neubewertung
behält die Unverändertheitsgrenzen aus SD-D10–D13.

## 8. SD2-D06 · Kontrollierte Bestandsumstellung

Ein ausdrücklicher Neubewertungsauftrag folgt dem
[Ablauf SD-D11](PUZZLE_DIFFICULTY.md#sd-d11--expliziter-wiederholbarer-ablauf).
Für eine Methodenumstellung MUSS der Vergleich zusätzlich Alt-/Neumethode,
drei Profile, Score, Beiträge, Grenznähe, Aussagegrenzen und offene Fälle je ID
sichtbar machen. Relationen innerhalb und zwischen Größen-, Modus- und
Hinweisgruppen sind fachlich zu prüfen. Methodenprobleme stoppen die Übernahme;
Noten, Raster oder Schwellen dürfen nicht im Datenpaket passend gemacht werden.

Vollständiger Auftragsabschluss verlangt die gültige Übernahme aller beauftragten
IDs und eine ausdrücklich beauftragte Aktivierung, falls der Produktionsstandard
gewechselt werden soll. Teilübernahme oder Aktivierung bei offenen Fällen
benötigt eine entsprechend begrenzte Freigabe; gültige Altwerte bleiben erhalten.
Ein bereits kombinierter bedingter Auftrag benötigt keine zusätzliche Freigabe
pro Rätsel. Fremde Quellenänderungen machen den Plan stale.

Exaktes Delta, kompakter Dauerbericht und Wiederholungs-No-op sind nachzuweisen.
Reviews, CI und Mergefreigaben folgen dem aktuellen Workflow und Auftrag.
Historische SD2-D-Ausnahmen werden nicht zu generellen Gates oder Befugnissen.
Recoveryproben verwenden synthetische Fälle, keine Fehlerinjektion am realen
Bestand. Kein Zeitplan, Nachtlauf, CI-Rating oder Solver im Spieler.

## 9. Historische Entwicklungspakete

SD2-A/B/C/D sind geliefert und integriert. Der
[feste frühere Dokumentstand](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/PUZZLE_DIFFICULTY_V2.md#9-entwicklungspakete-und-gates)
erhält Paketabfolge, damalige Gates und auftragsspezifische Ausnahmen.
Er ist keine zusätzliche aktuelle Normquelle. Neue Arbeit erhält ihre
Prüfauswahl aus [CI_WORKFLOW_V2](../ci/CI_WORKFLOW_V2.md) und dem tatsächlichen Diff.

## 10. Dauerhafte Zuständigkeiten

Dieses Dokument führt den fachlichen 0.4-Vertrag. Exakte Ableitungsregeln und
Rohprofile gehören allein zu SD2-Analyzer; Zahlen, Referenzen, Ergebnisformate
und Freeze allein zu SD2-Kalibrierung. Gemeinsame Fachgrenzen gehören zu SD,
aktuelle Katalogoperationen zu SD-Catalog. Issues/PRs führen Scope, tatsächliche
Änderungen, Nachweise, Entscheidungen und Freigaben. Ein Fachvertrag erteilt
keine technische Start-, Abnahme- oder Mergefreigabe.
