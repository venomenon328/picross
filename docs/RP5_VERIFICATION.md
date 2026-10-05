# RP-5: Reparatursuche und Prüfzuordnung

Stand: 05.10.2026 · Arbeitsfassung 0.1 · Umsetzung; unabhängiges Review offen

Auftrag [#39](https://github.com/venomenon328/picross/issues/39),
[Fachvertrag](PUZZLE_PRODUCTION.md), [Paket und vorab gebundene Parameter](../examples/rp5/README.md).
Basis `80ae2c19eb6f85bbac58a247badf65b3e0669132`, Branch
`feat/39-motif-repair-search`, eigener Draft-PR gegen `main`.
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

Aktuelle Messwerte und Sichtbefunde werden nach dem Lauf ergänzt. Das separate
unabhängige technische und visuelle Review am finalen Head bleibt vor Merge
erforderlich. Selbstreview ist keine unabhängige Zweitprüfung. Reale Eigentümer-
Lösung und finale Pilotabnahme sind RP-6-Gates.
