# SD2: Menschennähere Schwierigkeit und feste Skala 1–5

Stand: 26.10.2026 · Spezifikation 1.0 · SD2-A/B/C integriert, D bis F01/T01 auf dem Arbeitsbranch

[Gesamtissue #402](https://github.com/venomenon328/picross/issues/402) führt die
Methodenrevision nach Eigentümerfreigabe vom 25.10.2026. Der anschließende
ausdrückliche SD2-A-Auftrag liefert [technische Verträge](SD2_ANALYZER.md),
neue Regeln und drei Rohprofile über [PR #408](https://github.com/venomenon328/picross/pull/408),
nach separatem R01 integriert auf `c7c6156ac27dc033036443bc06ef398bbf94f32f`.
[A-Nachweise](SD2_A_VERIFICATION.md) behalten ihre historische Headbindung.
Der ausdrückliche B-Auftrag liefert [Referenzen, Zahlenvertrag und Freeze](SD2_CALIBRATION.md)
über [PR #409](https://github.com/venomenon328/picross/pull/409), nach separatem R01
integriert auf `0ae6535073fb808af44dcf3e12130a33ba49cdbc`.
[SD2-B-T01](SD2_B_VERIFICATION.md) bleibt historisch headgebunden.
[SD2-C-V01](SD2_INTEGRATION.md) schließt vor Code die gemeinsamen Formate,
Quellen-/Methodenwahl, Runtimezulassung und Transaktions-/Aktivierungsregeln.
C ist nach separatem R01 über [PR #410](https://github.com/venomenon328/picross/pull/410)
auf `4e23e644f3457362e02b75f78fdb575a99265494` integriert; die dortige
Eigentümerausnahme zum fehlenden Gesamt-CI-/Chromium-Gate gilt nur für #410.
Der gesonderte Auftrag [SD2-D-V01](SD2_D_VERIFICATION.md) liefert die gebundene
reale Analyse und Vorschau. Der Folgeauftrag [SD2-D-OM01](SD2_D_OM_FOLLOWUP.md)
klärt Om und ergänzt den vollständigen Plan mit 45 gültigen Vorschlägen.
Alle 45 Vorschläge einschließlich Om sind abgenommen. Der Eigentümer hat ausdrücklich
auf separates SD2-D-VR01 verzichtet; es wurde nicht durchgeführt. Diese
auftragsspezifische Ausnahme ersetzt nur dieses Gate, nicht finales R01 oder
Mergefreigabe. Der anschließende [F01/T01-Auftrag](SD2_D_ADOPTION.md) übernimmt
alle 45 Ratings und aktiviert 0.4, jeweils mit echtem Wiederholungs-No-op.
Die Web-Sperre gilt ausschließlich für PR #411 und lässt das Gesamt-CI-Gate
sichtbar unerfüllt; finales R01 und Merge bleiben offen.

## 1. Ausgangslage und gezielte Ablösung

Die Prüfung an `main@519bff3b3cc1e4634c09c23f597e84d1ad040ae6` las vorhandene
Ratings und die Bewertungsfunktion, ohne neue Rätselanalysen auszuführen:
45 sichtbare Rätsel, davon 0 × L1, 0 × L2, 32 × L3, 10 × L4 und 3 × L5.
Bei 42 vollständigen Linienbewertungen war R2 die höchste verwendete Familie;
zwei weitere Bewertungen beruhen auf separat erforderlichem R4, eine auf R3.
Der Größenbeitrag erhöhte bei zwei Einträgen die Stufe. Dies ist ein gebundener
Beobachtungsbefund, kein Sollhistogramm und kein automatischer Testbestand.

Die [0.3-Regeln](SD_ANALYZER.md) ordnen etwa eine durch einen bekannten leeren
Rand ermöglichte zusätzliche Überlappung bereits R2 zu. Die
[0.3-Aggregation](SD_CALIBRATION.md) führt R2 außerhalb einer engen lokalen
Ausnahme mindestens auf L3. Hinweiszahl und Hinweislängensumme werden erfasst,
aber nicht unmittelbar bewertet. Der kleine synthetische Referenzsatz belegt
technische Klassen, keine empirische menschliche Schwierigkeit. Diese Grenzen
begründen eine neue Methode, nicht das heimliche Verschieben alter Schwellen.

SD / #235 ist mit SD-A/B/C1/C2 und PR #240–#243 abgeschlossen. Historische
Lieferberichte mit damals offenen Gates werden dadurch nicht erneut geöffnet.
`picross-difficulty-0.3` bleibt bis zur gesonderten Umstellung aktiv und behält
seine exakten Regel-, Quellen-, Referenz-, Formel-, Hash- und Formatbindungen.
Kennung der neuen Methode ist **`picross-difficulty-0.4`**; SD2-B liefert sie
eigenständig implementiert, synthetisch kalibriert und eingefroren. Die gemeinsame
Integration ist geliefert; SD2-D-F01/T01 hat nach vollständiger Übernahme der
45 geprüften Bewertungen den Produktionsstandard 0.4 auf dem Arbeitsbranch
ausdrücklich aktiviert. Finales R01 und Main-Merge bleiben getrennt offen.

Diese Spezifikation ersetzt für die neue Methode gezielt die in
[SD-D01/D04–D08](PUZZLE_DIFFICULTY.md) beschriebene konkrete Technik-/Fluss-
Zuordnung durch die folgenden drei Profile und eine neue Kalibrierung. Die
konkreten 0.3-Formeln gelten weiterhin ausschließlich für 0.3. Die Grenzen
für Deduktionssicherheit, Versionierung, explizite Übernahme, Quellenbindung,
Spielstände und synthetische Tests aus SD-D02/D03/D09–D14 bleiben erhalten.
Die bisherige Begrenzung des reinen Umfangsbeitrags wird ausdrücklich erhalten.

## 2. Bedeutung der Bewertung

Die sichtbare Schwierigkeit beschreibt den modellierten menschlichen
Lösungsanspruch. **Denkanspruch, Suchaufwand und Bearbeitungsumfang** werden
intern getrennt gemessen, begründet und zu genau einer Stufe zusammengeführt.
Denkanspruch dominiert; Suche und Umfang tragen spürbar und nachvollziehbar bei.
Eine fünfmal längere Lösungszeit ist nicht automatisch fünfmal höhere Schwierigkeit.
CPU-Zeit ist weder Lösungszeit noch ein Bewertungsmerkmal.

| Stufe | Orientierung für 0.4 |
| --- | --- |
| 1 · Sehr leicht | Durchgehend unmittelbar verständlicher, flüssiger Fortschritt; auch große direkte Fälle. |
| 2 · Leicht | Übliche einfache Techniken einschließlich sicher eingeschränkter Überlappungen und eindeutiger Verlängerungen; gut auffindbarer regelmäßiger Fortschritt. |
| 3 · Mittel | Wiederholt Informationen kombinieren und/oder deutlich erhöhte Suche nach tragfähigem Fortschritt, ohne anhaltend hohen Gesamtanspruch. |
| 4 · Schwer | Anspruchsvolle Kombinationen, erheblicher Suchaufwand oder wiederkehrende relevante Engstellen bei entsprechendem logischem Profil. |
| 5 · Sehr schwer | Sehr anspruchsvolle reine Linienlogik mit ausgeprägten Anforderungen oder separat nachgewiesene notwendige Paarlinienlogik. |

Alle Stufen müssen an nachvollziehbaren Referenzen sinnvoll erreichbar sein.
Der echte Bestand muss nicht jede Stufe enthalten. Keine Quoten, automatische
Streckung, Katalog-Min/Max-Normierung oder Quantile. Neue Einträge verändern
weder Grenzen noch die Bewertung anderer Rätsel. Keine zusätzliche UI-Achse,
Zeitprognose, Scoreanzeige, Sortierart, Sterne- oder Progressionsänderung.

## 3. SD2-D01 · Menschennähere einfache Regeln

Die neue endliche Regelliste muss übliche einfache Nonogramm-Schlüsse tatsächlich
abbilden. Dazu gehören Überlappungen innerhalb eines durch bereits bekannte
Leerfelder oder sichere Grenzen eingeschränkten Bereichs, eindeutige
Blockzuordnungen und daraus folgende Verlängerungen. Eine solche Einschränkung
allein macht den Schluss nicht zur anspruchsvollen Kombination. Echte kombinierte
Zuordnung mehrerer Blöcke/Bedingungen bleibt separat unterscheidbar.
Nicht sämtliche bisherigen R2-Schlüsse pauschal umetikettieren.

Vor der jeweiligen Implementierung sind Voraussetzungen, Folgerungen, Grenzen
und Familienbezeichnungen exakt festzulegen. Die neuen Namen dürfen alte R0–R4-
Belege nicht umdeuten. Schwächere Regeln werden bis zum Fixpunkt ausgeschöpft,
bevor eine stärkere als erforderlich gilt; nach stärkerem Fortschritt beginnt
die Prüfung erneut schwach. Techniknotwendigkeit gilt für den definierten
Regelsatz, nicht für jede denkbare menschliche Strategie.

Analyseeingang bleibt ein vollständig unbekanntes Raster mit Hinweisen,
Dimensionen und echter Farb-/Abstandssemantik. Keine Zielmatrix, Motiverkennung,
vermutete Symmetrie, Eindeutigkeitsannahme oder hypothetische Spielfortsetzung.
Synchrone Bewertungszustände, deduplizierte Folgerungen und unabhängige Prüfung
bleiben. Der bestehende Zertifizierungs-/Paarlinienvertrag wird nicht gelockert.
R4 benötigt weiterhin die unabhängig bestätigte unvollständige Linienbaseline
und den vollständigen passenden Paarproof; notwendiges R4 bleibt L5.

## 4. SD2-D02 · Drei getrennte Messprofile

| Profil | Verbindlich zu erfassende Aspekte |
| --- | --- |
| Denkanspruch | Schwierigkeit tatsächlich nötiger Schlüsse, anspruchsvoller Informationsanteil, Zahl zusammenwirkender Bedingungen, Zuordnungsmehrdeutigkeit und anspruchsvolle Spitzen. |
| Suchaufwand | Auffindbarkeit des nächsten Schritts, gleichzeitiges Fortschrittsangebot im offenen Raster, Fortschritt pro Entscheidung/Welle, kleinteilige Verläufe und Stärke/Häufigkeit/Dauer früher wie später Engstellen. |
| Bearbeitungsumfang | Rastermaße, Hinweis-/Blockstruktur und tatsächlich erforderliche Bearbeitung; lange zusammenhängende Füllzüge gegenüber vielen kleinen Abschnitten/Einzelentscheidungen. |

Zusätzlich zu Verlauf und Technik sind Hinweiszahl, Verteilung kurzer/langer
Blöcke, verbleibende Platzierungsfreiheit und Farbstruktur zu untersuchen.
Statische Strukturmerkmale sind Indizien; ihr Einfluss muss am tatsächlichen
Verlauf und an Gegenbeispielen begründet werden. Viele kleine Hinweise können
vollständig gepackt und unmittelbar eindeutig sein. Farben können Zuordnungen
erleichtern oder kleinteilige Arbeit erzeugen. Weder Farbe noch Kleinzahlanteil
erhalten einen pauschalen Schwierigkeitsaufschlag.

Die Messdefinitionen trennen offene/gelöste Linien, neue Singletons, partielle
Farbausschlüsse, einzelne Positionen und wiederholte Ereignisse. Jeder
Informationsverlust zählt nur einmal je Zusammenführung. Nenner, leere Folgen,
Nullwerte, Normierung verschiedener Farbzahlen und Ressourcenabbrüche müssen
vor Format-/Analysecode exakt feststehen. Keine automatische Schwierigkeit aus
roher Anzahl entfernter Farbwerte oder überzähligen parallelen Begründungen.

Der Analyzer sieht alle Linien; ein Mensch muss den nächsten Schritt erst finden.
Das Suchprofil ist deshalb ausdrücklich ein modellierter Aufwand aus verfügbaren
Informationen, keine behauptete gemessene Suchzeit. Umfangs-/Gestenproxies dürfen
nicht als tatsächliche Spielerklicks ausgegeben werden. Rechner, Auflösung,
Zoom, Schriftgröße oder Zeilenabarbeitungsreihenfolge beeinflussen die Note nicht.

## 5. SD2-D03 · Aggregation und Schutz vor Fehlbewertungen

Aus den drei Profilen entsteht eine fein abgestufte interne Gesamtbewertung
mit festen Grenzen für L1–L5. Die konkrete numerische Skala, Gewichte,
Nichtlinearitäten, Grenzwerte, Arithmetik und Gleichheitsbehandlung sind
Liefergegenstand der Referenzkalibrierung, keine hier erfundenen Prozentzahlen.
Sie werden vor Bewertungsimplementierung dokumentiert und anschließend als
vollständige neue Methodenversion eingefroren.

Verbindliche Eigenschaften:

- Anspruchsvolle Spitzen und späte Schlüsselstellen werden nicht durch viel
  triviales Ausfüllen in einem globalen Durchschnitt verdeckt.
- Wiederkehrende Engstellen und dauerhaft kleinteiliger Fortschritt bleiben
  erkennbar; bloße einfache Wiederholung erzeugt keinen hohen Denkanspruch.
- Gegenüber derselben Bewertung aus Denkanspruch und Suche ohne Umfang darf
  der reine Umfangsbeitrag höchstens eine benachbarte Stufe erhöhen. Er erzeugt
  allein keine 4/5. Durchgehend unmittelbare/flüssige Fälle bleiben auch groß 1.
- Korrelierte Merkmale, etwa Zellzahl, Hinweiszahl und Kleinteiligkeit, werden
  nicht unbesehen mehrfach addiert. Die Wirkung jeder Merkmalsgruppe wird mit
  Gegenproben, Weglassen einzelner Gruppen und Sensitivitätsvergleichen begründet.
- Gleiche Eingabe/Version liefert gleiche Teilwerte und Stufe; Transposition,
  Spiegelung und reine Farb-ID-Umbenennung erhalten die skalare Bewertung.
- Kein Bonus/Malus aus Motivname, Kategorie, Bildästhetik oder erwartetem
  Histogramm. Kein automatisches Rating bei fehlendem vollständigem Nachweis.

Der Bericht weist Teilwerte, Gesamtscore, Stufe, wichtigste Beiträge und
Grenznähe aus. Ein Score innerhalb einer Stufe darf Unterschiede erklären,
ist aber keine präzise menschliche Messung. Keine zusätzlichen Runtimefreitexte
oder Spoiler. Konkrete 20×20-/30×40-Vergleichsrätsel des Eigentümers sind noch
nicht per ID benannt; keine Identität oder verbindliche Zielnote dafür erfinden.

## 6. SD2-D04 · Referenzen, unabhängige Validierung und Aussagegrenzen

Die Referenzbasis wird gegenüber 0.3 deutlich verbreitert und unabhängig vom
Produktionskatalog aufgebaut. Auswahlgrund, Herkunft und fachlich begründete
Erwartungsstufe beziehungsweise Vergleichsordnung werden **vor Betrachtung der
neuen Scores und finaler Parameterwahl** persistiert.

Die Abdeckungsmatrix umfasst alle fünf Stufen, mehrere Rastergrößen, Mono/Farbe,
lange/kurze Hinweise, direkte/eingeschränkte Überlappungen, flüssigen/kleinteiligen
Fortschritt, frühe/späte/wiederkehrende Engstellen sowie kleine schwierige und
große einfache Fälle. Jede Stufe benötigt mehrere unabhängige Muster; für L5
reine Linienlogik und notwendiges R4. Keine starre vollständige Kreuzproduktquote,
aber jede genannte Eigenschaft braucht zugeordnete konkrete Referenzbelege.

Vor Parametrisierung wird ein getrennter Validierungssatz zurückgehalten.
Ähnliche Varianten, Rotationen und nahe Ableitungen eines Musters bleiben in
derselben Gruppe. Validierungsergebnisse werden getrennt ausgewertet. Wird
danach anhand dieser Fälle nachjustiert, sind sie keine unangetastete Validierung
mehr; die Änderung und eine neue unabhängige Prüfung werden kenntlich gemacht.
Kein nachträgliches Umetikettieren von Erwartungen passend zum Ergebnis.

Die endgültige Methode muss die vorab begründeten Ordnungen, klare Anker und
Grenz-/Gegenbeispiele erklären. Widersprüche werden vor Freeze geklärt; eine
gewünschte Notenverteilung ist kein Ersatz. Grenzen bleiben nach Freeze fest.
Ein späterer echter Bestandsvergleich dient der Plausibilitätsprüfung, niemals
dem heimlichen Nachkalibrieren oder einem wachsenden CI-Testkorpus.

Freiwillige menschliche Vergleichslösungen sind hilfreich, aber kein neues
Pflichtgate je Rätsel oder Paket. Falls vorhanden, Erfahrung, Erstlösung oder
Wiederholung, Hilfen, Pausen und subjektiven Denkanspruch getrennt dokumentieren.
Zeit allein ist kein Label; subjektiver Anspruch und reine Eingabearbeit dürfen
nicht gleichgesetzt werden. Ohne passende menschliche Daten bleibt die Methode
eine instrumentierte Modellschätzung höchstens mittlerer Aussagekraft, ohne
Lösungsminuten oder Behauptung empirischer Kalibrierung.

## 7. SD2-D05 · Versionierung und gemeinsame Integration

Neue Regeln/Metriken/Aggregation werden separat versioniert. Die eingefrorenen
0.3-Quelldateien dürfen nicht geändert und anschließend mit neu berechneten Hashes
als alte Methode ausgegeben werden. Benötigte geänderte gemeinsame Module sind
geeignet zu isolieren/versionieren. Alte Aufrufe, Berichte, Ratings, Quellen und
Referenzprüfungen behalten ihre ursprüngliche Bedeutung und Funktionsfähigkeit.

[SD-C1](SD_CATALOG.md), [ZA-1](ZA1_ADAPTER.md) und [Kategorien](CATEGORIES.md)
bleiben der gemeinsame Integrations-/Transaktionsweg. Vor der ersten betroffenen
Codeänderung sind neue exakte Felder, Formate, Quellenpriorität, Versionsdispatch,
Limits und Alt-/Neujournal-Kompatibilität festzulegen. Eine geplante Methode
erweitert kein heutiges geschlossenes Schema stillschweigend.

Einzel-, Auswahl-, Bestands- und Produktionsweg verwenden denselben eingefrorenen
Methodensatz. Analyse, Vorschau, Übernahme und Aktivierung bleiben unterscheidbar.
Es gibt einen ausdrücklichen gebundenen Aktivierungsweg für den Produktionsstandard;
die reine technische Lieferung aktiviert ihn im echten Bestand noch nicht.
Bis SD2-D bleibt 0.3 aktiv. Gültige gemischte Methoden müssen während einer
kontrollierten Umstellung verarbeitet und redaktionell sichtbar gemacht werden.

Berichte/aktive Quelle erhalten die drei Profile und reproduzierbaren Bindungen.
Die Runtime erhält weiterhin nur minimale spoilerfreie Angaben für die
bestehende Fünferskala; kein neuer sichtbarer Score oder Sortierschlüssel.
Writer, Loader, Validator, Register, Update, Sync, Adoption, Cleanup und Recovery
verwenden denselben Vertrag einschließlich bestehender AT-/Added-Quellen.

Reine Neueinstufung verändert weder Rätseldefinition, Hinweise, ID, Puzzle-
Runtime-Revision, Slot, Kategorie, Added-Daten, Bild/AT-Quelle noch historische
Produktions-/Freigabebindungen oder Saves. Keine alte Bild-/Rasterproduktion
rekonstruieren. Fehlgeschlagene neue Versuche ersetzen keine gültige alte
Bewertung; fehlende/veraltete Ergebnisse werden niemals mit 0 oder 5 aufgefüllt.

## 8. SD2-D06 · Kontrollierte Bestandsumstellung

Erst nach abgenommenen SD2-A/B/C und gesondertem Ausführungsauftrag:

1. Quellcommit, vollständige gewählte ID-Liste, Eingangs-/Methodenbindungen und
   Budgets vorab festhalten; aktuelle vorhandene Werte lesen.
2. Den ausdrücklich gewählten Bestand mit dem unveränderten Freeze analysieren.
   Vergleich je ID mit Alt-/Neumethode und -stufe, drei Profilen, Score, Gründen,
   Grenznähe, Aussagegrenzen und konkreten offenen Fällen liefern.
3. Relationen innerhalb/zwischen Größen-, Modus- und Hinweisgruppen prüfen;
   Auffälligkeiten begründen. Separates qualifiziertes Vor-Übernahme-Review des
   vollständigen gebundenen Berichts/Plans (für #406 durch die oben dokumentierte
   Eigentümerentscheidung erlassen). Bei Methodenproblemen stoppen,
   nicht Noten, Raster oder Schwellen im Datenpaket passend machen.
4. Mit passendem Übernahmeauftrag aktuelle geprüfte Ergebnisse kontrolliert
   übernehmen und den Standard für neue Produktion ausdrücklich aktivieren.
   Ein bereits kombinierter bedingter Auftrag braucht keine erneute Freigabe
   pro Rätsel. Zwischenzeitlich fremde Quellenänderungen machen den Plan stale.
5. Exaktes Delta, vollständige kompakte Dauerberichte und echten Wiederholungs-
   No-op nachweisen. Separates finales Daten-/Integrationsreview und ausgewählte
   CI am gebundenen Head vor Merge; Merge benötigt seine eigene Freigabe.

Vollständiger Abschluss verlangt gültige Übernahme aller beauftragten IDs und
explizite Aktivierung für neue Rätsel. Offene Fälle bleiben offen und bewahren
gültige Altwerte. Teilübernahme oder Aktivierung trotz offener Fälle braucht
einen ausdrücklich begrenzten Folgeauftrag; sie ist kein stiller Standard.
Keine Fehlerinjektion am echten Bestand; Recoveryprüfungen verwenden synthetische
C-Fälle. Kein Zeitplan, Nachtlauf, CI-Rating oder Solver im Spieler.

## 9. Entwicklungspakete und Gates

| Paket | Eigenständiges Ergebnis | Abhängigkeit |
| --- | --- | --- |
| [SD2-A · #403](https://github.com/venomenon328/picross/issues/403) | Exakte menschennähere Regeln, getrennte Rohprofile, eigener Analyzer-/Berichts-/Prüfpfad; keine neue Endnote. | Integrierte SD2-Spezifikation |
| [SD2-B · #404](https://github.com/venomenon328/picross/issues/404) | Breite vorab gebundene Referenzen, getrennte Validierung, numerischer Vertrag und eingefrorene Methode 0.4. | SD2-A abgenommen |
| [SD2-C · #405](https://github.com/venomenon328/picross/issues/405) | Kompatibler gemeinsamer Produktions-/Katalog-/Übernahme-/Aktivierungsweg, synthetisch nachgewiesen; Altstandard bleibt aktiv. | SD2-A/B abgenommen |
| [SD2-D · #406](https://github.com/venomenon328/picross/issues/406) | Tatsächlicher vollständiger Vergleich, geprüfte Übernahme und Aktivierung samt Dauerbericht/No-op. | SD2-A/B/C integriert und abgenommen; ausdrücklicher Inhaltsauftrag |

Ein Implementierungs-PR je Paket; SD2-D trennt Vor-Übernahme- und finales Review
innerhalb desselben Datenpakets. Kein zusätzliches Issue allein für Tests oder
Dokumentation. Exakte Regeln/Formate und numerische Parameter sind sequenzielle
Liefergegenstände A/B/C und in deren Detailverträgen geschlossen.
SD2-A/B/C sind nach separaten Reviews über PR #408/#409/#410 integriert.
D liefert V01, den begrenzten Om-Folgeauftrag OM01 und nach vollständiger
Vorschlagsabnahme F01/T01 mit Übernahme/Aktivierung. VR01 ist durch die
Eigentümerentscheidung erlassen; finales R01 und Merge bleiben offen.
Dieser Fachvertrag allein
ist keine technische Startfreigabe und keine Modell-/Eigenumsetzungsempfehlung.

Jedes Paket erhält technische T01-Nachweise, getrenntes Selbstreview und ein
qualifiziertes separates R01 am konkreten Head vor Merge. Die Issue-Bodies
enthalten überprüfbare A01–A05, B01–B06, C01–C06 und D01–D06. Relevante
Altkompatibilität, Regelkorrektheit, deterministische Bewertung, Grenzfälle,
Farben/Symmetrien und Fehler-/Recoverygrenzen sind an festen unabhängigen
synthetischen Inputs nachzuweisen. Es entstehen keine Tests aus dem realen
Katalog oder daraus kopierten/abgeleiteten Fällen.

Die [CI-Policy](CI_POLICY.md) bestimmt die Auswahl aus dem tatsächlichen
Gesamtdiff. Reine Spezifikationspflege benötigt schnellen Docs-/Werkzeugpfad,
Dokumentvalidator, Diffcheck und `ci-required`, keine Rätsel-/Produktläufe.
Spätere Regeln/Bewertung, gemeinsame Datenintegration und echte Datenübernahme
behalten ihre jeweils passenden Prüfwege; kein pauschaler Kurzpfad für SD2.

## 10. Dauerhafte Zuständigkeiten

Dieses Dokument führt den fachlichen SD2-Sollvertrag; #402 den Gesamtstatus und
die vier Paket-Issues Scope/Akzeptanz/Abhängigkeiten. Die technischen A/B/C-
Lieferungen ergänzen ihre versionierten Detailverträge und die CLI-/Authoring-
Anleitung vor der jeweils betroffenen Codeänderung. Historische 0.3-Verträge
bleiben als solche erhalten. PRs binden tatsächliche Änderungen, Checks,
Reviews und Freigaben; eine Spezifikationsfreigabe ersetzt keine dieser Lieferungen.
