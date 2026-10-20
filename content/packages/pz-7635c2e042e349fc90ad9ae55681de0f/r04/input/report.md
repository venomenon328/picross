# Seepferdchen · Endabnahmevorlage r04

20.10.2026 · pz-7635c2e042e349fc90ad9ae55681de0f · `content_ready`.
Authoring 0.5.0/Dok.22, Toolcommit d8b3ccb8eb4b66982dea805c08c3b8ab6f095b8d.
Zyklusfreie Inventar-/ZIP-/Handoffhashes stehen im äußeren record.json neben dem ZIP.

**Vorlage:** [echtes Endraster und B-r01](qa/final-reveal-comparison.png),
[Zellauflösung](qa/final-raster.png), [Großansicht](qa/final-raster-large.png),
[Reparaturdiff](qa/repair-diff.png). B-r01 und MA-r01 bytegleich übernommen;
tatsächliche [Bildfreigabe](reveal-approval.json) und
[Motiv-/Parameterfreigabe](motif-approval-14x27.json) gebunden. Endabnahme offen.

**Auswahl:** 14×27, 378 Zellen, Mono genau 1 verwendete Vordergrundfarbe ink
(#202020), 164 gefüllt/214 leer; Leer zählt nicht. Vier [Direktkandidaten](qa/candidate-comparison.png)
verglichen. Die drei anderen verlieren das geschützte Auge, auch bei gelöster Logik.
14×27/160 erhält Auge und offenen Schwanz, endet unverändert auch im Paarprofil
mit vier offenen Schnauzenzellen. [Runde 1](repair-plan-r01.json) findet nach einem
Vorschlag (+1 Zelle, Z6/S11) eine vollständig zertifizierte lokale Verstärkung;
zweite Runde entfällt wegen Erfolg. Keine materielle Motivänderung.

**Pflichtprüfung bestanden:** Produktmaße; Farbzahl; Rand links/oben/unten belegt;
Quelle/Normalisierung/Matrix/Hinweise rekonstruiert; sämtliche gebundenen Dateien
geprüft. [Frischer Reparatur-Replay](qa/repair-replay.json),
[unabhängige finale Baseline-/Paarprüfung](qa/final-assessment-check.json): beide
`solved`, 110 Schritte, exakte Endmatrix, unbekannter Start, kein Raten.
Finales Paarprofil benötigt keine Paarschritte, R4=false; Eindeutigkeit folgt aus
vollständiger Deduktion. Keine zusätzliche Suchdiagnose nötig.

**Gestaltung:** [Einzelkriterien](visual-review.json) erfüllt. Auge, Halsfreiraum,
Flosse, Bauch und offener Greifschwanz bleiben. Keine isolierten Füllzellen oder
leeren Innenlinien. Rechte äußere Spalte 14 aus contain bewusst leer; Randregel
ohne Ausnahme erfüllt. [Statische Papierprobe](qa/reveal-paper-check.png) zeigt
transparente Außen-/C-Flächen und erhaltene helle Details; kein nativer Spieltest.

**Schwierigkeit:** [geprüftes 0.3](difficulty-checked.json) **L3 – Mittel**, logische
Basis 3 + Größe 0; R2, 24 Wellen (8 R0/9 R1/7 R2), keine definierte Engstelle.
Instrumentiert/medium, Methodenpunktbereich L3–L3; keine menschliche Kalibrierung
oder Zeitschätzung. Umfang separat 378 Zellen. [0.2-Produktionsangabe](difficulty.json)
bleibt als begrenzte L3-Schätzung/low, Bereich L2–L4, für ZA-1 separat erhalten.

**Grenze:** Eigenständig erzeugtes Artwork im Nutzerauftrag; Nutzungsgrundlage,
native Prompts und Herkunft erhalten. In dieser Phase keine Bildgenerierung,
3 Importaufrufe, 1 Reparatursuche, 1 vollständige SD-Analyse. Aktive Menschenzeit
nicht erfasst; Probespiel optional/nicht durchgeführt. ZIP-Inspektion folgt nach
Schreiben, Export/Registrierung warten auf menschliche Endabnahme. Auftrag 4 bindet
die tatsächliche Erklärung an Handoff, Inventar, Endkandidat und B-r01; erst danach
exportieren, 0.3 an die echten Definitionsbytes rebind, registrieren und ggf. mergen.
