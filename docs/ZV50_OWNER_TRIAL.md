# ZV-50 · gezielte Sicht- und Mausprobe

Stand: 06.10.2026 · [Issue #50](https://github.com/venomenon328/picross/issues/50).

Diese Probe ist nach der ausdrücklichen Mergeanweisung vom 06.10.2026 **kein Gate
für den beauftragten #50-Merge**. Sie wurde nicht durchgeführt und wird nicht als
bestanden behauptet. Die Anleitung bleibt für eine optionale reale Nachprobe erhalten.

## Isolierter Start

Das Actions-Artefakt `picross-p1-player-<Head>` entpacken, anschließend auch
`picross-p1-windows-x86_64.zip`. In PowerShell im entpackten Spielerordner:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\zv50-owner.ps1 -Profile (Join-Path $env:TEMP 'picross-zv50-meine-probe')
```

Der Helfer prüft Head und EXE-Hash und verwendet eigene APPDATA-/LOCALAPPDATA-Pfade.
Normale Spielstände werden nicht gelesen oder verändert.

## Szenario

1. Blatt 04 bei UI 100 % und möglichst 1920×1080 Clientfläche öffnen. Arbeitsgröße
   wählen. Das vollständige 20×20-Raster soll kompakt bleiben.
2. Nacheinander auf ungefähr 133 % und 150 % zoomen. Das vollständige Raster samt
   Hinweisen soll weiter sichtbar sein; Miniatur und Werkzeugleiste bleiben frei.
3. Einen weiteren Schritt auf ungefähr 167 % zoomen. Jetzt darf der echte
   Papier-/Werkzeugrand einen Ausschnitt erzwingen. Mit Hand/Miniatur navigieren,
   eine sichtbare Randzelle anklicken und zurück auf 150 % zoomen.
4. Einen Mausradzoom an einem deutlich außermittigen Rasterpunkt ausführen. Derselbe
   Rasterbereich soll unter dem Zeiger bleiben, soweit die reale Begrenzung dies
   zulässt.
5. Optional UI 125 % beziehungsweise ein kleineres Fenster prüfen: früheres
   Clipping ist zulässig, aber keine Überdeckung von Werkzeugen oder versteckte
   Zellverkleinerung.

Protokoll: Head/Artefakt, Windows-Version, Bildschirm- und Clientfläche,
Windows-Skalierung, UI-Skala, Zoomstufen sowie Ergebnis/Abweichungen. Technische
Renderbilder oder diese nicht ausgeführte Anleitung sind keine reale Abnahme.
