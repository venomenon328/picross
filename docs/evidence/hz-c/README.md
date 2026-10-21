# HZ-C · Gebundene Originalbelege

Die [Entwicklungsbindung](comparison/binding.json) archiviert unveränderte
Windows-Originalausschnitte mit korrigierten 14/15, Status- und Menüfällen sowie
neun Chromium-Originale aus einem isolierten statischen Komponentenexport.
Der direkte SHA-256-Vergleich bindet sämtliche verwendeten UI-Dateien und das
Vergleichsskript an die Lieferung. Keine Bildskalierung oder Nachzeichnung.

Die Quellen waren beim Entwicklungslauf auf `b00b5116dfef97151dbe84857f79eea568451860`
mit der explizit hashgebundenen anschließenden ganzzahligen Papierbutton-Textursprungs verändert.
Dies ist keine Behauptung eines sauberen Produktlaufs dieses alten Heads.
Der temporäre native Einstieg führt ausschließlich den HZ-C-Pfad aus; sein
Original und der Chromium-Einstieg samt Build-/Aufnahmeskripten sind komprimiert
erhalten. Alle Spielinputs sind synthetisch; es werden keine echten Saves gelesen.

Der Chromium-Vergleich verwendet die tatsächlichen Card-/Choice-/BookButton-
Komponenten und Originalfonts, 1280×720/UI125, 1920×1080/UI100 und
2560×1440/UI125. Die HTML-Canvasgröße folgt dem Client; diese reine statische
Prüffassung besitzt weder Gameplay- noch Save- oder Deploymentfreigabe.
Geschlossene Vergleiche sind unverkleinerte Komponentenrechtecke; offene
Listen sind vollständige Clientoriginale, damit kein Popupende abgeschnitten wird.

| Originalvergleich | Windows | Chromium |
| --- | --- | --- |
| 1280×720/UI125 | [14/15](comparison/hz-c-comparison-1280.png) | [14/15](comparison/chromium-comparison-1280.png) |
| 1920×1080/UI100 | [14/15](comparison/hz-c-comparison-1920.png) | [14/15](comparison/chromium-comparison-1920.png) |
| 2560×1440/UI125 | [14/15](comparison/hz-c-comparison-2560.png) | [14/15](comparison/chromium-comparison-2560.png) |

Weitere unveränderte Status-, Kategorien-, Sortier- und Ansichtsmenüoriginale
liegen im selben Verzeichnis. Die nativen Rollenmetriken stehen im
[Originalbericht](comparison/native-report.json); Browser-/Exportdateihashes
stehen in den separaten Chromium-Bindungen. Die technische Endentscheidung
15/19 und ihre Grenzen erläutert [HZ-C](../../HZ_C_VERIFICATION.md).

Der tatsächliche abschließende CI-/Windows-/PCK-Lauf wird im
[Draft-PR #296](https://github.com/venomenon328/picross/pull/296) mit seinem
eigenen sauberen Head, Basis, Checkout, Run/Attempt und Originalartefakten
gebunden. Diese Entwicklungsoriginale ersetzen ihn nicht. HZ-C-R01 und
HZ-C-M01 bleiben getrennt vor Merge erforderlich.

Die gezielte Gegenprobe stellt ausschließlich die alte wortabhängige vertikale
Papierbuttonzentrierung wieder her. Sie scheitert mit dem erwarteten Exit 4 an
acht der neuen Anfangsglyphenprüfungen. Mutierter temporärer Quelltext,
Originalbericht und Log sind komprimiert erhalten; die Produktdatei bleibt
unverändert. CRLF-Originalserialisierungen sind ebenfalls als `.gz` erhalten;
die danebenstehenden JSON-/Logtexte sind LF-Leseprojektionen.
