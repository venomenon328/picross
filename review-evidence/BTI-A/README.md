# BTI-A · befristete Originale für R01/M01

Produkt-Head: `51e58889583ccd6eeb40d21db1c09a0ff55a8433`.
Dieser reine Belegbranch `review/533-bti-a` zweigt direkt davon ab. Kein Merge-PR,
keine Übernahme der Belege in den Produktbranch. Empfänger: unabhängiger
BTI-A-R01-Reviewer und Eigentümer für BTI-A-M01 vor Merge.

Verfügbar bis **13.11.2026**. Danach im beauftragten Paketabschluss durch den
zuständigen Agenten zurücknehmen; bei noch offenem Review vorher Bedarf und
erneute Zustellung klären. Keine automatische Löschung oder dauerhafte
Verfügbarkeit durch diesen Text zugesagt. Produkt-PNGs bleiben Produktquellen.

## Originalsicht

[manifest.json](manifest.json) bindet Dateipfad, Bytezahl und SHA-256 für drei
Produktoriginale sowie diese aktuellen Belege. Die drei PNGs liegen unverändert
unter `game/art/drawing/view_titles/` im selben Commit; dort stehen auch
Produktmanifest und Herkunft. Der Stilbrief liegt unter
`docs/design/view_titles/STYLE.md`.

`catalog-`, `settings-`, `help-` jeweils mit folgenden Suffixen:

| Suffix | Tatsächliche Clientfläche | UI | Zweck |
| --- | --- | --- | --- |
| `1280x720-ui125.png` | 1280 × 720 | 125 % | enger Fallback |
| `1920x1080-ui100.png` | 1920 × 1080 | 100 % | primäre Referenz |
| `2560x1440-ui125.png` | 2560 × 1440 | 125 % | größere Referenz |

Zusätzlich `shipped-windows-catalog.png`: unveränderter exportierter
Windows-Spieler in seinem regulären 1920×1080-Fenster, isoliertes Profil,
Clientaufnahme über Windows PrintWindow; reguläres WM_CLOSE endet mit Code 0.
Kein Rätsel geöffnet, keine fremden Spielstände verwendet.

Die neun Matrixbilder sind unveränderte Godot-Viewport-PNGs unter Windows
mit NVIDIA RTX 3070/OpenGL. Reguläre `main.tscn`, echte Kamera-/Blattanimationen
und die tatsächlichen Windows-Anzeigecontrols; sechs synthetische Rätsel.
Für die programmatische Größenmatrix wurden ausschließlich im temporären
Prüfaufbau nach nativem Start Monitorpolling angehalten und Fensterdekoration/
Resize-Sperre entfernt, um Windows-Arbeitsflächenclipping bei 1440 Clientpixeln
zu vermeiden. Das ist kein Nachweis für Monitor-/Vollbildumschaltungen.
Die Inhalts-/Titel-/Navigationsimplementierung ist unverändert.

[native.json](native.json) enthält 250 erfolgreiche Assertions: alle drei
16:9-Größen × UI100/125, 1920×1200/UI125, Skalierungsrückweg, getrennte
Titel-/Scroll-/Navigationsbereiche, erreichbare Inhaltsenden, Kapitel-/Lesestände,
Fokus-/Zielnamen und echte Katalog-/Arbeitsursprünge. Mausereignisse werden an
das native Godot-Fenster geliefert; keine Behauptung physischer Mausbedienung.
Der einmalige Harness [native_titles.gd](native_titles.gd) ist nur hier abgelegt.
Die permanente `native.catalog`-Komponentenprüfung liefert zusätzlich die
Saveblockaden, Retry, Fallbacks und synthetischen Layoutregressionen.

[exports.json](exports.json) bindet die tatsächlichen lokalen Windows-/Web-PCKs
und die Windows-EXE. Beide PCKs wurden mit [pack_titles.gd](pack_titles.gd)
direkt geöffnet: alle drei Texturen mit exakten Maßen, Alpha und Mipmaps,
Titelmapping, Manifest und Herkunft vorhanden. Kein Webdeployment oder Chromium.

## Binärzugriff und Grenzen

Vom konkreten Belegcommit über `raw.githubusercontent.com/venomenon328/picross/`
oder Git binär laden, gegen das Manifest prüfen und anschließend öffnen.
Die Titeldateien und mehrere Aufnahmen überschreiten 1 MiB; ein textgebundener
Contents-API-Connector oder eine verkleinerte GitHub-Vorschau ersetzt die
Originalsicht nicht. Der im PR berichtete Rückdownload beweist den Abruf aus
der Implementierungsumgebung; jeder unabhängige Reviewer muss den eigenen
Zugang und seine tatsächliche Sichtprüfung bestätigen.

Sichtprüfung des Implementierers: exakte Wörter einschließlich Umlautpunkten
und doppeltem l, keine selbständigen Ornamente oder deckenden Rechtecke,
lesbar auf Papier, keine abgeschnittenen sichtbaren Züge, feste erreichbare
untere Aktionen. Die Alpha-Messung unterscheidet vollständig transparente,
teiltransparente und deckende Pixel; sehr schwache Generatorpixel können
außerhalb der deutlich sichtbaren Alphahülle liegen. Keine Retusche oder
Neukodierung der Produktoriginale. Dies ist T01-Selbstprüfung, **keine R01-
oder persönliche M01-Abnahme**.
