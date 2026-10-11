# PERF-A · gebundene Messung und Atlasgrundlage

Auftrag [#67](https://github.com/venomenon328/picross/issues/67), bestehender
Branch `feat/65-sidebar-frames`, Draft-PR #66 gegen main. Der
[Zellrendering-Vertrag](CELL_RENDERING.md) aus Spezifikationscommit
`4a7573f3adaf7cef6df08adafb6caa767da02ad2` ist übernommen. A behebt PERF-01
noch nicht; reguläre Atlasintegration und Ebenentrennung gehören zu #68.

## A1: vor dem optimierten Vergleich festgelegter Versuch

Der [endliche Messplan](../examples/perf_a/plan.json) ist seit `ec5e1ad`
versioniert. Unveränderte Renderer aus `a83ecf5` und integrierter Basis `e323dcf`
werden durch Git-Archive in temporäre Projekte kopiert. Das eigene
[Messprogramm](https://github.com/venomenon328/picross/blob/0f89f08729539bbb4a02a590cbd18e58fbbda305/prototypes/p1/tests/perf_a_baseline.gd) wird dort ergänzt;
Produktquellen und normale Benutzerprofile werden nicht verändert.

F02 bleibt einschließlich Definition, Lösung und Proof unverändert. Der dichte
synthetische Stand enthält 1216 Füllungen, 304 X und 80 unbekannte Felder. Die
dünne Kontrolle verwendet dieselbe Wertfolge nur an durch 31 teilbaren Indizes.
Beide entstehen als echte Transaktion ab unbekanntem Raster. Godots vollständiger
Schema-1-Prüfer und ein eigener Python-Historyoracle prüfen die gespeicherten
Snapshots; eine veränderte Matrix bei unveränderter History muss scheitern.
Dies ist kein Originalsave des Eigentümers und kein deduktiv hergeleiteter Spielstand.

Zehn Displaykontexte kombinieren beide echten Fensterzustände, UI100/125, G/V
und Wünsche 16/18/20/72. Wirksames Zellmaß und Fit werden separat protokolliert;
unerreichbare Werte bleiben fitbegrenzt. Beide Quellstände verwenden zunächst
`overview=false`; zwei zusätzliche Mainkontrollen verwenden `overview=true`.
Jeder Kontext prüft dünn/dicht, Effekte an/aus, Hover sowie 40-zellige Füll-/X-Striche
über synthetische native Viewportereignisse. Sechs Warm-up-Frames, drei Wiederholungen
und je 36 Rohintervalle sind vorab fixiert. Der Strich startet an Frame 0 nach
Warm-up; danach wird sein vollständiger Übergang einschließlich Ruhe gemessen.

Die Messung trennt Wall-Abstände zwischen `frame_post_draw`, CPU-Zeichenaufbau
des bisherigen Stiftzeichners und CPU-Ereignisdispatch. Zeichen-Signale zählen
tatsächliche Ausführungen von Board, Markierungen und Miniatur; mehrere zusammen-
gefasste `queue_redraw`-Aufrufe sind damit nicht einzeln gezählt. Effektzahl,
Godot-Static-/Texturspeicher und echte Anzeigeparameter werden mitgespeichert.
Wall-Abstände sind keine GPU-Zeit oder garantierte Präsentationszeit. Physische
Eingabe-zu-Pixel-Latenz und GPU-Dauer sind nicht erfasst. VSync bleibt unverändert.
Es gibt keine neue FPS-Garantie; 300-s-Prozess- und 20-/75-MB-Artefaktgrenzen bleiben.

Reproduktion unter nativem Windows mit geprüftem offiziellem Editorarchiv:

```powershell
python tools/perf_a.py baseline --cache-dir D:/AppData/Local/Temp/picross-rp6-cache --output-dir artifacts/perf-a-baseline
```

Den Cachepfad an den eigenen externen Archivcache anpassen, Ausgabe immer neu.
`--only-context 0` ist eine Diagnose, kein vollständiger Liefernachweis.
Der Harness bindet Plan-/Script-/Engine-/Renderer- und Rohdateihashes.
`summary.json` aggregiert p50/p95/p99/Maximum aus den drei Wiederholungen;
die Rohintervalle bleiben erhalten.

### Native A1-Ergebnisse · 11.10.2026

Der vollständige Lauf verwendet Harness `b25ab7c`: 22 Kontexte, 264 Fälle,
792 Wiederholungsdatensätze, 28.512 Rohintervalle, keine gemeldeten Fehler.
Die ergänzende 16-px-Eingabekontrolle prüft beide unveränderten Quellrollen mit
zusätzlichen Assertions für alle 40 Änderungen und jedes Ziel der Zeile.
Sie ersetzt keine Kontexte der vollständigen Ausgangsmessung. Die erste
ergänzende Kontrolle scheiterte an einer neuen `Window.vsync_mode`-Abfrage;
die korrigierte Fassung verwendet `DisplayServer.window_get_vsync_mode`.

[Dauerhafter Ergebnisindex](../examples/perf_a/a1-windows.json) und
[Rohdaten einschließlich aller Verteilungen und Harnessquellen](../examples/perf_a/a1-windows-raw.zip)
binden die tatsächlich geprüften Fassungen. Originale F02-Definition und Proof
sind unverändert. Dünn: 40 Füllungen, 10 X, 1550 unbekannt; dicht: 1216/304/80.

Maschine: Ryzen 7 5800X, RTX 3070, Windows 11 Pro Build 26200, NVIDIA 596.49 /
Treiber 32.0.15.9649, Godot 4.7.2 GL Compatibility/OpenGL3. Monitor 2560×1440;
normaler Client 1920×1080, maximierter Client 2560×1369, Windows-DPI 96 /
Skalierung 100 %. UI100/125 wird unabhängig davon variiert. Der Hardwarebericht
enthält auch den vom Treiber gemeldeten Refresh; die ergänzende native Kontrolle
bindet die Godot-Refresh-/VSync-Abfrage: 59,951 Hz, VSync-Modus 1. Die separate
Adapter-CIM-Abfrage meldet 143 Hz; beide Rohangaben bleiben erhalten und werden
nicht zu einer behaupteten physischen Präsentationsrate vereinheitlicht.
Diese Messung verwendet den nativen
Editor am archivierten Produktprojekt, keine nachträglich rekonstruierte Eigentümer-EXE.

Dichter F02-Hover, Effekte aus, je 108 Samples; Zeiten in Millisekunden:

| Quelle / Kontext | Istmaß | CPU Aufbau p50 / p95 / p99 / Max | Wall p50 / p95 / p99 / Max |
| --- | ---: | --- | --- |
| a83, normal G/UI100, Wunsch16 | 16 | 17,10 / 17,86 / 18,38 / 18,42 | 43,03 / 44,94 / 45,80 / 46,43 |
| a83, normal G/UI100, Wunsch18 | 18 | 148,39 / 154,82 / 158,43 / 173,32 | 275,57 / 285,84 / 297,10 / 314,07 |
| a83, normal G/UI100, Wunsch20 | 18,77 | 147,69 / 153,85 / 158,70 / 159,13 | 275,19 / 287,15 / 290,88 / 291,72 |
| a83, maximiert G/UI100, Wunsch72 | 25,71 | 148,80 / 156,36 / 165,23 / 186,95 | 277,30 / 290,15 / 320,98 / 325,00 |
| main, normal G/UI100, Wunsch18, overview=false | 18 | 159,49 / 188,33 / 206,56 / 208,89 | 297,63 / 342,63 / 361,97 / 377,63 |
| main, normal G/UI100, Wunsch72, overview=true | 18,77 | 18,98 / 20,93 / 22,65 / 25,74 | 49,64 / 52,77 / 54,45 / 59,74 |

Bei beiden Quellen zeichnen Board und Markierungen im Hover jeden Sampleframe
neu; Miniatur bleibt dabei ruhig. Der deutliche Sprung ab 18 px und die echte
Main-Overviewkontrolle stützen den detaillierten Stiftaufbau als Engpass. Das
beweist keine alleinige Ursache sämtlicher Wall-Kosten und keinen Sidebarfehler.
Auch der vereinfachte dichte Fall benötigt deutlich mehr Wallzeit als seine
gemessene Skriptaufbauzeit; übrige Engine-/Canvas-/Treiber-/Präsentationsanteile
sind hier nicht weiter aufgeteilt. Der sequenzielle Basisvergleich ist kein
Beleg für einen kleinen prozentualen Sidebarunterschied. B muss alle Kosten am
gleichen Plan erneut messen und darf CPU-/Wallwerte nicht als physische Latenz ausgeben.

## A2: reproduzierbare Füll-/X-Atlanten

[Herstellungsplan](../examples/perf_a/atlas-plan.json),
[Quellen und Befehle](../examples/perf_a/README.md) und
[Manifest](https://github.com/venomenon328/picross/blob/0f89f08729539bbb4a02a590cbd18e58fbbda305/prototypes/p1/perf_a/atlases/manifest.json) binden die Übergabe.
Der unveränderte Projektstift aus `a83ecf5` wird offline unter nativem Windows /
Godot 4.7.2 OpenGL3 in Schwarz-/Weiß-Basisbilder ausgerendert. Alle neun
[Originalbilder](../examples/perf_a/sources) bleiben gespeichert. Pillow exakt
12.3.0 erzeugt daraus sechs neutrale RGBA8-Koeffizientenmasken, ohne fremde Assets
oder Modellaufruf. R trägt die Grundfarbe einschließlich dunkler Kontur, G die
weißen Spuren, A die Deckung. Der gemeinsame kleine Shader rekonstruiert Farbe;
eine graue Textur mit einfacher Multiplikation würde helle Spuren verfälschen.

Festgelegt nach Einzelzell-, Flächen-, Bewegungs- und Ressourcenprobe:

| Parameter | Entscheidung und Prüfergebnis |
| --- | --- |
| Varianten / Zeitbilder | 16 Varianten, 24 Zeitbilder, 210 ms pro Zelle. 384 Bilder je Atlas. Mittel/groß besitzen je 16 verschiedene fertige Füllungen; X besitzt in allen Stufen 16 Endformen. Kleine Füllungen behalten bewusst die bisherige einfache Rechteckform. |
| Stufen | Logische Referenzen 16/24/72 px, Bildauflösungen 32/64/96 px; kleine Stufe unter 18, mittlere bis einschließlich 36, große darüber. Je ein Füll-/X-Atlas, keine Palettenkopien. |
| Sichere Innenfläche | Füllinnenfläche auf echte Zelle minus 2 px je Rand abbilden; X verwendet die Zellbox. 2 px transparentes Atlaspadding, Koeffizientenrand ohne Alphaausweitung. Linearfilter, kein Repeat/Mipmap, verlustloser Import. |
| Identität / Zeit | SHA-256 aus Renderfassung, Rätsel-ID, Revision und Zellkoordinate; erstes 32-Bit-Wort modulo 16. Zeitindex aus verstrichenen Mikrosekunden, Endframe 23. Farbe, Zoom, Redraw und History sind keine Eingaben; kein neues Savefeld. |
| Vorschau / Warten / Ruhe | Identische Variante und Endform, Vorschau/Warten 56 % Deckung. Aktiver Aufbau zeigt räumliche Schraffur beziehungsweise X-Zug eins vor zwei, ohne volle Unterzeichnung. |
| Ressourcen | 326.203 Bytes PNG, 48.906.240 Bytes dekodierte RGBA-Daten, sechs Texturen. Diese endliche Obergrenze benötigt keine Palette-/Zellkopien. Regulärer Spielerexport enthält keine A-Ressourcen. |

Die räumliche Probe weist wachsende bedeckte Flächen nach; Startbild ist leer.
Negativkontrollen verändern volle Unterzeichnung, globale Fadefolge, X-Reihenfolge,
Endvarianten, Padding, Datei-/Importidentität, Farbmaterial und Variantenwahl.
Zusätzlich werden leere und eingefrorene native Bewegungsbilder zurückgewiesen.
Native importierte Pixel müssen exakt den Manifesthash treffen. Reale
Grundfarben einschließlich dunkler Referenz, Kontur und weißer Spuren werden über
alle Zeitbilder gegen eine unabhängige Rechnung aus den gespeicherten
Schwarz-/Weiß-Originalen verglichen. Diese Rechnung verwendet weder den Shader
noch dessen Maskendekodierung. Zusätzlich gilt auf dem nativen Windows-
Herstellungsweg der strenge Vergleich mit dem frisch gezeichneten Originalstift;
maximaler Kanalfehler beträgt dort
0 bei kleiner und 1 von 255 bei mittlerer/großer Stufe. Vorschau entspricht dem
gleichen Bild mit 56 % Deckung innerhalb der dokumentierten Quantisierung.

### Native A2-Ergebnisse · 11.10.2026

[Ergebnisindex](../examples/perf_a/a2-windows.json) und
[Rohbilder, Logs und Reproduktionsbelege](../examples/perf_a/a2-windows-raw.zip)
binden die tatsächlichen Scripts, Masken und Prüfdateien. Zwei frische native
Herstellungen sind über alle 22 Original-/Derivat-/Import-/Manifestdateien
bytegleich; reine Ableitung ab gespeicherten Quellen reproduziert alle sechs
PNG-Dateien exakt. Zwei neue native Probeprozesse vergleichen dieselben 1600
Zellidentitäten nach Neustart. Die JSON-Zahlenrepräsentation wird kanonisch
verglichen, damit die vom Parser erzeugten Float-Varianten keine falsche
Array-Ungleichheit erzeugen.

Die native Fitprobe über alle neun Blätter, UI100/125 und G/V bei maximiertem
2560×1369-Client ergibt gültige Istmaße von 5,1 bis 57,73 px. Die Flächenprobe
prüft zusätzlich 8/14,81/16/17,06/17,99/18/18,77/20/21,75/24/25,71/26,77/36/48/72 px:
34 Füll-/X-Flächenfälle, transparente Fugen und echte native Clipränder.
72 px ist eine zusätzliche Ressourcengrenzprobe, kein behaupteter erreichbarer
Produktzoom. Bewegungsfolgen zeigen beide Markierungsarten mit 40 Zellen,
180-ms-Staffel und verstrichener Echtzeit bis 450 ms. Wartende letzte Zellen
werden gegen die abgeschwächte Endform, der Schluss gegen alle exakten Endbilder
geprüft; mehrere verschiedene Zwischenbilder sind zwingend.

Eigene Sichtung der nativen Originalbilder und heller Kontrollmontagen:
mittlere und große Füllungen zeigen Stiftspuren und unterscheidbare Konturen,
ohne regelmäßigen Block gleicher Varianten. Die 16er-Auswahl wiederholt sich
erwartungsgemäß, ohne feste Rasterperiode. Nichtganzzahlige Fugen bleiben offen,
keine benachbarten Zeitbilder oder Farbsäume sichtbar. Bei 5,1 px reduziert sich
die sichere Füllinnenfläche erwartungsgemäß auf etwa einen Pixel; eine detaillierte
Stifttextur ist dort nicht sinnvoll. X bleibt erkennbar. 24 Zeitbilder zeigen
sichtbaren räumlichen Aufbau; die native Folge erreicht ohne Formwechsel die
Endbilder. Das beurteilt die isolierten Ressourcen, nicht die Flüssigkeit des
noch unveränderten regulären Spielers.

Die anfängliche Bewegungsprobe aktualisierte ihren unsichtbaren SubViewport nicht;
deren leere Bilder sind kein gültiger Bewegungsnachweis. Der finale Probeweg nutzt
`UPDATE_ALWAYS` und unabhängige Bildprüfungen. Ebenso sind der korrigierte native
Float-Dateiname und kanonische Neustartvergleich in den finalen Script-Hashes
gebunden. Fehlversuche werden nicht als erfolgreiche Läufe gezählt.

Der erste Gesamt-CI-Lauf zu `d768aff` scheiterte in der A2-Farbgegenprobe:
erneut unter Mesa/llvmpipe gezeichnete Polygonpixel waren nicht identisch mit dem
Windows-Herstellungsbestand (maximale Kanalabweichung 255). Eine portable
Pixelidentität des ursprünglichen Geometriezeichners über GPU-Treiber war nicht
vereinbart. Der finale unabhängige Farb-/Alphaoracle verwendet deshalb überall
die gespeicherten Originalbasisbilder und unverändert höchstens vier Kanalwerte
Quantisierungstoleranz. Windows prüft zusätzlich weiterhin den frischen Stift
mit derselben strengen Grenze. Die frischen Originalvergleiche anderer Treiber
bleiben als Diagnose protokolliert; sie ersetzen keine native Windows-Abnahme.
Das ist keine erhöhte Farbtoleranz. A2-Fehlerberichte nominieren nun auch die
tatsächlichen Probe-/Farb-/Bewegungsbilder für die begrenzte Fehlerdiagnose.

## Abnahmegrenze

PERF-A01–A04 erhalten A1/A2 samt eigenen Bild-/Negativtests, Reproduktion und
nativen Einzelzell-/Flächen-/Bewegungsproben. Aktuelle CI für den gesamten
PR-Diff und der getrennte Selbstreview werden commitgebunden in Issue #67 / PR #66
dokumentiert; lokale Ressourcenproben allein ersetzen diese nicht.
SL-R02/B-01 bleibt historisch technisch
behoben; neue kombinierte unabhängige Prüfung, persönliche SL-M01/PERF-M01 und
gesonderte Mergefreigabe bleiben vor einem späteren Merge offen. Kein Release.
