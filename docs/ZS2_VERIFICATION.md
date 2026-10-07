# ZS-2 · reguläre Integration und Prüfzuordnung

Stand: 07.10.2026 · #53 · Arbeitsbranch `feat/53-zs2-regular-ui`, Ziel `main`.
Basis und native Vergleichsreferenz: `985cf08e0cd7dda4186c3dd42b5eccbba1b80e3f`
(integrierte ZS-1-Studie aus PR #55). Der Eigentümer hat die nach dessen Merge
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
Wirksame neue Vorschau entfernt abgelöste Effekte dauerhaft; Abbruch lässt sie
nicht zurückkehren. Der eine
Sitzungsschalter „Zellanimationen“ startet an und schreibt keine Einstellungsdatei.
Keine neue Rand-UI, Hintergrundproduktion, Spielregel oder Veröffentlichung.

## Akzeptanzzuordnung

| Issue-ID | Nachweise am Lieferstand |
| --- | --- |
| ZS2-A01 | `zs2_tests.gd`: reguläre Board-Erzeugung und 26/18 für alle neun Blätter bei UI 100/125 %. `zs2_capture.gd`/`zs2_delivery.py`: 16 Dreiervergleiche (bisher regulär, ausgewählte Studie, jetzt regulär), identische eigene Zellen, Geometrie und Eingaben; ausgewählter Studien- und regulärer Boardausschnitt pixelgleich. |
| ZS2-A02 | Native Ziffernprobe 0–9/11/17/40/100, drei Zustände, beide Achsen, C1; Schrift-/Glyphenmetriken und Plex-Marker. Reguläre P1-/GP-48-Tests und native Drag-/Drop-/Tooltip-/Markerprüfungen bleiben aktiv. Semantische Lesepositionen statt Pixelwerte gespeichert. |
| ZS2-A03 | Gemeinsame Gestenprobe aus `zs1_tests.gd` auf echter regulärer Hauptszene; G1-Neuwahl, Schutz, Umwandlung, Neutralisierung, Rückzug, Escape/Fokus. Native Echtzeitfolge bestätigt statische Vorschau einschließlich Wartezeit. |
| ZS2-A04 | Reale Eingabeereignisse und parallele Startzeit aller wirksamen Zellen; kontrollierte Ablaufgrenzen 79/80 und 139/140 ms. Sieben native Strichzeitbilder, unabhängige räumliche Pixelpunkte und zwei Negativkontrollen (gleichförmiges Fade, umgekehrte X-Reihenfolge). Separate Echtzeitfolge zeigt den laufenden Effekt. |
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
integrierte ausgewählte ZS-1-Fassung und verlangt identische Boardpixel.

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
  getrennte Echtzeitfolge mit Zeitangaben, Negativkontrollen und demselben Bericht.
- `zs1-*` bleiben eigene Studienartefakte; sie ersetzen keine reguläre ZS-2-Prüfung.

Kontrollierte Zeitbilder prüfen die unveränderte Produktionszeichenfunktion,
belegen aber keine Aufnahmefrequenz. Windows/OpenGL- und Linux/Mesa-Zeiten sind
konkrete technische Stichproben; keine allgemeine FPS-/DPI- oder Mausabnahme.

## Getrennte Abnahme

[ZS2-M01](ZS2_OWNER_TRIAL.md) am regulären Windows-Artefakt und das unabhängige
technische/visuelle Review des aktuellen Heads sind **offen vor Merge**. Der
getrennte Selbstreview wird im Draft-PR protokolliert und ersetzt keines dieser
Gates. Der Auftrag endet mit geprüftem Commit/Push und Draft-PR. Kein Merge oder
Release; #54 und historische #25/#28 werden nicht integriert. Die längere Nutzung
und Phasenentscheidung #24 folgen erst nach ZS-2.
