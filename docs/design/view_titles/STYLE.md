# BTI-B-V2-rev1 · Freigegebene Stilquelle

Die drei unveränderten [Produktoriginale](../../../game/art/drawing/view_titles/manifest.json)
sind die am 06.11.2026 persönlich freigegebene V2-rev1-Familie aus
[BTI-B-D03/M01](https://github.com/venomenon328/picross/issues/533#bti-b-d03).
BTI-C integriert genau diese Bytes; keine neue Stilwahl oder Bildproduktion.
Die verworfene braune BTI-A-Fassung bleibt nur in ihrer Git-Historie.
Die aktuelle Spielintegration benötigt eigene BTI-C-T01/R01/M01-Nachweise.

## Textunabhängige Grammatik

Breite, leicht geneigte, individuell gezeichnete Graphitbuchstaben. Kräftige,
unregelmäßig nachgezogene Konturen und grobe diagonale Schraffur mit offenen
Zwischenräumen; keine solide schwarze Füllung oder gleichmäßige Rauschtextur.
Buchstabenhöhe, Neigung, Grundlinie, Abstand und Strichdruck variieren leicht.
Dunkles neutrales Anthrazit/Graphit, kein dominantes Braun oder Sepia.
Nur Lettering auf echtem transparentem Grund, transparente Innenräume und
vollständige Punkte/Enden. Keine Banner, Rahmen, Blätter oder weiteren Bildmotive.

Kurze Wörter behalten ihre natürliche Breite. Der linkslaufende Querzug von
Hilfe wächst aus dem unteren f-Ende, der längere Zug von Einstellungen aus
dem unteren g-Bogen. Kein zusätzlicher abgelöster Doppelunterstrich. Der
Kataloganker behält seine eigene Behandlung; kein neuer Anschluss wird erzwungen.
Die freigegebenen Originale sind die Stilanker für später separat beauftragte
Wörter. Keine Zusage pixelidentischer Regeneration.

## Tatsächliche Herstellung und Referenzkette

[provenance.json](../../../game/art/drawing/view_titles/provenance.json) erhält
die vollständigen tatsächlichen V2-Prompts einschließlich Kataloganker sowie
alle vier Revisionsaufrufe, Referenzreihenfolge, Dateinamen, Hashes und bekannte
Parameter. Werkzeug `image_gen.imagegen`, `transparent_background=true`;
Backend-/Modellversion, Seed und nicht exponierte Parameter unbekannt.

Die Erstproduktion verwendete die damals tatsächlich betrachtete C-Chatreferenz
(kein verfügbarer Originaldateihash) und einen generierten V1-Kontrastanker.
V2-Katalog wurde danach als unmittelbare Bildreferenz geöffnet und eingesetzt.
G1 überarbeitet Hilfe; G2 überarbeitet Einstellungen, aber zu dicht/regelmäßig;
G3 öffnet deren Schraffur, enthält jedoch helle Sprenkel; G4 bereinigt G3
generativ. Nur G1/G4 und der unveränderte V2-Katalog werden ausgeliefert.
G4 ist keine deterministische Freistellung. Keine manuelle Rasterretusche,
Neufärbung, Beschneidung, Alphaersetzung oder Neucodierung der finalen Originale.
Die PNGs sind Master und Export; keine Vektorquelle oder TTF-Rasterung.
[Herkunftsnotiz](../../../game/art/drawing/view_titles/NOTICE.txt) ohne erfundene
Lizenz, Exklusivrechte oder Garantie.

## Originalbindung und Anzeige

Quelle aller drei PNGs: Belegcommit
`9029a4a3a05d6da2c8d88327594a4598fd0db505`,
`review-evidence/BTI-B-V2-rev1/originals/`.

| Datei | Pixel / Bytes | SHA-256 |
| --- | --- | --- |
| catalog.png | 2172×724 / 1814749 | `0931abd9e2b67211b6895575f7ab157d10547348d62d2e99c4ba067ee4772cc4` |
| help.png | 1536×1024 / 2500745 | `5ae830d1fe70007c67ed04570c034b446a3007c8ec78676cc335875bf3f8e87a` |
| settings.png | 2172×724 / 1427565 | `d4c84fbe95279c51e1a07df9511e3482b3d65591942d1849655c2ef8dc452c75` |

Verlustfreier Godot-Import mit Mipmaps, Alpha und lokalem linearem Sampling.
Das Manifest bindet die optischen Hüllen bei Alpha ≥16 (Endkoordinaten exklusiv).
Diese zentrieren die sichtbare Tinte; die gesamte PNG-Fläche wird proportional
mit vier Pixeln Rand um diesen Mittelpunkt eingepasst. Auch Alpha-1-Reste an
Bildkanten werden erhalten, nicht abgeschnitten oder als optischer Anker benutzt.
Hilfe wird nicht auf Langwortbreite gestreckt. Die Titelbereiche folgen der
verfügbaren Papierhöhe; Navigation, sichere Falzränder und nutzbarer Scrollraum
haben Vorrang. Statische 42-/96-px-Studienkörper sind keine Godot-Endmaße.
Originalsicht, reale Windowsmaße, Import und PCK-Prüfung stehen im aktuellen PR.
