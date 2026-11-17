# Schwierigkeit: gemeinsame Grundregeln und Methodenrouting

- Dokument-ID: `SD`.
- Status: aktive gemeinsame Fachregeln; 0.3 bleibt als historische Methode unterstützt.
- Dokumentstand: 17.11.2026.
- Zuständigkeit: Bedeutung der Bewertung, Deduktionsgrenzen, Versionierung und Auftragsscope.
- Normsprache: MUSS ist verpflichtend; DARF NICHT ist ein Verbot; DARF erlaubt eine Option.

## Pflichtquellen nach Aufgabe

| Aufgabe | Definierende Quelle |
| --- | --- |
| Aktuelle Methode 0.4 verstehen | [SD2](PUZZLE_DIFFICULTY_V2.md) |
| 0.4-Regeln, Rohprofile oder Analyseformate ändern/prüfen | [SD2-Analyzer](SD2_ANALYZER.md) |
| 0.4-Formel, Referenzen, Ergebnisformat oder Freeze prüfen | [SD2-Kalibrierung](SD2_CALIBRATION.md) |
| Historische Methode 0.3 lesen oder ausdrücklich analysieren | [SD-Analyzer](SD_ANALYZER.md) und [SD-Kalibrierung](SD_CALIBRATION.md) |
| Ratinghüllen, Auswahlberichte oder Defaultrecord lesen | [SD2-Integration](SD2_INTEGRATION.md) |
| Aktuelle Bewertungen übernehmen oder Katalogquellen prüfen | [SD-Catalog](SD_CATALOG.md) |
| Erstintegration oder gezielte Editorpflege durchführen | [RI](../production/PUZZLE_INTEGRATION.md) beziehungsweise [Editor §13](../tools/PUZZLE_EDITOR.md#13-pe-edit2-gezielte-pflege-statt-vollbestandsprüfung) |

Der Produktionsstandard ist der gültige Record in
[`content/difficulty-method.json`](../../content/difficulty-method.json), derzeit
`picross-difficulty-0.4`. Ein expliziter Analyseaufruf kann eine andere unterstützte
Methode wählen. Die Unterscheidung zwischen Produktionsdefault und CLI-Default
ist in SD2-Integration definiert.

## SD-D01 · Ziel und Bedeutung der Skala

Eine vollständige Einstufung MUSS eine begründete, wiederholbare Stufe von 1 bis 5
liefern. Sie beschreibt den modellierten menschlichen Lösungsanspruch. Sie
bewertet keine Spielerleistung und verändert weder Fehler, Undo, Sterne noch
Progression. Arbeitsumfang, Rechenaufwand und mögliche Lösungszeit sind
unterschiedliche Größen.

Alle fünf Stufen MÜSSEN mit nachvollziehbaren Referenzen erreichbar sein;
Stufe 5 auch durch reine Linienlogik. Der echte Katalog muss nicht jede Stufe
enthalten. Mengenquoten, Zwangsverteilungen und automatische Streckung sind
unzulässig. Die fachlichen Orientierungen der aktuellen Methode stehen allein
in [SD2 §2](PUZZLE_DIFFICULTY_V2.md#2-bedeutung-der-bewertung), ihre exakte
Zuordnung im jeweiligen Zahlenvertrag. Namen, Farbkreise und Darstellung
gehören zur [Katalogdarstellung](../game/CATALOG_PRESENTATION.md).

## SD-D02 · Versionierung und gezielte Ablösung

Eine Methode MUSS ihren Regelsatz, ihre Messdefinitionen, Aggregation, Grenzen,
Referenzen und exakte Konfigurations-/Quellbindung eindeutig festlegen. Diese
Bindung MUSS vor der Bestandsanwendung eingefroren sein. Bewertungswirksame
Änderungen benötigen eine neue Methodenidentität und einen ausdrücklichen
Neubewertungsauftrag. Ein neuer Hash unter derselben eingefrorenen Identität
legitimiert keine Änderung.

0.3 und 0.4 bleiben getrennte, unverändert prüfbare Methoden. Historische
0.1-/0.2-Werte behalten ihre Bedeutung im noch unterstützten Projektions- und
Berichtsreader; sie werden weder rückwirkend instrumentiert genannt noch als
0.3/0.4 umetikettiert. Daraus folgt keine Unterstützung früherer Produktions-,
Export- oder Recoverygenerationen. Die tatsächliche Readergrenze steht in
[SD2-Integration](SD2_INTEGRATION.md).

## SD-D03 · Zertifizierung und Bewertung getrennt prüfen

Zulässige Deduktion und deren Schwierigkeitsbewertung MÜSSEN getrennt geprüft
werden. Der bestehende Solver-/Verifiervertrag aus
[Rätselproduktion](../production/PUZZLE_PRODUCTION.md) bleibt maßgeblich; der Spieler erhält
keinen Solver und berechnet keine Schwierigkeit zur Laufzeit.

Der Bewertungsanalysator MUSS vom vollständig unbekannten Raster ausgehen.
Er DARF ausschließlich Hinweise, Dimensionen und echte Farb-/Abstandsregeln als
Deduktionsprämissen verwenden. Zielmatrix, Motivwissen, vermutete Symmetrie,
Vorbelegung, Eindeutigkeitsannahmen, Suchzweige und probeweise Spielfortsetzungen
sind als Prämissen unzulässig.

Die Bewertungsspur hat einen eigenen versionierten Vertrag. Eine absichtlich
schwächere Bewertungsregel DARF NICHT die vollständigen Ausschlussanforderungen
eines Zertifizierungsproofs lockern. Die Korrektheit eines Schlusses und seine
Zuordnung zu einer einfachen Regel sind getrennte Fragen. Solverflags oder
passende Endzellen allein belegen weder Techniknotwendigkeit noch Stufe.

## SD-D04 · Nachgewiesener Technikbedarf

Die endlichen Regellisten und ihre genaue Familienzuordnung stehen allein in
[SD-Analyzer](SD_ANALYZER.md) für R0–R3 und
[SD2-Analyzer](SD2_ANALYZER.md) für E0–E3. Ein verdeckter Aufruf vollständiger
Linienlogik DARF NICHT als einfache Regel ausgegeben werden.

Schwächere Familien MÜSSEN bis zum Fixpunkt ausgeschöpft sein, bevor eine stärkere
als erforderlich gilt. Nach stärkerem Fortschritt beginnt die Prüfung wieder
schwach. Diese Notwendigkeit bezieht sich auf den definierten Regelsatz, nicht
auf jede denkbare menschliche Strategie. Höchste benötigte Familie und ihre
Häufigkeit bleiben unterscheidbar.

Erforderliches R4 MUSS durch die separat unabhängig bestätigte `full-line-*`-
Baseline mit `stalled` und einen vollständigen geprüften Paarproof derselben
Logik belegt sein; der eigene Analysefixpunkt MUSS ebenfalls `stalled` sein.
Profilwahl, einzelner Paarschritt, Suchurteil oder Baselineabbruch genügen nicht.
Notwendiges R4 bedeutet L5 und „linienübergreifend / besonders hoher logischer
Anspruch“. Die konkreten Berichtsfelder und Präfixgrenzen stehen in den
Analyzer-/Zahlenverträgen. Ein vollständig gelöster Linienfall benötigt keinen
routinemäßigen Paar- oder Suchlauf. [Paarlinien](../production/PAIRED_LINES.md) definiert die
Proofsemantik, die Katalogdarstellung die sichtbare Darstellung.

## SD-D05 · Synchrone Bewertungswellen

Eine Welle MUSS alle Schlüsse derselben betrachteten Stärke am unveränderten
Vorzustand bestimmen und anschließend gemeinsam übernehmen. Mehrfach
begründete Zelländerungen und identische Ausschlüsse zählen jeweils einmal.
Schlüsse innerhalb derselben Welle dürfen nicht voneinander abhängen.
Regelreihenfolge, Zusammenführung und Abschluss MÜSSEN deterministisch sein.

Quellenreihenfolge, Threadplanung, Plattform oder Wörterbuchiteration dürfen
das Ergebnis nicht verändern. Die methodenspezifischen Analyzer definieren
Ausgabeordnung, Widerspruchsvorrang und atomare Abbruchgrenzen. Bewertungswellen
ändern keine bestehenden Proofbytes oder deren Verifikation. CPU-Zeit,
FIFO-Aufrufe, beliebige Proofschrittzahlen und bloße Wiederholung offensichtlicher
Schritte sind keine Schwierigkeitsskala.

## SD-D06 · Messwerte und Engstellen

Berichte MÜSSEN Technikbedarf, Fortschrittsangebot, Informationsgewinn, Verlauf,
Engstellen und Umfang getrennt ausweisen. Die jeweiligen Analyzer definieren
alle Zähler, Nenner, Nullfälle und Zustandsgrenzen; die Zahlenverträge definieren
alle bewertungswirksamen Schwellen. Eine sequentielle Einzelzugfolge belegt
keine fehlenden Alternativen: Das Angebot MUSS am gemeinsamen Vorzustand
ermittelt werden.

Partielle Farb-Domainverluste sind Fortschritt, aber keine neu bestimmten
Zellen. Ereignissummen und unterschiedliche Positionen bleiben getrennt.
Zusätzliche Farben und mehr rohe Ausschlüsse dürfen keinen pauschalen Aufschlag
erzeugen. Unterschiedliche Nachbarfarben dürfen sich berühren, gleiche Farben
benötigen ihren Pflichtabstand.

## SD-D07 · Begrenzter Einfluss der Größe

Die Bewertung MUSS Basis, Umfangsbeitrag und Endstufe getrennt ausweisen. Der
reine Umfangsbeitrag DARF höchstens um eine unmittelbar benachbarte Stufe
anheben und keine Mindestschwierigkeit allein aus der Größe erzeugen.
Unmittelbar und flüssig lösbare Fälle bleiben auch bei 50×50 auf Stufe 1.
Größe, Eintragungsmenge oder einfache Wiederholung allein begründen weder 4 noch 5.

0.3 verwendet die flächenbezogene Formel und die flüssige R1-Ausnahme aus
[SD-Kalibrierung](SD_CALIBRATION.md#numerischer-vertrag--nach-referenzfestlegung-vor-bewertungsimplementierung).
0.4 verwendet die getrennten Denk-/Such-/Umfangsbeiträge aus
[SD2-Kalibrierung §5](SD2_CALIBRATION.md#5-exakter-zahlenvertrag-sd2-rating-formula-1).
Diese Formeln dürfen nicht kombiniert oder zwischen Methoden übertragen werden.

## SD-D08 · Unabhängige Referenzen und feste Grenzen

Referenzen MÜSSEN unabhängig vom Produktionskatalog konstruiert und vor der
finalen Parameterwahl fachlich begründet werden. Sie decken Techniken,
Engstellen, Mono/Farbe, unterschiedliche Größen, Grenzfälle, kleine schwierige
und große sehr leichte Fälle ab. Die verbindlichen Referenzsätze und ihre
Methodenbindung stehen in den jeweiligen Kalibrierungsdokumenten.

Katalogquantile, Gleichverteilung oder relative Ränge dürfen keine Grenzen
festlegen. Neue Einträge verändern weder Parameter noch andere Bewertungen.
Ein ausdrücklich beauftragter realer Bestandsvergleich dient allein der
Plausibilitätsprüfung. Auffälligkeiten MÜSSEN berichtet werden; sie rechtfertigen
keine stille Nachkalibrierung, künstlichen Noten oder zusätzlichen Produktionsmotive.

Synthetische Referenzen sind keine empirische menschliche Kalibrierung.
Vollständig geprüfte Instrumentierung ohne passende menschliche Vergleichsdaten
hat höchstens `confidence=medium`; Lösungsminuten bleiben ungeschätzt.
Menschliches Probespielen ist optional und kein zusätzliches Pflichtgate.

## SD-D09 · Analyseinput und Bindungen

Bestandsanalysen MÜSSEN aus den aktuellen dauerhaften Definitionen möglich sein.
Alte Bilder, ZIPs, Proofs oder Produktionsläufe werden dafür nicht rekonstruiert.
Der Eingangsadapter prüft die Bindung und trennt die Lösungsmatrix vom Analyzer;
eine ausdrücklich benötigte R4-Prüfung behält ihre passenden eigenen Belege.

Der kanonische Analyseinput enthält Dimensionen, geordnete Hinweise,
Farb-/Leersemantik, Abstandsregeln und den unbekannten Startzustand. Runtime-
Farbnummern werden deterministisch abgebildet. Der neue Analysehash darf nicht
als identischer historischer Produktions-Logikhash ausgegeben werden.

Arbeitsbelege unterscheiden ID, Runtime-Revision, tatsächlichen Definitionshash,
Analysehash und Methoden-/Konfigurationsbindung. Werkzeugidentität gehört nur
in die dafür definierten Arbeitsformate. Aktuelle Integration fordert keine
historischen Producer-/Werkzeugdateien. Rebind verlangt unveränderte Logik,
Matrix, ID und Modus. Geänderte Hinweise, Zellwerte, Maße oder Modus verlangen
die dafür vorgesehene neue Analyse und Inhaltsprüfung.

## SD-D10 · Kanonische Bewertungsquelle und Runtimeprojektion

[SD-Catalog](SD_CATALOG.md) definiert allein die aktive Quelle, Quellenpriorität
und aktuellen Übernahme-/Transaktionsweg. Analysebefund, Übernahmeentscheidung
und aktive Bewertung bleiben unterscheidbar. Die Runtime erhält ausschließlich
die definierte kleine spoilerfreie Projektion: keine Rohmetriken, Lösungshinweise,
Motivbegründungen, Proofs oder Produktionsunterlagen.

Unbekannte Methoden dürfen nicht als bekannte interpretiert werden. `null` in
einer dafür zugelassenen Projektion bedeutet „Nicht eingestuft“, niemals 0 oder 5.
Das ist kein Fallback für eine fehlende oder defekte heute erforderliche Ratingdatei.
Reine Neubewertung verändert keine Definition, ID, Slot, Rätselrevision, Bilder,
Kategorie, Added-Daten, historischen Freigaben oder Saves.

## SD-D11 · Expliziter wiederholbarer Ablauf

Einzelanalyse, ausdrücklich gewählte ID-Menge und Kataloganalyse MÜSSEN dieselben
Methodenregeln verwenden. Auswahl, Eingangsstand, Methode und Budgets stehen
vor dem Lauf fest. Analyse und Vorschau schreiben keine aktive Bewertung.
Die Vorschau nennt Alt-/Neuwert, Gründe, Grenzen und Blocker.

Übernahme DARF nur innerhalb des erteilten Auftrags und mit unveränderten
geprüften Eingängen/Ausgangswerten erfolgen. Bewertung und Runtimeprojektion
MÜSSEN konsistent sein. Fremde Änderungen bleiben erhalten. Ein kombinierter
Analyse-/Übernahmeauftrag benötigt keine zusätzliche Bestätigung pro Rätsel;
ohne Übernahmeauftrag bleibt es beim Bericht. Keine Zeitplanung, CI-Auslösung,
Bewertung beim Spielstart oder stille Neubewertung durch Werkzeugänderung.

## SD-D12 · Neue Rätsel und spätere Änderungen

Das endgültige Raster benötigt nach vollständiger Deduktionsprüfung und vor
redaktioneller Endfreigabe/Integration eine passende Bewertung der aktiven
Produktionsmethode. Ein bereits vollständiger passender Arbeitsbericht wird
wiederverwendet. Die aktuellen Nutzdaten und Bindungen, nicht die frühere
Produktionsgeschichte, sind der Integrationseingang.

Reine Neueinstufung verlangt keine neue Bild-/Rasterproduktion oder Motivfreigabe.
Titel-, Kategorie-, Reveal- und Hintergrundpflege allein lösen keine Logikanalyse
aus. Erstintegration folgt [RI](../production/PUZZLE_INTEGRATION.md), gezielte Inhaltsänderung
dem [Editor](../tools/PUZZLE_EDITOR.md), Produktionsschritte dem
[Authoring](../production/authoring/PUZZLE_AUTHORING.md). Bestehende historische Unterlagen
werden durch die neue Bewertung nicht umgeschrieben.

## SD-D13 · Unvollständige und veraltete Ergebnisse

Abbruch, Ressourcenende, ungültiger Eingang, technischer Fehler und fehlender
vollständiger Deduktionsnachweis sind keine Stufe. Ein unvollständiger Versuch
MUSS Status, Grund und tatsächlichen Prüfumfang liefern, niemals ersatzweise L5.
Ein fehlgeschlagener Versuch ersetzt keine weiterhin gültige aktive Bewertung.
Eine veraltete Eingangsbindung darf jedoch nicht als aktuell ausgegeben werden.
Offene Fälle bleiben im Bericht sichtbar; beibehaltene Altwerte sind kein
Erfolg der neu beauftragten Methode.

## SD-D14 · Prüfung und Abnahme

Automatische Regressionen verwenden feste unabhängige synthetische Inputs.
Tests am realen Katalog, kopierte Katalogsnapshots, automatische Bestandsreplays,
fallweise wachsende CI-Listen und CI-Kalibrierung sind unzulässig. Ein neues
Produktionsrätsel erweitert keinen Testbestand. Ausdrücklich manuelle
Inhaltsanalyse bleibt davon getrennt.

Zu prüfen sind Regelkorrektheit, schwache Fixpunkte, synchrone Zusammenführung,
Stufen/Grenzen, partielle Farbdomains, Abbrüche und tatsächlich betroffene
Integrationsbindungen. Vollständige gleiche Eingänge/Methode liefern gleiche
Ergebnisse; Drehung/Spiegelung, Transposition und reine Farb-ID-Umbenennung
verändern keine skalare Einstufung. Technische Nachweise und separates Review
beziehen sich auf konkrete Heads/Basen. Aktuelle Prüfauswahl und Befugnisse
gehören zum [CI-Vertrag](../ci/CI_WORKFLOW_V2.md) und [Workflow](../dev-rules/WORKFLOW.md).

## SD-D15 · Historische Lieferung

Der [feste frühere Dokumentstand](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/PUZZLE_DIFFICULTY.md)
erhält SD-A/B/C, erste Bestandsübernahme und frühere Darstellungsentscheidungen.
Er ist keine zusätzliche aktive Normquelle. Die konkreten Methoden sind allein
in ihren unveränderten Analyzer-/Kalibrierverträgen definiert.
