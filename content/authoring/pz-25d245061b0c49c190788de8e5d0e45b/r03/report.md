# Kolibri · Endabnahmevorlage r03

17.10.2026 · pz-25d245061b0c49c190788de8e5d0e45b · content_ready · Authoring 0.5.0/Revision 14.
Toolcommit: f5f18819604167c8640c02d488ae95d3c646bb3f. Inventar-SHA-256: `206b85192e70003d1893a5b4b7d75622a8263871a93ef9ae5262608a5beb2440`.
Paket-SHA-256: `1929216402c352c22e2853dff487b60bce6f71e65a856b1ded68029f31827b08`.

Auswahl **paired/area-80**, 40 × 30 = 1200 Zellen, Mono, eine gewünschte und
tatsächlich verwendete Farbe ink (#202020); 359 gefüllt, 841 leer (29,92 %).
Echte Bilder: Raster (`preview/final-large.png` im ZIP), Gitter (`preview/final-grid.png` im ZIP),
Abschlussbild (`reveal/A-r01.png` im ZIP), Variantenvergleich (`preview/comparison.png` im ZIP).
Bildfreigabe A-r01 (`approvals/reveal.json` im ZIP), Motivfreigabe MA-r01 (`approvals/motif.json` im ZIP)
samt genauem Parameterkorridor belegt. Redaktionelle Endabnahme ausdrücklich offen.

Vier Startkandidaten verlieren das Auge. Zusatzschwelle64 verliert den Schnabel;
80 erhält Auge, lange Schnabelform und wichtige Zwischenräume. Schwanzspitzen
sind grob gestuft, das Auge ist eine Leerzelle; Gefieder/Füße/Farben entfallen.
Visuelle Kriterien (`visual-review.json` im ZIP) erfüllt. Rechte Leerlinien bleiben wegen
des festen Formats; keine isolierten Füllzellen oder leeren Innenzeilen.
Keine Zellkorrektur; Reparaturdiff 0. Geeigneter zertifizierter Kandidat macht
Reparaturrunden entbehrlich (Entscheidungen (`decisions.json` im ZIP)).

Technische Prüfung (`candidate-audit.json` im ZIP): sechs verschiedene Matrizen,
Produktmaße und tatsächliche Farbzahl gültig; Hinweise separat durch Runextraktion
bestätigt. Rand: links/oben belegt, rechts/unten leer; Formel erfüllt.
Quelle→Normalisierung→Matrix→Hinweise werden bei ZIP-Inspektion frisch rekonstruiert.
Unabhängiger frischer Prüferprozess (`verification.json` im ZIP): full-line-mono stalled
mit 785 offenen Zellen; paired-lines-mono solved, 211 Schritte; Endmatrix exakt gleich.
Vollständige Deduktion belegt zugleich Eindeutigkeit, keine Suchdiagnose nötig.

Schwierigkeit (`difficulty.json` im ZIP): **L5**, Bereich L5–L5, Methode 0.2 instrumented,
Vertrauen medium; R4-Notwendigkeit aus Baseline-/Paarvergleich belegt.
Keine R0–R3-Klassifikation oder menschliche Kalibrierung behauptet.
Bearbeitungsumfang 1200 Zellen; Lösungszeit nicht geschätzt, aktive Menschenzeit
nicht erfasst. Probespiel nicht durchgeführt, optional. Drei Importaufrufe,
sechs Matrizen, ein unveränderter Profilvergleich; keine neuen Bildaufrufe.

Nutzungsgrundlage: originale beauftragte KI-Illustration ohne fremde Bildreferenz;
Herkunft (`motif/MA-r01.provenance.json` im ZIP) und Prompts erhalten.
ZA-1-ZIP-Inspektion [inspection.json](inspection.json): technical=true,
Baseline/Paarproof und Herkunft frisch geprüft, einziger Blocker fehlende Endabnahme; Ziel-/Spielerexport und Registrierung
nicht ausgeführt, benötigen Endabnahme. Keine Spiel-/Render-/PCK-Tests bei reiner
Inhaltsablage erforderlich. Nächster Schritt: **4 · Abnehmen & ins Spiel integrieren**.

Alle übrigen relativen Beleg-/Bildpfade dieses Berichts bezeichnen Dateien innerhalb
von [package.zip](package.zip). [Record](record.json), [Handoff](handoff.json).
