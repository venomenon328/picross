# RP-3: Bildimport, Vergleich und erster P1-Export

**Integrationsstand vom 05.10.2026:** RP-3/#37 ist nach unabhängigem technischem
und visuellem Review R2 über [PR #44](https://github.com/venomenon328/picross/pull/44)
als `aa9cc23244c60d647d8468a8d76a819f977e85a6` in `main` integriert. R2 bindet
den Quellhead `3a1a9386750b50568f63d8277cdf67b9d2884c2c`; keine offenen B-/A-Befunde.
Die folgenden Draft-/Gateangaben sind historische Entwicklungsnachweise.
Aktuelle Vergleichsproduktion: [RP4_VERIFICATION.md](RP4_VERIFICATION.md).

Historischer Stand: 04.10.2026 · #37 · damalige Implementierung im Draft

Auftrag ist der vollständige [Issue-Body #37](https://github.com/venomenon328/picross/issues/37)
einschließlich Umsetzungsvorbereitung vom 04.10.2026. Branch
`feat/37-image-import-p1-export`, Ziel `main`. Die Startprüfung hat aktuelle
Pflichtquellen und Änderungen seit
`742977ed17568f5f55f13b80b609687f93f1eb32` geprüft: der gefetchte Main entsprach
diesem Commit; kein vorhandener RP-3-Branch/PR und keine weiteren Bereichsregeln.
RP-2 ist nach Review über #43 integriert, Z2 über #33. Z2-M01/M02/M03 wurden nicht
durchgeführt und für ihren damaligen Merge als Gate aufgehoben.

## Akzeptanzzuordnung

| Kriterium | Ausführbarer Nachweis |
| --- | --- |
| RP3-A01 | `test_images.py`: alle acht EXIF-Orientierungen mit unabhängigen erwarteten Pixeln, JPEG/sRGB-ICC/defektes ICC/CMYK, Alpha/Leer/heller Vordergrund, Palette/Grau, beschädigte/trunkierte PNG/JPEG/Animation/Fremdformat; Bytes/Pixel/Quellachsen/Varianten/100er-Grenzen, Rechtecke/1D, acht Farben und realer 100×100-Dateiimport samt geschriebenem Proof. Deterministische Kandidat-/Logik-/Proof-/Rasterbytes. |
| RP3-A02 | Exakte Runhinweise aus festgelegten Matrizen, frisches unabhängiges Replay geschriebener Proofs; Manipulation von Matrix/Hinweisen/Schritten einschließlich neu gebundenem Dateihash scheitert. Fixpunkt/Abbruch bleiben vergleichbar, erlauben keinen P1-Export. Keine Bild-/Lösungsdaten im Logikeingang. |
| RP3-A03 | Eigene reale PNG-Datei und `production/index.html`, drei begrenzte Varianten, Parameter/Herkunft/Versions-/Dateihashes und Briefing. HTML-Metadaten werden escaped; feste lokale Dateinamen. Eigene Browser-Sichtkontrolle und dateibasierte Übergabe, keine allgemeine Motivqualität. |
| RP3-A04 | `rp3_demo` importiert die reale Datei neu, rekonstruiert das eingecheckte Bundle und prüft alle Export-/Assetbindungen bytegenau gegen registriertes F-04. `rp3_probe.gd` lädt die reguläre Hauptszene, wählt F-04 über echte Viewport-Ereignisse, bearbeitet und schließt den neuen Inhalt ab. |
| RP3-A05 | Drei getrennte isolierte Prozesse `partial`/`finish`/`read`: Teilstand, History, Undo/Redo, Abschluss und Wiederherstellung samt Album. Eigene falsche Miniaturzelle; Name/Reveal bis zum letzten Commit verborgen. Andere Slots bleiben unverändert; feste IDs/Pfade. Native Arbeits-/Abschluss-/Albumrenders, zwei Client-/UI-Kombinationen. Alte F-01/F-02-Dateien/Proofs/Bilder und F-03 erhalten. |
| RP3-A06 | 56 gemeinsame Fachtests einschließlich 20 Bildtests; bestehende Werkzeug-/Dokumenttests, vollständiger Diffcheck, unverkleinerter Benchmark und Produkt-/Preflightweg bleiben aktiv. Aktuelle CI mit Windows-ZIP und genauer Head-/Basis-/Test-Merge-/Artefaktbindung im Draft-PR. Unabhängiges technisches/visuelles Review separat offen. |

## Reproduktionsweg und Grenzen

Pillow exakt 12.3.0 aus [requirements-image.txt](../tools/puzzle_production/requirements-image.txt)
in isolierter venv. Der Kern bleibt Standardbibliothek; ein gesperrter PIL-Import
im Test bestätigt das. Vollständiger Entwurfs-/Normalisierungs-/Hash-/CLI-Vertrag
und Installation stehen in der [Werkzeuganleitung](../tools/puzzle_production/README.md).
Quelle, Rechte und neue eigene Enthüllung: [examples/rp3](../examples/rp3/README.md).

```sh
python -m tools.puzzle_production.rp3_demo --output-dir artifacts/rp3-demo
python -m unittest discover -s tests/puzzle_production -p 'test_*.py' -v
python -m tools.puzzle_production.benchmark --output-dir artifacts/puzzle-production
python -m unittest discover -s tools -p 'test_*.py' -v
python tools/check_docs.py
python tools/p1_product.py --cache-dir <externer-cache> --output-dir artifacts/p1-product
git diff --check <basiscommit> <head>
```

Import: PNG/JPEG bis 32 MiB/8 Millionen Pixel/8192 je Achse, acht Varianten,
Ziel 1..100 je Achse und acht Vordergrundfarben plus Leer. Kein verstecktes
Strecken, keine dynamische Filter-/Modellintegration. P1-Adapter ausschließlich
quadratisch monochrom, F-04 und lokales SVG; andere Fälle werden klar abgewiesen.
Keine freie Save-/Definitionspfadableitung, Migration oder öffentliche Import-UI.

Pillow-Wheels bündeln unter Windows/Linux unterschiedliche JPEG-ABI-/zlib-Stände.
Ein Replay mit derselben Werkzeug-/Pillowversion behält die Produzentenidentität
und fordert exakt gleiche neu normalisierte RGBA-Pixel, Metadaten und Raster.
Abweichende Pixel oder Pillowversion scheitern im gezielten Cross-build-Test.
Der Demonstrationsbericht weist ursprüngliche/neue Kennung und beide Codecstände
separat aus; Definition und Reveal müssen bytegleich bleiben.

Der Export liest Original und Normalisierung erneut, prüft Dateibindungen,
rekonstruiert den Kandidaten, erzeugt Hinweise aus der Matrix und replayt den
**geschriebenen Proof** unabhängig. Nur `solved` und identische Singleton-
Enddomains erlauben den Export. Flags/Exitcode sind kein Ersatz. Reine RGB-/
Assetänderungen und Logikänderungen bleiben verschiedene Bindungen; keine
automatische redaktionelle Freigabe aus einem Zertifikat.

## Lokale Entwicklung und Sichtbefund

Lokale Fachprüfung am 04.10.2026: 55 Tests erfolgreich. Die eigens verifizierte
offizielle Godot-4.7.2-Windows-Engine lief in temporärer Projektkopie und
isoliertem APPDATA-/LOCALAPPDATA-Profil. Drei frische Prozesse meldeten
`RP3_PARTIAL_OK` (12 Checks), `RP3_FINISH_OK` (15) und `RP3_READ_OK` (9);
OpenGL-Capture meldete `RP3_CAPTURE_OK`. Dies sind Entwicklungsnachweise am
veränderten Arbeitsbaum, keine finale CI-/Commitabnahme.

Die echte Quell-/Vergleichsansicht zeigt eine breite Kappe und mittigen Stiel;
Flächenraster sind als einfache Pilzsilhouette lesbar, die Konturvariante bleibt
gesondert sichtbar. Der gewählte F-04-Kandidat hat 49 Schritte und 89 geprüfte
Linien. Die verfeinerte Enthüllung erhält Hauptproportionen und ergänzt rote
Farbe, Punkte und Schattierung. In der nativen Arbeitsansicht stehen ausschließlich
„Blatt 04“ und Größenangabe; der absichtlich falsche eigene Eckpixel erscheint
auch in der Miniatur. UI 100 % bei 1920×1080 und UI 125 % bei 1280×720 sind
lesbar, ohne abgeschnittene Arbeitsaktionen. Der letzte Zellcommit öffnet den
Abschluss mit Raster/Illustration; Album vor/nach Abschluss zeigt jeweils eigenen
Stand beziehungsweise erworbenes Bild. Kein allgemeines Qualitäts-/DPI-Urteil.

Aktuelle CI erzeugt `rp3/rp3-report.json`, frisches Produktions-/Exportbundle,
`renders/rp3-renders.json` und fünf `rp3-*.png` im Produktartefakt. Berichte binden
Source-Head, getesteten Checkout/Test-Merge, Basis, Run und tatsächliche Dateien.
Windows-ZIP/EXE-Hashes stehen im `product-report.json`. Der PR dokumentiert die
finalen CI-Runs, Artefakthashes, ausgeführte Schritte und getrenntes Selbstreview.
Linux-CI baut Windows, führt aber keinen Windows-Start aus. Ein lokaler Editor-
Renderlauf ist ebenfalls kein Start der exportierten Windows-EXE.

## Historischer Abnahmestand vor Review R2

Unabhängiges technisches und visuelles Review am benannten finalen PR-Stand bleibt
**offen** und Teil RP3-A06. Eigenes Selbstreview ersetzt es nicht. Eine echte
Eigentümer-Lösung ist ausdrücklich RP-6-Gate; sie wurde hier nicht durchgeführt.
Kein Merge, Release oder Schließen von Parent #34. RP-4/RP-5/RP-6 bleiben separate
Pakete; kein automatischer perfekter Fotoimport und keine Pilotfreigabe behauptet.
