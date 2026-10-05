# RP-3: reale eigene Bildquelle und F-04

Stand: 04.10.2026 · versioniertes Dateibeispiel, technischer Durchstich

`source.png` ist eine tatsächlich vorhandene 640×640-RGBA-Datei: eine breite
Pilzkappe mit mittigem Stiel und transparentem Umfeld. Die einfachen geometrischen
Formen wurden für diesen Auftrag mit dem eigenen [Quellskript](create_source.py)
gezeichnet, ohne Fremdasset, Foto, KI-Modell oder injizierte Rätselmatrix.
Das Skript erzeugt ausschließlich Bildpixel; der echte Import erzeugt Matrix und
Hinweise. Nutzungsgrundlage: eigene geometrische Illustration dieses Repositorys,
zur Bearbeitung und Weitergabe im Projekt erstellt; keine fremden Lizenzansprüche.

[design.json](design.json) dokumentiert die vorlagentreue Übertragung auf 20×20,
vollen Ausschnitt, `exact`, weißen Hintergrund, Alpha-Grenze 128 und dunkles `ink`.
Zwei Flächenvarianten 128/160 und eine Konturvariante 40 werden ausgewertet.
Alle drei gespeicherten Spuren erreichen vollständig geprüfte Enddomains.
Gewählt ist `area-128`: 49 Deduktionsschritte, 89 unabhängig geprüfte Linien.
Die Auswahl ist der begrenzte RP-3-Demonstrationsfall, keine allgemeine
Motiv-/Schwierigkeits-/Pilotabnahme.

[reveal.svg](reveal.svg) ist eine eigene 640×640-Vektorillustration: rote Kappe,
helle Punkte, verfeinerter Stiel und Boden. Kappenbreite, Position und mittiger
Stiel stimmen mit dem Raster überein; Farbe/Details verfeinern das monochrome
Motiv. Sie wurde für diesen Auftrag aus eigenen SVG-Formen erstellt, ohne
Fremdassets. Sie entspricht bytegenau `prototypes/p1/art/f04.svg`.

Produktionsansicht mit Motivspoiler: [production/index.html](production/index.html)
offline im Browser öffnen. Original/Normalisierung, echte Zellauflösung,
vergrößerter Vergleich, alle Hinweise, Parameter, Herkunft, technische Status,
Hashes und Briefing liegen daneben als Dateien für ChatGPT/Codex.
[production/manifest.json](production/manifest.json) bindet diese Dateien;
[p1-export/manifest.json](p1-export/manifest.json) bindet unabhängigen Proof,
Logik, F-04-Definition/Revision und Reveal. Laufzeiten sind Messwerte des
ursprünglichen Imports, keine reproduzierbaren Identitätsbestandteile.

| Bindung | SHA-256 |
| --- | --- |
| Original `source.png` | `79e40044c083443b171041b4d2d0699714d9c7b3a027f9eded850c3703471bc1` |
| F-04-Definition | `c575bd448f736045da13dd5553550f5154e1215d2eac743806245b776a7d4587` |
| Reveal-SVG | `602b5fa22cec2255292e209afb0a64c1d696aa5cd711c9d4b21044263bf1b15a` |
| normalisierter Logikhash `area-128` | `a0bee43d6172dc6076bcbe0ecab3ba773bb19a121a85bada5351db6e10eb49dd` |

Die vollständige Kandidatenkennung steht im Manifest; sie umfasst zusätzlich
Entwurf, Matrix und Werkzeug-/Codecversionen. Neue Ausgabeziele verwenden:

```sh
python -m tools.puzzle_production import-image --input examples/rp3/source.png --design examples/rp3/design.json --output-dir artifacts/rp3-import
python -m tools.puzzle_production export-p1 --bundle artifacts/rp3-import --variant area-128 --reveal examples/rp3/reveal.svg --name Fliegenpilz --output-dir artifacts/rp3-export
python -m tools.puzzle_production.rp3_demo --output-dir artifacts/rp3-demo
```

Vorher die isolierte Pillow-Umgebung aus der [Werkzeuganleitung](../../tools/puzzle_production/README.md)
einrichten. `rp3_demo` prüft frische und eingecheckte Produktionsdateien sowie
bytegleiche registrierte Definition/Assets. P1 lädt F-04 ausschließlich aus seiner
festen Registrierung; Name/Illustration erscheinen erst nach Abschluss.
[RP3_VERIFICATION.md](../../docs/RP3_VERIFICATION.md) beschreibt echte Spiel-/Render-
und Neustartnachweise. Unabhängiges technisches/visuelles Review bleibt offen;
reale Eigentümer-Lösung ist RP-6-Gate. Kein Merge/Release, Parent #34 bleibt offen.
