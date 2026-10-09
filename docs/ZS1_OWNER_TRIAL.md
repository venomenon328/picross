# ZS-1 · native Gestaltungsprobe

Aktualität 09.10.2026: Historische ZS1-Abnahmen und Timingwerte unten bleiben
an ihren alten Stand gebunden. Neue Studienexports erben den gemeinsamen
ZS2-Zeichner mit 210/120 ms, 12/180-ms-Staffelung (maximal 390 ms) und sichtbaren
Schraffurzügen ohne volle Unterzeichnung aktiver Füllungen.
Aktuelle Nachweise und offene Abnahme: [ZS2-Verifikation](ZS2_VERIFICATION.md).

Aktualitätshinweis 09.10.2026: Die unten beschriebene gleichzeitige Bewegung gehört
zum historisch abgenommenen ZS1-Stand. Neue Studienexports erben den gemeinsamen
Zeichner mit ZS2-N01–N03 (gerichtete Folge, geschriebenes X, Gegentasten-Abbruch).
Dessen aktuelle Prüfung und offene Abnahme stehen in [ZS2_VERIFICATION.md](ZS2_VERIFICATION.md);
die alte ZS1-M01-Bestätigung wird dadurch nicht auf einen neuen Head übertragen.

Stand: 07.10.2026 · ZS1-M01/E3: **nach Merge auf main erfolgreich abgeschlossen; Kombination bestätigt**

Das Studien-ZIP vollständig entpacken und `picross-zs1.exe` starten. Godot,
**Bakso Daging Regular und Chalkboard Regular** sowie die bisherigen UI-Fonts sind
eingebettet. [Quellen und Nutzungshinweise](ZS1_FONT_INPUT.md) folgen E2.
Dies ist ein Windows-Testexport, kein Release. **Chalkboard Regular, Stiftfüllung
und kurzes Timing sind gewählt.** Nach N07 startet die Studie mit Chalkboard und
kompakteren Zeilenhinweisen links vom Raster; Bakso/Plex bleiben nur Vergleich.
ZS1-M01 ist nach Merge von PR #55 auf `main@985cf08e` am 07.10.2026 vom Eigentümer erfolgreich abgeschlossen und die Kombination bestätigt. #52 ist abgeschlossen. Die [reguläre ZS-2-Integration](ZS2_VERIFICATION.md) ist separat beauftragt; ZS2-M01, unabhängiges aktuelles Review und Mergefreigabe bleiben vor Merge offen. Kein Release.
Quellhead, Basis, getesteter Checkout/Test-Merge, Run und EXE-Hashes stehen in
`zs1-report.json`; die genaue Downloadbindung steht im gemergten PR #55.

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
| Head, Run/Artefakt und ZIP-Hash | ZS1-M01 nach Merge `main@985cf08e` bestätigt; keine zusätzliche Artefaktkennung mitgeteilt |
| Windows-Version, Bildschirm, tatsächliche Clientfläche, Windows-Skalierung | offen |
| UI-Skalierung, Arbeitszoom, Eingabegerät | offen |
| Hinweisfont | Chalkboard gewählt; Bakso/Plex nur Vergleich |
| Stiftfüllung und Timing | bereits positiv gewählt |
| Neues X und räumlicher Strichaufbau | Kombination bestätigt |
| Zusätzliche Rand-UI | verworfen und entfernt; Hintergrundarbeit separat |
| Vorschaukontrast 56 % | bestätigte Kombination; keine gesonderte Messung mitgeteilt |
| Kleine Zellen, C1, Hinweisdrag/Tooltip, F-03-Folgegesten | Gesamtprobe erfolgreich; keine gesonderten Messwerte mitgeteilt |
| Kompaktere Zeilenhinweise (26 px bei UI 100 %) | nach Merge bestätigt |

Die erfolgreiche Nachprüfung ist in #52 dokumentiert. Diese Anleitung bleibt die
Studienanleitung; die reguläre Integration hat eine eigene [ZS2-M01-Probe](ZS2_OWNER_TRIAL.md).
