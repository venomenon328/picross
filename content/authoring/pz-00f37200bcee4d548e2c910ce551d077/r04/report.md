# Drachenfrucht r04 · blockierter Produktionsstand

pz-00f37200bcee4d548e2c910ce551d077 · 23.10.2026 · Authoring 0.5.0 / Dokumentrevision 23 · Toolcommit 983e511bfdd2b99f8c5eeceabeb5819a8172a00b. Inventarhash im Handoff/Record.

**Ergebnis:** Keine Endabnahmevorlage. MC-r01 und gesamter Korridor sind menschlich freigegeben; B-r01 bleibt unverändert. Endabnahme, Export und Spielregistrierung sind offen. [Rastervergleich](review/candidates.png), [Bildvergleich](comparison.png), [Sichtprüfung](review/visual-review.json).

| Variante | Farben tatsächlich | Linienprofil | Dunkle Kernformen |
| --- | --- | --- | --- |
| 20×22, 440 Zellen, vier Farben | 4 (117 Creme, 1 Dunkel, 68 Grün, 106 Pink) | solved, 91 Schritte, unabhängig bestätigt | 1 statt 6: verworfen |
| 20×22, drei Farben | 3 | stalled, 95 offen | 1 statt 6: verworfen |
| 22×24, 528 Zellen, vier Farben | 4 (138 Creme, 5 Dunkel, 83 Grün, 127 Pink) | stalled, 4 offen | 5 statt 6: keine Freigabe |
| 22×24, drei Farben | 3 | stalled, 95 offen | 5 statt 6: verworfen |

Gewünschte Farbzahl ursprünglich offen; freigegebener Korridor 3/4. Alle vier Matrizen verschieden, sämtliche Paletteneinträge genutzt. Alle Randregeln bestehen sogar an allen vier Kanten. Keine motivfremden Randanker. Nicht alle Kanten wären erforderlich. [Messwerte](review/candidate-metrics.json).

**Nachweise:** Original → Normalisierung → Matrix → Hinweise und exakte Rasterpixel in frischen unabhängigen Prüferprozessen rekonstruiert. Alle vier ursprünglichen Proofstatus bestätigt; der solved-20×22-Proof endet exakt auf seiner Matrix. Das ist ein logischer Beleg, keine Motivfreigabe. [Prüfberichte](review/verified-20x22-c4.json), weitere Varianten daneben. Bild-/Motivherkunft, Originalhashes, Rechte und beide echten Freigaben sind gebunden.

**Paarprofil/Reparatur:** 22×24/c4 bleibt mit paired-lines-color bei denselben vier offenen Zellen stehen (Spalten 1/3, Zeilen 7/10; 1-basiert). Beide Linienbaselines und Paarproofs frisch geprüft. R4 nicht nachgewiesen. Runde 1: nur zwei fehlklassifizierte Kernzellen veränderbar, höchstens zwei Änderungen/64 Bewertungen/512 Vorschläge; 3 Bewertungen, 2 Vorschläge, Abbruch bei effektiv 20 Mio. Paararbeit aus der Referenz. Runde 2: andere kombinierte Kern-/Flankenhypothese, neue unveränderte Referenz mit 100 Mio. Paararbeit, höchstens zwei Änderungen/128 Bewertungen/1024 Vorschläge; 17 Bewertungen, 20 Vorschläge, Abbruch bei 100 Mio. Paararbeit. Kein Fund, kein Endproof. Gesonderte repair verify-Aufrufe ebenfalls am Paarbudget abgebrochen; vollständiger Reparatur-Replay ausdrücklich nicht abgeschlossen. Originalbündel bleiben vollständig. [Pläne, Status und Grenzen](review/repair-verification.json). Kein Unmöglichkeitsurteil.

**Schwierigkeit:** keine Stufe, Methode/Vertrauen/Bereich nicht vergeben; es fehlt ein visuell akzeptierter vollständiger Endkandidat. 440/528 Zellen beschreiben nur Arbeitsumfang; Lösungszeit nicht geschätzt, Probespiel nicht durchgeführt und optional. SD-0.3-Analyse und ZA-1-content_ready-inspect entfallen an diesem frühen blockierten Eingang; kein Export erzeugt.

**Aufwand/Nächster Schritt:** 4 Rasterkandidaten, 2 zusätzliche profilierte Bindungen derselben Matrix, 2 Reparaturrunden, 0 neue Bildaufrufe; aktive Menschenzeit nicht erfasst. Nutzerbeauftragte KI-Bilder ohne fremde Vorlage, Nutzungsgrundlage in Provenienz. Motivvorlage aus dem unveränderten B-r01 mit ausreichend großen kompakten dunklen Kernflächen überarbeiten und konkrete neue Motivdatei vor Rasterproduktion freigeben. Keine Spiel-/Save-/Codeänderung. Ablage-CI und gesonderter Selbstreview werden außen im PR gebunden.
