# P1.1 · Spielprobe mit Maus

Zwischenstand zu Issue #8: ein monochromes 20×20-Rätsel, ohne Wertung,
Fehlerhilfe oder dauerhafte Speicherung. Albumwechsel erhält den Stand nur
innerhalb dieser Sitzung. Beenden verwirft ihn. K-06 ist noch offen.

## Windows starten

Das komplette ZIP entpacken und `picross-p1.exe` starten. Godot muss dafür
nicht installiert sein. `picross-p1.console.exe` zeigt zusätzlich technische
Ausgaben. `product-report.json` und diese Anleitung enthalten die
Quellcommitkennung; CI-Lauf und Artefaktkennung stehen zusätzlich im PR.
Dies ist eine unsignierte Debug-Spielprobe, kein Release oder Installer.

„Blatt 01 · 20 × 20 · öffnen“ öffnet das Rätsel. Hinweise stehen links und
oberhalb des Rasters; „–“ bedeutet eine vollständig leere Linie. Gleiche
Füllblöcke sind durch mindestens eine leere Zelle getrennt.

## Bedienung

- Linke Maustaste: füllen. Rechte Maustaste: leer markieren (Kreuz).
- „Radierer“ wählen, dann links klicken/ziehen: auf unbekannt zurücksetzen.
  Rechts bleibt auch beim Radierer die Leermarkierung. „■ Füllen“ schaltet zurück.
- Ziehen hält nach der ersten eindeutigen Bewegung eine Zeile oder Spalte fest.
  Bei genau diagonalem Start bleibt zunächst nur die Startzelle ausgewählt.
- Der kupferfarbene Rahmen markiert die unbestätigte Vorschau. Zurückziehen
  verkürzt sie; Loslassen übernimmt den letzten Abschnitt als eine Aktion.
- Bestehende Einträge sind geschützt. Erst gezielt radieren, dann neu setzen.
- Außerhalb des Rasters bleibt der letzte gültige Endpunkt stehen. Esc oder
  Fokusverlust verwirft den Strich; ein Albumwechsel ebenso.
- „Rückgängig“ nimmt einen ganzen Strich zurück, „Wiederholen“ stellt ihn wieder her.
- Die Miniatur zeigt nur deine Eingaben (mit derselben Vorschau), einschließlich
  möglicher Fehler. Punkte stehen dort für leere, helle Flächen für unbekannte Zellen.
- Für den Abschluss genügen alle richtigen Füllungen ohne zusätzliche Füllung.
  Hintergrundfelder müssen nicht vollständig ausgekreuzt sein. Erst dann
  erscheinen Motivname, Kolorierung und der fertige Albumeintrag.

Noch nicht enthalten: weitere Rätsel, Zoom/Pan, interaktive Miniaturnavigation,
Speichern/Fortsetzen, Tastatur-/Controllerbedienung, Wertung und Audio.
Die Oberfläche ist ab einer logischen Fläche von 1280×720 vorgesehen.

## K-06 · Eigentümerprobe vor #9

Am gelieferten Artefakt mit echter Maus prüfen:

1. In einer freien Zeile bei Spalte 5 beginnen, bis 12 ziehen, auf 9 zurückgehen:
   Vor Loslassen nur Vorschau, danach ausschließlich 5–9 gefüllt.
2. Ein Kreuz und eine Füllung vorbereiten und darüberziehen: beide bleiben geschützt.
   Mit Radierer korrigieren; Rückgängig/Wiederholen stellt genaue Zustände wieder her.
3. Diagonal beginnen, über den Rand ziehen und mit Esc beziehungsweise Fensterwechsel
   abbrechen. Keine unerwarteten Füllungen oder fortgesetzten Striche.
4. F-01 tatsächlich lösen, ohne alle Hintergrundzellen auszukreuzen. Vor Abschluss
   keine Lösungshilfe oder Motivdaten, danach erkennbar dasselbe kolorierte Motiv.

Bitte Quellcommit/Artefaktkennung, Windows-Version, Bildschirm- und Fenstergröße,
reale Anzeigeskalierung und Ergebnis/Abweichungen festhalten. Referenzhardware:
Windows 11, 2560×1440, Ryzen 7 5800X, RTX 3070. Skalierung wird nicht angenommen.
Codex-Tests und Start-Smoke ersetzen diese reale Mausprobe nicht.

## Entwicklung und technische Prüfung

Im Repository-Root mit Godot Standard 4.7.2-stable:

```sh
godot --headless --path prototypes/p1 --import
godot --headless --path prototypes/p1 --script res://tests/run_tests.gd
godot --path prototypes/p1
```

Für den vollständigen, isolierten Nachweis samt Export unter Windows PowerShell:

```powershell
$p1Cache = Join-Path $env:TEMP 'picross-p1-preflight-cache'
python tools/p1_product.py --cache-dir $p1Cache --output-dir artifacts/p1-product
```

Der Harness prüft dieselben offiziellen Archive wie P1.0, kopiert das Projekt
in einen temporären Arbeitsbereich und isoliert APPDATA/LOCALAPPDATA beziehungsweise
XDG-Pfade. Er prüft auch einen absichtlich fehlschlagenden Test (Exit 23), beendet den
Headless-Start automatisch und exportiert mit `P1 Windows x86_64`. Auf Windows wird
zusätzlich die exportierte Konsolenfassung kontrolliert gestartet. Keine Spielstände
werden gelesen oder geschrieben. Pro Prozess gelten 300 Sekunden, pro Download 1200.
Der Bericht unterscheidet Quellhead, getesteten Checkout und veränderten Arbeitsbaum.

Für einen direkten Export zuvor das Zielverzeichnis `prototypes/p1/build/windows/`
anlegen und die passenden Standard-Exportvorlagen installieren:

```sh
godot --headless --path prototypes/p1 --export-debug "P1 Windows x86_64" build/windows/picross-p1.exe
```

Die Herkunft und der nur für Prüfer gedachte Deduktionsnachweis stehen in
[F01_PROOF.md](F01_PROOF.md). Dieses Dokument enthält Motivspoiler und gehört
nicht zur Anleitung für die ungelöste Spielprobe.
