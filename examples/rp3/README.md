# Kleines Beispiel für Bildimport und Export

`source.png` ist eine eigene geometrische 640×640-RGBA-Illustration einer
Pilzkappe mit Stiel und transparentem Umfeld. `reveal.svg` ist die dazugehörige
eigene farbige Vektorillustration. Beide wurden aus geometrischen Formen für
dieses Repository erstellt, zur Bearbeitung und Weitergabe im Projekt;
keine Fremdassets oder fremden Lizenzansprüche.

[design.json](design.json) beschreibt den Import auf 20×20 Zellen mit vollem
Ausschnitt, `exact`, weißem Hintergrund, Alpha-Grenze 128 und dunklem `ink`.
Die Quelle dient außerdem als kleiner Eingang allgemeiner Reparaturtests.
Gespeicherte Produktionsresultate, Proofs und alte registrierte Exporte werden
hier nicht benötigt. Der [historische Demo-Stand](https://github.com/venomenon328/picross/blob/37f500d5e6599a6c8ff85c8ca8edb4d190474c5f/examples/rp3/README.md)
ist bei Bedarf separat abrufbar.

Nach Einrichtung der isolierten Pillow-Umgebung aus der
[Werkzeuganleitung](../../tools/puzzle_production/README.md), mit neuen Ausgabezielen:

```sh
python -m tools.puzzle_production import-image --input examples/rp3/source.png --design examples/rp3/design.json --output-dir artifacts/rp3-import
python -m tools.puzzle_production export-p1 --bundle artifacts/rp3-import --variant area-128 --reveal examples/rp3/reveal.svg --name Fliegenpilz --output-dir artifacts/rp3-export
```

Dieser alte quadratische Exportadapter ist ein technisches Formatbeispiel.
Neue Spielinhalte werden über [ZA-1](../../docs/ZA1_ADAPTER.md) und den aktuellen
[Authoringworkflow](../../docs/ai-workflows/PUZZLE_AUTHORING.md) freigegeben und
registriert. Das Beispiel erweitert weder den Spielkatalog noch die CI-Fallliste.
