# Huhn · Endabnahmevorlage r04

ID `pz-419437f56aba4603bf7a84bf0b624ba5` · 28.10.2026 · `content_ready`.
Regelwerk 0.5.0 · Toolcommit `1bc379c56ef3a8b8f743589f1f6f7affb2237b19`.
Inventarhash im [Handoff](handoff.json); Bericht ohne Selbstreferenz inventarisiert.

[Echtes Endraster](review/final-grid.png) · [Bildvergleich auf Buchpapier](review/final-comparison.png) ·
[Abschlussbild A-r01](images/reveal-a-r01.png) · [Motiv M-r01](images/motif-m-r01.png).
Beide Bilder bleiben bytegleich. Tatsächliche [Bildfreigabe](approvals/reveal-approval.json),
[Motivfreigabe](approvals/motif-approval.json) und [Croperweiterung](approvals/crop-extension.json)
sind mit Wortlaut belegt; menschliche Endabnahme ausdrücklich noch offen.

**Auswahl:** `import-crop-c/area-140`, Kandidat
`8fe16c75d0091b53041bd6c4e9d35cf87e176b9c0285e954982a146b87e50cee`.
30×32 / 960 Zellen, mono, `ink #242424` plus Leer; gewünscht und verwendet genau
eine Vordergrundfarbe. 434 Ink / 526 Leer (45,21 %). contain, Alpha 128,
area-Schwelle 140, engerer autorisierter Crop `[78,58,1212,1233]`.

Vier Grundkandidaten A/B und zwei vorab begründete Augenhypothesen C/D:
A140 gelöst, aber schlechtere Augenform; A180/B140/B180 `stalled` mit 7/16/23 offenen
Zellen, ohne Unlösbarkeitsbehauptung. D140 gelöst, aber stärkerer Seitenbeschnitt
und dichtere Körperform ohne Mehrwert. [Rastervergleich A/B](review/crop-candidates-grid.png),
[C/D](review/crop-cd-grid.png), [Pläne](crop-plan.json) und [Entscheidungen](decisions.json).
Die vier alten Raster bleiben mit vollständigen Bundles im gebundenen r03-Paket.

**Pflichtprüfungen:** Produktmaße und exakte Farbzahl erfüllt. Randregel durch
oben/rechts erfüllt; linke Spalte und letzte zwei Zeilen dürfen leer bleiben.
Original → Normalisierung → Matrix → Hinweise frisch rekonstruiert;
`full-line-mono` vollständig vom unbekannten Start, 150 Proofschritte,
unabhängiger Prüferprozess, Enddomains exakt gleich der Auswahl.
Damit Eindeutigkeit und vollständige Deduktion belegt. [Technische Belege](verification/crop-candidates.json),
[Matrix-/Warnbefunde](verification/final-matrix.json), [Quellen](verification/final-source.json).
Keine Paar-/Suchdiagnose oder Reparatur nötig: geeigneter Endkandidat bereits
vollständig zertifiziert. Keine manuellen Zelländerungen oder Rand-Ausnahme.

**Gestaltung:** Alle fünf Kriterien [erfüllt](visual-review.json). Kompakte
Augenform mit dunklem Zentrum, Kamm/Kehllappen, Flügel, Schwanz und zwei Beine
bleiben; Feder-/Iris-/Krallendetails sind stark reduziert. Auge und diagonal
angebundene Zehenspitze sind begründete Einzelzellen, keine Logikanker.
Farbige transparente Illustration und Raster bleiben motivisch konsistent.

**Schwierigkeit:** [vollständig geprüfte Methode 0.4](analysis/checked.json),
**L2 Leicht**, instrumented/medium; methodische Punktprojektion L2–L2, kein
menschliches Unsicherheitsintervall. E1 reicht in 23 Wellen, keine enge Nicht-E0-Welle.
Denkanspruch 1, Suche 72/121, Umfang 1/4; Score 893/484, auch ohne Umfang L2.
960 Zellen und 115 Hinweise sind Bearbeitungsumfang, keine Zeitprognose.
[Lesbarer Methodenbericht](analysis/full-bundle/rating/report.md).
Die [0.1-Adapterbegleitschätzung](difficulty.json) bleibt getrennt editorial/low;
keine Umetikettierung der tatsächlichen 0.4-Instrumentierung.

Nutzungsbasis: eigene auf Auftrag generierte Illustrationen, keine externen Assets.
Diese Fortsetzung: null Bildaufrufe, vier Importbündel/sechs Matrizen, keine Reparatur;
insgesamt zehn Rasterkandidaten. Menschenzeit/Lösungsminuten nicht erfasst,
Probespiel nicht durchgeführt und optional. ZIP-Inventar und geschriebene ZIP-Datei
werden frisch geprüft; die separate ZA-1-Inspektion liegt beim äußeren Record.
Export/Registrierung/Spielbuild nicht ausgeführt: tatsächliche Endabnahme fehlt.

**Nächster Schritt: 4 · Abnehmen & ins Spiel integrieren** – diese konkrete
Paketrevision samt Endraster und unverändertem A-r01 menschlich abnehmen.
