# ANZ-A-N03 einschließlich N03-E01 · Originale für unabhängiges R04

Produkt-Head: `6f13c885a7e9e35e13765db4b366ac460316a494`. Main-Basis: `5d90b218e3c96c7cd133c2b6c5db39a65674ff5c`.

[Verbindliche N03-Entscheidung](https://github.com/venomenon328/picross/issues/527#anz-a-n03), [Draft-PR #528](https://github.com/venomenon328/picross/pull/528). Empfänger: unabhängiger ANZ-A-N03-R04-Reviewer. Geplanter Endpunkt **13.11.2026**; kein automatischer Git-Ref-Ablauf. Nach R04 im passend beauftragten Rückbau entfernen; bei offenem Gate Bedarf/Zustellung erneut prüfen. Kein Merge-PR für diesen Ref und keine Übernahme in den Produktbranch.

## Tatsächlich ausgeführt

Exportierter regulärer Windows-Spieler am sauberen Head oben, synthetischer Testkatalog, keine echten Saves. **79 Assertions erfolgreich** (74 Hauptprobe, 5 Ergänzung). Vier echte 1920×1080-/1280×720-Clientflächen × UI100/UI125, voller Dropdownraum ohne Hilfsplatzhalter, nur zwei aktive Hilfen, tatsächliche aktive Bakso-Fontinstanz von Katalog und Einstellungen bei beiden Skalen, nach aktueller Eigentümerpräzisierung N03-E01 ebenfalls Bakso für die Gruppen bei kleinerer Grundgröße 20 × UI, Scrollende und Moduspopup. Echte Win32-Maus-/Rad-/Tasteneingaben; rein lesender externer Beobachter mit Original-Viewportcaptures.

Gezielte zusätzliche Szenen: Fenstergrößenhilfe per Hover, Ansichtshilfe per Tastaturfokus und Escape; separate Hilfe bei deaktivierter Vollbildgrößenwahl; 720p/UI125-Vorschau und tatsächlicher Abbruch; echter Display-Präferenzschreibfehler durch Verzeichnis auf dem isolierten .tmp-Pfad mit intakten alten Bytes. Einstellungen und Hilfe kehren aus Katalog-/Rätselursprung tatsächlich zum Ursprung zurück; sichtbarer Text Zurück mit zielbezogenem Tooltip/Accessibilityname. Vor den Rätselrückwegen wurde eine echte Zell-/Historyaktion ausgeführt; Rückwege bewahren exakte Zellen, History/Cursor und semantische Ansicht. Regulärer WM-close beendet den Spieler nach Flush.

Windows 11 (10.0.26200), NVIDIA RTX 3070, zwei 2560×1440-Desktops, effektiv 96 DPI/Skala 1.0. Keine physische 4K-/16:10-/andere-DPI-Abnahme, kein Chromium. Keine erneute vollständige W01-/N02-Matrix; Controller-/Timeout-/Fallback-/Save-/Exitregressionen bleiben im ausgewählten Paketumfang. Finale Head-CI wird im PR separat gebunden.

Die lokale Informationsprobe meldet **302 Checks/0 Fehler**. Sie wurde nach Commitabschluss am sauberen finalen Head ausgeführt; [source-binding.json](source-binding.json) und die Export-/Belegskripte vergleichen sämtliche kopierten GDScriptbytes mit dem sauberen Head. Ihr synchron stabilisierter Buchtest ist kein Zeit-/Bewegungsnachweis. Auch sämtliche Windowsoriginale wurden nach Commit/Push auf diesem Head aufgenommen. Die ergänzenden 1080p/UI125-Ansichtshilfe und rahmenlose Vollbildvorschau decken die entsprechenden früheren N02-Großbildzustände am neuen Endstand ab; keine Umdeutung alter Originale.

[Exportbindung](export.json) umfasst Quell-GDScripts, kompletten game/-Tree, tatsächliche Fontbytes und EXE/PCK-Hashes. [Bericht](n03-report.json), [Eingaben](os.jsonl), [Enginezustände](engine.jsonl), [Engineausgabe](stdout.log), [Beobachter](observer.gd), [Treiber](n03_gui.py), [Win32-Helfer](win.py), [Launcher](launch.py), [Exporter](export.py). Vollständige Originalspuren, keine Ausschnitt-/Montage-/Skalierungsersatzbelege.

## Binärzugang und unabhängige Sicht

Alle folgenden Original-PNGs wurden vom Implementierer direkt geöffnet. Größen/SHA-256 stehen im [Manifest](manifest.json). Öffentlicher binärer Rückdownload wird zusätzlich als download-verification.json dokumentiert. Originale vom konkreten Belegcommit per raw.githubusercontent.com, Contents mit Raw-Medientyp oder echtem Git-Checkout laden, Bytes prüfen und Bilder direkt öffnen.

Bekannte Empfängergrenze: Der frühere ChatGPT-Contents-/UTF-8-Zugang aus N02-R03 konnte große Bilder nicht liefern. Derselbe textgebundene Zugang wird durch einen neuen Ref oder ZIP nicht binärfähig. R04 benötigt einen funktionierenden Binärdownloader/Bildanzeiger oder tatsächlich zugängliche Originalanhänge. Diese Zustellung schließt die unabhängige Sicht nicht selbst; N02-R03-A01 ist am neuen Endstand durch R04 zu prüfen. Historische N02-Berichte/Bilder behalten ihre alte Bindung.

| Original | Client | UI | Modus / Szene |
| --- | --- | --- | --- |
| [catalog-title-1080p-ui100.png](catalog-title-1080p-ui100.png) | 1920×1080 | 100 % | window; album; Vorschau False; Scroll 0 |
| [settings-1080p-ui100.png](settings-1080p-ui100.png) | 1920×1080 | 100 % | window; album; Vorschau False; Scroll 0 |
| [settings-1080p-ui125.png](settings-1080p-ui125.png) | 1920×1080 | 125 % | window; album; Vorschau False; Scroll 0 |
| [settings-720p-ui100.png](settings-720p-ui100.png) | 1280×720 | 100 % | window; album; Vorschau False; Scroll 0 |
| [settings-720p-ui125.png](settings-720p-ui125.png) | 1280×720 | 125 % | window; album; Vorschau False; Scroll 0 |
| [settings-720p-ui125-bottom.png](settings-720p-ui125-bottom.png) | 1280×720 | 125 % | window; album; Vorschau False; Scroll 144 |
| [size-hover-720p-ui125.png](size-hover-720p-ui125.png) | 1280×720 | 125 % | window; album; Vorschau False; Scroll 0 |
| [view-focus-720p-ui125.png](view-focus-720p-ui125.png) | 1280×720 | 125 % | window; album; Vorschau False; Scroll 144 |
| [mode-popup-720p-ui125.png](mode-popup-720p-ui125.png) | 1280×720 | 125 % | window; album; Vorschau False; Scroll 0 |
| [fullscreen-size-help-ui125.png](fullscreen-size-help-ui125.png) | 2560×1440 | 125 % | borderless; album; Vorschau False; Scroll 0 |
| [preview-window-720p-ui125.png](preview-window-720p-ui125.png) | 1280×720 | 125 % | window; album; Vorschau True; Scroll 0 |
| [storage-error-720p-ui125.png](storage-error-720p-ui125.png) | 1280×720 | 125 % | window; album; Vorschau False; Scroll 0 |
| [catalog-origin-help-back.png](catalog-origin-help-back.png) | 1280×720 | 125 % | window; album; Vorschau False; Scroll 0 |
| [work-origin-settings-back.png](work-origin-settings-back.png) | 1280×720 | 125 % | window; work; Vorschau False; Scroll 0 |
| [work-origin-help-back.png](work-origin-help-back.png) | 1280×720 | 125 % | window; work; Vorschau False; Scroll 0 |
| [settings-1080p-ui125-view-help.png](settings-1080p-ui125-view-help.png) | 1920×1080 | 125 % | window; album; Vorschau False; Scroll 0 |
| [preview-borderless-ui125.png](preview-borderless-ui125.png) | 2560×1440 | 125 % | borderless; album; Vorschau True; Scroll 0 |

Ergänzung: [Bericht](supplement-report.json), [Eingaben](supplement-os.jsonl), [Engine](supplement-engine.jsonl), [Ausgabe](supplement-stdout.log), [Treiber](supplement.py).

[Lokales Informationsoriginal](information.log), [Ergebnis](information.json), [Prüfereinstieg](probe.py).
