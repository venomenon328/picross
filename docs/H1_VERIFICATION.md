# H1 · Erfüllte Hinweise: technische Nachweise und Eigentümerprobe

Stand: 25.09.2026 · [Issue #19](https://github.com/venomenon328/picross/issues/19),
Branch `feat/19-clue-completion`, aktuelle Integrationsbasis
`main@6dd33232977127592c2b881f73094658853dbd87` nach G1/#17 und PR #18.
Lieferhead, Test-Merge, erfolgreiche CI-Runs und geprüftes Windows-Artefakt werden
im PR gebunden. Die in #12 dokumentierte bisherige P1-Eigentümerabnahme bleibt
gültig; die gezielten G1-/H1-Proben werden nicht als bestanden umgedeutet.

## Technischer Prüfvertrag

`model/clue_completion.gd` erhält nur Zellen und Hinweise einer vollständigen Linie.
Ein gerichteter azyklischer Zustandsgraph über Hinweisindex und Zellposition erlaubt
Leerzellen- und Blockkanten samt gleichfarbigem Pflichtabstand. Vorwärts-Erreichbarkeit
und Rückwärts-Machbarkeit bestimmen alle möglichen Starts jedes Originalhinweises.
Genau ein Start und vollständige Spielerfüllung dieses Intervalls setzen das Flag.
Leere Machbarkeitsmenge ergibt ausschließlich false. Laufzeit und Speicher sind
O(Hinweise × Linienlänge), keine Aufzählung vollständiger Linienbelegungen.

Das Board hält pro konkreter Zeile/Spalte nur den letzten vollständigen Eingang und
die abgeleiteten Flags; maximal Breite + Höhe Cacheeinträge. Ein neuer Sessionbezug
leert den Cache. Der Vergleich mit `visible_cells()` erfasst auch zurückgezogene
Previewarme und Restore in derselben Session. Unveränderte Linien und reine
Render-/Geometrieänderungen starten keine neue Suche. Die Definition einer Session
bleibt wie bisher unveränderlich. Keine Schreibpfade zu Session, History oder Save.

| Akzeptanz | Technischer Nachweis |
| --- | --- |
| A-H01 | Neun Issuevektoren plus Farb-, Rand-, Teilblock-, Doppelhinweis-, Leerlinien- und Widerspruchsfälle; deterministische kurze mono-/farbige Eingänge gegen unabhängigen Zellbelegungs-Oracle, zusätzlich Spiegelung. |
| A-H02 | Eingänge unverändert; andere Lösung/Reveal/Abschluss-/Kreuzhinweise bei identischen Linieneingängen; keine erzwungene unbekannte Füllung. Save-/History-/Dateivergleich vor/nach Analyse und Schalter. |
| A-H03 | Viewportereignisse für Füllen/X/Radierwege, Eindeutigkeit, Widerspruch, Preview/Rückzug/Escape/Fokusverlust; Undo/Redo, Blattwechsel/Reset, Restore und echte Recovery. Eine direkte G1-Integrationsregression prüft horizontalen erfüllten Previewarm → tatsächliche Startzelle → vertikalen Arm und die sofortige Markerinvalidierung/-neuzuordnung. Zwei-Prozess-Roundtrip prüft den aktivierten Schalterdefault. |
| A-H04 | Echte Off/On-Paare: F-02/F-03, 1280×720 bis 2560×1440, UI 100/125 %, Zoom 50/75/92/100 %, unterschiedliche Lesepositionen, beide Achsen, alle Farben, ein-/mehrstellige Zahlen, Marker, Tooltip, kontinuierlicher Drag/Drop. Pixelvergleiche je Originaltoken sowie unverändertes Raster/Miniatur. Visuelle Stichproben ergänzen die maschinellen Vergleiche. |
| A-H05 | 100er-Linien: leer, stark mehrdeutig, 100 wechselnde Farben, Widerspruch; wiederholte Läufe mit Zeitprotokoll. Cache-/Redrawprüfung und bestehende 500-Aktionen-Folge bei aktivierter Markierung samt Neustart. |
| A-H06 | Produktdefinition, Gestaltungskonzept, P1-Vertrag, Profil und Anleitung nachgeführt; Lösungen, Hinweise, 48/80 Proofschritte, Artwork und Save-Schema unverändert. |
| A-H07 | Isolierter Produktweg, Godot-/Pythonprüfungen, Import, erwarteter Exit 23, bestehende Save-/Recovery- und Roundtripfälle, Renderprüfung, Windows-Export/-Start, docs/preflight/product und vollständiger Diffcheck. Konkrete Ergebnisse im Draft-PR. |

Reproduktion gemäß Prototypanleitung mit `tools/p1_product.py`, externem gepinnten
Cache und eigenem Outputverzeichnis. Alle Produktprozesse verwenden isolierte
temporäre Profile; 300 Sekunden pro Prozess, 1200 Sekunden pro Download. Zeitwerte
`H1_LINE_TIMING_US` nennen je 20 Analysen nach Fall. Die 500er-Messung bleibt unter
`integration/summary.json` mit Host/Engine, Dispatch und separaten Framewartezeiten.
Das sind keine physische Mauslatenz, FPS-Zusage oder Eigentümerbeobachtung.

Der Produktbericht bindet Head, Basis, Test-Merge/Checkout, Run, Baumzustand,
Engine-/Export-/Renderhashes und die separaten H1-Probehilfen. Das Benutzer-ZIP
enthält nur EXE-Paar, Anleitung und Bericht; die künstliche Linienprobe liegt außen.
Nach Download Hashes/Identität und exportierten Windows-Start kontrollieren.
Artefaktaufbewahrung: 14 Tage. Selbstreview ist keine unabhängige Zweitprüfung.

## Gezielte Eigentümerprobe · nicht durchgeführt

Mit dem im Draft-PR verlinkten Windows-Artefakt, echter Maus und einem eigenen
TEMP-Profil prüfen. Das normale Benutzer-ZIP entpacken; für F-02/F-03 den vorhandenen
`owner-probe.ps1` mit `-Exe <Pfad zu picross-p1.exe> -Profile <neuer TEMP-Unterordner>`
aufrufen. Derselbe Profilpfad erlaubt Fortsetzung; normale Saves bleiben getrennt.

Für die künstlichen Grenzfälle zusätzlich `h1-probe-windows-x86_64.zip` in den
Unterordner `h1-probe` entpacken und im äußeren Artefakt aus PowerShell starten:

```powershell
.\h1-owner-probe.ps1 -Exe .\h1-probe\picross-h1-probe.exe
```

Falls die EXE in einem Unterordner entpackt wurde, ihren tatsächlichen Pfad einsetzen.
Der Helfer startet die separate `picross-h1-probe.exe` mit eingebauten Prüfdaten in
einem frischen TEMP-Profil. Sie nutzt dasselbe Board wie das Spiel. Es ist
ausdrücklich kein Produkträtsel: vier künstliche Zeilen,
leere Spaltenhinweise, keine Speicherung und keine Motiventhüllung. „Leeren“ setzt
nur diese Probe zurück. Zeilen/Spalten werden ab oben/links mit 1 gezählt.

1. **3 5:** In Zeile 1 mit Farbe 1 Spalten 9–11 links füllen: keine Zahl markiert.
   Rechts X in Spalten 8 und 12: nur `3` wird markiert. Rechts Spalten 13–20
   auskreuzen: beide Zahlen unmarkiert, weil der Fünfer rechts nicht mehr passt.
   Undo stellt die `3` wieder her; Redo hebt sie wieder auf.
2. **3 3:** In Zeile 2 dieselben Spalten 9–11 füllen und 8/12 auskreuzen:
   beide `3` bleiben unmarkiert, da der Mittelblock zu beiden passen kann.
3. **Keine Rand-X-Pflicht / Preview:** Nach „Leeren“ in Zeile 3 einen linken
   Zehnerstrich von Spalte 3 bis 12 halten: `10` ist bereits in der Vorschau
   markiert. Auf Spalte 11 zurückziehen: unmarkiert. Wieder bis 12 und Escape:
   unmarkiert, keine bestätigten Zellen. Neu ziehen und loslassen: markiert;
   links auf eine Füllung oder mit Radierer neutralisieren: unmarkiert.
4. **Farben:** Zeile 4 direkt angrenzend je drei Zellen Farbe 1, 2, 3, 4 ab Spalte 1
   setzen. Alle vier Zahlen müssen einzeln durchgestrichen und weiter in ihrer
   Rätselfarbe lesbar sein. Schalter aus/an: normale/aktuelle erfüllte Darstellung,
   unveränderte Zellen und Undo. Dieselbe Lesbarkeit im normalen F-02 prüfen.
5. **Normale F-02/F-03-Probe:** Bei 50/75/92/100 % und UI 100/125 % erfüllte Zahlen
   in beiden Achsen betrachten, lange Folgen unabhängig ziehen und vollständigen
   Hoverhinweis lesen. Striche folgen denselben Zahlen, auch während Drag/Drop;
   `…`/`–`, Farbe, Slotzuordnung und Miniatur bleiben verständlich. Schalter aus,
   Blatt/Album wechseln und ausgewähltes Testblatt bewusst zurücksetzen: aus bleibt
   aus. App regulär schließen und erneut starten: an. Wiederholt in F-03 arbeiten,
   Vorschau zurückziehen/abbrechen und Undo/Redo nutzen: keine falschen/verlorenen
   Aktionen oder wahrnehmbaren Hänger. Variante-A-Hinweisnavigation bleibt erhalten.

   Reproduzierbarer Einstieg in F-02: Farbe D, Zeile 2, Spalten 2–39 füllen;
   `38` muss ohne Rand-X markiert sein. In Spalte 38 mit D die Zeilen 2–38 und
   mit A Zeile 39 füllen: beide Spaltenhinweise `37 1` werden markiert. Hier zählt
   jeweils nur die eigene Linie, auch wenn andere Linien noch unvollständig sind.

Protokoll: Head/Artefakt/ZIP-Hash ____; Windows ____; Bildschirm ____; Client/Rahmen
____; tatsächliche Windows-Skalierung ____; UI/Zoom ____; Maus ____; Ergebnis und
Abweichung je 1–5 ____. Technische Rendermaße ersetzen diese Angaben nicht.

Ergebnis der realen Probe derzeit **nicht durchgeführt** und ausdrücklich nicht als
bestanden zu behandeln. Nach Review R1 hat der Eigentümer am 25.09.2026 die B-01-
Nacharbeit und den anschließenden Merge von PR #20 beauftragt. Damit ist die Probe für
diesen Merge kein verbleibendes Gate; A-H01 bis A-H07, Review-Nacharbeit und aktuelle
technische Prüfungen des finalen kombinierten Heads bleiben erforderlich. Kein neues
Gesamt-P1-Gate für unveränderte #12-Szenarien und kein Release aus dieser Entscheidung.
