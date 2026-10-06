# RP-5: Reparatursuche und Prüfzuordnung

Stand: 06.10.2026 · RP-5 nach unabhängigem Review R1 über PR #46 als
`cd4a8db86e51891f13e305b589837a1a4354c5a2` integriert. Keine offenen B-/A-/O-Befunde.
Die folgenden Entwicklungsnachweise behalten ihre ursprüngliche Bindung.

Auftrag [#39](https://github.com/venomenon328/picross/issues/39),
[Fachvertrag](PUZZLE_PRODUCTION.md), [Paket und vorab gebundene Parameter](../examples/rp5/README.md).
Basis `80ae2c19eb6f85bbac58a247badf65b3e0669132`, Branch
`feat/39-motif-repair-search`, damaliger Arbeits-PR gegen `main`.
Parent #34 bleibt offen; kein Merge oder Release.

Die Vorabfestlegung enthält alle neun Referenzen und gesichtete harte Masken,
einschließlich empfindlicher Leerstellen. Der erste Implementierungscommit
bindet diese Dateien vor dem ersten Vergleichslauf. Baseline, Sichturteile und
Provenienz von RP-4 werden nicht umgeschrieben. Das Originalpaket ist nach R2 in
PR #45 als `80ae2c1` integriert; historische offene Reviewfelder bleiben erhalten.

| Kriterium | Prüfweg |
| --- | --- |
| RP5-A01 | `test_repair.py`: Farb-/Leerzellen, falsche Masken/Referenzen, Schutz vor Bewertung und rekonstruierter Ausgabe. |
| RP5-A02 | Referenzabstand bei Mehrfachumfärbung/Rücknahme; kumulative Vorschlags-/Kandidaten-/Linienbudgets, Zeit/Abbruch in Suche und Abschlussprüfung. |
| RP5-A03 | Echter 2×2-Dateiimport bleibt zunächst Fixpunkt, ein zulässiger Zelloperator löst Mono/Farbe; frischer geschriebener Endproof, unabhängiger Replay, Nichtfund und Abbruch. Kein Katalogmotiv aus dieser Funktionsfixture. |
| RP5-A04 | Gleiche Eingaben/Seed/Folge binden gleiche Reparatur-ID und Proofbytes. Rehashte Eltern-/Score-/Folgen-/Hinweis-/Proof-/Bildangriffe scheitern. Späteres Replay eines Abbruchs verleiht keine Freigabe. P1 weist Reparaturmanifest ausdrücklich zurück. |
| RP5-A05 | Genau neun vorab bestimmte Reparaturen; vollständiger Vergleich mit 48 unveränderten RP-4-Resultaten. Aufwand, Motivänderung und Ausbeute getrennt; menschliche Zeit unbekannt. |
| RP5-A06 | Tatsächlich geöffnete Vorher-/Nachher-/Änderungs-/Maskenbilder, dateigebundene Einzelurteile; Fach-/Replay-/Dokument-/Diffprüfung und aktuelle CI im PR. |

## Beobachteter Lauf und Sichtbefund

Vorabcommit `55f9e0f143bc79a4d5ff81d83d1c901b90f1797c`, bytegleich veröffentlichter
Tree `ed7c30cd4b6e0ad9f9c463f3fdc6fba9c250314e`; keine nachträgliche Parameterlockerung.
Neun vollständige Erstläufe: zwei neue Zertifikate, sechs ausgeschöpfte
Suchbudgets, ein Zeitabbruch. 113 begonnene Kandidatenbewertungen, 275 Vorschläge,
82,799 s kumulative Suchzeit einschließlich Referenzrekonstruktion und Prüfung;
separate Endprüfung und Gesamtdauer in den Originalresultaten. Windows,
Python 3.12.10 und Pillow 12.3.0; keine Linux-RSS-Messung für diesen Lauf behauptet.

Tulpe und Eule 40×40 werden mit je zwei Zelländerungen vollständig nachgewiesen.
Die eigene Sichtprüfung erhält Hauptform und empfindliche Details. Segelboot,
große Eule und stilisierte Astronautin erreichen bessere logische Teilstände,
aber zeigen neue Rand-/Hintergrundartefakte und werden als motivisch verschlechtert
ausgewiesen. Die übrigen gewählten Ausgaben bleiben unverändert. Alle neun
Vorher-/Nachher-/Änderungs-/Maskenansichten und sechs ursprünglichen RP-4-
Kontaktansichten wurden tatsächlich geöffnet. Hashgebundene Einzelbegründungen,
vollständige 48er-Übersicht und Grenzen stehen im [Paket](../examples/rp5/README.md).

321 Originaldateien sind im ZIP byteidentisch erhalten, einschließlich aller
113 Bewertungsproofs, zwei Endproofs und des beobachteten Abbruchs. Die
originale Ausbeute 19/29/14 und unbekannte menschliche Zeit bleiben unverändert.
Zwei zusätzliche motivisch geeignete Zertifikate bedeuten potentielle 21/16
Varianten, keine 16 unabhängigen Katalogrätsel oder Pilotfreigabe. Drei logisch
bessere, visuell verschlechterte Teilstände begrenzen den Nutzen dieser Suche.
Keine neuen Modellaufrufe, keine manuellen Rasterkorrekturen, keine beobachtete
menschliche Nacharbeitszeit und keine Produktivitätsquote.

Gezielte Entwicklung: 19 Reparaturtests plus drei Paket-/Archivtests bestanden;
unabhängiger vollständiger Paketreplay erfolgreich in 57,515 s am veränderten
Arbeitsbaum. Dies sind Entwicklungsbelege. Die aktuelle abschließende CI-/Head-/
Basis-/Test-Merge-/Artefaktbindung steht in [integriertem PR #46](https://github.com/venomenon328/picross/pull/46).
Der gemeinsame Fachjob führt sämtliche bisherigen und neuen Fachtests, sechs
Referenzen, RP-3-Demo und vollständigen RP-4-Replay aus. Ein zusätzlicher
`rp5-repair`-Job prüft alle Kandidaten-/Eltern-/Nachweis-/Vergleichsbindungen mit
300 s kooperativem Replaybudget, 60 s / 1000000 Linien pro Bundle und sechs
Minuten hartem Schrittlimit; Job insgesamt zehn Minuten. Archivgrenzen und
Extraktions-Negativtests sind dokumentiert. Windowsregression und
`docs`-/`product`-/`preflight`-Workflows bleiben unverändert aktiv.

## Abnahmestand

Das unabhängige technische und visuelle Review R1 am Head
`df77c0c1e76d150880570473e1225458a4924eca` ist in PR #46 abgeschlossen.
Selbstreview bleibt davon getrennt. Reale Eigentümer-
Lösung und finale Pilotabnahme sind RP-6-Gates.
