# HZ-C · Tidy-Hand-Ausrichtung und kleine Schriftrolle

Lieferung zu [#294](https://github.com/venomenon328/picross/issues/294),
auf `main@02b7fcd53b4eef8c94f873314848806eefc265cc`, Branch
`fix/294-tidy-typografie`. Stand: 21.10.2026.
Normativer Umfang: [HZ-D07](HAND_DRAWN_UI.md), A01–A06 im Issue.
Technischer Abschluss, Head/Basis/Checkout/Run/Attempt und Originalartefakte
werden im Implementierungs-PR gebunden. Dieses Dokument erklärt laufende
Prüfungen nicht für bestanden. R01 und M01 bleiben getrennte Mergegates.

## Startfähigkeit und Ursache · A01

HZ-C-P01 wurde vor Produktänderungen auf umsetzungsbereit fortgeschrieben.
Windows 11, interaktiver Desktop, Git-/Pushrechte, CI-/Originaldownload und
offizielle Windows-Engine sind tatsächlich geprüft. Der isolierte Start des
hashgeprüften historischen HZ-B-CI-Spielers diente ausschließlich diesem
Zugangsnachweis. Die HZ-C-Lieferung erhält eigene aktuelle Produktbelege.

Die native Messung trennt vier Pfade:

- Tidy-Hand-Labels und OptionButton/PopupMenu verwenden native Zeilenmetriken.
  Bei 14 beträgt die geformte Tidy-Zeile 13 px Oberlänge und 6 px Unterlänge;
  ein Plex-Fallbackzeichen erhöht die Oberlänge auf 15. Bei 15 sind es 14/6
  beziehungsweise 16/6. Bei UI125 wächst die Differenz auf bis zu 3 px.
  Derselbe Tidy-Buchstabe konnte deshalb mit einem Fallbackzeichen im selben
  Wert seine vertikale Position ändern. Vertikale Labelzentrierung allein
  behebt das nicht.
- `BookButton` zentrierte die tatsächliche Hülle jedes einzelnen Wortes.
  Beispielsweise unterscheiden sich die vertikalen Hüllen von „Neu“ und
  „Begonnen“. Daraus folgten verschiedene Grundlinien beim Wortwechsel.
- Die sichtbare aufrechte Buchstabenfläche und die native Zeilenbox besitzen
  verschiedene Mittelpunkte. Eine passende Controlbox beweist deshalb noch
  keine optische Ausrichtung.
- Status- und Schwierigkeitszeichen verwenden ihre bisherigen geometrischen
  Zeilenmitten. Sie werden zusammen mit dem korrigierten Schriftkörper und
  der unverändert 15 großen Blattkennung beurteilt; ihre Quellen bleiben.

`UiText.small_font(fs)` erzeugt je tatsächlicher Größe eine private
In-Memory-Kopie der unveränderten Fontdatei. Ihre primäre Ober-/Unterlänge
reserviert das gemeinsame gemessene Tidy-/Fallbackmaß. Eine FontVariation
gleicht danach den Mittelpunkt des festen aufrechten Referenzkörpers `Hhx`
aus. Diese Variante ändert weder Glyphenform noch Zeichenbreiten oder
Originalfontbytes. Die Referenz hängt nicht vom angezeigten Wort ab.
Die normale Tidy-Hand-Instanz samt Hilfe-/Dialog-/Tooltipmetriken bleibt erhalten.

Die Chromium-Sichtung fand bei einer zunächst verwendeten Resource-Kopie
beschädigte Glyphen: bereits gefüllte Atlastexturen wurden zwischen Varianten
geteilt. Frische FontFile-Instanzen aus den Originalbytes beseitigen diesen
Fehler; getrennte Font-RIDs und unveränderte Original-Glyphenbitmaps werden
zusätzlich geprüft. Der korrigierte Chromium-Direktvergleich liegt in den gebundenen Originalen vor.

Direkte Papierbuttontexte verwenden dieselbe feste native Referenzgrundlinie;
die tatsächliche Worthülle bestimmt weiterhin ihre horizontale Ausrichtung.
Ganzzahlige horizontale Textursprünge erhalten zusätzlich das native
Anfangsglyphenraster beim Wortwechsel. Eine echte Gegenprobe mit der alten
vertikalen Wortzentrierung wird von acht Pixelprüfungen zurückgewiesen.
Labels erhalten symmetrisches, aus den tatsächlichen Akzent-/Unterlängen-/
Fallbackhüllen bestimmtes Sicherheitspolster. Es erhält den optischen
Mittelpunkt und verhindert, dass der Grundlinienausgleich Unterlängen abschneidet.
Native Felder und Popupzeilen behalten ihre passenden eigenen Innenabstände.

Der erste vollständige CI-Lauf am Zwischenhead `f0338f9` fand zusätzlich eine
zu schmale Kategorienauswahl bei 1280×720/UI125. Der native Pfeil kam zur
bereits dafür vergrößerten rechten Styleboxreserve hinzu; größere Textbuttons
verbrauchten weiteren Kopfplatz. Der erste Korrekturschritt bestand zwar das
alte Zeichenbreitenorakel, zeigte im Originalframe aber weiterhin eine Ellipse.
Die Lieferung verwendet deshalb einfache gemessene Innenränder, die native
Sortierfeldmindestbreite, sichere Textbuttonränder und bei engem UI125 mehr
der vorhandenen sicheren Papierbreite (64 statt 90 logische Seitenabstände).
Die vertikalen Karten-/Bildbudgets bleiben erhalten. Ein zusätzlicher nativer
Ein-Element-Vergleich prüft den vollständigen üblichen Kategorienamen samt
Pfeil und Rändern; das bisherige Orakel bleibt unverändert erhalten.

## Größenentscheidung und Layout · A02–A04

Die Implementiererwahl lautet **15 bei UI100, 19 bei UI125** für Kategorie,
Größe, Schwierigkeitsname, Status, geschlossene/offene Dropdowns und die
betroffenen kleinen Papiertextbuttons. „Blatt NN“ bleibt 15/19. Die korrigierten
14/18 und 15/19 werden unter gleichen Bedingungen mit den tatsächlichen
Karten-, Dropdown- und Buttonkomponenten nebeneinander nativ aufgenommen.
15 verbessert die Lesbarkeit und die ruhige Anordnung insbesondere langer
Metadaten; 14 wirkt im direkten Vergleich enger. Diese technische Wahl ist
keine vorweggenommene Eigentümersichtabnahme M01.

Die Kategorie bleibt oben im festen zweizeiligen Bereich. Ein kurzer Name
wird nicht nachträglich darin zentriert. Fußzeile und Metadatenzeile verwenden
eine gemeinsame sichere Zeilenhöhe; Blattkennung, Status und Symbol behalten
ihre gegenseitige Anordnung. Breitenmessung, lange Metadaten, Zeilenhöhen,
Kartenmindestbreite und Rückwechsel verwenden dieselbe gewählte kleine Rolle.
Bildhöhe bleibt mindestens 112 × UI, Treffer bleiben mindestens 44/55 px.
Überschriften, normale Fließtexte, Hilfe, Dialoginhalt und Tooltips werden nicht
global vergrößert. HZ-B-Konturen und Symbolquellen bleiben unverändert.

## Gezielte Nachweise · A05–A06 / T01

| Ebene | Aktueller ausführbarer Nachweis |
| --- | --- |
| Metriken | `hz_c_cases.gd` im Kernlauf: Größen 14/15/18/19, feste native Grundlinie auch mit Fallback, unveränderte Glyphenbreiten und Normaltextmetriken, sichere Hüllen sowie Gegenbeispiel für die alte wortabhängige Zentrierung. |
| Windows-Darstellung | `hz_c_native.gd` im vorhandenen KAT-2-Modus `kk`: tatsächlich gerenderter gemeinsamer Anfangsbuchstabe bleibt beim Wort-/Fallbackwechsel pixelgleich; feste Kategorieposition, gleiche Fußbereiche, Statusfolge, drei native Dropdownarten und UI125→100→125→100. |
| Vergleich | `hz_c_sample.gd` baut die tatsächlichen Komponenten für korrigierte 14/15 unter gleichen Bedingungen. Originalframes und gemessene Ausgangs-/Zielmetriken stehen in `kk.json`/`hzc_measurements`. |
| Chromium | `HZ-C-W01` in `catalog`: echte Maus-/Tastatureingabe, alle drei Dropdownarten offen/geschlossen, Größen-/Volltext-/Fußzeilenbeobachtung, UI-Rückwechsel und erhaltene Zell-/History-/Abschlusswerte. Die Probe liest ausschließlich Zustand. |
| Regressionen | Bestehende HZ-A/B-, KAT-2-/KU-/KE-, Kern-, Save-/Recovery-, Hinweis-/Raster-, Ressourcen-/PCK- und Browserprüfungen bleiben laut tatsächlicher automatischer Auswahl erforderlich. |
| Exportierter Windows-Spieler | `hz_windows_probe.py`: aktuelle CI-Originalarchive samt Digest, EXE/PCK, offizieller Editor, isolierter echter Windowstart, PCK-Rollenprüfung, serieller Prozessneustart und native Katalogrouten. Bericht ausdrücklich HZ-C, R01/M01 offen. |

Darstellungsbasis: 1280×720/UI125, 1920×1080/UI100 und 2560×1440/UI125;
der zusätzliche Rückwechsel prüft 1920/UI100. Keine neue vollständige Kreuzmatrix.
Die nativen `hz-c-*.png`-Ausschnitte und 15 Chromium-Originale stehen im
verbindlich erweiterten Beleginventar. Es wird weder skaliert noch nachgezeichnet.
Die Windows-/Chromium-Belege des finalen technischen Stands sowie der getrennte
vollständige Selbstreview werden im PR mit Originalhashes gebunden. Der
Selbstreview erfüllt ausdrücklich nicht HZ-C-R01.

Die [dauerhaft archivierten Entwicklungsoriginale](evidence/hz-c/README.md)
bewahren insbesondere den direkten korrigierten 14/15-Vergleich in Windows und
Chromium einschließlich ganzer geöffneter Vergleichsmenüs. SHA-256-Bindungen
und die tatsächlichen temporären Einstiege legen ihre Quellen-/Gategrenzen offen.

### Tatsächlich ausgeführter Runtime-Abschluss

Der saubere Runtime-Head `5075e1bf883e18e24b9802118047a110ea2bf7f0` ist in
[CI 39578546117, Attempt 1](https://github.com/venomenon328/picross/actions/runs/39578546117)
vollständig erfolgreich: sechs Bereiche, sieben native und fünf Chromium-Gruppen;
`ci-required` akzeptiert 1.053 native Dateien und alle 33 Chromium-Szenarien.
Der tatsächliche Integrationscheckout
`46b56de206e2cd63e38eeb41814da1c79a915ab8` besitzt denselben Dateibaum.
Der Kernlauf bestand 17.247 Prüfungen ohne Fehler.

Der echte Windows-Lauf verwendet die unveränderten CI-EXE-/PCK-Originale:
eigener HWND-Start ohne Testargumente, Client 1920×1080, DPI 96, Exit 0;
316 PCK-Prüfungen und 316 im getrennten Prozessneustart, jeweils ohne Fehler.
Alle elf nativen Katalogmodi bestehen 7.719 Prüfungen, darunter KK/HZ 3.496.
Renderer ist NVIDIA GeForce RTX 3070; sämtliche 1.053 CI-Technikdateien wurden
vor Verwendung erneut validiert. Die vollständigen 73 Chromium-Dateien sind
ebenfalls erneut gegen das Browsergate geprüft.

[Originalarchive, Inventare und genaue Bindungen](evidence/hz-c/README.md)
erhalten diese tatsächlichen Identitäten. Der anschließende reine Dokument-/
Archivcommit ändert keine Laufzeit-, Test- oder Werkzeugdatei; seine eigene
Pflicht-CI und der getrennte vollständige Selbstreview werden im PR gebunden.
Die Windows-Nachweise werden mit unveränderten relevanten Voraussetzungen
gemäß WORKFLOW §8 wiederverwendet, ohne ihre Quellidentität umzubenennen.

## Erhaltung und offene Gates

Keine Änderung an Fontbytes, Fremdassets, Rätseln, Reveals, Bewertungen,
Sortiersemantik, IDs, Saveformaten oder echten Speicherprofilen. Keine Änderung
von Delight-Hinweisen, Raster-/Fit-/Draggeometrie, Symbolquellen, großen
SL-Rasterrahmen oder CI-Auswahlpolitik. Neue technische Fälle und ihre
Pflichtbilder erweitern die vorhandenen Prüfrouten.

**HZ-C-R01:** separater qualifizierter Review des finalen Diffs und der
gebundenen technischen/visuellen Originalbelege, vor Merge.
**HZ-C-M01:** Eigentümer beurteilt am gebundenen Build Ausrichtung, Endgröße,
Kategorien, Statusfußzeile, vollständige Metadaten und Dropdowns bei UI100/125,
vor Merge. Issue #294 bleibt bis zur vollständigen Abnahme offen.
Kein Merge, Release oder Deployment ist beauftragt.
