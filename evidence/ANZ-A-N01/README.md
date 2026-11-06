# ANZ-A-N01 · Originale für unabhängiges R02

Produkt-Head: `995d85de41194528467d492d81102625695d4ee4`. Basis: `0997be00b6969adde9d9c09ec83d6c0c1f2302f8`.

Quelle: [Issue #527 / ANZ-A-N01](https://github.com/venomenon328/picross/issues/527#anz-a-n01). Eigentümer hat diesen Abschnitt als Korrektur des ursprünglichen Reviewverweises im Nacharbeitsauftrag benannt. R01 bleibt historisch; dieses Material ist keine unabhängige R02-Abnahme.

Empfänger: unabhängiger R02-Reviewer von PR #528. Geplantes Ende 13.11.2026, keine automatische Ref-TTL. Kein Merge-PR; Produktbranch bleibt frei von diesen Originalen. Nach R02 im beauftragten Rückbau entfernen; bei weiter offenem Gate Bedarf vor Ablauf prüfen.

## Tatsächlich geprüft

Exportierter Windows-Spieler, synthetischer Katalog, unveränderte Produktquellen per `export.json` bytegebunden. Windows 11 / 10.0.26200, NVIDIA RTX 3070, zwei 2560×1440-Desktops bei 96 DPI. Keine physische 4K-/16:10-/abweichende-DPI-Probe. Keine Chromiumprobe.

33 positive Assertions in `n01-report.json`: vier Client/UI-Kombinationen mit echten Dropdown-/Scrollrad-/Mauseingaben; kompakte ausgerichtete 44/55-px-Controls; alle Abschnitte über vertikales Scrollen erreichbar; Vorschauannahme/-abbruch und echter Timeout; Vollbild-Desktopwert mit erhaltenem Fensterpreset; echter Schreibfehler durch Verzeichnis auf dem isolierten `.tmp`-Pfad samt sichtbarer Rücknahme; Hilfe-/UI-Rundweg und Katalog- sowie Arbeitsursprung.

Die Informations-Komponentenprobe liefert 189 erfolgreiche Checks. Sie stabilisiert das Buch synchron und ist kein eigener Bewegungsnachweis. Ausgewählte aktuelle Package-CI wird im PR separat verlinkt.

Die einmaligen Treiber wurden während der Diagnose korrigiert: native Popupauswahl per Maus statt ungeeigneter Home/Enter-Sequenz; einzelne Fokus-/Startklicks wurden wiederholt. Die ungekürzten Engine-/OS-Spuren zeigen auch diese Versuche. Endbericht und Bilder binden die tatsächlich erfolgreichen Zustände. Der niedrige DisplayServer-Größenwert kann nach Vollbildrückkehr um zwei Pixel abweichen; `Window.size`/Backend melden den WM_SIZE-Client. Keine neue DPI-/Mehrmonitorabnahme aus diesem UI-Lauf.

## Sichtung und Zuordnung

Alle folgenden PNGs wurden vom Implementierer in Originaldateien gesichtet. Keine Skalierung, Montage oder Bildbearbeitung für die Zustellung. Der Reviewer muss sie selbst öffnen. Der zusätzliche Vollbild-Vorschaurahmen bleibt als Original zum ersten Windowsbericht erhalten; `preview-720p-ui125` belegt gezielt die enge Rückkehrvorschau.

| Original | Client | UI | Modus / Szene |
| --- | --- | --- | --- |
| [settings-1080p-ui100.png](settings-1080p-ui100.png) | 1920×1080 | 100 % | window; Vorschau False; Scroll 0 |
| [settings-1080p-ui125.png](settings-1080p-ui125.png) | 1920×1080 | 125 % | window; Vorschau False; Scroll 0 |
| [settings-720p-ui100.png](settings-720p-ui100.png) | 1280×720 | 100 % | window; Vorschau False; Scroll 0 |
| [settings-720p-ui125.png](settings-720p-ui125.png) | 1280×720 | 125 % | window; Vorschau False; Scroll 0 |
| [settings-720p-ui125-bottom.png](settings-720p-ui125-bottom.png) | 1280×720 | 125 % | window; Vorschau False; Scroll 425 |
| [mode-options-720p-ui125.png](mode-options-720p-ui125.png) | 1280×720 | 125 % | window; Vorschau False; Scroll 0 |
| [preview-ui125.png](preview-ui125.png) | 2560×1440 | 125 % | borderless; Vorschau True; Scroll 0 |
| [fullscreen-desktop-ui125.png](fullscreen-desktop-ui125.png) | 2560×1440 | 125 % | borderless; Vorschau False; Scroll 0 |
| [storage-error-720p-ui125.png](storage-error-720p-ui125.png) | 1280×720 | 125 % | window; Vorschau False; Scroll 0 |
| [preview-720p-ui125.png](preview-720p-ui125.png) | 1280×720 | 125 % | window; Vorschau True; Scroll 0 |
| [puzzle-options-720p-ui125.png](puzzle-options-720p-ui125.png) | 1280×720 | 125 % | window; Vorschau False; Scroll 0 |

Bytezahlen und SHA-256: [Manifest](manifest.json). Originale: [Windowsbericht](n01-report.json), [OS-Eingaben](os.jsonl), [Enginezustände](engine.jsonl), [Informationsbericht](information.json), [Informationslog](information.log). Prüfer: [Beobachter](observer.gd), [Win32](win.py), [Hauptprobe](n01_gui.py), [Ergänzung](supplement.py).
