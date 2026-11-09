# RAND-P1: befristete Revieworiginale

Produkt-Head: `2647c79e5d633b9e0a24e02aa0a445172578c524`.
Basis: `cbe71057c66ff6ac0b11f30f8edd5792850401c6`.
Produkt-PR: [#557](https://github.com/venomenon328/picross/pull/557).
[Paketentscheidung](https://github.com/venomenon328/picross/issues/550#issuecomment-6729097692),
[Eigentümerpräzisierung und isolierte Desktopfreigabe](https://github.com/venomenon328/picross/issues/550#issuecomment-6729305267).

Empfänger sind der nachfolgende unabhängige technische/visuelle Reviewer für
**RAND-P1-R01** und der Eigentümer für **RAND-P1-M01**. Beide Gates bleiben offen.
Der Implementierer hat Originale geöffnet und einen Selbstreview durchgeführt;
das ist keine unabhängige oder persönliche Abnahme. Diese Dateien gehören nur
auf `review/550-rand-p1`, nicht in den Produkt-PR oder nach main.

Endpunkt: R01/M01, Bedarf spätestens **2026-11-16** erneut prüfen. Der Ref läuft
nicht automatisch ab. Nach erfülltem Zweck beauftragten Belegref entfernen;
bei noch offenen Gates Zustellung/Aufbewahrung gezielt neu entscheiden. Die
aktiven Produktillustrationen und ihre Herkunft bleiben im Produkt erhalten.

## Tatsächliche Ausführung

Godot Standard `4.7.2.stable.official.ed1daf0bf`, native Windows-Ausführung,
OpenGL3 auf NVIDIA GeForce RTX 3070, regulärer **Window-Framebuffer**.
Unverändertes `main.tscn` mit `book/main.gd` und normaler Echtzeituhr; kein
synchron stabilisierender Komponentenroot. Die Captures stammen aus dem
tatsächlichen Spielrenderer, nicht aus montierten Mock-Screenshots.
Die 70 tatsächlich verwendeten Produktquellen/aktiven Assets stimmen
bytegleich mit dem Produkt-Head überein: [sources.json](sources.json).

Ausschließlich synthetische Testkataloge/-definitionen und isolierte Saveprofile.
Die beiden Referenzblätter verwenden denselben synthetischen 20×20-Monofall
unter unterschiedlichen Kategorie-IDs. Großfall: synthetischer 50×50-Farbfall;
Überlappung: synthetischer 40×30-Monofall. Keine echten Katalogrätsel gelöst,
keine echten Benutzersaves berührt. Die Inputprüfung schickt echte Godot-GUI-
Pointer-/Wheel-Ereignisse in das native Fenster; **keine physische OS-Mausprobe**.
Eine persönliche Erprobung am regulären Windows-Spieler bleibt M01.

79 erfolgreiche native Assertions in [native.json](native.json) und
[native-extra.json](native-extra.json). 30 unveränderte PNGs, 75.241.190 Bytes.
[manifest.json](manifest.json) ordnet Auflösung, UI-Skala, Zoom und SHA-256 zu;
die Records enthalten außerdem Papier-, Raster-, Hinweis-/Text- und Motivgeometrie.
Elf Mit-/Ohne-Paare behalten exakt dieselbe Geometrie. Der separate Pixelvergleich
findet bei keinem Paar einen veränderten Pixel außerhalb der Motivbereiche
(zwei Pixel AA-Reserve). Bei weggefallenen Motiven sind beide Bilder pixelgleich.
Keine Neuaufnahme, Skalierung oder Umkodierung der Originaldateien.

## Direkte Sichtung der Originale

| Zweck | Mit Zeichnung | Ohne Zeichnung |
| --- | --- | --- |
| P1-K2 Wasserwelt, 1920×1080/UI100, Zoom 24 | [Original](water-1080-ui100-with.png) | [Original](water-1080-ui100-without.png) |
| P1-K2 Wasserwelt, 2560×1440/UI100, Zoom 24 | [Original](water-1440-ui100-with.png) | [Original](water-1440-ui100-without.png) |
| P1-K2 Landschaften & Natur, 1920×1080/UI100, Zoom 24 | [Original](nature-1080-ui100-with.png) | [Original](nature-1080-ui100-without.png) |
| P1-K2 Landschaften & Natur, 2560×1440/UI100, Zoom 24 | [Original](nature-1440-ui100-with.png) | [Original](nature-1440-ui100-without.png) |
| P1-K3 lange Hilfe, 1920×1080/UI100 | [Original](help-1080-ui100-with.png) | [Original](help-1080-ui100-without.png) |
| P1-K3 lange Hilfe, 2560×1440/UI100 | [Original](help-1440-ui100-with.png) | [Original](help-1440-ui100-without.png) |
| P1-K3 enge Hilfe, 1280×720/UI125, beide entfallen | [Original](help-720-ui125-tight-with.png) | [Original](help-720-ui125-tight-without.png) |
| P1-K4 50×50, 1280×720/UI125, Zoomwunsch 72/Fit 8,68, beide entfallen | [Original](large-720-ui125-high-zoom-with.png) | [Original](large-720-ui125-high-zoom-without.png) |
| P1-K4 50×50, 2560×1440/UI125, Zoomwunsch 72/Fit 20,97 | [Original](large-1440-ui125-high-zoom-with.png) | [Original](large-1440-ui125-high-zoom-without.png) |
| P1-K4 50×50, 1920×1080/UI100, Wunsch 72/Fit 15,49, nur links entfällt | [Original](independent-work-with.png) | [Original](independent-work-without.png) |
| Eigentümerpräzisierung: 40×30, 2560×1440/UI100, Zoom 37, geringe Überlagerung rechts | [Original](shallow-grid-overlap-1440-ui100-with.png) | [Original](shallow-grid-overlap-1440-ui100-without.png) |

Weitere gezielt ausgewählte Originale:

- Hoher zulässiger Zoom auf den Referenzblättern: [Wasserwelt](water-1440-high-zoom.png), [Natur](nature-1440-high-zoom.png).
- Kapitelwechsel/Scrollen: [Bedienung gescrollt](help-1440-ui100-scrolled.png); [nach tatsächlichem Einstellungenpan zurück](help-1440-return.png).
- Reale Buchbewegung: [Frame während Hilfe→Einstellungen](help-settings-pan-moving.png). Die Zeichnung steckt in derselben Capturehierarchie und bewegt sich auf dem Papier; der linke Teil bleibt an der rechten Hilfeseite, kein ortsfestes Overlay.
- Unveränderte belegte Ansichten: [12/12-Katalog UI100](catalog-1440-ui100.png), [Katalog UI125](catalog-1440-ui125.png), [befüllte Einstellungen](settings-1440-ui100.png).

Die sechs Illustrationsoriginale liegen bereits bytegleich in diesem vom
Produkt-Head abgezweigten Ref unter
[game/art/drawing/margins](../game/art/drawing/margins).
[Provenienz mit vollständigen Prompts, Alpha-/Maß-/Hashangaben und Auswahlstatus](../game/art/drawing/margins/provenance.json).
Built-in ImageGen über den tatsächlich gelesenen ImageGen-Skill, sechs
eigenständige Aufrufe, `transparent_background=true`; Modell/Seed nicht exponiert.
Originalbytes unverändert. Atlasregionen beschneiden nur die leeren Außenränder
bei der Darstellung; zur Laufzeit 48 % Deckkraft. Keine geometrischen Ersatzbilder,
keine übernommene UI aus den Gesprächsmocks. Alle Fassungen bleiben Pilotkandidaten.

## Selbstreview und Grenzen

Im tatsächlichen Papiervergleich sind die offenen Konturen und unterschiedlich
dichten Graphitdetails erkennbar, während Raster/Zahlen und Text deutlich führen.
Die kleine Hilfestift-Komponente ist im festen Registerrest schmal; die endgültige
Wirkungs-/Motiventscheidung dazu bleibt ausdrücklich M01. Im gezielt erzeugten
geringen Rasterüberlappungsfall bleibt die Zeichnung sehr blass; der vorhandene
Untergrund genügt in diesem geprüften Fall, deshalb kein zusätzlicher deckender
Rasterhintergrund. Dichte Fälle und harte UI-Flächen unterdrücken Komponenten.
Dies ist keine Behauptung vollständiger Überschneidungsfreiheit aller Rätsel/Zooms.

Commit/Undo, Wiederöffnung, Kapitelwahl, Wheel, Einstellungenrückkehr und reale
Bewegungen bestehen; Zeichnungsauswahl bleibt stabil. Ohne Zeichnung identische
Funktionsgeometrie; Saves/Registryfelder werden nicht erweitert. Im Produktdiff
stehen ausschließlich die sechs benutzten Runtime-Originale, kleine Buchintegration,
Herkunft/Exportnotizen, gezielte Tests und passende Normfortschreibung.

Der lokale kleine Python-CI-Vertrag lief unter Windows 14/15 erfolgreich. Der
einzige Fehlschlag ist der **unveränderte Main-Windows-Pfadfall** in
`test_core_growth_and_test_changes_need_a_decision`: `CORE_PATHS` enthält dort
wegen Backslashes einen absoluten statt relativen Pfad. Am Originalcode aus
`main@cbe71057` gesondert bestätigt; kein RAND-P1-Produktfehler und keine
stillschweigende Umgehung. Der reguläre Linux-`docs`-Check läuft am Produkt-Head
einschließlich genau dieser Vertragstests erfolgreich. Keine zentrale CI-Reparatur
in diesen begrenzten Produktauftrag aufgenommen.

Die erforderlichen Kern-/Modulergebnisse und der Windows-Spieler stehen im
Produkt-PR, getrennt von diesen einmaligen Belegen. Die folgenden Textinputs
erläutern die tatsächliche Belegproduktion, bilden keine neue Dauertestfamilie:
[Buchprobe](inputs/rand_visual.gd), [ergänzte enge/Überlappungsprobe](inputs/rand_extra.gd),
[isolierter Runner/Fixtureaufbau](inputs/run_visual.py), [unabhängiger Pixel-/Dateileser](inputs/verify_native.py).

## Binärer Zugang und Rückbau

Die im PR verlinkte unveränderliche Beleg-SHA auschecken oder die konkreten
Dateien von dieser SHA binär herunterladen. [inventory.json](inventory.json)
bindet Dateipfad, Bytes und SHA-256; danach die PNGs selbst öffnen. GitHub-HTML,
Hashlisten oder verkleinerte Vorschauen allein ersetzen R01 nicht. Der
normale textgebundene Contents-Connector kann bei Dateien über 1 MiB leeren
Base64-Inhalt liefern; dafür Git-Checkout oder einen binärfähigen Raw-Download
verwenden. Der Implementierer prüft den veröffentlichten Git-Abruf und öffnet
die zurückgelesenen Originale vor der Übergabe. Zugriff im eigenen Konto ist
kein behaupteter Zugriffstest mit den Zugangsdaten eines fremden Reviewers.
