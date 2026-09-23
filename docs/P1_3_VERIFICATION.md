# P1.3 · Persistenz und Recovery: technischer Prüfbericht

Stand: 24.09.2026 · [Issue #11](https://github.com/venomenon328/picross/issues/11) ·
Branch `feat/11-p1-persistence`, Zielbasis
`main@acc9c51161a18cca17813a8e44c07b2cf074cd44`.
Der finale Head, die dazugehörigen CI-Läufe und das Windows-Artefakt werden im
Draft-PR commitgebunden nachgewiesen. Dieses Dokument beschreibt den Prüfvertrag
und lokale Befunde; M-04 ist ausdrücklich keine automatisierte Abnahme.

## Speichervertrag und Recovery

`model/save_store.gd` verwendet ausschließlich `user://p1/saves/` und feste
Fixture-IDs. Schema 1 enthält Definitions-ID/-Revision, Dimensionen, bestätigte
Zellen, gesamte wirksame History samt Redo-Cursor und `undo_used`, Abschlussstatus
sowie Rasterfokus, Arbeitszoom/Gesamtansicht, Werkzeug/Farbe und individuelle
semantische Zeilen-/Spalten-Lesepositionen. Gesten/Preview, UI-Skalierung,
Fenstergeometrie, Lösung und Reveal bleiben außerhalb der Datei.

Vor Anwendung erfolgt vollständige Parse- und Vertragsprüfung. Jede History-Aktion
wird ab unbekanntem Raster bis einschließlich Redo-Zweig widerspruchsfrei replayt;
am Cursor muss die gespeicherte Matrix exakt passen. Abschluss wird anhand der
aktuellen Definition neu geprüft. Der Restore leitet aktuelle Hinweis-Slot-Offets
aus semantischen Ankern/Tokenbereichen ab und begrenzt den Rasterfokus an der
aktuellen Fenstergeometrie.

Schreiben: Temp im selben Root, Flush/Schließen, erneute Parse-/Vollvalidierung,
nur gültiges bisheriges Primary als Backup rotieren, dann Temp als Primary einsetzen.
Ein unterbrochener Ersatz lässt mindestens eine gültige ältere Fassung ladbar.
Verwaiste Temps sind nicht autoritativ. Ein beschädigtes Primary wird bei gültigem
Backup sichtbar aus dem Backup gelesen, aber nicht über dieses Backup rotiert.
Erst eine bestätigte Backupübernahme ersetzt die beschädigte oder fehlende Primärdatei;
normales Autosave bleibt in beiden Fällen gesperrt. Ohne
gültige Fassung bleibt der Slot im sichtbaren Fehlerzustand, bis sein Reset
bestätigt wird. Gültiges Primary mit beschädigtem Backup bleibt lesbar;
eine bestätigte Backup-Erneuerung erlaubt wieder Speichern. Ein Reset greift
nur auf Dateien des ausgewählten Slots zu.

Ein verpflichtender Flush liefert Erfolg oder Fehler an Album-, Blattwechsel-,
Beenden- und Window-Close-Pfade. Bei Schreibfehler bleibt die aktuelle Ansicht samt
ungesichertem Zustand und sichtbarer Fehlermeldung bestehen. Ein erfolgreicher Retry
ermöglicht den Übergang. Nach einem `after_rotation`-Abbruch bleibt das gültige Backup
bis zur bestätigten Übernahme unverändert; die Reparatur ist auch aus der Arbeitsansicht
erreichbar. Temporäre Subslotpositionen, Hoverbänder und Strichzähler werden nie
Teil von Schema 1.

## Nacharbeit D-23 bis D-27

Die angefasste Hinweisfolge folgt während eines Drags kontinuierlich ihrer Achse.
Nur beim Loslassen wird der nächste gültige gemeinsame Slot als semantische
Leseposition bestätigt; Escape, Fokusverlust und reguläre Übergänge rollen den
visuellen Versatz zurück. Der kleinere Füll-Inset vergrößert bestätigte und
vorläufige Farbflächen, während der Zwischenraum an normalen und kräftigen
Fünferlinien erhalten bleibt. Cursorzeile und -spalte erhalten gleich starke
Hintergrundbänder, deren Kreuzung nicht doppelt gezeichnet wird. X- und Preview-X-
Segmente werden bei angeschnittenen Zellen am Rasterviewport geometrisch geclippt.
Der Live-Zähler zeigt bei linken und rechten Zellgesten die gesamte aktuelle
geometrische Länge einschließlich Start, Ende, Sprüngen und vorbesetzten Zellen.

## Automatisierte Prüfungen

Die Godot-Suite ergänzt die P1.2-Regressionen um leere und verzweigte Stände aller
drei Fixtures, Wiederherstellung/Redo mit bleibendem `undo_used`, Schema-/Definitions-
und Revisionskonflikte, Matrix-/Palette-/History-/Cursor-/Abschluss-/Viewfehler,
korruptes JSON, Backuprotation und sichtbare Recovery, Temp- und Ersatzabbruch,
bewusste Backupübernahme und isolierten Einzelreset. Die bestehende Maus-,
Miniatur-, Hinweis-, Zoom-, Abschluss- und Renderprüfung bleibt erhalten.

`tests/p13_roundtrip.gd` wird im Produkt-Harness als zwei getrennte Godot-Prozesse
mit demselben **eigenen temporären** `P1_TEST_SAVE_ROOT` ausgeführt: A bearbeitet
alle drei Blätter mit unterschiedlichen Zell-/Viewzuständen; F-03 erhält zusätzlich
History/Redo, View/Werkzeug/Farbe und individuelle Hinweise. Prozess A
beginnt eine unbestätigte Vorschau und beendet regulär; B startet neu, liest den
Slot und prüft Zellen, ungespeicherte Vorschau, Redo/`undo_used`, View und die
unabhängige Wiederaufnahme der anderen Slots sowie deren spoilerfreie
Albumminiaturen. Test- und Render-Skripte setzen ebenfalls
eigene temporäre Speicherroots. Der Produkt-Harness nutzt zudem eine temporäre
Projektkopie mit isoliertem Godot-Profil; das Windows-ZIP enthält keine Saves.

Historischer Windows-Zwischenlauf des Ausgangsheads `1a5756f…`: Godot 4.7.2,
1038 Prüfungen erfolgreich;
isolierter Zwei-Prozess-Roundtrip mit beiden Erfolgsmarkern erfolgreich.
Der vollständige lokale Produktweg umfasste Import, erwarteten Negativtest
mit Exit 23, kontrollierten Start, 249 Render-PNGs, Windows-Export sowie
exportierten Headless- und OpenGL-Start. Dieser Lauf prüfte einen veränderten
Arbeitsbaum und ist deshalb kein commitgebundener Abschlussnachweis der Nacharbeit.

Die neuen Godot-Fälle injizieren Schreibfehler vor Album, Fixturewechsel,
Beenden und WM-Close, prüfen Retry und den Wiederanlauf mit fehlendem Primary
nach `after_rotation`. Eingabetests prüfen Subslot-Drag ohne Save, durchgehende
Bewegung über Slotgrenzen hinweg, Drop-Snap,
Abbruch, geometrischen Zähler, Hoverzustand und X-Segment-Clipping. Echte
OpenGL-SubViewport-Bilder und Pixelproben decken die größere Füllfläche samt
Trennung über alle Farben und Arbeitszoomstufen, dezente Bänder, Hintdrag,
Live-Zähler sowie bestätigte und vorläufige X an vier Rändern und einer Ecke
bei 24/36 Zellabstand ab. Der lokale Windows-Nacharbeitslauf auf verändertem
Arbeitsbaum erreichte 1089/0 Godot-Prüfungen, 277 echte Renderbilder und 530
Pixelchecks. Ein gesonderter isolierter Zwei-Prozess-Lauf meldete
`P1_ROUNDTRIP_WRITE_OK` und `P1_ROUNDTRIP_READ_OK`. Die commitgebundenen
Abschlussnachweise stehen nach den aktuellen CI-Läufen im Draft-PR.
Die CI führt zusätzlich Import, denselben Godot-Test, den erwarteten Negativpfad
mit Exit 23, kontrollierten Start, echte Renderbilder/Pixelchecks, Windows-Export,
Python-Dokumenttests und Preflight am finalen Head aus. Laufkennungen/Artefakthashes
stehen im Draft-PR und sind erst nach dessen erfolgreichem Lauf Nachweise.

## Selbstreview und offene Abnahme

Der getrennte Selbstreview prüft den vollständigen Diff gegen S-01 bis S-07,
insbesondere Dateigrenze, Schreibreihenfolge und Wiederanlauf, Slotisolation,
Spoilerfreiheit, unveränderte Fixture-/Proof-/Artworkdaten und Artefaktinhalt.
Er ist keine unabhängige Zweitprüfung; der konkrete Head und Befunde stehen im PR.

**M-04 offen beim Eigentümer vor Gesamt-P1-Merge:** Am commitgebundenen Windows-ZIP
ein Blatt bearbeiten, Undo/Redo-Zweig und Raster-/Hinweisansicht setzen, per
Beenden/Alt-F4 schließen, die Anwendung als echten neuen Prozess starten und
Fortsetzung prüfen. Zusätzlich Recovery-Meldung und bestätigten Einzelreset mit
isolierten Testdaten prüfen. Head/Artefakt, Windows-Version, Bildschirm-/Clientfläche,
Anzeigeskalierung, Maus und Einzelergebnisse dokumentieren. M-01/M-02/M-03/M-06,
#12/M-07 und die übrige P1-Gesamtabnahme bleiben separat offen.
