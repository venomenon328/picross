# Warnemünde r04 · Symmetrisches Raster

**30×40, vier Farben.** Leuchtturm maximal **9 Zellen**, Schaft **5 Zellen** breit;
Spiegelachse **Spalte 6**. Tür, vier Schaftfenster und Spitze liegen genau mittig.
Teepott **19 Zellen** breit, Spiegelachse **Spalte 20**: Dach und Fassade gespiegelt.
Prüfung aller Zellwerte innerhalb beider Gebäude: **0 Symmetrieabweichungen**.

[Vorher/Nachher](comparison.png) · [Rasteransicht](raster.png) ·
[Abschlussbildvergleich](reveal-comparison.png) · [Zell-Diff](cell-diff.png) ·
[Paket](package.zip) · [Record](record.json).

260 Positionen wurden ausdrücklich manuell neu gezeichnet. Himmel, Sonne und
übriger Vordergrund sind unverändert. Farben und Gesamtgröße bleiben erhalten.
Dunkle Konturen, Türen und Fenster sind jetzt klarer. Zwei gezielte Zeichenstände,
keine Reparatursuche. Alter Stand r03 bleibt unverändert im Repository erhalten.

**Vollständig deduktiv lösbar und eindeutig:** full-line-color-v1, 102 Proofschritte,
neuer unabhängiger Proofcheck in frischem Prozess und neue Herkunftsrekonstruktion
bestanden. Symmetrie wurde dem Löser nicht als Annahme gegeben. Hinweise,
Endmatrixgleichheit, Randregel und Maße geprüft. 915 gefüllt/285 leer (76,25%).
Schwierigkeit vorläufig L2, Bereich L1–L4, Vertrauen niedrig; keine definierte
Engstelle. Lösungszeit/Menschenminuten nicht erfasst; Probespiel optional.

**Status raster_review: neue Geometriefreigabe offen.** Die alte Motivfreigabe
gilt für MA-r01; sie wird nicht auf die manuelle Neuzeichnung MR-r03 übertragen.
PUZZLE_AUTHORING §4.4 verlangt bei materieller Motivänderung eine erneute
ausdrückliche Motivfreigabe. Der aktuelle Korrekturauftrag erlaubt die Änderungen,
ist keine vorweggenommene Freigabe des jetzt vorgelegten Ergebnisses.
Nächster Schritt: diese konkrete MR-r03/r04-Geometrie freigeben; anschließend
content_ready-Paket mit dieser Freigabe und gebundenen Prüfbelegen.
Keine Runtimeintegration oder Merge, kein ZA-1-Pass behauptet.

| Bindung | SHA-256 |
| --- | --- |
| Paket (5808148 Bytes) | `83ab39d189a8b9f24f62456fc7c918a678e738b29b0c682321ddebd3ad7fb5e7` |
| Inventar | `1e3718a9eb373956c324c45b5ccf0d3ce988c10b495a423db342203ee2a5de48` |
| Handoff | `e3f25e5e0f9093d018f845176b545c2083e4682af31dd334b56a37e85c10178b` |
| Neue Motiv-/Rasterdatei MR-r03 | `386bf8a223c5e2f6f3fa8bb6954151d8dc8caa5500fbff604e596eff4b9ec1b1` |
| Matrix (kanonisch) | `b93ee63dc591041c1252d67a0d083700ff7e312261e31fbcf62ae00474915eda` |

Im ZIP liegen beide vollständigen neuen RP3-Bündel, die gebundene frühere
RP3-/RP5-Referenzkette, gespeicherter Zeichenplan, sämtliche festen Edits,
Herkunfts-/Symmetrie-/Logikprüfungen, Qualitäts-/Schwierigkeitsbericht und
Freigabebelege. Kein altes ZIP eingebettet. Toolcommit `f26a3740d2902ddfe50fea1ccd14cb976e7d64da`.
