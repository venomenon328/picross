# KB: kompakter Katalog und gemeinsame Buchbuttons

Auftrag [#168](https://github.com/venomenon328/picross/issues/168), Startbasis
`9badc913adfdb63d5f4383163083a53068dbab64`, Branch `feat/168-katalog-buttons`, Ziel `main`.
Der aktuelle Issue-Body einschließlich Umsetzungsvorbereitung V1 bleibt die
vollständige Paketquelle. Die bestätigten Entscheidungen KB-D01–D05 erweitern
gezielt KAT-2 und den bisherigen Buttonstil; historische Lieferberichte bleiben.

## Umsetzung und Bindungen

`catalog.gd` berechnet die Spalten aus der tatsächlichen Scrollfläche einschließlich
Scrollbalkenreserve und 12 × UI Abstand. Karten bleiben bei 220–240 × UI Breite;
wenige Einträge und die letzte Reihe wachsen nicht über dieses Ziel. Mehr Höhe
folgt umbrochenem Text. Blattkennung und Motivname enthalten keine wiederholten
Dimensionen. Dekoration ignoriert Pointer, eigene Play-/Reset-/Recoverycontrols
verbrauchen ihre Ereignisse; alle Ziele bleiben stabile Registry-IDs.

`BookButton` bleibt die gemeinsame Komponente, einschließlich Textvarianten und
unveränderter Originalfarbflächen. Konturen hängen an Elementidentität, Zustände
zeichnen unmittelbar neu. Katalogcontrols behalten nativen Fokus. `BookTooltip`
nutzt die native Tooltipplatzierung mit begrenzter Textbreite, UI-skalierter
Schrift und Papierkontur; Layout-/Ansichtswechsel blenden alte Popups aus.
Das unabhängige HF-Overlay und die Board-/Sidebargeometrie bleiben erhalten.

Play/Reset sind eigene lokale Pfade in `tools/book_icons_kb.json`, mit separater
`game/art/book/KB-168-NOTICE.txt`. Die aktiven 13 Icons, SVG-Bytes, Font-/Buchhashes
und vollständiges Manifest werden durch `z2_resources.py` provisioniert/geprüft.
Die historische BP-3-Quellcommitkennung bezeichnet weiterhin nur dessen Bestand;
KB-Herkunft steht gesondert im Manifest. Keine Font-/Buch-/Rahmenbytes geändert.

## Technische Prüfzuordnung

| Akzeptanz | Tatsächlicher Prüfweg |
| --- | --- |
| A01/A02 | `kat2_probe.gd`, Modus `kb`: originale Bakso-Glyphen, drei gemeinsame Flächen, gemessene Breiten/Spalten/Innenrechtecke, einmalige Dimensionen, ein gefilterter Eintrag, UI-Rundweg; reguläre KAT-2-Proben ergänzen lange Kategorien, Abschlussnamen und 300 Einträge mit letzter Restseite. |
| A03/A04 | Native Viewport-Down/Up für Karte/Play/Reset, Abbrechen und Bestätigen, Filter und spätere Seite mit gebundener Dialog-ID; Neu/Leersave/Redo/Gelöst/Fehler/Recovery und tatsächlicher Prozessneustart im bestehenden KAT-2-Weg. Keine Signalaufrufe als alleiniger positiver Bedienbeleg. |
| A05/A06 | KB rendert Zustandsunterschiede und Fokus, stabile Wiederholungszeichnung, echte Hovertooltips und Seitenwechsel; 44/55-Treffer, 2×3-Werkzeuge, ZR-Up über Undo. Bestehende Save-/Recovery-/Flush-/500er-/Mehrprozess-, HF-/Palette-/Fit-/Pixel-/PERF-B-Regressionen bleiben ausgewählt. |
| A07 | Provisionierungswiederholung, Hash-/Inventar-/Korruptionsgegenproben; `content_pack_probe.gd` lädt die beiden importierten Texturen und prüft Inventar/Manifest/Herkunft im tatsächlichen Windows- und Web-PCK. Native Spielerstarts werden separat gebunden. |
| A08 | Vollständiger Diff, aktuelle ausgewählte Pflicht-CI samt Web/Preflight und `ci-required`; native Originalausschnitte mit Messdaten, gleich skalierter Altvergleich, Head/Basis/Checkout/Run und getrenntes Selbstreview im Draft-PR. |

`tools/kat2_product.py` führt KB mit den bestehenden festen synthetischen Inputs
in isolierten Projekt-/Saveprofilen aus und nimmt die kompakten Originalbilder
und Messdaten ins technische Product-Artefakt auf. Vollständige Framekontexte
bleiben lokal. Fensterclient, SubViewport/Framebuffer und physische Windows-
Skalierung sind unterschiedliche Messwerte. Keine Tests je Produktionsrätsel.
Web verwendet weiterhin echte Chromium-/Firefox-/Persistenz- und isolierte
SSH-/HTTP-Referenzprüfungen; kein realer Serverkontakt.

## Gates

Konkrete Ergebnisse und Dateihashes werden im Draft-PR an den finalen Stand
gebunden; dieses Dokument nimmt keinen Erfolg vorweg. KB-T01 verlangt die
technische Lieferung vor Übergabe/Implementierungsmerge. KB-R01 bleibt ein
unabhängiges technisches und visuelles Review vor Merge; Selbstreview ersetzt es
nicht. KB-M01 bleibt die persönliche Eigentümerprobe vor Merge am gebundenen
Windows-Spieler: Titel, Dichte, Lesbarkeit, Buttons/Tooltips bei UI100/125,
Karte/Play/Resetabbruch und bestätigter Reset nur im isolierten Profil,
Fortsetzen/Rückkehr und sechs Werkzeuge. Client-/Windows-/UI-Skalierung notieren.
Kein Merge, Release, Deployment oder Branchlöschen aus diesem Auftrag.
