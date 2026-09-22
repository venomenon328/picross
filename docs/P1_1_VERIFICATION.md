# P1.1: Prüfbericht und Übergabegrenze

Stand: 22.09.2026 · [Issue #8](https://github.com/venomenon328/picross/issues/8) · erster Zwischenstand von [P1 / #5](https://github.com/venomenon328/picross/issues/5)

Arbeitsbranch `feat/5-p1-prototype`, Ziel `main`, geprüfte Startbasis
`7f5f945edecdad0c5b86ecbe66ab3d81c7bfedac`. Keine fremden Änderungen beim Start;
kein vorheriger P1-Branch oder offener PR. Der Auftrag umfasst #8 und Draft-PR,
keinen Merge und keine Ausführung späterer Pakete.

## Technischer Nachweisumfang

| Kriterium | Implementierung und überprüfbarer Nachweis |
| --- | --- |
| K-01 | Eigener F-01-Datensatz mit ID/Revision, vollständigen validierten Hinweisen und motivtreuer Kolorierung. [Herkunft und Zertifikat](../prototypes/p1/F01_PROOF.md): 48 Linienschlüsse bestimmen 400 Zellen ohne Startfelder/Raten. Godot prüft Datenfehler, Leer-/Volllinien, gleiche und angrenzende verschiedene Farben; Python prüft die endliche Deduktionsfolge einschließlich manipulierter Nachweise. |
| K-02 | Getrennte Gestenlogik: Achsenbindung, diagonaler Gleichstand, Eingabesprung, 5→12→9, Rückwärtskreuzen des Starts, Vorbelegungsschutz, Rand, eingefrorenes Werkzeug/Farbe, Escape/Fokusverlust/Albumwechsel und No-op. Bestätigter Zustand bleibt während der Vorschau unverändert. Szenentests prüfen dieselben Adapter und Abbruchsignale wie die Oberfläche. |
| K-03 | Exakte Vor-/Nachwerte pro atomarem Strich; Undo/Redo, Radieren gemischter Vorzustände, Verzweigung, No-op-Erhalt des Redo-Zweigs und dauerhaftes Undo-Metadatum. Keine Wertung. |
| K-04 | Miniaturkomponente erhält nur Spielerdaten. Falsche Eingaben werden nicht korrigiert. Abschluss mit unbekanntem/leerem Hintergrund, negative Zusatz-/Fehl-/Falschfarben-/Leermotivfälle, keine Enthüllung durch Vorschau. Szenenwechsel bis zum kolorierten Albumeintrag werden automatisiert geprüft. |
| K-05 | [Produkt-Harness](../tools/p1_product.py): offizielle P1.0-Archive vollständig hashen, isoliert importieren/testen, erwarteten Exit 23 nachweisen, Hauptszene kontrolliert starten/beenden, Windows-x86_64 exportieren und auf Windows den Export starten. [Produkt-CI](../.github/workflows/p1-product.yml), Setup-Tests und vollständiger Diffcheck ergänzen sich. Aktuelle commitgebundene Läufe und Artefaktkennungen im Draft-PR. |
| K-06 | **Offen.** Reale Mausprobe durch Eigentümer am gelieferten Windows-Artefakt, mit tatsächlicher Skalierung und Ergebnis. Vor #9 durchführen oder ausdrücklich überspringen. Kein Tastatur-/Controllergate. |

## Ausführung und Grenzen

Die [Anleitung](../prototypes/p1/README.md) nennt reproduzierbare Befehle und
K-06-Szenarien. Die lokalen Windows-Entwicklungsläufe haben Import, Godot-Tests,
absichtlichen Negativtest, kontrollierten Quellstart, Export und exportierten
Headless-Start erfolgreich ausgeführt. Das isolierte Produkt-Harness schreibt
Phasenlogs und `product-report.json`; finaler Head und CI-Läufe werden nach dem
Push im PR gebunden, statt hier einen selbstreferenziellen Commit zu behaupten.

Die Renderprüfung mit `tests/capture.gd` nutzt eine echte OpenGL-Ausgabe und
isolierte Profilpfade. Album, Arbeitsansicht und Abschluss wurden bei 1280×720
visuell kontrolliert. Ein gefundener vertikaler Überlauf wurde korrigiert und
durch Szenenprüfungen abgesichert. Dies ist eine technische Layoutkontrolle,
keine Eigentümerprobe und kein Beleg für physische Maussignale oder eine
bestimmte Windows-Anzeigeskalierung.

Bei der Übergabe wird ein gesonderter Selbstreview gegen den gesamten Diff und
K-01 bis K-05 vorgenommen. Er ist keine unabhängige Zweitprüfung. Der Draft-PR
enthält dessen aktuellen Stand, technische Resultate, Quellhead/Test-Merge und
Artefaktkennung. Offene K-06-/Gesamt-P1-Gates bleiben dort ausdrücklich sichtbar.

## Noch nicht geliefert

F-02/F-03, Zoom/Pan, interaktive Miniatur, dauerhafte Speicherung und Recovery,
500-Aktionen-Integration sowie die übrigen P1-Maus-/Layout-/Performanceabnahmen
gehören zu den späteren beauftragbaren Paketen #9, #11 und #12. Spielstände
existieren in P1.1 nur innerhalb der laufenden Sitzung. Keine finale Themenwahl,
Wertung, Live-Fehlerhilfe, Release- oder Mergefähigkeit behaupten.
