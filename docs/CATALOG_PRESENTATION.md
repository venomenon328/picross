# Katalogdarstellung und unbekannte Motive · KU

**AT · 19.10.2026, Umsetzungsvorbereitung V3; AT-A in Umsetzung:**
Der [Transparenzstandard](REVEAL_TRANSPARENCY.md) ergänzt die verdienten
Katalogbilder. AT-A schafft den begrenzten Bildänderungsweg mit synthetischen
Alpha-/Spielstandsnachweisen; AT-B überarbeitet danach die Bestandsbilder mit
konkreter neuer Bildfreigabe. Kartenaufteilung und ungelöste Vorschauen bleiben erhalten.

Stand: 18.10.2026 · Spezifikation 2.0 · KU-A im Implementierungspaket umgesetzt; KU-B offen

Der Eigentümer hat die Katalogüberarbeitung am 18.10.2026 als Spezifikation
freigegeben. [Gesamtissue #244](https://github.com/venomenon328/picross/issues/244)
führt KU-A (Karten und Papierstreifen) und KU-B (Sortierung und Hinzugefügt-Metadaten),
ihre Akzeptanz und getrennten technischen, Review- und Eigentümergates.
Die spätere KU-A-Implementierung folgt dem gesonderten Auftrag auf
`feat/244-kataloggestaltung`. [Aktuelle Nachweise](KU_VERIFICATION.md) trennen
technische Lieferung, unabhängigen Review und Eigentümerabnahme. Kein Mergeauftrag.

## Geltung und gezielte Ablösung

Ausgangsbasis ist `main@72ba39391833f6fd834d0a6afaf881c86c7bdc3a` mit
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

## KE-D02 · Papieretikett und Moduspiktogramm

Der gemeinsame Streifen wirkt wie ein ruhiges Papieretikett des Rätselbuchs:
warmes Papier, leicht dunkler als die Kartenfläche, dünne subtil unregelmäßige
Kontur, höchstens ein sehr zurückhaltender Schatten. Keine drei gerahmten
Einzelfelder und kein schwerer Schmuckrahmen. Vorhandene lesbare Plex-Schrift
für Metadaten; Charakter entsteht durch Kontur, Zeichnungen und klare Abstände.
Keine neue Schrift oder Änderung der vorhandenen Schriftdateien. Streifen,
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
dahinter in dunkler Plex-Schrift und trägt die Bedeutung auch ohne
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
keines dieser Pakete. Paketakzeptanz, Reihenfolge, zuständige Akteure und getrennte
technische, unabhängige Review- und Eigentümergates vor Merge stehen im Gesamtissue.
Historische [KE-Prüfnachweise](KE_VERIFICATION.md) bleiben an ihre damalige Lieferung
gebunden und sind keine Abnahme der neuen KU-Darstellung.

Bei einer später beauftragten Umsetzung decken feste synthetische Daten alle
fünf Stufen, fehlende Einstufung, beide Modi und die Status-/Fehlerzustände ab;
keine Tests oder Replays pro echtem Produktionsrätsel. Geometrie und Darstellung
folgen den drei gemeinsamen Konfigurationen der aktuellen CI-Policy sowie
UI 100/125 %. Nachzuweisen sind die vollständige einzeilige Anzeige der längsten
Metadaten, größere ausgerichtete Symbole, ausbleibende Schwierigkeitstooltips,
erhaltene Modus-/Resettooltips und die Statusfußzeile. Filter-/Seitenwechsel,
Undo/Redo, Fehler/Recovery, Reset und Spoilergrenzen bleiben relevante Regressionen.
Native Windows- und Chromium-/Firefoxprüfungen folgen P1 und
[WEB-1](WEB_HOSTING.md); KU-B ergänzt die eigenen Sortier-/Datennachweise.
