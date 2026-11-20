# UI-Ressourcen · Quellen, Provisionierung und Rendererbindung

## Geltung und Zuständigkeit

Dieses Dokument führt aktive lokale UI-Ressourcen und ihren reproduzierbaren
Quellenweg. Es beschreibt keine alternative Layout-, Schrift- oder Spielregel.
Die Fachverträge im aktuellen Git-Stand gelten; Liefer-, Review- und
Abnahmeergebnisse bleiben an den jeweiligen Issue-/PR-Head gebunden.

| Bereich | Maßgebliche Quelle |
| --- | --- |
| Buchmaterial und Capture | [Buchdarstellung](BOOK_INTEGRATION.md) |
| UI-Schriftrollen, kleine Controls und Icons | [Handgezeichnete UI](HAND_DRAWN_UI.md) |
| Hinweisfont, Slots und Status | [Hinweistypografie](CLUE_TYPOGRAPHY.md), [Hinweisstatus](CLUE_STATUS.md) |
| Zellzeichnung und Animation | [Zeichensprache](UI_DRAWING_STYLE.md), [Zellrendering](CELL_RENDERING.md) |
| Drei große Gruppenrahmen | [Sidebar](SIDEBAR.md) |
| Bildhaupttitel | [VIEW_TITLE_ART](VIEW_TITLE_ART.md) |

## Aktive Quellen

| Ressource | Bindung |
| --- | --- |
| A · dunkler Inventarband | Unverändertes UI-freies PNG unter `docs/design/book_inventory/artwork/bp2-a-inventarband.png`; SHA-256 `957c2eab39b2334825fb159287b9d36a17b77fff1c628ea88110f2cfb5f7a71a`. Hintergrund und Control-/Rastergeometrie bleiben getrennt. |
| BP-Fonts | [Gepinnte BP-3-Upstreamquellen](../design/book_inventory/composition/inputs/fonts.json), lokale Fontbytes und zugehörige Nutzungshinweise. |
| Pangolin-Standardtext | Bytegebundene TTF und OFL unter `game/art/drawing/`; Originalhashes und Rollen in [HZ-D08](HAND_DRAWN_UI.md), Herkunft im [NOTICE](../../game/art/drawing/pangolin/NOTICE.txt). |
| Aktive Iconfamilie | [tools/book_icons_hz.json](../../tools/book_icons_hz.json); erzeugte SVGs, Inventar, Herkunft und Manifest gemeinsam fortschreiben. Dazu gehören Navigations-, Werkzeug-, Auswahl-, Checkbox-, Scrollpfeil- und Beendenzeichen. |
| Große Sidebarrahmen | `tools/sidebar_assets.py`, [Rahmenmanifest](../../game/art/book/frames.json) und [Originale](../design/sidebar_frames/README.md). |

`tools/book_icons_kb.json`, die BP-Iconquelle und historische Fontnachweise bleiben
Originale ihrer Lieferstände. Ein neues aktives Asset erhält eigene nachvollziehbare
Herkunft. Generierte Dateien allein zu überschreiben erfüllt den Quellenvertrag nicht.
Windows-/Webexport verwenden die tatsächlich geprüften aktiven Ressourcen samt
zugehörigen Nutzungshinweisen. Eine historische unbenutzte Standardtextschrift
wird dadurch nicht als zweite aktive Rolle exportiert.

## Freigegebene Erweiterung: Dancing Script

Für die Abschlussrolle nach HZ ist die unveränderte variable Originalschrift
**Dancing Script** freigegeben. Produktintegration, lokale Provisionierung und
tatsächliche Lieferung im Windows-/Webexport sind in
[VIS-A / #728](https://github.com/venomenon328/picross/issues/728) noch offen;
die folgenden Quellen sind keine bereits aktiven Produktressourcen.

Beide Originale sind an `googlefonts/DancingScript` bei Commit
`291f87c05206179b6bfd53735a5638b5cc84e3b3` gebunden:

| Original | Bytes | SHA-256 |
| --- | ---: | --- |
| [DancingScript[wght].ttf](https://github.com/googlefonts/DancingScript/blob/291f87c05206179b6bfd53735a5638b5cc84e3b3/fonts/variable/DancingScript%5Bwght%5D.ttf) | 133636 | `21808625578fe8d8cd10cb684be546dca077b27cd03a53a2f1ec11dc743c924c` |
| [OFL.txt](https://github.com/googlefonts/DancingScript/blob/291f87c05206179b6bfd53735a5638b5cc84e3b3/OFL.txt) | 4443 | `6f090277c00af96651ce6dbcc38ff1591047a3bffef486e80b6a32e8276a8201` |

Die [Google-Fonts-Metadaten](https://github.com/google/fonts/blob/f391eb5d1f3c7d64eab1bf992b1aee045ac48ffb/ofl/dancingscript/METADATA.pb)
weisen denselben Upstream-Pin, die Gewichtsachse 400–700 und die Bereiche
latin, latin-ext und vietnamese aus. Download und lokale Bündelung erhalten die
Originalbytes einschließlich ihrer Zeilenenden. Zeichenabdeckung und sichtbare
Akzenthüllen werden zusätzlich mit der eingebundenen Ressource nach HZ geprüft.

Die SIL Open Font License 1.1 erlaubt lokale Bündelung und kommerzielle Verwendung
unter ihren Bedingungen. Copyright- und vollständiger Lizenztext werden
mitgeliefert; der Reserved Font Name „Dancing Script“ bleibt beim unveränderten
Original erhalten. Produkt und Webexport verwenden lokale Bytes ohne externe
Fontanfrage. Historische Fontpakete werden nicht umgeschrieben.

## Bereitstellung

```sh
python tools/z2_resources.py provision
python tools/z2_resources.py verify
```

`provision` lädt ausschließlich die gepinnten BP-3-Upstreamquellen, prüft ihre
Downloadhashes, normalisiert die OFL-Texte wie BP-3 und prüft deren Zielhashes.
Die aktive HZ-Iconquelle erzeugt die SVGs und bindet Quellhash und Herkunft im
[aktiven Buchmanifest](../../game/art/book/manifest.json).

`verify` prüft lokale Bytes, vollständiges Inventar und A-Identität offline.
Pangolin-Original und OFL werden separat vom historischen HZ-Font geprüft.
Historische Fontquellen werden nicht durch die BP-Provisionierung ersetzt.
Gebündelte Fonts und Nutzungshinweise gehören in die native Anwendung;
es gibt keine Systemfontsuche oder nachträgliche Änderung historischer Pakete.

## C1 · Farbkontur

Die Farbkontur ist Teil der Hinweiszeichnung. Ihre Semantik und Renderermaße
stehen ausschließlich in [CLUE_TYPOGRAPHY · C1](CLUE_TYPOGRAPHY.md#c1--farbkontur).

## Herkunftsgrenzen des A-Materials

Das A-Master ist aufbereitetes 1672×941-Material auf 2560×1440 und keine nativ
in 1440p erzeugte Illustration. Untere Retuschestelle und weichere Detailauflösung
sind in den [Herkunftsdaten](../design/book_inventory/artwork/generation.json) und
im [historischen BP-2-Prozess](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/design/book_inventory/artwork/PROCESS.md)
dokumentiert. Originalpakete und historische Manifestbindungen sind im
[Designindex](../design/README.md#buchoriginale-und-historische-pakete) zugeordnet.
N1 ist eine reversible Hintergrundableitung. Die historische A-Auswahl legt
keine gesamte Themen-/Kapitelstruktur oder wählbaren Laufzeit-Themes fest.

## Herkunft und Nachweise

Fachentscheidungen und tatsächliche Review-/Abnahmeergebnisse: [GD-01–GD-05 / PR #32](https://github.com/venomenon328/picross/pull/32#issuecomment-5855483934), [PR #33](https://github.com/venomenon328/picross/pull/33), [#531](https://github.com/venomenon328/picross/issues/531) und die jeweils betroffenen UI-Pakete.
Der [historische Dokumentstand](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/Z2_SELECTION.md)
erhält frühere Lieferchronologie und ersetzte Regeln. Er ist keine zusätzliche
Normquelle oder dauerhafte Prüfpflicht. Aktuelle Prüfungen folgen dem
[Paketvertrag](../ci/CI_WORKFLOW_V2.md) und dem jeweils betroffenen Modul.
