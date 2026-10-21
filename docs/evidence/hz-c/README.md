# HZ-C · Gebundene Originalbelege

Die [Entwicklungsbindung](comparison/binding.json) archiviert unveränderte
Windows-Originalausschnitte mit korrigierten 14/15, Status- und Menüfällen sowie
neun Chromium-Originale aus einem isolierten statischen Komponentenexport.
Der direkte SHA-256-Vergleich bindet sämtliche verwendeten UI-Dateien und das
Vergleichsskript an die Lieferung. Keine Bildskalierung oder Nachzeichnung.

Die Quellen waren beim Entwicklungslauf auf `f0338f983facf529bd0c54a70dfb0b522bcf03bf`
mit den explizit hashgebundenen anschließenden Korrekturen an geschlossenen
Controlrändern, Kopf-/Textbuttonbudgets und engem Katalogseitenabstand verändert.
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

Der [erste CI-Katalogbefund](failure-f0338f9.json) bleibt mit unverändertem
[Bericht, Prozesslog und Originalframe](failure-f0338f9.zip) erhalten.
Dieser Zwischenstand scheiterte am langen Kategorienamen bei UI125 und ist
kein erfolgreicher HZ-C-T01-Nachweis. Die endgültigen Produktbelege sind separat.

## Sauberer Runtime-Nachweis und dauerhafte Originalarchive

Runtime-Head: `5075e1bf883e18e24b9802118047a110ea2bf7f0`; Basis `02b7fcd53b4eef8c94f873314848806eefc265cc`; tatsächlicher CI-Checkout `46b56de206e2cd63e38eeb41814da1c79a915ab8`.
[CI 39578546117, Attempt 1](https://github.com/venomenon328/picross/actions/runs/39578546117), Product-Job `119151110652`.
[Maschinenlesbare Zusammenfassung](runtime-evidence.json): 7719 native Prüfungen in elf Katalogmodi, keine Fehler; PCK 316 Prüfungen und 316 im getrennten Prozessneustart, keine Fehler.
Vor Verwendung wurden 1053 native CI-Dateien validiert. Chromium bestand alle 33 Szenarien der fünf Gruppen; 73 Originaldateien wurden erneut vollständig validiert.

| Originalarchiv | Bytes | SHA-256 |
| --- | ---: | --- |
| [windows-pck-5075e1b.zip](windows-pck-5075e1b.zip) · [Inventar](windows-pck-5075e1b-inventory.json) | 39238660 | `9a6ba01daf1eab31832034b13f3d4f0f9fc522f490fbfdb06ebac1300d58a15d` |
| [windows-pck-restart-5075e1b.zip](windows-pck-restart-5075e1b.zip) · [Inventar](windows-pck-restart-5075e1b-inventory.json) | 38061931 | `7751f020cbe63f591a2acbb5281004674d77e142105a8475b90e25d33137eea8` |
| [windows-controls-5075e1b.zip](windows-controls-5075e1b.zip) · [Inventar](windows-controls-5075e1b-inventory.json) | 17420813 | `6ea3df7016276bcad5fee5e3ae107520cfbcb94a464853605bc9c8652f973863` |
| [chromium-controls-5075e1b.zip](chromium-controls-5075e1b.zip) · [Inventar](chromium-controls-5075e1b-inventory.json) | 24350684 | `7555f53533fe2475969b22485e98face70b650d9110d48dcf09685d4b7b2ac93` |

Die Windows-PCK-Archive erhalten den tatsächlichen isolierten EXE-Fensterstart, vollständige PCK-Originalansichten beider Prozesse, synthetische Eingänge, unveränderte Prozesslogs und die vollständige Windows-Bindung einschließlich EXE-/PCK-/Enginehashes. Es wurde ausschließlich das eigene Spielerfenster per PrintWindow aufgenommen.
Das Controlsarchiv enthält sämtliche aktuellen HZ-A/B/C-Originalausschnitte und die elf nativen Berichte. Die 21 HZ-C-Originale zeigen Statuswechsel, alle drei Menüs und den korrigierten Größenvergleich bei UI100/125. Weitere unveränderte Kontextbilder bleiben lokal hashgebunden; die vollständigen CI-Pflichtbilder sind im Product-Originalartefakt gebunden.
Das Chromium-Archiv enthält die 15 unveränderten HZ-C-Interaktionsoriginale sowie sämtliche Berichte, Manifeste und Logs der fünf Gruppen. Der vollständige heruntergeladene Actions-Originalzip wurde mit allen 73 Dateien validiert; Artifact-ID, Digest und vollständiges Dateiinventar bleiben gebunden. Weitere Szenariobilder bleiben im vollständigen Originalartefakt und lokal erhalten. Die gezielte Repository-Auswahl ergänzt den oben archivierten direkten 14/15-Vergleich. Keine Bildskalierung oder Nachzeichnung.
Der folgende reine Dokumentations-/Archivstand ändert keine Laufzeit-, Test- oder Prüfwerkzeugdatei. Die alten Berichte werden ausdrücklich nicht auf dessen neue Commitidentität umetikettiert. Seine eigene Pflicht-CI und der getrennte abschließende Selbstreview werden im PR gebunden. Die tatsächlichen Windows-Voraussetzungen bleiben bytegleich und werden nach WORKFLOW §8 wiederverwendet; HZ-C-R01 und HZ-C-M01 bleiben offen.
