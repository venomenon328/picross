# Cầu Vàng · r04 · content_ready

25.10.2026 · `pz-86d1d588a88a46e6ac1285f0097afbca` · Authoring 0.5.0 / Dokumentrevision 23.
Quell-/Toolcommit `bdf0080316296f5187767465cde62ec7aa722323`; Inventarhash im Handoff/Record, ohne Selbstreferenz.

**Verbesserung:** **40×20, fünf Farben**, 800 Zellen, 459 gefüllt/341 leer.
Zusätzliche neutrale Steinschatten heben Fingerseiten, Daumen und Handflächen
von dunklerem Grün ab. Obere fünf Fingerzeilen: 8 grüne Zellen in r03,
0 in r04; nur beobachtender Farbvergleich, keine Erkennbarkeitskennzahl.
[Vorher/Nachher und Reveal](audit/final-comparison.png), [Raster](final-raster.png),
[groß](final-raster-large.png), [Gitter](final-grid.png), [Abschlussbild](reveals/A-r01.png).
Palette: charcoal #38413f (4 Zellen), gold #d1a02c (51 Zellen), green #356c36 (137 Zellen), shadow #7b817a (178 Zellen), stone #c9c8b7 (89 Zellen).
Grün Vegetation, Gold Brücke, heller Stein Hände/Felsen, neutraler Schatten
deren Konturen und Graphit die dunkelsten strukturellen Kanten. Alle fünf benutzt.
Nutzerfarbe ursprünglich offen, alter Korridor 3/4, jetzt zusätzliche Farben
tatsächlich autorisiert; die KI hat fünf/sechs als konkrete Untersuchung gewählt.

**Auswahl:** Sechs neue Varianten, drei 40×20 vollständig linienzertifiziert;
44×22/5 bleibt mit 4, 44×22/6 mit 11 Zellen im bestätigten Linienfixpunkt offen.
Die gezielte Fünffarbpalette mit dunklerem Grün trennt die Hände am klarsten.
Sechste graue Zwischenstufe bringt vor allem kleinteilige Tonaufteilung.
[Kandidaten](audit/hands-candidate-comparison.png), [Palettenvergleich](audit/hands-palette-comparison.png),
[Entscheidungen](decisions.json). Keine Reparatur erforderlich: geeigneter
zertifizierter Direktimport vorhanden. Keine zusätzliche Routinepaar-/Suchprüfung.

**Gestaltung/Grenzen:** Zwei Hände, größere linke, Daumenverlauf, Brückenkurve und
zentrale Öffnung erhalten. Belegt-/Leermaske und Maße exakt gleich r03;
184 Zellfarbwerte durch den neuen deterministischen Import anders,
keine manuelle Matrixbearbeitung. Fingergelenke/Geländerlücken bleiben abstrahiert.
Untere Außenzeile leer, keine isolierten Vordergrundzellen.
[Qualitätsprüfung](audit/final-quality.json), [vollständiger Farbdiff](audit/r03-r04-diff.json).

**Pflichtprüfung:** Produktmaße, tatsächliche Farben, Randregel (links/rechts/oben),
Herkunft, deterministische Hinweise, vollständige Deduktion mit **full-line-color**
vom unbekannten Start ohne Raten, unabhängiger frischer Prüfer und exakte
Endmatrix bestanden. Vollständige Deduktion belegt zugleich Eindeutigkeit.
[Prüfbelege](audit/technical-checks.json), [Rekonstruktion](audit/hands-verify-40x20-5c-clear.json).
Alle sechs vollständigen neuen RP-3-Bündel erhalten; frühere r03-Bündel bleiben
am gebundenen Vorgänger, nicht als redundante neue ZIP-Kopie.

**Schwierigkeit:** **L3 – Mittel**, Punktbereich L3–L3 der Methode 0.3,
instrumentiert/medium; Basis 3 + Größe 0, R2, 15 synchrone Wellen,
keine Engstellenwelle, kein R3/R4. [Vollständig geprüfter Input](analysis/checked.json).
Punktbereich ist kein menschliches Unsicherheitsintervall. Separate vorsichtige
[0.1-ZA-1-Begleitschätzung](difficulty.json) L3/low, L2–L4 bleibt methodisch getrennt.
Bearbeitungsumfang 800 Zellen, 459 Hinweise,
112 Proofschritte; Lösungszeit nicht geschätzt.

**Freigaben/Status:** Abschlussbild und Motivbytes samt Herkunft/Nutzungsgrundlage
unverändert; tatsächliche Farberweiterung in motif-approval.json und Nutzerbeleg.
Vier frühere Bildaufrufe, aktuell keine Bildgenerierung, sechs Importe/eine Analyse;
aktive Menschenzeit nicht erfasst. Probespiel optional/nicht erfolgt.
Menschliche Endabnahme von r04 ausdrücklich offen, kein ZA-1-Export/Spieleintrag.
Nächster Schritt: **4 · Abnehmen & ins Spiel integrieren** nach gebundener Endfreigabe.
