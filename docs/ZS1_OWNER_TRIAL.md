# ZS-1 · native Gestaltungsprobe

Stand: 07.10.2026 · ZS1-M01/E3: **Chalkboard, Stift und Timing gewählt; kombinierte Sichtprüfung nach Merge auf main**

Das Studien-ZIP vollständig entpacken und `picross-zs1.exe` starten. Godot,
**Bakso Daging Regular und Chalkboard Regular** sowie die bisherigen UI-Fonts sind
eingebettet. [Quellen und Nutzungshinweise](ZS1_FONT_INPUT.md) folgen E2.
Dies ist ein Windows-Testexport, kein Release. **Chalkboard Regular, Stiftfüllung
und kurzes Timing sind gewählt.** Nach N07 startet die Studie mit Chalkboard und
kompakteren Zeilenhinweisen links vom Raster; Bakso/Plex bleiben nur Vergleich.
Die kombinierte Darstellung wird nach ausdrücklicher Eigentümerentscheidung
anschließend auf dem gemergten `main`-Stand beurteilt.
Quellhead, Basis, getesteter Checkout/Test-Merge, Run und EXE-Hashes stehen in
`zs1-report.json`; die genaue Downloadbindung steht im Draft-PR zu #52.

Der Studienstart verwendet vor dem Laden der Hauptszene einen neuen, eigenen
Ordner unter `%LOCALAPPDATA%/picross-zs1/session-<Prozess>-<Startzeit>/`.
Er liest und verändert keine normalen P1-Slots. Jeder neue Start beginnt mit
frischen Vergleichsständen; innerhalb der Sitzung bleiben Änderungen und
Undo/Redo beim Blatt- und Variantenwechsel erhalten. Die getrennten temporären
Studienordner können nach der Probe gezielt entfernt werden.

1. Die Studie startet mit der bereits gewählten **Stiftfüllung**. Oben lässt sich
   der Hinweisfont zwischen **Bakso Daging**, **Chalkboard** und der bisherigen
   **Plex-Referenz** wechseln. Chalkboard startet als ausgewählte Fassung; Bakso und
   Plex bleiben Vergleichsreferenzen. In den Einstellungen lässt sich der Zellstil unabhängig zwischen
   Stift/neuem X und Baseline wechseln. Zellen, Ausschnitt und Hinweisleseposition bleiben gleich.
   Im Album links stehen F-01 (20×20 Mono), F-02 (40×40 Farbe) und F-03
   (100×100, ausdrücklich UI-Stresstest). Die angearbeiteten Muster enthalten
   nur eigene Beispielmarkierungen, darunter absichtliche Fehler und viele X.
2. In Menü/Einstellungen lassen sich der Vergleichsstand wiederherstellen,
   ein leeres Studienblatt öffnen und die **Ziffernprobe bis 100** betrachten.
   Diese beschriftete Schriftprobe ist kein zusätzlicher Rätseldatensatz.
   Normale, abgeschwächte und durchgestrichene Ziffern auch an echten Hinweisen
   vergleichen. Beispielsweise im leeren F-01 Zeile 4, Spalten 9–11 füllen;
   anschließend Spalten 8 und 12 mit X abgrenzen. Die `3` muss zunächst
   abgeschwächt und danach durchgestrichen sein.
3. F-02: alle vier Farben, angrenzende Füllungen an Fünferlinien und viele X
   vergleichen. Lange Zeilen-/Spaltenhinweise mit mittlerer Maustaste einzeln
   ziehen; nur die gestartete Linie darf folgen. Vollständigen Hoverhinweis,
   C1-Kontur heller Farben und Rückkehr zum vorherigen Ausschnitt prüfen.
4. Auf leerem Blatt links/rechts kurze und lange Striche ziehen, zurückziehen
   und mit Escape abbrechen. Die Vorschau bleibt statisch, heller und zeigt
   ausschließlich das Ziel. Start auf X plus links wandelt zu Farbe, Start
   auf Füllung plus rechts zu X; unbekannter Start schützt Vorbelegungen.
   Beim Radieren verschwindet die alte Markierung schon in der Vorschau.
5. Loslassen: alle geänderten Zellen beginnen gleichzeitig. Füllungen zeichnen
   sich räumlich in kurzen Stiftbahnen; beim X folgt Zug zwei auf Zug eins.
   Gesamtzeit bleibt 140 ms, Entfernen 80 ms (bereits positiv beurteiltes Timing). Sofort eine
   zweite Geste beginnen, auch auf denselben Zellen, dann zurückziehen oder
   abbrechen. Kein alter Effekt darf wiederkommen. Undo/Redo, Seitenwechsel,
   Zoom und Resize müssen sofort reagieren. In den Einstellungen
   **Zellanimationen** ausschalten: laufende Effekte enden sofort; Wiedereinschalten
   spielt nichts nach. Der Schalter gilt für diese Sitzung und startet wieder an.
6. 1920×1080 und 1280×720 mit UI 125 % vergleichen, ergänzend 1600×900 und
   2560×1440. F-01 bei 150 % Arbeitszoom, F-03 bei kleinen Zellen, Gesamtansicht
   und maximalem Zoom prüfen. Zusätzliche Randdekoration ist entfernt; funktionale Buchmontierungen bleiben.
   Auf F-03 lange Striche und schnelle Folgegesten besonders kritisch beurteilen.
7. Links vom Raster die Zeilenhinweise gezielt prüfen: Chalkboard verwendet
   gemeinsame **26-px-Slots bei UI 100 %** (UI-skaliert), also sichtbar weniger
   horizontalen Abstand als der vorige 30-px-Stand. Mehrstellige Hinweise, Marker,
   Drag/Snap und Tooltip dürfen nicht kollidieren. Die Spaltenhinweise oberhalb des
   Rasters behalten ihre bisherige vertikale Slotweite.

Die ursprünglichen Mauswerkzeuge, Miniatur, Hinweisnavigation, Speicherung im
Studienordner und Abschlusslogik bleiben aktiv. Die Miniatur zeigt sofort den
eigenen logischen Zustand, ohne Animation. Kein Motivname/Ergebnisbild vor Abschluss.

Bitte im Issue/PR am konkreten Artefakt festhalten:

| Feld | Eigentümerergebnis |
| --- | --- |
| Head, Run/Artefakt und ZIP-Hash | offen |
| Windows-Version, Bildschirm, tatsächliche Clientfläche, Windows-Skalierung | offen |
| UI-Skalierung, Arbeitszoom, Eingabegerät | offen |
| Hinweisfont | Chalkboard gewählt; Bakso/Plex nur Vergleich |
| Stiftfüllung und Timing | bereits positiv gewählt |
| Neues X und räumlicher Strichaufbau | abschließende Bestätigung offen |
| Zusätzliche Rand-UI | verworfen und entfernt; Hintergrundarbeit separat |
| Vorschaukontrast 56 % | unveränderter Ausarbeitungswert, Einzelbestätigung offen |
| Kleine Zellen, C1, Hinweisdrag/Tooltip, F-03-Folgegesten | offen |
| Kompaktere Zeilenhinweise (26 px bei UI 100 %) | nach Merge auf main prüfen |

E3 erteilt die Mergefreigabe nach technischer N07-Prüfung und verlegt die
kombinierte Sichtprüfung ausdrücklich auf den gemergten `main`-Stand. Das Ergebnis
dieser Nachprüfung vor #53 im Issue festhalten; sie wird nicht als bereits bestanden
behauptet. Diese Studie stellt die reguläre Arbeitsansicht noch nicht um.
