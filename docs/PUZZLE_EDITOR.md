# Lokaler Rätselbestand-Editor (PE)

Stand: 11.11.2026. **Vom Eigentümer als Spezifikation freigegebener Sollstand;
noch nicht implementiert oder abgenommen.** Auftrag und Paketkriterien stehen
im [PE-Issue #576](https://github.com/venomenon328/picross/issues/576). Geprüfte Ausgangsbasis ist
`main@9cc07b411155adeab0aa6516ab5b4c4341f48184`.

Dieser Vertrag beschreibt ein persönliches Werkzeug außerhalb des Spiels.
Die bisherigen Fachverträge beschreiben bis zur jeweiligen Lieferung weiterhin
die vorhandenen Ausführungswege. Die unten ausdrücklich beschlossenen
Erweiterungen sind keine Behauptung, diese Wege könnten sie bereits ausführen.
Neue Rätsel folgen weiterhin [PUZZLE_AUTHORING](ai-workflows/PUZZLE_AUTHORING.md).

## 1. Ziel und freigegebener Umfang

Eine lokale Weboberfläche öffnet einen vorhandenen Projektcheckout und pflegt
bereits registrierte Rätsel. Name, Kategorie, Abschlussbild und tatsächlich
wirksamer Hintergrund sind unmittelbar sichtbar und änderbar. Die Autorenansicht
darf alle Motivnamen und Bilder zeigen; die Spoilergrenze des Spiels bleibt erhalten.
Speichern übernimmt gültige Änderungen direkt in den lokalen Inhaltsbestand und
seine Laufzeitprojektion. Git, Build und Veröffentlichung erfolgen außerhalb des
Editors. Für Bearbeiten, Prüfen und Speichern ist kein KI-Zwischenschritt nötig.

| Bereich | Verbindliches Verhalten |
| --- | --- |
| Einstieg | Bequemer Start unter Windows; lokaler Backendprozess und Browseroberfläche. Der gewählte Checkout ist eindeutig sichtbar. Kein gehosteter Dienst oder GitHub-Zugang erforderlich. |
| Auswahl | Durchsuchbare Liste mit Name, Kategorie und Bildvorschauen; Kategorienfilter. Auswahl öffnet ein vorhandenes Rätsel. |
| Metadaten | Motivname und genau eine Kategorie direkt bearbeiten. Stabile IDs dienen der Zuordnung und sind keine gewöhnlichen Eingabefelder. |
| Kategorien | Anlegen, Anzeigenamen ändern, zuweisen. Löschen nur leer oder zusammen mit ausdrücklicher Neuzuordnung sämtlicher betroffener Rätsel. Keine Sortierungsverwaltung. |
| Bilder | Abschlussbild und Hintergrund ansehen, vorbereitete Datei auswählen oder hineinziehen, prüfen und unverändert importieren. |
| Hintergrund | Standard, eigenes Bild oder ausdrücklich kein Hintergrund. Auch erstmals bei einem bestehenden Legacyrätsel zuweisen und später zu Standard zurückkehren. |
| Raster | Nachgeordnete Textbearbeitung der Lösungsmatrix mit vorhandener Palette. Maße und Hinweise daraus ableiten beziehungsweise prüfen. Kein Zeichenwerkzeug und keine verpflichtende grafische Rastervorschau. |
| Speichern | Explizites Speichern und Verwerfen, erkennbare ungespeicherte Änderungen, konkrete Fehler. Zusammengehörige Änderungen werden konsistent übernommen. |

Keine Neuanlage oder Duplikation von Rätseln, keine Rätsellöschung, Bildgenerierung,
Bildbearbeitung, Git-Automatik, Veröffentlichung, Onlinekonten oder Mehrbenutzerlösung.
Die Inhaltsverwaltung bekommt keine zweite dauerhaft unabhängig bearbeitbare
Datenkopie in Browserstorage oder einer Datenbank. Eine schlichte Arbeitsoberfläche
genügt; der Editor übernimmt keine verpflichtende Buchinszenierung des Spiels.

## 2. Datenautorität und Änderungsgrenzen

Lesbare JSON-Quellen mit stabilen IDs bleiben maßgeblich. Die relationale Zuordnung
von Kategorien und Rätseln wird durch den gemeinsamen Datenzugriff geprüft.
SQLite und ein eigener Datenbankserver sind für diesen Umfang nicht vorgesehen.
Bilder bleiben Dateien. Der Spieler liest vorbereitete Laufzeitdaten und benötigt
weder Produktionspakete noch Python, Editor oder KI.

| Gegenstand | Zuständigkeit |
| --- | --- |
| Identität | Bestehende Rätsel-ID, Schlüssel und Save-Slot bleiben bei normaler Pflege erhalten. Technische Dateinamen werden beim Umbenennen nicht neu abgeleitet. |
| Aktuelle Metadaten | Genau eine aktuelle Namens-/Kategoriezuordnung je registrierter ID, getrennt von historischen Produktionsangaben. |
| Rasterlogik | Maße, Lösungsmatrix und Bedeutung der logischen Farbkennungen. Hinweise sind abgeleitete Daten. |
| Darstellung | Abschlussbild und Hintergrund haben eigene Inhaltsbindungen. Ein Bildwechsel ist keine Rasterrevision. |
| Produktionshistorie | Bestehende Exporte, Receipts, Freigaben und Rechte behalten ihren damaligen Inhalt. Eine manuelle Änderung wird ehrlich als solche geführt. |

Ein Bytehash darf sich ändern, ohne Rätselidentität oder Spielstandkompatibilität
zu ändern. Name, Kategorie, Bildbytes und JSON-Formatierung gehören nicht zur
logischen Identität. Prüfungen binden die tatsächlich relevanten Eingaben.
Unveränderte Logik erfordert keinen neuen Solver-/Schwierigkeitslauf. Neue
Bilddateien und Kategoriebezüge werden dennoch fachlich geprüft.

Editor, CLI, Standardproduktion und Laufzeitprojektion verwenden dieselbe
Auflösung der aktuellen Daten. Eine Pflege im Editor darf nicht durch einen
späteren Produktionsschritt aus historischen Angaben überschrieben werden.

## 3. Namen und Kategorien

Der bestehende Anzeigenamenbereich von 1 bis 128 Zeichen und nicht ausschließlich
Whitespace bleibt erhalten. Kategorien behalten den exakten Wertebereich aus
[CATEGORIES](CATEGORIES.md), insbesondere ihre stabilen IDs. Neue Kategorie-IDs
werden einmalig kollisionsfrei erzeugt; ein späterer Anzeigenamenwechsel ändert
die ID nicht. Bestehende technische `order`-Werte bleiben, neue Kategorien werden
automatisch angehängt. Erschöpfte Vertragsgrenzen werden als Fehler gemeldet.

Jedes registrierte Rätsel gehört genau einer aktuell vorhandenen Kategorie an,
auch wenn es nicht sichtbar ist. Beim Löschen einer belegten Kategorie muss der
Benutzer eine andere vorhandene Kategorie wählen. Neuzuordnung und Löschung
bilden einen gemeinsamen Speichervorgang. Historische Kategorien in alten
Produktionsbelegen werden dadurch weder umgeschrieben noch zu einer Pflicht,
die gelöschte Kategorie im aktuellen Katalog weiterzuführen.

## 4. Bilder und Hintergrundauswahl

### 4.1 Fertige Dateien unverändert importieren

Import übernimmt genau die ausgewählten Dateibytes in den verwalteten Assetbereich.
Die weitere Nutzung hängt nicht vom ursprünglichen externen Speicherort ab.
Keine Skalierung, Drehung, Beschneidung, Leinwanderweiterung, Freistellung,
Farbkonvertierung oder Neukodierung im Editor. Prüfung und Vorschau verändern
die Quelle nicht. Ein unzulässiger Eingang wird mit erwarteten und tatsächlichen
Eigenschaften zurückgewiesen; es gibt keine automatische Reparatur.

| Bildtyp | Importgrenzen |
| --- | --- |
| Hintergrund | Ein einzelnes, nicht animiertes, vollständig dekodierbares PNG, genau 2304 × 576 Pixel, höchstens 32 MiB; geeignete sRGB-/Alphaeigenschaften gemäß Hintergrundvertrag. Mindestens ein vollständig transparenter und ein sichtbarer Pixel. |
| Abschlussbild | Bestehende PNG-/begrenzte lokale SVG-Zulassung und Bildprüfung. Höchstens 32 MiB, 8192 Pixel je Achse und 8.000.000 Pixel insgesamt; mindestens zwei Bildpixel je Rasterzelle in jeder Achse. PNG bereits korrekt orientiert. |
| Abschlussbildgröße | Keine neue Einheitsgröße, keine Gleichheit mit den bisherigen Bildmaßen und kein erzwungenes Seitenverhältnis zum Raster. |

Der [Transparenzstandard](REVEAL_TRANSPARENCY.md) bleibt inhaltlich maßgeblich.
Ein technischer Alphacheck ersetzt keine menschliche Motivbeurteilung. Auswahl
und Speichern durch den Eigentümer erfassen die manuelle Inhaltsentscheidung;
es wird weder ein KI-Auftrag noch eine erfundene frühere Produktionsfreigabe erzeugt.
Gültige historische Assets verhindern eine reine Namens-/Kategoriepflege nicht.

Der vorhandene [Hintergrundweg](PUZZLE_BACKGROUNDS.md) leitet Originale deterministisch
ab und kodiert sie dabei neu. PE benötigt einen gesondert versionierten Eingang
für bereits fertige Assets; er darf nicht behaupten, eine solche Ableitung sei
ausgeführt worden. Die reguläre Produktionsableitung bleibt für ihre Eingänge
bestehen. Der spätere isolierte Godot-Texturimport ist ein davon getrenntes
Laufzeitnebenprodukt; Quellbilder bleiben bytegleich.

Ein Formatwechsel eines Abschlussbilds darf nicht in einen Writer eingeschleust
werden, der einen unveränderten Dateipfad beziehungsweise dieselbe Endung verlangt.
PE-A2 muss zulässige PNG-/SVG-Wechsel einschließlich verwaltetem Zielpfad,
aktueller Referenz und historischer Herkunft konsistent schließen.

### 4.2 Drei verständliche Hintergrundzustände

| Auswahl | Wirkung |
| --- | --- |
| Standard | Vorhandene Standardzeichnung der aktuell zugewiesenen Kategorie; ohne solche Zeichnung kein Hintergrund. |
| Eigenes Bild | Individuelles importiertes Bild ersetzt die Kategoriezeichnung. |
| Kein Hintergrund | Kategoriezeichnung ausdrücklich unterdrücken. |

Alle Wechsel zwischen diesen Zuständen sind Teil des Gesamtumfangs. Der Bestand
ohne individuelle Bindung startet ohne optische Änderung mit Standard. Ein
Kategoriewechsel aktualisiert die Standardvorschau; eigenes Bild und ausdrückliches
Kein Hintergrund behalten ihre Bedeutung. Eine defekte individuelle Quelle ist
ein Fehler und kein stiller Wechsel zu einem anderen Zustand.

Die heutige Runtime kennt `legacy/selected/none`; `legacy` ist eine historische
Ableitung und noch keine frei schreibbare Präferenz. PE-A2 muss Standard und die
Legacy-Erstzuordnung ausdrücklich im Quell-/Laufzeitvertrag einführen. Die bisherige
Sperre der Legacy-Nachrüstung beschreibt den alten Werkzeugweg, nicht das PE-Ziel.

## 5. Rastertext und Spielstandrevision

Das Textfeld bearbeitet die numerische `solution`-Matrix: Zeilen von oben nach
unten, Zellen von links nach rechts, `0` leer, positive Werte als vorhandene
Palette-IDs. Fehler nennen Zeile/Zelle und Ursache. Dimensionen und Palette
werden geprüft, `rows/columns` reproduzierbar erzeugt. Ungültige oder noch nicht
erfolgreich geprüfte Änderungen werden nicht in den spielbaren Bestand übernommen.
Ein eigener dauerhafter Entwurfsbestand ist für den ersten Editor nicht erforderlich.

Eine echte Änderung der kanonischen Rasterlogik erhöht die spielstandrelevante
Revision genau einmal pro erfolgreicher Übernahme. Identische Wiederholung,
andere Textformatierung oder identisch abgeleitete Hinweise erhöhen sie nicht.
Name, Kategorie und Bildwechsel erhöhen sie ebenfalls nicht. Der Editor führt
die erforderlichen bestehenden Logik-/Qualitätsprüfungen selbst aus; kein KI-Gate.
Eine veränderte Logik darf keine unverändert behauptete alte Bewertung übernehmen.

Beim nächsten Laden im Spiel beginnt ein eindeutig zuordenbarer Spielstand einer
älteren Rasterrevision desselben Rätsels automatisch neu. Zellen, History/Redo,
Undo-Merkmal, Abschluss, rätselbezogene Ansicht und alter Fortsetzen-Merker
werden zusammen behandelt. Andere Rätsel und allgemeine Einstellungen bleiben.
Ein kurzer Hinweis erklärt die Rätselüberarbeitung. Neue Fortschritte der aktuellen
Revision bleiben bei weiteren Starts erhalten.

Ein gültiger aktueller Primärstand beziehungsweise ein gültiges aktuelles Backup
hat Vorrang. Alte Backups dürfen weder alte Fortschritte zurückbringen noch nach
erfolgreichem Wechsel das Speichern blockieren. Unlesbare Daten, unbekannte
Saveformate, falsche IDs und höhere gespeicherte Revisionen bleiben Fehler-/
Recoveryfälle; ein Git-Downgrade löscht keinen neueren Spielstand automatisch.
Die Erkennung einer älteren Revision verwendet einen lesbaren, konsistenten
Speicherumschlag mit unterstütztem Schema, gleicher ID und positiver kleinerer
Revision. Sie verlangt keine Prüfung gegen eine nicht mehr verfügbare alte Lösung
und übernimmt keine alten Zellen in das neue Raster.

Der Revisionswechsel ist wiederholbar und abbruchsicher. Die bestehenden vollständigen
Prüfungen aktueller Saves bleiben. Editor und Inhaltswriter greifen auf kein
Spielerprofil zu; die Laufzeit behandelt den Wechsel. Die heutige manuelle
Resetpflicht aus [P1](PROTOTYPE_P1.md) bleibt bis PE-A3 implementierter Stand.

## 6. Gemeinsamer Zugriff, Speichern und Effizienz

Ein lokaler Python-Dienst verwendet die vorhandenen Fachfunktionen und gemeinsame
Writer. Die Browseroberfläche schreibt nicht an ihnen vorbei. Der Dienst bindet
nur lokal und begrenzt Dateizugriffe auf den bewusst geöffneten Checkout und
ausgewählte Importe; ein öffentliches Hosting wird nicht eingerichtet.

Ein Speichervorgang darf mehrere geänderte Felder zusammen übernehmen. Vor der
Mutation werden Eingaben, Ausgangsstand und betroffene Referenzen geprüft.
Zwischenzeitliche fremde Änderungen erzeugen einen Konflikt statt Überschreiben.
Zusammenhängende Dateien werden unter dem gemeinsamen Checkoutlock mit
vorhandener Transaktions-/Recoverysemantik übernommen; Runtime zuletzt. Offene
Journale werden nicht ignoriert. Ein No-op verändert keine Bytes oder mtimes.

Die aktuelle Namens-/Kategorieansicht wird aus einem kleinen Katalog einmal
geladen und nach ID aufgelöst. Dafür werden nicht sämtliche Rasterbilder oder
Produktionsbelege geöffnet. Umfangreiche Prüfungen gehören an den Schreib-/
Integrationsweg, nicht an jede Texteingabe. Dateihashes bleiben Integritäts- und
Konfliktschutz; sie sind keine fachlichen Rätsel-IDs.

PE verspricht keinen unbelegten Geschwindigkeitsgewinn. Der heutige Spielstart
lädt viele Definitionen/Saves bereits vorab. Ein allgemeiner Umbau dieses
Startverhaltens ist kein verdeckter Teil des Editors. Der erste Datenwechsel
bekommt einen begrenzten Vergleich von Aufwand, Dateizugriffen und Laufzeit;
spätere konkrete Engpässe werden anhand der Messung behandelt.

## 7. PE-A1: geschlossener Metadatenvertrag

PE-A1 ist das erste eigenständig lieferbare Fundament. Es liefert Namen,
Kategorien, Migration und gemeinsame API/CLI; noch keine Weboberfläche,
Bildübernahme, Rasteränderung oder automatische Savebehandlung.

### 7.1 Inhaltsregistry v4

Neue Wurzel `picross-content-registry-v4`, exakt
`format,entries,metadata,backgrounds`. `backgrounds` verwendet den bestehenden
Indexvertrag und darf leer sein. `entries` behalten ihren bestehenden exakten
Eintragsvertrag und die Produktionsbindungen. `metadata` ist eine nach ID
sortierte Liste mit exakt einer Zeile `{id,name,category_id}` je registrierter ID.
Keine fehlenden, zusätzlichen oder doppelten IDs. Name gemäß §3; `category_id`
verweist auf den aktuellen Kategorienkatalog. Bestehende Größen-/Anzahlgrenzen
der Inhaltsregistry und Kategorien bleiben.

| Daten | Autorität in v4 |
| --- | --- |
| Aktueller Motivname | `metadata[id].name` |
| Aktuelle Kategorie | `metadata[id].category_id` |
| Identität, Definition-/Assetpfade und Produktion | Bestehender `entries`-Eintrag und seine gebundenen Fachquellen |
| Aktuelles Raster | Bestehende Definitionsdatei mit ID, Revision, Matrix, Palette und Hinweisen |
| Name in `definition.reveal.name` / Kategorie in Produktionseintrag | Zum jeweiligen Produktionsstand gehörende Angabe; kein zweiter aktueller redaktioneller Wert |

Bestehende v2/v3 bleiben unter ihren exakten Altregeln lesbar. Nur dort darf die
aktuelle Ansicht aus Definition/Entry abgeleitet werden. Bei v4 sind fehlende oder
ungültige Metadaten ein Fehler, kein Rückfall auf alte Angaben. Der reine
Entry-Struktur-/Receiptvergleich wird von der Prüfung aktueller Kategoriebezüge
getrennt. Historische Entrykategorien bleiben gegen ihren damaligen Export-/
Receiptstand geprüft; sie müssen in v4 nicht mehr im aktuellen Kategorienkatalog
existieren. Keine Ersatzkategorien und kein Umschreiben alter Belege.

### 7.2 Laufzeitregistry v7

`picross-runtime-registry-v7` hat exakt `format,categories,entries`. Jeder Eintrag
enthält die zehn bisherigen v6-Felder
`id,key,save_slot,definition,reveal,visible,category_id,difficulty,added_at,background`
und zusätzlich `name`. Name und Kategorie stammen aus der aktuellen Metadatentabelle.
Es gibt genau eine v7-Form; Legacy erhält `background={status:legacy,
image_revision:null,asset:null}`. Sonstige Hintergrundformen entsprechen exakt v6.

V7 konsumiert ausdrücklich denselben Hintergrundteilvertrag wie v6. Die geschlossene
Capability-v1 und ihr v6-Fähigkeitsnachweis bleiben unverändert gültig; `selected/none`
verlangen weiterhin eine aktivierte kompatible Fähigkeit. Ein Legacy-only-v7-Katalog
erzwingt keine Hintergrundaktivierung. Unbekannte/defekte Fähigkeiten werden nicht
stillschweigend akzeptiert. V2–v6 behalten ihre geschlossenen Altleser.

Der gemeinsame Definitionsloader übernimmt bei v7 den aktuellen Namen ausschließlich
in das im Speicher verwendete Definitionsobjekt. ID, Revision, Lösung und übrige
Felder bleiben gleich; die Definitionsdatei wird dafür nicht geschrieben. Alle
normalen Spielanzeigen verwenden diese gemeinsame Auflösung. Neue/begonnene Rätsel
zeigen weiterhin keine unverdienten Motivnamen oder Bilder. Der Spieler lädt keine
Inhaltsregistry oder Produktionsbelege.

### 7.3 Migration und laufende Produktion

Die explizite einmalige Migration prüft den gültigen Ausgangscheckout und übernimmt
für jede ID den aktuellen Namen aus der Definition und die Kategorie aus dem Entry.
Bei v2 entsteht ein leerer Hintergrundindex, bei v3 bleibt der Index erhalten.
Nur Inhaltsregistry und Runtimeprojektion ändern sich; Kategorien, Definitionen,
Bilder, aktive Quellen, Ratings, Added und Herkunftsbelege bleiben bytegleich.
Keine sichtbare Umbenennung, neue Rätselrevision, erneute Zertifizierung oder
Spielstandmigration. Wiederholung eines bereits gültigen v4/v7-Stands ist No-op.

Neue mutierende PE-Operationen und die fortgeführten regulären Writer verlangen
einen gültigen v4/v7-Zielstand. Außer bei der ausdrücklich aufgerufenen Migration
stoppen sie auf v2/v3 vor Mutation mit einem konkreten Migrationshinweis.
Historische Prüfung, vollständig geprüfte No-ops und bereits gebundene Alt-Recovery
bleiben unter ihrem jeweiligen Vertrag möglich. Gewöhnliche Pflege- oder
Produktionsoperationen führen keine implizite Migration aus.

| Operation nach PE-A1 | Behandlung aktueller Metadaten |
| --- | --- |
| Erstregistrierung einer neuen ID | Aktuell vorhandene Kategorie verlangen; Zeile aus geprüfter Exportkategorie und Definitionsname initialisieren. |
| Historisch identische Registerwiederholung | Vollständige ursprüngliche Bindung prüfen, aktive Zeile erhalten. Eine inzwischen gelöschte Ursprungskategorie ist kein Grund, aktuelle Metadaten zurückzusetzen. |
| Rasterupdate einer vorhandenen ID | Aktive Zeile vollständig erhalten. Exportkategorie gegen den eigenen unveränderten Exportsnapshot prüfen; sie darf von der aktuellen Zuordnung abweichen und wird nur Herkunft des neuen Produktionseintrags. |
| Reveal-/Hintergrund-/Rating-/Added-Operation, Sync, Batch | Aktive Zeilen erhalten und bei Planung/Prüfung mitbinden. Keine Rekonstruktion aus historischen Angaben. |
| Name/Kategorie/Kategorienkatalog pflegen | Nur betroffene Metadaten beziehungsweise Kategorienquelle und erforderliche Runtimeprojektion ändern. Keine Definition-/Rating-/Bildneubindung allein dafür. |

Ein gemeinsamer Resolver liefert aktuelle und historische Angaben bewusst getrennt.
Alle Full-/Quick-/Snapshot-/Recovery-/Namespacewege müssen die neue Generation
konsistent akzeptieren oder eine unpassende alte Operation vor Mutation ablehnen.
Ein Metadatenwechsel nach Planung macht alte schreibende Pläne stale, auch wenn
deren eigenes Zielfeld unverändert ist. Offene alte Journale werden vor Migration
mit ihrem passenden bisherigen Vertrag aufgelöst; keine blinde Journalumschreibung.

### 7.4 API/CLI und Änderungsumfang

Eine kleine gemeinsame Python-API und CLI bieten lesende Auflösung, lesenden
Änderungsplan, explizite Übernahme sowie Migration und Wiederherstellung. Sie
unterstützen Name, Kategoriezuordnung, Kategorieanlage/-umbenennung sowie
Kategorieentfernung mit optionaler vollständiger Neuzuordnung. Keine API zum
freien Ersetzen der gesamten Registry und keine zweite alternative Schreiblogik.
Konkrete Befehlsnamen gehören zur mitzuliefernden Werkzeuganleitung.

Ein Plan zeigt ausgewählte IDs, Werte vorher/nachher und die tatsächlich betroffenen
Dateien. Er bindet Ausgangsbytes, relevante Abwesenheiten und gemeinsame Quellen.
Eine neue geschlossene Plangeneration und nötige Journalgeneration verwenden die
bestehenden Locks, Staging-, Konflikt- und Recoverymechanismen. Alte Generationen
werden nicht durch ignorierte Fremdfelder erweitert. Normale Name-/Kategoriepflege
erzeugt keine eigene endlose Metadatenhistorie oder zusätzliche Freigaberunde.

PE-A1 umfasst die verlustfreie Übernahme des dann aktuellen echten Bestands und
die nötigen gemeinsamen Leser-/Writeranpassungen. Der echte Bestand dient nur
der einmaligen Migration und Integritätskontrolle, nicht als wachsender Dauertest.

## 8. Lieferung, Abnahme und Grenzen der Vorbereitung

Die beiden Hauptbereiche bleiben Datenpflege und Weboberfläche. Das Fundament
wird wegen seiner unterschiedlichen Datenrisiken in eigenständige Pakete geteilt:

| Paket | Eigenständig prüfbarer Endzustand |
| --- | --- |
| PE-A1 | Aktuelle Namen/Kategorien, v4/v7-Migration, gemeinsame CLI/API und weiter funktionierende Standardproduktion. Erstes vorbereitetes Umsetzungspaket. |
| PE-A2 | Unveränderter Fertigbildimport, Abschlussbildwechsel, Legacy-Erstzuordnung und alle drei Hintergrundzustände. Baut auf PE-A1 auf. |
| PE-A3 | Textuelle Rasterübernahme mit vorhandenen Prüfungen und gezielter automatischer Savebehandlung bei älterer Rasterrevision. Baut auf PE-A1 und den tatsächlich benötigten Bildbindungen auf. |
| PE-B | Lokale Weboberfläche und komfortabler Windowsstart für sämtliche freigegebenen Bearbeitungen. Konsumiert die gemeinsamen Writer. |

Nur PE-A1 erhält jetzt seinen vollständigen Umsetzungsschnitt und Prüfplan im
Issue. Die weiteren Umfänge sind fachlich beschlossen; ihre konkreten Versions-/
Transaktions-/Prüfentscheidungen werden vor ihrer Umsetzung geschlossen. Ein
fertiges PE-A1 ist kein fertiger Editor und schließt das Gesamtissue nicht.

Die Spezifikationsänderung wird im zu PE-A1 gehörenden Draft-PR vorbereitet;
PE-A1 wird bei gesondertem Umsetzungsauftrag auf demselben Branch/PR fortgeführt.
Der anfängliche Dokumentdiff bleibt buildfrei und hat keine Zusatzmodule.
Die Umsetzung aktualisiert ihren eigenen `.ci/package.json` entsprechend dem
Issue-Prüfplan. Technische Lieferung, unabhängiges Review, persönliche Editorprobe
und Merge sind jeweils getrennt. Keine dieser Handlungen wird durch diese
Spezifikation als bereits erfolgt behauptet.
