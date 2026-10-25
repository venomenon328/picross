# SD-B: Referenzen und Bewertungsvertrag 0.3

**SD2 · 25.10.2026:** [Die neue Spezifikation](PUZZLE_DIFFICULTY_V2.md) / #402
verlangt breite unabhängige Referenzen, getrennte Validierungsfälle und drei
Teilwerte für eine neue Methode. SD2-B (#404) liefert den separaten
[numerischen Vertrag und Freeze](SD2_CALIBRATION.md) in Draft-PR #409.
Die hier beschriebene Methode 0.3 samt gebundenen Quelldateien,
Referenzen, Formeln und Hashes bleibt unverändert aktiv; 0.4 bleibt inaktiv.
Keine stillschweigende Nachkalibrierung oder Neubewertung durch diese Freigabe.

Stand: 17.10.2026 · Vertrag 1.0 · eingefrorener Methodensatz zu SD-B/#237

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
Bewertungsaggregation, Referenz-ID/-Hash und Kalibrierungs-ID/-Hash. Der Prüfer kennt genau den
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

## Numerischer Vertrag · nach Referenzfestlegung, vor Bewertungsimplementierung

Alle folgenden Werte sind rationale Zahlen; Vergleiche sind exakt, ohne
Rundung oder Epsilon. Das Profil heißt `sd-rating-aggregation-1` und verwendet
ausschließlich die geprüften SD-A-Rohmetriken mit `parameters={aggregation:null}`.
Die beliebige SD-A-Aggregation wird nicht als kalibrierter Default interpretiert.

Für jede produktive Welle w seien f ihre Familie als 0…3, O die offenen Zellen,
P produktive und L offene Linien beider Achsen zusammen. Dann gilt:

- Angebot q=P/L. Bereits gelöste Linien sind aus L ausgeschlossen.
- Informationsgewinn g=(Σ (a−b)/(a−1))/O über die **einmalig zusammengeführten**
  Zelländerungen mit Domain-Kardinalitäten a vorher und b nachher. Ein neues
  Singleton trägt 1, ein partieller Domainverlust strikt zwischen 0 und 1 bei.
  Unveränderte Zellen tragen 0 bei. O und L sind bei produktiven Wellen positiv.
  Doppelte Linienquellen sind keine zusätzlichen Zelländerungen.
- Lokale Enge e=(1−q)(1−g) für f≥2, sonst 0. Wenige produktive Linien bei
  großer gleichzeitiger Auflösung oder viele Alternativen ergeben keine starke
  Enge. Die Werte liegen einschließlich beider Enden in [0,1].
- Eine Engstellenwelle hat f≥2, q≤1/4 **und** g≤1/4. C zählt sie. D ist die
  längste unmittelbar zusammenhängende Folge solcher Wellen; jede andere
  Welle unterbricht eine Folge. Phasenzahl wird zusätzlich berichtet.
- B=min(1, max(e, Standard 0) + min(C,4)/32 + min(D,4)/32).
  Der lokale Spitzenwert erhält Gewicht 1; Häufigkeit und Dauer jeweils
  höchstens 1/8. Frühe einfache Arbeit kann eine späte Engstelle nicht verdünnen.
  Einfache Wellenzahl oder CPU-Zeit sind keine Bewertungsterme.
- S=Σ entfernte Domainwerte in Wellen f≥2 / (N·K), mit N=Breite·Höhe und
  K=Anzahl Vordergrundfarben. Damit zählt der **gesamte** monotone
  Informationsverlust je Zelle höchstens 1, unabhängig von K. Der einfache
  Informationsanteil ist bei vollständigen Linienfällen 1−S. Die bestehenden
  Singletonanteile werden im SD-A-Bericht daneben erhalten; sie sind andere Maße.
- Restaufräumen ist der maximale finale Suffix ausschließlich aus R0-Wellen
  eines gelösten Linienlaufs. Er wird berichtet, hat aber ebenso wie sämtliche
  anderen R0-Wellen Gewicht 0 in der Enge. Keine absolute Restzellschwelle.

Es gibt keine künstlichen Nullwellen. Für eine leere Folge gelten C=D=B=S=0
und keine Phase. Undefinierte SD-A-Anteile `[0,0]` werden nie dividiert oder als
einfache Nullanteile interpretiert; unvollständige Fälle erhalten keine Stufe.
Bei einem vollständig gelösten gültigen Raster ist N·K immer positiv.

Die **logische Basis L** wird in folgender Reihenfolge bestimmt:

| Bedingung | L |
| --- | --- |
| Unabhängig erforderliches R4 | 5, eigene Kennzeichnung; kein vollständiges Linienprofil behauptet |
| Höchste Familie R0 | 1 |
| Höchste Familie R1 und in jeder R1-Welle q≥1/2 **oder** g≥1/2 | 1 |
| Sonst höchste Familie R1 | 2 |
| Höchste Familie R2, S≤1/8 und jede R2-Welle mit q≥1/2 **und** g≥1/2 | 2 |
| Sonst höchste Familie R2 und B<3/4 | 3 |
| Sonst höchste Familie R2 | 4 |
| Höchste Familie R3 und B<3/4 | 4 |
| Sonst höchste Familie R3 | 5 |

Damit ist die begrenzte R1-Untersuchung entschieden: besonders flüssige R1-Fälle
fallen in 1. `fluid-r1` hat im entscheidenden Schritt Angebot 1 und Gewinn 8/9.
R1 bleibt sonst höchstens 2; viele einfache Wellen erzeugen keine 4/5.
Auch ein einzelner lokaler, breiter R2-Restschritt erzwingt nicht automatisch 3.
Diese Ausnahme verlangt sowohl einen kleinen gesamten Informationsanteil als
auch tatsächlich breite und ergiebige starke Wellen. R3 hat keine solche Ausnahme.

**Größe:** z=min(1/4, max(0,(N−100)/6400)). Die Größe hängt nur von der Fläche
ab, ist unter Achsentausch invariant und bevorzugt keine Orientierung. z ist
0 bis einschließlich 100 Zellen und erreicht bei 1700 Zellen die Kappung 1/4.
Der ganzzahlige Zusatz A ist genau 1, wenn eine der folgenden Bedingungen gilt,
sonst 0:

1. L=2 und z≥1/8 (ab 900 Zellen).
2. L∈{3,4}, höchste Linienfamilie mindestens L−1, B≥1/2 und B+z≥3/4.

Endstufe=L+A. Für L=1 und L=5 gilt immer A=0, ebenso für erforderliches R4.
R2 kann durch Größe keine 5 erhalten. Eine größenbedingte Anhebung auf 4/5
benötigt bereits ein starkes logisches Profil mit B≥1/2 sowie die entsprechende
Technik; Umfang allein genügt nicht. An jeder Gleichheit gilt ausdrücklich der inklusive Vergleich
der Formeln. Es gibt keine kaufmännische Rundung, Interpolation oder Quantile.

## Parameterentscheidung und Alternativen

Die Schwellen bilden nachvollziehbare grobe Unterschiede: mindestens die Hälfte
der Linien oder Restinformation für flüssiges R1; bei der lokalen R2-Ausnahme
beides und höchstens ein Achtel der Gesamtinformation. Ein Viertel begrenzt
gleichzeitig knappes Angebot und geringen Fortschritt. B=3/4 trennt markante
Enge von normalen Kombinationen; die begrenzten Wiederholungs-/Daueranteile
lassen wiederkehrende Engstellen relevant werden, ohne lange einfache Ketten
zu bestrafen. Die Größenwirkung ist auf ein Viertel des Engeintervalls und
eine einzige Nachbarstufe begrenzt; 10×10 ist die umfangsneutrale Basis.

Verworfen: alleinige höchste Familie (keine Verlaufsunterscheidung, lokales R2
überbewertet), globaler Durchschnitt (späte Engstelle verdeckt), bloße Zahl
produktiver Wellen (lange einfache Ketten überbewertet), feste Zahl produktiver
Linien ohne Nenner (formatabhängig) und reine Zellzahl-Mindeststufe.
Ein ausschließliches Engstellenmaximum ignoriert Wiederholung; unbeschränkte
Addition würde Umfang doppelt gewichten. Schärfere oder weichere Grenzwerte
bleiben andere denkbare Modelle, keine empirisch ausgeschlossenen Alternativen.
Gezielte Gegenproben unmittelbar unter/auf/über allen Grenzen sichern die
hier gewählte Entscheidung, ohne Referenzetiketten nachträglich anzupassen.

Der vollständige `result` hat exakt `status`, `reason`, `assessment_type`,
`logical_level`, `size_pressure`, `size_adjustment`, `level`, `confidence`,
`estimated_minutes`, `r4_required`, `logical_demand`, `profile`, `workload`,
`uncertainty`, `explanation`. `workload` hat `width`, `height`, `cells`.
Bei `rated` ist `reason=null`, `assessment_type=instrumented`, `confidence=medium`;
Stufen sind Ganzzahlen 1…5. `estimated_minutes` ist immer null. Bei `unrated`
sind Profil, Stufen, Größenwerte, Bewertungsart und Vertrauen null; mögliche
Gründe sind `analysis_aborted`, `line_contradiction`, `r4_necessity_unproven`
oder `analysis_incomplete`. Ungültiger Eingang/Prüffehler ist kein gültiges Rating.

Das Linienprofil hat exakt `highest_family`, `strong_information_fraction`,
`simple_information_fraction`, `peak_strain`, `bottleneck_waves`,
`bottleneck_phases`, `longest_bottleneck`, `recurrence_bonus`, `demand`,
`cleanup_suffix_waves`, `fluent_r1`, `localized_combination`. Bei R4 ist es null.
`uncertainty` trennt `model=rule_based_estimate`,
`human_calibration=not_performed` und `technical=verified_complete|incomplete`.
`logical_demand` ist nur bei erforderlichem R4 dessen bestehende Kennzeichnung,
sonst null. `explanation` nennt feste Formelresultate, keine Lösungszeit.

Der endgültige Freeze bindet zusätzlich die exakten SHA-256-Quellbytes der
beteiligten Analyse-/Prüf-/Bewertungsmodule. Geänderte Quellen werden unter
derselben eingefrorenen Identität zurückgewiesen. Hashes sind Bindungen, keine
Signaturen oder unabhängige fachliche Abnahme.

## Ergebnisse und Freeze

Die [gespeicherten Kalibrierungsbelege](../tools/puzzle_production/difficulty_calibration_0_3.json)
binden je Fall Analysehash, Spurhash, Metrikhash, Familienhäufigkeiten und das
vollständige Ratingresultat. Die unabhängige Spurprüfung und die getrennte
R4-Prüfung liefen tatsächlich; die allgemeinen Tests reproduzieren diese festen
Belege und prüfen Dateibundles frisch. Keine automatische Parametersuche.

| Fall | Fläche | Höchste Familie | Starker Informationsanteil S | Enge B | Engstellen C / längste Folge D | Basis + Größe = Stufe |
| --- | --- | --- | --- | --- | --- | --- |
| direct-50 | 2500 | R0 | 0 | 0 | 0 / 0 | 1 + 0 = 1 |
| fluid-r1 | 25 | R1 | 0 | 0 | 0 / 0 | 1 + 0 = 1 |
| local-combination | 42 | R2 | 1/14 | 0 | 0 / 0 | 2 + 0 = 2 |
| sustained-combination | 90 | R2 | 2/15 | 6/77 | 0 / 0 | 3 + 0 = 3 |
| color-combination | 42 | R2 | 47/84 | 4/81 | 0 / 0 | 3 + 0 = 3 |
| repeated-narrow | 72 | R2 | 1/3 | 893/1008 | 4 / 2 | 4 + 0 = 4 |
| late-general-line | 56 | R3 | 2/7 | 1 | 4 / 3 | 5 + 0 = 5 |
| required-pair | 16 | R4 separat belegt | kein vollständiges Linienprofil | – | – | 5 + 0 = 5 |
| stalled-general (Vergleich) | 56 | R3 benutzt, unvollständig | keine Bewertung | – | – | keine Stufe |
| color-pair (Vergleich) | 20 | R4 separat belegt | kein vollständiges Linienprofil | – | – | 5 + 0 = 5 |

Die Hälfte-/Achtelgrenzen trennen 1/2 und 2/3 anhand von flüssigem Angebot und
lokalem gegenüber wiederholtem Kombinationseinsatz. 3/4 benötigt starke Enge:
`repeated-narrow` hat schon einen Spitzenwert 44/63 und zusätzlich 3/16 aus
Wiederholung/Dauer. 4/5 benötigt R3 mit starker Enge oder erforderliches R4:
`late-general-line` hat einen R3-Schritt mit q=1/9 und g=1/14. Sein Spitzenwert
52/63 ist bereits hoch, zusätzlich 7/32 führen zur Kappung B=1. Bloße R3-Nutzung
bei breitem Angebot bleibt im mathematischen Gegenbeispiel 4. Alle fünf Stufen
sind durch echte, vollständig geprüfte technische Rätsel erreichbar.

Der Referenzstand wurde in Commit `4f726e7` **vor** finaler Parameterentscheidung
persistiert. Spätere JSON-Umformatierung ändert seine kanonische Identität nicht.
Der jetzige [Methodensatz](../tools/puzzle_production/difficulty_method_0_3.json)
hat exakt `format`, `id`, `analyzer`, `rules`, `aggregation`,
`analysis_parameters`, `references`, `calibration`, `configuration`,
`implementation`. Die beiden Standbindungen enthalten exakt `id` und `hash`;
`implementation` ordnet die festen lokalen Modulnamen ihren SHA-256-Dateibytes zu.
Der vollständige kanonische Methodenhash ist separat im
[Prüfeinstieg](../tools/puzzle_production/difficulty_identity.py) gepinnt.

| Bindung | SHA-256 der kanonischen JSON-Bytes |
| --- | --- |
| Methode `picross-difficulty-0.3` | `8f7efa0d5ac76a1bd73fbae3618fec18dba28cf704887188eba2fcf020b9df79` |
| Referenzen `sd-b-references-1` | `57cbee00fc9f91a7d75b2ca05f9d986c7a4d131fc3ed054e207ee9f40a67874f` |
| Kalibrierung `sd-b-calibration-1` | `771a8d57da90b62ca0a299ff60ee62c8a80a45338d44cbda41392e50b39cd6ff` |

Die Methode ist damit für dieses Paket eingefroren. Neue Einträge ändern nichts
an Parametern oder Bewertungen. Spätere Änderungen an Regeln, Merkmalen, Formeln
oder Grenzen benötigen eine neue Methodenversion und einen gesondert beauftragten
Neubewertungs-/Migrationslauf. Die Quellbindung ist konservativ: auch Änderungen
der gebundenen Dateien werden nicht still unter derselben Identität akzeptiert.
Dateigebundene v1-Analysen bleiben von der opt-in Methodenkontrolle unberührt.

## Prüfzuordnung und Aussagegrenzen

[SD-B-Tests](../tests/puzzle_production/test_difficulty_rating.py) decken A01–A08
mit dem festen Referenzinventar, den exakten Grenz-/Gegenbeispielen, frischen
Dateiprüfungen und Wiederholungen ab. Künstliche Metrikfolgen isolieren einzelne
Formelwirkungen (etwa zusätzliche frühe R0-Arbeit oder späte Endbereinigung);
sie sind ausdrücklich keine angeblich zertifizierten Rätsel. Die Klassenbelege
oben kommen ausschließlich aus vollständigen tatsächlichen Analysen/Proofs.
Symmetrien und Farb-ID-Umbenennung werden an ganzen Rätseln geprüft.

Die Grenzprüfungen verwenden unmittelbar benachbarte rationale Werte. Unter
anderem: 749/1000, 3/4, 751/1000 für die Enge; 124/1000, 1/8, 126/1000
für die lokale Ausnahme; 899/900/901 Zellen für den Größenwechsel 2→3.
Auch Kappung, Mindestanspruch vor 4/5, leere/undefinierte Anteile, partielle
Domains, Abbruch, Widerspruch, fehlende und neu gehashte falsche Bindungen
werden geprüft. Referenzwert und Bewertung sind unabhängig von anderen Einträgen.

Die Methodeneinführung ist modellbasiert, nicht empirisch menschlich kalibriert.
Ein kleiner fester Satz garantiert keine universelle Schwierigkeitseinschätzung;
insbesondere die R1-/lokale-R2-Ausnahme und die Größenformel bleiben bewusste
Modellentscheidungen. Technische Reproduzierbarkeit rechtfertigt `medium`, nicht
`high` oder Lösungsminuten. Auffälligkeiten bei einer später beauftragten
Bestandsbeobachtung sind zu untersuchen; ein gewünschtes Histogramm rechtfertigt
keine Grenzänderung. Keine reale Kataloganalyse wurde in SD-B durchgeführt.

SD-B-T01 umfasst aktuelle Pflicht-CI gemäß vollständigem Diff sowie die hier
gebundenen technischen Nachweise. Der getrennte Selbstreview ist Teil der
Implementiererlieferung. **SD-B-R01 und SD-B-M01 sind abgeschlossen**; PR #241
ist als `b625cc6af1342eafb2582beb9eec17991ea21a12` in main integriert.
Die vollständige CI 39060755154 einschließlich Web/ci-required ist erfolgreich;
eine damalige paketbezogene Web-Ausnahme wurde nicht benötigt und gilt nicht für SD-C.
Head-/Basis-/Checkout-/Runbindungen und Akzeptanzstand
stehen in [PR #241](https://github.com/venomenon328/picross/pull/241) und
[#237](https://github.com/venomenon328/picross/issues/237). Der Methodenfreeze
bleibt unverändert; [SD-C1](SD_CATALOG.md) verwendet neue Integrationsmodule.
