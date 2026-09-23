# P1.2 · Farben, Großraster und Mausprobe

Zwischenstand zu Issue #9 auf dem gemeinsamen P1-Draft #14. F-01 (20×20),
F-02 (40×40, vier Farben) und F-03 (100×100, ausdrücklich UI-Testdatensatz)
sind direkt zugänglich. Keine Wertung, Fehlerhilfe oder dauerhafte Speicherung.
Albumwechsel erhält den eigenen Stand und Undo/Redo pro Blatt innerhalb dieser
Sitzung. Beenden verwirft alle Stände.

## Windows starten

Das vollständige ZIP entpacken und `picross-p1.exe` starten. Keine Godot-Installation
nötig. `picross-p1.console.exe` zeigt technische Ausgaben. Dies ist eine unsignierte
Debug-Spielprobe, kein Release/Installer. Die Quellcommitkennung steht im beigefügten
README.txt; `product-report.json` bindet Head, getesteten Checkout/Test-Merge, Basis,
CI-Lauf, Engine-/Archivhashes, EXE-Hashes und Prüfphasen. Artefaktlink im PR.

Startziel: 1600×900, auf den verfügbaren Arbeitsbereich einschließlich Fensterrahmen
begrenzt. Unter 1280×720 erscheint eine verständliche Meldung. Vergrößern des Fensters
zeigt mehr Raster oder ruhige Ränder; es vergrößert die Arbeitszellen nicht automatisch.

## Bearbeiten und zurücknehmen

- Links auf unbekannt: aktive Farbe setzen. Links auf Füllung: Füllungen neutralisieren,
  auch andere Farben. Vorhandene Kreuze bleiben geschützt.
- Rechts auf unbekannt: Kreuz setzen. Rechts auf Kreuz: Kreuze neutralisieren.
  Vorhandene Füllungen bleiben geschützt.
- Start auf Gegenmarkierung: diese bleibt unverändert; der Strich kann unbekannte
  Nachbarzellen setzen. Zum Umfärben erst neutralisieren, dann neu füllen.
- Modus und Farbe stehen für die gesamte Geste fest. Achse nach erster eindeutiger
  Bewegung fest; bei diagonalem Gleichstand zunächst nur die Startzelle.
- Zurückziehen verkürzt die Vorschau. 5→12→9 übernimmt nur 5–9 als eine Aktion.
  Überqueren des Starts ändert die Achse nicht. Kein mehrfaches Umschalten.
- Außerhalb des sichtbaren Rasters bleibt der letzte gültige Endpunkt stehen.
  Esc, Fokusverlust oder Albumwechsel verwerfen den Strich. Kein Auto-Scrollen.
- Radierer links neutralisiert alle Markierungen; rechts gilt die Kreuzregel.
  Rückgängig/Wiederholen stellt ganze Striche mit exakten Vorzuständen wieder her.
- F-02/F-03: Farbe per Palette A–D wählen. Buchstaben in den Hinweisen entsprechen
  diesen Farben. Gleiche Farbblöcke brauchen Abstand; verschiedene dürfen angrenzen.

## Navigieren und Hinweise lesen

- Mausrad: Zoom am Zeiger. Sichtbare −/+ Knöpfe: Zoom um die Ansichtsmitte.
  Arbeitsstufen 75/100/150/200 % entsprechen 18/24/36/48 logischen Einheiten.
- Mittlere Taste oder Hand-Werkzeug links: Ansicht verschieben. Gesamtansicht passt
  das komplette Raster ein; Arbeitsgröße stellt 100 % wieder her.
- Eigene Miniatur: Klick/Ziehen versetzt den Ausschnitt. Der doppelte Rahmen markiert
  die sichtbare Fläche. Helle Flächen sind unbekannt, Punkte leer, Farben eigene Füllungen
  einschließlich möglicher Fehler und derselben Strichvorschau.
- Während Zellgesten sind Zoom und Navigation gesperrt. Navigation ändert keine Zellen
  oder Undo-Historie. Pro Blatt bleiben Bearbeitung/History erhalten; beim Blattwechsel
  startet die Ansicht wieder bei Arbeitsgröße.
- Hinweise gehören immer zur ganzen nummerierten Zeile/Spalte. „–“ ist eine leere Linie.
  „… ↗“ kennzeichnet Überlauf/verdichteten Zugriff, keine gekürzte Rätselregel.
  Hinweis anklicken oder über einer Zelle die aktive Zeile/Spalte wählen und
  „Ganze Zeile / Spalte ↗“ öffnen. Die Fokusansicht zeigt die vollständigen Folgen,
  mit Umbruch und bei Bedarf Mausscrollen. Miniatur bleibt daneben sichtbar.
- UI 100/125 % vergrößert Oberfläche und Hinweise unabhängig vom Arbeitszoom.
  Bei 1280×720/125 % ist der untere Hilfetext über die Seitenleiste scrollbar;
  Werkzeuge und Hinweiszugriff bleiben erreichbar, die Miniatur bleibt fest sichtbar.

Für den Abschluss genügen alle richtigen Füllungen ohne Zusatzfüllungen.
Hintergrund muss nicht vollständig ausgekreuzt sein. Name und Ergebnisbild erscheinen
erst nach bestätigtem Abschluss. F-01 zeigt das ursprüngliche Raster neben einer
detaillierteren Illustration desselben Motivs. F-03 bleibt auch danach als Test gekennzeichnet.

## Erneute Eigentümerprobe · offen vor Gesamt-P1-Merge

Die frühere #8-Probe ist mit Änderungsbedarf ausgewertet, keine pauschale Abnahme.
Am neuen Artefakt mit echter Maus prüfen und Ergebnisse einzeln protokollieren:

1. M-01: F-01 setzen/neutralisieren, 5→12→9 und Startüberquerung, Gegenmarkierungen,
   Radierer, Undo/Redo, Rand, falsche Tastenfreigabe, Esc und Fokusverlust. Tatsächlich
   lösen ohne Auskreuzpflicht; Detailbild und Raster als dasselbe Motiv beurteilen.
2. M-02: F-02, alle Farben A–D, andersfarbige Rücknahme, lange Hinweise, Farbzuordnung
   und Abschluss. Drei angrenzende Füllungen an einer Fünfergrenze müssen einzeln
   erkennbar sein, auch in Vorschau und bei allen angebotenen Arbeitszoomstufen.
3. M-03: F-03 eine notierte Koordinate bearbeiten, zoomen, weit verschieben und per
   Miniatur/Koordinaten wiederfinden. Keine verlorenen Aktionen oder Hänger.
4. M-06: Startfenster, Vergrößern/Maximieren, 1080p/1440p soweit verfügbar,
   UI 100/125 %, feste Zellgröße bei reinem Resize, erreichbare Werkzeuge/Hinweise.

Protokollfelder: tatsächlicher Head/Artefakt, Windows-Version, Bildschirmauflösung,
Fenster- und Clientfläche, tatsächliche Windows-Anzeigeskalierung, Maus, Szenario,
Ergebnis/Abweichung. Nicht aus Screenshotabmessungen ableiten. Referenz aus früheren
Angaben: Windows 11, 2560×1440, Ryzen 7 5800X, RTX 3070. Die reale Skalierung bleibt
unbekannt. Technische Renderflächen und synthetische Events ersetzen diese Abnahme nicht.

Persistenz/Recovery (#11), 500-Aktionen-Gesamtintegration (#12), Wertung,
Controller/Tastatur und Release bleiben außerhalb dieser Lieferung. Escape ist
weiterhin Mausgestenabbruch. Kein Merge durch diese Übergabe.

## Technische Reproduktion

Godot Standard 4.7.2-stable; vollständiger isolierter Prüfweg im Repository-Root:

```powershell
$p1Cache = Join-Path $env:TEMP 'picross-p1-preflight-cache'
python tools/p1_product.py --cache-dir $p1Cache --output-dir artifacts/p1-product
```

Unter Linux benötigt die echte OpenGL-Renderprüfung `xvfb-run` und Mesa. Der Harness
nutzt nur die gepinnten offiziellen Archive, prüft deren vollständige Hashes, arbeitet
in einer temporären Projektkopie mit isolierten APPDATA-/XDG-Pfaden und installiert
nichts global. Tests, Negativtest Exit 23, Import, begrenzter Start, echte Renderbilder,
Windows-Export und unter Windows exportierter Start. 300 Sekunden pro Prozess,
1200 pro Download. Exportpreset exakt `P1 Windows x86_64`.

```sh
godot --headless --path prototypes/p1 --import
godot --headless --path prototypes/p1 --script res://tests/run_tests.gd
godot --path prototypes/p1
```

Prüferdokumente mit Motivspoiler: [F-01](F01_PROOF.md), [F-02/F-03](F02_PROOF.md).
Technische Ergebnisse und Grenzen im [P1.2-Prüfbericht](../../docs/P1_2_VERIFICATION.md).
