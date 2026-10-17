# SD-B: Referenzen und Bewertungsvertrag 0.3

Stand: 17.10.2026 · SD-B/#237 · Referenzfestlegung vor Parameterentscheidung

Dieses Paket ergänzt den [SD-A-Analysator](SD_ANALYZER.md) gemäß
[SD-Fachvertrag](PUZZLE_DIFFICULTY.md). Ausschließlich technische synthetische
Referenzen; keine Kataloganalyse, Übernahme oder SD-C-Integration.

## Referenzfestlegung

Der feste [Referenzsatz](../tools/puzzle_production/difficulty_references_0_3.json)
enthält vollständige Hinweise, kanonischen Logik-/Analysehash, Herkunft,
Auswahlgrund und vor der endgültigen Parameterwahl festgelegte Erwartung.
Die Auswahl beurteilt Technik und Verlauf, nicht einen vorher berechneten Score.
Die Referenzzahlen sind fachliche Modellanker, keine menschlichen Messungen.

| Referenz | Erwartung | Fachliche Begründung |
| --- | --- | --- |
| direct-50 | 1 | 50×50, ausschließlich direkte Voll-/Leerlinien. |
| fluid-r1 | 1, zu untersuchende Ausnahme | Direkte Ränder, dann flüssige Überlappung mit breitem Angebot. |
| local-combination | 2 | Eine breite kombinierte Schlusswelle bestimmt den kleinen Rest. |
| sustained-combination | 3 | Wiederholt kombinierte Deduktion bei weiterhin mehreren Möglichkeiten. |
| color-combination | 3 | Gemeinsame Farblogik mit partiellen Domains und breitem Fortschritt. |
| repeated-narrow | 4 | Wiederkehrende enge kombinierte Fortschritte; hohe Anforderung ohne R3-Zwang. |
| late-general-line | 5 | Kleines 8×7, allgemeine Linienlogik an einer ausgeprägten späten Engstelle. |
| required-pair | 5 | Separat zu prüfender notwendiger Paarliniennachweis. |

Die getrennten Vergleichsfälle `stalled-general` und `color-pair` kontrollieren
Vollständigkeit und farbige R4-Bindung. Sie bestimmen keine Schwellen.
`direct-50` und `fluid-r1` sind neu konstruierte geometrische Muster. Die vier
neuen unregelmäßigen Muster stammen aus einer begrenzten technischen
Entwicklungsuntersuchung mit Seed 237 (2400 kleine Kandidaten, keine Scorefunktion).
Die R3-Referenz stammt aus einer einzelnen Zelländerung des nachweislich
synthetischen SD-A-Regeltests. Schon die erste passende Variante genügte;
es wurde kein vorhandener Katalogeintrag gelesen oder kopiert. Die exakten
Hinweise sind der dauerhafte Referenzinput, nicht ein künftig erneut gestarteter
Zufallsgenerator. Entwicklungssuche und Parameterwahl laufen niemals in CI.

## Vorab festgelegter Datei-, Hash- und CLI-Vertrag

Der bestehende Aufruf `analyze-difficulty` erhält ausdrücklich
`--method picross-difficulty-0.3`. Ohne diese Option bleibt der unkalibrierte
SD-A-Pfad einschließlich frei gewählter `--parameters` erhalten. Mit Methode
sind nur deren exakt gebundene Analyseparameter zulässig. Unbekannte Methoden
und abweichende Parameter sind Fehler, kein stiller Fallback.

Das neue Bundle enthält zusätzlich `rating.json` im Format
`picross-difficulty-rating-v1`. `report.json` und sämtliche v1-Spuren bleiben
unverändert unter ihrem bisherigen Vertrag lesbar. Das Rating hat exakt:

- `format`, `method` (vollständiger eingefrorener Methodensatz), `method_hash`;
- `analysis_result_hash` (kanonischer Hash des vollständig geprüften v1-result),
  `source` (exakte bestehende Quellbindung einschließlich Dateibytes/Revision);
- `result` (Status, Grund, Logikbasis, Umfang, Größenbeitrag, Endstufe und
  Aussagegrenzen) und `rating_hash`.

`rating_hash` ist SHA-256 der kanonischen JSON-Bytes des gesamten Objekts **ohne**
`rating_hash`. Kanonisierung entspricht dem bestehenden Produktionsvertrag:
sortierte Schlüssel, keine Leerzeichen, UTF-8 ohne BOM/Abschlusszeile,
keine nichtendlichen Zahlen. Gespeicherte Dateien haben eine LF-Abschlusszeile.
Rationale Zahlen werden als gekürzte `[Zähler,Nenner]` mit positivem Nenner
gespeichert. Keine gerundeten Fließkommazahlen in Bewertung oder Grenzvergleich.

Der Methodensatz bindet ID, Analyzer, Regeln, exakte Parameter, eigene
Bewertungsaggregation und Referenz-ID/-Hash. Der Prüfer kennt genau den
eingefrorenen Satz; ein bloß neu berechneter Hash legitimiert keine Änderung.
`check-analysis --method picross-difficulty-0.3` verlangt das Rating, prüft
zuerst das gesamte SD-A-Bundle einschließlich Eingangs-, Spur-, Metrik- und
optionaler R4-Bindungen unabhängig neu und rekonstruiert dann das komplette
Rating. Fehlende, fremde oder zusätzliche Felder sind Fehler. Keine Pfade aus
Ratings werden geöffnet. Ohne Methode bleibt die v1-Prüfung verfügbar und
beansprucht ausdrücklich keine Ratingprüfung. Ratingdateilimit: 64 KiB.

Nur ein geprüftes `solved` oder übereinstimmendes `stalled` mit separat frisch
bestätigter vollständiger Paarableitung **und** notwendigem R4 erhält eine
Stufe. `deduction_complete` allein genügt nicht. Alle anderen gültigen
Teilberichte erhalten `unrated`, null für Stufe/Vertrauen und einen Grund.
Ungültige Eingänge oder fehlgeschlagene Verifikation erzeugen kein Rating.
R4-Proofschritte werden keine Linienwellen. Zeit und Betriebszähler gehören
nicht zur Bewertungsidentität. Gültige Bewertungen sind `instrumented` mit
`confidence=medium`, ohne geschätzte Minuten oder menschliche Validierungsbehauptung.

Die numerische Aggregation und endgültige R1-Entscheidung werden nach dieser
Referenz-/Formatfestlegung im selben Paket begründet und eingefroren.
