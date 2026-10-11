# PERF-A · reproduzierbare Entwicklergrundlage

[Vertrag und Ergebniszuordnung](../../docs/PERF_A_IMPLEMENTATION.md),
[Messplan](plan.json), [Herstellungsparameter](atlas-plan.json).
Kein Eigentümersave und keine Behebung von PERF-01 durch A.

## Prüfpfade

Die offizielle Godot-4.7.2-Standard-Windows-ZIP aus dem vorhandenen externen Cache
wird vor jeder Nutzung erneut gegen den im Preflight gepinnten SHA-256 geprüft.
Alle nativen Prozesse erhalten temporäre Projekte und eigene Benutzerprofile;
das Prozesslimit bleibt 300 Sekunden. Die Originalrenderer werden aus dem
gepinnten Git-Commit archiviert, niemals im Arbeitsbaum zurückgesetzt.

```powershell
python tools/perf_a.py baseline --cache-dir "$env:TEMP/picross-rp6-cache" --output-dir artifacts/perf-a-baseline-new
python -m venv .venv/perfa
.venv/perfa/Scripts/python.exe -m pip install --only-binary=:all: -r tools/puzzle_production/requirements-image.txt
.venv/perfa/Scripts/python.exe tools/perf_a_atlas.py generate --cache-dir "$env:TEMP/picross-rp6-cache" --output-dir artifacts/perf-a-manufacture-new
.venv/perfa/Scripts/python.exe tools/perf_a_atlas.py derive --output-dir artifacts/perf-a-stored-source-new
.venv/perfa/Scripts/python.exe tools/perf_a_atlas.py verify
.venv/perfa/Scripts/python.exe tools/perf_a_atlas.py probe --cache-dir "$env:TEMP/picross-rp6-cache" --output-dir artifacts/perf-a-probe-new
.venv/perfa/Scripts/python.exe -m unittest discover -s tools -p test_perf_a_atlas.py -v
```

Jeder Ausgabeordner muss neu sein. `generate` braucht natives Windows/OpenGL und
das Quellobjekt aus `atlas-plan.json` im Git-Objektspeicher. `derive` rekonstruiert
die PNGs allein aus gespeicherten Basisbildern mit Pillow 12.3.0 und verlangt
exakte Dateiidentität. `verify` prüft zusätzlich Original-/Derivat-/Import-/
Hersteller-/Vertragshashes, jedes Zeitbild und die räumlichen Oracles.
`probe` führt zwei native Prozesse mit identischer Variantenliste aus; der zweite
prüft den tatsächlichen Neustart. Normale Spielstände werden nicht gelesen.
Der Farb-/Alphaoracle rechnet unabhängig aus den gespeicherten Schwarz-/Weiß-
Originalen. Zusätzlich muss der frisch gezeichnete Windows-Stift pixelnah passen;
frische Polygonraster anderer GPU-Treiber sind separat ausgewiesene Diagnosen,
keine versprochene plattformübergreifende Rasterpixelidentität.

## Anschluss für PERF-B

Die drei Auflösungsstufen enthalten je einen Füll- und X-Atlas; Zeitbilder liegen
horizontal, Varianten vertikal. `manifest.json` bindet jedes Rechteck, seine
Alpha-Hülle und den dekodierten Pixelhash. Gespeicherte Schwarz-/Weiß-Basisbilder
stammen aus dem Projektstiftzeichner, keine fremden Bildquellen.

Der Entwicklerhelfer `prototypes/p1/perf_a/atlas.gd` definiert stabile Identität,
Zeitindex und Innenflächenabbildung. Bei wartenden Zielen oder statischer Vorschau
Endframe 23 derselben Variante mit 56 % Deckung wählen; aktives Schreiben verwendet
den Zeitindex ohne Unterzeichnung. Farbe ist ein unabhängiger Materialparameter.
X verwendet die bestehende Stiftfarbe `#343f42`; dessen 60-%-Strichalpha steckt
bereits in der Maske. Vorschaualpha nicht versehentlich nochmals pro Zug aufbauen.
Die Füllmaske verwendet `RGB = Grundfarbe × R + Weiß × G`, `Alpha = A × Deckung`.
Sie braucht das gebundene Material, keinen Grauwert-Tint.

Füllungen bilden die Quellinnenfläche auf `Zellrechteck.grow(-2)` ab. Die daraus
abgeleitete Außenbox darf von der logischen Zellbox abweichen; transparentes
Padding ist kein zusätzlicher Innenabstand. X verwendet das logische Zellrechteck.
Linear filtern, nicht wiederholen, keine Mipmaps oder verlustbehaftete Kompression;
Maskenkanäle als Daten ohne `source_color`-Konvertierung laden. Der Farbparameter
des Shaders trägt dagegen den Farbhinweis. Koeffizienten werden zwei Pixel in
transparenten Rand fortgesetzt, Alpha niemals. Region und Clip bleiben gebunden.

Der aktuelle Export schließt `perf_a/*` vollständig aus. B muss die benötigten
Ressourcen ausdrücklich in seinen aktiven Laufzeitbestand übernehmen und das
tatsächliche PCK erneut prüfen. Gemeinsame Texturen/Materialien wiederverwenden;
Generator, Originale, Probe und Galerien bleiben Entwicklerdaten. Regulärer
Renderer, Cache-/Effektlebenszyklen und Miniatur sind kein Teil dieser A-Probe.
