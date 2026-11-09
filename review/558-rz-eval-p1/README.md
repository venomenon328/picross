# RZ-EVAL-P1 Â· aktuelle befristete Revieworiginale

Produkt-Head: `535403d8ac89c2da4800719f0d4a0fe0ba041950`, Draft-PR [#559](https://github.com/venomenon328/picross/pull/559).
MaÃŸgeblich: [Paketentscheidung](https://github.com/venomenon328/picross/issues/558#issuecomment-6739323575),
[EigentÃ¼mernachtrÃ¤ge und konkrete Bildwahl](https://github.com/venomenon328/picross/pull/559#issuecomment-6741480161).
EmpfÃ¤nger: unabhÃ¤ngiges R01 und D01; M01-Bildwahl ist dokumentiert. Bedarf/RÃ¼ckbau
spÃ¤testens **16.11.2026** prÃ¼fen. Kein Merge dieses Refs, kein dauerhaftes Archiv;
die Frist ist ein RÃ¼ckbauendpunkt, kein automatischer Git-LÃ¶schmechanismus.

## Konkrete Bilder auf dem tatsÃ¤chlichen Buchpapier

Alle Links Ã¶ffnen unverÃ¤nderte native 2560Ã—1440-PNGs. GewÃ¤hlt: **1 / 2 / 1 / 3 / 3**.
Hinweise folgen derselben A/B1/B2/C-Regel wie das Raster; keine separate harte
Hinweismaske. Gemeinsame QuellbildrÃ¤nder und Controlschutz laufen weich aus.

| RÃ¤tsel | Kandidat 1 | Kandidat 2 | Kandidat 3 | Ohne Zeichnung |
| --- | --- | --- | --- | --- |
| Tomate | [c1](owner-book/tomate-c1-1440-A.png) | [c2](owner-book/tomate-c2-1440-A.png) | [c3](owner-book/tomate-c3-1440-A.png) | [Referenz](owner-book/tomate-c1-1440-A-without.png) |
| Qualle | [c1](owner-book/qualle-c1-1440-A.png) | [c2](owner-book/qualle-c2-1440-A.png) | [c3](owner-book/qualle-c3-1440-A.png) | [Referenz](owner-book/qualle-c1-1440-A-without.png) |
| Chocolate Hills | [c1](owner-book/hills-c1-1440-A.png) | [c2](owner-book/hills-c2-1440-A.png) | [c3](owner-book/hills-c3-1440-A.png) | [Referenz](owner-book/hills-c1-1440-A-without.png) |
| Petronas / Kuala Lumpur r3-alpha | [c1](owner-book/petronas-c1-1440-A.png) | [c2](owner-book/petronas-c2-1440-A.png) | [c3](owner-book/petronas-c3-1440-A.png) | [Referenz](owner-book/petronas-c1-1440-A-without.png) |
| Stirnlappenbasilisk | [c1](owner-book/basilisk-c1-1440-A.png) | [c2](owner-book/basilisk-c2-1440-A.png) | [c3](owner-book/basilisk-c3-1440-A.png) | [Referenz](owner-book/basilisk-c1-1440-A-without.png) |

Kein konkretes RÃ¤tselsubjekt im aktuellen Bildsatz. Qualle folgt dem konkreten
Meeresboden-/Seegras-/Fischbriefing, Kuala Lumpur dem Stadtbriefing ohne TÃ¼rme.
23 ImageGen-Aufrufe: 20 unabhÃ¤ngige Generierungen und 3 zugeordnete Alpha-Edits.
15 aktuelle Kandidaten, 8 verworfene/ersetzte Vorstufen. `originals/` hÃ¤lt alle
unverÃ¤nderten Bytes einschlieÃŸlich Fehlversuchen; `reports/current-provenance.json`
bindet genaue Prompts, Elternbilder, Rechte, Hashes und standardisierte Ableitungen.
Korrekturen: ursprÃ¼nglicher zentraler DreitÃ¼rme-Aufbau; ferne Bohol-HÃ¼gelformen;
drei zu kleinstÃ¤dtische KL-Fassungen; drei Stadtbilder mit unerwÃ¼nschten weiÃŸen FÃ¼llungen.

## Technische Originale und tatsÃ¤chliche Bindung

- `owner-diagnostics/`: A/B1/B2/C, echte Zoom-/Input-/Abbruchfolge, 1080p,
  720p/UI125, 4K, 16:10, laufender RÃ¼ckweg und pixelidentischer Leerfall.
  288 Zoomstichproben; eine feste Leinwand/Textur und kein Nachladen.
  `pixel-analysis.json`: keine VariantenÃ¤nderung auÃŸerhalb von Raster **und Hinweisen**.
- `owner-mono/`: Qualle 2 bei erster/erneuter Ã–ffnung, reale schwarze FÃ¼llungen/X,
  identische Funktionsgeometrie/Zellen und schwarzer FÃ¼llpixel Ã¼ber alle Varianten.
- `owner-resources/`: 301 tatsÃ¤chliche Ãœbergangsframes; Capture, aktive Illustration
  und Anfrage am Ende freigegeben. GesamtzÃ¤hler sind keine reine Asset-/Allocatorbilanz.
- `owner-profiles/`: gewÃ¤hlter Basilisk 3 in sieben Profilen bei 1440p/4K;
  zusÃ¤tzliche technische KL-1-Gegenprobe. `owner-selected-profiles/` ergÃ¤nzt die
  tatsÃ¤chlich gewÃ¤hlte KL-3-Fassung in denselben sieben Profilen bei 1440p.
- `reports/profiles.json`: aktuelle fÃ¼nf gewÃ¤hlte Bilder, alle Quell-/Import-/
  Exportbytes und pro Bild/Profile Dekodier-/Packladezeiten. Keine alte Stichprobe.
- `imports/`: 50 unverÃ¤nderte CTEX aus tatsÃ¤chlichen Exporten, exakt zugeordnet
  und gehasht durch `reports/export-bindings.json`.
- `packs/`: vollstÃ¤ndige Baseline und PNG2304-PCK, direkter Exportzuwachs.
  Windows/Web sind pro Profil byteidentisch, keine doppelten Vollpacks.
- `logs/`, `harness/`: originale PrÃ¼fprotokolle und gezielter Einmalharness.
  Die alte CI-Timeoutursache ist mit ihrem damaligen Head getrennt dokumentiert.

`binding.json` und `reports/owner-native-runs.json` nennen tatsÃ¤chliche LaufstÃ¤nde
und die enge Wiederverwendung. Nur die Petronas-Defaultwahl Ã¤nderte sich nach den
aktuellen Buchoriginalen; diese wÃ¤hlen Kandidaten ausdrÃ¼cklich. Spiel-/Shadercode
des separaten Profilprojekts ist gegen den aktuellen Produktstand bytegeprÃ¼ft.
Dateien binÃ¤r Ã¼ber echten Git-Checkout oder Raw-Download aus diesem Belegcommit
abrufen; Bytezahl, SHA-256 und BildmaÃŸ gegen `manifest.json` prÃ¼fen und Originale
tatsÃ¤chlich Ã¶ffnen. GitHub-Vorschau oder leeres Contents-API-content bei >1 MiB
ersetzt keine geÃ¶ffnete BinÃ¤rdatei. Implementierersichtung erledigt R01 nicht.

## Aktuelle gemessene Profilbilanz

| Profil Â· fÃ¼nf gewÃ¤hlte Bilder | Quellbytes | Importbytes | PCK-Zuwachs Windows = Web |
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

Gemeinsame logische Leinwand 3072Ã—768, proportionaler Contain-Fit aller
2172Ã—724-Originale, mittig/unten; keine per-ID-Offsets oder Zuschnitte. Bei 1440p
Papierprojektion P(94,81481;66,37033), S(2370,37;2939,259); sichtbare Leinwand
P(296,5926;879,8519), S(2144,593;536,1481). Fensteranpassung bleibt vom Rasterzoom getrennt.

PNG-Optimierung war grÃ¶ÃŸer als die pixelgleiche Referenz-PNG. Verlustfreies WebP
spart Quellbytes, praktisch keine Import-/PCK-Bytes. Q85 und LA Ã¤ndern Bildwerte;
keine pauschale QualitÃ¤tsgleichheit. Native Image-Daten mit Mips (RGBA):
1536/2304/3072 = 3.145.720/7.077.844/12.582.904 Bytes; 2304 ohne Mips 5.308.416,
LA mit Mips 3.538.922. Transparenter Leerraum spart bei gleichen MaÃŸen nicht diesen Speicher.

PNG2304-Pillow-Quelldekodierung, Median aus sieben Versuchen je Bild: etwa
5,96â€“18,23 ms. TatsÃ¤chliche headless PCK-LadevorgÃ¤nge: etwa 7,91â€“18,51 ms,
einschlieÃŸlich Importtexturzugriff, ohne GPU-Upload. Native Besuche enthalten
Frames/Shader/Polling und sind kein reiner Decoderbenchmark. OS-Caches nicht geleert.
PNG2304-PCK-Zuwachs pro Stichprobenbild durchschnittlich 838.388 Bytes; **Hochrechnung**
fÃ¼r 100/300/500 Bilder: 83.838.800 / 251.516.400 / 419.194.000 Bytes.
Kein gelieferter Katalogumfang und kein allgemeines Budget. Gemeinsames Web-PCK
wird dadurch grÃ¶ÃŸer; lokales Bedarfsladen ist kein bedarfsgesteuerter Netzwerkdownload.

90-Frame-Stichprobe ohne VSync: Median A/B1/B2/C ungefÃ¤hr
2,397/2,304/2,395/2,301 ms; p95 2,752/3,230/5,686/4,434 ms. Reihenfolge/Warmup/
Gesamtspiel beeinflussen diese Werte: keine isolierte GPU-Zeit oder Nullkostenbehauptung.
TIME_PROCESS-Monitor wegen unplausibler Intervallwerte nicht als Framekosten interpretiert.
Drawcalls 771/771/771/772, TexturzÃ¤hler 256.817.931 Bytes in allen vier Modi;
VideozÃ¤hler A 273.073.471, danach 277.333.855 Bytes (kein isolierter Shadermehrbedarf).
301 Ãœbergangsframes: Spitzen Textur/Video/CPU 280.323.375/302.685.163/662.859.546 Bytes.
GesamtzÃ¤hler kehren wegen anderer Spiel-/Allocatorressourcen nicht exakt zur Baseline zurÃ¼ck.

## Entscheidungsvorlage und Grenzen

B1 ist die technische/gestalterische Tendenz des Implementierers: ruhiger unter
Raster und Hinweisen. A kann dichte Vegetation/Stadtlinien mit Funktionszeichen
konkurrieren lassen; B2 bleibt prÃ¤senter und bietet keinen belegten Vorteil gegen
AbschwÃ¤chung. C verdeckt vollstÃ¤ndig, erzeugt aber ein auffÃ¤lliges helles Rechteck
einschlieÃŸlich HinweisflÃ¤chen. Keine endgÃ¼ltige Produktwahl aus dieser Tendenz.
2304/PNG mit Mips ist der mittlere Versuchsstand. 1536 verliert bei 4K feinere
Striche; 3072 erhÃ¤lt mehr Originaldetail, erzeugt aber keine neuen Details aus der
2172er Quelle. Q85/LA und Mip-Verzicht bleiben QualitÃ¤ts-/Farb-/FilterabwÃ¤gungen.

Kuala Lumpur bleibt der stÃ¤rkste indirekte Motivhinweis; tatsÃ¤chliche Entdeckungs-
und Belohnungswirkung wurde nicht mit blind spielenden Personen gemessen.
EigentÃ¼merwahl ist konkret dokumentiert, keine Serien-/Workflowfreigabe.
Aufwand je Motiv: Tomate 3, Qualle 3, Hills 4 unabhÃ¤ngige Generierungen,
KL 7 Generierungen + 3 Alpha-Edits, Basilisk 3. Aktive Arbeitszeit unbekannt;
12 Generierungszeiten direkt erfasst, acht weitere und drei Editzeiten unbekannt.
Parallelzeiten nicht addieren; EigentÃ¼merwartezeit separat/unbekannt.

E1/E2/E4/E5/E7 sind als technische/kuratorische Versuchsergebnisse mit diesen
Grenzen geliefert; E3 hat konkrete Bildwahl, E6 eine begrenzte Empfehlung.
UnabhÃ¤ngiges R01 und die endgÃ¼ltige E1â€“E7-/Ãœbernahme-oder-RÃ¼ckbauentscheidung D01
bleiben offen. Keine Serienproduktion/Bestandsintegration. Folgefragen fÃ¼r
#489/#490/#491: Freigabe-/Herkunftsbindung, Kandidaten-/Revisionswahl und
deterministische Ableitungen/Wiederaufnahme. Diese Issues werden nicht geÃ¤ndert.

## Abschließende CI-, Windows- und Zugriffsprüfung

[Package CI 42627286101](https://github.com/venomenon328/picross/actions/runs/42627286101)
ist erfolgreich: docs/ci-required, 314 Werkzeugtests, native.catalog und regulärer
Windows-Build. Quellhead 535403d8, Testcheckout e69ee2b9; 582,625 s vor Upload,
keine technischen Erfolgsuploads. Einzelne pages-Dauer/Warnung wird nicht behauptet;
die Fortschrittsregel ist gezielt bis 900 s simuliert und mit echten Linux-
Prozessgruppen-Negativfällen geprüft. Originalquelle und kompakte Abschrift in
`reports/ci-summary.json`.

Das tatsächlich heruntergeladene CI-Windows-Artefakt 13678883964 wurde nativ mit
Grafikfenster gestartet (Exit 0, P1_START_OK, RTX 3070/OpenGL);
`reports/windows-start.json` und `logs/windows-start.log` binden Kommando,
Player-/PCK-Hashes und Dauer. Regulärer Katalog-/Ressourcenstart, kein Rätselreplay
oder OS-Pointer-/DPI-Nachweis. PCK des 15-Kandidaten-Spielers: 102.458.372 Bytes.

Zwei aktuelle Original-PNGs über 1 MiB sowie ein unverändertes CRLF-Prüflog wurden
frisch aus GitHub-Git-Blob-Binärdaten vollständig dekodiert, nach Größe/SHA-256/
Git-Blob-SHA geprüft und geöffnet. `reports/binary-access-current.json` bindet den
Belegcommit und die Bytes; der Harness zeigt den binärfähigen Abruf. Das ist eine
Implementierersichtung, kein unabhängiges R01.
