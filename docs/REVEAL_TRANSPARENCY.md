# AT · Transparente Abschlussbilder

Stand: 19.10.2026 · **Spezifikation freigegeben; Implementierung nicht begonnen** ·
[AT / #256](https://github.com/venomenon328/picross/issues/256).

## Auftrag, Quellen und Wirksamkeit

Der Eigentümer hat transparente Abschlussbilder einschließlich ihrer verdienten
Katalogvorschau als Spezifikation freigegeben. Der aktuelle Auftrag umfasst Issues
und dauerhafte Repository-Dokumentation, ausdrücklich noch keine Implementierung.
AT-A und AT-B benötigen jeweils einen späteren Auftrag; auch Merge und Freigaben
der erst noch zu erstellenden Bildbytes sind damit nicht erteilt.

Geprüfte Ausgangsbasis ist
`main@b019a32f8854070dfa3d7bb580fd35a3cd4a5686`. Das Issue führt aktuelle
Paketaufträge, Lieferstände und Abnahmen. Dieser Vertrag führt die dauerhaften
Entscheidungen. Er ergänzt gezielt [Produkt](PRODUCT_DEFINITION.md),
[Design](DESIGN_CONCEPT.md), [Katalogdarstellung](CATALOG_PRESENTATION.md),
[Rätselproduktion](PUZZLE_PRODUCTION.md),
[PUZZLE_AUTHORING](ai-workflows/PUZZLE_AUTHORING.md),
[ZA-1](ZA1_ADAPTER.md), [Kategorien](CATEGORIES.md),
[gemeinsame Katalogtransaktionen](SD_CATALOG.md) und [CI-Policy](CI_POLICY.md).
Historische Lieferberichte behalten ihren damaligen Umfang und Nachweisstand.

## 1. Ausgangsbefund und Ziel

Die geprüften aktiven PNGs `knoblauch_001.png`, `japanische_teekanne_001.png`
und `warnemuende_001.png` in `game/art/content/` sind deckende RGB-Bilder.
Die ersten beiden besitzen neutrale helle Außenflächen; die Teekanne zusätzlich
einen entsprechenden Innenraum im Griff. Warnemünde ist eine vollständige Szene
mit motivisch relevanter Umgebung. Diese Stichproben begründen die Paketbildung;
sie sind keine vollständige Bestandsaufnahme oder bereits erfolgte Bildabnahme.

Die reguläre Karte in [catalog_card.gd](../game/ui/catalog_card.gd) verwendet
denselben Revealpfad wie der Abschluss. [reveal.gd](../game/ui/reveal.gd) zeichnet
in diesem Modus die Textur, ohne einen weißen Bildkasten zu ergänzen.
[completion.gd](../game/ui/completion.gd) übernimmt ebenfalls diese Textur.
Der helle rechteckige Hintergrund liegt bei den geprüften Beispielen in den
Bildbytes. Die vorhandene Alphakantenkorrektur und proportionale Glättung lösen
keine Motivfreistellung eines deckenden Bildes.

Ziel ist ein tatsächlich transparentes freigegebenes Abschlussasset: Neutrale
Außenflächen und echte Aussparungen lassen in beiden Ansichten den vorhandenen
Papieruntergrund sichtbar. Keine separate, anders bearbeitete Katalogfassung.

## 2. Verbindlicher Bildstandard

- Neutrale weiße oder helle Flächen außerhalb des Motivs und echte Aussparungen
  werden transparent. Ein Alphakanal allein genügt nicht, wenn die störende
  Fläche weiterhin deckend bleibt.
- Weiße und helle Motivteile bleiben erhalten, ebenso Farben, Konturen, feine
  Details, Pose, Perspektive, Proportionen, Ausschnitt und Komposition. Helligkeit
  allein entscheidet nicht, ob ein Pixel zum Hintergrund gehört.
- Alphakanten sind in großer Darstellung, kleiner Katalogvorschau und während der
  Überblendung sauber. Keine hellen Matten/Säume, ausgeschnittenen Motivdetails
  oder ausgefransten Konturen; teiltransparente Randpixel bleiben möglich.
- Vollständige Szenen erhalten eine bewusste motivbezogene Bearbeitung. Prägende
  Umgebung und räumliche Beziehungen bleiben erhalten; transparente Außenfreiräume
  oder eine passende Vignette werden konkret vorgelegt und neu freigegeben.
  Himmel, Meer oder Boden werden nicht pauschal entfernt. Die Bezeichnung
  „Szene“ ist keine automatische Ausnahme für deckende Rechtecke. Erfordert eine
  Lösung weitergehende Motiv-/Kompositionsänderungen, sind diese vor Bearbeitung
  beziehungsweise Übernahme ausdrücklich zu entscheiden.
- Neue Bilder werden bereits für die Bildauswahl transparent vorbereitet und in
  diesem Stand freigegeben. Nachträgliche Freistellung ist eine neue Bildrevision,
  keine stillschweigende Änderung der bereits freigegebenen Datei.
- Die technische Kette erhält Alpha vom freigegebenen PNG beziehungsweise
  bestehenden SVG bis zu Export, Integration, Import und Darstellung. Keine
  JPEG-/deckende Zwischenstufe und kein globaler Weiß-/Farbfilter im Renderer.

Bestehende Lanczos-/Linear-Glättung, Ressourcengrenzen und proportionale Darstellung
bleiben. AT ändert weder Fragezeichen noch eigene Füllminiatur, Spoiler-/Recovery-
grenzen oder den Ablauf der transienten EA-Enthüllung von 2,15 Sekunden. Der
vorhandene Papieruntergrund wird nicht durch eine neue Ersatzfläche überdeckt.
Die früheren KE-/KU-Vorgaben unveränderter Originalassets beschreiben deren
Darstellungsarbeit; AT erlaubt gezielt separat freigegebene Bildrevisionen.

## 3. Reine Bildrevision: Identität und historische Bindungen

Eine reine Bildrevision ersetzt nur das freigegebene Abschlussbild samt den dafür
notwendigen aktuellen Revisions-/Freigabedaten. Sie ist kein Rasterupdate.

| Bereich | Verbindliche Grenze |
| --- | --- |
| Rätsel | Definitionsbytes und ihr Hash, Matrix, Hinweise und Puzzle-Runtime-Revision bleiben unverändert. Keine neue Logik-, Eindeutigkeits- oder Schwierigkeitsanalyse allein wegen der Bildänderung. |
| Identität und Auffindbarkeit | ID, Schlüssel, Save-Slot, Definitions-/Bildpfad, Kategorie und Sichtbarkeit bleiben erhalten. Die Definition bindet bereits den aktiven Bildpfad; deshalb wird am bestehenden Ressourcenpfad ersetzt. |
| Fortschritt | Vorhandene Spielstände bleiben gültig; kein Reset, keine Migration und keine Rückstufung eines begonnenen oder gelösten Rätsels. |
| Metadaten | Bestehende Schwierigkeitsbindung und `added_at` einschließlich ihrer Herkunft bleiben byte-/wertgleich; das Bild ist keine neue Katalogaufnahme. |
| Ursprüngliche Freigabe | Originalhandoff, Bildauswahl, Exportmanifest und kompakter Integrationsbeleg behalten ihre ursprünglichen Bytes und Aussage. Keine rückwirkende Umschreibung auf den neuen Bildhash. |
| Aktuelle Bildfassung | Getrennte, versionierte Bindung an Rätsel-ID, unveränderte Definition, ursprünglichen Integrationsbeleg, Vorgänger-/Neubildhash, konkrete Bildrevision und tatsächliche Freigabe. Herkunft, Nutzungsrechte und nötige neue Hinweise werden nachvollziehbar erhalten beziehungsweise ergänzt. |

Der vollständige Vergleich historischer Einträge bleibt gültig. Der Validator
prüft künftig zusätzlich, ob eine erlaubte aktive Bildrevision genau diese
historische Ausgangsbasis und die tatsächlich vorhandenen neuen Bildbytes bindet.
Er darf nicht einfach den alten Revealhash ignorieren oder den alten Beleg
neuberechnen. Die neue aktive Bindung bleibt auch nach der regulären Bereinigung
von Produktionsmaterial prüfbar; eine spätere Bildänderung verlangt keine
Rekonstruktion aller längst ausgeräumten historischen Produktionsdateien.

Die neue Bildfreigabe bindet die tatsächlichen Bytes. Bild-/Motiv-/Rasterkonsistenz
und Endkontrolle folgen PUZZLE_AUTHORING. Eine gemeinsame Freigabe mehrerer Bilder
ist möglich, wenn jede ID, Datei, Bildrevision und jeder Hash eindeutig aufgeführt
ist. Eine Freigabe der Spezifikation oder einer bloßen Vorschau ohne Dateibindung
ersetzt diese Entscheidung nicht.

## 4. Gemeinsamer technischer Vertrag für AT-A

### 4.1 Eigener Weg und kompatible Quellenprüfung

Der bestehende [Katalogintegrator](../tools/puzzle_production/catalog_integration.py)
erlaubt im Rasterupdate nur identische Revealbytes und verlangt eine höhere
Puzzle-Runtime-Revision. AT-A ergänzt einen eigenen Weg für reine Bildrevisionen.
Er macht weder den bestehenden Rasterupdatevertrag permissiver noch gibt er
einen direkten Austausch außerhalb der kontrollierten Übernahme frei.

Die konkrete Umsetzung benötigt eine gemeinsame Quellenprüfung. Registrierung,
Rasterupdate, Sync, Bewertungs-/Added-Übernahme, Prüfen, Export, Bereinigung und
Recovery müssen den aktiven freigegebenen Bildstand konsistent verstehen und
erhalten. Ein späteres Rasterupdate darf eine aktive AT-Bildfassung nicht still
verwerfen oder auf das historische Bild zurücksetzen; der kombinierte neue
Quellstand benötigt wieder eine vollständige gültige Bindung.

Gültige Altstände ohne AT-Bildrevision bleiben während AT-A prüfbar und nutzbar.
Der Transparenzstandard für neue beziehungsweise ausdrücklich bearbeitete Bilder
wird nicht als rückwirkende globale Sperre aller noch nicht umgestellten Assets
eingeführt. Fehlende AT-Metadaten eines legitimen Altstands und vorhandene defekte,
unvollständige oder widersprüchliche Revisionsdaten sind verschieden: Letztere
stoppen die Operation, ohne stillen Rückfall auf historische Werte.

Bestehende exakte Registry-/Receipt-/Journalformate behalten ihre Feldmengen und
Grenzen. Bereits gesperrte Altjournale bleiben gesperrt. Zusätzliche Felder oder
Operationen brauchen einen ausdrücklich versionierten Vertrag. Eine neue
Runtime-Registryversion ist nur bei tatsächlicher Änderung ihres Schemas nötig;
die reine neue Bilddatei rechtfertigt keine allgemeine Datenmigration.

### 4.2 Vorschau, binäre Ersetzung und Wiederherstellung

Eine Vorschau bindet den erwarteten Ausgangsstand und zeigt genau die betroffenen
IDs, Pfade, alten/neuen Hashes, Freigaben und geplanten Schreiboperationen.
Vollständige Vorprüfung erfolgt vor jeder Übernahme. Sperre und erneuter
Quellenvergleich verhindern Übernahme eines veralteten Plans oder einer
zwischenzeitlich konkurrierend geänderten Datei. Fremde Quellen werden nicht
automatisch repariert, überschrieben oder als eigener No-op ausgegeben.

Der [gemeinsame Journalweg](../tools/puzzle_production/catalog_transaction.py)
führt bisherige Bilddateien als unveränderte `retained`-Bytes; `old/new` enthält
UTF-8-Texte und `additions` neue Dateien. Binäre Ersetzung am gleichen Bildpfad
braucht deshalb einen ausdrücklichen versionierten Erweiterungsvertrag mit
gesicherten Altbytes, Staging und Hashbindung. PNG-Bytes dürfen weder als UTF-8
in das Textjournal geschoben noch als scheinbare Neuanlage an einem vorhandenen
Pfad behandelt werden.

Eine zusammenhängend geplante Übernahme bleibt als Gesamtheit konsistent:
Bildbytes und aktive Bindung werden vollständig übernommen oder auf den
vorherigen gültigen Zustand zurückgeführt. Das gilt bei Schreibfehler,
Unterbrechung und erneutem Recoveryaufruf. Gesicherte Altbytes und Journal werden
nicht vor erfolgreichem Abschluss entfernt; widersprüchliche Recoveryquellen
stoppen, statt fremde Daten zu überschreiben. Keine Mischung aus alter Freigabe
und neuen Bildbytes oder umgekehrt.

Nur der vollständig passende eigene Zielstand gilt bei identischer Wiederholung
als No-op: keine Byte-, Revisions- oder Zeitstempeländerung, kein Rewrite und kein
neues Journal. Fehlende Dateien, ungeprüfte Metadaten oder ein lediglich ähnlich
aussehendes Bild erfüllen diesen Zustand nicht.

### 4.3 Konkretisierung vor Implementierung

AT-A legt vor der ersten betroffenen Codeänderung konkrete Dateipfade, Feldmengen,
Versionsnamen, aktive Quellenautorität, CLI-/Plan-/Ergebnisformat und den binären
Journal-/Recoveryvertrag in den zuständigen Fachquellen fest. Sie müssen die hier
freigegebenen Invarianten erfüllen. Hier wird weder eine noch nicht existierende
CLI als ausführbar beschrieben noch ein Schema allein vorsorglich hochgezählt.
Offene technische Kernfragen verhindern den Status „umsetzungsbereit“; sie
berechtigen nicht zur stillen Änderung der freigegebenen Produkt-/Datengrenzen.

## 5. Pakete und Abnahme

Standard ist ein Implementierungs-PR je Paket. AT-A wird vor AT-B integriert;
der Zwischenstand muss mit allen gültigen bisherigen Inhalten kompatibel sein.
Ein Spezifikations-PR schließt das AT-Issue und die Umsetzungsgates nicht.

| Paket | Ergebnis | Abhängigkeit und Grenze |
| --- | --- | --- |
| AT-A · Sicherer Bildrevisionsweg | Produktionsstandard, konkrete Daten-/Werkzeugverträge, gemeinsame Quellen-/Transaktionsintegration, Alpha-Erhalt und feste synthetische Regressionen einschließlich notwendiger Dokumentation/CI-Zuordnung. | Späterer Implementierungsauftrag. Kein Austausch realer Katalogbilder in diesem Paket. |
| AT-B · Vorhandene Bilder umstellen | Vollständiger gebundener Startbestand, konkrete Freistellungen/Szenenlösungen, neue Bildfreigaben, Konsistenzkontrollen und kontrollierte Übernahme. | Integriertes AT-A und späterer Inhaltsauftrag. Technische Vertrags-/Recoveryfehler gehen in AT-A beziehungsweise benannte technische Nacharbeit zurück. |

### AT-A · Nachweise

AT-A-T01 bindet den finalen Quell-/Basisstand, tatsächliche ausgewählte Checks und
einen getrennten Selbstreview. Die feste synthetische Prüfung umfasst:

- Gültiger Altstand, erste und weitere Bildrevision, Wiederholung als echter No-op
  sowie byte-/wertgleiche Definitionen, Identitäten, Revisionen und übrige Metadaten.
- Falsche Identität/Definition, manipulierte Freigabe/Hashes, fehlende oder defekte
  aktive Bindung, veralteter Plan und konkurrierende Änderung; keine Teilübernahme.
- Binäre Altbytesicherung, Fehler an den Schreib-/Abschlussgrenzen, unterbrochene
  Übernahme, wiederholtes Recovery und widersprüchliche Fremdquellen; außerdem
  Erhalt der aktiven Bildfassung bei späteren gemeinsamen Operationen.
- Ein synthetisches Bild mit weißem Motivteil, Innenaussparung und weichen
  Alphakanten über die tatsächliche Export-/Importkette. Kleine Katalogansicht
  einschließlich Hover, Überblendung, Abschluss und Wiederöffnung zeigen die
  erwartete Transparenz und saubere Kanten bei UI 100/125 %.
- Ein bestehender synthetischer Save bleibt über den Bild-/Exportwechsel begonnen
  beziehungsweise gelöst. Neue/gesperrte Zustände offenbaren das Bild nicht früher;
  weder Reset noch Puzzle-Revisionmigration wird ausgelöst.

Technische Darstellung und Savewechsel werden in den betroffenen nativen Windows-
und Chromiumwegen belegt. Der tatsächliche Gesamtdiff wählt weitere bestehende
Pflichtchecks gemäß CI-Policy; AT verändert keine Plattform- oder Browsermatrix
und übernimmt keine frühere paketbezogene Ausnahme als allgemeine Freigabe.
Ein bloßer Start ersetzt keinen betroffenen Darstellungs-/Persistenznachweis.
AT-A-R01 ist ein separater qualifizierter Review des finalen Heads vor Merge.

### AT-B · Bestands- und Bildabnahme

AT-B inventarisiert sämtliche aktiven Abschlussbilder eines konkret genannten
Startcommits. Je ID werden Ressourcenpfad, bisheriger Hash/Freigabebezug, Befund
und gewählte Bearbeitung geführt; spätere Umfangsänderungen werden begründet.
Jedes geänderte Bild erhält Vorher/Nachher, konkrete Dateifreigabe und Sichtkontrolle
im Katalog-/Abschlusskontext. Die drei Ausgangsstichproben begrenzen den Bestand
nicht. Szenische Motive sind vollständig einzuplanen.

Die Abschlussliste weist jede Start-ID als bereits konform oder mit neuer
freigegebener und integrierter Bildrevision aus. Offene beziehungsweise blockierte
Motive bleiben sichtbar offen; ein ungeprüfter Szenenverzicht zählt nicht als
Erfüllung. Das Paket ist erst mit vollständiger Disposition und erfülltem Ziel
abgeschlossen.

AT-B-T01 bindet Inventar, Bildfreigaben, Konsistenz-/Endkontrolle, Übernahmeplan,
Ergebnis, identische Wiederholung und Kontrolle der tatsächlich integrierten
Dateien samt getrenntem Selbstreview. Definitionen, Revisionen, Identitäten und
übrige Metadaten bleiben nachweislich unverändert. AT-B-R01 ist die separate
finale Inhalts-/Integrationsprüfung; tatsächliche Bildfreigabe und
Eigentümerabnahme werden ausdrücklich an den vorgelegten Stand gebunden.

## 6. Prüfgrenzen und Nichtziele

Die aktuelle Dokumentlieferung nutzt Dokumentvalidator, schnelle Werkzeugtests,
vollständige Diffprüfung und die ausgewählte CI samt `ci-required`. Sie ist kein
Nachweis implementierter AT-Funktionalität oder bereits transparenter Bildbytes.

AT-A verwendet feste synthetische Regressionen. AT-B prüft tatsächliche Bilder
im Inhaltsauftrag außerhalb der CI; die Sichtkontrolle wird nicht zu einem
automatischen Katalog-Replay oder einem vollständigen Probespiel je Rätsel.
Reine zugelassene Inhaltsdateien behalten den kurzen CI-Pfad. Benötigt AT-A neue
Nachweispfade, wird deren enge Zuordnung mit der technischen Änderung festgelegt.
Gemischte Änderungen folgen weiterhin der Vereinigung des tatsächlichen Diffs.

Kein neues Kataloglayout, kein anderer Enthüllungsablauf, keine Neubewertung oder
Neuzertifizierung des Katalogs, keine Änderung von Rätsellogik, Saveformat oder
Hinzugefügt-Datum, keine allgemeine Registry-/Plattform-/Deploymentumstellung.
Aktuelle Paketstände und spätere Startprüfung stehen im Issue; Modellauswahl wird
erst bei ausdrücklich beauftragter Umsetzungsvorbereitung aktualitätsgebunden
vorgenommen.
