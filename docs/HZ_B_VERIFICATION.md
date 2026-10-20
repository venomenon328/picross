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
2560×1440/UI125. Die nativen Originalausschnitte `hz-b-{card,sort,settings,view,dialog,icons,hover,pressed,scroll-hover,scroll-pressed}-*.png`
stehen im technischen Katalogartefakt, ohne Skalierung oder Nachzeichnen.
Die neue Ressourcenfamilie wird auch gegen den tatsächlich ausgelieferten PCK
geladen; keine gepackte UI-/Iconressource wird im Test ersetzt.

## Archivierte native Entwicklungsoriginale

Der direkte Windows-Entwicklungslauf `hzb-1792524693` besteht 972 Prüfungen auf
Godot `4.7.2.stable.official.ed1daf0bf`, NVIDIA RTX 3070. Er lief vor dem Commit;
ein anschließender vollständiger Bytevergleich der geänderten Spielressourcen
bindet sie an `40a865b1ab2fcfd7fa5373e8be4e185d1aad5f07`.
[Bindung und Originalhashes](evidence/hz-b/windows-development/binding.json),
[Originalbericht](evidence/hz-b/windows-development/hzb.json),
[Prozesslog](evidence/hz-b/windows-development/run.log) und
[temporärer Testeinstieg](evidence/hz-b/windows-development/temporary-runner.gd.gz)
legen diese Grenze offen. Der Einstieg ergänzt ausschließlich einen direkten
HZ-B-Aufruf im synthetischen KAT-2-Runner. Das ist **kein Ersatz** für den
abschließenden sauberen Windows-/PCK-Lauf am gelieferten Head.

| Native Größe | Kartenfokus | Popup | Familie / echter Druck | Checkboxen / Dialog |
| --- | --- | --- | --- | --- |
| 1280×720/UI125 | [Karte](evidence/hz-b/windows-development/hz-b-card-1280.png) | [Sortierung](evidence/hz-b/windows-development/hz-b-sort-1280.png) | [Icons](evidence/hz-b/windows-development/hz-b-icons-1280.png), [Druck](evidence/hz-b/windows-development/hz-b-pressed-1280.png) | [Einstellungen](evidence/hz-b/windows-development/hz-b-settings-1280.png), [Dialog](evidence/hz-b/windows-development/hz-b-dialog-1280.png) |
| 1920×1080/UI100 | [Karte](evidence/hz-b/windows-development/hz-b-card-1920.png) | [Sortierung](evidence/hz-b/windows-development/hz-b-sort-1920.png) | [Icons](evidence/hz-b/windows-development/hz-b-icons-1920.png), [Druck](evidence/hz-b/windows-development/hz-b-pressed-1920.png) | [Einstellungen](evidence/hz-b/windows-development/hz-b-settings-1920.png), [Dialog](evidence/hz-b/windows-development/hz-b-dialog-1920.png) |
| 2560×1440/UI125 | [Karte](evidence/hz-b/windows-development/hz-b-card-2560.png) | [Sortierung](evidence/hz-b/windows-development/hz-b-sort-2560.png) | [Icons](evidence/hz-b/windows-development/hz-b-icons-2560.png), [Druck](evidence/hz-b/windows-development/hz-b-pressed-2560.png) | [Einstellungen](evidence/hz-b/windows-development/hz-b-settings-2560.png), [Dialog](evidence/hz-b/windows-development/hz-b-dialog-2560.png) |

Weitere originale Ansichtsmenü- und Hoverbilder liegen im selben Verzeichnis.
Alle Bilder sind direkte native Ausschnitte ohne Skalierung oder Nachzeichnen.

## Getrennter Selbstreview und Grenzen

Der Implementierer prüft nach den Entwicklungsläufen separat den vollständigen
Diff, die tatsächlichen Originalbilder bei UI-Größe, Ressourcen-/Exportbindung
und die Erhaltungsgrenzen. Befunde und Abschluss werden im PR am geprüften Head
festgehalten. Das bleibt ein Selbstreview und ersetzt **nicht HZ-B-R01**.

Entwicklungs- und Selbstreviewbefunde: Füllpolygone dürfen die offenen Strichüberstände nicht
enthalten (sonst Selbstüberschneidungen); die zusätzliche Triangulationsprüfung
deckt dies ab. Native Checkboxprüfungen scrollen bei kleiner Fensterhöhe vor
dem echten Klick. Historische Unicode-Pfeilannahmen und die exakten CI-/Web-
Inventare werden auf die neue aktive Familie angepasst. Der separate
Hüllencheck begrenzt die maximale Biegung großer Controls auf 5 UI-Pixel bei
7 UI-Pixeln Innenabstand; Eckversatz, stärkste Auswahlkontur und Antialiasing
bleiben damit auch für andere stabile IDs innerhalb des Trefferrechtecks.
Auch native Bestätigungs-/Abbruchbuttons erhalten explizit die 44/55-Pixel-
Mindesttrefferfläche; der Test klickt danach den unveränderten Abbruchweg.
Hover und Gedrückt werden im Kontaktbogen durch echte Zeigerbewegung und
gehaltene Maustaste erzeugt, nicht durch wirkungslose Toggle-Setter simuliert.
Die Originalsichtung zeigte am äußeren Popup-Polster durchscheinende Reste
des geschlossenen Felds. Der Popup-Panelstil füllt deshalb zusätzlich das
gesamte native Rechteck opak; die unregelmäßige Kontur liegt darin. Die
archivierten Entwicklungsbilder zeigen ausdrücklich noch den früheren Stand.
Der folgende Chromiumlauf fand einen durchgereichten Außenklick beim nativen,
eingebetteten Popup. `BookChoice` verbraucht ausschließlich dieses Ereignis im
Eltern-Viewport während das Popup noch sichtbar ist; der native Menüpfad bleibt
zuständig für Auswahl, Scrollen und Schließen. Chromium und der echte Windows-
PCK-Window prüfen das Schließen ohne Aktivierung der darunterliegenden Aktion.
Der zusätzliche SubViewport-Test prüft den Eingabeschutz und liefert die dort
fehlende native Fensterschließbenachrichtigung ausdrücklich separat.
Der KAT-2-Auswahlhelfer wartet nach einer vorausgehenden Größenänderung auf das
fertige Layout, bevor er das Menü an seiner neuen Position öffnet.
Der abschließende Zustandsvergleich fand außerdem identische Scrollbalken-
Darstellungen für Normal, Hover und Gedrückt. Die drei Zustände besitzen jetzt
unterschiedliche Flächen; der gedrückte Griff erhält zusätzlich stärkere Kontur
und Markierung. Auch die Pfeile unterscheiden ihre drei Zustände. Echte native
Zeiger-/Druckereignisse und getrennte Originalaufnahmen prüfen die sichtbare
Pixeländerung; der Ressourcentest prüft beide Pfeile in UI100/125.

**HZ-B-R01** (separater qualifizierter Review) und **HZ-B-M01** (Eigentümerabnahme)
bleiben vor Merge offen. Kein Merge, Deployment oder Issue-Abschluss.
