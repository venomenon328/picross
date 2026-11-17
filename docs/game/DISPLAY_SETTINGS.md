# ANZ · Feste Fenstergrößen und native Anzeigemodi

## Geltung und Vorrang

Dieser Vertrag besitzt Modus-/Presetwahl, Start/Fallback, Vorschau/Rücknahme und
die eigenständige Anzeigepräferenz im nativen Windows-Spieler. Die Regeln im
aktuellen Git-Stand sind vom technischen Liefer-/Abnahmestand im Issue/PR zu
unterscheiden. P1 besitzt Rasterzoom und Rätselsaves; HZ Schrift/Controls;
BOOK_INTEGRATION die Buchnavigation. Keine freie native Größenänderung oder
Maximierung neben den folgenden Presets.

[WEB_HOSTING](../operations/WEB_HOSTING.md) behält responsive Browserfenster; native Optionen
erscheinen dort nicht. Headless-/synthetische Tests schalten keine echten Monitore
um. Tatsächliche Windows-/Treiberwirkung muss am gebundenen Produktstand geprüft
werden; keine plattformübergreifende Exklusivgarantie.

## ANZ-D01 · Modus und Auflösung

| Einstellungswert | Tatsächliches Verhalten |
| --- | --- |
| **Fenster** | Verschiebbares, dekoriertes Fenster; seine *Clientfläche* hat genau eine wählbare feste Presetgröße. Kein Rahmenziehen zur Größenänderung und kein freies Maximieren. Programmatische Modus-/Preset-/Fallbackwechsel bleiben möglich. |
| **Rahmenloses Fenster** | Godots `WINDOW_MODE_FULLSCREEN`: bildschirmfüllend ohne Dekorationen, Desktopauflösung des aktuellen Monitors. |
| **Exklusives Vollbild** | Godots `WINDOW_MODE_EXCLUSIVE_FULLSCREEN`: ebenfalls aktuelle Desktopauflösung; kein automatischer Wechsel des Monitor-Videomodus. Ist der Modus tatsächlich nicht erreichbar, sicherer Fallback mit verständlicher Anzeige statt falscher Exklusivbehauptung. |

Beide Vollbildvarianten sind **echte Godot-Vollbildmodi**, nicht ein dekorationsloses normales Fenster mit hart gesetzter Desktopgröße. Für diese Modi zeigt die Auflösungszeile die aktuell erkannte Desktop-/Monitorauflösung nur lesbar und deaktiviert die Fenstergrößen-Presetauswahl. Bei Rückkehr zum Fenstermodus wird dessen zuletzt gewählte Presetgröße wiederverwendet. Der aktuelle Modus und dessen Wirksamkeit sind nach Anwendung zu prüfen. Treiberbedingte Schwarzbilder oder längeres Alt-Tab beim exklusiven Modus werden nicht als vermeidbar zugesagt.

Fensterpresets (logische **Clientpixel**, keine geänderten Betriebssystem-Videomodi):

| 16:9 bzw. verbreitetes HD+ | Optionale 16:10-Ergänzung |
| --- | --- |
| 1280 × 720 | 1920 × 1200 |
| 1366 × 768 | 2560 × 1600 |
| 1600 × 900 | |
| 1920 × 1080 | |
| 2560 × 1440 | |
| 3840 × 2160 | |

Alle Presets sind eine unterstützte Auswahl, aber **nur passend verfügbare** werden aktiv angeboten. Das vollständige dekorierte Fenster einschließlich tatsächlicher Rahmen und Titelleiste muss in den nutzbaren Arbeitsbereich des aktuellen Monitors passen. Windows-DPI, tatsächliche Client-/Rahmengeometrie, Taskleiste und Monitorposition berücksichtigen; eine bloße Rechnung mit nominellen Bildschirmmaßen genügt nicht. Nicht passende Optionen deaktivieren oder ausfiltern, mit verständlicher Information. Deshalb ist ein Fenster mit 3840×2160 Clientpixeln auf einem gewöhnlichen 3840×2160-Desktop nicht auswählbar; 4K bleibt im Vollbild bei 4K-Desktopauflösung möglich.

Der Fenstermodus verwendet die Resize-Sperre des nativen Fensterservers; durch OS-Maximieren oder externe Resizeereignisse darf kein frei veränderter Dauerzustand entstehen. Systeminterne Größenänderungen wie DPI-/Monitormigration bleiben Anlass für kontrollierte Neuberechnung, nicht für das Ignorieren der Anzeige. Fensterpositionen so anpassen, dass sie vollständig sichtbar bleiben.

## ANZ-D02 · Start und dynamischer Fallback

- **Ohne gespeicherte Display-Präferenz:** Fenstermodus mit 1920×1080, sofern vollständig passend; sonst größter vollständig passender Preset bis höchstens 1920×1080. Ist kein 1280×720-Fenster samt Dekorationen möglich, aber der Desktop selbst mindestens 1280×720 groß, **rahmenloses Vollbild** als sicherer Fallback.
- **Mit bestätigter Präferenz:** gespeicherten Modus und zuletzt gewählten Fensterpreset validieren und anwenden, soweit tatsächlich möglich. Bei defekter Datei sichere Defaults; bei veränderten Monitoren/Arbeitsbereichen sicherer sichtbarer Fallback und Hinweis. Bloße temporäre Fallbackanwendung überschreibt die gespeicherte Auswahl nicht.
- **Monitorkontext:** Aktuellen Monitor des Spiel-Fensters zugrunde legen; nach Monitor-, DPI- oder Arbeitsbereichswechsel nicht passende Fensterposition/-größe sicher zurückführen. Kein wählbares Monitorwechselmenü in ANZ-A.
- **Unter tatsächlichen 1280×720 Clientpixeln** bleibt die vorhandene Mindestflächenwarnung. 720p ist ein begrenzter Betrieb/Fallback, kein neues Komfortversprechen für alle Rätselgrößen. 1080p ist weiterhin der primäre Qualitätsmaßstab; 1440p, 4K und 16:10 nutzen die responsive Buch-/Katalog-/Rasterdarstellung bei unveränderten separaten Zoomfaktoren.
- **Keine Änderung der Desktopauflösung** und keine davon unabhängige konfigurierbare Renderauflösung. Die beiden Vollbildmodi erhalten die aktuelle Desktopauflösung, auch wenn der gespeicherte Fensterpreset davon abweicht.

## ANZ-D03 · Einstellungsseite, Vorschau, Persistenz

Auf der **vorhandenen linken Buch-Einstellungsseite** erscheint ein Abschnitt „Anzeige“ mit handgezeichneten, zum bestehenden [HZ-Stil](HAND_DRAWN_UI.md) passenden Controls:

1. **Anzeigemodus**: Fenster / Rahmenloses Fenster / Exklusives Vollbild.
2. **Fenstergröße**: gültige Presets, nur im Fenstermodus wählbar; andernfalls erkennbar deaktiviert und tatsächliche Vollbildauflösung lesbar.

Die Auswahl bleibt über Buchseiten, Hilfe-/Katalog-/Arbeitsrückkehr konsistent. Keine zusätzliche Einstellungsseite oder generelle Schrift-/Buttonneugestaltung. Dialog, Bestätigung und Fehlinformation müssen innerhalb des aktuellen Viewports erreichbar sein.

Genau **Anzeige** und **Rätselansicht** besitzen stabile handgezeichnete Rahmen
mit verbundenen Titellaschen. Der Block steht mittig in der sicheren linken
Papierfläche, höchstens 640 × UI breit; Inhalte bleiben linksbündig.
Bildhaupttitel und Titelvorrang folgen [VIEW_TITLE_ART](VIEW_TITLE_ART.md),
Gruppentitelfont und Schriftrollen [HAND_DRAWN_UI](HAND_DRAWN_UI.md).
Label und HZ-Dropdown stehen in einer gemeinsamen Zeile. Nur Fenstergröße und
Rätselansicht besitzen rechts ein eigenes fokussierbares Fragezeichen.
Anzeigemodus und UI-Skalierung nutzen stattdessen die volle frei werdende Breite
einschließlich Zwischenabstand, ohne Hilfe-/Fokusplatzhalter. Alle Zeilen behalten
dieselben Label-/Dropdownanfänge und die sichere rechte Innenkante.
UI-Skalierung hat genau 100 % und 125 %, sitzungsgebunden.
Die vollständige Ansichtserklärung und die Erklärung der Vollbild-Desktopauflösung
stehen nur in den gestylten Fragezeichen-Tooltips, erreichbar per Hover und Fokus.
Das separate Fragezeichen bleibt auch neben deaktivierter Größenwahl aktiv.
Vertikales Scrollen erhält bei 1080p/720p × UI100/125 sämtliche Optionen.
Kopfgruppe, Rückweg, Besuchsursprung, Übergang, Fokus und Scrollkontext folgen
[BOOK_INTEGRATION](BOOK_INTEGRATION.md).

Beenden-Gruppe und manueller Hinweisreset entfallen vollständig, einschließlich
des anderweitig produktiv ungenutzten `Board.reset_clue_pan()`. Kein Ersatzbefehl
oder automatischer Reset beim Einstellungsbesuch. Individuelles Hinweisziehen,
rasterseitige Slots, Default/Zoom-/Layoutnormalisierung und sichere Lesepositionen
bleiben. Katalog-Ausgang, OS-Schließen und Save-/Flush-/Recovery-/Web-Lifecycle
bleiben erhalten.

Keine zusätzliche Clientflächenzeile oder positive Speicherdauerzeile. Im Vollbild zeigt das deaktivierte Größenfeld die aktuelle
Desktopauflösung; der gemerkte Fensterpreset bleibt unverändert. Countdown,
Rücknahme-, Fehler- und Fallbackhinweise samt expliziter Übernahme bleiben sichtbar.
Ein Wechsel wird sofort **probeweise** wirksam und verlangt innerhalb von **15 Sekunden** eine explizite Bestätigung. In der Vorschau keine verketteten zweiten Moduswechsel. Abbrechen oder Timeout stellt den **letzten bestätigten funktionierenden** Zustand wieder her; auch bei fehlgeschlagener Anwendung muss ein sichtbar benutzbarer Zustand erreichbar bleiben. Ein bloßer Fokuswechsel/Alt-Tab darf nicht automatisch als Annahme gelten. Ein Prozessabbruch vor Bestätigung lässt die alte persistierte Auswahl bestehen. Erst ausdrücklich bestätigte und wirklich angewandte Änderungen werden geschrieben.

Die native Windowsfassung erhält die eigenständige versionierte, streng validierte Präferenzdatei `user://p1/display-preference.json` (Modus sowie zuletzt gewählter Fensterpreset). Sie wird fehlerbewusst/atomar gespeichert; unbekannte Versionen, ungültige Presets, doppelte/überzählige Schlüssel und korrupte Daten dürfen weder einen unsichtbaren Start verursachen noch echte User-Saves beschädigen. Fehler beim Schreiben sind sichtbar, die vorherige gültige Datei wird nicht zerstört oder die Änderung nicht fälschlich als dauerhaft gesichert angezeigt. Sie ist **nicht Teil von Save-Schema 1**, `user://p1/saves/`, Browser-IDBFS oder des bestehenden Katalogpräferenzformats; UI-Skalierung und Zellanimationen werden dadurch nicht zusätzlich dauerhaft gespeichert.

## Interaktionen, explizite Nichtziele und Prüfung

Viewportwechsel erhalten Seiten-, Hinweis-, Zell- und Trefferlayout sowie den
zuletzt bestätigten Rätselstand. Navigation, Fehlermeldungen, Undo/Redo,
Rückkehrkontexte und Abschluss bleiben wirksam. Auflösungswechsel während einer
Buchseitenanimation ist kein eigener ANZ-Sonderfall; allgemeine Resize-
Stabilisierung folgt BOOK_INTEGRATION.

Nicht Bestandteil sind freie Maße, maximiertes Fenster als weitere Option,
andere Betriebssysteme, Monitorauswahl, Browsermanagement/-fullscreen,
exklusive Monitorauflösungswahl, eigene Renderauflösung oder ein allgemeiner
GPU-/DPI-Umbau. Rätselsave- und Animationsverträge erhalten ihre Zuständigkeit.

ANZ-A01–A06, T01/W01/R01/M01 und die N01–N03-Nacharbeiten stehen in
[Issue #527](https://github.com/venomenon328/picross/issues/527). Neue Prüfungen
folgen dem tatsächlichen Paketplan nach [CI_WORKFLOW_V2](../ci/CI_WORKFLOW_V2.md)
und [CI_C_NATIVE_GROUPS](../ci/CI_C_NATIVE_GROUPS.md). Komponentenprüfung, echter
Windows-Moduswechsel und persönliche Komfortprobe sind getrennte Nachweise.

## Implementierungsbindung ANZ-A

`display_policy.gd` filtert die festen Clientpresets anhand nativer Arbeitsbereichs-
und Dekorationsmaße. `display_backend.gd` sperrt Resize, setzt ausschließlich
Godot-Fenstermodi und kontrolliert tatsächliche Client-/Moduswerte. Der Controller
serialisiert Anwendung, 15-s-Vorschau und Rücknahme; Monitoränderungen und
externe Größenänderungen werden periodisch sicher abgeglichen. Die Anzeigecontrols
verwenden die vorhandene HZ-Familie, die Bestätigung liegt innerhalb des Viewports.
Web, Headless und synthetische SubViewports starten keinen physischen Controller.

Die getrennte Präferenz verwendet Format `picross-display-preference-v1` und genau
die drei Stringschlüssel `format`, `mode`, `preset`. Moduswerte sind `window`,
`borderless`, `exclusive`, Presets beispielsweise `1920x1080`. Strikte JSON-Form,
unbekannte Werte/Versionen, doppelte (auch escapte) und zusätzliche Schlüssel
werden vor Anwendung geprüft. Nach Flush und erneuter Validierung der `.tmp`-Datei
rotiert eine gültige Primary in `.bak`; anschließend wird der Kandidat auf den
abwesenden Primarypfad verschoben. So wird Godots destruktives Windows-Overwrite
vermieden. Ein Abbruch in der Veröffentlichungslücke lädt `.bak`; ein Fehler
versucht die Rücknahme, ohne die gültige vorherige Fassung zu vernichten. `.tmp`
ist nie Ladequelle. Dieser eigene transaktionale Weg ändert keine P1-Saves.

## Herkunft und Nachweise

Fachentscheidungen und tatsächliche Review-/Abnahmeergebnisse: [#527](https://github.com/venomenon328/picross/issues/527) und die dort gebundenen Produkt-PRs.
Der [historische Dokumentstand](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/DISPLAY_SETTINGS.md)
erhält frühere Lieferchronologie und ersetzte Regeln. Er ist keine zusätzliche
Normquelle oder dauerhafte Prüfpflicht. Aktuelle Prüfungen folgen dem
[Paketvertrag](../ci/CI_WORKFLOW_V2.md) und dem jeweils betroffenen Modul.
