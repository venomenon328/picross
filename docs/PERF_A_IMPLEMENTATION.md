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
[Messprogramm](../prototypes/p1/tests/perf_a_baseline.gd) wird dort ergänzt;
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
die Rohintervalle bleiben erhalten. Laufresultate und Commitbindung folgen nach
tatsächlich erfolgreichem vollständigem Versuch im Issue/PR.

## Abnahmegrenze

PERF-A01–A04 verlangen zusätzlich A2-Herstellung, Bild-/Negativtests,
Reproduktion, native Einzelzell-/Flächen-/Bewegungsprobe, aktuellen gesamten
CI-Diffumfang und getrennten Selbstreview. Diese Datei behauptet deren Erfolg
erst mit den gebundenen Ergebnissen. SL-R02/B-01 bleibt historisch technisch
behoben; neue kombinierte unabhängige Prüfung, persönliche SL-M01/PERF-M01 und
gesonderte Mergefreigabe bleiben vor einem späteren Merge offen. Kein Release.
