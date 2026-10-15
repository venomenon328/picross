# Japanische Teekanne · Endabnahmevorlage r04

pz-51405ea1ad194507a60c9b6701d802f0 · **content_ready** · 15.10.2026 · Authoring0.5.0/Revision14.
Toolcommit `a54316d0cbb1cc1ec53ac63d22d6667c4f4640a4`. Inventar-Dateihash: `handoff.json → inventory.sha256` und äußerer `record.json` (selbstreferenzfrei).

**Freigaben:** B-r01: [reveal-approval.json](reveal-approval.json); MA-r01/Korridor: [motif-approval.json](motif-approval.json), echter Nutzerwortlaut jeweils gebunden. Redaktionelle Endabnahme **offen**.

**Auswahl:** `production/30x25 / area-144`, 30×25=750 Zellen; Mono `ink=#000000`, Leer weiß. Genau1 Farbe gewünscht/automatisch verwendet;395 gefüllt/355 leer (52,67%). [Echtes Raster](production/30x25/area-144-raster.png), [Gitter](final-raster.png), [Bildvergleich](final-comparison.png), [Originalabschlussbild](reveal/B-r01.png). Vier gezielte Varianten, keine Matrixduplikate. Zwei Schwelle112-Varianten stagnieren und haben Lücken an Henkelansätzen; 28×23/144 ist gültig,30×25 zeigt Knopf/Innenraum klarer. [Entscheidungen](decisions.json).

**Qualität:** Erkennbarkeit, Proportionen, Innenräume, Mono und Serienästhetik erfüllt. Knopf vom Bügel getrennt, linker Ausguss und Korpus erhalten. Rasterbedingte diagonale Konturanschlüsse explizit dokumentiert; keine isolierten Zellen, leeren Innenlinien, Zusatzanker oder Rand-Ausnahme. Keine Zelländerung/Reparatur: geeigneter Direktimport bereits vollständig zertifiziert. [Visuelle Prüfung](visual-review-r04.json).

**Pflichtprüfungen:** Maße/Palette/benutzte Farbzahl gültig; Rand links/oben/unten belegt. Original→Normalisierung→Matrix→Hinweise für alle vier Kandidaten frisch rekonstruiert; vollständiger `full-line-mono`-Proof mit172 Schritten unabhängig im frischen Prozess geprüft, Singleton-Endmatrix exakt gleich. Vollständige Deduktion belegt Eindeutigkeit, ohne Suchannahmen. [Herkunftsprüfung](origin-verification.json), [frische Proofprüfung](fresh-proof-verification.json). Paarprofil nicht nötig; keine separate Suchdiagnose.

**Schwierigkeit:** L2, plausibel L2–L4, `editorial_estimate`, Vertrauen low: dominante Überlappungen/Verlängerungen, mögliche kombinierte Zuordnung am Henkel; R0–R3-Notwendigkeit nicht validiert klassifiziert. Alle55 Linien vor jedem Schritt ausgewertet; vor15-Zellen-Restaufräumen mindestens3 produktive Linien, keine definierte Engstelle im Verlauf. [Schwierigkeit](difficulty.json) / [Checkpoints](difficulty-checkpoints.json).750-Zellen-Arbeitsumfang separat; menschliche Zeit **nicht geschätzt**.

**Herkunft/Aufwand:** native Projektgenerierung ohne fremde Referenzassets, Nutzungsgrundlage in den Provenienzdateien;3 frühere Reveal- und1 Motivbildaufruf, jetzt0 Bildaufrufe,2 Importe/4 Kandidaten/0 Reparaturrunden. Aktive Menschenzeit nicht erfasst. [Aufwand](effort.json).

**Zielstatus:** geschriebenes ZIP wird separat mit ZA-1 `inspect` geprüft; äußerer `inspection.json` bindet ZIP/Handoff/Inventar und Werkzeugstand. Export/Registrierung nicht ausgeführt; native Spiel-/Buildtests nicht erforderlich für diese Inhaltsablage. Einziger erwarteter Blocker: echte Endabnahme. Nächster Schritt: **4 · Abnehmen & ins Spiel integrieren**.
