# ZS-2 · reguläre Windows-Spielprobe

Stand: 09.10.2026 · **ZS2-M01 / R1-A01 offen**. ZS1-M01 wurde nach Merge von PR #55 vom
Eigentümer erfolgreich abgeschlossen; diese neue Probe betrifft die reguläre
Integration aus #53. Sie ist vor dessen Merge erforderlich.

Das zum Lieferhead gehörige `picross-p1-player-<Head>` herunterladen, das innere
`picross-p1-windows-x86_64.zip` vollständig entpacken und die mitgelieferte
`rp6-owner.ps1` verwenden. Der vorhandene Launcher legt ein separates Profil an
und startet die reguläre EXE. Für Fortsetzen denselben Profilpfad wiederverwenden;
Bedienung und Parameter stehen in `RP6-SPIELPROBE.md`. Ein direkter EXE-Start
verwendet dagegen die normalen P1-Slots. Dies ist ein Testexport, kein Release.

Quellhead, Basis, getesteter Checkout/Test-Merge, CI-Run und EXE-Hashes stehen in
`product-report.json`; ZIP-Hash und Downloadbindung im zugehörigen Draft-PR.
Chalkboard Regular ist eingebettet. Herkunft und bestehende Nutzungshinweise
stehen in `licenses/Chalkboard-NOTICES.md`; es wird keine neue Lizenz behauptet.

1. F-01 und F-02 öffnen: Chalkboard-Ziffern, drei Hinweiszustände, C1 und lange
   Hinweisfolgen prüfen. Zeilenhinweise verwenden 26 × UI, Spalten 18 × UI.
   Tooltip, Drag/Snap und zurückgekehrte Lesepositionen auf beiden Achsen prüfen.
2. Kurze und lange Stift-/X-Striche ziehen, verlängern, zurückziehen, am Ursprung
   die Achse neu wählen und per Escape abbrechen. Die vollständige Zielvorschau
   bleibt beim Warten statisch. X↔Füllung und Entfernen dürfen keine alte
   Gegenmarkierung stehen lassen; Miniatur folgt unmittelbar den eigenen Zellen.
3. Nach Mouse-Up räumlichen Stiftaufbau und X-Zug 1 vor Zug 2 beobachten.
   Das X muss bei normalen 24-px-Zellen sichtbar geschrieben werden; auch kleine
   12- und größere 36-px-Zellen prüfen. Setzen/Umwandeln startet vom tatsächlichen
   Start zum finalen Ende: Δ = min(8 ms, 120 ms/(m−1)) bei m > 1 wirksamen Zellen,
   140 ms je Zelle, maximal 260 ms insgesamt. Schutzlücken erzeugen keine Pause;
   Entfernen startet gemeinsam und dauert 80 ms. Beide Achsen/Richtungen,
   Umwandlung sowie 1/kurze/16/17/100 Zellen und G1-Rückzug vergleichen. Rasch weiterzeichnen, in laufende Effekte hineinzeichnen und
   zurückziehen/abbrechen. Keine verlorene Eingabe oder wiederkehrende Altmarkierung.
4. Während links gehalten ist rechts drücken und umgekehrt, auch außerhalb des
   Rasters im Fenster: Vorschau und Zähler verschwinden ohne Übernahme. Beide
   Tasten loslassen, erst dann frisch beginnen. Unterschiedliche Up-Reihenfolgen,
   erneutes Drücken bei noch gehaltener Taste, Escape und Fokuswechsel prüfen.
   Keine Phantomaktion, bleibende Sperre oder später wiederkehrende Animation.
   Mittlere Taste und Hand bleiben Navigation; Zählen ohne Commit bleibt separat.
5. Undo/Redo, Fokusverlust, Zoom/Pan/Resize sowie Blatt-/Album-/Informationswechsel
   prüfen. Unter Menü/Einstellungen „Zellanimationen“ aus- und einschalten:
   Aus beendet Effekte sofort; An spielt nichts nach. Aus bleibt über Blätter und
   Reset erhalten; nach vollständigem Neustart steht der Schalter wieder auf An.
6. F-07 (100×100 Farbe) mit vielen X und raschen langen Strichen spielen.
   Kleine Zellen, Randanschnitte, Farben, Fünferlinien und Gesamtansicht beurteilen.
   F-01 bei 1920×1080/UI100 muss bis 150 % vollständig sichtbar bleiben.
   1280×720/UI125 und weitere tatsächlich verfügbare Fenstergrößen vergleichen.
7. Speichern/Beenden/Fortsetzen im selben Testprofil durchführen. Eigene Fehler,
   Undo/Redo und semantische Hinweislesepositionen müssen erhalten bleiben.
   Ein echter letzter Lösungsstrich muss sofort zum Abschluss führen.

Bitte Ergebnis im #53-PR am tatsächlich verwendeten Artefakt festhalten:

| Feld | Ergebnis |
| --- | --- |
| Quellhead, Run/Artefakt, ZIP-SHA-256 | offen |
| Windows-Version, Bildschirm und tatsächliche Clientfläche | offen |
| Tatsächliche Windows-/UI-Skalierung, Arbeitszoom, Maus | offen |
| F-01/F-02/F-07, Hinweise/C1/Lesbarkeit | offen |
| Vorschau, Umwandlung, Abbruch, schnelle Folgegesten | offen |
| X sichtbar geschrieben bei 12/24/36 px; gerichtete Folge und Obergrenze | offen |
| Gegentasten-Abbruch, Fokus-Rückkehr und frische Eingabe | offen |
| Bisherige Änderungsrückmeldung zu N01–N03 erneut beurteilt | offen |
| Bewegung An/Aus, Performance und Ablenkung | offen |
| Undo/Redo, Seitenwechsel, Speichern/Fortsetzen/Abschluss | offen |
| Urteil und konkrete reproduzierbare Auffälligkeiten | offen |

Technische Bild-/Zeitnachweise und Selbstreview ersetzen diese Eigentümerprobe
nicht. Unabhängiges Review und passende Mergefreigabe bleiben separate Gates.
