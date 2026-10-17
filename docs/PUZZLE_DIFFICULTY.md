# Rätselschwierigkeit und wiederholbare Katalogeinstufung · SD

Stand: 17.10.2026 · Spezifikation 1.0 · freigegebener Sollvertrag

Die Spezifikation einschließlich der katalogunabhängigen Referenzkalibrierung
ist freigegeben. Beauftragt sind ihre Dokumentation und Entwicklungspakete;
Implementierung, reale Bewertungsdurchläufe und Merge sind noch nicht beauftragt.
Die nachstehenden Fähigkeiten beschreiben das Soll, keine bereits verfügbare CLI.

[Zielissue #235](https://github.com/venomenon328/picross/issues/235) führt den
Gesamtumfang; [SD-A #236](https://github.com/venomenon328/picross/issues/236),
[SD-B #237](https://github.com/venomenon328/picross/issues/237) und
[SD-C #238](https://github.com/venomenon328/picross/issues/238) die Entwicklungspakete.
Die Eigentümerklarstellung vom 17.10.2026 zu unabhängigen Skalenenden und
zulässigen unbesetzten Stufen ist in SD-D01/SD-D08 verbindlich übernommen.

Grundlage ist `main@d98c0066394c414b86f745c63fbfec2813ad3331`.
[Produktdefinition](PRODUCT_DEFINITION.md), [Rätselproduktion](PUZZLE_PRODUCTION.md),
[Paarlinienvertrag](PAIRED_LINES.md), [Authoring](ai-workflows/PUZZLE_AUTHORING.md),
[ZA-1](ZA1_ADAPTER.md), [Kategorien](CATEGORIES.md),
[Katalogdarstellung](CATALOG_PRESENTATION.md) und [CI-Policy](CI_POLICY.md)
gelten außerhalb der hier ausdrücklich fortgeschriebenen Schwierigkeit weiter.

## SD-D01 · Ziel und Bedeutung der Skala

Jedes fertig eingestufte Rätsel erhält eine begründete, wiederholbare Schwierigkeit
von 1 bis 5. Der logische Anspruch bestimmt die Bewertung; Größe darf einen
begrenzten Zusatzbeitrag leisten. Arbeitsumfang und mögliche Lösungszeit bleiben
separat erkennbar. Spielerleistung, Fehler, Undo, Sterne und Progression werden
dadurch nicht bewertet oder verändert.

| Stufe | Kataloganzeige | Fachliche Orientierung für die neue Methode |
| --- | --- | --- |
| 1 | Sehr leicht | Durchgehend unmittelbar verständliche, flüssige Deduktionen; vollständig mit R0 lösbare Rätsel gehören hierher. |
| 2 | Leicht | Regelmäßiger Fortschritt mit einfachen Techniken, insbesondere einfachen Überlappungen und Verlängerungen. |
| 3 | Mittel | Wiederholt mehrere Informationen kombinieren; weiterhin ausreichend erkennbare Fortschrittsmöglichkeiten. |
| 4 | Schwer | Komplexe Linienlogik oder wiederkehrende relevante Engstellen. |
| 5 | Sehr schwer | Anspruchsvolle Linienlogik mit ausgeprägten Engstellen oder nachgewiesener notwendiger Paarlinienlogik. |

Alle fünf Stufen müssen fachlich erreichbar sein. Stufe 5 ist innerhalb reiner
Linienlogik erreichbar und nicht ausschließlich für Paarlinien reserviert.
Der aktuelle Katalog muss nicht alle Stufen enthalten; es gibt keine Mengenquote,
Zwangsverteilung oder automatische Streckung vorhandener Werte auf die Skala.

## SD-D02 · Versionierung und gezielte Ablösung

Vorgesehen ist `picross-difficulty-0.3` als neue Bewertungsmethode. Ihre genaue
Regelliste, Metrikdefinitionen, Aggregation, Grenzwerte und Kalibrierungsgrundlage
werden in SD-A/SD-B vollständig festgelegt und vor der Bestandsanwendung gebunden.
Bis dahin bezeichnet 0.3 die geplante Methode, keine fertige Bewertungsfunktion.

Die bisherigen Methoden 0.1 und 0.2 behalten ihre historische Bedeutung.
Insbesondere bleiben der bisherige R0–R3-Vertrag und die zusätzliche
R4-Notwendigkeitsprüfung unter 0.2 unverändert lesbar. Vorhandene Schätzungen
werden weder rückwirkend instrumentiert genannt noch als 0.3 umetikettiert.

SD ersetzt für neue Bewertungen gezielt die bisher ausschließlich logische
Stufenzuordnung um den begrenzten Größenbeitrag und eine geprüfte Instrumentierung.
Die bisherigen vorläufigen Engstellenschwellen sind keine ungeprüft übernommenen
0.3-Grenzen. Eine spätere Änderung bewertungswirksamer Regeln oder Schwellen
benötigt eine neue Methodenversion und ausdrücklich beauftragte Neubewertungen.

## SD-D03 · Zertifizierung und Bewertung getrennt prüfen

Der vorhandene Solver mit unabhängigem Verifier bleibt Grundlage für zulässige
Deduktion. Er wird um ein getrenntes Bewertungsmodul ergänzt; das Spiel erhält
keinen Solver und keine Laufzeitberechnung der Schwierigkeit.

Der Bewertungsanalysator arbeitet vom vollständig unbekannten Raster aus mit
Hinweisen, Dimensionen sowie Farb-/Abstandsregeln. Er verwendet keine Zielmatrix,
Motivkenntnis, vermutete Symmetrie, Vorbelegung, Eindeutigkeitsannahme, Suchzweige
oder probeweise Spielfortsetzungen als Deduktionsprämisse.

Die Bewertungsspur erhält einen eigenen versionierten Vertrag. Bestehende
Proofs verlangen bei einer Linienanwendung sämtliche erzwungenen Ausschlüsse;
eine absichtlich schwächere Bewertungsregel darf diesen Vertrag nicht lockern.
Die Korrektheit eines Ausschlusses und seine Einstufung als bestimmte einfache
Regel sind getrennt zu prüfen. Solverflags oder passende Endzellen allein
beweisen weder Techniknotwendigkeit noch eine zutreffende Schwierigkeitsstufe.

## SD-D04 · Nachgewiesener Technikbedarf

| Familie | Zu instrumentierender Inhalt |
| --- | --- |
| R0 | Direkte Voll-/Leerbelegung, vollständige Packung und sichere Restleerfelder nach eindeutig abgeschlossenen Blöcken. |
| R1 | Einfache Überlappungen sowie Grenzen und Verlängerungen eindeutig zugeordneter Blöcke. |
| R2 | Kombinierte Zuordnung mehrerer Blöcke oder Segmente; mehrere Anker, Trennungen oder Farbregeln gemeinsam auswerten. |
| R3 | Allgemeine vollständige Zeilenunterstützung, soweit der Fortschritt nicht mit den definierten R0–R2-Regeln erreichbar ist. |
| R4 | Notwendige gemeinsame Paarlinienlogik unter dem unveränderten Paarlinienvertrag. |

SD-A konkretisiert R0–R2 in endliche, überprüfbare Regellisten mit eindeutigen
Voraussetzungen, Folgerungen und Familienzuordnung. Die Tabellenbeschreibungen
allein sind noch keine Implementierung. Ein verdeckter Aufruf vollständiger
Linienlogik darf einen Schluss nicht nachträglich als einfache Regel ausgeben.

Schwächere Regelfamilien werden bis zum vollständigen Fixpunkt ausgeschöpft,
bevor eine stärkere Familie als notwendig gilt. Nach stärkerem Fortschritt
beginnt die nächste Bewertung wieder bei den schwächeren Familien. Notwendigkeit
bezieht sich auf die genau definierten Familien, nicht auf jede denkbare
menschliche Lösungsstrategie. Höchste nötige Technik und ihre Häufigkeit zählen.

R4 verlangt weiterhin die separat unabhängig bestätigte `full-line-*`-Baseline
mit `stalled` und einen vollständigen unabhängig geprüften Paarproof derselben
Logik. Bloße Profilwahl, einzelner Paarschritt, Suchurteil oder Baselineabbruch
reichen nicht. Nachgewiesenes R4 bleibt Stufe 5 mit der bestehenden Kennzeichnung
„linienübergreifend / besonders hoher logischer Anspruch“. Vollständig gelöste
Linienfälle benötigen keinen zusätzlichen routinemäßigen Paar- oder Suchlauf.

## SD-D05 · Synchrone Bewertungswellen

Bewertungswellen vermeiden eine Einstufung nach zufälliger Zeilenreihenfolge:

1. Den Rasterzustand vor einer Welle unverändert festhalten.
2. Alle anwendbaren Schlüsse derselben gerade betrachteten Regelstärke aus
   genau diesem Zustand bestimmen; kein Schluss sieht Änderungen seiner Welle.
3. Sämtliche begründeten Ausschlüsse gemeinsam übernehmen. Mehrfach abgeleitete
   Zelländerungen und identische Ausschlüsse werden jeweils nur einmal gezählt.
4. Aus dem zusammengeführten Zustand fortsetzen und schwächere Regeln wieder
   vorrangig bis zum Fixpunkt ausschöpfen.

Die Zuordnung konkurrierender gleich starker Begründungen, Zählweisen und
Abschlussbedingungen werden deterministisch festgelegt. Quellenreihenfolge,
Threadplanung, Plattform oder Wörterbuchiteration dürfen das Resultat nicht
verändern. Bestehende Zertifizierungsprofile behalten ihren eigenen Ablauf;
Bewertungswellen ändern weder alte Proofbytes noch deren Verifikation.

CPU-Zeit, FIFO-Aufrufe und die Schrittzahl eines beliebigen vorhandenen Proofs
sind keine Schwierigkeitsskala. Eine lange Kette offensichtlicher Fortschritte
darf nicht allein wegen vieler Wellen als hoher logischer Anspruch erscheinen.

## SD-D06 · Messwerte und Engstellen

Der Bericht führt mindestens folgende getrennte, genau definierte Messwerte:

| Messwert | Aussage und Grenze |
| --- | --- |
| Einfache Deduktionen | Anteil des Fortschritts, der mit den schwachen Regelfamilien erreichbar ist. |
| Technikbedarf | Höchste tatsächlich benötigte Familie und Häufigkeit stärkerer Anwendungen. |
| Fortschrittsangebot | Gleichzeitig produktive noch offene Linien, gemessen am selben Zustand vor der Welle. |
| Informationsgewinn | Eindeutige geänderte Zellpositionen und neu bestimmte Zellen; partielle Domainverluste separat. |
| Engstellen | Häufigkeit und Dauer von Phasen mit wenig verfügbarem, anspruchsvollem Fortschritt. |
| Verlauf | Synchrone Wellen und Verteilung der Fortschritte, einschließlich gesonderten Restaufräumens. |
| Umfang | Breite, Höhe, Zellzahl und nachvollziehbarer Bearbeitungsumfang als eigene Angaben. |

SD-A legt für Anteile die Zähler und Nenner sowie die Behandlung bereits
bestimmter Linien und Zellen fest. SD-B bindet daraus genaue Engstellen- und
Restaufräumkriterien. Ein sequentieller Einzelzug ist kein Nachweis fehlender
Alternativen; produktive Linien müssen am gemeinsamen Vorzustand ermittelt sein.

Farbige Rätsel werden gemeinsam mit ihren echten Abstandsregeln untersucht.
Ein Ausschluss bei noch mehrwertiger Restdomain ist Fortschritt; er wird nicht
mit einer endgültig bestimmten Zelle gleichgesetzt. Zusätzliche Farben oder
mehr rohe Domainausschlüsse erhöhen die Stufe nicht automatisch. Unterschiedliche
Farben dürfen sich berühren; gleiche Nachbarfarben brauchen ihren Pflichtabstand.

## SD-D07 · Begrenzter Einfluss der Größe

Die Auswertung weist die logische Basisbewertung, den Größenbeitrag und die
resultierende Katalogstufe getrennt aus. Der Größenbeitrag kann höchstens in
die unmittelbar benachbarte höhere Stufe verschieben; er kann keine Stufe
überspringen und legt für große Rätsel keine Mindestschwierigkeit fest.

Vollständig mit R0 und flüssig lösbare Rätsel bleiben auch bei 50×50 auf Stufe 1.
Größe oder Eintragungsmenge allein begründen weder 4 noch 5. Die bereits hohe
logische Anforderung muss den höheren Katalogwert tragen; bloße Ausdehnung,
viele einfache Wiederholungen und lange offensichtliche Ketten genügen nicht.

Form des begrenzten Beitrags und genaue Übergangsgrenzen sind Liefergegenstand
von SD-B. Es wird kein unbegründetes Gewichtsverhältnis vorweg festgeschrieben.
SD-B prüft außerdem, ob besonders flüssige einfache R1-Überlappungen bereits
Stufe 1 verdienen. Das ist eine begrenzte bewusste Änderung gegenüber 0.1/0.2,
keine pauschale Gleichsetzung sämtlicher R1-Rätsel mit „Sehr leicht“.

## SD-D08 · Unabhängige Referenzen und feste Grenzen

Die Referenzbasis wird unabhängig vom heutigen Produktionskatalog kuratiert.
Gezielt konstruierte synthetische Rätsel müssen einfache und anspruchsvolle
Techniken, Engstellen, Mono/Farbe und unterschiedliche Größen abdecken. Die
erwartete fachliche Einordnung braucht jeweils eine nachvollziehbare Begründung.
Alle fünf Stufen, Grenzfälle sowie kleine schwierige und große sehr leichte
Beispiele werden vertreten; für Stufe 5 auch ein reiner Linienfall.

Der heutige Katalog wurde nicht gezielt zur Abdeckung der Skalenenden erstellt.
Er darf daher weder obere/untere Grenzen festlegen noch als unmittelbarer
Kalibrierungskorpus dienen. Keine Quantile, Gleichverteilung oder relativen Ränge
zur Besetzung aller Stufen. SD verlangt dafür auch keine neuen Produktionsmotive
oder künstlichen Bewertungsänderungen.

SD-B legt anhand der unabhängigen Referenzen die konkreten Zahlen, Formeln,
Rundungs-/Grenzregeln und begründete Auswahl fest. Die Methode samt Referenzstand
wird vor der Bestandsbewertung eingefroren. Neue Katalogeinträge verändern
weder diese Grenzen noch automatisch die Bewertung vorhandener Einträge.

Erst danach dient der reale Katalog einer ausdrücklich manuellen
Plausibilitätsprüfung am Bestand. Auffälligkeiten werden berichtet, nicht durch heimliches
Nachstellen von Schwellen beseitigt. Eine nötige Methodenkorrektur erhält eine
neue Version und gesonderte Freigabe zur betroffenen erneuten Bewertung.

Synthetische Referenzkalibrierung ist keine empirische menschliche Kalibrierung.
Vollständig geprüfte Instrumentierung ohne passende menschliche Vergleichsdaten
hat höchstens `confidence=medium`; Lösungszeit bleibt ohne belastbare Daten
ungeschätzt. Zusätzliche Eigentümer-Probespiele sind kein Pflichtgate.

## SD-D09 · Analyseinput und Bindungen

Bestandsbewertungen müssen nach dem Produktionscleanup aus den dauerhaft
vorhandenen Runtime-Definitionen ableitbar bleiben. Alte Bilder, ZIPs, Proofs
oder Produktionsläufe werden dafür nicht rekonstruiert. Ein vorgeschalteter
Adapter prüft die Eingangsbindung und trennt die Lösungsmatrix vom Analysator.

Der kanonische Analyseinput enthält nur Dimensionen, geordnete Hinweise,
Farb-/Leersemantik, Abstandsregeln und den vollständig unbekannten Startzustand.
Runtime-Farbnummern werden eindeutig und deterministisch abgebildet. Ursprüngliche
semantische Farb-IDs können nach Cleanup fehlen; der neue Analysehash darf
deshalb nicht als identischer historischer Produktions-Logikhash ausgegeben werden.

Ergebnisbindungen unterscheiden Rätsel-ID, Runtime-Revision, tatsächlichen
Definitions-Dateihash, kanonischen Analysehash, Methoden-/Konfigurationsversion
und Werkzeugstand. Eine unveränderte Logik kann trotz reiner Metadatenänderung
erneut gebunden werden; ein geänderter Hinweis, Modus, Zellwert oder ein anderes
Rastermaß benötigt die dafür vorgeschriebene neue Analyse und Inhaltsprüfung.

## SD-D10 · Kanonische Bewertungsquelle und Runtimeprojektion

Eine gesonderte versionierte Bewertungsquelle außerhalb der versiegelten
Produktionspakete wird autoritativ für die neue aktive Einstufung. Sie bindet
je Rätsel die geprüfte Eingabe, Methode, Rohmetriken, Basis-/Endstufe,
Größenbeitrag, Bewertungsart, Sicherheit, Begründung und relevante Nachweise.
Analyseergebnis, Übernahmeentscheidung und aktive Bewertung bleiben unterscheidbar.

Dateipfade, vollständige Schemas, Grenzen und konkrete CLI-Namen werden in den
Implementierungspaketen festgelegt. Dieser Vertrag behauptet keine bestehenden
Befehle und erlaubt keine frei erfundenen Felder in aktuellen Formatversionen.
Historische `production.difficulty`-Angaben und kompakte Integrationsbelege
bleiben unverändert; neue Bewertungen schreiben ihre ursprünglichen Freigaben
nicht um. Auswahl und Vorrang der neuen Quelle werden eindeutig implementiert.

Die Runtime erhält ausschließlich die für KE erforderlichen typisierten,
spoilerfreien Angaben. Keine Rohmetriken, Lösungshinweise, Motivbegründungen,
Proofs oder Produktionsunterlagen gelangen in den Spieler. Writer, Loader,
Validator und Recovery werden gemeinsam kompatibel fortgeschrieben; unbekannte
Methoden werden nicht still als bekannte interpretiert. Fehlend bleibt neutral
„Nicht eingestuft“ und ist weder 0 noch 5.

Reine Bewertungsänderungen ändern keine Runtime-Definition, ID, Slot, Revision,
Assets, Freigabebindung oder Savedatei. Der Cleanup erhält die neue kompakte
Bewertungsquelle und ihre Wiederholbarkeit, ohne alte Produktion aufzubewahren.

## SD-D11 · Expliziter wiederholbarer Ablauf

Ein zentraler manueller Werkzeugweg unterstützt genau ein Rätsel, eine ausdrücklich
gewählte Menge oder den ganzen Katalog. Einzel-, Bestands- und Integrationsweg
verwenden dieselben Regeln und Parameter, keine getrennten Bewertungsformeln.

1. Auswahl, Eingangsstand, Methodenversion und Budgets vor dem Lauf festhalten.
2. Nur die ausgewählten Definitionen analysieren; Ergebnisse und Grenzen in einem
   neuen Bericht ablegen. Der Bericht allein verändert keine aktive Einstufung.
3. Eine prüfbare Änderungsvorschau mit Alt-/Neuwerten, Gründen und Blockern erzeugen.
4. Nur gültige passend gebundene Ergebnisse innerhalb des erteilten Auftrags
   übernehmen; Eingaben und aktive Ausgangswerte vor Übernahme erneut vergleichen.
5. Bewertungsquelle und Runtimeprojektion konsistent übernehmen und die tatsächliche
   Änderung dokumentieren. Fremde oder zwischenzeitliche Änderungen nicht ersetzen.

Analyse und Übernahme dürfen zusammen beauftragt werden. Ein passender Auftrag
erfordert keine erneute Bestätigung pro Rätsel. Ohne Übernahmeauftrag bleibt es
beim Bericht; fehlende Einzelresultate werden nicht durch Schätzwerte aufgefüllt.
Keine Zeitplanung, CI-Auslösung, automatische Bewertung beim Spielstart oder
stillschweigende Neubewertung nach einer Katalog-/Werkzeugänderung.

## SD-D12 · Neue Rätsel und spätere Änderungen

Nach vollständiger Deduktionsprüfung des endgültigen Rasters entsteht die
Bewertung vor der redaktionellen Endfreigabe und Integration mit derselben
freigegebenen Methode. Der Bericht
gehört zur Produktionsübergabe; bei der Integration wird seine Eingangsbindung
geprüft. Ein bereits vollständiger passender Bericht wird wiederverwendet,
anstatt denselben Stand routinemäßig nochmals zu analysieren.

Der eingeführte Standard gilt ab SD-C für neue Integrationen. Die Behandlung
bereits versiegelter laufender Produktionen ergänzt ihre Bewertung außen und
erhält Originalhandoff, Inventar und echte Freigaben. Eine reine Neueinstufung
verlangt keine neue Bild-/Rasterproduktion oder zusätzliche Motiv-/Endfreigabe.
Titel-, Kategorie- oder Revealänderungen allein lösen keinen Logikanalyselauf aus.
Tatsächliche Inhaltsänderungen folgen weiterhin dem Authoring-/ZA-1-Vertrag.

## SD-D13 · Unvollständige und veraltete Ergebnisse

Abbruch, Ressourcenende, ungültiger Eingang, Fehler oder unvollständiger
Deduktionsnachweis sind keine Schwierigkeitsstufe. Budgets sind vorab festgelegt;
Messzeiten gehen nicht in die Stufe ein. Ein unvollständiger Versuch liefert
seinen Status, Grund und tatsächlichen Prüfumfang, niemals ersatzweise eine 5.

Ein fehlgeschlagener Wiederholungsversuch ersetzt keine weiterhin gültige aktive
Bewertung. Ist deren Eingangsbindung veraltet, darf sie nicht als aktuelle
Einstufung des geänderten Rätsels ausgegeben werden. Bei der Erstumstellung
bleiben fehlende/neue blockierte Bewertungen im Migrationsbericht sichtbar;
beibehaltene historische Schätzungen sind kein erfolgreicher 0.3-Abschluss.

## SD-D14 · Prüfung und Abnahme

Automatisierte Regressionen verwenden ausschließlich feste synthetische Inputs.
Verboten sind Tests am aktuellen Rätselkatalog, daraus kopierte Test-Snapshots,
automatische Bestands-Replays, fallweise wachsende CI-Listen und CI-Kalibrierung.
Ein neues Produktionsrätsel erweitert keinen Testbestand. Die ausdrücklich
manuelle Inhaltsanalyse ist davon getrennt und wird kein CI-Job.

SD-A/SD-B prüfen Regelkorrektheit, schwache Fixpunkte, synchrone Zusammenführung,
alle Stufen/Grenzen, partielle Farbdomains sowie Abbrüche. Gleicher Input und
gleiche Methode liefern gleiche Ergebnisse; Drehung/Spiegelung, Transposition
und reine Farb-ID-Umbenennung dürfen keine fachfremde Umstufung bewirken.
SD-C prüft Projektion, Fehler, Bindung und Save-Unverändertheit an künstlichen
Integrationen einschließlich abgeschlossener Produktion ohne alte Arbeitsdateien.

Technische Nachweise und getrenntes Review beziehen sich auf den konkreten
Head und seine Basis. Menschliches Probespielen ist optional; es wird keine
neue obligatorische Eigentümer-Spieldurchlaufabnahme eingeführt. Prüfgates der
betroffenen bestehenden Fachverträge werden durch SD nicht pauschal aufgehoben.

## SD-D15 · Pakete, Reihenfolge und Abschluss

| Paket | Eigenständiges Ergebnis | Voraussetzung für den Abschluss |
| --- | --- | --- |
| [SD-A · Analyse #236](https://github.com/venomenon328/picross/issues/236) | Definierte R0–R3-Regeln, synchrone Instrumentierung, Metriken und eigener nachvollziehbarer Analysebericht; bestehende Zertifizierung erhalten. | Synthetisch geprüfte Regeln, Farben, Fixpunkte, Zusammenführung und Abbruch; noch keine behauptete kalibrierte Katalogbewertung. |
| [SD-B · Referenzen und Methodenbindung #237](https://github.com/venomenon328/picross/issues/237) | Unabhängige synthetische Referenzbasis, begründete Grenzen, Größenbeitrag und eingefrorene vollständige Methode. | Alle fünf Stufen und Grenzfälle belegt; R0-Schutz, Linien-L5 und katalogunabhängige Grenzen erfüllt; Prüfentscheidung zu flüssigen R1-Fällen dokumentiert. |
| [SD-C · Katalog und Integration #238](https://github.com/venomenon328/picross/issues/238) | Kanonische Bewertungsquelle, kompatible KE-Projektion, manueller Übernahmeweg und derselbe Standard für neue Integrationen. | Synthetische Integrationsnachweise; ausdrücklich beauftragte erste Bestandsanalyse nach SD-B, dokumentierte Plausibilitätsprüfung und sichtbare Blocker. |

Reihenfolge: SD-A → SD-B → SD-C. Konkrete Issue-Bodies binden Scope,
Abhängigkeiten und Gates; PRs führen tatsächliche Änderungen und Prüfnachweise.
Bestandsanalyse, reine Metadatenübernahme und verbleibende Sonderfälle bleiben
von der technischen Werkzeugabnahme unterscheidbar. SD-C darf die anschließend
beauftragte Bestandsübernahme in einem eigenen Daten-PR auf der integrierten
Werkzeugbasis liefern; die Werkzeuglieferung allein schließt SD-C nicht ab.
Eine freie Methodennummer,
eine gefüllte Skala oder ein grüner Testlauf allein schließt SD nicht ab.
