# RZ-EVAL-P1 · aktuelle befristete Revieworiginale

Produkt-Head: `535403d8ac89c2da4800719f0d4a0fe0ba041950`, Draft-PR [#559](https://github.com/venomenon328/picross/pull/559).
Maßgeblich: [Paketentscheidung](https://github.com/venomenon328/picross/issues/558#issuecomment-6739323575),
[Eigentümernachträge und konkrete Bildwahl](https://github.com/venomenon328/picross/pull/559#issuecomment-6741480161).
Empfänger: unabhängiges R01 und D01; M01-Bildwahl ist dokumentiert. Bedarf/Rückbau
spätestens **16.11.2026** prüfen. Kein Merge dieses Refs, kein dauerhaftes Archiv;
die Frist ist ein Rückbauendpunkt, kein automatischer Git-Löschmechanismus.

## Konkrete Bilder auf dem tatsächlichen Buchpapier

Alle Links öffnen unveränderte native 2560×1440-PNGs. Gewählt: **1 / 2 / 1 / 3 / 3**.
Hinweise folgen derselben A/B1/B2/C-Regel wie das Raster; keine separate harte
Hinweismaske. Gemeinsame Quellbildränder und Controlschutz laufen weich aus.

| Rätsel | Kandidat 1 | Kandidat 2 | Kandidat 3 | Ohne Zeichnung |
| --- | --- | --- | --- | --- |
| Tomate | [c1](owner-book/tomate-c1-1440-A.png) | [c2](owner-book/tomate-c2-1440-A.png) | [c3](owner-book/tomate-c3-1440-A.png) | [Referenz](owner-book/tomate-c1-1440-A-without.png) |
| Qualle | [c1](owner-book/qualle-c1-1440-A.png) | [c2](owner-book/qualle-c2-1440-A.png) | [c3](owner-book/qualle-c3-1440-A.png) | [Referenz](owner-book/qualle-c1-1440-A-without.png) |
| Chocolate Hills | [c1](owner-book/hills-c1-1440-A.png) | [c2](owner-book/hills-c2-1440-A.png) | [c3](owner-book/hills-c3-1440-A.png) | [Referenz](owner-book/hills-c1-1440-A-without.png) |
| Petronas / Kuala Lumpur r3-alpha | [c1](owner-book/petronas-c1-1440-A.png) | [c2](owner-book/petronas-c2-1440-A.png) | [c3](owner-book/petronas-c3-1440-A.png) | [Referenz](owner-book/petronas-c1-1440-A-without.png) |
| Stirnlappenbasilisk | [c1](owner-book/basilisk-c1-1440-A.png) | [c2](owner-book/basilisk-c2-1440-A.png) | [c3](owner-book/basilisk-c3-1440-A.png) | [Referenz](owner-book/basilisk-c1-1440-A-without.png) |

Kein konkretes Rätselsubjekt im aktuellen Bildsatz. Qualle folgt dem konkreten
Meeresboden-/Seegras-/Fischbriefing, Kuala Lumpur dem Stadtbriefing ohne Türme.
23 ImageGen-Aufrufe: 20 unabhängige Generierungen und 3 zugeordnete Alpha-Edits.
15 aktuelle Kandidaten, 8 verworfene/ersetzte Vorstufen. `originals/` hält alle
unveränderten Bytes einschließlich Fehlversuchen; `reports/current-provenance.json`
bindet genaue Prompts, Elternbilder, Rechte, Hashes und standardisierte Ableitungen.
Korrekturen: ursprünglicher zentraler Dreitürme-Aufbau; ferne Bohol-Hügelformen;
drei zu kleinstädtische KL-Fassungen; drei Stadtbilder mit unerwünschten weißen Füllungen.

## Technische Originale und tatsächliche Bindung

- `owner-diagnostics/`: A/B1/B2/C, echte Zoom-/Input-/Abbruchfolge, 1080p,
  720p/UI125, 4K, 16:10, laufender Rückweg und pixelidentischer Leerfall.
  288 Zoomstichproben; eine feste Leinwand/Textur und kein Nachladen.
  `pixel-analysis.json`: keine Variantenänderung außerhalb von Raster **und Hinweisen**.
- `owner-mono/`: Qualle 2 bei erster/erneuter Öffnung, reale schwarze Füllungen/X,
  identische Funktionsgeometrie/Zellen und schwarzer Füllpixel über alle Varianten.
- `owner-resources/`: 301 tatsächliche Übergangsframes; Capture, aktive Illustration
  und Anfrage am Ende freigegeben. Gesamtzähler sind keine reine Asset-/Allocatorbilanz.
- `owner-profiles/`: gewählter Basilisk 3 in sieben Profilen bei 1440p/4K;
  zusätzliche technische KL-1-Gegenprobe. `owner-selected-profiles/` ergänzt die
  tatsächlich gewählte KL-3-Fassung in denselben sieben Profilen bei 1440p.
- `reports/profiles.json`: aktuelle fünf gewählte Bilder, alle Quell-/Import-/
  Exportbytes und pro Bild/Profile Dekodier-/Packladezeiten. Keine alte Stichprobe.
- `imports/`: 50 unveränderte CTEX aus tatsächlichen Exporten, exakt zugeordnet
  und gehasht durch `reports/export-bindings.json`.
- `packs/`: vollständige Baseline und PNG2304-PCK, direkter Exportzuwachs.
  Windows/Web sind pro Profil byteidentisch, keine doppelten Vollpacks.
- `logs/`, `harness/`: originale Prüfprotokolle und gezielter Einmalharness.
  Die alte CI-Timeoutursache ist mit ihrem damaligen Head getrennt dokumentiert.

`binding.json` und `reports/owner-native-runs.json` nennen tatsächliche Laufstände
und die enge Wiederverwendung. Nur die Petronas-Defaultwahl änderte sich nach den
aktuellen Buchoriginalen; diese wählen Kandidaten ausdrücklich. Spiel-/Shadercode
des separaten Profilprojekts ist gegen den aktuellen Produktstand bytegeprüft.
Dateien binär über echten Git-Checkout oder Raw-Download aus diesem Belegcommit
abrufen; Bytezahl, SHA-256 und Bildmaß gegen `manifest.json` prüfen und Originale
tatsächlich öffnen. GitHub-Vorschau oder leeres Contents-API-content bei >1 MiB
ersetzt keine geöffnete Binärdatei. Implementierersichtung erledigt R01 nicht.

## Aktuelle gemessene Profilbilanz

| Profil · fünf gewählte Bilder | Quellbytes | Importbytes | PCK-Zuwachs Windows = Web |
| --- | ---: | ---: | ---: |
| baseline | 0 | 0 | 0 |
| png-reference-2304 | 4,025,689 | 4,189,606 | 4,191,940 |
| png-1536 | 1,835,274 | 1,926,366 | 1,928,708 |
| png-2304 | 4,098,341 | 4,189,606 | 4,191,940 |
| png-3072 | 6,868,385 | 7,105,010 | 7,107,364 |
| webp-lossless-1536 | 1,177,184 | 1,926,366 | 1,928,716 |
| webp-lossless-2304 | 2,753,718 | 4,189,634 | 4,191,980 |
| webp-lossless-3072 | 4,785,386 | 7,105,030 | 7,107,404 |
| webp-q85-2304 | 1,405,790 | 3,731,394 | 3,733,740 |
| png-2304-no-mips | 4,098,341 | 3,021,634 | 3,023,972 |
| png-LA-2304 | 2,177,408 | 2,733,224 | 2,735,572 |

Gemeinsame logische Leinwand 3072×768, proportionaler Contain-Fit aller
2172×724-Originale, mittig/unten; keine per-ID-Offsets oder Zuschnitte. Bei 1440p
Papierprojektion P(94,81481;66,37033), S(2370,37;2939,259); sichtbare Leinwand
P(296,5926;879,8519), S(2144,593;536,1481). Fensteranpassung bleibt vom Rasterzoom getrennt.

PNG-Optimierung war größer als die pixelgleiche Referenz-PNG. Verlustfreies WebP
spart Quellbytes, praktisch keine Import-/PCK-Bytes. Q85 und LA ändern Bildwerte;
keine pauschale Qualitätsgleichheit. Native Image-Daten mit Mips (RGBA):
1536/2304/3072 = 3.145.720/7.077.844/12.582.904 Bytes; 2304 ohne Mips 5.308.416,
LA mit Mips 3.538.922. Transparenter Leerraum spart bei gleichen Maßen nicht diesen Speicher.

PNG2304-Pillow-Quelldekodierung, Median aus sieben Versuchen je Bild: etwa
5,96–18,23 ms. Tatsächliche headless PCK-Ladevorgänge: etwa 7,91–18,51 ms,
einschließlich Importtexturzugriff, ohne GPU-Upload. Native Besuche enthalten
Frames/Shader/Polling und sind kein reiner Decoderbenchmark. OS-Caches nicht geleert.
PNG2304-PCK-Zuwachs pro Stichprobenbild durchschnittlich 838.388 Bytes; **Hochrechnung**
für 100/300/500 Bilder: 83.838.800 / 251.516.400 / 419.194.000 Bytes.
Kein gelieferter Katalogumfang und kein allgemeines Budget. Gemeinsames Web-PCK
wird dadurch größer; lokales Bedarfsladen ist kein bedarfsgesteuerter Netzwerkdownload.

Unbegrenzte 90-Frame-Stichprobe ohne VSync: Median A/B1/B2/C ungefähr
2,397/2,304/2,395/2,301 ms; p95 2,752/3,230/5,686/4,434 ms. Reihenfolge/Warmup/
Gesamtspiel beeinflussen diese Werte: keine isolierte GPU-Zeit oder Nullkostenbehauptung.
TIME_PROCESS-Monitor wegen unplausibler Intervallwerte nicht als Framekosten interpretiert.
Drawcalls 771/771/771/772, Texturzähler 256.817.931 Bytes in allen vier Modi;
Videozähler A 273.073.471, danach 277.333.855 Bytes (kein isolierter Shadermehrbedarf).
301 Übergangsframes: Spitzen Textur/Video/CPU 280.323.375/302.685.163/662.859.546 Bytes.
Gesamtzähler kehren wegen anderer Spiel-/Allocatorressourcen nicht exakt zur Baseline zurück.

## Entscheidungsvorlage und Grenzen

B1 ist die technische/gestalterische Tendenz des Implementierers: ruhiger unter
Raster und Hinweisen. A kann dichte Vegetation/Stadtlinien mit Funktionszeichen
konkurrieren lassen; B2 bleibt präsenter und bietet keinen belegten Vorteil gegen
Abschwächung. C verdeckt vollständig, erzeugt aber ein auffälliges helles Rechteck
einschließlich Hinweisflächen. Keine endgültige Produktwahl aus dieser Tendenz.
2304/PNG mit Mips ist der mittlere Versuchsstand. 1536 verliert bei 4K feinere
Striche; 3072 erhält mehr Originaldetail, erzeugt aber keine neuen Details aus der
2172er Quelle. Q85/LA und Mip-Verzicht bleiben Qualitäts-/Farb-/Filterabwägungen.

Kuala Lumpur bleibt der stärkste indirekte Motivhinweis; tatsächliche Entdeckungs-
und Belohnungswirkung wurde nicht mit blind spielenden Personen gemessen.
Eigentümerwahl ist konkret dokumentiert, keine Serien-/Workflowfreigabe.
Aufwand je Motiv: Tomate 3, Qualle 3, Hills 4 unabhängige Generierungen,
KL 7 Generierungen + 3 Alpha-Edits, Basilisk 3. Aktive Arbeitszeit unbekannt;
12 Generierungszeiten direkt erfasst, acht weitere und drei Editzeiten unbekannt.
Parallelzeiten nicht addieren; Eigentümerwartezeit separat/unbekannt.

E1/E2/E4/E5/E7 sind als technische/kuratorische Versuchsergebnisse mit diesen
Grenzen geliefert; E3 hat konkrete Bildwahl, E6 eine begrenzte Empfehlung.
Unabhängiges R01 und die endgültige E1–E7-/Übernahme-oder-Rückbauentscheidung D01
bleiben offen. Keine Serienproduktion/Bestandsintegration. Folgefragen für
#489/#490/#491: Freigabe-/Herkunftsbindung, Kandidaten-/Revisionswahl und
deterministische Ableitungen/Wiederaufnahme. Diese Issues werden nicht geändert.
