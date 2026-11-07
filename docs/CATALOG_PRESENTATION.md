# Katalogdarstellung und unbekannte Motive · KU

## K-B: zuletzt bearbeitetes Rätsel

[Paketentscheidung #485](https://github.com/venomenon328/picross/issues/485#issuecomment-6705799391).
Die rechte Buchkopfzone oberhalb von Sortierung und Filter enthält ein reduziertes,
als Ganzes anklickbares Panel: links „Zuletzt bearbeitetes Rätsel fortsetzen“ und
neutrale Blattkennung/Dimensionen, rechts eine 56 × UI große eigene Fortschrittsminiatur.
Die Textzeilen sind gemeinsam vertikal zentriert, links um 12 × UI eingerückt.
Der Kasten sitzt mit 8 × UI Abstand unmittelbar über Sortierung/Filter;
Zusammenfassung und der feste scrollbare Meldungsbereich stehen darüber.
Sie ist kleiner als die reguläre Kartenvorschau und verrät weder Lösung noch Motivname.
Ohne gültigen begonnenen, unvollständigen Stand bleibt das Panel verborgen. Abschluss
oder Reset entfernt das Angebot sofort; es gibt keinen Rückfall auf ältere Rätsel.
Die feste Kopfzone hält Zusammenfassung, Panel und scrollbare Fehlermeldungen getrennt;
Kartenmaße, Filter und Sortiercontrols werden durch Fehler nicht verschoben.
Die ID-gebundene Buchroute erhält Kategorie, Filter, globale Seite und beide Scrollstände,
auch wenn die Karte des Ziels ausgefiltert ist. Ein Merkerfehler hat einen eigenen
nichtmodalen Retry im Meldungsbereich; er sperrt andere Rätsel oder das Beenden nicht.

**PANG-A / #531 · auf dem Arbeitsbranch implementierte normale Schriftrolle:**
Gemäß [HZ-D08](HAND_DRAWN_UI.md) ersetzt Pangolin Regular Tidy Hand
in vorhandenen normalen Katalogtexten einschließlich Kategorie, Metadaten,
Status/Blattkennung, Sortier-/Auswahlbeschriftungen und Tooltips. Die darunter
dokumentierten Tidy-Hand- und HZ-C-Angaben beschreiben den integrierten
Ausgangsstand; Bakso-Motivtitel, vollständige Angaben, gemessene Budgets und
Karten-/Bild-/Resetgeometrie bleiben verbindlich. [PANG-A](https://github.com/venomenon328/picross/issues/531).


**Prüfumfang P2-E-A-V02 / #502:** Die Produktregeln dieses Dokuments bleiben
unverändert. [D02](https://github.com/venomenon328/picross/issues/502#issuecomment-6655391391)
autorisiert den risikobasierten Abbau kosmetischer nativer KE-/KK-Kreuzprodukte.
Der [aktuelle Stichprobenvertrag samt akzeptierten Prüflücken](CI_C_NATIVE_GROUPS.md)
hat für die wiederkehrende Prüfung Vorrang vor älteren vollständigen
Metadaten-/Tooltip-/Größenmatrizen. Keine Ablösung der Methodenunterstützung,
Spoiler-, Save-/Recovery- oder übrigen Kataloggarantien.

**B-B / #498:** Die [reguläre Buchdarstellung](BOOK_INTEGRATION.md) verteilt eine
logische Katalogseite auf beide Buchhälften. Höchstens 24 aktive Karten,
vollständige Schrift-/Metadaten-/Bild-/Resetbudgets und ID-Aktionen bleiben.
Knappere Flächen verwenden weniger Spalten und Scrollen. Die revidierten Abstände
folgen projizierter Papierkante und ruhender Falzwölbung. Der reguläre Katalog
verwendet die integrierte B-B-Darstellung; bisherige KU-/HZ-Abnahmen bleiben gebunden.
N03 entfernt den isolierten Hoverstrich und leere Tooltippanels, erhält sinnvolle
Modus-/Reset-/Richtungshilfen und prüft deren verzögerte native Mauswege.
N04 füllt zuerst die linke Hälfte bis zwölf Karten, dann die rechte bis zwölf;
Spaltenzahl und Scrollen verändern die Mitgliedschaft nicht. Beide Hälften
scrollen getrennt. Kopf, Clipbereiche und Fußaktionen folgen einer einheitlichen
Papierprojektion einschließlich des gezielten 1920×1200-Nachweises.
N05 ergänzt neben dem Einstellungenzugang einen direkten Hilfezugang. Bei
knapper Breite erhält die Fußnavigation eine zweite Zeile ohne kleinere Buttons.
Beide Informationswege führen zum unveränderten Katalogkontext mit zwei Offsets zurück.

**KL-A / #523 · Layoutimplementierung vom 06.11.2026 (Abnahmen im Issue/PR):**
Das vorhandene Buch verteilt weiterhin je zwölf Karten links und rechts.
Das responsive Layout bestimmt maximal drei Spalten aus der schmaleren sicheren
Kartenfläche beider Hälften und zentriert jede belegte Zeile eigenständig.
Der flache Zeilencontainer erhält Karten und ID-Callbacks beim Umbruch;
Filter-/Seitenwechsel behalten ihren bisherigen begrenzten Neuaufbau.
Verbindlich ist [KL-D01](#kl-d01--responsives-katalograster-523); tatsächliche
Prüfstände und getrennte Abnahmen stehen in [#523](https://github.com/venomenon328/picross/issues/523).

**HZ · HZ-A/B/C integriert; aktuelle Abnahmeentscheidungen in #284/#294:**
[Handgezeichnete Bedienoberfläche](HAND_DRAWN_UI.md) verwendet Tidy Hand für normale
Katalogtexte bei unveränderten Bakso-Überschriften und organischeren stabilen
Kartenkonturen. HZ-A/B sind über PR #288/#289 integriert und in #284 abgenommen.
HZ-D07 ergänzt optische Ausrichtung, stabile Grundlinien und den begründeten
Vergleich der korrigierten kleinen Schriftgröße 14/15 einschließlich Kategorien.
Papierstreifen, vollständige Metadaten, gleiche Kartenbereiche, Bildraum und
Bedien-/Spoilergrenzen bleiben verbindlich.

**AT · Abschlussbildtransparenz:**
Der [Transparenzstandard](REVEAL_TRANSPARENCY.md) ergänzt die verdienten
Katalogbilder. AT-A liefert den begrenzten Bildänderungsweg mit synthetischen
Alpha-/Spielstandsnachweisen; die AT-B-Bestandsübernahme verwendet
konkreter neuer Bildfreigabe. Kartenaufteilung und ungelöste Vorschauen bleiben erhalten.

Fachstand: Spezifikation 2.3 · Workflowabgleich: 06.11.2026 · KU-A/B und HZ-A/B/C integriert; KL-D01 freigegebener Sollstand

## K-A · Kombinierbare Sitzungsfilter (#485)

[Die Paketentscheidung K-A](https://github.com/venomenon328/picross/issues/485#issuecomment-6704440743), die [bestätigte Bedienpräzisierung](https://github.com/venomenon328/picross/issues/485#issuecomment-6704732025)
und die [Größenpräzisierung](https://github.com/venomenon328/picross/issues/485#issuecomment-6704802593) binden die Umsetzung und ihre getrennten Gates. Der Katalog führt einen gemeinsamen
angewendeten Sitzungszustand: Kategorie, Status (Alle/Noch offen/Neu/Begonnen/Gelöst),
Modus (Alle/Monochrom/Farbe), optionale inklusive Schwierigkeit von/bis L1–L5 und
optionale maximale Breite/Höhe von je 1–99 Zellen. Alle Achsen gelten gemeinsam mit UND für den
vollständigen sichtbaren validierten Bestand. Danach folgen das unveränderte
Sortierpaar, 24er-Seiten und die unveränderte 12/12-Zuordnung mit KL-Raster.

Status verwendet dieselbe geprüfte Session wie die Karte: Abschluss vor History
(einschließlich Redo) oder wirksamen Zellwerten, leerer Save allein bleibt Neu.
Ungültige Saves zählen zu keinem spezifischen Status, auch nicht Noch offen.
Alle erhält ihre Diagnose-/Resetwege bei passenden Metadaten; gültige rekonstruierte
Stände behalten ihren Status und ihre Recoveryaktion. Ein Savefehler bleibt auch
außerhalb der Treffer sichtbar. Modus bezeichnet das Rätsel. Schwierigkeit verwendet
nur vorhandene validierte Werte: ohne Grenzen einschließlich fehlender Stufe,
mit mindestens einer Grenze ausschließlich eingestufte passende Rätsel. Breite und Höhe
werden separat einschließlich ihrer Grenzen geprüft, ohne die Orientierung zu
vertauschen. Leere Felder sind jeweils unbeschränkt; beide Maßgrenzen gelten
bei gemeinsamer Auswahl mit UND.

Der Button **Filter** steht rechts neben Sortierauswahl und Richtungspfeil,
mit 16×UI horizontalem Textinnenraum je Seite auch unter Fokus/Druck. Er
öffnet ein handgezeichnetes Papierpanel mit den zusätzlichen
Achsen. Die Schwierigkeitsfelder **Von/Bis** stehen nebeneinander und zeigen nur
die Bezeichnungen Sehr leicht bis Sehr schwer ohne L-Präfix. Die Dropdowns begrenzen einander auf auswählbare Stufen
mit Minimum ≤ Maximum. Bei Bedarf folgt die Gegengrenze der zuletzt geänderten;
gleiche Stufen und je ein unbeschränktes Ende bleiben möglich. Eine widersprüchliche
Spanne kann nicht ausgewählt werden und erzeugt keine Fehlermeldung.
Die Größenzeile enthält **Breite** und **Höhe** mit schmalen, auf zwei Stellen
begrenzten Eingabefeldern nebeneinander. Labels und Auswahlen sind in gemeinsamen
Spalten ausgerichtet. Jedes Maßfeld schließt rechtsbündig unter seinem
Schwierigkeitsdropdown ab und behält seine schmale Breite. Die Filtergrenze 99 erweitert nicht die Rätselgrenze 50×50.
**Übernehmen** wendet den gesamten gültigen Entwurf an. Andere als leere oder
positive ganzzahlige Breiten/Höhen bis 99 erhalten eine sichtbare Fehlermeldung;
die letzte gültige Auswahl und Trefferliste bleiben bestehen. Schließen verwirft den Entwurf. Bei knapper Höhe
scrollt der Panelinhalt. Die Höhe folgt dem tatsächlichen Inhalt statt einer
festen Leerfläche; nur nötiger Platzbedarf vergrößert sie. Übernehmen /
Zurücksetzen / Schließen bilden eine Zeile mit drei gleich großen Buttons. Kartenminimum,
Bildhöhe, Schriftrollen, Kopf/Fuß und Falzabstände bleiben erhalten.

Echte Filteränderungen setzen Seite und beide Scrollstände auf null; dieselbe
Auswahl ist ein No-op. Rückkehr aus Arbeits-/End-/Informationsansicht erhält den
angewendeten Zustand, Sortierung, Seite, beide Offsets und passende Auswahl-ID.
Abschluss/Reset aktualisieren die Treffer vor Seiten-/Offsetbegrenzung; entfällt
die letzte Seite, beginnt die begrenzte Seite oben. **Zurücksetzen**
neutralisiert Kategorie und alle zusätzlichen Achsen, erhält das Sortierpaar.
Diese Aktion steht ausschließlich im Filterpanel. Katalog-/Speicher- und
Sortierfehlermeldungen stehen im festen freien Kopfbereich der rechten Buchseite
über Sortieren/Filter. Bei Überlänge scrollt nur diese Meldungsfläche; Ein-/Ausblenden
verschiebt weder Kacheln noch Katalogcontrols. Entwurfsfehler stehen oben
im Filterpanel.
Trefferzahl, leerer Trefferbestand, gültiger leerer Katalog und Ladefehler sind
unterscheidbar. Ein neuer Prozess startet ohne Filter, bei Alle/Seite 1/oben.
Es gibt keine Filterpersistenz, zusätzlichen Einstellungen oder K-B-Fortsetzen-Aktion.

Die günstige Dauerregression liegt im vorhandenen synthetischen `catalog/pages`-
Prozess. Die einmalige echte Windows-Buchsicht K-A-T02 und die getrennten
K-A-R01/M01 vor Merge werden am konkreten Produkt-Head im PR nachgewiesen;
Selbstreview ist keine unabhängige oder persönliche Abnahme.

## KL-D01 · Responsives Katalograster (#523)

**Eigentümerfreigabe 06.11.2026: Sollstand, keine Implementierungs- oder
Sichtabnahme.** Der Katalog soll freie Papierbreite besser nutzen, ohne die
bestehende Karten-/Buchfunktion zu ändern. Maßgeblich ist die *tatsächlich
nutzbare Breite pro Buchhälfte* nach Papierprojektion, Falz- und sicheren
Innenrändern, vorhandenen Kopf-/Fußaktionen, Scrollbereich und UI-Skalierung;
eine feste 1440p-Auflösungsabfrage ist unzulässig.

Pro physischer Buchseite bleiben **höchstens zwölf Karten**, mit globaler
Filterung/Sortierung vor der unveränderten 24er-Paginierung und Zuordnung
zuerst links, danach rechts. Beide Hälften haben dieselbe aus **gemessenen**
Kartenmindestbreiten und jeweiligen Innenbreiten sicher bestimmte Spaltenzahl:
**höchstens drei**, bei genügend Platz drei, sonst zwei oder im engen Grenzfall
eine. Normalerweise entspricht dies bei drei Spalten **4×3** und bei zwei
Spalten **6×2** Kartenpositionen je Buchhälfte. Diese Reihen sind logisch
angeordnet; die vorhandene unabhängige vertikale Scrollmöglichkeit bleibt bei
geringer sichtbarer Höhe bestehen. Es werden weder Karten hinzugefügt noch
Seitenmitgliedschaften oder IDs durch den Umbruch geändert.

**Jede belegte Zeile wird innerhalb ihrer Buchhälfte eigenständig horizontal
zentriert**, auch eine letzte Zeile mit weniger Karten als Spalten. Ein nur
insgesamt zentriertes Grid mit linksbündiger Teilzeile erfüllt dies nicht;
leere unsichtbare Karten-/Hitbox-Platzhalter sind ebenfalls kein Ersatz.
Gleich große Karten, ruhige symmetrische Abstände und stabile Konturen bleiben.
Vorhandener Freiraum darf durch **behutsame Verringerung des Überschusses**
zwischen Mindestkartenbreite und Wunschkartenbreite sowie maßvolle äußere
Karten-/Zwischenabstände besser genutzt werden; es gibt kein pauschales
Schrumpfen unter die Mindestbreite.

**Die verbindlichen Inhaltsbudgets aus KE-D01/HZ-D02/D07 bleiben erhalten:**
vollständige einzeilige Größe, Schwierigkeit (einschließlich „Nicht eingestuft“
und „Sehr schwer“) und Moduspiktogramm, die abgestimmte kleine Schriftrolle
15/19 bei UI100/125, Kategorie-/Titelfläche, vorreservierter Resetplatz,
Fußzeile und Bildhöhe mindestens 112×UI bei proportionalem Fit. Die bislang
geprüften rechteckigen Trefferflächen mindestens 44×44 bzw. 55×55,
zeichnerische Konturüberstände, Fokus/Tooltips sowie Fehler-/Recoveryaktionen
dürfen nicht geclippt, überdeckt oder funktionslos werden. Kein verkleinerter
Pflichttext, kein abgekürzter Schwierigkeitsname und keine neuen
Metadatentooltips zur Platzkompensation.

**Angestrebte sichtbare Geometrie:** Im regulären nativen 3D-Buch soll
2560×1440/UI100 mit zwölf Karten **drei Spalten und vier Zeilen** je Hälfte
erreichen. Bei 1920×1080/UI100 sind normalerweise **zwei Spalten/sechs Zeilen**
sinnvoll. UI125, 1920×1200 und enge Größen dürfen entsprechend gemessener
Grenzen zurückfallen. Eine unlesbare Dreispaltenansicht ist kein Erfolg;
1440p/UI125 ist keine pauschale Drei-Spalten-Garantie. 720p ist ein
Fallbackfall. Verifikation muss tatsächliche Buchprojektion, Scroll-/Clip-
und Kartenmaße nachweisen; Setup/Quellinspektion allein genügt nicht.

Bestehende ID-gebundene Öffnung, Reset und Backup-/Recovery, beide
Scrollpositionen, ausgewählte Karte, Filter/Sortierung, Fokus, Scroll-Restore
und Capture/Seitenanimation bleiben beim Umbruch, Resize und UI100→125→100
erhalten. Der Inhalt bleibt spoilerfrei: neue Karten zeigen das Fragezeichen,
begonnene nur eigene Füllungen und abgeschlossene ihr verdientes Reveal.
Weder Rätsel-/Save-/Registry-/Präferenzdaten noch Buchkörper, Falz, Fonts,
Bildassets oder bestehende Animationszeiten werden geändert.
[BOOK_INTEGRATION](BOOK_INTEGRATION.md) bindet die doppelseitige Präsentation;
das konkrete Paket, seine Akzeptanz A01–A07 und die maßvolle Modulprüfung
stehen in [#523](https://github.com/venomenon328/picross/issues/523).
[Zusätzliche Katalogfilter und Wiedereinstieg](https://github.com/venomenon328/picross/issues/485)
bleiben ausdrücklich unabhängig.

**KL-A-Ausführung:** `ui/catalog_grid.gd` ordnet die vorhandenen Kartenwrapper
direkt an; eine Teilzeile reserviert nur ihre tatsächlichen Karten. Beide
Scrollflächen reservieren die jeweilige reale Balkenbreite plus 2×UI, auch bei
verborgenem Balken. Kapazität und gemeinsame Kartenbreite folgen der schmaleren
Fläche; jede Zeile zentriert sich in ihrer eigenen sicheren Kartenfläche.
Die Wunschbreite beträgt gemessenes Minimum plus höchstens 8×UI statt zuvor
16×UI; Innenränder, Schrift, Titel/Reset, Metadaten und Bildhöhe bleiben gleich.
Die native kleine Layoutregression läuft ausschließlich mit `native.catalog`
im vorhandenen synthetischen pages-Prozess. Einmalige echte Buchdarstellungen
und unabhängiges KL-A-R01 bleiben von dieser Komponentenprüfung getrennt.

---

Der Eigentümer hat die Katalogüberarbeitung am 18.10.2026 als Spezifikation
freigegeben. [Gesamtissue #244](https://github.com/venomenon328/picross/issues/244)
führt KU-A (Karten und Papierstreifen) und KU-B (Sortierung und Hinzugefügt-Metadaten),
ihre Akzeptanz und getrennten technischen, Review- und Eigentümergates.
KU-A ist über PR #254 und KU-B über PR #255 integriert.
[KU-A](KU_VERIFICATION.md) und [KU-B](KU_B_VERIFICATION.md) trennen ihre
technische Lieferung, Reviews und offenen persönlichen Abnahmen auf `main`.
HZ übernimmt weder diese Abnahmen noch damalige Mergeausnahmen.

## Geltung und gezielte Ablösung

Historische KU-Spezifikationsbasis ist `main@72ba39391833f6fd834d0a6afaf881c86c7bdc3a` mit
integrierter KE-Katalogdarstellung aus
[#233](https://github.com/venomenon328/picross/issues/233)/PR #234 und dem
bestehenden SD-Bewertungsweg. KU-A löst gezielt die zweizeilige KE-Infobox,
sichtbare Schwierigkeitsziffer, Monochrom-Farbprobe, Schwierigkeitstooltips und
Statusdarstellung im Etikett einschließlich des sichtbaren Wortes „Fertig“ ab.
KU-B ergänzt die bisher fehlende Sortierung gemäß
[Katalogsortierung](CATALOG_SORTING.md).

Die Abschnittskennungen KE-D01–D06 bleiben als Verweisziele erhalten und führen
nachfolgend den fortgeschriebenen Vertrag. Die KU-A-Implementierung setzt die
Kartenänderungen um; die Sortierung bleibt KU-B. Historische KE-/KK-/KB-/EA-Nachweise
und damalige Abnahmeentscheidungen werden weder geändert noch erneut geöffnet.
Gleiche Karten, Reservierung von Titel/Reset, Fehler-/Recoveryzugriff,
Spoilergrenze, Öffnen über die Karte und lokale Revealglättung bleiben verbindlich.

[Produktdefinition](PRODUCT_DEFINITION.md), [Gestaltungskonzept](DESIGN_CONCEPT.md),
[Zeichensprache](UI_DRAWING_STYLE.md), [Kategorien](CATEGORIES.md),
[ZA-1](ZA1_ADAPTER.md), [P1](PROTOTYPE_P1.md) und [CI-Policy](CI_POLICY.md)
gelten im übrigen Umfang weiter. Historische Prüfberichte bleiben unverändert.

## KE-D01 · Feste Kartenaufteilung

Alle Karten und Grid-Zellen haben bei gleichem Viewport und UI-Faktor dieselbe
Größe. Reihenfolge von oben nach unten:

1. Motivtitel erst nach gültigem Abschluss, sonst `???`; vorhandene Bakso-Rolle,
   höchstens zwei Zeilen mit bestehender Auslassungsregel. Reset oben rechts;
   sein Platz bleibt auch bei verborgenem Reset reserviert.
2. Kompakte Kategoriezeile: in „Alle Rätsel“ befüllt, bei Kategorienfilter leer
   und weiterhin reserviert.
3. Fester proportionaler Bildraum für Fragezeichen, eigene Füllminiatur,
   verdientes Reveal oder bestehende Fehler-/Recoverydarstellung.
4. Ein passiver Papierstreifen mit genau einer gemeinsamen Metadatenzeile.
5. Feste Fußzeile mit „Blatt NN“ links und Statussymbol samt Statuswort rechts.

| Papierstreifen | Inhalt |
| --- | --- |
| Links | Breite × Höhe, etwa `20 × 15` |
| Mitte | Gefüllter Schwierigkeitskreis und vollständige Bezeichnung |
| Rechts | Gezeichnetes Mono-/Farbpiktogramm |

Die drei Angaben stehen vertikal ausgewogen in derselben Zeile mit klaren
Abständen; keine drei Einzelkästchen und keine zweite Metadatenzeile.
Der Status steht ausschließlich in der Fußzeile. Größe und Modus werden nicht
zusätzlich sichtbar an anderer Stelle derselben Karte wiederholt. Das Etikett bleibt
passiv: Klick öffnet dieselbe Karte; Reset und Recoveryaktionen behalten ihre
eigenen vorhandenen Aktionen. KU-A ergänzt keine Filter, Sortieroptionen oder
Fortschrittsanzeigen; die separate KU-B-Sortierung verändert diese Kartenregel nicht.

Die bisherige Kartenbreite von ungefähr 220–240 logischen Pixeln ist keine neue
Breitengarantie. Etwa 260–280 logische Pixel für Karten, 28–32 für Moduspiktogramme
und 12–14 für Schwierigkeitskreise dienen ausschließlich als Entwurfsstart bei
UI 100 %, nicht als bereits gemessene Fit-Zusage oder starre Grenzwerte.
Die gemeinsame Mindestbreite wird aus tatsächlichen Volltextmaßen, Symbolhüllen,
Innenrändern und Abständen bestimmt. „Nicht eingestuft“, „Sehr leicht“ und
„Sehr schwer“ müssen mit Größe und Modus bei UI 100/125 % vollständig und
einzeilig lesbar bleiben. Keine kleinere Metadatenschrift, Abkürzung oder
Auslassung als Ersatz für ausreichende Breite; bei Bedarf sinkt die Spaltenzahl.

Bei gleichem Viewport und UI-Faktor bleiben alle Karten gleich groß, unabhängig
von Text, Modus und Status. Der feste proportionale Bildraum behält ausreichend
Platz; die bisherige Bildhöhe von 112 × UI darf nicht zur Unterbringung der
Metadaten verkleinert werden. Eine gemeinsam angepasste Kartenhöhe ist erlaubt.
Kategorie, mehrzeiliger Titel, Status, Reset und Fehlertexte funktionieren ohne
Überlappung und ohne zustandsabhängige Layoutsprünge. Der bestehende
Titelauslassungsvertrag bleibt von den vollständigen Metadaten getrennt.

HZ-D02/D03 ergänzt die gemessenen Tidy-Hand-Textmaße und die sichtbaren Hüllen der
neuen äußeren Kartenkontur einschließlich Überständen und Kantenglättung.
Diese passen in dieselben sicheren Karten-/Trefferbudgets; Sortierung oder
Neuaufbau verändert bei gleicher ID und Größe nicht die gezeichnete Grundform.

[HZ-D07](HAND_DRAWN_UI.md) präzisiert die optische Textausrichtung: stabile
Grundlinien pro Rolle/Größenstufe, keine wortabhängigen Höhenwechsel zwischen
„Neu“, „Begonnen“ und „Gelöst“. Blattkennung, Statuswort und Statussymbol werden
als gemeinsame Fußzeile betrachtet. Die Kategorie behält ihre feste Position im
reservierten, bis zu zweizeiligen Bereich; ein- und zweizeilige Namen werden
nicht jeweils neu darin zentriert.

Der [direkte Vergleich](HZ_C_VERIFICATION.md) der korrigierten kleinen Größen
14/15 unter gleichen Bedingungen begründet die Wahl 15 bei UI100 und 19 bei
UI125 für Kategorie, Größe, Schwierigkeit und Status. „Blatt NN“ bleibt 15/19.
Die tatsächliche separate Eigentümersichtabnahme M01 wird in #294/PR #296 geführt. Textmaße und gemeinsame Kartenmaße
werden zusammen angepasst; die oben genannten Volltext-/Bildraumgrenzen bleiben.

## KE-D02 · Papieretikett und Moduspiktogramm

Der gemeinsame Streifen wirkt wie ein ruhiges Papieretikett des Rätselbuchs:
warmes Papier, leicht dunkler als die Kartenfläche, dünne subtil unregelmäßige
Kontur, höchstens ein sehr zurückhaltender Schatten. Keine drei gerahmten
Einzelfelder und kein schwerer Schmuckrahmen. Als freigegebener HZ-Sollstand
verwenden Metadaten Tidy Hand gemäß HZ-A-FONT02 und
[HZ-D01/D02](HAND_DRAWN_UI.md), mit gemessenen Textmaßen und lokalen Fallbacks.
Die bisherige Plex-Metadatenrolle ist damit abgelöst; Originalfontbytes bleiben.
Charakter entsteht gemeinsam durch Schrift, Kontur, Zeichnungen und Abstände. Streifen,
Kreise und Stifte bleiben statisch.

| Rätselmodus | Zeichnung | Erklärung im gezielten Tooltip |
| --- | --- | --- |
| Monochrom | Ein einzelner dunkler Stift ohne Farbprobe | Monochromes Rätsel |
| Farbe | Drei aufgefächerte Stifte in gedecktem Rot, Blau und Gelb | Farbiges Rätsel |

Die Silhouette beziehungsweise Anzahl der Stifte unterscheidet die Modi auch ohne
Farbwahrnehmung. Alle Farbrätsel verwenden dasselbe Symbol; keine tatsächliche
Palette und keine Motivinformation. Der Modus beschreibt das Rätsel, nicht das
Abschlussbild: Auch ein monochromes Rätsel erhält sein farbiges Reveal.
Der Monostift wird nach Entfernung der Farbprobe im eigenen Symbolraum neu
zentriert; der bisher für das Gekritzel vorgesehene Leerraum bleibt nicht bestehen.
Beide Modussymbole werden gegenüber der KE-Ausgangsdarstellung größer und nach
ihren tatsächlichen sichtbaren Hüllen ausgerichtet. Der Entwurfsstart von 28–32
logischen Pixeln ist zusammen mit der Kartenzeile bei UI 100/125 % zu prüfen.

## KE-D03 · Schwierigkeit ohne neue Bewertung

| Vorhandene Stufe | Sichtbare Bezeichnung | Gefüllter Kreis |
| --- | --- | --- |
| L1 | Sehr leicht | Gedecktes Grün, `#52734e` |
| L2 | Leicht | Oliv, `#74713e` |
| L3 | Mittel | Ocker, `#997337` |
| L4 | Schwer | Rost, `#a36342` |
| L5 | Sehr schwer | Gedecktes Rot, `#9b514b` |
| Keine Einstufung | Nicht eingestuft | Neutralgrau, ohne Stufenzuordnung |

KU-A ersetzt die farbig akzentuierte KE-N1-Ziffer durch einen gefüllten Kreis in
derselben bestehenden Stufenfarbe. Der vollständige Name bleibt unmittelbar
dahinter in dunkler UI-Schrift gemäß HZ-D01 und trägt die Bedeutung auch ohne
Farbwahrnehmung. Kein sichtbarer Zahlenwert, keine Sterne und keine
Schätzkennzeichnung `≈`. Alle Kreise haben dieselbe Größe; eine dezent gezeichnete
Kontur darf die klar gefüllte Kreisform nicht auflösen. 12–14 logische Pixel sind
der Entwurfsstart; Lesbarkeit und gemeinsame Zeilengeometrie bestimmen das Endmaß.

„Nicht eingestuft“ bleibt neutral, erhält weder Null noch eine der fünf
Stufenfarben und wird nicht als sehr leicht behandelt. Die genaue neutrale
Graunuance folgt dem vorhandenen Papier-/Textkontrast. Redaktionelle und
instrumentierte Werte verwenden dieselbe unveränderte Fünferskala.
Über Kreis und Schwierigkeitstext erscheint kein Tooltip, einschließlich nativer
Ersatztooltips. Die bisherigen Methoden-/Unsicherheitstexte werden dort nicht
mehr angezeigt. Das entfernt nur die Erklärung aus der Katalogoberfläche;
Bewertungsquelle, Metadaten und Aussagegrenzen bleiben unverändert.
Keine neue Solveranalyse, menschliche Kalibrierung oder Ableitung aus Format,
Farbzahl oder Spielstand; fehlende Informationen werden nicht erfunden.

## SD · Aktuelle Quelle der Schwierigkeit

[SD-C1 und SD-C2](SD_CATALOG.md) führen die bestehende separate aktuelle
Bewertungsquelle zu KE-D03/D06 und den tatsächlichen Integrations-/Abnahmestand.
Historische Produktionsschätzungen bleiben erhalten. Fehlende Sidecars erhalten
die bisherigen Werte, ungültige vorhandene blockieren die Projektion.

Skala, Bezeichnungen, Farben, neutrale fehlende Einstufung und Spoilergrenze
bleiben. KU-A ersetzt ausschließlich Ziffer und Schwierigkeitstooltip gemäß
KE-D03. 0.3 ist ausschließlich instrumentiert mit mittlerer
Aussagekraft; `[Lx,Lx]` ist die Punktprojektion der eingefrorenen Methode, kein
menschliches Unsicherheitsintervall. Die Entfernung des Tooltips ist keine
menschliche Kalibrierung oder Neubewertung. Historische 0.1-/0.2-Spannen bleiben
unverändert. Writer und Loader prüfen gemeinsam die sechs bestehenden
Difficultyfelder. KU-A lässt Runtime-v3 und den exakten v2-Leser unverändert;
die kompatible Versionierung für KU-B folgt [CATALOG_SORTING](CATALOG_SORTING.md).

Logischer Anspruch, Lösungsfluss und begrenzter Größeneinfluss folgen dem
[SD-Vertrag](PUZZLE_DIFFICULTY.md). Die Oberfläche berechnet keinen Grad aus
Größe, Farbe oder Spielstand und startet keinen Solver. Eine Methodenumstellung,
ein neues Rätsel oder eine andere Verteilung verändert Altwerte nicht automatisch.

## KE-N1 · Lokale Bildglättung

Verdiente Reveals werden in Katalog und Abschluss mit Lanczos auf das tatsächliche
Anzeigemaß verkleinert und dann linear gezeichnet. Dies glättet starke Verkleinerungen auch
gegenüber der bisher schon linearen Abschlussanzeige. Vollständiger Bildausschnitt,
Proportion, Zentrierung und bestehender Bildraum bleiben gleich. Die Anzeige
verändert die PNG-/SVG-Quelldatei nicht; abgeleitete Texturen entstehen erst nach
der Spoilerfreigabe und werden mit dem jeweiligen Reveal freigegeben; je Anzeige bleibt nur die
zuletzt benötigte Zieltextur erhalten. Keine globale Glättung, kein
zusätzlicher persistenter Bildcache; eigene Füllminiaturen bleiben unverändert.

Die lokale Polygonkantenglättung einschließlich Holzspitze und gemeinsamem
Begonnen-Stift bleibt. Historische KE-N1-Vorher-/Nachherbelege zeigen den damaligen
Einzelstift samt Farbprobe und die Dreiergruppe; sie bleiben unverändert.
Für KU-A gilt die neue größere, zentrierte Zeichnung ohne Monochrom-Farbprobe
gemäß KE-D02. Technische Vergleichsbilder verwenden dieselben nativen
Viewport-/UI-Maße; die persönliche Sichtabnahme bleibt separat. Die EA-Zeitfolge,
Saves und Abbruchregeln ändern sich nicht.

## AT · Transparente verdiente Bilder

Der freigegebene [AT-Standard](REVEAL_TRANSPARENCY.md) betrifft die Bilddatei des
verdienten Reveals: neutrale Außenflächen und echte Aussparungen sind transparent,
weiße oder helle Motivteile bleiben erhalten. Das bestehende Kartenpapier scheint
durch; es wird keine zusätzliche weiße Bildfläche gezeichnet. Die Katalogkarte
verwendet dasselbe freigegebene farbige Bild wie die Abschlussansicht.
Bildraum, vollständiger Ausschnitt, Proportionen, Zentrierung und lokale
Lanczos-/Linear-Glättung bleiben; ein dynamischer Weißfilter ist ausgeschlossen.

AT-Bildrevisionen brauchen eine konkrete neue Bildfreigabe und den begrenzten
Änderungsweg aus AT-A. Damit wird ausschließlich für diese Revisionen die frühere
Vorgabe unveränderter Assets erweitert; historische Originale, Freigaben und
Liefernachweise bleiben erhalten. Szenen behalten ihren Inhalt; ihre transparente
Außengestaltung wird motivbezogen abgenommen. Weder pauschale Umfeldlöschung noch
eine ungeprüfte Generalausnahme für vollflächige Szenen folgt aus AT.

Alphakanten sind auf tatsächlichem Karten- und Buchpapier bei kleiner Vorschau,
laufender Überblendung, Endbild und Wiederöffnung zu prüfen, einschließlich
UI 100/125 %. Weiße oder dunkle Säume und verlorene helle Details sind Fehler.
Allgemeine technische Prüfungen verwenden feste synthetische Bilder; die Sichtung
konkreter Bestandsrevisionen bleibt eine getrennte redaktionelle Aufgabe.
Fragezeichen, eigene Füllminiatur, Fehler-/Recoverydarstellung und Spoilergrenze
folgen unverändert KE-D04/D05. EA-Timing, Speicherung und Reset ändern sich nicht.

## KE-D04 · Status und Vorschau

| Gültiger Spielzustand | Anzeige | Bildraum |
| --- | --- | --- |
| Neu | Offener Kreis, neutral, „Neu“ | Gemeinsames gezeichnetes Fragezeichen |
| Begonnen | Stift, gedecktes Ocker, „Begonnen“ | Ausschließlich eigene Füllzellen |
| Abgeschlossen | Gezeichneter Haken, gedecktes Grün, „Gelöst“ | Verdientes farbiges Reveal |

Symbol und Text erscheinen gemeinsam rechtsbündig in derselben festen Fußzeile
wie „Blatt NN“ links; Farbe allein trägt keine Bedeutung. KU-A ersetzt das
bisherige sichtbare Katalogwort „Fertig“ durch „Gelöst“. Dies ist eine
Darstellungsänderung, keine Umbenennung des internen Statusmodells oder
gespeicherter Werte. Die vorhandene Statusermittlung bleibt: gültiger Abschluss
hat Vorrang; vorhandene History einschließlich Redo oder nicht unbekannte
Zellwerte bedeuten Begonnen, sonst Neu.
Keine Änderung an Abschluss, Save-Schema, History oder globaler Terminologie.

Das Fragezeichen ist eine eigene Zeichnung in warmem Graphit mit leicht
unregelmäßiger Kontur und dezenter Bleistiftschraffur, kein Zeichen einer normalen
Schrift. Es steht mit großzügigem Freiraum auf warmem Papier und nimmt ungefähr
die halbe Bildhöhe ein. Es bleibt statisch und identisch für alle neuen Rätsel,
ohne Leuchten, Pulsieren, Schattenmotiv oder andere Lösungshinweise.

Begonnene Vorschauen zeigen auch falsche eigene Füllungen unverändert. X und
unbekannte Zellen bleiben neutral. Ein begonnener Stand ohne Füllzellen, etwa nur
X oder nach Undo mit verbleibender History/Redo, zeigt eine leere Füllminiatur
und ausdrücklich kein Fragezeichen. Motivname und Reveal bleiben vor gültigem
Abschluss verborgen; kein vorzeitiges Laden des Reveals für den Platzhalter.

## KE-D05 · Fehler, Bedienung und Tooltips

Ein ungültiger Speicherstand darf nicht als Neu dargestellt werden. Vorhandene
Fehlerkennzeichnung, Diagnose, Backup-/Recoveryaktionen und Reset bleiben
erreichbar; Diagnose/Recovery nutzt weiterhin den festen Bildraum und wird nicht
vom Fragezeichen verdeckt. Kein neuer Statusautomat. Reset bleibt bei gültigem,
fehlerfreiem Neu verborgen und in den bisher vorgesehenen Bearbeitungs-/Fehler-
und Recoveryzuständen verfügbar; vorhandene Bestätigung und Ursprungsbindung bleiben.

Kein Tooltip über der ganzen Karte und kein Tooltip über der Schwierigkeit,
auch nicht als nativer Ersatz für abgeschnittene Metadaten. Der gezielte
Modustooltip und der vorhandene Resettooltip bleiben. Bestehende zugängliche
Beschriftungen führen Größe, Modus, Schwierigkeit und Status spoilerfrei mit. Kein umfangreicher
Accessibility-Umbau, keine Änderung der bestehenden Fokus-/Öffnungsbedienung.

## KE-D06 · Minimaler Metadatenvertrag

`content/registry.json` enthält `production.difficulty`; die Runtimeprojektion v3
übernimmt minimale typisierte Katalogmetadaten. Writer, Loader und Validator
verwenden gemeinsam den in [CATEGORIES](CATEGORIES.md) festgelegten Vertrag.
Alte v2-Einträge behalten exakt sieben Felder. Benötigt werden die vorhandene
Stufe, Bewertungsart, Unsicherheit/plausible Spannweite und gegebenenfalls der
Nachweis notwendiger Paarlinienlogik. Methoden müssen eindeutig interpretiert
werden können. Ganze Produktionsobjekte, Freitexte, Motiverklärungen, Quellen,
Proofs oder Pakete dürfen nicht in den Spieler gelangen.

KU-A verändert diese Datenverträge nicht. Die zusätzliche Hinzugefügt-Metadatenquelle
und ihre kompatible Projektion gehören ausschließlich zu KU-B gemäß
[Katalogsortierung](CATALOG_SORTING.md), [CATEGORIES](CATEGORIES.md) und
[ZA1_ADAPTER](ZA1_ADAPTER.md). Der bestehende v2-/Siebenfeldervertrag darf nicht
stillschweigend umgedeutet werden. Vorhandene gültige Runtimeeinträge ohne
Schwierigkeit bleiben lesbar und zeigen „Nicht eingestuft“; ungültige vorhandene
Metadaten sind ein Validierungsfehler und werden nicht stillschweigend weggelassen.
Projektion und kanonische Byteprüfung bleiben deterministisch. Registrierungs-,
Update- und Recoverypfade müssen dieselbe kompatible Projektion verwenden.

Für die KU-Metadatenergänzung bleiben Definitionen, Maße, Hinweise, IDs, Keys,
Slots, Revisionen, Assets, Freigaben, Paket-/Integrationsbindungen, Save-Schema 1
und Speicherroot unverändert. Die gesondert freigegebenen AT-Bildrevisionen folgen
ausschließlich dem oben verlinkten Bildänderungsvertrag.
Die Metadatenergänzung benötigt keine erneute Rätselproduktion, Zertifizierung
oder Paketfreigabe und darf keine Wiederherstellung gelöschter Produktionsdaten
verlangen. Bestehende Inhalts-/Exportverträge werden nicht neu bewertet.

## Pakete, Prüfumfang und Übergabe

| Paket | Eigenständiges Ergebnis | Grenze |
| --- | --- | --- |
| KU-A | Einzeiliger Papierstreifen, gefüllte Schwierigkeitskreise, größere Modussymbole und Statusfußzeile | Verwendet vorhandene Daten und Bewertungsstufen; keine Sortierung oder Datenmigration |
| KU-B | Sortierauswahl mit Richtung sowie dauerhafte Hinzugefügt-Metadaten | Vertrag in [CATALOG_SORTING](CATALOG_SORTING.md); übernimmt keine Änderung von Rätsellogik, Bewertung oder Spielständen |

Standard ist je Paket ein Implementierungs-PR. Die Spezifikationslieferung beginnt
keines dieser Pakete. KU-A/B sind inzwischen über PR #254/#255 integriert;
Paketakzeptanz, technische Nachweise, Reviews und spätere Entscheidungen zu den
persönlichen Abnahmen stehen im Gesamtissue. HZ-A/B sind in #284 abgeschlossen;
das über PR #296 integrierte Folgepaket HZ-C / #294 hat seine eigene Prüfzuordnung gemäß
[HAND_DRAWN_UI](HAND_DRAWN_UI.md).
Historische [KE-Prüfnachweise](KE_VERIFICATION.md) bleiben an ihre damalige Lieferung
gebunden und sind keine Abnahme der neuen KU-Darstellung.

Die KU-Prüfzuordnung verlangt feste synthetische Fälle für alle
fünf Stufen, fehlende Einstufung, beide Modi und die Status-/Fehlerzustände;
keine Tests oder Replays pro echtem Produktionsrätsel. Geometrie und Darstellung
folgen bei gewähltem Modul dem [aktuellen Stichprobenvertrag](CI_C_NATIVE_GROUPS.md)
und dem begründeten Paketbedarf; keine automatische Vollmatrix. Nachzuweisen sind die vollständige einzeilige Anzeige der längsten
Metadaten, größere ausgerichtete Symbole, ausbleibende Schwierigkeitstooltips,
erhaltene Modus-/Resettooltips und die Statusfußzeile. Filter-/Seitenwechsel,
Undo/Redo, Fehler/Recovery, Reset und Spoilergrenzen bleiben relevante Regressionen.
Native Windowsprüfungen folgen dem gewählten Modul; ausdrücklich manuelle
Chromiumprüfungen dem [Webvertrag](WEB_HOSTING.md); KU-B ergänzt die eigenen Sortier-/Datennachweise.

