# Designoriginale und Ressourcenherkunft

Dokument-ID: `design-inputs`
Status: `reference`
Zuständigkeit: Erhaltung der benötigten Original-, Rechte- und Freigabebindungen.

Dieses Verzeichnis enthält Eingänge der Ressourcenherstellung und ihrer
Überprüfung. Historische Entwurfsvarianten und Abnahmebeschreibungen sind keine
zusätzliche aktuelle Spiel- oder Bildnorm. Aktuelle Gestaltung steht in den
[Spielverträgen](../game/UI_DRAWING_STYLE.md) beziehungsweise den
[Bildtypnormen](../production/images/README.md).

| Bestand | Erhaltungsgrund |
| --- | --- |
| `book_inventory/` | Aktive Buch-/Font- und Iconquellen mit Herkunftsdaten zum gewählten A-Material. |
| Schriftoriginale, Manifeste, ZIPs und Lizenztexte | Tatsächliche Inputs unter anderem von `tools/z2_resources.py` und `tools/sidebar_assets.py`; geschlossene Quellen- und Rechteprüfung. |
| Titelbildoriginale und Provenienz | Bindung der unveränderten ausgewählten Titelgrafiken. Aktueller Stil: [TITLES](../production/images/TITLES.md). |
| Sonstige gebundene SVG-/PNG-/JSON-Ressourcen | Konkrete Herstellung, Referenz oder ausdrücklich aufrufbare Diagnose gemäß ihrem Manifest. |

Ein historischer Dateiname ist kein Löschgrund. Originale, Dateihashes, Nutzungsrechte
und tatsächliche Freigaben bleiben erhalten. Ihre Pfade werden nur geändert, wenn
alle realen Verbraucher und Bindungen verstanden und kompatibel behandelt sind.
Die Dokumentationsbereinigung ersetzt keine neue Bildabnahme und verändert keine
freigegebenen Ressourcenbytes.

## Buchoriginale und historische Pakete

Die aktive Quellen- und Provisionierungsbindung steht in
[Z2_SELECTION](../game/Z2_SELECTION.md). `tools/z2_resources.py` verwendet das
[A-Original](book_inventory/artwork/bp2-a-inventarband.png) und die
[gepinnten Fontquellen](book_inventory/composition/inputs/fonts.json).
Die nativen A-Originale, ihre Prompts und die
[Generierungsdaten](book_inventory/artwork/generation.json) belegen Herkunft,
Retusche und native Auflösung. Das [historische Artworkmanifest](https://github.com/venomenon328/picross/blob/5b689e775ea89ae80ee1a3d8323b1a2c1f728f9a/docs/design/book_inventory/artwork/manifest.json)
bindet auch die damalige B-Variante.

BP-1R, BP-2 und BP-3 sind historische Entwurfs-/Lieferpakete. Ihre früheren
Briefings, Vergleiche und Prüfberichte begründen keine aktuelle Spielregel oder
offene Freigabepflicht. Die [Texte vor der Konsolidierung](https://github.com/venomenon328/picross/tree/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/design/book_inventory)
bleiben am festen Git-Stand erreichbar. Die vollständigen Originalpakete liegen
am früheren Archivcommit `fad885344874534629365917a2ab6a8d311cd3a7`:

| Paket | Unverändertes Originalpaket |
| --- | --- |
| BP-1R · Vorlage | [bp1r-review.zip](https://github.com/venomenon328/picross/blob/fad885344874534629365917a2ab6a8d311cd3a7/docs/design/book_inventory/production/bp1r-review.zip) |
| BP-2 · Hintergründe | [bp2-review.zip](https://github.com/venomenon328/picross/blob/fad885344874534629365917a2ab6a8d311cd3a7/docs/design/book_inventory/artwork/bp2-review.zip) |
| BP-3 · Komposition | [bp3-review.zip](https://github.com/venomenon328/picross/blob/fad885344874534629365917a2ab6a8d311cd3a7/docs/design/book_inventory/composition/bp3-review.zip) |

Das [historische Archivverzeichnis](https://github.com/venomenon328/picross/blob/5b689e775ea89ae80ee1a3d8323b1a2c1f728f9a/docs/design/book_inventory/ARCHIVE.json)
verzeichnet Pfade, Git-Blob-SHAs und Größen. Die ursprünglichen Paketmanifeste,
B-Quellen und Entwurfsdateien stehen im [gebundenen Git-Stand](https://github.com/venomenon328/picross/tree/5b689e775ea89ae80ee1a3d8323b1a2c1f728f9a/docs/design/book_inventory).
Die historische Prüfung folgt der [gebundenen Archiv-Anleitung](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/design/book_inventory/ARCHIVE.md).
