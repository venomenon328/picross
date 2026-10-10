# VS2-V3 · Umsetzung und Nachweisweg

Stand: 10.10.2026 · V3-01–07 umgesetzt; technische Lieferbindung im
[Draft-PR #62](https://github.com/venomenon328/picross/pull/62).
Neues unabhängiges Review, persönliche VS2-M01 und Mergefreigabe bleiben offen.

## Gebundener Ausgangspunkt

Auftrag [#61](https://github.com/venomenon328/picross/issues/61), Vorbereitung
V3-S1–S5 und [VS2-E2-Nachtrag](https://github.com/venomenon328/picross/pull/62#issuecomment-6099894860).
Vorbereiteter Head `e2547016cef7cfe400a77fb09f22c872306de22a`,
Main-Basis `d7ec4e1e4a29d82b6979537a33868d57732d3713`.
Der eigene [endliche Prüfplan](../examples/vs2/v3-plan.json) wurde vor Vergleichen
in `502883c` versioniert. Ein begrenzter Kandidat, keine neue Font-/Stilsuche.
Historische Pläne und Reports bleiben unverändert. R3 gilt für den Ausgangsstand.

## Parameter und Ressourcen

- Rasterabweichung maximal 0,28 statt 0,18px, bei kleinen Zellen reduziert.
  Strichbreiten bleiben 0,70–0,90px beziehungsweise 1,40–1,64px. Die Außenkanten
  liegen 1,10px innen: 0,28 + 1,64/2 + 1,00 AA − 1,10 = 1,00px Rahmenbudget.
  Fit, Zellgeometrie und Trefferabbildung ändern sich nicht.
- Drei geringe helle Füllzüge mit fünf Punkten variieren deterministisch je
  Zellindex und Zug: Enden, Neigung, Höhe, Abstand, Biegung und Strichbreite.
  Deckende Originalfarbe, Umriss und kleine vereinfachte Flächen bleiben.
  `draw_fill()` liefert Vorschau, wartendes Ziel und finalen Animationsdurchgang.
- Navigation (−20,+12) × UI gegenüber dem vorbereiteten Head. Miniatur/Palette
  behalten ihre sichere V1-Lage. Werkzeugspalte darunter: 44 × UI große Controls,
  4 × UI Abstand, doppelte Lücke zwischen den Gruppen 2/2/4. Bei Bedarf lokales
  Scrollen; keine versteckten Klickflächen außerhalb des sichtbaren Ausschnitts.
- Die beiden dauerhaften Textzeilen entfallen. Nichtnumerische Platz-/Hinweis-
  und technische Stressmeldungen nutzen getrennte Bereiche einer Fußzeile auf
  dem Papier; vertikales Stapeln würde bei großen Flächen die Papierkante kreuzen.
  Auswahlmarkierungen, alle acht Aktionen, Tooltips und Recovery bleiben.
- [Bakso-Nutzungshinweise](../prototypes/p1/art/drawing/Bakso-NOTICES.md): aktive
  Original-TTF `art/drawing/BaksoDaging-Regular.ttf`, 128924 Bytes,
  SHA-256 `56372bf12a6e4fa47a655ff9b2c4cc73172ddd387b3a047093d3e637d081790e`.
  Alle tatsächlichen Blatttitel werden nativ geprüft. Nur `·` fehlt im Original;
  gezielter gebündelter Plex-Fallback, keine Systemfontsuche. `×`, Buchstaben und
  Ziffern bleiben Bakso. Sammlung/Information behalten Fraunces. Das Export-ZIP
  führt eigene Bakso-Nutzungshinweise; `study/*` bleibt ausgeschlossen.

## V3-A01–07 und erhaltene Verträge

| Kriterium | Tatsächlich ausgeführter Prüfpfad / Gegenprobe |
| --- | --- |
| V3-A01 | `vs2_v3_tests.gd`: tatsächliche Liniengeometrie, maximale Abweichung >0,20 und ≤0,2801px; alte 0,18-Amplitude fällt durch denselben Oracle. `vs2_v2_cases.gd`: tatsächliche Breite/AA im unveränderten Budget; absichtlich verbreiterter Strich wird abgelehnt. Native Raster-/Fünferbilder, kompakte aktuelle Zellpixeloracles. |
| V3-A02 | Verschiedene benachbarte Fülltexturen und stabile Geometriefingerprints nach Redraw, Zoomrückkehr, Blattwechsel und frischem PCK-Prozess. Identische Muster und veränderte Zellidentität werden erkannt. `zs2_capture.gd` samt Pixelprüfer erhält reale 12/24/36px-, kontrollierte/live Strichaufbau-, Vorschau- und Timingoracles einschließlich Uniform-Fade-Gegenprobe. |
| V3-A03 | Exakter gemeinsamer Navversatz gegen gebundene Referenz, reale Trefferflächen und Papier-/Titel-/Miniaturgrenzen in 96 Fällen; alle drei Zugänge und Rückwege mit tatsächlichen Mausereignissen. |
| V3-A04 | Kein permanenter Werkzeug-/Farbtext; echte Füll-/Radierauswahl, Farbwahl/Tooltips, Zellaktion sowie gescrolltes Undo/Redo. G1/GP48/H1 und Save-/Historyregression bleiben. |
| V3-A05 | Keine numerische Zoomzeile; absichtlich eingesetztes `Zoom 100 %` wird abgelehnt. Vier Zoomaktionen, Rasterrad außerhalb der Leiste, Fitgrenzen und wahrheitsgemäße Warnungen bleiben geprüft. |
| V3-A06 | F01/F02/F08 × vier Flächen × UI100/125 × G/V × Arbeitsgröße/Einpassen = 96 Fälle. Eine Spalte, 44/55px, Scrollenden, vollständig erreichbare Treffer, keine Boardüberdeckung/alten Mulden. Reale Scroll- und Klickereignisse, abgeschnittene Controls ohne Klickwirkung, unveränderter Save-/Boardzustand beim Leistenrad. Horizontale und zu kleine Controls fallen durch. V1-Recoveryfälle bleiben. |
| V3-A07 | Eingebettete Fontbytes/Hash, tatsächlicher Font und Titelglyphen, natives Original-RID für alle Zeichen außer `·`, Maße und Kontextwechsel. Falscher Font wird erkannt; Exportinventur schließt Studien/Testressourcen weiterhin aus. |

304 reguläre VS2-Layoutfälle (neun reguläre plus zehn technische Blätter), 80
V1-Fokus-/Recoveryfälle, Glyphen 1/11/17/40, 24/18-Slots und GF1 bleiben erhalten.
V2-Projektions-/Vorschau-/Neustartprüfungen erhalten die reine Füllminiatur.
Geänderte Testannahmen betreffen gezielt die abgelöste Bodenleiste, entfernte
Textlabels, neue Rasteramplitude und bewusst aktive Bakso-Ressource.

## CI, Downloads und Beweisgrenzen

Der aktuelle Product-Harness führt V3 zusätzlich zur bestehenden aktuellen
Abdeckung aus. `verify_v3()` verlangt exakt die 96 unterschiedlichen Fälle,
fehlerfreie Assertions und sechs hashgebundene native Bilder; Tooltests lehnen
Duplikate, Fehler und veränderte Bilder ab. V3-Bilder haben in der begrenzten
Erfolgsauswahl Vorrang. Alle Matrixberichte bleiben erhalten. Keine historische
Studienproduktion im Standardlauf; Grenzen 20MB technisch/75MB gesamt und 15
Minuten einschließlich aller Piloten gemäß [CI-Policy](CI_POLICY.md).

`tools/vs2_windows_probe.py` lädt für den sauberen Lieferhead neu herunter,
verifiziert Artefakt-/ZIP-/EXE-/PCK-/Planbindungen und startet beide regulären
EXEs ohne Argumente mit frischem, altem teilgespieltem und gelöstem Profil.
Native externe Skripte prüfen ausschließlich Ressourcen des gelieferten PCK;
V3 läuft in zwei Prozessen einschließlich Geometrievergleich. Normale/maximierte
Clientflächen und Windows-DPI bleiben getrennt von UI100/125 dokumentiert.
Alle Profile sind isoliert. Bericht, Hashes, Lauf und tatsächliche Resultate
stehen commitgebunden im PR, ebenso der getrennte Selbstreview.

Native technische Prüfungen und Implementierersichtung sind keine persönliche
VS2-M01 und kein unabhängiges Review. Kleine/kollidierende Großfallhinweise
bleiben als Einschränkungen sichtbar. Kein Merge, Release oder Schließen von #61.
