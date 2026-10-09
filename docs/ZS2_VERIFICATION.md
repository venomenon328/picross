# ZS-2 · reguläre Integration und Prüfzuordnung

Stand: 09.10.2026 · ZS2-V1 / ZS2-E2 / N01–N03 · #53 · Arbeitsbranch `feat/53-zs2-regular-ui`, Ziel `main`.
Historische native Auswahlreferenz: `985cf08e0cd7dda4186c3dd42b5eccbba1b80e3f`
(integrierte ZS-1-Studie aus PR #55). Aktuelle integrierte main-Basis:
`24564dfed3bb9844d151f4c4ec055d051232d16f` (VS1/GF1); Mergecommit
`c13a699` führt beide Capture-/Export-/Uploadwege zusammen. Der Eigentümer hat die nach dessen Merge
vorgesehene ZS1-M01-Prüfung erfolgreich abgeschlossen und die Kombination bestätigt;
[#52](https://github.com/venomenon328/picross/issues/52) ist abgeschlossen. Nicht
mitgeteilte Windows-/DPI-Metadaten werden dieser Bestätigung nicht hinzugedichtet.

## Implementierung und Grenzen

Die reguläre `main.tscn` erzeugt `ui/chalkboard_board.gd`: ausgewählte Original-TTF,
Faktor 1,35, gemeinsame Zeilen-/Spaltenslots 26/18 × UI und explizite Plex-Zeichen
für `…`/`–`. Titel und übrige UI bleiben erhalten. `ui/drawing_board.gd` verwaltet
nur flüchtige Vorschau-/Effektdaten; `ui/pencil_marks.gd` zeichnet die ausgewählten
stabilen Stiftflächen und zwei X-Züge. Die Studie verwendet denselben Zeichner,
behält ihre Font-/Stilvergleiche und startet weiterhin vor dem Laden der Hauptszene
mit eigenem Speicherroot. Die reguläre Szene lädt keine Studienressourcen.

Die Spielmodelle, neun Registrierungen, Lösungen/Proofs/Paletten, Appidentität,
Save-Schema 1 und `user://p1/saves/` sind unverändert. Der atomare Commit samt
History, H1, Miniatur, Save und Abschluss geschieht vor dem Effektstart. Nur
Zellzeichnung wird pro Effektframe erneuert. Entartete, nicht triangulierbare
Subpixelanschnitte am bewegten Strichrand werden vor Übergabe an Godots Canvas
verworfen; die reguläre Form und ihre statischen Vergleichspixel bleiben erhalten.
Der Clipabstand berücksichtigt zusätzlich einen Pixel Antialiasing-Saum, damit
keine schwache X-Tinte außerhalb des Viewports verbleibt. Gegenüber der Studie
dürfen dadurch ausschließlich Pixel bis 5 px vom Viewportrand abweichen
(einschließlich diagonaler AA-Endkappen und Rundung);
Hinweise bleiben pixelgleich; im Rasterinneren ist ausschließlich ein
8-Bit-Rundungsschritt je Kanal aus neu abgeschnittenen AA-Linien zulässig.
Wirksame neue Vorschau entfernt abgelöste Effekte dauerhaft; Abbruch lässt sie
nicht zurückkehren. Der eine
Sitzungsschalter „Zellanimationen“ startet an und schreibt keine Einstellungsdatei.
Keine neue Rand-UI, Hintergrundproduktion, Spielregel oder Veröffentlichung.

## Akzeptanzzuordnung

| Issue-ID | Nachweise am Lieferstand |
| --- | --- |
| ZS2-A01 | `zs2_tests.gd`: reguläre Board-Erzeugung und 26/18 für alle neun Blätter bei UI 100/125 %. `zs2_capture.gd`/`zs2_delivery.py`: 16 Dreiervergleiche (bisher regulär, ausgewählte Studie, jetzt regulär), identische eigene Zellen, Geometrie und Eingaben; Hinweise pixelgleich, Rastervergleich mit der oben begrenzten AA-Clipkorrektur. |
| ZS2-A02 | Native Ziffernprobe 0–9/11/17/40/100, drei Zustände, beide Achsen, C1; Schrift-/Glyphenmetriken und Plex-Marker. Reguläre P1-/GP-48-Tests und native Drag-/Drop-/Tooltip-/Markerprüfungen bleiben aktiv. Semantische Lesepositionen statt Pixelwerte gespeichert. |
| ZS2-A03 | Gemeinsame Gestenprobe aus `zs1_tests.gd` auf echter regulärer Hauptszene; G1-Neuwahl, Schutz, Umwandlung, Neutralisierung, Rückzug, Escape/Fokus. Native Echtzeitfolge bestätigt statische Vorschau einschließlich Wartezeit. |
| ZS2-A04 | Reale Eingabeereignisse und gerichtete Startfolge aller wirksamen Setz-/Umwandlungszellen; kontrollierte Ablaufgrenzen 79/80 und 139/140 ms. Sieben native Strichzeitbilder, unabhängige räumliche Pixelpunkte und zwei Negativkontrollen (gleichförmiges Fade, umgekehrte X-Reihenfolge). Zusätzlich native kontrollierte und Echtzeit-X-Folgen bei 12/24/36 px mit 1:1-Wiedergabe und vollständigem Spielkontext; Negativkontrollen bei jeder Größe. |
| ZS2-A05 | Folgestrich vor Ablauf, Übernahme auf animierten Zellen, Zurückziehen/Abbruch ohne Wiederkehr, G1-Neuwahl; vier schnelle 100-Zellen-Farbstriche auf F-07. |
| ZS2-A06 | Undo/Redo, Fokus, Zoom/Resize/Pan, Reset/Restore, Blatt-/Album-/Informationswechsel und sofort gespeicherter letzter Lösungsstrich. Bestehender Gesamtproduktharness prüft Flushfehler, Backup/Recovery und Zwei-Prozess-Restore. |
| ZS2-A07 | Tatsächlicher Checkbox-Signalweg; Aus beendet Effekte, An spielt nichts nach; Zellen/History/View/Savebytes gleich. Aus über alle neun Blätter/Reset erhalten; frische Hauptszene beginnt an. |
| ZS2-A08 | Native Zelltrennung/Fünferlinien, alle Rand-/Eckanschnitte für bestätigte und Preview-X, G1-Pixel, Miniatur und viele X. Alte Vollflächen-Pixelproben gezielt auf Stiftinnenfläche/56-%-Zielvorschau umgestellt; Cliporacle vergleicht gerenderte Tinte mit ausgeblendeter Zellschicht. |
| ZS2-A09 | Native Matrix 1280×720/1600×900/1920×1080/2560×1440, UI 100/125 %, 12/24/36/72-px-Zellen und Gesamtansicht; F-01/02/03/07. Bestehende ZV-50-Matrix prüft weiterhin die vollständige 20×20-Arbeitsfläche bis 150 %. RP-6 erfasst alle neun Blätter. |
| ZS2-A10 | Gesamtharness inklusive 500 Aktionen, Zwei-Prozess-, G1/H1/GP-48/ZV-50/RP-6/Recovery und separater Studienregression. Echtzeit-/Lastmessung F-03 und F-07: Eingabe inklusive Save, Zellzeichenzeit und Frameabstände getrennt; Effektframes dürfen keine H1-Analyse anstoßen. |
| ZS2-A11 | Reguläres Windows-ZIP, getrennte `zs2-review`-/`zs2-strokes`-ZIPs, `zs2-report.json`. Export-Smoke prüft eingebettete Chalkboard-Bytes und Ausschluss von Studie/Bakso. Fontquelle und vorhandene Nutzungshinweise liegen im Spielerpaket. Vollrenderupload bleibt manuelles Opt-in. |

Die historische Vier-/Fünf-Slot-Repro in den P1-Tests berechnet ihren künstlichen
Hinweisbereich aus der tatsächlichen Schriftmetrik; Anzahl der Slots/Token und
vollständige monotone Leseroute bleiben hart geprüft. Historische GP-48-Bilder
behalten ihren alten Referenzcommit; die neue Typografie wird im Vergleich
ausdrücklich ausgewiesen. Der zusätzliche ZS-2-Vergleich bindet genau die
integrierte ausgewählte ZS-1-Fassung. Vollständig identische und ausschließlich
durch den begrenzten AA-Cliprand samt Rasterrundung abweichende Fälle werden im
Bericht getrennt gezählt.
Die H1-An/Aus-Bildprüfung bindet Token-/Tooltipbereiche und Marker an die
tatsächliche gewählte Schrift, Plex-Sonderzeichen und ihre Baseline-/Slotmetriken;
der unabhängige Pixelvergleich sowie Raster-/Miniaturgleichheit bleiben bestehen.
Die Pixelgrenze für subpixelweichen Hinweisdrag berücksichtigt die Fläche der
1,35-fachen Schriftgröße (550 statt 300 geänderte Pixel); Nachbarlinien bleiben
pixelgenau gleich. X-Testpositionen schneiden jetzt tatsächlich einen der
gekrümmten Züge an; die sichtbare Tinte und ihre Clipgrenze prüft der Bildvergleich.

## Nacharbeit ZS2-N01–N03

[ZS2-E2](https://github.com/venomenon328/picross/pull/56#issuecomment-6061611805)
bestätigt das zusammenhängende Paket. N01 entfernt bei gestarteten X die volle
Unterzeichnung; Zug eins und danach Zug zwei schreiben sichtbar. Dragvorschau
bleibt vollständig bei 56 %, wartende Ziele bleiben abgeschwächt. Endgeometrie,
Farben und Clipgrenzen bleiben unverändert.

N02 ordnet ausschließlich die transiente Darstellung nach dem tatsächlichen
Gestenstart und finalen G1-/Rückzugsabschnitt. Modelländerungen bleiben atomar.
Nur m effektive Setz-/Umwandlungszellen zählen: Δ = min(8 ms, 120 ms/(m−1)) bei
m > 1, sonst null; 140 ms je Zelle, höchstens 260 ms gesamt. Entfernen beginnt
ungestaffelt und dauert 80 ms. Vorschau/Commit ersetzt ältere aktive und wartende
Effekte dauerhaft; keine verzögerten Modell-, History- oder Save-Callbacks.

N03 behandelt Gegentasten-Down in der globalen Eingaberoute, auch außerhalb des
Boards. Vorschau/Zähler und Effekte enden ohne Commit. Bis zum Loslassen beider
Tasten werden zugehörige Ereignisse verbraucht; erst ein frisches Down startet
wieder. Escape/Fokusverlust, Re-Down, Bewegung und verschiedene Up-Reihenfolgen
sind geprüft. Falsches Up ohne Gegentasten-Down bleibt G1-konform; MMB/Hand bleiben
Navigation. N04 ist ausdrücklich zurückgestellt.

`zs2_rework_cases.gd` prüft über echte Viewport-Events mit `button_mask`:

- Längen 1/4/16/17/100, beide Achsen und Richtungen, Füllung/X, Schutzlücken,
  Umwandlung, G1-Neuwahl und finalen Rückzug; numerisch unabhängiges Timingoracle.
- Sofortige Zellen/Miniatur/Savebytes und atomare History, 139/140-ms-Endgrenze,
  höchstens 260 ms; gleichzeitige 80-ms-Entfernung. Keine spätere Zustandsänderung.
- Wirklich wartende Effekte bei Undo/Redo, Escape/Fokus, Pan/Zoom/Resize,
  Blatt-/Album-/Informationswechsel, Reset/Restore und Ausschalten; nach weiterlaufender
  Uhr kein Wiederanlauf. Miniaturnavigation beendet ebenfalls die Effekte.
- Beide Gegentastenrichtungen innerhalb/außerhalb des Boards, beide Up-Folgen,
  Re-Down bei noch gehaltener Taste, Escape/Fokus-Rückkehr mit und ohne gehaltene
  Taste, alte bestätigte Aktionen unverändert und anschließend frische Eingabe.

ZS1/VS1 erben denselben Zeichner. VS1 hat genau einen geerbten Animationsschalter
mit einer Verbindung. Neue VS-Berichte nennen den tatsächlichen Quellcommit und
Hashes aller beteiligten Zeichnerdateien; die historische Auswahlreferenz bleibt
getrennt. VS-D01 ist entschieden und GF-M01/#59 historisch bestanden; beides wird
nicht erneut als Voraussetzung geöffnet. #61 bleibt nach #53 separat.

## Reproduktion und Artefaktbindung

```powershell
python tools/p1_product.py --cache-dir "$env:TEMP/picross-rp6-cache" --output-dir artifacts/zs2-product
```

Gepinnte Godot-4.7.2-Standard-Toolchain und isolierte Pillow-12.3.0-Umgebung nach
Projektprofil; Linux verwendet Xvfb/Mesa. Alle Tests laufen in temporären Kopien
und Profilen. Es werden keine tatsächlichen Benutzer-Saves gelesen oder verändert.
Pflichtjobs: `docs`, `product`, `preflight`, `puzzle-production`, `rp4-windows`,
`rp5-repair`. Finale Head-/Basis-/Test-Merge-/Run-/Downloadbindungen und lokaler
Windows-Exportstart stehen im Draft-PR. Frühere Runs gelten nur für ihre Heads.

- `picross-p1-player-<Head>` enthält das reguläre Windows-Spielpaket, Anleitung,
  Quellen-/Nutzungshinweise und Produktbericht.
- `zs2-review-<Head>` enthält 48 native PNGs, die reguläre Ziffernprobe, drei
  Captureberichte, HTML-Index und `zs2-report.json` mit Export-/Bildhashes.
- `zs2-strokes-<Head>` enthält die kontrollierte räumliche Strichfolge und die
  getrennte Echtzeitfolge mit Zeitangaben, 12/24/36-px-X-Folgen, 1:1-Wiedergabe,
  Vollbildkontext, Negativkontrollen und demselben Bericht.
- `zs1-*` bleiben eigene Studienartefakte; sie ersetzen keine reguläre ZS-2-Prüfung.

Kontrollierte Zeitbilder prüfen die unveränderte Produktionszeichenfunktion,
belegen aber keine Aufnahmefrequenz. Windows/OpenGL- und Linux/Mesa-Zeiten sind
konkrete technische Stichproben; keine allgemeine FPS-/DPI- oder Mausabnahme.

## Getrennte Abnahme

[ZS2-M01 / R1-A01](ZS2_OWNER_TRIAL.md) am regulären Windows-Artefakt und das unabhängige
technische/visuelle Review des aktuellen Heads sind **offen vor Merge**. Die Eigentümerprobe umfasst die
bisherige Änderungsrückmeldung zu X-Aufbau, Staffelung und Gegentasten-Abbruch.
Eine ausdrückliche Mergefreigabe liegt mit diesem Umsetzungsauftrag nicht vor. Der
getrennte Selbstreview wird im Draft-PR protokolliert und ersetzt keines dieser
Gates. Der Auftrag endet mit geprüftem Commit/Push und Draft-PR. Kein Merge oder
Release; #54 und historische #25/#28 werden nicht integriert. Die längere Nutzung
und Phasenentscheidung #24 folgen erst nach ZS-2.
