# HZ-B · Controls und Piktogramme

Implementierung zu [#284](https://github.com/venomenon328/picross/issues/284),
ausschließlich HZ-B-A01–A06 nach HZ-B-P01 und
[HZ-D03–D06](HAND_DRAWN_UI.md). Basis:
`e9a957d1513c9c77281e738c4eb22b161bee2342`; Arbeitsbranch
`feat/284-handgezeichnete-controls`. Stand: 20.10.2026.

## Lieferung

- A01: `book_style.gd` zeichnet deterministische Bézierkanten, kleine Eckversätze,
  sichere Überstände und kurze zweite Striche. Karten verwenden weiter ihren
  `content_surface`-/StyleBox-Pfad und die Registry-ID. Kleine Papierbuttons
  verwenden denselben Stil, getrennt vom unveränderten Swatch-/Raster-Scribble.
- A02/A03: `book_choice.gd` bleibt ein nativer `OptionButton` mit `PopupMenu`.
  Kategorien, Sortierung und Rätselansicht erhalten zusammengehöriges Papier,
  Zeilenhervorhebung, Auswahlhaken, Chevron und Scrollbarressourcen.
  Auswahl, Tastatur, Rad und Trefferprüfung verbleiben bei Godot. Verstecken,
  Neuaufbau, UI-/Ansichts- und Größenwechsel schließen alte Popups.
- A04: `tools/book_icons_hz.json` enthält die 13 bisherigen Bedeutungen sowie
  vier Pfeile, zwei Chevrons, Auswahlhaken/Leerplatz und beide Checkboxzustände.
  Alle 23 SVGs entstehen reproduzierbar aus dieser neuen Quelle. Play bleibt
  geliefert, ohne wieder als zusätzliche Katalogaktion aufzutauchen.
- A05: Zustandsflächen, gezeichnete Auswahlmarkierung und separater Fokus
  erhalten die rechteckigen Trefferflächen. Seitenbuttons behalten lesbare
  Wörter neben den lokalen Pfeilbildern; Sortierbeschreibungen bleiben erhalten.
- A06: Generator, Quellhash, Manifest, Herkunftshinweis, PCK-Audit und Web-
  Lizenzinventar werden gemeinsam fortgeführt. BP-/SL-/KB-Originalquellen
  und ihre historischen Berichte bleiben unverändert.

HZ-A-Schriftdateien/-rollen, Hinweis-/Rastergeometrie, Rätseldefinitionen,
Runtime-/Autorendaten, Spielstandsmodelle, Sortierregeln und Palette/2×3-Werkzeuge
werden nicht verändert. Der technische KU-B-Pfeiltest prüft jetzt die SVG-
Zuordnung statt Unicode; sein Bedeutungs- und Sortierorakel bleibt bestehen.

## HZ-B-T01 · reproduzierbare Prüfwege

Die verbindlichen Laufnummern, Head-/Basis-/Integrations-SHAs, Producer-Versuche,
Ergebnisse und Originalhashes stehen im zugehörigen Draft-PR und Issue.
Dieses Dokument behauptet keinen Erfolg für noch laufende Prüfungen.

| Ebene | Nachweis |
| --- | --- |
| Ressourcen | `test_z2_delivery`: deterministische Provisionierung, exakte Inventare/SVGs/Hashes, defekte SVGs, zusätzliche Ressourcen und verfälschte HZ-Quellenbindung werden erkannt |
| Geometrie/Kern | `hz_b_cases.gd` im regulären Kernlauf: ID-/Zustands-/Neuaufbau-/Skalenstabilität, unterschiedliche IDs, AA-Hülle, triangulierbare Füllfläche, rechteckige Maske, alle importierten Icons |
| Native UI | `hz_b_native.gd` im bestehenden KAT-2-Modus `kk`: echte Control-Ereignisse, sortierte Kartenneuaufbauten, Popup-Abbruch/Ansichts-/Resizewechsel, Checkboxen, Originalausschnitte |
| Lange Liste | unverändertes `hz_native.gd`: synthetische 256 Kategorien, 128-Zeichen-Name, echtes Rad und Zeigerwahl bis zum letzten Eintrag, vollständige Tooltips |
| Chromium | HZ-B-W01 in `catalog`: echte Browserereignisse, Außenklick ohne Durchklicken, Resize, Tastaturauswahl, Checkboxen und unveränderte Rätselzustände |
| Windows/PCK | `hz_windows_probe.py`: CI-Artefakt-/ZIP-/PCK-/Editorbindung, echter Exportstart in isoliertem Profil, externe synthetische Definitionen gegen gepackte UI-/Iconressourcen, anschließend native KAT-2-Routen |
| Pflicht-CI | Auswahl durch `ci_scope.py` aus vollständigem Basis-/Head-Diff; abschließendes `ci-required` mit nativen und Chromium-Originalbelegen |

Die drei Bildkonfigurationen sind 1280×720/UI125, 1920×1080/UI100 und
2560×1440/UI125. Die nativen Originalausschnitte `hz-b-{card,sort,settings,view,icons}-*.png`
stehen im technischen Katalogartefakt, ohne Skalierung oder Nachzeichnen.
Die neue Ressourcenfamilie wird auch gegen den tatsächlich ausgelieferten PCK
geladen; keine gepackte UI-/Iconressource wird im Test ersetzt.

## Getrennter Selbstreview und Grenzen

Der Implementierer prüft nach den Entwicklungsläufen separat den vollständigen
Diff, die tatsächlichen Originalbilder bei UI-Größe, Ressourcen-/Exportbindung
und die Erhaltungsgrenzen. Befunde und Abschluss werden im PR am geprüften Head
festgehalten. Das bleibt ein Selbstreview und ersetzt **nicht HZ-B-R01**.

Entwicklungsbefunde: Füllpolygone dürfen die offenen Strichüberstände nicht
enthalten (sonst Selbstüberschneidungen); die zusätzliche Triangulationsprüfung
deckt dies ab. Native Checkboxprüfungen scrollen bei kleiner Fensterhöhe vor
dem echten Klick. Historische Unicode-Pfeilannahmen und die exakten CI-/Web-
Inventare werden auf die neue aktive Familie angepasst.

**HZ-B-R01** (separater qualifizierter Review) und **HZ-B-M01** (Eigentümerabnahme)
bleiben vor Merge offen. Kein Merge, Deployment oder Issue-Abschluss.
