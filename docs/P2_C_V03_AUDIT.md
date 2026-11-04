# P2-C-V03: Audit aller bisherigen nativen PNG-Pflichten

Verbindlich: [Eigentümerentscheidung #502](https://github.com/venomenon328/picross/issues/502#issuecomment-6637589747).
Basis `5471a42e6291d9eeda9b2a04811547d21b0430ff`, [V02-Erfolg](https://github.com/venomenon328/picross/actions/runs/41862944396).
Dieser Audit ersetzt die früheren Bild-/Mengenpflichten im beauftragten nativen CI-Bereich.
Er ist keine neue Bildsammlung und kein zusätzlicher Ausführungs-/Inventarguard.

## Vollständige Zuordnung

Die disjunkten Familien unten umfassen **alle 435 logischen PNGs**, einschließlich
kleiner Bilder und der 66 Aliasdateien: 423 feste Inventareinträge, fünf nach
echten Zeitstempeln ausgewählte EA-Frames und sieben HIL-Dateien. Quelle sind
`native_artifacts.json` am Basiscommit und die tatsächlichen `files`/`image_aliases`
des V02-Erfolgsoriginals. Keine Größenfilterung. Bisher 369 physische PNGs,
133.167.809 rohe Bildbytes; gesamtes Technik-ZIP 135.806.104 B.
Die Byte-Spalte zählt physische Originale einmal; Aliase kosten darin null.
Erzeugungskosten sind die realen Render-/Readback-/Encoderphasen, keine aus der
Dateigröße abgeleitete Laufzeit. Geteilte Phasen lassen keine additive CPU-Zuordnung
pro Screenshot zu. T01 vergleicht deshalb die gemessenen Phasen/Gruppen und den
gesamten kritischen Pfad, zusätzlich zu diesen exakten Dateikosten.

H = historische Einführung/Sicht → aus Dauer-CI entfernt; D = aktuelle Fachregression
→ kleinstes Oracle; E = konkrete offene persönliche Einmalabnahme außerhalb Dauer-CI.
Bei D ist die frühere Bildlieferung gerade **keine** selbständige Fachgarantie.

| Familie | Klasse | Alte logische PNGs | Alte physische PNG-Bytes | Producer → tatsächlicher Leser; Entscheidung und aktuelles Risiko |
| --- | --- | ---: | ---: | --- |
| RP6 | D | 1 | 1,375,374 | `rp6_capture → p1_product`. Abschluss-Sichtdatei entfällt; echte Pilotprozesse, Speicherstand und eigene falsche Miniaturpixel bleiben. Kleinste fallbezogene Fehleraufnahme nur bei Fehler. |
| ZA1 | D | 8 | 12,164 | `za1_probe → za1_product/native_results`. Acht Pflichtausschnitte und zusätzliche Vollkontexte werden nicht mehr geschrieben; Originalpixel der eigenen Miniatur, unverratenes/verdientes Bild, Palette, Saves, Registrierung und PCK bleiben geprüft. |
| KAT-Fachfälle | D | 53 | 31,048,859 | `kat2_probe → kat2_product/native_results`. Paging, Auswahl, Metadaten, Reset, Fehler/Recovery, reale Pointer und Text-/Kartenbegrenzung bleiben. shot liest/schreibt keine Bilder mehr; Crop-/Hash-Reader und Bildkostenbericht entfernt. |
| AT-klein | D | 10 | 431,950 | `at_alpha → at_evidence.native`. Fünf Kontexte; je Original+Papier wird zu einem 5×2-Sample. Unabhängige Alpha-Komposition am Gate, nicht bloß Hashvergleich. |
| AT-Matrix | H | 20 | 3,954,609 | `at_alpha → at_evidence.native`. 1920/2560 wiederholten dieselben fünf Kompositionsfälle. Keine eigenständige Alphaaussage; Erzeugung und Matrixpflicht entfernt. |
| HZ | H | 60 | 16,466,491 | `hz_native/hz_b_native/hz_c_native → Inventar`. HZ-A/B/C integriert; Schrift-/Kontur-/Menü-/Icon-Einführungsvergleiche samt Producern und Reports entfernt. Aktuelle Treffer-/Zustandsprüfungen bleiben separat. |
| KE-Vergleich | H | 27 | 7,152,282 | `ke_graphics → Inventar`. 27 PNG/SVG-/Status-/Abschluss-Sichtvergleiche ohne unabhängigen Fehleroracle; Producer gelöscht. Eigenes Vorschaubild, Spoilergrenze und Alpha werden aktuell in KAT/ZA1/AT geprüft. |
| EA-Sicht | H | 4 | 5,300,774 | `ea_probe → Inventar`. Vier Vollbilder ohne unabhängigen Pixelreader entfernt. Endgeometrie/Seitenverhältnis/Caption-Kollision und rechteckige Rasterpalette bleiben direkte Assertions. |
| EA-Film | H | 5 | 3,338,628 | `ea_probe → ea_product.prepare_images`. Fünf Filmphasen plus nicht als PNG gezählte APNG entfielen. Kein unabhängiger Bewegungsoracle las diese Datei; Filmframes, Encoder und Phase entfernt. Reale Completion-/Stop-/Save-/Restart-, Raster- und Blendprüfungen bleiben. |
| HIL | E | 7 | 12,192,409 | `help_native → book_lifecycle/native_results`. HIL-M01 offen; sieben reine Sichtdateien/Maße entfallen. Hilfe-, Schema-1-, Save-/Recovery-Assertions bleiben im echten Buchprozess. |
| ZS-Studie | H | 51 | 3,826,022 | `zs1/zs2_capture → frühere Vergleichs-/Galerieleser`. 51 alte Pflichtbilder: Vollszenen, Zifferngalerie, allgemeine Studienbewegung/Striche, zusätzliche 12/36-Pixel-Folgen. Kein Replay; eigenständiger aktueller 24-Pixel-Producer ohne Studienvererbung. Atlas prüft weiterhin alle Größen in-memory. |
| ZS-Zeitpixel | D | 24 | 60,341 | `zs2_capture → zs2_delivery/p1_current_visual`. 24 temporäre native Ausschnitte: X 7, Füllung 9, Welle 8. Kontrollierte und reale Zeitpunkte, räumlicher Aufbau und Gegenproben bleiben; nach erfolgreichem Pythonoracle gelöscht, keine Lieferung. |
| HC-Galerie | H | 36 | 197,714 | `hc92_capture → hc92_verify`. 36 Font-/Status-Einführungsbilder, Captureprozess und Galerieoracle entfernt. Laufende Glyphengeometrie und Font-Ressourcen bleiben durch VS2/HF/HS/Core geprüft. |
| HF-Fachfälle | D | 17 | 10,644,678 | `hf149_probe → hf149_verify`. 17 Datei-/Maßnachweise entfallen; semantische Fenster, Budget-/Font-/Clippingmathematik und echte Save-Runden bleiben. Kein Bildreadback nur für diese Lieferung. |
| HN-Bänder | D | 5 | 21,941 | `hn192_probe → hn_evidence`. Fünf minimale Rohpixelbelege bleiben für unabhängige Zeilen-/Spalten-/Kreuz-/Endzeilen-/Ziehbandprüfung, siehe Einzelbegründung. |
| HN-Matrix | H | 10 | 36,764 | `hn192_probe → hn_evidence`. Zehn Wiederholungen desselben Bandoracles bei größeren Fenstern entfallen. Reale native Eingaberouten und kleine Fläche bleiben. |
| HS-Matrix | H | 35 | 760,759 | `hs186_capture → hs186_verify`. 35 wiederholte Layerbilder/Restmatrix entfallen; keine weitere Aussage gegenüber dem gezielten fractional-edge-Fall. Die HF-Szenen-Maßreader entfallen ebenfalls. |
| HS-Zahl-X | D | 5 | 96,957 | `hs186_capture → hs186_verify`. Fünf temporäre Layerbilder im gebrochenen 23,37-Pixel/UI125-Fall: Zahl/X-Trennung, vollständige Tinte und stabile Identität mit drei echten Pixelmutanten. Nach Reader gelöscht. |
| Atlas | D | 13 | 2,018,227 | `perf_b_probe → p1_product/perf_b_resources`. 13 Lieferbilder einschließlich Streifen/Dichtbild entfallen. Pixelgleichheit Referenz/Atlas, Cache/Invalidierung, Dichte und Timing bleiben in-memory; keine Streifenherstellung. |
| Rasterpixel | D | 14 | 9,631,863 | `capture → p1_product`. 14 Pflichtbilder entfallen. Palette/Moat, Preview-Alpha, Linienfokus, Zähler und fehlerhafte Farben werden am echten Frame geprüft. Z2-Buch-/Tooltip-Einführungslauf entfernt. |
| V1-Einführung | H | 12 | 9,393,296 | `vs2_v1_tests → vs2_v1_verify`. 12 Bilder, separater Fokus-/Glyphenprozess und alte Mengenreader entfallen. Aktuelle unabhängige Layoutmathematik nutzt die ohnehin laufenden 96 VS2-Fälle mit echter Gegenprobe. |
| V2-Fachfälle | D | 6 | 3,458,816 | `vs2_v2_tests → vs2_delivery.verify_v2`. Sechs reine Datei-/Hashbelege entfallen. 19 reale Transitionsfälle, Miniatur-/Palettenpixel und separater Readprozess bleiben. |
| V3-Einführung | H | 12 | 11,746,891 | `vs2_v3_tests → vs2_delivery`. 12 Bilder und separater 36-Fälle-Einführungslauf entfallen aus Regel-CI; aktuelle Rahmen/Palette und Bedienelement-Erreichbarkeit prüfen capture/RP6/VS2. Ein expliziter alter Windows-Sichtaufruf ist kein CI-Reader. |

Summenkontrolle: D = 156, E = 7, H = 272; insgesamt 435.

## Verbleibende Erfolgsausnahmen, einzeln

Es bleiben **zehn logische PNGs** ausschließlich als Eingaben des unabhängigen
`native_results`-Gates. Die Gatefunktion liest die Originalpixel selbst; eine
Producer-JSON mit selbst erzeugtem Hash könnte falsche Komposition/Bänder als
Erfolg deklarieren und ist daher kein Ersatz. Temporäre In-process-Prüfung würde
diese bestehende unabhängige Vertrauensgrenze aufheben. Die fünf AT-Fälle verwenden
je **5×2 RGB8**: fünf konkrete Quellklassen (transparent außen, opakes Weiß,
transparentes Innenloch, Alpha 80, opake Tinte), jeweils mit tatsächlichem
Papierpixel. Die fünf HN-Fälle verwenden **50×100 RGBA8**: eine echte Probe je Zelle
des 50×50-Testbretts plus die passende Baseline. Dadurch kann der Reader auch
unerwartete Bänder außerhalb der gewählten Linie finden; ein einzelner positiver
Linienpixel wäre unzureichend. Kein Vollframe, kein skaliertes Vorschaubild.

| Datei relativ zur ausgewählten Gruppe | Eigenständige aktuelle Aussage | Unabhängiger Reader / Trigger |
| --- | --- | --- |
| `catalog/kat2/at-catalog-1280.png` | Verdienstgebundene kleine Katalogvorschau komponiert Transparenz und Weiß korrekt | `at_evidence.native`, Auswahl catalog |
| `catalog/kat2/at-hover-1280.png` | Große Hovervorschau verwendet dieselben Alphaquellen korrekt trotz eigener Darstellung | `at_evidence.native`, Auswahl catalog |
| `completion/ea/at-final-1280.png` | Vollständiges verdientes Abschlussbild behält Weiß und echte Löcher | `at_evidence.native`, Auswahl completion |
| `completion/ea/at-reopen-1280.png` | Erneutes Öffnen nach Navigation erhält die Alpha-Komposition | `at_evidence.native`, Auswahl completion |
| `completion/ea/at-blend-1280.png` | Tatsächlicher Zwischenzustand bei halber Opazität statt Endbild oder fehlendem Bild | `at_evidence.native`, Auswahl completion |
| `graphics/hn192/hn-1280-ui125-row.png` | Nur gewählte Zeile, kein Phantomspaltenband | `hn_evidence.verify`, Auswahl graphics |
| `graphics/hn192/hn-1280-ui125-column.png` | Nur gewählte Spalte, kein Phantomzeilenband | `hn_evidence.verify`, Auswahl graphics |
| `graphics/hn192/hn-1280-ui125-grid.png` | Beide Achsen am Rasterziel, keine weiteren Bänder | `hn_evidence.verify`, Auswahl graphics |
| `graphics/hn192/hn-1280-ui125-complete-row.png` | Vollhinweis der letzten Zeile, Overlay-Ausschluss und Brettgrenze | `hn_evidence.verify`, Auswahl graphics |
| `graphics/hn192/hn-1280-ui125-drag-row.png` | Beim Ziehen bleibt der semantische Zeilenbezug korrekt | `hn_evidence.verify`, Auswahl graphics |

Alle zehn: Owner `venomenon328`, Review **V03-R01, spätestens 18.11.2026**.
Vor Abschluss von #502 erneut Notwendigkeit/kleineren Vertrauensgrenzennachweis
bewerten; kein automatischer Dauerstatus allein durch dieses Inventar.
Unkomprimierte Nutzpixel insgesamt 100.150 B; tatsächliche PNG-/ZIP-/Readback-/CPU-
Kosten stehen in T01 am erfolgreichen Run. `native_contract.select_groups` wählt
bei jeweiligen UI-/Test-/Readeränderungen die betroffenen Gruppen, bei gemeinsamem
Harness oder unbekanntem Einfluss konservativ alle sieben. Kein Chromiumtrigger.

HS benötigt fünf temporäre 900×480-Layerbilder, um über 64 Fälle die vollständige
Zahl-/X-Tinte und Masken zu prüfen. ZS benötigt 24 temporäre Originalausschnitte
(7 X, 9 Füllung, 8 Welle); kontrollierte UND drei echte Renderzeitpunkte bleiben.
Ihre unabhängigen Pythonreader laufen vor dem Löschen, mitsamt mutierten Bildern
(fehlende Zahl/X, globales Fade, falsche Strichrichtung/Schraffur). Der Report
misst die konsumierten PNGs/Bytes ausdrücklich weiter. Erfolg liefert nur
Ergebnisse; Fehler behält nur fallbezogene Originaldaten nach bestehender Frist.

## Offene Abnahmen und Historie

HIL-M01 und die in den Produktquellen ausdrücklich offenen persönlichen KU-/VS2-/
Schrift-/Bedienabnahmen bleiben offen. Diese Änderung erklärt weder Sehqualität
noch Mausgefühl für abgenommen. Für eine konkret beauftragte persönliche Abnahme
erst dann einen einzelnen passenden Sichtkandidaten aus aktuellem Produkt erzeugen,
Owner/Gate/Frist binden und nach Entscheidung oder spätestens sieben Tagen beenden.
Jetzt wird kein E-Artefakt erzeugt und kein neuer automatischer Job eingerichtet.
Historische PRs/Commits und T01 bleiben Quelle; kein neues historisches Archiv.

Save/History/Recovery, Katalog-Spoilergrenzen, aktueller Glyphen-/Raster-/Alpha-/
Animationsvertrag, importierte Ressourcen und echter PCK-/Windows-Export behalten
ihre Fachprüfungen. Die überflüssigen Bild-Dateinamen-, Galerie-, Crop-/Hash- und
Mengenreader wurden zusammen mit Produzenten, Phasen und Inventar entfernt.
Quelle/Head/Basis/Versuch, Originalassertions, Pfad-/Dateiintegrität und negative
Manipulationen des **neuen** Solls bleiben fail-closed. 75 MiB/<10 Minuten sind
weiter Ziele; keine neue P3-B-Grenze, kein Merge-/Deployment-/Chromiumauftrag.
