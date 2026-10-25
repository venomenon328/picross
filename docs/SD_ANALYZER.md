# SD-A: Regel-, Wellen- und Berichtsvertrag

**SD2 · 25.10.2026:** [Der freigegebene neue Sollvertrag](PUZZLE_DIFFICULTY_V2.md)
beauftragt als Spezifikation getrennte menschennähere Regeln und drei Rohprofile
für die separat versionierte Methode 0.4. Dieser vollständige 0.3-Analysatorvertrag bleibt
unverändert gültig. SD2-A (#403) liefert neue Regeln, Formate und unabhängige Prüfung
im [separaten Analysevertrag](SD2_ANALYZER.md) und ist nach separatem R01 über
PR #408 auf `c7c6156ac27dc033036443bc06ef398bbf94f32f` integriert;
keine Umdeutung alter R1/R2-Belege. [SD2-B](SD2_CALIBRATION.md) ergänzt den
eigenständigen inaktiven 0.4-Freeze; B-R01 und Merge bleiben offen.

Stand: 17.10.2026 · Version 1.0 · technische Konkretisierung von
[SD-A/#236](https://github.com/venomenon328/picross/issues/236) und
[SD-D03–D06](PUZZLE_DIFFICULTY.md). Vor der Regelimplementierung festgelegt.
Dies ist der Analysator `picross-sd-analyzer-1`, Regelstand `sd-rules-1`.
Sein v1-Bericht bleibt unkalibriert. [SD-B](SD_CALIBRATION.md) ergänzt separat
`picross-difficulty-0.3` und dessen optionales `rating.json`, keine Katalogübernahme.

## Endliche Regelliste

Positionen und Blockindizes sind nullbasiert. Leer ist Bit 0, Vordergrundfarben
sind einzelne weitere Bits. Ein Schluss schneidet eine bestehende Domain mit
seiner erlaubten Wertmenge. Alle Regeln einer Linienauswertung sehen denselben
Vorzustand. Keine Regel setzt vorherige Schlüsse derselben Auswertung voraus.
Eine leere Schnittmenge belegt Widerspruch, wird aber nicht ins Raster übernommen.

Für Block i mit Länge l(i) und Farbe c(i) ist g(i,j)=1 bei gleicher Farbe,
sonst 0. Seine geometrische Startmenge S(i) ist das ganzzahlige Intervall
zwischen der frühestmöglichen Packung aller Vorgänger und der spätestmöglichen
Packung aller Nachfolger, ausschließlich aus Hinweisen und Linienlänge.
Überfüllte Hinweise sind Widerspruch, kein ungültiges Dateiformat.

| Regel | Voraussetzung und genau erlaubter Schluss |
| --- | --- |
| `R0-empty` | Keine Hinweise: alle Zellen leer. |
| `R0-packed` | Summe der Blocklängen und gleichfarbigen Pflichtabstände ist mindestens Linienlänge. Bei Gleichheit die einzig mögliche Packung einschließlich Separatoren; bei Überfüllung Widerspruch. Ein voller Einzelblock ist enthalten. |
| `R0-cleanup` | Die maximalen zusammenhängenden **bereits singleton-bestimmten** Vordergrundruns entsprechen exakt der geordneten Hinweisfolge. Alle übrigen Zellen werden leer. Unbekannte oder mehrwertige Zellen trennen diese Runs; deren Leerheit wird erst gefolgert. Die gesamte Vordergrundmenge ist bereits verbraucht. |
| `R1-overlap` | Für jeden Block alle geometrischen Starts S(i) betrachten. Der Schnitt seiner Intervalle wird c(i). Sonst keine Ausschlüsse, insbesondere keine allgemeine Linienunterstützung. |
| `R1-anchored` | Für jeden maximalen Singleton-Vordergrundrun [a,b) getrennt die Blöcke gleicher Farbe suchen, von denen ein geometrischer Start den ganzen Run abdeckt. Genau ein möglicher Block: dessen Starts auf die Abdeckung **dieses einen Runs** einschränken, den Intervallschnitt färben. Bei genau einem verbleibenden Start zusätzlich c(i) unmittelbar vor/hinter dem Block ausschließen. Ergebnisse aller einzelnen Anker vereinigen, ohne ihre Voraussetzungen zu kombinieren. Kein Besitzer: Widerspruch. |
| `R2-segments` | Die unten definierte lokale Kandidatenreduktion bis zum Fixpunkt; anschließend deren konservative Zellprojektion. |
| `R3-support` | Vollständige Unterstützung aller zulässigen Linienbelegungen unter sämtlichen Vorzustandsdomains. Der vorhandene Zellautomat darf verwendet werden; Prüfung durch den unabhängigen Blockintervall-DAG. |

Rk enthält alle Regeln bis einschließlich k. Die Anwendung prüft die Stufen
0,1,2,3 und verwendet die erste mit Fortschritt oder Widerspruch. Innerhalb
einer Stufe werden **alle** produktiven Linien und Unterregeln gespeichert.
Die Herkunft der einzelnen Ausschlüsse bleibt damit sichtbar, ohne aus
gleichzeitigen mehrfachen Begründungen mehrere Zellfortschritte zu machen.

### R2-Kandidatenreduktion und ausdrückliche R3-Grenze

1. Für jeden Block mit S(i) beginnen. Ein Kandidat [s,s+l) entfällt, wenn eine
   seiner Zellen c(i) ausschließt, eine direkt angrenzende Zelle bereits
   Singleton c(i) ist oder ein nötiger unmittelbar benachbarter Pflichtseparator
   Leer ausschließt. Der Separator ist nur bei einem gleichfarbigen
   Vorgänger/Nachfolger erforderlich. Linienränder ersetzen keine Zelle.
2. Ein Kandidat entfällt, wenn er keinen verträglichen Kandidaten seines
   unmittelbaren Vorgängers oder Nachfolgers besitzt. Verträglich bedeutet
   ausschließlich geordnete, disjunkte Intervalle mit g Pflichtabstand.
3. Für jede Zelle ohne Leer in ihrer Domain alle noch möglichen (Block,Start)-
   Besitzer sammeln. Kein Besitzer: Widerspruch. Gehören alle Besitzer zu
   demselben Block, entfallen dessen Starts, die diese Zelle nicht abdecken.
4. Schritte 2–3 bis zur unveränderten Kandidatenmenge wiederholen. Eine leere
   Blockmenge bedeutet Widerspruch. Es werden niemals Kandidaten ergänzt.
5. c ist an einer Position nur erlaubt, wenn mindestens ein verbleibender
   c-Blockkandidat sie abdeckt. Leer ist nur dann ausgeschlossen, wenn ein
   einzelner Block diese Position in **allen seinen** verbleibenden Kandidaten
   abdeckt. Mit den alten Domains schneiden.

Diese lokale Konsistenz löst weder einen vollständigen Belegungsgraphen noch
verzweigt sie in hypothetische Rasterfortsetzungen. Insbesondere wird die
gemeinsame Abdeckung mehrerer Pflichtzellen mit alternativen Blockbesitzern
nicht verlangt; optionale Lücken zwischen Kandidaten werden nicht als ganze
Intervalle gegen alle Domains geprüft. Solche Kombinationen bleiben R3.
Jede echte Linienbelegung liefert überlebende Kandidaten: die Filter prüfen
notwendige Bedingungen. Intervallschnitt/fehlende Farbabdeckung liefern daher
sichere, möglicherweise unvollständige Folgerungen. Dieser Invariant begründet
auch die endliche Fixpunktiteration und die Mono-/Farbsemantik.

### Kleine unabhängige Beispiele und Abgrenzungen

`?` bedeutet volle Domain, `.` Leer, `A/B` Singletonfarben.

- R0-empty: fünf `?`, keine Hinweise → fünf Leerfelder. Mit Hinweis 1 bleibt
  R0 zunächst unverändert.
- R0-packed: Länge 4, Hinweise A2/B2 → `AABB`; A2/A2 braucht Länge 5 und ergibt
  `AA.AA`. Länge 6 ist keine vollständige Packung.
- R0-cleanup: `?AA??B?`, Hinweise A2/B1 → `.AA..B.`. `?A???B?` genügt nicht.
- R1-overlap: Länge 5, A3 → `??A??`; Länge 6, A3 hat keinen Schnitt.
- R1-anchored: `A????`, A3 → `AAA.?` (außerhalb des festen Blocks nur das
  unmittelbar angrenzende A ausschließen). Bei `??A??`, A1/A1 ist der Anker
  nicht eindeutig zugeordnet; diese Regel liefert keine Änderung.
- R2-segments: `.????`, A3 → `.?AA?` einschließlich geometrischer R1-Überlappung an
  Position 2. R1 allein berücksichtigt den leeren Rand nicht.
- R3-support: `???A.??`, A1/A2. R0–R2 ändern nichts; R3 ergibt `?.?A.??`.
  A an Position 3 könnte zu beiden Blöcken gehören. Eine A-Belegung an Position 1
  ist aber mit keiner vollständigen gemeinsamen Platzierung vereinbar. R2 prüft
  diese globale Abdeckung alternativer Besitzer ausdrücklich nicht.

Die allgemeinen Tests prüfen jede Regel gegen kleine vollständige Mono-/Farb-
Belegungsorakel, einschließlich nicht erfüllbarer Vorzustände. Beispiele stammen
ausschließlich aus künstlichen Linien, niemals aus dem Produktionsbestand.

## Synchrone Wellen und Symmetrie

Start: vollständig unbekannte Domains. Pro Kandidatenstufe werden alle Zeilen
und Spalten aus genau demselben unveränderlichen Raster ausgewertet, auch bereits
bestimmte Linien zur Widerspruchskontrolle. Eine Linie ist offen, wenn mindestens
eine Domain mehrwertig ist. Produktiv heißt mindestens ein neuer Ausschluss.
Die erste produktive Stufe liefert eine Welle: alle Ausschlüsse vereinigen,
je Zelle schneiden und atomar übernehmen. Danach erneut bei R0 beginnen.
Ein Abbruch vor vollständiger Auswertung oder Speicherung verwirft die gesamte
angefangene Welle. Nullfortschritte zählen nicht als Wellen.

Sind alle Stufen unproduktiv, ist das Ergebnis `solved` bei lauter Singletons,
sonst `stalled`. Widerspruch hat innerhalb einer vollständig ausgewerteten Stufe
Vorrang vor Fortschritt; auch widersprüchliche Kreuzungsschlüsse werden erkannt.
Die widersprüchliche Welle wird als Terminalbeleg gespeichert, nicht angewendet.
Ein Abbruch beansprucht weder schwachen noch vollständigen Fixpunkt.

Zeilen/Spalten sind fachlich gleich gewichtet. Ausgabeordnung ist Zeilen,
Spalten, jeweils Index aufsteigend; Regelreihenfolge ist die obige Tabelle.
Alle gleich starken Begründungen bleiben erhalten. Keine Auswahl eines ersten
Gewinners. Spiegelung, Transposition und bijektive Farb-ID-Umbenennung erhalten
Status, Familienfolge und skalare Wellen-/Gesamtmetriken. Koordinaten, Achsen,
Dimensionen, Farbmasken und Hashes transformieren entsprechend; exakte Tracebytes
müssen bei transformierten Eingängen nicht gleich sein. Abgebrochene Zeitläufe
haben keine Symmetrie-/Reproduzierbarkeitszusage.

## Metriken und explizite Aggregation

Je Welle: Familie, offene und produktive offene Linien (gesamt und je Achse),
Angebotsanteil als ganzzahliges Zähler/Nenner-Paar, unterschiedliche geänderte
Zellen, neue Singletons, Änderungen mit weiterhin mehrwertiger Domain, entfernte
Werte sowie deren Domain-Kardinalitäten vorher/nachher. Geänderte Zellen sind
innerhalb einer Welle eindeutig; `unique_changed_cells` vereinigt über alle Wellen.
`first_changed_cells` zählt erstmals überhaupt eingeschränkte Positionen;
Singletons können im monotonen Verlauf nur einmal neu entstehen. Wiederholte
partielle Änderungen zählen als Ereignisse und separat als Positionsvereinigung.
`cell_change_events` ist ausdrücklich die Summe der Wellenänderungen.

Gesamt: Familienhäufigkeit als produktive Wellen und Linienanwendungen,
Unterregelhäufigkeit als produktive Linien-/Regelanwendungen, höchste erforderliche
Familie im abgeschlossenen Linienverlauf. Einfacher Anteil: durch Wellen bis R1
neu bestimmte Zellen / alle Rasterzellen, zusätzlich deren Anteil an allen
tatsächlich bestimmten Zellen. R0-Anteil separat. Kein Farbzahlmultiplikator.
Ohne bestimmte Zellen ist der zweite Anteil `[0,0]` (undefiniert, nicht Null).
Arbeitsumfang: Dimensionen, Zellzahl, Hinweisanzahl/-längensumme, je Achse und
gesamt, unterschiedliche Vordergrundfarben. Betriebsarbeit und Zeit separat.

`aggregation=null` ist der unkalibrierte Standard: Engstellen/Restaufräumen
werden nicht mit erfundenen Schwellwerten ausgewiesen. Optional hat
das Aggregationsobjekt genau `format="sd-aggregation-1"`, `min_family` (0…3), `max_productive_fraction` ([Z,N],
0≤Z≤N, N>0) und `cleanup_remaining_cells` (0…10000). Eine Welle ist Engstelle,
wenn ihre Familie mindestens min_family und ihr Angebotsanteil höchstens Z/N
ist. Häufigkeit = Anzahl maximal zusammenhängender Engstellenphasen; Dauer =
Wellenzahl je Phase, Summe und Maximum. Restaufräumen ist der maximale finale
Suffix eines vollständig gelösten Linienlaufs aus ausschließlich R0-Wellen,
deren jeweilige Zahl offener Zellen vor der Welle höchstens cleanup_remaining_cells
ist. Brüche werden ohne Floatvergleich
verglichen. Alle Parameter werden gespeichert/gehasht; dies sind ausdrücklich
benutzergewählte Messkriterien, keine SD-B-Defaults, Gewichte oder Stufengrenzen.

## Spur, Prüfung und Grenzen

`picross-analysis-trace-v1` bindet Analysehash, Analyzer-/Regelversion,
Parameter, vollständige produktive Linien-/Regelfolgerungen jeder Welle,
Enddomains, Terminalbeleg und Status/Abbruchgrund. Masken sind Ganzzahlen.
`picross-analysis-report-v1` bindet Spurhash und daraus rekonstruierte Metriken,
Umfang, Status, Vollständigkeit und kurze Begründung. `level` und `method` sind
null; SD-A vergibt auch im R4-Fall keine neue kalibrierte Note.

Der getrennte Prüfer importiert weder Analyseengine noch Regelerzeuger. Er
rekonstruiert R0/R1 durch eigene Intervallmengen und R2 durch eigene simultane
Kandidatenelimination. R3 verwendet den bestehenden unabhängigen DAG. Pro Welle
prüft er jede schwächere Stufe und das vollständige gleichzeitige Angebot.
Er vergleicht alle Regeln, Ausschlüsse und Enddomains und rekonstruiert Metriken
aus den geprüften Änderungen. Gemeinsame reine Format-/Metrikfunktionen sind
zulässig; Algorithmusfehler werden zusätzlich durch unabhängige Orakel geprüft.
Der Spurhash allein ist weder Prüfung noch Signatur.

`solved`, `stalled`, `contradiction`, `aborted`, `invalid_input` und
`technical_error` bleiben getrennt. Nur ein geprüfter vollständiger Linienlauf
hat `line_analysis_complete=true`. Ein geprüfter unvollständiger Fixpunkt ist
ausgewertet, aber kein vollständiger Lösungsverlauf. Abbruchpräfixe können
geprüft werden; ihr tatsächlicher Betriebsabbruch wird nicht nachträglich bewiesen.

Vorab gebundene Budgets: 120 Sekunden, 100000 Linienauswertungen, 20000000
Kandidatenoperationen, höchstens 80000 Wellen und 64 MiB kanonische Spurbytes.
Zulässige Arbeitsmaxima: 1000000 Linien, 100000000 Kandidatenoperationen;
Nullbudgets erlauben Abbruchproben. Jede Linienauswertung ist durch 100 Zellen
und 100 Hinweise begrenzt, Kandidatenfilter prüfen Zeit/Arbeit kooperativ.
Das ist kein OS-/RSS-Limit. Verifikation besitzt ein eigenes vorab gebundenes
Budget. Keine halbe Welle wird bei Zeit-, Arbeit-, Speicher- oder Wellenende
als Fortschritt verbucht. Zeit und Betriebszähler stehen außerhalb fachlicher
Ergebnisidentität; vollständig abgeschlossene gleiche Eingänge/Versionen/
Parameter liefern identische Spuren und Metriken.

## Eingangsbindung, R4 und manueller Dateipfad

Gespeicherte `picross-logic-v1/v2` werden strikt validiert. Der eigene Analysehash
ist der Hash von `{format:picross-analysis-input-v1,logic:<normalisierte Logik>}`.
Er ist ausdrücklich ein anderer Vertrag als ein Produktions-`logic_hash`.

Der Runtimeadapter liest ausschließlich die explizite Schema-2-Datei, keine
Registry, Pakete oder Assets. Dimensionen 1…50, Palette mit IDs 1…K (K=1…8),
Leer 0 und numerische Hinweise werden auf `c1`…`c8` in Logik v2 abgebildet.
Auch K=1 verwendet diese normalisierte Farbsemantik; die historische Produktionsart
ist `unknown`. Es gibt in Schema 2 weder ursprüngliche semantische Farb-IDs
noch ein Produktions-mode. ID, Revision und tatsächlicher Definitions-Dateihash
bleiben separate Bindungen. `solution` wird ausschließlich **nach** der Analyse
validiert und mit abgeschlossenen Enddomains verglichen; sie ist kein Engineinput.
Ein Matrixfehler verhindert einen erfolgreichen dateigebundenen Abschluss.

Optional werden ausdrücklich benannte Linienbaseline und Paarproof für exakt
die Engine-Logik frisch mit dem vorhandenen unabhängigen Verifier geprüft.
Nur `full-line-* / stalled` plus vollständiger Proof v3 belegt R4. Das eigene
Linienergebnis muss ebenfalls `stalled` sein. Beide Originaldateien, Profilhashes
und Status werden getrennt gebunden. R4-Schritte werden niemals Linienwellen.
Für remappte Runtimefarben sind alte Produktionsproofs nicht automatisch passend.
Ohne passende Proofs bleibt `r4=null`; es wird kein Paarlauf gestartet.
Mit Proofs unterscheidet `necessity` required/not_required/unproven. Ein separat
vollständig geprüfter Paarproof belegt `deduction_complete`, auch wenn eine
abgebrochene Baseline keine Notwendigkeit belegt. Er macht den gemessenen
Linienverlauf nicht vollständig und erzeugt keine kalibrierte Einstufung.

Die CLI erzeugt ausschließlich ein neues Verzeichnis mit Eingangskopie,
normalisierter Logik, Spur, Bericht und gegebenenfalls beiden Proofkopien.
Ein lesender Prüfbefehl kontrolliert Eingangsbytes, Logik, Spur, Bericht und R4
erneut. Dateinamen sind fest, keine Pfade aus Berichten werden geöffnet.
Der Bericht trennt deterministischen `result` samt Hash von Dateibindungen,
Budget-/Zeitdaten und Prüfstatus. Keine Katalogmutation, kein Produktionsstart.
Bedienung und reproduzierbarer künstlicher Durchstich stehen in der
[Werkzeuganleitung](../tools/puzzle_production/README.md).
