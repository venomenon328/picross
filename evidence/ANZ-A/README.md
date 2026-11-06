# ANZ-A · befristete Revieworiginale für R01

Produkt-Head: `c624dc9972f9234fa0c1c08268acf57d0afe6a24`.
Basis: `0997be00b6969adde9d9c09ec83d6c0c1f2302f8`.
Produkt-PR: https://github.com/venomenon328/picross/pull/528.
Diese Dateien gehören ausschließlich zum separaten Reviewref und werden nicht integriert.

Empfänger: unabhängiger ANZ-A-R01-Reviewer. Zweck: Anzeige, Schrift, Dropdowns,
Bestätigung und Windows-Modusprobe selbst an den Originalen prüfen.
Geplantes Aufbewahrungsende: **13.11.2026**. Der Ref hat keine automatische TTL.
Nach R01 sind die reinen Belege im beauftragten Rückbau entbehrlich; bei weiter
offenem Gate am 13.11. Bedarf/Zustellung erneut prüfen. Kein Merge-PR für diesen Ref.

| Original | Konkrete Zuordnung |
| --- | --- |
| `settings-1080p.png` | 1920×1080 Client, UI100, Fenstermodus; `report.json` / `snapshots.settings-1080p` |
| `mode-options-720p-ui125.png` | 1280×720 Client, UI125, echtes geöffnetes HZ-Modusmenü; `visual.json` gleichnamiger Capture |
| `confirmation-720p-ui125.png` | 1280×720 Client, UI125, erreichbare Beibehalten-/Abbrechenkarte; `visual.json` gleichnamiger Capture |
| `ui-exclusive-1440p-125.png` | 2560×1440 Desktop/Viewport, UI125, tatsächlicher Modus 4 und deaktivierte Fenstergröße; `visual.json` gleichnamiger Capture |

Die PNGs sind unveränderte native Viewportoriginale, nach tatsächlichem Rendern
aufgenommen. Sie wurden vom Implementierer geöffnet und gesichtet. Es gibt keine
Filme oder vollständige Galerie. `files.json` bindet die ausgewählten Bytes.
Strukturierte W01-Snapshots ohne Zeile in dieser Tabelle sind Zustandsbeobachtungen,
keine zusätzliche Bildlieferung. Die kurze nachgelagerte UI-Probe in `visual.json`
verwendet denselben bytegleichen Spieler und denselben Produkt-Head.

`report.json` enthält 18 erfolgreiche W01-Assertions am synthetischen regulären
EXE/PCK: alle drei Modi, Annahme, Rücknahme, echte 15-s-Frist, Alt-Tab während
rahmenloser Vorschau, Betriebssystem-Maximieren/Resize, Prozessabbruch vor Annahme,
Neustart, letzter Fensterpreset und tatsächlicher Wechsel auf den zweiten Monitor.
`files` bindet die exportierte EXE/PCK; `source_code` wurde gegen den sauberen
Produkt-Head geprüft. `engine-*.jsonl`/`stdout-*.log` sind die vollständigen
Originale der drei erfolgreichen W01-Spielprozesse und der kurzen UI-Probe;
`os.jsonl` enthält die echten Win32-Eingaben. Der externe Beobachter schreibt
keinen Produktzustand und injiziert keine Viewportereignisse. Seine Quellen und
die konkreten lokalen Treiber sind als aktuelle technische Prüfinputs beigelegt.
Sie sind keine neue permanente Testsuite.

`environment.json` hält die echte Windows-/Monitorgeometrie: zwei 2560×1440-
Monitore mit effektiv 96 DPI; NVIDIA RTX 3070. Godots Koordinaten verschieben die
virtuelle Monitorursprungslage gegenüber Win32, daher beide Kontexte getrennt.
Nach Vollbild kann `DisplayServer.window_get_size()` beim Fenstermodus zwei Pixel
weniger melden als `Window.size`/Win32. `server_client`, `window_client` und der
unabhängige `win32_client` in `report.json` machen das sichtbar; die tatsächliche
zurückgekehrte Windows-Clientfläche wurde mit 1920×1080 bestätigt.

`display-information.log` belegt den ergänzenden lokalen Lauf am Produkt-Head:
136 erfolgreiche Checks einschließlich der neuen deterministischen Displayfälle.
Die endgültige Package-CI und ihr Test-Merge sind im PR gebunden; dieser lokale
Log ersetzt weder `native.graphics` noch die unabhängige R01-Sichtung.

Physische 4K-/16:10-/720p-Desktops und geänderte DPI wurden nicht behauptet.
Preset-/DPI-/Arbeitsbereichsgrenzen und Bestätigungslayout sind hierfür synthetisch
geprüft. W01 ist eine Implementiererprobe. R01 bleibt vor Merge unabhängig;
ANZ-A-M01 bleibt als persönliche Komfort-/Lesbarkeitsprobe nach Integration vor Release offen.
