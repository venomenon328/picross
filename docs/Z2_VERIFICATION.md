# Z2: native Bucharbeitsansicht – Prüfbericht und Eigentümerprobe

Stand: 27.09.2026 · #23 / I-01 bis I-05 · eigener Draft unter #21

Quellbasis: `c3a5386580d7a0da29b927b41bd692f0cca59274`, regulärer P1-Kern.
Aktive Entscheidungen und native Abweichungen: [Z2-Auswahl](Z2_SELECTION.md).
Die endgültige Zuordnung von Quellhead, Test-Merge, CI-Run und Artefakt-Hashes
steht im zugehörigen Draft-PR und in `product-report.json` / `z2-binding.json`.
Ein Bericht im ZIP ist Teil seines benannten Quellstands, kein zirkulärer Hashbeleg
seines eigenen ZIPs. Es erfolgt kein Merge oder Release.

## Technischer Prüfweg

```sh
python -m unittest discover -s tools -p 'test_*.py' -v
python tools/check_docs.py
python tools/z2_resources.py verify
git diff --check
python tools/p1_product.py --cache-dir <externer-cache> --output-dir <externe-ausgabe>
```

Für jeden Produktlauf ein neues beziehungsweise leeres Ausgabeverzeichnis verwenden.
Der Harness verweigert ein nichtleeres Ziel, damit keine alten Screenshots in eine
neue Quell-/Hashbindung geraten. Bestehende Prüfpakete bleiben erhalten.

Der Produktweg prüft weiterhin den gesamten P1-Vertrag: beide Deduktionsnachweise,
Godot-Import/Tests, 500 Aktionen mit unabhängigem Oracle, echten Zwei-Prozess-Neustart,
erwarteten Exit-23-Negativtest, Start, bestehende Render-/G1-/H1-Regressionen,
regulären Windows-Export und die getrennte H1-Probe. Die unverkleinerte Rendermatrix
läuft in acht getrennten Prozessen (Layout, Ansichten, Zellfarben 1/2, Gesten,
Hinweise, Achsen und H1); jede Phase bleibt unter dem bestehenden 300-Sekunden-Limit. Auf Windows startet er sowohl
die exportierte Konsole als auch das echte OpenGL-Fenster mit Arbeitsbereichstest.
Linux-CI exportiert Windows, behauptet aber keinen Windowslauf.

| Matrix | Zusätzliche Evidenz |
| --- | --- |
| Z2-A01/A02 | `z2_cases.gd`: reguläre Auswahl, echte Viewport-Ereignisse für Werkzeuge, Palette, Undo/Redo, Zoom und Navigation, tatsächliche Fontnamen. `z2_capture.gd`: N1, per Zellgesten ausgelöster Abschluss, vorhandenes Album. |
| Z2-A03 | Alle N1-Zugänge mit konsistenter History/Redo/Ansicht; verdeckte Klicks/Rad ignoriert; Abbruch von Zelle, Raster, beiden Hinweisachsen und Miniatur; UI-Skalierung/Resize in N1. |
| Z2-A04 | Fehler nach Rotation: Primary fehlt, Backup bleibt unverändert, Arbeitsansicht/Fehler/Reparatur bleiben erreichbar. Abbruch der Bestätigung, erneuter Versuch, bestätigte Reparatur und unberührte Nachbarslots. Auch ein fehlgeschlagener N1-Rückweg hält die Reparatur oberhalb der Informationsseite erreichbar. Bestehende Recoverytests bleiben aktiv. |
| Z2-A05 | Fünf native Referenzen einschließlich exakter 57×28-/29×17-Fläche; vier Clientgrößen × zwei UI-Skalen, Raster-/Werkzeugabstand und Mindesttrefferflächen. |
| Z2-A06 | Bestehende Hint-/G1-/H1-Tests; historischer 24-px-Snapfall bleibt zusätzlich zur nativen 30-px-Route erhalten. C1-Tooltip/Drag und 1:1-Ausschnitte. |
| Z2-A07 | `z2-renders.json`: echte Fontnamen, native Textkontraste über korrespondierende Glyphen-/Untergrundpixel; zusätzliche visuelle Detailprüfung. Keine universelle Barrierefreiheitsbehauptung. |
| Z2-A08 | Ungekürzter isolierter Produktweg mit Export; aktuelles `docs`, `product`, `preflight` und vollständiger Diffcheck vor Übergabe. |

Die ursprünglichen gleichfarbigen Papiererwartungen der Pixeltests sind durch
den tatsächlich darunter gerenderten A-Papierpixel ersetzt. Glyphenmessungen
verwenden den gewählten Plex-Font; Marker erlauben dessen Antialiasing. Fachliche
Invarianten, Negativkontrollen und ursprüngliche Szenarien bleiben erhalten.

Gezielte lokale Nachprüfung am 27.09.2026: native Godot-Tests ohne Befund;
Hint-, Achsen- und H1-Renderphasen erfolgreich. Die fünf Referenzrechtecke werden
im Capture gegen die ausgewählten Maße geprüft. Die eigene native Z2-Messung auf
Windows / Godot 4.7.2 / OpenGL / NVIDIA GeForce RTX 3070 erfasst 88 Textproben,
einschließlich Recoverydialog, mit kleinstem Normaltextkontrast 7,39:1. Sie misst
den tatsächlich gerenderten Untergrund an deckenden Glyphenpixeln, nicht einen
Papiermittelwert. Normale Texte, C1-Ziffern, Farbflächen, Werkzeugzustände,
N1 und eingebettete Bestätigungsdialoge wurden zusätzlich visuell betrachtet.
Die Dialogeinbettung ist eine Capture-Einstellung; die reguläre App verwendet
weiterhin Godots normale Dialogfenster. Die vollständigen aktuellen Endresultate,
Artefakte und das getrennte Selbstreview werden commitgebunden im Draft-PR geführt.

## Artefakte und Sichtprüfung

Der CI-Artefaktlink im PR enthält `picross-p1-windows-x86_64.zip` (beide EXEs,
eingebettete Offline-Ressourcen, OFL-Texte, Commitkennung, Anleitung und sicherer
Profilstarter), `picross-z2-review.zip`, Logs, Renderbilder und JSON-Berichte.
Das Review-ZIP öffnet sich über `index.html`; Bilder für 1:1-Prüfung direkt öffnen.
`z2-binding.json` bindet Windows-ZIP, alle Reviewbilder, A-/Font-/Iconressourcen,
Quellhead, tatsächlichen Checkout und CI-Run. Es gibt kein separates Fontpaket.

Vorherbilder entstehen aus der regulären Basis in einer eigenen temporären
Projektkopie mit denselben z1-demo-1-Zellen, Fenstergrößen, UI-Skalen und Zellmaßen.
Die Layoutanordnung ist jeweils Ergebnis der alten/neuen UI. N1 hat keinen
angeblichen Vorgänger. Die Demoaktionen existieren ausschließlich in Tests.

Zu betrachten: beide Hinweisachsen, Farben 2/4, voller Tooltip, kontinuierlicher
Drag, H1-Striche, getrennte RGB-Füllungen, aktive/deaktivierte Icons, Palette,
Falz/Ränder, UI 125 %, N1-Hilfe/Einstellungen und blockierte Recovery mit Dialog.
Automatisierte Renderbilder belegen keine physische DPI-/Mausabnahme.

## Offenes Mergegate: repräsentative Eigentümerprobe

**OFFEN – Z2-M01/M02/M03.** Verantwortlich ist der Eigentümer, am im PR eindeutig
benannten Windows-ZIP. Ebenfalls vor Merge erforderlich: unabhängiges technisches
und visuelles Review und erfolgreiche aktuelle Checks. Das getrennte Selbstreview
des Implementierers ersetzt keine dieser Abnahmen. Frühere P1-/G1-/H1-Freigaben
gelten nicht als Z2-Freigabe. Die längere atmosphärische Sitzung bleibt #24.

1. ZIP vollständig entpacken. In PowerShell ein neues eigenes Profil unter TEMP
   wählen, etwa `$z2Profile = Join-Path $env:TEMP 'picross-z2-owner-01'`.
   Aus dem entpackten Ordner `./owner-probe.ps1 -Exe ./picross-p1.exe -Profile $z2Profile`
   starten. Der mitgelieferte Starter isoliert APPDATA/LOCALAPPDATA und verweigert
   fremde bestehende Profile ohne seinen Marker. Keine echten Saves kopieren.
2. **M01:** F-02 wählen. Hand → Farbe und Radierer → Farbe betätigen: jeweils Füllen,
   nächster Zellklick setzt diese Farbe. Strich, Rückzug, Undo/Redo, Hinweisdrag und
   Miniatur bedienen. Pfeil/`?`/Menü müssen dieselbe N1 öffnen; Einstellungen bzw.
   Hilfe sofort sichtbar. H1/UI 125 % bedienen, zurück: bestätigte Zellen, History,
   Werkzeug und bewusst unveränderte Lesepositionen bleiben erhalten.
3. **M02:** F-01/F-02/F-03 bei tatsächlich erreichbaren 1080p/1440p sowie 1280×720
   betrachten; UI 100/125 %. Keine Monitorfähigkeit vortäuschen. Originalziffern,
   C1, Zellzwischenräume, Fünferlinien, Randmarker, Werkzeugzustände, Falz und N1
   beurteilen. Windows-Skalierung, reale Clientgröße, UI-Skala und verwendeten
   ZIP-SHA-256 im Ergebnis notieren. Hilfe durchscrollen, Tooltip per Maus erreichen.
4. **M03:** Teilstand und Redozweig erzeugen, regulär beenden und mit demselben
   Starter/Profil wirklich neu starten. History/Ansicht fortsetzen. Für sichere
   Fehlerproben F-03 verwenden (der bestehende Starter begrenzt Eingriffe darauf):
   mindestens zwei wirksame Aktionen speichern. In einer zweiten PowerShell mit
   denselben Parametern zusätzlich `-Action BlockSave` ausführen, in der App Zoom
   ändern und N1 öffnen: Fehler sichtbar, Arbeit bleibt offen. `-Action UnblockSave`,
   Übergang erneut versuchen. Für Recovery App schließen, `-Action HidePrimary`
   ausführen und neu starten. Backupstatus muss sichtbar sein; nach Änderung darf
   N1 die Reparatur nicht unerreichbar machen. Bestätigung abbrechen, danach bewusst
   übernehmen und erneut wechseln. Die anderen Blätter bleiben unverändert.
5. Ergebnis je M01/M02/M03 mit Artefaktidentität, Umgebung und konkreten Befunden
   im PR festhalten. Nicht durchgeführte Schritte ausdrücklich offen lassen.

Der Starter verschiebt nur das isolierte F-03-Primary nach `f03.owner-held` und
entfernt bei UnblockSave ausschließlich den von ihm angelegten leeren Tempordner.
Keine produktiven Speicherdateien, globalen Godot-Einstellungen oder Dienste werden
für diese Probe benötigt. Einzelreset bleibt mit bestehender Bestätigung im Album.
