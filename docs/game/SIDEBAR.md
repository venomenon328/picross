# Sidebar · Miniatur, Palette und Werkzeuge

## Geltung und Zuständigkeit

Dieser Vertrag führt die gemeinsame Sidebargeometrie und ihre drei Rasterrahmen.
Die Regeln im aktuellen Git-Stand sind vom Nachweis einer konkreten Lieferung zu
unterscheiden; Review und persönliche Abnahme stehen in Issue/PR.

| Detail | Maßgebliche Quelle |
| --- | --- |
| Werkzeugwirkung, Vollsicht und Save-Kompatibilität | [P1](PROTOTYPE_P1.md) |
| Miniaturinhalt und sichtbare Strichsprache | [Zeichensprache](UI_DRAWING_STYLE.md) |
| Kleine Controls, Schrift und Piktogramme | [Handgezeichnete UI](HAND_DRAWN_UI.md) |
| Navigation und Buchmaterial | [Buchdarstellung](BOOK_INTEGRATION.md) |
| Aktive Quellen und Provisionierung | [Ressourcenvertrag](Z2_SELECTION.md) |

## Bedienung und Layout

Genau sechs Originalcontrols in 2×3: Füllen/Radieren, Undo/Redo, Minus/Plus.
44/55px Mindesttreffer und 4×UI Abstand ergeben 92×140 beziehungsweise 115×175px.
Alle sechs bleiben in den unterstützten Fenster-/UI-Konfigurationen ohne Scrollen erreichbar.
Die lokale UI-Radgrenze bleibt zur Trennung vom Rasterzoom bestehen.
Einpassen und Arbeitsgröße haben keine reguläre Action, Menü-/Tastenbindung,
Tooltip oder Anleitung mehr. Die gleichnamige historische Board-API bleibt für
alte Studien erhalten, wird von der regulären Oberfläche aber nicht aufgerufen.
G/V stehen weiterhin ausschließlich in den Optionen; interne Fitgrenze bleibt.

Die Überschrift „Dein Stand“ entfällt. Miniatur, Koordinaten, Palette und Werkzeuge
teilen die tatsächliche Mitte der unveränderten oberen Dreiernavigation.
Das entspricht `material.x + material.width - (187.5 bei Breite <1700, sonst 150) - 56×UI`;
der Korrekturweg ist damit abhängig von Breiten-Breakpoint und UI-Skalierung.
Die Alpha-Hüllen sind zuvor beschnitten;
symmetrische sichere Innenräume zentrieren die sichtbare Zeichnung. Die Miniatur
ist bei kompakter Breite, knapper Höhe oder andernfalls verletzter linker
Papiergrenze 86×UI, sonst 132×UI. Wenn die neuen
Gruppen in den belegten Arbeitsblock reichen, nimmt ausschließlich ungenutztes
linkes Papier den geometrisch ermittelten Abstand auf. Boardgröße, Fit,
Zell-/Schriftmaße und Hinweisplätze bleiben unverändert; keine neue Panroute.
Gemessen werden tatsächliche Alpha-Hüllen, Rasterkontur, vollständige Hinweis-
Treffer-/Reiseflächen und native Textmaße statt leerer Controlfläche.
Die Navigation selbst folgt dem [Buchvertrag](BOOK_INTEGRATION.md).
Drei Bildtexturen bilden die Gruppenrahmen; zusätzliche Metallhalter,
Trennlinie und Mulden entfallen. Die Arbeitsminiatur zeichnet keinen doppelten
Rahmen; Albumminiaturen behalten ihren Rahmen. Buchdekoration ignoriert Mausinput.
Hover, Auswahl, Disabledzustand und tatsächliche Treffer bleiben Controls.

## Ressourcen und Save-Kompatibilität

[Original, Bildauftrag und Aufbereitung](../design/sidebar_frames/README.md),
[aktives Rahmenmanifest](../../game/art/book/frames.json) und
`tools/sidebar_assets.py` binden die drei PNGs. Historische BP-Eingaben und
Herkunftsnachweise bleiben unverändert. Aktive Iconquellen und Exportbindungen
stehen im [Ressourcenvertrag](Z2_SELECTION.md); frühere Iconzahlen sind kein
zweites Inventar.

Die reguläre Schema-1-Normalisierung von `overview`, Handwerkzeug und Pan sowie
der Erhalt von Zoomwunsch, Spielstand und Recoverygrenzen stehen ausschließlich
in [P1 §6](PROTOTYPE_P1.md#6-speicherung-und-wiederaufnahme).

## Prüfzuordnung

SL-A01–A07 bezeichnen die ursprünglichen Kriterien aus
[#65](https://github.com/venomenon328/picross/issues/65): Save-Kompatibilität,
sechs bedienbare Controls, gemeinsame Achse, sichere Alpha-/Text-/Trefferhüllen,
Originalressourcen und vollständige Lieferung. Der aktuelle Paketplan wählt die
hierfür betroffenen Prüfungen gemäß [nativem Modulvertrag](../ci/CI_C_NATIVE_GROUPS.md).
Historische Vollmatrizen und frühere Bild-/ZIP-Grenzen sind keine erneuten Gates.

## Herkunft und Nachweise

Fachentscheidungen und tatsächliche Review-/Abnahmeergebnisse: [#65 / PR #66](https://github.com/venomenon328/picross/pull/66).
Der [historische Dokumentstand](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/SL65_IMPLEMENTATION.md)
erhält frühere Lieferchronologie und ersetzte Regeln. Er ist keine zusätzliche
Normquelle oder dauerhafte Prüfpflicht. Aktuelle Prüfungen folgen dem
[Paketvertrag](../ci/CI_WORKFLOW_V2.md) und dem jeweils betroffenen Modul.
