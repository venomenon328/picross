# ANZ-A-N02 · Originale für unabhängiges R03

Produkt-Head: `2c988cb1d58d75bacd3c8429981e80304816fccf`. Main-Basis: `5d90b218e3c96c7cd133c2b6c5db39a65674ff5c`.

[Verbindliches Paket ANZ-A-N02](https://github.com/venomenon328/picross/issues/527#anz-a-n02), [Draft-PR #528](https://github.com/venomenon328/picross/pull/528). Empfänger: unabhängiger ANZ-A-N02-R03-Reviewer. Geplantes Ende **13.11.2026**; Git-Ref ohne automatische TTL. Nach R03 im beauftragten Rückbau entfernen, bei weiter offenem Gate Bedarf/Zustellung erneut prüfen. Kein Merge-PR; diese Dateien werden nicht in den Produktbranch übernommen.

**Aktueller Review-Head:** `ce729e130f13b0a43c723c8d2045e9767d801fad`. [Bytebindung](head-binding.json): kompletter `game/`-Baum identisch zum tatsächlich ausgeführten Head oben. Danach nur Paketplan-Prosa und Dokumentformatierung; Originalberichte bleiben unverändert an ihren ausgeführten Head gebunden. Finale Package-CI wird separat am Review-Head geprüft.

[Öffentlicher Binär-Rückdownload](download-verification.json): alle 36 manifestgebundenen Dateien, 30.579.370 Bytes, darunter sieben Dateien über 1 MiB. Die großen zurückgeladenen 1080p-/Vollbild-/Vorschauoriginale wurden erneut direkt in Originalauflösung geöffnet. Kein bekannter Zugriffsvorbehalt; der Reviewer benötigt einen binärfähigen Downloader und Bildanzeiger.

## Tatsächlich ausgeführt

Exportierter Windows-Spieler aus sauberem Produkt-Checkout mit synthetischem Katalog und regulärem Buchroot. `export.json` bindet alle Produkt-GDScripts sowie EXE/PCK per SHA-256. Externer rein lesender Beobachter als isolierter Autoload; echte Win32-Maus-/Rad-/Tasteneingaben. Keine echten Saves. Windows 11 (10.0.26200), NVIDIA RTX 3070, zwei 2560×1440-Desktops, effektiv 96 DPI/Skala 1.0. Keine physische 4K-/16:10-/andere-DPI-Probe und kein Chromium.

55 positive Assertions in `n02-report.json`: vier tatsächliche Client/UI-Kombinationen; zwei verbundene HZ-Gruppen und Fraunces-600-Titel/28; sichere mittige Inlinezeilen, Scrollende, UI100→125→100, Fokus-/Hoverhilfe und Escape, vollständige Popupwerte samt Außenklick, Tooltipabbau bei Popup/Seitenwechsel, Modus 0/3/4, Vorschauannahme/-abbruch, 15-s-Timeout und echter Schreibfehler durch Verzeichnis auf dem isolierten `.tmp`-Pfad. Fehlerrollback erhielt die vorherigen bestätigten Preferencebytes. Bestätigung auch in echter 720p/UI125-Clientfläche bedient.

Weitere fünf positive Assertions in `restart-report.json`: frischer exportierter Prozess mit demselben isolierten Profil lädt Fenster/1280×720, UI startet mit 100 %; echter Rätselursprung → Einstellungen → UI125 → Rückkehr erhält Zellen, History/Cursor und semantische Hinweisansicht; regulärer WM-close endet nach Flush. Insgesamt 60 echte Windowsassertions. Getrennte Neustartspuren bewahren die Prozesszuordnung.

Die gezielte P12-/Z2-Komponentenprobe liefert 3705 Checks/0 Fehler (`core.log`, Einstieg `n02_core.gd`), am bytegleichen finalen Produktcode. Sie stabilisiert das Buch synchron und ist kein zeitlicher Bewegungsnachweis. Aktuelle Package-CI am exakten Head mit `native.catalog` und `native.graphics` wird im PR separat gebunden. Der ältere lokale Informationslauf hatte 269/0 vor der kleinen Titelkontur-/Testaufbaukorrektur; sein Bericht wird hier nicht als finaler Headnachweis ausgegeben.

Diagnose: Die erste Ersatz-Testvorbereitung via restore_view hob eine absichtlich schmale Hinweisprobe auf. Korrigiert durch synthetische Leseankerdaten ohne Layout; kein produktiver Resetbefehl. Ein früher Fokus-/Popup-Startversuch gehörte zum vorangehenden Diagnoseexport. Hier stehen ausschließlich finale UI-Originale samt vollständigen Spuren. Niedrige DisplayServer-Größenwerte nach Vollbild können von Window.size/Backend abweichen; Beobachtungen stehen getrennt im Bericht. Keine neue W01-Vollmatrix oder Hardwareabnahme aus dieser UI-Nacharbeit.

## Unveränderte Bilder

Alle folgenden PNG-Dateien wurden vom Implementierer geöffnet. Keine Umkodierung, Montage oder Größenänderung zur Zustellung. Unabhängiger Reviewer: Originale selbst binär herunterladen und ansehen. Bei >1 MiB genügt die normale textgebundene Contents-Antwort nicht. Raw-Abruf vom konkreten Belegcommit, Contents mit Raw-Medientyp oder Git-Checkout; Bytezahl/SHA-256 gegen [Manifest](manifest.json) prüfen. Tatsächlicher öffentlicher Rückdownload wird im PR gebunden.

| Original | Client | UI | Modus / Szene |
| --- | --- | --- | --- |
| [settings-1080p-ui100.png](settings-1080p-ui100.png) | 1920×1080 | 100 % | window; Vorschau False; Scroll 0 |
| [settings-1080p-ui125.png](settings-1080p-ui125.png) | 1920×1080 | 125 % | window; Vorschau False; Scroll 0 |
| [settings-1080p-ui125-view-help.png](settings-1080p-ui125-view-help.png) | 1920×1080 | 125 % | window; Vorschau False; Scroll 0 |
| [settings-720p-ui100.png](settings-720p-ui100.png) | 1280×720 | 100 % | window; Vorschau False; Scroll 0 |
| [settings-720p-ui100-view-help.png](settings-720p-ui100-view-help.png) | 1280×720 | 100 % | window; Vorschau False; Scroll 0 |
| [settings-720p-ui125.png](settings-720p-ui125.png) | 1280×720 | 125 % | window; Vorschau False; Scroll 0 |
| [settings-720p-ui125-bottom.png](settings-720p-ui125-bottom.png) | 1280×720 | 125 % | window; Vorschau False; Scroll 135 |
| [settings-720p-ui125-view-help.png](settings-720p-ui125-view-help.png) | 1280×720 | 125 % | window; Vorschau False; Scroll 135 |
| [scale-options-720p-ui125.png](scale-options-720p-ui125.png) | 1280×720 | 125 % | window; Vorschau False; Scroll 0 |
| [mode-options-720p-ui125.png](mode-options-720p-ui125.png) | 1280×720 | 125 % | window; Vorschau False; Scroll 0 |
| [size-hover-720p-ui125.png](size-hover-720p-ui125.png) | 1280×720 | 125 % | window; Vorschau False; Scroll 0 |
| [preview-borderless-ui125.png](preview-borderless-ui125.png) | 2560×1440 | 125 % | borderless; Vorschau True; Scroll 0 |
| [fullscreen-size-help-ui125.png](fullscreen-size-help-ui125.png) | 2560×1440 | 125 % | borderless; Vorschau False; Scroll 0 |
| [preview-window-720p-ui125.png](preview-window-720p-ui125.png) | 1280×720 | 125 % | window; Vorschau True; Scroll 0 |
| [storage-error-720p-ui125.png](storage-error-720p-ui125.png) | 1280×720 | 125 % | window; Vorschau False; Scroll 0 |
| [puzzle-options-720p-ui125.png](puzzle-options-720p-ui125.png) | 1280×720 | 125 % | window; Vorschau False; Scroll 175 |

Berichte: [Windows](n02-report.json), [Neustart/Rätsel/Close](restart-report.json), [Manifest](manifest.json), [Exportbindung](export.json), [3705 Komponentenchecks](core.log).

Hauptprobe: [OS-Eingaben](os.jsonl), [Enginezustände](engine.jsonl), [Beobachter](observer-main.gd), [Treiber](n02_gui.py), [Ergänzung](supplement.py). Neustart: [OS](restart-os.jsonl), [Engine](restart-engine.jsonl), [Beobachter](observer.gd), [Treiber](restart_gui.py). Gemeinsame [Win32-Eingabe](win.py), [Launcher](launch.py).
