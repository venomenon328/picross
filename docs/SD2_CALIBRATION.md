# SD2-B: Referenzen und Bewertungsvertrag 0.4

Stand: 25.10.2026 · Vertrag 1.0 · #404

Basis `c7c6156ac27dc033036443bc06ef398bbf94f32f`, integriertes SD2-A / PR #408.
[Fachvertrag](PUZZLE_DIFFICULTY_V2.md), [Analysevertrag](SD2_ANALYZER.md),
[unveränderter 0.3-Freeze](SD_CALIBRATION.md). Dieser eigenständige B-Weg
aktiviert keine Methode und verändert keine Katalog-/Produktionsdaten.

## 1. Referenzen vor Parametern

Der [feste Satz](../tools/puzzle_production/sd2_references_0_4.json) bindet 36
vollständige neue synthetische Rätsel, Herkunft, Ausgangsmatrix, daraus extrahierte
Hinweise, Logik-/Analysehash, Auswahlgrund, Erwartungsstufe und Mustergruppe.
20 Fälle gehören zur Kalibrierung, 16 zur zurückgehaltenen Validierung.
Die Matrix dokumentiert die Konstruktion und den nachgelagerten Endvergleich;
der Analysator erhält ausschließlich Hinweise und unbekannte Startdomains.
Keine Katalogdatei, Kopie, A-Regeltestmatrix oder alte 0.3-Referenz wurde übernommen.

Die geometrischen Muster wurden neu konstruiert. Die unabhängigen Zufallsmatrizen
stammen aus vier separaten deterministischen Untersuchungen; vollständiger
Erzeugertext, Seeds, Kandidatenzahlen und ausgewählte Indizes stehen im Satz.
Die Untersuchung endet nach 2200/2200 beziehungsweise 5281/4731 Kandidaten.
Sie ist kein CI-Befehl und wird nicht bei späteren Rätseln fortgesetzt.
Auswahl nach vollständigem Rohverlauf, niemals nach Score oder Histogramm.
Alle ausgewählten Spuren wurden mit dem unabhängigen SD2-Prüfer bestätigt;
Paarfälle zusätzlich mit vollständiger separater Linienbaseline und Paarproof.
Der bewiesene Endstand stimmt jeweils mit der konstruierten Matrix überein.

Die Erwartungen sind technische, begründete Modellanker, keine menschlichen
Messungen. Ihre Begründungen und Vergleichsordnungen sind vor der ersten
Scoreberechnung festgelegt. Numerischer Vertrag, Alternativenvergleich,
Implementierung und Freeze wurden als weitere versionierte Schritte desselben
Pakets geliefert. Der erste Referenzcommit behauptete noch keinen Methodenfreeze.

## 2. Vorab gebundene Abdeckung und Gruppentrennung

`s<Seed>-<Index>` bezeichnet exakt einen Fall im JSON. Jeder Fall besitzt eine
eigene Gruppe; Transformationen und spätere nahe Ableitungen müssen in derselben
Gruppe bleiben. Die unabhängigen Zufallsmatrizen wurden nicht aus gemeinsamen
Stammrastern mutiert. Geometrische Konstruktionen verbleiben vollständig in der
Kalibrierung; die Validierung verwendet unabhängige Zufallsmuster. Alle
Erwartungen, Gruppen und Splitzuordnungen werden nach Ergebnissen nicht geändert.

| Abdeckung / erwartete Stufe | Kalibrierung | Zurückgehaltene Validierung |
| --- | --- | --- |
| L1, unmittelbare Voll-/Leer-/Restregeln | full-50, bands-40, packed-colors | s40499-9, s40499-710 |
| L1, flüssige einfache Überlappungen | s40401-3, s40401-1080 | s40499-173 |
| L2, übliche eingeschränkte Überlappungen/Verlängerungen | s40401-10, s40401-44, s40401-98 | s40499-2, s40499-48 |
| L3, kleinteilige Suche ohne stärkere Schlussfamilie | s40401-526, s40401-1111 | s40499-654, s40499-957 |
| L3, gemeinsame Blockzuordnung mit gutem Fortschritt | s40401-6, s40401-1574 | s40499-747, s40499-1744 |
| L4, Kombinationen und wiederkehrende enge Phasen | s40401-1495, s40401-2093, s40401-888 | s40499-1564, s40499-656 |
| L5, reine allgemeine Linienlogik | s40405-230, s40405-3463, s40405-5280 | s40495-1729, s40495-2540, s40495-4730 |
| L5, notwendiges R4 | s40405-65, s40405-79 | s40495-103, s40495-109 |
| Frühe / späte / wiederholte Engstellen | s40401-1495 / s40405-3463 / s40401-888 | s40499-654 / s40495-4730 / s40499-656 |
| Kleine schwierige / große einfache Fälle | s40405-5280 / full-50, bands-40 | s40495-4730 / keine zusätzliche große Validierung behauptet |
| Mono / Farbe, partielle Farbausschlüsse | s40401-10 / s40401-44, s40401-888 | s40499-2 / s40499-48, s40499-1564 |
| Lange Füllzüge / viele gepackte kleine Zahlen | full-50, bands-40 / packed-colors | s40499-710 / keine vollständige Kreuzproduktquote |

Größen reichen von 35 bis 2500 Zellen; Rechtecke, quadratische Muster und beide
Farbsemantiken sind enthalten. E1-Rohbelege enthalten direkte Überlappung,
sicher eingeschränkte Überlappung und eindeutige Anker. Die konkrete Regelanwendung
bleibt in der reproduzierbaren vollständigen Spur prüfbar. Frühe/späte Phasen
beziehen sich auf den Fortschritt bei Phasenbeginn gemäß A-Vertrag; ein später
E3-Schritt kann innerhalb einer früh begonnenen Phase liegen.

Die breite Auswahl wird nicht als statistisch repräsentative Stichprobe bezeichnet.
Die seltenen E3-Fälle wurden bewusst gesucht, um technische Erreichbarkeit und
Schutz später Schlüsselstellen zu prüfen. Jeder Skalenwert hat mehrere
voneinander unabhängige ganze Muster. Künstliche Profilfolgen werden später nur
Formelgrenzen isolieren und niemals diese Rätselbelege ersetzen.

## 3. Chronologie und Aussagegrenzen

Die Referenzfestlegung wurde vor dem numerischen Vertragsauftakt committed.
Validierungsrohprofile wurden ausschließlich für die Kuratierung betrachtet;
sie werden nicht zur Parameterwahl oder Alternativenauswahl verwendet.
Nach Vertrags-/Implementierungsabschluss werden ihre Bewertungen separat geöffnet.
Eine spätere Änderung aufgrund dieser Ergebnisse müsste die Fälle als verwendet
kennzeichnen und einen neuen unabhängigen Validierungssatz binden.

Menschliche Vergleichsdaten liegen nicht vor. Deshalb höchstens mittlere
Aussagekraft, keine Lösungsminuten und keine behauptete empirische Kalibrierung.
SD2-B-T01 und getrennter Selbstreview werden in der
[Prüfzuordnung](SD2_B_VERIFICATION.md) und dem Implementierungs-PR gebunden; das separate
SD2-B-R01 und Merge bleiben nachgelagerte Gates. #405/#406 bleiben außerhalb.

## 4. Untersuchung und Wahl vor Implementierung

Referenzcommit: `ca31207e7e70b2610ec0ba5accb386fd6e7a017b`.
Der [numerische Vergleich](../tools/puzzle_production/sd2_comparison_0_4.json)
enthält die exakten Beiträge aller 20 Kalibrierungsfälle, den einmaligen
Untersuchungscode und zehn Varianten. Er berechnet ausschließlich Kalibrierung,
keine Validierungsnoten. Der Untersuchungscode ist kein freigegebener Prüfer.

| Variante | Erfüllte vorab festgelegte Stufen / 20 | Entscheidung |
| --- | --- | --- |
| Gewählte Spitzen-/Dauerformel | 20 | Grundlage dieses Vertrags |
| Ohne lokalen Kontext | 20 | Gleiche Stufen, aber weniger Binnenabstand; Kontext bleibt klein begrenzt |
| Ohne Suche | 12 | Enge E1-/E2-/E3-Verläufe werden unterschätzt |
| Mittlere statt maximaler Suchspannung, ohne Dauerglied | 12 | Seltene Schlüsselstellen verschwinden |
| Starke Familie nach globalem Informationsanteil verdünnt | 12 | Kleine notwendige Kombinationen verlieren ihre Bedeutung |
| Ohne Umfang | 20 | Umfang ist keine Voraussetzung für eine gebundene Erwartungsstufe |
| Zellzahl / 400 als ungeschützter Umfang | 17 | full-50 wird L5, bands-40 L4, packed-colors L2; verworfen |
| Ohne Dauer-/Wiederholungsglied | 16 | Mehrere kleinteilige Suchverläufe fallen eine Stufe |
| Suchbeitrag × 9/10 beziehungsweise × 11/10 | je 20 | Lokale Gewichtssensitivität ohne Stufenwechsel |

Die gewählten Kalibrierungsscores liegen bei L1 zwischen 0 und 0,3125,
L2 zwischen 1,3534… und 1,4507…, L3 zwischen 2,1283… und 2,2387…,
L4 zwischen 3,2296… und 3,3405…, linienlogischem L5 zwischen 4,2183…
und 4,3097…; notwendiges R4 erhält 4,5. Diese Zahlen sind Modellwerte,
keine gemessenen menschlichen Abstände. Keine Quantile oder Sollhäufigkeiten.

Angebot und Gewinn bilden gemeinsam eine Spannung; sie werden nicht nochmals
addiert. Dauer und Wiederholung erhalten zusammen höchstens 1/4. Blockzahl
und Zuordnungsmehrdeutigkeit gehen per Maximum in einen kleinen Kontextwert
ein. Zellzahl, Hinweiszahl, Farbzahl, Kleinzahlanzahl und Wellenzahl werden
nicht als zusätzliche Summanden verwendet. Umfang nutzt allein die in A
definierten Füll-/Leerabschnitte. Freie 40 Abschnitte und Sättigung nach weiteren
160 Abschnitten machen die kleinen Muster weitgehend umfangsneutral; die
Referenzstufen hängen nicht von dieser Feineinstellung ab. Ein gekacheltes
Raster ist kein reiner Umfangsgegenbeweis: Seine Hinweise und Schlussfamilien
können sich ändern. Isolierte Profilgegenproben ergänzen deshalb ganze Rätsel.

## 5. Exakter Zahlenvertrag `sd2-rating-formula-1`

Alle Rechnungen erfolgen mit gekürzten rationalen Zahlen beliebiger Präzision.
JSON schreibt jede rationale Zahl als `[Zähler, positiver Nenner]`, auch ganze
Zahlen als `[n,1]`. Kein Float, Runden, Epsilon oder laufzeitabhängiger Wert
entscheidet eine Stufe. `L(x)=1+Anzahl(t∈{1,2,3,4}: x≥t)`; Gleichheit gehört
zur höheren Stufe. L1 beginnt bei 0, L5 hat keine obere Grenze.

Für jede produktive A-Welle seien `q` Angebot, `g` Gewinn und
`s=(1-q)(1-g)` die A-Spannung. E0-Wellen sind unmittelbares Ausfüllen und
tragen keine Suche. Sie bleiben vollständig im Rohprofil sichtbar.

**Denkanspruch D.** `H` ist die höchste tatsächlich notwendige Familie. Ein
Verlauf heißt flüssig, wenn H≤E1 und jede E1-Welle `q≥1/2 oder g≥1/2`
erfüllt. Bei H=E0 gilt D=0, bei flüssigem E1 D=1/4, sonst bei E1 D=1.
Für H=E2/E3 gilt D=2+C/4 beziehungsweise 3+C/4. Der Kontext C ist das
Maximum über sämtliche E2-/E3-Wellen aus den folgenden beiden Größen:

- `max(0,b-1)/(b+3)` mit `b=interacting_blocks/(q*open_lines)`;
- `ambiguous_required_cells/(ambiguous_required_cells+unique_owner_required_cells+1)`.

`b` beschreibt beteiligte Blöcke je produktiver Linie, keinen behaupteten
minimalen Beweisaufwand. 0≤C<1. Zustandszahlen und Farbe wirken nur über
tatsächlich nötige lokale Schlüsse und Einschränkungen. Ein später E3-Schritt
behält H=E3 unabhängig von der Menge vorherigen/nachfolgenden E0-Ausfüllens.
Globale starke Informationsanteile bleiben diagnostisch und verdünnen D nicht.

**Suchbeitrag S.** `P=max(s)` über E1/E2/E3, leeres Maximum 0.
Eine enge Welle erfüllt Familie≠E0, `q≤1/4` und `g≤1/4`.
`N` zählt diese Wellen, `R` ist die längste zusammenhängende Folge im
ursprünglichen Verlauf; jede andere Welle einschließlich E0 unterbricht R.
`S=P+(min(N,4)+min(R,4))/32`. Damit 0≤S≤5/4. Spitzen bleiben erhalten,
Wiederholung ist relevant, aber nicht unbegrenzt und nicht linear zur Wellenzahl.
Flüssiges E1 hat S≤1/2 ohne enge Wellen und bleibt somit L1.

**Umfangsbeitrag W.** `A=fill_spans+empty_spans` aus A, nicht Zellzahl oder
Klickzahl. `Wraw=min(1/4,max(0,(A-40)/640))`. Basis `B=D+S`.
Flüssige Verläufe erhalten W=0. Sonst bestimme eine Oberstufe K:
`K=max(L(B),3)` bei H≤E1 oder S<3/4; andernfalls
`K=max(L(B),4)` bei H=E2 und K=5 bei H=E3.
Bei K=5 ist W=Wraw; sonst `W=min(Wraw,(K-B)/2)`.
Die halbe verbleibende Strecke hält den Score streng unter der nicht fachlich
getragenen oberen Grenze, ohne Rücksprung bei wachsendem Umfang. Der Bericht
nennt Wraw und den angewendeten Schutz. W≤1/4 bei Stufenbreite 1 garantiert
höchstens eine Nachbarstufe. Umfang führt nur dann zu L4/L5, wenn die
entsprechende Schlussfamilie und S≥3/4 bereits anspruchsvolle Arbeit belegen.

**Gesamtwert.** `score=D+S+W`, `level=L(score)`. Grenznähe enthält die
nächste untere/obere Stufengrenze und jeweils exakten Abstand; an einer Grenze
ist der untere Abstand 0, an den offenen Skalenenden fehlt die entsprechende
Grenze (`null`). Die nächste Entfernung bezieht sich nur auf Stufenwechsel,
nicht auf den Beginn bei 0. D, S, W, B und L(B) bleiben getrennt sichtbar.

**Notwendiges R4.** Nur frisch unabhängig bestätigte vollständige SD2-
Linienfixpunkte `stalled`, vollständige passende Linienbaseline `stalled`
und vollständiger verifizierter Paarproof `solved` mit `required=true`
erlauben D=9/2, S=W=0, Score=9/2 und L5. Die beiden Nullen sind der
konservative feste R4-Anker, keine Messung des fehlenden Paarverlaufs.
Linienprofile heißen ausdrücklich Präfixprofile; ihre Such-/Umfangssignale
werden nicht als vollständige Paarmessung ausgegeben. Bloßes
`deduction_complete`, abgebrochene Baseline oder vollständiger Paarproof allein
genügen nicht. Andere unvollständige, widersprüchliche oder abgebrochene
Analysen erhalten keine Beiträge, keinen Score und keine Stufe.

## 6. Eigener B-Datei-/Prüf-/CLI-Vertrag

Der unveränderte A-v1-Rohweg bleibt eigenständig. B verwendet die neue Hülle
`picross-sd2-rating-bundle-v1`: exakt `analysis/` (geschlossenes A-v1-Bundle),
`rating.json` und `report.md`. Keine weiteren Dateien oder Links/Reparsepunkte.
Auch `rating.json` bleibt als Zusatz in einem A-Bundle unzulässig.

`rating.json` besitzt exakt `format`, `result`, `result_hash`, `analysis_files`.
`format=picross-sd2-rating-bundle-v1`; `result_hash` ist SHA-256 der
kanonischen UTF-8-JSON-Bytes von result nach bestehendem `canonical_bytes`.
`analysis_files` bindet jede Datei einschließlich A-`report.json` nach
Roh-SHA-256 und Bytelänge; es ist keine semantische Ergebnisidentität.
`result` besitzt exakt `format=picross-sd2-rating-v1`, `method`, `method_hash`,
`analysis_result_hash`, `status` (`rated`/`unrated`), `reason`, `profile_scope`
(`complete_line`/`line_prefix`/`incomplete`), `assessment`, `confidence`,
`estimated_minutes=null` und `explanation`. `assessment` besitzt exakt
`contributions` (demand/search/workload), `score`, `level`, `boundaries`
(lower/upper/distance_lower/distance_upper/nearest_distance), `without_workload`,
`level_without_workload` und `signals`. Die Liniensignale heißen highest_family,
fluent, context, peak_search, narrow_waves, longest_narrow_run, spans,
raw_workload, workload_guard (`fluent`/`upper_boundary`/`none`), workload_ceiling.
R4-Signale heißen r4_required=true, line_profiles_are_prefix=true,
search_and_workload=`fixed_anchor_not_full_pair_measurement`.
Bei `unrated` sind assessment/confidence `null`; bei `rated` ist confidence
stets `medium` und die Erklärung bezeichnet eine Modellschätzung.
Der deterministische UTF-8-Markdownbericht wird aus diesem Ergebnis erzeugt
und beim Prüfen bytegenau rekonstruiert. Laufzeiten stehen ausschließlich im
A-Operationsbericht und ändern keinen B-Ergebnishash.

Jeder öffentliche Bewertungs-/Prüfeinstieg prüft zuerst den vollständigen
Methodenfreeze, dann das unveränderte A-Bundle mit unabhängiger Spurreproduktion
und frischer R4-/Zielprüfung. Er bindet die vor/nach Prüfung gelesenen Bytes
und den frisch geprüften A-Ergebnishash; ein Selbsthash allein reicht nicht.
Der B-Checker rekonstruiert das gesamte Ergebnis und den Bericht, prüft die
geschlossenen Dateimengen und alle Rohbindungen. Er vertraut weder gespeicherten
Teilwerten noch Status, Aussagekraft, Freigabefeldern oder `deduction_complete`.
Die reine interne Formel ist kein Prüf-/Freigabeeinstieg.

Dateien: B-JSON und jeder A-Prüfinput höchstens 64 MiB (A-Eingabe weiter
2 MiB), Markdown höchstens 1 MiB; streng gültiges UTF-8-JSON ohne BOM,
doppelte Schlüssel, nichtendliche Zahlen, Zusatzfelder oder Links. Eine Ausgabe
muss ein neues Verzeichnis sein; Fehler dürfen unvollständige Diagnoseartefakte
zurücklassen, aber niemals einen scheinbar gültigen Bewertungsbericht.

Eigene CLI: `python -m tools.puzzle_production.sd2_rating_cli` mit:

- `analyze --input PATH --input-kind logic|runtime --output-dir NEW`
  sowie optionalem explizitem `--r4-proof PATH --r4-baseline PATH` als Paar;
- `rate --input PATH --analysis-bundle DIR --output-dir NEW` für vorhandene
  A-Rohbündel; bytegetreue Kopie in die neue Hülle und frische Prüfung;
- `check --input PATH --bundle DIR` für eine vorhandene B-Hülle.

Alle Befehle erlauben `--seconds` (120), `--max-lines` (100000),
`--max-rule-work` (20000000), `--max-waves` (80000),
`--max-pair-work` (20000000), `--max-pair-records` (250000).
Bei `analyze` begrenzt ein eigener Analysator diese Budgets; die getrennte
Verifikation erhält `--verify-seconds` (120), `--verify-max-lines` (100000),
`--verify-max-rule-work` (20000000) und dieselben Paar-/Wellengrenzen.
`rate/check` verwenden alle Grenzen für die frische Verifikation. Frist beginnt
beim ersten tatsächlichen Check; keine Erhöhung oder Wiederholung nach Abbruch.
Syntaxfehler sind argparse-Exit 2, sonst eine JSON-Zeile auf stdout:
0 = vollständig geprüft (auch ausdrücklich unrated/stalled/contradiction),
2 = ungültige Eingabe/Methode/Pfad, 3 = ungültige Belege/Bundle/Ergebnis,
4 = Abbruch/Budget/Speicher/Interrupt, 5 = technischer Fehler.
Fehlerformat `picross-sd2-rating-error-v1` trägt stets `level=null`.
Ein verifizierter abgebrochener Präfix darf als `unrated` mit Exit 4 erhalten
bleiben; ein Prüfabbruch erzeugt kein Rating. Kein stilles R4-Rechnen,
Kataloglesen, Aktivieren oder Übernehmen.

## 7. Freeze und getrennte Validierung

Nach Implementierung wurden alle 36 Referenzen erneut vollständig analysiert,
unabhängig geprüft und bewertet. Die ersten 20 ergeben die feste
[Kalibrierungsevidenz](../tools/puzzle_production/sd2_calibration_0_4.json),
die übrigen 16 eine [separate Validierung](../tools/puzzle_production/sd2_validation_0_4.json).
Alle 20/20 und 16/16 unveränderten Erwartungen sowie alle 3/3 und 2/2
Vergleichsordnungen sind erfüllt. Keine Nachjustierung anhand der Validierung,
keine Umetikettierung, kein Austausch eines Falls. Jede Stufe ist in beiden
Splits durch mindestens zwei unabhängige vollständige Muster vertreten.

Validierungsscores: L1 0–0,325; L2 1,3267…–1,4213…;
L3 2,1700…–2,3116…; L4 3,3261…–3,3322…;
linienlogisches L5 4,1613…–4,2030…; notwendiges R4 4,5.
Die gewählten Schwellen trennen die begründeten Muster auch im zurückgehaltenen
Satz; daraus folgt keine Genauigkeitsquote für beliebige Rätsel oder Menschen.
Binnengewichte für Kontext und Umfang sind vorsichtige Modellentscheidungen,
keine aus diesen Daten eindeutig identifizierbaren menschlichen Koeffizienten.

Der neue Manifestvertrag `picross-sd2-method-v1` bindet A-Regeln/Analysator/
Rohmetrik, Formelversion, Parameter/Schwellen, die kanonischen Hashes des
Referenzsatzes, Vergleichs, beider Evidenzdateien und alle transitiv verwendeten
Python-Quellen nach Roh-SHA-256. Der separat gepinnte Manifesthash steht in
einer Identitätsdatei außerhalb der eigenen Quellliste, um keinen Hashzyklus
zu erzeugen. Das Manifest bindet auch die bytegleich erhaltenen 13 Quellen
des 0.3-Manifests. Keine Neuversiegelung von 0.3. Die Evidenz speichert nur
Formelergebnisse und geprüfte Analyse-/Spur-/Proofidentitäten, keinen rekursiven
B-Methodenhash. Eine spätere Änderung verlangt eine neue Methodenidentität;
dieses B-Paket schaltet die eingefrorene Methode weiterhin nicht aktiv.

Eingefrorener [Methodensatz](../tools/puzzle_production/sd2_method_0_4.json):
`db882ea14b17de725bf75e64904579cc7790c875d557f036fdd89586f303a97c`.
Er bindet 27 Python-Quellen und sieben kanonische JSON-Artefakte einschließlich
des unveränderten 0.3-Manifests samt Referenzen/Kalibrierung. Der B-Hash gehört
zur Standalone-Methode, nicht zu einer aktiven Katalogrevision.
