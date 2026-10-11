# PERF-B · Nativer Windows-Vergleich

Vorher: `a83ecf5db0800d198bb870932bf0365341aabb28`; aktueller Nachher-Quellstand:
`8ef3a1b0552939d2951179c4c9767126be601092`. Zehn F02-Kontexte, dünn/dicht,
Hover/Füllstrich/X-Strich, Effekte an/aus: 120 Vergleichsfälle, je drei
Wiederholungen mit sechs Warm-up-Frames und 36 Rohintervallen. Messplan in
[plan.json](plan.json), vollständige Verteilungen in [b1-windows.json](b1-windows.json),
Rohintervalle, Logs und gültige eigene Schema-1-Spielstände in
[b1-windows-raw.zip](b1-windows-raw.zip). Keine normalen Benutzersaves.

Windows 11 Build 26200, RTX 3070, NVIDIA 596.49, Godot 4.7.2, OpenGL3,
System-DPI 96. Tatsächliche Clientfläche, DPI, VSync, Bildschirm und Zoom
stehen je Kontext in den Rohdaten. Die beiden Vergleichsrollen liefen auf
demselben Host; während der aktuellen Nachhermessung lief kein anderer nativer
Godot-Prüfprozess. Keine Aussage über andere Hardware oder physische Eingabelatenz.

## Dichter F02-Hover, Effekte aus

Alle Zeiten in Millisekunden. CPU ist Skript-Zeichenaufbau; Wall ist der Abstand
zwischen `frame_post_draw`-Signalen, keine GPU- oder Präsentationsdauer.

| Fenster / UI / Ansicht / Wunsch | Ist px | CPU p50 vorher → nachher | Wall p50 vorher → nachher | Wall p99 nachher |
| --- | ---: | ---: | ---: | ---: |
| normal / 100 / G / 16 | 16.00 | 18.265 → 0.022 | 47.668 → 16.681 | 19.724 |
| normal / 100 / G / 18 | 18.00 | 168.070 → 0.025 | 314.205 → 16.682 | 22.720 |
| normal / 100 / G / 20 | 18.77 | 158.382 → 0.024 | 291.507 → 16.680 | 22.587 |
| normal / 100 / G / 72 | 18.77 | 154.558 → 0.020 | 291.254 → 16.678 | 21.104 |
| maximized / 100 / G / 72 | 25.71 | 158.863 → 0.021 | 298.327 → 16.680 | 21.974 |
| normal / 125 / G / 18 | 17.06 | 18.114 → 0.024 | 48.033 → 16.678 | 22.378 |
| maximized / 125 / G / 20 | 20.00 | 168.931 → 0.024 | 319.594 → 16.679 | 22.567 |
| maximized / 100 / V / 20 | 20.00 | 170.246 → 0.020 | 318.895 → 16.684 | 21.586 |
| normal / 125 / V / 16 | 14.81 | 18.423 → 0.021 | 48.606 → 16.679 | 20.843 |
| maximized / 125 / V / 72 | 21.75 | 168.543 → 0.022 | 317.860 → 16.679 | 23.786 |

Die frühere Sprungstelle bei 18 px erscheint im ruhenden Hover nicht mehr.
Gewünschte 20/72 px im normalen G/UI100-Fenster sind nur 18,77 px; es wurde
keine größere Geometrie erzwungen. Maximiert sind 20 bzw. 25,71 px erreichbar.

## Aufbau, Spitzen und Ressourcen

Die CPU-Abdeckung ist bewusst konservativ verschieden: vorher nur der alte
Stiftzeichner, nachher alle neuen Ebenen einschließlich Synchronisierung und
Board. Nullarbeitsintervalle bleiben enthalten. Der unveränderte Messadapter
ruft nach dem Warm-up `clear_effects()` auf; dadurch enthält jede Wiederholung
noch einen angeforderten Board-Neuaufbau. Beim Hover sind daher Board-Signale
`[1,0,0]` (Board/Marks-Wurzel/Miniatur) und CPU-p99 von etwa 13–16 ms enthalten.
Das ist kein kontinuierlicher Neuaufbau der ruhenden Chunks. Die separate native
Strukturprobe wartet diesen Aufbau ab und verlangt beim Hover null Ruhechunk-,
Board- und Miniatur-Neuzeichnungen; eine absichtliche Vollinvalidierung fällt durch.

| Dichter Strich / Effekte | CPU p95 nachher, Kontextspanne ms | Wall p99 vorher, Kontextspanne ms | Wall p99 nachher, Kontextspanne ms |
| --- | ---: | ---: | ---: |
| fill / aus | 0.000–0.000 | 113.569–402.712 | 74.762–87.590 |
| fill / an | 0.979–1.456 | 140.890–626.394 | 85.350–102.974 |
| x / aus | 0.000–0.000 | 124.938–409.612 | 83.085–93.703 |
| x / an | 0.687–0.829 | 138.450–671.469 | 83.146–104.449 |

Ohne Effekte sind CPU-p50/p95 bei Strichen null, weil nur das tatsächliche
Änderungsereignis Arbeit auslöst; daraus folgt keine kostenlose Eingabe.
Die Strichspitzen bleiben sichtbar: synchroner Press/Drag/Release-Dispatch
enthält Modell-, Hinweis-, History- und Speicherarbeit; sein p99 liegt nachher
bei ungefähr 48–71 ms im dichten Fall. Hinzu kommen Board-/Chunk-Neuaufbau und
Frameabstand. Animationstakte selbst zeigen keinen neuen 18-px-Sprung. Das
ist keine allgemeine FPS-Garantie oder persönliche Flüssigkeitsabnahme.

Der Texturspeichermonitor liegt je Kontext nachher um 65.207.680 Bytes höher
(nachher insgesamt 100.253.518–115.677.686 Bytes). Die sechs Atlasbilder belegen
48.906.240 dekodierte Bytes; der Engine-Monitor ist damit nicht gleichzusetzen.
GPU-Dauer und tatsächlicher VRAM-Verbrauch wurden nicht separat gemessen.
Rohdaten enthalten Draw-Call-/Objektzähler, statischen Speicher und jede
Wiederholung. Die unabhängige Laufzeitprobe prüft bei 24 Seiten-/Zoomwechseln
periodisch stabile Knoten-/Textur-/Chunkzahlen sowie ein Speicherplateau.

F03/F07 bleiben ausschließlich theoretische 100×100-Zusatzmessungen auf dem
älteren B-Head `f0f5791f87a565689dcc441a5a4f7643a49ba3b0`; 24 zugehörige
Vergleichsfälle sind gesondert markiert. Das Roharchiv bewahrt auch die damaligen
F02-Messungen, ersetzt damit aber nicht den aktuellen 50×50-Katalognachweis.

## Herkunft und Lieferung

[a-reproduction.json](a-reproduction.json) bindet die frische Herstellung:
22/22 Dateien einschließlich Manifest byteidentisch zu PERF-A. A-Lieferhead,
Herstellerquelle und ursprüngliche Einzelhashes bleiben unverändert.
`tools/perf_b_report.py` prüft Roharchiv, Inventar, Quellbindungen, Zusammenfassung,
Messplan/Harness und die vier unveränderten gemessenen Runtime-Dateien. Die CI
liefert Bericht, Roharchiv und Reproduktionsprotokoll getrennt vom Spieler.

Die aktuellen nativen Bild-/Zeitfolgen und zwölf SL-Bilder stehen im technischen
Product-Artefakt. Exakte finale Head-/Basis-/Run-/Download-Bindungen folgen in
[Issue #68](https://github.com/venomenon328/picross/issues/68) und
[Draft-PR #66](https://github.com/venomenon328/picross/pull/66). Unabhängiges
PERF-B-R01 und persönliche PERF-M01/SL-M01 bleiben vor Merge offen.
