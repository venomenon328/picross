# GP-48 · Gezielte Eigentümerprobe

Stand: 06.10.2026 · [Issue #48](https://github.com/venomenon328/picross/issues/48).
**GP48-M01 wurde am 06.10.2026 vom Eigentümer durchgeführt und als „funktioniert wie gewünscht“ bestätigt.**
Dies ist eine kurze Bedien-/Sichtprobe, keine vollständige Rätsellösung oder RP-6-Abnahme.

## Download und isolierter Start

Im Gameplay-PR den direkten Download `picross-p1-player-<Head>` verwenden.
Das äußere Actions-ZIP enthält nur `picross-p1-windows-x86_64.zip`;
dieses zweite ZIP ebenfalls vollständig entpacken. Der PR nennt Actions-Digest,
Spiel-ZIP-Hash und EXE-Hashes. `product-report.json` und `README.txt` binden den Head.
Keine Godot-Installation nötig. Unsignierte Windows-Debugprobe, kein Release.

PowerShell im entpackten Spielerordner, mit einem neuen TEMP-Unterordner:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\gp48-owner.ps1 -Profile (Join-Path $env:TEMP 'picross-gp48-meine-probe')
```

Der Helfer prüft EXE/Head und startet mit eigenen APPDATA-/LOCALAPPDATA-Pfaden.
Denselben Ordner nur für die Fortsetzung desselben Heads verwenden. Normale Saves
bleiben getrennt. `-ExecutionPolicy Bypass` gilt nur für diesen gestarteten Prozess;
keine globale Skriptrichtlinie wird geändert. Falls eine verbindliche Richtlinie
den Helfer sperrt, die Prüfung als nicht gestartet dokumentieren.
Das isolierte Profil enthält nur F-01 bis F-04; bisherige RP-6-Spielarbeit bleibt
in ihrem eigenen Profil. Die spätere Zusammenführung/Fortsetzung ist separat.

## Sechs Gestenfälle

F-02 öffnen; für die Vorbereitung eine frei gewählte Zeile mit Einzelklicks als
`? X F ? X` beziehungsweise `X ? F X ?` markieren (`?` unbekannt, `F` vorhandene
Füllung). Bei Bedarf mit Radierer säubern. Eine zweite Farbe für `F` verwenden;
danach wieder Farbe 1 wählen. Jeden Versuch vom gleichen Ausgangsstand starten;
Undo nach jedem Versuch oder neu vorbereiten. Koordinaten stehen am Arbeitsbereich.

| Start / Taste | Ausgangsfolge | Sollfolge nach Ziehen über fünf Felder |
| --- | --- | --- |
| Unbekannt / links | `? X F ? X` | `A X F A X` |
| Unbekannt / rechts | `? X F ? X` | `X X F X X` |
| X / links | `X ? F X ?` | `A A F A A` |
| X / rechts | `X ? F X ?` | `? ? F ? ?` |
| Füllung / links | `F ? X F ?` | `? ? X ? ?` |
| Füllung / rechts | `F ? X F ?` | `X X X X X` |

`A` ist die am Gestenstart aktive Farbe. Vorhandene Füllungen werden links
nicht umgefärbt. Einen Fall auch senkrecht wiederholen. Bei gedrückter Taste
verlängern und zurückziehen: Raster, eigene Miniatur und geometrischer Zähler
folgen nur dem aktuellen Abschnitt. Zur tatsächlichen Startzelle zurückkehren,
senkrecht weiterziehen: Startzustand/Farbe bleiben fest, nur die Achse wechselt.
Loslassen übernimmt eine Aktion; Undo/Redo stellt den ganzen Strich wieder her.
Einmal mit Esc abbrechen und die unveränderten Ausgangszellen prüfen.

## Drei Hinweiszustände und Abgrenzungen

F-01 öffnen. Zeilen/Spalten ab oben/links mit 1 zählen:

1. In Zeile 4 Spalten 9–11 füllen. Die `3` ist abgeschwächt, ohne Strich.
   Rechts X in Spalte 8 setzen: weiterhin abgeschwächt. X in Spalte 12 ergänzen:
   durchgestrichen. Undo/Redo und Entfernen des X nehmen den Status zurück.
2. Für den tatsächlichen Rasterrand dieselbe einzelne `3` in Zeile 4 vorbereiten:
   alte Füllungen/X per Radierer entfernen, Spalten 1–3 füllen. Ohne X in Spalte 4
   abgeschwächt; mit X in Spalte 4 durchgestrichen. Nur der echte Linienrand zählt.
   Dies ist absichtlich ein linienkompatibler Bedienfall, kein Lösungsbeweis.
3. F-02, Zeile 12: Farbe 4 in Spalten 2–5, Farbe 2 in Spalten 6–12 setzen.
   X in Spalte 1 schließt den ersten Block mit X und direkt anderer Farbe ab;
   dessen `4` wird durchgestrichen. Der Nachbarblock muss nicht selbst abgegrenzt
   sein. Eine zusätzliche Leerzelle zwischen den Farben ist nicht erforderlich.
4. F-02, Zeile 2: Farbe 4 in Spalten 2–39. Die mehrstellige `38` bleibt ohne X
   abgeschwächt; X in 1 und 40 streicht sie durch. In Spalte 38 Farbe 4 in
   Zeilen 2–38 und Farbe 1 in Zeile 39 setzen: beide Hinweise und Farbwechsel
   beurteilen. Die Bewertung bezieht sich auf jede vollständige Linie unabhängig.

Ein über Zoom/Pan entstandener Ausschnittrand schließt keinen Block ab.
Mehrdeutige Hinweise bleiben normal, widersprüchliche Linien verlieren positive
Zustände. Es gibt keine rote Fehlerhilfe oder automatisch gesetzten X.

## Lesbarkeit und leeres Ergebnisprotokoll

Mono-/Farbzahlen in beiden Achsen, ein-/mehrstellige Zahlen und alle drei Zustände
bei UI 100/125 % ansehen. Die Farbe muss auch abgeschwächt erkennbar bleiben;
Statuswechsel dürfen Zahlengröße/Position nicht verändern. F-02 lange Zeile 12
oder F-03 (nur technischer Großrasterfall) mit mittlerer Taste ziehen und den
vollständigen Hoverhinweis lesen. Unter Einstellungen den bestehenden Schalter
aus/an schalten: normale/aktuelle Zustände, ohne Änderung von Zellen oder Undo.

| Angabe | Tatsächliches Ergebnis – vom Eigentümer ausfüllen |
| --- | --- |
| Datum, Head, Run, Artefakt, ZIP-Hash | ____ |
| Windows-Version, Bildschirm, Client/Rahmen | ____ |
| Windows-Skalierung, UI-Skala, Zoom, Maus | ____ |
| Sechs Gestenfälle / senkrechter Fall | ____ |
| Rückzug / Achsenneuwahl / Abbruch / Undo/Redo | ____ |
| Normal / abgeschwächt / durchgestrichen und Rücknahme | ____ |
| X / echter Rasterrand / Farbwechsel / Ausschnittrand | ____ |
| Mono/Farbe, beide Achsen, Tooltip/Überlauf/Drag | ____ |
| Gesamturteil und konkrete Abweichungen | ____ |

Die leeren Felder oben bleiben die historische Vorlage; nicht übermittelte Umgebungsmetadaten werden nicht nachträglich erfunden. Review R1 und GP48-M01 sind abgeschlossen, PR #49 ist als `add7a7e6` integriert. Für den kombinierten PR-#47-Stand zählt dies als bereits abgenommene GP-Regel; RP-6 besitzt eigene offene Gates.
