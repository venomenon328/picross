# Sonnenblume · r04 · raster_review · 21.10.2026

ID `pz-a13368590b744814915eb722f5b2c5f2`; Regelwerk 0.5.0 / Dokumentrevision 22;
Quell-/Toolcommit `a59b08aeb8b1b5abc64297aa48fd22f3467a4a92`.
Inventarhash im [Handoff](handoff.json), vollständige Datei-/Hashliste im [Inventar](inventory.json).

[Abschlussbild und Vorher/Nachher](review/final-comparison.png) ·
[Zelldiff](review/veins-comparison.png) · [Endraster](review/final-raster.png) ·
[Gitter](review/final-grid.png) · [Zellauflösung](production/veins-r04/area-raster.png) ·
[unverändertes A-r01](reveals/A-r01.png) · [MA-r01](motifs/MA-r01.png).

**Änderung:** Beide vorhandenen Hauptadern samt Stängelanbindung sind durchgängig
abgebildet. Genau 27 Blattgrün-Zellen wurden gemäß [vorab gespeichertem Plan](edits/veins-plan.json)
dunkelgrün; [feste Editliste](edits/veins-record.json), keine Suche. Alle anderen
1253 Zellen einschließlich aller Leerzellen und des Blütenkopfs bleiben geschützt.
Füllmaske, Proportionen, Blattversatz, Zwischenräume, Maße und Palette unverändert.
A-r01, MA-r01 und deren echte Freigabebelege bleiben bytegleich. Die Änderung folgt
dem tatsächlichen [Korrekturauftrag](requests/leaf-veins.json), ist keine neue Motivvorlage.
Die ursprünglichen vier Varianten bleiben im gebundenen r03-Paket dokumentiert.

**Raster:** 32×40 = 1280 Zellen, farbig, vier tatsächlich verwendete Farben;
629 gefüllt / 651 leer. Gold #e8ae28:285; Braun #684323:107;
Dunkelgrün #29452e:50 (Stängel, Blattstiele, Hauptadern);
Blattgrün #638449:187 (Blattflächen). Genaue Wunschmaße/-farbzahl nicht vorgegeben.
Keine neue weiche Ausnahme; letzte Zeile/Spalte weiter leer durch contain;
Randformel besteht über links/oben. Alle fünf [Gestaltungskriterien erfüllt](review/visual-review.json).

**Neue technische Nachweise:** `full-line-color` vollständig, 213 Schritte,
[frischer unabhängiger Prüferprozess](review/proof-verification.json).
[Komponentenprüfung](review/components-verification.json): originalen Referenzimport
und neuen Kindimport frisch rekonstruiert; Normalisierung, Matrix und Hinweise,
exakte Enddomains und bestehender v1-Editreplay mit Schutzmaske geprüft.
Keine Vorbelegungen, Annahmen oder Motivprämissen. Vollständige Deduktion beweist Eindeutigkeit.
Keine Reparatur-, Paar- oder Eindeutigkeitssuche erforderlich.

**Neue Schwierigkeit:** [Methode 0.3 vollständig geprüft](analysis/checked.json):
L3 – Mittel, instrumented/medium, Basis 3 + Größe 0. 26 synchrone Wellen
(R0:6/R1:13/R2:7), keine Engstellenwelle, Enge 2273/14994; kein R3/R4 nötig.
Modellbewertung ohne menschliche Kalibrierung oder Zeitprognose.
0.1-[Kompatibilitätsmetadaten](difficulty.json) bleiben getrennte redaktionelle Schätzung.
Ein erfolgreicher Kindimport und eine vor Importbeginn korrigierte Pfadanlage;
[Aufwand](effort.json), aktive Menschenzeit nicht erfasst. Probespiel optional/nicht durchgeführt.
Nutzungsgrundlage: beauftragte native KI-Neuschöpfung und vorlagentreue Ableitung,
plus eigene feste Rasterkorrektur; keine Fremdvorlage/Exklusivitätsbehauptung.

**Freigabegrenze:** A-r01 und MA-r01 freigegeben; Endabnahme der r04-Korrektur offen.
Diese manuelle Fassung verwendet den bestehenden ZA-1-v4-Weg: `raster_review`,
`source_type=manual`, vollständig gebundener Originalimport und feste Ableitung.
Die echte Endabnahme samt darauf gebundener externer Autorisierung ist nach dem Vertrag
auch für die vollständige Adapterdiagnose erforderlich. Technische Komponenten
werden am geschriebenen ZIP getrennt frisch geprüft; kein falsches `technical=true`
für eine noch nicht autorisierte Adapterinspektion. Keine Spielregistrierung oder Veröffentlichung.
**Nächster Schritt: 4 · Abnehmen & ins Spiel integrieren** – die vorgelegte r04-Fassung
inklusive genau dieser Blattaderkorrektur ausdrücklich endabnehmen.
