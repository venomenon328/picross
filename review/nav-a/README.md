# NAV-A · temporäre Revieworiginale

Diese Dateien gelten ausschließlich dem Produkt-Head `7e2e8c3e305a79a002fe89910b192ec9d8b86a33` von [Draft-PR #554](https://github.com/venomenon328/picross/pull/554), Basis `bd264554093bd4748b2fdd3d29d8f2e8db2d2c18`, gemäß [#549 einschließlich X und gemeinsamer Kopfhöhe](https://github.com/venomenon328/picross/issues/549).

Empfänger sind der unabhängige technische/visuelle Reviewer **NAV-A-R01** und der Eigentümer für **NAV-A-M01**. Beide Vor-Merge-Gates sind offen. Die Implementierersicht ersetzt keine Abnahme. Dieser separate Ref `review/549-nav-a` wird nicht in main oder den Produktbranch gemergt.

[manifest.json](manifest.json) bindet jede unveränderte Datei mit Bytezahl, SHA-256 und Szenario an den Produkt-Head. Der konkrete Belegcommit steht in den unveränderlichen Links im PR. Frist: **15.11.2026**. Bis zur benötigten Prüfung erhalten; bei Gateabschluss oder Frist den Bedarf prüfen und den Ref im beauftragten Rückbau entfernen. Bei noch offenen Gates vor Fristablauf Zustellung erneuern. Zuständig ist der anschließende Reviewer/Eigentümer im Paketabschluss. Lokale Arbeitskopien dieses Implementierungslaufs werden nach verifiziertem Download entfernt.

## Native Windows-Probe

Windows 11 build 26200, NVIDIA RTX 3070, Bildschirm 2560×1440 bei 96 DPI / OS-Skala 1; offizieller SHA-256-verifizierter Godot 4.7.2 (`ed1daf0bf`). 389 Assertions sind bestanden; [observations.json](native-windows/observations.json) enthält 401 Zeilen einschließlich der 11 Aufnahmen und der tatsächlichen Symbolbutton-Inventur.

Es lief die reguläre `res://main.tscn` mit unverändertem `book/main.gd` im echten nativen Root-Window mit normalem Timing und echtem Input-Routing. Die Eingaben gingen durch Godots native Window-Viewport-Ereignisse; es wurden keine OS-Desktop-Eingaben automatisiert. Der Katalog mit 54 Testblättern und alle Profile sind synthetisch und isoliert. Die Produktkatalogdaten sind kein Prüfkorpus. [runtime-binding.json](native-windows/runtime-binding.json) verifiziert 290 Produkt-/Testskriptdateien bzw. Ressourcen gegen den sauberen Produktstand; Importsidecars behalten alle Quelloptionen und ergänzen nur Engine-Defaults.

Die Messflächen betrugen tatsächlich 1920×1080, 2560×1431 und 1280×720, UI100/125. Beim angeforderten 2560×1440-Fenster begrenzte Windows die Clienthöhe auf 1431 Pixel; PNG und Beobachtung führen dieses echte Maß. Die Komponentenprüfung und die separate Buchdiagnose verwenden zusätzlich die exakte 2560×1440-Messfläche. Dafür war der Display-Presetwächter pausiert, wie in der vorhandenen Layoutdiagnose. Die angezeigte gespeicherte Fenstergrößenauswahl kann deshalb 1920×1080 nennen, obwohl die gemessene Fläche 1280×720 ist. Dies ist kein Nachweis anderer OS-DPI-Stufen oder persönlicher Maus-/Monitorbedienung; **M01 bleibt erforderlich**. Die echten Windows-Anzeigeoptionen und beide lokalen Fragezeichen waren aktiv und Teil der Inventur.

Die Aufnahmen zeigen X-Hover und Fokus, Zahnrad-Hover, aktive Hilfemarkierung/Kapitel, aktive Einstellungsmarkierung/Fokus, Fortsetzen voll/halb, gefilterte erste/letzte/einzige Seite, engen UI125-Speicherfehler/Retry sowie beide Informationsseiten ohne zusätzliche Navigationshöhenzeile. Die Eingabeprüfung umfasst Katalog→Hilfe→Einstellungen→Katalog mit beiden Scrollständen, Rätsel→Hilfe→Einstellungen→Rätsel mit Arbeitszustand, aktiven No-op und blockiertes X/Hilfe bei fehlgeschlagenem Save samt erfolgreichem Retry.

| Unverändertes PNG | Viewport / UI | Bytes |
| --- | --- | --- |
| [01-catalog-first-1920-ui100.png](native-windows/01-catalog-first-1920-ui100.png) | [1920, 1080] / 1.0 | 1780983 |
| [02-work-gear-tooltip-1920-ui100.png](native-windows/02-work-gear-tooltip-1920-ui100.png) | [1920, 1080] / 1.0 | 1834128 |
| [03-help-active-1920-ui100.png](native-windows/03-help-active-1920-ui100.png) | [1920, 1080] / 1.0 | 2076238 |
| [04-settings-focus-1920-ui100.png](native-windows/04-settings-focus-1920-ui100.png) | [1920, 1080] / 1.0 | 1861381 |
| [05-catalog-recent-1920-ui100.png](native-windows/05-catalog-recent-1920-ui100.png) | [1920, 1080] / 1.0 | 1790234 |
| [06-catalog-half-recent-2560-ui100.png](native-windows/06-catalog-half-recent-2560-ui100.png) | [2560, 1431] / 1.0 | 2609956 |
| [07-catalog-last-2560-ui100.png](native-windows/07-catalog-last-2560-ui100.png) | [2560, 1431] / 1.0 | 2718979 |
| [08-catalog-error-full-recent-1280-ui125.png](native-windows/08-catalog-error-full-recent-1280-ui125.png) | [1280, 720] / 1.25 | 1011328 |
| [09-settings-1280-ui125.png](native-windows/09-settings-1280-ui125.png) | [1280, 720] / 1.25 | 998998 |
| [10-help-1280-ui125.png](native-windows/10-help-1280-ui125.png) | [1280, 720] / 1.25 | 1065981 |
| [11-catalog-single-1280-ui125.png](native-windows/11-catalog-single-1280-ui125.png) | [1280, 720] / 1.25 | 1087986 |

Die PNGs sind unveränderte Framebufferoriginale. Der textgebundene GitHub-Contents-Connector liefert bei Dateien über etwa 1 MiB gegebenenfalls keine Bildbytes. Zum Review den konkreten Belegcommit aus dem PR mit einem binärfähigen HTTP-/Git-Client abrufen, z. B. `raw.githubusercontent.com/venomenon328/picross/<Belegcommit>/review/nav-a/native-windows/<Dateiname>`, dann Bytes/SHA-256 mit dem Manifest vergleichen und die Originale öffnen. Ein normales Git-Checkout desselben Belegcommits ist ebenfalls geeignet. Keine ZIP-Doppelverpackung oder verkleinerte Ersatzreferenz.

Die einmaligen [Probe und Runner](native-input/) zeigen den tatsächlichen Erzeugungsweg. Die Laufzeitdateien stammen aus dem angegebenen Produkt-Head; der Zusatzprobe wird nur in die isolierte Kopie gelegt. Die gespeicherten Erfolgsbeobachtungen sind Implementierernachweise, keine unabhängige visuelle Freigabe.

## Einmalige Buchdiagnose und Ressourcen

[lifecycle/report.json](lifecycle/report.json), [integration.json](lifecycle/integration/integration.json) und die drei Original-Logs stammen vom sauberen Produkt-Head. `tools/book_lifecycle.py` lief explizit; `native_results.validate_book_lifecycle` prüfte die Originale anschließend unabhängig. Gemessener Wrapperlauf: 85,287 s. Die historische producerinterne Paketkennung `HIL-1-T01` bleibt im generischen Toolreport; Produkt-Head, Sourcehashes und dieses Manifest binden seinen jetzigen NAV-A-Einsatz.

[Offline-Prüfprotokoll](checks/offline-resources.log): Ressourcen-/Manifestprüfung, vier gezielte `test_z2_delivery.py`-Prüfungen und Dokumentenintegrität bestanden. Die ausgewählte finale Package-CI mit Windows-Spieler wird im PR gesondert verlinkt. CI bleibt `evidence.mode=none`; diese Dateien sind eine gezielte einmalige Reviewzustellung.
