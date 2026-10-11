# SL-65 · kompakte Sidebar und gezeichnete Rahmen

Auftrag [#65](https://github.com/venomenon328/picross/issues/65), Paket A+B auf
`feat/65-sidebar-frames`, Basis `e323dcf5c83b085144e61707ef98ecab2bfac39b`.
PR #62 ist integriert und abgeschlossen. Kein Merge-/Releaseauftrag.
SL-R01/B-01 wird gemäß [SL-N01](https://github.com/venomenon328/picross/pull/66#issuecomment-6103925038)
nachgearbeitet. Unabhängiges Nachreview, persönliche SL-M01 und gesonderte
Mergefreigabe bleiben offen.

## Bedienung und Layout

Genau sechs Originalcontrols in 2×3: Füllen/Radieren, Undo/Redo, Minus/Plus.
44/55px Mindesttreffer und 4×UI Abstand ergeben 92×140 beziehungsweise 115×175px.
Alle sechs sind auf den vier unterstützten Flächen ohne Scrollen erreichbar.
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
Der obere V3-Navversatz bleibt. Drei Bildtexturen ersetzen Gruppenrahmen,
Metallhalter, Trennlinie und Mulden. Die Arbeitsminiatur zeichnet keinen doppelten
Rahmen; Albumminiaturen behalten ihren Rahmen. Buchdekoration ignoriert Mausinput.
Hover, Auswahl, Disabledzustand und tatsächliche Treffer bleiben Controls.

## Ressourcen und Save-Kompatibilität

[Original, Bildauftrag und Aufbereitung](design/sidebar_frames/README.md),
[aktives Manifest](../prototypes/p1/art/book/frames.json) und
`tools/sidebar_assets.py` binden die drei PNGs. `z2_resources.py` provisioniert
nur elf aktive Icons; fit/work/hand/album werden nicht neu erzeugt. `nav-work`
bleibt die Rücknavigation. Historische BP-Eingaben wurden nicht geändert.
Neue Herkunft ist separat ausgewiesen und als Nutzungshinweis im Spieler-ZIP.

SaveStore bleibt unverändert: erst vollständige Schema-1-, Zell-/History-/Cursor-,
Abschluss- und Viewvalidierung, einschließlich erforderlichem booleschem
`overview`. Anschließend normalisiert nur die reguläre Anzeige `overview=false`,
`hand→fill` und Mittelpunkt statt Pan. Gültiger Zoomwunsch bleibt `requested_cell`,
Istmaß ist `min(Wunsch, Fit)`. Capture schreibt Schema 1, gültigen Wunsch und false.
Eigene Zellen, komplette History/Redo, `undo_used`, Abschluss, Farbe, Radierer und
Hinweisanker bleiben. Recovery erhält keine zusätzliche Schreibfreigabe.

## Aktuelle Nachweiszuordnung

| Kriterien | Prüfung |
| --- | --- |
| SL-A01/A06 | Bestehende Integration, P1.3/VS2-Prozessroundtrips, alter echter Writer mit overview true/false und Zoom72 → neuer Reader, neuer Writer → frischer Reader. Ungültige/missing overview-Werte weiterhin abgewiesen; hohe Zoomwünsche exakt fitbegrenzt. |
| SL-A02/A03 | Reale Klicks auf alle sechs Controls, Undo/Redo und Zellaktion, Rasterrad und wirkungsloses UI-Rad, 2×3-Positionen, Mindesttreffer, keine alte Action/Überschrift; versetzte/zu kleine Controls als Gegenprobe. |
| SL-A04/A05 | 96 Geometriefälle: vier Flächen × UI100/125 × F01/F02/F08 × G/V × Wunsch24/72; zusätzlich vollständige 304er-Matrix und 80 fokussierte V1-/Recoveryfälle. Alpha-Hüllen und tatsächliche Controls gegen unveränderte obere Navigation, Papier, Raster-/Hinweisflächen und Nachbargruppen. Gemeinsam verschobene untere Gruppen, getrennt verschobene Rahmen/Controls sowie eine verschobene obere Referenz scheitern nativ und im unabhängigen Berichtsoracle. RGBA-Hash/Innenalpha aus tatsächlich geladenen Texturen, gerenderter Bildvergleich mit entfernten Texturen. Falsche Textur/Überdeckung werden abgewiesen. |
| SL-A05/A06 | [Endliche Bildauswahl](../examples/vs2/sl65-plan.json): acht Vollansichten einschließlich knapper normaler und Recoveryansicht, plus vier 1:1-Details. Bestehende V1-Recovery-, V2-Miniatur-, GF1-/H1-/Animations-/Spoileroracles bleiben. |
| SL-A07/T01 | Aktuelle CI-Diffauswahl, Product/Visual/Integration, Produktion/Piloten und gegebenenfalls Preflight; docs und ci-required. `vs2_windows_probe.py` am sauberen Lieferhead: frische Downloads, beide EXEs regulär, tatsächliches PCK in frischen Prozessen, Asset-/Bild-/EXE-/PCK-/Runbindung. |

Die aktuelle Prüfausgabe und ausgeführten Ergebnisse werden commitgebunden im
bestehenden [Draft-PR #66](https://github.com/venomenon328/picross/pull/66) verlinkt,
einschließlich kompakter Vorher-/Nachherbelege und getrenntem Selbstreview. Dieses Dokument
ist die Zuordnung, kein vorweggenommenes Testergebnis. Technische native Sichtung
ist weder unabhängiges Review noch persönliche [SL-M01](VS2_OWNER_TRIAL.md).
Historische V1/V2/V3-Pläne und Messergebnisse bleiben unverändert.

Die bisherige optionale 12-MB-Bildauswahl würde den geforderten 1440p-Fall
verdrängen. Für die acht gezielten Vollbilder gilt ein 15-MB-Bildteilbudget;
20 MB technische Daten und 75 MB gesamt bleiben unveränderte harte Grenzen.
Eine redundante 1080p-Farbvollansicht entfällt, deren Prüfungen bleiben erhalten.
Für abschließende Berichts-/Auditmetadaten bleiben 250 kB reserviert; das harte
Techniklimit wird nach der Verpackung erneut geprüft. Fehlt eines der zwölf
gezielten SL-Bilder in der begrenzten Lieferung, schlägt Product fehl.
