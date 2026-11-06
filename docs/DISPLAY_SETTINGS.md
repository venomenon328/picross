# ANZ: Feste Fenstergrößen und native Anzeigemodi

**Status: ANZ-A auf dem Arbeitsbranch implementiert; technische Nachweise und getrennte Abnahmen stehen im Produkt-PR zu [Issue #527](https://github.com/venomenon328/picross/issues/527).** Eigentümerfreigabe der Spezifikation: 06.11.2026. Kein Merge oder Release aus dieser Implementierung ableiten.

## Geltung und Vorrang

Der Vertrag ergänzt [Produktdefinition](PRODUCT_DEFINITION.md), [Gestaltungskonzept](DESIGN_CONCEPT.md), [P1](PROTOTYPE_P1.md) und [Buchintegration](BOOK_INTEGRATION.md). Für den **nativen Windows-Spieler** ersetzt ANZ-A gezielt P1/D-07/D-21 und §5.2 **nur bezüglich freier Fenstergrößenänderung und Startgrößenauswahl**. Die primäre 1080p-Komfortreferenz, 720p-Fallbackgrenze, gültigen Raster- und Hinweis-Fitbudgets, 100-/125-%-UI-Skalierung, 24-px-Arbeitszoom, getrennte View-/Save-Zustände und die responsive 3D-Buchgeometrie bleiben bestehen.

Der Browserentwicklungsweg nach [WEB_HOSTING](WEB_HOSTING.md) behält seine bisherigen responsiven Browserfenster; native Anzeigeoptionen erscheinen dort nicht. Headless-/synthetische Tests verwenden keine echte Monitorumschaltung. Die Fähigkeit der Godot-Version 4.7.2-stable und der konkreten Windowsgrafiktreiber ist beim Implementieren tatsächlich zu prüfen; keine plattformübergreifende Exklusivgarantie.

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

Die [Eigentümer-Nacharbeit ANZ-A-N02](https://github.com/venomenon328/picross/issues/527#anz-a-n02)
ersetzt die N01-Anordnung: genau **Anzeige** und **Rätselansicht** erhalten stabile
handgezeichnete Rahmen mit verbundenen Titellaschen. Der Block steht mittig in der
sicheren linken Papierfläche, höchstens 640 × UI breit; Inhalte bleiben linksbündig.
Der Seitentitel verwendet Fraunces 600, Grundgröße 28, wie die festgelegte
Katalogtitel-Rolle. Label, HZ-Dropdown und fokussierbares Fragezeichen stehen in
einer gemeinsamen Zeile. UI-Skalierung hat genau 100 % und 125 %, sitzungsgebunden.
Die vollständige Ansichtserklärung und die Erklärung der Vollbild-Desktopauflösung
stehen nur in den gestylten Fragezeichen-Tooltips, erreichbar per Hover und Fokus.
Das separate Fragezeichen bleibt auch neben deaktivierter Größenwahl aktiv.
Vertikales Scrollen erhält bei 1080p/720p × UI100/125 sämtliche Optionen.

Beenden-Gruppe und manueller Hinweisreset entfallen vollständig, einschließlich
des anderweitig produktiv ungenutzten `Board.reset_clue_pan()`. Kein Ersatzbefehl
oder automatischer Reset beim Einstellungsbesuch. Individuelles Hinweisziehen,
rasterseitige Slots, Default/Zoom-/Layoutnormalisierung und sichere Lesepositionen
bleiben. Katalog-Ausgang, OS-Schließen und Save-/Flush-/Recovery-/Web-Lifecycle
bleiben erhalten. Die native Probe prüft diese existierenden Exitwege weiter.

N01-A03/A04 gelten weiter: keine zusätzliche Clientflächenzeile oder positive
Speicherdauerzeile. Im Vollbild zeigt das deaktivierte Größenfeld die aktuelle
Desktopauflösung; der gemerkte Fensterpreset bleibt unverändert. Countdown,
Rücknahme-, Fehler- und Fallbackhinweise samt expliziter Übernahme bleiben sichtbar.
Aktuelle N02-Windowsoriginale werden binär erreichbar für unabhängiges N02-R03
vor Merge befristet zugestellt. R01/W01/N01-R02 bleiben an ihre früheren Heads
gebunden; M01 bleibt persönliche Komfortprobe nach Integration vor Release.

Ein Wechsel wird sofort **probeweise** wirksam und verlangt innerhalb von **15 Sekunden** eine explizite Bestätigung. In der Vorschau keine verketteten zweiten Moduswechsel. Abbrechen oder Timeout stellt den **letzten bestätigten funktionierenden** Zustand wieder her; auch bei fehlgeschlagener Anwendung muss ein sichtbar benutzbarer Zustand erreichbar bleiben. Ein bloßer Fokuswechsel/Alt-Tab darf nicht automatisch als Annahme gelten. Ein Prozessabbruch vor Bestätigung lässt die alte persistierte Auswahl bestehen. Erst ausdrücklich bestätigte und wirklich angewandte Änderungen werden geschrieben.

Die native Windowsfassung erhält die eigenständige versionierte, streng validierte Präferenzdatei `user://p1/display-preference.json` (Modus sowie zuletzt gewählter Fensterpreset). Sie wird fehlerbewusst/atomar gespeichert; unbekannte Versionen, ungültige Presets, doppelte/überzählige Schlüssel und korrupte Daten dürfen weder einen unsichtbaren Start verursachen noch echte User-Saves beschädigen. Fehler beim Schreiben sind sichtbar, die vorherige gültige Datei wird nicht zerstört oder die Änderung nicht fälschlich als dauerhaft gesichert angezeigt. Sie ist **nicht Teil von Save-Schema 1**, `user://p1/saves/`, Browser-IDBFS oder des bestehenden Katalogpräferenzformats; UI-Skalierung und Zellanimationen werden dadurch nicht zusätzlich dauerhaft gespeichert.

## Interaktionen, explizite Nichtziele und Prüfung

Viewportwechsel dürfen Seiten-, Hinweis-, Zell- und Trefferlayout nicht verzerren oder den zuletzt bestätigten Rätselstand verändern. Vorhandene sichere Navigation, Speicher-/Recoverymeldung, Undo/Redo, Buchrückweg, Scrollkontexte und Abschlusssicht bleiben erhalten. Auflösungswechsel **während einer laufenden Buchseitenanimation** ist nach Eigentümerpräzisierung ausdrücklich **kein eigener ANZ-Sonderfall**; bestehende generelle Resize-Abbrüche nicht gezielt umbauen und dafür keine neue Prüfmatrix anlegen.

Nicht Bestandteil: frei editierbare Größen, maximiertes Fenster als weitere Option, andere Betriebssysteme, Monitor-Auswahlliste, Browserfenstermanagement oder Browserfullscreen, wählbare exklusive Monitorauflösung, eigenständige interne Renderauflösung, genereller GPU-/DPI-/UI-Skalierungsumbau, neue P1-Saves oder neue Animationsregel.

Das **einzige Paket ANZ-A** enthält die zugehörige Godot-Implementierung, passende gezielte synthetische und echte Windows-Prüfungen sowie eine erst mit implementierter Funktion aktualisierte [Spielanleitung](../game/README.md). Akzeptanz A01–A06, T01, Windows-W01, unabhängiges Review R01 und persönliche spätere Komfortprobe M01 stehen im [Issue #527](https://github.com/venomenon328/picross/issues/527). Für CI gelten [CI_WORKFLOW_V2](CI_WORKFLOW_V2.md) und [CI_CONTRACT](dev-rules/CI_CONTRACT.md): kleiner Kern und Windows-Spieler, Paketmodule `native.catalog` + `native.graphics`, zielgerichtete zusätzliche Einführungsprüfungen, technische Originale ausschließlich zweck-/zeitgebunden, kein automatisch gestartetes Chromium.

Technische Referenz: [Godot DisplayServer 4.6](https://docs.godotengine.org/en/4.6/classes/class_displayserver.html) zur Semantik der seit Godot 4 bestehenden Fenster-/Vollbildmodi. Das ist keine durchgeführte technische oder native 4.7.2-Abnahme.

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

Gezielte günstige Regressionen laufen in `catalog/information` bei Auswahl von
`native.catalog`; die vorhandene Grafikgruppe bleibt unverändert. Einmalige
Windows- und UI-Originale werden getrennt für R01 befristet zugestellt; die
Produktquellen enthalten keine neue Galerie oder Windows-Diagnosefamilie.
