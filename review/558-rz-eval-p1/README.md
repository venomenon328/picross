# RZ-EVAL-P1 · befristete Revieworiginale

Produkt-Head: `90aefb84dccd9e1cdcda73f03df113855b856857`, Draft-PR [#559](https://github.com/venomenon328/picross/pull/559).
Maßgeblich: [Paketentscheidung](https://github.com/venomenon328/picross/issues/558#issuecomment-6739323575).
Empfänger: unabhängiges R01 und Eigentümer-M01, danach D01. Bedarf/Rückbau spätestens
am **16.11.2026** neu prüfen. Dieser Ref wird nicht nach main gemergt; kein Dauerarchiv.
Die Frist ist ein benannter Prüf-/Rückbauendpunkt, kein automatischer Git-Löschmechanismus.

## Konkrete Kandidaten auf dem tatsächlichen Buchpapier

Jeder Link öffnet das unveränderte native 2560×1440-Original. Es ist keine Bildfreigabe.

| Rätsel | Kandidat 1 | Kandidat 2 | Kandidat 3 | Ohne Zeichnung |
| --- | --- | --- | --- | --- |
| Tomate | [c1](book/tomate-c1-1440-A.png) | [c2](book/tomate-c2-1440-A.png) | [c3](book/tomate-c3-1440-A.png) | [Referenz](book/tomate-c1-1440-A-without.png) |
| Qualle | [c1](book/qualle-c1-1440-A.png) | [c2](book/qualle-c2-1440-A.png) | [c3](book/qualle-c3-1440-A.png) | [Referenz](book/qualle-c1-1440-A-without.png) |
| Chocolate Hills | [c1](book/hills-c1-1440-A.png) | [c2](book/hills-c2-1440-A.png) | [c3](book/hills-c3-1440-A.png) | [Referenz](book/hills-c1-1440-A-without.png) |
| Petronas Towers | [c1](book/petronas-c1-1440-A.png) | [c2](book/petronas-c2-1440-A.png) | [c3](book/petronas-c3-1440-A.png) | [Referenz](book/petronas-c1-1440-A-without.png) |
| Stirnlappenbasilisk | [c1](book/basilisk-c1-1440-A.png) | [c2](book/basilisk-c2-1440-A.png) | [c3](book/basilisk-c3-1440-A.png) | [Referenz](book/basilisk-c1-1440-A-without.png) |

Kandidat 1 für Petronas und Chocolate Hills ist jeweils **rev2**. Die beiden
verworfenen Vorgänger bleiben unverändert unter `originals/`. Im Bohol-Vorgänger
waren ferne Hügelformen zu sehen; in der Ersatzfassung gibt es keinen Horizont.
Der zentrale Dreitürme-Aufbau wurde durch Eigentümerfeedback verworfen.
Keine Tomate, Qualle, Chocolate Hills, Petronas Towers oder Basilisk im gültigen Satz.

## Originale und Messwege

- `originals/`: 17 unveränderte ImageGen-PNGs, zwei verworfene Vorgänger, dazu transparenter Kontrollfall.
- `variants/`: gemeinsame 4:1-Ableitungen und explizite Qualitätsgegenproben; keine kreativen Zusatzkandidaten.
- `diagnostics-delivery/`: native A/B1/B2/C-Originale, echte Zoom-/Input-/Abbruchfolge,
  1080p/720p-UI125/4K/16:10, Seitenbewegung, pixelidentischer leerer Kontrollfall.
  `pixel-analysis.json`: außerhalb des Rasterrechtecks keine Pixeländerung zwischen Varianten;
  288 Zoomstichproben, eine feste Leinwand/Textur, kein Nachladen.
- `mono-originals/`: identischer Mono-Füll-/X-Stand in A/B1/B2/C; gleicher schwarzer
  Füllpixel, unveränderte Geometrie/Zellen, erstes Öffnen gegenüber Wiederöffnung.
- `profile-originals/`: native 1440p-/4K-Größen-, Format-, Alpha-/Filtergegenproben.
- `resource-originals/`: Speicherbeobachtung während tatsächlichem Öffnen/Rückweg,
  anschließend freigegebene Capture-/Illustrations-/Anfragereferenzen.
- `imports/`: 50 unveränderte CTEX-Dateien aus den tatsächlichen exportierten PCKs;
  Zuordnung, Bytes und Hashes in `reports/export-bindings.json`.
- `packs/`: unveränderte Baseline und PNG2304-PCK, um echten Exportzuwachs zu prüfen.
  Die Windows-/Web-PCKs sind in jedem Profil byteidentisch; deshalb keine Dubletten.
- `reports/`, `logs/`, `harness/`: unveränderte Laufberichte/Logs und der gezielte Einmalharness.
  Lokale Ausführungspfade im Harness sind Kontext, keine vorausgesetzten Reviewerpfade.

Bild-/Packdateien binär aus diesem Belegcommit abrufen, mindestens Bytezahl/SHA-256
gegen `manifest.json` prüfen und benötigte Originalbilder tatsächlich öffnen.
Ein echter Git-Checkout oder binärfähiger Raw-Download ist geeignet. GitHub-Vorschau,
leeres Contents-API-`content` bei >1 MiB, Hashliste und textgebundener Connector allein
ersetzen keine geöffnete Originaldatei. R01 wird durch die Implementierersichtung nicht erledigt.

`binding.json` nennt beide tatsächlichen Prüfstände und die enge Wiederverwendung:
Nach 232932f9 änderten sich nur Bohol-c1, Provenienz und Dokumentation. Alle Spiel-
und Shaderquellen, die übrigen 14 Bilder und die Profile-Gegenproben sind bytegleich.
Bohol-c1 wurde am aktuellen Produkt-Head neu aufgenommen; die finalen Exporte,
Mono-/Ressourcenproben gehören ebenfalls zu diesem Head. Keine alte Prüfung wird
als neue Ausführung ausgegeben.

## Gemessene Profilbilanz

| Profil (5 Referenzbilder) | Quellbytes | Importbytes | Windows-/Web-PCK-Zuwachs |
| --- | ---: | ---: | ---: |
| baseline | 0 | 0 | 0 / 0 |
| png-reference-2304 | 3,402,190 | 3,499,192 | 3,501,540 / 3,501,540 |
| png-1536 | 1,561,403 | 1,618,328 | 1,620,676 / 1,620,676 |
| png-2304 | 3,529,273 | 3,499,192 | 3,501,540 / 3,501,540 |
| png-3072 | 5,946,518 | 5,909,484 | 5,911,828 / 5,911,828 |
| webp-lossless-1536 | 879,762 | 1,618,328 | 1,620,684 / 1,620,684 |
| webp-lossless-2304 | 2,071,756 | 3,499,220 | 3,501,580 / 3,501,580 |
| webp-lossless-3072 | 3,536,330 | 5,909,496 | 5,911,852 / 5,911,852 |
| webp-q85-2304 | 1,206,306 | 3,183,732 | 3,186,076 / 3,186,076 |
| png-2304-no-mips | 3,529,273 | 2,483,530 | 2,485,860 / 2,485,860 |
| png-LA-2304 | 1,915,570 | 2,373,690 | 2,376,036 / 2,376,036 |

Quellbytes sind nicht Import-/Paketbytes. PNG-Optimierung war hier sogar größer
als die pixelgleiche Referenz-PNG. Verlustfreies WebP senkt Quellbytes, praktisch
nicht PCK/CTEX. Q85 und LA ändern Bildwerte; keine pauschale Gleichwertigkeit oder
Freigabe. 1536/2304/3072 haben als RGBA mit Mips nativ 3.145.720/7.077.844/12.582.904
Image-Datenbytes; 2304 ohne Mips 5.308.416, LA mit Mips 3.538.922. Transparenter
Leerraum spart bei gleicher Texturabmessung keinen solchen Speicher.

Ladezeiten unterscheiden Pillow-Quelldekodierung, headless ResourceLoader im
echten PCK und den nativen Besuch einschließlich Frame-/Shader-/Pollingzeit.
OS-Dateicaches wurden nicht geleert. Keine behauptete Kaltplattenmessung.
Native Gesamt-Speicherzähler enthalten das übrige Spiel und Captures, nicht nur
die Illustration. Keine isolierte GPU-Zeitmessung; Frameintervalle ohne VSync
sind eine kleine zeit-/reihenfolgeabhängige Stichprobe, kein Nullkostenbeweis.
Der rohe TIME_PROCESS-Monitor wird wegen unplausibler Intervallwerte nicht als
GPU-/CPU-Framekosten interpretiert. B1/B2 verwenden keine zusätzliche Textur oder
Renderfläche; C fügt einen Draw-Call hinzu. B2 führt neun lokale Textursamples aus.

Die Bildabnahme, tatsächliche Spoiler-/Belohnungswirkung und Serienwirtschaftlichkeit
sind offen. B1 ist die technische/gestalterische Tendenz des Implementierers.
A kann unter großen Rastern stören; B2 bleibt vergleichsweise präsent; C hat eine
auffällige helle rechteckige Papierfläche. Die gemeinsamen Hinweisflächen können
Kompositionen sichtbar gerade anschneiden. Das sind Nachteile für D01, keine
als gelöst ausgegebenen Bild-/Produktentscheidungen. Aktive Arbeitszeit unbekannt;
12 von 17 Generierungszeiten sind direkt protokolliert, fünf unbekannt. Parallele
Generierungszeiten nicht addieren; Eigentümerwartezeit separat/unbekannt.
