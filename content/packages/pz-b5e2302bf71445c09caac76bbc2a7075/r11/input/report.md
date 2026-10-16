# Carabao – Kopf · C-r03 · r11

`pz-b5e2302bf71445c09caac76bbc2a7075` · **Mehrdeutigkeit behoben; Endabnahme offen** · 2026-10-16T23:27:01.007730+00:00.
Regelwerk0.5.0/Rev14; Toolcommit `74b5827894ab67683d9ce7c8963a0e73ee8015fc`; Inventarhash außen nach Versiegelung.
[Raster](preview/C-r03-raster.png),[Gitter](preview/C-r03-grid.png),
[Vergleich](preview/C-r03-comparison.png),[B-r02/MA-r03/Endraster](preview/C-r03-acceptance.png).

**Korrektur:**Z2/S10 undZ4/S38 leer→ink. Die NutzerpositionenZ3/S36 bleibenleer,
Z5/S8 bleibtink; alle übrigen1038 Werte identisch zu C-r02. Hornkonturen lokal
zusammenhängend verdickt, große Innenräume/Hauptproportionen erhalten. Schnauze33
und Unterlippe3 Leerzellen weiterhin separat vierfach geschlossen, Augen/Ohren
unverändert. [Fünf Gestaltungskriterien](visual-review.json). Ein isolierter
diagonal angebundener Hornspitzenpixel Z1/S36 bleibt, feine Details weiterhin grob.

40×26/1040 Zellen,450 gefüllt/590 leer,gewünscht/verwendet genau1 Farbe ink+EMPTY.
Schwarz trägt Kopf/Konturen,Weiß Hintergrund/Binnenräume. Maße/Palette/Randregel PASS:
links/oben/unten belegt,rechts leer. B-r02/MA-r03 und tatsächliche Bildfreigaben bytegleich.

**Logik PASS:**252 informative full-line-mono-v1-Schritte vom unbekannten Start,
geschriebener Endproof frisch unabhängig geprüft,Endmatrix exakt. Vollständige
Deduktion belegt Eindeutigkeit, kein neuer Diagnosesuchlauf nötig.
[Finalaudit](audit/C-r03-final.json),[vollständiger RP5-Replay](audit/round-2-replay.json).
Originalquelle/Normalisierung/Matrix/Hinweise plus flache feste Edits und finaler
RP3-Import rekonstruiert; Endmatrix identisch zum RP5-Fund. Kein Direktimport aus
unveränderter Motivdatei behauptet; feste Mono-Ableitung ausdrücklich benannt.

Runde1 max2 Zellen,4 Bewertungen/8 Vorschläge,Frontier erschöpft. Runde2 anderer
Konturansatz mit acht freigegebenen Positionen,max2 Zellen,4 Bewertungen/4 Vorschläge,
Fund; sofort gestoppt. Vollständige vorher gespeicherte Pläne,Masken,Verläufe,
Eltern-/Endproofs und markierterDiff erhalten. Vorherige Paar-/multiple-Belege
bleiben an unveränderte alte Logik gebunden; keine Umdeutung oder Wiederholung.

**L2 geschätzt**,BereichL1–L4,editorial_estimate/low. Alle66 Linien vor252 Schritten
geprüft, mindestens3 produktive Linien vor Restaufräumen bei<=21 offenen Zellen,
keine numerische Engstelle nach<=2-Kriterium. Kein validierter schwächerer
Technikklassifikator, keine menschliche Kalibrierung. Umfang1040 Zellen,Zeit
nicht geschätzt;Probespiel optional/nicht durchgeführt. Hier0 Bildaufrufe,2
Suchreparaturrunden,1 finaler Import,keine neuen Paar-/Diagnoseläufe;aktive
Menschenzeit nicht erfasst. Nativ beauftragte KI-Bilder ohne Fremdassets,keine Exklusivität.

**Gesonderte Endabnahme offen.** Für feste Mono-Ableitungen verlangt ZA-1-v2 auch
für inspect externe exakte Autorisierung/Endfreigabe. Deshalb Handoff blocked
allein für diesen Freigabestopp, Logikgate pass; kein content_ready/ZA1-Erfolg
oder Owner-Override erfunden. Kein Zieladapterexport/Spielregistrierung.
Native Spiel-/Buildtests für Ablage nicht erforderlich.
**Nächster Schritt:4 · Abnehmen & ins Spiel integrieren.**
