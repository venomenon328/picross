# P1.1: Prüfbericht und Übergabegrenze

Historischer Nachweis des unten genannten Heads. Aktueller integrierter Prüf- und
Abnahmestand: [P1.4-Ergebnisbericht](P1_4_VERIFICATION.md).

Stand: 23.09.2026 · [Issue #8](https://github.com/venomenon328/picross/issues/8) · erster Zwischenstand von [P1 / #5](https://github.com/venomenon328/picross/issues/5)

## Technischer P1.1-Nachweis

Implementierungshead `64dcca4df9ed00cecedfdb8cabba09bcb7179ae8`, Arbeitsbranch `feat/5-p1-prototype`, Zielbasis `main@7f5f945edecdad0c5b86ecbe66ab3d81c7bfedac`, Draft-PR #14. Der damalige Auftrag umfasste #8, Tests und Draft-PR, keinen Merge. Nachfolgende Dokumentänderungen und Anforderungen für #9 sind kein neuer Implementierungsnachweis.

| Kriterium | Nachweis am genannten P1.1-Stand |
| --- | --- |
| K-01 | Eigener F-01-Datensatz mit ID/Revision, validierten Hinweisen und damals pixelgleicher Kolorierung. [Herkunft/Zertifikat](../prototypes/p1/F01_PROOF.md): 48 Linienschlüsse bestimmen alle 400 Zellen ohne Startfelder/Raten; Manipulationstests vorhanden. |
| K-02 | Achsenbindung, diagonaler Gleichstand, Sprünge, 5→12→9, Rückwärtskreuzen, Vorbelegungsschutz, Rand/UI, eingefrorenes Werkzeug/Farbe, Escape/Fokusverlust/Albumwechsel und No-op. Vorschau ändert keinen bestätigten Zustand. |
| K-03 | Exakte Vor-/Nachwerte atomarer Striche; Undo/Redo, gemischte Radieraktionen, Verzweigung, No-op und bleibendes Undo-Metadatum ohne Wertung. |
| K-04 | Miniatur nur aus Spielerdaten; keine Korrektur falscher Eingaben oder Enthüllung durch Vorschau. Abschlussfälle und Szenenwechsel bis zum Albumeintrag geprüft. |
| K-05 | 116 Godot-Prüfungen und 38 Python-Tests in Linux-CI, Dokument-/Diffprüfung, Negativpfad Exit 23, Import, kontrollierter Start und Windows-Export. |
| K-06 | Reale Nutzerprobe mit Feedback erfolgt; vier Folgepunkte für #9. Keine pauschale positive Einzel- oder Gesamt-Abnahme; siehe unten. |

CI-Test-Merge `a5b33540de307c79595b6a62c6f7182d307ea92a`. Erfolgreiche Läufe: Produkt `35784355355`, Setup `35784355144`, Preflight `35784355186`. Windows-Artefakt `10719712143`, inneres ZIP SHA-256 `9c5a0c998375144b53a36e9a8b2b672a5f954b236ebe535a8bad10367d7909dc`. Der konkrete [Review R1](https://github.com/venomenon328/picross/pull/14#pullrequestreview-5284205520) dokumentiert Umfang und Grenzen der Prüfung; er gilt für den genannten Codehead und damaligen Vertrag.

Der Implementierer berichtete erfolgreiche lokale Windows-Entwicklungsläufe und kontrollierte Starts des exportierten Artefakts headless/mit OpenGL. Renderbilder von Album, Arbeitsansicht und Abschluss wurden bei 1280×720 kontrolliert; ein Überlauf wurde vor dem Lieferhead korrigiert und getestet. Diese technischen Prüfungen ersetzen keine Eigentümerprobe oder echte DPI-/Maussignalabnahme.

## Eigentümerprobe und vier Folgepunkte

Nach Review R1 meldete der Nutzer Erfahrungen aus der angebotenen Spielprobe und lieferte zwei Screenshots: Abschlussansicht von F-01 sowie einen Rasterausschnitt mit optisch verschmolzenen Füllungen an kräftigen Fünferlinien. Bezug im Gespräch ist das oben bereitgestellte P1.1-Artefakt. Die Versionskennung des tatsächlich gestarteten Nutzerprogramms wurde nicht separat gezeigt; reale Fenstermaße/Windows-Skalierung und Einzelbestätigungen aller K-06-Szenarien wurden nicht vollständig genannt.

| Rückmeldung | Übernahme in #9 / P1 0.4 | Stand |
| --- | --- | --- |
| Fenster zu klein; 1080p/1440p ohne übergroßes Raster nutzen | D-07: größerer Start, getrennte Fenster-/UI-/Raster-Skalierung | Spezifiziert, nicht implementiert |
| Dunkle Füllung und dicke Fünferlinien verschmelzen | D-08: erkennbare Zelltrennung über Farben/Arbeitszoom/Vorschau | Spezifiziert, nicht behoben |
| Normales Werkzeug soll gesetzte Felder neutralisieren | D-09: links Füllungen, rechts Leermarkierungen zurücknehmen; Modus pro Strich einfrieren | Neue Bedienregel, noch nicht implementiert |
| Ergebnisbild darf detaillierter als das Raster sein | D-10: motivtreue Verfeinerung statt erzwungener identischer Pixelmaske | Präzisiert, noch nicht implementiert |

Die Probe ist **durchgeführt mit Änderungsbedarf**, nicht „alles bestanden“. Das sichtbare Abschlussbild bestätigt nicht automatisch jede Abbruch-/Undo-/Randprüfung. Aus Screenshotgrößen wird keine Windows-Skalierung abgeleitet. Auch die bereits global erlaubte Motivverfeinerung ist keine Zusicherung eines schon gelieferten detaillierten Bilds.

Der anschließende Nutzerauftrag lautet, diese Punkte einzuarbeiten und #9 vorzubereiten. Die frühe Feedbackschleife hat damit stattgefunden; es wird nicht erneut auf eine noch gar nicht erfolgte Rückmeldung gewartet. Die offenen Einzel-/Metadaten werden mit der erneuten Maus-/Layoutprobe am #9-Artefakt erfasst. Kein vollständiges M-01/M-06- oder Gesamt-P1-Abnahmeurteil daraus ableiten.

## Grenzen der nächsten Lieferung

#9 übernahm die vier damaligen Punkte und ergänzte F-02/F-03, Zoom/Pan und interaktive
Miniatur. Sie wurden zunächst in P1 0.4 festgehalten. Die aktuelle
[P1-Spezifikation 0.6](PROTOTYPE_P1.md) ergänzt D-11 bis D-17 und löst widersprechende
alte D-09-/Hinweisregeln ab. Dieser historische P1.1-Bericht beweist weder die
damaligen noch die späteren Änderungen oder deren Lesbarkeit.

Persistenz/Recovery, 500-Aktionen-Gesamtintegration und abschließende P1-Abnahme bleiben #11/#12. Spielstände existieren weiterhin nur in der Sitzung. Keine finale Themenwahl, Wertung, Live-Fehlerhilfe, Merge- oder Releasefähigkeit behaupten. Der gemeinsame PR bleibt Draft.
