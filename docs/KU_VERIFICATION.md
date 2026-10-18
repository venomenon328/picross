# KU-A · Kataloggestaltung und technische Übergabe

Paket [#244](https://github.com/venomenon328/picross/issues/244), Arbeitsbranch
`feat/244-kataloggestaltung`, eigener Draft-PR gegen `main`. Vertrag:
[Katalogdarstellung](CATALOG_PRESENTATION.md). KU-B bleibt offen.

## Ausgangspunkt und Umfang

Die Startprüfung verwendete den aktuellen Main-Head
`aa7676da70389f5afedc8ccd7d004b90e0878296`. Er enthält den Spezifikationsmerge
`227b966d92e498f41546da0330c6f538afd2be9f` und die danach integrierten CI-A/B/C-Pakete.
Der ursprüngliche Arbeitsbaum samt fremden unversionierten Designarchiven bleibt
unverändert; KU-A arbeitet in einem eigenen Worktree.

Native Windows-Ausführung mit Grafikzugriff, Python/Pillow 12.3.0, gebundene
Godot-4.7.2-Archive und GitHub-Artefaktdownload sind verfügbar. Dies löst die
Umgebungseinschränkung der historischen KU-A-P01/P02-Vorbereitung ab, schließt
aber noch kein technisches Gate. Vorhandene Main-Push-Fehler von Run
39142493446 betreffen CI-Auswahltest/Ergebnisbindung; sie sind kein KU-A-Nachweis.

## Umsetzung und feste Prüfzuordnung

| Akzeptanz | Umsetzung und Prüfrouten |
| --- | --- |
| KU-A-A01/A02 | Ein gemeinsamer einzeiliger Papierstreifen unter dem unverändert mindestens 112 logische Pixel hohen Bildraum; warme Papierfläche und organische Kontur. Größe links, Kreis und vollständiger Schwierigkeitsname mittig, Modus rechts. Vorhandene Schriften und Assets. |
| KU-A-A03 | L1–L5 verwenden die freigegebenen fünf Farben und vollständige Namen ohne sichtbare Nummer. Fehlende Einstufung bleibt neutralgrau mit „Nicht eingestuft“. Keine Bewertungs-/Registryänderung. |
| KU-A-A04 | Mono ohne Farbprobe; tatsächliche Stiftpolygone einschließlich Spitze sind zentriert und auf 30 logische Pixel vergrößert. Dreiergruppe in gedecktem Rot/Blau/Gelb. Kreis und Text haben weder eigenen noch nativen Ersatztooltip. Modus und Reset behalten ihre gezielten Tooltips. |
| KU-A-A05 | Blattkennung links und Symbol/Status rechts in fester gemeinsamer Fußzeile. „Gelöst“ wählt ausdrücklich die Hakenzeichnung; native Pixelprüfung verhindert einen unsichtbaren Statuswechsel. Abschlussvorrang, History/Redo und Zellzustände bleiben unverändert. |
| KU-A-A06 | Gemeinsame Breite aus tatsächlichen Plex-Textmaßen für „50 × 50“, alle fünf Namen und „Nicht eingestuft“, festen Symbolbreiten und Abständen. Neue Spaltenübergänge werden durch Resize durchlaufen. Keine verkleinerte Schrift, keine Ellipse für Metadaten. Reservierungen bleiben unabhängig von Status, Filter und Seite. |
| KU-A-A07 | Native und echte Browserklicks auf Größe, Kreis, Text, Modus, Papier sowie Blatt/Status öffnen dieselbe ID. Bestehende KAT-2/KK-Routen prüfen Filter, Seiten, Recovery, Resetbestätigung und Ursprungsbindung. |
| KU-A-A08 | Bestehende synthetische Fälle prüfen falsche eigene Füllungen, X-only, Undo/Redo-only, gültigen Abschluss, Fehler und Recovery. Fragezeichen, Spoilergrenze, Revealglättung und Ressourcenfreigabe bleiben erhalten. Bedienanleitung aktualisiert. |

`game/tests/kat2_probe.gd` verwendet feste synthetische Fälle. Seine nativen
Berichte enthalten Text-/Kartenmaße, Geometrie, Gerätezuteilung und Originalbilder.
Die KE-/KK-Kennungen der wiederverwendeten Regressionen sind keine historischen
Prüfergebnisse: jeder Lauf erzeugt neue Originale aus dem aktuellen Checkout.
Das aktive Artefaktinventar ersetzt ehemalige Schwierigkeitstooltipbilder durch
die neuen `ke-no-tooltip-*`-Ansichten.

Die Browsergruppe `catalog` prüft Chromium und Firefox mit echter Mausbedienung
bei 1280×720/UI125, 1920×1080/UI100 und 2560×1440/UI125. Read-only-Beobachtung im
separaten technischen Export liefert Textpassung, Popupanzahl, Fußzeile und
Klickpunkte. Der reguläre Spieler erhält keine Prüfschnittstelle.

## Reproduktion und Ergebnisbindung

Die Pflichtauswahl folgt dem vollständigen Base-/Head-Diff und der aktuellen
[CI-Policy](CI_POLICY.md). Neue/geänderte Harnessdateien können sämtliche
Bereiche auswählen. Kein ausgelassener Pflichtjob zählt als Erfolg.

Aus einem sauberen Checkout des konkret geprüften Heads:

```powershell
python tools/ku_windows_probe.py --head <vollständiger-Head> --run <CI-Run-ID> --engine <gebundene-console.exe> --cache-dir <P1-Archivcache> --output-dir <neuer-Ausgabeordner>
```

Der KU-A-Runner verwendet die bestehenden isolierten KAT-2/KB/KK/KE-Routen und
bindet sie mit Paketkennung `KU-A`. Der gemeinsame CI-Spielerprüfer berücksichtigt
CI-C-Artefaktnamen einschließlich Attempt, validiert sämtliche gelieferten
Gruppenberichte und Originalbytes und startet den tatsächlichen Windows-EXE/PCK.
Er prüft zusätzlich den isolierten EA-Schreib-/Neustartweg. Normale Benutzerprofile
werden nicht verwendet; der Fenstermitschnitt umfasst nur das nachgewiesene eigene HWND.

Der Abschlussnachweis im Draft-PR führt finalen Head, Basis, getesteten CI-Merge,
Run/Attempt, ausgewählte Jobs, sauberen Windows-Checkout, Originaldownload samt
Hashes und den getrennten Selbstreview. So muss kein Commit seinen eigenen Hash
enthalten. Lokale Pfade oder frühere Linux-/KE-Belege ersetzen den zugänglichen
aktuellen Windowsnachweis nicht. Weitere Änderungen verlangen eine erneute
Prüfzuordnung zum dann aktuellen Head.

## Getrennte Gates

KU-A-T01 ist erst mit ausgewählter erfolgreicher CI sowie aktuellen technischen
Windows-/Chromium-/Firefoxbelegen am finalen Head erfüllt. Der tatsächliche Stand
wird im Issue und Draft-PR nachgeführt. **KU-A-R01 bleibt für einen unabhängigen
Review offen. KU-A-M01 bleibt für die Eigentümerabnahme offen.** Selbstreview
ersetzt keinen dieser Schritte. Kein Merge und kein Schließen von #244.
